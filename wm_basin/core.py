"""Shared utilities for WM-Basin reproduction on EasyGAD (KGW + Dolly-15k)."""

from __future__ import annotations

import hashlib
import json
import math
import random
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np

# ---------------------------------------------------------------------------
# Default configuration aligned with EasyGAD KGW distillation
# ---------------------------------------------------------------------------
DEFAULT_TRUE_KEY = 15_485_863
DEFAULT_GAMMA = 0.5
DEFAULT_DELTA = 3.0
DEFAULT_PROJ_DIM = 8192
DEFAULT_PROJ_SEED = 20261125
DEFAULT_MAX_RESPONSE_TOKENS = 512
DEFAULT_MIN_RESPONSE_TOKENS = 32
DEFAULT_SYSTEM_PROMPT = "You are a helpful assistant."
DEFAULT_PUBLIC_MODELS_DIR = "/app/public_models"
DEFAULT_TEACHER_MODEL = f"{DEFAULT_PUBLIC_MODELS_DIR}/Qwen2.5-14B-Instruct"
DEFAULT_PROBE_MODEL = f"{DEFAULT_PUBLIC_MODELS_DIR}/Qwen2.5-1.5B-Instruct"

DEFAULT_LORA_TARGET_MODULES = [
    "q_proj",
    "k_proj",
    "v_proj",
    "o_proj",
    "gate_proj",
    "up_proj",
    "down_proj",
]

# Pilot (10 fast models) + Expansion (10 more models) = 20 models across 6 families
PILOT_CLEAN_MODELS = [
    "Qwen2.5-0.5B",
    "Qwen2.5-1.5B-Instruct",
    "Qwen2.5-3B-Instruct",
    "Qwen2.5-7B-Instruct",
    "Qwen3-0.6B",
    "Qwen3-4B",
    "Llama-3.2-1B-Instruct",
    "Llama-3.2-3B-Instruct",
    "Mistral-7B-Instruct-v0.2",
    "zephyr-7b-beta",
]

FULL_CLEAN_MODELS = PILOT_CLEAN_MODELS + [
    "Qwen2.5-Coder-7B-Instruct",
    "Qwen2.5-14B-Instruct",
    "Qwen3-8B",
    "Qwen3-14B",
    "Qwen3-32B-AWQ",
    "Llama-7b-hf",
    "Llama2-7b-hf",
    "Llama-3-8B",
    "Llama-3.2-1B",
    "Llama-3.2-3B",
    "meta-llama--Meta-Llama-3-8B-Instruct",
    "Llama-Guard-3-8B",
    "DeepSeek-Coder-V2-Lite-Instruct",
    "DeepSeek-R1-0528-Qwen3-8B",
    "DeepSeek-R1-Distill-Qwen-14B",
]

DEFAULT_CLEAN_TEMPERATURES = [0.7, 1.0, 1.3]


# ---------------------------------------------------------------------------
# I/O helpers (atomic writes)
# ---------------------------------------------------------------------------
def write_json(path: Path | str, data: Any) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def read_json(path: Path | str) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_jsonl(path: Path | str, rows: Iterable[dict[str, Any]]) -> int:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    count = 0
    with tmp.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            count += 1
    tmp.replace(path)
    return count


