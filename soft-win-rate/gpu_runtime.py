"""Read-only GPU discovery and conservative local-judge placement (stdlib only)."""
from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
import importlib.metadata
import itertools
import json
import math
import os
from pathlib import Path
import re
import subprocess
from typing import Any

MIB = 1024 ** 2


@dataclass(frozen=True)
class GPU:
    index: int
    uuid: str
    name: str
    total_mib: int
    free_mib: int
    utilization: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ModelSpec:
    weight_bytes: int
    num_attention_heads: int
    num_key_value_heads: int
    num_hidden_layers: int
    head_dim: int
    dtype_bytes: int = 2

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class GPUPlan:
    gpu_ids: tuple[int, ...]
    gpu_uuids: tuple[str, ...]
    tensor_parallel_size: int
    gpu_memory_utilization: float
    estimated_per_gpu_mib: float
    enforce_eager: bool = True
    memory_accounting: str = "per_instance"
    available_per_gpu_mib: float | None = None

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["gpu_ids"] = list(self.gpu_ids)
        result["gpu_uuids"] = list(self.gpu_uuids)
        return result


def detect_memory_accounting(vllm_version: str | None = None, use_v1: str | None = None) -> str:
    """Detect the verified 0.8.5 V1 global-occupancy formula without importing CUDA.

    That version subtracts other processes' occupancy in its profiling peak.
    Reducing its utilization by free/total would subtract that occupancy twice.
    Do not apply this exception to unverified releases or the V0 engine.
    """
    if vllm_version is None:
        try:
            vllm_version = importlib.metadata.version("vllm")
        except importlib.metadata.PackageNotFoundError:
            vllm_version = "unavailable"
    if use_v1 is None:
        use_v1 = os.environ.get("VLLM_USE_V1", "1")
    if use_v1 != "0" and re.match(r"^0\.8\.5(?:$|[.+])", vllm_version):
        return "legacy_v1_total"
    return "per_instance"


def filter_visible_gpus(gpus: list[GPU], mask: str | None) -> list[GPU]:
    """Resolve an existing CUDA mask; never silently expand the allowed set."""
    if mask is None:
        return list(gpus)
    if not mask.strip() or mask.strip() == "-1":
        return []
    selected: list[GPU] = []
    for token in mask.split(","):
        token = token.strip()
        if token.isdecimal():
            matches = [gpu for gpu in gpus if gpu.index == int(token)]
        else:
            matches = [gpu for gpu in gpus if gpu.uuid == token or gpu.uuid.startswith(token)]
        if len(matches) != 1 or matches[0] in selected:
            raise ValueError(f"CUDA_VISIBLE_DEVICES contains an invalid, ambiguous or duplicate GPU: {token!r}")
        selected.append(matches[0])
    return selected


def discover_gpus() -> list[GPU]:
    """Query current free memory without creating a CUDA context."""
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=index,uuid,name,memory.total,memory.free,utilization.gpu",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, check=True, timeout=30,
        )
    except (FileNotFoundError, subprocess.SubprocessError) as error:
        raise RuntimeError("Cannot query NVIDIA GPUs with nvidia-smi; run this script on the GPU server") from error
    gpus = []
    for fields in csv.reader(result.stdout.splitlines()):
        if not fields or not any(field.strip() for field in fields):
            continue
        if len(fields) != 6:
            raise ValueError("Unexpected nvidia-smi GPU inventory format")
        index, uuid, name, total, free, utilization = (field.strip() for field in fields)
        try:
            gpu = GPU(int(index), uuid, name, int(float(total)), int(float(free)), int(float(utilization)))
        except ValueError as error:
            raise ValueError("nvidia-smi did not return numeric GPU memory/utilization data") from error
        if not gpu.uuid or gpu.total_mib <= 0 or not 0 <= gpu.free_mib <= gpu.total_mib:
            raise ValueError("nvidia-smi returned invalid GPU memory data")
        gpus.append(gpu)
    return filter_visible_gpus(gpus, os.environ.get("CUDA_VISIBLE_DEVICES"))


