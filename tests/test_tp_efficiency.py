"""CPU regression checks for cached rules, early aborts and policy-aware resume."""

from dataclasses import replace
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from baseline_acl import paraphrase_tp as tp
from baseline_acl import paraphrase_up as up
from baseline_acl.inverse_watermark import RuleTable, TransformersInverseWatermarkProcessor
from tests.test_inverse_watermark import rules_document
from tests import test_paraphrase_tp as fixtures

try:
    import torch
except ImportError:
    torch = None


@unittest.skipIf(torch is None, "tensor equivalence checks require PyTorch")
class CachedBiasTests(unittest.TestCase):
    def test_cached_tensor_bias_is_bitwise_equal_to_original_combined_penalty(self):
        document = rules_document()
        document["global_scores"] = {"0": 0.0, "1": .09, "2": .4, "3": .7}
        document["prefix_scores"]["2"]["weight"] = .17
        document["prefix_scores"]["1,2"]["weight"] = .83
        rules = RuleTable(document)
        histories = torch.tensor([[0, 1, 2], [0, 0, 1], [0, 0, 2], [0, 3, 0]])
        for dtype in (torch.float32, torch.float64, torch.float16, torch.bfloat16):
            processor = TransformersInverseWatermarkProcessor(rules, 2.5)
            for _ in range(2):
                scores = torch.tensor([[7.13, -2.7, 0.1, 10.2, 100.0]] * 4, dtype=dtype)
                expected = scores.clone()
                for index, context in enumerate(histories.tolist()):
                    penalties = rules.penalties(context)
                    indices = list(penalties)
                    expected[index, indices] -= torch.tensor([2.5 * penalties[token] for token in indices], dtype=dtype)
                processor(histories, scores)
                self.assertTrue(torch.equal(scores, expected), dtype)
            cache = next(iter(processor._direct_bias._device_cache.values()))
            pointers = (cache[0].data_ptr(), cache[1].data_ptr())
            with patch.object(rules, "penalties", side_effect=AssertionError("full table rebuilt")):
                processor(histories, torch.ones((4, 5), dtype=dtype))
            self.assertEqual(pointers, (cache[0].data_ptr(), cache[1].data_ptr()))

    def test_invalid_context_does_not_mutate_scores(self):
        processor = TransformersInverseWatermarkProcessor(RuleTable(rules_document()))
        scores = torch.ones((1, 5))
        with self.assertRaises(ValueError):
            processor(torch.tensor([[99]]), scores)
        self.assertTrue(torch.equal(scores, torch.ones((1, 5))))


class CharTokenizer:
    pad_token_id = None

    def encode(self, text, add_special_tokens=False):
        return list(map(ord, text))

    def decode(self, tokens, **kwargs):
        return "".join(chr(token) for token in tokens if token)


