#!/usr/bin/env python3
"""Generate paired Dolly test answers and score their KGW signal.

The KGW-trained student and its untrained base model receive the same prompts.
KGW is NOT applied at inference: scores measure whether the trained student
learned the watermark from SFT data.
"""
from __future__ import annotations

import argparse
import gc
import json
import os
import sys
from collections import OrderedDict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if __package__ in (None, ""):
    sys.path.insert(0, str(ROOT))
DEFAULT_INPUT = ROOT / "data/dolly15k_test.parquet"
# DEFAULT_STUDENT = ROOT / (
#     "checkpoints/te_Qwen2.5-14B_st_Qwen2.5-1.5B-Instruct_KGW_FULL_SeqKD/"
#     "hf_model"
# )
# DEFAULT_STUDENT = ROOT / (
#     "checkpoints/kgw_gad_05b_14b_full/"
#     "gad/global_step_1813/actor/huggingface"
# )
# DEFAULT_STUDENT = ROOT / (
#     "checkpoints/kgw_gad_05b_14b_full/"
#     "warmup/global_step_1813/actor/huggingface"
# )
# DEFAULT_STUDENT = ROOT / (
#     "checkpoints/kgw_gad_05b_14b_full/gad/global_step_1500/actor/huggingface"
# )

DEFAULT_STUDENT = ROOT / (
    # "checkpoints/te_old_st_Qwen2.5-0.5B_SeqKD_kgwdata_epoch2_new/global_step_3626/actor/huggingface"
    # "checkpoints/te_old_st_Qwen2.5-0.5B_SeqKD_kgwdata_epoch2_new/global_step_2000/actor/huggingface"
    # "checkpoints/te_old_st_Qwen2.5-0.5B_SeqKD_kgwdata_epoch5/global_step_5500/actor/huggingface"
    # "checkpoints/kgw_gad_05b_kgwwarmup_cleangad_control/gad/global_step_1813/actor/huggingface"
    # "checkpoints/kgw_gad_05b_kgwwarmup_cleangad_control/warmup/global_step_1813/actor/huggingface"
    # "checkpoints/kgw_gad_05b_cleanwarmup_kgwgad_control/gad/global_step_1813/actor/huggingface"
    # "checkpoints/kgw_gad_05b_cleanwarmup_kgwgad_control/warmup/global_step_1813/actor/huggingface"

    # "checkpoints/gad_05b_cleanwarmup_cleangad_control/gad/global_step_1813/actor/huggingface"
    "checkpoints/gad_05b_cleanwarmup_cleangad_control/warmup/global_step_1813/actor/huggingface"

    # "checkpoints/te_old_st_Qwen2.5-0.5B_2warmup/warmup/global_step_3626/actor/huggingface"
    # "checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta3/gad/global_step_1813/actor/huggingface"
    # "checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta3/warmup/global_step_1813/actor/huggingface"
    # "checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta3/gad/global_step_1813/actor/huggingface"
    # "checkpoints/kgw_up_dipper_up_1ep_0.25-2/gad/global_step_1813/actor/huggingface"
    # "checkpoints/kgw_up_dipper_up_1ep_0.25-2/warmup/global_step_1813/actor/huggingface"
    # "checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta2/warmup/global_step_1813/actor/huggingface"
    # "checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta2/gad/global_step_1813/actor/huggingface"
    # "checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_new/warmup/global_step_1813/actor/huggingface"
    # "checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_new/gad/global_step_1813/actor/huggingface"
    # "checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta2_dipper2stage/warmup/global_step_1813/actor/huggingface"
    # "checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta2_dipper2stage/gad/global_step_1813/actor/huggingface"
    # "checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_new_dipper2stage/gad/global_step_1813/actor/huggingface"
    # "checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_new_dipper2stage/warmup/global_step_1813/actor/huggingface"
    # "checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_new1_dipper2stage/warmup/global_step_1813/actor/huggingface"
    # "checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_new1_dipper2stage/gad/global_step_1813/actor/huggingface"
)


