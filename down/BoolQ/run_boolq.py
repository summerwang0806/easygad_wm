#!/usr/bin/env python3
"""BoolQ zero-shot accuracy using the official lm-evaluation-harness task.

Edit MODEL_PATH below, then run: python down/BoolQ/run_boolq.py
"""
from __future__ import annotations

import argparse
from collections import Counter
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

# 相对路径以项目根目录为基准；也支持服务器绝对路径。
MODEL_PATH = "checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_new/gad/global_step_1813/actor/huggingface"
TOKENIZER_PATH = "/shared/public_models/Qwen2.5-0.5B"  # None = 使用模型导出目录。
DEVICE = "cuda:0"  # CUDA_VISIBLE_DEVICES=3 时仍写 cuda:0。
BATCH_SIZE = 8
DTYPE = "auto"
MAX_LENGTH = 2048
SEED = 42
LIMIT = None  # None = 全量；也支持 --limit 8。
RESULTS_DIR = HERE / "results"
EXPECTED_HARNESS_VERSION = "0.4.9.2"
EXPECTED_EXAMPLES = 3270
TASK = "boolq"
DATASET_PATH = "super_glue"
DATASET_NAME = "boolq"
EVAL_SPLIT = "validation"


def local_path(value: str | Path) -> Path:
    path = Path(value).expanduser()
    return (path if path.is_absolute() else ROOT / path).resolve()


def check_model_files(model_path: Path, tokenizer_path: Path) -> None:
    if not (model_path / "config.json").is_file():
        raise FileNotFoundError(f"缺少本地 Hugging Face config.json: {model_path}")
    config = json.loads((model_path / "config.json").read_text(encoding="utf-8"))
    if config.get("is_encoder_decoder", False):
        raise ValueError("此入口用于 Qwen 等 decoder-only causal LM。")
    indexes = [model_path / name for name in ("model.safetensors.index.json", "pytorch_model.bin.index.json")
               if (model_path / name).is_file()]
    if indexes:
        for index in indexes:
            mapping = json.loads(index.read_text(encoding="utf-8")).get("weight_map")
            if not isinstance(mapping, dict) or not mapping:
                raise ValueError(f"权重索引缺少有效 weight_map: {index}")
            missing = [name for name in set(mapping.values()) if not (model_path / name).is_file()]
            if missing:
                raise FileNotFoundError(f"模型导出缺少权重分片: {missing}")
    elif not any((model_path / name).is_file() for name in ("model.safetensors", "pytorch_model.bin")):
        raise FileNotFoundError(f"缺少完整 Hugging Face 权重或索引: {model_path}；不能使用未合并 FSDP 分片。")
    if not tokenizer_path.is_dir() or not any((tokenizer_path / name).is_file() for name in (
            "tokenizer.json", "vocab.json", "tokenizer.model", "spiece.model")):
        raise FileNotFoundError(f"tokenizer 不完整: {tokenizer_path}；请设置同一学生基座的 TOKENIZER_PATH。")


def package_versions() -> dict:
    versions = {}
    for name in ("lm_eval", "torch", "transformers", "datasets", "accelerate", "tokenizers"):
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = "not installed"
    return versions


def document_label(document: dict) -> int:
    if not isinstance(document, dict):
        raise ValueError("BoolQ 样本必须包含 doc 字典。")
    value = document.get("label")
    if type(value) not in (int, bool) or value not in (0, 1):
        raise ValueError("BoolQ validation 缺少有效 0/1 标签；不要使用无标签 test 集。")
    for key in ("passage", "question"):
        if not isinstance(document.get(key), str) or not document[key].strip():
            raise ValueError(f"BoolQ 样本缺少非空 {key}。")
    return int(value)


def majority_baseline(labels: list[int], *, scope: str) -> dict:
    if not labels:
        raise ValueError("BoolQ 评测样本为空。")
    counts = Counter(labels)
    label = max((0, 1), key=lambda value: (counts[value], value))
    score = counts[label] / len(labels)
    return {"label_counts": {"no": counts[0], "yes": counts[1]},
            "majority_label": "yes" if label else "no", "majority_baseline": score,
            "majority_baseline_percent": 100 * score, "majority_baseline_correct": counts[label],
            "majority_baseline_scope": scope}


