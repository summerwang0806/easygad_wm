#!/usr/bin/env python3
"""Pair discriminator targets with separate student warmup SFT targets.

Only CPU data preparation is performed. Neither input Parquet is modified.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile


def pair_sft_responses(original_rows, para_rows):
    """Return SFT answers in discriminator order after checking IDs and prompts."""
    if not original_rows or not para_rows:
        raise ValueError("Training inputs must be nonempty")

    def index_rows(rows, label):
        indexed = {}
        for row in rows:
            identifier = row["id"]
            if not isinstance(identifier, (str, int)) or isinstance(identifier, bool):
                raise ValueError(f"{label}: each id must be a non-null string or integer")
            if identifier in indexed:
                raise ValueError(f"{label}: duplicate id {identifier!r}")
            answer = row["teacher_response"]
            if not isinstance(answer, str) or not answer.strip():
                raise ValueError(f"{label}: empty or invalid answer for id {identifier!r}")
            indexed[identifier] = row
        return indexed

    original = index_rows(original_rows, "Discriminator")
    para = index_rows(para_rows, "SFT")
    if original.keys() != para.keys():
        missing = len(original.keys() - para.keys())
        extra = len(para.keys() - original.keys())
        raise ValueError(f"Training IDs differ: SFT is missing {missing} IDs and has {extra} extra IDs")
    result = []
    for row in original_rows:
        paired = para[row["id"]]
        if row["content"] != paired["content"]:
            raise ValueError(f"Prompt mismatch for id {row['id']!r}")
        result.append(paired["teacher_response"])
    return result


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def prepare(original_path, para_path, output_path, val_path=None):
    import pyarrow as pa
    import pyarrow.parquet as pq

    original_path, para_path, output_path = map(Path, (original_path, para_path, output_path))
    inputs = [original_path, para_path] + ([Path(val_path)] if val_path else [])
    if output_path.resolve() in {path.resolve() for path in inputs}:
        raise ValueError("Output must differ from both training inputs and validation data")
    tables = []
    for path in inputs:
        table = pq.read_table(path)
        required = {"id", "content", "teacher_response"}
        if not required.issubset(table.column_names):
            raise ValueError(f"{path}: missing columns {sorted(required - set(table.column_names))}")
        if "sft_response" in table.column_names:
            raise ValueError(f"{path}: input already has sft_response; use the original input files")
        tables.append(table)
    original, para = tables[:2]
    columns = ["id", "content", "teacher_response"]
    answers = pair_sft_responses(original.select(columns).to_pylist(), para.select(columns).to_pylist())
    if val_path:
        val_rows = tables[2].select(columns).to_pylist()
        pair_sft_responses(val_rows, val_rows)
        overlap = set(original["id"].to_pylist()) & set(tables[2]["id"].to_pylist())
        if overlap:
            raise ValueError(f"Validation overlaps training: {len(overlap)} IDs")
    metadata = dict(original.schema.metadata or {})
    metadata[b"easygad_split_warmup"] = json.dumps({
        "discriminator_sha256": sha256(original_path),
        "sft_sha256": sha256(para_path),
        "alignment": "id and identical content",
    }, sort_keys=True).encode("utf-8")
    merged = original.append_column("sft_response", pa.array(answers, type=pa.string()))
    merged = merged.replace_schema_metadata(metadata)
    changed = sum(a != b for a, b in zip(original["teacher_response"].to_pylist(), answers))
    if output_path.exists():
        if not pq.read_table(output_path).equals(merged, check_metadata=True):
            raise ValueError(f"Existing output differs from these inputs: {output_path}. Choose a new --merged_file")
        print(f"Reusing verified paired warmup data: {output_path}")
    else:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=output_path.parent, suffix=".parquet", delete=False) as stream:
            temporary = Path(stream.name)
        try:
            pq.write_table(merged, temporary)
            os.replace(temporary, output_path)
        finally:
            temporary.unlink(missing_ok=True)
        print(f"Prepared paired warmup data: {output_path}")
    print(f"Rows: {merged.num_rows}; differing discriminator/SFT answers: {changed}")
    print(f"Warmup discriminator teacher_response <- {original_path}")
    print(f"Warmup actor sft_response <- {para_path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--discriminator_train_file", "--original_train_file", dest="discriminator_train_file", required=True, type=Path)
    parser.add_argument("--sft_train_file", "--para_train_file", dest="sft_train_file", required=True, type=Path)
    parser.add_argument("--output_file", required=True, type=Path)
    parser.add_argument("--val_file", type=Path)
    args = parser.parse_args()
    try:
        prepare(args.discriminator_train_file, args.sft_train_file, args.output_file, args.val_file)
    except (ImportError, OSError, ValueError, KeyError) as error:
        parser.exit(2, f"Split warmup preparation failed: {error}\n")


if __name__ == "__main__":
    main()
