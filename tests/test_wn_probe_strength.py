"""CPU checks for the probe runner and its explicitly proportional mapping."""

from contextlib import nullcontext, redirect_stderr, redirect_stdout
import io
import json
import math
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from wn import probe_strength as runner


class Matrix:
    """Small tensor stand-in: enough to audit generation batching without torch."""

    def __init__(self, rows):
        self.rows = rows
        self.shape = (len(rows), len(rows[0]))

    def repeat(self, count, columns):
        assert columns == 1
        return Matrix(self.rows * count)

    def __getitem__(self, index):
        row_slice, column_slice = index
        return Matrix([row[column_slice] for row in self.rows[row_slice]])

    def cpu(self):
        return self

    def tolist(self):
        return self.rows


class Tokenizer:
    pad_token_id = None
    eos_token_id = 6

    def __len__(self):
        return 7

    def __call__(self, prompt, **kwargs):
        class Batch(dict):
            def to(self, device):
                return self

        return Batch(input_ids=Matrix([[4, 5]]), attention_mask=Matrix([[1, 1]]))


class ProbeStrengthTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix=".probe_runner_test_", dir=runner.ROOT)
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        self.student = self.directory / "student"
        self.reference = self.directory / "reference"
        self.tokenizer_path = self.directory / "tokenizer"
        config = {"model_type": "qwen2", "vocab_size": 7, "hidden_size": 4, "num_hidden_layers": 2}
        for model in (self.student, self.reference):
            model.mkdir()
            (model / "config.json").write_text(json.dumps(config), encoding="utf-8")
        self.tokenizer_path.mkdir()
        self.output = self.directory / "runs"
        self.history = self.directory / "history.md"
        self.argv = ["--student-model", str(self.student), "--reference-model", str(self.reference),
                     "--tokenizer", str(self.tokenizer_path), "--output-dir", str(self.output),
                     "--history", str(self.history)]
        self.tokenizer = Tokenizer()
        self.auto_tokenizer = Mock()
        self.auto_tokenizer.from_pretrained.return_value = self.tokenizer
        self.transformers = SimpleNamespace(AutoTokenizer=self.auto_tokenizer)

    def test_mapping_is_exactly_proportional_and_not_a_rounded_grid(self):
        value = runner.select_strength(.1694, .1366, 2.5)
        self.assertAlmostEqual(value, 2.5 * .1694 / .1366)
        self.assertGreater(value, 3.1)
        self.assertNotEqual(value, 3.0)
        self.assertEqual(runner.select_strength(.1, .1, 2.5), 2.5)
        self.assertEqual(runner.select_strength(.05, .1, 2.5), 1.25)

    def test_invalid_or_nonpositive_scores_cannot_produce_a_strength(self):
        for invalid in (0, -0.1, 1.01, math.inf, -math.inf, math.nan):
            for index in (0, 1):
                values = [.2, .1, 2.5]
                values[index] = invalid
                with self.subTest(index=index, invalid=invalid), self.assertRaises(ValueError):
                    runner.select_strength(*values)
        for invalid in (0, -1, math.inf, math.nan):
            with self.subTest(strength=invalid), self.assertRaises(ValueError):
                runner.select_strength(.2, .1, invalid)

    def test_dry_run_reports_two_model_budget_and_writes_nothing(self):
        output = io.StringIO()
        with patch.dict(sys.modules, {"transformers": self.transformers}), \
                patch.object(runner, "collect_model") as collect, redirect_stdout(output):
            self.assertEqual(runner.main(self.argv + ["--dry-run"]), 0)
        plan = json.loads(output.getvalue())
        self.assertEqual(plan["total_short_generations"], 80000)
        self.assertEqual(plan["samples_per_prompt"], 20000)
        self.assertEqual(plan["threshold"], 20)
        self.assertEqual(plan["repeats"], 1)
        self.assertEqual(len(plan["prompts"]), 2)
        self.assertFalse(self.output.exists())
        self.assertFalse(self.history.exists())
        collect.assert_not_called()
        self.auto_tokenizer.from_pretrained.assert_not_called()

    def test_supplied_reference_score_halves_the_dry_run_budget(self):
        argv = self.argv.copy()
        index = argv.index("--reference-model")
        argv[index:index + 2] = ["--reference-score", ".1366"]
        output = io.StringIO()
        with redirect_stdout(output):
            runner.main(argv + ["--samples-per-prompt", "11", "--dry-run"])
        plan = json.loads(output.getvalue())
        self.assertIsNone(plan["reference_model"])
        self.assertEqual(plan["total_short_generations"], 22)
        self.assertFalse(self.output.exists())

    def test_target_and_reference_cannot_be_the_same_checkpoint(self):
        argv = self.argv.copy()
        index = argv.index("--reference-model")
        argv[index + 1] = str(self.student / ".." / "student")
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            runner.parse_args(argv)
        self.assertFalse(self.output.exists())

    def test_two_successful_runs_append_history_and_keep_both_result_files(self):
        statistics = [{"score": .1694}, {"score": .1366}, {"score": .08}, {"score": .1}]
        output = io.StringIO()
        with patch.dict(sys.modules, {"transformers": self.transformers}), \
                patch.object(runner, "collect_model", side_effect=statistics) as collect, \
                redirect_stdout(output):
            runner.main(self.argv)
            runner.main(self.argv)
        results = [json.loads(path.read_text(encoding="utf-8"))
                   for path in self.output.glob("*/result.json")]
        self.assertEqual(len(results), 2)
        self.assertEqual(len({row["run_id"] for row in results}), 2)
        self.assertTrue(all(row["status"] == "ok" for row in results))
        strengths = sorted(row["selected_strength"] for row in results)
        self.assertAlmostEqual(strengths[0], 2.0)
        self.assertAlmostEqual(strengths[1], 2.5 * .1694 / .1366)
        text = self.history.read_text(encoding="utf-8")
        self.assertEqual(text.count("## "), 2)
        self.assertEqual(text.count("# WN 探针与比例选强度记录"), 1)
        self.assertEqual(collect.call_count, 4)
        self.assertEqual([call.args[-1] for call in collect.call_args_list],
                         ["student", "reference", "student", "reference"])
        self.assertTrue(all(call.args[1] is self.tokenizer for call in collect.call_args_list))

    def test_model_failure_records_null_and_preserves_exception(self):
        with patch.dict(sys.modules, {"transformers": self.transformers}), \
                patch.object(runner, "collect_model", side_effect=RuntimeError("sampling failed")), \
                self.assertRaisesRegex(RuntimeError, "sampling failed"):
            runner.main(self.argv)
        paths = list(self.output.glob("*/result.json"))
        self.assertEqual(len(paths), 1)
        report = json.loads(paths[0].read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "error")
        self.assertIsNone(report["selected_strength"])
        self.assertEqual(report["error"], "RuntimeError: sampling failed")
        self.assertIn('"selected_strength": null', self.history.read_text(encoding="utf-8"))

    def test_invalid_measured_score_records_null_instead_of_fabricating_strength(self):
        with patch.dict(sys.modules, {"transformers": self.transformers}), \
                patch.object(runner, "collect_model", side_effect=[{"score": -.01}, {"score": .1}]), \
                self.assertRaisesRegex(ValueError, "score must be positive"):
            runner.main(self.argv)
        report = json.loads(next(self.output.glob("*/result.json")).read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "error")
        self.assertIsNone(report["selected_strength"])

    def test_collect_model_samples_exact_tail_batch_without_eos_stopping(self):
        calls = []

        class Model:
            config = SimpleNamespace(max_position_embeddings=1000)

            def to(self, device):
                return self

            def eval(self):
                return self

            def get_output_embeddings(self):
                return SimpleNamespace(weight=SimpleNamespace(shape=(9, 4)))

            def generate(self, **kwargs):
                calls.append(kwargs)
                return Matrix([row + [1, 2] for row in kwargs["input_ids"].rows])

        torch = SimpleNamespace(device=lambda value: SimpleNamespace(type="cpu"), float32="float32",
                                manual_seed=Mock(), inference_mode=nullcontext)
        transformers = SimpleNamespace(AutoModelForCausalLM=SimpleNamespace(
            from_pretrained=Mock(return_value=Model())), GenerationConfig=SimpleNamespace)
        args = runner.parse_args(self.argv + ["--device", "cpu", "--samples-per-prompt", "5",
                                              "--batch-size", "2", "--threshold", "1"])
        run_dir = self.directory / "sample-run"
        run_dir.mkdir()
        with patch.dict(sys.modules, {"torch": torch, "transformers": transformers}), \
                patch.object(runner, "build_prefix_trie", return_value=({1: {"_prefix": " A"}}, 1)), \
                patch.object(runner, "score_distributions", return_value={"score": .2}) as score, \
                redirect_stderr(io.StringIO()):
            report = runner.collect_model(self.student, self.tokenizer, args, run_dir, "student")
        self.assertEqual([call["input_ids"].shape[0] for call in calls], [2, 2, 1, 2, 2, 1])
        for call in calls:
            config = call["generation_config"]
            self.assertEqual(config.eos_token_id, [])
            self.assertEqual(config.pad_token_id, 6)
            self.assertEqual(config.suppress_tokens, [7, 8])
            self.assertEqual(config.max_new_tokens, 2)
            self.assertEqual((config.temperature, config.top_p, config.top_k), (1.0, 1.0, 0))
        self.assertEqual([row["attempted"] for row in report["sampling"]], [5, 5])
        self.assertEqual([row["valid"] for row in report["sampling"]], [5, 5])
        self.assertEqual(score.call_args.kwargs, {"vocab_size": 7, "threshold": 1})
        self.assertEqual(score.call_args.args, ({" A": {2: 5}}, {" A": {2: 5}}))
        for index in (1, 2):
            lines = (run_dir / f"student_p{index}.samples.jsonl").read_text(encoding="utf-8").splitlines()
            self.assertEqual([json.loads(line)["index"] for line in lines], list(range(5)))


if __name__ == "__main__":
    unittest.main()