@unittest.skipIf(torch is None, "early-stop tensor checks require PyTorch")
class EfficientGenerationTests(unittest.TestCase):
    def test_adaptive_budget_keeps_long_answer_capacity_and_obeys_hard_limit(self):
        config = tp.GenerationConfig(generation_policy="efficient-v1")
        self.assertEqual(tp.output_budget(10, config), 256)
        self.assertEqual(tp.output_budget(125, config), 378)
        self.assertEqual(tp.output_budget(1536, config), 3200)
        self.assertEqual(tp.output_budget(5000, config), 4096)
        self.assertEqual(tp.output_budget(125, replace(config, max_new_tokens=100)), 100)
        self.assertEqual(tp.output_budget(125, replace(config, generation_policy="legacy")), 4096)

    def test_guard_ignores_prompt_and_detects_non_power_of_two_repetition(self):
        tokenizer = CharTokenizer()
        prompt = "Rewritten answer: "
        guard = tp.EarlyStopGuard(tokenizer, len(prompt))
        ordinary = "0123456789ABCDEF"
        self.assertFalse(guard(torch.tensor([tokenizer.encode(prompt + ordinary)])))
        repeated = ("abcdefghijk" * 6)[:64]
        self.assertTrue(guard(torch.tensor([tokenizer.encode(prompt + repeated)])))
        self.assertEqual(guard.reason, "repetition_loop")

    def test_guard_and_final_validation_reject_prompt_echo(self):
        tokenizer = CharTokenizer()
        text = "Rewritten answer:XYZ0123456789AB"
        self.assertEqual(len(text), 32)
        guard = tp.EarlyStopGuard(tokenizer, 0)
        self.assertTrue(guard(torch.tensor([tokenizer.encode(text)])))
        self.assertEqual(guard.reason, "generation_prompt_echo")
        candidate = tp.GeneratedResponse("Answer. You are an AI assistant.", "stop", 9)
        self.assertNotIn("generation_prompt_echo", tp.candidate_issues(candidate, "Answer.", tp.GenerationConfig()))
        self.assertIn("generation_prompt_echo", tp.candidate_issues(candidate, "Answer.", tp.GenerationConfig(generation_policy="efficient-v1")))

    def test_backend_passes_row_budget_and_never_accepts_early_abort_as_eos(self):
        config = tp.GenerationConfig(generation_policy="efficient-v1")
        tokenizer = CharTokenizer()
        generator = tp.StudentGenerator.__new__(tp.StudentGenerator)
        generator.config, generator.tokenizer = config, tokenizer
        generator.eos_ids, generator.logits_processor = {0}, "rule hook"
        generator.torch = SimpleNamespace(manual_seed=torch.manual_seed, tensor=lambda values, **kwargs: torch.tensor(values),
                                         long=torch.long, ones_like=torch.ones_like, inference_mode=torch.inference_mode)
        calls = {}
        def generate(**kwargs):
            calls.update(kwargs)
            prompt = kwargs["input_ids"][0].tolist()
            repeated = tokenizer.encode(("abcdefghijk" * 6)[:64])
            sequence = torch.tensor([prompt + repeated])
            self.assertTrue(kwargs["stopping_criteria"][0](sequence, None))
            return sequence
        generator.model = SimpleNamespace(generate=generate)
        source = "A" * 125
        prepared = tp.prepare_response(tokenizer, source, config)
        candidate = generator.generate([prepared], [4], [2])[0]
        self.assertEqual(calls["max_new_tokens"], 378)
        self.assertTrue(calls["use_cache"])
        self.assertEqual(candidate.finish_reason, "early_stop")
        self.assertIn("repetition_loop", candidate.issues)
        self.assertEqual(candidate.windows[0]["effective_max_new_tokens"], 378)
        self.assertEqual(tp.validate_audit(candidate, prepared, tokenizer, config, 4, 2), [])


