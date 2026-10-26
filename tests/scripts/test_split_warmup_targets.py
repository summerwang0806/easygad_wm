"""CPU tests for separate discriminator and warmup SFT targets.

Extract the real helpers with AST so importing training dependencies is unnecessary.
NumPy supplies a small tensor double; no PyTorch, Transformers, models or GPU load.
"""

import ast
from pathlib import Path
from types import SimpleNamespace
import unittest

import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASET_SOURCE = PROJECT_ROOT / "verl/utils/dataset/rl_dataset.py"
ACTOR_SOURCE = PROJECT_ROOT / "verl/workers/actor/dp_actor.py"
FUNCTIONAL_SOURCE = PROJECT_ROOT / "verl/utils/torch_functional.py"


def load_functions(path, names, namespace):
    """Execute only selected, unchanged top-level functions from a source file."""
    parsed = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    functions = [node for node in parsed.body if isinstance(node, ast.FunctionDef) and node.name in names]
    found = {node.name for node in functions}
    if found != set(names):
        raise AssertionError(f"Missing helper functions in {path}: {set(names) - found}")
    future = ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0)
    module = ast.fix_missing_locations(ast.Module(body=[future, *functions], type_ignores=[]))
    exec(compile(module, str(path), "exec"), namespace)
    return namespace


class TensorDouble:
    """Only the CPU tensor operations used by the extracted helpers."""

    def __init__(self, value):
        self.value = np.asarray(value)

    def __getitem__(self, key):
        return TensorDouble(self.value[key])

    def __add__(self, other):
        return TensorDouble(self.value + other.value)

    def __sub__(self, other):
        return TensorDouble(self.value - other.value)

    @property
    def shape(self):
        return self.value.shape

    @property
    def ndim(self):
        return self.value.ndim

    @property
    def dtype(self):
        return self.value.dtype

    @property
    def device(self):
        return "cpu"

    def size(self, dimension):
        return self.value.shape[dimension]

    def long(self):
        return TensorDouble(self.value.astype(np.int64))

    def int(self):
        return TensorDouble(self.value.astype(np.int32))

    def unsqueeze(self, dimension):
        return TensorDouble(np.expand_dims(self.value, dimension))

    def cumsum(self, dim):
        return TensorDouble(np.cumsum(self.value, axis=dim))

    def eq(self, value):
        return TensorDouble(self.value == value)

    def to(self, dtype):
        return TensorDouble(self.value.astype(dtype))


def pad_tensor(tensor, widths, mode, value):
    if mode != "constant":
        raise AssertionError(f"Unexpected padding mode: {mode}")
    return TensorDouble(np.pad(tensor.value, ((0, 0), widths), constant_values=value))


TORCH_DOUBLE = SimpleNamespace(
    Tensor=TensorDouble,
    int64=np.int64,
    tensor=lambda value, device=None: TensorDouble(value),
    isin=lambda tensor, values: TensorDouble(np.isin(tensor.value, values.value)),
    cat=lambda tensors, dim: TensorDouble(np.concatenate([tensor.value for tensor in tensors], axis=dim)),
    arange=lambda start, stop, device=None: TensorDouble(np.arange(start, stop)),
)
FUNCTIONALS = load_functions(
    FUNCTIONAL_SOURCE,
    {"get_response_mask", "pad_sequence_to_length", "postprocess_data"},
    {"torch": TORCH_DOUBLE, "F": SimpleNamespace(pad=pad_tensor)},
)
BUILD_TARGETS = load_functions(
    DATASET_SOURCE,
    {"build_sft_response_tensors"},
    {"torch": TORCH_DOUBLE, "verl_F": SimpleNamespace(**FUNCTIONALS)},
)["build_sft_response_tensors"]


class DataProtoDouble:
    def __init__(self, batch):
        self.batch = batch

    def select(self, batch_keys):
        return DataProtoDouble({key: self.batch[key] for key in batch_keys})


SELECT_TARGETS = load_functions(
    ACTOR_SOURCE, {"select_warmup_sft_targets"}, {"DataProto": DataProtoDouble}
)["select_warmup_sft_targets"]


class TokenizerDouble:
    eos_token_id = 2

    def __call__(self, text, return_tensors, add_special_tokens):
        if return_tensors != "pt" or add_special_tokens is not False:
            raise AssertionError("SFT tokenization must follow existing teacher tokenization")
        ids = [int(token) for token in text.split()]
        return {"input_ids": TensorDouble([ids]), "attention_mask": TensorDouble([[1] * len(ids)])}


