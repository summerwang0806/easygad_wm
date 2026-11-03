#!/usr/bin/env python3
"""Generate SQuAD 1.1 dev answers and compute official-normalized EM / F1.

Normally edit MODEL_PATH, then run: python down/SQuAD/run_squad.py
No teacher, LLM judge, paid API, or task-specific model fine-tuning is used.
"""
from __future__ import annotations

import argparse
from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import statistics
import string
import sys
import time
from urllib.request import urlopen
import uuid


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

# 日常只改这一行。相对路径以项目根目录为基准，也支持服务器绝对路径。

# cleanwarmup_cleangad
# MODEL_PATH = "checkpoints/gad_05b_cleanwarmup_cleangad_control/warmup/global_step_1813/actor/huggingface"
# MODEL_PATH = "checkpoints/gad_05b_cleanwarmup_cleangad_control/gad/global_step_1813/actor/huggingface"


# kgwwarmup_kgwgad
# MODEL_PATH = "checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_new/gad/global_step_1813/actor/huggingface"
# MODEL_PATH = "checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_new/warmup/global_step_1813/actor/huggingface"


# para
MODEL_PATH = "checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_new1_dipper2stage/gad/global_step_1813/actor/huggingface"







TOKENIZER_PATH = "/shared/public_models/Qwen2.5-0.5B"  # 缺少 tokenizer 时，指定相同学生基座的本地目录。
DEVICE = "cuda:0"
DTYPE = "auto"
MAX_INPUT_TOKENS = 4096
MAX_NEW_TOKENS = 64
TEMPERATURE = 0.0
SEED = 42
PROMPT_STYLE = "chat"  # chat 使用学生 tokenizer 模板；completion 使用下方纯文本提示。
NUM_FEWSHOT = 0  # 恢复原始零样例评测；直接运行不使用训练集示例。
FEWSHOT_SEED = 42  # 所有对照固定相同的示例和顺序，不根据 dev 得分挑选。
LIMIT = None  # None = 全量 10570 题；也可用 --limit 8 试跑。

# WN 是生成时处理器；未洗组/UP/TP 学生保持 0。WN 组设置规则路径及正强度。
WN_RULES_PATH = None  # 例如 "wn/acl_rules_gad_Qwen2.5-0.5B_gamma0.5_delta3_fp32.json"
WN_STRENGTH = 0.0

DATASET_FILE = HERE / "data" / "dev-v1.1.json"
DATASET_URL = "https://rajpurkar.github.io/SQuAD-explorer/dataset/dev-v1.1.json"
TRAIN_DATASET_FILE = HERE / "data" / "train-v1.1.json"
TRAIN_DATASET_URL = "https://rajpurkar.github.io/SQuAD-explorer/dataset/train-v1.1.json"
RESULTS_DIR = HERE / "results"
EXPECTED_DEV_COUNT = 10570
EXPECTED_TRAIN_COUNT = 87599
PROTOCOL = "squad-v1.1-generative-short-answer-v2"
PROMPT_TEMPLATE = (
    "Read the passage and answer the question. The answer is a span from the passage. "
    "Output only the shortest answer span, with no explanation or prefix.\n\n"
    "Passage:\n{context}\n\nQuestion: {question}\nAnswer:"
)


def resolve_path(value: str | Path) -> Path:
    value = Path(value).expanduser()
    return (value if value.is_absolute() else ROOT / value).resolve()


def digest(value) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def now() -> str:
    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")


def normalize_answer(text: str) -> str:
    """SQuAD v1.1: lowercase, remove ASCII punctuation/articles, fix whitespace."""
    no_punctuation = "".join(char for char in text.lower() if char not in string.punctuation)
    no_articles = re.sub(r"\b(a|an|the)\b", " ", no_punctuation)
    return " ".join(no_articles.split())


def exact_match_score(prediction: str, reference: str) -> float:
    return float(normalize_answer(prediction) == normalize_answer(reference))


def f1_score(prediction: str, reference: str) -> float:
    """Original v1.1 word-overlap F1; this does not use the model tokenizer."""
    prediction_tokens = normalize_answer(prediction).split()
    reference_tokens = normalize_answer(reference).split()
    same = sum((Counter(prediction_tokens) & Counter(reference_tokens)).values())
    if same == 0:
        return 0.0
    precision = same / len(prediction_tokens)
    recall = same / len(reference_tokens)
    return 2 * precision * recall / (precision + recall)


