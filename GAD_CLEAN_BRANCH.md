# KGW Warmup → clean GAD：独立对照分支

## 实验设置

脚本：`scripts/train/run_full_gad_clean_branch_optimized.sh`。
只新增文件，不修改原 GAD、SeqKD 或 clean Warmup 分支，不干扰当前训练。

| 阶段 | 训练数据 | 模型初始化 | 训练方式 |
| --- | --- | --- | --- |
| Warmup | 14B 教师 KGW 回答 | 原始 Qwen2.5-0.5B；actor、critic 独立骨干 | actor 监督训练；critic 比较教师回答与学生生成回答 |
| GAD | 14B 教师 clean 回答 | 本次 Warmup 的 actor 和 critic | actor 使用 critic 奖励进行 GAD 更新；critic 学习 clean 教师回答相对学生回答的排序 |

训练文件分别是：

- `data/dolly15k_qwen2_5_14b_kgw_train.parquet`
- `data/dolly15k_qwen2_5_14b_clean_train.parquet`

“clean GAD”是指教师目标数据不加水印，不代表学生生成的回答一定没有水印，
因为学生和 critic 已经做过 KGW Warmup。这也不是第二轮 clean SeqKD，
GAD 阶段仍使用原来的对抗训练方法。

两阶段默认验证均使用共同的 KGW test，与已有分支保持相同参考。
验证不更新参数；它不会把 KGW 回答混入 clean GAD 训练。
如需 clean 验证，可显式传：
`--gad_val_file data/dolly15k_qwen2_5_14b_clean_test.parquet`。
改变参考后不要直接与 KGW 参考的 ROUGE-L 曲线比较。

## 等当前实验结束后运行

选卡前确认显卡空闲；下面的 2,3 只是示例，不表示已检查实时占用。

```bash
cd /app/wwx/EasyGAD
conda activate wm

CUDA_VISIBLE_DEVICES=2,3 \
bash scripts/train/run_full_gad_clean_branch_optimized.sh \
  --model /shared/public_models/Qwen2.5-0.5B \
  --exp_name kgw_gad_05b_kgwwarmup_cleangad_control \
  --nnodes 1 --gpus_per_node 2 \
  --warmup_epochs 1 --gad_epochs 1
```

在命令末尾加 `--dry_run`，仅检查配置，不训练、不初始化 GPU、不访问 SwanLab。
未指定显卡时默认 0,3；明确指定后脚本不会覆盖。
单卡可用 `CUDA_VISIBLE_DEVICES=3` 配合 `--gpus_per_node 1`，
自动降低 vLLM 内存占用并启用 actor offload。

沿用原分支的 SwanLab 配置，正式训练前检查认证与网络。
若需要代理，请保持 SSH 反向隧道和代理环境可用。
不要使用 `bash -x` 暴露脚本中的密钥。

## 保持一致的参数与输出

默认 Warmup/GAD 各 1 epoch，batch=8；
actor Warmup/GAD LR 均为 1e-6，critic LR=1e-5；
Warmup rollout n=1，GAD n=2；
Warmup critic_warmup=10，GAD critic_warmup=0；
max prompt/response=2048/1536，temperature=0.8；
test_freq=250，save_freq=500；双卡 vLLM 内存比例=0.45。
这些与已有分支保持一致，不代表已经证明各 1 epoch 最优。

默认 `NCCL_P2P_DISABLE=1`；阶段间用 CPU FSDP merger 导出 actor 和 critic。
本脚本会重新做本实验的 KGW Warmup，不自动借用旧实验 checkpoint。

独立输出目录：
`checkpoints/kgw_gad_05b_kgwwarmup_cleangad_control/`，
内含 `warmup/` 和 `gad/`。同名目录存在时必须换新的实验名，不覆盖旧结果。
SwanLab 记录为 `<exp_name>_warmup`、`<exp_name>_gad`。

## 结果应该怎么比较

此分支检验 KGW Warmup 学到的水印，在 clean 目标的 GAD 更新后是否保留或减弱；
结果方向不能提前保证。它同时改变 GAD 的教师目标以及 critic 的学习目标，
不能单独归因于 actor 或 critic。

与「KGW Warmup → KGW GAD」和「clean Warmup → KGW GAD」比较时，
使用相同提示词、解码、检测器配置和 clean 负样本，
并检查 AUROC、TPR@FPR≤5%/10%、对共同 teacher clean/Dolly 参考的 ROUGE-L、
严重重复输出。主评估生成时不要另加显式 KGW 采样器。

## 本次检查

已检查脚本语法和单卡/双卡 dry-run；没有启动实际训练，
没有验证本分支的实际训练完成时间或效果。
