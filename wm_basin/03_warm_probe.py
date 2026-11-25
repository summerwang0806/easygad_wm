#!/usr/bin/env python3
"""Step 3: Warm up the clean probe model with LoRA on unwatermarked teacher traces.

Paper reference (Section 2.3, App. B.1, App. C.6 / Tab. 15):
  - Clean probe (default here: Qwen2.5-1.5B-Instruct)
  - LoRA r=32, alpha=64, dropout=0.0, targets={q,k,v,o,gate,up,down}_proj
  - Trained for 2 epochs, lr=2e-4, batch_size=1 on ~450 clean teacher traces
  - Prompt tokens masked with -100; response truncated to 512 tokens.
  - Adapter is saved and frozen for all subsequent gradient extractions.
"""

from __future__ import annotations

import argparse
import math
import random
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from wm_basin.core import (
    DEFAULT_LORA_TARGET_MODULES,
    DEFAULT_MAX_RESPONSE_TOKENS,
    DEFAULT_MIN_RESPONSE_TOKENS,
    DEFAULT_PROBE_MODEL,
    read_jsonl,
    render_prompt_with_fallback,
    write_json,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="LoRA warm-up for the WM-Basin probe model")
    p.add_argument("--work-dir", type=Path, default=Path("wm_basin_work"))
    p.add_argument("--probe-model", type=str, default=DEFAULT_PROBE_MODEL)
    p.add_argument("--warm-jsonl", type=Path, default=None, help="Defaults to <work-dir>/teacher_warm/clean_traces.jsonl")
    p.add_argument("--lora-r", type=int, default=32)
    p.add_argument("--lora-alpha", type=int, default=64)
    p.add_argument("--epochs", type=int, default=2)
    p.add_argument("--lr", type=float, default=2e-4)
    p.add_argument("--max-prompt-tokens", type=int, default=2048)
    p.add_argument("--max-response-tokens", type=int, default=DEFAULT_MAX_RESPONSE_TOKENS)
    p.add_argument("--min-response-tokens", type=int, default=DEFAULT_MIN_RESPONSE_TOKENS)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--overwrite", action="store_true")
    return p.parse_args()


def encode_pair(
    tokenizer,
    messages: list[dict],
    response: str,
    max_prompt_tokens: int,
    max_response_tokens: int,
) -> tuple[list[int], list[int], int]:
    prompt_str = render_prompt_with_fallback(tokenizer, messages, max_prompt_tokens=max_prompt_tokens)
    prompt_ids = tokenizer.encode(prompt_str, add_special_tokens=False)
    resp_ids = tokenizer.encode(response, add_special_tokens=False)[:max_response_tokens]
    input_ids = prompt_ids + resp_ids
    labels = [-100] * len(prompt_ids) + list(resp_ids)
    return input_ids, labels, len(resp_ids)


def main() -> None:
    args = parse_args()
    probe_dir = args.work_dir / "probe"
    adapter_dir = probe_dir / "adapter"
    meta_path = probe_dir / "probe_meta.json"

    if adapter_dir.exists() and meta_path.exists() and not args.overwrite:
        print(f"[probe] Warmed probe already exists at {probe_dir}, skipping.")
        return

    import torch
    from peft import LoraConfig, get_peft_model
    from transformers import AutoModelForCausalLM, AutoTokenizer

    torch.manual_seed(args.seed)
    random.seed(args.seed)

    warm_path = args.warm_jsonl or (args.work_dir / "teacher_warm" / "clean_traces.jsonl")
    raw_rows = read_jsonl(warm_path)
    tokenizer = AutoTokenizer.from_pretrained(args.probe_model, trust_remote_code=True)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token

    dataset: list[tuple[list[int], list[int]]] = []
    for r in raw_rows:
        input_ids, labels, n_resp = encode_pair(
            tokenizer,
            r["messages"],
            r["response"],
            max_prompt_tokens=args.max_prompt_tokens,
            max_response_tokens=args.max_response_tokens,
        )
        if n_resp >= args.min_response_tokens:
            dataset.append((input_ids, labels))

    if not dataset:
        raise RuntimeError(f"No valid warm-up examples (>= {args.min_response_tokens} tokens) in {warm_path}")
    print(f"[probe] Loaded {len(dataset)}/{len(raw_rows)} warm-up examples from {warm_path}")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32
    base_model = AutoModelForCausalLM.from_pretrained(
        args.probe_model,
        torch_dtype=dtype,
        trust_remote_code=True,
    ).to(device)

    lora_cfg = LoraConfig(
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=0.0,
        target_modules=DEFAULT_LORA_TARGET_MODULES,
        bias="none",
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(base_model, lora_cfg)
    model.print_trainable_parameters()

    optimizer = torch.optim.AdamW(
        [p for p in model.parameters() if p.requires_grad],
        lr=args.lr,
        weight_decay=0.0,
    )
    total_steps = args.epochs * len(dataset)
    warmup_steps = max(1, int(0.05 * total_steps))

    def lr_lambda(step: int) -> float:
        if step < warmup_steps:
            return float(step + 1) / float(warmup_steps)
        progress = float(step - warmup_steps) / max(1, total_steps - warmup_steps)
        return 0.5 * (1.0 + math.cos(math.pi * progress))

    scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda)

    model.train()
    t0 = time.time()
    loss_history: list[float] = []
    global_step = 0
    for epoch in range(1, args.epochs + 1):
        rng = random.Random(args.seed + epoch)
        order = list(range(len(dataset)))
        rng.shuffle(order)
        ep_loss = 0.0
        for idx in order:
            input_ids, labels = dataset[idx]
            inp = torch.tensor([input_ids], dtype=torch.long, device=device)
            lbl = torch.tensor([labels], dtype=torch.long, device=device)
            optimizer.zero_grad(set_to_none=True)
            out = model(input_ids=inp, labels=lbl)
            loss = out.loss
            if not torch.isfinite(loss):
                raise RuntimeError(f"Probe warm-up diverged at epoch {epoch} step {global_step} (loss={loss.item()})")
            loss.backward()
            torch.nn.utils.clip_grad_norm_([p for p in model.parameters() if p.requires_grad], 1.0)
            optimizer.step()
            scheduler.step()
            ep_loss += float(loss.item())
            global_step += 1
        avg_loss = ep_loss / len(dataset)
        loss_history.append(avg_loss)
        print(f"[probe] Epoch {epoch}/{args.epochs}: avg_loss={avg_loss:.4f} ({time.time() - t0:.1f}s)")

    adapter_dir.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(str(adapter_dir))
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    write_json(
        meta_path,
        {
            "probe_model": args.probe_model,
            "adapter_dir": str(adapter_dir),
            "warm_jsonl": str(warm_path),
            "num_examples": len(dataset),
            "lora_r": args.lora_r,
            "lora_alpha": args.lora_alpha,
            "target_modules": DEFAULT_LORA_TARGET_MODULES,
            "trainable_params": trainable_params,
            "epochs": args.epochs,
            "lr": args.lr,
            "max_response_tokens": args.max_response_tokens,
            "min_response_tokens": args.min_response_tokens,
            "loss_history": loss_history,
        },
    )
    print(f"[probe] Saved frozen LoRA adapter ({trainable_params:,} params) to {adapter_dir}")


if __name__ == "__main__":
    main()
