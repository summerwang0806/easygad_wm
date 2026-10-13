
## 评估记录：2026-09-24T16:26:21+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.752630
- Best F1：0.697436（z 阈值 -0.8687219087128831，TPR 0.952000，FPR 0.778000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.010000 | 0.144000 | 0.249567 | 3.3807363888764597 |
  | 5% | 0.050000 | 0.372000 | 0.523207 | 2.06418738616856 |
  | 10% | 0.098000 | 0.462000 | 0.592308 | 1.5782189036217624 |

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.7526300000000007,
  "best_f1": {
    "threshold": -0.8687219087128831,
    "fpr": 0.778,
    "tpr": 0.952,
    "precision": 0.5502890173410404,
    "f1": 0.6974358974358974,
    "tp": 476,
    "fp": 389,
    "tn": 111,
    "fn": 24
  },
  "tpr_at_fpr": {
    "1%": {
      "threshold": 3.3807363888764597,
      "fpr": 0.01,
      "tpr": 0.144,
      "precision": 0.935064935064935,
      "f1": 0.24956672443674174,
      "tp": 72,
      "fp": 5,
      "tn": 495,
      "fn": 428,
      "target_fpr": 0.01
    },
    "5%": {
      "threshold": 2.06418738616856,
      "fpr": 0.05,
      "tpr": 0.372,
      "precision": 0.8815165876777251,
      "f1": 0.5232067510548524,
      "tp": 186,
      "fp": 25,
      "tn": 475,
      "fn": 314,
      "target_fpr": 0.05
    },
    "10%": {
      "threshold": 1.5782189036217624,
      "fpr": 0.098,
      "tpr": 0.462,
      "precision": 0.825,
      "f1": 0.5923076923076923,
      "tp": 231,
      "fp": 49,
      "tn": 451,
      "fn": 269,
      "target_fpr": 0.1
    }
  },
  "note": "For each target FPR, select the empirical ROC point with the highest TPR whose FPR does not exceed the target; tied scores are kept together.",
  "evaluated_at": "2026-09-24T16:26:21+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wm_test/kgw_student_dolly15k_test.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_1_5b_dolly15k_test.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-09-24T16:29:05+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.752630
- Best F1：0.697436（z 阈值 -0.8687219087128831，TPR 0.952000，FPR 0.778000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.010000 | 0.144000 | 0.249567 | 3.3807363888764597 |
  | 5% | 0.050000 | 0.372000 | 0.523207 | 2.06418738616856 |
  | 10% | 0.098000 | 0.462000 | 0.592308 | 1.5782189036217624 |

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.7526300000000007,
  "best_f1": {
    "threshold": -0.8687219087128831,
    "fpr": 0.778,
    "tpr": 0.952,
    "precision": 0.5502890173410404,
    "f1": 0.6974358974358974,
    "tp": 476,
    "fp": 389,
    "tn": 111,
    "fn": 24
  },
  "tpr_at_fpr": {
    "1%": {
      "threshold": 3.3807363888764597,
      "fpr": 0.01,
      "tpr": 0.144,
      "precision": 0.935064935064935,
      "f1": 0.24956672443674174,
      "tp": 72,
      "fp": 5,
      "tn": 495,
      "fn": 428,
      "target_fpr": 0.01
    },
    "5%": {
      "threshold": 2.06418738616856,
      "fpr": 0.05,
      "tpr": 0.372,
      "precision": 0.8815165876777251,
      "f1": 0.5232067510548524,
      "tp": 186,
      "fp": 25,
      "tn": 475,
      "fn": 314,
      "target_fpr": 0.05
    },
    "10%": {
      "threshold": 1.5782189036217624,
      "fpr": 0.098,
      "tpr": 0.462,
      "precision": 0.825,
      "f1": 0.5923076923076923,
      "tp": 231,
      "fp": 49,
      "tn": 451,
      "fn": 269,
      "target_fpr": 0.1
    }
  },
  "note": "For each target FPR, select the empirical ROC point with the highest TPR whose FPR does not exceed the target; tied scores are kept together.",
  "evaluated_at": "2026-09-24T16:29:05+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wm_test/kgw_student_dolly15k_test.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_1_5b_dolly15k_test.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-09-28T11:42:10+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.610306
- Best F1：0.683631（z 阈值 -3.0641293851417064，TPR 0.994000，FPR 0.914000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.000000 | 0.000000 | 0.000000 | None |
  | 5% | 0.050000 | 0.024000 | 0.044693 | 3.491486243775878 |
  | 10% | 0.100000 | 0.140000 | 0.225806 | 2.140113683916483 |

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.6103059999999995,
  "best_f1": {
    "threshold": -3.0641293851417064,
    "fpr": 0.914,
    "tpr": 0.994,
    "precision": 0.5209643605870021,
    "f1": 0.6836313617606603,
    "tp": 497,
    "fp": 457,
    "tn": 43,
    "fn": 3
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
      "threshold": 3.491486243775878,
      "fpr": 0.05,
      "tpr": 0.024,
      "precision": 0.32432432432432434,
      "f1": 0.04469273743016759,
      "tp": 12,
      "fp": 25,
      "tn": 475,
      "fn": 488,
      "target_fpr": 0.05
    },
    "10%": {
      "threshold": 2.140113683916483,
      "fpr": 0.1,
      "tpr": 0.14,
      "precision": 0.5833333333333334,
      "f1": 0.22580645161290325,
      "tp": 70,
      "fp": 50,
      "tn": 450,
      "fn": 430,
      "target_fpr": 0.1
    }
  },
  "note": "For each target FPR, select the empirical ROC point with the highest TPR whose FPR does not exceed the target; tied scores are kept together.",
  "evaluated_at": "2026-09-28T11:42:10+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wm_test/kgw_gad_qwen2_5_0_5b_dolly15k_test.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-09-28T11:52:08+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.670048
- Best F1：0.688732（z 阈值 -1.7320508075688774，TPR 0.978000，FPR 0.862000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.000000 | 0.000000 | 0.000000 | None |
  | 5% | 0.050000 | 0.062000 | 0.111511 | 3.4935111939202663 |
  | 10% | 0.100000 | 0.256000 | 0.377581 | 2.1393634026872776 |

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.6700479999999993,
  "best_f1": {
    "threshold": -1.7320508075688774,
    "fpr": 0.862,
    "tpr": 0.978,
    "precision": 0.5315217391304348,
    "f1": 0.6887323943661973,
    "tp": 489,
    "fp": 431,
    "tn": 69,
    "fn": 11
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
      "threshold": 3.4935111939202663,
      "fpr": 0.05,
      "tpr": 0.062,
      "precision": 0.5535714285714286,
      "f1": 0.11151079136690646,
      "tp": 31,
      "fp": 25,
      "tn": 475,
      "fn": 469,
      "target_fpr": 0.05
    },
    "10%": {
      "threshold": 2.1393634026872776,
      "fpr": 0.1,
      "tpr": 0.256,
      "precision": 0.7191011235955056,
      "f1": 0.3775811209439528,
      "tp": 128,
      "fp": 50,
      "tn": 450,
      "fn": 372,
      "target_fpr": 0.1
    }
  },
  "note": "For each target FPR, select the empirical ROC point with the highest TPR whose FPR does not exceed the target; tied scores are kept together.",
  "evaluated_at": "2026-09-28T11:52:08+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wm_test/kgw_warmup_qwen2_5_0_5b_dolly15k_test.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-09-28T20:54:51+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.897014
- Best F1：0.836181（z 阈值 1.543033499620919，TPR 0.832000，FPR 0.158000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.010000 | 0.144000 | 0.249567 | 20.669129072660834 |
  | 5% | 0.050000 | 0.622000 | 0.744019 | 3.3606722016672235 |
  | 10% | 0.100000 | 0.782000 | 0.831031 | 2.060488785479727 |

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.8970139999999984,
  "best_f1": {
    "threshold": 1.543033499620919,
    "fpr": 0.158,
    "tpr": 0.832,
    "precision": 0.8404040404040404,
    "f1": 0.836180904522613,
    "tp": 416,
    "fp": 79,
    "tn": 421,
    "fn": 84
  },
  "tpr_at_fpr": {
    "1%": {
      "threshold": 20.669129072660834,
      "fpr": 0.01,
      "tpr": 0.144,
      "precision": 0.935064935064935,
      "f1": 0.24956672443674174,
      "tp": 72,
      "fp": 5,
      "tn": 495,
      "fn": 428,
      "target_fpr": 0.01
    },
    "5%": {
      "threshold": 3.3606722016672235,
      "fpr": 0.05,
      "tpr": 0.622,
      "precision": 0.9255952380952381,
      "f1": 0.7440191387559809,
      "tp": 311,
      "fp": 25,
      "tn": 475,
      "fn": 189,
      "target_fpr": 0.05
    },
    "10%": {
      "threshold": 2.060488785479727,
      "fpr": 0.1,
      "tpr": 0.782,
      "precision": 0.8866213151927438,
      "f1": 0.8310308182784272,
      "tp": 391,
      "fp": 50,
      "tn": 450,
      "fn": 109,
      "target_fpr": 0.1
    }
  },
  "note": "For each target FPR, select the empirical ROC point with the highest TPR whose FPR does not exceed the target; tied scores are kept together.",
  "evaluated_at": "2026-09-28T20:54:51+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_0.5b_kgw_test_kgw_scores.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_0.5b_clean_test_kgw_scores.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-09-29T11:00:20+08:00

- 样本数：seqkd clean 500，clean 500
- AUROC：0.483640
- Best F1：0.676671（z 阈值 -5.656854249492381，TPR 0.992000，FPR 0.940000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.000000 | 0.000000 | 0.000000 | None |
  | 5% | 0.050000 | 0.012000 | 0.022599 | 3.5925925925925926 |
  | 10% | 0.094000 | 0.056000 | 0.097391 | 2.2517050070105746 |

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.48363999999999974,
  "best_f1": {
    "threshold": -5.656854249492381,
    "fpr": 0.94,
    "tpr": 0.992,
    "precision": 0.5134575569358178,
    "f1": 0.6766712141882676,
    "tp": 496,
    "fp": 470,
    "tn": 30,
    "fn": 4
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
      "threshold": 3.5925925925925926,
      "fpr": 0.05,
      "tpr": 0.012,
      "precision": 0.1935483870967742,
      "f1": 0.02259887005649717,
      "tp": 6,
      "fp": 25,
      "tn": 475,
      "fn": 494,
      "target_fpr": 0.05
    },
    "10%": {
      "threshold": 2.2517050070105746,
      "fpr": 0.094,
      "tpr": 0.056,
      "precision": 0.37333333333333335,
      "f1": 0.09739130434782609,
      "tp": 28,
      "fp": 47,
      "tn": 453,
      "fn": 472,
      "target_fpr": 0.1
    }
  },
  "note": "For each target FPR, select the empirical ROC point with the highest TPR whose FPR does not exceed the target; tied scores are kept together.",
  "evaluated_at": "2026-09-29T11:00:20+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wm_test/kgw_seqKD_full_qwen2_5_0_5b_dolly15k_test.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-09-29T15:41:21+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.723184
- Best F1：0.698579（z 阈值 -0.8553372034476997，TPR 0.934000，FPR 0.740000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.000000 | 0.000000 | 0.000000 | None |
  | 5% | 0.050000 | 0.132000 | 0.223350 | 3.4839079607387857 |
  | 10% | 0.096000 | 0.370000 | 0.504775 | 2.151004918040496 |

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.7231839999999994,
  "best_f1": {
    "threshold": -0.8553372034476997,
    "fpr": 0.74,
    "tpr": 0.934,
    "precision": 0.5579450418160096,
    "f1": 0.6985789080029918,
    "tp": 467,
    "fp": 370,
    "tn": 130,
    "fn": 33
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
      "threshold": 3.4839079607387857,
      "fpr": 0.05,
      "tpr": 0.132,
      "precision": 0.7252747252747253,
      "f1": 0.2233502538071066,
      "tp": 66,
      "fp": 25,
      "tn": 475,
      "fn": 434,
      "target_fpr": 0.05
    },
    "10%": {
      "threshold": 2.151004918040496,
      "fpr": 0.096,
      "tpr": 0.37,
      "precision": 0.7939914163090128,
      "f1": 0.504774897680764,
      "tp": 185,
      "fp": 48,
      "tn": 452,
      "fn": 315,
      "target_fpr": 0.1
    }
  },
  "note": "For each target FPR, select the empirical ROC point with the highest TPR whose FPR does not exceed the target; tied scores are kept together.",
  "evaluated_at": "2026-09-29T15:41:21+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wm_test/kgw_seqKD_full_kgwdata_qwen2_5_0_5b_dolly15k_test.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-09-29T17:30:23+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.633170
