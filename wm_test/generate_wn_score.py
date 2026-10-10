#!/usr/bin/env python3
"""Run ACL watermark neutralization (WN) during trained-student inference.

Estimated rules alone affect sampling. The genuine KGW key is used afterwards
only to detect the residual watermark. ``--preflight`` validates local assets,
data, tokenizers and full prompt lengths on CPU, without loading model weights.
"""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
import math
import os
import re
import sys
import tempfile
from collections import OrderedDict
from pathlib import Path
from typing import Any, Callable

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from baseline_acl.inverse_watermark import RuleTable, VLLMInverseWatermarkProcessor


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Local test Parquet or JSONL; id and content message list")
    parser.add_argument("--student-model", "--model", dest="student_model", type=Path, required=True)
    parser.add_argument("--tokenizer", type=Path, default=None, help="Local tokenizer directory; defaults to student checkpoint")
    parser.add_argument("--rules", type=Path, required=True, help="Estimated rule JSON from steal_watermark.py")
    parser.add_argument("--output", "--student-output", dest="output", type=Path, required=True)
    parser.add_argument("--strength", "--inverse-strength", dest="strength", type=float, default=2.5,
                        help="Inverse logit bias delta-prime; 0 is a no-attack control")
    parser.add_argument("--limit", type=int, default=None, help="First N rows for smoke testing")
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--max-prompt-tokens", type=int, default=2048, help="Fail if any full prompt exceeds this budget")
    parser.add_argument("--max-new-tokens", type=int, default=1536)
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--top-p", type=float, default=0.9)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--tensor-parallel-size", type=int, default=1)
    parser.add_argument("--gpu-memory-utilization", type=float, default=0.75)
    parser.add_argument("--gamma", type=float, default=0.25, help="KGW detection only")
    parser.add_argument("--kgw-delta", type=float, default=2.0, help="Original KGW metadata; detection only")
    parser.add_argument("--hash-key", type=int, default=15_485_863, help="Original KGW key; detection only")
    parser.add_argument("--preflight", action="store_true", help="CPU checks only; no model loading or output writing")
    parser.add_argument("--overwrite", action="store_true", help="Atomically replace an existing final output")
    return parser.parse_args(argv)


def validate_args(args: argparse.Namespace) -> None:
    for key in ("batch_size", "max_prompt_tokens", "max_new_tokens", "tensor_parallel_size"):
        if getattr(args, key) <= 0:
            raise ValueError(f"--{key.replace('_', '-')} must be positive")
    if args.limit is not None and args.limit <= 0:
        raise ValueError("--limit must be positive")
    for key in ("strength", "temperature"):
        value = getattr(args, key)
        if not math.isfinite(value) or value < 0:
            raise ValueError(f"--{key} must be finite and nonnegative")
    for key in ("top_p", "gpu_memory_utilization", "gamma"):
        value = getattr(args, key)
        within_range = 0 < value <= 1 if key == "top_p" else 0 < value < 1
        if not math.isfinite(value) or not within_range:
            raise ValueError(f"--{key.replace('_', '-')} is outside its valid range")
    if not math.isfinite(args.kgw_delta) or args.kgw_delta <= 0 or args.hash_key <= 0:
        raise ValueError("KGW detector delta and key must be positive")
    destination = args.output.resolve()
    protected = [args.input.resolve(), args.rules.resolve()]
    if destination in protected:
        raise ValueError("output must differ from input and rule files")
    for directory in (args.student_model, args.tokenizer or args.student_model):
        if destination == directory.resolve() or directory.resolve() in destination.parents:
            raise ValueError("output must be outside the model/tokenizer directory")
    if args.output.exists() and not args.overwrite:
        raise FileExistsError(f"{args.output} exists; choose another output or pass --overwrite")
    if args.output.exists() and not args.output.is_file():
        raise ValueError("output path must be a regular file")


