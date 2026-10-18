"""Exact fixed-token KGW evaluation with ordinary-median aggregation.

The green lists remain this project's CUDA simple_1 lists. Answer token IDs are
concatenated without separators, including cross-answer contexts. Each block
skips its first context token, counts repetitions, and discards the short tail.
Grouping follows Pan's protocol; the median averages the two middle p-values
for an even number of groups.
"""

from __future__ import annotations

from collections import OrderedDict, defaultdict
import hashlib
import json
import math
import os
from pathlib import Path
import sys
from typing import Any


TOKEN_BUDGETS = (1000, 2000, 3000, 10000, 20000, 30000)
LEGACY_SCHEMA = "kgw-pan-exact-blocks-simple1-cuda-v1"
SCHEMA = "kgw-pan-exact-blocks-simple1-cuda-v2"
AGGREGATION = "ordinary_median"
METHOD = (
    "teacher-tokenizer answer IDs concatenated without separators; exact disjoint "
    "blocks; first token of each block is context only; no repetition deduplication; "
    "incomplete tail discarded; ordinary median of block p-values "
    "(arithmetic mean of the two middle p-values for even group counts)"
)


def tail_probability(z: float) -> tuple[float | str, float]:
    """Right-tail p and log10(p), retaining extreme p instead of rounding to zero."""
    if not math.isfinite(z):
        raise ValueError("Non-finite grouped z-score")
    p = 0.5 * math.erfc(z / math.sqrt(2.0))
    if z <= 30:
        return p, math.log10(p)
    # Large positive z: use the normal-tail Mills expansion in log space before
    # erfc enters the subnormal range and loses relative precision.
    total = term = 1.0
    for index in range(1, 20):
        term *= -(2 * index - 1) / (z * z)
        total += term
        if abs(term) < abs(total) * 1e-16:
            break
    log_p = (-0.5 * z * z - math.log(z) - 0.5 * math.log(2 * math.pi)
             + math.log(total)) / math.log(10)
    if log_p >= -300:
        return p, log_p
    exponent = math.floor(log_p)
    mantissa = 10 ** (log_p - exponent)
    return f"{mantissa:.12g}e{exponent:+d}", log_p


def ordinary_median_pvalues(groups: list[dict[str, Any]]) -> tuple[float | str | None, float | None]:
    """Median on the p scale, using log space only to prevent underflow."""
    if not groups:
        return None, None
    # Sorting z descending sorts right-tail p ascending, including tiny p-values
    # represented as scientific-notation strings.
    ordered = sorted(groups, key=lambda group: -group["z_score"])
    middle = len(ordered) // 2
    upper = ordered[middle]
    if len(ordered) % 2:
        return upper["p_value"], upper["log10_p_value"]
    lower = ordered[middle - 1]
    high_log = upper["log10_p_value"]
    low_log = lower["log10_p_value"]
    # log10((p_lower + p_upper) / 2), not the average of their logarithms.
    log_p = high_log + math.log10((1.0 + 10 ** (low_log - high_log)) / 2.0)
    if log_p >= -300:
        p = (float(lower["p_value"]) + float(upper["p_value"])) / 2.0
        return p, log_p
    exponent = math.floor(log_p)
    mantissa = 10 ** (log_p - exponent)
    return f"{mantissa:.12g}e{exponent:+d}", log_p


def group_token_flags(
    flags: list[int], gamma: float, budgets: tuple[int, ...] = TOKEN_BUDGETS,
) -> dict[str, dict[str, Any]]:
    """Each flag describes membership given the previous concatenated token."""
    if not 0 < gamma < 1:
        raise ValueError("gamma must be between zero and one")
    prefix = [0]
    for flag in flags:
        if flag not in (0, 1):
            raise ValueError("Green flags must be zero or one")
        prefix.append(prefix[-1] + flag)
    result = {}
    for budget in budgets:
        if not isinstance(budget, int) or budget < 2:
            raise ValueError("A token block needs at least two tokens")
        count = len(flags) // budget
        groups = []
        for index in range(count):
            start = index * budget
            # Pan's prefix_length=1: do not score the first token of ANY block.
            n = budget - 1
            green = prefix[start + budget] - prefix[start + 1]
            z = (green - gamma * n) / math.sqrt(n * gamma * (1 - gamma))
            p, log_p = tail_probability(z)
            groups.append({
                "index": index, "start_token": start, "end_token": start + budget,
                "num_tokens_scored": n, "green_tokens": green,
                "green_fraction": green / n, "z_score": z,
                "p_value": p, "log10_p_value": log_p,
            })
        median_p, median_log_p = ordinary_median_pvalues(groups)
        result[str(budget)] = {
            "group_token_count": budget, "scored_tokens_per_group": budget - 1,
            "num_groups": count, "total_answer_tokens": len(flags),
            "discarded_tail_tokens": len(flags) % budget,
            "median_p_value": median_p,
            "median_log10_p_value": median_log_p,
            "status": "ok" if count else "insufficient_tokens", "groups": groups,
        }
    return result


