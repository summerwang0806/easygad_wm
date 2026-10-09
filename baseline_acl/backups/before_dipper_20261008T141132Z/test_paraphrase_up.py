"""CPU tests for UP orchestration; no torch, transformers, or vLLM import."""

from dataclasses import replace
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from baseline_acl.paraphrase_up import (
    GeneratedResponse, GenerationConfig, file_sha256, inspect_source,
    generation_seed, parse_args, prepare_response, publish_new_file, response_issues,
    run_paraphrasing, validate_output_paths,
)

try:
    import pyarrow as pa
    import pyarrow.parquet as pq
except ImportError:
    pa = pq = None


class FakeTokenizer:
    def encode(self, text, add_special_tokens=False):
        return text.split()

    def apply_chat_template(self, messages, add_generation_prompt=True, tokenize=False):
        return "\n".join(message["content"] for message in messages) + "\nASSISTANT:"


class FakeGenerator:
    def __init__(self, responses=None, crash_on_attempts=None):
        self.responses = responses or {}
        self.crash_on_attempts = crash_on_attempts or set()
        self.calls = []
        self.attempt_calls = []

    def generate(self, prompts, indices, attempts):
        self.calls.extend(indices)
        self.attempt_calls.extend(zip(indices, attempts, strict=True))
        if any((index, attempt) in self.crash_on_attempts for index, attempt in zip(indices, attempts, strict=True)):
            raise RuntimeError("simulated interruption")
        return [self.responses.get((i, attempt), self.responses.get(i, GeneratedResponse(f"An edited response for row {i}.", "stop", 8)))
                for i, attempt in zip(indices, attempts, strict=True)]


