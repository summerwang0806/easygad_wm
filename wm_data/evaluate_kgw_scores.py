#!/usr/bin/env python3
"""Evaluate KGW z-scores for Dolly train and test splits without extra dependencies."""

from __future__ import annotations

import argparse
from datetime import datetime
import json
import math
import os
from pathlib import Path
from typing import Iterable


DEFAULT_FILES = {
    "clean_train": "dolly15k_qwen2_5_14b_clean_train_kgw_scores.jsonl",
    "kgw_train": "dolly15k_qwen2_5_14b_kgw_train_kgw_scores.jsonl",
    "clean_test": "dolly15k_qwen2_5_14b_clean_test_kgw_scores.jsonl",
    "kgw_test": "dolly15k_qwen2_5_14b_kgw_test_kgw_scores.jsonl",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    for name, filename in DEFAULT_FILES.items():
        parser.add_argument(
            f"--{name.replace('_', '-')}",
            type=Path,
            default=None,
            help=f"Override {name} score file (default: <data-dir>/{filename})",
        )
    parser.add_argument(
        "--f1-threshold",
        type=float,
        default=4.0,
        help="Fixed z-score threshold used for F1 (default: 4.0)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Append-only Markdown results file (default: wm_data/kgw_detection_results.md)",
    )
    return parser.parse_args()


def load_scores(path: Path, expected_watermarked: bool) -> tuple[list[str], list[float]]:
    if not path.is_file():
        raise FileNotFoundError(f"score file does not exist: {path}")
    ids: list[str] = []
    scores: list[float] = []
    seen: set[str] = set()
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"invalid JSON at {path}:{line_number}: {error}") from error
            sample_id = str(row.get("id", ""))
            if not sample_id:
                raise ValueError(f"missing id at {path}:{line_number}")
            if sample_id in seen:
                raise ValueError(f"duplicate id {sample_id!r} in {path}")
            if row.get("is_watermarked") is not expected_watermarked:
                raise ValueError(
                    f"wrong is_watermarked at {path}:{line_number}; "
                    f"expected {expected_watermarked}"
                )
            try:
                score = float(row["z_score"])
            except (KeyError, TypeError, ValueError) as error:
                raise ValueError(f"invalid z_score at {path}:{line_number}") from error
            if not math.isfinite(score):
                raise ValueError(f"non-finite z_score at {path}:{line_number}")
            seen.add(sample_id)
            ids.append(sample_id)
            scores.append(score)
    if not scores:
        raise ValueError(f"score file is empty: {path}")
    return ids, scores


def confusion_at_threshold(
    negative_scores: Iterable[float],
    positive_scores: Iterable[float],
    threshold: float,
) -> dict[str, int | float]:
    negative_scores = list(negative_scores)
    positive_scores = list(positive_scores)
    fp = sum(score >= threshold for score in negative_scores)
    tp = sum(score >= threshold for score in positive_scores)
    tn = len(negative_scores) - fp
    fn = len(positive_scores) - tp
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2.0 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "threshold": threshold,
        "f1": f1,
        "precision": precision,
        "recall_tpr": recall,
        "fpr": fp / len(negative_scores),
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
    }


def auroc(negative_scores: list[float], positive_scores: list[float]) -> float:
    """Mann-Whitney AUROC with average ranks for tied scores."""

    labelled = sorted(
        [(score, 0) for score in negative_scores]
        + [(score, 1) for score in positive_scores],
        key=lambda item: item[0],
    )
    positive_rank_sum = 0.0
    index = 0
    while index < len(labelled):
        end = index + 1
        while end < len(labelled) and labelled[end][0] == labelled[index][0]:
            end += 1
        average_rank = ((index + 1) + end) / 2.0
        positive_rank_sum += average_rank * sum(label for _, label in labelled[index:end])
        index = end
    n_positive = len(positive_scores)
    n_negative = len(negative_scores)
    return (
        positive_rank_sum - n_positive * (n_positive + 1) / 2.0
    ) / (n_positive * n_negative)


def roc_operating_points(
    negative_scores: list[float], positive_scores: list[float]
) -> list[dict[str, float | int]]:
    """Return empirical ROC points after each tied score group, high to low."""

    groups: dict[float, list[int]] = {}
    for score in negative_scores:
        groups.setdefault(score, [0, 0])[0] += 1
    for score in positive_scores:
        groups.setdefault(score, [0, 0])[1] += 1
    fp = tp = 0
    points: list[dict[str, float | int]] = [
        {"threshold": math.inf, "fpr": 0.0, "tpr": 0.0, "fp": 0, "tp": 0}
    ]
    for threshold in sorted(groups, reverse=True):
        negative_count, positive_count = groups[threshold]
        fp += negative_count
        tp += positive_count
        points.append(
            {
                "threshold": threshold,
                "fpr": fp / len(negative_scores),
                "tpr": tp / len(positive_scores),
                "fp": fp,
                "tp": tp,
            }
        )
    return points


