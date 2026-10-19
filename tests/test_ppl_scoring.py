"""Saved-answer PPL regressions without CUDA, weights, torch or network.

Run with ``python -m unittest tests.test_ppl_scoring -v``. The fake reference
model assigns known token probabilities so the assertions check the actual
token-weighted likelihood calculation rather than implementation details.
"""

from copy import deepcopy
import contextlib
import io
import json
import math
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import patch

from wm_test import ppl_scoring as ppl


ROOT = Path(__file__).resolve().parents[1]


class CharacterTokenizer:
    """An invertible tokenizer with a visible BOS and chat-template suffix."""

    bos_token_id = 1
    eos_token_id = 2
    pad_token_id = 0
    model_max_length = 128

    def encode(self, text, add_special_tokens=True):
        ids = [ord(char) + 10 for char in text]
        return ([self.bos_token_id] if add_special_tokens else []) + ids

    def decode(self, ids, skip_special_tokens=False, **kwargs):
        return "".join(chr(token - 10) for token in ids if token >= 10)

    def apply_chat_template(self, messages, add_generation_prompt=True, tokenize=False):
        text = "".join(f"[{message['role']}]{message['content']}" for message in messages)
        if add_generation_prompt:
            text += "[assistant]"
        return self.encode(text, add_special_tokens=False) if tokenize else text

    def __call__(self, text, add_special_tokens=True, return_offsets_mapping=False, **kwargs):
        result = {"input_ids": self.encode(text, add_special_tokens=add_special_tokens)}
        if return_offsets_mapping:
            offsets = [(index, index + 1) for index in range(len(text))]
            result["offset_mapping"] = ([(0, 0)] if add_special_tokens else []) + offsets
        return result


class KnownLikelihoodBackend:
    """Reference token probabilities: p(a)=1/2, p(b)=1/4."""

    def __init__(self, max_length=128):
        self.tokenizer = CharacterTokenizer()
        self.max_length = max_length
        self.calls = []

    def score(self, token_ids, answer_start):
        self.calls.append((list(token_ids), answer_start))
        nll = {ord("a") + 10: math.log(2), ord("b") + 10: math.log(4)}
        return sum(nll.get(token, math.log(8)) for token in token_ids[answer_start:])


class TinyTensor:
    """Minimal 2D/3D indexing needed by the real causal-CE scorer."""

    def __init__(self, values):
        self.values = values

    def __getitem__(self, index):
        values = self.values
        for part in index if isinstance(index, tuple) else (index,):
            values = values[part]
        return TinyTensor(values)

    def float(self):
        return self

    def item(self):
        return self.values


class CausalCrossEntropyTests(unittest.TestCase):
    def backend(self, probabilities):
        """Execute production score(), substituting only tensor primitives."""
        calls = []
        supplied_inputs = []

        def cross_entropy(logits, targets, reduction):
            self.assertEqual(reduction, "sum")
            self.assertEqual(len(logits.values), len(targets.values))
            calls.append((deepcopy(logits.values), list(targets.values)))
            total = 0.0
            for row, target in zip(logits.values, targets.values, strict=True):
                total += math.log(sum(math.exp(value) for value in row)) - row[target]
            return TinyTensor(total)

        def model(**kwargs):
            supplied_inputs.append(kwargs)
            self.assertFalse(kwargs["use_cache"])
            return types.SimpleNamespace(logits=TinyTensor([
                [[math.log(value) for value in row] for row in probabilities]]))

        backend = object.__new__(ppl._TransformersBackend)
        backend.device = "cpu"
        backend.model = model
        backend.torch = types.SimpleNamespace(
            tensor=lambda values, **kwargs: TinyTensor(values), long="long",
            inference_mode=contextlib.nullcontext,
            nn=types.SimpleNamespace(functional=types.SimpleNamespace(cross_entropy=cross_entropy)),
        )
        return backend, calls, supplied_inputs

    def test_real_scorer_excludes_prompt_and_predicts_first_answer_from_last_prompt(self):
        probabilities = [[0.1, 0.2, 0.3, 0.4], [0.1, 0.1, 0.7, 0.1],
                         [0.05, 0.05, 0.1, 0.8], [0.25] * 4]
        backend, calls, inputs = self.backend(probabilities)
        # Prompt IDs 0,1; answer IDs 2,3. The prompt's 0->1 transition has a
        # different probability and would make inclusion/off-by-one errors fail.
        nll = backend.score([0, 1, 2, 3], answer_start=2)
        self.assertAlmostEqual(nll, -math.log(0.7) - math.log(0.8))
        self.assertEqual([targets for _, targets in calls], [[2, 3]])
        self.assertEqual(inputs[0]["input_ids"].values, [[0, 1, 2, 3]])

    def test_chunk_boundary_scores_each_answer_token_exactly_once(self):
        answer = [index % 4 for index in range(130)]
        ids = [3, 2] + answer
        probabilities = [[0.1, 0.2, 0.3, 0.4] for _ in ids]
        backend, calls, _ = self.backend(probabilities)
        nll = backend.score(ids, answer_start=2)
        expected = sum(-math.log(probabilities[index + 1][token])
                       for index, token in enumerate(answer))
        self.assertAlmostEqual(nll, expected)
        self.assertEqual([len(targets) for _, targets in calls], [128, 2])
        self.assertEqual([token for _, targets in calls for token in targets], answer)


