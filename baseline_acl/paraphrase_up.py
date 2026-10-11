#!/usr/bin/env python3
"""Ordinary Dipper paraphrasing of EasyGAD training teacher responses.

Only teacher_response is replaced. The parquet schema, metadata, row order,
IDs, prompts, and all other columns are retained and checked after writing.
Generation has no watermark processor, detector, or adversarial objective.
Uses Dipper's input template and sampling example, with whole-response
paraphrasing instead of the author's three-sentence windows. The ACL paper
does not disclose all paraphrasing hyperparameters. --inspect and --preflight
need no GPU/model.
"""

from __future__ import annotations

import argparse
from collections import Counter
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field, replace
import hashlib
from importlib import metadata
import json
import math
import os
from pathlib import Path
import re
import sys
import tempfile
import time
from typing import Callable


FORMAT_VERSION = 3
BASELINE_DIR = Path(__file__).resolve().parent
DEFAULT_NLTK_DATA = BASELINE_DIR / "nltk_data"
EXPECTED_COLUMNS = [
    "id", "content", "teacher_response", "category", "grounded", "flaw", "agreement"
]
DIPPER_MODEL_CARD = "https://huggingface.co/kalpeshk2011/dipper-paraphraser-xxl"
INPUT_TEMPLATE = "lexical = {lex_code}, order = {order_code}{prefix} <sent> {window} </sent>"
REFUSAL_RE = re.compile(
    r"^\s*(?:i(?:['’]m| am) sorry\b|sorry[,!:]|"
    r"i (?:cannot|can['’]t|am unable to) (?:help|assist|paraphrase|rewrite|comply|provide)\b|"
    r"as an ai\b.{0,120}\b(?:cannot|can['’]t|unable))", re.IGNORECASE | re.DOTALL
)
PREFACE_RE = re.compile(
    r"^\s*(?:here(?:['’]s| is) (?:the|a|your) (?:paraphrase|paraphrased|rewritten)|"
    r"(?:paraphrased|rewritten) (?:response|text)\s*:)", re.IGNORECASE
)


@dataclass(frozen=True)
class GenerationConfig:
    batch_size: int = 1
    max_input_tokens: int = 4096
    max_output_length: int = 4096
    lex_diversity: int = 60
    order_diversity: int = 0
    top_p: float = 0.75
    top_k: int = 0
    temperature: float = 1.0
    dtype: str = "float32"
    seed: int = 42
    on_failure: str = "error"
    max_attempts: int = 1

    def validate(self) -> None:
        if self.batch_size <= 0 or self.max_input_tokens <= 0 or self.max_output_length < 2:
            raise ValueError("batch/input limits must be positive and decoder max length must be at least two")
        for value in (self.lex_diversity, self.order_diversity):
            if value not in (0, 20, 40, 60, 80, 100):
                raise ValueError("Dipper lexical/order diversity must be one of 0,20,40,60,80,100")
        if self.dtype not in ("float32", "bfloat16"):
            raise ValueError("dtype must be float32 or bfloat16")
        if self.top_k != 0:
            raise ValueError("top_k is fixed to zero, disabling filtering as in the author's top_k=None example")
        if not math.isfinite(self.temperature) or self.temperature <= 0:
            raise ValueError("temperature must be finite and positive")
        if not math.isfinite(self.top_p) or not 0 < self.top_p <= 1:
            raise ValueError("top p must be in (0, 1]")
        if self.on_failure not in ("error", "keep-original"):
            raise ValueError("on failure must be error or keep-original")
        if self.max_attempts < 1:
            raise ValueError("max attempts must be positive")
        if self.seed < 0:
            raise ValueError("seed must be nonnegative")


@dataclass(frozen=True)
class GeneratedResponse:
    text: str
    finish_reason: str
    output_tokens: int
    windows: list[dict] = field(default_factory=list)
    issues: list[str] = field(default_factory=list)


def parse_visible_gpus(visible: str | None, requested_count: int | None = None) -> list[str]:
    """Use only explicitly selected cards; never fall back to all system GPUs."""
    if requested_count is not None and (type(requested_count) is not int or requested_count < 1):
        raise ValueError("--num-gpus must be a positive integer")
    values = [value.strip() for value in (visible or "").split(",")]
    uuid = r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
    pattern = rf"(?:[0-9]+|GPU-{uuid}|MIG-{uuid}|MIG-GPU-{uuid}/[0-9]+/[0-9]+)"
    if not values or any(not re.fullmatch(pattern, value) for value in values):
        raise ValueError("set CUDA_VISIBLE_DEVICES to chosen GPU IDs separated by ASCII commas, e.g. 1,3")
    normalized = [str(int(value)) if value.isdigit() else value.lower() for value in values]
    if len(set(normalized)) != len(values):
        raise ValueError("CUDA_VISIBLE_DEVICES contains duplicate GPU IDs")
    if requested_count is not None and requested_count != len(values):
        raise ValueError(f"--num-gpus={requested_count} but CUDA_VISIBLE_DEVICES selects {len(values)} GPUs")
    return values


def select_dtype(requested: str, devices: list[dict]) -> str:
    """All replicas share one recorded precision, including on mixed hardware."""
    if requested not in ("auto", "float32", "bfloat16") or not devices:
        raise ValueError("dtype must be auto/float32/bfloat16 with at least one selected GPU")
    bf16 = all(device.get("bf16_supported") is True for device in devices)
    if requested == "bfloat16" and not bf16:
        raise ValueError("explicit bfloat16 requires support on every selected GPU; no silent dtype fallback")
    return ("bfloat16" if bf16 else "float32") if requested == "auto" else requested


def probe_selected_gpus(gpu_ids: list[str]) -> list[dict]:
    import torch

    if not torch.cuda.is_available() or torch.cuda.device_count() != len(gpu_ids):
        raise RuntimeError("CUDA cannot see exactly the selected GPUs; check CUDA_VISIBLE_DEVICES and --num-gpus")
    devices = []
    for logical, gpu_id in enumerate(gpu_ids):
        with torch.cuda.device(logical):
            props = torch.cuda.get_device_properties(logical)
            free, total = torch.cuda.mem_get_info(logical)
            # Request native support; emulation is not sufficient for T5-XXL.
            supported = torch.cuda.is_bf16_supported(including_emulation=False)
            devices.append({"gpu_id": gpu_id, "name": props.name, "bf16_supported": bool(supported),
                            "free_gib": round(free / 2**30, 2), "total_gib": round(total / 2**30, 2)})
    return devices


def canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def text_sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def generation_seed(base_seed: int, row_index: int, attempt: int) -> int:
    return (base_seed + row_index + (attempt - 1) * 1_000_003) % (2**63 - 1)


def window_generation_seed(row_seed: int, window_index: int) -> int:
    return (row_seed + window_index * 10_000_019) % (2**63 - 1)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def dipper_weight_source(directory: str | Path) -> tuple[bool, Path]:
    """Validate only the weight source that Transformers will load.

    A directory may retain both safetensors and legacy PyTorch indices while
    containing only one set of shards. Prefer safetensors, without requiring
    the unused legacy shards or silently falling back from a broken safe set.
    """
    model_path = Path(directory).expanduser()
    for filename, use_safetensors in (
        ("model.safetensors", True),
        ("model.safetensors.index.json", True),
        ("pytorch_model.bin", False),
        ("pytorch_model.bin.index.json", False),
    ):
        source = model_path / filename
        if not source.is_file():
            continue
        if filename.endswith(".index.json"):
            index = json.loads(source.read_text(encoding="utf-8"))
            weight_map = index.get("weight_map") if isinstance(index, dict) else None
            if not isinstance(weight_map, dict) or not weight_map:
                raise ValueError(f"Dipper weight index has no valid weight_map: {source}")
            shards = list(weight_map.values())
            if any(not isinstance(shard, str) or not shard for shard in shards):
                raise ValueError(f"Dipper weight index has an invalid shard name: {source}")
            for shard in sorted(set(shards)):
                if not (model_path / shard).is_file():
                    raise FileNotFoundError(f"Dipper weight shard is missing: {model_path / shard}")
        return use_safetensors, source
    raise FileNotFoundError(f"Dipper weights are missing from {model_path}; --preflight needs only tokenizer assets")


def asset_identity(directory: str, *, weights_required: bool = False) -> dict:
    """Fingerprint configs/tokenizer bytes and the local weight file manifest.

    Large weight files are identified by name, size and mtime, rather than read
    in full. Loading is local-only so a missing asset cannot trigger a download.
    """
    model_path = Path(directory).expanduser()
    identity = {"path": str(model_path.resolve()), "files": []}
    if model_path.is_dir():
        for path in sorted(model_path.iterdir()):
            if not path.is_file():
                continue
            if path.name == "prepare_manifest.json":
                # Asset preparation timestamps are operational metadata, not a
                # different tokenizer/model. Keep only stable source provenance.
                manifest = json.loads(path.read_text(encoding="utf-8"))
                identity["provenance"] = {key: manifest[key] for key in ("repo_id", "revision") if key in manifest}
                continue
            stat = path.stat()
            entry = {"name": path.name, "size": stat.st_size, "mtime_ns": stat.st_mtime_ns}
            if path.suffix in (".json", ".txt", ".model"):
                entry["sha256"] = file_sha256(path)
            elif path.suffix not in (".safetensors", ".bin"):
                continue
            identity["files"].append(entry)
    else:
        raise FileNotFoundError(f"local asset directory does not exist: {model_path}")
    if weights_required:
        config_path = model_path / "config.json"
        if not config_path.is_file() or json.loads(config_path.read_text(encoding="utf-8")).get("model_type") != "t5":
            raise ValueError(f"Dipper requires a local model with config.json model_type=t5: {model_path}")
        dipper_weight_source(model_path)
    return identity


def model_identity(model: str, tokenizer: str) -> dict:
    identity = {"model": asset_identity(model, weights_required=True), "tokenizer": asset_identity(tokenizer)}
    identity["versions"] = {}
    for package in ("torch", "transformers", "nltk", "sentencepiece", "pyarrow"):
        try:
            identity["versions"][package] = metadata.version(package)
        except metadata.PackageNotFoundError:
            identity["versions"][package] = "unavailable"
    return identity


def read_source(path: Path):
    import pyarrow as pa
    import pyarrow.parquet as pq

    table = pq.read_table(path)
    if table.schema.names != EXPECTED_COLUMNS:
        raise ValueError(f"unexpected columns {table.schema.names}; expected {EXPECTED_COLUMNS}")
    target = table.schema.field("teacher_response")
    if not pa.types.is_string(target.type):
        raise ValueError(f"teacher_response must be Arrow string, got {target.type}")
    if not table.num_rows:
        raise ValueError("source training parquet is empty")
    for index, value in enumerate(table["teacher_response"].to_pylist()):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"empty/null source teacher_response at row {index}")
    return table


def inspect_source(path: Path) -> dict:
    """Read and validate the parquet without importing a model or GPU runtime."""
    table = read_source(path)
    lengths = [len(value) for value in table["teacher_response"].to_pylist()]
    return {
        "input": str(path.resolve()), "input_sha256": file_sha256(path),
        "rows": table.num_rows, "columns": table.schema.names,
        "schema": str(table.schema),
        "schema_sha256": hashlib.sha256(table.schema.serialize().to_pybytes()).hexdigest(),
        "response_characters": {"min": min(lengths), "max": max(lengths), "mean": sum(lengths) / len(lengths)},
        "null_counts": {name: table[name].null_count for name in table.schema.names},
        "token_budget_checked": False,
        "note": "CPU parquet inspection only; exact model token budgets are checked before generation.",
    }


def load_sentence_splitter(nltk_data: Path | None = None) -> Callable:
    import nltk
    nltk_data = (nltk_data or DEFAULT_NLTK_DATA).resolve()
    if not nltk_data.is_dir():
        raise FileNotFoundError(f"NLTK data directory does not exist: {nltk_data}")
    # Keep the chosen experiment resources authoritative; no global cache can
    # silently substitute a different English sentence tokenizer.
    nltk.data.path[:] = [str(nltk_data)]
    try:
        nltk.sent_tokenize("A first sentence. A second sentence.", language="english")
    except LookupError as error:
        raise RuntimeError("NLTK English Punkt resources are missing; install punkt and punkt_tab with the asset downloader. No alternate sentence splitter is used.") from error
    english = nltk_data / "tokenizers" / "punkt_tab" / "english"
    files = []
    for name in ("abbrev_types.txt", "collocations.tab", "ortho_context.tab", "sent_starters.txt"):
        path = english / name
        if not path.is_file():
            raise FileNotFoundError(f"English Punkt resource is missing: {path}")
        files.append({"name": name, "sha256": file_sha256(path)})
    try:
        version = metadata.version("nltk")
    except metadata.PackageNotFoundError:
        version = "unavailable"
    splitter = lambda text: nltk.sent_tokenize(text, language="english")
    splitter.resource_identity = {"directory": str(nltk_data), "nltk_version": version, "english_punkt_tab": files}
    return splitter


