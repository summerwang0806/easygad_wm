#!/usr/bin/env python3
"""Easy/fast targeted student paraphrasing (TP) baseline.

paraphrase_tp.py rejects a whole-answer rewrite whenever it is truncated, shows
an obvious repetition loop, echoes the rewriting prompt, or leaves the source
answer unchanged, and then regenerates the row with a new seed.  On a small
student almost every attempt trips one of those gates, so a 14.5k-row baseline
needs many generations per row and days of GPU time.

This entrypoint keeps exactly the same model, rule table, prompt template,
sampling and command line, but uses a deliberately weaker acceptance policy for
a baseline:

* The first rewrite that contains any text is accepted.  Truncation at the
  per-row budget, a trimmed repetition tail, prompt/template echo, refusal and
  an unchanged answer are recorded as audit notes, not retry triggers.
* Echoed prompt scaffolding is stripped deterministically instead of rejecting
  the attempt.
* The only retry trigger is an empty (or echo-only) answer, and every row is
  generated at most --max-attempts times (default 3 = first try plus at most two
  retries).  If all attempts are empty the source answer is kept, so the run
  always finishes.
* Output length is capped per row at
  min(--max-new-tokens, max(256, 2 * source_tokens + 128)), the main speed win
  over the fixed 4096-token legacy budget.
* A clear repetition loop still stops decoding early, but the text produced so
  far is trimmed and accepted instead of discarded.

Durable checkpoints, --resume, multi-GPU workers, rule binding and the parquet
contract are reused from paraphrase_tp.py / paraphrase_up.py.  The checkpoint
format is specific to this script: use a new --output path rather than
--resume-ing a checkpoint written by the strict TP command.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict, dataclass, replace
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sys
import tempfile
import time

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from baseline_acl import paraphrase_tp as tp
from baseline_acl import paraphrase_up as up
from baseline_acl.inverse_watermark import TransformersInverseWatermarkProcessor, tokenizer_identity

GeneratedResponse = up.GeneratedResponse
GenerationConfig = tp.GenerationConfig

METHOD = "easy_targeted_student_paraphrasing"
FORMAT_VERSION = 1
POLICY = "easy-v1"
RETRY_ISSUES = frozenset({"empty_output"})
ECHO_MARKER = "Rewritten answer:"
SOURCE_OPEN = "<source_answer>"
SOURCE_CLOSE = "</source_answer>"
ECHO_ACTIONS = frozenset({"cut_echoed_source_block", "cut_echoed_template", "cut_instruction_echo"})

# The prompt is byte-identical to the strict TP baseline so the two runs differ
# only in acceptance policy, not in the instruction given to the student.
prepare_response = tp.prepare_response
prompt_ids = tp.prompt_ids
resolve_prompt_mode = tp.resolve_prompt_mode
output_budget = tp.output_budget


def policy_document(config) -> dict:
    """Deterministic description of what is accepted, for metadata and audit."""
    return {
        "policy": POLICY,
        "accepted_without_retry": [
            "truncated_at_budget",
            "repetition_loop (trimmed, kept)",
            "prompt_or_template_echo (stripped, kept)",
            "unchanged_source_answer",
            "refusal or editorial preface (noted only)",
        ],
        "retry_triggers": sorted(RETRY_ISSUES),
        "max_attempts": config.max_attempts,
        "retries_after_first_attempt": config.max_attempts - 1,
        "output_budget": f"min({config.max_new_tokens}, max(256, 2 * source_tokens + 128))",
        "exhausted_disposition": "keep original answer",
        "duplicate_generation_policy": "one generation per attempt, at most max_attempts attempts",
    }


def normalized(value: str) -> str:
    return " ".join(value.split())


def instruction_prefix(text: str) -> bool:
    """True when text is a (possibly truncated) copy of the rewriting instruction."""
    head = normalized(text)[:64]
    return bool(head) and normalized(tp.INSTRUCTION).startswith(head)


def clean_output(raw_text, prompt: str) -> tuple[str, list[str]]:
    """Strip echoed prompt scaffolding; never reject text for style.

    Returns ``(text, actions)``.  ``actions`` is a deterministic list of cleanup
    steps recorded in the durable generation audit.
    """
    actions = []
    text = raw_text.strip() if isinstance(raw_text, str) else ""
    if not text:
        return "", ["empty_generation"]
    if SOURCE_CLOSE in text:
        _, tail = text.rsplit(SOURCE_CLOSE, 1)
        if tail.strip():
            text = tail.strip()
            actions.append("cut_echoed_source_block")
    if ECHO_MARKER in text:
        head, tail = text.rsplit(ECHO_MARKER, 1)
        if not head.strip() or SOURCE_OPEN in head or SOURCE_CLOSE in head or instruction_prefix(head):
            text = tail.strip()
            actions.append("cut_echoed_template")
    text = re.sub(rf"^\s*{re.escape(SOURCE_OPEN)}\s*", "", text)
    text = re.sub(rf"^\s*(?:{re.escape(SOURCE_CLOSE)}|{re.escape(ECHO_MARKER)})\s*", "", text)
    text = re.sub(rf"\s*(?:{re.escape(SOURCE_CLOSE)}|{re.escape(ECHO_MARKER)})\s*$", "", text)
    text = text.strip()
    if not text:
        return "", actions + ["empty_after_cleanup"]
    if text.startswith(tp.INSTRUCTION):
        text = text[len(tp.INSTRUCTION):].strip()
        actions.append("cut_instruction_echo")
    if not text:
        return "", actions + ["empty_after_cleanup"]
    body, prompt_body = normalized(text), normalized(prompt)
    if len(body) >= 16 and prompt_body.startswith(body):
        return "", actions + ["prompt_echo_only"]
    return text, actions


def candidate_notes(raw_text, raw_reason, raw_notes, cleaned, source: str) -> list[str]:
    """Informational notes; none of them blocks acceptance."""
    notes = []
    if raw_reason == "length":
        notes.append("truncated_at_budget")
    for note in raw_notes or []:
        if isinstance(note, str) and note:
            notes.append(note)
    if not cleaned.strip() and isinstance(raw_text, str) and raw_text.strip():
        notes.append("empty_after_cleanup")
    if cleaned.strip():
        if normalized(cleaned) == normalized(source):
            notes.append("unchanged_source_answer")
        if up.REFUSAL_RE.search(cleaned) and not up.REFUSAL_RE.search(source):
            notes.append("refusal")
        if up.PREFACE_RE.search(cleaned) and not up.PREFACE_RE.search(source):
            notes.append("editorial_preface")
    return list(dict.fromkeys(notes))


def build_window(prepared, raw_text, raw_reason, raw_tokens, raw_notes, config, index, attempt) -> dict:
    """One reproducible generation audit record for a single attempt."""
    cleaned, cleanup = clean_output(raw_text, prepared["prompt"])
    tokens = raw_tokens if type(raw_tokens) is int else 0
    return {
        "source_sha256": up.text_sha256(prepared["source"]),
        "prompt_sha256": up.text_sha256(prepared["prompt"]),
        "input_tokens": prepared["prompt_tokens"],
        "source_tokens": prepared["source_tokens"],
        "seed": up.generation_seed(config.seed, index, attempt),
        "effective_max_new_tokens": output_budget(prepared["source_tokens"], config),
        "raw_output_text": raw_text if isinstance(raw_text, str) else "",
        "raw_finish_reason": raw_reason,
        "raw_notes": list(raw_notes or []),
        "output_text": cleaned,
        "output_tokens": tokens,
        "finish_reason": raw_reason,
        "cleanup_actions": cleanup,
        "notes": candidate_notes(raw_text, raw_reason, raw_notes, cleaned, prepared["source"]),
    }


def generate_response(prepared, raw, config, index, attempt) -> GeneratedResponse:
    """Convert a raw generation into the easy-policy result for one attempt."""
    if prepared["issues"]:
        return GeneratedResponse("", "input_limit", 0, [], list(prepared["issues"]))
    record = build_window(prepared, raw.text, raw.finish_reason, raw.output_tokens, raw.issues,
                          config, index, attempt)
    issues = sorted(RETRY_ISSUES) if not record["output_text"].strip() else []
    return GeneratedResponse(record["output_text"], record["finish_reason"], record["output_tokens"],
                             [record], issues)


def candidate_issues(candidate, source, config) -> list[str]:
    """The complete retry gate: only a rewrite with no usable text is retried."""
    issues = []
    if not isinstance(candidate.text, str) or not candidate.text.strip():
        issues.append("empty_output")
    return issues


def validate_audit(candidate, prepared, tokenizer, config, index, attempt) -> list[str]:
    """Recompute the attempt audit from the raw text and compare exactly."""
    if len(candidate.windows) != 1:
        return ["whole_answer_single_generation_required"]
    record = candidate.windows[0]
    expected = build_window(prepared, record.get("raw_output_text"), record.get("raw_finish_reason"),
                            record.get("output_tokens"), record.get("raw_notes"), config, index, attempt)
    issues = []
    if record != expected:
        issues.append("generation_audit_mismatch")
    if (candidate.text != expected["output_text"] or candidate.finish_reason != expected["finish_reason"]
            or candidate.output_tokens != expected["output_tokens"]):
        issues.append("output_reconstruction_mismatch")
    if len(prompt_ids(tokenizer, prepared["prompt"], config)) != prepared["prompt_tokens"]:
        issues.append("prompt_tokenization_changed")
    issues.extend(prepared["issues"])
    return list(dict.fromkeys(issues))


def metadata_builder(input_path, source, identity, config, prepared) -> dict:
    return {"kind": "meta", "format_version": FORMAT_VERSION,
            "input": {"path": str(input_path), "sha256": up.file_sha256(input_path), "rows": source.num_rows,
                      "schema_sha256": hashlib.sha256(source.schema.serialize().to_pybytes()).hexdigest()},
            "model": identity, "config": asdict(config),
            "easy_policy": policy_document(config),
            "input_template_sha256": up.text_sha256(tp.INSTRUCTION + tp.COMPLETION_TEMPLATE),
            "prompts_sha256": up.text_sha256(up.canonical_json([row["prompt"] for row in prepared])),
            "generation_contract": {"architecture": "causal_LM", "paraphrase_mode": "whole_response",
                                    "inputs_per_response": 1, "prompt_mode": config.prompt_mode,
                                    "max_new_tokens_excludes_prompt": True, "do_sample": True,
                                    "sentence_splitter": None, "prompt_truncation": False,
                                    "output_extraction": "new_tokens_only", "direct_token_id_bias": True,
                                    "acceptance_policy": POLICY, "retry_trigger": "empty_output",
                                    "max_attempts_includes_first_attempt": True}}


def attack_identity(args, rules, rules_hash) -> dict:
    attack = tp.attack_identity(args, rules, rules_hash)
    attack.update(method=METHOD, acceptance_policy=POLICY,
                  strict_checks="length/repetition/prompt-echo/unchanged are audit notes, not retries")
    return attack


def _window(record) -> dict:
    windows = record.get("windows") or []
    return windows[0] if windows else {}


def _read_checkpoint(path, expected_meta, source_values, ids):
    """Resume this script's own checkpoint; the settings must be identical."""
    config = GenerationConfig(**expected_meta["config"])
    complete, attempts, rejected, last_failure = {}, {}, [], {}
    with path.open("rb") as handle:
        lines = handle.readlines()
    if not lines or not lines[0].endswith(b"\n"):
        raise ValueError("checkpoint has no durable metadata header")
    header = json.loads(lines[0])
    if header != expected_meta:
        raise ValueError("checkpoint metadata differs from this run (input, model, rules, prompt or config); "
                         "resume with identical settings or choose a new --output")
    repair_size = None
    if not lines[-1].endswith(b"\n"):
        repair_size = sum(map(len, lines[:-1]))
        lines.pop()
        print("[resume] discarded an incomplete final checkpoint line", flush=True)
    for line in lines[1:]:
        entry = json.loads(line)
        kind = entry.get("kind")
        if kind not in ("result", "failure"):
            raise ValueError(f"invalid checkpoint record kind: {kind!r}")
        index = entry.get("row_index")
        if type(index) is not int or not 0 <= index < len(source_values):
            raise ValueError("invalid checkpoint row index")
        if entry.get("id") != ids[index] or entry.get("source_sha256") != up.text_sha256(source_values[index]):
            raise ValueError(f"checkpoint source mismatch at row {index}")
        if index in complete:
            raise ValueError(f"checkpoint has an attempt after completed row {index}")
        attempt = entry.get("attempt")
        budget_fallback = entry.get("status") == "fallback" and entry.get("finish_reason") == "not_generated"
        if budget_fallback:
            if attempt != 0 or entry.get("seed") is not None or index in attempts:
                raise ValueError("invalid input-budget fallback checkpoint")
        else:
            if (type(attempt) is not int or not 1 <= attempt <= config.max_attempts
                    or attempt != attempts.get(index, 0) + 1):
                raise ValueError(f"nonsequential or invalid checkpoint attempt at row {index}")
            if entry.get("seed") != up.generation_seed(config.seed, index, attempt):
                raise ValueError(f"checkpoint seed mismatch at row {index}")
            attempts[index] = attempt
        if kind == "failure":
            if entry.get("status") != "rejected" or not entry.get("issues"):
                raise ValueError(f"invalid rejected checkpoint attempt at row {index}")
            last_failure[index] = entry
            rejected.append(entry)
            continue
        status = entry.get("status")
        if status not in ("ok", "fallback"):
            raise ValueError(f"invalid completed checkpoint row {index}")
        if not isinstance(entry.get("paraphrase"), str) or not entry["paraphrase"].strip():
            raise ValueError(f"empty completed checkpoint row {index}")
        if status == "fallback":
            if (not budget_fallback and entry.get("paraphrase") != source_values[index]) or not entry.get("issues"):
                raise ValueError(f"invalid fallback at row {index}")
            if not budget_fallback and attempt != config.max_attempts:
                raise ValueError(f"invalid fallback attempt at row {index}")
        else:
            candidate = GeneratedResponse(entry["paraphrase"], entry.get("finish_reason"), entry.get("output_tokens"))
            windows = entry.get("windows")
            if (entry.get("issues") or candidate_issues(candidate, source_values[index], config)
                    or not isinstance(windows, list) or len(windows) != 1):
                raise ValueError(f"invalid accepted generation at checkpoint row {index}")
        complete[index] = entry
    # A crash between a final rejected attempt and its fallback is recoverable:
    # an exhausted row whose only failure is "no usable text" keeps the source.
    for index, failure in last_failure.items():
        if (index not in complete and attempts.get(index) == config.max_attempts
                and set(failure.get("issues", [])) <= RETRY_ISSUES
                and not (failure.get("candidate") or "").strip()):
            complete[index] = {**failure, "kind": "result", "status": "fallback",
                               "paraphrase": source_values[index]}
    if repair_size is not None:
        with path.open("r+b") as handle:
            handle.truncate(repair_size)
            handle.flush()
            os.fsync(handle.fileno())
    return complete, attempts, rejected, header