- Best F1：0.686342（z 阈值 -3.0323921743156137，TPR 1.000000，FPR 0.914000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.000000 | 0.000000 | 0.000000 | None |
  | 5% | 0.050000 | 0.028000 | 0.051948 | 3.4856723621962065 |
  | 10% | 0.096000 | 0.164000 | 0.260317 | 2.1437688030314894 |

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.63317,
  "best_f1": {
    "threshold": -3.0323921743156137,
    "fpr": 0.914,
    "tpr": 1.0,
    "precision": 0.522466039707419,
    "f1": 0.6863417982155113,
    "tp": 500,
    "fp": 457,
    "tn": 43,
    "fn": 0
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
      "threshold": 3.4856723621962065,
      "fpr": 0.05,
      "tpr": 0.028,
      "precision": 0.358974358974359,
      "f1": 0.051948051948051945,
      "tp": 14,
      "fp": 25,
      "tn": 475,
      "fn": 486,
      "target_fpr": 0.05
    },
    "10%": {
      "threshold": 2.1437688030314894,
      "fpr": 0.096,
      "tpr": 0.164,
      "precision": 0.6307692307692307,
      "f1": 0.2603174603174603,
      "tp": 82,
      "fp": 48,
      "tn": 452,
      "fn": 418,
      "target_fpr": 0.1
    }
  },
  "note": "For each target FPR, select the empirical ROC point with the highest TPR whose FPR does not exceed the target; tied scores are kept together.",
  "evaluated_at": "2026-09-29T17:30:23+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wm_test/kgw_gad1500_qwen2_5_0_5b_dolly15k_test.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-10-02T19:42:11+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.633170
- Best F1：0.686342（z 阈值 -3.0323921743156137，TPR 1.000000，FPR 0.914000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.000000 | 0.000000 | 0.000000 | None |
  | 5% | 0.050000 | 0.028000 | 0.051948 | 3.4856723621962065 |
  | 10% | 0.096000 | 0.164000 | 0.260317 | 2.1437688030314894 |

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.63317,
  "best_f1": {
    "threshold": -3.0323921743156137,
    "fpr": 0.914,
    "tpr": 1.0,
    "precision": 0.522466039707419,
    "f1": 0.6863417982155113,
    "tp": 500,
    "fp": 457,
    "tn": 43,
    "fn": 0
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
      "threshold": 3.4856723621962065,
      "fpr": 0.05,
      "tpr": 0.028,
      "precision": 0.358974358974359,
      "f1": 0.051948051948051945,
      "tp": 14,
      "fp": 25,
      "tn": 475,
      "fn": 486,
      "target_fpr": 0.05
    },
    "10%": {
      "threshold": 2.1437688030314894,
      "fpr": 0.096,
      "tpr": 0.164,
      "precision": 0.6307692307692307,
      "f1": 0.2603174603174603,
      "tp": 82,
      "fp": 48,
      "tn": 452,
      "fn": 418,
      "target_fpr": 0.1
    }
  },
  "note": "For each target FPR, select the empirical ROC point with the highest TPR whose FPR does not exceed the target; tied scores are kept together.",
  "evaluated_at": "2026-10-02T19:42:11+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wm_test/kgw_gad1500_qwen2_5_0_5b_dolly15k_test.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-10-02T19:43:09+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.750026
- Best F1：0.714667（z 阈值 0.19245008972987526，TPR 0.804000，FPR 0.446000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.000000 | 0.000000 | 0.000000 | None |
  | 5% | 0.050000 | 0.214000 | 0.338608 | 3.5075379218297824 |
  | 10% | 0.096000 | 0.430000 | 0.563565 | 2.1442250696755893 |

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.7500260000000002,
  "best_f1": {
    "threshold": 0.19245008972987526,
    "fpr": 0.446,
    "tpr": 0.804,
    "precision": 0.6432,
    "f1": 0.7146666666666667,
    "tp": 402,
    "fp": 223,
    "tn": 277,
    "fn": 98
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
      "threshold": 3.5075379218297824,
      "fpr": 0.05,
      "tpr": 0.214,
      "precision": 0.8106060606060606,
      "f1": 0.3386075949367089,
      "tp": 107,
      "fp": 25,
      "tn": 475,
      "fn": 393,
      "target_fpr": 0.05
    },
    "10%": {
      "threshold": 2.1442250696755893,
      "fpr": 0.096,
      "tpr": 0.43,
      "precision": 0.8174904942965779,
      "f1": 0.5635648754914809,
      "tp": 215,
      "fp": 48,
      "tn": 452,
      "fn": 285,
      "target_fpr": 0.1
    }
  },
  "note": "For each target FPR, select the empirical ROC point with the highest TPR whose FPR does not exceed the target; tied scores are kept together.",
  "evaluated_at": "2026-10-02T19:43:09+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wm_test/kgw_seqkd_epoch2_qwen2_5_0_5b_dolly15k_test.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-10-03T11:43:20+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.706396
- Best F1：0.695324（z 阈值 -0.8040724087286836，TPR 0.922000，FPR 0.730000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.000000 | 0.000000 | 0.000000 | None |
  | 5% | 0.050000 | 0.100000 | 0.173913 | 3.538151850686813 |
  | 10% | 0.100000 | 0.308000 | 0.437500 | 2.1333333333333333 |

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.7063959999999987,
  "best_f1": {
    "threshold": -0.8040724087286836,
    "fpr": 0.73,
    "tpr": 0.922,
    "precision": 0.5581113801452785,
    "f1": 0.6953242835595778,
    "tp": 461,
    "fp": 365,
    "tn": 135,
    "fn": 39
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
      "threshold": 3.538151850686813,
      "fpr": 0.05,
      "tpr": 0.1,
      "precision": 0.6666666666666666,
      "f1": 0.1739130434782609,
      "tp": 50,
      "fp": 25,
      "tn": 475,
      "fn": 450,
      "target_fpr": 0.05
    },
    "10%": {
      "threshold": 2.1333333333333333,
      "fpr": 0.1,
      "tpr": 0.308,
      "precision": 0.7549019607843137,
      "f1": 0.43749999999999994,
      "tp": 154,
      "fp": 50,
      "tn": 450,
      "fn": 346,
      "target_fpr": 0.1
    }
  },
  "note": "For each target FPR, select the empirical ROC point with the highest TPR whose FPR does not exceed the target; tied scores are kept together.",
  "evaluated_at": "2026-10-03T11:43:20+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wm_test/kgw_seqkd_epoch2_new_3626_qwen2_5_0_5b_dolly15k_test.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-10-03T11:57:43+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.689026
- Best F1：0.695518（z 阈值 -0.6255432421712243，TPR 0.900000，FPR 0.688000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.000000 | 0.002000 | 0.003992 | 30.405591591021548 |
  | 5% | 0.050000 | 0.092000 | 0.161121 | 3.5018951496390947 |
  | 10% | 0.100000 | 0.282000 | 0.408104 | 2.135453393887794 |

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.6890259999999994,
  "best_f1": {
    "threshold": -0.6255432421712243,
    "fpr": 0.688,
    "tpr": 0.9,
    "precision": 0.5667506297229219,
    "f1": 0.695517774343122,
    "tp": 450,
    "fp": 344,
    "tn": 156,
    "fn": 50
  },
  "tpr_at_fpr": {
    "1%": {
      "threshold": 30.405591591021548,
      "fpr": 0.0,
      "tpr": 0.002,
      "precision": 1.0,
      "f1": 0.003992015968063872,
      "tp": 1,
      "fp": 0,
      "tn": 500,
      "fn": 499,
      "target_fpr": 0.01
    },
    "5%": {
      "threshold": 3.5018951496390947,
      "fpr": 0.05,
      "tpr": 0.092,
      "precision": 0.647887323943662,
      "f1": 0.16112084063047286,
      "tp": 46,
      "fp": 25,
      "tn": 475,
      "fn": 454,
      "target_fpr": 0.05
    },
    "10%": {
      "threshold": 2.135453393887794,
      "fpr": 0.1,
      "tpr": 0.282,
      "precision": 0.7382198952879581,
      "f1": 0.4081041968162084,
      "tp": 141,
      "fp": 50,
      "tn": 450,
      "fn": 359,
      "target_fpr": 0.1
    }
  },
  "note": "For each target FPR, select the empirical ROC point with the highest TPR whose FPR does not exceed the target; tied scores are kept together.",
  "evaluated_at": "2026-10-03T11:57:43+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wm_test/kgw_seqkd_epoch2_new_2000_qwen2_5_0_5b_dolly15k_test.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-10-04T13:06:34+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.731504
- Best F1：0.700809（z 阈值 0.19331116825676478，TPR 0.780000，FPR 0.446000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.000000 | 0.002000 | 0.003992 | 61.87184335382291 |
  | 5% | 0.050000 | 0.152000 | 0.252912 | 3.4955442375314663 |
  | 10% | 0.100000 | 0.372000 | 0.505435 | 2.1343747458109497 |

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.7315039999999994,
  "best_f1": {
    "threshold": 0.19331116825676478,
    "fpr": 0.446,
    "tpr": 0.78,
    "precision": 0.636215334420881,
    "f1": 0.7008086253369272,
    "tp": 390,
    "fp": 223,
    "tn": 277,
    "fn": 110
  },
  "tpr_at_fpr": {
    "1%": {
      "threshold": 61.87184335382291,
      "fpr": 0.0,
      "tpr": 0.002,
      "precision": 1.0,
      "f1": 0.003992015968063872,
      "tp": 1,
      "fp": 0,
      "tn": 500,
      "fn": 499,
      "target_fpr": 0.01
    },
    "5%": {
      "threshold": 3.4955442375314663,
      "fpr": 0.05,
      "tpr": 0.152,
      "precision": 0.7524752475247525,
      "f1": 0.2529118136439268,
      "tp": 76,
      "fp": 25,
      "tn": 475,
      "fn": 424,
      "target_fpr": 0.05
    },
    "10%": {
      "threshold": 2.1343747458109497,
      "fpr": 0.1,
      "tpr": 0.372,
      "precision": 0.788135593220339,
      "f1": 0.5054347826086957,
      "tp": 186,
      "fp": 50,
      "tn": 450,
      "fn": 314,
      "target_fpr": 0.1
    }
  },
  "note": "For each target FPR, select the empirical ROC point with the highest TPR whose FPR does not exceed the target; tied scores are kept together.",
  "evaluated_at": "2026-10-04T13:06:34+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wm_test/kgw_seqkd_epoch5_8000_qwen2_5_0_5b_dolly15k_test.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-10-04T13:43:07+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.713944
- Best F1：0.698198（z 阈值 -0.8164965809277261，TPR 0.930000，FPR 0.734000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.000000 | 0.000000 | 0.000000 | None |
  | 5% | 0.050000 | 0.100000 | 0.173913 | 3.532237606526573 |
  | 10% | 0.100000 | 0.304000 | 0.433048 | 2.1393634026872776 |

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.7139439999999992,
  "best_f1": {
    "threshold": -0.8164965809277261,
    "fpr": 0.734,
    "tpr": 0.93,
    "precision": 0.5588942307692307,
    "f1": 0.6981981981981982,
    "tp": 465,
    "fp": 367,
    "tn": 133,
    "fn": 35
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
      "threshold": 3.532237606526573,
      "fpr": 0.05,
      "tpr": 0.1,
      "precision": 0.6666666666666666,
      "f1": 0.1739130434782609,
      "tp": 50,
      "fp": 25,
      "tn": 475,
      "fn": 450,
      "target_fpr": 0.05
    },
    "10%": {
      "threshold": 2.1393634026872776,
      "fpr": 0.1,
      "tpr": 0.304,
      "precision": 0.7524752475247525,
      "f1": 0.433048433048433,
      "tp": 152,
      "fp": 50,
      "tn": 450,
      "fn": 348,
      "target_fpr": 0.1
    }
  },
  "note": "For each target FPR, select the empirical ROC point with the highest TPR whose FPR does not exceed the target; tied scores are kept together.",
  "evaluated_at": "2026-10-04T13:43:07+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wm_test/kgw_seqkd_epoch5_5500_qwen2_5_0_5b_dolly15k_test.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-10-05T11:50:43+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.600458
