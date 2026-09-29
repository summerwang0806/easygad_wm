
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
