"""Spawn-based, dynamically scheduled independent Student GPU workers.

Only the owning process writes checkpoints. Each child sees one explicitly
selected GPU and loads a complete model; this is data parallelism, not model
sharding. Importing this module does not import torch or initialize CUDA.
"""

from __future__ import annotations

from dataclasses import asdict
import importlib
import multiprocessing as mp
import os
from pathlib import Path
import queue
import sys
import time
from typing import Callable, Iterator


def _core_module():
    # A direct ``python baseline_acl/paraphrase_tp.py`` run defines its
    # dataclasses in __main__, not baseline_acl.paraphrase_tp. Reconstructing
    # responses from a second imported copy would fail the owner's strict
    # isinstance check despite identical fields. Only trust the actual core
    # script path, never an unrelated test/application's __main__ module.
    main_module = sys.modules.get("__main__")
    main_path = getattr(main_module, "__file__", None)
    if (main_path is not None
            and Path(main_path).resolve() == Path(__file__).with_name("paraphrase_tp.py").resolve()
            and all(hasattr(main_module, name) for name in ("GeneratedResponse", "GenerationConfig", "StudentGenerator"))):
        return main_module
    if __package__:
        return importlib.import_module(".paraphrase_tp", __package__)
    return importlib.import_module("paraphrase_tp")


def _default_worker_factory(model: str, config, tokenizer_path: str, gpu_id: str):
    raise ValueError("student TP requires an explicit rule-bound worker factory")


def _worker_entry(model: str, config_dict: dict, tokenizer_path: str, gpu_id: str,
                  jobs, events, worker_factory: Callable | None) -> None:
    os.environ["CUDA_VISIBLE_DEVICES"] = gpu_id
    current_job = None
    generator = None
    try:
        config = _core_module().GenerationConfig(**config_dict)
        generator = (worker_factory or _default_worker_factory)(model, config, tokenizer_path, gpu_id)
        events.put({"kind": "ready", "gpu": gpu_id})
        while True:
            job = jobs.get()
            if job is None:
                break
            current_job = job
            events.put({"kind": "started", "gpu": gpu_id, "job_id": job["job_id"]})
            candidates = generator.generate([job["prepared"]], [job["index"]], [job["attempt"]])
            if len(candidates) != 1:
                raise RuntimeError("Student worker must return exactly one complete response per job")
            # Plain dictionaries avoid pickling __main__.GeneratedResponse when
            # the public script is launched directly instead of as a package.
            candidate = candidates[0]
            payload = {"text": candidate.text, "finish_reason": candidate.finish_reason,
                       "output_tokens": candidate.output_tokens, "windows": candidate.windows,
                       "issues": candidate.issues}
            events.put({"kind": "result", "gpu": gpu_id, "job_id": job["job_id"],
                        "index": job["index"], "attempt": job["attempt"], "candidate": payload})
            current_job = None
    except BaseException as error:
        # Reporting CUDA OOM/startup errors to the parent never affects other
        # users' processes. SIGKILL is handled by the parent's liveness checks.
        try:
            events.put({"kind": "error", "gpu": gpu_id,
                        "job_id": current_job["job_id"] if current_job else None,
                        "index": current_job["index"] if current_job else None,
                        "error_type": type(error).__name__, "error": str(error)[:2000]})
        except BaseException:
            pass
    finally:
        if generator is not None and hasattr(generator, "close"):
            try:
                generator.close()
            except BaseException:
                pass


