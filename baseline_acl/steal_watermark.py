#!/usr/bin/env python3
"""Estimate ACL TP/WN watermark rules from an un-attacked student's training data.

O is the original student base, W is the student trained on the original
watermarked responses, and C is the ORIGINAL train.parquet. This program uses
only C.teacher_response, no KGW key, green list, or detector. For each short
prefix it averages next-token probabilities over answer-only contexts BEFORE
computing the W/O ratio. The resulting JSON is consumed by inverse_watermark.

--preflight reads local tokenizers and parquet on CPU; it never loads weights,
imports torch, probes CUDA, downloads assets, or writes output. Execution loads
W and O sequentially on one explicitly selected device. The global rule uses
all effective positions in the first 200 tokens and the complete tokenizer
vocabulary. Conditional rules use W's top-k averaged probabilities and at most
1000 contexts per prefix, selected by shuffle-then-truncate without a fixed
sampling seed. No training is performed.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict, dataclass
import gc
import hashlib
from importlib import metadata
import inspect
import json
import math
import os
from pathlib import Path
import random
import re
import shutil
import sys
import tempfile
import time
from typing import Callable, Iterable, Mapping, Sequence


RULE_FORMAT = "acl-watermark-rules"
RULE_VERSION = 1
OFFICIAL_SOURCE = "https://github.com/THU-BPM/Watermark-Radioactivity-Attack"
Prefix = tuple[int, ...]


@dataclass(frozen=True)
class EstimationConfig:
    max_ngram: int = 3
    freq_threshold: float = 5e-5
    alpha: float = 0.3
    top_k: int = 50
    max_contexts_per_prefix: int = 1000
    max_context_tokens: int = 200
    batch_size: int = 4

    def validate(self) -> None:
        if type(self.max_ngram) is not int or not 1 <= self.max_ngram <= 3:
            raise ValueError("max_ngram must be 1, 2, or 3 (prefix lengths 0, 1, 2)")
        for name in ("top_k", "max_contexts_per_prefix", "max_context_tokens", "batch_size"):
            value = getattr(self, name)
            if type(value) is not int or value < 1:
                raise ValueError(f"{name} must be a positive integer")
        if not math.isfinite(self.freq_threshold) or not 0 <= self.freq_threshold < 1:
            raise ValueError("freq_threshold must be finite and in [0, 1)")
        if not math.isfinite(self.alpha) or self.alpha < 0:
            raise ValueError("alpha must be finite and nonnegative")


@dataclass(frozen=True, slots=True)
class ContextRef:
    """Reference a row prefix rather than copying its potentially 200 token IDs."""
    row_index: int
    end: int


@dataclass
class ContextPlan:
    token_rows: list[list[int]]
    prefix_metadata: dict[Prefix, dict]
    contexts: dict[Prefix, list[ContextRef]]
    statistics: dict


class EstimationProgress:
    """Terminal progress bar, or newline records when piped to a log file."""

    def __init__(self, label: str, total: int, unit: str, synchronize: Callable | None = None, stream=None):
        self.label, self.total, self.unit = label, total, unit
        self.done = 0
        self.started = self.last_report = time.monotonic()
        self.first_report = True
        self.synchronize = synchronize
        self.stream = sys.stderr if stream is None else stream
        self.terminal = self.stream.isatty()
        self.line_width = 0
        self.detail = ""
        self.closed = False
        self._render(0)

    @staticmethod
    def _duration(seconds: float) -> str:
        hours, rest = divmod(int(max(seconds, 0)), 3600)
        minutes, seconds = divmod(rest, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def _render(self, elapsed: float) -> None:
        fraction = min(self.done / self.total, 1) if self.total else 1
        rate = self.done / elapsed if elapsed > 0 else 0
        eta = self._duration(max(self.total - self.done, 0) / rate) if rate else "--:--:--"
        head = f"[{self.label}] "
        tail = f" {100 * fraction:5.1f}% {self.done}/{self.total} [{self._duration(elapsed)} < ~{eta}]"
        columns = shutil.get_terminal_size(fallback=(80, 24)).columns if self.terminal else None
        bar_width = max(5, min(20, columns - len(head) - len(tail) - 3)) if columns else 20
        filled = int(bar_width * fraction)
        bar = "#" * filled + "-" * (bar_width - filled)
        line = head + "|" + bar + "|" + tail
        extras = f" {self.unit}, {rate:.1f}/s" + (f"; {self.detail}" if self.detail else "")
        if columns is None or len(line + extras) < columns:
            line += extras
        if columns:
            line = line[:max(columns - 1, 1)]
            self.line_width = min(self.line_width, max(columns - 1, 1))
        finished = self.done == self.total
        if self.terminal:
            self.stream.write("\r" + line.ljust(self.line_width) + ("\n" if finished else ""))
        else:
            self.stream.write(line + "\n")
        self.stream.flush()
        self.line_width = len(line)
        self.closed = finished

    def advance(self, count: int, detail: str = "") -> None:
        self.update_to(self.done + count, detail)

    def update_to(self, completed: int, detail: str = "") -> None:
        if completed == self.done:
            return
        if not self.done <= completed <= self.total:
            raise ValueError("progress count must be monotonic and within the stage total")
        self.done = completed
        if detail:
            self.detail = detail
        now = time.monotonic()
        if not (self.first_report or self.done == self.total or now - self.last_report >= 5):
            return
        # Synchronize only at render points so a queued CUDA batch is not
        # reported as completed; do not synchronize on every inference batch.
        if self.synchronize is not None:
            self.synchronize()
        now = time.monotonic()
        self._render(max(now - self.started, 1e-9))
        self.first_report = False
        self.last_report = now

    def close(self) -> None:
        if self.terminal and not self.closed:
            self.stream.write("\n")
            self.stream.flush()
        self.closed = True


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def prefix_key(prefix: Sequence[int]) -> str:
    return ",".join(str(token_id) for token_id in prefix)


def validate_training_path(path: Path) -> None:
    """Require an explicitly named training parquet and reject test/dev names."""
    words = re.split(r"[^a-z0-9]+", path.stem.lower())
    # Both names are used by the project's original watermarked training sets.
    if path.suffix.lower() != ".parquet" or not {"train", "newtrain"}.intersection(words):
        raise ValueError("--input must be an explicitly named *_train.parquet or *_newtrain.parquet training dataset")
    if any(word in {"test", "validation", "valid", "val", "dev", "eval"} for word in words):
        raise ValueError("rule extraction cannot use a test/validation/evaluation dataset")


def validate_responses(responses: Sequence[object]) -> list[str]:
    if not responses:
        raise ValueError("source training parquet is empty")
    result = []
    for index, response in enumerate(responses):
        if not isinstance(response, str) or not response.strip():
            raise ValueError(f"teacher_response is empty/null/non-string at row {index}")
        result.append(response)
    return result


def read_training_responses(path: Path) -> tuple[list[str], dict]:
    validate_training_path(path)
    import pyarrow as pa
    import pyarrow.parquet as pq

    parquet = pq.ParquetFile(path)
    schema = parquet.schema_arrow
    if "teacher_response" not in schema.names:
        raise ValueError("training parquet must contain teacher_response")
    response_type = schema.field("teacher_response").type
    if not (pa.types.is_string(response_type) or pa.types.is_large_string(response_type)):
        raise ValueError("teacher_response must be an Arrow string column")
    # Load only responses: prompts, test data and watermark detector state never
    # enter the estimation pipeline. Other columns may exist in the source.
    responses = validate_responses(parquet.read(columns=["teacher_response"])["teacher_response"].to_pylist())
    info = {"path": str(path.resolve()), "sha256": file_sha256(path), "rows": len(responses),
            "column": "teacher_response", "split": "train", "columns": schema.names,
            "schema_sha256": hashlib.sha256(schema.serialize().to_pybytes()).hexdigest()}
    return responses, info


def require_same_tokenizers(before: Mapping, after: Mapping) -> None:
    try:
        from baseline_acl.inverse_watermark import tokenizer_identities_match, tokenizer_mismatch_details
    except ModuleNotFoundError:  # direct `python baseline_acl/steal_watermark.py`
        from inverse_watermark import tokenizer_identities_match, tokenizer_mismatch_details
    if not tokenizer_identities_match(before, after):
        raise ValueError("O and W must have identical tokenizer behavior, vocabulary IDs and special tokens; "
                         + tokenizer_mismatch_details(before, after))


def load_local_tokenizers(before_path: Path, after_path: Path):
    for path in (before_path, after_path):
        if not path.is_dir():
            raise FileNotFoundError(f"local tokenizer directory does not exist: {path}")
    from transformers import AutoTokenizer
    try:
        from baseline_acl.inverse_watermark import tokenizer_identity
    except ModuleNotFoundError:  # direct `python baseline_acl/steal_watermark.py`
        from inverse_watermark import tokenizer_identity

    before = AutoTokenizer.from_pretrained(str(before_path), local_files_only=True, trust_remote_code=False)
    after = AutoTokenizer.from_pretrained(str(after_path), local_files_only=True, trust_remote_code=False)
    before_identity = tokenizer_identity(before)
    after_identity = tokenizer_identity(after)
    require_same_tokenizers(before_identity, after_identity)
    return before, before_identity, after_identity


def tokenize_responses(responses: Sequence[str], tokenizer) -> list[list[int]]:
    rows = []
    vocab_size = len(tokenizer)
    for index, response in enumerate(responses):
        ids = list(tokenizer.encode(response, add_special_tokens=False))
        if not ids:
            raise ValueError(f"teacher_response produces no tokens at row {index}")
        if any(type(token_id) is not int or not 0 <= token_id < vocab_size for token_id in ids):
            raise ValueError(f"tokenizer emitted an invalid vocabulary ID at row {index}")
        rows.append(ids)
    return rows


def frequency_weight(frequency: float, maximum_frequency: float, alpha: float) -> float:
    if not (math.isfinite(frequency) and math.isfinite(maximum_frequency) and
            0 < frequency <= maximum_frequency <= 1 and math.isfinite(alpha) and alpha >= 0):
        raise ValueError("invalid relative frequency or alpha")
    if alpha == 0 or frequency == maximum_frequency:
        return 1.0
    # If an order has exactly one observed prefix, maximum_frequency == 1 and
    # frequency == maximum_frequency. That case above avoids log(1)/log(1).
    if maximum_frequency == 1:
        raise ValueError("inconsistent frequencies: max=1 requires one observed prefix")
    return (math.log(frequency) / math.log(maximum_frequency)) ** (-alpha)


def count_prefixes(token_rows: Sequence[Sequence[int]], config: EstimationConfig) -> tuple[dict[Prefix, dict], dict]:
    config.validate()
    counts_by_order = {length: Counter() for length in range(1, config.max_ngram)}
    totals = {length: 0 for length in counts_by_order}
    for ids in token_rows:
        # The official frequency analysis excludes the final answer token,
        # which has no following observed token, before counting every order.
        frequency_ids = ids[:-1]
        for length, counts in counts_by_order.items():
            for end in range(length, len(frequency_ids) + 1):
                counts[tuple(frequency_ids[end - length:end])] += 1
                totals[length] += 1
    selected = {}
    order_info = {}
    for length, counts in counts_by_order.items():
        total = totals[length]
        maximum = max(counts.values()) / total if total else 0.0
        for prefix, count in sorted(counts.items()):
            frequency = count / total
            # Strict greater-than matches official prefix selection.
            if frequency > config.freq_threshold:
                selected[prefix] = {"count": count, "frequency": frequency,
                                    "weight": frequency_weight(frequency, maximum, config.alpha)}
        order_info[str(length)] = {"occurrences": total, "distinct_prefixes": len(counts),
                                  "selected_prefixes": sum(len(prefix) == length for prefix in selected),
                                  "max_relative_frequency": maximum}
    return selected, order_info


def build_context_plan(token_rows: list[list[int]], config: EstimationConfig) -> ContextPlan:
    if not token_rows or any(not ids for ids in token_rows):
        raise ValueError("token rows must contain nonempty answers")
    selected, order_info = count_prefixes(token_rows, config)
    contexts = {prefix: [] for prefix in selected}
    excluded_late = 0
    for row_index, ids in enumerate(token_rows):
        # Complete answer prefixes ending after the first 200 tokens are
        # excluded, as in calculate_d_n.py; later contexts are NOT tail-cropped.
        limit = min(len(ids), config.max_context_tokens)
        excluded_late += len(ids) - limit
        for end in range(1, limit + 1):
            ref = ContextRef(row_index, end)
            for length in range(1, min(config.max_ngram - 1, end) + 1):
                prefix = tuple(ids[end - length:end])
                if prefix in selected:
                    contexts[prefix].append(ref)
    missing = [prefix for prefix, refs in contexts.items() if not refs]
    for prefix in missing:
        del contexts[prefix]
    for prefix, refs in contexts.items():
        selected[prefix]["eligible_contexts"] = len(refs)
        # Match calculate_d_n.py: keep all contexts when at most the limit;
        # otherwise shuffle the complete collection and take the first 1000.
        # Do not seed or replace the process-global random generator here.
        if len(refs) > config.max_contexts_per_prefix:
            random.shuffle(refs)
            contexts[prefix] = refs[:config.max_contexts_per_prefix]
    global_positions = sum(min(len(ids), config.max_context_tokens) for ids in token_rows)
    statistics = {"answer_rows": len(token_rows), "answer_tokens": sum(map(len, token_rows)),
                  "frequency_scope": "responses_excluding_final_token_per_prefix_length", "orders": order_info,
                  "context_mode": "answer_only", "context_limit_mode": "exclude_positions_after_limit",
                  "empty_contexts_excluded": len(token_rows), "late_context_positions_excluded": excluded_late,
                  "selected_prefixes_without_context": [prefix_key(prefix) for prefix in missing[:20]],
                  "missing_prefix_examples_truncated": len(missing) > 20,
                  "selected_prefixes_without_context_count": len(missing),
                  "retained_contexts": sum(map(len, contexts.values())),
                  "eligible_contexts": sum(selected[p]["eligible_contexts"] for p in contexts),
                  "sampled_prefixes": sum(selected[p]["eligible_contexts"] > len(refs)
                                          for p, refs in contexts.items()),
                  "global_eligible_contexts": global_positions,
                  "global_retained_contexts": global_positions}
    return ContextPlan(token_rows, selected, contexts, statistics)


def score_probability_change(before: Mapping[int, float], after: Mapping[int, float],
                             *, include_zero: bool = False) -> dict[str, float]:
    result = {}
    for token_id, after_probability in after.items():
        if token_id not in before:
            raise ValueError(f"O probability missing for candidate token {token_id}")
        before_probability = before[token_id]
        for value in (before_probability, after_probability):
            if not math.isfinite(value) or not 0 <= value <= 1:
                raise ValueError("next-token probabilities must be finite and in [0, 1]")
        if after_probability > before_probability:
            # A numerically underflowed O probability with positive W reaches
            # the capped ratio. 0/0 never enters this branch.
            ratio = 2.0 if before_probability == 0 else min(2.0, after_probability / before_probability)
            result[str(token_id)] = 0.5 * ratio
        elif include_zero:
            result[str(token_id)] = 0.0
    return result


def mean_probabilities(probabilities: Iterable[Sequence[float]]) -> list[float]:
    """Small pure-Python reference used by tests/mocks; models use torch below."""
    total = None
    count = 0
    for row in probabilities:
        row = list(row)
        if not row or any(not math.isfinite(value) or not 0 <= value <= 1 for value in row):
            raise ValueError("invalid probability vector")
        if total is None:
            total = [0.0] * len(row)
        if len(row) != len(total):
            raise ValueError("probability vectors have different vocabularies")
        for index, value in enumerate(row):
            total[index] += value
        count += 1
    if not count:
        raise ValueError("cannot estimate a prefix with zero contexts")
    return [value / count for value in total]


def top_candidates(probabilities: Sequence[float], top_k: int) -> dict[int, float]:
    if top_k < 1 or not probabilities:
        raise ValueError("top_k and vocabulary size must be positive")
    if any(not math.isfinite(value) or not 0 <= value <= 1 for value in probabilities):
        raise ValueError("invalid averaged probabilities")
    indices = sorted(range(len(probabilities)), key=lambda index: (-probabilities[index], index))[:top_k]
    return {index: probabilities[index] for index in indices}


def model_asset_identity(path: Path, *, weights_required: bool = False, hash_weights: bool = False) -> dict:
    if not path.is_dir():
        raise FileNotFoundError(f"local model directory does not exist: {path}")
    files = []
    for asset in sorted(path.iterdir()):
        if not asset.is_file() or asset.suffix not in (".json", ".txt", ".model", ".bin", ".safetensors"):
            continue
        stat = asset.stat()
        entry = {"name": asset.name, "size": stat.st_size, "mtime_ns": stat.st_mtime_ns}
        if asset.suffix not in (".bin", ".safetensors") or hash_weights:
            entry["sha256"] = file_sha256(asset)
        files.append(entry)
    if weights_required:
        if not (path / "config.json").is_file() or not any(f["name"].endswith((".bin", ".safetensors")) for f in files):
            raise FileNotFoundError(f"local model config/weights are missing: {path}")
        for index_path in path.glob("*.index.json"):
            weight_map = json.loads(index_path.read_text(encoding="utf-8")).get("weight_map", {})
            for shard in set(weight_map.values()):
                shard_path = (path / shard).resolve()
                if not shard_path.is_relative_to(path.resolve()):
                    raise ValueError("model index contains a shard outside the selected model directory")
                if not shard_path.is_file():
                    raise FileNotFoundError(f"local weight shard is missing: {shard_path}")
    return {"path": str(path.resolve()), "files": files, "weights_fully_hashed": hash_weights,
            "identity_mode": "config_content_and_weight_manifest" if not hash_weights else "content_hash",
            "manifest_sha256": hashlib.sha256(canonical_json(files).encode("utf-8")).hexdigest()}


def resolve_device(device: str, gpu: str | None, *, preflight: bool = False) -> str:
    if preflight:
        return "cpu"
    if device == "cpu":
        if gpu is not None:
            raise ValueError("--gpu requires --device cuda")
        return "cpu"
    if device != "cuda":
        raise ValueError("device must be cpu or cuda")
    visible = os.environ.get("CUDA_VISIBLE_DEVICES")
    selection = gpu if gpu is not None else visible
    uuid = r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
    pattern = rf"(?:[0-9]+|GPU-{uuid}|MIG-{uuid}|MIG-GPU-{uuid}/[0-9]+/[0-9]+)"
    if not selection or not re.fullmatch(pattern, selection.strip()):
        raise ValueError("select exactly one GPU explicitly with --gpu or CUDA_VISIBLE_DEVICES")
    selection = selection.strip()
    if gpu is not None and visible and visible.strip() != selection:
        raise ValueError("--gpu conflicts with CUDA_VISIBLE_DEVICES; use one matching explicit GPU selection")
    os.environ["CUDA_VISIBLE_DEVICES"] = selection
    return "cuda:0"  # selected physical GPU only, never an implicit physical 0


class HFProbabilityEstimator:
    """One local resident model; computes means over the exact same contexts."""

    def __init__(self, model_path: Path, tokenizer, device: str, dtype: str):
        import torch
        from transformers import AutoModelForCausalLM

        self.torch = torch
        self.device = device
        self.vocab_size = len(tokenizer)
        if device.startswith("cuda"):
            if not torch.cuda.is_available() or torch.cuda.device_count() != 1:
                raise RuntimeError("CUDA must expose exactly the explicitly selected GPU")
            bf16 = torch.cuda.is_bf16_supported()
        else:
            bf16 = False
        self.dtype_name = ("bfloat16" if bf16 else "float32") if dtype == "auto" else dtype
        if self.dtype_name == "bfloat16" and device.startswith("cuda") and not bf16:
            raise ValueError("selected GPU does not support explicit bfloat16")
        self.model = AutoModelForCausalLM.from_pretrained(
            str(model_path), local_files_only=True, trust_remote_code=False,
            torch_dtype=getattr(torch, self.dtype_name),
        ).to(device).eval()
        self.pad_token_id = tokenizer.pad_token_id
        if self.pad_token_id is None:
            self.pad_token_id = tokenizer.eos_token_id
        if self.pad_token_id is None:
            self.pad_token_id = tokenizer.bos_token_id
        if self.pad_token_id is None:
            raise ValueError("a padding/EOS/BOS token is required to batch answer contexts")
        if self.model.get_input_embeddings().num_embeddings < self.vocab_size:
            raise ValueError("model embedding vocabulary is smaller than the selected tokenizer")
        self.logits_kwargs = {}
        signature = inspect.signature(self.model.forward)
        for parameter in ("logits_to_keep", "num_logits_to_keep"):
            if parameter in signature.parameters:
                self.logits_kwargs[parameter] = 1
                break

    def mean(self, contexts: Sequence[Sequence[int]], batch_size: int,
             candidate_ids: Sequence[int] | None = None, top_k: int = 50) -> dict[int, float]:
        if not contexts or any(not context for context in contexts):
            raise ValueError("estimation contexts must be nonempty")
        torch = self.torch
        ids_tensor = (None if candidate_ids is None else
                      torch.tensor(list(candidate_ids), dtype=torch.long, device=self.device))
        total = None
        progress = getattr(self, "context_progress", None)
        completed_before = progress.done if progress is not None else 0
        with torch.inference_mode():
            for start in range(0, len(contexts), batch_size):
                batch = contexts[start:start + batch_size]
                width = max(map(len, batch))
                input_ids = torch.tensor([[self.pad_token_id] * (width - len(c)) + list(c) for c in batch],
                                         dtype=torch.long, device=self.device)
                attention_mask = torch.tensor([[0] * (width - len(c)) + [1] * len(c) for c in batch],
                                              dtype=torch.long, device=self.device)
                positions = attention_mask.cumsum(dim=-1) - 1
                positions.masked_fill_(attention_mask == 0, 0)
                outputs = self.model(input_ids=input_ids, attention_mask=attention_mask,
                                     position_ids=positions, use_cache=False, **self.logits_kwargs)
                # Keep the COMPLETE model softmax denominator, including any
                # padded vocabulary slots above len(tokenizer), then select real
                # tokenizer IDs. Do not renormalize a top-k vector.
                probabilities = torch.softmax(outputs.logits[:, -1, :].float(), dim=-1)
                if probabilities.shape[-1] < self.vocab_size:
                    raise ValueError("model output vocabulary is smaller than the selected tokenizer")
                probabilities = (probabilities[:, :self.vocab_size] if ids_tensor is None else
                                 probabilities.index_select(1, ids_tensor))
                batch_sum = probabilities.double().sum(dim=0)
                total = batch_sum if total is None else total + batch_sum
                del outputs, probabilities, batch_sum
                if progress is not None:
                    progress.update_to(completed_before + start + len(batch))
            average = total / len(contexts)
            if not bool(torch.isfinite(average).all().item()):
                raise ValueError("model produced non-finite averaged probabilities")
            if candidate_ids is None:
                values, indices = torch.topk(average, min(top_k, self.vocab_size))
                return {int(i): float(v) for i, v in zip(indices.cpu().tolist(), values.cpu().tolist(), strict=True)}
            return {int(i): float(v) for i, v in zip(candidate_ids, average.cpu().tolist(), strict=True)}

    def mean_global(self, token_rows: Sequence[Sequence[int]], batch_size: int,
                    max_context_tokens: int) -> dict[int, float]:
        """Average every valid logit position, including the final input token.

        calculate_d_0.py averages all attention-mask-selected next-token
        distributions in each answer's first 200 input tokens. It does not
        shift labels or weight short answers equally with long answers. The
        full forward pass evaluates all these contexts together; padding is
        excluded, while model vocabulary padding stays in the softmax.
        """
        if not token_rows or any(not row for row in token_rows):
            raise ValueError("global estimation rows must be nonempty")
        if batch_size < 1 or max_context_tokens < 1:
            raise ValueError("batch size and context limit must be positive")
        torch = self.torch
        total = None
        position_count = 0
        progress = None
        if hasattr(self, "progress_label"):
            synchronize = (lambda: torch.cuda.synchronize(self.device)) if self.device.startswith("cuda") else None
            progress = EstimationProgress(f"{self.progress_label} global d0", len(token_rows), "answers", synchronize)
            self.global_progress = progress
        # Conditional estimation may request only the last logit. Explicitly
        # request all logits for architectures exposing that optimization.
        all_logits_kwargs = {name: 0 for name in self.logits_kwargs}
        with torch.inference_mode():
            for start in range(0, len(token_rows), batch_size):
                batch = [list(row[:max_context_tokens]) for row in token_rows[start:start + batch_size]]
                width = max(map(len, batch))
                input_ids = torch.tensor([[self.pad_token_id] * (width - len(row)) + row for row in batch],
                                         dtype=torch.long, device=self.device)
                attention_mask = torch.tensor([[0] * (width - len(row)) + [1] * len(row) for row in batch],
                                              dtype=torch.long, device=self.device)
                positions = attention_mask.cumsum(dim=-1) - 1
                positions.masked_fill_(attention_mask == 0, 0)
                outputs = self.model(input_ids=input_ids, attention_mask=attention_mask,
                                     position_ids=positions, use_cache=False, **all_logits_kwargs)
                if outputs.logits.shape[1] != width:
                    raise ValueError("global estimation requires logits for every input position")
                if outputs.logits.shape[-1] < self.vocab_size:
                    raise ValueError("model output vocabulary is smaller than the selected tokenizer")
                # Softmax one answer at a time to avoid retaining a full
                # float32 batch-by-position-by-vocabulary probability tensor.
                # dtype on sum accumulates in float64 without casting the
                # entire probability matrix to double.
                for row_index, row in enumerate(batch):
                    row_logits = outputs.logits[row_index, width - len(row):, :]
                    probabilities = torch.softmax(row_logits.float(), dim=-1)
                    row_sum = probabilities[:, :self.vocab_size].sum(dim=0, dtype=torch.float64)
                    total = row_sum if total is None else total + row_sum
                    position_count += len(row)
                    del row_logits, probabilities, row_sum
                del outputs
                if progress is not None:
                    progress.advance(len(batch), f"positions={position_count}")
            average = total / position_count
            if not bool(torch.isfinite(average).all().item()):
                raise ValueError("model produced non-finite global averaged probabilities")
            values = average.cpu().tolist()
            return {token_id: float(value) for token_id, value in enumerate(values)}

    def close(self) -> None:
        for name in ("global_progress", "context_progress"):
            progress = getattr(self, name, None)
            if progress is not None:
                progress.close()
        self.model = None
        gc.collect()
        if self.device.startswith("cuda"):
            self.torch.cuda.empty_cache()


def estimate_rule_document(plan: ContextPlan, config: EstimationConfig, tokenizer_identity: dict,
                           before_model: Path, after_model: Path, tokenizer, device: str, dtype: str,
                           provenance: dict, estimator_factory: Callable = HFProbabilityEstimator) -> dict:
    config.validate()
    after_means = {}
    print(f"[load W] start: pid={os.getpid()}, device={device}, dtype={dtype}, model={after_model}", flush=True)
    load_started = time.monotonic()
    estimator = estimator_factory(after_model, tokenizer, device, dtype)
    actual_dtype = getattr(estimator, "dtype_name", dtype)
    estimator.progress_label = "1/4 W"
    print(f"[load W] ready: dtype={actual_dtype}, elapsed={time.monotonic() - load_started:.1f}s", flush=True)
    try:
        after_global = estimator.mean_global(plan.token_rows, config.batch_size, config.max_context_tokens)
        synchronize = (lambda: estimator.torch.cuda.synchronize(device)) if device.startswith("cuda") else None
        progress = EstimationProgress("2/4 W conditional", sum(map(len, plan.contexts.values())), "contexts", synchronize)
        estimator.context_progress = progress
        completed_contexts = 0
        for index, (prefix, refs) in enumerate(plan.contexts.items()):
            progress.detail = f"current_prefix={index + 1}/{len(plan.contexts)}"
            contexts = [plan.token_rows[ref.row_index][:ref.end] for ref in refs]
            after_means[prefix] = estimator.mean(contexts, config.batch_size, top_k=config.top_k)
            completed_contexts += len(refs)
            progress.update_to(completed_contexts)
    finally:
        estimator.close()
    scores = {}
    print(f"[load O] start: pid={os.getpid()}, device={device}, dtype={actual_dtype}, model={before_model}", flush=True)
    load_started = time.monotonic()
    estimator = estimator_factory(before_model, tokenizer, device, actual_dtype)
    estimator.progress_label = "3/4 O"
    print(f"[load O] ready: elapsed={time.monotonic() - load_started:.1f}s", flush=True)
    try:
        before_global = estimator.mean_global(plan.token_rows, config.batch_size, config.max_context_tokens)
        global_scores = score_probability_change(before_global, after_global, include_zero=True)
        synchronize = (lambda: estimator.torch.cuda.synchronize(device)) if device.startswith("cuda") else None
        progress = EstimationProgress("4/4 O conditional", sum(map(len, plan.contexts.values())), "contexts", synchronize)
        estimator.context_progress = progress
        completed_contexts = 0
        for index, (prefix, refs) in enumerate(plan.contexts.items()):
            progress.detail = f"current_prefix={index + 1}/{len(plan.contexts)}"
            contexts = [plan.token_rows[ref.row_index][:ref.end] for ref in refs]
            before_mean = estimator.mean(contexts, config.batch_size, candidate_ids=list(after_means[prefix]))
            scores[prefix] = score_probability_change(before_mean, after_means[prefix])
            completed_contexts += len(refs)
            progress.update_to(completed_contexts)
    finally:
        estimator.close()
    prefix_scores = {}
    for prefix, metadata_ in plan.prefix_metadata.items():
        if prefix not in scores:
            continue
        prefix_scores[prefix_key(prefix)] = {**metadata_, "scores": scores[prefix],
                                            "sampled_contexts": len(plan.contexts[prefix])}
    return {"format": RULE_FORMAT, "version": RULE_VERSION, "tokenizer": tokenizer_identity,
            "parameters": {**asdict(config), "candidate_selection": "conditional_top_k_after_averaging_W",
                           "ratio_cap": 2.0, "score_scale": 0.5,
                           "dtype_requested": dtype, "dtype_actual": actual_dtype},
            "provenance": {**provenance, "model_loading_order": ["W", "O"],
                           "context_statistics": plan.statistics, "official_source": OFFICIAL_SOURCE,
                           "stealing_protocol": {"global_scope": "all_effective_positions",
                                                 "global_vocabulary": "full_tokenizer_vocabulary_including_zero_scores",
                                                 "conditional_sampling": "shuffle_then_truncate",
                                                 "prefix_frequency": "excludes_final_token"},
                           "adaptations": ["answer_only_train_parquet", "nonempty_contexts_only",
                                           "sequential_models_same_device"]},
            "global_scores": global_scores, "prefix_scores": prefix_scores}


def publish_rules(path: Path, document: dict) -> None:
    """Atomically publish a complete JSON without ever replacing an old run."""
    if path.exists():
        raise FileExistsError(f"rule output already exists; choose a new path: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n", prefix=f".{path.name}.",
                                         suffix=".tmp", dir=path.parent, delete=False) as handle:
            temporary = Path(handle.name)
            json.dump(document, handle, ensure_ascii=False, indent=2, allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        # Windows rename is atomic and fails if the destination exists. POSIX
        # rename would replace it, so use atomic no-replace hard-link creation
        # there. os.replace is never used.
        if os.name == "nt":
            os.rename(temporary, path)
        else:
            os.link(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def parse_args(argv: Sequence[str] | None = None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="ORIGINAL watermarked *_train.parquet or *_newtrain.parquet used to train W")
    parser.add_argument("--model-before", type=Path, required=True, help="local original student base O, before Warmup/GAD")
    parser.add_argument("--model-after", type=Path, required=True, help="local student W trained without UP/TP; for GAD use the merged HF actor")
    parser.add_argument("--tokenizer-before", type=Path, help="local O tokenizer (defaults to model-before)")
    parser.add_argument("--tokenizer-after", type=Path, help="local W tokenizer (defaults to model-after)")
    parser.add_argument("--output", type=Path, help="new JSON rule file; existing outputs are never overwritten")
    parser.add_argument("--preflight", action="store_true", help="CPU tokenizer/data checks only, no weights or writes")
    parser.add_argument("--max-ngram", type=int, default=3)
    parser.add_argument("--freq-threshold", type=float, default=5e-5)
    parser.add_argument("--alpha", type=float, default=0.3)
    parser.add_argument("--top-k", type=int, default=50)
    parser.add_argument("--max-contexts-per-prefix", type=int, default=1000)
    parser.add_argument("--max-context-tokens", type=int, default=200)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cpu")
    parser.add_argument("--gpu", help="one explicit physical GPU ID/UUID; must match CUDA_VISIBLE_DEVICES if set")
    parser.add_argument("--dtype", choices=("auto", "float32", "bfloat16", "float16"), default="auto")
    parser.add_argument("--hash-model-weights", action="store_true", help="also SHA256 large weight files in provenance")
    args = parser.parse_args(argv)
    if not args.preflight and args.output is None:
        parser.error("--output is required unless --preflight is used")
    args.tokenizer_before = args.tokenizer_before or args.model_before
    args.tokenizer_after = args.tokenizer_after or args.model_after
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    config = EstimationConfig(args.max_ngram, args.freq_threshold, args.alpha, args.top_k,
                              args.max_contexts_per_prefix, args.max_context_tokens, args.batch_size)
    config.validate()
    validate_training_path(args.input)
    if args.model_before.resolve() == args.model_after.resolve():
        raise ValueError("O and W must be different model directories")
    if args.output is not None and not args.preflight:
        if args.output.suffix.lower() != ".json":
            raise ValueError("--output must be a new .json rule file")
        if args.output.exists():
            raise FileExistsError(f"rule output already exists: {args.output}")
        protected = [args.input, args.model_before, args.model_after, args.tokenizer_before, args.tokenizer_after]
        output = args.output.resolve()
        if any(output == path.resolve() or (path.is_dir() and output.is_relative_to(path.resolve())) for path in protected):
            raise ValueError("rule output must not overwrite training data or lie inside a model/tokenizer directory")
    device = resolve_device(args.device, args.gpu, preflight=args.preflight)
    model_before_info = model_asset_identity(args.model_before, weights_required=not args.preflight,
                                            hash_weights=args.hash_model_weights and not args.preflight)
    model_after_info = model_asset_identity(args.model_after, weights_required=not args.preflight,
                                           hash_weights=args.hash_model_weights and not args.preflight)
    tokenizer, before_identity, after_identity = load_local_tokenizers(args.tokenizer_before, args.tokenizer_after)
    if config.top_k > len(tokenizer):
        raise ValueError("--top-k cannot exceed the rule tokenizer vocabulary size")
    responses, data_info = read_training_responses(args.input)
    plan = build_context_plan(tokenize_responses(responses, tokenizer), config)
    versions = {}
    for package in ("transformers", "torch", "pyarrow"):
        try:
            versions[package] = metadata.version(package)
        except metadata.PackageNotFoundError:
            versions[package] = "unavailable"
    report = {"preflight": args.preflight, "input": data_info, "tokenizer_O": before_identity,
              "tokenizer_W": after_identity, "parameters": asdict(config), "context_statistics": plan.statistics,
              "report_stage": "before_model_loading", "model_weights_loaded": False, "device_probed": False}
    print(canonical_json(report), flush=True)
    if args.preflight:
        return 0
    started = time.time()
    provenance = {"input": data_info, "model_before": model_before_info, "model_after": model_after_info,
                  "tokenizer_before": before_identity, "tokenizer_after": after_identity,
                  "versions": versions, "device": device,
                  "physical_gpu_selection": os.environ.get("CUDA_VISIBLE_DEVICES") if device.startswith("cuda") else None}
    document = estimate_rule_document(plan, config, before_identity, args.model_before, args.model_after,
                                      tokenizer, device, args.dtype, provenance)
    # Recheck immutable inputs before publication; changed data/weights cannot
    # silently produce a rule file with the pre-run provenance.
    if file_sha256(args.input) != data_info["sha256"]:
        raise ValueError("training parquet changed during estimation; no rules published")
    if model_asset_identity(args.model_before, hash_weights=args.hash_model_weights) != model_before_info:
        raise ValueError("O checkpoint changed during estimation; no rules published")
    if model_asset_identity(args.model_after, hash_weights=args.hash_model_weights) != model_after_info:
        raise ValueError("W checkpoint changed during estimation; no rules published")
    try:
        from baseline_acl.inverse_watermark import RuleTable
    except ModuleNotFoundError:
        from inverse_watermark import RuleTable
    RuleTable(document)  # validate the shared consumer contract before writing
    document["provenance"]["elapsed_seconds"] = time.time() - started
    publish_rules(args.output, document)
    print(f"[published] {args.output.resolve()} prefixes={len(document['prefix_scores'])}, "
          f"global_candidates={len(document['global_scores'])}", flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, FileNotFoundError, FileExistsError, ImportError, RuntimeError) as error:
        print(f"[error] {error}", file=sys.stderr)
        raise SystemExit(1)
