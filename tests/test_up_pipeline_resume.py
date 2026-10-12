"""Offline regression tests for UP -> UP/KGW pipeline resume.

Run with ``python tests/test_up_pipeline_resume.py``.
Temporary launcher copies use fake validation, training, and CPU merge tools.
These tests use no model dependencies, GPUs, network, or real experiment files.
"""

import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
BASH = shutil.which("bash")
if os.name == "nt":
    for candidate in (
        Path(r"D:\software\Git\bin\bash.exe"),
        Path(r"C:\Program Files\Git\bin\bash.exe"),
    ):
        if candidate.is_file():
            BASH = str(candidate)
            break

UP_TRAIN = "data/dolly15k_qwen2_5_14b_kgw_up_dipper_train.parquet"
KGW_TRAIN = "data/dolly15k_qwen2_5_14b_kgw_train.parquet"
KGW_VAL = "data/dolly15k_qwen2_5_14b_kgw_test.parquet"


def shell_path(path):
    """Convert a local path for Git Bash without invoking another process."""
    path = Path(path).resolve()
    if os.name == "nt":
        return "/" + path.drive[0].lower() + path.as_posix()[2:]
    return str(path)


PYTHON_STUB = r'''#!/bin/bash
set -eu
mkdir -p "$WM_TEST_ROOT/calls"
counter=0
if [ -f "$WM_TEST_ROOT/counter" ]; then counter=$(< "$WM_TEST_ROOT/counter"); fi
counter=$((counter + 1))
printf '%s' "$counter" > "$WM_TEST_ROOT/counter"
printf '%s\n' "$@" > "$WM_TEST_ROOT/calls/$counter.args"
printf '%s\n' "CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES-}" > "$WM_TEST_ROOT/calls/$counter.env"
if [[ "${1-}" == */baseline_acl/validate_up_data.py ]]; then
    printf 'validator\n' >> "$WM_TEST_ROOT/events.log"
elif [ "${1-}" = "-m" ] && [ "${2-}" = "verl.trainer.main_ppo" ]; then
    stage= work_dir=
    for arg in "$@"; do
        case "$arg" in
            trainer.training_stage=*) stage=${arg#*=} ;;
            trainer.default_local_dir=*) work_dir=${arg#*=} ;;
        esac
    done
    printf 'trainer:%s\n' "$stage" >> "$WM_TEST_ROOT/events.log"
    checkpoint="$work_dir/global_step_5"
    mkdir -p "$checkpoint/actor" "$checkpoint/critic"
    printf '{}' > "$checkpoint/actor/config.json"
    printf '{}' > "$checkpoint/critic/config.json"
    printf 'dummy dataloader state' > "$checkpoint/data.pt"
    printf '5' > "$work_dir/latest_checkpointed_iteration.txt"
    if [ "${WM_FAIL_STAGE-}" = "$stage" ]; then exit 9; fi
elif [ "${1-}" = "scripts/model_merger.py" ] && [ "${2-}" = "merge" ]; then
    local_dir= target_dir= backend=
    shift 2
    while [ $# -gt 0 ]; do
        case "$1" in
            --local_dir) local_dir=$2; shift 2 ;;
            --target_dir) target_dir=$2; shift 2 ;;
            --backend) backend=$2; shift 2 ;;
            *) printf 'Unexpected merger argument\n' >&2; exit 92 ;;
        esac
    done
    [ "$backend" = fsdp ] && [ -n "$local_dir" ] && [ -n "$target_dir" ]
    printf 'merge:%s\n' "$local_dir" >> "$WM_TEST_ROOT/events.log"
    mkdir -p "$target_dir"
    printf '{}' > "$target_dir/config.json"
    printf 'new dummy model' > "$target_dir/model.safetensors"
else
    printf 'Unexpected python3 invocation\n' >&2
    exit 91
fi
'''


