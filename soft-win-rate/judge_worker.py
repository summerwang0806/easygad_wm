"""Isolated offline vLLM judge worker; only this process imports CUDA libraries."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import time
import traceback
from typing import Any


def _append_result(path: Path, row: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def _is_memory_error(error: BaseException) -> bool:
    message = str(error).lower()
    return any(term in message for term in (
        "out of memory", "cuda out of memory", "not enough memory", "insufficient memory",
        "free memory on device", "no available memory for the cache blocks",
        "larger than the maximum number of tokens that can be stored in kv cache",
        "no memory available for cache", "insufficient kv cache memory",
    ))


def run_worker(config: dict[str, Any]) -> int:
    """Preflight all prompts, then generate in bounded offline batches."""
    results_file = Path(config["results_file"])
    tasks_file = Path(config["tasks_file"])
    error_file = Path(config.get("error_file", str(results_file) + ".error.json"))
    if results_file.resolve() == tasks_file.resolve() or error_file.resolve() in {
            tasks_file.resolve(), results_file.resolve()}:
        raise ValueError("Worker output/error files must not overwrite input tasks")
    results_file.parent.mkdir(parents=True, exist_ok=True)
    stage = "configuration"
    try:
        device_ids = config.get("gpu_ids")
        if device_ids is None and config.get("gpu_uuids"):
            raise ValueError("Numeric gpu_ids are required; UUIDs are audit metadata, not the CUDA device mask")
        if device_ids is not None:
            if (not isinstance(device_ids, list) or not device_ids
                    or any(not isinstance(index, int) or isinstance(index, bool) or index < 0 for index in device_ids)
                    or len(set(device_ids)) != len(device_ids)):
                raise ValueError("Worker requires a list of distinct numeric GPU IDs")
            os.environ["CUDA_VISIBLE_DEVICES"] = ",".join(str(index) for index in device_ids)
        mask = os.environ.get("CUDA_VISIBLE_DEVICES", "")
        if mask and any(not item.strip().isdecimal() for item in mask.split(",")):
            raise ValueError("This vLLM-compatible worker needs numeric CUDA_VISIBLE_DEVICES; rerun the updated launcher")
        os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["TRANSFORMERS_OFFLINE"] = "1"
        os.environ["VLLM_NO_USAGE_STATS"] = "1"
        os.environ["VLLM_WORKER_MULTIPROC_METHOD"] = "spawn"
        # Never pass paid-service credentials into the local inference process.
        os.environ.pop("OPENAI_API_KEY", None)
        os.environ.pop("SWANLAB_API_KEY", None)
        if config.get("enable_thinking", False) is not False:
            raise ValueError("This fixed judge protocol requires enable_thinking=False")
        if config.get("temperature", 0) != 0:
            raise ValueError("This fixed judge protocol uses greedy temperature=0")
        maximum = int(config.get("max_model_len", 8192))
        max_output = int(config.get("max_output_tokens", 512))
        max_seqs = int(config.get("max_num_seqs", 2))
        max_batched_tokens = int(config.get("max_num_batched_tokens", 4096))
        chunked_prefill = config.get("enable_chunked_prefill", True)
        if not 0 < max_output < maximum or max_seqs < 1:
            raise ValueError("Invalid worker context/output/batch limits")
        if (not isinstance(chunked_prefill, bool) or max_batched_tokens < max_seqs
                or (not chunked_prefill and max_batched_tokens < maximum)):
            raise ValueError("Invalid worker prefill token budget/chunking configuration")
        stage = "preflight"
        from transformers import AutoTokenizer

        tokenizer = AutoTokenizer.from_pretrained(config["model_path"], local_files_only=True)
        tasks = []
        keys = set()
        with tasks_file.open(encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, 1):
                if not line.strip():
                    continue
                task = json.loads(line)
                key = task.get("key")
                if not isinstance(key, str) or not key or key in keys:
                    raise ValueError(f"Invalid/duplicate task key at line {line_number}")
                keys.add(key)
                messages = task.get("messages")
                if (not isinstance(messages, list) or not messages
                        or any(not isinstance(item, dict) or not isinstance(item.get("role"), str)
                               or not isinstance(item.get("content"), str) for item in messages)):
                    raise ValueError(f"Invalid judge messages at line {line_number}")
                tokens = tokenizer.apply_chat_template(
                    messages, tokenize=True, add_generation_prompt=True, enable_thinking=False,
                )
                if not isinstance(tokens, list) or not tokens:
                    raise ValueError("Judge tokenizer did not return a nonempty token list")
                if len(tokens) + max_output > maximum:
                    raise ValueError(
                        f"Judge input too long for task {key}: prompt={len(tokens)}, "
                        f"output_budget={max_output}, window={maximum}; no text was truncated"
                    )
                tasks.append((key, tokens))
        if not tasks:
            print("[Local judge] No pending tasks; model was not loaded", file=sys.stderr, flush=True)
            return 0
        print(f"[Local judge] Preflight passed: {len(tasks)} tasks; max input "
              f"{max(len(tokens) for _, tokens in tasks)} tokens", file=sys.stderr, flush=True)
        stage = "model_startup"
        from vllm import LLM, SamplingParams

        model = LLM(
            model=config["model_path"], tokenizer=config["model_path"],
            dtype=config.get("dtype", "bfloat16"),
            tensor_parallel_size=int(config.get("tensor_parallel_size", 1)),
            gpu_memory_utilization=float(config["gpu_memory_utilization"]),
            max_model_len=maximum, max_num_seqs=max_seqs,
            max_num_batched_tokens=max_batched_tokens,
            enable_chunked_prefill=chunked_prefill,
            enforce_eager=bool(config.get("enforce_eager", True)),
            distributed_executor_backend="mp",
            seed=int(config.get("seed", 42)), generation_config="vllm",
            disable_log_stats=True,
        )
        sampling = SamplingParams(
            temperature=0.0, top_p=1.0, max_tokens=max_output,
            seed=int(config.get("seed", 42)),
        )
        stage = "generation"
        started = time.monotonic()
        for start in range(0, len(tasks), max_seqs):
            batch = tasks[start:start + max_seqs]
            outputs = model.generate(
                [{"prompt_token_ids": tokens} for _, tokens in batch], sampling, use_tqdm=False,
            )
            if len(outputs) != len(batch):
                raise RuntimeError("Local model returned a different number of outputs than tasks")
            for (key, tokens), output in zip(batch, outputs, strict=True):
                if len(output.outputs) != 1:
                    raise RuntimeError("Local judge expected exactly one completion per task")
                completion = output.outputs[0]
                _append_result(results_file, {
                    "key": key, "text": completion.text,
                    "finish_reason": completion.finish_reason,
                    "prompt_tokens": len(tokens), "completion_tokens": len(completion.token_ids),
                })
            done = min(start + len(batch), len(tasks))
            elapsed = max(time.monotonic() - started, 0.001)
            rate = done / elapsed
            eta = (len(tasks) - done) / rate
            print(f"[Local judge] {done}/{len(tasks)} ({done / len(tasks):.1%}) "
                  f"{rate:.2f} judgments/s ETA {eta:.0f}s", file=sys.stderr, flush=True)
        return 0
    except Exception as error:
        memory_error = _is_memory_error(error)
        failure = {"stage": stage, "error_type": type(error).__name__,
                   "message": str(error), "retryable_memory": memory_error}
        error_file.parent.mkdir(parents=True, exist_ok=True)
        error_file.write_text(json.dumps(failure, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[Local judge] {stage}: {type(error).__name__}: {error}", file=sys.stderr, flush=True)
        traceback.print_exc(file=sys.stderr)
        return 42 if memory_error else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    return run_worker(config)


if __name__ == "__main__":
    raise SystemExit(main())
