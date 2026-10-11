#!/usr/bin/env python3
"""Rescore saved answers with explicit KGW parameters without generating text.

Outputs are separate JSONL files. Both the watermarked student answers and the
clean comparison answers must be rescored with the same detector configuration.
The original CUDA green-list RNG is required; no model weights are loaded.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCORE_FIELDS = (
    "num_tokens", "green_tokens", "green_fraction", "z_score", "p_value",
    "dedup_num_tokens", "dedup_green_tokens", "dedup_green_fraction",
    "dedup_z_score", "dedup_p_value",
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", type=Path, nargs="+", required=True,
                        help="Saved student and clean answer JSONL files")
    parser.add_argument("--gamma", type=float, required=True,
                        help="Original watermark green-list fraction")
    parser.add_argument("--delta", type=float, required=True,
                        help="Original generation bias; stored as metadata")
    parser.add_argument("--hash-key", type=int, default=15_485_863)
    parser.add_argument("--tokenizer", type=Path, default=None,
                        help="Local tokenizer directory; defaults to each row's model_path")
    parser.add_argument("--score-device", default="cuda",
                        help="CUDA device reproducing the original green-list RNG")
    parser.add_argument("--output-dir", type=Path, default=None,
                        help="Output directory; defaults to each source's directory")
    parser.add_argument("--overwrite", action="store_true",
                        help="Replace previously rescored outputs, never original inputs")
    return parser.parse_args(argv)


def validate_config(config: dict[str, Any]) -> dict[str, float | int]:
    try:
        gamma = float(config["gamma"])
        delta = float(config["delta"])
        raw_key = config["hash_key"]
        hash_key = int(raw_key)
    except (KeyError, TypeError, ValueError, OverflowError) as error:
        raise ValueError("KGW gamma, delta and integer hash_key must be supplied") from error
    if not math.isfinite(gamma) or not 0.0 < gamma < 1.0:
        raise ValueError("--gamma must be finite and in (0, 1)")
    if not math.isfinite(delta) or delta <= 0.0:
        raise ValueError("--delta must be finite and positive")
    if isinstance(raw_key, bool) or hash_key <= 0 or hash_key != raw_key:
        raise ValueError("--hash-key must be a positive integer")
    return {"gamma": gamma, "delta": delta, "hash_key": hash_key}


def validate_device(score_device: str) -> None:
    if not isinstance(score_device, str) or not (
        score_device == "cuda"
        or (score_device.startswith("cuda:") and score_device[5:].isdigit())
    ):
        raise ValueError("--score-device must be cuda or cuda:N; CPU uses different KGW green lists")


def output_path_for(
    source: Path, config: dict[str, Any], output_dir: Path | None = None,
) -> Path:
    config = validate_config(config)
    # repr retains the exact float and strips only an integer's trailing .0.
    def number(value: float | int) -> str:
        text = repr(value)
        return text[:-2] if text.endswith(".0") else text

    tag = (f"rescored_gamma{number(config['gamma'])}_delta{number(config['delta'])}"
           f"_key{config['hash_key']}")
    return (output_dir or source.parent) / f"{source.stem}.{tag}.jsonl"


def load_source(source: Path) -> tuple[bytes, list[dict[str, Any]]]:
    if not source.is_file():
        raise FileNotFoundError(f"input JSONL file not found: {source}")
    raw = source.read_bytes()
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for line_number, line in enumerate(raw.decode("utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(f"invalid JSON at {source}:{line_number}") from error
        where = f"{source}:{line_number}"
        if not isinstance(row, dict):
            raise ValueError(f"JSONL record must be an object at {where}")
        sample_id = row.get("id")
        if not isinstance(sample_id, str) or not sample_id.strip():
            raise ValueError(f"missing nonempty string id at {where}")
        if sample_id in seen:
            raise ValueError(f"duplicate id {sample_id!r} at {where}")
        seen.add(sample_id)
        label = row.get("label")
        if label not in ("kgw", "clean") or row.get("is_watermarked") is not (label == "kgw"):
            raise ValueError(f"label/is_watermarked must be kgw/true or clean/false at {where}")
        prompt = row.get("prompt")
        if isinstance(prompt, list):
            valid_prompt = bool(prompt) and all(
                isinstance(message, dict)
                and isinstance(message.get("role"), str) and bool(message["role"])
                and isinstance(message.get("content"), str)
                for message in prompt
            )
        else:
            valid_prompt = isinstance(prompt, str) and bool(prompt)
        if not valid_prompt or not isinstance(row.get("answer"), str):
            raise ValueError(f"rescoring requires a prompt and answer text at {where}")
        if "kgw" in row and not isinstance(row["kgw"], dict):
            raise ValueError(f"kgw metadata must be an object at {where}")
        generation = row.get("generation", {})
        if not isinstance(generation, dict):
            raise ValueError(f"generation metadata must be an object at {where}")
        if "max_prompt_tokens" in generation:
            limit = generation["max_prompt_tokens"]
            if isinstance(limit, bool) or not isinstance(limit, int) or limit <= 0:
                raise ValueError(f"generation.max_prompt_tokens must be a positive integer at {where}")
        rows.append(row)
    if not rows:
        raise ValueError(f"no answer records found in {source}")
    return raw, rows


def plan_outputs(
    inputs: list[Path], config: dict[str, Any], output_dir: Path | None = None,
    overwrite: bool = False,
) -> list[tuple[Path, Path]]:
    """Validate every input and output before any scoring or output writes."""
    config = validate_config(config)
    sources = [Path(source).resolve() for source in inputs]
    if not sources:
        raise ValueError("at least one input JSONL file is required")
    if len(set(sources)) != len(sources):
        raise ValueError("--inputs contains the same source more than once")
    directory = Path(output_dir).resolve() if output_dir is not None else None
    if directory is not None and directory.exists() and not directory.is_dir():
        raise ValueError(f"--output-dir is not a directory: {directory}")
    for source in sources:
        load_source(source)
    plans: list[tuple[Path, Path]] = []
    seen_outputs: set[Path] = set()
    for source in sources:
        output = output_path_for(source, config, directory).resolve()
        if output in seen_outputs:
            raise ValueError(f"multiple inputs would produce the same output: {output}")
        seen_outputs.add(output)
        if output in sources or (output.exists() and any(output.samefile(item) for item in sources)):
            raise ValueError(f"rescoring must never overwrite an original input: {output}")
        if output.exists():
            if not output.is_file():
                raise ValueError(f"output is not a file: {output}")
            if not overwrite:
                raise FileExistsError(f"{output} exists; use --overwrite to replace only rescored outputs")
        plans.append((source, output))
    return plans


def make_rescorer(args: argparse.Namespace) -> Any:
    # Importing this module and using injected scorers require only stdlib.
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from wm_test.evaluate_compare_metrics import LegacyRescorer

    return LegacyRescorer(args)


def rescore_file(
    source: Path, output: Path, config: dict[str, Any], args: argparse.Namespace,
    rescorer: Any = None,
) -> Path:
    """Score existing answers and atomically write a distinct output JSONL."""
    source, output = Path(source).resolve(), Path(output).resolve()
    config = validate_config(config)
    validate_device(args.score_device)
    raw, rows = load_source(source)
    if output == source or (output.exists() and output.samefile(source)):
        raise ValueError("rescoring must never overwrite an original input")
    if output.exists() and not args.overwrite:
        raise FileExistsError(f"{output} exists; use --overwrite to replace only rescored outputs")
    if output.exists() and not output.is_file():
        raise ValueError(f"output is not a file: {output}")
    if rescorer is None:
        rescorer = make_rescorer(args)
    digest = hashlib.sha256(raw).hexdigest()
    tokenizer_override = str(Path(args.tokenizer).resolve()) if args.tokenizer is not None else None
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n", dir=output.parent,
            prefix=output.name + ".", suffix=".tmp", delete=False,
        ) as handle:
            temporary = Path(handle.name)
            for index, row in enumerate(rows, 1):
                score = rescorer.score(row, config_override=config)
                if not isinstance(score, dict) or not all(key in score for key in SCORE_FIELDS):
                    raise ValueError(f"scorer did not return complete raw and deduplicated scores for {row['id']}")
                original_kgw = dict(row.get("kgw", {}))
                record = {key: value for key, value in row.items() if key not in SCORE_FIELDS}
                record.update(score)
                record["kgw"] = {
                    **original_kgw, **config,
                    "seeding": "simple_1 (hash_key * previous_token_id)",
                    "deduplication": "unique (previous_token_id, token_id) pairs",
                }
                record["rescoring"] = {
                    "source_path": str(source), "source_sha256": digest,
                    "original_kgw": original_kgw,
                    "tokenizer_override": tokenizer_override,
                    "score_device": args.score_device,
                }
                handle.write(json.dumps(record, ensure_ascii=False, allow_nan=False) + "\n")
                if index == 1 or index % 50 == 0 or index == len(rows):
                    print(f"Rescoring {source.name}: {index}/{len(rows)}", flush=True)
        if output.exists() and not args.overwrite:
            raise FileExistsError(f"output appeared during scoring: {output}")
        os.replace(temporary, output)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return output


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    config = validate_config({"gamma": args.gamma, "delta": args.delta, "hash_key": args.hash_key})
    validate_device(args.score_device)
    if args.tokenizer is not None and not args.tokenizer.is_dir():
        raise FileNotFoundError(f"local tokenizer directory not found: {args.tokenizer}")
    plans = plan_outputs(args.inputs, config, args.output_dir, args.overwrite)
    # Check all rows can locate a tokenizer before writing any of the outputs.
    if args.tokenizer is None:
        for source, _ in plans:
            _, rows = load_source(source)
            for row in rows:
                if not isinstance(row.get("model_path"), str) or not row["model_path"]:
                    raise ValueError(f"no model_path for {row['id']} in {source}; supply --tokenizer")
    print(f"KGW rescoring config: {json.dumps(config, sort_keys=True)}", flush=True)
    rescorer = make_rescorer(args)
    for source, output in plans:
        saved = rescore_file(source, output, config, args, rescorer=rescorer)
        print(f"Saved rescored answers: {saved}", flush=True)


if __name__ == "__main__":
    main()
