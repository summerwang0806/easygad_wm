"""Backup approximate Qwen-rule -> Dipper-token projection for the old TP.

The paper did not publish its Dipper TP implementation. This bridge scores
the changed reference-token suffix after decoding a candidate continuation,
including tokens revised by boundary re-tokenization. It averages D over that
suffix. A finite candidate set and decoder-context suffix are recorded project
approximations; zero limits request all ordinary tokens / full decoder history.
No reference model is loaded, queried, or initialized by this module.
"""

from __future__ import annotations

import math


class TextProjection:
    def __init__(self, decoder_tokenizer, rule_tokenizer, rules, *, context_tokens: int = 64):
        if type(context_tokens) is not int or context_tokens < 0:
            raise ValueError("projection context tokens must be a nonnegative integer")
        self.decoder_tokenizer = decoder_tokenizer
        self.rule_tokenizer = rule_tokenizer
        self.rules = rules
        self.context_tokens = context_tokens
        self.special_ids = frozenset(decoder_tokenizer.all_special_ids)
        self.valid_ids = frozenset(int(value) for value in decoder_tokenizer.get_vocab().values())

    def project_candidates(self, decoder_ids: list[int], candidate_ids: list[int]) -> dict[int, float]:
        history = list(decoder_ids)
        if self.context_tokens:
            history = history[-self.context_tokens:]
        base_text = self.decoder_tokenizer.decode(
            history, skip_special_tokens=True, clean_up_tokenization_spaces=False)
        before = self.rule_tokenizer.encode(base_text, add_special_tokens=False)
        projected = {}
        for candidate in candidate_ids:
            if candidate in self.special_ids or candidate not in self.valid_ids:
                projected[candidate] = 0.0
                continue
            text = self.decoder_tokenizer.decode(
                [*history, candidate], skip_special_tokens=True, clean_up_tokenization_spaces=False)
            if text == base_text:
                projected[candidate] = 0.0
                continue
            after = self.rule_tokenizer.encode(text, add_special_tokens=False)
            common = 0
            for left, right in zip(before, after):
                if left != right:
                    break
                common += 1
            # An appended Dipper piece may replace the final Qwen token rather
            # than add a token. Include the entire changed suffix in that case.
            tail = after[common:]
            projected[candidate] = (
                sum(self.rules.confidence(after[:position], after[position])
                    for position in range(common, len(after))) / len(tail)
                if tail else 0.0)
        return projected

    def candidate_penalty(self, decoder_ids: list[int], candidate_id: int) -> float:
        return self.project_candidates(decoder_ids, [candidate_id])[candidate_id]


class TPTextProjectionProcessor:
    """Transformers-compatible callable; adjust scores before sampling warpers.

Only the highest-scoring ordinary candidate IDs are projected when top_k>0.
Other candidates retain their scores and may be sampled. This is a bounded
approximation, not a vocabulary-wide implementation of the paper formula.
"""

    def __init__(self, projection: TextProjection, *, strength: float = 2.5, candidate_top_k: int = 128):
        if not math.isfinite(strength) or strength < 0:
            raise ValueError("inverse strength must be finite and nonnegative")
        if type(candidate_top_k) is not int or candidate_top_k < 0:
            raise ValueError("candidate top-k must be a nonnegative integer")
        self.projection = projection
        self.strength = float(strength)
        self.candidate_top_k = candidate_top_k

    def __call__(self, input_ids, scores):
        if self.strength == 0:
            return scores
        for row in range(scores.shape[0]):
            if self.candidate_top_k:
                candidates = scores[row].topk(min(self.candidate_top_k, scores.shape[1])).indices.tolist()
            else:
                candidates = sorted(self.projection.valid_ids)
            candidates = [token for token in candidates
                          if token < scores.shape[1] and token not in self.projection.special_ids]
            values = self.projection.project_candidates(input_ids[row].tolist(), candidates)
            # Scalar indexing works with Transformers' score tensors without
            # introducing a torch dependency at module import / CPU preflight.
            for token, penalty in values.items():
                if penalty:
                    scores[row, token] -= self.strength * penalty
        return scores
