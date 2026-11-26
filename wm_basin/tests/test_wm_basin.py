"""Unit tests for WM-Basin core math, incremental keys, PCA removal, and CLI scoring."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from wm_basin.core import (
    BlockRademacherProjector,
    DEFAULT_TRUE_KEY,
    TaskSubspace,
    build_messages,
    cosine_similarities,
    fit_task_subspace,
    generate_keys,
    rank_test,
    write_json,
)


class TestWMBasinCore(unittest.TestCase):
    def test_generate_keys_incremental_preserves_prefix(self):
        k40 = generate_keys(total_keys=40, true_key=DEFAULT_TRUE_KEY, seed=42)
        self.assertEqual(len(k40), 40)
        self.assertEqual(k40[0], DEFAULT_TRUE_KEY)
        self.assertEqual(len(set(k40)), 40)

        k100 = generate_keys(total_keys=100, true_key=DEFAULT_TRUE_KEY, seed=42, existing_keys=k40)
        self.assertEqual(len(k100), 100)
        self.assertEqual(k100[:40], k40)
        self.assertEqual(len(set(k100)), 100)

    def test_build_messages_matches_dolly_format(self):
        msgs = build_messages("Summarize this.", "Some context.")
        self.assertEqual(msgs[0]["role"], "system")
        self.assertEqual(msgs[0]["content"], "You are a helpful assistant.")
        self.assertIn("### Instruction:\nSummarize this.", msgs[1]["content"])
        self.assertIn("### Context:\nSome context.", msgs[1]["content"])
        self.assertTrue(msgs[1]["content"].endswith("### Response:\n"))

        msgs_no_ctx = build_messages("Say hi.")
        self.assertNotIn("### Context:", msgs_no_ctx[1]["content"])

    def test_block_rademacher_linearity(self):
        rng = np.random.default_rng(7)
        vecs = [rng.normal(size=5000).astype(np.float32) for _ in range(5)]
        proj = BlockRademacherProjector(proj_dim=256, seed=123, block_size=1024)

        mean_vec = np.mean(vecs, axis=0)
        p_of_mean = proj.project_numpy(mean_vec)
        mean_of_p = np.mean([proj.project_numpy(v) for v in vecs], axis=0)
        np.testing.assert_allclose(p_of_mean, mean_of_p, rtol=1e-4, atol=1e-4)

    def test_pca_removal_recovers_faint_watermark_signal(self):
        """Synthetic geometry check: strong shared task subspace masks faint watermark key,
        and All-but-the-Top PCA projection restores rank=1 detection."""
        rng = np.random.default_rng(0)
        d = 512
        q_true = 5
        # Shared task basis (large variance)
        task_basis, _ = np.linalg.qr(rng.normal(size=(d, q_true)))
        task_mean = rng.normal(size=d) * 5.0

        # 30 clean cells living mostly in the task subspace + small isotropic noise (L2 norm ~ 0.05)
        noise_scale = 0.05 / np.sqrt(d)
        clean_cells = np.array([
            task_mean + task_basis @ (rng.normal(size=q_true) * 10.0) + rng.normal(size=d) * noise_scale
            for _ in range(30)
        ])

        # 40 reference keys: strong task component + faint key-specific orthogonal direction
        key_dirs = rng.normal(size=(40, d))
        key_dirs -= (key_dirs @ task_basis) @ task_basis.T
        key_dirs /= np.linalg.norm(key_dirs, axis=1, keepdims=True)
        bank = np.array([
            task_mean + task_basis @ (rng.normal(size=q_true) * 10.0) + 0.3 * key_dirs[k]
            for k in range(40)
        ])

        # Distilled suspect: shares task subspace + faint component along key 0
        suspect = (
            task_mean
            + task_basis @ (rng.normal(size=q_true) * 10.0)
            + 0.25 * key_dirs[0]
            + rng.normal(size=d) * (0.02 / np.sqrt(d))
        )

        sub = fit_task_subspace(clean_cells, q=q_true)
        # Residual must be orthogonal to fitted task components
        sus_res = sub.project_out(suspect)
        self.assertLess(float(np.max(np.abs(sub.components @ sus_res))), 1e-10)

        bank_res = sub.project_out(bank)
        scores = cosine_similarities(sus_res, bank_res)
        res = rank_test(scores, claimed_idx=0)
        self.assertEqual(res["rank"], 1)
        self.assertAlmostEqual(res["p_rank"], 1.0 / 40.0)

    def test_rank_test_ties_count_against_rejection(self):
        res = rank_test([0.5, 0.5, 0.1, 0.2], claimed_idx=0)
        self.assertEqual(res["rank"], 2)
        self.assertAlmostEqual(res["p_rank"], 0.5)

    def test_end_to_end_pca_and_only_score_cli(self):
        """Smoke-test 05_fit_pca.py and 06_gen_and_score_suspect.py --only-score on synthetic .npy files."""
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            rng = np.random.default_rng(42)
            d = 128
            keys = generate_keys(total_keys=40, true_key=DEFAULT_TRUE_KEY, seed=42)
            write_json(
                work / "keys.json",
                {
                    "scheme": "kgw_simple_1",
                    "gamma": 0.5,
                    "delta": 3.0,
                    "true_key": DEFAULT_TRUE_KEY,
                    "true_key_idx": 0,
                    "seed": 42,
                    "num_keys": 40,
                    "keys": keys,
                },
            )

            task_dir = rng.normal(size=d)
            task_dir /= np.linalg.norm(task_dir)
            wm_dirs = rng.normal(size=(40, d))
            wm_dirs /= np.linalg.norm(wm_dirs, axis=1, keepdims=True)

            # Save 12 clean cells (4 models x 3 temps)
            clean_dir = work / "grads" / "clean_pool"
            clean_dir.mkdir(parents=True)
            for m in range(4):
                for t in (0.7, 1.0, 1.3):
                    vec = 10.0 * task_dir + rng.normal(size=d) * 0.1
                    np.save(clean_dir / f"model{m}__T{t:.1f}.npy", vec.astype(np.float32))

            # Save 40 bank keys
            bank_dir = work / "grads" / "bank"
            bank_dir.mkdir(parents=True)
            for idx, hk in enumerate(keys):
                vec = 10.0 * task_dir + 0.5 * wm_dirs[idx]
                np.save(bank_dir / f"key_{idx:04d}_{hk}.npy", vec.astype(np.float32))

            # Save synthetic distilled suspect aligned with key 0
            sus_dir = work / "suspects" / "test_student"
            sus_dir.mkdir(parents=True)
            sus_vec = 10.0 * task_dir + 0.4 * wm_dirs[0] + rng.normal(size=d) * 0.02
            np.save(sus_dir / "grad.npy", sus_vec.astype(np.float32))

            # Run 05_fit_pca.py
            r1 = subprocess.run(
                [sys.executable, str(ROOT / "wm_basin" / "05_fit_pca.py"), "--work-dir", str(work), "--q", "3", "--sweep-q", "0", "1", "3"],
                capture_output=True,
                text=True,
                check=True,
            )
            self.assertTrue((work / "pca" / "task_subspace.npz").exists(), r1.stdout + r1.stderr)

            # Run 06_gen_and_score_suspect.py --only-score
            r2 = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "wm_basin" / "06_gen_and_score_suspect.py"),
                    "--work-dir",
                    str(work),
                    "--suspect-name",
                    "test_student",
                    "--only-score",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            score = json.loads((sus_dir / "score.json").read_text(encoding="utf-8"))
            self.assertEqual(score["wm_basin"]["rank"], 1, r2.stdout + r2.stderr)
            self.assertTrue(score["flagged_at_5pct"])

    def test_multi_window_100keys_tpr_and_summary(self):
        """End-to-end test of 100-key bank + 20 disjoint windows -> TPR@5%, TPR@1%, AUROC."""
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            rng = np.random.default_rng(123)
            d = 256
            keys = generate_keys(total_keys=100, true_key=DEFAULT_TRUE_KEY, seed=42)
            write_json(
                work / "keys.json",
                {
                    "scheme": "kgw_simple_1",
                    "gamma": 0.5,
                    "delta": 3.0,
                    "true_key": DEFAULT_TRUE_KEY,
                    "true_key_idx": 0,
                    "seed": 42,
                    "num_keys": 100,
                    "keys": keys,
                },
            )

            task_dir = rng.normal(size=d)
            task_dir /= np.linalg.norm(task_dir)
            wm_dirs = rng.normal(size=(100, d))
            wm_dirs -= np.outer(wm_dirs @ task_dir, task_dir)
            wm_dirs /= np.linalg.norm(wm_dirs, axis=1, keepdims=True)

            clean_dir = work / "grads" / "clean_pool"
            clean_dir.mkdir(parents=True)
            for m in range(6):
                for t in (0.7, 1.0, 1.3):
                    vec = 10.0 * task_dir + rng.normal(size=d) * (0.05 / np.sqrt(d))
                    np.save(clean_dir / f"model{m}__T{t:.1f}.npy", vec.astype(np.float32))

            bank_dir = work / "grads" / "bank"
            bank_dir.mkdir(parents=True)
            for idx, hk in enumerate(keys):
                vec = 10.0 * task_dir + 0.5 * wm_dirs[idx]
                np.save(bank_dir / f"key_{idx:04d}_{hk}.npy", vec.astype(np.float32))

            # Dummy window files so 09_audit_multi_window.py discovers G=20 windows
            win_dir = work / "pools" / "audit_windows"
            win_dir.mkdir(parents=True)
            for w in range(20):
                (win_dir / f"window_{w:02d}.jsonl").write_text("{}\n", encoding="utf-8")

            # Fit PCA
            subprocess.run(
                [sys.executable, str(ROOT / "wm_basin" / "05_fit_pca.py"), "--work-dir", str(work), "--q", "2", "--sweep-q", "2"],
                check=True,
                capture_output=True,
            )

            # Create 20 window gradients for a clean control & a watermarked student
            neg_dir = work / "suspects_mw" / "clean_gad_ctrl"
            pos_dir = work / "suspects_mw" / "kgw_gad_pos"
            neg_dir.mkdir(parents=True)
            pos_dir.mkdir(parents=True)
            for w in range(20):
                v_neg = 10.0 * task_dir + rng.normal(size=d) * 0.1
                v_pos = 10.0 * task_dir + 0.35 * wm_dirs[0] + rng.normal(size=d) * 0.02
                np.save(neg_dir / f"grad_win_{w:02d}.npy", v_neg.astype(np.float32))
                np.save(pos_dir / f"grad_win_{w:02d}.npy", v_pos.astype(np.float32))
                write_json(neg_dir / f"grad_win_{w:02d}.meta.json", {"num_used_samples": 100, "total_scored_tokens": 20000})
                write_json(pos_dir / f"grad_win_{w:02d}.meta.json", {"num_used_samples": 100, "total_scored_tokens": 20000})

            for name in ("clean_gad_ctrl", "kgw_gad_pos"):
                subprocess.run(
                    [sys.executable, str(ROOT / "wm_basin" / "09_audit_multi_window.py"), "--work-dir", str(work), "--suspect-name", name, "--only-score"],
                    check=True,
                    capture_output=True,
                )

            out_res = work / "results"
            subprocess.run(
                [sys.executable, str(ROOT / "wm_basin" / "07_summarize_results.py"), "--work-dir", str(work), "--out-dir", str(out_res)],
                check=True,
                capture_output=True,
            )
            mw_sum = json.loads((out_res / "mw_summary.json").read_text(encoding="utf-8"))
            by_name = {r["suspect_name"]: r for r in mw_sum["multi_window_suspects"]}
            self.assertEqual(by_name["kgw_gad_pos"]["tpr_at_5pct"], 1.0)
            self.assertEqual(by_name["kgw_gad_pos"]["tpr_at_1pct"], 1.0)
            self.assertGreater(by_name["kgw_gad_pos"]["auroc_vs_negatives"], 0.99)


if __name__ == "__main__":
    unittest.main()
