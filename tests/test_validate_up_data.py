"""CPU-only checks that only audited exhausted UP failures may be dropped."""

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from baseline_acl.validate_up_data import file_sha256, validate_tables

try:
    import pyarrow as pa
    import pyarrow.parquet as pq
except ImportError:
    pa = pq = None


@unittest.skipUnless(pa is not None, "UP dataset validation tests require pyarrow; no model or training is loaded")
class TestUPDropValidation(unittest.TestCase):
    def setUp(self):
        self.schema = pa.schema([
            ("id", pa.int64()), ("content", pa.string()),
            ("teacher_response", pa.string()), ("category", pa.string()),
        ], metadata={b"huggingface": b"preserve this metadata"})
        self.original = self.table([11, 12, 13, 14], [f"Original answer {i}." for i in range(4)])
        self.retained = [0, 2, 3]
        self.up = self.original.take(self.retained).set_column(
            2, self.schema.field(2), pa.array(["Rewritten one.", "Rewritten three.", "Rewritten four."]))
        self.validation = self.table([99], ["Original held-out answer."])
        self.audit = {
            "complete": True, "method": "ordinary_untargeted_dipper_paraphrasing",
            "metadata": {"input": {"rows": 4}, "config": {"on_failure": "drop", "max_attempts": 3}},
            "source_rows": 4, "processed_rows": 4, "rows": 3, "dropped_count": 1,
            "dropped_rows": [1], "dropped_ids": [12], "status_counts": {"ok": 3, "dropped": 1},
            "dropped_records": [{"row_index": 1, "id": 12, "attempt": 3,
                                 "issues": ["empty_output", "full_response_empty_output"],
                                 "source_sha256": hashlib.sha256(b"Original answer 1.").hexdigest()}],
        }

    def table(self, ids, answers):
        return pa.Table.from_pydict({
            "id": ids, "content": [f"Prompt {i}" for i in ids],
            "teacher_response": answers, "category": ["test"] * len(ids),
        }, schema=self.schema)

    def validate(self, up=None, audit=None):
        return validate_tables(self.original, self.up if up is None else up,
                               self.validation, drop_evidence=self.audit if audit is None else audit)

    def test_exhausted_drop_subset_is_valid_and_counts_retained_rows(self):
        summary = self.validate()
        self.assertEqual(summary, {"train_rows": 3, "source_rows": 4, "dropped_rows": 1,
                                   "validation_rows": 1, "changed_response_rows": 3})

    def test_full_row_data_needs_no_drop_audit(self):
        full = self.original.set_column(2, self.schema.field(2), pa.array(["Changed."] * 4))
        self.assertEqual(validate_tables(self.original, full, self.validation)["train_rows"], 4)

    def test_unaudited_partial_and_smoke_output_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "partial"):
            validate_tables(self.original, self.up, self.validation)

    def test_retained_rows_must_preserve_order_and_protected_columns(self):
        reordered = self.up.take([2, 0, 1])
        changed_prompt = self.up.set_column(1, self.schema.field(1), pa.array(["Wrong", "Prompt 13", "Prompt 14"]))
        changed_category = self.up.set_column(3, self.schema.field(3), pa.array(["wrong"] * 3))
        changed_metadata = self.up.replace_schema_metadata({b"huggingface": b"changed"})
        for table in [reordered, changed_prompt, changed_category, changed_metadata]:
            with self.subTest(table=table.to_pydict()):
                with self.assertRaises(ValueError):
                    self.validate(up=table)

    def test_missing_forged_or_unsorted_drop_ids_and_indices_are_rejected(self):
        for updates in [
            {"dropped_ids": None}, {"dropped_ids": [13]}, {"dropped_ids": [True]},
            {"dropped_rows": [0]}, {"dropped_rows": [1, 1]}, {"dropped_rows": [True]},
            {"dropped_rows": [-1]}, {"dropped_rows": [4]},
        ]:
            with self.subTest(updates=updates):
                audit = copy.deepcopy(self.audit)
                audit.update(updates)
                with self.assertRaises(ValueError):
                    self.validate(audit=audit)

    def test_incomplete_wrong_method_or_counts_are_rejected(self):
        for updates in [
            {"complete": False}, {"complete": 1}, {"method": "targeted_student_paraphrasing"},
            {"processed_rows": 3}, {"source_rows": 3}, {"rows": 4}, {"dropped_count": True},
            {"status_counts": {"ok": 3}}, {"status_counts": {"ok": 2, "dropped": 1, "pending": 1}},
        ]:
            with self.subTest(updates=updates):
                audit = copy.deepcopy(self.audit)
                audit.update(updates)
                with self.assertRaises(ValueError):
                    self.validate(audit=audit)

    def test_non_drop_policy_invalid_cap_and_source_count_are_rejected(self):
        for config in [{"on_failure": "error", "max_attempts": 3},
                       {"on_failure": "drop", "max_attempts": True},
                       {"on_failure": "drop", "max_attempts": 0}]:
            with self.subTest(config=config):
                audit = copy.deepcopy(self.audit)
                audit["metadata"]["config"] = config
                with self.assertRaises(ValueError):
                    self.validate(audit=audit)
        audit = copy.deepcopy(self.audit)
        audit["metadata"]["input"]["rows"] = 3
        with self.assertRaises(ValueError):
            self.validate(audit=audit)

    def test_drop_record_requires_terminal_attempt_issue_id_and_source_hash(self):
        for updates in [{"attempt": 2}, {"attempt": True}, {"id": 14}, {"row_index": 2},
                        {"issues": []}, {"issues": [""]}, {"issues": "empty_output"},
                        {"source_sha256": "wrong"}, {"issues": ["full_response_exceeds_encoder_budget"]}]:
            with self.subTest(updates=updates):
                audit = copy.deepcopy(self.audit)
                audit["dropped_records"][0].update(updates)
                with self.assertRaises(ValueError):
                    self.validate(audit=audit)
        audit = copy.deepcopy(self.audit)
        audit["dropped_records"] = []
        with self.assertRaises(ValueError):
            self.validate(audit=audit)

    def test_empty_response_empty_dataset_and_validation_overlap_are_rejected(self):
        for bad in [self.up.set_column(2, self.schema.field(2), pa.array(["", "Valid.", "Valid."])), self.up.slice(0, 0)]:
            with self.assertRaises(ValueError):
                self.validate(up=bad)
        with self.assertRaisesRegex(ValueError, "overlap"):
            validate_tables(self.original, self.up, self.original.slice(1, 1), drop_evidence=self.audit)

    def run_cli(self, root, audit=None, override=False):
        source, up, validation = [root / name for name in ["source.parquet", "up.parquet", "validation.parquet"]]
        for table, path in [(self.original, source), (self.up, up), (self.validation, validation)]:
            pq.write_table(table, path)
        extra = []
        if audit is not None:
            audit = copy.deepcopy(audit)
            audit["metadata"]["input"].setdefault("sha256", file_sha256(source))
            audit.setdefault("output_sha256", file_sha256(up))
            audit_path = root / "custom.audit.json" if override else Path(str(up) + ".audit.json")
            audit_path.write_text(json.dumps(audit), encoding="utf-8")
            if override:
                extra = ["--audit_file", str(audit_path)]
        return subprocess.run([
            sys.executable, "-m", "baseline_acl.validate_up_data", "--original_train_file", str(source),
            "--up_train_file", str(up), "--val_file", str(validation), *extra,
        ], text=True, capture_output=True, timeout=20)

    def test_cli_discovers_default_drop_audit_and_accepts_explicit_override(self):
        for override in [False, True]:
            with self.subTest(override=override), tempfile.TemporaryDirectory() as directory:
                result = self.run_cli(Path(directory), self.audit, override=override)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("3 retained training rows from 4 source rows", result.stdout)
                self.assertIn("1 audited exhausted failures dropped", result.stdout)

    def test_cli_rejects_missing_drop_audit_or_file_hash_mismatch(self):
        variants = [None, "source", "output"]
        for variant in variants:
            with self.subTest(variant=variant), tempfile.TemporaryDirectory() as directory:
                audit = None if variant is None else copy.deepcopy(self.audit)
                if variant == "source":
                    audit["metadata"]["input"]["sha256"] = "wrong"
                elif variant == "output":
                    audit["output_sha256"] = "wrong"
                result = self.run_cli(Path(directory), audit)
                self.assertEqual(result.returncode, 2)
                self.assertIn("audit", result.stderr)

    def test_real_up_writer_drop_audit_passes_training_validator(self):
        from baseline_acl.paraphrase_up import GenerationConfig, GeneratedResponse, run_paraphrasing
        from tests.test_paraphrase_up import FakeGenerator, FakeTokenizer, one_sentence

        def full_schema(table):
            for name, kind, value in [("grounded", pa.bool_(), False), ("flaw", pa.string(), "normal"),
                                      ("agreement", pa.bool_(), True)]:
                table = table.append_column(name, pa.array([value] * table.num_rows, type=kind))
            return table

        config = GenerationConfig(max_attempts=3, on_failure="drop")
        generator = FakeGenerator({1: GeneratedResponse("", "stop", 2)})
        generator.config = config
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, output, held_out = [root / name for name in ["kgw_train.parquet", "up_train.parquet", "validation.parquet"]]
            pq.write_table(full_schema(self.original), source)
            pq.write_table(full_schema(self.validation), held_out)
            report = run_paraphrasing(source, output, config, FakeTokenizer(), lambda: generator,
                                     {"model": "CPU fake"}, sentence_splitter=one_sentence)
            self.assertEqual(report["dropped_rows"], [1])
            result = subprocess.run([
                sys.executable, "-m", "baseline_acl.validate_up_data", "--original_train_file", str(source),
                "--up_train_file", str(output), "--val_file", str(held_out),
            ], text=True, capture_output=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("3 retained training rows from 4 source rows", result.stdout)


if __name__ == "__main__":
    unittest.main()
