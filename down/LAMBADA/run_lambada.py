#!/usr/bin/env python3
"""LAMBADA, zero-shot, using the official lm-evaluation-harness task.

Normally change only MODEL_PATH below, then: python down/LAMBADA/run_lambada.py
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import re
import sys
import time
import uuid


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

# 日常只改 MODEL_PATH：相对路径以项目根目录为基准，也支持服务器绝对路径。
MODEL_PATH = "checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_new/gad/global_step_1813/actor/huggingface"

# 指定学生基座 tokenizer；设为 None 时改用模型导出目录。不要使用教师 tokenizer。
TOKENIZER_PATH = "/shared/public_models/Qwen2.5-0.5B"
DEVICE = "cuda:0"  # CUDA_VISIBLE_DEVICES=3 时，这里仍为 cuda:0。
BATCH_SIZE = 8  # 显存不足先改成 1；不改变任务/指标定义。
DTYPE = "auto"
MAX_LENGTH = 2048
SEED = 42
LIMIT = None  # None = 全量；改成 8 可试跑。也支持 --limit 8。
RESULTS_DIR = HERE / "results"
EXPECTED_HARNESS_VERSION = "0.4.9.2"
TASK = "lambada_openai"
DATASET_PATH = "EleutherAI/lambada_openai"
DATASET_NAME = "default"
EVAL_SPLIT = "test"
EXPECTED_EXAMPLES = 5153


def local_path(value: str | Path) -> Path:
    path = Path(value).expanduser()
    return (path if path.is_absolute() else ROOT / path).resolve()


def check_model_files(model_path: Path, tokenizer_path: Path) -> None:
    if not (model_path / "config.json").is_file():
        raise FileNotFoundError(
            f"模型目录不存在或缺少 config.json: {model_path}\n"
            "请指向包含完整 Hugging Face 权重的目录，不能直接使用 FSDP 分片目录。"
        )
    config = json.loads((model_path / "config.json").read_text(encoding="utf-8"))
    if config.get("is_encoder_decoder", False):
        raise ValueError("此入口用于 Qwen 等 decoder-only causal LM。")
    indexes = [model_path / name for name in (
        "model.safetensors.index.json", "pytorch_model.bin.index.json"
    ) if (model_path / name).is_file()]
    if indexes:
        for index in indexes:
            weight_map = json.loads(index.read_text(encoding="utf-8")).get("weight_map", {})
            if not weight_map:
                raise ValueError(f"权重索引缺少 weight_map: {index}")
            missing = [name for name in set(weight_map.values()) if not (model_path / name).is_file()]
            if missing:
                raise FileNotFoundError(f"模型导出不完整，缺少权重分片: {missing}")
    elif not any((model_path / name).is_file() for name in ("model.safetensors", "pytorch_model.bin")):
        raise FileNotFoundError(f"未找到完整模型权重或分片索引: {model_path}")
    if not tokenizer_path.is_dir():
        raise FileNotFoundError(f"tokenizer 目录不存在: {tokenizer_path}")
    if not any((tokenizer_path / name).is_file() for name in (
        "tokenizer.json", "vocab.json", "tokenizer.model", "spiece.model"
    )):
        raise FileNotFoundError(
            f"目录缺少 tokenizer 文件: {tokenizer_path}\n"
            "请补齐导出文件，或将 TOKENIZER_PATH 指向相同学生基座的本地目录。"
        )


def package_versions() -> dict:
    versions = {}
    for name in ("lm_eval", "torch", "transformers", "datasets", "accelerate", "tokenizers"):
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = "not installed"
    return versions


def validate_dataset(data) -> None:
    """Check the exact labeled completion split consumed by the official task."""
    rows = data[EVAL_SPLIT]
    if len(rows) != EXPECTED_EXAMPLES:
        raise ValueError(f"LAMBADA test 应为 {EXPECTED_EXAMPLES} 题，读取到 {len(rows)} 题。")
    for index, row in enumerate(rows):
        text = row.get("text")
        if not isinstance(text, str) or not text.strip() or len(text.split(" ")) < 2:
            raise ValueError(f"LAMBADA 第 {index} 题缺少有效上下文及目标末词。")
        if not text.split(" ")[-1] or not " ".join(text.split(" ")[:-1]).strip():
            raise ValueError(f"LAMBADA 第 {index} 题的上下文或末词为空；不静默改写官方文本。")


def validate_results(result: dict, limit: int | None) -> tuple[dict, list]:
    """Validate greedy last-word accuracy and exp(-mean(target-word log P))."""
    metrics = result["results"][TASK]
    counts = result["n-samples"][TASK]
    rows = result["samples"][TASK]
    total = int(counts["original"])
    expected = total if limit is None else min(limit, total)
    if total != EXPECTED_EXAMPLES or int(counts["effective"]) != expected or len(rows) != expected:
        raise ValueError(f"样本覆盖不完整: original={total}, effective={counts['effective']}, saved={len(rows)}; full={EXPECTED_EXAMPLES}")
    ids = [row["doc_id"] for row in rows]
    if len(set(ids)) != expected:
        raise ValueError("逐题结果包含重复 doc_id。")
    accuracy = float(metrics["acc,none"])
    values = [float(row["acc"]) for row in rows]
    if any(value not in (0.0, 1.0) for value in values):
        raise ValueError("acc 逐题结果必须为 0 或 1。")
    if not math.isfinite(accuracy) or not 0 <= accuracy <= 1 or not math.isclose(accuracy, sum(values) / expected, abs_tol=1e-12):
        raise ValueError(f"acc 汇总与逐题结果不一致: {accuracy}")
    # In harness 0.4.9.2 sample['perplexity'] contains log P(target word),
    # not exp(-log P). A word can span multiple model tokens; their log Ps sum.
    loglikelihoods = [float(row["perplexity"]) for row in rows]
    if any(not math.isfinite(value) or value > 1e-6 for value in loglikelihoods):
        raise ValueError("目标末词 loglikelihood 必须为有限非正数。")
    mean_nll = -sum(loglikelihoods) / expected
    try:
        recomputed = math.exp(mean_nll)
    except OverflowError as error:
        raise ValueError("末词 PPL 上溢；不保存无穷值为成功结果。") from error
    perplexity = float(metrics["perplexity,none"])
    if not math.isfinite(perplexity) or perplexity < 1 - 1e-6 or not math.isclose(perplexity, recomputed, rel_tol=1e-10, abs_tol=1e-10):
        raise ValueError(f"perplexity 汇总与逐题末词 loglikelihood 不一致: {perplexity}; recomputed={recomputed}")
    summary = {
        "total_test_examples": total, "evaluated_examples": expected, "limited_run": limit is not None,
        "acc": accuracy, "acc_percent": 100 * accuracy, "acc_correct": int(sum(values)),
        "acc_stderr": metrics.get("acc_stderr,none"), "perplexity": perplexity,
        "perplexity_stderr": metrics.get("perplexity_stderr,none"), "mean_target_word_nll": mean_nll,
        "perplexity_definition": "exp(-mean(sum_token_logprob_of_target_last_word))",
        "perplexity_higher_is_better": False,
    }
    return summary, rows


def save_results(result: dict, summary: dict, model_path: Path, serializer) -> Path:
    try:
        model_name = model_path.relative_to(ROOT).as_posix()
    except ValueError:
        model_name = model_path.as_posix()
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "_", model_name)[-64:]
    tag = hashlib.sha256(str(model_path).encode()).hexdigest()[:8]
    stamp = datetime.now(timezone(timedelta(hours=8))).strftime("%Y%m%d-%H%M%S")
    output = RESULTS_DIR / f"{slug}-{tag}" / f"{stamp}-{uuid.uuid4().hex[:8]}"
    output.mkdir(parents=True, exist_ok=False)
    samples = result["samples"][TASK]
    with (output / "samples.jsonl").open("w", encoding="utf-8") as stream:
        for sample in samples:
            stream.write(json.dumps(sample, ensure_ascii=False, default=serializer) + "\n")
    # Preserve harness metadata/configs without duplicating the large sample log.
    aggregate = {key: value for key, value in result.items() if key != "samples"}
    for name, payload in (("harness_results.json", aggregate), ("summary.json", summary)):
        (output / name).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, default=serializer) + "\n", encoding="utf-8"
        )
    report = (
        f"# LAMBADA {'LIMITED RUN' if summary['limited_run'] else 'full test'}\n\n"
        f"- Model: `{model_path}`\n"
        f"- Tokenizer: `{summary['tokenizer_path']}`\n"
        f"- Protocol: 0-shot, plain completion, no chat template, no decoding watermark\n"
        f"- Examples: {summary['evaluated_examples']} / {summary['total_test_examples']}\n"
        f"- Harness: {summary['versions']['lm_eval']}\n\n"
        "| Metric | Score | Direction |\n|---|---:|---|\n"
        f"| acc (%) | {summary['acc_percent']:.4f} | higher is better |\n"
        f"| target-word perplexity | {summary['perplexity']:.6f} | lower is better |\n\n"
        "PPL = exp(-mean(log P(target last word | passage prefix))).\n"
        "This is last-word perplexity, not full-text or per-model-token perplexity.\n"
        "In samples.jsonl, perplexity is the per-example target-word loglikelihood, as in the official harness.\n"
        "Limited runs are for debugging, not final paper results.\n"
    )
    (output / "report.md").write_text(report, encoding="utf-8")
    return output


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--prepare-data", action="store_true", help="只下载并检查数据集，不加载模型/GPU")
    modes.add_argument("--check-only", action="store_true", help="只检查依赖、模型文件和设备，不下载数据或推理")
    parser.add_argument("--limit", type=int, default=LIMIT, help="只评测前 N 题；省略则使用顶部 LIMIT")
    args = parser.parse_args(argv)
    if args.limit is not None and (isinstance(args.limit, bool) or not isinstance(args.limit, int) or args.limit < 1):
        parser.error("LIMIT / --limit 必须为正整数，或者在代码中设为 None")
    if sys.version_info < (3, 10):
        raise RuntimeError("此评测要求 Python >= 3.10。")

    # Share the normal Hugging Face cache with the server's other scripts.
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    if args.prepare_data:
        from datasets import load_dataset
        print(f"[Data] Downloading {DATASET_PATH} / {DATASET_NAME}", flush=True)
        data = load_dataset(DATASET_PATH, DATASET_NAME)
        print(f"[Data] Cached splits: {dict((name, len(split)) for name, split in data.items())}")
        validate_dataset(data)
        print("[OK] 数据已缓存；正式评测请使用同一环境、用户和 Hugging Face 缓存目录。")
        return 0

    model_path = local_path(MODEL_PATH)
    tokenizer_path = local_path(TOKENIZER_PATH) if TOKENIZER_PATH is not None else model_path
    check_model_files(model_path, tokenizer_path)
    versions = package_versions()
    if versions["lm_eval"] != EXPECTED_HARNESS_VERSION:
        raise RuntimeError(
            f"需要 lm_eval=={EXPECTED_HARNESS_VERSION}，当前为 {versions['lm_eval']}。\n"
            "请运行: python -m pip install -r down/LAMBADA/requirements.txt"
        )
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from lm_eval import simple_evaluate
    from lm_eval.models.huggingface import HFLM
    from lm_eval.utils import handle_non_serializable

    if int(os.environ.get("WORLD_SIZE", "1")) != 1:
        raise RuntimeError("本入口使用单进程单卡，请直接用 python 运行，不使用 torchrun/多卡 accelerate。")
    if DEVICE.startswith("cuda"):
        index = torch.device(DEVICE).index or 0
        if not torch.cuda.is_available() or index >= torch.cuda.device_count():
            raise RuntimeError(f"CUDA 设备不可用: {DEVICE}；请检查 PyTorch/CUDA 和 CUDA_VISIBLE_DEVICES。")
    tokenizer = AutoTokenizer.from_pretrained(str(tokenizer_path), local_files_only=True, trust_remote_code=False)
    print(f"[Model] {model_path}\n[Tokenizer] {tokenizer_path}", flush=True)
    print(f"[Protocol] LAMBADA test, 0-shot, completion, limit={args.limit}", flush=True)
    print(f"[Device] {DEVICE}, batch_size={BATCH_SIZE}, dtype={DTYPE}", flush=True)
    if args.check_only:
        print("[OK] 依赖可导入、模型文件和 tokenizer 可读取、设备可用；尚未加载权重/数据或推理。")
        return 0

    started = time.monotonic()
    # lm-eval 0.4.9.2 passes dtype= to Transformers internally, whereas older
    # Transformers 4.x consumes torch_dtype=. Preload with the compatible public
    # API, then use HFLM's supported pre-initialized-model path (no second load).
    model = AutoModelForCausalLM.from_pretrained(
        str(model_path), torch_dtype=DTYPE, local_files_only=True,
        trust_remote_code=False, low_cpu_mem_usage=True,
    ).to(DEVICE)
    model.eval()
    lm = HFLM(
        pretrained=model, tokenizer=tokenizer, backend="causal",
        batch_size=BATCH_SIZE, max_length=MAX_LENGTH,
    )
    result = simple_evaluate(
        model=lm, tasks=[TASK], num_fewshot=0, batch_size=BATCH_SIZE, device=DEVICE,
        limit=args.limit, log_samples=True, apply_chat_template=False,
        random_seed=SEED, numpy_random_seed=SEED, torch_random_seed=SEED,
        fewshot_random_seed=SEED, bootstrap_iters=0,
    )
    if result is None:
        raise RuntimeError("Harness 未返回评测结果。")
    summary, _ = validate_results(result, args.limit)
    summary.update({
        "model_path": str(model_path), "tokenizer_path": str(tokenizer_path),
        "task": TASK, "dataset_path": DATASET_PATH, "dataset_name": DATASET_NAME,
        "split": EVAL_SPLIT, "num_fewshot": 0, "apply_chat_template": False,
        "watermark_at_inference": False, "output_type": "loglikelihood",
        "target_definition": "space_plus_last_word", "normalization": "none",
        "device": DEVICE, "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        "batch_size": BATCH_SIZE, "dtype_requested": DTYPE, "max_length": MAX_LENGTH,
        "model_loader": "transformers_torch_dtype_preloaded",
        "seed": SEED, "versions": versions, "elapsed_seconds": time.monotonic() - started,
    })
    output = save_results(result, summary, model_path, handle_non_serializable)
    print(f"\n[{'LIMITED RUN' if args.limit is not None else 'FULL TEST'}] {summary['evaluated_examples']} examples")
    print(f"acc      = {summary['acc']:.6f} ({summary['acc_percent']:.4f}%)")
    print(f"perplexity = {summary['perplexity']:.6f} (lower is better)")
    print(f"[Saved] {output}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, RuntimeError, ImportError, KeyError) as error:
        print(f"[FAILED] {type(error).__name__}: {error}", file=sys.stderr)
        print("排查：依赖见 down/LAMBADA/README.md；下载失败先运行 --prepare-data；显存不足降低 BATCH_SIZE。", file=sys.stderr)
        raise SystemExit(1)
