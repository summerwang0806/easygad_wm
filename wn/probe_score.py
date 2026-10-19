# Copyright 2024 THU BPM
# Copyright 2026 contributors to this reproduction
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy at http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
"""Local WaterProbe-v2 prefix parsing and cosine score.

Adapted from THU-BPM/Watermarked_LLM_Identification at commit
f946e4d93d6f3e8e308e86d6c6cd95170792a70b:
  scripts/gen_logits.py, scripts/utils/generation_utils.py,
  scripts/samplers/base_sampler.py, and scripts/experiment.py.

The only failure guards added here reject an empty statistic or an entirely
zero-vector statistic, rather than returning a misleading strength estimate.
"""

from itertools import combinations, product
import math
from numbers import Integral
from typing import Any

import numpy as np


def build_prefix_trie(tokenizer: Any, prompt: str) -> tuple[dict, int]:
    """Encode the official 1040 ngram prefixes with the official boundary rule."""
    post_prompt = prompt.rsplit("\n", 1)[-1]
    post_ids = tokenizer.encode(post_prompt, add_special_tokens=False)
    trie: dict = {}
    max_prefix_tokens = 0
    for letter, number, animal in product(
        (f" {chr(code)}" for code in range(65, 91)),
        (f" {number}" for number in (
            "zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"
        )),
        (" cat", " dog", " tiger", " lion"),
    ):
        prefix = letter + number + animal
        prefix_ids = tokenizer.encode(post_prompt + prefix, add_special_tokens=False)[len(post_ids):]
        if not prefix_ids:
            raise ValueError("Tokenizer produced an empty official probe prefix")
        node = trie
        for token_id in prefix_ids:
            node = node.setdefault(int(token_id), {})
        previous = node.get("_prefix")
        if previous is not None and previous != prefix:
            raise ValueError("Tokenizer maps distinct official probe prefixes to the same token sequence")
        node["_prefix"] = prefix
        max_prefix_tokens = max(max_prefix_tokens, len(prefix_ids))
    return trie, max_prefix_tokens


def extract_sample(ids: Any, trie: dict) -> tuple[str, int] | None:
    """Accept only a complete trie prefix from the first generated token.

    As in the official free sampler, a token that leaves an internal node is
    invalid; a token sampled after a leaf is the measured continuation token.
    """
    node = trie
    for token_id in ids:
        token_id = int(token_id)
        if "_prefix" in node and not any(isinstance(key, int) for key in node):
            return node["_prefix"], token_id
        if token_id not in node:
            return None
        node = node[token_id]
    return None


def _prepare_distribution(counts: dict[int, int], vocab_size: int, top_n: int) -> dict:
    dense = np.zeros(vocab_size, dtype=np.int64)
    for token_id, count in counts.items():
        if not isinstance(token_id, Integral) or not 0 <= token_id < vocab_size:
            raise ValueError(f"Token id outside probe vocabulary: {token_id!r}")
        if not isinstance(count, Integral) or count < 0:
            raise ValueError(f"Invalid probe count: {count!r}")
        dense[int(token_id)] = int(count)
    total = int(dense.sum())
    # np.argsort on the full count vector deliberately preserves the official
    # top50 selection, including NumPy's ordering among zero-count ties.
    top = set(np.argsort(dense)[::-1][:top_n].tolist())
    positive = dense[dense > 0]
    values, frequencies = np.unique(positive, return_counts=True)
    rank_by_count = {}
    lower_count = vocab_size - len(positive)
    for value, frequency in zip(values.tolist(), frequencies.tolist()):
        rank_by_count[value] = lower_count + 1
        lower_count += frequency
    # The all-vocabulary min rank of an unseen token is 1. Positive ranks can
    # be cached sparsely because zero-count tokens share that same rank.
    ranks = {int(token): rank_by_count[int(dense[token])] for token in np.flatnonzero(dense)}
    return {"total": total, "top": top, "ranks": ranks}


def score_distributions(
    p1: dict[str, dict[int, int]],
    p2: dict[str, dict[int, int]],
    vocab_size: int,
    threshold: float = 20,
    top_n: int = 50,
) -> dict:
    """Compute the official local WaterProbe-v2 mean prefix-pair cosine.

    Counts are normalized independently in the upstream implementation. That
    normalization is monotone, so ranks of integer counts are identical and
    can be precomputed without storing a dense rank vector per prefix.
    """
    if not isinstance(vocab_size, Integral) or vocab_size <= 0:
        raise ValueError("vocab_size must be a positive integer")
    if not isinstance(top_n, Integral) or top_n <= 0:
        raise ValueError("top_n must be a positive integer")
    if not math.isfinite(threshold) or threshold <= 0:
        raise ValueError("threshold must be positive and finite")
    prepared = []
    for distributions in (p1, p2):
        current = {}
        for prefix, counts in distributions.items():
            distribution = _prepare_distribution(counts, vocab_size, top_n)
            if distribution["total"] >= threshold:
                current[prefix] = distribution
        prepared.append(current)
    common = sorted(set(prepared[0]).intersection(prepared[1]))
    similarities = []
    nonzero_pair_count = 0
    for prefix1, prefix2 in combinations(common, 2):
        d11, d12 = prepared[0][prefix1], prepared[0][prefix2]
        d21, d22 = prepared[1][prefix1], prepared[1][prefix2]
        support = (d11["top"] | d12["top"]) & (d21["top"] | d22["top"])
        if not support:
            continue
        dot = norm1 = norm2 = 0
        for token_id in support:
            difference1 = d11["ranks"].get(token_id, 1) - d12["ranks"].get(token_id, 1)
            difference2 = d21["ranks"].get(token_id, 1) - d22["ranks"].get(token_id, 1)
            sign1 = (difference1 > 0) - (difference1 < 0)
            sign2 = (difference2 > 0) - (difference2 < 0)
            dot += sign1 * sign2
            norm1 += sign1 * sign1
            norm2 += sign2 * sign2
        if norm1 == 0 and norm2 == 0:
            similarities.append(1.0)
        elif norm1 == 0 or norm2 == 0:
            similarities.append(0.0)
        else:
            similarities.append(dot / math.sqrt(norm1 * norm2))
            nonzero_pair_count += 1
    if not similarities:
        raise ValueError("No usable prefix pairs; collect more valid probe samples")
    if nonzero_pair_count == 0:
        raise ValueError("All probe pairs have zero rank-difference vectors; no usable probe evidence")
    return {
        "score": float(np.mean(similarities)),
        "pair_count": len(similarities),
        "common_prefix_count": len(common),
        "nonzero_pair_count": nonzero_pair_count,
    }
