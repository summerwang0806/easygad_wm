"""CPU tests for Dipper UP; no torch, transformers, NLTK resources, or GPU."""

from dataclasses import replace
from contextlib import nullcontext, redirect_stderr
import io
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from baseline_acl.paraphrase_up import (
    GeneratedResponse, GenerationConfig, file_sha256, inspect_source,
    generation_seed, window_generation_seed, parse_args, prepare_response, publish_new_file, response_issues,
    run_paraphrasing, validate_output_paths, render_dipper_input, paraphrase_windows, validate_window_audit,
    preflight_source, asset_identity,
    load_sentence_splitter, DipperGenerator,
)

try:
    import pyarrow as pa
    import pyarrow.parquet as pq
except ImportError:
    pa = pq = None


class FakeTokenizer:
    def encode(self, text, add_special_tokens=False):
        return text.split() + (["EOS"] if add_special_tokens else [])


def one_sentence(text):
    return [text]


class FakeGenerator:
    def __init__(self, responses=None, crash_on_attempts=None):
        self.responses = responses or {}
        self.crash_on_attempts = crash_on_attempts or set()
        self.calls = []
        self.attempt_calls = []
        self.config = GenerationConfig()

    def generate(self, prepared_rows, indices, attempts):
        self.calls.extend(indices)
        self.attempt_calls.extend(zip(indices, attempts, strict=True))
        if any((index, attempt) in self.crash_on_attempts for index, attempt in zip(indices, attempts, strict=True)):
            raise RuntimeError("simulated interruption")
        result = []
        for row, index, attempt in zip(prepared_rows, indices, attempts, strict=True):
            candidate = self.responses.get((index, attempt), self.responses.get(index, GeneratedResponse(f"An edited response for row {index}.", "stop", 8)))
            result.append(paraphrase_windows(row, lambda prompt, seed: candidate, FakeTokenizer(), self.config, index, attempt))
        return result


