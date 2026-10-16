"""CPU-only rule extraction tests; no real model weights, torch, CUDA or SSH."""

from contextlib import nullcontext, redirect_stdout
from dataclasses import replace
import io
import json
import math
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from baseline_acl.steal_watermark import (
    ContextRef, EstimationConfig, HFProbabilityEstimator, build_context_plan, canonical_json,
    count_prefixes, estimate_rule_document, file_sha256, frequency_weight,
    load_local_tokenizers, main, mean_probabilities, model_asset_identity,
    parse_args, publish_rules, read_training_responses,
    require_same_tokenizers, resolve_device, score_probability_change,
    tokenize_responses, top_candidates, validate_responses, validate_training_path,
)

try:
    import pyarrow as pa
    import pyarrow.parquet as pq
except ImportError:
    pa = pq = None

try:
    import numpy as np
except ImportError:
    np = None


def workspace_tempdir():
    # The Windows sandbox virtual TEMP permits writes but denies atomic moves.
    # Use the explicit writable workspace, and verify the cleanup target before
    # TemporaryDirectory performs its recursive cleanup.
    root = Path(__file__).resolve().parents[1]
    temporary = tempfile.TemporaryDirectory(prefix=".steal-test-", dir=root)
    if not Path(temporary.name).resolve().is_relative_to(root):
        raise AssertionError("test cleanup directory is outside the workspace")
    return temporary


class FakeTokenizer:
    pad_token_id = 0
    eos_token_id = 0
    bos_token_id = None
    name_or_path = "fake-tokenizer"

    def __len__(self):
        return 6

    def encode(self, text, add_special_tokens=False):
        if add_special_tokens:
            raise AssertionError("rules must be estimated from answer tokens without prompts/special tokens")
        return [int(word) for word in text.split()]


