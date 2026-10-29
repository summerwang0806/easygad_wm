"""Four-file overnight queue regressions using fake local judgments only."""
from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
TOOL_ROOT = ROOT / "soft-win-rate"
if str(TOOL_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOL_ROOT))

import run_four_soft_win_rate as batch


class FourFileBatchTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix=".four-soft-win-rate-test-", dir=ROOT)
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.assertTrue(self.root.is_relative_to(ROOT))
        self.model = self.root / "local-model"
        self.model.mkdir()
        (self.model / "config.json").write_text(json.dumps({
            "model_type": "qwen3", "hidden_size": 512, "num_attention_heads": 8,
            "num_key_value_heads": 2, "num_hidden_layers": 2, "head_dim": 64,
        }), encoding="utf-8")
        (self.model / "tokenizer.json").write_text("{}", encoding="utf-8")
        (self.model / "model.safetensors").write_bytes(b"offline fake model weights")
        self.config = batch.single.JudgeConfig(model_path=self.model, bootstrap=20, retries=0)
        self.reference = self.write_answers("reference.jsonl", "reference")
        self.jobs = tuple(batch.Job(f"method-{index}", self.write_answers(
            f"candidate-{index}.jsonl", f"candidate-{index}")) for index in range(4))
        self.results = self.root / "results"
        self.history = self.root / "individual-history.md"
        self.batch_history = self.root / "batch-history.md"

    def write_answers(self, name, answer_prefix, *, wrong_prompt=False):
        path = self.root / name
        rows = [{"id": sample_id, "prompt": "Wrong question" if wrong_prompt else f"Question {sample_id}?",
                 "answer": f"{answer_prefix} answer {sample_id}"} for sample_id in ("one", "two")]
        path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
        return path

    @staticmethod
    def winning_results(tasks, config, attempt_dir):
        return [{"key": task["key"], "finish_reason": "stop", "prompt_tokens": 100,
                 "completion_tokens": 20, "text": json.dumps({
                     "winner": "B" if task["swapped"] else "A", "reason": "Offline batch test judgment",
                 })} for task in tasks]

    def run_batch(self, runner=None, **kwargs):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return batch.run_batch(self.jobs, reference_path=self.reference, config=self.config,
                                   results_dir=self.results, history_file=self.history,
                                   batch_history_file=self.batch_history, runner=runner, **kwargs)

    def assert_saved_snapshot(self, result):
        for key in ("summary_file", "report_file", "log_file"):
            self.assertTrue(Path(result[key]).is_file(), key)
        saved = json.loads(Path(result["summary_file"]).read_text(encoding="utf-8"))
        self.assertEqual(saved["complete"], result["complete"])
        self.assertEqual([job["status"] for job in saved["jobs"]],
                         [job["status"] for job in result["jobs"]])

    def test_all_four_run_in_order_and_keep_separate_results_and_history(self):
        calls = []
        originals = {job.input_path: job.input_path.read_bytes() for job in self.jobs}
        originals[self.reference] = self.reference.read_bytes()
        self.history.write_text("Earlier individual results.\n", encoding="utf-8")
        self.batch_history.write_text("Earlier batch results.\n", encoding="utf-8")

        def runner(tasks, config, attempt_dir):
            payload = json.loads(tasks[0]["messages"][-1]["content"])
            calls.append(payload["answer_a"])
            return self.winning_results(tasks, config, attempt_dir)

        result = self.run_batch(runner)
        self.assertEqual(calls, [f"candidate-{index} answer one" for index in range(4)])
        self.assertTrue(result["complete"])
        self.assertFalse(result["interrupted"])
        self.assertEqual([row["label"] for row in result["jobs"]], [job.label for job in self.jobs])
        self.assertEqual([row["status"] for row in result["jobs"]], ["complete"] * 4)
        caches, runs = set(), set()
        for row in result["jobs"]:
            self.assertEqual(row["result"]["num_valid_samples"], 2)
            self.assertEqual(row["result"]["soft_win_rate"], 1)
            self.assertTrue(Path(row["result"]["run_file"]).is_file())
            caches.add(row["result"]["cache_file"])
            runs.add(row["result"]["run_file"])
        self.assertEqual(len(caches), 4)
        self.assertEqual(len(runs), 4)
        self.assert_saved_snapshot(result)
        individual = self.history.read_text(encoding="utf-8")
        self.assertTrue(individual.startswith("Earlier individual results.\n"))
        self.assertEqual(individual.count("## 评测记录"), 4)
        report = self.batch_history.read_text(encoding="utf-8")
        self.assertTrue(report.startswith("Earlier batch results.\n"))
        self.assertTrue(all(job.label in report for job in self.jobs))
        for path, original in originals.items():
            self.assertEqual(path.read_bytes(), original)

    def test_second_batch_reuses_single_file_caches_without_starting_worker(self):
        first = self.run_batch(self.winning_results)
        history_before = self.batch_history.read_text(encoding="utf-8")
        cache_before = {row["result"]["cache_file"]: Path(row["result"]["cache_file"]).read_bytes()
                        for row in first["jobs"]}

        def forbidden_runner(*args, **kwargs):
            self.fail("Complete caches must not start a judge worker")

        second = self.run_batch(forbidden_runner)
        self.assertTrue(second["complete"])
        self.assertNotEqual(second["summary_file"], first["summary_file"])
        self.assertTrue(self.batch_history.read_text(encoding="utf-8").startswith(history_before))
        self.assertGreater(self.batch_history.stat().st_size, len(history_before.encode("utf-8")))
        for row in second["jobs"]:
            self.assertEqual(row["result"]["cache_reused_rounds"], 4)
            self.assertEqual(row["result"]["new_judgments"], 0)
        for path, original in cache_before.items():
            self.assertEqual(Path(path).read_bytes(), original)

    def test_one_exception_is_recorded_and_remaining_files_still_run(self):
        calls = []

        def runner(tasks, config, attempt_dir):
            calls.append(tasks)
            if len(calls) == 2:
                raise RuntimeError("Synthetic second-file startup error")
            return self.winning_results(tasks, config, attempt_dir)

        result = self.run_batch(runner)
        self.assertEqual(len(calls), 4)
        self.assertFalse(result["complete"])
        self.assertEqual([row["status"] for row in result["jobs"]],
                         ["complete", "failed", "complete", "complete"])
        self.assertIn("Synthetic second-file startup error", result["jobs"][1]["error"])
        self.assert_saved_snapshot(result)
        self.assertIn("Synthetic second-file startup error", self.batch_history.read_text(encoding="utf-8"))

    def test_partial_judgments_are_incomplete_and_do_not_block_next_file(self):
        calls = []

        def runner(tasks, config, attempt_dir):
            calls.append(tasks)
            rows = self.winning_results(tasks, config, attempt_dir)
            return rows[:1] if len(calls) == 2 else rows

        result = self.run_batch(runner)
        self.assertEqual(len(calls), 4)
        self.assertFalse(result["complete"])
        self.assertEqual([row["status"] for row in result["jobs"]],
                         ["complete", "incomplete", "complete", "complete"])
        self.assertIsNone(result["jobs"][1]["result"]["soft_win_rate"])
        self.assertEqual(result["jobs"][1]["result"]["num_valid_samples"], 0)
        self.assert_saved_snapshot(result)

    def test_preflight_aggregates_bad_files_before_any_worker_is_started(self):
        bad = self.write_answers("bad-prompt.jsonl", "bad", wrong_prompt=True)
        missing = self.root / "missing-input.jsonl"
        self.jobs = (self.jobs[0], batch.Job("bad", bad), self.jobs[2], batch.Job("missing", missing))
        calls = []
        with self.assertRaises(ValueError) as caught:
            self.run_batch(lambda *args, **kwargs: calls.append(args))
        self.assertEqual(calls, [])
        self.assertIn("bad-prompt.jsonl", str(caught.exception))
        self.assertIn("missing-input.jsonl", str(caught.exception))
        self.assertFalse(self.history.exists())

    def test_keyboard_interrupt_preserves_snapshot_and_does_not_start_later_files(self):
        calls = []

        def runner(tasks, config, attempt_dir):
            calls.append(tasks)
            if len(calls) == 2:
                raise KeyboardInterrupt
            return self.winning_results(tasks, config, attempt_dir)

        result = self.run_batch(runner)
        self.assertEqual(len(calls), 2)
        self.assertFalse(result["complete"])
        self.assertTrue(result["interrupted"])
        self.assertEqual([row["status"] for row in result["jobs"]],
                         ["complete", "interrupted", "pending", "pending"])
        self.assert_saved_snapshot(result)
        self.assertTrue(self.batch_history.exists())

    def test_limit_smoke_test_and_full_batch_share_successful_judgments(self):
        calls = []

        def runner(tasks, config, attempt_dir):
            calls.append(len(tasks))
            return self.winning_results(tasks, config, attempt_dir)

        small = self.run_batch(runner, limit=1)
        full = self.run_batch(runner)
        self.assertTrue(small["complete"])
        self.assertTrue(full["complete"])
        self.assertEqual(calls, [2] * 8)
        self.assertTrue(all(row["result"]["cache_reused_rounds"] == 2 for row in full["jobs"]))

    def test_summary_only_never_starts_runner_with_empty_or_complete_caches(self):
        calls = []

        def forbidden_runner(*args, **kwargs):
            calls.append(args)
            self.fail("Summary-only must never start a judge worker")

        empty = self.run_batch(forbidden_runner, summary_only=True)
        self.assertEqual(calls, [])
        self.assertFalse(empty["complete"])
        self.assertEqual([row["status"] for row in empty["jobs"]], ["incomplete"] * 4)
        self.assertTrue(all(row["result"]["num_valid_samples"] == 0 for row in empty["jobs"]))
        self.assertTrue(all(row["result"]["soft_win_rate"] is None for row in empty["jobs"]))
        self.assert_saved_snapshot(empty)

        completed = self.run_batch(self.winning_results)
        self.assertTrue(completed["complete"])
        cached = self.run_batch(forbidden_runner, summary_only=True)
        self.assertEqual(calls, [])
        self.assertTrue(cached["complete"])
        self.assertEqual([row["status"] for row in cached["jobs"]], ["complete"] * 4)
        self.assertTrue(all(row["result"]["cache_reused_rounds"] == 4 for row in cached["jobs"]))
        self.assertTrue(all(row["result"]["new_judgments"] == 0 for row in cached["jobs"]))
        self.assert_saved_snapshot(cached)

    def test_input_changed_while_queued_is_rejected_without_mixed_results(self):
        calls = []

        def runner(tasks, config, attempt_dir):
            payload = json.loads(tasks[0]["messages"][-1]["content"])
            calls.append(payload["answer_a"])
            if len(calls) == 1:
                self.write_answers("candidate-1.jsonl", "changed-after-preflight")
            return self.winning_results(tasks, config, attempt_dir)

        result = self.run_batch(runner)
        self.assertEqual(calls, ["candidate-0 answer one", "candidate-2 answer one", "candidate-3 answer one"])
        self.assertFalse(result["complete"])
        self.assertEqual([row["status"] for row in result["jobs"]],
                         ["complete", "failed", "complete", "complete"])
        rejected = result["jobs"][1]
        self.assertIsNone(rejected["result"])
        self.assertIn("Input changed since batch preflight", rejected["error"])
        self.assertEqual(list(self.results.glob("candidate-1.*")), [])
        self.assert_saved_snapshot(result)


if __name__ == "__main__":
    unittest.main()
