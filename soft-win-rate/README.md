# 本地固定参照 Soft Win Rate

使用本地 `/shared/public_models/Qwen3-32B` 评判已经保存的学生回答。没有外部 API 请求、API key、模型下载或重新生成学生回答。

## 正常使用

在 `run_soft_win_rate.py` 顶部修改 **`INPUT_JSONL`** 为本次待测 JSONL，然后在服务器已有的 `wm` 环境运行：

```bash
python soft-win-rate/run_soft_win_rate.py
```

不需要手动指定 GPU，也不需要先启动模型服务。脚本会自动选卡、启动离线 vLLM worker、显示进度，并在结束时释放自己启动的 worker。相对输入路径始终以项目根目录为基准，所以也可以进入本目录运行 `python run_soft_win_rate.py`。

`REFERENCE_JSONL` 默认固定为：

```text
wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl
```

这是无水印蒸馏 GAD 学生的保存回答，与水印检测脚本的 `clean-file` 独立。比较不同方法时保持此文件、测试题目、裁判权重及评分提示不变。输入需要逐行包含 `id`、`prompt`、`answer`；ID 集合和对应问题必须与参照完全一致，不静默取交集。空回答也保留评判。

## 指标定义

每个问题都匿名评判两个顺序：待测回答在 A 的顺序，以及待测回答在 B 的顺序。裁判只输出 `A`、`B` 或 `tie` 与简短理由，不接收 checkpoint 名称或水印标签。

每轮将待测回答的胜、平、负分别记为 `1`、`0.5`、`0`；先对同题两个顺序求平均，再对所有完整题目求算术平均。结果百分比越高，表示裁判越偏好待测回答。

**本工具的 Soft Win Rate 明确是平局半分，不是 PostMark 的“胜＋平”比例。**

- 交换顺序出现相反选择时，两个偏好平均为 0.5，但不把这两轮伪装成真实平局；另报双顺序一致率。
- 胜／平／负比例的分母是完整题目的 `2N` 次单轮判定。
- 拒答、解析失败、输出被 token 上限截断，不记为平局。一个问题只有两个顺序都成功时才进入主指标；报告覆盖率与有效样本数。
- 95% CI 按问题成对 bootstrap，不能解释为裁判无偏或模型训练种子间的不确定性。
- 50% 是相对固定参照的偏好平衡，不是正确率，也不是能力保留百分比。

裁判使用 BF16、`enable_thinking=False`、固定 seed 和 greedy decoding。这是本实验选择的协议，不声称是 Qwen 官方推荐的裁判参数。评分重点是指令遵循、正确性、相关性、连贯性和有用性；明确不奖励冗长、复读或仅有措辞重合。

## 自动选卡与显存不足重试

1. 用 `nvidia-smi` 读取真实可用显存，不只看总显存或 GPU 数量。若外部已设置 `CUDA_VISIBLE_DEVICES`，只在其允许的卡中选择。
   启动子进程时使用数字卡号，并设置 `CUDA_DEVICE_ORDER=PCI_BUS_ID`；UUID 仍保存在执行记录中。这样兼容将 `CUDA_VISIBLE_DEVICES` 强制转换为整数的旧版 vLLM。
2. 根据本地权重大小、模型层数、KV heads 和窗口估算空间；优先能容纳模型的单卡，之后考虑合法的 TP 组合。
3. 对 Qwen3-32B，64 attention heads / 8 KV heads 支持常规 TP=1、2、4，六张卡不会被直接配置为 TP=6。
4. 自动识别 vLLM 的显存计算方式。普通模式从实际空闲显存计算分配比例；已核对的 **vLLM 0.8.5 V1** 使用全卡已占用预算，因此以总显存预留至少 2% 计算比例，避免原有占用被重复扣减。两种模式都逐卡检查当前空闲显存是否足够，不把已有进程的显存计为可用。显式设置 `VLLM_USE_V1=0` 时保留普通模式；旧版 V1 方案只在自己的子进程设置 `VLLM_USE_V1=1`，确保计算方式一致。
   若显存不足，先以并发 1、分块 prefill 上限 1024 token 的方案降低预热峰值，再尝试其他可行卡组；这不会缩短 8192 的上下文窗口。
5. 显存不足时尝试下一可行配置；多卡通信初始化持续 180 秒没有进入后续阶段时，清理本次自己的 worker，跳过同一卡组的其余并发变体，再尝试其他可行卡组。依赖缺失、数据错误等会停止并指出日志位置。

本地多卡使用 `mp` 后端，默认采用 PCIe 兼容通信配置：仅在自己的子进程中禁用 NCCL P2P、InfiniBand 和 vLLM 自定义 all-reduce，启用共享内存，并绑定本机回环接口。用于处理跨 NUMA/PCIe 卡组在 NCCL 初始化阶段停滞的情况，可能降低多卡吞吐。单卡不覆盖这些通信环境变量，所有通信设置均写入实际执行记录。不会修改系统设置、全局 shell 环境或其他 GPU 进程。

