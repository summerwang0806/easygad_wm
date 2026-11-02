"""Offline tests for fixed training-only SQuAD demonstration selection."""
import copy
import importlib.util
from pathlib import Path
import random
import unittest


SPEC = importlib.util.spec_from_file_location("squad_fewshot", Path(__file__).with_name("fewshot.py"))
fewshot = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(fewshot)


def row(number):
    return {"id": f"train-{number:03}", "title": f"Article {number}",
            "context": f"The city of London is mentioned in passage {number}.",
            "question": "Which city is mentioned?", "references": ["London", "city of London"]}


class FewshotChecks(unittest.TestCase):
    def test_deterministic_order_invariant_seeded_and_nonmutating(self):
        rows = [row(number) for number in range(20)]
        original = copy.deepcopy(rows)
        global_state = random.getstate()
        selected = fewshot.select_examples(rows, 4, 42)
        self.assertEqual(selected, fewshot.select_examples(rows, 4, 42))
        self.assertEqual(selected, fewshot.select_examples(list(reversed(rows)), 4, 42))
        self.assertNotEqual(selected, fewshot.select_examples(rows, 4, 43))
        self.assertEqual(rows, original)
        self.assertEqual(random.getstate(), global_state)
        self.assertEqual(set(selected[0]), {"id", "title", "context", "question", "answer"})
        self.assertEqual(selected[0]["answer"], "London")
        selected[0]["answer"] = "changed output"
        self.assertEqual(rows, original)

    def test_excludes_evaluation_ids(self):
        rows = [row(number) for number in range(6)]
        excluded = {rows[0]["id"], rows[2]["id"]}
        result = fewshot.select_examples(rows, 4, 1, exclude_ids=iter(excluded))
        self.assertTrue(excluded.isdisjoint(item["id"] for item in result))

    def test_distinct_nonempty_titles_and_contexts(self):
        rows = [row(number) for number in range(6)]
        rows[1]["title"] = rows[0]["title"]
        rows[3]["context"] = rows[2]["context"]
        rows[5]["title"] = "   "
        result = fewshot.select_examples(rows, 3, 42)
        self.assertEqual(len({item["title"].strip() for item in result}), 3)
        self.assertEqual(len({item["context"] for item in result}), 3)
        with self.assertRaisesRegex(ValueError, "only 3 eligible"):
            fewshot.select_examples(rows, 4, 42)

    def test_short_answer_and_length_filters(self):
        invalid = [row(number) for number in range(10)]
        invalid[0]["context"] = " "
        invalid[1]["context"] = "London " + "x" * fewshot.MAX_CONTEXT_CHARS
        invalid[2]["question"] = " "
        invalid[3]["question"] = "x" * (fewshot.MAX_QUESTION_CHARS + 1)
        invalid[4]["references"] = []
        invalid[5]["references"] = ["  "]
        invalid[6]["references"] = ["London is a place with far too many words here"]
        invalid[6]["context"] = invalid[6]["references"][0]
        invalid[7]["references"] = ["Missing literal span", "London"]
        invalid[8]["title"] = None
        invalid[9]["references"] = [None]
        valid = row(99)
        self.assertEqual(fewshot.select_examples([*invalid, valid], 1, 0)[0]["id"], valid["id"])
        with self.assertRaisesRegex(ValueError, "only 1 eligible"):
            fewshot.select_examples([*invalid, valid], 2, 0)

    def test_crossing_title_context_collisions_find_feasible_selection(self):
        rows = [row(number) for number in range(3)]
        rows[1]["title"] = rows[0]["title"]
        rows[2]["context"] = rows[0]["context"]
        # Selecting row 0 greedily would block both remaining rows, although
        # rows 1 and 2 form a valid pair with distinct titles and contexts.
        for seed in range(10):
            with self.subTest(seed=seed):
                result = fewshot.select_examples(rows, 2, seed)
                self.assertEqual({item["id"] for item in result}, {rows[1]["id"], rows[2]["id"]})

    def test_filter_boundaries_are_inclusive(self):
        candidate = row(1)
        candidate["references"] = ["one two three four five six seven eight"]
        candidate["context"] = candidate["references"][0] + "x" * (fewshot.MAX_CONTEXT_CHARS - len(candidate["references"][0]))
        candidate["question"] = "?" * fewshot.MAX_QUESTION_CHARS
        self.assertEqual(fewshot.select_examples([candidate], 1, 0)[0]["answer"], candidate["references"][0])

    def test_insufficient_candidates_and_duplicate_ids_fail(self):
        with self.assertRaisesRegex(ValueError, "only 0 eligible"):
            fewshot.select_examples([], 1, 0)
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            fewshot.select_examples([row(1), row(1)], 1, 0)

    def test_count_and_seed_validation_and_zero_count(self):
        for invalid in (-1, True, 1.0, "1", None):
            with self.subTest(count=invalid), self.assertRaises(ValueError):
                fewshot.select_examples([], invalid, 0)
            with self.subTest(seed=invalid), self.assertRaises(ValueError):
                fewshot.select_examples([], 0, invalid)
        self.assertEqual(fewshot.select_examples([], 0, 42), [])


if __name__ == "__main__":
    unittest.main()