class MathAndContextTests(unittest.TestCase):
    def test_formula_positive_only_ratio_capped_and_zero_safe(self):
        before = {0: 0.1, 1: 0.2, 2: 0.0, 3: 0.0, 4: 0.4, 5: 0.1}
        after = {0: 0.15, 1: 0.6, 2: 0.05, 3: 0.0, 4: 0.15, 5: 0.1}
        scores = score_probability_change(before, after)
        self.assertAlmostEqual(scores["0"], 0.75)
        self.assertEqual(scores["1"], 1.0)
        self.assertEqual(scores["2"], 1.0)
        self.assertEqual(set(scores), {"0", "1", "2"})
        dense = score_probability_change(before, after, include_zero=True)
        self.assertEqual(set(dense), {str(token) for token in after})
        self.assertEqual(dense["4"], 0.0)
        self.assertEqual(dense["5"], 0.0)
        with self.assertRaisesRegex(ValueError, "missing"):
            score_probability_change({}, {0: 0.1})
        for bad in (-0.1, 1.1, math.nan, math.inf):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                score_probability_change({0: bad}, {0: 0.2})

    def test_mean_probabilities_precede_ratio_not_mean_of_ratios(self):
        before = mean_probabilities([[0.1, 0.9], [0.8, 0.2]])
        after = mean_probabilities([[0.3, 0.7], [0.6, 0.4]])
        scores = score_probability_change(dict(enumerate(before)), dict(enumerate(after)))
        self.assertNotIn("0", scores)
        self.assertGreater((0.3 / 0.1 + 0.6 / 0.8) / 2, 1)
        self.assertAlmostEqual(after[0] / before[0], 1.0)

    def test_top_k_after_full_mean_probability_and_no_topk_renormalization(self):
        average = mean_probabilities([[0.8, 0.2, 0.0], [0.0, 0.2, 0.8]])
        self.assertEqual(top_candidates(average, 1), {0: 0.4})
        self.assertEqual(top_candidates(average, 2), {0: 0.4, 2: 0.4})
        for vectors in ([], [[0.1, 0.9], [1.0]], [[math.nan]], [[]]):
            with self.subTest(vectors=vectors), self.assertRaises(ValueError):
                mean_probabilities(vectors)

    def test_prefix_frequency_strict_boundary_and_separate_order_denominators(self):
        config = EstimationConfig(freq_threshold=0.25)
        selected, order_info = count_prefixes([[1, 1, 2, 3, 4]], config)
        self.assertEqual(selected[(1,)]["count"], 2)
        self.assertEqual(selected[(1,)]["frequency"], 0.5)
        self.assertNotIn((2,), selected)  # frequency exactly threshold excluded
        self.assertNotIn((3,), selected)
        self.assertNotIn((4,), selected)  # Final answer token excluded before counting.
        self.assertAlmostEqual(selected[(1, 2)]["frequency"], 1 / 3)
        self.assertEqual(order_info["1"]["occurrences"], 4)
        self.assertEqual(order_info["2"]["occurrences"], 3)

    def test_frequency_weight_uses_log_relative_frequency(self):
        expected = (math.log(0.02) / math.log(0.2)) ** -0.3
        self.assertAlmostEqual(frequency_weight(0.02, 0.2, 0.3), expected)
        self.assertLess(frequency_weight(0.02, 0.2, 0.3), 1)
        self.assertEqual(frequency_weight(0.2, 0.2, 0.3), 1)
        self.assertEqual(frequency_weight(1, 1, 0.3), 1)
        self.assertEqual(frequency_weight(0.02, 0.2, 0), 1)
        for frequency, maximum, alpha in ((0, 0.2, 0.3), (0.5, 0.2, 0.3),
                                          (0.2, 1, 0.3), (math.nan, 0.2, 0.3), (0.2, 0.3, -1)):
            with self.subTest(values=(frequency, maximum, alpha)), self.assertRaises(ValueError):
                frequency_weight(frequency, maximum, alpha)

    def test_frequency_excludes_final_token_but_contexts_use_full_answer_prefixes(self):
        config = EstimationConfig(freq_threshold=0, max_context_tokens=2)
        plan = build_context_plan([[1, 2, 3, 4]], config)
        self.assertEqual(plan.prefix_metadata[(3,)]["frequency"], 1 / 3)
        self.assertNotIn((4,), plan.prefix_metadata)
        self.assertNotIn((2, 3), plan.contexts)
        self.assertEqual(plan.contexts[(2,)], [ContextRef(0, 2)])
        self.assertEqual(plan.statistics["global_eligible_contexts"], 2)
        self.assertEqual(plan.statistics["global_retained_contexts"], 2)
        self.assertEqual(plan.statistics["late_context_positions_excluded"], 2)
        self.assertEqual(plan.statistics["empty_contexts_excluded"], 1)
        self.assertIn("3", plan.statistics["selected_prefixes_without_context"])
        for contexts in plan.contexts.values():
            self.assertTrue(all(1 <= ref.end <= 2 for ref in contexts))

    def test_conditional_contexts_shuffle_then_truncate_without_setting_seed(self):
        # A controlled shuffle makes exact selected refs observable without
        # relying on or changing the process's random seed in production.
        def reverse(contexts):
            contexts.reverse()
        with patch("baseline_acl.steal_watermark.random.shuffle", side_effect=reverse) as shuffle, \
             patch("baseline_acl.steal_watermark.random.seed", side_effect=AssertionError("no fixed seed")), \
             patch("baseline_acl.steal_watermark.random.Random", side_effect=AssertionError("no private fixed RNG")):
            plan = build_context_plan([[1] * 200], EstimationConfig(max_contexts_per_prefix=7))
        self.assertEqual(plan.contexts[(1,)], [ContextRef(0, end) for end in range(200, 193, -1)])
        self.assertEqual(plan.prefix_metadata[(1,)]["eligible_contexts"], 200)
        self.assertEqual(shuffle.call_count, 2)  # One- and two-token conditional groups only.
        self.assertEqual(plan.statistics["global_retained_contexts"], 200)
        self.assertNotIn((), plan.contexts)

    def test_groups_at_or_below_limit_keep_all_contexts_without_shuffle(self):
        with patch("baseline_acl.steal_watermark.random.shuffle", side_effect=AssertionError("no subsampling")):
            plan = build_context_plan([[1, 1, 1]], EstimationConfig(max_contexts_per_prefix=3))
        self.assertEqual(plan.contexts[(1,)], [ContextRef(0, 1), ContextRef(0, 2), ContextRef(0, 3)])
        self.assertEqual(plan.contexts[(1, 1)], [ContextRef(0, 2), ContextRef(0, 3)])

    def test_frequency_exclusion_applies_per_answer_and_never_crosses_rows(self):
        selected, orders = count_prefixes([[1, 2, 5], [3, 4, 5], [5]], EstimationConfig(freq_threshold=0))
        self.assertEqual(orders["1"]["occurrences"], 4)
        self.assertEqual(orders["2"]["occurrences"], 2)
        self.assertEqual({prefix for prefix in selected if len(prefix) == 2}, {(1, 2), (3, 4)})
        self.assertNotIn((5,), selected)
        self.assertNotIn((2, 3), selected)

    def test_unigram_only_has_global_rule_without_prefixes(self):
        plan = build_context_plan([[1, 2]], EstimationConfig(max_ngram=1))
        self.assertEqual(plan.contexts, {})
        self.assertEqual(plan.prefix_metadata, {})
        self.assertEqual(plan.statistics["global_retained_contexts"], 2)

    def test_configs_and_empty_contexts_rejected(self):
        for values in ({"max_ngram": 4}, {"freq_threshold": 1}, {"alpha": -1},
                       {"top_k": 0}, {"max_contexts_per_prefix": 0}, {"max_context_tokens": 0},
                       {"batch_size": 0}):
            with self.subTest(values=values), self.assertRaises(ValueError):
                replace(EstimationConfig(), **values).validate()
        for rows in ([], [[]]):
            with self.assertRaises(ValueError):
                build_context_plan(rows, EstimationConfig())