class EasyProgress:
    """Throttled progress: completed rows plus how many attempts were retried."""

    def __init__(self):
        self.counted = set()
        self.restored = None
        self.rejected_attempts = 0
        self.fallbacks = 0
        self.unchanged = 0
        self.truncated = 0
        self.repetition = 0
        self.echo_cleaned = 0
        self.last_print = 0.0

    def _count(self, index, record, source_values):
        key = (index, record.get("attempt"))
        if key in self.counted:
            return
        self.counted.add(key)
        if record.get("kind") != "result":
            self.rejected_attempts += 1
            return
        if record.get("paraphrase") == source_values[index]:
            self.unchanged += 1
        window = _window(record)
        notes = window.get("notes") or []
        if record.get("status") == "fallback":
            self.fallbacks += 1
            return
        if "truncated_at_budget" in notes:
            self.truncated += 1
        if "repetition_loop" in notes:
            self.repetition += 1
        if ECHO_ACTIONS.intersection(window.get("cleanup_actions") or []):
            self.echo_cleaned += 1

    def __call__(self, complete, source_values, *, record=None, started):
        if record is not None:
            self._count(record["row_index"], record, source_values)
        else:
            for index, item in complete.items():
                self._count(index, item, source_values)
        total, done = len(source_values), len(complete)
        if self.restored is None:
            self.restored = done
        now = time.monotonic()
        urgent = record is not None and record.get("kind") == "failure"
        if not (urgent or record is None or done == total or now - self.last_print >= 15.0):
            return
        self.last_print = now
        elapsed = max(now - started, 0.001)
        filled = 24 * done // total
        bar = "#" * filled + "-" * (24 - filled)
        delta = done - self.restored
        rate = delta / elapsed
        eta = f"{(total - done) / rate / 3600:.1f}h" if rate > 0 else "warming-up"
        detail = f", row={record['row_index']}, attempt={record['attempt']}" if record is not None else ""
        print(f"[TP-easy progress] [{bar}] completed={done}/{total} ({100 * done / total:.1f}%), "
              f"rejected_attempts={self.rejected_attempts}, fallbacks={self.fallbacks}, "
              f"unchanged={self.unchanged}, truncated={self.truncated}, "
              f"repetition_trimmed={self.repetition}, "
              f"echo_cleaned={self.echo_cleaned}{detail}, rate={rate * 3600:.1f}/h, eta={eta}, "
              f"elapsed={elapsed:.1f}s", flush=True)


