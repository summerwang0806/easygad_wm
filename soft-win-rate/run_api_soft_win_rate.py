#!/usr/bin/env python3
"""Remote API pairwise judging; normally change only INPUT_JSONL.

Reuses text_quality's HTTP client and the local judge's pure scoring helpers.
No local model, CUDA, GPU inventory, tokenizer, or inference service is needed.
Running normally sends the saved question/answer pairs to the configured API.
"""
from __future__ import annotations

import argparse
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import json
import math
import os
from pathlib import Path
import random
import re
import sys
import threading
import time
from types import SimpleNamespace
from urllib import error
from urllib.parse import urlsplit
import uuid

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(ROOT / "text_quality") not in sys.path:
    sys.path.insert(0, str(ROOT / "text_quality"))
import evaluate_quality as quality
import run_soft_win_rate as common

# 日常只改这一行；相对路径以项目根目录为基准。
INPUT_JSONL = ROOT / "wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.jsonl"
REFERENCE_JSONL = common.REFERENCE_JSONL

# 沿用 text_quality/run_quality.sh；密钥不写入源代码或结果文件。
API_BASE_URL = "http://43.159.131.189:8080/v1"
JUDGE_MODEL = "gpt-5.5"
API_STYLE = "responses"
API_KEY_FILE = HERE / ".api_judge.key"
REASONING_EFFORT = "low"
MAX_OUTPUT_TOKENS = 4096
CONCURRENCY = 4
MAX_API_CALLS = 1500
REQUEST_TIMEOUT = 120
RETRIES = 2

RESULTS_DIR = HERE / "results" / "api"
HISTORY_FILE = HERE / "api_soft_win_rate_history.md"
SCHEMA = "api-fixed-reference-half-tie-preferences-v1"


def winner_schema() -> dict:
    return {"type": "object", "properties": {
        "winner": {"type": "string", "enum": ["A", "B", "tie"]},
        "reason": {"type": "string"}},
        "required": ["winner", "reason"], "additionalProperties": False}


@dataclass(frozen=True)
class APIConfig:
    base_url: str = API_BASE_URL
    judge_model: str = JUDGE_MODEL
    api_style: str = API_STYLE
    api_key_file: Path | None = API_KEY_FILE
    reasoning_effort: str = REASONING_EFFORT
    response_format: str = "json_schema"
    max_output_tokens: int = MAX_OUTPUT_TOKENS
    concurrency: int = CONCURRENCY
    max_api_calls: int = MAX_API_CALLS
    timeout: float = REQUEST_TIMEOUT
    retries: int = RETRIES
    rate_limit_base_delay: float = 30
    max_rate_limit_wait: float = 300
    max_consecutive_429: int = 6
    post_429_interval: float = 5
    bootstrap: int = 2000
    seed: int = 42

    def validate(self) -> None:
        url = urlsplit(self.base_url)
        if (url.scheme not in {"http", "https"} or not url.netloc or url.username or url.password
                or url.query or url.fragment):
            raise ValueError("API base URL must be http(s) without credentials, query parameters or fragments")
        if not isinstance(self.judge_model, str) or not self.judge_model.strip():
            raise ValueError("judge_model must be nonempty")
        if self.api_style not in {"responses", "chat_completions"}:
            raise ValueError("api_style must be responses or chat_completions")
        if self.response_format not in {"json_schema", "json_object", "text"}:
            raise ValueError("Unsupported response format")
        for name in ("max_output_tokens", "concurrency", "max_api_calls", "bootstrap", "max_consecutive_429"):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value < 1:
                raise ValueError(f"{name} must be a positive integer")
        if (not isinstance(self.retries, int) or isinstance(self.retries, bool) or self.retries < 0
                or not isinstance(self.timeout, (int, float)) or isinstance(self.timeout, bool)
                or not math.isfinite(self.timeout) or self.timeout <= 0):
            raise ValueError("Invalid retry count or request timeout")
        if self.reasoning_effort not in {"none", "low", "medium", "high", "xhigh"}:
            raise ValueError("Invalid reasoning effort")
        for name in ("rate_limit_base_delay", "max_rate_limit_wait", "post_429_interval"):
            value = getattr(self, name)
            if (not isinstance(value, (int, float)) or isinstance(value, bool)
                    or not math.isfinite(value) or value < 0):
                raise ValueError(f"{name} must be finite and nonnegative")

    def public_dict(self) -> dict:
        return {**asdict(self), "api_key_file": str(self.api_key_file) if self.api_key_file else None}

    def payload(self, messages: list[dict]) -> dict:
        structured = {"type": "json_schema", "name": "pairwise_preference", "strict": True,
                      "schema": winner_schema()}
        if self.api_style == "responses":
            payload = {"model": self.judge_model, "input": messages, "store": False,
                       "max_output_tokens": self.max_output_tokens, "reasoning": {"effort": self.reasoning_effort}}
            if self.response_format != "text":
                payload["text"] = {"format": structured if self.response_format == "json_schema" else {"type": "json_object"}}
            return payload
        payload = {"model": self.judge_model, "messages": messages, "temperature": 0, "store": False,
                   "max_tokens": self.max_output_tokens}
        if self.response_format == "json_schema":
            payload["response_format"] = {"type": "json_schema", "json_schema": {
                key: value for key, value in structured.items() if key != "type"}}
        elif self.response_format == "json_object":
            payload["response_format"] = {"type": "json_object"}
        return payload


