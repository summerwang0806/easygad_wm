# Easy TP：放宽验收条件的快速基线

`baseline_acl/easy_paraphrase_tp.py` 与 `paraphrase_tp.py` 使用同一个原始学生 O、同一份规则、同一段改写提示、同样的采样参数和命令行参数，只改变**验收策略**：基准实验故意做得弱一些，换生成速度。

## 1. 与严格 TP 的区别

| 情况 | `paraphrase_tp.py` | `easy_paraphrase_tp.py` |
| --- | --- | --- |
| 输出到达长度上限（截断） | 本次作废，换 seed 重试 | **接受**，审计记 `truncated_at_budget` |
| 检测到长段重复 | 提前终止并作废 | 提前终止，**裁掉重复尾后接受** |
| 生成出改写提示/模板 | 作废 | 用固定规则剥掉回显后**接受** |
| 改写结果与原文相同 | 作废重试 | **接受**，记 `unchanged_source_answer` |
| 拒答、编辑口吻前言 | 作废 | 只记录，不拒绝 |
| 空输出 | 重试 | **仍是唯一的重试条件** |
| 每行生成次数 | 最多 3 次 | 最多 `--max-attempts` 次，默认 3（首次 + 最多 2 次重试） |
| 输出预算 | 默认 `legacy` 固定 4096 | 固定 `efficient-v1`：`min(--max-new-tokens, max(256, 2*原文token数+128))` |
| 最终仍失败 | `error` 会停；`keep-last` 保留异常文本 | 固定 `keep-original`，保留原文，**不会中断整个任务** |

`--generation-policy` 和 `--on-failure` 仍然可以照原命令传入（便于复用旧命令），但生效值固定为 `efficient-v1` / `keep-original`，启动时会打印一行提示。

## 2. 首次运行

用**新的输出文件名**，第一次不要加 `--resume`：

```bash
CUDA_VISIBLE_DEVICES=1,2 python baseline_acl/easy_paraphrase_tp.py \
  --input data/dolly15k_qwen2_5_14b_kgw_gamma0.5_delta3_newtrain.parquet \
  --output data/easy_tp_warmup_dolly15k_qwen2_5_14b_kgw_gamma0.5_delta3_student_newtrain_strength2.5.parquet \
  --rules wn/acl_rules_tp_warmup_Qwen2.5-0.5B_gamma0.5_delta3_fp32.json \
  --model /shared/public_models/Qwen2.5-0.5B \
  --num-gpus 2 \
  --dtype float32 \
  --prompt-mode completion \
  --inverse-strength 2.5 \
  --max-attempts 3
```

注意：

- 不要复用严格 TP 的 `.progress.jsonl` 断点：两种脚本的断点格式不同，`--resume` 会明确报错，不会静默混用。
- 输出 Parquet、断点、审计文件都不能与已有文件重名；已有输出不会覆盖。
- `--inspect`、`--preflight` 的用法与严格 TP 相同，只做 CPU 检查，不加载权重。

## 3. 中断后续跑

保持输入、输出、规则、模型、精度、采样、`--max-attempts` 完全不变，在原命令末尾加 `--resume`：

```bash
CUDA_VISIBLE_DEVICES=1,2 python baseline_acl/easy_paraphrase_tp.py \
  --input data/dolly15k_qwen2_5_14b_kgw_gamma0.5_delta3_newtrain.parquet \
  --output data/easy_tp_warmup_dolly15k_qwen2_5_14b_kgw_gamma0.5_delta3_student_newtrain_strength2.5.parquet \
  --rules wn/acl_rules_tp_warmup_Qwen2.5-0.5B_gamma0.5_delta3_fp32.json \
  --model /shared/public_models/Qwen2.5-0.5B \
  --num-gpus 2 --dtype float32 --prompt-mode completion \
  --inverse-strength 2.5 --max-attempts 3 \
  --resume
```

`.parquet.progress.jsonl` 里已完成的行原样保留，不会重新生成；崩溃时最后一行只写了一半会被自动丢弃。想改设置请换新的 `--output`，不要在半途改 seed、温度、规则或模型。

## 4. 日志

```text
[TP-easy progress] [####----] completed=1234/14511 (8.5%), rejected_attempts=6,
fallbacks=1, unchanged=3, truncated=812, repetition_trimmed=41, echo_cleaned=17,
row=1233, attempt=1, rate=480.0/h, eta=27.6h, elapsed=9250.1s
```

- `completed`：已有最终结果的行数（接受或保留原文）。
- `rejected_attempts`：触发重试的生成次数，正常情况下应远小于行数。
- `fallbacks`：所有尝试都为空、最终保留原文的行数。
- `truncated` / `repetition_trimmed` / `echo_cleaned`：被接受但带有对应审计标记的行数。
- `unchanged`：最终与原文相同的行数（包含 `fallbacks`）。
- `rate`、`eta`：本进程新增完成速度和剩余时间；刚续跑时显示 `warming-up` 属正常。

进度默认每 15 秒一行，出现重试时立即打印。

## 5. 审计字段

`<output>.audit.json` 中除常规的 `rows`、`status_counts`、`output_tokens` 外，重点看：

- `truncated_accepted_count`：截断仍被接受的行数。
- `repetition_trimmed_count`：裁掉重复尾仍被接受的行数。
- `prompt_echo_cleaned_count`：剥掉提示/模板回显后接受的行数。
- `unchanged_accepted_count`：被接受但内容与原文相同的行数；`unchanged_teacher_responses`、`unchanged_response_rows`、`unchanged_response_ids` 则统计最终结果（含保留原文的回退行）。
- `fallback_rows`、`fallback_reasons`：所有尝试都为空而保留原文的行。
- `rejected_generation_attempts`、`rejected_attempt_reasons`：重试次数与原因（只有 `empty_output`）。
- `accepted_attempts`：最终结果是第几次生成得到的。
- `note_counts`、`cleanup_counts`：各类标记与清洗动作的计数。

每条被接受的尝试在断点中保留 `raw_output_text`、`output_text`、`cleanup_actions`、`notes`、`finish_reason`、`seed`、`effective_max_new_tokens`，可离线复核。

## 6. 速度与质量

速度主要来自两点：

1. 绝大多数行第一次生成就被接受，不再为截断、重复、提示回显、未改写反复重跑。
2. 每行输出预算按原文长度分配，不再对每条都允许 4096 token。

以本目录已完成的一次严格 `efficient-v1` 运行为参照（14511 行、18045 次生成、约 2.2 小时，其中 2368 行第二次才成功、1166 行第三次才成功、490 行靠 `keep-last` 保留），easy 版本预计只需约 1.5 万次生成，同型号 GPU 上通常在一到数小时量级，而当前默认固定 4096 token 的严格运行需要数百小时。

代价是基准更弱：截断、重复、回显、未改写都会进入训练数据。若需要更干净的数据，可：

- 用审计里的 `unchanged_response_rows` / `truncated_accepted_count` 过滤；
- 或把 `--max-attempts` 设为 `1`（最快，空输出直接保留原文）；
- 或用 `--max-new-tokens` 进一步压低单行输出上限（更快但截断更多）。

## 7. 需要同步的文件

除本文件外，服务器上还需要严格 TP 已依赖的模块（保持原样即可）：

- `baseline_acl/easy_paraphrase_tp.py`
- `baseline_acl/paraphrase_tp.py`
- `baseline_acl/paraphrase_up.py`
- `baseline_acl/inverse_watermark.py`
- `baseline_acl/student_parallel.py`

规则文件、模型目录与严格 TP 完全一致，不需要重新估计规则。