def score_answer(prediction: str, references: list[str]) -> dict:
    if not references:
        raise ValueError("SQuAD 1.1 的每个问题都必须有人工答案。")
    # The maxima for EM and F1 are independent, as in the original evaluator.
    return {
        "exact_match": max(exact_match_score(prediction, ref) for ref in references),
        "f1": max(f1_score(prediction, ref) for ref in references),
    }


def parse_dataset(document: dict, expected_count: int | None = EXPECTED_DEV_COUNT) -> list[dict]:
    if not isinstance(document, dict) or document.get("version") != "1.1" or not isinstance(document.get("data"), list):
        raise ValueError("输入必须是官方 SQuAD 1.1 JSON（version=1.1、data 列表），不能使用 2.0。")
    rows, seen = [], set()
    for article in document["data"]:
        for paragraph in article["paragraphs"]:
            context = paragraph["context"]
            if not isinstance(context, str) or not context.strip():
                raise ValueError("SQuAD 段落缺少文本。")
            for qa in paragraph["qas"]:
                identity, question = qa["id"], qa["question"]
                if not isinstance(identity, str) or not identity or identity in seen:
                    raise ValueError(f"SQuAD ID 缺失或重复: {identity!r}")
                if not isinstance(question, str) or not question.strip() or qa.get("is_impossible", False):
                    raise ValueError(f"问题无效或不可回答（不是 1.1 配置）: {identity}")
                answers = qa.get("answers")
                if not isinstance(answers, list) or not answers:
                    raise ValueError(f"问题缺少人工答案: {identity}")
                references = []
                for answer in answers:
                    text, start = answer["text"], answer["answer_start"]
                    # Official EM/F1 use the annotated text, not character offsets.
                    # Preserve annotation quirks rather than reject/rewrite a gold answer.
                    if not isinstance(text, str) or not text or type(start) is not int or not 0 <= start < len(context):
                        raise ValueError(f"人工答案文本或段落位置无效: {identity}")
                    references.append(text)
                rows.append({"id": identity, "title": article.get("title", ""), "context": context,
                             "question": question, "references": references})
                seen.add(identity)
    if not rows or (expected_count is not None and len(rows) != expected_count):
        raise ValueError(f"SQuAD 1.1 文件应为 {expected_count} 题，读取到 {len(rows)} 题。")
    return rows


def load_data(path: Path, expected_count: int = EXPECTED_DEV_COUNT) -> list[dict]:
    return parse_dataset(json.loads(path.read_text(encoding="utf-8")), expected_count=expected_count)


def prepare_data(path: Path, *, url: str = DATASET_URL, expected_count: int = EXPECTED_DEV_COUNT,
                 max_bytes: int = 20 * 1024 * 1024) -> list[dict]:
    if path.is_file():
        rows = load_data(path, expected_count=expected_count)
        print(f"[Data] Reusing {path} ({len(rows)} questions)", flush=True)
        return rows
    print(f"[Data] Downloading official SQuAD 1.1: {url}", flush=True)
    with urlopen(url, timeout=90) as response:
        data = response.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise ValueError("下载超过预期大小，尚未保存。")
    rows = parse_dataset(json.loads(data.decode("utf-8")), expected_count=expected_count)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        temporary.write_bytes(data)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)
    print(f"[Data] Saved {path} ({len(rows)} questions)", flush=True)
    return rows


def prepare_examples(num_fewshot: int, dev_rows: list[dict], *, check_only: bool = False) -> tuple[list[dict], dict]:
    if num_fewshot == 0:
        # Original evaluation needs only dev; no training data or selection module.
        return [], {"num_fewshot": 0, "selection_seed": None, "source_split": None,
                    "examples": [], "train_sha256": None}
    if str(HERE) not in sys.path:
        sys.path.insert(0, str(HERE))
    import fewshot

    # This does not inspect dev references or scores when selecting demonstrations.
    provenance = {"num_fewshot": num_fewshot, "selection_seed": FEWSHOT_SEED,
                  "source_split": "train" if num_fewshot else None,
                  "selection_code_sha256": hashlib.sha256(Path(fewshot.__file__).read_bytes()).hexdigest(),
                  "selection_limits": {"max_context_chars": fewshot.MAX_CONTEXT_CHARS,
                                       "max_question_chars": fewshot.MAX_QUESTION_CHARS,
                                       "max_answer_words": fewshot.MAX_ANSWER_WORDS}}
    train_path = resolve_path(TRAIN_DATASET_FILE)
    if check_only and not train_path.is_file():
        raise FileNotFoundError("few-shot 需要 train-v1.1.json；请先运行 --prepare-data。")
    train = prepare_data(train_path, url=TRAIN_DATASET_URL, expected_count=EXPECTED_TRAIN_COUNT,
                         max_bytes=50 * 1024 * 1024)
    examples = fewshot.select_examples(train, num_fewshot, FEWSHOT_SEED,
                                      exclude_ids={row["id"] for row in dev_rows})
    provenance.update({"examples": examples,
                       "train_sha256": hashlib.sha256(train_path.read_bytes()).hexdigest()})
    print(f"[Few-shot] {num_fewshot} fixed TRAIN examples: {[example['id'] for example in examples]}", flush=True)
    return examples, provenance