class APIRateLimitError(RuntimeError):
    def __init__(self, details: dict):
        self.details = details
        super().__init__("API HTTP 429: " + rate_limit_summary(details))


def rate_limit_summary(details: dict) -> str:
    return (f"category={details['category']}, provider_code={details.get('provider_code') or 'not supplied'}, "
            f"provider_type={details.get('provider_type') or 'not supplied'}, "
            f"provider_reason={details.get('provider_reason') or 'not supplied'}")


def parse_rate_limit_error(body: bytes, headers, secret: str = "") -> dict:
    """Classify errors without printing/saving provider messages or credentials."""
    try:
        data = json.loads(body)
    except (ValueError, TypeError):
        data = {}
    if not isinstance(data, dict):
        data = {}
    nested = data.get("error")
    detail = nested if isinstance(nested, dict) else data
    code, kind = detail.get("code"), detail.get("type")
    message = detail.get("message") or detail.get("msg") or (nested if isinstance(nested, str) else "")
    hint = " ".join(str(value) for value in (code, kind, message) if value is not None).casefold()
    quota_codes = {"insufficient_quota", "billing_hard_limit_reached", "insufficient_balance",
                   "credit_balance_exhausted", "organization_spend_limit_exceeded", "project_spend_limit_exceeded",
                   "organization_usage_limit_exceeded"}
    if str(code).lower() in quota_codes or str(kind).lower() in quota_codes or any(word in hint for word in (
            "insufficient quota", "insufficient balance", "credit balance exhausted", "余额不足")):
        category = "quota"
    elif "request too large" in hint and any(word in hint for word in ("tpm", "tokens per min", "token rate")):
        category = "request_too_large"
    elif any(word in hint for word in ("no available channel", "no available provider", "no available upstream",
            "no available route", "no active channel", "无可用渠道", "无可用通道", "没有可用渠道", "渠道不可用",
            "通道不可用", "当前分组无可用模型")):
        category = "capacity"
    elif any(word in hint for word in ("rate_limit", "rate limit", "slow_down", "too many requests", "rpm", "tpm",
                                      "限流", "速率", "请求过于频繁", "请求频率", "并发限制", "每分钟", "每秒")):
        category = "rate_limit"
    elif any(word in hint for word in ("额度不足", "配额不足", "quota exhausted")):
        category = "quota"
    else:
        category = "unknown_429"

    def identifier(value):
        if value is None:
            return None
        text = str(value)
        if (secret and secret in text) or text.lower().startswith(("sk-", "sess-", "bearer ")):
            return "redacted"
        return text if re.fullmatch(r"[A-Za-z0-9_.:-]{1,100}", text) else "unrecognized"

    retry_after = None
    if headers is not None:
        value = headers.get("Retry-After") or headers.get("retry-after")
        if value:
            try:
                retry_after = float(value)
            except (ValueError, TypeError):
                try:
                    date = parsedate_to_datetime(value)
                    if date.tzinfo is None:
                        date = date.replace(tzinfo=timezone.utc)
                    retry_after = (date - datetime.now(timezone.utc)).total_seconds()
                except (ValueError, TypeError, OverflowError):
                    pass
        milliseconds = headers.get("retry-after-ms")
        if milliseconds:
            try:
                hint_seconds = float(milliseconds) / 1000
                if math.isfinite(hint_seconds):
                    retry_after = max(retry_after or 0, hint_seconds)
            except (ValueError, TypeError):
                pass
    if retry_after is not None:
        retry_after = max(0.0, retry_after) if math.isfinite(retry_after) else None
    provider_reason = ("all_upstream_accounts_rate_limited" if "all available accounts" in hint
                       and any(word in hint for word in ("rate-limited", "rate limited", "rate_limit")) else None)
    return {"http_status": 429, "category": category, "provider_reason": provider_reason, "provider_code": identifier(code),
            "provider_type": identifier(kind), "retry_after_seconds": retry_after}