def render_dipper_input(window: str, prefix: str, config: GenerationConfig) -> str:
    return INPUT_TEMPLATE.format(lex_code=100 - config.lex_diversity, order_code=100 - config.order_diversity,
                                 prefix=f" {prefix}" if prefix else "", window=window)


def prepare_response(tokenizer, response: str, config: GenerationConfig, sentence_splitter: Callable | None = None) -> dict:
    """Join ALL sentences into one complete answer, never three-sentence chunks.

    The internal ``windows`` list is retained for durable audit records, but
    contains exactly one full-response item. No generated prefix is needed.
    """
    normalized = " ".join(response.split())
    sentences = (sentence_splitter or load_sentence_splitter())(normalized)
    if not sentences or any(not isinstance(sentence, str) or not sentence.strip() for sentence in sentences):
        raise ValueError("NLTK sentence splitting produced no valid sentences")
    source_tokens = len(tokenizer.encode(response, add_special_tokens=False))
    text = " ".join(sentences)
    input_tokens = len(tokenizer.encode(render_dipper_input(text, "", config), add_special_tokens=True))
    answer_tokens = len(tokenizer.encode(text, add_special_tokens=True))
    issues = ["full_response_exceeds_encoder_budget"] if input_tokens > config.max_input_tokens else []
    # Source length does not constrain decoder output length. Ending naturally
    # in EOS avoids hard truncation, but does not guarantee factual completeness.
    return {"windows": [{"text": text, "source_tokens": answer_tokens, "minimum_input_tokens": input_tokens}],
            "sentence_count": len(sentences), "prompt_tokens": input_tokens,
            "source_tokens": source_tokens, "issues": issues}


def preflight_source(path: Path, tokenizer, config: GenerationConfig, sentence_splitter: Callable) -> dict:
    config.validate()
    table = read_source(path)
    prepared = [prepare_response(tokenizer, text, config, sentence_splitter) for text in table["teacher_response"].to_pylist()]
    windows = [window for row in prepared for window in row["windows"]]
    invalid = [{"row_index": index, "id": table["id"][index].as_py(), "issues": row["issues"]}
               for index, row in enumerate(prepared) if row["issues"]]
    return {"input": str(path.resolve()), "input_sha256": file_sha256(path), "rows": table.num_rows,
            "config": asdict(config), "sentence_splitter_resources": getattr(sentence_splitter, "resource_identity", {}),
            "tokenizer_preflight": True, "model_weights_loaded": False,
            "paraphrase_mode": "whole_response", "generation_inputs": len(windows), "inputs_per_row": 1,
            "max_sentences_per_row": max(row["sentence_count"] for row in prepared),
            "max_source_response_tokens_including_eos": max(window["source_tokens"] for window in windows),
            "source_responses_longer_than_decoder_allowance": sum(window["source_tokens"] > config.max_output_length - 1 for window in windows),
            "max_full_response_input_tokens": max(window["minimum_input_tokens"] for window in windows),
            "invalid_rows": invalid, "valid": not invalid,
            "note": "All sentences from each response are passed in one input, without chunks or rolling prefixes. Encoder and decoder budgets are independent; natural EOS does not guarantee semantic completeness."}


def response_issues(generated: GeneratedResponse, source: str, config: GenerationConfig) -> list[str]:
    issues = []
    if not isinstance(generated.text, str) or not generated.text.strip():
        issues.append("empty_output")
    if generated.finish_reason != "stop":
        issues.append("length_limit" if generated.finish_reason == "length" else "unexpected_finish_reason")
    if type(generated.output_tokens) is not int or generated.output_tokens < 1:
        issues.append("invalid_output_token_count")
    if isinstance(generated.text, str):
        if REFUSAL_RE.search(generated.text) and not REFUSAL_RE.search(source):
            issues.append("refusal")
        if PREFACE_RE.search(generated.text) and not PREFACE_RE.search(source):
            issues.append("editorial_preface")
    return issues + generated.issues


def paraphrase_windows(prepared: dict, generate_window: Callable, tokenizer, config: GenerationConfig,
                       row_index: int, attempt: int) -> GeneratedResponse:
    """One Dipper call for the complete response; name retained for audit users."""
    if len(prepared["windows"]) != 1:
        raise ValueError("whole-response mode requires exactly one complete response; chunked inputs are refused")
    window = prepared["windows"][0]
    prompt = render_dipper_input(window["text"], "", config)
    input_tokens = len(tokenizer.encode(prompt, add_special_tokens=True))
    seed = generation_seed(config.seed, row_index, attempt)
    record = {"window_index": 0, "source_sha256": text_sha256(window["text"]), "source_tokens": window["source_tokens"],
              "prefix_sha256": text_sha256(""), "input_tokens": input_tokens, "seed": seed}
    if input_tokens > config.max_input_tokens:
        issues = ["full_response_exceeds_encoder_budget"]
        record.update(output_text="", output_tokens=0, decoder_length=0, finish_reason="input_limit", issues=issues)
        return GeneratedResponse("", "input_limit", 0, [record], issues)
    candidate = generate_window(prompt, seed)
    issues = response_issues(candidate, window["text"], config)
    if type(candidate.output_tokens) is int and candidate.output_tokens > config.max_output_length - 1:
        issues.append("full_response_output_exceeds_decoder_budget")
    record.update(output_text=candidate.text, output_tokens=candidate.output_tokens,
                  decoder_length=candidate.output_tokens + 1 if type(candidate.output_tokens) is int else None,
                  finish_reason=candidate.finish_reason, issues=issues)
    return GeneratedResponse(candidate.text, candidate.finish_reason, candidate.output_tokens, [record], issues)


