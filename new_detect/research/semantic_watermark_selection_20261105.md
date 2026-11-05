# 语义水印 baseline 选型：Qwen / Dolly / EasyGAD

调研日期：2026-11-05。范围：自回归文本生成水印，重点是蒸馏/GAD 后的模型残留。本文是文献和源码选型，不是模型运行结果。已有 KGW 数据不含 SIR/PMark 信号，不能直接拿来验证这些水印的放射性。

**范围修订（用户后续决定）：先做好token级水印，核心转为抽取“语义如何决定种子/偏置”。下文SIR+PMark是此前广义覆盖建议，不再是当前执行优先级。当前优先比较Context-aware Watermark with Semantic Balanced Green-red Lists（EMNLP 2024）与SIR，详见[语义条件规则抽取补充](semantic_key_extraction_20261105.md)。句级方法暂缓；这不表示已证明它们残留较弱。**

## 1. 推荐

**优先组合：SIR + PMark-offline。**

- 只实现一个语义方法，先做 SIR：可与现有 token 偏置路线比较，官方推荐 MarkLLM，生成和检测实现清楚。
- 已有/准备做 SIR，再增加一个不同机制的方法，优先 PMark-offline：真正按句子 embedding 选择候选，提供多通道证据，官方代码已有 vLLM 后端。
- 时间很紧、只想快速探索语义统计能否被学生学到，可先做 cosine-SimMark。但它默认使用固定相似度区间，不能单凭阳性检测完成某个教师/提供方的独有归因，不宜作为唯一的溯源 baseline。
- k-SemStamp 是经典句级对照，可作为第三项；不建议第一轮同时实现原版 SemStamp、k-SemStamp 和多个 SIR 变体。

这里的“优先”是针对本项目可解释性、机制覆盖、代码接入成本的判断，不是声称 PMark 已被证明最有放射性，也不是跨论文性能排名。

## 2. Domain Brief / 证据边界

**来源支持：** SIR/SemaMark/Adaptive 使用语义决定 token 分布；SemStamp/k-SemStamp/SimMark/PMark 使用句级语义采样；AliMark重点处理分句合句后对齐问题。下文均链接原论文或作者代码。

**推断：** 本项目先使用 SIR，再补充 PMark-offline，可以区分语义条件下的选词偏好与整句语义偏好是否通过训练传递。PMark多通道在短文本上可能比每个句子对一个统计量更有用，但这必须实测；各通道不是可随意当作独立样本。

**未知：** 这些候选在 Qwen2.5-14B-Instruct → Qwen2.5-0.5B、Dolly、GAD 中的残留强度、误报率和数据生成速度。本次没有核实到能直接回答该精确设置的实验证据；这不构成“无人研究”的结论。原始 Radioactivity 的 G.1 未评估语义类方法，不能作为其放射性已被证明的依据。

核心瓶颈是：有足够教师文本水印不等于学生继承；学生输出分数升高也不等于可靠溯源。任务/长度/语义分布变化可能影响零假设。

