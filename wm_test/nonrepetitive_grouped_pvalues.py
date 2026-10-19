"""Fixed-token KGW p-values after excluding severely repetitive whole answers.

This is a quality-filtered supplementary evaluation. It does not deduplicate
token pairs inside the retained blocks or change the original grouped results.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

if __package__:
    from .grouped_pvalues import (
        AGGREGATION, TOKEN_BUDGETS, ExactKGWScorer, _write_cache, format_p,
        group_token_flags, summarize_grouped, tokenizer_signature,
    )
else:
    from grouped_pvalues import (
        AGGREGATION, TOKEN_BUDGETS, ExactKGWScorer, _write_cache, format_p,
        group_token_flags, summarize_grouped, tokenizer_signature,
    )


SEVERE_REPETITION_THRESHOLD = 0.5
SCHEMA = "kgw-nonrepetitive-answer-blocks-simple1-cuda-v1"
METHOD = (
    "exclude whole answers whose answer-internal adjacent-token-pair repetition "
    "ratio (1 - unique pairs / all pairs) is strictly greater than 0.5; prompts "
    "excluded from repetition assessment; filter each label independently; "
    "retain original answer order, then concatenate teacher-tokenizer answer IDs "
    "without separators; exact disjoint blocks, first token context only; "
    "no token-pair deduplication within retained blocks; incomplete tail discarded; "
    "ordinary median of block p-values (mean of the middle two for even counts)"
)


def filter_severely_repetitive_answers(
    rows: list[dict[str, Any]], tokenizer: Any,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Keep answers with at most 50% repeated adjacent token pairs; no prompts."""
    retained = []
    per_answer = []
    seen_ids = set()
    for row in rows:
        sample_id = row.get("id")
        if not isinstance(sample_id, str) or not sample_id or sample_id in seen_ids:
            raise ValueError(f"Missing or duplicate answer id: {sample_id!r}")
        seen_ids.add(sample_id)
        if not isinstance(row.get("answer"), str):
            raise ValueError(f"Missing answer text for {sample_id}")
        tokens = tokenizer.encode(row["answer"], add_special_tokens=False)
        if len(tokens) != row.get("num_tokens"):
            raise ValueError(
                f"Teacher-tokenizer length mismatch for {sample_id}: "
                f"encoded={len(tokens)}, saved={row.get('num_tokens')}. "
                "Use the tokenizer used for watermark generation."
            )
        num_pairs = max(0, len(tokens) - 1)
        num_unique_pairs = len(set(zip(tokens, tokens[1:])))
        ratio = (num_pairs - num_unique_pairs) / num_pairs if num_pairs else 0.0
        excluded = ratio > SEVERE_REPETITION_THRESHOLD
        per_answer.append({
            "id": sample_id, "num_tokens": len(tokens), "num_pairs": num_pairs,
            "num_unique_pairs": num_unique_pairs,
            "repetition_ratio": ratio, "excluded": excluded,
        })
        if not excluded:
            retained.append(row)
    removed = [item for item in per_answer if item["excluded"]]
    total_before = sum(item["num_tokens"] for item in per_answer)
    total_removed = sum(item["num_tokens"] for item in removed)
    return retained, {
        "repetition_threshold": SEVERE_REPETITION_THRESHOLD,
        "comparison": ">", "scope": "answer-internal adjacent token pairs; prompt excluded",
        "num_answers_before": len(rows), "num_answers_retained": len(retained),
        "num_answers_removed": len(removed),
        "fraction_answers_removed": len(removed) / len(rows) if rows else 0.0,
        "total_answer_tokens_before": total_before,
        "total_answer_tokens_retained": total_before - total_removed,
        "total_answer_tokens_removed": total_removed,
        "removed_answer_ids": [item["id"] for item in removed],
        "per_answer": per_answer,
    }


