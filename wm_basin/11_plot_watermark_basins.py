#!/usr/bin/env python3
"""Step 11: Reproduce Figure 3 (Watermark Basin Geometry) for all models.

Implements Section 2.2 (Eq. 1) of Chang et al. (arXiv:2610.37266):
  1. For each watermark strength group (delta=6 and delta=3), constructs the
     exact orthonormal parameter-space axes from:
       - theta_base : /app/public_models/Qwen2.5-0.5B
       - theta_ctrl : clean_gad_control
       - theta_ref  : kgw_delta6_gad (or kgw_delta3_gad)
     via Eq. (1):
       Delta_task = theta_ctrl - theta_base
       Delta_total = theta_ref - theta_base
       Delta_wm = Delta_total - (<Delta_total, Delta_task> / ||Delta_task||^2) * Delta_task
       u_wm = Delta_wm / ||Delta_wm||,   u_task = Delta_task / ||Delta_task||

  2. For every model theta_m (all 14 models), scans the 2D plane and 1D slices:
       theta_m(t_wm, t_task) = theta_m + t_wm * u_wm + t_task * u_task
     evaluating the open-weight KGW radioactivity significance (-log10 p)
     (Sander et al., 2024; teacher-forced greedy next-token predictions on
     KGW-watermarked teacher traces under k*=15485863, with unique-bigram
     deduplication so clean models stay strictly at -log10 p ~ 0).

  3. Generates publication-ready figures in <out-dir> (default: wm_basin/results/basin_plots/):
       - Per-model Figure 3 (3-panel: 3D landscape, 2D contour, 1D slices):
           basin_<model>.png
       - Overview 2D contour + projected model trajectories + weight decomposition:
           overview_basin_delta6.png, overview_basin_delta3.png
       - Side-by-side 2D contour gallery on a unified colorbar:
           gallery_delta6.png, gallery_delta3.png
       - Exact numerical geometry report:
           basin_geometry_summary.json & basin_geometry_summary.md
"""

from __future__ import annotations

import argparse
import gc
import math
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from wm_basin.core import (
    DEFAULT_GAMMA,
    DEFAULT_TRUE_KEY,
    read_jsonl,
    render_prompt_with_fallback,
    write_json,
)

# Default model registry matching our 14 evaluated checkpoints
DEFAULT_MODELS: dict[str, dict[str, str]] = {
    "base_qwen25_05b": {
        "path": "/app/public_models/Qwen2.5-0.5B",
        "group": "control",
        "label": "Base 0.5B",
    },
    "clean_gad_control": {
        "path": "/app/wwx/EasyGAD/checkpoints/gad_05b_cleanwarmup_cleangad_control/gad/global_step_1813/actor/huggingface",
        "group": "control",
        "label": "Clean-GAD",
    },
    "kgw_delta3_warmup": {
        "path": "/app/wwx/EasyGAD/checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_new/warmup/global_step_1813/actor/huggingface",
        "group": "delta3",
        "label": "KGW (δ=3) Warmup",
    },
    "kgw_delta3_gad": {
        "path": "/app/wwx/EasyGAD/checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_new/gad/global_step_1813/actor/huggingface",
        "group": "delta3",
        "label": "KGW (δ=3) GAD",
    },
    "up_dipper_delta3_warmup": {
        "path": "/app/wwx/EasyGAD/checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_new1_dipper2stage/warmup/global_step_1813/actor/huggingface",
        "group": "delta3",
        "label": "UP-DIPPER (δ=3) Warmup",
    },
    "up_dipper_delta3_gad": {
        "path": "/app/wwx/EasyGAD/checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_new1_dipper2stage/gad/global_step_1813/actor/huggingface",
        "group": "delta3",
        "label": "UP-DIPPER (δ=3) GAD",
    },
    "tp_delta3_warmup": {
        "path": "/app/wwx/EasyGAD/checkpoints/tp_warmup_rules_g05_d3_s25_tp_tp_keeplast/warmup/global_step_1813/actor/huggingface",
        "group": "delta3",
        "label": "TP (δ=3) Warmup",
    },
    "tp_delta3_gad": {
        "path": "/app/wwx/EasyGAD/checkpoints/tp_warmup_rules_g05_d3_s25_tp_tp_keeplast/gad/global_step_1813/actor/huggingface",
        "group": "delta3",
        "label": "TP (δ=3) GAD",
    },
    "kgw_delta6_warmup": {
        "path": "/app/wwx/EasyGAD/checkpoints/kgwwarmup_kgwgad_gamma0.5_delta6/warmup/global_step_1813/actor/huggingface",
        "group": "delta6",
        "label": "KGW (δ=6) Warmup",
    },
    "kgw_delta6_gad": {
        "path": "/app/wwx/EasyGAD/checkpoints/kgwwarmup_kgwgad_gamma0.5_delta6/gad/global_step_1813/actor/huggingface",
        "group": "delta6",
        "label": "KGW (δ=6) GAD",
    },
    "up_dipper_delta6_warmup": {
        "path": "/app/wwx/EasyGAD/checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta6_dipper2stage/warmup/global_step_1813/actor/huggingface",
        "group": "delta6",
        "label": "UP-DIPPER (δ=6) Warmup",
    },
    "up_dipper_delta6_gad": {
        "path": "/app/wwx/EasyGAD/checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta6_dipper2stage/gad/global_step_1813/actor/huggingface",
        "group": "delta6",
        "label": "UP-DIPPER (δ=6) GAD",
    },
    "tp_delta6_warmup": {
        "path": "/app/wwx/EasyGAD/checkpoints/tp_gad_rules_g5_d6_s4_te_old_st_Qwen2.5-0.5B/warmup/global_step_1813/actor/huggingface",
        "group": "delta6",
        "label": "TP (δ=6) Warmup",
    },
    "tp_delta6_gad": {
        "path": "/app/wwx/EasyGAD/checkpoints/tp_gad_rules_g5_d6_s4_te_old_st_Qwen2.5-0.5B/gad/global_step_1813/actor/huggingface",
        "group": "delta6",
        "label": "TP (δ=6) GAD",
    },
}


