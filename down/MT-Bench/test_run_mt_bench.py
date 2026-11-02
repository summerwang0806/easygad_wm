"""Protocol tests: no model weights, GPU, Transformers, or network required."""
from __future__ import annotations

from contextlib import redirect_stdout
import copy
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("mt_bench_runner", HERE / "run_mt_bench.py")
mt = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mt)


def question(number=81, category="writing"):
    return {"question_id": number, "category": category, "turns": [f"Question {number}", "Follow up"]}


def prompts():
    templates = {
        "single-v1": "Q={question}\nA={answer}",
        "single-v1-multi-turn": "Q1={question_1}\nA1={answer_1}\nQ2={question_2}\nA2={answer_2}",
        "single-math-v1": "Q={question}\nR={ref_answer_1}\nA={answer}",
        "single-math-v1-multi-turn": "Q1={question_1}\nR1={ref_answer_1}\nA1={answer_1}\nQ2={question_2}\nR2={ref_answer_2}\nA2={answer_2}",
    }
    return {name: {"name": name, "type": "single", "output_format": "[[rating]]", "system_prompt": "Judge quality.", "prompt_template": template} for name, template in templates.items()}


def output(text, reason="stop"):
    return {"text": text, "finish_reason": reason, "prompt_tokens": 12, "completion_tokens": 3, "rendered_prompt": "rendered"}


def answer(q):
    return {"question_id": q["question_id"], "category": q["category"], "questions": q["turns"],
            "turns": ["Student first", "Student second"], "generation": [output("Student first"), output("Student second")]}


class FakeGenerator:
    def __init__(self, outputs, events=None, name="generator"):
        self.outputs = iter(outputs)
        self.calls = []
        self.events = events if events is not None else []
        self.name = name

    def check(self):
        self.events.append(self.name + ":check")
        return {"fake": True, "chat_template_present": True}

    def generate(self, messages, **settings):
        self.calls.append((copy.deepcopy(messages), settings))
        self.events.append(self.name + ":generate")
        return next(self.outputs)

    def close(self):
        self.events.append(self.name + ":close")


