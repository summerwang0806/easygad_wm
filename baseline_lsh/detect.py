"""Score saved Parquet/JSONL answers using the frozen TEACHER LSH asset.

No LLM weights or GPU are loaded. Scores are diagnostics, not calibrated p-values.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from baseline_lsh.core import BucketAsset, LSHConfig, LSHWatermark, canonical, sha256_file
from baseline_lsh.io_utils import atomic_json, prompt_ids, read_json


def response_rows(path, text_field=None):
    if path.suffix == ".parquet":
        import pyarrow.parquet as pq
        rows = pq.read_table(path).to_pylist()
    elif path.suffix == ".jsonl":
        with path.open(encoding="utf-8") as f:
            rows = [json.loads(line) for line in f if line.strip()]
    else:
        raise ValueError("input must be .parquet or .jsonl")
    seen = set()
    for index, row in enumerate(rows):
        fields = [text_field] if text_field else ["teacher_response", "answer", "text", "generated_text"]
        name = next((k for k in fields if k in row), None)
        if name is None or not isinstance(row[name], str) or not row[name].strip():
            raise ValueError(f"missing/empty answer at input row {index}; select --text-field explicitly if needed")
        sample_id = row.get("id", index)
        if sample_id is None or sample_id in seen:
            raise ValueError(f"duplicate/null answer ID {sample_id!r}")
        seen.add(sample_id)
        yield sample_id, row[name], row


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True, help="New score .jsonl; does not edit input")
    p.add_argument("--asset", type=Path, default=Path("baseline_lsh/assets/qwen2_5_14b_lsh4_seed42.npz"))
    p.add_argument("--tokenizer", type=Path, help="Original teacher tokenizer; default path stored in asset")
    p.add_argument("--text-field", help="Default: teacher_response / answer / text / generated_text")
    p.add_argument("--context", choices=["prompt", "answer-only"], default="prompt")
    p.add_argument("--max-prompt-tokens", type=int, default=2048)
    p.add_argument("--max-tokens", type=int)
    p.add_argument("--gamma", type=float, default=0.5)
    p.add_argument("--hash-key", type=int, default=15_485_863)
    p.add_argument("--partition", choices=["balanced", "global"], default="balanced")
    a = p.parse_args(argv)
    if a.max_prompt_tokens <= 0 or (a.max_tokens is not None and a.max_tokens <= 0):
        p.error("token limits must be positive")
    a.input, a.output, a.asset = a.input.resolve(), a.output.resolve(), a.asset.resolve()
    meta_output = a.output.with_name(a.output.name + ".metadata.json")
    if len({a.input, a.output, a.asset, meta_output}) != 4 or a.output.suffix != ".jsonl":
        p.error("output must be a distinct .jsonl")
    if a.output.exists() or meta_output.exists():
        raise FileExistsError("detector output exists; choose a new output path")
    wm = LSHWatermark(BucketAsset.load(a.asset), LSHConfig(a.gamma, 0.0, a.hash_key, a.partition))
    a.tokenizer = (a.tokenizer or Path(wm.asset.metadata["model"])).resolve()
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(a.tokenizer, use_fast=True, local_files_only=True)
    wm.asset.check_tokenizer(tokenizer)
    # If our generator's provenance is present, refuse an accidentally wrong key.
    source_meta = a.input.with_name(a.input.name + ".metadata.json")
    if source_meta.exists() and a.input.suffix == ".parquet":
        saved = read_json(source_meta)
        spec = saved.get("specification", {})
        old = spec.get("watermark_config")
        if old:
            for key in ("version", "asset_sha256", "gamma", "hash_key", "partition"):
                if old[key] != wm.descriptor()[key]:
                    raise ValueError(f"detector disagrees with generated data's {key}")
            if saved["output_sha256"] != sha256_file(a.input):
                raise ValueError("generated input no longer matches its provenance")
            if a.max_prompt_tokens != spec["generation"]["max_prompt_tokens"]:
                raise ValueError("max-prompt-tokens differs from generation")
    a.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = a.output.with_name(a.output.name + ".tmp")
    n = 0
    with temporary.open("w", encoding="utf-8", newline="\n") as f:
        for sample_id, text, row in response_rows(a.input, a.text_field):
            context = []
            if a.context == "prompt":
                raw_prompt = row.get("content", row.get("prompt"))
                if isinstance(raw_prompt, list) and raw_prompt:
                    context = prompt_ids(tokenizer, raw_prompt, a.max_prompt_tokens)
                elif isinstance(raw_prompt, str) and raw_prompt:
                    # A string prompt must already be rendered. No guessed template.
                    context = tokenizer.encode(raw_prompt, add_special_tokens=False)[:a.max_prompt_tokens]
                else:
                    raise ValueError(f"no prompt for {sample_id!r}; use --context answer-only to skip the first answer token")
                if not context:
                    raise ValueError(f"empty prompt for {sample_id!r}")
            result = wm.score(tokenizer.encode(text, add_special_tokens=False), context, a.max_tokens)
            f.write(canonical({"id": sample_id, "context_policy": a.context, **result}) + "\n")
            n += 1
    if not n:
        raise ValueError("no saved answers to score")
    os.replace(temporary, a.output)
    descriptor = wm.descriptor()
    descriptor.pop("delta")  # Strength is not an input to green-list detection.
    atomic_json(meta_output, {"rows": n, "input": str(a.input), "input_sha256": sha256_file(a.input),
                              "output_sha256": sha256_file(a.output), "detector": descriptor,
                              "context_policy": a.context, "max_prompt_tokens": a.max_prompt_tokens,
                              "max_tokens": a.max_tokens, "tokenizer": str(a.tokenizer),
                              "score_basis": "saved answer retokenized with frozen teacher tokenizer; no LLM inference"})
    print(f"[scored] {n} saved answers → {a.output}")


if __name__ == "__main__":
    main()