class PureUnitTests(unittest.TestCase):
    def test_defaults_and_answer_only_prompt(self):
        config = GenerationConfig()
        self.assertEqual(config.max_output_length, 512)
        self.assertEqual(config.max_input_tokens, 4096)
        self.assertEqual(config.max_attempts, 1)
        self.assertEqual(config.dtype, "float32")
        self.assertEqual(config.temperature, 1.0)
        self.assertEqual(config.top_k, 0)
        self.assertNotEqual(generation_seed(42, 5, 1), generation_seed(42, 5, 2))
        args = parse_args(["--input", "train.parquet", "--inspect"])
        self.assertTrue(args.inspect)
        self.assertIsNone(args.output)
        self.assertEqual(args.max_output_length, config.max_output_length)
        self.assertIn("dipper", args.model)
        self.assertIn("t5-v1_1-xxl", args.tokenizer)
        result = prepare_response(FakeTokenizer(), "The existing answer.", config, one_sentence)
        prompt = render_dipper_input(result["windows"][0]["text"], "", config)
        self.assertEqual(prompt, "lexical = 40, order = 100 <sent> The existing answer. </sent>")
        self.assertNotIn("watermark", prompt.lower())
        self.assertNotIn("detector", prompt.lower())
        self.assertEqual(result["issues"], [])

    def test_token_budget_never_truncates(self):
        text = "one two three four five six"
        config = replace(GenerationConfig(), max_input_tokens=5, max_output_length=3)
        result = prepare_response(FakeTokenizer(), text, config, one_sentence)
        self.assertEqual(text, result["windows"][0]["text"])
        self.assertEqual(result["source_tokens"], 6)
        self.assertEqual(result["issues"], ["window_0_minimum_input_exceeds_encoder_budget"])
        # Encoder and decoder budgets are independent; input>decoder cap is valid.
        independent = prepare_response(FakeTokenizer(), " ".join(["word"] * 600), GenerationConfig(), one_sentence)
        self.assertEqual(independent["issues"], [])

    def test_generation_failures_are_classified(self):
        config = GenerationConfig()
        self.assertIn("empty_output", response_issues(GeneratedResponse("  ", "stop", 1), "normal", config))
        self.assertIn("length_limit", response_issues(GeneratedResponse("truncated", "length", 511), "normal", config))
        self.assertIn("refusal", response_issues(GeneratedResponse("I cannot rewrite this.", "stop", 6), "normal", config))
        self.assertIn("editorial_preface", response_issues(GeneratedResponse("Here is the rewritten response: hello", "stop", 8), "normal", config))
        # An existing refusal is legitimate text to paraphrase, not a new refusal.
        self.assertNotIn("refusal", response_issues(GeneratedResponse("I cannot help with that.", "stop", 6), "I cannot assist with that.", config))
        self.assertIn("invalid_output_token_count", response_issues(GeneratedResponse("answer", "stop", 0), "normal", config))

    def test_config_rejects_invalid_values(self):
        for config in (replace(GenerationConfig(), batch_size=0), replace(GenerationConfig(), max_output_length=1),
                       replace(GenerationConfig(), temperature=float("nan")), replace(GenerationConfig(), top_p=0),
                       replace(GenerationConfig(), on_failure="silent"), replace(GenerationConfig(), max_attempts=0),
                       replace(GenerationConfig(), lex_diversity=15), replace(GenerationConfig(), window_size=0),
                       replace(GenerationConfig(), dtype="float16"), replace(GenerationConfig(), top_k=50)):
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

    def test_official_window_template_and_row_local_prefix(self):
        tokenizer, config = FakeTokenizer(), GenerationConfig()
        split_inputs = []
        def split(text):
            split_inputs.append(text)
            return ["One.", "Two.", "Three.", "Four."]
        prepared = prepare_response(tokenizer, "One.\n Two.  Three. Four.", config, split)
        self.assertEqual(split_inputs, ["One. Two. Three. Four."])
        self.assertEqual([window["text"] for window in prepared["windows"]], ["One. Two. Three.", "Four."])
        calls = []
        def generate(prompt, seed):
            calls.append((prompt, seed))
            return GeneratedResponse("first edit" if len(calls) == 1 else "second edit", "stop", 3)
        result = paraphrase_windows(prepared, generate, tokenizer, config, 7, 1)
        self.assertEqual(calls[0][0], "lexical = 40, order = 100 <sent> One. Two. Three. </sent>")
        self.assertEqual(calls[1][0], "lexical = 40, order = 100  first edit <sent> Four. </sent>")
        self.assertEqual(result.text, " first edit second edit")
        self.assertEqual(calls[0][1], generation_seed(42, 7, 1))
        self.assertEqual(calls[1][1], window_generation_seed(generation_seed(42, 7, 1), 1))
        self.assertEqual(validate_window_audit(result, prepared, tokenizer, config, 7, 1), [])
        fresh = []
        paraphrase_windows(prepared, lambda prompt, seed: (fresh.append(prompt) or GeneratedResponse("new edit", "stop", 3)),
                           tokenizer, config, 8, 1)
        self.assertNotIn("first edit", fresh[0])

    def test_multiwindow_full_answer_may_exceed_decoder_512(self):
        tokenizer = FakeTokenizer()
        config = replace(GenerationConfig(), window_size=1)
        prepared = prepare_response(tokenizer, "source", config, lambda text: [f"Sentence {i}." for i in range(7)])
        edited = " ".join(["edited"] * 100)
        result = paraphrase_windows(prepared, lambda prompt, seed: GeneratedResponse(edited, "stop", 101), tokenizer, config, 0, 1)
        self.assertEqual(result.output_tokens, 700)
        self.assertEqual(len(result.windows), 7)
        self.assertEqual(response_issues(result, "source", config), [])
        self.assertEqual(validate_window_audit(result, prepared, tokenizer, config, 0, 1), [])

    def test_generated_rolling_prefix_budget_is_checked_without_truncation(self):
        tokenizer = FakeTokenizer()
        config = replace(GenerationConfig(), window_size=1, max_input_tokens=10)
        prepared = prepare_response(tokenizer, "First. Second.", config, lambda text: ["First.", "Second."])
        self.assertEqual(prepared["issues"], [])
        calls = []
        def generate(prompt, seed):
            calls.append(prompt)
            return GeneratedResponse(" ".join(["expanded"] * 20), "stop", 21)
        result = paraphrase_windows(prepared, generate, tokenizer, config, 0, 1)
        self.assertEqual(len(calls), 1)
        self.assertEqual(result.finish_reason, "input_limit")
        self.assertIn("window_1_rolling_prefix_exceeds_encoder_budget", result.issues)
        self.assertGreater(result.windows[1]["input_tokens"], 10)
        self.assertEqual(result.windows[1]["output_tokens"], 0)

    def test_missing_punkt_is_an_explicit_error(self):
        def missing(*args, **kwargs):
            raise LookupError("missing punkt")
        fake = SimpleNamespace(data=SimpleNamespace(path=[]), sent_tokenize=missing)
        with tempfile.TemporaryDirectory() as temporary, patch.dict(sys.modules, {"nltk": fake}):
            with self.assertRaisesRegex(RuntimeError, "No alternate sentence splitter"):
                load_sentence_splitter(Path(temporary))

    def test_model_asset_guard_rejects_non_t5_and_missing_weights(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "config.json").write_text(json.dumps({"model_type": "qwen2"}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "model_type=t5"):
                asset_identity(str(root), weights_required=True)
            (root / "config.json").write_text(json.dumps({"model_type": "t5"}), encoding="utf-8")
            with self.assertRaisesRegex(FileNotFoundError, "weights are missing"):
                asset_identity(str(root), weights_required=True)

    def test_authoritative_punkt_directory_and_resource_fingerprints(self):
        fake = SimpleNamespace(data=SimpleNamespace(path=["unrelated global cache"]),
                               sent_tokenize=lambda text, language: [text])
        with tempfile.TemporaryDirectory() as temporary, patch.dict(sys.modules, {"nltk": fake}):
            root = Path(temporary)
            english = root / "tokenizers" / "punkt_tab" / "english"
            english.mkdir(parents=True)
            names = ("abbrev_types.txt", "collocations.tab", "ortho_context.tab", "sent_starters.txt")
            for name in names:
                (english / name).write_text(name, encoding="utf-8")
            splitter = load_sentence_splitter(root)
            self.assertEqual(fake.data.path, [str(root.resolve())])
            self.assertEqual(splitter.resource_identity["directory"], str(root.resolve()))
            self.assertEqual(splitter.resource_identity["english_punkt_tab"],
                             [{"name": name, "sha256": file_sha256(english / name)} for name in names])
            self.assertIn("nltk_version", splitter.resource_identity)

    def test_asset_preparation_timestamps_do_not_invalidate_resume_identity(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "config.json").write_text(json.dumps({"model_type": "t5"}), encoding="utf-8")
            manifest = {"repo_id": "google/t5-v1_1-xxl", "revision": "fixed", "prepared_at": "yesterday"}
            path = root / "prepare_manifest.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            before = asset_identity(str(root))
            path.write_text(json.dumps({**manifest, "prepared_at": "today", "downloaded_at": "now"}), encoding="utf-8")
            self.assertEqual(before, asset_identity(str(root)))
            self.assertEqual(before["provenance"], {"repo_id": "google/t5-v1_1-xxl", "revision": "fixed"})

    def test_cli_preflight_and_obsolete_backend_flags(self):
        args = parse_args(["--input", "train.parquet", "--preflight"])
        self.assertTrue(args.preflight)
        self.assertIsNone(args.output)
        self.assertEqual(args.top_k, 0)
        self.assertEqual(args.temperature, 1.0)
        with redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                parse_args(["--input", "train.parquet", "--inspect", "--engine", "vllm"])

    def test_t5_decoder_only_output_and_total_length_semantics(self):
        class InputIDs:
            shape = (1, 30)
        class Inputs(dict):
            def to(self, device):
                return self
        class Sequence:
            def __init__(self, values):
                self.values = values
            def tolist(self):
                return self.values
        class Tokenizer(FakeTokenizer):
            def __call__(self, prompts, **kwargs):
                self.kwargs = kwargs
                return Inputs(input_ids=InputIDs())
            def batch_decode(self, outputs, skip_special_tokens):
                return ["rewritten sentence"]
        calls = []
        tokens = [0, 10, 11, 1]
        def generate(**kwargs):
            calls.append(kwargs)
            return [Sequence(list(tokens))]
        engine = DipperGenerator.__new__(DipperGenerator)
        engine.config, engine.tokenizer = GenerationConfig(), Tokenizer()
        engine.torch = SimpleNamespace(manual_seed=lambda seed: None, inference_mode=nullcontext)
        engine.model = SimpleNamespace(generate=generate, generation_config=SimpleNamespace(eos_token_id=1, forced_eos_token_id=None))
        result = engine.generate_window("a much longer encoder source prompt", 42)
        self.assertEqual(result.text, "rewritten sentence")
        self.assertEqual(result.output_tokens, 3)  # start excluded, EOS included
        self.assertEqual(result.finish_reason, "stop")
        self.assertEqual(calls[0]["max_length"], 512)
        self.assertNotIn("max_new_tokens", calls[0])
        self.assertEqual(calls[0]["top_k"], 0)
        self.assertTrue(calls[0]["do_sample"])
        self.assertFalse(engine.tokenizer.kwargs["truncation"])
        tokens[:] = [0] + [10] * 511
        self.assertEqual(engine.generate_window("source", 43).finish_reason, "length")


@unittest.skipIf(pa is None, "pyarrow is needed for parquet integration tests")
class ParquetTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.source = self.root / "kgw_train.parquet"
        self.output = self.root / "up_train.parquet"
        self.checkpoint = self.output.with_suffix(".parquet.progress.jsonl")
        self.audit = self.output.with_suffix(".parquet.audit.json")
        self.tokenizer, self.config = FakeTokenizer(), GenerationConfig(batch_size=1, max_attempts=3)
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
        config = kwargs.pop("config", self.config)
        generator.config = config
        return run_paraphrasing(self.source, self.output, config, self.tokenizer,
                               lambda: generator, self.identity, sentence_splitter=one_sentence, **kwargs)

    def fail_after_first(self):
        bad = FakeGenerator({(1, 1): GeneratedResponse("unfinished text", "length", 511)}, crash_on_attempts={(1, 2)})
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
        self.assertEqual(output["teacher_response"].to_pylist(), [f" An edited response for row {i}." for i in range(3)])
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
        self.assertEqual(report["rejected_attempt_reasons"]["length_limit"], 1)

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
        self.assertEqual(report["fallback_reasons"]["refusal"], 1)
        self.assertEqual(report["rejected_generation_attempts"], 3)
        self.assertEqual(generator.attempt_calls, [(0, 1), (1, 1), (1, 2), (1, 3), (2, 1)])
        self.assertEqual(pq.read_table(self.output)["teacher_response"][1].as_py(), self.rows[1]["teacher_response"])

    def test_budget_failure_does_not_initialize_backend_or_truncate(self):
        generator = FakeGenerator()
        with self.assertRaisesRegex(ValueError, "No source text is truncated"):
            self.run_job(generator, config=replace(self.config, max_input_tokens=2))
        self.assertEqual(generator.calls, [])
        self.assertFalse(self.checkpoint.exists())
        self.assertFalse(self.output.exists())

    def test_explicit_budget_fallback_does_not_generate(self):
        def forbidden_factory():
            self.fail("backend must not initialize when every row has an explicit budget fallback")
        report = run_paraphrasing(self.source, self.output, replace(self.config, max_input_tokens=2, on_failure="keep-original"),
                                 self.tokenizer, forbidden_factory, self.identity, sentence_splitter=one_sentence)
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
                                 self.identity, resume=True, sentence_splitter=one_sentence)
        self.assertEqual(report["processed_rows"], 3)

    def test_distinct_seed_retry_accepts_second_attempt(self):
        generator = FakeGenerator({(0, 1): GeneratedResponse("truncated response", "length", 511)})
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

    def test_default_one_attempt_never_silently_retries(self):
        generator = FakeGenerator({0: GeneratedResponse("I cannot rewrite this.", "stop", 6)})
        with self.assertRaisesRegex(RuntimeError, "exhausted 1 attempts"):
            self.run_job(generator, config=replace(self.config, max_attempts=1))
        self.assertEqual(generator.attempt_calls, [(0, 1)])
        self.assertFalse(self.output.exists())

    def test_cpu_preflight_needs_no_weights_and_keeps_long_sources_valid(self):
        config = replace(self.config, max_output_length=2)
        report = preflight_source(self.source, self.tokenizer, config, one_sentence)
        self.assertTrue(report["valid"])
        self.assertFalse(report["model_weights_loaded"])
        self.assertEqual(report["source_windows_longer_than_decoder_allowance"], 3)
        self.assertEqual(report["windows"], 3)


if __name__ == "__main__":
    unittest.main()
