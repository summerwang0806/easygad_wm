# EasyGAD：从原始学生模型训练 KGW GAD 的运行说明

更新于 2026-09-27。服务器项目目录：`/shared/wwx/EasyGAD`。本页的全参数运行命令已调整为 **1+3 号 GPU、原始 Qwen2.5-0.5B、SwanLab 云端记录**。

## 先说结论

- full 流水线从**原始学生模型**开始，先 warmup，再 GAD；不是从已训练的 SeqKD 模型继续训练。本次为优先跑通而改用 `/shared/public_models/Qwen2.5-0.5B`，因此不能把最终结果当作与 1.5B SeqKD 的同模型对照。
- **不能直接把 SeqKD checkpoint 交给现有 `run_only_gad_optimized.sh`。**SeqKD 的 `global_step_1813` 只有 `actor/`，没有 `critic/`；onlygad 脚本要求同时具备 warmup 后的 actor 与 critic。因此 onlygad 脚本保持原样，先运行 full 流水线（warmup → GAD）。
- 两个 full optimized 脚本都改成 warmup 1 epoch、GAD 1 epoch，作为资源受限时的**第一轮实验**，不是“1 epoch 已足够”的结论。根据曲线和水印检测结果决定是否继续。
- 1+3 号 GPU 的 0.5B 全参数版已通过 warmup 2 step + GAD 2 step 短测；完整 1 epoch + 1 epoch 尚未验证。LoRA 更省显存，但不一定更快；此前 SeqKD 的 LoRA 实测反而比全参数慢。

## 已修改的服务器脚本

| 脚本 | 用途 | 初始 actor 学习率 | 资源设置 |
|---|---|---:|---|
| `scripts/train/run_full_gad_optimized.sh` | 全参数 warmup + GAD | `1e-6` | 本次默认固定 1+3 号 GPU、2 卡、0.5B；vLLM 显存比例 0.45 |
| `scripts/train/run_full_gad_lora_optimized.sh` | LoRA warmup + GAD | `5e-6`，rank 16 | 默认 2 GPU；actor/critic 均使用原脚本的 offload |

本次修改仅针对全参数脚本：其 `--model` 默认改为 `/shared/public_models/Qwen2.5-0.5B`；LoRA 脚本默认仍为 `/shared/public_models/Qwen2.5-1.5B-Instruct`。两者的 critic 学习率均为 `1e-5`；`--reward_model` 可省略，默认从各自的原始学生模型初始化**独立的 critic 骨干**。如需与 1.5B SeqKD 基线比较，不要用 0.5B 结果直接对照。

两阶段都使用 KGW 教师数据：训练集 `data/dolly15k_qwen2_5_14b_kgw_train.parquet`（14,511 条），验证集 `data/dolly15k_qwen2_5_14b_kgw_test.parquet`（500 条）。每次取 8 个 prompt；warmup 每个 prompt 生成 1 条，GAD 每个 prompt 生成 2 条。GAD 使用 GRPO 和 discriminator，不能简单照搬 SeqKD 中 `n=1` 的资源配置。脚本保持 prompt 上限 2048、response 上限 1536；每 250 step 验证，每 500 step 保存，最多保留最近 2 份 actor/critic checkpoint。本次全参数脚本两卡 vLLM 显存比例为 0.45、每卡动态 token 预算 8192，tensor parallel 为 1。

全参数版把 warmup 与 GAD checkpoint 放在不同目录，并在 GAD 阶段重新初始化优化器；这一路径已通过 1+3 号卡 2+2 step 短测。LoRA 版通过 warmup checkpoint 恢复 actor/critic 的权重和优化器，但使用新数据迭代器进入 GAD 阶段；LoRA 阶段衔接本次未测试。

## 本次全参数 full：1+3 号卡、0.5B

先在**本地电脑**确保 `127.0.0.1:56734` 的代理正在运行，再用以下命令登录服务器，且在训练期间保持该 SSH 连接不断开（`-R` 把本地代理转发到服务器的 7890 端口）：

```powershell
ssh -R 7890:127.0.0.1:56734 -p 3389 wwx@10.107.6.60
```

然后在**服务器**执行；不要把服务器上的 `curl` 与本地 PowerShell 命令混用：

```bash
cd /shared/wwx/EasyGAD
conda activate wm
nvidia-smi
bash scripts/train/run_full_gad_optimized.sh \
  --exp_name kgw_gad_05b_14b_full --nnodes 1 --gpus_per_node 2
```

`--exp_name` 必须是尚未使用的新名字；脚本会拒绝覆盖已有 checkpoint 目录。脚本内已经设置 `CUDA_VISIBLE_DEVICES=1,3`、原始 0.5B 模型、`RAY_TMPDIR=/shared/wwx/EasyGAD/ray_tmp`、`VLLM_USE_V1=0`、SwanLab 项目/密钥/云端模式及代理，无须再手动 `export`。运行前会用 `swanlab verify` 检查登录；失败则在启动 Ray 前退出。脚本的 warmup 与 GAD 都配置 `console` + `swanlab` 记录，SwanLab 项目为 `easyGAD-wm`，两个 run 的名字分别带 `_warmup`、`_gad` 后缀。若断开 SSH 隧道，之后的云端上传可能失败。

两阶段 checkpoint 分别在 `checkpoints/<exp_name>/warmup` 和 `checkpoints/<exp_name>/gad`。`--gpu_memory_utilization 0.45` 是 vLLM 按每张卡**总显存**计算的使用预算比例，并不意味着整个训练只占 45% 显存；actor、critic、Ray 还会占显存。训练时留意 `nvidia-smi`、step 是否推进、验证是否完成以及 SwanLab 页面上两个 run 是否出现。

本次不使用 `--constrained_2gpu`：它仍只接受 `CUDA_VISIBLE_DEVICES=2,3`，与脚本内固定的 1+3 不相容。也不要用当前 full 脚本的旧单卡或 2+3 命令。

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

## 检查和回退

本次 full 脚本已通过 `bash -n`；代理下 `swanlab verify` 成功登录，且用已有实验名做过启动前检查：认证成功后，脚本因 checkpoint 目录已存在而按预期退出，没有启动训练。此前 1+3 号卡的 0.5B full 仅完成 warmup 2 step + GAD 2 step 短测，完整训练及云端指标写入仍须实际运行确认。`run_full_gad_lora_optimized.sh` 和 `run_only_gad_optimized.sh` 本次未修改。
