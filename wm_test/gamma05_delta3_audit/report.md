本次核对的是 Qwen2.5-0.5B，KGW γ=0.5、δ=3 的 kgwwarmup_kgwgad 实验。warmup 和 GAD 各 500 条；下表 AUROC/TPR 使用原始 z-score，p-value 两列为逐条回答单侧正态近似 p-value 的算术均值。

| 模型/方式 | AUROC | TPR@FPR≤5% | TPR@FPR≤10% | 500条采样文本ROUGE-L（和clean教师比较） | 严重重复输出¹ | p-value均值 | p-value去重后均值 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Qwen2.5-0.5B / KGW warmup | 0.738816 | 26.2% | 38.4% | 0.219981² | 20.8%（104/500） | 0.256877 | 0.272810 |
| Qwen2.5-0.5B / KGW GAD | 0.736264 | 66.6% | 68.0% | 0.036049² | 99.6%（498/500） | 0.268329 | 0.257038 |

¹ 严重重复与已有消融表口径一致：回答内部相邻 token 对的重复比例 `1 - unique_pairs / all_pairs > 0.5`，不计 prompt 边界。不是相同整篇回答的数量，也不是去除重复后重新生成回答。独立本地 byte-BPE 质量审计的 1000 条回答长度与保存的 num_tokens 全部一致；每条回答内 unique_pairs 与检测保存的 dedup_num_tokens 相差 0 或 1，符合检测另计 prompt→answer 边界的定义。warmup 临界样本 dolly-06622 的真实回答内 unique_pairs=196，all_pairs=393，重复率=0.5012722646，计入严重重复。

² ROUGE-L 从拉取的 `detection_metrics_history.md` 最新两段匹配实验记录读取，分别为 0.21998142710768617 / 0.03604859207167721。本地未发现教师原参考 parquet，因此这两格尚未独立重算。报告代码使用 `RougeScorer(['rougeL'], use_stemmer=True)`，逐条 F1 等权平均，并在计算前检查 500 个 ID 和完整 prompt 完全对齐；方法符合该表要求。Dolly 人工答案指标 0.198672 / 0.017157 是另一个参考，不能填入本表的 clean 教师列。

复算结论：当前统计计算与最新服务器记录一致，但 GAD 的回答质量已严重退化，原始检测结果受重复放大。不能用该表原始检出率证明 GAD 获得了可靠且可用的水印蒸馏结果。

已逐条确认的范围：

- warmup、GAD、clean 负例各有 500 个唯一 ID，ID 顺序、完整 prompt、逐条 seed 相同；seed 为 42–541。共同记录的生成参数为 temperature=0.7、top_p=0.9、max_new_tokens=1536，学生 max_prompt_tokens=2048；base 旧记录未保存 max_prompt_tokens。
- 当前三个检测文件全部使用 γ=0.5、δ=3、hash_key=15485863 和 simple_1；正例路径分别为 warmup/gad 的 global_step_1813。生成代码与元数据均表明评测时没有额外开启 KGW logits bias。
- 负例使用 `base_qwen2_5_0_5b_dolly15k_test.rescored_gamma0.5_delta3_key15485863.jsonl`。原 base 文件仍是 γ=0.25、δ=2，直接拿它与当前学生比较会造成检测错配。重评分 base 与原 base 的回答、prompt、ID、模型路径、生成元数据逐条一致；源 SHA 在 CRLF→LF 正规化后精确匹配。
- 三个文件共 1500 条的 raw/dedup z 值、p 值、绿 token 比例、token 数量与旁路 p-value 文件一致。z 值按 `(green - γ*n)/sqrt(n*γ*(1-γ))` 重算；p 值按 `0.5*erfc(z/sqrt(2))` 重算。旁路 hash 都精确匹配 LF 源文件，Windows Git 换行变化不表示回答变更。
- AUROC 用独立的正负样本两两排序概率（相等记半）复算，TPR 用不拆分同分样本的全部经验阈值复算，匹配最新报告。warmup 5% 工作点 TP=131、FP=25，10% TP=192、FP=50；GAD 5% TP=333、FP=23（实际 FPR=4.6%），10% TP=340、FP=50。
- 所列 TPR 工作点在当前测试集上直接选阈值，是经验 ROC 描述；若用于部署阈值或报告独立泛化性能，应另用校准集选阈值后再测试。

去重检测提供的补充证据：

| 阶段 | 去重AUROC | 去重TPR@FPR≤5% | 去重TPR@FPR≤10% | 原始p中位数 | 去重p中位数 | 原始p≤0.01 | 去重p≤0.01 |
|---|---:|---:|---:|---:|---:|---:|---:|
| warmup | 0.747380 | 24.6% | 38.6% | 0.119477 | 0.179887 | 24.6%（123/500） | 10.4%（52/500） |
| GAD | 0.763446 | 24.6% | 36.2% | 2.64323e-14 | 0.192044 | 66.4%（332/500） | 8.0%（40/500） |

