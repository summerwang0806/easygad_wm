"""Teacher Parquet alignment and resumable judging without models or GPUs."""
from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import pyarrow as pa
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "soft-win-rate"))
import run_teacher_soft_win_rate as teacher

common = teacher.common


class TeacherReferenceTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix=".teacher-preference-test-", dir=ROOT)
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.reference = self.root / "teacher.parquet"
        self.rows = [{"id": name, "content": [{"role": "user", "content": f"Question {name}?"}],
                      "teacher_response": f"Teacher {name}"} for name in ("one", "two")]
        self.write_reference(self.rows)
        self.input = self.root / "candidate.jsonl"
        self.input.write_text("".join(json.dumps({"id": row["id"], "prompt": row["content"],
                                               "answer": f"Candidate {row['id']}"}) + "\n"
                                      for row in self.rows), encoding="utf-8")
        model = self.root / "fake-model"
        model.mkdir()
        (model / "config.json").write_text('{"model_type":"qwen3"}', encoding="utf-8")
        (model / "tokenizer.json").write_text("{}", encoding="utf-8")
        (model / "model.safetensors").write_bytes(b"offline test weights")
        self.config = common.JudgeConfig(model_path=model, bootstrap=30, retries=0)
        self.output, self.history = self.root / "results", self.root / "history.md"

    def write_reference(self, rows):
        pq.write_table(pa.Table.from_pylist(rows), self.reference)

    @staticmethod
    def fake_runner(tasks, config, attempt_dir):
        return [{"key": task["key"], "finish_reason": "stop", "text": json.dumps({
            "winner": "tie" if task["id"] == "two" else ("B" if task["swapped"] else "A"),
            "reason": "Offline test judgment"})} for task in tasks]

    def evaluate(self, **kwargs):
        with contextlib.redirect_stdout(io.StringIO()):
            return common.run_evaluation(self.input, self.reference, self.config, self.output, self.history, **kwargs)

    def test_real_project_teacher_and_clean_student_align_on_all_500_prompts(self):
        reference = common.load_answers(teacher.REFERENCE_PARQUET)
        candidate = common.load_answers(ROOT / "wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl")
        self.assertEqual(len(common.align_answers(candidate, reference)), 500)
        self.assertTrue(all(isinstance(row["answer"], str) and row["answer"].strip()
                            for row in reference.values()))

    def test_bad_teacher_rows_and_mismatched_prompts_are_rejected(self):
        for rows in ([self.rows[0], self.rows[0]],
                     [{**self.rows[0], "teacher_response": None}],
                     [{**self.rows[0], "id": ""}]):
            with self.subTest(rows=rows):
                self.write_reference(rows)
                with self.assertRaises(ValueError):
                    common.load_answers(self.reference)
        for rows in ([self.rows[0]],
                     [{**self.rows[0], "content": [{"role": "user", "content": "Different question"}]}, self.rows[1]]):
            with self.subTest(rows=rows):
                self.write_reference(rows)
                with self.assertRaises(ValueError):
                    common.align_answers(common.load_answers(self.input), common.load_answers(self.reference))

    def test_entrypoint_uses_manual_input_and_project_relative_paths_without_writes(self):
        original_defaults = common.INPUT_JSONL, common.REFERENCE_JSONL, common.RESULTS_DIR, common.HISTORY_FILE
        missing_model_config = common.JudgeConfig(model_path=self.root / "missing-model")
        before = sorted(path.relative_to(self.root) for path in self.root.rglob("*"))
        with patch.object(teacher, "INPUT_JSONL", self.input.relative_to(ROOT)), \
                patch.object(teacher, "REFERENCE_PARQUET", self.reference.relative_to(ROOT)), \
                patch.object(teacher, "RESULTS_DIR", self.output), \
                patch.object(teacher, "HISTORY_FILE", self.history), \
                patch.object(common, "JudgeConfig", return_value=missing_model_config), \
                patch.object(common, "run_auto_gpu", side_effect=AssertionError("No GPU allowed")), \
                contextlib.chdir(self.root), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(teacher.main(["--check-only"]), 0)
        self.assertEqual(before, sorted(path.relative_to(self.root) for path in self.root.rglob("*")))
        self.assertEqual(original_defaults,
                         (common.INPUT_JSONL, common.REFERENCE_JSONL, common.RESULTS_DIR, common.HISTORY_FILE))

    def test_two_orders_limit_resume_and_parquet_hash_in_report(self):
        originals = self.input.read_bytes(), self.reference.read_bytes()
        first = self.evaluate(runner=self.fake_runner, limit=1)
        self.assertEqual(first["soft_win_rate"], 1)
        second = self.evaluate(runner=self.fake_runner)
        self.assertTrue(second["complete"])
        self.assertEqual(second["soft_win_rate"], .75)
        self.assertEqual(second["cache_reused_rounds"], 2)
        self.assertEqual(second["new_judgments"], 2)
        self.assertEqual(second["reference_sha256"], common.file_hash(self.reference))
        self.assertEqual(second["reference_file"], str(self.reference))
        with patch.object(common, "run_auto_gpu", side_effect=AssertionError("Reuse complete cache")):
            third = self.evaluate()
            summary = self.evaluate(summary_only=True)
        self.assertEqual(third["cache_reused_rounds"], 4)
        self.assertEqual(summary["soft_win_rate"], .75)
        history = self.history.read_text(encoding="utf-8")
        self.assertIn("固定 clean 教师参照（Parquet）", history)
        self.assertNotIn("固定 Clean-KD", history)
        self.assertEqual(history.count("## 评测记录"), 4)
        self.assertEqual(originals, (self.input.read_bytes(), self.reference.read_bytes()))

    def test_changed_teacher_answers_invalidate_cached_judgments(self):
        first = self.evaluate(runner=self.fake_runner)
        self.write_reference([{**self.rows[0], "teacher_response": "Updated teacher answer"}, self.rows[1]])
        second = self.evaluate(runner=self.fake_runner)
        self.assertNotEqual(first["cache_file"], second["cache_file"])
        self.assertEqual(second["cache_reused_rounds"], 0)
        self.assertEqual(second["new_judgments"], 4)


if __name__ == "__main__":
    unittest.main()
