
## 评估记录：2026-10-05T12:13:04+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.600458
- Best F1：0.682995（z 阈值 -2.0303030303030303，TPR 0.976000，FPR 0.882000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.000000 | 0.000000 | 0.000000 | None |
  | 5% | 0.050000 | 0.026000 | 0.048327 | 3.5555555555555554 |
  | 10% | 0.100000 | 0.132000 | 0.214286 | 2.141239281438989 |

两种逐条文本 p-value 统计（单侧正态近似；不是 AUROC 的显著性检验）：

去重规则：相同的 `(previous_token_id, token_id)` 只计一次；不修改回答文本。

| 数据 | 检测方式 | 有效样本 | p 均值 | p 中位数 | p≤0.01 | p≤0.05 | p≤0.10 |
|---|---|---:|---:|---:|---:|---:|---:|
| kgw | 原始 | 500/500 | 0.366206 | 0.302604 | 51 (10.20%) | 103 (20.60%) | 145 (29.00%) |
| kgw | token 对去重 | 500/500 | 0.373617 | 0.315403 | 24 (4.80%) | 62 (12.40%) | 104 (20.80%) |
| clean | 原始 | 500/500 | 0.489848 | 0.473107 | 42 (8.40%) | 71 (14.20%) | 102 (20.40%) |
| clean | token 对去重 | 500/500 | 0.493376 | 0.5 | 7 (1.40%) | 29 (5.80%) | 61 (12.20%) |

KGW 的小 p 占比是该理论阈值下的检出率，clean 的小 p 占比是实测误报率。p≤0.05 不保证实际 FPR=5%；去重可改善重复带来的失真，但不保证完全校准。空回答不做显著性检验，p=null，并排除在有效样本统计之外。

逐条 p-value：`/shared/wwx/EasyGAD/wm_test/kgwwarmup_cleangad_gad_qwen2_5_0_5b_dolly15k_test.p_values.jsonl`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test.p_values.jsonl`

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.6004579999999998,
  "best_f1": {
    "threshold": -2.0303030303030303,
    "fpr": 0.882,
    "tpr": 0.976,
    "precision": 0.5252960172228203,
    "f1": 0.6829951014695592,
    "tp": 488,
    "fp": 441,
    "tn": 59,
    "fn": 12
  },
  "tpr_at_fpr": {
    "1%": {
      "threshold": null,
      "fpr": 0.0,
      "tpr": 0.0,
      "precision": 0.0,
      "f1": 0.0,
      "tp": 0,
      "fp": 0,
      "tn": 500,
      "fn": 500,
      "target_fpr": 0.01
    },
    "5%": {
      "threshold": 3.5555555555555554,
      "fpr": 0.05,
      "tpr": 0.026,
      "precision": 0.34210526315789475,
      "f1": 0.0483271375464684,
      "tp": 13,
      "fp": 25,
      "tn": 475,
      "fn": 487,
      "target_fpr": 0.05
    },
    "10%": {
      "threshold": 2.141239281438989,
      "fpr": 0.1,
      "tpr": 0.132,
      "precision": 0.5689655172413793,
      "f1": 0.21428571428571427,
      "tp": 66,
      "fp": 50,
      "tn": 450,
      "fn": 434,
      "target_fpr": 0.1
    }
  },
  "note": "For each target FPR, select the empirical ROC point with the highest TPR whose FPR does not exceed the target; tied scores are kept together.",
  "p_values": {
    "kgw": {
      "raw": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.366206425570285,
        "median": 0.3026038169157176,
        "min": 5.460103213465051e-09,
        "max": 0.999999999999998,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 51,
            "fraction": 0.102
          },
          "5%": {
            "alpha": 0.05,
            "count": 103,
            "fraction": 0.206
          },
          "10%": {
            "alpha": 0.1,
            "count": 145,
            "fraction": 0.29
          }
        }
      },
      "deduplicated": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.3736173385023518,
        "median": 0.315403424171104,
        "min": 2.2630152656432415e-05,
        "max": 0.994979056704527,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 24,
            "fraction": 0.048
          },
          "5%": {
            "alpha": 0.05,
            "count": 62,
            "fraction": 0.124
          },
          "10%": {
            "alpha": 0.1,
            "count": 104,
            "fraction": 0.208
          }
        }
      }
    },
    "clean": {
      "raw": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.4898484984234752,
        "median": 0.47310655220988485,
        "min": 1.6726509285640453e-112,
        "max": 1.0,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 42,
            "fraction": 0.084
          },
          "5%": {
            "alpha": 0.05,
            "count": 71,
            "fraction": 0.142
          },
          "10%": {
            "alpha": 0.1,
            "count": 102,
            "fraction": 0.204
          }
        }
      },
      "deduplicated": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.49337648065434225,
        "median": 0.5,
        "min": 0.0011733627719406451,
        "max": 0.9992323580322656,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 7,
            "fraction": 0.014
          },
          "5%": {
            "alpha": 0.05,
            "count": 29,
            "fraction": 0.058
          },
          "10%": {
            "alpha": 0.1,
            "count": 61,
            "fraction": 0.122
          }
        }
      }
    }
  },
  "p_value_method": "one-sided normal survival probability; unique context-token pairs for dedup",
  "per_sample_p_value_files": {
    "kgw": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_cleangad_gad_qwen2_5_0_5b_dolly15k_test.p_values.jsonl",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test.p_values.jsonl"
  },
  "evaluated_at": "2026-10-05T12:13:04+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_cleangad_gad_qwen2_5_0_5b_dolly15k_test.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/pvalue_update_20261005/verification_history.md"
}
```
