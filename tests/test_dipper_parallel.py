"""Real spawned CPU workers exercise multi-GPU scheduling without CUDA."""

import json
import multiprocessing as mp
import os
from pathlib import Path
import sys
import time
from types import ModuleType
import unittest
from unittest.mock import patch

from baseline_acl import dipper_parallel, paraphrase_up
from baseline_acl.dipper_parallel import ParallelDipperGenerator
from baseline_acl.paraphrase_up import DipperGenerator, GeneratedResponse, GenerationConfig, generation_seed


class MockDipperWorker:
    def __init__(self, config, gpu_id):
        self.config = config
        self.gpu_id = gpu_id

    def generate(self, rows, indices, attempts):
        result = []
        for row, index, attempt in zip(rows, indices, attempts, strict=True):
            if row.get("die"):
                os._exit(7)
            if row.get("fail"):
                raise RuntimeError("mock CUDA out of memory")
            time.sleep(row.get("delay", 0))
            payload = {"index": index, "attempt": attempt, "gpu": self.gpu_id,
                       "visible": os.environ["CUDA_VISIBLE_DEVICES"],
                       "seed": generation_seed(self.config.seed, index, attempt), "prepared": row}
            result.append(GeneratedResponse(json.dumps(payload), "stop", 12, [{"seed": payload["seed"]}], []))
        return result


def mock_worker_factory(model, config, tokenizer_path, gpu_id):
    # A top-level callable is genuinely spawn-picklable on Windows and Linux.
    if gpu_id == "bad":
        raise RuntimeError("mock model initialization failure")
    return MockDipperWorker(config, gpu_id)


class DirectEntryGeneratedResponse(GeneratedResponse):
    """Distinct class simulates the direct script owner's dataclass identity."""


