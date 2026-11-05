"""Generate LSH teacher data, or unwatermarked student/base answers, with scores.

Run from the project root: python baseline_lsh/generate.py --help
All non-teacher_response Arrow columns/types/metadata are preserved exactly.
"""
from __future__ import annotations

import argparse
from importlib import metadata
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from baseline_lsh.core import BucketAsset, LSHConfig, LSHLogitsProcessor, LSHWatermark, VERSION, canonical, sha256_file
from baseline_lsh.io_utils import (atomic_json, ensure_manifest, prompt_ids, read_json, read_part,
                                   commit_part, run_lock, validate_preserved, validate_source)


def parse_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", type=Path, default=Path("data/dolly15k_train.parquet"))
    p.add_argument("--model", type=Path, default=Path("/shared/public_models/Qwen2.5-14B-Instruct"))
    p.add_argument("--asset", type=Path, default=Path("baseline_lsh/assets/qwen2_5_14b_lsh4_seed42.npz"))
    p.add_argument("--tokenizer", type=Path, help="Original teacher tokenizer (default: asset's teacher path)")
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--score-output", type=Path, help="Default: <output stem>_lsh_scores.jsonl")
    p.add_argument("--watermark", choices=["lsh", "none"], default="lsh",
                   help="Use none to measure student/base inheritance without inference-time watermarking")
    p.add_argument("--gamma", type=float, default=0.5)
    p.add_argument("--delta", type=float, default=3.0, help="Fixed additive logit bias; configurable, e.g. 3 or 6")
    p.add_argument("--hash-key", type=int, default=15_485_863)
    p.add_argument("--partition", choices=["balanced", "global"], default="balanced")
    p.add_argument("--batch-size", type=int, default=8)
    p.add_argument("--shard-size", type=int, default=64)
    p.add_argument("--start", type=int, default=0)
    p.add_argument("--limit", type=int)
    p.add_argument("--max-prompt-tokens", type=int, default=2048)
    p.add_argument("--max-new-tokens", type=int, default=1536)
    p.add_argument("--score-max-tokens", type=int)
    p.add_argument("--temperature", type=float, default=0.7)
    p.add_argument("--top-p", type=float, default=0.9)
    p.add_argument("--top-k", type=int, default=-1)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--num-gpus", type=int, default=1, help="Independent data-parallel workers; set CUDA_VISIBLE_DEVICES explicitly")
    p.add_argument("--tensor-parallel-size", type=int, default=1)
    p.add_argument("--gpu-memory-utilization", type=float, default=0.85)
    p.add_argument("--dtype", choices=["bfloat16", "float16", "auto"], default="bfloat16")
    p.add_argument("--preflight", action="store_true", help="Check data/assets/local model/tokenizers; no weights loaded, no CUDA generation")
    p.add_argument("--worker-rank", type=int, help=argparse.SUPPRESS)
    p.add_argument("--worker-count", type=int, help=argparse.SUPPRESS)
    a = p.parse_args(argv)
    a.cli_argv = list(sys.argv[1:] if argv is None else argv)
    LSHConfig(a.gamma, a.delta, a.hash_key, a.partition)
    if min(a.batch_size, a.shard_size, a.max_prompt_tokens, a.max_new_tokens, a.num_gpus, a.tensor_parallel_size) <= 0:
        p.error("batch/shard/token/GPU counts must be positive")
    if a.start < 0 or (a.limit is not None and a.limit <= 0) or (a.score_max_tokens is not None and a.score_max_tokens <= 0):
        p.error("start must be nonnegative; limit/score-max-tokens positive")
    if not 0 <= a.temperature <= 2 or not 0 < a.top_p <= 1 or (a.top_k != -1 and a.top_k < 1):
        p.error("invalid temperature/top-p/top-k")
    if a.seed < 0 or not 0 < a.gpu_memory_utilization < 1:
        p.error("seed must be nonnegative; GPU memory utilization must be in (0,1)")
    if a.num_gpus > 1 and a.tensor_parallel_size != 1:
        p.error("use either data-parallel num-gpus or tensor-parallel-size")
    for k in ("input", "model", "asset", "output"):
        setattr(a, k, getattr(a, k).resolve())
    a.score_output = (a.score_output or a.output.with_name(a.output.stem + "_lsh_scores.jsonl")).resolve()
    if len({a.input, a.output, a.score_output, a.asset}) != 4:
        p.error("input, output, score-output and asset must be distinct paths")
    if a.output.suffix != ".parquet" or a.score_output.suffix != ".jsonl":
        p.error("output must be .parquet and score-output .jsonl")
    if (a.worker_rank is None) != (a.worker_count is None):
        p.error("internal worker arguments must be paired")
    if a.worker_rank is not None and not 0 <= a.worker_rank < a.worker_count:
        p.error("invalid worker rank")
    return a


