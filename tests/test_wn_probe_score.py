"""Semantic tests against the official dense local WaterProbe-v2 statistic."""

from itertools import combinations
import unittest

import numpy as np

from wn.probe_score import build_prefix_trie, extract_sample, score_distributions


def dense_min_ranks(probabilities):
    """Definition of scipy.stats.rankdata(..., method='min'), without SciPy."""
    return np.array([1 + np.count_nonzero(probabilities < value) for value in probabilities])


def dense_official_score(p1, p2, vocab_size, threshold=20, top_n=50):
    prepared = []
    for distributions in (p1, p2):
        current = {}
        for prefix, counts in distributions.items():
            dense = np.zeros(vocab_size, dtype=np.int64)
            for token, count in counts.items():
                dense[token] = count
            if dense.sum() >= threshold:
                current[prefix] = dense
        prepared.append(current)
    scores = []
    common = sorted(set(prepared[0]) & set(prepared[1]))
    nonzero = 0
    for a, b in combinations(common, 2):
        ds = (prepared[0][a], prepared[0][b], prepared[1][a], prepared[1][b])
        tops = [set(np.argsort(d)[::-1][:top_n]) for d in ds]
        support = sorted((tops[0] | tops[1]) & (tops[2] | tops[3]))
        if not support:
            continue
        ranks = [dense_min_ranks(d / d.sum()) for d in ds]
        first = np.sign(ranks[0][support] - ranks[1][support])
        second = np.sign(ranks[2][support] - ranks[3][support])
        norm1, norm2 = np.linalg.norm(first), np.linalg.norm(second)
        if norm1 == 0 and norm2 == 0:
            scores.append(1.0)
        elif norm1 == 0 or norm2 == 0:
            scores.append(0.0)
        else:
            scores.append(float(np.dot(first, second) / (norm1 * norm2)))
            nonzero += 1
    return float(np.mean(scores)), len(scores), len(common), nonzero


class BoundaryTokenizer:
    def __init__(self):
        self.calls = []

    def encode(self, text, add_special_tokens):
        self.calls.append((text, add_special_tokens))
        # Prefix encodings depend on the last line's tail, making a mistaken
        # isolated-prefix encoding observably different.
        return [ord(char) for char in text]


