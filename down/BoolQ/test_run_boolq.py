"""Offline protocol/reporting tests; no real model weights, CUDA, or downloads."""
from contextlib import redirect_stderr, redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import tempfile
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import Mock, patch


SPEC = importlib.util.spec_from_file_location("run_boolq", Path(__file__).with_name("run_boolq.py"))
entry = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(entry)


def document(label):
    return {"label": label, "passage": "London is a city in England.", "question": "Is London a city"}


def result(total=3270):
    return {"results": {"boolq": {"acc,none": 0.5, "acc_stderr,none": 0.1}},
            "n-samples": {"boolq": {"original": total, "effective": 2}},
            "samples": {"boolq": [{"doc_id": 0, "doc": document(1), "acc": 1},
                                   {"doc_id": 1, "doc": document(0), "acc": 0}]}}


def fake_backend():
    evaluator = Mock(return_value=result())
    tokenizer = Mock()
    model = Mock()
    model.to.return_value = model

    def legacy_load(path, *, torch_dtype, local_files_only, trust_remote_code, low_cpu_mem_usage):
        return model

    loader = Mock(side_effect=legacy_load)
    backend = Mock(return_value=object())
    modules = {name: ModuleType(name) for name in (
        "torch", "transformers", "lm_eval", "lm_eval.models", "lm_eval.models.huggingface", "lm_eval.utils")}
    modules["transformers"].AutoTokenizer = SimpleNamespace(from_pretrained=Mock(return_value=tokenizer))
    modules["transformers"].AutoModelForCausalLM = SimpleNamespace(from_pretrained=loader)
    modules["lm_eval"].simple_evaluate = evaluator
    modules["lm_eval.models.huggingface"].HFLM = backend
    modules["lm_eval.utils"].handle_non_serializable = str
    return modules, evaluator, model, loader, backend