class ProtocolTests(unittest.TestCase):
    def test_rating_requires_one_final_in_range_score(self):
        self.assertEqual(mt.parse_rating("Reasoning. [[7.5]]\n"), 7.5)
        self.assertEqual(mt.parse_rating("[[10]]."), 10)
        for text in ("7", "[[0]]", "[[11]]", "[[8]] then [[9]]", "[[8]] more text", "[[nan]]", "[8]", "[[-1]]"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                mt.parse_rating(text)

    def test_missing_template_rejected_before_generation(self):
        generator = FakeGenerator([])
        with patch.object(generator, "check", return_value={"chat_template_present": False}):
            with self.assertRaisesRegex(ValueError, "chat_template"):
                mt.check_chat_generator(generator)
        self.assertEqual(generator.calls, [])

    def test_judge_gpu_visibility_and_path_do_not_change_student_cache_identity(self):
        manifest = {"files": {"question.jsonl": {"sha256": "questions"}}}
        with patch.object(mt, "model_fingerprint", return_value={"model": "fixture"}), \
                patch.object(mt, "tokenizer_fingerprint", return_value={"tokenizer": "fixture"}), \
                patch.dict("os.environ", {"CUDA_VISIBLE_DEVICES": "3"}):
            before = mt.generation_identity(manifest)
            with patch.dict("os.environ", {"CUDA_VISIBLE_DEVICES": "0,1"}), \
                    patch.object(mt, "JUDGE_MODEL_PATH", "another-judge"), \
                    patch.object(mt, "JUDGE_MAX_NEW_TOKENS", 4096):
                self.assertEqual(mt.generation_identity(manifest), before)

    def test_official_prompt_routing_and_reference_visibility(self):
        q = question(category="math")
        a = answer(q)
        refs = {81: {"choices": [{"turns": ["Reference first", "Reference second"]}]}}
        name, messages = mt.judge_messages(q, a, 2, prompts(), refs)
        self.assertEqual(name, "single-math-v1-multi-turn")
        for value in ("Student first", "Student second", "Reference first", "Reference second", "Follow up"):
            self.assertIn(value, messages[1]["content"])
        self.assertIn("evaluation data", messages[0]["content"])
        q["category"] = "writing"
        name, messages = mt.judge_messages(q, a, 1, prompts(), {})
        self.assertEqual(name, "single-v1")
        self.assertNotIn("Reference", messages[1]["content"])

    def test_student_second_turn_uses_own_first_answer_and_resume(self):
        q = question()
        fake = FakeGenerator([output("Own first"), output("Own second")])
        with tempfile.TemporaryDirectory(dir=HERE, prefix=".test-") as temporary:
            directory = Path(temporary)
            with redirect_stdout(io.StringIO()):
                saved = mt.generate_answers([q], directory, generator_factory=lambda: fake)
            self.assertEqual(fake.calls[0][0], [{"role": "user", "content": q["turns"][0]}])
            self.assertEqual(fake.calls[1][0], [{"role": "user", "content": q["turns"][0]}, {"role": "assistant", "content": "Own first"}, {"role": "user", "content": "Follow up"}])
            self.assertEqual(saved[81]["turns"], ["Own first", "Own second"])
            self.assertEqual(fake.events[-1], "generator:close")
            with redirect_stdout(io.StringIO()):
                resumed = mt.generate_answers([q], directory, generator_factory=lambda: self.fail("Resume must not load student"))
            mt.validate_answers([q], resumed)
            self.assertEqual(resumed, saved)

    def test_invalid_or_truncated_judge_outputs_remain_unscored(self):
        questions = [question(81), question(82)]
        answers = {q["question_id"]: answer(q) for q in questions}
        fake = FakeGenerator([output("Good [[8]]"), output("[[9]]", "length"), output("[[2]] or [[3]]"), output("Good [[6]]")])
        with tempfile.TemporaryDirectory(dir=HERE, prefix=".test-") as temporary:
            directory = Path(temporary)
            with redirect_stdout(io.StringIO()):
                judged = mt.judge_answers(questions, answers, prompts(), {}, directory, generator_factory=lambda: fake)
            self.assertEqual(set(judged), {"81:1", "82:2"})
            errors = mt.read_cache(directory / "judge_errors.jsonl", "key")
            self.assertEqual(set(errors), {"81:2", "82:1"})
            self.assertTrue(all("score" not in row for row in errors.values()))
            report = mt.summarize(questions, answers, judged, limited=True)
            self.assertFalse(report["complete"])
            self.assertIsNone(report["overall_score"])
            self.assertEqual(report["coverage"], 0.5)
            self.assertIsNone(report["categories"]["writing"]["score"])
            # Scores are bound to the exact answer and prompt, not just question ID.
            answers[81]["turns"][0] = "Changed first answer"
            with self.assertRaisesRegex(ValueError, "不匹配"):
                mt.judge_answers(questions, answers, prompts(), {}, directory, score_only=True)

    def test_complete_means_and_category_means(self):
        questions = [question(81), question(82, "math")]
        answers = {q["question_id"]: answer(q) for q in questions}
        judgments = {f"{qid}:{turn}": {"score": score, "turn": turn, "category": category}
                     for qid, category, scores in ((81, "writing", (6, 8)), (82, "math", (2, 4)))
                     for turn, score in enumerate(scores, 1)}
        summary = mt.summarize(questions, answers, judgments, limited=False)
        self.assertTrue(summary["complete"])
        self.assertEqual(summary["overall_score"], 5)
        self.assertEqual(summary["turns"]["1"]["score"], 4)
        self.assertEqual(summary["turns"]["2"]["score"], 6)
        self.assertEqual(summary["categories"]["writing"]["score"], 7)
        self.assertEqual(summary["categories"]["math"]["score"], 3)

    def test_data_downloader_validates_and_pins_all_assets(self):
        questions = [question(number) for number in range(81, 161)]
        rows = {"question.jsonl": questions, "judge_prompts.jsonl": list(prompts().values()), "reference_gpt4.jsonl": []}
        payloads = {mt.SOURCE_FILES[name]: ("\n".join(json.dumps(row) for row in data) + "\n").encode() for name, data in rows.items()}
        with tempfile.TemporaryDirectory(dir=HERE, prefix=".test-") as temporary, patch.object(mt, "DATA_DIR", Path(temporary)), patch.object(mt, "urlopen", side_effect=lambda url, **kwargs: io.BytesIO(payloads[url])):
            with redirect_stdout(io.StringIO()):
                mt.prepare_data()
            loaded, _, _, manifest = mt.load_data()
            self.assertEqual(len(loaded), 80)
            self.assertEqual(manifest["fastchat_commit"], mt.FASTCHAT_COMMIT)
            with (mt.DATA_DIR / "question.jsonl").open("a") as stream:
                stream.write("\n")
            with self.assertRaisesRegex(ValueError, "已变化"):
                mt.load_data()

    def test_default_flow_releases_student_before_judge_and_limit_is_whole_questions(self):
        events = []
        student = FakeGenerator([output("First"), output("Second")], events, "student")
        judge = FakeGenerator([output("[[8]]"), output("[[6]]")], events, "judge")
        with tempfile.TemporaryDirectory(dir=HERE, prefix=".test-") as temporary, patch.object(mt, "RESULTS_DIR", Path(temporary)), patch.object(mt, "MODEL_PATH", "student"), \
             patch.object(mt, "load_data", return_value=([question(81), question(82)], prompts(), {}, {})), \
             patch.object(mt, "generation_identity", return_value={"student": "fixture"}), \
             patch.object(mt, "judgment_identity", return_value={"judge": "fixture"}), \
             patch.object(mt, "student_generator", return_value=student), patch.object(mt, "judge_generator", return_value=judge):
            with redirect_stdout(io.StringIO()):
                self.assertEqual(mt.main(["--limit", "1"]), 0)
            self.assertLess(events.index("student:close"), events.index("judge:check"))
            self.assertEqual(len(student.calls), 2)
            self.assertEqual(len(judge.calls), 2)
            report_path = next(Path(temporary).rglob("summary.json"))
            report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertTrue(report["limited_run"])
            self.assertEqual(report["planned_turns"], 2)
            self.assertEqual(report["overall_score"], 7)
            with patch.object(mt, "student_generator", side_effect=AssertionError("No student in score-only")), patch.object(mt, "judge_generator", side_effect=AssertionError("No judge in score-only")), redirect_stdout(io.StringIO()):
                self.assertEqual(mt.main(["--score-only", "--limit", "1"]), 0)

    def test_wn_is_only_passed_to_student(self):
        with patch.object(mt, "LocalGenerator") as constructor, patch.object(mt, "WN_RULES_PATH", "rules.json"), patch.object(mt, "WN_STRENGTH", 2.5):
            mt.student_generator()
            self.assertEqual(constructor.call_args.kwargs["wn_rules_path"], "rules.json")
            self.assertEqual(constructor.call_args.kwargs["wn_strength"], 2.5)
            mt.judge_generator()
            self.assertNotIn("wn_rules_path", constructor.call_args.kwargs)
            self.assertNotIn("wn_strength", constructor.call_args.kwargs)


if __name__ == "__main__":
    unittest.main()