def tpr_at_fpr(
    points: list[dict[str, float | int]], target_fpr: float
) -> dict[str, float | int | None]:
    eligible = [point for point in points if float(point["fpr"]) <= target_fpr]
    best = max(eligible, key=lambda point: (float(point["tpr"]), float(point["threshold"])))
    threshold = float(best["threshold"])
    return {
        "target_fpr": target_fpr,
        "tpr": best["tpr"],
        "achieved_fpr": best["fpr"],
        "threshold": threshold if math.isfinite(threshold) else None,
        "tp": best["tp"],
        "fp": best["fp"],
    }


def best_f1(points: list[dict[str, float | int]], n_positive: int) -> dict[str, float | int | None]:
    best: dict[str, float | int | None] | None = None
    for point in points:
        tp = int(point["tp"])
        fp = int(point["fp"])
        fn = n_positive - tp
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / n_positive
        f1 = 2.0 * precision * recall / (precision + recall) if precision + recall else 0.0
        threshold = float(point["threshold"])
        candidate: dict[str, float | int | None] = {
            "threshold": threshold if math.isfinite(threshold) else None,
            "f1": f1,
            "precision": precision,
            "recall_tpr": recall,
            "fpr": point["fpr"],
            "tp": tp,
            "fp": fp,
            "fn": fn,
        }
        if best is None or f1 > float(best["f1"]):
            best = candidate
    assert best is not None
    return best


def evaluate_split(
    split: str,
    clean_path: Path,
    kgw_path: Path,
    fixed_threshold: float,
) -> dict[str, object]:
    clean_ids, negative_scores = load_scores(clean_path, expected_watermarked=False)
    kgw_ids, positive_scores = load_scores(kgw_path, expected_watermarked=True)
    if set(clean_ids) != set(kgw_ids):
        only_clean = len(set(clean_ids) - set(kgw_ids))
        only_kgw = len(set(kgw_ids) - set(clean_ids))
        raise ValueError(
            f"{split} clean/KGW IDs do not match: only_clean={only_clean}, only_kgw={only_kgw}"
        )
    points = roc_operating_points(negative_scores, positive_scores)
    return {
        "split": split,
        "clean_file": str(clean_path),
        "kgw_file": str(kgw_path),
        "num_clean": len(negative_scores),
        "num_kgw": len(positive_scores),
        "auroc": auroc(negative_scores, positive_scores),
        "tpr_at_fpr": {
            "1%": tpr_at_fpr(points, 0.01),
            "5%": tpr_at_fpr(points, 0.05),
            "10%": tpr_at_fpr(points, 0.10),
        },
        "f1_at_fixed_threshold": confusion_at_threshold(
            negative_scores, positive_scores, fixed_threshold
        ),
        "best_f1": best_f1(points, len(positive_scores)),
    }


def print_results(result: dict[str, object]) -> None:
    print("\nKGW detection results")
    print("=" * 106)
    print(
        f"{'split':<8} {'clean':>8} {'kgw':>8} {'AUROC':>9} "
        f"{'TPR@1%':>9} {'TPR@5%':>9} {'TPR@10%':>10} "
        f"{'F1 fixed':>10} {'best F1':>9} {'best z':>10}"
    )
    print("-" * 106)
    for split in ("train", "test"):
        metrics = result[split]
        rates = metrics["tpr_at_fpr"]
        fixed = metrics["f1_at_fixed_threshold"]
        best = metrics["best_f1"]
        print(
            f"{split:<8} {metrics['num_clean']:>8} {metrics['num_kgw']:>8} "
            f"{metrics['auroc']:>9.6f} {rates['1%']['tpr']:>9.6f} "
            f"{rates['5%']['tpr']:>9.6f} {rates['10%']['tpr']:>10.6f} "
            f"{fixed['f1']:>10.6f} {best['f1']:>9.6f} {best['threshold']:>10.6f}"
        )
    print("=" * 106)
    print(f"Fixed F1 threshold: z >= {result['f1_threshold']}")
    print(f"Saved full metrics: {result['output']}")