@unittest.skipIf(fixtures.pa is None, "resume integration requires PyArrow")
class EfficientResumeTests(unittest.TestCase):
    def setUp(self):
        self.job = fixtures.DataContractTests()
        self.job.setUp()
        self.addCleanup(self.job.doCleanups)
        self.job.config = replace(self.job.config, max_new_tokens=4096, context_window=10000)

    def test_resume_exhausted_mixed_policy_failure_keeps_third_text_without_fourth_attempt(self):
        job = self.job
        field = job.table.schema.get_field_index("teacher_response")
        job.table = job.table.set_column(field, job.table.schema.field(field),
            fixtures.pa.array(["Original answer a.", " ".join(f"word{i}" for i in range(131))]))
        fixtures.pq.write_table(job.table, job.source)
        def legacy(row, index, attempt):
            if index == 0:
                return tp.GeneratedResponse("A completed legacy answer.", "stop", 6)
            if attempt == 1:
                return tp.GeneratedResponse("A long repeated legacy fragment.", "length", 4096)
            raise RuntimeError("legacy interrupted")
        with self.assertRaisesRegex(RuntimeError, "legacy interrupted"):
            job.run_job(factory=job.scripted_factory(legacy, []))
        job.config = replace(job.config, generation_policy="efficient-v1")
        last_text = "The number of games has been increasing. " * 5
        def efficient(row, index, attempt):
            if attempt == 2:
                return tp.GeneratedResponse("The echoed answer </source_answer>", "stop", 146)
            return tp.GeneratedResponse(last_text, "length", 390)
        with self.assertRaisesRegex(RuntimeError, "exhausted"):
            job.run_job(resume=True, factory=job.scripted_factory(efficient, []))
        checkpoint = job.output.with_suffix(".parquet.progress.jsonl")
        previous = checkpoint.read_bytes()
        job.config = replace(job.config, on_failure="keep-last")
        original_publish = up.publish_new_file
        def interrupt_after_audit(temporary, destination):
            if Path(destination) == job.output.resolve():
                raise RuntimeError("interrupt after audit")
            return original_publish(temporary, destination)
        with patch.object(up, "publish_new_file", side_effect=interrupt_after_audit), self.assertRaisesRegex(RuntimeError, "interrupt after audit"):
            job.run_job(resume=True, factory=lambda: self.fail("no fourth attempt or regeneration"))
        after_policy = checkpoint.read_bytes()
        self.assertTrue(after_policy.startswith(previous))
        entries = [json.loads(line) for line in after_policy.decode("utf-8").splitlines()]
        self.assertEqual([entry["attempt"] for entry in entries if entry.get("row_index") == 1], [1, 2, 3])
        self.assertEqual(sum(entry["kind"] == "resume_policy" for entry in entries), 1)
        report = job.run_job(resume=True, factory=lambda: self.fail("saved disposition must replay"))
        self.assertEqual(checkpoint.read_bytes(), after_policy)
        self.assertEqual(fixtures.pq.read_table(job.output)["teacher_response"].to_pylist(), ["A completed legacy answer.", last_text])
        self.assertEqual(report["status_counts"], {"ok": 1, "abnormal": 1})
        self.assertEqual(report["abnormal_kept_count"], 1)
        self.assertEqual(report["resumed_abnormal_kept_rows"], [1])
        self.assertEqual(report["abnormal_kept_reasons"], {"length_limit": 1})
        self.assertEqual(report["abnormal_kept_records"][0]["output_tokens"], 390)
        self.assertEqual(report["attempt_policy_counts"], {"legacy": 2, "efficient-v1": 2})

    def test_retained_last_failure_cannot_bypass_audit_or_change_generation(self):
        job = self.job
        job.config = replace(job.config, generation_policy="efficient-v1")
        with self.assertRaisesRegex(RuntimeError, "exhausted"):
            job.run_job(candidate=tp.GeneratedResponse("A truncated candidate.", "length", 256))
        checkpoint = job.output.with_suffix(".parquet.progress.jsonl")
        previous = checkpoint.read_bytes()
        job.config = replace(job.config, on_failure="keep-last", temperature=.7)
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            job.run_job(resume=True, factory=lambda: self.fail("changed sampling"))
        self.assertEqual(checkpoint.read_bytes(), previous)
        job.config = replace(job.config, temperature=1.0)
        entries = [json.loads(line) for line in previous.decode("utf-8").splitlines()]
        entries[-1]["candidate"] = "A tampered saved candidate."
        corrupted = "".join(up.canonical_json(entry) + "\n" for entry in entries).encode("utf-8")
        checkpoint.write_bytes(corrupted)
        with self.assertRaisesRegex(ValueError, "invalid accepted"):
            job.run_job(resume=True, factory=lambda: self.fail("tampered failure"))
        self.assertEqual(checkpoint.read_bytes(), corrupted)

    def test_legacy_checkpoint_retains_completed_rows_and_resumes_twice_after_upgrade(self):
        job = self.job
        old_answer = "An existing answer. You are an AI assistant."
        def initial(row, index, attempt):
            if index == 0:
                return tp.GeneratedResponse(old_answer, "stop", 300)
            if attempt == 1:
                return tp.GeneratedResponse(row["source"], "stop", 5)
            raise RuntimeError("legacy interruption")
        with self.assertRaisesRegex(RuntimeError, "legacy interruption"):
            job.run_job(factory=job.scripted_factory(initial, []))
        checkpoint = job.output.with_suffix(".parquet.progress.jsonl")
        entries = [json.loads(line) for line in checkpoint.read_text(encoding="utf-8").splitlines()]
        for entry in entries:
            entry.pop("generation_config", None)  # Real old checkpoints have no per-row configuration.
        checkpoint.write_text("".join(up.canonical_json(entry) + "\n" for entry in entries), encoding="utf-8")
        job.config = replace(job.config, generation_policy="efficient-v1")
        calls = []
        def interrupted_upgrade(row, index, attempt):
            if attempt == 2:
                return tp.GeneratedResponse(row["source"], "stop", 5)
            raise RuntimeError("efficient interruption")
        with self.assertRaisesRegex(RuntimeError, "efficient interruption"):
            job.run_job(resume=True, factory=job.scripted_factory(interrupted_upgrade, calls))
        self.assertEqual([call[:2] for call in calls], [(1, 2), (1, 3)])
        saved = [json.loads(line) for line in checkpoint.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(sum(entry["kind"] == "generation_policy" for entry in saved), 1)
        self.assertEqual(saved[-1]["attempt"], 2)
        calls = []
        report = job.run_job(resume=True, factory=job.scripted_factory(
            lambda row, index, attempt: tp.GeneratedResponse("A newly revised answer.", "stop", 6), calls))
        self.assertEqual(calls, [(1, 3, up.generation_seed(42, 1, 3))])
        self.assertEqual(fixtures.pq.read_table(job.output)["teacher_response"].to_pylist(), [old_answer, "A newly revised answer."])
        self.assertTrue(report["mixed_generation_policies"])
        phases = {phase["config"].get("generation_policy", "legacy"): phase for phase in report["generation_phases"]}
        self.assertEqual(phases["legacy"]["row_indices"], [0])
        self.assertEqual(phases["efficient-v1"]["row_indices"], [1])
        self.assertEqual(report["attempt_policy_counts"], {"legacy": 2, "efficient-v1": 2})
        self.assertEqual(report["rejected_generation_attempts"], 2)

    def test_policy_upgrade_rejects_changes_to_sampling_and_rejects_downgrade(self):
        job = self.job
        with patch.object(up, "publish_new_file", side_effect=RuntimeError("stop")), self.assertRaises(RuntimeError):
            job.run_job()
        checkpoint = job.output.with_suffix(".parquet.progress.jsonl")
        old = json.loads(checkpoint.read_text(encoding="utf-8").splitlines()[0])
        def updated(**values):
            doc = {**old, "config": {**old["config"], **values}}
            doc.pop("fingerprint")
            doc["fingerprint"] = up.text_sha256(up.canonical_json(doc))
            return doc
        efficient = updated(generation_policy="efficient-v1")
        tp.validate_resume_metadata(old, efficient)
        for change in ({"temperature": .7}, {"seed": 99}, {"dtype": "bfloat16"}, {"max_new_tokens": 512}):
            with self.subTest(change=change), self.assertRaisesRegex(ValueError, "fingerprint"):
                tp.validate_resume_metadata(old, updated(generation_policy="efficient-v1", **change))
        with self.assertRaises(ValueError):
            tp.validate_resume_metadata(efficient, old)

    def test_efficient_audit_only_publication_recovers_without_regeneration(self):
        job = self.job
        job.config = replace(job.config, generation_policy="efficient-v1")
        original_publish = up.publish_new_file
        def publish(temporary, destination):
            if Path(destination) == job.output.resolve():
                raise RuntimeError("interrupt after audit")
            return original_publish(temporary, destination)
        with patch.object(up, "publish_new_file", side_effect=publish), self.assertRaisesRegex(RuntimeError, "interrupt after audit"):
            job.run_job()
        audit = job.output.with_suffix(".parquet.audit.json")
        saved = audit.read_bytes()
        result = job.run_job(resume=True, factory=lambda: self.fail("completed efficient rows must not regenerate"))
        self.assertEqual(audit.read_bytes(), saved)
        self.assertFalse(result["mixed_generation_policies"])
        self.assertEqual(result["generation_phases"][0]["row_indices"], [0, 1])


if __name__ == "__main__":
    unittest.main()
