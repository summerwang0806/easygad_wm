"""Remote judging regressions: fake replies only, no GPU or paid requests."""
from __future__ import annotations

import contextlib
from dataclasses import replace
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "soft-win-rate"))
import run_api_soft_win_rate as api


class FakeClient:
    def __init__(self, config, responder=None):
        self.config, self.responder = config, responder
        self.calls, self.call_lock, self.stop = 0, threading.Lock(), threading.Event()
        self.payloads = []
        self.closed = False

    def complete(self, payload):
        with self.call_lock:
            if self.stop.is_set() or self.calls >= self.config.max_api_calls:
                self.stop.set()
                raise api.quality.FatalAPIError("API-call budget reached; cached judgments remain reusable")
            self.calls += 1
            number = self.calls
            self.payloads.append(payload)
        pair = json.loads(payload.get("input", payload.get("messages"))[-1]["content"])
        content = self.responder(pair, number) if self.responder else {
            "winner": "A" if pair["answer_a"].startswith("Candidate") else "B", "reason": "Offline test preference"}
        return {"content": content if isinstance(content, str) else json.dumps(content),
                "usage": {"prompt_tokens": 11, "completion_tokens": 3, "total_tokens": 14},
                "actual_model": "fake-api-judge", "response_id": f"fake-{number}"}

    def close(self):
        self.closed = True


class APIPreferenceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix=".api-preference-test-", dir=ROOT)
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.assertTrue(self.root.is_relative_to(ROOT))
        self.input = self.write("candidate.jsonl", "Candidate")
        self.reference = self.write("reference.jsonl", "Reference")
        self.output, self.history = self.root / "results" / "api", self.root / "history.md"
        self.config = replace(api.APIConfig(), api_key_file=self.root / "absent.key", concurrency=2,
                              max_api_calls=10, retries=0, bootstrap=30)
        self.clients = []

    def write(self, filename, prefix):
        path = self.root / filename
        rows = [{"id": name, "prompt": f"Question {name}?", "answer": f"{prefix} {name}",
                 "generation": {"temperature": 0.7}, "model_path": "/secret/watermark-checkpoint"}
                for name in ("one", "two")]
        path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
        return path

    def factory(self, config):
        client = FakeClient(config)
        self.clients.append(client)
        return client

    def run_evaluation(self, config=None, factory=None, **kwargs):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return api.run_evaluation(self.input, self.reference, config or self.config, self.output, self.history,
                                      client_factory=factory or self.factory, **kwargs)

    def test_two_orders_and_immediate_cache_without_local_models(self):
        original = self.input.read_bytes(), self.reference.read_bytes()
        with patch.object(api.common, "fingerprint_model", side_effect=AssertionError("API must not inspect local weights")):
            result = self.run_evaluation()
        self.assertTrue(result["complete"])
        self.assertEqual(result["api_calls"], 4)
        self.assertEqual(result["num_valid_samples"], 2)
        self.assertEqual(result["soft_win_rate"], 1)
        self.assertEqual(result["win_plus_tie_rate"], 1)
        self.assertEqual(result["actual_model_ids"], ["fake-api-judge"])
        self.assertTrue(self.clients[0].closed)
        cached = [json.loads(line) for line in Path(result["cache_file"]).read_text(encoding="utf-8").splitlines()]
        self.assertEqual(len(cached), 4)
        self.assertEqual({(row["id"], row["swapped"]) for row in cached},
                         {("one", False), ("one", True), ("two", False), ("two", True)})
        self.assertTrue(all(row["preference"] == 1 and row["judgment"]["reason"] for row in cached))
        self.assertTrue(all(row["round_preferences"] == [1, 1] for row in result["per_sample"]))
        self.assertEqual(result["usage_in_successful_cache"]["total_tokens"], 56)
        for payload in self.clients[0].payloads:
            self.assertNotIn("/secret/watermark-checkpoint", json.dumps(payload))
            self.assertFalse(payload["store"])
        self.assertEqual((self.input.read_bytes(), self.reference.read_bytes()), original)

    def test_resume_and_summary_only_do_not_need_credentials_or_network(self):
        first = self.run_evaluation()
        before = self.history.read_text(encoding="utf-8")
        cache = Path(first["cache_file"]).read_bytes()

        def forbidden(*args):
            self.fail("Complete cache must not create an API client or read a key")

        second = self.run_evaluation(factory=forbidden)
        third = self.run_evaluation(factory=forbidden, summary_only=True)
        self.assertTrue(second["complete"] and third["complete"])
        self.assertEqual(second["api_calls"], 0)
        self.assertEqual(second["cache_reused_rounds"], 4)
        self.assertEqual(Path(first["cache_file"]).read_bytes(), cache)
        self.assertTrue(self.history.read_text(encoding="utf-8").startswith(before))
        self.assertEqual(self.history.read_text(encoding="utf-8").count("## API 评测记录"), 3)

    def test_budget_exhaustion_excludes_partial_pairs_and_can_resume(self):
        result = self.run_evaluation(config=replace(self.config, max_api_calls=1, concurrency=1))
        self.assertFalse(result["complete"])
        self.assertEqual(result["new_judgments"], 1)
        self.assertEqual(result["num_valid_samples"], 0)
        self.assertIsNone(result["soft_win_rate"])
        self.assertIn("budget reached", result["failure"])
        resumed = self.run_evaluation()
        self.assertTrue(resumed["complete"])
        self.assertEqual(resumed["new_judgments"], 3)
        self.assertEqual(resumed["cache_file"], result["cache_file"])

    def test_invalid_outputs_are_not_ties_and_other_questions_continue(self):
        def factory(config):
            return FakeClient(config, lambda pair, _: {"winner": "invalid", "reason": "Bad format"}
                              if "two" in pair["conversation"][0]["content"] else {"winner": "tie", "reason": "Equivalent"})

        result = self.run_evaluation(factory=factory)
        self.assertFalse(result["complete"])
        self.assertEqual(result["num_valid_samples"], 1)
        self.assertEqual(result["failed_orders_this_run"], 2)
        self.assertEqual(result["soft_win_rate"], .5)
        self.assertEqual(result["win_plus_tie_rate"], 1)
        self.assertEqual(result["num_valid_rounds"], 2)

    def test_retry_validates_content_and_only_saves_successful_result_once(self):
        client = None

        def factory(config):
            nonlocal client
            client = FakeClient(config, lambda pair, number: "not json" if number == 1 else
                                {"winner": "tie", "reason": "Valid retry"})
            client.stop.wait = lambda timeout=None: client.stop.is_set()
            return client

        result = self.run_evaluation(config=replace(self.config, retries=1, concurrency=1), factory=factory)
        self.assertTrue(result["complete"])
        self.assertEqual(result["api_calls"], 5)
        self.assertEqual(result["new_judgments"], 4)
        self.assertEqual(len(Path(result["cache_file"]).read_text(encoding="utf-8").splitlines()), 4)

    def test_limit_and_runtime_settings_share_cache_but_model_changes_do_not(self):
        small = self.run_evaluation(limit=1)
        full = self.run_evaluation(config=replace(self.config, concurrency=1, max_api_calls=20,
                                                 timeout=15, api_key_file=self.root / "another-absent.key"))
        self.assertEqual(small["cache_file"], full["cache_file"])
        self.assertEqual(full["cache_reused_rounds"], 2)
        changed = self.run_evaluation(config=replace(self.config, judge_model="another-api-judge"))
        self.assertNotEqual(changed["cache_file"], full["cache_file"])
        self.assertEqual(changed["cache_reused_rounds"], 0)

    def test_summary_only_with_empty_cache_never_creates_client(self):
        def forbidden(*args):
            self.fail("Summary-only must never contact API")
        result = self.run_evaluation(factory=forbidden, summary_only=True)
        self.assertFalse(result["complete"])
        self.assertEqual(result["api_calls"], 0)
        self.assertIsNone(result["soft_win_rate"])

    def test_interrupt_keeps_already_inflight_success_and_stops_new_requests(self):
        barrier = threading.Barrier(2)

        class InterruptingClient(FakeClient):
            def complete(self, payload):
                with self.call_lock:
                    self.calls += 1
                    number = self.calls
                if number == 1:
                    return {"content": '{"winner":"tie","reason":"Readiness probe"}',
                            "usage": {}, "actual_model": "fake-api-judge", "response_id": "probe"}
                barrier.wait(timeout=5)
                if number == 2:
                    raise KeyboardInterrupt
                # Finish only after the parent has stopped scheduling. This
                # paid/in-flight success must still be flushed to the cache.
                self.stop.wait(timeout=5)
                return {"content": '{"winner":"tie","reason":"In-flight completion"}',
                        "usage": {}, "actual_model": "fake-api-judge", "response_id": "inflight"}

        result = self.run_evaluation(factory=InterruptingClient)
        self.assertTrue(result["interrupted"])
        self.assertFalse(result["complete"])
        self.assertEqual(result["api_calls"], 3)
        self.assertEqual(result["new_judgments"], 2)
        self.assertEqual(len(Path(result["cache_file"]).read_text(encoding="utf-8").splitlines()), 2)

    def test_check_only_has_no_writes_and_no_client_or_local_model_access(self):
        with patch.object(api, "REFERENCE_JSONL", self.reference), patch.object(api, "RESULTS_DIR", self.output), \
                patch.object(api, "PreferenceAPIClient", side_effect=AssertionError("No credentials or network")), \
                patch.object(api.common, "fingerprint_model", side_effect=AssertionError("No local model")), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(api.main(["--input-file", str(self.input), "--check-only"]), 0)
        self.assertFalse(self.output.exists())

    def test_mismatched_prompt_is_rejected_before_creating_client(self):
        data = self.reference.read_text(encoding="utf-8").replace("Question one?", "Other question?")
        self.reference.write_text(data, encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "prompts differ"):
            self.run_evaluation()
        self.assertEqual(self.clients, [])

    def test_trailing_interrupted_cache_line_is_recovered(self):
        first = self.run_evaluation()
        with Path(first["cache_file"]).open("ab") as handle:
            handle.write(b'{"interrupted":')
        second = self.run_evaluation()
        self.assertTrue(second["complete"])
        self.assertEqual(second["api_calls"], 0)
        self.assertTrue(list(Path(first["cache_file"]).parent.glob("judgments.jsonl.interrupted_*")))

    def test_cache_write_failure_stops_instead_of_repeating_paid_requests(self):
        with patch.object(api.common, "append_jsonl", side_effect=OSError("Synthetic disk full")):
            result = self.run_evaluation(config=replace(self.config, concurrency=1, retries=2))
        self.assertFalse(result["complete"])
        self.assertEqual(result["api_calls"], 1)
        self.assertIn("Cannot write API judgment cache", result["failure"])

    def actual_client(self, **kwargs):
        path = self.root / "test.key"
        path.write_text("offline-placeholder-not-a-real-key", encoding="utf-8")
        return api.PreferenceAPIClient(replace(self.config, api_key_file=path, **kwargs))

    def test_missing_new_key_file_does_not_fall_back_to_old_environment_key(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "old-offline-placeholder"}):
            with self.assertRaisesRegex(ValueError, "API key file not found"):
                api.PreferenceAPIClient(self.config)

    class Reply(io.BytesIO):
        def __enter__(self):
            return self
        def __exit__(self, *args):
            self.close()

    def test_responses_api_uses_preference_schema_and_existing_client(self):
        client = self.actual_client()
        body = {"status": "completed", "id": "response-test", "model": "fake-api-model",
                "output": [{"type": "message", "content": [{"type": "output_text",
                    "text": '{"winner":"tie","reason":"Equal quality"}'}]}],
                "usage": {"input_tokens": 12, "output_tokens": 3, "total_tokens": 15}}
        with patch.object(api.quality.request, "urlopen", return_value=self.Reply(json.dumps(body).encode())) as send:
            response = client.complete(self.config.payload([]))
        req = send.call_args.args[0]
        payload = json.loads(req.data)
        self.assertTrue(req.full_url.endswith("/responses"))
        self.assertFalse(payload["store"])
        self.assertEqual(payload["reasoning"], {"effort": "low"})
        self.assertEqual(payload["text"]["format"]["schema"]["required"], ["winner", "reason"])
        self.assertNotIn("assistant_a", json.dumps(payload))
        self.assertEqual(response["usage"]["prompt_tokens"], 12)
        self.assertEqual(api.common.parse_judgment(response["content"])["winner"], "tie")

    def test_chat_completions_payload_and_response_are_supported(self):
        config = replace(self.config, api_style="chat_completions")
        client = self.actual_client(api_style="chat_completions")
        body = {"choices": [{"finish_reason": "stop", "message": {"content": '{"winner":"A","reason":"Better"}'}}]}
        with patch.object(api.quality.request, "urlopen", return_value=self.Reply(json.dumps(body).encode())) as send:
            response = client.complete(config.payload([]))
        payload = json.loads(send.call_args.args[0].data)
        self.assertTrue(send.call_args.args[0].full_url.endswith("/chat/completions"))
        self.assertTrue(payload["response_format"]["json_schema"]["strict"])
        self.assertEqual(api.common.parse_judgment(response["content"])["winner"], "A")

    def test_refusal_and_incomplete_response_are_not_accepted(self):
        for body in ({"status": "incomplete", "output": []},
                     {"status": "completed", "output": [{"type": "message", "content": [{"type": "refusal"}]}]}):
            with self.subTest(body=body):
                client = self.actual_client()
                with patch.object(api.quality.request, "urlopen", return_value=self.Reply(json.dumps(body).encode())):
                    with self.assertRaises(ValueError):
                        client.complete(self.config.payload([]))

    def test_auth_errors_and_quota_errors_stop_without_logging_provider_body(self):
        for code, body in ((401, b'provider body with sensitive text'),
                           (429, b'{"error":{"code":"insufficient_quota","message":"sensitive text"}}')):
            client = self.actual_client()
            failure = HTTPError(client.base_url + "/responses", code, "test", {}, io.BytesIO(body))
            with patch.object(api.quality.request, "urlopen", side_effect=failure):
                with self.assertRaises(api.quality.FatalAPIError) as caught:
                    client.complete(self.config.payload([]))
            self.assertNotIn("sensitive text", str(caught.exception))
            self.assertNotIn("offline-placeholder", str(caught.exception))
            self.assertEqual(client.calls, 1)


if __name__ == "__main__":
    unittest.main()
