"""Offline detector configuration and saved-answer rescoring regressions.

Run with ``python -m unittest tests.test_compare_detection -v``. All result files
are temporary fixtures; CUDA, model weights and network access are mocked.
"""

import argparse
from copy import deepcopy
import contextlib
import hashlib
import io
import json
import math
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import MagicMock, patch

from wm_test import evaluate_compare_metrics as evaluator
from wm_test import generate_compare_score as generator
from wm_test import rescore_compare_scores as rescoring


KEY = 15_485_863
SEEDING = "simple_1 (hash_key * previous_token_id)"
TARGET = {"gamma": 0.5, "delta": 3.0, "hash_key": KEY}
REPO_ROOT = Path(__file__).resolve().parents[1]


def scores(gamma, n=100, green=60, dedup_n=20, dedup_green=12):
    raw_z = (green - gamma * n) / math.sqrt(n * gamma * (1 - gamma)) if n else 0.0
    dedup_z = (dedup_green - gamma * dedup_n) / math.sqrt(dedup_n * gamma * (1 - gamma)) if dedup_n else None
    return {
        "num_tokens": n, "green_tokens": green, "green_fraction": green / n if n else 0.0,
        "z_score": raw_z, "p_value": evaluator.p_from_z(raw_z) if n else None,
        "dedup_num_tokens": dedup_n, "dedup_green_tokens": dedup_green,
        "dedup_green_fraction": dedup_green / dedup_n if dedup_n else 0.0,
        "dedup_z_score": dedup_z, "dedup_p_value": evaluator.p_from_z(dedup_z),
    }


def answer_row(sample_id="sample", label="kgw", gamma=0.25, delta=2.0, key=KEY, seeding=SEEDING):
    return {
        "id": sample_id, "label": label, "is_watermarked": label == "kgw",
        "model_path": "/offline/model", "prompt": [{"role": "user", "content": "Question"}],
        "answer": "Saved answer remains byte-for-byte the same: 测试。",
        "generation": {"max_prompt_tokens": 2048, "temperature": 0.7, "kgw_enabled_during_generation": False},
        "kgw": {"gamma": gamma, "delta": delta, "hash_key": key, "seeding": seeding},
        **scores(gamma),
    }


class FakeRescorer:
    def __init__(self):
        self.calls = []

    def score(self, row, config_override=None):
        if config_override is None:
            raise AssertionError("explicit rescoring must pass the target detector config")
        self.calls.append((deepcopy(row), dict(config_override)))
        # New green-list counts differ from the source as well as its gamma.
        return scores(config_override["gamma"], n=80, green=48, dedup_n=16, dedup_green=10)


class FileTestCase(unittest.TestCase):
    def setUp(self):
        # The Windows sandbox's virtual TEMP forbids atomic file replacement.
        # Keep fixtures in the explicit writable workspace and verify the target
        # before TemporaryDirectory registers its recursive cleanup.
        self.temporary = tempfile.TemporaryDirectory(prefix=".compare-detector-test-", dir=REPO_ROOT)
        if not Path(self.temporary.name).resolve().is_relative_to(REPO_ROOT):
            raise AssertionError("test cleanup directory is outside the workspace")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def write_rows(self, name, rows):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="\n") as handle:
            for row in rows:
                handle.write(json.dumps(row, ensure_ascii=False, allow_nan=True) + "\n")
        return path

    @staticmethod
    def read_rows(path):
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


