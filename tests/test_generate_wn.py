"""CPU integration tests for WN sampling, local preflight and atomic output."""

from contextlib import redirect_stderr, redirect_stdout
import io
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from wm_test.generate_wn_score import (
    WNProgress, main, parse_args, prepare_rows, read_rows, run_model, selected_gpus,
    validate_args, validate_model_assets,
)
from baseline_acl.inverse_watermark import RuleTable
from tests.test_inverse_watermark import FakeTokenizer, rules_document


class FakeEngine:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.calls = []
        self.biased_logits = []
        self.progress_flags = []

    def generate(self, prompts, parameters, use_tqdm):
        self.calls.append((prompts, parameters))
        self.progress_flags.append(use_tqdm)
        answers = []
        for prompt, params in zip(prompts, parameters, strict=True):
            logits = [10.0] * 4
            params.logits_processors[0](prompt["prompt_token_ids"], [], logits)
            self.biased_logits.append(logits)
            answers.append(SimpleNamespace(prompt_token_ids=prompt["prompt_token_ids"],
                                           outputs=[SimpleNamespace(text="a", finish_reason="stop")]))
        return answers


class WNTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix=".wn_test_", dir=Path(__file__).resolve().parents[1])
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.model = self.directory / "model"
        self.model.mkdir()
        (self.model / "config.json").write_text('{"model_type":"qwen2"}', encoding="utf-8")
        (self.model / "model.safetensors").write_bytes(b"test-placeholder")
        self.input = self.directory / "input.jsonl"
        self.rows = [{"id": "one", "content": [{"role": "user", "content": "a b"}]},
                     {"id": "two", "content": [{"role": "user", "content": "a b"}]}]
        self.input.write_text("".join(json.dumps(row) + "\n" for row in self.rows), encoding="utf-8")
        self.tokenizer = FakeTokenizer(str(self.model))
        self.rules_path = self.directory / "rules.json"
        self.rules_path.write_text(json.dumps(rules_document(self.tokenizer)), encoding="utf-8")
        self.rules = RuleTable.load(self.rules_path)
        self.output = self.directory / "output.jsonl"
        self.argv = ["--input", str(self.input), "--student-model", str(self.model),
                     "--rules", str(self.rules_path), "--output", str(self.output)]
        self.args = parse_args(self.argv)
        self.prepared = prepare_rows(self.rows, self.tokenizer, self.args.max_prompt_tokens)
        self.score = Mock(return_value={"z_score": 0.0, "num_tokens": 1, "green_tokens": 0,
                                       "green_fraction": 0.0, "dedup_z_score": 0.0,
                                       "dedup_num_tokens": 1, "dedup_green_tokens": 0,
                                       "dedup_green_fraction": 0.0, "p_value": 0.5, "dedup_p_value": 0.5})

    def run_fake(self, engine_factory=FakeEngine, detector_tokenizer=None, progress_stream=None):
        self.stdout = io.StringIO()
        self.stderr = io.StringIO() if progress_stream is None else progress_stream
        with redirect_stdout(self.stdout), redirect_stderr(self.stderr):
            run_model(args=self.args, prepared=self.prepared, tokenizer=self.tokenizer,
                      rules=self.rules, rules_sha256="rule-hash", input_sha256="input-hash",
                      engine_factory=engine_factory, sampling_factory=SimpleNamespace,
                      score_function=self.score, score_config_factory=SimpleNamespace,
                      detector_tokenizer=self.tokenizer if detector_tokenizer is None else detector_tokenizer)

    def test_sampling_hook_biases_student_and_emits_evaluator_compatible_records(self):
        engines = []

        def factory(**kwargs):
            engine = FakeEngine(**kwargs)
            engines.append(engine)
            return engine

        self.run_fake(factory)
        engine = engines[0]
        self.assertAlmostEqual(engine.biased_logits[0][3], 10 - 2.5 * 2.4)
        self.assertEqual(engine.kwargs["trust_remote_code"], False)
        self.assertEqual(engine.calls[0][0], [{"prompt_token_ids": [1, 2]}, {"prompt_token_ids": [1, 2]}])
        self.assertEqual([param.seed for param in engine.calls[0][1]], [42, 43])
        records = [json.loads(line) for line in self.output.read_text(encoding="utf-8").splitlines()]
        self.assertEqual([row["id"] for row in records], ["one", "two"])
        self.assertEqual(records[0]["prompt"], self.rows[0]["content"])
        self.assertEqual(records[0]["label"], "kgw")
        self.assertTrue(records[0]["is_watermarked"])
        self.assertEqual(records[0]["attack"]["rules_sha256"], "rule-hash")
        self.assertEqual(records[0]["attack"]["strength"], 2.5)
        self.assertFalse(records[0]["generation"]["kgw_enabled_during_generation"])
        self.assertFalse(records[0]["generation"]["prompt_truncated"])
        self.assertTrue(records[0]["generation"]["wn_enabled_during_generation"])
        self.assertEqual(self.score.call_count, 2)
        self.assertTrue(self.score.call_args.kwargs["include_deduplicated"])
        self.assertEqual(self.score.call_args.kwargs["device"], "cuda")
        from wm_test.evaluate_compare_metrics import load_scores

        self.assertEqual(load_scores(self.output, "kgw", True), {"one": 0.0, "two": 0.0})

    def test_detection_uses_teacher_while_generation_and_rules_use_student(self):
        teacher = FakeTokenizer("teacher")
        teacher.vocab = {"<eos>": 0, "a": 4, "b": 3, "c": 1, "d": 2}
        teacher.apply_chat_template = Mock(side_effect=AssertionError("use actual rendered prompt"))
        engine = FakeEngine()
        self.run_fake(lambda **kwargs: engine, detector_tokenizer=teacher)
        self.assertEqual(engine.calls[0][0], [{"prompt_token_ids": [1, 2]}, {"prompt_token_ids": [1, 2]}])
        self.assertAlmostEqual(engine.biased_logits[0][3], 10 - 2.5 * 2.4)
        for call in self.score.call_args_list:
            self.assertEqual(call.kwargs["prompt_token_ids"], [4, 3])
            self.assertEqual(call.kwargs["generated_token_ids"], [4])
            self.assertEqual(call.kwargs["vocab_size"], 5)
        teacher.apply_chat_template.assert_not_called()

    def test_strength_zero_preserves_logits_and_records_control(self):
        self.args.strength = 0
        engine = FakeEngine()
        self.run_fake(lambda **kwargs: engine)
        self.assertEqual(engine.biased_logits[0], [10.0] * 4)
        row = json.loads(self.output.read_text(encoding="utf-8").splitlines()[0])
        self.assertFalse(row["generation"]["wn_enabled_during_generation"])

    def test_failure_does_not_publish_partial_or_replace_previous_file(self):
        self.output.write_text("previous-output", encoding="utf-8")
        self.args.overwrite = True
        self.score.side_effect = [self.score.return_value, RuntimeError("simulated scoring failure")]
        with self.assertRaisesRegex(RuntimeError, "scoring failure"):
            self.run_fake()
        self.assertEqual(self.output.read_text(encoding="utf-8"), "previous-output")
        self.assertEqual(list(self.directory.glob("output.jsonl.*.tmp")), [])

    def test_progress_counts_final_partial_batch_and_keeps_logs_readable(self):
        self.args.batch_size = 2
        self.prepared.append({**self.prepared[0], "row": {**self.rows[0], "id": "three"}})
        engine = FakeEngine()
        self.run_fake(lambda **kwargs: engine)
        log = self.stderr.getvalue()
        self.assertIn("[WN generate 1/2]", log)
        self.assertIn("[WN score 2/2]", log)
        self.assertIn("1/3", log)
        self.assertIn("3/3", log)
        self.assertIn("[WN saving]", log)
        self.assertIn("[WN done]", log)
        self.assertNotIn("\r", log)
        self.assertEqual(engine.progress_flags, [False, False])
        self.assertEqual([[param.seed for param in call[1]] for call in engine.calls], [[42, 43], [44]])
        self.assertEqual(len(self.output.read_text(encoding="utf-8").splitlines()), 3)

    def test_scoring_failure_keeps_actual_count_and_never_reports_done(self):
        self.score.side_effect = [self.score.return_value, RuntimeError("scoring stopped")]
        with self.assertRaisesRegex(RuntimeError, "scoring stopped"):
            self.run_fake()
        log = self.stderr.getvalue()
        self.assertIn("[WN failed]", log)
        self.assertIn("1/2", log.splitlines()[-1])
        self.assertNotIn("[WN done]", log)
        self.assertNotIn("Saved", self.stdout.getvalue())
        self.assertFalse(self.output.exists())

    def test_publication_failure_is_not_reported_as_success(self):
        self.output.write_text("previous-output", encoding="utf-8")
        self.args.overwrite = True
        with patch("wm_test.generate_wn_score.os.replace", side_effect=OSError("publish failed")), \
                self.assertRaisesRegex(OSError, "publish failed"):
            self.run_fake()
        log = self.stderr.getvalue()
        self.assertIn("[WN failed]", log)
        self.assertIn("2/2", log.splitlines()[-1])
        self.assertNotIn("[WN done]", log)
        self.assertNotIn("Saved", self.stdout.getvalue())
        self.assertEqual(self.output.read_text(encoding="utf-8"), "previous-output")
        self.assertEqual(list(self.directory.glob("output.jsonl.*.tmp")), [])

    def test_terminal_enables_live_vllm_batch_progress_and_finishes_line(self):
        class Terminal(io.StringIO):
            def isatty(self):
                return True

        engine = FakeEngine()
        self.run_fake(lambda **kwargs: engine, progress_stream=Terminal())
        log = self.stderr.getvalue()
        self.assertEqual(engine.progress_flags, [True])
        self.assertIn("\r[WN", log)
        self.assertIn("[WN done]", log)
        self.assertTrue(log.endswith("\n"))

    def test_keyboard_interrupt_ends_progress_without_publishing(self):
        self.score.side_effect = KeyboardInterrupt
        with self.assertRaises(KeyboardInterrupt):
            self.run_fake()
        self.assertIn("[WN failed]", self.stderr.getvalue())
        self.assertTrue(self.stderr.getvalue().endswith("\n"))
        self.assertNotIn("[WN done]", self.stderr.getvalue())
        self.assertFalse(self.output.exists())
        self.assertEqual(list(self.directory.glob("output.jsonl.*.tmp")), [])

    def test_default_refuses_existing_output(self):
        self.output.write_text("previous-output", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            validate_args(self.args)
        with self.assertRaises(FileExistsError):
            self.run_fake()

    def test_missing_or_extra_backend_results_never_publish(self):
        class Incomplete(FakeEngine):
            def generate(self, prompts, parameters, use_tqdm):
                return super().generate(prompts, parameters, use_tqdm)[:1]

        with self.assertRaises(ValueError):
            self.run_fake(Incomplete)
        self.assertFalse(self.output.exists())
        self.assertEqual(list(self.directory.glob("output.jsonl.*.tmp")), [])

    def test_backend_prompt_retokenization_is_rejected(self):
        class Retokenized(FakeEngine):
            def generate(self, prompts, parameters, use_tqdm):
                results = super().generate(prompts, parameters, use_tqdm)
                results[0].prompt_token_ids = [0] + results[0].prompt_token_ids
                return results

        with self.assertRaisesRegex(ValueError, "prompt IDs differ"):
            self.run_fake(Retokenized)
        self.assertFalse(self.output.exists())

    def test_preflight_neither_loads_model_nor_writes_output_nor_requires_gpu(self):
        loader = Mock(return_value=self.tokenizer)
        fake_transformers = SimpleNamespace(AutoTokenizer=SimpleNamespace(from_pretrained=loader))
        with patch.dict("sys.modules", {"transformers": fake_transformers}), \
                patch("wm_test.generate_wn_score.run_model") as runner, \
                patch.dict(os.environ, {"CUDA_VISIBLE_DEVICES": ""}), \
                redirect_stdout(io.StringIO()) as output, redirect_stderr(io.StringIO()) as progress:
            main(self.argv + ["--preflight", "--limit", "1"])
        self.assertFalse(self.output.exists())
        runner.assert_not_called()
        self.assertTrue(loader.call_args.kwargs["local_files_only"])
        self.assertFalse(loader.call_args.kwargs["trust_remote_code"])
        self.assertEqual(json.loads(output.getvalue())["rows"], 1)
        self.assertEqual(progress.getvalue(), "")

    def test_full_prompt_budget_failure_occurs_before_engine_load(self):
        with self.assertRaisesRegex(ValueError, "full prompt has 2 tokens"):
            prepare_rows(self.rows, self.tokenizer, 1)
        self.assertEqual(self.rows[0]["content"][0]["content"], "a b")

    def test_prompt_budget_failure_reports_maximum_over_all_rows(self):
        rows = [
            {"id": "first-long", "content": [{"role": "user", "content": "a b c"}]},
            {"id": "longest", "content": [{"role": "user", "content": "a b c a b"}]},
            {"id": "short", "content": [{"role": "user", "content": "a"}]},
        ]
        with self.assertRaises(ValueError) as failure:
            prepare_rows(rows, self.tokenizer, 2)
        message = str(failure.exception)
        self.assertIn("id 'longest': full prompt has 5 tokens", message)
        self.assertIn("scanned all 3 prompts, 2 exceed budget", message)
        self.assertIn("set --max-prompt-tokens to at least 5", message)
        prepared = prepare_rows(rows, self.tokenizer, 5)
        self.assertEqual([len(row["prompt_ids"]) for row in prepared], [3, 5, 1])
        self.assertEqual(prepared[1]["prompt"], "a b c a b")

    def test_input_schema_and_unique_ids_checked_before_limit(self):
        duplicate = [self.rows[0], self.rows[0]]
        self.input.write_text("".join(json.dumps(row) + "\n" for row in duplicate), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "duplicate id"):
            read_rows(self.input, limit=1)

    def test_output_cannot_overwrite_source_rules_or_model_files(self):
        for destination in (self.input, self.rules_path, self.model / "new.jsonl"):
            self.args.output = destination
            self.args.overwrite = True
            with self.subTest(destination=destination), self.assertRaises(ValueError):
                validate_args(self.args)

    def test_missing_local_weight_shard_is_detected(self):
        (self.model / "model.safetensors.index.json").write_text(
            json.dumps({"weight_map": {"layer": "missing.safetensors"}}), encoding="utf-8")
        with self.assertRaisesRegex(FileNotFoundError, "missing model shard"):
            validate_model_assets(self.model)

    def test_gpu_selection_is_explicit_and_does_not_choose_defaults(self):
        self.assertEqual(selected_gpus("2", 1), ["2"])
        self.assertEqual(selected_gpus("2,5", 2), ["2", "5"])
        for value, count in ((None, 1), ("", 1), ("2,2", 2), ("2", 2), ("-1", 1), ("1，2", 2)):
            with self.subTest(value=value, count=count), self.assertRaises(ValueError):
                selected_gpus(value, count)


class WNProgressTests(unittest.TestCase):
    def test_bar_reports_elapsed_speed_and_estimated_remaining_time(self):
        stream = io.StringIO()
        with patch("wm_test.generate_wn_score.time.monotonic", return_value=100) as clock:
            progress = WNProgress(4, stream=stream)
            self.assertIn("--:--:--", stream.getvalue())
            clock.return_value = 102
            progress.advance()
            line = stream.getvalue().splitlines()[-1]
            self.assertIn("25.0% 1/4", line)
            self.assertIn("00:00:02<~00:00:06, 0.50/s", line)
            with self.assertRaisesRegex(ValueError, "before all answers"):
                progress.finish(success=True)
            progress.finish(success=False)
        self.assertNotIn("[WN done]", stream.getvalue())


if __name__ == "__main__":
    unittest.main()