class TestWarmupTargetRouting(unittest.TestCase):
    fields = ("response", "input_ids", "attention_mask", "position_ids")

    def make_data(self):
        batch = {f"teacher_{name}": object() for name in self.fields}
        batch.update({f"sft_{name}": object() for name in self.fields})
        batch["responses"] = object()
        return DataProtoDouble(batch)

    def test_warmup_routes_para_without_mutating_discriminator_targets(self):
        data = self.make_data()
        original = data.batch.copy()
        routed = SELECT_TARGETS(data, "warmup")
        self.assertIsNot(routed, data)
        self.assertIsNot(routed.batch, data.batch)
        for name in self.fields:
            self.assertIs(routed.batch[f"teacher_{name}"], original[f"sft_{name}"])
            self.assertIs(data.batch[f"teacher_{name}"], original[f"teacher_{name}"])
        self.assertIs(routed.batch["responses"], original["responses"])

    def test_gad_and_seqkd_keep_original_teacher_targets(self):
        for stage in ("gad", "seqkd", "tlgad"):
            with self.subTest(stage=stage):
                data = self.make_data()
                self.assertIs(SELECT_TARGETS(data, stage), data)

    def test_no_optional_targets_retains_existing_warmup_behavior(self):
        data = DataProtoDouble({f"teacher_{name}": object() for name in self.fields})
        self.assertIs(SELECT_TARGETS(data, "warmup"), data)

    def test_any_incomplete_target_group_is_rejected(self):
        for missing in self.fields:
            with self.subTest(missing=missing):
                data = self.make_data()
                del data.batch[f"sft_{missing}"]
                with self.assertRaisesRegex(ValueError, "all four sft_.* tensors"):
                    SELECT_TARGETS(data, "warmup")

    def test_routing_precedes_uid_deduplication(self):
        source = ast.parse(ACTOR_SOURCE.read_text(encoding="utf-8"))
        actor = next(node for node in source.body if isinstance(node, ast.ClassDef) and node.name == "DataParallelPPOActor")
        update = next(node for node in actor.body if isinstance(node, ast.FunctionDef) and node.name == "update_policy")
        routing_calls = [node.lineno for node in ast.walk(update) if isinstance(node, ast.Call)
                         and isinstance(node.func, ast.Name) and node.func.id == "select_warmup_sft_targets"]
        dedup_calls = [node.lineno for node in ast.walk(update) if isinstance(node, ast.Call)
                       and isinstance(node.func, ast.Attribute) and node.func.attr == "deduplicate_by_uid"]
        self.assertEqual(len(routing_calls), 1)
        self.assertEqual(len(dedup_calls), 1)
        self.assertLess(routing_calls[0], dedup_calls[0])


class TestSFTResponseTensors(unittest.TestCase):
    def build(self, response="10 11", max_length=5, truncation="right", eos_token_id=None):
        return BUILD_TARGETS(
            TokenizerDouble(), response,
            TensorDouble([[0, 0, 8, 9]]),
            TensorDouble([[0, 0, 1, 1]]),
            TensorDouble([[0, 0, 0, 1]]),
            max_length, truncation, eos_token_id=eos_token_id,
        )

    def test_padding_mask_and_positions_match_rollout_teacher_convention(self):
        output = self.build()
        self.assertEqual(output["sft_response"].value.tolist(), [10, 11, 2, 2, 2])
        self.assertEqual(output["sft_input_ids"].value.tolist(), [0, 0, 8, 9, 10, 11, 2, 2, 2])
        self.assertEqual(output["sft_attention_mask"].value.tolist(), [0, 0, 1, 1, 1, 1, 1, 0, 0])
        self.assertEqual(output["sft_position_ids"].value.tolist(), [0, 0, 0, 1, 2, 3, 4, 5, 6])
        self.assertEqual(output["sft_response"].dtype, np.int64)
        self.assertTrue(all(tensor.ndim == 1 for tensor in output.values()))

    def test_first_embedded_eos_ends_mask_even_if_text_follows(self):
        output = self.build("10 2 11")
        self.assertEqual(output["sft_response"].value.tolist(), [10, 2, 11, 2, 2])
        self.assertEqual(output["sft_attention_mask"].value.tolist(), [0, 0, 1, 1, 1, 1, 0, 0, 0])

    def test_generation_config_single_eos_overrides_tokenizer_for_mask(self):
        output = self.build("10 99 11", eos_token_id=99)
        self.assertEqual(output["sft_response"].value.tolist(), [10, 99, 11, 2, 2])
        self.assertEqual(output["sft_attention_mask"].value.tolist(), [0, 0, 1, 1, 1, 1, 0, 0, 0])

    def test_generation_config_multiple_eos_ids_stop_at_first_matching_token(self):
        for response in ("10 99 11 100", "10 100 11 99"):
            with self.subTest(response=response):
                output = self.build(response, eos_token_id=[99, 100, 2])
                self.assertEqual(output["sft_attention_mask"].value.tolist(), [0, 0, 1, 1, 1, 1, 0, 0, 0])
                self.assertEqual(output["sft_response"].value.tolist()[-1], 2)

    def test_generation_eos_override_preserves_tokenizer_eos_padding(self):
        output = self.build(eos_token_id=99)
        self.assertEqual(output["sft_response"].value.tolist(), [10, 11, 2, 2, 2])
        # Preserve the existing teacher convention even if padding EOS is not
        # among the generation config's stopping tokens.
        self.assertEqual(output["sft_attention_mask"].value.tolist(), [0, 0, 1, 1, 1, 1, 1, 1, 1])

    def test_exact_length_target_without_eos_is_fully_attended(self):
        output = self.build("10 11 12 13 14")
        self.assertEqual(output["sft_attention_mask"].value.tolist(), [0, 0, 1, 1, 1, 1, 1, 1, 1])

    def test_truncation_preserves_selected_target_and_prompt(self):
        expected = {
            "right": [10, 11, 12, 13, 14],
            "left": [11, 12, 13, 14, 15],
            "middle": [10, 11, 13, 14, 15],
        }
        for mode, response in expected.items():
            with self.subTest(truncation=mode):
                output = self.build("10 11 12 13 14 15", truncation=mode)
                self.assertEqual(output["sft_response"].value.tolist(), response)
                self.assertEqual(output["sft_input_ids"].value.tolist()[:4], [0, 0, 8, 9])
                self.assertEqual(output["sft_attention_mask"].value.tolist(), [0, 0, 1, 1, 1, 1, 1, 1, 1])

    def test_error_truncation_rejects_overlong_target(self):
        with self.assertRaises(NotImplementedError):
            self.build("10 11 12 13 14 15", truncation="error")

    def test_empty_null_and_non_string_targets_are_rejected(self):
        for response in ("", " ", None, 123, []):
            with self.subTest(response=response):
                with self.assertRaisesRegex(ValueError, "non-empty string"):
                    self.build(response)


if __name__ == "__main__":
    unittest.main()
