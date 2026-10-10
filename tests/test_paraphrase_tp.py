"""CPU checks for student TP: prompt budgets, direct logits, durable data output."""

from dataclasses import asdict, replace
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from baseline_acl import paraphrase_tp as tp
from baseline_acl import paraphrase_up as up
from baseline_acl.student_parallel import ParallelStudentGenerator

try:
    import pyarrow as pa
    import pyarrow.parquet as pq
except ImportError:
    pa = pq = None


class Tokenizer:
    chat_template = None
    pad_token_id = None
    eos_token_id = 99

    def encode(self, text, add_special_tokens=False):
        return list(range(1, len(text.split()) + 1)) + ([98] if add_special_tokens else [])

    def apply_chat_template(self, messages, tokenize, add_generation_prompt):
        assert not tokenize and add_generation_prompt
        return f"<chat>{messages[0]['content']}</chat><assistant>"

    def decode(self, ids, **kwargs):
        self.decoded_ids = ids
        return "A complete rewritten answer."

    def __len__(self):
        return 100


class Generator:
    def __init__(self, config, tokenizer=None, candidate=None):
        self.config = config
        self.tokenizer = tokenizer or Tokenizer()
        self.candidate = candidate or up.GeneratedResponse("A targeted revised answer.", "stop", 5)

    def generate(self, rows, indices, attempts):
        return [tp.generate_response(row, lambda prompt, seed: self.candidate,
                                     self.tokenizer, self.config, index, attempt)
                for row, index, attempt in zip(rows, indices, attempts, strict=True)]


class MockStudentWorker:
    def __init__(self, config, gpu):
        self.config, self.gpu = config, gpu

    def generate(self, rows, indices, attempts):
        output = []
        for row, index, attempt in zip(rows, indices, attempts, strict=True):
            time.sleep(row.get("delay", 0))
            payload = {"row": index, "attempt": attempt, "visible": os.environ["CUDA_VISIBLE_DEVICES"],
                       "gpu": self.gpu, "seed": up.generation_seed(self.config.seed, index, attempt),
                       "prompt_mode": self.config.prompt_mode, "max_new_tokens": self.config.max_new_tokens}
            output.append(up.GeneratedResponse(json.dumps(payload), "stop", 12))
        return output


def mock_worker_factory(model, config, tokenizer_path, gpu):
    return MockStudentWorker(config, gpu)