def neg_log10_p_from_z(z: float) -> float:
    """Exact one-sided upper-tail -log10(1 - Phi(z)) without overflow for huge z."""
    if not math.isfinite(z):
        return 0.0
    if z <= 7.5:
        p = 0.5 * math.erfc(z / math.sqrt(2.0))
        return max(0.0, -math.log10(max(p, 1e-300)))
    # Mills ratio asymptotic expansion for z > 7.5 (accurate to >10 digits):
    # 1 - Phi(z) = phi(z)/z * (1 - 1/z^2 + 3/z^4 - 15/z^6)
    inv_z2 = 1.0 / (z * z)
    series = 1.0 - inv_z2 * (1.0 - inv_z2 * (3.0 - 15.0 * inv_z2))
    log_p = -0.5 * z * z - math.log(z * math.sqrt(2.0 * math.pi)) + math.log(max(series, 1e-12))
    return max(0.0, -log_p / math.log(10.0))


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Map & plot 3D/2D/1D Watermark Basins (Chang et al. Fig. 3)")
    p.add_argument("--work-dir", type=Path, default=Path("wm_basin_work"))
    p.add_argument("--out-dir", type=Path, default=Path("wm_basin/results/basin_plots"))
    p.add_argument(
        "--teacher-model",
        type=str,
        default="/app/public_models/Qwen2.5-14B-Instruct",
        help="Used only to read exact tokenizer len(tokenizer) matching KGW generation",
    )
    p.add_argument(
        "--traces-path",
        type=Path,
        default=None,
        help="KGW teacher traces for open-weight teacher forcing (default: <work-dir>/teacher_bank/key_0000_15485863.jsonl)",
    )
    p.add_argument(
        "--models",
        nargs="+",
        default=["ALL"],
        help="Model names to map (default: ALL 14 models; or subset e.g. kgw_delta6_gad up_dipper_delta6_warmup)",
    )
    p.add_argument("--hash-key", type=int, default=DEFAULT_TRUE_KEY)
    p.add_argument("--gamma", type=float, default=DEFAULT_GAMMA)
    p.add_argument("--num-traces", type=int, default=128, help="Teacher-forced traces per grid point (default: 128)")
    p.add_argument("--max-prompt-tokens", type=int, default=512)
    p.add_argument("--max-response-tokens", type=int, default=256)
    p.add_argument("--eval-batch-size", type=int, default=32, help="Forward batch size for 0.5B student")
    p.add_argument("--grid-n", type=int, default=25, help="2D grid resolution per axis (default: 25 -> 625 pts)")
    p.add_argument("--slice-n", type=int, default=61, help="1D slice resolution per axis (default: 61 pts)")
    p.add_argument(
        "--radius-mult-2d",
        type=float,
        default=2.0,
        help="2D grid radius as multiple of max(||Delta_wm||, ||Delta_task||)",
    )
    p.add_argument(
        "--radius-mult-1d",
        type=float,
        default=3.0,
        help="1D slice radius as multiple of max(||Delta_wm||, ||Delta_task||)",
    )
    p.add_argument("--only-plot", action="store_true", help="Re-render all plots from saved .npz caches (CPU only)")
    p.add_argument("--overwrite", action="store_true", help="Recompute existing .npz grid caches")
    return p.parse_args()


def load_cpu_state_fp32(model_path: str) -> dict[str, Any]:
    """Load floating-point named parameters of a HF CausalLM on CPU in float32."""
    import torch
    from transformers import AutoModelForCausalLM

    m = AutoModelForCausalLM.from_pretrained(model_path, torch_dtype=torch.float32, trust_remote_code=True)
    sd = {name: p.detach().cpu().clone() for name, p in m.named_parameters() if p.is_floating_point()}
    del m
    gc.collect()
    return sd


def flat_dot(a: dict[str, Any], b: dict[str, Any], keys: list[str]) -> float:
    import torch

    total = 0.0
    for k in keys:
        total += float(torch.dot(a[k].reshape(-1).double(), b[k].reshape(-1).double()).item())
    return total


def flat_norm(a: dict[str, Any], keys: list[str]) -> float:
    return math.sqrt(max(0.0, flat_dot(a, a, keys)))


def build_orthogonal_axes(
    base_sd: dict[str, Any],
    ctrl_sd: dict[str, Any],
    ref_sd: dict[str, Any],
    keys: list[str],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, float]]:
    """Eq. (1) of WM-Basin: orthogonal unit axes (u_wm, u_task) and their natural L2 norms."""
    d_task = {k: ctrl_sd[k] - base_sd[k] for k in keys}
    d_total = {k: ref_sd[k] - base_sd[k] for k in keys}

    norm_task = flat_norm(d_task, keys)
    norm_total = flat_norm(d_total, keys)
    if norm_task < 1e-12:
        raise RuntimeError("Delta_task has near-zero norm; check ctrl vs base checkpoint paths")

    proj_coeff = flat_dot(d_total, d_task, keys) / (norm_task * norm_task)
    d_wm = {k: d_total[k] - proj_coeff * d_task[k] for k in keys}
    norm_wm = flat_norm(d_wm, keys)
    if norm_wm < 1e-12:
        raise RuntimeError("Delta_wm has near-zero norm; check ref vs ctrl checkpoint paths")

    u_task = {k: (d_task[k] / norm_task).contiguous() for k in keys}
    u_wm = {k: (d_wm[k] / norm_wm).contiguous() for k in keys}
    ortho_check = abs(flat_dot(u_wm, u_task, keys))
    meta = {
        "norm_task": norm_task,
        "norm_total": norm_total,
        "norm_wm": norm_wm,
        "proj_total_on_task": proj_coeff * norm_task,
        "ortho_dot": ortho_check,
    }
    return u_wm, u_task, meta