- Best F1：0.682995（z 阈值 -2.0303030303030303，TPR 0.976000，FPR 0.882000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.000000 | 0.000000 | 0.000000 | None |
  | 5% | 0.050000 | 0.026000 | 0.048327 | 3.5555555555555554 |
  | 10% | 0.100000 | 0.132000 | 0.214286 | 2.141239281438989 |

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
  "evaluated_at": "2026-10-05T11:50:43+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_cleangad_gad_qwen2_5_0_5b_dolly15k_test.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-10-05T12:12:14+08:00

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
  "evaluated_at": "2026-10-05T12:12:14+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_cleangad_gad_qwen2_5_0_5b_dolly15k_test.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-10-05T12:17:58+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.662250
- Best F1：0.685593（z 阈值 -1.585187847802434，TPR 0.966000，FPR 0.852000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.000000 | 0.000000 | 0.000000 | None |
  | 5% | 0.050000 | 0.052000 | 0.094374 | 3.4944624201204117 |
  | 10% | 0.096000 | 0.232000 | 0.349398 | 2.1602468994692865 |

两种逐条文本 p-value 统计（单侧正态近似；不是 AUROC 的显著性检验）：

去重规则：相同的 `(previous_token_id, token_id)` 只计一次；不修改回答文本。

| 数据 | 检测方式 | 有效样本 | p 均值 | p 中位数 | p≤0.01 | p≤0.05 | p≤0.10 |
|---|---|---:|---:|---:|---:|---:|---:|
| kgw | 原始 | 500/500 | 0.296924 | 0.167857 | 89 (17.80%) | 170 (34.00%) | 216 (43.20%) |
| kgw | token 对去重 | 500/500 | 0.329181 | 0.244359 | 35 (7.00%) | 85 (17.00%) | 134 (26.80%) |
| clean | 原始 | 500/500 | 0.489848 | 0.473107 | 42 (8.40%) | 71 (14.20%) | 102 (20.40%) |
| clean | token 对去重 | 500/500 | 0.493376 | 0.5 | 7 (1.40%) | 29 (5.80%) | 61 (12.20%) |

KGW 的小 p 占比是该理论阈值下的检出率，clean 的小 p 占比是实测误报率。p≤0.05 不保证实际 FPR=5%；去重可改善重复带来的失真，但不保证完全校准。空回答不做显著性检验，p=null，并排除在有效样本统计之外。

逐条 p-value：`/shared/wwx/EasyGAD/wm_test/kgwwarmup_cleangad_warmup_qwen2_5_0_5b_dolly15k_test.p_values.jsonl`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test.p_values.jsonl`

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.6622499999999996,
  "best_f1": {
    "threshold": -1.585187847802434,
    "fpr": 0.852,
    "tpr": 0.966,
    "precision": 0.5313531353135313,
    "f1": 0.6855926188786373,
    "tp": 483,
    "fp": 426,
    "tn": 74,
    "fn": 17
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
      "threshold": 3.4944624201204117,
      "fpr": 0.05,
      "tpr": 0.052,
      "precision": 0.5098039215686274,
      "f1": 0.09437386569872958,
      "tp": 26,
      "fp": 25,
      "tn": 475,
      "fn": 474,
      "target_fpr": 0.05
    },
    "10%": {
      "threshold": 2.1602468994692865,
      "fpr": 0.096,
      "tpr": 0.232,
      "precision": 0.7073170731707317,
      "f1": 0.3493975903614458,
      "tp": 116,
      "fp": 48,
      "tn": 452,
      "fn": 384,
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
        "mean": 0.29692448570776825,
        "median": 0.16785694155618253,
        "min": 9.061085262198103e-26,
        "max": 1.0,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 89,
            "fraction": 0.178
          },
          "5%": {
            "alpha": 0.05,
            "count": 170,
            "fraction": 0.34
          },
          "10%": {
            "alpha": 0.1,
            "count": 216,
            "fraction": 0.432
          }
        }
      },
      "deduplicated": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.32918121832493313,
        "median": 0.244358884932058,
        "min": 5.258177701681559e-05,
        "max": 0.9867799654880297,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 35,
            "fraction": 0.07
          },
          "5%": {
            "alpha": 0.05,
            "count": 85,
            "fraction": 0.17
          },
          "10%": {
            "alpha": 0.1,
            "count": 134,
            "fraction": 0.268
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
    "kgw": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_cleangad_warmup_qwen2_5_0_5b_dolly15k_test.p_values.jsonl",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test.p_values.jsonl"
  },
  "evaluated_at": "2026-10-05T12:17:58+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_cleangad_warmup_qwen2_5_0_5b_dolly15k_test.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-10-05T12:26:15+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.522538
- Best F1：0.681349（z 阈值 -3.159890134225771，TPR 0.990000，FPR 0.916000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.000000 | 0.002000 | 0.003992 | 42.83888582688501 |
  | 5% | 0.050000 | 0.014000 | 0.026316 | 3.491189739487307 |
  | 10% | 0.096000 | 0.056000 | 0.097222 | 2.17219856411465 |

两种逐条文本 p-value 统计（单侧正态近似；不是 AUROC 的显著性检验）：

去重规则：相同的 `(previous_token_id, token_id)` 只计一次；不修改回答文本。

| 数据 | 检测方式 | 有效样本 | p 均值 | p 中位数 | p≤0.01 | p≤0.05 | p≤0.10 |
|---|---|---:|---:|---:|---:|---:|---:|
| kgw | 原始 | 500/500 | 0.46215 | 0.455296 | 21 (4.20%) | 59 (11.80%) | 96 (19.20%) |
| kgw | token 对去重 | 500/500 | 0.482545 | 0.47931 | 3 (0.60%) | 23 (4.60%) | 59 (11.80%) |
| clean | 原始 | 500/500 | 0.489848 | 0.473107 | 42 (8.40%) | 71 (14.20%) | 102 (20.40%) |
| clean | token 对去重 | 500/500 | 0.493376 | 0.5 | 7 (1.40%) | 29 (5.80%) | 61 (12.20%) |

KGW 的小 p 占比是该理论阈值下的检出率，clean 的小 p 占比是实测误报率。p≤0.05 不保证实际 FPR=5%；去重可改善重复带来的失真，但不保证完全校准。空回答不做显著性检验，p=null，并排除在有效样本统计之外。

逐条 p-value：`/shared/wwx/EasyGAD/wm_test/cleanwarmup_kgwgad_gad_qwen2_5_0_5b_dolly15k_test.p_values.jsonl`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test.p_values.jsonl`

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.5225379999999996,
  "best_f1": {
    "threshold": -3.159890134225771,
    "fpr": 0.916,
    "tpr": 0.99,
    "precision": 0.5194123819517313,
    "f1": 0.6813489332415691,
    "tp": 495,
    "fp": 458,
    "tn": 42,
    "fn": 5
  },
  "tpr_at_fpr": {
    "1%": {
      "threshold": 42.83888582688501,
      "fpr": 0.0,
      "tpr": 0.002,
      "precision": 1.0,
      "f1": 0.003992015968063872,
      "tp": 1,
      "fp": 0,
      "tn": 500,
      "fn": 499,
      "target_fpr": 0.01
    },
    "5%": {
      "threshold": 3.491189739487307,
      "fpr": 0.05,
      "tpr": 0.014,
      "precision": 0.21875,
      "f1": 0.02631578947368421,
      "tp": 7,
      "fp": 25,
      "tn": 475,
      "fn": 493,
      "target_fpr": 0.05
    },
    "10%": {
      "threshold": 2.17219856411465,
      "fpr": 0.096,
      "tpr": 0.056,
      "precision": 0.3684210526315789,
      "f1": 0.09722222222222222,
      "tp": 28,
      "fp": 48,
      "tn": 452,
      "fn": 472,
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
        "mean": 0.4621502486409507,
        "median": 0.4552964624992169,
        "min": 0.0,
        "max": 1.0,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 21,
            "fraction": 0.042
          },
          "5%": {
            "alpha": 0.05,
            "count": 59,
            "fraction": 0.118
          },
          "10%": {
            "alpha": 0.1,
            "count": 96,
            "fraction": 0.192
          }
        }
      },
      "deduplicated": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.4825448785378064,
        "median": 0.4793102763030042,
        "min": 0.0008739357725210371,
        "max": 0.9987892664257371,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 3,
            "fraction": 0.006
          },
          "5%": {
            "alpha": 0.05,
            "count": 23,
            "fraction": 0.046
          },
          "10%": {
            "alpha": 0.1,
            "count": 59,
            "fraction": 0.118
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
    "kgw": "/shared/wwx/EasyGAD/wm_test/cleanwarmup_kgwgad_gad_qwen2_5_0_5b_dolly15k_test.p_values.jsonl",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test.p_values.jsonl"
  },
  "evaluated_at": "2026-10-05T12:26:15+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wm_test/cleanwarmup_kgwgad_gad_qwen2_5_0_5b_dolly15k_test.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-10-05T12:33:29+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.484542
- Best F1：0.682256（z 阈值 -3.158168135806891，TPR 0.992000，FPR 0.916000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.000000 | 0.000000 | 0.000000 | None |
  | 5% | 0.048000 | 0.004000 | 0.007605 | 3.8057119844530107 |
  | 10% | 0.096000 | 0.050000 | 0.087260 | 2.1716575062521586 |

两种逐条文本 p-value 统计（单侧正态近似；不是 AUROC 的显著性检验）：

去重规则：相同的 `(previous_token_id, token_id)` 只计一次；不修改回答文本。

| 数据 | 检测方式 | 有效样本 | p 均值 | p 中位数 | p≤0.01 | p≤0.05 | p≤0.10 |
|---|---|---:|---:|---:|---:|---:|---:|
| kgw | 原始 | 500/500 | 0.509044 | 0.5 | 20 (4.00%) | 44 (8.80%) | 68 (13.60%) |
| kgw | token 对去重 | 500/500 | 0.524468 | 0.53617 | 4 (0.80%) | 19 (3.80%) | 37 (7.40%) |
| clean | 原始 | 500/500 | 0.489848 | 0.473107 | 42 (8.40%) | 71 (14.20%) | 102 (20.40%) |
| clean | token 对去重 | 500/500 | 0.493376 | 0.5 | 7 (1.40%) | 29 (5.80%) | 61 (12.20%) |

KGW 的小 p 占比是该理论阈值下的检出率，clean 的小 p 占比是实测误报率。p≤0.05 不保证实际 FPR=5%；去重可改善重复带来的失真，但不保证完全校准。空回答不做显著性检验，p=null，并排除在有效样本统计之外。

