#!/usr/bin/env python3
"""Step 9: Audit a suspect across G disjoint prompt windows to compute TPR@5%FPR & TPR@1%FPR.

Protocol:
  1. Optionally imports exact-prompt cached responses from an earlier multi-window run
     via `--reuse-responses-from suspects_mw` (zero wasted generation when expanding
     20 x 1,000 -> 100 x 450!).
  2. Loads the suspect model ONCE in vLLM (KGW OFF) and samples remaining missing
     prompts in large chunks (`--gen-chunk-windows 10`) for high A100 throughput,
     checkpointing each window atomically to `responses_win_XX.jsonl`.
  3. Loads the frozen probe ONCE and extracts one projected gradient vector per window
     (skips already-computed window gradients).
  4. Scores every window independently against the K-key reference bank (e.g. K=200)
     to report exact, trick-free:
       - TPR @ 5% FPR  (fraction of disjoint windows with p_rank <= 0.05)
       - TPR @ 1% FPR  (fraction of disjoint windows with p_rank <= 0.01, when K >= 100)
       - Window mean/median rank, mean z-score +/- std
       - Pooled full-budget rank, p_rank, z-score, and S(k*) across all G windows combined.
"""

from __future__ import annotations

import argparse
import gc
import importlib.util
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

# Use V0 engine by default for stable multi-GPU concurrent runs without port/IPC clashes.
os.environ.setdefault("VLLM_USE_V1", "0")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from wm_basin.core import (
    BlockRademacherProjector,
    DEFAULT_MAX_RESPONSE_TOKENS,
    DEFAULT_MIN_RESPONSE_TOKENS,
    DEFAULT_PROJ_DIM,
    DEFAULT_PROJ_SEED,
    TaskSubspace,
    cosine_similarities,
    rank_test,
    read_json,
    read_jsonl,
    render_prompt_with_fallback,
    write_json,
    write_jsonl,
)