DEFAULT_BASE = Path("/shared/public_models/Qwen2.5-0.5B")
DEFAULT_DETECTOR_TOKENIZER = Path("/shared/public_models/Qwen2.5-14B-Instruct")
DEFAULT_STUDENT_OUTPUT = ROOT / "wm_test/cleanwarmup_cleangad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl"
DEFAULT_BASE_OUTPUT = ROOT / "wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--student-model", type=Path, default=DEFAULT_STUDENT)
    parser.add_argument("--base-model", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--student-output", type=Path, default=DEFAULT_STUDENT_OUTPUT)
    parser.add_argument("--base-output", type=Path, default=DEFAULT_BASE_OUTPUT)
    parser.add_argument("--limit", type=int, default=None,
                        help="Optional first-N limit for a small smoke run")
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--max-prompt-tokens", type=int, default=2048)
    parser.add_argument("--max-new-tokens", type=int, default=1536)
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--top-p", type=float, default=0.9)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--gpu-memory-utilization", type=float, default=0.4,
                        help="Fraction of total GPU memory reserved by vLLM (default: 0.20)")
    parser.add_argument("--gamma", type=float, required=True,
                        help="KGW detector green fraction; explicitly match the training watermark")
    parser.add_argument("--delta", type=float, required=True,
                        help="Training watermark logit bias, recorded as metadata; no inference watermark is applied")
    parser.add_argument("--hash-key", type=int, default=15_485_863)
    parser.add_argument("--overwrite", action="store_true",
                        help="Replace the two final output files")
    return parser.parse_args(argv)


def render_prompt(tokenizer: Any, messages: list[dict[str, str]], max_tokens: int) -> str:
    prompt = tokenizer.apply_chat_template(
        messages, add_generation_prompt=True, tokenize=False
    )
    prompt_ids = tokenizer.encode(prompt, add_special_tokens=False)
    if len(prompt_ids) > max_tokens:
        prompt_ids = prompt_ids[:max_tokens]
        prompt = tokenizer.decode(prompt_ids, skip_special_tokens=False)
    return prompt


