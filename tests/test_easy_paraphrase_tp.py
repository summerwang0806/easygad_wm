"""CPU checks for the easy/fast student TP baseline.

No torch or Transformers is imported: a fake tokenizer and scripted generator
exercise the real cleanup, acceptance, retry, audit and resume paths.
"""

from dataclasses import replace
import io
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from baseline_acl import easy_paraphrase_tp as easy
from baseline_acl import paraphrase_tp as tp
from baseline_acl import paraphrase_up as up

try:
    import pyarrow as pa
    import pyarrow.parquet as pq
except ImportError:
    pa = pq = None


class Tokenizer:
    chat_template = None
    pad_token_id = None
    eos_token_id = 99

    def encode(self, text, add_special_tokens=True):
        ids = [11 + (ord(ch) % 997) for ch in text]
        return ([1] + ids) if add_special_tokens else ids

    def decode(self, ids, **kwargs):
        self.decoded_ids = list(ids)
        return "A complete rewritten answer."

    def __len__(self):
        return 100000


SOURCES = [
    "The first source answer explains the topic clearly.",
    "The second source answer mentions two facts and one number: 42.",
    "The third source answer is about a small test.",
    "The fourth source answer will never be rewritten.",
    "The fifth source answer has a repetitive rewrite attempt.",
    "The sixth source answer should stay unchanged.",
    "The seventh source answer only triggers instruction echo.",
]


class PolicyTests(unittest.TestCase):
    def setUp(self):
        self.config = tp.GenerationConfig(max_input_tokens=5000, max_new_tokens=100, context_window=10000,
                                          on_failure="keep-original", generation_policy="efficient-v1")

    def test_cleanup_strips_echoed_scaffolding_and_keeps_plain_text(self):
        prompt = tp.render_prompt(Tokenizer(), SOURCES[2], self.config)
        echoed = (f"{tp.INSTRUCTION}\n\n<source_answer>\n{SOURCES[2]}\n</source_answer>\n\n"
                  f"Rewritten answer:\nReal rewrite.")
        self.assertEqual(easy.clean_output(echoed, prompt), ("Real rewrite.", ["cut_echoed_source_block",
                                                                              "cut_echoed_template"]))
        self.assertEqual(easy.clean_output(f"Rewritten answer:\nTrimmed.\n</source_answer>", prompt),
                         ("Trimmed.", ["cut_echoed_template"]))
        self.assertEqual(easy.clean_output(SOURCES[2], prompt), (SOURCES[2], []))
        self.assertEqual(easy.clean_output(tp.INSTRUCTION, prompt),
                         ("", ["cut_instruction_echo", "empty_after_cleanup"]))
        self.assertEqual(easy.clean_output("", prompt), ("", ["empty_generation"]))

    def test_only_empty_text_is_a_retry_trigger(self):
        prepared = tp.prepare_response(Tokenizer(), SOURCES[0], self.config)
        for text, reason, notes in (("A changed answer.", "length", []),
                                    (SOURCES[0], "stop", []),
                                    ("A trimmed answer.", "early_stop", ["repetition_loop"]),
                                    ("Here is the rewritten answer: text", "stop", [])):
            with self.subTest(reason=reason):
                raw = up.GeneratedResponse(text, reason, 5, issues=notes)
                candidate = easy.generate_response(prepared, raw, self.config, 0, 1)
                self.assertEqual(easy.candidate_issues(candidate, SOURCES[0], self.config), [])
                self.assertEqual(easy.validate_audit(candidate, prepared, Tokenizer(), self.config, 0, 1), [])
        empty = easy.generate_response(prepared, up.GeneratedResponse("", "stop", 0), self.config, 0, 1)
        self.assertEqual(easy.candidate_issues(empty, SOURCES[0], self.config), ["empty_output"])

    def test_notes_record_weak_acceptance_reasons(self):
        prepared = tp.prepare_response(Tokenizer(), SOURCES[0], self.config)
        truncated = easy.generate_response(prepared, up.GeneratedResponse("Partial", "length", 3),
                                           self.config, 0, 1)
        self.assertIn("truncated_at_budget", truncated.windows[0]["notes"])
        unchanged = easy.generate_response(prepared, up.GeneratedResponse(SOURCES[0], "stop", 9),
                                           self.config, 0, 1)
        self.assertIn("unchanged_source_answer", unchanged.windows[0]["notes"])
        repeated = easy.generate_response(prepared, up.GeneratedResponse("Same.", "early_stop", 2,
                                                                         issues=["repetition_loop"]),
                                          self.config, 0, 1)
        self.assertIn("repetition_loop", repeated.windows[0]["notes"])

    def test_audit_is_recomputed_from_raw_text_and_tampering_is_rejected(self):
        prepared = tp.prepare_response(Tokenizer(), SOURCES[2], self.config)
        echo = (f"{tp.INSTRUCTION}\n\n<source_answer>\n{SOURCES[2]}\n</source_answer>\n\n"
                f"Rewritten answer:\nA clean rewrite.")
        candidate = easy.generate_response(prepared, up.GeneratedResponse(echo, "stop", 40), self.config, 4, 2)
        self.assertEqual(candidate.text, "A clean rewrite.")
        self.assertEqual(easy.validate_audit(candidate, prepared, Tokenizer(), self.config, 4, 2), [])
        candidate.windows[0]["prompt_sha256"] = "tampered"
        self.assertIn("generation_audit_mismatch",
                      easy.validate_audit(candidate, prepared, Tokenizer(), self.config, 4, 2))

    def test_repetition_tail_detection_and_trimming(self):
        self.assertEqual(easy.repeated_tail_width([1, 2, 1, 2, 1, 2]), 2)
        self.assertEqual(easy.trim_repeated_tail([5, 9, 7, 9, 7, 9, 7], 2), [5])
        sentence = [1, 2, 3, 4, 5, 6, 7, 8]
        self.assertEqual(easy.trim_repeated_tail(sentence * 3, 8), sentence)
        self.assertEqual(easy.repeated_tail_width([9, 8, 7, 6, 5, 4]), 0)
        self.assertEqual(easy.trim_repeated_tail([1, 2, 3], 5), [1, 2, 3])


