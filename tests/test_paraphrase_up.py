"""CPU tests for Dipper UP; no torch, transformers, NLTK resources, or GPU."""

from dataclasses import replace
from contextlib import nullcontext, redirect_stderr
import io
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from baseline_acl.paraphrase_up import (
    GeneratedResponse, GenerationConfig, file_sha256, inspect_source,
    generation_seed, parse_args, prepare_response, publish_new_file, response_issues,
    run_paraphrasing, validate_output_paths, render_dipper_input, paraphrase_windows, validate_window_audit,
    preflight_source, asset_identity, dipper_weight_source,
    load_sentence_splitter, DipperGenerator, FORMAT_VERSION,
    parse_visible_gpus, select_dtype, main,
)

try:
    import pyarrow as pa
    import pyarrow.parquet as pq
except ImportError:
    pa = pq = None


class FakeTokenizer:
    def encode(self, text, add_special_tokens=False):
        return text.split() + (["EOS"] if add_special_tokens else [])


def one_sentence(text):
    return [text]


class FakeGenerator:
    def __init__(self, responses=None, crash_on_attempts=None):
        self.responses = responses or {}
        self.crash_on_attempts = crash_on_attempts or set()
        self.calls = []
        self.attempt_calls = []
        self.config = GenerationConfig()

    def generate(self, prepared_rows, indices, attempts):
        self.calls.extend(indices)
        self.attempt_calls.extend(zip(indices, attempts, strict=True))
        if any((index, attempt) in self.crash_on_attempts for index, attempt in zip(indices, attempts, strict=True)):
            raise RuntimeError("simulated interruption")
        result = []
        for row, index, attempt in zip(prepared_rows, indices, attempts, strict=True):
            candidate = self.responses.get((index, attempt), self.responses.get(index, GeneratedResponse(f"An edited response for row {index}.", "stop", 8)))
            result.append(paraphrase_windows(row, lambda prompt, seed: candidate, FakeTokenizer(), self.config, index, attempt))
        return result


class FakeStreamingGenerator:
    """Out-of-order, per-result backend with explicit lifecycle and failure hooks."""

    def __init__(self, responses=None, *, order=None, crash_after=None, malformed=None):
        self.responses = responses or {}
        self.order = order
        self.crash_after = crash_after
        self.malformed = malformed
        self.worker_count = 2
        self.config = GenerationConfig()
        self.calls = []
        self.attempt_calls = []
        self.scheduled = []
        self.closed = False
        self.before_yield = None

    def iter_generate(self, prepared_rows, indices, attempts):
        self.scheduled.append(list(indices))
        jobs = {index: (row, attempt) for row, index, attempt
                in zip(prepared_rows, indices, attempts, strict=True)}
        order = list(reversed(indices)) if self.order is None else [i for i in self.order if i in jobs]
        emitted = 0
        for index in order:
            if self.crash_after is not None and emitted >= self.crash_after:
                raise RuntimeError("simulated worker interruption")
            row, attempt = jobs[index]
            self.calls.append(index)
            self.attempt_calls.append((index, attempt))
            if self.before_yield is not None:
                self.before_yield(index, attempt)
            candidate = self.responses.get((index, attempt), self.responses.get(
                index, GeneratedResponse(f"An edited response for row {index}.", "stop", 8)))
            generated = paraphrase_windows(row, lambda prompt, seed: candidate,
                                          FakeTokenizer(), self.config, index, attempt)
            result = (index, attempt, generated)
            yield self.malformed(result, emitted) if self.malformed is not None else result
            emitted += 1

    def close(self):
        self.closed = True


