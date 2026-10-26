"""Offline regression tests for the two-stage GAD launcher's resume contract.

Run with ``python -m unittest discover -s tests/scripts -p 'test_full_gad_resume.py'``.
The launcher runs in a temporary sandbox with fake training/merge commands; no
GPU, training dependencies, network access, or existing checkpoint is used.
"""

import ast
import contextlib
import io
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts/train/run_full_gad_optimized.sh"
TRAINER = REPO_ROOT / "verl/trainer/ppo/ray_trainer.py"
BASH = shutil.which("bash")
if os.name == "nt":
    for candidate in (Path(r"D:\software\Git\bin\bash.exe"), Path(r"C:\Program Files\Git\bin\bash.exe")):
        if candidate.is_file():
            BASH = str(candidate)
            break


def shell_path(path):
    """Convert a local path for Git Bash without launching an extra process."""
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
printf '%s\n' "CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES-}" "RAY_TMPDIR=${RAY_TMPDIR-}" > "$WM_TEST_ROOT/calls/$counter.env"
if [ "${1-}" = "-m" ] && [ "${2-}" = "verl.trainer.main_ppo" ]; then
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
elif [ "${1-}" = "tools/prepare_split_warmup_data.py" ]; then
    output=
    while [ $# -gt 0 ]; do
        if [ "$1" = "--output_file" ]; then output=$2; shift 2; else shift; fi
    done
    printf 'dummy paired data' > "$output"
elif [ "${1-}" = "tools/merge_model2hf.py" ]; then
    local_dir=
    while [ $# -gt 0 ]; do
        if [ "$1" = "--local_dir" ]; then local_dir=$2; shift 2; else shift; fi
    done
    printf 'merge:%s\n' "$local_dir" >> "$WM_TEST_ROOT/events.log"
    mkdir -p "$local_dir/huggingface"
    printf '{}' > "$local_dir/huggingface/config.json"
    printf 'dummy model' > "$local_dir/huggingface/model.safetensors"
else
    printf 'Unexpected python3 invocation\n' >&2
    exit 91
fi
'''


@unittest.skipUnless(BASH, "Bash is required for the launcher smoke tests")
class LauncherResumeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="gad-resume-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.bin = self.root / "bin"
        self.bin.mkdir()
        # Keep a copied launcher isolated, including credentials in its config.
        source = SCRIPT.read_text(encoding="utf-8")
        source = re.sub(r"^export SWANLAB_API_KEY=.*$", "export SWANLAB_API_KEY='offline-test'", source, flags=re.MULTILINE)
        (self.root / "launch.sh").write_text(source, encoding="utf-8", newline="\n")
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
        (self.root / "data").mkdir()
        for split in ("up_dipper_newtrain", "newtest"):
            (self.root / f"data/dolly15k_qwen2_5_14b_kgw_gamma0.5_delta3_{split}.parquet").write_text("dummy", encoding="utf-8")
        self.work = self.root / "checkpoints/experiment"
        self.env = os.environ.copy()
        self.env.update({
            "PATH": str(self.bin) + os.pathsep + os.environ.get("PATH", ""),
            "WM_TEST_ROOT": shell_path(self.root),
            "CUDA_VISIBLE_DEVICES": "1,2",
            "RAY_TMPDIR": shell_path(self.root / "ray"),
            "RAY_NUM_CPUS": "8",
        })
        self.env.pop("WM_FAIL_STAGE", None)

    def launch(self, *args, fail_stage=None):
        env = self.env.copy()
        if fail_stage:
            env["WM_FAIL_STAGE"] = fail_stage
        return subprocess.run(
            [BASH, "launch.sh", "--model", "model", "--exp_name", "experiment", "--nnodes", "1", *args],
            cwd=self.root, env=env, text=True, encoding="utf-8", capture_output=True, timeout=30,
        )

    def events(self):
        path = self.root / "events.log"
        return path.read_text(encoding="utf-8").splitlines() if path.is_file() else []

    def calls(self):
        paths = sorted((self.root / "calls").glob("*.args"), key=lambda p: int(p.stem))
        return [p.read_text(encoding="utf-8").splitlines() for p in paths]

    def trainer_calls(self):
        return [args for args in self.calls() if args[:2] == ["-m", "verl.trainer.main_ppo"]]

    def clear_calls(self):
        for path in (self.root / "calls").glob("*"):
            path.unlink()
        for name in ("events.log", "counter"):
            path = self.root / name
            if path.exists():
                path.unlink()

    def checkpoint(self, stage="warmup", step=5, merged=False):
        stage_dir = self.work / stage
        checkpoint = stage_dir / f"global_step_{step}"
        for role in ("actor", "critic"):
            role_dir = checkpoint / role
            role_dir.mkdir(parents=True)
            (role_dir / "config.json").write_text("{}", encoding="utf-8")
            if merged:
                hf = role_dir / "huggingface"
                hf.mkdir()
                (hf / "config.json").write_text("{}", encoding="utf-8")
                (hf / "model.safetensors").write_text("dummy", encoding="utf-8")
                (hf / ".merge_completed").touch()
        (checkpoint / "data.pt").write_text("dummy", encoding="utf-8")
        (stage_dir / "latest_checkpointed_iteration.txt").write_text(str(step), encoding="utf-8")
        return checkpoint

    def assertSuccess(self, result):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_fresh_run_completes_both_stages_and_marks_warmup(self):
        result = self.launch()
        self.assertSuccess(result)
        self.assertEqual(self.events(), [
            "trainer:warmup",
            "merge:checkpoints/experiment/warmup/global_step_5/actor",
            "merge:checkpoints/experiment/warmup/global_step_5/critic",
            "trainer:gad",
        ])
        self.assertTrue((self.work / "warmup/.stage_completed").is_file())
        for args in self.trainer_calls():
            self.assertIn("trainer.resume_mode=disable", args)

    def test_existing_experiment_requires_explicit_resume(self):
        self.work.mkdir(parents=True)
        result = self.launch()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("already exists", result.stdout + result.stderr)
        self.assertIn("--resume", result.stdout + result.stderr)
        self.assertEqual(self.events(), [])

    def test_stage_data_overrides_reach_each_trainer(self):
        for name in ("paired", "para", "validation"):
            (self.root / f"data/{name}.parquet").write_text("dummy", encoding="utf-8")
        result = self.launch(
            "--warmup_train_file", "data/paired.parquet", "--gad_train_file", "data/para.parquet",
            "--val_file", "data/validation.parquet", "--logger", "console",
        )
        self.assertSuccess(result)
        warmup, gad = self.trainer_calls()
        self.assertIn("data.train_files=data/paired.parquet", warmup)
        self.assertIn("data.train_files=data/para.parquet", gad)
        for args in (warmup, gad):
            self.assertIn("data.val_files=data/validation.parquet", args)
            self.assertIn("trainer.logger=['console']", args)

    def test_dry_run_starts_no_training_or_merging(self):
        result = self.launch("--dry_run", "--logger", "console")
        self.assertSuccess(result)
        self.assertIn("Configuration checks passed", result.stdout)
        self.assertEqual(self.events(), [])
        self.assertFalse(self.work.exists())

    def test_split_wrapper_preserves_all_non_data_training_arguments(self):
        self.assertSuccess(self.launch())
        baseline = self.trainer_calls()
        self.clear_calls()
        for name in ("scripts/train", "verl/utils/dataset", "verl/workers/actor"):
            (self.root / name).mkdir(parents=True, exist_ok=True)
        wrapper_name = "run_full_gad_kgwD_paraSFT_paraGAD_optimized.sh"
        shutil.copyfile(REPO_ROOT / "scripts/train" / wrapper_name, self.root / "scripts/train" / wrapper_name)
        shutil.copyfile(self.root / "launch.sh", self.root / "scripts/train/run_full_gad_optimized.sh")
        (self.root / "verl/utils/dataset/rl_dataset.py").write_text("build_sft_response_tensors", encoding="utf-8")
        (self.root / "verl/workers/actor/dp_actor.py").write_text("select_warmup_sft_targets", encoding="utf-8")
        result = subprocess.run(
            [BASH, f"scripts/train/{wrapper_name}", "--model", "model", "--exp_name", "experiment", "--work_dir", "compare_split"],
            cwd=self.root, env=self.env, text=True, encoding="utf-8", capture_output=True, timeout=30,
        )
        self.assertSuccess(result)
        variant = self.trainer_calls()
        self.assertEqual(len(baseline), 2)
        self.assertEqual(len(variant), 2)
        for stage, old, new in zip(("warmup", "gad"), baseline, variant):
            with self.subTest(stage=stage):
                if stage == "warmup":
                    self.assertIn("data.train_files=data/dolly15k_qwen2_5_14b_kgw_gamma0.5_delta3_kgwD_paraSFT_newtrain.parquet", new)
                else:
                    self.assertEqual([arg for arg in old if arg.startswith("data.train_files=")],
                                     [arg for arg in new if arg.startswith("data.train_files=")])
                def normalized(args):
                    return [arg.replace("compare_split/experiment/", "checkpoints/experiment/")
                            for arg in args if not arg.startswith("data.train_files=")]
                self.assertEqual(normalized(old), normalized(new))
                self.assertIn("trainer.logger=['console','swanlab']", new)

    def test_resume_requires_existing_experiment(self):
        result = self.launch("--resume")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("existing experiment directory", result.stdout + result.stderr)
        self.assertEqual(self.events(), [])

    def test_old_successful_warmup_can_be_explicitly_skipped(self):
        self.checkpoint()
        result = self.launch("--resume", "--skip_warmup")
        self.assertSuccess(result)
        self.assertNotIn("trainer:warmup", self.events())
        self.assertEqual(len(self.trainer_calls()), 1)
        self.assertIn("trainer.training_stage=gad", self.trainer_calls()[0])
        self.assertIn("trainer.resume_mode=auto", self.trainer_calls()[0])

    def test_completed_warmup_marker_automatically_skips_warmup(self):
        self.checkpoint()
        (self.work / "warmup/.stage_completed").touch()
        result = self.launch("--resume")
        self.assertSuccess(result)
        self.assertNotIn("trainer:warmup", self.events())

    def test_failed_warmup_is_resumed_before_gad(self):
        failed = self.launch(fail_stage="warmup")
        self.assertNotEqual(failed.returncode, 0)
        self.assertEqual(self.events(), ["trainer:warmup"])
        self.assertFalse((self.work / "warmup/.stage_completed").exists())
        self.clear_calls()
        resumed = self.launch("--resume")
        self.assertSuccess(resumed)
        self.assertEqual(self.events()[0], "trainer:warmup")
        self.assertEqual(self.events()[-1], "trainer:gad")
        for args in self.trainer_calls():
            self.assertIn("trainer.resume_mode=auto", args)

    def test_failed_gad_resumes_automatically_and_reuses_exports(self):
        failed = self.launch(fail_stage="gad")
        self.assertNotEqual(failed.returncode, 0)
        self.assertTrue((self.work / "warmup/.stage_completed").is_file())
        self.clear_calls()
        resumed = self.launch("--resume")
        self.assertSuccess(resumed)
        self.assertEqual(self.events(), ["trainer:gad"])
        self.assertIn("trainer.resume_mode=auto", self.trainer_calls()[0])

    def test_gad_tracker_skips_warmup_for_legacy_runs_without_marker(self):
        self.checkpoint("warmup", merged=True)
        self.checkpoint("gad")
        result = self.launch("--resume")
        self.assertSuccess(result)
        self.assertEqual(self.events(), ["trainer:gad"])

    def test_merged_models_with_completion_markers_are_reused(self):
        self.checkpoint(merged=True)
        result = self.launch("--resume", "--skip_warmup")
        self.assertSuccess(result)
        self.assertEqual(self.events(), ["trainer:gad"])
        self.assertIn("Reusing merged model", result.stdout)

    def test_unmarked_legacy_exports_are_merged_again(self):
        checkpoint = self.checkpoint(merged=True)
        for role in ("actor", "critic"):
            (checkpoint / role / "huggingface/.merge_completed").unlink()
        result = self.launch("--resume", "--skip_warmup")
        self.assertSuccess(result)
        self.assertEqual(sum(event.startswith("merge:") for event in self.events()), 2)

    def test_tracker_selects_saved_checkpoint_instead_of_newer_partial_save(self):
        self.checkpoint(step=5)
        (self.work / "warmup/global_step_999/actor").mkdir(parents=True)
        result = self.launch("--resume", "--skip_warmup")
        self.assertSuccess(result)
        self.assertIn("actor_rollout_ref.model.path=checkpoints/experiment/warmup/global_step_5/actor/huggingface", self.trainer_calls()[0])

    def test_corrupt_tracker_is_rejected_before_training(self):
        self.checkpoint()
        (self.work / "warmup/latest_checkpointed_iteration.txt").write_text("not-a-step", encoding="utf-8")
        result = self.launch("--resume", "--skip_warmup")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid checkpoint tracker", result.stdout + result.stderr)
        self.assertEqual(self.events(), [])

    def test_incomplete_checkpoint_is_rejected_before_training(self):
        checkpoint = self.checkpoint()
        shutil.rmtree(checkpoint / "critic")
        result = self.launch("--resume", "--skip_warmup")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("incomplete checkpoint", result.stdout + result.stderr)
        self.assertEqual(self.events(), [])

    def test_skip_warmup_requires_resume_and_a_checkpoint(self):
        result = self.launch("--skip_warmup")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--skip_warmup requires --resume", result.stdout + result.stderr)
        self.work.mkdir(parents=True)
        result = self.launch("--resume", "--skip_warmup")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("saved warmup checkpoint", result.stdout + result.stderr)
        self.assertEqual(self.events(), [])

    def test_external_gpu_and_ray_settings_reach_each_trainer(self):
        custom_ray = shell_path(self.root / "custom-ray")
        result = self.launch("--ray_tmpdir", custom_ray, "--ray_num_cpus", "3")
        self.assertSuccess(result)
        for args in self.trainer_calls():
            self.assertIn("ray_init.num_cpus=3", args)
        for path in (self.root / "calls").glob("*.env"):
            env_lines = path.read_text(encoding="utf-8").splitlines()
            self.assertIn("CUDA_VISIBLE_DEVICES=1,2", env_lines)
            self.assertIn(f"RAY_TMPDIR={custom_ray}", env_lines)
        self.assertTrue((self.root / "custom-ray").is_dir())

    def test_ray_environment_setting_is_used_without_cli_override(self):
        self.env["RAY_NUM_CPUS"] = "6"
        result = self.launch()
        self.assertSuccess(result)
        for args in self.trainer_calls():
            self.assertIn("ray_init.num_cpus=6", args)

    def test_invalid_ray_cpu_count_and_unknown_arguments_fail(self):
        for args in (("--ray_num_cpus", "0"), ("--unknown-option",)):
            with self.subTest(args=args):
                result = self.launch(*args)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(self.events(), [])


class AttrDict(dict):
    """Enough of DictConfig's interface for the isolated fit entry path."""

    __getattr__ = dict.__getitem__


class CompletedTrainingGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        tree = ast.parse(TRAINER.read_text(encoding="utf-8"))
        trainer = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "RayPPOTrainer")
        fit = next(node for node in trainer.body if isinstance(node, ast.FunctionDef) and node.name == "fit")
        isolated = ast.fix_missing_locations(ast.Module(body=[fit], type_ignores=[]))
        # Compile only fit so importing the trainer cannot initialize CUDA/Ray.
        namespace = {"pprint": lambda *args, **kwargs: None, "tqdm": cls.unexpected_progress}
        exec(compile(isolated, str(TRAINER), "exec"), namespace)
        cls.fit = namespace["fit"]

    @staticmethod
    def unexpected_progress(*args, **kwargs):
        raise AssertionError("completed training must not reach the progress bar or training loop")

    def run_fit(self, step, total, val_only=False):
        events = []

        class Dataloader:
            def __iter__(self):
                raise AssertionError("completed training must not iterate the dataloader")

        class Tracking:
            def __init__(self, **kwargs):
                pass

            def log(self, **kwargs):
                events.append("log")

        trainer_config = AttrDict(project_name="offline", experiment_name="offline", logger=[], val_only=val_only, val_before_train=True)
        fake = types.SimpleNamespace(
            config=AttrDict(trainer=trainer_config),
            total_training_steps=total,
            val_reward_fn=object(),
            train_dataloader=Dataloader(),
        )

        def load_checkpoint():
            events.append("load")
            fake.global_steps = step

        def validate():
            events.append("validate")
            return {"offline/validation": 1}

        fake._load_checkpoint = load_checkpoint
        fake._validate = validate
        omega = types.ModuleType("omegaconf")
        omega.OmegaConf = types.SimpleNamespace(to_container=lambda config, **kwargs: {})
        tracking = types.ModuleType("verl.utils.tracking")
        tracking.Tracking = Tracking
        with patch.dict(sys.modules, {"omegaconf": omega, "verl.utils.tracking": tracking}), contextlib.redirect_stdout(io.StringIO()):
            type(self).fit(fake)
        return events, fake.global_steps

    def test_completed_or_over_budget_checkpoint_returns_before_validation(self):
        for step in (10, 11):
            with self.subTest(step=step):
                events, actual_step = self.run_fit(step=step, total=10)
                self.assertEqual(events, ["load"])
                self.assertEqual(actual_step, step)

    def test_val_only_still_validates_completed_checkpoint(self):
        events, actual_step = self.run_fit(step=10, total=10, val_only=True)
        self.assertEqual(events, ["load", "validate", "log"])
        self.assertEqual(actual_step, 10)


if __name__ == "__main__":
    unittest.main()