class PureUnitTests(unittest.TestCase):
    def test_defaults_and_answer_only_prompt(self):
        config = GenerationConfig()
        self.assertEqual(config.max_new_tokens, 2048)
        self.assertEqual(config.max_context_length, 4096)
        self.assertEqual(config.max_attempts, 3)
        self.assertNotEqual(generation_seed(42, 5, 1), generation_seed(42, 5, 2))
        args = parse_args(["--input", "train.parquet", "--inspect"])
        self.assertTrue(args.inspect)
        self.assertIsNone(args.output)
        self.assertEqual(args.max_new_tokens, config.max_new_tokens)
        result = prepare_response(FakeTokenizer(), "The existing answer.", config)
        self.assertIn("The existing answer.", result["prompt"])
        self.assertNotIn("watermark", result["prompt"].lower())
        self.assertNotIn("detector", result["prompt"].lower())
        self.assertEqual(result["issues"], [])

    def test_token_budget_never_truncates(self):
        text = "one two three four five six"
        config = replace(GenerationConfig(), max_new_tokens=5, max_context_length=10)
        result = prepare_response(FakeTokenizer(), text, config)
        self.assertIn(text, result["prompt"])
        self.assertEqual(result["source_tokens"], 6)
        self.assertEqual(result["issues"], ["source_exceeds_generation_budget", "prompt_plus_generation_exceeds_context"])

    def test_generation_failures_are_classified(self):
        config = GenerationConfig()
        self.assertIn("empty_output", response_issues(GeneratedResponse("  ", "stop", 1), "normal", config))
        self.assertIn("length_limit", response_issues(GeneratedResponse("truncated", "length", 2048), "normal", config))
        self.assertIn("refusal", response_issues(GeneratedResponse("I cannot rewrite this.", "stop", 6), "normal", config))
        self.assertIn("editorial_preface", response_issues(GeneratedResponse("Here is the rewritten response: hello", "stop", 8), "normal", config))
        # An existing refusal is legitimate text to paraphrase, not a new refusal.
        self.assertNotIn("refusal", response_issues(GeneratedResponse("I cannot help with that.", "stop", 6), "I cannot assist with that.", config))
        self.assertIn("invalid_output_token_count", response_issues(GeneratedResponse("answer", "stop", 0), "normal", config))

    def test_config_rejects_invalid_values(self):
        for config in (replace(GenerationConfig(), batch_size=0), replace(GenerationConfig(), max_new_tokens=4096),
                       replace(GenerationConfig(), temperature=float("nan")), replace(GenerationConfig(), top_p=0),
                       replace(GenerationConfig(), on_failure="silent"), replace(GenerationConfig(), max_attempts=0)):
            with self.assertRaises(ValueError):
                config.validate()

    def test_paths_refuse_heldout_and_overwrite(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source, target, checkpoint, audit = [root / name for name in ("train.parquet", "up.parquet", "up.jsonl", "up.json")]
            with self.assertRaises(ValueError):
                validate_output_paths(root / "dolly_test.parquet", target, checkpoint, audit, False)
            with self.assertRaises(ValueError):
                validate_output_paths(source, source, checkpoint, audit, False)
            target.touch()
            with self.assertRaises(FileExistsError):
                validate_output_paths(source, target, checkpoint, audit, False)


@unittest.skipIf(pa is None, "pyarrow is needed for parquet integration tests")
class ParquetTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.source = self.root / "kgw_train.parquet"
        self.output = self.root / "up_train.parquet"
        self.checkpoint = self.output.with_suffix(".parquet.progress.jsonl")
        self.audit = self.output.with_suffix(".parquet.audit.json")
        self.tokenizer, self.config = FakeTokenizer(), GenerationConfig(batch_size=1)
        self.identity = {"model": "fake", "revision": "fixed"}
        content_type = pa.list_(pa.field("element", pa.struct([pa.field("content", pa.string()), pa.field("role", pa.string())])))
        self.schema = pa.schema([
            pa.field("id", pa.string()), pa.field("content", content_type),
            pa.field("teacher_response", pa.string(), metadata={b"field_contract": b"preserve"}),
            pa.field("category", pa.string()), pa.field("grounded", pa.bool_()),
            pa.field("flaw", pa.string()), pa.field("agreement", pa.bool_()),
        ], metadata={b"huggingface": b'{"info":{"features":{}}}', b"source_contract": b"keep me"})
        self.rows = [
            {"id": f"source-{index}", "content": [{"role": "user", "content": f"UNCHANGED question {index}"}],
             "teacher_response": f"Original answer number {index}.", "category": "open_qa", "grounded": bool(index % 2),
             "flaw": "normal", "agreement": None if index == 0 else True}
            for index in range(3)
        ]
        self.table = pa.Table.from_pylist(self.rows, schema=self.schema)
        pq.write_table(self.table, self.source)

    def tearDown(self):
        self.temporary.cleanup()

    def run_job(self, generator, **kwargs):
        return run_paraphrasing(self.source, self.output, kwargs.pop("config", self.config), self.tokenizer,
                               lambda: generator, self.identity, **kwargs)

    def fail_after_first(self):
        bad = FakeGenerator({(1, 1): GeneratedResponse("unfinished text", "length", 2048)}, crash_on_attempts={(1, 2)})
        with self.assertRaisesRegex(RuntimeError, "simulated interruption"):
            self.run_job(bad)
        self.assertEqual(bad.calls, [0, 1, 1])
        self.assertFalse(self.output.exists())
        self.assertFalse(self.audit.exists())

    def test_full_parquet_contract_and_audit(self):
        before_hash = file_sha256(self.source)
        generator = FakeGenerator()
        report = self.run_job(generator)
        output = pq.read_table(self.output)
        self.assertEqual(generator.calls, [0, 1, 2])
        self.assertEqual(file_sha256(self.source), before_hash)
        self.assertTrue(output.schema.equals(self.schema, check_metadata=True))
        for name in self.schema.names:
            if name != "teacher_response":
                self.assertTrue(output[name].equals(self.table[name]), name)
        self.assertEqual(output["teacher_response"].to_pylist(), [f"An edited response for row {i}." for i in range(3)])
        self.assertEqual(report["rows"], 3)
        self.assertEqual(report["status_counts"], {"ok": 3})
        self.assertEqual(report["output_sha256"], file_sha256(self.output))
        self.assertEqual(json.loads(self.audit.read_text(encoding="utf-8")), report)
        self.assertEqual(len(self.checkpoint.read_text(encoding="utf-8").splitlines()), 4)

    def test_resume_keeps_successes_and_retries_only_failure(self):
        self.fail_after_first()
        generator = FakeGenerator()
        report = self.run_job(generator, resume=True)
        self.assertEqual(generator.calls, [1, 2])
        self.assertEqual(generator.attempt_calls, [(1, 2), (2, 1)])
        self.assertEqual(report["status_counts"], {"ok": 3})
        self.assertEqual(report["rejected_generation_attempts"], 1)
        self.assertEqual(report["rejected_attempt_reasons"], {"length_limit": 1})

    def test_resume_repairs_only_an_incomplete_tail(self):
        self.fail_after_first()
        with self.checkpoint.open("ab") as handle:
            handle.write(b'{"partial":')
        generator = FakeGenerator()
        self.run_job(generator, resume=True)
        self.assertEqual(generator.calls, [1, 2])
        for line in self.checkpoint.read_text(encoding="utf-8").splitlines():
            json.loads(line)

    def test_resume_rejects_input_and_config_drift(self):
        self.fail_after_first()
        generator = FakeGenerator()
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            self.run_job(generator, resume=True, config=replace(self.config, temperature=0.7))
        self.assertEqual(generator.calls, [])
        rows = list(self.rows)
        rows[1] = {**rows[1], "teacher_response": "Changed source response."}
        pq.write_table(pa.Table.from_pylist(rows, schema=self.schema), self.source)
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            self.run_job(generator, resume=True)
        self.assertEqual(generator.calls, [])

    def test_resume_rejects_tampered_success(self):
        self.fail_after_first()
        lines = self.checkpoint.read_text(encoding="utf-8").splitlines()
        record = json.loads(lines[1])
        record["finish_reason"] = "length"
        lines[1] = json.dumps(record)
        self.checkpoint.write_text("\n".join(lines) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "invalid accepted generation"):
            self.run_job(FakeGenerator(), resume=True)

    def test_fallback_requires_explicit_option_and_is_audited(self):
        generator = FakeGenerator({1: GeneratedResponse("I cannot rewrite this.", "stop", 6)})
        report = self.run_job(generator, config=replace(self.config, on_failure="keep-original"))
        self.assertEqual(report["status_counts"], {"ok": 2, "fallback": 1})
        self.assertEqual(report["fallback_rows"], [1])
        self.assertEqual(report["fallback_reasons"], {"refusal": 1})
        self.assertEqual(report["rejected_generation_attempts"], 3)
        self.assertEqual(generator.attempt_calls, [(0, 1), (1, 1), (1, 2), (1, 3), (2, 1)])
        self.assertEqual(pq.read_table(self.output)["teacher_response"][1].as_py(), self.rows[1]["teacher_response"])

    def test_budget_failure_does_not_initialize_backend_or_truncate(self):
        generator = FakeGenerator()
        with self.assertRaisesRegex(ValueError, "No source text is truncated"):
            self.run_job(generator, config=replace(self.config, max_new_tokens=2))
        self.assertEqual(generator.calls, [])
        self.assertFalse(self.checkpoint.exists())
        self.assertFalse(self.output.exists())

    def test_explicit_budget_fallback_does_not_generate(self):
        def forbidden_factory():
            self.fail("backend must not initialize when every row has an explicit budget fallback")
        report = run_paraphrasing(self.source, self.output, replace(self.config, max_new_tokens=2, on_failure="keep-original"),
                                 self.tokenizer, forbidden_factory, self.identity)
        self.assertEqual(report["status_counts"], {"fallback": 3})
        self.assertEqual(report["fallback_rows"], [0, 1, 2])
        self.assertTrue(pq.read_table(self.output).equals(self.table, check_metadata=True))

    def test_cpu_inspection_and_output_overwrite(self):
        info = inspect_source(self.source)
        self.assertEqual(info["rows"], 3)
        self.assertFalse(info["token_budget_checked"])
        self.run_job(FakeGenerator())
        with self.assertRaises(FileExistsError):
            self.run_job(FakeGenerator(), resume=True)

    def test_completed_resume_does_not_initialize_backend(self):
        self.run_job(FakeGenerator())
        self.output.rename(self.output.with_suffix(".saved.parquet"))
        self.audit.rename(self.audit.with_suffix(".saved.json"))
        def forbidden_factory():
            self.fail("fully completed checkpoint must not initialize the model")
        report = run_paraphrasing(self.source, self.output, self.config, self.tokenizer, forbidden_factory,
                                 self.identity, resume=True)
        self.assertEqual(report["processed_rows"], 3)

    def test_distinct_seed_retry_accepts_second_attempt(self):
        generator = FakeGenerator({(0, 1): GeneratedResponse("truncated response", "length", 2048)})
        report = self.run_job(generator)
        self.assertEqual(generator.attempt_calls, [(0, 1), (0, 2), (1, 1), (2, 1)])
        self.assertEqual(report["accepted_attempts"], {"2": 1, "1": 2})
        records = [json.loads(line) for line in self.checkpoint.read_text(encoding="utf-8").splitlines()[1:]]
        self.assertEqual(records[0]["row_index"], records[1]["row_index"])
        self.assertNotEqual(records[0]["seed"], records[1]["seed"])
        self.assertEqual([records[0]["attempt"], records[1]["attempt"]], [1, 2])

    def test_exhausted_attempts_never_finalize_or_repeat_on_resume(self):
        generator = FakeGenerator({0: GeneratedResponse("I cannot rewrite this.", "stop", 6)})
        with self.assertRaisesRegex(RuntimeError, "exhausted 3 attempts"):
            self.run_job(generator)
        self.assertEqual(generator.attempt_calls, [(0, 1), (0, 2), (0, 3)])
        self.assertFalse(self.output.exists())
        self.assertFalse(self.audit.exists())
        resumed = FakeGenerator()
        with self.assertRaisesRegex(RuntimeError, "already exhausted"):
            self.run_job(resumed, resume=True)
        self.assertEqual(resumed.calls, [])

    def test_orphan_audit_recovers_final_publication_without_generation(self):
        def interrupt_publication(temporary, destination):
            if destination == self.output:
                raise OSError("simulated publication interruption")
            publish_new_file(temporary, destination)
        with patch("baseline_acl.paraphrase_up.publish_new_file", side_effect=interrupt_publication):
            with self.assertRaisesRegex(OSError, "publication interruption"):
                self.run_job(FakeGenerator())
        self.assertTrue(self.audit.exists())
        self.assertFalse(self.output.exists())
        before = self.audit.read_bytes()
        generator = FakeGenerator()
        self.run_job(generator, resume=True)
        self.assertEqual(generator.calls, [])
        self.assertEqual(self.audit.read_bytes(), before)
        self.assertEqual(pq.read_table(self.output).num_rows, 3)

    def test_conflicting_orphan_audit_is_never_changed(self):
        self.run_job(FakeGenerator())
        self.output.rename(self.output.with_suffix(".saved.parquet"))
        report = json.loads(self.audit.read_text(encoding="utf-8"))
        report["metadata"]["fingerprint"] = "unrelated job"
        self.audit.write_text(json.dumps(report), encoding="utf-8")
        before = self.audit.read_bytes()
        generator = FakeGenerator()
        with self.assertRaisesRegex(FileExistsError, "does not match"):
            self.run_job(generator, resume=True)
        self.assertEqual(generator.calls, [])
        self.assertEqual(self.audit.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
