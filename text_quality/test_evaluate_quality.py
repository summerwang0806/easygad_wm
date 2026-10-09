"""No credentials, external API, GPU, or third-party packages required."""
import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
import threading
import time
from types import SimpleNamespace
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

import evaluate_quality as eq


def scoring(a=6, b=8):
    return {"assistant_a": {d: a for d in eq.DIMENSIONS},
            "assistant_b": {d: b for d in eq.DIMENSIONS}, "explanation": "Test-only deterministic judge"}


class FakeClient(eq.APIClient):
    total_calls = 0

    def complete(self, payload):
        if self.calls >= self.args.max_api_calls:
            raise eq.FatalAPIError("Test budget exhausted")
        self.calls += 1
        FakeClient.total_calls += 1
        if "response_format" in payload or "text" in payload:
            data = json.loads(payload.get("messages", payload.get("input"))[-1]["content"])
            grade = lambda text: {"base answer": 4, "warmup answer": 6,
                                  "gad answer": 7, "reference answer": 8}[text]
            content = json.dumps(scoring(grade(data["assistant_a"]), grade(data["assistant_b"])))
        else:
            content = "reference answer"
        return {"content": content, "usage": {"total_tokens": 20},
                "actual_model": "fake-gpt-4o", "response_id": "fake-response"}


class QualityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.files = {}
        for label in ("base", "warmup", "gad"):
            path = self.root / (label + ".jsonl")
            rows = [{"id": str(i), "prompt": [{"role": "user", "content": f"Question {i}"}],
                     "answer": label + " answer", "generation": {"temperature": .7, "seed": i},
                     "num_tokens": 5} for i in range(2)]
            path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
            self.files[label] = path
        self.argv = ["--output-dir", str(self.root / "results"), "--bootstrap", "50"]
        for label, path in self.files.items():
            self.argv += ["--model", f"{label}={path}"]
        FakeClient.total_calls = 0

    def run_main(self, extra=()):
        extra = list(extra)
        if "--reference-file" not in extra and "pairwise" not in extra:
            extra.append("--generate-reference")  # Exercise explicitly retained legacy mode.
        with patch.object(eq, "APIClient", FakeClient), patch.dict(os.environ, {"OPENAI_API_KEY": "test-not-a-real-key"}), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return eq.main(self.argv + list(extra))

    def metrics(self):
        return json.loads((self.root / "results/metrics.json").read_text(encoding="utf-8"))

    def test_dry_run_has_no_writes_or_calls(self):
        self.assertEqual(self.run_main(), 0)
        self.assertEqual(FakeClient.total_calls, 0)
        self.assertFalse((self.root / "results").exists())

    def test_paper_scores_and_resume_and_summary_without_calls(self):
        self.assertEqual(self.run_main(["--run-api"]), 0)
        self.assertEqual(FakeClient.total_calls, 14)  # 2 references + 2*3*2 judges.
        metrics = self.metrics()
        self.assertTrue(metrics["complete"])
        self.assertAlmostEqual(metrics["comparisons"]["gad vs reference"]["left_relative_score"]["mean"], 100*7/15)
        self.assertAlmostEqual(metrics["comparisons"]["warmup vs reference"]["left_relative_score"]["mean"], 100*6/14)
        self.assertEqual(self.run_main(["--run-api"]), 0)
        self.assertEqual(self.run_main(["--summary-only"]), 0)
        self.assertEqual(FakeClient.total_calls, 14)

    def test_pairwise_swapping_and_resume(self):
        args = ["--mode", "pairwise", "--run-api"]
        self.assertEqual(self.run_main(args), 0)
        data = self.metrics()["comparisons"]["gad vs warmup"]
        self.assertEqual(data["left_win_rate"], 1)
        self.assertEqual(data["order_agreement_rate"], 1)
        self.assertAlmostEqual(data["left_minus_right"]["mean"], 1)
        self.assertEqual(self.run_main(args), 0)
        self.assertEqual(FakeClient.total_calls, 4)

    def test_limit_can_extend_without_rejudging_old_samples(self):
        self.assertEqual(self.run_main(["--limit", "1", "--run-api"]), 0)
        self.assertEqual(FakeClient.total_calls, 7)
        self.assertEqual(self.run_main(["--run-api"]), 0)
        self.assertEqual(FakeClient.total_calls, 14)

    def test_budget_preserves_cache_and_excludes_incomplete_pair(self):
        self.assertEqual(self.run_main(["--run-api", "--max-api-calls", "2"]), 2)
        self.assertFalse(self.metrics()["complete"])
        self.assertEqual(self.metrics()["comparisons"], {})
        self.assertEqual(self.run_main(["--run-api"]), 0)
        self.assertEqual(FakeClient.total_calls, 14)

    def test_changed_configuration_cannot_mix_results(self):
        self.run_main(["--run-api"])
        with self.assertRaisesRegex(ValueError, "different inputs/settings"):
            self.run_main(["--summary-only", "--judge-model", "different-model"])

    def test_missing_ids_and_different_prompts_and_settings_fail(self):
        datasets = {label: eq.load_dataset(path) for label, path in self.files.items()}
        del datasets["gad"]["1"]
        with self.assertRaisesRegex(ValueError, "IDs differ"):
            eq.align_datasets(datasets)
        datasets["gad"] = eq.load_dataset(self.files["gad"])
        datasets["gad"]["0"]["prompt"][0]["content"] = "different"
        with self.assertRaisesRegex(ValueError, "Different prompts"):
            eq.align_datasets(datasets)
        datasets["gad"] = eq.load_dataset(self.files["gad"])
        datasets["gad"]["0"]["generation"]["temperature"] = 1
        with self.assertRaisesRegex(ValueError, "generation settings"):
            eq.align_datasets(datasets)
        eq.align_datasets(datasets, allow_mismatch=True)

    def test_duplicate_id_rejected(self):
        path = self.files["base"]
        path.write_text(path.read_text(encoding="utf-8") * 2, encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "duplicate id"):
            eq.load_dataset(path)

    def test_invalid_scores_and_boolean_and_nan_rejected(self):
        for value in (0, 11, True, float("nan")):
            with self.assertRaises(ValueError):
                eq.validate_scores(json.dumps(scoring(value, 8)))
        self.assertEqual(eq.validate_scores("```json\n" + json.dumps(scoring()) + "\n```")["assistant_a"]["overall"], 6)

    def test_api_http_and_schema_without_network(self):
        class Reply(io.BytesIO):
            def __enter__(self):
                return self
            def __exit__(self, *args):
                self.close()
        args = eq.parse_args(['--api-style','chat_completions'])
        client = eq.APIClient(args)
        client.key = "test-only"
        body = {"choices": [{"finish_reason": "stop", "message": {"content": json.dumps(scoring())}}]}
        with patch.object(eq.request, "urlopen", return_value=Reply(json.dumps(body).encode())) as mock:
            response = client.complete(client.payload([], True))
        self.assertEqual(eq.validate_scores(response["content"])["assistant_b"]["overall"], 8)
        sent = json.loads(mock.call_args.args[0].data)
        self.assertTrue(sent["response_format"]["json_schema"]["strict"])
        self.assertFalse(sent["store"])

    def test_supplied_reference_file_skips_reference_api(self):
        path = self.root / "provided_references.jsonl"
        rows = eq.read_jsonl(self.files["base"])
        for row in rows:
            row["answer"] = "reference answer"
        path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
        self.assertEqual(self.run_main(["--run-api", "--reference-file", str(path)]), 0)
        self.assertEqual(FakeClient.total_calls, 12)

    def test_responses_payload_and_decode(self):
        args = eq.parse_args(["--api-style", "responses", "--judge-model", "gpt-5.5"])
        client = eq.APIClient(args)
        payload = client.payload([{"role": "user", "content": "test"}], True)
        self.assertNotIn("temperature", payload)
        self.assertNotIn("messages", payload)
        self.assertFalse(payload["store"])
        self.assertTrue(payload["text"]["format"]["strict"])
        self.assertEqual(payload["reasoning"], {"effort": "low"})
        body = {"status": "completed", "model": "gpt-5.5", "id": "test",
                "output": [{"type": "reasoning"}, {"type": "message", "content": [
                    {"type": "output_text", "text": json.dumps(scoring())}]}],
                "usage": {"input_tokens": 10, "output_tokens": 20, "total_tokens": 30}}
        with patch.object(eq.request, "urlopen", return_value=io.BytesIO(json.dumps(body).encode())) as mock:
            result = client.complete(payload)
        self.assertTrue(mock.call_args.args[0].full_url.endswith("/responses"))
        self.assertEqual(result["usage"]["prompt_tokens"], 10)
        self.assertEqual(result["usage"]["completion_tokens"], 20)
        self.assertEqual(eq.validate_scores(result["content"])["assistant_a"]["overall"], 6)
        self.assertNotIn("text", client.payload([], False))

    def test_responses_incomplete_and_refusal_not_scored(self):
        client = eq.APIClient(eq.parse_args(["--api-style", "responses"]))
        for body in ({"status": "incomplete"}, {"status": "completed", "output": []},
                     {"status": "completed", "output": [{"type": "message", "content": [
                         {"type": "refusal", "refusal": "No"}]}]}):
            with patch.object(eq.request, "urlopen", return_value=io.BytesIO(json.dumps(body).encode())):
                with self.assertRaises(ValueError):
                    client.complete(client.payload([], True))

    def test_key_file_only_read_for_live_requests(self):
        keyfile = self.root / "secret.key"
        args = eq.parse_args(["--api-key-file", str(keyfile)])
        eq.APIClient(args)  # Dry/summary mode does not require a key file.
        keyfile.write_text("test-private-key\n", encoding="utf-8")
        args.run_api = True
        with patch.dict(os.environ, {"OPENAI_API_KEY": "different-test-key"}):
            self.assertEqual(eq.APIClient(args).key, "test-private-key")

    def test_active_lock_and_source_output_collision_rejected(self):
        self.run_main(["--run-api"])
        lock = self.root / "results/.evaluation.lock"
        lock.write_text("12345", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "another run"):
            self.run_main(["--summary-only"])
        self.assertTrue(lock.exists())

    def test_result_history_appends_without_overwriting_snapshots(self):
        self.assertEqual(self.run_main(["--run-api", "--limit", "1"]), 0)
        index = self.root / "results/results_index.jsonl"
        original = index.read_bytes()
        first = eq.read_jsonl(index)[0]
        snapshot = self.root / "results" / first["artifacts"]["metrics.json"]
        snapshot_bytes = snapshot.read_bytes()
        self.assertEqual(self.run_main(["--run-api"]), 0)
        calls = FakeClient.total_calls
        self.assertEqual(self.run_main(["--summary-only"]), 0)
        self.assertEqual(FakeClient.total_calls, calls)
        self.assertTrue(index.read_bytes().startswith(original))
        history = eq.read_jsonl(index)
        self.assertEqual(len(history), 3)
        self.assertEqual(len({r["run_id"] for r in history}), 3)
        self.assertEqual([r["metrics"]["expected_samples"] for r in history], [1, 2, 2])
        self.assertEqual(history[-1]["source"], "summary_only")
        self.assertEqual(snapshot.read_bytes(), snapshot_bytes)
        self.assertNotIn("test-not-a-real-key", index.read_text(encoding="utf-8"))
        for entry in history:
            for path in entry["artifacts"].values():
                self.assertTrue((self.root / "results" / path).exists())

    def test_legacy_latest_is_imported_and_partial_is_archived(self):
        self.run_main(["--run-api", "--max-api-calls", "2"])
        index = self.root / "results/results_index.jsonl"
        self.assertFalse(eq.read_jsonl(index)[0]["metrics"]["complete"])
        old_metrics = (self.root / "results/metrics.json").read_bytes()
        index.unlink()  # Simulate an output directory made by the pre-history version.
        self.assertEqual(self.run_main(["--run-api"]), 0)
        history = eq.read_jsonl(index)
        self.assertEqual([r["source"] for r in history], ["legacy_import", "evaluation"])
        archived = self.root / "results" / history[0]["artifacts"]["metrics.json"]
        self.assertEqual(archived.read_bytes(), old_metrics)
        self.assertTrue(history[1]["metrics"]["complete"])

    def test_parallel_prompts_overlap_and_keep_serial_scores(self):
        self.run_main(["--run-api", "--concurrency", "1"])
        serial = self.metrics()["comparisons"]
        class SlowClient(FakeClient):
            active = 0
            peak = 0
            guard = threading.Lock()
            def complete(self, payload):
                with self.guard:
                    SlowClient.active += 1
                    SlowClient.peak = max(SlowClient.peak, SlowClient.active)
                try:
                    time.sleep(.01)
                    return super().complete(payload)
                finally:
                    with self.guard:
                        SlowClient.active -= 1
        target = self.root / "parallel"
        with patch.object(eq, "APIClient", SlowClient), patch.dict(os.environ, {"OPENAI_API_KEY": "test"}), \
                contextlib.redirect_stdout(io.StringIO()):
            code = eq.main(self.argv + ["--run-api", "--generate-reference", "--concurrency", "2", "--output-dir", str(target)])
        self.assertEqual(code, 0)
        self.assertEqual(SlowClient.peak, 2)
        self.assertEqual(json.loads((target / "metrics.json").read_text())["comparisons"], serial)
        self.assertEqual(len(eq.read_jsonl(target / "cache.jsonl")), 14)

    def test_real_client_budget_is_atomic_under_concurrency(self):
        client = eq.APIClient(eq.parse_args(["--max-api-calls", "3", '--api-style','chat_completions']))
        body = {"choices": [{"finish_reason": "stop", "message": {"content": "ok"}}]}
        def reply(*args, **kwargs):
            time.sleep(.01)
            return io.BytesIO(json.dumps(body).encode())
        def invoke(_):
            try:
                return client.complete(client.payload([], False))["content"]
            except eq.FatalAPIError:
                return "stopped"
        with patch.object(eq.request, "urlopen", side_effect=reply) as mock, ThreadPoolExecutor(max_workers=8) as pool:
            outcomes = list(pool.map(invoke, range(20)))
        self.assertEqual(mock.call_count, 3)
        self.assertEqual(client.calls, 3)
        self.assertEqual(outcomes.count("ok"), 3)

    def test_parallel_identical_cache_task_is_only_requested_once(self):
        client = FakeClient(eq.parse_args([]))
        cache = eq.Cache(self.root / "cache.jsonl", client, True)
        def invoke(_):
            return cache.task("reference", "same-id", [{"role": "user", "content": "same"}], {})
        with contextlib.redirect_stdout(io.StringIO()), ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(invoke, range(12)))
        self.assertEqual(client.calls, 1)
        self.assertEqual(len(eq.read_jsonl(cache.path)), 1)
        self.assertTrue(all(r == {"answer": "reference answer"} for r in results))

    def test_default_paper_requires_human_reference_no_generation_fallback(self):
        args = eq.parse_args([])
        self.assertEqual(args.reference_file.name, "dolly_human_500.jsonl")
        self.assertFalse(args.generate_reference)
        self.assertIsNone(eq.parse_args(["--mode", "pairwise"]).reference_file)
        with self.assertRaises(FileNotFoundError):
            self.run_main(["--run-api", "--reference-file", str(self.root / "missing.jsonl")])
        self.assertEqual(FakeClient.total_calls, 0)

    def test_dolly_human_reference_provenance_and_prompt_checks(self):
        from prepare_dolly_references import build_prompt, verified_references
        raw = [{"instruction": "Question", "context": "Some context", "response": "Human answer"}]
        prompt = build_prompt("Question", "Some context")
        split = [{"id": "dolly-00000", "content": prompt, "teacher_response": "Human answer"}]
        models = {"base": {"dolly-00000": {"prompt": prompt, "answer": "Generated", "generation": None}}}
        refs = verified_references(raw, split, models)
        self.assertEqual(refs[0]["answer"], "Human answer")
        split[0]["teacher_response"] = "Teacher-generated answer"
        with self.assertRaisesRegex(ValueError, "differs from raw"):
            verified_references(raw, split, models)
        split[0]["teacher_response"] = "Human answer"
        raw[0]["context"] = "Wrong context"
        with self.assertRaisesRegex(ValueError, "context differs"):
            verified_references(raw, split, models)

    def test_live_status_partial_and_swanlab_resume_without_exposing_keys(self):
        uploads, inits = [], []
        def init(project=None, mode=None, **kwargs):
            inits.append(kwargs)
            return SimpleNamespace(id=kwargs['id'], log=lambda values, step: uploads.append((step, values)))
        fake = SimpleNamespace(init=init, finish=lambda: None, login=lambda **kwargs: None)
        with patch.dict('sys.modules', {'swanlab': fake}), patch.dict(os.environ, {'SWANLAB_API_KEY': 'test-swanlab-key'}):
            self.assertEqual(self.run_main(['--run-api', '--swanlab-mode', 'cloud']), 0)
            first_steps = [step for step, _ in uploads]
            self.assertEqual(self.run_main(['--summary-only', '--swanlab-mode', 'cloud']), 0)
        self.assertEqual(inits[0]['id'], inits[1]['id'])
        self.assertEqual(sorted(set(step for step, _ in uploads)), [step for step, _ in uploads])
        self.assertGreater(uploads[-1][0], first_steps[-1])
        values = uploads[-1][1]
        self.assertEqual(values['progress/coverage'], 1)
        self.assertEqual(values['quality/gad_vs_reference/overall'], 7)
        path = self.root / 'results/live_status.json'
        self.assertEqual(json.loads(path.read_text())['metrics']['status/complete'], 1)
        history = eq.read_jsonl(self.root / 'results/live_metrics.jsonl')
        self.assertGreaterEqual(len(history), 4)
        self.assertNotIn('test-not-a-real-key', json.dumps(inits)+path.read_text())
        self.assertNotIn('test-swanlab-key', json.dumps(inits)+path.read_text())

    def test_live_pair_differences_require_same_prompt_and_exclude_partial_rounds(self):
        from live_monitor import live_scores
        def row(label, sample_id, score):
            return {'id': sample_id, 'left': label, 'right': 'reference',
                    'left_scores': {d: score for d in eq.DIMENSIONS},
                    'right_scores': {d: 8 for d in eq.DIMENSIONS},
                    'left_relative_score': score, 'winner': 'right', 'order_agreement': True}
        values = live_scores([row('gad','1',7),row('warmup','2',6)], 2)
        self.assertNotIn('paired/gad_minus_warmup/n', values)
        values = live_scores([row('gad','1',7),row('warmup','1',6)], 2)
        self.assertEqual(values['paired/gad_minus_warmup/n'], 1)
        self.assertEqual(values['paired/gad_minus_warmup/relative_score_difference'], 1)

    def test_single_file_does_not_load_other_models_and_uses_own_output(self):
        references = self.root / 'refs.jsonl'
        refs = eq.read_jsonl(self.files['base'])
        for r in refs:
            r['answer'] = 'reference answer'
        references.write_text(''.join(json.dumps(r)+'\n' for r in refs))
        target = self.root / 'single'
        with patch.object(eq, 'APIClient', FakeClient), patch.dict(os.environ, {'OPENAI_API_KEY': 'test'}), \
             patch.object(eq, 'DEFAULT_FILES', {'unrelated': self.root/'not-present.jsonl'}), \
             contextlib.redirect_stdout(io.StringIO()):
            code = eq.main(['--input-file',str(self.files['gad']), '--reference-file',str(references),
                           '--output-dir',str(target), '--run-api', '--bootstrap','20'])
        self.assertEqual(code, 0)
        metrics = json.loads((target/'metrics.json').read_text())
        self.assertEqual(set(metrics['comparisons']), {'gad vs reference'})
        self.assertEqual(FakeClient.total_calls, 4)
        self.assertNotEqual(eq.parse_args(['--input-file','a.jsonl']).output_dir,
                            eq.parse_args(['--input-file','b.jsonl']).output_dir)

    def test_gpu_selection_number_explicit_and_insufficient_idle(self):
        from local_judge import select_gpus, parse_gpu_ids
        rows = [{'index':i,'uuid':str(i),'total':40000,'used':used,'utilization':util}
                for i,used,util in [(0,0,0),(1,0,0),(2,10000,60),(3,0,0)]]
        args = SimpleNamespace(gpus=None,num_gpus=2,exclude_gpus='0',gpu_memory_utilization=.85)
        self.assertEqual([r['index'] for r in select_gpus(args,rows)], [1,3])
        args.gpus = '3,1'
        self.assertEqual([r['index'] for r in select_gpus(args,rows)], [3,1])
        args.gpus = '2'
        with self.assertRaisesRegex(ValueError,'free'):
            select_gpus(args,rows)
        args.gpus = None
        args.num_gpus = 3
        with self.assertRaisesRegex(ValueError,'idle'):
            select_gpus(args,rows)
        with self.assertRaises(ValueError):
            parse_gpu_ids('1,1')

    def test_local_replica_prompt_routing_and_cache_identity(self):
        from local_judge import make_local_client
        args = eq.parse_args(['--api-style','chat_completions'])
        args.api_key_file = None
        data = eq.load_dataset(self.files['gad'])
        client = make_local_client(args, eq.APIClient, eq.FatalAPIError, eq.digest, data, list(data))
        client.ready = True
        client.endpoints = ['http://127.0.0.1:1234/v1','http://127.0.0.1:1235/v1']
        for i,sample_id in enumerate(data):
            for swap in (False,True):
                message = {'role':'user','content':json.dumps({'conversation':data[sample_id]['prompt'],
                           'assistant_a':'a' if swap else 'b'})}
                payload = client.payload([message],True)
                self.assertEqual(client.request_url(payload),client.endpoints[i]+'/chat/completions')
                self.assertEqual(payload['seed'],42)
        self.assertEqual(client.base_url,'http://local-vllm/v1')
        client.close()

    def test_local_transport_bypasses_external_proxy(self):
        from local_judge import make_local_client
        from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
        class Handler(BaseHTTPRequestHandler):
            received = []
            def log_message(self,*args):
                pass
            def do_POST(self):
                payload = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                Handler.received.append(payload)
                body = json.dumps({'model':'local-test','choices':[{'finish_reason':'stop',
                    'message':{'content':json.dumps(scoring())}}]}).encode()
                self.send_response(200)
                self.send_header('Content-Type','application/json')
                self.send_header('Content-Length',str(len(body)))
                self.end_headers()
                self.wfile.write(body)
        server = ThreadingHTTPServer(('127.0.0.1',0),Handler)
        thread = threading.Thread(target=server.serve_forever,daemon=True)
        thread.start()
        try:
            args = eq.parse_args(['--api-style','chat_completions'])
            args.backend = 'local'
            data = eq.load_dataset(self.files['gad'])
            client = make_local_client(args,eq.APIClient,eq.FatalAPIError,eq.digest,data,list(data))
            client.ready = True
            client.endpoints = [f'http://127.0.0.1:{server.server_port}/v1']
            user = {'role':'user','content':json.dumps({'conversation':data['0']['prompt']})}
            with patch.dict(os.environ,{'http_proxy':'http://127.0.0.1:1','HTTP_PROXY':'http://127.0.0.1:1'}):
                reply = client.complete(client.payload([user],True))
            self.assertEqual(eq.validate_scores(reply['content'])['assistant_a']['overall'],6)
            self.assertEqual(client.calls,1)
            self.assertEqual(Handler.received[0]['seed'],42)
            client.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
