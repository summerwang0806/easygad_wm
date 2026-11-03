# SQuAD 1.1：已下载结果检查与引用

检查日期：2026-11-02。未修改用户提供的预测、参考答案、模型配置或评测代码。

本报告记录的是调整前的 **0-shot** 结果；随后入口增加了默认固定 **3-shot** 协议，具体设置见上一级 README。两种协议应分开报告，以下历史数值不变。

2026-11-03 更新：入口默认已恢复 **0-shot**，3-shot 仅保留为显式复现实验选项。

## 实际结果

两组都是同一数据 SHA256、同一 10570 个问题；chat、0-shot、greedy、输入上限 4096、输出上限 64、WN 关闭。

| 模型结果 | EM / 100 | F1 / 100 | 完全匹配数 | 输出达到上限 |
|---|---:|---:|---:|---:|
| `te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_new/gad` | 0.170293 | 29.263649 | 18 / 10570 | 237（2.24%） |
| `te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_new1_dipper2stage/gad` | 0.643330 | 24.712055 | 68 / 10570 | 463（4.38%） |

第一组目录：`C:/Users/wenxin/Desktop/elta3_new_gad_global_step_1813_actor_huggingface.0b9e5135c9c1b918/`。
第二组目录：`C:/Users/wenxin/Desktop/per2stage_gad_global_step_1813_actor_huggingface.26a446b88671e909/`。

已逐条重新计算 EM/F1，核对 `scores.jsonl`、`predictions.json` 与 `generations.jsonl`，全部一致。
第一组的两个 runs 使用相同预测；较晚一次复用全部 10570 条缓存，不能作为独立重复实验。

## 为什么 EM 接近零

主要可见问题是答案格式：学生常输出完整句子，而标准 EM 要求归一化后的完整输出匹配参考短答案。
预测归一化词数中位数分别为 12、13；最短参考答案的词数中位数为 2。

真实示例（第一组，问题 ID `56be4db0acb8001400a502ec`）：

- 问题：Which NFL team represented the AFC at Super Bowl 50?
- 参考：`Denver Broncos`
- 输出：`The AFC champion team at Super Bowl 50 was the Denver Broncos.`
- 标准评分：EM=0，F1=33.3333/100。这句话包含正确队名，但不是要求的答案片段。

归一化后包含至少一个完整参考答案词序列的预测为 7966/10570（75.36%）与 6536/10570（61.84%）。
这是诊断字符串统计，不是标准指标或语义准确率；包含答案不能保证陈述正确。
输入长度为 94–870 token，没有触及 4096 上限；少量输出截断不足以解释近零 EM。

也有实际内容错误。例如问题 `Which NFL team won Super Bowl 50?`，参考 `Denver Broncos`，
第二组输出 `The NFC champion Carolina Panthers won Super Bowl 50.`。
因此不能把低分全部归因于格式，也不能把第二组 EM 稍高解释为总体能力更强。
F1 从 29.2636 降为 24.7121，差值为 -4.5516 分；该差值仍混合了回答内容、长度和风格影响。

标准归一化只移除 ASCII 标点。弯引号、Unicode 连接号等也会影响词重合；这符合当前官方规则，
不应悄悄扩大归一化范围后仍称结果为同一标准 EM/F1。

## 单位与指标

- 终端、`summary.json` 的 `exact_match` / `f1`：0–100，越高越好。
- `exact_match_fraction` / `f1_fraction` 与逐题评分：0–1。
- EM：按官方规则规范化后，整段预测是否与任一人工参考完全相同；按题平均再乘 100。
- F1：规范化后按词计数的重合计算 precision、recall 和调和平均；每题对多参考取最高 F1，再按题平均乘 100。
- 这里的词不是 Qwen tokenizer 的 subword token；F1 也不是二分类的类别 F1 或语义相似度。

SQuAD 1.1 是英文阅读理解数据集：输入英文 Wikipedia 段落与问题，回答段落中的答案片段。
本项目评测公开 dev 的 10570 题，直接由学生生成答案；没有为学生额外做 SQuAD 监督训练。