class ArrayTensor:
    """Small numerical test adapter; the actual estimator method runs unchanged."""

    def __init__(self, values):
        self.values = np.asarray(values)

    @property
    def shape(self):
        return self.values.shape

    def __getitem__(self, key):
        return ArrayTensor(self.values[key])

    def __eq__(self, other):
        return ArrayTensor(self.values == other)

    def __sub__(self, other):
        return ArrayTensor(self.values - other)

    def __add__(self, other):
        return ArrayTensor(self.values + other.values)

    def __truediv__(self, other):
        return ArrayTensor(self.values / other)

    def cumsum(self, dim):
        return ArrayTensor(self.values.cumsum(axis=dim))

    def masked_fill_(self, mask, value):
        self.values[mask.values] = value
        return self

    def float(self):
        return ArrayTensor(self.values.astype(np.float32))

    def sum(self, dim=None, dtype=None):
        return ArrayTensor(self.values.sum(axis=dim, dtype=dtype))

    def all(self):
        return ArrayTensor(self.values.all())

    def item(self):
        return self.values.item()

    def cpu(self):
        return self

    def tolist(self):
        return self.values.tolist()


class ArrayTorch:
    """NumPy softmax provides an independent numerical oracle without Torch."""

    @staticmethod
    def tensor(values, dtype=None, device=None):
        return ArrayTensor(np.asarray(values, dtype=dtype))

    @staticmethod
    def inference_mode():
        return nullcontext()

    @staticmethod
    def softmax(tensor, dim):
        shifted = tensor.values - tensor.values.max(axis=dim, keepdims=True)
        exponentials = np.exp(shifted)
        return ArrayTensor(exponentials / exponentials.sum(axis=dim, keepdims=True))

    @staticmethod
    def isfinite(tensor):
        return ArrayTensor(np.isfinite(tensor.values))

    @property
    def long(self):
        return np.int64

    @property
    def float64(self):
        return np.float64


