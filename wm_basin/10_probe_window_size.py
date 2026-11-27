#!/usr/bin/env python3
"""Step 10: Fast exact multi-granularity window-size probe & 100-window scorer.

Reuses already-generated responses in:
  <work-dir>/suspects_mw/<suspect_name>/responses_win_00.jsonl .. responses_win_19.jsonl
(20,000 unique responses per suspect — ZERO new vLLM generation needed!)

Because both token-weighted gradient averaging and CountSketch projection are
strictly linear, extracting one projected gradient per 50-prompt micro-block
(400 micro-blocks total, ~1.5 min per model on A100) lets us compute EXACT,
bit-equivalent disjoint-window scores at ANY multiple of 50 prompts in <1s:
  - 200 prompts/window  -> 100 disjoint windows (1% granularity!)
  - 450 prompts/window  ->  44 disjoint windows (preview of 100 x 450)
  - 500 prompts/window  ->  40 disjoint windows (preview of 100 x 500)
  - 1000 prompts/window ->  20 disjoint windows (sanity check vs mw_score.json)
"""

from __future__ import annotations

import argparse
import gc
import importlib.util
import sys
import time
from pathlib import Path

import numpy as np

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
    write_json,
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


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Single-pass exact comparison of 200 / 450 / 500 / 1000 prompts per disjoint window"
    )
    p.add_argument("--work-dir", type=Path, default=Path("wm_basin_work"))
    p.add_argument(
        "--suspects",
        nargs="+",
        required=True,
        help="Suspect names under suspects_mw/ (or 'ALL' for all suspects)",
    )
    p.add_argument("--micro-size", type=int, default=50, help="Prompts per micro-block (default: 50)")
    p.add_argument(
        "--window-sizes",
        nargs="+",
        type=int,
        default=[200, 450, 500, 1000],
        help="Disjoint window sizes (prompts) to evaluate; each must be a multiple of --micro-size",
    )
    p.add_argument("--max-prompt-tokens", type=int, default=2048)
    p.add_argument("--batch-size", type=int, default=8, help="Probe forward/backward micro-batch size")
    p.add_argument("--overwrite-cache", action="store_true", help="Re-extract micro-block gradients")
    p.add_argument("--out-json", type=Path, default=None, help="Optional path to save comparison JSON")
    return p.parse_args()


def load_all_responses(sus_dir: Path) -> list[dict]:
    files = sorted(sus_dir.glob("responses_win_*.jsonl"))
    if not files:
        raise FileNotFoundError(f"No responses_win_*.jsonl found in {sus_dir}")
    rows: list[dict] = []
    for f in files:
        rows.extend(read_jsonl(f))
    return rows


