"""CPU checks for paired discriminator/SFT data and its training wrapper."""

import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("split_data", ROOT / "tools/prepare_split_warmup_data.py")
split_data = importlib.util.module_from_spec(spec)
spec.loader.exec_module(split_data)
BASH = shutil.which("bash")
if os.name == "nt":
    for candidate in (Path("D:/software/Git/bin/bash.exe"), Path("C:/Program Files/Git/bin/bash.exe")):
        if candidate.is_file():
            BASH = str(candidate)
            break
try:
    import pyarrow as pa
    import pyarrow.parquet as pq
except ImportError:
    pa = pq = None


def rows():
    return [
        {"id": "a", "content": "Prompt A", "teacher_response": "KGW A"},
        {"id": "b", "content": "Prompt B", "teacher_response": "KGW B"},
    ]


class PairingTests(unittest.TestCase):
    def test_id_join_handles_different_order(self):
        para = rows()[::-1]
        for row in para:
            row["teacher_response"] = f"Para {row['id']}"
        self.assertEqual(split_data.pair_sft_responses(rows(), para), ["Para a", "Para b"])

    def test_duplicate_missing_extra_and_mismatched_prompts_rejected(self):
        invalid = [rows()[:1], rows() + [rows()[0]], [*rows(), {"id": "c", "content": "C", "teacher_response": "C"}]]
        mismatch = rows()
        mismatch[0]["content"] = "Wrong prompt"
        invalid.append(mismatch)
        for para in invalid:
            with self.subTest(para=para), self.assertRaises(ValueError):
                split_data.pair_sft_responses(rows(), para)

    def test_empty_answers_and_null_ids_rejected(self):
        for key, value in [("id", None), ("teacher_response", None), ("teacher_response", " ")]:
            para = rows()
            para[0][key] = value
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                split_data.pair_sft_responses(rows(), para)


@unittest.skipUnless(pa, "Parquet integration requires pyarrow")
class ParquetTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.original, self.para, self.output, self.val = [self.root / f"{n}.parquet" for n in ("original", "para", "output", "val")]
        pq.write_table(pa.Table.from_pylist(rows()).replace_schema_metadata({b"source": b"keep"}), self.original)
        para = rows()[::-1]
        for row in para:
            row["teacher_response"] = f"Para {row['id']}"
        pq.write_table(pa.Table.from_pylist(para), self.para)
        pq.write_table(pa.Table.from_pylist([{"id": "test", "content": "Test", "teacher_response": "Test"}]), self.val)

    def test_preserves_original_targets_and_pairs_sft_without_changing_inputs(self):
        original_hash, para_hash = split_data.sha256(self.original), split_data.sha256(self.para)
        split_data.prepare(self.original, self.para, self.output, self.val)
        table = pq.read_table(self.output)
        self.assertEqual(table["teacher_response"].to_pylist(), ["KGW A", "KGW B"])
        self.assertEqual(table["sft_response"].to_pylist(), ["Para a", "Para b"])
        self.assertEqual(table.schema.metadata[b"source"], b"keep")
        self.assertEqual((split_data.sha256(self.original), split_data.sha256(self.para)), (original_hash, para_hash))
        split_data.prepare(self.original, self.para, self.output, self.val)

    def test_stale_output_is_rejected(self):
        split_data.prepare(self.original, self.para, self.output)
        pq.write_table(pa.Table.from_pylist(rows()), self.para)
        with self.assertRaisesRegex(ValueError, "Existing output differs"):
            split_data.prepare(self.original, self.para, self.output)

    def test_input_overwrite_and_validation_overlap_rejected(self):
        with self.assertRaisesRegex(ValueError, "Output must differ"):
            split_data.prepare(self.original, self.para, self.original)
        with self.assertRaisesRegex(ValueError, "Validation overlaps"):
            split_data.prepare(self.original, self.para, self.output, self.original)


@unittest.skipUnless(BASH, "Shell checks require Git Bash/Bash")
class WrapperTests(unittest.TestCase):
    def test_wrapper_forwards_separate_stage_files_to_parent(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ("scripts/train", "tools", "verl/utils/dataset", "verl/workers/actor", "bin"):
                (root / name).mkdir(parents=True, exist_ok=True)
            wrapper_name = "run_full_gad_kgwD_paraSFT_paraGAD_optimized.sh"
            shutil.copyfile(ROOT / "scripts/train" / wrapper_name, root / "scripts/train" / wrapper_name)
            (root / "verl/utils/dataset/rl_dataset.py").write_text("build_sft_response_tensors", encoding="utf-8")
            (root / "verl/workers/actor/dp_actor.py").write_text("select_warmup_sft_targets", encoding="utf-8")
            (root / "scripts/train/run_full_gad_optimized.sh").write_text(
                '#!/bin/bash\n# --warmup_train_file\nprintf "%s\\n" "$@"\n', encoding="utf-8", newline="\n")
            python = root / "bin/python3"
            python.write_text('#!/bin/bash\nprintf "PREPARE:%s\\n" "$@"\n', encoding="utf-8", newline="\n")
            python.chmod(0o755)
            env = os.environ.copy()
            env.update({"PATH": str(root / "bin") + os.pathsep + env.get("PATH", ""), "CUDA_VISIBLE_DEVICES": "4,7"})
            result = subprocess.run([BASH, f"scripts/train/{wrapper_name}", "--dry_run"], cwd=root, env=env, text=True, capture_output=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            lines = result.stdout.splitlines()
            for key, value in [
                ("--warmup_train_file", "data/dolly15k_qwen2_5_14b_kgw_gamma0.5_delta3_kgwD_paraSFT_newtrain.parquet"),
                ("--gad_train_file", "data/dolly15k_qwen2_5_14b_kgw_gamma0.5_delta3_up_dipper_newtrain.parquet"),
                ("--logger", "swanlab"),
            ]:
                self.assertEqual(lines[lines.index(key) + 1], value)
            self.assertIn("--dry_run", lines)
            self.assertIn("PREPARE:--original_train_file", lines)


if __name__ == "__main__":
    unittest.main()
