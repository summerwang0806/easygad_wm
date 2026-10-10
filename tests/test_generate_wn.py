"""CPU integration tests for WN sampling, local preflight and atomic output."""

from contextlib import redirect_stdout
import io
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from wm_test.generate_wn_score import (
    main, parse_args, prepare_rows, read_rows, run_model, selected_gpus,
    validate_args, validate_model_assets,
)
from baseline_acl.inverse_watermark import RuleTable
from tests.test_inverse_watermark import FakeTokenizer, rules_document


class FakeEngine:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.calls = []
        self.biased_logits = []

    def generate(self, prompts, parameters, use_tqdm):
        self.calls.append((prompts, parameters))
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

    def run_fake(self, engine_factory=FakeEngine):
        with redirect_stdout(io.StringIO()):
            run_model(args=self.args, prepared=self.prepared, tokenizer=self.tokenizer,
                      rules=self.rules, rules_sha256="rule-hash", input_sha256="input-hash",
                      engine_factory=engine_factory, sampling_factory=SimpleNamespace,
                      score_function=self.score, score_config_factory=SimpleNamespace)

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
                patch.dict(os.environ, {"CUDA_VISIBLE_DEVICES": ""}), redirect_stdout(io.StringIO()) as output:
            main(self.argv + ["--preflight", "--limit", "1"])
        self.assertFalse(self.output.exists())
        runner.assert_not_called()
        self.assertTrue(loader.call_args.kwargs["local_files_only"])
        self.assertFalse(loader.call_args.kwargs["trust_remote_code"])
        self.assertEqual(json.loads(output.getvalue())["rows"], 1)

    def test_full_prompt_budget_failure_occurs_before_engine_load(self):
        with self.assertRaisesRegex(ValueError, "full prompt has 2 tokens"):
            prepare_rows(self.rows, self.tokenizer, 1)
        self.assertEqual(self.rows[0]["content"][0]["content"], "a b")

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


if __name__ == "__main__":
    unittest.main()
