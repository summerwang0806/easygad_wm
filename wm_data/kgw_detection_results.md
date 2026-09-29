# KGW detection experiment results

This file is append-only: every evaluation run adds a timestamped record.

## Run 2026-09-24T16:36:16+08:00

- Positive class: `kgw`
- Detection score: `z_score` (larger means more likely watermarked)
- Fixed decision: `z_score >= 4.0`
- TPR@FPR: the highest empirical TPR whose empirical FPR does not exceed the target

### Input files

- `clean_train`: `/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_clean_train_kgw_scores.jsonl`
- `kgw_train`: `/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_kgw_train_kgw_scores.jsonl`
- `clean_test`: `/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_clean_test_kgw_scores.jsonl`
- `kgw_test`: `/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_kgw_test_kgw_scores.jsonl`

### Summary

| Split | Clean | KGW | AUROC | TPR@FPR=1% | TPR@FPR=5% | TPR@FPR=10% | Fixed F1 | Best F1 | Best threshold |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| train | 14511 | 14511 | 0.865916 | 0.542485 | 0.652264 | 0.711116 | 0.615260 | 0.789685 | 1.309307 |
| test | 500 | 500 | 0.877674 | 0.602000 | 0.692000 | 0.740000 | 0.662216 | 0.809061 | 1.513289 |

### TPR operating points

| Split | Target FPR | Achieved FPR | TPR | Threshold | TP | FP |
|---|---:|---:|---:|---:|---:|---:|
| train | 1% | 0.009992 | 0.542485 | 3.067399 | 7872 | 145 |
| train | 5% | 0.049893 | 0.652264 | 2.094786 | 9465 | 724 |
| train | 10% | 0.099993 | 0.711116 | 1.601282 | 10319 | 1451 |
| test | 1% | 0.010000 | 0.602000 | 2.958109 | 301 | 5 |
| test | 5% | 0.050000 | 0.692000 | 2.036744 | 346 | 25 |
| test | 10% | 0.096000 | 0.740000 | 1.549193 | 370 | 48 |

### F1 details

| Split | Type | Threshold | F1 | Precision | Recall/TPR | FPR | TP | FP | TN | FN |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| train | fixed | 4.000000 | 0.615260 | 0.994614 | 0.445386 | 0.002412 | 6463 | 35 | 14476 | 8048 |
| train | best | 1.309307 | 0.789685 | 0.837518 | 0.747020 | 0.144925 | 10840 | 2103 | 12408 | 3671 |
| test | fixed | 4.000000 | 0.662216 | 0.995984 | 0.496000 | 0.002000 | 248 | 1 | 499 | 252 |
| test | best | 1.513289 | 0.809061 | 0.878220 | 0.750000 | 0.104000 | 375 | 52 | 448 | 125 |

---
## Run 2026-09-24T16:37:23+08:00

- Positive class: `kgw`
- Detection score: `z_score` (larger means more likely watermarked)
- Fixed decision: `z_score >= 4.0`
- TPR@FPR: the highest empirical TPR whose empirical FPR does not exceed the target

### Input files

- `clean_train`: `/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_clean_train_kgw_scores.jsonl`
- `kgw_train`: `/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_kgw_train_kgw_scores.jsonl`
- `clean_test`: `/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_clean_test_kgw_scores.jsonl`
- `kgw_test`: `/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_kgw_test_kgw_scores.jsonl`

### Summary

| Split | Clean | KGW | AUROC | TPR@FPR=1% | TPR@FPR=5% | TPR@FPR=10% | Fixed F1 | Best F1 | Best threshold |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| train | 14511 | 14511 | 0.865916 | 0.542485 | 0.652264 | 0.711116 | 0.615260 | 0.789685 | 1.309307 |
| test | 500 | 500 | 0.877674 | 0.602000 | 0.692000 | 0.740000 | 0.662216 | 0.809061 | 1.513289 |

### TPR operating points

| Split | Target FPR | Achieved FPR | TPR | Threshold | TP | FP |
|---|---:|---:|---:|---:|---:|---:|
| train | 1% | 0.009992 | 0.542485 | 3.067399 | 7872 | 145 |
| train | 5% | 0.049893 | 0.652264 | 2.094786 | 9465 | 724 |
| train | 10% | 0.099993 | 0.711116 | 1.601282 | 10319 | 1451 |
| test | 1% | 0.010000 | 0.602000 | 2.958109 | 301 | 5 |
| test | 5% | 0.050000 | 0.692000 | 2.036744 | 346 | 25 |
| test | 10% | 0.096000 | 0.740000 | 1.549193 | 370 | 48 |

### F1 details

| Split | Type | Threshold | F1 | Precision | Recall/TPR | FPR | TP | FP | TN | FN |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| train | fixed | 4.000000 | 0.615260 | 0.994614 | 0.445386 | 0.002412 | 6463 | 35 | 14476 | 8048 |
| train | best | 1.309307 | 0.789685 | 0.837518 | 0.747020 | 0.144925 | 10840 | 2103 | 12408 | 3671 |
| test | fixed | 4.000000 | 0.662216 | 0.995984 | 0.496000 | 0.002000 | 248 | 1 | 499 | 252 |
| test | best | 1.513289 | 0.809061 | 0.878220 | 0.750000 | 0.104000 | 375 | 52 | 448 | 125 |

---