def markdown_record(result: dict[str, object]) -> str:
    lines = [
        f"## Run {result['recorded_at']}",
        "",
        f"- Positive class: `kgw`",
        f"- Detection score: `z_score` (larger means more likely watermarked)",
        f"- Fixed decision: `z_score >= {result['f1_threshold']}`",
        "- TPR@FPR: the highest empirical TPR whose empirical FPR does not exceed the target",
        "",
        "### Input files",
        "",
    ]
    for key in ("clean_train", "kgw_train", "clean_test", "kgw_test"):
        lines.append(f"- `{key}`: `{result['input_files'][key]}`")
    lines.extend(
        [
            "",
            "### Summary",
            "",
            "| Split | Clean | KGW | AUROC | TPR@FPR=1% | TPR@FPR=5% | TPR@FPR=10% | Fixed F1 | Best F1 | Best threshold |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for split in ("train", "test"):
        metrics = result[split]
        rates = metrics["tpr_at_fpr"]
        fixed = metrics["f1_at_fixed_threshold"]
        best = metrics["best_f1"]
        lines.append(
            f"| {split} | {metrics['num_clean']} | {metrics['num_kgw']} | "
            f"{metrics['auroc']:.6f} | {rates['1%']['tpr']:.6f} | "
            f"{rates['5%']['tpr']:.6f} | {rates['10%']['tpr']:.6f} | "
            f"{fixed['f1']:.6f} | {best['f1']:.6f} | {best['threshold']:.6f} |"
        )
    lines.extend(
        [
            "",
            "### TPR operating points",
            "",
            "| Split | Target FPR | Achieved FPR | TPR | Threshold | TP | FP |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for split in ("train", "test"):
        for label in ("1%", "5%", "10%"):
            point = result[split]["tpr_at_fpr"][label]
            threshold = "inf" if point["threshold"] is None else f"{point['threshold']:.6f}"
            lines.append(
                f"| {split} | {label} | {point['achieved_fpr']:.6f} | "
                f"{point['tpr']:.6f} | {threshold} | {point['tp']} | {point['fp']} |"
            )
    lines.extend(
        [
            "",
            "### F1 details",
            "",
            "| Split | Type | Threshold | F1 | Precision | Recall/TPR | FPR | TP | FP | TN | FN |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for split in ("train", "test"):
        metrics = result[split]
        for label, key in (("fixed", "f1_at_fixed_threshold"), ("best", "best_f1")):
            point = metrics[key]
            tn = metrics["num_clean"] - point["fp"]
            lines.append(
                f"| {split} | {label} | {point['threshold']:.6f} | {point['f1']:.6f} | "
                f"{point['precision']:.6f} | {point['recall_tpr']:.6f} | {point['fpr']:.6f} | "
                f"{point['tp']} | {point['fp']} | {tn} | {point['fn']} |"
            )
    lines.extend(["", "---", ""])
    return "\n".join(lines)


def append_markdown(result: dict[str, object], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    is_new = not output.exists() or output.stat().st_size == 0
    with output.open("a", encoding="utf-8", newline="\n") as handle:
        if is_new:
            handle.write(
                "# KGW detection experiment results\n\n"
                "This file is append-only: every evaluation run adds a timestamped record.\n\n"
            )
        handle.write(markdown_record(result))
        handle.flush()
        os.fsync(handle.fileno())


def main() -> None:
    args = parse_args()
    data_dir = args.data_dir.resolve()
    paths = {
        name: (getattr(args, name) or data_dir / filename).resolve()
        for name, filename in DEFAULT_FILES.items()
    }
    output = (
        args.output or Path(__file__).resolve().parent / "kgw_detection_results.md"
    ).resolve()
    if output.suffix.lower() != ".md":
        raise ValueError("--output must use the .md extension")
    result: dict[str, object] = {
        "recorded_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "input_files": {name: str(path) for name, path in paths.items()},
        "metric_definition": {
            "positive_class": "kgw",
            "score": "z_score (larger means more likely watermarked)",
            "tpr_at_fpr": "highest empirical TPR whose empirical FPR does not exceed the target",
            "fixed_prediction": f"watermarked if z_score >= {args.f1_threshold}",
        },
        "f1_threshold": args.f1_threshold,
        "train": evaluate_split(
            "train", paths["clean_train"], paths["kgw_train"], args.f1_threshold
        ),
        "test": evaluate_split(
            "test", paths["clean_test"], paths["kgw_test"], args.f1_threshold
        ),
    }
    result["output"] = str(output)
    append_markdown(result, output)
    print_results(result)


if __name__ == "__main__":
    main()
