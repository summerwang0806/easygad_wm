"""Run: python -m unittest discover -s new_detect -p 'test_*.py' -v"""
import copy
import json
import math
import tempfile
import unittest
from types import SimpleNamespace
from pathlib import Path
from unittest.mock import patch

from new_detect.core import binomial_score, logmean, probability, roc, score_records, summarize
from new_detect import run_blackbox as runner

TEST_ROOT = Path(__file__).resolve().parent


def records():
    return [dict(id="a", prompt_ids=[9], answer_ids=[1, 2, 1, 2], green_flags=[1, 1, 0, 1]),
            dict(id="b", prompt_ids=[8], answer_ids=[1, 2, 3], green_flags=[0, 1, 1])]


class StatisticsTests(unittest.TestCase):
    def test_inclusive_tail_and_empty(self):
        self.assertAlmostEqual(binomial_score(4, 3, .5)["p_value"], 5 / 16)
        self.assertEqual(binomial_score(4, 0, .5)["p_value"], 1.)
        self.assertIsNone(binomial_score(0, 0, .5)["p_value"])

    def test_extreme_probability_does_not_underflow(self):
        result = binomial_score(10000, 10000, .5)
        self.assertAlmostEqual(result["log10_p_value"], -10000 * math.log10(2))
        self.assertIsInstance(result["p_value"], str)

    def test_probability_mean_and_even_median_not_log_mean(self):
        units = [dict(n=10, log10_p_value=math.log10(x)) for x in [.01, .09, .2, .8]]
        summary = summarize(units)
        self.assertAlmostEqual(summary["mean_p_value"], .275)
        self.assertAlmostEqual(summary["median_p_value"], .145)
        self.assertAlmostEqual(logmean([-400, -400]), -400)
        self.assertIsInstance(probability(-400), str)

    def test_cross_answer_global_dedup_and_prompt_exclusion(self):
        result = score_records(records(), .5, (3,))
        corpus = result["corpus"]
        self.assertEqual((corpus["n"], corpus["green"]), (3, 2))
        self.assertEqual(corpus["prompt_excluded"], 2)
        self.assertEqual(corpus["duplicates_excluded"], 2)
        self.assertEqual([r["n"] for r in result["per_answer"]], [2, 2])

    def test_groups_reset_tape_preserve_context_discard_tail(self):
        result = score_records(records(), .5, (3,))
        block = result["budgets"]["3"]
        self.assertEqual(block["discarded_tail_tokens"], 1)
        self.assertEqual([(r["n"], r["green"]) for r in block["groups"]], [(2, 1), (1, 1)])
        self.assertEqual(block["groups"][1]["answer_ids"], ["a", "b"])
        self.assertEqual(block["groups"][1]["start_token"], 3)

    def test_filter_is_context_only_and_no_fake_boundary(self):
        result = score_records(records(), .5, (7,), allowed={2})
        self.assertEqual((result["corpus"]["n"], result["corpus"]["green"]), (2, 1))
        self.assertEqual(result["corpus"]["teacher_filter_excluded"], 3)
        # If answers were concatenated, the first token of b would create (2,1).
        self.assertEqual(result["corpus"]["prompt_excluded"], 2)

    def test_empty_answer_and_all_excluded_groups(self):
        result = score_records([dict(id="a", prompt_ids=[1], answer_ids=[1, 1], green_flags=[1, 1]),
                                dict(id="b", prompt_ids=[1], answer_ids=[], green_flags=[])], .5, (2, 3))
        self.assertEqual(result["per_answer_summary"]["valid_units"], 0)
        self.assertEqual(result["budgets"]["2"]["summary"]["valid_units"], 0)
        self.assertEqual(result["budgets"]["3"]["summary"]["num_units"], 0)
        self.assertEqual(roc(result["per_answer"], result["per_answer"])["status"], "insufficient_valid_units")

    def test_roc_ties_and_fpr_ceiling_unequal_sizes(self):
        unit = lambda score: dict(n=10, log10_p_value=-score)
        tied = roc([unit(1)] * 20, [unit(1)] * 10)
        self.assertEqual(tied["auroc"], .5)
        self.assertEqual(tied["tpr_at_fpr"]["5%"]["tpr"], 0.)
        perfect = roc([unit(1)] * 20, [unit(2)] * 3)
        self.assertEqual(perfect["auroc"], 1.)
        self.assertEqual(perfect["tpr_at_fpr"]["5%"]["fpr"], 0.)
        self.assertEqual(perfect["tpr_at_fpr"]["5%"]["tpr"], 1.)

    def test_binomial_uses_real_greenlist_fraction(self):
        self.assertAlmostEqual(binomial_score(1, 1, 2/5)["p_value"], .4)