def runtime_versions():
    result = {"python": sys.version.split()[0]}
    for name in ("numpy", "pyarrow", "torch", "transformers", "vllm"):
        try:
            result[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            result[name] = None
    return result


def model_identity(model):
    if not (model / "config.json").is_file():
        raise FileNotFoundError(f"local HF model config not found: {model / 'config.json'}")
    weights = sorted(model.glob("*.safetensors")) or sorted(model.glob("pytorch_model*.bin"))
    if not weights:
        raise FileNotFoundError(f"no local model weights under {model}")
    # A drift guard, not a claim to cryptographically hash the entire 28GB model.
    return {"path": str(model), "config_sha256": sha256_file(model / "config.json"),
            "weight_files_size_mtime": [{"name": f.name, "size": f.stat().st_size, "mtime_ns": f.stat().st_mtime_ns} for f in weights]}


def build_spec(a, source, wm, tokenizer):
    fields = ("watermark", "batch_size", "shard_size", "start", "limit", "max_prompt_tokens", "max_new_tokens",
              "score_max_tokens", "temperature", "top_p", "top_k", "seed", "dtype", "gpu_memory_utilization",
              "tensor_parallel_size")
    code = Path(__file__).parent
    return {"version": VERSION, "input": str(a.input), "input_sha256": sha256_file(a.input),
            "input_rows": source.num_rows, "schema_sha256": __import__("hashlib").sha256(source.schema.serialize().to_pybytes()).hexdigest(),
            "model": model_identity(a.model), "tokenizer": str(a.tokenizer),
            "watermark_config": wm.descriptor(), "generation": {k: getattr(a, k) for k in fields},
            "runtime": runtime_versions(),
            "source_code": {n: sha256_file(code / n) for n in ("core.py", "io_utils.py", "generate.py")}}


def shards(a, total):
    if a.start >= total:
        raise ValueError("start is beyond the input row count")
    end = total if a.limit is None else min(total, a.start + a.limit)
    return [(i, start, min(a.shard_size, end - start)) for i, start in enumerate(range(a.start, end, a.shard_size))]


def generate_shard(a, source, global_start, tokenizer, wm, llm, params_factory):
    """Dependency-injected engine entry for CPU contract tests."""
    import pyarrow as pa
    values, scores = [], []
    processor = LSHLogitsProcessor(wm) if a.watermark == "lsh" else None
    rows = source.to_pylist()
    for offset in range(0, len(rows), a.batch_size):
        mini = rows[offset:offset + a.batch_size]
        prompts = [prompt_ids(tokenizer, r["content"], a.max_prompt_tokens) for r in mini]
        params = [params_factory(n=1, temperature=a.temperature, top_p=a.top_p, top_k=a.top_k,
                                 max_tokens=a.max_new_tokens, seed=a.seed + global_start + offset + j,
                                 skip_special_tokens=True, logits_processors=[processor] if processor else None)
                  for j in range(len(mini))]
        requests = llm.generate([{"prompt_token_ids": ids} for ids in prompts], sampling_params=params, use_tqdm=False)
        if len(requests) != len(mini):
            raise RuntimeError("vLLM returned the wrong number of requests")
        for j, (row, context, request) in enumerate(zip(mini, prompts, requests)):
            if len(request.outputs) != 1:
                raise RuntimeError("expected exactly one completion per input")
            if list(request.prompt_token_ids) != context:
                raise RuntimeError("vLLM prompt tokenization drifted")
            output = request.outputs[0]
            text, raw_ids = output.text, [int(i) for i in output.token_ids]
            if not isinstance(text, str) or not text.strip() or not raw_ids:
                raise RuntimeError(f"empty teacher response for id={row['id']!r}")
            text_ids = tokenizer.encode(text, add_special_tokens=False)
            values.append(text)  # No strip: preserve leading spaces and line breaks.
            score = {"id": row["id"], "label": a.watermark,
                     "is_watermarked": True if a.watermark == "lsh" else None,
                     "watermark_enabled_during_generation": a.watermark == "lsh",
                     "finish_reason": output.finish_reason, "stop_reason": output.stop_reason,
                     "generation_seed": a.seed + global_start + offset + j,
                     "prompt_last_token_id": context[-1], "generated_token_ids": raw_ids,
                     "text_token_ids_match": raw_ids == text_ids,
                     "generation_score": wm.score(raw_ids, context, a.score_max_tokens),
                     **wm.score(text_ids, context, a.score_max_tokens)}
            scores.append(score)
        print(f"[generate+score] rows {global_start + offset}:{global_start + offset + len(mini)}", flush=True)
    field = source.schema.field("teacher_response")
    generated = source.set_column(source.schema.get_field_index("teacher_response"), field, pa.array(values, type=field.type))
    validate_preserved(source, generated)
    return generated, scores


def run_worker(a, source, tokenizer, wm, directory, plan):
    rank, count = a.worker_rank or 0, a.worker_count or 1
    pending = []
    for index, start, size in plan:
        if index % count != rank:
            continue
        part_source = source.slice(start, size)
        if read_part(directory, index, part_source) is None:
            pending.append((index, start, size))
        else:
            print(f"[resume] committed shard {index}", flush=True)
    if not pending:
        return
    # Keep the existing project's vLLM 0.8.x V0 backend contract.
    os.environ["VLLM_USE_V1"] = "0"
    from vllm import LLM, SamplingParams
    llm = LLM(model=str(a.model), tokenizer=str(a.tokenizer), tensor_parallel_size=a.tensor_parallel_size,
              dtype=a.dtype, gpu_memory_utilization=a.gpu_memory_utilization,
              max_model_len=a.max_prompt_tokens + a.max_new_tokens, max_num_seqs=a.batch_size,
              enforce_eager=True, disable_log_stats=True)
    for index, start, size in pending:
        original = source.slice(start, size)
        generated, scores = generate_shard(a, original, start, tokenizer, wm, llm, SamplingParams)
        commit_part(directory, index, original, generated, scores)
        print(f"[committed] shard={index} rows={size}", flush=True)


def dispatch_workers(a, directory):
    visible = os.environ.get("CUDA_VISIBLE_DEVICES", "")
    devices = [d.strip() for d in visible.split(",") if d.strip()]
    if len(devices) != a.num_gpus or len(set(devices)) != len(devices) or "-1" in devices:
        raise ValueError("data parallel requires exactly --num-gpus distinct CUDA_VISIBLE_DEVICES entries; no other GPUs are selected")
    running = []
    try:
        for rank, device in enumerate(devices):
            log = (directory / f"worker-{rank:02d}.log").open("a", encoding="utf-8")
            env = os.environ.copy()
            env.update(CUDA_VISIBLE_DEVICES=device, PYTHONUNBUFFERED="1", VLLM_USE_V1="0")
            command = [sys.executable, str(Path(__file__).resolve()), *a.cli_argv,
                       "--worker-rank", str(rank), "--worker-count", str(a.num_gpus)]
            try:
                process = subprocess.Popen(command, env=env, stdout=log, stderr=subprocess.STDOUT,
                                           start_new_session=os.name == "posix")
            except BaseException:
                log.close()
                raise
            running.append((process, log, rank))
        while any(p.poll() is None for p, _, _ in running):
            for process, _, rank in running:
                if process.poll() not in (None, 0):
                    raise RuntimeError(f"worker {rank} failed; see {directory / f'worker-{rank:02d}.log'}")
            completed = len(list(directory.glob("part-*.done.json")))
            print(f"[multi-GPU] committed shards={completed}; logs={directory}", flush=True)
            time.sleep(5)
        for process, _, rank in running:
            if process.returncode:
                raise RuntimeError(f"worker {rank} failed; inspect its log")
    finally:
        for process, log, _ in running:
            if process.poll() is None:
                if os.name == "posix":
                    # Only the session created for this worker and its vLLM children.
                    try:
                        os.killpg(process.pid, signal.SIGTERM)
                    except ProcessLookupError:
                        pass
                else:
                    process.terminate()
        for process, log, _ in running:
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            log.close()


def finalize(a, source, directory, plan, spec):
    import pyarrow.parquet as pq
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.score_output.parent.mkdir(parents=True, exist_ok=True)
    data_tmp = a.output.with_name(a.output.name + ".tmp")
    score_tmp = a.score_output.with_name(a.score_output.name + ".tmp")
    length_finishes = mismatches = n = 0
    with pq.ParquetWriter(data_tmp, source.schema, compression="zstd", use_compliant_nested_type=False) as writer, score_tmp.open("w", encoding="utf-8", newline="\n") as f:
        for index, start, size in plan:
            result = read_part(directory, index, source.slice(start, size))
            if result is None:
                raise RuntimeError(f"missing committed shard {index}")
            table, rows = result
            writer.write_table(table)
            for row in rows:
                f.write(canonical(row) + "\n")
                length_finishes += row["finish_reason"] == "length"
                mismatches += not row["text_token_ids_match"]
                n += 1
    os.replace(data_tmp, a.output)
    os.replace(score_tmp, a.score_output)
    atomic_json(a.output.with_name(a.output.name + ".metadata.json"),
                {"status": "complete", "specification": spec, "rows": n, "finish_reason_length": length_finishes,
                 "raw_vs_text_token_mismatches": mismatches, "output_sha256": sha256_file(a.output),
                 "score_sha256": sha256_file(a.score_output), "score_output": str(a.score_output),
                 "score_basis": "top-level=text retokenized with teacher tokenizer; generation_score=actual generated token IDs",
                 "parts_retained": str(directory)})
    print(f"[complete] {a.output}: {n} rows; scores={a.score_output}; length finishes={length_finishes}; token roundtrip mismatches={mismatches}")


def main(argv=None):
    a = parse_args(argv)
    asset = BucketAsset.load(a.asset)
    a.tokenizer = (a.tokenizer or Path(asset.metadata["model"])).resolve()
    import pyarrow.parquet as pq
    from transformers import AutoTokenizer
    source = pq.read_table(a.input)
    validate_source(source)
    tokenizer = AutoTokenizer.from_pretrained(a.tokenizer, use_fast=True, local_files_only=True)
    asset.check_tokenizer(tokenizer)
    model_tokenizer = AutoTokenizer.from_pretrained(a.model, use_fast=True, local_files_only=True)
    # Inference uses the teacher template; model tokenizer may only differ in template.
    model_tokenizer.chat_template = tokenizer.chat_template
    asset.check_tokenizer(model_tokenizer)
    wm = LSHWatermark(asset, LSHConfig(a.gamma, a.delta, a.hash_key, a.partition))
    plan = shards(a, source.num_rows)
    # Fail before starting vLLM on malformed messages or overlong/empty templates.
    for row in source.to_pylist()[a.start:a.start + sum(s for _, _, s in plan)]:
        prompt_ids(tokenizer, row["content"], a.max_prompt_tokens)
    spec = build_spec(a, source, wm, tokenizer)
    if a.preflight:
        print(json.dumps({"status": "preflight_ok", "rows_selected": sum(s for _, _, s in plan),
                          "shards": len(plan), "asset": asset.metadata, "specification": spec,
                          "missing_runtime_packages": [k for k, v in spec["runtime"].items() if v is None]}, ensure_ascii=False, indent=2))
        return
    missing = [k for k, v in spec["runtime"].items() if v is None]
    if missing:
        raise RuntimeError(f"missing runtime packages: {missing}; use the server wm environment")
    directory = a.output.with_name(a.output.name + ".parts")
    if a.worker_rank is not None:
        if not (directory / "run.lock").exists() or read_json(directory / "manifest.json") != spec:
            raise RuntimeError("worker must be launched by a matching locked supervisor")
        run_worker(a, source, tokenizer, wm, directory, plan)
        return
    # Do not adopt or overwrite existing files without our matching provenance.
    if (a.output.exists() or a.score_output.exists()) and not (directory / "manifest.json").exists():
        raise FileExistsError("final output exists without matching resumable state; choose a new output path")
    if a.output == a.model or a.output == a.tokenizer:
        raise ValueError("output must not replace a model or tokenizer")
    with run_lock(directory):
        ensure_manifest(directory, spec)
        done = a.output.with_name(a.output.name + ".metadata.json")
        if done.exists():
            record = read_json(done)
            if (record["specification"] == spec and a.output.exists() and a.score_output.exists()
                    and record["output_sha256"] == sha256_file(a.output) and record["score_sha256"] == sha256_file(a.score_output)):
                print(f"[already complete] {a.output}")
                return
            raise ValueError("completed outputs/provenance changed; use a new output path")
        if a.num_gpus > 1:
            dispatch_workers(a, directory)
        else:
            run_worker(a, source, tokenizer, wm, directory, plan)
        finalize(a, source, directory, plan, spec)


if __name__ == "__main__":
    main()
