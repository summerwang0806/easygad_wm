"""Minimal canonical KGW (Kirchenbauer et al.) watermark for vLLM.

The implementation uses the ``simple_1`` seeding scheme: the previous token and
a secret integer key seed a PRNG, a fraction ``gamma`` of the tokenizer
vocabulary becomes the green list, and ``delta`` is added to those logits.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import torch


@dataclass(frozen=True)
class KGWConfig:
    gamma: float = 0.25
    delta: float = 2.0
    hash_key: int = 15_485_863

    def validate(self) -> None:
        if not 0.0 < self.gamma < 1.0:
            raise ValueError(f"gamma must be in (0, 1), got {self.gamma}")
        if self.delta <= 0.0:
            raise ValueError(f"delta must be positive, got {self.delta}")
        if self.hash_key <= 0:
            raise ValueError("hash_key must be a positive integer")


class KGWLogitsProcessor:
    """vLLM-compatible KGW logits processor.

    The three-argument call signature is intentional: vLLM then supplies both
    prompt token IDs and already generated token IDs. This lets the first output
    token use the final prompt token as its KGW context.
    """

    def __init__(self, vocab_size: int, config: KGWConfig):
        config.validate()
        if vocab_size <= 1:
            raise ValueError(f"vocab_size must be > 1, got {vocab_size}")
        self.vocab_size = int(vocab_size)
        self.gamma = float(config.gamma)
        self.delta = float(config.delta)
        self.hash_key = int(config.hash_key)
        self.greenlist_size = max(1, int(self.vocab_size * self.gamma))


# 种子怎么来的
    def _seed(self, previous_token_id: int) -> int:
        # torch.Generator.manual_seed accepts signed 64-bit-compatible values.
        return (self.hash_key * int(previous_token_id)) % (2**63 - 1)

    def _greenlist(self, previous_token_id: int, device: torch.device) -> torch.Tensor:
        generator = torch.Generator(device=device)
        generator.manual_seed(self._seed(previous_token_id))
        return torch.randperm(
            self.vocab_size,
            device=device,
            generator=generator,
        )[: self.greenlist_size]

    def __call__(
        self,
        prompt_token_ids: list[int],
        generated_token_ids: list[int],
        logits: torch.Tensor,
    ) -> torch.Tensor:
        context = generated_token_ids if generated_token_ids else prompt_token_ids
        if not context:
            return logits
        green_ids = self._greenlist(context[-1], logits.device)
        logits[green_ids] += self.delta
        return logits


def kgw_score(
    prompt_token_ids: list[int],
    generated_token_ids: list[int],
    vocab_size: int,
    config: KGWConfig,
    max_tokens: int | None = None,
    device: str | torch.device | None = None,
) -> dict[str, float | int]:
    """Return green-token count, fraction, and one-sided KGW z-score."""

    processor = KGWLogitsProcessor(vocab_size=vocab_size, config=config)
    tokens = generated_token_ids[:max_tokens] if max_tokens else generated_token_ids
    if not tokens:
        return {"num_tokens": 0, "green_tokens": 0, "green_fraction": 0.0, "z_score": 0.0}

    # torch CPU and CUDA generators intentionally use different algorithms.
    # Detection must therefore reproduce the CUDA green lists used at generation.
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    else:
        device = torch.device(device)

    previous = prompt_token_ids[-1] if prompt_token_ids else tokens[0]
    green_count = 0
    for token_id in tokens:
        green_ids = processor._greenlist(previous, device)
        if bool((green_ids == int(token_id)).any()):
            green_count += 1
        previous = int(token_id)

    n = len(tokens)
    expected = config.gamma * n
    variance = n * config.gamma * (1.0 - config.gamma)
    z_score = (green_count - expected) / math.sqrt(variance)
    return {
        "num_tokens": n,
        "green_tokens": green_count,
        "green_fraction": green_count / n,
        "z_score": z_score,
    }