class IntegrationTests(unittest.TestCase):
    def fixture(self, directory):
        root = Path(directory)
        specs = []
        rows_by_name = {}
        for name, role, delta in [("base", "clean", 2.), ("target", "target", 3.)]:
            source_rows = []
            for item in records():
                n, g = len(item["answer_ids"]), sum(item["green_flags"])
                source_rows.append(dict(id=item["id"], prompt="same prompt", answer="synthetic test",
                    model_path="synthetic-test-only", num_tokens=n, green_tokens=g,
                    z_score=(g-.5*n)/math.sqrt(.25*n),
                    kgw=dict(gamma=.5, delta=delta, hash_key=runner.KEY, seeding="simple_1"),
                    generation=dict(kgw_enabled_during_generation=False)))
            path = root / f"{name}.jsonl"
            path.write_text("\n".join(json.dumps(x) for x in source_rows), encoding="utf-8")
            specs.append(dict(name=name, role=role, path=path.name, family=name, stage="gad"))
            rows_by_name[name] = source_rows
            payload = dict(version=runner.VERSION, source_sha256=runner.digest(path), gamma=.5,
                hash_key=runner.KEY, rng="cuda", vocab_size=10,
                tokenizer_signatures=dict(detector={"synthetic_fixture": "test_only"}), records=records())
            runner.write_json(root / "cache" / f"{name}.tokens.json", payload)
        runner.write_json(root / "manifest.json", dict(reference="base", teacher_filter="unused", experiments=specs))
        return root, rows_by_name

    def test_portable_cache_full_cli_statistics(self):
        with tempfile.TemporaryDirectory(dir=TEST_ROOT) as d:
            root, _ = self.fixture(d)
            with patch.object(runner, "ROOT", root), patch.object(runner, "environment", return_value={"test": True}):
                runner.main(["--manifest", str(root/"manifest.json"), "--cache-dir", str(root/"cache"),
                             "--output-dir", str(root/"output"), "--from-cache-only", "--filter-mode", "none",
                             "--budgets", "3", "7"])
            result = json.loads((root/"output/summary.json").read_text(encoding="utf8"))
            self.assertEqual(len(result["rows"]), 6)
            self.assertEqual(result["rows"][3]["roc"]["auroc"], .5)
            self.assertTrue((root/"output/summary.md").is_file())

    def test_source_metadata_and_cache_invalidation(self):
        with tempfile.TemporaryDirectory(dir=TEST_ROOT) as d:
            root, rows = self.fixture(d)
            source = root/"target.jsonl"
            payload = json.loads((root/"cache/target.tokens.json").read_text())
            runner.validate_cache(payload, {"sha256":runner.digest(source)}, rows["target"])
            with self.assertRaises(ValueError):
                runner.validate_cache(payload, {"sha256":"changed"}, rows["target"])
            broken = copy.deepcopy(payload)
            broken["records"][0]["green_flags"][0] = 0
            with self.assertRaises(ValueError):
                runner.validate_cache(broken, {"sha256":runner.digest(source)}, rows["target"])
            broken_rows = rows["target"]
            broken_rows[0]["kgw"]["gamma"] = .25
            source.write_text("\n".join(json.dumps(x) for x in broken_rows), encoding="utf8")
            with self.assertRaises(ValueError):
                runner.load_rows(source, dict(role="target"))

    def test_teacher_filter_overlap_and_frequency(self):
        class Tokenizer:
            def encode(self, text, **kwargs):
                return [int(x) for x in text.split()]
        with tempfile.TemporaryDirectory(dir=TEST_ROOT) as d:
            path = Path(d)/"teacher.jsonl"
            path.write_text(json.dumps(dict(id="train", text="1 2 1 3")), encoding="utf8")
            info = dict(path=str(path), field="text", min_count=2)
            self.assertEqual(runner.teacher_contexts(info, Tokenizer(), {"test"})["context_ids"], [1])
            with self.assertRaises(ValueError):
                runner.teacher_contexts(info, Tokenizer(), {"train"})

    def test_prompt_reconstruction_and_wn_length_guard(self):
        class Tokenizer:
            def apply_chat_template(self, prompt, **kwargs):
                return "1 2 3 4"
            def encode(self, text, **kwargs):
                return [int(x) for x in text.split()]
            def decode(self, ids, **kwargs):
                return " ".join(map(str, ids))
        scorer = runner.CudaTokenizerScorer.__new__(runner.CudaTokenizerScorer)
        scorer.tokenizer = Tokenizer()
        scorer.get_tokenizer = lambda path: Tokenizer()
        scorer.args = SimpleNamespace(generation_tokenizer="fixture")
        row = dict(id="test", prompt=[dict(role="user", content="text")], answer="5 6", num_tokens=2,
                   model_path="fixture", generation=dict(max_prompt_tokens=2))
        self.assertEqual(scorer.encode(row)["prompt_ids"], [1, 2])
        row["generation"] = dict(max_prompt_tokens=8, prompt_truncated=False, prompt_tokens=4)
        self.assertEqual(scorer.encode(row)["prompt_ids"], [1, 2, 3, 4])
        row["generation"]["prompt_tokens"] = 3
        with self.assertRaises(ValueError):
            scorer.encode(row)


if __name__ == "__main__":
    unittest.main()
