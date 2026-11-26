#!/usr/bin/env python3
"""Step 8: Build G disjoint, matched-domain audit windows (e.g. 20 x 1,000 prompts).

Strictly excludes:
  - All Dolly-15k train and test prompts
  - All X_build/{warm,bank,pca}.jsonl prompts used to construct the detector

Each window is saved as <work-dir>/pools/audit_windows/window_XX.jsonl with zero
prompt overlap across windows, enabling rigorous, trick-free TPR@5%FPR & TPR@1%FPR
evaluation across G independent black-box audit trials.
"""

from __future__ import annotations

import argparse
import importlib.util
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from wm_basin.core import (
    build_messages,
    normalize_text_for_dedup,
    read_jsonl,
    sha256_file,
    write_json,
    write_jsonl,
)


def _import_step0():
    spec = importlib.util.spec_from_file_location(
        "wm_basin_step0",
        Path(__file__).resolve().parent / "00_prepare_pools.py",
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build disjoint multi-window audit prompt pools")
    p.add_argument("--work-dir", type=Path, default=Path("wm_basin_work"))
    p.add_argument("--dolly-train", type=Path, default=Path("data/dolly15k_train.parquet"))
    p.add_argument("--dolly-test", type=Path, default=Path("data/dolly15k_test.parquet"))
    p.add_argument("--alpaca-path", type=str, default=None)
    p.add_argument("--hf-dataset", type=str, default="yahma/alpaca-cleaned")
    p.add_argument("--num-windows", type=int, default=20, help="Number of disjoint audit windows (default: 20)")
    p.add_argument("--prompts-per-window", type=int, default=1000, help="Unique prompts per window (default: 1000)")
    p.add_argument("--seed", type=int, default=2026)
    p.add_argument("--overwrite", action="store_true")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    if args.num_windows < 2 or args.prompts_per_window < 10:
        raise ValueError("Need >=2 windows and >=10 prompts per window")

    out_dir = args.work_dir / "pools" / "audit_windows"
    manifest_path = out_dir / "manifest.json"
    expected_files = [out_dir / f"window_{w:02d}.jsonl" for w in range(args.num_windows)]
    if manifest_path.exists() and all(f.exists() for f in expected_files) and not args.overwrite:
        print(f"[windows] All {args.num_windows} audit windows already exist in {out_dir}. Pass --overwrite to rebuild.")
        return

    step0 = _import_step0()

    # 1. Exclude all Dolly prompts + all X_build prompts
    excluded: set[str] = step0.load_dolly_dedup_set([args.dolly_train, args.dolly_test])
    build_files = [
        args.work_dir / "pools" / "X_build_warm.jsonl",
        args.work_dir / "pools" / "X_build_bank.jsonl",
        args.work_dir / "pools" / "X_build_pca.jsonl",
    ]
    for bf in build_files:
        if not bf.exists():
            raise FileNotFoundError(f"Missing build pool {bf}; run 00_prepare_pools.py first")
        for r in read_jsonl(bf):
            excluded.add(normalize_text_for_dedup(step0.extract_user_text(r["messages"])))
    print(f"[windows] Exclusion set size (Dolly + X_build): {len(excluded):,}")

    # 2. Load external instruction pool and filter out excluded + duplicates
    raw_pairs = step0.load_external_instructions(args.alpaca_path, args.hf_dataset)
    rng = random.Random(args.seed)
    rng.shuffle(raw_pairs)

    need_total = args.num_windows * args.prompts_per_window
    selected: list[dict] = []
    for instr, ctx in raw_pairs:
        messages = build_messages(instr, ctx)
        norm = normalize_text_for_dedup(step0.extract_user_text(messages))
        if norm in excluded:
            continue
        excluded.add(norm)
        selected.append(
            {
                "source": args.alpaca_path or args.hf_dataset,
                "messages": messages,
            }
        )
        if len(selected) >= need_total:
            break

    if len(selected) < need_total:
        raise RuntimeError(f"Only found {len(selected):,} unique prompts after dedup, need {need_total:,}")

    out_dir.mkdir(parents=True, exist_ok=True)
    win_records = []
    for w in range(args.num_windows):
        start = w * args.prompts_per_window
        chunk = selected[start : start + args.prompts_per_window]
        rows = []
        for idx, item in enumerate(chunk):
            rows.append(
                {
                    "id": f"mw-w{w:02d}-{idx:04d}",
                    "window_idx": w,
                    "prompt_idx": idx,
                    "pool": f"audit_window_{w:02d}",
                    "source": item["source"],
                    "messages": item["messages"],
                }
            )
        fp = out_dir / f"window_{w:02d}.jsonl"
        write_jsonl(fp, rows)
        win_records.append(
            {
                "window_idx": w,
                "file": fp.name,
                "num_prompts": len(rows),
                "sha256": sha256_file(fp),
            }
        )

    write_json(
        manifest_path,
        {
            "seed": args.seed,
            "source": args.alpaca_path or args.hf_dataset,
            "num_windows": args.num_windows,
            "prompts_per_window": args.prompts_per_window,
            "total_prompts": need_total,
            "windows": win_records,
        },
    )
    print(
        f"[windows] Created {args.num_windows} strictly disjoint windows "
        f"({args.prompts_per_window} prompts each, {need_total:,} total) in {out_dir}"
    )


if __name__ == "__main__":
    main()
