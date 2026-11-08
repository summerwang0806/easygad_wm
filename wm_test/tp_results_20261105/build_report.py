"""Read-only CPU verification of the downloaded TP experiment and its caches."""

from collections import Counter
from functools import lru_cache
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import statistics
import sys

import pyarrow.parquet as pq

def load_porter_stemmer():
    try:
        from nltk.stem.porter import PorterStemmer
        return PorterStemmer()
    except ModuleNotFoundError:
        # This machine has NLTK's pure-Python stemmer but lacks an unrelated
        # tokenizer dependency. Load the installed stemmer/interface unchanged,
        # replacing only the package import, without installing anything.
        package = Path(importlib.util.find_spec("nltk").origin).parent
        api_path = package / "stem/api.py"
        spec = importlib.util.spec_from_file_location("_tp_stem_api", api_path)
        api = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(api)
        porter_path = package / "stem/porter.py"
        source = porter_path.read_text(encoding="utf-8")
        statement = "from nltk.stem.api import StemmerI"
        assert source.count(statement) == 1
        namespace = {"__name__": "_tp_porter", "StemmerI": api.StemmerI}
        exec(compile(source.replace(statement, ""), str(porter_path), "exec"), namespace)
        return namespace["PorterStemmer"]()

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from wm_test import evaluate_compare_metrics as evaluator

STEMMER = load_porter_stemmer()


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def hashes(path):
    raw = path.read_bytes()
    return {"raw": hashlib.sha256(raw).hexdigest(),
            "lf": hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()}


@lru_cache(maxsize=100000)
def stem(word):
    return STEMMER.stem(word) if len(word) > 3 else word


def tokens(text):
    return [stem(word) for word in re.sub(r"[^a-z0-9]+", " ", text.lower()).split()]


def rouge_l(reference, answer):
    ref, hyp = tokens(reference), tokens(answer)
    if not ref or not hyp:
        return 0.0
    # Bit-parallel LCS length, with the same tokenization/stemming as rouge_score.
    positions = {}
    for index, word in enumerate(ref):
        positions[word] = positions.get(word, 0) | (1 << index)
    state = 0
    for word in hyp:
        combined = state | positions.get(word, 0)
        state = combined & ~(combined - ((state << 1) | 1))
    return 2 * state.bit_count() / (len(ref) + len(hyp))


def history_records():
    text = (ROOT / "wm_test/detection_metrics_history.md").read_text(encoding="utf-8")
    result = {}
    for match in re.finditer(r"```json\s*(\{.*?\})\s*```", text, re.S):
        try:
            record = json.loads(match.group(1))
        except ValueError:
            continue
        if record.get("kgw_file"):
            result[Path(record["kgw_file"]).name] = record
    return result


def close(actual, expected):
    assert math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-12), (actual, expected)


def grouped_summary(cache, source_hashes):
    assert cache["signature"]["source_sha256"] in source_hashes.values()
    detector = cache["signature"]["detector"]
    assert detector["gamma"] == .5 and detector["hash_key"] == 15485863
    result = {}
    for budget in ("1000", "2000", "3000"):
        block = cache["budgets"][budget]
        groups = block["groups"]
        median = statistics.median(group["p_value"] for group in groups)
        close(median, block["median_p_value"])
        for group in groups:
            n = group["num_tokens_scored"]
            z = (group["green_tokens"] - .5 * n) / math.sqrt(.25 * n)
            close(z, group["z_score"])
            close(.5 * math.erfc(z / math.sqrt(2)), group["p_value"])
        result[budget] = {"median": median, "groups": len(groups)}
    return result


