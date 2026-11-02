"""Deterministic short-answer demonstrations selected from SQuAD training rows."""
from __future__ import annotations

from collections.abc import Iterable
import random


MAX_CONTEXT_CHARS = 1800
MAX_QUESTION_CHARS = 300
MAX_ANSWER_WORDS = 8


def select_examples(
    rows: list[dict], count: int, seed: int, exclude_ids: Iterable[str] = (),
) -> list[dict]:
    """Choose distinct passages/articles without changing caller data or RNG.

    The caller supplies training rows and excludes evaluation IDs. Only the
    first annotated answer is used, and it must be a literal short span. Sorting
    IDs before a local seeded shuffle makes selection independent of file order.
    """
    if isinstance(count, bool) or not isinstance(count, int) or count < 0:
        raise ValueError("Few-shot count must be a nonnegative integer")
    if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
        raise ValueError("Few-shot seed must be a nonnegative integer")
    if count == 0:
        return []

    excluded = set(exclude_ids)
    eligible = []
    identities = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        identity = row.get("id")
        if not isinstance(identity, str) or not identity or identity in excluded:
            continue
        if identity in identities:
            raise ValueError(f"Duplicate demonstration candidate ID: {identity}")
        identities.add(identity)
        title, context, question = (row.get(key) for key in ("title", "context", "question"))
        references = row.get("references")
        if (not isinstance(title, str) or not title.strip()
                or not isinstance(context, str) or not context.strip() or len(context) > MAX_CONTEXT_CHARS
                or not isinstance(question, str) or not question.strip() or len(question) > MAX_QUESTION_CHARS
                or not isinstance(references, list) or not references):
            continue
        answer = references[0]
        if (not isinstance(answer, str) or not answer.strip()
                or len(answer.split()) > MAX_ANSWER_WORDS or answer not in context):
            continue
        eligible.append({"id": identity, "title": title, "context": context,
                         "question": question, "answer": answer})

    eligible.sort(key=lambda row: row["id"])
    random.Random(seed).shuffle(eligible)
    # Match titles to contexts rather than greedily dropping collisions: a
    # candidate sharing both dimensions can otherwise hide a feasible selection.
    by_title = {}
    for row in eligible:
        title = row["title"].strip()
        by_title.setdefault(title, []).append(row)
    chosen, context_owner = {}, {}

    def assign(title: str, visited_contexts: set[str]) -> bool:
        for candidate in by_title[title]:
            context = candidate["context"]
            if context in visited_contexts:
                continue
            visited_contexts.add(context)
            previous = context_owner.get(context)
            if previous is None or assign(previous, visited_contexts):
                context_owner[context] = title
                chosen[title] = candidate
                return True
        return False

    for title in by_title:
        assign(title, set())
        if len(chosen) == count:
            return list(chosen.values())
    raise ValueError(
        f"Requested {count} few-shot examples, but only {len(chosen)} eligible "
        "examples with distinct titles and contexts are available"
    )
