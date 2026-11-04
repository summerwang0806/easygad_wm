"""Radioactivity statistics on saved, token-level observations (no torch dependency).

Within a detection unit, repeated (context, next-token) pairs count once.
Separate fixed-budget tests reset their tape; the corpus test has one tape
across ALL answers. Prompt exclusion and optional teacher filtering precede
deduplication. Boundaries never introduce synthetic token pairs.
"""
from __future__ import annotations

import math
from collections import Counter


def probability(log10_p):
    if log10_p is None:
        return None
    if log10_p >= -300:
        return 10.0 ** log10_p
    exponent = math.floor(log10_p)
    return f"{10 ** (log10_p - exponent):.12g}e{exponent:+d}"


def logmean(logs):
    high = max(logs)
    return high + math.log10(sum(10 ** (x - high) for x in logs) / len(logs))


def binomial_score(n, green, q):
    """Inclusive right tail P[X >= green]; retain a finite log even on underflow."""
    if not (0 < q < 1) or not (0 <= green <= n):
        raise ValueError("Invalid binomial counts or null probability")
    if n == 0:
        return dict(n=0, green=0, green_fraction=None, z_score=None,
                    p_value=None, log10_p_value=None, status="no_eligible_tokens")
    from scipy.stats import binom
    log_p = float(binom.logsf(green - 1, n, q))
    if not math.isfinite(log_p):
        import numpy as np
        from scipy.special import logsumexp
        log_p = float(logsumexp(binom.logpmf(np.arange(green, n + 1), n, q)))
    log10_p = min(0.0, log_p / math.log(10))
    return dict(n=n, green=green, green_fraction=green / n,
                z_score=(green - n * q) / math.sqrt(n * q * (1 - q)),
                p_value=probability(log10_p), log10_p_value=log10_p, status="ok")


class Tape:
    def __init__(self, allowed=None):
        self.allowed = allowed
        self.seen = set()
        self.green = 0
        self.counts = Counter()

    def add(self, context, token, green, prompt_contexts):
        self.counts["raw_tokens"] += 1
        if context is None:
            self.counts["missing_context"] += 1
        elif context in prompt_contexts:
            self.counts["prompt_excluded"] += 1
        elif self.allowed is not None and context not in self.allowed:
            self.counts["teacher_filter_excluded"] += 1
        elif (context, token) in self.seen:
            self.counts["duplicates_excluded"] += 1
        else:
            self.seen.add((context, token))
            self.green += int(green)

    def result(self, q):
        return {**dict(self.counts), **binomial_score(len(self.seen), self.green, q)}


def summarize(units):
    logs = sorted(x["log10_p_value"] for x in units if x["n"])
    if not logs:
        return dict(num_units=len(units), valid_units=0, mean_p_value=None,
                    median_p_value=None, mean_log10_p_value=None, median_log10_p_value=None)
    middle = len(logs) // 2
    median = logs[middle] if len(logs) % 2 else logmean(logs[middle-1:middle+1])
    mean = logmean(logs)
    return dict(num_units=len(units), valid_units=len(logs),
                mean_p_value=probability(mean), median_p_value=probability(median),
                mean_log10_p_value=mean, median_log10_p_value=median,
                mean_effective_n=sum(x["n"] for x in units if x["n"]) / len(logs),
                fraction_p_le_0_05=sum(x <= math.log10(.05) for x in logs) / len(logs),
                fraction_p_le_1e_5=sum(x <= -5 for x in logs) / len(logs))


def score_records(records, q, budgets=(1000, 2000, 3000), allowed=None):
    """Records contain true prompt/answer token IDs and raw green flags.

    Budgets count observed answer tokens BEFORE exclusions. A group may split
    an answer, but context remains that answer's actual preceding token.
    """
    if not budgets or any(type(b) is not int or b <= 0 for b in budgets):
        raise ValueError("Budgets must be positive integers")
    corpus = Tape(allowed)
    groups = {b: [] for b in budgets}
    tapes = {b: Tape(allowed) for b in budgets}
    sources = {b: [] for b in budgets}
    answers = []
    offset = 0
    for row in records:
        prompt = row["prompt_ids"]
        tokens, flags = row["answer_ids"], row["green_flags"]
        if len(tokens) != len(flags):
            raise ValueError("Token/flag length mismatch")
        prompt_contexts = set(prompt)  # simple_1: watermark window is one token
        previous = prompt[-1] if prompt else None
        answer = Tape(allowed)
        for token, green in zip(tokens, flags):
            if green not in (0, 1):
                raise ValueError("Green flags must be 0/1")
            event = (previous, token, green, prompt_contexts)
            answer.add(*event)
            corpus.add(*event)
            for b in budgets:
                tapes[b].add(*event)
                if not sources[b] or sources[b][-1] != row["id"]:
                    sources[b].append(row["id"])
                if tapes[b].counts["raw_tokens"] == b:
                    groups[b].append(dict(index=len(groups[b]),
                                          start_token=offset + 1 - b, end_token=offset + 1,
                                          answer_ids=sources[b], **tapes[b].result(q)))
                    tapes[b], sources[b] = Tape(allowed), []
            previous = token
            offset += 1
        answers.append(dict(id=row["id"], **answer.result(q)))
    return dict(corpus=corpus.result(q), per_answer=answers,
                per_answer_summary=summarize(answers), budgets={str(b): dict(
                    groups=groups[b], summary=summarize(groups[b]),
                    discarded_tail_tokens=tapes[b].counts["raw_tokens"]) for b in budgets})


def roc(negative, positive):
    """Descriptive empirical ROC; unequal counts allowed, ties kept together."""
    neg = [-x["log10_p_value"] for x in negative if x["n"]]
    pos = [-x["log10_p_value"] for x in positive if x["n"]]
    if not neg or not pos:
        return dict(status="insufficient_valid_units", n_negative=len(neg), n_positive=len(pos))
    counts = {}
    for label, values in enumerate((neg, pos)):
        for score in values:
            counts.setdefault(score, [0, 0])[label] += 1
    points = [dict(threshold=None, fpr=0., tpr=0., fp=0, tp=0)]
    fp = tp = 0
    for score, (cn, cp) in sorted(counts.items(), reverse=True):
        fp += cn
        tp += cp
        points.append(dict(threshold=score, fpr=fp / len(neg), tpr=tp / len(pos), fp=fp, tp=tp))
    area = sum((b["fpr"] - a["fpr"]) * (a["tpr"] + b["tpr"]) / 2
               for a, b in zip(points, points[1:]))
    working = {}
    for target in (.05, .10):
        # First maximum retains the highest threshold attaining that TPR.
        best = max((p for p in points if p["fpr"] <= target), key=lambda p: p["tpr"])
        working[f"{target:.0%}"] = dict(best, target_fpr=target)
    return dict(status="ok", auroc=area, n_negative=len(neg), n_positive=len(pos),
                tpr_at_fpr=working, score="-log10(inclusive binomial p)",
                threshold_selection="descriptive empirical ROC on these evaluation units; not held-out calibration")
