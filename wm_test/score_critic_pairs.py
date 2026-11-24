#!/usr/bin/env python3
"""Score paired KGW and clean teacher answers with a trained EasyGAD critic."""

import argparse
import json
import math
import statistics
from pathlib import Path


DATA = Path(__file__).resolve().parents[1] / "data"
ACTOR_MODEL = Path("/shared/public_models/Qwen2.5-0.5B")


def load_pairs(kgw_file, clean_file):
    import pyarrow.parquet as pq

    def read(path):
        rows = pq.read_table(path, columns=["id", "content", "teacher_response"]).to_pylist()
        by_id = {}
        for row in rows:
            identifier = row["id"]
            answer = row["teacher_response"]
            if not isinstance(identifier, str) or not identifier.strip() or identifier in by_id:
                raise ValueError(f"{path}: missing or duplicate id {identifier!r}")
            if not row["content"] or not isinstance(answer, str) or not answer.strip():
                raise ValueError(f"{path}: empty prompt or response for id {identifier!r}")
            by_id[identifier] = row
        return by_id

    kgw = read(kgw_file)
    clean = read(clean_file)
    if kgw.keys() != clean.keys():
        raise ValueError(f"ID sets differ: {len(kgw.keys() - clean.keys())} KGW-only, "
                         f"{len(clean.keys() - kgw.keys())} clean-only")
    if len(kgw) < 2:
        raise ValueError("At least two matched prompt IDs are required")
    pairs = []
    for identifier, row in kgw.items():
        clean_row = clean[identifier]
        if row["content"] != clean_row["content"]:
            raise ValueError(f"Prompt content differs for id {identifier!r}")
        pairs.append((identifier, row["content"], row["teacher_response"], clean_row["teacher_response"]))
    return pairs


def teacher_tokens(ids, pad_eos, rollout_eos, max_length):
    # EasyGAD right-pads teacher responses with tokenizer EOS and scores the
    # last valid token, including the first EOS recognized by actor rollout.
    for index, token in enumerate(ids):
        if token in rollout_eos:
            return ids[:index + 1]
    padding = max_length - len(ids)
    if pad_eos in rollout_eos:
        padding = min(padding, 1)
    return ids + [pad_eos] * padding


def score_batch(model, sequences, pad_id, device):
    import torch
    from torch.nn.utils.rnn import pad_sequence

    tensors = [torch.tensor(ids, dtype=torch.long) for ids in sequences]
    lengths = torch.tensor([len(ids) for ids in sequences], device=device)
    input_ids = pad_sequence(tensors, batch_first=True, padding_value=pad_id).to(device)
    positions = torch.arange(input_ids.shape[1], device=device).expand_as(input_ids)
    output = model(
        input_ids=input_ids,
        attention_mask=(positions < lengths[:, None]).long(),
        position_ids=positions,
        use_cache=False,
    )
    if output.logits.shape != (*input_ids.shape, 1):
        raise ValueError(f"Expected one critic logit per token, got {tuple(output.logits.shape)}")
    scores = output.logits[torch.arange(len(sequences), device=device), lengths - 1, 0]
    if not torch.isfinite(scores).all():
        raise ValueError("Critic returned a non-finite score")
    return scores.float().tolist()


def score_pairs(args, pairs):
    import torch
    from transformers import AutoConfig, AutoModelForTokenClassification, AutoTokenizer, GenerationConfig

    device = torch.device(args.device)
    dtype = torch.bfloat16 if device.type == "cuda" else torch.float32
    actor = args.actor_model.resolve()
    critic = args.critic.resolve()
    for path in (actor, critic):
        if not path.is_dir():
            raise ValueError(f"Local model directory not found: {path}")

    tokenizer = AutoTokenizer.from_pretrained(actor, local_files_only=True)
    tokenizer.truncation_side = "right"
    try:
        generation = GenerationConfig.from_pretrained(actor, local_files_only=True)
    except OSError:
        generation = GenerationConfig.from_model_config(AutoConfig.from_pretrained(actor, local_files_only=True))
    eos = generation.eos_token_id
    rollout_eos = set(eos if isinstance(eos, (list, tuple)) else [eos])
    pad_eos = tokenizer.eos_token_id
    if pad_eos is None or tokenizer.pad_token_id is None or None in rollout_eos or not rollout_eos:
        raise ValueError("Actor tokenizer and generation config must provide the EasyGAD padding and EOS IDs")

    config = AutoConfig.from_pretrained(critic, local_files_only=True)
    if config.num_labels != 1 or not any("ForTokenClassification" in arch for arch in config.architectures or []):
        raise ValueError("Use the exported single-logit critic/huggingface directory")
    model, loading = AutoModelForTokenClassification.from_pretrained(
        critic, config=config, torch_dtype=dtype, local_files_only=True, output_loading_info=True,
    )
    if loading["missing_keys"] or loading["mismatched_keys"]:
        raise ValueError(f"Critic weights are incomplete or mismatched: {loading}")
    model = model.to(device).eval()

    scored = []
    with torch.inference_mode():
        for start in range(0, len(pairs), args.batch_size):
            batch = pairs[start:start + args.batch_size]
            sequences = []
            counts = []
            for identifier, messages, kgw_answer, clean_answer in batch:
                prompt = tokenizer.apply_chat_template(messages, add_generation_prompt=True, tokenize=False)
                prompt_ids = tokenizer(prompt, add_special_tokens=False, truncation=True,
                                       max_length=args.max_prompt_length)["input_ids"]
                lengths = []
                for answer in (kgw_answer, clean_answer):
                    answer_ids = tokenizer(answer, add_special_tokens=False, truncation=True,
                                           max_length=args.max_response_length)["input_ids"]
                    if not answer_ids:
                        raise ValueError(f"Response encoded to no tokens for id {identifier!r}")
                    tokens = teacher_tokens(answer_ids, pad_eos, rollout_eos, args.max_response_length)
                    sequences.append(prompt_ids + tokens)
                    lengths.append(len(tokens))
                counts.append(lengths)
            scores = score_batch(model, sequences, tokenizer.pad_token_id, device)
            for index, (identifier, _, _, _) in enumerate(batch):
                kgw_score, clean_score = scores[2 * index:2 * index + 2]
                if sequences[2 * index] == sequences[2 * index + 1]:
                    clean_score = kgw_score
                scored.append({
                    "id": identifier,
                    "kgw_score": kgw_score,
                    "clean_score": clean_score,
                    "difference": kgw_score - clean_score,
                    "kgw_scored_response_tokens": counts[index][0],
                    "clean_scored_response_tokens": counts[index][1],
                })
    return scored