class BoolQChecks(unittest.TestCase):
    def test_project_root_and_dataset_contract(self):
        self.assertEqual(entry.ROOT, Path(__file__).resolve().parents[2])
        self.assertEqual(entry.local_path("checkpoints/test"), (entry.ROOT / "checkpoints/test").resolve())
        self.assertEqual((entry.TASK, entry.DATASET_PATH, entry.DATASET_NAME, entry.EVAL_SPLIT),
                         ("boolq", "super_glue", "boolq", "validation"))

    def test_partial_duplicate_invalid_and_inconsistent_results_fail(self):
        cases = []
        item = result(); item["n-samples"]["boolq"]["effective"] = 1; cases.append(item)
        item = result(); item["samples"]["boolq"][1]["doc_id"] = 0; cases.append(item)
        item = result(); item["samples"]["boolq"][1]["acc"] = .5; cases.append(item)
        item = result(); item["results"]["boolq"]["acc,none"] = .9; cases.append(item)
        item = result(); item["results"]["boolq"]["acc,none"] = float("nan"); cases.append(item)
        cases.append(result(total=2))
        for item in cases:
            with self.subTest(item=item), self.assertRaises(ValueError):
                entry.validate_results(item, 2)
        with self.assertRaises(ValueError):
            entry.validate_results(result(), None)

    def test_acc_units_and_subset_majority_baseline(self):
        item = result()
        item["samples"]["boolq"][1]["doc"]["label"] = True
        summary, rows = entry.validate_results(item, 2)
        self.assertEqual(len(rows), 2)
        self.assertEqual(summary["acc"], .5)
        self.assertEqual(summary["acc_percent"], 50)
        self.assertEqual(summary["acc_correct"], 1)
        self.assertTrue(summary["limited_run"])
        self.assertEqual(summary["label_counts"], {"no": 0, "yes": 2})
        self.assertEqual(summary["majority_baseline_percent"], 100)
        self.assertEqual(summary["majority_baseline_scope"], "evaluated_subset")
        with patch.object(entry, "EXPECTED_EXAMPLES", 2):
            summary, _ = entry.validate_results(result(total=2), None)
        self.assertEqual(summary["majority_baseline_scope"], "full_validation")
        self.assertFalse(summary["limited_run"])

    def test_labels_and_documents_are_validated(self):
        for label in (-1, 2, "1", None, 1.0):
            with self.subTest(label=label), self.assertRaises(ValueError):
                entry.document_label(document(label))
        for key in ("question", "passage"):
            item = document(1); item[key] = " "
            with self.assertRaises(ValueError):
                entry.document_label(item)
        self.assertEqual(entry.document_label(document(False)), 0)
        with self.assertRaises(ValueError):
            entry.majority_baseline([], scope="test")

    def test_prepare_data_uses_labeled_validation_not_test(self):
        datasets = ModuleType("datasets")
        fixture = {"validation": [document(1), document(0)], "test": [document(-1)]}
        datasets.load_dataset = Mock(return_value=fixture)
        with patch.dict("sys.modules", {"datasets": datasets}), patch.object(entry, "EXPECTED_EXAMPLES", 2), redirect_stdout(io.StringIO()):
            self.assertEqual(entry.main(["--prepare-data"]), 0)
            datasets.load_dataset.assert_called_once_with("super_glue", "boolq")
            fixture["validation"][0]["label"] = -1
            with self.assertRaisesRegex(ValueError, "validation"):
                entry.main(["--prepare-data"])

    def test_missing_weight_shard_or_tokenizer_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            model = Path(tmp)
            (model / "config.json").write_text("{}", encoding="utf-8")
            (model / "tokenizer.json").write_text("{}", encoding="utf-8")
            (model / "model.safetensors.index.json").write_text(json.dumps({"weight_map": {"a": "missing.safetensors"}}), encoding="utf-8")
            with self.assertRaises(FileNotFoundError):
                entry.check_model_files(model, model)

    def test_preloaded_model_invocation_and_unique_reports(self):
        modules, evaluator, loaded_model, loader, backend = fake_backend()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            model = root / "checkpoints" / "experiment" / "actor" / "huggingface"
            model.mkdir(parents=True)
            for name in ("config.json", "tokenizer.json", "model.safetensors"):
                (model / name).write_text("{}", encoding="utf-8")
            with patch.dict("sys.modules", modules), patch.dict("os.environ", {"WORLD_SIZE": "1"}), \
                    patch.multiple(entry, ROOT=root, RESULTS_DIR=root / "results", MODEL_PATH="checkpoints/experiment/actor/huggingface", TOKENIZER_PATH=None, DEVICE="cpu"), \
                    patch.object(entry, "package_versions", return_value={"lm_eval": entry.EXPECTED_HARNESS_VERSION}), redirect_stdout(io.StringIO()):
                self.assertEqual(entry.main(["--check-only"]), 0)
                loader.assert_not_called(); evaluator.assert_not_called(); backend.assert_not_called()
                for _ in range(2):
                    self.assertEqual(entry.main(["--limit", "2"]), 0)
            settings = evaluator.call_args.kwargs
            self.assertEqual(settings["tasks"], ["boolq"])
            self.assertEqual(settings["num_fewshot"], 0)
            self.assertFalse(settings["apply_chat_template"])
            self.assertTrue(settings["log_samples"])
            self.assertEqual(settings["random_seed"], entry.SEED)
            self.assertEqual(loader.call_count, 2)
            self.assertEqual(loader.call_args.kwargs["torch_dtype"], entry.DTYPE)
            self.assertNotIn("dtype", loader.call_args.kwargs)
            self.assertTrue(loader.call_args.kwargs["local_files_only"])
            self.assertIs(backend.call_args.kwargs["pretrained"], loaded_model)
            self.assertNotIn("dtype", backend.call_args.kwargs)
            loaded_model.to.assert_called_with("cpu")
            summaries = list((root / "results").glob("*/*/summary.json"))
            self.assertEqual(len(summaries), 2)
            for path in summaries:
                summary = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(summary["acc_percent"], 50)
                self.assertEqual(summary["majority_baseline_scope"], "evaluated_subset")
                self.assertFalse(summary["watermark_at_inference"])
                self.assertEqual(summary["split"], "validation")
                self.assertIn("LIMITED RUN", path.with_name("report.md").read_text(encoding="utf-8"))
                self.assertEqual(len(path.with_name("samples.jsonl").read_text(encoding="utf-8").splitlines()), 2)
                aggregate = json.loads(path.with_name("harness_results.json").read_text(encoding="utf-8"))
                self.assertNotIn("samples", aggregate)

    def test_cli_rejects_invalid_limit_and_mixed_modes(self):
        for argv in (["--limit", "0"], ["--limit", "-1"], ["--prepare-data", "--check-only"]):
            with self.subTest(argv=argv), redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                entry.main(argv)
            self.assertEqual(error.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
