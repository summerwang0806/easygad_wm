#!/usr/bin/env python3
"""Sequential overnight evaluation of four saved answer files.

Run without arguments. Reuses the unchanged single-file judge, cache, GPU
selection and reporting code; no CUDA libraries are imported by this launcher.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import time
import traceback
from typing import Any
import uuid

import run_soft_win_rate as single


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


@dataclass(frozen=True)
class Job:
    label: str
    input_path: Path


# Only this batch launcher uses this list. The single-file defaults stay intact.
JOBS = (
    Job("未清洗（KGW GAD）", ROOT / "wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.jsonl"),
    Job("Para", ROOT / "wm_test/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta3_new1_qwen2_5_0_5b_dolly15k_test.jsonl"),
    Job("WN strength=2.5", ROOT / "wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new.jsonl"),
    Job("WN strength=3", ROOT / "wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new_strength3.jsonl"),
)
REFERENCE_JSONL = single.REFERENCE_JSONL
RESULTS_DIR = single.RESULTS_DIR
HISTORY_FILE = single.HISTORY_FILE
BATCH_HISTORY_FILE = HERE / "four_soft_win_rate_history.md"


def project_path(path: Path) -> Path:
    path = Path(path)
    return (path if path.is_absolute() else ROOT / path).resolve()


def preflight(jobs: tuple[Job, ...] | list[Job], reference_path: Path) -> list[dict]:
    """Validate every input before starting the first expensive judge worker."""
    if not jobs:
        raise ValueError("The batch input list is empty")
    reference_path = project_path(reference_path)
    reference_hash = single.file_hash(reference_path)
    reference = single.load_answers(reference_path)
    rows, errors, labels, paths = [], [], set(), set()
    for job in jobs:
        path = project_path(job.input_path)
        try:
            if not job.label.strip() or job.label in labels or path in paths:
                raise ValueError("Batch labels and input paths must be nonempty and distinct")
            labels.add(job.label)
            paths.add(path)
            input_hash = single.file_hash(path)
            candidate = single.load_answers(path)
            ids = single.align_answers(candidate, reference)
            if not ids:
                raise ValueError("No aligned questions")
            if single.file_hash(path) != input_hash:
                raise ValueError("Input changed during batch preflight")
            rows.append({"label": job.label, "input_file": str(path), "input_sha256": input_hash,
                         "num_samples": len(ids),
                         "empty_candidate_answers": sum(not candidate[i]["answer"].strip() for i in ids)})
        except (OSError, ValueError, TypeError, KeyError) as error:
            errors.append(f"{job.label}: {path}: {type(error).__name__}: {error}")
    if single.file_hash(reference_path) != reference_hash:
        errors.append("Fixed reference changed during batch preflight")
    if errors:
        raise ValueError("Batch preflight failed; no judge was started:\n" + "\n".join(errors))
    return rows


class Tee:
    def __init__(self, stream, log):
        self.stream, self.log = stream, log

    def write(self, text: str) -> int:
        self.stream.write(text)
        self.log.write(text)
        self.log.flush()
        return len(text)

    def flush(self) -> None:
        self.stream.flush()
        self.log.flush()


@contextmanager
def batch_log(path: Path):
    with path.open("a", encoding="utf-8", newline="\n") as log:
        with redirect_stdout(Tee(sys.stdout, log)), redirect_stderr(Tee(sys.stderr, log)):
            yield


def cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\r", " ").replace("\n", " ")


def render_summary(summary: dict) -> str:
    states = {"pending": "待运行", "running": "运行中", "complete": "完成",
              "incomplete": "未完成", "failed": "失败", "interrupted": "已中断"}
    mode = "全量" if summary["limit"] is None else f"前 {summary['limit']} 题试跑"
    lines = [f"## 四文件评测 {summary['run_id']}", "",
             f"开始：{summary['started_at']}；结束：{summary.get('finished_at') or '尚未结束'}；范围：{mode}。",
             f"本轮状态：{'全部完成' if summary['complete'] else '尚未全部完成'}；固定参照：`{summary['reference_file']}`。",
             f"裁判：`{summary['judge_configuration']['model_path']}`；胜=1、平=0.5、负=0，逐题双顺序平均。", "",
             "| 方法 | 状态 | Soft Win Rate ↑ | 95% CI | 完整题目 | 复用/新增判断 |",
             "|---|---|---:|---|---:|---:|"]
    for row in summary["jobs"]:
        result = row.get("result") or {}
        score = result.get("soft_win_rate")
        score_text = f"{score:.2%}" if score is not None else "N/A"
        if score is not None and row["status"] != "complete":
            score_text += "（部分）"
        ci = result.get("ci95")
        ci_text = f"[{ci[0]:.2%}, {ci[1]:.2%}]" if ci else "N/A"
        valid = result.get("num_valid_samples", 0)
        cache = f"{result.get('cache_reused_rounds', 0)}/{result.get('new_judgments', 0)}"
        lines.append(f"| {cell(row['label'])} | {states[row['status']]} | {score_text} | {ci_text} | "
                     f"{valid}/{row['selected_samples']} | {cache} |")
    lines.extend(["", "未完成行的分数只覆盖已完成双顺序的题目；N/A 表示没有有效胜率。", ""])
    for row in summary["jobs"]:
        lines.append(f"- {cell(row['label'])}：`{row['input_file']}`")
        if row.get("error"):
            lines.append(f"  错误：{cell(row['error'])}")
        if row.get("result"):
            lines.append(f"  独立结果 JSON：`{row['result']['run_file']}`")
    lines.extend(["", f"逐文件详细记录：`{summary['history_file']}`。",
                  f"本轮汇总 JSON：`{summary['summary_file']}`。",
                  f"本轮完整日志：`{summary['log_file']}`。", ""])
    return "\n".join(lines) + "\n"


def write_snapshot(summary: dict) -> None:
    """Atomically replace this run's snapshot; never overwrite prior runs."""
    for filename, text in ((summary["summary_file"], json.dumps(summary, ensure_ascii=False, indent=2, allow_nan=False) + "\n"),
                           (summary["report_file"], render_summary(summary))):
        path = Path(filename)
        temporary = path.with_name(path.name + ".tmp")
        with temporary.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        temporary.replace(path)


