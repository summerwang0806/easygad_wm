# gamma=0.5、delta=3 最终结果汇总

来源：`wm_test/detection_metrics_history.md` 中各目标文件最新含 PPL 的完整评估记录（2026-10-19，17:16:58–17:21:42，Asia/Shanghai）。未重新生成回答或重跑模型。

## 综合主表（全部 500 条回答）

| 方法 | AUROC | TPR@FPR≤5% ↓ | TPR@FPR≤10% ↓ | PPL ↓ | ROUGE-L：Dolly ↑ | ROUGE-L：clean 教师 ↑ | 严重重复回答比例 ↓ |
|---|---:|---:|---:|---:|---:|---:|---:|
| 未清洗 No Attack | 0.647688 | 11.40% | 22.80% | 3.545652 | 0.198494 | 0.309174 | 2.20% |
| Para | 0.531456 | 3.80% | 8.40% | 3.417079 | 0.211098 | 0.262207 | 3.00% |
| WN strength=2.5 | 0.433434 | 2.60% | 5.00% | 3.305133 | 0.185418 | 0.286763 | 4.20% |
| WN strength=3 | 0.416208 | 2.40% | 5.20% | 3.196939 | 0.175276 | 0.270563 | 7.00% |

ROUGE-L 使用 0–1 标度。Dolly 参考为人工回答，教师参考为 Qwen2.5-14B clean 回答；两者均为逐回答 ROUGE-L F1 的无权平均。
严重重复指回答内部相邻 token 对重复比例 `1 - unique_pairs / all_pairs > 0.5`。主表其他指标没有剔除这些回答。
AUROC 低于 0.5 表示原检测方向发生反转，不能直接解释为比 0.5 更干净。TPR 是在 clean 实测 FPR 不超过指定值时取得的最高 TPR；5% 列的实际 FPR 依次为 5.0%、4.6%、4.6%、5.0%，10% 列均为 10.0%。

## 固定 token 分组 p-value：全部回答，普通中位数

教师 tokenizer 编码回答，无分隔拼接，切成不重叠完整组；每组首 token 仅作上下文，实际计分预算减 1，尾部丢弃。偶数组取中间两个 p 的算术平均。

| Token 预算 | 未清洗 No Attack | Para | WN strength=2.5 | WN strength=3 |
|---:|---:|---:|---:|---:|
| 1k | 0.097284 | 0.647832 | 0.922739 | 0.953214 |
| 2k | 0.021011 | 0.631374 | 0.979091 | 0.994946 |
| 3k | 0.004511 | 0.550856 | 0.996744 | 0.998542 |
| 10k | 1.05520e-04 | 0.979823 | 0.999997820385361 | 0.99999999927713 |
| 20k | 3.02847e-09 | 0.986561 | 0.999999991974081 | 1 |
| 30k | 3.40648e-11 | 0.500352 | 1 | 1 |

对应预算的完整组数依次为：No Attack 124/62/41/12/6/4；Para 70/35/23/7/3/2；WN 2.5 141/70/47/14/7/4；WN 3 155/77/51/15/7/5。
Para 的 30k 只有两组，逐组 p 为 0.0007045020015890655 与 1，普通中位数为 0.5003522510007945；中位数不能代表所有组均无显著证据。
这里的 p 是原单侧 KGW 检验的证据指标；p 高表示正向水印证据弱，不是无水印的概率，1 也不代表完全去除。

## 剔除严重重复回答后的分组 p-value（补充结果）

各文件独立筛选整条回答后重新拼接、分组，仍使用普通中位数。主表 PPL 和 ROUGE-L 不对应这一筛选子集。