def project_model_displacement(
    model_sd: dict[str, Any],
    ref_sd: dict[str, Any],
    u_wm: dict[str, Any],
    u_task: dict[str, Any],
    keys: list[str],
) -> dict[str, float]:
    """Decompose (theta_model - theta_ref) into Along-wm, Along-task, and Orthogonal L2."""
    diff = {k: model_sd[k] - ref_sd[k] for k in keys}
    total = flat_norm(diff, keys)
    along_wm = flat_dot(diff, u_wm, keys)
    along_task = flat_dot(diff, u_task, keys)
    orth_sq = max(0.0, total * total - along_wm * along_wm - along_task * along_task)
    return {
        "along_wm": float(along_wm),
        "along_task": float(along_task),
        "orthogonal_l2": float(math.sqrt(orth_sq)),
        "total_l2": float(total),
    }


class FastOpenWeightKGWScorer:
    """Fast teacher-forced Sander et al. (2024) open-weight KGW detector on CUDA."""

    def __init__(
        self,
        traces_path: Path,
        tokenizer,
        vocab_size: int,
        hash_key: int,
        gamma: float,
        num_traces: int,
        max_prompt_tokens: int,
        max_response_tokens: int,
        batch_size: int,
        device,
    ):
        import torch

        rows = read_jsonl(traces_path)
        encoded: list[tuple[list[int], int]] = []  # (full_ids, prompt_len)
        for r in rows:
            prompt_str = render_prompt_with_fallback(tokenizer, r["messages"], max_prompt_tokens=max_prompt_tokens)
            p_ids = tokenizer.encode(prompt_str, add_special_tokens=False)
            r_ids = tokenizer.encode(r["response"], add_special_tokens=False)[:max_response_tokens]
            if len(p_ids) < 1 or len(r_ids) < 16:
                continue
            encoded.append((p_ids + r_ids, len(p_ids)))
            if len(encoded) >= num_traces:
                break
        if not encoded:
            raise RuntimeError(f"No valid traces found in {traces_path}")

        # Sort by sequence length to minimize padding overhead
        encoded.sort(key=lambda x: len(x[0]))
        pad_id = tokenizer.pad_token_id if tokenizer.pad_token_id is not None else 0

        self.vocab_size = int(vocab_size)
        self.gamma = float(gamma)
        self.hash_key = int(hash_key)
        self.device = device
        self.batches: list[dict[str, Any]] = []

        # Collect all unique previous tokens across all scored positions
        unique_prev_set: set[int] = set()
        raw_batches = []
        for start in range(0, len(encoded), batch_size):
            chunk = encoded[start : start + batch_size]
            max_len = max(len(x[0]) for x in chunk)
            bs = len(chunk)
            inp = torch.full((bs, max_len), pad_id, dtype=torch.long)
            attn = torch.zeros((bs, max_len), dtype=torch.long)
            # Positions where shift_logits[:, t] predicts token t+1 (which is a response token)
            # For response token at index pos (pos >= prompt_len), its previous token is inp[i, pos - 1]
            # and its logits are at logits[i, pos - 1].
            score_mask = torch.zeros((bs, max_len - 1), dtype=torch.bool)
            for i, (ids, p_len) in enumerate(chunk):
                L = len(ids)
                inp[i, :L] = torch.tensor(ids, dtype=torch.long)
                attn[i, :L] = 1
                score_mask[i, p_len - 1 : L - 1] = True
            prev_tokens = inp[:, :-1][score_mask]
            for tid in prev_tokens.tolist():
                unique_prev_set.add(int(tid))
            raw_batches.append((inp, attn, score_mask, prev_tokens))

        unique_prev = sorted(unique_prev_set)
        prev_to_row = {tid: idx for idx, tid in enumerate(unique_prev)}
        greenlist_size = max(1, int(self.vocab_size * self.gamma))

        # Precompute exact CUDA greenlist lookup table bit-identical to wm_data/kgw.py
        t0 = time.time()
        green_table = torch.zeros((len(unique_prev), self.vocab_size), dtype=torch.bool, device=device)
        gen = torch.Generator(device=device)
        for row_idx, prev_tid in enumerate(unique_prev):
            seed = (self.hash_key * int(prev_tid)) % (2**63 - 1)
            gen.manual_seed(seed)
            green_ids = torch.randperm(self.vocab_size, device=device, generator=gen)[:greenlist_size]
            green_table[row_idx, green_ids] = True
        self.green_table = green_table

        total_pos = 0
        for inp, attn, score_mask, prev_tokens in raw_batches:
            prev_row_idx = torch.tensor([prev_to_row[int(t)] for t in prev_tokens.tolist()], dtype=torch.long, device=device)
            b_idx, t_idx = score_mask.nonzero(as_tuple=True)
            total_pos += int(prev_row_idx.numel())
            self.batches.append(
                {
                    "input_ids": inp.to(device),
                    "attention_mask": attn.to(device),
                    "b_idx": b_idx.to(device),
                    "t_idx": t_idx.to(device),
                    "prev_tokens": prev_tokens.to(device, dtype=torch.int64),
                    "prev_row_idx": prev_row_idx,
                }
            )
        self.num_traces = len(encoded)
        self.total_positions = total_pos
        print(
            f"[basin_eval] Precomputed exact KGW greenlist table: {len(unique_prev):,} unique prev tokens "
            f"across {self.num_traces} traces ({total_pos:,} positions, vocab={self.vocab_size}) in {time.time() - t0:.1f}s",
            flush=True,
        )

    def score_model(self, model) -> tuple[float, float, int, int]:
        """Return (neg_log10_p, z_score, unique_green, unique_total) with bigram deduplication."""
        import torch

        all_pair_keys = []
        all_green_flags = []
        with torch.inference_mode():
            for batch in self.batches:
                out = model(
                    input_ids=batch["input_ids"],
                    attention_mask=batch["attention_mask"],
                    use_cache=False,
                )
                sel_logits = out.logits[batch["b_idx"], batch["t_idx"], : self.vocab_size]
                preds = sel_logits.argmax(dim=-1)
                is_green = self.green_table[batch["prev_row_idx"], preds]
                # Encode unique (prev_token, pred_token) bigram key in int64
                pair_key = batch["prev_tokens"] * self.vocab_size + preds
                all_pair_keys.append(pair_key)
                all_green_flags.append(is_green)

        keys_cat = torch.cat(all_pair_keys, dim=0)
        green_cat = torch.cat(all_green_flags, dim=0)

        # Deduplicate unique (prev_token, pred_token) pairs on GPU (Sander et al. 2024 exact rule)
        order = torch.argsort(keys_cat)
        sorted_keys = keys_cat[order]
        sorted_green = green_cat[order]
        is_first = torch.ones_like(sorted_keys, dtype=torch.bool)
        is_first[1:] = sorted_keys[1:] != sorted_keys[:-1]
        uniq_green = int(sorted_green[is_first].sum().item())
        uniq_total = int(is_first.sum().item())

        if uniq_total == 0:
            return 0.0, 0.0, 0, 0
        z = (uniq_green - self.gamma * uniq_total) / math.sqrt(self.gamma * (1.0 - self.gamma) * uniq_total)
        nlp = neg_log10_p_from_z(z)
        return float(nlp), float(z), uniq_green, uniq_total


