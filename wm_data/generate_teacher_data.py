#!/usr/bin/env python3
"""Generate clean or KGW-watermarked teacher responses in EasyGAD format.

The source parquet is treated as the schema contract. Every source column and
Arrow type is retained exactly; only ``teacher_response`` is replaced.
Generation and KGW detection are performed in the same resumable job. Two
files are finalized atomically: the strict EasyGAD parquet and a per-row score
JSONL for later AUROC calculation.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Iterator

# EasyGAD's external-launcher integration is compatible with vLLM V0. vLLM
# 0.8.5 V1 can incorrectly report zero KV-cache blocks in this environment.
os.environ["VLLM_USE_V1"] = "0"

import pyarrow as pa
import pyarrow.parquet as pq
from transformers import AutoTokenizer
from tqdm.auto import tqdm
from vllm import LLM, SamplingParams

from kgw import KGWConfig, KGWLogitsProcessor, kgw_score


def parse_args(default_watermark: str | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Source EasyGAD parquet")
    parser.add_argument("--output", required=True, type=Path, help="Final output parquet")
    parser.add_argument(
        "--score-output",
        type=Path,
        default=None,
        help="Per-row KGW score JSONL (default: <output stem>_kgw_scores.jsonl)",
    )
    parser.add_argument(
        "--model",
        default="/shared/public_models/Qwen2.5-0.5B",
        help="Teacher model path",
    )
    parser.add_argument(
        "--watermark",
        choices=("none", "kgw"),
        default=default_watermark or "none",
    )
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--shard-size", type=int, default=256)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--max-prompt-tokens", type=int, default=2048)
    parser.add_argument("--max-new-tokens", type=int, default=1536)
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--top-p", type=float, default=0.9)
    parser.add_argument("--top-k", type=int, default=-1)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--tensor-parallel-size", type=int, default=1)
    parser.add_argument(
        "--num-gpus",
        type=int,
        default=1,
        help="Number of independent GPUs used for data-parallel generation",
    )
    parser.add_argument("--gpu-memory-utilization", type=float, default=0.85)
    parser.add_argument("--gamma", type=float, default=0.25)
    parser.add_argument("--delta", type=float, default=2.0)
    parser.add_argument("--hash-key", type=int, default=15_485_863)
    parser.add_argument(
        "--kgw-max-tokens",
        type=int,
        default=None,
        help="Optionally score only the first N response tokens; default scores all tokens",
    )
    parser.add_argument("--kgw-device", default="cuda")
    parser.add_argument(
        "--keep-parts",
        action="store_true",
        help="Keep intermediate resumable parts after both final parquets are complete",
    )
    parser.add_argument("--internal-worker", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Delete this output and its own part directory before starting",
    )
    return parser.parse_args()


def validate_args(args: argparse.Namespace, total_rows: int) -> tuple[int, int]:
    if args.start < 0 or args.start >= total_rows:
        raise ValueError(f"--start must be in [0, {total_rows}), got {args.start}")
    if args.limit is not None and args.limit <= 0:
        raise ValueError("--limit must be positive")
    if args.batch_size <= 0 or args.shard_size <= 0:
        raise ValueError("batch and shard sizes must be positive")
    if args.shard_size % args.batch_size != 0:
        raise ValueError("--shard-size must be divisible by --batch-size")
    if args.max_prompt_tokens <= 0 or args.max_new_tokens <= 0:
        raise ValueError("token limits must be positive")
    if not 0.0 < args.gpu_memory_utilization < 1.0:
        raise ValueError("--gpu-memory-utilization must be in (0, 1)")
    if args.num_gpus <= 0:
        raise ValueError("--num-gpus must be positive")
    end = total_rows if args.limit is None else min(total_rows, args.start + args.limit)
    return args.start, end


def iter_range(
    parquet_file: pq.ParquetFile,
    start: int,
    end: int,
    shard_size: int,
) -> Iterator[tuple[int, pa.Table]]:
    cursor = 0
    for batch in parquet_file.iter_batches(batch_size=shard_size):
        batch_end = cursor + batch.num_rows
        left, right = max(start, cursor), min(end, batch_end)
        if left < right:
            table = pa.Table.from_batches([batch]).slice(left - cursor, right - left)
            yield left, table
        cursor = batch_end
        if cursor >= end:
            break


def render_prompts(tokenizer, rows: list[dict], max_prompt_tokens: int) -> list[str]:
    prompts: list[str] = []
    for row in rows:
        messages = row.get("content")
        if not isinstance(messages, list) or not messages:
            raise ValueError(f"invalid content messages for row id={row.get('id')!r}")
        prompt = tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=False,
        )
        prompt_ids = tokenizer.encode(prompt, add_special_tokens=False)
        if len(prompt_ids) > max_prompt_tokens:
            prompt_ids = prompt_ids[:max_prompt_tokens]
            prompt = tokenizer.decode(prompt_ids, skip_special_tokens=False)
        prompts.append(prompt)
    return prompts


def sampling_params_for_rows(
    args: argparse.Namespace,
    global_indices: list[int],
    kgw_processor: KGWLogitsProcessor | None,
) -> list[SamplingParams]:
    params = []
    for index in global_indices:
        params.append(
            SamplingParams(
                n=1,
                temperature=args.temperature,
                top_p=args.top_p,
                top_k=args.top_k,
                max_tokens=args.max_new_tokens,
                seed=args.seed + index,
                skip_special_tokens=True,
                logits_processors=[kgw_processor] if kgw_processor else None,
            )
        )
    return params


def generate_shard(
    llm: LLM,
    tokenizer,
    table: pa.Table,
    global_start: int,
    args: argparse.Namespace,
    kgw_processor: KGWLogitsProcessor | None,
    progress: tqdm | None = None,
) -> pa.Table:
    rows = table.to_pylist()
    generated: list[str] = []
    for offset in range(0, len(rows), args.batch_size):
        mini_rows = rows[offset : offset + args.batch_size]
        prompts = render_prompts(tokenizer, mini_rows, args.max_prompt_tokens)
        indices = list(range(global_start + offset, global_start + offset + len(mini_rows)))
        requests = llm.generate(
            prompts,
            sampling_params=sampling_params_for_rows(args, indices, kgw_processor),
            use_tqdm=False,
        )
        for request, row in zip(requests, mini_rows, strict=True):
            # Preserve the exact decoded text. Stripping a leading whitespace or
            # newline changes the first token and breaks KGW's chained context.
            text = request.outputs[0].text
            if not text.strip():
                raise RuntimeError(f"teacher generated an empty response for id={row.get('id')!r}")
            generated.append(text)
        if progress is not None:
            progress.update(len(mini_rows))

    teacher_index = table.schema.get_field_index("teacher_response")
    if teacher_index < 0:
        raise ValueError("source parquet has no teacher_response column")
    replacement = pa.array(generated, type=table.schema.field(teacher_index).type)
    return table.set_column(teacher_index, "teacher_response", replacement)


def build_score_schema(args: argparse.Namespace) -> pa.Schema:
    detector_metadata = {
        "generated_output": str(args.output),
        "input": str(args.input),
        "model": args.model,
        "generation_mode": args.watermark,
        "gamma": args.gamma,
        "delta": args.delta,
        "hash_key": args.hash_key,
        "seeding": "simple_1",
        "max_tokens": args.kgw_max_tokens,
        "device": args.kgw_device,
        "sampling": {
            "temperature": args.temperature,
            "top_p": args.top_p,
            "top_k": args.top_k,
            "max_prompt_tokens": args.max_prompt_tokens,
            "max_new_tokens": args.max_new_tokens,
            "seed": args.seed,
        },
    }
    return pa.schema(
        [
            pa.field("id", pa.string(), nullable=False),
            pa.field("label", pa.string(), nullable=False),
            pa.field("is_watermarked", pa.bool_(), nullable=False),
            pa.field("num_tokens", pa.int64(), nullable=False),
            pa.field("green_tokens", pa.int64(), nullable=False),
            pa.field("green_fraction", pa.float64(), nullable=False),
            pa.field("z_score", pa.float64(), nullable=False),
        ],
        metadata={
            b"kgw_detector": json.dumps(detector_metadata, ensure_ascii=False).encode("utf-8")
        },
    )


def score_shard(
    tokenizer,
    table: pa.Table,
    args: argparse.Namespace,
    kgw_config: KGWConfig,
    score_schema: pa.Schema,
    progress: tqdm | None = None,
) -> pa.Table:
    rows = table.to_pylist()
    prompts = render_prompts(tokenizer, rows, args.max_prompt_tokens)
    label = "kgw" if args.watermark == "kgw" else "clean"
    scored_rows = []
    for prompt, row in zip(prompts, rows, strict=True):
        prompt_ids = tokenizer.encode(prompt, add_special_tokens=False)
        response_ids = tokenizer.encode(row["teacher_response"], add_special_tokens=False)
        score = kgw_score(
            prompt_token_ids=prompt_ids,
            generated_token_ids=response_ids,
            vocab_size=len(tokenizer),
            config=kgw_config,
            max_tokens=args.kgw_max_tokens,
            device=args.kgw_device,
        )
        scored_rows.append(
            {
                "id": row["id"],
                "label": label,
                "is_watermarked": args.watermark == "kgw",
                "num_tokens": score["num_tokens"],
                "green_tokens": score["green_tokens"],
                "green_fraction": score["green_fraction"],
                "z_score": score["z_score"],
            }
        )
        if progress is not None:
            progress.update(1)
    return pa.Table.from_pylist(scored_rows, schema=score_schema)


def valid_existing_part(path: Path, schema: pa.Schema, rows: int) -> bool:
    if not path.exists():
        return False
    part = pq.ParquetFile(path)
    return part.metadata.num_rows == rows and part.schema_arrow.equals(schema, check_metadata=True)


def merge_parts(parts: list[Path], schema: pa.Schema, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    writer = pq.ParquetWriter(temporary, schema=schema, compression="zstd")
    try:
        for part in parts:
            writer.write_table(pq.read_table(part, schema=schema))
    finally:
        writer.close()
    os.replace(temporary, output)


def write_scores_jsonl(tables: list[pa.Table], output: Path) -> None:
    """Atomically save one human-readable score object per line."""

    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        for table in tables:
            for row in table.to_pylist():
                handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
    os.replace(temporary, output)


def write_score_parts_jsonl(parts: list[Path], output: Path) -> None:
    tables = [pq.read_table(part) for part in parts]
    write_scores_jsonl(tables, output)


def gpu_inventory() -> list[dict[str, int | str]]:
    result = subprocess.run(
        [
            "nvidia-smi",
            "--query-gpu=index,name,memory.total,memory.free",
            "--format=csv,noheader,nounits",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    inventory = []
    for line in result.stdout.splitlines():
        index, name, total, free = (value.strip() for value in line.split(",", 3))
        inventory.append(
            {"gpu": int(index), "name": name, "total_mib": int(total), "free_mib": int(free)}
        )
    return inventory


def validate_single_gpu(args: argparse.Namespace) -> None:
    inventory = gpu_inventory()
    if not inventory:
        raise RuntimeError("no NVIDIA GPU was detected")
    visible = os.environ.get("CUDA_VISIBLE_DEVICES")
    if visible is not None:
        entries = [value.strip() for value in visible.split(",") if value.strip()]
        if not entries or entries[0] == "-1":
            raise RuntimeError("CUDA_VISIBLE_DEVICES does not expose an NVIDIA GPU")
        try:
            physical_index = int(entries[0])
        except ValueError as error:
            raise RuntimeError(
                "single-GPU preflight requires a numeric CUDA_VISIBLE_DEVICES entry"
            ) from error
    else:
        physical_index = 0
    gpu = next((item for item in inventory if item["gpu"] == physical_index), None)
    if gpu is None:
        raise RuntimeError(f"requested GPU {physical_index} does not exist")

    requested_mib = int(gpu["total_mib"] * args.gpu_memory_utilization)
    required_mib = max(29_500, requested_mib) + 512
    if gpu["free_mib"] < required_mib:
        raise RuntimeError(
            f"GPU {physical_index} ({gpu['name']}) does not have enough free memory: "
            f"free={gpu['free_mib']} MiB, estimated required={required_mib} MiB. "
            "Choose another CUDA_VISIBLE_DEVICES value, wait for memory to be released, "
            "or lower --gpu-memory-utilization if the model still fits."
        )
    print(
        f"[GPU check] GPU {physical_index} ({gpu['name']}): free={gpu['free_mib']} MiB, "
        f"estimated required={required_mib} MiB"
    )


def select_data_parallel_gpus(
    args: argparse.Namespace,
) -> list[dict[str, float | int | str]]:
    inventory = gpu_inventory()
    by_index = {item["gpu"]: item for item in inventory}
    visible = os.environ.get("CUDA_VISIBLE_DEVICES")
    if visible:
        try:
            requested = [int(value.strip()) for value in visible.split(",") if value.strip()]
        except ValueError as error:
            raise ValueError("multi-GPU mode requires numeric CUDA_VISIBLE_DEVICES entries") from error
        candidates = [by_index[index] for index in requested if index in by_index]
        if len(candidates) < args.num_gpus:
            remaining = sorted(
                (item for item in inventory if item["gpu"] not in requested),
                key=lambda item: item["free_mib"],
                reverse=True,
            )
            candidates.extend(remaining)
    else:
        candidates = sorted(inventory, key=lambda item: item["free_mib"], reverse=True)

    selected = []
    max_model_len = args.max_prompt_tokens + args.max_new_tokens
    per_full_sequence_mib = 700.0 * max_model_len / 3584.0
    for gpu in candidates:
        if gpu["free_mib"] < 30_000:
            continue
        safe_utilization = min(
            args.gpu_memory_utilization,
            (gpu["free_mib"] - 1024) / gpu["total_mib"],
        )
        target_mib = gpu["total_mib"] * safe_utilization
        if target_mib < 29_500:
            continue
        estimated_kv_mib = max(512.0, target_mib - 29_000.0)
        weight = min(
            float(args.batch_size),
            max(1.0, estimated_kv_mib / per_full_sequence_mib),
        )
        selected.append(
            {
                **gpu,
                "utilization": round(safe_utilization, 4),
                "weight": weight,
            }
        )
        if len(selected) == args.num_gpus:
            break
    if len(selected) != args.num_gpus:
        summary = ", ".join(
            f"GPU {item['gpu']} free={item['free_mib']}MiB" for item in candidates
        )
        raise RuntimeError(
            f"only {len(selected)} GPU(s) currently have enough free memory for the model; "
            f"requested {args.num_gpus}. {summary}"
        )
    for item in selected:
        print(
            f"[GPU select] GPU {item['gpu']}: free={item['free_mib']} MiB, "
            f"worker utilization={item['utilization']}, scheduling weight={item['weight']:.2f}"
        )
    return selected


def weighted_ranges(total_rows: int, weights: list[float]) -> list[tuple[int, int]]:
    total_weight = sum(weights)
    raw = [total_rows * weight / total_weight for weight in weights]
    lengths = [int(value) for value in raw]
    remainder = total_rows - sum(lengths)
    order = sorted(
        range(len(weights)), key=lambda index: raw[index] - lengths[index], reverse=True
    )
    for index in order[:remainder]:
        lengths[index] += 1
    ranges = []
    start = 0
    for length in lengths:
        if length <= 0:
            raise ValueError("a multi-GPU worker received an empty range")
        ranges.append((start, start + length))
        start += length
    return ranges


def score_config_without_output(schema: pa.Schema) -> dict[str, object]:
    raw = (schema.metadata or {}).get(b"kgw_detector")
    if raw is None:
        raise AssertionError("score parquet is missing kgw_detector metadata")
    config = json.loads(raw.decode("utf-8"))
    config.pop("generated_output", None)
    return config


def merge_worker_outputs(
    args: argparse.Namespace,
    source_table: pa.Table,
    workers: list[dict[str, object]],
) -> None:
    data_tables = []
    score_tables = []
    common_score_fields: pa.Schema | None = None
    common_config: dict[str, object] | None = None
    expected_start = 0
    for worker in workers:
        start, end = int(worker["start"]), int(worker["end"])
        if start != expected_start:
            raise AssertionError(f"worker ranges are not contiguous at {start}:{end}")
        data = pq.read_table(worker["output"])
        scores = pq.read_table(worker["score_output"])
        expected_rows = end - start
        if data.num_rows != expected_rows or scores.num_rows != expected_rows:
            raise AssertionError(f"worker {start}:{end} row count mismatch")
        if not data.schema.equals(source_table.schema, check_metadata=True):
            raise AssertionError(f"worker {start}:{end} EasyGAD schema mismatch")
        source_slice = source_table.slice(start, expected_rows)
        for name in (name for name in data.schema.names if name != "teacher_response"):
            if not data[name].equals(source_slice[name]):
                raise AssertionError(f"worker {start}:{end} changed source column {name!r}")
        if not data["id"].equals(scores["id"]):
            raise AssertionError(f"worker {start}:{end} data and score IDs differ")
        expected_label = "kgw" if args.watermark == "kgw" else "clean"
        if set(scores["label"].to_pylist()) != {expected_label}:
            raise AssertionError(f"worker {start}:{end} has incorrect labels")
        score_fields = pa.schema(list(scores.schema))
        score_config = score_config_without_output(scores.schema)
        if common_score_fields is None:
            common_score_fields, common_config = score_fields, score_config
        elif not score_fields.equals(common_score_fields) or score_config != common_config:
            raise AssertionError(f"worker {start}:{end} score configuration mismatch")
        data_tables.append(data)
        score_tables.append(scores.replace_schema_metadata(None))
        expected_start = end

    if expected_start != source_table.num_rows:
        raise AssertionError("worker ranges do not cover the complete input")
    merged_data = pa.concat_tables(data_tables)
    merged_scores = pa.concat_tables(score_tables)
    if not merged_data["id"].equals(source_table["id"]):
        raise AssertionError("merged data IDs differ from source order")
    if not merged_data["id"].equals(merged_scores["id"]):
        raise AssertionError("merged data and score IDs differ")

    data_tmp = args.output.with_suffix(args.output.suffix + ".tmp")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(merged_data, data_tmp, compression="zstd", row_group_size=1000)
    os.replace(data_tmp, args.output)
    write_scores_jsonl([merged_scores], args.score_output)


def run_data_parallel(args: argparse.Namespace, source: pq.ParquetFile) -> None:
    if args.start != 0 or args.limit is not None:
        raise ValueError("--start/--limit cannot be combined with --num-gpus > 1")
    if args.tensor_parallel_size != 1:
        raise ValueError("data-parallel --num-gpus cannot be combined with tensor parallelism")
    selected = select_data_parallel_gpus(args)
    ranges = weighted_ranges(
        source.metadata.num_rows, [float(item["weight"]) for item in selected]
    )
    parts_dir = args.output.with_suffix(args.output.suffix + ".parts")
    legacy_score_parts = args.score_output.with_suffix(args.score_output.suffix + ".parts")
    if args.overwrite:
        args.output.unlink(missing_ok=True)
        args.score_output.unlink(missing_ok=True)
        args.output.with_suffix(args.output.suffix + ".metadata.json").unlink(missing_ok=True)
        if parts_dir.exists():
            shutil.rmtree(parts_dir)
        if legacy_score_parts.exists():
            shutil.rmtree(legacy_score_parts)
    elif args.output.exists() or args.score_output.exists():
        existing = args.output if args.output.exists() else args.score_output
        raise FileExistsError(f"output already exists: {existing}; use --overwrite to replace it")
    parts_dir.mkdir(parents=True, exist_ok=True)

    workers: list[dict[str, object]] = []
    processes: list[tuple[dict[str, object], subprocess.Popen, object]] = []
    entry_script = Path(sys.argv[0]).resolve()
    for rank, (gpu, (start, end)) in enumerate(zip(selected, ranges, strict=True)):
        worker_output = parts_dir / f"worker-{rank:02d}.parquet"
        worker_scores = parts_dir / f"worker-{rank:02d}_kgw_scores.parquet"
        worker = {
            "rank": rank,
            "gpu": int(gpu["gpu"]),
            "start": start,
            "end": end,
            "output": worker_output,
            "score_output": worker_scores,
            "log": parts_dir / f"worker-{rank:02d}.log",
        }
        workers.append(worker)
        print(
            f"[split] worker {rank}: GPU {worker['gpu']}, rows {start}:{end} "
            f"({end - start} rows)"
        )
        if worker_output.exists() and worker_scores.exists():
            print(f"[resume completed worker] {rank}")
            continue
        worker_output.unlink(missing_ok=True)
        worker_scores.unlink(missing_ok=True)
        command = [
            sys.executable,
            str(entry_script),
            "--input", str(args.input),
            "--output", str(worker_output),
            "--score-output", str(worker_scores),
            "--model", args.model,
            "--watermark", args.watermark,
            "--batch-size", str(args.batch_size),
            "--shard-size", str(args.shard_size),
            "--start", str(start),
            "--limit", str(end - start),
            "--max-prompt-tokens", str(args.max_prompt_tokens),
            "--max-new-tokens", str(args.max_new_tokens),
            "--temperature", str(args.temperature),
            "--top-p", str(args.top_p),
            "--top-k", str(args.top_k),
            "--seed", str(args.seed),
            "--tensor-parallel-size", "1",
            "--num-gpus", "1",
            "--gpu-memory-utilization", str(gpu["utilization"]),
            "--gamma", str(args.gamma),
            "--delta", str(args.delta),
            "--hash-key", str(args.hash_key),
            "--kgw-device", "cuda",
            "--internal-worker",
        ]
        if args.kgw_max_tokens is not None:
            command.extend(["--kgw-max-tokens", str(args.kgw_max_tokens)])
        log_handle = Path(worker["log"]).open("a", encoding="utf-8")
        env = os.environ.copy()
        env["CUDA_VISIBLE_DEVICES"] = str(worker["gpu"])
        env["PYTHONUNBUFFERED"] = "1"
        process = subprocess.Popen(
            command,
            cwd=entry_script.parent.parent,
            env=env,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
        )
        processes.append((worker, process, log_handle))

    generation_progress = tqdm(
        total=source.metadata.num_rows,
        desc="Generating responses",
        unit="rows",
        dynamic_ncols=True,
        position=0,
    )
    scoring_progress = tqdm(
        total=source.metadata.num_rows,
        desc="Scoring responses",
        unit="rows",
        dynamic_ncols=True,
        position=1,
    )

    def completed_rows(worker: dict[str, object], scores: bool) -> int:
        final_path = Path(worker["score_output"] if scores else worker["output"])
        if final_path.exists():
            return pq.ParquetFile(final_path).metadata.num_rows
        worker_parts = Path(worker["output"]).with_suffix(
            Path(worker["output"]).suffix + ".parts"
        )
        part_dir = worker_parts / "scores" if scores else worker_parts
        total = 0
        for part in part_dir.glob("part-*.parquet"):
            try:
                total += pq.ParquetFile(part).metadata.num_rows
            except (OSError, pa.ArrowInvalid):
                continue
        return total

    try:
        while processes:
            generation_progress.n = sum(completed_rows(worker, False) for worker in workers)
            scoring_progress.n = sum(completed_rows(worker, True) for worker in workers)
            generation_progress.refresh()
            scoring_progress.refresh()
            remaining = []
            failed: tuple[dict[str, object], int] | None = None
            for worker, process, log_handle in processes:
                code = process.poll()
                if code is None:
                    remaining.append((worker, process, log_handle))
                else:
                    log_handle.close()
                    if code != 0:
                        failed = (worker, code)
                        break
                    print(f"[worker complete] {worker['rank']} on GPU {worker['gpu']}")
            if failed:
                for _, process, log_handle in processes:
                    if process.poll() is None:
                        process.terminate()
                    if not log_handle.closed:
                        log_handle.close()
                worker, code = failed
                raise RuntimeError(
                    f"worker {worker['rank']} failed with exit code {code}; see {worker['log']}"
                )
            processes = remaining
            if processes:
                time.sleep(5)
    except KeyboardInterrupt:
        for _, process, log_handle in processes:
            process.terminate()
            log_handle.close()
        raise
    finally:
        generation_progress.n = sum(completed_rows(worker, False) for worker in workers)
        scoring_progress.n = sum(completed_rows(worker, True) for worker in workers)
        generation_progress.refresh()
        scoring_progress.refresh()
        generation_progress.close()
        scoring_progress.close()

    merge_worker_outputs(args, pq.read_table(args.input), workers)
    if not args.keep_parts:
        shutil.rmtree(parts_dir)
    print(f"done data: {args.output} ({source.metadata.num_rows} rows, schema preserved exactly)")
    print(f"done scores: {args.score_output} ({source.metadata.num_rows} per-row z-scores)")


def main(default_watermark: str | None = None) -> None:
    args = parse_args(default_watermark=default_watermark)
    args.input = args.input.resolve()
    args.output = args.output.resolve()
    args.score_output = (
        args.score_output.resolve()
        if args.score_output is not None
        else args.output.with_name(f"{args.output.stem}_kgw_scores.jsonl")
    )
    if args.score_output == args.output:
        raise ValueError("--score-output must differ from --output")
    if not args.internal_worker and args.score_output.suffix.lower() != ".jsonl":
        raise ValueError("the final --score-output must use the .jsonl extension")
    if not args.input.exists():
        raise FileNotFoundError(args.input)

    source = pq.ParquetFile(args.input)
    schema = source.schema_arrow
    expected_columns = ["id", "content", "teacher_response", "category", "grounded", "flaw", "agreement"]
    if schema.names != expected_columns:
        raise ValueError(f"unexpected source columns: {schema.names}; expected: {expected_columns}")
    start, end = validate_args(args, source.metadata.num_rows)
    if args.num_gpus > 1 and not args.internal_worker:
        run_data_parallel(args, source)
        return
    validate_single_gpu(args)

    parts_dir = args.output.with_suffix(args.output.suffix + ".parts")
    score_parts_dir = parts_dir / "scores"
    legacy_score_parts_dir = args.score_output.with_suffix(args.score_output.suffix + ".parts")
    if args.overwrite:
        args.output.unlink(missing_ok=True)
        args.score_output.unlink(missing_ok=True)
        args.output.with_suffix(args.output.suffix + ".metadata.json").unlink(missing_ok=True)
        if parts_dir.exists():
            shutil.rmtree(parts_dir)
        if legacy_score_parts_dir.exists():
            shutil.rmtree(legacy_score_parts_dir)
    elif args.output.exists() or args.score_output.exists():
        existing = args.output if args.output.exists() else args.score_output
        raise FileExistsError(f"output already exists: {existing}; use --overwrite to replace it")
    parts_dir.mkdir(parents=True, exist_ok=True)
    score_parts_dir.mkdir(parents=True, exist_ok=True)

    tokenizer = AutoTokenizer.from_pretrained(args.model, trust_remote_code=True)
    kgw_config = KGWConfig(gamma=args.gamma, delta=args.delta, hash_key=args.hash_key)
    score_schema = build_score_schema(args)
    kgw_processor = (
        KGWLogitsProcessor(vocab_size=len(tokenizer), config=kgw_config)
        if args.watermark == "kgw"
        else None
    )
    llm = LLM(
        model=args.model,
        tokenizer=args.model,
        tensor_parallel_size=args.tensor_parallel_size,
        dtype="bfloat16",
        trust_remote_code=True,
        gpu_memory_utilization=args.gpu_memory_utilization,
        max_model_len=args.max_prompt_tokens + args.max_new_tokens,
        max_num_seqs=args.batch_size,
        enforce_eager=True,
        disable_log_stats=True,
    )

    expected_parts: list[Path] = []
    expected_score_parts: list[Path] = []
    generation_progress = tqdm(
        total=end - start,
        desc="Generating responses",
        unit="rows",
        dynamic_ncols=True,
        position=0,
    )
    scoring_progress = tqdm(
        total=end - start,
        desc="Scoring responses",
        unit="rows",
        dynamic_ncols=True,
        position=1,
    )
    try:
        for global_start, table in iter_range(source, start, end, args.shard_size):
            global_end = global_start + table.num_rows
            part = parts_dir / f"part-{global_start:09d}-{global_end:09d}.parquet"
            score_part = score_parts_dir / f"part-{global_start:09d}-{global_end:09d}.parquet"
            expected_parts.append(part)
            expected_score_parts.append(score_part)
            if valid_existing_part(part, schema, table.num_rows):
                print(f"[resume] {part.name}")
                generated_table = pq.read_table(part, schema=schema)
                generation_progress.update(table.num_rows)
            else:
                generated_table = generate_shard(
                    llm=llm,
                    tokenizer=tokenizer,
                    table=table,
                    global_start=global_start,
                    args=args,
                    kgw_processor=kgw_processor,
                    progress=generation_progress,
                )
                temporary = part.with_suffix(part.suffix + ".tmp")
                pq.write_table(generated_table, temporary, compression="zstd")
                os.replace(temporary, part)

            if valid_existing_part(score_part, score_schema, table.num_rows):
                print(f"[resume score] {score_part.name}")
                scoring_progress.update(table.num_rows)
            else:
                score_table = score_shard(
                    tokenizer=tokenizer,
                    table=generated_table,
                    args=args,
                    kgw_config=kgw_config,
                    score_schema=score_schema,
                    progress=scoring_progress,
                )
                temporary = score_part.with_suffix(score_part.suffix + ".tmp")
                pq.write_table(score_table, temporary, compression="zstd")
                os.replace(temporary, score_part)
    finally:
        generation_progress.close()
        scoring_progress.close()

    merge_parts(expected_parts, schema, args.output)
    if args.internal_worker:
        merge_parts(expected_score_parts, score_schema, args.score_output)
    else:
        write_score_parts_jsonl(expected_score_parts, args.score_output)
    if not args.keep_parts:
        shutil.rmtree(parts_dir)
    print(f"done data: {args.output} ({end - start} rows, schema preserved exactly)")
    print(f"done scores: {args.score_output} ({end - start} per-row z-scores)")


if __name__ == "__main__":
    main()
