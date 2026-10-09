#!/usr/bin/env python3
"""Verify saved Dolly human answers against raw data and all four model files. No API/GPU."""
import argparse
import json
import re
from pathlib import Path

from evaluate_quality import ROOT, DEFAULT_FILES, load_dataset, align_datasets, normalize_prompt


def build_prompt(instruction, context):
    parts = ["Below is an instruction that describes a task. "
             "Write a response that appropriately completes the request.",
             "### Instruction:\n" + instruction.strip()]
    if context.strip():
        parts.append("### Context:\n" + context.strip())
    parts.append("### Response:\n")
    return [{"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "\n\n".join(parts)}]


def verified_references(raw, split, datasets):
    ids = align_datasets(datasets)
    by_id = {}
    for row in split:
        if row["id"] in by_id:
            raise ValueError("Duplicate ID in test split")
        by_id[row["id"]] = row
    if set(ids) != set(by_id):
        raise ValueError("Test split and generated answer IDs do not match exactly")
    first = next(iter(datasets.values()))
    result = []
    for sample_id in ids:
        match = re.fullmatch(r"dolly-(\d+)", sample_id)
        if not match or int(match[1]) >= len(raw):
            raise ValueError(f"Invalid source index: {sample_id}")
        source_index = int(match[1])
        original, converted = raw[source_index], by_id[sample_id]
        prompt = build_prompt(original["instruction"], original.get("context") or "")
        answer = (original["response"] or "").strip()
        if not answer or answer != converted["teacher_response"]:
            raise ValueError(f"Reference differs from raw Dolly response: {sample_id}")
        if prompt != normalize_prompt(converted["content"]) or prompt != first[sample_id]["prompt"]:
            raise ValueError(f"Instruction/context differs from raw Dolly: {sample_id}")
        result.append({"id": sample_id, "prompt": prompt, "answer": answer,
                       "reference_source": "databricks/databricks-dolly-15k:response",
                       "source_index": source_index, "category": original.get("category")})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=ROOT / "wm_data/raw/databricks-dolly-15k")
    parser.add_argument("--test-split", type=Path, default=ROOT / "data/dolly15k_test.parquet")
    parser.add_argument("--output", type=Path, default=ROOT / "text_quality/references/dolly_human_500.jsonl")
    args = parser.parse_args()
    # Only preparation requires the project's already-installed datasets/pyarrow.
    from datasets import load_from_disk, DatasetDict
    import pyarrow.parquet as pq
    saved = load_from_disk(str(args.raw_dir))
    raw = saved["train"] if isinstance(saved, DatasetDict) else saved
    models = {label: load_dataset(path) for label, path in DEFAULT_FILES.items()}
    rows = verified_references(raw, pq.read_table(args.test_split).to_pylist(), models)
    contents = "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows)
    if args.output.exists():
        if args.output.read_text(encoding="utf-8") != contents:
            raise ValueError("Existing reference file differs; choose a new output, do not overwrite")
        print(f"Verified existing {len(rows)} human references: {args.output}")
        return
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as handle:
        handle.write(contents)
    print(f"Verified and saved {len(rows)} human references: {args.output}; API calls=0")


if __name__ == "__main__":
    main()
