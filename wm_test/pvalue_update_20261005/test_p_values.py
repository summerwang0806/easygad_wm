"""Bounded regression checks; no model or GPU is required."""
import argparse
import importlib.util
import io
import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    import sys
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


kgw = load("scorer_under_test", HERE / "kgw.py")
evaluation = load("evaluation_under_test", HERE / "evaluate_compare_metrics.py")
config = kgw.KGWConfig()
for prompt, answer in (([1], [2, 2, 2, 3, 2, 3]), ([2], [2] * 100), ([1], [2, 3, 4]), ([], [])):
    legacy = kgw.kgw_score(prompt, answer, 16, config, device="cpu")
    updated = kgw.kgw_score(prompt, answer, 16, config, device="cpu", include_deduplicated=True)
    for key in legacy:
        assert legacy[key] == updated[key], (key, legacy, updated)
    if answer:
        previous = prompt[-1] if prompt else answer[0]
        pairs = set()
        for token in answer:
            pairs.add((previous, token))
            previous = token
        assert updated["dedup_num_tokens"] == len(pairs)
        processor = kgw.KGWLogitsProcessor(16, config)
        expected_green = sum(bool((processor._greenlist(prev, __import__("torch").device("cpu")) == token).any())
                             for prev, token in pairs)
        assert updated["dedup_green_tokens"] == expected_green
        assert math.isclose(updated["dedup_p_value"], evaluation.p_from_z(updated["dedup_z_score"]))
    else:
        assert updated["p_value"] is None and updated["dedup_p_value"] is None
assert evaluation.p_from_z(0) == 0.5
assert math.isclose(evaluation.p_from_z(4), 3.1671241833119965e-5, rel_tol=1e-12)
assert evaluation.p_from_z(-3) > 0.99
assert evaluation.p_from_z(None) is None


class NoRescoring:
    def score(self, row):
        raise AssertionError("New generation files should need no GPU rescoring")


with tempfile.TemporaryDirectory() as directory:
    path = Path(directory) / "sample.jsonl"
    rows = [{"id": "one", "label": "clean", "num_tokens": 10, "z_score": 0.0,
             "dedup_num_tokens": 3, "dedup_z_score": -1.0},
            {"id": "empty", "label": "clean", "num_tokens": 0, "z_score": 0.0,
             "dedup_num_tokens": 0, "dedup_z_score": None}]
    original = "\n".join(json.dumps(row) for row in rows)
    path.write_text(original, encoding="utf-8")
    records, cache = evaluation.load_pvalue_records(path, NoRescoring())
    assert path.read_text(encoding="utf-8") == original
    assert records[0]["p_value_raw"] == 0.5
    assert records[1]["p_value_raw"] is None
    assert evaluation.load_pvalue_records(path, NoRescoring())[0] == records
    summary = evaluation.summarize_pvalues(records, "p_value_raw")
    assert summary["n_valid"] == 1 and summary["n_invalid"] == 1
    rows[0]["dedup_z_score"] = 3.0
    path.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")
    refreshed, _ = evaluation.load_pvalue_records(path, NoRescoring())
    assert refreshed[0]["p_value_dedup"] < 0.01
    output = io.StringIO()
    methods = {"raw": summary, "deduplicated": summary}
    evaluation.write_pvalue_summary(output, {"clean": methods, "kgw": methods})
    assert "token 对去重" in output.getvalue() and "p≤0.05" in output.getvalue()

    clean_path, kgw_path = Path(directory) / "clean.jsonl", Path(directory) / "kgw.jsonl"
    for label, target, z in (("clean", clean_path, -1.0), ("kgw", kgw_path, 3.0)):
        fixture = [{"id": "one", "label": label, "is_watermarked": label == "kgw",
                    "num_tokens": 10, "z_score": z, "dedup_num_tokens": 7, "dedup_z_score": z}]
        target.write_text(json.dumps(fixture[0]) + "\n", encoding="utf-8")
    history = Path(directory) / "history.md"
    history.write_text("Existing history\n", encoding="utf-8")
    command = [sys.executable, str(HERE / "evaluate_compare_metrics.py"),
               "--clean-file", str(clean_path), "--kgw-file", str(kgw_path), "--output", str(history)]
    for _ in range(2):
        completed = subprocess.run(command, check=True, capture_output=True, text=True)
        assert "AUROC: 1.000000" in completed.stdout
    contents = history.read_text(encoding="utf-8")
    assert contents.startswith("Existing history\n") and contents.count("## 评估记录") == 2
    assert contents.count("两种逐条文本 p-value") == 2
print("PASS: raw scores preserved; unique-pair counts, p-values, empty answers, cache invalidation and reports")
