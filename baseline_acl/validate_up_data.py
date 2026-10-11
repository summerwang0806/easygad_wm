#!/usr/bin/env python3
"""CPU-only preflight for full-source UP teacher-response replacement.

This checks the original Parquet source rather than a hard-coded split size, so
a --max_samples smoke output cannot be used with the full source for training.
Only teacher_response may differ; schema metadata and row order must survive.
Exhausted generation failures may be omitted only with a matching complete UP
audit; an arbitrary partial or smoke dataset remains invalid for training.
"""

from __future__ import annotations

import argparse
import hashlib
import json
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


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_drop_evidence(original: Any, up: Any, audit: Any) -> list[int]:
    """Identify the retained source rows from a complete exhausted-failure audit."""
    if not isinstance(audit, dict) or audit.get("complete") is not True:
        raise ValueError("UP drop audit is missing or incomplete; partial data must not be trained")
    if audit.get("method") != "ordinary_untargeted_dipper_paraphrasing":
        raise ValueError("Only an ordinary UP audit may authorize dropped generation failures")
    metadata = audit.get("metadata")
    config = metadata.get("config") if isinstance(metadata, dict) else None
    source = metadata.get("input") if isinstance(metadata, dict) else None
    if not isinstance(config, dict) or config.get("on_failure") != "drop":
        raise ValueError("UP drop audit must record on_failure=drop")
    cap = config.get("max_attempts")
    if type(cap) is not int or cap < 1:
        raise ValueError("UP drop audit has an invalid max_attempts")
    if not isinstance(source, dict) or type(source.get("rows")) is not int or source["rows"] != original.num_rows:
        raise ValueError("UP drop audit does not cover the full original source")

    count_fields = {
        "source_rows": original.num_rows, "processed_rows": original.num_rows,
        "rows": up.num_rows, "dropped_count": original.num_rows - up.num_rows,
    }
    for field, expected in count_fields.items():
        if type(audit.get(field)) is not int or audit[field] != expected:
            raise ValueError(f"UP drop audit has inconsistent {field}")
    dropped = audit.get("dropped_rows")
    if (not isinstance(dropped, list)
            or any(type(index) is not int or not 0 <= index < original.num_rows for index in dropped)
            or dropped != sorted(set(dropped)) or len(dropped) != count_fields["dropped_count"]):
        raise ValueError("UP drop audit has invalid or unsorted dropped_rows")
    ids = original["id"].to_pylist()
    dropped_ids = audit.get("dropped_ids")
    if (not isinstance(dropped_ids, list) or len(dropped_ids) != len(dropped)
            or any(type(value) is not type(ids[index]) or value != ids[index]
                   for index, value in zip(dropped, dropped_ids, strict=True))):
        raise ValueError("UP drop audit dropped_ids differ from the original source")
    statuses = audit.get("status_counts")
    if (not isinstance(statuses, dict)
            or any(type(count) is not int or count < 0 for count in statuses.values())
            or set(statuses).difference({"ok", "dropped", "fallback"})
            or statuses.get("dropped", 0) != len(dropped)
            or statuses.get("ok", 0) != up.num_rows or statuses.get("fallback", 0) != 0
            or sum(statuses.values()) != original.num_rows):
        raise ValueError("UP drop audit status_counts do not account for all source rows")
    records = audit.get("dropped_records")
    if not isinstance(records, list) or len(records) != len(dropped):
        raise ValueError("UP drop audit is missing exhausted failure records")
    responses = original["teacher_response"].to_pylist()
    for index, record in zip(dropped, records, strict=True):
        issues = record.get("issues") if isinstance(record, dict) else None
        if (not isinstance(record, dict) or type(record.get("row_index")) is not int
                or record["row_index"] != index
                or type(record.get("id")) is not type(ids[index]) or record["id"] != ids[index]
                or type(record.get("attempt")) is not int or record["attempt"] != cap
                or not isinstance(issues, list) or not issues
                or any(not isinstance(issue, str) or not issue.strip() for issue in issues)
                or record.get("source_sha256") != hashlib.sha256(responses[index].encode("utf-8")).hexdigest()):
            raise ValueError(f"UP drop audit has an invalid exhausted failure record for source row {index}")
        if any(issue in {"full_response_exceeds_encoder_budget", "full_response_input_limit"} for issue in issues):
            raise ValueError("UP drop audit cannot omit source rows that exceeded the input budget")
    omitted = set(dropped)
    return [index for index in range(original.num_rows) if index not in omitted]


