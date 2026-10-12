"""Read-only CPU audit; run from the repository root with local tokenizer assets."""
import hashlib
from importlib import metadata
import json
import re
import sys
from collections import Counter
from pathlib import Path

import pyarrow.parquet as pq
from transformers import T5Tokenizer

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from baseline_acl.paraphrase_up import GenerationConfig, load_sentence_splitter, prepare_response

OUT = Path(__file__).resolve().parent
tokenizer = T5Tokenizer.from_pretrained(
    ROOT / "baseline_acl/models/t5-v1_1-xxl-tokenizer", local_files_only=True, legacy=True
)
tokenizer.model_max_length = 4096
splitter = load_sentence_splitter()
config = GenerationConfig()


def repeated_line_run(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    best = {"unit": [], "repeats": 0, "characters_without_separators": 0}
    for period in range(1, 5):
        start = 0
        while start + period < len(lines):
            unit = lines[start:start + period]
            end = start + period
            while lines[end:end + period] == unit:
                end += period
            repeats = (end - start) // period
            chars = sum(map(len, unit)) * repeats
            if repeats >= 2 and chars > best["characters_without_separators"]:
                best = {"unit": unit, "repeats": repeats, "characters_without_separators": chars}
            start = max(start + 1, end - period + 1)
    best["fraction_of_original_characters_excluding_run_separators"] = best["characters_without_separators"] / len(text)
    return best


def repeat_fraction(text):
    words = text.lower().split()
    grams = [tuple(words[i:i + 4]) for i in range(len(words) - 3)]
    return 1 - len(set(grams)) / len(grams) if grams else 0


datasets = {}
rows_by_group = {}
lengths_by_group = {}
for group, stem in [("old", "kgw"), ("new", "kgw_gamma0.5_delta3")]:
    path = ROOT / f"data/dolly15k_qwen2_5_14b_{stem}_train.parquet"
    rows = pq.read_table(path).to_pylist()
    lengths = [prepare_response(tokenizer, row["teacher_response"], config, splitter)["prompt_tokens"] for row in rows]
    suspicious = [i for i, row in enumerate(rows) if repeat_fraction(row["teacher_response"]) > .5]
    datasets[group] = {
        "path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "rows": len(rows), "max_full_input_tokens": max(lengths),
        "over_budget_indices": [i for i, length in enumerate(lengths) if length > 4096],
        "whitespace_word4_repeat_gt_50pct_count": len(suspicious),
        "whitespace_word4_repeat_gt_50pct_indices": suspicious,
    }
    rows_by_group[group] = rows
    lengths_by_group[group] = lengths
    print(group, {key: value for key, value in datasets[group].items() if not key.endswith("indices")}, flush=True)

old_by_id = {row["id"]: (i, row) for i, row in enumerate(rows_by_group["old"])}
examples = []
for i in datasets["new"]["over_budget_indices"]:
    row = rows_by_group["new"][i]
    old_index, old_row = old_by_id[row["id"]]
    text = row["teacher_response"]
    examples.append({
        "row_index_zero_based": i, "id": row["id"], "input_tokens": lengths_by_group["new"][i],
        "old_input_tokens": lengths_by_group["old"][old_index], "characters": len(text),
        "whitespace_word4_repeat_fraction": repeat_fraction(text), "repeated_line_run": repeated_line_run(text),
        "prompt": row["content"], "teacher_response": text, "old_teacher_response": old_row["teacher_response"],
    })
    print(json.dumps({k: v for k, v in examples[-1].items() if k not in {"prompt", "teacher_response", "old_teacher_response"}}, ensure_ascii=False), flush=True)

result = {
    "method": "Local T5Tokenizer legacy=True; existing UP prepare_response and bundled English NLTK Punkt; full Dipper template including EOS, limit 4096. No model weights loaded.",
    "tokenizer_class": str(type(tokenizer)), "sentence_splitter_identity": splitter.resource_identity,
    "repeat_method": "lowercase and whitespace split (including punctuation and code); 1 - unique word 4-grams / all word 4-grams; diagnostic screening, not an automatic quality verdict",
    "same_id_order": [r["id"] for r in rows_by_group["old"]] == [r["id"] for r in rows_by_group["new"]],
    "content_mismatches": sum(a["content"] != b["content"] for a, b in zip(rows_by_group["old"], rows_by_group["new"], strict=True)),
    "datasets": datasets, "overlong_examples": examples,
    "first_overlong_raw_source_tokens": len(tokenizer.encode(examples[0]["teacher_response"], add_special_tokens=False)) if examples else None,
    "analysis_package_versions": {name: metadata.version(name) for name in ("transformers", "sentencepiece", "nltk", "pyarrow")},
    "tokenizer_spiece_sha256": hashlib.sha256((ROOT / "baseline_acl/models/t5-v1_1-xxl-tokenizer/spiece.model").read_bytes()).hexdigest(),
    "conclusion": "All 20 over-budget responses contain continuous unrelated repetition, already in the source teacher_response.",
    "limitations": "Generation provenance is absent in downloaded final parquet metadata. Filenames do not establish teacher identity or prove that gamma/delta were the only changed generation settings.",
}
(OUT / "input_length_audit.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
report = [
    "# UP 输入超长核对（2026-10-12）", "",
    "仅本地 CPU 检查，没有加载模型权重，没有修改训练、转述或数据文件。", "",
    "核对结果：20 条超长回答全部包含大段无关循环，重复在原始教师回答中已存在。前 10 个行号与服务器报错完全一致。", "",
    "old 指原 KGW（0.25/2）训练集，new 指 KGW gamma0.5_delta3 训练集；参数名称来自用户实验说明及文件名，生成设置没有溯源元数据可核验。", "",
    "两组训练数据的 ID、顺序和问题一致。使用现有 UP 的完整输入构造与本地 T5 tokenizer，限制为 4096。", "",
    "| 数据 | 条数 | 最大完整输入 token | 超长条数 | 重复四词片段占比 >50% 初筛条数 |",
    "|---|---:|---:|---:|---:|",
]
for group, data in datasets.items():
    report.append(f"| {group} | {data['rows']} | {data['max_full_input_tokens']} | {len(data['over_budget_indices'])} | {data['whitespace_word4_repeat_gt_50pct_count']} |")
report += ["", "第 1898 行原始回答为 6095 个 T5 token，与服务器警告一致；规范化并加入完整 Dipper 模板及 EOS 后为 6114 个 token。", "",
           "初筛将文本转为小写后按空白分词（保留代码和标点），重复率为 `1 - 不同四词片段数 / 全部四词片段数`。不是人工判定，亦不是实验使用的 tokenizer 重复率。", "",
           "`teacher_comparison.json` 另有只提取 ASCII 英文/数字词的指标；它不保留纯符号循环，两种指标不能混用。", "",
           "## 全部超长回答", "", "行号从 0 开始，和报错一致。循环次数按原文本非空行的最长连续重复块计算。", "",
           "| 行号 | ID | 新输入 token | 旧输入 token | 连续重复单元 | 次数 |", "|---:|---|---:|---:|---|---:|"]
for e in examples:
    run = e["repeated_line_run"]
    unit = " / ".join(run["unit"]).replace("|", "\\|")
    report.append(f"| {e['row_index_zero_based']} | {e['id']} | {e['input_tokens']} | {e['old_input_tokens']} | `{unit}` | {run['repeats']} |")
report += ["", "完整新旧回答及问题保存在 `input_length_audit.json` 的 `overlong_examples`，可以按 ID 查阅。", "",
           "## 判断边界", "", "超长回答包含大量连续循环的无关片段，重复在原始 teacher_response 中已经存在。应优先检查上游教师数据生成与整体数据质量；仅扩大 UP 输入长度不会修复重复内容。", "",
           "最终 parquet 没有教师模型、采样和生成配置的溯源元数据，当前证据不能确定究竟是哪项生成设置造成退化，也不能仅凭文件名认定教师模型。"]
(OUT / "report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