class PreferenceAPIClient(quality.APIClient):
    def __init__(self, config: APIConfig):
        self.config = config
        # Keep this evaluator's new key separate from the old text_quality key.
        # A missing configured file must not silently select another account.
        key_file = Path(config.api_key_file).expanduser() if config.api_key_file else None
        if key_file is not None and not key_file.is_file():
            raise ValueError(f"API key file not found: {key_file}; create it with the new key")
        if key_file is None and not os.environ.get("OPENAI_API_KEY", "").strip():
            raise ValueError("API key missing: set OPENAI_API_KEY or configure a key file")
        args = SimpleNamespace(base_url=config.base_url, judge_model=config.judge_model,
            api_style=config.api_style, api_key_file=key_file,
            run_api=True, backend="api", max_api_calls=config.max_api_calls, timeout=config.timeout,
            retries=config.retries, judge_max_tokens=config.max_output_tokens,
            reference_max_tokens=config.max_output_tokens, reasoning_effort=config.reasoning_effort,
            response_format=config.response_format)
        super().__init__(args)
        if not self.key.strip():
            raise ValueError("API key file is empty")
        if any(character.isspace() for character in self.key):
            raise ValueError("API key must be a single token, without embedded whitespace")
        self._rate_condition = threading.Condition()
        self._active_requests = 0
        self._limited = False
        self._cooldown_until = self._next_start = 0.0
        self._rate_epoch = self._cooldown_rounds = self._consecutive_429 = 0
        self._last_rate_limit = None
        self.fatal_reason = None
        self.credential_source = str(key_file) if key_file else "environment:OPENAI_API_KEY"

    def stop_with_reason(self, message: str) -> None:
        with self._rate_condition:
            if not self.fatal_reason:
                self.fatal_reason = message
            self.stop.set()
            self._rate_condition.notify_all()

    def rate_limit_status(self) -> dict:
        with self._rate_condition:
            return {"cooldown_seconds": max(0.0, self._cooldown_until - time.monotonic()),
                    "effective_concurrency": 1 if self._limited else self.config.concurrency,
                    "consecutive_429": self._consecutive_429, "last_rate_limit": self._last_rate_limit}

    def _enter_http(self) -> int:
        with self._rate_condition:
            while True:
                if self.stop.is_set():
                    raise quality.FatalAPIError(self.fatal_reason or "Stopping; successful judgments remain cached")
                now = time.monotonic()
                delay = max(self._cooldown_until, self._next_start) - now
                cap = 1 if self._limited else self.config.concurrency
                if delay <= 0 and self._active_requests < cap:
                    self._active_requests += 1
                    if self._limited:
                        self._next_start = now + self.config.post_429_interval
                    return self._rate_epoch
                self._rate_condition.wait(timeout=min(delay, .25) if delay > 0 else .25)

    def _record_429(self, details: dict, epoch: int) -> None:
        with self._rate_condition:
            if not self._limited or epoch == self._rate_epoch:
                self._rate_epoch += 1
                self._cooldown_rounds += 1
            self._limited = True
            self._consecutive_429 += 1
            self._last_rate_limit = details
            category = details["category"]
            summary = rate_limit_summary(details)
            if category == "quota":
                reason = "API provider reports exhausted quota/balance/spend limit: " + summary
            elif category == "request_too_large":
                reason = "One API request exceeds the provider's token-rate limit; waiting or concurrency alone may not fix it: " + summary
            elif self._consecutive_429 >= self.config.max_consecutive_429:
                reason = f"API returned {self._consecutive_429} consecutive HTTP 429 responses; stopped new requests: " + summary
            elif (details["retry_after_seconds"] or 0) > self.config.max_rate_limit_wait:
                reason = f"API requests waiting at least {details['retry_after_seconds']:.0f}s; stopped instead of retrying early: " + summary
            else:
                reason = None
            if reason:
                self.stop_with_reason(reason)
                raise quality.FatalAPIError(reason)
            delay = max(details["retry_after_seconds"] or 0,
                        min(self.config.max_rate_limit_wait,
                            self.config.rate_limit_base_delay * 2 ** max(0, min(self._cooldown_rounds - 1, 12))))
            self._cooldown_until = max(self._cooldown_until, time.monotonic() + delay)
            self._rate_condition.notify_all()
            print(f"[API 429] {summary}; all workers cooling down for at least {delay:.1f}s; "
                  "subsequent HTTP requests use concurrency=1.", file=sys.stderr, flush=True)

    def _record_success(self, epoch: int) -> None:
        with self._rate_condition:
            # A late response started BEFORE a 429 remains valid, but must not
            # release the new global cooldown or reset its failure streak.
            if epoch == self._rate_epoch:
                self._consecutive_429 = self._cooldown_rounds = 0
                self._cooldown_until = 0

    def payload(self, messages: list[dict], judging: bool = True) -> dict:
        return self.config.payload(messages)

    def complete(self, payload: dict) -> dict:
        epoch = self._enter_http()
        try:
            response = super().complete(payload)
            self._record_success(epoch)
            return response
        except RuntimeError as exc:
            cause = exc.__cause__
            if isinstance(cause, error.HTTPError) and cause.code == 429:
                try:
                    body = cause.read(65536)
                except OSError:
                    body = b""
                details = parse_rate_limit_error(body, cause.headers, self.key)
                self._record_429(details, epoch)
                raise APIRateLimitError(details) from cause
            if isinstance(exc, quality.FatalAPIError):
                self.stop_with_reason(str(exc))
            raise
        finally:
            with self._rate_condition:
                self._active_requests -= 1
                self._rate_condition.notify_all()