def set_perturbed_weights(
    gpu_params: list,
    center_gpu: list,
    u_wm_gpu: list,
    u_task_gpu: list,
    t_wm: float,
    t_task: float,
) -> None:
    import torch

    with torch.no_grad():
        for p, c, uw, ut in zip(gpu_params, center_gpu, u_wm_gpu, u_task_gpu):
            p.copy_(c)
            if t_wm != 0.0:
                p.add_(uw, alpha=t_wm)
            if t_task != 0.0:
                p.add_(ut, alpha=t_task)


def measure_half_width(coords: np.ndarray, vals: np.ndarray, threshold: float) -> float:
    """Measure total span along 1D slice where -log10(p) >= threshold around 0."""
    above = coords[vals >= threshold]
    if above.size == 0:
        return 0.0
    return float(above.max() - above.min())


def compute_model_basin(
    model_name: str,
    model_path: str,
    u_wm_cpu: dict[str, Any],
    u_task_cpu: dict[str, Any],
    param_keys: list[str],
    scorer: FastOpenWeightKGWScorer,
    radius_2d: float,
    radius_1d: float,
    grid_n: int,
    slice_n: int,
    cache_path: Path,
    device,
) -> dict[str, Any]:
    import torch
    from tqdm import tqdm
    from transformers import AutoModelForCausalLM

    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(model_path, torch_dtype=torch.bfloat16, trust_remote_code=True).to(device)
    model.eval()
    name_to_param = dict(model.named_parameters())
    gpu_params = [name_to_param[k] for k in param_keys]
    center_gpu = [p.detach().clone() for p in gpu_params]
    u_wm_gpu = [u_wm_cpu[k].to(device=device, dtype=torch.bfloat16) for k in param_keys]
    u_task_gpu = [u_task_cpu[k].to(device=device, dtype=torch.bfloat16) for k in param_keys]

    t_wm_grid = np.linspace(-radius_2d, radius_2d, grid_n)
    t_task_grid = np.linspace(-radius_2d, radius_2d, grid_n)
    nlp_2d = np.zeros((grid_n, grid_n), dtype=np.float32)  # [i_task, j_wm]
    z_2d = np.zeros((grid_n, grid_n), dtype=np.float32)

    slice_coords = np.linspace(-radius_1d, radius_1d, slice_n)
    nlp_wm_1d = np.zeros((slice_n,), dtype=np.float32)
    z_wm_1d = np.zeros((slice_n,), dtype=np.float32)
    nlp_task_1d = np.zeros((slice_n,), dtype=np.float32)
    z_task_1d = np.zeros((slice_n,), dtype=np.float32)

    try:
        # Center point (0, 0)
        set_perturbed_weights(gpu_params, center_gpu, u_wm_gpu, u_task_gpu, 0.0, 0.0)
        c_nlp, c_z, c_g, c_n = scorer.score_model(model)

        total_evals = grid_n * grid_n + 2 * slice_n
        pbar = tqdm(total=total_evals, desc=f"basin:{model_name}", unit="pt")

        # 2D landscape
        for i_t, tt in enumerate(t_task_grid):
            for j_w, tw in enumerate(t_wm_grid):
                set_perturbed_weights(gpu_params, center_gpu, u_wm_gpu, u_task_gpu, float(tw), float(tt))
                nlp, z, _, _ = scorer.score_model(model)
                nlp_2d[i_t, j_w] = nlp
                z_2d[i_t, j_w] = z
                pbar.update(1)

        # 1D slice along watermark axis
        for k, tw in enumerate(slice_coords):
            set_perturbed_weights(gpu_params, center_gpu, u_wm_gpu, u_task_gpu, float(tw), 0.0)
            nlp, z, _, _ = scorer.score_model(model)
            nlp_wm_1d[k] = nlp
            z_wm_1d[k] = z
            pbar.update(1)

        # 1D slice along task axis
        for k, tt in enumerate(slice_coords):
            set_perturbed_weights(gpu_params, center_gpu, u_wm_gpu, u_task_gpu, 0.0, float(tt))
            nlp, z, _, _ = scorer.score_model(model)
            nlp_task_1d[k] = nlp
            z_task_1d[k] = z
            pbar.update(1)

        pbar.close()
    finally:
        del model, gpu_params, center_gpu, u_wm_gpu, u_task_gpu
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(
        cache_path,
        t_wm_grid=t_wm_grid,
        t_task_grid=t_task_grid,
        nlp_2d=nlp_2d,
        z_2d=z_2d,
        slice_coords=slice_coords,
        nlp_wm_1d=nlp_wm_1d,
        z_wm_1d=z_wm_1d,
        nlp_task_1d=nlp_task_1d,
        z_task_1d=z_task_1d,
        center_nlp=np.array(c_nlp, dtype=np.float64),
        center_z=np.array(c_z, dtype=np.float64),
        center_green=np.array(c_g, dtype=np.int64),
        center_total=np.array(c_n, dtype=np.int64),
    )
    print(
        f"[basin:{model_name}] center -log10(p)={c_nlp:.2f} (z={c_z:+.2f}, {c_g}/{c_n}) | "
        f"max2D={float(nlp_2d.max()):.2f} | done in {time.time() - t0:.1f}s -> {cache_path}",
        flush=True,
    )
    return dict(np.load(cache_path))


