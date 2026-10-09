"""Read-only offline analysis of four ablation outputs; no generation/API calls."""
import hashlib
import json
import math
import statistics
import sys
from pathlib import Path

import pyarrow.parquet as pq
from rouge_score import rouge_scorer
from transformers import AutoTokenizer

ROOT = Path("/shared/wwx/EasyGAD")
sys.path.insert(0, str(ROOT / "wm_test"))
import evaluate_compare_metrics as detection

FILES = {
    "kgwwarmup_cleangad/kgwwarmup": "kgwwarmup_cleangad_warmup_qwen2_5_0_5b_dolly15k_test.jsonl",
    "kgwwarmup_cleangad/cleangad": "kgwwarmup_cleangad_gad_qwen2_5_0_5b_dolly15k_test.jsonl",
    "cleanwarmup_kgwgad/cleanwarmup": "cleanwarmup_kgwgad_warmup_qwen2_5_0_5b_dolly15k_test.jsonl",
    "cleanwarmup_kgwgad/kgwgad": "cleanwarmup_kgwgad_gad_qwen2_5_0_5b_dolly15k_test.jsonl",
}
OUTPUT_NAME = "ablation_table_metrics.json"
if "--clean-clean" in sys.argv:
    FILES = {
        "cleanwarmup_cleangad/cleanwarmup": "cleanwarmup_cleangad_warmup_qwen2_5_0_5b_dolly15k_test.jsonl",
        "cleanwarmup_cleangad/cleangad": "cleanwarmup_cleangad_gad_qwen2_5_0_5b_dolly15k_test.jsonl",
    }
    OUTPUT_NAME = "cleanwarmup_cleangad_table_metrics.json"


def load(path):
    records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    result = {str(row["id"]): row for row in records}
    assert len(result) == len(records), f"duplicate IDs in {path}"
    return result


teacher_path = ROOT / "data/dolly15k_qwen2_5_14b_clean_test.parquet"
teacher_rows = pq.read_table(teacher_path).to_pylist()
teacher = {str(row["id"]): row for row in teacher_rows}
assert len(teacher) == len(teacher_rows) == 500
base_path = ROOT / "wm_test/base_qwen2_5_0_5b_dolly15k_test.jsonl"
base = load(base_path)
negative = detection.load_scores(base_path, "clean", False)
tokenizer = AutoTokenizer.from_pretrained("/shared/public_models/Qwen2.5-0.5B", local_files_only=True)
scorer = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)
result = {
    "teacher_file": str(teacher_path),
    "teacher_sha256": hashlib.sha256(teacher_path.read_bytes()).hexdigest(),
    "clean_negative_file": str(base_path),
    "clean_negative_sha256": hashlib.sha256(base_path.read_bytes()).hexdigest(),
    "rouge_method": "rouge-score 0.1.2 RougeScorer(['rougeL'], use_stemmer=True), mean F1, aligned by ID",
    "repetition_method": "1 - unique_adjacent_token_pairs / all_adjacent_token_pairs > 0.5; Qwen2.5-0.5B tokenizer, no special tokens",
    "p_value_method": "mean per-answer single-sided normal-approximation p-value, raw and unique-pair deduplicated",
    "models": {},
}
for label, filename in FILES.items():
    path = ROOT / "wm_test" / filename
    samples = load(path)
    assert len(samples) == 500 and set(samples) == set(teacher) == set(base)
    source_sha = hashlib.sha256(path.read_bytes()).hexdigest()
    p_path = path.with_suffix(".p_values.jsonl")
    p_rows = load(p_path)
    assert set(p_rows) == set(samples)
    assert all(row["source_sha256"] == source_sha for row in p_rows.values()), f"stale p-value cache: {p_path}"
    assert all(row["schema"] == "kgw-single-sided-unique-bigram-v1" for row in p_rows.values())
    for sample_id, row in samples.items():
        assert math.isclose(float(row["z_score"]), p_rows[sample_id]["z_score_raw"], rel_tol=1e-12, abs_tol=1e-15)
        assert row["num_tokens"] == p_rows[sample_id]["num_tokens_raw"]
        if "dedup_p_value" in row:
            assert math.isclose(row["dedup_p_value"], p_rows[sample_id]["p_value_dedup"], rel_tol=1e-12, abs_tol=1e-15)
    roc = detection.evaluate(negative, detection.load_scores(path, "kgw", True))
    rouge_values, repetition_ratios, severe_ids, per_sample = [], [], [], []
    for index, (sample_id, row) in enumerate(samples.items(), 1):
        assert row["prompt"] == teacher[sample_id]["content"] == base[sample_id]["prompt"], sample_id
        answer = row["answer"]
        reference = teacher[sample_id]["teacher_response"]
        score = scorer.score(reference, answer)["rougeL"].fmeasure
        tokens = tokenizer.encode(answer, add_special_tokens=False)
        assert len(tokens) == row["num_tokens"], f"tokenizer mismatch: {label}/{sample_id}"
        pairs = list(zip(tokens, tokens[1:]))
        ratio = 1 - len(set(pairs)) / len(pairs) if pairs else 0.0
        raw_p = 0.5 * math.erfc(float(row["z_score"]) / math.sqrt(2))
        assert math.isclose(raw_p, p_rows[sample_id]["p_value_raw"], rel_tol=1e-12, abs_tol=1e-15)
        rouge_values.append(score)
        repetition_ratios.append(ratio)
        if ratio > 0.5:
            severe_ids.append(sample_id)
        per_sample.append({"id": sample_id, "rouge_l_clean_teacher": score,
                           "repeated_bigram_fraction": ratio, "severe_repetition": ratio > 0.5,
                           "p_value_raw": p_rows[sample_id]["p_value_raw"],
                           "p_value_dedup": p_rows[sample_id]["p_value_dedup"]})
        if index % 100 == 0:
            print(label, index, "/", len(samples), flush=True)
    model = {
        "source_file": str(path), "source_sha256": source_sha,
        "model_paths": sorted({row["model_path"] for row in samples.values()}),
        "generation_configs": list({json.dumps(row["generation"], sort_keys=True) for row in samples.values()}),
        "n": len(samples), "auroc": roc["auroc"],
        "tpr_at_fpr_le_5pct": roc["tpr_at_fpr"]["5%"]["tpr"],
        "actual_fpr_5pct": roc["tpr_at_fpr"]["5%"]["fpr"],
        "tpr_at_fpr_le_10pct": roc["tpr_at_fpr"]["10%"]["tpr"],
        "actual_fpr_10pct": roc["tpr_at_fpr"]["10%"]["fpr"],
        "rouge_l_clean_teacher_mean": statistics.mean(rouge_values),
        "severe_repetition_count": len(severe_ids), "severe_repetition_fraction": len(severe_ids) / len(samples),
        "p_value_raw_mean": statistics.mean(row["p_value_raw"] for row in p_rows.values()),
        "p_value_dedup_mean": statistics.mean(row["p_value_dedup"] for row in p_rows.values()),
        "severe_repetition_ids": severe_ids,
    }
    result["models"][label] = model
    output_dir = ROOT / "wm_test/pvalue_update_20261005"
    per_sample_path = output_dir / (filename.removesuffix(".jsonl") + ".table_metrics.jsonl")
    with per_sample_path.open("w", encoding="utf-8") as handle:
        for row in per_sample:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    print("MODEL_RESULT", label, json.dumps(model, ensure_ascii=False), flush=True)
output_path = ROOT / "wm_test/pvalue_update_20261005" / OUTPUT_NAME
output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("SAVED", output_path, flush=True)