class EntryTests(unittest.TestCase):
    def argv(self, *extra):
        return ["--input", "train.parquet", "--rules", "rules.json", "--model", "qwen", *extra]

    def test_formal_cli_defaults_to_same_student_tokenizer_without_dipper_options(self):
        args = tp.parse_args(self.argv("--inspect"))
        self.assertEqual(args.tokenizer, args.model)
        self.assertEqual((args.inverse_strength, args.max_new_tokens, args.prompt_mode), (2.5, 4096, "completion"))
        for obsolete in ("--rule-tokenizer", "--candidate-top-k", "--lex-diversity", "--nltk-data"):
            with self.subTest(obsolete=obsolete), patch("sys.stderr", new_callable=io.StringIO), self.assertRaises(SystemExit):
                tp.parse_args(self.argv("--inspect", obsolete, "0"))

    def test_model_required_and_invalid_limits_rejected(self):
        with patch("sys.stderr", new_callable=io.StringIO), self.assertRaises(SystemExit):
            tp.parse_args(["--input", "train.parquet", "--rules", "rules.json", "--inspect"])
        for extra in (("--inverse-strength", "nan"), ("--inverse-strength", "-1"), ("--context-window", "0")):
            with self.subTest(extra=extra), patch("sys.stderr", new_callable=io.StringIO), self.assertRaises(SystemExit):
                tp.parse_args(self.argv("--inspect", *extra))

    def test_rules_heldout_and_model_assets_are_protected(self):
        for args in (tp.parse_args(self.argv("--output", "rules.json")),
                     tp.parse_args(self.argv("--output", "qwen/tp.parquet")),
                     tp.parse_args(["--input", "test.parquet", "--rules", "rules.json", "--model", "qwen", "--inspect"])):
            with self.assertRaises(ValueError):
                tp.validate_attack_paths(args)

    def test_inspect_never_imports_transformers_or_probes_cuda(self):
        with patch.object(tp.up, "inspect_source", return_value={"rows": 1, "input_sha256": "hash"}), \
             patch.object(tp.up, "file_sha256", return_value="hash"), \
             patch("baseline_acl.inverse_watermark.RuleTable.load") as load, \
             patch.object(tp.up, "probe_selected_gpus", side_effect=AssertionError("CUDA")), \
             patch.dict(sys.modules, {"transformers": None}), patch("sys.stdout", new_callable=io.StringIO):
            load.return_value.tokenizer = {"vocab_size": 5}
            load.return_value.document = {"provenance": {}}
            report = tp.main(self.argv("--inspect"))
        self.assertEqual(report["method"], tp.METHOD)
        self.assertFalse(report["cross_tokenizer"])
        self.assertFalse(report["tokenizer_identity_checked"])

    def test_attack_identifies_original_student_and_shared_rules(self):
        args = tp.parse_args(self.argv("--inspect"))
        rules = SimpleNamespace(tokenizer={"fingerprint": "f"}, document={"provenance": {"input": {"sha256": "h"}}})
        attack = tp.attack_identity(args, rules, "a" * 64)
        self.assertEqual(attack["paraphraser_model_role"], "original_student_O")
        self.assertIs(attack["cross_tokenizer"], False)
        self.assertIsNone(attack["projection"])
        self.assertTrue(attack["tokenizer_identity_checked"])
        self.assertEqual(asdict(tp.TPWorkerFactory("rules.json", 2.5, "a" * 64)),
                         {"rules_path": "rules.json", "strength": 2.5, "rules_sha256": "a" * 64})

    def test_rule_drift_and_original_corpus_binding(self):
        with patch.object(tp.up, "file_sha256", return_value="new"), self.assertRaisesRegex(ValueError, "audited version"):
            tp.load_bound_rules(Path("rules.json"), "old")
        with patch.object(tp.up, "file_sha256", side_effect=["old", "new"]), \
             patch("baseline_acl.inverse_watermark.RuleTable.load"), self.assertRaisesRegex(ValueError, "while loading"):
            tp.load_bound_rules(Path("rules.json"), "old")
        rules = SimpleNamespace(document={"provenance": {"input": {"sha256": "original"}}})
        tp.validate_rule_source(rules, "original")
        with self.assertRaisesRegex(ValueError, "training corpus"):
            tp.validate_rule_source(rules, "different")

    def test_original_student_binding_checks_path_and_checkpoint_manifest(self):
        original = {"path": str(Path("qwen").resolve()), "weights_fully_hashed": True, "files": [], "manifest_sha256": "m"}
        rules = SimpleNamespace(document={"provenance": {"model_before": original}})
        with self.assertRaisesRegex(ValueError, "original student O"):
            tp.validate_original_student(rules, "different")
        with patch("baseline_acl.steal_watermark.model_asset_identity", return_value=original) as identity:
            tp.validate_original_student(rules, "qwen")
            identity.assert_called_once_with(Path("qwen"), hash_weights=True)
        with patch("baseline_acl.steal_watermark.model_asset_identity", return_value={"changed": True}), \
             self.assertRaisesRegex(ValueError, "changed since"):
            tp.validate_original_student(rules, "qwen")
        with self.assertRaisesRegex(ValueError, "recorded original student"):
            tp.validate_original_student(SimpleNamespace(document={"provenance": {}}), "qwen")

    def test_worker_loads_same_tokenizer_and_direct_shared_processor(self):
        from baseline_acl.inverse_watermark import TransformersInverseWatermarkProcessor
        tokenizer = Tokenizer()
        rules = SimpleNamespace(validate_tokenizer=lambda actual: self.assertIs(actual, tokenizer))
        fake_transformers = SimpleNamespace(AutoTokenizer=SimpleNamespace(from_pretrained=lambda *args, **kwargs: tokenizer))
        worker = tp.TPWorkerFactory("rules.json", 2.5, "h")
        with patch.dict(sys.modules, {"transformers": fake_transformers}), \
             patch.object(tp, "load_bound_rules", return_value=rules), \
             patch.object(tp, "validate_original_student") as original, \
             patch.object(tp, "StudentGenerator") as generator:
            worker("original-model", tp.GenerationConfig(), "student-tokenizer", "3")
        original.assert_called_once_with(rules, "original-model")
        args, kwargs = generator.call_args
        self.assertEqual(args[0], "original-model")
        self.assertIs(args[2], tokenizer)
        self.assertIsInstance(kwargs["logits_processor"], TransformersInverseWatermarkProcessor)

    def test_worker_refuses_mismatched_tokenizer_before_model_loading(self):
        def mismatch(tokenizer): raise ValueError("tokenizer mismatch")
        rules = SimpleNamespace(validate_tokenizer=mismatch)
        fake_transformers = SimpleNamespace(AutoTokenizer=SimpleNamespace(from_pretrained=lambda *args, **kwargs: Tokenizer()))
        with patch.dict(sys.modules, {"transformers": fake_transformers}), \
             patch.object(tp, "load_bound_rules", return_value=rules), patch.object(tp, "StudentGenerator") as generator:
            with self.assertRaisesRegex(ValueError, "tokenizer mismatch"):
                tp.TPWorkerFactory("rules.json", 2.5, "h")("model", tp.GenerationConfig(), "tokenizer", "3")
        generator.assert_not_called()


