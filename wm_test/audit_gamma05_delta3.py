"""Offline, non-generating audit of the gamma=0.5/delta=3 warmup and GAD files.

Uses only the standard library by default. Optional --teacher-reference and
--tokenizer arguments enable an independent ROUGE-L and exact text-token audit
in an environment with rouge_score, pyarrow and transformers installed.
Never overwrites the sampled answers or p-value caches.
"""
from __future__ import annotations

import argparse
from bisect import bisect_left, bisect_right
import hashlib
import json
import math
from pathlib import Path
import re
import statistics

ROOT = Path(__file__).resolve().parent
BASE_NAME = "base_qwen2_5_0_5b_dolly15k_test.rescored_gamma0.5_delta3_key15485863.jsonl"
STUDENT_NAMES = {
    stage: f"kgwwarmup_kgwgad_{stage}_gamma0.5_delta3_qwen2_5_0_5b_dolly15k_test.jsonl"
    for stage in ("warmup", "gad")
}


def load(path: Path) -> list[dict]:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    ids = [row["id"] for row in rows]
    if len(set(ids)) != len(ids) or len(rows) != 500:
        raise ValueError(f"Expected exactly 500 distinct IDs: {path}")
    return rows


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lf_digest(path: Path) -> str:
    # Git checkout on Windows may convert the server's LF files to CRLF.
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def near(actual, expected, where):
    if actual is None or not math.isclose(float(actual), float(expected), rel_tol=1e-10, abs_tol=1e-14):
        raise ValueError(f"Mismatch {where}: {actual!r} != {expected!r}")


def check_rows(path: Path, label: str):
    rows = load(path)
    sidecar = load(path.with_suffix(".p_values.jsonl"))
    if [r["id"] for r in rows] != [r["id"] for r in sidecar]:
        raise ValueError(f"Cache ID/order mismatch: {path}")
    source_sha = digest(path)
    config = None
    for row, cached in zip(rows, sidecar):
        where = f"{path.name}/{row['id']}"
        if row["label"] != label or row["is_watermarked"] is not (label == "kgw"):
            raise ValueError(f"Wrong label: {where}")
        metadata = row["kgw"]
        current = {k: metadata[k] for k in ("gamma", "delta", "hash_key", "seeding")}
        if (current["gamma"], current["delta"], current["hash_key"]) != (0.5, 3.0, 15485863):
            raise ValueError(f"Wrong detector config: {where}")
        if config is not None and current != config:
            raise ValueError(f"Mixed config: {where}")
        config = current
        for prefix, cached_suffix in (("", "raw"), ("dedup_", "dedup")):
            n, green = row[prefix + "num_tokens"], row[prefix + "green_tokens"]
            if not isinstance(n, int) or not isinstance(green, int) or not 0 < n or not 0 <= green <= n:
                raise ValueError(f"Invalid counts: {where}")
            z = (green - 0.5 * n) / math.sqrt(0.25 * n)
            p = 0.5 * math.erfc(z / math.sqrt(2))
            near(row[prefix + "z_score"], z, where + "/z")
            near(row[prefix + "p_value"], p, where + "/p")
            near(row[prefix + "green_fraction"], green / n, where + "/green_fraction")
            near(cached["z_score_" + cached_suffix], z, where + "/cache_z")
            near(cached["p_value_" + cached_suffix], p, where + "/cache_p")
            if cached["num_tokens_" + cached_suffix] != n:
                raise ValueError(f"Cache token count mismatch: {where}")
        if not row["dedup_num_tokens"] <= row["num_tokens"]:
            raise ValueError(f"Impossible unique count: {where}")
        if cached["source_sha256"] not in (source_sha, lf_digest(path)) or cached["schema"] != "kgw-single-sided-unique-bigram-v1":
            raise ValueError(f"Stale cache: {where}")
    return rows, config, source_sha


