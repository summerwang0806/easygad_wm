"""Offline, answer-only reference-LM PPL for saved generation JSONL files.

This module has no import-time torch/transformers dependency.  It never loads a
student's weights or generates answers.  The scoring protocol reconstructs the
source generation prompt, encodes prompt and answer separately with the fixed
reference tokenizer, and scores every answer token (including the first).
"""
from __future__ import annotations

import gc
import hashlib
import importlib.metadata
import json
import math
import os
import platform
import sys
import tempfile
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, TextIO


SCHEMA = "saved-answer-reference-ppl-v1"
DEFAULT_MODEL = "/shared/public_models/Llama-3-8B"
LEGACY_MAX_PROMPT_TOKENS = 2048
PROTOCOL = {
    "prompt": "source-generation-prompt; source chat template, not reference chat template",
    "boundary": "encode prompt and answer separately with add_special_tokens=False, then concatenate",
    "bos": "one reference BOS at start when defined; no extra EOS",
    "loss": "causal next-token NLL on all answer tokens, including the first; no prompt or padding loss",
    "aggregate": "exp(sum(answer NLL) / sum(scored answer tokens)); not mean per-answer PPL",
    "source_tokenizer_selection": "explicit override, otherwise row.model_path; fallback assumes the generation tokenizer matches that checkpoint",
    "legacy_prompt_limit": LEGACY_MAX_PROMPT_TOKENS,
    "weights_fingerprint": "weight filenames, sizes and mtime_ns; weight contents are not hashed",
}


@dataclass(frozen=True)
class PPLConfig:
    model_path: str | Path = DEFAULT_MODEL
    device: str = "cuda"
    dtype: str = "bfloat16"
    generation_tokenizer: str | Path | None = None
    max_length: int | None = None
    overflow: str = "error"

    def validate(self) -> None:
        if self.dtype not in {"float32", "float16", "bfloat16"}:
            raise ValueError("PPL dtype must be float32, float16 or bfloat16")
        if not self.device or self.overflow not in {"error", "truncate_prompt"}:
            raise ValueError("PPL device must be set; overflow must be error or truncate_prompt")
        if self.max_length is not None and (not isinstance(self.max_length, int)
                                             or isinstance(self.max_length, bool) or self.max_length < 2):
            raise ValueError("PPL max_length must be at least 2")


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _asset_fingerprint(path: str | Path, *, weights: bool = False) -> dict[str, Any]:
    directory = Path(path).expanduser().resolve()
    if not directory.is_dir():
        raise FileNotFoundError(f"local PPL model/tokenizer directory not found: {directory}")
    assets = []
    weight_stats = []
    for file in sorted(directory.iterdir()):
        if not file.is_file():
            continue
        if file.suffix in {".safetensors", ".bin", ".pt"}:
            if weights:
                stat = file.stat()
                weight_stats.append({"name": file.name, "size": stat.st_size, "mtime_ns": stat.st_mtime_ns})
        elif file.suffix in {".json", ".model", ".txt", ".jinja", ".tiktoken", ".py"}:
            assets.append({"name": file.name, "size": file.stat().st_size, "sha256": _file_sha256(file)})
    if not assets:
        raise ValueError(f"no local model/tokenizer configuration assets found in {directory}")
    if weights and not (directory / "config.json").is_file():
        raise FileNotFoundError(f"PPL reference model requires config.json: {directory}")
    return {"path": str(directory), "assets": assets, "weight_stats": weight_stats,
            "weight_content_hashed": False}


def _configured_max_length(path: str | Path) -> int:
    with (Path(path) / "config.json").open(encoding="utf-8") as handle:
        config = json.load(handle)
    for key in ("max_position_embeddings", "n_positions", "n_ctx"):
        value = config.get(key)
        if isinstance(value, int) and not isinstance(value, bool) and value >= 2:
            return value
    raise ValueError("PPL reference config has no supported finite context length")


