"""Estimated watermark rules and inverse logits bias for ACL TP/WN attacks.

This module imports only the standard library. It neither knows the KGW key nor
loads models. Rule estimation lives in ``steal_watermark.py``.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


RULE_FORMAT = "acl-watermark-rules"
RULE_VERSION = 1
TOKENIZER_COMPATIBILITY_VERSION = 1


def _stable_value(value: Any) -> Any:
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    if isinstance(value, Mapping):
        return {str(key): _stable_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_stable_value(item) for item in value]
    # Hugging Face AddedToken carries flags that str(token) alone would lose.
    if hasattr(value, "content"):
        return {key: _stable_value(getattr(value, key)) for key in
                ("content", "single_word", "lstrip", "rstrip", "normalized", "special")
                if hasattr(value, key)}
    raise TypeError(f"unsupported tokenizer configuration value: {type(value).__name__}")


def _value_fingerprint(value: Any) -> str:
    payload = json.dumps(_stable_value(value), sort_keys=True, ensure_ascii=False,
                         separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def tokenizer_identity(tokenizer: Any) -> dict[str, Any]:
    """Fingerprint token IDs and tokenization behavior, independently of paths.

The fast tokenizer's backend covers normalizer, pre-tokenizer, model, decoder,
and post-processor. Slow SentencePiece tokenizers contribute their serialized
model. Backend padding/truncation state and model/cache paths are excluded.
The original fingerprint is retained for existing rule files; a versioned
compatibility fingerprint normalizes redundant save_pretrained metadata.
    """
    vocab = tokenizer.get_vocab()
    vocab_size = len(tokenizer)
    if not isinstance(vocab, dict) or not vocab or not isinstance(vocab_size, int):
        raise ValueError("tokenizer must expose a nonempty vocabulary and integer length")
    for token, token_id in vocab.items():
        if not isinstance(token, str) or type(token_id) is not int or not 0 <= token_id < vocab_size:
            raise ValueError("invalid token-to-ID vocabulary mapping")
    ignored_keys = {
        "name_or_path", "_name_or_path", "cache_dir", "revision", "_commit_hash",
        "local_files_only", "trust_remote_code", "model_max_length",
        "tokenizer_file", "vocab_file", "merges_file", "sp_model_file",
        "special_tokens_map_file", "added_tokens_file", "tokenizer_config_file",
    }
    init_kwargs = getattr(tokenizer, "init_kwargs", {})
    stable_kwargs = {key: value for key, value in init_kwargs.items()
                     if key not in ignored_keys and not key.endswith("_file")}
    behavior: dict[str, Any] = {
        "vocab": vocab,
        "vocab_size": vocab_size,
        "special_tokens_map": getattr(tokenizer, "special_tokens_map", {}),
        "all_special_ids": getattr(tokenizer, "all_special_ids", []),
        "added_tokens_decoder": getattr(tokenizer, "added_tokens_decoder", {}),
        "init_kwargs": stable_kwargs,
        "chat_template": getattr(tokenizer, "chat_template", None),
        "attributes": {key: getattr(tokenizer, key) for key in (
            "padding_side", "truncation_side", "clean_up_tokenization_spaces",
            "split_special_tokens", "add_bos_token", "add_eos_token", "legacy",
            "do_lower_case", "strip_accents", "tokenize_chinese_chars",
        ) if hasattr(tokenizer, key)},
    }
    backend = getattr(tokenizer, "backend_tokenizer", None)
    if backend is not None:
        serialized = json.loads(backend.to_str())
        serialized.pop("padding", None)
        serialized.pop("truncation", None)
        behavior["backend"] = serialized
    sp_model = getattr(tokenizer, "sp_model", None)
    if sp_model is not None and hasattr(sp_model, "serialized_model_proto"):
        behavior["sentencepiece_sha256"] = hashlib.sha256(sp_model.serialized_model_proto()).hexdigest()
    # Keep the old hash unchanged so already published rules remain readable.
    fingerprint = _value_fingerprint(behavior)
    effective = dict(behavior)
    effective_kwargs = dict(stable_kwargs)
    # HF saves effective settings back into init_kwargs, sometimes changing
    # strings to AddedToken objects or introducing previously absent defaults.
    # These values are checked above through their actual runtime properties.
    redundant_keys = set(behavior["attributes"]) | set(behavior["special_tokens_map"])
    redundant_keys.update({"chat_template", "added_tokens_decoder", "tokenizer_class"})
    for key in redundant_keys:
        effective_kwargs.pop(key, None)
    # Missing and empty extra_special_tokens both mean no extra named roles.
    # Retain nonempty mappings and every unknown kwarg rather than ignoring
    # arbitrary settings that might change tokenization.
    if effective_kwargs.get("extra_special_tokens") == {}:
        effective_kwargs.pop("extra_special_tokens")
    effective["init_kwargs"] = effective_kwargs
    effective["tokenizer_class"] = f"{type(tokenizer).__module__}.{type(tokenizer).__qualname__}"
    return {"vocab_size": vocab_size, "fingerprint": fingerprint,
            "name_or_path": str(getattr(tokenizer, "name_or_path", "")),
            "compatibility": {"version": TOKENIZER_COMPATIBILITY_VERSION,
                              "fingerprint": _value_fingerprint(effective)},
            "component_fingerprints": {key: _value_fingerprint(value) for key, value in effective.items()},
            "init_kwargs_fingerprints": {key: _value_fingerprint(value) for key, value in effective_kwargs.items()}}


def _is_fingerprint(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(char in "0123456789abcdef" for char in value)


def tokenizer_identities_match(expected: Mapping, actual: Mapping) -> bool:
    """Accept an exact legacy identity or equal versioned effective behavior."""
    if expected.get("vocab_size") != actual.get("vocab_size"):
        return False
    if expected.get("fingerprint") is not None and expected.get("fingerprint") == actual.get("fingerprint"):
        return True
    left, right = expected.get("compatibility"), actual.get("compatibility")
    return (isinstance(left, Mapping) and isinstance(right, Mapping)
            and type(left.get("version")) is int and type(right.get("version")) is int
            and left["version"] == right["version"] == TOKENIZER_COMPATIBILITY_VERSION
            and _is_fingerprint(left.get("fingerprint"))
            and left["fingerprint"] == right.get("fingerprint"))


def tokenizer_mismatch_details(expected: Mapping, actual: Mapping) -> str:
    """Bounded diagnostics without printing the vocabulary or chat template."""
    details = [f"vocab_size: {expected.get('vocab_size')} vs {actual.get('vocab_size')}"]
    for field, label in (("component_fingerprints", "differing components"),
                         ("init_kwargs_fingerprints", "differing init_kwargs")):
        left, right = expected.get(field), actual.get(field)
        if isinstance(left, Mapping) and isinstance(right, Mapping):
            changed = sorted(key for key in left.keys() | right.keys() if left.get(key) != right.get(key))
            if changed:
                details.append(f"{label}: {', '.join(changed[:20])}" + (" ..." if len(changed) > 20 else ""))
    details.append(f"paths: {expected.get('name_or_path', '?')} vs {actual.get('name_or_path', '?')}")
    return "; ".join(details)


def _number(value: Any, label: str, *, minimum: float = 0, maximum: float | None = None) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a finite number")
    result = float(value)
    if not math.isfinite(result) or result < minimum or (maximum is not None and result > maximum):
        raise ValueError(f"{label} out of range")
    return result


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key!r}")
        result[key] = value
    return result


class RuleTable:
    """Validated sparse single-token scores plus weighted prefix scores.

