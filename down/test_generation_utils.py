"""Offline inference-contract tests; no model weights or Transformers install."""
import importlib.util
from pathlib import Path
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import torch


SPEC = importlib.util.spec_from_file_location("generation_utils", Path(__file__).with_name("generation_utils.py"))
runtime = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runtime)


class FakeTokenizer:
    chat_template = "test-template"
    eos_token_id = 2
    pad_token_id = 0

    def apply_chat_template(self, messages, **kwargs):
        self.messages = messages
        self.options = kwargs
        return "rendered conversation"

    def __call__(self, prompt, **kwargs):
        self.tokenize_options = kwargs
        return {"input_ids": torch.tensor([[0, 1]]), "attention_mask": torch.tensor([[1, 1]])}

    def decode(self, ids, **kwargs):
        return "answer" if ids else ""


class FakeModel:
    config = SimpleNamespace()
    generation_config = SimpleNamespace(eos_token_id=[2, 3])

    def get_input_embeddings(self):
        return SimpleNamespace(weight=torch.zeros(1))

    def generate(self, **kwargs):
        self.options = kwargs
        scores = torch.tensor([[0.0, 5.0, 4.0, 0.0]])
        for processor in kwargs["logits_processor"]:
            scores = processor(kwargs["input_ids"], scores)
        chosen = int(scores.argmax(dim=1)[0])
        # EOS appended only if the output budget permits it.
        new = [chosen, 2] if kwargs["generation_config"].max_new_tokens > 1 else [chosen]
        return torch.cat([kwargs["input_ids"], torch.tensor([new])], dim=1)


class GenerationChecks(unittest.TestCase):
    def generator(self, **kwargs):
        result = runtime.LocalGenerator("unused", device="cpu", **kwargs)
        result._metadata = {}
        result._torch = torch
        result._tokenizer = FakeTokenizer()
        result._model = FakeModel()
        return result

    def fake_transformers(self):
        module = ModuleType("transformers")
        module.GenerationConfig = SimpleNamespace(from_model_config=lambda config: SimpleNamespace(eos_token_id=2))
        module.LogitsProcessorList = list
        return module

    def test_render_multi_turn_and_completion_excludes_prompt(self):
        model = self.generator()
        conversation = [{"role": "user", "content": "first"}, {"role": "assistant", "content": "own answer"},
                        {"role": "user", "content": "follow-up"}]
        with patch.dict("sys.modules", {"transformers": self.fake_transformers()}):
            output = model.generate(conversation, temperature=0.0, seed=123)
        self.assertEqual(model._tokenizer.messages, conversation)
        self.assertFalse(model._tokenizer.options["enable_thinking"])
        self.assertFalse(model._tokenizer.tokenize_options["truncation"])
        self.assertEqual(output["completion_tokens"], 2)
        self.assertEqual(output["finish_reason"], "stop")
        self.assertEqual(output["seed"], 123)
        config = model._model.options["generation_config"]
        self.assertFalse(config.do_sample)
        self.assertEqual(config.eos_token_id, [2, 3])
        self.assertEqual(config.repetition_penalty, 1.0)

    def test_wn_is_actually_applied_to_logits(self):
        plain = self.generator(max_new_tokens=1)
        attacked = self.generator(max_new_tokens=1)
        attacked.wn_strength = 2.0
        attacked._rules = SimpleNamespace(vocab_size=4, max_prefix=1, penalties=lambda context: {1: 1.0})
        with patch.dict("sys.modules", {"transformers": self.fake_transformers()}):
            first = plain.generate("question", temperature=0.0)
            second = attacked.generate("question", temperature=0.0)
        self.assertFalse(first["wn_enabled"])
        self.assertTrue(second["wn_enabled"])
        self.assertEqual(len(plain._model.options["logits_processor"]), 0)
        self.assertEqual(len(attacked._model.options["logits_processor"]), 1)
        self.assertEqual(first["finish_reason"], "length")
        self.assertEqual(second["finish_reason"], "stop")  # penalty changes argmax from 1 to EOS=2

    def test_overlong_prompt_or_context_fails_before_loading(self):
        model = self.generator(max_input_tokens=1)
        model._load = Mock()
        with self.assertRaisesRegex(ValueError, "no text was truncated"):
            model.generate("question")
        model._load.assert_not_called()
        model.max_input_tokens = 10
        model._context_limit = 3
        with self.assertRaisesRegex(ValueError, "exceeds model context"):
            model.generate("question", max_new_tokens=2)
        model._load.assert_not_called()

    def test_missing_chat_template_and_missing_wn_rules_fail(self):
        model = self.generator()
        model._tokenizer.chat_template = None
        with self.assertRaisesRegex(ValueError, "no chat_template"):
            model.generate([{"role": "user", "content": "question"}])
        with self.assertRaisesRegex(ValueError, "requires an estimated"):
            runtime.LocalGenerator("unused", wn_strength=2.5)


if __name__ == "__main__":
    unittest.main()