def _versions() -> dict[str, str | None]:
    result: dict[str, str | None] = {"python": platform.python_version()}
    for package in ("torch", "transformers", "tokenizers"):
        try:
            result[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            result[package] = None
    return result


def _load_tokenizer(path: str | Path) -> Any:
    from transformers import AutoTokenizer

    return AutoTokenizer.from_pretrained(str(path), local_files_only=True)


def restore_generation_prompt(row: dict[str, Any], tokenizer: Any = None) -> tuple[str, dict[str, Any]]:
    """Reproduce generate_compare_score / generate_wn_score prompt semantics."""
    prompt = row.get("prompt")
    if isinstance(prompt, str):
        return prompt, {"format": "saved_string", "source_prompt_truncated": False,
                        "source_limit_origin": "saved_string_already_rendered"}
    if not isinstance(prompt, list) or not prompt or tokenizer is None:
        raise ValueError("PPL prompt must be a string or nonempty message list with source tokenizer")
    if any(not isinstance(item, dict) or not isinstance(item.get("role"), str)
           or not isinstance(item.get("content"), str) for item in prompt):
        raise ValueError("PPL prompt messages require string role and content")
    text = tokenizer.apply_chat_template(prompt, add_generation_prompt=True, tokenize=False)
    if not isinstance(text, str):
        raise ValueError("source tokenizer chat template did not return text")
    ids = list(tokenizer.encode(text, add_special_tokens=False))
    generation = row.get("generation") or {}
    if not isinstance(generation, dict):
        raise ValueError("generation metadata must be an object")
    limit = generation.get("max_prompt_tokens", LEGACY_MAX_PROMPT_TOKENS)
    if not isinstance(limit, int) or isinstance(limit, bool) or limit <= 0:
        raise ValueError("generation.max_prompt_tokens must be a positive integer")
    no_truncation = generation.get("prompt_truncated") is False
    if no_truncation and len(ids) > limit:
        raise ValueError(f"saved generation says prompt_truncated=False but prompt has {len(ids)} tokens > {limit}")
    actual_truncated = not no_truncation and len(ids) > limit
    if actual_truncated:
        text = tokenizer.decode(ids[:limit], skip_special_tokens=False)
    if no_truncation and "prompt_tokens" in generation and generation["prompt_tokens"] != len(ids):
        raise ValueError("reconstructed source prompt length differs from generation.prompt_tokens; check source tokenizer")
    return text, {"format": "source_chat_template", "source_prompt_tokens_full": len(ids),
                  "source_prompt_tokens_used": min(len(ids), limit) if actual_truncated else len(ids),
                  "source_max_prompt_tokens": limit, "source_prompt_truncated": actual_truncated,
                  "source_limit_origin": "generation_metadata" if "max_prompt_tokens" in generation else "legacy_default_2048"}


def prepare_sample(prompt: str, answer: str, tokenizer: Any, max_length: int,
                   overflow: str = "error") -> tuple[list[int], int, dict[str, Any]]:
    """Encode with a stable split boundary and one optional initial BOS."""
    prompt_ids = list(tokenizer.encode(prompt, add_special_tokens=False))
    answer_ids = list(tokenizer.encode(answer, add_special_tokens=False))
    bos = getattr(tokenizer, "bos_token_id", None)
    had_bos = bool(prompt_ids and bos is not None and prompt_ids[0] == bos)
    if had_bos:
        prompt_ids = prompt_ids[1:]
    prefix = [bos] if bos is not None else []
    full_prompt_count = len(prefix) + len(prompt_ids)
    if not answer_ids:
        return prefix + prompt_ids, full_prompt_count, {
            "answer_tokens": 0, "reference_prompt_tokens_full": full_prompt_count,
            "reference_prompt_tokens_used": full_prompt_count, "reference_prompt_tokens_removed": 0,
            "reference_bos_added": bos is not None and not had_bos}
    if not prefix and not prompt_ids:
        raise ValueError("cannot score the first answer token without a prompt token or reference BOS")
    available = max_length - len(answer_ids)
    minimum_context = len(prefix) + (1 if prompt_ids else 0)
    if available < max(minimum_context, 1):
        raise ValueError(f"answer has {len(answer_ids)} tokens and cannot fit context length {max_length} without dropping answer tokens")
    if full_prompt_count + len(answer_ids) > max_length:
        if overflow != "truncate_prompt":
            raise ValueError(f"reference prompt+answer has {full_prompt_count + len(answer_ids)} tokens > {max_length}; "
                             "use --ppl-overflow truncate_prompt to left-truncate only prompt context")
        prompt_ids = prompt_ids[-(available - len(prefix)):]
    context = prefix + prompt_ids
    return context + answer_ids, len(context), {
        "answer_tokens": len(answer_ids), "reference_prompt_tokens_full": full_prompt_count,
        "reference_prompt_tokens_used": len(context),
        "reference_prompt_tokens_removed": full_prompt_count - len(context),
        "reference_bos_added": bos is not None and not had_bos}


class _TransformersBackend:
    def __init__(self, config: PPLConfig):
        import torch
        from transformers import AutoModelForCausalLM

        self.torch = torch
        self.tokenizer = _load_tokenizer(config.model_path)
        self.max_length = _configured_max_length(config.model_path)
        self.device = config.device
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        print(f"[PPL] Loading fixed reference LM: {config.model_path} ({config.device}, {config.dtype})", file=sys.stderr, flush=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            str(config.model_path), local_files_only=True, torch_dtype=getattr(torch, config.dtype)
        ).to(config.device)
        self.model.eval()
        actual_limit = getattr(self.model.config, "max_position_embeddings", None)
        if isinstance(actual_limit, int) and actual_limit >= 2:
            self.max_length = min(self.max_length, actual_limit)

    def score(self, token_ids: list[int], answer_start: int) -> float:
        torch = self.torch
        inputs = torch.tensor([token_ids], dtype=torch.long, device=self.device)
        with torch.inference_mode():
            output = self.model(input_ids=inputs, use_cache=False, return_dict=True)
            # The answer's first token is predicted by the final prompt token.
            # Convert only small CE slices to float32, never the full logits.
            losses = []
            for start in range(answer_start, len(token_ids), 128):
                stop = min(start + 128, len(token_ids))
                loss = torch.nn.functional.cross_entropy(
                    output.logits[0, start - 1:stop - 1].float(), inputs[0, start:stop], reduction="sum")
                losses.append(float(loss.item()))
        return math.fsum(losses)


def _load_backend(config: PPLConfig) -> Any:
    return _TransformersBackend(config)


class _Progress:
    def __init__(self, label: str, total: int):
        self.label, self.total = label, total
        self.stream = sys.stderr
        self.tty = self.stream.isatty()
        self.started = self.last_report = time.monotonic()
        self.update(0, force=True)

    def update(self, done: int, *, force: bool = False) -> None:
        now = time.monotonic()
        if not force and done != self.total and now - self.last_report < (0.5 if self.tty else 5.0):
            return
        elapsed = max(now - self.started, 0.001)
        rate = done / elapsed
        eta = f"{(self.total - done) / rate:.0f}s" if rate else "--"
        filled = int(20 * done / max(self.total, 1))
        line = (f"[PPL {self.label}] |{'#' * filled}{'-' * (20 - filled)}| "
                f"{done}/{self.total} {100 * done / max(self.total, 1):.1f}% {rate:.2f} samples/s ETA {eta}")
        self.stream.write(("\r" if self.tty else "") + line + ("\n" if not self.tty or done == self.total else ""))
        self.stream.flush()
        self.last_report = now


def _read_source(path: Path) -> list[tuple[int, dict[str, Any], str]]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict) or not isinstance(row.get("answer"), str):
                raise ValueError(f"{path}:{line_number}: JSON object with string answer required (use main generation JSONL)")
            if "id" not in row or not isinstance(row.get("prompt"), (str, list)):
                raise ValueError(f"{path}:{line_number}: id and saved prompt required")
            rows.append((line_number, row, _digest(row)))
    if not rows:
        raise ValueError(f"PPL input contains no records: {path}")
    return rows


