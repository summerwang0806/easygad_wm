#!/usr/bin/env python3
"""Step 4: Extract 8,192-dim projected probe gradients for reference bank & clean pool.

Uses exact gradient accumulation over all valid responses in each file (strictly
equivalent to per-sample projection + averaging because random projection is linear):
  g(x, y) = grad_{theta_probe} log p(y | x)   (prompt tokens masked with -100)
  z = Project(mean_g) in R^{8192}

All sources (bank keys, clean pool cells, suspects) call the exact same helper
`extract_projected_gradient` so tokenization, truncation, weighting, and projection
are 100% consistent.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from wm_basin.core import (
    BlockRademacherProjector,
    DEFAULT_MAX_RESPONSE_TOKENS,
    DEFAULT_MIN_RESPONSE_TOKENS,
    DEFAULT_PROJ_DIM,
    DEFAULT_PROJ_SEED,
    read_json,
    read_jsonl,
    render_prompt_with_fallback,
    write_json,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Extract projected LoRA gradients using the frozen probe")
    p.add_argument("--work-dir", type=Path, default=Path("wm_basin_work"))
    p.add_argument("--target", choices=["bank", "clean_pool", "both"], default="both")
    p.add_argument("--max-bank-samples", type=int, default=512, help="Max valid responses per key (paper=512)")
    p.add_argument("--max-pca-samples", type=int, default=512, help="Max valid responses per clean cell")
    p.add_argument("--max-prompt-tokens", type=int, default=2048)
    p.add_argument("--max-response-tokens", type=int, default=DEFAULT_MAX_RESPONSE_TOKENS)
    p.add_argument("--min-response-tokens", type=int, default=DEFAULT_MIN_RESPONSE_TOKENS)
    p.add_argument("--batch-size", type=int, default=4, help="Forward/backward micro-batch size on probe GPU")
    p.add_argument("--weighting", choices=["token", "sample"], default="token")
    p.add_argument("--proj-dim", type=int, default=DEFAULT_PROJ_DIM)
    p.add_argument("--proj-seed", type=int, default=DEFAULT_PROJ_SEED)
    p.add_argument("--block-size", type=int, default=65536)
    p.add_argument("--overwrite", action="store_true")
    return p.parse_args()


def load_frozen_probe(work_dir: Path):
    """Load base probe + warmed LoRA adapter in eval mode with only LoRA params trainable."""
    import torch
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer

    meta = read_json(work_dir / "probe" / "probe_meta.json")
    probe_model_path = meta["probe_model"]
    adapter_dir = work_dir / "probe" / "adapter"

    tokenizer = AutoTokenizer.from_pretrained(probe_model_path, trust_remote_code=True)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32
    base_model = AutoModelForCausalLM.from_pretrained(
        probe_model_path,
        torch_dtype=dtype,
        trust_remote_code=True,
    ).to(device)
    model = PeftModel.from_pretrained(base_model, str(adapter_dir), is_trainable=True)
    model.eval()  # disable dropout for deterministic gradients

    lora_params = [
        p for name, p in sorted(model.named_parameters(), key=lambda x: x[0]) if p.requires_grad
    ]
    if not lora_params:
        raise RuntimeError("No trainable LoRA parameters found in loaded probe!")
    return model, tokenizer, lora_params, meta


def prepare_encoded_samples(
    tokenizer,
    rows: list[dict[str, Any]],
    max_prompt_tokens: int,
    max_response_tokens: int,
    min_response_tokens: int,
    max_samples: int | None = None,
) -> list[tuple[list[int], list[int], int]]:
    encoded: list[tuple[list[int], list[int], int]] = []
    for r in rows:
        prompt_str = render_prompt_with_fallback(tokenizer, r["messages"], max_prompt_tokens=max_prompt_tokens)
        prompt_ids = tokenizer.encode(prompt_str, add_special_tokens=False)
        resp_ids = tokenizer.encode(r["response"], add_special_tokens=False)[:max_response_tokens]
        if len(resp_ids) < min_response_tokens:
            continue
        input_ids = prompt_ids + resp_ids
        labels = [-100] * len(prompt_ids) + list(resp_ids)
        encoded.append((input_ids, labels, len(resp_ids)))
        if max_samples is not None and len(encoded) >= max_samples:
            break
    return encoded


def extract_projected_gradient(
    model,
    tokenizer,
    lora_params: list,
    rows: list[dict[str, Any]],
    projector: BlockRademacherProjector,
    max_prompt_tokens: int = 2048,
    max_response_tokens: int = DEFAULT_MAX_RESPONSE_TOKENS,
    min_response_tokens: int = DEFAULT_MIN_RESPONSE_TOKENS,
    max_samples: int | None = None,
    batch_size: int = 4,
    weighting: str = "token",
    show_progress: bool = True,
    desc: str = "extract_grad",
) -> tuple[np.ndarray, dict[str, int]]:
    """Accumulate mean log-prob gradient wrt LoRA params and project to proj_dim."""
    import torch
    import torch.nn.functional as F
    from tqdm import tqdm

    encoded = prepare_encoded_samples(
        tokenizer,
        rows,
        max_prompt_tokens=max_prompt_tokens,
        max_response_tokens=max_response_tokens,
        min_response_tokens=min_response_tokens,
        max_samples=max_samples,
    )
    if not encoded:
        raise RuntimeError("No valid responses remained after min_response_tokens filtering")

    device = next(model.parameters()).device
    pad_id = tokenizer.pad_token_id if tokenizer.pad_token_id is not None else 0

    for p in lora_params:
        p.grad = None

    # Sort by length to minimize padding waste during micro-batching
    encoded.sort(key=lambda item: len(item[0]))
    total_tokens = sum(item[2] for item in encoded)
    num_samples = len(encoded)

    # Accumulate in fp32 on device for numerical stability across many micro-batches
    grad_accum = [torch.zeros_like(p, dtype=torch.float32, device=device) for p in lora_params]

    starts = range(0, num_samples, batch_size)
    if show_progress:
        starts = tqdm(starts, total=(num_samples + batch_size - 1) // batch_size, desc=desc, unit="batch")

    for start in starts:
        batch = encoded[start : start + batch_size]
        max_len = max(len(item[0]) for item in batch)
        bs = len(batch)
        inp = torch.full((bs, max_len), pad_id, dtype=torch.long, device=device)
        attn = torch.zeros((bs, max_len), dtype=torch.long, device=device)
        lbl = torch.full((bs, max_len), -100, dtype=torch.long, device=device)
        for i, (ids, labs, _) in enumerate(batch):
            L = len(ids)
            inp[i, :L] = torch.tensor(ids, dtype=torch.long, device=device)
            attn[i, :L] = 1
            lbl[i, :L] = torch.tensor(labs, dtype=torch.long, device=device)

        outputs = model(input_ids=inp, attention_mask=attn, use_cache=False)
        shift_logits = outputs.logits[:, :-1, :].contiguous()
        shift_labels = lbl[:, 1:].contiguous()

        if weighting == "token":
            # Positive log-prob sum divided by total scored tokens across the entire collection
            nll_sum = F.cross_entropy(
                shift_logits.view(-1, shift_logits.size(-1)),
                shift_labels.view(-1),
                ignore_index=-100,
                reduction="sum",
            )
            objective = -nll_sum / float(total_tokens)
        else:
            # Mean of per-sample average log-prob
            per_tok_nll = F.cross_entropy(
                shift_logits.view(-1, shift_logits.size(-1)),
                shift_labels.view(-1),
                ignore_index=-100,
                reduction="none",
            ).view(bs, -1)
            mask = (shift_labels != -100).to(per_tok_nll.dtype)
            per_sample_mean_nll = (per_tok_nll * mask).sum(dim=1) / mask.sum(dim=1).clamp(min=1.0)
            objective = -per_sample_mean_nll.sum() / float(num_samples)

        objective.backward()
        for acc, p in zip(grad_accum, lora_params):
            if p.grad is not None:
                acc.add_(p.grad.detach().to(torch.float32))
                p.grad = None

    flat = torch.cat([g.reshape(-1) for g in grad_accum], dim=0)
    projected = projector.project_torch(flat)
    stats = {
        "num_input_rows": len(rows),
        "num_used_samples": num_samples,
        "total_scored_tokens": int(total_tokens),
        "grad_dim": int(flat.numel()),
    }
    return projected, stats


def process_directory(
    in_dir: Path,
    out_dir: Path,
    pattern: str,
    max_samples: int | None,
    model,
    tokenizer,
    lora_params: list,
    projector: BlockRademacherProjector,
    args: argparse.Namespace,
) -> None:
    files = sorted(in_dir.glob(pattern))
    if not files:
        print(f"[grads] No files matching {pattern} in {in_dir}")
        return
    out_dir.mkdir(parents=True, exist_ok=True)

    done = 0
    for idx, fp in enumerate(files, 1):
        out_npy = out_dir / f"{fp.stem}.npy"
        if out_npy.exists() and not args.overwrite:
            continue
        t0 = time.time()
        rows = read_jsonl(fp)
        vec, stats = extract_projected_gradient(
            model=model,
            tokenizer=tokenizer,
            lora_params=lora_params,
            rows=rows,
            projector=projector,
            max_prompt_tokens=args.max_prompt_tokens,
            max_response_tokens=args.max_response_tokens,
            min_response_tokens=args.min_response_tokens,
            max_samples=max_samples,
            batch_size=args.batch_size,
            weighting=args.weighting,
            show_progress=True,
            desc=f"{fp.stem}",
        )
        np.save(out_npy, vec)
        write_json(out_dir / f"{fp.stem}.meta.json", stats)
        done += 1
        print(
            f"[grads] ({idx}/{len(files)}) {fp.stem}: "
            f"used={stats['num_used_samples']}, tokens={stats['total_scored_tokens']:,}, "
            f"norm={float(np.linalg.norm(vec)):.4f} ({time.time() - t0:.1f}s)",
            flush=True,
        )
    print(f"[grads] Finished {in_dir.name}: newly computed {done}/{len(files)} vectors.")


def main() -> None:
    args = parse_args()
    model, tokenizer, lora_params, probe_meta = load_frozen_probe(args.work_dir)
    projector = BlockRademacherProjector(
        proj_dim=args.proj_dim,
        seed=args.proj_seed,
        block_size=args.block_size,
    )

    write_json(
        args.work_dir / "grads" / "projector_meta.json",
        {
            "proj_dim": args.proj_dim,
            "proj_seed": args.proj_seed,
            "block_size": args.block_size,
            "weighting": args.weighting,
            "max_response_tokens": args.max_response_tokens,
            "min_response_tokens": args.min_response_tokens,
            "probe_model": probe_meta["probe_model"],
            "trainable_params": probe_meta["trainable_params"],
        },
    )

    if args.target in ("bank", "both"):
        process_directory(
            in_dir=args.work_dir / "teacher_bank",
            out_dir=args.work_dir / "grads" / "bank",
            pattern="key_*.jsonl",
            max_samples=args.max_bank_samples,
            model=model,
            tokenizer=tokenizer,
            lora_params=lora_params,
            projector=projector,
            args=args,
        )
    if args.target in ("clean_pool", "both"):
        process_directory(
            in_dir=args.work_dir / "clean_pool",
            out_dir=args.work_dir / "grads" / "clean_pool",
            pattern="*.jsonl",
            max_samples=args.max_pca_samples,
            model=model,
            tokenizer=tokenizer,
            lora_params=lora_params,
            projector=projector,
            args=args,
        )


if __name__ == "__main__":
    main()