def validate_window_audit(generated: GeneratedResponse, prepared: dict, tokenizer, config: GenerationConfig,
                          row_index: int, attempt: int) -> list[str]:
    issues = []
    if len(prepared["windows"]) != 1 or len(generated.windows) != 1:
        return ["whole_response_single_input_required"]
    window, record = prepared["windows"][0], generated.windows[0]
    expected_input = len(tokenizer.encode(render_dipper_input(window["text"], "", config), add_special_tokens=True))
    if (record.get("window_index") != 0 or record.get("source_sha256") != text_sha256(window["text"])
            or record.get("source_tokens") != window["source_tokens"] or record.get("prefix_sha256") != text_sha256("")
            or record.get("seed") != generation_seed(config.seed, row_index, attempt)
            or record.get("input_tokens") != expected_input):
        issues.append("full_response_audit_mismatch")
    if expected_input > config.max_input_tokens:
        issues.append("full_response_input_limit")
    count = record.get("output_tokens")
    if type(count) is not int or not 0 < count <= config.max_output_length - 1 or record.get("decoder_length") != count + 1:
        issues.append("full_response_decoder_limit")
    if record.get("finish_reason") != "stop" or record.get("issues"):
        issues.append("full_response_generation_failure")
    text = record.get("output_text")
    if not isinstance(text, str) or not text.strip():
        issues.append("full_response_empty_output")
    if generated.text != text or generated.output_tokens != count or generated.finish_reason != record.get("finish_reason"):
        issues.append("full_response_output_reconstruction_mismatch")
    return issues