class DetectorMetadataTests(FileTestCase):
    def test_consistent_metadata_is_loaded_without_cuda(self):
        source = self.write_rows("scores.jsonl", [answer_row("1"), answer_row("2")])
        self.assertEqual(evaluator.load_detection_config(source), {
            "gamma": 0.25, "delta": 2.0, "hash_key": KEY, "seeding": SEEDING,
        })

    def test_mixed_config_within_a_file_is_rejected(self):
        for change in ({"gamma": 0.5}, {"delta": 3.0}, {"key": KEY + 1}, {"seeding": "other-seeding"}):
            with self.subTest(change=change):
                source = self.write_rows("mixed.jsonl", [answer_row("1"), answer_row("2", **change)])
                with self.assertRaises(ValueError):
                    evaluator.load_detection_config(source)

    def test_invalid_metadata_parameters_are_rejected(self):
        for change in ({"gamma": 0.0}, {"gamma": 1.0}, {"gamma": float("nan")}, {"delta": 0.0}, {"delta": float("inf")}, {"hash_key": -1}, {"hash_key": True}, {"hash_key": 3.5}, {"hash_key": float("inf")}):
            with self.subTest(change=change):
                row = answer_row()
                row["kgw"].update(change)
                source = self.write_rows("invalid.jsonl", [row])
                with self.assertRaises(ValueError):
                    evaluator.load_detection_config(source)

    def test_missing_detector_metadata_is_rejected(self):
        row = answer_row()
        del row["kgw"]["gamma"]
        source = self.write_rows("missing.jsonl", [row])
        with self.assertRaises(ValueError):
            evaluator.load_detection_config(source)

    def test_filename_mismatch_is_rejected_and_explicit_name_check_can_be_disabled(self):
        source = self.write_rows("experiment_gamma0.5_delta3.jsonl", [answer_row()])
        with self.assertRaises(ValueError):
            evaluator.load_detection_config(source)
        self.assertEqual(evaluator.load_detection_config(source, check_names=False)["gamma"], 0.25)

    def test_model_path_mismatch_is_rejected(self):
        row = answer_row()
        row["model_path"] = "/checkpoints/experiment_gamma0.5_delta3/actor/huggingface"
        source = self.write_rows("scores.jsonl", [row])
        with self.assertRaises(ValueError):
            evaluator.load_detection_config(source)

    def test_matching_names_are_accepted(self):
        row = answer_row(gamma=0.5, delta=3.0)
        row["model_path"] = "/checkpoints/experiment_gamma0.5_delta3/actor/huggingface"
        source = self.write_rows("experiment_gamma0.5_delta3.jsonl", [row])
        self.assertEqual(evaluator.load_detection_config(source)["gamma"], 0.5)

    def test_metadata_change_without_rescoring_is_rejected(self):
        row = answer_row()
        row["kgw"].update(TARGET)
        source = self.write_rows("scores.jsonl", [row])
        with self.assertRaises(ValueError):
            evaluator.load_detection_config(source)

    def test_correct_student_and_clean_pair_is_accepted(self):
        positive = self.write_rows("student.jsonl", [answer_row(label="kgw", gamma=0.5, delta=3.0)])
        negative = self.write_rows("clean.jsonl", [answer_row(label="clean", gamma=0.5, delta=3.0)])
        self.assertEqual(evaluator.validate_detector_pair(positive, negative), {
            "gamma": 0.5, "hash_key": KEY, "seeding": SEEDING,
            "delta_by_label": {"kgw": 3.0, "clean": 3.0},
        })

    def test_delta_differences_do_not_change_the_detector_pair(self):
        positive = self.write_rows("student.jsonl", [answer_row(label="kgw", gamma=0.5, delta=3.0)])
        negative = self.write_rows("clean.jsonl", [answer_row(label="clean", gamma=0.5, delta=2.0)])
        result = evaluator.validate_detector_pair(positive, negative)
        self.assertEqual(result["delta_by_label"], {"kgw": 3.0, "clean": 2.0})

    def test_gamma_hash_and_seeding_differences_between_files_are_rejected(self):
        positive = self.write_rows("student.jsonl", [answer_row(label="kgw")])
        for change in ({"gamma": 0.5}, {"key": KEY + 1}, {"seeding": "other-seeding"}):
            with self.subTest(change=change):
                negative = self.write_rows("clean.jsonl", [answer_row(label="clean", **change)])
                with self.assertRaises(ValueError):
                    evaluator.validate_detector_pair(positive, negative)

    def test_main_rejects_mismatched_config_before_evaluating_metrics(self):
        positive = self.write_rows("student.jsonl", [answer_row(label="kgw")])
        negative = self.write_rows("clean.jsonl", [answer_row(label="clean", gamma=0.5)])
        args = argparse.Namespace(kgw_file=positive, clean_file=negative)
        with patch.object(evaluator, "parse_args", return_value=args), patch.object(evaluator, "evaluate") as calculate:
            with self.assertRaises(ValueError):
                evaluator.main()
        calculate.assert_not_called()

    def test_main_report_displays_actual_detector_config(self):
        positive = self.write_rows("student.jsonl", [answer_row(label="kgw", gamma=0.5, delta=3.0)])
        negative = self.write_rows("clean.jsonl", [answer_row(label="clean", gamma=0.5, delta=3.0)])
        report = self.root / "report.md"
        report.write_text("Existing history must remain intact.\n", encoding="utf-8")
        args = argparse.Namespace(
            kgw_file=positive, clean_file=negative, output=report,
            dolly_reference_file=self.root / "dolly.jsonl",
            teacher_clean_reference_file=self.root / "teacher.jsonl",
            tokenizer=None, score_device="cuda",
        )
        rouge = {"mean": 0.7, "num_samples": 1, "reference_file": "offline-reference"}
        from wm_test.grouped_pvalues import group_token_flags
        grouped_payload = {"num_answers": 1, "total_answer_tokens": 100,
                           "budgets": group_token_flags([0, 1] * 50, 0.5)}
        with patch.object(evaluator, "parse_args", return_value=args), patch.object(evaluator, "evaluate_dolly_rouge", return_value=rouge), patch.object(evaluator, "evaluate_teacher_clean_rouge", return_value=rouge), patch.object(evaluator, "load_grouped_pvalues", return_value=(grouped_payload, self.root / "grouped.json")), contextlib.redirect_stdout(io.StringIO()) as stdout:
            evaluator.main()
            evaluator.main()
        text = report.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("Existing history must remain intact.\n"))
        self.assertEqual(text.count("## 评估记录"), 2)
        self.assertEqual(text.count("固定 token 分组 p-value（普通中位数"), 2)
        self.assertEqual(text.count('"auroc": 0.5'), 2)
        self.assertEqual(text.count("两种逐条文本 p-value"), 2)
        self.assertIn('"detector_config"', text)
        self.assertIn('"gamma": 0.5', text)
        self.assertIn('"delta_by_label"', text)
        self.assertIn("Detector config:", stdout.getvalue())
        self.assertIn("普通中位数", stdout.getvalue())
        self.assertNotIn("上中位数", text)
        self.assertIn('"aggregation": "ordinary_median"', text)
        self.assertIn('"grouped_p_values"', text)
        for budget in (1000, 2000, 3000, 10000, 20000, 30000):
            self.assertIn(f"| {budget} | {budget - 1} |", text)
        self.assertIn("N/A", text)


