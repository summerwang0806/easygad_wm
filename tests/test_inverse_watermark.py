"""CPU tests of rule identity, schema validation and actual inverse bias."""

import copy
import inspect
import json
from pathlib import Path
import tempfile
import unittest

from baseline_acl.inverse_watermark import (
    RuleTable, VLLMInverseWatermarkProcessor, TransformersInverseWatermarkProcessor, tokenizer_identity,
)


class FakeTokenizer:
    def __init__(self, path="local/tokenizer"):
        self.name_or_path = path
        self.init_kwargs = {"name_or_path": path, "vocab_file": path + "/vocab.json", "do_lower_case": False}
        self.special_tokens_map = {"eos_token": "<eos>"}
        self.all_special_ids = [0]
        self.added_tokens_decoder = {}
        self.chat_template = "test-template"
        self.vocab = {"<eos>": 0, "a": 1, "b": 2, "c": 3}

    def get_vocab(self):
        return self.vocab.copy()

    def __len__(self):
        return len(self.vocab)

    def encode(self, text, add_special_tokens=False):
        return [self.vocab[word] for word in text.split()]

    def apply_chat_template(self, messages, add_generation_prompt=True, tokenize=False):
        return " ".join(message["content"] for message in messages)


def rules_document(tokenizer=None):
    return {
        "format": "acl-watermark-rules", "version": 1,
        "tokenizer": tokenizer_identity(tokenizer or FakeTokenizer()),
        "parameters": {"max_ngram": 3, "freq_threshold": 5e-5, "alpha": 0.3, "top_k": 4},
        "provenance": {"source": "unit-test"},
        "global_scores": {"3": 0.7},
        "prefix_scores": {
            "2": {"weight": 1.0, "frequency": 0.2, "count": 20, "scores": {"3": 0.9}},
            "1,2": {"weight": 1.0, "frequency": 0.1, "count": 10, "scores": {"3": 0.8, "1": 0.2}},
        },
    }


class IdentityTests(unittest.TestCase):
    def test_path_independent_but_vocab_and_configuration_sensitive(self):
        original = FakeTokenizer("old/path")
        moved = FakeTokenizer("new/path")
        self.assertEqual(tokenizer_identity(original)["fingerprint"], tokenizer_identity(moved)["fingerprint"])
        self.assertNotEqual(tokenizer_identity(original)["name_or_path"], tokenizer_identity(moved)["name_or_path"])
        variants = []
        swapped = copy.deepcopy(original)
        swapped.vocab["a"], swapped.vocab["b"] = swapped.vocab["b"], swapped.vocab["a"]
        variants.append(swapped)
        special = copy.deepcopy(original)
        special.all_special_ids = [1]
        variants.append(special)
        config = copy.deepcopy(original)
        config.init_kwargs["do_lower_case"] = True
        variants.append(config)
        template = copy.deepcopy(original)
        template.chat_template = "different-template"
        variants.append(template)
        for variant in variants:
            with self.subTest(variant=variant.__dict__):
                self.assertNotEqual(tokenizer_identity(original)["fingerprint"], tokenizer_identity(variant)["fingerprint"])
                with self.assertRaisesRegex(ValueError, "tokenizer mismatch"):
                    RuleTable(rules_document(original)).validate_tokenizer(variant)

    def test_backend_normalizer_included_but_runtime_padding_ignored(self):
        class Backend:
            def __init__(self, lower=False, padding=None):
                self.lower = lower
                self.padding = padding

            def to_str(self):
                return json.dumps({"normalizer": {"lower": self.lower}, "padding": self.padding,
                                   "truncation": None, "model": {"type": "BPE"}})

        tokenizer = FakeTokenizer()
        tokenizer.backend_tokenizer = Backend()
        original = tokenizer_identity(tokenizer)["fingerprint"]
        tokenizer.backend_tokenizer.padding = {"length": 100}
        self.assertEqual(original, tokenizer_identity(tokenizer)["fingerprint"])
        tokenizer.backend_tokenizer.lower = True
        self.assertNotEqual(original, tokenizer_identity(tokenizer)["fingerprint"])


