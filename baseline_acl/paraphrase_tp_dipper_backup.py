#!/usr/bin/env python3
"""Backup Dipper TP with estimated inverse scores and explicit text projection.

Only teacher_response is replaced. Uses UP's checked whole-response writer,
durable checkpoints, and independent GPU scheduling. Cross-tokenizer projection
is a project adaptation because the original TP code was not published.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, replace
import json
import math
import os
from pathlib import Path
import sys

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from baseline_acl import paraphrase_up as up
from baseline_acl.tokenizer_bridge_dipper_backup import TextProjection, TPTextProjectionProcessor


@dataclass(frozen=True)
class TPWorkerFactory:
    """Spawn-picklable factory; each worker loads only its selected local GPU."""
    rules_path: str
    rule_tokenizer_path: str
    strength: float
    candidate_top_k: int
    projection_context_tokens: int
    rules_sha256: str

    def __call__(self, model, config, tokenizer_path, gpu_id):
        from transformers import AutoTokenizer, T5Tokenizer
        from baseline_acl.inverse_watermark import RuleTable

        decoder = T5Tokenizer.from_pretrained(tokenizer_path, local_files_only=True, legacy=True)
        decoder.model_max_length = config.max_input_tokens
        reference = AutoTokenizer.from_pretrained(self.rule_tokenizer_path, local_files_only=True)
        rules = load_bound_rules(Path(self.rules_path), self.rules_sha256)
        rules.validate_tokenizer(reference)
        projection = TextProjection(decoder, reference, rules, context_tokens=self.projection_context_tokens)
        processor = TPTextProjectionProcessor(projection, strength=self.strength, candidate_top_k=self.candidate_top_k)
        return up.DipperGenerator(model, config, decoder, logits_processor=processor)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--rules", type=Path, required=True)
    parser.add_argument("--rule-tokenizer", required=True, help="Local tokenizer used when estimating Qwen rules")
    parser.add_argument("--model", default=str(up.BASELINE_DIR / "models" / "dipper-paraphraser-xxl"))
    parser.add_argument("--tokenizer", default=str(up.BASELINE_DIR / "models" / "t5-v1_1-xxl-tokenizer"))
    parser.add_argument("--nltk-data", type=Path, default=up.DEFAULT_NLTK_DATA)
    parser.add_argument("--inverse-strength", type=float, default=2.5)
    parser.add_argument("--candidate-top-k", type=int, default=128,
                        help="TP projection candidates before sampling; 0 projects all ordinary Dipper tokens (slow)")
    parser.add_argument("--projection-context-tokens", type=int, default=64,
                        help="Approximate suffix of decoder history to project; 0 uses full history")
    parser.add_argument("--num-gpus", type=int)
    parser.add_argument("--dtype", choices=("auto", "float32", "bfloat16"), default="auto")
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--max-input-tokens", type=int, default=4096)
    parser.add_argument("--max-output-length", type=int, default=4096)
    parser.add_argument("--lex-diversity", type=int, choices=(0, 20, 40, 60, 80, 100), default=60)
    parser.add_argument("--order-diversity", type=int, choices=(0, 20, 40, 60, 80, 100), default=0)
    parser.add_argument("--temperature", type=float, default=1.0)
    parser.add_argument("--top-p", type=float, default=0.75)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-attempts", type=int, default=1)
    parser.add_argument("--on-failure", choices=("error", "keep-original"), default="error")
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--audit", type=Path)
    parser.add_argument("--resume", action="store_true")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--inspect", action="store_true", help="Check source/rules without importing Transformers or CUDA")
    modes.add_argument("--preflight", action="store_true", help="CPU tokenizer, rule identity and whole-response budget checks")
    args = parser.parse_args(argv)
    if not math.isfinite(args.inverse_strength) or args.inverse_strength < 0:
        parser.error("--inverse-strength must be finite and nonnegative")
    if args.candidate_top_k < 0 or args.projection_context_tokens < 0:
        parser.error("projection limits must be nonnegative")
    if args.num_gpus is not None and args.num_gpus < 1:
        parser.error("--num-gpus must be positive")
    if not (args.inspect or args.preflight) and args.output is None:
        parser.error("--output is required for TP generation")
    return args


def load_bound_rules(path: Path, expected_hash: str | None = None):
    """Bind every worker's in-memory rule table to the version in the audit."""
    from baseline_acl.inverse_watermark import RuleTable

    actual_hash = up.file_sha256(path)
    if expected_hash is not None and actual_hash != expected_hash:
        raise ValueError("TP rules changed since preflight; every worker must use the audited version")
    rules = RuleTable.load(path)
    if up.file_sha256(path) != actual_hash:
        raise ValueError("TP rules changed while loading")
    return rules