class PureUnitTests(unittest.TestCase):
    def test_visible_gpu_selection_is_explicit_and_matches_requested_count(self):
        self.assertEqual(parse_visible_gpus("1,3", 2), ["1", "3"])
        self.assertEqual(parse_visible_gpus(" 2 , 5 ", 2), ["2", "5"])
        self.assertEqual(parse_visible_gpus("4"), ["4"])
        self.assertEqual(parse_visible_gpus("1,2,3"), ["1", "2", "3"])
        gpu_uuid = "GPU-aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
        mig_uuid = "MIG-ffffffff-1111-2222-3333-444444444444"
        self.assertEqual(parse_visible_gpus(f"{gpu_uuid},{mig_uuid}", 2), [gpu_uuid, mig_uuid])
        for visible, count in (("", None), (" ", None), ("-1", 1), ("1,1", 2),
                               ("1,3", 1), ("1", 2), ("1,3", 0), ("1,3", -1),
                               ("1，3", 2), ("1,,3", 2), ("1,", 1), (",1", 1),
                               ("abc", 1), ("1,other", 2)):
            with self.subTest(visible=visible, count=count), self.assertRaises(ValueError):
                parse_visible_gpus(visible, count)

    def test_dtype_auto_uses_only_common_supported_precision(self):
        supported = [{"bf16_supported": True}, {"bf16_supported": True}]
        mixed = [{"bf16_supported": True}, {"bf16_supported": False}]
        self.assertEqual(select_dtype("auto", supported), "bfloat16")
        self.assertEqual(select_dtype("auto", mixed), "float32")
        self.assertEqual(select_dtype("float32", supported), "float32")
        self.assertEqual(select_dtype("float32", mixed), "float32")
        self.assertEqual(select_dtype("bfloat16", supported), "bfloat16")
        for requested, devices in (("bfloat16", mixed), ("float16", supported), ("auto", [])):
            with self.subTest(requested=requested, devices=devices), self.assertRaises(ValueError):
                select_dtype(requested, devices)

    def test_cli_accepts_gpu_count_without_turning_cpu_modes_into_gpu_work(self):
        for mode in ("--inspect", "--preflight"):
            with self.subTest(mode=mode):
                args = parse_args(["--input", "train.parquet", mode, "--num-gpus", "2"])
                self.assertEqual(args.num_gpus, 2)
                self.assertEqual(args.dtype, "auto")
        for dtype in ("auto", "float32", "bfloat16"):
            self.assertEqual(parse_args(["--input", "train.parquet", "--inspect", "--dtype", dtype]).dtype, dtype)
        with redirect_stderr(io.StringIO()):
            for count in ("0", "-1", "two"):
                with self.subTest(count=count), self.assertRaises(SystemExit):
                    parse_args(["--input", "train.parquet", "--inspect", "--num-gpus", count])

    def test_cpu_entrypoints_do_not_validate_visible_gpus_or_probe_precision(self):
        forbidden = AssertionError("CPU modes must not inspect CUDA devices")
        with patch("baseline_acl.paraphrase_up.parse_visible_gpus", side_effect=forbidden), \
             patch("baseline_acl.paraphrase_up.select_dtype", side_effect=forbidden), \
             patch("baseline_acl.paraphrase_up.inspect_source", return_value={"rows": 3}), \
             patch("sys.stdout", new_callable=io.StringIO):
            main(["--input", "train.parquet", "--inspect", "--num-gpus", "2"])
        fake_transformers = SimpleNamespace(T5Tokenizer=SimpleNamespace(from_pretrained=lambda *args, **kwargs: FakeTokenizer()))
        with patch.dict(sys.modules, {"transformers": fake_transformers}), \
             patch("baseline_acl.paraphrase_up.parse_visible_gpus", side_effect=forbidden), \
             patch("baseline_acl.paraphrase_up.select_dtype", side_effect=forbidden), \
             patch("baseline_acl.paraphrase_up.asset_identity", return_value={}), \
             patch("baseline_acl.paraphrase_up.load_sentence_splitter", return_value=one_sentence), \
             patch("baseline_acl.paraphrase_up.preflight_source", return_value={"valid": True, "invalid_rows": []}), \
             patch("sys.stdout", new_callable=io.StringIO):
            main(["--input", "train.parquet", "--preflight", "--num-gpus", "2"])

    def test_defaults_and_answer_only_prompt(self):
        config = GenerationConfig()
        self.assertEqual(config.max_output_length, 4096)
        self.assertEqual(config.max_input_tokens, 4096)
        self.assertEqual(FORMAT_VERSION, 3)
        self.assertNotIn("window_size", GenerationConfig.__dataclass_fields__)
        self.assertEqual(config.max_attempts, 1)
        self.assertEqual(config.dtype, "float32")
        self.assertEqual(config.temperature, 1.0)
        self.assertEqual(config.top_k, 0)
        self.assertNotEqual(generation_seed(42, 5, 1), generation_seed(42, 5, 2))
        args = parse_args(["--input", "train.parquet", "--inspect"])
        self.assertTrue(args.inspect)
        self.assertIsNone(args.output)
        self.assertEqual(args.max_output_length, config.max_output_length)
        self.assertIn("dipper", args.model)
        self.assertIn("t5-v1_1-xxl", args.tokenizer)
        result = prepare_response(FakeTokenizer(), "The existing answer.", config, one_sentence)
        prompt = render_dipper_input(result["windows"][0]["text"], "", config)
        self.assertEqual(prompt, "lexical = 40, order = 100 <sent> The existing answer. </sent>")
        self.assertNotIn("watermark", prompt.lower())
        self.assertNotIn("detector", prompt.lower())
        self.assertEqual(result["issues"], [])

    def test_token_budget_never_truncates(self):
        text = "one two three four five six"
        config = replace(GenerationConfig(), max_input_tokens=5, max_output_length=3)
        result = prepare_response(FakeTokenizer(), text, config, one_sentence)
        self.assertEqual(text, result["windows"][0]["text"])
        self.assertEqual(result["source_tokens"], 6)
        self.assertEqual(result["issues"], ["full_response_exceeds_encoder_budget"])
        # Encoder and decoder budgets are independent; input>decoder cap is valid.
        independent = prepare_response(FakeTokenizer(), " ".join(["word"] * 600),
                                       replace(GenerationConfig(), max_output_length=512), one_sentence)
        self.assertEqual(independent["issues"], [])

    def test_generation_failures_are_classified(self):
        config = GenerationConfig()
        self.assertIn("empty_output", response_issues(GeneratedResponse("  ", "stop", 1), "normal", config))
        self.assertIn("length_limit", response_issues(GeneratedResponse("truncated", "length", 511), "normal", config))
        self.assertIn("refusal", response_issues(GeneratedResponse("I cannot rewrite this.", "stop", 6), "normal", config))
        self.assertIn("editorial_preface", response_issues(GeneratedResponse("Here is the rewritten response: hello", "stop", 8), "normal", config))
        # An existing refusal is legitimate text to paraphrase, not a new refusal.
        self.assertNotIn("refusal", response_issues(GeneratedResponse("I cannot help with that.", "stop", 6), "I cannot assist with that.", config))
        self.assertIn("invalid_output_token_count", response_issues(GeneratedResponse("answer", "stop", 0), "normal", config))

    def test_config_rejects_invalid_values(self):
        for config in (replace(GenerationConfig(), batch_size=0), replace(GenerationConfig(), max_output_length=1),
                       replace(GenerationConfig(), temperature=float("nan")), replace(GenerationConfig(), top_p=0),
                       replace(GenerationConfig(), on_failure="silent"), replace(GenerationConfig(), max_attempts=0),
                       replace(GenerationConfig(), lex_diversity=15), replace(GenerationConfig(), max_input_tokens=0),
                       replace(GenerationConfig(), dtype="float16"), replace(GenerationConfig(), top_k=50)):
            with self.assertRaises(ValueError):
                config.validate()

    def test_paths_refuse_heldout_and_overwrite(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source, target, checkpoint, audit = [root / name for name in ("train.parquet", "up.parquet", "up.jsonl", "up.json")]
            with self.assertRaises(ValueError):
                validate_output_paths(root / "dolly_test.parquet", target, checkpoint, audit, False)
            with self.assertRaises(ValueError):
                validate_output_paths(source, source, checkpoint, audit, False)
            target.touch()
            with self.assertRaises(FileExistsError):
                validate_output_paths(source, target, checkpoint, audit, False)

    def test_all_sentences_are_joined_and_generated_once_without_prefix(self):
        tokenizer, config = FakeTokenizer(), GenerationConfig()
        split_inputs = []
        def split(text):
            split_inputs.append(text)
            return ["One.", "Two.", "Three.", "Four."]
        prepared = prepare_response(tokenizer, "One.\n Two.  Three. Four.", config, split)
        self.assertEqual(split_inputs, ["One. Two. Three. Four."])
        self.assertEqual([window["text"] for window in prepared["windows"]], ["One. Two. Three. Four."])
        self.assertEqual(prepared["sentence_count"], 4)
        calls = []
        def generate(prompt, seed):
            calls.append((prompt, seed))
            return GeneratedResponse("full response edit", "stop", 4)
        result = paraphrase_windows(prepared, generate, tokenizer, config, 7, 1)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][0], "lexical = 40, order = 100 <sent> One. Two. Three. Four. </sent>")
        self.assertEqual(result.text, "full response edit")
        self.assertEqual(result.output_tokens, 4)  # EOS remains included; no re-tokenization.
        self.assertEqual(len(result.windows), 1)
        self.assertEqual(calls[0][1], generation_seed(42, 7, 1))
        self.assertEqual(validate_window_audit(result, prepared, tokenizer, config, 7, 1), [])
        fresh = []
        paraphrase_windows(prepared, lambda prompt, seed: (fresh.append(prompt) or GeneratedResponse("new edit", "stop", 3)),
                           tokenizer, config, 8, 1)
        self.assertEqual(len(fresh), 1)
        self.assertEqual(fresh[0], calls[0][0])
        self.assertNotIn("full response edit", fresh[0])

    def test_whole_answer_longer_than_512_uses_one_decoder_sequence(self):
        tokenizer = FakeTokenizer()
        config = GenerationConfig()
        sentences = [f"Sentence {i}." for i in range(40)]
        prepared = prepare_response(tokenizer, " ".join(sentences), config, lambda text: sentences)
        edited = " ".join(["edited"] * 700)
        calls = []
        def generate(prompt, seed):
            calls.append(prompt)
            return GeneratedResponse(edited, "stop", 701)
        result = paraphrase_windows(prepared, generate, tokenizer, config, 0, 1)
        self.assertEqual(result.output_tokens, 701)
        self.assertEqual(result.text, edited)
        self.assertEqual(len(result.windows), 1)
        self.assertEqual(len(calls), 1)
        self.assertIn("Sentence 0.", calls[0])
        self.assertIn("Sentence 39.", calls[0])
        self.assertEqual(prepared["sentence_count"], 40)
        self.assertEqual(response_issues(result, "source", config), [])
        self.assertEqual(validate_window_audit(result, prepared, tokenizer, config, 0, 1), [])

    def test_whole_response_encoder_budget_refuses_generation_without_chunking(self):
        tokenizer = FakeTokenizer()
        config = replace(GenerationConfig(), max_input_tokens=10)
        prepared = prepare_response(tokenizer, "First. Second.", config, lambda text: ["First.", "Second."])
        self.assertEqual(prepared["issues"], ["full_response_exceeds_encoder_budget"])
        self.assertEqual(prepared["windows"][0]["text"], "First. Second.")
        calls = []
        def generate(prompt, seed):
            calls.append(prompt)
            return GeneratedResponse(" ".join(["expanded"] * 20), "stop", 21)
        result = paraphrase_windows(prepared, generate, tokenizer, config, 0, 1)
        self.assertEqual(calls, [])
        self.assertEqual(result.finish_reason, "input_limit")
        self.assertIn("full_response_exceeds_encoder_budget", result.issues)
        self.assertEqual(len(result.windows), 1)
        self.assertGreater(result.windows[0]["input_tokens"], 10)
        self.assertEqual(result.windows[0]["output_tokens"], 0)

    def test_chunked_prepared_input_is_refused_not_silently_regenerated(self):
        tokenizer, config = FakeTokenizer(), GenerationConfig()
        prepared = prepare_response(tokenizer, "First. Second.", config, one_sentence)
        chunked = {**prepared, "windows": [prepared["windows"][0], prepared["windows"][0]]}
        with self.assertRaisesRegex(ValueError, "chunked inputs are refused"):
            paraphrase_windows(chunked, lambda prompt, seed: self.fail("generation must not run"),
                               tokenizer, config, 0, 1)

    def test_whole_response_decoder_budget_rejects_oversized_natural_eos_output(self):
        tokenizer, config = FakeTokenizer(), replace(GenerationConfig(), max_output_length=5)
        prepared = prepare_response(tokenizer, "First. Second.", config, one_sentence)
        result = paraphrase_windows(prepared, lambda prompt, seed: GeneratedResponse("an overly long response", "stop", 5),
                                    tokenizer, config, 0, 1)
        self.assertIn("full_response_output_exceeds_decoder_budget", result.issues)
        self.assertIn("full_response_decoder_limit", validate_window_audit(result, prepared, tokenizer, config, 0, 1))
        self.assertEqual(result.windows[0]["decoder_length"], 6)
        valid = paraphrase_windows(prepared, lambda prompt, seed: GeneratedResponse("an exact fit", "stop", 4),
                                   tokenizer, config, 0, 1)
        self.assertEqual(validate_window_audit(valid, prepared, tokenizer, config, 0, 1), [])

    def test_whole_response_audit_detects_tampering_and_reconstruction_mismatch(self):
        tokenizer, config = FakeTokenizer(), GenerationConfig()
        prepared = prepare_response(tokenizer, "First. Second.", config, one_sentence)
        result = paraphrase_windows(prepared, lambda prompt, seed: GeneratedResponse("full rewrite", "stop", 3),
                                    tokenizer, config, 0, 1)
        self.assertEqual(validate_window_audit(result, prepared, tokenizer, config, 0, 1), [])
        for field, value in (("window_index", 1), ("source_sha256", "wrong"), ("prefix_sha256", "rolling-prefix"),
                             ("seed", 999), ("input_tokens", 999), ("source_tokens", 999)):
            with self.subTest(field=field):
                record = {**result.windows[0], field: value}
                tampered = replace(result, windows=[record])
                self.assertIn("full_response_audit_mismatch",
                              validate_window_audit(tampered, prepared, tokenizer, config, 0, 1))
        for tampered in (replace(result, text="different answer"), replace(result, output_tokens=2),
                         replace(result, finish_reason="length")):
            self.assertIn("full_response_output_reconstruction_mismatch",
                          validate_window_audit(tampered, prepared, tokenizer, config, 0, 1))
        for windows in ([], [result.windows[0], result.windows[0]]):
            self.assertEqual(validate_window_audit(replace(result, windows=windows), prepared, tokenizer, config, 0, 1),
                             ["whole_response_single_input_required"])

    def test_malformed_output_token_counts_are_rejected_without_type_errors(self):
        tokenizer, config = FakeTokenizer(), GenerationConfig()
        prepared = prepare_response(tokenizer, "normal source", config, one_sentence)
        for count in (None, "bad", True):
            with self.subTest(count=count):
                candidate = GeneratedResponse("rewritten answer", "stop", count)
                self.assertIn("invalid_output_token_count", response_issues(candidate, "normal source", config))
                result = paraphrase_windows(prepared, lambda prompt, seed: candidate, tokenizer, config, 0, 1)
                self.assertIn("invalid_output_token_count", result.issues)
                self.assertIsNone(result.windows[0]["decoder_length"])
                self.assertIn("full_response_decoder_limit", validate_window_audit(result, prepared, tokenizer, config, 0, 1))

    def test_missing_punkt_is_an_explicit_error(self):
        def missing(*args, **kwargs):
            raise LookupError("missing punkt")
        fake = SimpleNamespace(data=SimpleNamespace(path=[]), sent_tokenize=missing)
        with tempfile.TemporaryDirectory() as temporary, patch.dict(sys.modules, {"nltk": fake}):
            with self.assertRaisesRegex(RuntimeError, "No alternate sentence splitter"):
                load_sentence_splitter(Path(temporary))

    def test_model_asset_guard_rejects_non_t5_and_missing_weights(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "config.json").write_text(json.dumps({"model_type": "qwen2"}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "model_type=t5"):
                asset_identity(str(root), weights_required=True)
            (root / "config.json").write_text(json.dumps({"model_type": "t5"}), encoding="utf-8")
            with self.assertRaisesRegex(FileNotFoundError, "weights are missing"):
                asset_identity(str(root), weights_required=True)

    def test_safetensors_download_accepts_unused_legacy_bin_index(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "config.json").write_text(json.dumps({"model_type": "t5"}), encoding="utf-8")
            safe_index = root / "model.safetensors.index.json"
            safe_index.write_text(json.dumps({"weight_map": {"layer": "model-00001-of-00001.safetensors"}}), encoding="utf-8")
            (root / "model-00001-of-00001.safetensors").write_bytes(b"fake-safe-weights")
            (root / "pytorch_model.bin.index.json").write_text(
                json.dumps({"weight_map": {"layer": "missing-pytorch-model.bin"}}), encoding="utf-8")
            self.assertEqual(dipper_weight_source(root), (True, safe_index))
            identity = asset_identity(str(root), weights_required=True)
            self.assertIn("model-00001-of-00001.safetensors", [item["name"] for item in identity["files"]])

    def test_missing_selected_safe_shard_is_rejected_without_bin_fallback(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "config.json").write_text(json.dumps({"model_type": "t5"}), encoding="utf-8")
            (root / "model.safetensors.index.json").write_text(
                json.dumps({"weight_map": {"layer": "missing-model.safetensors"}}), encoding="utf-8")
            (root / "pytorch_model.bin").write_bytes(b"complete-legacy-file")
            with self.assertRaisesRegex(FileNotFoundError, "missing-model.safetensors"):
                asset_identity(str(root), weights_required=True)

    def test_weight_source_single_file_priority_and_bin_only_support(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "model.safetensors").write_bytes(b"fake-safe-weights")
            (root / "model.safetensors.index.json").write_text("invalid unused JSON", encoding="utf-8")
            self.assertEqual(dipper_weight_source(root), (True, root / "model.safetensors"))
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "pytorch_model.bin").write_bytes(b"fake-bin-weights")
            (root / "pytorch_model.bin.index.json").write_text("invalid unused JSON", encoding="utf-8")
            self.assertEqual(dipper_weight_source(root), (False, root / "pytorch_model.bin"))
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            index = root / "pytorch_model.bin.index.json"
            index.write_text(json.dumps({"weight_map": {"layer": "pytorch_model-00001-of-00001.bin"}}), encoding="utf-8")
            (root / "pytorch_model-00001-of-00001.bin").write_bytes(b"fake-bin-shard")
            self.assertEqual(dipper_weight_source(root), (False, index))
            (root / "pytorch_model-00001-of-00001.bin").unlink()
            with self.assertRaisesRegex(FileNotFoundError, "pytorch_model-00001-of-00001.bin"):
                dipper_weight_source(root)

    def test_selected_weight_index_requires_nonempty_valid_shard_map(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for index in ([], {}, {"weight_map": {}}, {"weight_map": []},
                          {"weight_map": {"layer": None}}, {"weight_map": {"layer": []}}):
                with self.subTest(index=index):
                    (root / "model.safetensors.index.json").write_text(json.dumps(index), encoding="utf-8")
                    with self.assertRaises(ValueError):
                        dipper_weight_source(root)

    def test_dipper_loader_uses_the_validated_weight_format(self):
        fake_torch = SimpleNamespace(
            cuda=SimpleNamespace(is_available=lambda: True, device_count=lambda: 1),
            float32="fp32")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for filename, expected_safe in (("model.safetensors", True), ("pytorch_model.bin", False)):
                with self.subTest(filename=filename):
                    (root / filename).write_bytes(b"fake-weights")
                    model = SimpleNamespace(to=lambda device: SimpleNamespace(eval=lambda: "loaded-model"))
                    from unittest.mock import Mock
                    loader = Mock(return_value=model)
                    fake_transformers = SimpleNamespace(T5ForConditionalGeneration=SimpleNamespace(from_pretrained=loader))
                    with patch.dict(sys.modules, {"torch": fake_torch, "transformers": fake_transformers}):
                        generator = DipperGenerator(str(root), GenerationConfig(), FakeTokenizer())
                    self.assertEqual(generator.model, "loaded-model")
                    self.assertIs(loader.call_args.kwargs["use_safetensors"], expected_safe)
                    self.assertTrue(loader.call_args.kwargs["local_files_only"])
                    (root / filename).unlink()

    def test_authoritative_punkt_directory_and_resource_fingerprints(self):
        fake = SimpleNamespace(data=SimpleNamespace(path=["unrelated global cache"]),
                               sent_tokenize=lambda text, language: [text])
        with tempfile.TemporaryDirectory() as temporary, patch.dict(sys.modules, {"nltk": fake}):
            root = Path(temporary)
            english = root / "tokenizers" / "punkt_tab" / "english"
            english.mkdir(parents=True)
            names = ("abbrev_types.txt", "collocations.tab", "ortho_context.tab", "sent_starters.txt")
            for name in names:
                (english / name).write_text(name, encoding="utf-8")
            splitter = load_sentence_splitter(root)
            self.assertEqual(fake.data.path, [str(root.resolve())])
            self.assertEqual(splitter.resource_identity["directory"], str(root.resolve()))
            self.assertEqual(splitter.resource_identity["english_punkt_tab"],
                             [{"name": name, "sha256": file_sha256(english / name)} for name in names])
            self.assertIn("nltk_version", splitter.resource_identity)

    def test_asset_preparation_timestamps_do_not_invalidate_resume_identity(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "config.json").write_text(json.dumps({"model_type": "t5"}), encoding="utf-8")
            manifest = {"repo_id": "google/t5-v1_1-xxl", "revision": "fixed", "prepared_at": "yesterday"}
            path = root / "prepare_manifest.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            before = asset_identity(str(root))
            path.write_text(json.dumps({**manifest, "prepared_at": "today", "downloaded_at": "now"}), encoding="utf-8")
            self.assertEqual(before, asset_identity(str(root)))
            self.assertEqual(before["provenance"], {"repo_id": "google/t5-v1_1-xxl", "revision": "fixed"})

    def test_cli_preflight_and_obsolete_backend_flags(self):
        args = parse_args(["--input", "train.parquet", "--preflight"])
        self.assertTrue(args.preflight)
        self.assertIsNone(args.output)
        self.assertEqual(args.top_k, 0)
        self.assertEqual(args.temperature, 1.0)
        with redirect_stderr(io.StringIO()):
            for flag, value in (("--engine", "vllm"), ("--window-size", "3")):
                with self.subTest(flag=flag), self.assertRaises(SystemExit):
                    parse_args(["--input", "train.parquet", "--inspect", flag, value])

    def test_t5_decoder_only_output_and_total_length_semantics(self):
        class InputIDs:
            shape = (1, 30)
        class Inputs(dict):
            def to(self, device):
                return self
        class Sequence:
            def __init__(self, values):
                self.values = values
            def tolist(self):
                return self.values
        class Tokenizer(FakeTokenizer):
            def __call__(self, prompts, **kwargs):
                self.kwargs = kwargs
                return Inputs(input_ids=InputIDs())
            def batch_decode(self, outputs, skip_special_tokens):
                return ["rewritten sentence"]
        calls = []
        tokens = [0, 10, 11, 1]
        def generate(**kwargs):
            calls.append(kwargs)
            return [Sequence(list(tokens))]
        engine = DipperGenerator.__new__(DipperGenerator)
        engine.config, engine.tokenizer = GenerationConfig(), Tokenizer()
        engine.torch = SimpleNamespace(manual_seed=lambda seed: None, inference_mode=nullcontext)
        engine.model = SimpleNamespace(generate=generate, generation_config=SimpleNamespace(eos_token_id=1, forced_eos_token_id=None))
        result = engine.generate_window("a much longer encoder source prompt", 42)
        self.assertEqual(result.text, "rewritten sentence")
        self.assertEqual(result.output_tokens, 3)  # start excluded, EOS included
        self.assertEqual(result.finish_reason, "stop")
        self.assertEqual(calls[0]["max_length"], 4096)
        self.assertNotIn("max_new_tokens", calls[0])
        self.assertEqual(calls[0]["top_k"], 0)
        self.assertTrue(calls[0]["do_sample"])
        self.assertFalse(engine.tokenizer.kwargs["truncation"])
        tokens[:] = [0] + [10] * 4095
        self.assertEqual(engine.generate_window("source", 43).finish_reason, "length")
        # An imposed EOS at the hard limit is not mistaken for natural completion.
        tokens[-1] = 1
        engine.model.generation_config.forced_eos_token_id = 1
        self.assertEqual(engine.generate_window("source", 44).finish_reason, "length")


@unittest.skipIf(pa is None, "pyarrow is needed for parquet integration tests")
class ParquetTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.source = self.root / "kgw_train.parquet"
        self.output = self.root / "up_train.parquet"
        self.checkpoint = self.output.with_suffix(".parquet.progress.jsonl")
        self.audit = self.output.with_suffix(".parquet.audit.json")
        self.tokenizer, self.config = FakeTokenizer(), GenerationConfig(batch_size=1, max_attempts=3)
        self.identity = {"model": "fake", "revision": "fixed"}
        content_type = pa.list_(pa.field("element", pa.struct([pa.field("content", pa.string()), pa.field("role", pa.string())])))
        self.schema = pa.schema([
            pa.field("id", pa.string()), pa.field("content", content_type),
            pa.field("teacher_response", pa.string(), metadata={b"field_contract": b"preserve"}),
            pa.field("category", pa.string()), pa.field("grounded", pa.bool_()),
            pa.field("flaw", pa.string()), pa.field("agreement", pa.bool_()),
        ], metadata={b"huggingface": b'{"info":{"features":{}}}', b"source_contract": b"keep me"})
        self.rows = [
            {"id": f"source-{index}", "content": [{"role": "user", "content": f"UNCHANGED question {index}"}],
             "teacher_response": f"Original answer number {index}.", "category": "open_qa", "grounded": bool(index % 2),
             "flaw": "normal", "agreement": None if index == 0 else True}
            for index in range(3)
        ]
        self.table = pa.Table.from_pylist(self.rows, schema=self.schema)
        pq.write_table(self.table, self.source)

    def tearDown(self):
        self.temporary.cleanup()

    def run_job(self, generator, **kwargs):
        config = kwargs.pop("config", self.config)
        generator.config = config
        return run_paraphrasing(self.source, self.output, config, self.tokenizer,
                               lambda: generator, self.identity, sentence_splitter=one_sentence, **kwargs)

    def fail_after_first(self):
        bad = FakeGenerator({(1, 1): GeneratedResponse("unfinished text", "length", 511)}, crash_on_attempts={(1, 2)})
        with self.assertRaisesRegex(RuntimeError, "simulated interruption"):
            self.run_job(bad)
        self.assertEqual(bad.calls, [0, 1, 1])
        self.assertFalse(self.output.exists())
        self.assertFalse(self.audit.exists())

    def checkpoint_records(self):
        return [json.loads(line) for line in self.checkpoint.read_text(encoding="utf-8").splitlines()[1:]]

    def test_streaming_out_of_order_keeps_ids_output_order_and_parallel_default_group(self):
        generator = FakeStreamingGenerator(order=[2, 0, 1])
        report = self.run_job(generator)
        self.assertEqual(generator.scheduled, [[0, 1, 2]])
        self.assertEqual(generator.calls, [2, 0, 1])
        self.assertTrue(generator.closed)
        self.assertEqual([record["row_index"] for record in self.checkpoint_records()], [2, 0, 1])
        self.assertEqual([record["id"] for record in self.checkpoint_records()], ["source-2", "source-0", "source-1"])
        output = pq.read_table(self.output)
        self.assertEqual(output["id"].to_pylist(), [row["id"] for row in self.rows])
        self.assertEqual(output["teacher_response"].to_pylist(), [f"An edited response for row {i}." for i in range(3)])
        self.assertEqual(report["status_counts"], {"ok": 3})

    def test_streaming_results_are_durable_before_next_backend_yield(self):
        generator = FakeStreamingGenerator(order=[2, 0, 1])
        counts = []
        def observe(index, attempt):
            counts.append(len(self.checkpoint_records()))
        generator.before_yield = observe
        self.run_job(generator)
        self.assertEqual(counts, [0, 1, 2])
        self.assertTrue(generator.closed)

    def test_streaming_retries_only_invalid_outputs(self):
        generator = FakeStreamingGenerator({(1, 1): GeneratedResponse("unfinished", "length", 6)}, order=[2, 1, 0])
        report = self.run_job(generator)
        self.assertEqual(generator.scheduled, [[0, 1, 2], [1]])
        self.assertEqual(generator.attempt_calls, [(2, 1), (1, 1), (0, 1), (1, 2)])
        self.assertEqual(report["rejected_generation_attempts"], 1)
        self.assertEqual(report["accepted_attempts"], {"1": 2, "2": 1})
        self.assertTrue(generator.closed)

    def test_streaming_worker_failure_retains_finished_rows_and_resume_skips_them(self):
        failed = FakeStreamingGenerator(order=[2, 0, 1], crash_after=1)
        with self.assertRaisesRegex(RuntimeError, "worker interruption"):
            self.run_job(failed)
        self.assertTrue(failed.closed)
        self.assertEqual([record["row_index"] for record in self.checkpoint_records()], [2])
        self.assertFalse(self.output.exists())
        self.assertFalse(self.audit.exists())
        resumed = FakeStreamingGenerator(order=[1, 0])
        self.run_job(resumed, resume=True)
        self.assertEqual(resumed.scheduled, [[0, 1]])
        self.assertEqual(resumed.attempt_calls, [(1, 1), (0, 1)])
        self.assertTrue(resumed.closed)
        self.assertEqual(pq.read_table(self.output)["teacher_response"].to_pylist(),
                         [f"An edited response for row {i}." for i in range(3)])

    def test_streaming_rejects_duplicate_indices_before_accepting_unmatched_rows(self):
        generator = FakeStreamingGenerator(order=[0, 1, 2],
                                           malformed=lambda result, number: (0, result[1], result[2]) if number == 1 else result)
        with self.assertRaisesRegex(RuntimeError, "duplicate"):
            self.run_job(generator)
        self.assertTrue(generator.closed)
        self.assertEqual([record["row_index"] for record in self.checkpoint_records()], [0])
        self.assertFalse(self.output.exists())
        self.assertFalse(self.audit.exists())

    def test_streaming_rejects_missing_indices_and_preserves_completed_progress(self):
        generator = FakeStreamingGenerator(order=[2, 0])
        with self.assertRaisesRegex(RuntimeError, "missing|different number"):
            self.run_job(generator)
        self.assertTrue(generator.closed)
        self.assertEqual([record["row_index"] for record in self.checkpoint_records()], [2, 0])
        self.assertFalse(self.output.exists())
        self.assertFalse(self.audit.exists())

    def test_streaming_rejects_unexpected_indices_and_attempts(self):
        for name, malformed in (("index", lambda result, number: (99, result[1], result[2])),
                                ("attempt", lambda result, number: (result[0], result[1] + 1, result[2]))):
            with self.subTest(name=name):
                self.checkpoint.unlink(missing_ok=True)
                generator = FakeStreamingGenerator(malformed=malformed)
                with self.assertRaisesRegex(RuntimeError, "unexpected|invalid|attempt"):
                    self.run_job(generator)
                self.assertTrue(generator.closed)
                self.assertEqual(self.checkpoint_records(), [])
                self.assertFalse(self.output.exists())
                self.assertFalse(self.audit.exists())

    def test_streaming_rejects_malformed_payload_without_poisoning_checkpoint(self):
        malformed_values = (
            lambda result, number: result[:2],
            lambda result, number: (str(result[0]), result[1], result[2]),
            lambda result, number: (True, result[1], result[2]),
            lambda result, number: (result[0], str(result[1]), result[2]),
            lambda result, number: (result[0], True, result[2]),
        )
        for number, malformed in enumerate(malformed_values):
            with self.subTest(number=number):
                self.checkpoint.unlink(missing_ok=True)
                generator = FakeStreamingGenerator(malformed=malformed)
                with self.assertRaisesRegex(RuntimeError, "malformed|invalid|unexpected|attempt"):
                    self.run_job(generator)
                self.assertTrue(generator.closed)
                self.assertEqual(self.checkpoint_records(), [])
                self.assertFalse(self.output.exists())
                self.assertFalse(self.audit.exists())

    def test_streaming_closes_when_durable_record_write_fails(self):
        generator = FakeStreamingGenerator()
        from baseline_acl.paraphrase_up import append_record
        def fail_result(handle, record):
            if record.get("kind") == "result":
                raise OSError("simulated durable write failure")
            append_record(handle, record)
        with patch("baseline_acl.paraphrase_up.append_record", side_effect=fail_result):
            with self.assertRaisesRegex(OSError, "durable write failure"):
                self.run_job(generator)
        self.assertTrue(generator.closed)
        self.assertFalse(self.output.exists())
        self.assertFalse(self.audit.exists())

    def test_streaming_exhausted_outputs_close_backend_without_publication(self):
        generator = FakeStreamingGenerator({0: GeneratedResponse("I cannot rewrite this.", "stop", 6)})
        with self.assertRaisesRegex(RuntimeError, "exhausted 1 attempts"):
            self.run_job(generator, config=replace(self.config, max_attempts=1))
        self.assertTrue(generator.closed)
        self.assertFalse(self.output.exists())
        self.assertFalse(self.audit.exists())

    def test_streaming_keyboard_interrupt_closes_backend_and_preserves_progress(self):
        generator = FakeStreamingGenerator(order=[2, 0, 1])
        def interrupt_after_first(index, attempt):
            if index == 0:
                raise KeyboardInterrupt("simulated Ctrl+C")
        generator.before_yield = interrupt_after_first
        with self.assertRaises(KeyboardInterrupt):
            self.run_job(generator)
        self.assertTrue(generator.closed)
        self.assertEqual([record["row_index"] for record in self.checkpoint_records()], [2])
        self.assertFalse(self.output.exists())
        self.assertFalse(self.audit.exists())

    def test_full_parquet_contract_and_audit(self):
        before_hash = file_sha256(self.source)
        generator = FakeGenerator()
        report = self.run_job(generator)
        output = pq.read_table(self.output)
        self.assertEqual(generator.calls, [0, 1, 2])
        self.assertEqual(file_sha256(self.source), before_hash)
        self.assertTrue(output.schema.equals(self.schema, check_metadata=True))
        for name in self.schema.names:
            if name != "teacher_response":
                self.assertTrue(output[name].equals(self.table[name]), name)
        self.assertEqual(output["teacher_response"].to_pylist(), [f"An edited response for row {i}." for i in range(3)])
        self.assertEqual(report["rows"], 3)
        self.assertEqual(report["status_counts"], {"ok": 3})
        self.assertEqual(report["output_sha256"], file_sha256(self.output))
        self.assertEqual(report["format_version"], 3)
        self.assertEqual(report["paraphrase_mode"], "whole_response")
        self.assertEqual(report["response_input_checks"], 3)
        self.assertEqual(report["generated_response_attempts"], 3)
        contract = report["metadata"]["generation_contract"]
        self.assertEqual(contract["inputs_per_response"], 1)
        self.assertFalse(contract["rolling_prefix"])
        self.assertEqual(contract["initial_prefix"], "")
        self.assertEqual(json.loads(self.audit.read_text(encoding="utf-8")), report)
        self.assertEqual(len(self.checkpoint.read_text(encoding="utf-8").splitlines()), 4)

    def test_resume_keeps_successes_and_retries_only_failure(self):
        self.fail_after_first()
        generator = FakeGenerator()
        report = self.run_job(generator, resume=True)
        self.assertEqual(generator.calls, [1, 2])
        self.assertEqual(generator.attempt_calls, [(1, 2), (2, 1)])
        self.assertEqual(report["status_counts"], {"ok": 3})
        self.assertEqual(report["rejected_generation_attempts"], 1)
        self.assertEqual(report["rejected_attempt_reasons"]["length_limit"], 1)

    def test_drop_after_three_attempts_omits_entire_row_and_continues(self):
        generator = FakeGenerator({1: GeneratedResponse("", "stop", 2)})
        report = self.run_job(generator, config=replace(self.config, on_failure="drop"))
        self.assertEqual(generator.attempt_calls, [(0, 1), (1, 1), (1, 2), (1, 3), (2, 1)])
        output = pq.read_table(self.output)
        self.assertEqual(output["id"].to_pylist(), ["source-0", "source-2"])
        self.assertEqual(output["teacher_response"].to_pylist(),
                         ["An edited response for row 0.", "An edited response for row 2."])
        retained = self.table.take(pa.array([0, 2], type=pa.int64()))
        self.assertTrue(output.schema.equals(self.schema, check_metadata=True))
        for name in self.schema.names:
            if name != "teacher_response":
                self.assertTrue(output[name].equals(retained[name]), name)
        self.assertEqual(report["rows"], 2)
        self.assertEqual(report["source_rows"], 3)
        self.assertEqual(report["processed_rows"], 3)
        self.assertEqual(report["status_counts"], {"ok": 2, "dropped": 1})
        self.assertEqual(report["dropped_rows"], [1])
        self.assertEqual(report["dropped_ids"], ["source-1"])
        self.assertEqual(report["dropped_records"][0]["attempt"], 3)
        self.assertIn("empty_output", report["dropped_records"][0]["issues"])
        self.assertEqual(report["rejected_generation_attempts"], 3)
        self.assertEqual(report["changed_teacher_responses"], 2)
        self.assertEqual(file_sha256(self.source), report["metadata"]["input"]["sha256"])
        # The real training gate must accept the generated subset and sidecar.
        from baseline_acl.validate_up_data import main as validate_training
        validation_path = self.root / "kgw_test.parquet"
        validation = self.table.slice(0, 1).set_column(0, self.schema.field(0), pa.array(["held-out-id"]))
        pq.write_table(validation, validation_path)
        with patch("sys.argv", ["validate_up_data", "--original_train_file", str(self.source),
                                "--up_train_file", str(self.output), "--val_file", str(validation_path)]):
            self.assertEqual(validate_training(), 0)

    def test_streaming_drop_preserves_other_worker_results(self):
        generator = FakeStreamingGenerator({0: GeneratedResponse("", "stop", 2)})
        report = self.run_job(generator, config=replace(self.config, on_failure="drop"))
        self.assertTrue(generator.closed)
        self.assertEqual(generator.scheduled, [[0, 1, 2], [0], [0]])
        self.assertEqual(report["dropped_rows"], [0])
        self.assertEqual(pq.read_table(self.output)["id"].to_pylist(), ["source-1", "source-2"])

    def test_resume_can_drop_an_already_exhausted_row_without_a_fourth_attempt(self):
        with self.assertRaisesRegex(RuntimeError, "exhausted 3 attempts"):
            self.run_job(FakeGenerator({0: GeneratedResponse("", "stop", 2)}))
        original_bytes = self.checkpoint.read_bytes()
        resumed = FakeGenerator()
        report = self.run_job(resumed, resume=True, config=replace(self.config, on_failure="drop"))
        self.assertEqual(resumed.attempt_calls, [(1, 1), (2, 1)])
        self.assertTrue(self.checkpoint.read_bytes().startswith(original_bytes))
        self.assertEqual(report["dropped_rows"], [0])
        self.assertEqual(report["dropped_records"][0]["attempt"], 3)
        self.assertEqual(self.checkpoint_records()[3]["kind"], "resume_policy")

    def test_resume_from_old_one_attempt_checkpoint_can_retry_then_drop(self):
        with self.assertRaisesRegex(RuntimeError, "exhausted 1 attempts"):
            self.run_job(FakeStreamingGenerator({1: GeneratedResponse("", "stop", 2)}, order=[2, 0, 1]),
                         config=replace(self.config, max_attempts=1))
        original_bytes = self.checkpoint.read_bytes()
        resumed = FakeStreamingGenerator({1: GeneratedResponse("", "stop", 2)})
        report = self.run_job(resumed, resume=True, config=replace(self.config, on_failure="drop"))
        self.assertEqual(resumed.attempt_calls, [(1, 2), (1, 3)])
        self.assertTrue(self.checkpoint.read_bytes().startswith(original_bytes))
        self.assertEqual(report["status_counts"], {"ok": 2, "dropped": 1})

    def test_interrupted_drop_record_is_recovered_and_cannot_be_forged(self):
        from baseline_acl.paraphrase_up import append_record
        def fail_drop(handle, record):
            if record["kind"] == "drop":
                raise OSError("simulated drop write interruption")
            append_record(handle, record)
        config = replace(self.config, on_failure="drop")
        with patch("baseline_acl.paraphrase_up.append_record", side_effect=fail_drop):
            with self.assertRaisesRegex(OSError, "drop write interruption"):
                self.run_job(FakeGenerator({0: GeneratedResponse("", "stop", 2)}), config=config)
        resumed = FakeGenerator(crash_on_attempts={(1, 1)})
        with self.assertRaisesRegex(RuntimeError, "simulated interruption"):
            self.run_job(resumed, resume=True, config=config)
        self.assertEqual(resumed.attempt_calls, [(1, 1)])
        saved = self.checkpoint.read_text(encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "after rows have been dropped"):
            self.run_job(FakeGenerator(), resume=True, config=replace(config, max_attempts=5))
        self.assertEqual(self.checkpoint.read_text(encoding="utf-8"), saved)
        lines = saved.splitlines()
        record = json.loads(lines[-1])
        self.assertEqual(record["kind"], "drop")
        record["issues"] = ["forged reason"]
        lines[-1] = json.dumps(record)
        self.checkpoint.write_text("\n".join(lines) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "invalid dropped checkpoint"):
            self.run_job(FakeGenerator(), resume=True, config=config)
        self.checkpoint.write_text(saved, encoding="utf-8")
        finished = FakeGenerator()
        self.run_job(finished, resume=True, config=config)
        self.assertEqual(finished.attempt_calls, [(1, 1), (2, 1)])

    def test_all_dropped_rows_never_publish_empty_training_data(self):
        generator = FakeStreamingGenerator({i: GeneratedResponse("", "stop", 2) for i in range(3)})
        with self.assertRaisesRegex(RuntimeError, "empty training dataset"):
            self.run_job(generator, config=replace(self.config, on_failure="drop"))
        self.assertTrue(generator.closed)
        self.assertFalse(self.output.exists())
        self.assertFalse(self.audit.exists())

    def test_drop_mode_does_not_drop_over_budget_sources_without_generation(self):
        generator = FakeGenerator()
        with self.assertRaisesRegex(ValueError, "No source text is truncated"):
            self.run_job(generator, config=replace(self.config, on_failure="drop", max_input_tokens=2))
        self.assertEqual(generator.calls, [])
        self.assertFalse(self.checkpoint.exists())

    def test_drop_audit_recovers_interrupted_final_publication(self):
        def fail_publication(temporary, destination):
            if destination == self.output:
                raise OSError("simulated publication interruption")
            publish_new_file(temporary, destination)
        config = replace(self.config, on_failure="drop")
        with patch("baseline_acl.paraphrase_up.publish_new_file", side_effect=fail_publication):
            with self.assertRaisesRegex(OSError, "publication interruption"):
                self.run_job(FakeGenerator({0: GeneratedResponse("", "stop", 2)}), config=config)
        before = self.audit.read_bytes()
        resumed = FakeGenerator()
        self.run_job(resumed, resume=True, config=config)
        self.assertEqual(resumed.calls, [])
        self.assertEqual(self.audit.read_bytes(), before)
        self.assertEqual(pq.read_table(self.output).num_rows, 2)

    def test_resume_increases_exhausted_retry_limit_without_rewriting_successes(self):
        original_config = replace(self.config, max_attempts=1)
        failed = FakeStreamingGenerator({1: GeneratedResponse("", "stop", 2)}, order=[2, 0, 1])
        with self.assertRaisesRegex(RuntimeError, "exhausted 1 attempts"):
            self.run_job(failed, config=original_config)
        original_bytes = self.checkpoint.read_bytes()
        successes = [record for record in self.checkpoint_records() if record["kind"] == "result"]
        self.assertEqual([record["row_index"] for record in successes], [2, 0])

        # A second interruption after the policy change must retain that change.
        interrupted = FakeGenerator(crash_on_attempts={(1, 2)})
        with self.assertRaisesRegex(RuntimeError, "simulated interruption"):
            self.run_job(interrupted, resume=True)
        self.assertTrue(self.checkpoint.read_bytes().startswith(original_bytes))
        update = self.checkpoint_records()[-1]
        self.assertEqual(update["kind"], "retry_limit")
        self.assertEqual(update["metadata"]["config"]["max_attempts"], 3)
        before = self.checkpoint.read_bytes()
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            self.run_job(FakeGenerator(), resume=True, config=replace(self.config, max_attempts=2))
        self.assertEqual(self.checkpoint.read_bytes(), before)

        resumed = FakeStreamingGenerator()
        report = self.run_job(resumed, resume=True)
        self.assertEqual(resumed.attempt_calls, [(1, 2)])
        self.assertEqual([record for record in self.checkpoint_records()
                          if record["kind"] == "result" and record["row_index"] != 1], successes)
        self.assertEqual(report["status_counts"], {"ok": 3})
        self.assertEqual(report["rejected_generation_attempts"], 1)
        self.assertEqual(report["metadata"]["config"]["max_attempts"], 3)
        attempts = [record for record in self.checkpoint_records() if record.get("row_index") == 1]
        self.assertEqual([record["attempt"] for record in attempts], [1, 2])
        self.assertNotEqual(attempts[0]["seed"], attempts[1]["seed"])
        self.assertTrue(pq.read_table(self.output).schema.equals(self.schema, check_metadata=True))
        self.assertEqual(pq.read_table(self.output)["teacher_response"].to_pylist(),
                         [f"An edited response for row {i}." for i in range(3)])

    def test_resume_can_increase_retry_limit_again_after_another_exhaustion(self):
        always_empty = {0: GeneratedResponse("", "stop", 2)}
        with self.assertRaisesRegex(RuntimeError, "exhausted 1 attempts"):
            self.run_job(FakeGenerator(always_empty), config=replace(self.config, max_attempts=1))
        with self.assertRaisesRegex(RuntimeError, "exhausted 3 attempts"):
            self.run_job(FakeGenerator(always_empty), resume=True)
        original_bytes = self.checkpoint.read_bytes()
        resumed = FakeGenerator()
        report = self.run_job(resumed, resume=True, config=replace(self.config, max_attempts=5))
        self.assertEqual(resumed.attempt_calls, [(0, 4), (1, 1), (2, 1)])
        self.assertTrue(self.checkpoint.read_bytes().startswith(original_bytes))
        updates = [record for record in self.checkpoint_records() if record["kind"] == "retry_limit"]
        self.assertEqual([record["metadata"]["config"]["max_attempts"] for record in updates], [3, 5])
        self.assertEqual(updates[1]["previous_fingerprint"], updates[0]["metadata"]["fingerprint"])
        self.assertEqual(report["rejected_generation_attempts"], 3)
        self.assertEqual(report["status_counts"], {"ok": 3})

    def test_retry_increase_still_rejects_generation_model_and_input_drift(self):
        with self.assertRaisesRegex(RuntimeError, "exhausted 1 attempts"):
            self.run_job(FakeGenerator({0: GeneratedResponse("", "stop", 2)}),
                         config=replace(self.config, max_attempts=1))
        before = self.checkpoint.read_bytes()
        for changed in (replace(self.config, temperature=0.7), replace(self.config, seed=43),
                        replace(self.config, dtype="bfloat16"), replace(self.config, on_failure="keep-original")):
            with self.subTest(config=changed):
                generator = FakeGenerator()
                with self.assertRaisesRegex(ValueError, "fingerprint"):
                    self.run_job(generator, resume=True, config=changed)
                self.assertEqual(generator.calls, [])
                self.assertEqual(self.checkpoint.read_bytes(), before)
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            run_paraphrasing(self.source, self.output, self.config, self.tokenizer, lambda: FakeGenerator(),
                             {**self.identity, "revision": "changed"}, resume=True, sentence_splitter=one_sentence)
        self.assertEqual(self.checkpoint.read_bytes(), before)
        rows = list(self.rows)
        rows[0] = {**rows[0], "teacher_response": "Changed source response."}
        pq.write_table(pa.Table.from_pylist(rows, schema=self.schema), self.source)
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            self.run_job(FakeGenerator(), resume=True)
        self.assertEqual(self.checkpoint.read_bytes(), before)

    def test_retry_limit_chain_and_attempt_order_are_verified(self):
        with self.assertRaisesRegex(RuntimeError, "exhausted 1 attempts"):
            self.run_job(FakeGenerator({0: GeneratedResponse("", "stop", 2)}),
                         config=replace(self.config, max_attempts=1))
        with self.assertRaisesRegex(RuntimeError, "simulated interruption"):
            self.run_job(FakeGenerator(crash_on_attempts={(0, 2)}), resume=True)
        saved = self.checkpoint.read_text(encoding="utf-8")
        lines = saved.splitlines()
        update = json.loads(lines[-1])
        update["previous_fingerprint"] = "wrong predecessor"
        lines[-1] = json.dumps(update)
        self.checkpoint.write_text("\n".join(lines) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "invalid retry limit"):
            self.run_job(FakeGenerator(), resume=True)

        # An attempt over the old limit is invalid before the durable update.
        self.checkpoint.write_text(saved, encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "simulated interruption"):
            self.run_job(FakeGenerator(crash_on_attempts={(1, 1)}), resume=True)
        lines = self.checkpoint.read_text(encoding="utf-8").splitlines()
        lines[2], lines[3] = lines[3], lines[2]
        self.checkpoint.write_text("\n".join(lines) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "invalid checkpoint attempt"):
            self.run_job(FakeGenerator(), resume=True)

    def test_retry_increase_rejects_completed_audit_without_mutating_checkpoint(self):
        self.run_job(FakeGenerator(), config=replace(self.config, max_attempts=1))
        self.output.rename(self.output.with_suffix(".saved.parquet"))
        before_checkpoint, before_audit = self.checkpoint.read_bytes(), self.audit.read_bytes()
        generator = FakeGenerator()
        with self.assertRaisesRegex(FileExistsError, "does not match"):
            self.run_job(generator, resume=True)
        self.assertEqual(generator.calls, [])
        self.assertEqual(self.checkpoint.read_bytes(), before_checkpoint)
        self.assertEqual(self.audit.read_bytes(), before_audit)

    def test_resume_repairs_only_an_incomplete_tail(self):
        self.fail_after_first()
        with self.checkpoint.open("ab") as handle:
            handle.write(b'{"partial":')
        generator = FakeGenerator()
        self.run_job(generator, resume=True)
        self.assertEqual(generator.calls, [1, 2])
        for line in self.checkpoint.read_text(encoding="utf-8").splitlines():
            json.loads(line)

    def test_resume_rejects_input_and_config_drift(self):
        self.fail_after_first()
        generator = FakeGenerator()
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            self.run_job(generator, resume=True, config=replace(self.config, temperature=0.7))
        self.assertEqual(generator.calls, [])
        rows = list(self.rows)
        rows[1] = {**rows[1], "teacher_response": "Changed source response."}
        pq.write_table(pa.Table.from_pylist(rows, schema=self.schema), self.source)
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            self.run_job(generator, resume=True)
        self.assertEqual(generator.calls, [])

    def test_resume_rejects_tampered_success(self):
        self.fail_after_first()
        lines = self.checkpoint.read_text(encoding="utf-8").splitlines()
        record = json.loads(lines[1])
        record["finish_reason"] = "length"
        lines[1] = json.dumps(record)
        self.checkpoint.write_text("\n".join(lines) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "invalid accepted generation"):
            self.run_job(FakeGenerator(), resume=True)

    def test_resume_rejects_version_two_windowed_checkpoint_without_mutation(self):
        self.fail_after_first()
        lines = self.checkpoint.read_text(encoding="utf-8").splitlines()
        old_meta = json.loads(lines[0])
        old_meta["format_version"] = 2
        old_meta["config"]["window_size"] = 3
        old_meta["config"]["max_output_length"] = 512
        old_meta["generation_contract"]["rolling_prefix"] = True
        old_meta["generation_contract"].pop("inputs_per_response", None)
        lines[0] = json.dumps(old_meta)
        self.checkpoint.write_text("\n".join(lines) + "\n", encoding="utf-8")
        before = self.checkpoint.read_bytes()
        generator = FakeGenerator()
        with self.assertRaisesRegex(ValueError, "fingerprint differs"):
            self.run_job(generator, resume=True)
        self.assertEqual(generator.calls, [])
        self.assertEqual(self.checkpoint.read_bytes(), before)
        self.assertFalse(self.output.exists())

    def test_resume_rejects_tampered_single_response_audit(self):
        self.fail_after_first()
        lines = self.checkpoint.read_text(encoding="utf-8").splitlines()
        record = json.loads(lines[1])
        record["windows"][0]["prefix_sha256"] = "unexpected rolling prefix"
        lines[1] = json.dumps(record)
        self.checkpoint.write_text("\n".join(lines) + "\n", encoding="utf-8")
        generator = FakeGenerator()
        with self.assertRaisesRegex(ValueError, "invalid accepted window audit"):
            self.run_job(generator, resume=True)
        self.assertEqual(generator.calls, [])
        self.assertFalse(self.output.exists())

    def test_fallback_requires_explicit_option_and_is_audited(self):
        generator = FakeGenerator({1: GeneratedResponse("I cannot rewrite this.", "stop", 6)})
        report = self.run_job(generator, config=replace(self.config, on_failure="keep-original"))
        self.assertEqual(report["status_counts"], {"ok": 2, "fallback": 1})
        self.assertEqual(report["fallback_rows"], [1])
        self.assertEqual(report["fallback_reasons"]["refusal"], 1)
        self.assertEqual(report["rejected_generation_attempts"], 3)
        self.assertEqual(generator.attempt_calls, [(0, 1), (1, 1), (1, 2), (1, 3), (2, 1)])
        self.assertEqual(pq.read_table(self.output)["teacher_response"][1].as_py(), self.rows[1]["teacher_response"])

    def test_explicit_fallback_safely_audits_malformed_output_token_counts(self):
        generator = FakeGenerator({index: GeneratedResponse("rewritten answer", "stop", count)
                                   for index, count in enumerate((None, "bad", True))})
        report = self.run_job(generator, config=replace(self.config, on_failure="keep-original", max_attempts=1))
        self.assertEqual(report["status_counts"], {"fallback": 3})
        self.assertEqual(report["fallback_rows"], [0, 1, 2])
        self.assertEqual(report["fallback_reasons"]["invalid_output_token_count"], 3)
        self.assertEqual(report["rejected_generation_attempts"], 3)
        self.assertEqual(report["generated_response_attempts"], 0)
        self.assertIsNone(report["max_decoder_sequence_length"])
        self.assertTrue(pq.read_table(self.output).equals(self.table, check_metadata=True))

    def test_budget_failure_does_not_initialize_backend_or_truncate(self):
        generator = FakeGenerator()
        with self.assertRaisesRegex(ValueError, "No source text is truncated"):
            self.run_job(generator, config=replace(self.config, max_input_tokens=2))
        self.assertEqual(generator.calls, [])
        self.assertFalse(self.checkpoint.exists())
        self.assertFalse(self.output.exists())

    def test_explicit_budget_fallback_does_not_generate(self):
        def forbidden_factory():
            self.fail("backend must not initialize when every row has an explicit budget fallback")
        report = run_paraphrasing(self.source, self.output, replace(self.config, max_input_tokens=2, on_failure="keep-original"),
                                 self.tokenizer, forbidden_factory, self.identity, sentence_splitter=one_sentence)
        self.assertEqual(report["status_counts"], {"fallback": 3})
        self.assertEqual(report["fallback_rows"], [0, 1, 2])
        self.assertTrue(pq.read_table(self.output).equals(self.table, check_metadata=True))

    def test_cpu_inspection_and_output_overwrite(self):
        info = inspect_source(self.source)
        self.assertEqual(info["rows"], 3)
        self.assertFalse(info["token_budget_checked"])
        self.run_job(FakeGenerator())
        with self.assertRaises(FileExistsError):
            self.run_job(FakeGenerator(), resume=True)

    def test_completed_resume_does_not_initialize_backend(self):
        self.run_job(FakeGenerator())
        self.output.rename(self.output.with_suffix(".saved.parquet"))
        self.audit.rename(self.audit.with_suffix(".saved.json"))
        def forbidden_factory():
            self.fail("fully completed checkpoint must not initialize the model")
        report = run_paraphrasing(self.source, self.output, self.config, self.tokenizer, forbidden_factory,
                                 self.identity, resume=True, sentence_splitter=one_sentence)
        self.assertEqual(report["processed_rows"], 3)

    def test_distinct_seed_retry_accepts_second_attempt(self):
        generator = FakeGenerator({(0, 1): GeneratedResponse("truncated response", "length", 511)})
        report = self.run_job(generator)
        self.assertEqual(generator.attempt_calls, [(0, 1), (0, 2), (1, 1), (2, 1)])
        self.assertEqual(report["accepted_attempts"], {"2": 1, "1": 2})
        records = [json.loads(line) for line in self.checkpoint.read_text(encoding="utf-8").splitlines()[1:]]
        self.assertEqual(records[0]["row_index"], records[1]["row_index"])
        self.assertNotEqual(records[0]["seed"], records[1]["seed"])
        self.assertEqual([records[0]["attempt"], records[1]["attempt"]], [1, 2])

    def test_exhausted_attempts_never_finalize_or_repeat_on_resume(self):
        generator = FakeGenerator({0: GeneratedResponse("I cannot rewrite this.", "stop", 6)})
        with self.assertRaisesRegex(RuntimeError, "exhausted 3 attempts"):
            self.run_job(generator)
        self.assertEqual(generator.attempt_calls, [(0, 1), (0, 2), (0, 3)])
        self.assertFalse(self.output.exists())
        self.assertFalse(self.audit.exists())
        resumed = FakeGenerator()
        with self.assertRaisesRegex(RuntimeError, "already exhausted"):
            self.run_job(resumed, resume=True)
        self.assertEqual(resumed.calls, [])

    def test_orphan_audit_recovers_final_publication_without_generation(self):
        def interrupt_publication(temporary, destination):
            if destination == self.output:
                raise OSError("simulated publication interruption")
            publish_new_file(temporary, destination)
        with patch("baseline_acl.paraphrase_up.publish_new_file", side_effect=interrupt_publication):
            with self.assertRaisesRegex(OSError, "publication interruption"):
                self.run_job(FakeGenerator())
        self.assertTrue(self.audit.exists())
        self.assertFalse(self.output.exists())
        before = self.audit.read_bytes()
        generator = FakeGenerator()
        self.run_job(generator, resume=True)
        self.assertEqual(generator.calls, [])
        self.assertEqual(self.audit.read_bytes(), before)
        self.assertEqual(pq.read_table(self.output).num_rows, 3)

    def test_conflicting_orphan_audit_is_never_changed(self):
        self.run_job(FakeGenerator())
        self.output.rename(self.output.with_suffix(".saved.parquet"))
        report = json.loads(self.audit.read_text(encoding="utf-8"))
        report["metadata"]["fingerprint"] = "unrelated job"
        self.audit.write_text(json.dumps(report), encoding="utf-8")
        before = self.audit.read_bytes()
        generator = FakeGenerator()
        with self.assertRaisesRegex(FileExistsError, "does not match"):
            self.run_job(generator, resume=True)
        self.assertEqual(generator.calls, [])
        self.assertEqual(self.audit.read_bytes(), before)

    def test_default_one_attempt_never_silently_retries(self):
        generator = FakeGenerator({0: GeneratedResponse("I cannot rewrite this.", "stop", 6)})
        with self.assertRaisesRegex(RuntimeError, "exhausted 1 attempts"):
            self.run_job(generator, config=replace(self.config, max_attempts=1))
        self.assertEqual(generator.attempt_calls, [(0, 1)])
        self.assertFalse(self.output.exists())

    def test_cpu_preflight_needs_no_weights_and_keeps_long_sources_valid(self):
        config = replace(self.config, max_output_length=2)
        report = preflight_source(self.source, self.tokenizer, config, one_sentence)
        self.assertTrue(report["valid"])
        self.assertFalse(report["model_weights_loaded"])
        self.assertEqual(report["source_responses_longer_than_decoder_allowance"], 3)
        self.assertEqual(report["generation_inputs"], 3)
        self.assertEqual(report["inputs_per_row"], 1)
        self.assertEqual(report["max_sentences_per_row"], 1)
        self.assertEqual(report["paraphrase_mode"], "whole_response")
        self.assertNotIn("windows", report)
        self.assertNotIn("max_windows_per_row", report)


if __name__ == "__main__":
    unittest.main()
