#!/usr/bin/env python3
"""Probe an inherited watermark, then scale a known WN strength once.

Uses the official local Water-Probe-v2 ngram prompts and rank/cosine statistic.
Pan Appendix F does NOT publish an exact score-to-strength formula. The ratio
below is an explicit minimal implementation of its 'proportionally increase'
description, not an author-provided formula or a guarantee of watermark removal.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import gc
import hashlib
import json
import math
from pathlib import Path
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
if __package__ in (None, ""):
    sys.path.insert(0, str(ROOT))

from wn.probe_score import build_prefix_trie, extract_sample, score_distributions

DEFAULT_STUDENT = "/shared/wwx/EasyGAD/checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_new/gad/global_step_1813/actor/huggingface"
UPSTREAM_COMMIT = "f946e4d93d6f3e8e308e86d6c6cd95170792a70b"
PROMPT_DIR = Path(__file__).resolve().parent / "prompts"


def select_strength(score: float, reference_score: float, reference_strength: float) -> float:
    """One proportional mapping; no grid, floor, threshold band or rounding grid."""
    for name, value in (("score", score), ("reference_score", reference_score)):
        if not math.isfinite(value) or not 0 < value <= 1:
            raise ValueError(f"{name} must be positive and at most 1; cannot calibrate this probe")
    if not math.isfinite(reference_strength) or reference_strength <= 0:
        raise ValueError("reference_strength must be finite and positive")
    strength = reference_strength * score / reference_score
    if not math.isfinite(strength) or strength <= 0:
        raise ValueError("proportional strength is not finite and positive")
    return strength


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--student-model", "--model", dest="student_model", type=Path,
                        default=Path(DEFAULT_STUDENT))
    reference = parser.add_mutually_exclusive_group(required=True)
    reference.add_argument("--reference-model", type=Path,
                           help="Same-family distilled student with known effective WN strength")
    reference.add_argument("--reference-score", type=float,
                           help="Previously measured score under identical probe/model settings")
    parser.add_argument("--reference-strength", type=float, default=2.5)
    parser.add_argument("--tokenizer", type=Path, default=Path("/shared/public_models/Qwen2.5-0.5B"))
    parser.add_argument("--samples-per-prompt", type=int, default=20000)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--threshold", type=int, default=20,
                        help="Minimum count per prefix per prompt (recorded in report)")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--dtype", choices=("auto", "float32", "float16", "bfloat16"), default="auto")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "wn/probe_runs")
    parser.add_argument("--history", type=Path, default=ROOT / "wn/probe_strength_history.md")
    parser.add_argument("--dry-run", action="store_true", help="Print inputs/budget; no model loading or writes")
    args = parser.parse_args(argv)
    for name in ("samples_per_prompt", "batch_size", "threshold"):
        if getattr(args, name) <= 0:
            parser.error(f"--{name.replace('_', '-')} must be positive")
    if args.seed < 0:
        parser.error("--seed must be nonnegative")
    if not math.isfinite(args.reference_strength) or args.reference_strength <= 0:
        parser.error("--reference-strength must be finite and positive")
    if args.reference_score is not None and (not math.isfinite(args.reference_score)
                                            or not 0 < args.reference_score <= 1):
        parser.error("--reference-score must be positive and at most 1")
    if args.reference_model is not None and args.reference_model.resolve() == args.student_model.resolve():
        parser.error("target and reference are the same checkpoint: this only reproduces the anchor, not a new estimate")
    return args


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def model_config(path):
    path = path.resolve()
    config_path = path / "config.json"
    if not config_path.is_file():
        raise FileNotFoundError(f"local Hugging Face checkpoint required: {path}")
    return json.loads(config_path.read_text(encoding="utf-8"))


def collect_model(model_path, tokenizer, args, run_dir, role):
    """Free sampling; retain the first token following a valid official prefix.

    This runs the model directly instead of the upstream precomputed-logit trie.
    Generation settings are fresh and EOS stopping is disabled: the upstream
    sampler also treats EOS as a token rather than an early-stop instruction.
    """
    import torch
    from transformers import AutoModelForCausalLM, GenerationConfig

    model_config(model_path)
    device = torch.device(args.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA unavailable; use the server GPU environment or --device cpu")
    if args.dtype == "auto":
        dtype = torch.float32
        if device.type == "cuda":
            with torch.cuda.device(device):
                dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    else:
        dtype = getattr(torch, args.dtype)
    model = AutoModelForCausalLM.from_pretrained(
        str(model_path), torch_dtype=dtype, local_files_only=True,
    ).to(device).eval()
    try:
        vocab_size = len(tokenizer)
        output_vocab = model.get_output_embeddings().weight.shape[0]
        if output_vocab < vocab_size:
            raise ValueError("model output vocabulary is smaller than the supplied tokenizer")
        pad = tokenizer.pad_token_id
        if pad is None:
            pad = tokenizer.eos_token_id if tokenizer.eos_token_id is not None else 0
        distributions = []
        diagnostics = []
        for prompt_index in (1, 2):
            prompt = (PROMPT_DIR / f"ngram-p{prompt_index}.txt").read_text(encoding="utf-8")
            trie, max_prefix_tokens = build_prefix_trie(tokenizer, prompt)
            inputs = tokenizer(prompt, return_tensors="pt", add_special_tokens=True).to(device)
            prompt_length = inputs["input_ids"].shape[1]
            context_limit = getattr(model.config, "max_position_embeddings", None)
            if context_limit is not None and prompt_length + max_prefix_tokens + 1 > context_limit:
                raise ValueError("full official probe prompt exceeds the model context window")
            config = GenerationConfig(
                do_sample=True, temperature=1.0, top_p=1.0, top_k=0,
                max_new_tokens=max_prefix_tokens + 1, eos_token_id=[],
                pad_token_id=pad, use_cache=True,
                suppress_tokens=list(range(vocab_size, output_vocab)) or None,
            )
            torch.manual_seed(args.seed + prompt_index - 1)
            counts = {}
            valid = 0
            sample_path = run_dir / f"{role}_p{prompt_index}.samples.jsonl"
            with sample_path.open("x", encoding="utf-8") as handle:
                for start in range(0, args.samples_per_prompt, args.batch_size):
                    batch_size = min(args.batch_size, args.samples_per_prompt - start)
                    repeated = {key: value.repeat(batch_size, 1) for key, value in inputs.items()}
                    with torch.inference_mode():
                        outputs = model.generate(**repeated, generation_config=config)
                    generated = outputs[:, prompt_length:].cpu().tolist()
                    for offset, ids in enumerate(generated):
                        sample = extract_sample(ids, trie)
                        if sample is not None:
                            prefix, token_id = sample
                            counts.setdefault(prefix, Counter())[token_id] += 1
                            valid += 1
                        handle.write(json.dumps({"index": start + offset, "token_ids": ids,
                                                 "sample": sample}, ensure_ascii=False) + "\n")
                    print(f"[{role} p{prompt_index}] {start + batch_size}/{args.samples_per_prompt}; valid={valid}",
                          file=sys.stderr, flush=True)
                    del outputs, generated, repeated
            distributions.append(counts)
            diagnostics.append({"prompt": prompt_index, "attempted": args.samples_per_prompt,
                                "valid": valid, "prefixes": len(counts), "samples": str(sample_path)})
            write_json(run_dir / f"{role}_p{prompt_index}.counts.json", counts)
        statistic = score_distributions(*distributions, vocab_size=vocab_size, threshold=args.threshold)
        statistic.update({"model": str(model_path.resolve()), "sampling": diagnostics,
                          "dtype": str(dtype), "vocab_size": vocab_size})
        return statistic
    finally:
        del model
        gc.collect()
        if device.type == "cuda":
            torch.cuda.empty_cache()


def append_history(path, report):
    path.parent.mkdir(parents=True, exist_ok=True)
    new_file = not path.exists() or path.stat().st_size == 0
    with path.open("a", encoding="utf-8") as handle:
        if new_file:
            handle.write("# WN 探针与比例选强度记录\n\n"
                         "探针采用官方 local Water-Probe-v2。比例换算为本项目对 Pan 附录 F 的最小实现，非作者公开公式。\n\n")
        handle.write(f"## {report['run_id']}\n\n")
        handle.write(f"- 状态：`{report['status']}`\n")
        handle.write(f"- 输出强度：`{report.get('selected_strength')}`\n")
        handle.write(f"- 详细结果：`{report['result_file']}`\n\n")
        handle.write("```json\n" + json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n```\n\n")


def main(argv=None):
    args = parse_args(argv)
    prompts = [PROMPT_DIR / f"ngram-p{i}.txt" for i in (1, 2)]
    plan = {
        "student_model": str(args.student_model),
        "reference_model": str(args.reference_model) if args.reference_model else None,
        "provided_reference_score": args.reference_score,
        "reference_strength": args.reference_strength,
        "tokenizer": str(args.tokenizer),
        "prompts": [{"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                    for path in prompts],
        "upstream_commit": UPSTREAM_COMMIT,
        "samples_per_prompt": args.samples_per_prompt,
        "total_short_generations": args.samples_per_prompt * 2 * (2 if args.reference_model else 1),
        "batch_size": args.batch_size, "threshold": args.threshold, "seed": args.seed,
        "temperature": 1.0, "top_p": 1.0, "top_k": 0, "repeats": 1,
        "device": args.device, "dtype": args.dtype,
        "formula": "selected_strength = reference_strength * student_score / reference_score",
        "mapping_origin": "project proportional implementation of Pan Appendix F; not a published exact formula",
        "assumption": "reference is a same-family, comparably distilled student with a known effective WN strength",
        "scope": "Pan Appendix F tested KGW n=1; this project's previous-token KGW and Qwen are a transfer experiment",
    }
    if args.dry_run:
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        return 0
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + uuid.uuid4().hex[:8]
    run_dir = args.output_dir.resolve() / run_id
    for directory in (args.student_model, args.reference_model, args.tokenizer):
        if directory is not None and run_dir.is_relative_to(directory.resolve()):
            raise ValueError("probe outputs must be outside model/tokenizer directories")
        if directory is not None and args.history.resolve().is_relative_to(directory.resolve()):
            raise ValueError("history must be outside model/tokenizer directories")
    run_dir.mkdir(parents=True, exist_ok=False)
    report = {"run_id": run_id, "status": "running", "config": plan,
              "selected_strength": None, "result_file": str(run_dir / "result.json")}
    try:
        from transformers import AutoTokenizer
        target_config = model_config(args.student_model)
        if args.reference_model:
            reference_config = model_config(args.reference_model)
            for key in ("model_type", "vocab_size", "hidden_size", "num_hidden_layers"):
                if target_config.get(key) != reference_config.get(key):
                    raise ValueError(f"reference and target model architectures differ: {key}")
        tokenizer = AutoTokenizer.from_pretrained(str(args.tokenizer), local_files_only=True, use_fast=True)
        report["student"] = collect_model(args.student_model, tokenizer, args, run_dir, "student")
        if args.reference_model:
            report["reference"] = collect_model(args.reference_model, tokenizer, args, run_dir, "reference")
        else:
            report["reference"] = {"score": args.reference_score, "source": "user-provided same-setting score"}
        report["selected_strength"] = select_strength(
            report["student"]["score"], report["reference"]["score"], args.reference_strength,
        )
        report["status"] = "ok"
    except Exception as exc:
        report["status"] = "error"
        report["error"] = f"{type(exc).__name__}: {exc}"
        raise
    finally:
        write_json(run_dir / "result.json", report)
        append_history(args.history.resolve(), report)
    print(json.dumps({"student_score": report["student"]["score"],
                      "reference_score": report["reference"]["score"],
                      "selected_strength": report["selected_strength"],
                      "result_file": report["result_file"], "history": str(args.history.resolve())},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