逐条 p-value：`/shared/wwx/EasyGAD/wm_test/cleanwarmup_kgwgad_warmup_qwen2_5_0_5b_dolly15k_test.p_values.jsonl`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test.p_values.jsonl`

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.484542,
  "best_f1": {
    "threshold": -3.158168135806891,
    "fpr": 0.916,
    "tpr": 0.992,
    "precision": 0.519916142557652,
    "f1": 0.6822558459422282,
    "tp": 496,
    "fp": 458,
    "tn": 42,
    "fn": 4
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
      "threshold": 3.8057119844530107,
      "fpr": 0.048,
      "tpr": 0.004,
      "precision": 0.07692307692307693,
      "f1": 0.0076045627376425855,
      "tp": 2,
      "fp": 24,
      "tn": 476,
      "fn": 498,
      "target_fpr": 0.05
    },
    "10%": {
      "threshold": 2.1716575062521586,
      "fpr": 0.096,
      "tpr": 0.05,
      "precision": 0.3424657534246575,
      "f1": 0.08726003490401396,
      "tp": 25,
      "fp": 48,
      "tn": 452,
      "fn": 475,
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
        "mean": 0.5090444053340631,
        "median": 0.5,
        "min": 7.840636238644007e-08,
        "max": 1.0,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 20,
            "fraction": 0.04
          },
          "5%": {
            "alpha": 0.05,
            "count": 44,
            "fraction": 0.088
          },
          "10%": {
            "alpha": 0.1,
            "count": 68,
            "fraction": 0.136
          }
        }
      },
      "deduplicated": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.5244682560737947,
        "median": 0.5361704852048943,
        "min": 0.0019462085613893175,
        "max": 0.9977218250984075,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 4,
            "fraction": 0.008
          },
          "5%": {
            "alpha": 0.05,
            "count": 19,
            "fraction": 0.038
          },
          "10%": {
            "alpha": 0.1,
            "count": 37,
            "fraction": 0.074
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
    "kgw": "/shared/wwx/EasyGAD/wm_test/cleanwarmup_kgwgad_warmup_qwen2_5_0_5b_dolly15k_test.p_values.jsonl",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test.p_values.jsonl"
  },
  "evaluated_at": "2026-10-05T12:33:29+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wm_test/cleanwarmup_kgwgad_warmup_qwen2_5_0_5b_dolly15k_test.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-10-06T11:23:54+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.487712
- Best F1：0.679374（z 阈值 -5.295444082550467，TPR 0.998000，FPR 0.940000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.000000 | 0.000000 | 0.000000 | None |
  | 5% | 0.050000 | 0.008000 | 0.015123 | 3.6187343222787294 |
  | 10% | 0.096000 | 0.056000 | 0.097222 | 2.1844063737486574 |

两种逐条文本 p-value 统计（单侧正态近似；不是 AUROC 的显著性检验）：

去重规则：相同的 `(previous_token_id, token_id)` 只计一次；不修改回答文本。

| 数据 | 检测方式 | 有效样本 | p 均值 | p 中位数 | p≤0.01 | p≤0.05 | p≤0.10 |
|---|---|---:|---:|---:|---:|---:|---:|
| kgw | 原始 | 500/500 | 0.505966 | 0.521893 | 23 (4.60%) | 52 (10.40%) | 77 (15.40%) |
| kgw | token 对去重 | 500/500 | 0.508728 | 0.512854 | 6 (1.20%) | 32 (6.40%) | 53 (10.60%) |
| clean | 原始 | 500/500 | 0.489848 | 0.473107 | 42 (8.40%) | 71 (14.20%) | 102 (20.40%) |
| clean | token 对去重 | 500/500 | 0.493376 | 0.5 | 7 (1.40%) | 29 (5.80%) | 61 (12.20%) |

KGW 的小 p 占比是该理论阈值下的检出率，clean 的小 p 占比是实测误报率。p≤0.05 不保证实际 FPR=5%；去重可改善重复带来的失真，但不保证完全校准。空回答不做显著性检验，p=null，并排除在有效样本统计之外。

逐条 p-value：`/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_qwen2_5_0_5b_dolly15k_test.p_values.jsonl`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test.p_values.jsonl`

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.487712,
  "best_f1": {
    "threshold": -5.295444082550467,
    "fpr": 0.94,
    "tpr": 0.998,
    "precision": 0.5149638802889577,
    "f1": 0.6793737236215113,
    "tp": 499,
    "fp": 470,
    "tn": 30,
    "fn": 1
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
      "threshold": 3.6187343222787294,
      "fpr": 0.05,
      "tpr": 0.008,
      "precision": 0.13793103448275862,
      "f1": 0.015122873345935728,
      "tp": 4,
      "fp": 25,
      "tn": 475,
      "fn": 496,
      "target_fpr": 0.05
    },
    "10%": {
      "threshold": 2.1844063737486574,
      "fpr": 0.096,
      "tpr": 0.056,
      "precision": 0.3684210526315789,
      "f1": 0.09722222222222222,
      "tp": 28,
      "fp": 48,
      "tn": 452,
      "fn": 472,
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
        "mean": 0.5059663726303677,
        "median": 0.5218933569278486,
        "min": 3.1462726017640533e-17,
        "max": 1.0,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 23,
            "fraction": 0.046
          },
          "5%": {
            "alpha": 0.05,
            "count": 52,
            "fraction": 0.104
          },
          "10%": {
            "alpha": 0.1,
            "count": 77,
            "fraction": 0.154
          }
        }
      },
      "deduplicated": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.5087281027065359,
        "median": 0.5128542587341163,
        "min": 0.00038705035184787105,
        "max": 0.9987882431028179,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 6,
            "fraction": 0.012
          },
          "5%": {
            "alpha": 0.05,
            "count": 32,
            "fraction": 0.064
          },
          "10%": {
            "alpha": 0.1,
            "count": 53,
            "fraction": 0.106
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
    "kgw": "/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_qwen2_5_0_5b_dolly15k_test.p_values.jsonl",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test.p_values.jsonl"
  },
  "evaluated_at": "2026-10-06T11:23:54+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_qwen2_5_0_5b_dolly15k_test.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-10-06T11:57:00+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.487700
- Best F1：0.680441（z 阈值 -3.158168135806891，TPR 0.988000，FPR 0.916000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.000000 | 0.000000 | 0.000000 | None |
  | 5% | 0.048000 | 0.004000 | 0.007605 | 3.8057119844530107 |
  | 10% | 0.096000 | 0.048000 | 0.083916 | 2.1442250696755893 |

两种逐条文本 p-value 统计（单侧正态近似；不是 AUROC 的显著性检验）：

去重规则：相同的 `(previous_token_id, token_id)` 只计一次；不修改回答文本。

| 数据 | 检测方式 | 有效样本 | p 均值 | p 中位数 | p≤0.01 | p≤0.05 | p≤0.10 |
|---|---|---:|---:|---:|---:|---:|---:|
| kgw | 原始 | 500/500 | 0.504572 | 0.520982 | 17 (3.40%) | 44 (8.80%) | 76 (15.20%) |
| kgw | token 对去重 | 500/500 | 0.534169 | 0.54334 | 5 (1.00%) | 13 (2.60%) | 34 (6.80%) |
| clean | 原始 | 500/500 | 0.489848 | 0.473107 | 42 (8.40%) | 71 (14.20%) | 102 (20.40%) |
| clean | token 对去重 | 500/500 | 0.493376 | 0.5 | 7 (1.40%) | 29 (5.80%) | 61 (12.20%) |

KGW 的小 p 占比是该理论阈值下的检出率，clean 的小 p 占比是实测误报率。p≤0.05 不保证实际 FPR=5%；去重可改善重复带来的失真，但不保证完全校准。空回答不做显著性检验，p=null，并排除在有效样本统计之外。

逐条 p-value：`/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_warmup_qwen2_5_0_5b_dolly15k_test.p_values.jsonl`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test.p_values.jsonl`

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.48769999999999986,
  "best_f1": {
    "threshold": -3.158168135806891,
    "fpr": 0.916,
    "tpr": 0.988,
    "precision": 0.5189075630252101,
    "f1": 0.6804407713498623,
    "tp": 494,
    "fp": 458,
    "tn": 42,
    "fn": 6
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
      "threshold": 3.8057119844530107,
      "fpr": 0.048,
      "tpr": 0.004,
      "precision": 0.07692307692307693,
      "f1": 0.0076045627376425855,
      "tp": 2,
      "fp": 24,
      "tn": 476,
      "fn": 498,
      "target_fpr": 0.05
    },
    "10%": {
      "threshold": 2.1442250696755893,
      "fpr": 0.096,
      "tpr": 0.048,
      "precision": 0.3333333333333333,
      "f1": 0.08391608391608392,
      "tp": 24,
      "fp": 48,
      "tn": 452,
      "fn": 476,
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
        "mean": 0.504571865763331,
        "median": 0.5209818624841773,
        "min": 9.273268396098596e-15,
        "max": 0.9999999972882996,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 17,
            "fraction": 0.034
          },
          "5%": {
            "alpha": 0.05,
            "count": 44,
            "fraction": 0.088
          },
          "10%": {
            "alpha": 0.1,
            "count": 76,
            "fraction": 0.152
          }
        }
      },
      "deduplicated": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.5341690425677306,
        "median": 0.543340262242735,
        "min": 0.0019462085613893175,
        "max": 0.9977673710638368,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 5,
            "fraction": 0.01
          },
          "5%": {
            "alpha": 0.05,
            "count": 13,
            "fraction": 0.026
          },
          "10%": {
            "alpha": 0.1,
            "count": 34,
            "fraction": 0.068
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
    "kgw": "/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_warmup_qwen2_5_0_5b_dolly15k_test.p_values.jsonl",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test.p_values.jsonl"
  },
  "evaluated_at": "2026-10-06T11:57:00+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_warmup_qwen2_5_0_5b_dolly15k_test.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-10-08T16:08:38+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.705720
- Best F1：0.695324（z 阈值 -0.8006407690254357，TPR 0.922000，FPR 0.730000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.000000 | 0.000000 | 0.000000 | None |
  | 5% | 0.050000 | 0.078000 | 0.138298 | 3.4935111939202663 |
  | 10% | 0.098000 | 0.296000 | 0.424677 | 2.141965214767366 |

两种逐条文本 p-value 统计（单侧正态近似；不是 AUROC 的显著性检验）：

去重规则：相同的 `(previous_token_id, token_id)` 只计一次；不修改回答文本。

| 数据 | 检测方式 | 有效样本 | p 均值 | p 中位数 | p≤0.01 | p≤0.05 | p≤0.10 |
|---|---|---:|---:|---:|---:|---:|---:|
| kgw | 原始 | 500/500 | 0.247444 | 0.0940527 | 128 (25.60%) | 209 (41.80%) | 253 (50.60%) |
| kgw | token 对去重 | 500/500 | 0.278221 | 0.18136 | 62 (12.40%) | 126 (25.20%) | 187 (37.40%) |
| clean | 原始 | 500/500 | 0.489848 | 0.473107 | 42 (8.40%) | 71 (14.20%) | 102 (20.40%) |
| clean | token 对去重 | 500/500 | 0.493376 | 0.5 | 7 (1.40%) | 29 (5.80%) | 61 (12.20%) |

KGW 的小 p 占比是该理论阈值下的检出率，clean 的小 p 占比是实测误报率。p≤0.05 不保证实际 FPR=5%；去重可改善重复带来的失真，但不保证完全校准。空回答不做显著性检验，p=null，并排除在有效样本统计之外。

逐条 p-value：`/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_warmup2_qwen2_5_0_5b_dolly15k_test.p_values.jsonl`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test.p_values.jsonl`

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.7057199999999991,
  "best_f1": {
    "threshold": -0.8006407690254357,
    "fpr": 0.73,
    "tpr": 0.922,
    "precision": 0.5581113801452785,
    "f1": 0.6953242835595778,
    "tp": 461,
    "fp": 365,
    "tn": 135,
    "fn": 39
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
      "threshold": 3.4935111939202663,
      "fpr": 0.05,
      "tpr": 0.078,
      "precision": 0.609375,
      "f1": 0.13829787234042554,
      "tp": 39,
      "fp": 25,
      "tn": 475,
      "fn": 461,
      "target_fpr": 0.05
    },
    "10%": {
      "threshold": 2.141965214767366,
      "fpr": 0.098,
      "tpr": 0.296,
      "precision": 0.751269035532995,
      "f1": 0.42467718794835,
      "tp": 148,
      "fp": 49,
      "tn": 451,
      "fn": 352,
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
        "mean": 0.2474444057426342,
        "median": 0.09405267111077248,
        "min": 6.023614438102209e-51,
        "max": 1.0,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 128,
            "fraction": 0.256
          },
          "5%": {
            "alpha": 0.05,
            "count": 209,
            "fraction": 0.418
          },
          "10%": {
            "alpha": 0.1,
            "count": 253,
            "fraction": 0.506
          }
        }
      },
      "deduplicated": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.2782208381422736,
        "median": 0.18135973148317605,
        "min": 2.852167919054653e-05,
        "max": 0.9826186186888858,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 62,
            "fraction": 0.124
          },
          "5%": {
            "alpha": 0.05,
            "count": 126,
            "fraction": 0.252
          },
          "10%": {
            "alpha": 0.1,
            "count": 187,
            "fraction": 0.374
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
    "kgw": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_warmup2_qwen2_5_0_5b_dolly15k_test.p_values.jsonl",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test.p_values.jsonl"
  },
  "evaluated_at": "2026-10-08T16:08:38+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_warmup2_qwen2_5_0_5b_dolly15k_test.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-10-08T16:58:50+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.705720