class PPLFileTests(unittest.TestCase):
    def setUp(self):
        # Atomic replacement is available inside the explicit writable workspace.
        self.temporary = tempfile.TemporaryDirectory(prefix=".ppl-test-", dir=ROOT)
        if not Path(self.temporary.name).resolve().is_relative_to(ROOT):
            raise AssertionError("temporary directory escaped workspace")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.reference = self.root / "reference"
        self.source_model = self.root / "student"
        for directory in (self.reference, self.source_model):
            directory.mkdir()
            (directory / "config.json").write_text(
                json.dumps({"model_type": "llama", "max_position_embeddings": 128}), encoding="utf-8")
            (directory / "tokenizer.json").write_text("{}", encoding="utf-8")
            (directory / "tokenizer_config.json").write_text("{}", encoding="utf-8")
        (self.reference / "model.safetensors").write_bytes(b"offline fake model")

    def row(self, sample_id="one", answer="a", prompt="Question: "):
        return {"id": sample_id, "prompt": prompt, "answer": answer,
                "model_path": str(self.source_model),
                "generation": {"max_prompt_tokens": 2048, "temperature": 0.7}}

    def write_rows(self, name, rows):
        path = self.root / name
        path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
        return path

    def config(self, **overrides):
        values = {"model_path": self.reference, "device": "cpu", "dtype": "float32"}
        values.update(overrides)
        return ppl.PPLConfig(**values)

    def evaluate(self, sources, backend=None, config=None):
        backend = backend or KnownLikelihoodBackend()
        with patch.object(ppl, "_load_backend", return_value=backend) as loader, \
                patch.object(ppl, "_load_tokenizer", return_value=CharacterTokenizer()):
            result = ppl.evaluate_ppl_files(sources, config or self.config())
        return result, backend, loader.call_count