def _summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    finite = [row for row in records if row["status"] in {"ok", "ppl_overflow"}]
    try:
        nll = math.fsum(row["nll_sum"] for row in finite)
    except OverflowError:
        nll = None
    tokens = sum(row["scored_tokens"] for row in finite)
    mean_nll = nll / tokens if tokens and nll is not None else None
    ppl = math.exp(mean_nll) if mean_nll is not None and mean_nll <= math.log(sys.float_info.max) else None
    nonfinite = sum(row["status"] == "nonfinite_loss" for row in records)
    empty = sum(row["status"] == "skipped_empty_answer" for row in records)
    status = ("partial_failure" if nonfinite else "no_scored_answers" if not tokens
              else "ppl_overflow" if ppl is None else "ok")
    generation_configs: dict[str, dict[str, Any]] = {}
    seeds = []
    for row in records:
        generation = row.get("generation") or {}
        # Record individual seeds in immutable sample records, summarize them
        # here so each history entry describes the actual generation protocol.
        seed = generation.get("seed")
        if isinstance(seed, int) and not isinstance(seed, bool):
            seeds.append(seed)
        common = {key: value for key, value in generation.items()
                  if key not in {"seed", "prompt_tokens", "finish_reason"}}
        key = _canonical(common)
        if key not in generation_configs:
            generation_configs[key] = {"configuration": common, "samples": 0}
        generation_configs[key]["samples"] += 1
    return {"samples": len(records), "valid_samples": len(finite),
            "skipped_empty_answers": empty, "complete": nonfinite == 0 and empty == 0,
            "nonfinite_samples": nonfinite, "status": status, "total_nll": nll,
            "scored_tokens": tokens, "mean_nll": mean_nll, "token_weighted_ppl": ppl,
            "mean_answer_tokens": sum(row["answer_tokens"] for row in records) / len(records) if records else None,
            "source_prompt_truncated_samples": sum(bool(row["source_prompt_truncated"]) for row in records),
            "reference_prompt_truncated_samples": sum(row["reference_prompt_tokens_removed"] > 0 for row in records),
            "generation_configurations": list(generation_configs.values()),
            "generation_seeds": {"recorded_samples": len(seeds), "minimum": min(seeds) if seeds else None,
                                 "maximum": max(seeds) if seeds else None,
                                 "individual_values": "see per-sample immutable records"},
            "student_model_paths": sorted({row["model_path"] for row in records if isinstance(row.get("model_path"), str)}),
            "generation_tokenizer_paths": sorted({row["generation_tokenizer"] for row in records if row.get("generation_tokenizer")})}


