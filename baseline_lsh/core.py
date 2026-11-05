"""Frozen semantic buckets, deterministic green lists, and a vLLM V0 processor.

Only NumPy is required for loading assets and scoring token IDs. No teacher
weights, CUDA PRNG, or embedding encoder is needed after asset preparation.
"""
from __future__ import annotations

from collections import OrderedDict
from dataclasses import asdict, dataclass
import hashlib
import json
import math
from pathlib import Path

import numpy as np

VERSION = "semantic-lsh-additive-v1"
ASSET_VERSION = "semantic-lsh-buckets-v1"


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256_file(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def tokenizer_identity(tokenizer):
    """Use effective tokenization, including ID assignment, without path names."""
    vocab = tokenizer.get_vocab()
    if not vocab or len(set(vocab.values())) != len(vocab):
        raise ValueError("tokenizer must have unique nonempty vocabulary IDs")
    ids = sorted(vocab.values())
    if any(type(i) is not int or i < 0 for i in ids):
        raise ValueError("invalid tokenizer IDs")
    backend = getattr(tokenizer, "backend_tokenizer", None)
    if backend is None:
        raise ValueError("a fast tokenizer with a serializable backend is required")
    state = json.loads(backend.to_str())
    state.pop("padding", None)
    state.pop("truncation", None)
    payload = {"vocab": vocab, "backend": state,
               "special_ids": sorted(tokenizer.all_special_ids),
               "chat_template": tokenizer.chat_template}
    return {"sha256": hashlib.sha256(canonical(payload).encode()).hexdigest(),
            "num_tokens": len(ids), "id_space": ids[-1] + 1}


def project_buckets(embeddings, planes):
    """Gaussian hyperplane sign bits; float64 accumulation, LSB=plane zero."""
    e, p = np.asarray(embeddings), np.asarray(planes)
    if e.ndim != 2 or p.ndim != 2 or e.shape[1] != p.shape[1] or not 1 <= len(p) <= 12:
        raise ValueError("incompatible embedding/hyperplane dimensions (bits must be 1..12)")
    if not np.isfinite(e).all() or not np.isfinite(p).all():
        raise ValueError("non-finite embedding or hyperplane")
    signs = e.astype(np.float64) @ p.astype(np.float64).T >= 0
    return (signs.astype(np.int64) * (1 << np.arange(len(p), dtype=np.int64))).sum(axis=1)


class BucketAsset:
    def __init__(self, token_ids, bucket_ids, planes, metadata, digest=None):
        self.token_ids = np.asarray(token_ids, dtype=np.int64)
        self.bucket_ids = np.asarray(bucket_ids, dtype=np.int64)
        self.planes = np.asarray(planes, dtype=np.float32)
        self.metadata = dict(metadata)
        if self.metadata.get("format") != ASSET_VERSION:
            raise ValueError("unsupported LSH asset format")
        if self.token_ids.ndim != 1 or self.bucket_ids.shape != self.token_ids.shape or not len(self.token_ids):
            raise ValueError("invalid bucket map shapes")
        if self.token_ids[0] < 0 or np.any(np.diff(self.token_ids) <= 0):
            raise ValueError("asset token IDs must be nonnegative, unique, sorted")
        bits = self.metadata["lsh_bits"]
        if type(bits) is not int or not 1 <= bits <= 12 or self.planes.ndim != 2 or len(self.planes) != bits:
            raise ValueError("invalid LSH hyperplanes")
        if np.any(self.bucket_ids < 0) or np.any(self.bucket_ids >= 2 ** bits) or not np.isfinite(self.planes).all():
            raise ValueError("invalid bucket IDs or hyperplanes")
        identity = self.metadata["tokenizer"]
        if identity["num_tokens"] != len(self.token_ids) or identity["id_space"] != int(self.token_ids[-1]) + 1:
            raise ValueError("bucket map and tokenizer identity differ")
        self.id_space = int(self.token_ids[-1]) + 1
        self.lookup = np.full(self.id_space, -1, dtype=np.int64)
        self.lookup[self.token_ids] = self.bucket_ids
        self.groups = {int(k): self.token_ids[self.bucket_ids == k] for k in np.unique(self.bucket_ids)}
        self.sha256 = digest

    def bucket(self, token_id):
        token_id = int(token_id)
        if not 0 <= token_id < self.id_space or self.lookup[token_id] < 0:
            raise ValueError(f"token ID {token_id} is outside the frozen teacher vocabulary")
        return int(self.lookup[token_id])

    def check_tokenizer(self, tokenizer):
        if tokenizer_identity(tokenizer) != self.metadata["tokenizer"]:
            raise ValueError("tokenizer differs from frozen LSH asset; use the original teacher tokenizer")

    def save(self, path):
        path = Path(path)
        if path.exists():
            raise FileExistsError(f"asset already exists: {path}; choose a new path")
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(path.name + ".tmp")
        with temporary.open("wb") as f:
            np.savez_compressed(f, token_ids=self.token_ids, bucket_ids=self.bucket_ids,
                                planes=self.planes, metadata=np.array(canonical(self.metadata)))
        temporary.replace(path)
        self.sha256 = sha256_file(path)

    @classmethod
    def load(cls, path):
        with np.load(path, allow_pickle=False) as f:
            result = cls(f["token_ids"], f["bucket_ids"], f["planes"], json.loads(str(f["metadata"].item())), sha256_file(path))
        return result


@dataclass(frozen=True)
class LSHConfig:
    gamma: float = 0.5
    delta: float = 3.0
    hash_key: int = 15_485_863
    partition: str = "balanced"

    def __post_init__(self):
        if not math.isfinite(self.gamma) or not 0 < self.gamma < 1:
            raise ValueError("gamma must be finite and in (0,1)")
        if not math.isfinite(self.delta) or self.delta < 0:
            raise ValueError("delta must be finite and nonnegative")
        if type(self.hash_key) is not int or not 0 < self.hash_key < 2 ** 63:
            raise ValueError("hash-key must be a positive int64")
        if self.partition not in ("balanced", "global"):
            raise ValueError("partition must be balanced or global")


class LSHWatermark:
    def __init__(self, asset, config=LSHConfig(), cache_size=32):
        self.asset, self.config, self.cache_size = asset, config, cache_size
        self._cache = OrderedDict()

    def _rng(self, bucket, group, purpose):
        key = f"{VERSION}:{self.config.hash_key}:{bucket}:{group}:{purpose}"
        seed = int.from_bytes(hashlib.sha256(key.encode()).digest()[:16], "little")
        return np.random.Generator(np.random.PCG64(seed))

    def partition_for_bucket(self, bucket):
        """Largest-remainder allocation: exact global floor(gamma*V) count.

        Within each semantic group the green count differs from gamma*size by
        less than one. Keyed tie breaking avoids always rounding the same group.
        The precise split is an explicit implementation convention, not claimed
        to be the original authors' unpublished PRNG implementation.
        """
        if bucket in self._cache:
            self._cache.move_to_end(bucket)
            return self._cache[bucket]
        groups = self.asset.groups if self.config.partition == "balanced" else {0: self.asset.token_ids}
        keys = sorted(groups)
        target = int(self.config.gamma * len(self.asset.token_ids))
        quotas = {k: int(self.config.gamma * len(groups[k])) for k in keys}
        order = sorted(keys, key=lambda k: (-(self.config.gamma * len(groups[k]) - quotas[k]),
                                           int(self._rng(bucket, k, "round").bit_generator.random_raw())))
        for k in order[:target - sum(quotas.values())]:
            quotas[k] += 1
        mask = np.zeros(self.asset.id_space, dtype=np.bool_)
        rates = np.zeros(2 ** self.asset.metadata["lsh_bits"], dtype=np.float64)
        for k in keys:
            ids = groups[k]
            # PCG64 guarantees its raw bit stream. Avoid Generator.permutation,
            # whose sampling implementation need not be stable across versions.
            priorities = self._rng(bucket, k, "split").bit_generator.random_raw(len(ids))
            chosen = ids[np.lexsort((ids, priorities))[:quotas[k]]]
            mask[chosen] = True
            if self.config.partition == "balanced":
                rates[k] = quotas[k] / len(ids)
            else:
                rates[:] = quotas[k] / len(ids)
        self._cache[bucket] = (mask, rates)
        if len(self._cache) > self.cache_size:
            self._cache.popitem(last=False)
        return mask, rates

    def descriptor(self):
        return {"version": VERSION, "asset_sha256": self.asset.sha256, **asdict(self.config),
                "seeding": "previous-token-static-embedding-lsh",
                "prng": "PCG64-raw64-SHA256-ranked-per-context-bucket-and-semantic-group"}

    def score(self, generated_token_ids, prompt_token_ids=(), max_tokens=None):
        if max_tokens is not None and max_tokens <= 0:
            raise ValueError("max-tokens must be positive")
        tokens = [int(i) for i in generated_token_ids]
        if max_tokens is not None:
            tokens = tokens[:max_tokens]
        previous = int(prompt_token_ids[-1]) if len(prompt_token_ids) else None
        hits, probabilities, dedup_hits, dedup_probs, seen = [], [], [], [], set()
        for token in tokens:
            group = self.asset.bucket(token)
            if previous is not None:
                bucket = self.asset.bucket(previous)
                mask, rates = self.partition_for_bucket(bucket)
                hit, q = int(mask[token]), float(rates[group])
                hits.append(hit)
                probabilities.append(q)
                pair = (bucket, token)  # repeated key/token, not raw previous-token IDs
                if pair not in seen:
                    seen.add(pair)
                    dedup_hits.append(hit)
                    dedup_probs.append(q)
            previous = token

        def stats(flags, qs):
            n, g = len(flags), sum(flags)
            expected, variance = sum(qs), sum(q * (1 - q) for q in qs)
            return {"num_tokens": n, "green_tokens": g,
                    "green_fraction": g / n if n else 0.0, "null_expected": expected,
                    "null_variance": variance,
                    "z_score": (g - expected) / math.sqrt(variance) if variance > 0 else None}
        result = stats(hits, probabilities)
        result.update({"dedup_" + k: v for k, v in stats(dedup_hits, dedup_probs).items()})
        result["score_interpretation"] = "diagnostic standardized count; calibrate on matched clean outputs; no exact p-value"
        return result


class LSHLogitsProcessor:
    """Three-argument callable for vLLM 0.8.x V0, with lazy CUDA indices.

    CPU NumPy green lists are identical on CPU/CUDA. Padded/non-token logits
    are masked; all real tokenizer tokens, including special tokens, participate.
    """
    def __init__(self, watermark):
        self.watermark = watermark
        self._device_cache = OrderedDict()

    def __getstate__(self):
        return {"watermark": self.watermark, "_device_cache": OrderedDict()}

    def __call__(self, prompt_token_ids, generated_token_ids, logits):
        import torch
        if logits.ndim != 1 or logits.shape[0] < self.watermark.asset.id_space:
            raise ValueError("model logits do not cover the frozen tokenizer vocabulary")
        context = generated_token_ids if len(generated_token_ids) else prompt_token_ids
        key = (str(logits.device), None if not len(context) else self.watermark.asset.bucket(context[-1]))
        cached = self._device_cache.get(key)
        if cached is None:
            if len(context):
                mask, _ = self.watermark.partition_for_bucket(key[1])
                green = torch.tensor(np.flatnonzero(mask), dtype=torch.long, device=logits.device)
            else:
                green = torch.empty(0, dtype=torch.long, device=logits.device)
            valid = np.zeros(logits.shape[0], dtype=np.bool_)
            valid[self.watermark.asset.token_ids] = True
            invalid = torch.tensor(np.flatnonzero(~valid), dtype=torch.long, device=logits.device)
            cached = (green, invalid)
            self._device_cache[key] = cached
            if len(self._device_cache) > self.watermark.cache_size:
                self._device_cache.popitem(last=False)
        else:
            self._device_cache.move_to_end(key)
        green, invalid = cached
        logits[invalid] = -float("inf")
        logits[green] += self.watermark.config.delta
        return logits
