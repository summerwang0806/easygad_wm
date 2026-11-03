# TP 加速与已有断点续跑

先用 `Ctrl+C` 停止旧任务，保留当前输出对应的 `.parquet.progress.jsonl`。

将下列三个文件同步到服务器的同名位置，代码和模型资产目录分开同步：

- `baseline_acl/paraphrase_tp.py`
- `baseline_acl/paraphrase_up.py`
- `baseline_acl/inverse_watermark.py`

在服务器 `~/EasyGAD` 执行：

```bash
CUDA_VISIBLE_DEVICES=1,2 python baseline_acl/paraphrase_tp.py \
  --input data/dolly15k_qwen2_5_14b_kgw_gamma0.5_delta3_newtrain.parquet \
  --output data/tp_warmup_dolly15k_qwen2_5_14b_kgw_gamma0.5_delta3_student_newtrain_strength2.5.parquet \
  --rules wn/acl_rules_tp_warmup_Qwen2.5-0.5B_gamma0.5_delta3_fp32.json \
  --model /shared/public_models/Qwen2.5-0.5B \
  --num-gpus 2 \
  --dtype float32 \
  --prompt-mode completion \
  --inverse-strength 2.5 \
  --max-attempts 3 \
  --generation-policy efficient-v1 \
  --resume
```

必须沿用实际运行的原输出路径，不能换成一个没有断点的新路径。失败样本此前保存的尝试次数会保留，每条累计最多 3 次（首次加两次重试），重试使用不同 seed。

## 加速内容

- 动态输出上限：`min(4096, max(256, 2 * 原文token数 + 128))`。例如原文 125 token，上限为 378；原文 1536 token，上限为 3200。
- 长段重复或提示词回显会提前结束本次尝试并记为失败，部分文本不直接作为完整改写保存。
- 全局规则和前缀惩罚 tensor 缓存到 GPU，避免每步重建全局规则字典并重复传输全部惩罚数据。
- 保留 FP32、原始学生 O、相同规则和逐行 seed；每卡仍逐条解码。
- 进度打印当前进程新增完成速度 `rate` 和剩余时间估算 `eta`，已有完成行不会计入当前进程的速度分子。刚恢复、尚无新增完成行时显示 `warming-up`。

## 断点与实验记录

已完成行原样保留，即使后续检查更严格，也不会自动重写旧结果。旧失败行和未开始行使用新策略继续。断点追加策略升级元数据；再次中断后，用上面同一条命令恢复。

最终 `.parquet.audit.json` 中：

- `generation_phases`：各阶段配置及最终行号；行号从 0 开始。
- `mixed_generation_policies`：是否包含旧、新两种生成策略。
- `attempt_policy_counts`：各策略产生的已保存尝试数。
- `early_aborted_attempts`：因早停而终止的尝试数。
- `unchanged_teacher_responses`、`unchanged_response_rows`、`unchanged_response_ids`：最终保留原文的数量与样本。

输入、输出、模型、规则和其它采样设置必须匹配原任务。当前迁移只允许 `legacy` 到 `efficient-v1`，并允许将尝试上限提高到最多 3；不允许反向降级或顺便更换精度、温度、seed 等设置。

本次基于附件副本验证，750 条完成记录和 224 次失败尝试均能保留读入，原附件未修改。服务器最新断点的实际数量可能更多。CPU 回归验证不等于实际 GPU 提速或语义质量验证；旧结果中的事实漂移会随断点一起保留。

其它耗尽失败仍按原 `--on-failure error` 停止并保存断点。原文相同的最终尝试会自动保留原文并继续；循环或截断输出不会因此被当成有效转述。