@contextmanager
def checkpoint_lock(path: Path):
    """An OS lock is released even if a process exits unexpectedly."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.with_suffix(path.suffix + ".lock").open("a+b") as handle:
        handle.seek(0, os.SEEK_END)
        if not handle.tell():
            handle.write(b"0")
            handle.flush()
        handle.seek(0)
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as error:
            raise RuntimeError(f"another process is using checkpoint {path}") from error
        try:
            yield
        finally:
            handle.seek(0)
            if os.name == "nt":
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def append_record(handle, record: dict) -> None:
    handle.write(canonical_json(record) + "\n")
    handle.flush()
    os.fsync(handle.fileno())


def load_checkpoint(path: Path, expected_meta: dict, source_values: list[str], ids: list) -> tuple[dict[int, dict], dict[int, int], list[dict]]:
    complete = {}
    attempts = {}
    rejected = []
    config = GenerationConfig(**expected_meta["config"])
    # A crash can leave an incomplete final JSONL write. Only this final tail is
    # recoverable; malformed complete lines or duplicate successful rows fail.
    with path.open("rb") as handle:
        lines = handle.readlines()
    if not lines or not lines[0].endswith(b"\n"):
        raise ValueError("checkpoint has no durable metadata header")
    header = json.loads(lines[0])
    if header != expected_meta:
        raise ValueError("checkpoint fingerprint differs from input/model/config; use a new output path")
    repair_size = None
    if not lines[-1].endswith(b"\n"):
        repair_size = sum(map(len, lines[:-1]))
        lines.pop()
    for line_number, line in enumerate(lines[1:], 2):
        entry = json.loads(line)
        if entry.get("kind") not in ("result", "failure"):
            raise ValueError(f"invalid checkpoint record kind at line {line_number}")
        index = entry.get("row_index")
        if not isinstance(index, int) or not 0 <= index < len(source_values):
            raise ValueError(f"invalid checkpoint row at line {line_number}")
        if entry.get("id") != ids[index] or entry.get("source_sha256") != text_sha256(source_values[index]):
            raise ValueError(f"checkpoint source mismatch at row {index}")
        if index in complete:
            raise ValueError(f"checkpoint has an attempt after completed row {index}")
        attempt = entry.get("attempt")
        if entry.get("status") == "fallback" and entry.get("finish_reason") == "not_generated":
            if attempt != 0 or entry.get("seed") is not None or index in attempts:
                raise ValueError(f"invalid budget fallback attempt at row {index}")
        elif not isinstance(attempt, int) or not 1 <= attempt <= config.max_attempts or attempt != attempts.get(index, 0) + 1:
            raise ValueError(f"nonsequential or invalid checkpoint attempt at row {index}")
        else:
            if entry.get("seed") != generation_seed(config.seed, index, attempt):
                raise ValueError(f"checkpoint seed mismatch at row {index}")
            attempts[index] = attempt
            if entry.get("issues"):
                rejected.append(entry)
        if entry["kind"] == "failure":
            if entry.get("status") != "rejected" or not entry.get("issues"):
                raise ValueError(f"invalid rejected checkpoint attempt at row {index}")
            continue
        if entry.get("status") not in ("ok", "fallback") or not isinstance(entry.get("paraphrase"), str) or not entry["paraphrase"].strip():
            raise ValueError(f"invalid completed checkpoint row {index}")
        if entry["status"] == "fallback":
            if expected_meta["config"]["on_failure"] != "keep-original" or entry["paraphrase"] != source_values[index] or not entry.get("issues"):
                raise ValueError(f"unauthorized/invalid fallback at row {index}")
        else:
            candidate = GeneratedResponse(entry["paraphrase"], entry.get("finish_reason"), entry.get("output_tokens"))
            if entry.get("issues") or response_issues(candidate, source_values[index], config):
                raise ValueError(f"invalid accepted generation at checkpoint row {index}")
        complete[index] = entry
    if repair_size is not None:
        with path.open("r+b") as handle:
            handle.truncate(repair_size)
            handle.flush()
            os.fsync(handle.fileno())
        print("[resume] discarded an incomplete final checkpoint line", flush=True)
    return complete, attempts, rejected


def validate_output_paths(input_path: Path, output_path: Path, checkpoint_path: Path, audit_path: Path, resume: bool) -> None:
    paths = [path.resolve() for path in (input_path, output_path, checkpoint_path, audit_path)]
    if len(set(paths)) != len(paths):
        raise ValueError("input, output, checkpoint and audit paths must all differ")
    for index, left in enumerate(paths):
        for right in paths[index + 1:]:
            if left.exists() and right.exists() and os.path.samefile(left, right):
                raise ValueError("input, output, checkpoint and audit must not alias the same file")
    tokens = re.split(r"[_\-.]", input_path.stem.lower())
    if any(token in ("test", "val", "validation", "eval") for token in tokens):
        raise ValueError("this command rewrites training data only; held-out test/validation input is refused")
    if output_path.exists():
        raise FileExistsError(f"refusing to overwrite {output_path}; choose a new output")
    if audit_path.exists() and not resume:
        raise FileExistsError(f"refusing to overwrite {audit_path}; choose a new output")
    if checkpoint_path.exists() and not resume:
        raise FileExistsError(f"checkpoint exists: {checkpoint_path}; pass --resume")
    if resume and not checkpoint_path.is_file():
        raise FileNotFoundError(f"--resume requires an existing checkpoint: {checkpoint_path}")


def publish_new_file(temporary: Path, destination: Path) -> None:
    """Publish a complete file atomically without replacing an existing file."""
    if os.name == "nt":
        # Windows rename atomically refuses an existing destination. Hard-link
        # creation is unavailable in some local sandbox filesystems.
        os.rename(temporary, destination)
        return
    # Hard links are same-filesystem atomic and fail if the target already
    # exists, unlike os.replace. The temporary is always in this directory.
    os.link(temporary, destination)
    temporary.unlink()


def validate_orphan_audit(audit_path: Path, output_path: Path, meta: dict, total_rows: int, complete_rows: int) -> dict:
    """An audit-only publication is recoverable solely from a complete matching job."""
    report = json.loads(audit_path.read_text(encoding="utf-8"))
    if (complete_rows != total_rows or not report.get("complete") or report.get("metadata") != meta
            or report.get("output") != str(output_path.resolve()) or report.get("rows") != total_rows
            or report.get("processed_rows") != total_rows):
        raise FileExistsError(f"existing audit does not match a complete checkpoint; refusing to replace {audit_path}")
    return report


def write_final_outputs(source, responses: list[str], records: dict[int, dict], rejected: list[dict], output_path: Path, audit_path: Path, meta: dict, started: float, *, resume: bool = False) -> dict:
    import pyarrow as pa
    import pyarrow.parquet as pq

    index = source.schema.get_field_index("teacher_response")
    result = source.set_column(index, source.schema.field(index), pa.array(responses, type=source.schema.field(index).type))
    if not result.schema.equals(source.schema, check_metadata=True):
        raise AssertionError("replacement changed the original Arrow schema or metadata")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(prefix=output_path.name + ".", suffix=".tmp", dir=output_path.parent, delete=False) as handle:
        parquet_temp = Path(handle.name)
    audit_temp = None
    try:
        pq.write_table(result, parquet_temp, compression="zstd")
        # Windows fsync needs a writable descriptor for the newly written file.
        with parquet_temp.open("r+b") as handle:
            os.fsync(handle.fileno())
        reread = pq.read_table(parquet_temp)
        if reread.num_rows != source.num_rows or not reread.schema.equals(source.schema, check_metadata=True):
            raise AssertionError("written parquet row count/schema/metadata differs from source")
        unchanged = {}
        for name in source.schema.names:
            if name == "teacher_response":
                continue
            unchanged[name] = reread[name].equals(source[name])
            if not unchanged[name]:
                raise AssertionError(f"written parquet changed protected column {name}")
        if reread["teacher_response"].to_pylist() != responses:
            raise AssertionError("written teacher_response values differ from accepted outputs")
        statuses = Counter(record["status"] for record in records.values())
        original = source["teacher_response"].to_pylist()
        output_tokens = [record["output_tokens"] for record in records.values() if record["status"] == "ok"]
        report = {
            "format_version": FORMAT_VERSION, "complete": True, "method": "ordinary_untargeted_dipper_paraphrasing",
            "metadata": meta, "output": str(output_path.resolve()), "output_sha256": file_sha256(parquet_temp),
            "rows": source.num_rows, "processed_rows": len(records),
            "status_counts": dict(statuses), "fallback_rows": sorted(i for i, r in records.items() if r["status"] == "fallback"),
            "fallback_reasons": dict(Counter(issue for r in records.values() if r["status"] == "fallback" for issue in r["issues"])),
            "finish_reasons": dict(Counter(str(r["finish_reason"]) for r in records.values())),
            "accepted_attempts": dict(Counter(str(r["attempt"]) for r in records.values())),
            "rejected_generation_attempts": len(rejected),
            "rejected_attempt_reasons": dict(Counter(issue for r in rejected for issue in r["issues"])),
            "changed_teacher_responses": sum(left != right for left, right in zip(original, responses, strict=True)),
            "identical_accepted_responses": sum(r["status"] == "ok" and r["paraphrase"] == original[i] for i, r in records.items()),
            "schema_and_metadata_equal": True, "row_order_and_ids_equal": True, "protected_columns_equal": unchanged,
            "output_tokens": {"min": min(output_tokens), "max": max(output_tokens), "mean": sum(output_tokens) / len(output_tokens)} if output_tokens else None,
            "duration_seconds": round(time.monotonic() - started, 3),
            "semantic_preservation": "Dipper paraphrasing; not an automatic factual equivalence guarantee",
            "parameter_provenance": "Dipper author template/sampling with user-requested whole-response mode and enlarged decoder limit; full ACL paraphrasing hyperparameters were not disclosed",
            "paraphrase_mode": "whole_response",
            "model_card": DIPPER_MODEL_CARD,
        }
        # A separate targeted entrypoint can reuse the durable data writer.
        # Ordinary UP does not supply attack metadata and keeps its old contract.
        attack = meta["model"].get("attack")
        if attack is not None:
            if attack.get("method") != "targeted_dipper_paraphrasing":
                raise ValueError("unsupported attack method for the Dipper data writer")
            report.update(method=attack["method"], input_sha256=meta["input"]["sha256"], attack=attack)
            report["parameter_provenance"] = "ACL inverse watermark formula with explicit cross-tokenizer text projection; project adaptation, not an exact reproduction of unpublished TP code"
        attempted = {(r["row_index"], r["attempt"]): r for r in [*rejected, *records.values()] if r["attempt"] > 0}
        all_windows = [window for record in attempted.values() for window in record.get("windows", [])]
        report["response_input_checks"] = len(all_windows)
        report["generated_response_attempts"] = sum(type(window.get("output_tokens")) is int and window["output_tokens"] > 0 for window in all_windows)
        report["max_encoder_input_tokens"] = max((window["input_tokens"] for window in all_windows if type(window.get("input_tokens")) is int), default=None)
        report["max_decoder_sequence_length"] = max((window["decoder_length"] for window in all_windows if type(window.get("decoder_length")) is int), default=None)
        if audit_path.exists():
            if not resume:
                raise FileExistsError(f"refusing to overwrite {audit_path}")
            previous = validate_orphan_audit(audit_path, output_path, meta, source.num_rows, len(records))
            comparable_previous, comparable_report = dict(previous), dict(report)
            comparable_previous.pop("duration_seconds", None)
            comparable_report.pop("duration_seconds", None)
            if comparable_previous != comparable_report:
                raise FileExistsError(f"orphan audit verification/hash differs; refusing to replace {audit_path}")
            report = previous
            print("[resume] verified existing audit; publishing missing final parquet", flush=True)
        else:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n", prefix=audit_path.name + ".", suffix=".tmp", dir=audit_path.parent, delete=False) as handle:
                audit_temp = Path(handle.name)
                handle.write(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
                handle.flush()
                os.fsync(handle.fileno())
            # A crash between audit and parquet publication is recoverable above.
            publish_new_file(audit_temp, audit_path)
            audit_temp = None
        publish_new_file(parquet_temp, output_path)
        print(f"[done] {output_path}: {source.num_rows} rows; audit: {audit_path}", flush=True)
        return report
    finally:
        parquet_temp.unlink(missing_ok=True)
        if audit_temp is not None:
            audit_temp.unlink(missing_ok=True)


def run_paraphrasing(input_path: Path, output_path: Path, config: GenerationConfig, tokenizer, generator_factory: Callable,
                     identity: dict, *, resume: bool = False, checkpoint_path: Path | None = None, audit_path: Path | None = None,
                     sentence_splitter: Callable | None = None, prepare_fn: Callable | None = None,
                     candidate_issues_fn: Callable | None = None, validate_audit_fn: Callable | None = None,
                     metadata_builder: Callable | None = None, final_writer: Callable | None = None,
                     checkpoint_loader: Callable | None = None) -> dict:
    """Durable row orchestration with explicit model-specific contracts.

    The defaults retain the Dipper UP/backup TP behavior. A causal student TP
    supplies its own preparation, validation, metadata and persistence adapters
    and never invokes the default sentence splitter or T5 budget checks.
    """
    started = time.monotonic()
    config.validate()
    input_path, output_path = input_path.resolve(), output_path.resolve()
    checkpoint_path = (checkpoint_path or output_path.with_suffix(output_path.suffix + ".progress.jsonl")).resolve()
    audit_path = (audit_path or output_path.with_suffix(output_path.suffix + ".audit.json")).resolve()
    validate_output_paths(input_path, output_path, checkpoint_path, audit_path, resume)
    source = read_source(input_path)
    values, ids = source["teacher_response"].to_pylist(), source["id"].to_pylist()
    candidate_issues = candidate_issues_fn or response_issues
    validate_audit = validate_audit_fn or validate_window_audit
    load_progress = checkpoint_loader or load_checkpoint
    write_outputs = final_writer or write_final_outputs
    if prepare_fn is None:
        splitter = sentence_splitter or load_sentence_splitter()
        prepared = [prepare_response(tokenizer, value, config, splitter) for value in values]
    else:
        splitter = None
        prepared = [prepare_fn(tokenizer, value, config) for value in values]
    if metadata_builder is None:
        meta = {
            "kind": "meta", "format_version": FORMAT_VERSION,
            "input": {"path": str(input_path), "sha256": file_sha256(input_path), "rows": source.num_rows,
                      "schema_sha256": hashlib.sha256(source.schema.serialize().to_pybytes()).hexdigest()},
            "model": identity, "config": asdict(config),
            "input_template_sha256": text_sha256(INPUT_TEMPLATE),
            "segmentation_sha256": text_sha256(canonical_json([[window["text"] for window in row["windows"]] for row in prepared])),
            "sentence_splitter_resources": getattr(splitter, "resource_identity", {}),
            "generation_contract": {"architecture": "T5_encoder_decoder", "paraphrase_mode": "whole_response",
                                    "inputs_per_response": 1, "initial_prefix": "", "rolling_prefix": False,
                                    "sentence_splitter": "nltk.sent_tokenize", "language": "english", "do_sample": True,
                                    "top_k_zero_equivalent_to_author_example_none": True, "decoder_max_length_includes_start_token": True},
        }
    else:
        meta = metadata_builder(input_path, source, identity, config, prepared)
    meta["fingerprint"] = text_sha256(canonical_json(meta))
    over_budget = [(index, info["issues"]) for index, info in enumerate(prepared) if info["issues"]]
    if over_budget and config.on_failure == "error":
        raise ValueError(f"{len(over_budget)} complete source responses exceed the input budget; examples: {over_budget[:10]}. "
                         "Review --max-input-tokens; whole-response mode never falls back to chunks. No source text is truncated.")
    print(f"[preflight] rows={source.num_rows}, maximum source tokens={max(p['source_tokens'] for p in prepared)}, "
          f"maximum complete response input={max(p['prompt_tokens'] for p in prepared)}, "
          "all sentences per row are passed in ONE input; no chunks or rolling prefixes", flush=True)
    with checkpoint_lock(checkpoint_path):
        # Recheck after obtaining the lock to avoid two writers racing at startup.
        validate_output_paths(input_path, output_path, checkpoint_path, audit_path, resume)
        complete, attempts_done, rejected = load_progress(checkpoint_path, meta, values, ids) if resume else ({}, {}, [])
        for index, record in complete.items():
            if any(record.get(key) != prepared[index][key] for key in ("prompt_tokens", "source_tokens")):
                raise ValueError(f"checkpoint token counts differ at row {index}")
            if record["status"] == "ok":
                candidate = GeneratedResponse(record["paraphrase"], record["finish_reason"], record["output_tokens"],
                                              record.get("windows", []), record.get("generation_issues", []))
                if candidate_issues(candidate, values[index], config) or validate_audit(candidate, prepared[index], tokenizer, config, index, record["attempt"]):
                    raise ValueError(f"invalid accepted window audit at row {index}")
        if audit_path.exists():
            validate_orphan_audit(audit_path, output_path, meta, source.num_rows, len(complete))
        with checkpoint_path.open("a" if resume else "x", encoding="utf-8", newline="\n") as handle:
            if not resume:
                append_record(handle, meta)
            print(f"[resume] accepted {len(complete)}/{source.num_rows} completed rows", flush=True)
            pending = []
            for index, info in enumerate(prepared):
                if index in complete:
                    continue
                if info["issues"]:
                    record = {"kind": "result", "row_index": index, "id": ids[index], "source_sha256": text_sha256(values[index]),
                              "status": "fallback", "paraphrase": values[index], "issues": info["issues"], "finish_reason": "not_generated",
                              "prompt_tokens": info["prompt_tokens"], "source_tokens": info["source_tokens"], "output_tokens": info["source_tokens"],
                              "attempt": 0, "seed": None, "windows": [], "generation_issues": info["issues"]}
                    append_record(handle, record)
                    complete[index] = record
                else:
                    pending.append(index)
            exhausted = [i for i in pending if attempts_done.get(i, 0) >= config.max_attempts]
            if exhausted:
                raise RuntimeError(f"rows already exhausted --max-attempts={config.max_attempts}: {exhausted[:20]}; "
                                   "no final training parquet was written. Choose a new output/config after reviewing failures.")
            generator = generator_factory() if pending else None
            try:
                streaming = callable(getattr(generator, "iter_generate", None))
                # Streaming workers receive the entire pending pool, not a
                # batch_size=1 slice that would serialize multiple GPUs.
                groups = [pending] if streaming else [pending[offset:offset + config.batch_size]
                                                     for offset in range(0, len(pending), config.batch_size)]
                for indices in groups:
                    terminal_failures = []
                    while indices:
                        attempt_numbers = [attempts_done.get(i, 0) + 1 for i in indices]
                        expected = dict(zip(indices, attempt_numbers, strict=True))
                        if streaming:
                            results = generator.iter_generate([prepared[i] for i in indices], indices, attempt_numbers)
                        else:
                            generated = generator.generate([prepared[i] for i in indices], indices, attempt_numbers)
                            if len(generated) != len(indices):
                                raise RuntimeError("backend returned a different number of responses; no unmatched row is accepted")
                            results = zip(indices, attempt_numbers, generated, strict=True)
                        retries, seen = [], set()
                        for result in results:
                            if not isinstance(result, (tuple, list)) or len(result) != 3:
                                raise RuntimeError("malformed backend result; expected (index, attempt, response)")
                            index, attempt, candidate = result
                            if type(index) is not int or index not in expected:
                                raise RuntimeError(f"unexpected/invalid backend row index: {index!r}")
                            if index in seen:
                                raise RuntimeError(f"duplicate backend row index: {index}")
                            if type(attempt) is not int or attempt != expected[index]:
                                raise RuntimeError(f"unexpected backend attempt for row {index}: {attempt!r}")
                            if not isinstance(candidate, GeneratedResponse):
                                raise RuntimeError(f"invalid backend response for row {index}")
                            seen.add(index)
                            issues = candidate_issues(candidate, values[index], config)
                            issues.extend(validate_audit(candidate, prepared[index], tokenizer, config, index, attempt))
                            issues = list(dict.fromkeys(issues))
                            info = prepared[index]
                            record = {"kind": "result", "row_index": index, "id": ids[index], "source_sha256": text_sha256(values[index]),
                                      "status": "ok", "paraphrase": candidate.text, "issues": issues, "finish_reason": candidate.finish_reason,
                                      "prompt_tokens": info["prompt_tokens"], "source_tokens": info["source_tokens"], "output_tokens": candidate.output_tokens,
                                      "attempt": attempt, "seed": generation_seed(config.seed, index, attempt),
                                      "windows": candidate.windows, "generation_issues": candidate.issues}
                            if issues:
                                record["candidate"] = record.pop("paraphrase")
                                if attempt >= config.max_attempts and config.on_failure == "keep-original":
                                    record["status"], record["paraphrase"] = "fallback", values[index]
                                else:
                                    record["kind"], record["status"] = "failure", "rejected"
                                    if attempt >= config.max_attempts:
                                        terminal_failures.append((index, issues))
                                    else:
                                        retries.append(index)
                                rejected.append(record)
                            append_record(handle, record)
                            attempts_done[index] = attempt
                            if record["kind"] == "result":
                                complete[index] = record
                            if streaming and (len(complete) % 20 == 0 or issues or len(complete) == source.num_rows):
                                print(f"[progress] completed={len(complete)}/{source.num_rows}, workers={generator.worker_count}, "
                                      f"elapsed={time.monotonic() - started:.1f}s", flush=True)
                            if streaming and terminal_failures:
                                raise RuntimeError(f"paraphrases exhausted {config.max_attempts} attempts: {terminal_failures}; "
                                                   "no final training parquet was written; completed rows are preserved in the checkpoint")
                        if seen != set(expected):
                            raise RuntimeError(f"backend returned missing row indices: {sorted(set(expected) - seen)}")
                        print(f"[batch] completed={len(complete)}/{source.num_rows}, attempted={len(indices)}, retry_rows={len(retries)}, "
                              f"fallbacks={sum(r['status'] == 'fallback' for r in complete.values())}, elapsed={time.monotonic() - started:.1f}s", flush=True)
                        indices = retries
                    if terminal_failures:
                        raise RuntimeError(f"paraphrases exhausted {config.max_attempts} attempts: {terminal_failures}; "
                                           "no final training parquet was written. Review checkpoint failures before choosing a new output/config.")
            finally:
                close = getattr(generator, "close", None)
                if callable(close):
                    close()
        if len(complete) != source.num_rows:
            raise AssertionError("cannot finalize a partial dataset")
        if file_sha256(input_path) != meta["input"]["sha256"]:
            raise RuntimeError("input parquet changed during generation; finalization refused")
        return write_outputs(source, [complete[i]["paraphrase"] for i in range(source.num_rows)], complete, rejected,
                             output_path, audit_path, meta, started, resume=resume)


class DipperGenerator:
    def __init__(self, model: str, config: GenerationConfig, tokenizer, *, logits_processor=None):
        use_safetensors, _ = dipper_weight_source(model)
        import torch
        from transformers import T5ForConditionalGeneration
        if not torch.cuda.is_available() or torch.cuda.device_count() != 1:
            raise RuntimeError("Dipper requires exactly one visible CUDA GPU")
        if config.dtype == "bfloat16" and not torch.cuda.is_bf16_supported():
            raise RuntimeError("the selected GPU does not support bfloat16")
        self.torch, self.tokenizer, self.config = torch, tokenizer, config
        self.logits_processor = logits_processor
        dtype = torch.float32 if config.dtype == "float32" else torch.bfloat16
        self.model = T5ForConditionalGeneration.from_pretrained(
            model, torch_dtype=dtype, local_files_only=True,
            use_safetensors=use_safetensors).to("cuda:0").eval()

    def generate_window(self, prompt: str, seed: int) -> GeneratedResponse:
        torch = self.torch
        torch.manual_seed(seed)
        inputs = self.tokenizer([prompt], return_tensors="pt", add_special_tokens=True, truncation=False).to("cuda:0")
        if inputs["input_ids"].shape[1] > self.config.max_input_tokens:
            raise RuntimeError("Dipper tokenizer input exceeded its prechecked encoder budget")
        with torch.inference_mode():
            extra = {"logits_processor": [self.logits_processor]} if getattr(self, "logits_processor", None) is not None else {}
            sequences = self.model.generate(**inputs, do_sample=True, top_p=self.config.top_p, top_k=0,
                                            temperature=self.config.temperature, max_length=self.config.max_output_length, **extra)
        # T5 returns decoder sequences, including its initial start token. There
        # is no encoder prompt in the output to slice away as in causal models.
        tokens = sequences[0].tolist()
        eos = self.model.generation_config.eos_token_id
        eos_ids = set(eos if isinstance(eos, list) else [eos])
        reason = "stop" if len(tokens) > 1 and tokens[-1] in eos_ids else "length"
        forced_eos = self.model.generation_config.forced_eos_token_id
        if forced_eos is not None and len(tokens) >= self.config.max_output_length:
            reason = "length"
        text = self.tokenizer.batch_decode(sequences, skip_special_tokens=True)[0]
        return GeneratedResponse(text, reason, max(0, len(tokens) - 1))

    def generate(self, prepared_rows: list[dict], indices: list[int], attempts: list[int]) -> list[GeneratedResponse]:
        return [paraphrase_windows(row, self.generate_window, self.tokenizer, self.config, index, attempt)
                for row, index, attempt in zip(prepared_rows, indices, attempts, strict=True)]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", type=Path, help="New training parquet; required except with --inspect")
    parser.add_argument("--checkpoint", type=Path, help="Default: <output>.progress.jsonl")
    parser.add_argument("--audit", type=Path, help="Default: <output>.audit.json")
    parser.add_argument("--model", default=str(BASELINE_DIR / "models" / "dipper-paraphraser-xxl"), help="Local Dipper T5-XXL weights")
    parser.add_argument("--tokenizer", default=str(BASELINE_DIR / "models" / "t5-v1_1-xxl-tokenizer"), help="Local google/t5-v1_1-xxl tokenizer")
    parser.add_argument("--nltk-data", type=Path, default=DEFAULT_NLTK_DATA, help="Local authoritative NLTK directory; global resources are not searched")
    parser.add_argument("--num-gpus", type=int, help="GPU count, not IDs; must match CUDA_VISIBLE_DEVICES, or inferred from it when omitted")
    parser.add_argument("--dtype", choices=("auto", "float32", "bfloat16"), default="auto", help="Auto uses bf16 only when every selected GPU supports it, otherwise float32; author example uses float32")
    parser.add_argument("--batch-size", type=int, default=1, help="Legacy progress-group size, not GPU count or tensor batch size; parallel workers dynamically schedule individual answers")
    parser.add_argument("--max-input-tokens", type=int, default=4096, help="Full-response encoder budget, including the input template and encoder EOS; never truncate or chunk")
    parser.add_argument("--max-output-length", type=int, default=4096, help="Full-response decoder total max_length including start token; raised from author's 512-window example")
    parser.add_argument("--lex-diversity", type=int, choices=(0, 20, 40, 60, 80, 100), default=60)
    parser.add_argument("--order-diversity", type=int, choices=(0, 20, 40, 60, 80, 100), default=0)
    parser.add_argument("--temperature", type=float, default=1.0, help="Explicit Transformers default; the author example does not specify it")
    parser.add_argument("--top-p", type=float, default=0.75)
    parser.add_argument("--top-k", type=int, choices=(0,), default=0, help="Disable top-k, equivalent to the author's top_k=None")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--on-failure", choices=("error", "keep-original"), default="error",
                        help="Explicit opt-in to retain and audit originals for rejected/budget-exceeding rows")
    parser.add_argument("--max-attempts", type=int, default=1, help="One ordinary attempt by default; explicit >1 enables engineering retries for invalid outputs")
    parser.add_argument("--resume", action="store_true", help="Reuse completed checkpoint rows with matching fingerprint")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--inspect", action="store_true", help="Validate and report parquet only; no tokenizer, GPU or writes")
    modes.add_argument("--preflight", action="store_true", help="CPU tokenizer+NLTK whole-response budget report; no model weights, GPU or writes")
    args = parser.parse_args(argv)
    if args.num_gpus is not None and args.num_gpus < 1:
        parser.error("--num-gpus must be positive")
    if not args.inspect and not args.preflight and args.output is None:
        parser.error("--output is required unless --inspect/--preflight is used")
    return args


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    if args.inspect:
        print(json.dumps(inspect_source(args.input), ensure_ascii=False, indent=2))
        return
    config_values = {name: getattr(args, name) for name in GenerationConfig.__dataclass_fields__}
    # CPU-only preflight checks text budgets and never probes CUDA. A concrete
    # runtime dtype is selected and fingerprinted below for real generation.
    config_values["dtype"] = "float32" if args.dtype == "auto" else args.dtype
    config = GenerationConfig(**config_values)
    config.validate()
    from transformers import T5Tokenizer
    asset_identity(args.tokenizer)
    tokenizer = T5Tokenizer.from_pretrained(args.tokenizer, local_files_only=True, legacy=True)
    # This is an encoder budget, not decoder max_length. T5 uses relative
    # positions; avoid the tokenizer's generic 512-token warning while keeping
    # our explicit whole-response checks and truncation=False authoritative.
    tokenizer.model_max_length = config.max_input_tokens
    splitter = load_sentence_splitter(args.nltk_data)
    if args.preflight:
        report = preflight_source(args.input, tokenizer, config, splitter)
        report["tokenizer_identity"] = asset_identity(args.tokenizer)
        print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)
        if not report["valid"]:
            raise ValueError(f"Dipper CPU preflight found {len(report['invalid_rows'])} oversized full responses; no text was truncated or chunked")
        return
    checkpoint = args.checkpoint or args.output.with_suffix(args.output.suffix + ".progress.jsonl")
    audit = args.audit or args.output.with_suffix(args.output.suffix + ".audit.json")
    validate_output_paths(args.input, args.output, checkpoint, audit, args.resume)
    visible = parse_visible_gpus(os.environ.get("CUDA_VISIBLE_DEVICES"), args.num_gpus)
    identity = model_identity(args.model, args.tokenizer)
    devices = probe_selected_gpus(visible)
    config = replace(config, dtype=select_dtype(args.dtype, devices))
    print(f"[gpu-plan] count={len(visible)}, dtype={config.dtype}, selected={canonical_json(devices)}; "
          "one complete Dipper replica per GPU; VRAM is NOT pooled", flush=True)
    if __package__:
        from .dipper_parallel import ParallelDipperGenerator
    else:
        from dipper_parallel import ParallelDipperGenerator
    factory = lambda: ParallelDipperGenerator(args.model, config, args.tokenizer, visible)
    run_paraphrasing(args.input, args.output, config, tokenizer, factory, identity,
                     resume=args.resume, checkpoint_path=checkpoint, audit_path=audit, sentence_splitter=splitter)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, RuntimeError, OSError) as error:
        print(f"[error] {error}", file=sys.stderr, flush=True)
        sys.exit(1)