这里去重是相同 `(previous_token_id, token_id)` 只计一次，未修改文本。GAD 的有效评分长度中位数为 1536，而 unique token 对数量中位数只有 40；493/500 条的 unique token 对占比低于 10%。非常小的原始 p 值大量来自循环重复。p-value 均值不是整个实验的显著性 p 值，两个 p 均值的升降也不能代替检出率和输出质量。

clean 的原始 p≤0.05 误报率是 10.8%，去重后为 5.0%；p≤0.01 对应 4.4% 和 1.0%。因此原始理论 p 阈值不能直接等同实测 FPR，表格中的 TPR 必须从 clean 实测 ROC 得到。

生成和训练环节仍需核实的事项：

- 原教师 parquet、实际教师生成命令和模型 provenance 本地缺失。`wm_data/generate_teacher_data.py:47-49` 当前默认模型为 Qwen2.5-0.5B；README 中带 14b 文件名的 γ=0.5、δ=3 示例未显式设置 `--model`。这不证明本次教师用错，但仅凭 14b 文件名不能确认教师为 14B，应核对当时的 `--model` 命令或 parquet part 中 `kgw_detector` metadata。
- warmup 实际日志证明用 Qwen2.5-0.5B、γ0.5δ3 名称的 train/test parquet 训练 1 epoch，并保存 global_step_1813。服务器后续返回的 `resume_audit.json` 也补齐成功 GAD 的实际配置：从当前 warmup 1813 actor/critic 权重初始化，日志 `Training from scratch`，训练从 step1 到1813。新旧 GAD 的全部 342 个安全配置字段已比较，只有预期数据/初始化/实验路径，以及恢复模式和 Ray CPU 数的差异；训练超参数一致。详细证据见同目录 `resume_config_comparison.md`、`server_gad_config_comparison.json`。
- 代码中 warmup 对 teacher_response 做 SFT，GAD 对学生 rollout 做 PPO，脚本将 warmup actor/critic 导出并加载为 GAD 初始化。当前 GAD 脚本 `actor.use_kl_loss=False`，配置 `use_kl_in_reward=False`，阶段也关闭 reference；`KL_COEF=0.001` 本身不表示启用了 KL 约束。后续核对确认这些设置在旧实验也相同，未由断点恢复补丁引入，不能据此解释新旧结果差异；新旧对照以同目录 `resume_config_comparison.md` 为准。
- 训练/测试拆分代码有固定 seed 的随机划分，但本地没有本次实际 train/test parquet，无法实证核对是否无 ID 重叠、教师样本参数是否混用。教师生成断点恢复对旧 part 主要检查行数/schema，若改变模型或γ后复用旧未完成输出目录，存在混合旧回答的可能；本次没有发生证据。
- GAD 有 9 条可见回答重新编码后超过1536个 token，最大1777；clean 有2条，warmup没有。生成脚本确实设置 vLLM `max_tokens=1536`，检测用 `result.outputs[0].text` 重新编码，而未保存原输出 token IDs；因此目前不能把重编码后的数值认定为生成时上限失效，需保存原 token IDs/finish_reason 才能追查。
- 本地 tokenizer 交叉检查显示有 3 条完整 prompt 超过2048，代码截取开头2048，可能丢失末尾指令或 assistant 模板。三组使用同样的处理，但本次原始生成信息不全；这3条不能解释 GAD 的498条严重重复。
- 本机没有 CUDA/PyTorch 与该 checkpoint tokenizer，未重新运行原 CUDA randperm 对所有 token 重判绿名单。已完成的是保存分数、公式、缓存、文本重复和排名统计的一致性核对，不能称为完整独立复现生成及训练。

复算文件：`metrics.json`、`detector_audit.json`、`warmup.repetition_audit.jsonl`、`gad.repetition_audit.jsonl`。主脚本为 `../audit_gamma05_delta3.py`；标准库即可重新检查当前文件。要补完教师 ROUGE-L，在有 rouge_score/pyarrow 的服务器环境运行：

```bash
python wm_test/audit_gamma05_delta3.py \
  --teacher-reference data/dolly15k_qwen2_5_14b_clean_test.parquet \
  --tokenizer /shared/public_models/Qwen2.5-0.5B
```

该命令只读取回答，重算文本指标，不重新生成回答、不修改原样本或 p-value 缓存。`--tokenizer` 可完整复核严重重复；若不复制本地质量审计 JSON、也不提供 tokenizer，warmup 临界样本会标为待确认，避免以含 prompt 边界的检测 pair 数冒充回答内部统计。