def analyze(scored):
    from scipy.stats import t

    differences = [row["difference"] for row in scored]
    n = len(differences)
    mean = statistics.mean(differences)
    standard_error = statistics.stdev(differences) / math.sqrt(n)
    margin = float(t.ppf(0.975, df=n - 1)) * standard_error
    p_value = float(t.sf(mean / standard_error, df=n - 1)) if standard_error else None
    return {
        "n_pairs": n,
        "kgw_mean_score": statistics.mean(row["kgw_score"] for row in scored),
        "clean_mean_score": statistics.mean(row["clean_score"] for row in scored),
        "mean_kgw_minus_clean": mean,
        "mean_difference_95pct_t_interval": [mean - margin, mean + margin] if standard_error else None,
        "paired_t_p_value_kgw_greater": p_value,
        "kgw_wins": sum(delta > 0 for delta in differences),
        "ties": sum(delta == 0 for delta in differences),
        "clean_wins": sum(delta < 0 for delta in differences),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--critic", type=Path, help="Trained critic exported as critic/huggingface")
    parser.add_argument("--actor-model", type=Path, default=ACTOR_MODEL,
                        help="Actor model directory used with the critic, for tokenizer and generation EOS")
    parser.add_argument("--kgw-data", type=Path, default=DATA / "dolly15k_qwen2_5_14b_kgw_gamma0.5_delta3_newtest.parquet")
    parser.add_argument("--clean-data", type=Path, default=DATA / "dolly15k_qwen2_5_14b_clean_test.parquet")
    parser.add_argument("--output", type=Path, help="New JSON file for summary and per-prompt scores")
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--batch-size", type=int, default=4, help="Number of prompt pairs per forward pass")
    parser.add_argument("--max-prompt-length", type=int, default=2048)
    parser.add_argument("--max-response-length", type=int, default=1536)
    parser.add_argument("--check-data", action="store_true", help="Validate pairs without loading a model")
    args = parser.parse_args()
    if min(args.batch_size, args.max_prompt_length, args.max_response_length) < 1:
        parser.error("Batch size and token limits must be positive")
    if not args.check_data and (args.critic is None or args.output is None):
        parser.error("--critic and --output are required for scoring")
    if not args.check_data and args.output.exists():
        parser.error(f"Choose a new output path: {args.output}")
    try:
        pairs = load_pairs(args.kgw_data, args.clean_data)
        data = {
            "kgw_data": str(args.kgw_data.resolve()),
            "clean_data": str(args.clean_data.resolve()),
            "n_pairs": len(pairs),
            "identical_answer_pairs": sum(kgw == clean for _, _, kgw, clean in pairs),
        }
        if args.check_data:
            print(json.dumps(data, indent=2))
            return
        scored = score_pairs(args, pairs)
        summary = analyze(scored)
        result = {
            **data,
            "critic": str(args.critic.resolve()),
            "actor_model": str(args.actor_model.resolve()),
            "device": args.device,
            "batch_size_pairs": args.batch_size,
            "max_prompt_length": args.max_prompt_length,
            "max_response_length": args.max_response_length,
            "summary": summary,
            "pairs": scored,
        }
        report = json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(report + "\n")
        print(json.dumps(summary, indent=2))
    except (ImportError, OSError, ValueError) as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
