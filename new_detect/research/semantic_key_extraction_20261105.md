# Token级语义水印：抽取语义条件规则

日期：2026-11-05。用户将方向收窄为token级水印，句级方法暂缓。目标是理解并抽取语义条件下的token偏置；句级放射性较弱目前仍是假设。

## 已核实机制

### Context-aware Watermark with Semantic Balanced Green-red Lists for Large Language Models

EMNLP 2024：[论文入口](https://aclanthology.org/2024.emnlp-main.1260/)，[全文](https://aclanthology.org/2024.emnlp-main.1260.pdf)。

原文§3.2明确以**上一token的LLM输入embedding**表示context，再用随机超平面LSH获得离散种子。不是对整段前文做句子编码，也不是使用当前上下文中的最后层hidden state。论文将全词表token→key映射预先保存，检测时查询。

§3.3另有一层：按语义集合分别划分绿/红名单，再合并，保证语义覆盖；§3.4另有动态偏置。不能把“语义生成种子”当成完整方法，也不能假设同义词因此必然同为绿色。

抽象：`previous_token → static_embedding → LSH_bucket → balanced_green_red_partition → token_bias`。

### SIR

[论文§4](https://arxiv.org/html/2310.06356v3#S4)。

抽象：`prefix → semantic_encoder → trained_mapping → vocabulary_bias_vector`。不需要先产生离散LSH种子；官方实现还包含分块、缩放和词表映射，复现必须与检测保持一致。

## 对现有规则抽取的含义

本地`baseline_acl/steal_watermark.py`当前按短token前缀收集上下文，先平均W/O下一token概率，再计算比例；`max_ngram=1..3`对应前缀长度0..2。它已经能表达前一个token条件下的规律，但不能直接表达SIR的整个语义上下文映射。

- 对LSH方法：上一token查表仍然是有效基线，无须先知道LSH。增量是发现不同token具有相同/近似的水印偏置，将它们合并统计，帮助低频token，而不是只会重新得到旧前缀表。
- 已知真实embedding、超平面和词表分组时，按真实bucket合并属于oracle条件，不是黑盒恢复。没有这些资产时，只用公开代理encoder分桶也只是替代划分。
- 对SIR：学习连续的`semantic_feature → token_bias`代理模型更贴近其机制；不能把“恢复LSH”统一套用到SIR。
- 需要抽取可迁移的**有效偏置函数**，不一定唯一恢复真实超平面、网络参数或原始秘密。多个不同参数化可产生相同可观测偏好。

## 最小判别实验

先在LSH方法上比较三组，固定可用教师查询/训练文本预算、实际tokenizer与测试划分：

1. 原有逐token前缀规则表。
2. 真LSH桶合并的oracle规则表：仅给分组标签，偏置仍从同一预算数据估计；完整真绿名单另外用于评估上限。
3. 不使用真实桶/绿名单标签的学习分组或语义条件代理。

先测试原教师上能否恢复，再测普通SFT学生留下的偏置，最后进入GAD/UP/WN。原教师可恢复但学生不可恢复，可能是学生未继承或信号不足；不能据此断言语义生成机制不可恢复。

三个竞争解释：语义分组确实共享水印规则；规则表只记住高频token；提取到的是正常语言/微调任务偏好。需要同类clean微调对照、匹配上下文和token频率控制。

预先分出少见/未用于拟合的context-token测试组，并用不同完整前文测试同一上一token。真正的规则共享应在这些场景有帮助；若只在已见token/原文有效，则尚不能说明抽取了语义机制。

用embedding近邻代表“同桶”并无保证，LSH边界和下游PRNG会产生不连续性。按观察偏置向量聚类时，也需防止token概率稀疏和自然语义关联导致伪聚类。

评估包括真绿名单/偏置的恢复质量、held-out预测和下游去水印/质量权衡。仅靠水印检测分数下降，不能证明规则恢复准确；已知真实规则仅用于oracle和最终评估，不能泄漏到黑盒拟合中。

## 当前决定与边界

当前顺序：先验证LSH语义种子的规则共享，再以SIR检验连续映射能否迁移。SIR作为现成官方实现可并行用于复现准备，但本次未核实该EMNLP方法可运行的作者代码，未宣称已完成复现。所有抽取收益、放射性和GAD效果尚待实验。本轮仅核对论文和本地已有抽取接口，没有修改生产代码或启动训练。