# ---------------------------------------------------------------------------
# Plotting routines (matplotlib Agg, publication-grade styling)
# ---------------------------------------------------------------------------
def plot_single_model_figure3(
    model_name: str,
    label: str,
    group_tag: str,
    data: dict[str, Any],
    out_path: Path,
    vmax: float | None = None,
) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import cm

    t_wm = data["t_wm_grid"]
    t_task = data["t_task_grid"]
    nlp_2d = data["nlp_2d"]
    sc = data["slice_coords"]
    nlp_w = data["nlp_wm_1d"]
    nlp_t = data["nlp_task_1d"]
    c_nlp = float(data["center_nlp"])
    c_z = float(data["center_z"])

    W, T = np.meshgrid(t_wm, t_task)
    z_cap = max(float(nlp_2d.max()), float(nlp_w.max()), float(nlp_t.max()), 5.0) if vmax is None else max(vmax, 5.0)

    fig = plt.figure(figsize=(15.5, 4.6), dpi=220)

    # Panel 1: 3D surface landscape (matches Chang et al. Fig. 3 Left)
    ax1 = fig.add_subplot(1, 3, 1, projection="3d")
    surf = ax1.plot_surface(
        W,
        T,
        nlp_2d,
        cmap=cm.coolwarm,
        vmin=0.0,
        vmax=z_cap,
        linewidth=0.15,
        edgecolor=(0.2, 0.2, 0.2, 0.25),
        antialiased=True,
        alpha=0.95,
    )
    ax1.scatter([0.0], [0.0], [c_nlp + 0.02 * z_cap], color="#d62728", s=95, marker="*", zorder=10, edgecolors="black", linewidths=0.5)
    ax1.set_xlabel("watermark dir. $w$ ($L_2$)", fontsize=9, labelpad=6)
    ax1.set_ylabel("task dir. $d_{\\mathrm{task}}$ ($L_2$)", fontsize=9, labelpad=6)
    ax1.set_zlabel("$-\\log_{10} p$", fontsize=9, labelpad=4)
    ax1.set_zlim(0.0, z_cap * 1.05)
    ax1.view_init(elev=28, azim=-52)
    ax1.set_title("3D Watermark Basin", fontsize=11, fontweight="bold", pad=8)

    # Panel 2: 2D contour map (matches Chang et al. Fig. 3 Middle)
    ax2 = fig.add_subplot(1, 3, 2)
    levels = np.linspace(0.0, z_cap, 18)
    cf = ax2.contourf(W, T, nlp_2d, levels=levels, cmap="coolwarm", extend="max")
    ax2.contour(W, T, nlp_2d, levels=levels[::2], colors="k", linewidths=0.35, alpha=0.45)
    ax2.axhline(0.0, color="white", linestyle="--", linewidth=0.7, alpha=0.7)
    ax2.axvline(0.0, color="white", linestyle="--", linewidth=0.7, alpha=0.7)
    ax2.scatter([0.0], [0.0], color="#d62728", s=160, marker="*", zorder=6, edgecolors="white", linewidths=0.9, label="$\\theta_{\\mathrm{model}}$")
    cbar = fig.colorbar(cf, ax=ax2, fraction=0.046, pad=0.04)
    cbar.set_label("$-\\log_{10} p$", fontsize=9)
    ax2.set_aspect("equal", adjustable="box")
    ax2.set_xlabel("watermark dir. $w$ ($L_2$)", fontsize=10)
    ax2.set_ylabel("task dir. $d_{\\mathrm{task}}$ ($L_2$)", fontsize=10)
    ax2.set_title("2D Basin Contour", fontsize=11, fontweight="bold")
    ax2.legend(loc="upper right", fontsize=8.5, framealpha=0.85)

    # Panel 3: 1D slices through center model (matches Chang et al. Fig. 3 Right)
    ax3 = fig.add_subplot(1, 3, 3)
    ax3.plot(sc, nlp_w, color="#d62728", linewidth=2.2, label="watermark dir. $\\hat{\\Delta}_{\\mathrm{wm}}$")
    ax3.plot(sc, nlp_t, color="#2ca02c", linewidth=2.2, label="task dir. $\\hat{\\Delta}_{\\mathrm{task}}$")
    ax3.axhline(1.301, color="gray", linestyle=":", linewidth=1.2, label="$p=0.05$ ($-\\log_{10}p=1.30$)")
    ax3.axvline(0.0, color="black", linestyle="--", linewidth=0.8, alpha=0.4)
    ax3.set_ylim(-0.02 * z_cap, z_cap * 1.08)
    ax3.set_xlabel("Perturbation magnitude ($L_2$)", fontsize=10)
    ax3.set_ylabel("$-\\log_{10} p$", fontsize=10)
    ax3.set_title("1D Slices through $\\theta_{\\mathrm{model}}$", fontsize=11, fontweight="bold")
    ax3.grid(True, linestyle="--", alpha=0.35)
    ax3.legend(loc="upper right", fontsize=8.5, framealpha=0.9)

    fig.suptitle(
        f"Watermark Basin Geometry — {label}  [{group_tag} axes | center $-\\log_{{10}}p={c_nlp:.2f}$, $z={c_z:+.2f}$]",
        fontsize=12.5,
        fontweight="bold",
        y=0.99,
    )
    plt.tight_layout(rect=[0, 0, 1, 0.94])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=220)
    plt.close(fig)


