#!/usr/bin/env python3
"""Step 0: Build disjoint prompt pools (X_build, X_test) and keys.json.

- X_build/{warm,bank,pca}.jsonl and X_test_ext.jsonl are sampled from an external
  general instruction dataset (default: yahma/alpaca-cleaned), deduplicated
  against both Dolly-15k train and test prompts so there is zero prompt overlap.
- X_test.jsonl is exported directly from data/dolly15k_test.parquet (500 rows).
- keys.json stores [true_key, decoy_1, ..., decoy_M]. Re-running with a larger
  --num-keys preserves existing keys verbatim and appends new decoys only.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from wm_basin.core import (
    DEFAULT_GAMMA,
    DEFAULT_DELTA,
    DEFAULT_TRUE_KEY,
    build_messages,
    generate_keys,
    normalize_text_for_dedup,
    read_json,
    write_json,
    write_jsonl,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Prepare WM-Basin prompt pools and keys.json")
    p.add_argument("--work-dir", type=Path, default=Path("wm_basin_work"), help="Output workspace directory")
    p.add_argument("--dolly-train", type=Path, default=Path("data/dolly15k_train.parquet"))
    p.add_argument("--dolly-test", type=Path, default=Path("data/dolly15k_test.parquet"))
    p.add_argument(
        "--alpaca-path",
        type=str,
        default=None,
        help="Optional local path to alpaca-cleaned (.json/.jsonl/.parquet/HF disk dir). "
             "If omitted, downloads 'yahma/alpaca-cleaned' via HuggingFace datasets.",
    )
    p.add_argument("--hf-dataset", type=str, default="yahma/alpaca-cleaned")
    p.add_argument("--num-keys", type=int, default=40, help="Total keys (1 true + M decoys). Pilot=40, Full=100.")
    p.add_argument("--true-key", type=int, default=DEFAULT_TRUE_KEY)
    p.add_argument("--warm-size", type=int, default=450)
    p.add_argument("--bank-size", type=int, default=576, help="512 target + 64 buffer for short-response filtering")
    p.add_argument("--pca-size", type=int, default=512)
    p.add_argument("--ext-test-size", type=int, default=500, help="Disjoint external test set for cross-check")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--only-expand-keys", action="store_true", help="Only expand keys.json without touching pools")
    p.add_argument("--overwrite-pools", action="store_true", help="Overwrite existing prompt pool files")
    return p.parse_args()


def extract_user_text(messages: list[dict]) -> str:
    return "\n".join(m.get("content", "") for m in messages if m.get("role") == "user")


def load_dolly_dedup_set(paths: list[Path]) -> set[str]:
    seen: set[str] = set()
    for p in paths:
        if not p.exists():
            print(f"[warn] Dolly parquet not found for dedup: {p}")
            continue
        table = pq.read_table(p, columns=["content"])
        for row in table.to_pylist():
            seen.add(normalize_text_for_dedup(extract_user_text(row["content"])))
    return seen


def load_external_instructions(alpaca_path: str | None, hf_dataset: str) -> list[tuple[str, str]]:
    """Return list of (instruction, context) tuples from local file or HuggingFace."""
    records: list[dict] = []
    if alpaca_path is not None:
        path = Path(alpaca_path)
        if not path.exists():
            raise FileNotFoundError(f"--alpaca-path not found: {path}")
        if path.is_dir():
            from datasets import load_from_disk
            ds = load_from_disk(str(path))
            if hasattr(ds, "keys") and "train" in ds:
                ds = ds["train"]
            records = list(ds)
        elif path.suffix == ".json":
            records = json.loads(path.read_text(encoding="utf-8"))
        elif path.suffix == ".jsonl":
            records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        elif path.suffix == ".parquet":
            records = pq.read_table(path).to_pylist()
        else:
            raise ValueError(f"Unsupported --alpaca-path format: {path}")
    else:
        from datasets import load_dataset
        ds = load_dataset(hf_dataset, split="train")
        records = list(ds)

    pairs: list[tuple[str, str]] = []
    for r in records:
        instr = (r.get("instruction") or r.get("prompt") or "").strip()
        ctx = (r.get("input") or r.get("context") or "").strip()
        if instr:
            pairs.append((instr, ctx))
    return pairs


def export_dolly_test(dolly_test_path: Path, out_path: Path) -> int:
    if not dolly_test_path.exists():
        raise FileNotFoundError(f"Dolly test parquet not found: {dolly_test_path}")
    table = pq.read_table(dolly_test_path, columns=["id", "content"])
    rows = []
    for idx, row in enumerate(table.to_pylist()):
        rows.append(
            {
                "id": str(row["id"]),
                "prompt_idx": idx,
                "source": "dolly15k_test",
                "messages": row["content"],
            }
        )
    return write_jsonl(out_path, rows)


def main() -> None:
    args = parse_args()
    work_dir: Path = args.work_dir
    work_dir.mkdir(parents=True, exist_ok=True)

    # 1. Generate or incrementally expand keys.json
    keys_path = work_dir / "keys.json"
    existing_keys = None
    if keys_path.exists():
        payload = read_json(keys_path)
        existing_keys = payload["keys"]
        if len(existing_keys) >= args.num_keys:
            print(f"[keys] {keys_path} already has {len(existing_keys)} keys (>= {args.num_keys}), keeping as-is.")
        else:
            print(f"[keys] Expanding {keys_path} from {len(existing_keys)} -> {args.num_keys} keys.")
    keys = generate_keys(
        total_keys=max(args.num_keys, len(existing_keys) if existing_keys else 0),
        true_key=args.true_key,
        seed=args.seed,
        existing_keys=existing_keys,
    )
    write_json(
        keys_path,
        {
            "scheme": "kgw_simple_1",
            "gamma": DEFAULT_GAMMA,
            "delta": DEFAULT_DELTA,
            "true_key": args.true_key,
            "true_key_idx": 0,
            "seed": args.seed,
            "num_keys": len(keys),
            "keys": keys,
        },
    )
    print(f"[keys] Saved {len(keys)} keys to {keys_path} (k*={keys[0]} at idx 0)")

    if args.only_expand_keys:
        return

    # 2. Prepare disjoint prompt pools
    pools_dir = work_dir / "pools"
    warm_path = pools_dir / "X_build_warm.jsonl"
    bank_path = pools_dir / "X_build_bank.jsonl"
    pca_path = pools_dir / "X_build_pca.jsonl"
    test_path = pools_dir / "X_test.jsonl"
    ext_test_path = pools_dir / "X_test_ext.jsonl"

    if all(p.exists() for p in (warm_path, bank_path, pca_path, test_path)) and not args.overwrite_pools:
        print(f"[pools] All pools already exist under {pools_dir}. Pass --overwrite-pools to regenerate.")
        return

    dolly_seen = load_dolly_dedup_set([args.dolly_train, args.dolly_test])
    print(f"[dedup] Loaded {len(dolly_seen)} unique Dolly prompts for exclusion.")

    raw_pairs = load_external_instructions(args.alpaca_path, args.hf_dataset)
    rng = random.Random(args.seed)
    rng.shuffle(raw_pairs)

    need_total = args.warm_size + args.bank_size + args.pca_size + args.ext_test_size
    clean_rows: list[dict] = []
    seen_ext: set[str] = set()
    for instr, ctx in raw_pairs:
        messages = build_messages(instr, ctx)
        norm = normalize_text_for_dedup(extract_user_text(messages))
        if norm in dolly_seen or norm in seen_ext:
            continue
        seen_ext.add(norm)
        clean_rows.append(
            {
                "id": f"ext-{len(clean_rows):05d}",
                "source": args.alpaca_path or args.hf_dataset,
                "messages": messages,
            }
        )
        if len(clean_rows) >= need_total:
            break

    if len(clean_rows) < need_total:
        raise RuntimeError(f"Only found {len(clean_rows)} deduplicated external prompts, need {need_total}")

    def slice_pool(start: int, size: int, pool_name: str) -> list[dict]:
        out = []
        for i, item in enumerate(clean_rows[start : start + size]):
            row = dict(item)
            row["pool"] = pool_name
            row["prompt_idx"] = i
            out.append(row)
        return out

    c0 = 0
    warm_rows = slice_pool(c0, args.warm_size, "X_build_warm"); c0 += args.warm_size
    bank_rows = slice_pool(c0, args.bank_size, "X_build_bank"); c0 += args.bank_size
    pca_rows = slice_pool(c0, args.pca_size, "X_build_pca"); c0 += args.pca_size
    ext_rows = slice_pool(c0, args.ext_test_size, "X_test_ext")

    write_jsonl(warm_path, warm_rows)
    write_jsonl(bank_path, bank_rows)
    write_jsonl(pca_path, pca_rows)
    write_jsonl(ext_test_path, ext_rows)
    n_test = export_dolly_test(args.dolly_test, test_path)

    write_json(
        pools_dir / "manifest.json",
        {
            "seed": args.seed,
            "external_source": args.alpaca_path or args.hf_dataset,
            "dolly_train": str(args.dolly_train),
            "dolly_test": str(args.dolly_test),
            "counts": {
                "X_build_warm": len(warm_rows),
                "X_build_bank": len(bank_rows),
                "X_build_pca": len(pca_rows),
                "X_test": n_test,
                "X_test_ext": len(ext_rows),
            },
        },
    )
    print(
        f"[pools] Written under {pools_dir}: "
        f"warm={len(warm_rows)}, bank={len(bank_rows)}, pca={len(pca_rows)}, "
        f"X_test={n_test}, X_test_ext={len(ext_rows)}"
    )


if __name__ == "__main__":
    main()
