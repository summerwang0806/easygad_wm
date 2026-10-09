# EasyGAD：从原始学生模型训练 KGW GAD 的运行说明

更新于 2026-10-09。服务器项目目录：`/shared/wwx/EasyGAD`。全参数脚本默认原始 Qwen2.5-0.5B、SwanLab 云端记录；现在尊重外部 `CUDA_VISIBLE_DEVICES`，未设置时才默认 1+3 号 GPU。本地修改和检查由 Codex 完成；推送、服务器拉取及执行均由用户自行完成。

## 已有实验的断点恢复

原脚本同时有两处限制：已有实验目录直接退出；warmup 和 GAD 均显式设置 `trainer.resume_mode=disable`。训练器本身支持恢复模型、优化器、学习率调度器、随机数状态和数据迭代器，但原启动脚本没有启用这些能力。

新脚本用 `--resume` 恢复原实验；不加该参数仍拒绝已有目录。每个阶段使用自己的 `latest_checkpointed_iteration.txt`，避免误选保存到一半的 `global_step_*` 目录。训练结束后写入 `warmup/.stage_completed`，后续恢复会跳过 warmup。已有 GAD checkpoint 也会自动跳过 warmup。加载已完成目标步数的 checkpoint 时，训练器直接结束该阶段，不再多训练一步。

这次日志已经确认 warmup 成功、最终保存点为 `global_step_1813`，但旧脚本没有完成标记。更新代码后首次恢复请显式加 `--skip_warmup`：

```bash
CUDA_VISIBLE_DEVICES=1,2 bash scripts/train/run_full_gad_optimized.sh \
  --model /shared/public_models/Qwen2.5-0.5B \
  --exp_name te_old_st_Qwen2.5-0.5B_gamma0.5_delta3 \
  --nnodes 1 --resume --skip_warmup \
  --ray_tmpdir /tmp/easygad-wwx --ray_num_cpus 8
```

`--skip_warmup` 要求 `--resume` 和有效的 warmup checkpoint，只用于确认 warmup 已完成的实验。若 warmup 中途失败，仅加 `--resume`。GAD 有保存点时自动从 GAD 保存点继续；没有保存点时从 warmup 模型开始 GAD。恢复不会补回最后一次保存之后丢失的训练进度。保持模型、数据、批大小和 GPU 数与原实验一致。

首次恢复旧实验会重新合并一次 warmup 模型，不重新训练 warmup；合并成功后写入 `.merge_completed`，再次恢复可复用导出的模型。损坏的 tracker、缺少 actor/critic 或 `data.pt` 时会报错，不静默当作新实验运行。

## Ray 启动失败排查

2026-10-09 日志中的直接失败是 runtime env agent 的连接在 30 秒内始终失败，raylet 退出，继而出现 `ActorDiedError`。日志明确指出 TaskRunner 尚未运行；这份日志不能证明是 GAD 训练或 GPU 显存不足造成。

`/shared` 使用率超过 95% 是另一条风险提示，即使仍有约 1605 GB 空间，Ray 也会按使用比例告警。它不能单独证明 agent 的连接失败原因。现在 Ray 临时目录默认 `/tmp/easygad-${USER:-user}`，可通过外部 `RAY_TMPDIR` 或 `--ray_tmpdir` 指定；Ray CPU 默认 8，可用 `--ray_num_cpus` 调整。单机 CPU 数至少为 GPU 数加 1，以容纳训练资源池和控制任务。使用前检查所选目录的可用空间：

```bash
df -h /tmp /shared/wwx/EasyGAD
```

这些设置用于避开共享盘压力和减少 Ray 预启动进程，不能保证修复尚未定位的 agent 故障。失败后查看本次实际 session 的日志；Ray 会在 `RAY_TMPDIR` 下追加 `ray/`：

```bash
tail -n 100 /tmp/easygad-wwx/ray/session_latest/logs/runtime_env_agent.{log,err,out}
tail -n 100 /tmp/easygad-wwx/ray/session_latest/logs/raylet.{out,err}
```