@unittest.skipUnless(BASH, "Bash is required for the UP pipeline smoke tests")
class UpPipelineResumeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="up-resume-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for relative in (
            "baseline_acl/run_up_gad_pipeline.sh",
            "scripts/train/run_full_gad_all_clean_optimized.sh",
            "scripts/train/run_full_gad_up_up_optimized.sh",
            "scripts/train/run_full_gad_up_kgw_optimized.sh",
        ):
            source = (REPO_ROOT / relative).read_text(encoding="utf-8")
            # The offline copies must neither configure nor expose a real key.
            source = re.sub(r"^export SWANLAB_API_KEY=.*\n?", "", source, flags=re.MULTILINE)
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(source, encoding="utf-8", newline="\n")
        (self.root / "baseline_acl/validate_up_data.py").touch()
        self.bin = self.root / "bin"
        self.bin.mkdir()
        for name, content in {
            "python3": PYTHON_STUB,
            "swanlab": "#!/bin/bash\nexit 0\n",
            "timeout": '#!/bin/bash\nshift\nexec "$@"\n',
        }.items():
            path = self.bin / name
            path.write_text(content, encoding="utf-8", newline="\n")
            path.chmod(0o755)
        (self.root / "model").mkdir()
        (self.root / "model/config.json").write_text("{}", encoding="utf-8")
        for relative in (UP_TRAIN, KGW_TRAIN, KGW_VAL):
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"offline fixture; validation is stubbed")
        self.env = os.environ.copy()
        for name in ("BASH_ENV", "ENV", "SHELLOPTS", "WM_FAIL_STAGE", "SWANLAB_API_KEY"):
            self.env.pop(name, None)
        self.env.update({
            "PATH": str(self.bin) + os.pathsep + self.env.get("PATH", ""),
            "WM_TEST_ROOT": shell_path(self.root),
            "CUDA_VISIBLE_DEVICES": "1,3",
            "RAY_TMPDIR": shell_path(self.root / "ray_tmp"),
            "RAY_NUM_CPUS": "8",
        })

    def run_pipeline(self, *options, branch="up_kgw", experiment="experiment", fail_stage=None):
        env = self.env.copy()
        if fail_stage:
            env["WM_FAIL_STAGE"] = fail_stage
        return subprocess.run(
            [
                BASH, f"scripts/train/run_full_gad_{branch}_optimized.sh",
                "--model", "model", "--exp_name", experiment, "--work_dir", "work",
                *options,
            ],
            cwd=self.root, env=env, capture_output=True, text=True, timeout=30,
        )

    def calls(self):
        return [
            path.read_text(encoding="utf-8").splitlines()
            for path in sorted((self.root / "calls").glob("*.args"), key=lambda p: int(p.stem))
        ]

    def trainer_calls(self):
        return [args for args in self.calls() if args[:2] == ["-m", "verl.trainer.main_ppo"]]

    def merge_calls(self):
        return [args for args in self.calls() if args[:2] == ["scripts/model_merger.py", "merge"]]

    def validator_call(self):
        calls = [args for args in self.calls() if args[0].endswith("/baseline_acl/validate_up_data.py")]
        self.assertEqual(len(calls), 1)
        return calls[0]

    def assert_success(self, result):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def clear_calls(self):
        for path in (self.root / "calls").glob("*"):
            path.unlink()
        for name in ("counter", "events.log"):
            (self.root / name).unlink(missing_ok=True)

    def checkpoint(self, stage="warmup", *, step=5, merged=False, completed=False, experiment="experiment"):
        stage_dir = self.root / "work" / experiment / stage
        checkpoint = stage_dir / f"global_step_{step}"
        for role in ("actor", "critic"):
            role_dir = checkpoint / role
            role_dir.mkdir(parents=True)
            (role_dir / "config.json").write_text("{}", encoding="utf-8")
            if merged:
                exported = role_dir / "huggingface"
                exported.mkdir()
                (exported / "config.json").write_text("{}", encoding="utf-8")
                (exported / "model.safetensors").write_bytes(f"preserve {role}".encode())
                (exported / ".merge_completed").touch()
        (checkpoint / "data.pt").write_bytes(b"saved dataloader")
        (stage_dir / "latest_checkpointed_iteration.txt").write_text(str(step), encoding="utf-8")
        if completed:
            (stage_dir / ".stage_completed").write_text(str(step), encoding="utf-8")
        return checkpoint

    def assert_stage_data(self, args, *, stage, train_file, val_file=KGW_VAL, resume_mode="auto"):
        for expected in (
            f"trainer.training_stage={stage}", f"data.train_files={train_file}",
            f"data.val_files={val_file}", f"trainer.resume_mode={resume_mode}",
            "trainer.total_epochs=1",
        ):
            self.assertIn(expected, args)

    def assert_exports_unchanged(self, checkpoint):
        for role in ("actor", "critic"):
            exported = checkpoint / role / "huggingface"
            self.assertEqual((exported / "model.safetensors").read_bytes(), f"preserve {role}".encode())
            self.assertTrue((exported / ".merge_completed").is_file())

    def test_fresh_both_branches_keep_up_training_and_kgw_validation(self):
        for branch, gad_file in (("up_up", UP_TRAIN), ("up_kgw", KGW_TRAIN)):
            with self.subTest(branch=branch):
                result = self.run_pipeline(branch=branch, experiment=branch)
                self.assert_success(result)
                calls = self.trainer_calls()
                self.assertEqual(len(calls), 2)
                self.assert_stage_data(calls[0], stage="warmup", train_file=UP_TRAIN, resume_mode="disable")
                self.assert_stage_data(calls[1], stage="gad", train_file=gad_file, resume_mode="disable")
                validator = self.validator_call()
                for flag, value in (("--original_train_file", KGW_TRAIN), ("--up_train_file", UP_TRAIN), ("--val_file", KGW_VAL)):
                    self.assertEqual(validator[validator.index(flag) + 1], value)
                self.assertEqual(len(self.merge_calls()), 2)
                self.assertTrue((self.root / "work" / branch / "warmup/.stage_completed").is_file())
                self.clear_calls()

    def test_resume_completed_warmup_skips_training_and_preserves_both_exports(self):
        for branch, gad_file in (("up_up", UP_TRAIN), ("up_kgw", KGW_TRAIN)):
            with self.subTest(branch=branch):
                checkpoint = self.checkpoint(merged=True, completed=True, experiment=branch)
                self.assert_success(self.run_pipeline("--resume", branch=branch, experiment=branch))
                calls = self.trainer_calls()
                self.assertEqual(len(calls), 1)
                self.assert_stage_data(calls[0], stage="gad", train_file=gad_file)
                self.assertIn("actor_rollout_ref.model.path=" + str(Path("work") / branch / "warmup/global_step_5/actor/huggingface").replace("\\", "/"), calls[0])
                self.assertIn("critic.model.path=" + str(Path("work") / branch / "warmup/global_step_5/critic/huggingface").replace("\\", "/"), calls[0])
                self.assertEqual(self.merge_calls(), [])
                self.assert_exports_unchanged(checkpoint)
                self.validator_call()
                self.clear_calls()

    def test_explicit_skip_warmup_for_legacy_run_remerges_unmarked_exports_on_cpu(self):
        checkpoint = self.checkpoint(merged=True)
        for role in ("actor", "critic"):
            (checkpoint / role / "huggingface/.merge_completed").unlink()
        self.assert_success(self.run_pipeline("--resume", "--skip_warmup"))
        self.assertEqual(len(self.trainer_calls()), 1)
        self.assert_stage_data(self.trainer_calls()[0], stage="gad", train_file=KGW_TRAIN)
        merges = self.merge_calls()
        self.assertEqual(len(merges), 2)
        for args, role in zip(merges, ("actor", "critic")):
            self.assertEqual(args[args.index("--backend") + 1], "fsdp")
            self.assertEqual(args[args.index("--local_dir") + 1], f"work/experiment/warmup/global_step_5/{role}")
            self.assertEqual(args[args.index("--target_dir") + 1], f"work/experiment/warmup/global_step_5/{role}/huggingface")
        merge_env = [path.read_text(encoding="utf-8").strip() for path in (self.root / "calls").glob("*.env")]
        self.assertEqual(merge_env.count("CUDA_VISIBLE_DEVICES="), 2)

    def test_gad_checkpoint_without_legacy_completion_marker_auto_skips_warmup(self):
        checkpoint = self.checkpoint(merged=True)
        self.checkpoint("gad")
        self.assert_success(self.run_pipeline("--resume"))
        self.assertEqual(len(self.trainer_calls()), 1)
        self.assert_stage_data(self.trainer_calls()[0], stage="gad", train_file=KGW_TRAIN)
        self.assertEqual(self.merge_calls(), [])
        self.assert_exports_unchanged(checkpoint)

    def test_interrupted_warmup_resumes_then_exports_and_runs_gad(self):
        result = self.run_pipeline(fail_stage="warmup")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.root / "work/experiment/warmup/.stage_completed").exists())
        self.assertEqual(self.merge_calls(), [])
        self.clear_calls()
        self.assert_success(self.run_pipeline("--resume"))
        calls = self.trainer_calls()
        self.assertEqual(len(calls), 2)
        self.assert_stage_data(calls[0], stage="warmup", train_file=UP_TRAIN)
        self.assert_stage_data(calls[1], stage="gad", train_file=KGW_TRAIN)
        self.assertEqual(len(self.merge_calls()), 2)

    def test_custom_data_paths_survive_resume_and_validator_preflight(self):
        up, kgw, val = "custom/up.parquet", "custom/kgw.parquet", "custom/val.parquet"
        for relative in (up, kgw, val):
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()
        self.checkpoint(merged=True, completed=True)
        self.assert_success(self.run_pipeline("--resume", "--up_train_file", up, "--kgw_train_file", kgw, "--val_file", val))
        calls = self.trainer_calls()
        self.assertEqual(len(calls), 1)
        self.assert_stage_data(calls[0], stage="gad", train_file=kgw, val_file=val)
        validator = self.validator_call()
        for flag, value in (("--original_train_file", kgw), ("--up_train_file", up), ("--val_file", val)):
            self.assertEqual(validator[validator.index(flag) + 1], value)

    def test_existing_directory_without_resume_is_rejected_before_training(self):
        checkpoint = self.checkpoint(merged=True, completed=True)
        result = self.run_pipeline()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("already exists", result.stdout + result.stderr)
        self.assertEqual(self.trainer_calls(), [])
        self.assertEqual(self.merge_calls(), [])
        self.assert_exports_unchanged(checkpoint)

    def test_skip_warmup_requires_resume_and_saved_warmup_checkpoint(self):
        result = self.run_pipeline("--skip_warmup")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("requires --resume", result.stdout + result.stderr)
        self.assertEqual(self.trainer_calls(), [])
        (self.root / "work/experiment").mkdir(parents=True)
        self.clear_calls()
        result = self.run_pipeline("--resume", "--skip_warmup")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("saved warmup checkpoint", result.stdout + result.stderr)
        self.assertEqual(self.trainer_calls(), [])

    def test_tracker_ignores_newer_incomplete_save_and_refuses_incomplete_tracked_save(self):
        checkpoint = self.checkpoint(merged=True, completed=True)
        incomplete = self.root / "work/experiment/warmup/global_step_999"
        (incomplete / "actor").mkdir(parents=True)
        self.assert_success(self.run_pipeline("--resume"))
        self.assertIn("actor_rollout_ref.model.path=work/experiment/warmup/global_step_5/actor/huggingface", self.trainer_calls()[0])
        self.assert_exports_unchanged(checkpoint)
        self.clear_calls()
        (checkpoint / "data.pt").unlink()
        result = self.run_pipeline("--resume")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("incomplete checkpoint", result.stdout + result.stderr)
        self.assertEqual(self.trainer_calls(), [])
        self.assertEqual(self.merge_calls(), [])

    def test_empty_or_mismatched_completion_marker_is_rejected(self):
        self.checkpoint(merged=True, completed=True)
        marker = self.root / "work/experiment/warmup/.stage_completed"
        for value in ("", "4", "not-a-step"):
            with self.subTest(marker=value):
                marker.write_text(value, encoding="utf-8")
                result = self.run_pipeline("--resume")
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("marker", result.stdout + result.stderr)
                self.assertEqual(self.trainer_calls(), [])
                self.assertEqual(self.merge_calls(), [])
                self.clear_calls()


if __name__ == "__main__":
    unittest.main()
