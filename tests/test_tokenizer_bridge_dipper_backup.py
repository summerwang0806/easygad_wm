"""CPU checks of TP token projection, including rewritten token boundaries."""

import unittest
from types import SimpleNamespace

from baseline_acl.tokenizer_bridge_dipper_backup import TextProjection, TPTextProjectionProcessor


class Decoder:
    all_special_ids = [0]
    pieces = {0: "", 1: "a", 2: "b", 3: "xy", 4: "z"}

    def get_vocab(self):
        return {piece or "<eos>": token for token, piece in self.pieces.items()}

    def decode(self, ids, **kwargs):
        return "".join(self.pieces[token] for token in ids)


class Reference:
    def encode(self, text, **kwargs):
        # The ab merge replaces the existing final a token when b is appended.
        tokens, index = [], 0
        while index < len(text):
            if text[index:index + 2] == "ab":
                tokens.append(7)
                index += 2
            else:
                tokens.append({"a": 5, "b": 6, "x": 8, "y": 9, "z": 10}[text[index]])
                index += 1
        return tokens


class Rules:
    def confidence(self, prefix, token):
        if token == 7:
            return 0.8
        if token == 8:
            return 0.2
        if token == 9 and prefix and prefix[-1] == 8:
            return 0.6
        if token == 10:
            return 1.2  # Combined D may exceed one.
        return 0.0


class Row:
    def __init__(self, values):
        self.values = values

    def tolist(self):
        return list(self.values)

    def topk(self, count):
        ids = sorted(range(len(self.values)), key=lambda index: self.values[index], reverse=True)[:count]
        return SimpleNamespace(indices=Row(ids))


class Matrix:
    def __init__(self, values):
        self.values = [list(row) for row in values]
        self.shape = (len(self.values), len(self.values[0]))

    def __getitem__(self, key):
        if isinstance(key, tuple):
            return self.values[key[0]][key[1]]
        return Row(self.values[key])

    def __setitem__(self, key, value):
        self.values[key[0]][key[1]] = value


class ProjectionTests(unittest.TestCase):
    def setUp(self):
        self.projection = TextProjection(Decoder(), Reference(), Rules(), context_tokens=0)

    def test_boundary_retokenization_scores_replaced_token(self):
        self.assertAlmostEqual(self.projection.candidate_penalty([0, 1], 2), 0.8)

    def test_multi_reference_token_piece_uses_mean_with_each_context(self):
        self.assertAlmostEqual(self.projection.candidate_penalty([0], 3), 0.4)

    def test_special_and_unused_decoder_ids_have_no_penalty(self):
        self.assertEqual(self.projection.project_candidates([1], [0, 99]), {0: 0.0, 99: 0.0})

    def test_combined_d_is_not_clamped(self):
        self.assertEqual(self.projection.candidate_penalty([], 4), 1.2)

    def test_recorded_context_limit_is_explicit(self):
        limited = TextProjection(Decoder(), Reference(), Rules(), context_tokens=1)
        self.assertAlmostEqual(limited.candidate_penalty([4, 1], 2), 0.8)
        with self.assertRaises(ValueError):
            TextProjection(Decoder(), Reference(), Rules(), context_tokens=-1)

    def test_zero_strength_leaves_scores_and_skips_projection(self):
        class Forbidden:
            def project_candidates(self, *args):
                raise AssertionError("zero strength must not tokenize candidates")
        values = Matrix([[0, 1, 2, 3, 4]])
        self.assertIs(TPTextProjectionProcessor(Forbidden(), strength=0)(None, values), values)
        self.assertEqual(values.values, [[0, 1, 2, 3, 4]])

    def test_processor_penalizes_only_configured_candidate_set(self):
        values = Matrix([[1, 2, 9, 3, 4]])
        processor = TPTextProjectionProcessor(self.projection, strength=2, candidate_top_k=1)
        processor(Matrix([[0, 1]]), values)
        self.assertEqual(values.values, [[1, 2, 7.4, 3, 4]])

    def test_full_candidate_mode_handles_batch_and_preserves_special_ids(self):
        values = Matrix([[1, 2, 3, 4, 5], [1, 2, 3, 4, 5]])
        processor = TPTextProjectionProcessor(self.projection, strength=2, candidate_top_k=0)
        processor(Matrix([[0, 1], [0, 0]]), values)
        self.assertAlmostEqual(values[0, 2], 1.4)
        self.assertAlmostEqual(values[1, 3], 3.2)
        self.assertAlmostEqual(values[0, 4], 2.6)
        self.assertEqual(values[0, 0], 1)

    def test_invalid_settings_fail(self):
        for kwargs in ({"strength": -1}, {"strength": float("nan")}, {"candidate_top_k": -1}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                TPTextProjectionProcessor(self.projection, **kwargs)


if __name__ == "__main__":
    unittest.main()
