#!/usr/bin/env python3
"""Step 6: Sample a suspect model on X_test (KGW OFF), extract its probe gradient,
remove the clean task subspace, and compute its WM-Basin rank p-value.

Supports:
  - Full online audit: sample suspect -> extract gradient -> score against bank.
  - --responses-jsonl: reuse existing suspect generations (skip vLLM sampling).
  - --only-score: reuse existing grad.npy (instant re-scoring after expanding bank or refitting PCA).
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


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Audit a suspect model with WM-Basin")
    p.add_argument("--work-dir", type=Path, default=Path("wm_basin_work"))
    p.add_argument("--suspect-name", type=str, required=True, help="Short tag for this suspect (e.g. kgw_gad_05b)")
    p.add_argument("--suspect-model", type=str, default=None, help="Path to suspect HF checkpoint")
    p.add_argument("--test-pool", type=Path, default=None, help="Defaults to <work-dir>/pools/X_test.jsonl")
    p.add_argument("--responses-jsonl", type=Path, default=None, help="Optional pre-generated responses JSONL")
    p.add_argument("--num-samples-per-prompt", type=int, default=4, help="500 prompts x 4 = 2000 responses (~0.4M tokens)")
    p.add_argument("--temperature", type=float, default=1.0)
    p.add_argument("--top-p", type=float, default=0.95)
    p.add_argument("--max-prompt-tokens", type=int, default=2048)
    p.add_argument("--max-new-tokens", type=int, default=DEFAULT_MAX_RESPONSE_TOKENS)
    p.add_argument("--min-response-tokens", type=int, default=DEFAULT_MIN_RESPONSE_TOKENS)
    p.add_argument("--batch-size", type=int, default=1, help="Micro-batch size for probe gradient extraction (1 avoids OOM on long Dolly prompts)")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--gpu-memory-utilization", type=float, default=0.25)
    p.add_argument("--only-score", action="store_true", help="Skip sampling & gradient; re-score existing grad.npy")
    p.add_argument("--overwrite", action="store_true")
    return p.parse_args()


def sample_suspect(args: argparse.Namespace, out_jsonl: Path) -> None:
    import torch
    from vllm import LLM, SamplingParams

    if not args.suspect_model:
        raise ValueError("--suspect-model is required when responses.jsonl does not exist")

    test_pool = args.test_pool or (args.work_dir / "pools" / "X_test.jsonl")
    rows = read_jsonl(test_pool)

    print(f"[suspect] Loading suspect model (KGW OFF): {args.suspect_model}")
    llm = LLM(
        model=args.suspect_model,
        gpu_memory_utilization=args.gpu_memory_utilization,
        max_model_len=args.max_prompt_tokens + args.max_new_tokens,
        dtype="auto",
        trust_remote_code=True,
    )
    tokenizer = llm.get_tokenizer()
    base_prompts = [render_prompt_with_fallback(tokenizer, r["messages"], args.max_prompt_tokens) for r in rows]

    all_prompts: list[str] = []
    all_params: list[SamplingParams] = []
    all_meta: list[tuple[dict, int]] = []
    for sample_idx in range(args.num_samples_per_prompt):
        for r, prompt in zip(rows, base_prompts):
            all_prompts.append(prompt)
            all_params.append(
                SamplingParams(
                    n=1,
                    temperature=args.temperature,
                    top_p=args.top_p,
                    max_tokens=args.max_new_tokens,
                    repetition_penalty=1.0,
                    seed=args.seed + sample_idx * 100_003 + r["prompt_idx"],
                    skip_special_tokens=True,
                )
            )
            all_meta.append((r, sample_idx))

    t0 = time.time()
    outputs = llm.generate(all_prompts, sampling_params=all_params, use_tqdm=True)
    saved = []
    for (r, sample_idx), req in zip(all_meta, outputs):
        saved.append(
            {
                "id": f"{r['id']}__s{sample_idx}",
                "prompt_idx": r["prompt_idx"],
                "sample_idx": sample_idx,
                "messages": r["messages"],
                "response": req.outputs[0].text,
                "num_tokens": len(req.outputs[0].token_ids),
                "suspect_name": args.suspect_name,
                "kgw_enabled_during_generation": False,
            }
        )
    write_jsonl(out_jsonl, saved)
    print(f"[suspect] Sampled {len(saved)} responses to {out_jsonl} in {time.time() - t0:.1f}s")

    if hasattr(llm, "llm_engine") and hasattr(llm.llm_engine, "engine_core"):
        try:
            llm.llm_engine.engine_core.shutdown()
        except Exception:
            pass
    del llm
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def compute_suspect_grad(args: argparse.Namespace, responses_path: Path, grad_path: Path) -> dict:
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
    rows = read_jsonl(responses_path)

    t0 = time.time()
    vec, stats = extract_mod.extract_projected_gradient(
        model=model,
        tokenizer=tokenizer,
        lora_params=lora_params,
        rows=rows,
        projector=projector,
        max_prompt_tokens=args.max_prompt_tokens,
        max_response_tokens=max_resp,
        min_response_tokens=min_resp,
        max_samples=None,  # use all suspect generations
        batch_size=args.batch_size,
        weighting=weighting,
        show_progress=True,
        desc=f"grad:{args.suspect_name}",
    )
    np.save(grad_path, vec)
    write_json(grad_path.with_suffix(".meta.json"), stats)
    print(
        f"[suspect] Extracted grad -> {grad_path} "
        f"(used={stats['num_used_samples']}, tokens={stats['total_scored_tokens']:,}) in {time.time() - t0:.1f}s"
    )
    return stats


def score_suspect(args: argparse.Namespace, grad_path: Path, score_path: Path) -> dict:
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
    if len(bank_vecs) < 2:
        raise RuntimeError(f"Need >= 2 bank gradients in {bank_dir}, found {len(bank_vecs)}")
    if bank_keys[0] != int(keys_info["true_key"]):
        raise RuntimeError("Claimed true key (index 0) gradient is missing from bank!")

    bank_mat = np.stack(bank_vecs, axis=0)
    sus_vec = np.load(grad_path).astype(np.float64)

    # Raw (unprojected) score for ablation reference
    raw_scores = cosine_similarities(sus_vec, bank_mat)
    raw_res = rank_test(raw_scores, claimed_idx=0)

    # Task-subspace-removed (WM-Basin) score
    bank_res = subspace.project_out(bank_mat)
    sus_res = subspace.project_out(sus_vec)
    scores = cosine_similarities(sus_res, bank_res)
    res = rank_test(scores, claimed_idx=0)

    # Top-5 candidate keys for inspection
    top_order = np.argsort(-scores)[:5]
    top5 = [
        {
            "rank": r_i + 1,
            "key_idx": int(k_i),
            "hash_key": bank_keys[int(k_i)],
            "is_claimed": int(k_i) == 0,
            "cosine": float(scores[int(k_i)]),
        }
        for r_i, k_i in enumerate(top_order)
    ]

    report = {
        "suspect_name": args.suspect_name,
        "suspect_model": args.suspect_model,
        "true_key": bank_keys[0],
        "pca_q": subspace.q,
        "wm_basin": res,
        "raw_no_pca": raw_res,
        "top5_keys": top5,
        "flagged_at_5pct": bool(res["p_rank"] <= 0.05),
        "flagged_at_1pct": bool(res["p_rank"] <= 0.01),
    }
    write_json(score_path, report)

    print("=" * 72)
    print(f"WM-Basin Audit Report: {args.suspect_name}")
    print(f"  Keys in bank : {res['num_keys']} (k*={bank_keys[0]}, p_floor={res['p_floor']:.4f}, PCA q={subspace.q})")
    print(f"  WM-Basin     : rank={res['rank']}/{res['num_keys']} | p_rank={res['p_rank']:.4f} | "
          f"S(k*)={res['claimed_score']:.5f} (z={res['z_score']:+.2f})")
    print(f"  Raw (no PCA) : rank={raw_res['rank']}/{raw_res['num_keys']} | p_rank={raw_res['p_rank']:.4f}")
    print(f"  Verdict @5%  : {'DISTILLED (flagged)' if report['flagged_at_5pct'] else 'No evidence'}")
    print("=" * 72)
    return report


def main() -> None:
    args = parse_args()
    sus_dir = args.work_dir / "suspects" / args.suspect_name
    sus_dir.mkdir(parents=True, exist_ok=True)
    responses_path = args.responses_jsonl or (sus_dir / "responses.jsonl")
    grad_path = sus_dir / "grad.npy"
    score_path = sus_dir / "score.json"

    if not args.only_score:
        if not responses_path.exists() or args.overwrite:
            sample_suspect(args, responses_path)
        else:
            print(f"[suspect] Reusing existing responses: {responses_path}")

        if not grad_path.exists() or args.overwrite:
            compute_suspect_grad(args, responses_path, grad_path)
        else:
            print(f"[suspect] Reusing existing gradient: {grad_path}")

    score_suspect(args, grad_path, score_path)


if __name__ == "__main__":
    main()