class ProbeScoreTests(unittest.TestCase):
    def test_official_prefix_set_and_boundary(self):
        tokenizer = BoundaryTokenizer()
        trie, maximum = build_prefix_trie(tokenizer, "header\nExample12:")
        self.assertEqual(len(tokenizer.calls), 1041)
        self.assertEqual(tokenizer.calls[0], ("Example12:", False))
        self.assertEqual(tokenizer.calls[1], ("Example12: A zero cat", False))
        self.assertTrue(all(not special for _, special in tokenizer.calls))
        self.assertEqual(maximum, len(" A three tiger"))
        for prefix in (" A zero cat", " Z nine lion"):
            sample = extract_sample([ord(char) for char in prefix] + [777], trie)
            self.assertEqual(sample, (prefix, 777))

    def test_requires_first_token_prefix_and_following_token(self):
        trie = {10: {20: {"_prefix": " A zero cat"}}}
        self.assertEqual(extract_sample([10, 20, 42, 99], trie), (" A zero cat", 42))
        self.assertIsNone(extract_sample([8, 10, 20, 42], trie))
        self.assertIsNone(extract_sample([10, 8, 20, 42], trie))
        self.assertIsNone(extract_sample([10, 20], trie))
        self.assertIsNone(extract_sample([], trie))

    def test_internal_node_is_not_accepted_as_leaf(self):
        trie = {10: {"_prefix": "short", 20: {"_prefix": "long"}}}
        self.assertIsNone(extract_sample([10, 42], trie))
        self.assertEqual(extract_sample([10, 20, 42], trie), ("long", 42))

    def test_matches_dense_reference_with_ties_zeros_and_filtered_prefix(self):
        p1 = {"a": {0: 5, 1: 5, 3: 1}, "b": {0: 2, 2: 4, 3: 5},
              "c": {1: 4, 2: 4, 4: 6}, "small": {0: 4}, "only_p1": {2: 10}}
        p2 = {"a": {0: 6, 2: 1, 3: 6}, "b": {1: 8, 2: 2, 3: 1},
              "c": {0: 2, 1: 3, 4: 10}, "small": {0: 9}}
        for vocab_size, top_n in ((8, 50), (8, 3), (80, 50)):
            with self.subTest(vocab_size=vocab_size, top_n=top_n):
                expected = dense_official_score(p1, p2, vocab_size, threshold=5, top_n=top_n)
                actual = score_distributions(p1, p2, vocab_size, threshold=5, top_n=top_n)
                self.assertAlmostEqual(actual["score"], expected[0], places=14)
                self.assertEqual(actual["pair_count"], expected[1])
                self.assertEqual(actual["common_prefix_count"], expected[2])
                self.assertEqual(actual["nonzero_pair_count"], expected[3])

    def test_random_sparse_distributions_match_dense_reference(self):
        rng = np.random.default_rng(924)
        for trial in range(12):
            distributions = []
            for _ in range(2):
                current = {}
                for prefix in ("a", "b", "c", "d"):
                    values = rng.integers(0, 8, size=65)
                    values[rng.random(65) < 0.65] = 0
                    current[prefix] = {int(i): int(values[i]) for i in np.flatnonzero(values)}
                distributions.append(current)
            expected = dense_official_score(*distributions, 65)
            actual = score_distributions(*distributions, 65)
            self.assertAlmostEqual(actual["score"], expected[0], places=14, msg=str(trial))

    def test_count_five_is_included_and_four_is_filtered(self):
        p1 = {"a": {0: 5}, "b": {1: 5}, "four": {2: 4}}
        p2 = {"a": {0: 5}, "b": {1: 5}, "four": {2: 5}}
        result = score_distributions(p1, p2, 8, threshold=5)
        self.assertEqual(result["common_prefix_count"], 2)
        self.assertEqual(result["pair_count"], 1)
        self.assertAlmostEqual(result["score"], 1.0)

    def test_zero_vectors_keep_official_semantics_when_other_pairs_are_valid(self):
        p1 = {"a": {0: 5}, "b": {0: 5}, "c": {1: 5}}
        p2 = {"a": {0: 5}, "b": {0: 5}, "c": {1: 5}}
        expected = dense_official_score(p1, p2, 6, threshold=5)
        result = score_distributions(p1, p2, 6, threshold=5)
        self.assertAlmostEqual(result["score"], expected[0])
        self.assertEqual(result["pair_count"], 3)
        self.assertEqual(result["nonzero_pair_count"], 2)
        p2["b"] = {1: 5}
        expected = dense_official_score(p1, p2, 6, threshold=5)
        result = score_distributions(p1, p2, 6, threshold=5)
        self.assertAlmostEqual(result["score"], expected[0])
        self.assertEqual(result["nonzero_pair_count"], 1)

    def test_empty_or_zero_evidence_is_rejected(self):
        for p1, p2 in (({}, {}), ({"a": {0: 5}}, {"a": {0: 5}}),
                       ({"a": {0: 5}, "b": {0: 5}}, {"a": {0: 5}, "b": {0: 5}}),
                       ({"a": {0: 5}, "b": {0: 5}}, {"a": {0: 5}, "b": {1: 5}})):
            with self.subTest(p1=p1, p2=p2), self.assertRaises(ValueError):
                score_distributions(p1, p2, 6, threshold=5)

    def test_default_local_pipeline_threshold_is_twenty(self):
        p1 = {"a": {0: 20}, "b": {1: 20}, "nineteen": {2: 19}}
        p2 = {"a": {0: 20}, "b": {1: 20}, "nineteen": {2: 20}}
        result = score_distributions(p1, p2, 8)
        self.assertEqual(result["common_prefix_count"], 2)
        self.assertEqual(result["pair_count"], 1)

    def test_invalid_inputs_are_rejected(self):
        for counts in ({8: 5}, {-1: 5}, {1: -2}, {1: 2.5}):
            with self.subTest(counts=counts), self.assertRaises(ValueError):
                score_distributions({"a": counts}, {}, 8)
        for kwargs in ({"vocab_size": 0}, {"vocab_size": 8, "top_n": 0},
                       {"vocab_size": 8, "threshold": 0}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                score_distributions({}, {}, **kwargs)


if __name__ == "__main__":
    unittest.main()