def tokenizer_signature(path: Path) -> dict[str, Any]:
    """Invalidate caches when local tokenizer files or tokenizer code change."""
    if not path.is_dir():
        raise FileNotFoundError(
            f"Grouped p-values require the local teacher tokenizer: {path}. "
            "Set --tokenizer to the tokenizer used for watermark generation."
        )
    names = {
        "tokenizer.json", "tokenizer.model", "spiece.model", "vocab.json",
        "vocab.txt", "merges.txt", "tokenizer_config.json", "config.json",
        "special_tokens_map.json", "added_tokens.json",
    }
    files = {file.name: hashlib.sha256(file.read_bytes()).hexdigest()
             for file in sorted(path.iterdir())
             if file.is_file() and (file.name in names or file.suffix == ".py")}
    if not files:
        raise ValueError(f"No tokenizer files found in {path}")
    return {"path": str(path.resolve()), "files_sha256": files}


class ExactKGWScorer:
    """Classify a concatenated stream once; no model weights are loaded."""

    def __init__(self, tokenizer_path: Path, device: str, config: dict[str, Any],
                 greenlist_cache: OrderedDict | None = None):
        import torch
        from transformers import AutoTokenizer

        if not str(device).startswith("cuda") or not torch.cuda.is_available():
            raise RuntimeError(
                "First-time exact grouped p-value scoring requires CUDA to reproduce "
                "the generation green lists. Re-run evaluate_compare_metrics.py with "
                "--score-device cuda on the server. Valid grouped caches need no GPU."
            )
        root = str(Path(__file__).resolve().parents[1])
        if root not in sys.path:
            sys.path.insert(0, root)
        from wm_data.kgw import KGWConfig, KGWLogitsProcessor

        self.torch = torch
        self.device = torch.device(device)
        self.tokenizer = AutoTokenizer.from_pretrained(
            str(tokenizer_path), trust_remote_code=True, local_files_only=True,
        )
        self.config = config
        self.vocab_size = len(self.tokenizer)
        self.processor = KGWLogitsProcessor(
            self.vocab_size,
            KGWConfig(gamma=config["gamma"], delta=1.0, hash_key=config["hash_key"]),
        )
        self.cache = greenlist_cache if greenlist_cache is not None else OrderedDict()

    def score(self, rows: list[dict[str, Any]]) -> list[int]:
        tokens = []
        for row in rows:
            if not isinstance(row.get("answer"), str):
                raise ValueError(f"Missing answer text for {row.get('id')}")
            encoded = self.tokenizer.encode(row["answer"], add_special_tokens=False)
            if len(encoded) != row["num_tokens"]:
                raise ValueError(
                    f"Teacher-tokenizer length mismatch for {row.get('id')}: "
                    f"encoded={len(encoded)}, saved={row['num_tokens']}. "
                    "Check --tokenizer; grouped scoring cannot use a different vocabulary."
                )
            tokens.extend(encoded)
        flags = [0] * len(tokens)
        contexts = defaultdict(list)
        for index in range(1, len(tokens)):
            contexts[tokens[index - 1]].append((index, tokens[index]))
        torch = self.torch
        for index, (previous, positions) in enumerate(contexts.items(), 1):
            key = (self.vocab_size, self.config["gamma"], self.config["hash_key"],
                   str(self.device), previous)
            mask = self.cache.get(key)
            if mask is None:
                mask = torch.zeros(self.vocab_size, dtype=torch.bool, device=self.device)
                mask[self.processor._greenlist(previous, self.device)] = True
                self.cache[key] = mask
                if len(self.cache) > 256:
                    self.cache.popitem(last=False)
            else:
                self.cache.move_to_end(key)
            selected = torch.tensor([token for _, token in positions], device=self.device)
            membership = mask[selected].tolist()
            for (position, _), green in zip(positions, membership):
                flags[position] = int(green)
            if index % 1000 == 0:
                print(f"Grouped KGW scoring: {index}/{len(contexts)} contexts", flush=True)
        return flags