- ROUGE-L（同批 500 条原始 Dolly 回答作参考）：0.200507（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 原始 Dolly 参考文件：`/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl`
- Best F1：0.695324（z 阈值 -0.8006407690254357，TPR 0.922000，FPR 0.730000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.000000 | 0.000000 | 0.000000 | None |
  | 5% | 0.050000 | 0.078000 | 0.138298 | 3.4935111939202663 |
  | 10% | 0.098000 | 0.296000 | 0.424677 | 2.141965214767366 |

两种逐条文本 p-value 统计（单侧正态近似；不是 AUROC 的显著性检验）：

去重规则：相同的 `(previous_token_id, token_id)` 只计一次；不修改回答文本。

| 数据 | 检测方式 | 有效样本 | p 均值 | p 中位数 | p≤0.01 | p≤0.05 | p≤0.10 |
|---|---|---:|---:|---:|---:|---:|---:|
| kgw | 原始 | 500/500 | 0.247444 | 0.0940527 | 128 (25.60%) | 209 (41.80%) | 253 (50.60%) |
| kgw | token 对去重 | 500/500 | 0.278221 | 0.18136 | 62 (12.40%) | 126 (25.20%) | 187 (37.40%) |
| clean | 原始 | 500/500 | 0.489848 | 0.473107 | 42 (8.40%) | 71 (14.20%) | 102 (20.40%) |
| clean | token 对去重 | 500/500 | 0.493376 | 0.5 | 7 (1.40%) | 29 (5.80%) | 61 (12.20%) |

KGW 的小 p 占比是该理论阈值下的检出率，clean 的小 p 占比是实测误报率。p≤0.05 不保证实际 FPR=5%；去重可改善重复带来的失真，但不保证完全校准。空回答不做显著性检验，p=null，并排除在有效样本统计之外。

逐条 p-value：`/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_warmup2_qwen2_5_0_5b_dolly15k_test.p_values.jsonl`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test.p_values.jsonl`

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.7057199999999991,
  "best_f1": {
    "threshold": -0.8006407690254357,
    "fpr": 0.73,
    "tpr": 0.922,
    "precision": 0.5581113801452785,
    "f1": 0.6953242835595778,
    "tp": 461,
    "fp": 365,
    "tn": 135,
    "fn": 39
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
      "threshold": 3.4935111939202663,
      "fpr": 0.05,
      "tpr": 0.078,
      "precision": 0.609375,
      "f1": 0.13829787234042554,
      "tp": 39,
      "fp": 25,
      "tn": 475,
      "fn": 461,
      "target_fpr": 0.05
    },
    "10%": {
      "threshold": 2.141965214767366,
      "fpr": 0.098,
      "tpr": 0.296,
      "precision": 0.751269035532995,
      "f1": 0.42467718794835,
      "tp": 148,
      "fp": 49,
      "tn": 451,
      "fn": 352,
      "target_fpr": 0.1
    }
  },
  "note": "For each target FPR, select the empirical ROC point with the highest TPR whose FPR does not exceed the target; tied scores are kept together.",
  "rouge_l_dolly": {
    "mean": 0.20050686994466815,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_warmup2_qwen2_5_0_5b_dolly15k_test.jsonl",
    "reference_file": "/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl",
    "reference_source": "databricks/databricks-dolly-15k:response",
    "metric": "rougeL",
    "measure": "fmeasure",
    "use_stemmer": true,
    "aggregation": "unweighted mean of per-sample ROUGE-L F1"
  },
  "p_values": {
    "kgw": {
      "raw": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.2474444057426342,
        "median": 0.09405267111077248,
        "min": 6.023614438102209e-51,
        "max": 1.0,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 128,
            "fraction": 0.256
          },
          "5%": {
            "alpha": 0.05,
            "count": 209,
            "fraction": 0.418
          },
          "10%": {
            "alpha": 0.1,
            "count": 253,
            "fraction": 0.506
          }
        }
      },
      "deduplicated": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.2782208381422736,
        "median": 0.18135973148317605,
        "min": 2.852167919054653e-05,
        "max": 0.9826186186888858,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 62,
            "fraction": 0.124
          },
          "5%": {
            "alpha": 0.05,
            "count": 126,
            "fraction": 0.252
          },
          "10%": {
            "alpha": 0.1,
            "count": 187,
            "fraction": 0.374
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
    "kgw": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_warmup2_qwen2_5_0_5b_dolly15k_test.p_values.jsonl",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test.p_values.jsonl"
  },
  "evaluated_at": "2026-10-08T16:58:50+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_warmup2_qwen2_5_0_5b_dolly15k_test.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-10-08T17:07:32+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.705720
- ROUGE-L（同批 500 条原始 Dolly 回答作参考）：0.200507（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 原始 Dolly 参考文件：`/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl`
- ROUGE-L（同批 500 条 14B clean 教师回答作参考）：0.311308（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 14B clean 教师参考文件：`/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_clean_test.parquet`
- Best F1：0.695324（z 阈值 -0.8006407690254357，TPR 0.922000，FPR 0.730000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.000000 | 0.000000 | 0.000000 | None |
  | 5% | 0.050000 | 0.078000 | 0.138298 | 3.4935111939202663 |
  | 10% | 0.098000 | 0.296000 | 0.424677 | 2.141965214767366 |

两种逐条文本 p-value 统计（单侧正态近似；不是 AUROC 的显著性检验）：

去重规则：相同的 `(previous_token_id, token_id)` 只计一次；不修改回答文本。

| 数据 | 检测方式 | 有效样本 | p 均值 | p 中位数 | p≤0.01 | p≤0.05 | p≤0.10 |
|---|---|---:|---:|---:|---:|---:|---:|
| kgw | 原始 | 500/500 | 0.247444 | 0.0940527 | 128 (25.60%) | 209 (41.80%) | 253 (50.60%) |
| kgw | token 对去重 | 500/500 | 0.278221 | 0.18136 | 62 (12.40%) | 126 (25.20%) | 187 (37.40%) |
| clean | 原始 | 500/500 | 0.489848 | 0.473107 | 42 (8.40%) | 71 (14.20%) | 102 (20.40%) |
| clean | token 对去重 | 500/500 | 0.493376 | 0.5 | 7 (1.40%) | 29 (5.80%) | 61 (12.20%) |

KGW 的小 p 占比是该理论阈值下的检出率，clean 的小 p 占比是实测误报率。p≤0.05 不保证实际 FPR=5%；去重可改善重复带来的失真，但不保证完全校准。空回答不做显著性检验，p=null，并排除在有效样本统计之外。

逐条 p-value：`/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_warmup2_qwen2_5_0_5b_dolly15k_test.p_values.jsonl`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test.p_values.jsonl`

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.7057199999999991,
  "best_f1": {
    "threshold": -0.8006407690254357,
    "fpr": 0.73,
    "tpr": 0.922,
    "precision": 0.5581113801452785,
    "f1": 0.6953242835595778,
    "tp": 461,
    "fp": 365,
    "tn": 135,
    "fn": 39
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
      "threshold": 3.4935111939202663,
      "fpr": 0.05,
      "tpr": 0.078,
      "precision": 0.609375,
      "f1": 0.13829787234042554,
      "tp": 39,
      "fp": 25,
      "tn": 475,
      "fn": 461,
      "target_fpr": 0.05
    },
    "10%": {
      "threshold": 2.141965214767366,
      "fpr": 0.098,
      "tpr": 0.296,
      "precision": 0.751269035532995,
      "f1": 0.42467718794835,
      "tp": 148,
      "fp": 49,
      "tn": 451,
      "fn": 352,
      "target_fpr": 0.1
    }
  },
  "note": "For each target FPR, select the empirical ROC point with the highest TPR whose FPR does not exceed the target; tied scores are kept together.",
  "rouge_l_dolly": {
    "mean": 0.20050686994466815,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_warmup2_qwen2_5_0_5b_dolly15k_test.jsonl",
    "reference_file": "/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl",
    "reference_source": "databricks/databricks-dolly-15k:response",
    "metric": "rougeL",
    "measure": "fmeasure",
    "use_stemmer": true,
    "aggregation": "unweighted mean of per-sample ROUGE-L F1"
  },
  "rouge_l_teacher_clean": {
    "mean": 0.31130826270416995,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_warmup2_qwen2_5_0_5b_dolly15k_test.jsonl",
    "reference_file": "/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_clean_test.parquet",
    "reference_source": "Qwen2.5-14B clean teacher responses",
    "metric": "rougeL",
    "measure": "fmeasure",
    "use_stemmer": true,
    "aggregation": "unweighted mean of per-sample ROUGE-L F1"
  },
  "p_values": {
    "kgw": {
      "raw": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.2474444057426342,
        "median": 0.09405267111077248,
        "min": 6.023614438102209e-51,
        "max": 1.0,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 128,
            "fraction": 0.256
          },
          "5%": {
            "alpha": 0.05,
            "count": 209,
            "fraction": 0.418
          },
          "10%": {
            "alpha": 0.1,
            "count": 253,
            "fraction": 0.506
          }
        }
      },
      "deduplicated": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.2782208381422736,
        "median": 0.18135973148317605,
        "min": 2.852167919054653e-05,
        "max": 0.9826186186888858,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 62,
            "fraction": 0.124
          },
          "5%": {
            "alpha": 0.05,
            "count": 126,
            "fraction": 0.252
          },
          "10%": {
            "alpha": 0.1,
            "count": 187,
            "fraction": 0.374
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
    "kgw": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_warmup2_qwen2_5_0_5b_dolly15k_test.p_values.jsonl",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test.p_values.jsonl"
  },
  "evaluated_at": "2026-10-08T17:07:32+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_warmup2_qwen2_5_0_5b_dolly15k_test.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-10-10T17:16:54+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.652642
- ROUGE-L（同批 500 条原始 Dolly 回答作参考）：0.017157（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 原始 Dolly 参考文件：`/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl`
- ROUGE-L（同批 500 条 14B clean 教师回答作参考）：0.036049（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 14B clean 教师参考文件：`/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_clean_test.parquet`
- Best F1：0.698795（z 阈值 2.365776664185823，TPR 0.580000，FPR 0.080000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.010000 | 0.160000 | 0.273504 | 20.800724479904275 |
  | 5% | 0.050000 | 0.548000 | 0.685857 | 3.476608340833859 |
  | 10% | 0.096000 | 0.588000 | 0.698337 | 2.1802459086585215 |

两种逐条文本 p-value 统计（单侧正态近似；不是 AUROC 的显著性检验）：

去重规则：相同的 `(previous_token_id, token_id)` 只计一次；不修改回答文本。

| 数据 | 检测方式 | 有效样本 | p 均值 | p 中位数 | p≤0.01 | p≤0.05 | p≤0.10 |
|---|---|---:|---:|---:|---:|---:|---:|
| kgw | 原始 | 500/500 | 0.342893 | 3.81239e-07 | 290 (58.00%) | 300 (60.00%) | 304 (60.80%) |
| kgw | token 对去重 | 500/500 | 0.290415 | 0.207108 | 45 (9.00%) | 117 (23.40%) | 170 (34.00%) |
| clean | 原始 | 500/500 | 0.489848 | 0.473107 | 42 (8.40%) | 71 (14.20%) | 102 (20.40%) |
| clean | token 对去重 | 500/500 | 0.493376 | 0.5 | 7 (1.40%) | 29 (5.80%) | 61 (12.20%) |