class PromptBoundaryTests(PPLFileTests):
    def test_prompt_tokens_do_not_enter_answer_scoring_and_bos_is_kept(self):
        tokenizer = CharacterTokenizer()
        ids, answer_start, _ = ppl.prepare_sample("Long prompt", "ab", tokenizer, 128, "error")
        self.assertEqual(ids[0], tokenizer.bos_token_id)
        self.assertEqual(ids[answer_start:], tokenizer.encode("ab", add_special_tokens=False))
        self.assertEqual(ids[:answer_start], tokenizer.encode("Long prompt", add_special_tokens=True))
        self.assertGreater(answer_start, 0)

    def test_first_answer_token_is_scorable_even_with_empty_prompt(self):
        tokenizer = CharacterTokenizer()
        ids, answer_start, _ = ppl.prepare_sample("", "a", tokenizer, 128, "error")
        self.assertEqual(ids, [tokenizer.bos_token_id, ord("a") + 10])
        self.assertEqual(answer_start, 1)

    def test_original_generation_prompt_uses_source_tokenizer_and_prefix_budget(self):
        from wm_test.generate_compare_score import render_prompt

        tokenizer = CharacterTokenizer()
        messages = [{"role": "user", "content": "A long prompt whose suffix is removed"}]
        row = self.row(prompt=messages)
        row["generation"]["max_prompt_tokens"] = 12
        restored, metadata = ppl.restore_generation_prompt(row, tokenizer)
        self.assertEqual(restored, render_prompt(tokenizer, messages, 12))
        self.assertEqual(restored, "[user]A long")
        self.assertNotIn("suffix", restored)

    def test_saved_wn_no_truncation_metadata_must_match_reconstructed_prompt(self):
        tokenizer = CharacterTokenizer()
        row = self.row(prompt=[{"role": "user", "content": "Long question"}])
        row["generation"].update(prompt_truncated=False, max_prompt_tokens=5)
        with self.assertRaisesRegex(ValueError, "prompt_truncated=False"):
            ppl.restore_generation_prompt(row, tokenizer)
        row["generation"]["max_prompt_tokens"] = 128
        row["generation"]["prompt_tokens"] = 1
        with self.assertRaisesRegex(ValueError, "prompt_tokens"):
            ppl.restore_generation_prompt(row, tokenizer)
        row["generation"]["prompt_tokens"] = len(tokenizer.apply_chat_template(row["prompt"]))
        text, metadata = ppl.restore_generation_prompt(row, tokenizer)
        self.assertEqual(text, tokenizer.apply_chat_template(row["prompt"]))
        self.assertFalse(metadata["source_prompt_truncated"])

    def test_reference_overflow_fails_or_removes_only_prompt_without_losing_answer(self):
        tokenizer = CharacterTokenizer()
        with self.assertRaises(ValueError):
            ppl.prepare_sample("12345678", "ab", tokenizer, 6, "error")
        ids, answer_start, _ = ppl.prepare_sample("12345678", "ab", tokenizer, 6, "truncate_prompt")
        self.assertLessEqual(len(ids), 6)
        self.assertEqual(ids[answer_start:], tokenizer.encode("ab", add_special_tokens=False))
        self.assertGreaterEqual(answer_start, 1)
        with self.assertRaises(ValueError):
            ppl.prepare_sample("x", "a" * 10, tokenizer, 6, "truncate_prompt")


