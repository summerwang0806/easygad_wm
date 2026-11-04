# TP 加速、保留第三次异常输出与已有断点续跑

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
  --on-failure keep-last \
  --resume
```

必须沿用实际运行的原输出路径，不能换成一个没有断点的新路径。失败样本此前保存的尝试次数会保留，每条累计最多 3 次（首次加两次重试），重试使用不同 seed。

## 三次失败后直接保留最后输出

本命令显式使用 `--on-failure keep-last`。前三次仍按原有检查处理，若最终一次仍触及长度上限、循环早停或回显等，但生成文本非空，就把**最后一次已经生成的原始文本**写入 `teacher_response`，标为 `status=abnormal`，并继续其它行。它不是正常完整改写，不会标为 `ok`，也不回退到原文。真正的空输出仍会报错，避免写入空训练样本。

支持从原来的 `on_failure=error` 断点直接切换到这个显式策略。已经耗尽三次的样本使用断点中的第三次文本，**不生成第四次**；已完成行保留。旧的失败记录不改写，追加 `resume_policy` 元数据记录该决策，重启时按该阶段恢复同样的结果。采样、精度、规则、输入和预算不变。

终端进度和结束信息显示 `abnormal_kept`，结束时另输出 `[abnormal summary]`。最终 `<output>.audit.json` 保存：

- `abnormal_kept_count`、`abnormal_kept_rate`：保留的异常**样本**数量及比例（比例为 0–1，不是失败尝试次数）。
- `abnormal_kept_rows`、`abnormal_kept_ids`：对应行号和 ID，行号从 0 开始。
- `abnormal_kept_reasons`：最终异常原因的逐类数量；一条样本可有多个原因。
- `length_limited_kept_count`：其中最后一次因长度上限结束的样本数。
- `abnormal_kept_records`：最终尝试次数、原因、token 数和停止原因。
- `resumed_abnormal_kept_rows`：由旧断点中已耗尽的失败记录恢复的异常样本。

不加该选项时仍为 `--on-failure error`，保持原来的严格停止行为；`keep-original` 是另一种保留原文的策略，不等同于本次要求。

## 加速内容

- 动态输出上限：`min(4096, max(256, 2 * 原文token数 + 128))`。例如原文 125 token，上限为 378；原文 1536 token，上限为 3200。
- 长段重复或提示词回显会提前结束本次尝试并记为失败；在本命令的 `keep-last` 下，最后一次的非空异常文本会保留并单独计数。
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

输入、输出、模型、规则和其它采样设置必须匹配原任务。当前迁移允许 `legacy` 到 `efficient-v1`、将尝试上限提高到最多 3，以及显式 `error` 到 `keep-last`；不允许反向降级或顺便更换精度、温度、seed 等设置。

本次基于附件副本验证，750 条完成记录和 224 次失败尝试均能保留读入，原附件未修改。服务器最新断点的实际数量可能更多。CPU 回归验证不等于实际 GPU 提速或语义质量验证；旧结果中的事实漂移会随断点一起保留。

原文相同的最终尝试在原来的严格模式下仍自动保留原文并继续；本命令的 `keep-last` 则把最终异常生成明确计入异常数量。