| Token 预算 | 未清洗 No Attack | Para | WN strength=2.5 | WN strength=3 |
|---:|---:|---:|---:|---:|
| 1k | 0.053311 | 0.562723 | 0.879126 | 0.939464 |
| 2k | 0.025835 | 0.535635 | 0.957484 | 0.974165 |
| 3k | 0.007578 | 0.514506 | 0.974642 | 0.994984 |
| 10k | 3.90689e-06 | 0.680831 | 0.999847 | 0.99999887870794 |
| 20k | 2.09115e-11 | 0.661378 | 0.999999785861883 | 0.999999999990309 |
| 30k | 4.33976e-19 | 0.841062 | 0.999999999997782 | 0.999999999999994 |

保留回答数：No Attack 489、Para 485、WN 2.5 479、WN 3 465。30k 完整组数依次为 3、1、3、3；Para 在该预算只剩一组。

## PPL 评分口径及样本量

四组 PPL 的完整评分 configuration 相同：固定参考模型 `/shared/public_models/Llama-3-8B`，bfloat16，参考上下文长度 8192。恢复源生成 prompt 后，计算所有回答 token（含首 token）的条件负对数似然，不计 prompt 损失。
总体 `PPL = exp(sum(answer NLL) / sum(scored answer tokens))`，不是逐回答 PPL 的算术平均。

| 方法 | 有效回答数 | PPL 计分 tokens | 平均回答 tokens | PPL 相对未清洗下降 |
|---|---:|---:|---:|---:|
| 未清洗 No Attack | 500/500 | 122479 | 244.96 | 0.00% |
| Para | 500/500 | 69402 | 138.80 | 3.63% |
| WN strength=2.5 | 500/500 | 138174 | 276.35 | 6.78% |
| WN strength=3 | 500/500 | 149884 | 299.77 | 9.83% |

PPL 表中的 token 数由 Llama-3 tokenizer 计算，和水印分组的教师 tokenizer token 数不同。所有四组均无空回答、无异常 loss、无参考模型上下文截断。
生成阶段 No Attack/Para 的 max_prompt_tokens=2048，各有 3 条 prompt 截断；WN 两组为 6144，无 prompt 截断。这是现有结果的比较限制。
共享 clean 参考是原始 Qwen2.5-0.5B 基座采样，PPL=1.535880，并非无水印蒸馏学生；其严重重复回答比例为 17.60%，不能把该低 PPL 单独视为更高质量。

## 文件与记录对应

- **未清洗 No Attack**：`wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.jsonl`；评估时间 `2026-10-19T17:18:39+08:00`；[原始完整 JSON](C:/Users/wenxin/Desktop/distall-watermark/my_easygad/wm_test/detection_metrics_history.md:16884)。
- **Para**：`wm_test/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta3_new1_qwen2_5_0_5b_dolly15k_test.jsonl`；评估时间 `2026-10-19T17:16:58+08:00`；[原始完整 JSON](C:/Users/wenxin/Desktop/distall-watermark/my_easygad/wm_test/detection_metrics_history.md:15849)。
- **WN strength=2.5**：`wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new.jsonl`；评估时间 `2026-10-19T17:20:18+08:00`；[原始完整 JSON](C:/Users/wenxin/Desktop/distall-watermark/my_easygad/wm_test/detection_metrics_history.md:17917)。
- **WN strength=3**：`wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new_strength3.jsonl`；评估时间 `2026-10-19T17:21:42+08:00`；[原始完整 JSON](C:/Users/wenxin/Desktop/distall-watermark/my_easygad/wm_test/detection_metrics_history.md:18962)。

## 结果解读

三种清洗结果的原方向 TPR 均明显降低，且 PPL 均低于 No Attack。Para 的 AUROC 最接近 0.5、Dolly ROUGE-L 最高；WN 两组的原方向检出率更低，且其分组 p 在剔除严重重复回答后仍较高。
WN strength=3 的 PPL 最低、TPR@5% 最低，但严重重复回答比例升至 7.00%，两种 ROUGE-L 均低于 WN strength=2.5；strength=2.5 的 TPR@10% 略低（5.00% 对 5.20%）。因此不能仅用 PPL 或单侧 p 宣称某方法全面更优。
