"""Small shared IO contracts for resumable generation and offline detection."""
from __future__ import annotations

from contextlib import contextmanager
import json
import os
from pathlib import Path
import socket

from baseline_lsh.core import canonical, sha256_file


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="\n") as f:
        f.write(canonical(value) + "\n")
    os.replace(tmp, path)


def atomic_parquet(path, table):
    import pyarrow.parquet as pq
    path = Path(path)
    tmp = path.with_name(path.name + ".tmp")
    pq.write_table(table, tmp, compression="zstd", use_compliant_nested_type=False)
    os.replace(tmp, path)


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


@contextmanager
def run_lock(directory):
    """Fail closed on a concurrent/stale run; never kill or steal another job."""
    path = Path(directory) / "run.lock"
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as e:
        raise RuntimeError(f"run lock exists: {path}; after confirming the old job stopped, remove ONLY this lock and resume") from e
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(canonical({"pid": os.getpid(), "host": socket.gethostname()}))
        yield
    finally:
        path.unlink(missing_ok=True)


def ensure_manifest(directory, specification):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "manifest.json"
    if path.exists():
        old = read_json(path)
        if old != specification:
            changed = sorted(k for k in set(old) | set(specification) if old.get(k) != specification.get(k))
            raise ValueError(f"resume configuration mismatch ({', '.join(changed)}); use a new output path")
    else:
        if any(directory.glob("part-*")):
            raise ValueError("orphan parts without a manifest; use a new output path")
        atomic_json(path, specification)


def validate_source(table):
    import pyarrow as pa
    if "id" not in table.schema.names or "content" not in table.schema.names or "teacher_response" not in table.schema.names:
        raise ValueError("input must have id, content and teacher_response columns")
    if not (pa.types.is_string(table.schema.field("teacher_response").type)
            or pa.types.is_large_string(table.schema.field("teacher_response").type)):
        raise ValueError("teacher_response must be an Arrow string")
    ids = table["id"].to_pylist()
    if any(i is None for i in ids) or len(set(ids)) != len(ids):
        raise ValueError("input IDs must be non-null and unique")
    for row in table.to_pylist():
        if not isinstance(row["content"], list) or not row["content"]:
            raise ValueError(f"invalid content messages for id={row['id']!r}")


def validate_preserved(source, generated):
    if not source.schema.equals(generated.schema, check_metadata=True) or source.num_rows != generated.num_rows:
        raise ValueError("generated EasyGAD schema/metadata/row count changed")
    for name in source.schema.names:
        if name != "teacher_response" and not source[name].equals(generated[name]):
            raise ValueError(f"protected source column changed: {name}")
    if any(not isinstance(s, str) or not s.strip() for s in generated["teacher_response"].to_pylist()):
        raise ValueError("generated teacher_response contains empty/null values")


def prompt_ids(tokenizer, messages, max_prompt_tokens):
    """Same right truncation as existing KGW; pass IDs directly to vLLM."""
    text = tokenizer.apply_chat_template(messages, add_generation_prompt=True, tokenize=False)
    result = tokenizer.encode(text, add_special_tokens=False)[:max_prompt_tokens]
    if not result:
        raise ValueError("empty rendered prompt")
    return result


def part_paths(directory, index):
    stem = Path(directory) / f"part-{index:06d}"
    return Path(str(stem) + ".parquet"), Path(str(stem) + ".scores.json"), Path(str(stem) + ".done.json")


def read_part(directory, index, source):
    import pyarrow.parquet as pq
    data, scores, done = part_paths(directory, index)
    if not done.exists():
        return None
    stamp = read_json(done)
    if not data.is_file() or not scores.is_file() or sha256_file(data) != stamp["data_sha256"] or sha256_file(scores) != stamp["scores_sha256"]:
        raise ValueError(f"corrupt committed part {index}; do not silently regenerate or mix outputs")
    table, rows = pq.read_table(data), read_json(scores)
    validate_preserved(source, table)
    if [r["id"] for r in rows] != source["id"].to_pylist():
        raise ValueError(f"score IDs differ in part {index}")
    return table, rows


def commit_part(directory, index, source, generated, scores):
    validate_preserved(source, generated)
    if [r["id"] for r in scores] != source["id"].to_pylist():
        raise ValueError("score IDs do not match source")
    data, scorefile, done = part_paths(directory, index)
    atomic_parquet(data, generated)
    atomic_json(scorefile, scores)
    atomic_json(done, {"data_sha256": sha256_file(data), "scores_sha256": sha256_file(scorefile)})
