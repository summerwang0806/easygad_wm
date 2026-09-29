#!/usr/bin/env python3
"""Convert downloaded Databricks Dolly-15k into the exact EasyGAD schema."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
from datasets import Dataset, DatasetDict, Features, Value, load_from_disk


EXPECTED_COLUMNS = [
    "id",
    "content",
    "teacher_response",
    "category",
    "grounded",
    "flaw",
    "agreement",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=Path("wm_data/raw/databricks-dolly-15k"),
        help="Dataset previously saved with datasets.save_to_disk",
    )
    parser.add_argument("--train-output", type=Path, default=Path("data/dolly15k_train.parquet"))
    parser.add_argument("--test-output", type=Path, default=Path("data/dolly15k_test.parquet"))
    parser.add_argument("--test-size", type=int, default=500)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def build_easygad_schema() -> pa.Schema:
    """Return the fixed EasyGAD schema without depending on another dataset."""

    features = Features(
        {
            "id": Value("string"),
            "content": [{"content": Value("string"), "role": Value("string")}],
            "teacher_response": Value("string"),
            "category": Value("string"),
            "grounded": Value("bool"),
            "flaw": Value("string"),
            "agreement": Value("bool"),
        }
    )
    content_type = pa.list_(
        pa.field(
            "element",
            pa.struct([pa.field("content", pa.string()), pa.field("role", pa.string())]),
        )
    )
    return pa.schema(
        [
            pa.field("id", pa.string()),
            pa.field("content", content_type),
            pa.field("teacher_response", pa.string()),
            pa.field("category", pa.string()),
            pa.field("grounded", pa.bool_()),
            pa.field("flaw", pa.string()),
            pa.field("agreement", pa.bool_()),
        ],
        metadata=features.arrow_schema.metadata,
    )


def build_messages(instruction: str, context: str) -> list[dict[str, str]]:
    """Build the Dolly prompt that both teacher generation and students will see."""

    instruction = instruction.strip()
    context = context.strip()
    if not instruction:
        raise ValueError("Dolly instruction must not be empty")

    sections = [
        "Below is an instruction that describes a task. "
        "Write a response that appropriately completes the request.",
        f"### Instruction:\n{instruction}",
    ]
    if context:
        sections.append(f"### Context:\n{context}")
    sections.append("### Response:\n")
    return [
        {"content": "You are a helpful assistant.", "role": "system"},
        {"content": "\n\n".join(sections), "role": "user"},
    ]


def convert_split(dataset: Dataset, schema: pa.Schema) -> pa.Table:
    rows = []
    for example in dataset:
        source_index = int(example["_source_index"])
        context = example["context"] or ""
        response = (example["response"] or "").strip()
        if not response:
            raise ValueError(f"Dolly response is empty at source index {source_index}")
        rows.append(
            {
                "id": f"dolly-{source_index:05d}",
                "content": build_messages(example["instruction"], context),
                "teacher_response": response,
                "category": example["category"],
                "grounded": bool(context.strip()),
                "flaw": "normal",
                "agreement": None,
            }
        )
    table = pa.Table.from_pylist(rows, schema=schema)
    if table.schema.names != EXPECTED_COLUMNS:
        raise AssertionError(f"unexpected converted columns: {table.schema.names}")
    if not table.schema.equals(schema, check_metadata=True):
        raise AssertionError("converted Dolly schema differs from the fixed EasyGAD schema")
    return table


def write_parquet(table: pa.Table, output: Path, overwrite: bool) -> None:
    if output.exists() and not overwrite:
        raise FileExistsError(f"{output} exists; pass --overwrite to replace it")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    pq.write_table(table, temporary, compression="zstd", row_group_size=1000)
    temporary.replace(output)


def main() -> None:
    args = parse_args()
    if not args.raw_dir.exists():
        raise FileNotFoundError(
            f"downloaded Dolly dataset not found: {args.raw_dir}; see wm_data/README.md"
        )
    schema = build_easygad_schema()

    saved = load_from_disk(str(args.raw_dir))
    dolly = saved["train"] if isinstance(saved, DatasetDict) else saved
    dolly = dolly.add_column("_source_index", list(range(len(dolly))))
    if not 0 < args.test_size < len(dolly):
        raise ValueError(f"--test-size must be between 1 and {len(dolly) - 1}")
    splits = dolly.train_test_split(test_size=args.test_size, seed=args.seed, shuffle=True)

    train_table = convert_split(splits["train"], schema)
    test_table = convert_split(splits["test"], schema)
    write_parquet(train_table, args.train_output, args.overwrite)
    write_parquet(test_table, args.test_output, args.overwrite)

    manifest = {
        "dataset": "databricks/databricks-dolly-15k",
        "raw_dir": str(args.raw_dir.resolve()),
        "seed": args.seed,
        "train_rows": train_table.num_rows,
        "test_rows": test_table.num_rows,
        "train_output": str(args.train_output.resolve()),
        "test_output": str(args.test_output.resolve()),
        "prompt_fields": ["instruction", "context"],
        "teacher_response_in_base_parquet": "Dolly response",
        "schema": "fixed EasyGAD seven-column schema",
    }
    manifest_path = args.train_output.parent / "dolly15k_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(manifest, indent=2))
    print("sample content:", test_table.column("content")[0].as_py())


if __name__ == "__main__":
    main()