def run_model(
    *, model_path: Path, label: str, output_path: Path, rows: list[dict[str, Any]],
    tokenizer: Any, args: argparse.Namespace,
    detector_tokenizer: Any = None,
) -> None:
    import torch

    from vllm import LLM, SamplingParams
    from wm_data.kgw import KGWConfig, kgw_score

    if detector_tokenizer is None:
        from transformers import AutoTokenizer
        detector_tokenizer = AutoTokenizer.from_pretrained(
            str(DEFAULT_DETECTOR_TOKENIZER), trust_remote_code=True
        )

    greenlist_cache = OrderedDict()

    if output_path.exists() and not args.overwrite:
        raise FileExistsError(f"{output_path} exists; pass --overwrite to replace it")
    if not model_path.exists():
        raise FileNotFoundError(f"model directory not found: {model_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = output_path.with_suffix(output_path.suffix + ".tmp")
    print(f"Loading {label}: {model_path}", flush=True)
    engine = LLM(
        model=str(model_path),
        tokenizer=str(model_path),
        trust_remote_code=True,
        tensor_parallel_size=1,
        dtype="auto",
        gpu_memory_utilization=args.gpu_memory_utilization,
        max_model_len=args.max_prompt_tokens + args.max_new_tokens,
    )

    try:
        with tmp_path.open("w", encoding="utf-8") as out_file:
            for start in range(0, len(rows), args.batch_size):
                batch = rows[start:start + args.batch_size]
                prompts = [
                    render_prompt(tokenizer, row["content"], args.max_prompt_tokens)
                    for row in batch
                ]
                sampling = [
                    SamplingParams(
                        n=1,
                        temperature=args.temperature,
                        top_p=args.top_p,
                        max_tokens=args.max_new_tokens,
                        seed=args.seed + start + offset,
                        skip_special_tokens=True,
                    )
                    for offset in range(len(batch))
                ]
                generations = engine.generate(prompts, sampling, use_tqdm=False)
                for offset, (row, prompt, result) in enumerate(
                    zip(batch, prompts, generations, strict=True)
                ):
                    answer = result.outputs[0].text
                    prompt_ids = detector_tokenizer.encode(prompt, add_special_tokens=False)
                    # Match wm_data's existing scorer by scoring the visible,
                    # re-tokenized answer and excluding the prompt itself.
                    answer_ids = detector_tokenizer.encode(answer, add_special_tokens=False)
                    score = kgw_score(
                        prompt_token_ids=prompt_ids,
                        generated_token_ids=answer_ids,
                        vocab_size=len(detector_tokenizer),
                        config=KGWConfig(
                            gamma=args.gamma, delta=args.delta, hash_key=args.hash_key
                        ),
                        device="cuda",
                        include_deduplicated=True,
                        greenlist_cache=greenlist_cache,
                    )
                    record = {
                        "id": row["id"],
                        "model_label": label,
                        "label": "kgw" if label == "kgw_trained_student" else "clean",
                        "is_watermarked": label == "kgw_trained_student",
                        "model_path": str(model_path),
                        "prompt": row["content"],
                        "answer": answer,
                        **score,
                        "kgw": {
                            "gamma": args.gamma,
                            "delta": args.delta,
                            "hash_key": args.hash_key,
                            "seeding": "simple_1 (hash_key * previous_token_id)",
                            "detection_threshold_z": 4.0,
                            "deduplication": "unique (previous_token_id, token_id) pairs",
                        },
                        "generation": {
                            "temperature": args.temperature,
                            "top_p": args.top_p,
                            "max_new_tokens": args.max_new_tokens,
                            "max_prompt_tokens": args.max_prompt_tokens,
                            "seed": args.seed + start + offset,
                            "kgw_enabled_during_generation": False,
                        },
                    }
                    out_file.write(json.dumps(record, ensure_ascii=False) + "\n")
                out_file.flush()
                done = min(start + len(batch), len(rows))
                print(f"{label}: {done}/{len(rows)} answers generated and scored", flush=True)
        os.replace(tmp_path, output_path)
    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise
    finally:
        del engine
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    print(f"Saved {len(rows)} rows to {output_path}", flush=True)


def main() -> None:
    args = parse_args()
    import pyarrow.parquet as pq
    import torch
    from transformers import AutoTokenizer

    from wm_data.kgw import KGWConfig

    KGWConfig(gamma=args.gamma, delta=args.delta, hash_key=args.hash_key).validate()
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required: KGW scoring must use the same CUDA RNG as wm_data")
    if args.batch_size <= 0:
        raise ValueError("--batch-size must be positive")
    if args.limit is not None and args.limit <= 0:
        raise ValueError("--limit must be positive")
    if args.student_output.resolve() == args.base_output.resolve():
        raise ValueError("student and base outputs must be different files")

    rows = pq.read_table(args.input).to_pylist()
    if args.limit is not None:
        rows = rows[:args.limit]
    if not rows:
        raise ValueError(f"no test rows found in {args.input}")
    for row in rows:
        if not row.get("id") or not isinstance(row.get("content"), list):
            raise ValueError("input rows must contain a nonempty id and message-list content")
    print(f"Loaded {len(rows)} prompts from {args.input}", flush=True)

    # Keep generation formatting unchanged; detect in the watermark teacher's token space.
    tokenizer = AutoTokenizer.from_pretrained(str(args.student_model), trust_remote_code=True)
    detector_tokenizer = AutoTokenizer.from_pretrained(str(DEFAULT_DETECTOR_TOKENIZER), trust_remote_code=True)
    run_model(
        model_path=args.student_model,
        label="kgw_trained_student",
        output_path=args.student_output,
        rows=rows,
        tokenizer=tokenizer,
        detector_tokenizer=detector_tokenizer,
        args=args,
    )
    run_model(
        model_path=args.base_model,
        label="untrained_base",
        output_path=args.base_output,
        rows=rows,
        tokenizer=tokenizer,
        detector_tokenizer=detector_tokenizer,
        args=args,
    )
    print("Done. Both files contain the same prompt IDs, answers, and KGW z-scores.", flush=True)


if __name__ == "__main__":
    main()