def independent_roc(negative: list[float], positive: list[float]):
    """AUC as P(positive>negative)+0.5*P(tie); exhaustive tied thresholds."""
    ordered = sorted(negative)
    wins = sum(bisect_left(ordered, score) for score in positive)
    ties = sum(bisect_right(ordered, score) - bisect_left(ordered, score) for score in positive)
    area = (wins + 0.5 * ties) / (len(negative) * len(positive))
    n_sorted, p_sorted = sorted(negative), sorted(positive)
    points = []
    for threshold in sorted(set(negative + positive), reverse=True):
        fp = len(negative) - bisect_left(n_sorted, threshold)
        tp = len(positive) - bisect_left(p_sorted, threshold)
        points.append({"threshold": threshold, "fp": fp, "tp": tp,
                       "fpr": fp / len(negative), "tpr": tp / len(positive)})
    selected = {}
    for limit in (0.01, 0.05, 0.1):
        feasible = [p for p in points if p["fpr"] <= limit]
        selected[f"{limit:.0%}"] = max(feasible, key=lambda p: (p["tp"], p["threshold"])) if feasible else {
            "threshold": None, "fp": 0, "tp": 0, "fpr": 0.0, "tpr": 0.0}
    return {"auroc": area, "tpr_at_fpr": selected, "wins": wins, "ties": ties}


def p_summary(rows, prefix):
    ps = [r[prefix + "p_value"] for r in rows]
    return {"mean": statistics.mean(ps), "median": statistics.median(ps),
            "at_alpha": {str(a): {"count": sum(p <= a for p in ps),
                                   "fraction": sum(p <= a for p in ps) / len(ps)}
                         for a in (0.01, 0.05, 0.1)}}