def read_jsonl(path: Path | str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def sha256_file(path: Path | str) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# Prompt formatting (exact match with wm_data/prepare_dolly.py)
# ---------------------------------------------------------------------------
def build_messages(instruction: str, context: str = "") -> list[dict[str, str]]:
    """Format instruction + optional context identically to EasyGAD Dolly prompts."""
    instruction = (instruction or "").strip()
    context = (context or "").strip()
    if not instruction:
        raise ValueError("Instruction must not be empty")

    sections = [
        "Below is an instruction that describes a task. "
        "Write a response that appropriately completes the request.",
        f"### Instruction:\n{instruction}",
    ]
    if context:
        sections.append(f"### Context:\n{context}")
    sections.append("### Response:\n")
    return [
        {"content": DEFAULT_SYSTEM_PROMPT, "role": "system"},
        {"content": "\n\n".join(sections), "role": "user"},
    ]


def normalize_text_for_dedup(text: str) -> str:
    return " ".join((text or "").lower().split())


def render_prompt_with_fallback(
    tokenizer: Any,
    messages: list[dict[str, str]],
    max_prompt_tokens: int = 2048,
) -> str:
    """Render chat messages using the model's chat template, falling back for base models."""
    chat_template = getattr(tokenizer, "chat_template", None)
    if chat_template:
        try:
            prompt = tokenizer.apply_chat_template(
                messages,
                add_generation_prompt=True,
                tokenize=False,
            )
        except Exception:
            # Some instruct models (e.g. Mistral/Gemma) reject a standalone system role.
            merged = _merge_system_into_user(messages)
            prompt = tokenizer.apply_chat_template(
                merged,
                add_generation_prompt=True,
                tokenize=False,
            )
    else:
        user_text = "\n\n".join(m["content"] for m in messages if m["role"] != "system")
        prompt = user_text

    prompt_ids = tokenizer.encode(prompt, add_special_tokens=False)
    if len(prompt_ids) > max_prompt_tokens:
        prompt_ids = prompt_ids[:max_prompt_tokens]
        prompt = tokenizer.decode(prompt_ids, skip_special_tokens=False)
    return prompt


def _merge_system_into_user(messages: list[dict[str, str]]) -> list[dict[str, str]]:
    sys_parts = [m["content"].strip() for m in messages if m["role"] == "system" and m.get("content")]
    rest = [dict(m) for m in messages if m["role"] != "system"]
    if sys_parts and rest and rest[0]["role"] == "user":
        rest[0]["content"] = "\n\n".join(sys_parts) + "\n\n" + rest[0]["content"]
    return rest


# ---------------------------------------------------------------------------
# Key generation (supports incremental expansion while preserving existing keys)
# ---------------------------------------------------------------------------
def generate_keys(
    total_keys: int,
    true_key: int = DEFAULT_TRUE_KEY,
    seed: int = 42,
    existing_keys: list[int] | None = None,
) -> list[int]:
    """Return [true_key, decoy_1, ..., decoy_{total_keys-1}].

    If existing_keys is supplied, preserves its prefix verbatim and appends new
    unique decoy keys so expanding from 40 -> 100 -> 1000 never invalidates prior work.
    """
    if total_keys < 2:
        raise ValueError(f"total_keys must be >= 2, got {total_keys}")
    if existing_keys:
        if existing_keys[0] != true_key:
            raise ValueError(
                f"Existing keys[0]={existing_keys[0]} does not match true_key={true_key}"
            )
        keys = list(existing_keys)
    else:
        keys = [int(true_key)]

    seen = set(keys)
    rng = random.Random(seed)
    # Fast-forward RNG deterministically if expanding from an earlier list
    # by drawing until we reach total_keys unique entries.
    upper = (1 << 62) - 1
    while len(keys) < total_keys:
        cand = rng.randrange(1, upper)
        if cand not in seen:
            seen.add(cand)
            keys.append(cand)
    return keys[:total_keys]


# ---------------------------------------------------------------------------
# Cached KGW LogitsProcessor (bit-for-bit identical to wm_data.kgw.KGWLogitsProcessor)
# ---------------------------------------------------------------------------
def make_cached_kgw_processor(
    vocab_size: int,
    gamma: float,
    delta: float,
    hash_key: int,
    cache_size: int = 256,
):
    """Create a KGWLogitsProcessor with a bounded int32 LRU cache on CUDA green lists.

    Each cached entry is int32 (~0.3 MB for 152k vocab), so cache_size=256 caps
    VRAM usage at ~75 MB per active key while staying bit-for-bit identical to
    wm_data.kgw.KGWLogitsProcessor.
    """
    import torch
    from wm_data.kgw import KGWConfig, KGWLogitsProcessor

    class CachedKGWLogitsProcessor(KGWLogitsProcessor):
        def __init__(self, vs: int, cfg: KGWConfig, maxsize: int = 256):
            super().__init__(vs, cfg)
            self._cache: OrderedDict[tuple[int, str], Any] = OrderedDict()
            self._maxsize = maxsize

        def _greenlist(self, previous_token_id: int, device):
            if self._maxsize <= 0:
                return super()._greenlist(previous_token_id, device)
            key = (int(previous_token_id), str(device))
            cached = self._cache.get(key)
            if cached is not None:
                self._cache.move_to_end(key)
                return cached
            green = super()._greenlist(previous_token_id, device).to(torch.int32)
            self._cache[key] = green
            if len(self._cache) > self._maxsize:
                self._cache.popitem(last=False)
            return green

    return CachedKGWLogitsProcessor(
        vocab_size,
        KGWConfig(gamma=gamma, delta=delta, hash_key=hash_key),
        maxsize=cache_size,
    )


# ---------------------------------------------------------------------------
# Fixed-seed CountSketch / JL random projection (D -> proj_dim)
# ---------------------------------------------------------------------------
class BlockRademacherProjector:
    """Fast, memory-friendly, deterministic JL projection (D -> proj_dim).

    Uses CountSketch (each coordinate i maps to a deterministic bucket h(i) in
    [0, proj_dim) with sign s(i) in {-1, +1}).
    Properties:
      - Strictly linear: P(mean(g_i)) == mean(P(g_i))
      - Unbiased inner-product preservation: E[<Px, Py>] == <x, y>
      - O(D) time (~0.01s per 37M-dim vector on GPU) instead of O(D * proj_dim).
    """

    def __init__(
        self,
        proj_dim: int = DEFAULT_PROJ_DIM,
        seed: int = DEFAULT_PROJ_SEED,
        block_size: int = 65536,
    ):
        if proj_dim <= 0 or block_size <= 0:
            raise ValueError("proj_dim and block_size must be positive")
        self.proj_dim = int(proj_dim)
        self.seed = int(seed)
        self.block_size = int(block_size)
        self._cached_dim: int | None = None
        self._cached_device: str | None = None
        self._buckets = None
        self._signs = None

    def _ensure_sketch_torch(self, total: int, device) -> tuple[Any, Any]:
        import torch

        dev_key = str(device)
        if self._cached_dim == total and self._cached_device == dev_key:
            return self._buckets, self._signs
        # Generate on CPU with fixed seed so the sketch is identical across GPUs
        gen = torch.Generator(device="cpu")
        gen.manual_seed(self.seed)
        buckets = torch.randint(0, self.proj_dim, (total,), generator=gen, dtype=torch.int64)
        signs = (torch.randint(0, 2, (total,), generator=gen, dtype=torch.int8) * 2 - 1).to(torch.float32)
        self._buckets = buckets.to(device=device)
        self._signs = signs.to(device=device)
        self._cached_dim = total
        self._cached_device = dev_key
        return self._buckets, self._signs

    def project_torch(self, vec) -> np.ndarray:
        """Project a 1D torch.Tensor (CPU or CUDA) -> float32 numpy array of shape (proj_dim,)."""
        import torch

        if vec.ndim != 1:
            vec = vec.reshape(-1)
        device = vec.device
        vec = vec.to(dtype=torch.float32)
        total = vec.numel()
        buckets, signs = self._ensure_sketch_torch(total, device)
        out = torch.zeros(self.proj_dim, dtype=torch.float32, device=device)
        out.scatter_add_(0, buckets, vec * signs)
        return out.detach().cpu().numpy().astype(np.float32)

    def project_numpy(self, vec: np.ndarray) -> np.ndarray:
        """Pure-numpy CountSketch projection (for unit tests or CPU-only environments)."""
        vec = np.asarray(vec, dtype=np.float32).reshape(-1)
        total = vec.shape[0]
        rng = np.random.default_rng(self.seed)
        buckets = rng.integers(0, self.proj_dim, size=total, dtype=np.int64)
        signs = rng.choice(np.array([-1.0, 1.0], dtype=np.float32), size=total)
        out = np.zeros(self.proj_dim, dtype=np.float32)
        np.add.at(out, buckets, vec * signs)
        return out


# ---------------------------------------------------------------------------
# All-but-the-Top PCA subspace removal & Key-Randomization Rank Test
# ---------------------------------------------------------------------------
@dataclass
class TaskSubspace:
    mean: np.ndarray        # shape (d,)
    components: np.ndarray  # shape (q, d), orthonormal rows (U^T)

    @property
    def q(self) -> int:
        return int(self.components.shape[0])

    def project_out(self, x: np.ndarray) -> np.ndarray:
        """Remove mean and top-q task directions: (I - U U^T)(x - mean)."""
        x = np.asarray(x, dtype=np.float64)
        centered = x - self.mean
        if self.components.shape[0] == 0:
            return centered
        # components has shape (q, d): centered @ U @ U^T
        proj = (centered @ self.components.T) @ self.components
        return centered - proj

    def save(self, path: Path | str) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        np.savez(path, mean=self.mean.astype(np.float64), components=self.components.astype(np.float64))

    @classmethod
    def load(cls, path: Path | str) -> "TaskSubspace":
        data = np.load(path)
        return cls(mean=data["mean"], components=data["components"])


def fit_task_subspace(clean_matrix: np.ndarray, q: int) -> TaskSubspace:
    """Fit mean and top-q principal directions on clean model gradients (n_cells, d)."""
    X = np.asarray(clean_matrix, dtype=np.float64)
    if X.ndim != 2 or X.shape[0] < 2:
        raise ValueError(f"clean_matrix must be 2D with >=2 rows, got {X.shape}")
    mean = X.mean(axis=0)
    centered = X - mean
    max_q = min(X.shape[0] - 1, X.shape[1])
    if q < 0:
        raise ValueError(f"q must be >= 0, got {q}")
    eff_q = min(q, max_q)
    if eff_q == 0:
        return TaskSubspace(mean=mean, components=np.zeros((0, X.shape[1]), dtype=np.float64))
    # Economy SVD on (n_cells, d) is fast because n_cells << d
    _, _, vt = np.linalg.svd(centered, full_matrices=False)
    return TaskSubspace(mean=mean, components=vt[:eff_q])


def cosine_similarities(query: np.ndarray, bank: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    """Compute cosine similarity between query (d,) and each row of bank (K, d)."""
    q = np.asarray(query, dtype=np.float64).reshape(-1)
    B = np.asarray(bank, dtype=np.float64)
    q_norm = np.linalg.norm(q)
    b_norms = np.linalg.norm(B, axis=1)
    denom = np.maximum(q_norm * b_norms, eps)
    return (B @ q) / denom


def rank_test(scores: Sequence[float] | np.ndarray, claimed_idx: int = 0) -> dict[str, float | int]:
    """Non-parametric key-randomization rank test (Eq. 4 of WM-Basin).

    p_rank = (1 + #{j != claimed_idx : S(k_j) >= S(k*)}) / K
    Ties count against rejection, preserving exact finite-sample FPR control.
    """
    s = np.asarray(scores, dtype=np.float64).reshape(-1)
    K = int(s.shape[0])
    if K < 2:
        raise ValueError(f"Need at least 2 candidate keys, got {K}")
    if not 0 <= claimed_idx < K:
        raise ValueError(f"claimed_idx {claimed_idx} out of range [0, {K})")

    claimed_score = float(s[claimed_idx])
    decoys = np.delete(s, claimed_idx)
    num_ge = int(np.sum(decoys >= claimed_score))
    rank = 1 + num_ge
    p_rank = rank / K

    decoy_mean = float(decoys.mean())
    decoy_std = float(decoys.std(ddof=1)) if decoys.size > 1 else 0.0
    z_score = (claimed_score - decoy_mean) / decoy_std if decoy_std > 1e-12 else 0.0

    return {
        "claimed_idx": claimed_idx,
        "num_keys": K,
        "claimed_score": claimed_score,
        "decoy_mean": decoy_mean,
        "decoy_std": decoy_std,
        "decoy_max": float(decoys.max()),
        "z_score": float(z_score),
        "rank": rank,
        "p_rank": float(p_rank),
        "p_floor": 1.0 / K,
    }