def _import_extract_module():
    spec = importlib.util.spec_from_file_location(
        "wm_basin_extract_grads",
        Path(__file__).resolve().parent / "04_extract_grads.py",
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def _win_tag(w_idx: int, num_windows: int) -> str:
    width = max(2, len(str(max(1, num_windows) - 1)))
    return f"{w_idx:0{width}d}"


def _messages_key(messages: list[dict]) -> str:
    return json.dumps(messages, ensure_ascii=False, sort_keys=True)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Multi-window disjoint WM-Basin audit for TPR@FPR")
    p.add_argument("--work-dir", type=Path, default=Path("wm_basin_work"))
    p.add_argument("--suspect-name", type=str, required=True)
    p.add_argument("--suspect-model", type=str, default=None)
    p.add_argument(
        "--role",
        choices=["suspect", "negative"],
        default="suspect",
        help="Tag as 'negative' for clean/base controls so summary script can also compute empirical AUROC",
    )
    p.add_argument("--windows-dir", type=Path, default=None, help="Defaults to <work-dir>/pools/audit_windows")
    p.add_argument("--suspects-subdir", type=str, default="suspects_mw", help="Subdir under work-dir (e.g. suspects_mw100)")
    p.add_argument(
        "--reuse-responses-from",
        type=str,
        default=None,
        help="Optional earlier subdir under work-dir (e.g. suspects_mw) to reuse exact-prompt responses from",
    )
    p.add_argument("--num-windows", type=int, default=None, help="Optional cap on number of windows to evaluate")
    p.add_argument("--num-samples-per-prompt", type=int, default=1, help="Samples per unique prompt (default: 1)")
    p.add_argument("--gen-chunk-windows", type=int, default=10, help="Number of windows batched per vLLM generate call")
    p.add_argument("--temperature", type=float, default=1.0)
    p.add_argument("--top-p", type=float, default=0.95)
    p.add_argument("--max-prompt-tokens", type=int, default=1024)
    p.add_argument("--max-new-tokens", type=int, default=DEFAULT_MAX_RESPONSE_TOKENS)
    p.add_argument("--min-response-tokens", type=int, default=DEFAULT_MIN_RESPONSE_TOKENS)
    p.add_argument("--batch-size", type=int, default=6, help="Probe gradient micro-batch size (default: 6)")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--gpu-memory-utilization", type=float, default=0.55)
    p.add_argument("--only-score", action="store_true", help="Skip sampling & gradient; re-score existing window grads")
    p.add_argument("--overwrite", action="store_true")
    return p.parse_args()


def load_reuse_cache(work_dir: Path, reuse_subdir: str | None, suspect_name: str) -> dict[tuple[str, int], dict]:
    if not reuse_subdir:
        return {}
    src_dir = work_dir / reuse_subdir / suspect_name
    if not src_dir.exists():
        return {}
    cache: dict[tuple[str, int], dict] = {}
    for fp in sorted(src_dir.glob("responses_win_*.jsonl")):
        for row in read_jsonl(fp):
            s_idx = int(row.get("sample_idx", 0))
            key = (_messages_key(row["messages"]), s_idx)
            if key not in cache:
                cache[key] = row
    return cache


def sample_missing_windows(
    args: argparse.Namespace,
    window_files: list[Path],
    sus_dir: Path,
) -> None:
    num_windows = len(window_files)
    pending: list[tuple[int, Path, Path]] = []
    for w_idx, wf in enumerate(window_files):
        resp_path = sus_dir / f"responses_win_{_win_tag(w_idx, num_windows)}.jsonl"
        if not resp_path.exists() or args.overwrite:
            pending.append((w_idx, wf, resp_path))

    if not pending:
        print(f"[mw:{args.suspect_name}] All {num_windows} window responses exist, skipping vLLM.", flush=True)
        return

    # 1. Try reusing exact-prompt responses from an earlier run (e.g. suspects_mw)
    reuse_cache = load_reuse_cache(args.work_dir, args.reuse_responses_from, args.suspect_name)
    reused_rows_total = 0
    reused_full_windows = 0
    still_pending: list[tuple[int, Path, Path, list[dict], dict[tuple[int, int], dict]]] = []

    for w_idx, wf, resp_path in pending:
        rows = read_jsonl(wf)
        cached_map: dict[tuple[int, int], dict] = {}
        if reuse_cache:
            for s_idx in range(args.num_samples_per_prompt):
                for r_pos, r in enumerate(rows):
                    hit = reuse_cache.get((_messages_key(r["messages"]), s_idx))
                    if hit is not None:
                        cached_map[(s_idx, r_pos)] = {
                            "id": f"{r['id']}__s{s_idx}",
                            "window_idx": w_idx,
                            "prompt_idx": r["prompt_idx"],
                            "sample_idx": s_idx,
                            "messages": r["messages"],
                            "response": hit["response"],
                            "num_tokens": hit.get("num_tokens", 0),
                            "suspect_name": args.suspect_name,
                            "kgw_enabled_during_generation": False,
                            "reused_from": args.reuse_responses_from,
                        }
        expected_total = len(rows) * args.num_samples_per_prompt
        if len(cached_map) == expected_total:
            saved = [
                cached_map[(s_idx, r_pos)]
                for s_idx in range(args.num_samples_per_prompt)
                for r_pos in range(len(rows))
            ]
            write_jsonl(resp_path, saved)
            reused_full_windows += 1
            reused_rows_total += len(saved)
        else:
            reused_rows_total += len(cached_map)
            still_pending.append((w_idx, wf, resp_path, rows, cached_map))

    if reuse_cache:
        print(
            f"[mw:{args.suspect_name}] Reused {reused_rows_total:,} cached responses from {args.reuse_responses_from} "
            f"({reused_full_windows} full windows completed instantly; {len(still_pending)} windows need vLLM).",
            flush=True,
        )

    if not still_pending:
        return
    if not args.suspect_model:
        raise ValueError(f"--suspect-model is required to sample {len(still_pending)} missing windows")

    import torch
    from vllm import LLM, SamplingParams

    missing_prompts_total = sum(
        len(rows) * args.num_samples_per_prompt - len(cached_map)
        for _, _, _, rows, cached_map in still_pending
    )
    print(
        f"[mw:{args.suspect_name}] Loading suspect in vLLM for {len(still_pending)} windows "
        f"({missing_prompts_total:,} new prompts): {args.suspect_model}",
        flush=True,
    )
    llm = LLM(
        model=args.suspect_model,
        gpu_memory_utilization=args.gpu_memory_utilization,
        max_model_len=args.max_prompt_tokens + args.max_new_tokens,
        dtype="auto",
        trust_remote_code=True,
    )
    tokenizer = llm.get_tokenizer()

    try:
        chunk_sz = max(1, int(args.gen_chunk_windows))
        for start in range(0, len(still_pending), chunk_sz):
            group = still_pending[start : start + chunk_sz]
            all_prompts: list[str] = []
            all_params: list[SamplingParams] = []
            all_slots: list[tuple[int, int, int, dict]] = []  # (group_pos, s_idx, r_pos, row)

            for g_pos, (w_idx, _, _, rows, cached_map) in enumerate(group):
                for s_idx in range(args.num_samples_per_prompt):
                    for r_pos, r in enumerate(rows):
                        if (s_idx, r_pos) in cached_map:
                            continue
                        prompt = render_prompt_with_fallback(tokenizer, r["messages"], args.max_prompt_tokens)
                        all_prompts.append(prompt)
                        all_params.append(
                            SamplingParams(
                                n=1,
                                temperature=args.temperature,
                                top_p=args.top_p,
                                max_tokens=args.max_new_tokens,
                                repetition_penalty=1.0,
                                seed=args.seed + w_idx * 1_000_003 + s_idx * 100_003 + r["prompt_idx"],
                                skip_special_tokens=True,
                            )
                        )
                        all_slots.append((g_pos, s_idx, r_pos, r))

            t0 = time.time()
            outputs = llm.generate(all_prompts, sampling_params=all_params, use_tqdm=True)
            for (g_pos, s_idx, r_pos, r), req in zip(all_slots, outputs):
                w_idx, _, _, _, cached_map = group[g_pos]
                cached_map[(s_idx, r_pos)] = {
                    "id": f"{r['id']}__s{s_idx}",
                    "window_idx": w_idx,
                    "prompt_idx": r["prompt_idx"],
                    "sample_idx": s_idx,
                    "messages": r["messages"],
                    "response": req.outputs[0].text,
                    "num_tokens": len(req.outputs[0].token_ids),
                    "suspect_name": args.suspect_name,
                    "kgw_enabled_during_generation": False,
                }

            for w_idx, _, resp_path, rows, cached_map in group:
                saved = [
                    cached_map[(s_idx, r_pos)]
                    for s_idx in range(args.num_samples_per_prompt)
                    for r_pos in range(len(rows))
                ]
                write_jsonl(resp_path, saved)

            w_lo = _win_tag(group[0][0], num_windows)
            w_hi = _win_tag(group[-1][0], num_windows)
            print(
                f"[mw:{args.suspect_name}] Windows {w_lo}..{w_hi}/{num_windows-1}: "
                f"sampled {len(all_prompts):,} new responses in {time.time() - t0:.1f}s",
                flush=True,
            )
    finally:
        if hasattr(llm, "llm_engine") and hasattr(llm.llm_engine, "engine_core"):
            try:
                llm.llm_engine.engine_core.shutdown()
            except Exception:
                pass
        del llm
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()


def extract_missing_window_grads(
    args: argparse.Namespace,
    num_windows: int,
    sus_dir: Path,
) -> None:
    pending = []
    for w_idx in range(num_windows):
        tag = _win_tag(w_idx, num_windows)
        grad_path = sus_dir / f"grad_win_{tag}.npy"
        resp_path = sus_dir / f"responses_win_{tag}.jsonl"
        if not grad_path.exists() or args.overwrite:
            pending.append((w_idx, tag, resp_path, grad_path))

    if not pending:
        print(f"[mw:{args.suspect_name}] All {num_windows} window gradients exist, skipping probe.", flush=True)
        return

    import torch
    from tqdm import tqdm

    extract_mod = _import_extract_module()
    proj_meta_path = args.work_dir / "grads" / "projector_meta.json"
    if proj_meta_path.exists():
        pm = read_json(proj_meta_path)
        proj_dim = int(pm["proj_dim"])
        proj_seed = int(pm["proj_seed"])
        block_size = int(pm["block_size"])
        weighting = pm["weighting"]
        max_resp = int(pm["max_response_tokens"])
        min_resp = int(pm["min_response_tokens"])
    else:
        proj_dim, proj_seed, block_size = DEFAULT_PROJ_DIM, DEFAULT_PROJ_SEED, 65536
        weighting = "token"
        max_resp, min_resp = args.max_new_tokens, args.min_response_tokens

    model, tokenizer, lora_params, _ = extract_mod.load_frozen_probe(args.work_dir)
    projector = BlockRademacherProjector(proj_dim=proj_dim, seed=proj_seed, block_size=block_size)

    t_all = time.time()
    try:
        for idx_p, (w_idx, tag, resp_path, grad_path) in enumerate(
            tqdm(pending, desc=f"grad:{args.suspect_name}", unit="win"), 1
        ):
            rows = read_jsonl(resp_path)
            vec, stats = extract_mod.extract_projected_gradient(
                model=model,
                tokenizer=tokenizer,
                lora_params=lora_params,
                rows=rows,
                projector=projector,
                max_prompt_tokens=args.max_prompt_tokens,
                max_response_tokens=max_resp,
                min_response_tokens=min_resp,
                max_samples=None,
                batch_size=args.batch_size,
                weighting=weighting,
                show_progress=False,
                desc=f"{args.suspect_name}:w{tag}",
            )
            np.save(grad_path, vec)
            write_json(grad_path.with_suffix(".meta.json"), stats)
            if idx_p % 10 == 0 or idx_p == len(pending):
                print(
                    f"[mw:{args.suspect_name}] Extracted {idx_p}/{len(pending)} window grads "
                    f"(last w{tag}: used={stats['num_used_samples']}, tokens={stats['total_scored_tokens']:,}, "
                    f"elapsed={time.time() - t_all:.1f}s)",
                    flush=True,
                )
    finally:
        del model
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()


def score_all_windows(
    args: argparse.Namespace,
    num_windows: int,
    sus_dir: Path,
) -> dict:
    subspace = TaskSubspace.load(args.work_dir / "pca" / "task_subspace.npz")
    keys_info = read_json(args.work_dir / "keys.json")
    bank_dir = args.work_dir / "grads" / "bank"

    bank_vecs = []
    bank_keys = []
    for idx, hk in enumerate(keys_info["keys"]):
        fp = bank_dir / f"key_{idx:04d}_{hk}.npy"
        if fp.exists():
            bank_vecs.append(np.load(fp).astype(np.float64))
            bank_keys.append(int(hk))
    K = len(bank_vecs)
    if K < 2 or bank_keys[0] != int(keys_info["true_key"]):
        raise RuntimeError(f"Invalid reference bank in {bank_dir} (found {K} keys)")

    bank_mat = np.stack(bank_vecs, axis=0)
    bank_res = subspace.project_out(bank_mat)

    win_results = []
    win_vecs = []
    win_weights = []

    for w_idx in range(num_windows):
        tag = _win_tag(w_idx, num_windows)
        grad_path = sus_dir / f"grad_win_{tag}.npy"
        meta_path = sus_dir / f"grad_win_{tag}.meta.json"
        vec = np.load(grad_path).astype(np.float64)
        gm = read_json(meta_path) if meta_path.exists() else {}
        tok_w = int(gm.get("total_scored_tokens", 1))

        sus_res = subspace.project_out(vec)
        scores = cosine_similarities(sus_res, bank_res)
        res = rank_test(scores, claimed_idx=0)
        win_results.append(
            {
                "window_idx": w_idx,
                "used_samples": gm.get("num_used_samples"),
                "scored_tokens": gm.get("total_scored_tokens"),
                "rank": res["rank"],
                "p_rank": res["p_rank"],
                "cosine": res["claimed_score"],
                "z_score": res["z_score"],
                "flagged_at_5pct": bool(res["p_rank"] <= 0.05),
                "flagged_at_1pct": bool(res["p_rank"] <= 0.01) if K >= 100 else None,
            }
        )
        win_vecs.append(vec)
        win_weights.append(float(tok_w))

    # Exact token-weighted pooled gradient across all G windows combined
    weights_arr = np.asarray(win_weights, dtype=np.float64)
    pooled_vec = np.average(np.stack(win_vecs, axis=0), axis=0, weights=weights_arr)
    pooled_res = rank_test(cosine_similarities(subspace.project_out(pooled_vec), bank_res), claimed_idx=0)

    p_ranks = np.array([w["p_rank"] for w in win_results], dtype=np.float64)
    ranks = np.array([w["rank"] for w in win_results], dtype=np.float64)
    z_scores = np.array([w["z_score"] for w in win_results], dtype=np.float64)
    cosines = np.array([w["cosine"] for w in win_results], dtype=np.float64)

    tpr_5pct = float(np.mean(p_ranks <= 0.05))
    tpr_1pct = float(np.mean(p_ranks <= 0.01)) if K >= 100 else None
    tpr_10pct = float(np.mean(p_ranks <= 0.10))

    # Auto-infer role if name clearly denotes clean/base control
    role = args.role
    low_name = args.suspect_name.lower()
    if any(tag in low_name for tag in ("clean", "base_qwen")):
        role = "negative"

    report = {
        "suspect_name": args.suspect_name,
        "suspect_model": args.suspect_model,
        "role": role,
        "num_keys": K,
        "true_key": bank_keys[0],
        "pca_q": subspace.q,
        "num_windows": num_windows,
        "total_scored_tokens": int(sum(w["scored_tokens"] or 0 for w in win_results)),
        "tpr_at_5pct": tpr_5pct,
        "tpr_at_1pct": tpr_1pct,
        "tpr_at_10pct": tpr_10pct,
        "hits_at_5pct": int(np.sum(p_ranks <= 0.05)),
        "hits_at_1pct": int(np.sum(p_ranks <= 0.01)) if K >= 100 else None,
        "mean_rank": float(ranks.mean()),
        "median_rank": float(np.median(ranks)),
        "mean_p_rank": float(p_ranks.mean()),
        "mean_cosine": float(cosines.mean()),
        "mean_z_score": float(z_scores.mean()),
        "std_z_score": float(z_scores.std(ddof=1)) if num_windows > 1 else 0.0,
        "pooled": pooled_res,
        "windows": win_results,
    }
    out_path = sus_dir / "mw_score.json"
    write_json(out_path, report)

    t1_str = f"{tpr_1pct*100:5.1f}% ({report['hits_at_1pct']}/{num_windows})" if tpr_1pct is not None else "N/A (need K>=100)"
    print("=" * 76, flush=True)
    print(f"WM-Basin Multi-Window Audit: {args.suspect_name} ({num_windows} disjoint windows, K={K} keys, q={subspace.q})")
    print(f"  TPR @ 5% FPR : {tpr_5pct*100:5.1f}% ({report['hits_at_5pct']}/{num_windows})")
    print(f"  TPR @ 1% FPR : {t1_str}")
    print(f"  Window stats : median_rank={report['median_rank']:.1f}/{K} | mean_z={report['mean_z_score']:+.2f} +/- {report['std_z_score']:.2f}")
    print(f"  Pooled (all) : rank={pooled_res['rank']}/{K} | p_rank={pooled_res['p_rank']:.4f} | z={pooled_res['z_score']:+.2f}")
    print("=" * 76, flush=True)
    return report


def main() -> None:
    args = parse_args()
    win_dir = args.windows_dir or (args.work_dir / "pools" / "audit_windows")
    win_files = sorted(win_dir.glob("window_*.jsonl"))
    if not win_files:
        raise FileNotFoundError(f"No window_*.jsonl found in {win_dir}; run 08_prepare_audit_windows.py first")
    if args.num_windows is not None:
        win_files = win_files[: args.num_windows]

    sus_dir = args.work_dir / args.suspects_subdir / args.suspect_name
    sus_dir.mkdir(parents=True, exist_ok=True)

    if not args.only_score:
        sample_missing_windows(args, win_files, sus_dir)
        extract_missing_window_grads(args, len(win_files), sus_dir)

    score_all_windows(args, len(win_files), sus_dir)


if __name__ == "__main__":
    main()
