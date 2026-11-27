#!/usr/bin/env python3
"""Step 7: Collect all small JSON audit reports into git-friendly summary files.

Exports:
  1. Single-pool summaries (from <work-dir>/suspects/*/score.json):
       - <out-dir>/summary.json
       - <out-dir>/summary.md
  2. Multi-window TPR@FPR summaries (auto-detects both suspects_mw and suspects_mw100):
       - <out-dir>/mw_summary.json & mw_summary.md        (from suspects_mw/)
       - <out-dir>/mw100_summary.json & mw100_summary.md  (from suspects_mw100/)
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from wm_basin.core import read_json, write_json


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Summarize WM-Basin suspect scores into git-friendly JSON & Markdown")
    p.add_argument("--work-dir", type=Path, default=Path("wm_basin_work"))
    p.add_argument("--out-dir", type=Path, default=Path("wm_basin/results"))
    return p.parse_args()


def empirical_auroc(neg_scores: list[float], pos_scores: list[float]) -> float | None:
    """Exact Wilcoxon-Mann-Whitney AUROC (ties get 0.5) using higher=more watermarked."""
    if not neg_scores or not pos_scores:
        return None
    wins = 0.0
    for ps in pos_scores:
        for ns in neg_scores:
            if ps > ns:
                wins += 1.0
            elif ps == ns:
                wins += 0.5
    return wins / (len(pos_scores) * len(neg_scores))


def export_single_pool(args: argparse.Namespace, meta_header: dict) -> None:
    sus_root = args.work_dir / "suspects"
    score_files = sorted(sus_root.glob("*/score.json")) if sus_root.exists() else []
    if not score_files:
        return

    records = []
    for sf in score_files:
        sc = read_json(sf)
        grad_meta_path = sf.parent / "grad.meta.json"
        gm = read_json(grad_meta_path) if grad_meta_path.exists() else {}
        wb = sc["wm_basin"]
        raw = sc["raw_no_pca"]
        records.append(
            {
                "suspect_name": sc["suspect_name"],
                "suspect_model": sc.get("suspect_model"),
                "num_keys": wb["num_keys"],
                "pca_q": sc.get("pca_q"),
                "used_samples": gm.get("num_used_samples"),
                "scored_tokens": gm.get("total_scored_tokens"),
                "rank": wb["rank"],
                "p_rank": wb["p_rank"],
                "cosine": wb["claimed_score"],
                "z_score": wb["z_score"],
                "raw_rank": raw["rank"],
                "raw_p_rank": raw["p_rank"],
                "flagged_at_5pct": sc["flagged_at_5pct"],
                "flagged_at_1pct": sc["flagged_at_1pct"],
                "top5_keys": sc.get("top5_keys", []),
            }
        )

    payload = {**meta_header, "suspects": records}
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_json(args.out_dir / "summary.json", payload)

    lines = [
        "# WM-Basin Single-Pool Audit Summary",
        "",
        f"- **Generated (UTC)**: `{payload['generated_at_utc']}`",
        f"- **Probe**: `{payload['probe']['model']}` (LoRA `r={payload['probe']['lora_r']}`, epochs=`{payload['probe']['epochs']}`)",
        f"- **Projector**: `proj_dim={payload['projector']['proj_dim']}`, `weighting={payload['projector']['weighting']}`",
        f"- **Clean PCA**: `q={payload['pca']['q']}`, `{payload['pca']['num_clean_cells']}` cells (`{payload['pca']['num_base_models']}` base models)",
        "",
        "| Suspect | Used / Tokens | Raw Rank | **WM-Basin Rank** | **`p_rank`** | **`S(k*)`** | **`z-score`** | **@5% Verdict** |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for r in records:
        verdict = "**DISTILLED**" if r["flagged_at_5pct"] else "No evidence"
        ut = f"{r['used_samples']} / {r['scored_tokens']:,}" if r["used_samples"] and r["scored_tokens"] else "-"
        lines.append(
            f"| `{r['suspect_name']}` | {ut} | {r['raw_rank']}/{r['num_keys']} | "
            f"**{r['rank']}/{r['num_keys']}** | `{r['p_rank']:.4f}` | `{r['cosine']:+.5f}` | "
            f"`{r['z_score']:+.2f}` | {verdict} |"
        )
    lines.append("")
    md_path = args.out_dir / "summary.md"
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"[summary] Exported {len(records)} single-pool suspects -> {md_path}")


def export_multi_window(
    args: argparse.Namespace,
    meta_header: dict,
    subdir: str = "suspects_mw",
    prefix: str = "mw",
) -> None:
    mw_root = args.work_dir / subdir
    mw_files = sorted(mw_root.glob("*/mw_score.json")) if mw_root.exists() else []
    if not mw_files:
        return

    raw_reports = [read_json(f) for f in mw_files]

    # Collect negative control window scores (-p_rank so higher = more watermarked) for empirical AUROC
    neg_window_scores: list[float] = []
    for rep in raw_reports:
        if rep.get("role") == "negative":
            neg_window_scores.extend([-float(w["p_rank"]) for w in rep.get("windows", [])])

    records = []
    for rep in raw_reports:
        pos_scores = [-float(w["p_rank"]) for w in rep.get("windows", [])]
        auroc = empirical_auroc(neg_window_scores, pos_scores) if rep.get("role") != "negative" else None
        rep_copy = dict(rep)
        rep_copy["auroc_vs_negatives"] = auroc
        records.append(rep_copy)

    payload = {**meta_header, "suspects_subdir": subdir, "multi_window_suspects": records}
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_json(args.out_dir / f"{prefix}_summary.json", payload)

    lines = [
        f"# WM-Basin Multi-Window TPR@FPR Summary (`{subdir}`)",
        "",
        f"- **Generated (UTC)**: `{payload['generated_at_utc']}`",
        f"- **Probe**: `{payload['probe']['model']}` (LoRA `r={payload['probe']['lora_r']}`, epochs=`{payload['probe']['epochs']}`)",
        f"- **Projector**: `proj_dim={payload['projector']['proj_dim']}`, `weighting={payload['projector']['weighting']}`",
        f"- **Clean PCA**: `q={payload['pca']['q']}`, `{payload['pca']['num_clean_cells']}` cells (`{payload['pca']['num_base_models']}` base models)",
        "",
        "| Suspect | **`TPR @ 10% FPR`** | **`TPR @ 5% FPR`** | **`TPR @ 1% FPR`** | **AUROC** | **Pooled `Rank`** | **Pooled `p_rank`** | **Pooled `z`** | **Pooled `S(k*)`** | Windows (Tokens) |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in records:
        K = r["num_keys"]
        G = r["num_windows"]
        tpr10 = f"**{r['tpr_at_10pct']*100:.1f}%**" if r.get("tpr_at_10pct") is not None else "—"
        tpr5 = f"**{r['tpr_at_5pct']*100:.1f}%**"
        tpr1 = f"**{r['tpr_at_1pct']*100:.1f}%**" if r["tpr_at_1pct"] is not None else "—"
        auroc_str = f"`{r['auroc_vs_negatives']:.3f}`" if r["auroc_vs_negatives"] is not None else "*(neg)*"
        pooled = r["pooled"]
        lines.append(
            f"| `{r['suspect_name']}` | {tpr10} | {tpr5} | {tpr1} | {auroc_str} | "
            f"`{pooled['rank']}/{K}` | `{pooled['p_rank']:.3f}` | `{pooled['z_score']:+.2f}` | "
            f"`{pooled['claimed_score']:+.4f}` | {G} ({r['total_scored_tokens']:,}) |"
        )
    lines.append("")
    md_path = args.out_dir / f"{prefix}_summary.md"
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"[summary] Exported {len(records)} multi-window suspects ({subdir}) -> {md_path}")


def main() -> None:
    args = parse_args()
    probe_meta = read_json(args.work_dir / "probe" / "probe_meta.json") if (args.work_dir / "probe" / "probe_meta.json").exists() else {}
    pca_summary = read_json(args.work_dir / "pca" / "pca_summary.json") if (args.work_dir / "pca" / "pca_summary.json").exists() else {}
    proj_meta = read_json(args.work_dir / "grads" / "projector_meta.json") if (args.work_dir / "grads" / "projector_meta.json").exists() else {}

    meta_header = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "probe": {
            "model": probe_meta.get("probe_model"),
            "lora_r": probe_meta.get("lora_r"),
            "epochs": probe_meta.get("epochs"),
        },
        "projector": {
            "proj_dim": proj_meta.get("proj_dim"),
            "proj_seed": proj_meta.get("proj_seed"),
            "weighting": proj_meta.get("weighting"),
        },
        "pca": {
            "q": pca_summary.get("q"),
            "num_clean_cells": pca_summary.get("num_clean_cells"),
            "num_base_models": pca_summary.get("num_base_models"),
            "calibration_sweep": pca_summary.get("calibration_sweep", []),
        },
    }

    export_single_pool(args, meta_header)
    export_multi_window(args, meta_header, subdir="suspects_mw", prefix="mw")
    export_multi_window(args, meta_header, subdir="suspects_mw100", prefix="mw100")


if __name__ == "__main__":
    main()