Each stored d score is in [0, 1]. The combined D score is the sum of the global
score and every matching suffix's weighted score; D is intentionally not capped.
    """

    def __init__(self, document: dict[str, Any]):
        if not isinstance(document, dict):
            raise ValueError("rules must be a JSON object")
        if document.get("format") != RULE_FORMAT or type(document.get("version")) is not int or document["version"] != RULE_VERSION:
            raise ValueError(f"expected {RULE_FORMAT!r} version {RULE_VERSION}")
        identity = document.get("tokenizer")
        if not isinstance(identity, dict) or type(identity.get("vocab_size")) is not int or identity["vocab_size"] <= 1:
            raise ValueError("rules tokenizer.vocab_size must be an integer > 1")
        fingerprint = identity.get("fingerprint")
        if not _is_fingerprint(fingerprint):
            raise ValueError("rules tokenizer.fingerprint must be a SHA256 hex digest")
        compatibility = identity.get("compatibility")
        if compatibility is not None and (not isinstance(compatibility, dict)
                or type(compatibility.get("version")) is not int
                or compatibility["version"] != TOKENIZER_COMPATIBILITY_VERSION
                or not _is_fingerprint(compatibility.get("fingerprint"))):
            raise ValueError("rules tokenizer.compatibility must contain a supported version and SHA256 fingerprint")
        if not isinstance(identity.get("name_or_path"), str):
            raise ValueError("rules tokenizer.name_or_path must be a string")
        parameters = document.get("parameters")
        if not isinstance(parameters, dict):
            raise ValueError("rules parameters must be an object")
        max_ngram = parameters.get("max_ngram")
        if type(max_ngram) is not int or not 1 <= max_ngram <= 16:
            raise ValueError("parameters.max_ngram must be an integer in [1,16]")
        _number(parameters.get("freq_threshold"), "parameters.freq_threshold", maximum=1)
        _number(parameters.get("alpha"), "parameters.alpha")
        if type(parameters.get("top_k")) is not int or not 1 <= parameters["top_k"] <= identity["vocab_size"]:
            raise ValueError("parameters.top_k must be in [1,vocab_size]")
        if not isinstance(document.get("provenance"), dict):
            raise ValueError("rules provenance must be an object")
        self.document = document
        self.tokenizer = dict(identity)
        self.parameters = dict(parameters)
        self.vocab_size = identity["vocab_size"]
        self.max_prefix = max_ngram - 1
        self.global_scores = self._scores(document.get("global_scores"), "global_scores")
        prefixes = document.get("prefix_scores")
        if not isinstance(prefixes, dict):
            raise ValueError("prefix_scores must be an object")
        self.prefix_scores: dict[tuple[int, ...], tuple[float, dict[int, float]]] = {}
        for key, entry in prefixes.items():
            if not isinstance(key, str) or not key:
                raise ValueError("prefix_scores keys must be comma-separated token IDs")
            parts = key.split(",")
            prefix = tuple(self._token_id(part, "prefix_scores key") for part in parts)
            if not 1 <= len(prefix) <= self.max_prefix:
                raise ValueError("prefix length exceeds parameters.max_ngram - 1")
            if not isinstance(entry, dict):
                raise ValueError(f"prefix_scores[{key!r}] must be an object")
            weight = _number(entry.get("weight"), f"prefix {key} weight")
            frequency = _number(entry.get("frequency"), f"prefix {key} frequency", maximum=1)
            if frequency <= 0 or type(entry.get("count")) is not int or entry["count"] <= 0:
                raise ValueError("prefix frequency and count must be positive")
            scores = self._scores(entry.get("scores"), f"prefix {key} scores")
            self.prefix_scores[prefix] = (weight, scores)

    def _token_id(self, value: Any, label: str) -> int:
        if not isinstance(value, str) or not value.isascii() or not value.isdecimal() or str(int(value)) != value:
            raise ValueError(f"{label}: token IDs must be canonical decimal strings")
        token_id = int(value)
        if not 0 <= token_id < self.vocab_size:
            raise ValueError(f"{label}: token ID {token_id} is outside the tokenizer vocabulary")
        return token_id

    def _scores(self, value: Any, label: str) -> dict[int, float]:
        if not isinstance(value, dict):
            raise ValueError(f"{label} must be an object")
        return {self._token_id(key, label): _number(score, label, maximum=1)
                for key, score in value.items()}

    @classmethod
    def load(cls, path: str | Path) -> RuleTable:
        with Path(path).open("r", encoding="utf-8") as handle:
            return cls(json.load(handle, object_pairs_hook=_unique_object))

    def validate_tokenizer(self, tokenizer: Any) -> None:
        actual = tokenizer_identity(tokenizer)
        if not tokenizer_identities_match(self.tokenizer, actual):
            raise ValueError("tokenizer mismatch: rules require the same vocabulary, token IDs, and tokenization configuration; "
                             + tokenizer_mismatch_details(self.tokenizer, actual))

    def penalties(self, prefix_ids: Sequence[int]) -> dict[int, float]:
        context = tuple(prefix_ids[-self.max_prefix:]) if self.max_prefix else ()
        if any(type(token_id) is not int or not 0 <= token_id < self.vocab_size for token_id in context):
            raise ValueError("prefix token IDs must be integers within the tokenizer vocabulary")
        result = {token_id: score for token_id, score in self.global_scores.items() if score}
        for length in range(1, min(len(context), self.max_prefix) + 1):
            match = self.prefix_scores.get(context[-length:])
            if match is None:
                continue
            weight, scores = match
            for token_id, score in scores.items():
                if weight and score:
                    result[token_id] = result.get(token_id, 0.0) + weight * score
        if any(not math.isfinite(score) for score in result.values()):
            raise ValueError("combined watermark scores overflowed")
        return result

    def confidence(self, prefix_ids: Sequence[int], token_id: int) -> float:
        if type(token_id) is not int or not 0 <= token_id < self.vocab_size:
            raise ValueError("token_id is outside the tokenizer vocabulary")
        context = tuple(prefix_ids[-self.max_prefix:]) if self.max_prefix else ()
        if any(type(value) is not int or not 0 <= value < self.vocab_size for value in context):
            raise ValueError("prefix token IDs must be integers within the tokenizer vocabulary")
        # TP asks about one candidate at a time. A complete global rule table
        # must not turn each such query into a full-vocabulary scan.
        result = self.global_scores.get(token_id, 0.0)
        for length in range(1, min(len(context), self.max_prefix) + 1):
            match = self.prefix_scores.get(context[-length:])
            if match is not None:
                weight, scores = match
                result += weight * scores.get(token_id, 0.0)
        if not math.isfinite(result):
            raise ValueError("combined watermark scores overflowed")
        return result


class VLLMInverseWatermarkProcessor:
    """vLLM V0 three-argument logits hook: logits -= strength * estimated D."""

    def __init__(self, rules: RuleTable, strength: float = 2.5):
        self.rules = rules
        self.strength = _number(strength, "strength")

    def __call__(self, prompt_token_ids: list[int], generated_token_ids: list[int], logits: Any) -> Any:
        if self.strength == 0:
            return logits
        # Concatenating is essential while generated context is shorter than two
        # tokens; the first output uses the prompt's final token(s).
        context = list(prompt_token_ids[-self.rules.max_prefix:]) + list(generated_token_ids[-self.rules.max_prefix:]) if self.rules.max_prefix else []
        penalties = self.rules.penalties(context)
        if not penalties:
            return logits
        if len(logits) < self.rules.vocab_size:
            raise ValueError("logits vocabulary is smaller than the rule tokenizer")
        if hasattr(logits, "device"):
            import torch

            token_ids = list(penalties)
            indices = torch.tensor(token_ids, dtype=torch.long, device=logits.device)
            amounts = torch.tensor([self.strength * penalties[token_id] for token_id in token_ids],
                                   dtype=logits.dtype, device=logits.device)
            logits[indices] -= amounts
        else:
            for token_id, score in penalties.items():
                logits[token_id] -= self.strength * score
        return logits


class TransformersInverseWatermarkProcessor:
    """Two-argument HF generation hook using the same direct-ID bias as WN.

    Causal ``input_ids`` already include both the paraphrase prompt and the
    generated answer. Only their final rule-context IDs are needed. There is
    no text projection or candidate filtering: every scored vocabulary token
    is penalized before the model's sampling warpers run.
    """

    def __init__(self, rules: RuleTable, strength: float = 2.5):
        self.rules = rules
        self.strength = _number(strength, "strength")
        self._direct_bias = VLLMInverseWatermarkProcessor(rules, self.strength)

    def __call__(self, input_ids: Any, scores: Any) -> Any:
        if self.strength == 0:
            return scores
        score_shape = getattr(scores, "shape", None)
        if score_shape is None or len(score_shape) != 2:
            raise ValueError("Transformers scores must be a two-dimensional batch of logits")
        if score_shape[1] < self.rules.vocab_size:
            raise ValueError("logits vocabulary is smaller than the rule tokenizer")
        if len(input_ids) != score_shape[0]:
            raise ValueError("input_ids and scores must have the same batch size")
        for row in range(score_shape[0]):
            suffix = input_ids[row][-self.rules.max_prefix:] if self.rules.max_prefix else []
            context = suffix.tolist() if hasattr(suffix, "tolist") else list(suffix)
            self._direct_bias(context, [], scores[row])
        return scores
