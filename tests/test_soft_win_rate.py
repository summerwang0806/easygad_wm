"""Local soft-win-rate evaluation regressions without CUDA, models or APIs.

Run with ``python -m unittest tests.test_soft_win_rate -v``. The fake worker
returns explicit preferences, allowing source alignment, anonymous swapping,
aggregation and cache/report behavior to be checked independently of an LLM.
"""

from __future__ import annotations

import contextlib
from copy import deepcopy
import importlib.util
import io
import json
import math
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
TOOL_ROOT = ROOT / "soft-win-rate"
if str(TOOL_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOL_ROOT))
_SPEC = importlib.util.spec_from_file_location("soft_win_rate_runner", TOOL_ROOT / "run_soft_win_rate.py")
swr = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = swr
_SPEC.loader.exec_module(swr)


class SoftWinRateCase(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix=".soft-win-rate-test-", dir=ROOT)
        if not Path(self.temporary.name).resolve().is_relative_to(ROOT):
            raise AssertionError("test cleanup directory is outside the workspace")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def write_rows(self, name, rows):
        path = self.root / name
        with path.open("w", encoding="utf-8", newline="\n") as handle:
            for row in rows:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        return path

    def row(self, sample_id="one", answer="Candidate answer", prompt="Question?"):
        return {"id": sample_id, "prompt": prompt, "answer": answer,
                "model_path": "/private/student-checkpoint", "model_label": "secret-watermark-label",
                "z_score": 12345.0}

    def sources(self, ids=("one",)):
        candidate = self.write_rows("candidate.jsonl", [self.row(i, "Candidate answer " + i) for i in ids])
        reference = self.write_rows("reference.jsonl", [self.row(i, "Reference answer " + i) for i in ids])
        return candidate, reference

    def tasks(self, ids=("one",)):
        candidate, reference = self.sources(ids)
        left, right = swr.load_answers(candidate), swr.load_answers(reference)
        return swr.make_tasks(left, right, swr.align_answers(left, right), "test-protocol")

    @staticmethod
    def judgment(winner):
        return {"winner": winner, "reason": "Fixed offline test judgment"}


class AlignmentAndPromptTests(SoftWinRateCase):
    def test_text_and_equivalent_message_prompt_align_by_id(self):
        candidate, reference = self.sources()
        right = self.row(answer="Reference answer", prompt=[{"role": "user", "content": "Question?"}])
        reference = self.write_rows("reference.jsonl", [right])
        left_rows, right_rows = swr.load_answers(candidate), swr.load_answers(reference)
        self.assertEqual(swr.align_answers(left_rows, right_rows), ["one"])

    def test_missing_ids_duplicate_ids_or_changed_prompt_fail_without_silent_intersection(self):
        candidate, reference = self.sources(("one", "two"))
        left, right = swr.load_answers(candidate), swr.load_answers(reference)
        with self.assertRaises(ValueError):
            swr.align_answers(left, {"one": right["one"]})
        changed = deepcopy(right)
        changed["one"]["prompt"] = [{"role": "user", "content": "Different question"}]
        with self.assertRaises(ValueError):
            swr.align_answers(left, changed)
        duplicate = self.write_rows("duplicates.jsonl", [self.row(), self.row()])
        with self.assertRaises(ValueError):
            swr.load_answers(duplicate)

    def test_both_orders_are_anonymous_and_only_reorder_the_original_answers(self):
        tasks = self.tasks()
        self.assertEqual(len(tasks), 2)
        self.assertEqual({task["swapped"] for task in tasks}, {False, True})
        self.assertEqual(len({task["key"] for task in tasks}), 2)
        for task in tasks:
            text = json.dumps(task["messages"], ensure_ascii=False)
            self.assertIn("Question?", text)
            self.assertIn("Candidate answer one", text)
            self.assertIn("Reference answer one", text)
            self.assertNotIn("secret-watermark-label", text)
            self.assertNotIn("/private/student-checkpoint", text)
            self.assertNotIn("12345", text)
            self.assertEqual(text.index("Candidate answer one") > text.index("Reference answer one"), task["swapped"])

    def test_task_cache_identity_changes_with_answer_or_protocol(self):
        candidate, reference = self.sources()
        left, right = swr.load_answers(candidate), swr.load_answers(reference)
        first = swr.make_tasks(left, right, ["one"], "protocol-one")
        second = swr.make_tasks(left, right, ["one"], "protocol-two")
        self.assertNotEqual([task["key"] for task in first], [task["key"] for task in second])
        right["one"]["answer"] += " changed"
        third = swr.make_tasks(left, right, ["one"], "protocol-one")
        self.assertNotEqual([task["key"] for task in first], [task["key"] for task in third])