def inspect_file(path, history, negative, dolly, teacher):
    rows = read_jsonl(path)
    by_id = {row["id"]: row for row in rows}
    assert len(rows) == len(by_id) == 500 and set(by_id) == set(negative)
    source_hashes = hashes(path)
    config = evaluator.validate_detector_pair(path, ROOT / "wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl")
    assert config["gamma"] == .5 and config["hash_key"] == 15485863
    assert all(not row["generation"]["kgw_enabled_during_generation"] for row in rows)
    detection = evaluator.evaluate(negative, {key: row["z_score"] for key, row in by_id.items()})
    close(detection["auroc"], history["auroc"])
    independent_auc = sum((row["z_score"] > score) + .5 * (row["z_score"] == score)
                          for row in rows for score in negative.values()) / 250000
    close(independent_auc, detection["auroc"])
    all_scores = [math.inf] + sorted(set([*negative.values(), *(row["z_score"] for row in rows)]), reverse=True)
    for name, point in detection["tpr_at_fpr"].items():
        target = float(name.rstrip("%")) / 100
        attainable = []
        for threshold in all_scores:
            fp = sum(value >= threshold for value in negative.values())
            tp = sum(row["z_score"] >= threshold for row in rows)
            if fp / 500 <= target:
                attainable.append(tp / 500)
        close(max(attainable), point["tpr"])
        close(point["tpr"], history["tpr_at_fpr"][name]["tpr"])
    seq = evaluator.evaluate_seq_rep3(path)
    close(seq["mean"], history["seq_rep_3"]["kgw"]["mean"])
    close(seq["median"], history["seq_rep_3"]["kgw"]["median"])
    raw_cache = json.loads(path.with_suffix(".grouped_p_values.json").read_text(encoding="utf-8"))
    filtered_cache = json.loads(path.with_suffix(".nonrepetitive_grouped_p_values.json").read_text(encoding="utf-8"))
    grouped = grouped_summary(raw_cache, source_hashes)
    filtered = grouped_summary(filtered_cache, source_hashes)
    filtering = filtered_cache["filtering"]
    excluded = [record["id"] for record in filtering["per_answer"]
                if (1 - record["num_unique_pairs"] / record["num_pairs"] if record["num_pairs"] else 0) > .5]
    assert excluded == filtering["removed_answer_ids"]
    assert {record["id"] for record in filtering["per_answer"]} == set(by_id)
    assert len(excluded) == filtering["num_answers_removed"]
    assert all(record["num_tokens"] == by_id[record["id"]]["num_tokens"] for record in filtering["per_answer"])
    ppl_path = next(path.parent.glob(path.stem + ".ppl.*.jsonl"))
    ppl_cache = read_jsonl(ppl_path)
    assert ppl_cache[0]["source_sha256"] in source_hashes.values()
    samples = [record for record in ppl_cache if record.get("type") == "sample"]
    assert len(samples) == 500 and {record["id"] for record in samples} == set(by_id)
    ppl_values = []
    for sample in samples:
        assert sample["answer_sha256"] == hashlib.sha256(by_id[sample["id"]]["answer"].encode("utf-8")).hexdigest()
        if sample["status"] == "ok":
            close(math.exp(sample["nll_sum"] / sample["scored_tokens"]), sample["ppl"])
            ppl_values.append(sample["ppl"])
    ppl_median = statistics.median(ppl_values)
    close(ppl_median, history["ppl"]["files"]["kgw"]["median_per_answer_ppl"])
    assert set(dolly) == set(teacher) == set(by_id)
    per_answer = []
    for row in rows:
        sample_id = row["id"]
        assert row["prompt"] == dolly[sample_id]["prompt"] == teacher[sample_id]["content"]
        per_answer.append({"id": sample_id, "rouge_dolly": rouge_l(dolly[sample_id]["answer"], row["answer"]),
                           "rouge_teacher_clean": rouge_l(teacher[sample_id]["teacher_response"], row["answer"])})
    rouge_dolly = statistics.mean(row["rouge_dolly"] for row in per_answer)
    rouge_teacher = statistics.mean(row["rouge_teacher_clean"] for row in per_answer)
    close(rouge_dolly, history["rouge_l_dolly"]["mean"])
    close(rouge_teacher, history["rouge_l_teacher_clean"]["mean"])
    return {"source": str(path), "source_sha256": source_hashes, "samples": 500,
            "evaluation_timestamp": history["evaluated_at"], "detector": config, "detection": detection,
            "rouge_dolly": rouge_dolly, "rouge_teacher_clean": rouge_teacher,
            "seq_rep3_mean": seq["mean"], "seq_rep3_median": seq["median"],
            "severe_repetition_count": len(excluded), "severe_repetition_rate": len(excluded) / 500,
            "grouped_p_values": grouped, "filtered_grouped_p_values": filtered,
            "ppl_median": ppl_median, "ppl_valid_samples": len(ppl_values), "ppl_cache": str(ppl_path),
            "ppl_reference_configuration": ppl_cache[0]["configuration"],
            "mean_answer_tokens": statistics.mean(row["num_tokens"] for row in rows),
            "median_answer_tokens": statistics.median(row["num_tokens"] for row in rows),
            "median_z_score": statistics.median(row["z_score"] for row in rows),
            "model_paths": sorted({row["model_path"] for row in rows}), "generation": rows[0]["generation"],
            "llm_judge_clean_gad": None, "llm_judge_clean_teacher": None,
            "llm_judge_kgw_teacher": None, "llm_mt_bench": None,
            "per_answer_reference_metrics": per_answer}