class LikelihoodAndCacheTests(PPLFileTests):
    def test_overall_ppl_uses_all_answer_tokens_not_mean_of_per_answer_ppl(self):
        source = self.write_rows("answers.jsonl", [self.row("one", "a"), self.row("two", "bbb")])
        before = source.read_bytes()
        result, backend, loads = self.evaluate({"kgw": source})
        summary = result["files"]["kgw"]
        self.assertEqual(loads, 1)
        self.assertEqual(summary["scored_tokens"], 4)
        self.assertAlmostEqual(summary["total_nll"], math.log(2) + 3 * math.log(4))
        self.assertAlmostEqual(summary["token_weighted_ppl"], 2 ** 1.75)
        self.assertNotAlmostEqual(summary["token_weighted_ppl"], (2 + 4) / 2)
        per_sample = [row for line in Path(summary["per_sample_file"]).read_text(
            encoding="utf-8").splitlines() if line.strip()
            for row in [json.loads(line)] if row.get("type") == "sample"]
        self.assertEqual([row["scored_tokens"] for row in per_sample], [1, 3])
        self.assertAlmostEqual(per_sample[0]["ppl"], 2)
        self.assertAlmostEqual(per_sample[1]["ppl"], 4)
        self.assertEqual(source.read_bytes(), before)

    def test_reference_loaded_once_for_both_groups_and_cached_run_loads_nothing(self):
        kgw = self.write_rows("kgw.jsonl", [self.row("one", "a")])
        clean = self.write_rows("clean.jsonl", [self.row("one", "b")])
        sources = {"kgw": kgw, "clean": clean}
        with contextlib.redirect_stderr(io.StringIO()) as first_progress:
            result, backend, loads = self.evaluate(sources)
        self.assertEqual(loads, 1)
        self.assertEqual(len(backend.calls), 2)
        self.assertIn("kgw", first_progress.getvalue())
        self.assertIn("clean", first_progress.getvalue())
        self.assertIn("1/1", first_progress.getvalue())
        with contextlib.redirect_stderr(io.StringIO()) as cached_progress:
            cached, backend, loads = self.evaluate(sources)
        self.assertEqual(loads, 0)
        self.assertEqual(len(backend.calls), 0)
        self.assertTrue(all(summary["cache_reused"] for summary in cached["files"].values()))
        self.assertIn("cache", cached_progress.getvalue().lower())
        self.assertEqual(cached["files"]["kgw"]["token_weighted_ppl"],
                         result["files"]["kgw"]["token_weighted_ppl"])

    def test_input_and_scoring_config_changes_invalidate_cache_without_changing_source(self):
        source = self.write_rows("answers.jsonl", [self.row("one", "a")])
        self.evaluate({"kgw": source})
        self.write_rows("answers.jsonl", [self.row("one", "bb")])
        before = source.read_bytes()
        changed, _, loads = self.evaluate({"kgw": source})
        self.assertEqual(loads, 1)
        self.assertFalse(changed["files"]["kgw"]["cache_reused"])
        self.assertAlmostEqual(changed["files"]["kgw"]["token_weighted_ppl"], 4)
        changed_config, _, loads = self.evaluate({"kgw": source}, config=self.config(max_length=64))
        self.assertEqual(loads, 1)
        self.assertFalse(changed_config["files"]["kgw"]["cache_reused"])
        self.assertEqual(source.read_bytes(), before)

    def test_reference_tokenizer_changes_invalidate_cached_result(self):
        source = self.write_rows("answers.jsonl", [self.row()])
        self.evaluate({"kgw": source})
        (self.reference / "tokenizer_config.json").write_text('{"version": 2}', encoding="utf-8")
        result, _, loads = self.evaluate({"kgw": source})
        self.assertEqual(loads, 1)
        self.assertFalse(result["files"]["kgw"]["cache_reused"])

    def test_generation_tokenizer_changes_invalidate_cached_result(self):
        source = self.write_rows("answers.jsonl", [self.row(prompt=[{"role": "user", "content": "Question"}])])
        self.evaluate({"kgw": source})
        before = source.read_bytes()
        (self.source_model / "tokenizer_config.json").write_text('{"chat_template": "changed"}', encoding="utf-8")
        result, _, loads = self.evaluate({"kgw": source})
        self.assertEqual(loads, 1)
        self.assertFalse(result["files"]["kgw"]["cache_reused"])
        self.assertEqual(source.read_bytes(), before)

    def test_empty_answer_is_reported_and_not_scored_or_counted_in_denominator(self):
        source = self.write_rows("answers.jsonl", [self.row("empty", ""), self.row("valid", "a")])
        result, backend, _ = self.evaluate({"kgw": source})
        summary = result["files"]["kgw"]
        self.assertEqual(summary["samples"], 2)
        self.assertEqual(summary["valid_samples"], 1)
        self.assertEqual(summary["skipped_empty_answers"], 1)
        self.assertEqual(summary["scored_tokens"], 1)
        self.assertEqual(len(backend.calls), 1)
        self.assertAlmostEqual(summary["token_weighted_ppl"], 2)

    def test_nonfinite_loss_is_explicit_and_does_not_contaminate_summary_json(self):
        source = self.write_rows("answers.jsonl", [self.row("bad", "b"), self.row("good", "a")])
        backend = KnownLikelihoodBackend()
        original = backend.score
        backend.score = lambda ids, start: float("nan") if ids[start:] == [ord("b") + 10] else original(ids, start)
        result, _, _ = self.evaluate({"kgw": source}, backend=backend)
        summary = result["files"]["kgw"]
        self.assertEqual(summary["nonfinite_samples"], 1)
        self.assertEqual(summary["valid_samples"], 1)
        self.assertEqual(summary["scored_tokens"], 1)
        self.assertAlmostEqual(summary["token_weighted_ppl"], 2)
        self.assertEqual(summary["status"], "partial_failure")
        self.assertFalse(summary["complete"])
        encoded = json.dumps(result, allow_nan=False)
        self.assertNotIn("NaN", encoded)
        rows = [row for line in Path(summary["per_sample_file"]).read_text(
            encoding="utf-8").splitlines() if line.strip()
            for row in [json.loads(line)] if row.get("type") == "sample"]
        self.assertEqual(rows[0]["status"], "nonfinite_loss")
        self.assertIsNone(rows[0]["nll_sum"])
        self.assertIsNone(rows[0]["ppl"])