def validate_results(result: dict, limit: int | None) -> tuple[dict, list]:
    metrics = result["results"][TASK]
    counts = result["n-samples"][TASK]
    rows = result["samples"][TASK]
    total = int(counts["original"])
    expected = total if limit is None else min(limit, total)
    if total != EXPECTED_EXAMPLES:
        raise ValueError(f"BoolQ validation 应为 {EXPECTED_EXAMPLES} 题，harness 报告 {total}。")
    if int(counts["effective"]) != expected or len(rows) != expected:
        raise ValueError(f"样本覆盖不完整: expected={expected}, effective={counts['effective']}, saved={len(rows)}")
    identities = [row["doc_id"] for row in rows]
    if len(set(identities)) != expected:
        raise ValueError("逐题结果包含重复 doc_id。")
    values = [float(row["acc"]) for row in rows]
    score = float(metrics["acc,none"])
    if (any(value not in (0., 1.) for value in values) or not math.isfinite(score)
            or not 0 <= score <= 1 or not math.isclose(score, sum(values) / expected, abs_tol=1e-12)):
        raise ValueError("acc 汇总与逐题 0/1 结果不一致。")
    labels = [document_label(row.get("doc")) for row in rows]
    summary = {"total_validation_examples": total, "evaluated_examples": expected,
               "limited_run": limit is not None, "acc": score, "acc_percent": 100 * score,
               "acc_correct": int(sum(values)), "acc_stderr": metrics.get("acc_stderr,none")}
    summary.update(majority_baseline(labels, scope="evaluated_subset" if limit is not None else "full_validation"))
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
    with (output / "samples.jsonl").open("w", encoding="utf-8") as stream:
        for sample in result["samples"][TASK]:
            stream.write(json.dumps(sample, ensure_ascii=False, default=serializer) + "\n")
    aggregate = {key: value for key, value in result.items() if key != "samples"}
    for name, payload in (("harness_results.json", aggregate), ("summary.json", summary)):
        (output / name).write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=serializer) + "\n", encoding="utf-8")
    report = (
        f"# BoolQ {'LIMITED RUN' if summary['limited_run'] else 'full validation'}\n\n"
        f"- Model: `{model_path}`\n- Tokenizer: `{summary['tokenizer_path']}`\n"
        "- Protocol: 0-shot, native no/yes conditional likelihood, no chat template, no WN processor\n"
        f"- Examples: {summary['evaluated_examples']} / {summary['total_validation_examples']}\n"
        f"- Harness: {summary['versions']['lm_eval']}\n\n"
        "| Metric | Score (%) | Correct |\n|---|---:|---:|\n"
        f"| acc | {summary['acc_percent']:.4f} | {summary['acc_correct']} |\n"
        f"| Majority-class baseline | {summary['majority_baseline_percent']:.4f} | {summary['majority_baseline_correct']} |\n\n"
        f"Baseline scope: {summary['majority_baseline_scope']}; always predict `{summary['majority_label']}`.\n"
        f"Label counts: {summary['label_counts']}.\n"
        "The baseline is computed from exactly the evaluated questions, not copied from a paper.\n"
        "Limited runs are for debugging, not final paper results.\n"
        "This evaluates checkpoint probabilities; inference-only WN quality is not measured.\n"
    )
    (output / "report.md").write_text(report, encoding="utf-8")
    return output


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--prepare-data", action="store_true", help="只下载并检查有标签 validation 数据，不加载模型/GPU")
    modes.add_argument("--check-only", action="store_true", help="只检查依赖、模型/tokenizer 和设备，不加载权重/数据或推理")
    parser.add_argument("--limit", type=int, default=LIMIT, help="只测前 N 题；省略使用顶部 LIMIT")
    args = parser.parse_args(argv)
    if args.limit is not None and (type(args.limit) is not int or args.limit < 1):
        parser.error("LIMIT / --limit 必须为正整数或 None。")
    if sys.version_info < (3, 10):
        raise RuntimeError("需要 Python >= 3.10。")
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    if args.prepare_data:
        from datasets import load_dataset
        print(f"[Data] Downloading {DATASET_PATH} / {DATASET_NAME}", flush=True)
        data = load_dataset(DATASET_PATH, DATASET_NAME)
        rows = data[EVAL_SPLIT]
        if len(rows) != EXPECTED_EXAMPLES:
            raise ValueError(f"BoolQ validation 应为 {EXPECTED_EXAMPLES} 题，得到 {len(rows)}。")
        baseline = majority_baseline([document_label(row) for row in rows], scope="full_validation")
        print(f"[Data] Cached splits: {dict((name, len(split)) for name, split in data.items())}")
        print(f"[Baseline] validation label counts={baseline['label_counts']}; majority={baseline['majority_baseline_percent']:.4f}%")
        print("[OK] validation 标签已检查；正式评测请使用同一环境、用户和 Hugging Face 缓存目录。")
        return 0

    model_path = local_path(MODEL_PATH)
    tokenizer_path = local_path(TOKENIZER_PATH) if TOKENIZER_PATH is not None else model_path
    check_model_files(model_path, tokenizer_path)
    versions = package_versions()
    if versions["lm_eval"] != EXPECTED_HARNESS_VERSION:
        raise RuntimeError(f"需要 lm_eval=={EXPECTED_HARNESS_VERSION}，当前 {versions['lm_eval']}；请安装 down/BoolQ/requirements.txt。")
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from lm_eval import simple_evaluate
    from lm_eval.models.huggingface import HFLM
    from lm_eval.utils import handle_non_serializable

    if int(os.environ.get("WORLD_SIZE", "1")) != 1:
        raise RuntimeError("请使用单进程 python，不使用 torchrun/多卡 accelerate。")
    if DEVICE.startswith("cuda"):
        index = torch.device(DEVICE).index or 0
        if not torch.cuda.is_available() or index >= torch.cuda.device_count():
            raise RuntimeError(f"CUDA 设备不可用: {DEVICE}；检查 CUDA_VISIBLE_DEVICES。")
    elif DEVICE != "cpu":
        raise ValueError("DEVICE 只支持 cpu 或 cuda[:N]。")
    tokenizer = AutoTokenizer.from_pretrained(str(tokenizer_path), local_files_only=True, trust_remote_code=False)
    print(f"[Model] {model_path}\n[Tokenizer] {tokenizer_path}", flush=True)
    print(f"[Protocol] BoolQ validation, 0-shot, no/yes likelihood, limit={args.limit}", flush=True)
    print(f"[Device] {DEVICE}, batch_size={BATCH_SIZE}, dtype={DTYPE}", flush=True)
    if args.check_only:
        print("[OK] 依赖/模型文件/tokenizer/设备检查通过；未加载权重/数据或推理。")
        return 0

    started = time.monotonic()
    # Keep compatibility with Transformers 4.x: pre-load via torch_dtype, then
    # give HFLM the initialized model instead of its dtype= loading path.
    model = AutoModelForCausalLM.from_pretrained(
        str(model_path), torch_dtype=DTYPE, local_files_only=True,
        trust_remote_code=False, low_cpu_mem_usage=True,
    ).to(DEVICE)
    model.eval()
    lm = HFLM(pretrained=model, tokenizer=tokenizer, backend="causal",
              batch_size=BATCH_SIZE, max_length=MAX_LENGTH)
    result = simple_evaluate(
        model=lm, tasks=[TASK], num_fewshot=0, batch_size=BATCH_SIZE, device=DEVICE,
        limit=args.limit, log_samples=True, apply_chat_template=False,
        random_seed=SEED, numpy_random_seed=SEED, torch_random_seed=SEED,
        fewshot_random_seed=SEED, bootstrap_iters=0,
    )
    if result is None:
        raise RuntimeError("Harness 未返回结果。")
    summary, _ = validate_results(result, args.limit)
    summary.update({"model_path": str(model_path), "tokenizer_path": str(tokenizer_path),
                    "task": TASK, "dataset_path": DATASET_PATH, "dataset_name": DATASET_NAME,
                    "split": EVAL_SPLIT, "num_fewshot": 0, "apply_chat_template": False,
                    "watermark_at_inference": False, "scoring": "no_yes_conditional_loglikelihood",
                    "device": DEVICE, "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
                    "batch_size": BATCH_SIZE, "dtype_requested": DTYPE, "max_length": MAX_LENGTH,
                    "model_loader": "transformers_torch_dtype_preloaded", "seed": SEED,
                    "versions": versions, "elapsed_seconds": time.monotonic() - started})
    output = save_results(result, summary, model_path, handle_non_serializable)
    print(f"\n[{'LIMITED RUN' if args.limit is not None else 'FULL VALIDATION'}] {summary['evaluated_examples']} examples")
    print(f"acc = {summary['acc']:.6f} ({summary['acc_percent']:.4f}%), correct={summary['acc_correct']}")
    print(f"majority baseline ({summary['majority_baseline_scope']}) = {summary['majority_baseline_percent']:.4f}%")
    print(f"[Saved] {output}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, RuntimeError, ImportError, KeyError) as error:
        print(f"[FAILED] {type(error).__name__}: {error}", file=sys.stderr)
        print("说明见 down/BoolQ/README.md；下载失败先 --prepare-data；显存不足降低 BATCH_SIZE。", file=sys.stderr)
        raise SystemExit(1)