class ParallelStudentGenerator:
    """One persistent full-model worker per GPU with a shared dynamic queue.

    ``worker_factory`` is a spawn-picklable top-level callable intended for CPU
    tests. Production TP supplies its rule-bound factory. It receives
    ``(model, GenerationConfig, tokenizer_path, gpu_id)`` and returns an object
    implementing the same ``generate`` method as StudentGenerator.
    """

    def __init__(self, model: str, config, tokenizer_path: str, gpu_ids: list[str], *,
                 worker_factory: Callable | None = None, startup_timeout: float = 1800):
        config.validate()
        if not gpu_ids or any(not isinstance(gpu, str) or not gpu.strip() or "," in gpu
                              or gpu == "-1" or gpu != gpu.strip() for gpu in gpu_ids):
            raise ValueError("supply at least one explicit CUDA GPU ID without commas or whitespace")
        if len(set(gpu_ids)) != len(gpu_ids):
            raise ValueError("CUDA GPU IDs must be unique")
        if startup_timeout <= 0:
            raise ValueError("worker startup timeout must be positive")
        self.worker_count = len(gpu_ids)
        self.gpu_ids = list(gpu_ids)
        self._closed = False
        self._active = False
        self._next_job_id = 0
        self._context = mp.get_context("spawn")
        self._jobs = self._context.Queue(maxsize=2 * self.worker_count)
        self._events = self._context.Queue(maxsize=4 * self.worker_count)
        self._processes = []
        try:
            for gpu in self.gpu_ids:
                process = self._context.Process(
                    target=_worker_entry,
                    args=(model, asdict(config), tokenizer_path, gpu, self._jobs, self._events, worker_factory),
                    name=f"student-gpu-{gpu}",
                )
                process.start()
                self._processes.append((gpu, process))
            deadline = time.monotonic() + startup_timeout
            ready = set()
            while len(ready) < self.worker_count:
                if time.monotonic() >= deadline:
                    missing = [gpu for gpu in self.gpu_ids if gpu not in ready]
                    raise RuntimeError(f"Student workers did not load before startup timeout; GPUs: {missing}")
                event = self._get_event(deadline=deadline)
                if event is None:
                    continue
                self._raise_worker_error(event)
                if event["kind"] != "ready" or event.get("gpu") not in self.gpu_ids or event["gpu"] in ready:
                    raise RuntimeError("unexpected event while starting Student workers")
                ready.add(event["gpu"])
                print(f"[worker-ready] GPU={event['gpu']}, loaded={len(ready)}/{self.worker_count}", flush=True)
        except BaseException:
            self.close()
            raise

    def _check_workers(self) -> None:
        for gpu, process in self._processes:
            if not process.is_alive():
                raise RuntimeError(f"Student worker on GPU {gpu} exited unexpectedly (exit code {process.exitcode}); "
                                   "check available GPU memory and the worker error above; completed rows remain checkpointed")

    @staticmethod
    def _raise_worker_error(event: dict) -> None:
        if event.get("kind") == "error":
            location = f" at row {event['index']}" if event.get("index") is not None else " during model loading"
            raise RuntimeError(f"Student worker on GPU {event.get('gpu')}{location}: "
                               f"{event.get('error_type')}: {event.get('error')}")

    def _get_event(self, *, deadline: float | None = None) -> dict | None:
        timeout = 0.25 if deadline is None else max(0.001, min(0.25, deadline - time.monotonic()))
        try:
            return self._events.get(timeout=timeout)
        except queue.Empty:
            self._check_workers()
            return None

    def iter_generate(self, prepared_rows: list[dict], indices: list[int], attempts: list[int]) -> Iterator:
        """Yield ``(global_row_index, attempt, GeneratedResponse)`` as rows finish.

        At most twice the worker count is in flight. Workers pull the next row
        immediately, so shorter/faster generations receive more work. Returning
        early, a worker error, or Ctrl+C closes only this pool's child processes.
        """
        if self._closed:
            raise RuntimeError("Student worker pool is closed")
        if self._active:
            raise RuntimeError("only one Student generation iterator may run at a time")
        if not (len(prepared_rows) == len(indices) == len(attempts)):
            raise ValueError("Student rows, indices, and attempts must have equal lengths")
        if len(set(indices)) != len(indices):
            raise ValueError("Student row indices must be unique within one submission")
        if any(type(index) is not int or index < 0 for index in indices):
            raise ValueError("Student global row indices must be nonnegative integers")
        if any(type(attempt) is not int or attempt < 1 for attempt in attempts):
            raise ValueError("Student attempt numbers must be positive integers")
        self._active = True
        completed = False
        submitted = 0
        inflight = {}
        limit = 2 * self.worker_count

        def submit_next() -> None:
            nonlocal submitted
            job_id = self._next_job_id
            self._next_job_id += 1
            job = {"job_id": job_id, "prepared": prepared_rows[submitted],
                   "index": indices[submitted], "attempt": attempts[submitted]}
            # The in-flight bound guarantees queue capacity: every queued job
            # is in inflight, while some inflight jobs are already processing.
            self._jobs.put(job)
            inflight[job_id] = (job["index"], job["attempt"])
            submitted += 1

        try:
            self._check_workers()
            while submitted < len(indices) and len(inflight) < limit:
                submit_next()
            while inflight:
                event = self._get_event()
                if event is None:
                    continue
                self._raise_worker_error(event)
                job_id = event.get("job_id")
                if event.get("gpu") not in self.gpu_ids or job_id not in inflight:
                    raise RuntimeError("Student worker returned an unknown or duplicate job")
                if event["kind"] == "started":
                    continue
                if event["kind"] != "result":
                    raise RuntimeError("unexpected Student worker event")
                index, attempt = inflight.pop(job_id)
                if event.get("index") != index or event.get("attempt") != attempt:
                    raise RuntimeError("Student worker result does not match its submitted row/attempt")
                candidate = _core_module().GeneratedResponse(**event["candidate"])
                if submitted < len(indices):
                    submit_next()
                yield index, attempt, candidate
            completed = True
        finally:
            self._active = False
            if not completed:
                self.close()

    def generate(self, prepared_rows: list[dict], indices: list[int], attempts: list[int]) -> list:
        """Compatibility adapter; orchestration should prefer iter_generate."""
        results = {index: candidate for index, _, candidate in self.iter_generate(prepared_rows, indices, attempts)}
        return [results[index] for index in indices]

    def close(self) -> None:
        """Idempotently stop only children and queues created by this object."""
        if self._closed:
            return
        self._closed = True
        # Brief cooperative shutdown first. Busy workers are then terminated by
        # their exact multiprocessing Process handles, never by global searches.
        for _ in self._processes:
            try:
                self._jobs.put_nowait(None)
            except (queue.Full, ValueError, OSError):
                break
        deadline = time.monotonic() + 1.0
        for _, process in self._processes:
            process.join(timeout=max(0.0, deadline - time.monotonic()))
        for _, process in self._processes:
            if process.is_alive():
                process.terminate()
        deadline = time.monotonic() + 3.0
        for _, process in self._processes:
            process.join(timeout=max(0.0, deadline - time.monotonic()))
        for _, process in self._processes:
            if process.is_alive() and hasattr(process, "kill"):
                process.kill()
                process.join(timeout=1.0)
        for own_queue in (self._jobs, self._events):
            # A terminated consumer can leave pending bytes in a feeder thread;
            # joining that feeder could block forever. Queues are not reused.
            own_queue.cancel_join_thread()
            own_queue.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

