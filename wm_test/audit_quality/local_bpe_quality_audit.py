"""Offline quality cross-check using local tokenizer JSON, no torch/detection rerun.

This implementation is accepted only if answer token lengths match ALL saved
samples. Its byte BPE follows the model's serialized pretokenizer and merge list.
It does not reproduce a GPU randperm and is not used for watermark membership.
"""
import functools
import hashlib
import json
import re
import statistics
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOKENIZER = Path("C:/Users/wenxin/Desktop/distall-watermark/model/Qwen2.5-1.5B-Instruct/tokenizer.json")
FILES = {
    stage: ROOT / "wm_test" / f"kgwwarmup_kgwgad_{stage}_gamma0.5_delta3_qwen2_5_0_5b_dolly15k_test.jsonl"
    for stage in ("warmup", "gad")
}
rows_by_stage = {
    stage: [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    for stage, path in FILES.items()
}
config = json.loads(TOKENIZER.read_text(encoding="utf-8"))
assert config["normalizer"] == {"type": "NFC"}
assert config["pre_tokenizer"]["pretokenizers"][1]["use_regex"] is False
assert config["pre_tokenizer"]["pretokenizers"][1]["add_prefix_space"] is False

# Python's stdlib re lacks Unicode property escapes. Build exact equivalent
# classes for all Unicode characters encountered in this corpus after NFC.
all_chars = set("".join(unicodedata.normalize("NFC", row["answer"])
                        for rows in rows_by_stage.values() for row in rows))
letters = "".join(re.escape(c) for c in sorted(all_chars) if unicodedata.category(c).startswith("L"))
numbers = "".join(re.escape(c) for c in sorted(all_chars) if unicodedata.category(c).startswith("N"))
pattern_text = config["pre_tokenizer"]["pretokenizers"][0]["pattern"]["Regex"]
pattern_text = pattern_text.replace(r"\p{L}", "[" + letters + "]")
pattern_text = pattern_text.replace(r"\p{N}", "[" + numbers + "]")
# Replacing a property inside a negated class must not leave nested brackets.
pattern_text = pattern_text.replace(r"[^\r\n[" + letters + "][" + numbers + "]]",
                                    r"[^\r\n" + letters + numbers + "]")
pattern_text = pattern_text.replace(r"[^\s[" + letters + "][" + numbers + "]]",
                                    r"[^\s" + letters + numbers + "]")
pretoken = re.compile(pattern_text)
byte_values = list(range(ord("!"), ord("~") + 1)) + list(range(ord("¡"), ord("¬") + 1)) + list(range(ord("®"), ord("ÿ") + 1))
unicode_values = byte_values[:]
extra = 0
for value in range(256):
    if value not in byte_values:
        byte_values.append(value)
        unicode_values.append(256 + extra)
        extra += 1
byte_encoder = dict(zip(byte_values, map(chr, unicode_values)))
vocab = config["model"]["vocab"]
merges = config["model"]["merges"]
ranks = {tuple(pair.split(" ") if isinstance(pair, str) else pair): rank
         for rank, pair in enumerate(merges)}
added = {row["content"]: row["id"] for row in config["added_tokens"]}
special_split = re.compile("(" + "|".join(re.escape(token) for token in sorted(added, key=len, reverse=True)) + ")")


@functools.lru_cache(maxsize=None)
def encode_piece(piece):
    symbols = tuple(byte_encoder[b] for b in piece.encode("utf-8"))
    while len(symbols) > 1:
        pair = min(zip(symbols, symbols[1:]), key=lambda pair: ranks.get(pair, float("inf")))
        if pair not in ranks:
            break
        new_symbols = []
        index = 0
        while index < len(symbols):
            if index + 1 < len(symbols) and (symbols[index], symbols[index + 1]) == pair:
                new_symbols.append(symbols[index] + symbols[index + 1])
                index += 2
            else:
                new_symbols.append(symbols[index])
                index += 1
        symbols = tuple(new_symbols)
    return tuple(vocab[symbol] for symbol in symbols)


def encode(answer):
    output = []
    for segment in special_split.split(answer):
        if segment in added:
            output.append(added[segment])
        elif segment:
            segment = unicodedata.normalize("NFC", segment)
            pieces = pretoken.findall(segment)
            assert "".join(pieces) == segment
            for piece in pieces:
                output.extend(encode_piece(piece))
    return output


tokens_by_stage = {
    stage: [(row, encode(row["answer"])) for row in rows]
    for stage, rows in rows_by_stage.items()
}
mismatches = [
    {"stage": stage, "id": row["id"], "saved_tokens": row["num_tokens"], "local_tokens": len(tokens)}
    for stage, rows in tokens_by_stage.items() for row, tokens in rows
    if len(tokens) != row["num_tokens"]
]
print(json.dumps({"length_checks": sum(len(rows) for rows in tokens_by_stage.values()),
                  "mismatches": mismatches}, ensure_ascii=False), flush=True)
assert not mismatches, "Local tokenizer must match every saved answer token length"
result = {
    "tokenizer_file": str(TOKENIZER),
    "tokenizer_sha256": hashlib.sha256(TOKENIZER.read_bytes()).hexdigest(),
    "length_checks_passed": 1000,
    "method": "1 - unique answer-adjacent token pairs / all answer-adjacent token pairs > 0.5; prompt excluded",
    "models": {},
}
for stage, rows in tokens_by_stage.items():
    per_sample = []
    for row, tokens in rows:
        pairs = list(zip(tokens, tokens[1:]))
        unique = len(set(pairs))
        ratio = 1 - unique / len(pairs) if pairs else 0
        per_sample.append({"id": row["id"], "answer_tokens": len(tokens),
                           "answer_pairs": len(pairs), "unique_answer_pairs": unique,
                           "saved_detection_unique_pairs": row["dedup_num_tokens"],
                           "repeated_fraction": ratio, "severe": ratio > .5})
        assert row["dedup_num_tokens"] - unique in (0, 1)
    result["models"][stage] = {
        "source_sha256": hashlib.sha256(FILES[stage].read_bytes()).hexdigest(),
        "n": len(rows), "severe_count": sum(row["severe"] for row in per_sample),
        "mean_repeated_fraction": statistics.mean(row["repeated_fraction"] for row in per_sample),
        "median_repeated_fraction": statistics.median(row["repeated_fraction"] for row in per_sample),
        "over_saved_max_tokens": [row["id"] for row, tokens in rows if len(tokens) > row["generation"]["max_new_tokens"]],
        "per_sample": per_sample,
    }
output = Path(__file__).with_suffix(".json")
output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({stage: {k: v for k, v in model.items() if k != "per_sample"}
                  for stage, model in result["models"].items()}, ensure_ascii=False))
print("SAVED", output)