class PromptAndGenerationTests(unittest.TestCase):
    def setUp(self):
        self.tokenizer = Tokenizer()
        self.config = tp.GenerationConfig(max_input_tokens=500, max_new_tokens=100, context_window=1000)
        self.source = "First factual answer.\n\nSecond paragraph, with number 42."

    def test_complete_source_preserved_once_inside_pure_completion_prompt(self):
        prepared = tp.prepare_response(self.tokenizer, self.source, self.config)
        self.assertEqual(prepared["source"], self.source)
        self.assertIn(self.source, prepared["prompt"])
        self.assertEqual(prepared["prompt"].count(self.source), 1)
        self.assertIn(tp.INSTRUCTION, prepared["prompt"])
        self.assertTrue(prepared["prompt"].endswith("Rewritten answer:\n"))
        self.assertEqual(prepared["issues"], [])

    def test_auto_handles_base_and_chat_without_replacing_tokenizer_template(self):
        self.assertEqual(tp.resolve_prompt_mode(self.tokenizer, "auto"), "completion")
        with self.assertRaisesRegex(ValueError, "own chat template"):
            tp.resolve_prompt_mode(self.tokenizer, "chat")
        self.tokenizer.chat_template = "owned student template"
        self.assertEqual(tp.resolve_prompt_mode(self.tokenizer, "auto"), "chat")
        config = replace(self.config, prompt_mode="chat")
        prepared = tp.prepare_response(self.tokenizer, self.source, config)
        self.assertTrue(prepared["prompt"].startswith("<chat>"))
        self.assertEqual(prepared["prompt_tokens"], len(self.tokenizer.encode(prepared["prompt"], add_special_tokens=False)))
        self.assertEqual(self.tokenizer.chat_template, "owned student template")

    def test_budget_counts_instructions_and_total_causal_context(self):
        prepared = tp.prepare_response(self.tokenizer, self.source, self.config)
        input_limit = replace(self.config, max_input_tokens=prepared["prompt_tokens"] - 1)
        self.assertIn("full_prompt_exceeds_input_budget", tp.prepare_response(self.tokenizer, self.source, input_limit)["issues"])
        context_limit = replace(self.config, context_window=prepared["prompt_tokens"] + self.config.max_new_tokens - 1)
        self.assertIn("prompt_plus_output_exceeds_context_window", tp.prepare_response(self.tokenizer, self.source, context_limit)["issues"])
        exactly = replace(self.config, context_window=prepared["prompt_tokens"] + self.config.max_new_tokens)
        self.assertEqual(tp.prepare_response(self.tokenizer, self.source, exactly)["issues"], [])

    def test_rejects_empty_original_instruction_echo_and_length_truncation(self):
        for candidate, issue in ((up.GeneratedResponse("", "stop", 1), "empty_output"),
                                 (up.GeneratedResponse(self.source, "stop", 5), "unchanged_source_answer"),
                                 (up.GeneratedResponse("</source_answer> echoed", "stop", 5), "prompt_or_instruction_echo"),
                                 (up.GeneratedResponse("Here is the rewritten text: words", "stop", 5), "editorial_preface"),
                                 (up.GeneratedResponse("A revised answer.", "length", 100), "length_limit")):
            with self.subTest(issue=issue):
                self.assertIn(issue, tp.candidate_issues(candidate, self.source, self.config))

    def test_single_generation_audit_binds_exact_prompt_source_row_seed_and_output(self):
        prepared = tp.prepare_response(self.tokenizer, self.source, self.config)
        calls = []
        def generate(prompt, seed):
            calls.append((prompt, seed))
            return up.GeneratedResponse("A fully rewritten answer.", "stop", 7)
        candidate = tp.generate_response(prepared, generate, self.tokenizer, self.config, 4, 2)
        self.assertEqual(calls, [(prepared["prompt"], up.generation_seed(42, 4, 2))])
        self.assertEqual(tp.validate_audit(candidate, prepared, self.tokenizer, self.config, 4, 2), [])
        candidate.windows[0]["prompt_sha256"] = "tampered"
        self.assertIn("causal_generation_audit_mismatch", tp.validate_audit(candidate, prepared, self.tokenizer, self.config, 4, 2))

    def test_causal_backend_extracts_only_new_tokens_and_disables_forced_eos(self):
        class Tensor:
            def __init__(self, values): self.values = values
            def __getitem__(self, index): return Tensor(self.values[index])
            def tolist(self): return self.values
        class Inference:
            def __enter__(self): return None
            def __exit__(self, *args): return None
        calls = {}
        prompt = tp.render_prompt(self.tokenizer, self.source, self.config)
        ids = tp.prompt_ids(self.tokenizer, prompt, self.config)
        def generate(**kwargs):
            calls.update(kwargs)
            return Tensor([ids + [4, 7, 99]])
        generator = tp.StudentGenerator.__new__(tp.StudentGenerator)
        generator.tokenizer, generator.config = self.tokenizer, self.config
        generator.eos_ids, generator.logits_processor = {99}, "direct processor"
        generator.torch = SimpleNamespace(manual_seed=lambda seed: None, tensor=lambda value, **kwargs: value,
                                         long="long", ones_like=lambda value: "mask", inference_mode=Inference)
        generator.model = SimpleNamespace(generate=generate)
        candidate = generator.generate_prompt(prompt, 42)
        self.assertEqual(self.tokenizer.decoded_ids, [4, 7, 99])
        self.assertEqual((candidate.finish_reason, candidate.output_tokens), ("stop", 3))
        self.assertEqual(calls["logits_processor"], ["direct processor"])
        self.assertEqual(calls["max_new_tokens"], 100)
        self.assertIsNone(calls["forced_eos_token_id"])
        generator.model.generate = lambda **kwargs: Tensor([ids + [4, 7]])
        self.assertEqual(generator.generate_prompt(prompt, 42).finish_reason, "length")
        generator.model.generate = lambda **kwargs: Tensor([[123] + ids[1:] + [99]])
        with self.assertRaisesRegex(RuntimeError, "unexpected prompt prefix"):
            generator.generate_prompt(prompt, 42)

    def test_spawned_workers_get_student_config_and_explicit_independent_gpu_masks(self):
        config = replace(self.config, max_new_tokens=123, prompt_mode="chat")
        with ParallelStudentGenerator("unused", config, "unused", ["1", "3"],
                                      worker_factory=mock_worker_factory, startup_timeout=15) as pool:
            results = list(pool.iter_generate([{"delay": 0.4}, {}, {}, {}], [4, 5, 6, 7], [2] * 4))
            self.assertEqual({index for index, _, _ in results}, {4, 5, 6, 7})
            for index, attempt, candidate in results:
                payload = json.loads(candidate.text)
                self.assertEqual(payload["visible"], payload["gpu"])
                self.assertEqual(payload["seed"], up.generation_seed(42, index, attempt))
                self.assertEqual((payload["prompt_mode"], payload["max_new_tokens"]), ("chat", 123))
        self.assertTrue(all(not process.is_alive() for _, process in pool._processes))