class SavedAnswerRescoringTests(FileTestCase):
    def setUp(self):
        super().setUp()
        self.args = argparse.Namespace(score_device="cuda", tokenizer=None, overwrite=False)

    def rescore(self, source, scorer=None, output=None):
        output = output or rescoring.output_path_for(source, TARGET)
        scorer = scorer or FakeRescorer()
        with contextlib.redirect_stdout(io.StringIO()):
            result = rescoring.rescore_file(source, output, TARGET, self.args, rescorer=scorer)
        return result, scorer

    def test_rescoring_replaces_raw_and_dedup_scores_and_preserves_answers_and_source(self):
        original = answer_row()
        source = self.write_rows("student.jsonl", [original])
        before = source.read_bytes()
        output, scorer = self.rescore(source)
        self.assertEqual(source.read_bytes(), before)
        self.assertEqual(output.name, "student.rescored_gamma0.5_delta3_key15485863.jsonl")
        row = self.read_rows(output)[0]
        for field in ("id", "label", "is_watermarked", "prompt", "answer", "model_path", "generation"):
            self.assertEqual(row[field], original[field])
        self.assertEqual(len(scorer.calls), 1)
        self.assertEqual(scorer.calls[0][1], TARGET)
        self.assertNotEqual(row["z_score"], original["z_score"])
        self.assertNotEqual(row["dedup_z_score"], original["dedup_z_score"])
        self.assertEqual(row["green_tokens"], 48)
        self.assertEqual(row["dedup_green_tokens"], 10)
        self.assertEqual(row["kgw"]["gamma"], 0.5)
        self.assertEqual(row["rescoring"]["original_kgw"], original["kgw"])
        self.assertEqual(row["rescoring"]["source_sha256"], hashlib.sha256(before).hexdigest())
        self.assertEqual(evaluator.load_detection_config(output)["gamma"], 0.5)

    def test_rescoring_does_not_read_existing_source_score_cache(self):
        source = self.write_rows("student.jsonl", [answer_row()])
        source_cache = source.with_suffix(".p_values.jsonl")
        source_cache.write_text("deliberately invalid old detector cache", encoding="utf-8")
        before = source_cache.read_bytes()
        output, scorer = self.rescore(source)
        self.assertEqual(len(scorer.calls), 1)
        self.assertEqual(source_cache.read_bytes(), before)
        self.assertEqual(self.read_rows(output)[0]["num_tokens"], 80)

    def test_rescored_pair_accepts_original_model_names_under_new_detector(self):
        outputs = []
        for label in ("kgw", "clean"):
            row = answer_row(label=label)
            row["model_path"] = "/checkpoints/original_gamma0.25_delta2/actor/huggingface"
            source = self.write_rows(f"{label}_gamma0.25_delta2.jsonl", [row])
            output, _ = self.rescore(source)
            outputs.append(output)
        self.assertEqual(evaluator.validate_detector_pair(*outputs)["gamma"], 0.5)

    def test_rescoring_cannot_overwrite_the_original_even_when_overwrite_is_enabled(self):
        source = self.write_rows("student.jsonl", [answer_row()])
        before = source.read_bytes()
        scorer = FakeRescorer()
        self.args.overwrite = True
        with self.assertRaises(ValueError):
            rescoring.rescore_file(source, source, TARGET, self.args, rescorer=scorer)
        self.assertEqual(source.read_bytes(), before)
        self.assertEqual(scorer.calls, [])

    def test_existing_output_requires_overwrite(self):
        source = self.write_rows("student.jsonl", [answer_row()])
        output = rescoring.output_path_for(source, TARGET)
        output.write_text("existing output", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            self.rescore(source, output=output)
        self.assertEqual(output.read_text(encoding="utf-8"), "existing output")

    def test_incomplete_scoring_fails_without_partial_output(self):
        source = self.write_rows("student.jsonl", [answer_row()])
        output = rescoring.output_path_for(source, TARGET)
        scorer = types.SimpleNamespace(score=lambda row, config_override: {"z_score": 0.0})
        with self.assertRaises(ValueError):
            self.rescore(source, output=output, scorer=scorer)
        self.assertFalse(output.exists())
        self.assertEqual(list(self.root.glob("*.tmp")), [])

    def test_pvalue_cache_and_detection_metrics_use_new_scores(self):
        source = self.write_rows("student.jsonl", [answer_row()])
        output, _ = self.rescore(source)
        row = self.read_rows(output)[0]
        no_rescore = types.SimpleNamespace(score=MagicMock(side_effect=AssertionError("dedup scores were already recomputed")))
        stale = output.with_suffix(".p_values.jsonl")
        stale.write_text(json.dumps({
            "id": row["id"], "schema": evaluator.P_VALUE_SCHEMA,
            "source_sha256": "old-source", "z_score_raw": 999.0,
        }) + "\n", encoding="utf-8")
        records, cache = evaluator.load_pvalue_records(output, no_rescore)
        self.assertEqual(records[0]["z_score_raw"], row["z_score"])
        self.assertEqual(records[0]["z_score_dedup"], row["dedup_z_score"])
        self.assertAlmostEqual(records[0]["p_value_raw"], evaluator.p_from_z(row["z_score"]))
        self.assertEqual(records[0]["source_sha256"], hashlib.sha256(output.read_bytes()).hexdigest())
        self.assertEqual(self.read_rows(cache), records)
        self.assertEqual(evaluator.load_scores(output, "kgw", True), {row["id"]: row["z_score"]})
        second, _ = evaluator.load_pvalue_records(output, no_rescore)
        self.assertEqual(second, records)
        no_rescore.score.assert_not_called()

    def test_planning_rejects_duplicate_output_names_before_any_write(self):
        left = self.write_rows("a/student.jsonl", [answer_row()])
        right = self.write_rows("b/student.jsonl", [answer_row()])
        output_dir = self.root / "combined"
        with self.assertRaises(ValueError):
            rescoring.plan_outputs([left, right], TARGET, output_dir=output_dir)
        self.assertFalse(output_dir.exists())


class DetectorBackendAndCliTests(FileTestCase):
    @staticmethod
    def fake_backend(score_function):
        tokenizer = types.SimpleNamespace(
            encode=lambda text, **kwargs: [1, 2, 3],
            decode=lambda tokens, **kwargs: "decoded prompt",
            apply_chat_template=lambda prompt, **kwargs: "rendered question",
        )
        # __len__ is a special method, so it belongs on the type.
        class Tokenizer:
            def __len__(self):
                return 100

        instance = Tokenizer()
        instance.__dict__.update(tokenizer.__dict__)
        torch = types.ModuleType("torch")
        torch.cuda = types.SimpleNamespace(is_available=lambda: True, empty_cache=lambda: None)
        transformers = types.ModuleType("transformers")
        transformers.AutoTokenizer = types.SimpleNamespace(from_pretrained=MagicMock(return_value=instance))
        package = types.ModuleType("wm_data")
        package.__path__ = []
        kgw = types.ModuleType("wm_data.kgw")
        kgw.KGWConfig = lambda **kwargs: types.SimpleNamespace(**kwargs)
        kgw.kgw_score = score_function
        return {"torch": torch, "transformers": transformers, "wm_data": package, "wm_data.kgw": kgw}, instance

    def test_legacy_override_passes_new_config_to_backend_and_skips_old_z_check(self):
        seen = []

        def score_function(**kwargs):
            seen.append(kwargs)
            return scores(kwargs["config"].gamma)

        modules, _ = self.fake_backend(score_function)
        row = answer_row()
        rescorer = evaluator.LegacyRescorer(argparse.Namespace(tokenizer=None, score_device="cuda"))
        with patch.dict("sys.modules", modules):
            original = rescorer.score(row)
            revised = rescorer.score(row, config_override=TARGET)
        self.assertEqual(original["z_score"], row["z_score"])
        self.assertNotEqual(revised["z_score"], row["z_score"])
        self.assertEqual([call["config"].gamma for call in seen], [0.25, 0.5])
        self.assertEqual(seen[-1]["config"].delta, 3.0)
        self.assertEqual(seen[-1]["config"].hash_key, KEY)
        self.assertTrue(seen[-1]["include_deduplicated"])
        self.assertEqual(seen[-1]["device"], "cuda")
        self.assertEqual([call.args[0] for call in modules["transformers"].AutoTokenizer.from_pretrained.call_args_list],
                         [str(evaluator.DEFAULT_DETECTOR_TOKENIZER), "/offline/model"])

    def test_legacy_without_override_still_rejects_nonreproduced_old_scores(self):
        modules, _ = self.fake_backend(lambda **kwargs: scores(0.5))
        rescorer = evaluator.LegacyRescorer(argparse.Namespace(tokenizer=None, score_device="cuda"))
        with patch.dict("sys.modules", modules), self.assertRaises(ValueError):
            rescorer.score(answer_row())

    def test_legacy_uses_native_prompt_format_and_teacher_token_ids(self):
        calls = []
        modules, teacher = self.fake_backend(lambda **kwargs: calls.append(kwargs) or scores(0.5))
        native = type(teacher)()
        native.apply_chat_template = MagicMock(return_value="native student prompt")
        native.encode = MagicMock(return_value=[4, 5, 6])
        native.decode = MagicMock(return_value="truncated native student prompt")
        teacher.encode = MagicMock(side_effect=lambda text, **kwargs:
                                   [71, 72, 73] if text == "truncated native student prompt" else [81, 82])
        teacher.apply_chat_template = MagicMock(side_effect=AssertionError("teacher must not render the student prompt"))
        loader = modules["transformers"].AutoTokenizer.from_pretrained
        loader.side_effect = lambda path, **kwargs: teacher if path == str(evaluator.DEFAULT_DETECTOR_TOKENIZER) else native
        row = answer_row()
        row["generation"]["max_prompt_tokens"] = 2
        rescorer = evaluator.LegacyRescorer(argparse.Namespace(tokenizer=None, score_device="cuda"))
        with patch.dict("sys.modules", modules):
            result = rescorer.score(row, config_override=TARGET)
        native.apply_chat_template.assert_called_once_with(row["prompt"], add_generation_prompt=True, tokenize=False)
        native.decode.assert_called_once_with([4, 5], skip_special_tokens=False)
        self.assertEqual(calls[0]["prompt_token_ids"], [71, 72, 73])
        self.assertEqual(calls[0]["generated_token_ids"], [81, 82])
        self.assertEqual(calls[0]["vocab_size"], len(teacher))
        self.assertEqual(set(result), set(scores(0.5)))

    def test_generation_and_rescore_cli_require_explicit_gamma_and_delta(self):
        for parser, prefix in ((generator.parse_args, []), (rescoring.parse_args, ["--inputs", "saved.jsonl"])):
            for suffix in ([], ["--gamma", "0.5"], ["--delta", "3"]):
                with self.subTest(parser=parser.__module__, suffix=suffix), contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit):
                        parser(prefix + suffix)
            args = parser(prefix + ["--gamma", "0.5", "--delta", "3"])
            self.assertEqual((args.gamma, args.delta), (0.5, 3.0))

    def test_detector_arguments_do_not_change_generation_sampling(self):
        sampling_calls, detector_calls = [], []

        def score_function(**kwargs):
            detector_calls.append(kwargs)
            return scores(kwargs["config"].gamma)

        modules, tokenizer = self.fake_backend(score_function)
        class TeacherTokenizer(type(tokenizer)):
            def __len__(self):
                return 200

        teacher = TeacherTokenizer()
        teacher.encode = MagicMock(side_effect=lambda text, **kwargs:
                                   [71, 72] if text == "rendered question" else [81, 82, 83])
        teacher.apply_chat_template = MagicMock(side_effect=AssertionError("teacher must not render the student prompt"))
        modules["transformers"].AutoTokenizer.from_pretrained.return_value = teacher
        vllm = types.ModuleType("vllm")

        class Engine:
            def __init__(self, **kwargs):
                pass

            def generate(self, prompts, sampling, **kwargs):
                return [types.SimpleNamespace(outputs=[types.SimpleNamespace(text="saved mocked generation")]) for _ in prompts]

        def sampling_params(**kwargs):
            sampling_calls.append(kwargs)
            return types.SimpleNamespace(**kwargs)

        vllm.LLM = Engine
        vllm.SamplingParams = sampling_params
        modules["vllm"] = vllm
        model = self.root / "model"
        model.mkdir()
        rows = [{"id": "sample", "content": [{"role": "user", "content": "Question"}]}]
        with patch.dict("sys.modules", modules), contextlib.redirect_stdout(io.StringIO()):
            for index, (gamma, delta) in enumerate(((0.25, 2.0), (0.5, 3.0))):
                args = generator.parse_args(["--gamma", str(gamma), "--delta", str(delta)])
                generator.run_model(model_path=model, label="kgw_trained_student", output_path=self.root / f"generated-{index}.jsonl", rows=rows, tokenizer=tokenizer, args=args)
        self.assertEqual(sampling_calls[0], sampling_calls[1])
        self.assertEqual([(call["config"].gamma, call["config"].delta) for call in detector_calls], [(0.25, 2.0), (0.5, 3.0)])
        for call in detector_calls:
            self.assertEqual(call["prompt_token_ids"], [71, 72])
            self.assertEqual(call["generated_token_ids"], [81, 82, 83])
            self.assertEqual(call["vocab_size"], len(teacher))
        for call in modules["transformers"].AutoTokenizer.from_pretrained.call_args_list:
            self.assertEqual(call.args[0], str(generator.DEFAULT_DETECTOR_TOKENIZER))
        for index in (0, 1):
            row = self.read_rows(self.root / f"generated-{index}.jsonl")[0]
            self.assertFalse(row["generation"]["kgw_enabled_during_generation"])
            self.assertNotIn("detector_tokenizer", row)
            self.assertNotIn("rendered_prompt", row)


if __name__ == "__main__":
    unittest.main()