来源：[Radioactivity G.1](https://arxiv.org/html/2402.14904v2#A7.SS1)。

## 3. 候选比较

| 方法 | 机制与证据单位 | 官方实现检查 | 本项目判断 |
|---|---|---|---|
| SIR，ICLR 2024 | 前文 embedding 经映射得到 token 偏置；token/文本块打分 | 检查了原仓库 README、MarkLLM 的 sir.py 和配置 | 第一项；不能直接使用默认 OPT 词表映射或默认阈值 |
| SemaMark，Findings NAACL 2024 | 池化模型隐藏表示，映射到 NE-Ring 离散区域，再决定 token 绿名单 | README要求替换 Transformers 类/函数，提供 OPT-2.7B checkpoint | 暂缓；迁移 Qwen 的隐藏维度、前向接口和映射训练代价更高 |
| Adaptive Text Watermark，ICML 2024 | 辅助模型衡量熵，在适合的位置施加语义条件偏置 | README、watermark.py；需额外测量模型、embedder、semantic mapping | 第二轮质量/熵消融；第一轮比 SIR 增加更多混杂因素 |
| SemStamp，NAACL 2024 | LSH 划分句子 embedding 空间，拒绝采样合法区域 | 官方共同仓库提供生成、检测、微调 embedder | 经典，但生成重试和边界约束成本较高 |
| k-SemStamp，Findings ACL 2024 | k-means 取代 LSH；前一句簇控制下一句合法集合 | 官方共同仓库；有 embedder、centroids 和多卡说明 | 经典句级备选；需冻结匹配的 encoder/centroids，不直接复用 C4 分布假设 |
| SimMark，EMNLP 2025 | 相邻句 embedding 相似度/距离落在固定区间；soft counting | README、sampling.py、sampling_utils.py、detection.py 均已检查 | 最简单句级探针；建议 cosine/no-PCA 起步，但其固定区间签名并非提供方独有标识 |
| PMark，ICLR 2026 | embedding 对 pivot 的代理分数，多通道约束；online估中位数，offline用先验 | README、pmark.py、detect.py、utils/sample.py、utils/detect.py、gen.sh 已检查 | **SIR之外第一优先，先做offline并明确标注变体** |
| AliMark，ICML 2026 | 语义映射成位序列，检测时重构分句并自适应对齐 | README、alimark.py 已检查；官方vLLM后端，默认12句、64候选 | 若重点评测DIPPER合句/拆句，值得第三阶段加入；初版检测/校准更复杂 |

上述“检查”指静态源码审查；没有下载权重、安装候选依赖或完成 GPU 运行。

论文与代码：

- SIR：[论文](https://arxiv.org/html/2310.06356v3)，[原作者仓库](https://github.com/THU-BPM/Robust_Watermark)，[推荐实现](https://github.com/THU-BPM/MarkLLM/tree/main/watermark/sir)。
- SemaMark：[论文](https://aclanthology.org/2024.findings-naacl.40/)，[代码](https://github.com/renjie3/SemaMark)。
- Adaptive：[论文](https://proceedings.mlr.press/v235/liu24e.html)，[代码](https://github.com/yepengliu/adaptive-text-watermark)。
- SemStamp：[论文](https://aclanthology.org/2024.naacl-long.226/)，[共同代码](https://github.com/abehou/SemStamp)。
- k-SemStamp：[论文](https://aclanthology.org/2024.findings-acl.98/)，[共同代码](https://github.com/abehou/SemStamp)。
- SimMark：[论文](https://aclanthology.org/2025.emnlp-main.1567/)，[全文](https://arxiv.org/html/2502.02787)，[代码](https://github.com/DabiriAghdam/SimMark)。
- PMark：[正式论文入口](https://proceedings.iclr.cc/paper_files/paper/2026/hash/2d8911db9ecedf866015091b28946e15-Abstract-Conference.html)，[全文](https://arxiv.org/html/2509.21057)，[代码，旧PMark-repo地址已重定向](https://github.com/Z1zs/PMark)。
- AliMark：[论文](https://arxiv.org/html/2605.29434)，[代码](https://github.com/imethanlee/AliMark)。

## 4. 补查的新方法和相关变体

- **X-SIR，ACL 2024**：面向跨语言一致性。若主任务仍是英文Dolly、同语言蒸馏，优先级低于增加独立句级机制；做翻译攻击时再加入。[论文](https://aclanthology.org/2024.acl-long.226.pdf)，[作者代码](https://github.com/zwhe99/X-SIR)。本次核对论文/代码入口，没有深入审查实现。
- **SWAN，ACL 2026**：AMR结构模板引导生成，检测需要AMR parser。与原回答任务内容和事实保真的相容性需要额外验证，因此不作为首批。[作者页面](https://www.amazon.science/publications/swan-semantic-watermarking-with-abstract-meaning-representation)，[全文](https://arxiv.org/html/2605.04305)。
- **SemanticShift，AAAI Spring Symposium Series 2026**：免训练的候选token语义位移路线；本次核对官方论文入口，没有完成源码或Qwen运行核验，不凭摘要性能优先于已审查的实现。[官方论文](https://ojs.aaai.org/index.php/AAAI-SS/article/view/42577)。注意是Spring Symposium Series，不写成AAAI主会。
- **SemField，2026-10预印本**：连续的密钥语义方向及文档级累计信号，机制值得关注；论文公开链接对应GitHub API在本次请求返回404，尚未核实可运行代码，先保留观察。[论文](https://arxiv.org/html/2610.11848)。这不表示代码永久不可用。
- **DenMark，2026预印本**：面向diffusion语言模型；当前Qwen自回归训练链不匹配，不作为本次候选。[论文](https://arxiv.org/abs/2609.14257)。

## 5. 本地接入审查

已阅读 `wm_data/generate_teacher_data.py`、`wm_data/kgw.py`、`wm_data/README.md` 和 `new_detect/README_reading.md`。

当前生成器只接受none/kgw，采用vLLM SamplingParams和token logits processor，并以源Parquet schema为契约，仅替换teacher_response。这些输出/断点约束应复用。

### SIR的关键适配

1. **词表映射**：MarkLLM默认配置引用50272映射；Qwen必须生成与实际logits/token ID空间匹配的映射，记录seed、文件hash，拒绝错长文件。MarkLLM缺文件时使用随机数生成映射；不能依赖未固定的进程随机状态。
2. **上下文一致性**：生成器使用prompt+response，检测器输入如何包含prompt、跳过首块、如何切词/分块必须一致。聊天模板和逐块重编码也需核对，不能直接把普通generate示例搬过来。
3. **算力**：官方MarkLLM logits processor每步调用语义模型；不会自动获得现有KGW的吞吐。先用HF做参考一致性，再评估vLLM和缓存，缓存必须保持相同上下文和偏置。
4. **分数**：检查到detect_watermark返回的所谓z_score实际是token偏置均值；不要把它当标准正态z后调用norm.sf。

来源：[sir.py](https://github.com/THU-BPM/MarkLLM/blob/main/watermark/sir/sir.py)，[SIR.json](https://github.com/THU-BPM/MarkLLM/blob/main/config/SIR.json)。

### PMark-offline的关键适配

1. 官方 `median_method=prior` 对应offline；优先固定该变体，不把online理论保证自动套到offline。先验中位数在Dolly上可能偏离。
2. 官方生成器支持vLLM，但其数据是续写式text输入；需要接入Dolly chat template，正确处理EOS、列表和回答边界。
3. 句子编号、secret bit序列、pivot向量、encoder必须在生成/检测中保持同一约定，按回答重置；不得错误地用数据集行号替代句子编号。
4. 检查到多通道prior底层检测分支无需重新采样LLM，但原detect.py入口仍初始化生成模型。可以进行延迟加载适配；须与官方分数做一致性核对。
5. 官方脚本依赖生成时log里的句子。学生评测必须从实际回答文本重新分句；不得把教师隐藏的句子边界当作黑盒检测已知信息。
6. 候选预算、无完整句/EOS、候选不足、重试/回退都要记录。达到上限的句子不能悄悄当作成功嵌印。

来源：[pmark.py](https://github.com/Z1zs/PMark/blob/main/pmark.py)，[detect.py](https://github.com/Z1zs/PMark/blob/main/detect.py)，[sample.py](https://github.com/Z1zs/PMark/blob/main/utils/sample.py)，[底层检测](https://github.com/Z1zs/PMark/blob/main/utils/detect.py)。

### Dolly短回答问题

本次对已有14B KGW newtrain/newtest做了标点启发式统计：按句末`.!?`后空白切分，不是官方NLTK分句，缩写/列表可能误分，仅用于粗筛。

| 文件 | 回答数 | 最多1句 | 最多2句 | 最多3句 |
|---|---:|---:|---:|---:|
| newtrain | 14,511 | 2,388 (16.46%) | 3,896 (26.85%) | 5,230 (36.04%) |
| newtest | 500 | 66 (13.2%) | 117 (23.4%) | 160 (32.0%) |

本机NLTK因缺少regex包未能导入，因此没有冒称官方分句计数，也未为本次调研改动依赖。统计来自KGW回答，不等于未来SIR/PMark数据的真实句数。

这意味着相邻句统计的有效证据可能有限；PMark多通道也不能保证自动解决短文本问题。正式评估应同时报告全部回答和预先确定的长度分层。不能强迫所有答案扩写到12句，或者只删掉难检测的短答案后报告总体效果。跨回答累计时不能创造跨回答的相邻句关系。

## 6. Source Audit

| 决策性主张 | 来源类型与支持 | 限定 |
|---|---|---|
| SIR可作为语义条件token偏置baseline | 原论文+作者推荐代码，直接支持 | Qwen/vLLM迁移和蒸馏效果未运行 |
| PMark支持online/offline，官方有vLLM后端 | 原论文§4+作者源码，直接支持 | 不把offline先验视为普适真值 |
| SimMark容易实现相邻句语义统计 | 原论文+源码，直接支持 | 固定区间不构成独有教师归因；阈值需迁移校准 |
| SemaMark官方接入侵入性较高 | 官方README，直接支持 | 对Qwen的实际工时仍是工程估计 |
| 选择SIR+PMark最适合本项目首轮覆盖 | 上述证据+本地代码，迁移推断 | 不构成实测优劣或放射性排序 |
| SIR/PMark经GAD仍有放射性 | 本次没有直接证据 | 只能作为可检验假设 |

## 7. 两周pilot与决策门槛

**核心问题**：固定教师能力、训练预算和质量约束时，token级语义条件偏置与句级语义选择偏好能否通过SFT继承，GAD是否进一步削弱它们？

竞争性解释：H1学生学到可泛化水印；H2只记住教师片段；H3分数变化来自长度/主题/分句/检测器偏差。

- 第1阶段：冻结官方版本与资产，构建生成/检测参考一致性检查；用相同prompt做小批clean/SIR/PMark候选预算与质量试跑。200条可用于工程试跑，不能据此可靠声称1%尾部误报已校准。
- 第2阶段：先只比较clean/SIR/PMark的普通SFT学生，保持初始化、训练条数和更新预算可比。SIR/PMark各做两个预先指定的密钥/映射重复用于探索稳定性；这不是强多密钥统计保证。
- 第3阶段：只在教师信号、检测器和SFT链条验证后加入GAD/UP。若不能训练学生，这一轮最多得到文本鲁棒性结论，不能称放射性实验。
- 校准集、调参集、最终测试集分开；同prompt多次采样不能算独立任务；不同训练seed不要混成同一个模型的大样本。
- 每回答分数、AUROC、冻结阈值下TPR/FPR、长度分层、平均候选消耗、事实/指令质量一起报告。500条负例上1%仅约5次误报，需报告二项置信区间；不伪造极小p值。
- 模型级累计另设固定的回答数/token预算，按回答或prompt分组建立clean零分布；不得直接沿用KGW的独立二项检验，也不把全部句子跨回答拼接。
- 若teacher水印正常，学生仅在训练prompt/原文续写中偏高而新prompt无效，优先解释为记忆或局部继承；若clean也高分，优先修复校准；若合理预算下教师数据严重丢失事实/无法生成，则暂缓该配置。

最强质疑：方法在Dolly短回答上没有足够检测能力，或检测到了任务分布差异而非水印。对此，预先确认教师端可检性、匹配clean对照、长度分层和错密钥敏感性分析。错密钥结果是辅助证据，不能单独提供任意小的p值。

当前决定：推进SIR与PMark-offline的参考适配；本次仅完成调研，未修改训练/生成/检测生产代码，未启动训练。

## 8. 源码版本记录

调研时读取main并随后核对HEAD；实际实现时应按下列SHA重新固定文件与资产，不依赖移动分支。

| 仓库 | 调研时HEAD |
|---|---|
| THU-BPM/MarkLLM | 0a4fe8c642b31b8a8c4993615b1c70a0c300d918 |
| abehou/SemStamp | 97db73d11fd80f376a02b0a604d500627622f7e6 |
| DabiriAghdam/SimMark | 8b91c97cc1d8cc4a219917cdff628ae750f8dd5a |
| renjie3/SemaMark | b14888959b660a19b2533c506de77acfc145f97b |
| Z1zs/PMark | 75140fe7142f88c51ba50984d9eb07f44f5961b3 |
| imethanlee/AliMark | 975039c390078e17b913dc88f5e873a3f62fdf37 |
