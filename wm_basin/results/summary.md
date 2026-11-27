# WM-Basin Single-Pool Audit Summary

- **Generated (UTC)**: `2026-11-27T13:20:31.886524+00:00`
- **Probe**: `/app/public_models/Qwen2.5-0.5B` (LoRA `r=128`, epochs=`4`)
- **Projector**: `proj_dim=131072`, `weighting=token`
- **Clean PCA**: `q=40`, `57` cells (`19` base models)

| Suspect | Used / Tokens | Raw Rank | **WM-Basin Rank** | **`p_rank`** | **`S(k*)`** | **`z-score`** | **@5% Verdict** |
|---|---:|---:|---:|---:|---:|---:|---|
| `base_qwen25_05b` | 1732 / 384,537 | 31/40 | **36/40** | `0.9000` | `-0.00909` | `-1.05` | No evidence |
| `base_qwen25_05b_on_ext` | 1688 / 375,135 | 31/40 | **39/40** | `0.9750` | `+0.02125` | `-2.10` | No evidence |
| `clean_gad_control` | 1795 / 388,671 | 39/40 | **36/40** | `0.9000` | `+0.01758` | `-1.35` | No evidence |
| `clean_gad_control_on_ext` | 1562 / 375,441 | 40/40 | **35/40** | `0.8750` | `+0.01620` | `-1.44` | No evidence |
| `kgw_delta3_gad` | 1864 / 484,593 | 14/40 | **6/40** | `0.1500` | `+0.11839` | `+1.04` | No evidence |
| `kgw_delta3_gad_on_ext` | 1673 / 494,507 | 1/40 | **2/40** | `0.0500` | `+0.18877` | `+2.49` | **DISTILLED** |
| `kgw_delta3_warmup_on_ext` | 1649 / 482,296 | 31/40 | **3/40** | `0.0750` | `-0.02261` | `+1.84` | No evidence |
| `kgw_delta6_gad` | 1777 / 462,690 | 18/40 | **1/40** | `0.0250` | `+0.16482` | `+1.68` | **DISTILLED** |
| `kgw_delta6_gad_on_ext` | 1554 / 413,845 | 13/40 | **1/40** | `0.0250` | `+0.26255` | `+2.60` | **DISTILLED** |
| `kgw_delta6_warmup` | 1906 / 719,529 | 29/40 | **2/40** | `0.0500` | `-0.02784` | `+1.56` | **DISTILLED** |
| `kgw_delta6_warmup_on_ext` | 1696 / 578,849 | 28/40 | **2/40** | `0.0500` | `-0.03102` | `+2.32` | **DISTILLED** |
| `tp_delta3_gad_on_ext` | 1730 / 309,924 | 37/40 | **39/40** | `0.9750` | `-0.03866` | `-1.51` | No evidence |
| `tp_delta3_warmup_on_ext` | 1794 / 394,327 | 37/40 | **33/40** | `0.8250` | `-0.08564` | `-1.02` | No evidence |
| `tp_delta6_gad_on_ext` | 1696 / 238,571 | 39/40 | **39/40** | `0.9750` | `-0.07610` | `-1.43` | No evidence |
| `tp_delta6_warmup_on_ext` | 1840 / 381,468 | 38/40 | **37/40** | `0.9250` | `-0.08222` | `-1.21` | No evidence |
| `up_dipper_delta3_gad_on_ext` | 1595 / 229,301 | 18/40 | **7/40** | `0.1750` | `-0.00814` | `+1.08` | No evidence |
| `up_dipper_delta3_warmup_on_ext` | 1653 / 308,659 | 26/40 | **8/40** | `0.2000` | `-0.05696` | `+1.09` | No evidence |
| `up_dipper_delta6_gad_on_ext` | 1567 / 206,180 | 18/40 | **7/40** | `0.1750` | `-0.00153` | `+0.88` | No evidence |
| `up_dipper_delta6_warmup_on_ext` | 1648 / 336,779 | 23/40 | **3/40** | `0.0750` | `-0.04372` | `+1.55` | No evidence |
