"""Offline PIQA protocol, labeled-data and reporting checks; no real inference."""
from contextlib import redirect_stderr, redirect_stdout
import copy
import importlib.util
import io
import json
from pathlib import Path
import tempfile
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import Mock, patch


SPEC = importlib.util.spec_from_file_location("run_piqa", Path(__file__).with_name("run_piqa.py"))
entry = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(entry)


def harness_result(total=1838):
    return {
        "results": {"piqa": {"acc,none": 0.5, "acc_norm,none": 1.0}},
        "n-samples": {"piqa": {"original": total, "effective": 2}},
        "samples": {"piqa": [
            {"doc_id": 0, "acc": 1.0, "acc_norm": 1.0},
            {"doc_id": 1, "acc": 0.0, "acc_norm": 1.0},
        ]},
    }


def validation_data():
    return {"validation": [
        {"goal": "Keep water cold.", "sol1": "Use ice.", "sol2": "Use fire.", "label": 0},
        {"goal": "Make water hot.", "sol1": "Use ice.", "sol2": "Use fire.", "label": 1},
    ], "test": [{"label": -1}]}


class PiqaChecks(unittest.TestCase):
    def test_project_root_and_official_dataset(self):
        self.assertEqual(entry.ROOT, Path(__file__).resolve().parents[2])
        self.assertEqual(entry.local_path("checkpoints/example"), (entry.ROOT / "checkpoints/example").resolve())
        self.assertEqual(entry.DATASET_PATH, "baber/piqa")
        self.assertIsNone(entry.DATASET_NAME)
        self.assertEqual(entry.EVAL_SPLIT, "validation")
        self.assertEqual(entry.EXPECTED_EXAMPLES, 1838)

    def test_partial_wrong_total_duplicate_and_inconsistent_results_rejected(self):
        with self.assertRaises(ValueError):
            entry.validate_results(harness_result(), None)
        with self.assertRaises(ValueError):
            entry.validate_results(harness_result(total=2), 2)
        result = harness_result()
        result["results"]["piqa"]["acc,none"] = 0.9
        with self.assertRaises(ValueError):
            entry.validate_results(result, 2)
        for identity in (0, 9):
            result = harness_result()
            result["samples"]["piqa"][1]["doc_id"] = identity
            with self.assertRaises(ValueError):
                entry.validate_results(result, 2)
        result = harness_result()
        result["samples"]["piqa"][0]["acc_norm"] = 0.2
        with self.assertRaises(ValueError):
            entry.validate_results(result, 2)

    def test_smoke_run_units_and_counts(self):
        summary, _ = entry.validate_results(harness_result(), 2)
        self.assertTrue(summary["limited_run"])
        self.assertEqual(summary["total_validation_examples"], 1838)
        self.assertEqual(summary["evaluated_examples"], 2)
        self.assertEqual(summary["acc_correct"], 1)
        self.assertEqual(summary["acc_percent"], 50.0)
        self.assertEqual(summary["acc_norm_correct"], 2)

    def test_validation_requires_labeled_real_examples(self):
        with patch.object(entry, "EXPECTED_EXAMPLES", 2):
            entry.validate_dataset(validation_data())
            for mutation in ("label", "goal", "sol1", "sol2"):
                data = copy.deepcopy(validation_data())
                data["validation"][0][mutation] = -1 if mutation == "label" else ""
                with self.subTest(field=mutation), self.assertRaises(ValueError):
                    entry.validate_dataset(data)
            with self.assertRaises(ValueError):
                entry.validate_dataset({"test": validation_data()["validation"]})
        with self.assertRaises(ValueError):
            entry.validate_dataset(validation_data())

    def test_prepare_data_uses_same_official_cache_without_model(self):
        module = ModuleType("datasets")
        module.load_dataset = Mock(return_value=validation_data())
        with patch.dict("sys.modules", {"datasets": module}), patch.object(entry, "EXPECTED_EXAMPLES", 2), \
                patch.object(entry, "check_model_files", side_effect=AssertionError("No models in prepare-data")), redirect_stdout(io.StringIO()):
            self.assertEqual(entry.main(["--prepare-data"]), 0)
        module.load_dataset.assert_called_once_with("baber/piqa", None)

    def test_missing_weight_shard_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            model = Path(tmp)
            (model / "config.json").write_text("{}", encoding="utf-8")
            (model / "tokenizer.json").write_text("{}", encoding="utf-8")
            (model / "model.safetensors.index.json").write_text(json.dumps({"weight_map": {"layer.weight": "missing.safetensors"}}), encoding="utf-8")
            with self.assertRaises(FileNotFoundError):
                entry.check_model_files(model, model)

    def test_entrypoint_legacy_loader_protocol_and_unique_saved_results(self):
        evaluator = Mock(return_value=harness_result())
        tokenizer = Mock()
        loaded = Mock()
        loaded.to.return_value = loaded
        def legacy_load(path, *, torch_dtype, local_files_only, trust_remote_code, low_cpu_mem_usage):
            return loaded
        loader = Mock(side_effect=legacy_load)
        backend = Mock(return_value=object())
        modules = {name: ModuleType(name) for name in (
            "torch", "transformers", "lm_eval", "lm_eval.models", "lm_eval.models.huggingface", "lm_eval.utils")}
        modules["transformers"].AutoTokenizer = SimpleNamespace(from_pretrained=Mock(return_value=tokenizer))
        modules["transformers"].AutoModelForCausalLM = SimpleNamespace(from_pretrained=loader)
        modules["lm_eval"].simple_evaluate = evaluator
        modules["lm_eval.models.huggingface"].HFLM = backend
        modules["lm_eval.utils"].handle_non_serializable = str
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            model = root / "checkpoints" / "student"
            model.mkdir(parents=True)
            for name in ("config.json", "tokenizer.json", "model.safetensors"):
                (model / name).write_text("{}", encoding="utf-8")
            with patch.dict("sys.modules", modules), patch.dict("os.environ", {"WORLD_SIZE": "1"}), \
                    patch.multiple(entry, ROOT=root, RESULTS_DIR=root / "results", MODEL_PATH="checkpoints/student", TOKENIZER_PATH=None, DEVICE="cpu"), \
                    patch.object(entry, "package_versions", return_value={"lm_eval": entry.EXPECTED_HARNESS_VERSION}), redirect_stdout(io.StringIO()):
                self.assertEqual(entry.main(["--check-only"]), 0)
                loader.assert_not_called()
                evaluator.assert_not_called()
                for _ in range(2):
                    self.assertEqual(entry.main(["--limit", "2"]), 0)
            options = evaluator.call_args.kwargs
            self.assertEqual(options["tasks"], ["piqa"])
            self.assertEqual(options["num_fewshot"], 0)
            self.assertFalse(options["apply_chat_template"])
            self.assertTrue(options["log_samples"])
            self.assertEqual(loader.call_count, 2)
            self.assertEqual(loader.call_args.kwargs["torch_dtype"], entry.DTYPE)
            self.assertNotIn("dtype", loader.call_args.kwargs)
            self.assertIs(backend.call_args.kwargs["pretrained"], loaded)
            self.assertNotIn("dtype", backend.call_args.kwargs)
            summaries = list((root / "results").glob("*/*/summary.json"))
            self.assertEqual(len(summaries), 2)
            for path in summaries:
                summary = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(summary["acc_percent"], 50.0)
                self.assertEqual(summary["acc_norm_percent"], 100.0)
                self.assertEqual(summary["dataset_path"], "baber/piqa")
                self.assertEqual(summary["split"], "validation")
                self.assertFalse(summary["watermark_at_inference"])
                self.assertTrue(summary["limited_run"])
                self.assertIn("LIMITED RUN", path.with_name("report.md").read_text(encoding="utf-8"))
                self.assertEqual(len(path.with_name("samples.jsonl").read_text(encoding="utf-8").splitlines()), 2)

    def test_cli_rejects_invalid_limit_and_conflicting_modes(self):
        for argv in (["--limit", "0"], ["--prepare-data", "--check-only"]):
            with self.subTest(argv=argv), redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                entry.main(argv)


if __name__ == "__main__":
    unittest.main()
