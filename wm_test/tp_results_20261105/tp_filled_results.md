# TP Warmup / GAD 结果汇总

核对日期：2026-11-05。每份输出均为 500 条，模型 checkpoint 为相应阶段的 global_step_1813；推理阶段未额外施加 KGW 或 WN 偏置。

| 模型/方式 | AUROC | TPR@FPR≤5% | TPR@FPR≤10% | ROUGE-L（原始Dolly） | ROUGE-L（clean教师） | 严重重复输出 | Seq-Rep-3均值 | Seq-Rep-3中位数 | PPL中位数 | LLM judge vs clean GAD | LLM judge vs clean教师 | LLM judge vs KGW教师 | LLM-MT-Bench | p中位数1k | p中位数2k | p中位数3k | 剔除严重重复后p中位数1k | 剔除严重重复后p中位数2k | 剔除严重重复后p中位数3k |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| warmup | 0.418420 | 4.80% | 7.20% | 0.166714 | 0.229723 | 108/500（21.60%） | 0.222037 | 0.068682 | 3.163390 | — | — | — | — | 0.982988 | 0.999495 | 0.999957 | 0.959081 | 0.994909 | 0.996744 |
| gad | 0.447162 | 3.40% | 5.80% | 0.207037 | 0.257639 | 43/500（8.60%） | 0.114053 | 0.043651 | 3.171506 | — | — | — | — | 0.913158 | 0.976737 | 0.978664 | 0.939464 | 0.943857 | 0.983718 |

## 计算口径

- 检测参数：gamma=0.5、delta=3、hash_key=15485863。正类为 TP 学生输出，负类为同批 500 条原始未训练 Qwen2.5-0.5B 输出。两阶段 5% 工作点实际 FPR 均为 4.6%，10% 工作点实际 FPR 均为 10.0%。
- ROUGE-L 为同题逐回答 F1 的等权平均；英文小写/字母数字分词、长度大于 3 的词做 Porter stemming，采用 LCS。独立实现与保存的评估结果一致。参考实现：[Google ROUGE scorer](https://github.com/google-research/google-research/blob/master/rouge/rouge_scorer.py)、[tokenize](https://github.com/google-research/google-research/blob/master/rouge/tokenize.py)。
- 严重重复为回答内部相邻 tokenizer token 对的重复比例 > 0.5，不含 prompt；依据绑定相同源文件哈希的逐回答缓存复核。
- Seq-Rep-3 按 answer.split() 的词级三元组计算，保留大小写和标点，不跨回答，均值和中位数均使用全部 500 条。
- PPL 为固定 Llama-3-8B 参考模型的逐回答 PPL 中位数，两个阶段各 500 条有效记录；不是 token 加权总体 PPL。已核对缓存的来源哈希、回答哈希和 NLL/PPL 数值。
- 表中后三列对应原表的‘去重后’，实际是剔除严重重复的整条回答后重新拼接、按精确 1k/2k/3k token 块分组。Warmup 保留 392 条，GAD 保留 457 条；组内没有去除重复 token 对。不要与 unique-token-pair 检测混称。
- 原始分组数 Warmup 为 179/89/59，GAD 为 87/43/29；筛选后为 57/28/19 和 55/27/18。每块首 token 只作上下文，尾部不足一块丢弃，最后对完整块的 p-value 取普通中位数。
- 四项 LLM judge / MT-Bench 指标未发现本次实验的对应结果，留空，不用 ROUGE 或 PPL 替代。
- p-value 接近 1 表示当前单侧正向 KGW 检验缺乏证据，不是‘无水印概率’。AUROC 小于 0.5 反映打分方向上的偏移，不足以证明所有检测方法都无法识别。

## 对照与解读

TP GAD 的正向检测明显弱于匹配的无攻击 GAD：AUROC 0.647688 → 0.447162，TPR@FPR≤5% 11.4% → 3.4%，TPR@FPR≤10% 22.8% → 5.8%。
TP GAD 相比 TP Warmup，ROUGE-L（Dolly）0.166714 → 0.207037、ROUGE-L（clean教师）0.229723 → 0.257639，严重重复 21.6% → 8.6%，Seq-Rep-3 均值 0.222037 → 0.114053。GAD 改善了这组 TP 学生的文本质量指标。
相对无攻击 GAD，TP GAD 的 clean 教师 ROUGE-L 从 0.309174 降至 0.257639，严重重复从 2.2% 增至 8.6%，说明去水印伴随质量代价。与 clean GAD 的 0.330629 相比，词序重合也更低；还需要 LLM judge 评估内容正确性和实用性。
PPL 中位数 Warmup/GAD 约 3.163/3.172，基本不变；不能以较低 PPL 单独判断回答更正确，特别是这里仍有明显重复。

## 来源

- warmup：`tp2.5warmup_tp2.5gad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl`；评估时间 `2026-11-05T17:07:34+08:00`；LF SHA-256 `e684a9f3b2c95b2b4a79ce8f2efe0fdc6e933d89ee3f803dc905ef4178b8dd53`。
- gad：`tp2.5warmup_tp2.5gad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl`；评估时间 `2026-11-05T16:55:46+08:00`；LF SHA-256 `6cf1a473eeaf8a29b5217268f17c055fbdb8d101dd50dab5ed4c76561890416d`。
- 原始评估历史：`wm_test/detection_metrics_history.md`。精确值、缓存配置和逐回答 ROUGE 见同目录 `tp_metrics.json`。
- 仅分析已下载文件，未重新生成回答、训练模型或调用外部裁判。