def prepare(input_path: Path, reference_path: Path, config: APIConfig, output_dir: Path,
            limit: int | None = None) -> dict:
    config.validate()
    if limit is not None and (not isinstance(limit, int) or isinstance(limit, bool) or limit < 1):
        raise ValueError("limit must be a positive integer")
    input_path, reference_path = input_path.resolve(), reference_path.resolve()
    hashes = {str(path): common.file_hash(path) for path in (input_path, reference_path)}
    candidate, reference = common.load_answers(input_path), common.load_answers(reference_path)
    ids = common.align_answers(candidate, reference)
    selected = ids[:limit] if limit else ids
    generation = {"input_generation": common.describe_dataset(candidate),
                  "reference_generation": common.describe_dataset(reference)}
    # Runtime budgets, concurrency, retries, credentials and --limit do not
    # change logical judgments; model/endpoint/payload/rubric changes do.
    protocol = {"schema": SCHEMA, "task_schema": common.SCHEMA,
        "endpoint": config.base_url.rstrip("/") + ("/responses" if config.api_style == "responses" else "/chat/completions"),
        "request_template": config.payload([]), "rubric": common.JUDGE_SYSTEM,
        "input_sha256": hashes[str(input_path)], "reference_sha256": hashes[str(reference_path)]}
    identity = common.digest(protocol)
    stem = re.sub(r"[^\w.-]", "_", input_path.stem)[:64]
    directory = output_dir.resolve() / (stem + "." + identity[:16])
    all_tasks = common.make_tasks(candidate, reference, ids, identity)
    selected_set = set(selected)
    return {"candidate": candidate, "reference": reference, "ids": ids, "selected": selected, **generation,
            "tasks": [task for task in all_tasks if task["id"] in selected_set], "all_tasks": all_tasks,
            "input_path": input_path, "reference_path": reference_path, "hashes": hashes,
            "protocol": protocol, "directory": directory}