KGW 的小 p 占比是该理论阈值下的检出率，clean 的小 p 占比是实测误报率。p≤0.05 不保证实际 FPR=5%；去重可改善重复带来的失真，但不保证完全校准。空回答不做显著性检验，p=null，并排除在有效样本统计之外。

逐条 p-value：`/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_gamma0.5_delta3_qwen2_5_0_5b_dolly15k_test.p_values.jsonl`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test.p_values.jsonl`

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.6526420000000005,
  "best_f1": {
    "threshold": 2.365776664185823,
    "fpr": 0.08,
    "tpr": 0.58,
    "precision": 0.8787878787878788,
    "f1": 0.6987951807228915,
    "tp": 290,
    "fp": 40,
    "tn": 460,
    "fn": 210
  },
  "tpr_at_fpr": {
    "1%": {
      "threshold": 20.800724479904275,
      "fpr": 0.01,
      "tpr": 0.16,
      "precision": 0.9411764705882353,
      "f1": 0.27350427350427353,
      "tp": 80,
      "fp": 5,
      "tn": 495,
      "fn": 420,
      "target_fpr": 0.01
    },
    "5%": {
      "threshold": 3.476608340833859,
      "fpr": 0.05,
      "tpr": 0.548,
      "precision": 0.9163879598662207,
      "f1": 0.6858573216520653,
      "tp": 274,
      "fp": 25,
      "tn": 475,
      "fn": 226,
      "target_fpr": 0.05
    },
    "10%": {
      "threshold": 2.1802459086585215,
      "fpr": 0.096,
      "tpr": 0.588,
      "precision": 0.8596491228070176,
      "f1": 0.6983372921615201,
      "tp": 294,
      "fp": 48,
      "tn": 452,
      "fn": 206,
      "target_fpr": 0.1
    }
  },
  "note": "For each target FPR, select the empirical ROC point with the highest TPR whose FPR does not exceed the target; tied scores are kept together.",
  "rouge_l_dolly": {
    "mean": 0.017157403801369882,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_gamma0.5_delta3_qwen2_5_0_5b_dolly15k_test.jsonl",
    "reference_file": "/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl",
    "reference_source": "databricks/databricks-dolly-15k:response",
    "metric": "rougeL",
    "measure": "fmeasure",
    "use_stemmer": true,
    "aggregation": "unweighted mean of per-sample ROUGE-L F1"
  },
  "rouge_l_teacher_clean": {
    "mean": 0.03604859207167721,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_gamma0.5_delta3_qwen2_5_0_5b_dolly15k_test.jsonl",
    "reference_file": "/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_clean_test.parquet",
    "reference_source": "Qwen2.5-14B clean teacher responses",
    "metric": "rougeL",
    "measure": "fmeasure",
    "use_stemmer": true,
    "aggregation": "unweighted mean of per-sample ROUGE-L F1"
  },
  "p_values": {
    "kgw": {
      "raw": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.3428926448825068,
        "median": 3.81238837976517e-07,
        "min": 0.0,
        "max": 1.0,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 290,
            "fraction": 0.58
          },
          "5%": {
            "alpha": 0.05,
            "count": 300,
            "fraction": 0.6
          },
          "10%": {
            "alpha": 0.1,
            "count": 304,
            "fraction": 0.608
          }
        }
      },
      "deduplicated": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.29041465646102604,
        "median": 0.20710808912126255,
        "min": 1.214233736487924e-06,
        "max": 0.9736838487171297,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 45,
            "fraction": 0.09
          },
          "5%": {
            "alpha": 0.05,
            "count": 117,
            "fraction": 0.234
          },
          "10%": {
            "alpha": 0.1,
            "count": 170,
            "fraction": 0.34
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
    "kgw": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_gamma0.5_delta3_qwen2_5_0_5b_dolly15k_test.p_values.jsonl",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test.p_values.jsonl"
  },
  "evaluated_at": "2026-10-10T17:16:54+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_gamma0.5_delta3_qwen2_5_0_5b_dolly15k_test.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-10-10T17:25:59+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.664956
- ROUGE-L（同批 500 条原始 Dolly 回答作参考）：0.198672（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 原始 Dolly 参考文件：`/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl`
- ROUGE-L（同批 500 条 14B clean 教师回答作参考）：0.219981（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 14B clean 教师参考文件：`/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_clean_test.parquet`
- Best F1：0.677794（z 阈值 -1.281025230440697，TPR 0.934000，FPR 0.822000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.010000 | 0.022000 | 0.042636 | 20.859650045003153 |
  | 5% | 0.050000 | 0.126000 | 0.214286 | 3.491189739487307 |
  | 10% | 0.096000 | 0.242000 | 0.361734 | 2.1669453555438456 |

两种逐条文本 p-value 统计（单侧正态近似；不是 AUROC 的显著性检验）：

去重规则：相同的 `(previous_token_id, token_id)` 只计一次；不修改回答文本。

| 数据 | 检测方式 | 有效样本 | p 均值 | p 中位数 | p≤0.01 | p≤0.05 | p≤0.10 |
|---|---|---:|---:|---:|---:|---:|---:|
| kgw | 原始 | 500/500 | 0.29663 | 0.156811 | 110 (22.00%) | 174 (34.80%) | 224 (44.80%) |
| kgw | token 对去重 | 500/500 | 0.31041 | 0.207108 | 39 (7.80%) | 99 (19.80%) | 160 (32.00%) |
| clean | 原始 | 500/500 | 0.489848 | 0.473107 | 42 (8.40%) | 71 (14.20%) | 102 (20.40%) |
| clean | token 对去重 | 500/500 | 0.493376 | 0.5 | 7 (1.40%) | 29 (5.80%) | 61 (12.20%) |

KGW 的小 p 占比是该理论阈值下的检出率，clean 的小 p 占比是实测误报率。p≤0.05 不保证实际 FPR=5%；去重可改善重复带来的失真，但不保证完全校准。空回答不做显著性检验，p=null，并排除在有效样本统计之外。

逐条 p-value：`/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_warmup_gamma0.5_delta3_qwen2_5_0_5b_dolly15k_test.p_values.jsonl`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test.p_values.jsonl`

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.6649560000000003,
  "best_f1": {
    "threshold": -1.281025230440697,
    "fpr": 0.822,
    "tpr": 0.934,
    "precision": 0.5318906605922551,
    "f1": 0.6777939042089985,
    "tp": 467,
    "fp": 411,
    "tn": 89,
    "fn": 33
  },
  "tpr_at_fpr": {
    "1%": {
      "threshold": 20.859650045003153,
      "fpr": 0.01,
      "tpr": 0.022,
      "precision": 0.6875,
      "f1": 0.04263565891472868,
      "tp": 11,
      "fp": 5,
      "tn": 495,
      "fn": 489,
      "target_fpr": 0.01
    },
    "5%": {
      "threshold": 3.491189739487307,
      "fpr": 0.05,
      "tpr": 0.126,
      "precision": 0.7159090909090909,
      "f1": 0.21428571428571427,
      "tp": 63,
      "fp": 25,
      "tn": 475,
      "fn": 437,
      "target_fpr": 0.05
    },
    "10%": {
      "threshold": 2.1669453555438456,
      "fpr": 0.096,
      "tpr": 0.242,
      "precision": 0.7159763313609467,
      "f1": 0.3617339312406577,
      "tp": 121,
      "fp": 48,
      "tn": 452,
      "fn": 379,
      "target_fpr": 0.1
    }
  },
  "note": "For each target FPR, select the empirical ROC point with the highest TPR whose FPR does not exceed the target; tied scores are kept together.",
  "rouge_l_dolly": {
    "mean": 0.19867200550783484,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_warmup_gamma0.5_delta3_qwen2_5_0_5b_dolly15k_test.jsonl",
    "reference_file": "/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl",
    "reference_source": "databricks/databricks-dolly-15k:response",
    "metric": "rougeL",
    "measure": "fmeasure",
    "use_stemmer": true,
    "aggregation": "unweighted mean of per-sample ROUGE-L F1"
  },
  "rouge_l_teacher_clean": {
    "mean": 0.21998142710768617,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_warmup_gamma0.5_delta3_qwen2_5_0_5b_dolly15k_test.jsonl",
    "reference_file": "/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_clean_test.parquet",
    "reference_source": "Qwen2.5-14B clean teacher responses",
    "metric": "rougeL",
    "measure": "fmeasure",
    "use_stemmer": true,
    "aggregation": "unweighted mean of per-sample ROUGE-L F1"
  },
  "p_values": {
    "kgw": {
      "raw": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.2966298257861382,
        "median": 0.15681063727788394,
        "min": 0.0,
        "max": 1.0,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 110,
            "fraction": 0.22
          },
          "5%": {
            "alpha": 0.05,
            "count": 174,
            "fraction": 0.348
          },
          "10%": {
            "alpha": 0.1,
            "count": 224,
            "fraction": 0.448
          }
        }
      },
      "deduplicated": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.3104104697954897,
        "median": 0.20710808912126252,
        "min": 5.723517107695229e-06,
        "max": 0.9961696194324102,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 39,
            "fraction": 0.078
          },
          "5%": {
            "alpha": 0.05,
            "count": 99,
            "fraction": 0.198
          },
          "10%": {
            "alpha": 0.1,
            "count": 160,
            "fraction": 0.32
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
    "kgw": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_warmup_gamma0.5_delta3_qwen2_5_0_5b_dolly15k_test.p_values.jsonl",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test.p_values.jsonl"
  },
  "evaluated_at": "2026-10-10T17:25:59+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_warmup_gamma0.5_delta3_qwen2_5_0_5b_dolly15k_test.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-10-11T22:24:40+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.738816
- 实际检测配置：`{"gamma": 0.5, "hash_key": 15485863, "seeding": "simple_1 (hash_key * previous_token_id)", "delta_by_label": {"kgw": 3.0, "clean": 3.0}}`
- ROUGE-L（同批 500 条原始 Dolly 回答作参考）：0.198672（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 原始 Dolly 参考文件：`/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl`
- ROUGE-L（同批 500 条 14B clean 教师回答作参考）：0.219981（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 14B clean 教师参考文件：`/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_clean_test.parquet`
- Best F1：0.712281（z 阈值 0.0，TPR 0.812000，FPR 0.468000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.010000 | 0.072000 | 0.133087 | 8.582243986207274 |
  | 5% | 0.050000 | 0.262000 | 0.399390 | 2.2283440581246223 |
  | 10% | 0.100000 | 0.384000 | 0.517520 | 1.6840241981634352 |

两种逐条文本 p-value 统计（单侧正态近似；不是 AUROC 的显著性检验）：

去重规则：相同的 `(previous_token_id, token_id)` 只计一次；不修改回答文本。

| 数据 | 检测方式 | 有效样本 | p 均值 | p 中位数 | p≤0.01 | p≤0.05 | p≤0.10 |
|---|---|---:|---:|---:|---:|---:|---:|
| kgw | 原始 | 500/500 | 0.256877 | 0.119477 | 123 (24.60%) | 196 (39.20%) | 240 (48.00%) |
| kgw | token 对去重 | 500/500 | 0.27281 | 0.179887 | 52 (10.40%) | 122 (24.40%) | 184 (36.80%) |
| clean | 原始 | 500/500 | 0.538121 | 0.57157 | 22 (4.40%) | 54 (10.80%) | 73 (14.60%) |
| clean | token 对去重 | 500/500 | 0.537418 | 0.555154 | 5 (1.00%) | 25 (5.00%) | 46 (9.20%) |

KGW 的小 p 占比是该理论阈值下的检出率，clean 的小 p 占比是实测误报率。p≤0.05 不保证实际 FPR=5%；去重可改善重复带来的失真，但不保证完全校准。空回答不做显著性检验，p=null，并排除在有效样本统计之外。