def validate_model_assets(model_path: Path) -> None:
    if not model_path.is_dir() or not (model_path / "config.json").is_file():
        raise FileNotFoundError(f"local HF model directory with config.json required: {model_path}")
    with (model_path / "config.json").open("r", encoding="utf-8") as handle:
        config = json.load(handle)
    if not isinstance(config, dict) or not isinstance(config.get("model_type"), str):
        raise ValueError(f"invalid local HF config.json: {model_path}")
    weights = list(model_path.glob("*.safetensors")) + list(model_path.glob("pytorch_model*.bin"))
    if not weights:
        raise FileNotFoundError(f"no local HF model weights found in {model_path}")
    for index_path in model_path.glob("*.index.json"):
        with index_path.open("r", encoding="utf-8") as handle:
            index = json.load(handle)
        weight_map = index.get("weight_map")
        if not isinstance(weight_map, dict) or not weight_map:
            raise ValueError(f"invalid model weight index: {index_path}")
        for filename in set(weight_map.values()):
            if not isinstance(filename, str) or Path(filename).name != filename:
                raise ValueError(f"invalid shard filename in {index_path}")
            if not (model_path / filename).is_file():
                raise FileNotFoundError(f"missing model shard: {model_path / filename}")


def read_rows(path: Path, limit: int | None = None) -> list[dict[str, Any]]:
    if path.suffix.lower() == ".parquet":
        import pyarrow.parquet as pq

        rows = pq.read_table(path, columns=["id", "content"]).to_pylist()
    elif path.suffix.lower() == ".jsonl":
        with path.open("r", encoding="utf-8") as handle:
            rows = [json.loads(line) for line in handle if line.strip()]
    else:
        raise ValueError("input must be a .parquet or .jsonl file")
    if not rows:
        raise ValueError("test input contains no rows")
    seen: set[str] = set()
    for index, row in enumerate(rows):
        if not isinstance(row, dict) or not isinstance(row.get("id"), str) or not row["id"]:
            raise ValueError(f"row {index}: nonempty string id required")
        if row["id"] in seen:
            raise ValueError(f"row {index}: duplicate id {row['id']!r}")
        seen.add(row["id"])
        content = row.get("content")
        if not isinstance(content, list) or not content:
            raise ValueError(f"row {index}: nonempty content message list required")
        for message in content:
            if not isinstance(message, dict) or not isinstance(message.get("role"), str) or not message["role"] or not isinstance(message.get("content"), str):
                raise ValueError(f"row {index}: messages require role and string content")
    return rows if limit is None else rows[:limit]


def prepare_rows(rows: list[dict[str, Any]], tokenizer: Any, max_prompt_tokens: int) -> list[dict[str, Any]]:
    prepared = []
    for row in rows:
        prompt = tokenizer.apply_chat_template(row["content"], add_generation_prompt=True, tokenize=False)
        if not isinstance(prompt, str):
            raise ValueError("tokenizer chat template did not return text")
        ids = tokenizer.encode(prompt, add_special_tokens=False)
        if not ids:
            raise ValueError(f"empty tokenized prompt for id {row['id']!r}")
        if len(ids) > max_prompt_tokens:
            raise ValueError(f"id {row['id']!r}: full prompt has {len(ids)} tokens, exceeds --max-prompt-tokens={max_prompt_tokens}; increase budget explicitly")
        prepared.append({"row": row, "prompt": prompt, "prompt_ids": ids})
    return prepared


def selected_gpus(value: str | None, tensor_parallel_size: int) -> list[str]:
    if not value or not value.strip():
        raise ValueError("set CUDA_VISIBLE_DEVICES explicitly to the GPU IDs chosen for WN inference")
    devices = [item.strip() for item in value.split(",")]
    pattern = re.compile(r"(?:[0-9]+|GPU-[A-Za-z0-9-]+|MIG-[A-Za-z0-9/-]+)\Z")
    if any(not pattern.fullmatch(item) for item in devices) or len(set(devices)) != len(devices):
        raise ValueError("CUDA_VISIBLE_DEVICES must contain distinct GPU IDs separated by ASCII commas")
    if len(devices) != tensor_parallel_size:
        raise ValueError("selected GPU count must equal --tensor-parallel-size")
    return devices