class EntryTests(unittest.TestCase):
    def argv(self, *extra):
        return ["--input", "train.parquet", "--rules", "rules.json", "--model", "qwen", *extra]

    def test_cli_defaults_are_the_easy_policy(self):
        args = easy.parse_args(self.argv("--inspect"))
        self.assertEqual(args.tokenizer, args.model)
        self.assertEqual((args.max_attempts, args.on_failure, args.generation_policy),
                         (3, "keep-original", "efficient-v1"))
        self.assertEqual((args.inverse_strength, args.max_new_tokens, args.prompt_mode),
                         (2.5, 4096, "completion"))
        for extra in (("--max-attempts", "4"), ("--on-failure", "drop")):
            with self.subTest(extra=extra), patch("sys.stderr", new_callable=io.StringIO), \
                 self.assertRaises(SystemExit):
                easy.parse_args(self.argv("--inspect", *extra))

    def test_rules_heldout_and_model_assets_are_protected(self):
        for args in (easy.parse_args(self.argv("--output", "rules.json")),
                     easy.parse_args(self.argv("--output", "qwen/tp.parquet")),
                     easy.parse_args(["--input", "test.parquet", "--rules", "rules.json",
                                      "--model", "qwen", "--inspect"])):
            with self.assertRaises(ValueError):
                tp.validate_attack_paths(args)

    def test_attack_identity_marks_easy_policy(self):
        args = easy.parse_args(self.argv("--inspect"))
        rules = SimpleNamespace(tokenizer={"fingerprint": "f"}, document={"provenance": {}})
        attack = easy.attack_identity(args, rules, "a" * 64)
        self.assertEqual(attack["method"], easy.METHOD)
        self.assertEqual(attack["acceptance_policy"], easy.POLICY)
        self.assertEqual(attack["paraphraser_model_role"], "original_student_O")

    def test_policy_document_reports_bounded_attempts(self):
        document = easy.policy_document(tp.GenerationConfig(max_attempts=2))
        self.assertEqual(document["retry_triggers"], ["empty_output"])
        self.assertEqual(document["max_attempts"], 2)
        self.assertEqual(document["retries_after_first_attempt"], 1)