def make_prompt(row: dict, examples: list[dict] | None = None):
    examples = examples or []
    prompt = PROMPT_TEMPLATE.format(context=row["context"], question=row["question"])
    if PROMPT_STYLE == "chat":
        messages = []
        for example in examples:
            messages.extend([
                {"role": "user", "content": PROMPT_TEMPLATE.format(context=example["context"], question=example["question"])},
                {"role": "assistant", "content": example["answer"]},
            ])
        return messages + [{"role": "user", "content": prompt}]
    if PROMPT_STYLE == "completion":
        demonstrations = [PROMPT_TEMPLATE.format(context=example["context"], question=example["question"])
                          + " " + example["answer"] for example in examples]
        return "\n\n".join([*demonstrations, prompt])
    raise ValueError("PROMPT_STYLE 只能为 chat 或 completion。")


@contextmanager
def cache_lock(directory: Path):
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / ".lock"
    try:
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as error:
        raise RuntimeError(f"同一配置已有运行锁: {path}；确认旧进程已经结束后再移除该锁。") from error
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(json.dumps({"pid": os.getpid(), "started": now()}))
        yield
    finally:
        path.unlink(missing_ok=True)


def load_cached(path: Path, rows: list[dict], protocol_hash: str) -> dict:
    if not path.exists():
        return {}
    expected = {row["id"]: row for row in rows}
    records = {}
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        identity = row["id"]
        if identity not in expected or identity in records or row.get("protocol_hash") != protocol_hash:
            raise ValueError(f"续跑缓存 ID/协议不匹配或重复，第 {line_number} 行: {path}")
        if not isinstance(row.get("raw_prediction"), str):
            raise ValueError(f"缓存缺少原始预测，第 {line_number} 行: {path}")
        records[identity] = row
    return records


def evaluate_predictions(rows: list[dict], predictions: dict[str, str]) -> tuple[dict, list]:
    required = {row["id"] for row in rows}
    if not isinstance(predictions, dict):
        raise ValueError("预测文件必须是 question_id -> answer 的 JSON 对象。")
    if set(predictions) != required or any(not isinstance(value, str) for value in predictions.values()):
        raise ValueError(f"预测必须与本次问题 ID 完全匹配：需要 {len(required)} 条，收到 {len(predictions)} 条。")
    scores = []
    for row in rows:
        prediction = predictions[row["id"]]
        scores.append({"id": row["id"], "title": row["title"], "question": row["question"],
                       "references": row["references"], "prediction": prediction,
                       "normalized_prediction": normalize_answer(prediction), **score_answer(prediction, row["references"])})
    count = len(scores)
    if not count:
        raise ValueError("没有待评问题。")
    em = sum(row["exact_match"] for row in scores) / count
    f1 = sum(row["f1"] for row in scores) / count
    prediction_lengths = [len(normalize_answer(value).split()) for value in predictions.values()]
    reference_lengths = [min(len(normalize_answer(ref).split()) for ref in row["references"]) for row in rows]
    return {"evaluated_examples": count, "exact_match": em * 100, "f1": f1 * 100,
            "exact_match_fraction": em, "f1_fraction": f1,
            "exact_match_correct": int(sum(row["exact_match"] for row in scores)),
            "empty_predictions": sum(not value.strip() for value in predictions.values()),
            "prediction_words_mean": statistics.mean(prediction_lengths),
            "prediction_words_median": statistics.median(prediction_lengths),
            "shortest_reference_words_median": statistics.median(reference_lengths)}, scores