def load_cache(path: Path, tasks: dict) -> dict:
    rows = {}
    for row in common.complete_jsonl_rows(path, repair_tail=True):
        task = tasks.get(row.get("key"))
        if (task is None or row["key"] in rows or row.get("id") != task["id"]
                or row.get("swapped") != task["swapped"] or row.get("finish_reason") != "stop"
                or row.get("judgment") != common.parse_judgment(row.get("text"))
                or row.get("preference") != common.preference(task, row["judgment"])):
            raise ValueError(f"Invalid or duplicate API judgment cache: {path}")
        rows[row["key"]] = row
    return rows


def score_pending(tasks: list[dict], rows: dict, cache_file: Path, config: APIConfig,
                  client, events_file: Path) -> dict:
    """Bound in-flight requests; persist each valid result inside its worker."""
    lock = threading.RLock()
    failures, latencies = [], []
    ready = threading.Event()
    started = last_progress = time.monotonic()
    fatal, interrupted = None, False
    rng = random.Random(config.seed)

    def score(task):
        for attempt in range(config.retries + 1):
            if client.stop.is_set():
                return
            request_started = time.monotonic()
            try:
                response = client.complete(config.payload(task["messages"]))
                judgment = common.parse_judgment(response["content"])
                usage = response.get("usage") or {}
                if not isinstance(usage, dict) or any(response.get(name) is not None and not isinstance(response[name], str)
                                                      for name in ("actual_model", "response_id")):
                    raise ValueError("Malformed API response metadata")
                row = {"key": task["key"], "id": task["id"], "swapped": task["swapped"],
                    "text": response["content"], "judgment": judgment, "finish_reason": "stop",
                    "preference": common.preference(task, judgment), "usage": usage,
                    "actual_model": response.get("actual_model"), "response_id": response.get("response_id"),
                    "attempts": attempt + 1, "at": common.now(),
                    "seconds": round(time.monotonic() - request_started, 3)}
                with lock:
                    try:
                        common.append_jsonl(cache_file, row)
                    except OSError:
                        client.stop.set()
                        raise quality.FatalAPIError("Cannot write API judgment cache; stopped new requests") from None
                    rows[task["key"]] = row
                    latencies.append(row["seconds"])
                    ready.set()
                return
            except quality.FatalAPIError:
                client.stop.set()
                raise
            except (ValueError, KeyError, IndexError, RuntimeError, error.URLError, TimeoutError, OSError) as exc:
                # Do not serialize exception text or provider bodies into logs.
                cause = exc.__cause__
                http_status = cause.code if isinstance(cause, error.HTTPError) else None
                rate_error = isinstance(exc, APIRateLimitError)
                with lock:
                    common.append_jsonl(events_file, {"key": task["key"], "id": task["id"],
                        "swapped": task["swapped"], "attempt": attempt + 1,
                        "error_type": type(exc).__name__, "http_status": http_status,
                        "api_error": exc.details if rate_error else None, "at": common.now()})
                    if attempt == config.retries:
                        failures.append(task["key"])
                if attempt == config.retries:
                    if rate_error or not ready.is_set():
                        reason = ("API kept returning 429 after bounded retries; stopped before trying other texts: "
                                  + rate_limit_summary(exc.details)) if rate_error else (
                                  f"Initial API judgment failed after retries ({type(exc).__name__}, HTTP={http_status}); "
                                  "stopped before launching the full dataset")
                        if hasattr(client, "stop_with_reason"):
                            client.stop_with_reason(reason)
                        else:
                            client.stop.set()
                        raise quality.FatalAPIError(reason) from None
                    print(f"[API WARNING] id={task['id']!r}, swapped={task['swapped']}: "
                          f"{type(exc).__name__}, HTTP={http_status}; retries exhausted, continuing.", file=sys.stderr, flush=True)
                    return
                if rate_error:
                    continue  # The client's shared HTTP gate owns 429 backoff.
                client.stop.wait(min(5 * 2 ** attempt, 60) + rng.random())

    executor = ThreadPoolExecutor(max_workers=config.concurrency)
    queue = iter(tasks)
    futures = set()

    def fill():
        # Verify ONE real judgment with this account/model before the full
        # queue, without buying an extra synthetic health-check request.
        cap = config.concurrency if ready.is_set() else 1
        while not client.stop.is_set() and len(futures) < cap:
            task = next(queue, None)
            if task is None:
                return
            futures.add(executor.submit(score, task))

    try:
        fill()
        print(f"[API] {len(tasks)} missing orders; first real judgment is a single readiness probe; "
              f"then concurrency<={config.concurrency}; request budget={config.max_api_calls}", flush=True)
        while futures:
            done, _ = wait(futures, timeout=5, return_when=FIRST_COMPLETED)
            for future in done:
                futures.remove(future)
                try:
                    future.result()
                except quality.FatalAPIError as exc:
                    fatal = fatal or str(exc)
                    client.stop.set()
                except Exception as exc:
                    fatal = f"API worker failed: {type(exc).__name__}"
                    client.stop.set()
            fill()
            if time.monotonic() - last_progress >= 5 or not futures:
                with lock:
                    completed = sum(task["key"] in rows for task in tasks)
                    failed = len(failures)
                with client.call_lock:
                    calls = client.calls
                elapsed = time.monotonic() - started
                status = client.rate_limit_status() if hasattr(client, "rate_limit_status") else {}
                rate_note = (f"; effective_concurrency={status['effective_concurrency']}; "
                             f"cooldown={status['cooldown_seconds']:.0f}s; 429_streak={status['consecutive_429']}") if status else ""
                print(f"[API] |{'#' * (20 * completed // len(tasks))}{'-' * (20 - 20 * completed // len(tasks))}| "
                      f"{completed}/{len(tasks)} new orders saved; requests={calls}/{config.max_api_calls}; "
                      f"inflight={len(futures)}; failed={failed}; elapsed={elapsed:.0f}s{rate_note}", flush=True)
                last_progress = time.monotonic()
    except KeyboardInterrupt:
        interrupted, fatal = True, "Interrupted by user; saved judgments can be resumed"
        client.stop.set()
        print("[API] Stopping new requests; allowing in-flight replies to be cached (up to request timeout).", flush=True)
    finally:
        for future in futures:
            future.cancel()
        executor.shutdown(wait=True, cancel_futures=True)
    fatal = getattr(client, "fatal_reason", None) or fatal
    if not fatal and failures:
        fatal = f"{len(failures)} orders exhausted retries; successful judgments remain cached"
    return {"failure": fatal, "interrupted": interrupted, "api_calls": client.calls,
            "rate_limit_status": client.rate_limit_status() if hasattr(client, "rate_limit_status") else None,
            "failed_orders_this_run": len(failures), "elapsed_seconds": round(time.monotonic() - started, 2),
            "mean_successful_request_seconds": sum(latencies) / len(latencies) if latencies else None}


