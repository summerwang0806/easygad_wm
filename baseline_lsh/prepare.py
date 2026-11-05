"""Prepare frozen LSH buckets from ONLY the teacher input-embedding tensor."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np

from baseline_lsh.core import ASSET_VERSION, BucketAsset, project_buckets, sha256_file, tokenizer_identity


def locate_embedding(model, name):
    """Qwen HF safetensors (single or sharded); never load a complete model."""
    model = Path(model).resolve()
    index = model / "model.safetensors.index.json"
    if index.exists():
        mapping = json.loads(index.read_text(encoding="utf-8"))["weight_map"]
        if name not in mapping:
            raise ValueError(f"embedding tensor {name!r} not found in {index}")
        weight = (model / mapping[name]).resolve()
        if not weight.is_relative_to(model):
            raise ValueError("weight shard escapes model directory")
        return weight
    weight = model / "model.safetensors"
    if not weight.is_file():
        raise FileNotFoundError(f"no HF safetensors checkpoint under {model}; expected model.safetensors[.index.json]")
    return weight


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--model", type=Path, default=Path("/shared/public_models/Qwen2.5-14B-Instruct"))
    p.add_argument("--output", type=Path, required=True, help="New .npz asset; never overwritten")
    p.add_argument("--lsh-bits", type=int, default=4, help="Gaussian hyperplanes; paper uses 4")
    p.add_argument("--lsh-seed", type=int, default=42)
    p.add_argument("--embedding-key", default="model.embed_tokens.weight")
    p.add_argument("--chunk-size", type=int, default=1024)
    args = p.parse_args(argv)
    if not 1 <= args.lsh_bits <= 12 or args.lsh_seed < 0 or args.chunk_size <= 0:
        p.error("bits must be 1..12, seed nonnegative, chunk-size positive")
    if args.output.exists():
        raise FileExistsError(f"asset exists: {args.output}; reuse it or choose a new path")
    if args.output.suffix != ".npz":
        p.error("output must end in .npz")
    from safetensors import safe_open
    from transformers import AutoTokenizer
    import torch

    tokenizer = AutoTokenizer.from_pretrained(args.model, use_fast=True, local_files_only=True)
    identity = tokenizer_identity(tokenizer)
    token_ids = np.array(sorted(tokenizer.get_vocab().values()), dtype=np.int64)
    shard = locate_embedding(args.model, args.embedding_key)
    h = hashlib.sha256()
    with safe_open(shard, framework="pt", device="cpu") as f:
        if args.embedding_key not in f.keys():
            raise ValueError(f"{args.embedding_key} not in {shard}")
        tensor = f.get_slice(args.embedding_key)
        shape = tensor.get_shape()
        if len(shape) != 2 or shape[0] < identity["id_space"]:
            raise ValueError("embedding tensor does not cover all tokenizer IDs")
        planes = np.random.Generator(np.random.PCG64(args.lsh_seed)).standard_normal(
            (args.lsh_bits, shape[1])).astype(np.float32)
        lookup = np.empty(identity["id_space"], dtype=np.int64)
        zero_rows = 0
        for start in range(0, identity["id_space"], args.chunk_size):
            end = min(identity["id_space"], start + args.chunk_size)
            block = tensor[start:end, :].contiguous()
            h.update(block.view(torch.uint8).numpy().tobytes())
            values = block.to(torch.float32).numpy()
            zero_rows += int(np.count_nonzero(np.linalg.norm(values, axis=1) == 0))
            lookup[start:end] = project_buckets(values, planes)
            print(f"[embedding → LSH] {end}/{identity['id_space']}", flush=True)
    groups, sizes = np.unique(lookup[token_ids], return_counts=True)
    metadata = {"format": ASSET_VERSION, "lsh_bits": args.lsh_bits, "lsh_seed": args.lsh_seed,
                "tokenizer": identity, "model": str(args.model.resolve()), "embedding_key": args.embedding_key,
                "embedding_shape": shape, "embedding_prefix_sha256": h.hexdigest(),
                "embedding_rows_hashed": identity["id_space"], "zero_embedding_rows": zero_rows,
                "projection": "float64 matmul of float32 weights/planes; sign>=0; bit0 is LSB",
                "numpy_version": np.__version__, "torch_version": torch.__version__,
                "model_config_sha256": sha256_file(args.model / "config.json"),
                "bucket_sizes": {str(int(k)): int(n) for k, n in zip(groups, sizes)}}
    asset = BucketAsset(token_ids, lookup[token_ids], planes, metadata)
    asset.save(args.output)
    print(json.dumps({"asset": str(args.output.resolve()), "sha256": asset.sha256,
                      "occupied_buckets": len(groups), "bucket_sizes": metadata["bucket_sizes"]}, indent=2))


if __name__ == "__main__":
    main()