@unittest.skipIf(np is None, "numpy unavailable; global numerical checks need the bundled Python runtime")
class GlobalPositionTests(unittest.TestCase):
    def make_estimator(self, probabilities=None, logit_parameter="logits_to_keep"):
        probability_rows = probabilities or {
            0: [0.97, 0.01, 0.01, 0.01],  # Also used for padding, which must be excluded.
            1: [0.80, 0.10, 0.05, 0.05],
            2: [0.10, 0.20, 0.30, 0.40],
            3: [0.05, 0.10, 0.05, 0.80],
        }
        calls = []

        class Model:
            def __call__(self, input_ids, attention_mask, position_ids, use_cache, **kwargs):
                calls.append((input_ids.values.copy(), attention_mask.values.copy(),
                              position_ids.values.copy(), kwargs))
                distributions = np.asarray([[probability_rows[int(token)] for token in row]
                                            for row in input_ids.values])
                logits = np.log(distributions)
                if kwargs.get(logit_parameter) == 1:
                    logits = logits[:, -1:, :]
                return SimpleNamespace(logits=ArrayTensor(logits))

        estimator = HFProbabilityEstimator.__new__(HFProbabilityEstimator)
        estimator.torch = ArrayTorch()
        estimator.device = "cpu"
        estimator.pad_token_id = 0
        estimator.vocab_size = 3  # Model has an extra slot; keep its softmax mass.
        estimator.logits_kwargs = {logit_parameter: 1}
        estimator.model = Model()
        return estimator, calls

    def test_global_uses_every_valid_position_with_token_weighting_and_full_softmax(self):
        # One short answer contributes one position, the longer contributes
        # three. The fourth token is past the limit and must not contribute.
        for parameter in ("logits_to_keep", "num_logits_to_keep"):
            with self.subTest(parameter=parameter):
                estimator, calls = self.make_estimator(logit_parameter=parameter)
                actual = estimator.mean_global([[1], [2, 2, 2, 3]], batch_size=2, max_context_tokens=3)
                expected = {0: (0.8 + 3 * 0.1) / 4,
                            1: (0.1 + 3 * 0.2) / 4,
                            2: (0.05 + 3 * 0.3) / 4}
                self.assertEqual(set(actual), {0, 1, 2})
                for token, value in expected.items():
                    self.assertAlmostEqual(actual[token], value, places=6)
                self.assertAlmostEqual(sum(actual.values()), 0.6875, places=6)
                self.assertFalse(np.any(calls[0][0] == 3))
                np.testing.assert_array_equal(calls[0][1], [[0, 0, 1], [1, 1, 1]])
                np.testing.assert_array_equal(calls[0][2], [[0, 0, 0], [0, 1, 2]])
                self.assertEqual(calls[0][3][parameter], 0)
                self.assertEqual(estimator.logits_kwargs[parameter], 1)  # Conditional optimization preserved.
                single_batch = estimator.mean_global([[1], [2, 2, 2, 3]], batch_size=1, max_context_tokens=3)
                for token in actual:
                    self.assertAlmostEqual(single_batch[token], actual[token], places=6)

    def test_valid_token_equal_to_padding_id_still_contributes(self):
        estimator, _ = self.make_estimator()
        actual = estimator.mean_global([[0], [2, 2]], batch_size=2, max_context_tokens=200)
        self.assertAlmostEqual(actual[0], (0.97 + 2 * 0.1) / 3, places=6)
        self.assertAlmostEqual(actual[1], (0.01 + 2 * 0.2) / 3, places=6)

    def test_global_rejects_last_position_only_or_missing_vocabulary(self):
        estimator, _ = self.make_estimator()
        original_model = estimator.model
        def last_position_only(**kwargs):
            output = original_model(**kwargs)
            return SimpleNamespace(logits=output.logits[:, -1:, :])
        estimator.model = last_position_only
        with self.assertRaisesRegex(ValueError, "every input position"):
            estimator.mean_global([[1, 2]], batch_size=1, max_context_tokens=200)
        estimator, _ = self.make_estimator({1: [0.5, 0.5]})
        with self.assertRaisesRegex(ValueError, "vocabulary"):
            estimator.mean_global([[1]], batch_size=1, max_context_tokens=200)

    def test_global_input_validation_and_nonfinite_probabilities(self):
        estimator, _ = self.make_estimator()
        for rows in ([], [[]]):
            with self.subTest(rows=rows), self.assertRaisesRegex(ValueError, "nonempty"):
                estimator.mean_global(rows, batch_size=1, max_context_tokens=200)
        for batch_size, limit in ((0, 200), (1, 0)):
            with self.subTest(batch_size=batch_size, limit=limit), self.assertRaisesRegex(ValueError, "positive"):
                estimator.mean_global([[1]], batch_size=batch_size, max_context_tokens=limit)
        estimator, _ = self.make_estimator({1: [math.nan, 0.1, 0.1, 0.8]})
        with self.assertRaisesRegex(ValueError, "non-finite"):
            estimator.mean_global([[1]], batch_size=1, max_context_tokens=200)