def main():
    history = history_records()
    base = ROOT / "wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl"
    negative = evaluator.load_scores(base, "clean", False)
    dolly_path = ROOT / "text_quality/references/dolly_human_500.jsonl"
    teacher_path = ROOT / "data/dolly15k_qwen2_5_14b_clean_test.parquet"
    dolly = {row["id"]: row for row in read_jsonl(dolly_path)}
    teacher = {row["id"]: row for row in pq.read_table(teacher_path).to_pylist()}
    results = {}
    for stage in ("warmup", "gad"):
        path = ROOT / f"wm_test/tp2.5warmup_tp2.5gad_{stage}_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl"
        results[stage] = inspect_file(path, history[path.name], negative, dolly, teacher)
    baselines = {}
    for label, name in {
        "no_attack_gad": "kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.jsonl",
        "clean_gad": "cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl",
    }.items():
        path = ROOT / "wm_test" / name
        record = history[name]
        metrics = evaluator.evaluate(negative, evaluator.load_scores(path, "kgw", True))
        close(metrics["auroc"], record["auroc"])
        assert record["seq_rep_3"]["kgw"]["source_sha256"] in hashes(path).values()
        filtered_cache = json.loads(path.with_suffix(".nonrepetitive_grouped_p_values.json").read_text())
        assert filtered_cache["signature"]["source_sha256"] in hashes(path).values()
        baselines[label] = {"source": str(path), "detection": metrics,
                            "rouge_dolly": record["rouge_l_dolly"]["mean"],
                            "rouge_teacher_clean": record["rouge_l_teacher_clean"]["mean"],
                            "severe_repetition_count": filtered_cache["filtering"]["num_answers_removed"],
                            "seq_rep3_mean": evaluator.evaluate_seq_rep3(path)["mean"],
                            "ppl_median": record["ppl"]["files"]["kgw"]["median_per_answer_ppl"]}
    report = {"experiment": "TP strength=2.5; TP Warmup + TP GAD; warmup-derived rules",
              "results": results, "baselines": baselines,
              "reference_hashes": {"negative_base": hashes(base), "dolly": hashes(dolly_path), "clean_teacher": hashes(teacher_path)},
              "missing": "No matching TP Qwen-32B pairwise judge or MT-Bench evaluation was found locally.",
              "verification": "CPU-only independent ROC/Seq-Rep-3/ROUGE recomputation; cache hash, grouped p median and per-answer PPL verification. No model inference."}
    (OUT / "tp_metrics.json").write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    headers = ["模型/方式", "AUROC", "TPR@FPR≤5%", "TPR@FPR≤10%", "ROUGE-L（原始Dolly）", "ROUGE-L（clean教师）", "严重重复输出", "Seq-Rep-3均值", "Seq-Rep-3中位数", "PPL中位数", "LLM judge vs clean GAD", "LLM judge vs clean教师", "LLM judge vs KGW教师", "LLM-MT-Bench", "p中位数1k", "p中位数2k", "p中位数3k", "剔除严重重复后p中位数1k", "剔除严重重复后p中位数2k", "剔除严重重复后p中位数3k"]
    lines = ["# TP Warmup / GAD 结果汇总", "", "核对日期：2026-11-05。每份输出均为 500 条，模型 checkpoint 为相应阶段的 global_step_1813；推理阶段未额外施加 KGW 或 WN 偏置。", "", "| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    for stage, r in results.items():
        d = r["detection"]
        values = [stage, f"{d['auroc']:.6f}", f"{d['tpr_at_fpr']['5%']['tpr']:.2%}", f"{d['tpr_at_fpr']['10%']['tpr']:.2%}", f"{r['rouge_dolly']:.6f}", f"{r['rouge_teacher_clean']:.6f}", f"{r['severe_repetition_count']}/500（{r['severe_repetition_rate']:.2%}）", f"{r['seq_rep3_mean']:.6f}", f"{r['seq_rep3_median']:.6f}", f"{r['ppl_median']:.6f}", "—", "—", "—", "—"]
        values += [f"{r[key][str(b)]['median']:.6f}" for key in ("grouped_p_values", "filtered_grouped_p_values") for b in (1000, 2000, 3000)]
        lines.append("| " + " | ".join(values) + " |")
    lines += ["", "## 计算口径", "", "- 检测参数：gamma=0.5、delta=3、hash_key=15485863。正类为 TP 学生输出，负类为同批 500 条原始未训练 Qwen2.5-0.5B 输出。两阶段 5% 工作点实际 FPR 均为 4.6%，10% 工作点实际 FPR 均为 10.0%。",
              "- ROUGE-L 为同题逐回答 F1 的等权平均；英文小写/字母数字分词、长度大于 3 的词做 Porter stemming，采用 LCS。独立实现与保存的评估结果一致。参考实现：[Google ROUGE scorer](https://github.com/google-research/google-research/blob/master/rouge/rouge_scorer.py)、[tokenize](https://github.com/google-research/google-research/blob/master/rouge/tokenize.py)。",
              "- 严重重复为回答内部相邻 tokenizer token 对的重复比例 > 0.5，不含 prompt；依据绑定相同源文件哈希的逐回答缓存复核。",
              "- Seq-Rep-3 按 answer.split() 的词级三元组计算，保留大小写和标点，不跨回答，均值和中位数均使用全部 500 条。",
              "- PPL 为固定 Llama-3-8B 参考模型的逐回答 PPL 中位数，两个阶段各 500 条有效记录；不是 token 加权总体 PPL。已核对缓存的来源哈希、回答哈希和 NLL/PPL 数值。",
              "- 表中后三列对应原表的‘去重后’，实际是剔除严重重复的整条回答后重新拼接、按精确 1k/2k/3k token 块分组。Warmup 保留 392 条，GAD 保留 457 条；组内没有去除重复 token 对。不要与 unique-token-pair 检测混称。",
              "- 原始分组数 Warmup 为 179/89/59，GAD 为 87/43/29；筛选后为 57/28/19 和 55/27/18。每块首 token 只作上下文，尾部不足一块丢弃，最后对完整块的 p-value 取普通中位数。",
              "- 四项 LLM judge / MT-Bench 指标未发现本次实验的对应结果，留空，不用 ROUGE 或 PPL 替代。",
              "- p-value 接近 1 表示当前单侧正向 KGW 检验缺乏证据，不是‘无水印概率’。AUROC 小于 0.5 反映打分方向上的偏移，不足以证明所有检测方法都无法识别。", "", "## 对照与解读", "",
              "TP GAD 的正向检测明显弱于匹配的无攻击 GAD：AUROC 0.647688 → 0.447162，TPR@FPR≤5% 11.4% → 3.4%，TPR@FPR≤10% 22.8% → 5.8%。",
              "TP GAD 相比 TP Warmup，ROUGE-L（Dolly）0.166714 → 0.207037、ROUGE-L（clean教师）0.229723 → 0.257639，严重重复 21.6% → 8.6%，Seq-Rep-3 均值 0.222037 → 0.114053。GAD 改善了这组 TP 学生的文本质量指标。",
              "相对无攻击 GAD，TP GAD 的 clean 教师 ROUGE-L 从 0.309174 降至 0.257639，严重重复从 2.2% 增至 8.6%，说明去水印伴随质量代价。与 clean GAD 的 0.330629 相比，词序重合也更低；还需要 LLM judge 评估内容正确性和实用性。",
              "PPL 中位数 Warmup/GAD 约 3.163/3.172，基本不变；不能以较低 PPL 单独判断回答更正确，特别是这里仍有明显重复。", "", "## 来源", ""]
    for stage, r in results.items():
        lines += [f"- {stage}：`{Path(r['source']).name}`；评估时间 `{r['evaluation_timestamp']}`；LF SHA-256 `{r['source_sha256']['lf']}`。"]
    lines += ["- 原始评估历史：`wm_test/detection_metrics_history.md`。精确值、缓存配置和逐回答 ROUGE 见同目录 `tp_metrics.json`。",
              "- 仅分析已下载文件，未重新生成回答、训练模型或调用外部裁判。"]
    (OUT / "tp_filled_results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    for stage, r in results.items():
        print(json.dumps({"stage": stage, **{key: r[key] for key in ("rouge_dolly", "rouge_teacher_clean", "severe_repetition_count", "seq_rep3_mean", "seq_rep3_median", "ppl_median", "median_z_score", "mean_answer_tokens")}, "auroc": r["detection"]["auroc"], "tpr5": r["detection"]["tpr_at_fpr"]["5%"], "tpr10": r["detection"]["tpr_at_fpr"]["10%"], "p": r["grouped_p_values"], "p_filtered": r["filtered_grouped_p_values"], "hashes": r["source_sha256"]}))


if __name__ == "__main__":
    main()