def repetition_bounds(rows):
    severe, nonsevere, ambiguous = [], [], []
    per_sample = []
    for row in rows:
        n, d = row["num_tokens"], row["dedup_num_tokens"]
        # KGW includes one boundary pair (last prompt token, first answer token).
        # Removing it lowers unique count by either zero or one.
        low = 1 - min(d, n - 1) / (n - 1) if n > 1 else 0.0
        high = 1 - max(0, d - 1) / (n - 1) if n > 1 else 0.0
        state = True if low > 0.5 else False if high <= 0.5 else None
        (severe if state is True else nonsevere if state is False else ambiguous).append(row["id"])
        per_sample.append({"id": row["id"], "repetition_fraction_lower": low,
                           "repetition_fraction_upper": high, "severe_repetition": state})
    return {"count": len(severe) if not ambiguous else None,
            "fraction": len(severe) / len(rows) if not ambiguous else None,
            "ambiguous_ids": ambiguous, "severe_ids": severe,
            "median_scored_tokens": statistics.median(r["num_tokens"] for r in rows),
            "median_unique_pairs": statistics.median(r["dedup_num_tokens"] for r in rows),
            "max_length_count": sum(r["num_tokens"] == r["generation"]["max_new_tokens"] for r in rows)}, per_sample


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "gamma05_delta3_audit/metrics.json")
    parser.add_argument("--teacher-reference", type=Path)
    parser.add_argument("--tokenizer", type=Path)
    parser.add_argument("--quality-audit", type=Path, default=ROOT / "audit_quality/local_bpe_quality_audit.json",
                        help="Optional independently tokenized text audit, checked against source SHA and IDs")
    args = parser.parse_args()
    base_path = ROOT / BASE_NAME
    base, config, base_sha = check_rows(base_path, "clean")
    base_by_id = {row["id"]: row for row in base}
    original_base_path = ROOT / "base_qwen2_5_0_5b_dolly15k_test.jsonl"
    original_base = load(original_base_path)
    original_by_id = {r["id"]: r for r in original_base}
    original_base_sha = digest(original_base_path)
    for row in base:
        source = original_by_id[row["id"]]
        provenance = row["rescoring"]
        if provenance["source_sha256"] not in (original_base_sha, lf_digest(original_base_path)):
            raise ValueError("Base rescoring source hash does not match local original")
        for field in ("id", "prompt", "answer", "generation", "model_path", "label", "is_watermarked"):
            if row[field] != source[field]:
                raise ValueError(f"Base text/provenance mismatch: {row['id']}/{field}")
    history_path = ROOT / "detection_metrics_history.md"
    history = [json.loads(block) for block in re.findall(r"```json\s*(.*?)\s*```", history_path.read_text(encoding="utf-8"), re.S)]
    output = {"detector_config": config, "base_file": str(base_path), "base_sha256": base_sha,
              "base_lf_sha256": lf_digest(base_path),
              "original_base_sha256": original_base_sha, "history_sha256": digest(history_path),
              "sha_note": "Server hashes match after CRLF to LF normalization; every cache score was independently checked.",
              "p_value_aggregation": "mean of 500 per-answer one-sided normal approximation p-values",
              "repetition_definition": "1 - unique answer-internal adjacent token pairs / (answer token count - 1) > 0.5",
              "verification_scope": "Formula/count/cache checks; no local CUDA reclassification of green tokens.",
              "base": {"p_raw": p_summary(base, ""), "p_dedup": p_summary(base, "dedup_")}, "models": {}}
    tokenizer = None
    text_audit = (json.loads(args.quality_audit.read_text(encoding="utf-8"))
                  if not args.tokenizer and args.quality_audit.is_file() else None)
    if args.tokenizer:
        from transformers import AutoTokenizer
        tokenizer = AutoTokenizer.from_pretrained(args.tokenizer, local_files_only=True)
    for stage, filename in STUDENT_NAMES.items():
        path = ROOT / filename
        rows, student_config, sha = check_rows(path, "kgw")
        if student_config != config or {r["id"] for r in rows} != set(base_by_id):
            raise ValueError(f"Detector or ID pair mismatch: {stage}")
        for row in rows:
            base_row = base_by_id[row["id"]]
            common_gen_keys = set(row["generation"]) & set(base_row["generation"])
            if row["prompt"] != base_row["prompt"] or any(row["generation"][k] != base_row["generation"][k] for k in common_gen_keys):
                raise ValueError(f"Prompt/generation pair mismatch: {stage}/{row['id']}")
            if row["generation"]["kgw_enabled_during_generation"] is not False:
                raise ValueError("Extra KGW bias applied during sampling")
        roc = independent_roc([r["z_score"] for r in base], [r["z_score"] for r in rows])
        dedup_roc = independent_roc([r["dedup_z_score"] for r in base], [r["dedup_z_score"] for r in rows])
        repetition, per_sample = repetition_bounds(rows)
        if text_audit is not None:
            quality = text_audit["models"][stage]
            if quality["source_sha256"] != sha:
                raise ValueError("Text audit source SHA mismatch")
            q_samples = {r["id"]: r for r in quality["per_sample"]}
            if set(q_samples) != {r["id"] for r in rows}:
                raise ValueError("Text audit ID mismatch")
            for row, sample in zip(rows, per_sample):
                q = q_samples[row["id"]]
                if q["answer_tokens"] != row["num_tokens"] or q["answer_pairs"] != row["num_tokens"] - 1:
                    raise ValueError("Text audit length mismatch")
                if row["dedup_num_tokens"] - q["unique_answer_pairs"] not in (0, 1):
                    raise ValueError("Text audit unique-pair mismatch")
                rate = 1 - q["unique_answer_pairs"] / q["answer_pairs"] if q["answer_pairs"] else 0.0
                if not sample["repetition_fraction_lower"] - 1e-12 <= rate <= sample["repetition_fraction_upper"] + 1e-12:
                    raise ValueError("Text audit out of bounds")
                sample.update(repetition_fraction_exact=rate, severe_repetition=rate > 0.5)
            repetition.update(count=sum(p["severe_repetition"] for p in per_sample),
                              fraction=sum(p["severe_repetition"] for p in per_sample) / len(rows),
                              ambiguous_ids=[],
                              text_audit_file=str(args.quality_audit),
                              text_audit_tokenizer=text_audit["tokenizer_file"],
                              text_audit_tokenizer_sha256=text_audit["tokenizer_sha256"])
            repetition["severe_ids"] = [p["id"] for p in per_sample if p["severe_repetition"]]
        if tokenizer:
            for row, sample in zip(rows, per_sample):
                tokens = tokenizer.encode(row["answer"], add_special_tokens=False)
                if len(tokens) != row["num_tokens"]:
                    raise ValueError(f"Tokenizer length mismatch: {stage}/{row['id']}")
                pairs = list(zip(tokens, tokens[1:]))
                if row["dedup_num_tokens"] - len(set(pairs)) not in (0, 1):
                    raise ValueError(f"Tokenizer unique-pair mismatch: {stage}/{row['id']}")
                rate = 1 - len(set(pairs)) / len(pairs) if pairs else 0.0
                sample["repetition_fraction_exact"] = rate
                sample["severe_repetition"] = rate > 0.5
            repetition["count"] = sum(p["severe_repetition"] for p in per_sample)
            repetition["fraction"] = repetition["count"] / len(rows)
            repetition["exact_tokenizer_audit"] = str(args.tokenizer)
            repetition["ambiguous_ids"] = []
            repetition["severe_ids"] = [p["id"] for p in per_sample if p["severe_repetition"]]
        reports = [r for r in history if Path(r.get("kgw_file", "")).name == filename
                   and Path(r.get("clean_file", "")).name == BASE_NAME
                   and r.get("detector_config", {}).get("gamma") == 0.5]
        if not reports:
            raise ValueError(f"Missing matching history entry: {stage}")
        report = reports[-1]
        near(report["auroc"], roc["auroc"], stage + "/history_auc")
        for target in ("1%", "5%", "10%"):
            for k in ("tpr", "fpr", "threshold"):
                near(report["tpr_at_fpr"][target][k], roc["tpr_at_fpr"][target][k], stage + "/history_" + k)
        raw_ps, dedup_ps = p_summary(rows, ""), p_summary(rows, "dedup_")
        near(report["p_values"]["kgw"]["raw"]["mean"], raw_ps["mean"], stage + "/history_raw_p")
        near(report["p_values"]["kgw"]["deduplicated"]["mean"], dedup_ps["mean"], stage + "/history_dedup_p")
        model = {"source_file": str(path), "source_sha256": sha, "source_lf_sha256": lf_digest(path),
                 "model_paths": sorted({r["model_path"] for r in rows}),
                 "generation_configs_without_seed": sorted({json.dumps({k: v for k, v in r["generation"].items() if k != "seed"}, sort_keys=True) for r in rows}),
                 "per_sample_seed_range": [min(r["generation"]["seed"] for r in rows), max(r["generation"]["seed"] for r in rows)],
                 "n": len(rows), "raw_detection": roc, "dedup_detection": dedup_roc,
                 "unrecorded_base_generation_keys": sorted(set(rows[0]["generation"]) - set(base[0]["generation"])),
                 "repetition": repetition, "p_raw": raw_ps, "p_dedup": dedup_ps,
                 "teacher_rouge_l": {"mean": report["rouge_l_teacher_clean"]["mean"],
                                     "status": "server history value; teacher reference unavailable locally",
                                     "report_evaluated_at": report["evaluated_at"],
                                     "method": report["rouge_l_teacher_clean"]}}
        if args.teacher_reference:
            import evaluate_compare_metrics as evaluator
            recomputed = evaluator.evaluate_teacher_clean_rouge(path, args.teacher_reference)
            near(recomputed["mean"], model["teacher_rouge_l"]["mean"], stage + "/teacher_rouge")
            model["teacher_rouge_l"].update(status="independently recomputed", recomputed=recomputed,
                                           reference_sha256=digest(args.teacher_reference))
        output["models"][stage] = model
        print(stage, json.dumps({"auroc": roc["auroc"], "tpr5": roc["tpr_at_fpr"]["5%"],
                                "tpr10": roc["tpr_at_fpr"]["10%"], "severe": repetition["count"],
                                "ambiguous": repetition["ambiguous_ids"],
                                "p_raw_mean": raw_ps["mean"], "p_dedup_mean": dedup_ps["mean"],
                                "rouge_teacher": model["teacher_rouge_l"]["mean"],
                                "dedup_auroc": dedup_roc["auroc"], "dedup_tpr": dedup_roc["tpr_at_fpr"]}))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        sample_output = args.output.parent / f"{stage}.repetition_audit.jsonl"
        sample_output.write_text("".join(json.dumps(r) + "\n" for r in per_sample), encoding="utf-8")
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Saved", args.output)


if __name__ == "__main__":
    main()
