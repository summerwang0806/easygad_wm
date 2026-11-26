#!/usr/bin/env python3
"""Step 2: Generate clean PCA pool responses across off-the-shelf models x 3 temperatures.

- Preset 'pilot': 10 fast local models x 3 temps = 30 clean cells.
- Preset 'full':  20 local models (6 families) x 3 temps = 60 clean cells.
- Supports resume (skips completed model__T{temp}.jsonl) and incremental expansion.
"""

from __future__ import annotations

import argparse
import gc
import sys
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from wm_basin.core import (
    DEFAULT_CLEAN_TEMPERATURES,
    DEFAULT_MAX_RESPONSE_TOKENS,
    DEFAULT_PUBLIC_MODELS_DIR,
    FULL_CLEAN_MODELS,
    PILOT_CLEAN_MODELS,
    read_jsonl,
    render_prompt_with_fallback,
    write_jsonl,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate Clean PCA Pool responses (unwatermarked)")
    p.add_argument("--work-dir", type=Path, default=Path("wm_basin_work"))
    p.add_argument("--models-dir", type=Path, default=Path(DEFAULT_PUBLIC_MODELS_DIR))
    p.add_argument("--preset", choices=["pilot", "full"], default="pilot")
    p.add_argument(
        "--models",
        nargs="+",
        default=None,
        help="Optional explicit list of model directory names under --models-dir (overrides --preset)",
    )
    p.add_argument("--temperatures", nargs="+", type=float, default=DEFAULT_CLEAN_TEMPERATURES)
    p.add_argument("--top-p", type=float, default=0.95)
    p.add_argument("--max-prompt-tokens", type=int, default=2048)
    p.add_argument("--max-new-tokens", type=int, default=DEFAULT_MAX_RESPONSE_TOKENS)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--gpu-memory-utilization", type=float, default=0.75)
    p.add_argument("--overwrite", action="store_true")
    return p.parse_args()


def safe_tag(name: str) -> str:
    return name.replace("/", "__").replace(" ", "_")


def generate_for_model(
    model_name: str,
    model_path: Path,
    rows: list[dict],
    out_dir: Path,
    args: argparse.Namespace,
) -> None:
    import torch
    from vllm import LLM, SamplingParams

    tag = safe_tag(model_name)
    pending_temps = []
    for temp in args.temperatures:
        out_path = out_dir / f"{tag}__T{temp:.1f}.jsonl"
        if out_path.exists() and not args.overwrite:
            continue
        pending_temps.append((temp, out_path))

    if not pending_temps:
        print(f"[clean_pool] {model_name}: all temperatures already done, skipping.")
        return

    print(f"[clean_pool] Loading {model_name} from {model_path} for temps {[t for t, _ in pending_temps]}...")
    t_load = time.time()
    llm = LLM(
        model=str(model_path),
        gpu_memory_utilization=args.gpu_memory_utilization,
        max_model_len=args.max_prompt_tokens + args.max_new_tokens,
        dtype="auto",
        trust_remote_code=True,
    )
    tokenizer = llm.get_tokenizer()
    prompts = [render_prompt_with_fallback(tokenizer, r["messages"], args.max_prompt_tokens) for r in rows]
    print(f"[clean_pool] Loaded {model_name} in {time.time() - t_load:.1f}s")

    try:
        for temp, out_path in pending_temps:
            t0 = time.time()
            sp_list = [
                SamplingParams(
                    n=1,
                    temperature=temp,
                    top_p=args.top_p,
                    max_tokens=args.max_new_tokens,
                    seed=args.seed + r["prompt_idx"] + int(round(temp * 1000)),
                    skip_special_tokens=True,
                )
                for r in rows
            ]
            outputs = llm.generate(prompts, sampling_params=sp_list, use_tqdm=True)
            saved = []
            for r, req in zip(rows, outputs):
                saved.append(
                    {
                        "id": r["id"],
                        "prompt_idx": r["prompt_idx"],
                        "messages": r["messages"],
                        "response": req.outputs[0].text,
                        "num_tokens": len(req.outputs[0].token_ids),
                        "model_name": model_name,
                        "temperature": temp,
                    }
                )
            write_jsonl(out_path, saved)
            print(f"[clean_pool] Saved {out_path.name} ({len(saved)} rows) in {time.time() - t0:.1f}s")
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


def main() -> None:
    args = parse_args()
    model_names = args.models if args.models else (PILOT_CLEAN_MODELS if args.preset == "pilot" else FULL_CLEAN_MODELS)
    rows = read_jsonl(args.work_dir / "pools" / "X_build_pca.jsonl")
    out_dir = args.work_dir / "clean_pool"
    out_dir.mkdir(parents=True, exist_ok=True)

    failed: list[str] = []
    for name in model_names:
        model_path = args.models_dir / name
        if not model_path.exists():
            print(f"[warn] Model path not found, skipping: {model_path}")
            failed.append(name)
            continue
        try:
            generate_for_model(name, model_path, rows, out_dir, args)
        except Exception as exc:
            print(f"[error] Failed on {name}: {exc}")
            traceback.print_exc()
            failed.append(name)

    if failed:
        print(f"[clean_pool] Finished with {len(failed)} skipped/failed models: {failed}")
    else:
        print(f"[clean_pool] All {len(model_names)} models finished successfully.")


if __name__ == "__main__":
    main()
