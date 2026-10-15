#!/usr/bin/env python3
"""Audit raw and unique-bigram KGW p-values using a local tokenizer and CUDA."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import math
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
WM_TEST = ROOT / "wm_test"
OUTPUT = Path(__file__).resolve().parent
sys.path.insert(0, str(WM_TEST))

from evaluate_compare_metrics import (  # noqa: E402
    LegacyRescorer,
    P_VALUE_SCHEMA,
    load_detection_config,
    load_pvalue_records,
    p_from_z,
    summarize_pvalues,
)


def sha256(path: Path) -> str:
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def same_number(actual: Any, expected: Any, label: str) -> None:
    if actual is None or expected is None:
        require(actual is expected, f"{label}: {actual!r} != {expected!r}")
    else:
        require(
            math.isfinite(float(actual))
            and math.isclose(float(actual), float(expected), rel_tol=1e-12, abs_tol=1e-15),
            f"{label}: {actual!r} != {expected!r}",
        )


def read_source(path: Path) -> tuple[list[dict[str, Any]], str, dict[str, Any]]:
    digest = sha256(path)
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    require(len(rows) == 500, f"Expected 500 samples in {path}, found {len(rows)}")
    ids = [row.get("id") for row in rows]
    require(all(isinstance(value, str) and value for value in ids), f"Missing sample ID in {path}")
    require(len(set(ids)) == 500, f"Duplicate sample IDs in {path}")
    for row in rows:
        require(all(key in row for key in ("num_tokens", "green_tokens", "z_score")),
                f"Missing raw counts or z-score for {path.name}:{row['id']}")
    # Also checks every saved z-score against its counts and detector configuration.
    config = load_detection_config(path)
    require(sha256(path) == digest, f"Source changed during validation: {path}")
    return rows, digest, config


class AuditedRescorer(LegacyRescorer):
    """Check both integer counts in addition to LegacyRescorer's raw z check."""

    def score(self, row: dict[str, Any], config_override: dict[str, Any] | None = None) -> dict[str, Any]:
        require(config_override is None, "This audit must retain the original detector configuration")
        result = super().score(row)
        for key in ("num_tokens", "green_tokens"):
            require(result[key] == row[key],
                    f"Rescored {key} differs for {row['id']}: {result[key]} != {row[key]}")
        same_number(result["z_score"], row["z_score"], f"Rescored raw z for {row['id']}")
        return result


def verify_records(rows: list[dict[str, Any]], records: list[dict[str, Any]], digest: str) -> None:
    require(len(records) == len(rows), "Cache and source sample counts differ")
    for row, record in zip(rows, records):
        sample_id = row["id"]
        require(record.get("id") == sample_id, f"Cache sample ID mismatch for {sample_id}")
        require(record.get("schema") == P_VALUE_SCHEMA, f"Cache schema mismatch for {sample_id}")
        require(record.get("source_sha256") == digest, f"Cache source hash mismatch for {sample_id}")
        require(record.get("label") == row["label"], f"Cache label mismatch for {sample_id}")
        require(record.get("num_tokens_raw") == row["num_tokens"], f"Cache raw count mismatch for {sample_id}")
        same_number(record.get("z_score_raw"), row["z_score"], f"Cache raw z for {sample_id}")
        expected_p = p_from_z(row["z_score"]) if row["num_tokens"] else None
        same_number(record.get("p_value_raw"), expected_p, f"Cache raw p for {sample_id}")
        dedup_n = record.get("num_tokens_dedup")
        require(type(dedup_n) is int and 0 <= dedup_n <= row["num_tokens"],
                f"Invalid deduplicated token count for {sample_id}")
        require((record.get("z_score_dedup") is None) == (dedup_n == 0),
                f"Invalid deduplicated z/empty count for {sample_id}")
        same_number(record.get("p_value_dedup"), p_from_z(record.get("z_score_dedup")),
                    f"Cache deduplicated p for {sample_id}")