该处理依据 [vLLM 0.8.5 排障说明](https://docs.vllm.ai/en/v0.8.5/getting_started/troubleshooting.html#incorrect-hardware-driver) 和 [NCCL 2.21.5 环境变量说明](https://docs.nvidia.com/deeplearning/nccl/archives/nccl_2215/user-guide/docs/env.html)。兼容配置属于通信故障的应对措施，服务器实测仍是启动成功的依据。

worker 失败时，终端会直接显示失败阶段、实际异常与 `worker.log` 路径；如果 vLLM 外层只报 `Engine core initialization failed`，还会提取日志内的 KV 缓存或 OOM 原因。没有完整有效题目时明确显示 `[FAILED]`，不会把 `None` 当作已完成的胜率。详细 traceback 保存在 worker 日志。进度条会显示当前处于 tokenizer 检查、多卡通信初始化、权重加载、显存预热或首轮判断阶段；0/1000 表示尚未完成第一轮判断。

部署通信修复时需要同时更新 `run_soft_win_rate.py` 和 `judge_worker.py`，后者负责把 `disable_custom_all_reduce` 传给 vLLM。之后仍只需修改入口顶部的 `INPUT_JSONL` 并执行原命令。

默认从窗口 8192、并发上限 2 开始，采用 eager 模式与分块 prefill 减少峰值显存。每对完整输入先用裁判 tokenizer 检查长度；若超窗，单文件入口会根据 worker 报告的实际 token 数自动扩大**当前文件**的窗口，再检查全部待评输入并重新选卡。比如本轮 KGW GAD 的 `8646 + 512 > 8192` 会触发 `8192 → 16384`；显存紧张时自动选卡器会尝试并发 1。**保留完整问题和回答，不静默截断，不自动开启 RoPE 扩展**。超过模型本地配置的 `max_position_embeddings` 才会停止并明确报错。

之后仍然只需修改顶部的 `INPUT_JSONL` 并运行原命令，不需要手动追加窗口或 GPU 参数。当前默认输入已经设为待补测的：

```text
wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.jsonl
```

首次发现长输入时会看到 `[Context] ... automatically increasing 8192 -> 16384`，属于自动恢复。最终窗口写入 Markdown 和每次运行的 JSON，并保存在 `results/context_plans/` 中；同一文件重跑会直接采用已保存的窗口，继续复用成功判断。选择另一个短文件时仍从原协议读取缓存，已完成的 Para、WN 2.5、WN 3 不会因为其他文件扩窗而失效。

内存估算不保证每个计划都能启动，最终以 vLLM profiling 为准。脚本不结束已有 GPU 任务，只清理自己创建的 worker 进程组。每条判断记录实际 GPU、TP、并发、窗口、prefill 上限、显存计算模式和日志路径，并随汇总追加到结果文档；更换 GPU/TP 可能带来数值差异，greedy 不代表跨硬件逐字一致。

在 80GB 卡剩余 70778 MiB 的六卡快照中，旧版 V1 方案选 GPU 1、比例约 0.980：这是全卡占用上限；再扣已有占用后，本 worker 的实际预算约 67.52 GiB。其他卡组因每卡空闲显存不足被排除。此结论是规划器测试，不是服务器实测启动结果。

旧版 V1 的公式依据：[vLLM v0.8.5 gpu_worker.py](https://github.com/vllm-project/vllm/blob/v0.8.5/vllm/v1/worker/gpu_worker.py#L149-L191)。该兼容规则不自动外推到其他版本。

## 保存、缓存与续跑

- `soft-win-rate/soft_win_rate_history.md`：每次运行追加一段结果、置信区间、覆盖率、文本生成配置、裁判指纹及实际执行配置，不覆盖旧记录。
- `soft-win-rate/results/<输入名>.<协议哈希>/judgments.jsonl`：逐轮成功判断，重复运行直接复用。
- 同一目录的 `runs/*.json`：每次运行独立归档，包括逐题偏好。
- `workers/*/plan_*/`：具体选卡、worker 配置、原始输出与 `worker.log`。
- `errors.jsonl`：不合格的裁判输出；成功判断不因重试而重算。
- `results/context_plans/*.json`：按输入、参照、裁判资产和原评分协议绑定的自动窗口选择；续跑长输入时保留此目录。

中断时 worker 已逐条 flush/fsync 的原始输出也会在下次启动时恢复到主缓存。主缓存若只剩最后一条未写完的数据，会保留该尾部备份后恢复完整行。改变输入、参照、裁判资产、提示或评分配置会使用不同缓存，旧记录保留。权重指纹采用文件名、大小和修改时间，配置/tokenizer 采用内容哈希；不全量读取几十 GB 权重做哈希。

两个进程不能同时写同一组缓存；不同输入可以使用不同缓存目录运行，但仍需自行避免 GPU 资源竞争。历史文档追加也有文件锁。

## 可选检查命令

```bash
# 只验证数据并查看可行选卡方案，不推理、不写结果
python soft-win-rate/run_soft_win_rate.py --check-only

# 首次先跑前5题；之后原命令跑全量会复用这10轮判断
python soft-win-rate/run_soft_win_rate.py --limit 5

# 可选：命令行更换输入，无需编辑常量
python soft-win-rate/run_soft_win_rate.py --input-file wm_test/example.jsonl

# 只从已有缓存追加汇总，不启动GPU；模型目录仍须可读以核对指纹
python soft-win-rate/run_soft_win_rate.py --summary-only
```

运行需要服务器上兼容 Qwen3 的 PyTorch、Transformers 与 vLLM（Qwen 文档以 vLLM≥0.8.5 为起点）。先使用现有 `wm` 环境；不要为这个脚本盲目升级到不匹配当前 NVIDIA 驱动的 CUDA 构建。父进程仅依赖标准库，模型库只在独立 worker 中导入。

Windows 工作区只能完成数据、统计、缓存及模拟 worker 测试；真实模型启动、显存和吞吐需要在 GPU 服务器运行确认。
