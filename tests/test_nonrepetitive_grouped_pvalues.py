"""Quality-filtered fixed-token evaluation checks; no models or CUDA needed."""

import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from wm_test import nonrepetitive_grouped_pvalues as filtered
from wm_test import grouped_pvalues as grouped


ROOT = Path(__file__).resolve().parents[1]
CONFIG = {"gamma": 0.5, "hash_key": 15485863,
          "seeding": "simple_1 (hash_key * previous_token_id)"}


def answer_row(sample_id, tokens, prompt="ignored prompt"):
    return {"id": sample_id, "answer": " ".join(map(str, tokens)),
            "prompt": prompt, "num_tokens": len(tokens)}


class Tokenizer:
    def __init__(self):
        self.calls = []

    def encode(self, text, add_special_tokens):
        self.calls.append((text, add_special_tokens))
        return [int(token) for token in text.split()]


class FakeScorer:
    """Retain stream-building behavior, replace only green-list membership."""

    def __init__(self, *_args):
        self.tokenizer = Tokenizer()
        self.scored_rows = None

    def score(self, rows):
        self.scored_rows = rows
        tokens = [token for row in rows for token in self.tokenizer.encode(
            row["answer"], add_special_tokens=False)]
        return ([0] + [(previous + current) % 2
                       for previous, current in zip(tokens, tokens[1:])]
                if tokens else [])


class SevereRepetitionFilteringTests(unittest.TestCase):
    def test_strict_threshold_keeps_equal_half_and_removes_above_half(self):
        tokenizer = Tokenizer()
        equal = answer_row("equal", [1, 2, 1, 2, 1])
        above = answer_row("above", [1, 2, 1, 2, 1, 2])
        retained, info = filtered.filter_severely_repetitive_answers(
            [equal, above], tokenizer)
        self.assertEqual(retained, [equal])
        self.assertEqual(info["num_answers_before"], 2)
        self.assertEqual(info["num_answers_retained"], 1)
        self.assertEqual(info["num_answers_removed"], 1)
        self.assertEqual(info["removed_answer_ids"], ["above"])
        self.assertEqual(info["fraction_answers_removed"], 0.5)
        self.assertEqual(info["total_answer_tokens_before"], 11)
        self.assertEqual(info["total_answer_tokens_retained"], 5)
        self.assertEqual(info["total_answer_tokens_removed"], 6)
        self.assertEqual(info["per_answer"][0], {
            "id": "equal", "num_tokens": 5, "num_pairs": 4,
            "num_unique_pairs": 2, "repetition_ratio": 0.5, "excluded": False,
        })
        self.assertEqual(info["per_answer"][1]["repetition_ratio"], 0.6)
        self.assertTrue(info["per_answer"][1]["excluded"])
        self.assertTrue(all(special is False for _, special in tokenizer.calls))

    def test_prompt_is_never_encoded_or_used_for_repetition(self):
        tokenizer = Tokenizer()
        # A non-numeric prompt would fail our tokenizer if the prompt leaked in.
        row = answer_row("a", [1, 2, 3, 4], prompt="repeat repeat " * 1000)
        retained, info = filtered.filter_severely_repetitive_answers([row], tokenizer)
        self.assertEqual(retained, [row])
        self.assertEqual(tokenizer.calls, [(row["answer"], False)])
        self.assertEqual(info["per_answer"][0]["repetition_ratio"], 0)

    def test_empty_and_single_token_answers_have_zero_repetition(self):
        rows = [answer_row("empty", []), answer_row("single", [8])]
        retained, info = filtered.filter_severely_repetitive_answers(rows, Tokenizer())
        self.assertEqual(retained, rows)
        self.assertEqual(info["num_answers_removed"], 0)
        for item in info["per_answer"]:
            self.assertEqual(item["num_pairs"], 0)
            self.assertEqual(item["repetition_ratio"], 0)
            self.assertFalse(item["excluded"])

    def test_saved_token_count_mismatch_rejects_even_a_removed_answer(self):
        row = answer_row("broken", [1] * 10)
        row["num_tokens"] = 9
        with self.assertRaisesRegex(ValueError, "length mismatch.*broken"):
            filtered.filter_severely_repetitive_answers([row], Tokenizer())

    def test_invalid_or_duplicate_ids_are_rejected(self):
        for rows in ([answer_row("", [1])], [answer_row(2, [1])],
                     [answer_row("a", [1]), answer_row("a", [2])]):
            with self.subTest(rows=rows), self.assertRaisesRegex(ValueError, "answer id"):
                filtered.filter_severely_repetitive_answers(rows, Tokenizer())


class NonrepetitiveCacheTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix=".nonrepetitive-test-", dir=ROOT)
        if not Path(self.temp.name).resolve().is_relative_to(ROOT):
            raise AssertionError("Test cleanup path outside workspace")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.tokenizer = self.root / "tokenizer"
        self.tokenizer.mkdir()
        (self.tokenizer / "tokenizer.json").write_text("{}", encoding="utf-8")
        self.source = self.root / "answers.jsonl"
        self.rows = [answer_row("first", list(range(601))),
                     answer_row("repeat", [9] * 100),
                     answer_row("last", list(range(700, 1301)))]
        self.write_rows(self.rows)

    def write_rows(self, rows):
        self.source.write_text("".join(json.dumps(row) + "\n" for row in rows),
                               encoding="utf-8")

    def run_scoring(self, device="cuda", config=None):
        with contextlib.redirect_stdout(io.StringIO()):
            return filtered.load_nonrepetitive_grouped_pvalues(
                self.source, self.tokenizer, device, config or CONFIG)

    def test_filter_retains_order_and_rebuilds_cross_answer_contexts(self):
        scorer = FakeScorer()
        with patch.object(filtered, "ExactKGWScorer", return_value=scorer):
            payload, cache = self.run_scoring()
        expected_rows = [self.rows[0], self.rows[2]]
        self.assertEqual(scorer.scored_rows, expected_rows)
        self.assertEqual(payload["num_answers"], 2)
        self.assertEqual(payload["total_answer_tokens"], 1202)
        self.assertEqual(payload["filtering"]["removed_answer_ids"], ["repeat"])
        expected_flags = FakeScorer().score(expected_rows)
        self.assertEqual(payload["budgets"], grouped.group_token_flags(expected_flags, 0.5))
        self.assertEqual(cache.name, "answers.nonrepetitive_grouped_p_values.json")
        signature = payload["signature"]
        self.assertEqual(signature["token_budgets"], list(grouped.TOKEN_BUDGETS))
        self.assertEqual(signature["severe_repetition_threshold"], 0.5)
        self.assertEqual(signature["schema"], filtered.SCHEMA)
        self.assertEqual(signature["detector"], CONFIG)

    def test_cache_reuse_is_cpu_safe_and_preserves_source_and_raw_caches(self):
        source_before = self.source.read_bytes()
        raw_files = [self.source.with_suffix(".grouped_p_values.json"),
                     self.source.with_suffix(".p_values.jsonl")]
        for path in raw_files:
            path.write_bytes(b"legacy raw evaluation must remain unchanged\n")
        originals = {path: path.read_bytes() for path in raw_files}
        with patch.object(filtered, "ExactKGWScorer", side_effect=FakeScorer) as factory:
            payload, _ = self.run_scoring()
            self.assertEqual(factory.call_count, 1)
        with patch.object(filtered, "ExactKGWScorer", side_effect=AssertionError("No CUDA")):
            self.assertEqual(self.run_scoring(device="cpu")[0], payload)
        self.assertEqual(self.source.read_bytes(), source_before)
        self.assertEqual({path: path.read_bytes() for path in raw_files}, originals)

    def test_source_tokenizer_detector_and_threshold_changes_invalidate_cache(self):
        with patch.object(filtered, "ExactKGWScorer", side_effect=FakeScorer) as factory:
            self.run_scoring()
            self.run_scoring()
            self.assertEqual(factory.call_count, 1)
            (self.tokenizer / "tokenizer.json").write_text('{"changed": true}', encoding="utf-8")
            self.run_scoring()
            self.assertEqual(factory.call_count, 2)
            self.write_rows(self.rows + [answer_row("new", [3, 8])])
            self.run_scoring()
            self.assertEqual(factory.call_count, 3)
            self.run_scoring(config={**CONFIG, "gamma": 0.25})
            self.assertEqual(factory.call_count, 4)
            self.run_scoring()
            self.assertEqual(factory.call_count, 5)
            with patch.object(filtered, "SEVERE_REPETITION_THRESHOLD", 0.6):
                self.run_scoring()
            self.assertEqual(factory.call_count, 6)

    def test_corrupt_or_incomplete_cache_is_rebuilt(self):
        with patch.object(filtered, "ExactKGWScorer", side_effect=FakeScorer) as factory:
            payload, cache = self.run_scoring()
            for damaged in ("{", "null", "[]", '"scalar"'):
                cache.write_text(damaged, encoding="utf-8")
                self.run_scoring()
            payload["budgets"].pop("1000")
            cache.write_text(json.dumps(payload), encoding="utf-8")
            self.run_scoring()
            self.assertEqual(factory.call_count, 6)

    def test_all_excluded_needs_no_scoring_and_reports_six_insufficient_budgets(self):
        self.write_rows([answer_row("repeat", [7] * 100)])
        scorer = FakeScorer()
        with patch.object(filtered, "ExactKGWScorer", return_value=scorer), \
                patch.object(scorer, "score", side_effect=AssertionError("No scoring needed")):
            payload, _ = self.run_scoring()
        self.assertEqual(payload["num_answers"], 0)
        self.assertEqual(payload["total_answer_tokens"], 0)
        self.assertEqual(payload["filtering"]["num_answers_removed"], 1)
        self.assertEqual(tuple(map(int, payload["budgets"])), grouped.TOKEN_BUDGETS)
        for summary in payload["budgets"].values():
            self.assertEqual(summary["status"], "insufficient_tokens")
            self.assertEqual(summary["num_groups"], 0)
            self.assertIsNone(summary["median_p_value"])

    def test_scored_stream_length_mismatch_does_not_write_cache(self):
        scorer = FakeScorer()
        with patch.object(filtered, "ExactKGWScorer", return_value=scorer), \
                patch.object(scorer, "score", return_value=[]):
            with self.assertRaisesRegex(ValueError, "stream length"):
                self.run_scoring()
        self.assertFalse(self.source.with_suffix(".nonrepetitive_grouped_p_values.json").exists())

    def test_report_keeps_filtering_totals_and_both_labels_without_large_details(self):
        with patch.object(filtered, "ExactKGWScorer", side_effect=FakeScorer):
            payload, _ = self.run_scoring()
        summary = filtered.summarize_nonrepetitive_grouped(payload)
        self.assertNotIn("per_answer", summary["filtering"])
        self.assertEqual(summary["filtering"]["removed_answer_ids"], ["repeat"])
        self.assertEqual(summary["aggregation"], "ordinary_median")
        self.assertNotIn("groups", summary["budgets"]["1000"])
        out = io.StringIO()
        filtered.write_nonrepetitive_grouped_summary(out, {"kgw": summary, "clean": summary})
        report = out.getvalue()
        for budget in grouped.TOKEN_BUDGETS:
            self.assertIn(f"| {budget} | {budget - 1} |", report)
        for label in ("kgw", "clean"):
            self.assertIn(f"| {label} | 3 | 1 (33.33%) | 2 | 1302 | 100 | 1202 |", report)
        self.assertIn("N/A", report)
        self.assertIn("普通中位数", report)
        self.assertIn("剔除整条回答", report)
        self.assertIn("不做 token 对去重", report)


if __name__ == "__main__":
    unittest.main()
