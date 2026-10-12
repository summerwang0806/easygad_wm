用户选择追加 4 次完整 warmup→GAD。目标是在当前 Qwen2.5-0.5B 管线中区分 γ 的影响、δ 的影响、组合条件的放大效应，以及历史差异能否复现。每次从同一原始学生模型开始，独立完成两个阶段。

| 新任务 | γ | δ | 用途 | 建议实验名 |
|---|---:|---:|---|---|
| A | 0.25 | 3 | 与旧 0.25/2 比较 δ；与当前 0.5/3 比较 γ | kgw_factorial_g025_d3_r1 |
| B | 0.5 | 2 | 与旧 0.25/2 比较 γ；与当前 0.5/3 比较 δ | kgw_factorial_g05_d2_r1 |
| C | 0.25 | 2 | 在当前执行环境重做旧稳定端点 | kgw_factorial_g025_d2_repeat |
| D | 0.5 | 3 | 在当前执行环境重做当前崩溃端点 | kgw_factorial_g05_d3_repeat |

这构成 γ∈{0.25,0.5}、δ∈{2,3} 的四格对照。旧结果保留为历史记录，新四格作为同批比较。四格交叉能分别比较两个因素及其交互；设计依据见 [NIST full factorial designs](https://www.itl.nist.gov/div898/handbook/pri/section3/pri333.htm) 和 [two-level designs](https://www.itl.nist.gov/div898/handbook/pri/section3/pri3331.htm)。每格一次仍是探索性筛查，不能估计各格的训练随机方差或崩溃概率。

已有证据：旧端点严重重复 5.2%→1.6%；当前端点 20.8%→99.6%。训练超参数和核心训练代码相同，恢复后当前 GAD 从 warmup1813 权重初始化并从 step1 开始，未加载旧 GAD optimizer。实际教师数据摘要仍待用户返回。模型身份不能由含 14b 的文件名推断。

竞争性解释及判别结果：

| 本轮观察（以端点差异可复现为前提） | 支持的下一步方向 |
|---|---|
| A 较差、B 较好 | δ 从 2 到 3 的影响值得优先查；后续可补 γ=0.5、δ=2.5 |
| A 较好、B 较差 | γ 从 0.25 到 0.5 的影响值得优先查；后续可补 γ=0.375、δ=3 |
| A、B 都较好，只有 D 严重退化 | 组合条件或非线性边界值得查；先补 0.5/2.5，再视结果补 0.375/3 |
| A、B 均严重退化，仅 C 较好 | 两种单独改变都可能触发退化；后续在 C 与坏点间补 0.25/2.5 或 0.375/2 |
| C/D 未复现历史差异 | 优先查数据、初始化、环境及随机性，先重复关键点 |

不要先用二分类“崩/稳”代替数值。主要结果是各阶段 token-pair 严重重复率，以及 GAD放大量 Δ=GAD重复率−warmup重复率；同时比较 ROUGE-L。可在这些响应的百分点尺度上分别计算同 γ 下的 δ 差、同 δ 下的 γ 差，并比较差值是否随另一因素改变。仅两个交叉点正常不自动证明唯一的算法机制。

数据与运行控制：

- 显式记录并指定教师模型及 tokenizer。按目前保存代码与用户命令，默认教师为 `/shared/public_models/Qwen2.5-0.5B`；新任务应显式传 `--model`，避免文件名或默认值歧义。源输入固定 `data/dolly15k_train.parquet`、`data/dolly15k_test.parquet`。
- 若 `teacher_comparison.json` 确认已有端点数据的模型/采样/prompt 来源可比，可以复用已验证文件。若历史教师来源或生成协议仍不能确认，四格用同一显式教师 recipe 生成匹配数据，再训练这四次；不要混用未核实来源的教师数据。
- 新生成数据统一采样 temperature=.7、top_p=.9、top_k=-1、max_prompt_tokens=2048、max_new_tokens=1536、seed=42、hash_key=15485863、simple_1，以及 GPU 并行数。每组独立输出文件和 parts 目录，保留生成 metadata；换 γ/δ 不能复用另一组未完成 parts。
- 四次训练统一同一源码/模型快照、GPU数量、Ray CPU数和软件环境；actor LR=1e-6、critic LR=1e-5、batch8、warmup n1、GAD n2、rollout temperature=.8、prompt2048/response1536、每阶段1epoch，以及原 loss/KL/entropy 设置。
- 每组使用新的实验名和 checkpoint 目录，从原始模型完整训练 warmup，随后用本组 warmup actor/critic 初始化 GAD。新实验首次启动不要 resume；本组中断后才恢复本组 checkpoint。
- 教师/评测 seed42 不是统一训练 seed。当前 launcher 没有统一训练 seed入口；默认 sampler seed1、vLLM engine seed0、设备生成 RNG 使用 DP rank+1000，仍有其他随机状态。保存实际配置与日志，不能把四格一次运行写成多训练 seed 验证。

当前 launcher 的数据路径写在 `scripts/train/run_full_gad_optimized.sh` 的 TRAIN_FILE、VAL_FILE；没有 `--train_file`/`--val_file` 参数，环境同名变量也会被脚本赋值覆盖。仅改 `--exp_name` 会继续训练当前 0.5/3 数据。实际启动前应让每组使用正确的这两个配置值，不需要改训练 loss 或更新算法。

可采用以下路径；名字中的 14b 是兼容历史命名，模型仍以显式 --model 参数为准：

| 任务 | TRAIN_FILE | VAL_FILE |
|---|---|---|
| A | data/dolly15k_qwen2_5_14b_kgw_gamma0.25_delta3_train.parquet | data/dolly15k_qwen2_5_14b_kgw_gamma0.25_delta3_test.parquet |
| B | data/dolly15k_qwen2_5_14b_kgw_gamma0.5_delta2_train.parquet | data/dolly15k_qwen2_5_14b_kgw_gamma0.5_delta2_test.parquet |
| C，已有数据核验通过时 | data/dolly15k_qwen2_5_14b_kgw_train.parquet | data/dolly15k_qwen2_5_14b_kgw_test.parquet |
| D，已有数据核验通过时 | data/dolly15k_qwen2_5_14b_kgw_gamma0.5_delta3_train.parquet | data/dolly15k_qwen2_5_14b_kgw_gamma0.5_delta3_test.parquet |

若需统一重新生成四格，则为 C、D 也使用新的匹配生成文件名，保留原文件作为历史证据。

阶段记录：

1. 固定同一批500 test prompts和同一份 clean 教师参考，评测 sampling参数与逐条seed一致。学生评测不额外施加水印偏置。
2. 对 KGW教师、warmup1813、GAD1813 分别记录同口径的回答内 token-pair 严重重复率、ROUGE-L、回答token长度和截断率。词4gram摘要只初筛，不填本表严重重复列。
3. 水印 raw/dedup 检测并列；每个 γ 使用相应 γ/key/tokenizer 重评分同一批 clean 负例，再算ROC，避免使用上一组阴性分数。不要把重复造成的 raw 检出提升当作有效收益。
4. 保存 GAD step1、500、1000、1500、1813 的长度/截断率、actor entropy、critic教师与学生评分、d_loss/d_acc、固定验证ROUGE。用已有中间保存点观察退化何时出现。

| 配置 | 教师严重重复 | warmup严重重复 | GAD严重重复 | GAD−warmup百分点 | warmup clean ROUGE-L | GAD clean ROUGE-L | GAD去重AUROC | GAD去重TPR@5% |
|---|---|---|---|---|---|---|---|---|
| 0.25/3 | 待测 | 待测 | 待测 | 待测 | 待测 | 待测 | 待测 | 待测 |
| 0.5/2 | 待测 | 待测 | 待测 | 待测 | 待测 | 待测 | 待测 | 待测 |
| 0.25/2，本轮重做 | 待测 | 待测 | 待测 | 待测 | 待测 | 待测 | 待测 | 待测 |
| 0.5/3，本轮重做 | 待测 | 待测 | 待测 | 待测 | 待测 | 待测 | 待测 | 待测 |

教师已差→问题在教师生成目标已出现；教师正常而warmup变差→定位到warmup蒸馏；前两阶段正常而GAD变差→定位到GAD。这是阶段定位，不是某个算法机制的唯一归因。

领域依据：[KGW官方参数说明](https://github.com/jwkirchenbauer/lm-watermarking#how-to-watermark---a-short-guide-on-watermark-hyperparameters) 将 γ 定义为绿词表比例，δ 为 logit偏置；它们是不同控制量，作者也强调质量与δ/输出分布的关系。该说明用于形成可检验的假设，不替代当前0.5B管线的实测结论。

本轮只生成实验计划，没有启动训练，也没有更改训练代码。
