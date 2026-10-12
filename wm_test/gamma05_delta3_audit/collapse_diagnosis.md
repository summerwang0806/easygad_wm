后续核对修正（2026-10-12）：本地 Git 与实际日志比较已确认，下文讨论的 KL 缺失、UID 去重等行为在旧实验也存在，未由这次断点恢复补丁引入，因此不能用它们解释新旧实验差异。用户当前要求仅核对新旧配置与恢复过程，没有授权或要求按原论文修复实现。本轮未改训练代码。以同目录 `resume_config_comparison.md` 和 `old_new_config_comparison.json` 的新旧对照为准。

下文保留此前机制分析；它描述重复被强化的可能路径，不是已经证实的新旧差异原因。后续服务器记录已补齐 GAD 配置与首末日志：从当前 warmup1813 初始化、GAD从step1开始、最终1813，没有加载旧GAD优化器。新旧训练超参数相同。新最终判别器学生评分-45.5、教师16.094，因此“判别器给重复很高的绝对奖励”不是日志支持的结论。用户也补充两组教师命令，均未传 --model，按已核对脚本默认值都使用Qwen2.5-0.5B；尚待实际教师数据摘要验证。

输出层面的证据：

| 实验 | warmup严重重复 | GAD严重重复 | GAD回答token数中位数 |
|---|---:|---:|---:|
| 当前 γ=0.5、δ=3 | 104/500（20.8%） | 498/500（99.6%） | 1536 |
| 旧 kgw_gad_05b_14b_full run，γ=0.25、δ=2 | 26/500（5.2%） | 8/500（1.6%） | 145 |

当前 warmup 的396条非严重重复回答中，395条在GAD后变为严重重复。500条GAD回答全文各不相同，重复的是各自prompt诱导的短句。例如 dolly-02687 的 “These percussion instruments are percussion instruments” 循环217次。两次实验共同记录的500个ID、prompt、seed、temperature=.7、top_p=.9、max_new_tokens=1536均相同，模型路径均标为0.5B、step1813；训练run、数据和优化过程不同，旧记录也缺max_prompt_tokens与环境版本，因此不能用它建立γ/δ的单变量因果。

1. **参考 KL 是首要实现检查点。** 原[GAD论文附录A.2](https://arxiv.org/html/2511.10643v2#A2) 使用group size=8、KL权重β=.001、batch256。本地当前脚本group size=2、batch8；`run_full_gad_optimized.sh:431`关闭use_kl_loss，`ray_trainer.py:412-415`关闭GAD reference。更关键的是 `dp_actor.py:523-524` 虽然有选取ref_log_prob的开关，`:670-685` 实际训练loss完全没有计算并加入reference KL。作者的[官方gad分支actor](https://github.com/YTianZHU/verl/blob/gad/verl/workers/actor/dp_actor.py#L445) 在445-452行有这段loss。因此仅把use_kl_loss=True或调KL_COEF不能修复；reference模型、log-prob计算和loss都需要接通。日志actor/ppo_kl是相对rollout旧策略的统计，并非对warmup参考模型的锚定。

2. **真实GAD rollout被按prompt UID删除。** `ray_trainer.py:1152-1155`给每个prompt一个UID并repeat(n=2)，两条不同回答共享UID。GRPO先用两条计算优势、critic也训练两条；但 `dp_actor.py:501` 不分阶段调用 `deduplicate_by_uid`，`:454-484`只留下每个UID第一条。当前默认batch8、n2、DP2、SP1且balance被注释的配置中，全局16条rollout只8条进入actor更新。每rank mini-batch原归一化大小为8，删除后实际4条，动态batch缩放总权重也变为0.5。固定保留第一条在IID假设下不必然导致期望梯度偏差，但浪费一半采样、增加噪声并改变步幅；GAD不应套用重复教师SFT样本的去重逻辑。

3. **奖励和更新方式可以放大误判。** 训练reward是critic整句原始logit（`ray_trainer.py:1237-1264`），不是水印z-score或ROUGE。critic学的是教师回答比学生回答高分的Bradley-Terry目标（`core_algos.py:992-995`），没有显式正确性或重复惩罚。GRPO在同prompt组内比较，再把一个序列优势广播到所有有效token（`:231-263`）。两条回答的分数即使只差很小，在差值明显大于epsilon时优势也接近±0.707；两条都差的回答也会有相对赢家。若判别器偶然给循环回答更高分，整个循环片段都会获正梯度。GAD又没有混入教师SFT（`dp_actor.py:600-682`）和可用reference KL，因此缺少将其拉回正常回答的约束。

4. **长重复回答参与更多token梯度项。** `ppo_trainer.yaml:208` / `core_algos.py:690-691`使用microbatch总token平均，而非每条回答先平均再均分。因此长回答在同microbatch中占更多token项，重复token逐次参与更新。这会放大已获正优势的长重复序列；不意味着任何长回答必然获正奖励。

需要明确的两个边界：critic只保留最后有效token的分数（`dp_critic.py:120-148`），所以后面的sum不是“每多写一个token就直接多一份奖励”；目前也没有证据表明训练的奖励方向、detach、temperature或prompt/sample对应关系发生反转。

本轮warmup日志最后100步的critic/d_acc平均0.6425、d_loss平均0.61658、rollout平均长度326.51、长度clip_ratio平均0.14625。这只能说明判别器已学到部分区分、学生尚有质量问题，不能替代GAD阶段日志。原论文主要验证≥3B的Instruct学生；当前0.5B基座、较小batch/group、KGW教师回答是不同设置，需要独立验证稳定性。

优先处理顺序：修正GAD阶段rollout去重；恢复真正reference KL；评估现存中间checkpoint并检查reward与重复率、长度、entropy的关系；核查教师回答的重复率与实际教师模型。之后再用小规模对照判断是否需要增大group/batch或混合教师SFT。当前建议为待验证的修复方向，本轮只完成原因审计，没有更改训练代码。
