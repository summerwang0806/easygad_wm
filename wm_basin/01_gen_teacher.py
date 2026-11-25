#!/usr/bin/env python3
"""Step 1: Generate teacher traces with Qwen2.5-14B-Instruct via vLLM.

Modes:
  - warm: Unwatermarked (clean) teacher traces on X_build_warm.jsonl for probe warm-up.
  - bank: KGW-watermarked teacher traces on X_build_bank.jsonl for keys[key_start:key_end].

Supports resume (skips already-generated key files) and incremental key expansion.
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

# vLLM V0 engine is required for per-request Python logits_processors (KGW).
os.environ.setdefault("VLLM_USE_V1", "0")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from wm_basin.core import (
    DEFAULT_DELTA,
    DEFAULT_GAMMA,
    DEFAULT_MAX_RESPONSE_TOKENS,
    DEFAULT_TEACHER_MODEL,
    make_cached_kgw_processor,
    read_json,
    read_jsonl,
    render_prompt_with_fallback,
    write_jsonl,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate clean (warm) or KGW-keyed (bank) teacher traces")
    p.add_argument("--work-dir", type=Path, default=Path("wm_basin_work"))
    p.add_argument("--mode", choices=["warm", "bank", "both"], default="both")
    p.add_argument("--teacher-model", type=str, default=DEFAULT_TEACHER_MODEL)
    p.add_argument("--key-start", type=int, default=0, help="Start key index (inclusive) in keys.json")
    p.add_argument("--key-end", type=int, default=None, help="End key index (exclusive); defaults to all keys")
    p.add_argument("--temperature", type=float, default=0.7, help="Match distillation teacher temperature (0.7)")
    p.add_argument("--top-p", type=float, default=0.9, help="Match distillation teacher top-p (0.9)")
    p.add_argument("--max-prompt-tokens", type=int, default=2048)
    p.add_argument("--max-new-tokens", type=int, default=DEFAULT_MAX_RESPONSE_TOKENS)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--gamma", type=float, default=DEFAULT_GAMMA)
    p.add_argument("--delta", type=float, default=DEFAULT_DELTA)
    p.add_argument("--keys-per-chunk", type=int, default=4, help="How many keys to batch together in one llm.generate")
    p.add_argument("--gpu-memory-utilization", type=float, default=0.72)
    p.add_argument("--tensor-parallel-size", type=int, default=1)
    p.add_argument("--overwrite", action="store_true")
    return p.parse_args()


def run_warm(llm, tokenizer, args: argparse.Namespace) -> None:
    from vllm import SamplingParams

    out_path = args.work_dir / "teacher_warm" / "clean_traces.jsonl"
    if out_path.exists() and not args.overwrite:
        print(f"[warm] Already exists: {out_path}, skipping.")
        return

    rows = read_jsonl(args.work_dir / "pools" / "X_build_warm.jsonl")
    prompts = [render_prompt_with_fallback(tokenizer, r["messages"], args.max_prompt_tokens) for r in rows]
    sp_list = [
        SamplingParams(
            n=1,
            temperature=args.temperature,
            top_p=args.top_p,
            max_tokens=args.max_new_tokens,
            seed=args.seed + r["prompt_idx"],
            skip_special_tokens=True,
        )
        for r in rows
    ]

    t0 = time.time()
    outputs = llm.generate(prompts, sampling_params=sp_list, use_tqdm=True)
    saved = []
    for r, req in zip(rows, outputs):
        text = req.outputs[0].text
        saved.append(
            {
                "id": r["id"],
                "prompt_idx": r["prompt_idx"],
                "messages": r["messages"],
                "response": text,
                "num_tokens": len(req.outputs[0].token_ids),
                "watermarked": False,
                "hash_key": None,
            }
        )
    write_jsonl(out_path, saved)
    print(f"[warm] Saved {len(saved)} clean traces to {out_path} in {time.time() - t0:.1f}s")


def run_bank(llm, tokenizer, args: argparse.Namespace) -> None:
    from vllm import SamplingParams

    keys_info = read_json(args.work_dir / "keys.json")
    all_keys: list[int] = keys_info["keys"]
    k_start = max(0, args.key_start)
    k_end = len(all_keys) if args.key_end is None else min(len(all_keys), args.key_end)
    if k_start >= k_end:
        print(f"[bank] Empty key range [{k_start}, {k_end}), nothing to do.")
        return

    bank_dir = args.work_dir / "teacher_bank"
    bank_dir.mkdir(parents=True, exist_ok=True)

    pending: list[tuple[int, int, Path]] = []
    for k_idx in range(k_start, k_end):
        hk = int(all_keys[k_idx])
        out_path = bank_dir / f"key_{k_idx:04d}_{hk}.jsonl"
        if out_path.exists() and not args.overwrite:
            continue
        pending.append((k_idx, hk, out_path))

    if not pending:
        print(f"[bank] All keys in [{k_start}, {k_end}) already generated.")
        return

    rows = read_jsonl(args.work_dir / "pools" / "X_build_bank.jsonl")
    prompts = [render_prompt_with_fallback(tokenizer, r["messages"], args.max_prompt_tokens) for r in rows]
    vocab_size = len(tokenizer)
    print(f"[bank] Generating {len(pending)} pending keys x {len(rows)} prompts (vocab={vocab_size})...")

    for chunk_off in range(0, len(pending), args.keys_per_chunk):
        chunk = pending[chunk_off : chunk_off + args.keys_per_chunk]
        chunk_prompts: list[str] = []
        chunk_params: list[SamplingParams] = []
        chunk_meta: list[tuple[int, int, Path, dict]] = []

        for k_idx, hk, out_path in chunk:
            # One cached processor per key (bit-for-bit identical to wm_data/kgw.py)
            proc = make_cached_kgw_processor(
                vocab_size=vocab_size,
                gamma=args.gamma,
                delta=args.delta,
                hash_key=hk,
            )
            for r, prompt in zip(rows, prompts):
                chunk_prompts.append(prompt)
                # Common random numbers across keys: same seed for same prompt_idx
                chunk_params.append(
                    SamplingParams(
                        n=1,
                        temperature=args.temperature,
                        top_p=args.top_p,
                        max_tokens=args.max_new_tokens,
                        seed=args.seed + r["prompt_idx"],
                        skip_special_tokens=True,
                        logits_processors=[proc],
                    )
                )
                chunk_meta.append((k_idx, hk, out_path, r))

        t0 = time.time()
        outputs = llm.generate(chunk_prompts, sampling_params=chunk_params, use_tqdm=True)
        elapsed = time.time() - t0

        # Group outputs by key and write atomically
        by_key: dict[tuple[int, int, Path], list[dict]] = {}
        for (k_idx, hk, out_path, r), req in zip(chunk_meta, outputs):
            by_key.setdefault((k_idx, hk, out_path), []).append(
                {
                    "id": r["id"],
                    "prompt_idx": r["prompt_idx"],
                    "messages": r["messages"],
                    "response": req.outputs[0].text,  # preserve exact decoded text
                    "num_tokens": len(req.outputs[0].token_ids),
                    "watermarked": True,
                    "key_idx": k_idx,
                    "hash_key": hk,
                }
            )
        for (k_idx, hk, out_path), key_rows in by_key.items():
            write_jsonl(out_path, key_rows)
        key_ids = [c[0] for c in chunk]
        print(f"[bank] Finished keys {key_ids} ({len(outputs)} traces) in {elapsed:.1f}s")


def main() -> None:
    args = parse_args()
    from vllm import LLM

    print(f"[vllm] Loading teacher: {args.teacher_model}")
    llm = LLM(
        model=args.teacher_model,
        tensor_parallel_size=args.tensor_parallel_size,
        gpu_memory_utilization=args.gpu_memory_utilization,
        max_model_len=args.max_prompt_tokens + args.max_new_tokens,
        dtype="bfloat16",
        trust_remote_code=True,
    )
    tokenizer = llm.get_tokenizer()

    if args.mode in ("warm", "both"):
        run_warm(llm, tokenizer, args)
    if args.mode in ("bank", "both"):
        run_bank(llm, tokenizer, args)


if __name__ == "__main__":
    main()
