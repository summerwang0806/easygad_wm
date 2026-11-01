#!/usr/bin/env python3
"""ARC-Easy, zero-shot, using the official lm-evaluation-harness task.

Normally change only MODEL_PATH below, then: python down/ARC-Easy/run_arc_easy.py
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

# 日常只修改这里：相对路径始终以项目根目录为基准，也支持服务器绝对路径。
MODEL_PATH = "checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_new/gad/global_step_1813/actor/huggingface"

# 默认使用模型目录中的 tokenizer。若导出的权重没有 tokenizer，可改为同一学生
# 基座的本地目录，例如 /shared/public_models/Qwen2.5-0.5B；不要使用教师 tokenizer。
TOKENIZER_PATH = None
DEVICE = "cuda:0"  # CUDA_VISIBLE_DEVICES=3 时，这里仍为 cuda:0。
BATCH_SIZE = 8  # 显存不足先改成 1；不改变任务/指标定义。
DTYPE = "auto"
MAX_LENGTH = 2048
SEED = 42
LIMIT = None  # None = 全量；改成 8 可试跑。也支持 --limit 8。
RESULTS_DIR = HERE / "results"
EXPECTED_HARNESS_VERSION = "0.4.9.2"
TASK = "arc_easy"
DATASET_PATH = "allenai/ai2_arc"
DATASET_NAME = "ARC-Easy"
EVAL_SPLIT = "test"


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


def validate_results(result: dict, limit: int | None) -> tuple[dict, list]:
    """Do not publish missing/partial/inconsistent results as a successful run."""
    metrics = result["results"][TASK]
    counts = result["n-samples"][TASK]
    rows = result["samples"][TASK]
    total = int(counts["original"])
    expected = total if limit is None else min(limit, total)
    if total <= 0 or int(counts["effective"]) != expected or len(rows) != expected:
        raise ValueError(f"样本覆盖不完整: original={total}, effective={counts['effective']}, saved={len(rows)}")
    ids = [row["doc_id"] for row in rows]
    if len(set(ids)) != expected:
        raise ValueError("逐题结果包含重复 doc_id。")
    summary = {"total_test_examples": total, "evaluated_examples": expected, "limited_run": limit is not None}
    for metric in ("acc", "acc_norm"):
        score = float(metrics[f"{metric},none"])
        values = [float(row[metric]) for row in rows]
        if any(value not in (0.0, 1.0) for value in values):
            raise ValueError(f"{metric} 逐题结果必须为 0 或 1。")
        if not math.isfinite(score) or not 0 <= score <= 1 or not math.isclose(score, sum(values) / expected, abs_tol=1e-12):
            raise ValueError(f"{metric} 汇总与逐题结果不一致: {score}")
        summary[metric] = score
        summary[f"{metric}_percent"] = 100 * score
        summary[f"{metric}_correct"] = int(sum(values))
        summary[f"{metric}_stderr"] = metrics.get(f"{metric}_stderr,none")
    return summary, rows


def save_results(result: dict, summary: dict, model_path: Path, serializer) -> Path:
    try:
        model_name = model_path.relative_to(ROOT).as_posix()
    except ValueError:
        model_name = model_path.as_posix()
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "_", model_name)[-120:]
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
        f"# ARC-Easy {'LIMITED RUN' if summary['limited_run'] else 'full test'}\n\n"
        f"- Model: `{model_path}`\n"
        f"- Tokenizer: `{summary['tokenizer_path']}`\n"
        f"- Protocol: 0-shot, plain completion, no chat template, no decoding watermark\n"
        f"- Examples: {summary['evaluated_examples']} / {summary['total_test_examples']}\n"
        f"- Harness: {summary['versions']['lm_eval']}\n\n"
        "| Metric | Score (%) | Correct |\n|---|---:|---:|\n"
        f"| acc | {summary['acc_percent']:.4f} | {summary['acc_correct']} |\n"
        f"| acc_norm | {summary['acc_norm_percent']:.4f} | {summary['acc_norm_correct']} |\n\n"
        "acc_norm uses answer character length in lm-eval 0.4.9.2, not token length.\n"
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
    if args.limit is not None and (isinstance(args.limit, bool) or args.limit < 1):
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
        if not len(data["test"]):
            raise ValueError("ARC-Easy test split 为空。")
        print("[OK] 数据已缓存；正式评测请使用同一环境、用户和 Hugging Face 缓存目录。")
        return 0

    model_path = local_path(MODEL_PATH)
    tokenizer_path = local_path(TOKENIZER_PATH) if TOKENIZER_PATH is not None else model_path
    check_model_files(model_path, tokenizer_path)
    versions = package_versions()
    if versions["lm_eval"] != EXPECTED_HARNESS_VERSION:
        raise RuntimeError(
            f"需要 lm_eval=={EXPECTED_HARNESS_VERSION}，当前为 {versions['lm_eval']}。\n"
            "请运行: python -m pip install -r down/ARC-Easy/requirements.txt"
        )
    import torch
    from transformers import AutoTokenizer
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
    print(f"[Protocol] ARC-Easy test, 0-shot, completion, limit={args.limit}", flush=True)
    print(f"[Device] {DEVICE}, batch_size={BATCH_SIZE}, dtype={DTYPE}", flush=True)
    if args.check_only:
        print("[OK] 依赖可导入、模型文件和 tokenizer 可读取、设备可用；尚未加载权重/数据或推理。")
        return 0

    started = time.monotonic()
    lm = HFLM(
        pretrained=str(model_path), tokenizer=tokenizer, backend="causal", device=DEVICE,
        dtype=DTYPE, batch_size=BATCH_SIZE, max_length=MAX_LENGTH,
        trust_remote_code=False, parallelize=False, local_files_only=True,
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
        "watermark_at_inference": False, "normalization": "answer_character_length",
        "device": DEVICE, "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        "batch_size": BATCH_SIZE, "dtype_requested": DTYPE, "max_length": MAX_LENGTH,
        "seed": SEED, "versions": versions, "elapsed_seconds": time.monotonic() - started,
    })
    output = save_results(result, summary, model_path, handle_non_serializable)
    print(f"\n[{'LIMITED RUN' if args.limit is not None else 'FULL TEST'}] {summary['evaluated_examples']} examples")
    print(f"acc      = {summary['acc']:.6f} ({summary['acc_percent']:.4f}%)")
    print(f"acc_norm = {summary['acc_norm']:.6f} ({summary['acc_norm_percent']:.4f}%)")
    print(f"[Saved] {output}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, ValueError, RuntimeError, ImportError) as error:
        print(f"[FAILED] {type(error).__name__}: {error}", file=sys.stderr)
        print("排查：依赖见 down/ARC-Easy/README.md；下载失败先运行 --prepare-data；显存不足降低 BATCH_SIZE。", file=sys.stderr)
        raise SystemExit(1)
