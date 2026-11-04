#!/usr/bin/env python3
"""Score existing wm_test/wn answers; never load an LLM or generate answers."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from new_detect.core import roc, score_records
from wm_test.grouped_pvalues import tokenizer_signature

VERSION = "radioactivity-simple1-closed-v1"
KEY = 15485863
GAMMA = .5


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    tmp.replace(path)


def load_rows(path, spec):
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not rows:
        raise ValueError(f"Empty source: {path}")
    ids = set()
    config = None
    for row in rows:
        sid = row.get("id")
        if not isinstance(sid, str) or not sid or sid in ids:
            raise ValueError(f"Missing/duplicate sample ID: {path}: {sid}")
        ids.add(sid)
        if not isinstance(row.get("answer"), str) or not row.get("prompt"):
            raise ValueError(f"Missing prompt/answer: {path}: {sid}")
        kgw = row.get("kgw", {})
        current = {k: kgw.get(k) for k in ("gamma", "delta", "hash_key", "seeding")}
        if config is not None and current != config:
            raise ValueError(f"Mixed detector configurations: {path}")
        config = current
        if kgw.get("gamma") != GAMMA or kgw.get("hash_key") != KEY or not str(kgw.get("seeding", "")).startswith("simple_1"):
            raise ValueError(f"Expected gamma=.5, key={KEY}, simple_1: {path}: {sid}")
        if spec["role"] != "clean" and kgw.get("delta") != 3:
            raise ValueError(f"Target is not delta=3: {path}: {sid}")
        gen = row.get("generation", {})
        if gen.get("kgw_enabled_during_generation") is not False:
            raise ValueError(f"Source must explicitly disable inference KGW: {path}: {sid}")
        if "strength" in spec and (row.get("attack", {}).get("method") != "WN" or
                                   row["attack"].get("strength") != spec["strength"]):
            raise ValueError(f"WN strength mismatch: {path}: {sid}")
        n, g = row.get("num_tokens"), row.get("green_tokens")
        if type(n) is not int or type(g) is not int or not 0 <= g <= n:
            raise ValueError(f"Invalid saved counts: {path}: {sid}")
        z = (g - .5 * n) / math.sqrt(.25 * n) if n else 0.
        if not math.isclose(z, float(row["z_score"]), abs_tol=1e-8, rel_tol=1e-8):
            raise ValueError(f"Saved raw score contradicts metadata: {path}: {sid}")
    return rows


def inventory(args):
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    specs = manifest["experiments"]
    names = [s["name"] for s in specs]
    if len(names) != len(set(names)) or any(not re.fullmatch(r"[A-Za-z0-9_]+", x) for x in names):
        raise ValueError("Manifest names must be unique filename-safe identifiers")
    reference = args.reference or manifest["reference"]
    if reference not in names or next(s for s in specs if s["name"] == reference)["role"] != "clean":
        raise ValueError("Reference must name a manifest clean source")
    if args.experiments:
        unknown = set(args.experiments) - set(names)
        if unknown:
            raise ValueError(f"Unknown experiments: {unknown}")
        specs = [s for s in specs if s["name"] in set(args.experiments) | {reference}]
    datasets, sources = {}, {}
    for spec in specs:
        path = ROOT / spec["path"]
        rows = load_rows(path, spec)
        datasets[spec["name"]] = rows
        sources[spec["name"]] = dict(spec, sha256=digest(path), rows=len(rows),
            saved_raw_tokens=sum(r["num_tokens"] for r in rows), detector=rows[0]["kgw"],
            model_paths=sorted({r["model_path"] for r in rows}),
            note="Role comes from manifest, not legacy label; clean delta is metadata only" if spec["role"] == "clean" else "")
    base = {r["id"]: r for r in datasets[reference]}
    for name, rows in datasets.items():
        if {r["id"] for r in rows} != set(base):
            raise ValueError(f"Prompt IDs differ from reference: {name}")
        if any(r["prompt"] != base[r["id"]]["prompt"] for r in rows):
            raise ValueError(f"Prompt contents differ from reference: {name}")
        # Fixed reference order, never rank/order by detector score.
        by_id = {r["id"]: r for r in rows}
        datasets[name] = [by_id[k] for k in base]
    teacher_path = args.teacher_filter or ROOT / manifest["teacher_filter"]
    teacher = None
    if args.filter_mode != "none":
        if not teacher_path.is_file():
            raise FileNotFoundError(f"Missing teacher filter corpus: {teacher_path}")
        teacher = dict(path=str(teacher_path), sha256=digest(teacher_path),
                       field=args.teacher_field, min_count=args.filter_min_count)
    return specs, datasets, sources, reference, teacher


def generation_path(row, override):
    if override:
        return str(override)
    if row.get("attack", {}).get("method") == "WN":
        return row["attack"]["tokenizer"]["name_or_path"]
    return row["model_path"]


class CudaTokenizerScorer:
    def __init__(self, args):
        import torch
        if not str(args.device).startswith("cuda") or not torch.cuda.is_available():
            raise RuntimeError("First scoring requires CUDA: CPU KGW RNG produces different green lists.")
        from transformers import AutoTokenizer
        from wm_data.kgw import KGWConfig, KGWLogitsProcessor
        self.torch, self.AutoTokenizer = torch, AutoTokenizer
        self.device = torch.device(args.device)
        self.tokenizers = {}
        self.tokenizer = self.get_tokenizer(str(args.tokenizer))
        self.processor = KGWLogitsProcessor(len(self.tokenizer), KGWConfig(gamma=.5, delta=3, hash_key=KEY))
        self.pairs = {}
        self.args = args

    def get_tokenizer(self, path):
        if path not in self.tokenizers:
            self.tokenizers[path] = self.AutoTokenizer.from_pretrained(path, local_files_only=True, trust_remote_code=False)
        return self.tokenizers[path]

    def encode(self, row):
        prompt = row["prompt"]
        if isinstance(prompt, list):
            gen = self.get_tokenizer(generation_path(row, self.args.generation_tokenizer))
            prompt = gen.apply_chat_template(prompt, add_generation_prompt=True, tokenize=False)
            ids = gen.encode(prompt, add_special_tokens=False)
            settings = row.get("generation", {})
            limit = int(settings.get("max_prompt_tokens", 2048))
            if settings.get("prompt_truncated") is False:
                if len(ids) > limit or ("prompt_tokens" in settings and len(ids) != settings["prompt_tokens"]):
                    raise ValueError(f"WN prompt/tokenizer mismatch: {row['id']}")
            elif len(ids) > limit:
                prompt = gen.decode(ids[:limit], skip_special_tokens=False)
        if not isinstance(prompt, str):
            raise ValueError("Unsupported prompt representation")
        prompt_ids = self.tokenizer.encode(prompt, add_special_tokens=False)
        if not prompt_ids:
            raise ValueError("Cannot reconstruct an empty prompt")
        answer_ids = self.tokenizer.encode(row["answer"], add_special_tokens=False)
        if len(answer_ids) != row["num_tokens"]:
            raise ValueError(f"Teacher tokenizer answer length mismatch: {row['id']}")
        return dict(id=row["id"], prompt_ids=prompt_ids, answer_ids=answer_ids)

    def prepare(self, rows):
        records = [self.encode(row) for row in rows]
        needed = defaultdict(set)
        for record in records:
            previous = record["prompt_ids"][-1]
            for token in record["answer_ids"]:
                if (previous, token) not in self.pairs:
                    needed[previous].add(token)
                previous = token
        for i, (previous, tokens) in enumerate(sorted(needed.items()), 1):
            ordered = sorted(tokens)
            mask = self.torch.zeros(self.processor.vocab_size, dtype=self.torch.bool, device=self.device)
            mask[self.processor._greenlist(previous, self.device)] = True
            flags = mask[self.torch.tensor(ordered, device=self.device)].tolist()
            self.pairs.update(((previous, token), int(flag)) for token, flag in zip(ordered, flags))
            if i % 1000 == 0:
                print(f"  CUDA green lists {i}/{len(needed)} contexts", flush=True)
        for record, row in zip(records, rows):
            previous = record["prompt_ids"][-1]
            flags = []
            for token in record["answer_ids"]:
                flags.append(self.pairs[previous, token])
                previous = token
            if sum(flags) != row["green_tokens"]:
                raise ValueError(f"Saved raw green count mismatch: {row['id']}; check tokenizer/template/key/CUDA RNG")
            record["green_flags"] = flags
        return records


def teacher_contexts(teacher, tokenizer, evaluation_ids):
    """Filter contains only input context frequencies, never student green scores."""
    from collections import Counter
    path = Path(teacher["path"])
    if path.suffix == ".parquet":
        import pyarrow.parquet as pq
        rows = pq.read_table(path).to_pylist()
    else:
        rows = [json.loads(s) for s in path.read_text(encoding="utf-8").splitlines() if s.strip()]
    counts = Counter()
    overlap = set()
    for row in rows:
        text = row.get(teacher["field"])
        if not isinstance(text, str):
            raise ValueError(f"Teacher data must contain text field {teacher['field']}")
        if row.get("id") in evaluation_ids:
            overlap.add(row["id"])
        ids = tokenizer.encode(text, add_special_tokens=False)
        counts.update(ids[:-1])  # answer-internal contexts only, no synthetic boundaries
    if overlap:
        raise ValueError(f"Teacher filter overlaps evaluation prompt IDs ({len(overlap)}); use a separate filter corpus")
    allowed = sorted(k for k, count in counts.items() if count >= teacher["min_count"])
    if not allowed:
        raise ValueError("Empty teacher context filter")
    return dict(context_ids=allowed, source_rows=len(rows), unique_contexts=len(counts), kept_contexts=len(allowed))


def validate_cache(payload, source, rows):
    if payload.get("version") != VERSION or payload.get("source_sha256") != source["sha256"]:
        raise ValueError("Cache source/version mismatch")
    if payload.get("gamma") != GAMMA or payload.get("hash_key") != KEY or payload.get("rng") != "cuda":
        raise ValueError("Cache detector mismatch")
    records = payload["records"]
    if [r["id"] for r in records] != [r["id"] for r in rows]:
        raise ValueError("Cache sample order mismatch")
    vocab = payload["vocab_size"]
    if type(vocab) is not int or vocab < 2:
        raise ValueError("Invalid cached vocabulary")
    for record, row in zip(records, rows):
        tokens, flags = record["answer_ids"], record["green_flags"]
        if not record["prompt_ids"] or len(tokens) != row["num_tokens"] or len(flags) != len(tokens):
            raise ValueError("Cache token counts differ from saved source")
        if any(type(t) is not int or not 0 <= t < vocab for t in tokens + record["prompt_ids"]):
            raise ValueError("Cache token ID out of range")
        if any(f not in (0, 1) for f in flags) or sum(flags) != row["green_tokens"]:
            raise ValueError("Cache raw green flags differ from saved source")


def environment():
    result = {m: importlib.util.find_spec(m) is not None for m in ("torch", "transformers", "scipy", "pyarrow")}
    if result["torch"]:
        import torch
        result.update(torch_version=torch.__version__, cuda_available=torch.cuda.is_available())
    else:
        result["cuda_available"] = False
    return result


def report_markdown(summary):
    lines = ["# 黑盒水印检测", "", f"对照：{summary['reference']}。分数为 -log10(p)，越大越像带水印。",
        "", "各预算是过滤前回答 token 数。逐回答和每个预算组内跨回答去重；语料级另作全局去重。",
        "阈值由当前评估组的经验 ROC 选择，属于描述性指标，不是独立校准后的泛化性能。",
        "clean 行的 AUROC/TPR 仅为对照分布诊断，不代表水印检出率。", "",
        "| 实验 | 模式 | 检测单位 | 有效组数 | AUROC | TPR≤5% (实际FPR) | TPR≤10% (实际FPR) | p中位数 | p平均数 | 平均有效N |",
        "|---|---|---|---:|---:|---|---|---:|---:|---:|"]
    def fmt(value):
        return "N/A" if value is None else f"{value:.6g}" if isinstance(value, (int, float)) else str(value)
    for row in summary["rows"]:
        metric, stats = row["roc"], row["summary"]
        rates = metric.get("tpr_at_fpr", {})
        rate = lambda key: f"{rates[key]['tpr']:.2%} ({rates[key]['fpr']:.2%})" if key in rates else "N/A"
        lines.append(f"| {row['experiment']} | {row['mode']} | {row['unit']} | {stats['valid_units']} | "
                     f"{fmt(metric.get('auroc'))} | {rate('5%')} | {rate('10%')} | "
                     f"{fmt(stats['median_p_value'])} | {fmt(stats['mean_p_value'])} | {fmt(stats.get('mean_effective_n'))} |")
    lines += ["", "## 全语料单次检验", "", "| 实验 | 模式 | 原始tokens | 有效N | 绿名单比例 | p | log10(p) |",
              "|---|---|---:|---:|---:|---:|---:|"]
    for row in summary["corpus"]:
        s = row["score"]
        lines.append(f"| {row['experiment']} | {row['mode']} | {s.get('raw_tokens',0)} | {s['n']} | {fmt(s['green_fraction'])} | {fmt(s['p_value'])} | {fmt(s['log10_p_value'])} |")
    lines += ["", "p均值/中位数是组间描述统计，不是合并检验。零有效token组记N/A并剔除ROC。",
              "窗口筛选来自预先指定教师语料；复用已有Dolly输出，未复现论文的主动探测问题生成。",
              "不同模型/攻击的输出长度和有效token数可能不同；完整JSON保留组数、丢弃尾部和过滤计数。",
              "同一checkpoint的多组回答不是独立训练模型；低p须与clean误报及效应大小一起解释。", ""]
    return "\n".join(lines)


def parse_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest", type=Path, default=ROOT / "new_detect/experiments.json")
    p.add_argument("--output-dir", type=Path, default=None)
    p.add_argument("--cache-dir", type=Path, default=ROOT / "new_detect/cache")
    p.add_argument("--tokenizer", type=Path, default=Path("/shared/public_models/Qwen2.5-14B-Instruct"))
    p.add_argument("--generation-tokenizer", type=Path, help="Explicit common generation tokenizer override; must match original templates")
    p.add_argument("--device", default="cuda")
    p.add_argument("--budgets", type=int, nargs="+", default=[1000, 2000, 3000])
    p.add_argument("--experiments", nargs="+")
    p.add_argument("--reference", help="Manifest clean source; default base, optional clean_gad or clean_warmup")
    p.add_argument("--filter-mode", choices=["none", "teacher", "both"], default="both")
    p.add_argument("--teacher-filter", type=Path)
    p.add_argument("--teacher-field", default="teacher_response")
    p.add_argument("--filter-min-count", type=int, default=1)
    p.add_argument("--preflight", action="store_true", help="Validate sources and environment without tokenizers, weights or GPU scoring")
    p.add_argument("--from-cache-only", action="store_true", help="CPU-only statistics from previously verified CUDA token caches")
    args = p.parse_args(argv)
    if any(x <= 0 for x in args.budgets) or len(args.budgets) != len(set(args.budgets)) or args.filter_min_count <= 0:
        p.error("Budgets must be unique positive integers; min-count must be positive")
    return args


def main(argv=None):
    args = parse_args(argv)
    specs, datasets, sources, reference, teacher = inventory(args)
    out = args.output_dir or ROOT / "new_detect/runs" / datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    # New run directory avoids overwriting old scientific results or any input.
    if out.exists() and any(out.iterdir()):
        raise FileExistsError(f"Output directory must be empty: {out}")
    out.mkdir(parents=True, exist_ok=True)
    preflight = dict(version=VERSION, reference=reference, sources=sources, teacher_filter=teacher,
                     environment=environment(), teacher_tokenizer_exists=args.tokenizer.is_dir(),
                     total_sources=len(specs), total_answers=sum(len(x) for x in datasets.values()))
    write_json(out / "preflight.json", preflight)
    print(f"Validated {len(specs)} sources / {preflight['total_answers']} answers. Reference: {reference}")
    if args.preflight:
        print(json.dumps(preflight["environment"], ensure_ascii=True))
        print(f"Preflight saved: {out / 'preflight.json'}")
        return
    scorer = None
    prepared = {}
    detector_signature = None
    if not args.from_cache_only:
        scorer = CudaTokenizerScorer(args)
        detector_signature = tokenizer_signature(args.tokenizer)["files_sha256"]
    for spec in specs:
        name, source, rows = spec["name"], sources[spec["name"]], datasets[spec["name"]]
        cache_path = args.cache_dir / f"{name}.tokens.json"
        signature = None
        if scorer:
            generation_signatures = {generation_path(row, args.generation_tokenizer): None for row in rows if isinstance(row["prompt"], list)}
            for path in generation_signatures:
                generation_signatures[path] = tokenizer_signature(Path(path))["files_sha256"]
            signature = dict(detector=detector_signature, generation=generation_signatures,
                             torch_version=scorer.torch.__version__)
        payload = None
        if cache_path.is_file():
            try:
                candidate = json.loads(cache_path.read_text(encoding="utf-8"))
                validate_cache(candidate, source, rows)
                if scorer and candidate["tokenizer_signatures"] != signature:
                    raise ValueError("Tokenizer/runtime signature mismatch")
                payload = candidate
                print(f"Cache: {name}", flush=True)
            except (ValueError, KeyError, TypeError) as exc:
                if args.from_cache_only:
                    raise ValueError(f"Invalid portable cache {cache_path}: {exc}") from exc
                print(f"Rebuild cache {name}: {exc}", flush=True)
        if payload is None:
            if args.from_cache_only:
                raise FileNotFoundError(f"Missing validated CUDA cache: {cache_path}; run once on server")
            print(f"Tokenize/score {name} ({len(rows)} answers)", flush=True)
            payload = dict(version=VERSION, source_sha256=source["sha256"], gamma=GAMMA,
                hash_key=KEY, rng="cuda", vocab_size=len(scorer.tokenizer),
                tokenizer_signatures=signature, records=scorer.prepare(rows))
            validate_cache(payload, source, rows)
            write_json(cache_path, payload)
        prepared[name] = payload
    vocabs = {x["vocab_size"] for x in prepared.values()}
    fingerprints = {json.dumps(x["tokenizer_signatures"]["detector"], sort_keys=True) for x in prepared.values()}
    if len(vocabs) != 1 or len(fingerprints) != 1:
        raise ValueError("All sources must use the same teacher tokenizer/vocabulary")
    vocab = next(iter(vocabs))
    q = max(1, int(vocab * GAMMA)) / vocab
    allowed, filter_info = None, None
    if teacher:
        filter_cache = args.cache_dir / "teacher_filter.json"
        filter_signature = dict(source_sha256=teacher["sha256"], field=teacher["field"],
                                min_count=teacher["min_count"], detector=json.loads(next(iter(fingerprints))),
                                evaluation_ids_sha256=hashlib.sha256(json.dumps(sorted(r["id"] for r in datasets[reference])).encode()).hexdigest())
        if args.from_cache_only:
            filter_info = json.loads(filter_cache.read_text(encoding="utf-8"))
            if filter_info.get("signature") != filter_signature or filter_info.get("version") != VERSION:
                raise ValueError("Teacher filter cache does not match source/tokenizer/protocol")
        else:
            filter_info = dict(version=VERSION, signature=filter_signature,
                **teacher_contexts(teacher, scorer.tokenizer, {r["id"] for r in datasets[reference]}))
            write_json(filter_cache, filter_info)
        allowed = set(filter_info["context_ids"])
        if not allowed or any(type(t) is not int or not 0 <= t < vocab for t in allowed):
            raise ValueError("Teacher filter cache has empty/out-of-range context IDs")
    modes = ["dedup", "teacher_filtered"] if args.filter_mode == "both" else ["dedup" if args.filter_mode == "none" else "teacher_filtered"]
    results = {}
    for name, payload in prepared.items():
        print(f"Statistics: {name}", flush=True)
        results[name] = {}
        for mode in modes:
            result = score_records(payload["records"], q, tuple(args.budgets), allowed if mode == "teacher_filtered" else None)
            results[name][mode] = result
            write_json(out / f"{name}.{mode}.json", dict(version=VERSION, source=sources[name],
                null_probability=q, nominal_gamma=GAMMA, mode=mode, result=result))
    summary = dict(version=VERSION, created_at=datetime.now(timezone.utc).isoformat(), reference=reference,
                   sources=sources, teacher_filter=teacher, filter_info=filter_info, null_probability=q,
                   budgets=args.budgets, portable_cache_only=args.from_cache_only,
                   tokenizer_signatures={name: p["tokenizer_signatures"] for name, p in prepared.items()}, rows=[], corpus=[])
    for name in results:
        for mode in modes:
            result, control = results[name][mode], results[reference][mode]
            summary["corpus"].append(dict(experiment=name, mode=mode, score=result["corpus"]))
            for unit in ["per_answer"] + [str(x) for x in args.budgets]:
                if unit == "per_answer":
                    positive, negative, stats = result[unit], control[unit], result["per_answer_summary"]
                else:
                    positive, negative = result["budgets"][unit]["groups"], control["budgets"][unit]["groups"]
                    stats = result["budgets"][unit]["summary"]
                metric = dict(status="reference_only") if name == reference else roc(negative, positive)
                summary["rows"].append(dict(experiment=name, role=sources[name]["role"], mode=mode,
                                            unit=unit, summary=stats, roc=metric))
    write_json(out / "summary.json", summary)
    (out / "summary.md").write_text(report_markdown(summary), encoding="utf-8")
    print(f"Completed: {out / 'summary.md'}")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, RuntimeError, FileNotFoundError, FileExistsError, ImportError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