def render_report(result: dict) -> str:
    pct = lambda value: f"{value:.2%}" if value is not None else "N/A"
    ci = result["ci95"]
    interval = f"[{pct(ci[0])}, {pct(ci[1])}]" if ci else "N/A"
    lines = [f"\n## API 评测记录：{result['evaluated_at']}（{result['run_id']}）", "",
        f"- 待测文件：`{result['input_file']}`；SHA256 `{result['input_sha256']}`",
        f"- 固定 clean 参照：`{result['reference_file']}`；SHA256 `{result['reference_sha256']}`",
        f"- API 裁判：`{result['api_configuration']['judge_model']}`；接口：`{result['protocol']['endpoint']}`",
        f"- 返回的模型标识：`{', '.join(result['actual_model_ids']) or '未提供'}`；只评已保存回答，无本地模型加载。", "",
        "| 半平局胜率 ↑ | 95% CI | 胜＋平比例 ↑ | 完整题目 | 单轮胜/平/负 | 双顺序一致率 | 复用/新增判断 | API请求数 |",
        "|---:|---|---:|---:|---|---:|---:|---:|",
        f"| {pct(result['soft_win_rate'])} | {interval} | {pct(result['win_plus_tie_rate'])} | "
        f"{result['num_valid_samples']}/{result['num_samples']} | {pct(result['strict_win_rate'])} / "
        f"{pct(result['tie_rate'])} / {pct(result['loss_rate'])} | {pct(result['order_agreement_rate'])} | "
        f"{result['cache_reused_rounds']}/{result['new_judgments']} | {result['api_calls']} |", "",
        "每题匿名交换 A/B 两次。每轮胜=1、平=0.5、负=0，先平均同题两轮，再平均完整题目。"
        "胜＋平比例另按单轮胜和平都记 1 计算；两者不是同一指标，50% 也不是正确率。",
        f"本次完整评测：{result['complete']}；覆盖率：{pct(result['coverage'])}。"
        "拒答、截断、无效 JSON 和缺少任一顺序的题目均不记为平局。",
        f"逐条缓存：`{result['cache_file']}`；本轮完整 JSON：`{result['run_file']}`。", ""]
    if result.get("failure"):
        lines += [f"本次未完成：{result['failure']}。成功判断已经保存。", ""]
    lines += ["API 配置、生成配置与使用量（不含密钥）：", "", "```json", json.dumps({
        "api_configuration": result["api_configuration"], "input_generation": result["input_generation"],
        "reference_generation": result["reference_generation"], "usage_in_successful_cache": result["usage_in_successful_cache"],
        "rate_limit_status": result.get("rate_limit_status"), "credential_source": result.get("credential_source"),
        "elapsed_seconds": result["elapsed_seconds"], "failed_orders_this_run": result["failed_orders_this_run"],
        "rubric_sha256": common.digest(common.JUDGE_SYSTEM)}, ensure_ascii=False, indent=2), "```", ""]
    return "\n".join(lines)