def runtime_metadata(tokenizer: Path, device: str) -> dict[str, Any]:
    import torch

    token_files = {
        str(path.relative_to(tokenizer)): sha256(path)
        for path in sorted(tokenizer.rglob("*"))
        if path.is_file() and path.suffix.lower() in {".json", ".txt", ".jinja", ".model", ".tiktoken"}
    }
    versions = {}
    for package in ("torch", "transformers", "tokenizers"):
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package] = None
    return {
        "python": sys.version,
        "packages": versions,
        "torch_cuda_version": torch.version.cuda,
        "score_device": device,
        "cuda_device_name": torch.cuda.get_device_name(torch.device(device)) if torch.cuda.is_available() else None,
        "tokenizer_path": str(tokenizer),
        "tokenizer_files_sha256": token_files,
        "tokenizer_loading": "AutoTokenizer.from_pretrained(local_files_only=True); no model weights loaded",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tokenizer", type=Path, required=True, help="Existing local tokenizer directory")
    parser.add_argument("--score-device", default="cuda")
    parser.add_argument("--inputs", type=Path, nargs="+", default=[
        WM_TEST / "kgw_warmup_qwen2_5_0_5b_dolly15k_test.jsonl",
        WM_TEST / "kgw_gad_qwen2_5_0_5b_dolly15k_test.jsonl",
    ])
    parser.add_argument("--limit-check", type=int, default=0,
                        help="Rescore first N samples per input; print checks and write no results")
    args = parser.parse_args()
    args.tokenizer = args.tokenizer.resolve()
    require(args.tokenizer.is_dir(), "--tokenizer must be an existing directory")
    require(str(args.score_device).startswith("cuda"), "Original KGW detection requires the CUDA RNG")
    require(0 <= args.limit_check <= 500, "--limit-check must be between 0 and 500")
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    sources = [(path.resolve(), *read_source(path.resolve())) for path in args.inputs]
    rescorer = AuditedRescorer(args)

    if args.limit_check:
        for path, rows, digest, _config in sources:
            for row in rows[:args.limit_check]:
                score = rescorer.score(row)
                print(json.dumps({
                    "file": str(path), "id": row["id"], "raw_counts_and_z_match": True,
                    "saved_num_tokens": row["num_tokens"], "saved_green_tokens": row["green_tokens"],
                    "saved_z_score": row["z_score"], "rescored": score,
                }, ensure_ascii=False, allow_nan=False), flush=True)
            require(sha256(path) == digest, f"Source changed during check: {path}")
        return

    summary: dict[str, Any] = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "schema": P_VALUE_SCHEMA,
        "method": "Mean of valid per-answer p = 0.5 * erfc(z / sqrt(2)); deduplicate (previous_token_id, token_id)",
        "runtime": runtime_metadata(args.tokenizer, args.score_device),
        "inputs": [],
    }
    table = ["| 模型/方式 | 有效样本（原始/去重） | p-value | p-value去重后 |",
             "| :---: | :---: | ---: | ---: |"]
    for path, rows, digest, config in sources:
        records, cache = load_pvalue_records(path, rescorer)
        verify_records(rows, records, digest)
        # Read persisted bytes back rather than accepting only the in-memory return value.
        persisted = [json.loads(line) for line in cache.read_text(encoding="utf-8").splitlines() if line.strip()]
        require(persisted == records, f"Persisted cache differs from returned records: {cache}")
        require(sha256(path) == digest, f"Original source changed: {path}")
        raw = summarize_pvalues(records, "p_value_raw")
        dedup = summarize_pvalues(records, "p_value_dedup")
        name = "warmup" if "warmup" in path.stem else "gad" if "gad" in path.stem else path.stem
        summary["inputs"].append({
            "model": name, "source_path": str(path), "source_sha256": digest,
            "source_unchanged": True, "n_unique_ids": len(rows), "detector": config,
            "cache_path": str(cache), "cache_sha256": sha256(cache),
            "raw": raw, "deduplicated": dedup,
        })
        raw_mean = f"{raw['mean']:.6f}" if raw["mean"] is not None else "N/A"
        dedup_mean = f"{dedup['mean']:.6f}" if dedup["mean"] is not None else "N/A"
        table.append(f"| {name} | {raw['n_valid']}/{dedup['n_valid']} | {raw_mean} | {dedup_mean} |")
        print(f"{name}: raw={raw['mean']}, deduplicated={dedup['mean']}", flush=True)
    for path, _rows, digest, _config in sources:
        require(sha256(path) == digest, f"Original source changed before report: {path}")
    table.extend(["", "两列均为逐条回答的单侧正态近似 p-value 均值，空回答不纳入均值。",
                  "去重规则：相同的 (previous_token_id, token_id) 仅计一次；使用原始 KGW 参数和 CUDA 随机数算法。",
                  "已核对每条原始分数、token 数量、缓存来源哈希与格式版本；原始采样文件未修改。", ""])
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    (OUTPUT / "table.md").write_text("\n".join(table), encoding="utf-8")
    print(f"Saved audit: {OUTPUT / 'summary.json'}", flush=True)
    print(f"Saved table: {OUTPUT / 'table.md'}", flush=True)


if __name__ == "__main__":
    main()
