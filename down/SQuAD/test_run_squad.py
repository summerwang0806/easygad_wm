"""SQuAD metric/coverage and resumable workflow checks; no real GPU needed."""
from contextlib import redirect_stderr, redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import tempfile
from types import ModuleType
import unittest
from unittest.mock import Mock, patch


SPEC = importlib.util.spec_from_file_location("run_squad", Path(__file__).with_name("run_squad.py"))
entry = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(entry)


def questions():
    return [
        {"id": "q1", "title": "Places", "context": "New York and London.", "question": "Name the first city.", "references": ["New York"]},
        {"id": "q2", "title": "Places", "context": "New York and London.", "question": "Name the second city.", "references": ["London"]},
    ]


def fixture():
    return {"version": "1.1", "data": [{"title": "Places", "paragraphs": [{
        "context": "New York and London.", "qas": [
            {"id": "q1", "question": "Name the first city.", "answers": [{"text": "New York", "answer_start": 0}]},
            {"id": "q2", "question": "Name the second city.", "answers": [{"text": "London", "answer_start": 13}]},
        ]}]}]}


class SquadChecks(unittest.TestCase):
    def test_original_v11_normalization(self):
        self.assertEqual(entry.normalize_answer("  The NEW-YORK, an apple!  "), "newyork apple")
        self.assertEqual(entry.exact_match_score("The New York!", "new york"), 1.0)
        self.assertAlmostEqual(entry.f1_score("New York City", "New York"), 0.8)
        self.assertAlmostEqual(entry.f1_score("cat cat dog", "cat dog dog"), 2 / 3)
        self.assertEqual(entry.f1_score("", "New York"), 0.0)
        # Original v1.1 returns 0 when overlap count is 0, even when both
        # normalized strings are empty. Do not silently substitute v2 behavior.
        self.assertEqual(entry.f1_score("the", "a"), 0.0)
        self.assertEqual(entry.exact_match_score("the", "a"), 1.0)

    def test_multiple_references_and_no_hidden_extraction(self):
        self.assertEqual(entry.score_answer("London", ["New York", "London"]), {"exact_match": 1.0, "f1": 1.0})
        result = entry.score_answer("The answer is London.", ["London"])
        self.assertEqual(result["exact_match"], 0.0)
        self.assertLess(result["f1"], 1.0)
        with self.assertRaises(ValueError):
            entry.score_answer("London", [])

    def test_dataset_version_ids_and_answer_spans(self):
        self.assertEqual(len(entry.parse_dataset(fixture(), expected_count=None)), 2)
        document = fixture()
        document["version"] = "2.0"
        with self.assertRaises(ValueError):
            entry.parse_dataset(document, expected_count=None)
        document = fixture()
        document["data"][0]["paragraphs"][0]["qas"][1]["id"] = "q1"
        with self.assertRaises(ValueError):
            entry.parse_dataset(document, expected_count=None)
        document = fixture()
        document["data"][0]["paragraphs"][0]["qas"][0]["answers"][0]["answer_start"] = -1
        with self.assertRaises(ValueError):
            entry.parse_dataset(document, expected_count=None)
        # EM/F1 use gold text; offset-text quirks do not change gold answers.
        document["data"][0]["paragraphs"][0]["qas"][0]["answers"][0]["answer_start"] = 2
        self.assertEqual(entry.parse_dataset(document, expected_count=None)[0]["references"], ["New York"])

    def test_prediction_coverage_is_exact(self):
        rows = questions()
        with self.assertRaises(ValueError):
            entry.evaluate_predictions(rows, {"q1": "New York"})
        with self.assertRaises(ValueError):
            entry.evaluate_predictions(rows, {"q1": "New York", "q2": "London", "other": "x"})
        result, scores = entry.evaluate_predictions(rows, {"q1": "New York City", "q2": "London"})
        self.assertEqual(result["exact_match"], 50.0)
        self.assertAlmostEqual(result["f1"], 90.0)
        self.assertEqual(scores[0]["prediction"], "New York City")

    def test_project_root_and_prompt_styles(self):
        self.assertEqual(entry.ROOT, Path(__file__).resolve().parents[2])
        self.assertEqual(entry.resolve_path("checkpoints/test"), (entry.ROOT / "checkpoints/test").resolve())
        with patch.object(entry, "PROMPT_STYLE", "chat"):
            prompt = entry.make_prompt(questions()[0])
            self.assertEqual(prompt[0]["role"], "user")
        with patch.object(entry, "PROMPT_STYLE", "completion"):
            self.assertIsInstance(entry.make_prompt(questions()[0]), str)

    def test_fewshot_prompt_roles_and_no_evaluation_gold_injection(self):
        example = {"id": "train-1", "title": "Training", "context": "Oxford is a city.",
                   "question": "Which city?", "answer": "Oxford"}
        row = {**questions()[0], "references": ["GOLD_MUST_NOT_BE_INJECTED"]}
        with patch.object(entry, "PROMPT_STYLE", "chat"):
            messages = entry.make_prompt(row, [example] * 3)
            self.assertEqual([item["role"] for item in messages], ["user", "assistant"] * 3 + ["user"])
            self.assertTrue(all(messages[index]["content"] == "Oxford" for index in (1, 3, 5)))
            self.assertNotIn("GOLD_MUST_NOT_BE_INJECTED", json.dumps(messages))
        with patch.object(entry, "PROMPT_STYLE", "completion"):
            prompt = entry.make_prompt(row, [example])
            self.assertIn("Answer: Oxford", prompt)
            self.assertTrue(prompt.endswith("Answer:"))
            self.assertNotIn("GOLD_MUST_NOT_BE_INJECTED", prompt)

    def test_training_examples_have_fixed_provenance_and_no_dev_ids(self):
        document = {"version": "1.1", "data": [{"title": f"Training {number}", "paragraphs": [{
            "context": f"Oxford is a city in passage {number}.", "qas": [{
                "id": "q1" if number == 0 else f"train-{number}", "question": "Which city?",
                "answers": [{"text": "Oxford", "answer_start": 0}],
            }]}]} for number in range(5)]}
        with tempfile.TemporaryDirectory(dir=entry.HERE) as tmp:
            path = Path(tmp) / "train-v1.1.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            with patch.multiple(entry, TRAIN_DATASET_FILE=path, EXPECTED_TRAIN_COUNT=5), redirect_stdout(io.StringIO()):
                examples, provenance = entry.prepare_examples(3, questions(), check_only=True)
                self.assertEqual((examples, provenance), entry.prepare_examples(3, list(reversed(questions())), check_only=True))
            self.assertEqual(provenance["source_split"], "train")
            self.assertEqual(provenance["num_fewshot"], 3)
            self.assertEqual(len(provenance["train_sha256"]), 64)
            self.assertEqual(len({item["title"] for item in examples}), 3)
            self.assertNotIn("q1", {item["id"] for item in examples})

    def test_zero_shot_and_score_only_do_not_require_training_data(self):
        with patch.object(entry, "prepare_data", side_effect=AssertionError("TRAIN must not be accessed")), \
                patch.dict("sys.modules", {"fewshot": None}):
            examples, provenance = entry.prepare_examples(0, questions())
            self.assertEqual(examples, [])
            self.assertIsNone(provenance["train_sha256"])
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "missing-train.json"
            with patch.object(entry, "TRAIN_DATASET_FILE", missing), patch.object(entry, "prepare_data") as download:
                with self.assertRaisesRegex(FileNotFoundError, "prepare-data"):
                    entry.prepare_examples(3, questions(), check_only=True)
                download.assert_not_called()

    def test_zero_and_three_shot_use_separate_caches(self):
        runtime = ModuleType("generation_utils")
        backend = Mock()
        backend.check.return_value = {"model": {}, "tokenizer": {}, "versions": {}, "chat_template_present": True}
        backend.generate.return_value = {"text": "New York", "finish_reason": "stop"}
        runtime.LocalGenerator = Mock(return_value=backend)
        runtime.sha256_file = lambda path: "fake"
        example = {"id": "train", "title": "Training", "context": "Oxford is a city.", "question": "Which city?", "answer": "Oxford"}
        def prepared(count, rows, **kwargs):
            demos = [example] * count
            return demos, {"num_fewshot": count, "examples": demos, "train_sha256": "train-hash" if count else None}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "dev.json"
            path.write_text("{}", encoding="utf-8")
            with patch.multiple(entry, DATASET_FILE=path, RESULTS_DIR=Path(tmp) / "results"), \
                    patch.object(entry, "load_data", return_value=questions()), \
                    patch.object(entry, "prepare_examples", side_effect=prepared), \
                    patch.dict("sys.modules", {"generation_utils": runtime}), redirect_stdout(io.StringIO()):
                self.assertEqual(entry.main(["--limit", "1", "--num-fewshot", "3"]), 0)
                self.assertEqual(entry.main(["--limit", "1", "--num-fewshot", "0"]), 0)
                self.assertEqual(entry.main(["--limit", "1", "--num-fewshot", "3"]), 0)
            self.assertEqual(backend.generate.call_count, 2)
            self.assertEqual(len(backend.generate.call_args_list[0].args[0]), 7)
            self.assertEqual(len(backend.generate.call_args_list[1].args[0]), 1)
            self.assertEqual(len(list((Path(tmp) / "results").glob("*/generations.jsonl"))), 2)
            summaries = [json.loads(p.read_text(encoding="utf-8")) for p in (Path(tmp) / "results").glob("*/runs/*/summary.json")]
            self.assertEqual({s["num_fewshot"] for s in summaries}, {0, 3})
            self.assertEqual(sum(s["reused_answers"] for s in summaries), 1)

    def test_smoke_to_full_resume_preserves_raw_answers(self):
        runtime = ModuleType("generation_utils")
        backend = Mock()
        backend.check.return_value = {"model": {"path": "fake"}, "tokenizer": {"path": "fake"},
                                      "versions": {"transformers": "fake"}, "runtime_sha256": "fake",
                                      "chat_template_present": True}
        backend.generate.side_effect = [
            {"text": "New York City", "finish_reason": "length", "prompt_tokens": 10, "completion_tokens": 3},
            {"text": "London", "finish_reason": "stop", "prompt_tokens": 10, "completion_tokens": 1},
        ]
        runtime.LocalGenerator = Mock(return_value=backend)
        runtime.model_fingerprint = lambda path: {"path": str(path)}
        runtime.tokenizer_fingerprint = lambda path: {"path": str(path)}
        runtime.sha256_file = lambda path: "fakehash"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data_path = root / "dev-v1.1.json"
            data_path.write_text(json.dumps(fixture()), encoding="utf-8")
            with patch.multiple(entry, ROOT=root, DATASET_FILE=data_path, RESULTS_DIR=root / "results"), \
                    patch.object(entry, "load_data", return_value=questions()), \
                    patch.dict("sys.modules", {"generation_utils": runtime}), redirect_stdout(io.StringIO()):
                self.assertEqual(entry.main(["--limit", "1"]), 0)
                self.assertEqual(entry.main([]), 0)
            self.assertEqual(backend.generate.call_count, 2)
            self.assertEqual(backend.close.call_count, 2)
            self.assertTrue(all(len(call.args[0]) == 1 and call.args[0][0]["role"] == "user"
                                for call in backend.generate.call_args_list))
            summaries = [json.loads(path.read_text(encoding="utf-8")) for path in (root / "results").glob("*/runs/*/summary.json")]
            self.assertEqual(len(summaries), 2)
            full = next(row for row in summaries if not row["limited_run"])
            self.assertEqual(full["reused_answers"], 1)
            self.assertEqual(full["exact_match"], 50.0)
            self.assertAlmostEqual(full["f1"], 90.0)
            self.assertEqual(full["length_limited_predictions"], 1)
            self.assertEqual(full["num_fewshot"], 0)
            self.assertEqual(full["fewshot"]["examples"], [])
            self.assertIsNone(full["fewshot"]["train_sha256"])
            cache = next((root / "results").glob("*/generations.jsonl"))
            lines = [json.loads(line) for line in cache.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(len(lines), 2)
            self.assertEqual(lines[0]["raw_prediction"], "New York City")

    def test_scoring_existing_predictions_does_not_load_generator(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data_path = root / "dev.json"
            data_path.write_text("{}", encoding="utf-8")
            predictions = root / "predictions.json"
            predictions.write_text(json.dumps({"q1": "New York", "q2": "London"}), encoding="utf-8")
            with patch.multiple(entry, ROOT=root, DATASET_FILE=data_path, RESULTS_DIR=root / "results"), \
                    patch.object(entry, "load_data", return_value=questions()), \
                    patch.object(entry, "prepare_examples", side_effect=AssertionError("No TRAIN in score-only")), redirect_stdout(io.StringIO()):
                self.assertEqual(entry.main(["--score-only", "--predictions-file", str(predictions)]), 0)
            result = json.loads(next((root / "results").glob("external/runs/*/summary.json")).read_text(encoding="utf-8"))
            self.assertEqual(result["exact_match"], 100.0)
            self.assertEqual(result["f1"], 100.0)

    def test_check_only_rejects_missing_chat_template(self):
        runtime = ModuleType("generation_utils")
        backend = Mock()
        backend.check.return_value = {"chat_template_present": False}
        runtime.LocalGenerator = Mock(return_value=backend)
        runtime.sha256_file = Mock(return_value="fake")
        with tempfile.TemporaryDirectory() as tmp:
            data_path = Path(tmp) / "dev.json"
            data_path.write_text("{}", encoding="utf-8")
            with patch.object(entry, "DATASET_FILE", data_path), \
                    patch.object(entry, "load_data", return_value=questions()), \
                    patch.dict("sys.modules", {"generation_utils": runtime}):
                with self.assertRaisesRegex(ValueError, "chat_template"):
                    entry.main(["--check-only"])
        backend.generate.assert_not_called()
        backend.close.assert_called_once()

    def test_prepare_data_downloads_once_validates_and_preserves_existing(self):
        response = Mock()
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        response.read.return_value = json.dumps(fixture()).encode("utf-8")
        with tempfile.TemporaryDirectory(dir=entry.HERE) as tmp:
            path = Path(tmp) / "data" / "dev-v1.1.json"
            real_parse = entry.parse_dataset
            with patch.object(entry, "urlopen", return_value=response) as request, \
                    patch.object(entry, "parse_dataset", side_effect=lambda doc, **kwargs: real_parse(doc, expected_count=None)), \
                    patch.object(entry, "load_data", return_value=questions()), redirect_stdout(io.StringIO()):
                self.assertEqual(len(entry.prepare_data(path)), 2)
                saved = path.read_bytes()
                self.assertEqual(len(entry.prepare_data(path)), 2)
                self.assertEqual(path.read_bytes(), saved)
                request.assert_called_once_with(entry.DATASET_URL, timeout=90)
                self.assertFalse(list(path.parent.glob("*.tmp")))

    def test_cli_requires_consistent_exclusive_modes(self):
        invalid = [
            ["--score-only"], ["--predictions-file", "answers.json"],
            ["--prepare-data", "--score-only", "--predictions-file", "answers.json"],
            ["--prepare-data", "--check-only"], ["--limit", "0"],
            ["--num-fewshot", "-1"],
        ]
        for argv in invalid:
            with self.subTest(argv=argv), redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as error:
                    entry.main(argv)
                self.assertEqual(error.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
