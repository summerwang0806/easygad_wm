"""Offline mechanism and resumable-generation contracts, no downloaded models."""
from __future__ import annotations

from contextlib import redirect_stdout
import io
import json
import math
import os
from pathlib import Path
import pickle
import sys
import tempfile
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
import torch

from baseline_lsh import detect, generate, prepare
from baseline_lsh.core import ASSET_VERSION, BucketAsset, LSHConfig, LSHLogitsProcessor, LSHWatermark, project_buckets, tokenizer_identity
from baseline_lsh.io_utils import (atomic_json, commit_part, ensure_manifest, prompt_ids,
                                   read_json, read_part, run_lock, validate_preserved)

ROOT = Path(__file__).resolve().parents[2]


class FakeBackend:
    def to_str(self):
        return json.dumps({"model": {"vocab": {f"t{i}": i for i in range(32)}}, "padding": None})


class FakeTokenizer:
    all_special_ids = [31]
    chat_template = "fake-template-v1"
    backend_tokenizer = FakeBackend()

    def get_vocab(self):
        return {f"t{i}": i for i in range(32)}

    def encode(self, text, add_special_tokens=False):
        return [ord(c) % 32 for c in text]

    def apply_chat_template(self, messages, add_generation_prompt, tokenize):
        return "|".join(m["content"] for m in messages) + "?"


class FakeAutoTokenizer:
    @staticmethod
    def from_pretrained(*args, **kwargs):
        return FakeTokenizer()


class FakeEngine:
    calls = []
    instances = 0
    fail_call = None

    def __init__(self, **kwargs):
        type(self).instances += 1

    def generate(self, prompts, sampling_params, use_tqdm):
        cls = type(self)
        cls.calls.append([(p["prompt_token_ids"], s["seed"], s["logits_processors"]) for p, s in zip(prompts, sampling_params)])
        if cls.fail_call == len(cls.calls):
            raise RuntimeError("synthetic interrupted engine")
        result = []
        for prompt, params in zip(prompts, sampling_params):
            text = " " + chr(97 + params["seed"] % 3) * 3
            ids = FakeTokenizer().encode(text)
            # Exercise the actual processor for every token, like a decoder.
            for j, token in enumerate(ids):
                for processor in params["logits_processors"] or []:
                    processor(prompt["prompt_token_ids"], ids[:j], torch.zeros(34))
            result.append(SimpleNamespace(prompt_token_ids=prompt["prompt_token_ids"],
                          outputs=[SimpleNamespace(text=text, token_ids=ids, finish_reason="stop", stop_reason=None)]))
        return result


def make_asset(token_ids=None, buckets=None):
    token_ids = np.arange(32) if token_ids is None else np.asarray(token_ids)
    buckets = token_ids % 4 if buckets is None else np.asarray(buckets)
    identity = tokenizer_identity(FakeTokenizer())
    identity.update(num_tokens=len(token_ids), id_space=int(max(token_ids)) + 1)
    return BucketAsset(token_ids, buckets, np.eye(2, dtype=np.float32),
                       {"format": ASSET_VERSION, "lsh_bits": 2, "lsh_seed": 42,
                        "tokenizer": identity, "model": "/synthetic/teacher"})


def source_table(n=5):
    field = pa.field("teacher_response", pa.string(), nullable=False, metadata={b"field": b"preserve"})
    schema = pa.schema([pa.field("id", pa.string()),
                        pa.field("content", pa.list_(pa.struct([("role", pa.string()), ("content", pa.string())]))),
                        field, pa.field("extra", pa.int32())], metadata={b"source": b"keep exactly"})
    return pa.Table.from_pylist([{"id": f"id-{i}", "content": [{"role": "user", "content": f"question{i}"}],
                                 "teacher_response": "old", "extra": i} for i in range(n)], schema=schema)


