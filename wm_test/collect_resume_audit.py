"""Collect small local evidence for a two-stage training audit; no torch needed.

Run from the server's project directory. Reads checkpoints and Ray logs, never
loads weights or changes training state. Only --output is written.
"""
import argparse
import ast
from collections import deque
import hashlib
import json
import os
from pathlib import Path
import re


SENSITIVE = re.compile(r"api.?key|password|secret|credential|authorization|access.?token|auth.?token", re.I)
EVENT = re.compile(r"Training from scratch|Load from checkpoint folder:|Setting global step|Resuming from|Loaded (?:model|optimizer|rng|lr_scheduler) from|No dataloader state|Total training steps:|local_global_step_folder:|already completed|Last validation metrics")
CONFIG_KEYS = {"_name_or_path", "name_or_path", "architectures", "model_type", "torch_dtype", "dtype", "hidden_size", "num_hidden_layers", "num_attention_heads", "num_labels", "vocab_size", "bos_token_id", "eos_token_id", "pad_token_id"}
CODE_FILES = ["scripts/train/run_full_gad_optimized.sh", "verl/trainer/ppo/ray_trainer.py", "verl/workers/actor/dp_actor.py", "verl/workers/critic/dp_critic.py", "verl/trainer/ppo/core_algos.py", "verl/workers/fsdp_workers.py", "tools/merge_model2hf.py"]


def flat_safe(value, prefix="", result=None):
    result = {} if result is None else result
    if isinstance(value, dict):
        for key, child in value.items():
            if SENSITIVE.search(str(key)):
                continue
            flat_safe(child, f"{prefix}.{key}" if prefix else str(key), result)
    else:
        result[prefix] = value
    return result


def small_text(path):
    if not path.is_file():
        return None
    if path.stat().st_size > 16384:
        return "FILE_TOO_LARGE_FOR_SMALL_METADATA"
    return path.read_text(encoding="utf-8", errors="replace").strip()


def snapshot(checkpoint):
    result = {}
    for stage in ("warmup", "gad"):
        directory = checkpoint / stage
        tracker = small_text(directory / "latest_checkpointed_iteration.txt")
        saved = sorted((p.name for p in directory.glob("global_step_*") if p.is_dir()), key=lambda name: int(name.rsplit("_", 1)[-1]) if name.rsplit("_", 1)[-1].isdigit() else -1)
        info = {"tracker": tracker, "stage_completed": small_text(directory / ".stage_completed"), "checkpoint_directories": saved}
        if tracker and tracker.isdigit():
            selected = directory / ("global_step_" + tracker)
            info["selected_checkpoint"] = str(selected)
            info["data_pt_exists"] = (selected / "data.pt").is_file()
            info["files"] = []
            for relative in ["data.pt"] + [f"{role}/{p.name}" for role in ("actor", "critic") for p in (selected / role).glob("*") if p.is_file()] + [f"{role}/huggingface/{p.name}" for role in ("actor", "critic") for p in (selected / role / "huggingface").glob("*") if p.is_file()]:
                path = selected / relative
                if path.is_file():
                    info["files"].append({"path": relative, "bytes": path.stat().st_size})
            info["model_configs"] = {}
            info["merge_completed"] = {}
            for role in ("actor", "critic"):
                info["merge_completed"][role] = (selected / role / "huggingface/.merge_completed").is_file()
                for relative in (f"{role}/config.json", f"{role}/huggingface/config.json"):
                    path = selected / relative
                    if path.is_file():
                        try:
                            cfg = json.loads(path.read_text(encoding="utf-8"))
                            info["model_configs"][relative] = {k: v for k, v in cfg.items() if k in CONFIG_KEYS}
                        except (OSError, ValueError) as exc:
                            info["model_configs"][relative] = {"error": type(exc).__name__}
        result[stage] = info
    return result


def inspect_log(path, experiment):
    # Resolved config is a pprint Python dict in the TaskRunner .out log.
    needle = experiment.encode("utf-8")
    found = False
    with path.open("rb") as handle:
        tail = b""
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            combined = tail + chunk
            if needle in combined:
                found = True
                break
            tail = combined[-len(needle):]
    if not found:
        return None
    config_lines = []
    config = None
    active = False
    matches = False
    events = []
    last_metrics = deque(maxlen=2)
    first_metric = None
    with path.open(encoding="utf-8", errors="replace") as handle:
        for lineno, line in enumerate(handle, 1):
            matches |= experiment in line
            if not config and not active and line.lstrip().startswith("{'actor_rollout_ref':"):
                active = True
            if active:
                config_lines.append(line)
                if len(config_lines) > 1500:
                    active = False
                    config_lines = []
                elif line.rstrip().endswith("}"):
                    try:
                        config = ast.literal_eval("".join(config_lines))
                        active = False
                    except (SyntaxError, ValueError):
                        pass
            if EVENT.search(line) and not SENSITIVE.search(line):
                events.append({"line": lineno, "text": line.strip()[:4000]})
            if re.search(r"step:\s*\d+\s+-", line) and ("actor/" in line or "critic/" in line) and not SENSITIVE.search(line):
                metric = {"line": lineno, "text": line.strip()[:16000]}
                if first_metric is None:
                    first_metric = metric
                last_metrics.append(metric)
    if not matches:
        return None
    item = {"path": str(path), "events": events[-100:]}
    if config is not None:
        item["actual_config_safe"] = flat_safe(config)
    if first_metric is not None:
        item["first_train_metric"] = first_metric
        item["last_train_metrics"] = list(last_metrics)
    return item


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", default="checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta3")
    parser.add_argument("--log-root", action="append", default=[], help="Additional Ray root, session directory, or logs directory")
    parser.add_argument("--output", default="resume_audit.json")
    args = parser.parse_args()
    checkpoint = Path(args.checkpoint).resolve()
    roots = [Path("ray_tmp/ray"), Path("/tmp") / ("easygad-" + os.environ.get("USER", "user")) / "ray"]
    if os.environ.get("RAY_TMPDIR"):
        roots += [Path(os.environ["RAY_TMPDIR"]) / "ray", Path(os.environ["RAY_TMPDIR"])]
    roots += [Path(p) for p in args.log_root]
    files = set()
    for root in roots:
        if root.is_dir():
            for pattern in ("**/logs/worker-*.out", "**/logs/worker-*.err", "worker-*.out", "worker-*.err"):
                files.update(p.resolve() for p in root.glob(pattern) if p.is_file())
    report = {"checkpoint": str(checkpoint), "checkpoint_metadata": snapshot(checkpoint), "searched_log_roots": [str(p) for p in roots], "ray_logs": [], "source_sha256_lf": {}, "errors": []}
    for path in sorted(files):
        try:
            item = inspect_log(path, checkpoint.name)
            if item:
                report["ray_logs"].append(item)
        except OSError as exc:
            report["errors"].append({"path": str(path), "error": type(exc).__name__})
    for filename in CODE_FILES:
        path = Path(filename)
        if path.is_file():
            report["source_sha256_lf"][filename] = hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
    output = Path(args.output)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    gad = [item for item in report["ray_logs"] if item.get("actual_config_safe", {}).get("trainer.training_stage") == "gad"]
    print(f"Saved {output.resolve()}; matching logs={len(report['ray_logs'])}, GAD configs={len(gad)}")
    if not gad:
        print("No GAD config found. Add --log-root <the Ray root used for the completed run> if logs are stored elsewhere.")


if __name__ == "__main__":
    main()