def _median_ppl(records: list[dict[str, Any]]) -> dict[str, Any]:
    # Keep overflowing answers in the ordering. For an even sample, average
    # the middle PPLs, using log-mean-exp only if a middle PPL overflowed.
    values = sorted((row for row in records if row["status"] in {"ok", "ppl_overflow"}),
                    key=lambda row: row["nll_sum"] / row["scored_tokens"])
    value = None
    if values:
        middle = len(values) // 2
        upper = values[middle]
        value = upper["ppl"]
        if len(values) % 2 == 0:
            lower = values[middle - 1]
            if lower["ppl"] is not None and upper["ppl"] is not None:
                value = lower["ppl"] / 2 + upper["ppl"] / 2
            else:
                lower_log = lower["nll_sum"] / lower["scored_tokens"]
                upper_log = upper["nll_sum"] / upper["scored_tokens"]
                median_log = upper_log + math.log1p(math.exp(lower_log - upper_log)) - math.log(2)
                value = math.exp(median_log) if median_log <= math.log(sys.float_info.max) else None
    finite = value is not None and math.isfinite(value)
    return {"median_per_answer_ppl": value if finite else None,
            "median_samples": len(values),
            "median_status": "ok" if finite else "ppl_overflow" if values else "no_scored_answers"}


def summarize_ppl_quality(
    records: list[dict[str, Any]], source_sha256: str,
    repetition_filter: dict[str, Any] | None = None, filter_file: str | Path | None = None,
) -> dict[str, Any]:
    """Derive quality statistics without changing the immutable v1 LM cache.

    Reuse the watermark evaluator's teacher-tokenizer repetition decisions, but
    aggregate reference-LM NLL and reference-token counts for the retained IDs.
    """
    result = {**_median_ppl(records), "without_severe_repetition": None}
    if repetition_filter is None:
        return result
    try:
        signature = repetition_filter["signature"]
        filtering = repetition_filter["filtering"]
        if signature["source_sha256"] != source_sha256:
            raise ValueError("source SHA256 does not match PPL input")
        if (signature["severe_repetition_threshold"] != 0.5
                or filtering["repetition_threshold"] != 0.5 or filtering["comparison"] != ">"
                or filtering["scope"] != "answer-internal adjacent token pairs; prompt excluded"):
            raise ValueError("expected answer-internal adjacent-pair repetition > 0.5")
        ids = [row["id"] for row in records]
        if len(set(ids)) != len(ids):
            raise ValueError("duplicate PPL answer IDs")
        decisions = {}
        for item in filtering["per_answer"]:
            sample_id, excluded, ratio = item["id"], item["excluded"], item["repetition_ratio"]
            if (sample_id in decisions or not isinstance(excluded, bool)
                    or not isinstance(ratio, (int, float)) or isinstance(ratio, bool)
                    or not math.isfinite(ratio) or not 0 <= ratio <= 1 or excluded != (ratio > 0.5)):
                raise ValueError("invalid or duplicate repetition decision")
            decisions[sample_id] = excluded
        if set(decisions) != set(ids):
            raise ValueError("repetition answer IDs do not match PPL answer IDs")
        removed = [sample_id for sample_id in ids if decisions[sample_id]]
        declared_removed = filtering["removed_answer_ids"]
        retained = [row for row in records if not decisions[row["id"]]]
        if (len(declared_removed) != len(set(declared_removed)) or set(declared_removed) != set(removed)
                or filtering["num_answers_before"] != len(records)
                or filtering["num_answers_retained"] != len(retained)
                or filtering["num_answers_removed"] != len(removed)
                or filtering["fraction_answers_removed"] != (len(removed) / len(records) if records else 0.0)):
            raise ValueError("repetition counts or removed answer IDs do not match decisions")
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError(f"invalid PPL repetition filter {filter_file or '<payload>'}: {error}") from error
    result["without_severe_repetition"] = {
        **_summarize(retained), **_median_ppl(retained),
        "num_answers_before": len(records), "num_answers_retained": len(retained),
        "num_answers_removed": len(removed),
        "fraction_answers_removed": len(removed) / len(records) if records else 0.0,
        "repetition_threshold": 0.5, "comparison": ">", "scope": filtering["scope"],
        "removed_answer_ids": removed, "filtering_source_file": str(filter_file) if filter_file else None,
        "filtering_source_sha256": source_sha256, "filtering_tokenizer": signature.get("tokenizer"),
    }
    return result


