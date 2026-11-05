# 可迁移检测器调研

调研日期：2026-11-05。对象：现有 Qwen2.5 学生、KGW simple_1、k=1、gamma=.5、delta=3。
当前各训练/攻击设置均视为探索，不视为已确定的最终方案。

## 结论与证据边界

- 来源支持：EWD、WinMax、Signature filtering可用于KGW类文本；WM-Basin直接研究蒸馏溯源并测试KGW。
- 迁移推断：前三者可能检出我们的蒸馏残留，实际收益未知；直接生成水印文本的实验不等同于蒸馏后的弱残留。
- 待验证：本项目独立测试集TPR/FPR、WN下的表现、代码移植与CUDA PRNG一致性、计算成本。
- 不预先假定去水印必然严重伤害质量；通过统一检测权限、预算及质量评估测量权衡。

## 首选：EWD

论文：An Entropy-based Text Watermarking Detection Method，ACL 2024。

- 用模型计算spike entropy，给token加权，再计算加权绿名单统计量；不需要重新训练学生。
- 可复用wm_test/wn回答，需额外前向补算熵；当前token/预测缓存只有ID和绿标记，不足以还原熵。
- 默认按论文确定评分模型；改用固定clean代理模型必须标为适配，并用独立clean样本校准。
- 首先保持逐回答的评测单位。EWD与Reading组合是进一步扩展，不能称为原论文设定。
- 主要风险：熵加权在直接生成水印文本上有效，不保证蒸馏残留与高熵位置仍有相同关系。

论文：https://aclanthology.org/2024.acl-long.630/

公式/算法：https://arxiv.org/html/2403.13485v2#S4.SS2

官方代码：https://github.com/luyijian3/EWD

## 补充：WinMax / WaterSeeker

WinMax来自 On the Reliability of Watermarks for Large Language Models，ICLR 2024，附录A.9.1。
WaterSeeker来自 Findings of NAACL 2025，为长文档中的局部水印定位提供更高效的搜索。

- 可复用已有文本/逐token绿名单标记，无需学生权重；只有z/G/N汇总时需重新取得逐token标记。
- WinMax搜索最大局部z；WaterSeeker采用定位后检测。它们不会把500条回答合并成39/41个样本。
- 搜索会引入多重比较，不能用最大z直接套普通单次z检验p；用独立clean数据校准整个搜索流程。
- 适用前提是残留呈局部集中；如果整条回答均匀地只有微弱偏好，搜索未必有益。

WinMax论文：https://proceedings.iclr.cc/paper_files/paper/2024/file/d78e9e4316e1714fbb0f20be66f8044c-Paper-Conference.pdf

WaterSeeker论文：https://aclanthology.org/2025.findings-naacl.156/

WaterSeeker代码：https://github.com/THU-BPM/WaterSeeker

## 条件候选：Signature filtering

论文：Signature filtering: A lightweight enhancement for statistical watermark detection in large language models，2026预印本；出版社已有在线文章，卷期标为2027年。

- 用MILP在开发语料上学习不利于检测的token/context签名，计分时屏蔽这些位置；不修改保存文本或重新制造token相邻关系。
- 有KGW实验，且改变的是检测端；现有文本可以复用。
- 与普通去重/教师窗口白名单不同，过滤器是依据密钥和开发数据学习的。
- 学习、阈值校准、最终测试必须分离；应用同一冻结过滤器到水印、攻击和clean组。
- 固定密钥和相关文本下FPR尤其需要实测。论文自己讨论KGW过滤可能人为抬高绿比例的风险。
- 作者声明提供Bitbucket代码，本次未检查该代码是否可完整运行。

预印本：https://arxiv.org/html/2606.18430v1

出版社：https://www.sciencedirect.com/science/article/pii/S0306457326003894

代码入口：https://bitbucket.org/chihduo/llm-signature

## 高相关但成本高：WM-Basin

论文：Watermark Basins: Black-Box Detection of Distilled LLMs，2026-10-27预印本。

- 直接检测蒸馏，使用clean探针梯度、任务子空间投影和多密钥排名。
- 验证者需准备多密钥教师数据和clean模型池；不需要重训被测学生，但需训练探针适配器。
- 不是旧z分数的后处理；完整配置资源大。本次未核实可直接运行的公开代码。
- 其结果来自数学推理设置，迁移Dolly须验证。附录也提供改写等攻击结果，应同时检查检测收益和去水印代价。

论文：https://arxiv.org/html/2610.37266v1

方法：§2.3；资源：B.3/B.4；校准：B.6；改写：D.3。

## 不直接移植的统计检测器

| 文献 | 核对到的机制 | 当前判断 |
|---|---|---|
| A Likelihood Based Approach for Watermark Detection，AISTATS 2025 | 利用密钥随机序列与下一token概率的似然统计 | 原推导围绕Aaronson/Gumbel类生成机制；迁移KGW需重建似然模型 |
| Robust Detection of Watermarks for Large Language Models Under Human Edits，Tr-GoF | Gumbel-max的连续pivot与混合污染检验 | 不能把KGW 0/1绿标记塞入其原公式并沿用保证 |
| Predictive Likelihood Ratios for Language Model Watermark Detection，2026 | predictive alternatives和Gumbel pivot；顺序证据 | 不是已有KGW结果的直接替代品，当前低优先级 |

来源：

- https://proceedings.mlr.press/v258/li25d.html
- https://raw.githubusercontent.com/mlresearch/v258/main/assets/li25d/li25d.pdf
- https://github.com/doccstat/llm-watermark-adaptive
- https://academic.oup.com/jrsssb/article-abstract/88/2/491/8261309
- https://arxiv.org/abs/2411.13868
- https://github.com/lx10077/TrGoF
- https://arxiv.org/abs/2609.15657

## 证据审计与实施次序

| 判断 | 支持程度 | 需要额外实验证明什么 |
|---|---|---|
| EWD能兼容KGW文本检测 | 直接：论文方法及官方代码 | 对本项目蒸馏弱残留是否仍提高独立测试TPR |
| WinMax不要求更改嵌入端 | 直接：论文A.9.1 | 是否存在局部集中残留；搜索整体FPR是否正确 |
| Signature filtering适配KGW | 直接：论文方法与实验 | 不泄漏测试集时能否提升，特别是相关clean样本 |
| WM-Basin针对蒸馏并测试KGW | 直接：论文方法与实验 | 本项目领域/密钥/资源条件下能否重建有效参考库 |
| 以上方法一定提高我们的继承检出率 | 未知 | 统一预算和独立校准/测试后的对照实验 |

建议先做EWD与WinMax，两者在原有逐回答口径下各给一个分数；根据开发集结果固定规则，再做独立测试。
如果clean误报同步升高，或只有增加预算后才改善，不将其描述为同预算检测器增益。
Signature filtering作为第二阶段，WM-Basin先做资源审计。重训学生不是上述检测迁移的默认前提。
