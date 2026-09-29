"""No credentials, external API, GPU, or third-party packages required."""
import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import evaluate_quality as eq


def scoring(a=6, b=8):
    return {"assistant_a": {d: a for d in eq.DIMENSIONS},
            "assistant_b": {d: b for d in eq.DIMENSIONS}, "explanation": "Test-only deterministic judge"}


class FakeClient(eq.APIClient):
    total_calls = 0

    def complete(self, payload):
        if self.calls >= self.args.max_api_calls:
            raise eq.FatalAPIError("Test budget exhausted")
        self.calls += 1
        FakeClient.total_calls += 1
        if "response_format" in payload:
            data = json.loads(payload["messages"][-1]["content"])
            grade = lambda text: {"base answer": 4, "warmup answer": 6,
                                  "gad answer": 7, "reference answer": 8}[text]
            content = json.dumps(scoring(grade(data["assistant_a"]), grade(data["assistant_b"])))
        else:
            content = "reference answer"
        return {"content": content, "usage": {"total_tokens": 20},
                "actual_model": "fake-gpt-4o", "response_id": "fake-response"}


class QualityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.files = {}
        for label in ("base", "warmup", "gad"):
            path = self.root / (label + ".jsonl")
            rows = [{"id": str(i), "prompt": [{"role": "user", "content": f"Question {i}"}],
                     "answer": label + " answer", "generation": {"temperature": .7, "seed": i},
                     "num_tokens": 5} for i in range(2)]
            path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
            self.files[label] = path
        self.argv = ["--output-dir", str(self.root / "results"), "--bootstrap", "50"]
        for label, path in self.files.items():
            self.argv += ["--model", f"{label}={path}"]
        FakeClient.total_calls = 0

    def run_main(self, extra=()):
        with patch.object(eq, "APIClient", FakeClient), patch.dict(os.environ, {"OPENAI_API_KEY": "test-not-a-real-key"}), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return eq.main(self.argv + list(extra))

    def metrics(self):
        return json.loads((self.root / "results/metrics.json").read_text(encoding="utf-8"))

    def test_dry_run_has_no_writes_or_calls(self):
        self.assertEqual(self.run_main(), 0)
        self.assertEqual(FakeClient.total_calls, 0)
        self.assertFalse((self.root / "results").exists())

    def test_paper_scores_and_resume_and_summary_without_calls(self):
        self.assertEqual(self.run_main(["--run-api"]), 0)
        self.assertEqual(FakeClient.total_calls, 14)  # 2 references + 2*3*2 judges.
        metrics = self.metrics()
        self.assertTrue(metrics["complete"])
        self.assertAlmostEqual(metrics["comparisons"]["gad vs reference"]["left_relative_score"]["mean"], 100*7/15)
        self.assertAlmostEqual(metrics["comparisons"]["warmup vs reference"]["left_relative_score"]["mean"], 100*6/14)
        self.assertEqual(self.run_main(["--run-api"]), 0)
        self.assertEqual(self.run_main(["--summary-only"]), 0)
        self.assertEqual(FakeClient.total_calls, 14)

    def test_pairwise_swapping_and_resume(self):
        args = ["--mode", "pairwise", "--run-api"]
        self.assertEqual(self.run_main(args), 0)
        data = self.metrics()["comparisons"]["gad vs warmup"]
        self.assertEqual(data["left_win_rate"], 1)
        self.assertEqual(data["order_agreement_rate"], 1)
        self.assertAlmostEqual(data["left_minus_right"]["mean"], 1)
        self.assertEqual(self.run_main(args), 0)
        self.assertEqual(FakeClient.total_calls, 4)

    def test_limit_can_extend_without_rejudging_old_samples(self):
        self.assertEqual(self.run_main(["--limit", "1", "--run-api"]), 0)
        self.assertEqual(FakeClient.total_calls, 7)
        self.assertEqual(self.run_main(["--run-api"]), 0)
        self.assertEqual(FakeClient.total_calls, 14)

    def test_budget_preserves_cache_and_excludes_incomplete_pair(self):
        self.assertEqual(self.run_main(["--run-api", "--max-api-calls", "2"]), 2)
        self.assertFalse(self.metrics()["complete"])
        self.assertEqual(self.metrics()["comparisons"], {})
        self.assertEqual(self.run_main(["--run-api"]), 0)
        self.assertEqual(FakeClient.total_calls, 14)

    def test_changed_configuration_cannot_mix_results(self):
        self.run_main(["--run-api"])
        with self.assertRaisesRegex(ValueError, "different inputs/settings"):
            self.run_main(["--summary-only", "--judge-model", "different-model"])

    def test_missing_ids_and_different_prompts_and_settings_fail(self):
        datasets = {label: eq.load_dataset(path) for label, path in self.files.items()}
        del datasets["gad"]["1"]
        with self.assertRaisesRegex(ValueError, "IDs differ"):
            eq.align_datasets(datasets)
        datasets["gad"] = eq.load_dataset(self.files["gad"])
        datasets["gad"]["0"]["prompt"][0]["content"] = "different"
        with self.assertRaisesRegex(ValueError, "Different prompts"):
            eq.align_datasets(datasets)
        datasets["gad"] = eq.load_dataset(self.files["gad"])
        datasets["gad"]["0"]["generation"]["temperature"] = 1
        with self.assertRaisesRegex(ValueError, "generation settings"):
            eq.align_datasets(datasets)
        eq.align_datasets(datasets, allow_mismatch=True)

    def test_duplicate_id_rejected(self):
        path = self.files["base"]
        path.write_text(path.read_text(encoding="utf-8") * 2, encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "duplicate id"):
            eq.load_dataset(path)

    def test_invalid_scores_and_boolean_and_nan_rejected(self):
        for value in (0, 11, True, float("nan")):
            with self.assertRaises(ValueError):
                eq.validate_scores(json.dumps(scoring(value, 8)))
        self.assertEqual(eq.validate_scores("```json\n" + json.dumps(scoring()) + "\n```")["assistant_a"]["overall"], 6)

    def test_api_http_and_schema_without_network(self):
        class Reply(io.BytesIO):
            def __enter__(self):
                return self
            def __exit__(self, *args):
                self.close()
        args = eq.parse_args([])
        client = eq.APIClient(args)
        client.key = "test-only"
        body = {"choices": [{"finish_reason": "stop", "message": {"content": json.dumps(scoring())}}]}
        with patch.object(eq.request, "urlopen", return_value=Reply(json.dumps(body).encode())) as mock:
            response = client.complete(client.payload([], True))
        self.assertEqual(eq.validate_scores(response["content"])["assistant_b"]["overall"], 8)
        sent = json.loads(mock.call_args.args[0].data)
        self.assertTrue(sent["response_format"]["json_schema"]["strict"])
        self.assertFalse(sent["store"])

    def test_supplied_reference_file_skips_reference_api(self):
        path = self.root / "provided_references.jsonl"
        rows = eq.read_jsonl(self.files["base"])
        for row in rows:
            row["answer"] = "reference answer"
        path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
        self.assertEqual(self.run_main(["--run-api", "--reference-file", str(path)]), 0)
        self.assertEqual(FakeClient.total_calls, 12)

    def test_active_lock_and_source_output_collision_rejected(self):
        self.run_main(["--run-api"])
        lock = self.root / "results/.evaluation.lock"
        lock.write_text("12345", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "another run"):
            self.run_main(["--summary-only"])
        self.assertTrue(lock.exists())


if __name__ == "__main__":
    unittest.main()
