#!/usr/bin/env python3
"""Read-only audit of two Dolly teacher datasets; write aggregate JSON only.

Run in the server's existing environment with pyarrow installed. This script
does not load a model, generate answers, change Parquet files, or export text.
The repetition diagnostic is based on English word 4-grams, NOT tokenizer
bigrams; it must not replace the severe-repetition metric in the result table.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import re
import statistics
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MAX_METADATA_RECORDS = 4
PARAMETER_ALIASES = {
    "model": "model", "teacher_model": "model", "teacher_model_path": "model",
    "model_path": "model", "input": "input", "input_file": "input",
    "source_file": "input", "generation_mode": "watermark", "watermark": "watermark",
    "gamma": "gamma", "delta": "delta", "hash_key": "hash_key", "seeding": "seeding",
    "temperature": "temperature", "top_p": "top_p", "top_k": "top_k",
    "max_prompt_tokens": "max_prompt_tokens", "max_new_tokens": "max_new_tokens",
    "seed": "seed",
}
NESTED_PARAMETER_KEYS = {"args", "sampling", "generation", "kgw", "kgw_detector", "config"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    for name, default in (
        ("old-train", "dolly15k_qwen2_5_14b_kgw_train.parquet"),
        ("new-train", "dolly15k_qwen2_5_14b_kgw_gamma0.5_delta3_train.parquet"),
        ("old-test", "dolly15k_qwen2_5_14b_kgw_test.parquet"),
        ("new-test", "dolly15k_qwen2_5_14b_kgw_gamma0.5_delta3_test.parquet"),
    ):
        parser.add_argument("--" + name, type=Path, default=ROOT / "data" / default)
    parser.add_argument("--output", type=Path, default=ROOT / "teacher_comparison.json")
    return parser.parse_args()


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sequence_hash(values: list[Any]) -> str:
    digest = hashlib.sha256()
    for value in values:
        encoded = canonical(value).encode("utf-8")
        digest.update(len(encoded).to_bytes(8, "big"))
        digest.update(encoded)
    return digest.hexdigest()


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def distribution(values: list[int | float]) -> dict[str, Any]:
    if not values:
        return {"n": 0, "mean": None, "min": None, "p05": None, "p25": None,
                "median": None, "p75": None, "p95": None, "max": None}
    ordered = sorted(values)

    def quantile(fraction: float) -> float:
        position = fraction * (len(ordered) - 1)
        left = math.floor(position)
        right = math.ceil(position)
        return ordered[left] + (ordered[right] - ordered[left]) * (position - left)

    return {"n": len(values), "mean": statistics.mean(values), "min": ordered[0],
            "p05": quantile(.05), "p25": quantile(.25), "median": quantile(.5),
            "p75": quantile(.75), "p95": quantile(.95), "max": ordered[-1]}


def answer_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    answers = [row["teacher_response"] for row in rows if isinstance(row["teacher_response"], str)]
    nonempty = [answer for answer in answers if answer.strip()]
    frequencies = Counter(nonempty)
    word_counts, repeated_fractions = [], []
    for answer in answers:
        words = re.findall(r"[a-z0-9]+", answer.lower())
        word_counts.append(len(words))
        if len(words) >= 4:
            grams = list(zip(words, words[1:], words[2:], words[3:]))
            repeated_fractions.append(1 - len(set(grams)) / len(grams))
    repeat_count = sum(value > .5 for value in repeated_fractions)
    return {
        "non_string_count": len(rows) - len(answers),
        "empty_or_whitespace_count": len(answers) - len(nonempty),
        "nonempty_count": len(nonempty),
        "unique_nonempty_exact_text_count": len(frequencies),
        "duplicate_nonempty_extra_rows": len(nonempty) - len(frequencies),
        "max_identical_nonempty_response_frequency": max(frequencies.values(), default=0),
        "character_lengths": distribution([len(answer) for answer in answers]),
        "english_alphanumeric_word_lengths": distribution(word_counts),
        "simple_text_repetition": {
            "method": "lowercase text, extract ASCII [a-z0-9]+ words, then 1 - unique word 4-grams / all word 4-grams",
            "warning": "Not tokenizer repetition and not the severe token-bigram statistic in the result table.",
            "valid_answers_with_at_least_four_words": len(repeated_fractions),
            "repeated_word4_fraction": distribution(repeated_fractions),
            "word4_fraction_gt_0_5_count": repeat_count,
            "word4_fraction_gt_0_5_fraction_of_all_rows": repeat_count / len(rows) if rows else None,
        },
    }


def collect_parameters(value: Any, depth: int = 0) -> dict[str, list[Any]]:
    """Inspect only known generation keys; never return arbitrary sidecar fields."""
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except (TypeError, ValueError):
            return {}
    if not isinstance(value, dict) or depth > 4:
        return {}
    found: dict[str, list[Any]] = {}
    for key, item in value.items():
        if key in PARAMETER_ALIASES and isinstance(item, (str, int, float, bool, type(None))):
            if isinstance(item, float) and not math.isfinite(item):
                continue
            found.setdefault(PARAMETER_ALIASES[key], []).append(item)
        elif key == "chat_template" and isinstance(item, (str, dict, list)):
            found.setdefault("chat_template_sha256", []).append(hashlib.sha256(canonical(item).encode("utf-8")).hexdigest())
        elif key in NESTED_PARAMETER_KEYS:
            nested = collect_parameters(item, depth + 1)
            for name, values in nested.items():
                found.setdefault(name, []).extend(values)
    return {key: [json.loads(item) for item in sorted({canonical(v) for v in values})]
            for key, values in found.items()}


def generation_metadata(path: Path, schema: Any, pq: Any) -> dict[str, Any]:
    records: list[dict[str, Any]] = []

    def schema_record(candidate: Path, candidate_schema: Any) -> None:
        raw = (candidate_schema.metadata or {}).get(b"kgw_detector")
        parameters = collect_parameters(raw.decode("utf-8")) if raw is not None else {}
        records.append({"source": str(candidate), "kind": "parquet_schema.kgw_detector",
                        "status": "available" if parameters else "missing",
                        "parameters": parameters})

    schema_record(path, schema)
    sidecar = path.with_suffix(path.suffix + ".metadata.json")
    if sidecar.exists():
        try:
            parameters = collect_parameters(json.loads(sidecar.read_text(encoding="utf-8")))
            records.append({"source": str(sidecar), "kind": "metadata_sidecar",
                            "status": "available" if parameters else "missing",
                            "parameters": parameters})
        except Exception as exc:
            records.append({"source": str(sidecar), "kind": "metadata_sidecar",
                            "status": "error", "error_type": type(exc).__name__})
    else:
        records.append({"source": str(sidecar), "kind": "metadata_sidecar", "status": "missing"})
    parts = path.with_suffix(path.suffix + ".parts")
    candidates = sorted({candidate for candidate in parts.rglob("*.parquet")
                         if candidate.name.endswith("_kgw_scores.parquet") or candidate.parent.name == "scores"}) if parts.exists() else []
    for candidate in candidates[:MAX_METADATA_RECORDS]:
        try:
            schema_record(candidate, pq.ParquetFile(candidate).schema_arrow)
        except Exception as exc:
            records.append({"source": str(candidate), "kind": "parquet_schema.kgw_detector",
                            "status": "error", "error_type": type(exc).__name__})
    parameters: dict[str, list[Any]] = {}
    for record in records:
        for key, values in record.get("parameters", {}).items():
            parameters.setdefault(key, []).extend(values)
    parameters = {key: [json.loads(item) for item in sorted({canonical(v) for v in values})]
                  for key, values in parameters.items()}
    return {
        "status": "available" if parameters else "missing",
        "parts_directory": str(parts), "parts_directory_exists": parts.exists(),
        "candidate_score_parquet_count": len(candidates),
        "score_parquet_metadata_examined": min(len(candidates), MAX_METADATA_RECORDS),
        "parameter_values": parameters, "records": records,
        "limitations": ["No teacher identity is inferred from a dataset filename.",
                        "Recorded model paths do not prove immutable model weights or tokenizer versions.",
                        "The generator normally preserves source schema in final teacher Parquet and may delete parts after completion.",
                        "Only the first four score-part metadata records are inspected."],
    }


def load_dataset(path: Path, pq: Any) -> tuple[dict[str, Any], list[dict[str, Any]], Any]:
    summary: dict[str, Any] = {"path": str(path), "status": "missing"}
    if not path.is_file():
        return summary, [], None
    try:
        parquet = pq.ParquetFile(path)
        schema = parquet.schema_arrow
        summary.update({"file_sha256": file_hash(path), "parquet_rows": parquet.metadata.num_rows,
                        "schema": [{"name": field.name, "type": str(field.type), "nullable": field.nullable} for field in schema],
                        "schema_metadata_keys": sorted(key.decode("utf-8", errors="replace") for key in (schema.metadata or {}))})
        required = {"id", "content", "teacher_response"}
        if not required.issubset(schema.names):
            summary.update({"status": "error", "missing_columns": sorted(required - set(schema.names))})
            return summary, [], schema
        rows = pq.read_table(path, columns=["id", "content", "teacher_response"]).to_pylist()
        ids = [row["id"] for row in rows]
        valid = [sample_id for sample_id in ids if isinstance(sample_id, str) and sample_id.strip()]
        id_counts = Counter(valid)
        ordered_content = [{"id": row["id"], "content": row["content"]} for row in rows]
        summary.update({
            "status": "ok", "rows": len(rows), "invalid_id_count": len(ids) - len(valid),
            "unique_valid_id_count": len(id_counts), "duplicate_valid_id_extra_rows": len(valid) - len(id_counts),
            "id_order_sha256": sequence_hash(ids),
            "id_content_order_sha256": sequence_hash(ordered_content),
            "id_content_sorted_sha256": sequence_hash(sorted(ordered_content, key=canonical)),
            "teacher_responses": answer_summary(rows),
            "generation_metadata": generation_metadata(path, schema, pq),
        })
        return summary, rows, schema
    except Exception as exc:
        summary.update({"status": "error", "error_type": type(exc).__name__})
        return summary, [], None


def valid_id_set(rows: list[dict[str, Any]]) -> set[str]:
    return {row["id"] for row in rows if isinstance(row["id"], str) and row["id"].strip()}


def compare_datasets(old: tuple, new: tuple) -> dict[str, Any]:
    a, old_rows, old_schema = old
    b, new_rows, new_schema = new
    if a["status"] != "ok" or b["status"] != "ok":
        return {"status": "missing_or_error", "old_status": a["status"], "new_status": b["status"]}
    old_ids, new_ids = valid_id_set(old_rows), valid_id_set(new_rows)
    common_ids = old_ids & new_ids
    unambiguous = all(summary["invalid_id_count"] == 0 and summary["duplicate_valid_id_extra_rows"] == 0 for summary in (a, b))
    result = {
        "status": "ok" if unambiguous else "invalid_or_duplicate_ids",
        "same_valid_id_set": old_ids == new_ids,
        "old_only_id_count": len(old_ids - new_ids), "new_only_id_count": len(new_ids - old_ids),
        "same_id_order": [row["id"] for row in old_rows] == [row["id"] for row in new_rows],
        "same_schema_without_metadata": old_schema.remove_metadata().equals(new_schema.remove_metadata()),
        "same_schema_including_metadata": old_schema.equals(new_schema, check_metadata=True),
        "common_valid_ids": len(common_ids), "content_alignment_status": "not_checked_due_to_invalid_or_duplicate_ids",
    }
    if unambiguous:
        old_by_id, new_by_id = ({row["id"]: row for row in rows} for rows in (old_rows, new_rows))
        mismatched_content = sorted(sample_id for sample_id in common_ids if old_by_id[sample_id]["content"] != new_by_id[sample_id]["content"])
        same_response = sum(isinstance(old_by_id[i]["teacher_response"], str) and old_by_id[i]["teacher_response"] == new_by_id[i]["teacher_response"] for i in common_ids)
        result.update({"content_alignment_status": "checked_by_id", "content_mismatch_count": len(mismatched_content),
                       "first_content_mismatch_ids": mismatched_content[:8],
                       "all_id_aligned_content_equal": old_ids == new_ids and not mismatched_content,
                       "same_exact_teacher_response_count": same_response,
                       "same_exact_teacher_response_fraction_of_common_ids": same_response / len(common_ids) if common_ids else None})
    old_params = a["generation_metadata"]["parameter_values"]
    new_params = b["generation_metadata"]["parameter_values"]
    result["generation_parameter_comparison"] = {}
    for key in sorted(set(PARAMETER_ALIASES.values()) | {"chat_template_sha256"}):
        left, right = old_params.get(key, []), new_params.get(key, [])
        status = ("missing" if not left or not right else "ambiguous" if len(left) != 1 or len(right) != 1
                  else "same" if left == right else "different")
        result["generation_parameter_comparison"][key] = {"status": status, "old_values": left, "new_values": right}
    return result


def main() -> int:
    args = parse_args()
    paths = {name: getattr(args, name).resolve() for name in ("old_train", "new_train", "old_test", "new_test")}
    output = args.output.resolve()
    if output in paths.values():
        raise SystemExit("--output must differ from all source Parquet paths")
    try:
        import pyarrow.parquet as pq
    except ImportError:
        raise SystemExit("pyarrow is required; run this script in the server's existing wm environment")
    datasets = {name: load_dataset(path, pq) for name, path in paths.items()}
    result = {
        "schema": "teacher-dataset-comparison-v1", "script_sha256": file_hash(Path(__file__).resolve()),
        "datasets": {name: dataset[0] for name, dataset in datasets.items()},
        "comparisons": {split: compare_datasets(datasets["old_" + split], datasets["new_" + split]) for split in ("train", "test")},
        "train_test_disjointness": {},
        "limitations": ["Only summaries and short problem IDs are exported; no teacher response or prompt text is exported.",
                        "English word 4-gram repetition is a text diagnostic, not the tokenizer metric in the experiment table.",
                        "Missing generation metadata cannot establish that gamma and delta were the only changes.",
                        "This audit does not load models, prove weight identity, or reproduce watermark generation."],
    }
    for group in ("old", "new"):
        train, test = datasets[group + "_train"], datasets[group + "_test"]
        if train[0]["status"] == test[0]["status"] == "ok":
            overlap = valid_id_set(train[1]) & valid_id_set(test[1])
            ids_valid = all(summary["invalid_id_count"] == 0 and summary["duplicate_valid_id_extra_rows"] == 0 for summary in (train[0], test[0]))
            result["train_test_disjointness"][group] = {"status": "checked", "overlap_id_count": len(overlap),
                                                        "disjoint": not overlap, "all_ids_valid_and_unique": ids_valid}
        else:
            result["train_test_disjointness"][group] = {"status": "missing_or_error", "disjoint": None}
    output.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    output.write_text(rendered, encoding="utf-8")
    print(f"Saved {output}")
    for split, comparison in result["comparisons"].items():
        print(f"{split}: status={comparison['status']}, "
              f"same_id_order={comparison.get('same_id_order')}, "
              f"content_mismatch_count={comparison.get('content_mismatch_count')}")
    for name, dataset in result["datasets"].items():
        print(f"{name}: status={dataset['status']}, "
              f"generation_metadata={dataset.get('generation_metadata', {}).get('status', 'missing')}")
    return 0 if all(dataset[0]["status"] == "ok" for dataset in datasets.values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())