class RuleTests(unittest.TestCase):
    def test_weighted_global_and_all_matching_suffixes_without_total_cap(self):
        rules = RuleTable(rules_document())
        self.assertAlmostEqual(rules.penalties([0, 1, 2])[3], 2.4)
        self.assertAlmostEqual(rules.confidence([1, 2], 1), 0.2)
        self.assertEqual(rules.confidence([1, 2], 2), 0)
        modified = rules_document()
        modified["prefix_scores"]["2"]["weight"] = 0.5
        self.assertAlmostEqual(RuleTable(modified).confidence([1, 2], 3), 0.7 + 0.45 + 0.8)

    def test_short_prefix_and_missing_prefix_use_available_scores(self):
        rules = RuleTable(rules_document())
        self.assertEqual(rules.penalties([]), {3: 0.7})
        self.assertEqual(rules.penalties([1]), {3: 0.7})
        self.assertAlmostEqual(rules.penalties([2])[3], 1.6)
        self.assertEqual(rules.penalties([0, 1]), {3: 0.7})

    def test_single_token_queries_agree_with_full_bias_for_dense_global_rules(self):
        document = rules_document()
        document["global_scores"].update({"0": 0.0, "1": 0.4, "2": 0.0})
        document["prefix_scores"]["2"]["weight"] = 0.5
        rules = RuleTable(document)
        for context in ([], [1], [2], [1, 2], [0, 1, 2], [999, 1, 2]):
            penalties = rules.penalties(context)
            for token_id in range(rules.vocab_size):
                with self.subTest(context=context, token_id=token_id):
                    self.assertAlmostEqual(rules.confidence(context, token_id), penalties.get(token_id, 0.0))
        document["parameters"]["max_ngram"] = 1
        document["prefix_scores"] = {}
        global_only = RuleTable(document)
        self.assertEqual(global_only.confidence(["unused-prefix"], 1), 0.4)

    def test_schema_rejects_unsafe_or_ambiguous_rules(self):
        mutations = [
            lambda doc: doc.update(format="kgw-secret-key-rules"),
            lambda doc: doc.update(version=True),
            lambda doc: doc["tokenizer"].update(fingerprint="unknown"),
            lambda doc: doc["global_scores"].update({"4": 0.1}),
            lambda doc: doc["global_scores"].update({"01": 0.1}),
            lambda doc: doc["global_scores"].update({"2": 1.01}),
            lambda doc: doc["global_scores"].update({"2": float("nan")}),
            lambda doc: doc["prefix_scores"]["2"].update(weight=-0.1),
            lambda doc: doc["prefix_scores"]["2"].update(frequency=0),
            lambda doc: doc["prefix_scores"]["2"].update(count=True),
            lambda doc: doc["parameters"].update(max_ngram=2),
        ]
        for mutation in mutations:
            document = rules_document()
            mutation(document)
            with self.subTest(document=document), self.assertRaises(ValueError):
                RuleTable(document)

    def test_load_and_duplicate_json_key_protection(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "rules.json"
            path.write_text(json.dumps(rules_document()), encoding="utf-8")
            self.assertAlmostEqual(RuleTable.load(path).confidence([1, 2], 3), 2.4)
            path.write_text('{"format":"acl-watermark-rules","format":"other"}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                RuleTable.load(path)

    def test_invalid_context_rejected(self):
        rules = RuleTable(rules_document())
        for context in ([4], [-1], [True], ["1"]):
            with self.subTest(context=context), self.assertRaises(ValueError):
                rules.penalties(context)
            with self.subTest(context=context), self.assertRaises(ValueError):
                rules.confidence(context, 3)
        for token_id in (-1, 4, True, "1"):
            with self.subTest(token_id=token_id), self.assertRaises(ValueError):
                rules.confidence([], token_id)


class ProcessorTests(unittest.TestCase):
    def test_three_argument_hook_uses_prompt_and_generated_context(self):
        rules = RuleTable(rules_document())
        processor = VLLMInverseWatermarkProcessor(rules, strength=2.5)
        self.assertEqual(len(inspect.signature(processor).parameters), 3)
        for prompt, generated in (([0, 1, 2], []), ([0, 1], [2]), ([0], [1, 2])):
            logits = [10.0] * 5
            result = processor(prompt, generated, logits)
            self.assertIs(result, logits)
            self.assertAlmostEqual(logits[3], 10 - 2.5 * 2.4)
            self.assertAlmostEqual(logits[1], 10 - 2.5 * 0.2)
            self.assertEqual(logits[4], 10)

    def test_zero_strength_is_an_exact_no_op(self):
        processor = VLLMInverseWatermarkProcessor(RuleTable(rules_document()), 0)
        logits = [1.0, 2.0, 3.0, 4.0]
        self.assertIs(processor([1, 2], [], logits), logits)
        self.assertEqual(logits, [1.0, 2.0, 3.0, 4.0])

    def test_negative_or_nonfinite_strength_rejected(self):
        for strength in (-0.1, float("nan"), float("inf")):
            with self.subTest(strength=strength), self.assertRaises(ValueError):
                VLLMInverseWatermarkProcessor(RuleTable(rules_document()), strength)


class BatchScores:
    """Mutable two-dimensional scores without importing torch or NumPy."""

    def __init__(self, rows):
        self.rows = rows
        self.shape = (len(rows), len(rows[0]))

    def __getitem__(self, index):
        return self.rows[index]


class TransformersProcessorTests(unittest.TestCase):
    def test_tp_and_wn_apply_identical_bias_to_each_distinct_prefix(self):
        rules = RuleTable(rules_document())
        histories = [[0, 1, 2], [0, 0, 1], [2]]
        scores = BatchScores([[10.0] * 6 for _ in histories])
        tp = TransformersInverseWatermarkProcessor(rules, 2.5)
        self.assertEqual(len(inspect.signature(tp).parameters), 2)
        self.assertIs(tp(histories, scores), scores)
        wn = VLLMInverseWatermarkProcessor(rules, 2.5)
        for history, actual in zip(histories, scores.rows):
            expected = wn(history, [], [10.0] * 6)
            self.assertEqual(actual, expected)
        self.assertAlmostEqual(scores.rows[0][3], 4.0)
        self.assertAlmostEqual(scores.rows[0][1], 9.5)
        self.assertAlmostEqual(scores.rows[1][3], 8.25)
        self.assertEqual(scores.rows[0][4:], [10.0, 10.0])

    def test_global_only_rules_need_no_prefix_and_cover_low_logit_tokens(self):
        document = rules_document()
        document["parameters"]["max_ngram"] = 1
        document["prefix_scores"] = {}
        scores = BatchScores([[100.0, 10.0, 5.0, -100.0]])
        processor = TransformersInverseWatermarkProcessor(RuleTable(document), 2.0)
        processor([[]], scores)
        self.assertEqual(scores.rows[0], [100.0, 10.0, 5.0, -101.4])

    def test_shape_and_vocabulary_mismatch_fail_before_mutation(self):
        processor = TransformersInverseWatermarkProcessor(RuleTable(rules_document()))
        for histories, scores in (([[1]], [1.0, 2.0]),
                                  ([[1]], BatchScores([[1.0] * 3])),
                                  ([[1], [2]], BatchScores([[1.0] * 4]))):
            with self.subTest(histories=histories), self.assertRaises(ValueError):
                processor(histories, scores)

    def test_zero_strength_is_exact_no_op_and_invalid_strength_is_rejected(self):
        scores = BatchScores([[1.0, 2.0, 3.0, 4.0]])
        processor = TransformersInverseWatermarkProcessor(RuleTable(rules_document()), 0)
        self.assertIs(processor([[1, 2]], scores), scores)
        self.assertEqual(scores.rows[0], [1.0, 2.0, 3.0, 4.0])
        for strength in (-1, float("nan"), float("inf")):
            with self.subTest(strength=strength), self.assertRaises(ValueError):
                TransformersInverseWatermarkProcessor(RuleTable(rules_document()), strength)


if __name__ == "__main__":
    unittest.main()
