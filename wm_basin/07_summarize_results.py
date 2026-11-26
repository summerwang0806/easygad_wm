#!/usr/bin/env python3
"""Step 7: Collect all small JSON audit reports into git-friendly summary files.

Reads:
  - <work-dir>/suspects/*/score.json (+ grad.meta.json)
  - <work-dir>/pca/pca_summary.json
  - <work-dir>/probe/probe_meta.json

Writes (lightweight, safe to commit & git push):
  - <out-dir>/summary.json
  - <out-dir>/summary.md
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


def main() -> None:
    args = parse_args()
    sus_root = args.work_dir / "suspects"
    score_files = sorted(sus_root.glob("*/score.json"))
    if not score_files:
        raise FileNotFoundError(f"No score.json files found under {sus_root}")

    probe_meta = read_json(args.work_dir / "probe" / "probe_meta.json") if (args.work_dir / "probe" / "probe_meta.json").exists() else {}
    pca_summary = read_json(args.work_dir / "pca" / "pca_summary.json") if (args.work_dir / "pca" / "pca_summary.json").exists() else {}
    proj_meta = read_json(args.work_dir / "grads" / "projector_meta.json") if (args.work_dir / "grads" / "projector_meta.json").exists() else {}

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

    payload = {
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
        "suspects": records,
    }

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_json(args.out_dir / "summary.json", payload)

    # Render clean Markdown table
    lines = [
        "# WM-Basin Audit Summary",
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
    print(f"[summary] Exported {len(records)} suspects -> {args.out_dir / 'summary.json'} and {md_path}")


if __name__ == "__main__":
    main()