def load_nonrepetitive_grouped_pvalues(
    source_path: Path, tokenizer_path: Path, device: str, config: dict[str, Any],
    greenlist_cache: Any = None,
) -> tuple[dict[str, Any], Path]:
    """Cache quality-filtered groups independently of every existing cache."""
    if config["seeding"] not in ("simple_1", "simple_1 (hash_key * previous_token_id)"):
        raise ValueError("Quality-filtered grouped scoring supports simple_1 only")
    source = source_path.read_bytes()
    signature = {
        "schema": SCHEMA, "source_sha256": hashlib.sha256(source).hexdigest(),
        "tokenizer": tokenizer_signature(tokenizer_path),
        "detector": {key: config[key] for key in ("gamma", "hash_key", "seeding")},
        "token_budgets": list(TOKEN_BUDGETS),
        "severe_repetition_threshold": SEVERE_REPETITION_THRESHOLD,
        "filter": "exclude whole answers; strict >; answer-internal pairs only",
        "aggregation": AGGREGATION,
    }
    cache_path = source_path.with_suffix(".nonrepetitive_grouped_p_values.json")
    if cache_path.exists():
        try:
            cached = json.loads(cache_path.read_text(encoding="utf-8"))
            if (isinstance(cached, dict) and cached.get("signature") == signature
                    and set(cached.get("budgets", {})) == {str(n) for n in TOKEN_BUDGETS}
                    and isinstance(cached.get("filtering"), dict)
                    and all(len(summary["groups"]) == summary["num_groups"]
                            for summary in cached["budgets"].values())):
                return cached, cache_path
        except (KeyError, TypeError, ValueError, OSError):
            pass
    rows = [json.loads(line) for line in source.decode("utf-8").splitlines() if line.strip()]
    scorer = ExactKGWScorer(tokenizer_path, device, config, greenlist_cache)
    retained, filtering = filter_severely_repetitive_answers(rows, scorer.tokenizer)
    print(
        f"Quality-filtered grouping {source_path.name}: removed "
        f"{filtering['num_answers_removed']}/{len(rows)} severely repetitive answers; "
        f"retained {len(retained)} answers / {filtering['total_answer_tokens_retained']} tokens",
        flush=True,
    )
    # Re-score the retained stream: skipping whole answers changes cross-answer
    # contexts. Original per-answer or per-block totals cannot be reused here.
    flags = scorer.score(retained) if retained else []
    if len(flags) != filtering["total_answer_tokens_retained"]:
        raise ValueError("Quality-filtered scored stream length differs from retained token count")
    payload = {
        "signature": signature, "source_file": str(source_path), "method": METHOD,
        "aggregation": AGGREGATION, "filtering": filtering,
        "num_answers": len(retained), "total_answer_tokens": len(flags),
        "budgets": group_token_flags(flags, config["gamma"]),
    }
    _write_cache(cache_path, payload)
    return payload, cache_path


def summarize_nonrepetitive_grouped(payload: dict[str, Any]) -> dict[str, Any]:
    summary = summarize_grouped(payload)
    summary["filtering"] = {key: value for key, value in payload["filtering"].items()
                            if key != "per_answer"}
    return summary


def write_nonrepetitive_grouped_summary(handle: Any, summaries: dict[str, Any]) -> None:
    handle.write("\n剔除严重重复回答后的固定 token 分组 p-value（普通中位数）：\n\n")
    handle.write("先独立筛选 KGW 和 clean：回答内部相邻 token 对重复比例严格大于 50% 时，"
                 "剔除整条回答；prompt 不参与判断。保留回答按原顺序重新无分隔拼接，"
                 "各组首 token 仅作上下文；组内不做 token 对去重，尾部不足一组丢弃。"
                 "这是质量筛选补充指标，原始全样本统计另行保留。\n\n")
    handle.write("| 数据 | 原回答数 | 剔除严重重复回答 | 保留回答数 | 原 tokens | "
                 "剔除 tokens | 保留 tokens |\n")
    handle.write("|---|---:|---:|---:|---:|---:|---:|\n")
    for label in ("kgw", "clean"):
        info = summaries[label]["filtering"]
        handle.write(
            f"| {label} | {info['num_answers_before']} | {info['num_answers_removed']} "
            f"({info['fraction_answers_removed']:.2%}) | {info['num_answers_retained']} | "
            f"{info['total_answer_tokens_before']} | {info['total_answer_tokens_removed']} | "
            f"{info['total_answer_tokens_retained']} |\n"
        )
    handle.write("\n| 每组 token 数 | 计分 token 数 | KGW 组数 | KGW median p ↑ | "
                 "clean 组数 | clean median p | KGW/clean 丢弃尾部 tokens |\n")
    handle.write("|---:|---:|---:|---:|---:|---:|---:|\n")
    for budget in TOKEN_BUDGETS:
        positive = summaries["kgw"]["budgets"][str(budget)]
        negative = summaries["clean"]["budgets"][str(budget)]
        handle.write(
            f"| {budget} | {budget - 1} | {positive['num_groups']} | "
            f"{format_p(positive['median_p_value'])} | {negative['num_groups']} | "
            f"{format_p(negative['median_p_value'])} | "
            f"{positive['discarded_tail_tokens']}/{negative['discarded_tail_tokens']} |\n"
        )
    handle.write("\nN/A 表示筛选后不足一个完整组。各组 p 取普通中位数，偶数组取中间两个 p "
                 "的算术平均；组数较少时请结合逐组缓存解释。\n")
