#!/usr/bin/env python3
"""CPU-only preflight for full-source UP teacher-response replacement.

This checks the original Parquet source rather than a hard-coded split size, so
a --max_samples smoke output cannot be used with the full source for training.
Only teacher_response may differ; schema metadata and row order must survive.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Any


REQUIRED_COLUMNS = {"id", "content", "teacher_response"}


def has_prompt_text(value: Any) -> bool:
    """Support the source's list<struct<content, role>> and plain text prompts."""
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return bool(value) and all(
            isinstance(message, dict)
            and isinstance(message.get("role"), str)
            and bool(message["role"].strip())
            and isinstance(message.get("content"), str)
            and bool(message["content"].strip())
            for message in value
        )
    return False


def validate_required_values(table: Any, label: str) -> list[Any]:
    missing = REQUIRED_COLUMNS.difference(table.column_names)
    if missing:
        raise ValueError(f"{label}: missing required columns: {sorted(missing)}")
    if table.num_rows == 0:
        raise ValueError(f"{label}: dataset is empty")

    ids = table["id"].to_pylist()
    seen = set()
    for row, value in enumerate(ids):
        if value is None or isinstance(value, bool) or not isinstance(value, (str, int)):
            raise ValueError(f"{label}: invalid id at row {row}; expected a nonempty string or integer")
        if isinstance(value, str) and not value.strip():
            raise ValueError(f"{label}: empty id at row {row}")
        if value in seen:
            raise ValueError(f"{label}: duplicate id at row {row}")
        seen.add(value)

    for row, value in enumerate(table["content"].to_pylist()):
        if not has_prompt_text(value):
            raise ValueError(f"{label}: empty or malformed content at row {row}")
    for row, value in enumerate(table["teacher_response"].to_pylist()):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{label}: empty or non-string teacher_response at row {row}")
    return ids


def validate_tables(original: Any, up: Any, validation: Any, expected_rows: int | None = None) -> dict[str, int]:
    original_ids = validate_required_values(original, "Original KGW train")
    up_ids = validate_required_values(up, "UP train")
    validation_ids = validate_required_values(validation, "Original KGW validation")

    if expected_rows is not None and original.num_rows != expected_rows:
        raise ValueError(f"Original KGW train has {original.num_rows} rows; expected {expected_rows}")
    if up.num_rows != original.num_rows:
        raise ValueError(
            f"UP train has {up.num_rows} rows, but the full original KGW train has {original.num_rows}; "
            "partial / --max_samples smoke data must not be trained"
        )
    if not original.schema.equals(up.schema, check_metadata=True):
        raise ValueError("UP schema or metadata differs from the original KGW train; preserve all fields and Hugging Face metadata")
    if original_ids != up_ids:
        raise ValueError("UP IDs or row order differ from the full original KGW train")
    for column in original.column_names:
        if column != "teacher_response" and not original[column].equals(up[column]):
            raise ValueError(f"UP changed protected column {column!r}; only teacher_response may change")
    if set(original_ids).intersection(validation_ids):
        raise ValueError("Validation IDs overlap training IDs; use the original held-out KGW test split")
    if not original.schema.equals(validation.schema, check_metadata=True):
        raise ValueError("Validation schema or metadata differs from the original KGW train")

    changed_rows = sum(
        original_text != up_text
        for original_text, up_text in zip(
            original["teacher_response"].to_pylist(), up["teacher_response"].to_pylist()
        )
    )
    if changed_rows == 0:
        raise ValueError("UP teacher responses are identical to the original KGW train; no paraphrasing was applied")
    return {"train_rows": original.num_rows, "validation_rows": validation.num_rows, "changed_response_rows": changed_rows}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original_train_file", required=True, type=Path)
    parser.add_argument("--up_train_file", required=True, type=Path)
    parser.add_argument("--val_file", required=True, type=Path)
    parser.add_argument("--expected_rows", type=int, help="Optional known full-source row count (for this server split: 14511)")
    args = parser.parse_args()
    if args.expected_rows is not None and args.expected_rows < 1:
        parser.error("--expected_rows must be a positive integer")
    return args


def main() -> int:
    args = parse_args()
    try:
        paths = [args.original_train_file.resolve(), args.up_train_file.resolve(), args.val_file.resolve()]
        if len(set(paths)) != len(paths):
            raise ValueError("Original KGW train, UP train and validation must be three distinct files")
        for path in paths:
            if not path.is_file():
                raise ValueError(f"Parquet file is missing: {path}")

        try:
            import pyarrow.parquet as pq
        except ImportError as exc:
            raise ValueError("CPU preflight requires pyarrow; run in the EasyGAD environment that provides it") from exc

        # ParquetFile avoids interpreting directories as partitioned datasets.
        original, up, validation = [pq.ParquetFile(path).read() for path in paths]
        summary = validate_tables(original, up, validation, args.expected_rows)
    except (ValueError, OSError) as exc:
        print(f"UP data preflight failed: {exc}", file=sys.stderr)
        return 2

    print(
        "UP data preflight passed: "
        f"{summary['train_rows']} full-source training rows, "
        f"{summary['changed_response_rows']} changed teacher responses, "
        f"{summary['validation_rows']} held-out original KGW validation rows; "
        "schema, metadata, IDs, prompts and all other columns preserved."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