def attack_identity(args, rule_tokenizer_identity, rules, rules_sha256):
    return {
        "method": "targeted_dipper_paraphrasing", "rules_sha256": rules_sha256,
        "rules_tokenizer": rules.tokenizer, "rule_tokenizer": rule_tokenizer_identity,
        "rules_provenance": rules.document["provenance"],
        "inverse_strength": args.inverse_strength,
        "projection": {"method": "decoded_candidate_changed_suffix_mean", "candidate_top_k": args.candidate_top_k,
                       "decoder_context_tokens": args.projection_context_tokens,
                       "special_tokens_penalized": False, "cross_tokenizer": True,
                       "project_adaptation": True, "official_tp_code_available": False},
    }


def validate_rule_source(rules, source_hash: str):
    recorded = rules.document["provenance"].get("input", {})
    if isinstance(recorded, dict) and recorded.get("sha256") and recorded["sha256"] != source_hash:
        raise ValueError("TP source differs from the original training corpus used for rule estimation")


def validate_attack_paths(args):
    """Rules are an input asset and must never alias an output/checkpoint/audit."""
    outputs = []
    if args.output is not None:
        outputs = [args.output, args.checkpoint or args.output.with_suffix(args.output.suffix + ".progress.jsonl"),
                   args.audit or args.output.with_suffix(args.output.suffix + ".audit.json")]
    for path in [args.input, *outputs]:
        if args.rules.resolve() == path.resolve() or (
                args.rules.exists() and path.exists() and os.path.samefile(args.rules, path)):
            raise ValueError("rules must not alias source, output, checkpoint or audit")
    # Reject held-out inputs even in CPU modes, before any model loading.
    import re
    if any(token in ("test", "val", "validation", "eval")
           for token in re.split(r"[_\-.]", args.input.stem.lower())):
        raise ValueError("TP only rewrites training responses; held-out input is refused")


def main(argv=None):
    args = parse_args(argv)
    validate_attack_paths(args)
    from baseline_acl.inverse_watermark import tokenizer_identity

    rules_hash = up.file_sha256(args.rules)
    rules = load_bound_rules(args.rules, rules_hash)
    if args.inspect:
        report = up.inspect_source(args.input)
        validate_rule_source(rules, report["input_sha256"])
        report.update(method="targeted_dipper_paraphrasing", rules_sha256=rules_hash,
                      rules_tokenizer=rules.tokenizer, tokenizer_identity_checked=False,
                      projection_is_project_adaptation=True)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return
    validate_rule_source(rules, up.file_sha256(args.input))
    config_values = {name: getattr(args, name) for name in up.GenerationConfig.__dataclass_fields__
                     if hasattr(args, name)}
    config_values["dtype"] = "float32" if args.dtype == "auto" else args.dtype
    config = up.GenerationConfig(**config_values)
    config.validate()
    from transformers import AutoTokenizer, T5Tokenizer

    up.asset_identity(args.tokenizer)
    up.asset_identity(args.rule_tokenizer)
    decoder = T5Tokenizer.from_pretrained(args.tokenizer, local_files_only=True, legacy=True)
    decoder.model_max_length = config.max_input_tokens
    reference = AutoTokenizer.from_pretrained(args.rule_tokenizer, local_files_only=True)
    rules.validate_tokenizer(reference)
    attack = attack_identity(args, tokenizer_identity(reference), rules, rules_hash)
    splitter = up.load_sentence_splitter(args.nltk_data)
    if args.preflight:
        report = up.preflight_source(args.input, decoder, config, splitter)
        report.update(method=attack["method"], attack=attack, tokenizer_identity_checked=True)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        if not report["valid"]:
            raise ValueError("TP source exceeds whole-response encoder budget; no text was truncated")
        return
    checkpoint = args.checkpoint or args.output.with_suffix(args.output.suffix + ".progress.jsonl")
    audit = args.audit or args.output.with_suffix(args.output.suffix + ".audit.json")
    up.validate_output_paths(args.input, args.output, checkpoint, audit, args.resume)
    visible = up.parse_visible_gpus(os.environ.get("CUDA_VISIBLE_DEVICES"), args.num_gpus)
    identity = up.model_identity(args.model, args.tokenizer)
    identity["attack"] = attack
    devices = up.probe_selected_gpus(visible)
    config = replace(config, dtype=up.select_dtype(args.dtype, devices))
    print(f"[TP] GPUs={visible}, dtype={config.dtype}, projection={up.canonical_json(attack['projection'])}", flush=True)
    from baseline_acl.dipper_parallel import ParallelDipperGenerator

    worker = TPWorkerFactory(str(args.rules.resolve()), str(Path(args.rule_tokenizer).resolve()),
                             args.inverse_strength, args.candidate_top_k, args.projection_context_tokens, rules_hash)
    factory = lambda: ParallelDipperGenerator(args.model, config, args.tokenizer, visible, worker_factory=worker)
    return up.run_paraphrasing(args.input, args.output, config, decoder, factory, identity,
                              resume=args.resume, checkpoint_path=checkpoint, audit_path=audit,
                              sentence_splitter=splitter)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, RuntimeError, OSError, ImportError) as error:
        print(f"[error] {error}", file=sys.stderr, flush=True)
        sys.exit(1)
