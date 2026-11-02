"""Offline checks for reporting integrity and the harness invocation contract.

No checkpoint download, GPU, or installed inference packages are needed.
"""
import importlib.util
import json
import math
from pathlib import Path
import tempfile
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import Mock, patch


SPEC = importlib.util.spec_from_file_location("run_lambada", Path(__file__).with_name("run_lambada.py"))
entry = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(entry)


def harness_result(total=5153):
    return {
        "results": {"lambada_openai": {"acc,none": 0.5, "perplexity,none": 8.0}},
        "n-samples": {"lambada_openai": {"original": total, "effective": 2}},
        "samples": {"lambada_openai": [
            {"doc_id": 0, "acc": 1.0, "perplexity": -math.log(4.0)},
            {"doc_id": 1, "acc": 0.0, "perplexity": -math.log(16.0)},
        ]},
    }


class LambadaChecks(unittest.TestCase):
    def test_project_root_after_directory_move(self):
        self.assertEqual(entry.ROOT, Path(__file__).resolve().parents[2])
        self.assertEqual(entry.local_path("checkpoints/example"), (entry.ROOT / "checkpoints/example").resolve())

    def test_partial_or_inconsistent_scores_are_rejected(self):
        with self.assertRaises(ValueError):
            entry.validate_results(harness_result(total=5153), None)
        result = harness_result()
        result["results"]["lambada_openai"]["acc,none"] = 0.9
        with self.assertRaises(ValueError):
            entry.validate_results(result, 2)
        result = harness_result()
        result["samples"]["lambada_openai"][1]["doc_id"] = 0
        with self.assertRaises(ValueError):
            entry.validate_results(result, 2)

    def test_smoke_run_is_labeled_and_counts_are_preserved(self):
        summary, _ = entry.validate_results(harness_result(total=5153), 2)
        self.assertTrue(summary["limited_run"])
        self.assertEqual(summary["total_test_examples"], 5153)
        self.assertEqual(summary["evaluated_examples"], 2)
        self.assertEqual(summary["acc_correct"], 1)
        self.assertEqual(summary["perplexity"], 8.0)
        self.assertAlmostEqual(summary["mean_target_word_nll"], math.log(8.0))

    def test_ppl_uses_exponential_of_mean_loglikelihood(self):
        result = harness_result()
        summary, _ = entry.validate_results(result, 2)
        self.assertEqual(summary["perplexity"], 8.0)
        result["results"][entry.TASK]["perplexity,none"] = 10.0  # mean(4,16), wrong aggregation
        with self.assertRaisesRegex(ValueError, "perplexity"):
            entry.validate_results(result, 2)

    def test_nonfinite_positive_logprobs_and_invalid_accuracy_rejected(self):
        for value in (float("nan"), float("inf"), 1.0):
            result = harness_result()
            result["samples"][entry.TASK][0]["perplexity"] = value
            with self.subTest(logprob=value), self.assertRaises(ValueError):
                entry.validate_results(result, 2)
        result = harness_result()
        result["samples"][entry.TASK][0]["acc"] = 0.25
        with self.assertRaises(ValueError):
            entry.validate_results(result, 2)
        result = harness_result()
        result["results"][entry.TASK]["perplexity,none"] = float("nan")
        with self.assertRaises(ValueError):
            entry.validate_results(result, 2)

    def test_prepare_data_is_model_free_and_checks_exact_official_split(self):
        module = ModuleType("datasets")
        module.load_dataset = Mock(return_value={"test": [{"text": "The answer was Paris"}, {"text": "She returned home"}]})
        with patch.dict("sys.modules", {"datasets": module}), patch.object(entry, "EXPECTED_EXAMPLES", 2):
            with patch.object(entry, "check_model_files", side_effect=AssertionError("No model during data preparation")):
                self.assertEqual(entry.main(["--prepare-data"]), 0)
        module.load_dataset.assert_called_once_with("EleutherAI/lambada_openai", "default")
        with patch.object(entry, "EXPECTED_EXAMPLES", 1):
            for row in ({"text": ""}, {"text": "oneword"}, {"text": "A trailing space "}, {"missing": "text"}):
                with self.subTest(row=row), self.assertRaises(ValueError):
                    entry.validate_dataset({"test": [row]})
        with self.assertRaises(ValueError):
            entry.validate_dataset({"test": [{"text": "Valid context target"}]})

    def test_missing_weight_shard_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            model = Path(tmp)
            (model / "config.json").write_text("{}", encoding="utf-8")
            (model / "tokenizer.json").write_text("{}", encoding="utf-8")
            (model / "model.safetensors.index.json").write_text(
                json.dumps({"weight_map": {"layer.weight": "missing.safetensors"}}), encoding="utf-8"
            )
            with self.assertRaises(FileNotFoundError):
                entry.check_model_files(model, model)

    def test_entrypoint_contract_and_saved_results(self):
        # Exercise main/report writing with a fake inference backend. This is NOT
        # a real-model accuracy test; the numerical scoring stays in lm-eval.
        evaluator = Mock(return_value=harness_result(total=5153))
        tokenizer = Mock()
        auto_tokenizer = SimpleNamespace(from_pretrained=Mock(return_value=tokenizer))
        loaded_model = Mock()
        loaded_model.to.return_value = loaded_model

        # Reproduce the server's legacy Transformers API: dtype= is not accepted.
        def legacy_load(path, *, torch_dtype, local_files_only, trust_remote_code, low_cpu_mem_usage):
            return loaded_model

        model_loader = Mock(side_effect=legacy_load)
        backend = Mock(return_value=object())
        modules = {}
        for name in ("torch", "transformers", "lm_eval", "lm_eval.models", "lm_eval.models.huggingface", "lm_eval.utils"):
            modules[name] = ModuleType(name)
        modules["transformers"].AutoTokenizer = auto_tokenizer
        modules["transformers"].AutoModelForCausalLM = SimpleNamespace(from_pretrained=model_loader)
        modules["lm_eval"].simple_evaluate = evaluator
        modules["lm_eval.models.huggingface"].HFLM = backend
        modules["lm_eval.utils"].handle_non_serializable = str
        versions = {"lm_eval": entry.EXPECTED_HARNESS_VERSION}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            model = root / "checkpoints" / "experiment" / "actor" / "huggingface"
            model.mkdir(parents=True)
            for name in ("config.json", "tokenizer.json", "model.safetensors"):
                (model / name).write_text("{}", encoding="utf-8")
            with patch.dict("sys.modules", modules), patch.dict("os.environ", {"WORLD_SIZE": "1"}), \
                    patch.multiple(entry, ROOT=root, RESULTS_DIR=root / "results", MODEL_PATH="checkpoints/experiment/actor/huggingface", TOKENIZER_PATH=None, DEVICE="cpu"), \
                    patch.object(entry, "package_versions", return_value=versions):
                for _ in range(2):
                    self.assertEqual(entry.main(["--limit", "2"]), 0)
                self.assertEqual(entry.main(["--check-only"]), 0)
            options = evaluator.call_args.kwargs
            self.assertEqual(options["tasks"], ["lambada_openai"])
            self.assertEqual(options["num_fewshot"], 0)
            self.assertFalse(options["apply_chat_template"])
            self.assertTrue(options["log_samples"])
            self.assertEqual(model_loader.call_count, 2)  # Exactly one load per run.
            self.assertEqual(evaluator.call_count, 2)  # check-only never evaluates.
            self.assertEqual(model_loader.call_args.args, (str(model.resolve()),))
            self.assertTrue(model_loader.call_args.kwargs["local_files_only"])
            self.assertEqual(model_loader.call_args.kwargs["torch_dtype"], entry.DTYPE)
            self.assertNotIn("dtype", model_loader.call_args.kwargs)
            self.assertIs(backend.call_args.kwargs["pretrained"], loaded_model)
            self.assertNotIn("dtype", backend.call_args.kwargs)
            loaded_model.to.assert_called_with("cpu")
            self.assertEqual(loaded_model.eval.call_count, 2)
            reports = list((root / "results").glob("*/*/summary.json"))
            self.assertEqual(len(reports), 2)  # Repeated runs must not overwrite.
            for report in reports:
                summary = json.loads(report.read_text(encoding="utf-8"))
                self.assertEqual(summary["acc_percent"], 50.0)
                self.assertEqual(summary["perplexity"], 8.0)
                self.assertFalse(summary["watermark_at_inference"])
                self.assertEqual(summary["output_type"], "loglikelihood")
                self.assertTrue(summary["limited_run"])
                self.assertIn("LIMITED RUN", report.with_name("report.md").read_text(encoding="utf-8"))
                self.assertEqual(len(report.with_name("samples.jsonl").read_text(encoding="utf-8").splitlines()), 2)


if __name__ == "__main__":
    unittest.main()