def extract_or_load_micro_blocks(
    work_dir: Path,
    suspect_name: str,
    micro_size: int,
    max_prompt_tokens: int,
    batch_size: int,
    overwrite: bool,
    probe_bundle: list,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return (grads [B, D], weights [B], used_samples [B]) for disjoint micro-blocks."""
    sus_dir = work_dir / "suspects_mw" / suspect_name
    cache_path = sus_dir / f"micro_blocks_{micro_size}.npz"
    if cache_path.exists() and not overwrite:
        data = np.load(cache_path)
        return data["grads"], data["weights"], data["used_samples"]

    rows = load_all_responses(sus_dir)
    n_blocks = len(rows) // micro_size
    if n_blocks == 0:
        raise RuntimeError(f"{suspect_name}: only {len(rows)} rows, smaller than micro_size={micro_size}")

    if not probe_bundle:
        extract_mod = _import_extract_module()
        proj_meta_path = work_dir / "grads" / "projector_meta.json"
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
            max_resp, min_resp = DEFAULT_MAX_RESPONSE_TOKENS, DEFAULT_MIN_RESPONSE_TOKENS
        model, tokenizer, lora_params, _ = extract_mod.load_frozen_probe(work_dir)
        projector = BlockRademacherProjector(proj_dim=proj_dim, seed=proj_seed, block_size=block_size)
        probe_bundle.extend([extract_mod, model, tokenizer, lora_params, projector, weighting, max_resp, min_resp])

    extract_mod, model, tokenizer, lora_params, projector, weighting, max_resp, min_resp = probe_bundle

    grads = np.zeros((n_blocks, projector.proj_dim), dtype=np.float32)
    weights = np.zeros((n_blocks,), dtype=np.float64)
    used_samples = np.zeros((n_blocks,), dtype=np.int64)

    t0 = time.time()
    from tqdm import tqdm

    for b in tqdm(range(n_blocks), desc=f"{suspect_name} (micro={micro_size})", unit="blk"):
        chunk = rows[b * micro_size : (b + 1) * micro_size]
        vec, stats = extract_mod.extract_projected_gradient(
            model=model,
            tokenizer=tokenizer,
            lora_params=lora_params,
            rows=chunk,
            projector=projector,
            max_prompt_tokens=max_prompt_tokens,
            max_response_tokens=max_resp,
            min_response_tokens=min_resp,
            max_samples=None,
            batch_size=batch_size,
            weighting=weighting,
            show_progress=False,
        )
        grads[b] = vec.astype(np.float32)
        weights[b] = float(stats["total_scored_tokens"] if weighting == "token" else stats["num_used_samples"])
        used_samples[b] = int(stats["num_used_samples"])

    np.savez(cache_path, grads=grads, weights=weights, used_samples=used_samples)
    print(
        f"[probe_ws:{suspect_name}] Extracted {n_blocks} micro-blocks ({n_blocks * micro_size:,} prompts) "
        f"in {time.time() - t0:.1f}s -> {cache_path}",
        flush=True,
    )
    return grads, weights, used_samples


def evaluate_window_size(
    grads: np.ndarray,
    weights: np.ndarray,
    micro_size: int,
    window_size: int,
    subspace: TaskSubspace,
    bank_res: np.ndarray,
    claimed_idx: int,
) -> dict:
    if window_size % micro_size != 0:
        raise ValueError(f"window_size={window_size} must be a multiple of micro_size={micro_size}")
    k = window_size // micro_size
    n_win = grads.shape[0] // k
    if n_win == 0:
        raise ValueError(f"Not enough micro-blocks ({grads.shape[0]}) for window_size={window_size}")

    # Linear exact aggregation of micro-block gradients
    win_vecs = np.zeros((n_win, grads.shape[1]), dtype=np.float64)
    win_tokens = np.zeros((n_win,), dtype=np.float64)
    for w in range(n_win):
        sl = slice(w * k, (w + 1) * k)
        w_sum = float(weights[sl].sum())
        win_tokens[w] = w_sum
        win_vecs[w] = (grads[sl].astype(np.float64) * weights[sl, None]).sum(axis=0) / w_sum

    win_res = subspace.project_out(win_vecs)

    ranks = []
    p_ranks = []
    z_scores = []
    hits_5 = 0
    hits_1 = 0
    hits_10 = 0
    for w in range(n_win):
        scores = cosine_similarities(win_res[w], bank_res)
        rt = rank_test(scores, claimed_idx=claimed_idx)
        ranks.append(rt["rank"])
        p_ranks.append(rt["p_rank"])
        z_scores.append(rt["z_score"])
        if rt["p_rank"] <= 0.05:
            hits_5 += 1
        if rt["p_rank"] <= 0.01:
            hits_1 += 1
        if rt["p_rank"] <= 0.10:
            hits_10 += 1

    return {
        "window_size_prompts": int(window_size),
        "num_windows": int(n_win),
        "mean_tokens_per_window": float(np.mean(win_tokens)),
        "tpr_at_5pct": float(hits_5 / n_win),
        "tpr_at_1pct": float(hits_1 / n_win),
        "tpr_at_10pct": float(hits_10 / n_win),
        "hits_at_5pct": int(hits_5),
        "hits_at_1pct": int(hits_1),
        "mean_rank": float(np.mean(ranks)),
        "median_rank": float(np.median(ranks)),
        "mean_z_score": float(np.mean(z_scores)),
        "std_z_score": float(np.std(z_scores)),
        "min_rank": int(np.min(ranks)),
        "max_rank": int(np.max(ranks)),
    }


def main() -> None:
    args = parse_args()
    for ws in args.window_sizes:
        if ws % args.micro_size != 0:
            raise ValueError(f"--window-sizes {ws} is not divisible by --micro-size {args.micro_size}")

    if args.suspects == ["ALL"]:
        mw_root = args.work_dir / "suspects_mw"
        suspect_names = sorted(p.name for p in mw_root.iterdir() if p.is_dir() and list(p.glob("responses_win_*.jsonl")))
    else:
        suspect_names = args.suspects

    # Load PCA + 200-key reference bank once
    subspace = TaskSubspace.load(args.work_dir / "pca" / "task_subspace.npz")
    keys_info = read_json(args.work_dir / "keys.json")
    bank_dir = args.work_dir / "grads" / "bank"
    bank_vecs = [np.load(bank_dir / f"key_{idx:04d}_{hk}.npy") for idx, hk in enumerate(keys_info["keys"])]
    bank_res = subspace.project_out(np.stack(bank_vecs, axis=0))
    claimed_idx = int(keys_info["true_key_idx"])
    num_keys = len(keys_info["keys"])

    probe_bundle: list = []
    all_results: dict[str, list[dict]] = {}

    try:
        for name in suspect_names:
            grads, weights, _ = extract_or_load_micro_blocks(
                work_dir=args.work_dir,
                suspect_name=name,
                micro_size=args.micro_size,
                max_prompt_tokens=args.max_prompt_tokens,
                batch_size=args.batch_size,
                overwrite=args.overwrite_cache,
                probe_bundle=probe_bundle,
            )
            res_list = []
            for ws in args.window_sizes:
                res_list.append(
                    evaluate_window_size(
                        grads=grads,
                        weights=weights,
                        micro_size=args.micro_size,
                        window_size=ws,
                        subspace=subspace,
                        bank_res=bank_res,
                        claimed_idx=claimed_idx,
                    )
                )
            all_results[name] = res_list
    finally:
        if probe_bundle:
            del probe_bundle[1]  # model
            probe_bundle.clear()
            gc.collect()
            try:
                import torch

                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            except Exception:
                pass

    print(f"\n=== Window-Size Comparison (K = {num_keys} keys, PCA q = {subspace.q}) ===")
    header = (
        f"{'Suspect':26s} | {'Prompts/Win':>11s} | {'#Wins':>5s} | {'Tok/Win':>8s} | "
        f"{'TPR@5%':>14s} | {'TPR@1%':>14s} | {'MedRank':>8s} | {'Mean z ± std':>14s}"
    )
    print(header)
    print("-" * len(header))
    for name, res_list in all_results.items():
        for r in res_list:
            t5 = f"{r['tpr_at_5pct']*100:5.1f}% ({r['hits_at_5pct']}/{r['num_windows']})"
            t1 = f"{r['tpr_at_1pct']*100:5.1f}% ({r['hits_at_1pct']}/{r['num_windows']})"
            z_str = f"{r['mean_z_score']:+.2f} ± {r['std_z_score']:.2f}"
            print(
                f"{name:26s} | {r['window_size_prompts']:11d} | {r['num_windows']:5d} | "
                f"{r['mean_tokens_per_window']/1000:7.1f}k | {t5:>14s} | {t1:>14s} | "
                f"{r['median_rank']:5.1f}/{num_keys:<3d} | {z_str:>14s}"
            )
        print("-" * len(header))

    if args.out_json is not None:
        write_json(args.out_json, {"num_keys": num_keys, "pca_q": subspace.q, "results": all_results})
        print(f"[probe_ws] Saved JSON report -> {args.out_json}")


if __name__ == "__main__":
    main()