def load_model_spec(model_path: str | Path) -> ModelSpec:
    """Estimate BF16 allocation using local model config and weight metadata."""
    path = Path(model_path)
    config = json.loads((path / "config.json").read_text(encoding="utf-8"))
    if isinstance(config.get("text_config"), dict):
        config = config["text_config"]
    index = path / "model.safetensors.index.json"
    if index.is_file():
        weight_bytes = json.loads(index.read_text(encoding="utf-8"))["metadata"]["total_size"]
    else:
        weights = list(path.glob("*.safetensors"))
        if not weights:
            weights = list(path.glob("pytorch_model*.bin"))
        if not weights:
            raise FileNotFoundError(f"No local model weights found in {path}")
        weight_bytes = sum(file.stat().st_size for file in weights)
    heads = config["num_attention_heads"]
    if not isinstance(heads, int) or isinstance(heads, bool) or heads <= 0:
        raise ValueError("Invalid local model attention head count")
    spec = ModelSpec(
        weight_bytes=weight_bytes,
        num_attention_heads=heads,
        num_key_value_heads=config.get("num_key_value_heads", heads),
        num_hidden_layers=config["num_hidden_layers"],
        head_dim=config["head_dim"] if "head_dim" in config else config["hidden_size"] // heads,
    )
    if any(not isinstance(value, int) or isinstance(value, bool) or value <= 0
           for value in spec.to_dict().values()):
        raise ValueError("Invalid local model dimensions or weight size")
    return spec


def plan_gpus(
    gpus: list[GPU], model_spec: ModelSpec, *, max_model_len: int = 8192, max_num_seqs: int = 2,
    memory_accounting: str = "per_instance",
) -> list[GPUPlan]:
    """Single-card plans first, then valid TP groups using current free memory.

    Memory estimates are admission heuristics, not guarantees. vLLM performs
    actual startup profiling; the caller may retry another plan after an OOM.
    Existing GPU processes are never stopped, and GPU counts are not assumed
    to be valid tensor-parallel factors merely because they are available.
    """
    if max_model_len < 1 or max_num_seqs < 1:
        raise ValueError("max_model_len and max_num_seqs must be positive")
    if memory_accounting not in {"per_instance", "legacy_v1_total"}:
        raise ValueError(f"Unknown vLLM memory accounting mode: {memory_accounting}")
    if not gpus:
        return []
    # Two GiB per rank for runtime/workspaces, plus >=768 MiB free headroom.
    # Eager mode avoids a large CUDA-graph allocation during startup.
    runtime_mib = 2048
    kv_bytes = (2 * model_spec.num_hidden_layers * model_spec.num_key_value_heads
                * model_spec.head_dim * model_spec.dtype_bytes * max_model_len * max_num_seqs)
    candidates: list[tuple[tuple[Any, ...], GPUPlan]] = []
    for tp in range(1, len(gpus) + 1):
        if model_spec.num_attention_heads % tp:
            continue
        # Restrict to non-replicated KV head splits for a conservative estimate.
        if model_spec.num_key_value_heads % tp:
            continue
        estimate = (model_spec.weight_bytes + kv_bytes) / tp / MIB + runtime_mib
        for group in itertools.combinations(gpus, tp):
            headrooms = [max(768, gpu.total_mib * 0.01) for gpu in group]
            if any(gpu.free_mib - reserve < estimate for gpu, reserve in zip(group, headrooms)):
                continue
            if memory_accounting == "legacy_v1_total":
                # v0.8.5 V1: utilization caps global occupancy, including existing
                # processes. Its own budget is total*fraction - existing usage.
                # Keep >=2% total free; never treat occupied memory as available.
                utilization = min(0.98, *(1 - reserve / gpu.total_mib
                                          for gpu, reserve in zip(group, headrooms)))
            else:
                # Per-instance accounting: keep the request within free VRAM.
                utilization = min(0.93, *(max(0.0, gpu.free_mib - reserve) / gpu.total_mib
                                          for gpu, reserve in zip(group, headrooms)))
            utilization = math.floor(utilization * 1000) / 1000
            budgets = [gpu.total_mib * utilization - (
                gpu.total_mib - gpu.free_mib if memory_accounting == "legacy_v1_total" else 0)
                for gpu in group]
            if utilization <= 0 or min(budgets) < estimate:
                continue
            plan = GPUPlan(tuple(gpu.index for gpu in group), tuple(gpu.uuid for gpu in group),
                           tp, utilization, round(estimate, 2), memory_accounting=memory_accounting,
                           available_per_gpu_mib=round(min(budgets), 2))
            # Prefer the simplest feasible plan, then more spare memory and idle compute.
            rank = (tp, -min(budget - estimate for budget in budgets),
                    sum(gpu.utilization for gpu in group), plan.gpu_ids)
            candidates.append((rank, plan))
    return [plan for _, plan in sorted(candidates, key=lambda item: item[0])]