class PreferenceStatisticsTests(SoftWinRateCase):
    def test_wins_ties_and_losses_have_explicit_half_tie_weight(self):
        tasks = self.tasks(("win", "tie", "loss"))
        judgments = {}
        for task in tasks:
            desired = {"win": ("B" if task["swapped"] else "A"),
                       "tie": "tie", "loss": ("A" if task["swapped"] else "B")}[task["id"]]
            judgments[task["key"]] = self.judgment(desired)
        result = swr.summarize_judgments(tasks, judgments, bootstrap=100, seed=42)
        self.assertEqual(result["num_samples"], 3)
        self.assertEqual(result["num_valid_samples"], 3)
        self.assertEqual(result["num_valid_rounds"], 6)
        self.assertAlmostEqual(result["soft_win_rate"], 0.5)
        self.assertAlmostEqual(result["strict_win_rate"], 1 / 3)
        self.assertAlmostEqual(result["tie_rate"], 1 / 3)
        self.assertAlmostEqual(result["loss_rate"], 1 / 3)
        self.assertEqual(result["order_agreement_rate"], 1.0)
        self.assertLessEqual(result["ci95"][0], 0.5)
        self.assertGreaterEqual(result["ci95"][1], 0.5)

    def test_order_conflict_is_not_misreported_as_a_true_judge_tie(self):
        tasks = self.tasks()
        judgments = {task["key"]: self.judgment("A") for task in tasks}
        result = swr.summarize_judgments(tasks, judgments, bootstrap=50, seed=42)
        self.assertEqual(result["soft_win_rate"], 0.5)
        self.assertEqual(result["strict_win_rate"], 0.5)
        self.assertEqual(result["loss_rate"], 0.5)
        self.assertEqual(result["tie_rate"], 0.0)
        self.assertEqual(result["order_agreement_rate"], 0.0)

    def test_missing_one_order_excludes_whole_prompt_and_reports_coverage(self):
        tasks = self.tasks(("complete", "partial"))
        judgments = {task["key"]: self.judgment("tie") for task in tasks
                     if task["id"] == "complete" or not task["swapped"]}
        result = swr.summarize_judgments(tasks, judgments, bootstrap=50, seed=42)
        self.assertEqual(result["num_samples"], 2)
        self.assertEqual(result["num_valid_samples"], 1)
        self.assertEqual(result["num_valid_rounds"], 2)
        self.assertEqual(result["num_expected_rounds"], 4)
        self.assertEqual(result["coverage"], 0.5)
        self.assertEqual(result["soft_win_rate"], 0.5)

    def test_zero_completed_prompts_produces_null_not_zero_quality(self):
        result = swr.summarize_judgments(self.tasks(), {}, bootstrap=50, seed=42)
        self.assertEqual(result["num_valid_samples"], 0)
        self.assertIsNone(result["soft_win_rate"])
        self.assertIsNone(result["ci95"])
        json.dumps(result, allow_nan=False)

    def test_invalid_or_refused_judgments_are_not_interpreted_as_ties(self):
        for raw in ('I cannot judge this.', '{"winner":"unknown","reason":"bad"}',
                    '{"winner":"A"}', '{"winner":"tie","reason":null}',
                    '{"winner":"A","reason":"ok","score":10}'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                swr.parse_judgment(raw)
        for winner in ("A", "B", "tie"):
            self.assertEqual(swr.parse_judgment(json.dumps(self.judgment(winner)))["winner"], winner)


class GPUPlanningTests(unittest.TestCase):
    @staticmethod
    def model():
        from gpu_runtime import ModelSpec
        return ModelSpec(weight_bytes=65_524_246_528, num_attention_heads=64,
                         num_key_value_heads=8, num_hidden_layers=64, head_dim=128)

    @staticmethod
    def gpu(index, total=40960, free=None):
        from gpu_runtime import GPU
        return GPU(index=index, uuid=f"GPU-test-{index}", name="NVIDIA A100",
                   total_mib=total, free_mib=total if free is None else free, utilization=0)

    def test_mixed_six_card_machine_prefers_single_80gb_and_never_tp6(self):
        from gpu_runtime import plan_gpus
        devices = [self.gpu(index, total=81920 if index == 1 else 40960) for index in range(6)]
        plans = plan_gpus(devices, self.model(), max_model_len=8192, max_num_seqs=2)
        self.assertTrue(plans)
        self.assertEqual(plans[0].gpu_ids, (1,))
        self.assertEqual(plans[0].tensor_parallel_size, 1)
        self.assertNotIn(6, {plan.tensor_parallel_size for plan in plans})
        self.assertTrue(all(64 % plan.tensor_parallel_size == 0 for plan in plans))

    def test_gpu_selection_accounts_for_actual_free_memory(self):
        from gpu_runtime import plan_gpus
        # The 80GB device is physically larger, but its occupied memory must
        # not be treated as available to this evaluation.
        devices = [self.gpu(1, total=81920, free=12000),
                   self.gpu(2), self.gpu(3), self.gpu(4), self.gpu(5)]
        plans = plan_gpus(devices, self.model(), max_model_len=8192, max_num_seqs=2)
        self.assertTrue(plans)
        self.assertTrue(all(1 not in plan.gpu_ids for plan in plans))
        self.assertTrue(all(plan.tensor_parallel_size in (2, 4) for plan in plans))
        self.assertEqual(plan_gpus([self.gpu(0, free=4000)], self.model()), [])


    def test_existing_cuda_mask_is_respected_including_uuid_masks(self):
        from gpu_runtime import filter_visible_gpus
        devices = [self.gpu(index) for index in range(6)]
        self.assertEqual([gpu.index for gpu in filter_visible_gpus(devices, "2,1")], [2, 1])
        self.assertEqual([gpu.index for gpu in filter_visible_gpus(devices, "GPU-test-3")], [3])
        self.assertEqual(filter_visible_gpus(devices, "-1"), [])
        with self.assertRaises(ValueError):
            filter_visible_gpus(devices, "1,1")


class OfflineWorkerTests(SoftWinRateCase):
    def worker_config(self, tasks):
        tasks_file = self.write_rows("tasks.jsonl", tasks)
        return {"model_path": str(self.root / "local-model"), "tasks_file": str(tasks_file),
                "results_file": str(self.root / "worker-results.jsonl"),
                "error_file": str(self.root / "worker-error.json"),
                "gpu_uuids": ["GPU-test-1"], "max_model_len": 128,
                "max_output_tokens": 16, "max_num_seqs": 2,
                "gpu_memory_utilization": 0.9, "seed": 42}

    def test_overlong_pair_fails_before_loading_model_and_never_truncates(self):
        import judge_worker
        config = self.worker_config([{"key": "long", "messages": [{"role": "user", "content": "original complete pair"}]}])
        tokenizer = types.SimpleNamespace(apply_chat_template=lambda *args, **kwargs: list(range(120)))
        with patch.dict(sys.modules, {"transformers": types.SimpleNamespace(
                AutoTokenizer=types.SimpleNamespace(from_pretrained=lambda *args, **kwargs: tokenizer)),
                "vllm": types.SimpleNamespace(LLM=lambda **kwargs: self.fail("Model loaded before length preflight"))}), \
                patch.dict(os.environ), contextlib.redirect_stderr(io.StringIO()):
            code = judge_worker.run_worker(config)
        self.assertNotEqual(code, 0)
        failure = json.loads(Path(config["error_file"]).read_text(encoding="utf-8"))
        self.assertEqual(failure["stage"], "preflight")
        self.assertIn("no text was truncated", failure["message"])
        self.assertFalse(Path(config["results_file"]).exists())

    def test_offline_worker_preserves_order_flags_and_reports_finish_reason(self):
        import judge_worker
        config = self.worker_config(self.tasks())
        template_options = []
        load_options = []

        def render(messages, **kwargs):
            template_options.append(kwargs)
            return [10, 20, 30]

        def tokenizer_loader(*args, **kwargs):
            self.assertTrue(kwargs["local_files_only"])
            return types.SimpleNamespace(apply_chat_template=render)

        def model_loader(**kwargs):
            load_options.append(kwargs)
            self.assertNotIn("OPENAI_API_KEY", os.environ)
            return types.SimpleNamespace(generate=lambda batch, sampling, **options: [
                types.SimpleNamespace(outputs=[types.SimpleNamespace(text='{"winner":"A","reason":"test"}',
                    finish_reason="stop", token_ids=[1, 2])]) for _ in batch])

        with patch.dict(sys.modules, {"transformers": types.SimpleNamespace(
                AutoTokenizer=types.SimpleNamespace(from_pretrained=tokenizer_loader)),
                "vllm": types.SimpleNamespace(LLM=model_loader, SamplingParams=lambda **kwargs: kwargs)}), \
                patch.dict(os.environ, {"OPENAI_API_KEY": "offline-test-placeholder"}), \
                contextlib.redirect_stderr(io.StringIO()):
            code = judge_worker.run_worker(config)
        self.assertEqual(code, 0)
        results = [json.loads(line) for line in Path(config["results_file"]).read_text(encoding="utf-8").splitlines()]
        self.assertEqual(len(results), 2)
        self.assertEqual({item["key"] for item in results}, {task["key"] for task in self.tasks()})
        self.assertTrue(all(item["finish_reason"] == "stop" for item in results))
        self.assertTrue(all(options["enable_thinking"] is False for options in template_options))
        self.assertEqual(load_options[0]["tensor_parallel_size"], 1)


class CachedRunAndReportTests(SoftWinRateCase):
    def setUp(self):
        super().setUp()
        self.model = self.root / "local-model"
        self.model.mkdir()
        (self.model / "config.json").write_text(json.dumps({"model_type": "qwen3", "hidden_size": 512,
            "num_attention_heads": 8, "num_key_value_heads": 2, "num_hidden_layers": 2,
            "head_dim": 64}), encoding="utf-8")
        (self.model / "tokenizer.json").write_text("{}", encoding="utf-8")
        (self.model / "model.safetensors").write_bytes(b"offline test weights")
        self.config = swr.JudgeConfig(model_path=self.model, bootstrap=50, retries=0)
        self.output = self.root / "results"
        self.history = self.root / "history.md"

    def run_evaluation(self, candidate, reference, runner=None, **kwargs):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return swr.run_evaluation(candidate, reference, self.config, self.output, self.history,
                                      runner=runner, **kwargs)

    def winning_results(self, tasks, config, attempt_dir):
        return [{"key": task["key"], "finish_reason": "stop", "prompt_tokens": 100,
                 "completion_tokens": 20, "text": json.dumps(self.judgment("B" if task["swapped"] else "A"))}
                for task in tasks]

    def test_completed_cache_reuses_all_judgments_and_history_appends_each_run(self):
        candidate, reference = self.sources(("one", "two"))
        original = candidate.read_bytes(), reference.read_bytes()
        self.history.write_text("Earlier results stay intact.\n", encoding="utf-8")
        calls = []

        def first_runner(tasks, config, attempt_dir):
            calls.append([task["key"] for task in tasks])
            return self.winning_results(tasks, config, attempt_dir)

        first = self.run_evaluation(candidate, reference, first_runner)
        cache_before = Path(first["cache_file"]).read_bytes()
        with patch.object(swr, "run_auto_gpu", side_effect=AssertionError("Completed cache must not launch a GPU worker")):
            second = self.run_evaluation(candidate, reference)
        self.assertEqual(len(calls), 1)
        self.assertEqual(first["soft_win_rate"], 1.0)
        self.assertEqual(second["soft_win_rate"], 1.0)
        self.assertEqual(second["cache_reused_rounds"], 4)
        self.assertEqual(second["new_judgments"], 0)
        self.assertEqual(Path(second["cache_file"]).read_bytes(), cache_before)
        self.assertNotEqual(first["run_file"], second["run_file"])
        self.assertTrue(Path(first["run_file"]).is_file())
        self.assertTrue(Path(second["run_file"]).is_file())
        history = self.history.read_text(encoding="utf-8")
        self.assertTrue(history.startswith("Earlier results stay intact.\n"))
        self.assertEqual(history.count("## 评测记录"), 2)
        self.assertIn("Soft Win Rate", history)
        self.assertIn("固定 Clean-KD", history)
        self.assertIn("平局半分", history)
        self.assertEqual((candidate.read_bytes(), reference.read_bytes()), original)

    def test_partial_run_caches_successful_order_and_resumes_only_missing_order(self):
        candidate, reference = self.sources()
        first = self.run_evaluation(candidate, reference,
            lambda tasks, config, directory: self.winning_results(tasks[:1], config, directory))
        self.assertFalse(first["complete"])
        self.assertEqual(first["num_valid_samples"], 0)
        self.assertIsNone(first["soft_win_rate"])
        pending_sizes = []

        def resumed_runner(tasks, config, directory):
            pending_sizes.append(len(tasks))
            return self.winning_results(tasks, config, directory)

        second = self.run_evaluation(candidate, reference, resumed_runner)
        self.assertEqual(pending_sizes, [1])
        self.assertTrue(second["complete"])
        self.assertEqual(second["cache_reused_rounds"], 1)
        self.assertEqual(second["new_judgments"], 1)
        self.assertEqual(second["soft_win_rate"], 1.0)

    def test_summary_only_does_not_start_inference_when_no_cache_exists(self):
        candidate, reference = self.sources()
        with patch.object(swr, "run_auto_gpu", side_effect=AssertionError("Summary-only mode cannot start inference")):
            result = self.run_evaluation(candidate, reference, summary_only=True)
        self.assertFalse(result["complete"])
        self.assertEqual(result["new_judgments"], 0)
        self.assertIsNone(result["soft_win_rate"])

    def test_changed_model_assets_invalidate_scoring_cache_without_modifying_reference(self):
        candidate, reference = self.sources()
        original_reference = reference.read_bytes()
        first = self.run_evaluation(candidate, reference, self.winning_results)
        (self.model / "tokenizer.json").write_text('{"revision":2}', encoding="utf-8")
        second = self.run_evaluation(candidate, reference, self.winning_results)
        self.assertNotEqual(first["cache_file"], second["cache_file"])
        self.assertEqual(second["cache_reused_rounds"], 0)
        self.assertEqual(second["new_judgments"], 2)
        self.assertEqual(reference.read_bytes(), original_reference)

    def test_refused_invalid_or_truncated_outputs_never_count_as_ties(self):
        candidate, reference = self.sources()

        def broken_runner(tasks, config, directory):
            return [{"key": task["key"], "finish_reason": "length" if task["swapped"] else "stop",
                     "text": json.dumps(self.judgment("A")) if task["swapped"] else "I cannot judge"}
                    for task in tasks]

        result = self.run_evaluation(candidate, reference, broken_runner)
        self.assertFalse(result["complete"])
        self.assertEqual(result["num_valid_samples"], 0)
        self.assertEqual(result["num_valid_rounds"], 0)
        self.assertIsNone(result["soft_win_rate"])
        self.assertIsNone(result["tie_rate"])
        self.assertEqual(result["new_judgments"], 0)

    def test_history_cannot_overwrite_candidate_or_fixed_reference(self):
        candidate, reference = self.sources()
        original = candidate.read_bytes(), reference.read_bytes()
        for protected in (candidate, reference):
            with self.subTest(protected=protected), self.assertRaises(ValueError), \
                    contextlib.redirect_stdout(io.StringIO()):
                swr.run_evaluation(candidate, reference, self.config, self.output, protected,
                                   runner=self.winning_results)
            self.assertEqual((candidate.read_bytes(), reference.read_bytes()), original)


    def test_interrupted_worker_results_are_recovered_without_rejudging(self):
        candidate, reference = self.sources()

        def interrupted(tasks, config, directory):
            plan = directory / "plan_00"
            plan.mkdir()
            (plan / "worker_config.json").write_text(json.dumps({"gpu_ids": [1], "tensor_parallel_size": 1}), encoding="utf-8")
            (plan / "tasks.jsonl").write_text("".join(json.dumps(task) + "\n" for task in tasks), encoding="utf-8")
            output = self.winning_results(tasks, config, directory)
            (plan / "raw_results.jsonl").write_text("".join(json.dumps(row) + "\n" for row in output)
                                                     + '{"incomplete":', encoding="utf-8")
            raise KeyboardInterrupt

        with self.assertRaises(KeyboardInterrupt):
            self.run_evaluation(candidate, reference, interrupted)
        with patch.object(swr, "run_auto_gpu", side_effect=AssertionError("Recovered complete pair must not be judged again")):
            result = self.run_evaluation(candidate, reference)
        self.assertTrue(result["complete"])
        self.assertEqual(result["soft_win_rate"], 1.0)
        self.assertEqual(result["recovered_judgments"], 2)
        self.assertEqual(result["new_judgments"], 0)
        self.assertEqual(result["execution_plans"][0]["gpu_ids"], [1])

    def test_incomplete_master_cache_tail_is_backed_up_and_does_not_block_resume(self):
        candidate, reference = self.sources()
        first = self.run_evaluation(candidate, reference, self.winning_results)
        cache = Path(first["cache_file"])
        complete_bytes = cache.read_bytes()
        with cache.open("ab") as handle:
            handle.write(b'{"interrupted":')
        with patch.object(swr, "run_auto_gpu", side_effect=AssertionError("Only cache tail repair was needed")):
            second = self.run_evaluation(candidate, reference)
        self.assertTrue(second["complete"])
        self.assertEqual(cache.read_bytes(), complete_bytes)
        backups = list(cache.parent.glob("judgments.jsonl.interrupted_*"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_bytes(), b'{"interrupted":')

    def test_small_limit_run_and_full_run_share_the_same_judgment_cache(self):
        candidate, reference = self.sources(("one", "two"))
        first = self.run_evaluation(candidate, reference, self.winning_results, limit=1)
        pending = []

        def finish(tasks, config, directory):
            pending.extend(task["id"] for task in tasks)
            return self.winning_results(tasks, config, directory)

        full = self.run_evaluation(candidate, reference, finish)
        self.assertEqual(first["cache_file"], full["cache_file"])
        self.assertEqual(pending, ["two", "two"])
        self.assertEqual(full["cache_reused_rounds"], 2)
        self.assertEqual(full["num_valid_samples"], 2)


class AutomaticWorkerFallbackTests(SoftWinRateCase):
    winning_results = CachedRunAndReportTests.winning_results

    def test_own_process_group_is_cleaned_even_if_top_worker_already_exited(self):
        process = types.SimpleNamespace(pid=9876, poll=lambda: 0, wait=lambda **kwargs: 0)
        with patch.object(swr.os, "name", "posix"), \
                patch.object(swr.os, "killpg", create=True, side_effect=[None, ProcessLookupError]) as kill_group:
            swr.stop_worker(process)
        self.assertEqual(kill_group.call_args_list[0].args, (9876, swr.signal.SIGTERM))
        self.assertEqual(kill_group.call_args_list[1].args, (9876, 0))

    def test_memory_failure_tries_next_valid_gpu_plan_without_changing_parent_cuda_mask(self):
        import gpu_runtime as gpu
        self.model = self.root / "local-model"
        self.config = swr.JudgeConfig(model_path=self.model)
        tasks = self.tasks()
        plans = [gpu.GPUPlan((1,), ("GPU-one",), 1, .8, 68000),
                 gpu.GPUPlan((0, 2), ("GPU-zero", "GPU-two"), 2, .8, 35000)]
        inventory = [gpu.GPU(1, "GPU-one", "A100", 81920, 75000, 0),
                     gpu.GPU(0, "GPU-zero", "A100", 40960, 40000, 0),
                     gpu.GPU(2, "GPU-two", "A100", 40960, 40000, 0)]
        spawned = []

        def fake_process(command, **kwargs):
            config = json.loads(Path(command[-1]).read_text(encoding="utf-8"))
            spawned.append((config, kwargs["env"]))
            code = 42 if len(spawned) == 1 else 0
            if code == 0:
                batch = [json.loads(line) for line in Path(config["tasks_file"]).read_text(encoding="utf-8").splitlines()]
                rows = self.winning_results(batch, self.config, self.root)
                Path(config["results_file"]).write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
            return types.SimpleNamespace(pid=1234, returncode=code, poll=lambda: code, wait=lambda **options: code)

        config = swr.JudgeConfig(model_path=self.model, max_num_seqs=1, bootstrap=20)
        with patch.object(gpu, "discover_gpus", return_value=inventory), \
                patch.object(gpu, "load_model_spec", return_value=None), \
                patch.object(gpu, "plan_gpus", return_value=plans), \
                patch.object(swr.subprocess, "Popen", side_effect=fake_process), \
                patch.object(swr, "stop_worker") as cleanup, \
                patch.dict(os.environ, {"CUDA_VISIBLE_DEVICES": "original-mask", "OPENAI_API_KEY": "not-a-real-key"}), \
                contextlib.redirect_stdout(io.StringIO()):
            results = swr.run_auto_gpu(tasks, config, self.root / "auto-attempt")
            self.assertEqual(os.environ["CUDA_VISIBLE_DEVICES"], "original-mask")
        self.assertEqual(len(spawned), 2)
        self.assertEqual(spawned[0][1]["CUDA_VISIBLE_DEVICES"], "GPU-one")
        self.assertEqual(spawned[1][1]["CUDA_VISIBLE_DEVICES"], "GPU-zero,GPU-two")
        self.assertNotIn("OPENAI_API_KEY", spawned[1][1])
        self.assertEqual(cleanup.call_count, 2)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["execution"]["tensor_parallel_size"], 2)


if __name__ == "__main__":
    unittest.main()
