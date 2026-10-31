
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

## 评估记录：2026-10-15T11:14:06+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.635794
- 实际检测配置：`{"gamma": 0.5, "hash_key": 15485863, "seeding": "simple_1 (hash_key * previous_token_id)", "delta_by_label": {"kgw": 2.0, "clean": 2.0}}`
- ROUGE-L（同批 500 条原始 Dolly 回答作参考）：0.206096（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 原始 Dolly 参考文件：`/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl`
- ROUGE-L（同批 500 条 14B clean 教师回答作参考）：0.303203（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 14B clean 教师参考文件：`/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_clean_test.parquet`
- Best F1：0.679915（z 阈值 -1.9044331628182154，TPR 0.958000，FPR 0.860000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.000000 | 0.000000 | 0.000000 | None |
  | 5% | 0.048000 | 0.128000 | 0.217687 | 2.2460579065115365 |
  | 10% | 0.100000 | 0.216000 | 0.328267 | 1.6895637160701555 |

两种逐条文本 p-value 统计（单侧正态近似；不是 AUROC 的显著性检验）：

去重规则：相同的 `(previous_token_id, token_id)` 只计一次；不修改回答文本。

| 数据 | 检测方式 | 有效样本 | p 均值 | p 中位数 | p≤0.01 | p≤0.05 | p≤0.10 |
|---|---|---:|---:|---:|---:|---:|---:|
| kgw | 原始 | 500/500 | 0.379972 | 0.279789 | 60 (12.00%) | 114 (22.80%) | 164 (32.80%) |
| kgw | token 对去重 | 500/500 | 0.380593 | 0.32216 | 22 (4.40%) | 63 (12.60%) | 108 (21.60%) |
| clean | 原始 | 500/500 | 0.538121 | 0.57157 | 22 (4.40%) | 54 (10.80%) | 73 (14.60%) |
| clean | token 对去重 | 500/500 | 0.537418 | 0.555154 | 5 (1.00%) | 25 (5.00%) | 46 (9.20%) |

KGW 的小 p 占比是该理论阈值下的检出率，clean 的小 p 占比是实测误报率。p≤0.05 不保证实际 FPR=5%；去重可改善重复带来的失真，但不保证完全校准。空回答不做显著性检验，p=null，并排除在有效样本统计之外。

逐条 p-value：`/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_warmup_gamma0.5_delta2_qwen2_5_0_5b_dolly15k_test.p_values.jsonl`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl`

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.6357940000000003,
  "best_f1": {
    "threshold": -1.9044331628182154,
    "fpr": 0.86,
    "tpr": 0.958,
    "precision": 0.5269526952695269,
    "f1": 0.6799148332150461,
    "tp": 479,
    "fp": 430,
    "tn": 70,
    "fn": 21
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
      "threshold": 2.2460579065115365,
      "fpr": 0.048,
      "tpr": 0.128,
      "precision": 0.7272727272727273,
      "f1": 0.217687074829932,
      "tp": 64,
      "fp": 24,
      "tn": 476,
      "fn": 436,
      "target_fpr": 0.05
    },
    "10%": {
      "threshold": 1.6895637160701555,
      "fpr": 0.1,
      "tpr": 0.216,
      "precision": 0.6835443037974683,
      "f1": 0.3282674772036474,
      "tp": 108,
      "fp": 50,
      "tn": 450,
      "fn": 392,
      "target_fpr": 0.1
    }
  },
  "note": "For each target FPR, select the empirical ROC point with the highest TPR whose FPR does not exceed the target; tied scores are kept together.",
  "detector_config": {
    "gamma": 0.5,
    "hash_key": 15485863,
    "seeding": "simple_1 (hash_key * previous_token_id)",
    "delta_by_label": {
      "kgw": 2.0,
      "clean": 2.0
    }
  },
  "rouge_l_dolly": {
    "mean": 0.2060959350581176,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_warmup_gamma0.5_delta2_qwen2_5_0_5b_dolly15k_test.jsonl",
    "reference_file": "/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl",
    "reference_source": "databricks/databricks-dolly-15k:response",
    "metric": "rougeL",
    "measure": "fmeasure",
    "use_stemmer": true,
    "aggregation": "unweighted mean of per-sample ROUGE-L F1"
  },
  "rouge_l_teacher_clean": {
    "mean": 0.3032032044407931,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_warmup_gamma0.5_delta2_qwen2_5_0_5b_dolly15k_test.jsonl",
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
        "mean": 0.3799718602947059,
        "median": 0.2797888182915552,
        "min": 9.691561294488009e-15,
        "max": 1.0,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 60,
            "fraction": 0.12
          },
          "5%": {
            "alpha": 0.05,
            "count": 114,
            "fraction": 0.228
          },
          "10%": {
            "alpha": 0.1,
            "count": 164,
            "fraction": 0.328
          }
        }
      },
      "deduplicated": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.3805934043195033,
        "median": 0.32215994192734054,
        "min": 0.0004793542787484259,
        "max": 0.9973271615636728,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 22,
            "fraction": 0.044
          },
          "5%": {
            "alpha": 0.05,
            "count": 63,
            "fraction": 0.126
          },
          "10%": {
            "alpha": 0.1,
            "count": 108,
            "fraction": 0.216
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
    "kgw": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_warmup_gamma0.5_delta2_qwen2_5_0_5b_dolly15k_test.p_values.jsonl",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl"
  },
  "evaluated_at": "2026-10-15T11:14:06+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_warmup_gamma0.5_delta2_qwen2_5_0_5b_dolly15k_test.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-10-15T11:21:37+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.575170
- 实际检测配置：`{"gamma": 0.5, "hash_key": 15485863, "seeding": "simple_1 (hash_key * previous_token_id)", "delta_by_label": {"kgw": 2.0, "clean": 2.0}}`
- ROUGE-L（同批 500 条原始 Dolly 回答作参考）：0.214492（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 原始 Dolly 参考文件：`/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl`
- ROUGE-L（同批 500 条 14B clean 教师回答作参考）：0.320875（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 14B clean 教师参考文件：`/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_clean_test.parquet`
- Best F1：0.679426（z 阈值 -3.9584169497668436，TPR 0.994000，FPR 0.932000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.000000 | 0.000000 | 0.000000 | None |
  | 5% | 0.050000 | 0.048000 | 0.087432 | 2.2294816068526147 |
  | 10% | 0.100000 | 0.122000 | 0.199673 | 1.6909936308157578 |

两种逐条文本 p-value 统计（单侧正态近似；不是 AUROC 的显著性检验）：

去重规则：相同的 `(previous_token_id, token_id)` 只计一次；不修改回答文本。

| 数据 | 检测方式 | 有效样本 | p 均值 | p 中位数 | p≤0.01 | p≤0.05 | p≤0.10 |
|---|---|---:|---:|---:|---:|---:|---:|
| kgw | 原始 | 500/500 | 0.45252 | 0.431158 | 20 (4.00%) | 64 (12.80%) | 100 (20.00%) |
| kgw | token 对去重 | 500/500 | 0.434624 | 0.397918 | 9 (1.80%) | 51 (10.20%) | 76 (15.20%) |
| clean | 原始 | 500/500 | 0.538121 | 0.57157 | 22 (4.40%) | 54 (10.80%) | 73 (14.60%) |
| clean | token 对去重 | 500/500 | 0.537418 | 0.555154 | 5 (1.00%) | 25 (5.00%) | 46 (9.20%) |

KGW 的小 p 占比是该理论阈值下的检出率，clean 的小 p 占比是实测误报率。p≤0.05 不保证实际 FPR=5%；去重可改善重复带来的失真，但不保证完全校准。空回答不做显著性检验，p=null，并排除在有效样本统计之外。

逐条 p-value：`/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta2_qwen2_5_0_5b_dolly15k_test.p_values.jsonl`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl`

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.5751699999999997,
  "best_f1": {
    "threshold": -3.9584169497668436,
    "fpr": 0.932,
    "tpr": 0.994,
    "precision": 0.5160955347871236,
    "f1": 0.6794258373205742,
    "tp": 497,
    "fp": 466,
    "tn": 34,
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
      "threshold": 2.2294816068526147,
      "fpr": 0.05,
      "tpr": 0.048,
      "precision": 0.4897959183673469,
      "f1": 0.08743169398907102,
      "tp": 24,
      "fp": 25,
      "tn": 475,
      "fn": 476,
      "target_fpr": 0.05
    },
    "10%": {
      "threshold": 1.6909936308157578,
      "fpr": 0.1,
      "tpr": 0.122,
      "precision": 0.5495495495495496,
      "f1": 0.19967266775777415,
      "tp": 61,
      "fp": 50,
      "tn": 450,
      "fn": 439,
      "target_fpr": 0.1
    }
  },
  "note": "For each target FPR, select the empirical ROC point with the highest TPR whose FPR does not exceed the target; tied scores are kept together.",
  "detector_config": {
    "gamma": 0.5,
    "hash_key": 15485863,
    "seeding": "simple_1 (hash_key * previous_token_id)",
    "delta_by_label": {
      "kgw": 2.0,
      "clean": 2.0
    }
  },
  "rouge_l_dolly": {
    "mean": 0.21449190214028263,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta2_qwen2_5_0_5b_dolly15k_test.jsonl",
    "reference_file": "/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl",
    "reference_source": "databricks/databricks-dolly-15k:response",
    "metric": "rougeL",
    "measure": "fmeasure",
    "use_stemmer": true,
    "aggregation": "unweighted mean of per-sample ROUGE-L F1"
  },
  "rouge_l_teacher_clean": {
    "mean": 0.32087517853541186,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta2_qwen2_5_0_5b_dolly15k_test.jsonl",
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
        "mean": 0.452519525086268,
        "median": 0.43115843880879967,
        "min": 4.73666139662072e-06,
        "max": 1.0,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 20,
            "fraction": 0.04
          },
          "5%": {
            "alpha": 0.05,
            "count": 64,
            "fraction": 0.128
          },
          "10%": {
            "alpha": 0.1,
            "count": 100,
            "fraction": 0.2
          }
        }
      },
      "deduplicated": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.43462442290871683,
        "median": 0.3979178688051665,
        "min": 2.8904972787142577e-05,
        "max": 0.9984630130390078,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 9,
            "fraction": 0.018
          },
          "5%": {
            "alpha": 0.05,
            "count": 51,
            "fraction": 0.102
          },
          "10%": {
            "alpha": 0.1,
            "count": 76,
            "fraction": 0.152
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
    "kgw": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta2_qwen2_5_0_5b_dolly15k_test.p_values.jsonl",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl"
  },
  "evaluated_at": "2026-10-15T11:21:37+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta2_qwen2_5_0_5b_dolly15k_test.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-10-15T11:38:32+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.679584
- 实际检测配置：`{"gamma": 0.5, "hash_key": 15485863, "seeding": "simple_1 (hash_key * previous_token_id)", "delta_by_label": {"kgw": 3.0, "clean": 2.0}}`
- ROUGE-L（同批 500 条原始 Dolly 回答作参考）：0.204170（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 原始 Dolly 参考文件：`/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl`
- ROUGE-L（同批 500 条 14B clean 教师回答作参考）：0.300920（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 14B clean 教师参考文件：`/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_clean_test.parquet`
- Best F1：0.686441（z 阈值 -1.9532533420699492，TPR 0.972000，FPR 0.860000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.000000 | 0.000000 | 0.000000 | None |
  | 5% | 0.048000 | 0.190000 | 0.306947 | 2.2460579065115365 |
  | 10% | 0.100000 | 0.300000 | 0.428571 | 1.7038855027411943 |

两种逐条文本 p-value 统计（单侧正态近似；不是 AUROC 的显著性检验）：

去重规则：相同的 `(previous_token_id, token_id)` 只计一次；不修改回答文本。

| 数据 | 检测方式 | 有效样本 | p 均值 | p 中位数 | p≤0.01 | p≤0.05 | p≤0.10 |
|---|---|---:|---:|---:|---:|---:|---:|
| kgw | 原始 | 500/500 | 0.329666 | 0.219151 | 92 (18.40%) | 153 (30.60%) | 188 (37.60%) |
| kgw | token 对去重 | 500/500 | 0.338577 | 0.294798 | 37 (7.40%) | 97 (19.40%) | 142 (28.40%) |
| clean | 原始 | 500/500 | 0.538121 | 0.57157 | 22 (4.40%) | 54 (10.80%) | 73 (14.60%) |
| clean | token 对去重 | 500/500 | 0.537418 | 0.555154 | 5 (1.00%) | 25 (5.00%) | 46 (9.20%) |

KGW 的小 p 占比是该理论阈值下的检出率，clean 的小 p 占比是实测误报率。p≤0.05 不保证实际 FPR=5%；去重可改善重复带来的失真，但不保证完全校准。空回答不做显著性检验，p=null，并排除在有效样本统计之外。

逐条 p-value：`/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_warmup_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.p_values.jsonl`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl`

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.6795839999999989,
  "best_f1": {
    "threshold": -1.9532533420699492,
    "fpr": 0.86,
    "tpr": 0.972,
    "precision": 0.5305676855895196,
    "f1": 0.6864406779661016,
    "tp": 486,
    "fp": 430,
    "tn": 70,
    "fn": 14
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
      "threshold": 2.2460579065115365,
      "fpr": 0.048,
      "tpr": 0.19,
      "precision": 0.7983193277310925,
      "f1": 0.30694668820678517,
      "tp": 95,
      "fp": 24,
      "tn": 476,
      "fn": 405,
      "target_fpr": 0.05
    },
    "10%": {
      "threshold": 1.7038855027411943,
      "fpr": 0.1,
      "tpr": 0.3,
      "precision": 0.75,
      "f1": 0.4285714285714285,
      "tp": 150,
      "fp": 50,
      "tn": 450,
      "fn": 350,
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
      "clean": 2.0
    }
  },
  "rouge_l_dolly": {
    "mean": 0.20416985319974867,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_warmup_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.jsonl",
    "reference_file": "/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl",
    "reference_source": "databricks/databricks-dolly-15k:response",
    "metric": "rougeL",
    "measure": "fmeasure",
    "use_stemmer": true,
    "aggregation": "unweighted mean of per-sample ROUGE-L F1"
  },
  "rouge_l_teacher_clean": {
    "mean": 0.300919843309813,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_warmup_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.jsonl",
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
        "mean": 0.3296664932281066,
        "median": 0.21915062085091014,
        "min": 5.357780917290389e-13,
        "max": 1.0,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 92,
            "fraction": 0.184
          },
          "5%": {
            "alpha": 0.05,
            "count": 153,
            "fraction": 0.306
          },
          "10%": {
            "alpha": 0.1,
            "count": 188,
            "fraction": 0.376
          }
        }
      },
      "deduplicated": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.3385771887153556,
        "median": 0.29479844477264167,
        "min": 1.3561332466625727e-05,
        "max": 0.9831684817377956,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 37,
            "fraction": 0.074
          },
          "5%": {
            "alpha": 0.05,
            "count": 97,
            "fraction": 0.194
          },
          "10%": {
            "alpha": 0.1,
            "count": 142,
            "fraction": 0.284
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
    "kgw": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_warmup_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.p_values.jsonl",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl"
  },
  "evaluated_at": "2026-10-15T11:38:32+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_warmup_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-10-15T12:01:50+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.647688
- 实际检测配置：`{"gamma": 0.5, "hash_key": 15485863, "seeding": "simple_1 (hash_key * previous_token_id)", "delta_by_label": {"kgw": 3.0, "clean": 2.0}}`
- ROUGE-L（同批 500 条原始 Dolly 回答作参考）：0.198494（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 原始 Dolly 参考文件：`/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl`
- ROUGE-L（同批 500 条 14B clean 教师回答作参考）：0.309174（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 14B clean 教师参考文件：`/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_clean_test.parquet`
- Best F1：0.685011（z 阈值 -1.5460413650478515，TPR 0.946000，FPR 0.816000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.000000 | 0.000000 | 0.000000 | None |
  | 5% | 0.050000 | 0.114000 | 0.195876 | 2.225394561056747 |
  | 10% | 0.100000 | 0.228000 | 0.343373 | 1.6859773678906163 |

两种逐条文本 p-value 统计（单侧正态近似；不是 AUROC 的显著性检验）：

去重规则：相同的 `(previous_token_id, token_id)` 只计一次；不修改回答文本。

| 数据 | 检测方式 | 有效样本 | p 均值 | p 中位数 | p≤0.01 | p≤0.05 | p≤0.10 |
|---|---|---:|---:|---:|---:|---:|---:|
| kgw | 原始 | 500/500 | 0.365777 | 0.238373 | 53 (10.60%) | 119 (23.80%) | 156 (31.20%) |
| kgw | token 对去重 | 500/500 | 0.347472 | 0.270591 | 19 (3.80%) | 80 (16.00%) | 140 (28.00%) |
| clean | 原始 | 500/500 | 0.538121 | 0.57157 | 22 (4.40%) | 54 (10.80%) | 73 (14.60%) |
| clean | token 对去重 | 500/500 | 0.537418 | 0.555154 | 5 (1.00%) | 25 (5.00%) | 46 (9.20%) |

KGW 的小 p 占比是该理论阈值下的检出率，clean 的小 p 占比是实测误报率。p≤0.05 不保证实际 FPR=5%；去重可改善重复带来的失真，但不保证完全校准。空回答不做显著性检验，p=null，并排除在有效样本统计之外。

逐条 p-value：`/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.p_values.jsonl`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl`

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.6476880000000005,
  "best_f1": {
    "threshold": -1.5460413650478515,
    "fpr": 0.816,
    "tpr": 0.946,
    "precision": 0.5368898978433598,
    "f1": 0.6850108616944243,
    "tp": 473,
    "fp": 408,
    "tn": 92,
    "fn": 27
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
      "threshold": 2.225394561056747,
      "fpr": 0.05,
      "tpr": 0.114,
      "precision": 0.6951219512195121,
      "f1": 0.19587628865979384,
      "tp": 57,
      "fp": 25,
      "tn": 475,
      "fn": 443,
      "target_fpr": 0.05
    },
    "10%": {
      "threshold": 1.6859773678906163,
      "fpr": 0.1,
      "tpr": 0.228,
      "precision": 0.6951219512195121,
      "f1": 0.34337349397590367,
      "tp": 114,
      "fp": 50,
      "tn": 450,
      "fn": 386,
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
      "clean": 2.0
    }
  },
  "rouge_l_dolly": {
    "mean": 0.19849387557587408,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.jsonl",
    "reference_file": "/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl",
    "reference_source": "databricks/databricks-dolly-15k:response",
    "metric": "rougeL",
    "measure": "fmeasure",
    "use_stemmer": true,
    "aggregation": "unweighted mean of per-sample ROUGE-L F1"
  },
  "rouge_l_teacher_clean": {
    "mean": 0.3091744425525882,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.jsonl",
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
        "mean": 0.36577704616420137,
        "median": 0.2383728596628124,
        "min": 6.834897526731109e-14,
        "max": 0.9999999683624243,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 53,
            "fraction": 0.106
          },
          "5%": {
            "alpha": 0.05,
            "count": 119,
            "fraction": 0.238
          },
          "10%": {
            "alpha": 0.1,
            "count": 156,
            "fraction": 0.312
          }
        }
      },
      "deduplicated": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.3474721954408633,
        "median": 0.2705911687912894,
        "min": 9.802720950622567e-05,
        "max": 0.9947064313329715,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 19,
            "fraction": 0.038
          },
          "5%": {
            "alpha": 0.05,
            "count": 80,
            "fraction": 0.16
          },
          "10%": {
            "alpha": 0.1,
            "count": 140,
            "fraction": 0.28
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
    "kgw": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.p_values.jsonl",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl"
  },
  "evaluated_at": "2026-10-15T12:01:50+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-10-15T16:05:11+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.546198
- 实际检测配置：`{"gamma": 0.5, "hash_key": 15485863, "seeding": "simple_1 (hash_key * previous_token_id)", "delta_by_label": {"kgw": 2.0, "clean": 2.0}}`
- ROUGE-L（同批 500 条原始 Dolly 回答作参考）：0.203002（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 原始 Dolly 参考文件：`/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl`
- ROUGE-L（同批 500 条 14B clean 教师回答作参考）：0.255151（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 14B clean 教师参考文件：`/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_clean_test.parquet`
- Best F1：0.670337（z 阈值 -3.834824944236852，TPR 0.974000，FPR 0.932000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.010000 | 0.020000 | 0.038835 | 9.593834825900782 |
  | 5% | 0.046000 | 0.076000 | 0.135472 | 2.271099895830676 |
  | 10% | 0.100000 | 0.118000 | 0.193760 | 1.6924558427507104 |

两种逐条文本 p-value 统计（单侧正态近似；不是 AUROC 的显著性检验）：

去重规则：相同的 `(previous_token_id, token_id)` 只计一次；不修改回答文本。

| 数据 | 检测方式 | 有效样本 | p 均值 | p 中位数 | p≤0.01 | p≤0.05 | p≤0.10 |
|---|---|---:|---:|---:|---:|---:|---:|
| kgw | 原始 | 500/500 | 0.486092 | 0.5 | 36 (7.20%) | 62 (12.40%) | 88 (17.60%) |
| kgw | token 对去重 | 500/500 | 0.516226 | 0.5 | 3 (0.60%) | 20 (4.00%) | 42 (8.40%) |
| clean | 原始 | 500/500 | 0.538121 | 0.57157 | 22 (4.40%) | 54 (10.80%) | 73 (14.60%) |
| clean | token 对去重 | 500/500 | 0.537418 | 0.555154 | 5 (1.00%) | 25 (5.00%) | 46 (9.20%) |

KGW 的小 p 占比是该理论阈值下的检出率，clean 的小 p 占比是实测误报率。p≤0.05 不保证实际 FPR=5%；去重可改善重复带来的失真，但不保证完全校准。空回答不做显著性检验，p=null，并排除在有效样本统计之外。

逐条 p-value：`/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_warmup_gamma0.5_delta2_qwen2_5_0_5b_dolly15k_test.p_values.jsonl`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl`

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.5461980000000002,
  "best_f1": {
    "threshold": -3.834824944236852,
    "fpr": 0.932,
    "tpr": 0.974,
    "precision": 0.5110178384050367,
    "f1": 0.6703372333103923,
    "tp": 487,
    "fp": 466,
    "tn": 34,
    "fn": 13
  },
  "tpr_at_fpr": {
    "1%": {
      "threshold": 9.593834825900782,
      "fpr": 0.01,
      "tpr": 0.02,
      "precision": 0.6666666666666666,
      "f1": 0.038834951456310676,
      "tp": 10,
      "fp": 5,
      "tn": 495,
      "fn": 490,
      "target_fpr": 0.01
    },
    "5%": {
      "threshold": 2.271099895830676,
      "fpr": 0.046,
      "tpr": 0.076,
      "precision": 0.6229508196721312,
      "f1": 0.13547237076648844,
      "tp": 38,
      "fp": 23,
      "tn": 477,
      "fn": 462,
      "target_fpr": 0.05
    },
    "10%": {
      "threshold": 1.6924558427507104,
      "fpr": 0.1,
      "tpr": 0.118,
      "precision": 0.5412844036697247,
      "f1": 0.19376026272577995,
      "tp": 59,
      "fp": 50,
      "tn": 450,
      "fn": 441,
      "target_fpr": 0.1
    }
  },
  "note": "For each target FPR, select the empirical ROC point with the highest TPR whose FPR does not exceed the target; tied scores are kept together.",
  "detector_config": {
    "gamma": 0.5,
    "hash_key": 15485863,
    "seeding": "simple_1 (hash_key * previous_token_id)",
    "delta_by_label": {
      "kgw": 2.0,
      "clean": 2.0
    }
  },
  "rouge_l_dolly": {
    "mean": 0.20300235975931522,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_warmup_gamma0.5_delta2_qwen2_5_0_5b_dolly15k_test.jsonl",
    "reference_file": "/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl",
    "reference_source": "databricks/databricks-dolly-15k:response",
    "metric": "rougeL",
    "measure": "fmeasure",
    "use_stemmer": true,
    "aggregation": "unweighted mean of per-sample ROUGE-L F1"
  },
  "rouge_l_teacher_clean": {
    "mean": 0.2551511891699088,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_warmup_gamma0.5_delta2_qwen2_5_0_5b_dolly15k_test.jsonl",
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
        "mean": 0.4860921504689607,
        "median": 0.5,
        "min": 0.0,
        "max": 1.0,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 36,
            "fraction": 0.072
          },
          "5%": {
            "alpha": 0.05,
            "count": 62,
            "fraction": 0.124
          },
          "10%": {
            "alpha": 0.1,
            "count": 88,
            "fraction": 0.176
          }
        }
      },
      "deduplicated": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.5162260304469206,
        "median": 0.5,
        "min": 0.0038164408938961528,
        "max": 0.9990129301439148,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 3,
            "fraction": 0.006
          },
          "5%": {
            "alpha": 0.05,
            "count": 20,
            "fraction": 0.04
          },
          "10%": {
            "alpha": 0.1,
            "count": 42,
            "fraction": 0.084
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
    "kgw": "/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_warmup_gamma0.5_delta2_qwen2_5_0_5b_dolly15k_test.p_values.jsonl",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl"
  },
  "evaluated_at": "2026-10-15T16:05:11+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_warmup_gamma0.5_delta2_qwen2_5_0_5b_dolly15k_test.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-10-15T16:12:14+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.555228
- 实际检测配置：`{"gamma": 0.5, "hash_key": 15485863, "seeding": "simple_1 (hash_key * previous_token_id)", "delta_by_label": {"kgw": 2.0, "clean": 2.0}}`
- ROUGE-L（同批 500 条原始 Dolly 回答作参考）：0.192682（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 原始 Dolly 参考文件：`/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl`
- ROUGE-L（同批 500 条 14B clean 教师回答作参考）：0.266186（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 14B clean 教师参考文件：`/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_clean_test.parquet`
- Best F1：0.673943（z 阈值 -5.154134667106271，TPR 0.988000，FPR 0.944000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.010000 | 0.006000 | 0.011811 | 8.981462390204987 |
  | 5% | 0.046000 | 0.052000 | 0.094718 | 2.2517050070105746 |
  | 10% | 0.100000 | 0.114000 | 0.187809 | 1.6867605906952476 |

两种逐条文本 p-value 统计（单侧正态近似；不是 AUROC 的显著性检验）：

去重规则：相同的 `(previous_token_id, token_id)` 只计一次；不修改回答文本。

| 数据 | 检测方式 | 有效样本 | p 均值 | p 中位数 | p≤0.01 | p≤0.05 | p≤0.10 |
|---|---|---:|---:|---:|---:|---:|---:|
| kgw | 原始 | 500/500 | 0.474719 | 0.457099 | 21 (4.20%) | 59 (11.80%) | 101 (20.20%) |
| kgw | token 对去重 | 500/500 | 0.494142 | 0.470608 | 5 (1.00%) | 31 (6.20%) | 62 (12.40%) |
| clean | 原始 | 500/500 | 0.538121 | 0.57157 | 22 (4.40%) | 54 (10.80%) | 73 (14.60%) |
| clean | token 对去重 | 500/500 | 0.537418 | 0.555154 | 5 (1.00%) | 25 (5.00%) | 46 (9.20%) |

KGW 的小 p 占比是该理论阈值下的检出率，clean 的小 p 占比是实测误报率。p≤0.05 不保证实际 FPR=5%；去重可改善重复带来的失真，但不保证完全校准。空回答不做显著性检验，p=null，并排除在有效样本统计之外。

逐条 p-value：`/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta2_qwen2_5_0_5b_dolly15k_test.p_values.jsonl`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl`

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.5552279999999995,
  "best_f1": {
    "threshold": -5.154134667106271,
    "fpr": 0.944,
    "tpr": 0.988,
    "precision": 0.5113871635610766,
    "f1": 0.6739427012278308,
    "tp": 494,
    "fp": 472,
    "tn": 28,
    "fn": 6
  },
  "tpr_at_fpr": {
    "1%": {
      "threshold": 8.981462390204987,
      "fpr": 0.01,
      "tpr": 0.006,
      "precision": 0.375,
      "f1": 0.011811023622047246,
      "tp": 3,
      "fp": 5,
      "tn": 495,
      "fn": 497,
      "target_fpr": 0.01
    },
    "5%": {
      "threshold": 2.2517050070105746,
      "fpr": 0.046,
      "tpr": 0.052,
      "precision": 0.5306122448979592,
      "f1": 0.09471766848816028,
      "tp": 26,
      "fp": 23,
      "tn": 477,
      "fn": 474,
      "target_fpr": 0.05
    },
    "10%": {
      "threshold": 1.6867605906952476,
      "fpr": 0.1,
      "tpr": 0.114,
      "precision": 0.5327102803738317,
      "f1": 0.18780889621087316,
      "tp": 57,
      "fp": 50,
      "tn": 450,
      "fn": 443,
      "target_fpr": 0.1
    }
  },
  "note": "For each target FPR, select the empirical ROC point with the highest TPR whose FPR does not exceed the target; tied scores are kept together.",
  "detector_config": {
    "gamma": 0.5,
    "hash_key": 15485863,
    "seeding": "simple_1 (hash_key * previous_token_id)",
    "delta_by_label": {
      "kgw": 2.0,
      "clean": 2.0
    }
  },
  "rouge_l_dolly": {
    "mean": 0.19268209024137792,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta2_qwen2_5_0_5b_dolly15k_test.jsonl",
    "reference_file": "/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl",
    "reference_source": "databricks/databricks-dolly-15k:response",
    "metric": "rougeL",
    "measure": "fmeasure",
    "use_stemmer": true,
    "aggregation": "unweighted mean of per-sample ROUGE-L F1"
  },
  "rouge_l_teacher_clean": {
    "mean": 0.2661856003624705,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta2_qwen2_5_0_5b_dolly15k_test.jsonl",
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
        "mean": 0.4747191572248848,
        "median": 0.45709878118725006,
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
            "count": 101,
            "fraction": 0.202
          }
        }
      },
      "deduplicated": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.4941416552299487,
        "median": 0.4706080915381696,
        "min": 0.0008081111075299945,
        "max": 0.9982156857815333,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 5,
            "fraction": 0.01
          },
          "5%": {
            "alpha": 0.05,
            "count": 31,
            "fraction": 0.062
          },
          "10%": {
            "alpha": 0.1,
            "count": 62,
            "fraction": 0.124
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
    "kgw": "/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta2_qwen2_5_0_5b_dolly15k_test.p_values.jsonl",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl"
  },
  "evaluated_at": "2026-10-15T16:12:14+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta2_qwen2_5_0_5b_dolly15k_test.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-10-15T19:57:15+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.641034
- 实际检测配置：`{"gamma": 0.5, "hash_key": 15485863, "seeding": "simple_1 (hash_key * previous_token_id)", "delta_by_label": {"kgw": 3.0, "clean": 2.0}}`
- ROUGE-L（同批 500 条原始 Dolly 回答作参考）：0.212690（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 原始 Dolly 参考文件：`/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl`
- ROUGE-L（同批 500 条 14B clean 教师回答作参考）：0.304432（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 14B clean 教师参考文件：`/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_clean_test.parquet`
- Best F1：0.681663（z 阈值 -4.085966464769322，TPR 1.000000，FPR 0.934000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.000000 | 0.000000 | 0.000000 | None |
  | 5% | 0.050000 | 0.110000 | 0.189655 | 2.225995548013356 |
  | 10% | 0.100000 | 0.196000 | 0.302469 | 1.6867605906952476 |

两种逐条文本 p-value 统计（单侧正态近似；不是 AUROC 的显著性检验）：

去重规则：相同的 `(previous_token_id, token_id)` 只计一次；不修改回答文本。

| 数据 | 检测方式 | 有效样本 | p 均值 | p 中位数 | p≤0.01 | p≤0.05 | p≤0.10 |
|---|---|---:|---:|---:|---:|---:|---:|
| kgw | 原始 | 500/500 | 0.373018 | 0.286903 | 45 (9.00%) | 102 (20.40%) | 143 (28.60%) |
| kgw | token 对去重 | 500/500 | 0.37025 | 0.29268 | 28 (5.60%) | 72 (14.40%) | 117 (23.40%) |
| clean | 原始 | 500/500 | 0.538121 | 0.57157 | 22 (4.40%) | 54 (10.80%) | 73 (14.60%) |
| clean | token 对去重 | 500/500 | 0.537418 | 0.555154 | 5 (1.00%) | 25 (5.00%) | 46 (9.20%) |

KGW 的小 p 占比是该理论阈值下的检出率，clean 的小 p 占比是实测误报率。p≤0.05 不保证实际 FPR=5%；去重可改善重复带来的失真，但不保证完全校准。空回答不做显著性检验，p=null，并排除在有效样本统计之外。

逐条 p-value：`/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.p_values.jsonl`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl`

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.6410340000000009,
  "best_f1": {
    "threshold": -4.085966464769322,
    "fpr": 0.934,
    "tpr": 1.0,
    "precision": 0.5170630816959669,
    "f1": 0.6816632583503749,
    "tp": 500,
    "fp": 467,
    "tn": 33,
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
      "threshold": 2.225995548013356,
      "fpr": 0.05,
      "tpr": 0.11,
      "precision": 0.6875,
      "f1": 0.1896551724137931,
      "tp": 55,
      "fp": 25,
      "tn": 475,
      "fn": 445,
      "target_fpr": 0.05
    },
    "10%": {
      "threshold": 1.6867605906952476,
      "fpr": 0.1,
      "tpr": 0.196,
      "precision": 0.6621621621621622,
      "f1": 0.30246913580246915,
      "tp": 98,
      "fp": 50,
      "tn": 450,
      "fn": 402,
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
      "clean": 2.0
    }
  },
  "rouge_l_dolly": {
    "mean": 0.21269025925218651,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.jsonl",
    "reference_file": "/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl",
    "reference_source": "databricks/databricks-dolly-15k:response",
    "metric": "rougeL",
    "measure": "fmeasure",
    "use_stemmer": true,
    "aggregation": "unweighted mean of per-sample ROUGE-L F1"
  },
  "rouge_l_teacher_clean": {
    "mean": 0.3044319488556256,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.jsonl",
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
        "mean": 0.37301834928378047,
        "median": 0.28690262573002534,
        "min": 6.869952468447251e-09,
        "max": 0.9999780531408222,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 45,
            "fraction": 0.09
          },
          "5%": {
            "alpha": 0.05,
            "count": 102,
            "fraction": 0.204
          },
          "10%": {
            "alpha": 0.1,
            "count": 143,
            "fraction": 0.286
          }
        }
      },
      "deduplicated": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.3702501637134407,
        "median": 0.2926804848339488,
        "min": 7.852614211537582e-05,
        "max": 0.9989889754015482,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 28,
            "fraction": 0.056
          },
          "5%": {
            "alpha": 0.05,
            "count": 72,
            "fraction": 0.144
          },
          "10%": {
            "alpha": 0.1,
            "count": 117,
            "fraction": 0.234
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
    "kgw": "/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.p_values.jsonl",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl"
  },
  "evaluated_at": "2026-10-15T19:57:15+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-10-15T20:08:49+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.680012
- 实际检测配置：`{"gamma": 0.5, "hash_key": 15485863, "seeding": "simple_1 (hash_key * previous_token_id)", "delta_by_label": {"kgw": 3.0, "clean": 2.0}}`
- ROUGE-L（同批 500 条原始 Dolly 回答作参考）：0.199697（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 原始 Dolly 参考文件：`/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl`
- ROUGE-L（同批 500 条 14B clean 教师回答作参考）：0.298178（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 14B clean 教师参考文件：`/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_clean_test.parquet`
- Best F1：0.685757（z 阈值 -1.0834726777719228，TPR 0.910000，FPR 0.744000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.010000 | 0.004000 | 0.007890 | 8.369089954509192 |
  | 5% | 0.050000 | 0.218000 | 0.343849 | 2.223781796726481 |
  | 10% | 0.100000 | 0.310000 | 0.439716 | 1.6818826599284376 |

两种逐条文本 p-value 统计（单侧正态近似；不是 AUROC 的显著性检验）：

去重规则：相同的 `(previous_token_id, token_id)` 只计一次；不修改回答文本。

| 数据 | 检测方式 | 有效样本 | p 均值 | p 中位数 | p≤0.01 | p≤0.05 | p≤0.10 |
|---|---|---:|---:|---:|---:|---:|---:|
| kgw | 原始 | 500/500 | 0.329854 | 0.237216 | 99 (19.80%) | 157 (31.40%) | 183 (36.60%) |
| kgw | token 对去重 | 500/500 | 0.326485 | 0.240835 | 40 (8.00%) | 98 (19.60%) | 148 (29.60%) |
| clean | 原始 | 500/500 | 0.538121 | 0.57157 | 22 (4.40%) | 54 (10.80%) | 73 (14.60%) |
| clean | token 对去重 | 500/500 | 0.537418 | 0.555154 | 5 (1.00%) | 25 (5.00%) | 46 (9.20%) |

KGW 的小 p 占比是该理论阈值下的检出率，clean 的小 p 占比是实测误报率。p≤0.05 不保证实际 FPR=5%；去重可改善重复带来的失真，但不保证完全校准。空回答不做显著性检验，p=null，并排除在有效样本统计之外。

逐条 p-value：`/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_warmup_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.p_values.jsonl`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl`

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.6800119999999998,
  "best_f1": {
    "threshold": -1.0834726777719228,
    "fpr": 0.744,
    "tpr": 0.91,
    "precision": 0.5501813784764208,
    "f1": 0.6857573474001507,
    "tp": 455,
    "fp": 372,
    "tn": 128,
    "fn": 45
  },
  "tpr_at_fpr": {
    "1%": {
      "threshold": 8.369089954509192,
      "fpr": 0.01,
      "tpr": 0.004,
      "precision": 0.2857142857142857,
      "f1": 0.007889546351084811,
      "tp": 2,
      "fp": 5,
      "tn": 495,
      "fn": 498,
      "target_fpr": 0.01
    },
    "5%": {
      "threshold": 2.223781796726481,
      "fpr": 0.05,
      "tpr": 0.218,
      "precision": 0.8134328358208955,
      "f1": 0.3438485804416404,
      "tp": 109,
      "fp": 25,
      "tn": 475,
      "fn": 391,
      "target_fpr": 0.05
    },
    "10%": {
      "threshold": 1.6818826599284376,
      "fpr": 0.1,
      "tpr": 0.31,
      "precision": 0.7560975609756098,
      "f1": 0.43971631205673756,
      "tp": 155,
      "fp": 50,
      "tn": 450,
      "fn": 345,
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
      "clean": 2.0
    }
  },
  "rouge_l_dolly": {
    "mean": 0.19969676240172327,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_warmup_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.jsonl",
    "reference_file": "/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl",
    "reference_source": "databricks/databricks-dolly-15k:response",
    "metric": "rougeL",
    "measure": "fmeasure",
    "use_stemmer": true,
    "aggregation": "unweighted mean of per-sample ROUGE-L F1"
  },
  "rouge_l_teacher_clean": {
    "mean": 0.2981779421838879,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_warmup_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.jsonl",
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
        "mean": 0.32985368204963733,
        "median": 0.237215515326687,
        "min": 1.9456879130293956e-98,
        "max": 1.0,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 99,
            "fraction": 0.198
          },
          "5%": {
            "alpha": 0.05,
            "count": 157,
            "fraction": 0.314
          },
          "10%": {
            "alpha": 0.1,
            "count": 183,
            "fraction": 0.366
          }
        }
      },
      "deduplicated": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.3264851781114101,
        "median": 0.24083499339513048,
        "min": 1.3561332466625727e-05,
        "max": 0.9911469670963167,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 40,
            "fraction": 0.08
          },
          "5%": {
            "alpha": 0.05,
            "count": 98,
            "fraction": 0.196
          },
          "10%": {
            "alpha": 0.1,
            "count": 148,
            "fraction": 0.296
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
    "kgw": "/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_warmup_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.p_values.jsonl",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl"
  },
  "evaluated_at": "2026-10-15T20:08:49+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_warmup_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-10-16T10:32:28+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.546344
- 实际检测配置：`{"gamma": 0.5, "hash_key": 15485863, "seeding": "simple_1 (hash_key * previous_token_id)", "delta_by_label": {"kgw": 3.0, "clean": 2.0}}`
- ROUGE-L（同批 500 条原始 Dolly 回答作参考）：0.195773（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 原始 Dolly 参考文件：`/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl`
- ROUGE-L（同批 500 条 14B clean 教师回答作参考）：0.251185（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 14B clean 教师参考文件：`/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_clean_test.parquet`
- Best F1：0.670300（z 阈值 -6.041186552271796，TPR 0.984000，FPR 0.952000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.010000 | 0.008000 | 0.015717 | 12.655697004379755 |
  | 5% | 0.046000 | 0.052000 | 0.094718 | 2.2616463578083135 |
  | 10% | 0.100000 | 0.110000 | 0.181818 | 1.697056274847714 |

两种逐条文本 p-value 统计（单侧正态近似；不是 AUROC 的显著性检验）：

去重规则：相同的 `(previous_token_id, token_id)` 只计一次；不修改回答文本。

| 数据 | 检测方式 | 有效样本 | p 均值 | p 中位数 | p≤0.01 | p≤0.05 | p≤0.10 |
|---|---|---:|---:|---:|---:|---:|---:|
| kgw | 原始 | 500/500 | 0.484232 | 0.441858 | 24 (4.80%) | 57 (11.40%) | 90 (18.00%) |
| kgw | token 对去重 | 500/500 | 0.503516 | 0.5 | 6 (1.20%) | 23 (4.60%) | 60 (12.00%) |
| clean | 原始 | 500/500 | 0.538121 | 0.57157 | 22 (4.40%) | 54 (10.80%) | 73 (14.60%) |
| clean | token 对去重 | 500/500 | 0.537418 | 0.555154 | 5 (1.00%) | 25 (5.00%) | 46 (9.20%) |

KGW 的小 p 占比是该理论阈值下的检出率，clean 的小 p 占比是实测误报率。p≤0.05 不保证实际 FPR=5%；去重可改善重复带来的失真，但不保证完全校准。空回答不做显著性检验，p=null，并排除在有效样本统计之外。

逐条 p-value：`/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_warmup_gamma0.5_delta3_new1_qwen2_5_0_5b_dolly15k_test.p_values.jsonl`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl`

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.5463439999999997,
  "best_f1": {
    "threshold": -6.041186552271796,
    "fpr": 0.952,
    "tpr": 0.984,
    "precision": 0.5082644628099173,
    "f1": 0.670299727520436,
    "tp": 492,
    "fp": 476,
    "tn": 24,
    "fn": 8
  },
  "tpr_at_fpr": {
    "1%": {
      "threshold": 12.655697004379755,
      "fpr": 0.01,
      "tpr": 0.008,
      "precision": 0.4444444444444444,
      "f1": 0.015717092337917484,
      "tp": 4,
      "fp": 5,
      "tn": 495,
      "fn": 496,
      "target_fpr": 0.01
    },
    "5%": {
      "threshold": 2.2616463578083135,
      "fpr": 0.046,
      "tpr": 0.052,
      "precision": 0.5306122448979592,
      "f1": 0.09471766848816028,
      "tp": 26,
      "fp": 23,
      "tn": 477,
      "fn": 474,
      "target_fpr": 0.05
    },
    "10%": {
      "threshold": 1.697056274847714,
      "fpr": 0.1,
      "tpr": 0.11,
      "precision": 0.5238095238095238,
      "f1": 0.18181818181818182,
      "tp": 55,
      "fp": 50,
      "tn": 450,
      "fn": 445,
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
      "clean": 2.0
    }
  },
  "rouge_l_dolly": {
    "mean": 0.1957726793727063,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_warmup_gamma0.5_delta3_new1_qwen2_5_0_5b_dolly15k_test.jsonl",
    "reference_file": "/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl",
    "reference_source": "databricks/databricks-dolly-15k:response",
    "metric": "rougeL",
    "measure": "fmeasure",
    "use_stemmer": true,
    "aggregation": "unweighted mean of per-sample ROUGE-L F1"
  },
  "rouge_l_teacher_clean": {
    "mean": 0.2511847002824468,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_warmup_gamma0.5_delta3_new1_qwen2_5_0_5b_dolly15k_test.jsonl",
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
        "mean": 0.4842321922560427,
        "median": 0.4418578947135764,
        "min": 5.201255510577453e-268,
        "max": 1.0,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 24,
            "fraction": 0.048
          },
          "5%": {
            "alpha": 0.05,
            "count": 57,
            "fraction": 0.114
          },
          "10%": {
            "alpha": 0.1,
            "count": 90,
            "fraction": 0.18
          }
        }
      },
      "deduplicated": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.5035157893462947,
        "median": 0.5,
        "min": 0.0027372886455343834,
        "max": 0.9999771109119667,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 6,
            "fraction": 0.012
          },
          "5%": {
            "alpha": 0.05,
            "count": 23,
            "fraction": 0.046
          },
          "10%": {
            "alpha": 0.1,
            "count": 60,
            "fraction": 0.12
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
    "kgw": "/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_warmup_gamma0.5_delta3_new1_qwen2_5_0_5b_dolly15k_test.p_values.jsonl",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl"
  },
  "evaluated_at": "2026-10-16T10:32:28+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_warmup_gamma0.5_delta3_new1_qwen2_5_0_5b_dolly15k_test.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-10-16T10:39:06+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.531456
- 实际检测配置：`{"gamma": 0.5, "hash_key": 15485863, "seeding": "simple_1 (hash_key * previous_token_id)", "delta_by_label": {"kgw": 3.0, "clean": 2.0}}`
- ROUGE-L（同批 500 条原始 Dolly 回答作参考）：0.211098（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 原始 Dolly 参考文件：`/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl`
- ROUGE-L（同批 500 条 14B clean 教师回答作参考）：0.262207（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 14B clean 教师参考文件：`/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_clean_test.parquet`
- Best F1：0.675396（z 阈值 -3.2716515254078793，TPR 0.980000，FPR 0.922000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.002000 | 0.002000 | 0.003984 | 37.201625468519524 |
  | 5% | 0.046000 | 0.038000 | 0.070111 | 2.2541740866685807 |
  | 10% | 0.100000 | 0.084000 | 0.141892 | 1.6924558427507104 |

两种逐条文本 p-value 统计（单侧正态近似；不是 AUROC 的显著性检验）：

去重规则：相同的 `(previous_token_id, token_id)` 只计一次；不修改回答文本。

| 数据 | 检测方式 | 有效样本 | p 均值 | p 中位数 | p≤0.01 | p≤0.05 | p≤0.10 |
|---|---|---:|---:|---:|---:|---:|---:|
| kgw | 原始 | 500/500 | 0.505501 | 0.5 | 16 (3.20%) | 44 (8.80%) | 71 (14.20%) |
| kgw | token 对去重 | 500/500 | 0.516716 | 0.544534 | 2 (0.40%) | 25 (5.00%) | 41 (8.20%) |
| clean | 原始 | 500/500 | 0.538121 | 0.57157 | 22 (4.40%) | 54 (10.80%) | 73 (14.60%) |
| clean | token 对去重 | 500/500 | 0.537418 | 0.555154 | 5 (1.00%) | 25 (5.00%) | 46 (9.20%) |

KGW 的小 p 占比是该理论阈值下的检出率，clean 的小 p 占比是实测误报率。p≤0.05 不保证实际 FPR=5%；去重可改善重复带来的失真，但不保证完全校准。空回答不做显著性检验，p=null，并排除在有效样本统计之外。

逐条 p-value：`/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta3_new1_qwen2_5_0_5b_dolly15k_test.p_values.jsonl`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl`

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.5314559999999995,
  "best_f1": {
    "threshold": -3.2716515254078793,
    "fpr": 0.922,
    "tpr": 0.98,
    "precision": 0.5152471083070452,
    "f1": 0.67539627842867,
    "tp": 490,
    "fp": 461,
    "tn": 39,
    "fn": 10
  },
  "tpr_at_fpr": {
    "1%": {
      "threshold": 37.201625468519524,
      "fpr": 0.002,
      "tpr": 0.002,
      "precision": 0.5,
      "f1": 0.00398406374501992,
      "tp": 1,
      "fp": 1,
      "tn": 499,
      "fn": 499,
      "target_fpr": 0.01
    },
    "5%": {
      "threshold": 2.2541740866685807,
      "fpr": 0.046,
      "tpr": 0.038,
      "precision": 0.4523809523809524,
      "f1": 0.07011070110701106,
      "tp": 19,
      "fp": 23,
      "tn": 477,
      "fn": 481,
      "target_fpr": 0.05
    },
    "10%": {
      "threshold": 1.6924558427507104,
      "fpr": 0.1,
      "tpr": 0.084,
      "precision": 0.45652173913043476,
      "f1": 0.14189189189189189,
      "tp": 42,
      "fp": 50,
      "tn": 450,
      "fn": 458,
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
      "clean": 2.0
    }
  },
  "rouge_l_dolly": {
    "mean": 0.21109795092047476,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta3_new1_qwen2_5_0_5b_dolly15k_test.jsonl",
    "reference_file": "/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl",
    "reference_source": "databricks/databricks-dolly-15k:response",
    "metric": "rougeL",
    "measure": "fmeasure",
    "use_stemmer": true,
    "aggregation": "unweighted mean of per-sample ROUGE-L F1"
  },
  "rouge_l_teacher_clean": {
    "mean": 0.26220712387693723,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta3_new1_qwen2_5_0_5b_dolly15k_test.jsonl",
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
        "mean": 0.5055007826165114,
        "median": 0.5,
        "min": 3.211705727028823e-303,
        "max": 1.0,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 16,
            "fraction": 0.032
          },
          "5%": {
            "alpha": 0.05,
            "count": 44,
            "fraction": 0.088
          },
          "10%": {
            "alpha": 0.1,
            "count": 71,
            "fraction": 0.142
          }
        }
      },
      "deduplicated": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.5167162971578534,
        "median": 0.5445336546656558,
        "min": 0.00020112215103030562,
        "max": 0.9986501019683699,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 2,
            "fraction": 0.004
          },
          "5%": {
            "alpha": 0.05,
            "count": 25,
            "fraction": 0.05
          },
          "10%": {
            "alpha": 0.1,
            "count": 41,
            "fraction": 0.082
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
    "kgw": "/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta3_new1_qwen2_5_0_5b_dolly15k_test.p_values.jsonl",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl"
  },
  "evaluated_at": "2026-10-16T10:39:06+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta3_new1_qwen2_5_0_5b_dolly15k_test.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-10-18T13:00:54+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.433434
- 实际检测配置：`{"gamma": 0.5, "hash_key": 15485863, "seeding": "simple_1 (hash_key * previous_token_id)", "delta_by_label": {"kgw": 3.0, "clean": 2.0}}`
- ROUGE-L（同批 500 条原始 Dolly 回答作参考）：0.185418（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 原始 Dolly 参考文件：`/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl`
- ROUGE-L（同批 500 条 14B clean 教师回答作参考）：0.286763（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 14B clean 教师参考文件：`/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_clean_test.parquet`
- Best F1：0.672087（z 阈值 -7.654655446197432，TPR 0.992000，FPR 0.960000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.002000 | 0.002000 | 0.003984 | 36.23203577866784 |
  | 5% | 0.046000 | 0.026000 | 0.048507 | 2.2519414081056586 |
  | 10% | 0.100000 | 0.050000 | 0.086957 | 1.7075311565539322 |

两种逐条文本 p-value 统计（单侧正态近似；不是 AUROC 的显著性检验）：

去重规则：相同的 `(previous_token_id, token_id)` 只计一次；不修改回答文本。

| 数据 | 检测方式 | 有效样本 | p 均值 | p 中位数 | p≤0.01 | p≤0.05 | p≤0.10 |
|---|---|---:|---:|---:|---:|---:|---:|
| kgw | 原始 | 500/500 | 0.619542 | 0.685885 | 11 (2.20%) | 27 (5.40%) | 44 (8.80%) |
| kgw | token 对去重 | 500/500 | 0.618146 | 0.665092 | 3 (0.60%) | 11 (2.20%) | 22 (4.40%) |
| clean | 原始 | 500/500 | 0.538121 | 0.57157 | 22 (4.40%) | 54 (10.80%) | 73 (14.60%) |
| clean | token 对去重 | 500/500 | 0.537418 | 0.555154 | 5 (1.00%) | 25 (5.00%) | 46 (9.20%) |

KGW 的小 p 占比是该理论阈值下的检出率，clean 的小 p 占比是实测误报率。p≤0.05 不保证实际 FPR=5%；去重可改善重复带来的失真，但不保证完全校准。空回答不做显著性检验，p=null，并排除在有效样本统计之外。

逐条 p-value：`/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new.p_values.jsonl`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl`

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.4334339999999997,
  "best_f1": {
    "threshold": -7.654655446197432,
    "fpr": 0.96,
    "tpr": 0.992,
    "precision": 0.5081967213114754,
    "f1": 0.6720867208672088,
    "tp": 496,
    "fp": 480,
    "tn": 20,
    "fn": 4
  },
  "tpr_at_fpr": {
    "1%": {
      "threshold": 36.23203577866784,
      "fpr": 0.002,
      "tpr": 0.002,
      "precision": 0.5,
      "f1": 0.00398406374501992,
      "tp": 1,
      "fp": 1,
      "tn": 499,
      "fn": 499,
      "target_fpr": 0.01
    },
    "5%": {
      "threshold": 2.2519414081056586,
      "fpr": 0.046,
      "tpr": 0.026,
      "precision": 0.3611111111111111,
      "f1": 0.04850746268656716,
      "tp": 13,
      "fp": 23,
      "tn": 477,
      "fn": 487,
      "target_fpr": 0.05
    },
    "10%": {
      "threshold": 1.7075311565539322,
      "fpr": 0.1,
      "tpr": 0.05,
      "precision": 0.3333333333333333,
      "f1": 0.08695652173913045,
      "tp": 25,
      "fp": 50,
      "tn": 450,
      "fn": 475,
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
      "clean": 2.0
    }
  },
  "rouge_l_dolly": {
    "mean": 0.185418046008631,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new.jsonl",
    "reference_file": "/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl",
    "reference_source": "databricks/databricks-dolly-15k:response",
    "metric": "rougeL",
    "measure": "fmeasure",
    "use_stemmer": true,
    "aggregation": "unweighted mean of per-sample ROUGE-L F1"
  },
  "rouge_l_teacher_clean": {
    "mean": 0.2867632931442953,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new.jsonl",
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
        "mean": 0.6195424620785832,
        "median": 0.6858849758356487,
        "min": 9.53201291013277e-288,
        "max": 1.0,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 11,
            "fraction": 0.022
          },
          "5%": {
            "alpha": 0.05,
            "count": 27,
            "fraction": 0.054
          },
          "10%": {
            "alpha": 0.1,
            "count": 44,
            "fraction": 0.088
          }
        }
      },
      "deduplicated": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.618146070028407,
        "median": 0.6650923212002917,
        "min": 0.004024651677903384,
        "max": 0.9998630818329007,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 3,
            "fraction": 0.006
          },
          "5%": {
            "alpha": 0.05,
            "count": 11,
            "fraction": 0.022
          },
          "10%": {
            "alpha": 0.1,
            "count": 22,
            "fraction": 0.044
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
    "kgw": "/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new.p_values.jsonl",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl"
  },
  "evaluated_at": "2026-10-18T13:00:54+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-10-18T14:57:06+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.416208
- 实际检测配置：`{"gamma": 0.5, "hash_key": 15485863, "seeding": "simple_1 (hash_key * previous_token_id)", "delta_by_label": {"kgw": 3.0, "clean": 2.0}}`
- ROUGE-L（同批 500 条原始 Dolly 回答作参考）：0.175276（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 原始 Dolly 参考文件：`/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl`
- ROUGE-L（同批 500 条 14B clean 教师回答作参考）：0.270563（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 14B clean 教师参考文件：`/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_clean_test.parquet`
- Best F1：0.669388（z 阈值 -6.685065756345757，TPR 0.984000，FPR 0.956000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.010000 | 0.004000 | 0.007890 | 9.593834825900782 |
  | 5% | 0.050000 | 0.024000 | 0.044693 | 2.2223355980148636 |
  | 10% | 0.100000 | 0.052000 | 0.090278 | 1.6994116628998401 |

两种逐条文本 p-value 统计（单侧正态近似；不是 AUROC 的显著性检验）：

去重规则：相同的 `(previous_token_id, token_id)` 只计一次；不修改回答文本。

| 数据 | 检测方式 | 有效样本 | p 均值 | p 中位数 | p≤0.01 | p≤0.05 | p≤0.10 |
|---|---|---:|---:|---:|---:|---:|---:|
| kgw | 原始 | 500/500 | 0.639621 | 0.716527 | 8 (1.60%) | 32 (6.40%) | 50 (10.00%) |
| kgw | token 对去重 | 500/500 | 0.635533 | 0.70537 | 1 (0.20%) | 12 (2.40%) | 34 (6.80%) |
| clean | 原始 | 500/500 | 0.538121 | 0.57157 | 22 (4.40%) | 54 (10.80%) | 73 (14.60%) |
| clean | token 对去重 | 500/500 | 0.537418 | 0.555154 | 5 (1.00%) | 25 (5.00%) | 46 (9.20%) |

KGW 的小 p 占比是该理论阈值下的检出率，clean 的小 p 占比是实测误报率。p≤0.05 不保证实际 FPR=5%；去重可改善重复带来的失真，但不保证完全校准。空回答不做显著性检验，p=null，并排除在有效样本统计之外。

逐条 p-value：`/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new_strength3.p_values.jsonl`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl`

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.416208,
  "best_f1": {
    "threshold": -6.685065756345757,
    "fpr": 0.956,
    "tpr": 0.984,
    "precision": 0.5072164948453608,
    "f1": 0.6693877551020408,
    "tp": 492,
    "fp": 478,
    "tn": 22,
    "fn": 8
  },
  "tpr_at_fpr": {
    "1%": {
      "threshold": 9.593834825900782,
      "fpr": 0.01,
      "tpr": 0.004,
      "precision": 0.2857142857142857,
      "f1": 0.007889546351084811,
      "tp": 2,
      "fp": 5,
      "tn": 495,
      "fn": 498,
      "target_fpr": 0.01
    },
    "5%": {
      "threshold": 2.2223355980148636,
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
      "threshold": 1.6994116628998401,
      "fpr": 0.1,
      "tpr": 0.052,
      "precision": 0.34210526315789475,
      "f1": 0.09027777777777778,
      "tp": 26,
      "fp": 50,
      "tn": 450,
      "fn": 474,
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
      "clean": 2.0
    }
  },
  "rouge_l_dolly": {
    "mean": 0.17527607072154583,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new_strength3.jsonl",
    "reference_file": "/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl",
    "reference_source": "databricks/databricks-dolly-15k:response",
    "metric": "rougeL",
    "measure": "fmeasure",
    "use_stemmer": true,
    "aggregation": "unweighted mean of per-sample ROUGE-L F1"
  },
  "rouge_l_teacher_clean": {
    "mean": 0.27056293657683556,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new_strength3.jsonl",
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
        "mean": 0.6396205720998028,
        "median": 0.7165273408147196,
        "min": 1.6759570266182036e-84,
        "max": 1.0,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 8,
            "fraction": 0.016
          },
          "5%": {
            "alpha": 0.05,
            "count": 32,
            "fraction": 0.064
          },
          "10%": {
            "alpha": 0.1,
            "count": 50,
            "fraction": 0.1
          }
        }
      },
      "deduplicated": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.6355330807744789,
        "median": 0.7053699393912358,
        "min": 0.00921106272704951,
        "max": 0.9989289915261519,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 1,
            "fraction": 0.002
          },
          "5%": {
            "alpha": 0.05,
            "count": 12,
            "fraction": 0.024
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
    "kgw": "/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new_strength3.p_values.jsonl",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl"
  },
  "evaluated_at": "2026-10-18T14:57:06+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new_strength3.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-10-18T22:04:11+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.416208
- 实际检测配置：`{"gamma": 0.5, "hash_key": 15485863, "seeding": "simple_1 (hash_key * previous_token_id)", "delta_by_label": {"kgw": 3.0, "clean": 2.0}}`
- ROUGE-L（同批 500 条原始 Dolly 回答作参考）：0.175276（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 原始 Dolly 参考文件：`/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl`
- ROUGE-L（同批 500 条 14B clean 教师回答作参考）：0.270563（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 14B clean 教师参考文件：`/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_clean_test.parquet`
- Best F1：0.669388（z 阈值 -6.685065756345757，TPR 0.984000，FPR 0.956000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.010000 | 0.004000 | 0.007890 | 9.593834825900782 |
  | 5% | 0.050000 | 0.024000 | 0.044693 | 2.2223355980148636 |
  | 10% | 0.100000 | 0.052000 | 0.090278 | 1.6994116628998401 |

两种逐条文本 p-value 统计（单侧正态近似；不是 AUROC 的显著性检验）：

去重规则：相同的 `(previous_token_id, token_id)` 只计一次；不修改回答文本。

| 数据 | 检测方式 | 有效样本 | p 均值 | p 中位数 | p≤0.01 | p≤0.05 | p≤0.10 |
|---|---|---:|---:|---:|---:|---:|---:|
| kgw | 原始 | 500/500 | 0.639621 | 0.716527 | 8 (1.60%) | 32 (6.40%) | 50 (10.00%) |
| kgw | token 对去重 | 500/500 | 0.635533 | 0.70537 | 1 (0.20%) | 12 (2.40%) | 34 (6.80%) |
| clean | 原始 | 500/500 | 0.538121 | 0.57157 | 22 (4.40%) | 54 (10.80%) | 73 (14.60%) |
| clean | token 对去重 | 500/500 | 0.537418 | 0.555154 | 5 (1.00%) | 25 (5.00%) | 46 (9.20%) |

KGW 的小 p 占比是该理论阈值下的检出率，clean 的小 p 占比是实测误报率。p≤0.05 不保证实际 FPR=5%；去重可改善重复带来的失真，但不保证完全校准。空回答不做显著性检验，p=null，并排除在有效样本统计之外。

逐条 p-value：`/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new_strength3.p_values.jsonl`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl`

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.416208,
  "best_f1": {
    "threshold": -6.685065756345757,
    "fpr": 0.956,
    "tpr": 0.984,
    "precision": 0.5072164948453608,
    "f1": 0.6693877551020408,
    "tp": 492,
    "fp": 478,
    "tn": 22,
    "fn": 8
  },
  "tpr_at_fpr": {
    "1%": {
      "threshold": 9.593834825900782,
      "fpr": 0.01,
      "tpr": 0.004,
      "precision": 0.2857142857142857,
      "f1": 0.007889546351084811,
      "tp": 2,
      "fp": 5,
      "tn": 495,
      "fn": 498,
      "target_fpr": 0.01
    },
    "5%": {
      "threshold": 2.2223355980148636,
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
      "threshold": 1.6994116628998401,
      "fpr": 0.1,
      "tpr": 0.052,
      "precision": 0.34210526315789475,
      "f1": 0.09027777777777778,
      "tp": 26,
      "fp": 50,
      "tn": 450,
      "fn": 474,
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
      "clean": 2.0
    }
  },
  "rouge_l_dolly": {
    "mean": 0.17527607072154583,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new_strength3.jsonl",
    "reference_file": "/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl",
    "reference_source": "databricks/databricks-dolly-15k:response",
    "metric": "rougeL",
    "measure": "fmeasure",
    "use_stemmer": true,
    "aggregation": "unweighted mean of per-sample ROUGE-L F1"
  },
  "rouge_l_teacher_clean": {
    "mean": 0.27056293657683556,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new_strength3.jsonl",
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
        "mean": 0.6396205720998028,
        "median": 0.7165273408147196,
        "min": 1.6759570266182036e-84,
        "max": 1.0,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 8,
            "fraction": 0.016
          },
          "5%": {
            "alpha": 0.05,
            "count": 32,
            "fraction": 0.064
          },
          "10%": {
            "alpha": 0.1,
            "count": 50,
            "fraction": 0.1
          }
        }
      },
      "deduplicated": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.6355330807744789,
        "median": 0.7053699393912358,
        "min": 0.00921106272704951,
        "max": 0.9989289915261519,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 1,
            "fraction": 0.002
          },
          "5%": {
            "alpha": 0.05,
            "count": 12,
            "fraction": 0.024
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
    "kgw": "/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new_strength3.p_values.jsonl",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl"
  },
  "evaluated_at": "2026-10-18T22:04:11+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new_strength3.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-10-18T22:12:54+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.416208
- 实际检测配置：`{"gamma": 0.5, "hash_key": 15485863, "seeding": "simple_1 (hash_key * previous_token_id)", "delta_by_label": {"kgw": 3.0, "clean": 2.0}}`
- ROUGE-L（同批 500 条原始 Dolly 回答作参考）：0.175276（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 原始 Dolly 参考文件：`/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl`
- ROUGE-L（同批 500 条 14B clean 教师回答作参考）：0.270563（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 14B clean 教师参考文件：`/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_clean_test.parquet`
- Best F1：0.669388（z 阈值 -6.685065756345757，TPR 0.984000，FPR 0.956000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.010000 | 0.004000 | 0.007890 | 9.593834825900782 |
  | 5% | 0.050000 | 0.024000 | 0.044693 | 2.2223355980148636 |
  | 10% | 0.100000 | 0.052000 | 0.090278 | 1.6994116628998401 |

两种逐条文本 p-value 统计（单侧正态近似；不是 AUROC 的显著性检验）：

去重规则：相同的 `(previous_token_id, token_id)` 只计一次；不修改回答文本。

| 数据 | 检测方式 | 有效样本 | p 均值 | p 中位数 | p≤0.01 | p≤0.05 | p≤0.10 |
|---|---|---:|---:|---:|---:|---:|---:|
| kgw | 原始 | 500/500 | 0.639621 | 0.716527 | 8 (1.60%) | 32 (6.40%) | 50 (10.00%) |
| kgw | token 对去重 | 500/500 | 0.635533 | 0.70537 | 1 (0.20%) | 12 (2.40%) | 34 (6.80%) |
| clean | 原始 | 500/500 | 0.538121 | 0.57157 | 22 (4.40%) | 54 (10.80%) | 73 (14.60%) |
| clean | token 对去重 | 500/500 | 0.537418 | 0.555154 | 5 (1.00%) | 25 (5.00%) | 46 (9.20%) |

KGW 的小 p 占比是该理论阈值下的检出率，clean 的小 p 占比是实测误报率。p≤0.05 不保证实际 FPR=5%；去重可改善重复带来的失真，但不保证完全校准。空回答不做显著性检验，p=null，并排除在有效样本统计之外。

逐条 p-value：`/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new_strength3.p_values.jsonl`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl`

Pan 口径固定 token 分组 p-value（新增；p 越大表示原单侧检验证据越弱）：

按教师 tokenizer 编码回答并无分隔拼接，精确分组；每组首 token 仅作上下文，其余 token 用本项目原 KGW 绿表评分；不去重，尾部不足一组丢弃；各组 p 排序后取上中位数（偶数组不平均）。

| 每组 token 数 | 计分 token 数 | KGW 组数 | KGW median p ↑ | clean 组数 | clean median p | KGW/clean 丢弃尾部 tokens |
|---:|---:|---:|---:|---:|---:|---:|
| 1000 | 999 | 155 | 0.953214 | 159 | 0.865929 | 939/765 |
| 2000 | 1999 | 77 | 0.994946 | 79 | 0.971358 | 1939/1765 |
| 3000 | 2999 | 51 | 0.998542 | 53 | 0.982134 | 2939/765 |
| 10000 | 9999 | 15 | 1 | 15 | 1 | 5939/9765 |
| 20000 | 19999 | 7 | 1 | 7 | 1 | 15939/19765 |
| 30000 | 29999 | 5 | 1 | 5 | 1 | 5939/9765 |

N/A 表示总 token 数不足一个完整组；组数为 1 或 2 时需结合逐组结果解释。极小 p 用科学计数法字符串保存，同时保留 log10(p)，避免浮点下溢为 0。

逐组 p-value 缓存：`/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new_strength3.grouped_p_values.json`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.grouped_p_values.json`

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.416208,
  "best_f1": {
    "threshold": -6.685065756345757,
    "fpr": 0.956,
    "tpr": 0.984,
    "precision": 0.5072164948453608,
    "f1": 0.6693877551020408,
    "tp": 492,
    "fp": 478,
    "tn": 22,
    "fn": 8
  },
  "tpr_at_fpr": {
    "1%": {
      "threshold": 9.593834825900782,
      "fpr": 0.01,
      "tpr": 0.004,
      "precision": 0.2857142857142857,
      "f1": 0.007889546351084811,
      "tp": 2,
      "fp": 5,
      "tn": 495,
      "fn": 498,
      "target_fpr": 0.01
    },
    "5%": {
      "threshold": 2.2223355980148636,
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
      "threshold": 1.6994116628998401,
      "fpr": 0.1,
      "tpr": 0.052,
      "precision": 0.34210526315789475,
      "f1": 0.09027777777777778,
      "tp": 26,
      "fp": 50,
      "tn": 450,
      "fn": 474,
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
      "clean": 2.0
    }
  },
  "rouge_l_dolly": {
    "mean": 0.17527607072154583,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new_strength3.jsonl",
    "reference_file": "/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl",
    "reference_source": "databricks/databricks-dolly-15k:response",
    "metric": "rougeL",
    "measure": "fmeasure",
    "use_stemmer": true,
    "aggregation": "unweighted mean of per-sample ROUGE-L F1"
  },
  "rouge_l_teacher_clean": {
    "mean": 0.27056293657683556,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new_strength3.jsonl",
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
        "mean": 0.6396205720998028,
        "median": 0.7165273408147196,
        "min": 1.6759570266182036e-84,
        "max": 1.0,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 8,
            "fraction": 0.016
          },
          "5%": {
            "alpha": 0.05,
            "count": 32,
            "fraction": 0.064
          },
          "10%": {
            "alpha": 0.1,
            "count": 50,
            "fraction": 0.1
          }
        }
      },
      "deduplicated": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.6355330807744789,
        "median": 0.7053699393912358,
        "min": 0.00921106272704951,
        "max": 0.9989289915261519,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 1,
            "fraction": 0.002
          },
          "5%": {
            "alpha": 0.05,
            "count": 12,
            "fraction": 0.024
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
    "kgw": "/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new_strength3.p_values.jsonl",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl"
  },
  "grouped_p_values": {
    "kgw": {
      "num_answers": 500,
      "total_answer_tokens": 155939,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 155,
          "total_answer_tokens": 155939,
          "discarded_tail_tokens": 939,
          "median_p_value": 0.9532136797396964,
          "median_log10_p_value": -0.02080973364321328,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 77,
          "total_answer_tokens": 155939,
          "discarded_tail_tokens": 1939,
          "median_p_value": 0.9949461262550343,
          "median_log10_p_value": -0.00220043453426638,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 51,
          "total_answer_tokens": 155939,
          "discarded_tail_tokens": 2939,
          "median_p_value": 0.998541992279534,
          "median_log10_p_value": -0.0006336667654240838,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 15,
          "total_answer_tokens": 155939,
          "discarded_tail_tokens": 5939,
          "median_p_value": 0.9999999992771296,
          "median_log10_p_value": -3.139386390720775e-10,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 7,
          "total_answer_tokens": 155939,
          "discarded_tail_tokens": 15939,
          "median_p_value": 1.0,
          "median_log10_p_value": 0.0,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 5,
          "total_answer_tokens": 155939,
          "discarded_tail_tokens": 5939,
          "median_p_value": 1.0,
          "median_log10_p_value": 0.0,
          "status": "ok"
        }
      }
    },
    "clean": {
      "num_answers": 500,
      "total_answer_tokens": 159765,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 159,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 765,
          "median_p_value": 0.8659288977499955,
          "median_log10_p_value": -0.06251776685396769,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 79,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 1765,
          "median_p_value": 0.971357711016285,
          "median_log10_p_value": -0.012620807875598238,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 53,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 765,
          "median_p_value": 0.9821335190767914,
          "median_log10_p_value": -0.007829466737979084,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 15,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 9765,
          "median_p_value": 0.9999999999999984,
          "median_log10_p_value": -6.750292265873014e-16,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 7,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 19765,
          "median_p_value": 1.0,
          "median_log10_p_value": 0.0,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 5,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 9765,
          "median_p_value": 1.0,
          "median_log10_p_value": 0.0,
          "status": "ok"
        }
      }
    }
  },
  "grouped_p_value_method": "teacher-tokenizer answer IDs concatenated without separators; exact disjoint blocks; first token of each block is context only; no repetition deduplication; incomplete tail discarded; upper median of block p-values",
  "per_group_p_value_files": {
    "kgw": "/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new_strength3.grouped_p_values.json",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.grouped_p_values.json"
  },
  "evaluated_at": "2026-10-18T22:12:54+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new_strength3.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-10-18T22:16:05+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.433434
- 实际检测配置：`{"gamma": 0.5, "hash_key": 15485863, "seeding": "simple_1 (hash_key * previous_token_id)", "delta_by_label": {"kgw": 3.0, "clean": 2.0}}`
- ROUGE-L（同批 500 条原始 Dolly 回答作参考）：0.185418（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 原始 Dolly 参考文件：`/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl`
- ROUGE-L（同批 500 条 14B clean 教师回答作参考）：0.286763（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 14B clean 教师参考文件：`/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_clean_test.parquet`
- Best F1：0.672087（z 阈值 -7.654655446197432，TPR 0.992000，FPR 0.960000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.002000 | 0.002000 | 0.003984 | 36.23203577866784 |
  | 5% | 0.046000 | 0.026000 | 0.048507 | 2.2519414081056586 |
  | 10% | 0.100000 | 0.050000 | 0.086957 | 1.7075311565539322 |

两种逐条文本 p-value 统计（单侧正态近似；不是 AUROC 的显著性检验）：

去重规则：相同的 `(previous_token_id, token_id)` 只计一次；不修改回答文本。

| 数据 | 检测方式 | 有效样本 | p 均值 | p 中位数 | p≤0.01 | p≤0.05 | p≤0.10 |
|---|---|---:|---:|---:|---:|---:|---:|
| kgw | 原始 | 500/500 | 0.619542 | 0.685885 | 11 (2.20%) | 27 (5.40%) | 44 (8.80%) |
| kgw | token 对去重 | 500/500 | 0.618146 | 0.665092 | 3 (0.60%) | 11 (2.20%) | 22 (4.40%) |
| clean | 原始 | 500/500 | 0.538121 | 0.57157 | 22 (4.40%) | 54 (10.80%) | 73 (14.60%) |
| clean | token 对去重 | 500/500 | 0.537418 | 0.555154 | 5 (1.00%) | 25 (5.00%) | 46 (9.20%) |

KGW 的小 p 占比是该理论阈值下的检出率，clean 的小 p 占比是实测误报率。p≤0.05 不保证实际 FPR=5%；去重可改善重复带来的失真，但不保证完全校准。空回答不做显著性检验，p=null，并排除在有效样本统计之外。

逐条 p-value：`/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new.p_values.jsonl`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl`

Pan 口径固定 token 分组 p-value（新增；p 越大表示原单侧检验证据越弱）：

按教师 tokenizer 编码回答并无分隔拼接，精确分组；每组首 token 仅作上下文，其余 token 用本项目原 KGW 绿表评分；不去重，尾部不足一组丢弃；各组 p 排序后取上中位数（偶数组不平均）。

| 每组 token 数 | 计分 token 数 | KGW 组数 | KGW median p ↑ | clean 组数 | clean median p | KGW/clean 丢弃尾部 tokens |
|---:|---:|---:|---:|---:|---:|---:|
| 1000 | 999 | 141 | 0.922739 | 159 | 0.865929 | 647/765 |
| 2000 | 1999 | 70 | 0.979091 | 79 | 0.971358 | 1647/1765 |
| 3000 | 2999 | 47 | 0.996744 | 53 | 0.982134 | 647/765 |
| 10000 | 9999 | 14 | 0.999999 | 15 | 1 | 1647/9765 |
| 20000 | 19999 | 7 | 1 | 7 | 1 | 1647/19765 |
| 30000 | 29999 | 4 | 1 | 5 | 1 | 21647/9765 |

N/A 表示总 token 数不足一个完整组；组数为 1 或 2 时需结合逐组结果解释。极小 p 用科学计数法字符串保存，同时保留 log10(p)，避免浮点下溢为 0。

逐组 p-value 缓存：`/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new.grouped_p_values.json`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.grouped_p_values.json`

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.4334339999999997,
  "best_f1": {
    "threshold": -7.654655446197432,
    "fpr": 0.96,
    "tpr": 0.992,
    "precision": 0.5081967213114754,
    "f1": 0.6720867208672088,
    "tp": 496,
    "fp": 480,
    "tn": 20,
    "fn": 4
  },
  "tpr_at_fpr": {
    "1%": {
      "threshold": 36.23203577866784,
      "fpr": 0.002,
      "tpr": 0.002,
      "precision": 0.5,
      "f1": 0.00398406374501992,
      "tp": 1,
      "fp": 1,
      "tn": 499,
      "fn": 499,
      "target_fpr": 0.01
    },
    "5%": {
      "threshold": 2.2519414081056586,
      "fpr": 0.046,
      "tpr": 0.026,
      "precision": 0.3611111111111111,
      "f1": 0.04850746268656716,
      "tp": 13,
      "fp": 23,
      "tn": 477,
      "fn": 487,
      "target_fpr": 0.05
    },
    "10%": {
      "threshold": 1.7075311565539322,
      "fpr": 0.1,
      "tpr": 0.05,
      "precision": 0.3333333333333333,
      "f1": 0.08695652173913045,
      "tp": 25,
      "fp": 50,
      "tn": 450,
      "fn": 475,
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
      "clean": 2.0
    }
  },
  "rouge_l_dolly": {
    "mean": 0.185418046008631,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new.jsonl",
    "reference_file": "/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl",
    "reference_source": "databricks/databricks-dolly-15k:response",
    "metric": "rougeL",
    "measure": "fmeasure",
    "use_stemmer": true,
    "aggregation": "unweighted mean of per-sample ROUGE-L F1"
  },
  "rouge_l_teacher_clean": {
    "mean": 0.2867632931442953,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new.jsonl",
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
        "mean": 0.6195424620785832,
        "median": 0.6858849758356487,
        "min": 9.53201291013277e-288,
        "max": 1.0,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 11,
            "fraction": 0.022
          },
          "5%": {
            "alpha": 0.05,
            "count": 27,
            "fraction": 0.054
          },
          "10%": {
            "alpha": 0.1,
            "count": 44,
            "fraction": 0.088
          }
        }
      },
      "deduplicated": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.618146070028407,
        "median": 0.6650923212002917,
        "min": 0.004024651677903384,
        "max": 0.9998630818329007,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 3,
            "fraction": 0.006
          },
          "5%": {
            "alpha": 0.05,
            "count": 11,
            "fraction": 0.022
          },
          "10%": {
            "alpha": 0.1,
            "count": 22,
            "fraction": 0.044
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
    "kgw": "/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new.p_values.jsonl",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl"
  },
  "grouped_p_values": {
    "kgw": {
      "num_answers": 500,
      "total_answer_tokens": 141647,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 141,
          "total_answer_tokens": 141647,
          "discarded_tail_tokens": 647,
          "median_p_value": 0.9227386896857669,
          "median_log10_p_value": -0.03492126939122037,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 70,
          "total_answer_tokens": 141647,
          "discarded_tail_tokens": 1647,
          "median_p_value": 0.9790911982428734,
          "median_log10_p_value": -0.009176853601383308,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 47,
          "total_answer_tokens": 141647,
          "discarded_tail_tokens": 647,
          "median_p_value": 0.996743879934514,
          "median_log10_p_value": -0.001416422250799275,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 14,
          "total_answer_tokens": 141647,
          "discarded_tail_tokens": 1647,
          "median_p_value": 0.9999988787079404,
          "median_log10_p_value": -4.869712271251867e-07,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 7,
          "total_answer_tokens": 141647,
          "discarded_tail_tokens": 1647,
          "median_p_value": 0.9999999919740807,
          "median_log10_p_value": -3.4856124619019655e-09,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 4,
          "total_answer_tokens": 141647,
          "discarded_tail_tokens": 21647,
          "median_p_value": 1.0,
          "median_log10_p_value": 0.0,
          "status": "ok"
        }
      }
    },
    "clean": {
      "num_answers": 500,
      "total_answer_tokens": 159765,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 159,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 765,
          "median_p_value": 0.8659288977499955,
          "median_log10_p_value": -0.06251776685396769,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 79,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 1765,
          "median_p_value": 0.971357711016285,
          "median_log10_p_value": -0.012620807875598238,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 53,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 765,
          "median_p_value": 0.9821335190767914,
          "median_log10_p_value": -0.007829466737979084,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 15,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 9765,
          "median_p_value": 0.9999999999999984,
          "median_log10_p_value": -6.750292265873014e-16,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 7,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 19765,
          "median_p_value": 1.0,
          "median_log10_p_value": 0.0,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 5,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 9765,
          "median_p_value": 1.0,
          "median_log10_p_value": 0.0,
          "status": "ok"
        }
      }
    }
  },
  "grouped_p_value_method": "teacher-tokenizer answer IDs concatenated without separators; exact disjoint blocks; first token of each block is context only; no repetition deduplication; incomplete tail discarded; upper median of block p-values",
  "per_group_p_value_files": {
    "kgw": "/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new.grouped_p_values.json",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.grouped_p_values.json"
  },
  "evaluated_at": "2026-10-18T22:16:05+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-10-18T22:30:20+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.647688
- 实际检测配置：`{"gamma": 0.5, "hash_key": 15485863, "seeding": "simple_1 (hash_key * previous_token_id)", "delta_by_label": {"kgw": 3.0, "clean": 2.0}}`
- ROUGE-L（同批 500 条原始 Dolly 回答作参考）：0.198494（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 原始 Dolly 参考文件：`/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl`
- ROUGE-L（同批 500 条 14B clean 教师回答作参考）：0.309174（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 14B clean 教师参考文件：`/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_clean_test.parquet`
- Best F1：0.685011（z 阈值 -1.5460413650478515，TPR 0.946000，FPR 0.816000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.000000 | 0.000000 | 0.000000 | None |
  | 5% | 0.050000 | 0.114000 | 0.195876 | 2.225394561056747 |
  | 10% | 0.100000 | 0.228000 | 0.343373 | 1.6859773678906163 |

两种逐条文本 p-value 统计（单侧正态近似；不是 AUROC 的显著性检验）：

去重规则：相同的 `(previous_token_id, token_id)` 只计一次；不修改回答文本。

| 数据 | 检测方式 | 有效样本 | p 均值 | p 中位数 | p≤0.01 | p≤0.05 | p≤0.10 |
|---|---|---:|---:|---:|---:|---:|---:|
| kgw | 原始 | 500/500 | 0.365777 | 0.238373 | 53 (10.60%) | 119 (23.80%) | 156 (31.20%) |
| kgw | token 对去重 | 500/500 | 0.347472 | 0.270591 | 19 (3.80%) | 80 (16.00%) | 140 (28.00%) |
| clean | 原始 | 500/500 | 0.538121 | 0.57157 | 22 (4.40%) | 54 (10.80%) | 73 (14.60%) |
| clean | token 对去重 | 500/500 | 0.537418 | 0.555154 | 5 (1.00%) | 25 (5.00%) | 46 (9.20%) |

KGW 的小 p 占比是该理论阈值下的检出率，clean 的小 p 占比是实测误报率。p≤0.05 不保证实际 FPR=5%；去重可改善重复带来的失真，但不保证完全校准。空回答不做显著性检验，p=null，并排除在有效样本统计之外。

逐条 p-value：`/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.p_values.jsonl`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl`

Pan 口径固定 token 分组 p-value（新增；p 越大表示原单侧检验证据越弱）：

按教师 tokenizer 编码回答并无分隔拼接，精确分组；每组首 token 仅作上下文，其余 token 用本项目原 KGW 绿表评分；不去重，尾部不足一组丢弃；各组 p 排序后取上中位数（偶数组不平均）。

| 每组 token 数 | 计分 token 数 | KGW 组数 | KGW median p ↑ | clean 组数 | clean median p | KGW/clean 丢弃尾部 tokens |
|---:|---:|---:|---:|---:|---:|---:|
| 1000 | 999 | 124 | 0.0972842 | 159 | 0.865929 | 556/765 |
| 2000 | 1999 | 62 | 0.0232625 | 79 | 0.971358 | 556/1765 |
| 3000 | 2999 | 41 | 0.00451065 | 53 | 0.982134 | 1556/765 |
| 10000 | 9999 | 12 | 0.000141611 | 15 | 1 | 4556/9765 |
| 20000 | 19999 | 6 | 4.13001e-09 | 7 | 1 | 4556/19765 |
| 30000 | 29999 | 4 | 6.07036e-11 | 5 | 1 | 4556/9765 |

N/A 表示总 token 数不足一个完整组；组数为 1 或 2 时需结合逐组结果解释。极小 p 用科学计数法字符串保存，同时保留 log10(p)，避免浮点下溢为 0。

逐组 p-value 缓存：`/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.grouped_p_values.json`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.grouped_p_values.json`

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.6476880000000005,
  "best_f1": {
    "threshold": -1.5460413650478515,
    "fpr": 0.816,
    "tpr": 0.946,
    "precision": 0.5368898978433598,
    "f1": 0.6850108616944243,
    "tp": 473,
    "fp": 408,
    "tn": 92,
    "fn": 27
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
      "threshold": 2.225394561056747,
      "fpr": 0.05,
      "tpr": 0.114,
      "precision": 0.6951219512195121,
      "f1": 0.19587628865979384,
      "tp": 57,
      "fp": 25,
      "tn": 475,
      "fn": 443,
      "target_fpr": 0.05
    },
    "10%": {
      "threshold": 1.6859773678906163,
      "fpr": 0.1,
      "tpr": 0.228,
      "precision": 0.6951219512195121,
      "f1": 0.34337349397590367,
      "tp": 114,
      "fp": 50,
      "tn": 450,
      "fn": 386,
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
      "clean": 2.0
    }
  },
  "rouge_l_dolly": {
    "mean": 0.19849387557587408,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.jsonl",
    "reference_file": "/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl",
    "reference_source": "databricks/databricks-dolly-15k:response",
    "metric": "rougeL",
    "measure": "fmeasure",
    "use_stemmer": true,
    "aggregation": "unweighted mean of per-sample ROUGE-L F1"
  },
  "rouge_l_teacher_clean": {
    "mean": 0.3091744425525882,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.jsonl",
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
        "mean": 0.36577704616420137,
        "median": 0.2383728596628124,
        "min": 6.834897526731109e-14,
        "max": 0.9999999683624243,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 53,
            "fraction": 0.106
          },
          "5%": {
            "alpha": 0.05,
            "count": 119,
            "fraction": 0.238
          },
          "10%": {
            "alpha": 0.1,
            "count": 156,
            "fraction": 0.312
          }
        }
      },
      "deduplicated": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.3474721954408633,
        "median": 0.2705911687912894,
        "min": 9.802720950622567e-05,
        "max": 0.9947064313329715,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 19,
            "fraction": 0.038
          },
          "5%": {
            "alpha": 0.05,
            "count": 80,
            "fraction": 0.16
          },
          "10%": {
            "alpha": 0.1,
            "count": 140,
            "fraction": 0.28
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
    "kgw": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.p_values.jsonl",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl"
  },
  "grouped_p_values": {
    "kgw": {
      "num_answers": 500,
      "total_answer_tokens": 124556,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 124,
          "total_answer_tokens": 124556,
          "discarded_tail_tokens": 556,
          "median_p_value": 0.09728418407710798,
          "median_log10_p_value": -1.0119577591802715,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 62,
          "total_answer_tokens": 124556,
          "discarded_tail_tokens": 556,
          "median_p_value": 0.023262538509681907,
          "median_log10_p_value": -1.6333428949131483,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 41,
          "total_answer_tokens": 124556,
          "discarded_tail_tokens": 1556,
          "median_p_value": 0.004510647390091074,
          "median_log10_p_value": -2.345761121588415,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 12,
          "total_answer_tokens": 124556,
          "discarded_tail_tokens": 4556,
          "median_p_value": 0.00014161098937565957,
          "median_log10_p_value": -3.848903042973794,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 6,
          "total_answer_tokens": 124556,
          "discarded_tail_tokens": 4556,
          "median_p_value": 4.130014279977983e-09,
          "median_log10_p_value": -8.384048446720133,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 4,
          "total_answer_tokens": 124556,
          "discarded_tail_tokens": 4556,
          "median_p_value": 6.070355091020732e-11,
          "median_log10_p_value": -10.216785903725345,
          "status": "ok"
        }
      }
    },
    "clean": {
      "num_answers": 500,
      "total_answer_tokens": 159765,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 159,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 765,
          "median_p_value": 0.8659288977499955,
          "median_log10_p_value": -0.06251776685396769,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 79,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 1765,
          "median_p_value": 0.971357711016285,
          "median_log10_p_value": -0.012620807875598238,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 53,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 765,
          "median_p_value": 0.9821335190767914,
          "median_log10_p_value": -0.007829466737979084,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 15,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 9765,
          "median_p_value": 0.9999999999999984,
          "median_log10_p_value": -6.750292265873014e-16,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 7,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 19765,
          "median_p_value": 1.0,
          "median_log10_p_value": 0.0,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 5,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 9765,
          "median_p_value": 1.0,
          "median_log10_p_value": 0.0,
          "status": "ok"
        }
      }
    }
  },
  "grouped_p_value_method": "teacher-tokenizer answer IDs concatenated without separators; exact disjoint blocks; first token of each block is context only; no repetition deduplication; incomplete tail discarded; upper median of block p-values",
  "per_group_p_value_files": {
    "kgw": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.grouped_p_values.json",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.grouped_p_values.json"
  },
  "evaluated_at": "2026-10-18T22:30:20+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-10-18T22:32:06+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.531456
- 实际检测配置：`{"gamma": 0.5, "hash_key": 15485863, "seeding": "simple_1 (hash_key * previous_token_id)", "delta_by_label": {"kgw": 3.0, "clean": 2.0}}`
- ROUGE-L（同批 500 条原始 Dolly 回答作参考）：0.211098（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 原始 Dolly 参考文件：`/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl`
- ROUGE-L（同批 500 条 14B clean 教师回答作参考）：0.262207（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 14B clean 教师参考文件：`/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_clean_test.parquet`
- Best F1：0.675396（z 阈值 -3.2716515254078793，TPR 0.980000，FPR 0.922000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.002000 | 0.002000 | 0.003984 | 37.201625468519524 |
  | 5% | 0.046000 | 0.038000 | 0.070111 | 2.2541740866685807 |
  | 10% | 0.100000 | 0.084000 | 0.141892 | 1.6924558427507104 |

两种逐条文本 p-value 统计（单侧正态近似；不是 AUROC 的显著性检验）：

去重规则：相同的 `(previous_token_id, token_id)` 只计一次；不修改回答文本。

| 数据 | 检测方式 | 有效样本 | p 均值 | p 中位数 | p≤0.01 | p≤0.05 | p≤0.10 |
|---|---|---:|---:|---:|---:|---:|---:|
| kgw | 原始 | 500/500 | 0.505501 | 0.5 | 16 (3.20%) | 44 (8.80%) | 71 (14.20%) |
| kgw | token 对去重 | 500/500 | 0.516716 | 0.544534 | 2 (0.40%) | 25 (5.00%) | 41 (8.20%) |
| clean | 原始 | 500/500 | 0.538121 | 0.57157 | 22 (4.40%) | 54 (10.80%) | 73 (14.60%) |
| clean | token 对去重 | 500/500 | 0.537418 | 0.555154 | 5 (1.00%) | 25 (5.00%) | 46 (9.20%) |

KGW 的小 p 占比是该理论阈值下的检出率，clean 的小 p 占比是实测误报率。p≤0.05 不保证实际 FPR=5%；去重可改善重复带来的失真，但不保证完全校准。空回答不做显著性检验，p=null，并排除在有效样本统计之外。

逐条 p-value：`/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta3_new1_qwen2_5_0_5b_dolly15k_test.p_values.jsonl`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl`

Pan 口径固定 token 分组 p-value（新增；p 越大表示原单侧检验证据越弱）：

按教师 tokenizer 编码回答并无分隔拼接，精确分组；每组首 token 仅作上下文，其余 token 用本项目原 KGW 绿表评分；不去重，尾部不足一组丢弃；各组 p 排序后取上中位数（偶数组不平均）。

| 每组 token 数 | 计分 token 数 | KGW 组数 | KGW median p ↑ | clean 组数 | clean median p | KGW/clean 丢弃尾部 tokens |
|---:|---:|---:|---:|---:|---:|---:|
| 1000 | 999 | 70 | 0.659574 | 159 | 0.865929 | 907/765 |
| 2000 | 1999 | 35 | 0.631374 | 79 | 0.971358 | 907/1765 |
| 3000 | 2999 | 23 | 0.550856 | 53 | 0.982134 | 1907/765 |
| 10000 | 9999 | 7 | 0.979823 | 15 | 1 | 907/9765 |
| 20000 | 19999 | 3 | 0.986561 | 7 | 1 | 10907/19765 |
| 30000 | 29999 | 2 | 1 | 5 | 1 | 10907/9765 |

N/A 表示总 token 数不足一个完整组；组数为 1 或 2 时需结合逐组结果解释。极小 p 用科学计数法字符串保存，同时保留 log10(p)，避免浮点下溢为 0。

逐组 p-value 缓存：`/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta3_new1_qwen2_5_0_5b_dolly15k_test.grouped_p_values.json`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.grouped_p_values.json`

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.5314559999999995,
  "best_f1": {
    "threshold": -3.2716515254078793,
    "fpr": 0.922,
    "tpr": 0.98,
    "precision": 0.5152471083070452,
    "f1": 0.67539627842867,
    "tp": 490,
    "fp": 461,
    "tn": 39,
    "fn": 10
  },
  "tpr_at_fpr": {
    "1%": {
      "threshold": 37.201625468519524,
      "fpr": 0.002,
      "tpr": 0.002,
      "precision": 0.5,
      "f1": 0.00398406374501992,
      "tp": 1,
      "fp": 1,
      "tn": 499,
      "fn": 499,
      "target_fpr": 0.01
    },
    "5%": {
      "threshold": 2.2541740866685807,
      "fpr": 0.046,
      "tpr": 0.038,
      "precision": 0.4523809523809524,
      "f1": 0.07011070110701106,
      "tp": 19,
      "fp": 23,
      "tn": 477,
      "fn": 481,
      "target_fpr": 0.05
    },
    "10%": {
      "threshold": 1.6924558427507104,
      "fpr": 0.1,
      "tpr": 0.084,
      "precision": 0.45652173913043476,
      "f1": 0.14189189189189189,
      "tp": 42,
      "fp": 50,
      "tn": 450,
      "fn": 458,
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
      "clean": 2.0
    }
  },
  "rouge_l_dolly": {
    "mean": 0.21109795092047476,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta3_new1_qwen2_5_0_5b_dolly15k_test.jsonl",
    "reference_file": "/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl",
    "reference_source": "databricks/databricks-dolly-15k:response",
    "metric": "rougeL",
    "measure": "fmeasure",
    "use_stemmer": true,
    "aggregation": "unweighted mean of per-sample ROUGE-L F1"
  },
  "rouge_l_teacher_clean": {
    "mean": 0.26220712387693723,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta3_new1_qwen2_5_0_5b_dolly15k_test.jsonl",
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
        "mean": 0.5055007826165114,
        "median": 0.5,
        "min": 3.211705727028823e-303,
        "max": 1.0,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 16,
            "fraction": 0.032
          },
          "5%": {
            "alpha": 0.05,
            "count": 44,
            "fraction": 0.088
          },
          "10%": {
            "alpha": 0.1,
            "count": 71,
            "fraction": 0.142
          }
        }
      },
      "deduplicated": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.5167162971578534,
        "median": 0.5445336546656558,
        "min": 0.00020112215103030562,
        "max": 0.9986501019683699,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 2,
            "fraction": 0.004
          },
          "5%": {
            "alpha": 0.05,
            "count": 25,
            "fraction": 0.05
          },
          "10%": {
            "alpha": 0.1,
            "count": 41,
            "fraction": 0.082
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
    "kgw": "/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta3_new1_qwen2_5_0_5b_dolly15k_test.p_values.jsonl",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl"
  },
  "grouped_p_values": {
    "kgw": {
      "num_answers": 500,
      "total_answer_tokens": 70907,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 70,
          "total_answer_tokens": 70907,
          "discarded_tail_tokens": 907,
          "median_p_value": 0.6595743743853253,
          "median_log10_p_value": -0.1807362257977395,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 35,
          "total_answer_tokens": 70907,
          "discarded_tail_tokens": 907,
          "median_p_value": 0.6313737953880422,
          "median_log10_p_value": -0.19971344707880243,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 23,
          "total_answer_tokens": 70907,
          "discarded_tail_tokens": 1907,
          "median_p_value": 0.5508555692782966,
          "median_log10_p_value": -0.25896225539111434,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 7,
          "total_answer_tokens": 70907,
          "discarded_tail_tokens": 907,
          "median_p_value": 0.9798227856258324,
          "median_log10_p_value": -0.008852465311915528,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 3,
          "total_answer_tokens": 70907,
          "discarded_tail_tokens": 10907,
          "median_p_value": 0.9865614999705343,
          "median_log10_p_value": -0.005875836650683909,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 2,
          "total_answer_tokens": 70907,
          "discarded_tail_tokens": 10907,
          "median_p_value": 1.0,
          "median_log10_p_value": 0.0,
          "status": "ok"
        }
      }
    },
    "clean": {
      "num_answers": 500,
      "total_answer_tokens": 159765,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 159,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 765,
          "median_p_value": 0.8659288977499955,
          "median_log10_p_value": -0.06251776685396769,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 79,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 1765,
          "median_p_value": 0.971357711016285,
          "median_log10_p_value": -0.012620807875598238,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 53,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 765,
          "median_p_value": 0.9821335190767914,
          "median_log10_p_value": -0.007829466737979084,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 15,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 9765,
          "median_p_value": 0.9999999999999984,
          "median_log10_p_value": -6.750292265873014e-16,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 7,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 19765,
          "median_p_value": 1.0,
          "median_log10_p_value": 0.0,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 5,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 9765,
          "median_p_value": 1.0,
          "median_log10_p_value": 0.0,
          "status": "ok"
        }
      }
    }
  },
  "grouped_p_value_method": "teacher-tokenizer answer IDs concatenated without separators; exact disjoint blocks; first token of each block is context only; no repetition deduplication; incomplete tail discarded; upper median of block p-values",
  "per_group_p_value_files": {
    "kgw": "/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta3_new1_qwen2_5_0_5b_dolly15k_test.grouped_p_values.json",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.grouped_p_values.json"
  },
  "evaluated_at": "2026-10-18T22:32:06+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta3_new1_qwen2_5_0_5b_dolly15k_test.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-10-19T10:21:10+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.531456
- 实际检测配置：`{"gamma": 0.5, "hash_key": 15485863, "seeding": "simple_1 (hash_key * previous_token_id)", "delta_by_label": {"kgw": 3.0, "clean": 2.0}}`
- ROUGE-L（同批 500 条原始 Dolly 回答作参考）：0.211098（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 原始 Dolly 参考文件：`/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl`
- ROUGE-L（同批 500 条 14B clean 教师回答作参考）：0.262207（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 14B clean 教师参考文件：`/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_clean_test.parquet`
- Best F1：0.675396（z 阈值 -3.2716515254078793，TPR 0.980000，FPR 0.922000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.002000 | 0.002000 | 0.003984 | 37.201625468519524 |
  | 5% | 0.046000 | 0.038000 | 0.070111 | 2.2541740866685807 |
  | 10% | 0.100000 | 0.084000 | 0.141892 | 1.6924558427507104 |

两种逐条文本 p-value 统计（单侧正态近似；不是 AUROC 的显著性检验）：

去重规则：相同的 `(previous_token_id, token_id)` 只计一次；不修改回答文本。

| 数据 | 检测方式 | 有效样本 | p 均值 | p 中位数 | p≤0.01 | p≤0.05 | p≤0.10 |
|---|---|---:|---:|---:|---:|---:|---:|
| kgw | 原始 | 500/500 | 0.505501 | 0.5 | 16 (3.20%) | 44 (8.80%) | 71 (14.20%) |
| kgw | token 对去重 | 500/500 | 0.516716 | 0.544534 | 2 (0.40%) | 25 (5.00%) | 41 (8.20%) |
| clean | 原始 | 500/500 | 0.538121 | 0.57157 | 22 (4.40%) | 54 (10.80%) | 73 (14.60%) |
| clean | token 对去重 | 500/500 | 0.537418 | 0.555154 | 5 (1.00%) | 25 (5.00%) | 46 (9.20%) |

KGW 的小 p 占比是该理论阈值下的检出率，clean 的小 p 占比是实测误报率。p≤0.05 不保证实际 FPR=5%；去重可改善重复带来的失真，但不保证完全校准。空回答不做显著性检验，p=null，并排除在有效样本统计之外。

逐条 p-value：`/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta3_new1_qwen2_5_0_5b_dolly15k_test.p_values.jsonl`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl`

固定 token 分组 p-value（普通中位数；p 越大表示原单侧检验证据越弱）：

按教师 tokenizer 编码回答并无分隔拼接，精确分组；每组首 token 仅作上下文，其余 token 用本项目原 KGW 绿表评分；不去重，尾部不足一组丢弃；各组 p 排序后取普通中位数（偶数组取中间两个 p 的算术平均）。

| 每组 token 数 | 计分 token 数 | KGW 组数 | KGW median p ↑ | clean 组数 | clean median p | KGW/clean 丢弃尾部 tokens |
|---:|---:|---:|---:|---:|---:|---:|
| 1000 | 999 | 70 | 0.647832 | 159 | 0.865929 | 907/765 |
| 2000 | 1999 | 35 | 0.631374 | 79 | 0.971358 | 907/1765 |
| 3000 | 2999 | 23 | 0.550856 | 53 | 0.982134 | 1907/765 |
| 10000 | 9999 | 7 | 0.979823 | 15 | 1 | 907/9765 |
| 20000 | 19999 | 3 | 0.986561 | 7 | 1 | 10907/19765 |
| 30000 | 29999 | 2 | 0.500352 | 5 | 1 | 10907/9765 |

N/A 表示总 token 数不足一个完整组；组数为 1 或 2 时需结合逐组结果解释。极小 p 用科学计数法字符串保存，同时保留 log10(p)，避免浮点下溢为 0。

逐组 p-value 缓存：`/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta3_new1_qwen2_5_0_5b_dolly15k_test.grouped_p_values.json`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.grouped_p_values.json`

剔除严重重复回答后的固定 token 分组 p-value（普通中位数）：

先独立筛选 KGW 和 clean：回答内部相邻 token 对重复比例严格大于 50% 时，剔除整条回答；prompt 不参与判断。保留回答按原顺序重新无分隔拼接，各组首 token 仅作上下文；组内不做 token 对去重，尾部不足一组丢弃。这是质量筛选补充指标，原始全样本统计另行保留。

| 数据 | 原回答数 | 剔除严重重复回答 | 保留回答数 | 原 tokens | 剔除 tokens | 保留 tokens |
|---|---:|---:|---:|---:|---:|---:|
| kgw | 500 | 15 (3.00%) | 485 | 70907 | 14061 | 56846 |
| clean | 500 | 88 (17.60%) | 412 | 159765 | 113883 | 45882 |

| 每组 token 数 | 计分 token 数 | KGW 组数 | KGW median p ↑ | clean 组数 | clean median p | KGW/clean 丢弃尾部 tokens |
|---:|---:|---:|---:|---:|---:|---:|
| 1000 | 999 | 56 | 0.562723 | 45 | 0.636089 | 846/882 |
| 2000 | 1999 | 28 | 0.535635 | 22 | 0.796038 | 846/1882 |
| 3000 | 2999 | 18 | 0.514506 | 15 | 0.738626 | 2846/882 |
| 10000 | 9999 | 5 | 0.680831 | 4 | 0.947597 | 6846/5882 |
| 20000 | 19999 | 2 | 0.661378 | 2 | 0.978374 | 16846/5882 |
| 30000 | 29999 | 1 | 0.841062 | 1 | 0.999568 | 26846/15882 |

N/A 表示筛选后不足一个完整组。各组 p 取普通中位数，偶数组取中间两个 p 的算术平均；组数较少时请结合逐组缓存解释。

剔除严重重复回答后的逐组 p-value 缓存：`/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta3_new1_qwen2_5_0_5b_dolly15k_test.nonrepetitive_grouped_p_values.json`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.nonrepetitive_grouped_p_values.json`

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.5314559999999995,
  "best_f1": {
    "threshold": -3.2716515254078793,
    "fpr": 0.922,
    "tpr": 0.98,
    "precision": 0.5152471083070452,
    "f1": 0.67539627842867,
    "tp": 490,
    "fp": 461,
    "tn": 39,
    "fn": 10
  },
  "tpr_at_fpr": {
    "1%": {
      "threshold": 37.201625468519524,
      "fpr": 0.002,
      "tpr": 0.002,
      "precision": 0.5,
      "f1": 0.00398406374501992,
      "tp": 1,
      "fp": 1,
      "tn": 499,
      "fn": 499,
      "target_fpr": 0.01
    },
    "5%": {
      "threshold": 2.2541740866685807,
      "fpr": 0.046,
      "tpr": 0.038,
      "precision": 0.4523809523809524,
      "f1": 0.07011070110701106,
      "tp": 19,
      "fp": 23,
      "tn": 477,
      "fn": 481,
      "target_fpr": 0.05
    },
    "10%": {
      "threshold": 1.6924558427507104,
      "fpr": 0.1,
      "tpr": 0.084,
      "precision": 0.45652173913043476,
      "f1": 0.14189189189189189,
      "tp": 42,
      "fp": 50,
      "tn": 450,
      "fn": 458,
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
      "clean": 2.0
    }
  },
  "rouge_l_dolly": {
    "mean": 0.21109795092047476,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta3_new1_qwen2_5_0_5b_dolly15k_test.jsonl",
    "reference_file": "/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl",
    "reference_source": "databricks/databricks-dolly-15k:response",
    "metric": "rougeL",
    "measure": "fmeasure",
    "use_stemmer": true,
    "aggregation": "unweighted mean of per-sample ROUGE-L F1"
  },
  "rouge_l_teacher_clean": {
    "mean": 0.26220712387693723,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta3_new1_qwen2_5_0_5b_dolly15k_test.jsonl",
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
        "mean": 0.5055007826165114,
        "median": 0.5,
        "min": 3.211705727028823e-303,
        "max": 1.0,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 16,
            "fraction": 0.032
          },
          "5%": {
            "alpha": 0.05,
            "count": 44,
            "fraction": 0.088
          },
          "10%": {
            "alpha": 0.1,
            "count": 71,
            "fraction": 0.142
          }
        }
      },
      "deduplicated": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.5167162971578534,
        "median": 0.5445336546656558,
        "min": 0.00020112215103030562,
        "max": 0.9986501019683699,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 2,
            "fraction": 0.004
          },
          "5%": {
            "alpha": 0.05,
            "count": 25,
            "fraction": 0.05
          },
          "10%": {
            "alpha": 0.1,
            "count": 41,
            "fraction": 0.082
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
    "kgw": "/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta3_new1_qwen2_5_0_5b_dolly15k_test.p_values.jsonl",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl"
  },
  "grouped_p_values": {
    "kgw": {
      "aggregation": "ordinary_median",
      "num_answers": 500,
      "total_answer_tokens": 70907,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 70,
          "total_answer_tokens": 70907,
          "discarded_tail_tokens": 907,
          "median_p_value": 0.6478317596858809,
          "median_log10_p_value": -0.18853776469536945,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 35,
          "total_answer_tokens": 70907,
          "discarded_tail_tokens": 907,
          "median_p_value": 0.6313737953880422,
          "median_log10_p_value": -0.19971344707880243,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 23,
          "total_answer_tokens": 70907,
          "discarded_tail_tokens": 1907,
          "median_p_value": 0.5508555692782966,
          "median_log10_p_value": -0.25896225539111434,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 7,
          "total_answer_tokens": 70907,
          "discarded_tail_tokens": 907,
          "median_p_value": 0.9798227856258324,
          "median_log10_p_value": -0.008852465311915528,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 3,
          "total_answer_tokens": 70907,
          "discarded_tail_tokens": 10907,
          "median_p_value": 0.9865614999705343,
          "median_log10_p_value": -0.005875836650683909,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 2,
          "total_answer_tokens": 70907,
          "discarded_tail_tokens": 10907,
          "median_p_value": 0.5003522510007945,
          "median_log10_p_value": -0.30072414205679476,
          "status": "ok"
        }
      }
    },
    "clean": {
      "aggregation": "ordinary_median",
      "num_answers": 500,
      "total_answer_tokens": 159765,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 159,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 765,
          "median_p_value": 0.8659288977499955,
          "median_log10_p_value": -0.06251776685396769,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 79,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 1765,
          "median_p_value": 0.971357711016285,
          "median_log10_p_value": -0.012620807875598238,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 53,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 765,
          "median_p_value": 0.9821335190767914,
          "median_log10_p_value": -0.007829466737979084,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 15,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 9765,
          "median_p_value": 0.9999999999999984,
          "median_log10_p_value": -6.750292265873014e-16,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 7,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 19765,
          "median_p_value": 1.0,
          "median_log10_p_value": 0.0,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 5,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 9765,
          "median_p_value": 1.0,
          "median_log10_p_value": 0.0,
          "status": "ok"
        }
      }
    }
  },
  "grouped_p_value_method": "teacher-tokenizer answer IDs concatenated without separators; exact disjoint blocks; first token of each block is context only; no repetition deduplication; incomplete tail discarded; ordinary median of block p-values (arithmetic mean of the two middle p-values for even group counts)",
  "per_group_p_value_files": {
    "kgw": "/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta3_new1_qwen2_5_0_5b_dolly15k_test.grouped_p_values.json",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.grouped_p_values.json"
  },
  "grouped_p_values_without_severe_repetition": {
    "kgw": {
      "aggregation": "ordinary_median",
      "num_answers": 485,
      "total_answer_tokens": 56846,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 56,
          "total_answer_tokens": 56846,
          "discarded_tail_tokens": 846,
          "median_p_value": 0.5627229887103784,
          "median_log10_p_value": -0.24970534241464606,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 28,
          "total_answer_tokens": 56846,
          "discarded_tail_tokens": 846,
          "median_p_value": 0.535634960500796,
          "median_log10_p_value": -0.27113108465279767,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 18,
          "total_answer_tokens": 56846,
          "discarded_tail_tokens": 2846,
          "median_p_value": 0.5145059419790791,
          "median_log10_p_value": -0.2886096052478569,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 5,
          "total_answer_tokens": 56846,
          "discarded_tail_tokens": 6846,
          "median_p_value": 0.6808308865958813,
          "median_log10_p_value": -0.16696075025912627,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 2,
          "total_answer_tokens": 56846,
          "discarded_tail_tokens": 16846,
          "median_p_value": 0.661378100059638,
          "median_log10_p_value": -0.17955018979836485,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 1,
          "total_answer_tokens": 56846,
          "discarded_tail_tokens": 26846,
          "median_p_value": 0.8410621077238487,
          "median_log10_p_value": -0.0751719328039635,
          "status": "ok"
        }
      },
      "filtering": {
        "repetition_threshold": 0.5,
        "comparison": ">",
        "scope": "answer-internal adjacent token pairs; prompt excluded",
        "num_answers_before": 500,
        "num_answers_retained": 485,
        "num_answers_removed": 15,
        "fraction_answers_removed": 0.03,
        "total_answer_tokens_before": 70907,
        "total_answer_tokens_retained": 56846,
        "total_answer_tokens_removed": 14061,
        "removed_answer_ids": [
          "dolly-08884",
          "dolly-01092",
          "dolly-02844",
          "dolly-03638",
          "dolly-13981",
          "dolly-10747",
          "dolly-04773",
          "dolly-07936",
          "dolly-09563",
          "dolly-02451",
          "dolly-06932",
          "dolly-08607",
          "dolly-00148",
          "dolly-05355",
          "dolly-06970"
        ]
      }
    },
    "clean": {
      "aggregation": "ordinary_median",
      "num_answers": 412,
      "total_answer_tokens": 45882,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 45,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 882,
          "median_p_value": 0.6360891449864364,
          "median_log10_p_value": -0.1964820156995508,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 22,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 1882,
          "median_p_value": 0.7960378878131416,
          "median_log10_p_value": -0.09906626131183685,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 15,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 882,
          "median_p_value": 0.7386263221105359,
          "median_log10_p_value": -0.13157521964243946,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 4,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 5882,
          "median_p_value": 0.947596846602552,
          "median_log10_p_value": -0.0233763931850151,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 2,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 5882,
          "median_p_value": 0.9783739864832501,
          "median_log10_p_value": -0.009495103065976066,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 1,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 15882,
          "median_p_value": 0.9995678964162934,
          "median_log10_p_value": -0.00018770075802065225,
          "status": "ok"
        }
      },
      "filtering": {
        "repetition_threshold": 0.5,
        "comparison": ">",
        "scope": "answer-internal adjacent token pairs; prompt excluded",
        "num_answers_before": 500,
        "num_answers_retained": 412,
        "num_answers_removed": 88,
        "fraction_answers_removed": 0.176,
        "total_answer_tokens_before": 159765,
        "total_answer_tokens_retained": 45882,
        "total_answer_tokens_removed": 113883,
        "removed_answer_ids": [
          "dolly-00135",
          "dolly-12241",
          "dolly-07923",
          "dolly-07103",
          "dolly-05608",
          "dolly-07788",
          "dolly-11310",
          "dolly-02097",
          "dolly-03614",
          "dolly-13505",
          "dolly-02580",
          "dolly-08884",
          "dolly-12659",
          "dolly-00420",
          "dolly-11014",
          "dolly-08008",
          "dolly-02186",
          "dolly-00275",
          "dolly-08512",
          "dolly-14060",
          "dolly-01461",
          "dolly-02223",
          "dolly-04949",
          "dolly-08689",
          "dolly-08574",
          "dolly-08406",
          "dolly-04141",
          "dolly-03209",
          "dolly-06227",
          "dolly-11078",
          "dolly-09778",
          "dolly-04856",
          "dolly-13779",
          "dolly-06595",
          "dolly-08936",
          "dolly-09344",
          "dolly-05605",
          "dolly-08340",
          "dolly-04589",
          "dolly-04686",
          "dolly-14700",
          "dolly-03696",
          "dolly-03914",
          "dolly-11987",
          "dolly-01939",
          "dolly-05628",
          "dolly-13339",
          "dolly-08911",
          "dolly-03239",
          "dolly-13445",
          "dolly-02139",
          "dolly-14265",
          "dolly-13610",
          "dolly-07427",
          "dolly-09563",
          "dolly-02451",
          "dolly-13544",
          "dolly-06824",
          "dolly-05312",
          "dolly-10992",
          "dolly-06932",
          "dolly-08607",
          "dolly-05388",
          "dolly-11386",
          "dolly-02069",
          "dolly-09439",
          "dolly-00148",
          "dolly-08211",
          "dolly-12186",
          "dolly-03319",
          "dolly-07407",
          "dolly-10389",
          "dolly-03916",
          "dolly-08222",
          "dolly-14947",
          "dolly-03624",
          "dolly-09330",
          "dolly-11182",
          "dolly-02059",
          "dolly-02916",
          "dolly-09816",
          "dolly-05355",
          "dolly-06970",
          "dolly-05634",
          "dolly-02500",
          "dolly-11314",
          "dolly-13235",
          "dolly-04223"
        ]
      }
    }
  },
  "grouped_p_value_without_severe_repetition_method": "exclude whole answers whose answer-internal adjacent-token-pair repetition ratio (1 - unique pairs / all pairs) is strictly greater than 0.5; prompts excluded from repetition assessment; filter each label independently; retain original answer order, then concatenate teacher-tokenizer answer IDs without separators; exact disjoint blocks, first token context only; no token-pair deduplication within retained blocks; incomplete tail discarded; ordinary median of block p-values (mean of the middle two for even counts)",
  "per_group_p_value_without_severe_repetition_files": {
    "kgw": "/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta3_new1_qwen2_5_0_5b_dolly15k_test.nonrepetitive_grouped_p_values.json",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.nonrepetitive_grouped_p_values.json"
  },
  "evaluated_at": "2026-10-19T10:21:10+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta3_new1_qwen2_5_0_5b_dolly15k_test.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-10-19T10:25:24+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.647688
- 实际检测配置：`{"gamma": 0.5, "hash_key": 15485863, "seeding": "simple_1 (hash_key * previous_token_id)", "delta_by_label": {"kgw": 3.0, "clean": 2.0}}`
- ROUGE-L（同批 500 条原始 Dolly 回答作参考）：0.198494（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 原始 Dolly 参考文件：`/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl`
- ROUGE-L（同批 500 条 14B clean 教师回答作参考）：0.309174（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 14B clean 教师参考文件：`/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_clean_test.parquet`
- Best F1：0.685011（z 阈值 -1.5460413650478515，TPR 0.946000，FPR 0.816000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.000000 | 0.000000 | 0.000000 | None |
  | 5% | 0.050000 | 0.114000 | 0.195876 | 2.225394561056747 |
  | 10% | 0.100000 | 0.228000 | 0.343373 | 1.6859773678906163 |

两种逐条文本 p-value 统计（单侧正态近似；不是 AUROC 的显著性检验）：

去重规则：相同的 `(previous_token_id, token_id)` 只计一次；不修改回答文本。

| 数据 | 检测方式 | 有效样本 | p 均值 | p 中位数 | p≤0.01 | p≤0.05 | p≤0.10 |
|---|---|---:|---:|---:|---:|---:|---:|
| kgw | 原始 | 500/500 | 0.365777 | 0.238373 | 53 (10.60%) | 119 (23.80%) | 156 (31.20%) |
| kgw | token 对去重 | 500/500 | 0.347472 | 0.270591 | 19 (3.80%) | 80 (16.00%) | 140 (28.00%) |
| clean | 原始 | 500/500 | 0.538121 | 0.57157 | 22 (4.40%) | 54 (10.80%) | 73 (14.60%) |
| clean | token 对去重 | 500/500 | 0.537418 | 0.555154 | 5 (1.00%) | 25 (5.00%) | 46 (9.20%) |

KGW 的小 p 占比是该理论阈值下的检出率，clean 的小 p 占比是实测误报率。p≤0.05 不保证实际 FPR=5%；去重可改善重复带来的失真，但不保证完全校准。空回答不做显著性检验，p=null，并排除在有效样本统计之外。

逐条 p-value：`/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.p_values.jsonl`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl`

固定 token 分组 p-value（普通中位数；p 越大表示原单侧检验证据越弱）：

按教师 tokenizer 编码回答并无分隔拼接，精确分组；每组首 token 仅作上下文，其余 token 用本项目原 KGW 绿表评分；不去重，尾部不足一组丢弃；各组 p 排序后取普通中位数（偶数组取中间两个 p 的算术平均）。

| 每组 token 数 | 计分 token 数 | KGW 组数 | KGW median p ↑ | clean 组数 | clean median p | KGW/clean 丢弃尾部 tokens |
|---:|---:|---:|---:|---:|---:|---:|
| 1000 | 999 | 124 | 0.0972842 | 159 | 0.865929 | 556/765 |
| 2000 | 1999 | 62 | 0.0210112 | 79 | 0.971358 | 556/1765 |
| 3000 | 2999 | 41 | 0.00451065 | 53 | 0.982134 | 1556/765 |
| 10000 | 9999 | 12 | 0.00010552 | 15 | 1 | 4556/9765 |
| 20000 | 19999 | 6 | 3.02847e-09 | 7 | 1 | 4556/19765 |
| 30000 | 29999 | 4 | 3.40648e-11 | 5 | 1 | 4556/9765 |

N/A 表示总 token 数不足一个完整组；组数为 1 或 2 时需结合逐组结果解释。极小 p 用科学计数法字符串保存，同时保留 log10(p)，避免浮点下溢为 0。

逐组 p-value 缓存：`/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.grouped_p_values.json`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.grouped_p_values.json`

剔除严重重复回答后的固定 token 分组 p-value（普通中位数）：

先独立筛选 KGW 和 clean：回答内部相邻 token 对重复比例严格大于 50% 时，剔除整条回答；prompt 不参与判断。保留回答按原顺序重新无分隔拼接，各组首 token 仅作上下文；组内不做 token 对去重，尾部不足一组丢弃。这是质量筛选补充指标，原始全样本统计另行保留。

| 数据 | 原回答数 | 剔除严重重复回答 | 保留回答数 | 原 tokens | 剔除 tokens | 保留 tokens |
|---|---:|---:|---:|---:|---:|---:|
| kgw | 500 | 11 (2.20%) | 489 | 124556 | 7546 | 117010 |
| clean | 500 | 88 (17.60%) | 412 | 159765 | 113883 | 45882 |

| 每组 token 数 | 计分 token 数 | KGW 组数 | KGW median p ↑ | clean 组数 | clean median p | KGW/clean 丢弃尾部 tokens |
|---:|---:|---:|---:|---:|---:|---:|
| 1000 | 999 | 117 | 0.0533105 | 45 | 0.636089 | 10/882 |
| 2000 | 1999 | 58 | 0.0258354 | 22 | 0.796038 | 1010/1882 |
| 3000 | 2999 | 39 | 0.00757776 | 15 | 0.738626 | 10/882 |
| 10000 | 9999 | 11 | 3.90689e-06 | 4 | 0.947597 | 7010/5882 |
| 20000 | 19999 | 5 | 2.09115e-11 | 2 | 0.978374 | 17010/5882 |
| 30000 | 29999 | 3 | 4.33976e-19 | 1 | 0.999568 | 27010/15882 |

N/A 表示筛选后不足一个完整组。各组 p 取普通中位数，偶数组取中间两个 p 的算术平均；组数较少时请结合逐组缓存解释。

剔除严重重复回答后的逐组 p-value 缓存：`/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.nonrepetitive_grouped_p_values.json`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.nonrepetitive_grouped_p_values.json`

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.6476880000000005,
  "best_f1": {
    "threshold": -1.5460413650478515,
    "fpr": 0.816,
    "tpr": 0.946,
    "precision": 0.5368898978433598,
    "f1": 0.6850108616944243,
    "tp": 473,
    "fp": 408,
    "tn": 92,
    "fn": 27
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
      "threshold": 2.225394561056747,
      "fpr": 0.05,
      "tpr": 0.114,
      "precision": 0.6951219512195121,
      "f1": 0.19587628865979384,
      "tp": 57,
      "fp": 25,
      "tn": 475,
      "fn": 443,
      "target_fpr": 0.05
    },
    "10%": {
      "threshold": 1.6859773678906163,
      "fpr": 0.1,
      "tpr": 0.228,
      "precision": 0.6951219512195121,
      "f1": 0.34337349397590367,
      "tp": 114,
      "fp": 50,
      "tn": 450,
      "fn": 386,
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
      "clean": 2.0
    }
  },
  "rouge_l_dolly": {
    "mean": 0.19849387557587408,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.jsonl",
    "reference_file": "/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl",
    "reference_source": "databricks/databricks-dolly-15k:response",
    "metric": "rougeL",
    "measure": "fmeasure",
    "use_stemmer": true,
    "aggregation": "unweighted mean of per-sample ROUGE-L F1"
  },
  "rouge_l_teacher_clean": {
    "mean": 0.3091744425525882,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.jsonl",
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
        "mean": 0.36577704616420137,
        "median": 0.2383728596628124,
        "min": 6.834897526731109e-14,
        "max": 0.9999999683624243,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 53,
            "fraction": 0.106
          },
          "5%": {
            "alpha": 0.05,
            "count": 119,
            "fraction": 0.238
          },
          "10%": {
            "alpha": 0.1,
            "count": 156,
            "fraction": 0.312
          }
        }
      },
      "deduplicated": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.3474721954408633,
        "median": 0.2705911687912894,
        "min": 9.802720950622567e-05,
        "max": 0.9947064313329715,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 19,
            "fraction": 0.038
          },
          "5%": {
            "alpha": 0.05,
            "count": 80,
            "fraction": 0.16
          },
          "10%": {
            "alpha": 0.1,
            "count": 140,
            "fraction": 0.28
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
    "kgw": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.p_values.jsonl",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl"
  },
  "grouped_p_values": {
    "kgw": {
      "aggregation": "ordinary_median",
      "num_answers": 500,
      "total_answer_tokens": 124556,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 124,
          "total_answer_tokens": 124556,
          "discarded_tail_tokens": 556,
          "median_p_value": 0.09728418407710798,
          "median_log10_p_value": -1.0119577591802715,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 62,
          "total_answer_tokens": 124556,
          "discarded_tail_tokens": 556,
          "median_p_value": 0.021011201066677636,
          "median_log10_p_value": -1.677549121238903,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 41,
          "total_answer_tokens": 124556,
          "discarded_tail_tokens": 1556,
          "median_p_value": 0.004510647390091074,
          "median_log10_p_value": -2.345761121588415,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 12,
          "total_answer_tokens": 124556,
          "discarded_tail_tokens": 4556,
          "median_p_value": 0.00010552043060425137,
          "median_log10_p_value": -3.976663445203648,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 6,
          "total_answer_tokens": 124556,
          "discarded_tail_tokens": 4556,
          "median_p_value": 3.0284724385078573e-09,
          "median_log10_p_value": -8.518776374405638,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 4,
          "total_answer_tokens": 124556,
          "discarded_tail_tokens": 4556,
          "median_p_value": 3.406482841307593e-11,
          "median_log10_p_value": -10.467693794290765,
          "status": "ok"
        }
      }
    },
    "clean": {
      "aggregation": "ordinary_median",
      "num_answers": 500,
      "total_answer_tokens": 159765,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 159,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 765,
          "median_p_value": 0.8659288977499955,
          "median_log10_p_value": -0.06251776685396769,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 79,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 1765,
          "median_p_value": 0.971357711016285,
          "median_log10_p_value": -0.012620807875598238,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 53,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 765,
          "median_p_value": 0.9821335190767914,
          "median_log10_p_value": -0.007829466737979084,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 15,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 9765,
          "median_p_value": 0.9999999999999984,
          "median_log10_p_value": -6.750292265873014e-16,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 7,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 19765,
          "median_p_value": 1.0,
          "median_log10_p_value": 0.0,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 5,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 9765,
          "median_p_value": 1.0,
          "median_log10_p_value": 0.0,
          "status": "ok"
        }
      }
    }
  },
  "grouped_p_value_method": "teacher-tokenizer answer IDs concatenated without separators; exact disjoint blocks; first token of each block is context only; no repetition deduplication; incomplete tail discarded; ordinary median of block p-values (arithmetic mean of the two middle p-values for even group counts)",
  "per_group_p_value_files": {
    "kgw": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.grouped_p_values.json",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.grouped_p_values.json"
  },
  "grouped_p_values_without_severe_repetition": {
    "kgw": {
      "aggregation": "ordinary_median",
      "num_answers": 489,
      "total_answer_tokens": 117010,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 117,
          "total_answer_tokens": 117010,
          "discarded_tail_tokens": 10,
          "median_p_value": 0.05331051692833846,
          "median_log10_p_value": -1.2731871062944602,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 58,
          "total_answer_tokens": 117010,
          "discarded_tail_tokens": 1010,
          "median_p_value": 0.025835438978909653,
          "median_log10_p_value": -1.587784154807367,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 39,
          "total_answer_tokens": 117010,
          "discarded_tail_tokens": 10,
          "median_p_value": 0.007577755382079972,
          "median_log10_p_value": -2.12045941831776,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 11,
          "total_answer_tokens": 117010,
          "discarded_tail_tokens": 7010,
          "median_p_value": 3.906894729933383e-06,
          "median_log10_p_value": -5.408168290547667,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 5,
          "total_answer_tokens": 117010,
          "discarded_tail_tokens": 17010,
          "median_p_value": 2.0911493971713533e-11,
          "median_log10_p_value": -10.679614938942542,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 3,
          "total_answer_tokens": 117010,
          "discarded_tail_tokens": 27010,
          "median_p_value": 4.339760379368728e-19,
          "median_log10_p_value": -18.36253424947156,
          "status": "ok"
        }
      },
      "filtering": {
        "repetition_threshold": 0.5,
        "comparison": ">",
        "scope": "answer-internal adjacent token pairs; prompt excluded",
        "num_answers_before": 500,
        "num_answers_retained": 489,
        "num_answers_removed": 11,
        "fraction_answers_removed": 0.022,
        "total_answer_tokens_before": 124556,
        "total_answer_tokens_retained": 117010,
        "total_answer_tokens_removed": 7546,
        "removed_answer_ids": [
          "dolly-00423",
          "dolly-07103",
          "dolly-02678",
          "dolly-00143",
          "dolly-04773",
          "dolly-11030",
          "dolly-13445",
          "dolly-06932",
          "dolly-08607",
          "dolly-12001",
          "dolly-01356"
        ]
      }
    },
    "clean": {
      "aggregation": "ordinary_median",
      "num_answers": 412,
      "total_answer_tokens": 45882,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 45,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 882,
          "median_p_value": 0.6360891449864364,
          "median_log10_p_value": -0.1964820156995508,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 22,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 1882,
          "median_p_value": 0.7960378878131416,
          "median_log10_p_value": -0.09906626131183685,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 15,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 882,
          "median_p_value": 0.7386263221105359,
          "median_log10_p_value": -0.13157521964243946,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 4,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 5882,
          "median_p_value": 0.947596846602552,
          "median_log10_p_value": -0.0233763931850151,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 2,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 5882,
          "median_p_value": 0.9783739864832501,
          "median_log10_p_value": -0.009495103065976066,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 1,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 15882,
          "median_p_value": 0.9995678964162934,
          "median_log10_p_value": -0.00018770075802065225,
          "status": "ok"
        }
      },
      "filtering": {
        "repetition_threshold": 0.5,
        "comparison": ">",
        "scope": "answer-internal adjacent token pairs; prompt excluded",
        "num_answers_before": 500,
        "num_answers_retained": 412,
        "num_answers_removed": 88,
        "fraction_answers_removed": 0.176,
        "total_answer_tokens_before": 159765,
        "total_answer_tokens_retained": 45882,
        "total_answer_tokens_removed": 113883,
        "removed_answer_ids": [
          "dolly-00135",
          "dolly-12241",
          "dolly-07923",
          "dolly-07103",
          "dolly-05608",
          "dolly-07788",
          "dolly-11310",
          "dolly-02097",
          "dolly-03614",
          "dolly-13505",
          "dolly-02580",
          "dolly-08884",
          "dolly-12659",
          "dolly-00420",
          "dolly-11014",
          "dolly-08008",
          "dolly-02186",
          "dolly-00275",
          "dolly-08512",
          "dolly-14060",
          "dolly-01461",
          "dolly-02223",
          "dolly-04949",
          "dolly-08689",
          "dolly-08574",
          "dolly-08406",
          "dolly-04141",
          "dolly-03209",
          "dolly-06227",
          "dolly-11078",
          "dolly-09778",
          "dolly-04856",
          "dolly-13779",
          "dolly-06595",
          "dolly-08936",
          "dolly-09344",
          "dolly-05605",
          "dolly-08340",
          "dolly-04589",
          "dolly-04686",
          "dolly-14700",
          "dolly-03696",
          "dolly-03914",
          "dolly-11987",
          "dolly-01939",
          "dolly-05628",
          "dolly-13339",
          "dolly-08911",
          "dolly-03239",
          "dolly-13445",
          "dolly-02139",
          "dolly-14265",
          "dolly-13610",
          "dolly-07427",
          "dolly-09563",
          "dolly-02451",
          "dolly-13544",
          "dolly-06824",
          "dolly-05312",
          "dolly-10992",
          "dolly-06932",
          "dolly-08607",
          "dolly-05388",
          "dolly-11386",
          "dolly-02069",
          "dolly-09439",
          "dolly-00148",
          "dolly-08211",
          "dolly-12186",
          "dolly-03319",
          "dolly-07407",
          "dolly-10389",
          "dolly-03916",
          "dolly-08222",
          "dolly-14947",
          "dolly-03624",
          "dolly-09330",
          "dolly-11182",
          "dolly-02059",
          "dolly-02916",
          "dolly-09816",
          "dolly-05355",
          "dolly-06970",
          "dolly-05634",
          "dolly-02500",
          "dolly-11314",
          "dolly-13235",
          "dolly-04223"
        ]
      }
    }
  },
  "grouped_p_value_without_severe_repetition_method": "exclude whole answers whose answer-internal adjacent-token-pair repetition ratio (1 - unique pairs / all pairs) is strictly greater than 0.5; prompts excluded from repetition assessment; filter each label independently; retain original answer order, then concatenate teacher-tokenizer answer IDs without separators; exact disjoint blocks, first token context only; no token-pair deduplication within retained blocks; incomplete tail discarded; ordinary median of block p-values (mean of the middle two for even counts)",
  "per_group_p_value_without_severe_repetition_files": {
    "kgw": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.nonrepetitive_grouped_p_values.json",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.nonrepetitive_grouped_p_values.json"
  },
  "evaluated_at": "2026-10-19T10:25:24+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-10-19T10:26:51+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.416208
- 实际检测配置：`{"gamma": 0.5, "hash_key": 15485863, "seeding": "simple_1 (hash_key * previous_token_id)", "delta_by_label": {"kgw": 3.0, "clean": 2.0}}`
- ROUGE-L（同批 500 条原始 Dolly 回答作参考）：0.175276（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 原始 Dolly 参考文件：`/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl`
- ROUGE-L（同批 500 条 14B clean 教师回答作参考）：0.270563（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 14B clean 教师参考文件：`/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_clean_test.parquet`
- Best F1：0.669388（z 阈值 -6.685065756345757，TPR 0.984000，FPR 0.956000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.010000 | 0.004000 | 0.007890 | 9.593834825900782 |
  | 5% | 0.050000 | 0.024000 | 0.044693 | 2.2223355980148636 |
  | 10% | 0.100000 | 0.052000 | 0.090278 | 1.6994116628998401 |

两种逐条文本 p-value 统计（单侧正态近似；不是 AUROC 的显著性检验）：

去重规则：相同的 `(previous_token_id, token_id)` 只计一次；不修改回答文本。

| 数据 | 检测方式 | 有效样本 | p 均值 | p 中位数 | p≤0.01 | p≤0.05 | p≤0.10 |
|---|---|---:|---:|---:|---:|---:|---:|
| kgw | 原始 | 500/500 | 0.639621 | 0.716527 | 8 (1.60%) | 32 (6.40%) | 50 (10.00%) |
| kgw | token 对去重 | 500/500 | 0.635533 | 0.70537 | 1 (0.20%) | 12 (2.40%) | 34 (6.80%) |
| clean | 原始 | 500/500 | 0.538121 | 0.57157 | 22 (4.40%) | 54 (10.80%) | 73 (14.60%) |
| clean | token 对去重 | 500/500 | 0.537418 | 0.555154 | 5 (1.00%) | 25 (5.00%) | 46 (9.20%) |

KGW 的小 p 占比是该理论阈值下的检出率，clean 的小 p 占比是实测误报率。p≤0.05 不保证实际 FPR=5%；去重可改善重复带来的失真，但不保证完全校准。空回答不做显著性检验，p=null，并排除在有效样本统计之外。

逐条 p-value：`/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new_strength3.p_values.jsonl`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl`

固定 token 分组 p-value（普通中位数；p 越大表示原单侧检验证据越弱）：

按教师 tokenizer 编码回答并无分隔拼接，精确分组；每组首 token 仅作上下文，其余 token 用本项目原 KGW 绿表评分；不去重，尾部不足一组丢弃；各组 p 排序后取普通中位数（偶数组取中间两个 p 的算术平均）。

| 每组 token 数 | 计分 token 数 | KGW 组数 | KGW median p ↑ | clean 组数 | clean median p | KGW/clean 丢弃尾部 tokens |
|---:|---:|---:|---:|---:|---:|---:|
| 1000 | 999 | 155 | 0.953214 | 159 | 0.865929 | 939/765 |
| 2000 | 1999 | 77 | 0.994946 | 79 | 0.971358 | 1939/1765 |
| 3000 | 2999 | 51 | 0.998542 | 53 | 0.982134 | 2939/765 |
| 10000 | 9999 | 15 | 1 | 15 | 1 | 5939/9765 |
| 20000 | 19999 | 7 | 1 | 7 | 1 | 15939/19765 |
| 30000 | 29999 | 5 | 1 | 5 | 1 | 5939/9765 |

N/A 表示总 token 数不足一个完整组；组数为 1 或 2 时需结合逐组结果解释。极小 p 用科学计数法字符串保存，同时保留 log10(p)，避免浮点下溢为 0。

逐组 p-value 缓存：`/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new_strength3.grouped_p_values.json`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.grouped_p_values.json`

剔除严重重复回答后的固定 token 分组 p-value（普通中位数）：

先独立筛选 KGW 和 clean：回答内部相邻 token 对重复比例严格大于 50% 时，剔除整条回答；prompt 不参与判断。保留回答按原顺序重新无分隔拼接，各组首 token 仅作上下文；组内不做 token 对去重，尾部不足一组丢弃。这是质量筛选补充指标，原始全样本统计另行保留。

| 数据 | 原回答数 | 剔除严重重复回答 | 保留回答数 | 原 tokens | 剔除 tokens | 保留 tokens |
|---|---:|---:|---:|---:|---:|---:|
| kgw | 500 | 35 (7.00%) | 465 | 155939 | 37582 | 118357 |
| clean | 500 | 88 (17.60%) | 412 | 159765 | 113883 | 45882 |

| 每组 token 数 | 计分 token 数 | KGW 组数 | KGW median p ↑ | clean 组数 | clean median p | KGW/clean 丢弃尾部 tokens |
|---:|---:|---:|---:|---:|---:|---:|
| 1000 | 999 | 118 | 0.939464 | 45 | 0.636089 | 357/882 |
| 2000 | 1999 | 59 | 0.974165 | 22 | 0.796038 | 357/1882 |
| 3000 | 2999 | 39 | 0.994984 | 15 | 0.738626 | 1357/882 |
| 10000 | 9999 | 11 | 0.999999 | 4 | 0.947597 | 8357/5882 |
| 20000 | 19999 | 5 | 1 | 2 | 0.978374 | 18357/5882 |
| 30000 | 29999 | 3 | 1 | 1 | 0.999568 | 28357/15882 |

N/A 表示筛选后不足一个完整组。各组 p 取普通中位数，偶数组取中间两个 p 的算术平均；组数较少时请结合逐组缓存解释。

剔除严重重复回答后的逐组 p-value 缓存：`/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new_strength3.nonrepetitive_grouped_p_values.json`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.nonrepetitive_grouped_p_values.json`

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.416208,
  "best_f1": {
    "threshold": -6.685065756345757,
    "fpr": 0.956,
    "tpr": 0.984,
    "precision": 0.5072164948453608,
    "f1": 0.6693877551020408,
    "tp": 492,
    "fp": 478,
    "tn": 22,
    "fn": 8
  },
  "tpr_at_fpr": {
    "1%": {
      "threshold": 9.593834825900782,
      "fpr": 0.01,
      "tpr": 0.004,
      "precision": 0.2857142857142857,
      "f1": 0.007889546351084811,
      "tp": 2,
      "fp": 5,
      "tn": 495,
      "fn": 498,
      "target_fpr": 0.01
    },
    "5%": {
      "threshold": 2.2223355980148636,
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
      "threshold": 1.6994116628998401,
      "fpr": 0.1,
      "tpr": 0.052,
      "precision": 0.34210526315789475,
      "f1": 0.09027777777777778,
      "tp": 26,
      "fp": 50,
      "tn": 450,
      "fn": 474,
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
      "clean": 2.0
    }
  },
  "rouge_l_dolly": {
    "mean": 0.17527607072154583,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new_strength3.jsonl",
    "reference_file": "/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl",
    "reference_source": "databricks/databricks-dolly-15k:response",
    "metric": "rougeL",
    "measure": "fmeasure",
    "use_stemmer": true,
    "aggregation": "unweighted mean of per-sample ROUGE-L F1"
  },
  "rouge_l_teacher_clean": {
    "mean": 0.27056293657683556,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new_strength3.jsonl",
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
        "mean": 0.6396205720998028,
        "median": 0.7165273408147196,
        "min": 1.6759570266182036e-84,
        "max": 1.0,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 8,
            "fraction": 0.016
          },
          "5%": {
            "alpha": 0.05,
            "count": 32,
            "fraction": 0.064
          },
          "10%": {
            "alpha": 0.1,
            "count": 50,
            "fraction": 0.1
          }
        }
      },
      "deduplicated": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.6355330807744789,
        "median": 0.7053699393912358,
        "min": 0.00921106272704951,
        "max": 0.9989289915261519,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 1,
            "fraction": 0.002
          },
          "5%": {
            "alpha": 0.05,
            "count": 12,
            "fraction": 0.024
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
    "kgw": "/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new_strength3.p_values.jsonl",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl"
  },
  "grouped_p_values": {
    "kgw": {
      "aggregation": "ordinary_median",
      "num_answers": 500,
      "total_answer_tokens": 155939,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 155,
          "total_answer_tokens": 155939,
          "discarded_tail_tokens": 939,
          "median_p_value": 0.9532136797396964,
          "median_log10_p_value": -0.02080973364321328,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 77,
          "total_answer_tokens": 155939,
          "discarded_tail_tokens": 1939,
          "median_p_value": 0.9949461262550343,
          "median_log10_p_value": -0.00220043453426638,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 51,
          "total_answer_tokens": 155939,
          "discarded_tail_tokens": 2939,
          "median_p_value": 0.998541992279534,
          "median_log10_p_value": -0.0006336667654240838,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 15,
          "total_answer_tokens": 155939,
          "discarded_tail_tokens": 5939,
          "median_p_value": 0.9999999992771296,
          "median_log10_p_value": -3.139386390720775e-10,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 7,
          "total_answer_tokens": 155939,
          "discarded_tail_tokens": 15939,
          "median_p_value": 1.0,
          "median_log10_p_value": 0.0,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 5,
          "total_answer_tokens": 155939,
          "discarded_tail_tokens": 5939,
          "median_p_value": 1.0,
          "median_log10_p_value": 0.0,
          "status": "ok"
        }
      }
    },
    "clean": {
      "aggregation": "ordinary_median",
      "num_answers": 500,
      "total_answer_tokens": 159765,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 159,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 765,
          "median_p_value": 0.8659288977499955,
          "median_log10_p_value": -0.06251776685396769,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 79,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 1765,
          "median_p_value": 0.971357711016285,
          "median_log10_p_value": -0.012620807875598238,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 53,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 765,
          "median_p_value": 0.9821335190767914,
          "median_log10_p_value": -0.007829466737979084,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 15,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 9765,
          "median_p_value": 0.9999999999999984,
          "median_log10_p_value": -6.750292265873014e-16,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 7,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 19765,
          "median_p_value": 1.0,
          "median_log10_p_value": 0.0,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 5,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 9765,
          "median_p_value": 1.0,
          "median_log10_p_value": 0.0,
          "status": "ok"
        }
      }
    }
  },
  "grouped_p_value_method": "teacher-tokenizer answer IDs concatenated without separators; exact disjoint blocks; first token of each block is context only; no repetition deduplication; incomplete tail discarded; ordinary median of block p-values (arithmetic mean of the two middle p-values for even group counts)",
  "per_group_p_value_files": {
    "kgw": "/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new_strength3.grouped_p_values.json",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.grouped_p_values.json"
  },
  "grouped_p_values_without_severe_repetition": {
    "kgw": {
      "aggregation": "ordinary_median",
      "num_answers": 465,
      "total_answer_tokens": 118357,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 118,
          "total_answer_tokens": 118357,
          "discarded_tail_tokens": 357,
          "median_p_value": 0.939464203891651,
          "median_log10_p_value": -0.02711976303391753,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 59,
          "total_answer_tokens": 118357,
          "discarded_tail_tokens": 357,
          "median_p_value": 0.9741645610210904,
          "median_log10_p_value": -0.011367673607334343,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 39,
          "total_answer_tokens": 118357,
          "discarded_tail_tokens": 1357,
          "median_p_value": 0.994984011891031,
          "median_log10_p_value": -0.0021838977500412957,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 11,
          "total_answer_tokens": 118357,
          "discarded_tail_tokens": 8357,
          "median_p_value": 0.9999988787079404,
          "median_log10_p_value": -4.869712271251867e-07,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 5,
          "total_answer_tokens": 118357,
          "discarded_tail_tokens": 18357,
          "median_p_value": 0.9999999999903094,
          "median_log10_p_value": -4.208566145925575e-12,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 3,
          "total_answer_tokens": 118357,
          "discarded_tail_tokens": 28357,
          "median_p_value": 0.9999999999999941,
          "median_log10_p_value": -2.5554677863662184e-15,
          "status": "ok"
        }
      },
      "filtering": {
        "repetition_threshold": 0.5,
        "comparison": ">",
        "scope": "answer-internal adjacent token pairs; prompt excluded",
        "num_answers_before": 500,
        "num_answers_retained": 465,
        "num_answers_removed": 35,
        "fraction_answers_removed": 0.07,
        "total_answer_tokens_before": 155939,
        "total_answer_tokens_retained": 118357,
        "total_answer_tokens_removed": 37582,
        "removed_answer_ids": [
          "dolly-00423",
          "dolly-12156",
          "dolly-11025",
          "dolly-00720",
          "dolly-07788",
          "dolly-06622",
          "dolly-07239",
          "dolly-08709",
          "dolly-13505",
          "dolly-04362",
          "dolly-04421",
          "dolly-05394",
          "dolly-02844",
          "dolly-06920",
          "dolly-06595",
          "dolly-14358",
          "dolly-09918",
          "dolly-06771",
          "dolly-11987",
          "dolly-05628",
          "dolly-14970",
          "dolly-11030",
          "dolly-11445",
          "dolly-06895",
          "dolly-08607",
          "dolly-11386",
          "dolly-09439",
          "dolly-08451",
          "dolly-14465",
          "dolly-07407",
          "dolly-02816",
          "dolly-12001",
          "dolly-01356",
          "dolly-12236",
          "dolly-13235"
        ]
      }
    },
    "clean": {
      "aggregation": "ordinary_median",
      "num_answers": 412,
      "total_answer_tokens": 45882,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 45,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 882,
          "median_p_value": 0.6360891449864364,
          "median_log10_p_value": -0.1964820156995508,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 22,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 1882,
          "median_p_value": 0.7960378878131416,
          "median_log10_p_value": -0.09906626131183685,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 15,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 882,
          "median_p_value": 0.7386263221105359,
          "median_log10_p_value": -0.13157521964243946,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 4,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 5882,
          "median_p_value": 0.947596846602552,
          "median_log10_p_value": -0.0233763931850151,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 2,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 5882,
          "median_p_value": 0.9783739864832501,
          "median_log10_p_value": -0.009495103065976066,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 1,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 15882,
          "median_p_value": 0.9995678964162934,
          "median_log10_p_value": -0.00018770075802065225,
          "status": "ok"
        }
      },
      "filtering": {
        "repetition_threshold": 0.5,
        "comparison": ">",
        "scope": "answer-internal adjacent token pairs; prompt excluded",
        "num_answers_before": 500,
        "num_answers_retained": 412,
        "num_answers_removed": 88,
        "fraction_answers_removed": 0.176,
        "total_answer_tokens_before": 159765,
        "total_answer_tokens_retained": 45882,
        "total_answer_tokens_removed": 113883,
        "removed_answer_ids": [
          "dolly-00135",
          "dolly-12241",
          "dolly-07923",
          "dolly-07103",
          "dolly-05608",
          "dolly-07788",
          "dolly-11310",
          "dolly-02097",
          "dolly-03614",
          "dolly-13505",
          "dolly-02580",
          "dolly-08884",
          "dolly-12659",
          "dolly-00420",
          "dolly-11014",
          "dolly-08008",
          "dolly-02186",
          "dolly-00275",
          "dolly-08512",
          "dolly-14060",
          "dolly-01461",
          "dolly-02223",
          "dolly-04949",
          "dolly-08689",
          "dolly-08574",
          "dolly-08406",
          "dolly-04141",
          "dolly-03209",
          "dolly-06227",
          "dolly-11078",
          "dolly-09778",
          "dolly-04856",
          "dolly-13779",
          "dolly-06595",
          "dolly-08936",
          "dolly-09344",
          "dolly-05605",
          "dolly-08340",
          "dolly-04589",
          "dolly-04686",
          "dolly-14700",
          "dolly-03696",
          "dolly-03914",
          "dolly-11987",
          "dolly-01939",
          "dolly-05628",
          "dolly-13339",
          "dolly-08911",
          "dolly-03239",
          "dolly-13445",
          "dolly-02139",
          "dolly-14265",
          "dolly-13610",
          "dolly-07427",
          "dolly-09563",
          "dolly-02451",
          "dolly-13544",
          "dolly-06824",
          "dolly-05312",
          "dolly-10992",
          "dolly-06932",
          "dolly-08607",
          "dolly-05388",
          "dolly-11386",
          "dolly-02069",
          "dolly-09439",
          "dolly-00148",
          "dolly-08211",
          "dolly-12186",
          "dolly-03319",
          "dolly-07407",
          "dolly-10389",
          "dolly-03916",
          "dolly-08222",
          "dolly-14947",
          "dolly-03624",
          "dolly-09330",
          "dolly-11182",
          "dolly-02059",
          "dolly-02916",
          "dolly-09816",
          "dolly-05355",
          "dolly-06970",
          "dolly-05634",
          "dolly-02500",
          "dolly-11314",
          "dolly-13235",
          "dolly-04223"
        ]
      }
    }
  },
  "grouped_p_value_without_severe_repetition_method": "exclude whole answers whose answer-internal adjacent-token-pair repetition ratio (1 - unique pairs / all pairs) is strictly greater than 0.5; prompts excluded from repetition assessment; filter each label independently; retain original answer order, then concatenate teacher-tokenizer answer IDs without separators; exact disjoint blocks, first token context only; no token-pair deduplication within retained blocks; incomplete tail discarded; ordinary median of block p-values (mean of the middle two for even counts)",
  "per_group_p_value_without_severe_repetition_files": {
    "kgw": "/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new_strength3.nonrepetitive_grouped_p_values.json",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.nonrepetitive_grouped_p_values.json"
  },
  "evaluated_at": "2026-10-19T10:26:51+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new_strength3.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-10-19T10:27:30+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.433434
- 实际检测配置：`{"gamma": 0.5, "hash_key": 15485863, "seeding": "simple_1 (hash_key * previous_token_id)", "delta_by_label": {"kgw": 3.0, "clean": 2.0}}`
- ROUGE-L（同批 500 条原始 Dolly 回答作参考）：0.185418（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 原始 Dolly 参考文件：`/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl`
- ROUGE-L（同批 500 条 14B clean 教师回答作参考）：0.286763（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 14B clean 教师参考文件：`/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_clean_test.parquet`
- Best F1：0.672087（z 阈值 -7.654655446197432，TPR 0.992000，FPR 0.960000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.002000 | 0.002000 | 0.003984 | 36.23203577866784 |
  | 5% | 0.046000 | 0.026000 | 0.048507 | 2.2519414081056586 |
  | 10% | 0.100000 | 0.050000 | 0.086957 | 1.7075311565539322 |

两种逐条文本 p-value 统计（单侧正态近似；不是 AUROC 的显著性检验）：

去重规则：相同的 `(previous_token_id, token_id)` 只计一次；不修改回答文本。

| 数据 | 检测方式 | 有效样本 | p 均值 | p 中位数 | p≤0.01 | p≤0.05 | p≤0.10 |
|---|---|---:|---:|---:|---:|---:|---:|
| kgw | 原始 | 500/500 | 0.619542 | 0.685885 | 11 (2.20%) | 27 (5.40%) | 44 (8.80%) |
| kgw | token 对去重 | 500/500 | 0.618146 | 0.665092 | 3 (0.60%) | 11 (2.20%) | 22 (4.40%) |
| clean | 原始 | 500/500 | 0.538121 | 0.57157 | 22 (4.40%) | 54 (10.80%) | 73 (14.60%) |
| clean | token 对去重 | 500/500 | 0.537418 | 0.555154 | 5 (1.00%) | 25 (5.00%) | 46 (9.20%) |

KGW 的小 p 占比是该理论阈值下的检出率，clean 的小 p 占比是实测误报率。p≤0.05 不保证实际 FPR=5%；去重可改善重复带来的失真，但不保证完全校准。空回答不做显著性检验，p=null，并排除在有效样本统计之外。

逐条 p-value：`/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new.p_values.jsonl`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl`

固定 token 分组 p-value（普通中位数；p 越大表示原单侧检验证据越弱）：

按教师 tokenizer 编码回答并无分隔拼接，精确分组；每组首 token 仅作上下文，其余 token 用本项目原 KGW 绿表评分；不去重，尾部不足一组丢弃；各组 p 排序后取普通中位数（偶数组取中间两个 p 的算术平均）。

| 每组 token 数 | 计分 token 数 | KGW 组数 | KGW median p ↑ | clean 组数 | clean median p | KGW/clean 丢弃尾部 tokens |
|---:|---:|---:|---:|---:|---:|---:|
| 1000 | 999 | 141 | 0.922739 | 159 | 0.865929 | 647/765 |
| 2000 | 1999 | 70 | 0.979091 | 79 | 0.971358 | 1647/1765 |
| 3000 | 2999 | 47 | 0.996744 | 53 | 0.982134 | 647/765 |
| 10000 | 9999 | 14 | 0.999998 | 15 | 1 | 1647/9765 |
| 20000 | 19999 | 7 | 1 | 7 | 1 | 1647/19765 |
| 30000 | 29999 | 4 | 1 | 5 | 1 | 21647/9765 |

N/A 表示总 token 数不足一个完整组；组数为 1 或 2 时需结合逐组结果解释。极小 p 用科学计数法字符串保存，同时保留 log10(p)，避免浮点下溢为 0。

逐组 p-value 缓存：`/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new.grouped_p_values.json`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.grouped_p_values.json`

剔除严重重复回答后的固定 token 分组 p-value（普通中位数）：

先独立筛选 KGW 和 clean：回答内部相邻 token 对重复比例严格大于 50% 时，剔除整条回答；prompt 不参与判断。保留回答按原顺序重新无分隔拼接，各组首 token 仅作上下文；组内不做 token 对去重，尾部不足一组丢弃。这是质量筛选补充指标，原始全样本统计另行保留。

| 数据 | 原回答数 | 剔除严重重复回答 | 保留回答数 | 原 tokens | 剔除 tokens | 保留 tokens |
|---|---:|---:|---:|---:|---:|---:|
| kgw | 500 | 21 (4.20%) | 479 | 141647 | 22772 | 118875 |
| clean | 500 | 88 (17.60%) | 412 | 159765 | 113883 | 45882 |

| 每组 token 数 | 计分 token 数 | KGW 组数 | KGW median p ↑ | clean 组数 | clean median p | KGW/clean 丢弃尾部 tokens |
|---:|---:|---:|---:|---:|---:|---:|
| 1000 | 999 | 118 | 0.879126 | 45 | 0.636089 | 875/882 |
| 2000 | 1999 | 59 | 0.957484 | 22 | 0.796038 | 875/1882 |
| 3000 | 2999 | 39 | 0.974642 | 15 | 0.738626 | 1875/882 |
| 10000 | 9999 | 11 | 0.999847 | 4 | 0.947597 | 8875/5882 |
| 20000 | 19999 | 5 | 1 | 2 | 0.978374 | 18875/5882 |
| 30000 | 29999 | 3 | 1 | 1 | 0.999568 | 28875/15882 |

N/A 表示筛选后不足一个完整组。各组 p 取普通中位数，偶数组取中间两个 p 的算术平均；组数较少时请结合逐组缓存解释。

剔除严重重复回答后的逐组 p-value 缓存：`/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new.nonrepetitive_grouped_p_values.json`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.nonrepetitive_grouped_p_values.json`

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.4334339999999997,
  "best_f1": {
    "threshold": -7.654655446197432,
    "fpr": 0.96,
    "tpr": 0.992,
    "precision": 0.5081967213114754,
    "f1": 0.6720867208672088,
    "tp": 496,
    "fp": 480,
    "tn": 20,
    "fn": 4
  },
  "tpr_at_fpr": {
    "1%": {
      "threshold": 36.23203577866784,
      "fpr": 0.002,
      "tpr": 0.002,
      "precision": 0.5,
      "f1": 0.00398406374501992,
      "tp": 1,
      "fp": 1,
      "tn": 499,
      "fn": 499,
      "target_fpr": 0.01
    },
    "5%": {
      "threshold": 2.2519414081056586,
      "fpr": 0.046,
      "tpr": 0.026,
      "precision": 0.3611111111111111,
      "f1": 0.04850746268656716,
      "tp": 13,
      "fp": 23,
      "tn": 477,
      "fn": 487,
      "target_fpr": 0.05
    },
    "10%": {
      "threshold": 1.7075311565539322,
      "fpr": 0.1,
      "tpr": 0.05,
      "precision": 0.3333333333333333,
      "f1": 0.08695652173913045,
      "tp": 25,
      "fp": 50,
      "tn": 450,
      "fn": 475,
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
      "clean": 2.0
    }
  },
  "rouge_l_dolly": {
    "mean": 0.185418046008631,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new.jsonl",
    "reference_file": "/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl",
    "reference_source": "databricks/databricks-dolly-15k:response",
    "metric": "rougeL",
    "measure": "fmeasure",
    "use_stemmer": true,
    "aggregation": "unweighted mean of per-sample ROUGE-L F1"
  },
  "rouge_l_teacher_clean": {
    "mean": 0.2867632931442953,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new.jsonl",
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
        "mean": 0.6195424620785832,
        "median": 0.6858849758356487,
        "min": 9.53201291013277e-288,
        "max": 1.0,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 11,
            "fraction": 0.022
          },
          "5%": {
            "alpha": 0.05,
            "count": 27,
            "fraction": 0.054
          },
          "10%": {
            "alpha": 0.1,
            "count": 44,
            "fraction": 0.088
          }
        }
      },
      "deduplicated": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.618146070028407,
        "median": 0.6650923212002917,
        "min": 0.004024651677903384,
        "max": 0.9998630818329007,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 3,
            "fraction": 0.006
          },
          "5%": {
            "alpha": 0.05,
            "count": 11,
            "fraction": 0.022
          },
          "10%": {
            "alpha": 0.1,
            "count": 22,
            "fraction": 0.044
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
    "kgw": "/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new.p_values.jsonl",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl"
  },
  "grouped_p_values": {
    "kgw": {
      "aggregation": "ordinary_median",
      "num_answers": 500,
      "total_answer_tokens": 141647,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 141,
          "total_answer_tokens": 141647,
          "discarded_tail_tokens": 647,
          "median_p_value": 0.9227386896857669,
          "median_log10_p_value": -0.03492126939122037,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 70,
          "total_answer_tokens": 141647,
          "discarded_tail_tokens": 1647,
          "median_p_value": 0.9790911982428734,
          "median_log10_p_value": -0.009176853601383308,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 47,
          "total_answer_tokens": 141647,
          "discarded_tail_tokens": 647,
          "median_p_value": 0.996743879934514,
          "median_log10_p_value": -0.001416422250799275,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 14,
          "total_answer_tokens": 141647,
          "discarded_tail_tokens": 1647,
          "median_p_value": 0.9999978203853606,
          "median_log10_p_value": -9.465956421558859e-07,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 7,
          "total_answer_tokens": 141647,
          "discarded_tail_tokens": 1647,
          "median_p_value": 0.9999999919740807,
          "median_log10_p_value": -3.4856124619019655e-09,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 4,
          "total_answer_tokens": 141647,
          "discarded_tail_tokens": 21647,
          "median_p_value": 1.0,
          "median_log10_p_value": 0.0,
          "status": "ok"
        }
      }
    },
    "clean": {
      "aggregation": "ordinary_median",
      "num_answers": 500,
      "total_answer_tokens": 159765,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 159,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 765,
          "median_p_value": 0.8659288977499955,
          "median_log10_p_value": -0.06251776685396769,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 79,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 1765,
          "median_p_value": 0.971357711016285,
          "median_log10_p_value": -0.012620807875598238,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 53,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 765,
          "median_p_value": 0.9821335190767914,
          "median_log10_p_value": -0.007829466737979084,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 15,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 9765,
          "median_p_value": 0.9999999999999984,
          "median_log10_p_value": -6.750292265873014e-16,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 7,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 19765,
          "median_p_value": 1.0,
          "median_log10_p_value": 0.0,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 5,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 9765,
          "median_p_value": 1.0,
          "median_log10_p_value": 0.0,
          "status": "ok"
        }
      }
    }
  },
  "grouped_p_value_method": "teacher-tokenizer answer IDs concatenated without separators; exact disjoint blocks; first token of each block is context only; no repetition deduplication; incomplete tail discarded; ordinary median of block p-values (arithmetic mean of the two middle p-values for even group counts)",
  "per_group_p_value_files": {
    "kgw": "/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new.grouped_p_values.json",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.grouped_p_values.json"
  },
  "grouped_p_values_without_severe_repetition": {
    "kgw": {
      "aggregation": "ordinary_median",
      "num_answers": 479,
      "total_answer_tokens": 118875,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 118,
          "total_answer_tokens": 118875,
          "discarded_tail_tokens": 875,
          "median_p_value": 0.8791258704238145,
          "median_log10_p_value": -0.0559489395827206,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 59,
          "total_answer_tokens": 118875,
          "discarded_tail_tokens": 875,
          "median_p_value": 0.9574836194235159,
          "median_log10_p_value": -0.01886864718161641,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 39,
          "total_answer_tokens": 118875,
          "discarded_tail_tokens": 1875,
          "median_p_value": 0.9746416714628057,
          "median_log10_p_value": -0.011155024003919335,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 11,
          "total_answer_tokens": 118875,
          "discarded_tail_tokens": 8875,
          "median_p_value": 0.9998470080082608,
          "median_log10_p_value": -6.64486609738552e-05,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 5,
          "total_answer_tokens": 118875,
          "discarded_tail_tokens": 18875,
          "median_p_value": 0.999999785861883,
          "median_log10_p_value": -9.299901254260768e-08,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 3,
          "total_answer_tokens": 118875,
          "discarded_tail_tokens": 28875,
          "median_p_value": 0.999999999997782,
          "median_log10_p_value": -9.632667063411467e-13,
          "status": "ok"
        }
      },
      "filtering": {
        "repetition_threshold": 0.5,
        "comparison": ">",
        "scope": "answer-internal adjacent token pairs; prompt excluded",
        "num_answers_before": 500,
        "num_answers_retained": 479,
        "num_answers_removed": 21,
        "fraction_answers_removed": 0.042,
        "total_answer_tokens_before": 141647,
        "total_answer_tokens_retained": 118875,
        "total_answer_tokens_removed": 22772,
        "removed_answer_ids": [
          "dolly-00423",
          "dolly-00720",
          "dolly-12249",
          "dolly-12764",
          "dolly-11348",
          "dolly-08406",
          "dolly-00143",
          "dolly-01162",
          "dolly-14358",
          "dolly-09918",
          "dolly-03773",
          "dolly-12951",
          "dolly-08607",
          "dolly-11386",
          "dolly-03319",
          "dolly-07407",
          "dolly-07780",
          "dolly-11182",
          "dolly-01356",
          "dolly-12236",
          "dolly-13235"
        ]
      }
    },
    "clean": {
      "aggregation": "ordinary_median",
      "num_answers": 412,
      "total_answer_tokens": 45882,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 45,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 882,
          "median_p_value": 0.6360891449864364,
          "median_log10_p_value": -0.1964820156995508,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 22,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 1882,
          "median_p_value": 0.7960378878131416,
          "median_log10_p_value": -0.09906626131183685,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 15,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 882,
          "median_p_value": 0.7386263221105359,
          "median_log10_p_value": -0.13157521964243946,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 4,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 5882,
          "median_p_value": 0.947596846602552,
          "median_log10_p_value": -0.0233763931850151,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 2,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 5882,
          "median_p_value": 0.9783739864832501,
          "median_log10_p_value": -0.009495103065976066,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 1,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 15882,
          "median_p_value": 0.9995678964162934,
          "median_log10_p_value": -0.00018770075802065225,
          "status": "ok"
        }
      },
      "filtering": {
        "repetition_threshold": 0.5,
        "comparison": ">",
        "scope": "answer-internal adjacent token pairs; prompt excluded",
        "num_answers_before": 500,
        "num_answers_retained": 412,
        "num_answers_removed": 88,
        "fraction_answers_removed": 0.176,
        "total_answer_tokens_before": 159765,
        "total_answer_tokens_retained": 45882,
        "total_answer_tokens_removed": 113883,
        "removed_answer_ids": [
          "dolly-00135",
          "dolly-12241",
          "dolly-07923",
          "dolly-07103",
          "dolly-05608",
          "dolly-07788",
          "dolly-11310",
          "dolly-02097",
          "dolly-03614",
          "dolly-13505",
          "dolly-02580",
          "dolly-08884",
          "dolly-12659",
          "dolly-00420",
          "dolly-11014",
          "dolly-08008",
          "dolly-02186",
          "dolly-00275",
          "dolly-08512",
          "dolly-14060",
          "dolly-01461",
          "dolly-02223",
          "dolly-04949",
          "dolly-08689",
          "dolly-08574",
          "dolly-08406",
          "dolly-04141",
          "dolly-03209",
          "dolly-06227",
          "dolly-11078",
          "dolly-09778",
          "dolly-04856",
          "dolly-13779",
          "dolly-06595",
          "dolly-08936",
          "dolly-09344",
          "dolly-05605",
          "dolly-08340",
          "dolly-04589",
          "dolly-04686",
          "dolly-14700",
          "dolly-03696",
          "dolly-03914",
          "dolly-11987",
          "dolly-01939",
          "dolly-05628",
          "dolly-13339",
          "dolly-08911",
          "dolly-03239",
          "dolly-13445",
          "dolly-02139",
          "dolly-14265",
          "dolly-13610",
          "dolly-07427",
          "dolly-09563",
          "dolly-02451",
          "dolly-13544",
          "dolly-06824",
          "dolly-05312",
          "dolly-10992",
          "dolly-06932",
          "dolly-08607",
          "dolly-05388",
          "dolly-11386",
          "dolly-02069",
          "dolly-09439",
          "dolly-00148",
          "dolly-08211",
          "dolly-12186",
          "dolly-03319",
          "dolly-07407",
          "dolly-10389",
          "dolly-03916",
          "dolly-08222",
          "dolly-14947",
          "dolly-03624",
          "dolly-09330",
          "dolly-11182",
          "dolly-02059",
          "dolly-02916",
          "dolly-09816",
          "dolly-05355",
          "dolly-06970",
          "dolly-05634",
          "dolly-02500",
          "dolly-11314",
          "dolly-13235",
          "dolly-04223"
        ]
      }
    }
  },
  "grouped_p_value_without_severe_repetition_method": "exclude whole answers whose answer-internal adjacent-token-pair repetition ratio (1 - unique pairs / all pairs) is strictly greater than 0.5; prompts excluded from repetition assessment; filter each label independently; retain original answer order, then concatenate teacher-tokenizer answer IDs without separators; exact disjoint blocks, first token context only; no token-pair deduplication within retained blocks; incomplete tail discarded; ordinary median of block p-values (mean of the middle two for even counts)",
  "per_group_p_value_without_severe_repetition_files": {
    "kgw": "/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new.nonrepetitive_grouped_p_values.json",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.nonrepetitive_grouped_p_values.json"
  },
  "evaluated_at": "2026-10-19T10:27:30+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-10-19T11:39:16+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.452822
- 实际检测配置：`{"gamma": 0.5, "hash_key": 15485863, "seeding": "simple_1 (hash_key * previous_token_id)", "delta_by_label": {"kgw": 2.0, "clean": 2.0}}`
- ROUGE-L（同批 500 条原始 Dolly 回答作参考）：0.229593（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 原始 Dolly 参考文件：`/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl`
- ROUGE-L（同批 500 条 14B clean 教师回答作参考）：0.330629（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 14B clean 教师参考文件：`/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_clean_test.parquet`
- Best F1：0.675749（z 阈值 -5.195844985353305，TPR 0.992000，FPR 0.944000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.010000 | 0.002000 | 0.003953 | 9.593834825900782 |
  | 5% | 0.046000 | 0.024000 | 0.044860 | 2.2662573397778742 |
  | 10% | 0.100000 | 0.070000 | 0.119658 | 1.697749375254331 |

两种逐条文本 p-value 统计（单侧正态近似；不是 AUROC 的显著性检验）：

去重规则：相同的 `(previous_token_id, token_id)` 只计一次；不修改回答文本。

| 数据 | 检测方式 | 有效样本 | p 均值 | p 中位数 | p≤0.01 | p≤0.05 | p≤0.10 |
|---|---|---:|---:|---:|---:|---:|---:|
| kgw | 原始 | 500/500 | 0.598076 | 0.670405 | 10 (2.00%) | 35 (7.00%) | 53 (10.60%) |
| kgw | token 对去重 | 500/500 | 0.565465 | 0.608443 | 1 (0.20%) | 15 (3.00%) | 38 (7.60%) |
| clean | 原始 | 500/500 | 0.538121 | 0.57157 | 22 (4.40%) | 54 (10.80%) | 73 (14.60%) |
| clean | token 对去重 | 500/500 | 0.537418 | 0.555154 | 5 (1.00%) | 25 (5.00%) | 46 (9.20%) |

KGW 的小 p 占比是该理论阈值下的检出率，clean 的小 p 占比是实测误报率。p≤0.05 不保证实际 FPR=5%；去重可改善重复带来的失真，但不保证完全校准。空回答不做显著性检验，p=null，并排除在有效样本统计之外。

逐条 p-value：`/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.p_values.jsonl`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl`

固定 token 分组 p-value（普通中位数；p 越大表示原单侧检验证据越弱）：

按教师 tokenizer 编码回答并无分隔拼接，精确分组；每组首 token 仅作上下文，其余 token 用本项目原 KGW 绿表评分；不去重，尾部不足一组丢弃；各组 p 排序后取普通中位数（偶数组取中间两个 p 的算术平均）。

| 每组 token 数 | 计分 token 数 | KGW 组数 | KGW median p ↑ | clean 组数 | clean median p | KGW/clean 丢弃尾部 tokens |
|---:|---:|---:|---:|---:|---:|---:|
| 1000 | 999 | 108 | 0.953214 | 159 | 0.865929 | 189/765 |
| 2000 | 1999 | 54 | 0.972771 | 79 | 0.971358 | 189/1765 |
| 3000 | 2999 | 36 | 0.987652 | 53 | 0.982134 | 189/765 |
| 10000 | 9999 | 10 | 0.999999 | 15 | 1 | 8189/9765 |
| 20000 | 19999 | 5 | 1 | 7 | 1 | 8189/19765 |
| 30000 | 29999 | 3 | 1 | 5 | 1 | 18189/9765 |

N/A 表示总 token 数不足一个完整组；组数为 1 或 2 时需结合逐组结果解释。极小 p 用科学计数法字符串保存，同时保留 log10(p)，避免浮点下溢为 0。

逐组 p-value 缓存：`/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.grouped_p_values.json`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.grouped_p_values.json`

剔除严重重复回答后的固定 token 分组 p-value（普通中位数）：

先独立筛选 KGW 和 clean：回答内部相邻 token 对重复比例严格大于 50% 时，剔除整条回答；prompt 不参与判断。保留回答按原顺序重新无分隔拼接，各组首 token 仅作上下文；组内不做 token 对去重，尾部不足一组丢弃。这是质量筛选补充指标，原始全样本统计另行保留。

| 数据 | 原回答数 | 剔除严重重复回答 | 保留回答数 | 原 tokens | 剔除 tokens | 保留 tokens |
|---|---:|---:|---:|---:|---:|---:|
| kgw | 500 | 11 (2.20%) | 489 | 108189 | 12069 | 96120 |
| clean | 500 | 88 (17.60%) | 412 | 159765 | 113883 | 45882 |

| 每组 token 数 | 计分 token 数 | KGW 组数 | KGW median p ↑ | clean 组数 | clean median p | KGW/clean 丢弃尾部 tokens |
|---:|---:|---:|---:|---:|---:|---:|
| 1000 | 999 | 96 | 0.891381 | 45 | 0.636089 | 120/882 |
| 2000 | 1999 | 48 | 0.982219 | 22 | 0.796038 | 120/1882 |
| 3000 | 2999 | 32 | 0.993787 | 15 | 0.738626 | 120/882 |
| 10000 | 9999 | 9 | 0.999995 | 4 | 0.947597 | 6120/5882 |
| 20000 | 19999 | 4 | 1 | 2 | 0.978374 | 16120/5882 |
| 30000 | 29999 | 3 | 1 | 1 | 0.999568 | 6120/15882 |

N/A 表示筛选后不足一个完整组。各组 p 取普通中位数，偶数组取中间两个 p 的算术平均；组数较少时请结合逐组缓存解释。

剔除严重重复回答后的逐组 p-value 缓存：`/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.nonrepetitive_grouped_p_values.json`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.nonrepetitive_grouped_p_values.json`

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.45282199999999984,
  "best_f1": {
    "threshold": -5.195844985353305,
    "fpr": 0.944,
    "tpr": 0.992,
    "precision": 0.512396694214876,
    "f1": 0.6757493188010898,
    "tp": 496,
    "fp": 472,
    "tn": 28,
    "fn": 4
  },
  "tpr_at_fpr": {
    "1%": {
      "threshold": 9.593834825900782,
      "fpr": 0.01,
      "tpr": 0.002,
      "precision": 0.16666666666666666,
      "f1": 0.003952569169960474,
      "tp": 1,
      "fp": 5,
      "tn": 495,
      "fn": 499,
      "target_fpr": 0.01
    },
    "5%": {
      "threshold": 2.2662573397778742,
      "fpr": 0.046,
      "tpr": 0.024,
      "precision": 0.34285714285714286,
      "f1": 0.044859813084112146,
      "tp": 12,
      "fp": 23,
      "tn": 477,
      "fn": 488,
      "target_fpr": 0.05
    },
    "10%": {
      "threshold": 1.697749375254331,
      "fpr": 0.1,
      "tpr": 0.07,
      "precision": 0.4117647058823529,
      "f1": 0.11965811965811966,
      "tp": 35,
      "fp": 50,
      "tn": 450,
      "fn": 465,
      "target_fpr": 0.1
    }
  },
  "note": "For each target FPR, select the empirical ROC point with the highest TPR whose FPR does not exceed the target; tied scores are kept together.",
  "detector_config": {
    "gamma": 0.5,
    "hash_key": 15485863,
    "seeding": "simple_1 (hash_key * previous_token_id)",
    "delta_by_label": {
      "kgw": 2.0,
      "clean": 2.0
    }
  },
  "rouge_l_dolly": {
    "mean": 0.2295929496951247,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl",
    "reference_file": "/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl",
    "reference_source": "databricks/databricks-dolly-15k:response",
    "metric": "rougeL",
    "measure": "fmeasure",
    "use_stemmer": true,
    "aggregation": "unweighted mean of per-sample ROUGE-L F1"
  },
  "rouge_l_teacher_clean": {
    "mean": 0.33062936890217354,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl",
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
        "mean": 0.5980756128415708,
        "median": 0.6704045868001102,
        "min": 4.243529073241433e-22,
        "max": 1.0,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 10,
            "fraction": 0.02
          },
          "5%": {
            "alpha": 0.05,
            "count": 35,
            "fraction": 0.07
          },
          "10%": {
            "alpha": 0.1,
            "count": 53,
            "fraction": 0.106
          }
        }
      },
      "deduplicated": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.5654645905266942,
        "median": 0.6084433058368692,
        "min": 0.007646685515099473,
        "max": 0.9979483607953694,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 1,
            "fraction": 0.002
          },
          "5%": {
            "alpha": 0.05,
            "count": 15,
            "fraction": 0.03
          },
          "10%": {
            "alpha": 0.1,
            "count": 38,
            "fraction": 0.076
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
    "kgw": "/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.p_values.jsonl",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl"
  },
  "grouped_p_values": {
    "kgw": {
      "aggregation": "ordinary_median",
      "num_answers": 500,
      "total_answer_tokens": 108189,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 108,
          "total_answer_tokens": 108189,
          "discarded_tail_tokens": 189,
          "median_p_value": 0.9532136797396964,
          "median_log10_p_value": -0.02080973364321328,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 54,
          "total_answer_tokens": 108189,
          "discarded_tail_tokens": 189,
          "median_p_value": 0.9727708620407867,
          "median_log10_p_value": -0.011989446546280093,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 36,
          "total_answer_tokens": 108189,
          "discarded_tail_tokens": 189,
          "median_p_value": 0.98765196739754,
          "median_log10_p_value": -0.005396066816028589,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 10,
          "total_answer_tokens": 108189,
          "discarded_tail_tokens": 8189,
          "median_p_value": 0.9999992426252889,
          "median_log10_p_value": -3.289237823092744e-07,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 5,
          "total_answer_tokens": 108189,
          "discarded_tail_tokens": 8189,
          "median_p_value": 0.9999999999999999,
          "median_log10_p_value": -4.8216373327664354e-17,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 3,
          "total_answer_tokens": 108189,
          "discarded_tail_tokens": 18189,
          "median_p_value": 0.9999999999998027,
          "median_log10_p_value": -8.5680495403268e-14,
          "status": "ok"
        }
      }
    },
    "clean": {
      "aggregation": "ordinary_median",
      "num_answers": 500,
      "total_answer_tokens": 159765,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 159,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 765,
          "median_p_value": 0.8659288977499955,
          "median_log10_p_value": -0.06251776685396769,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 79,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 1765,
          "median_p_value": 0.971357711016285,
          "median_log10_p_value": -0.012620807875598238,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 53,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 765,
          "median_p_value": 0.9821335190767914,
          "median_log10_p_value": -0.007829466737979084,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 15,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 9765,
          "median_p_value": 0.9999999999999984,
          "median_log10_p_value": -6.750292265873014e-16,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 7,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 19765,
          "median_p_value": 1.0,
          "median_log10_p_value": 0.0,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 5,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 9765,
          "median_p_value": 1.0,
          "median_log10_p_value": 0.0,
          "status": "ok"
        }
      }
    }
  },
  "grouped_p_value_method": "teacher-tokenizer answer IDs concatenated without separators; exact disjoint blocks; first token of each block is context only; no repetition deduplication; incomplete tail discarded; ordinary median of block p-values (arithmetic mean of the two middle p-values for even group counts)",
  "per_group_p_value_files": {
    "kgw": "/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.grouped_p_values.json",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.grouped_p_values.json"
  },
  "grouped_p_values_without_severe_repetition": {
    "kgw": {
      "aggregation": "ordinary_median",
      "num_answers": 489,
      "total_answer_tokens": 96120,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 96,
          "total_answer_tokens": 96120,
          "discarded_tail_tokens": 120,
          "median_p_value": 0.8913809204225676,
          "median_log10_p_value": -0.04993666601367001,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 48,
          "total_answer_tokens": 96120,
          "discarded_tail_tokens": 120,
          "median_p_value": 0.9822191552453498,
          "median_log10_p_value": -0.007791600507575589,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 32,
          "total_answer_tokens": 96120,
          "discarded_tail_tokens": 120,
          "median_p_value": 0.993786531657336,
          "median_log10_p_value": -0.0027068933487222604,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 9,
          "total_answer_tokens": 96120,
          "discarded_tail_tokens": 6120,
          "median_p_value": 0.9999948367296856,
          "median_log10_p_value": -2.2423855951505638e-06,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 4,
          "total_answer_tokens": 96120,
          "discarded_tail_tokens": 16120,
          "median_p_value": 0.9999999999971494,
          "median_log10_p_value": -1.2379553851888302e-12,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 3,
          "total_answer_tokens": 96120,
          "discarded_tail_tokens": 6120,
          "median_p_value": 0.9999999999836495,
          "median_log10_p_value": -7.100921732769837e-12,
          "status": "ok"
        }
      },
      "filtering": {
        "repetition_threshold": 0.5,
        "comparison": ">",
        "scope": "answer-internal adjacent token pairs; prompt excluded",
        "num_answers_before": 500,
        "num_answers_retained": 489,
        "num_answers_removed": 11,
        "fraction_answers_removed": 0.022,
        "total_answer_tokens_before": 108189,
        "total_answer_tokens_retained": 96120,
        "total_answer_tokens_removed": 12069,
        "removed_answer_ids": [
          "dolly-08884",
          "dolly-09935",
          "dolly-04624",
          "dolly-14700",
          "dolly-08911",
          "dolly-13445",
          "dolly-02451",
          "dolly-08607",
          "dolly-11386",
          "dolly-12065",
          "dolly-01739"
        ]
      }
    },
    "clean": {
      "aggregation": "ordinary_median",
      "num_answers": 412,
      "total_answer_tokens": 45882,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 45,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 882,
          "median_p_value": 0.6360891449864364,
          "median_log10_p_value": -0.1964820156995508,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 22,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 1882,
          "median_p_value": 0.7960378878131416,
          "median_log10_p_value": -0.09906626131183685,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 15,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 882,
          "median_p_value": 0.7386263221105359,
          "median_log10_p_value": -0.13157521964243946,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 4,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 5882,
          "median_p_value": 0.947596846602552,
          "median_log10_p_value": -0.0233763931850151,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 2,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 5882,
          "median_p_value": 0.9783739864832501,
          "median_log10_p_value": -0.009495103065976066,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 1,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 15882,
          "median_p_value": 0.9995678964162934,
          "median_log10_p_value": -0.00018770075802065225,
          "status": "ok"
        }
      },
      "filtering": {
        "repetition_threshold": 0.5,
        "comparison": ">",
        "scope": "answer-internal adjacent token pairs; prompt excluded",
        "num_answers_before": 500,
        "num_answers_retained": 412,
        "num_answers_removed": 88,
        "fraction_answers_removed": 0.176,
        "total_answer_tokens_before": 159765,
        "total_answer_tokens_retained": 45882,
        "total_answer_tokens_removed": 113883,
        "removed_answer_ids": [
          "dolly-00135",
          "dolly-12241",
          "dolly-07923",
          "dolly-07103",
          "dolly-05608",
          "dolly-07788",
          "dolly-11310",
          "dolly-02097",
          "dolly-03614",
          "dolly-13505",
          "dolly-02580",
          "dolly-08884",
          "dolly-12659",
          "dolly-00420",
          "dolly-11014",
          "dolly-08008",
          "dolly-02186",
          "dolly-00275",
          "dolly-08512",
          "dolly-14060",
          "dolly-01461",
          "dolly-02223",
          "dolly-04949",
          "dolly-08689",
          "dolly-08574",
          "dolly-08406",
          "dolly-04141",
          "dolly-03209",
          "dolly-06227",
          "dolly-11078",
          "dolly-09778",
          "dolly-04856",
          "dolly-13779",
          "dolly-06595",
          "dolly-08936",
          "dolly-09344",
          "dolly-05605",
          "dolly-08340",
          "dolly-04589",
          "dolly-04686",
          "dolly-14700",
          "dolly-03696",
          "dolly-03914",
          "dolly-11987",
          "dolly-01939",
          "dolly-05628",
          "dolly-13339",
          "dolly-08911",
          "dolly-03239",
          "dolly-13445",
          "dolly-02139",
          "dolly-14265",
          "dolly-13610",
          "dolly-07427",
          "dolly-09563",
          "dolly-02451",
          "dolly-13544",
          "dolly-06824",
          "dolly-05312",
          "dolly-10992",
          "dolly-06932",
          "dolly-08607",
          "dolly-05388",
          "dolly-11386",
          "dolly-02069",
          "dolly-09439",
          "dolly-00148",
          "dolly-08211",
          "dolly-12186",
          "dolly-03319",
          "dolly-07407",
          "dolly-10389",
          "dolly-03916",
          "dolly-08222",
          "dolly-14947",
          "dolly-03624",
          "dolly-09330",
          "dolly-11182",
          "dolly-02059",
          "dolly-02916",
          "dolly-09816",
          "dolly-05355",
          "dolly-06970",
          "dolly-05634",
          "dolly-02500",
          "dolly-11314",
          "dolly-13235",
          "dolly-04223"
        ]
      }
    }
  },
  "grouped_p_value_without_severe_repetition_method": "exclude whole answers whose answer-internal adjacent-token-pair repetition ratio (1 - unique pairs / all pairs) is strictly greater than 0.5; prompts excluded from repetition assessment; filter each label independently; retain original answer order, then concatenate teacher-tokenizer answer IDs without separators; exact disjoint blocks, first token context only; no token-pair deduplication within retained blocks; incomplete tail discarded; ordinary median of block p-values (mean of the middle two for even counts)",
  "per_group_p_value_without_severe_repetition_files": {
    "kgw": "/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.nonrepetitive_grouped_p_values.json",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.nonrepetitive_grouped_p_values.json"
  },
  "evaluated_at": "2026-10-19T11:39:16+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-10-19T12:27:01+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.462604
- 实际检测配置：`{"gamma": 0.5, "hash_key": 15485863, "seeding": "simple_1 (hash_key * previous_token_id)", "delta_by_label": {"kgw": 2.0, "clean": 2.0}}`
- ROUGE-L（同批 500 条原始 Dolly 回答作参考）：0.209115（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 原始 Dolly 参考文件：`/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl`
- ROUGE-L（同批 500 条 14B clean 教师回答作参考）：0.309962（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 14B clean 教师参考文件：`/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_clean_test.parquet`
- Best F1：0.678450（z 阈值 -5.03309510460972，TPR 0.998000，FPR 0.944000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.000000 | 0.000000 | 0.000000 | None |
  | 5% | 0.050000 | 0.030000 | 0.055556 | 2.2283440581246223 |
  | 10% | 0.100000 | 0.070000 | 0.119658 | 1.7008401285415224 |

两种逐条文本 p-value 统计（单侧正态近似；不是 AUROC 的显著性检验）：

去重规则：相同的 `(previous_token_id, token_id)` 只计一次；不修改回答文本。

| 数据 | 检测方式 | 有效样本 | p 均值 | p 中位数 | p≤0.01 | p≤0.05 | p≤0.10 |
|---|---|---:|---:|---:|---:|---:|---:|
| kgw | 原始 | 500/500 | 0.587914 | 0.658361 | 11 (2.20%) | 36 (7.20%) | 55 (11.00%) |
| kgw | token 对去重 | 500/500 | 0.561811 | 0.599669 | 2 (0.40%) | 22 (4.40%) | 35 (7.00%) |
| clean | 原始 | 500/500 | 0.538121 | 0.57157 | 22 (4.40%) | 54 (10.80%) | 73 (14.60%) |
| clean | token 对去重 | 500/500 | 0.537418 | 0.555154 | 5 (1.00%) | 25 (5.00%) | 46 (9.20%) |

KGW 的小 p 占比是该理论阈值下的检出率，clean 的小 p 占比是实测误报率。p≤0.05 不保证实际 FPR=5%；去重可改善重复带来的失真，但不保证完全校准。空回答不做显著性检验，p=null，并排除在有效样本统计之外。

逐条 p-value：`/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.p_values.jsonl`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl`

固定 token 分组 p-value（普通中位数；p 越大表示原单侧检验证据越弱）：

按教师 tokenizer 编码回答并无分隔拼接，精确分组；每组首 token 仅作上下文，其余 token 用本项目原 KGW 绿表评分；不去重，尾部不足一组丢弃；各组 p 排序后取普通中位数（偶数组取中间两个 p 的算术平均）。

| 每组 token 数 | 计分 token 数 | KGW 组数 | KGW median p ↑ | clean 组数 | clean median p | KGW/clean 丢弃尾部 tokens |
|---:|---:|---:|---:|---:|---:|---:|
| 1000 | 999 | 110 | 0.851774 | 159 | 0.865929 | 315/765 |
| 2000 | 1999 | 55 | 0.968302 | 79 | 0.971358 | 315/1765 |
| 3000 | 2999 | 36 | 0.980464 | 53 | 0.982134 | 2315/765 |
| 10000 | 9999 | 11 | 0.997949 | 15 | 1 | 315/9765 |
| 20000 | 19999 | 5 | 1 | 7 | 1 | 10315/19765 |
| 30000 | 29999 | 3 | 1 | 5 | 1 | 20315/9765 |

N/A 表示总 token 数不足一个完整组；组数为 1 或 2 时需结合逐组结果解释。极小 p 用科学计数法字符串保存，同时保留 log10(p)，避免浮点下溢为 0。

逐组 p-value 缓存：`/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.grouped_p_values.json`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.grouped_p_values.json`

剔除严重重复回答后的固定 token 分组 p-value（普通中位数）：

先独立筛选 KGW 和 clean：回答内部相邻 token 对重复比例严格大于 50% 时，剔除整条回答；prompt 不参与判断。保留回答按原顺序重新无分隔拼接，各组首 token 仅作上下文；组内不做 token 对去重，尾部不足一组丢弃。这是质量筛选补充指标，原始全样本统计另行保留。

| 数据 | 原回答数 | 剔除严重重复回答 | 保留回答数 | 原 tokens | 剔除 tokens | 保留 tokens |
|---|---:|---:|---:|---:|---:|---:|
| kgw | 500 | 15 (3.00%) | 485 | 110315 | 10798 | 99517 |
| clean | 500 | 88 (17.60%) | 412 | 159765 | 113883 | 45882 |

| 每组 token 数 | 计分 token 数 | KGW 组数 | KGW median p ↑ | clean 组数 | clean median p | KGW/clean 丢弃尾部 tokens |
|---:|---:|---:|---:|---:|---:|---:|
| 1000 | 999 | 99 | 0.851774 | 45 | 0.636089 | 517/882 |
| 2000 | 1999 | 49 | 0.96138 | 22 | 0.796038 | 1517/1882 |
| 3000 | 2999 | 33 | 0.961742 | 15 | 0.738626 | 517/882 |
| 10000 | 9999 | 9 | 0.999698 | 4 | 0.947597 | 9517/5882 |
| 20000 | 19999 | 4 | 0.999998 | 2 | 0.978374 | 19517/5882 |
| 30000 | 29999 | 3 | 1 | 1 | 0.999568 | 9517/15882 |

N/A 表示筛选后不足一个完整组。各组 p 取普通中位数，偶数组取中间两个 p 的算术平均；组数较少时请结合逐组缓存解释。

剔除严重重复回答后的逐组 p-value 缓存：`/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.nonrepetitive_grouped_p_values.json`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.nonrepetitive_grouped_p_values.json`

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.4626040000000001,
  "best_f1": {
    "threshold": -5.03309510460972,
    "fpr": 0.944,
    "tpr": 0.998,
    "precision": 0.513903192584964,
    "f1": 0.6784500339904826,
    "tp": 499,
    "fp": 472,
    "tn": 28,
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
      "threshold": 2.2283440581246223,
      "fpr": 0.05,
      "tpr": 0.03,
      "precision": 0.375,
      "f1": 0.05555555555555555,
      "tp": 15,
      "fp": 25,
      "tn": 475,
      "fn": 485,
      "target_fpr": 0.05
    },
    "10%": {
      "threshold": 1.7008401285415224,
      "fpr": 0.1,
      "tpr": 0.07,
      "precision": 0.4117647058823529,
      "f1": 0.11965811965811966,
      "tp": 35,
      "fp": 50,
      "tn": 450,
      "fn": 465,
      "target_fpr": 0.1
    }
  },
  "note": "For each target FPR, select the empirical ROC point with the highest TPR whose FPR does not exceed the target; tied scores are kept together.",
  "detector_config": {
    "gamma": 0.5,
    "hash_key": 15485863,
    "seeding": "simple_1 (hash_key * previous_token_id)",
    "delta_by_label": {
      "kgw": 2.0,
      "clean": 2.0
    }
  },
  "rouge_l_dolly": {
    "mean": 0.20911479663899177,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl",
    "reference_file": "/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl",
    "reference_source": "databricks/databricks-dolly-15k:response",
    "metric": "rougeL",
    "measure": "fmeasure",
    "use_stemmer": true,
    "aggregation": "unweighted mean of per-sample ROUGE-L F1"
  },
  "rouge_l_teacher_clean": {
    "mean": 0.30996181867715505,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl",
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
        "mean": 0.587913978437283,
        "median": 0.658361434051861,
        "min": 0.002197952486763932,
        "max": 0.9999999978094234,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 11,
            "fraction": 0.022
          },
          "5%": {
            "alpha": 0.05,
            "count": 36,
            "fraction": 0.072
          },
          "10%": {
            "alpha": 0.1,
            "count": 55,
            "fraction": 0.11
          }
        }
      },
      "deduplicated": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.5618113459887325,
        "median": 0.5996692153351387,
        "min": 0.00921106272704951,
        "max": 0.9997579313716072,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 2,
            "fraction": 0.004
          },
          "5%": {
            "alpha": 0.05,
            "count": 22,
            "fraction": 0.044
          },
          "10%": {
            "alpha": 0.1,
            "count": 35,
            "fraction": 0.07
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
    "kgw": "/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.p_values.jsonl",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl"
  },
  "grouped_p_values": {
    "kgw": {
      "aggregation": "ordinary_median",
      "num_answers": 500,
      "total_answer_tokens": 110315,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 110,
          "total_answer_tokens": 110315,
          "discarded_tail_tokens": 315,
          "median_p_value": 0.8517743756590758,
          "median_log10_p_value": -0.06967542915691224,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 55,
          "total_answer_tokens": 110315,
          "discarded_tail_tokens": 315,
          "median_p_value": 0.9683017588985491,
          "median_log10_p_value": -0.013989279259781976,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 36,
          "total_answer_tokens": 110315,
          "discarded_tail_tokens": 2315,
          "median_p_value": 0.9804642099767789,
          "median_log10_p_value": -0.008568254819532509,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 11,
          "total_answer_tokens": 110315,
          "discarded_tail_tokens": 315,
          "median_p_value": 0.9979485722951797,
          "median_log10_p_value": -0.0008918388167411366,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 5,
          "total_answer_tokens": 110315,
          "discarded_tail_tokens": 10315,
          "median_p_value": 0.9999999196212623,
          "median_log10_p_value": -3.490804363351823e-08,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 3,
          "total_answer_tokens": 110315,
          "discarded_tail_tokens": 20315,
          "median_p_value": 0.9999999983699949,
          "median_log10_p_value": -7.079022343879514e-10,
          "status": "ok"
        }
      }
    },
    "clean": {
      "aggregation": "ordinary_median",
      "num_answers": 500,
      "total_answer_tokens": 159765,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 159,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 765,
          "median_p_value": 0.8659288977499955,
          "median_log10_p_value": -0.06251776685396769,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 79,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 1765,
          "median_p_value": 0.971357711016285,
          "median_log10_p_value": -0.012620807875598238,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 53,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 765,
          "median_p_value": 0.9821335190767914,
          "median_log10_p_value": -0.007829466737979084,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 15,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 9765,
          "median_p_value": 0.9999999999999984,
          "median_log10_p_value": -6.750292265873014e-16,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 7,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 19765,
          "median_p_value": 1.0,
          "median_log10_p_value": 0.0,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 5,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 9765,
          "median_p_value": 1.0,
          "median_log10_p_value": 0.0,
          "status": "ok"
        }
      }
    }
  },
  "grouped_p_value_method": "teacher-tokenizer answer IDs concatenated without separators; exact disjoint blocks; first token of each block is context only; no repetition deduplication; incomplete tail discarded; ordinary median of block p-values (arithmetic mean of the two middle p-values for even group counts)",
  "per_group_p_value_files": {
    "kgw": "/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.grouped_p_values.json",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.grouped_p_values.json"
  },
  "grouped_p_values_without_severe_repetition": {
    "kgw": {
      "aggregation": "ordinary_median",
      "num_answers": 485,
      "total_answer_tokens": 99517,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 99,
          "total_answer_tokens": 99517,
          "discarded_tail_tokens": 517,
          "median_p_value": 0.8517743756590758,
          "median_log10_p_value": -0.06967542915691224,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 49,
          "total_answer_tokens": 99517,
          "discarded_tail_tokens": 1517,
          "median_p_value": 0.9613804838256327,
          "median_log10_p_value": -0.017104698363877752,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 33,
          "total_answer_tokens": 99517,
          "discarded_tail_tokens": 517,
          "median_p_value": 0.9617416641553246,
          "median_log10_p_value": -0.016941569229135967,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 9,
          "total_answer_tokens": 99517,
          "discarded_tail_tokens": 9517,
          "median_p_value": 0.999698400080992,
          "median_log10_p_value": -0.00013100293679839522,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 4,
          "total_answer_tokens": 99517,
          "discarded_tail_tokens": 19517,
          "median_p_value": 0.9999979012264593,
          "median_log10_p_value": -9.114867240411086e-07,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 3,
          "total_answer_tokens": 99517,
          "discarded_tail_tokens": 9517,
          "median_p_value": 0.9999999073746251,
          "median_log10_p_value": -4.0226691077415586e-08,
          "status": "ok"
        }
      },
      "filtering": {
        "repetition_threshold": 0.5,
        "comparison": ">",
        "scope": "answer-internal adjacent token pairs; prompt excluded",
        "num_answers_before": 500,
        "num_answers_retained": 485,
        "num_answers_removed": 15,
        "fraction_answers_removed": 0.03,
        "total_answer_tokens_before": 110315,
        "total_answer_tokens_retained": 99517,
        "total_answer_tokens_removed": 10798,
        "removed_answer_ids": [
          "dolly-07923",
          "dolly-08884",
          "dolly-01092",
          "dolly-02516",
          "dolly-02725",
          "dolly-03239",
          "dolly-13445",
          "dolly-03231",
          "dolly-08607",
          "dolly-11386",
          "dolly-03319",
          "dolly-05355",
          "dolly-01356",
          "dolly-12236",
          "dolly-13235"
        ]
      }
    },
    "clean": {
      "aggregation": "ordinary_median",
      "num_answers": 412,
      "total_answer_tokens": 45882,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 45,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 882,
          "median_p_value": 0.6360891449864364,
          "median_log10_p_value": -0.1964820156995508,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 22,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 1882,
          "median_p_value": 0.7960378878131416,
          "median_log10_p_value": -0.09906626131183685,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 15,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 882,
          "median_p_value": 0.7386263221105359,
          "median_log10_p_value": -0.13157521964243946,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 4,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 5882,
          "median_p_value": 0.947596846602552,
          "median_log10_p_value": -0.0233763931850151,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 2,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 5882,
          "median_p_value": 0.9783739864832501,
          "median_log10_p_value": -0.009495103065976066,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 1,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 15882,
          "median_p_value": 0.9995678964162934,
          "median_log10_p_value": -0.00018770075802065225,
          "status": "ok"
        }
      },
      "filtering": {
        "repetition_threshold": 0.5,
        "comparison": ">",
        "scope": "answer-internal adjacent token pairs; prompt excluded",
        "num_answers_before": 500,
        "num_answers_retained": 412,
        "num_answers_removed": 88,
        "fraction_answers_removed": 0.176,
        "total_answer_tokens_before": 159765,
        "total_answer_tokens_retained": 45882,
        "total_answer_tokens_removed": 113883,
        "removed_answer_ids": [
          "dolly-00135",
          "dolly-12241",
          "dolly-07923",
          "dolly-07103",
          "dolly-05608",
          "dolly-07788",
          "dolly-11310",
          "dolly-02097",
          "dolly-03614",
          "dolly-13505",
          "dolly-02580",
          "dolly-08884",
          "dolly-12659",
          "dolly-00420",
          "dolly-11014",
          "dolly-08008",
          "dolly-02186",
          "dolly-00275",
          "dolly-08512",
          "dolly-14060",
          "dolly-01461",
          "dolly-02223",
          "dolly-04949",
          "dolly-08689",
          "dolly-08574",
          "dolly-08406",
          "dolly-04141",
          "dolly-03209",
          "dolly-06227",
          "dolly-11078",
          "dolly-09778",
          "dolly-04856",
          "dolly-13779",
          "dolly-06595",
          "dolly-08936",
          "dolly-09344",
          "dolly-05605",
          "dolly-08340",
          "dolly-04589",
          "dolly-04686",
          "dolly-14700",
          "dolly-03696",
          "dolly-03914",
          "dolly-11987",
          "dolly-01939",
          "dolly-05628",
          "dolly-13339",
          "dolly-08911",
          "dolly-03239",
          "dolly-13445",
          "dolly-02139",
          "dolly-14265",
          "dolly-13610",
          "dolly-07427",
          "dolly-09563",
          "dolly-02451",
          "dolly-13544",
          "dolly-06824",
          "dolly-05312",
          "dolly-10992",
          "dolly-06932",
          "dolly-08607",
          "dolly-05388",
          "dolly-11386",
          "dolly-02069",
          "dolly-09439",
          "dolly-00148",
          "dolly-08211",
          "dolly-12186",
          "dolly-03319",
          "dolly-07407",
          "dolly-10389",
          "dolly-03916",
          "dolly-08222",
          "dolly-14947",
          "dolly-03624",
          "dolly-09330",
          "dolly-11182",
          "dolly-02059",
          "dolly-02916",
          "dolly-09816",
          "dolly-05355",
          "dolly-06970",
          "dolly-05634",
          "dolly-02500",
          "dolly-11314",
          "dolly-13235",
          "dolly-04223"
        ]
      }
    }
  },
  "grouped_p_value_without_severe_repetition_method": "exclude whole answers whose answer-internal adjacent-token-pair repetition ratio (1 - unique pairs / all pairs) is strictly greater than 0.5; prompts excluded from repetition assessment; filter each label independently; retain original answer order, then concatenate teacher-tokenizer answer IDs without separators; exact disjoint blocks, first token context only; no token-pair deduplication within retained blocks; incomplete tail discarded; ordinary median of block p-values (mean of the middle two for even counts)",
  "per_group_p_value_without_severe_repetition_files": {
    "kgw": "/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.nonrepetitive_grouped_p_values.json",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.nonrepetitive_grouped_p_values.json"
  },
  "evaluated_at": "2026-10-19T12:27:01+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-10-19T17:13:34+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.452822
- 实际检测配置：`{"gamma": 0.5, "hash_key": 15485863, "seeding": "simple_1 (hash_key * previous_token_id)", "delta_by_label": {"kgw": 2.0, "clean": 2.0}}`
- ROUGE-L（同批 500 条原始 Dolly 回答作参考）：0.229593（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 原始 Dolly 参考文件：`/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl`
- ROUGE-L（同批 500 条 14B clean 教师回答作参考）：0.330629（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 14B clean 教师参考文件：`/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_clean_test.parquet`
- Best F1：0.675749（z 阈值 -5.195844985353305，TPR 0.992000，FPR 0.944000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.010000 | 0.002000 | 0.003953 | 9.593834825900782 |
  | 5% | 0.046000 | 0.024000 | 0.044860 | 2.2662573397778742 |
  | 10% | 0.100000 | 0.070000 | 0.119658 | 1.697749375254331 |

两种逐条文本 p-value 统计（单侧正态近似；不是 AUROC 的显著性检验）：

去重规则：相同的 `(previous_token_id, token_id)` 只计一次；不修改回答文本。

| 数据 | 检测方式 | 有效样本 | p 均值 | p 中位数 | p≤0.01 | p≤0.05 | p≤0.10 |
|---|---|---:|---:|---:|---:|---:|---:|
| kgw | 原始 | 500/500 | 0.598076 | 0.670405 | 10 (2.00%) | 35 (7.00%) | 53 (10.60%) |
| kgw | token 对去重 | 500/500 | 0.565465 | 0.608443 | 1 (0.20%) | 15 (3.00%) | 38 (7.60%) |
| clean | 原始 | 500/500 | 0.538121 | 0.57157 | 22 (4.40%) | 54 (10.80%) | 73 (14.60%) |
| clean | token 对去重 | 500/500 | 0.537418 | 0.555154 | 5 (1.00%) | 25 (5.00%) | 46 (9.20%) |

KGW 的小 p 占比是该理论阈值下的检出率，clean 的小 p 占比是实测误报率。p≤0.05 不保证实际 FPR=5%；去重可改善重复带来的失真，但不保证完全校准。空回答不做显著性检验，p=null，并排除在有效样本统计之外。

逐条 p-value：`/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.p_values.jsonl`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl`

固定 token 分组 p-value（普通中位数；p 越大表示原单侧检验证据越弱）：

按教师 tokenizer 编码回答并无分隔拼接，精确分组；每组首 token 仅作上下文，其余 token 用本项目原 KGW 绿表评分；不去重，尾部不足一组丢弃；各组 p 排序后取普通中位数（偶数组取中间两个 p 的算术平均）。

| 每组 token 数 | 计分 token 数 | KGW 组数 | KGW median p ↑ | clean 组数 | clean median p | KGW/clean 丢弃尾部 tokens |
|---:|---:|---:|---:|---:|---:|---:|
| 1000 | 999 | 108 | 0.953214 | 159 | 0.865929 | 189/765 |
| 2000 | 1999 | 54 | 0.972771 | 79 | 0.971358 | 189/1765 |
| 3000 | 2999 | 36 | 0.987652 | 53 | 0.982134 | 189/765 |
| 10000 | 9999 | 10 | 0.999999 | 15 | 1 | 8189/9765 |
| 20000 | 19999 | 5 | 1 | 7 | 1 | 8189/19765 |
| 30000 | 29999 | 3 | 1 | 5 | 1 | 18189/9765 |

N/A 表示总 token 数不足一个完整组；组数为 1 或 2 时需结合逐组结果解释。极小 p 用科学计数法字符串保存，同时保留 log10(p)，避免浮点下溢为 0。

逐组 p-value 缓存：`/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.grouped_p_values.json`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.grouped_p_values.json`

剔除严重重复回答后的固定 token 分组 p-value（普通中位数）：

先独立筛选 KGW 和 clean：回答内部相邻 token 对重复比例严格大于 50% 时，剔除整条回答；prompt 不参与判断。保留回答按原顺序重新无分隔拼接，各组首 token 仅作上下文；组内不做 token 对去重，尾部不足一组丢弃。这是质量筛选补充指标，原始全样本统计另行保留。

| 数据 | 原回答数 | 剔除严重重复回答 | 保留回答数 | 原 tokens | 剔除 tokens | 保留 tokens |
|---|---:|---:|---:|---:|---:|---:|
| kgw | 500 | 11 (2.20%) | 489 | 108189 | 12069 | 96120 |
| clean | 500 | 88 (17.60%) | 412 | 159765 | 113883 | 45882 |

| 每组 token 数 | 计分 token 数 | KGW 组数 | KGW median p ↑ | clean 组数 | clean median p | KGW/clean 丢弃尾部 tokens |
|---:|---:|---:|---:|---:|---:|---:|
| 1000 | 999 | 96 | 0.891381 | 45 | 0.636089 | 120/882 |
| 2000 | 1999 | 48 | 0.982219 | 22 | 0.796038 | 120/1882 |
| 3000 | 2999 | 32 | 0.993787 | 15 | 0.738626 | 120/882 |
| 10000 | 9999 | 9 | 0.999995 | 4 | 0.947597 | 6120/5882 |
| 20000 | 19999 | 4 | 1 | 2 | 0.978374 | 16120/5882 |
| 30000 | 29999 | 3 | 1 | 1 | 0.999568 | 6120/15882 |

N/A 表示筛选后不足一个完整组。各组 p 取普通中位数，偶数组取中间两个 p 的算术平均；组数较少时请结合逐组缓存解释。

剔除严重重复回答后的逐组 p-value 缓存：`/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.nonrepetitive_grouped_p_values.json`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.nonrepetitive_grouped_p_values.json`

### 固定参考模型 PPL（只评分已保存的回答）

| 文件组 | 总体 PPL ↓ | 有效样本/总样本 | 计分回答 tokens | 平均回答 tokens | 状态 | 缓存复用 |
|---|---:|---:|---:|---:|---|---|
| kgw | 3.106746 | 500/500 | 105228 | 210.46 | ok | False |
| clean | 1.535880 | 500/500 | 156267 | 312.53 | ok | False |

总体 PPL = exp(全部有效回答 NLL 总和 / 全部计分回答 token 数)，不是逐条 PPL 的算术平均。
原生成 tokenizer 恢复实际生成 prompt；参考 tokenizer 对 prompt/answer 分开编码后拼接；只计回答，包含首回答 token。Base 参考模型不再套用 chat template；只添加一次参考 BOS，不额外评分 EOS；输入 JSONL 不修改。

- kgw: `/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl`；SHA256 `dd4cfdbe540e2227bbad3b46f6a64e34bb1a46b7e7d24860ef8be90ec03efd48`；逐条明细 `/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.ppl.2fbd37ec395a4c387a8e.jsonl`；空回答 0；异常 loss 0；原生成截断 3；参考上下文截断 0。

  生成文本配置（种子逐条保存在明细中）：

```json
{
  "student_model_paths": [
    "/shared/wwx/EasyGAD/checkpoints/gad_05b_cleanwarmup_cleangad_control/gad/global_step_1813/actor/huggingface"
  ],
  "generation_tokenizer_paths": [
    "/shared/public_models/Qwen2.5-0.5B"
  ],
  "generation_configurations": [
    {
      "configuration": {
        "temperature": 0.7,
        "top_p": 0.9,
        "max_new_tokens": 1536,
        "max_prompt_tokens": 2048,
        "kgw_enabled_during_generation": false
      },
      "samples": 500
    }
  ],
  "generation_seeds": {
    "recorded_samples": 500,
    "minimum": 42,
    "maximum": 541,
    "individual_values": "see per-sample immutable records"
  }
}
```
- clean: `/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl`；SHA256 `597b843d28d31c353c7bb9b94a3b6dccb564cb45ac2c5252f6a1592ccd768efe`；逐条明细 `/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.ppl.877fc574f9ee35a5145f.jsonl`；空回答 0；异常 loss 0；原生成截断 3；参考上下文截断 0。

  生成文本配置（种子逐条保存在明细中）：

```json
{
  "student_model_paths": [
    "/shared/public_models/Qwen2.5-0.5B"
  ],
  "generation_tokenizer_paths": [
    "/shared/public_models/Qwen2.5-0.5B"
  ],
  "generation_configurations": [
    {
      "configuration": {
        "temperature": 0.7,
        "top_p": 0.9,
        "max_new_tokens": 1536,
        "max_prompt_tokens": 2048,
        "kgw_enabled_during_generation": false
      },
      "samples": 500
    }
  ],
  "generation_seeds": {
    "recorded_samples": 500,
    "minimum": 42,
    "maximum": 541,
    "individual_values": "see per-sample immutable records"
  }
}
```

完整评分配置（含模型/tokenizer 指纹、软件版本；权重使用 size/mtime 标识，不全量哈希）：

```json
{
  "model_path": "/shared/public_models/Llama-3-8B",
  "device": "cuda",
  "dtype": "bfloat16",
  "generation_tokenizer": "/shared/public_models/Qwen2.5-0.5B",
  "max_length": null,
  "overflow": "error",
  "effective_max_length": 8192,
  "protocol": {
    "prompt": "source-generation-prompt; source chat template, not reference chat template",
    "boundary": "encode prompt and answer separately with add_special_tokens=False, then concatenate",
    "bos": "one reference BOS at start when defined; no extra EOS",
    "loss": "causal next-token NLL on all answer tokens, including the first; no prompt or padding loss",
    "aggregate": "exp(sum(answer NLL) / sum(scored answer tokens)); not mean per-answer PPL",
    "source_tokenizer_selection": "explicit override, otherwise row.model_path; fallback assumes the generation tokenizer matches that checkpoint",
    "legacy_prompt_limit": 2048,
    "weights_fingerprint": "weight filenames, sizes and mtime_ns; weight contents are not hashed"
  },
  "reference_assets": {
    "path": "/shared/public_models/Llama-3-8B",
    "assets": [
      {
        "name": "config.json",
        "size": 654,
        "sha256": "2430cee764b6530ff8673cf9ba8561e1d5a33152d503cd0de909ff5718261441"
      },
      {
        "name": "generation_config.json",
        "size": 126,
        "sha256": "55550e95c40c53fb0ee3f960d6d2b25a46405c8f790e5c4bb02caf3e98f2b5d0"
      },
      {
        "name": "model.safetensors.index.json",
        "size": 23950,
        "sha256": "146776fce3f6db1103aa6f249e65ee5544c5923ce6f971b092eee79aa6e5d37b"
      },
      {
        "name": "special_tokens_map.json",
        "size": 73,
        "sha256": "462d91939dbc37178aa5a3eae7068d1990ccc92e09f288cc71f42cdf139d69cc"
      },
      {
        "name": "tokenizer.json",
        "size": 9085698,
        "sha256": "e134af98b985517b4f068e3755ae90d4e9cd2d45d328325dc503f1c6b2d06cc7"
      },
      {
        "name": "tokenizer_config.json",
        "size": 50566,
        "sha256": "690727b4fed286383df1c7ca5e805124cb70c6eb4529f807c7b2e60ff741da7e"
      }
    ],
    "weight_stats": [
      {
        "name": "model-00001-of-00004.safetensors",
        "size": 4976698672,
        "mtime_ns": 1736746522477644778
      },
      {
        "name": "model-00002-of-00004.safetensors",
        "size": 4999802720,
        "mtime_ns": 1736746656058650226
      },
      {
        "name": "model-00003-of-00004.safetensors",
        "size": 4915916176,
        "mtime_ns": 1736746768408654808
      },
      {
        "name": "model-00004-of-00004.safetensors",
        "size": 1168138808,
        "mtime_ns": 1736746796088655937
      }
    ],
    "weight_content_hashed": false
  },
  "software": {
    "python": "3.10.21",
    "torch": "2.6.0",
    "transformers": "4.51.3",
    "tokenizers": "0.21.4"
  }
}
```

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.45282199999999984,
  "best_f1": {
    "threshold": -5.195844985353305,
    "fpr": 0.944,
    "tpr": 0.992,
    "precision": 0.512396694214876,
    "f1": 0.6757493188010898,
    "tp": 496,
    "fp": 472,
    "tn": 28,
    "fn": 4
  },
  "tpr_at_fpr": {
    "1%": {
      "threshold": 9.593834825900782,
      "fpr": 0.01,
      "tpr": 0.002,
      "precision": 0.16666666666666666,
      "f1": 0.003952569169960474,
      "tp": 1,
      "fp": 5,
      "tn": 495,
      "fn": 499,
      "target_fpr": 0.01
    },
    "5%": {
      "threshold": 2.2662573397778742,
      "fpr": 0.046,
      "tpr": 0.024,
      "precision": 0.34285714285714286,
      "f1": 0.044859813084112146,
      "tp": 12,
      "fp": 23,
      "tn": 477,
      "fn": 488,
      "target_fpr": 0.05
    },
    "10%": {
      "threshold": 1.697749375254331,
      "fpr": 0.1,
      "tpr": 0.07,
      "precision": 0.4117647058823529,
      "f1": 0.11965811965811966,
      "tp": 35,
      "fp": 50,
      "tn": 450,
      "fn": 465,
      "target_fpr": 0.1
    }
  },
  "note": "For each target FPR, select the empirical ROC point with the highest TPR whose FPR does not exceed the target; tied scores are kept together.",
  "detector_config": {
    "gamma": 0.5,
    "hash_key": 15485863,
    "seeding": "simple_1 (hash_key * previous_token_id)",
    "delta_by_label": {
      "kgw": 2.0,
      "clean": 2.0
    }
  },
  "rouge_l_dolly": {
    "mean": 0.2295929496951247,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl",
    "reference_file": "/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl",
    "reference_source": "databricks/databricks-dolly-15k:response",
    "metric": "rougeL",
    "measure": "fmeasure",
    "use_stemmer": true,
    "aggregation": "unweighted mean of per-sample ROUGE-L F1"
  },
  "rouge_l_teacher_clean": {
    "mean": 0.33062936890217354,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl",
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
        "mean": 0.5980756128415708,
        "median": 0.6704045868001102,
        "min": 4.243529073241433e-22,
        "max": 1.0,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 10,
            "fraction": 0.02
          },
          "5%": {
            "alpha": 0.05,
            "count": 35,
            "fraction": 0.07
          },
          "10%": {
            "alpha": 0.1,
            "count": 53,
            "fraction": 0.106
          }
        }
      },
      "deduplicated": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.5654645905266942,
        "median": 0.6084433058368692,
        "min": 0.007646685515099473,
        "max": 0.9979483607953694,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 1,
            "fraction": 0.002
          },
          "5%": {
            "alpha": 0.05,
            "count": 15,
            "fraction": 0.03
          },
          "10%": {
            "alpha": 0.1,
            "count": 38,
            "fraction": 0.076
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
    "kgw": "/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.p_values.jsonl",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl"
  },
  "grouped_p_values": {
    "kgw": {
      "aggregation": "ordinary_median",
      "num_answers": 500,
      "total_answer_tokens": 108189,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 108,
          "total_answer_tokens": 108189,
          "discarded_tail_tokens": 189,
          "median_p_value": 0.9532136797396964,
          "median_log10_p_value": -0.02080973364321328,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 54,
          "total_answer_tokens": 108189,
          "discarded_tail_tokens": 189,
          "median_p_value": 0.9727708620407867,
          "median_log10_p_value": -0.011989446546280093,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 36,
          "total_answer_tokens": 108189,
          "discarded_tail_tokens": 189,
          "median_p_value": 0.98765196739754,
          "median_log10_p_value": -0.005396066816028589,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 10,
          "total_answer_tokens": 108189,
          "discarded_tail_tokens": 8189,
          "median_p_value": 0.9999992426252889,
          "median_log10_p_value": -3.289237823092744e-07,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 5,
          "total_answer_tokens": 108189,
          "discarded_tail_tokens": 8189,
          "median_p_value": 0.9999999999999999,
          "median_log10_p_value": -4.8216373327664354e-17,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 3,
          "total_answer_tokens": 108189,
          "discarded_tail_tokens": 18189,
          "median_p_value": 0.9999999999998027,
          "median_log10_p_value": -8.5680495403268e-14,
          "status": "ok"
        }
      }
    },
    "clean": {
      "aggregation": "ordinary_median",
      "num_answers": 500,
      "total_answer_tokens": 159765,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 159,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 765,
          "median_p_value": 0.8659288977499955,
          "median_log10_p_value": -0.06251776685396769,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 79,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 1765,
          "median_p_value": 0.971357711016285,
          "median_log10_p_value": -0.012620807875598238,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 53,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 765,
          "median_p_value": 0.9821335190767914,
          "median_log10_p_value": -0.007829466737979084,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 15,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 9765,
          "median_p_value": 0.9999999999999984,
          "median_log10_p_value": -6.750292265873014e-16,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 7,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 19765,
          "median_p_value": 1.0,
          "median_log10_p_value": 0.0,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 5,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 9765,
          "median_p_value": 1.0,
          "median_log10_p_value": 0.0,
          "status": "ok"
        }
      }
    }
  },
  "grouped_p_value_method": "teacher-tokenizer answer IDs concatenated without separators; exact disjoint blocks; first token of each block is context only; no repetition deduplication; incomplete tail discarded; ordinary median of block p-values (arithmetic mean of the two middle p-values for even group counts)",
  "per_group_p_value_files": {
    "kgw": "/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.grouped_p_values.json",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.grouped_p_values.json"
  },
  "grouped_p_values_without_severe_repetition": {
    "kgw": {
      "aggregation": "ordinary_median",
      "num_answers": 489,
      "total_answer_tokens": 96120,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 96,
          "total_answer_tokens": 96120,
          "discarded_tail_tokens": 120,
          "median_p_value": 0.8913809204225676,
          "median_log10_p_value": -0.04993666601367001,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 48,
          "total_answer_tokens": 96120,
          "discarded_tail_tokens": 120,
          "median_p_value": 0.9822191552453498,
          "median_log10_p_value": -0.007791600507575589,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 32,
          "total_answer_tokens": 96120,
          "discarded_tail_tokens": 120,
          "median_p_value": 0.993786531657336,
          "median_log10_p_value": -0.0027068933487222604,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 9,
          "total_answer_tokens": 96120,
          "discarded_tail_tokens": 6120,
          "median_p_value": 0.9999948367296856,
          "median_log10_p_value": -2.2423855951505638e-06,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 4,
          "total_answer_tokens": 96120,
          "discarded_tail_tokens": 16120,
          "median_p_value": 0.9999999999971494,
          "median_log10_p_value": -1.2379553851888302e-12,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 3,
          "total_answer_tokens": 96120,
          "discarded_tail_tokens": 6120,
          "median_p_value": 0.9999999999836495,
          "median_log10_p_value": -7.100921732769837e-12,
          "status": "ok"
        }
      },
      "filtering": {
        "repetition_threshold": 0.5,
        "comparison": ">",
        "scope": "answer-internal adjacent token pairs; prompt excluded",
        "num_answers_before": 500,
        "num_answers_retained": 489,
        "num_answers_removed": 11,
        "fraction_answers_removed": 0.022,
        "total_answer_tokens_before": 108189,
        "total_answer_tokens_retained": 96120,
        "total_answer_tokens_removed": 12069,
        "removed_answer_ids": [
          "dolly-08884",
          "dolly-09935",
          "dolly-04624",
          "dolly-14700",
          "dolly-08911",
          "dolly-13445",
          "dolly-02451",
          "dolly-08607",
          "dolly-11386",
          "dolly-12065",
          "dolly-01739"
        ]
      }
    },
    "clean": {
      "aggregation": "ordinary_median",
      "num_answers": 412,
      "total_answer_tokens": 45882,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 45,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 882,
          "median_p_value": 0.6360891449864364,
          "median_log10_p_value": -0.1964820156995508,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 22,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 1882,
          "median_p_value": 0.7960378878131416,
          "median_log10_p_value": -0.09906626131183685,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 15,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 882,
          "median_p_value": 0.7386263221105359,
          "median_log10_p_value": -0.13157521964243946,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 4,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 5882,
          "median_p_value": 0.947596846602552,
          "median_log10_p_value": -0.0233763931850151,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 2,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 5882,
          "median_p_value": 0.9783739864832501,
          "median_log10_p_value": -0.009495103065976066,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 1,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 15882,
          "median_p_value": 0.9995678964162934,
          "median_log10_p_value": -0.00018770075802065225,
          "status": "ok"
        }
      },
      "filtering": {
        "repetition_threshold": 0.5,
        "comparison": ">",
        "scope": "answer-internal adjacent token pairs; prompt excluded",
        "num_answers_before": 500,
        "num_answers_retained": 412,
        "num_answers_removed": 88,
        "fraction_answers_removed": 0.176,
        "total_answer_tokens_before": 159765,
        "total_answer_tokens_retained": 45882,
        "total_answer_tokens_removed": 113883,
        "removed_answer_ids": [
          "dolly-00135",
          "dolly-12241",
          "dolly-07923",
          "dolly-07103",
          "dolly-05608",
          "dolly-07788",
          "dolly-11310",
          "dolly-02097",
          "dolly-03614",
          "dolly-13505",
          "dolly-02580",
          "dolly-08884",
          "dolly-12659",
          "dolly-00420",
          "dolly-11014",
          "dolly-08008",
          "dolly-02186",
          "dolly-00275",
          "dolly-08512",
          "dolly-14060",
          "dolly-01461",
          "dolly-02223",
          "dolly-04949",
          "dolly-08689",
          "dolly-08574",
          "dolly-08406",
          "dolly-04141",
          "dolly-03209",
          "dolly-06227",
          "dolly-11078",
          "dolly-09778",
          "dolly-04856",
          "dolly-13779",
          "dolly-06595",
          "dolly-08936",
          "dolly-09344",
          "dolly-05605",
          "dolly-08340",
          "dolly-04589",
          "dolly-04686",
          "dolly-14700",
          "dolly-03696",
          "dolly-03914",
          "dolly-11987",
          "dolly-01939",
          "dolly-05628",
          "dolly-13339",
          "dolly-08911",
          "dolly-03239",
          "dolly-13445",
          "dolly-02139",
          "dolly-14265",
          "dolly-13610",
          "dolly-07427",
          "dolly-09563",
          "dolly-02451",
          "dolly-13544",
          "dolly-06824",
          "dolly-05312",
          "dolly-10992",
          "dolly-06932",
          "dolly-08607",
          "dolly-05388",
          "dolly-11386",
          "dolly-02069",
          "dolly-09439",
          "dolly-00148",
          "dolly-08211",
          "dolly-12186",
          "dolly-03319",
          "dolly-07407",
          "dolly-10389",
          "dolly-03916",
          "dolly-08222",
          "dolly-14947",
          "dolly-03624",
          "dolly-09330",
          "dolly-11182",
          "dolly-02059",
          "dolly-02916",
          "dolly-09816",
          "dolly-05355",
          "dolly-06970",
          "dolly-05634",
          "dolly-02500",
          "dolly-11314",
          "dolly-13235",
          "dolly-04223"
        ]
      }
    }
  },
  "grouped_p_value_without_severe_repetition_method": "exclude whole answers whose answer-internal adjacent-token-pair repetition ratio (1 - unique pairs / all pairs) is strictly greater than 0.5; prompts excluded from repetition assessment; filter each label independently; retain original answer order, then concatenate teacher-tokenizer answer IDs without separators; exact disjoint blocks, first token context only; no token-pair deduplication within retained blocks; incomplete tail discarded; ordinary median of block p-values (mean of the middle two for even counts)",
  "per_group_p_value_without_severe_repetition_files": {
    "kgw": "/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.nonrepetitive_grouped_p_values.json",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.nonrepetitive_grouped_p_values.json"
  },
  "ppl": {
    "enabled": true,
    "schema": "saved-answer-reference-ppl-v1",
    "configuration": {
      "model_path": "/shared/public_models/Llama-3-8B",
      "device": "cuda",
      "dtype": "bfloat16",
      "generation_tokenizer": "/shared/public_models/Qwen2.5-0.5B",
      "max_length": null,
      "overflow": "error",
      "effective_max_length": 8192,
      "protocol": {
        "prompt": "source-generation-prompt; source chat template, not reference chat template",
        "boundary": "encode prompt and answer separately with add_special_tokens=False, then concatenate",
        "bos": "one reference BOS at start when defined; no extra EOS",
        "loss": "causal next-token NLL on all answer tokens, including the first; no prompt or padding loss",
        "aggregate": "exp(sum(answer NLL) / sum(scored answer tokens)); not mean per-answer PPL",
        "source_tokenizer_selection": "explicit override, otherwise row.model_path; fallback assumes the generation tokenizer matches that checkpoint",
        "legacy_prompt_limit": 2048,
        "weights_fingerprint": "weight filenames, sizes and mtime_ns; weight contents are not hashed"
      },
      "reference_assets": {
        "path": "/shared/public_models/Llama-3-8B",
        "assets": [
          {
            "name": "config.json",
            "size": 654,
            "sha256": "2430cee764b6530ff8673cf9ba8561e1d5a33152d503cd0de909ff5718261441"
          },
          {
            "name": "generation_config.json",
            "size": 126,
            "sha256": "55550e95c40c53fb0ee3f960d6d2b25a46405c8f790e5c4bb02caf3e98f2b5d0"
          },
          {
            "name": "model.safetensors.index.json",
            "size": 23950,
            "sha256": "146776fce3f6db1103aa6f249e65ee5544c5923ce6f971b092eee79aa6e5d37b"
          },
          {
            "name": "special_tokens_map.json",
            "size": 73,
            "sha256": "462d91939dbc37178aa5a3eae7068d1990ccc92e09f288cc71f42cdf139d69cc"
          },
          {
            "name": "tokenizer.json",
            "size": 9085698,
            "sha256": "e134af98b985517b4f068e3755ae90d4e9cd2d45d328325dc503f1c6b2d06cc7"
          },
          {
            "name": "tokenizer_config.json",
            "size": 50566,
            "sha256": "690727b4fed286383df1c7ca5e805124cb70c6eb4529f807c7b2e60ff741da7e"
          }
        ],
        "weight_stats": [
          {
            "name": "model-00001-of-00004.safetensors",
            "size": 4976698672,
            "mtime_ns": 1736746522477644778
          },
          {
            "name": "model-00002-of-00004.safetensors",
            "size": 4999802720,
            "mtime_ns": 1736746656058650226
          },
          {
            "name": "model-00003-of-00004.safetensors",
            "size": 4915916176,
            "mtime_ns": 1736746768408654808
          },
          {
            "name": "model-00004-of-00004.safetensors",
            "size": 1168138808,
            "mtime_ns": 1736746796088655937
          }
        ],
        "weight_content_hashed": false
      },
      "software": {
        "python": "3.10.21",
        "torch": "2.6.0",
        "transformers": "4.51.3",
        "tokenizers": "0.21.4"
      }
    },
    "files": {
      "kgw": {
        "samples": 500,
        "valid_samples": 500,
        "skipped_empty_answers": 0,
        "complete": true,
        "nonfinite_samples": 0,
        "status": "ok",
        "total_nll": 119283.93737233058,
        "scored_tokens": 105228,
        "mean_nll": 1.1335760194276292,
        "token_weighted_ppl": 3.1067464450215216,
        "mean_answer_tokens": 210.456,
        "source_prompt_truncated_samples": 3,
        "reference_prompt_truncated_samples": 0,
        "generation_configurations": [
          {
            "configuration": {
              "temperature": 0.7,
              "top_p": 0.9,
              "max_new_tokens": 1536,
              "max_prompt_tokens": 2048,
              "kgw_enabled_during_generation": false
            },
            "samples": 500
          }
        ],
        "generation_seeds": {
          "recorded_samples": 500,
          "minimum": 42,
          "maximum": 541,
          "individual_values": "see per-sample immutable records"
        },
        "student_model_paths": [
          "/shared/wwx/EasyGAD/checkpoints/gad_05b_cleanwarmup_cleangad_control/gad/global_step_1813/actor/huggingface"
        ],
        "generation_tokenizer_paths": [
          "/shared/public_models/Qwen2.5-0.5B"
        ],
        "source_path": "/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl",
        "source_sha256": "dd4cfdbe540e2227bbad3b46f6a64e34bb1a46b7e7d24860ef8be90ec03efd48",
        "per_sample_file": "/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.ppl.2fbd37ec395a4c387a8e.jsonl",
        "cache_reused": false
      },
      "clean": {
        "samples": 500,
        "valid_samples": 500,
        "skipped_empty_answers": 0,
        "complete": true,
        "nonfinite_samples": 0,
        "status": "ok",
        "total_nll": 67054.72902449768,
        "scored_tokens": 156267,
        "mean_nll": 0.42910357928735865,
        "token_weighted_ppl": 1.5358801115260794,
        "mean_answer_tokens": 312.534,
        "source_prompt_truncated_samples": 3,
        "reference_prompt_truncated_samples": 0,
        "generation_configurations": [
          {
            "configuration": {
              "temperature": 0.7,
              "top_p": 0.9,
              "max_new_tokens": 1536,
              "max_prompt_tokens": 2048,
              "kgw_enabled_during_generation": false
            },
            "samples": 500
          }
        ],
        "generation_seeds": {
          "recorded_samples": 500,
          "minimum": 42,
          "maximum": 541,
          "individual_values": "see per-sample immutable records"
        },
        "student_model_paths": [
          "/shared/public_models/Qwen2.5-0.5B"
        ],
        "generation_tokenizer_paths": [
          "/shared/public_models/Qwen2.5-0.5B"
        ],
        "source_path": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl",
        "source_sha256": "597b843d28d31c353c7bb9b94a3b6dccb564cb45ac2c5252f6a1592ccd768efe",
        "per_sample_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.ppl.877fc574f9ee35a5145f.jsonl",
        "cache_reused": false
      }
    }
  },
  "evaluated_at": "2026-10-19T17:13:34+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-10-19T17:15:07+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.462604
- 实际检测配置：`{"gamma": 0.5, "hash_key": 15485863, "seeding": "simple_1 (hash_key * previous_token_id)", "delta_by_label": {"kgw": 2.0, "clean": 2.0}}`
- ROUGE-L（同批 500 条原始 Dolly 回答作参考）：0.209115（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 原始 Dolly 参考文件：`/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl`
- ROUGE-L（同批 500 条 14B clean 教师回答作参考）：0.309962（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 14B clean 教师参考文件：`/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_clean_test.parquet`
- Best F1：0.678450（z 阈值 -5.03309510460972，TPR 0.998000，FPR 0.944000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.000000 | 0.000000 | 0.000000 | None |
  | 5% | 0.050000 | 0.030000 | 0.055556 | 2.2283440581246223 |
  | 10% | 0.100000 | 0.070000 | 0.119658 | 1.7008401285415224 |

两种逐条文本 p-value 统计（单侧正态近似；不是 AUROC 的显著性检验）：

去重规则：相同的 `(previous_token_id, token_id)` 只计一次；不修改回答文本。

| 数据 | 检测方式 | 有效样本 | p 均值 | p 中位数 | p≤0.01 | p≤0.05 | p≤0.10 |
|---|---|---:|---:|---:|---:|---:|---:|
| kgw | 原始 | 500/500 | 0.587914 | 0.658361 | 11 (2.20%) | 36 (7.20%) | 55 (11.00%) |
| kgw | token 对去重 | 500/500 | 0.561811 | 0.599669 | 2 (0.40%) | 22 (4.40%) | 35 (7.00%) |
| clean | 原始 | 500/500 | 0.538121 | 0.57157 | 22 (4.40%) | 54 (10.80%) | 73 (14.60%) |
| clean | token 对去重 | 500/500 | 0.537418 | 0.555154 | 5 (1.00%) | 25 (5.00%) | 46 (9.20%) |

KGW 的小 p 占比是该理论阈值下的检出率，clean 的小 p 占比是实测误报率。p≤0.05 不保证实际 FPR=5%；去重可改善重复带来的失真，但不保证完全校准。空回答不做显著性检验，p=null，并排除在有效样本统计之外。

逐条 p-value：`/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.p_values.jsonl`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl`

固定 token 分组 p-value（普通中位数；p 越大表示原单侧检验证据越弱）：

按教师 tokenizer 编码回答并无分隔拼接，精确分组；每组首 token 仅作上下文，其余 token 用本项目原 KGW 绿表评分；不去重，尾部不足一组丢弃；各组 p 排序后取普通中位数（偶数组取中间两个 p 的算术平均）。

| 每组 token 数 | 计分 token 数 | KGW 组数 | KGW median p ↑ | clean 组数 | clean median p | KGW/clean 丢弃尾部 tokens |
|---:|---:|---:|---:|---:|---:|---:|
| 1000 | 999 | 110 | 0.851774 | 159 | 0.865929 | 315/765 |
| 2000 | 1999 | 55 | 0.968302 | 79 | 0.971358 | 315/1765 |
| 3000 | 2999 | 36 | 0.980464 | 53 | 0.982134 | 2315/765 |
| 10000 | 9999 | 11 | 0.997949 | 15 | 1 | 315/9765 |
| 20000 | 19999 | 5 | 1 | 7 | 1 | 10315/19765 |
| 30000 | 29999 | 3 | 1 | 5 | 1 | 20315/9765 |

N/A 表示总 token 数不足一个完整组；组数为 1 或 2 时需结合逐组结果解释。极小 p 用科学计数法字符串保存，同时保留 log10(p)，避免浮点下溢为 0。

逐组 p-value 缓存：`/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.grouped_p_values.json`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.grouped_p_values.json`

剔除严重重复回答后的固定 token 分组 p-value（普通中位数）：

先独立筛选 KGW 和 clean：回答内部相邻 token 对重复比例严格大于 50% 时，剔除整条回答；prompt 不参与判断。保留回答按原顺序重新无分隔拼接，各组首 token 仅作上下文；组内不做 token 对去重，尾部不足一组丢弃。这是质量筛选补充指标，原始全样本统计另行保留。

| 数据 | 原回答数 | 剔除严重重复回答 | 保留回答数 | 原 tokens | 剔除 tokens | 保留 tokens |
|---|---:|---:|---:|---:|---:|---:|
| kgw | 500 | 15 (3.00%) | 485 | 110315 | 10798 | 99517 |
| clean | 500 | 88 (17.60%) | 412 | 159765 | 113883 | 45882 |

| 每组 token 数 | 计分 token 数 | KGW 组数 | KGW median p ↑ | clean 组数 | clean median p | KGW/clean 丢弃尾部 tokens |
|---:|---:|---:|---:|---:|---:|---:|
| 1000 | 999 | 99 | 0.851774 | 45 | 0.636089 | 517/882 |
| 2000 | 1999 | 49 | 0.96138 | 22 | 0.796038 | 1517/1882 |
| 3000 | 2999 | 33 | 0.961742 | 15 | 0.738626 | 517/882 |
| 10000 | 9999 | 9 | 0.999698 | 4 | 0.947597 | 9517/5882 |
| 20000 | 19999 | 4 | 0.999998 | 2 | 0.978374 | 19517/5882 |
| 30000 | 29999 | 3 | 1 | 1 | 0.999568 | 9517/15882 |

N/A 表示筛选后不足一个完整组。各组 p 取普通中位数，偶数组取中间两个 p 的算术平均；组数较少时请结合逐组缓存解释。

剔除严重重复回答后的逐组 p-value 缓存：`/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.nonrepetitive_grouped_p_values.json`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.nonrepetitive_grouped_p_values.json`

### 固定参考模型 PPL（只评分已保存的回答）

| 文件组 | 总体 PPL ↓ | 有效样本/总样本 | 计分回答 tokens | 平均回答 tokens | 状态 | 缓存复用 |
|---|---:|---:|---:|---:|---|---|
| kgw | 3.571931 | 500/500 | 108367 | 216.73 | ok | False |
| clean | 1.535880 | 500/500 | 156267 | 312.53 | ok | True |

总体 PPL = exp(全部有效回答 NLL 总和 / 全部计分回答 token 数)，不是逐条 PPL 的算术平均。
原生成 tokenizer 恢复实际生成 prompt；参考 tokenizer 对 prompt/answer 分开编码后拼接；只计回答，包含首回答 token。Base 参考模型不再套用 chat template；只添加一次参考 BOS，不额外评分 EOS；输入 JSONL 不修改。

- kgw: `/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl`；SHA256 `a544802bd1d1b310dec9bb254958b3386c3692ae848346b77eb36bfe64d96c74`；逐条明细 `/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.ppl.3f65ad2ad246b50e822c.jsonl`；空回答 0；异常 loss 0；原生成截断 3；参考上下文截断 0。

  生成文本配置（种子逐条保存在明细中）：

```json
{
  "student_model_paths": [
    "/shared/wwx/EasyGAD/checkpoints/gad_05b_cleanwarmup_cleangad_control/warmup/global_step_1813/actor/huggingface"
  ],
  "generation_tokenizer_paths": [
    "/shared/public_models/Qwen2.5-0.5B"
  ],
  "generation_configurations": [
    {
      "configuration": {
        "temperature": 0.7,
        "top_p": 0.9,
        "max_new_tokens": 1536,
        "max_prompt_tokens": 2048,
        "kgw_enabled_during_generation": false
      },
      "samples": 500
    }
  ],
  "generation_seeds": {
    "recorded_samples": 500,
    "minimum": 42,
    "maximum": 541,
    "individual_values": "see per-sample immutable records"
  }
}
```
- clean: `/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl`；SHA256 `597b843d28d31c353c7bb9b94a3b6dccb564cb45ac2c5252f6a1592ccd768efe`；逐条明细 `/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.ppl.877fc574f9ee35a5145f.jsonl`；空回答 0；异常 loss 0；原生成截断 3；参考上下文截断 0。

  生成文本配置（种子逐条保存在明细中）：

```json
{
  "student_model_paths": [
    "/shared/public_models/Qwen2.5-0.5B"
  ],
  "generation_tokenizer_paths": [
    "/shared/public_models/Qwen2.5-0.5B"
  ],
  "generation_configurations": [
    {
      "configuration": {
        "kgw_enabled_during_generation": false,
        "max_new_tokens": 1536,
        "max_prompt_tokens": 2048,
        "temperature": 0.7,
        "top_p": 0.9
      },
      "samples": 500
    }
  ],
  "generation_seeds": {
    "recorded_samples": 500,
    "minimum": 42,
    "maximum": 541,
    "individual_values": "see per-sample immutable records"
  }
}
```

完整评分配置（含模型/tokenizer 指纹、软件版本；权重使用 size/mtime 标识，不全量哈希）：

```json
{
  "model_path": "/shared/public_models/Llama-3-8B",
  "device": "cuda",
  "dtype": "bfloat16",
  "generation_tokenizer": "/shared/public_models/Qwen2.5-0.5B",
  "max_length": null,
  "overflow": "error",
  "effective_max_length": 8192,
  "protocol": {
    "prompt": "source-generation-prompt; source chat template, not reference chat template",
    "boundary": "encode prompt and answer separately with add_special_tokens=False, then concatenate",
    "bos": "one reference BOS at start when defined; no extra EOS",
    "loss": "causal next-token NLL on all answer tokens, including the first; no prompt or padding loss",
    "aggregate": "exp(sum(answer NLL) / sum(scored answer tokens)); not mean per-answer PPL",
    "source_tokenizer_selection": "explicit override, otherwise row.model_path; fallback assumes the generation tokenizer matches that checkpoint",
    "legacy_prompt_limit": 2048,
    "weights_fingerprint": "weight filenames, sizes and mtime_ns; weight contents are not hashed"
  },
  "reference_assets": {
    "path": "/shared/public_models/Llama-3-8B",
    "assets": [
      {
        "name": "config.json",
        "size": 654,
        "sha256": "2430cee764b6530ff8673cf9ba8561e1d5a33152d503cd0de909ff5718261441"
      },
      {
        "name": "generation_config.json",
        "size": 126,
        "sha256": "55550e95c40c53fb0ee3f960d6d2b25a46405c8f790e5c4bb02caf3e98f2b5d0"
      },
      {
        "name": "model.safetensors.index.json",
        "size": 23950,
        "sha256": "146776fce3f6db1103aa6f249e65ee5544c5923ce6f971b092eee79aa6e5d37b"
      },
      {
        "name": "special_tokens_map.json",
        "size": 73,
        "sha256": "462d91939dbc37178aa5a3eae7068d1990ccc92e09f288cc71f42cdf139d69cc"
      },
      {
        "name": "tokenizer.json",
        "size": 9085698,
        "sha256": "e134af98b985517b4f068e3755ae90d4e9cd2d45d328325dc503f1c6b2d06cc7"
      },
      {
        "name": "tokenizer_config.json",
        "size": 50566,
        "sha256": "690727b4fed286383df1c7ca5e805124cb70c6eb4529f807c7b2e60ff741da7e"
      }
    ],
    "weight_stats": [
      {
        "name": "model-00001-of-00004.safetensors",
        "size": 4976698672,
        "mtime_ns": 1736746522477644778
      },
      {
        "name": "model-00002-of-00004.safetensors",
        "size": 4999802720,
        "mtime_ns": 1736746656058650226
      },
      {
        "name": "model-00003-of-00004.safetensors",
        "size": 4915916176,
        "mtime_ns": 1736746768408654808
      },
      {
        "name": "model-00004-of-00004.safetensors",
        "size": 1168138808,
        "mtime_ns": 1736746796088655937
      }
    ],
    "weight_content_hashed": false
  },
  "software": {
    "python": "3.10.21",
    "torch": "2.6.0",
    "transformers": "4.51.3",
    "tokenizers": "0.21.4"
  }
}
```

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.4626040000000001,
  "best_f1": {
    "threshold": -5.03309510460972,
    "fpr": 0.944,
    "tpr": 0.998,
    "precision": 0.513903192584964,
    "f1": 0.6784500339904826,
    "tp": 499,
    "fp": 472,
    "tn": 28,
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
      "threshold": 2.2283440581246223,
      "fpr": 0.05,
      "tpr": 0.03,
      "precision": 0.375,
      "f1": 0.05555555555555555,
      "tp": 15,
      "fp": 25,
      "tn": 475,
      "fn": 485,
      "target_fpr": 0.05
    },
    "10%": {
      "threshold": 1.7008401285415224,
      "fpr": 0.1,
      "tpr": 0.07,
      "precision": 0.4117647058823529,
      "f1": 0.11965811965811966,
      "tp": 35,
      "fp": 50,
      "tn": 450,
      "fn": 465,
      "target_fpr": 0.1
    }
  },
  "note": "For each target FPR, select the empirical ROC point with the highest TPR whose FPR does not exceed the target; tied scores are kept together.",
  "detector_config": {
    "gamma": 0.5,
    "hash_key": 15485863,
    "seeding": "simple_1 (hash_key * previous_token_id)",
    "delta_by_label": {
      "kgw": 2.0,
      "clean": 2.0
    }
  },
  "rouge_l_dolly": {
    "mean": 0.20911479663899177,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl",
    "reference_file": "/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl",
    "reference_source": "databricks/databricks-dolly-15k:response",
    "metric": "rougeL",
    "measure": "fmeasure",
    "use_stemmer": true,
    "aggregation": "unweighted mean of per-sample ROUGE-L F1"
  },
  "rouge_l_teacher_clean": {
    "mean": 0.30996181867715505,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl",
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
        "mean": 0.587913978437283,
        "median": 0.658361434051861,
        "min": 0.002197952486763932,
        "max": 0.9999999978094234,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 11,
            "fraction": 0.022
          },
          "5%": {
            "alpha": 0.05,
            "count": 36,
            "fraction": 0.072
          },
          "10%": {
            "alpha": 0.1,
            "count": 55,
            "fraction": 0.11
          }
        }
      },
      "deduplicated": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.5618113459887325,
        "median": 0.5996692153351387,
        "min": 0.00921106272704951,
        "max": 0.9997579313716072,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 2,
            "fraction": 0.004
          },
          "5%": {
            "alpha": 0.05,
            "count": 22,
            "fraction": 0.044
          },
          "10%": {
            "alpha": 0.1,
            "count": 35,
            "fraction": 0.07
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
    "kgw": "/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.p_values.jsonl",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl"
  },
  "grouped_p_values": {
    "kgw": {
      "aggregation": "ordinary_median",
      "num_answers": 500,
      "total_answer_tokens": 110315,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 110,
          "total_answer_tokens": 110315,
          "discarded_tail_tokens": 315,
          "median_p_value": 0.8517743756590758,
          "median_log10_p_value": -0.06967542915691224,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 55,
          "total_answer_tokens": 110315,
          "discarded_tail_tokens": 315,
          "median_p_value": 0.9683017588985491,
          "median_log10_p_value": -0.013989279259781976,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 36,
          "total_answer_tokens": 110315,
          "discarded_tail_tokens": 2315,
          "median_p_value": 0.9804642099767789,
          "median_log10_p_value": -0.008568254819532509,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 11,
          "total_answer_tokens": 110315,
          "discarded_tail_tokens": 315,
          "median_p_value": 0.9979485722951797,
          "median_log10_p_value": -0.0008918388167411366,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 5,
          "total_answer_tokens": 110315,
          "discarded_tail_tokens": 10315,
          "median_p_value": 0.9999999196212623,
          "median_log10_p_value": -3.490804363351823e-08,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 3,
          "total_answer_tokens": 110315,
          "discarded_tail_tokens": 20315,
          "median_p_value": 0.9999999983699949,
          "median_log10_p_value": -7.079022343879514e-10,
          "status": "ok"
        }
      }
    },
    "clean": {
      "aggregation": "ordinary_median",
      "num_answers": 500,
      "total_answer_tokens": 159765,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 159,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 765,
          "median_p_value": 0.8659288977499955,
          "median_log10_p_value": -0.06251776685396769,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 79,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 1765,
          "median_p_value": 0.971357711016285,
          "median_log10_p_value": -0.012620807875598238,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 53,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 765,
          "median_p_value": 0.9821335190767914,
          "median_log10_p_value": -0.007829466737979084,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 15,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 9765,
          "median_p_value": 0.9999999999999984,
          "median_log10_p_value": -6.750292265873014e-16,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 7,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 19765,
          "median_p_value": 1.0,
          "median_log10_p_value": 0.0,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 5,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 9765,
          "median_p_value": 1.0,
          "median_log10_p_value": 0.0,
          "status": "ok"
        }
      }
    }
  },
  "grouped_p_value_method": "teacher-tokenizer answer IDs concatenated without separators; exact disjoint blocks; first token of each block is context only; no repetition deduplication; incomplete tail discarded; ordinary median of block p-values (arithmetic mean of the two middle p-values for even group counts)",
  "per_group_p_value_files": {
    "kgw": "/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.grouped_p_values.json",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.grouped_p_values.json"
  },
  "grouped_p_values_without_severe_repetition": {
    "kgw": {
      "aggregation": "ordinary_median",
      "num_answers": 485,
      "total_answer_tokens": 99517,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 99,
          "total_answer_tokens": 99517,
          "discarded_tail_tokens": 517,
          "median_p_value": 0.8517743756590758,
          "median_log10_p_value": -0.06967542915691224,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 49,
          "total_answer_tokens": 99517,
          "discarded_tail_tokens": 1517,
          "median_p_value": 0.9613804838256327,
          "median_log10_p_value": -0.017104698363877752,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 33,
          "total_answer_tokens": 99517,
          "discarded_tail_tokens": 517,
          "median_p_value": 0.9617416641553246,
          "median_log10_p_value": -0.016941569229135967,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 9,
          "total_answer_tokens": 99517,
          "discarded_tail_tokens": 9517,
          "median_p_value": 0.999698400080992,
          "median_log10_p_value": -0.00013100293679839522,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 4,
          "total_answer_tokens": 99517,
          "discarded_tail_tokens": 19517,
          "median_p_value": 0.9999979012264593,
          "median_log10_p_value": -9.114867240411086e-07,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 3,
          "total_answer_tokens": 99517,
          "discarded_tail_tokens": 9517,
          "median_p_value": 0.9999999073746251,
          "median_log10_p_value": -4.0226691077415586e-08,
          "status": "ok"
        }
      },
      "filtering": {
        "repetition_threshold": 0.5,
        "comparison": ">",
        "scope": "answer-internal adjacent token pairs; prompt excluded",
        "num_answers_before": 500,
        "num_answers_retained": 485,
        "num_answers_removed": 15,
        "fraction_answers_removed": 0.03,
        "total_answer_tokens_before": 110315,
        "total_answer_tokens_retained": 99517,
        "total_answer_tokens_removed": 10798,
        "removed_answer_ids": [
          "dolly-07923",
          "dolly-08884",
          "dolly-01092",
          "dolly-02516",
          "dolly-02725",
          "dolly-03239",
          "dolly-13445",
          "dolly-03231",
          "dolly-08607",
          "dolly-11386",
          "dolly-03319",
          "dolly-05355",
          "dolly-01356",
          "dolly-12236",
          "dolly-13235"
        ]
      }
    },
    "clean": {
      "aggregation": "ordinary_median",
      "num_answers": 412,
      "total_answer_tokens": 45882,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 45,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 882,
          "median_p_value": 0.6360891449864364,
          "median_log10_p_value": -0.1964820156995508,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 22,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 1882,
          "median_p_value": 0.7960378878131416,
          "median_log10_p_value": -0.09906626131183685,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 15,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 882,
          "median_p_value": 0.7386263221105359,
          "median_log10_p_value": -0.13157521964243946,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 4,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 5882,
          "median_p_value": 0.947596846602552,
          "median_log10_p_value": -0.0233763931850151,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 2,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 5882,
          "median_p_value": 0.9783739864832501,
          "median_log10_p_value": -0.009495103065976066,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 1,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 15882,
          "median_p_value": 0.9995678964162934,
          "median_log10_p_value": -0.00018770075802065225,
          "status": "ok"
        }
      },
      "filtering": {
        "repetition_threshold": 0.5,
        "comparison": ">",
        "scope": "answer-internal adjacent token pairs; prompt excluded",
        "num_answers_before": 500,
        "num_answers_retained": 412,
        "num_answers_removed": 88,
        "fraction_answers_removed": 0.176,
        "total_answer_tokens_before": 159765,
        "total_answer_tokens_retained": 45882,
        "total_answer_tokens_removed": 113883,
        "removed_answer_ids": [
          "dolly-00135",
          "dolly-12241",
          "dolly-07923",
          "dolly-07103",
          "dolly-05608",
          "dolly-07788",
          "dolly-11310",
          "dolly-02097",
          "dolly-03614",
          "dolly-13505",
          "dolly-02580",
          "dolly-08884",
          "dolly-12659",
          "dolly-00420",
          "dolly-11014",
          "dolly-08008",
          "dolly-02186",
          "dolly-00275",
          "dolly-08512",
          "dolly-14060",
          "dolly-01461",
          "dolly-02223",
          "dolly-04949",
          "dolly-08689",
          "dolly-08574",
          "dolly-08406",
          "dolly-04141",
          "dolly-03209",
          "dolly-06227",
          "dolly-11078",
          "dolly-09778",
          "dolly-04856",
          "dolly-13779",
          "dolly-06595",
          "dolly-08936",
          "dolly-09344",
          "dolly-05605",
          "dolly-08340",
          "dolly-04589",
          "dolly-04686",
          "dolly-14700",
          "dolly-03696",
          "dolly-03914",
          "dolly-11987",
          "dolly-01939",
          "dolly-05628",
          "dolly-13339",
          "dolly-08911",
          "dolly-03239",
          "dolly-13445",
          "dolly-02139",
          "dolly-14265",
          "dolly-13610",
          "dolly-07427",
          "dolly-09563",
          "dolly-02451",
          "dolly-13544",
          "dolly-06824",
          "dolly-05312",
          "dolly-10992",
          "dolly-06932",
          "dolly-08607",
          "dolly-05388",
          "dolly-11386",
          "dolly-02069",
          "dolly-09439",
          "dolly-00148",
          "dolly-08211",
          "dolly-12186",
          "dolly-03319",
          "dolly-07407",
          "dolly-10389",
          "dolly-03916",
          "dolly-08222",
          "dolly-14947",
          "dolly-03624",
          "dolly-09330",
          "dolly-11182",
          "dolly-02059",
          "dolly-02916",
          "dolly-09816",
          "dolly-05355",
          "dolly-06970",
          "dolly-05634",
          "dolly-02500",
          "dolly-11314",
          "dolly-13235",
          "dolly-04223"
        ]
      }
    }
  },
  "grouped_p_value_without_severe_repetition_method": "exclude whole answers whose answer-internal adjacent-token-pair repetition ratio (1 - unique pairs / all pairs) is strictly greater than 0.5; prompts excluded from repetition assessment; filter each label independently; retain original answer order, then concatenate teacher-tokenizer answer IDs without separators; exact disjoint blocks, first token context only; no token-pair deduplication within retained blocks; incomplete tail discarded; ordinary median of block p-values (mean of the middle two for even counts)",
  "per_group_p_value_without_severe_repetition_files": {
    "kgw": "/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.nonrepetitive_grouped_p_values.json",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.nonrepetitive_grouped_p_values.json"
  },
  "ppl": {
    "enabled": true,
    "schema": "saved-answer-reference-ppl-v1",
    "configuration": {
      "model_path": "/shared/public_models/Llama-3-8B",
      "device": "cuda",
      "dtype": "bfloat16",
      "generation_tokenizer": "/shared/public_models/Qwen2.5-0.5B",
      "max_length": null,
      "overflow": "error",
      "effective_max_length": 8192,
      "protocol": {
        "prompt": "source-generation-prompt; source chat template, not reference chat template",
        "boundary": "encode prompt and answer separately with add_special_tokens=False, then concatenate",
        "bos": "one reference BOS at start when defined; no extra EOS",
        "loss": "causal next-token NLL on all answer tokens, including the first; no prompt or padding loss",
        "aggregate": "exp(sum(answer NLL) / sum(scored answer tokens)); not mean per-answer PPL",
        "source_tokenizer_selection": "explicit override, otherwise row.model_path; fallback assumes the generation tokenizer matches that checkpoint",
        "legacy_prompt_limit": 2048,
        "weights_fingerprint": "weight filenames, sizes and mtime_ns; weight contents are not hashed"
      },
      "reference_assets": {
        "path": "/shared/public_models/Llama-3-8B",
        "assets": [
          {
            "name": "config.json",
            "size": 654,
            "sha256": "2430cee764b6530ff8673cf9ba8561e1d5a33152d503cd0de909ff5718261441"
          },
          {
            "name": "generation_config.json",
            "size": 126,
            "sha256": "55550e95c40c53fb0ee3f960d6d2b25a46405c8f790e5c4bb02caf3e98f2b5d0"
          },
          {
            "name": "model.safetensors.index.json",
            "size": 23950,
            "sha256": "146776fce3f6db1103aa6f249e65ee5544c5923ce6f971b092eee79aa6e5d37b"
          },
          {
            "name": "special_tokens_map.json",
            "size": 73,
            "sha256": "462d91939dbc37178aa5a3eae7068d1990ccc92e09f288cc71f42cdf139d69cc"
          },
          {
            "name": "tokenizer.json",
            "size": 9085698,
            "sha256": "e134af98b985517b4f068e3755ae90d4e9cd2d45d328325dc503f1c6b2d06cc7"
          },
          {
            "name": "tokenizer_config.json",
            "size": 50566,
            "sha256": "690727b4fed286383df1c7ca5e805124cb70c6eb4529f807c7b2e60ff741da7e"
          }
        ],
        "weight_stats": [
          {
            "name": "model-00001-of-00004.safetensors",
            "size": 4976698672,
            "mtime_ns": 1736746522477644778
          },
          {
            "name": "model-00002-of-00004.safetensors",
            "size": 4999802720,
            "mtime_ns": 1736746656058650226
          },
          {
            "name": "model-00003-of-00004.safetensors",
            "size": 4915916176,
            "mtime_ns": 1736746768408654808
          },
          {
            "name": "model-00004-of-00004.safetensors",
            "size": 1168138808,
            "mtime_ns": 1736746796088655937
          }
        ],
        "weight_content_hashed": false
      },
      "software": {
        "python": "3.10.21",
        "torch": "2.6.0",
        "transformers": "4.51.3",
        "tokenizers": "0.21.4"
      }
    },
    "files": {
      "kgw": {
        "samples": 500,
        "valid_samples": 500,
        "skipped_empty_answers": 0,
        "complete": true,
        "nonfinite_samples": 0,
        "status": "ok",
        "total_nll": 137962.72345853038,
        "scored_tokens": 108367,
        "mean_nll": 1.2731064203911742,
        "token_weighted_ppl": 3.571931266011677,
        "mean_answer_tokens": 216.734,
        "source_prompt_truncated_samples": 3,
        "reference_prompt_truncated_samples": 0,
        "generation_configurations": [
          {
            "configuration": {
              "temperature": 0.7,
              "top_p": 0.9,
              "max_new_tokens": 1536,
              "max_prompt_tokens": 2048,
              "kgw_enabled_during_generation": false
            },
            "samples": 500
          }
        ],
        "generation_seeds": {
          "recorded_samples": 500,
          "minimum": 42,
          "maximum": 541,
          "individual_values": "see per-sample immutable records"
        },
        "student_model_paths": [
          "/shared/wwx/EasyGAD/checkpoints/gad_05b_cleanwarmup_cleangad_control/warmup/global_step_1813/actor/huggingface"
        ],
        "generation_tokenizer_paths": [
          "/shared/public_models/Qwen2.5-0.5B"
        ],
        "source_path": "/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl",
        "source_sha256": "a544802bd1d1b310dec9bb254958b3386c3692ae848346b77eb36bfe64d96c74",
        "per_sample_file": "/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.ppl.3f65ad2ad246b50e822c.jsonl",
        "cache_reused": false
      },
      "clean": {
        "samples": 500,
        "valid_samples": 500,
        "skipped_empty_answers": 0,
        "complete": true,
        "nonfinite_samples": 0,
        "status": "ok",
        "total_nll": 67054.72902449768,
        "scored_tokens": 156267,
        "mean_nll": 0.42910357928735865,
        "token_weighted_ppl": 1.5358801115260794,
        "mean_answer_tokens": 312.534,
        "source_prompt_truncated_samples": 3,
        "reference_prompt_truncated_samples": 0,
        "generation_configurations": [
          {
            "configuration": {
              "kgw_enabled_during_generation": false,
              "max_new_tokens": 1536,
              "max_prompt_tokens": 2048,
              "temperature": 0.7,
              "top_p": 0.9
            },
            "samples": 500
          }
        ],
        "generation_seeds": {
          "recorded_samples": 500,
          "minimum": 42,
          "maximum": 541,
          "individual_values": "see per-sample immutable records"
        },
        "student_model_paths": [
          "/shared/public_models/Qwen2.5-0.5B"
        ],
        "generation_tokenizer_paths": [
          "/shared/public_models/Qwen2.5-0.5B"
        ],
        "source_path": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl",
        "source_sha256": "597b843d28d31c353c7bb9b94a3b6dccb564cb45ac2c5252f6a1592ccd768efe",
        "per_sample_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.ppl.877fc574f9ee35a5145f.jsonl",
        "cache_reused": true
      }
    }
  },
  "evaluated_at": "2026-10-19T17:15:07+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-10-19T17:16:58+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.531456
- 实际检测配置：`{"gamma": 0.5, "hash_key": 15485863, "seeding": "simple_1 (hash_key * previous_token_id)", "delta_by_label": {"kgw": 3.0, "clean": 2.0}}`
- ROUGE-L（同批 500 条原始 Dolly 回答作参考）：0.211098（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 原始 Dolly 参考文件：`/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl`
- ROUGE-L（同批 500 条 14B clean 教师回答作参考）：0.262207（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 14B clean 教师参考文件：`/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_clean_test.parquet`
- Best F1：0.675396（z 阈值 -3.2716515254078793，TPR 0.980000，FPR 0.922000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.002000 | 0.002000 | 0.003984 | 37.201625468519524 |
  | 5% | 0.046000 | 0.038000 | 0.070111 | 2.2541740866685807 |
  | 10% | 0.100000 | 0.084000 | 0.141892 | 1.6924558427507104 |

两种逐条文本 p-value 统计（单侧正态近似；不是 AUROC 的显著性检验）：

去重规则：相同的 `(previous_token_id, token_id)` 只计一次；不修改回答文本。

| 数据 | 检测方式 | 有效样本 | p 均值 | p 中位数 | p≤0.01 | p≤0.05 | p≤0.10 |
|---|---|---:|---:|---:|---:|---:|---:|
| kgw | 原始 | 500/500 | 0.505501 | 0.5 | 16 (3.20%) | 44 (8.80%) | 71 (14.20%) |
| kgw | token 对去重 | 500/500 | 0.516716 | 0.544534 | 2 (0.40%) | 25 (5.00%) | 41 (8.20%) |
| clean | 原始 | 500/500 | 0.538121 | 0.57157 | 22 (4.40%) | 54 (10.80%) | 73 (14.60%) |
| clean | token 对去重 | 500/500 | 0.537418 | 0.555154 | 5 (1.00%) | 25 (5.00%) | 46 (9.20%) |

KGW 的小 p 占比是该理论阈值下的检出率，clean 的小 p 占比是实测误报率。p≤0.05 不保证实际 FPR=5%；去重可改善重复带来的失真，但不保证完全校准。空回答不做显著性检验，p=null，并排除在有效样本统计之外。

逐条 p-value：`/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta3_new1_qwen2_5_0_5b_dolly15k_test.p_values.jsonl`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl`

固定 token 分组 p-value（普通中位数；p 越大表示原单侧检验证据越弱）：

按教师 tokenizer 编码回答并无分隔拼接，精确分组；每组首 token 仅作上下文，其余 token 用本项目原 KGW 绿表评分；不去重，尾部不足一组丢弃；各组 p 排序后取普通中位数（偶数组取中间两个 p 的算术平均）。

| 每组 token 数 | 计分 token 数 | KGW 组数 | KGW median p ↑ | clean 组数 | clean median p | KGW/clean 丢弃尾部 tokens |
|---:|---:|---:|---:|---:|---:|---:|
| 1000 | 999 | 70 | 0.647832 | 159 | 0.865929 | 907/765 |
| 2000 | 1999 | 35 | 0.631374 | 79 | 0.971358 | 907/1765 |
| 3000 | 2999 | 23 | 0.550856 | 53 | 0.982134 | 1907/765 |
| 10000 | 9999 | 7 | 0.979823 | 15 | 1 | 907/9765 |
| 20000 | 19999 | 3 | 0.986561 | 7 | 1 | 10907/19765 |
| 30000 | 29999 | 2 | 0.500352 | 5 | 1 | 10907/9765 |

N/A 表示总 token 数不足一个完整组；组数为 1 或 2 时需结合逐组结果解释。极小 p 用科学计数法字符串保存，同时保留 log10(p)，避免浮点下溢为 0。

逐组 p-value 缓存：`/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta3_new1_qwen2_5_0_5b_dolly15k_test.grouped_p_values.json`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.grouped_p_values.json`

剔除严重重复回答后的固定 token 分组 p-value（普通中位数）：

先独立筛选 KGW 和 clean：回答内部相邻 token 对重复比例严格大于 50% 时，剔除整条回答；prompt 不参与判断。保留回答按原顺序重新无分隔拼接，各组首 token 仅作上下文；组内不做 token 对去重，尾部不足一组丢弃。这是质量筛选补充指标，原始全样本统计另行保留。

| 数据 | 原回答数 | 剔除严重重复回答 | 保留回答数 | 原 tokens | 剔除 tokens | 保留 tokens |
|---|---:|---:|---:|---:|---:|---:|
| kgw | 500 | 15 (3.00%) | 485 | 70907 | 14061 | 56846 |
| clean | 500 | 88 (17.60%) | 412 | 159765 | 113883 | 45882 |

| 每组 token 数 | 计分 token 数 | KGW 组数 | KGW median p ↑ | clean 组数 | clean median p | KGW/clean 丢弃尾部 tokens |
|---:|---:|---:|---:|---:|---:|---:|
| 1000 | 999 | 56 | 0.562723 | 45 | 0.636089 | 846/882 |
| 2000 | 1999 | 28 | 0.535635 | 22 | 0.796038 | 846/1882 |
| 3000 | 2999 | 18 | 0.514506 | 15 | 0.738626 | 2846/882 |
| 10000 | 9999 | 5 | 0.680831 | 4 | 0.947597 | 6846/5882 |
| 20000 | 19999 | 2 | 0.661378 | 2 | 0.978374 | 16846/5882 |
| 30000 | 29999 | 1 | 0.841062 | 1 | 0.999568 | 26846/15882 |

N/A 表示筛选后不足一个完整组。各组 p 取普通中位数，偶数组取中间两个 p 的算术平均；组数较少时请结合逐组缓存解释。

剔除严重重复回答后的逐组 p-value 缓存：`/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta3_new1_qwen2_5_0_5b_dolly15k_test.nonrepetitive_grouped_p_values.json`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.nonrepetitive_grouped_p_values.json`

### 固定参考模型 PPL（只评分已保存的回答）

| 文件组 | 总体 PPL ↓ | 有效样本/总样本 | 计分回答 tokens | 平均回答 tokens | 状态 | 缓存复用 |
|---|---:|---:|---:|---:|---|---|
| kgw | 3.417079 | 500/500 | 69402 | 138.80 | ok | False |
| clean | 1.535880 | 500/500 | 156267 | 312.53 | ok | True |

总体 PPL = exp(全部有效回答 NLL 总和 / 全部计分回答 token 数)，不是逐条 PPL 的算术平均。
原生成 tokenizer 恢复实际生成 prompt；参考 tokenizer 对 prompt/answer 分开编码后拼接；只计回答，包含首回答 token。Base 参考模型不再套用 chat template；只添加一次参考 BOS，不额外评分 EOS；输入 JSONL 不修改。

- kgw: `/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta3_new1_qwen2_5_0_5b_dolly15k_test.jsonl`；SHA256 `b1c02a02c9e074669d99cc9965618971b50b81e66d62c386002cdde73652f192`；逐条明细 `/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta3_new1_qwen2_5_0_5b_dolly15k_test.ppl.444a5089035b343829bc.jsonl`；空回答 0；异常 loss 0；原生成截断 3；参考上下文截断 0。

  生成文本配置（种子逐条保存在明细中）：

```json
{
  "student_model_paths": [
    "/shared/wwx/EasyGAD/checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_new1_dipper2stage/gad/global_step_1813/actor/huggingface"
  ],
  "generation_tokenizer_paths": [
    "/shared/public_models/Qwen2.5-0.5B"
  ],
  "generation_configurations": [
    {
      "configuration": {
        "temperature": 0.7,
        "top_p": 0.9,
        "max_new_tokens": 1536,
        "max_prompt_tokens": 2048,
        "kgw_enabled_during_generation": false
      },
      "samples": 500
    }
  ],
  "generation_seeds": {
    "recorded_samples": 500,
    "minimum": 42,
    "maximum": 541,
    "individual_values": "see per-sample immutable records"
  }
}
```
- clean: `/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl`；SHA256 `597b843d28d31c353c7bb9b94a3b6dccb564cb45ac2c5252f6a1592ccd768efe`；逐条明细 `/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.ppl.877fc574f9ee35a5145f.jsonl`；空回答 0；异常 loss 0；原生成截断 3；参考上下文截断 0。

  生成文本配置（种子逐条保存在明细中）：

```json
{
  "student_model_paths": [
    "/shared/public_models/Qwen2.5-0.5B"
  ],
  "generation_tokenizer_paths": [
    "/shared/public_models/Qwen2.5-0.5B"
  ],
  "generation_configurations": [
    {
      "configuration": {
        "kgw_enabled_during_generation": false,
        "max_new_tokens": 1536,
        "max_prompt_tokens": 2048,
        "temperature": 0.7,
        "top_p": 0.9
      },
      "samples": 500
    }
  ],
  "generation_seeds": {
    "recorded_samples": 500,
    "minimum": 42,
    "maximum": 541,
    "individual_values": "see per-sample immutable records"
  }
}
```

完整评分配置（含模型/tokenizer 指纹、软件版本；权重使用 size/mtime 标识，不全量哈希）：

```json
{
  "model_path": "/shared/public_models/Llama-3-8B",
  "device": "cuda",
  "dtype": "bfloat16",
  "generation_tokenizer": "/shared/public_models/Qwen2.5-0.5B",
  "max_length": null,
  "overflow": "error",
  "effective_max_length": 8192,
  "protocol": {
    "prompt": "source-generation-prompt; source chat template, not reference chat template",
    "boundary": "encode prompt and answer separately with add_special_tokens=False, then concatenate",
    "bos": "one reference BOS at start when defined; no extra EOS",
    "loss": "causal next-token NLL on all answer tokens, including the first; no prompt or padding loss",
    "aggregate": "exp(sum(answer NLL) / sum(scored answer tokens)); not mean per-answer PPL",
    "source_tokenizer_selection": "explicit override, otherwise row.model_path; fallback assumes the generation tokenizer matches that checkpoint",
    "legacy_prompt_limit": 2048,
    "weights_fingerprint": "weight filenames, sizes and mtime_ns; weight contents are not hashed"
  },
  "reference_assets": {
    "path": "/shared/public_models/Llama-3-8B",
    "assets": [
      {
        "name": "config.json",
        "size": 654,
        "sha256": "2430cee764b6530ff8673cf9ba8561e1d5a33152d503cd0de909ff5718261441"
      },
      {
        "name": "generation_config.json",
        "size": 126,
        "sha256": "55550e95c40c53fb0ee3f960d6d2b25a46405c8f790e5c4bb02caf3e98f2b5d0"
      },
      {
        "name": "model.safetensors.index.json",
        "size": 23950,
        "sha256": "146776fce3f6db1103aa6f249e65ee5544c5923ce6f971b092eee79aa6e5d37b"
      },
      {
        "name": "special_tokens_map.json",
        "size": 73,
        "sha256": "462d91939dbc37178aa5a3eae7068d1990ccc92e09f288cc71f42cdf139d69cc"
      },
      {
        "name": "tokenizer.json",
        "size": 9085698,
        "sha256": "e134af98b985517b4f068e3755ae90d4e9cd2d45d328325dc503f1c6b2d06cc7"
      },
      {
        "name": "tokenizer_config.json",
        "size": 50566,
        "sha256": "690727b4fed286383df1c7ca5e805124cb70c6eb4529f807c7b2e60ff741da7e"
      }
    ],
    "weight_stats": [
      {
        "name": "model-00001-of-00004.safetensors",
        "size": 4976698672,
        "mtime_ns": 1736746522477644778
      },
      {
        "name": "model-00002-of-00004.safetensors",
        "size": 4999802720,
        "mtime_ns": 1736746656058650226
      },
      {
        "name": "model-00003-of-00004.safetensors",
        "size": 4915916176,
        "mtime_ns": 1736746768408654808
      },
      {
        "name": "model-00004-of-00004.safetensors",
        "size": 1168138808,
        "mtime_ns": 1736746796088655937
      }
    ],
    "weight_content_hashed": false
  },
  "software": {
    "python": "3.10.21",
    "torch": "2.6.0",
    "transformers": "4.51.3",
    "tokenizers": "0.21.4"
  }
}
```

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.5314559999999995,
  "best_f1": {
    "threshold": -3.2716515254078793,
    "fpr": 0.922,
    "tpr": 0.98,
    "precision": 0.5152471083070452,
    "f1": 0.67539627842867,
    "tp": 490,
    "fp": 461,
    "tn": 39,
    "fn": 10
  },
  "tpr_at_fpr": {
    "1%": {
      "threshold": 37.201625468519524,
      "fpr": 0.002,
      "tpr": 0.002,
      "precision": 0.5,
      "f1": 0.00398406374501992,
      "tp": 1,
      "fp": 1,
      "tn": 499,
      "fn": 499,
      "target_fpr": 0.01
    },
    "5%": {
      "threshold": 2.2541740866685807,
      "fpr": 0.046,
      "tpr": 0.038,
      "precision": 0.4523809523809524,
      "f1": 0.07011070110701106,
      "tp": 19,
      "fp": 23,
      "tn": 477,
      "fn": 481,
      "target_fpr": 0.05
    },
    "10%": {
      "threshold": 1.6924558427507104,
      "fpr": 0.1,
      "tpr": 0.084,
      "precision": 0.45652173913043476,
      "f1": 0.14189189189189189,
      "tp": 42,
      "fp": 50,
      "tn": 450,
      "fn": 458,
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
      "clean": 2.0
    }
  },
  "rouge_l_dolly": {
    "mean": 0.21109795092047476,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta3_new1_qwen2_5_0_5b_dolly15k_test.jsonl",
    "reference_file": "/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl",
    "reference_source": "databricks/databricks-dolly-15k:response",
    "metric": "rougeL",
    "measure": "fmeasure",
    "use_stemmer": true,
    "aggregation": "unweighted mean of per-sample ROUGE-L F1"
  },
  "rouge_l_teacher_clean": {
    "mean": 0.26220712387693723,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta3_new1_qwen2_5_0_5b_dolly15k_test.jsonl",
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
        "mean": 0.5055007826165114,
        "median": 0.5,
        "min": 3.211705727028823e-303,
        "max": 1.0,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 16,
            "fraction": 0.032
          },
          "5%": {
            "alpha": 0.05,
            "count": 44,
            "fraction": 0.088
          },
          "10%": {
            "alpha": 0.1,
            "count": 71,
            "fraction": 0.142
          }
        }
      },
      "deduplicated": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.5167162971578534,
        "median": 0.5445336546656558,
        "min": 0.00020112215103030562,
        "max": 0.9986501019683699,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 2,
            "fraction": 0.004
          },
          "5%": {
            "alpha": 0.05,
            "count": 25,
            "fraction": 0.05
          },
          "10%": {
            "alpha": 0.1,
            "count": 41,
            "fraction": 0.082
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
    "kgw": "/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta3_new1_qwen2_5_0_5b_dolly15k_test.p_values.jsonl",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl"
  },
  "grouped_p_values": {
    "kgw": {
      "aggregation": "ordinary_median",
      "num_answers": 500,
      "total_answer_tokens": 70907,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 70,
          "total_answer_tokens": 70907,
          "discarded_tail_tokens": 907,
          "median_p_value": 0.6478317596858809,
          "median_log10_p_value": -0.18853776469536945,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 35,
          "total_answer_tokens": 70907,
          "discarded_tail_tokens": 907,
          "median_p_value": 0.6313737953880422,
          "median_log10_p_value": -0.19971344707880243,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 23,
          "total_answer_tokens": 70907,
          "discarded_tail_tokens": 1907,
          "median_p_value": 0.5508555692782966,
          "median_log10_p_value": -0.25896225539111434,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 7,
          "total_answer_tokens": 70907,
          "discarded_tail_tokens": 907,
          "median_p_value": 0.9798227856258324,
          "median_log10_p_value": -0.008852465311915528,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 3,
          "total_answer_tokens": 70907,
          "discarded_tail_tokens": 10907,
          "median_p_value": 0.9865614999705343,
          "median_log10_p_value": -0.005875836650683909,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 2,
          "total_answer_tokens": 70907,
          "discarded_tail_tokens": 10907,
          "median_p_value": 0.5003522510007945,
          "median_log10_p_value": -0.30072414205679476,
          "status": "ok"
        }
      }
    },
    "clean": {
      "aggregation": "ordinary_median",
      "num_answers": 500,
      "total_answer_tokens": 159765,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 159,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 765,
          "median_p_value": 0.8659288977499955,
          "median_log10_p_value": -0.06251776685396769,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 79,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 1765,
          "median_p_value": 0.971357711016285,
          "median_log10_p_value": -0.012620807875598238,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 53,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 765,
          "median_p_value": 0.9821335190767914,
          "median_log10_p_value": -0.007829466737979084,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 15,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 9765,
          "median_p_value": 0.9999999999999984,
          "median_log10_p_value": -6.750292265873014e-16,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 7,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 19765,
          "median_p_value": 1.0,
          "median_log10_p_value": 0.0,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 5,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 9765,
          "median_p_value": 1.0,
          "median_log10_p_value": 0.0,
          "status": "ok"
        }
      }
    }
  },
  "grouped_p_value_method": "teacher-tokenizer answer IDs concatenated without separators; exact disjoint blocks; first token of each block is context only; no repetition deduplication; incomplete tail discarded; ordinary median of block p-values (arithmetic mean of the two middle p-values for even group counts)",
  "per_group_p_value_files": {
    "kgw": "/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta3_new1_qwen2_5_0_5b_dolly15k_test.grouped_p_values.json",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.grouped_p_values.json"
  },
  "grouped_p_values_without_severe_repetition": {
    "kgw": {
      "aggregation": "ordinary_median",
      "num_answers": 485,
      "total_answer_tokens": 56846,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 56,
          "total_answer_tokens": 56846,
          "discarded_tail_tokens": 846,
          "median_p_value": 0.5627229887103784,
          "median_log10_p_value": -0.24970534241464606,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 28,
          "total_answer_tokens": 56846,
          "discarded_tail_tokens": 846,
          "median_p_value": 0.535634960500796,
          "median_log10_p_value": -0.27113108465279767,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 18,
          "total_answer_tokens": 56846,
          "discarded_tail_tokens": 2846,
          "median_p_value": 0.5145059419790791,
          "median_log10_p_value": -0.2886096052478569,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 5,
          "total_answer_tokens": 56846,
          "discarded_tail_tokens": 6846,
          "median_p_value": 0.6808308865958813,
          "median_log10_p_value": -0.16696075025912627,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 2,
          "total_answer_tokens": 56846,
          "discarded_tail_tokens": 16846,
          "median_p_value": 0.661378100059638,
          "median_log10_p_value": -0.17955018979836485,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 1,
          "total_answer_tokens": 56846,
          "discarded_tail_tokens": 26846,
          "median_p_value": 0.8410621077238487,
          "median_log10_p_value": -0.0751719328039635,
          "status": "ok"
        }
      },
      "filtering": {
        "repetition_threshold": 0.5,
        "comparison": ">",
        "scope": "answer-internal adjacent token pairs; prompt excluded",
        "num_answers_before": 500,
        "num_answers_retained": 485,
        "num_answers_removed": 15,
        "fraction_answers_removed": 0.03,
        "total_answer_tokens_before": 70907,
        "total_answer_tokens_retained": 56846,
        "total_answer_tokens_removed": 14061,
        "removed_answer_ids": [
          "dolly-08884",
          "dolly-01092",
          "dolly-02844",
          "dolly-03638",
          "dolly-13981",
          "dolly-10747",
          "dolly-04773",
          "dolly-07936",
          "dolly-09563",
          "dolly-02451",
          "dolly-06932",
          "dolly-08607",
          "dolly-00148",
          "dolly-05355",
          "dolly-06970"
        ]
      }
    },
    "clean": {
      "aggregation": "ordinary_median",
      "num_answers": 412,
      "total_answer_tokens": 45882,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 45,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 882,
          "median_p_value": 0.6360891449864364,
          "median_log10_p_value": -0.1964820156995508,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 22,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 1882,
          "median_p_value": 0.7960378878131416,
          "median_log10_p_value": -0.09906626131183685,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 15,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 882,
          "median_p_value": 0.7386263221105359,
          "median_log10_p_value": -0.13157521964243946,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 4,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 5882,
          "median_p_value": 0.947596846602552,
          "median_log10_p_value": -0.0233763931850151,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 2,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 5882,
          "median_p_value": 0.9783739864832501,
          "median_log10_p_value": -0.009495103065976066,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 1,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 15882,
          "median_p_value": 0.9995678964162934,
          "median_log10_p_value": -0.00018770075802065225,
          "status": "ok"
        }
      },
      "filtering": {
        "repetition_threshold": 0.5,
        "comparison": ">",
        "scope": "answer-internal adjacent token pairs; prompt excluded",
        "num_answers_before": 500,
        "num_answers_retained": 412,
        "num_answers_removed": 88,
        "fraction_answers_removed": 0.176,
        "total_answer_tokens_before": 159765,
        "total_answer_tokens_retained": 45882,
        "total_answer_tokens_removed": 113883,
        "removed_answer_ids": [
          "dolly-00135",
          "dolly-12241",
          "dolly-07923",
          "dolly-07103",
          "dolly-05608",
          "dolly-07788",
          "dolly-11310",
          "dolly-02097",
          "dolly-03614",
          "dolly-13505",
          "dolly-02580",
          "dolly-08884",
          "dolly-12659",
          "dolly-00420",
          "dolly-11014",
          "dolly-08008",
          "dolly-02186",
          "dolly-00275",
          "dolly-08512",
          "dolly-14060",
          "dolly-01461",
          "dolly-02223",
          "dolly-04949",
          "dolly-08689",
          "dolly-08574",
          "dolly-08406",
          "dolly-04141",
          "dolly-03209",
          "dolly-06227",
          "dolly-11078",
          "dolly-09778",
          "dolly-04856",
          "dolly-13779",
          "dolly-06595",
          "dolly-08936",
          "dolly-09344",
          "dolly-05605",
          "dolly-08340",
          "dolly-04589",
          "dolly-04686",
          "dolly-14700",
          "dolly-03696",
          "dolly-03914",
          "dolly-11987",
          "dolly-01939",
          "dolly-05628",
          "dolly-13339",
          "dolly-08911",
          "dolly-03239",
          "dolly-13445",
          "dolly-02139",
          "dolly-14265",
          "dolly-13610",
          "dolly-07427",
          "dolly-09563",
          "dolly-02451",
          "dolly-13544",
          "dolly-06824",
          "dolly-05312",
          "dolly-10992",
          "dolly-06932",
          "dolly-08607",
          "dolly-05388",
          "dolly-11386",
          "dolly-02069",
          "dolly-09439",
          "dolly-00148",
          "dolly-08211",
          "dolly-12186",
          "dolly-03319",
          "dolly-07407",
          "dolly-10389",
          "dolly-03916",
          "dolly-08222",
          "dolly-14947",
          "dolly-03624",
          "dolly-09330",
          "dolly-11182",
          "dolly-02059",
          "dolly-02916",
          "dolly-09816",
          "dolly-05355",
          "dolly-06970",
          "dolly-05634",
          "dolly-02500",
          "dolly-11314",
          "dolly-13235",
          "dolly-04223"
        ]
      }
    }
  },
  "grouped_p_value_without_severe_repetition_method": "exclude whole answers whose answer-internal adjacent-token-pair repetition ratio (1 - unique pairs / all pairs) is strictly greater than 0.5; prompts excluded from repetition assessment; filter each label independently; retain original answer order, then concatenate teacher-tokenizer answer IDs without separators; exact disjoint blocks, first token context only; no token-pair deduplication within retained blocks; incomplete tail discarded; ordinary median of block p-values (mean of the middle two for even counts)",
  "per_group_p_value_without_severe_repetition_files": {
    "kgw": "/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta3_new1_qwen2_5_0_5b_dolly15k_test.nonrepetitive_grouped_p_values.json",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.nonrepetitive_grouped_p_values.json"
  },
  "ppl": {
    "enabled": true,
    "schema": "saved-answer-reference-ppl-v1",
    "configuration": {
      "model_path": "/shared/public_models/Llama-3-8B",
      "device": "cuda",
      "dtype": "bfloat16",
      "generation_tokenizer": "/shared/public_models/Qwen2.5-0.5B",
      "max_length": null,
      "overflow": "error",
      "effective_max_length": 8192,
      "protocol": {
        "prompt": "source-generation-prompt; source chat template, not reference chat template",
        "boundary": "encode prompt and answer separately with add_special_tokens=False, then concatenate",
        "bos": "one reference BOS at start when defined; no extra EOS",
        "loss": "causal next-token NLL on all answer tokens, including the first; no prompt or padding loss",
        "aggregate": "exp(sum(answer NLL) / sum(scored answer tokens)); not mean per-answer PPL",
        "source_tokenizer_selection": "explicit override, otherwise row.model_path; fallback assumes the generation tokenizer matches that checkpoint",
        "legacy_prompt_limit": 2048,
        "weights_fingerprint": "weight filenames, sizes and mtime_ns; weight contents are not hashed"
      },
      "reference_assets": {
        "path": "/shared/public_models/Llama-3-8B",
        "assets": [
          {
            "name": "config.json",
            "size": 654,
            "sha256": "2430cee764b6530ff8673cf9ba8561e1d5a33152d503cd0de909ff5718261441"
          },
          {
            "name": "generation_config.json",
            "size": 126,
            "sha256": "55550e95c40c53fb0ee3f960d6d2b25a46405c8f790e5c4bb02caf3e98f2b5d0"
          },
          {
            "name": "model.safetensors.index.json",
            "size": 23950,
            "sha256": "146776fce3f6db1103aa6f249e65ee5544c5923ce6f971b092eee79aa6e5d37b"
          },
          {
            "name": "special_tokens_map.json",
            "size": 73,
            "sha256": "462d91939dbc37178aa5a3eae7068d1990ccc92e09f288cc71f42cdf139d69cc"
          },
          {
            "name": "tokenizer.json",
            "size": 9085698,
            "sha256": "e134af98b985517b4f068e3755ae90d4e9cd2d45d328325dc503f1c6b2d06cc7"
          },
          {
            "name": "tokenizer_config.json",
            "size": 50566,
            "sha256": "690727b4fed286383df1c7ca5e805124cb70c6eb4529f807c7b2e60ff741da7e"
          }
        ],
        "weight_stats": [
          {
            "name": "model-00001-of-00004.safetensors",
            "size": 4976698672,
            "mtime_ns": 1736746522477644778
          },
          {
            "name": "model-00002-of-00004.safetensors",
            "size": 4999802720,
            "mtime_ns": 1736746656058650226
          },
          {
            "name": "model-00003-of-00004.safetensors",
            "size": 4915916176,
            "mtime_ns": 1736746768408654808
          },
          {
            "name": "model-00004-of-00004.safetensors",
            "size": 1168138808,
            "mtime_ns": 1736746796088655937
          }
        ],
        "weight_content_hashed": false
      },
      "software": {
        "python": "3.10.21",
        "torch": "2.6.0",
        "transformers": "4.51.3",
        "tokenizers": "0.21.4"
      }
    },
    "files": {
      "kgw": {
        "samples": 500,
        "valid_samples": 500,
        "skipped_empty_answers": 0,
        "complete": true,
        "nonfinite_samples": 0,
        "status": "ok",
        "total_nll": 85280.21128384396,
        "scored_tokens": 69402,
        "mean_nll": 1.2287860765373326,
        "token_weighted_ppl": 3.417078945244024,
        "mean_answer_tokens": 138.804,
        "source_prompt_truncated_samples": 3,
        "reference_prompt_truncated_samples": 0,
        "generation_configurations": [
          {
            "configuration": {
              "temperature": 0.7,
              "top_p": 0.9,
              "max_new_tokens": 1536,
              "max_prompt_tokens": 2048,
              "kgw_enabled_during_generation": false
            },
            "samples": 500
          }
        ],
        "generation_seeds": {
          "recorded_samples": 500,
          "minimum": 42,
          "maximum": 541,
          "individual_values": "see per-sample immutable records"
        },
        "student_model_paths": [
          "/shared/wwx/EasyGAD/checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_new1_dipper2stage/gad/global_step_1813/actor/huggingface"
        ],
        "generation_tokenizer_paths": [
          "/shared/public_models/Qwen2.5-0.5B"
        ],
        "source_path": "/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta3_new1_qwen2_5_0_5b_dolly15k_test.jsonl",
        "source_sha256": "b1c02a02c9e074669d99cc9965618971b50b81e66d62c386002cdde73652f192",
        "per_sample_file": "/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta3_new1_qwen2_5_0_5b_dolly15k_test.ppl.444a5089035b343829bc.jsonl",
        "cache_reused": false
      },
      "clean": {
        "samples": 500,
        "valid_samples": 500,
        "skipped_empty_answers": 0,
        "complete": true,
        "nonfinite_samples": 0,
        "status": "ok",
        "total_nll": 67054.72902449768,
        "scored_tokens": 156267,
        "mean_nll": 0.42910357928735865,
        "token_weighted_ppl": 1.5358801115260794,
        "mean_answer_tokens": 312.534,
        "source_prompt_truncated_samples": 3,
        "reference_prompt_truncated_samples": 0,
        "generation_configurations": [
          {
            "configuration": {
              "kgw_enabled_during_generation": false,
              "max_new_tokens": 1536,
              "max_prompt_tokens": 2048,
              "temperature": 0.7,
              "top_p": 0.9
            },
            "samples": 500
          }
        ],
        "generation_seeds": {
          "recorded_samples": 500,
          "minimum": 42,
          "maximum": 541,
          "individual_values": "see per-sample immutable records"
        },
        "student_model_paths": [
          "/shared/public_models/Qwen2.5-0.5B"
        ],
        "generation_tokenizer_paths": [
          "/shared/public_models/Qwen2.5-0.5B"
        ],
        "source_path": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl",
        "source_sha256": "597b843d28d31c353c7bb9b94a3b6dccb564cb45ac2c5252f6a1592ccd768efe",
        "per_sample_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.ppl.877fc574f9ee35a5145f.jsonl",
        "cache_reused": true
      }
    }
  },
  "evaluated_at": "2026-10-19T17:16:58+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta3_new1_qwen2_5_0_5b_dolly15k_test.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-10-19T17:18:39+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.647688
- 实际检测配置：`{"gamma": 0.5, "hash_key": 15485863, "seeding": "simple_1 (hash_key * previous_token_id)", "delta_by_label": {"kgw": 3.0, "clean": 2.0}}`
- ROUGE-L（同批 500 条原始 Dolly 回答作参考）：0.198494（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 原始 Dolly 参考文件：`/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl`
- ROUGE-L（同批 500 条 14B clean 教师回答作参考）：0.309174（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 14B clean 教师参考文件：`/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_clean_test.parquet`
- Best F1：0.685011（z 阈值 -1.5460413650478515，TPR 0.946000，FPR 0.816000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.000000 | 0.000000 | 0.000000 | None |
  | 5% | 0.050000 | 0.114000 | 0.195876 | 2.225394561056747 |
  | 10% | 0.100000 | 0.228000 | 0.343373 | 1.6859773678906163 |

两种逐条文本 p-value 统计（单侧正态近似；不是 AUROC 的显著性检验）：

去重规则：相同的 `(previous_token_id, token_id)` 只计一次；不修改回答文本。

| 数据 | 检测方式 | 有效样本 | p 均值 | p 中位数 | p≤0.01 | p≤0.05 | p≤0.10 |
|---|---|---:|---:|---:|---:|---:|---:|
| kgw | 原始 | 500/500 | 0.365777 | 0.238373 | 53 (10.60%) | 119 (23.80%) | 156 (31.20%) |
| kgw | token 对去重 | 500/500 | 0.347472 | 0.270591 | 19 (3.80%) | 80 (16.00%) | 140 (28.00%) |
| clean | 原始 | 500/500 | 0.538121 | 0.57157 | 22 (4.40%) | 54 (10.80%) | 73 (14.60%) |
| clean | token 对去重 | 500/500 | 0.537418 | 0.555154 | 5 (1.00%) | 25 (5.00%) | 46 (9.20%) |

KGW 的小 p 占比是该理论阈值下的检出率，clean 的小 p 占比是实测误报率。p≤0.05 不保证实际 FPR=5%；去重可改善重复带来的失真，但不保证完全校准。空回答不做显著性检验，p=null，并排除在有效样本统计之外。

逐条 p-value：`/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.p_values.jsonl`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl`

固定 token 分组 p-value（普通中位数；p 越大表示原单侧检验证据越弱）：

按教师 tokenizer 编码回答并无分隔拼接，精确分组；每组首 token 仅作上下文，其余 token 用本项目原 KGW 绿表评分；不去重，尾部不足一组丢弃；各组 p 排序后取普通中位数（偶数组取中间两个 p 的算术平均）。

| 每组 token 数 | 计分 token 数 | KGW 组数 | KGW median p ↑ | clean 组数 | clean median p | KGW/clean 丢弃尾部 tokens |
|---:|---:|---:|---:|---:|---:|---:|
| 1000 | 999 | 124 | 0.0972842 | 159 | 0.865929 | 556/765 |
| 2000 | 1999 | 62 | 0.0210112 | 79 | 0.971358 | 556/1765 |
| 3000 | 2999 | 41 | 0.00451065 | 53 | 0.982134 | 1556/765 |
| 10000 | 9999 | 12 | 0.00010552 | 15 | 1 | 4556/9765 |
| 20000 | 19999 | 6 | 3.02847e-09 | 7 | 1 | 4556/19765 |
| 30000 | 29999 | 4 | 3.40648e-11 | 5 | 1 | 4556/9765 |

N/A 表示总 token 数不足一个完整组；组数为 1 或 2 时需结合逐组结果解释。极小 p 用科学计数法字符串保存，同时保留 log10(p)，避免浮点下溢为 0。

逐组 p-value 缓存：`/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.grouped_p_values.json`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.grouped_p_values.json`

剔除严重重复回答后的固定 token 分组 p-value（普通中位数）：

先独立筛选 KGW 和 clean：回答内部相邻 token 对重复比例严格大于 50% 时，剔除整条回答；prompt 不参与判断。保留回答按原顺序重新无分隔拼接，各组首 token 仅作上下文；组内不做 token 对去重，尾部不足一组丢弃。这是质量筛选补充指标，原始全样本统计另行保留。

| 数据 | 原回答数 | 剔除严重重复回答 | 保留回答数 | 原 tokens | 剔除 tokens | 保留 tokens |
|---|---:|---:|---:|---:|---:|---:|
| kgw | 500 | 11 (2.20%) | 489 | 124556 | 7546 | 117010 |
| clean | 500 | 88 (17.60%) | 412 | 159765 | 113883 | 45882 |

| 每组 token 数 | 计分 token 数 | KGW 组数 | KGW median p ↑ | clean 组数 | clean median p | KGW/clean 丢弃尾部 tokens |
|---:|---:|---:|---:|---:|---:|---:|
| 1000 | 999 | 117 | 0.0533105 | 45 | 0.636089 | 10/882 |
| 2000 | 1999 | 58 | 0.0258354 | 22 | 0.796038 | 1010/1882 |
| 3000 | 2999 | 39 | 0.00757776 | 15 | 0.738626 | 10/882 |
| 10000 | 9999 | 11 | 3.90689e-06 | 4 | 0.947597 | 7010/5882 |
| 20000 | 19999 | 5 | 2.09115e-11 | 2 | 0.978374 | 17010/5882 |
| 30000 | 29999 | 3 | 4.33976e-19 | 1 | 0.999568 | 27010/15882 |

N/A 表示筛选后不足一个完整组。各组 p 取普通中位数，偶数组取中间两个 p 的算术平均；组数较少时请结合逐组缓存解释。

剔除严重重复回答后的逐组 p-value 缓存：`/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.nonrepetitive_grouped_p_values.json`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.nonrepetitive_grouped_p_values.json`

### 固定参考模型 PPL（只评分已保存的回答）

| 文件组 | 总体 PPL ↓ | 有效样本/总样本 | 计分回答 tokens | 平均回答 tokens | 状态 | 缓存复用 |
|---|---:|---:|---:|---:|---|---|
| kgw | 3.545652 | 500/500 | 122479 | 244.96 | ok | False |
| clean | 1.535880 | 500/500 | 156267 | 312.53 | ok | True |

总体 PPL = exp(全部有效回答 NLL 总和 / 全部计分回答 token 数)，不是逐条 PPL 的算术平均。
原生成 tokenizer 恢复实际生成 prompt；参考 tokenizer 对 prompt/answer 分开编码后拼接；只计回答，包含首回答 token。Base 参考模型不再套用 chat template；只添加一次参考 BOS，不额外评分 EOS；输入 JSONL 不修改。

- kgw: `/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.jsonl`；SHA256 `618df1162dbd1bbf770b90baabfd23226ef52fd3028f5fdb6490919cca78b92e`；逐条明细 `/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.ppl.3d457111bb8e21e8feec.jsonl`；空回答 0；异常 loss 0；原生成截断 3；参考上下文截断 0。

  生成文本配置（种子逐条保存在明细中）：

```json
{
  "student_model_paths": [
    "/shared/wwx/EasyGAD/checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_new/gad/global_step_1813/actor/huggingface"
  ],
  "generation_tokenizer_paths": [
    "/shared/public_models/Qwen2.5-0.5B"
  ],
  "generation_configurations": [
    {
      "configuration": {
        "temperature": 0.7,
        "top_p": 0.9,
        "max_new_tokens": 1536,
        "max_prompt_tokens": 2048,
        "kgw_enabled_during_generation": false
      },
      "samples": 500
    }
  ],
  "generation_seeds": {
    "recorded_samples": 500,
    "minimum": 42,
    "maximum": 541,
    "individual_values": "see per-sample immutable records"
  }
}
```
- clean: `/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl`；SHA256 `597b843d28d31c353c7bb9b94a3b6dccb564cb45ac2c5252f6a1592ccd768efe`；逐条明细 `/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.ppl.877fc574f9ee35a5145f.jsonl`；空回答 0；异常 loss 0；原生成截断 3；参考上下文截断 0。

  生成文本配置（种子逐条保存在明细中）：

```json
{
  "student_model_paths": [
    "/shared/public_models/Qwen2.5-0.5B"
  ],
  "generation_tokenizer_paths": [
    "/shared/public_models/Qwen2.5-0.5B"
  ],
  "generation_configurations": [
    {
      "configuration": {
        "kgw_enabled_during_generation": false,
        "max_new_tokens": 1536,
        "max_prompt_tokens": 2048,
        "temperature": 0.7,
        "top_p": 0.9
      },
      "samples": 500
    }
  ],
  "generation_seeds": {
    "recorded_samples": 500,
    "minimum": 42,
    "maximum": 541,
    "individual_values": "see per-sample immutable records"
  }
}
```

完整评分配置（含模型/tokenizer 指纹、软件版本；权重使用 size/mtime 标识，不全量哈希）：

```json
{
  "model_path": "/shared/public_models/Llama-3-8B",
  "device": "cuda",
  "dtype": "bfloat16",
  "generation_tokenizer": "/shared/public_models/Qwen2.5-0.5B",
  "max_length": null,
  "overflow": "error",
  "effective_max_length": 8192,
  "protocol": {
    "prompt": "source-generation-prompt; source chat template, not reference chat template",
    "boundary": "encode prompt and answer separately with add_special_tokens=False, then concatenate",
    "bos": "one reference BOS at start when defined; no extra EOS",
    "loss": "causal next-token NLL on all answer tokens, including the first; no prompt or padding loss",
    "aggregate": "exp(sum(answer NLL) / sum(scored answer tokens)); not mean per-answer PPL",
    "source_tokenizer_selection": "explicit override, otherwise row.model_path; fallback assumes the generation tokenizer matches that checkpoint",
    "legacy_prompt_limit": 2048,
    "weights_fingerprint": "weight filenames, sizes and mtime_ns; weight contents are not hashed"
  },
  "reference_assets": {
    "path": "/shared/public_models/Llama-3-8B",
    "assets": [
      {
        "name": "config.json",
        "size": 654,
        "sha256": "2430cee764b6530ff8673cf9ba8561e1d5a33152d503cd0de909ff5718261441"
      },
      {
        "name": "generation_config.json",
        "size": 126,
        "sha256": "55550e95c40c53fb0ee3f960d6d2b25a46405c8f790e5c4bb02caf3e98f2b5d0"
      },
      {
        "name": "model.safetensors.index.json",
        "size": 23950,
        "sha256": "146776fce3f6db1103aa6f249e65ee5544c5923ce6f971b092eee79aa6e5d37b"
      },
      {
        "name": "special_tokens_map.json",
        "size": 73,
        "sha256": "462d91939dbc37178aa5a3eae7068d1990ccc92e09f288cc71f42cdf139d69cc"
      },
      {
        "name": "tokenizer.json",
        "size": 9085698,
        "sha256": "e134af98b985517b4f068e3755ae90d4e9cd2d45d328325dc503f1c6b2d06cc7"
      },
      {
        "name": "tokenizer_config.json",
        "size": 50566,
        "sha256": "690727b4fed286383df1c7ca5e805124cb70c6eb4529f807c7b2e60ff741da7e"
      }
    ],
    "weight_stats": [
      {
        "name": "model-00001-of-00004.safetensors",
        "size": 4976698672,
        "mtime_ns": 1736746522477644778
      },
      {
        "name": "model-00002-of-00004.safetensors",
        "size": 4999802720,
        "mtime_ns": 1736746656058650226
      },
      {
        "name": "model-00003-of-00004.safetensors",
        "size": 4915916176,
        "mtime_ns": 1736746768408654808
      },
      {
        "name": "model-00004-of-00004.safetensors",
        "size": 1168138808,
        "mtime_ns": 1736746796088655937
      }
    ],
    "weight_content_hashed": false
  },
  "software": {
    "python": "3.10.21",
    "torch": "2.6.0",
    "transformers": "4.51.3",
    "tokenizers": "0.21.4"
  }
}
```

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.6476880000000005,
  "best_f1": {
    "threshold": -1.5460413650478515,
    "fpr": 0.816,
    "tpr": 0.946,
    "precision": 0.5368898978433598,
    "f1": 0.6850108616944243,
    "tp": 473,
    "fp": 408,
    "tn": 92,
    "fn": 27
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
      "threshold": 2.225394561056747,
      "fpr": 0.05,
      "tpr": 0.114,
      "precision": 0.6951219512195121,
      "f1": 0.19587628865979384,
      "tp": 57,
      "fp": 25,
      "tn": 475,
      "fn": 443,
      "target_fpr": 0.05
    },
    "10%": {
      "threshold": 1.6859773678906163,
      "fpr": 0.1,
      "tpr": 0.228,
      "precision": 0.6951219512195121,
      "f1": 0.34337349397590367,
      "tp": 114,
      "fp": 50,
      "tn": 450,
      "fn": 386,
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
      "clean": 2.0
    }
  },
  "rouge_l_dolly": {
    "mean": 0.19849387557587408,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.jsonl",
    "reference_file": "/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl",
    "reference_source": "databricks/databricks-dolly-15k:response",
    "metric": "rougeL",
    "measure": "fmeasure",
    "use_stemmer": true,
    "aggregation": "unweighted mean of per-sample ROUGE-L F1"
  },
  "rouge_l_teacher_clean": {
    "mean": 0.3091744425525882,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.jsonl",
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
        "mean": 0.36577704616420137,
        "median": 0.2383728596628124,
        "min": 6.834897526731109e-14,
        "max": 0.9999999683624243,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 53,
            "fraction": 0.106
          },
          "5%": {
            "alpha": 0.05,
            "count": 119,
            "fraction": 0.238
          },
          "10%": {
            "alpha": 0.1,
            "count": 156,
            "fraction": 0.312
          }
        }
      },
      "deduplicated": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.3474721954408633,
        "median": 0.2705911687912894,
        "min": 9.802720950622567e-05,
        "max": 0.9947064313329715,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 19,
            "fraction": 0.038
          },
          "5%": {
            "alpha": 0.05,
            "count": 80,
            "fraction": 0.16
          },
          "10%": {
            "alpha": 0.1,
            "count": 140,
            "fraction": 0.28
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
    "kgw": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.p_values.jsonl",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl"
  },
  "grouped_p_values": {
    "kgw": {
      "aggregation": "ordinary_median",
      "num_answers": 500,
      "total_answer_tokens": 124556,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 124,
          "total_answer_tokens": 124556,
          "discarded_tail_tokens": 556,
          "median_p_value": 0.09728418407710798,
          "median_log10_p_value": -1.0119577591802715,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 62,
          "total_answer_tokens": 124556,
          "discarded_tail_tokens": 556,
          "median_p_value": 0.021011201066677636,
          "median_log10_p_value": -1.677549121238903,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 41,
          "total_answer_tokens": 124556,
          "discarded_tail_tokens": 1556,
          "median_p_value": 0.004510647390091074,
          "median_log10_p_value": -2.345761121588415,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 12,
          "total_answer_tokens": 124556,
          "discarded_tail_tokens": 4556,
          "median_p_value": 0.00010552043060425137,
          "median_log10_p_value": -3.976663445203648,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 6,
          "total_answer_tokens": 124556,
          "discarded_tail_tokens": 4556,
          "median_p_value": 3.0284724385078573e-09,
          "median_log10_p_value": -8.518776374405638,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 4,
          "total_answer_tokens": 124556,
          "discarded_tail_tokens": 4556,
          "median_p_value": 3.406482841307593e-11,
          "median_log10_p_value": -10.467693794290765,
          "status": "ok"
        }
      }
    },
    "clean": {
      "aggregation": "ordinary_median",
      "num_answers": 500,
      "total_answer_tokens": 159765,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 159,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 765,
          "median_p_value": 0.8659288977499955,
          "median_log10_p_value": -0.06251776685396769,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 79,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 1765,
          "median_p_value": 0.971357711016285,
          "median_log10_p_value": -0.012620807875598238,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 53,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 765,
          "median_p_value": 0.9821335190767914,
          "median_log10_p_value": -0.007829466737979084,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 15,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 9765,
          "median_p_value": 0.9999999999999984,
          "median_log10_p_value": -6.750292265873014e-16,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 7,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 19765,
          "median_p_value": 1.0,
          "median_log10_p_value": 0.0,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 5,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 9765,
          "median_p_value": 1.0,
          "median_log10_p_value": 0.0,
          "status": "ok"
        }
      }
    }
  },
  "grouped_p_value_method": "teacher-tokenizer answer IDs concatenated without separators; exact disjoint blocks; first token of each block is context only; no repetition deduplication; incomplete tail discarded; ordinary median of block p-values (arithmetic mean of the two middle p-values for even group counts)",
  "per_group_p_value_files": {
    "kgw": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.grouped_p_values.json",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.grouped_p_values.json"
  },
  "grouped_p_values_without_severe_repetition": {
    "kgw": {
      "aggregation": "ordinary_median",
      "num_answers": 489,
      "total_answer_tokens": 117010,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 117,
          "total_answer_tokens": 117010,
          "discarded_tail_tokens": 10,
          "median_p_value": 0.05331051692833846,
          "median_log10_p_value": -1.2731871062944602,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 58,
          "total_answer_tokens": 117010,
          "discarded_tail_tokens": 1010,
          "median_p_value": 0.025835438978909653,
          "median_log10_p_value": -1.587784154807367,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 39,
          "total_answer_tokens": 117010,
          "discarded_tail_tokens": 10,
          "median_p_value": 0.007577755382079972,
          "median_log10_p_value": -2.12045941831776,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 11,
          "total_answer_tokens": 117010,
          "discarded_tail_tokens": 7010,
          "median_p_value": 3.906894729933383e-06,
          "median_log10_p_value": -5.408168290547667,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 5,
          "total_answer_tokens": 117010,
          "discarded_tail_tokens": 17010,
          "median_p_value": 2.0911493971713533e-11,
          "median_log10_p_value": -10.679614938942542,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 3,
          "total_answer_tokens": 117010,
          "discarded_tail_tokens": 27010,
          "median_p_value": 4.339760379368728e-19,
          "median_log10_p_value": -18.36253424947156,
          "status": "ok"
        }
      },
      "filtering": {
        "repetition_threshold": 0.5,
        "comparison": ">",
        "scope": "answer-internal adjacent token pairs; prompt excluded",
        "num_answers_before": 500,
        "num_answers_retained": 489,
        "num_answers_removed": 11,
        "fraction_answers_removed": 0.022,
        "total_answer_tokens_before": 124556,
        "total_answer_tokens_retained": 117010,
        "total_answer_tokens_removed": 7546,
        "removed_answer_ids": [
          "dolly-00423",
          "dolly-07103",
          "dolly-02678",
          "dolly-00143",
          "dolly-04773",
          "dolly-11030",
          "dolly-13445",
          "dolly-06932",
          "dolly-08607",
          "dolly-12001",
          "dolly-01356"
        ]
      }
    },
    "clean": {
      "aggregation": "ordinary_median",
      "num_answers": 412,
      "total_answer_tokens": 45882,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 45,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 882,
          "median_p_value": 0.6360891449864364,
          "median_log10_p_value": -0.1964820156995508,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 22,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 1882,
          "median_p_value": 0.7960378878131416,
          "median_log10_p_value": -0.09906626131183685,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 15,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 882,
          "median_p_value": 0.7386263221105359,
          "median_log10_p_value": -0.13157521964243946,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 4,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 5882,
          "median_p_value": 0.947596846602552,
          "median_log10_p_value": -0.0233763931850151,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 2,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 5882,
          "median_p_value": 0.9783739864832501,
          "median_log10_p_value": -0.009495103065976066,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 1,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 15882,
          "median_p_value": 0.9995678964162934,
          "median_log10_p_value": -0.00018770075802065225,
          "status": "ok"
        }
      },
      "filtering": {
        "repetition_threshold": 0.5,
        "comparison": ">",
        "scope": "answer-internal adjacent token pairs; prompt excluded",
        "num_answers_before": 500,
        "num_answers_retained": 412,
        "num_answers_removed": 88,
        "fraction_answers_removed": 0.176,
        "total_answer_tokens_before": 159765,
        "total_answer_tokens_retained": 45882,
        "total_answer_tokens_removed": 113883,
        "removed_answer_ids": [
          "dolly-00135",
          "dolly-12241",
          "dolly-07923",
          "dolly-07103",
          "dolly-05608",
          "dolly-07788",
          "dolly-11310",
          "dolly-02097",
          "dolly-03614",
          "dolly-13505",
          "dolly-02580",
          "dolly-08884",
          "dolly-12659",
          "dolly-00420",
          "dolly-11014",
          "dolly-08008",
          "dolly-02186",
          "dolly-00275",
          "dolly-08512",
          "dolly-14060",
          "dolly-01461",
          "dolly-02223",
          "dolly-04949",
          "dolly-08689",
          "dolly-08574",
          "dolly-08406",
          "dolly-04141",
          "dolly-03209",
          "dolly-06227",
          "dolly-11078",
          "dolly-09778",
          "dolly-04856",
          "dolly-13779",
          "dolly-06595",
          "dolly-08936",
          "dolly-09344",
          "dolly-05605",
          "dolly-08340",
          "dolly-04589",
          "dolly-04686",
          "dolly-14700",
          "dolly-03696",
          "dolly-03914",
          "dolly-11987",
          "dolly-01939",
          "dolly-05628",
          "dolly-13339",
          "dolly-08911",
          "dolly-03239",
          "dolly-13445",
          "dolly-02139",
          "dolly-14265",
          "dolly-13610",
          "dolly-07427",
          "dolly-09563",
          "dolly-02451",
          "dolly-13544",
          "dolly-06824",
          "dolly-05312",
          "dolly-10992",
          "dolly-06932",
          "dolly-08607",
          "dolly-05388",
          "dolly-11386",
          "dolly-02069",
          "dolly-09439",
          "dolly-00148",
          "dolly-08211",
          "dolly-12186",
          "dolly-03319",
          "dolly-07407",
          "dolly-10389",
          "dolly-03916",
          "dolly-08222",
          "dolly-14947",
          "dolly-03624",
          "dolly-09330",
          "dolly-11182",
          "dolly-02059",
          "dolly-02916",
          "dolly-09816",
          "dolly-05355",
          "dolly-06970",
          "dolly-05634",
          "dolly-02500",
          "dolly-11314",
          "dolly-13235",
          "dolly-04223"
        ]
      }
    }
  },
  "grouped_p_value_without_severe_repetition_method": "exclude whole answers whose answer-internal adjacent-token-pair repetition ratio (1 - unique pairs / all pairs) is strictly greater than 0.5; prompts excluded from repetition assessment; filter each label independently; retain original answer order, then concatenate teacher-tokenizer answer IDs without separators; exact disjoint blocks, first token context only; no token-pair deduplication within retained blocks; incomplete tail discarded; ordinary median of block p-values (mean of the middle two for even counts)",
  "per_group_p_value_without_severe_repetition_files": {
    "kgw": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.nonrepetitive_grouped_p_values.json",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.nonrepetitive_grouped_p_values.json"
  },
  "ppl": {
    "enabled": true,
    "schema": "saved-answer-reference-ppl-v1",
    "configuration": {
      "model_path": "/shared/public_models/Llama-3-8B",
      "device": "cuda",
      "dtype": "bfloat16",
      "generation_tokenizer": "/shared/public_models/Qwen2.5-0.5B",
      "max_length": null,
      "overflow": "error",
      "effective_max_length": 8192,
      "protocol": {
        "prompt": "source-generation-prompt; source chat template, not reference chat template",
        "boundary": "encode prompt and answer separately with add_special_tokens=False, then concatenate",
        "bos": "one reference BOS at start when defined; no extra EOS",
        "loss": "causal next-token NLL on all answer tokens, including the first; no prompt or padding loss",
        "aggregate": "exp(sum(answer NLL) / sum(scored answer tokens)); not mean per-answer PPL",
        "source_tokenizer_selection": "explicit override, otherwise row.model_path; fallback assumes the generation tokenizer matches that checkpoint",
        "legacy_prompt_limit": 2048,
        "weights_fingerprint": "weight filenames, sizes and mtime_ns; weight contents are not hashed"
      },
      "reference_assets": {
        "path": "/shared/public_models/Llama-3-8B",
        "assets": [
          {
            "name": "config.json",
            "size": 654,
            "sha256": "2430cee764b6530ff8673cf9ba8561e1d5a33152d503cd0de909ff5718261441"
          },
          {
            "name": "generation_config.json",
            "size": 126,
            "sha256": "55550e95c40c53fb0ee3f960d6d2b25a46405c8f790e5c4bb02caf3e98f2b5d0"
          },
          {
            "name": "model.safetensors.index.json",
            "size": 23950,
            "sha256": "146776fce3f6db1103aa6f249e65ee5544c5923ce6f971b092eee79aa6e5d37b"
          },
          {
            "name": "special_tokens_map.json",
            "size": 73,
            "sha256": "462d91939dbc37178aa5a3eae7068d1990ccc92e09f288cc71f42cdf139d69cc"
          },
          {
            "name": "tokenizer.json",
            "size": 9085698,
            "sha256": "e134af98b985517b4f068e3755ae90d4e9cd2d45d328325dc503f1c6b2d06cc7"
          },
          {
            "name": "tokenizer_config.json",
            "size": 50566,
            "sha256": "690727b4fed286383df1c7ca5e805124cb70c6eb4529f807c7b2e60ff741da7e"
          }
        ],
        "weight_stats": [
          {
            "name": "model-00001-of-00004.safetensors",
            "size": 4976698672,
            "mtime_ns": 1736746522477644778
          },
          {
            "name": "model-00002-of-00004.safetensors",
            "size": 4999802720,
            "mtime_ns": 1736746656058650226
          },
          {
            "name": "model-00003-of-00004.safetensors",
            "size": 4915916176,
            "mtime_ns": 1736746768408654808
          },
          {
            "name": "model-00004-of-00004.safetensors",
            "size": 1168138808,
            "mtime_ns": 1736746796088655937
          }
        ],
        "weight_content_hashed": false
      },
      "software": {
        "python": "3.10.21",
        "torch": "2.6.0",
        "transformers": "4.51.3",
        "tokenizers": "0.21.4"
      }
    },
    "files": {
      "kgw": {
        "samples": 500,
        "valid_samples": 500,
        "skipped_empty_answers": 0,
        "complete": true,
        "nonfinite_samples": 0,
        "status": "ok",
        "total_nll": 155024.37507087755,
        "scored_tokens": 122479,
        "mean_nll": 1.2657220835480167,
        "token_weighted_ppl": 3.5456520689977062,
        "mean_answer_tokens": 244.958,
        "source_prompt_truncated_samples": 3,
        "reference_prompt_truncated_samples": 0,
        "generation_configurations": [
          {
            "configuration": {
              "temperature": 0.7,
              "top_p": 0.9,
              "max_new_tokens": 1536,
              "max_prompt_tokens": 2048,
              "kgw_enabled_during_generation": false
            },
            "samples": 500
          }
        ],
        "generation_seeds": {
          "recorded_samples": 500,
          "minimum": 42,
          "maximum": 541,
          "individual_values": "see per-sample immutable records"
        },
        "student_model_paths": [
          "/shared/wwx/EasyGAD/checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_new/gad/global_step_1813/actor/huggingface"
        ],
        "generation_tokenizer_paths": [
          "/shared/public_models/Qwen2.5-0.5B"
        ],
        "source_path": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.jsonl",
        "source_sha256": "618df1162dbd1bbf770b90baabfd23226ef52fd3028f5fdb6490919cca78b92e",
        "per_sample_file": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.ppl.3d457111bb8e21e8feec.jsonl",
        "cache_reused": false
      },
      "clean": {
        "samples": 500,
        "valid_samples": 500,
        "skipped_empty_answers": 0,
        "complete": true,
        "nonfinite_samples": 0,
        "status": "ok",
        "total_nll": 67054.72902449768,
        "scored_tokens": 156267,
        "mean_nll": 0.42910357928735865,
        "token_weighted_ppl": 1.5358801115260794,
        "mean_answer_tokens": 312.534,
        "source_prompt_truncated_samples": 3,
        "reference_prompt_truncated_samples": 0,
        "generation_configurations": [
          {
            "configuration": {
              "kgw_enabled_during_generation": false,
              "max_new_tokens": 1536,
              "max_prompt_tokens": 2048,
              "temperature": 0.7,
              "top_p": 0.9
            },
            "samples": 500
          }
        ],
        "generation_seeds": {
          "recorded_samples": 500,
          "minimum": 42,
          "maximum": 541,
          "individual_values": "see per-sample immutable records"
        },
        "student_model_paths": [
          "/shared/public_models/Qwen2.5-0.5B"
        ],
        "generation_tokenizer_paths": [
          "/shared/public_models/Qwen2.5-0.5B"
        ],
        "source_path": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl",
        "source_sha256": "597b843d28d31c353c7bb9b94a3b6dccb564cb45ac2c5252f6a1592ccd768efe",
        "per_sample_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.ppl.877fc574f9ee35a5145f.jsonl",
        "cache_reused": true
      }
    }
  },
  "evaluated_at": "2026-10-19T17:18:39+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-10-19T17:20:18+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.433434
- 实际检测配置：`{"gamma": 0.5, "hash_key": 15485863, "seeding": "simple_1 (hash_key * previous_token_id)", "delta_by_label": {"kgw": 3.0, "clean": 2.0}}`
- ROUGE-L（同批 500 条原始 Dolly 回答作参考）：0.185418（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 原始 Dolly 参考文件：`/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl`
- ROUGE-L（同批 500 条 14B clean 教师回答作参考）：0.286763（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 14B clean 教师参考文件：`/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_clean_test.parquet`
- Best F1：0.672087（z 阈值 -7.654655446197432，TPR 0.992000，FPR 0.960000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.002000 | 0.002000 | 0.003984 | 36.23203577866784 |
  | 5% | 0.046000 | 0.026000 | 0.048507 | 2.2519414081056586 |
  | 10% | 0.100000 | 0.050000 | 0.086957 | 1.7075311565539322 |

两种逐条文本 p-value 统计（单侧正态近似；不是 AUROC 的显著性检验）：

去重规则：相同的 `(previous_token_id, token_id)` 只计一次；不修改回答文本。

| 数据 | 检测方式 | 有效样本 | p 均值 | p 中位数 | p≤0.01 | p≤0.05 | p≤0.10 |
|---|---|---:|---:|---:|---:|---:|---:|
| kgw | 原始 | 500/500 | 0.619542 | 0.685885 | 11 (2.20%) | 27 (5.40%) | 44 (8.80%) |
| kgw | token 对去重 | 500/500 | 0.618146 | 0.665092 | 3 (0.60%) | 11 (2.20%) | 22 (4.40%) |
| clean | 原始 | 500/500 | 0.538121 | 0.57157 | 22 (4.40%) | 54 (10.80%) | 73 (14.60%) |
| clean | token 对去重 | 500/500 | 0.537418 | 0.555154 | 5 (1.00%) | 25 (5.00%) | 46 (9.20%) |

KGW 的小 p 占比是该理论阈值下的检出率，clean 的小 p 占比是实测误报率。p≤0.05 不保证实际 FPR=5%；去重可改善重复带来的失真，但不保证完全校准。空回答不做显著性检验，p=null，并排除在有效样本统计之外。

逐条 p-value：`/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new.p_values.jsonl`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl`

固定 token 分组 p-value（普通中位数；p 越大表示原单侧检验证据越弱）：

按教师 tokenizer 编码回答并无分隔拼接，精确分组；每组首 token 仅作上下文，其余 token 用本项目原 KGW 绿表评分；不去重，尾部不足一组丢弃；各组 p 排序后取普通中位数（偶数组取中间两个 p 的算术平均）。

| 每组 token 数 | 计分 token 数 | KGW 组数 | KGW median p ↑ | clean 组数 | clean median p | KGW/clean 丢弃尾部 tokens |
|---:|---:|---:|---:|---:|---:|---:|
| 1000 | 999 | 141 | 0.922739 | 159 | 0.865929 | 647/765 |
| 2000 | 1999 | 70 | 0.979091 | 79 | 0.971358 | 1647/1765 |
| 3000 | 2999 | 47 | 0.996744 | 53 | 0.982134 | 647/765 |
| 10000 | 9999 | 14 | 0.999998 | 15 | 1 | 1647/9765 |
| 20000 | 19999 | 7 | 1 | 7 | 1 | 1647/19765 |
| 30000 | 29999 | 4 | 1 | 5 | 1 | 21647/9765 |

N/A 表示总 token 数不足一个完整组；组数为 1 或 2 时需结合逐组结果解释。极小 p 用科学计数法字符串保存，同时保留 log10(p)，避免浮点下溢为 0。

逐组 p-value 缓存：`/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new.grouped_p_values.json`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.grouped_p_values.json`

剔除严重重复回答后的固定 token 分组 p-value（普通中位数）：

先独立筛选 KGW 和 clean：回答内部相邻 token 对重复比例严格大于 50% 时，剔除整条回答；prompt 不参与判断。保留回答按原顺序重新无分隔拼接，各组首 token 仅作上下文；组内不做 token 对去重，尾部不足一组丢弃。这是质量筛选补充指标，原始全样本统计另行保留。

| 数据 | 原回答数 | 剔除严重重复回答 | 保留回答数 | 原 tokens | 剔除 tokens | 保留 tokens |
|---|---:|---:|---:|---:|---:|---:|
| kgw | 500 | 21 (4.20%) | 479 | 141647 | 22772 | 118875 |
| clean | 500 | 88 (17.60%) | 412 | 159765 | 113883 | 45882 |

| 每组 token 数 | 计分 token 数 | KGW 组数 | KGW median p ↑ | clean 组数 | clean median p | KGW/clean 丢弃尾部 tokens |
|---:|---:|---:|---:|---:|---:|---:|
| 1000 | 999 | 118 | 0.879126 | 45 | 0.636089 | 875/882 |
| 2000 | 1999 | 59 | 0.957484 | 22 | 0.796038 | 875/1882 |
| 3000 | 2999 | 39 | 0.974642 | 15 | 0.738626 | 1875/882 |
| 10000 | 9999 | 11 | 0.999847 | 4 | 0.947597 | 8875/5882 |
| 20000 | 19999 | 5 | 1 | 2 | 0.978374 | 18875/5882 |
| 30000 | 29999 | 3 | 1 | 1 | 0.999568 | 28875/15882 |

N/A 表示筛选后不足一个完整组。各组 p 取普通中位数，偶数组取中间两个 p 的算术平均；组数较少时请结合逐组缓存解释。

剔除严重重复回答后的逐组 p-value 缓存：`/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new.nonrepetitive_grouped_p_values.json`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.nonrepetitive_grouped_p_values.json`

### 固定参考模型 PPL（只评分已保存的回答）

| 文件组 | 总体 PPL ↓ | 有效样本/总样本 | 计分回答 tokens | 平均回答 tokens | 状态 | 缓存复用 |
|---|---:|---:|---:|---:|---|---|
| kgw | 3.305133 | 500/500 | 138174 | 276.35 | ok | False |
| clean | 1.535880 | 500/500 | 156267 | 312.53 | ok | True |

总体 PPL = exp(全部有效回答 NLL 总和 / 全部计分回答 token 数)，不是逐条 PPL 的算术平均。
原生成 tokenizer 恢复实际生成 prompt；参考 tokenizer 对 prompt/answer 分开编码后拼接；只计回答，包含首回答 token。Base 参考模型不再套用 chat template；只添加一次参考 BOS，不额外评分 EOS；输入 JSONL 不修改。

- kgw: `/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new.jsonl`；SHA256 `a6cb5b53fe168f08def87ed1c4ebb6a5e038e93fe2ba6ba94044adbb8ff9d034`；逐条明细 `/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new.ppl.2f44d6804314edd20e4f.jsonl`；空回答 0；异常 loss 0；原生成截断 0；参考上下文截断 0。

  生成文本配置（种子逐条保存在明细中）：

```json
{
  "student_model_paths": [
    "/shared/wwx/EasyGAD/checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_new/gad/global_step_1813/actor/huggingface"
  ],
  "generation_tokenizer_paths": [
    "/shared/public_models/Qwen2.5-0.5B"
  ],
  "generation_configurations": [
    {
      "configuration": {
        "temperature": 0.7,
        "top_p": 0.9,
        "max_new_tokens": 1536,
        "max_prompt_tokens": 6144,
        "prompt_truncated": false,
        "kgw_enabled_during_generation": false,
        "wn_enabled_during_generation": true
      },
      "samples": 500
    }
  ],
  "generation_seeds": {
    "recorded_samples": 500,
    "minimum": 42,
    "maximum": 541,
    "individual_values": "see per-sample immutable records"
  }
}
```
- clean: `/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl`；SHA256 `597b843d28d31c353c7bb9b94a3b6dccb564cb45ac2c5252f6a1592ccd768efe`；逐条明细 `/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.ppl.877fc574f9ee35a5145f.jsonl`；空回答 0；异常 loss 0；原生成截断 3；参考上下文截断 0。

  生成文本配置（种子逐条保存在明细中）：

```json
{
  "student_model_paths": [
    "/shared/public_models/Qwen2.5-0.5B"
  ],
  "generation_tokenizer_paths": [
    "/shared/public_models/Qwen2.5-0.5B"
  ],
  "generation_configurations": [
    {
      "configuration": {
        "kgw_enabled_during_generation": false,
        "max_new_tokens": 1536,
        "max_prompt_tokens": 2048,
        "temperature": 0.7,
        "top_p": 0.9
      },
      "samples": 500
    }
  ],
  "generation_seeds": {
    "recorded_samples": 500,
    "minimum": 42,
    "maximum": 541,
    "individual_values": "see per-sample immutable records"
  }
}
```

完整评分配置（含模型/tokenizer 指纹、软件版本；权重使用 size/mtime 标识，不全量哈希）：

```json
{
  "model_path": "/shared/public_models/Llama-3-8B",
  "device": "cuda",
  "dtype": "bfloat16",
  "generation_tokenizer": "/shared/public_models/Qwen2.5-0.5B",
  "max_length": null,
  "overflow": "error",
  "effective_max_length": 8192,
  "protocol": {
    "prompt": "source-generation-prompt; source chat template, not reference chat template",
    "boundary": "encode prompt and answer separately with add_special_tokens=False, then concatenate",
    "bos": "one reference BOS at start when defined; no extra EOS",
    "loss": "causal next-token NLL on all answer tokens, including the first; no prompt or padding loss",
    "aggregate": "exp(sum(answer NLL) / sum(scored answer tokens)); not mean per-answer PPL",
    "source_tokenizer_selection": "explicit override, otherwise row.model_path; fallback assumes the generation tokenizer matches that checkpoint",
    "legacy_prompt_limit": 2048,
    "weights_fingerprint": "weight filenames, sizes and mtime_ns; weight contents are not hashed"
  },
  "reference_assets": {
    "path": "/shared/public_models/Llama-3-8B",
    "assets": [
      {
        "name": "config.json",
        "size": 654,
        "sha256": "2430cee764b6530ff8673cf9ba8561e1d5a33152d503cd0de909ff5718261441"
      },
      {
        "name": "generation_config.json",
        "size": 126,
        "sha256": "55550e95c40c53fb0ee3f960d6d2b25a46405c8f790e5c4bb02caf3e98f2b5d0"
      },
      {
        "name": "model.safetensors.index.json",
        "size": 23950,
        "sha256": "146776fce3f6db1103aa6f249e65ee5544c5923ce6f971b092eee79aa6e5d37b"
      },
      {
        "name": "special_tokens_map.json",
        "size": 73,
        "sha256": "462d91939dbc37178aa5a3eae7068d1990ccc92e09f288cc71f42cdf139d69cc"
      },
      {
        "name": "tokenizer.json",
        "size": 9085698,
        "sha256": "e134af98b985517b4f068e3755ae90d4e9cd2d45d328325dc503f1c6b2d06cc7"
      },
      {
        "name": "tokenizer_config.json",
        "size": 50566,
        "sha256": "690727b4fed286383df1c7ca5e805124cb70c6eb4529f807c7b2e60ff741da7e"
      }
    ],
    "weight_stats": [
      {
        "name": "model-00001-of-00004.safetensors",
        "size": 4976698672,
        "mtime_ns": 1736746522477644778
      },
      {
        "name": "model-00002-of-00004.safetensors",
        "size": 4999802720,
        "mtime_ns": 1736746656058650226
      },
      {
        "name": "model-00003-of-00004.safetensors",
        "size": 4915916176,
        "mtime_ns": 1736746768408654808
      },
      {
        "name": "model-00004-of-00004.safetensors",
        "size": 1168138808,
        "mtime_ns": 1736746796088655937
      }
    ],
    "weight_content_hashed": false
  },
  "software": {
    "python": "3.10.21",
    "torch": "2.6.0",
    "transformers": "4.51.3",
    "tokenizers": "0.21.4"
  }
}
```

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.4334339999999997,
  "best_f1": {
    "threshold": -7.654655446197432,
    "fpr": 0.96,
    "tpr": 0.992,
    "precision": 0.5081967213114754,
    "f1": 0.6720867208672088,
    "tp": 496,
    "fp": 480,
    "tn": 20,
    "fn": 4
  },
  "tpr_at_fpr": {
    "1%": {
      "threshold": 36.23203577866784,
      "fpr": 0.002,
      "tpr": 0.002,
      "precision": 0.5,
      "f1": 0.00398406374501992,
      "tp": 1,
      "fp": 1,
      "tn": 499,
      "fn": 499,
      "target_fpr": 0.01
    },
    "5%": {
      "threshold": 2.2519414081056586,
      "fpr": 0.046,
      "tpr": 0.026,
      "precision": 0.3611111111111111,
      "f1": 0.04850746268656716,
      "tp": 13,
      "fp": 23,
      "tn": 477,
      "fn": 487,
      "target_fpr": 0.05
    },
    "10%": {
      "threshold": 1.7075311565539322,
      "fpr": 0.1,
      "tpr": 0.05,
      "precision": 0.3333333333333333,
      "f1": 0.08695652173913045,
      "tp": 25,
      "fp": 50,
      "tn": 450,
      "fn": 475,
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
      "clean": 2.0
    }
  },
  "rouge_l_dolly": {
    "mean": 0.185418046008631,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new.jsonl",
    "reference_file": "/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl",
    "reference_source": "databricks/databricks-dolly-15k:response",
    "metric": "rougeL",
    "measure": "fmeasure",
    "use_stemmer": true,
    "aggregation": "unweighted mean of per-sample ROUGE-L F1"
  },
  "rouge_l_teacher_clean": {
    "mean": 0.2867632931442953,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new.jsonl",
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
        "mean": 0.6195424620785832,
        "median": 0.6858849758356487,
        "min": 9.53201291013277e-288,
        "max": 1.0,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 11,
            "fraction": 0.022
          },
          "5%": {
            "alpha": 0.05,
            "count": 27,
            "fraction": 0.054
          },
          "10%": {
            "alpha": 0.1,
            "count": 44,
            "fraction": 0.088
          }
        }
      },
      "deduplicated": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.618146070028407,
        "median": 0.6650923212002917,
        "min": 0.004024651677903384,
        "max": 0.9998630818329007,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 3,
            "fraction": 0.006
          },
          "5%": {
            "alpha": 0.05,
            "count": 11,
            "fraction": 0.022
          },
          "10%": {
            "alpha": 0.1,
            "count": 22,
            "fraction": 0.044
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
    "kgw": "/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new.p_values.jsonl",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl"
  },
  "grouped_p_values": {
    "kgw": {
      "aggregation": "ordinary_median",
      "num_answers": 500,
      "total_answer_tokens": 141647,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 141,
          "total_answer_tokens": 141647,
          "discarded_tail_tokens": 647,
          "median_p_value": 0.9227386896857669,
          "median_log10_p_value": -0.03492126939122037,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 70,
          "total_answer_tokens": 141647,
          "discarded_tail_tokens": 1647,
          "median_p_value": 0.9790911982428734,
          "median_log10_p_value": -0.009176853601383308,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 47,
          "total_answer_tokens": 141647,
          "discarded_tail_tokens": 647,
          "median_p_value": 0.996743879934514,
          "median_log10_p_value": -0.001416422250799275,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 14,
          "total_answer_tokens": 141647,
          "discarded_tail_tokens": 1647,
          "median_p_value": 0.9999978203853606,
          "median_log10_p_value": -9.465956421558859e-07,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 7,
          "total_answer_tokens": 141647,
          "discarded_tail_tokens": 1647,
          "median_p_value": 0.9999999919740807,
          "median_log10_p_value": -3.4856124619019655e-09,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 4,
          "total_answer_tokens": 141647,
          "discarded_tail_tokens": 21647,
          "median_p_value": 1.0,
          "median_log10_p_value": 0.0,
          "status": "ok"
        }
      }
    },
    "clean": {
      "aggregation": "ordinary_median",
      "num_answers": 500,
      "total_answer_tokens": 159765,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 159,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 765,
          "median_p_value": 0.8659288977499955,
          "median_log10_p_value": -0.06251776685396769,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 79,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 1765,
          "median_p_value": 0.971357711016285,
          "median_log10_p_value": -0.012620807875598238,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 53,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 765,
          "median_p_value": 0.9821335190767914,
          "median_log10_p_value": -0.007829466737979084,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 15,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 9765,
          "median_p_value": 0.9999999999999984,
          "median_log10_p_value": -6.750292265873014e-16,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 7,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 19765,
          "median_p_value": 1.0,
          "median_log10_p_value": 0.0,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 5,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 9765,
          "median_p_value": 1.0,
          "median_log10_p_value": 0.0,
          "status": "ok"
        }
      }
    }
  },
  "grouped_p_value_method": "teacher-tokenizer answer IDs concatenated without separators; exact disjoint blocks; first token of each block is context only; no repetition deduplication; incomplete tail discarded; ordinary median of block p-values (arithmetic mean of the two middle p-values for even group counts)",
  "per_group_p_value_files": {
    "kgw": "/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new.grouped_p_values.json",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.grouped_p_values.json"
  },
  "grouped_p_values_without_severe_repetition": {
    "kgw": {
      "aggregation": "ordinary_median",
      "num_answers": 479,
      "total_answer_tokens": 118875,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 118,
          "total_answer_tokens": 118875,
          "discarded_tail_tokens": 875,
          "median_p_value": 0.8791258704238145,
          "median_log10_p_value": -0.0559489395827206,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 59,
          "total_answer_tokens": 118875,
          "discarded_tail_tokens": 875,
          "median_p_value": 0.9574836194235159,
          "median_log10_p_value": -0.01886864718161641,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 39,
          "total_answer_tokens": 118875,
          "discarded_tail_tokens": 1875,
          "median_p_value": 0.9746416714628057,
          "median_log10_p_value": -0.011155024003919335,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 11,
          "total_answer_tokens": 118875,
          "discarded_tail_tokens": 8875,
          "median_p_value": 0.9998470080082608,
          "median_log10_p_value": -6.64486609738552e-05,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 5,
          "total_answer_tokens": 118875,
          "discarded_tail_tokens": 18875,
          "median_p_value": 0.999999785861883,
          "median_log10_p_value": -9.299901254260768e-08,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 3,
          "total_answer_tokens": 118875,
          "discarded_tail_tokens": 28875,
          "median_p_value": 0.999999999997782,
          "median_log10_p_value": -9.632667063411467e-13,
          "status": "ok"
        }
      },
      "filtering": {
        "repetition_threshold": 0.5,
        "comparison": ">",
        "scope": "answer-internal adjacent token pairs; prompt excluded",
        "num_answers_before": 500,
        "num_answers_retained": 479,
        "num_answers_removed": 21,
        "fraction_answers_removed": 0.042,
        "total_answer_tokens_before": 141647,
        "total_answer_tokens_retained": 118875,
        "total_answer_tokens_removed": 22772,
        "removed_answer_ids": [
          "dolly-00423",
          "dolly-00720",
          "dolly-12249",
          "dolly-12764",
          "dolly-11348",
          "dolly-08406",
          "dolly-00143",
          "dolly-01162",
          "dolly-14358",
          "dolly-09918",
          "dolly-03773",
          "dolly-12951",
          "dolly-08607",
          "dolly-11386",
          "dolly-03319",
          "dolly-07407",
          "dolly-07780",
          "dolly-11182",
          "dolly-01356",
          "dolly-12236",
          "dolly-13235"
        ]
      }
    },
    "clean": {
      "aggregation": "ordinary_median",
      "num_answers": 412,
      "total_answer_tokens": 45882,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 45,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 882,
          "median_p_value": 0.6360891449864364,
          "median_log10_p_value": -0.1964820156995508,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 22,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 1882,
          "median_p_value": 0.7960378878131416,
          "median_log10_p_value": -0.09906626131183685,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 15,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 882,
          "median_p_value": 0.7386263221105359,
          "median_log10_p_value": -0.13157521964243946,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 4,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 5882,
          "median_p_value": 0.947596846602552,
          "median_log10_p_value": -0.0233763931850151,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 2,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 5882,
          "median_p_value": 0.9783739864832501,
          "median_log10_p_value": -0.009495103065976066,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 1,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 15882,
          "median_p_value": 0.9995678964162934,
          "median_log10_p_value": -0.00018770075802065225,
          "status": "ok"
        }
      },
      "filtering": {
        "repetition_threshold": 0.5,
        "comparison": ">",
        "scope": "answer-internal adjacent token pairs; prompt excluded",
        "num_answers_before": 500,
        "num_answers_retained": 412,
        "num_answers_removed": 88,
        "fraction_answers_removed": 0.176,
        "total_answer_tokens_before": 159765,
        "total_answer_tokens_retained": 45882,
        "total_answer_tokens_removed": 113883,
        "removed_answer_ids": [
          "dolly-00135",
          "dolly-12241",
          "dolly-07923",
          "dolly-07103",
          "dolly-05608",
          "dolly-07788",
          "dolly-11310",
          "dolly-02097",
          "dolly-03614",
          "dolly-13505",
          "dolly-02580",
          "dolly-08884",
          "dolly-12659",
          "dolly-00420",
          "dolly-11014",
          "dolly-08008",
          "dolly-02186",
          "dolly-00275",
          "dolly-08512",
          "dolly-14060",
          "dolly-01461",
          "dolly-02223",
          "dolly-04949",
          "dolly-08689",
          "dolly-08574",
          "dolly-08406",
          "dolly-04141",
          "dolly-03209",
          "dolly-06227",
          "dolly-11078",
          "dolly-09778",
          "dolly-04856",
          "dolly-13779",
          "dolly-06595",
          "dolly-08936",
          "dolly-09344",
          "dolly-05605",
          "dolly-08340",
          "dolly-04589",
          "dolly-04686",
          "dolly-14700",
          "dolly-03696",
          "dolly-03914",
          "dolly-11987",
          "dolly-01939",
          "dolly-05628",
          "dolly-13339",
          "dolly-08911",
          "dolly-03239",
          "dolly-13445",
          "dolly-02139",
          "dolly-14265",
          "dolly-13610",
          "dolly-07427",
          "dolly-09563",
          "dolly-02451",
          "dolly-13544",
          "dolly-06824",
          "dolly-05312",
          "dolly-10992",
          "dolly-06932",
          "dolly-08607",
          "dolly-05388",
          "dolly-11386",
          "dolly-02069",
          "dolly-09439",
          "dolly-00148",
          "dolly-08211",
          "dolly-12186",
          "dolly-03319",
          "dolly-07407",
          "dolly-10389",
          "dolly-03916",
          "dolly-08222",
          "dolly-14947",
          "dolly-03624",
          "dolly-09330",
          "dolly-11182",
          "dolly-02059",
          "dolly-02916",
          "dolly-09816",
          "dolly-05355",
          "dolly-06970",
          "dolly-05634",
          "dolly-02500",
          "dolly-11314",
          "dolly-13235",
          "dolly-04223"
        ]
      }
    }
  },
  "grouped_p_value_without_severe_repetition_method": "exclude whole answers whose answer-internal adjacent-token-pair repetition ratio (1 - unique pairs / all pairs) is strictly greater than 0.5; prompts excluded from repetition assessment; filter each label independently; retain original answer order, then concatenate teacher-tokenizer answer IDs without separators; exact disjoint blocks, first token context only; no token-pair deduplication within retained blocks; incomplete tail discarded; ordinary median of block p-values (mean of the middle two for even counts)",
  "per_group_p_value_without_severe_repetition_files": {
    "kgw": "/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new.nonrepetitive_grouped_p_values.json",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.nonrepetitive_grouped_p_values.json"
  },
  "ppl": {
    "enabled": true,
    "schema": "saved-answer-reference-ppl-v1",
    "configuration": {
      "model_path": "/shared/public_models/Llama-3-8B",
      "device": "cuda",
      "dtype": "bfloat16",
      "generation_tokenizer": "/shared/public_models/Qwen2.5-0.5B",
      "max_length": null,
      "overflow": "error",
      "effective_max_length": 8192,
      "protocol": {
        "prompt": "source-generation-prompt; source chat template, not reference chat template",
        "boundary": "encode prompt and answer separately with add_special_tokens=False, then concatenate",
        "bos": "one reference BOS at start when defined; no extra EOS",
        "loss": "causal next-token NLL on all answer tokens, including the first; no prompt or padding loss",
        "aggregate": "exp(sum(answer NLL) / sum(scored answer tokens)); not mean per-answer PPL",
        "source_tokenizer_selection": "explicit override, otherwise row.model_path; fallback assumes the generation tokenizer matches that checkpoint",
        "legacy_prompt_limit": 2048,
        "weights_fingerprint": "weight filenames, sizes and mtime_ns; weight contents are not hashed"
      },
      "reference_assets": {
        "path": "/shared/public_models/Llama-3-8B",
        "assets": [
          {
            "name": "config.json",
            "size": 654,
            "sha256": "2430cee764b6530ff8673cf9ba8561e1d5a33152d503cd0de909ff5718261441"
          },
          {
            "name": "generation_config.json",
            "size": 126,
            "sha256": "55550e95c40c53fb0ee3f960d6d2b25a46405c8f790e5c4bb02caf3e98f2b5d0"
          },
          {
            "name": "model.safetensors.index.json",
            "size": 23950,
            "sha256": "146776fce3f6db1103aa6f249e65ee5544c5923ce6f971b092eee79aa6e5d37b"
          },
          {
            "name": "special_tokens_map.json",
            "size": 73,
            "sha256": "462d91939dbc37178aa5a3eae7068d1990ccc92e09f288cc71f42cdf139d69cc"
          },
          {
            "name": "tokenizer.json",
            "size": 9085698,
            "sha256": "e134af98b985517b4f068e3755ae90d4e9cd2d45d328325dc503f1c6b2d06cc7"
          },
          {
            "name": "tokenizer_config.json",
            "size": 50566,
            "sha256": "690727b4fed286383df1c7ca5e805124cb70c6eb4529f807c7b2e60ff741da7e"
          }
        ],
        "weight_stats": [
          {
            "name": "model-00001-of-00004.safetensors",
            "size": 4976698672,
            "mtime_ns": 1736746522477644778
          },
          {
            "name": "model-00002-of-00004.safetensors",
            "size": 4999802720,
            "mtime_ns": 1736746656058650226
          },
          {
            "name": "model-00003-of-00004.safetensors",
            "size": 4915916176,
            "mtime_ns": 1736746768408654808
          },
          {
            "name": "model-00004-of-00004.safetensors",
            "size": 1168138808,
            "mtime_ns": 1736746796088655937
          }
        ],
        "weight_content_hashed": false
      },
      "software": {
        "python": "3.10.21",
        "torch": "2.6.0",
        "transformers": "4.51.3",
        "tokenizers": "0.21.4"
      }
    },
    "files": {
      "kgw": {
        "samples": 500,
        "valid_samples": 500,
        "skipped_empty_answers": 0,
        "complete": true,
        "nonfinite_samples": 0,
        "status": "ok",
        "total_nll": 165183.80199582456,
        "scored_tokens": 138174,
        "mean_nll": 1.1954767322059472,
        "token_weighted_ppl": 3.3051330583504672,
        "mean_answer_tokens": 276.348,
        "source_prompt_truncated_samples": 0,
        "reference_prompt_truncated_samples": 0,
        "generation_configurations": [
          {
            "configuration": {
              "temperature": 0.7,
              "top_p": 0.9,
              "max_new_tokens": 1536,
              "max_prompt_tokens": 6144,
              "prompt_truncated": false,
              "kgw_enabled_during_generation": false,
              "wn_enabled_during_generation": true
            },
            "samples": 500
          }
        ],
        "generation_seeds": {
          "recorded_samples": 500,
          "minimum": 42,
          "maximum": 541,
          "individual_values": "see per-sample immutable records"
        },
        "student_model_paths": [
          "/shared/wwx/EasyGAD/checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_new/gad/global_step_1813/actor/huggingface"
        ],
        "generation_tokenizer_paths": [
          "/shared/public_models/Qwen2.5-0.5B"
        ],
        "source_path": "/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new.jsonl",
        "source_sha256": "a6cb5b53fe168f08def87ed1c4ebb6a5e038e93fe2ba6ba94044adbb8ff9d034",
        "per_sample_file": "/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new.ppl.2f44d6804314edd20e4f.jsonl",
        "cache_reused": false
      },
      "clean": {
        "samples": 500,
        "valid_samples": 500,
        "skipped_empty_answers": 0,
        "complete": true,
        "nonfinite_samples": 0,
        "status": "ok",
        "total_nll": 67054.72902449768,
        "scored_tokens": 156267,
        "mean_nll": 0.42910357928735865,
        "token_weighted_ppl": 1.5358801115260794,
        "mean_answer_tokens": 312.534,
        "source_prompt_truncated_samples": 3,
        "reference_prompt_truncated_samples": 0,
        "generation_configurations": [
          {
            "configuration": {
              "kgw_enabled_during_generation": false,
              "max_new_tokens": 1536,
              "max_prompt_tokens": 2048,
              "temperature": 0.7,
              "top_p": 0.9
            },
            "samples": 500
          }
        ],
        "generation_seeds": {
          "recorded_samples": 500,
          "minimum": 42,
          "maximum": 541,
          "individual_values": "see per-sample immutable records"
        },
        "student_model_paths": [
          "/shared/public_models/Qwen2.5-0.5B"
        ],
        "generation_tokenizer_paths": [
          "/shared/public_models/Qwen2.5-0.5B"
        ],
        "source_path": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl",
        "source_sha256": "597b843d28d31c353c7bb9b94a3b6dccb564cb45ac2c5252f6a1592ccd768efe",
        "per_sample_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.ppl.877fc574f9ee35a5145f.jsonl",
        "cache_reused": true
      }
    }
  },
  "evaluated_at": "2026-10-19T17:20:18+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-10-19T17:21:42+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.416208
- 实际检测配置：`{"gamma": 0.5, "hash_key": 15485863, "seeding": "simple_1 (hash_key * previous_token_id)", "delta_by_label": {"kgw": 3.0, "clean": 2.0}}`
- ROUGE-L（同批 500 条原始 Dolly 回答作参考）：0.175276（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 原始 Dolly 参考文件：`/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl`
- ROUGE-L（同批 500 条 14B clean 教师回答作参考）：0.270563（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 14B clean 教师参考文件：`/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_clean_test.parquet`
- Best F1：0.669388（z 阈值 -6.685065756345757，TPR 0.984000，FPR 0.956000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.010000 | 0.004000 | 0.007890 | 9.593834825900782 |
  | 5% | 0.050000 | 0.024000 | 0.044693 | 2.2223355980148636 |
  | 10% | 0.100000 | 0.052000 | 0.090278 | 1.6994116628998401 |

两种逐条文本 p-value 统计（单侧正态近似；不是 AUROC 的显著性检验）：

去重规则：相同的 `(previous_token_id, token_id)` 只计一次；不修改回答文本。

| 数据 | 检测方式 | 有效样本 | p 均值 | p 中位数 | p≤0.01 | p≤0.05 | p≤0.10 |
|---|---|---:|---:|---:|---:|---:|---:|
| kgw | 原始 | 500/500 | 0.639621 | 0.716527 | 8 (1.60%) | 32 (6.40%) | 50 (10.00%) |
| kgw | token 对去重 | 500/500 | 0.635533 | 0.70537 | 1 (0.20%) | 12 (2.40%) | 34 (6.80%) |
| clean | 原始 | 500/500 | 0.538121 | 0.57157 | 22 (4.40%) | 54 (10.80%) | 73 (14.60%) |
| clean | token 对去重 | 500/500 | 0.537418 | 0.555154 | 5 (1.00%) | 25 (5.00%) | 46 (9.20%) |

KGW 的小 p 占比是该理论阈值下的检出率，clean 的小 p 占比是实测误报率。p≤0.05 不保证实际 FPR=5%；去重可改善重复带来的失真，但不保证完全校准。空回答不做显著性检验，p=null，并排除在有效样本统计之外。

逐条 p-value：`/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new_strength3.p_values.jsonl`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl`

固定 token 分组 p-value（普通中位数；p 越大表示原单侧检验证据越弱）：

按教师 tokenizer 编码回答并无分隔拼接，精确分组；每组首 token 仅作上下文，其余 token 用本项目原 KGW 绿表评分；不去重，尾部不足一组丢弃；各组 p 排序后取普通中位数（偶数组取中间两个 p 的算术平均）。

| 每组 token 数 | 计分 token 数 | KGW 组数 | KGW median p ↑ | clean 组数 | clean median p | KGW/clean 丢弃尾部 tokens |
|---:|---:|---:|---:|---:|---:|---:|
| 1000 | 999 | 155 | 0.953214 | 159 | 0.865929 | 939/765 |
| 2000 | 1999 | 77 | 0.994946 | 79 | 0.971358 | 1939/1765 |
| 3000 | 2999 | 51 | 0.998542 | 53 | 0.982134 | 2939/765 |
| 10000 | 9999 | 15 | 1 | 15 | 1 | 5939/9765 |
| 20000 | 19999 | 7 | 1 | 7 | 1 | 15939/19765 |
| 30000 | 29999 | 5 | 1 | 5 | 1 | 5939/9765 |

N/A 表示总 token 数不足一个完整组；组数为 1 或 2 时需结合逐组结果解释。极小 p 用科学计数法字符串保存，同时保留 log10(p)，避免浮点下溢为 0。

逐组 p-value 缓存：`/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new_strength3.grouped_p_values.json`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.grouped_p_values.json`

剔除严重重复回答后的固定 token 分组 p-value（普通中位数）：

先独立筛选 KGW 和 clean：回答内部相邻 token 对重复比例严格大于 50% 时，剔除整条回答；prompt 不参与判断。保留回答按原顺序重新无分隔拼接，各组首 token 仅作上下文；组内不做 token 对去重，尾部不足一组丢弃。这是质量筛选补充指标，原始全样本统计另行保留。

| 数据 | 原回答数 | 剔除严重重复回答 | 保留回答数 | 原 tokens | 剔除 tokens | 保留 tokens |
|---|---:|---:|---:|---:|---:|---:|
| kgw | 500 | 35 (7.00%) | 465 | 155939 | 37582 | 118357 |
| clean | 500 | 88 (17.60%) | 412 | 159765 | 113883 | 45882 |

| 每组 token 数 | 计分 token 数 | KGW 组数 | KGW median p ↑ | clean 组数 | clean median p | KGW/clean 丢弃尾部 tokens |
|---:|---:|---:|---:|---:|---:|---:|
| 1000 | 999 | 118 | 0.939464 | 45 | 0.636089 | 357/882 |
| 2000 | 1999 | 59 | 0.974165 | 22 | 0.796038 | 357/1882 |
| 3000 | 2999 | 39 | 0.994984 | 15 | 0.738626 | 1357/882 |
| 10000 | 9999 | 11 | 0.999999 | 4 | 0.947597 | 8357/5882 |
| 20000 | 19999 | 5 | 1 | 2 | 0.978374 | 18357/5882 |
| 30000 | 29999 | 3 | 1 | 1 | 0.999568 | 28357/15882 |

N/A 表示筛选后不足一个完整组。各组 p 取普通中位数，偶数组取中间两个 p 的算术平均；组数较少时请结合逐组缓存解释。

剔除严重重复回答后的逐组 p-value 缓存：`/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new_strength3.nonrepetitive_grouped_p_values.json`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.nonrepetitive_grouped_p_values.json`

### 固定参考模型 PPL（只评分已保存的回答）

| 文件组 | 总体 PPL ↓ | 有效样本/总样本 | 计分回答 tokens | 平均回答 tokens | 状态 | 缓存复用 |
|---|---:|---:|---:|---:|---|---|
| kgw | 3.196939 | 500/500 | 149884 | 299.77 | ok | False |
| clean | 1.535880 | 500/500 | 156267 | 312.53 | ok | True |

总体 PPL = exp(全部有效回答 NLL 总和 / 全部计分回答 token 数)，不是逐条 PPL 的算术平均。
原生成 tokenizer 恢复实际生成 prompt；参考 tokenizer 对 prompt/answer 分开编码后拼接；只计回答，包含首回答 token。Base 参考模型不再套用 chat template；只添加一次参考 BOS，不额外评分 EOS；输入 JSONL 不修改。

- kgw: `/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new_strength3.jsonl`；SHA256 `b8eb3e5748736faeb53e3df2749af258cbaab7288da6a9eebedf771ac7db747d`；逐条明细 `/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new_strength3.ppl.6d3efc6e08e6739eceb1.jsonl`；空回答 0；异常 loss 0；原生成截断 0；参考上下文截断 0。

  生成文本配置（种子逐条保存在明细中）：

```json
{
  "student_model_paths": [
    "/shared/wwx/EasyGAD/checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_new/gad/global_step_1813/actor/huggingface"
  ],
  "generation_tokenizer_paths": [
    "/shared/public_models/Qwen2.5-0.5B"
  ],
  "generation_configurations": [
    {
      "configuration": {
        "temperature": 0.7,
        "top_p": 0.9,
        "max_new_tokens": 1536,
        "max_prompt_tokens": 6144,
        "prompt_truncated": false,
        "kgw_enabled_during_generation": false,
        "wn_enabled_during_generation": true
      },
      "samples": 500
    }
  ],
  "generation_seeds": {
    "recorded_samples": 500,
    "minimum": 42,
    "maximum": 541,
    "individual_values": "see per-sample immutable records"
  }
}
```
- clean: `/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl`；SHA256 `597b843d28d31c353c7bb9b94a3b6dccb564cb45ac2c5252f6a1592ccd768efe`；逐条明细 `/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.ppl.877fc574f9ee35a5145f.jsonl`；空回答 0；异常 loss 0；原生成截断 3；参考上下文截断 0。

  生成文本配置（种子逐条保存在明细中）：

```json
{
  "student_model_paths": [
    "/shared/public_models/Qwen2.5-0.5B"
  ],
  "generation_tokenizer_paths": [
    "/shared/public_models/Qwen2.5-0.5B"
  ],
  "generation_configurations": [
    {
      "configuration": {
        "kgw_enabled_during_generation": false,
        "max_new_tokens": 1536,
        "max_prompt_tokens": 2048,
        "temperature": 0.7,
        "top_p": 0.9
      },
      "samples": 500
    }
  ],
  "generation_seeds": {
    "recorded_samples": 500,
    "minimum": 42,
    "maximum": 541,
    "individual_values": "see per-sample immutable records"
  }
}
```

完整评分配置（含模型/tokenizer 指纹、软件版本；权重使用 size/mtime 标识，不全量哈希）：

```json
{
  "model_path": "/shared/public_models/Llama-3-8B",
  "device": "cuda",
  "dtype": "bfloat16",
  "generation_tokenizer": "/shared/public_models/Qwen2.5-0.5B",
  "max_length": null,
  "overflow": "error",
  "effective_max_length": 8192,
  "protocol": {
    "prompt": "source-generation-prompt; source chat template, not reference chat template",
    "boundary": "encode prompt and answer separately with add_special_tokens=False, then concatenate",
    "bos": "one reference BOS at start when defined; no extra EOS",
    "loss": "causal next-token NLL on all answer tokens, including the first; no prompt or padding loss",
    "aggregate": "exp(sum(answer NLL) / sum(scored answer tokens)); not mean per-answer PPL",
    "source_tokenizer_selection": "explicit override, otherwise row.model_path; fallback assumes the generation tokenizer matches that checkpoint",
    "legacy_prompt_limit": 2048,
    "weights_fingerprint": "weight filenames, sizes and mtime_ns; weight contents are not hashed"
  },
  "reference_assets": {
    "path": "/shared/public_models/Llama-3-8B",
    "assets": [
      {
        "name": "config.json",
        "size": 654,
        "sha256": "2430cee764b6530ff8673cf9ba8561e1d5a33152d503cd0de909ff5718261441"
      },
      {
        "name": "generation_config.json",
        "size": 126,
        "sha256": "55550e95c40c53fb0ee3f960d6d2b25a46405c8f790e5c4bb02caf3e98f2b5d0"
      },
      {
        "name": "model.safetensors.index.json",
        "size": 23950,
        "sha256": "146776fce3f6db1103aa6f249e65ee5544c5923ce6f971b092eee79aa6e5d37b"
      },
      {
        "name": "special_tokens_map.json",
        "size": 73,
        "sha256": "462d91939dbc37178aa5a3eae7068d1990ccc92e09f288cc71f42cdf139d69cc"
      },
      {
        "name": "tokenizer.json",
        "size": 9085698,
        "sha256": "e134af98b985517b4f068e3755ae90d4e9cd2d45d328325dc503f1c6b2d06cc7"
      },
      {
        "name": "tokenizer_config.json",
        "size": 50566,
        "sha256": "690727b4fed286383df1c7ca5e805124cb70c6eb4529f807c7b2e60ff741da7e"
      }
    ],
    "weight_stats": [
      {
        "name": "model-00001-of-00004.safetensors",
        "size": 4976698672,
        "mtime_ns": 1736746522477644778
      },
      {
        "name": "model-00002-of-00004.safetensors",
        "size": 4999802720,
        "mtime_ns": 1736746656058650226
      },
      {
        "name": "model-00003-of-00004.safetensors",
        "size": 4915916176,
        "mtime_ns": 1736746768408654808
      },
      {
        "name": "model-00004-of-00004.safetensors",
        "size": 1168138808,
        "mtime_ns": 1736746796088655937
      }
    ],
    "weight_content_hashed": false
  },
  "software": {
    "python": "3.10.21",
    "torch": "2.6.0",
    "transformers": "4.51.3",
    "tokenizers": "0.21.4"
  }
}
```

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.416208,
  "best_f1": {
    "threshold": -6.685065756345757,
    "fpr": 0.956,
    "tpr": 0.984,
    "precision": 0.5072164948453608,
    "f1": 0.6693877551020408,
    "tp": 492,
    "fp": 478,
    "tn": 22,
    "fn": 8
  },
  "tpr_at_fpr": {
    "1%": {
      "threshold": 9.593834825900782,
      "fpr": 0.01,
      "tpr": 0.004,
      "precision": 0.2857142857142857,
      "f1": 0.007889546351084811,
      "tp": 2,
      "fp": 5,
      "tn": 495,
      "fn": 498,
      "target_fpr": 0.01
    },
    "5%": {
      "threshold": 2.2223355980148636,
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
      "threshold": 1.6994116628998401,
      "fpr": 0.1,
      "tpr": 0.052,
      "precision": 0.34210526315789475,
      "f1": 0.09027777777777778,
      "tp": 26,
      "fp": 50,
      "tn": 450,
      "fn": 474,
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
      "clean": 2.0
    }
  },
  "rouge_l_dolly": {
    "mean": 0.17527607072154583,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new_strength3.jsonl",
    "reference_file": "/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl",
    "reference_source": "databricks/databricks-dolly-15k:response",
    "metric": "rougeL",
    "measure": "fmeasure",
    "use_stemmer": true,
    "aggregation": "unweighted mean of per-sample ROUGE-L F1"
  },
  "rouge_l_teacher_clean": {
    "mean": 0.27056293657683556,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new_strength3.jsonl",
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
        "mean": 0.6396205720998028,
        "median": 0.7165273408147196,
        "min": 1.6759570266182036e-84,
        "max": 1.0,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 8,
            "fraction": 0.016
          },
          "5%": {
            "alpha": 0.05,
            "count": 32,
            "fraction": 0.064
          },
          "10%": {
            "alpha": 0.1,
            "count": 50,
            "fraction": 0.1
          }
        }
      },
      "deduplicated": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.6355330807744789,
        "median": 0.7053699393912358,
        "min": 0.00921106272704951,
        "max": 0.9989289915261519,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 1,
            "fraction": 0.002
          },
          "5%": {
            "alpha": 0.05,
            "count": 12,
            "fraction": 0.024
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
    "kgw": "/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new_strength3.p_values.jsonl",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl"
  },
  "grouped_p_values": {
    "kgw": {
      "aggregation": "ordinary_median",
      "num_answers": 500,
      "total_answer_tokens": 155939,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 155,
          "total_answer_tokens": 155939,
          "discarded_tail_tokens": 939,
          "median_p_value": 0.9532136797396964,
          "median_log10_p_value": -0.02080973364321328,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 77,
          "total_answer_tokens": 155939,
          "discarded_tail_tokens": 1939,
          "median_p_value": 0.9949461262550343,
          "median_log10_p_value": -0.00220043453426638,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 51,
          "total_answer_tokens": 155939,
          "discarded_tail_tokens": 2939,
          "median_p_value": 0.998541992279534,
          "median_log10_p_value": -0.0006336667654240838,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 15,
          "total_answer_tokens": 155939,
          "discarded_tail_tokens": 5939,
          "median_p_value": 0.9999999992771296,
          "median_log10_p_value": -3.139386390720775e-10,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 7,
          "total_answer_tokens": 155939,
          "discarded_tail_tokens": 15939,
          "median_p_value": 1.0,
          "median_log10_p_value": 0.0,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 5,
          "total_answer_tokens": 155939,
          "discarded_tail_tokens": 5939,
          "median_p_value": 1.0,
          "median_log10_p_value": 0.0,
          "status": "ok"
        }
      }
    },
    "clean": {
      "aggregation": "ordinary_median",
      "num_answers": 500,
      "total_answer_tokens": 159765,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 159,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 765,
          "median_p_value": 0.8659288977499955,
          "median_log10_p_value": -0.06251776685396769,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 79,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 1765,
          "median_p_value": 0.971357711016285,
          "median_log10_p_value": -0.012620807875598238,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 53,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 765,
          "median_p_value": 0.9821335190767914,
          "median_log10_p_value": -0.007829466737979084,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 15,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 9765,
          "median_p_value": 0.9999999999999984,
          "median_log10_p_value": -6.750292265873014e-16,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 7,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 19765,
          "median_p_value": 1.0,
          "median_log10_p_value": 0.0,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 5,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 9765,
          "median_p_value": 1.0,
          "median_log10_p_value": 0.0,
          "status": "ok"
        }
      }
    }
  },
  "grouped_p_value_method": "teacher-tokenizer answer IDs concatenated without separators; exact disjoint blocks; first token of each block is context only; no repetition deduplication; incomplete tail discarded; ordinary median of block p-values (arithmetic mean of the two middle p-values for even group counts)",
  "per_group_p_value_files": {
    "kgw": "/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new_strength3.grouped_p_values.json",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.grouped_p_values.json"
  },
  "grouped_p_values_without_severe_repetition": {
    "kgw": {
      "aggregation": "ordinary_median",
      "num_answers": 465,
      "total_answer_tokens": 118357,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 118,
          "total_answer_tokens": 118357,
          "discarded_tail_tokens": 357,
          "median_p_value": 0.939464203891651,
          "median_log10_p_value": -0.02711976303391753,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 59,
          "total_answer_tokens": 118357,
          "discarded_tail_tokens": 357,
          "median_p_value": 0.9741645610210904,
          "median_log10_p_value": -0.011367673607334343,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 39,
          "total_answer_tokens": 118357,
          "discarded_tail_tokens": 1357,
          "median_p_value": 0.994984011891031,
          "median_log10_p_value": -0.0021838977500412957,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 11,
          "total_answer_tokens": 118357,
          "discarded_tail_tokens": 8357,
          "median_p_value": 0.9999988787079404,
          "median_log10_p_value": -4.869712271251867e-07,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 5,
          "total_answer_tokens": 118357,
          "discarded_tail_tokens": 18357,
          "median_p_value": 0.9999999999903094,
          "median_log10_p_value": -4.208566145925575e-12,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 3,
          "total_answer_tokens": 118357,
          "discarded_tail_tokens": 28357,
          "median_p_value": 0.9999999999999941,
          "median_log10_p_value": -2.5554677863662184e-15,
          "status": "ok"
        }
      },
      "filtering": {
        "repetition_threshold": 0.5,
        "comparison": ">",
        "scope": "answer-internal adjacent token pairs; prompt excluded",
        "num_answers_before": 500,
        "num_answers_retained": 465,
        "num_answers_removed": 35,
        "fraction_answers_removed": 0.07,
        "total_answer_tokens_before": 155939,
        "total_answer_tokens_retained": 118357,
        "total_answer_tokens_removed": 37582,
        "removed_answer_ids": [
          "dolly-00423",
          "dolly-12156",
          "dolly-11025",
          "dolly-00720",
          "dolly-07788",
          "dolly-06622",
          "dolly-07239",
          "dolly-08709",
          "dolly-13505",
          "dolly-04362",
          "dolly-04421",
          "dolly-05394",
          "dolly-02844",
          "dolly-06920",
          "dolly-06595",
          "dolly-14358",
          "dolly-09918",
          "dolly-06771",
          "dolly-11987",
          "dolly-05628",
          "dolly-14970",
          "dolly-11030",
          "dolly-11445",
          "dolly-06895",
          "dolly-08607",
          "dolly-11386",
          "dolly-09439",
          "dolly-08451",
          "dolly-14465",
          "dolly-07407",
          "dolly-02816",
          "dolly-12001",
          "dolly-01356",
          "dolly-12236",
          "dolly-13235"
        ]
      }
    },
    "clean": {
      "aggregation": "ordinary_median",
      "num_answers": 412,
      "total_answer_tokens": 45882,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 45,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 882,
          "median_p_value": 0.6360891449864364,
          "median_log10_p_value": -0.1964820156995508,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 22,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 1882,
          "median_p_value": 0.7960378878131416,
          "median_log10_p_value": -0.09906626131183685,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 15,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 882,
          "median_p_value": 0.7386263221105359,
          "median_log10_p_value": -0.13157521964243946,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 4,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 5882,
          "median_p_value": 0.947596846602552,
          "median_log10_p_value": -0.0233763931850151,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 2,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 5882,
          "median_p_value": 0.9783739864832501,
          "median_log10_p_value": -0.009495103065976066,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 1,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 15882,
          "median_p_value": 0.9995678964162934,
          "median_log10_p_value": -0.00018770075802065225,
          "status": "ok"
        }
      },
      "filtering": {
        "repetition_threshold": 0.5,
        "comparison": ">",
        "scope": "answer-internal adjacent token pairs; prompt excluded",
        "num_answers_before": 500,
        "num_answers_retained": 412,
        "num_answers_removed": 88,
        "fraction_answers_removed": 0.176,
        "total_answer_tokens_before": 159765,
        "total_answer_tokens_retained": 45882,
        "total_answer_tokens_removed": 113883,
        "removed_answer_ids": [
          "dolly-00135",
          "dolly-12241",
          "dolly-07923",
          "dolly-07103",
          "dolly-05608",
          "dolly-07788",
          "dolly-11310",
          "dolly-02097",
          "dolly-03614",
          "dolly-13505",
          "dolly-02580",
          "dolly-08884",
          "dolly-12659",
          "dolly-00420",
          "dolly-11014",
          "dolly-08008",
          "dolly-02186",
          "dolly-00275",
          "dolly-08512",
          "dolly-14060",
          "dolly-01461",
          "dolly-02223",
          "dolly-04949",
          "dolly-08689",
          "dolly-08574",
          "dolly-08406",
          "dolly-04141",
          "dolly-03209",
          "dolly-06227",
          "dolly-11078",
          "dolly-09778",
          "dolly-04856",
          "dolly-13779",
          "dolly-06595",
          "dolly-08936",
          "dolly-09344",
          "dolly-05605",
          "dolly-08340",
          "dolly-04589",
          "dolly-04686",
          "dolly-14700",
          "dolly-03696",
          "dolly-03914",
          "dolly-11987",
          "dolly-01939",
          "dolly-05628",
          "dolly-13339",
          "dolly-08911",
          "dolly-03239",
          "dolly-13445",
          "dolly-02139",
          "dolly-14265",
          "dolly-13610",
          "dolly-07427",
          "dolly-09563",
          "dolly-02451",
          "dolly-13544",
          "dolly-06824",
          "dolly-05312",
          "dolly-10992",
          "dolly-06932",
          "dolly-08607",
          "dolly-05388",
          "dolly-11386",
          "dolly-02069",
          "dolly-09439",
          "dolly-00148",
          "dolly-08211",
          "dolly-12186",
          "dolly-03319",
          "dolly-07407",
          "dolly-10389",
          "dolly-03916",
          "dolly-08222",
          "dolly-14947",
          "dolly-03624",
          "dolly-09330",
          "dolly-11182",
          "dolly-02059",
          "dolly-02916",
          "dolly-09816",
          "dolly-05355",
          "dolly-06970",
          "dolly-05634",
          "dolly-02500",
          "dolly-11314",
          "dolly-13235",
          "dolly-04223"
        ]
      }
    }
  },
  "grouped_p_value_without_severe_repetition_method": "exclude whole answers whose answer-internal adjacent-token-pair repetition ratio (1 - unique pairs / all pairs) is strictly greater than 0.5; prompts excluded from repetition assessment; filter each label independently; retain original answer order, then concatenate teacher-tokenizer answer IDs without separators; exact disjoint blocks, first token context only; no token-pair deduplication within retained blocks; incomplete tail discarded; ordinary median of block p-values (mean of the middle two for even counts)",
  "per_group_p_value_without_severe_repetition_files": {
    "kgw": "/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new_strength3.nonrepetitive_grouped_p_values.json",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.nonrepetitive_grouped_p_values.json"
  },
  "ppl": {
    "enabled": true,
    "schema": "saved-answer-reference-ppl-v1",
    "configuration": {
      "model_path": "/shared/public_models/Llama-3-8B",
      "device": "cuda",
      "dtype": "bfloat16",
      "generation_tokenizer": "/shared/public_models/Qwen2.5-0.5B",
      "max_length": null,
      "overflow": "error",
      "effective_max_length": 8192,
      "protocol": {
        "prompt": "source-generation-prompt; source chat template, not reference chat template",
        "boundary": "encode prompt and answer separately with add_special_tokens=False, then concatenate",
        "bos": "one reference BOS at start when defined; no extra EOS",
        "loss": "causal next-token NLL on all answer tokens, including the first; no prompt or padding loss",
        "aggregate": "exp(sum(answer NLL) / sum(scored answer tokens)); not mean per-answer PPL",
        "source_tokenizer_selection": "explicit override, otherwise row.model_path; fallback assumes the generation tokenizer matches that checkpoint",
        "legacy_prompt_limit": 2048,
        "weights_fingerprint": "weight filenames, sizes and mtime_ns; weight contents are not hashed"
      },
      "reference_assets": {
        "path": "/shared/public_models/Llama-3-8B",
        "assets": [
          {
            "name": "config.json",
            "size": 654,
            "sha256": "2430cee764b6530ff8673cf9ba8561e1d5a33152d503cd0de909ff5718261441"
          },
          {
            "name": "generation_config.json",
            "size": 126,
            "sha256": "55550e95c40c53fb0ee3f960d6d2b25a46405c8f790e5c4bb02caf3e98f2b5d0"
          },
          {
            "name": "model.safetensors.index.json",
            "size": 23950,
            "sha256": "146776fce3f6db1103aa6f249e65ee5544c5923ce6f971b092eee79aa6e5d37b"
          },
          {
            "name": "special_tokens_map.json",
            "size": 73,
            "sha256": "462d91939dbc37178aa5a3eae7068d1990ccc92e09f288cc71f42cdf139d69cc"
          },
          {
            "name": "tokenizer.json",
            "size": 9085698,
            "sha256": "e134af98b985517b4f068e3755ae90d4e9cd2d45d328325dc503f1c6b2d06cc7"
          },
          {
            "name": "tokenizer_config.json",
            "size": 50566,
            "sha256": "690727b4fed286383df1c7ca5e805124cb70c6eb4529f807c7b2e60ff741da7e"
          }
        ],
        "weight_stats": [
          {
            "name": "model-00001-of-00004.safetensors",
            "size": 4976698672,
            "mtime_ns": 1736746522477644778
          },
          {
            "name": "model-00002-of-00004.safetensors",
            "size": 4999802720,
            "mtime_ns": 1736746656058650226
          },
          {
            "name": "model-00003-of-00004.safetensors",
            "size": 4915916176,
            "mtime_ns": 1736746768408654808
          },
          {
            "name": "model-00004-of-00004.safetensors",
            "size": 1168138808,
            "mtime_ns": 1736746796088655937
          }
        ],
        "weight_content_hashed": false
      },
      "software": {
        "python": "3.10.21",
        "torch": "2.6.0",
        "transformers": "4.51.3",
        "tokenizers": "0.21.4"
      }
    },
    "files": {
      "kgw": {
        "samples": 500,
        "valid_samples": 500,
        "skipped_empty_answers": 0,
        "complete": true,
        "nonfinite_samples": 0,
        "status": "ok",
        "total_nll": 174194.25859526824,
        "scored_tokens": 149884,
        "mean_nll": 1.1621938205229927,
        "token_weighted_ppl": 3.1969390991536555,
        "mean_answer_tokens": 299.768,
        "source_prompt_truncated_samples": 0,
        "reference_prompt_truncated_samples": 0,
        "generation_configurations": [
          {
            "configuration": {
              "temperature": 0.7,
              "top_p": 0.9,
              "max_new_tokens": 1536,
              "max_prompt_tokens": 6144,
              "prompt_truncated": false,
              "kgw_enabled_during_generation": false,
              "wn_enabled_during_generation": true
            },
            "samples": 500
          }
        ],
        "generation_seeds": {
          "recorded_samples": 500,
          "minimum": 42,
          "maximum": 541,
          "individual_values": "see per-sample immutable records"
        },
        "student_model_paths": [
          "/shared/wwx/EasyGAD/checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_new/gad/global_step_1813/actor/huggingface"
        ],
        "generation_tokenizer_paths": [
          "/shared/public_models/Qwen2.5-0.5B"
        ],
        "source_path": "/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new_strength3.jsonl",
        "source_sha256": "b8eb3e5748736faeb53e3df2749af258cbaab7288da6a9eebedf771ac7db747d",
        "per_sample_file": "/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new_strength3.ppl.6d3efc6e08e6739eceb1.jsonl",
        "cache_reused": false
      },
      "clean": {
        "samples": 500,
        "valid_samples": 500,
        "skipped_empty_answers": 0,
        "complete": true,
        "nonfinite_samples": 0,
        "status": "ok",
        "total_nll": 67054.72902449768,
        "scored_tokens": 156267,
        "mean_nll": 0.42910357928735865,
        "token_weighted_ppl": 1.5358801115260794,
        "mean_answer_tokens": 312.534,
        "source_prompt_truncated_samples": 3,
        "reference_prompt_truncated_samples": 0,
        "generation_configurations": [
          {
            "configuration": {
              "kgw_enabled_during_generation": false,
              "max_new_tokens": 1536,
              "max_prompt_tokens": 2048,
              "temperature": 0.7,
              "top_p": 0.9
            },
            "samples": 500
          }
        ],
        "generation_seeds": {
          "recorded_samples": 500,
          "minimum": 42,
          "maximum": 541,
          "individual_values": "see per-sample immutable records"
        },
        "student_model_paths": [
          "/shared/public_models/Qwen2.5-0.5B"
        ],
        "generation_tokenizer_paths": [
          "/shared/public_models/Qwen2.5-0.5B"
        ],
        "source_path": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl",
        "source_sha256": "597b843d28d31c353c7bb9b94a3b6dccb564cb45ac2c5252f6a1592ccd768efe",
        "per_sample_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.ppl.877fc574f9ee35a5145f.jsonl",
        "cache_reused": true
      }
    }
  },
  "evaluated_at": "2026-10-19T17:21:42+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new_strength3.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-10-29T16:50:13+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.535000
- 实际检测配置：`{"gamma": 0.5, "hash_key": 15485863, "seeding": "simple_1 (hash_key * previous_token_id)", "delta_by_label": {"kgw": 3.0, "clean": 2.0}}`
- ROUGE-L（同批 500 条原始 Dolly 回答作参考）：0.197498（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 原始 Dolly 参考文件：`/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl`
- ROUGE-L（同批 500 条 14B clean 教师回答作参考）：0.248975（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 14B clean 教师参考文件：`/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_clean_test.parquet`
- Best F1：0.670765（z 阈值 -5.613413993878117，TPR 0.982000，FPR 0.946000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.010000 | 0.006000 | 0.011811 | 12.40054182283984 |
  | 5% | 0.046000 | 0.072000 | 0.128801 | 2.263009527424072 |
  | 10% | 0.100000 | 0.112000 | 0.184818 | 1.6903085094570331 |

两种逐条文本 p-value 统计（单侧正态近似；不是 AUROC 的显著性检验）：

去重规则：相同的 `(previous_token_id, token_id)` 只计一次；不修改回答文本。

| 数据 | 检测方式 | 有效样本 | p 均值 | p 中位数 | p≤0.01 | p≤0.05 | p≤0.10 |
|---|---|---:|---:|---:|---:|---:|---:|
| kgw | 原始 | 500/500 | 0.498251 | 0.46888 | 34 (6.80%) | 56 (11.20%) | 81 (16.20%) |
| kgw | token 对去重 | 500/500 | 0.520983 | 0.541992 | 10 (2.00%) | 35 (7.00%) | 52 (10.40%) |
| clean | 原始 | 500/500 | 0.538121 | 0.57157 | 22 (4.40%) | 54 (10.80%) | 73 (14.60%) |
| clean | token 对去重 | 500/500 | 0.537418 | 0.555154 | 5 (1.00%) | 25 (5.00%) | 46 (9.20%) |

KGW 的小 p 占比是该理论阈值下的检出率，clean 的小 p 占比是实测误报率。p≤0.05 不保证实际 FPR=5%；去重可改善重复带来的失真，但不保证完全校准。空回答不做显著性检验，p=null，并排除在有效样本统计之外。

逐条 p-value：`/shared/wwx/EasyGAD/wm_test/cleanD_dipperparaSFT_dipperparagad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.p_values.jsonl`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl`

固定 token 分组 p-value（普通中位数；p 越大表示原单侧检验证据越弱）：

按教师 tokenizer 编码回答并无分隔拼接，精确分组；每组首 token 仅作上下文，其余 token 用本项目原 KGW 绿表评分；不去重，尾部不足一组丢弃；各组 p 排序后取普通中位数（偶数组取中间两个 p 的算术平均）。

| 每组 token 数 | 计分 token 数 | KGW 组数 | KGW median p ↑ | clean 组数 | clean median p | KGW/clean 丢弃尾部 tokens |
|---:|---:|---:|---:|---:|---:|---:|
| 1000 | 999 | 99 | 0.659574 | 159 | 0.865929 | 488/765 |
| 2000 | 1999 | 49 | 0.85342 | 79 | 0.971358 | 1488/1765 |
| 3000 | 2999 | 33 | 0.761817 | 53 | 0.982134 | 488/765 |
| 10000 | 9999 | 9 | 0.999759 | 15 | 1 | 9488/9765 |
| 20000 | 19999 | 4 | 0.999981 | 7 | 1 | 19488/19765 |
| 30000 | 29999 | 3 | 1 | 5 | 1 | 9488/9765 |

N/A 表示总 token 数不足一个完整组；组数为 1 或 2 时需结合逐组结果解释。极小 p 用科学计数法字符串保存，同时保留 log10(p)，避免浮点下溢为 0。

逐组 p-value 缓存：`/shared/wwx/EasyGAD/wm_test/cleanD_dipperparaSFT_dipperparagad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.grouped_p_values.json`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.grouped_p_values.json`

剔除严重重复回答后的固定 token 分组 p-value（普通中位数）：

先独立筛选 KGW 和 clean：回答内部相邻 token 对重复比例严格大于 50% 时，剔除整条回答；prompt 不参与判断。保留回答按原顺序重新无分隔拼接，各组首 token 仅作上下文；组内不做 token 对去重，尾部不足一组丢弃。这是质量筛选补充指标，原始全样本统计另行保留。

| 数据 | 原回答数 | 剔除严重重复回答 | 保留回答数 | 原 tokens | 剔除 tokens | 保留 tokens |
|---|---:|---:|---:|---:|---:|---:|
| kgw | 500 | 48 (9.60%) | 452 | 99488 | 45342 | 54146 |
| clean | 500 | 88 (17.60%) | 412 | 159765 | 113883 | 45882 |

| 每组 token 数 | 计分 token 数 | KGW 组数 | KGW median p ↑ | clean 组数 | clean median p | KGW/clean 丢弃尾部 tokens |
|---:|---:|---:|---:|---:|---:|---:|
| 1000 | 999 | 54 | 0.449672 | 45 | 0.636089 | 146/882 |
| 2000 | 1999 | 27 | 0.437794 | 22 | 0.796038 | 146/1882 |
| 3000 | 2999 | 18 | 0.56527 | 15 | 0.738626 | 146/882 |
| 10000 | 9999 | 5 | 0.590959 | 4 | 0.947597 | 4146/5882 |
| 20000 | 19999 | 2 | 0.710325 | 2 | 0.978374 | 14146/5882 |
| 30000 | 29999 | 1 | 0.516119 | 1 | 0.999568 | 24146/15882 |

N/A 表示筛选后不足一个完整组。各组 p 取普通中位数，偶数组取中间两个 p 的算术平均；组数较少时请结合逐组缓存解释。

剔除严重重复回答后的逐组 p-value 缓存：`/shared/wwx/EasyGAD/wm_test/cleanD_dipperparaSFT_dipperparagad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.nonrepetitive_grouped_p_values.json`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.nonrepetitive_grouped_p_values.json`

### 固定参考模型 PPL（只评分已保存的回答）

| 文件组 | 总体 PPL ↓ | 逐回答 PPL 中位数 ↓ | 剔除严重重复后总体 PPL ↓ | 保留回答数/原回答数 | 有效样本/总样本 | 状态 | 缓存复用 |
|---|---:|---:|---:|---:|---:|---|---|
| kgw | 2.633080 | 4.497939 | 4.787485 | 452/500 | 500/500 | ok | False |
| clean | 1.535880 | 2.557640 | 2.702170 | 412/500 | 500/500 | ok | True |

总体 PPL = exp(全部有效回答 NLL 总和 / 全部计分回答 token 数)，不是逐条 PPL 的算术平均。
逐回答 PPL 中位数对全量有效回答的 PPL 排序；偶数条取中间两个 PPL 的算术平均，不对平均 NLL 取中位数后再 exp。空回答或异常 loss 不计入，并单独报告数量。
剔除严重重复后总体 PPL：复用同源重复筛选缓存，按教师 tokenizer 的回答内部相邻 token 对重复率严格 > 50% 剔除整条回答，prompt 不参与判断；只汇总保留回答原有的参考模型 NLL 和参考 tokenizer token 数。保留回答的文本不变，不删除文内 token，不丢弃尾部。KGW 与 clean 各自筛选，保留回答数含未成功评分回答。N/A 表示未提供筛选，null 表示无可计算数值；筛选后结果是子集统计，全量结果另行保留。
原生成 tokenizer 恢复实际生成 prompt；参考 tokenizer 对 prompt/answer 分开编码后拼接；只计回答，包含首回答 token。Base 参考模型不再套用 chat template；只添加一次参考 BOS，不额外评分 EOS；输入 JSONL 不修改。

- kgw: `/shared/wwx/EasyGAD/wm_test/cleanD_dipperparaSFT_dipperparagad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl`；SHA256 `3d35e43ee786d40ea166608bbea1bab245425c775b54ae5212007fe879431738`；逐条明细 `/shared/wwx/EasyGAD/wm_test/cleanD_dipperparaSFT_dipperparagad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.ppl.030e75ac8bae5041811a.jsonl`；空回答 0；异常 loss 0；原生成截断 3；参考上下文截断 0；计分回答 tokens 95869；平均回答 tokens 191.74；中位数样本数 500（状态 ok）。
  剔除严重重复回答 48（9.60%）；保留回答中有效评分 452/452；保留回答计分 tokens 53539；状态 ok；重复筛选缓存 `/shared/wwx/EasyGAD/wm_test/cleanD_dipperparaSFT_dipperparagad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.nonrepetitive_grouped_p_values.json`。

  生成文本配置（种子逐条保存在明细中）：

```json
{
  "student_model_paths": [
    "/shared/wwx/EasyGAD/checkpoints/kgwD_paraSFT_paraGAD_v1/warmup/global_step_1813/actor/huggingface"
  ],
  "generation_tokenizer_paths": [
    "/shared/public_models/Qwen2.5-0.5B"
  ],
  "generation_configurations": [
    {
      "configuration": {
        "temperature": 0.7,
        "top_p": 0.9,
        "max_new_tokens": 1536,
        "max_prompt_tokens": 2048,
        "kgw_enabled_during_generation": false
      },
      "samples": 500
    }
  ],
  "generation_seeds": {
    "recorded_samples": 500,
    "minimum": 42,
    "maximum": 541,
    "individual_values": "see per-sample immutable records"
  }
}
```
- clean: `/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl`；SHA256 `597b843d28d31c353c7bb9b94a3b6dccb564cb45ac2c5252f6a1592ccd768efe`；逐条明细 `/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.ppl.877fc574f9ee35a5145f.jsonl`；空回答 0；异常 loss 0；原生成截断 3；参考上下文截断 0；计分回答 tokens 156267；平均回答 tokens 312.53；中位数样本数 500（状态 ok）。
  剔除严重重复回答 88（17.60%）；保留回答中有效评分 412/412；保留回答计分 tokens 45137；状态 ok；重复筛选缓存 `/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.nonrepetitive_grouped_p_values.json`。

  生成文本配置（种子逐条保存在明细中）：

```json
{
  "student_model_paths": [
    "/shared/public_models/Qwen2.5-0.5B"
  ],
  "generation_tokenizer_paths": [
    "/shared/public_models/Qwen2.5-0.5B"
  ],
  "generation_configurations": [
    {
      "configuration": {
        "kgw_enabled_during_generation": false,
        "max_new_tokens": 1536,
        "max_prompt_tokens": 2048,
        "temperature": 0.7,
        "top_p": 0.9
      },
      "samples": 500
    }
  ],
  "generation_seeds": {
    "recorded_samples": 500,
    "minimum": 42,
    "maximum": 541,
    "individual_values": "see per-sample immutable records"
  }
}
```

完整评分配置（含模型/tokenizer 指纹、软件版本；权重使用 size/mtime 标识，不全量哈希）：

```json
{
  "model_path": "/shared/public_models/Llama-3-8B",
  "device": "cuda",
  "dtype": "bfloat16",
  "generation_tokenizer": "/shared/public_models/Qwen2.5-0.5B",
  "max_length": null,
  "overflow": "error",
  "effective_max_length": 8192,
  "protocol": {
    "prompt": "source-generation-prompt; source chat template, not reference chat template",
    "boundary": "encode prompt and answer separately with add_special_tokens=False, then concatenate",
    "bos": "one reference BOS at start when defined; no extra EOS",
    "loss": "causal next-token NLL on all answer tokens, including the first; no prompt or padding loss",
    "aggregate": "exp(sum(answer NLL) / sum(scored answer tokens)); not mean per-answer PPL",
    "source_tokenizer_selection": "explicit override, otherwise row.model_path; fallback assumes the generation tokenizer matches that checkpoint",
    "legacy_prompt_limit": 2048,
    "weights_fingerprint": "weight filenames, sizes and mtime_ns; weight contents are not hashed"
  },
  "reference_assets": {
    "path": "/shared/public_models/Llama-3-8B",
    "assets": [
      {
        "name": "config.json",
        "size": 654,
        "sha256": "2430cee764b6530ff8673cf9ba8561e1d5a33152d503cd0de909ff5718261441"
      },
      {
        "name": "generation_config.json",
        "size": 126,
        "sha256": "55550e95c40c53fb0ee3f960d6d2b25a46405c8f790e5c4bb02caf3e98f2b5d0"
      },
      {
        "name": "model.safetensors.index.json",
        "size": 23950,
        "sha256": "146776fce3f6db1103aa6f249e65ee5544c5923ce6f971b092eee79aa6e5d37b"
      },
      {
        "name": "special_tokens_map.json",
        "size": 73,
        "sha256": "462d91939dbc37178aa5a3eae7068d1990ccc92e09f288cc71f42cdf139d69cc"
      },
      {
        "name": "tokenizer.json",
        "size": 9085698,
        "sha256": "e134af98b985517b4f068e3755ae90d4e9cd2d45d328325dc503f1c6b2d06cc7"
      },
      {
        "name": "tokenizer_config.json",
        "size": 50566,
        "sha256": "690727b4fed286383df1c7ca5e805124cb70c6eb4529f807c7b2e60ff741da7e"
      }
    ],
    "weight_stats": [
      {
        "name": "model-00001-of-00004.safetensors",
        "size": 4976698672,
        "mtime_ns": 1736746522477644778
      },
      {
        "name": "model-00002-of-00004.safetensors",
        "size": 4999802720,
        "mtime_ns": 1736746656058650226
      },
      {
        "name": "model-00003-of-00004.safetensors",
        "size": 4915916176,
        "mtime_ns": 1736746768408654808
      },
      {
        "name": "model-00004-of-00004.safetensors",
        "size": 1168138808,
        "mtime_ns": 1736746796088655937
      }
    ],
    "weight_content_hashed": false
  },
  "software": {
    "python": "3.10.21",
    "torch": "2.6.0",
    "transformers": "4.51.3",
    "tokenizers": "0.21.4"
  }
}
```

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.5350000000000004,
  "best_f1": {
    "threshold": -5.613413993878117,
    "fpr": 0.946,
    "tpr": 0.982,
    "precision": 0.5093360995850622,
    "f1": 0.6707650273224043,
    "tp": 491,
    "fp": 473,
    "tn": 27,
    "fn": 9
  },
  "tpr_at_fpr": {
    "1%": {
      "threshold": 12.40054182283984,
      "fpr": 0.01,
      "tpr": 0.006,
      "precision": 0.375,
      "f1": 0.011811023622047246,
      "tp": 3,
      "fp": 5,
      "tn": 495,
      "fn": 497,
      "target_fpr": 0.01
    },
    "5%": {
      "threshold": 2.263009527424072,
      "fpr": 0.046,
      "tpr": 0.072,
      "precision": 0.6101694915254238,
      "f1": 0.12880143112701253,
      "tp": 36,
      "fp": 23,
      "tn": 477,
      "fn": 464,
      "target_fpr": 0.05
    },
    "10%": {
      "threshold": 1.6903085094570331,
      "fpr": 0.1,
      "tpr": 0.112,
      "precision": 0.5283018867924528,
      "f1": 0.18481848184818483,
      "tp": 56,
      "fp": 50,
      "tn": 450,
      "fn": 444,
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
      "clean": 2.0
    }
  },
  "rouge_l_dolly": {
    "mean": 0.1974983910661132,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/cleanD_dipperparaSFT_dipperparagad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl",
    "reference_file": "/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl",
    "reference_source": "databricks/databricks-dolly-15k:response",
    "metric": "rougeL",
    "measure": "fmeasure",
    "use_stemmer": true,
    "aggregation": "unweighted mean of per-sample ROUGE-L F1"
  },
  "rouge_l_teacher_clean": {
    "mean": 0.24897537195744776,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/cleanD_dipperparaSFT_dipperparagad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl",
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
        "mean": 0.49825071141627064,
        "median": 0.46888006004173544,
        "min": 4.2296e-319,
        "max": 1.0,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 34,
            "fraction": 0.068
          },
          "5%": {
            "alpha": 0.05,
            "count": 56,
            "fraction": 0.112
          },
          "10%": {
            "alpha": 0.1,
            "count": 81,
            "fraction": 0.162
          }
        }
      },
      "deduplicated": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.5209833934905409,
        "median": 0.5419918379770678,
        "min": 0.001241973233842605,
        "max": 0.9989889754015482,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 10,
            "fraction": 0.02
          },
          "5%": {
            "alpha": 0.05,
            "count": 35,
            "fraction": 0.07
          },
          "10%": {
            "alpha": 0.1,
            "count": 52,
            "fraction": 0.104
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
    "kgw": "/shared/wwx/EasyGAD/wm_test/cleanD_dipperparaSFT_dipperparagad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.p_values.jsonl",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl"
  },
  "grouped_p_values": {
    "kgw": {
      "aggregation": "ordinary_median",
      "num_answers": 500,
      "total_answer_tokens": 99488,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 99,
          "total_answer_tokens": 99488,
          "discarded_tail_tokens": 488,
          "median_p_value": 0.6595743743853253,
          "median_log10_p_value": -0.1807362257977395,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 49,
          "total_answer_tokens": 99488,
          "discarded_tail_tokens": 1488,
          "median_p_value": 0.853420023132693,
          "median_log10_p_value": -0.06883717184227363,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 33,
          "total_answer_tokens": 99488,
          "discarded_tail_tokens": 488,
          "median_p_value": 0.7618165377103661,
          "median_log10_p_value": -0.11814960379584206,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 9,
          "total_answer_tokens": 99488,
          "discarded_tail_tokens": 9488,
          "median_p_value": 0.9997586473897683,
          "median_log10_p_value": -0.00010483075791404954,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 4,
          "total_answer_tokens": 99488,
          "discarded_tail_tokens": 19488,
          "median_p_value": 0.999980691578046,
          "median_log10_p_value": -8.385622065740633e-06,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 3,
          "total_answer_tokens": 99488,
          "discarded_tail_tokens": 9488,
          "median_p_value": 0.9999999999989408,
          "median_log10_p_value": -4.599842015461615e-13,
          "status": "ok"
        }
      }
    },
    "clean": {
      "aggregation": "ordinary_median",
      "num_answers": 500,
      "total_answer_tokens": 159765,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 159,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 765,
          "median_p_value": 0.8659288977499955,
          "median_log10_p_value": -0.06251776685396769,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 79,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 1765,
          "median_p_value": 0.971357711016285,
          "median_log10_p_value": -0.012620807875598238,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 53,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 765,
          "median_p_value": 0.9821335190767914,
          "median_log10_p_value": -0.007829466737979084,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 15,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 9765,
          "median_p_value": 0.9999999999999984,
          "median_log10_p_value": -6.750292265873014e-16,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 7,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 19765,
          "median_p_value": 1.0,
          "median_log10_p_value": 0.0,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 5,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 9765,
          "median_p_value": 1.0,
          "median_log10_p_value": 0.0,
          "status": "ok"
        }
      }
    }
  },
  "grouped_p_value_method": "teacher-tokenizer answer IDs concatenated without separators; exact disjoint blocks; first token of each block is context only; no repetition deduplication; incomplete tail discarded; ordinary median of block p-values (arithmetic mean of the two middle p-values for even group counts)",
  "per_group_p_value_files": {
    "kgw": "/shared/wwx/EasyGAD/wm_test/cleanD_dipperparaSFT_dipperparagad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.grouped_p_values.json",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.grouped_p_values.json"
  },
  "grouped_p_values_without_severe_repetition": {
    "kgw": {
      "aggregation": "ordinary_median",
      "num_answers": 452,
      "total_answer_tokens": 54146,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 54,
          "total_answer_tokens": 54146,
          "discarded_tail_tokens": 146,
          "median_p_value": 0.44967160674560175,
          "median_log10_p_value": -0.34710453387525253,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 27,
          "total_answer_tokens": 54146,
          "discarded_tail_tokens": 146,
          "median_p_value": 0.437794275922607,
          "median_log10_p_value": -0.3587299210492138,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 18,
          "total_answer_tokens": 54146,
          "discarded_tail_tokens": 146,
          "median_p_value": 0.5652698902835346,
          "median_log10_p_value": -0.24774414709246043,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 5,
          "total_answer_tokens": 54146,
          "discarded_tail_tokens": 4146,
          "median_p_value": 0.5909585835499608,
          "median_log10_p_value": -0.22844295493260433,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 2,
          "total_answer_tokens": 54146,
          "discarded_tail_tokens": 14146,
          "median_p_value": 0.7103247155407992,
          "median_log10_p_value": -0.1485430739155219,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 1,
          "total_answer_tokens": 54146,
          "discarded_tail_tokens": 24146,
          "median_p_value": 0.5161189408334832,
          "median_log10_p_value": -0.2872502026457561,
          "status": "ok"
        }
      },
      "filtering": {
        "repetition_threshold": 0.5,
        "comparison": ">",
        "scope": "answer-internal adjacent token pairs; prompt excluded",
        "num_answers_before": 500,
        "num_answers_retained": 452,
        "num_answers_removed": 48,
        "fraction_answers_removed": 0.096,
        "total_answer_tokens_before": 99488,
        "total_answer_tokens_retained": 54146,
        "total_answer_tokens_removed": 45342,
        "removed_answer_ids": [
          "dolly-00423",
          "dolly-05185",
          "dolly-01998",
          "dolly-01089",
          "dolly-08884",
          "dolly-00303",
          "dolly-00275",
          "dolly-08391",
          "dolly-10398",
          "dolly-14859",
          "dolly-04421",
          "dolly-05394",
          "dolly-07027",
          "dolly-04949",
          "dolly-08689",
          "dolly-08574",
          "dolly-00143",
          "dolly-04856",
          "dolly-05555",
          "dolly-08625",
          "dolly-01386",
          "dolly-02128",
          "dolly-01028",
          "dolly-09228",
          "dolly-12027",
          "dolly-07117",
          "dolly-10898",
          "dolly-11987",
          "dolly-03726",
          "dolly-04773",
          "dolly-01979",
          "dolly-02725",
          "dolly-14265",
          "dolly-09609",
          "dolly-12916",
          "dolly-02451",
          "dolly-06824",
          "dolly-06932",
          "dolly-14235",
          "dolly-11386",
          "dolly-08451",
          "dolly-09420",
          "dolly-03624",
          "dolly-09039",
          "dolly-00182",
          "dolly-06562",
          "dolly-03113",
          "dolly-01356"
        ]
      }
    },
    "clean": {
      "aggregation": "ordinary_median",
      "num_answers": 412,
      "total_answer_tokens": 45882,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 45,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 882,
          "median_p_value": 0.6360891449864364,
          "median_log10_p_value": -0.1964820156995508,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 22,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 1882,
          "median_p_value": 0.7960378878131416,
          "median_log10_p_value": -0.09906626131183685,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 15,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 882,
          "median_p_value": 0.7386263221105359,
          "median_log10_p_value": -0.13157521964243946,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 4,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 5882,
          "median_p_value": 0.947596846602552,
          "median_log10_p_value": -0.0233763931850151,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 2,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 5882,
          "median_p_value": 0.9783739864832501,
          "median_log10_p_value": -0.009495103065976066,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 1,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 15882,
          "median_p_value": 0.9995678964162934,
          "median_log10_p_value": -0.00018770075802065225,
          "status": "ok"
        }
      },
      "filtering": {
        "repetition_threshold": 0.5,
        "comparison": ">",
        "scope": "answer-internal adjacent token pairs; prompt excluded",
        "num_answers_before": 500,
        "num_answers_retained": 412,
        "num_answers_removed": 88,
        "fraction_answers_removed": 0.176,
        "total_answer_tokens_before": 159765,
        "total_answer_tokens_retained": 45882,
        "total_answer_tokens_removed": 113883,
        "removed_answer_ids": [
          "dolly-00135",
          "dolly-12241",
          "dolly-07923",
          "dolly-07103",
          "dolly-05608",
          "dolly-07788",
          "dolly-11310",
          "dolly-02097",
          "dolly-03614",
          "dolly-13505",
          "dolly-02580",
          "dolly-08884",
          "dolly-12659",
          "dolly-00420",
          "dolly-11014",
          "dolly-08008",
          "dolly-02186",
          "dolly-00275",
          "dolly-08512",
          "dolly-14060",
          "dolly-01461",
          "dolly-02223",
          "dolly-04949",
          "dolly-08689",
          "dolly-08574",
          "dolly-08406",
          "dolly-04141",
          "dolly-03209",
          "dolly-06227",
          "dolly-11078",
          "dolly-09778",
          "dolly-04856",
          "dolly-13779",
          "dolly-06595",
          "dolly-08936",
          "dolly-09344",
          "dolly-05605",
          "dolly-08340",
          "dolly-04589",
          "dolly-04686",
          "dolly-14700",
          "dolly-03696",
          "dolly-03914",
          "dolly-11987",
          "dolly-01939",
          "dolly-05628",
          "dolly-13339",
          "dolly-08911",
          "dolly-03239",
          "dolly-13445",
          "dolly-02139",
          "dolly-14265",
          "dolly-13610",
          "dolly-07427",
          "dolly-09563",
          "dolly-02451",
          "dolly-13544",
          "dolly-06824",
          "dolly-05312",
          "dolly-10992",
          "dolly-06932",
          "dolly-08607",
          "dolly-05388",
          "dolly-11386",
          "dolly-02069",
          "dolly-09439",
          "dolly-00148",
          "dolly-08211",
          "dolly-12186",
          "dolly-03319",
          "dolly-07407",
          "dolly-10389",
          "dolly-03916",
          "dolly-08222",
          "dolly-14947",
          "dolly-03624",
          "dolly-09330",
          "dolly-11182",
          "dolly-02059",
          "dolly-02916",
          "dolly-09816",
          "dolly-05355",
          "dolly-06970",
          "dolly-05634",
          "dolly-02500",
          "dolly-11314",
          "dolly-13235",
          "dolly-04223"
        ]
      }
    }
  },
  "grouped_p_value_without_severe_repetition_method": "exclude whole answers whose answer-internal adjacent-token-pair repetition ratio (1 - unique pairs / all pairs) is strictly greater than 0.5; prompts excluded from repetition assessment; filter each label independently; retain original answer order, then concatenate teacher-tokenizer answer IDs without separators; exact disjoint blocks, first token context only; no token-pair deduplication within retained blocks; incomplete tail discarded; ordinary median of block p-values (mean of the middle two for even counts)",
  "per_group_p_value_without_severe_repetition_files": {
    "kgw": "/shared/wwx/EasyGAD/wm_test/cleanD_dipperparaSFT_dipperparagad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.nonrepetitive_grouped_p_values.json",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.nonrepetitive_grouped_p_values.json"
  },
  "ppl": {
    "enabled": true,
    "schema": "saved-answer-reference-ppl-v1",
    "configuration": {
      "model_path": "/shared/public_models/Llama-3-8B",
      "device": "cuda",
      "dtype": "bfloat16",
      "generation_tokenizer": "/shared/public_models/Qwen2.5-0.5B",
      "max_length": null,
      "overflow": "error",
      "effective_max_length": 8192,
      "protocol": {
        "prompt": "source-generation-prompt; source chat template, not reference chat template",
        "boundary": "encode prompt and answer separately with add_special_tokens=False, then concatenate",
        "bos": "one reference BOS at start when defined; no extra EOS",
        "loss": "causal next-token NLL on all answer tokens, including the first; no prompt or padding loss",
        "aggregate": "exp(sum(answer NLL) / sum(scored answer tokens)); not mean per-answer PPL",
        "source_tokenizer_selection": "explicit override, otherwise row.model_path; fallback assumes the generation tokenizer matches that checkpoint",
        "legacy_prompt_limit": 2048,
        "weights_fingerprint": "weight filenames, sizes and mtime_ns; weight contents are not hashed"
      },
      "reference_assets": {
        "path": "/shared/public_models/Llama-3-8B",
        "assets": [
          {
            "name": "config.json",
            "size": 654,
            "sha256": "2430cee764b6530ff8673cf9ba8561e1d5a33152d503cd0de909ff5718261441"
          },
          {
            "name": "generation_config.json",
            "size": 126,
            "sha256": "55550e95c40c53fb0ee3f960d6d2b25a46405c8f790e5c4bb02caf3e98f2b5d0"
          },
          {
            "name": "model.safetensors.index.json",
            "size": 23950,
            "sha256": "146776fce3f6db1103aa6f249e65ee5544c5923ce6f971b092eee79aa6e5d37b"
          },
          {
            "name": "special_tokens_map.json",
            "size": 73,
            "sha256": "462d91939dbc37178aa5a3eae7068d1990ccc92e09f288cc71f42cdf139d69cc"
          },
          {
            "name": "tokenizer.json",
            "size": 9085698,
            "sha256": "e134af98b985517b4f068e3755ae90d4e9cd2d45d328325dc503f1c6b2d06cc7"
          },
          {
            "name": "tokenizer_config.json",
            "size": 50566,
            "sha256": "690727b4fed286383df1c7ca5e805124cb70c6eb4529f807c7b2e60ff741da7e"
          }
        ],
        "weight_stats": [
          {
            "name": "model-00001-of-00004.safetensors",
            "size": 4976698672,
            "mtime_ns": 1736746522477644778
          },
          {
            "name": "model-00002-of-00004.safetensors",
            "size": 4999802720,
            "mtime_ns": 1736746656058650226
          },
          {
            "name": "model-00003-of-00004.safetensors",
            "size": 4915916176,
            "mtime_ns": 1736746768408654808
          },
          {
            "name": "model-00004-of-00004.safetensors",
            "size": 1168138808,
            "mtime_ns": 1736746796088655937
          }
        ],
        "weight_content_hashed": false
      },
      "software": {
        "python": "3.10.21",
        "torch": "2.6.0",
        "transformers": "4.51.3",
        "tokenizers": "0.21.4"
      }
    },
    "files": {
      "kgw": {
        "samples": 500,
        "valid_samples": 500,
        "skipped_empty_answers": 0,
        "complete": true,
        "nonfinite_samples": 0,
        "status": "ok",
        "total_nll": 92815.9778377926,
        "scored_tokens": 95869,
        "mean_nll": 0.9681542296028184,
        "token_weighted_ppl": 2.6330799103630023,
        "mean_answer_tokens": 191.738,
        "source_prompt_truncated_samples": 3,
        "reference_prompt_truncated_samples": 0,
        "generation_configurations": [
          {
            "configuration": {
              "temperature": 0.7,
              "top_p": 0.9,
              "max_new_tokens": 1536,
              "max_prompt_tokens": 2048,
              "kgw_enabled_during_generation": false
            },
            "samples": 500
          }
        ],
        "generation_seeds": {
          "recorded_samples": 500,
          "minimum": 42,
          "maximum": 541,
          "individual_values": "see per-sample immutable records"
        },
        "student_model_paths": [
          "/shared/wwx/EasyGAD/checkpoints/kgwD_paraSFT_paraGAD_v1/warmup/global_step_1813/actor/huggingface"
        ],
        "generation_tokenizer_paths": [
          "/shared/public_models/Qwen2.5-0.5B"
        ],
        "median_per_answer_ppl": 4.497938726023064,
        "median_samples": 500,
        "median_status": "ok",
        "without_severe_repetition": {
          "samples": 452,
          "valid_samples": 452,
          "skipped_empty_answers": 0,
          "complete": true,
          "nonfinite_samples": 0,
          "status": "ok",
          "total_nll": 83842.34942483902,
          "scored_tokens": 53539,
          "mean_nll": 1.566005144377725,
          "token_weighted_ppl": 4.787484631531891,
          "mean_answer_tokens": 118.44911504424779,
          "source_prompt_truncated_samples": 3,
          "reference_prompt_truncated_samples": 0,
          "generation_configurations": [
            {
              "configuration": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_new_tokens": 1536,
                "max_prompt_tokens": 2048,
                "kgw_enabled_during_generation": false
              },
              "samples": 452
            }
          ],
          "generation_seeds": {
            "recorded_samples": 452,
            "minimum": 42,
            "maximum": 541,
            "individual_values": "see per-sample immutable records"
          },
          "student_model_paths": [
            "/shared/wwx/EasyGAD/checkpoints/kgwD_paraSFT_paraGAD_v1/warmup/global_step_1813/actor/huggingface"
          ],
          "generation_tokenizer_paths": [
            "/shared/public_models/Qwen2.5-0.5B"
          ],
          "median_per_answer_ppl": 4.779041918758374,
          "median_samples": 452,
          "median_status": "ok",
          "num_answers_before": 500,
          "num_answers_retained": 452,
          "num_answers_removed": 48,
          "fraction_answers_removed": 0.096,
          "repetition_threshold": 0.5,
          "comparison": ">",
          "scope": "answer-internal adjacent token pairs; prompt excluded",
          "removed_answer_ids": [
            "dolly-00423",
            "dolly-05185",
            "dolly-01998",
            "dolly-01089",
            "dolly-08884",
            "dolly-00303",
            "dolly-00275",
            "dolly-08391",
            "dolly-10398",
            "dolly-14859",
            "dolly-04421",
            "dolly-05394",
            "dolly-07027",
            "dolly-04949",
            "dolly-08689",
            "dolly-08574",
            "dolly-00143",
            "dolly-04856",
            "dolly-05555",
            "dolly-08625",
            "dolly-01386",
            "dolly-02128",
            "dolly-01028",
            "dolly-09228",
            "dolly-12027",
            "dolly-07117",
            "dolly-10898",
            "dolly-11987",
            "dolly-03726",
            "dolly-04773",
            "dolly-01979",
            "dolly-02725",
            "dolly-14265",
            "dolly-09609",
            "dolly-12916",
            "dolly-02451",
            "dolly-06824",
            "dolly-06932",
            "dolly-14235",
            "dolly-11386",
            "dolly-08451",
            "dolly-09420",
            "dolly-03624",
            "dolly-09039",
            "dolly-00182",
            "dolly-06562",
            "dolly-03113",
            "dolly-01356"
          ],
          "filtering_source_file": "/shared/wwx/EasyGAD/wm_test/cleanD_dipperparaSFT_dipperparagad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.nonrepetitive_grouped_p_values.json",
          "filtering_source_sha256": "3d35e43ee786d40ea166608bbea1bab245425c775b54ae5212007fe879431738",
          "filtering_tokenizer": {
            "path": "/shared/public_models/Qwen2.5-14B-Instruct",
            "files_sha256": {
              "config.json": "7362de7db90a1e57fe153e55094e6c2fb7d904a3705d34296ff7de84488235f4",
              "merges.txt": "0de0bc38a29ea38eef099b677fa1ff52edd181e573529af26c4cd2136e233777",
              "tokenizer.json": "47ec9be242d3ef39b9c97ac0a3f06c1752f061b234e295bc0a2842067a3fe4f9",
              "tokenizer_config.json": "fa2a40a9d8c8c4bb7f25ab726eb78ec9cbaaef96d1fa26f1d7f5615e886449a8",
              "vocab.json": "ca10d7e9fb3ed18575dd1e277a2579c16d108e32f27439684afa0e10b1440910"
            }
          }
        },
        "source_path": "/shared/wwx/EasyGAD/wm_test/cleanD_dipperparaSFT_dipperparagad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl",
        "source_sha256": "3d35e43ee786d40ea166608bbea1bab245425c775b54ae5212007fe879431738",
        "per_sample_file": "/shared/wwx/EasyGAD/wm_test/cleanD_dipperparaSFT_dipperparagad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.ppl.030e75ac8bae5041811a.jsonl",
        "cache_reused": false
      },
      "clean": {
        "samples": 500,
        "valid_samples": 500,
        "skipped_empty_answers": 0,
        "complete": true,
        "nonfinite_samples": 0,
        "status": "ok",
        "total_nll": 67054.72902449768,
        "scored_tokens": 156267,
        "mean_nll": 0.42910357928735865,
        "token_weighted_ppl": 1.5358801115260794,
        "mean_answer_tokens": 312.534,
        "source_prompt_truncated_samples": 3,
        "reference_prompt_truncated_samples": 0,
        "generation_configurations": [
          {
            "configuration": {
              "kgw_enabled_during_generation": false,
              "max_new_tokens": 1536,
              "max_prompt_tokens": 2048,
              "temperature": 0.7,
              "top_p": 0.9
            },
            "samples": 500
          }
        ],
        "generation_seeds": {
          "recorded_samples": 500,
          "minimum": 42,
          "maximum": 541,
          "individual_values": "see per-sample immutable records"
        },
        "student_model_paths": [
          "/shared/public_models/Qwen2.5-0.5B"
        ],
        "generation_tokenizer_paths": [
          "/shared/public_models/Qwen2.5-0.5B"
        ],
        "median_per_answer_ppl": 2.5576398946471928,
        "median_samples": 500,
        "median_status": "ok",
        "without_severe_repetition": {
          "samples": 412,
          "valid_samples": 412,
          "skipped_empty_answers": 0,
          "complete": true,
          "nonfinite_samples": 0,
          "status": "ok",
          "total_nll": 44868.67048177123,
          "scored_tokens": 45137,
          "mean_nll": 0.9940552203684612,
          "token_weighted_ppl": 2.702170179562856,
          "mean_answer_tokens": 109.55582524271844,
          "source_prompt_truncated_samples": 1,
          "reference_prompt_truncated_samples": 0,
          "generation_configurations": [
            {
              "configuration": {
                "kgw_enabled_during_generation": false,
                "max_new_tokens": 1536,
                "max_prompt_tokens": 2048,
                "temperature": 0.7,
                "top_p": 0.9
              },
              "samples": 412
            }
          ],
          "generation_seeds": {
            "recorded_samples": 412,
            "minimum": 42,
            "maximum": 541,
            "individual_values": "see per-sample immutable records"
          },
          "student_model_paths": [
            "/shared/public_models/Qwen2.5-0.5B"
          ],
          "generation_tokenizer_paths": [
            "/shared/public_models/Qwen2.5-0.5B"
          ],
          "median_per_answer_ppl": 2.8522532998790773,
          "median_samples": 412,
          "median_status": "ok",
          "num_answers_before": 500,
          "num_answers_retained": 412,
          "num_answers_removed": 88,
          "fraction_answers_removed": 0.176,
          "repetition_threshold": 0.5,
          "comparison": ">",
          "scope": "answer-internal adjacent token pairs; prompt excluded",
          "removed_answer_ids": [
            "dolly-00135",
            "dolly-12241",
            "dolly-07923",
            "dolly-07103",
            "dolly-05608",
            "dolly-07788",
            "dolly-11310",
            "dolly-02097",
            "dolly-03614",
            "dolly-13505",
            "dolly-02580",
            "dolly-08884",
            "dolly-12659",
            "dolly-00420",
            "dolly-11014",
            "dolly-08008",
            "dolly-02186",
            "dolly-00275",
            "dolly-08512",
            "dolly-14060",
            "dolly-01461",
            "dolly-02223",
            "dolly-04949",
            "dolly-08689",
            "dolly-08574",
            "dolly-08406",
            "dolly-04141",
            "dolly-03209",
            "dolly-06227",
            "dolly-11078",
            "dolly-09778",
            "dolly-04856",
            "dolly-13779",
            "dolly-06595",
            "dolly-08936",
            "dolly-09344",
            "dolly-05605",
            "dolly-08340",
            "dolly-04589",
            "dolly-04686",
            "dolly-14700",
            "dolly-03696",
            "dolly-03914",
            "dolly-11987",
            "dolly-01939",
            "dolly-05628",
            "dolly-13339",
            "dolly-08911",
            "dolly-03239",
            "dolly-13445",
            "dolly-02139",
            "dolly-14265",
            "dolly-13610",
            "dolly-07427",
            "dolly-09563",
            "dolly-02451",
            "dolly-13544",
            "dolly-06824",
            "dolly-05312",
            "dolly-10992",
            "dolly-06932",
            "dolly-08607",
            "dolly-05388",
            "dolly-11386",
            "dolly-02069",
            "dolly-09439",
            "dolly-00148",
            "dolly-08211",
            "dolly-12186",
            "dolly-03319",
            "dolly-07407",
            "dolly-10389",
            "dolly-03916",
            "dolly-08222",
            "dolly-14947",
            "dolly-03624",
            "dolly-09330",
            "dolly-11182",
            "dolly-02059",
            "dolly-02916",
            "dolly-09816",
            "dolly-05355",
            "dolly-06970",
            "dolly-05634",
            "dolly-02500",
            "dolly-11314",
            "dolly-13235",
            "dolly-04223"
          ],
          "filtering_source_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.nonrepetitive_grouped_p_values.json",
          "filtering_source_sha256": "597b843d28d31c353c7bb9b94a3b6dccb564cb45ac2c5252f6a1592ccd768efe",
          "filtering_tokenizer": {
            "path": "/shared/public_models/Qwen2.5-14B-Instruct",
            "files_sha256": {
              "config.json": "7362de7db90a1e57fe153e55094e6c2fb7d904a3705d34296ff7de84488235f4",
              "merges.txt": "0de0bc38a29ea38eef099b677fa1ff52edd181e573529af26c4cd2136e233777",
              "tokenizer.json": "47ec9be242d3ef39b9c97ac0a3f06c1752f061b234e295bc0a2842067a3fe4f9",
              "tokenizer_config.json": "fa2a40a9d8c8c4bb7f25ab726eb78ec9cbaaef96d1fa26f1d7f5615e886449a8",
              "vocab.json": "ca10d7e9fb3ed18575dd1e277a2579c16d108e32f27439684afa0e10b1440910"
            }
          }
        },
        "source_path": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl",
        "source_sha256": "597b843d28d31c353c7bb9b94a3b6dccb564cb45ac2c5252f6a1592ccd768efe",
        "per_sample_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.ppl.877fc574f9ee35a5145f.jsonl",
        "cache_reused": true
      }
    }
  },
  "evaluated_at": "2026-10-29T16:50:13+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wm_test/cleanD_dipperparaSFT_dipperparagad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-10-29T16:58:32+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.552234
- 实际检测配置：`{"gamma": 0.5, "hash_key": 15485863, "seeding": "simple_1 (hash_key * previous_token_id)", "delta_by_label": {"kgw": 3.0, "clean": 2.0}}`
- ROUGE-L（同批 500 条原始 Dolly 回答作参考）：0.230625（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 原始 Dolly 参考文件：`/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl`
- ROUGE-L（同批 500 条 14B clean 教师回答作参考）：0.262990（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 14B clean 教师参考文件：`/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_clean_test.parquet`
- Best F1：0.675342（z 阈值 -4.086514987502555，TPR 0.986000，FPR 0.934000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.010000 | 0.024000 | 0.046422 | 10.97167280621632 |
  | 5% | 0.050000 | 0.062000 | 0.111511 | 2.227560395692044 |
  | 10% | 0.100000 | 0.100000 | 0.166667 | 1.7210709770537855 |

两种逐条文本 p-value 统计（单侧正态近似；不是 AUROC 的显著性检验）：

去重规则：相同的 `(previous_token_id, token_id)` 只计一次；不修改回答文本。

| 数据 | 检测方式 | 有效样本 | p 均值 | p 中位数 | p≤0.01 | p≤0.05 | p≤0.10 |
|---|---|---:|---:|---:|---:|---:|---:|
| kgw | 原始 | 499/500 | 0.478944 | 0.456813 | 26 (5.21%) | 52 (10.42%) | 87 (17.43%) |
| kgw | token 对去重 | 499/500 | 0.498162 | 0.5 | 8 (1.60%) | 23 (4.61%) | 50 (10.02%) |
| clean | 原始 | 500/500 | 0.538121 | 0.57157 | 22 (4.40%) | 54 (10.80%) | 73 (14.60%) |
| clean | token 对去重 | 500/500 | 0.537418 | 0.555154 | 5 (1.00%) | 25 (5.00%) | 46 (9.20%) |

KGW 的小 p 占比是该理论阈值下的检出率，clean 的小 p 占比是实测误报率。p≤0.05 不保证实际 FPR=5%；去重可改善重复带来的失真，但不保证完全校准。空回答不做显著性检验，p=null，并排除在有效样本统计之外。

逐条 p-value：`/shared/wwx/EasyGAD/wm_test/cleanD_dipperparaSFT_dipperparagad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.p_values.jsonl`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl`

固定 token 分组 p-value（普通中位数；p 越大表示原单侧检验证据越弱）：

按教师 tokenizer 编码回答并无分隔拼接，精确分组；每组首 token 仅作上下文，其余 token 用本项目原 KGW 绿表评分；不去重，尾部不足一组丢弃；各组 p 排序后取普通中位数（偶数组取中间两个 p 的算术平均）。

| 每组 token 数 | 计分 token 数 | KGW 组数 | KGW median p ↑ | clean 组数 | clean median p | KGW/clean 丢弃尾部 tokens |
|---:|---:|---:|---:|---:|---:|---:|
| 1000 | 999 | 78 | 0.352168 | 159 | 0.865929 | 954/765 |
| 2000 | 1999 | 39 | 0.127002 | 79 | 0.971358 | 954/1765 |
| 3000 | 2999 | 26 | 0.0118824 | 53 | 0.982134 | 954/765 |
| 10000 | 9999 | 7 | 2.70108e-73 | 15 | 1 | 8954/9765 |
| 20000 | 19999 | 3 | 8.06414e-73 | 7 | 1 | 18954/19765 |
| 30000 | 29999 | 2 | 1.29584e-113 | 5 | 1 | 18954/9765 |

N/A 表示总 token 数不足一个完整组；组数为 1 或 2 时需结合逐组结果解释。极小 p 用科学计数法字符串保存，同时保留 log10(p)，避免浮点下溢为 0。

逐组 p-value 缓存：`/shared/wwx/EasyGAD/wm_test/cleanD_dipperparaSFT_dipperparagad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.grouped_p_values.json`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.grouped_p_values.json`

剔除严重重复回答后的固定 token 分组 p-value（普通中位数）：

先独立筛选 KGW 和 clean：回答内部相邻 token 对重复比例严格大于 50% 时，剔除整条回答；prompt 不参与判断。保留回答按原顺序重新无分隔拼接，各组首 token 仅作上下文；组内不做 token 对去重，尾部不足一组丢弃。这是质量筛选补充指标，原始全样本统计另行保留。

| 数据 | 原回答数 | 剔除严重重复回答 | 保留回答数 | 原 tokens | 剔除 tokens | 保留 tokens |
|---|---:|---:|---:|---:|---:|---:|
| kgw | 500 | 28 (5.60%) | 472 | 78954 | 29029 | 49925 |
| clean | 500 | 88 (17.60%) | 412 | 159765 | 113883 | 45882 |

| 每组 token 数 | 计分 token 数 | KGW 组数 | KGW median p ↑ | clean 组数 | clean median p | KGW/clean 丢弃尾部 tokens |
|---:|---:|---:|---:|---:|---:|---:|
| 1000 | 999 | 49 | 0.562848 | 45 | 0.636089 | 925/882 |
| 2000 | 1999 | 24 | 0.544344 | 22 | 0.796038 | 1925/1882 |
| 3000 | 2999 | 16 | 0.668105 | 15 | 0.738626 | 1925/882 |
| 10000 | 9999 | 4 | 0.920699 | 4 | 0.947597 | 9925/5882 |
| 20000 | 19999 | 2 | 0.794234 | 2 | 0.978374 | 9925/5882 |
| 30000 | 29999 | 1 | 0.903038 | 1 | 0.999568 | 19925/15882 |

N/A 表示筛选后不足一个完整组。各组 p 取普通中位数，偶数组取中间两个 p 的算术平均；组数较少时请结合逐组缓存解释。

剔除严重重复回答后的逐组 p-value 缓存：`/shared/wwx/EasyGAD/wm_test/cleanD_dipperparaSFT_dipperparagad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.nonrepetitive_grouped_p_values.json`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.nonrepetitive_grouped_p_values.json`

### 固定参考模型 PPL（只评分已保存的回答）

| 文件组 | 总体 PPL ↓ | 逐回答 PPL 中位数 ↓ | 剔除严重重复后总体 PPL ↓ | 保留回答数/原回答数 | 有效样本/总样本 | 状态 | 缓存复用 |
|---|---:|---:|---:|---:|---:|---|---|
| kgw | 2.607720 | 3.872479 | 4.083214 | 472/500 | 499/500 | ok | False |
| clean | 1.535880 | 2.557640 | 2.702170 | 412/500 | 500/500 | ok | True |

总体 PPL = exp(全部有效回答 NLL 总和 / 全部计分回答 token 数)，不是逐条 PPL 的算术平均。
逐回答 PPL 中位数对全量有效回答的 PPL 排序；偶数条取中间两个 PPL 的算术平均，不对平均 NLL 取中位数后再 exp。空回答或异常 loss 不计入，并单独报告数量。
剔除严重重复后总体 PPL：复用同源重复筛选缓存，按教师 tokenizer 的回答内部相邻 token 对重复率严格 > 50% 剔除整条回答，prompt 不参与判断；只汇总保留回答原有的参考模型 NLL 和参考 tokenizer token 数。保留回答的文本不变，不删除文内 token，不丢弃尾部。KGW 与 clean 各自筛选，保留回答数含未成功评分回答。N/A 表示未提供筛选，null 表示无可计算数值；筛选后结果是子集统计，全量结果另行保留。
原生成 tokenizer 恢复实际生成 prompt；参考 tokenizer 对 prompt/answer 分开编码后拼接；只计回答，包含首回答 token。Base 参考模型不再套用 chat template；只添加一次参考 BOS，不额外评分 EOS；输入 JSONL 不修改。

- kgw: `/shared/wwx/EasyGAD/wm_test/cleanD_dipperparaSFT_dipperparagad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl`；SHA256 `b6a1c151b66159f7d008c57d2b3b29282beb7dd5d8c0df69cbf24b9432139f54`；逐条明细 `/shared/wwx/EasyGAD/wm_test/cleanD_dipperparaSFT_dipperparagad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.ppl.999b78b10a07062da961.jsonl`；空回答 1；异常 loss 0；原生成截断 3；参考上下文截断 0；计分回答 tokens 77168；平均回答 tokens 154.34；中位数样本数 499（状态 ok）。
  **kgw 的评测不完整：总体值只覆盖有效回答，不能作为全量样本 PPL。**
  剔除严重重复回答 28（5.60%）；保留回答中有效评分 471/472；保留回答计分 tokens 49184；状态 ok；重复筛选缓存 `/shared/wwx/EasyGAD/wm_test/cleanD_dipperparaSFT_dipperparagad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.nonrepetitive_grouped_p_values.json`。
  **kgw 的筛选后评测不完整：筛选后 PPL 仅覆盖成功评分的保留回答。**

  生成文本配置（种子逐条保存在明细中）：

```json
{
  "student_model_paths": [
    "/shared/wwx/EasyGAD/checkpoints/kgwD_paraSFT_paraGAD_v1/gad/global_step_1813/actor/huggingface"
  ],
  "generation_tokenizer_paths": [
    "/shared/public_models/Qwen2.5-0.5B"
  ],
  "generation_configurations": [
    {
      "configuration": {
        "temperature": 0.7,
        "top_p": 0.9,
        "max_new_tokens": 1536,
        "max_prompt_tokens": 2048,
        "kgw_enabled_during_generation": false
      },
      "samples": 500
    }
  ],
  "generation_seeds": {
    "recorded_samples": 500,
    "minimum": 42,
    "maximum": 541,
    "individual_values": "see per-sample immutable records"
  }
}
```
- clean: `/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl`；SHA256 `597b843d28d31c353c7bb9b94a3b6dccb564cb45ac2c5252f6a1592ccd768efe`；逐条明细 `/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.ppl.877fc574f9ee35a5145f.jsonl`；空回答 0；异常 loss 0；原生成截断 3；参考上下文截断 0；计分回答 tokens 156267；平均回答 tokens 312.53；中位数样本数 500（状态 ok）。
  剔除严重重复回答 88（17.60%）；保留回答中有效评分 412/412；保留回答计分 tokens 45137；状态 ok；重复筛选缓存 `/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.nonrepetitive_grouped_p_values.json`。

  生成文本配置（种子逐条保存在明细中）：

```json
{
  "student_model_paths": [
    "/shared/public_models/Qwen2.5-0.5B"
  ],
  "generation_tokenizer_paths": [
    "/shared/public_models/Qwen2.5-0.5B"
  ],
  "generation_configurations": [
    {
      "configuration": {
        "kgw_enabled_during_generation": false,
        "max_new_tokens": 1536,
        "max_prompt_tokens": 2048,
        "temperature": 0.7,
        "top_p": 0.9
      },
      "samples": 500
    }
  ],
  "generation_seeds": {
    "recorded_samples": 500,
    "minimum": 42,
    "maximum": 541,
    "individual_values": "see per-sample immutable records"
  }
}
```

完整评分配置（含模型/tokenizer 指纹、软件版本；权重使用 size/mtime 标识，不全量哈希）：

```json
{
  "model_path": "/shared/public_models/Llama-3-8B",
  "device": "cuda",
  "dtype": "bfloat16",
  "generation_tokenizer": "/shared/public_models/Qwen2.5-0.5B",
  "max_length": null,
  "overflow": "error",
  "effective_max_length": 8192,
  "protocol": {
    "prompt": "source-generation-prompt; source chat template, not reference chat template",
    "boundary": "encode prompt and answer separately with add_special_tokens=False, then concatenate",
    "bos": "one reference BOS at start when defined; no extra EOS",
    "loss": "causal next-token NLL on all answer tokens, including the first; no prompt or padding loss",
    "aggregate": "exp(sum(answer NLL) / sum(scored answer tokens)); not mean per-answer PPL",
    "source_tokenizer_selection": "explicit override, otherwise row.model_path; fallback assumes the generation tokenizer matches that checkpoint",
    "legacy_prompt_limit": 2048,
    "weights_fingerprint": "weight filenames, sizes and mtime_ns; weight contents are not hashed"
  },
  "reference_assets": {
    "path": "/shared/public_models/Llama-3-8B",
    "assets": [
      {
        "name": "config.json",
        "size": 654,
        "sha256": "2430cee764b6530ff8673cf9ba8561e1d5a33152d503cd0de909ff5718261441"
      },
      {
        "name": "generation_config.json",
        "size": 126,
        "sha256": "55550e95c40c53fb0ee3f960d6d2b25a46405c8f790e5c4bb02caf3e98f2b5d0"
      },
      {
        "name": "model.safetensors.index.json",
        "size": 23950,
        "sha256": "146776fce3f6db1103aa6f249e65ee5544c5923ce6f971b092eee79aa6e5d37b"
      },
      {
        "name": "special_tokens_map.json",
        "size": 73,
        "sha256": "462d91939dbc37178aa5a3eae7068d1990ccc92e09f288cc71f42cdf139d69cc"
      },
      {
        "name": "tokenizer.json",
        "size": 9085698,
        "sha256": "e134af98b985517b4f068e3755ae90d4e9cd2d45d328325dc503f1c6b2d06cc7"
      },
      {
        "name": "tokenizer_config.json",
        "size": 50566,
        "sha256": "690727b4fed286383df1c7ca5e805124cb70c6eb4529f807c7b2e60ff741da7e"
      }
    ],
    "weight_stats": [
      {
        "name": "model-00001-of-00004.safetensors",
        "size": 4976698672,
        "mtime_ns": 1736746522477644778
      },
      {
        "name": "model-00002-of-00004.safetensors",
        "size": 4999802720,
        "mtime_ns": 1736746656058650226
      },
      {
        "name": "model-00003-of-00004.safetensors",
        "size": 4915916176,
        "mtime_ns": 1736746768408654808
      },
      {
        "name": "model-00004-of-00004.safetensors",
        "size": 1168138808,
        "mtime_ns": 1736746796088655937
      }
    ],
    "weight_content_hashed": false
  },
  "software": {
    "python": "3.10.21",
    "torch": "2.6.0",
    "transformers": "4.51.3",
    "tokenizers": "0.21.4"
  }
}
```

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.5522339999999997,
  "best_f1": {
    "threshold": -4.086514987502555,
    "fpr": 0.934,
    "tpr": 0.986,
    "precision": 0.5135416666666667,
    "f1": 0.6753424657534247,
    "tp": 493,
    "fp": 467,
    "tn": 33,
    "fn": 7
  },
  "tpr_at_fpr": {
    "1%": {
      "threshold": 10.97167280621632,
      "fpr": 0.01,
      "tpr": 0.024,
      "precision": 0.7058823529411765,
      "f1": 0.04642166344294004,
      "tp": 12,
      "fp": 5,
      "tn": 495,
      "fn": 488,
      "target_fpr": 0.01
    },
    "5%": {
      "threshold": 2.227560395692044,
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
      "threshold": 1.7210709770537855,
      "fpr": 0.1,
      "tpr": 0.1,
      "precision": 0.5,
      "f1": 0.16666666666666669,
      "tp": 50,
      "fp": 50,
      "tn": 450,
      "fn": 450,
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
      "clean": 2.0
    }
  },
  "rouge_l_dolly": {
    "mean": 0.23062544307532987,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/cleanD_dipperparaSFT_dipperparagad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl",
    "reference_file": "/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl",
    "reference_source": "databricks/databricks-dolly-15k:response",
    "metric": "rougeL",
    "measure": "fmeasure",
    "use_stemmer": true,
    "aggregation": "unweighted mean of per-sample ROUGE-L F1"
  },
  "rouge_l_teacher_clean": {
    "mean": 0.26299021564828223,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/cleanD_dipperparaSFT_dipperparagad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl",
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
        "mean": 0.47894372739853036,
        "median": 0.45681333053142953,
        "min": 0.0,
        "max": 1.0,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 26,
            "fraction": 0.052104208416833664
          },
          "5%": {
            "alpha": 0.05,
            "count": 52,
            "fraction": 0.10420841683366733
          },
          "10%": {
            "alpha": 0.1,
            "count": 87,
            "fraction": 0.1743486973947896
          }
        }
      },
      "deduplicated": {
        "n_total": 500,
        "n_valid": 499,
        "n_invalid": 1,
        "mean": 0.4981618534436643,
        "median": 0.5,
        "min": 0.00066727476323454,
        "max": 0.998458406954546,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 8,
            "fraction": 0.01603206412825651
          },
          "5%": {
            "alpha": 0.05,
            "count": 23,
            "fraction": 0.04609218436873747
          },
          "10%": {
            "alpha": 0.1,
            "count": 50,
            "fraction": 0.10020040080160321
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
    "kgw": "/shared/wwx/EasyGAD/wm_test/cleanD_dipperparaSFT_dipperparagad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.p_values.jsonl",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl"
  },
  "grouped_p_values": {
    "kgw": {
      "aggregation": "ordinary_median",
      "num_answers": 500,
      "total_answer_tokens": 78954,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 78,
          "total_answer_tokens": 78954,
          "discarded_tail_tokens": 954,
          "median_p_value": 0.3521682403141192,
          "median_log10_p_value": -0.4532498127022394,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 39,
          "total_answer_tokens": 78954,
          "discarded_tail_tokens": 954,
          "median_p_value": 0.12700158236106993,
          "median_log10_p_value": -0.8961908679700281,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 26,
          "total_answer_tokens": 78954,
          "discarded_tail_tokens": 954,
          "median_p_value": 0.011882386166088107,
          "median_log10_p_value": -1.925096337578257,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 7,
          "total_answer_tokens": 78954,
          "discarded_tail_tokens": 8954,
          "median_p_value": 2.701083854173134e-73,
          "median_log10_p_value": -72.56846193308786,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 3,
          "total_answer_tokens": 78954,
          "discarded_tail_tokens": 18954,
          "median_p_value": 8.064137075348553e-73,
          "median_log10_p_value": -72.09344209863646,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 2,
          "total_answer_tokens": 78954,
          "discarded_tail_tokens": 18954,
          "median_p_value": 1.2958368800443609e-113,
          "median_log10_p_value": -112.88744966401731,
          "status": "ok"
        }
      }
    },
    "clean": {
      "aggregation": "ordinary_median",
      "num_answers": 500,
      "total_answer_tokens": 159765,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 159,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 765,
          "median_p_value": 0.8659288977499955,
          "median_log10_p_value": -0.06251776685396769,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 79,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 1765,
          "median_p_value": 0.971357711016285,
          "median_log10_p_value": -0.012620807875598238,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 53,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 765,
          "median_p_value": 0.9821335190767914,
          "median_log10_p_value": -0.007829466737979084,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 15,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 9765,
          "median_p_value": 0.9999999999999984,
          "median_log10_p_value": -6.750292265873014e-16,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 7,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 19765,
          "median_p_value": 1.0,
          "median_log10_p_value": 0.0,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 5,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 9765,
          "median_p_value": 1.0,
          "median_log10_p_value": 0.0,
          "status": "ok"
        }
      }
    }
  },
  "grouped_p_value_method": "teacher-tokenizer answer IDs concatenated without separators; exact disjoint blocks; first token of each block is context only; no repetition deduplication; incomplete tail discarded; ordinary median of block p-values (arithmetic mean of the two middle p-values for even group counts)",
  "per_group_p_value_files": {
    "kgw": "/shared/wwx/EasyGAD/wm_test/cleanD_dipperparaSFT_dipperparagad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.grouped_p_values.json",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.grouped_p_values.json"
  },
  "grouped_p_values_without_severe_repetition": {
    "kgw": {
      "aggregation": "ordinary_median",
      "num_answers": 472,
      "total_answer_tokens": 49925,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 49,
          "total_answer_tokens": 49925,
          "discarded_tail_tokens": 925,
          "median_p_value": 0.5628476399744019,
          "median_log10_p_value": -0.24960915057209193,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 24,
          "total_answer_tokens": 49925,
          "discarded_tail_tokens": 1925,
          "median_p_value": 0.5443443589647108,
          "median_log10_p_value": -0.26412627330992794,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 16,
          "total_answer_tokens": 49925,
          "discarded_tail_tokens": 1925,
          "median_p_value": 0.6681052837703183,
          "median_log10_p_value": -0.17515509357601214,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 4,
          "total_answer_tokens": 49925,
          "discarded_tail_tokens": 9925,
          "median_p_value": 0.9206989325641465,
          "median_log10_p_value": -0.035882360358637407,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 2,
          "total_answer_tokens": 49925,
          "discarded_tail_tokens": 9925,
          "median_p_value": 0.7942343200919133,
          "median_log10_p_value": -0.10005135033119261,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 1,
          "total_answer_tokens": 49925,
          "discarded_tail_tokens": 19925,
          "median_p_value": 0.9030382887789778,
          "median_log10_p_value": -0.04429383523145779,
          "status": "ok"
        }
      },
      "filtering": {
        "repetition_threshold": 0.5,
        "comparison": ">",
        "scope": "answer-internal adjacent token pairs; prompt excluded",
        "num_answers_before": 500,
        "num_answers_retained": 472,
        "num_answers_removed": 28,
        "fraction_answers_removed": 0.056,
        "total_answer_tokens_before": 78954,
        "total_answer_tokens_retained": 49925,
        "total_answer_tokens_removed": 29029,
        "removed_answer_ids": [
          "dolly-00423",
          "dolly-12156",
          "dolly-12241",
          "dolly-07923",
          "dolly-02678",
          "dolly-01092",
          "dolly-03638",
          "dolly-05605",
          "dolly-12371",
          "dolly-11987",
          "dolly-03726",
          "dolly-13610",
          "dolly-08999",
          "dolly-05528",
          "dolly-06824",
          "dolly-08607",
          "dolly-10037",
          "dolly-03319",
          "dolly-07407",
          "dolly-10389",
          "dolly-07780",
          "dolly-12001",
          "dolly-06628",
          "dolly-09816",
          "dolly-06970",
          "dolly-00571",
          "dolly-01356",
          "dolly-12236"
        ]
      }
    },
    "clean": {
      "aggregation": "ordinary_median",
      "num_answers": 412,
      "total_answer_tokens": 45882,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 45,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 882,
          "median_p_value": 0.6360891449864364,
          "median_log10_p_value": -0.1964820156995508,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 22,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 1882,
          "median_p_value": 0.7960378878131416,
          "median_log10_p_value": -0.09906626131183685,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 15,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 882,
          "median_p_value": 0.7386263221105359,
          "median_log10_p_value": -0.13157521964243946,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 4,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 5882,
          "median_p_value": 0.947596846602552,
          "median_log10_p_value": -0.0233763931850151,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 2,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 5882,
          "median_p_value": 0.9783739864832501,
          "median_log10_p_value": -0.009495103065976066,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 1,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 15882,
          "median_p_value": 0.9995678964162934,
          "median_log10_p_value": -0.00018770075802065225,
          "status": "ok"
        }
      },
      "filtering": {
        "repetition_threshold": 0.5,
        "comparison": ">",
        "scope": "answer-internal adjacent token pairs; prompt excluded",
        "num_answers_before": 500,
        "num_answers_retained": 412,
        "num_answers_removed": 88,
        "fraction_answers_removed": 0.176,
        "total_answer_tokens_before": 159765,
        "total_answer_tokens_retained": 45882,
        "total_answer_tokens_removed": 113883,
        "removed_answer_ids": [
          "dolly-00135",
          "dolly-12241",
          "dolly-07923",
          "dolly-07103",
          "dolly-05608",
          "dolly-07788",
          "dolly-11310",
          "dolly-02097",
          "dolly-03614",
          "dolly-13505",
          "dolly-02580",
          "dolly-08884",
          "dolly-12659",
          "dolly-00420",
          "dolly-11014",
          "dolly-08008",
          "dolly-02186",
          "dolly-00275",
          "dolly-08512",
          "dolly-14060",
          "dolly-01461",
          "dolly-02223",
          "dolly-04949",
          "dolly-08689",
          "dolly-08574",
          "dolly-08406",
          "dolly-04141",
          "dolly-03209",
          "dolly-06227",
          "dolly-11078",
          "dolly-09778",
          "dolly-04856",
          "dolly-13779",
          "dolly-06595",
          "dolly-08936",
          "dolly-09344",
          "dolly-05605",
          "dolly-08340",
          "dolly-04589",
          "dolly-04686",
          "dolly-14700",
          "dolly-03696",
          "dolly-03914",
          "dolly-11987",
          "dolly-01939",
          "dolly-05628",
          "dolly-13339",
          "dolly-08911",
          "dolly-03239",
          "dolly-13445",
          "dolly-02139",
          "dolly-14265",
          "dolly-13610",
          "dolly-07427",
          "dolly-09563",
          "dolly-02451",
          "dolly-13544",
          "dolly-06824",
          "dolly-05312",
          "dolly-10992",
          "dolly-06932",
          "dolly-08607",
          "dolly-05388",
          "dolly-11386",
          "dolly-02069",
          "dolly-09439",
          "dolly-00148",
          "dolly-08211",
          "dolly-12186",
          "dolly-03319",
          "dolly-07407",
          "dolly-10389",
          "dolly-03916",
          "dolly-08222",
          "dolly-14947",
          "dolly-03624",
          "dolly-09330",
          "dolly-11182",
          "dolly-02059",
          "dolly-02916",
          "dolly-09816",
          "dolly-05355",
          "dolly-06970",
          "dolly-05634",
          "dolly-02500",
          "dolly-11314",
          "dolly-13235",
          "dolly-04223"
        ]
      }
    }
  },
  "grouped_p_value_without_severe_repetition_method": "exclude whole answers whose answer-internal adjacent-token-pair repetition ratio (1 - unique pairs / all pairs) is strictly greater than 0.5; prompts excluded from repetition assessment; filter each label independently; retain original answer order, then concatenate teacher-tokenizer answer IDs without separators; exact disjoint blocks, first token context only; no token-pair deduplication within retained blocks; incomplete tail discarded; ordinary median of block p-values (mean of the middle two for even counts)",
  "per_group_p_value_without_severe_repetition_files": {
    "kgw": "/shared/wwx/EasyGAD/wm_test/cleanD_dipperparaSFT_dipperparagad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.nonrepetitive_grouped_p_values.json",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.nonrepetitive_grouped_p_values.json"
  },
  "ppl": {
    "enabled": true,
    "schema": "saved-answer-reference-ppl-v1",
    "configuration": {
      "model_path": "/shared/public_models/Llama-3-8B",
      "device": "cuda",
      "dtype": "bfloat16",
      "generation_tokenizer": "/shared/public_models/Qwen2.5-0.5B",
      "max_length": null,
      "overflow": "error",
      "effective_max_length": 8192,
      "protocol": {
        "prompt": "source-generation-prompt; source chat template, not reference chat template",
        "boundary": "encode prompt and answer separately with add_special_tokens=False, then concatenate",
        "bos": "one reference BOS at start when defined; no extra EOS",
        "loss": "causal next-token NLL on all answer tokens, including the first; no prompt or padding loss",
        "aggregate": "exp(sum(answer NLL) / sum(scored answer tokens)); not mean per-answer PPL",
        "source_tokenizer_selection": "explicit override, otherwise row.model_path; fallback assumes the generation tokenizer matches that checkpoint",
        "legacy_prompt_limit": 2048,
        "weights_fingerprint": "weight filenames, sizes and mtime_ns; weight contents are not hashed"
      },
      "reference_assets": {
        "path": "/shared/public_models/Llama-3-8B",
        "assets": [
          {
            "name": "config.json",
            "size": 654,
            "sha256": "2430cee764b6530ff8673cf9ba8561e1d5a33152d503cd0de909ff5718261441"
          },
          {
            "name": "generation_config.json",
            "size": 126,
            "sha256": "55550e95c40c53fb0ee3f960d6d2b25a46405c8f790e5c4bb02caf3e98f2b5d0"
          },
          {
            "name": "model.safetensors.index.json",
            "size": 23950,
            "sha256": "146776fce3f6db1103aa6f249e65ee5544c5923ce6f971b092eee79aa6e5d37b"
          },
          {
            "name": "special_tokens_map.json",
            "size": 73,
            "sha256": "462d91939dbc37178aa5a3eae7068d1990ccc92e09f288cc71f42cdf139d69cc"
          },
          {
            "name": "tokenizer.json",
            "size": 9085698,
            "sha256": "e134af98b985517b4f068e3755ae90d4e9cd2d45d328325dc503f1c6b2d06cc7"
          },
          {
            "name": "tokenizer_config.json",
            "size": 50566,
            "sha256": "690727b4fed286383df1c7ca5e805124cb70c6eb4529f807c7b2e60ff741da7e"
          }
        ],
        "weight_stats": [
          {
            "name": "model-00001-of-00004.safetensors",
            "size": 4976698672,
            "mtime_ns": 1736746522477644778
          },
          {
            "name": "model-00002-of-00004.safetensors",
            "size": 4999802720,
            "mtime_ns": 1736746656058650226
          },
          {
            "name": "model-00003-of-00004.safetensors",
            "size": 4915916176,
            "mtime_ns": 1736746768408654808
          },
          {
            "name": "model-00004-of-00004.safetensors",
            "size": 1168138808,
            "mtime_ns": 1736746796088655937
          }
        ],
        "weight_content_hashed": false
      },
      "software": {
        "python": "3.10.21",
        "torch": "2.6.0",
        "transformers": "4.51.3",
        "tokenizers": "0.21.4"
      }
    },
    "files": {
      "kgw": {
        "samples": 500,
        "valid_samples": 499,
        "skipped_empty_answers": 1,
        "complete": false,
        "nonfinite_samples": 0,
        "status": "ok",
        "total_nll": 73963.68284063414,
        "scored_tokens": 77168,
        "mean_nll": 0.9584760890606746,
        "token_weighted_ppl": 2.6077195116345013,
        "mean_answer_tokens": 154.336,
        "source_prompt_truncated_samples": 3,
        "reference_prompt_truncated_samples": 0,
        "generation_configurations": [
          {
            "configuration": {
              "temperature": 0.7,
              "top_p": 0.9,
              "max_new_tokens": 1536,
              "max_prompt_tokens": 2048,
              "kgw_enabled_during_generation": false
            },
            "samples": 500
          }
        ],
        "generation_seeds": {
          "recorded_samples": 500,
          "minimum": 42,
          "maximum": 541,
          "individual_values": "see per-sample immutable records"
        },
        "student_model_paths": [
          "/shared/wwx/EasyGAD/checkpoints/kgwD_paraSFT_paraGAD_v1/gad/global_step_1813/actor/huggingface"
        ],
        "generation_tokenizer_paths": [
          "/shared/public_models/Qwen2.5-0.5B"
        ],
        "median_per_answer_ppl": 3.8724792292019137,
        "median_samples": 499,
        "median_status": "ok",
        "without_severe_repetition": {
          "samples": 472,
          "valid_samples": 471,
          "skipped_empty_answers": 1,
          "complete": false,
          "nonfinite_samples": 0,
          "status": "ok",
          "total_nll": 69196.19782468677,
          "scored_tokens": 49184,
          "mean_nll": 1.4068843084069365,
          "token_weighted_ppl": 4.083213530435112,
          "mean_answer_tokens": 104.20338983050847,
          "source_prompt_truncated_samples": 3,
          "reference_prompt_truncated_samples": 0,
          "generation_configurations": [
            {
              "configuration": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_new_tokens": 1536,
                "max_prompt_tokens": 2048,
                "kgw_enabled_during_generation": false
              },
              "samples": 472
            }
          ],
          "generation_seeds": {
            "recorded_samples": 472,
            "minimum": 42,
            "maximum": 541,
            "individual_values": "see per-sample immutable records"
          },
          "student_model_paths": [
            "/shared/wwx/EasyGAD/checkpoints/kgwD_paraSFT_paraGAD_v1/gad/global_step_1813/actor/huggingface"
          ],
          "generation_tokenizer_paths": [
            "/shared/public_models/Qwen2.5-0.5B"
          ],
          "median_per_answer_ppl": 3.9670735594143722,
          "median_samples": 471,
          "median_status": "ok",
          "num_answers_before": 500,
          "num_answers_retained": 472,
          "num_answers_removed": 28,
          "fraction_answers_removed": 0.056,
          "repetition_threshold": 0.5,
          "comparison": ">",
          "scope": "answer-internal adjacent token pairs; prompt excluded",
          "removed_answer_ids": [
            "dolly-00423",
            "dolly-12156",
            "dolly-12241",
            "dolly-07923",
            "dolly-02678",
            "dolly-01092",
            "dolly-03638",
            "dolly-05605",
            "dolly-12371",
            "dolly-11987",
            "dolly-03726",
            "dolly-13610",
            "dolly-08999",
            "dolly-05528",
            "dolly-06824",
            "dolly-08607",
            "dolly-10037",
            "dolly-03319",
            "dolly-07407",
            "dolly-10389",
            "dolly-07780",
            "dolly-12001",
            "dolly-06628",
            "dolly-09816",
            "dolly-06970",
            "dolly-00571",
            "dolly-01356",
            "dolly-12236"
          ],
          "filtering_source_file": "/shared/wwx/EasyGAD/wm_test/cleanD_dipperparaSFT_dipperparagad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.nonrepetitive_grouped_p_values.json",
          "filtering_source_sha256": "b6a1c151b66159f7d008c57d2b3b29282beb7dd5d8c0df69cbf24b9432139f54",
          "filtering_tokenizer": {
            "path": "/shared/public_models/Qwen2.5-14B-Instruct",
            "files_sha256": {
              "config.json": "7362de7db90a1e57fe153e55094e6c2fb7d904a3705d34296ff7de84488235f4",
              "merges.txt": "0de0bc38a29ea38eef099b677fa1ff52edd181e573529af26c4cd2136e233777",
              "tokenizer.json": "47ec9be242d3ef39b9c97ac0a3f06c1752f061b234e295bc0a2842067a3fe4f9",
              "tokenizer_config.json": "fa2a40a9d8c8c4bb7f25ab726eb78ec9cbaaef96d1fa26f1d7f5615e886449a8",
              "vocab.json": "ca10d7e9fb3ed18575dd1e277a2579c16d108e32f27439684afa0e10b1440910"
            }
          }
        },
        "source_path": "/shared/wwx/EasyGAD/wm_test/cleanD_dipperparaSFT_dipperparagad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl",
        "source_sha256": "b6a1c151b66159f7d008c57d2b3b29282beb7dd5d8c0df69cbf24b9432139f54",
        "per_sample_file": "/shared/wwx/EasyGAD/wm_test/cleanD_dipperparaSFT_dipperparagad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.ppl.999b78b10a07062da961.jsonl",
        "cache_reused": false
      },
      "clean": {
        "samples": 500,
        "valid_samples": 500,
        "skipped_empty_answers": 0,
        "complete": true,
        "nonfinite_samples": 0,
        "status": "ok",
        "total_nll": 67054.72902449768,
        "scored_tokens": 156267,
        "mean_nll": 0.42910357928735865,
        "token_weighted_ppl": 1.5358801115260794,
        "mean_answer_tokens": 312.534,
        "source_prompt_truncated_samples": 3,
        "reference_prompt_truncated_samples": 0,
        "generation_configurations": [
          {
            "configuration": {
              "kgw_enabled_during_generation": false,
              "max_new_tokens": 1536,
              "max_prompt_tokens": 2048,
              "temperature": 0.7,
              "top_p": 0.9
            },
            "samples": 500
          }
        ],
        "generation_seeds": {
          "recorded_samples": 500,
          "minimum": 42,
          "maximum": 541,
          "individual_values": "see per-sample immutable records"
        },
        "student_model_paths": [
          "/shared/public_models/Qwen2.5-0.5B"
        ],
        "generation_tokenizer_paths": [
          "/shared/public_models/Qwen2.5-0.5B"
        ],
        "median_per_answer_ppl": 2.5576398946471928,
        "median_samples": 500,
        "median_status": "ok",
        "without_severe_repetition": {
          "samples": 412,
          "valid_samples": 412,
          "skipped_empty_answers": 0,
          "complete": true,
          "nonfinite_samples": 0,
          "status": "ok",
          "total_nll": 44868.67048177123,
          "scored_tokens": 45137,
          "mean_nll": 0.9940552203684612,
          "token_weighted_ppl": 2.702170179562856,
          "mean_answer_tokens": 109.55582524271844,
          "source_prompt_truncated_samples": 1,
          "reference_prompt_truncated_samples": 0,
          "generation_configurations": [
            {
              "configuration": {
                "kgw_enabled_during_generation": false,
                "max_new_tokens": 1536,
                "max_prompt_tokens": 2048,
                "temperature": 0.7,
                "top_p": 0.9
              },
              "samples": 412
            }
          ],
          "generation_seeds": {
            "recorded_samples": 412,
            "minimum": 42,
            "maximum": 541,
            "individual_values": "see per-sample immutable records"
          },
          "student_model_paths": [
            "/shared/public_models/Qwen2.5-0.5B"
          ],
          "generation_tokenizer_paths": [
            "/shared/public_models/Qwen2.5-0.5B"
          ],
          "median_per_answer_ppl": 2.8522532998790773,
          "median_samples": 412,
          "median_status": "ok",
          "num_answers_before": 500,
          "num_answers_retained": 412,
          "num_answers_removed": 88,
          "fraction_answers_removed": 0.176,
          "repetition_threshold": 0.5,
          "comparison": ">",
          "scope": "answer-internal adjacent token pairs; prompt excluded",
          "removed_answer_ids": [
            "dolly-00135",
            "dolly-12241",
            "dolly-07923",
            "dolly-07103",
            "dolly-05608",
            "dolly-07788",
            "dolly-11310",
            "dolly-02097",
            "dolly-03614",
            "dolly-13505",
            "dolly-02580",
            "dolly-08884",
            "dolly-12659",
            "dolly-00420",
            "dolly-11014",
            "dolly-08008",
            "dolly-02186",
            "dolly-00275",
            "dolly-08512",
            "dolly-14060",
            "dolly-01461",
            "dolly-02223",
            "dolly-04949",
            "dolly-08689",
            "dolly-08574",
            "dolly-08406",
            "dolly-04141",
            "dolly-03209",
            "dolly-06227",
            "dolly-11078",
            "dolly-09778",
            "dolly-04856",
            "dolly-13779",
            "dolly-06595",
            "dolly-08936",
            "dolly-09344",
            "dolly-05605",
            "dolly-08340",
            "dolly-04589",
            "dolly-04686",
            "dolly-14700",
            "dolly-03696",
            "dolly-03914",
            "dolly-11987",
            "dolly-01939",
            "dolly-05628",
            "dolly-13339",
            "dolly-08911",
            "dolly-03239",
            "dolly-13445",
            "dolly-02139",
            "dolly-14265",
            "dolly-13610",
            "dolly-07427",
            "dolly-09563",
            "dolly-02451",
            "dolly-13544",
            "dolly-06824",
            "dolly-05312",
            "dolly-10992",
            "dolly-06932",
            "dolly-08607",
            "dolly-05388",
            "dolly-11386",
            "dolly-02069",
            "dolly-09439",
            "dolly-00148",
            "dolly-08211",
            "dolly-12186",
            "dolly-03319",
            "dolly-07407",
            "dolly-10389",
            "dolly-03916",
            "dolly-08222",
            "dolly-14947",
            "dolly-03624",
            "dolly-09330",
            "dolly-11182",
            "dolly-02059",
            "dolly-02916",
            "dolly-09816",
            "dolly-05355",
            "dolly-06970",
            "dolly-05634",
            "dolly-02500",
            "dolly-11314",
            "dolly-13235",
            "dolly-04223"
          ],
          "filtering_source_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.nonrepetitive_grouped_p_values.json",
          "filtering_source_sha256": "597b843d28d31c353c7bb9b94a3b6dccb564cb45ac2c5252f6a1592ccd768efe",
          "filtering_tokenizer": {
            "path": "/shared/public_models/Qwen2.5-14B-Instruct",
            "files_sha256": {
              "config.json": "7362de7db90a1e57fe153e55094e6c2fb7d904a3705d34296ff7de84488235f4",
              "merges.txt": "0de0bc38a29ea38eef099b677fa1ff52edd181e573529af26c4cd2136e233777",
              "tokenizer.json": "47ec9be242d3ef39b9c97ac0a3f06c1752f061b234e295bc0a2842067a3fe4f9",
              "tokenizer_config.json": "fa2a40a9d8c8c4bb7f25ab726eb78ec9cbaaef96d1fa26f1d7f5615e886449a8",
              "vocab.json": "ca10d7e9fb3ed18575dd1e277a2579c16d108e32f27439684afa0e10b1440910"
            }
          }
        },
        "source_path": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl",
        "source_sha256": "597b843d28d31c353c7bb9b94a3b6dccb564cb45ac2c5252f6a1592ccd768efe",
        "per_sample_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.ppl.877fc574f9ee35a5145f.jsonl",
        "cache_reused": true
      }
    }
  },
  "evaluated_at": "2026-10-29T16:58:32+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wm_test/cleanD_dipperparaSFT_dipperparagad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-10-29T19:45:29+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.552234
- 实际检测配置：`{"gamma": 0.5, "hash_key": 15485863, "seeding": "simple_1 (hash_key * previous_token_id)", "delta_by_label": {"kgw": 3.0, "clean": 2.0}}`
- ROUGE-L（同批 500 条原始 Dolly 回答作参考）：0.230625（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 原始 Dolly 参考文件：`/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl`
- ROUGE-L（同批 500 条 14B clean 教师回答作参考）：0.262990（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 14B clean 教师参考文件：`/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_clean_test.parquet`
- Best F1：0.675342（z 阈值 -4.086514987502555，TPR 0.986000，FPR 0.934000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.010000 | 0.024000 | 0.046422 | 10.97167280621632 |
  | 5% | 0.050000 | 0.062000 | 0.111511 | 2.227560395692044 |
  | 10% | 0.100000 | 0.100000 | 0.166667 | 1.7210709770537855 |

### Seq-Rep-3（全量回答，词级三元组重复率）

每条回答单独计算 1 - 不同三元组数 / 全部三元组数，再汇总逐回答算术平均和普通中位数；偶数条的中位数取中间两个值的算术平均。只对 answer 使用 split() 空白分词，保留大小写和标点；不包含 prompt，不跨回答拼接，不剔除严重重复回答，不按长度加权。少于 3 个词（含空回答）按 0 计入，数量单独列出；空回答数包含在短回答数内。数值以 0–1 比例报告。

| 文件组 | 样本数 | Seq-Rep-3 逐回答算术平均 ↓ | Seq-Rep-3 逐回答普通中位数 ↓ | 少于3词回答数 | 空回答数 |
|---|---:|---:|---:|---:|---:|
| kgw | 500 | 0.075443 | 0.015268 | 1 | 1 |
| clean | 500 | 0.159015 | 0.021919 | 1 | 0 |

- kgw: `/shared/wwx/EasyGAD/wm_test/cleanD_dipperparaSFT_dipperparagad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl`；SHA256 `b6a1c151b66159f7d008c57d2b3b29282beb7dd5d8c0df69cbf24b9432139f54`。

- clean: `/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl`；SHA256 `597b843d28d31c353c7bb9b94a3b6dccb564cb45ac2c5252f6a1592ccd768efe`。

两种逐条文本 p-value 统计（单侧正态近似；不是 AUROC 的显著性检验）：

去重规则：相同的 `(previous_token_id, token_id)` 只计一次；不修改回答文本。

| 数据 | 检测方式 | 有效样本 | p 均值 | p 中位数 | p≤0.01 | p≤0.05 | p≤0.10 |
|---|---|---:|---:|---:|---:|---:|---:|
| kgw | 原始 | 499/500 | 0.478944 | 0.456813 | 26 (5.21%) | 52 (10.42%) | 87 (17.43%) |
| kgw | token 对去重 | 499/500 | 0.498162 | 0.5 | 8 (1.60%) | 23 (4.61%) | 50 (10.02%) |
| clean | 原始 | 500/500 | 0.538121 | 0.57157 | 22 (4.40%) | 54 (10.80%) | 73 (14.60%) |
| clean | token 对去重 | 500/500 | 0.537418 | 0.555154 | 5 (1.00%) | 25 (5.00%) | 46 (9.20%) |

KGW 的小 p 占比是该理论阈值下的检出率，clean 的小 p 占比是实测误报率。p≤0.05 不保证实际 FPR=5%；去重可改善重复带来的失真，但不保证完全校准。空回答不做显著性检验，p=null，并排除在有效样本统计之外。

逐条 p-value：`/shared/wwx/EasyGAD/wm_test/cleanD_dipperparaSFT_dipperparagad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.p_values.jsonl`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl`

固定 token 分组 p-value（普通中位数；p 越大表示原单侧检验证据越弱）：

按教师 tokenizer 编码回答并无分隔拼接，精确分组；每组首 token 仅作上下文，其余 token 用本项目原 KGW 绿表评分；不去重，尾部不足一组丢弃；各组 p 排序后取普通中位数（偶数组取中间两个 p 的算术平均）。

| 每组 token 数 | 计分 token 数 | KGW 组数 | KGW median p ↑ | clean 组数 | clean median p | KGW/clean 丢弃尾部 tokens |
|---:|---:|---:|---:|---:|---:|---:|
| 1000 | 999 | 78 | 0.352168 | 159 | 0.865929 | 954/765 |
| 2000 | 1999 | 39 | 0.127002 | 79 | 0.971358 | 954/1765 |
| 3000 | 2999 | 26 | 0.0118824 | 53 | 0.982134 | 954/765 |
| 10000 | 9999 | 7 | 2.70108e-73 | 15 | 1 | 8954/9765 |
| 20000 | 19999 | 3 | 8.06414e-73 | 7 | 1 | 18954/19765 |
| 30000 | 29999 | 2 | 1.29584e-113 | 5 | 1 | 18954/9765 |

N/A 表示总 token 数不足一个完整组；组数为 1 或 2 时需结合逐组结果解释。极小 p 用科学计数法字符串保存，同时保留 log10(p)，避免浮点下溢为 0。

逐组 p-value 缓存：`/shared/wwx/EasyGAD/wm_test/cleanD_dipperparaSFT_dipperparagad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.grouped_p_values.json`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.grouped_p_values.json`

剔除严重重复回答后的固定 token 分组 p-value（普通中位数）：

先独立筛选 KGW 和 clean：回答内部相邻 token 对重复比例严格大于 50% 时，剔除整条回答；prompt 不参与判断。保留回答按原顺序重新无分隔拼接，各组首 token 仅作上下文；组内不做 token 对去重，尾部不足一组丢弃。这是质量筛选补充指标，原始全样本统计另行保留。

| 数据 | 原回答数 | 剔除严重重复回答 | 保留回答数 | 原 tokens | 剔除 tokens | 保留 tokens |
|---|---:|---:|---:|---:|---:|---:|
| kgw | 500 | 28 (5.60%) | 472 | 78954 | 29029 | 49925 |
| clean | 500 | 88 (17.60%) | 412 | 159765 | 113883 | 45882 |

| 每组 token 数 | 计分 token 数 | KGW 组数 | KGW median p ↑ | clean 组数 | clean median p | KGW/clean 丢弃尾部 tokens |
|---:|---:|---:|---:|---:|---:|---:|
| 1000 | 999 | 49 | 0.562848 | 45 | 0.636089 | 925/882 |
| 2000 | 1999 | 24 | 0.544344 | 22 | 0.796038 | 1925/1882 |
| 3000 | 2999 | 16 | 0.668105 | 15 | 0.738626 | 1925/882 |
| 10000 | 9999 | 4 | 0.920699 | 4 | 0.947597 | 9925/5882 |
| 20000 | 19999 | 2 | 0.794234 | 2 | 0.978374 | 9925/5882 |
| 30000 | 29999 | 1 | 0.903038 | 1 | 0.999568 | 19925/15882 |

N/A 表示筛选后不足一个完整组。各组 p 取普通中位数，偶数组取中间两个 p 的算术平均；组数较少时请结合逐组缓存解释。

剔除严重重复回答后的逐组 p-value 缓存：`/shared/wwx/EasyGAD/wm_test/cleanD_dipperparaSFT_dipperparagad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.nonrepetitive_grouped_p_values.json`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.nonrepetitive_grouped_p_values.json`

### 固定参考模型 PPL（只评分已保存的回答）

| 文件组 | 总体 PPL ↓ | 逐回答 PPL 中位数 ↓ | 剔除严重重复后总体 PPL ↓ | 保留回答数/原回答数 | 有效样本/总样本 | 状态 | 缓存复用 |
|---|---:|---:|---:|---:|---:|---|---|
| kgw | 2.607720 | 3.872479 | 4.083214 | 472/500 | 499/500 | ok | True |
| clean | 1.535880 | 2.557640 | 2.702170 | 412/500 | 500/500 | ok | True |

总体 PPL = exp(全部有效回答 NLL 总和 / 全部计分回答 token 数)，不是逐条 PPL 的算术平均。
逐回答 PPL 中位数对全量有效回答的 PPL 排序；偶数条取中间两个 PPL 的算术平均，不对平均 NLL 取中位数后再 exp。空回答或异常 loss 不计入，并单独报告数量。
剔除严重重复后总体 PPL：复用同源重复筛选缓存，按教师 tokenizer 的回答内部相邻 token 对重复率严格 > 50% 剔除整条回答，prompt 不参与判断；只汇总保留回答原有的参考模型 NLL 和参考 tokenizer token 数。保留回答的文本不变，不删除文内 token，不丢弃尾部。KGW 与 clean 各自筛选，保留回答数含未成功评分回答。N/A 表示未提供筛选，null 表示无可计算数值；筛选后结果是子集统计，全量结果另行保留。
原生成 tokenizer 恢复实际生成 prompt；参考 tokenizer 对 prompt/answer 分开编码后拼接；只计回答，包含首回答 token。Base 参考模型不再套用 chat template；只添加一次参考 BOS，不额外评分 EOS；输入 JSONL 不修改。

- kgw: `/shared/wwx/EasyGAD/wm_test/cleanD_dipperparaSFT_dipperparagad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl`；SHA256 `b6a1c151b66159f7d008c57d2b3b29282beb7dd5d8c0df69cbf24b9432139f54`；逐条明细 `/shared/wwx/EasyGAD/wm_test/cleanD_dipperparaSFT_dipperparagad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.ppl.999b78b10a07062da961.jsonl`；空回答 1；异常 loss 0；原生成截断 3；参考上下文截断 0；计分回答 tokens 77168；平均回答 tokens 154.34；中位数样本数 499（状态 ok）。
  **kgw 的评测不完整：总体值只覆盖有效回答，不能作为全量样本 PPL。**
  剔除严重重复回答 28（5.60%）；保留回答中有效评分 471/472；保留回答计分 tokens 49184；状态 ok；重复筛选缓存 `/shared/wwx/EasyGAD/wm_test/cleanD_dipperparaSFT_dipperparagad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.nonrepetitive_grouped_p_values.json`。
  **kgw 的筛选后评测不完整：筛选后 PPL 仅覆盖成功评分的保留回答。**

  生成文本配置（种子逐条保存在明细中）：

```json
{
  "student_model_paths": [
    "/shared/wwx/EasyGAD/checkpoints/kgwD_paraSFT_paraGAD_v1/gad/global_step_1813/actor/huggingface"
  ],
  "generation_tokenizer_paths": [
    "/shared/public_models/Qwen2.5-0.5B"
  ],
  "generation_configurations": [
    {
      "configuration": {
        "kgw_enabled_during_generation": false,
        "max_new_tokens": 1536,
        "max_prompt_tokens": 2048,
        "temperature": 0.7,
        "top_p": 0.9
      },
      "samples": 500
    }
  ],
  "generation_seeds": {
    "recorded_samples": 500,
    "minimum": 42,
    "maximum": 541,
    "individual_values": "see per-sample immutable records"
  }
}
```
- clean: `/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl`；SHA256 `597b843d28d31c353c7bb9b94a3b6dccb564cb45ac2c5252f6a1592ccd768efe`；逐条明细 `/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.ppl.877fc574f9ee35a5145f.jsonl`；空回答 0；异常 loss 0；原生成截断 3；参考上下文截断 0；计分回答 tokens 156267；平均回答 tokens 312.53；中位数样本数 500（状态 ok）。
  剔除严重重复回答 88（17.60%）；保留回答中有效评分 412/412；保留回答计分 tokens 45137；状态 ok；重复筛选缓存 `/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.nonrepetitive_grouped_p_values.json`。

  生成文本配置（种子逐条保存在明细中）：

```json
{
  "student_model_paths": [
    "/shared/public_models/Qwen2.5-0.5B"
  ],
  "generation_tokenizer_paths": [
    "/shared/public_models/Qwen2.5-0.5B"
  ],
  "generation_configurations": [
    {
      "configuration": {
        "kgw_enabled_during_generation": false,
        "max_new_tokens": 1536,
        "max_prompt_tokens": 2048,
        "temperature": 0.7,
        "top_p": 0.9
      },
      "samples": 500
    }
  ],
  "generation_seeds": {
    "recorded_samples": 500,
    "minimum": 42,
    "maximum": 541,
    "individual_values": "see per-sample immutable records"
  }
}
```

完整评分配置（含模型/tokenizer 指纹、软件版本；权重使用 size/mtime 标识，不全量哈希）：

```json
{
  "model_path": "/shared/public_models/Llama-3-8B",
  "device": "cuda",
  "dtype": "bfloat16",
  "generation_tokenizer": "/shared/public_models/Qwen2.5-0.5B",
  "max_length": null,
  "overflow": "error",
  "effective_max_length": 8192,
  "protocol": {
    "prompt": "source-generation-prompt; source chat template, not reference chat template",
    "boundary": "encode prompt and answer separately with add_special_tokens=False, then concatenate",
    "bos": "one reference BOS at start when defined; no extra EOS",
    "loss": "causal next-token NLL on all answer tokens, including the first; no prompt or padding loss",
    "aggregate": "exp(sum(answer NLL) / sum(scored answer tokens)); not mean per-answer PPL",
    "source_tokenizer_selection": "explicit override, otherwise row.model_path; fallback assumes the generation tokenizer matches that checkpoint",
    "legacy_prompt_limit": 2048,
    "weights_fingerprint": "weight filenames, sizes and mtime_ns; weight contents are not hashed"
  },
  "reference_assets": {
    "path": "/shared/public_models/Llama-3-8B",
    "assets": [
      {
        "name": "config.json",
        "size": 654,
        "sha256": "2430cee764b6530ff8673cf9ba8561e1d5a33152d503cd0de909ff5718261441"
      },
      {
        "name": "generation_config.json",
        "size": 126,
        "sha256": "55550e95c40c53fb0ee3f960d6d2b25a46405c8f790e5c4bb02caf3e98f2b5d0"
      },
      {
        "name": "model.safetensors.index.json",
        "size": 23950,
        "sha256": "146776fce3f6db1103aa6f249e65ee5544c5923ce6f971b092eee79aa6e5d37b"
      },
      {
        "name": "special_tokens_map.json",
        "size": 73,
        "sha256": "462d91939dbc37178aa5a3eae7068d1990ccc92e09f288cc71f42cdf139d69cc"
      },
      {
        "name": "tokenizer.json",
        "size": 9085698,
        "sha256": "e134af98b985517b4f068e3755ae90d4e9cd2d45d328325dc503f1c6b2d06cc7"
      },
      {
        "name": "tokenizer_config.json",
        "size": 50566,
        "sha256": "690727b4fed286383df1c7ca5e805124cb70c6eb4529f807c7b2e60ff741da7e"
      }
    ],
    "weight_stats": [
      {
        "name": "model-00001-of-00004.safetensors",
        "size": 4976698672,
        "mtime_ns": 1736746522477644778
      },
      {
        "name": "model-00002-of-00004.safetensors",
        "size": 4999802720,
        "mtime_ns": 1736746656058650226
      },
      {
        "name": "model-00003-of-00004.safetensors",
        "size": 4915916176,
        "mtime_ns": 1736746768408654808
      },
      {
        "name": "model-00004-of-00004.safetensors",
        "size": 1168138808,
        "mtime_ns": 1736746796088655937
      }
    ],
    "weight_content_hashed": false
  },
  "software": {
    "python": "3.10.21",
    "torch": "2.6.0",
    "transformers": "4.51.3",
    "tokenizers": "0.21.4"
  }
}
```

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.5522339999999997,
  "best_f1": {
    "threshold": -4.086514987502555,
    "fpr": 0.934,
    "tpr": 0.986,
    "precision": 0.5135416666666667,
    "f1": 0.6753424657534247,
    "tp": 493,
    "fp": 467,
    "tn": 33,
    "fn": 7
  },
  "tpr_at_fpr": {
    "1%": {
      "threshold": 10.97167280621632,
      "fpr": 0.01,
      "tpr": 0.024,
      "precision": 0.7058823529411765,
      "f1": 0.04642166344294004,
      "tp": 12,
      "fp": 5,
      "tn": 495,
      "fn": 488,
      "target_fpr": 0.01
    },
    "5%": {
      "threshold": 2.227560395692044,
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
      "threshold": 1.7210709770537855,
      "fpr": 0.1,
      "tpr": 0.1,
      "precision": 0.5,
      "f1": 0.16666666666666669,
      "tp": 50,
      "fp": 50,
      "tn": 450,
      "fn": 450,
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
      "clean": 2.0
    }
  },
  "rouge_l_dolly": {
    "mean": 0.23062544307532987,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/cleanD_dipperparaSFT_dipperparagad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl",
    "reference_file": "/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl",
    "reference_source": "databricks/databricks-dolly-15k:response",
    "metric": "rougeL",
    "measure": "fmeasure",
    "use_stemmer": true,
    "aggregation": "unweighted mean of per-sample ROUGE-L F1"
  },
  "rouge_l_teacher_clean": {
    "mean": 0.26299021564828223,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/cleanD_dipperparaSFT_dipperparagad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl",
    "reference_file": "/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_clean_test.parquet",
    "reference_source": "Qwen2.5-14B clean teacher responses",
    "metric": "rougeL",
    "measure": "fmeasure",
    "use_stemmer": true,
    "aggregation": "unweighted mean of per-sample ROUGE-L F1"
  },
  "seq_rep_3": {
    "kgw": {
      "mean": 0.07544276629476974,
      "median": 0.015268065268065234,
      "num_samples": 500,
      "num_short_answers": 1,
      "num_empty_answers": 1,
      "evaluated_file": "/shared/wwx/EasyGAD/wm_test/cleanD_dipperparaSFT_dipperparagad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl",
      "source_sha256": "b6a1c151b66159f7d008c57d2b3b29282beb7dd5d8c0df69cbf24b9432139f54",
      "ngram_size": 3,
      "tokenization": "answer.split(); whitespace-delimited words; case and punctuation preserved",
      "scope": "answer only; overlapping trigrams within each complete original answer; no filtering or cross-answer trigrams",
      "short_answer_policy": "answers with fewer than 3 words, including empty answers, contribute 0; counts reported",
      "aggregation": {
        "mean": "unweighted arithmetic mean of per-answer Seq-Rep-3",
        "median": "ordinary median of per-answer Seq-Rep-3; arithmetic mean of the middle two for even counts"
      }
    },
    "clean": {
      "mean": 0.15901538183339659,
      "median": 0.021919288974297402,
      "num_samples": 500,
      "num_short_answers": 1,
      "num_empty_answers": 0,
      "evaluated_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl",
      "source_sha256": "597b843d28d31c353c7bb9b94a3b6dccb564cb45ac2c5252f6a1592ccd768efe",
      "ngram_size": 3,
      "tokenization": "answer.split(); whitespace-delimited words; case and punctuation preserved",
      "scope": "answer only; overlapping trigrams within each complete original answer; no filtering or cross-answer trigrams",
      "short_answer_policy": "answers with fewer than 3 words, including empty answers, contribute 0; counts reported",
      "aggregation": {
        "mean": "unweighted arithmetic mean of per-answer Seq-Rep-3",
        "median": "ordinary median of per-answer Seq-Rep-3; arithmetic mean of the middle two for even counts"
      }
    }
  },
  "p_values": {
    "kgw": {
      "raw": {
        "n_total": 500,
        "n_valid": 499,
        "n_invalid": 1,
        "mean": 0.47894372739853036,
        "median": 0.45681333053142953,
        "min": 0.0,
        "max": 1.0,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 26,
            "fraction": 0.052104208416833664
          },
          "5%": {
            "alpha": 0.05,
            "count": 52,
            "fraction": 0.10420841683366733
          },
          "10%": {
            "alpha": 0.1,
            "count": 87,
            "fraction": 0.1743486973947896
          }
        }
      },
      "deduplicated": {
        "n_total": 500,
        "n_valid": 499,
        "n_invalid": 1,
        "mean": 0.4981618534436643,
        "median": 0.5,
        "min": 0.00066727476323454,
        "max": 0.998458406954546,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 8,
            "fraction": 0.01603206412825651
          },
          "5%": {
            "alpha": 0.05,
            "count": 23,
            "fraction": 0.04609218436873747
          },
          "10%": {
            "alpha": 0.1,
            "count": 50,
            "fraction": 0.10020040080160321
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
    "kgw": "/shared/wwx/EasyGAD/wm_test/cleanD_dipperparaSFT_dipperparagad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.p_values.jsonl",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl"
  },
  "grouped_p_values": {
    "kgw": {
      "aggregation": "ordinary_median",
      "num_answers": 500,
      "total_answer_tokens": 78954,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 78,
          "total_answer_tokens": 78954,
          "discarded_tail_tokens": 954,
          "median_p_value": 0.3521682403141192,
          "median_log10_p_value": -0.4532498127022394,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 39,
          "total_answer_tokens": 78954,
          "discarded_tail_tokens": 954,
          "median_p_value": 0.12700158236106993,
          "median_log10_p_value": -0.8961908679700281,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 26,
          "total_answer_tokens": 78954,
          "discarded_tail_tokens": 954,
          "median_p_value": 0.011882386166088107,
          "median_log10_p_value": -1.925096337578257,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 7,
          "total_answer_tokens": 78954,
          "discarded_tail_tokens": 8954,
          "median_p_value": 2.701083854173134e-73,
          "median_log10_p_value": -72.56846193308786,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 3,
          "total_answer_tokens": 78954,
          "discarded_tail_tokens": 18954,
          "median_p_value": 8.064137075348553e-73,
          "median_log10_p_value": -72.09344209863646,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 2,
          "total_answer_tokens": 78954,
          "discarded_tail_tokens": 18954,
          "median_p_value": 1.2958368800443609e-113,
          "median_log10_p_value": -112.88744966401731,
          "status": "ok"
        }
      }
    },
    "clean": {
      "aggregation": "ordinary_median",
      "num_answers": 500,
      "total_answer_tokens": 159765,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 159,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 765,
          "median_p_value": 0.8659288977499955,
          "median_log10_p_value": -0.06251776685396769,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 79,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 1765,
          "median_p_value": 0.971357711016285,
          "median_log10_p_value": -0.012620807875598238,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 53,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 765,
          "median_p_value": 0.9821335190767914,
          "median_log10_p_value": -0.007829466737979084,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 15,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 9765,
          "median_p_value": 0.9999999999999984,
          "median_log10_p_value": -6.750292265873014e-16,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 7,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 19765,
          "median_p_value": 1.0,
          "median_log10_p_value": 0.0,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 5,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 9765,
          "median_p_value": 1.0,
          "median_log10_p_value": 0.0,
          "status": "ok"
        }
      }
    }
  },
  "grouped_p_value_method": "teacher-tokenizer answer IDs concatenated without separators; exact disjoint blocks; first token of each block is context only; no repetition deduplication; incomplete tail discarded; ordinary median of block p-values (arithmetic mean of the two middle p-values for even group counts)",
  "per_group_p_value_files": {
    "kgw": "/shared/wwx/EasyGAD/wm_test/cleanD_dipperparaSFT_dipperparagad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.grouped_p_values.json",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.grouped_p_values.json"
  },
  "grouped_p_values_without_severe_repetition": {
    "kgw": {
      "aggregation": "ordinary_median",
      "num_answers": 472,
      "total_answer_tokens": 49925,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 49,
          "total_answer_tokens": 49925,
          "discarded_tail_tokens": 925,
          "median_p_value": 0.5628476399744019,
          "median_log10_p_value": -0.24960915057209193,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 24,
          "total_answer_tokens": 49925,
          "discarded_tail_tokens": 1925,
          "median_p_value": 0.5443443589647108,
          "median_log10_p_value": -0.26412627330992794,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 16,
          "total_answer_tokens": 49925,
          "discarded_tail_tokens": 1925,
          "median_p_value": 0.6681052837703183,
          "median_log10_p_value": -0.17515509357601214,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 4,
          "total_answer_tokens": 49925,
          "discarded_tail_tokens": 9925,
          "median_p_value": 0.9206989325641465,
          "median_log10_p_value": -0.035882360358637407,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 2,
          "total_answer_tokens": 49925,
          "discarded_tail_tokens": 9925,
          "median_p_value": 0.7942343200919133,
          "median_log10_p_value": -0.10005135033119261,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 1,
          "total_answer_tokens": 49925,
          "discarded_tail_tokens": 19925,
          "median_p_value": 0.9030382887789778,
          "median_log10_p_value": -0.04429383523145779,
          "status": "ok"
        }
      },
      "filtering": {
        "repetition_threshold": 0.5,
        "comparison": ">",
        "scope": "answer-internal adjacent token pairs; prompt excluded",
        "num_answers_before": 500,
        "num_answers_retained": 472,
        "num_answers_removed": 28,
        "fraction_answers_removed": 0.056,
        "total_answer_tokens_before": 78954,
        "total_answer_tokens_retained": 49925,
        "total_answer_tokens_removed": 29029,
        "removed_answer_ids": [
          "dolly-00423",
          "dolly-12156",
          "dolly-12241",
          "dolly-07923",
          "dolly-02678",
          "dolly-01092",
          "dolly-03638",
          "dolly-05605",
          "dolly-12371",
          "dolly-11987",
          "dolly-03726",
          "dolly-13610",
          "dolly-08999",
          "dolly-05528",
          "dolly-06824",
          "dolly-08607",
          "dolly-10037",
          "dolly-03319",
          "dolly-07407",
          "dolly-10389",
          "dolly-07780",
          "dolly-12001",
          "dolly-06628",
          "dolly-09816",
          "dolly-06970",
          "dolly-00571",
          "dolly-01356",
          "dolly-12236"
        ]
      }
    },
    "clean": {
      "aggregation": "ordinary_median",
      "num_answers": 412,
      "total_answer_tokens": 45882,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 45,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 882,
          "median_p_value": 0.6360891449864364,
          "median_log10_p_value": -0.1964820156995508,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 22,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 1882,
          "median_p_value": 0.7960378878131416,
          "median_log10_p_value": -0.09906626131183685,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 15,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 882,
          "median_p_value": 0.7386263221105359,
          "median_log10_p_value": -0.13157521964243946,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 4,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 5882,
          "median_p_value": 0.947596846602552,
          "median_log10_p_value": -0.0233763931850151,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 2,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 5882,
          "median_p_value": 0.9783739864832501,
          "median_log10_p_value": -0.009495103065976066,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 1,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 15882,
          "median_p_value": 0.9995678964162934,
          "median_log10_p_value": -0.00018770075802065225,
          "status": "ok"
        }
      },
      "filtering": {
        "repetition_threshold": 0.5,
        "comparison": ">",
        "scope": "answer-internal adjacent token pairs; prompt excluded",
        "num_answers_before": 500,
        "num_answers_retained": 412,
        "num_answers_removed": 88,
        "fraction_answers_removed": 0.176,
        "total_answer_tokens_before": 159765,
        "total_answer_tokens_retained": 45882,
        "total_answer_tokens_removed": 113883,
        "removed_answer_ids": [
          "dolly-00135",
          "dolly-12241",
          "dolly-07923",
          "dolly-07103",
          "dolly-05608",
          "dolly-07788",
          "dolly-11310",
          "dolly-02097",
          "dolly-03614",
          "dolly-13505",
          "dolly-02580",
          "dolly-08884",
          "dolly-12659",
          "dolly-00420",
          "dolly-11014",
          "dolly-08008",
          "dolly-02186",
          "dolly-00275",
          "dolly-08512",
          "dolly-14060",
          "dolly-01461",
          "dolly-02223",
          "dolly-04949",
          "dolly-08689",
          "dolly-08574",
          "dolly-08406",
          "dolly-04141",
          "dolly-03209",
          "dolly-06227",
          "dolly-11078",
          "dolly-09778",
          "dolly-04856",
          "dolly-13779",
          "dolly-06595",
          "dolly-08936",
          "dolly-09344",
          "dolly-05605",
          "dolly-08340",
          "dolly-04589",
          "dolly-04686",
          "dolly-14700",
          "dolly-03696",
          "dolly-03914",
          "dolly-11987",
          "dolly-01939",
          "dolly-05628",
          "dolly-13339",
          "dolly-08911",
          "dolly-03239",
          "dolly-13445",
          "dolly-02139",
          "dolly-14265",
          "dolly-13610",
          "dolly-07427",
          "dolly-09563",
          "dolly-02451",
          "dolly-13544",
          "dolly-06824",
          "dolly-05312",
          "dolly-10992",
          "dolly-06932",
          "dolly-08607",
          "dolly-05388",
          "dolly-11386",
          "dolly-02069",
          "dolly-09439",
          "dolly-00148",
          "dolly-08211",
          "dolly-12186",
          "dolly-03319",
          "dolly-07407",
          "dolly-10389",
          "dolly-03916",
          "dolly-08222",
          "dolly-14947",
          "dolly-03624",
          "dolly-09330",
          "dolly-11182",
          "dolly-02059",
          "dolly-02916",
          "dolly-09816",
          "dolly-05355",
          "dolly-06970",
          "dolly-05634",
          "dolly-02500",
          "dolly-11314",
          "dolly-13235",
          "dolly-04223"
        ]
      }
    }
  },
  "grouped_p_value_without_severe_repetition_method": "exclude whole answers whose answer-internal adjacent-token-pair repetition ratio (1 - unique pairs / all pairs) is strictly greater than 0.5; prompts excluded from repetition assessment; filter each label independently; retain original answer order, then concatenate teacher-tokenizer answer IDs without separators; exact disjoint blocks, first token context only; no token-pair deduplication within retained blocks; incomplete tail discarded; ordinary median of block p-values (mean of the middle two for even counts)",
  "per_group_p_value_without_severe_repetition_files": {
    "kgw": "/shared/wwx/EasyGAD/wm_test/cleanD_dipperparaSFT_dipperparagad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.nonrepetitive_grouped_p_values.json",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.nonrepetitive_grouped_p_values.json"
  },
  "ppl": {
    "enabled": true,
    "schema": "saved-answer-reference-ppl-v1",
    "configuration": {
      "model_path": "/shared/public_models/Llama-3-8B",
      "device": "cuda",
      "dtype": "bfloat16",
      "generation_tokenizer": "/shared/public_models/Qwen2.5-0.5B",
      "max_length": null,
      "overflow": "error",
      "effective_max_length": 8192,
      "protocol": {
        "prompt": "source-generation-prompt; source chat template, not reference chat template",
        "boundary": "encode prompt and answer separately with add_special_tokens=False, then concatenate",
        "bos": "one reference BOS at start when defined; no extra EOS",
        "loss": "causal next-token NLL on all answer tokens, including the first; no prompt or padding loss",
        "aggregate": "exp(sum(answer NLL) / sum(scored answer tokens)); not mean per-answer PPL",
        "source_tokenizer_selection": "explicit override, otherwise row.model_path; fallback assumes the generation tokenizer matches that checkpoint",
        "legacy_prompt_limit": 2048,
        "weights_fingerprint": "weight filenames, sizes and mtime_ns; weight contents are not hashed"
      },
      "reference_assets": {
        "path": "/shared/public_models/Llama-3-8B",
        "assets": [
          {
            "name": "config.json",
            "size": 654,
            "sha256": "2430cee764b6530ff8673cf9ba8561e1d5a33152d503cd0de909ff5718261441"
          },
          {
            "name": "generation_config.json",
            "size": 126,
            "sha256": "55550e95c40c53fb0ee3f960d6d2b25a46405c8f790e5c4bb02caf3e98f2b5d0"
          },
          {
            "name": "model.safetensors.index.json",
            "size": 23950,
            "sha256": "146776fce3f6db1103aa6f249e65ee5544c5923ce6f971b092eee79aa6e5d37b"
          },
          {
            "name": "special_tokens_map.json",
            "size": 73,
            "sha256": "462d91939dbc37178aa5a3eae7068d1990ccc92e09f288cc71f42cdf139d69cc"
          },
          {
            "name": "tokenizer.json",
            "size": 9085698,
            "sha256": "e134af98b985517b4f068e3755ae90d4e9cd2d45d328325dc503f1c6b2d06cc7"
          },
          {
            "name": "tokenizer_config.json",
            "size": 50566,
            "sha256": "690727b4fed286383df1c7ca5e805124cb70c6eb4529f807c7b2e60ff741da7e"
          }
        ],
        "weight_stats": [
          {
            "name": "model-00001-of-00004.safetensors",
            "size": 4976698672,
            "mtime_ns": 1736746522477644778
          },
          {
            "name": "model-00002-of-00004.safetensors",
            "size": 4999802720,
            "mtime_ns": 1736746656058650226
          },
          {
            "name": "model-00003-of-00004.safetensors",
            "size": 4915916176,
            "mtime_ns": 1736746768408654808
          },
          {
            "name": "model-00004-of-00004.safetensors",
            "size": 1168138808,
            "mtime_ns": 1736746796088655937
          }
        ],
        "weight_content_hashed": false
      },
      "software": {
        "python": "3.10.21",
        "torch": "2.6.0",
        "transformers": "4.51.3",
        "tokenizers": "0.21.4"
      }
    },
    "files": {
      "kgw": {
        "samples": 500,
        "valid_samples": 499,
        "skipped_empty_answers": 1,
        "complete": false,
        "nonfinite_samples": 0,
        "status": "ok",
        "total_nll": 73963.68284063414,
        "scored_tokens": 77168,
        "mean_nll": 0.9584760890606746,
        "token_weighted_ppl": 2.6077195116345013,
        "mean_answer_tokens": 154.336,
        "source_prompt_truncated_samples": 3,
        "reference_prompt_truncated_samples": 0,
        "generation_configurations": [
          {
            "configuration": {
              "kgw_enabled_during_generation": false,
              "max_new_tokens": 1536,
              "max_prompt_tokens": 2048,
              "temperature": 0.7,
              "top_p": 0.9
            },
            "samples": 500
          }
        ],
        "generation_seeds": {
          "recorded_samples": 500,
          "minimum": 42,
          "maximum": 541,
          "individual_values": "see per-sample immutable records"
        },
        "student_model_paths": [
          "/shared/wwx/EasyGAD/checkpoints/kgwD_paraSFT_paraGAD_v1/gad/global_step_1813/actor/huggingface"
        ],
        "generation_tokenizer_paths": [
          "/shared/public_models/Qwen2.5-0.5B"
        ],
        "median_per_answer_ppl": 3.8724792292019137,
        "median_samples": 499,
        "median_status": "ok",
        "without_severe_repetition": {
          "samples": 472,
          "valid_samples": 471,
          "skipped_empty_answers": 1,
          "complete": false,
          "nonfinite_samples": 0,
          "status": "ok",
          "total_nll": 69196.19782468677,
          "scored_tokens": 49184,
          "mean_nll": 1.4068843084069365,
          "token_weighted_ppl": 4.083213530435112,
          "mean_answer_tokens": 104.20338983050847,
          "source_prompt_truncated_samples": 3,
          "reference_prompt_truncated_samples": 0,
          "generation_configurations": [
            {
              "configuration": {
                "kgw_enabled_during_generation": false,
                "max_new_tokens": 1536,
                "max_prompt_tokens": 2048,
                "temperature": 0.7,
                "top_p": 0.9
              },
              "samples": 472
            }
          ],
          "generation_seeds": {
            "recorded_samples": 472,
            "minimum": 42,
            "maximum": 541,
            "individual_values": "see per-sample immutable records"
          },
          "student_model_paths": [
            "/shared/wwx/EasyGAD/checkpoints/kgwD_paraSFT_paraGAD_v1/gad/global_step_1813/actor/huggingface"
          ],
          "generation_tokenizer_paths": [
            "/shared/public_models/Qwen2.5-0.5B"
          ],
          "median_per_answer_ppl": 3.9670735594143722,
          "median_samples": 471,
          "median_status": "ok",
          "num_answers_before": 500,
          "num_answers_retained": 472,
          "num_answers_removed": 28,
          "fraction_answers_removed": 0.056,
          "repetition_threshold": 0.5,
          "comparison": ">",
          "scope": "answer-internal adjacent token pairs; prompt excluded",
          "removed_answer_ids": [
            "dolly-00423",
            "dolly-12156",
            "dolly-12241",
            "dolly-07923",
            "dolly-02678",
            "dolly-01092",
            "dolly-03638",
            "dolly-05605",
            "dolly-12371",
            "dolly-11987",
            "dolly-03726",
            "dolly-13610",
            "dolly-08999",
            "dolly-05528",
            "dolly-06824",
            "dolly-08607",
            "dolly-10037",
            "dolly-03319",
            "dolly-07407",
            "dolly-10389",
            "dolly-07780",
            "dolly-12001",
            "dolly-06628",
            "dolly-09816",
            "dolly-06970",
            "dolly-00571",
            "dolly-01356",
            "dolly-12236"
          ],
          "filtering_source_file": "/shared/wwx/EasyGAD/wm_test/cleanD_dipperparaSFT_dipperparagad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.nonrepetitive_grouped_p_values.json",
          "filtering_source_sha256": "b6a1c151b66159f7d008c57d2b3b29282beb7dd5d8c0df69cbf24b9432139f54",
          "filtering_tokenizer": {
            "path": "/shared/public_models/Qwen2.5-14B-Instruct",
            "files_sha256": {
              "config.json": "7362de7db90a1e57fe153e55094e6c2fb7d904a3705d34296ff7de84488235f4",
              "merges.txt": "0de0bc38a29ea38eef099b677fa1ff52edd181e573529af26c4cd2136e233777",
              "tokenizer.json": "47ec9be242d3ef39b9c97ac0a3f06c1752f061b234e295bc0a2842067a3fe4f9",
              "tokenizer_config.json": "fa2a40a9d8c8c4bb7f25ab726eb78ec9cbaaef96d1fa26f1d7f5615e886449a8",
              "vocab.json": "ca10d7e9fb3ed18575dd1e277a2579c16d108e32f27439684afa0e10b1440910"
            }
          }
        },
        "source_path": "/shared/wwx/EasyGAD/wm_test/cleanD_dipperparaSFT_dipperparagad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl",
        "source_sha256": "b6a1c151b66159f7d008c57d2b3b29282beb7dd5d8c0df69cbf24b9432139f54",
        "per_sample_file": "/shared/wwx/EasyGAD/wm_test/cleanD_dipperparaSFT_dipperparagad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.ppl.999b78b10a07062da961.jsonl",
        "cache_reused": true
      },
      "clean": {
        "samples": 500,
        "valid_samples": 500,
        "skipped_empty_answers": 0,
        "complete": true,
        "nonfinite_samples": 0,
        "status": "ok",
        "total_nll": 67054.72902449768,
        "scored_tokens": 156267,
        "mean_nll": 0.42910357928735865,
        "token_weighted_ppl": 1.5358801115260794,
        "mean_answer_tokens": 312.534,
        "source_prompt_truncated_samples": 3,
        "reference_prompt_truncated_samples": 0,
        "generation_configurations": [
          {
            "configuration": {
              "kgw_enabled_during_generation": false,
              "max_new_tokens": 1536,
              "max_prompt_tokens": 2048,
              "temperature": 0.7,
              "top_p": 0.9
            },
            "samples": 500
          }
        ],
        "generation_seeds": {
          "recorded_samples": 500,
          "minimum": 42,
          "maximum": 541,
          "individual_values": "see per-sample immutable records"
        },
        "student_model_paths": [
          "/shared/public_models/Qwen2.5-0.5B"
        ],
        "generation_tokenizer_paths": [
          "/shared/public_models/Qwen2.5-0.5B"
        ],
        "median_per_answer_ppl": 2.5576398946471928,
        "median_samples": 500,
        "median_status": "ok",
        "without_severe_repetition": {
          "samples": 412,
          "valid_samples": 412,
          "skipped_empty_answers": 0,
          "complete": true,
          "nonfinite_samples": 0,
          "status": "ok",
          "total_nll": 44868.67048177123,
          "scored_tokens": 45137,
          "mean_nll": 0.9940552203684612,
          "token_weighted_ppl": 2.702170179562856,
          "mean_answer_tokens": 109.55582524271844,
          "source_prompt_truncated_samples": 1,
          "reference_prompt_truncated_samples": 0,
          "generation_configurations": [
            {
              "configuration": {
                "kgw_enabled_during_generation": false,
                "max_new_tokens": 1536,
                "max_prompt_tokens": 2048,
                "temperature": 0.7,
                "top_p": 0.9
              },
              "samples": 412
            }
          ],
          "generation_seeds": {
            "recorded_samples": 412,
            "minimum": 42,
            "maximum": 541,
            "individual_values": "see per-sample immutable records"
          },
          "student_model_paths": [
            "/shared/public_models/Qwen2.5-0.5B"
          ],
          "generation_tokenizer_paths": [
            "/shared/public_models/Qwen2.5-0.5B"
          ],
          "median_per_answer_ppl": 2.8522532998790773,
          "median_samples": 412,
          "median_status": "ok",
          "num_answers_before": 500,
          "num_answers_retained": 412,
          "num_answers_removed": 88,
          "fraction_answers_removed": 0.176,
          "repetition_threshold": 0.5,
          "comparison": ">",
          "scope": "answer-internal adjacent token pairs; prompt excluded",
          "removed_answer_ids": [
            "dolly-00135",
            "dolly-12241",
            "dolly-07923",
            "dolly-07103",
            "dolly-05608",
            "dolly-07788",
            "dolly-11310",
            "dolly-02097",
            "dolly-03614",
            "dolly-13505",
            "dolly-02580",
            "dolly-08884",
            "dolly-12659",
            "dolly-00420",
            "dolly-11014",
            "dolly-08008",
            "dolly-02186",
            "dolly-00275",
            "dolly-08512",
            "dolly-14060",
            "dolly-01461",
            "dolly-02223",
            "dolly-04949",
            "dolly-08689",
            "dolly-08574",
            "dolly-08406",
            "dolly-04141",
            "dolly-03209",
            "dolly-06227",
            "dolly-11078",
            "dolly-09778",
            "dolly-04856",
            "dolly-13779",
            "dolly-06595",
            "dolly-08936",
            "dolly-09344",
            "dolly-05605",
            "dolly-08340",
            "dolly-04589",
            "dolly-04686",
            "dolly-14700",
            "dolly-03696",
            "dolly-03914",
            "dolly-11987",
            "dolly-01939",
            "dolly-05628",
            "dolly-13339",
            "dolly-08911",
            "dolly-03239",
            "dolly-13445",
            "dolly-02139",
            "dolly-14265",
            "dolly-13610",
            "dolly-07427",
            "dolly-09563",
            "dolly-02451",
            "dolly-13544",
            "dolly-06824",
            "dolly-05312",
            "dolly-10992",
            "dolly-06932",
            "dolly-08607",
            "dolly-05388",
            "dolly-11386",
            "dolly-02069",
            "dolly-09439",
            "dolly-00148",
            "dolly-08211",
            "dolly-12186",
            "dolly-03319",
            "dolly-07407",
            "dolly-10389",
            "dolly-03916",
            "dolly-08222",
            "dolly-14947",
            "dolly-03624",
            "dolly-09330",
            "dolly-11182",
            "dolly-02059",
            "dolly-02916",
            "dolly-09816",
            "dolly-05355",
            "dolly-06970",
            "dolly-05634",
            "dolly-02500",
            "dolly-11314",
            "dolly-13235",
            "dolly-04223"
          ],
          "filtering_source_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.nonrepetitive_grouped_p_values.json",
          "filtering_source_sha256": "597b843d28d31c353c7bb9b94a3b6dccb564cb45ac2c5252f6a1592ccd768efe",
          "filtering_tokenizer": {
            "path": "/shared/public_models/Qwen2.5-14B-Instruct",
            "files_sha256": {
              "config.json": "7362de7db90a1e57fe153e55094e6c2fb7d904a3705d34296ff7de84488235f4",
              "merges.txt": "0de0bc38a29ea38eef099b677fa1ff52edd181e573529af26c4cd2136e233777",
              "tokenizer.json": "47ec9be242d3ef39b9c97ac0a3f06c1752f061b234e295bc0a2842067a3fe4f9",
              "tokenizer_config.json": "fa2a40a9d8c8c4bb7f25ab726eb78ec9cbaaef96d1fa26f1d7f5615e886449a8",
              "vocab.json": "ca10d7e9fb3ed18575dd1e277a2579c16d108e32f27439684afa0e10b1440910"
            }
          }
        },
        "source_path": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl",
        "source_sha256": "597b843d28d31c353c7bb9b94a3b6dccb564cb45ac2c5252f6a1592ccd768efe",
        "per_sample_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.ppl.877fc574f9ee35a5145f.jsonl",
        "cache_reused": true
      }
    }
  },
  "evaluated_at": "2026-10-29T19:45:29+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wm_test/cleanD_dipperparaSFT_dipperparagad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-10-31T16:24:41+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.452822
- 实际检测配置：`{"gamma": 0.5, "hash_key": 15485863, "seeding": "simple_1 (hash_key * previous_token_id)", "delta_by_label": {"kgw": 2.0, "clean": 2.0}}`
- ROUGE-L（同批 500 条原始 Dolly 回答作参考）：0.229593（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 原始 Dolly 参考文件：`/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl`
- ROUGE-L（同批 500 条 14B clean 教师回答作参考）：0.330629（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 14B clean 教师参考文件：`/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_clean_test.parquet`
- Best F1：0.675749（z 阈值 -5.195844985353305，TPR 0.992000，FPR 0.944000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.010000 | 0.002000 | 0.003953 | 9.593834825900782 |
  | 5% | 0.046000 | 0.024000 | 0.044860 | 2.2662573397778742 |
  | 10% | 0.100000 | 0.070000 | 0.119658 | 1.697749375254331 |

### Seq-Rep-3（全量回答，词级三元组重复率）

每条回答单独计算 1 - 不同三元组数 / 全部三元组数，再汇总逐回答算术平均和普通中位数；偶数条的中位数取中间两个值的算术平均。只对 answer 使用 split() 空白分词，保留大小写和标点；不包含 prompt，不跨回答拼接，不剔除严重重复回答，不按长度加权。少于 3 个词（含空回答）按 0 计入，数量单独列出；空回答数包含在短回答数内。数值以 0–1 比例报告。

| 文件组 | 样本数 | Seq-Rep-3 逐回答算术平均 ↓ | Seq-Rep-3 逐回答普通中位数 ↓ | 少于3词回答数 | 空回答数 |
|---|---:|---:|---:|---:|---:|
| kgw | 500 | 0.042492 | 0.013770 | 0 | 0 |
| clean | 500 | 0.159015 | 0.021919 | 1 | 0 |

- kgw: `/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl`；SHA256 `dd4cfdbe540e2227bbad3b46f6a64e34bb1a46b7e7d24860ef8be90ec03efd48`。

- clean: `/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl`；SHA256 `597b843d28d31c353c7bb9b94a3b6dccb564cb45ac2c5252f6a1592ccd768efe`。

两种逐条文本 p-value 统计（单侧正态近似；不是 AUROC 的显著性检验）：

去重规则：相同的 `(previous_token_id, token_id)` 只计一次；不修改回答文本。

| 数据 | 检测方式 | 有效样本 | p 均值 | p 中位数 | p≤0.01 | p≤0.05 | p≤0.10 |
|---|---|---:|---:|---:|---:|---:|---:|
| kgw | 原始 | 500/500 | 0.598076 | 0.670405 | 10 (2.00%) | 35 (7.00%) | 53 (10.60%) |
| kgw | token 对去重 | 500/500 | 0.565465 | 0.608443 | 1 (0.20%) | 15 (3.00%) | 38 (7.60%) |
| clean | 原始 | 500/500 | 0.538121 | 0.57157 | 22 (4.40%) | 54 (10.80%) | 73 (14.60%) |
| clean | token 对去重 | 500/500 | 0.537418 | 0.555154 | 5 (1.00%) | 25 (5.00%) | 46 (9.20%) |

KGW 的小 p 占比是该理论阈值下的检出率，clean 的小 p 占比是实测误报率。p≤0.05 不保证实际 FPR=5%；去重可改善重复带来的失真，但不保证完全校准。空回答不做显著性检验，p=null，并排除在有效样本统计之外。

逐条 p-value：`/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.p_values.jsonl`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl`

固定 token 分组 p-value（普通中位数；p 越大表示原单侧检验证据越弱）：

按教师 tokenizer 编码回答并无分隔拼接，精确分组；每组首 token 仅作上下文，其余 token 用本项目原 KGW 绿表评分；不去重，尾部不足一组丢弃；各组 p 排序后取普通中位数（偶数组取中间两个 p 的算术平均）。

| 每组 token 数 | 计分 token 数 | KGW 组数 | KGW median p ↑ | clean 组数 | clean median p | KGW/clean 丢弃尾部 tokens |
|---:|---:|---:|---:|---:|---:|---:|
| 1000 | 999 | 108 | 0.953214 | 159 | 0.865929 | 189/765 |
| 2000 | 1999 | 54 | 0.972771 | 79 | 0.971358 | 189/1765 |
| 3000 | 2999 | 36 | 0.987652 | 53 | 0.982134 | 189/765 |
| 10000 | 9999 | 10 | 0.999999 | 15 | 1 | 8189/9765 |
| 20000 | 19999 | 5 | 1 | 7 | 1 | 8189/19765 |
| 30000 | 29999 | 3 | 1 | 5 | 1 | 18189/9765 |

N/A 表示总 token 数不足一个完整组；组数为 1 或 2 时需结合逐组结果解释。极小 p 用科学计数法字符串保存，同时保留 log10(p)，避免浮点下溢为 0。

逐组 p-value 缓存：`/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.grouped_p_values.json`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.grouped_p_values.json`

剔除严重重复回答后的固定 token 分组 p-value（普通中位数）：

先独立筛选 KGW 和 clean：回答内部相邻 token 对重复比例严格大于 50% 时，剔除整条回答；prompt 不参与判断。保留回答按原顺序重新无分隔拼接，各组首 token 仅作上下文；组内不做 token 对去重，尾部不足一组丢弃。这是质量筛选补充指标，原始全样本统计另行保留。

| 数据 | 原回答数 | 剔除严重重复回答 | 保留回答数 | 原 tokens | 剔除 tokens | 保留 tokens |
|---|---:|---:|---:|---:|---:|---:|
| kgw | 500 | 11 (2.20%) | 489 | 108189 | 12069 | 96120 |
| clean | 500 | 88 (17.60%) | 412 | 159765 | 113883 | 45882 |

| 每组 token 数 | 计分 token 数 | KGW 组数 | KGW median p ↑ | clean 组数 | clean median p | KGW/clean 丢弃尾部 tokens |
|---:|---:|---:|---:|---:|---:|---:|
| 1000 | 999 | 96 | 0.891381 | 45 | 0.636089 | 120/882 |
| 2000 | 1999 | 48 | 0.982219 | 22 | 0.796038 | 120/1882 |
| 3000 | 2999 | 32 | 0.993787 | 15 | 0.738626 | 120/882 |
| 10000 | 9999 | 9 | 0.999995 | 4 | 0.947597 | 6120/5882 |
| 20000 | 19999 | 4 | 1 | 2 | 0.978374 | 16120/5882 |
| 30000 | 29999 | 3 | 1 | 1 | 0.999568 | 6120/15882 |

N/A 表示筛选后不足一个完整组。各组 p 取普通中位数，偶数组取中间两个 p 的算术平均；组数较少时请结合逐组缓存解释。

剔除严重重复回答后的逐组 p-value 缓存：`/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.nonrepetitive_grouped_p_values.json`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.nonrepetitive_grouped_p_values.json`

### 固定参考模型 PPL（只评分已保存的回答）

| 文件组 | 总体 PPL ↓ | 逐回答 PPL 中位数 ↓ | 剔除严重重复后总体 PPL ↓ | 保留回答数/原回答数 | 有效样本/总样本 | 状态 | 缓存复用 |
|---|---:|---:|---:|---:|---:|---|---|
| kgw | 3.106746 | 3.160327 | 3.227877 | 489/500 | 500/500 | ok | True |
| clean | 1.535880 | 2.557640 | 2.702170 | 412/500 | 500/500 | ok | True |

总体 PPL = exp(全部有效回答 NLL 总和 / 全部计分回答 token 数)，不是逐条 PPL 的算术平均。
逐回答 PPL 中位数对全量有效回答的 PPL 排序；偶数条取中间两个 PPL 的算术平均，不对平均 NLL 取中位数后再 exp。空回答或异常 loss 不计入，并单独报告数量。
剔除严重重复后总体 PPL：复用同源重复筛选缓存，按教师 tokenizer 的回答内部相邻 token 对重复率严格 > 50% 剔除整条回答，prompt 不参与判断；只汇总保留回答原有的参考模型 NLL 和参考 tokenizer token 数。保留回答的文本不变，不删除文内 token，不丢弃尾部。KGW 与 clean 各自筛选，保留回答数含未成功评分回答。N/A 表示未提供筛选，null 表示无可计算数值；筛选后结果是子集统计，全量结果另行保留。
原生成 tokenizer 恢复实际生成 prompt；参考 tokenizer 对 prompt/answer 分开编码后拼接；只计回答，包含首回答 token。Base 参考模型不再套用 chat template；只添加一次参考 BOS，不额外评分 EOS；输入 JSONL 不修改。

- kgw: `/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl`；SHA256 `dd4cfdbe540e2227bbad3b46f6a64e34bb1a46b7e7d24860ef8be90ec03efd48`；逐条明细 `/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.ppl.2fbd37ec395a4c387a8e.jsonl`；空回答 0；异常 loss 0；原生成截断 3；参考上下文截断 0；计分回答 tokens 105228；平均回答 tokens 210.46；中位数样本数 500（状态 ok）。
  剔除严重重复回答 11（2.20%）；保留回答中有效评分 489/489；保留回答计分 tokens 94592；状态 ok；重复筛选缓存 `/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.nonrepetitive_grouped_p_values.json`。

  生成文本配置（种子逐条保存在明细中）：

```json
{
  "student_model_paths": [
    "/shared/wwx/EasyGAD/checkpoints/gad_05b_cleanwarmup_cleangad_control/gad/global_step_1813/actor/huggingface"
  ],
  "generation_tokenizer_paths": [
    "/shared/public_models/Qwen2.5-0.5B"
  ],
  "generation_configurations": [
    {
      "configuration": {
        "kgw_enabled_during_generation": false,
        "max_new_tokens": 1536,
        "max_prompt_tokens": 2048,
        "temperature": 0.7,
        "top_p": 0.9
      },
      "samples": 500
    }
  ],
  "generation_seeds": {
    "recorded_samples": 500,
    "minimum": 42,
    "maximum": 541,
    "individual_values": "see per-sample immutable records"
  }
}
```
- clean: `/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl`；SHA256 `597b843d28d31c353c7bb9b94a3b6dccb564cb45ac2c5252f6a1592ccd768efe`；逐条明细 `/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.ppl.877fc574f9ee35a5145f.jsonl`；空回答 0；异常 loss 0；原生成截断 3；参考上下文截断 0；计分回答 tokens 156267；平均回答 tokens 312.53；中位数样本数 500（状态 ok）。
  剔除严重重复回答 88（17.60%）；保留回答中有效评分 412/412；保留回答计分 tokens 45137；状态 ok；重复筛选缓存 `/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.nonrepetitive_grouped_p_values.json`。

  生成文本配置（种子逐条保存在明细中）：

```json
{
  "student_model_paths": [
    "/shared/public_models/Qwen2.5-0.5B"
  ],
  "generation_tokenizer_paths": [
    "/shared/public_models/Qwen2.5-0.5B"
  ],
  "generation_configurations": [
    {
      "configuration": {
        "kgw_enabled_during_generation": false,
        "max_new_tokens": 1536,
        "max_prompt_tokens": 2048,
        "temperature": 0.7,
        "top_p": 0.9
      },
      "samples": 500
    }
  ],
  "generation_seeds": {
    "recorded_samples": 500,
    "minimum": 42,
    "maximum": 541,
    "individual_values": "see per-sample immutable records"
  }
}
```

完整评分配置（含模型/tokenizer 指纹、软件版本；权重使用 size/mtime 标识，不全量哈希）：

```json
{
  "model_path": "/shared/public_models/Llama-3-8B",
  "device": "cuda",
  "dtype": "bfloat16",
  "generation_tokenizer": "/shared/public_models/Qwen2.5-0.5B",
  "max_length": null,
  "overflow": "error",
  "effective_max_length": 8192,
  "protocol": {
    "prompt": "source-generation-prompt; source chat template, not reference chat template",
    "boundary": "encode prompt and answer separately with add_special_tokens=False, then concatenate",
    "bos": "one reference BOS at start when defined; no extra EOS",
    "loss": "causal next-token NLL on all answer tokens, including the first; no prompt or padding loss",
    "aggregate": "exp(sum(answer NLL) / sum(scored answer tokens)); not mean per-answer PPL",
    "source_tokenizer_selection": "explicit override, otherwise row.model_path; fallback assumes the generation tokenizer matches that checkpoint",
    "legacy_prompt_limit": 2048,
    "weights_fingerprint": "weight filenames, sizes and mtime_ns; weight contents are not hashed"
  },
  "reference_assets": {
    "path": "/shared/public_models/Llama-3-8B",
    "assets": [
      {
        "name": "config.json",
        "size": 654,
        "sha256": "2430cee764b6530ff8673cf9ba8561e1d5a33152d503cd0de909ff5718261441"
      },
      {
        "name": "generation_config.json",
        "size": 126,
        "sha256": "55550e95c40c53fb0ee3f960d6d2b25a46405c8f790e5c4bb02caf3e98f2b5d0"
      },
      {
        "name": "model.safetensors.index.json",
        "size": 23950,
        "sha256": "146776fce3f6db1103aa6f249e65ee5544c5923ce6f971b092eee79aa6e5d37b"
      },
      {
        "name": "special_tokens_map.json",
        "size": 73,
        "sha256": "462d91939dbc37178aa5a3eae7068d1990ccc92e09f288cc71f42cdf139d69cc"
      },
      {
        "name": "tokenizer.json",
        "size": 9085698,
        "sha256": "e134af98b985517b4f068e3755ae90d4e9cd2d45d328325dc503f1c6b2d06cc7"
      },
      {
        "name": "tokenizer_config.json",
        "size": 50566,
        "sha256": "690727b4fed286383df1c7ca5e805124cb70c6eb4529f807c7b2e60ff741da7e"
      }
    ],
    "weight_stats": [
      {
        "name": "model-00001-of-00004.safetensors",
        "size": 4976698672,
        "mtime_ns": 1736746522477644778
      },
      {
        "name": "model-00002-of-00004.safetensors",
        "size": 4999802720,
        "mtime_ns": 1736746656058650226
      },
      {
        "name": "model-00003-of-00004.safetensors",
        "size": 4915916176,
        "mtime_ns": 1736746768408654808
      },
      {
        "name": "model-00004-of-00004.safetensors",
        "size": 1168138808,
        "mtime_ns": 1736746796088655937
      }
    ],
    "weight_content_hashed": false
  },
  "software": {
    "python": "3.10.21",
    "torch": "2.6.0",
    "transformers": "4.51.3",
    "tokenizers": "0.21.4"
  }
}
```

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.45282199999999984,
  "best_f1": {
    "threshold": -5.195844985353305,
    "fpr": 0.944,
    "tpr": 0.992,
    "precision": 0.512396694214876,
    "f1": 0.6757493188010898,
    "tp": 496,
    "fp": 472,
    "tn": 28,
    "fn": 4
  },
  "tpr_at_fpr": {
    "1%": {
      "threshold": 9.593834825900782,
      "fpr": 0.01,
      "tpr": 0.002,
      "precision": 0.16666666666666666,
      "f1": 0.003952569169960474,
      "tp": 1,
      "fp": 5,
      "tn": 495,
      "fn": 499,
      "target_fpr": 0.01
    },
    "5%": {
      "threshold": 2.2662573397778742,
      "fpr": 0.046,
      "tpr": 0.024,
      "precision": 0.34285714285714286,
      "f1": 0.044859813084112146,
      "tp": 12,
      "fp": 23,
      "tn": 477,
      "fn": 488,
      "target_fpr": 0.05
    },
    "10%": {
      "threshold": 1.697749375254331,
      "fpr": 0.1,
      "tpr": 0.07,
      "precision": 0.4117647058823529,
      "f1": 0.11965811965811966,
      "tp": 35,
      "fp": 50,
      "tn": 450,
      "fn": 465,
      "target_fpr": 0.1
    }
  },
  "note": "For each target FPR, select the empirical ROC point with the highest TPR whose FPR does not exceed the target; tied scores are kept together.",
  "detector_config": {
    "gamma": 0.5,
    "hash_key": 15485863,
    "seeding": "simple_1 (hash_key * previous_token_id)",
    "delta_by_label": {
      "kgw": 2.0,
      "clean": 2.0
    }
  },
  "rouge_l_dolly": {
    "mean": 0.2295929496951247,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl",
    "reference_file": "/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl",
    "reference_source": "databricks/databricks-dolly-15k:response",
    "metric": "rougeL",
    "measure": "fmeasure",
    "use_stemmer": true,
    "aggregation": "unweighted mean of per-sample ROUGE-L F1"
  },
  "rouge_l_teacher_clean": {
    "mean": 0.33062936890217354,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl",
    "reference_file": "/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_clean_test.parquet",
    "reference_source": "Qwen2.5-14B clean teacher responses",
    "metric": "rougeL",
    "measure": "fmeasure",
    "use_stemmer": true,
    "aggregation": "unweighted mean of per-sample ROUGE-L F1"
  },
  "seq_rep_3": {
    "kgw": {
      "mean": 0.0424920159990153,
      "median": 0.013770383010997311,
      "num_samples": 500,
      "num_short_answers": 0,
      "num_empty_answers": 0,
      "evaluated_file": "/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl",
      "source_sha256": "dd4cfdbe540e2227bbad3b46f6a64e34bb1a46b7e7d24860ef8be90ec03efd48",
      "ngram_size": 3,
      "tokenization": "answer.split(); whitespace-delimited words; case and punctuation preserved",
      "scope": "answer only; overlapping trigrams within each complete original answer; no filtering or cross-answer trigrams",
      "short_answer_policy": "answers with fewer than 3 words, including empty answers, contribute 0; counts reported",
      "aggregation": {
        "mean": "unweighted arithmetic mean of per-answer Seq-Rep-3",
        "median": "ordinary median of per-answer Seq-Rep-3; arithmetic mean of the middle two for even counts"
      }
    },
    "clean": {
      "mean": 0.15901538183339659,
      "median": 0.021919288974297402,
      "num_samples": 500,
      "num_short_answers": 1,
      "num_empty_answers": 0,
      "evaluated_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl",
      "source_sha256": "597b843d28d31c353c7bb9b94a3b6dccb564cb45ac2c5252f6a1592ccd768efe",
      "ngram_size": 3,
      "tokenization": "answer.split(); whitespace-delimited words; case and punctuation preserved",
      "scope": "answer only; overlapping trigrams within each complete original answer; no filtering or cross-answer trigrams",
      "short_answer_policy": "answers with fewer than 3 words, including empty answers, contribute 0; counts reported",
      "aggregation": {
        "mean": "unweighted arithmetic mean of per-answer Seq-Rep-3",
        "median": "ordinary median of per-answer Seq-Rep-3; arithmetic mean of the middle two for even counts"
      }
    }
  },
  "p_values": {
    "kgw": {
      "raw": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.5980756128415708,
        "median": 0.6704045868001102,
        "min": 4.243529073241433e-22,
        "max": 1.0,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 10,
            "fraction": 0.02
          },
          "5%": {
            "alpha": 0.05,
            "count": 35,
            "fraction": 0.07
          },
          "10%": {
            "alpha": 0.1,
            "count": 53,
            "fraction": 0.106
          }
        }
      },
      "deduplicated": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.5654645905266942,
        "median": 0.6084433058368692,
        "min": 0.007646685515099473,
        "max": 0.9979483607953694,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 1,
            "fraction": 0.002
          },
          "5%": {
            "alpha": 0.05,
            "count": 15,
            "fraction": 0.03
          },
          "10%": {
            "alpha": 0.1,
            "count": 38,
            "fraction": 0.076
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
    "kgw": "/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.p_values.jsonl",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl"
  },
  "grouped_p_values": {
    "kgw": {
      "aggregation": "ordinary_median",
      "num_answers": 500,
      "total_answer_tokens": 108189,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 108,
          "total_answer_tokens": 108189,
          "discarded_tail_tokens": 189,
          "median_p_value": 0.9532136797396964,
          "median_log10_p_value": -0.02080973364321328,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 54,
          "total_answer_tokens": 108189,
          "discarded_tail_tokens": 189,
          "median_p_value": 0.9727708620407867,
          "median_log10_p_value": -0.011989446546280093,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 36,
          "total_answer_tokens": 108189,
          "discarded_tail_tokens": 189,
          "median_p_value": 0.98765196739754,
          "median_log10_p_value": -0.005396066816028589,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 10,
          "total_answer_tokens": 108189,
          "discarded_tail_tokens": 8189,
          "median_p_value": 0.9999992426252889,
          "median_log10_p_value": -3.289237823092744e-07,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 5,
          "total_answer_tokens": 108189,
          "discarded_tail_tokens": 8189,
          "median_p_value": 0.9999999999999999,
          "median_log10_p_value": -4.8216373327664354e-17,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 3,
          "total_answer_tokens": 108189,
          "discarded_tail_tokens": 18189,
          "median_p_value": 0.9999999999998027,
          "median_log10_p_value": -8.5680495403268e-14,
          "status": "ok"
        }
      }
    },
    "clean": {
      "aggregation": "ordinary_median",
      "num_answers": 500,
      "total_answer_tokens": 159765,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 159,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 765,
          "median_p_value": 0.8659288977499955,
          "median_log10_p_value": -0.06251776685396769,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 79,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 1765,
          "median_p_value": 0.971357711016285,
          "median_log10_p_value": -0.012620807875598238,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 53,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 765,
          "median_p_value": 0.9821335190767914,
          "median_log10_p_value": -0.007829466737979084,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 15,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 9765,
          "median_p_value": 0.9999999999999984,
          "median_log10_p_value": -6.750292265873014e-16,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 7,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 19765,
          "median_p_value": 1.0,
          "median_log10_p_value": 0.0,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 5,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 9765,
          "median_p_value": 1.0,
          "median_log10_p_value": 0.0,
          "status": "ok"
        }
      }
    }
  },
  "grouped_p_value_method": "teacher-tokenizer answer IDs concatenated without separators; exact disjoint blocks; first token of each block is context only; no repetition deduplication; incomplete tail discarded; ordinary median of block p-values (arithmetic mean of the two middle p-values for even group counts)",
  "per_group_p_value_files": {
    "kgw": "/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.grouped_p_values.json",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.grouped_p_values.json"
  },
  "grouped_p_values_without_severe_repetition": {
    "kgw": {
      "aggregation": "ordinary_median",
      "num_answers": 489,
      "total_answer_tokens": 96120,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 96,
          "total_answer_tokens": 96120,
          "discarded_tail_tokens": 120,
          "median_p_value": 0.8913809204225676,
          "median_log10_p_value": -0.04993666601367001,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 48,
          "total_answer_tokens": 96120,
          "discarded_tail_tokens": 120,
          "median_p_value": 0.9822191552453498,
          "median_log10_p_value": -0.007791600507575589,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 32,
          "total_answer_tokens": 96120,
          "discarded_tail_tokens": 120,
          "median_p_value": 0.993786531657336,
          "median_log10_p_value": -0.0027068933487222604,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 9,
          "total_answer_tokens": 96120,
          "discarded_tail_tokens": 6120,
          "median_p_value": 0.9999948367296856,
          "median_log10_p_value": -2.2423855951505638e-06,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 4,
          "total_answer_tokens": 96120,
          "discarded_tail_tokens": 16120,
          "median_p_value": 0.9999999999971494,
          "median_log10_p_value": -1.2379553851888302e-12,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 3,
          "total_answer_tokens": 96120,
          "discarded_tail_tokens": 6120,
          "median_p_value": 0.9999999999836495,
          "median_log10_p_value": -7.100921732769837e-12,
          "status": "ok"
        }
      },
      "filtering": {
        "repetition_threshold": 0.5,
        "comparison": ">",
        "scope": "answer-internal adjacent token pairs; prompt excluded",
        "num_answers_before": 500,
        "num_answers_retained": 489,
        "num_answers_removed": 11,
        "fraction_answers_removed": 0.022,
        "total_answer_tokens_before": 108189,
        "total_answer_tokens_retained": 96120,
        "total_answer_tokens_removed": 12069,
        "removed_answer_ids": [
          "dolly-08884",
          "dolly-09935",
          "dolly-04624",
          "dolly-14700",
          "dolly-08911",
          "dolly-13445",
          "dolly-02451",
          "dolly-08607",
          "dolly-11386",
          "dolly-12065",
          "dolly-01739"
        ]
      }
    },
    "clean": {
      "aggregation": "ordinary_median",
      "num_answers": 412,
      "total_answer_tokens": 45882,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 45,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 882,
          "median_p_value": 0.6360891449864364,
          "median_log10_p_value": -0.1964820156995508,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 22,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 1882,
          "median_p_value": 0.7960378878131416,
          "median_log10_p_value": -0.09906626131183685,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 15,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 882,
          "median_p_value": 0.7386263221105359,
          "median_log10_p_value": -0.13157521964243946,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 4,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 5882,
          "median_p_value": 0.947596846602552,
          "median_log10_p_value": -0.0233763931850151,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 2,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 5882,
          "median_p_value": 0.9783739864832501,
          "median_log10_p_value": -0.009495103065976066,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 1,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 15882,
          "median_p_value": 0.9995678964162934,
          "median_log10_p_value": -0.00018770075802065225,
          "status": "ok"
        }
      },
      "filtering": {
        "repetition_threshold": 0.5,
        "comparison": ">",
        "scope": "answer-internal adjacent token pairs; prompt excluded",
        "num_answers_before": 500,
        "num_answers_retained": 412,
        "num_answers_removed": 88,
        "fraction_answers_removed": 0.176,
        "total_answer_tokens_before": 159765,
        "total_answer_tokens_retained": 45882,
        "total_answer_tokens_removed": 113883,
        "removed_answer_ids": [
          "dolly-00135",
          "dolly-12241",
          "dolly-07923",
          "dolly-07103",
          "dolly-05608",
          "dolly-07788",
          "dolly-11310",
          "dolly-02097",
          "dolly-03614",
          "dolly-13505",
          "dolly-02580",
          "dolly-08884",
          "dolly-12659",
          "dolly-00420",
          "dolly-11014",
          "dolly-08008",
          "dolly-02186",
          "dolly-00275",
          "dolly-08512",
          "dolly-14060",
          "dolly-01461",
          "dolly-02223",
          "dolly-04949",
          "dolly-08689",
          "dolly-08574",
          "dolly-08406",
          "dolly-04141",
          "dolly-03209",
          "dolly-06227",
          "dolly-11078",
          "dolly-09778",
          "dolly-04856",
          "dolly-13779",
          "dolly-06595",
          "dolly-08936",
          "dolly-09344",
          "dolly-05605",
          "dolly-08340",
          "dolly-04589",
          "dolly-04686",
          "dolly-14700",
          "dolly-03696",
          "dolly-03914",
          "dolly-11987",
          "dolly-01939",
          "dolly-05628",
          "dolly-13339",
          "dolly-08911",
          "dolly-03239",
          "dolly-13445",
          "dolly-02139",
          "dolly-14265",
          "dolly-13610",
          "dolly-07427",
          "dolly-09563",
          "dolly-02451",
          "dolly-13544",
          "dolly-06824",
          "dolly-05312",
          "dolly-10992",
          "dolly-06932",
          "dolly-08607",
          "dolly-05388",
          "dolly-11386",
          "dolly-02069",
          "dolly-09439",
          "dolly-00148",
          "dolly-08211",
          "dolly-12186",
          "dolly-03319",
          "dolly-07407",
          "dolly-10389",
          "dolly-03916",
          "dolly-08222",
          "dolly-14947",
          "dolly-03624",
          "dolly-09330",
          "dolly-11182",
          "dolly-02059",
          "dolly-02916",
          "dolly-09816",
          "dolly-05355",
          "dolly-06970",
          "dolly-05634",
          "dolly-02500",
          "dolly-11314",
          "dolly-13235",
          "dolly-04223"
        ]
      }
    }
  },
  "grouped_p_value_without_severe_repetition_method": "exclude whole answers whose answer-internal adjacent-token-pair repetition ratio (1 - unique pairs / all pairs) is strictly greater than 0.5; prompts excluded from repetition assessment; filter each label independently; retain original answer order, then concatenate teacher-tokenizer answer IDs without separators; exact disjoint blocks, first token context only; no token-pair deduplication within retained blocks; incomplete tail discarded; ordinary median of block p-values (mean of the middle two for even counts)",
  "per_group_p_value_without_severe_repetition_files": {
    "kgw": "/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.nonrepetitive_grouped_p_values.json",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.nonrepetitive_grouped_p_values.json"
  },
  "ppl": {
    "enabled": true,
    "schema": "saved-answer-reference-ppl-v1",
    "configuration": {
      "model_path": "/shared/public_models/Llama-3-8B",
      "device": "cuda",
      "dtype": "bfloat16",
      "generation_tokenizer": "/shared/public_models/Qwen2.5-0.5B",
      "max_length": null,
      "overflow": "error",
      "effective_max_length": 8192,
      "protocol": {
        "prompt": "source-generation-prompt; source chat template, not reference chat template",
        "boundary": "encode prompt and answer separately with add_special_tokens=False, then concatenate",
        "bos": "one reference BOS at start when defined; no extra EOS",
        "loss": "causal next-token NLL on all answer tokens, including the first; no prompt or padding loss",
        "aggregate": "exp(sum(answer NLL) / sum(scored answer tokens)); not mean per-answer PPL",
        "source_tokenizer_selection": "explicit override, otherwise row.model_path; fallback assumes the generation tokenizer matches that checkpoint",
        "legacy_prompt_limit": 2048,
        "weights_fingerprint": "weight filenames, sizes and mtime_ns; weight contents are not hashed"
      },
      "reference_assets": {
        "path": "/shared/public_models/Llama-3-8B",
        "assets": [
          {
            "name": "config.json",
            "size": 654,
            "sha256": "2430cee764b6530ff8673cf9ba8561e1d5a33152d503cd0de909ff5718261441"
          },
          {
            "name": "generation_config.json",
            "size": 126,
            "sha256": "55550e95c40c53fb0ee3f960d6d2b25a46405c8f790e5c4bb02caf3e98f2b5d0"
          },
          {
            "name": "model.safetensors.index.json",
            "size": 23950,
            "sha256": "146776fce3f6db1103aa6f249e65ee5544c5923ce6f971b092eee79aa6e5d37b"
          },
          {
            "name": "special_tokens_map.json",
            "size": 73,
            "sha256": "462d91939dbc37178aa5a3eae7068d1990ccc92e09f288cc71f42cdf139d69cc"
          },
          {
            "name": "tokenizer.json",
            "size": 9085698,
            "sha256": "e134af98b985517b4f068e3755ae90d4e9cd2d45d328325dc503f1c6b2d06cc7"
          },
          {
            "name": "tokenizer_config.json",
            "size": 50566,
            "sha256": "690727b4fed286383df1c7ca5e805124cb70c6eb4529f807c7b2e60ff741da7e"
          }
        ],
        "weight_stats": [
          {
            "name": "model-00001-of-00004.safetensors",
            "size": 4976698672,
            "mtime_ns": 1736746522477644778
          },
          {
            "name": "model-00002-of-00004.safetensors",
            "size": 4999802720,
            "mtime_ns": 1736746656058650226
          },
          {
            "name": "model-00003-of-00004.safetensors",
            "size": 4915916176,
            "mtime_ns": 1736746768408654808
          },
          {
            "name": "model-00004-of-00004.safetensors",
            "size": 1168138808,
            "mtime_ns": 1736746796088655937
          }
        ],
        "weight_content_hashed": false
      },
      "software": {
        "python": "3.10.21",
        "torch": "2.6.0",
        "transformers": "4.51.3",
        "tokenizers": "0.21.4"
      }
    },
    "files": {
      "kgw": {
        "samples": 500,
        "valid_samples": 500,
        "skipped_empty_answers": 0,
        "complete": true,
        "nonfinite_samples": 0,
        "status": "ok",
        "total_nll": 119283.93737233058,
        "scored_tokens": 105228,
        "mean_nll": 1.1335760194276292,
        "token_weighted_ppl": 3.1067464450215216,
        "mean_answer_tokens": 210.456,
        "source_prompt_truncated_samples": 3,
        "reference_prompt_truncated_samples": 0,
        "generation_configurations": [
          {
            "configuration": {
              "kgw_enabled_during_generation": false,
              "max_new_tokens": 1536,
              "max_prompt_tokens": 2048,
              "temperature": 0.7,
              "top_p": 0.9
            },
            "samples": 500
          }
        ],
        "generation_seeds": {
          "recorded_samples": 500,
          "minimum": 42,
          "maximum": 541,
          "individual_values": "see per-sample immutable records"
        },
        "student_model_paths": [
          "/shared/wwx/EasyGAD/checkpoints/gad_05b_cleanwarmup_cleangad_control/gad/global_step_1813/actor/huggingface"
        ],
        "generation_tokenizer_paths": [
          "/shared/public_models/Qwen2.5-0.5B"
        ],
        "median_per_answer_ppl": 3.16032674637607,
        "median_samples": 500,
        "median_status": "ok",
        "without_severe_repetition": {
          "samples": 489,
          "valid_samples": 489,
          "skipped_empty_answers": 0,
          "complete": true,
          "nonfinite_samples": 0,
          "status": "ok",
          "total_nll": 110845.23477697,
          "scored_tokens": 94592,
          "mean_nll": 1.1718246234033534,
          "token_weighted_ppl": 3.2278769283761526,
          "mean_answer_tokens": 193.439672801636,
          "source_prompt_truncated_samples": 2,
          "reference_prompt_truncated_samples": 0,
          "generation_configurations": [
            {
              "configuration": {
                "kgw_enabled_during_generation": false,
                "max_new_tokens": 1536,
                "max_prompt_tokens": 2048,
                "temperature": 0.7,
                "top_p": 0.9
              },
              "samples": 489
            }
          ],
          "generation_seeds": {
            "recorded_samples": 489,
            "minimum": 42,
            "maximum": 541,
            "individual_values": "see per-sample immutable records"
          },
          "student_model_paths": [
            "/shared/wwx/EasyGAD/checkpoints/gad_05b_cleanwarmup_cleangad_control/gad/global_step_1813/actor/huggingface"
          ],
          "generation_tokenizer_paths": [
            "/shared/public_models/Qwen2.5-0.5B"
          ],
          "median_per_answer_ppl": 3.177512127385817,
          "median_samples": 489,
          "median_status": "ok",
          "num_answers_before": 500,
          "num_answers_retained": 489,
          "num_answers_removed": 11,
          "fraction_answers_removed": 0.022,
          "repetition_threshold": 0.5,
          "comparison": ">",
          "scope": "answer-internal adjacent token pairs; prompt excluded",
          "removed_answer_ids": [
            "dolly-08884",
            "dolly-09935",
            "dolly-04624",
            "dolly-14700",
            "dolly-08911",
            "dolly-13445",
            "dolly-02451",
            "dolly-08607",
            "dolly-11386",
            "dolly-12065",
            "dolly-01739"
          ],
          "filtering_source_file": "/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.nonrepetitive_grouped_p_values.json",
          "filtering_source_sha256": "dd4cfdbe540e2227bbad3b46f6a64e34bb1a46b7e7d24860ef8be90ec03efd48",
          "filtering_tokenizer": {
            "path": "/shared/public_models/Qwen2.5-14B-Instruct",
            "files_sha256": {
              "config.json": "7362de7db90a1e57fe153e55094e6c2fb7d904a3705d34296ff7de84488235f4",
              "merges.txt": "0de0bc38a29ea38eef099b677fa1ff52edd181e573529af26c4cd2136e233777",
              "tokenizer.json": "47ec9be242d3ef39b9c97ac0a3f06c1752f061b234e295bc0a2842067a3fe4f9",
              "tokenizer_config.json": "fa2a40a9d8c8c4bb7f25ab726eb78ec9cbaaef96d1fa26f1d7f5615e886449a8",
              "vocab.json": "ca10d7e9fb3ed18575dd1e277a2579c16d108e32f27439684afa0e10b1440910"
            }
          }
        },
        "source_path": "/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl",
        "source_sha256": "dd4cfdbe540e2227bbad3b46f6a64e34bb1a46b7e7d24860ef8be90ec03efd48",
        "per_sample_file": "/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.ppl.2fbd37ec395a4c387a8e.jsonl",
        "cache_reused": true
      },
      "clean": {
        "samples": 500,
        "valid_samples": 500,
        "skipped_empty_answers": 0,
        "complete": true,
        "nonfinite_samples": 0,
        "status": "ok",
        "total_nll": 67054.72902449768,
        "scored_tokens": 156267,
        "mean_nll": 0.42910357928735865,
        "token_weighted_ppl": 1.5358801115260794,
        "mean_answer_tokens": 312.534,
        "source_prompt_truncated_samples": 3,
        "reference_prompt_truncated_samples": 0,
        "generation_configurations": [
          {
            "configuration": {
              "kgw_enabled_during_generation": false,
              "max_new_tokens": 1536,
              "max_prompt_tokens": 2048,
              "temperature": 0.7,
              "top_p": 0.9
            },
            "samples": 500
          }
        ],
        "generation_seeds": {
          "recorded_samples": 500,
          "minimum": 42,
          "maximum": 541,
          "individual_values": "see per-sample immutable records"
        },
        "student_model_paths": [
          "/shared/public_models/Qwen2.5-0.5B"
        ],
        "generation_tokenizer_paths": [
          "/shared/public_models/Qwen2.5-0.5B"
        ],
        "median_per_answer_ppl": 2.5576398946471928,
        "median_samples": 500,
        "median_status": "ok",
        "without_severe_repetition": {
          "samples": 412,
          "valid_samples": 412,
          "skipped_empty_answers": 0,
          "complete": true,
          "nonfinite_samples": 0,
          "status": "ok",
          "total_nll": 44868.67048177123,
          "scored_tokens": 45137,
          "mean_nll": 0.9940552203684612,
          "token_weighted_ppl": 2.702170179562856,
          "mean_answer_tokens": 109.55582524271844,
          "source_prompt_truncated_samples": 1,
          "reference_prompt_truncated_samples": 0,
          "generation_configurations": [
            {
              "configuration": {
                "kgw_enabled_during_generation": false,
                "max_new_tokens": 1536,
                "max_prompt_tokens": 2048,
                "temperature": 0.7,
                "top_p": 0.9
              },
              "samples": 412
            }
          ],
          "generation_seeds": {
            "recorded_samples": 412,
            "minimum": 42,
            "maximum": 541,
            "individual_values": "see per-sample immutable records"
          },
          "student_model_paths": [
            "/shared/public_models/Qwen2.5-0.5B"
          ],
          "generation_tokenizer_paths": [
            "/shared/public_models/Qwen2.5-0.5B"
          ],
          "median_per_answer_ppl": 2.8522532998790773,
          "median_samples": 412,
          "median_status": "ok",
          "num_answers_before": 500,
          "num_answers_retained": 412,
          "num_answers_removed": 88,
          "fraction_answers_removed": 0.176,
          "repetition_threshold": 0.5,
          "comparison": ">",
          "scope": "answer-internal adjacent token pairs; prompt excluded",
          "removed_answer_ids": [
            "dolly-00135",
            "dolly-12241",
            "dolly-07923",
            "dolly-07103",
            "dolly-05608",
            "dolly-07788",
            "dolly-11310",
            "dolly-02097",
            "dolly-03614",
            "dolly-13505",
            "dolly-02580",
            "dolly-08884",
            "dolly-12659",
            "dolly-00420",
            "dolly-11014",
            "dolly-08008",
            "dolly-02186",
            "dolly-00275",
            "dolly-08512",
            "dolly-14060",
            "dolly-01461",
            "dolly-02223",
            "dolly-04949",
            "dolly-08689",
            "dolly-08574",
            "dolly-08406",
            "dolly-04141",
            "dolly-03209",
            "dolly-06227",
            "dolly-11078",
            "dolly-09778",
            "dolly-04856",
            "dolly-13779",
            "dolly-06595",
            "dolly-08936",
            "dolly-09344",
            "dolly-05605",
            "dolly-08340",
            "dolly-04589",
            "dolly-04686",
            "dolly-14700",
            "dolly-03696",
            "dolly-03914",
            "dolly-11987",
            "dolly-01939",
            "dolly-05628",
            "dolly-13339",
            "dolly-08911",
            "dolly-03239",
            "dolly-13445",
            "dolly-02139",
            "dolly-14265",
            "dolly-13610",
            "dolly-07427",
            "dolly-09563",
            "dolly-02451",
            "dolly-13544",
            "dolly-06824",
            "dolly-05312",
            "dolly-10992",
            "dolly-06932",
            "dolly-08607",
            "dolly-05388",
            "dolly-11386",
            "dolly-02069",
            "dolly-09439",
            "dolly-00148",
            "dolly-08211",
            "dolly-12186",
            "dolly-03319",
            "dolly-07407",
            "dolly-10389",
            "dolly-03916",
            "dolly-08222",
            "dolly-14947",
            "dolly-03624",
            "dolly-09330",
            "dolly-11182",
            "dolly-02059",
            "dolly-02916",
            "dolly-09816",
            "dolly-05355",
            "dolly-06970",
            "dolly-05634",
            "dolly-02500",
            "dolly-11314",
            "dolly-13235",
            "dolly-04223"
          ],
          "filtering_source_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.nonrepetitive_grouped_p_values.json",
          "filtering_source_sha256": "597b843d28d31c353c7bb9b94a3b6dccb564cb45ac2c5252f6a1592ccd768efe",
          "filtering_tokenizer": {
            "path": "/shared/public_models/Qwen2.5-14B-Instruct",
            "files_sha256": {
              "config.json": "7362de7db90a1e57fe153e55094e6c2fb7d904a3705d34296ff7de84488235f4",
              "merges.txt": "0de0bc38a29ea38eef099b677fa1ff52edd181e573529af26c4cd2136e233777",
              "tokenizer.json": "47ec9be242d3ef39b9c97ac0a3f06c1752f061b234e295bc0a2842067a3fe4f9",
              "tokenizer_config.json": "fa2a40a9d8c8c4bb7f25ab726eb78ec9cbaaef96d1fa26f1d7f5615e886449a8",
              "vocab.json": "ca10d7e9fb3ed18575dd1e277a2579c16d108e32f27439684afa0e10b1440910"
            }
          }
        },
        "source_path": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl",
        "source_sha256": "597b843d28d31c353c7bb9b94a3b6dccb564cb45ac2c5252f6a1592ccd768efe",
        "per_sample_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.ppl.877fc574f9ee35a5145f.jsonl",
        "cache_reused": true
      }
    }
  },
  "evaluated_at": "2026-10-31T16:24:41+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```

## 评估记录：2026-10-31T16:25:01+08:00

- 样本数：KGW 500，clean 500
- AUROC：0.462604
- 实际检测配置：`{"gamma": 0.5, "hash_key": 15485863, "seeding": "simple_1 (hash_key * previous_token_id)", "delta_by_label": {"kgw": 2.0, "clean": 2.0}}`
- ROUGE-L（同批 500 条原始 Dolly 回答作参考）：0.209115（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 原始 Dolly 参考文件：`/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl`
- ROUGE-L（同批 500 条 14B clean 教师回答作参考）：0.309962（KGW 文件中的采样回答，逐条 F1 平均，use_stemmer=True）
- 14B clean 教师参考文件：`/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_clean_test.parquet`
- Best F1：0.678450（z 阈值 -5.03309510460972，TPR 0.998000，FPR 0.944000）
- TPR@FPR 及该工作点的 F1：

  | 目标 FPR | 实际 FPR | TPR | F1 | z 阈值 |
  |---:|---:|---:|---:|---:|
  | 1% | 0.000000 | 0.000000 | 0.000000 | None |
  | 5% | 0.050000 | 0.030000 | 0.055556 | 2.2283440581246223 |
  | 10% | 0.100000 | 0.070000 | 0.119658 | 1.7008401285415224 |

### Seq-Rep-3（全量回答，词级三元组重复率）

每条回答单独计算 1 - 不同三元组数 / 全部三元组数，再汇总逐回答算术平均和普通中位数；偶数条的中位数取中间两个值的算术平均。只对 answer 使用 split() 空白分词，保留大小写和标点；不包含 prompt，不跨回答拼接，不剔除严重重复回答，不按长度加权。少于 3 个词（含空回答）按 0 计入，数量单独列出；空回答数包含在短回答数内。数值以 0–1 比例报告。

| 文件组 | 样本数 | Seq-Rep-3 逐回答算术平均 ↓ | Seq-Rep-3 逐回答普通中位数 ↓ | 少于3词回答数 | 空回答数 |
|---|---:|---:|---:|---:|---:|
| kgw | 500 | 0.053141 | 0.025975 | 1 | 0 |
| clean | 500 | 0.159015 | 0.021919 | 1 | 0 |

- kgw: `/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl`；SHA256 `a544802bd1d1b310dec9bb254958b3386c3692ae848346b77eb36bfe64d96c74`。

- clean: `/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl`；SHA256 `597b843d28d31c353c7bb9b94a3b6dccb564cb45ac2c5252f6a1592ccd768efe`。

两种逐条文本 p-value 统计（单侧正态近似；不是 AUROC 的显著性检验）：

去重规则：相同的 `(previous_token_id, token_id)` 只计一次；不修改回答文本。

| 数据 | 检测方式 | 有效样本 | p 均值 | p 中位数 | p≤0.01 | p≤0.05 | p≤0.10 |
|---|---|---:|---:|---:|---:|---:|---:|
| kgw | 原始 | 500/500 | 0.587914 | 0.658361 | 11 (2.20%) | 36 (7.20%) | 55 (11.00%) |
| kgw | token 对去重 | 500/500 | 0.561811 | 0.599669 | 2 (0.40%) | 22 (4.40%) | 35 (7.00%) |
| clean | 原始 | 500/500 | 0.538121 | 0.57157 | 22 (4.40%) | 54 (10.80%) | 73 (14.60%) |
| clean | token 对去重 | 500/500 | 0.537418 | 0.555154 | 5 (1.00%) | 25 (5.00%) | 46 (9.20%) |

KGW 的小 p 占比是该理论阈值下的检出率，clean 的小 p 占比是实测误报率。p≤0.05 不保证实际 FPR=5%；去重可改善重复带来的失真，但不保证完全校准。空回答不做显著性检验，p=null，并排除在有效样本统计之外。

逐条 p-value：`/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.p_values.jsonl`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl`

固定 token 分组 p-value（普通中位数；p 越大表示原单侧检验证据越弱）：

按教师 tokenizer 编码回答并无分隔拼接，精确分组；每组首 token 仅作上下文，其余 token 用本项目原 KGW 绿表评分；不去重，尾部不足一组丢弃；各组 p 排序后取普通中位数（偶数组取中间两个 p 的算术平均）。

| 每组 token 数 | 计分 token 数 | KGW 组数 | KGW median p ↑ | clean 组数 | clean median p | KGW/clean 丢弃尾部 tokens |
|---:|---:|---:|---:|---:|---:|---:|
| 1000 | 999 | 110 | 0.851774 | 159 | 0.865929 | 315/765 |
| 2000 | 1999 | 55 | 0.968302 | 79 | 0.971358 | 315/1765 |
| 3000 | 2999 | 36 | 0.980464 | 53 | 0.982134 | 2315/765 |
| 10000 | 9999 | 11 | 0.997949 | 15 | 1 | 315/9765 |
| 20000 | 19999 | 5 | 1 | 7 | 1 | 10315/19765 |
| 30000 | 29999 | 3 | 1 | 5 | 1 | 20315/9765 |

N/A 表示总 token 数不足一个完整组；组数为 1 或 2 时需结合逐组结果解释。极小 p 用科学计数法字符串保存，同时保留 log10(p)，避免浮点下溢为 0。

逐组 p-value 缓存：`/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.grouped_p_values.json`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.grouped_p_values.json`

剔除严重重复回答后的固定 token 分组 p-value（普通中位数）：

先独立筛选 KGW 和 clean：回答内部相邻 token 对重复比例严格大于 50% 时，剔除整条回答；prompt 不参与判断。保留回答按原顺序重新无分隔拼接，各组首 token 仅作上下文；组内不做 token 对去重，尾部不足一组丢弃。这是质量筛选补充指标，原始全样本统计另行保留。

| 数据 | 原回答数 | 剔除严重重复回答 | 保留回答数 | 原 tokens | 剔除 tokens | 保留 tokens |
|---|---:|---:|---:|---:|---:|---:|
| kgw | 500 | 15 (3.00%) | 485 | 110315 | 10798 | 99517 |
| clean | 500 | 88 (17.60%) | 412 | 159765 | 113883 | 45882 |

| 每组 token 数 | 计分 token 数 | KGW 组数 | KGW median p ↑ | clean 组数 | clean median p | KGW/clean 丢弃尾部 tokens |
|---:|---:|---:|---:|---:|---:|---:|
| 1000 | 999 | 99 | 0.851774 | 45 | 0.636089 | 517/882 |
| 2000 | 1999 | 49 | 0.96138 | 22 | 0.796038 | 1517/1882 |
| 3000 | 2999 | 33 | 0.961742 | 15 | 0.738626 | 517/882 |
| 10000 | 9999 | 9 | 0.999698 | 4 | 0.947597 | 9517/5882 |
| 20000 | 19999 | 4 | 0.999998 | 2 | 0.978374 | 19517/5882 |
| 30000 | 29999 | 3 | 1 | 1 | 0.999568 | 9517/15882 |

N/A 表示筛选后不足一个完整组。各组 p 取普通中位数，偶数组取中间两个 p 的算术平均；组数较少时请结合逐组缓存解释。

剔除严重重复回答后的逐组 p-value 缓存：`/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.nonrepetitive_grouped_p_values.json`；`/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.nonrepetitive_grouped_p_values.json`

### 固定参考模型 PPL（只评分已保存的回答）

| 文件组 | 总体 PPL ↓ | 逐回答 PPL 中位数 ↓ | 剔除严重重复后总体 PPL ↓ | 保留回答数/原回答数 | 有效样本/总样本 | 状态 | 缓存复用 |
|---|---:|---:|---:|---:|---:|---|---|
| kgw | 3.571931 | 3.727753 | 3.845888 | 485/500 | 500/500 | ok | True |
| clean | 1.535880 | 2.557640 | 2.702170 | 412/500 | 500/500 | ok | True |

总体 PPL = exp(全部有效回答 NLL 总和 / 全部计分回答 token 数)，不是逐条 PPL 的算术平均。
逐回答 PPL 中位数对全量有效回答的 PPL 排序；偶数条取中间两个 PPL 的算术平均，不对平均 NLL 取中位数后再 exp。空回答或异常 loss 不计入，并单独报告数量。
剔除严重重复后总体 PPL：复用同源重复筛选缓存，按教师 tokenizer 的回答内部相邻 token 对重复率严格 > 50% 剔除整条回答，prompt 不参与判断；只汇总保留回答原有的参考模型 NLL 和参考 tokenizer token 数。保留回答的文本不变，不删除文内 token，不丢弃尾部。KGW 与 clean 各自筛选，保留回答数含未成功评分回答。N/A 表示未提供筛选，null 表示无可计算数值；筛选后结果是子集统计，全量结果另行保留。
原生成 tokenizer 恢复实际生成 prompt；参考 tokenizer 对 prompt/answer 分开编码后拼接；只计回答，包含首回答 token。Base 参考模型不再套用 chat template；只添加一次参考 BOS，不额外评分 EOS；输入 JSONL 不修改。

- kgw: `/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl`；SHA256 `a544802bd1d1b310dec9bb254958b3386c3692ae848346b77eb36bfe64d96c74`；逐条明细 `/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.ppl.3f65ad2ad246b50e822c.jsonl`；空回答 0；异常 loss 0；原生成截断 3；参考上下文截断 0；计分回答 tokens 108367；平均回答 tokens 216.73；中位数样本数 500（状态 ok）。
  剔除严重重复回答 15（3.00%）；保留回答中有效评分 485/485；保留回答计分 tokens 98197；状态 ok；重复筛选缓存 `/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.nonrepetitive_grouped_p_values.json`。

  生成文本配置（种子逐条保存在明细中）：

```json
{
  "student_model_paths": [
    "/shared/wwx/EasyGAD/checkpoints/gad_05b_cleanwarmup_cleangad_control/warmup/global_step_1813/actor/huggingface"
  ],
  "generation_tokenizer_paths": [
    "/shared/public_models/Qwen2.5-0.5B"
  ],
  "generation_configurations": [
    {
      "configuration": {
        "kgw_enabled_during_generation": false,
        "max_new_tokens": 1536,
        "max_prompt_tokens": 2048,
        "temperature": 0.7,
        "top_p": 0.9
      },
      "samples": 500
    }
  ],
  "generation_seeds": {
    "recorded_samples": 500,
    "minimum": 42,
    "maximum": 541,
    "individual_values": "see per-sample immutable records"
  }
}
```
- clean: `/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl`；SHA256 `597b843d28d31c353c7bb9b94a3b6dccb564cb45ac2c5252f6a1592ccd768efe`；逐条明细 `/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.ppl.877fc574f9ee35a5145f.jsonl`；空回答 0；异常 loss 0；原生成截断 3；参考上下文截断 0；计分回答 tokens 156267；平均回答 tokens 312.53；中位数样本数 500（状态 ok）。
  剔除严重重复回答 88（17.60%）；保留回答中有效评分 412/412；保留回答计分 tokens 45137；状态 ok；重复筛选缓存 `/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.nonrepetitive_grouped_p_values.json`。

  生成文本配置（种子逐条保存在明细中）：

```json
{
  "student_model_paths": [
    "/shared/public_models/Qwen2.5-0.5B"
  ],
  "generation_tokenizer_paths": [
    "/shared/public_models/Qwen2.5-0.5B"
  ],
  "generation_configurations": [
    {
      "configuration": {
        "kgw_enabled_during_generation": false,
        "max_new_tokens": 1536,
        "max_prompt_tokens": 2048,
        "temperature": 0.7,
        "top_p": 0.9
      },
      "samples": 500
    }
  ],
  "generation_seeds": {
    "recorded_samples": 500,
    "minimum": 42,
    "maximum": 541,
    "individual_values": "see per-sample immutable records"
  }
}
```

完整评分配置（含模型/tokenizer 指纹、软件版本；权重使用 size/mtime 标识，不全量哈希）：

```json
{
  "model_path": "/shared/public_models/Llama-3-8B",
  "device": "cuda",
  "dtype": "bfloat16",
  "generation_tokenizer": "/shared/public_models/Qwen2.5-0.5B",
  "max_length": null,
  "overflow": "error",
  "effective_max_length": 8192,
  "protocol": {
    "prompt": "source-generation-prompt; source chat template, not reference chat template",
    "boundary": "encode prompt and answer separately with add_special_tokens=False, then concatenate",
    "bos": "one reference BOS at start when defined; no extra EOS",
    "loss": "causal next-token NLL on all answer tokens, including the first; no prompt or padding loss",
    "aggregate": "exp(sum(answer NLL) / sum(scored answer tokens)); not mean per-answer PPL",
    "source_tokenizer_selection": "explicit override, otherwise row.model_path; fallback assumes the generation tokenizer matches that checkpoint",
    "legacy_prompt_limit": 2048,
    "weights_fingerprint": "weight filenames, sizes and mtime_ns; weight contents are not hashed"
  },
  "reference_assets": {
    "path": "/shared/public_models/Llama-3-8B",
    "assets": [
      {
        "name": "config.json",
        "size": 654,
        "sha256": "2430cee764b6530ff8673cf9ba8561e1d5a33152d503cd0de909ff5718261441"
      },
      {
        "name": "generation_config.json",
        "size": 126,
        "sha256": "55550e95c40c53fb0ee3f960d6d2b25a46405c8f790e5c4bb02caf3e98f2b5d0"
      },
      {
        "name": "model.safetensors.index.json",
        "size": 23950,
        "sha256": "146776fce3f6db1103aa6f249e65ee5544c5923ce6f971b092eee79aa6e5d37b"
      },
      {
        "name": "special_tokens_map.json",
        "size": 73,
        "sha256": "462d91939dbc37178aa5a3eae7068d1990ccc92e09f288cc71f42cdf139d69cc"
      },
      {
        "name": "tokenizer.json",
        "size": 9085698,
        "sha256": "e134af98b985517b4f068e3755ae90d4e9cd2d45d328325dc503f1c6b2d06cc7"
      },
      {
        "name": "tokenizer_config.json",
        "size": 50566,
        "sha256": "690727b4fed286383df1c7ca5e805124cb70c6eb4529f807c7b2e60ff741da7e"
      }
    ],
    "weight_stats": [
      {
        "name": "model-00001-of-00004.safetensors",
        "size": 4976698672,
        "mtime_ns": 1736746522477644778
      },
      {
        "name": "model-00002-of-00004.safetensors",
        "size": 4999802720,
        "mtime_ns": 1736746656058650226
      },
      {
        "name": "model-00003-of-00004.safetensors",
        "size": 4915916176,
        "mtime_ns": 1736746768408654808
      },
      {
        "name": "model-00004-of-00004.safetensors",
        "size": 1168138808,
        "mtime_ns": 1736746796088655937
      }
    ],
    "weight_content_hashed": false
  },
  "software": {
    "python": "3.10.21",
    "torch": "2.6.0",
    "transformers": "4.51.3",
    "tokenizers": "0.21.4"
  }
}
```

完整指标（JSON）：

```json
{
  "positive_class": "kgw",
  "score": "z_score (higher means more likely watermarked)",
  "num_kgw": 500,
  "num_clean": 500,
  "auroc": 0.4626040000000001,
  "best_f1": {
    "threshold": -5.03309510460972,
    "fpr": 0.944,
    "tpr": 0.998,
    "precision": 0.513903192584964,
    "f1": 0.6784500339904826,
    "tp": 499,
    "fp": 472,
    "tn": 28,
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
      "threshold": 2.2283440581246223,
      "fpr": 0.05,
      "tpr": 0.03,
      "precision": 0.375,
      "f1": 0.05555555555555555,
      "tp": 15,
      "fp": 25,
      "tn": 475,
      "fn": 485,
      "target_fpr": 0.05
    },
    "10%": {
      "threshold": 1.7008401285415224,
      "fpr": 0.1,
      "tpr": 0.07,
      "precision": 0.4117647058823529,
      "f1": 0.11965811965811966,
      "tp": 35,
      "fp": 50,
      "tn": 450,
      "fn": 465,
      "target_fpr": 0.1
    }
  },
  "note": "For each target FPR, select the empirical ROC point with the highest TPR whose FPR does not exceed the target; tied scores are kept together.",
  "detector_config": {
    "gamma": 0.5,
    "hash_key": 15485863,
    "seeding": "simple_1 (hash_key * previous_token_id)",
    "delta_by_label": {
      "kgw": 2.0,
      "clean": 2.0
    }
  },
  "rouge_l_dolly": {
    "mean": 0.20911479663899177,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl",
    "reference_file": "/shared/wwx/EasyGAD/text_quality/references/dolly_human_500.jsonl",
    "reference_source": "databricks/databricks-dolly-15k:response",
    "metric": "rougeL",
    "measure": "fmeasure",
    "use_stemmer": true,
    "aggregation": "unweighted mean of per-sample ROUGE-L F1"
  },
  "rouge_l_teacher_clean": {
    "mean": 0.30996181867715505,
    "num_samples": 500,
    "evaluated_file": "/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl",
    "reference_file": "/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_clean_test.parquet",
    "reference_source": "Qwen2.5-14B clean teacher responses",
    "metric": "rougeL",
    "measure": "fmeasure",
    "use_stemmer": true,
    "aggregation": "unweighted mean of per-sample ROUGE-L F1"
  },
  "seq_rep_3": {
    "kgw": {
      "mean": 0.05314098910455279,
      "median": 0.0259751212312882,
      "num_samples": 500,
      "num_short_answers": 1,
      "num_empty_answers": 0,
      "evaluated_file": "/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl",
      "source_sha256": "a544802bd1d1b310dec9bb254958b3386c3692ae848346b77eb36bfe64d96c74",
      "ngram_size": 3,
      "tokenization": "answer.split(); whitespace-delimited words; case and punctuation preserved",
      "scope": "answer only; overlapping trigrams within each complete original answer; no filtering or cross-answer trigrams",
      "short_answer_policy": "answers with fewer than 3 words, including empty answers, contribute 0; counts reported",
      "aggregation": {
        "mean": "unweighted arithmetic mean of per-answer Seq-Rep-3",
        "median": "ordinary median of per-answer Seq-Rep-3; arithmetic mean of the middle two for even counts"
      }
    },
    "clean": {
      "mean": 0.15901538183339659,
      "median": 0.021919288974297402,
      "num_samples": 500,
      "num_short_answers": 1,
      "num_empty_answers": 0,
      "evaluated_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl",
      "source_sha256": "597b843d28d31c353c7bb9b94a3b6dccb564cb45ac2c5252f6a1592ccd768efe",
      "ngram_size": 3,
      "tokenization": "answer.split(); whitespace-delimited words; case and punctuation preserved",
      "scope": "answer only; overlapping trigrams within each complete original answer; no filtering or cross-answer trigrams",
      "short_answer_policy": "answers with fewer than 3 words, including empty answers, contribute 0; counts reported",
      "aggregation": {
        "mean": "unweighted arithmetic mean of per-answer Seq-Rep-3",
        "median": "ordinary median of per-answer Seq-Rep-3; arithmetic mean of the middle two for even counts"
      }
    }
  },
  "p_values": {
    "kgw": {
      "raw": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.587913978437283,
        "median": 0.658361434051861,
        "min": 0.002197952486763932,
        "max": 0.9999999978094234,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 11,
            "fraction": 0.022
          },
          "5%": {
            "alpha": 0.05,
            "count": 36,
            "fraction": 0.072
          },
          "10%": {
            "alpha": 0.1,
            "count": 55,
            "fraction": 0.11
          }
        }
      },
      "deduplicated": {
        "n_total": 500,
        "n_valid": 500,
        "n_invalid": 0,
        "mean": 0.5618113459887325,
        "median": 0.5996692153351387,
        "min": 0.00921106272704951,
        "max": 0.9997579313716072,
        "at_alpha": {
          "1%": {
            "alpha": 0.01,
            "count": 2,
            "fraction": 0.004
          },
          "5%": {
            "alpha": 0.05,
            "count": 22,
            "fraction": 0.044
          },
          "10%": {
            "alpha": 0.1,
            "count": 35,
            "fraction": 0.07
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
    "kgw": "/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.p_values.jsonl",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.p_values.jsonl"
  },
  "grouped_p_values": {
    "kgw": {
      "aggregation": "ordinary_median",
      "num_answers": 500,
      "total_answer_tokens": 110315,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 110,
          "total_answer_tokens": 110315,
          "discarded_tail_tokens": 315,
          "median_p_value": 0.8517743756590758,
          "median_log10_p_value": -0.06967542915691224,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 55,
          "total_answer_tokens": 110315,
          "discarded_tail_tokens": 315,
          "median_p_value": 0.9683017588985491,
          "median_log10_p_value": -0.013989279259781976,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 36,
          "total_answer_tokens": 110315,
          "discarded_tail_tokens": 2315,
          "median_p_value": 0.9804642099767789,
          "median_log10_p_value": -0.008568254819532509,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 11,
          "total_answer_tokens": 110315,
          "discarded_tail_tokens": 315,
          "median_p_value": 0.9979485722951797,
          "median_log10_p_value": -0.0008918388167411366,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 5,
          "total_answer_tokens": 110315,
          "discarded_tail_tokens": 10315,
          "median_p_value": 0.9999999196212623,
          "median_log10_p_value": -3.490804363351823e-08,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 3,
          "total_answer_tokens": 110315,
          "discarded_tail_tokens": 20315,
          "median_p_value": 0.9999999983699949,
          "median_log10_p_value": -7.079022343879514e-10,
          "status": "ok"
        }
      }
    },
    "clean": {
      "aggregation": "ordinary_median",
      "num_answers": 500,
      "total_answer_tokens": 159765,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 159,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 765,
          "median_p_value": 0.8659288977499955,
          "median_log10_p_value": -0.06251776685396769,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 79,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 1765,
          "median_p_value": 0.971357711016285,
          "median_log10_p_value": -0.012620807875598238,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 53,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 765,
          "median_p_value": 0.9821335190767914,
          "median_log10_p_value": -0.007829466737979084,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 15,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 9765,
          "median_p_value": 0.9999999999999984,
          "median_log10_p_value": -6.750292265873014e-16,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 7,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 19765,
          "median_p_value": 1.0,
          "median_log10_p_value": 0.0,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 5,
          "total_answer_tokens": 159765,
          "discarded_tail_tokens": 9765,
          "median_p_value": 1.0,
          "median_log10_p_value": 0.0,
          "status": "ok"
        }
      }
    }
  },
  "grouped_p_value_method": "teacher-tokenizer answer IDs concatenated without separators; exact disjoint blocks; first token of each block is context only; no repetition deduplication; incomplete tail discarded; ordinary median of block p-values (arithmetic mean of the two middle p-values for even group counts)",
  "per_group_p_value_files": {
    "kgw": "/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.grouped_p_values.json",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.grouped_p_values.json"
  },
  "grouped_p_values_without_severe_repetition": {
    "kgw": {
      "aggregation": "ordinary_median",
      "num_answers": 485,
      "total_answer_tokens": 99517,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 99,
          "total_answer_tokens": 99517,
          "discarded_tail_tokens": 517,
          "median_p_value": 0.8517743756590758,
          "median_log10_p_value": -0.06967542915691224,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 49,
          "total_answer_tokens": 99517,
          "discarded_tail_tokens": 1517,
          "median_p_value": 0.9613804838256327,
          "median_log10_p_value": -0.017104698363877752,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 33,
          "total_answer_tokens": 99517,
          "discarded_tail_tokens": 517,
          "median_p_value": 0.9617416641553246,
          "median_log10_p_value": -0.016941569229135967,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 9,
          "total_answer_tokens": 99517,
          "discarded_tail_tokens": 9517,
          "median_p_value": 0.999698400080992,
          "median_log10_p_value": -0.00013100293679839522,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 4,
          "total_answer_tokens": 99517,
          "discarded_tail_tokens": 19517,
          "median_p_value": 0.9999979012264593,
          "median_log10_p_value": -9.114867240411086e-07,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 3,
          "total_answer_tokens": 99517,
          "discarded_tail_tokens": 9517,
          "median_p_value": 0.9999999073746251,
          "median_log10_p_value": -4.0226691077415586e-08,
          "status": "ok"
        }
      },
      "filtering": {
        "repetition_threshold": 0.5,
        "comparison": ">",
        "scope": "answer-internal adjacent token pairs; prompt excluded",
        "num_answers_before": 500,
        "num_answers_retained": 485,
        "num_answers_removed": 15,
        "fraction_answers_removed": 0.03,
        "total_answer_tokens_before": 110315,
        "total_answer_tokens_retained": 99517,
        "total_answer_tokens_removed": 10798,
        "removed_answer_ids": [
          "dolly-07923",
          "dolly-08884",
          "dolly-01092",
          "dolly-02516",
          "dolly-02725",
          "dolly-03239",
          "dolly-13445",
          "dolly-03231",
          "dolly-08607",
          "dolly-11386",
          "dolly-03319",
          "dolly-05355",
          "dolly-01356",
          "dolly-12236",
          "dolly-13235"
        ]
      }
    },
    "clean": {
      "aggregation": "ordinary_median",
      "num_answers": 412,
      "total_answer_tokens": 45882,
      "budgets": {
        "1000": {
          "group_token_count": 1000,
          "scored_tokens_per_group": 999,
          "num_groups": 45,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 882,
          "median_p_value": 0.6360891449864364,
          "median_log10_p_value": -0.1964820156995508,
          "status": "ok"
        },
        "2000": {
          "group_token_count": 2000,
          "scored_tokens_per_group": 1999,
          "num_groups": 22,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 1882,
          "median_p_value": 0.7960378878131416,
          "median_log10_p_value": -0.09906626131183685,
          "status": "ok"
        },
        "3000": {
          "group_token_count": 3000,
          "scored_tokens_per_group": 2999,
          "num_groups": 15,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 882,
          "median_p_value": 0.7386263221105359,
          "median_log10_p_value": -0.13157521964243946,
          "status": "ok"
        },
        "10000": {
          "group_token_count": 10000,
          "scored_tokens_per_group": 9999,
          "num_groups": 4,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 5882,
          "median_p_value": 0.947596846602552,
          "median_log10_p_value": -0.0233763931850151,
          "status": "ok"
        },
        "20000": {
          "group_token_count": 20000,
          "scored_tokens_per_group": 19999,
          "num_groups": 2,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 5882,
          "median_p_value": 0.9783739864832501,
          "median_log10_p_value": -0.009495103065976066,
          "status": "ok"
        },
        "30000": {
          "group_token_count": 30000,
          "scored_tokens_per_group": 29999,
          "num_groups": 1,
          "total_answer_tokens": 45882,
          "discarded_tail_tokens": 15882,
          "median_p_value": 0.9995678964162934,
          "median_log10_p_value": -0.00018770075802065225,
          "status": "ok"
        }
      },
      "filtering": {
        "repetition_threshold": 0.5,
        "comparison": ">",
        "scope": "answer-internal adjacent token pairs; prompt excluded",
        "num_answers_before": 500,
        "num_answers_retained": 412,
        "num_answers_removed": 88,
        "fraction_answers_removed": 0.176,
        "total_answer_tokens_before": 159765,
        "total_answer_tokens_retained": 45882,
        "total_answer_tokens_removed": 113883,
        "removed_answer_ids": [
          "dolly-00135",
          "dolly-12241",
          "dolly-07923",
          "dolly-07103",
          "dolly-05608",
          "dolly-07788",
          "dolly-11310",
          "dolly-02097",
          "dolly-03614",
          "dolly-13505",
          "dolly-02580",
          "dolly-08884",
          "dolly-12659",
          "dolly-00420",
          "dolly-11014",
          "dolly-08008",
          "dolly-02186",
          "dolly-00275",
          "dolly-08512",
          "dolly-14060",
          "dolly-01461",
          "dolly-02223",
          "dolly-04949",
          "dolly-08689",
          "dolly-08574",
          "dolly-08406",
          "dolly-04141",
          "dolly-03209",
          "dolly-06227",
          "dolly-11078",
          "dolly-09778",
          "dolly-04856",
          "dolly-13779",
          "dolly-06595",
          "dolly-08936",
          "dolly-09344",
          "dolly-05605",
          "dolly-08340",
          "dolly-04589",
          "dolly-04686",
          "dolly-14700",
          "dolly-03696",
          "dolly-03914",
          "dolly-11987",
          "dolly-01939",
          "dolly-05628",
          "dolly-13339",
          "dolly-08911",
          "dolly-03239",
          "dolly-13445",
          "dolly-02139",
          "dolly-14265",
          "dolly-13610",
          "dolly-07427",
          "dolly-09563",
          "dolly-02451",
          "dolly-13544",
          "dolly-06824",
          "dolly-05312",
          "dolly-10992",
          "dolly-06932",
          "dolly-08607",
          "dolly-05388",
          "dolly-11386",
          "dolly-02069",
          "dolly-09439",
          "dolly-00148",
          "dolly-08211",
          "dolly-12186",
          "dolly-03319",
          "dolly-07407",
          "dolly-10389",
          "dolly-03916",
          "dolly-08222",
          "dolly-14947",
          "dolly-03624",
          "dolly-09330",
          "dolly-11182",
          "dolly-02059",
          "dolly-02916",
          "dolly-09816",
          "dolly-05355",
          "dolly-06970",
          "dolly-05634",
          "dolly-02500",
          "dolly-11314",
          "dolly-13235",
          "dolly-04223"
        ]
      }
    }
  },
  "grouped_p_value_without_severe_repetition_method": "exclude whole answers whose answer-internal adjacent-token-pair repetition ratio (1 - unique pairs / all pairs) is strictly greater than 0.5; prompts excluded from repetition assessment; filter each label independently; retain original answer order, then concatenate teacher-tokenizer answer IDs without separators; exact disjoint blocks, first token context only; no token-pair deduplication within retained blocks; incomplete tail discarded; ordinary median of block p-values (mean of the middle two for even counts)",
  "per_group_p_value_without_severe_repetition_files": {
    "kgw": "/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.nonrepetitive_grouped_p_values.json",
    "clean": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.nonrepetitive_grouped_p_values.json"
  },
  "ppl": {
    "enabled": true,
    "schema": "saved-answer-reference-ppl-v1",
    "configuration": {
      "model_path": "/shared/public_models/Llama-3-8B",
      "device": "cuda",
      "dtype": "bfloat16",
      "generation_tokenizer": "/shared/public_models/Qwen2.5-0.5B",
      "max_length": null,
      "overflow": "error",
      "effective_max_length": 8192,
      "protocol": {
        "prompt": "source-generation-prompt; source chat template, not reference chat template",
        "boundary": "encode prompt and answer separately with add_special_tokens=False, then concatenate",
        "bos": "one reference BOS at start when defined; no extra EOS",
        "loss": "causal next-token NLL on all answer tokens, including the first; no prompt or padding loss",
        "aggregate": "exp(sum(answer NLL) / sum(scored answer tokens)); not mean per-answer PPL",
        "source_tokenizer_selection": "explicit override, otherwise row.model_path; fallback assumes the generation tokenizer matches that checkpoint",
        "legacy_prompt_limit": 2048,
        "weights_fingerprint": "weight filenames, sizes and mtime_ns; weight contents are not hashed"
      },
      "reference_assets": {
        "path": "/shared/public_models/Llama-3-8B",
        "assets": [
          {
            "name": "config.json",
            "size": 654,
            "sha256": "2430cee764b6530ff8673cf9ba8561e1d5a33152d503cd0de909ff5718261441"
          },
          {
            "name": "generation_config.json",
            "size": 126,
            "sha256": "55550e95c40c53fb0ee3f960d6d2b25a46405c8f790e5c4bb02caf3e98f2b5d0"
          },
          {
            "name": "model.safetensors.index.json",
            "size": 23950,
            "sha256": "146776fce3f6db1103aa6f249e65ee5544c5923ce6f971b092eee79aa6e5d37b"
          },
          {
            "name": "special_tokens_map.json",
            "size": 73,
            "sha256": "462d91939dbc37178aa5a3eae7068d1990ccc92e09f288cc71f42cdf139d69cc"
          },
          {
            "name": "tokenizer.json",
            "size": 9085698,
            "sha256": "e134af98b985517b4f068e3755ae90d4e9cd2d45d328325dc503f1c6b2d06cc7"
          },
          {
            "name": "tokenizer_config.json",
            "size": 50566,
            "sha256": "690727b4fed286383df1c7ca5e805124cb70c6eb4529f807c7b2e60ff741da7e"
          }
        ],
        "weight_stats": [
          {
            "name": "model-00001-of-00004.safetensors",
            "size": 4976698672,
            "mtime_ns": 1736746522477644778
          },
          {
            "name": "model-00002-of-00004.safetensors",
            "size": 4999802720,
            "mtime_ns": 1736746656058650226
          },
          {
            "name": "model-00003-of-00004.safetensors",
            "size": 4915916176,
            "mtime_ns": 1736746768408654808
          },
          {
            "name": "model-00004-of-00004.safetensors",
            "size": 1168138808,
            "mtime_ns": 1736746796088655937
          }
        ],
        "weight_content_hashed": false
      },
      "software": {
        "python": "3.10.21",
        "torch": "2.6.0",
        "transformers": "4.51.3",
        "tokenizers": "0.21.4"
      }
    },
    "files": {
      "kgw": {
        "samples": 500,
        "valid_samples": 500,
        "skipped_empty_answers": 0,
        "complete": true,
        "nonfinite_samples": 0,
        "status": "ok",
        "total_nll": 137962.72345853038,
        "scored_tokens": 108367,
        "mean_nll": 1.2731064203911742,
        "token_weighted_ppl": 3.571931266011677,
        "mean_answer_tokens": 216.734,
        "source_prompt_truncated_samples": 3,
        "reference_prompt_truncated_samples": 0,
        "generation_configurations": [
          {
            "configuration": {
              "kgw_enabled_during_generation": false,
              "max_new_tokens": 1536,
              "max_prompt_tokens": 2048,
              "temperature": 0.7,
              "top_p": 0.9
            },
            "samples": 500
          }
        ],
        "generation_seeds": {
          "recorded_samples": 500,
          "minimum": 42,
          "maximum": 541,
          "individual_values": "see per-sample immutable records"
        },
        "student_model_paths": [
          "/shared/wwx/EasyGAD/checkpoints/gad_05b_cleanwarmup_cleangad_control/warmup/global_step_1813/actor/huggingface"
        ],
        "generation_tokenizer_paths": [
          "/shared/public_models/Qwen2.5-0.5B"
        ],
        "median_per_answer_ppl": 3.727752959839494,
        "median_samples": 500,
        "median_status": "ok",
        "without_severe_repetition": {
          "samples": 485,
          "valid_samples": 485,
          "skipped_empty_answers": 0,
          "complete": true,
          "nonfinite_samples": 0,
          "status": "ok",
          "total_nll": 132271.8077686429,
          "scored_tokens": 98197,
          "mean_nll": 1.3470045700850628,
          "token_weighted_ppl": 3.84588817117029,
          "mean_answer_tokens": 202.4680412371134,
          "source_prompt_truncated_samples": 2,
          "reference_prompt_truncated_samples": 0,
          "generation_configurations": [
            {
              "configuration": {
                "kgw_enabled_during_generation": false,
                "max_new_tokens": 1536,
                "max_prompt_tokens": 2048,
                "temperature": 0.7,
                "top_p": 0.9
              },
              "samples": 485
            }
          ],
          "generation_seeds": {
            "recorded_samples": 485,
            "minimum": 42,
            "maximum": 541,
            "individual_values": "see per-sample immutable records"
          },
          "student_model_paths": [
            "/shared/wwx/EasyGAD/checkpoints/gad_05b_cleanwarmup_cleangad_control/warmup/global_step_1813/actor/huggingface"
          ],
          "generation_tokenizer_paths": [
            "/shared/public_models/Qwen2.5-0.5B"
          ],
          "median_per_answer_ppl": 3.7997439925261323,
          "median_samples": 485,
          "median_status": "ok",
          "num_answers_before": 500,
          "num_answers_retained": 485,
          "num_answers_removed": 15,
          "fraction_answers_removed": 0.03,
          "repetition_threshold": 0.5,
          "comparison": ">",
          "scope": "answer-internal adjacent token pairs; prompt excluded",
          "removed_answer_ids": [
            "dolly-07923",
            "dolly-08884",
            "dolly-01092",
            "dolly-02516",
            "dolly-02725",
            "dolly-03239",
            "dolly-13445",
            "dolly-03231",
            "dolly-08607",
            "dolly-11386",
            "dolly-03319",
            "dolly-05355",
            "dolly-01356",
            "dolly-12236",
            "dolly-13235"
          ],
          "filtering_source_file": "/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.nonrepetitive_grouped_p_values.json",
          "filtering_source_sha256": "a544802bd1d1b310dec9bb254958b3386c3692ae848346b77eb36bfe64d96c74",
          "filtering_tokenizer": {
            "path": "/shared/public_models/Qwen2.5-14B-Instruct",
            "files_sha256": {
              "config.json": "7362de7db90a1e57fe153e55094e6c2fb7d904a3705d34296ff7de84488235f4",
              "merges.txt": "0de0bc38a29ea38eef099b677fa1ff52edd181e573529af26c4cd2136e233777",
              "tokenizer.json": "47ec9be242d3ef39b9c97ac0a3f06c1752f061b234e295bc0a2842067a3fe4f9",
              "tokenizer_config.json": "fa2a40a9d8c8c4bb7f25ab726eb78ec9cbaaef96d1fa26f1d7f5615e886449a8",
              "vocab.json": "ca10d7e9fb3ed18575dd1e277a2579c16d108e32f27439684afa0e10b1440910"
            }
          }
        },
        "source_path": "/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl",
        "source_sha256": "a544802bd1d1b310dec9bb254958b3386c3692ae848346b77eb36bfe64d96c74",
        "per_sample_file": "/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.ppl.3f65ad2ad246b50e822c.jsonl",
        "cache_reused": true
      },
      "clean": {
        "samples": 500,
        "valid_samples": 500,
        "skipped_empty_answers": 0,
        "complete": true,
        "nonfinite_samples": 0,
        "status": "ok",
        "total_nll": 67054.72902449768,
        "scored_tokens": 156267,
        "mean_nll": 0.42910357928735865,
        "token_weighted_ppl": 1.5358801115260794,
        "mean_answer_tokens": 312.534,
        "source_prompt_truncated_samples": 3,
        "reference_prompt_truncated_samples": 0,
        "generation_configurations": [
          {
            "configuration": {
              "kgw_enabled_during_generation": false,
              "max_new_tokens": 1536,
              "max_prompt_tokens": 2048,
              "temperature": 0.7,
              "top_p": 0.9
            },
            "samples": 500
          }
        ],
        "generation_seeds": {
          "recorded_samples": 500,
          "minimum": 42,
          "maximum": 541,
          "individual_values": "see per-sample immutable records"
        },
        "student_model_paths": [
          "/shared/public_models/Qwen2.5-0.5B"
        ],
        "generation_tokenizer_paths": [
          "/shared/public_models/Qwen2.5-0.5B"
        ],
        "median_per_answer_ppl": 2.5576398946471928,
        "median_samples": 500,
        "median_status": "ok",
        "without_severe_repetition": {
          "samples": 412,
          "valid_samples": 412,
          "skipped_empty_answers": 0,
          "complete": true,
          "nonfinite_samples": 0,
          "status": "ok",
          "total_nll": 44868.67048177123,
          "scored_tokens": 45137,
          "mean_nll": 0.9940552203684612,
          "token_weighted_ppl": 2.702170179562856,
          "mean_answer_tokens": 109.55582524271844,
          "source_prompt_truncated_samples": 1,
          "reference_prompt_truncated_samples": 0,
          "generation_configurations": [
            {
              "configuration": {
                "kgw_enabled_during_generation": false,
                "max_new_tokens": 1536,
                "max_prompt_tokens": 2048,
                "temperature": 0.7,
                "top_p": 0.9
              },
              "samples": 412
            }
          ],
          "generation_seeds": {
            "recorded_samples": 412,
            "minimum": 42,
            "maximum": 541,
            "individual_values": "see per-sample immutable records"
          },
          "student_model_paths": [
            "/shared/public_models/Qwen2.5-0.5B"
          ],
          "generation_tokenizer_paths": [
            "/shared/public_models/Qwen2.5-0.5B"
          ],
          "median_per_answer_ppl": 2.8522532998790773,
          "median_samples": 412,
          "median_status": "ok",
          "num_answers_before": 500,
          "num_answers_retained": 412,
          "num_answers_removed": 88,
          "fraction_answers_removed": 0.176,
          "repetition_threshold": 0.5,
          "comparison": ">",
          "scope": "answer-internal adjacent token pairs; prompt excluded",
          "removed_answer_ids": [
            "dolly-00135",
            "dolly-12241",
            "dolly-07923",
            "dolly-07103",
            "dolly-05608",
            "dolly-07788",
            "dolly-11310",
            "dolly-02097",
            "dolly-03614",
            "dolly-13505",
            "dolly-02580",
            "dolly-08884",
            "dolly-12659",
            "dolly-00420",
            "dolly-11014",
            "dolly-08008",
            "dolly-02186",
            "dolly-00275",
            "dolly-08512",
            "dolly-14060",
            "dolly-01461",
            "dolly-02223",
            "dolly-04949",
            "dolly-08689",
            "dolly-08574",
            "dolly-08406",
            "dolly-04141",
            "dolly-03209",
            "dolly-06227",
            "dolly-11078",
            "dolly-09778",
            "dolly-04856",
            "dolly-13779",
            "dolly-06595",
            "dolly-08936",
            "dolly-09344",
            "dolly-05605",
            "dolly-08340",
            "dolly-04589",
            "dolly-04686",
            "dolly-14700",
            "dolly-03696",
            "dolly-03914",
            "dolly-11987",
            "dolly-01939",
            "dolly-05628",
            "dolly-13339",
            "dolly-08911",
            "dolly-03239",
            "dolly-13445",
            "dolly-02139",
            "dolly-14265",
            "dolly-13610",
            "dolly-07427",
            "dolly-09563",
            "dolly-02451",
            "dolly-13544",
            "dolly-06824",
            "dolly-05312",
            "dolly-10992",
            "dolly-06932",
            "dolly-08607",
            "dolly-05388",
            "dolly-11386",
            "dolly-02069",
            "dolly-09439",
            "dolly-00148",
            "dolly-08211",
            "dolly-12186",
            "dolly-03319",
            "dolly-07407",
            "dolly-10389",
            "dolly-03916",
            "dolly-08222",
            "dolly-14947",
            "dolly-03624",
            "dolly-09330",
            "dolly-11182",
            "dolly-02059",
            "dolly-02916",
            "dolly-09816",
            "dolly-05355",
            "dolly-06970",
            "dolly-05634",
            "dolly-02500",
            "dolly-11314",
            "dolly-13235",
            "dolly-04223"
          ],
          "filtering_source_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.nonrepetitive_grouped_p_values.json",
          "filtering_source_sha256": "597b843d28d31c353c7bb9b94a3b6dccb564cb45ac2c5252f6a1592ccd768efe",
          "filtering_tokenizer": {
            "path": "/shared/public_models/Qwen2.5-14B-Instruct",
            "files_sha256": {
              "config.json": "7362de7db90a1e57fe153e55094e6c2fb7d904a3705d34296ff7de84488235f4",
              "merges.txt": "0de0bc38a29ea38eef099b677fa1ff52edd181e573529af26c4cd2136e233777",
              "tokenizer.json": "47ec9be242d3ef39b9c97ac0a3f06c1752f061b234e295bc0a2842067a3fe4f9",
              "tokenizer_config.json": "fa2a40a9d8c8c4bb7f25ab726eb78ec9cbaaef96d1fa26f1d7f5615e886449a8",
              "vocab.json": "ca10d7e9fb3ed18575dd1e277a2579c16d108e32f27439684afa0e10b1440910"
            }
          }
        },
        "source_path": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl",
        "source_sha256": "597b843d28d31c353c7bb9b94a3b6dccb564cb45ac2c5252f6a1592ccd768efe",
        "per_sample_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.ppl.877fc574f9ee35a5145f.jsonl",
        "cache_reused": true
      }
    }
  },
  "evaluated_at": "2026-10-31T16:25:01+08:00",
  "kgw_file": "/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl",
  "clean_file": "/shared/wwx/EasyGAD/wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl",
  "history_document": "/shared/wwx/EasyGAD/wm_test/detection_metrics_history.md"
}
```
