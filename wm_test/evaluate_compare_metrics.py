#!/usr/bin/env python3
"""Evaluate KGW detection, reference ROUGE-L, Seq-Rep-3 and saved-answer PPL."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import statistics
import sys
from collections import OrderedDict
from datetime import datetime
from pathlib import Path
from typing import Any

if __package__:
    from .grouped_pvalues import METHOD as GROUPED_P_VALUE_METHOD, load_grouped_pvalues, summarize_grouped, write_grouped_summary
    from .nonrepetitive_grouped_pvalues import (
        METHOD as NONREPETITIVE_GROUPED_P_VALUE_METHOD,
        load_nonrepetitive_grouped_pvalues, summarize_nonrepetitive_grouped,
        write_nonrepetitive_grouped_summary,
    )
    from .ppl_scoring import PPLConfig, evaluate_ppl_files, write_ppl_summary
else:
    from grouped_pvalues import METHOD as GROUPED_P_VALUE_METHOD, load_grouped_pvalues, summarize_grouped, write_grouped_summary
    from nonrepetitive_grouped_pvalues import (
        METHOD as NONREPETITIVE_GROUPED_P_VALUE_METHOD,
        load_nonrepetitive_grouped_pvalues, summarize_nonrepetitive_grouped,
        write_nonrepetitive_grouped_summary,
    )
    from ppl_scoring import PPLConfig, evaluate_ppl_files, write_ppl_summary


ROOT = Path(__file__).resolve().parent
DEFAULT_DETECTOR_TOKENIZER = Path("/shared/public_models/Qwen2.5-14B-Instruct")

# DEFAULT_KGW = "data/dolly15k_qwen2_5_0.5b_kgw_test_kgw_scores.jsonl"
# DEFAULT_CLEAN = "data/dolly15k_qwen2_5_0.5b_clean_test_kgw_scores.jsonl"

# 两个wn
DEFAULT_KGW = "wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new_strength3.jsonl"
# DEFAULT_KGW = "wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new.jsonl"



# 没有洗水印的
# DEFAULT_KGW = "wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.jsonl"
# DEFAULT_KGW = "wm_test/kgwwarmup_kgwgad_warmup_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.jsonl"


# dipper para之后的
# DEFAULT_KGW = "wm_test/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta3_new1_qwen2_5_0_5b_dolly15k_test.jsonl"
DEFAULT_KGW = "wm_test/dipper_upkgwwarmup_upkgwgad_warmup_gamma0.5_delta3_new1_qwen2_5_0_5b_dolly15k_test.jsonl"

# cleanwarmup_cleangad
# DEFAULT_KGW = "wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl"
# DEFAULT_KGW = "wm_test/cleanwarmup_cleangad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl"


# 测试判别器是否会被para伤害的
# DEFAULT_KGW = "wm_test/cleanD_dipperparaSFT_dipperparagad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl"
# DEFAULT_KGW = "wm_test/cleanD_dipperparaSFT_dipperparagad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl"

# DEFAULT_KGW = ROOT / "dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta3_new1_qwen2_5_0_5b_dolly15k_test.jsonl"
# DEFAULT_CLEAN = ROOT / "base_qwen2_5_0_5b_dolly15k_test.jsonl"
DEFAULT_CLEAN = ROOT / "base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl"
# 下面是gamma=0.5，上面是gamma=0.25,需要和待测试文本相对应

DEFAULT_DOLLY_REFERENCE = ROOT.parent / "text_quality/references/dolly_human_500.jsonl"
DEFAULT_TEACHER_CLEAN_REFERENCE = ROOT.parent / "data/dolly15k_qwen2_5_14b_clean_test.parquet"

DEFAULT_REPORT = ROOT / "detection_metrics_history.md"

# 固定 PPL 配置：直接运行 evaluate 即使用这些设置，可在这里统一修改。
DEFAULT_PPL_ENABLED = True
DEFAULT_PPL_MODEL = Path("/shared/public_models/Llama-3-8B")
DEFAULT_PPL_GENERATION_TOKENIZER = Path("/shared/public_models/Qwen2.5-0.5B")
DEFAULT_PPL_DEVICE = "cuda"
DEFAULT_PPL_DTYPE = "bfloat16"
DEFAULT_PPL_MAX_LENGTH = None  # 使用评分模型配置的上下文窗口。
DEFAULT_PPL_OVERFLOW = "error"  # 超长时报错，不静默截断回答。
TARGET_FPRS = (0.01, 0.05, 0.10)
P_VALUE_SCHEMA = "kgw-single-sided-unique-bigram-v1"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kgw-file", type=Path, default=DEFAULT_KGW)
    parser.add_argument("--clean-file", type=Path, default=DEFAULT_CLEAN)
    parser.add_argument(
        "--dolly-reference-file", type=Path, default=DEFAULT_DOLLY_REFERENCE,
        help="Original Dolly human answers (JSONL with id, answer and prompt); matched by ID",
    )
    parser.add_argument(
        "--teacher-clean-reference-file", type=Path, default=DEFAULT_TEACHER_CLEAN_REFERENCE,
        help="14B clean teacher answers (Parquet with id, teacher_response and content, "
             "or JSONL with id, answer and prompt); matched by ID",
    )
    parser.add_argument("--tokenizer", type=Path, default=None,
                        help="Teacher tokenizer override for legacy rescoring; defaults to Qwen2.5-14B-Instruct")
    parser.add_argument("--score-device", default="cuda",
                        help="CUDA device for one-time rescoring of old JSONL; no model is loaded")
    parser.add_argument("--ppl", action=argparse.BooleanOptionalAction, default=DEFAULT_PPL_ENABLED,
                        help="Score saved answers with the fixed reference LM (enabled by default); "
                             "use --no-ppl to disable temporarily")
    parser.add_argument("--ppl-model", type=Path, default=DEFAULT_PPL_MODEL,
                        help="Local reference causal LM and tokenizer for PPL (default: Llama-3-8B Base)")
    parser.add_argument("--ppl-device", default=DEFAULT_PPL_DEVICE,
                        help="Device for the PPL reference model, e.g. cuda, cuda:0 or cpu")
    parser.add_argument("--ppl-dtype", choices=("bfloat16", "float16", "float32"), default=DEFAULT_PPL_DTYPE,
                        help="Reference model precision; use float32 for CPU scoring")
    parser.add_argument("--ppl-generation-tokenizer", type=Path, default=DEFAULT_PPL_GENERATION_TOKENIZER,
                        help="Original generation tokenizer for reconstructing prompts "
                             "(default: Qwen2.5-0.5B; tokenizer only, no student weights)")
    parser.add_argument("--ppl-max-length", type=int, default=DEFAULT_PPL_MAX_LENGTH,
                        help="Optional reference context limit, no larger than the reference model's configured limit")
    parser.add_argument("--ppl-overflow", choices=("error", "truncate_prompt"), default=DEFAULT_PPL_OVERFLOW,
                        help="Reference-context overflow: fail by default, or explicitly left-truncate only the prompt; "
                             "the full saved answer is always retained")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_REPORT,
        help="Append each run to this Markdown history document",
    )
    return parser.parse_args(argv)


def load_scores(path: Path, expected_label: str, expected_flag: bool) -> dict[str, float]:
    if not path.is_file():
        raise FileNotFoundError(f"JSONL file not found: {path}")
    scores: dict[str, float] = {}
    with path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                row: dict[str, Any] = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"invalid JSON at {path}:{line_no}: {error}") from error
            sample_id = str(row.get("id", ""))
            if not sample_id:
                raise ValueError(f"missing id at {path}:{line_no}")
            if sample_id in scores:
                raise ValueError(f"duplicate id {sample_id!r} at {path}:{line_no}")
            if row.get("label") != expected_label:
                raise ValueError(
                    f"wrong label at {path}:{line_no}: expected {expected_label!r}, "
                    f"got {row.get('label')!r}"
                )
            if row.get("is_watermarked") is not expected_flag:
                raise ValueError(
                    f"wrong is_watermarked at {path}:{line_no}: expected {expected_flag}"
                )
            try:
                score = float(row["z_score"])
            except (KeyError, TypeError, ValueError) as error:
                raise ValueError(f"invalid z_score at {path}:{line_no}") from error
            if not math.isfinite(score):
                raise ValueError(f"non-finite z_score at {path}:{line_no}")
            scores[sample_id] = score
    if not scores:
        raise ValueError(f"no scores found in {path}")
    return scores


def load_detection_config(path: Path, check_names: bool = True) -> dict[str, Any]:
    """Validate the detector that produced the saved scores, without loading CUDA."""
    config = None
    with path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError(f"KGW record must be an object at {path}:{line_no}")
            metadata = row.get("kgw", {})
            if not isinstance(metadata, dict):
                raise ValueError(f"KGW detector metadata must be an object at {path}:{line_no}")
            try:
                raw_key = metadata["hash_key"]
                current = {
                    "gamma": float(metadata["gamma"]), "delta": float(metadata["delta"]),
                    "hash_key": int(raw_key),
                    "seeding": metadata.get("seeding", "simple_1 (hash_key * previous_token_id)"),
                }
            except (KeyError, TypeError, ValueError, OverflowError) as error:
                raise ValueError(f"Missing or invalid KGW detector metadata at {path}:{line_no}") from error
            if (not math.isfinite(current["gamma"]) or not 0 < current["gamma"] < 1
                    or not math.isfinite(current["delta"]) or current["delta"] <= 0
                    or isinstance(raw_key, bool) or current["hash_key"] != raw_key or current["hash_key"] <= 0
                    or not isinstance(current["seeding"], str) or not current["seeding"]):
                raise ValueError(f"Invalid KGW detector parameters at {path}:{line_no}: {current}")
            if config is None:
                config = current
            elif current != config:
                raise ValueError(f"Mixed KGW detector parameters inside {path}:{line_no}")

            # Catch edited metadata attached to scores that were never recomputed.
            try:
                n, green, z = int(row["num_tokens"]), int(row["green_tokens"]), float(row["z_score"])
            except (KeyError, TypeError, ValueError, OverflowError) as error:
                raise ValueError(f"Missing KGW token counts or score at {path}:{line_no}") from error
            if (isinstance(row["num_tokens"], bool) or isinstance(row["green_tokens"], bool)
                    or n != row["num_tokens"] or green != row["green_tokens"] or n < 0 or not 0 <= green <= n):
                raise ValueError(f"Invalid KGW token counts at {path}:{line_no}")
            gamma = current["gamma"]
            expected_z = (green - gamma * n) / math.sqrt(n * gamma * (1 - gamma)) if n else 0.0
            if not math.isfinite(z) or not math.isclose(z, expected_z, rel_tol=1e-8, abs_tol=1e-8):
                raise ValueError(
                    f"Saved z_score is inconsistent with KGW metadata at {path}:{line_no}. "
                    "Re-score the saved prompt/answer; editing gamma alone does not rebuild green lists."
                )
            if check_names:
                names = [str(path)]
                # A deliberate rescore can change the detector without changing
                # the model that originally produced the answers.
                provenance = row.get("rescoring", {})
                has_rescore_source = (
                    isinstance(provenance, dict) and isinstance(provenance.get("source_path"), str)
                    and isinstance(provenance.get("source_sha256"), str)
                    and re.fullmatch(r"[0-9a-f]{64}", provenance["source_sha256"]) is not None
                )
                if not has_rescore_source:
                    names.append(str(row.get("model_path", "")))
                for name in names:
                    tags = re.findall(r"gamma([0-9]+(?:\.[0-9]+)?)_delta([0-9]+(?:\.[0-9]+)?)", name)
                    if tags:
                        tagged_gamma, tagged_delta = map(float, tags[-1])
                        if (not math.isclose(tagged_gamma, gamma)
                                or not math.isclose(tagged_delta, current["delta"])):
                            raise ValueError(
                                f"Watermark name declares gamma={tagged_gamma}, delta={tagged_delta}, "
                                f"but saved detector used gamma={gamma}, delta={current['delta']} "
                                f"at {path}:{line_no}. Re-score BOTH student and clean answers with "
                                "wm_test/rescore_compare_scores.py before evaluating this experiment."
                            )
    if config is None:
        raise ValueError(f"No KGW records found in {path}")
    return config


def validate_detector_pair(kgw_path: Path, clean_path: Path) -> dict[str, Any]:
    positive = load_detection_config(kgw_path)
    negative = load_detection_config(clean_path)
    # Delta is the generation logit bias; it is absent from the detection formula.
    for key in ("gamma", "hash_key", "seeding"):
        if positive[key] != negative[key]:
            raise ValueError(
                f"Student and clean detector {key} differ: {positive[key]!r} vs {negative[key]!r}. "
                "Re-score BOTH files with the same gamma, key and tokenizer before computing AUROC."
            )
    return {
        "gamma": positive["gamma"], "hash_key": positive["hash_key"], "seeding": positive["seeding"],
        "delta_by_label": {"kgw": positive["delta"], "clean": negative["delta"]},
    }


def evaluate_reference_rouge(
    sample_path: Path, reference_path: Path, reference_source: str
) -> dict[str, Any]:
    """Macro-average ROUGE-L F1 for the KGW-file answers, without altering text."""
    def load_answers(path: Path) -> dict[str, dict[str, Any]]:
        answers: dict[str, dict[str, Any]] = {}
        if path.suffix.lower() == ".parquet":
            import pyarrow.parquet as pq

            records = [
                (index, {"id": row["id"], "answer": row["teacher_response"],
                         "prompt": row["content"]})
                for index, row in enumerate(
                    pq.read_table(path, columns=["id", "teacher_response", "content"]).to_pylist(), 1
                )
            ]
        else:
            with path.open("r", encoding="utf-8") as handle:
                records = [(index, json.loads(line)) for index, line in enumerate(handle, 1)
                           if line.strip()]
        for line_no, row in records:
            if not isinstance(row, dict):
                raise ValueError(f"Expected record object at {path}:{line_no}")
            sample_id = row.get("id")
            if not isinstance(sample_id, str) or not sample_id:
                raise ValueError(f"Missing or invalid id at {path}:{line_no}")
            if sample_id in answers:
                raise ValueError(f"Duplicate id {sample_id!r} at {path}:{line_no}")
            if not isinstance(row.get("answer"), str):
                raise ValueError(f"Missing answer text at {path}:{line_no}")
            answers[sample_id] = row
        if not answers:
            raise ValueError(f"No answers found in {path}")
        return answers

    samples = load_answers(sample_path)
    references = load_answers(reference_path)
    if set(samples) != set(references):
        raise ValueError(
            "Sample and reference IDs must match exactly "
            f"(sample-only={len(set(samples) - set(references))}, "
            f"reference-only={len(set(references) - set(samples))})."
        )
    for sample_id, row in samples.items():
        reference = references[sample_id]
        if not reference["answer"].strip():
            raise ValueError(f"Empty reference answer: {sample_id}")
        if "prompt" not in row or "prompt" not in reference:
            raise ValueError(f"Missing prompt for reference alignment: {sample_id}")
        if row["prompt"] != reference["prompt"]:
            raise ValueError(f"Sample and reference prompts differ: {sample_id}")

    from rouge_score import rouge_scorer

    scorer = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)
    scores = [
        scorer.score(references[sample_id]["answer"], row["answer"])["rougeL"].fmeasure
        for sample_id, row in samples.items()
    ]
    return {
        "mean": statistics.mean(scores),
        "num_samples": len(scores),
        "evaluated_file": str(sample_path.resolve()),
        "reference_file": str(reference_path.resolve()),
        "reference_source": reference_source,
        "metric": "rougeL", "measure": "fmeasure", "use_stemmer": True,
        "aggregation": "unweighted mean of per-sample ROUGE-L F1",
    }


def evaluate_dolly_rouge(sample_path: Path, reference_path: Path) -> dict[str, Any]:
    return evaluate_reference_rouge(
        sample_path, reference_path, "databricks/databricks-dolly-15k:response"
    )


def evaluate_teacher_clean_rouge(sample_path: Path, reference_path: Path) -> dict[str, Any]:
    return evaluate_reference_rouge(
        sample_path, reference_path, "Qwen2.5-14B clean teacher responses"
    )


def evaluate_seq_rep3(sample_path: Path) -> dict[str, Any]:
    """Word-level Seq-Rep-3 on complete saved answers, with equal answer weight."""
    source = sample_path.read_bytes()
    values = []
    seen_ids = set()
    short_answers = empty_answers = 0
    for line_number, line in enumerate(source.decode("utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(f"Invalid JSON at {sample_path}:{line_number}") from error
        if not isinstance(row, dict) or not isinstance(row.get("answer"), str):
            raise ValueError(f"Missing answer text at {sample_path}:{line_number}")
        sample_id = row.get("id")
        if not isinstance(sample_id, str) or not sample_id or sample_id in seen_ids:
            raise ValueError(f"Missing or duplicate answer id at {sample_path}:{line_number}")
        seen_ids.add(sample_id)
        words = row["answer"].split()
        num_trigrams = max(len(words) - 2, 0)
        num_unique = len(set(zip(words, words[1:], words[2:])))
        values.append(1.0 - num_unique / num_trigrams if num_trigrams else 0.0)
        short_answers += len(words) < 3
        empty_answers += not words
    if not values:
        raise ValueError(f"No answers found in {sample_path}")
    return {
        "mean": math.fsum(values) / len(values), "median": statistics.median(values),
        "num_samples": len(values), "num_short_answers": short_answers,
        "num_empty_answers": empty_answers, "evaluated_file": str(sample_path.resolve()),
        "source_sha256": hashlib.sha256(source).hexdigest(), "ngram_size": 3,
        "tokenization": "answer.split(); whitespace-delimited words; case and punctuation preserved",
        "scope": "answer only; overlapping trigrams within each complete original answer; no filtering or cross-answer trigrams",
        "short_answer_policy": "answers with fewer than 3 words, including empty answers, contribute 0; counts reported",
        "aggregation": {
            "mean": "unweighted arithmetic mean of per-answer Seq-Rep-3",
            "median": "ordinary median of per-answer Seq-Rep-3; arithmetic mean of the middle two for even counts",
        },
    }


def write_seq_rep3_summary(handle: Any, summaries: dict[str, Any]) -> None:
    handle.write("\n### Seq-Rep-3（全量回答，词级三元组重复率）\n\n")
    handle.write("每条回答单独计算 1 - 不同三元组数 / 全部三元组数，再汇总逐回答算术平均和普通中位数；"
                 "偶数条的中位数取中间两个值的算术平均。只对 answer 使用 split() 空白分词，保留大小写和标点；"
                 "不包含 prompt，不跨回答拼接，不剔除严重重复回答，不按长度加权。"
                 "少于 3 个词（含空回答）按 0 计入，数量单独列出；空回答数包含在短回答数内。数值以 0–1 比例报告。\n\n")
    handle.write("| 文件组 | 样本数 | Seq-Rep-3 逐回答算术平均 ↓ | Seq-Rep-3 逐回答普通中位数 ↓ | 少于3词回答数 | 空回答数 |\n")
    handle.write("|---|---:|---:|---:|---:|---:|\n")
    for label, summary in summaries.items():
        handle.write(f"| {label} | {summary['num_samples']} | {summary['mean']:.6f} | {summary['median']:.6f}"
                     f" | {summary['num_short_answers']} | {summary['num_empty_answers']} |\n")
    for label, summary in summaries.items():
        handle.write(f"\n- {label}: `{summary['evaluated_file']}`；SHA256 `{summary['source_sha256']}`。\n")


def p_from_z(z_score: float | None) -> float | None:
    if z_score is None:
        return None
    z = float(z_score)
    if not math.isfinite(z):
        raise ValueError(f"non-finite detection z-score: {z_score}")
    return 0.5 * math.erfc(z / math.sqrt(2.0))


class LegacyRescorer:
    """Rescore saved answers using the original CUDA RNG; never generate text."""

    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.tokenizers: dict[str, Any] = {}
        self.greenlist_cache = OrderedDict()

    def score(self, row: dict[str, Any], config_override: dict[str, Any] | None = None) -> dict[str, Any]:
        import torch
        from transformers import AutoTokenizer

        sys.path.insert(0, str(ROOT.parent)) if str(ROOT.parent) not in sys.path else None
        from wm_data.kgw import KGWConfig, kgw_score

        if not str(self.args.score_device).startswith("cuda") or not torch.cuda.is_available():
            raise RuntimeError(
                "KGW rescoring requires CUDA "
                "because CPU/CUDA KGW random generators differ. Use an available GPU "
                "with CUDA_VISIBLE_DEVICES; later evaluations use the saved scores or p-value cache."
            )
        model_path = str(self.args.tokenizer or DEFAULT_DETECTOR_TOKENIZER)
        if model_path not in self.tokenizers:
            self.tokenizers[model_path] = AutoTokenizer.from_pretrained(
                model_path, trust_remote_code=True, local_files_only=True
            )
        tokenizer = self.tokenizers[model_path]
        prompt = row.get("prompt")
        if isinstance(prompt, list):
            # Preserve the original generation template and truncation, then
            # encode that same prompt text with the teacher detector tokenizer.
            generation_path = str(row.get("model_path", ""))
            if not generation_path:
                raise ValueError("Legacy message prompts require the generating model_path")
            if generation_path not in self.tokenizers:
                self.tokenizers[generation_path] = AutoTokenizer.from_pretrained(
                    generation_path, trust_remote_code=True, local_files_only=True
                )
            generation_tokenizer = self.tokenizers[generation_path]
            prompt = generation_tokenizer.apply_chat_template(prompt, add_generation_prompt=True, tokenize=False)
            generation_ids = generation_tokenizer.encode(prompt, add_special_tokens=False)
            limit = int(row.get("generation", {}).get("max_prompt_tokens", 2048))
            if len(generation_ids) > limit:
                prompt = generation_tokenizer.decode(generation_ids[:limit], skip_special_tokens=False)
        if not isinstance(prompt, str) or not isinstance(row.get("answer"), str):
            raise ValueError("Legacy rescoring requires prompt and answer text in each JSONL row")
        prompt_ids = tokenizer.encode(prompt, add_special_tokens=False)
        metadata = config_override if config_override is not None else row.get("kgw", {})
        if not all(key in metadata for key in ("gamma", "delta", "hash_key")):
            raise ValueError("Legacy rescoring requires the original kgw gamma/delta/hash_key metadata")
        score = kgw_score(
            prompt_token_ids=prompt_ids,
            generated_token_ids=tokenizer.encode(row["answer"], add_special_tokens=False),
            vocab_size=len(tokenizer),
            config=KGWConfig(gamma=float(metadata["gamma"]), delta=float(metadata["delta"]),
                             hash_key=int(metadata["hash_key"])),
            device=self.args.score_device, include_deduplicated=True,
            greenlist_cache=self.greenlist_cache,
        )
        if config_override is None and not math.isclose(float(score["z_score"]), float(row["z_score"]), abs_tol=1e-9, rel_tol=1e-9):
            raise ValueError(
                f"Raw z-score mismatch for {row['id']}: saved={row['z_score']}, "
                f"rescored={score['z_score']}. Check tokenizer, prompt format/truncation, "
                "KGW key/gamma and RNG device before accepting deduplicated p-values."
            )
        return score


def load_pvalue_records(path: Path, rescorer: LegacyRescorer) -> tuple[list[dict[str, Any]], Path]:
    source = path.read_bytes()
    digest = hashlib.sha256(source).hexdigest()
    rows = [json.loads(line) for line in source.decode("utf-8").splitlines() if line.strip()]
    cache = path.with_suffix(".p_values.jsonl")
    if cache.exists():
        try:
            cached = [json.loads(line) for line in cache.read_text(encoding="utf-8").splitlines() if line.strip()]
            if (len(cached) == len(rows)
                    and [r.get("id") for r in cached] == [r["id"] for r in rows]
                    and all(r.get("source_sha256") == digest and r.get("schema") == P_VALUE_SCHEMA
                            for r in cached)):
                return cached, cache
        except (ValueError, OSError):
            pass
    records = []
    legacy_count = 0
    for index, row in enumerate(rows, 1):
        if "dedup_z_score" in row and "dedup_num_tokens" in row:
            score = row
        else:
            score = rescorer.score(row)
            legacy_count += 1
            if legacy_count == 1 or index % 50 == 0:
                print(f"Deduplicated scoring {path.name}: {index}/{len(rows)}", flush=True)
        raw_z = float(row["z_score"])
        raw_n = score.get("num_tokens", row.get("num_tokens"))
        dedup_n = int(score["dedup_num_tokens"])
        dedup_z = float(score["dedup_z_score"]) if dedup_n > 0 else None
        records.append({
            "schema": P_VALUE_SCHEMA, "source_sha256": digest,
            "id": row["id"], "label": row["label"],
            "num_tokens_raw": raw_n, "num_tokens_dedup": dedup_n,
            "z_score_raw": raw_z, "z_score_dedup": dedup_z,
            "p_value_raw": p_from_z(raw_z) if raw_n != 0 else None,
            "p_value_dedup": p_from_z(dedup_z),
        })
    # Separate, versioned cache: never overwrite the sampled answer files.
    temporary = cache.with_name(cache.name + f".{os.getpid()}.tmp")
    try:
        with temporary.open("w", encoding="utf-8", newline="\n") as handle:
            for record in records:
                handle.write(json.dumps(record, ensure_ascii=False, allow_nan=False) + "\n")
        os.replace(temporary, cache)
    finally:
        temporary.unlink(missing_ok=True)
    return records, cache


def summarize_pvalues(records: list[dict[str, Any]], key: str) -> dict[str, Any]:
    values = [float(row[key]) for row in records if row[key] is not None]
    if any(not math.isfinite(p) or not 0 <= p <= 1 for p in values):
        raise ValueError(f"Invalid p-value in {key}")
    return {
        "n_total": len(records), "n_valid": len(values), "n_invalid": len(records) - len(values),
        "mean": statistics.mean(values) if values else None,
        "median": statistics.median(values) if values else None,
        "min": min(values) if values else None, "max": max(values) if values else None,
        "at_alpha": {
            f"{alpha:.0%}": {"alpha": alpha, "count": sum(p <= alpha for p in values),
                             "fraction": sum(p <= alpha for p in values) / len(values) if values else None}
            for alpha in TARGET_FPRS
        },
    }


def write_pvalue_summary(handle: Any, summaries: dict[str, Any]) -> None:
    handle.write("\n两种逐条文本 p-value 统计（单侧正态近似；不是 AUROC 的显著性检验）：\n\n")
    handle.write("去重规则：相同的 `(previous_token_id, token_id)` 只计一次；不修改回答文本。\n\n")
    handle.write("| 数据 | 检测方式 | 有效样本 | p 均值 | p 中位数 | p≤0.01 | p≤0.05 | p≤0.10 |\n")
    handle.write("|---|---|---:|---:|---:|---:|---:|---:|\n")
    for label in ("kgw", "clean"):
        for method, title in (("raw", "原始"), ("deduplicated", "token 对去重")):
            summary = summaries[label][method]
            mean = f"{summary['mean']:.6g}" if summary["mean"] is not None else "N/A"
            median = f"{summary['median']:.6g}" if summary["median"] is not None else "N/A"
            rates_text = []
            for alpha in ("1%", "5%", "10%"):
                rate = summary["at_alpha"][alpha]
                rates_text.append(f"{rate['count']} ({rate['fraction']:.2%})" if rate["fraction"] is not None else "N/A")
            handle.write(f"| {label} | {title} | {summary['n_valid']}/{summary['n_total']} | "
                         f"{mean} | {median} | {' | '.join(rates_text)} |\n")
    handle.write("\nKGW 的小 p 占比是该理论阈值下的检出率，clean 的小 p 占比是实测误报率。"
                 "p≤0.05 不保证实际 FPR=5%；去重可改善重复带来的失真，但不保证完全校准。"
                 "空回答不做显著性检验，p=null，并排除在有效样本统计之外。\n")


def roc_points(negative: dict[str, float], positive: dict[str, float]) -> list[dict[str, float | int]]:
    """Empirical ROC points; equal scores are treated as one threshold group."""
    groups: dict[float, list[int]] = {}
    for score in negative.values():
        groups.setdefault(score, [0, 0])[0] += 1
    for score in positive.values():
        groups.setdefault(score, [0, 0])[1] += 1
    fp = tp = 0
    points: list[dict[str, float | int]] = [
        {"threshold": math.inf, "fpr": 0.0, "tpr": 0.0, "fp": 0, "tp": 0}
    ]
    for threshold in sorted(groups, reverse=True):
        n_negative, n_positive = groups[threshold]
        fp += n_negative
        tp += n_positive
        points.append({
            "threshold": threshold,
            "fpr": fp / len(negative),
            "tpr": tp / len(positive),
            "fp": fp,
            "tp": tp,
        })
    return points


def auc(points: list[dict[str, float | int]]) -> float:
    area = 0.0
    for left, right in zip(points, points[1:]):
        area += (float(right["fpr"]) - float(left["fpr"])) * (
            float(right["tpr"]) + float(left["tpr"])
        ) / 2.0
    return area


def rates(point: dict[str, float | int], n_negative: int, n_positive: int) -> dict[str, Any]:
    tp, fp = int(point["tp"]), int(point["fp"])
    fn, tn = n_positive - tp, n_negative - fp
    precision = tp / (tp + fp) if tp + fp else 0.0
    tpr = tp / n_positive
    fpr = fp / n_negative
    f1 = 2 * precision * tpr / (precision + tpr) if precision + tpr else 0.0
    threshold = float(point["threshold"])
    return {
        "threshold": threshold if math.isfinite(threshold) else None,
        "fpr": fpr,
        "tpr": tpr,
        "precision": precision,
        "f1": f1,
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
    }


def evaluate(negative: dict[str, float], positive: dict[str, float]) -> dict[str, Any]:
    if set(negative) != set(positive):
        raise ValueError(
            "The two JSONL files must have identical sample IDs "
            f"(clean-only={len(set(negative) - set(positive))}, "
            f"kgw-only={len(set(positive) - set(negative))})."
        )
    points = roc_points(negative, positive)
    best: dict[str, Any] | None = None
    for point in points:
        candidate = rates(point, len(negative), len(positive))
        if best is None or candidate["f1"] > best["f1"]:
            best = candidate
    assert best is not None

    # For each target FPR, report the largest empirical TPR achievable without
    # exceeding that FPR. Tied scores move together as one threshold group.
    at_fpr: dict[str, Any] = {}
    for target in TARGET_FPRS:
        eligible = [point for point in points if float(point["fpr"]) <= target]
        point = max(
            eligible,
            key=lambda item: (float(item["tpr"]), float(item["threshold"])),
        )
        result = rates(point, len(negative), len(positive))
        result["target_fpr"] = target
        at_fpr[f"{target:.0%}"] = result

    return {
        "positive_class": "kgw",
        "score": "z_score (higher means more likely watermarked)",
        "num_kgw": len(positive),
        "num_clean": len(negative),
        "auroc": auc(points),
        "best_f1": best,
        "tpr_at_fpr": at_fpr,
        "note": "For each target FPR, select the empirical ROC point with the highest "
                "TPR whose FPR does not exceed the target; tied scores are kept together.",
    }


def main() -> None:
    args = parse_args()
    kgw = load_scores(args.kgw_file.resolve(), "kgw", True)
    clean = load_scores(args.clean_file.resolve(), "clean", False)
    detector = validate_detector_pair(args.kgw_file.resolve(), args.clean_file.resolve())
    result = evaluate(clean, kgw)
    result["detector_config"] = detector
    result["rouge_l_dolly"] = evaluate_dolly_rouge(
        args.kgw_file.resolve(), args.dolly_reference_file.resolve()
    )
    result["rouge_l_teacher_clean"] = evaluate_teacher_clean_rouge(
        args.kgw_file.resolve(), args.teacher_clean_reference_file.resolve()
    )
    result["seq_rep_3"] = {
        label: evaluate_seq_rep3(path.resolve())
        for label, path in (("kgw", args.kgw_file), ("clean", args.clean_file))
    }
    rescorer = LegacyRescorer(args)
    p_kgw, kgw_cache = load_pvalue_records(args.kgw_file.resolve(), rescorer)
    p_clean, clean_cache = load_pvalue_records(args.clean_file.resolve(), rescorer)
    result["p_values"] = {
        label: {"raw": summarize_pvalues(records, "p_value_raw"),
                "deduplicated": summarize_pvalues(records, "p_value_dedup")}
        for label, records in (("kgw", p_kgw), ("clean", p_clean))
    }
    result["p_value_method"] = "one-sided normal survival probability; unique context-token pairs for dedup"
    result["per_sample_p_value_files"] = {"kgw": str(kgw_cache), "clean": str(clean_cache)}
    # Additional fixed-token statistics with ordinary-median aggregation; existing per-answer metrics
    # and their caches are left unchanged.
    grouped_summaries = {}
    grouped_caches = {}
    for label, path in (("kgw", args.kgw_file), ("clean", args.clean_file)):
        payload, cache = load_grouped_pvalues(
            path.resolve(), Path(args.tokenizer or DEFAULT_DETECTOR_TOKENIZER),
            args.score_device, detector, rescorer.greenlist_cache,
        )
        grouped_summaries[label] = summarize_grouped(payload)
        grouped_caches[label] = str(cache)
    result["grouped_p_values"] = grouped_summaries
    result["grouped_p_value_method"] = GROUPED_P_VALUE_METHOD
    result["per_group_p_value_files"] = grouped_caches
    nonrepetitive_summaries = {}
    nonrepetitive_caches = {}
    nonrepetitive_payloads = {}
    for label, path in (("kgw", args.kgw_file), ("clean", args.clean_file)):
        payload, cache = load_nonrepetitive_grouped_pvalues(
            path.resolve(), Path(args.tokenizer or DEFAULT_DETECTOR_TOKENIZER),
            args.score_device, detector, rescorer.greenlist_cache,
        )
        nonrepetitive_summaries[label] = summarize_nonrepetitive_grouped(payload)
        nonrepetitive_caches[label] = str(cache)
        nonrepetitive_payloads[label] = payload
    result["grouped_p_values_without_severe_repetition"] = nonrepetitive_summaries
    result["grouped_p_value_without_severe_repetition_method"] = NONREPETITIVE_GROUPED_P_VALUE_METHOD
    result["per_group_p_value_without_severe_repetition_files"] = nonrepetitive_caches
    result["ppl"] = {"enabled": False}
    if getattr(args, "ppl", False):
        # All watermark scoring is finished. Release cached CUDA green lists
        # before loading the reference language model.
        rescorer.greenlist_cache.clear()
        print("PPL: evaluating saved answers only (no student generation)", flush=True)
        result["ppl"] = evaluate_ppl_files(
            {"kgw": args.kgw_file.resolve(), "clean": args.clean_file.resolve()},
            PPLConfig(
                model_path=args.ppl_model,
                device=args.ppl_device,
                dtype=args.ppl_dtype,
                generation_tokenizer=args.ppl_generation_tokenizer,
                max_length=args.ppl_max_length,
                overflow=args.ppl_overflow,
            ),
            repetition_filters=nonrepetitive_payloads,
            repetition_filter_files=nonrepetitive_caches,
        )
    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    result["evaluated_at"] = timestamp
    result["kgw_file"] = str(args.kgw_file.resolve())
    result["clean_file"] = str(args.clean_file.resolve())
    output = args.output.resolve()
    result["history_document"] = str(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    best = result["best_f1"]
    with output.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(f"\n## 评估记录：{timestamp}\n\n")
        handle.write(f"- 样本数：KGW {result['num_kgw']}，clean {result['num_clean']}\n")
        handle.write(f"- AUROC：{result['auroc']:.6f}\n")
        handle.write(f"- 实际检测配置：`{json.dumps(detector, ensure_ascii=False)}`\n")
        rouge = result["rouge_l_dolly"]
        handle.write(
            f"- ROUGE-L（同批 {rouge['num_samples']} 条原始 Dolly 回答作参考）："
            f"{rouge['mean']:.6f}（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）\n"
        )
        handle.write(f"- 原始 Dolly 参考文件：`{rouge['reference_file']}`\n")
        teacher_rouge = result["rouge_l_teacher_clean"]
        handle.write(
            f"- ROUGE-L（同批 {teacher_rouge['num_samples']} 条 14B clean 教师回答作参考）："
            f"{teacher_rouge['mean']:.6f}（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）\n"
        )
        handle.write(f"- 14B clean 教师参考文件：`{teacher_rouge['reference_file']}`\n")
        handle.write(
            f"- Best F1：{best['f1']:.6f}（z 阈值 {best['threshold']}，"
            f"TPR {best['tpr']:.6f}，FPR {best['fpr']:.6f}）\n"
        )
        handle.write("- TPR@FPR 及该工作点的 F1：\n\n")
        handle.write("  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |\n")
        handle.write("  |---:|---:|---:|---:|---:|\n")
        for target, metrics in result["tpr_at_fpr"].items():
            handle.write(
                f"  | {target} | {metrics['fpr']:.6f} | {metrics['tpr']:.6f} | "
                f"{metrics['f1']:.6f} | {metrics['threshold']} |\n"
            )
        write_seq_rep3_summary(handle, result["seq_rep_3"])
        write_pvalue_summary(handle, result["p_values"])
        handle.write(f"\n逐条 p-value：`{kgw_cache}`；`{clean_cache}`\n")
        write_grouped_summary(handle, grouped_summaries)
        handle.write(f"\n逐组 p-value 缓存：`{grouped_caches['kgw']}`；`{grouped_caches['clean']}`\n")
        write_nonrepetitive_grouped_summary(handle, nonrepetitive_summaries)
        handle.write(
            f"\n剔除严重重复回答后的逐组 p-value 缓存：`{nonrepetitive_caches['kgw']}`；"
            f"`{nonrepetitive_caches['clean']}`\n"
        )
        if result["ppl"]["enabled"]:
            write_ppl_summary(handle, result["ppl"])
        handle.write("\n完整指标（JSON）：\n\n```json\n")
        json.dump(result, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n```\n")

    print(f"KGW samples: {result['num_kgw']} | clean samples: {result['num_clean']}")
    print(f"AUROC: {result['auroc']:.6f}")
    print(f"Detector config: {json.dumps(detector, ensure_ascii=False)}")
    rouge = result["rouge_l_dolly"]
    print(
        f"ROUGE-L（原始 Dolly 参考）: {rouge['mean']:.6f} "
        f"| samples: {rouge['num_samples']} | per-sample F1 mean, use_stemmer=True"
    )
    teacher_rouge = result["rouge_l_teacher_clean"]
    print(
        f"ROUGE-L（14B clean 教师参考）: {teacher_rouge['mean']:.6f} "
        f"| samples: {teacher_rouge['num_samples']} | per-sample F1 mean, use_stemmer=True"
    )
    write_seq_rep3_summary(sys.stdout, result["seq_rep_3"])
    print(
        f"Best F1: {best['f1']:.6f} | z threshold: {best['threshold']} | "
        f"TPR: {best['tpr']:.6f} | FPR: {best['fpr']:.6f}"
    )
    print("TPR at target FPR:")
    for target, metrics in result["tpr_at_fpr"].items():
        print(
            f"  {target:>3}: TPR={metrics['tpr']:.6f} | F1={metrics['f1']:.6f} | "
            f"actual FPR={metrics['fpr']:.6f} | z threshold={metrics['threshold']}"
        )
    print(f"Appended metrics to: {output}")
    for label, methods in result["p_values"].items():
        for method, summary in methods.items():
            print(f"p-values {label}/{method}: {json.dumps(summary, ensure_ascii=False)}")
    print(f"Per-sample p-values: {kgw_cache} | {clean_cache}")
    write_grouped_summary(sys.stdout, grouped_summaries)
    print(f"Per-group p-values: {grouped_caches['kgw']} | {grouped_caches['clean']}")
    write_nonrepetitive_grouped_summary(sys.stdout, nonrepetitive_summaries)
    print(
        f"Per-group p-values without severe repetition: "
        f"{nonrepetitive_caches['kgw']} | {nonrepetitive_caches['clean']}"
    )
    if result["ppl"]["enabled"]:
        write_ppl_summary(sys.stdout, result["ppl"])


if __name__ == "__main__":
    main()