def write_results(directory: Path, summary: dict, scores: list[dict], predictions: dict) -> Path:
    destination = directory / "runs" / (datetime.now(timezone(timedelta(hours=8))).strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:8])
    destination.mkdir(parents=True, exist_ok=False)
    for name, value in (("summary.json", summary), ("predictions.json", predictions)):
        (destination / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (destination / "scores.jsonl").open("w", encoding="utf-8") as stream:
        for row in scores:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    report = (
        f"# SQuAD 1.1 {'LIMITED RUN' if summary['limited_run'] else 'full dev'}\n\n"
        f"- Model: `{summary.get('model_path', 'external predictions')}`\n"
        f"- Questions: {summary['evaluated_examples']} / {summary['total_dev_examples']}\n"
        f"- Fixed train demonstrations: {summary.get('num_fewshot', 'external/unknown')}\n"
        f"- Median normalized answer words: prediction={summary['prediction_words_median']}, shortest reference={summary['shortest_reference_words_median']}\n"
        f"- WN strength: {summary.get('wn_strength', 'external/unknown')}\n"
        f"- Output-token limit hits: {summary.get('length_limited_predictions', 'external/unknown')}\n\n"
        "| Metric | Score (0-100) |\n|---|---:|\n"
        f"| EM | {summary['exact_match']:.4f} |\n| F1 | {summary['f1']:.4f} |\n\n"
        "Metrics use the original v1.1 normalization and maximum over human references.\n"
        "The complete generated answer is scored; no best-line/span extraction or judge is used.\n"
        "Limited runs are for debugging, not final paper results.\n"
    )
    (destination / "report.md").write_text(report, encoding="utf-8")
    return destination


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--prepare-data", action="store_true", help="准备官方 dev；显式开启 few-shot 时另准备 train，不加载模型/GPU")
    modes.add_argument("--check-only", action="store_true", help="只检查数据、配置、模型和 tokenizer，不生成")
    modes.add_argument("--score-only", action="store_true", help="只评测已有 id->answer 的 predictions.json")
    parser.add_argument("--predictions-file", type=Path, help="--score-only 使用的预测文件")
    parser.add_argument("--limit", type=int, default=LIMIT, help="只取官方顺序前 N 题试跑")
    parser.add_argument("--num-fewshot", type=int, default=NUM_FEWSHOT, help="训练示例数，默认 %(default)s（原始零样例）；3 用于复现 few-shot 实验")
    args = parser.parse_args(argv)
    if args.limit is not None and (type(args.limit) is not int or args.limit < 1):
        parser.error("LIMIT / --limit 必须为正整数或 None。")
    if type(args.num_fewshot) is not int or args.num_fewshot < 0:
        parser.error("NUM_FEWSHOT / --num-fewshot 必须为非负整数。")
    if type(FEWSHOT_SEED) is not int or FEWSHOT_SEED < 0:
        parser.error("FEWSHOT_SEED 必须为非负整数。")
    if args.score_only != (args.predictions_file is not None):
        parser.error("--score-only 和 --predictions-file 必须一起使用。")
    data_path = resolve_path(DATASET_FILE)
    if args.prepare_data:
        dev = prepare_data(data_path)
        prepare_examples(args.num_fewshot, dev)
        return 0
    if args.check_only and not data_path.is_file():
        raise FileNotFoundError("请先运行 python down/SQuAD/run_squad.py --prepare-data")
    rows = load_data(data_path) if data_path.is_file() else prepare_data(data_path)
    all_rows = rows
    rows = rows if args.limit is None else rows[:args.limit]
    data_hash = hashlib.sha256(data_path.read_bytes()).hexdigest()

    if args.score_only:
        predictions = json.loads(resolve_path(args.predictions_file).read_text(encoding="utf-8"))
        summary, scores = evaluate_predictions(rows, predictions)
        summary.update({"protocol": PROTOCOL, "created_at": now(), "mode": "score_only", "dataset_sha256": data_hash,
                        "total_dev_examples": len(all_rows), "limited_run": args.limit is not None,
                        "predictions_file": str(resolve_path(args.predictions_file))})
        output = write_results(RESULTS_DIR / "external", summary, scores, predictions)
    else:
        examples, fewshot_protocol = prepare_examples(args.num_fewshot, all_rows, check_only=args.check_only)
        if str(HERE.parent) not in sys.path:
            sys.path.insert(0, str(HERE.parent))
        from generation_utils import LocalGenerator, sha256_file

        model_path = resolve_path(MODEL_PATH)
        tokenizer_path = resolve_path(TOKENIZER_PATH) if TOKENIZER_PATH is not None else model_path
        rules_path = resolve_path(WN_RULES_PATH) if WN_RULES_PATH is not None else None
        generator = LocalGenerator(
            model_path, tokenizer_path=tokenizer_path, device=DEVICE, dtype=DTYPE,
            max_input_tokens=MAX_INPUT_TOKENS, max_new_tokens=MAX_NEW_TOKENS, seed=SEED,
            wn_rules_path=rules_path, wn_strength=WN_STRENGTH, enable_thinking=False,
        )
        try:
            metadata = generator.check()
            if PROMPT_STYLE not in {"chat", "completion"}:
                raise ValueError("PROMPT_STYLE 只能为 chat 或 completion。")
            if PROMPT_STYLE == "chat" and not metadata.get("chat_template_present"):
                raise ValueError("学生 tokenizer 缺少 chat_template；设置对应 TOKENIZER_PATH，或明确使用 PROMPT_STYLE='completion'。")
            protocol = {
                "protocol": PROTOCOL, "dataset_sha256": data_hash,
                "model": metadata["model"], "tokenizer": metadata["tokenizer"],
                "runtime_versions": metadata["versions"], "runtime_sha256": metadata.get("runtime_sha256"),
                "runner_sha256": sha256_file(Path(__file__)),
                "prompt_template": PROMPT_TEMPLATE, "prompt_style": PROMPT_STYLE,
                "fewshot": fewshot_protocol,
                "max_input_tokens": MAX_INPUT_TOKENS, "max_new_tokens": MAX_NEW_TOKENS,
                "temperature": TEMPERATURE, "seed": SEED, "dtype": DTYPE,
                "rules_sha256": sha256_file(rules_path) if rules_path is not None else None,
                "wn_strength": WN_STRENGTH,
            }
            protocol_hash = digest(protocol)
            print(f"[Protocol] SQuAD 1.1 dev, {len(rows)}/{len(all_rows)} questions; prompt={PROMPT_STYLE}, {args.num_fewshot}-shot, WN={WN_STRENGTH}", flush=True)
            if args.check_only:
                print("[OK] 数据和本地模型检查通过，尚未加载权重/生成。", flush=True)
                return 0
            # Keep paths short enough for Windows test/development environments.
            model_tag = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(model_path))[-48:]
            cache_dir = RESULTS_DIR / f"{model_tag}.{protocol_hash[:16]}"
            started = time.monotonic()
            with cache_lock(cache_dir):
                cached = load_cached(cache_dir / "generations.jsonl", all_rows, protocol_hash)
                (cache_dir / "protocol.json").write_text(json.dumps(protocol, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                (cache_dir / "fewshot_examples.json").write_text(json.dumps(fewshot_protocol, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                reused = sum(row["id"] in cached for row in rows)
                print(f"[Resume] Reusing {reused}/{len(rows)} answers", flush=True)
                with (cache_dir / "generations.jsonl").open("a", encoding="utf-8") as stream:
                    for index, row in enumerate(rows):
                        identity = row["id"]
                        if identity not in cached:
                            answer = generator.generate(make_prompt(row, examples), temperature=TEMPERATURE, seed=SEED + index)
                            if not isinstance(answer.get("text"), str):
                                raise ValueError(f"生成器未返回文本: {identity}")
                            record = {"id": identity, "protocol_hash": protocol_hash,
                                      "raw_prediction": answer["text"], "generation": answer}
                            stream.write(json.dumps(record, ensure_ascii=False) + "\n")
                            stream.flush()
                            os.fsync(stream.fileno())
                            cached[identity] = record
                        if index == 0 or (index + 1) % 20 == 0 or index + 1 == len(rows):
                            print(f"[SQuAD] {index + 1}/{len(rows)} answers available", flush=True)
                predictions = {row["id"]: cached[row["id"]]["raw_prediction"] for row in rows}
                summary, scores = evaluate_predictions(rows, predictions)
                summary.update({"protocol": PROTOCOL, "created_at": now(), "mode": "generate_and_score",
                                "model_path": str(model_path), "tokenizer_path": str(tokenizer_path),
                                "protocol_hash": protocol_hash, "dataset_sha256": data_hash,
                                "total_dev_examples": len(all_rows), "limited_run": args.limit is not None,
                                "num_fewshot": args.num_fewshot, "fewshot": fewshot_protocol,
                                "wn_strength": WN_STRENGTH, "rules_path": str(rules_path) if rules_path is not None else None,
                                "generation_metadata": metadata, "reused_answers": reused,
                                "length_limited_predictions": sum(cached[row["id"]]["generation"].get("finish_reason") == "length" for row in rows),
                                "elapsed_seconds": time.monotonic() - started})
                output = write_results(cache_dir, summary, scores, predictions)
        finally:
            generator.close()
    print(f"\n[{'LIMITED RUN' if args.limit is not None else 'FULL DEV'}] EM={summary['exact_match']:.4f}  F1={summary['f1']:.4f} (0-100)")
    print(f"[Saved] {output}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, RuntimeError, ImportError) as error:
        print(f"[FAILED] {type(error).__name__}: {error}", file=sys.stderr)
        print("详见 down/SQuAD/README.md；成功生成的逐题缓存会保留，可原命令续跑。", file=sys.stderr)
        raise SystemExit(1)