def run_evaluation(input_path: Path, reference_path: Path, config: APIConfig, output_dir: Path,
                   history_file: Path, *, limit: int | None = None, summary_only: bool = False,
                   client_factory=None) -> dict:
    prepared = prepare(input_path, reference_path, config, output_dir, limit)
    directory = prepared["directory"]
    history_file = history_file.resolve()
    protected = {prepared["input_path"], prepared["reference_path"]}
    if config.api_key_file:
        protected.add(Path(config.api_key_file).expanduser().resolve())
    if history_file in protected:
        raise ValueError("History must not overwrite input/reference/API-key files")
    directory.mkdir(parents=True, exist_ok=True)
    cache_file = directory / "judgments.jsonl"
    by_key = {task["key"]: task for task in prepared["all_tasks"]}
    with common.evaluation_lock(directory / ".run.lock"):
        manifest = directory / "manifest.json"
        if manifest.exists() and json.loads(manifest.read_text(encoding="utf-8")) != prepared["protocol"]:
            raise ValueError("API result directory contains another input/reference/judge protocol")
        if not manifest.exists():
            manifest.write_text(json.dumps(prepared["protocol"], ensure_ascii=False, indent=2), encoding="utf-8")
            (directory / "tasks.jsonl").write_text("".join(common.canonical(task) + "\n" for task in prepared["all_tasks"]), encoding="utf-8")
        rows = load_cache(cache_file, by_key)
        chosen = prepared["tasks"]
        reused = sum(task["key"] in rows for task in chosen)
        pending = [task for task in chosen if task["key"] not in rows]
        print(f"[API] Aligned {len(prepared['ids'])} questions; selected {len(prepared['selected'])}; "
              f"cached={reused}/{len(chosen)} orders; uncached={len(pending)}", flush=True)
        runtime = {"failure": None, "interrupted": False, "api_calls": 0, "failed_orders_this_run": 0,
                   "elapsed_seconds": 0, "mean_successful_request_seconds": None}
        if pending and not summary_only:
            client = (client_factory or PreferenceAPIClient)(config)
            print(f"[API] endpoint={prepared['protocol']['endpoint']}; model={config.judge_model}; "
                  f"key_source={getattr(client, 'credential_source', 'injected client')}", flush=True)
            try:
                runtime = score_pending(pending, rows, cache_file, config, client, directory / "errors.jsonl")
                runtime["credential_source"] = getattr(client, "credential_source", None)
            finally:
                client.close()
        if any(common.file_hash(Path(path)) != sha for path, sha in prepared["hashes"].items()):
            raise RuntimeError("Input/reference changed during API judging; no summary was published")
        metrics = common.summarize_judgments(chosen, {key: row["judgment"] for key, row in rows.items()}, config.bootstrap, config.seed)
        selected_rows = [rows[task["key"]] for task in chosen if task["key"] in rows]
        # Keep the extra win+tie statistic explicit; the main metric stays half-tie.
        win_plus_tie = None if metrics["strict_win_rate"] is None else metrics["strict_win_rate"] + metrics["tie_rate"]
        usage = {name: sum(row.get("usage", {}).get(name, 0) or 0 for row in selected_rows)
                 for name in ("prompt_tokens", "completion_tokens", "total_tokens")}
        run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + uuid.uuid4().hex[:8]
        runs = directory / "runs"
        runs.mkdir(exist_ok=True)
        run_file = runs / (run_id + ".json")
        result = {**metrics, **runtime, "schema": SCHEMA, "protocol": prepared["protocol"],
            "run_id": run_id, "evaluated_at": common.now(), "summary_only": summary_only,
            "input_file": str(prepared["input_path"]), "reference_file": str(prepared["reference_path"]),
            "input_sha256": prepared["hashes"][str(prepared["input_path"])],
            "reference_sha256": prepared["hashes"][str(prepared["reference_path"])],
            "api_configuration": config.public_dict(), "cache_reused_rounds": reused,
            "new_judgments": sum(task["key"] in rows for task in chosen) - reused,
            "actual_model_ids": sorted({row["actual_model"] for row in selected_rows if row.get("actual_model")}),
            "usage_in_successful_cache": usage, "win_plus_tie_rate": win_plus_tie,
            "input_generation": prepared["input_generation"],
            "reference_generation": prepared["reference_generation"],
            "cache_file": str(cache_file), "run_file": str(run_file)}
        run_file.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
        history_file.parent.mkdir(parents=True, exist_ok=True)
        with common.evaluation_lock(history_file.with_suffix(history_file.suffix + ".lock")):
            with history_file.open("a", encoding="utf-8", newline="\n") as handle:
                handle.write(render_report(result))
                handle.flush()
                os.fsync(handle.fileno())
        print(f"[API] Soft Win Rate={metrics['soft_win_rate']:.2%}; complete={metrics['complete']}" if metrics["soft_win_rate"] is not None
              else "[FAILED] No complete answer pairs; no valid API Soft Win Rate.", flush=True)
        if runtime["failure"]:
            print(f"[API ERROR] {runtime['failure']}", file=sys.stderr, flush=True)
        print(f"Appended: {history_file}", flush=True)
        return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-file", type=Path, default=INPUT_JSONL)
    parser.add_argument("--check-only", action="store_true", help="Validate data/configuration without reading the API key or calling the API")
    parser.add_argument("--summary-only", action="store_true", help="Summarize existing API cache without credentials or network")
    parser.add_argument("--limit", type=int, default=None, help="Optional first-N smoke test; full runs reuse successful judgments")
    args = parser.parse_args(argv)
    path = args.input_file if args.input_file.is_absolute() else ROOT / args.input_file
    config = APIConfig()
    if args.check_only:
        prepared = prepare(path, REFERENCE_JSONL, config, RESULTS_DIR, args.limit)
        print(f"[CHECK] Aligned {len(prepared['ids'])} IDs; selected {len(prepared['selected'])}; "
              f"up to {len(prepared['tasks'])} uncached logical API judgments (retries extra).")
        print(f"Fixed reference: {REFERENCE_JSONL}\nAPI judge: {config.judge_model}; style={config.api_style}; concurrency={config.concurrency}")
        print("CHECK ONLY: no API key read, no network requests, no GPU/model loading, no result writes.")
        return 0
    result = run_evaluation(path, REFERENCE_JSONL, config, RESULTS_DIR, HISTORY_FILE,
                            limit=args.limit, summary_only=args.summary_only)
    return 130 if result["interrupted"] else (0 if result["complete"] else 1)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, RuntimeError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr, flush=True)
        raise SystemExit(1)