def _write_cache(cache_path: Path, payload: dict[str, Any]) -> None:
    temporary = cache_path.with_name(cache_path.name + f".{os.getpid()}.tmp")
    try:
        with temporary.open("w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2, allow_nan=False)
            handle.write("\n")
        os.replace(temporary, cache_path)
    finally:
        temporary.unlink(missing_ok=True)


def load_grouped_pvalues(
    source_path: Path, tokenizer_path: Path, device: str, config: dict[str, Any],
    greenlist_cache: OrderedDict | None = None,
) -> tuple[dict[str, Any], Path]:
    """Cache all six budgets separately from existing per-answer p-value files."""
    if config["seeding"] not in ("simple_1", "simple_1 (hash_key * previous_token_id)"):
        raise ValueError("Exact grouped scoring currently supports this project's simple_1 only")
    source = source_path.read_bytes()
    signature = {
        "schema": SCHEMA, "source_sha256": hashlib.sha256(source).hexdigest(),
        "tokenizer": tokenizer_signature(tokenizer_path),
        "detector": {key: config[key] for key in ("gamma", "hash_key", "seeding")},
        "token_budgets": list(TOKEN_BUDGETS),
    }
    cache_path = source_path.with_suffix(".grouped_p_values.json")
    if cache_path.exists():
        migrated = None
        try:
            cached = json.loads(cache_path.read_text(encoding="utf-8"))
            if set(cached.get("budgets", {})) == {str(n) for n in TOKEN_BUDGETS}:
                if cached.get("signature") == signature:
                    return cached, cache_path
                legacy_signature = {**signature, "schema": LEGACY_SCHEMA}
                if cached.get("signature") == legacy_signature:
                    # All token scoring inputs still match. Only aggregation
                    # changed, so reuse the saved per-group evidence without CUDA.
                    for summary in cached["budgets"].values():
                        groups = summary["groups"]
                        if len(groups) != summary["num_groups"]:
                            raise ValueError("Incomplete legacy grouped cache")
                        median_p, median_log_p = ordinary_median_pvalues(groups)
                        summary["median_p_value"] = median_p
                        summary["median_log10_p_value"] = median_log_p
                    cached.update(signature=signature, method=METHOD, aggregation=AGGREGATION)
                    migrated = cached
        except (KeyError, TypeError, ValueError, OSError):
            pass
        if migrated is not None:
            _write_cache(cache_path, migrated)
            return migrated, cache_path
    rows = [json.loads(line) for line in source.decode("utf-8").splitlines() if line.strip()]
    scorer = ExactKGWScorer(tokenizer_path, device, config, greenlist_cache)
    flags = scorer.score(rows)
    payload = {
        "signature": signature, "source_file": str(source_path), "method": METHOD,
        "aggregation": AGGREGATION,
        "num_answers": len(rows), "total_answer_tokens": len(flags),
        "budgets": group_token_flags(flags, config["gamma"]),
    }
    _write_cache(cache_path, payload)
    return payload, cache_path


def summarize_grouped(payload: dict[str, Any]) -> dict[str, Any]:
    return {"aggregation": AGGREGATION,
            "num_answers": payload["num_answers"],
            "total_answer_tokens": payload["total_answer_tokens"],
            "budgets": {budget: {key: value for key, value in summary.items() if key != "groups"}
                        for budget, summary in payload["budgets"].items()}}


def format_p(value: float | str | None) -> str:
    return "N/A" if value is None else value if isinstance(value, str) else f"{value:.6g}"


def write_grouped_summary(handle: Any, summaries: dict[str, Any]) -> None:
    handle.write("\n固定 token 分组 p-value（普通中位数；p 越大表示原单侧检验证据越弱）：\n\n")
    handle.write("按教师 tokenizer 编码回答并无分隔拼接，精确分组；每组首 token 仅作上下文，"
                 "其余 token 用本项目原 KGW 绿表评分；不去重，尾部不足一组丢弃；"
                 "各组 p 排序后取普通中位数（偶数组取中间两个 p 的算术平均）。\n\n")
    handle.write("| 每组 token 数 | 计分 token 数 | KGW 组数 | KGW median p ↑ | "
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
    handle.write("\nN/A 表示总 token 数不足一个完整组；组数为 1 或 2 时需结合逐组结果解释。"
                 "极小 p 用科学计数法字符串保存，同时保留 log10(p)，避免浮点下溢为 0。\n")