def _read_cache(path: Path, metadata: dict[str, Any], source_rows: list[tuple[int, dict[str, Any], str]]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    try:
        with path.open(encoding="utf-8") as handle:
            objects = [json.loads(line) for line in handle if line.strip()]
        if len(objects) != len(source_rows) + 2 or objects[0] != {"type": "metadata", **metadata}:
            raise ValueError("metadata or record count mismatch")
        records = objects[1:-1]
        for record, (line_number, row, row_hash) in zip(records, source_rows, strict=True):
            if not isinstance(record, dict):
                raise ValueError("sample record must be an object")
            if (record.get("type") != "sample" or record.get("id") != row["id"]
                    or record.get("source_line") != line_number or record.get("source_row_sha256") != row_hash):
                raise ValueError("record order/identity mismatch")
            if record.get("status") not in {"ok", "ppl_overflow", "nonfinite_loss", "skipped_empty_answer"}:
                raise ValueError("unknown sample status")
            for key in ("answer_tokens", "scored_tokens", "reference_prompt_tokens_removed"):
                if not isinstance(record.get(key), int) or isinstance(record[key], bool) or record[key] < 0:
                    raise ValueError(f"invalid sample {key}")
            if record["status"] in {"ok", "ppl_overflow"}:
                if record["scored_tokens"] != record["answer_tokens"] or record["scored_tokens"] == 0:
                    raise ValueError("scored answer token count mismatch")
                if not isinstance(record.get("nll_sum"), (int, float)) or not math.isfinite(record["nll_sum"]) or record["nll_sum"] < 0:
                    raise ValueError("invalid finite sample loss")
                expected_ppl = (None if record["nll_sum"] / record["scored_tokens"] > math.log(sys.float_info.max)
                                else math.exp(record["nll_sum"] / record["scored_tokens"]))
                if record.get("ppl") != expected_ppl:
                    raise ValueError("sample PPL does not match loss/token count")
            elif record["scored_tokens"] != 0 or record.get("nll_sum") is not None or record.get("ppl") is not None:
                raise ValueError("unscored sample contains a numeric score")
        summary = _summarize(records)
        if objects[-1] != {"type": "summary", "records_sha256": _digest(records), **summary}:
            raise ValueError("record integrity or summary mismatch")
        return summary, records
    except (ValueError, KeyError, TypeError, OverflowError) as error:
        raise ValueError(f"invalid PPL cache {path}: {error}; remove the invalid file explicitly before recomputing") from error


def _write_cache(path: Path, metadata: dict[str, Any], records: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=path.name + ".", suffix=".tmp", delete=False) as handle:
            temporary = Path(handle.name)
            for obj in [{"type": "metadata", **metadata}, *records,
                        {"type": "summary", "records_sha256": _digest(records), **summary}]:
                handle.write(_canonical(obj) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def evaluate_ppl_files(
    paths: dict[str, Path], config: PPLConfig, *,
    repetition_filters: dict[str, dict[str, Any]] | None = None,
    repetition_filter_files: dict[str, str | Path] | None = None,
) -> dict[str, Any]:
    """Score each file once; content-addressed complete caches avoid reloading LM."""
    config.validate()
    if repetition_filters is not None and set(repetition_filters) != set(paths):
        raise ValueError("PPL repetition filters must cover exactly the evaluated file groups")
    model_path = Path(config.model_path).expanduser().resolve()
    config = PPLConfig(model_path=model_path, device=config.device, dtype=config.dtype,
                       generation_tokenizer=config.generation_tokenizer,
                       max_length=config.max_length, overflow=config.overflow)
    maximum = _configured_max_length(model_path)
    if config.max_length is not None and config.max_length > maximum:
        raise ValueError(f"PPL max_length {config.max_length} exceeds reference config limit {maximum}")
    maximum = config.max_length or maximum
    configuration = {**asdict(config), "model_path": str(model_path),
                     "generation_tokenizer": str(Path(config.generation_tokenizer).expanduser().resolve()) if config.generation_tokenizer else None,
                     "effective_max_length": maximum, "protocol": PROTOCOL,
                     "reference_assets": _asset_fingerprint(model_path, weights=True), "software": _versions()}
    files: dict[str, Any] = {}
    backend = None
    tokenizers: dict[str, Any] = {}
    try:
        for label, supplied_path in paths.items():
            path = Path(supplied_path).expanduser().resolve()
            source_hash = _file_sha256(path)
            source_rows = _read_source(path)
            tokenizer_assets: dict[str, Any] = {}
            tokenizer_for_row: dict[int, str] = {}
            for line_number, row, _ in source_rows:
                if isinstance(row["prompt"], list):
                    selected = config.generation_tokenizer or row.get("model_path")
                    if not selected:
                        raise ValueError(f"{path}:{line_number}: source generation tokenizer required; use --ppl-generation-tokenizer")
                    tokenizer_path = str(Path(selected).expanduser().resolve())
                    tokenizer_for_row[line_number] = tokenizer_path
                    if tokenizer_path not in tokenizer_assets:
                        tokenizer_assets[tokenizer_path] = _asset_fingerprint(tokenizer_path)
            metadata = {"schema": SCHEMA, "source_path": str(path), "source_sha256": source_hash,
                        "configuration": configuration, "generation_tokenizer_assets": tokenizer_assets}
            cache_path = path.with_name(f"{path.stem}.ppl.{_digest(metadata)[:20]}.jsonl")
            if cache_path.exists():
                summary, records = _read_cache(cache_path, metadata, source_rows)
                quality = summarize_ppl_quality(
                    records, source_hash,
                    repetition_filters[label] if repetition_filters is not None else None,
                    (repetition_filter_files or {}).get(label),
                )
                print(f"[PPL {label}] {len(source_rows)}/{len(source_rows)} cache reused: {cache_path}", file=sys.stderr, flush=True)
                files[label] = {**summary, **quality, "source_path": str(path), "source_sha256": source_hash,
                                "per_sample_file": str(cache_path), "cache_reused": True}
                continue
            if backend is None:
                backend = _load_backend(config)
                if maximum > backend.max_length:
                    raise ValueError(f"PPL configured context {maximum} exceeds loaded model context {backend.max_length}")
            for selected in tokenizer_assets:
                if selected not in tokenizers:
                    print(f"[PPL] Loading source prompt tokenizer only: {selected}", file=sys.stderr, flush=True)
                    tokenizers[selected] = _load_tokenizer(selected)
            records = []
            progress = _Progress(label, len(source_rows))
            for index, (line_number, row, row_hash) in enumerate(source_rows):
                selected = tokenizer_for_row.get(line_number)
                try:
                    prompt, source_meta = restore_generation_prompt(row, tokenizers.get(selected))
                    ids, answer_start, reference_meta = prepare_sample(
                        prompt, row["answer"], backend.tokenizer, maximum, config.overflow)
                except ValueError as error:
                    raise ValueError(f"{path}:{line_number} id={row['id']!r}: {error}") from error
                record = {"type": "sample", "id": row["id"], "source_path": str(path),
                          "source_sha256": source_hash, "source_line": line_number, "source_row_sha256": row_hash,
                          "model_path": row.get("model_path"), "model_label": row.get("model_label"),
                          "generation": row.get("generation"), "attack": row.get("attack"),
                          "generation_tokenizer": selected,
                          "generation_tokenizer_selection": ("saved_string" if selected is None else
                                                              "explicit_override" if config.generation_tokenizer else "model_path_assumption"),
                          "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
                          "answer_sha256": hashlib.sha256(row["answer"].encode("utf-8")).hexdigest(),
                          **source_meta, **reference_meta, "source_prompt_truncated": source_meta.get("source_prompt_truncated", False),
                          "scored_tokens": 0, "nll_sum": None, "ppl": None}
                if reference_meta["answer_tokens"] == 0:
                    record["status"] = "skipped_empty_answer"
                else:
                    nll = float(backend.score(ids, answer_start))
                    if not math.isfinite(nll) or nll < 0:
                        record["status"] = "nonfinite_loss"
                    else:
                        mean_nll = nll / reference_meta["answer_tokens"]
                        overflowed = mean_nll > math.log(sys.float_info.max)
                        record.update(status="ppl_overflow" if overflowed else "ok", nll_sum=nll,
                                      scored_tokens=reference_meta["answer_tokens"],
                                      ppl=None if overflowed else math.exp(mean_nll))
                records.append(record)
                progress.update(index + 1)
            if _file_sha256(path) != source_hash:
                raise RuntimeError(f"PPL input changed during scoring: {path}; no cache was published")
            summary = _summarize(records)
            _write_cache(cache_path, metadata, records, summary)
            quality = summarize_ppl_quality(
                records, source_hash,
                repetition_filters[label] if repetition_filters is not None else None,
                (repetition_filter_files or {}).get(label),
            )
            files[label] = {**summary, **quality, "source_path": str(path), "source_sha256": source_hash,
                            "per_sample_file": str(cache_path), "cache_reused": False}
    finally:
        if backend is not None:
            del backend
            gc.collect()
            if "torch" in sys.modules and sys.modules["torch"].cuda.is_available():
                sys.modules["torch"].cuda.empty_cache()
    return {"enabled": True, "schema": SCHEMA, "configuration": configuration, "files": files}


def write_ppl_summary(handle: TextIO, result: dict[str, Any]) -> None:
    if not result.get("enabled"):
        return
    handle.write("\n### 固定参考模型 PPL（只评分已保存的回答）\n\n")
    handle.write("| 文件组 | 总体 PPL ↓ | 逐回答 PPL 中位数 ↓ | 剔除严重重复后总体 PPL ↓ | 保留回答数/原回答数 | 有效样本/总样本 | 状态 | 缓存复用 |\n")
    handle.write("|---|---:|---:|---:|---:|---:|---|---|\n")

    def format_ppl(value: float | None) -> str:
        return f"{value:.6f}" if value is not None else "null"

    for label, summary in result["files"].items():
        filtered = summary["without_severe_repetition"]
        filtered_ppl = format_ppl(filtered["token_weighted_ppl"]) if filtered is not None else "N/A"
        retained = f"{filtered['num_answers_retained']}/{filtered['num_answers_before']}" if filtered is not None else "N/A"
        handle.write(f"| {label} | {format_ppl(summary['token_weighted_ppl'])}"
                     f" | {format_ppl(summary['median_per_answer_ppl'])} | {filtered_ppl} | {retained}"
                     f" | {summary['valid_samples']}/{summary['samples']} | {summary['status']} | {summary['cache_reused']} |\n")
    handle.write("\n总体 PPL = exp(全部有效回答 NLL 总和 / 全部计分回答 token 数)，不是逐条 PPL 的算术平均。\n")
    handle.write("逐回答 PPL 中位数对全量有效回答的 PPL 排序；偶数条取中间两个 PPL 的算术平均，"
                 "不对平均 NLL 取中位数后再 exp。空回答或异常 loss 不计入，并单独报告数量。\n")
    handle.write("剔除严重重复后总体 PPL：复用同源重复筛选缓存，按教师 tokenizer 的回答内部相邻 token 对重复率"
                 "严格 > 50% 剔除整条回答，prompt 不参与判断；只汇总保留回答原有的参考模型 NLL 和参考 tokenizer token 数。"
                 "保留回答的文本不变，不删除文内 token，不丢弃尾部。KGW 与 clean 各自筛选，保留回答数含未成功评分回答。"
                 "N/A 表示未提供筛选，null 表示无可计算数值；筛选后结果是子集统计，全量结果另行保留。\n")
    handle.write("原生成 tokenizer 恢复实际生成 prompt；参考 tokenizer 对 prompt/answer 分开编码后拼接；只计回答，包含首回答 token。"
                 "Base 参考模型不再套用 chat template；只添加一次参考 BOS，不额外评分 EOS；输入 JSONL 不修改。\n\n")
    if result["configuration"]["generation_tokenizer"] is None:
        handle.write("未显式指定原生成 tokenizer 时，消息列表按每条记录的 model_path 推定。"
                     "旧生成脚本可能让 student/base 共用 student tokenizer；需确认模板一致，"
                     "否则使用 --ppl-generation-tokenizer 指定实际生成 tokenizer。\n\n")
    for label, summary in result["files"].items():
        handle.write(f"- {label}: `{summary['source_path']}`；SHA256 `{summary['source_sha256']}`；"
                     f"逐条明细 `{summary['per_sample_file']}`；空回答 {summary['skipped_empty_answers']}；"
                     f"异常 loss {summary['nonfinite_samples']}；原生成截断 {summary['source_prompt_truncated_samples']}；"
                     f"参考上下文截断 {summary['reference_prompt_truncated_samples']}；计分回答 tokens {summary['scored_tokens']}；"
                     f"平均回答 tokens {summary['mean_answer_tokens']:.2f}；中位数样本数 {summary['median_samples']}"
                     f"（状态 {summary['median_status']}）。\n")
        if not summary["complete"]:
            handle.write(f"  **{label} 的评测不完整：总体值只覆盖有效回答，不能作为全量样本 PPL。**\n")
        filtered = summary["without_severe_repetition"]
        if filtered is not None:
            handle.write(f"  剔除严重重复回答 {filtered['num_answers_removed']}（{filtered['fraction_answers_removed']:.2%}）；"
                         f"保留回答中有效评分 {filtered['valid_samples']}/{filtered['samples']}；"
                         f"保留回答计分 tokens {filtered['scored_tokens']}；状态 {filtered['status']}；"
                         f"重复筛选缓存 `{filtered['filtering_source_file']}`。\n")
            if not filtered["complete"]:
                handle.write(f"  **{label} 的筛选后评测不完整：筛选后 PPL 仅覆盖成功评分的保留回答。**\n")
        handle.write("\n  生成文本配置（种子逐条保存在明细中）：\n\n```json\n")
        handle.write(json.dumps({"student_model_paths": summary["student_model_paths"],
                                 "generation_tokenizer_paths": summary["generation_tokenizer_paths"],
                                 "generation_configurations": summary["generation_configurations"],
                                 "generation_seeds": summary["generation_seeds"]}, ensure_ascii=False, indent=2, allow_nan=False))
        handle.write("\n```\n")
    handle.write("\n完整评分配置（含模型/tokenizer 指纹、软件版本；权重使用 size/mtime 标识，不全量哈希）：\n\n```json\n")
    handle.write(json.dumps(result["configuration"], ensure_ascii=False, indent=2, allow_nan=False))
    handle.write("\n```\n")