class EvaluatorIntegrationTests(PPLFileTests):
    def test_enabled_and_disabled_runs_both_append_history_without_regeneration(self):
        from wm_test import evaluate_compare_metrics as evaluator
        from tests.test_compare_detection import answer_row

        kgw = self.write_rows("kgw.jsonl", [answer_row("one", "kgw", gamma=0.5, delta=3)])
        clean = self.write_rows("clean.jsonl", [answer_row("one", "clean", gamma=0.5, delta=3)])
        # Use a real PPL payload, but keep this CLI test independent of scoring.
        known = self.write_rows("known.jsonl", [self.row("one", "a")])
        payload, _, _ = self.evaluate({"kgw": known, "clean": known})
        history = self.root / "history.md"
        history.write_text("Existing history stays here.\n", encoding="utf-8")
        # The ordinary evaluate command must enable PPL without PPL arguments.
        args = evaluator.parse_args([
            "--kgw-file", str(kgw), "--clean-file", str(clean), "--output", str(history),
            "--dolly-reference-file", str(self.root / "human.jsonl"),
            "--teacher-clean-reference-file", str(self.root / "teacher.jsonl"),
            "--score-device", "cpu",
        ])
        self.assertTrue(args.ppl)
        disabled = evaluator.parse_args(["--no-ppl"]).ppl
        self.assertFalse(disabled)
        rouge = {"mean": 0.7, "num_samples": 1, "reference_file": "offline-reference"}
        p_records = [{"p_value_raw": 0.5, "p_value_dedup": 0.5}]
        before = kgw.read_bytes(), clean.read_bytes()
        with contextlib.ExitStack() as stack:
            stack.enter_context(patch.object(evaluator, "parse_args", return_value=args))
            stack.enter_context(patch.object(evaluator, "evaluate_dolly_rouge", return_value=rouge))
            stack.enter_context(patch.object(evaluator, "evaluate_teacher_clean_rouge", return_value=rouge))
            stack.enter_context(patch.object(evaluator, "load_pvalue_records", return_value=(p_records, self.root / "p.jsonl")))
            stack.enter_context(patch.object(evaluator, "load_grouped_pvalues", return_value=({}, self.root / "g.json")))
            stack.enter_context(patch.object(evaluator, "summarize_grouped", return_value={}))
            stack.enter_context(patch.object(evaluator, "write_grouped_summary"))
            stack.enter_context(patch.object(evaluator, "load_nonrepetitive_grouped_pvalues", return_value=({}, self.root / "n.json")))
            stack.enter_context(patch.object(evaluator, "summarize_nonrepetitive_grouped", return_value={}))
            stack.enter_context(patch.object(evaluator, "write_nonrepetitive_grouped_summary"))
            calculate = stack.enter_context(patch.object(evaluator, "evaluate_ppl_files", return_value=payload))
            stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
            evaluator.main()
            args.ppl = disabled
            evaluator.main()
        self.assertEqual(calculate.call_count, 1)
        self.assertEqual(calculate.call_args.args[0], {"kgw": kgw.resolve(), "clean": clean.resolve()})
        scoring_config = calculate.call_args.args[1]
        self.assertEqual(scoring_config.model_path, Path("/shared/public_models/Llama-3-8B"))
        self.assertEqual(scoring_config.generation_tokenizer, Path("/shared/public_models/Qwen2.5-0.5B"))
        self.assertEqual((scoring_config.device, scoring_config.dtype), ("cuda", "bfloat16"))
        text = history.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("Existing history stays here.\n"))
        self.assertEqual(text.count("## 评估记录"), 2)
        self.assertIn('"enabled": true', text)
        self.assertIn('"enabled": false', text)
        self.assertIn("token_weighted_ppl", text)
        documents = [json.loads(block.split("\n```", 1)[0])
                     for block in text.split("```json\n")[1:]]
        runs = [document for document in documents if "ppl" in document]
        self.assertEqual(len(runs), 2)
        self.assertEqual(runs[0]["ppl"]["configuration"]["model_path"], str(self.reference))
        self.assertFalse(runs[1]["ppl"]["enabled"])
        self.assertEqual((kgw.read_bytes(), clean.read_bytes()), before)


if __name__ == "__main__":
    unittest.main()
