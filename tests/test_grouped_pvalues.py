"""Fixed-token evaluation checks; no CUDA, models or network required."""

import contextlib
import io
import json
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from wm_test import grouped_pvalues as grouped


ROOT = Path(__file__).resolve().parents[1]
CONFIG = {"gamma": 0.5, "hash_key": 15485863,
          "seeding": "simple_1 (hash_key * previous_token_id)"}


class FixedTokenGroupsTests(unittest.TestCase):
    def test_exact_blocks_skip_each_first_context_and_discard_tail(self):
        # The green flag at index 3 must NOT count in the second 3-token block.
        result = grouped.group_token_flags([0, 1, 0, 1, 1, 1, 1], 0.5, (3,))["3"]
        self.assertEqual(result["num_groups"], 2)
        self.assertEqual(result["discarded_tail_tokens"], 1)
        self.assertEqual([r["green_tokens"] for r in result["groups"]], [1, 2])
        self.assertEqual([r["num_tokens_scored"] for r in result["groups"]], [2, 2])
        self.assertEqual(result["groups"][0]["p_value"], 0.5)
        expected = 0.5 * math.erfc(1.0)
        self.assertAlmostEqual(result["groups"][1]["p_value"], expected)

    def test_upper_median_not_average_and_not_mean_of_answer_p(self):
        # Four blocks with 0, 1, 2 and 3 green scored tokens, respectively.
        flags = [0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 1, 1]
        result = grouped.group_token_flags(flags, 0.5, (4,))["4"]
        expected = 0.5 * math.erfc(((1 - 1.5) / math.sqrt(0.75)) / math.sqrt(2))
        self.assertAlmostEqual(result["median_p_value"], expected)
        self.assertGreater(result["median_p_value"], 0.5)

    def test_all_six_budgets_and_insufficient_groups(self):
        result = grouped.group_token_flags([0, 1] * 3100, 0.5)
        self.assertEqual(tuple(map(int, result)), grouped.TOKEN_BUDGETS)
        self.assertEqual(result["1000"]["num_groups"], 6)
        self.assertEqual(result["3000"]["num_groups"], 2)
        for budget in (10000, 20000, 30000):
            self.assertEqual(result[str(budget)]["status"], "insufficient_tokens")
            self.assertIsNone(result[str(budget)]["median_p_value"])

    def test_extreme_tail_preserves_nonzero_scientific_value(self):
        p, log_p = grouped.tail_probability(40.0)
        self.assertIsInstance(p, str)
        mantissa, exponent = p.split("e")
        self.assertEqual(int(exponent), -350)
        self.assertAlmostEqual(float(mantissa), 3.655893540915, places=9)
        self.assertAlmostEqual(log_p, -349.4370064593458, places=9)
        self.assertEqual(grouped.tail_probability(0), (0.5, math.log10(0.5)))
        self.assertEqual(grouped.tail_probability(-40), (1.0, 0.0))

    def test_report_contains_every_budget_and_both_labels(self):
        summary = grouped.summarize_grouped({
            "num_answers": 2, "total_answer_tokens": 1100,
            "budgets": grouped.group_token_flags([0, 1] * 550, 0.5),
        })
        out = io.StringIO()
        grouped.write_grouped_summary(out, {"kgw": summary, "clean": summary})
        text = out.getvalue()
        for budget in grouped.TOKEN_BUDGETS:
            self.assertIn(f"| {budget} | {budget - 1} |", text)
        self.assertIn("N/A", text)
        self.assertIn("clean median p", text)
        self.assertIn("上中位数", text)
        self.assertNotIn("groups", summary["budgets"]["1000"])


class ExactStreamTests(unittest.TestCase):
    def test_answer_encoding_has_no_separator_and_checks_saved_lengths(self):
        # Exercise the production encoding path without constructing a GPU scorer.
        scorer = object.__new__(grouped.ExactKGWScorer)

        class Tokenizer:
            def encode(self, answer, add_special_tokens):
                self.last_special = add_special_tokens
                return {"first": [1, 2], "second": [3, 4]}[answer]

        scorer.tokenizer = Tokenizer()
        # Empty context iteration is not sufficient to test cross-answer flags;
        # inject tensor/mask operations, retaining the real stream-building loop.
        scorer.vocab_size = 8
        scorer.device = "cuda"
        scorer.config = CONFIG

        class Mask:
            def __getitem__(self, tokens):
                class Membership:
                    def tolist(self):
                        return [int(token % 2 == 0) for token in tokens]
                return Membership()

        from collections import OrderedDict
        scorer.cache = OrderedDict({(8, 0.5, CONFIG["hash_key"], "cuda", prev): Mask()
                                    for prev in (1, 2, 3)})

        class Torch:
            @staticmethod
            def tensor(values, device):
                return values

        scorer.torch = Torch()
        rows = [{"id": "a", "answer": "first", "num_tokens": 2},
                {"id": "b", "answer": "second", "num_tokens": 2}]
        self.assertEqual(scorer.score(rows), [0, 1, 0, 1])
        self.assertFalse(scorer.tokenizer.last_special)
        rows[1]["num_tokens"] = 3
        with self.assertRaisesRegex(ValueError, "length mismatch"):
            scorer.score(rows)


class GroupedCacheTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix=".grouped-test-", dir=ROOT)
        if not Path(self.temp.name).resolve().is_relative_to(ROOT):
            raise AssertionError("Test cleanup path outside workspace")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.tokenizer = self.root / "tokenizer"
        self.tokenizer.mkdir()
        (self.tokenizer / "tokenizer.json").write_text("{}", encoding="utf-8")
        self.source = self.root / "answers.jsonl"
        self.source.write_text(json.dumps({"id": "a", "answer": "saved text"}) + "\n",
                               encoding="utf-8")

    def run_scoring(self):
        return grouped.load_grouped_pvalues(self.source, self.tokenizer, "cuda", CONFIG)

    def test_cache_reuse_and_invalidation_preserve_source(self):
        original = self.source.read_bytes()
        with patch.object(grouped, "ExactKGWScorer") as scorer:
            scorer.return_value.score.return_value = [0, 1] * 3100
            payload, cache = self.run_scoring()
            self.assertEqual(scorer.call_count, 1)
            self.assertEqual(cache.name, "answers.grouped_p_values.json")
            self.assertEqual(self.source.read_bytes(), original)
            self.assertEqual(self.run_scoring()[0], payload)
            self.assertEqual(scorer.call_count, 1)
            # Changes to the tokenizer and source independently invalidate cache.
            (self.tokenizer / "tokenizer.json").write_text('{"changed": true}', encoding="utf-8")
            self.run_scoring()
            self.assertEqual(scorer.call_count, 2)
            self.source.write_text(original.decode() + json.dumps({"id": "b", "answer": "more"}) + "\n",
                                   encoding="utf-8")
            self.run_scoring()
            self.assertEqual(scorer.call_count, 3)
            # A truncated/corrupt cache is recomputed, not silently accepted.
            cache.write_text("{", encoding="utf-8")
            self.run_scoring()
            self.assertEqual(scorer.call_count, 4)

    def test_valid_cache_can_be_read_without_cuda(self):
        with patch.object(grouped, "ExactKGWScorer") as scorer:
            scorer.return_value.score.return_value = [0, 1] * 600
            self.run_scoring()
        with patch.object(grouped, "ExactKGWScorer", side_effect=AssertionError("No CUDA")):
            payload, _ = grouped.load_grouped_pvalues(self.source, self.tokenizer, "cpu", CONFIG)
        self.assertEqual(payload["budgets"]["1000"]["num_groups"], 1)


if __name__ == "__main__":
    unittest.main()