def sampling_parameters(factory: Callable, args: argparse.Namespace, rules: RuleTable, index: int) -> Any:
    return factory(n=1, temperature=args.temperature, top_p=args.top_p,
                   max_tokens=args.max_new_tokens, seed=args.seed + index,
                   skip_special_tokens=True,
                   logits_processors=[VLLMInverseWatermarkProcessor(rules, args.strength)])


def run_model(*, args: argparse.Namespace, prepared: list[dict[str, Any]], tokenizer: Any,
              rules: RuleTable, rules_sha256: str, input_sha256: str,
              engine_factory: Callable | None = None, sampling_factory: Callable | None = None,
              score_function: Callable | None = None, score_config_factory: Callable | None = None) -> None:
    """Generate all rows into a temporary file; publish only after complete success.

Optional factories enable CPU integration tests of the actual sampling hook and
output writer. Production dependencies are imported only at execution time.
    """
    if not prepared:
        raise ValueError("no prompts to generate")
    if args.output.exists() and not args.overwrite:
        raise FileExistsError(f"{args.output} already exists")
    if engine_factory is None or sampling_factory is None:
        from vllm import LLM, SamplingParams

        engine_factory = engine_factory or LLM
        sampling_factory = sampling_factory or SamplingParams
    if score_function is None or score_config_factory is None:
        from wm_data.kgw import KGWConfig, kgw_score

        score_function = score_function or kgw_score
        score_config_factory = score_config_factory or KGWConfig
    detector_config = score_config_factory(gamma=args.gamma, delta=args.kgw_delta, hash_key=args.hash_key)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    engine = None
    cache: OrderedDict = OrderedDict()
    try:
        engine = engine_factory(model=str(args.student_model.resolve()),
                                tokenizer=str((args.tokenizer or args.student_model).resolve()),
                                trust_remote_code=False, tensor_parallel_size=args.tensor_parallel_size,
                                dtype="auto", gpu_memory_utilization=args.gpu_memory_utilization,
                                max_model_len=args.max_prompt_tokens + args.max_new_tokens,
                                seed=args.seed)
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="\n", dir=args.output.parent,
                                         prefix=args.output.name + ".", suffix=".tmp", delete=False) as handle:
            temporary = Path(handle.name)
            for start in range(0, len(prepared), args.batch_size):
                batch = prepared[start:start + args.batch_size]
                sampling = [sampling_parameters(sampling_factory, args, rules, start + offset)
                            for offset in range(len(batch))]
                # Passing IDs explicitly prevents vLLM from adding BOS or
                # retokenizing a prompt differently from length checks/scoring.
                prompts = [{"prompt_token_ids": item["prompt_ids"]} for item in batch]
                generations = engine.generate(prompts, sampling, use_tqdm=False)
                for offset, (item, result) in enumerate(zip(batch, generations, strict=True)):
                    if len(result.outputs) != 1:
                        raise ValueError("WN expects exactly one answer per prompt")
                    answer = result.outputs[0].text
                    if not isinstance(answer, str) or not answer.strip():
                        raise ValueError(f"empty/non-text answer for id {item['row']['id']!r}")
                    if list(result.prompt_token_ids) != list(item["prompt_ids"]):
                        raise ValueError("vLLM result prompt IDs differ from validated input")
                    # Match wm_test's visible-answer retokenization and deduped
                    # KGW detection; this is independent of estimated rules.
                    score = score_function(prompt_token_ids=item["prompt_ids"],
                                           generated_token_ids=tokenizer.encode(answer, add_special_tokens=False),
                                           vocab_size=len(tokenizer), config=detector_config, device="cuda",
                                           include_deduplicated=True, greenlist_cache=cache)
                    record = {
                        "id": item["row"]["id"], "model_label": "kgw_trained_student_wn",
                        "label": "kgw", "is_watermarked": True,
                        "model_path": str(args.student_model.resolve()),
                        "prompt": item["row"]["content"], "answer": answer, **score,
                        "kgw": {"gamma": args.gamma, "delta": args.kgw_delta, "hash_key": args.hash_key,
                                "seeding": "simple_1 (hash_key * previous_token_id)",
                                "detection_threshold_z": 4.0,
                                "deduplication": "unique (previous_token_id, token_id) pairs"},
                        "generation": {"temperature": args.temperature, "top_p": args.top_p,
                                       "max_new_tokens": args.max_new_tokens, "max_prompt_tokens": args.max_prompt_tokens,
                                       "prompt_tokens": len(item["prompt_ids"]), "prompt_truncated": False,
                                       "seed": args.seed + start + offset,
                                       "kgw_enabled_during_generation": False,
                                       "wn_enabled_during_generation": args.strength > 0,
                                       "finish_reason": getattr(result.outputs[0], "finish_reason", None)},
                        "attack": {"method": "WN", "stage": "inference", "strength": args.strength,
                                   "rules_path": str(args.rules.resolve()), "rules_sha256": rules_sha256,
                                   "rule_format": rules.document["format"], "rule_version": rules.document["version"],
                                   "tokenizer": rules.tokenizer, "parameters": rules.parameters,
                                   "rules_provenance": rules.document["provenance"],
                                   "input_path": str(args.input.resolve()), "input_sha256": input_sha256,
                                   "model_path": str(args.student_model.resolve()),
                                   "seed": args.seed + start + offset},
                    }
                    handle.write(json.dumps(record, ensure_ascii=False, allow_nan=False) + "\n")
                handle.flush()
                print(f"WN: {start + len(batch)}/{len(prepared)} answers generated and scored", flush=True)
            os.fsync(handle.fileno())
        if args.overwrite:
            os.replace(temporary, args.output)
        elif os.name == "nt":
            # Windows rename refuses an existing destination atomically. Its
            # sandbox may forbid hard links even within a writable directory.
            os.rename(temporary, args.output)
        else:
            # Hard-link publication is atomic and refuses a raced destination.
            os.link(temporary, args.output)
            temporary.unlink()
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
        del engine
        gc.collect()
    print(f"Saved {len(prepared)} WN answers to {args.output}", flush=True)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    validate_args(args)
    validate_model_assets(args.student_model)
    tokenizer_path = args.tokenizer or args.student_model
    if not tokenizer_path.is_dir():
        raise FileNotFoundError(f"local tokenizer directory not found: {tokenizer_path}")
    rules_hash = file_sha256(args.rules)
    rules = RuleTable.load(args.rules)
    if file_sha256(args.rules) != rules_hash:
        raise ValueError("rule file changed while it was being loaded")
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(str(tokenizer_path.resolve()), local_files_only=True,
                                              trust_remote_code=False)
    rules.validate_tokenizer(tokenizer)
    input_hash = file_sha256(args.input)
    rows = read_rows(args.input, args.limit)
    if file_sha256(args.input) != input_hash:
        raise ValueError("input file changed while it was being loaded")
    prepared = prepare_rows(rows, tokenizer, args.max_prompt_tokens)
    if args.preflight:
        print(json.dumps({"mode": "preflight", "attack": "WN", "rows": len(prepared),
                          "model": str(args.student_model.resolve()), "rules_sha256": rules_hash,
                          "input_sha256": input_hash, "strength": args.strength,
                          "maximum_prompt_tokens": max(len(item["prompt_ids"]) for item in prepared),
                          "tokenizer": rules.tokenizer}, ensure_ascii=False, indent=2))
        return
    selected_gpus(os.environ.get("CUDA_VISIBLE_DEVICES"), args.tensor_parallel_size)
    if os.environ.get("VLLM_USE_V1", "0") != "0":
        raise ValueError("WN uses vLLM V0 custom logits processors; set VLLM_USE_V1=0")
    os.environ["VLLM_USE_V1"] = "0"
    import torch

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required for WN generation and the original KGW detector RNG")
    if torch.cuda.device_count() != args.tensor_parallel_size:
        raise RuntimeError("CUDA device count differs from explicitly selected tensor-parallel devices")
    run_model(args=args, prepared=prepared, tokenizer=tokenizer, rules=rules,
              rules_sha256=rules_hash, input_sha256=input_hash)


if __name__ == "__main__":
    main()
