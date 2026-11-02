"""Local Hugging Face generation shared by SQuAD and MT-Bench.

Imports of torch/transformers and WN rules are lazy. No weights or tokenizer are
downloaded, and no prompt is silently truncated. Batch size is intentionally one
so that per-example seeds and WN suffix contexts have unambiguous semantics.
"""
from __future__ import annotations

import gc
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import random
import sys
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def resolve_path(value: str | Path) -> Path:
    path = Path(value).expanduser()
    return (path if path.is_absolute() else PROJECT_ROOT / path).resolve()


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _model_files(path: Path) -> list[Path]:
    if not (path / "config.json").is_file():
        raise FileNotFoundError(f"Missing local Hugging Face config.json: {path}")
    for name in ("model.safetensors.index.json", "pytorch_model.bin.index.json"):
        index = path / name
        if index.is_file():
            mapping = json.loads(index.read_text(encoding="utf-8")).get("weight_map", {})
            if not isinstance(mapping, dict) or not mapping:
                raise ValueError(f"Invalid weight index: {index}")
            shards = sorted({path / value for value in mapping.values()})
            missing = [str(shard) for shard in shards if not shard.is_file()]
            if missing:
                raise FileNotFoundError(f"Incomplete model export, missing shards: {missing}")
            return [index, *shards]
    for name in ("model.safetensors", "pytorch_model.bin"):
        if (path / name).is_file():
            return [path / name]
    raise FileNotFoundError(f"Missing full HF weights/index: {path}; export/merge FSDP weights first")


def model_fingerprint(path: str | Path) -> dict[str, Any]:
    """Hash small model assets; record weight size/mtime instead of reading GBs."""
    path = resolve_path(path)
    weights = _model_files(path)
    assets = []
    for file in sorted(path.iterdir()):
        if file.is_file() and file.suffix in {".json", ".jinja", ".txt", ".model"}:
            assets.append({"name": file.name, "sha256": sha256_file(file)})
    return {
        "path": str(path), "assets": assets,
        "weights": [{"name": file.name, "size": file.stat().st_size, "mtime_ns": file.stat().st_mtime_ns} for file in weights],
        "weight_identity": "file_names_sizes_mtimes_not_full_weight_hash",
    }


def tokenizer_fingerprint(path: str | Path) -> dict[str, Any]:
    path = resolve_path(path)
    if not path.is_dir():
        raise FileNotFoundError(f"Tokenizer directory does not exist: {path}")
    names = ("tokenizer.json", "tokenizer_config.json", "special_tokens_map.json", "chat_template.jinja",
             "vocab.json", "merges.txt", "tokenizer.model", "spiece.model", "added_tokens.json")
    assets = [{"name": name, "sha256": sha256_file(path / name)} for name in names if (path / name).is_file()]
    if not any(item["name"] in {"tokenizer.json", "vocab.json", "tokenizer.model", "spiece.model"} for item in assets):
        raise FileNotFoundError(f"Tokenizer vocabulary is missing: {path}; set TOKENIZER_PATH to the student's tokenizer")
    return {"path": str(path), "assets": assets}


