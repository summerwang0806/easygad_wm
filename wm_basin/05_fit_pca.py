#!/usr/bin/env python3
"""Step 5: Fit the clean task subspace (All-but-the-Top PCA) and calibrate FPR.

Paper reference (Section 2.3, App. B.5, App. B.6 / Fig. 6 & Tab. 11):
  - Fits mean & top-q principal components ONLY on clean off-the-shelf model gradients.
  - Evaluates per-key FPR at alpha=5% via 4-fold cross-fitting grouped by base model
    (so no clean model is ever scored by a PCA subspace fit on its own temperatures).
  - Never touches any suspect model.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from wm_basin.core import (
    cosine_similarities,
    fit_task_subspace,
    rank_test,
    read_json,
    write_json,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Fit clean task PCA subspace and run cross-fitted FPR calibration")
    p.add_argument("--work-dir", type=Path, default=Path("wm_basin_work"))
    p.add_argument("--q", type=int, default=20, help="Number of principal task directions to project out (Pilot=15-20)")
    p.add_argument("--sweep-q", nargs="+", type=int, default=[0, 5, 10, 15, 20, 30, 50])
    p.add_argument("--alpha", type=float, default=0.05, help="Nominal FPR threshold for calibration check")
    p.add_argument("--folds", type=int, default=4, help="Cross-fitting folds grouped by base model")
    return p.parse_args()


def load_clean_cells(clean_grad_dir: Path) -> tuple[np.ndarray, list[str], list[str]]:
    files = sorted(clean_grad_dir.glob("*.npy"))
    if len(files) < 2:
        raise RuntimeError(f"Need at least 2 clean cell .npy files in {clean_grad_dir}, found {len(files)}")
    vecs = []
    cell_names = []
    base_models = []
    for f in files:
        vecs.append(np.load(f).astype(np.float64))
        name = f.stem
        cell_names.append(name)
        base = name.split("__T")[0] if "__T" in name else name
        base_models.append(base)
    return np.stack(vecs, axis=0), cell_names, base_models


def load_bank_matrix(work_dir: Path) -> tuple[np.ndarray, list[int]]:
    keys_info = read_json(work_dir / "keys.json")
    bank_dir = work_dir / "grads" / "bank"
    vecs = []
    loaded_keys = []
    for idx, hk in enumerate(keys_info["keys"]):
        fp = bank_dir / f"key_{idx:04d}_{hk}.npy"
        if fp.exists():
            vecs.append(np.load(fp).astype(np.float64))
            loaded_keys.append(int(hk))
    if not vecs:
        return np.zeros((0, 0), dtype=np.float64), []
    return np.stack(vecs, axis=0), loaded_keys


def cross_fitted_calibration(
    clean_mat: np.ndarray,
    base_models: list[str],
    bank_mat: np.ndarray,
    q: int,
    alpha: float,
    num_folds: int,
) -> dict[str, float | int]:
    """4-fold cross-fitting by base model: compute per-key empirical FPR at nominal alpha."""
    unique_models = sorted(set(base_models))
    eff_folds = min(num_folds, len(unique_models))
    if eff_folds < 2:
        return {"skipped": 1, "reason": "need >= 2 distinct base models"}

    model_to_fold = {m: i % eff_folds for i, m in enumerate(unique_models)}
    K = bank_mat.shape[0]
    N = clean_mat.shape[0]
    # hits[k, c] = True if key k fires on clean cell c at p_rank <= alpha
    hits = np.zeros((K, N), dtype=bool)

    for fold in range(eff_folds):
        val_idx = [i for i, m in enumerate(base_models) if model_to_fold[m] == fold]
        fit_idx = [i for i, m in enumerate(base_models) if model_to_fold[m] != fold]
        sub = fit_task_subspace(clean_mat[fit_idx], q=q)
        bank_res = sub.project_out(bank_mat)
        for ci in val_idx:
            cell_res = sub.project_out(clean_mat[ci])
            scores = cosine_similarities(cell_res, bank_res)
            for k_idx in range(K):
                res = rank_test(scores, claimed_idx=k_idx)
                hits[k_idx, ci] = res["p_rank"] <= alpha

    per_key_fpr = hits.mean(axis=1)  # fraction of clean cells firing for each key
    return {
        "q": q,
        "alpha": alpha,
        "num_keys": K,
        "num_clean_cells": N,
        "num_base_models": len(unique_models),
        "mean_fpr": float(per_key_fpr.mean()),
        "median_fpr": float(np.median(per_key_fpr)),
        "p90_fpr": float(np.percentile(per_key_fpr, 90)),
        "p95_fpr": float(np.percentile(per_key_fpr, 95)),
        "worst_fpr": float(per_key_fpr.max()),
        "claimed_key0_fpr": float(per_key_fpr[0]),
    }


def main() -> None:
    args = parse_args()
    clean_mat, cell_names, base_models = load_clean_cells(args.work_dir / "grads" / "clean_pool")
    bank_mat, loaded_keys = load_bank_matrix(args.work_dir)
    n_cells, dim = clean_mat.shape
    print(f"[pca] Loaded {n_cells} clean cells ({len(set(base_models))} base models), dim={dim}.")

    # Fit and save the final subspace on all clean cells (for scoring suspects)
    eff_q = min(args.q, n_cells - 1)
    if eff_q != args.q:
        print(f"[pca] Clamped q from {args.q} to {eff_q} (n_cells - 1).")
    subspace = fit_task_subspace(clean_mat, q=eff_q)
    pca_dir = args.work_dir / "pca"
    subspace_path = pca_dir / "task_subspace.npz"
    subspace.save(subspace_path)
    print(f"[pca] Saved task subspace (q={subspace.q}) to {subspace_path}")

    # Cross-fitted per-key FPR sweep over q (if bank gradients exist)
    calibration_results: list[dict] = []
    if bank_mat.shape[0] >= 2:
        print(f"[pca] Running {args.folds}-fold cross-fitted FPR calibration on {bank_mat.shape[0]} keys @ alpha={args.alpha}...")
        for q_cand in args.sweep_q:
            if q_cand >= n_cells - 1:
                continue
            stats = cross_fitted_calibration(
                clean_mat=clean_mat,
                base_models=base_models,
                bank_mat=bank_mat,
                q=q_cand,
                alpha=args.alpha,
                num_folds=args.folds,
            )
            calibration_results.append(stats)
            if "skipped" not in stats:
                print(
                    f"  q={q_cand:3d} | median_FPR={stats['median_fpr']*100:5.1f}% | "
                    f"p90={stats['p90_fpr']*100:5.1f}% | p95={stats['p95_fpr']*100:5.1f}% | "
                    f"worst={stats['worst_fpr']*100:5.1f}% | k*_FPR={stats['claimed_key0_fpr']*100:5.1f}%"
                )
    else:
        print("[pca] Bank gradients not found yet; skipping cross-fitted FPR calibration.")

    write_json(
        pca_dir / "pca_summary.json",
        {
            "subspace_path": str(subspace_path),
            "q": subspace.q,
            "dim": dim,
            "num_clean_cells": n_cells,
            "num_base_models": len(set(base_models)),
            "clean_cells": cell_names,
            "num_bank_keys_calibrated": len(loaded_keys),
            "calibration_sweep": calibration_results,
        },
    )


if __name__ == "__main__":
    main()