def validate_tables(original: Any, up: Any, validation: Any, expected_rows: int | None = None,
                    drop_evidence: Any = None) -> dict[str, int]:
    original_ids = validate_required_values(original, "Original KGW train")
    up_ids = validate_required_values(up, "UP train")
    validation_ids = validate_required_values(validation, "Original KGW validation")

    if expected_rows is not None and original.num_rows != expected_rows:
        raise ValueError(f"Original KGW train has {original.num_rows} rows; expected {expected_rows}")
    if up.num_rows != original.num_rows and drop_evidence is None:
        raise ValueError(
            f"UP train has {up.num_rows} rows, but the full original KGW train has {original.num_rows}; "
            "partial / --max_samples smoke data must not be trained"
        )
    retained = validate_drop_evidence(original, up, drop_evidence) if drop_evidence is not None else list(range(original.num_rows))
    kept_original = original.take(retained)
    if not original.schema.equals(up.schema, check_metadata=True):
        raise ValueError("UP schema or metadata differs from the original KGW train; preserve all fields and Hugging Face metadata")
    if [original_ids[index] for index in retained] != up_ids:
        raise ValueError("UP IDs or row order differ from the retained original KGW train")
    for column in original.column_names:
        if column != "teacher_response" and not kept_original[column].equals(up[column]):
            raise ValueError(f"UP changed protected column {column!r}; only teacher_response may change")
    if set(original_ids).intersection(validation_ids):
        raise ValueError("Validation IDs overlap training IDs; use the original held-out KGW test split")
    if not original.schema.equals(validation.schema, check_metadata=True):
        raise ValueError("Validation schema or metadata differs from the original KGW train")

    changed_rows = sum(
        original_text != up_text
        for original_text, up_text in zip(
            kept_original["teacher_response"].to_pylist(), up["teacher_response"].to_pylist()
        )
    )
    if changed_rows == 0:
        raise ValueError("UP teacher responses are identical to the original KGW train; no paraphrasing was applied")
    return {"train_rows": up.num_rows, "source_rows": original.num_rows,
            "dropped_rows": original.num_rows - up.num_rows,
            "validation_rows": validation.num_rows, "changed_response_rows": changed_rows}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original_train_file", required=True, type=Path)
    parser.add_argument("--up_train_file", required=True, type=Path)
    parser.add_argument("--val_file", required=True, type=Path)
    parser.add_argument("--audit_file", type=Path, help="Drop audit override; default: <up_train_file>.audit.json")
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
        audit = None
        if up.num_rows < original.num_rows or args.audit_file is not None:
            audit_path = args.audit_file or Path(str(paths[1]) + ".audit.json")
            if not audit_path.is_file():
                raise ValueError(f"UP partial data requires the completed drop audit: {audit_path}")
            audit = json.loads(audit_path.read_text(encoding="utf-8"))
            if not isinstance(audit, dict):
                raise ValueError("UP drop audit must be a JSON object")
            audit_source = audit.get("metadata", {}).get("input", {}) if isinstance(audit.get("metadata"), dict) else {}
            if (not isinstance(audit_source, dict) or audit_source.get("sha256") != file_sha256(paths[0])
                    or audit.get("output_sha256") != file_sha256(paths[1])):
                raise ValueError("UP drop audit input/output SHA-256 does not match the training files")
        summary = validate_tables(original, up, validation, args.expected_rows, audit)
    except (ValueError, OSError) as exc:
        print(f"UP data preflight failed: {exc}", file=sys.stderr)
        return 2

    print(
        "UP data preflight passed: "
        f"{summary['train_rows']} retained training rows from {summary['source_rows']} source rows, "
        f"{summary['dropped_rows']} audited exhausted failures dropped, "
        f"{summary['changed_response_rows']} changed teacher responses, "
        f"{summary['validation_rows']} held-out original KGW validation rows; "
        "retained schema, metadata, row order, IDs, prompts and all other columns preserved."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