class GenerationTests(unittest.TestCase):
    class Tensor:
        def __init__(self, values):
            self.values = values

        def __getitem__(self, index):
            return GenerationTests.Tensor(self.values[index])

        def tolist(self):
            return self.values

    class Inference:
        def __enter__(self):
            return None

        def __exit__(self, *args):
            return None

    class Ids:
        def __init__(self, values):
            self.values = values

        @property
        def shape(self):
            return (1, len(self.values))

        def __getitem__(self, key):
            row, column = key
            assert row == 0
            return GenerationTests.Slice(self.values[column])

    class Slice:
        def __init__(self, values):
            self.values = values

        def tolist(self):
            return self.values

    def test_tail_guard_stops_only_after_three_repeated_blocks(self):
        prompt_length = 3
        guard = easy.EasyTailGuard(prompt_length)
        self.assertFalse(guard(self.Ids([0, 0, 0] + [5] * 31)))
        self.assertFalse(guard(self.Ids([0, 0, 0] + list(range(100, 148)))))
        self.assertFalse(guard.reason)
        self.assertTrue(guard(self.Ids([0, 0, 0] + [7, 8] * 40)))
        self.assertEqual((guard.reason, guard.repeat_width), ("repetition_loop", 2))

    def test_causal_backend_uses_row_budget_and_accepts_length(self):
        tokenizer = Tokenizer()
        config = tp.GenerationConfig(max_input_tokens=5000, max_new_tokens=100, context_window=10000,
                                     on_failure="keep-original", generation_policy="efficient-v1")
        source = SOURCES[0]
        prepared = tp.prepare_response(tokenizer, source, config)
        ids = easy.prompt_ids(tokenizer, prepared["prompt"], config)
        calls = {}

        def generate(**kwargs):
            calls.update(kwargs)
            return self.Tensor([ids + [4, 7]])

        generator = easy.EasyStudentGenerator.__new__(easy.EasyStudentGenerator)
        generator.tokenizer, generator.config = tokenizer, config
        generator.eos_ids, generator.logits_processor = {99}, "direct processor"
        generator.torch = SimpleNamespace(manual_seed=lambda seed: None, tensor=lambda value, **kwargs: value,
                                          long="long", ones_like=lambda value: "mask",
                                          inference_mode=self.Inference)
        generator.model = SimpleNamespace(generate=generate)
        candidate = generator.generate([prepared], [0], [1])[0]
        self.assertEqual(calls["max_new_tokens"], easy.output_budget(prepared["source_tokens"], config))
        self.assertEqual(calls["forced_eos_token_id"], None)
        self.assertEqual(calls["logits_processor"], ["direct processor"])
        self.assertIsInstance(calls["stopping_criteria"][0], easy.EasyTailGuard)
        self.assertEqual(tokenizer.decoded_ids, [4, 7])
        self.assertEqual((candidate.finish_reason, candidate.output_tokens), ("length", 2))
        self.assertEqual(candidate.issues, [])
        self.assertEqual(candidate.text, "A complete rewritten answer.")
        self.assertIn("truncated_at_budget", candidate.windows[0]["notes"])


