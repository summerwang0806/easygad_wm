"""Rate-limit recovery regressions using fake HTTP replies and private test keys."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import contextlib
from dataclasses import replace
from datetime import datetime, timezone
from email.utils import format_datetime
import io
import json
from pathlib import Path
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "soft-win-rate") not in sys.path:
    sys.path.insert(0, str(ROOT / "soft-win-rate"))
import run_api_soft_win_rate as api


class Reply(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def successful_reply():
    return Reply(json.dumps({"status": "completed", "model": "fake-rate-limit-judge", "id": "fake-response",
        "output": [{"type": "message", "content": [{"type": "output_text",
            "text": '{"winner":"tie","reason":"Test-only equivalent answers"}'}]}],
        "usage": {"input_tokens": 10, "output_tokens": 3, "total_tokens": 13}}).encode())


def rate_error(*, body=None, headers=None):
    body = body or {"error": {"code": "rate_limit_exceeded", "type": "requests", "message": "Too many requests"}}
    raw = body if isinstance(body, bytes) else json.dumps(body).encode()
    return HTTPError("https://invalid.example/v1/responses", 429, "Too Many Requests", headers or {}, io.BytesIO(raw))


class RateLimitRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix=".api-rate-limit-test-", dir=ROOT)
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.assertTrue(self.root.is_relative_to(ROOT))
        self.key_file = self.root / "test.key"
        self.secret = "sk-offline-placeholder-not-a-real-key"
        self.key_file.write_text(self.secret, encoding="utf-8")

    def config(self, **changes):
        config = replace(api.APIConfig(), api_key_file=self.key_file, concurrency=4, retries=0,
                         max_api_calls=20, bootstrap=20, rate_limit_base_delay=0.0,
                         max_rate_limit_wait=300.0, max_consecutive_429=10,
                         post_429_interval=0.0)
        return replace(config, **changes)

    def client(self, **changes):
        return api.PreferenceAPIClient(self.config(**changes))

    def test_classification_distinguishes_quota_capacity_rate_and_request_size(self):
        cases = (
            ({"error": {"code": "insufficient_quota", "message": "You exceeded your current quota"}}, "quota"),
            ({"error": {"code": "insufficient_user_quota", "message": "用户余额不足"}}, "quota"),
            ({"error": {"code": "no_available_channel", "message": "当前分组下对于模型 gpt-5.5 无可用渠道"}}, "capacity"),
            ({"error": {"code": "rate_limit_exceeded", "type": "requests", "message": "Rate limit reached"}}, "rate_limit"),
            ({"error": {"code": "rate_limit_exceeded", "message": "Request too large for gpt-5.5 on tokens per min (TPM): Limit 10000, Requested 12000."}}, "request_too_large"),
            (b"<html>Service unavailable temporarily</html>", "unknown_429"),
            ({"error": {"code": "quota_exceeded", "message": "每分钟额度不足，TPM limit"}}, "rate_limit"),
            ({"error": {"code": "quota_exceeded"}}, "unknown_429"),
        )
        for body, category in cases:
            with self.subTest(category=category, body=body):
                raw = body if isinstance(body, bytes) else json.dumps(body).encode()
                result = api.parse_rate_limit_error(raw, {})
                self.assertEqual(result["category"], category)

    def test_upstream_account_pool_error_is_reported_without_raw_body(self):
        result = api.parse_rate_limit_error(json.dumps({"error": {"type": "rate_limit_error",
            "message": "All available accounts are currently rate-limited. Please retry later."}}).encode(), {})
        self.assertEqual(result["category"], "rate_limit")
        self.assertEqual(result["provider_reason"], "all_upstream_accounts_rate_limited")
        self.assertNotIn("message", result)

    def test_error_details_do_not_include_credentials_or_echoed_candidate_text(self):
        candidate = "private candidate text must not appear in rate-limit logs"
        body = {"error": {"code": "rate_limit_exceeded", "type": "requests",
                          "message": f"Authorization: Bearer {self.secret}; prompt={candidate}"}}
        result = api.parse_rate_limit_error(json.dumps(body).encode(), {}, secret=self.secret)
        rendered = json.dumps(result, ensure_ascii=False)
        self.assertNotIn(self.secret, rendered)
        self.assertNotIn(candidate, rendered)
        self.assertEqual(result["category"], "rate_limit")
        self.assertEqual(result["provider_code"], "rate_limit_exceeded")
        self.assertEqual(result["provider_type"], "requests")

    def test_retry_after_supports_seconds_and_http_dates(self):
        raw = b'{"error":{"code":"rate_limit_exceeded"}}'
        seconds = api.parse_rate_limit_error(raw, {"Retry-After": "12"})
        self.assertAlmostEqual(seconds["retry_after_seconds"], 12)
        future = datetime.fromtimestamp(time.time() + 60, timezone.utc)
        dated = api.parse_rate_limit_error(raw, {"Retry-After": format_datetime(future, usegmt=True)})
        self.assertGreaterEqual(dated["retry_after_seconds"], 57)
        self.assertLessEqual(dated["retry_after_seconds"], 61)

    def test_explicit_quota_and_oversized_requests_are_fatal_immediately(self):
        bodies = ({"error": {"code": "insufficient_user_quota", "message": "余额不足"}},
                  {"error": {"code": "rate_limit_exceeded", "message": "Request too large for tokens per min (TPM): Limit 100, Requested 200."}})
        for body in bodies:
            client = self.client()
            with self.subTest(body=body), patch.object(api.quality.request, "urlopen", side_effect=rate_error(body=body)) as send:
                with self.assertRaises(api.quality.FatalAPIError):
                    client.complete(client.payload([]))
            self.assertEqual(send.call_count, 1)
            self.assertTrue(client.stop.is_set())

    def test_retry_after_over_maximum_wait_stops_without_sleeping(self):
        client = self.client()
        with patch.object(api.quality.request, "urlopen", side_effect=rate_error(headers={"Retry-After": "301"})) as send:
            with self.assertRaises(api.quality.FatalAPIError):
                client.complete(client.payload([]))
        self.assertEqual(send.call_count, 1)
        self.assertTrue(client.stop.is_set())

    def test_continuous_429_stops_after_threshold_not_after_hundreds_of_tasks(self):
        client = self.client(max_consecutive_429=3)

        def send(*args, **kwargs):
            raise rate_error()

        with patch.object(api.quality.request, "urlopen", side_effect=send) as request:
            for _ in range(2):
                with self.assertRaises(api.APIRateLimitError) as caught:
                    client.complete(client.payload([]))
                self.assertEqual(caught.exception.details["category"], "rate_limit")
            with self.assertRaises(api.quality.FatalAPIError):
                client.complete(client.payload([]))
        self.assertEqual(request.call_count, 3)
        self.assertTrue(client.stop.is_set())
        self.assertGreaterEqual(client.rate_limit_status()["consecutive_429"], 3)

    def test_all_http_entries_are_serialized_after_a_429(self):
        client = self.client()
        counter_lock = threading.Lock()
        state = {"number": 0, "active": 0, "maximum": 0}

        def send(*args, **kwargs):
            with counter_lock:
                state["number"] += 1
                number = state["number"]
                state["active"] += 1
                state["maximum"] = max(state["maximum"], state["active"])
            try:
                if number == 1:
                    return successful_reply()
                time.sleep(.01)
                raise rate_error()
            finally:
                with counter_lock:
                    state["active"] -= 1

        with patch.object(api.quality.request, "urlopen", side_effect=send):
            client.complete(client.payload([]))  # Initial successful readiness probe.
            with self.assertRaises(api.APIRateLimitError):
                client.complete(client.payload([]))
            state["maximum"] = 0
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = [executor.submit(client.complete, client.payload([])) for _ in range(4)]
                for future in futures:
                    with self.assertRaises(api.APIRateLimitError):
                        future.result(timeout=3)
        self.assertEqual(state["maximum"], 1)
        self.assertEqual(client.rate_limit_status()["effective_concurrency"], 1)

    def test_runtime_rate_limit_controls_do_not_change_cache_identity(self):
        paths = []
        for name, answer in (("candidate.jsonl", "Candidate"), ("reference.jsonl", "Reference")):
            path = self.root / name
            path.write_text(json.dumps({"id": "one", "prompt": "Question?", "answer": answer}) + "\n", encoding="utf-8")
            paths.append(path)
        first = api.prepare(paths[0], paths[1], self.config(), self.root / "results")
        changed = replace(self.config(), rate_limit_base_delay=45.0, max_rate_limit_wait=500.0,
                          max_consecutive_429=8, post_429_interval=10.0)
        second = api.prepare(paths[0], paths[1], changed, self.root / "results")
        self.assertEqual(first["directory"], second["directory"])
        self.assertEqual(first["protocol"], second["protocol"])
        self.assertEqual(first["tasks"], second["tasks"])

    def test_first_actual_judgment_is_a_single_readiness_probe(self):
        paths = []
        for name, answer in (("candidate.jsonl", "Candidate"), ("reference.jsonl", "Reference")):
            path = self.root / name
            path.write_text("".join(json.dumps({"id": str(i), "prompt": f"Question {i}?", "answer": answer}) + "\n"
                                    for i in range(2)), encoding="utf-8")
            paths.append(path)
        entered, release, more = threading.Event(), threading.Event(), threading.Event()
        lock, state = threading.Lock(), {"calls": 0}

        def send(*args, **kwargs):
            with lock:
                state["calls"] += 1
                number = state["calls"]
            if number == 1:
                entered.set()
                release.wait(timeout=3)
            else:
                more.set()
            return successful_reply()

        def run():
            return api.run_evaluation(paths[0], paths[1], self.config(), self.root / "results",
                                      self.root / "history.md")

        with patch.object(api.quality.request, "urlopen", side_effect=send), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(run)
                try:
                    self.assertTrue(entered.wait(timeout=2))
                    self.assertFalse(more.wait(timeout=.05))
                finally:
                    release.set()
                result = future.result(timeout=5)
        self.assertTrue(result["complete"])
        self.assertEqual(state["calls"], 4)

    def test_late_normal_success_does_not_cancel_existing_global_cooldown(self):
        client = self.client(rate_limit_base_delay=30.0)
        entered, release = threading.Event(), threading.Event()
        lock, state = threading.Lock(), {"calls": 0}

        def send(*args, **kwargs):
            with lock:
                state["calls"] += 1
                number = state["calls"]
            if number == 1:
                return successful_reply()
            if number == 2:
                entered.set()
                release.wait(timeout=3)
                return successful_reply()
            raise rate_error(headers={"Retry-After": "30"})

        with patch.object(api.quality.request, "urlopen", side_effect=send):
            client.complete(client.payload([]))
            with ThreadPoolExecutor(max_workers=2) as executor:
                slow = executor.submit(client.complete, client.payload([]))
                self.assertTrue(entered.wait(timeout=2))
                fast = executor.submit(client.complete, client.payload([]))
                try:
                    with self.assertRaises(api.APIRateLimitError):
                        fast.result(timeout=2)
                    self.assertGreater(client.rate_limit_status()["cooldown_seconds"], 20)
                finally:
                    release.set()
                slow.result(timeout=3)
            status = client.rate_limit_status()
        self.assertGreater(status["cooldown_seconds"], 20)
        self.assertEqual(status["effective_concurrency"], 1)


if __name__ == "__main__":
    unittest.main()