def run_batch(jobs: tuple[Job, ...] | list[Job], *, reference_path: Path, config: single.JudgeConfig,
              results_dir: Path, history_file: Path, batch_history_file: Path,
              runner=None, limit: int | None = None, summary_only: bool = False) -> dict:
    if limit is not None and (not isinstance(limit, int) or isinstance(limit, bool) or limit < 1):
        raise ValueError("limit must be a positive integer")
    config.validate()
    checked = preflight(jobs, reference_path)
    reference_path, results_dir = project_path(reference_path), project_path(results_dir)
    history_file, batch_history_file = project_path(history_file), project_path(batch_history_file)
    model_path = project_path(Path(config.model_path))
    protected = {reference_path, *(Path(row["input_file"]) for row in checked)}
    if (history_file == batch_history_file or any(path in protected or path.is_relative_to(model_path)
                                                 for path in (history_file, batch_history_file))):
        raise ValueError("Batch history documents must be distinct and must not overwrite input/reference/model assets")
    # Fail early on missing/incomplete model assets, before creating any workers.
    single.fingerprint_model(model_path)
    reference_hash = single.file_hash(reference_path)
    batches = results_dir / "batches"
    batches.mkdir(parents=True, exist_ok=True)
    with single.evaluation_lock(batches / ".batch.lock"):
        run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + uuid.uuid4().hex[:8]
        directory = batches / run_id
        directory.mkdir()
        summary = {"run_id": run_id, "started_at": single.now(), "finished_at": None,
                   "complete": False, "interrupted": False, "limit": limit, "summary_only": summary_only,
                   "reference_file": str(reference_path), "reference_sha256": reference_hash,
                   "judge_configuration": {**asdict(config), "model_path": str(model_path)},
                   "history_file": str(history_file), "batch_history_file": str(batch_history_file),
                   "summary_file": str(directory / "summary.json"), "report_file": str(directory / "summary.md"),
                   "log_file": str(directory / "batch.log"),
                   "jobs": [{**row, "selected_samples": min(limit, row["num_samples"]) if limit else row["num_samples"],
                             "status": "pending", "result": None, "error": None} for row in checked]}
        write_snapshot(summary)
        with batch_log(Path(summary["log_file"])):
            print(f"[Batch] {len(checked)} files; fixed reference: {reference_path}", flush=True)
            print(f"[Batch] Summary: {summary['report_file']}", flush=True)
            print(f"[Batch] Full log: {summary['log_file']}", flush=True)
            try:
                for index, row in enumerate(summary["jobs"], 1):
                    started = time.monotonic()
                    row.update(status="running", started_at=single.now())
                    write_snapshot(summary)
                    print(f"\n[Batch {index}/{len(checked)}] START {row['label']}: {row['input_file']}", flush=True)
                    try:
                        if single.file_hash(reference_path) != reference_hash:
                            raise ValueError("Fixed reference changed since batch preflight")
                        if single.file_hash(Path(row["input_file"])) != row["input_sha256"]:
                            raise ValueError("Input changed since batch preflight")
                        result = single.run_evaluation(Path(row["input_file"]), reference_path, config,
                            results_dir, history_file, runner=runner, limit=limit, summary_only=summary_only)
                        row["result"] = result
                        row["status"] = "complete" if result["complete"] else "incomplete"
                        row["error"] = result.get("failure")
                    except KeyboardInterrupt:
                        row.update(status="interrupted", error="Interrupted by user; durable judgments can be resumed")
                        summary["interrupted"] = True
                        print("[Batch] Interrupted; no more files will be started. Rerun to reuse saved judgments.", flush=True)
                        break
                    except Exception as error:
                        row.update(status="failed", error=f"{type(error).__name__}: {error}")
                        print(f"[Batch] FAILED {row['label']}: {row['error']}; continuing with next file.", file=sys.stderr, flush=True)
                        traceback.print_exc()
                    finally:
                        row.update(finished_at=single.now(), duration_seconds=round(time.monotonic() - started, 2))
                        write_snapshot(summary)
                    print(f"[Batch {index}/{len(checked)}] {row['status'].upper()} {row['label']}", flush=True)
            except KeyboardInterrupt:
                # Also cover an interrupt between files or while printing status.
                summary["interrupted"] = True
                print("[Batch] Interrupted between files; saved judgments remain reusable.", flush=True)
            finally:
                summary["finished_at"] = single.now()
                summary["complete"] = all(row["status"] == "complete" for row in summary["jobs"])
                write_snapshot(summary)
                batch_history_file.parent.mkdir(parents=True, exist_ok=True)
                with single.evaluation_lock(batch_history_file.with_suffix(batch_history_file.suffix + ".lock")):
                    with batch_history_file.open("a", encoding="utf-8", newline="\n") as handle:
                        handle.write(render_summary(summary))
                        handle.flush()
                        os.fsync(handle.fileno())
                print("\n" + render_summary(summary), flush=True)
                print(f"[Batch] Appended comparison: {batch_history_file}", flush=True)
        return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only", action="store_true", help="Validate all four inputs and inspect GPU plans without inference/result writes")
    parser.add_argument("--limit", type=int, default=None, help="Optional first-N smoke test for each file; full runs reuse its cache")
    parser.add_argument("--summary-only", action="store_true", help="Summarize all four files from cache without starting judge workers")
    args = parser.parse_args()
    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be positive")
    config = single.JudgeConfig()
    if args.check_only:
        rows = preflight(JOBS, REFERENCE_JSONL)
        for row in rows:
            count = min(args.limit, row["num_samples"]) if args.limit else row["num_samples"]
            print(f"[CHECK] {row['label']}: aligned {row['num_samples']} questions; selected {count}; {row['input_file']}")
        if not Path(config.model_path).is_dir():
            print(f"Local judge not present: {config.model_path}; data passed, GPU readiness is NOT verified.")
            return 0
        single.fingerprint_model(Path(config.model_path))
        from gpu_runtime import discover_gpus, load_model_spec
        plans = single.plan_judge_execution(discover_gpus(), load_model_spec(Path(config.model_path)), config)
        print(json.dumps([{**plan.to_dict(), "max_num_seqs": seqs, "max_num_batched_tokens": prefill}
                          for seqs, prefill, plan in plans], indent=2))
        return 0 if plans else 1
    summary = run_batch(JOBS, reference_path=REFERENCE_JSONL, config=config, results_dir=RESULTS_DIR,
                        history_file=HISTORY_FILE, batch_history_file=BATCH_HISTORY_FILE,
                        limit=args.limit, summary_only=args.summary_only)
    return 130 if summary["interrupted"] else (0 if summary["complete"] else 1)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, RuntimeError, OSError) as error:
        print(f"ERROR: {error}", file=sys.stderr, flush=True)
        raise SystemExit(1)