@unittest.skipIf(pa is None, "pyarrow is required for Parquet checks")
class DataContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source, self.output = self.root / "train.parquet", self.root / "easy.parquet"
        self.source_texts = list(SOURCES)
        self.table = pa.table({
            "id": [f"id-{index}" for index in range(len(self.source_texts))],
            "content": ["question"] * len(self.source_texts),
            "teacher_response": self.source_texts,
            "category": ["qa"] * len(self.source_texts),
            "grounded": [True] * len(self.source_texts),
            "flaw": [None] * len(self.source_texts),
            "agreement": [None] * len(self.source_texts),
        }).replace_schema_metadata({b"source": b"easy-source"})
        pq.write_table(self.table, self.source)
        self.config = tp.GenerationConfig(max_input_tokens=5000, max_new_tokens=100, context_window=10000,
                                          on_failure="keep-original", generation_policy="efficient-v1")
        args = SimpleNamespace(inverse_strength=2.5)
        rules = SimpleNamespace(tokenizer={"fingerprint": "f"}, document={"provenance": {}})
        self.identity = {"model": "fake-local-original-student",
                         "attack": easy.attack_identity(args, rules, "a" * 64)}

    def checkpoint(self, name="easy"):
        return self.output.with_suffix(".parquet.progress.jsonl")

    def scripted_factory(self, choose, calls, config=None):
        config = config or self.config
        tokenizer = Tokenizer()

        class ScriptedGenerator:
            def generate(self, rows, indices, attempts):
                results = []
                for row, index, attempt in zip(rows, indices, attempts, strict=True):
                    calls.append((index, attempt, up.generation_seed(config.seed, index, attempt)))
                    results.append(easy.generate_response(row, choose(row, index, attempt),
                                                          config, index, attempt))
                return results

        return ScriptedGenerator

    def run_job(self, factory=None, config=None, **kwargs):
        config = config or self.config
        return easy.run_paraphrasing(self.source, self.output, config, Tokenizer(),
                                     factory or (lambda: self.fail("no generation expected")),
                                     self.identity, **kwargs)

    def choose_one(self, calls):
        def choose(row, index, attempt):
            if index == 0:
                return up.GeneratedResponse("A short paraphrase of the first answer.", "stop", 8)
            if index == 1:
                return up.GeneratedResponse("This rewrite stops at the token budget", "length", 9)
            if index == 2:
                echo = (f"{tp.INSTRUCTION}\n\n<source_answer>\n{SOURCES[2]}\n</source_answer>\n\n"
                        f"Rewritten answer:\nA clean rewrite of the third answer.")
                return up.GeneratedResponse(echo, "stop", 40)
            if index == 3:
                return up.GeneratedResponse("", "stop", 0)
            if index == 4:
                return up.GeneratedResponse("Repeated sentence. Repeated sentence. Repeated sentence.",
                                            "early_stop", 6, issues=["repetition_loop"])
            if index == 5:
                return up.GeneratedResponse(SOURCES[5], "stop", 11)
            return up.GeneratedResponse(tp.INSTRUCTION, "stop", 12)
        return choose

    def test_first_nonempty_rewrite_is_accepted_and_empty_rows_keep_source(self):
        calls = []
        report = self.run_job(factory=self.scripted_factory(self.choose_one(calls), calls))
        expected = ["A short paraphrase of the first answer.", "This rewrite stops at the token budget",
                    "A clean rewrite of the third answer.", SOURCES[3],
                    "Repeated sentence. Repeated sentence. Repeated sentence.", SOURCES[5], SOURCES[6]]
        self.assertEqual(pq.read_table(self.output)["teacher_response"].to_pylist(), expected)
        self.assertEqual([index for index, _, _ in calls].count(3), 3)
        self.assertEqual([index for index, _, _ in calls].count(6), 3)
        self.assertEqual([index for index, _, _ in calls].count(0), 1)
        self.assertEqual(report["status_counts"], {"ok": 5, "fallback": 2})
        self.assertEqual(report["fallback_rows"], [3, 6])
        self.assertEqual(report["rejected_generation_attempts"], 4)
        self.assertEqual(report["truncated_accepted_count"], 1)
        self.assertEqual(report["repetition_trimmed_count"], 1)
        self.assertEqual(report["prompt_echo_cleaned_count"], 1)
        self.assertEqual(report["unchanged_accepted_count"], 1)
        self.assertEqual(report["output_tokens"]["max"], 40)
        for name in self.table.column_names:
            if name != "teacher_response":
                self.assertTrue(report["protected_columns_equal"][name])
        self.assertEqual(report["metadata"]["easy_policy"]["policy"], easy.POLICY)
        self.assertEqual(report["note_counts"]["truncated_at_budget"], 1)
        self.assertEqual(report["cleanup_counts"]["cut_echoed_template"], 1)
        self.assertTrue(report["schema_and_metadata_equal"])
        self.assertTrue(self.output.exists())

    def test_checkpoint_records_raw_text_and_cleanup(self):
        calls = []
        self.run_job(factory=self.scripted_factory(self.choose_one(calls), calls))
        entries = [json.loads(line) for line in self.checkpoint().read_text(encoding="utf-8").splitlines()]
        accepted = next(entry for entry in entries if entry.get("row_index") == 2)
        self.assertEqual(accepted["windows"][0]["raw_output_text"].count(tp.INSTRUCTION), 1)
        self.assertEqual(accepted["paraphrase"], "A clean rewrite of the third answer.")
        self.assertEqual(accepted["windows"][0]["cleanup_actions"], ["cut_echoed_source_block",
                                                                     "cut_echoed_template"])

    def test_crash_then_resume_only_generates_pending_rows(self):
        calls = []
        inner = self.scripted_factory(self.choose_one(calls), calls)

        class Crashing:
            def __init__(self):
                self.count = 0

            def generate(self, rows, indices, attempts):
                self.count += 1
                if self.count > 2:
                    raise RuntimeError("simulated crash")
                return inner().generate(rows, indices, attempts)

        factory = lambda: Crashing()
        with self.assertRaisesRegex(RuntimeError, "simulated crash"):
            self.run_job(factory=factory)
        self.assertFalse(self.output.exists())

        resumed = []
        report = self.run_job(resume=True, factory=self.scripted_factory(self.choose_one(resumed), resumed))
        self.assertNotIn(0, [index for index, _, _ in resumed])
        self.assertNotIn(1, [index for index, _, _ in resumed])
        self.assertEqual(resumed[0][0], 2)
        self.assertEqual(report["rows"], len(SOURCES))
        expected = ["A short paraphrase of the first answer.", "This rewrite stops at the token budget",
                    "A clean rewrite of the third answer.", SOURCES[3],
                    "Repeated sentence. Repeated sentence. Repeated sentence.", SOURCES[5], SOURCES[6]]
        self.assertEqual(pq.read_table(self.output)["teacher_response"].to_pylist(), expected)

    def test_torn_final_checkpoint_line_is_discarded(self):
        calls = []
        self.run_job(factory=self.scripted_factory(self.choose_one(calls), calls))
        self.output.unlink()
        with self.checkpoint().open("ab") as handle:
            handle.write(b'{"kind":"result","row_index":2')
        resumed = []
        report = self.run_job(resume=True, factory=lambda: self.fail("completed rows must not regenerate"))
        self.assertTrue(self.checkpoint().read_bytes().endswith(b"\n"))
        self.assertEqual(report["rows"], len(SOURCES))
        self.assertTrue(self.output.exists())

    def test_resume_with_different_config_is_refused(self):
        calls = []
        self.run_job(factory=self.scripted_factory(self.choose_one(calls), calls))
        self.output.unlink()
        with self.assertRaisesRegex(ValueError, "checkpoint metadata differs"):
            self.run_job(resume=True, config=replace(self.config, seed=7),
                         factory=lambda: self.fail("must not generate"))

    def test_max_attempts_two_retries_once_then_keeps_source(self):
        config = replace(self.config, max_attempts=2)
        calls = []
        report = self.run_job(config=config, factory=self.scripted_factory(self.choose_one(calls), calls, config))
        self.assertEqual([index for index, _, _ in calls].count(3), 2)
        self.assertEqual([index for index, _, _ in calls].count(6), 2)
        self.assertEqual(report["status_counts"], {"ok": 5, "fallback": 2})
        self.assertEqual(report["rejected_generation_attempts"], 2)

    def test_input_budget_violations_keep_source_without_loading_a_backend(self):
        config = replace(self.config, max_input_tokens=1)
        report = self.run_job(config=config)
        self.assertEqual(report["status_counts"], {"fallback": len(SOURCES)})
        self.assertEqual(pq.read_table(self.output)["teacher_response"].to_pylist(), self.source_texts)
        self.assertEqual(report["fallback_reasons"], {"full_prompt_exceeds_input_budget": len(SOURCES)})

    def test_preflight_reports_budget_fallbacks_but_stays_valid(self):
        config = replace(self.config, max_input_tokens=1)
        report = easy.preflight_source(self.source, Tokenizer(), config)
        self.assertTrue(report["valid"])
        self.assertEqual(report["budget_fallback_count"], len(SOURCES))
        self.assertEqual(report["easy_policy"]["policy"], easy.POLICY)

    def test_main_preflight_forces_easy_policy_without_model_or_cuda(self):
        tokenizer = Tokenizer()
        validated = []
        rules = SimpleNamespace(tokenizer={"fingerprint": "f"}, document={"provenance": {}},
                                validate_tokenizer=lambda actual: validated.append(actual))
        fake_transformers = SimpleNamespace(
            AutoConfig=SimpleNamespace(from_pretrained=lambda *args, **kwargs: SimpleNamespace(
                is_encoder_decoder=False, max_position_embeddings=1000)),
            AutoTokenizer=SimpleNamespace(from_pretrained=lambda *args, **kwargs: tokenizer))
        argv = ["--input", str(self.source), "--rules", str(self.root / "rules.json"), "--model", "original",
                "--max-input-tokens", "5000", "--max-new-tokens", "100",
                "--generation-policy", "legacy", "--on-failure", "keep-last", "--preflight"]
        with patch.dict(sys.modules, {"transformers": fake_transformers}), \
             patch.object(tp, "load_bound_rules", return_value=rules), \
             patch.object(tp, "validate_original_student"), patch.object(up, "asset_identity"), \
             patch.object(up, "file_sha256", return_value="h"), \
             patch.object(up, "probe_selected_gpus", side_effect=AssertionError("GPU")), \
             patch("sys.stdout", new_callable=io.StringIO) as output:
            report = easy.main(argv)
        self.assertTrue(report["valid"])
        self.assertEqual(report["method"], easy.METHOD)
        self.assertEqual(report["config"]["generation_policy"], "efficient-v1")
        self.assertEqual(report["config"]["on_failure"], "keep-original")
        self.assertEqual(report["config"]["max_attempts"], 3)
        self.assertEqual(report["config"]["context_window"], 1000)
        self.assertEqual(report["budget_fallback_count"], 0)
        self.assertEqual(validated, [tokenizer])
        self.assertIn("--generation-policy=legacy", output.getvalue())
        self.assertIn("--on-failure=keep-last", output.getvalue())

    def test_audit_publication_crash_is_recovered_without_regeneration(self):
        calls = []
        original_publish = up.publish_new_file
        publications = []

        def interrupt_after_audit(temporary, destination):
            publications.append(destination)
            if len(publications) == 2:
                raise RuntimeError("interrupt after audit")
            return original_publish(temporary, destination)

        with patch.object(up, "publish_new_file", side_effect=interrupt_after_audit), \
             self.assertRaisesRegex(RuntimeError, "interrupt after audit"):
            self.run_job(factory=self.scripted_factory(self.choose_one(calls), calls))
        audit = self.output.with_suffix(".parquet.audit.json")
        previous = audit.read_bytes()
        self.assertFalse(self.output.exists())
        report = self.run_job(resume=True, factory=lambda: self.fail("completed rows must not regenerate"))
        self.assertEqual(audit.read_bytes(), previous)
        self.assertEqual(report["output_sha256"], up.file_sha256(self.output))
        self.assertTrue(report["complete"])


if __name__ == "__main__":
    unittest.main()
