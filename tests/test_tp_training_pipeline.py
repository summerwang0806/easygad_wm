"""CPU-only TP training preflight tests; never load models or launch training."""

import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PIPELINE = PROJECT_ROOT / "baseline_acl" / "run_tp_gad_pipeline.sh"
AUDIT_SCRIPT = PIPELINE.read_text(encoding="utf-8").split("<<'TP_AUDIT_PY'\n", 1)[1].split("\nTP_AUDIT_PY", 1)[0]
BACKUP_PIPELINE = PROJECT_ROOT / "baseline_acl" / "run_tp_gad_pipeline_dipper_backup.sh"
BACKUP_AUDIT_SCRIPT = BACKUP_PIPELINE.read_text(encoding="utf-8").split("<<'TP_AUDIT_PY'\n", 1)[1].split("\nTP_AUDIT_PY", 1)[0]

try:
    import pyarrow as pa
    import pyarrow.parquet as pq
except ImportError:
    pa = pq = None


def find_bash():
    if os.name != "nt":
        return shutil.which("bash")
    # Avoid Windows' WSL launchers; these integration tests use only local Git Bash.
    candidates = [
        Path("C:/Program Files/Git/bin/bash.exe"),
        Path("C:/Program Files/Git/usr/bin/bash.exe"),
        Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/usr/bin/bash.exe",
    ]
    found = shutil.which("bash.exe")
    if found and "git" in found.lower():
        candidates.insert(0, Path(found))
    return next((str(path) for path in candidates if path.is_file()), None)