class MechanismTests(unittest.TestCase):
    def test_hyperplane_geometry_and_positive_scaling(self):
        e = np.array([[1, 2], [-1, 2], [-1, -2], [1, -2]], dtype=np.float32)
        planes = np.eye(2, dtype=np.float32)
        np.testing.assert_array_equal(project_buckets(e, planes), [3, 2, 0, 1])
        np.testing.assert_array_equal(project_buckets(10 * e, planes), project_buckets(e, planes))

    def test_shared_bucket_not_raw_previous_token_controls_rule(self):
        wm = LSHWatermark(make_asset())
        self.assertEqual(wm.asset.bucket(1), wm.asset.bucket(5))
        processor = LSHLogitsProcessor(wm)
        a = processor([1], [], torch.zeros(35))
        b = processor([29, 5], [], torch.zeros(35))
        c = processor([22], [7, 5], torch.zeros(35))
        torch.testing.assert_close(a, b)
        torch.testing.assert_close(a, c)
        self.assertTrue(torch.isneginf(a[32:]).all())
        self.assertEqual(int((a[:32] > 0).sum()), 16)

    def test_balanced_odd_groups_exact_total_and_rates(self):
        asset = make_asset(np.arange(13), [0] * 3 + [1] * 5 + [2] * 5)
        wm = LSHWatermark(asset, LSHConfig(gamma=0.5))
        for previous in asset.token_ids:
            mask, rates = wm.partition_for_bucket(asset.bucket(previous))
            self.assertEqual(int(mask.sum()), 6)
            for group, ids in asset.groups.items():
                self.assertLess(abs(mask[ids].sum() - 0.5 * len(ids)), 1)
                self.assertEqual(rates[group], mask[ids].sum() / len(ids))

    def test_key_and_strength_are_separate(self):
        asset = make_asset()
        weak = LSHWatermark(asset, LSHConfig(delta=3))
        strong = LSHWatermark(asset, LSHConfig(delta=6))
        other = LSHWatermark(asset, LSHConfig(hash_key=23))
        np.testing.assert_array_equal(weak.partition_for_bucket(1)[0], strong.partition_for_bucket(1)[0])
        self.assertFalse(np.array_equal(weak.partition_for_bucket(1)[0], other.partition_for_bucket(1)[0]))
        lo = LSHLogitsProcessor(weak)([1], [], torch.zeros(32))
        hi = LSHLogitsProcessor(strong)([1], [], torch.zeros(32))
        torch.testing.assert_close(hi, 2 * lo)

    def test_processor_and_score_agree_at_each_decoding_step(self):
        wm = LSHWatermark(make_asset())
        processor = LSHLogitsProcessor(wm)
        prompt, tokens = [10, 1], [7, 10, 3, 2, 31, 2]
        flags = []
        for i, token in enumerate(tokens):
            logits = processor(prompt, tokens[:i], torch.zeros(32))
            flags.append(int(logits[token] > 0))
        result = wm.score(tokens, prompt)
        self.assertEqual(result["num_tokens"], len(tokens))
        self.assertEqual(result["green_tokens"], sum(flags))
        self.assertAlmostEqual(result["z_score"], (sum(flags) - len(tokens) / 2) / math.sqrt(len(tokens) / 4))
        self.assertEqual(wm.score(tokens)["num_tokens"], len(tokens) - 1)
        self.assertIsNone(wm.score([])["z_score"])
        self.assertEqual(wm.score(tokens, prompt, max_tokens=2)["num_tokens"], 2)

    def test_dedup_is_bucket_token_not_previous_token_token(self):
        wm = LSHWatermark(make_asset())
        result = wm.score([2, 5, 2], [1])
        self.assertEqual(result["num_tokens"], 3)
        self.assertEqual(result["dedup_num_tokens"], 2)

    def test_invalid_vocabulary_and_options_rejected(self):
        wm = LSHWatermark(make_asset([0, 2, 3], [0, 1, 1]))
        with self.assertRaises(ValueError):
            wm.score([1], [0])
        with self.assertRaises(ValueError):
            LSHLogitsProcessor(wm)([0], [], torch.zeros(3))
        result = LSHLogitsProcessor(wm)([0], [], torch.zeros(5))
        self.assertTrue(torch.isneginf(result[[1, 4]]).all())
        for kwargs in ({"gamma": 0}, {"delta": float("nan")}, {"partition": "wrong"}, {"hash_key": 0}):
            with self.assertRaises(ValueError):
                LSHConfig(**kwargs)

    def test_global_partition_and_pickle_keep_same_masks(self):
        wm = LSHWatermark(make_asset(), LSHConfig(partition="global"))
        for bucket in range(4):
            mask, rates = wm.partition_for_bucket(bucket)
            self.assertEqual(int(mask.sum()), 16)
            np.testing.assert_array_equal(rates, np.repeat(0.5, 4))
        processor = LSHLogitsProcessor(wm)
        expected = processor([2], [], torch.zeros(32))
        restored = pickle.loads(pickle.dumps(processor))
        self.assertFalse(restored._device_cache)
        torch.testing.assert_close(expected, restored([2], [], torch.zeros(32)))


class FilesAndPipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix=".lsh-test-", dir=ROOT)
        self.root = Path(self.temp.name).resolve()
        # Confirm cleanup stays within the explicitly writable workspace.
        if not self.root.is_relative_to(ROOT) or not self.root.name.startswith(".lsh-test-"):
            raise AssertionError("unsafe test cleanup path")
        self.addCleanup(self.temp.cleanup)
        FakeEngine.calls, FakeEngine.instances, FakeEngine.fail_call = [], 0, None

    def test_asset_roundtrip_fingerprint_and_no_overwrite(self):
        asset = make_asset()
        path = self.root / "asset.npz"
        asset.save(path)
        restored = BucketAsset.load(path)
        self.assertEqual(asset.sha256, restored.sha256)
        np.testing.assert_array_equal(asset.lookup, restored.lookup)
        restored.check_tokenizer(FakeTokenizer())
        with self.assertRaises(FileExistsError):
            asset.save(path)
        tok = FakeTokenizer()
        tok.chat_template = "changed template"
        with self.assertRaises(ValueError):
            restored.check_tokenizer(tok)

    def test_manifest_lock_and_corrupt_committed_part(self):
        directory = self.root / "parts"
        with run_lock(directory):
            with self.assertRaises(RuntimeError):
                with run_lock(directory):
                    pass
            ensure_manifest(directory, {"delta": 3})
            with self.assertRaises(ValueError):
                ensure_manifest(directory, {"delta": 6})
        source = source_table(2)
        generated = source.set_column(2, source.schema.field(2), pa.array(["new1", "new2"]))
        commit_part(directory, 0, source, generated, [{"id": "id-0"}, {"id": "id-1"}])
        read_part(directory, 0, source)
        (directory / "part-000000.scores.json").write_text("[]", encoding="utf-8")
        with self.assertRaises(ValueError):
            read_part(directory, 0, source)

    def test_nonresponse_fields_are_protected(self):
        source = source_table(2)
        with self.assertRaises(ValueError):
            validate_preserved(source, source.set_column(3, "extra", pa.array([50, 51], type=pa.int32())))

    def test_preparation_reads_only_chunked_embedding_and_freezes_buckets(self):
        model = self.root / "model"
        model.mkdir()
        (model / "config.json").write_text("{}", encoding="utf-8")
        (model / "model.safetensors").write_bytes(b"fake file; safe_open mocked")
        embedding = torch.arange(96).reshape(32, 3).to(torch.bfloat16)
        slices = []

        class FakeSlice:
            def get_shape(self):
                return list(embedding.shape)

            def __getitem__(self, item):
                slices.append(item[0])
                return embedding[item]

        class FakeSafeOpen:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def keys(self):
                return ["model.embed_tokens.weight"]

            def get_slice(self, key):
                self.assert_key = key
                return FakeSlice()

        transformers = ModuleType("transformers")
        transformers.AutoTokenizer = FakeAutoTokenizer
        safetensors = ModuleType("safetensors")
        safetensors.safe_open = lambda *args, **kwargs: FakeSafeOpen()
        output = self.root / "prepared.npz"
        with patch.dict(sys.modules, {"transformers": transformers, "safetensors": safetensors}), redirect_stdout(io.StringIO()):
            prepare.main(["--model", str(model), "--output", str(output), "--chunk-size", "7", "--lsh-bits", "2"])
        self.assertEqual([(s.start, s.stop) for s in slices], [(0, 7), (7, 14), (14, 21), (21, 28), (28, 32)])
        asset = BucketAsset.load(output)
        np.testing.assert_array_equal(asset.bucket_ids, project_buckets(embedding.float().numpy(), asset.planes))
        asset.check_tokenizer(FakeTokenizer())

    def test_sharded_embedding_resolution_and_path_guard(self):
        model = self.root / "model"
        model.mkdir()
        index = model / "model.safetensors.index.json"
        atomic_json(index, {"weight_map": {"model.embed_tokens.weight": "model-00001-of-00008.safetensors"}})
        self.assertEqual(prepare.locate_embedding(model, "model.embed_tokens.weight"), model / "model-00001-of-00008.safetensors")
        atomic_json(index, {"weight_map": {"model.embed_tokens.weight": "../outside.safetensors"}})
        with self.assertRaises(ValueError):
            prepare.locate_embedding(model, "model.embed_tokens.weight")

    def setup_run(self):
        model = self.root / "model"
        model.mkdir()
        (model / "config.json").write_text("{}", encoding="utf-8")
        (model / "model.safetensors").write_bytes(b"synthetic engine; never read as actual model weights")
        asset = make_asset()
        asset.metadata["model"] = str(model)
        asset.save(self.root / "asset.npz")
        pq.write_table(source_table(), self.root / "input.parquet")
        args = ["--input", str(self.root / "input.parquet"), "--model", str(model),
                "--asset", str(self.root / "asset.npz"), "--output", str(self.root / "out.parquet"),
                "--batch-size", "2", "--shard-size", "2"]
        transformers = ModuleType("transformers")
        transformers.AutoTokenizer = FakeAutoTokenizer
        vllm = ModuleType("vllm")
        vllm.LLM = FakeEngine
        vllm.SamplingParams = lambda **kwargs: kwargs
        return args, {"transformers": transformers, "vllm": vllm}

    def test_end_to_end_interruption_resume_finalization_and_offline_detection(self):
        args, modules = self.setup_run()
        versions = {"python": "test", "numpy": "test", "vllm": "test"}
        with patch.dict(sys.modules, modules), patch.object(generate, "runtime_versions", return_value=versions), patch.dict(os.environ), redirect_stdout(io.StringIO()):
            # Read-only preflight: no engine or output state.
            generate.main(args + ["--preflight"])
            self.assertEqual(FakeEngine.instances, 0)
            self.assertFalse((self.root / "out.parquet.parts").exists())
            FakeEngine.fail_call = 2
            with self.assertRaisesRegex(RuntimeError, "synthetic interrupted"):
                generate.main(args)
            self.assertFalse((self.root / "out.parquet").exists())
            self.assertTrue((self.root / "out.parquet.parts/part-000000.done.json").exists())
            self.assertFalse((self.root / "out.parquet.parts/run.lock").exists())
            FakeEngine.fail_call = None
            generate.main(args)
            completed_instances = FakeEngine.instances
            generate.main(args)  # Complete rerun must not instantiate the engine.
            self.assertEqual(FakeEngine.instances, completed_instances)
            output = pq.read_table(self.root / "out.parquet")
            validate_preserved(pq.read_table(self.root / "input.parquet"), output)
            self.assertTrue(all(t.startswith(" ") for t in output["teacher_response"].to_pylist()))
            report = read_json(self.root / "out.parquet.metadata.json")
            self.assertEqual(report["rows"], 5)
            scores = [json.loads(s) for s in (self.root / "out_lsh_scores.jsonl").read_text().splitlines()]
            self.assertEqual([r["generation_seed"] for r in scores], list(range(42, 47)))
            self.assertTrue(all(r["text_token_ids_match"] for r in scores))
            rescore = ["--input", str(self.root / "out.parquet"), "--asset", str(self.root / "asset.npz"),
                       "--output", str(self.root / "rescored.jsonl")]
            detect.main(rescore)
            rows = [json.loads(s) for s in (self.root / "rescored.jsonl").read_text().splitlines()]
            self.assertEqual([r["z_score"] for r in rows], [r["z_score"] for r in scores])
            with self.assertRaises(ValueError):
                generate.main(args + ["--delta", "6"])
            with self.assertRaises(ValueError):
                detect.main(rescore[:-1] + [str(self.root / "wrong.jsonl"), "--hash-key", "23"])

    def test_none_mode_never_injects_student_watermark(self):
        args, modules = self.setup_run()
        with patch.dict(sys.modules, modules), patch.object(generate, "runtime_versions", return_value={"vllm": "test"}), patch.dict(os.environ), redirect_stdout(io.StringIO()):
            generate.main(args + ["--watermark", "none"])
        self.assertTrue(all(p[2] is None for call in FakeEngine.calls for p in call))
        rows = [json.loads(s) for s in (self.root / "out_lsh_scores.jsonl").read_text().splitlines()]
        self.assertTrue(all(not r["watermark_enabled_during_generation"] for r in rows))
        self.assertTrue(all(r["is_watermarked"] is None for r in rows))

    def test_worker_partition_and_ordered_merge_contract(self):
        args, modules = self.setup_run()

        def run_two_workers(a, directory):
            # Execute the same internal CLI paths without actual GPUs/subprocesses.
            for rank in range(2):
                generate.main(a.cli_argv + ["--worker-rank", str(rank), "--worker-count", "2"])

        with patch.dict(sys.modules, modules), patch.object(generate, "runtime_versions", return_value={"vllm": "test"}), patch.dict(os.environ), patch.object(generate, "dispatch_workers", side_effect=run_two_workers), redirect_stdout(io.StringIO()):
            generate.main(args + ["--num-gpus", "2"])
        self.assertEqual(FakeEngine.instances, 2)
        actual_seeds = [p[1] for call in FakeEngine.calls for p in call]
        self.assertEqual(actual_seeds, [42, 43, 46, 44, 45])
        output = pq.read_table(self.root / "out.parquet")
        self.assertEqual(output["id"].to_pylist(), [f"id-{i}" for i in range(5)])

    def test_multigpu_refuses_implicit_or_extra_visible_devices(self):
        a = generate.parse_args(["--output", str(self.root / "x.parquet"), "--num-gpus", "2"])
        for visible in ("", "0", "0,0", "0,1,2", "-1,0"):
            with patch.dict(os.environ, {"CUDA_VISIBLE_DEVICES": visible}), patch.object(generate.subprocess, "Popen") as launch:
                with self.assertRaises(ValueError):
                    generate.dispatch_workers(a, self.root)
                launch.assert_not_called()

    def test_original_offsets_and_prompt_ids_survive_batching(self):
        args = generate.parse_args(["--output", str(self.root / "x.parquet"), "--batch-size", "2", "--shard-size", "3"])
        source = source_table(3)
        engine = FakeEngine()
        _, scores = generate.generate_shard(args, source, 10, FakeTokenizer(), LSHWatermark(make_asset()), engine, lambda **kw: kw)
        self.assertEqual([s["generation_seed"] for s in scores], [52, 53, 54])
        self.assertEqual([p[1] for call in FakeEngine.calls for p in call], [52, 53, 54])
        self.assertEqual(FakeEngine.calls[0][0][0], prompt_ids(FakeTokenizer(), source.to_pylist()[0]["content"], 2048))


if __name__ == "__main__":
    unittest.main()