class LocalGenerator:
    """Single-process causal LM; device='auto' shards over visible devices."""

    def __init__(
        self, model_path: str | Path, tokenizer_path: str | Path | None = None,
        device: str = "cuda:0", dtype: str = "auto", max_input_tokens: int = 4096,
        max_new_tokens: int = 64, seed: int = 42,
        wn_rules_path: str | Path | None = None, wn_strength: float = 0.0,
        enable_thinking: bool = False,
    ):
        self.model_path = resolve_path(model_path)
        self.tokenizer_path = resolve_path(tokenizer_path) if tokenizer_path is not None else self.model_path
        self.device, self.dtype = device, dtype
        self.max_input_tokens, self.max_new_tokens, self.seed = max_input_tokens, max_new_tokens, seed
        self.wn_rules_path = resolve_path(wn_rules_path) if wn_rules_path is not None else None
        self.wn_strength, self.enable_thinking = wn_strength, enable_thinking
        self._model = self._tokenizer = self._torch = self._rules = None
        self._metadata = None
        self._context_limit = None
        for name, value in (("max_input_tokens", max_input_tokens), ("max_new_tokens", max_new_tokens)):
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise ValueError(f"{name} must be a positive integer")
        if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
            raise ValueError("seed must be a nonnegative integer")
        if isinstance(wn_strength, bool) or not isinstance(wn_strength, (int, float)) or not math.isfinite(wn_strength) or wn_strength < 0:
            raise ValueError("wn_strength must be finite and nonnegative")
        if wn_strength > 0 and self.wn_rules_path is None:
            raise ValueError("WN_STRENGTH > 0 requires an estimated WN_RULES_PATH; no KGW key is used")
        if dtype not in {"auto", "float32", "float16", "bfloat16"}:
            raise ValueError("dtype must be auto, float32, float16 or bfloat16")
        if enable_thinking is not False:
            raise ValueError("These evaluation protocols use enable_thinking=False")

    def check(self) -> dict[str, Any]:
        """Validate local assets/device/rules and load tokenizer, never weights."""
        if self._metadata is not None:
            return self._metadata
        if int(os.environ.get("WORLD_SIZE", "1")) != 1:
            raise RuntimeError("Run with python in one process; do not use multi-process torchrun/accelerate")
        fingerprint = model_fingerprint(self.model_path)
        tokenizer_identity = tokenizer_fingerprint(self.tokenizer_path)
        config = json.loads((self.model_path / "config.json").read_text(encoding="utf-8"))
        if config.get("is_encoder_decoder", False):
            raise ValueError("Only decoder-only causal models are supported")
        position_limit = config.get("max_position_embeddings")
        if isinstance(position_limit, int) and 0 < position_limit < 10**9:
            self._context_limit = position_limit
        import torch
        from transformers import AutoTokenizer

        self._torch = torch
        if self.device == "auto" or self.device.startswith("cuda"):
            if not torch.cuda.is_available():
                raise RuntimeError("CUDA is unavailable; use CUDA PyTorch or explicitly set DEVICE='cpu'")
            if self.device != "auto":
                index = torch.device(self.device).index or 0
                if index >= torch.cuda.device_count():
                    raise ValueError(f"Unavailable device {self.device}; check CUDA_VISIBLE_DEVICES")
        elif self.device != "cpu":
            raise ValueError("device must be cpu, cuda[:N] or auto")
        os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
        self._tokenizer = AutoTokenizer.from_pretrained(
            str(self.tokenizer_path), local_files_only=True, trust_remote_code=False,
        )
        if self.wn_strength > 0:
            if str(PROJECT_ROOT) not in sys.path:
                sys.path.insert(0, str(PROJECT_ROOT))
            from baseline_acl.inverse_watermark import RuleTable

            self._rules = RuleTable.load(self.wn_rules_path)
            self._rules.validate_tokenizer(self._tokenizer)
        versions = {}
        for name in ("torch", "transformers", "accelerate", "tokenizers"):
            try:
                versions[name] = importlib.metadata.version(name)
            except importlib.metadata.PackageNotFoundError:
                versions[name] = "not installed"
        self._metadata = {
            "model": fingerprint, "tokenizer": tokenizer_identity,
            "device": self.device, "dtype_requested": self.dtype,
            "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
            "max_input_tokens": self.max_input_tokens, "max_new_tokens": self.max_new_tokens,
            "model_context_limit": self._context_limit, "seed": self.seed,
            "enable_thinking": False, "versions": versions,
            "runtime_sha256": sha256_file(Path(__file__)),
            "chat_template_present": bool(getattr(self._tokenizer, "chat_template", None)),
            "wn": {"enabled": self.wn_strength > 0, "strength": self.wn_strength,
                   "rules_path": str(self.wn_rules_path) if self.wn_strength > 0 else None,
                   "rules_sha256": sha256_file(self.wn_rules_path) if self.wn_strength > 0 else None},
        }
        return self._metadata

    def _load(self) -> None:
        if self._model is not None:
            return
        self.check()
        from transformers import AutoModelForCausalLM

        options = {"local_files_only": True, "trust_remote_code": False,
                   "torch_dtype": self.dtype, "low_cpu_mem_usage": True}
        if self.device == "auto":
            options["device_map"] = "auto"
        print(f"[Load] {self.model_path} ({self.device}, {self.dtype})", flush=True)
        self._model = AutoModelForCausalLM.from_pretrained(str(self.model_path), **options)
        if self.device != "auto":
            self._model.to(self.device)
        self._model.eval()
        self._metadata["dtype_loaded"] = str(getattr(self._model, "dtype", "unknown"))

    def _render(self, messages: list[dict[str, str]] | str) -> str:
        if isinstance(messages, str):
            if not messages.strip():
                raise ValueError("Prompt must be nonempty")
            return messages
        if (not isinstance(messages, list) or not messages
                or any(not isinstance(item, dict) or item.get("role") not in {"system", "user", "assistant"}
                       or not isinstance(item.get("content"), str) for item in messages)
                or messages[-1]["role"] != "user"):
            raise ValueError("Expected a nonempty system/user/assistant conversation ending in user")
        if not getattr(self._tokenizer, "chat_template", None):
            raise ValueError("Tokenizer has no chat_template; use the student's training tokenizer/template, or explicitly pass a plain completion prompt")
        return self._tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True, enable_thinking=False,
        )

    def generate(
        self, messages: list[dict[str, str]] | str, *, temperature: float = 0.0,
        seed: int | None = None, max_new_tokens: int | None = None,
    ) -> dict[str, Any]:
        if not isinstance(temperature, (int, float)) or not math.isfinite(temperature) or temperature < 0:
            raise ValueError("temperature must be finite and nonnegative")
        budget = self.max_new_tokens if max_new_tokens is None else max_new_tokens
        if isinstance(budget, bool) or not isinstance(budget, int) or budget < 1:
            raise ValueError("max_new_tokens must be a positive integer")
        actual_seed = self.seed if seed is None else seed
        if isinstance(actual_seed, bool) or not isinstance(actual_seed, int) or actual_seed < 0:
            raise ValueError("seed must be a nonnegative integer")
        self.check()
        prompt = self._render(messages)
        encoded = self._tokenizer(prompt, return_tensors="pt", add_special_tokens=False, truncation=False)
        length = int(encoded["input_ids"].shape[-1])
        if not length or length > self.max_input_tokens:
            raise ValueError(f"Prompt has {length} tokens, limit={self.max_input_tokens}; no text was truncated. Increase MAX_INPUT_TOKENS consistently across comparisons")
        if self._context_limit is not None and length + budget > self._context_limit:
            raise ValueError(f"Prompt {length} + output budget {budget} exceeds model context {self._context_limit}; no text was truncated")
        self._load()
        from transformers import GenerationConfig, LogitsProcessorList

        torch = self._torch
        random.seed(actual_seed)
        torch.manual_seed(actual_seed)
        # Reset hidden sampling/repetition defaults inherited from a checkpoint.
        config = GenerationConfig.from_model_config(self._model.config)
        eos_ids = []
        for value in (config.eos_token_id, getattr(self._model.generation_config, "eos_token_id", None), self._tokenizer.eos_token_id):
            for token_id in value if isinstance(value, (list, tuple)) else [value]:
                if token_id is not None and token_id not in eos_ids:
                    eos_ids.append(int(token_id))
        if not eos_ids:
            raise ValueError("Model/tokenizer has no EOS token")
        config.eos_token_id = eos_ids
        pad = self._tokenizer.pad_token_id
        config.pad_token_id = eos_ids[0] if pad is None else pad
        config.max_new_tokens = budget
        config.num_beams = 1
        config.do_sample = temperature > 1e-5
        config.temperature = float(temperature) if config.do_sample else 1.0
        config.top_p = 1.0
        config.top_k = 0
        config.repetition_penalty = 1.0
        config.no_repeat_ngram_size = 0
        config.return_dict_in_generate = False
        processors = LogitsProcessorList()
        if self._rules is not None:
            from baseline_acl.inverse_watermark import TransformersInverseWatermarkProcessor

            processors.append(TransformersInverseWatermarkProcessor(self._rules, self.wn_strength))
        device = self._model.get_input_embeddings().weight.device
        if str(device) == "meta":
            device = next((p.device for p in self._model.parameters() if str(p.device) != "meta"), self._model.device)
        inputs = {key: value.to(device) for key, value in encoded.items()}
        with torch.inference_mode():
            sequences = self._model.generate(**inputs, generation_config=config, logits_processor=processors)
        completion = sequences[0, length:].tolist()
        finished = bool(completion) and completion[-1] in eos_ids
        return {
            "text": self._tokenizer.decode(completion, skip_special_tokens=True),
            "prompt_tokens": length, "completion_tokens": len(completion),
            "finish_reason": "stop" if finished or len(completion) < budget else "length",
            "rendered_prompt": prompt, "seed": actual_seed, "temperature": temperature,
            "wn_enabled": self._rules is not None,
            "model_dtype": str(getattr(self._model, "dtype", "unknown")),
        }

    def close(self) -> None:
        self._model = None
        gc.collect()
        if self._torch is not None and self._torch.cuda.is_available():
            self._torch.cuda.empty_cache()