class DipperParallelTests(unittest.TestCase):
    def make_pool(self, gpu_ids=None):
        return ParallelDipperGenerator("unused-local-model", GenerationConfig(), "unused-tokenizer",
                                       gpu_ids or ["1", "3"], worker_factory=mock_worker_factory,
                                       startup_timeout=15)

    def assert_stopped(self, pool):
        self.assertTrue(pool._closed)
        self.assertTrue(all(not process.is_alive() for _, process in pool._processes))

    def test_spawn_mask_out_of_order_dynamic_scheduling_and_global_row_seed(self):
        with self.make_pool() as pool:
            self.assertEqual(pool._context.get_start_method(), "spawn")
            self.assertEqual(pool.worker_count, 2)
            rows = [{"delay": 0.7 if i == 0 else 0.02, "source": str(i)} for i in range(10)]
            indices = [100 + i for i in range(10)]
            attempts = [2] * 10
            results = list(pool.iter_generate(rows, indices, attempts))
            self.assertNotEqual(results[0][0], 100, "must emit fast rows before the slow row completes")
            self.assertEqual(set(index for index, _, _ in results), set(indices))
            by_gpu = {gpu: [] for gpu in pool.gpu_ids}
            for index, attempt, candidate in results:
                payload = json.loads(candidate.text)
                self.assertEqual(payload["index"], index)
                self.assertEqual(attempt, 2)
                self.assertEqual(payload["visible"], payload["gpu"])
                self.assertEqual(payload["seed"], generation_seed(42, index, attempt))
                self.assertEqual(payload["prepared"], rows[index - 100])
                self.assertEqual(candidate.windows, [{"seed": payload["seed"]}])
                by_gpu[payload["gpu"]].append(index)
            # The worker processing the long first job cannot receive a static
            # half of the dataset; the faster worker draws almost all the rest.
            self.assertGreater(max(map(len, by_gpu.values())), 5)
        self.assert_stopped(pool)
        pool.close()  # idempotent

    def test_ordered_adapter_and_persistent_pool_multiple_submissions(self):
        with self.make_pool() as pool:
            results = pool.generate([{"delay": 0.1}, {}], [7, 2], [1, 3])
            self.assertEqual([json.loads(candidate.text)["index"] for candidate in results], [7, 2])
            again = list(pool.iter_generate([{}], [99], [4]))
            self.assertEqual(again[0][:2], (99, 4))
            self.assertEqual(pool.generate([], [], []), [])
        self.assert_stopped(pool)

    def test_three_spawned_workers_receive_all_rows_once_with_stable_seeds(self):
        with self.make_pool(["1", "2", "3"]) as pool:
            indices = list(range(90, 108))
            results = list(pool.iter_generate([{"delay": .08}] * len(indices), indices, [2] * len(indices)))
            self.assertEqual(pool.worker_count, 3)
            self.assertEqual(sorted(index for index, _, _ in results), indices)
            payloads = [json.loads(candidate.text) for _, _, candidate in results]
            self.assertEqual({payload["gpu"] for payload in payloads}, {"1", "2", "3"})
            for payload in payloads:
                self.assertEqual(payload["visible"], payload["gpu"])
                self.assertEqual(payload["seed"], generation_seed(42, payload["index"], 2))
        self.assert_stopped(pool)

    def test_core_resolution_prefers_only_the_actual_direct_entry_module(self):
        direct_main = ModuleType("__main__")
        direct_main.__file__ = str(Path(paraphrase_up.__file__).resolve())
        direct_main.GeneratedResponse = DirectEntryGeneratedResponse
        direct_main.GenerationConfig = GenerationConfig
        direct_main.DipperGenerator = DipperGenerator
        with patch.dict(sys.modules, {"__main__": direct_main}):
            self.assertIs(dipper_parallel._core_module(), direct_main)
            direct_main.__file__ = str(Path(__file__).resolve())
            self.assertIs(dipper_parallel._core_module(), paraphrase_up)
            del direct_main.__file__
            self.assertIs(dipper_parallel._core_module(), paraphrase_up)

    def test_real_spawn_with_direct_script_main_reconstructs_owners_response_class(self):
        # Spawn will run the real paraphrase_up.py as __mp_main__, exactly as
        # the production direct CLI does, without executing its guarded main().
        # Only the parent response class is substituted; plain result dicts must
        # be reconstructed as that exact owning class, not an imported copy.
        direct_main = ModuleType("__main__")
        direct_main.__file__ = str(Path(paraphrase_up.__file__).resolve())
        direct_main.__spec__ = None
        direct_main.GeneratedResponse = DirectEntryGeneratedResponse
        direct_main.GenerationConfig = GenerationConfig
        direct_main.DipperGenerator = DipperGenerator
        with patch.dict(sys.modules, {"__main__": direct_main}):
            with self.make_pool(["3"]) as pool:
                [(index, attempt, candidate)] = list(pool.iter_generate([{}], [17], [2]))
                self.assertEqual((index, attempt), (17, 2))
                self.assertIs(type(candidate), DirectEntryGeneratedResponse)
                self.assertIsInstance(candidate, direct_main.GeneratedResponse)
        self.assert_stopped(pool)

    def test_worker_error_reports_selected_gpu_and_cleans_own_workers(self):
        pool = self.make_pool(["3"])
        with self.assertRaisesRegex(RuntimeError, "GPU 3 at row 81.*mock CUDA out of memory"):
            list(pool.iter_generate([{"fail": True}], [81], [1]))
        self.assert_stopped(pool)

    def test_abrupt_worker_exit_detected_without_hanging(self):
        pool = self.make_pool(["2"])
        started = time.monotonic()
        with self.assertRaisesRegex(RuntimeError, "GPU 2 exited unexpectedly.*7"):
            list(pool.iter_generate([{"die": True}], [4], [1]))
        self.assertLess(time.monotonic() - started, 6)
        self.assert_stopped(pool)

    def test_stopping_iterator_early_closes_pool(self):
        pool = self.make_pool()
        iterator = pool.iter_generate([{}, {"delay": 2}, {}, {}], [1, 2, 3, 4], [1] * 4)
        next(iterator)
        iterator.close()
        self.assert_stopped(pool)

    def test_startup_error_cleans_children(self):
        previous = {child.pid for child in mp.active_children()}
        with self.assertRaisesRegex(RuntimeError, "GPU bad during model loading.*initialization failure"):
            self.make_pool(["1", "bad"])
        leaked = [child for child in mp.active_children()
                  if child.pid not in previous and child.name.startswith("dipper-gpu-")]
        self.assertEqual(leaked, [])

    def test_argument_validation(self):
        with self.assertRaisesRegex(ValueError, "equal lengths"):
            with self.make_pool(["1"]) as pool:
                list(pool.iter_generate([{}], [1, 2], [1]))
        with self.make_pool(["1"]) as pool:
            for indices, attempts, message in (([1, 1], [1, 1], "unique"),
                                              ([-1], [1], "nonnegative"),
                                              ([1], [0], "positive")):
                with self.assertRaisesRegex(ValueError, message):
                    list(pool.iter_generate([{}] * len(indices), indices, attempts))
            self.assertFalse(pool._closed)
        for gpu_ids, message in (([], "at least one"), (["1", "1"], "unique"),
                                 (["1,3"], "without commas"), (["-1"], "explicit"),
                                 ([" 1"], "whitespace")):
            with self.assertRaisesRegex(ValueError, message):
                ParallelDipperGenerator("unused", GenerationConfig(), "unused", gpu_ids,
                                        worker_factory=mock_worker_factory)


if __name__ == "__main__":
    unittest.main()