class InputAndDeviceTests(unittest.TestCase):
    def test_input_must_be_training_parquet(self):
        for name in ("original_kgw_train.parquet", "dolly15k_qwen2_5_14b_kgw_gamma0.5_delta3_newtrain.parquet"):
            with self.subTest(name=name):
                validate_training_path(Path(name))
        for name in ("kgw_test.parquet", "kgw_train_test.parquet", "train_val.parquet", "train.json", "kgw.parquet",
                     "kgw_newtrain_test.parquet", "newtrain_val.parquet", "newtrain.json", "kgw_pretrain.parquet"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                validate_training_path(Path(name))
        for values in ([], [None], [42], [" "], ["ok", ""]):
            with self.subTest(values=values), self.assertRaises(ValueError):
                validate_responses(values)
        self.assertEqual(validate_responses([" an answer "]), [" an answer "])

    def test_o_w_tokenizers_must_match_behavior_not_path(self):
        before = {"vocab_size": 6, "fingerprint": "abc", "name_or_path": "O"}
        after = {**before, "name_or_path": "W"}
        require_same_tokenizers(before, after)
        for changed in ({"vocab_size": 7}, {"fingerprint": "different"}):
            with self.subTest(changed=changed), self.assertRaises(ValueError):
                require_same_tokenizers(before, {**after, **changed})

    def test_tokenization_never_adds_prompts_or_special_tokens(self):
        self.assertEqual(tokenize_responses(["1 2", "3"], FakeTokenizer()), [[1, 2], [3]])
        with self.assertRaisesRegex(ValueError, "invalid"):
            tokenize_responses(["6"], FakeTokenizer())
        with self.assertRaisesRegex(ValueError, "no tokens"):
            tokenize_responses([""], FakeTokenizer())

    def test_local_tokenizer_loaders_are_offline_and_verify_identity(self):
        tokenizers = [FakeTokenizer(), FakeTokenizer()]
        identities = [{"vocab_size": 6, "fingerprint": "same", "name_or_path": "O"},
                      {"vocab_size": 6, "fingerprint": "same", "name_or_path": "W"}]
        calls = []
        def load(path, **kwargs):
            calls.append((path, kwargs))
            return tokenizers[len(calls) - 1]
        with workspace_tempdir() as temp:
            o, w = Path(temp) / "O", Path(temp) / "W"
            o.mkdir()
            w.mkdir()
            module = SimpleNamespace(AutoTokenizer=SimpleNamespace(from_pretrained=load))
            with patch.dict(sys.modules, {"transformers": module}), \
                 patch("baseline_acl.inverse_watermark.tokenizer_identity", side_effect=identities):
                _, before, after = load_local_tokenizers(o, w)
            self.assertEqual(before["fingerprint"], after["fingerprint"])
            self.assertEqual(len(calls), 2)
            self.assertTrue(all(kwargs == {"local_files_only": True, "trust_remote_code": False} for _, kwargs in calls))

    def test_gpu_is_explicit_single_card_and_preflight_is_cpu(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(resolve_device("cpu", None), "cpu")
            with self.assertRaises(ValueError):
                resolve_device("cuda", None)
            self.assertEqual(resolve_device("cuda", "3"), "cuda:0")
            self.assertEqual(os.environ["CUDA_VISIBLE_DEVICES"], "3")
            with self.assertRaisesRegex(ValueError, "conflicts"):
                resolve_device("cuda", "4")
        with patch.dict(os.environ, {"CUDA_VISIBLE_DEVICES": "1,3"}, clear=True):
            with self.assertRaises(ValueError):
                resolve_device("cuda", None)
            self.assertEqual(resolve_device("cuda", "4", preflight=True), "cpu")
            self.assertEqual(os.environ["CUDA_VISIBLE_DEVICES"], "1,3")
        with self.assertRaises(ValueError):
            resolve_device("cpu", "1")

    def test_model_identity_records_local_config_and_weight_manifest(self):
        with workspace_tempdir() as temp:
            directory = Path(temp)
            (directory / "config.json").write_text('{"model_type":"qwen2"}', encoding="utf-8")
            (directory / "model.safetensors").write_bytes(b"mock weight bytes")
            info = model_asset_identity(directory, weights_required=True)
            files = {entry["name"]: entry for entry in info["files"]}
            self.assertIn("sha256", files["config.json"])
            self.assertNotIn("sha256", files["model.safetensors"])
            full = model_asset_identity(directory, weights_required=True, hash_weights=True)
            self.assertTrue(full["weights_fully_hashed"])
            self.assertIn("sha256", full["files"][1])
            (directory / "model.safetensors.index.json").write_text('{"weight_map":{"x":"missing.safetensors"}}', encoding="utf-8")
            with self.assertRaisesRegex(FileNotFoundError, "shard"):
                model_asset_identity(directory, weights_required=True)

    def test_parser_help_and_preflight_need_no_output_or_torch(self):
        args = parse_args(["--input", "train.parquet", "--model-before", "O", "--model-after", "W", "--preflight"])
        self.assertIsNone(args.output)
        self.assertEqual(args.tokenizer_before, Path("O"))
        self.assertEqual(args.tokenizer_after, Path("W"))
        self.assertFalse(hasattr(args, "seed"))
        with redirect_stdout(io.StringIO()), patch("sys.stderr", new=io.StringIO()), self.assertRaises(SystemExit):
            parse_args(["--input", "train.parquet", "--model-before", "O", "--model-after", "W",
                        "--preflight", "--seed", "42"])
        identity = {"vocab_size": 6, "fingerprint": "fake", "name_or_path": "fake"}
        with patch("baseline_acl.steal_watermark.model_asset_identity", return_value={}), \
             patch("baseline_acl.steal_watermark.load_local_tokenizers", return_value=(FakeTokenizer(), identity, identity)), \
             patch("baseline_acl.steal_watermark.read_training_responses", return_value=(["1 2 3"], {"rows": 1})), \
             patch("baseline_acl.steal_watermark.HFProbabilityEstimator", side_effect=AssertionError("no model in preflight")), \
             patch("baseline_acl.steal_watermark.publish_rules", side_effect=AssertionError("no write in preflight")), \
             redirect_stdout(io.StringIO()) as output:
            code = main(["--input", "train.parquet", "--model-before", "O", "--model-after", "W", "--preflight", "--device", "cuda", "--top-k", "3"])
        self.assertEqual(code, 0)
        report = json.loads(output.getvalue())
        self.assertFalse(report["model_weights_loaded"])
        self.assertFalse(report["device_probed"])


class MockExecutionTests(unittest.TestCase):
    def test_sequential_models_same_contexts_and_shared_rule_contract(self):
        events = []
        contexts_seen = {"O": [], "W": []}
        global_seen = {}
        class MockEstimator:
            dtype_name = "float32"
            def __init__(self, path, tokenizer, device, dtype):
                self.name = str(path)
                events.append(("load", self.name))
            def mean_global(self, token_rows, batch_size, max_context_tokens):
                global_seen[self.name] = ([list(row) for row in token_rows], batch_size, max_context_tokens)
                if self.name == "W":
                    return {0: 0.1, 1: 0.2, 2: 0.3, 3: 0.2, 4: 0.15, 5: 0.05}
                return {0: 0.15, 1: 0.3, 2: 0.1, 3: 0.25, 4: 0.18, 5: 0.02}
            def mean(self, contexts, batch_size, candidate_ids=None, top_k=50):
                contexts_seen[self.name].append([list(context) for context in contexts])
                if self.name == "W":
                    return {2: 0.3, 1: 0.2}
                if candidate_ids != [2, 1]:
                    raise AssertionError("O must use W candidates after W has averaged all contexts")
                return {2: 0.1, 1: 0.3}
            def close(self):
                events.append(("close", self.name))
        config = EstimationConfig(top_k=2, max_context_tokens=2, max_contexts_per_prefix=1, freq_threshold=0)
        plan = build_context_plan([[1, 2, 3]], config)
        identity = {"vocab_size": 6, "fingerprint": "a" * 64, "name_or_path": "fake"}
        document = estimate_rule_document(plan, config, identity, Path("O"), Path("W"),
                                          FakeTokenizer(), "cpu", "auto", {}, MockEstimator)
        self.assertEqual(events, [("load", "W"), ("close", "W"), ("load", "O"), ("close", "O")])
        self.assertEqual(contexts_seen["O"], contexts_seen["W"])
        self.assertEqual(global_seen["O"], global_seen["W"])
        self.assertEqual(global_seen["W"], ([[1, 2, 3]], 4, 2))
        self.assertEqual(document["global_scores"], {"0": 0.0, "1": 0.0, "2": 1.0, "3": 0.0, "4": 0.0, "5": 1.0})
        # Token 5 has a positive global score despite never being a conditional
        # top-k candidate; zero-valued global entries also remain explicit.
        self.assertEqual(len(document["global_scores"]), len(FakeTokenizer()))
        self.assertEqual(plan.statistics["global_retained_contexts"], 2)
        self.assertEqual(set(document["prefix_scores"]), {"1", "2", "1,2"})
        self.assertEqual(document["prefix_scores"]["2"]["scores"], {"2": 1.0})
        self.assertEqual(document["parameters"]["dtype_actual"], "float32")
        self.assertNotIn("seed", document["parameters"])
        from baseline_acl.inverse_watermark import RuleTable
        table = RuleTable(document)
        self.assertAlmostEqual(table.penalties([1, 2])[2], 3.0)
        self.assertEqual(table.penalties([1, 2])[5], 1.0)
        self.assertNotIn(0, table.penalties([1, 2]))

    def test_models_are_closed_when_probability_estimation_fails(self):
        closed = []
        class FailingEstimator:
            def __init__(self, *args):
                pass
            def mean(self, *args, **kwargs):
                raise RuntimeError("simulated model error")
            mean_global = mean
            def close(self):
                closed.append(True)
        config = EstimationConfig(top_k=2)
        plan = build_context_plan([[1]], config)
        with self.assertRaisesRegex(RuntimeError, "simulated"):
            estimate_rule_document(plan, config, {}, Path("O"), Path("W"), None,
                                   "cpu", "auto", {}, FailingEstimator)
        self.assertEqual(closed, [True])

    def test_rule_publication_is_atomic_and_never_overwrites(self):
        with workspace_tempdir() as temp:
            output = Path(temp) / "new.json"
            document = {"rule": {"2": 0.75}}
            publish_rules(output, document)
            first_hash = file_sha256(output)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8")), document)
            with self.assertRaises(FileExistsError):
                publish_rules(output, {"different": True})
            self.assertEqual(file_sha256(output), first_hash)
            self.assertFalse(list(Path(temp).glob("*.tmp")))
            invalid = Path(temp) / "invalid.json"
            with self.assertRaises(ValueError):
                publish_rules(invalid, {"nan": math.nan})
            self.assertFalse(invalid.exists())
            self.assertFalse(list(Path(temp).glob("*.tmp")))

    def test_atomic_publication_preserves_destination_created_during_race(self):
        operation = "rename" if os.name == "nt" else "link"
        real_publish = getattr(os, operation)
        with workspace_tempdir() as temp:
            output = Path(temp) / "rules.json"
            def competing_writer(source, destination):
                Path(destination).write_text("existing run", encoding="utf-8")
                return real_publish(source, destination)
            with patch(f"baseline_acl.steal_watermark.os.{operation}", side_effect=competing_writer):
                with self.assertRaises(FileExistsError):
                    publish_rules(output, {"new": True})
            self.assertEqual(output.read_text(encoding="utf-8"), "existing run")
            self.assertFalse(list(Path(temp).glob("*.tmp")))


@unittest.skipIf(pa is None, "pyarrow unavailable; pure CPU tests remain active")
class RealParquetContractTests(unittest.TestCase):
    def test_only_teacher_responses_are_loaded_and_source_is_unchanged(self):
        with workspace_tempdir() as temp:
            path = Path(temp) / "original_kgw_train.parquet"
            table = pa.table({"id": [1, 2], "content": ["question A", "question B"],
                              "teacher_response": ["1 2", "2 3"], "other": [3, 4]})
            pq.write_table(table, path)
            before = file_sha256(path)
            responses, info = read_training_responses(path)
            self.assertEqual(responses, ["1 2", "2 3"])
            self.assertEqual(info["column"], "teacher_response")
            self.assertEqual(info["split"], "train")
            self.assertEqual(info["rows"], 2)
            self.assertEqual(file_sha256(path), before)
            self.assertEqual(pq.read_table(path).to_pydict(), table.to_pydict())

    def test_bad_columns_types_and_empty_rows_are_rejected(self):
        with workspace_tempdir() as temp:
            path = Path(temp) / "train.parquet"
            bad_tables = [pa.table({"answer": ["answer"]}), pa.table({"teacher_response": [1]}),
                          pa.table({"teacher_response": pa.array([], type=pa.string())}),
                          pa.table({"teacher_response": pa.array([None], type=pa.string())})]
            for table in bad_tables:
                with self.subTest(table=table.to_pydict()):
                    pq.write_table(table, path)
                    with self.assertRaises(ValueError):
                        read_training_responses(path)


if __name__ == "__main__":
    unittest.main()