## 原论文核实的可引用成绩

下列全为 SQuAD 1.1 dev/validation，单位 0–100。均有任务监督训练，不能当作当前 zero-shot 学生的预期分数。

| 论文 | 模型 | EM | F1 | 原文位置与设置 |
|---|---|---:|---:|---|
| Devlin et al., 2019 | BERT-Base | 80.8 | 88.5 | Table 2；监督微调，抽取答案起止位置 |
| Sanh et al., 2019 | DistilBERT | 77.7 | 85.8 | Table 2；使用 arXiv v4 修订版数值 |
| Sanh et al., 2019 | DistilBERT (D) | 79.1 | 86.9 | Table 2；SQuAD 微调阶段增加蒸馏 |
| Jiao et al., 2020 | TinyBERT4 | 72.7 | 82.1 | Appendix B，Table 6；任务蒸馏、抽取式 QA |
| Jiao et al., 2020 | TinyBERT6 | 79.7 | 87.5 | 同上 |
| Raffel et al., 2020 | T5-Small (60M) | 79.10 | 87.24 | Table 14；生成式、经过任务训练 |
| Raffel et al., 2020 | T5-Base (220M) | 85.44 | 92.08 | 同上 |

来源与正式引用：

1. Rajpurkar, P., Zhang, J., Lopyrev, K., and Liang, P. (2016). *SQuAD: 100,000+ Questions for Machine Comprehension of Text*. EMNLP, 2383–2392. [原文与 BibTeX](https://aclanthology.org/D16-1264/)。任务与指标引用此文，§6.1 定义 EM/F1。其原始实验 Table 5 明确使用 v1.0，不应把该表的旧基线改标为 1.1。
2. Devlin, J., Chang, M.-W., Lee, K., and Toutanova, K. (2019). *BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding*. NAACL-HLT, 4171–4186. [原文与 BibTeX](https://aclanthology.org/N19-1423/)。Table 2 在印刷页 4177。
3. Sanh, V., Debut, L., Chaumond, J., and Wolf, T. (2019). *DistilBERT, a distilled version of BERT: smaller, faster, cheaper and lighter*. [arXiv:1910.01108](https://arxiv.org/abs/1910.01108)。核实版本为 v4，PDF 第 3 页 Table 2；不要混用旧版本指标。
4. Jiao, X., et al. (2020). *TinyBERT: Distilling BERT for Natural Language Understanding*. Findings of EMNLP, 4163–4174. [出版页与 BibTeX](https://aclanthology.org/2020.findings-emnlp.372/)，[含附录 PDF](https://arxiv.org/pdf/1909.10351)。Appendix B、Table 6。
5. Raffel, C., et al. (2020). *Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer*. JMLR, 21(140), 1–67. [原论文](https://jmlr.org/papers/volume21/20-074/20-074.pdf)。Table 14 在论文第 39 页，caption 特别注明 SQuAD 使用 validation。

论文方法表述示例：

“We evaluate reading comprehension on the SQuAD 1.1 development set using normalized Exact Match (EM) and word-overlap F1 (Rajpurkar et al., 2016). All student models are evaluated with the same zero-shot generative prompt and decoding configuration.”

DistilBERT/TinyBERT 可支持“蒸馏研究也采用 SQuAD EM/F1 评价学生”；T5 可支持“生成式模型也可以用 EM/F1”。
引用这些成绩时需明确它们是经过任务训练的参考结果，而不是与本项目同设置的基线。

## 下一步建议

保留当前原始预测和标准分数。先用 SQuAD train 中固定的少量短答示例明确输出格式，
在小规模样本上检查是否稳定只输出答案片段，再用统一协议重新评估所有对照。
不要依据参考答案截取模型输出中的“最优短语”，也不要将包含参考答案的比例改称准确率。
若更改提示，应标明新的 few-shot/生成协议，与现有 zero-shot 结果分别报告。

详细统计见同目录 `20261102_saved_results_audit.json`；可复制引用条目见 `squad_references.bib`。
