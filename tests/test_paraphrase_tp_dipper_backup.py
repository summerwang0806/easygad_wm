"""TP entrypoint/data tests without loading models or contacting a server."""

from dataclasses import asdict
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from baseline_acl import paraphrase_tp_dipper_backup as tp
from baseline_acl import paraphrase_up as up

try:
    import pyarrow as pa
    import pyarrow.parquet as pq
except ImportError:
    pa = pq = None


class Tokenizer:
    def encode(self, text, add_special_tokens=False):
        return text.split() + (["EOS"] if add_special_tokens else [])


class Generator:
    def __init__(self, config):
        self.config = config

    def generate(self, prepared_rows, indices, attempts):
        return [up.paraphrase_windows(row, lambda prompt, seed: up.GeneratedResponse(
            "A targeted revised answer.", "stop", 5), Tokenizer(), self.config, index, attempt)
                for row, index, attempt in zip(prepared_rows, indices, attempts, strict=True)]


class EntryTests(unittest.TestCase):
    def test_projection_defaults_and_full_projection_options(self):
        base = ["--input", "train.parquet", "--rules", "rules.json", "--rule-tokenizer", "qwen", "--inspect"]
        args = tp.parse_args(base)
        self.assertEqual(args.inverse_strength, 2.5)
        self.assertEqual(args.candidate_top_k, 128)
        self.assertEqual(args.projection_context_tokens, 64)
        full = tp.parse_args([*base, "--candidate-top-k", "0", "--projection-context-tokens", "0"])
        self.assertEqual((full.candidate_top_k, full.projection_context_tokens), (0, 0))

    def test_rules_and_held_out_source_are_protected(self):
        for argv in (["--input", "test.parquet", "--rules", "rules.json"],
                     ["--input", "train.parquet", "--rules", "train.parquet"]):
            args = tp.parse_args([*argv, "--rule-tokenizer", "qwen", "--inspect"])
            with self.assertRaises(ValueError):
                tp.validate_attack_paths(args)
        args = tp.parse_args(["--input", "train.parquet", "--rules", "rules.json",
                              "--rule-tokenizer", "qwen", "--output", "rules.json"])
        with self.assertRaises(ValueError):
            tp.validate_attack_paths(args)

    def test_inspect_never_checks_cuda_or_imports_a_model(self):
        with patch("baseline_acl.paraphrase_tp_dipper_backup.up.inspect_source", return_value={"rows": 1, "input_sha256": "hash"}), \
             patch("baseline_acl.paraphrase_tp_dipper_backup.up.file_sha256", return_value="hash"), \
             patch("baseline_acl.inverse_watermark.RuleTable.load") as loader, \
             patch("baseline_acl.paraphrase_tp_dipper_backup.up.probe_selected_gpus", side_effect=AssertionError("CUDA")), \
             patch("sys.stdout", new_callable=io.StringIO):
            loader.return_value.tokenizer = {"vocab_size": 5}
            loader.return_value.document = {"provenance": {}}
            tp.main(["--input", "train.parquet", "--rules", "rules.json", "--rule-tokenizer", "qwen", "--inspect"])

    def test_spawn_factory_has_stable_serializable_configuration(self):
        worker = tp.TPWorkerFactory("rules.json", "qwen", 2.5, 128, 64, "a" * 64)
        self.assertEqual(asdict(worker)["candidate_top_k"], 128)

    def test_workers_reject_rule_drift_and_loading_races(self):
        with patch("baseline_acl.paraphrase_tp_dipper_backup.up.file_sha256", return_value="new"):
            with self.assertRaisesRegex(ValueError, "audited version"):
                tp.load_bound_rules(Path("rules.json"), "old")
        with patch("baseline_acl.paraphrase_tp_dipper_backup.up.file_sha256", side_effect=["old", "new"]), \
             patch("baseline_acl.inverse_watermark.RuleTable.load"):
            with self.assertRaisesRegex(ValueError, "while loading"):
                tp.load_bound_rules(Path("rules.json"), "old")

    def test_rules_are_bound_to_original_training_corpus_when_provenance_is_available(self):
        from types import SimpleNamespace
        rules = SimpleNamespace(document={"provenance": {"input": {"sha256": "original"}}})
        tp.validate_rule_source(rules, "original")
        with self.assertRaisesRegex(ValueError, "training corpus"):
            tp.validate_rule_source(rules, "different")


@unittest.skipIf(pa is None, "pyarrow is required for real Parquet checks")
class DataContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "train.parquet"
        self.output = self.root / "tp.parquet"
        table = pa.table({"id": ["a", "b"], "content": ["question a", "question b"],
                          "teacher_response": ["Original answer a.", "Original answer b."],
                          "category": ["qa", "qa"], "grounded": [True, False],
                          "flaw": [None, None], "agreement": [None, None]})
        self.table = table.replace_schema_metadata({b"source": b"strict-source"})
        pq.write_table(self.table, self.source)
        self.config = up.GenerationConfig()
        self.identity = {"model": "fake-local", "attack": {
            "method": "targeted_dipper_paraphrasing", "rules_sha256": "a" * 64,
            "inverse_strength": 2.5, "projection": {"candidate_top_k": 128}}}

    def run_job(self, **kwargs):
        return up.run_paraphrasing(self.source, self.output, self.config, Tokenizer(),
                                  lambda: Generator(self.config), self.identity,
                                  sentence_splitter=lambda text: [text], **kwargs)

    def test_tp_replaces_only_response_and_publishes_method_and_hashes(self):
        report = self.run_job()
        result = pq.read_table(self.output)
        self.assertTrue(result.schema.equals(self.table.schema, check_metadata=True))
        for name in self.table.column_names:
            if name != "teacher_response":
                self.assertTrue(result[name].equals(self.table[name]))
        self.assertEqual(report["method"], "targeted_dipper_paraphrasing")
        self.assertEqual(report["input_sha256"], up.file_sha256(self.source))
        self.assertEqual(report["output_sha256"], up.file_sha256(self.output))
        self.assertEqual(report["changed_teacher_responses"], 2)
        self.assertEqual(report["metadata"]["model"]["attack"], self.identity["attack"])

    def test_resume_rejects_different_rule_hash_before_generation(self):
        with patch("baseline_acl.paraphrase_up.publish_new_file", side_effect=RuntimeError("interrupt publication")):
            with self.assertRaises(RuntimeError):
                self.run_job()
        self.identity["attack"]["rules_sha256"] = "b" * 64
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            self.run_job(resume=True)
        self.assertFalse(self.output.exists())

    def test_ordinary_up_keeps_its_original_audit_contract(self):
        self.identity.pop("attack")
        report = self.run_job()
        self.assertEqual(report["method"], "ordinary_untargeted_dipper_paraphrasing")
        self.assertNotIn("attack", report)
        self.assertNotIn("input_sha256", report)


if __name__ == "__main__":
    unittest.main()