补充的 agent 日志显示进程在 18:29:12 打印 `Listening to address ... port 57992`，但这仍不能证明端口已成功监听。Ray 的该条日志在 agent 构造阶段打印，实际 HTTP 服务之后才启动（[官方 agent 源码](https://raw.githubusercontent.com/ray-project/ray/ray-2.41.0/python/ray/_private/runtime_env/agent/runtime_env_agent.py)、[服务启动入口](https://raw.githubusercontent.com/ray-project/ray/ray-2.49.0/python/ray/_private/runtime_env/agent/main.py)）。需要结合实际安装的 Ray 版本和同一 session 的 raylet 日志继续排查，不把空 stderr 当作服务正常的证明。

保留日志和 checkpoint。不要仅为绕过目录检查删除原实验，也不要在缺少 agent 错误依据时盲目升级 Ray 或 grpc。

## 先说结论

- full 流水线从**原始学生模型**开始，先 warmup，再 GAD；不是从已训练的 SeqKD 模型继续训练。本次为优先跑通而改用 `/shared/public_models/Qwen2.5-0.5B`，因此不能把最终结果当作与 1.5B SeqKD 的同模型对照。
- **不能直接把 SeqKD checkpoint 交给现有 `run_only_gad_optimized.sh`。**SeqKD 的 `global_step_1813` 只有 `actor/`，没有 `critic/`；onlygad 脚本要求同时具备 warmup 后的 actor 与 critic。因此 onlygad 脚本保持原样，先运行 full 流水线（warmup → GAD）。
- 两个 full optimized 脚本都改成 warmup 1 epoch、GAD 1 epoch，作为资源受限时的**第一轮实验**，不是“1 epoch 已足够”的结论。根据曲线和水印检测结果决定是否继续。
- 1+3 号 GPU 的 0.5B 全参数版已通过 warmup 2 step + GAD 2 step 短测；完整 1 epoch + 1 epoch 尚未验证。LoRA 更省显存，但不一定更快；此前 SeqKD 的 LoRA 实测反而比全参数慢。

## 已修改的服务器脚本

| 脚本 | 用途 | 初始 actor 学习率 | 资源设置 |
|---|---|---:|---|
| `scripts/train/run_full_gad_optimized.sh` | 全参数 warmup + GAD | `1e-6` | 尊重外部 GPU 设置，默认 1+3、2 卡、0.5B；vLLM 显存比例 0.45 |
| `scripts/train/run_full_gad_lora_optimized.sh` | LoRA warmup + GAD | `5e-6`，rank 16 | 默认 2 GPU；actor/critic 均使用原脚本的 offload |

本次修改仅针对全参数脚本：其 `--model` 默认改为 `/shared/public_models/Qwen2.5-0.5B`；LoRA 脚本默认仍为 `/shared/public_models/Qwen2.5-1.5B-Instruct`。两者的 critic 学习率均为 `1e-5`；`--reward_model` 可省略，默认从各自的原始学生模型初始化**独立的 critic 骨干**。如需与 1.5B SeqKD 基线比较，不要用 0.5B 结果直接对照。

两阶段当前都使用 gamma=0.5、delta=3 的 KGW 教师数据：训练集 `data/dolly15k_qwen2_5_14b_kgw_gamma0.5_delta3_train.parquet`，验证集 `data/dolly15k_qwen2_5_14b_kgw_gamma0.5_delta3_test.parquet`。每次取 8 个 prompt；warmup 每个 prompt 生成 1 条，GAD 每个 prompt 生成 2 条。GAD 使用 GRPO 和 discriminator，不能简单照搬 SeqKD 中 `n=1` 的资源配置。脚本保持 prompt 上限 2048、response 上限 1536；每 250 step 验证，每 500 step 保存，最多保留最近 2 份 actor/critic checkpoint。本次全参数脚本两卡 vLLM 显存比例为 0.45、每卡动态 token 预算 8192，tensor parallel 为 1。

全参数版把 warmup 与 GAD checkpoint 放在不同目录，并在 GAD 阶段重新初始化优化器；这一路径已通过 1+3 号卡 2+2 step 短测。LoRA 版通过 warmup checkpoint 恢复 actor/critic 的权重和优化器，但使用新数据迭代器进入 GAD 阶段；LoRA 阶段衔接本次未测试。

## 本次全参数 full：1+3 号卡、0.5B

由用户在**服务器**自行执行：

```bash
cd /shared/wwx/EasyGAD
conda activate wm
nvidia-smi
bash scripts/train/run_full_gad_optimized.sh \
  --exp_name kgw_gad_05b_14b_full --nnodes 1 --gpus_per_node 2
```

新实验用未使用的 `--exp_name`；已有实验按上面的方式加 `--resume`。脚本内默认原始 0.5B 模型、`VLLM_USE_V1=0`、SwanLab 项目和云端模式。GPU 和 Ray 目录可由外部环境或参数配置。运行前会用 `swanlab verify` 检查登录；失败则在启动 Ray 前退出。脚本的 warmup 与 GAD 都配置 `console` + `swanlab` 记录，SwanLab 项目为 `easyGAD-wm`，两个 run 的名字分别带 `_warmup`、`_gad` 后缀。网络配置由用户自行管理。

两阶段 checkpoint 分别在 `checkpoints/<exp_name>/warmup` 和 `checkpoints/<exp_name>/gad`。`--gpu_memory_utilization 0.45` 是 vLLM 按每张卡**总显存**计算的使用预算比例，并不意味着整个训练只占 45% 显存；actor、critic、Ray 还会占显存。训练时留意 `nvidia-smi`、step 是否推进、验证是否完成以及 SwanLab 页面上两个 run 是否出现。

`--constrained_2gpu` 仍只接受 `CUDA_VISIBLE_DEVICES=2,3`、`--gpus_per_node 2` 和 `--nnodes 1`；当前恢复示例的 1+2 号卡不使用该参数。

## LoRA 命令（另一套脚本，不属于本次修改）

先确认目标卡的使用已协调。以下仍是 1.5B LoRA 原配置的两卡启动命令；它没有经过本次 1+3、0.5B 和 SwanLab 验证，不要把上面 full 的短测结果套用到 LoRA：

```bash
cd /shared/wwx/EasyGAD
conda activate wm
CUDA_VISIBLE_DEVICES=1,3 bash scripts/train/run_full_gad_lora_optimized.sh \
  --model /shared/public_models/Qwen2.5-1.5B-Instruct \
  --exp_name kgw_gad_lora_13_v1 --nnodes 1 --gpus_per_node 2
```

## 1 epoch 是否够，以及如何看结果

从此前的 SeqKD 实验只能确认 SFT 的 ROUGE-L 有提升，不能推出 GAD 的最优轮数。GAD 还要训练 discriminator，且 PPO 的优化目标不同。因此 **warmup 1 epoch + GAD 1 epoch 是起点**：先看 warmup 后 critic 的 `critic/d_loss`、`critic/d_acc` 是否正常记录，再看 GAD 各 checkpoint 的验证 ROUGE-L、回答质量和水印指标。尤其需要用相同生成设置比较 SeqKD 基线与 GAD 的 AUROC、`TPR@FPR=1%/5%`，不能只看训练 loss 或 ROUGE-L。若 GAD 中后段仍持续改善，再考虑续训；若明显退化，应选较早 checkpoint。

当前 500 条 KGW test 数据同时用于训练期验证和水印分析。最终报告最好另用未参与选模型、选阈值的 prompt 测一次，避免高估结果。

## 耗时预估

此前 SeqKD 在两卡上完成约 1813 step，墙钟时间约 3 小时 50 分。这里每个阶段也约 1813 step，但 warmup 多了 critic 更新，GAD 还做双采样、critic 更新与 PPO，因此**不能按 SeqKD 的 4 小时估算**。根据 1+3 号卡的极短测试，当前 0.5B full 先粗略预留 **12–24 小时**；这不是完整训练实测，两卡上其他任务、验证和 checkpoint 写入都可能拉长时间。LoRA 的旧粗估为两卡 **20–40 小时**，不适用于本次 0.5B full。

最可靠的办法是观察每个阶段前 30–50 个稳定 step 的 `timing_s/step`，再按剩余 step 数估算；首轮模型加载、验证和保存另计时间。2026-09-27 服务器 `/shared` 约剩 301 GB，Ray 因文件系统使用率超过 95% 会报警；训练期间可用 `df -h /shared/wwx/EasyGAD` 检查。不要删除或移动其他人的文件。

## 检查记录

2026-10-09 本地已通过 `bash -n`、Python 语法检查、`git diff --check` 和 19 项离线回归测试：

```bash
python -m unittest discover -s tests/scripts -p test_full_gad_resume.py -v
```

测试用临时目录和模拟命令覆盖阶段恢复、GPU/Ray 参数传递、损坏 checkpoint 检查和最终步数边界，不启动真实训练，不联网。当前本地环境没有 Ray、PyTorch 或 GPU 训练依赖，因此未验证服务器上的 agent 启动、真实 checkpoint 加载和完整训练。

2026-09-27 的历史记录：1+3 号卡的 0.5B full 曾完成 warmup 2 step + GAD 2 step 短测，SwanLab 登录曾验证成功；这些历史结果不能作为当前服务器环境检查结果。`run_full_gad_lora_optimized.sh` 和 `run_only_gad_optimized.sh` 本次未修改。