BASH = find_bash()


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class TestTPAuditPreflight(unittest.TestCase):
    """Exercise the exact embedded audit gate even when Bash/pyarrow are absent."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / "source.parquet"
        self.output = self.root / "target.parquet"
        self.source.write_bytes(b"original KGW source")
        self.output.write_bytes(b"targeted paraphrasing output")
        self.audit = self.output.with_suffix(self.output.suffix + ".audit.json")
        self.metadata = {
            "complete": True,
            "method": "targeted_student_paraphrasing",
            "attack": {"method": "targeted_student_paraphrasing", "cross_tokenizer": False,
                       "projection": None, "paraphraser_model_role": "original_student_O",
                       "tokenizer_identity_checked": True},
            "changed_teacher_responses": 2,
            "input_sha256": sha256(self.source),
            "output_sha256": sha256(self.output),
        }

    def run_gate(self, metadata=None, script=AUDIT_SCRIPT):
        if metadata is not None:
            self.audit.write_text(json.dumps(metadata), encoding="utf-8")
        return subprocess.run(
            [sys.executable, "-c", script, str(self.source), str(self.output)],
            text=True, capture_output=True, timeout=20,
        )

    def test_complete_targeted_output_passes(self):
        result = self.run_gate(self.metadata)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("verified input/output SHA-256", result.stdout)

    def test_missing_audit_rejected(self):
        result = self.run_gate()
        self.assertEqual(result.returncode, 2)
        self.assertIn("TP audit preflight failed", result.stderr)

    def test_ordinary_up_is_not_tp(self):
        self.metadata["method"] = "dipper_paraphrasing"
        result = self.run_gate(self.metadata)
        self.assertEqual(result.returncode, 2)
        self.assertIn("ordinary UP and Dipper backup data", result.stderr)

    def test_dipper_backup_is_not_formal_student_tp(self):
        self.metadata["method"] = "targeted_dipper_paraphrasing"
        result = self.run_gate(self.metadata)
        self.assertEqual(result.returncode, 2)
        self.assertIn("Dipper backup data", result.stderr)

    def test_backup_gate_retains_dipper_contract_and_rejects_formal_student_data(self):
        student = self.run_gate(self.metadata, script=BACKUP_AUDIT_SCRIPT)
        self.assertEqual(student.returncode, 2)
        self.assertIn("targeted_dipper_paraphrasing", student.stderr)
        self.metadata["method"] = "targeted_dipper_paraphrasing"
        self.metadata["attack"] = {"method": "targeted_dipper_paraphrasing", "projection": {"method": "backup"}}
        dipper = self.run_gate(self.metadata, script=BACKUP_AUDIT_SCRIPT)
        self.assertEqual(dipper.returncode, 0, dipper.stderr)

    def test_missing_or_mismatched_attack_metadata_rejected(self):
        for attack in [None, {}, {"method": "targeted_dipper_paraphrasing"}]:
            with self.subTest(attack=attack):
                self.metadata["attack"] = attack
                result = self.run_gate(self.metadata)
                self.assertEqual(result.returncode, 2)
                self.assertIn("matching student attack metadata", result.stderr)

    def test_projection_or_unverified_tokenizer_rejected(self):
        clean = self.metadata["attack"].copy()
        for field, value, message in [
            ("cross_tokenizer", True, "cross_tokenizer=false"),
            ("cross_tokenizer", 0, "cross_tokenizer=false"),
            ("projection", {}, "projection=null"),
            ("tokenizer_identity_checked", False, "verified tokenizer identity"),
            ("paraphraser_model_role", "trained_student_W", "original_student_O"),
        ]:
            with self.subTest(field=field, value=value):
                self.metadata["attack"] = {**clean, field: value}
                result = self.run_gate(self.metadata)
                self.assertEqual(result.returncode, 2)
                self.assertIn(message, result.stderr)

    def test_incomplete_and_non_boolean_completion_rejected(self):
        for value in [False, 1, "true", None]:
            with self.subTest(complete=value):
                self.metadata["complete"] = value
                result = self.run_gate(self.metadata)
                self.assertEqual(result.returncode, 2)
                self.assertIn("incomplete", result.stderr)

    def test_zero_and_invalid_changed_counts_rejected(self):
        for value in [0, -1, True, "2", 2.0, None]:
            with self.subTest(changed=value):
                self.metadata["changed_teacher_responses"] = value
                result = self.run_gate(self.metadata)
                self.assertEqual(result.returncode, 2)
                self.assertIn("changed_teacher_responses", result.stderr)

    def test_modified_source_rejected(self):
        self.source.write_bytes(b"a different source")
        result = self.run_gate(self.metadata)
        self.assertEqual(result.returncode, 2)
        self.assertIn("input_sha256", result.stderr)

    def test_modified_output_rejected(self):
        self.output.write_bytes(b"a different output")
        result = self.run_gate(self.metadata)
        self.assertEqual(result.returncode, 2)
        self.assertIn("output_sha256", result.stderr)

    def test_missing_hash_rejected(self):
        del self.metadata["output_sha256"]
        result = self.run_gate(self.metadata)
        self.assertEqual(result.returncode, 2)
        self.assertIn("output_sha256", result.stderr)

    def test_invalid_json_and_non_object_rejected(self):
        for value in ["{broken json", "[]"]:
            with self.subTest(payload=value):
                self.audit.write_text(value, encoding="utf-8")
                result = self.run_gate()
                self.assertEqual(result.returncode, 2)
                self.assertIn("TP audit preflight failed", result.stderr)


@unittest.skipUnless(pa, "Student TP writer integration requires pyarrow")
class TestTPWriterPreflight(unittest.TestCase):
    def test_actual_student_writer_audit_passes_exact_training_gate(self):
        from baseline_acl import paraphrase_tp as tp

        class Tokenizer:
            def encode(self, text, add_special_tokens=False):
                return list(range(len(text.split()))) + ([100] if add_special_tokens else [])

        tokenizer = Tokenizer()
        config = tp.GenerationConfig(max_input_tokens=500, max_new_tokens=100, context_window=1000)

        class Generator:
            def generate(self, rows, indices, attempts):
                return [tp.generate_response(
                    row, lambda prompt, seed: tp.GeneratedResponse("A fully revised factual answer.", "stop", 7),
                    tokenizer, config, index, attempt,
                ) for row, index, attempt in zip(rows, indices, attempts, strict=True)]

        with tempfile.TemporaryDirectory() as directory:
            source, output = (Path(directory) / name for name in ("train.parquet", "tp.parquet"))
            table = pa.table({
                "id": ["a", "b"], "content": ["Question a", "Question b"],
                "teacher_response": ["Original answer a.", "Original answer b."],
                "category": ["qa", "qa"], "grounded": [True, False],
                "flaw": [None, None], "agreement": [None, None],
            }).replace_schema_metadata({b"source": b"writer-to-training-gate"})
            pq.write_table(table, source)
            rules = SimpleNamespace(tokenizer={"fingerprint": "mock-student"},
                                    document={"provenance": {"input": {"sha256": sha256(source)}}})
            attack = tp.attack_identity(SimpleNamespace(inverse_strength=2.5), rules, "a" * 64)
            report = tp.run_paraphrasing(source, output, config, tokenizer, Generator,
                                        {"model": "mock-original-student", "attack": attack})
            self.assertEqual(report["changed_teacher_responses"], table.num_rows)
            self.assertTrue(pq.read_table(output).schema.equals(table.schema, check_metadata=True))
            result = subprocess.run(
                [sys.executable, "-c", AUDIT_SCRIPT, str(source), str(output)],
                text=True, capture_output=True, timeout=20,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("verified input/output SHA-256", result.stdout)


@unittest.skipUnless(BASH, "Local Git Bash/Bash is unavailable; shell integration was not run")
class TestTPShellArguments(unittest.TestCase):
    def run_pipeline(self, *args, env=None):
        environment = os.environ.copy()
        environment.pop("CUDA_VISIBLE_DEVICES", None)
        environment.update(env or {})
        return subprocess.run(
            [BASH, str(PIPELINE).replace("\\", "/"), *args],
            env=environment, text=True, capture_output=True, timeout=20,
        )

    def test_bash_syntax(self):
        for path in [PIPELINE, BACKUP_PIPELINE, *sorted((PROJECT_ROOT / "scripts/train").glob("run_full_gad_tp_*_optimized.sh"))]:
            result = subprocess.run([BASH, "-n", str(path).replace("\\", "/")], capture_output=True, text=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_training_requires_explicit_gpu_selection(self):
        result = self.run_pipeline("--branch", "tp_tp")
        self.assertEqual(result.returncode, 2)
        self.assertIn("Set CUDA_VISIBLE_DEVICES explicitly", result.stderr)

    def test_duplicate_and_reserved_stage_options_rejected(self):
        for args, message in [
            (("--branch", "tp_tp", "--dry_run", "--dry_run"), "Duplicate option"),
            (("--branch", "tp_tp", "--gad_train_file", "other.parquet"), "fixed by the branch"),
            (("--branch", "tp_tp", "--warmup_epochs", "2"), "pinned to 1"),
        ]:
            with self.subTest(args=args):
                result = self.run_pipeline(*args)
                self.assertEqual(result.returncode, 2)
                self.assertIn(message, result.stderr)


@unittest.skipUnless(BASH and pa, "Full shell/Parquet integration requires local Git Bash/Bash and pyarrow; no training was run")
class TestTPTrainingBranches(unittest.TestCase):
    """Run copied wrappers against a fake parent in a disposable project tree."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "project with spaces"
        for directory in ["baseline_acl", "scripts/train", "data", "bin", "elsewhere"]:
            (self.root / directory).mkdir(parents=True, exist_ok=True)
        for name in ["run_tp_gad_pipeline.sh", "validate_up_data.py"]:
            shutil.copyfile(PROJECT_ROOT / "baseline_acl" / name, self.root / "baseline_acl" / name)
        for branch in ["tp_tp", "tp_kgw"]:
            name = f"run_full_gad_{branch}_optimized.sh"
            shutil.copyfile(PROJECT_ROOT / "scripts/train" / name, self.root / "scripts/train" / name)
        parent = self.root / "scripts/train/run_full_gad_all_clean_optimized.sh"
        parent.write_text('#!/usr/bin/env bash\nset -euo pipefail\nprintf "%s\\n" "$@" > "$TEST_CAPTURE_FILE"\nprintf "PARENT_EXECUTED\\n"\n', encoding="utf-8")
        python_shim = self.root / "bin/python3"
        python_shim.write_text("#!/usr/bin/env bash\nexec " + shlex.quote(sys.executable.replace("\\", "/")) + ' "$@"\n', encoding="utf-8")
        python_shim.chmod(0o755)
        self.capture = self.root / "parent.args"
        self.source = self.root / "data/source.parquet"
        self.tp = self.root / "data/tp.parquet"
        self.validation = self.root / "data/validation.parquet"
        schema = pa.schema([("id", pa.int64()), ("content", pa.string()), ("teacher_response", pa.string())], metadata={b"huggingface": b"preserve me"})
        for path, ids, answers in [
            (self.source, [1, 2], ["Original answer one.", "Original answer two."]),
            (self.tp, [1, 2], ["Targeted answer one.", "Targeted answer two."]),
            (self.validation, [3], ["Held-out original answer."]),
        ]:
            table = pa.Table.from_pydict({"id": ids, "content": [f"Prompt {i}" for i in ids], "teacher_response": answers}, schema=schema)
            pq.write_table(table, path)
        self.write_audit()

    def write_audit(self, **overrides):
        metadata = {
            "complete": True, "method": "targeted_student_paraphrasing",
            "attack": {"method": "targeted_student_paraphrasing", "cross_tokenizer": False,
                       "projection": None, "paraphraser_model_role": "original_student_O",
                       "tokenizer_identity_checked": True},
            "changed_teacher_responses": 2,
            "input_sha256": sha256(self.source), "output_sha256": sha256(self.tp),
        }
        metadata.update(overrides)
        self.tp.with_suffix(".parquet.audit.json").write_text(json.dumps(metadata), encoding="utf-8")

    def run_branch(self, branch, *extra, gpu=None):
        environment = os.environ.copy()
        environment.pop("CUDA_VISIBLE_DEVICES", None)
        if gpu is not None:
            environment["CUDA_VISIBLE_DEVICES"] = gpu
        environment["TEST_CAPTURE_FILE"] = str(self.capture).replace("\\", "/")
        environment["PATH"] = str(self.root / "bin") + os.pathsep + environment.get("PATH", "")
        entry = self.root / "scripts/train" / f"run_full_gad_{branch}_optimized.sh"
        return subprocess.run([
            BASH, str(entry).replace("\\", "/"),
            "--tp_train_file", "data/tp.parquet", "--kgw_train_file", "data/source.parquet",
            "--val_file", "data/validation.parquet", *extra,
        ], cwd=self.root / "elsewhere", env=environment, capture_output=True, text=True, timeout=30)

    def test_dry_run_validates_from_any_directory_without_starting_parent(self):
        result = self.run_branch("tp_tp", "--dry_run")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("TP audit preflight passed", result.stdout)
        self.assertIn("--warmup_train_file data/tp.parquet", result.stdout)
        self.assertIn("--gad_train_file data/tp.parquet", result.stdout)
        self.assertNotIn("PARENT_EXECUTED", result.stdout)
        self.assertFalse(self.capture.exists())

    def test_both_branches_forward_correct_stage_files_to_fake_parent(self):
        for branch, gad in [("tp_tp", "data/tp.parquet"), ("tp_kgw", "data/source.parquet")]:
            with self.subTest(branch=branch):
                result = self.run_branch(branch, "--model", "models/local", "--exp_name", "test_case", gpu="7,9")
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                args = self.capture.read_text(encoding="utf-8").splitlines()
                for flag, value in [
                    ("--warmup_train_file", "data/tp.parquet"), ("--gad_train_file", gad),
                    ("--warmup_val_file", "data/validation.parquet"), ("--gad_val_file", "data/validation.parquet"),
                    ("--warmup_epochs", "1"), ("--gad_epochs", "1"), ("--nnodes", "1"),
                    ("--exp_name", "test_case"), ("--model", "models/local"),
                ]:
                    self.assertEqual(args[args.index(flag) + 1], value)

    def test_partial_parquet_never_reaches_parent(self):
        pq.write_table(pq.ParquetFile(self.tp).read().slice(0, 1), self.tp)
        self.write_audit(changed_teacher_responses=1)
        result = self.run_branch("tp_tp", "--dry_run")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("partial", result.stderr)
        self.assertFalse(self.capture.exists())

    def test_ordinary_up_audit_never_reaches_parent(self):
        self.write_audit(method="dipper_paraphrasing")
        result = self.run_branch("tp_kgw", "--dry_run")
        self.assertEqual(result.returncode, 2)
        self.assertIn("ordinary UP and Dipper backup data", result.stderr)
        self.assertFalse(self.capture.exists())


if __name__ == "__main__":
    unittest.main()