def plot_group_overview(
    group_name: str,
    ref_model: str,
    ref_data: dict[str, Any],
    all_model_data: dict[str, dict[str, Any]],
    projections: dict[str, dict[str, float]],
    member_names: list[str],
    out_path: Path,
) -> None:
    """Overview figure: (A) 2D basin of ref KGW-GAD with all models projected, (B) 1D wm-axis slices, (C) Along-wm bar."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    t_wm = ref_data["t_wm_grid"]
    t_task = ref_data["t_task_grid"]
    nlp_2d = ref_data["nlp_2d"]
    W, T = np.meshgrid(t_wm, t_task)
    z_cap = max(float(nlp_2d.max()), 5.0)

    style_map = {
        "kgw": ("#d62728", "*", 170),
        "up_dipper": ("#ff7f0e", "D", 75),
        "tp": ("#1f77b4", "X", 95),
        "clean": ("#2ca02c", "s", 80),
        "base": ("#7f7f7f", "o", 75),
    }

    def pick_style(mname: str):
        for prefix, st in style_map.items():
            if mname.startswith(prefix):
                return st
        return ("#9467bd", "o", 70)

    fig, axes = plt.subplots(1, 3, figsize=(17.0, 5.0), dpi=220)

    # Panel A: 2D contour of canonical KGW-GAD + projected positions of all models
    ax = axes[0]
    levels = np.linspace(0.0, z_cap, 18)
    cf = ax.contourf(W, T, nlp_2d, levels=levels, cmap="coolwarm", alpha=0.88, extend="max")
    ax.contour(W, T, nlp_2d, levels=levels[::2], colors="k", linewidths=0.35, alpha=0.35)
    fig.colorbar(cf, ax=ax, fraction=0.046, pad=0.03, label="$-\\log_{10} p$")
    for mname in member_names:
        if mname not in projections:
            continue
        p = projections[mname]
        color, marker, sz = pick_style(mname)
        lbl = DEFAULT_MODELS.get(mname, {}).get("label", mname)
        ax.scatter(
            [p["along_wm"]],
            [p["along_task"]],
            color=color,
            marker=marker,
            s=sz,
            edgecolors="black",
            linewidths=0.8,
            zorder=8,
            label=lbl,
        )
        ax.annotate(
            lbl.replace(f" (δ={group_name[-1]})", ""),
            (p["along_wm"], p["along_task"]),
            xytext=(5, 4),
            textcoords="offset points",
            fontsize=7.5,
            fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.72),
            zorder=9,
        )
    ax.axhline(0.0, color="white", linestyle="--", linewidth=0.7, alpha=0.7)
    ax.axvline(0.0, color="white", linestyle="--", linewidth=0.7, alpha=0.7)
    ax.set_xlabel("Projection along watermark axis $\\hat{\\Delta}_{\\mathrm{wm}}$ ($L_2$)", fontsize=9.5)
    ax.set_ylabel("Projection along task axis $\\hat{\\Delta}_{\\mathrm{task}}$ ($L_2$)", fontsize=9.5)
    ax.set_title(f"(a) Models Projected onto {group_name} Basin", fontsize=11, fontweight="bold")

    # Panel B: 1D watermark-axis slices across all models
    ax2 = axes[1]
    for mname in member_names:
        if mname not in all_model_data:
            continue
        d = all_model_data[mname]
        color, _, _ = pick_style(mname)
        ls = "--" if "warmup" in mname else "-"
        lbl = DEFAULT_MODELS.get(mname, {}).get("label", mname).replace(f" (δ={group_name[-1]})", "")
        ax2.plot(d["slice_coords"], d["nlp_wm_1d"], color=color, linestyle=ls, linewidth=1.9, label=lbl)
    ax2.axhline(1.301, color="gray", linestyle=":", linewidth=1.1, label="$p=0.05$")
    ax2.axvline(0.0, color="black", linestyle="--", linewidth=0.7, alpha=0.4)
    ax2.set_xlabel("Perturbation along $\\hat{\\Delta}_{\\mathrm{wm}}$ ($L_2$)", fontsize=9.5)
    ax2.set_ylabel("$-\\log_{10} p$", fontsize=9.5)
    ax2.set_title("(b) 1D Watermark-Axis Slices per Model", fontsize=11, fontweight="bold")
    ax2.grid(True, linestyle="--", alpha=0.35)
    ax2.legend(fontsize=7.5, loc="upper right", framealpha=0.88)

    # Panel C: Signed displacement along watermark axis relative to Clean-GAD
    ax3 = axes[2]
    clean_x = projections.get("clean_gad_control", {}).get("along_wm", 0.0)
    bar_names = [m for m in member_names if m in projections]
    bar_labels = [DEFAULT_MODELS.get(m, {}).get("label", m).replace(f" (δ={group_name[-1]})", "") for m in bar_names]
    bar_vals = [projections[m]["along_wm"] - clean_x for m in bar_names]
    bar_cols = [pick_style(m)[0] for m in bar_names]
    y_pos = np.arange(len(bar_names))
    ax3.barh(y_pos, bar_vals, color=bar_cols, edgecolor="black", linewidth=0.6, alpha=0.9)
    ax3.axvline(0.0, color="black", linewidth=1.0)
    ax3.set_yticks(y_pos)
    ax3.set_yticklabels(bar_labels, fontsize=8.5)
    ax3.invert_yaxis()
    ax3.set_xlabel("Signed coordinate along $\\hat{\\Delta}_{\\mathrm{wm}}$ vs Clean-GAD ($L_2$)", fontsize=9)
    ax3.set_title("(c) Position Along Watermark Axis", fontsize=11, fontweight="bold")
    ax3.grid(True, axis="x", linestyle="--", alpha=0.35)

    fig.suptitle(f"Watermark Basin Overview ({group_name}, reference = {ref_model})", fontsize=13, fontweight="bold", y=0.99)
    plt.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(out_path, dpi=220)
    plt.close(fig)


def plot_group_gallery(
    group_name: str,
    all_model_data: dict[str, dict[str, Any]],
    member_names: list[str],
    out_path: Path,
) -> None:
    """2x4 side-by-side 2D contour gallery on a unified colorbar for instant visual comparison."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    avail = [m for m in member_names if m in all_model_data]
    if not avail:
        return
    z_cap = max([float(all_model_data[m]["nlp_2d"].max()) for m in avail] + [5.0])
    levels = np.linspace(0.0, z_cap, 18)

    ncols = 4
    nrows = int(math.ceil(len(avail) / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(4.2 * ncols, 3.9 * nrows), dpi=220, squeeze=False)
    cf = None
    for idx, mname in enumerate(avail):
        r, c = divmod(idx, ncols)
        ax = axes[r][c]
        d = all_model_data[mname]
        W, T = np.meshgrid(d["t_wm_grid"], d["t_task_grid"])
        cf = ax.contourf(W, T, d["nlp_2d"], levels=levels, cmap="coolwarm", extend="max")
        ax.contour(W, T, d["nlp_2d"], levels=levels[::3], colors="k", linewidths=0.3, alpha=0.4)
        ax.scatter([0.0], [0.0], color="#d62728", s=110, marker="*", edgecolors="white", linewidths=0.8, zorder=6)
        lbl = DEFAULT_MODELS.get(mname, {}).get("label", mname)
        c_nlp = float(d["center_nlp"])
        c_z = float(d["center_z"])
        ax.set_title(f"{lbl}\n$-\\log_{{10}}p={c_nlp:.1f}$ ($z={c_z:+.1f}$)", fontsize=9.5, fontweight="bold")
        ax.set_aspect("equal", adjustable="box")
        if r == nrows - 1:
            ax.set_xlabel("watermark dir. $w$", fontsize=8.5)
        if c == 0:
            ax.set_ylabel("task dir. $d_{\\mathrm{task}}$", fontsize=8.5)

    for idx in range(len(avail), nrows * ncols):
        r, c = divmod(idx, ncols)
        axes[r][c].axis("off")

    fig.subplots_adjust(right=0.91, top=0.88, wspace=0.25, hspace=0.35)
    if cf is not None:
        cbar_ax = fig.add_axes([0.93, 0.14, 0.018, 0.70])
        fig.colorbar(cf, cax=cbar_ax, label="$-\\log_{10} p$")
    fig.suptitle(f"2D Watermark Basin Gallery — {group_name} (Unified Colorbar)", fontsize=13, fontweight="bold", y=0.97)
    fig.savefig(out_path, dpi=220)
    plt.close(fig)


def main() -> None:
    args = parse_args()
    cache_dir = args.work_dir / "basin_grids"
    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)

    target_models = list(DEFAULT_MODELS.keys()) if args.models == ["ALL"] else args.models
    for m in target_models:
        if m not in DEFAULT_MODELS:
            raise ValueError(f"Unknown model name '{m}'. Choices: {list(DEFAULT_MODELS.keys())}")

    # Determine which delta groups are needed
    need_delta6 = any(DEFAULT_MODELS[m]["group"] in ("delta6", "control") for m in target_models)
    need_delta3 = any(DEFAULT_MODELS[m]["group"] == "delta3" for m in target_models)
    groups_to_run: list[tuple[str, str, list[str]]] = []
    if need_delta6:
        d6_members = [
            "kgw_delta6_gad",
            "kgw_delta6_warmup",
            "up_dipper_delta6_warmup",
            "up_dipper_delta6_gad",
            "tp_delta6_warmup",
            "tp_delta6_gad",
            "clean_gad_control",
            "base_qwen25_05b",
        ]
        groups_to_run.append(("delta6", "kgw_delta6_gad", [m for m in d6_members if m in target_models]))
    if need_delta3:
        d3_members = [
            "kgw_delta3_gad",
            "kgw_delta3_warmup",
            "up_dipper_delta3_warmup",
            "up_dipper_delta3_gad",
            "tp_delta3_warmup",
            "tp_delta3_gad",
            "clean_gad_control",
            "base_qwen25_05b",
        ]
        groups_to_run.append(("delta3", "kgw_delta3_gad", [m for m in d3_members if m in target_models]))

    summary_json_path = out_dir / "basin_geometry_summary.json"
    summary: dict[str, Any] = {"groups": {}, "models": {}}

    scorer = None
    device = None
    base_sd = None
    ctrl_sd = None
    param_keys: list[str] = []

    if not args.only_plot:
        import torch
        from transformers import AutoTokenizer

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        traces_path = args.traces_path or (args.work_dir / "teacher_bank" / f"key_0000_{args.hash_key}.jsonl")
        if not traces_path.exists():
            raise FileNotFoundError(f"Teacher traces not found: {traces_path}")

        teacher_tok = AutoTokenizer.from_pretrained(args.teacher_model, trust_remote_code=True)
        vocab_size = len(teacher_tok)
        student_tok = AutoTokenizer.from_pretrained(DEFAULT_MODELS["base_qwen25_05b"]["path"], trust_remote_code=True)
        if student_tok.pad_token_id is None:
            student_tok.pad_token = student_tok.eos_token

        scorer = FastOpenWeightKGWScorer(
            traces_path=traces_path,
            tokenizer=student_tok,
            vocab_size=vocab_size,
            hash_key=args.hash_key,
            gamma=args.gamma,
            num_traces=args.num_traces,
            max_prompt_tokens=args.max_prompt_tokens,
            max_response_tokens=args.max_response_tokens,
            batch_size=args.eval_batch_size,
            device=device,
        )

        print("[basin] Loading base & clean_gad_control weights on CPU...", flush=True)
        base_sd = load_cpu_state_fp32(DEFAULT_MODELS["base_qwen25_05b"]["path"])
        ctrl_sd = load_cpu_state_fp32(DEFAULT_MODELS["clean_gad_control"]["path"])
        param_keys = sorted(base_sd.keys())

    # Process each group
    for group_name, ref_model, members in groups_to_run:
        print(f"\n================ Group: {group_name} (ref={ref_model}) ================", flush=True)
        group_projections: dict[str, dict[str, float]] = {}
        group_axes_meta: dict[str, float] = {}
        u_wm_cpu = None
        u_task_cpu = None
        radius_2d = 20.0
        radius_1d = 30.0

        if not args.only_plot:
            ref_sd = load_cpu_state_fp32(DEFAULT_MODELS[ref_model]["path"])
            u_wm_cpu, u_task_cpu, group_axes_meta = build_orthogonal_axes(base_sd, ctrl_sd, ref_sd, param_keys)
            nat_scale = max(group_axes_meta["norm_wm"], group_axes_meta["norm_task"])
            radius_2d = args.radius_mult_2d * nat_scale
            radius_1d = args.radius_mult_1d * nat_scale
            print(
                f"[axes:{group_name}] ||Delta_wm||={group_axes_meta['norm_wm']:.3f}, "
                f"||Delta_task||={group_axes_meta['norm_task']:.3f}, "
                f"ortho_dot={group_axes_meta['ortho_dot']:.2e}, "
                f"R_2D={radius_2d:.2f}, R_1D={radius_1d:.2f}",
                flush=True,
            )
            # Project all member models onto (u_wm, u_task)
            for mname in members:
                if mname == "base_qwen25_05b":
                    msd = base_sd
                elif mname == "clean_gad_control":
                    msd = ctrl_sd
                elif mname == ref_model:
                    msd = ref_sd
                else:
                    msd = load_cpu_state_fp32(DEFAULT_MODELS[mname]["path"])
                group_projections[mname] = project_model_displacement(msd, ref_sd, u_wm_cpu, u_task_cpu, param_keys)
                if mname not in ("base_qwen25_05b", "clean_gad_control", ref_model):
                    del msd
                    gc.collect()
            del ref_sd
            gc.collect()
        elif summary_json_path.exists():
            prev = dict(__import__("json").loads(summary_json_path.read_text(encoding="utf-8")))
            g_prev = prev.get("groups", {}).get(group_name, {})
            group_axes_meta = g_prev.get("axes_meta", {})
            group_projections = g_prev.get("projections", {})

        group_data: dict[str, dict[str, Any]] = {}
        for mname in members:
            # Controls share delta6 axes when both groups run, or get group-tagged cache
            cache_file = cache_dir / f"{group_name}__{mname}.npz"
            if cache_file.exists() and not args.overwrite:
                data = dict(np.load(cache_file))
                print(f"[basin:{group_name}/{mname}] Loaded cached grid -> {cache_file}", flush=True)
            else:
                if args.only_plot:
                    print(f"[basin:{group_name}/{mname}] Missing cache {cache_file}, skipping in --only-plot mode.")
                    continue
                data = compute_model_basin(
                    model_name=f"{group_name}/{mname}",
                    model_path=DEFAULT_MODELS[mname]["path"],
                    u_wm_cpu=u_wm_cpu,
                    u_task_cpu=u_task_cpu,
                    param_keys=param_keys,
                    scorer=scorer,
                    radius_2d=radius_2d,
                    radius_1d=radius_1d,
                    grid_n=args.grid_n,
                    slice_n=args.slice_n,
                    cache_path=cache_file,
                    device=device,
                )
            group_data[mname] = data

            # Render individual Figure 3 (3D + 2D + 1D) for every model!
            # Avoid duplicate filenames for controls by tagging with group when delta3
            if DEFAULT_MODELS[mname]["group"] == "control" and group_name == "delta3" and need_delta6:
                fig_name = f"basin_{mname}_on_delta3.png"
            else:
                fig_name = f"basin_{mname}.png"
            plot_single_model_figure3(
                model_name=mname,
                label=DEFAULT_MODELS[mname]["label"],
                group_tag=group_name,
                data=data,
                out_path=out_dir / fig_name,
            )

            # Record geometry metrics
            wm_w = measure_half_width(data["slice_coords"], data["nlp_wm_1d"], threshold=1.301)
            task_w = measure_half_width(data["slice_coords"], data["nlp_task_1d"], threshold=1.301)
            summary["models"][f"{group_name}/{mname}"] = {
                "model": mname,
                "group": group_name,
                "label": DEFAULT_MODELS[mname]["label"],
                "center_neg_log10_p": float(data["center_nlp"]),
                "center_z": float(data["center_z"]),
                "center_green": int(data["center_green"]),
                "center_total": int(data["center_total"]),
                "max_2d_neg_log10_p": float(data["nlp_2d"].max()),
                "wm_width_at_p05_L2": wm_w,
                "task_width_at_p05_L2": task_w,
                "anisotropy_ratio": (task_w / wm_w) if wm_w > 1e-6 else None,
                "projection": group_projections.get(mname, {}),
                "plot_file": fig_name,
            }

        if ref_model in group_data:
            plot_group_overview(
                group_name=group_name,
                ref_model=ref_model,
                ref_data=group_data[ref_model],
                all_model_data=group_data,
                projections=group_projections,
                member_names=members,
                out_path=out_dir / f"overview_basin_{group_name}.png",
            )
        plot_group_gallery(
            group_name=group_name,
            all_model_data=group_data,
            member_names=members,
            out_path=out_dir / f"gallery_{group_name}.png",
        )
        summary["groups"][group_name] = {
            "ref_model": ref_model,
            "axes_meta": group_axes_meta,
            "projections": group_projections,
        }

    # Save JSON + clean Markdown geometry table
    write_json(summary_json_path, summary)
    md_lines = [
        "# Watermark Basin Weight-Space Geometry Summary (Figure 3 Reproduction)",
        "",
        "| Group | Model | Center `-log10 p` | Center `z` | Max 2D `-log10 p` | WM Width ($p\\le 0.05$) | Task Width ($p\\le 0.05$) | Along $w$ ($L_2$) | Along Task ($L_2$) | Orth ($L_2$) | Plot |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for key, rec in summary["models"].items():
        p = rec.get("projection", {})
        aw = f"{p['along_wm']:+.2f}" if "along_wm" in p else "—"
        at = f"{p['along_task']:+.2f}" if "along_task" in p else "—"
        ao = f"{p['orthogonal_l2']:.2f}" if "orthogonal_l2" in p else "—"
        md_lines.append(
            f"| `{rec['group']}` | `{rec['model']}` | **{rec['center_neg_log10_p']:.2f}** | "
            f"`{rec['center_z']:+.2f}` | `{rec['max_2d_neg_log10_p']:.2f}` | "
            f"`{rec['wm_width_at_p05_L2']:.2f}` | `{rec['task_width_at_p05_L2']:.2f}` | "
            f"`{aw}` | `{at}` | `{ao}` | `{rec['plot_file']}` |"
        )
    md_lines.append("")
    md_path = out_dir / "basin_geometry_summary.md"
    md_path.write_text("\n".join(md_lines), encoding="utf-8")
    print(f"\n[basin] ALL DONE! Plots & geometry summary saved in {out_dir}", flush=True)


if __name__ == "__main__":
    main()