逐条 p-value：`/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_warmup_gamma0.5_delta3_qwen2_5_0_5b_dolly15k_test.p_values.jsonl`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test.rescored_gamma0.5_delta3_key15485863.p_values.jsonl`

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.7388160000000006,
  "best_f1": {
    "threshold": 0.0,
    "fpr": 0.468,
    "tpr": 0.812,
    "precision": 0.634375,
    "f1": 0.712280701754386,
    "tp": 406,
    "fp": 234,
    "tn": 266,
    "fn": 94
  },
  "tpr_at_fpr": {
    "1%": {
      "threshold": 8.582243986207274,
      "fpr": 0.01,
      "tpr": 0.072,
      "precision": 0.8780487804878049,
      "f1": 0.13308687615526804,
      "tp": 36,
      "fp": 5,
      "tn": 495,
      "fn": 464,
      "target_fpr": 0.01
    },
    "5%": {
      "threshold": 2.2283440581246223,
      "fpr": 0.05,
      "tpr": 0.262,
      "precision": 0.8397435897435898,
      "f1": 0.399390243902439,
      "tp": 131,
      "fp": 25,
      "tn": 475,
      "fn": 369,
      "target_fpr": 0.05
    },
    "10%": {
      "threshold": 1.6840241981634352,
      "fpr": 0.1,
      "tpr": 0.384,
      "precision": 0.7933884297520661,
      "f1": 0.5175202156334232,
      "tp": 192,
      "fp": 50,
      "tn": 450,
      "fn": 308,
      "target_fpr": 0.1
    }
  },
  "note": "For each target FPR, select the empirical ROC point with the highest TPR whose FPR does not exceed the target; tied scores are kept together.",
  "detector_config": {
    "gamma": 0.5,
    "hash_key": 15485863,
    "seeding": "simple_1 (hash_key * previous_token_id)",
    "delta_by_label": {
      "kgw": 3.0,
      "clean": 3.0
    }
  },
  "rouge_l_dolly": {
    "mean": 0.19867200550783484,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_warmup_gamma0.5_delta3_qwen2_5_0_5b_dolly15k_test.jsonl",
    "reference_file": "/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl",
    "reference_source": "databricks/databricks-dolly-15k:response",
    "metric": "rougeL",
    "measure": "fmeasure",
    "use_stemmer": true,
    "aggregation": "unweighted mean of per-sample ROUGE-L F1"
  },
  "rouge_l_teacher_clean": {
    "mean": 0.21998142710768617,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_warmup_gamma0.5_delta3_qwen2_5_0_5b_dolly15k_test.jsonl",
    "reference_file": "/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_clean_test.parquet",
    "reference_source": "Qwen2.5-14B clean teacher responses",
    "metric": "rougeL",
    "measure": "fmeasure",
    "use_stemmer": true,
    "aggregation": "unweighted mean of per-sample ROUGE-L F1"
  },
  "p_values": {
    "kgw": {
      "raw": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.2568766941040838,
        "median": 0.11947734263448269,
        "min": 1.5754012273979718e-306,
        "max": 1.0,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 123,
            "fraction": 0.246
          },
          "5%": {
            "alpha": 0.05,
            "count": 196,
            "fraction": 0.392
          },
          "10%": {
            "alpha": 0.1,
            "count": 240,
            "fraction": 0.48
          }
        }
      },
      "deduplicated": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.2728097058772901,
        "median": 0.1798872992415606,
        "min": 3.8613397752717086e-05,
        "max": 0.9941915542829208,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 52,
            "fraction": 0.104
          },
          "5%": {
            "alpha": 0.05,
            "count": 122,
            "fraction": 0.244
          },
          "10%": {
            "alpha": 0.1,
            "count": 184,
            "fraction": 0.368
          }
        }
      }
    },
    "clean": {
      "raw": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.5381206505070838,
        "median": 0.5715704145196637,
        "min": 6.0143e-320,
        "max": 1.0,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 22,
            "fraction": 0.044
          },
          "5%": {
            "alpha": 0.05,
            "count": 54,
            "fraction": 0.108
          },
          "10%": {
            "alpha": 0.1,
            "count": 73,
            "fraction": 0.146
          }
        }
      },
      "deduplicated": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.5374177558749705,
        "median": 0.5551540845432315,
        "min": 0.0006810523357921015,
        "max": 0.9993618427741491,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 5,
            "fraction": 0.01
          },
          "5%": {
            "alpha": 0.05,
            "count": 25,
            "fraction": 0.05
          },
          "10%": {
            "alpha": 0.1,
            "count": 46,
            "fraction": 0.092
          }
        }
      }
    }
  },
  "p_value_method": "one-sided normal survival probability; unique context-token pairs for dedup",
  "per_sample_p_value_files": {
    "kgw": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_warmup_gamma0.5_delta3_qwen2_5_0_5b_dolly15k_test.p_values.jsonl",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test.rescored_gamma0.5_delta3_key15485863.p_values.jsonl"
  },
  "evaluated_at": "2026-10-11T22:24:40+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_warmup_gamma0.5_delta3_qwen2_5_0_5b_dolly15k_test.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test.rescored_gamma0.5_delta3_key15485863.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-10-11T22:39:01+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.736264
- 实际检测配置：`{"gamma": 0.5, "hash_key": 15485863, "seeding": "simple_1 (hash_key * previous_token_id)", "delta_by_label": {"kgw": 3.0, "clean": 3.0}}`
- ROUGE-L（同批 500 条原始 Dolly 回答作参考）：0.017157（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 原始 Dolly 参考文件：`/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl`
- ROUGE-L（同批 500 条 14B clean 教师回答作参考）：0.036049（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 14B clean 教师参考文件：`/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_clean_test.parquet`
- Best F1：0.779343（z 阈值 2.3474276701672125，TPR 0.664000，FPR 0.040000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.010000 | 0.474000 | 0.638814 | 8.420120990817175 |
  | 5% | 0.046000 | 0.666000 | 0.778037 | 2.2963966338592297 |
  | 10% | 0.100000 | 0.680000 | 0.764045 | 1.6840241981634352 |

两种逐条文本 p-value 统计（单侧正态近似；不是 AUROC 的显著性检验）：

去重规则：相同的 `(previous_token_id, token_id)` 只计一次；不修改回答文本。

| 数据 | 检测方式 | 有效样本 | p 均值 | p 中位数 | p≤0.01 | p≤0.05 | p≤0.10 |
|---|---|---:|---:|---:|---:|---:|---:|
| kgw | 原始 | 500/500 | 0.268329 | 2.64323e-14 | 332 (66.40%) | 340 (68.00%) | 346 (69.20%) |
| kgw | token 对去重 | 500/500 | 0.257038 | 0.192044 | 40 (8.00%) | 121 (24.20%) | 169 (33.80%) |
| clean | 原始 | 500/500 | 0.538121 | 0.57157 | 22 (4.40%) | 54 (10.80%) | 73 (14.60%) |
| clean | token 对去重 | 500/500 | 0.537418 | 0.555154 | 5 (1.00%) | 25 (5.00%) | 46 (9.20%) |

KGW 的小 p 占比是该理论阈值下的检出率，clean 的小 p 占比是实测误报率。p≤0.05 不保证实际 FPR=5%；去重可改善重复带来的失真，但不保证完全校准。空回答不做显著性检验，p=null，并排除在有效样本统计之外。

逐条 p-value：`/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta3_qwen2_5_0_5b_dolly15k_test.p_values.jsonl`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test.rescored_gamma0.5_delta3_key15485863.p_values.jsonl`

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.7362639999999994,
  "best_f1": {
    "threshold": 2.3474276701672125,
    "fpr": 0.04,
    "tpr": 0.664,
    "precision": 0.9431818181818182,
    "f1": 0.7793427230046949,
    "tp": 332,
    "fp": 20,
    "tn": 480,
    "fn": 168
  },
  "tpr_at_fpr": {
    "1%": {
      "threshold": 8.420120990817175,
      "fpr": 0.01,
      "tpr": 0.474,
      "precision": 0.9793388429752066,
      "f1": 0.6388140161725067,
      "tp": 237,
      "fp": 5,
      "tn": 495,
      "fn": 263,
      "target_fpr": 0.01
    },
    "5%": {
      "threshold": 2.2963966338592297,
      "fpr": 0.046,
      "tpr": 0.666,
      "precision": 0.9353932584269663,
      "f1": 0.7780373831775702,
      "tp": 333,
      "fp": 23,
      "tn": 477,
      "fn": 167,
      "target_fpr": 0.05
    },
    "10%": {
      "threshold": 1.6840241981634352,
      "fpr": 0.1,
      "tpr": 0.68,
      "precision": 0.8717948717948718,
      "f1": 0.7640449438202247,
      "tp": 340,
      "fp": 50,
      "tn": 450,
      "fn": 160,
      "target_fpr": 0.1
    }
  },
  "note": "For each target FPR, select the empirical ROC point with the highest TPR whose FPR does not exceed the target; tied scores are kept together.",
  "detector_config": {
    "gamma": 0.5,
    "hash_key": 15485863,
    "seeding": "simple_1 (hash_key * previous_token_id)",
    "delta_by_label": {
      "kgw": 3.0,
      "clean": 3.0
    }
  },
  "rouge_l_dolly": {
    "mean": 0.017157403801369882,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta3_qwen2_5_0_5b_dolly15k_test.jsonl",
    "reference_file": "/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl",
    "reference_source": "databricks/databricks-dolly-15k:response",
    "metric": "rougeL",
    "measure": "fmeasure",
    "use_stemmer": true,
    "aggregation": "unweighted mean of per-sample ROUGE-L F1"
  },
  "rouge_l_teacher_clean": {
    "mean": 0.03604859207167721,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta3_qwen2_5_0_5b_dolly15k_test.jsonl",
    "reference_file": "/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_clean_test.parquet",
    "reference_source": "Qwen2.5-14B clean teacher responses",
    "metric": "rougeL",
    "measure": "fmeasure",
    "use_stemmer": true,
    "aggregation": "unweighted mean of per-sample ROUGE-L F1"
  },
  "p_values": {
    "kgw": {
      "raw": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.2683292607151813,
        "median": 2.6432295116347963e-14,
        "min": 0.0,
        "max": 1.0,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 332,
            "fraction": 0.664
          },
          "5%": {
            "alpha": 0.05,
            "count": 340,
            "fraction": 0.68
          },
          "10%": {
            "alpha": 0.1,
            "count": 346,
            "fraction": 0.692
          }
        }
      },
      "deduplicated": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.25703808953358714,
        "median": 0.19204412473692606,
        "min": 0.00021979371943833099,
        "max": 0.9899316242248268,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 40,
            "fraction": 0.08
          },
          "5%": {
            "alpha": 0.05,
            "count": 121,
            "fraction": 0.242
          },
          "10%": {
            "alpha": 0.1,
            "count": 169,
            "fraction": 0.338
          }
        }
      }
    },
    "clean": {
      "raw": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.5381206505070838,
        "median": 0.5715704145196637,
        "min": 6.0143e-320,
        "max": 1.0,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 22,
            "fraction": 0.044
          },
          "5%": {
            "alpha": 0.05,
            "count": 54,
            "fraction": 0.108
          },
          "10%": {
            "alpha": 0.1,
            "count": 73,
            "fraction": 0.146
          }
        }
      },
      "deduplicated": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.5374177558749705,
        "median": 0.5551540845432315,
        "min": 0.0006810523357921015,
        "max": 0.9993618427741491,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 5,
            "fraction": 0.01
          },
          "5%": {
            "alpha": 0.05,
            "count": 25,
            "fraction": 0.05
          },
          "10%": {
            "alpha": 0.1,
            "count": 46,
            "fraction": 0.092
          }
        }
      }
    }
  },
  "p_value_method": "one-sided normal survival probability; unique context-token pairs for dedup",
  "per_sample_p_value_files": {
    "kgw": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta3_qwen2_5_0_5b_dolly15k_test.p_values.jsonl",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test.rescored_gamma0.5_delta3_key15485863.p_values.jsonl"
  },
  "evaluated_at": "2026-10-11T22:39:01+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta3_qwen2_5_0_5b_dolly15k_test.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test.rescored_gamma0.5_delta3_key15485863.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-10-13T10:39:56+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.554078