@unittest.skipIf(pa is None, "pyarrow is required for Parquet checks")
class DataContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source, self.output = self.root / "train.parquet", self.root / "tp.parquet"
        self.table = pa.table({"id": ["a", "b"], "content": ["question a", "question b"],
                               "teacher_response": ["Original answer a.", "Original answer b."],
                               "category": ["qa", "qa"], "grounded": [True, False],
                               "flaw": [None, None], "agreement": [None, None]}).replace_schema_metadata({b"source": b"strict-source"})
        pq.write_table(self.table, self.source)
        self.config = tp.GenerationConfig(max_input_tokens=500, max_new_tokens=100, context_window=1000)
        args = SimpleNamespace(inverse_strength=2.5)
        rules = SimpleNamespace(tokenizer={"fingerprint": "f"}, document={"provenance": {}})
        self.identity = {"model": "fake-local-original-student", "attack": tp.attack_identity(args, rules, "a" * 64)}

    def run_job(self, candidate=None, factory=None, **kwargs):
        return tp.run_paraphrasing(self.source, self.output, self.config, Tokenizer(),
                                  factory or (lambda: Generator(self.config, candidate=candidate)), self.identity, **kwargs)

    def test_only_response_changes_and_formal_audit_has_no_dipper_contract(self):
        with patch.object(up, "load_sentence_splitter", side_effect=AssertionError("NLTK")):
            report = self.run_job()
        result = pq.read_table(self.output)
        self.assertTrue(result.schema.equals(self.table.schema, check_metadata=True))
        for name in self.table.column_names:
            if name != "teacher_response": self.assertTrue(result[name].equals(self.table[name]))
        self.assertEqual(report["method"], tp.METHOD)
        self.assertEqual(report["attack"], self.identity["attack"])
        self.assertEqual(report["input_sha256"], up.file_sha256(self.source))
        self.assertEqual(report["output_sha256"], up.file_sha256(self.output))
        self.assertEqual(report["changed_teacher_responses"], 2)
        self.assertEqual(report["metadata"]["generation_contract"]["architecture"], "causal_LM")
        self.assertNotIn("model_card", report)
        self.assertNotIn("max_encoder_input_tokens", report)
        with self.assertRaises(FileExistsError): self.run_job()

    def test_budget_preflight_checks_all_rows_before_backend_creation(self):
        self.config = replace(self.config, max_input_tokens=1)
        report = tp.preflight_source(self.source, Tokenizer(), self.config)
        self.assertEqual(len(report["invalid_rows"]), 2)
        self.assertFalse(report["valid"])
        with self.assertRaisesRegex(ValueError, "budget"):
            self.run_job(factory=lambda: self.fail("must not load a backend"))
        self.assertFalse(self.output.exists())

    def test_main_preflight_reads_all_rows_with_cpu_tokenizer_and_no_model_cuda_nltk(self):
        tokenizer = Tokenizer()
        validated = []
        rules = SimpleNamespace(tokenizer={"fingerprint": "f"}, document={"provenance": {}},
                                validate_tokenizer=lambda actual: validated.append(actual))
        fake_transformers = SimpleNamespace(
            AutoConfig=SimpleNamespace(from_pretrained=lambda *args, **kwargs: SimpleNamespace(is_encoder_decoder=False, max_position_embeddings=1000)),
            AutoTokenizer=SimpleNamespace(from_pretrained=lambda *args, **kwargs: tokenizer))
        argv = ["--input", str(self.source), "--rules", str(self.root / "rules.json"), "--model", "original",
                "--max-input-tokens", "500", "--max-new-tokens", "100", "--preflight"]
        with patch.dict(sys.modules, {"transformers": fake_transformers}), \
             patch.object(tp, "load_bound_rules", return_value=rules), \
             patch.object(tp, "validate_original_student"), patch.object(up, "asset_identity"), \
             patch.object(up, "file_sha256", return_value="h"), \
             patch.object(up, "probe_selected_gpus", side_effect=AssertionError("GPU")), \
             patch.object(up, "load_sentence_splitter", side_effect=AssertionError("NLTK")), \
             patch.object(tp, "StudentGenerator", side_effect=AssertionError("model weights")), \
             patch("sys.stdout", new_callable=io.StringIO):
            report = tp.main(argv)
        self.assertTrue(report["valid"])
        self.assertEqual(report["rows"], 2)
        self.assertFalse(report["model_weights_loaded"])
        self.assertEqual(report["config"]["context_window"], 1000)
        self.assertEqual(validated, [tokenizer])

    def test_truncated_output_is_checkpointed_rejected_without_final_dataset(self):
        with self.assertRaisesRegex(RuntimeError, "exhausted"):
            self.run_job(candidate=up.GeneratedResponse("A partial paraphrase.", "length", 100))
        self.assertFalse(self.output.exists())
        entries = [json.loads(line) for line in self.output.with_suffix(".parquet.progress.jsonl").read_text().splitlines()]
        self.assertEqual(entries[1]["status"], "rejected")
        self.assertIn("length_limit", entries[1]["issues"])

    def test_resume_rejects_rule_hash_prompt_mode_and_output_audit_tampering(self):
        with patch.object(up, "publish_new_file", side_effect=RuntimeError("interrupt publication")), self.assertRaises(RuntimeError):
            self.run_job()
        original_hash = self.identity["attack"]["rules_sha256"]
        self.identity["attack"]["rules_sha256"] = "b" * 64
        with self.assertRaisesRegex(ValueError, "fingerprint"): self.run_job(resume=True)
        self.identity["attack"]["rules_sha256"] = original_hash
        self.config = replace(self.config, context_window=1001)
        with self.assertRaisesRegex(ValueError, "fingerprint"): self.run_job(resume=True)
        self.config = replace(self.config, context_window=1000)
        checkpoint = self.output.with_suffix(".parquet.progress.jsonl")
        lines = [json.loads(line) for line in checkpoint.read_text().splitlines()]
        lines[1]["windows"][0]["prompt_sha256"] = "tampered"
        checkpoint.write_text("".join(json.dumps(line) + "\n" for line in lines), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "invalid accepted"): self.run_job(resume=True)

    def test_resume_keeps_completed_rows_and_repairs_only_partial_final_tail(self):
        with patch.object(up, "publish_new_file", side_effect=RuntimeError("interrupt publication")), self.assertRaises(RuntimeError):
            self.run_job()
        checkpoint = self.output.with_suffix(".parquet.progress.jsonl")
        with checkpoint.open("ab") as handle: handle.write(b'{"partial":')
        report = self.run_job(resume=True, factory=lambda: self.fail("completed rows must not regenerate"))
        self.assertTrue(report["complete"])
        self.assertTrue(checkpoint.read_bytes().endswith(b"\n"))

    def test_resume_recovers_audit_publication_before_parquet_without_overwriting(self):
        original_publish = up.publish_new_file
        publications = []
        def interrupt_after_audit(temporary, destination):
            publications.append(destination)
            if len(publications) == 2:
                raise RuntimeError("interrupt after audit")
            return original_publish(temporary, destination)
        with patch.object(up, "publish_new_file", side_effect=interrupt_after_audit), self.assertRaisesRegex(RuntimeError, "interrupt after audit"):
            self.run_job()
        audit = self.output.with_suffix(".parquet.audit.json")
        previous = audit.read_bytes()
        self.assertFalse(self.output.exists())
        report = self.run_job(resume=True, factory=lambda: self.fail("completed rows must not regenerate"))
        self.assertEqual(audit.read_bytes(), previous)
        self.assertTrue(report["complete"])
        self.assertEqual(report["output_sha256"], up.file_sha256(self.output))

    def test_explicit_keep_original_records_visible_fallback(self):
        self.config = replace(self.config, on_failure="keep-original")
        report = self.run_job(candidate=up.GeneratedResponse("", "stop", 1))
        self.assertEqual(report["fallback_rows"], [0, 1])
        self.assertEqual(report["status_counts"], {"fallback": 2})
        self.assertEqual(pq.read_table(self.output)["teacher_response"].to_pylist(), self.table["teacher_response"].to_pylist())


if __name__ == "__main__":
    unittest.main()
