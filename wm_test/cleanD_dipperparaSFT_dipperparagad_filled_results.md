# 指定 Warmup / GAD 输出的结果汇总

按 `detection_metrics_history.md` 中 2026-10-29 16:50:13（warmup）和 16:58:32（GAD）的评估记录填写。每份生成文件均为 500 条；Seq-Rep-3 两列依用户要求仅报告已有结果，未补算。

| 模型/方式 | AUROC | TPR@FPR≤5% | TPR@FPR≤10% | ROUGE-L（原始Dolly） | 500条采样文本ROUGE-L（和clean教师比较） | 严重重复输出¹ | Seq-Rep-3 | Seq-Rep-3平均数 | ppl中位数² | p-value中位数1ktoken | p-value中位数2ktoken | p-value中位数3ktoken | p-value去重后中位数1ktoken³ | p-value去重后中位数2ktoken³ | p-value去重后中位数3ktoken³ |
| :---: | ---: | ---: | ---: | ---: | ---: | ---: | :---: | :---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| warmup | 0.535000 | 7.20% | 11.20% | 0.197498 | 0.248975 | 48/500（9.60%） | 未统计 | 未统计 | 4.497939 | 0.659574 | 0.853420 | 0.761817 | 0.449672 | 0.437794 | 0.565270 |
| gad | 0.552234 | 6.20% | 10.00% | 0.230625 | 0.262990 | 28/500（5.60%） | 未统计 | 未统计 | 3.872479 | 0.352168 | 0.127002 | 0.0118824 | 0.562848 | 0.544344 | 0.668105 |

¹ 严重重复：回答内部相邻 token 对重复比例 `1 - 唯一相邻token对数 / 全部相邻token对数 > 0.5`，不计 prompt。两种 ROUGE-L 均为同批 500 条回答的逐条 F1 等权平均，`use_stemmer=True`。

² PPL 使用固定 Llama-3-8B 参考模型；本表是逐回答 PPL 中位数，不是 token 加权总体 PPL。warmup 纳入 500 条有效回答；GAD 纳入 499 条，另有 1 条空回答被排除。

³ 本表沿用用户表头“去重后”，但数值对应已有 MD 的“剔除严重重复回答后重新分组”：warmup 保留 452 条，GAD 保留 472 条；组内没有做 token 对去重。建议正式报告将后三列表头改为“剔除严重重复回答后的 p-value 中位数”，避免与逐回答 unique-token-pair 去重混淆。分组中位数为完整 1000/2000/3000-token 块各自 p-value 的普通中位数，尾部不足一组丢弃，每组首 token 仅作上下文。

TPR@FPR≤5% 对应的实际 FPR：warmup 为 4.6%，GAD 为 5.0%；10% 列两者实际 FPR 都为 10.0%。AUROC/TPR 使用全样本原始 z-score，与现有历史记录保持一致。

## 来源和核对

- Warmup：`detection_metrics_history.md` 第 19782–19867 行；具体原始分组 p 在 19821–19823 行、筛选后分组 p 在 19843–19845 行。
- GAD：`detection_metrics_history.md` 第 21122–21208 行；具体原始分组 p 在 21161–21163 行、筛选后分组 p 在 21183–21185 行。
- 输入：`cleanD_dipperparaSFT_dipperparagad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl`、`cleanD_dipperparaSFT_dipperparagad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl`。
- 已核对每份生成文件与其分组/PPL 缓存源哈希（LF 规范化后）；从逐组 p-value 和逐回答 PPL 缓存复核中位数，并独立复核 AUROC 与两个 FPR 工作点。未重新生成文本、未重新运行模型。
- 文件名含 `cleanD`，但两份输出元数据中的实际模型路径均为 `checkpoints/kgwD_paraSFT_paraGAD_v1/{warmup,gad}/global_step_1813/actor/huggingface`。本表只标识指定输出及其已有指标，不能由文件名独立认定判别器训练数据为 clean。