- 实际检测配置：`{"gamma": 0.25, "hash_key": 15485863, "seeding": "simple_1 (hash_key * previous_token_id)", "delta_by_label": {"kgw": 2.0, "clean": 2.0}}`
- ROUGE-L（同批 500 条原始 Dolly 回答作参考）：0.196329（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 原始 Dolly 参考文件：`/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl`
- ROUGE-L（同批 500 条 14B clean 教师回答作参考）：0.258049（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 14B clean 教师参考文件：`/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_clean_test.parquet`
- Best F1：0.677330（z 阈值 -2.480302145742977，TPR 0.974000，FPR 0.902000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.000000 | 0.002000 | 0.003992 | 27.812866726670872 |
  | 5% | 0.050000 | 0.038000 | 0.069853 | 3.5395790044325226 |
  | 10% | 0.100000 | 0.128000 | 0.208469 | 2.140113683916483 |

两种逐条文本 p-value 统计（单侧正态近似；不是 AUROC 的显著性检验）：

去重规则：相同的 `(previous_token_id, token_id)` 只计一次；不修改回答文本。

| 数据 | 检测方式 | 有效样本 | p 均值 | p 中位数 | p≤0.01 | p≤0.05 | p≤0.10 |
|---|---|---:|---:|---:|---:|---:|---:|
| kgw | 原始 | 500/500 | 0.425456 | 0.383576 | 51 (10.20%) | 89 (17.80%) | 123 (24.60%) |
| kgw | token 对去重 | 500/500 | 0.44751 | 0.440749 | 15 (3.00%) | 47 (9.40%) | 71 (14.20%) |
| clean | 原始 | 500/500 | 0.489848 | 0.473107 | 42 (8.40%) | 71 (14.20%) | 102 (20.40%) |
| clean | token 对去重 | 500/500 | 0.493376 | 0.5 | 7 (1.40%) | 29 (5.80%) | 61 (12.20%) |

KGW 的小 p 占比是该理论阈值下的检出率，clean 的小 p 占比是实测误报率。p≤0.05 不保证实际 FPR=5%；去重可改善重复带来的失真，但不保证完全校准。空回答不做显著性检验，p=null，并排除在有效样本统计之外。

逐条 p-value：`/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_gad_gamma0.25_delta2_qwen2_5_0_5b_dolly15k_test.p_values.jsonl`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test.p_values.jsonl`

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.5540779999999995,
  "best_f1": {
    "threshold": -2.480302145742977,
    "fpr": 0.902,
    "tpr": 0.974,
    "precision": 0.5191897654584222,
    "f1": 0.6773296244784424,
    "tp": 487,
    "fp": 451,
    "tn": 49,
    "fn": 13
  },
  "tpr_at_fpr": {
    "1%": {
      "threshold": 27.812866726670872,
      "fpr": 0.0,
      "tpr": 0.002,
      "precision": 1.0,
      "f1": 0.003992015968063872,
      "tp": 1,
      "fp": 0,
      "tn": 500,
      "fn": 499,
      "target_fpr": 0.01
    },
    "5%": {
      "threshold": 3.5395790044325226,
      "fpr": 0.05,
      "tpr": 0.038,
      "precision": 0.4318181818181818,
      "f1": 0.06985294117647059,
      "tp": 19,
      "fp": 25,
      "tn": 475,
      "fn": 481,
      "target_fpr": 0.05
    },
    "10%": {
      "threshold": 2.140113683916483,
      "fpr": 0.1,
      "tpr": 0.128,
      "precision": 0.5614035087719298,
      "f1": 0.20846905537459282,
      "tp": 64,
      "fp": 50,
      "tn": 450,
      "fn": 436,
      "target_fpr": 0.1
    }
  },
  "note": "For each target FPR, select the empirical ROC point with the highest TPR whose FPR does not exceed the target; tied scores are kept together.",
  "detector_config": {
    "gamma": 0.25,
    "hash_key": 15485863,
    "seeding": "simple_1 (hash_key * previous_token_id)",
    "delta_by_label": {
      "kgw": 2.0,
      "clean": 2.0
    }
  },
  "rouge_l_dolly": {
    "mean": 0.19632861897473253,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_gad_gamma0.25_delta2_qwen2_5_0_5b_dolly15k_test.jsonl",
    "reference_file": "/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl",
    "reference_source": "databricks/databricks-dolly-15k:response",
    "metric": "rougeL",
    "measure": "fmeasure",
    "use_stemmer": true,
    "aggregation": "unweighted mean of per-sample ROUGE-L F1"
  },
  "rouge_l_teacher_clean": {
    "mean": 0.25804914381084126,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_gad_gamma0.25_delta2_qwen2_5_0_5b_dolly15k_test.jsonl",
    "reference_file": "/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_clean_test.parquet",
    "reference_source": "Qwen2.5-14B clean teacher responses",
    "metric": "rougeL",
    "measure": "fmeasure",
    "use_stemmer": true,
    "aggregation": "unweighted mean of per-sample ROUGE-L F1"
  },
  "p_values": {
    "kgw": {
      "raw": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.4254562015241885,
        "median": 0.38357616140589945,
        "min": 1.5158285270292843e-170,
        "max": 1.0,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 51,
            "fraction": 0.102
          },
          "5%": {
            "alpha": 0.05,
            "count": 89,
            "fraction": 0.178
          },
          "10%": {
            "alpha": 0.1,
            "count": 123,
            "fraction": 0.246
          }
        }
      },
      "deduplicated": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.4475097885599825,
        "median": 0.44074872609550675,
        "min": 0.00038705035184787105,
        "max": 0.9933033434805012,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 15,
            "fraction": 0.03
          },
          "5%": {
            "alpha": 0.05,
            "count": 47,
            "fraction": 0.094
          },
          "10%": {
            "alpha": 0.1,
            "count": 71,
            "fraction": 0.142
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
    "kgw": "/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_gad_gamma0.25_delta2_qwen2_5_0_5b_dolly15k_test.p_values.jsonl",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test.p_values.jsonl"
  },
  "evaluated_at": "2026-10-13T10:39:56+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_gad_gamma0.25_delta2_qwen2_5_0_5b_dolly15k_test.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-10-13T10:56:12+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.547194
- 实际检测配置：`{"gamma": 0.25, "hash_key": 15485863, "seeding": "simple_1 (hash_key * previous_token_id)", "delta_by_label": {"kgw": 2.0, "clean": 2.0}}`
- ROUGE-L（同批 500 条原始 Dolly 回答作参考）：0.191711（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 原始 Dolly 参考文件：`/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl`
- ROUGE-L（同批 500 条 14B clean 教师回答作参考）：0.244020（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 14B clean 教师参考文件：`/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_clean_test.parquet`
- Best F1：0.666667（z 阈值 -22.332789172475128，TPR 1.000000，FPR 1.000000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.008000 | 0.010000 | 0.019646 | 21.27212900069531 |
  | 5% | 0.050000 | 0.038000 | 0.069853 | 3.476608340833859 |
  | 10% | 0.096000 | 0.108000 | 0.179402 | 2.1783245945486835 |

两种逐条文本 p-value 统计（单侧正态近似；不是 AUROC 的显著性检验）：

去重规则：相同的 `(previous_token_id, token_id)` 只计一次；不修改回答文本。

| 数据 | 检测方式 | 有效样本 | p 均值 | p 中位数 | p≤0.01 | p≤0.05 | p≤0.10 |
|---|---|---:|---:|---:|---:|---:|---:|
| kgw | 原始 | 499/500 | 0.431213 | 0.392747 | 46 (9.22%) | 84 (16.83%) | 122 (24.45%) |
| kgw | token 对去重 | 499/500 | 0.459589 | 0.431583 | 12 (2.40%) | 33 (6.61%) | 57 (11.42%) |
| clean | 原始 | 500/500 | 0.489848 | 0.473107 | 42 (8.40%) | 71 (14.20%) | 102 (20.40%) |
| clean | token 对去重 | 500/500 | 0.493376 | 0.5 | 7 (1.40%) | 29 (5.80%) | 61 (12.20%) |

KGW 的小 p 占比是该理论阈值下的检出率，clean 的小 p 占比是实测误报率。p≤0.05 不保证实际 FPR=5%；去重可改善重复带来的失真，但不保证完全校准。空回答不做显著性检验，p=null，并排除在有效样本统计之外。

逐条 p-value：`/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_warmup_gamma0.25_delta2_qwen2_5_0_5b_dolly15k_test.p_values.jsonl`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test.p_values.jsonl`

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.5471940000000001,
  "best_f1": {
    "threshold": -22.332789172475128,
    "fpr": 1.0,
    "tpr": 1.0,
    "precision": 0.5,
    "f1": 0.6666666666666666,
    "tp": 500,
    "fp": 500,
    "tn": 0,
    "fn": 0
  },
  "tpr_at_fpr": {
    "1%": {
      "threshold": 21.27212900069531,
      "fpr": 0.008,
      "tpr": 0.01,
      "precision": 0.5555555555555556,
      "f1": 0.019646365422396856,
      "tp": 5,
      "fp": 4,
      "tn": 496,
      "fn": 495,
      "target_fpr": 0.01
    },
    "5%": {
      "threshold": 3.476608340833859,
      "fpr": 0.05,
      "tpr": 0.038,
      "precision": 0.4318181818181818,
      "f1": 0.06985294117647059,
      "tp": 19,
      "fp": 25,
      "tn": 475,
      "fn": 481,
      "target_fpr": 0.05
    },
    "10%": {
      "threshold": 2.1783245945486835,
      "fpr": 0.096,
      "tpr": 0.108,
      "precision": 0.5294117647058824,
      "f1": 0.17940199335548174,
      "tp": 54,
      "fp": 48,
      "tn": 452,
      "fn": 446,
      "target_fpr": 0.1
    }
  },
  "note": "For each target FPR, select the empirical ROC point with the highest TPR whose FPR does not exceed the target; tied scores are kept together.",
  "detector_config": {
    "gamma": 0.25,
    "hash_key": 15485863,
    "seeding": "simple_1 (hash_key * previous_token_id)",
    "delta_by_label": {
      "kgw": 2.0,
      "clean": 2.0
    }
  },
  "rouge_l_dolly": {
    "mean": 0.19171139917277105,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_warmup_gamma0.25_delta2_qwen2_5_0_5b_dolly15k_test.jsonl",
    "reference_file": "/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl",
    "reference_source": "databricks/databricks-dolly-15k:response",
    "metric": "rougeL",
    "measure": "fmeasure",
    "use_stemmer": true,
    "aggregation": "unweighted mean of per-sample ROUGE-L F1"
  },
  "rouge_l_teacher_clean": {
    "mean": 0.2440201727234147,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_warmup_gamma0.25_delta2_qwen2_5_0_5b_dolly15k_test.jsonl",
    "reference_file": "/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_clean_test.parquet",
    "reference_source": "Qwen2.5-14B clean teacher responses",
    "metric": "rougeL",
    "measure": "fmeasure",
    "use_stemmer": true,
    "aggregation": "unweighted mean of per-sample ROUGE-L F1"
  },
  "p_values": {
    "kgw": {
      "raw": {
        "n_total": 500,
        "n_valid": 499,
        "n_invalid": 1,
        "mean": 0.4312126091624406,
        "median": 0.3927473735591771,
        "min": 0.0,
        "max": 1.0,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 46,
            "fraction": 0.09218436873747494
          },
          "5%": {
            "alpha": 0.05,
            "count": 84,
            "fraction": 0.1683366733466934
          },
          "10%": {
            "alpha": 0.1,
            "count": 122,
            "fraction": 0.24448897795591182
          }
        }
      },
      "deduplicated": {
        "n_total": 500,
        "n_valid": 499,
        "n_invalid": 1,
        "mean": 0.45958885818907325,
        "median": 0.4315829590466157,
        "min": 6.746866635113954e-06,
        "max": 0.9998450020239172,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 12,
            "fraction": 0.02404809619238477
          },
          "5%": {
            "alpha": 0.05,
            "count": 33,
            "fraction": 0.06613226452905811
          },
          "10%": {
            "alpha": 0.1,
            "count": 57,
            "fraction": 0.11422845691382766
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
    "kgw": "/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_warmup_gamma0.25_delta2_qwen2_5_0_5b_dolly15k_test.p_values.jsonl",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test.p_values.jsonl"
  },
  "evaluated_at": "2026-10-13T10:56:12+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_warmup_gamma0.25_delta2_qwen2_5_0_5b_dolly15k_test.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```