def write_final_outputs(source, responses, records, rejected, output_path, audit_path, meta, started,
                        *, resume=False) -> dict:
    import pyarrow as pa
    import pyarrow.parquet as pq

    field = source.schema.get_field_index("teacher_response")
    result = source.set_column(field, source.schema.field(field),
                               pa.array(responses, type=source.schema.field(field).type))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(prefix=output_path.name + ".", suffix=".tmp",
                                     dir=output_path.parent, delete=False) as handle:
        parquet_temp = Path(handle.name)
    audit_temp = None
    try:
        pq.write_table(result, parquet_temp, compression="zstd")
        with parquet_temp.open("r+b") as handle:
            os.fsync(handle.fileno())
        reread = pq.read_table(parquet_temp)
        if reread.num_rows != source.num_rows or not reread.schema.equals(source.schema, check_metadata=True):
            raise AssertionError("written parquet row count/schema/metadata differs from source")
        protected = {name: reread[name].equals(source[name])
                     for name in source.column_names if name != "teacher_response"}
        if not all(protected.values()) or reread["teacher_response"].to_pylist() != responses:
            raise AssertionError("written parquet changed protected columns or accepted responses")

        original = source["teacher_response"].to_pylist()
        unchanged_rows = [i for i, (before, after) in enumerate(zip(original, responses, strict=True))
                          if before == after]
        fallback_rows = sorted(i for i, record in records.items() if record["status"] == "fallback")
        rejected_attempts = [record for record in rejected if record.get("kind") == "failure"]
        windows = [_window(record) for record in records.values()]
        note_counts = Counter(note for window in windows for note in window.get("notes", []))
        cleanup_counts = Counter(action for window in windows for action in window.get("cleanup_actions", []))
        accepted = [record for record in records.values() if record["status"] == "ok"]
        accepted_windows = [_window(record) for record in accepted]
        token_counts = [record["output_tokens"] for record in accepted
                        if type(record.get("output_tokens")) is int]
        budgets = [window["effective_max_new_tokens"] for window in windows
                   if type(window.get("effective_max_new_tokens")) is int]
        attempted = {(record["row_index"], record["attempt"]): record
                     for record in [*rejected, *records.values()] if record["attempt"] > 0}
        all_generations = [item for record in attempted.values() for item in record.get("windows", [])]
        report = {
            "format_version": FORMAT_VERSION, "complete": True, "method": METHOD,
            "acceptance_policy": POLICY, "easy_policy": policy_document(GenerationConfig(**meta["config"])),
            "metadata": meta, "input_sha256": meta["input"]["sha256"], "output": str(output_path.resolve()),
            "output_sha256": up.file_sha256(parquet_temp),
            "rows": source.num_rows, "processed_rows": len(records),
            "status_counts": dict(Counter(record["status"] for record in records.values())),
            "finish_reasons": dict(Counter(str(record["finish_reason"]) for record in records.values())),
            "accepted_attempts": dict(Counter(str(record["attempt"]) for record in records.values())),
            "rejected_generation_attempts": len(rejected_attempts),
            "rejected_attempt_reasons": dict(Counter(issue for record in rejected_attempts
                                                     for issue in record["issues"])),
            "fallback_rows": fallback_rows,
            "fallback_reasons": dict(Counter(issue for record in records.values()
                                             if record["status"] == "fallback" for issue in record["issues"])),
            "note_counts": dict(note_counts), "cleanup_counts": dict(cleanup_counts),
            "truncated_accepted_count": sum(1 for window in accepted_windows
                                            if "truncated_at_budget" in (window.get("notes") or [])),
            "repetition_trimmed_count": sum(1 for window in accepted_windows
                                            if "repetition_loop" in (window.get("notes") or [])),
            "prompt_echo_cleaned_count": sum(1 for window in accepted_windows
                                             if ECHO_ACTIONS.intersection(window.get("cleanup_actions") or [])),
            "unchanged_accepted_count": sum(1 for window in accepted_windows
                                            if "unchanged_source_answer" in (window.get("notes") or [])),
            "changed_teacher_responses": sum(a != b for a, b in zip(original, responses, strict=True)),
            "unchanged_teacher_responses": len(unchanged_rows),
            "unchanged_response_rows": unchanged_rows,
            "unchanged_response_ids": [source["id"][i].as_py() for i in unchanged_rows],
            "schema_and_metadata_equal": True, "row_order_and_ids_equal": True,
            "protected_columns_equal": protected,
            "output_tokens": ({"min": min(token_counts), "max": max(token_counts),
                               "mean": sum(token_counts) / len(token_counts)} if token_counts else None),
            "effective_max_new_tokens": ({"min": min(budgets), "max": max(budgets),
                                          "mean": sum(budgets) / len(budgets)} if budgets else None),
            "response_input_checks": len(all_generations),
            "generated_response_attempts": len(all_generations),
            "duration_seconds": round(time.monotonic() - started, 3),
            "paraphrase_mode": "whole_response",
            "semantic_preservation": "Requested by prompt; automatic checks do not prove factual equivalence",
            "parameter_provenance": ("Project TP variant: original student O paraphrases with the shared WN "
                                     "rules; easy baseline acceptance policy"),
        }
        if audit_path.exists():
            if not resume:
                raise FileExistsError(f"refusing to overwrite {audit_path}")
            previous = up.validate_orphan_audit(audit_path, output_path, meta, source.num_rows, len(records))
            comparable_previous, comparable_report = dict(previous), dict(report)
            comparable_previous.pop("duration_seconds", None)
            comparable_report.pop("duration_seconds", None)
            if comparable_previous != comparable_report:
                raise FileExistsError("existing audit verification/hash differs")
            report = previous
        else:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n",
                                             prefix=audit_path.name + ".", suffix=".tmp",
                                             dir=audit_path.parent, delete=False) as handle:
                audit_temp = Path(handle.name)
                handle.write(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
                handle.flush()
                os.fsync(handle.fileno())
            up.publish_new_file(audit_temp, audit_path)
            audit_temp = None
        up.publish_new_file(parquet_temp, output_path)
        print(f"[done] {output_path}: {source.num_rows} rows, unchanged={len(unchanged_rows)}, "
              f"fallbacks={len(fallback_rows)}, rejected_attempts={len(rejected_attempts)}, "
              f"truncated={report['truncated_accepted_count']}, "
              f"repetition_trimmed={report['repetition_trimmed_count']}, "
              f"echo_cleaned={report['prompt_echo_cleaned_count']}; audit: {audit_path}", flush=True)
        return report
    finally:
        parquet_temp.unlink(missing_ok=True)
        if audit_temp is not None:
            audit_temp.unlink(missing_ok=True)


def run_paraphrasing(input_path, output_path, config, tokenizer, generator_factory, identity, **kwargs):
    return up.run_paraphrasing(input_path, output_path, config, tokenizer, generator_factory, identity,
                               prepare_fn=prepare_response, candidate_issues_fn=candidate_issues,
                               validate_audit_fn=validate_audit, metadata_builder=metadata_builder,
                               final_writer=write_final_outputs, checkpoint_loader=_read_checkpoint,
                               keep_original_issues=RETRY_ISSUES,
                               progress_callback=EasyProgress(),
                               record_metadata={"generation_config": asdict(config)}, **kwargs)


def preflight_source(path, tokenizer, config) -> dict:
    report = tp.preflight_source(path, tokenizer, config)
    report["easy_policy"] = policy_document(config)
    report["budget_fallback_rows"] = report["invalid_rows"]
    report["budget_fallback_count"] = len(report["invalid_rows"])
    report["valid"] = True
    report["note"] = ("Easy TP keeps the source answer for rows whose complete prompt exceeds the input "
                      "budget; no text is truncated. Other rows are accepted on the first non-empty rewrite.")
    return report


def repeated_tail_width(tokens: list[int], max_width: int = 128) -> int:
    """Smallest block width repeated at least three times at the very end."""
    length = len(tokens)
    if length < 6:
        return 0
    for width in range(2, min(max_width, length // 3) + 1):
        block = tokens[-width:]
        if tokens[-2 * width:-width] == block and tokens[-3 * width:-2 * width] == block:
            return width
    return 0


def trim_repeated_tail(tokens: list[int], width: int) -> list[int]:
    """Drop the repeated copies; keep one copy of a sentence-sized block."""
    if width < 1 or len(tokens) < 3 * width:
        return tokens
    block = tokens[-width:]
    count = 1
    while len(tokens) >= (count + 1) * width and tokens[-(count + 1) * width:-count * width] == block:
        count += 1
    keep = 1 if width >= 8 else 0
    if count <= keep:
        return tokens
    return tokens[:len(tokens) - (count - keep) * width]


class EasyTailGuard:
    """Stop a clear repetition loop early; the produced text is kept, not rejected."""

    def __init__(self, prompt_length: int):
        self.prompt_length = prompt_length
        self.reason = None
        self.repeat_width = 0
        self.next_check = 32

    def __call__(self, input_ids, scores=None, **kwargs):
        if self.reason is not None:
            return True
        length = input_ids.shape[1] - self.prompt_length
        if length < self.next_check:
            return False
        self.next_check = length + 16
        suffix = input_ids[0, -min(length, 512):].tolist()
        width = repeated_tail_width(suffix)
        if width:
            self.reason, self.repeat_width = "repetition_loop", width
            return True
        return False


class EasyStudentGenerator(tp.StudentGenerator):
    """Student generator that returns the first non-empty rewrite for every attempt."""

    def generate_prompt(self, prompt, seed, *, max_new_tokens=None):
        torch, config = self.torch, self.config
        torch.manual_seed(seed)
        ids = prompt_ids(self.tokenizer, prompt, config)
        budget = config.max_new_tokens if max_new_tokens is None else max_new_tokens
        if len(ids) > config.max_input_tokens or len(ids) + budget > config.context_window:
            raise RuntimeError("full student prompt exceeds its prechecked input/context budget")
        inputs = torch.tensor([ids], dtype=torch.long, device="cuda:0")
        guard = EasyTailGuard(len(ids))
        with torch.inference_mode():
            sequence = self.model.generate(
                input_ids=inputs, attention_mask=torch.ones_like(inputs), do_sample=True,
                temperature=config.temperature, top_p=config.top_p, top_k=0,
                max_new_tokens=budget, logits_processor=[self.logits_processor],
                eos_token_id=sorted(self.eos_ids),
                pad_token_id=(self.tokenizer.pad_token_id if self.tokenizer.pad_token_id is not None
                              else min(self.eos_ids)),
                # A forced last EOS can conceal length truncation, so disable it.
                forced_eos_token_id=None, stopping_criteria=[guard], use_cache=True)
        tokens = sequence[0].tolist()
        if tokens[:len(ids)] != ids:
            raise RuntimeError("causal model returned an unexpected prompt prefix")
        new_tokens = tokens[len(ids):]
        reason = "stop" if new_tokens and new_tokens[-1] in self.eos_ids else "length"
        notes = []
        if guard.reason == "repetition_loop":
            new_tokens = trim_repeated_tail(new_tokens, guard.repeat_width)
            reason = "early_stop"
            notes.append("repetition_loop")
        text = self.tokenizer.decode(new_tokens, skip_special_tokens=True, clean_up_tokenization_spaces=False)
        return GeneratedResponse(text, reason, len(new_tokens), issues=notes)

    def generate(self, rows, indices, attempts):
        results = []
        for row, index, attempt in zip(rows, indices, attempts, strict=True):
            budget = output_budget(row["source_tokens"], self.config)
            raw = self.generate_prompt(row["prompt"], up.generation_seed(self.config.seed, index, attempt),
                                       max_new_tokens=budget)
            results.append(generate_response(row, raw, self.config, index, attempt))
        return results


@dataclass(frozen=True)
class EasyWorkerFactory:
    rules_path: str
    strength: float
    rules_sha256: str

    def __call__(self, model, config, tokenizer_path, gpu_id):
        from transformers import AutoTokenizer
        tokenizer = AutoTokenizer.from_pretrained(tokenizer_path, local_files_only=True, trust_remote_code=False)
        rules = tp.load_bound_rules(Path(self.rules_path), self.rules_sha256)
        rules.validate_tokenizer(tokenizer)
        tp.validate_original_student(rules, model)
        processor = TransformersInverseWatermarkProcessor(rules, strength=self.strength)
        return EasyStudentGenerator(model, config, tokenizer, logits_processor=processor)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--rules", type=Path, required=True)
    parser.add_argument("--model", required=True,
                        help="Local original student O used for --model-before during rule estimation")
    parser.add_argument("--tokenizer", help="Defaults to --model; must match the rule tokenizer fingerprint")
    parser.add_argument("--inverse-strength", type=float, default=2.5)
    parser.add_argument("--prompt-mode", choices=("auto", "completion", "chat"), default="completion",
                        help="Base O defaults to completion; explicit auto chooses chat solely when a chat template exists")
    parser.add_argument("--generation-policy", choices=("legacy", "efficient-v1"), default="efficient-v1",
                        help="Accepted for command-line compatibility; easy mode always uses the efficient "
                             "per-row output budget")
    parser.add_argument("--context-window", type=int,
                        help="Context cap no larger than model max_position_embeddings")
    parser.add_argument("--num-gpus", type=int)
    parser.add_argument("--workers-per-gpu", type=int, default=1,
                        help="Independent model replicas sharing each GPU; 2-3 usually lifts small-model "
                             "throughput without changing per-row seeds or generated text")
    parser.add_argument("--dtype", choices=("auto", "float32", "bfloat16"), default="auto")
    parser.add_argument("--batch-size", type=int, default=1,
                        help="Legacy progress-group size, not GPU count or tensor batch size")
    parser.add_argument("--max-input-tokens", type=int, default=4096)
    parser.add_argument("--max-new-tokens", type=int, default=4096,
                        help="Upper bound for the per-row budget min(max_new_tokens, max(256, 2*source+128))")
    parser.add_argument("--temperature", type=float, default=1.0)
    parser.add_argument("--top-p", type=float, default=0.75)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-attempts", type=int, choices=(1, 2, 3), default=3,
                        help="Total generations per row (default 3 = first attempt plus at most two retries); "
                             "only an empty rewrite is retried")
    parser.add_argument("--on-failure", choices=("error", "keep-original", "keep-last"),
                        default="keep-original",
                        help="Accepted for command-line compatibility; easy mode always keeps the source answer "
                             "when every attempt is empty, so a baseline run always finishes")
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--audit", type=Path)
    parser.add_argument("--resume", action="store_true")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--inspect", action="store_true", help="CPU source/rules inspection without Transformers")
    mode.add_argument("--preflight", action="store_true", help="CPU tokenizer identity and prompt/context checks")
    args = parser.parse_args(argv)
    args.tokenizer = args.tokenizer or args.model
    if not math.isfinite(args.inverse_strength) or args.inverse_strength < 0:
        parser.error("--inverse-strength must be finite and nonnegative")
    if args.num_gpus is not None and args.num_gpus < 1:
        parser.error("--num-gpus must be positive")
    if args.workers_per_gpu < 1:
        parser.error("--workers-per-gpu must be positive")
    if args.context_window is not None and args.context_window < 1:
        parser.error("--context-window must be positive")
    if not (args.inspect or args.preflight) and args.output is None:
        parser.error("--output is required for TP generation")
    return args


def main(argv=None):
    args = parse_args(argv)
    tp.validate_attack_paths(args)
    rules_hash = up.file_sha256(args.rules)
    rules = tp.load_bound_rules(args.rules, rules_hash)
    if args.inspect:
        report = up.inspect_source(args.input)
        tp.validate_rule_source(rules, report["input_sha256"])
        report.update(method=METHOD, acceptance_policy=POLICY, rules_sha256=rules_hash,
                      rules_tokenizer=rules.tokenizer, tokenizer_identity_checked=False,
                      cross_tokenizer=False, projection=None)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return report
    tp.validate_rule_source(rules, up.file_sha256(args.input))
    tp.validate_original_student(rules, args.model)
    up.asset_identity(args.tokenizer)
    from transformers import AutoConfig, AutoTokenizer
    model_config = AutoConfig.from_pretrained(args.model, local_files_only=True, trust_remote_code=False)
    if getattr(model_config, "is_encoder_decoder", False):
        raise ValueError("easy TP requires the original causal student, not an encoder-decoder paraphraser")
    native_context = getattr(model_config, "max_position_embeddings", None)
    if type(native_context) is not int or native_context < 1:
        raise ValueError("student config must expose max_position_embeddings for exact context budgeting")
    context = native_context if args.context_window is None else args.context_window
    if context > native_context:
        raise ValueError("--context-window cannot exceed the student's max_position_embeddings")
    tokenizer = AutoTokenizer.from_pretrained(args.tokenizer, local_files_only=True, trust_remote_code=False)
    rules.validate_tokenizer(tokenizer)
    if args.generation_policy != "efficient-v1":
        print(f"[easy] --generation-policy={args.generation_policy}: easy mode always uses the efficient "
              "per-row output budget", flush=True)
    args.generation_policy = "efficient-v1"
    if args.on_failure != "keep-original":
        print(f"[easy] --on-failure={args.on_failure}: easy mode always keeps the source answer when every "
              "attempt is empty", flush=True)
    args.on_failure = "keep-original"
    config = GenerationConfig(**{name: getattr(args, name) for name in GenerationConfig.__dataclass_fields__
                                 if hasattr(args, name) and name not in ("dtype", "prompt_mode", "context_window")},
                              dtype="float32" if args.dtype == "auto" else args.dtype,
                              prompt_mode=resolve_prompt_mode(tokenizer, args.prompt_mode), context_window=context)
    config.validate()
    attack = attack_identity(args, rules, rules_hash)
    if args.preflight:
        report = preflight_source(args.input, tokenizer, config)
        report.update(method=METHOD, attack=attack, tokenizer_identity_checked=True)
        print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)
        if report["budget_fallback_count"]:
            print(f"[easy] {report['budget_fallback_count']} rows exceed the complete prompt budget and will "
                  "keep their source answer", flush=True)
        return report
    checkpoint = args.checkpoint or args.output.with_suffix(args.output.suffix + ".progress.jsonl")
    audit = args.audit or args.output.with_suffix(args.output.suffix + ".audit.json")
    up.validate_output_paths(args.input, args.output, checkpoint, audit, args.resume)
    visible = up.parse_visible_gpus(os.environ.get("CUDA_VISIBLE_DEVICES"), args.num_gpus)
    identity = tp.model_identity(args.model, args.tokenizer)
    identity["attack"] = attack
    identity["tokenizer_fingerprint"] = tokenizer_identity(tokenizer)
    config = replace(config, dtype=up.select_dtype(args.dtype, up.probe_selected_gpus(visible)))
    from baseline_acl.student_parallel import ParallelStudentGenerator
    worker = EasyWorkerFactory(str(args.rules.resolve()), args.inverse_strength, rules_hash)
    factory = lambda: ParallelStudentGenerator(args.model, config, args.tokenizer, visible,
                                               worker_factory=worker,
                                               workers_per_gpu=args.workers_per_gpu)
    print(f"[TP-easy] policy={POLICY}; GPUs={visible}, workers={len(visible) * args.workers_per_gpu} "
          f"({args.workers_per_gpu}/GPU), dtype={config.dtype}, prompt={config.prompt_mode}, "
          f"max_attempts={config.max_attempts} (first try + up to {config.max_attempts - 1} retries)", flush=True)
    print("[TP-easy] accepts truncation, repeated text, prompt echo and unchanged answers; retries only an "
          "empty rewrite; per-row output budget=min(--max-new-tokens, max(256, 2*source_tokens+128))", flush=True)
    return run_paraphrasing(args.input, args.output, config, tokenizer, factory, identity,
                            resume=args.resume, checkpoint_path=checkpoint, audit_path=audit)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, RuntimeError, OSError, ImportError) as error:
        print(f"[error] {error}", file=sys.stderr, flush=True)
        sys.exit(1)
