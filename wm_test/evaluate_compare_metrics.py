#!/usr/bin/env python3
"""Evaluate KGW detection and ROUGE-L against Dolly and 14B clean teacher answers."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import statistics
import sys
from collections import OrderedDict
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent

# DEFAULT_KGW = "data/dolly15k_qwen2_5_0.5b_kgw_test_kgw_scores.jsonl"
# DEFAULT_CLEAN = "data/dolly15k_qwen2_5_0.5b_clean_test_kgw_scores.jsonl"

DEFAULT_KGW = ROOT / "kgwwarmup_kgwgad_warmup_gamma0.5_delta3_qwen2_5_0_5b_dolly15k_test.jsonl"
DEFAULT_CLEAN = ROOT / "base_qwen2_5_0_5b_dolly15k_test.jsonl"

DEFAULT_DOLLY_REFERENCE = ROOT.parent / "text_quality/references/dolly_human_500.jsonl"
DEFAULT_TEACHER_CLEAN_REFERENCE = ROOT.parent / "data/dolly15k_qwen2_5_14b_clean_test.parquet"

DEFAULT_REPORT = ROOT / "detection_metrics_history.md"
TARGET_FPRS = (0.01, 0.05, 0.10)
P_VALUE_SCHEMA = "kgw-single-sided-unique-bigram-v1"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kgw-file", type=Path, default=DEFAULT_KGW)
    parser.add_argument("--clean-file", type=Path, default=DEFAULT_CLEAN)
    parser.add_argument(
        "--dolly-reference-file", type=Path, default=DEFAULT_DOLLY_REFERENCE,
        help="Original Dolly human answers (JSONL with id, answer and prompt); matched by ID",
    )
    parser.add_argument(
        "--teacher-clean-reference-file", type=Path, default=DEFAULT_TEACHER_CLEAN_REFERENCE,
        help="14B clean teacher answers (Parquet with id, teacher_response and content, "
             "or JSONL with id, answer and prompt); matched by ID",
    )
    parser.add_argument("--tokenizer", type=Path, default=None,
                        help="Tokenizer override for old JSONL files missing deduplicated scores")
    parser.add_argument("--score-device", default="cuda",
                        help="CUDA device for one-time rescoring of old JSONL; no model is loaded")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_REPORT,
        help="Append each run to this Markdown history document",
    )
    return parser.parse_args()


def load_scores(path: Path, expected_label: str, expected_flag: bool) -> dict[str, float]:
    if not path.is_file():
        raise FileNotFoundError(f"JSONL file not found: {path}")
    scores: dict[str, float] = {}
    with path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                row: dict[str, Any] = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"invalid JSON at {path}:{line_no}: {error}") from error
            sample_id = str(row.get("id", ""))
            if not sample_id:
                raise ValueError(f"missing id at {path}:{line_no}")
            if sample_id in scores:
                raise ValueError(f"duplicate id {sample_id!r} at {path}:{line_no}")
            if row.get("label") != expected_label:
                raise ValueError(
                    f"wrong label at {path}:{line_no}: expected {expected_label!r}, "
                    f"got {row.get('label')!r}"
                )
            if row.get("is_watermarked") is not expected_flag:
                raise ValueError(
                    f"wrong is_watermarked at {path}:{line_no}: expected {expected_flag}"
                )
            try:
                score = float(row["z_score"])
            except (KeyError, TypeError, ValueError) as error:
                raise ValueError(f"invalid z_score at {path}:{line_no}") from error
            if not math.isfinite(score):
                raise ValueError(f"non-finite z_score at {path}:{line_no}")
            scores[sample_id] = score
    if not scores:
        raise ValueError(f"no scores found in {path}")
    return scores


def evaluate_reference_rouge(
    sample_path: Path, reference_path: Path, reference_source: str
) -> dict[str, Any]:
    """Macro-average ROUGE-L F1 for the KGW-file answers, without altering text."""
    def load_answers(path: Path) -> dict[str, dict[str, Any]]:
        answers: dict[str, dict[str, Any]] = {}
        if path.suffix.lower() == ".parquet":
            import pyarrow.parquet as pq

            records = [
                (index, {"id": row["id"], "answer": row["teacher_response"],
                         "prompt": row["content"]})
                for index, row in enumerate(
                    pq.read_table(path, columns=["id", "teacher_response", "content"]).to_pylist(), 1
                )
            ]
        else:
            with path.open("r", encoding="utf-8") as handle:
                records = [(index, json.loads(line)) for index, line in enumerate(handle, 1)
                           if line.strip()]
        for line_no, row in records:
            if not isinstance(row, dict):
                raise ValueError(f"Expected record object at {path}:{line_no}")
            sample_id = row.get("id")
            if not isinstance(sample_id, str) or not sample_id:
                raise ValueError(f"Missing or invalid id at {path}:{line_no}")
            if sample_id in answers:
                raise ValueError(f"Duplicate id {sample_id!r} at {path}:{line_no}")
            if not isinstance(row.get("answer"), str):
                raise ValueError(f"Missing answer text at {path}:{line_no}")
            answers[sample_id] = row
        if not answers:
            raise ValueError(f"No answers found in {path}")
        return answers

    samples = load_answers(sample_path)
    references = load_answers(reference_path)
    if set(samples) != set(references):
        raise ValueError(
            "Sample and reference IDs must match exactly "
            f"(sample-only={len(set(samples) - set(references))}, "
            f"reference-only={len(set(references) - set(samples))})."
        )
    for sample_id, row in samples.items():
        reference = references[sample_id]
        if not reference["answer"].strip():
            raise ValueError(f"Empty reference answer: {sample_id}")
        if "prompt" not in row or "prompt" not in reference:
            raise ValueError(f"Missing prompt for reference alignment: {sample_id}")
        if row["prompt"] != reference["prompt"]:
            raise ValueError(f"Sample and reference prompts differ: {sample_id}")

    from rouge_score import rouge_scorer

    scorer = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)
    scores = [
        scorer.score(references[sample_id]["answer"], row["answer"])["rougeL"].fmeasure
        for sample_id, row in samples.items()
    ]
    return {
        "mean": statistics.mean(scores),
        "num_samples": len(scores),
        "evaluated_file": str(sample_path.resolve()),
        "reference_file": str(reference_path.resolve()),
        "reference_source": reference_source,
        "metric": "rougeL", "measure": "fmeasure", "use_stemmer": True,
        "aggregation": "unweighted mean of per-sample ROUGE-L F1",
    }


def evaluate_dolly_rouge(sample_path: Path, reference_path: Path) -> dict[str, Any]:
    return evaluate_reference_rouge(
        sample_path, reference_path, "databricks/databricks-dolly-15k:response"
    )


def evaluate_teacher_clean_rouge(sample_path: Path, reference_path: Path) -> dict[str, Any]:
    return evaluate_reference_rouge(
        sample_path, reference_path, "Qwen2.5-14B clean teacher responses"
    )


def p_from_z(z_score: float | None) -> float | None:
    if z_score is None:
        return None
    z = float(z_score)
    if not math.isfinite(z):
        raise ValueError(f"non-finite detection z-score: {z_score}")
    return 0.5 * math.erfc(z / math.sqrt(2.0))


class LegacyRescorer:
    """Rescore saved answers using the original CUDA RNG; never generate text."""

    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.tokenizers: dict[str, Any] = {}
        self.greenlist_cache = OrderedDict()

    def score(self, row: dict[str, Any]) -> dict[str, Any]:
        import torch
        from transformers import AutoTokenizer

        sys.path.insert(0, str(ROOT.parent)) if str(ROOT.parent) not in sys.path else None
        from wm_data.kgw import KGWConfig, kgw_score

        if not str(self.args.score_device).startswith("cuda") or not torch.cuda.is_available():
            raise RuntimeError(
                "Old JSONL has no deduplicated scores. One-time rescoring requires CUDA "
                "because CPU/CUDA KGW random generators differ. Use an available GPU "
                "with CUDA_VISIBLE_DEVICES; later evaluations use the p-value cache."
            )
        model_path = str(self.args.tokenizer or row.get("model_path", ""))
        if not model_path:
            raise ValueError("Cannot rescore old JSONL without model_path; supply --tokenizer")
        if model_path not in self.tokenizers:
            self.tokenizers[model_path] = AutoTokenizer.from_pretrained(
                model_path, trust_remote_code=True, local_files_only=True
            )
        tokenizer = self.tokenizers[model_path]
        prompt = row.get("prompt")
        if isinstance(prompt, list):
            prompt = tokenizer.apply_chat_template(prompt, add_generation_prompt=True, tokenize=False)
        if not isinstance(prompt, str) or not isinstance(row.get("answer"), str):
            raise ValueError("Legacy rescoring requires prompt and answer text in each JSONL row")
        prompt_ids = tokenizer.encode(prompt, add_special_tokens=False)
        limit = int(row.get("generation", {}).get("max_prompt_tokens", 2048))
        if len(prompt_ids) > limit:
            prompt = tokenizer.decode(prompt_ids[:limit], skip_special_tokens=False)
            prompt_ids = tokenizer.encode(prompt, add_special_tokens=False)
        metadata = row.get("kgw", {})
        if not all(key in metadata for key in ("gamma", "delta", "hash_key")):
            raise ValueError("Legacy rescoring requires the original kgw gamma/delta/hash_key metadata")
        score = kgw_score(
            prompt_token_ids=prompt_ids,
            generated_token_ids=tokenizer.encode(row["answer"], add_special_tokens=False),
            vocab_size=len(tokenizer),
            config=KGWConfig(gamma=float(metadata["gamma"]), delta=float(metadata["delta"]),
                             hash_key=int(metadata["hash_key"])),
            device=self.args.score_device, include_deduplicated=True,
            greenlist_cache=self.greenlist_cache,
        )
        if not math.isclose(float(score["z_score"]), float(row["z_score"]), abs_tol=1e-9, rel_tol=1e-9):
            raise ValueError(
                f"Raw z-score mismatch for {row['id']}: saved={row['z_score']}, "
                f"rescored={score['z_score']}. Check tokenizer, prompt format/truncation, "
                "KGW key/gamma and RNG device before accepting deduplicated p-values."
            )
        return score


def load_pvalue_records(path: Path, rescorer: LegacyRescorer) -> tuple[list[dict[str, Any]], Path]:
    source = path.read_bytes()
    digest = hashlib.sha256(source).hexdigest()
    rows = [json.loads(line) for line in source.decode("utf-8").splitlines() if line.strip()]
    cache = path.with_suffix(".p_values.jsonl")
    if cache.exists():
        try:
            cached = [json.loads(line) for line in cache.read_text(encoding="utf-8").splitlines() if line.strip()]
            if (len(cached) == len(rows)
                    and [r.get("id") for r in cached] == [r["id"] for r in rows]
                    and all(r.get("source_sha256") == digest and r.get("schema") == P_VALUE_SCHEMA
                            for r in cached)):
                return cached, cache
        except (ValueError, OSError):
            pass
    records = []
    legacy_count = 0
    for index, row in enumerate(rows, 1):
        if "dedup_z_score" in row and "dedup_num_tokens" in row:
            score = row
        else:
            score = rescorer.score(row)
            legacy_count += 1
            if legacy_count == 1 or index % 50 == 0:
                print(f"Deduplicated scoring {path.name}: {index}/{len(rows)}", flush=True)
        raw_z = float(row["z_score"])
        raw_n = score.get("num_tokens", row.get("num_tokens"))
        dedup_n = int(score["dedup_num_tokens"])
        dedup_z = float(score["dedup_z_score"]) if dedup_n > 0 else None
        records.append({
            "schema": P_VALUE_SCHEMA, "source_sha256": digest,
            "id": row["id"], "label": row["label"],
            "num_tokens_raw": raw_n, "num_tokens_dedup": dedup_n,
            "z_score_raw": raw_z, "z_score_dedup": dedup_z,
            "p_value_raw": p_from_z(raw_z) if raw_n != 0 else None,
            "p_value_dedup": p_from_z(dedup_z),
        })
    # Separate, versioned cache: never overwrite the sampled answer files.
    temporary = cache.with_name(cache.name + f".{os.getpid()}.tmp")
    try:
        with temporary.open("w", encoding="utf-8", newline="\n") as handle:
            for record in records:
                handle.write(json.dumps(record, ensure_ascii=False, allow_nan=False) + "\n")
        os.replace(temporary, cache)
    finally:
        temporary.unlink(missing_ok=True)
    return records, cache


def summarize_pvalues(records: list[dict[str, Any]], key: str) -> dict[str, Any]:
    values = [float(row[key]) for row in records if row[key] is not None]
    if any(not math.isfinite(p) or not 0 <= p <= 1 for p in values):
        raise ValueError(f"Invalid p-value in {key}")
    return {
        "n_total": len(records), "n_valid": len(values), "n_invalid": len(records) - len(values),
        "mean": statistics.mean(values) if values else None,
        "median": statistics.median(values) if values else None,
        "min": min(values) if values else None, "max": max(values) if values else None,
        "at_alpha": {
            f"{alpha:.0%}": {"alpha": alpha, "count": sum(p <= alpha for p in values),
                             "fraction": sum(p <= alpha for p in values) / len(values) if values else None}
            for alpha in TARGET_FPRS
        },
    }


def write_pvalue_summary(handle: Any, summaries: dict[str, Any]) -> None:
    handle.write("\n两种逐条文本 p-value 统计（单侧正态近似；不是 AUROC 的显著性检验）：\n\n")
    handle.write("去重规则：相同的 `(previous_token_id, token_id)` 只计一次；不修改回答文本。\n\n")
    handle.write("| 数据 | 检测方式 | 有效样本 | p 均值 | p 中位数 | p≤0.01 | p≤0.05 | p≤0.10 |\n")
    handle.write("|---|---|---:|---:|---:|---:|---:|---:|\n")
    for label in ("kgw", "clean"):
        for method, title in (("raw", "原始"), ("deduplicated", "token 对去重")):
            summary = summaries[label][method]
            mean = f"{summary['mean']:.6g}" if summary["mean"] is not None else "N/A"
            median = f"{summary['median']:.6g}" if summary["median"] is not None else "N/A"
            rates_text = []
            for alpha in ("1%", "5%", "10%"):
                rate = summary["at_alpha"][alpha]
                rates_text.append(f"{rate['count']} ({rate['fraction']:.2%})" if rate["fraction"] is not None else "N/A")
            handle.write(f"| {label} | {title} | {summary['n_valid']}/{summary['n_total']} | "
                         f"{mean} | {median} | {' | '.join(rates_text)} |\n")
    handle.write("\nKGW 的小 p 占比是该理论阈值下的检出率，clean 的小 p 占比是实测误报率。"
                 "p≤0.05 不保证实际 FPR=5%；去重可改善重复带来的失真，但不保证完全校准。"
                 "空回答不做显著性检验，p=null，并排除在有效样本统计之外。\n")


def roc_points(negative: dict[str, float], positive: dict[str, float]) -> list[dict[str, float | int]]:
    """Empirical ROC points; equal scores are treated as one threshold group."""
    groups: dict[float, list[int]] = {}
    for score in negative.values():
        groups.setdefault(score, [0, 0])[0] += 1
    for score in positive.values():
        groups.setdefault(score, [0, 0])[1] += 1
    fp = tp = 0
    points: list[dict[str, float | int]] = [
        {"threshold": math.inf, "fpr": 0.0, "tpr": 0.0, "fp": 0, "tp": 0}
    ]
    for threshold in sorted(groups, reverse=True):
        n_negative, n_positive = groups[threshold]
        fp += n_negative
        tp += n_positive
        points.append({
            "threshold": threshold,
            "fpr": fp / len(negative),
            "tpr": tp / len(positive),
            "fp": fp,
            "tp": tp,
        })
    return points


def auc(points: list[dict[str, float | int]]) -> float:
    area = 0.0
    for left, right in zip(points, points[1:]):
        area += (float(right["fpr"]) - float(left["fpr"])) * (
            float(right["tpr"]) + float(left["tpr"])
        ) / 2.0
    return area


def rates(point: dict[str, float | int], n_negative: int, n_positive: int) -> dict[str, Any]:
    tp, fp = int(point["tp"]), int(point["fp"])
    fn, tn = n_positive - tp, n_negative - fp
    precision = tp / (tp + fp) if tp + fp else 0.0
    tpr = tp / n_positive
    fpr = fp / n_negative
    f1 = 2 * precision * tpr / (precision + tpr) if precision + tpr else 0.0
    threshold = float(point["threshold"])
    return {
        "threshold": threshold if math.isfinite(threshold) else None,
        "fpr": fpr,
        "tpr": tpr,
        "precision": precision,
        "f1": f1,
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
    }


def evaluate(negative: dict[str, float], positive: dict[str, float]) -> dict[str, Any]:
    if set(negative) != set(positive):
        raise ValueError(
            "The two JSONL files must have identical sample IDs "
            f"(clean-only={len(set(negative) - set(positive))}, "
            f"kgw-only={len(set(positive) - set(negative))})."
        )
    points = roc_points(negative, positive)
    best: dict[str, Any] | None = None
    for point in points:
        candidate = rates(point, len(negative), len(positive))
        if best is None or candidate["f1"] > best["f1"]:
            best = candidate
    assert best is not None

    # For each target FPR, report the largest empirical TPR achievable without
    # exceeding that FPR. Tied scores move together as one threshold group.
    at_fpr: dict[str, Any] = {}
    for target in TARGET_FPRS:
        eligible = [point for point in points if float(point["fpr"]) <= target]
        point = max(
            eligible,
            key=lambda item: (float(item["tpr"]), float(item["threshold"])),
        )
        result = rates(point, len(negative), len(positive))
        result["target_fpr"] = target
        at_fpr[f"{target:.0%}"] = result

    return {
        "positive_class": "kgw",
        "score": "z_score (higher means more likely watermarked)",
        "num_kgw": len(positive),
        "num_clean": len(negative),
        "auroc": auc(points),
        "best_f1": best,
        "tpr_at_fpr": at_fpr,
        "note": "For each target FPR, select the empirical ROC point with the highest "
                "TPR whose FPR does not exceed the target; tied scores are kept together.",
    }


def main() -> None:
    args = parse_args()
    kgw = load_scores(args.kgw_file.resolve(), "kgw", True)
    clean = load_scores(args.clean_file.resolve(), "clean", False)
    result = evaluate(clean, kgw)
    result["rouge_l_dolly"] = evaluate_dolly_rouge(
        args.kgw_file.resolve(), args.dolly_reference_file.resolve()
    )
    result["rouge_l_teacher_clean"] = evaluate_teacher_clean_rouge(
        args.kgw_file.resolve(), args.teacher_clean_reference_file.resolve()
    )
    rescorer = LegacyRescorer(args)
    p_kgw, kgw_cache = load_pvalue_records(args.kgw_file.resolve(), rescorer)
    p_clean, clean_cache = load_pvalue_records(args.clean_file.resolve(), rescorer)
    result["p_values"] = {
        label: {"raw": summarize_pvalues(records, "p_value_raw"),
                "deduplicated": summarize_pvalues(records, "p_value_dedup")}
        for label, records in (("kgw", p_kgw), ("clean", p_clean))
    }
    result["p_value_method"] = "one-sided normal survival probability; unique context-token pairs for dedup"
    result["per_sample_p_value_files"] = {"kgw": str(kgw_cache), "clean": str(clean_cache)}
    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    result["evaluated_at"] = timestamp
    result["kgw_file"] = str(args.kgw_file.resolve())
    result["clean_file"] = str(args.clean_file.resolve())
    output = args.output.resolve()
    result["history_document"] = str(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    best = result["best_f1"]
    with output.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(f"\n## 评估记录：{timestamp}\n\n")
        handle.write(f"- 样本数：KGW {result['num_kgw']}，clean {result['num_clean']}\n")
        handle.write(f"- AUROC：{result['auroc']:.6f}\n")
        rouge = result["rouge_l_dolly"]
        handle.write(
            f"- ROUGE-L（同批 {rouge['num_samples']} 条原始 Dolly 回答作参考）："
            f"{rouge['mean']:.6f}（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）\n"
        )
        handle.write(f"- 原始 Dolly 参考文件：`{rouge['reference_file']}`\n")
        teacher_rouge = result["rouge_l_teacher_clean"]
        handle.write(
            f"- ROUGE-L（同批 {teacher_rouge['num_samples']} 条 14B clean 教师回答作参考）："
            f"{teacher_rouge['mean']:.6f}（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）\n"
        )
        handle.write(f"- 14B clean 教师参考文件：`{teacher_rouge['reference_file']}`\n")
        handle.write(
            f"- Best F1：{best['f1']:.6f}（z 阈值 {best['threshold']}，"
            f"TPR {best['tpr']:.6f}，FPR {best['fpr']:.6f}）\n"
        )
        handle.write("- TPR@FPR 及该工作点的 F1：\n\n")
        handle.write("  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |\n")
        handle.write("  |---:|---:|---:|---:|---:|\n")
        for target, metrics in result["tpr_at_fpr"].items():
            handle.write(
                f"  | {target} | {metrics['fpr']:.6f} | {metrics['tpr']:.6f} | "
                f"{metrics['f1']:.6f} | {metrics['threshold']} |\n"
            )
        write_pvalue_summary(handle, result["p_values"])
        handle.write(f"\n逐条 p-value：`{kgw_cache}`；`{clean_cache}`\n")
        handle.write("\n完整指标（JSON）：\n\n```json\n")
        json.dump(result, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n```\n")

    print(f"KGW samples: {result['num_kgw']} | clean samples: {result['num_clean']}")
    print(f"AUROC: {result['auroc']:.6f}")
    rouge = result["rouge_l_dolly"]
    print(
        f"ROUGE-L（原始 Dolly 参考）: {rouge['mean']:.6f} "
        f"| samples: {rouge['num_samples']} | per-sample F1 mean, use_stemmer=True"
    )
    teacher_rouge = result["rouge_l_teacher_clean"]
    print(
        f"ROUGE-L（14B clean 教师参考）: {teacher_rouge['mean']:.6f} "
        f"| samples: {teacher_rouge['num_samples']} | per-sample F1 mean, use_stemmer=True"
    )
    print(
        f"Best F1: {best['f1']:.6f} | z threshold: {best['threshold']} | "
        f"TPR: {best['tpr']:.6f} | FPR: {best['fpr']:.6f}"
    )
    print("TPR at target FPR:")
    for target, metrics in result["tpr_at_fpr"].items():
        print(
            f"  {target:>3}: TPR={metrics['tpr']:.6f} | F1={metrics['f1']:.6f} | "
            f"actual FPR={metrics['fpr']:.6f} | z threshold={metrics['threshold']}"
        )
    print(f"Appended metrics to: {output}")
    for label, methods in result["p_values"].items():
        for method, summary in methods.items():
            print(f"p-values {label}/{method}: {json.dumps(summary, ensure_ascii=False)}")
    print(f"Per-sample p-values: {kgw_cache} | {clean_cache}")


if __name__ == "__main__":
    main()
