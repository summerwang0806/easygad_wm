#!/usr/bin/env python3
"""Evaluate KGW z-score detection from the paired wm_test JSONL files."""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent

# DEFAULT_KGW = "data/dolly15k_qwen2_5_0.5b_kgw_test_kgw_scores.jsonl"
# DEFAULT_CLEAN = "data/dolly15k_qwen2_5_0.5b_clean_test_kgw_scores.jsonl"

DEFAULT_KGW = ROOT / "kgwwarmup_cleangad_gad_qwen2_5_0_5b_dolly15k_test.jsonl"
DEFAULT_CLEAN = ROOT / "base_qwen2_5_0_5b_dolly15k_test.jsonl"

DEFAULT_REPORT = ROOT / "detection_metrics_history.md"
TARGET_FPRS = (0.01, 0.05, 0.10)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kgw-file", type=Path, default=DEFAULT_KGW)
    parser.add_argument("--clean-file", type=Path, default=DEFAULT_CLEAN)
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
        handle.write("\n完整指标（JSON）：\n\n```json\n")
        json.dump(result, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n```\n")

    print(f"KGW samples: {result['num_kgw']} | clean samples: {result['num_clean']}")
    print(f"AUROC: {result['auroc']:.6f}")
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


if __name__ == "__main__":
    main()
