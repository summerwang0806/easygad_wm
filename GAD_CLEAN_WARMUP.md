# Clean Warmup → KGW GAD 对照实验

## 文件与实验目的

独立脚本：`scripts/train/run_full_gad_clean_warmup_optimized.sh`。
原有 `run_full_gad_optimized.sh` 和 SeqKD 脚本不修改。

本实验比较原来的「KGW Warmup → KGW GAD」与新的「clean Warmup → KGW GAD」。
同时改变 actor 和 critic 的 Warmup 数据，检验联合初始化策略的影响；
不能凭这个实验单独归因于 actor 或 critic。

## 两阶段的输入输出

| 阶段 | actor 输入及训练 | critic 输入及训练 | 输出 |
| --- | --- | --- | --- |
| clean Warmup | 原始 Qwen2.5-0.5B，以 clean 教师回答做监督训练 | 独立原始 Qwen2.5-0.5B 骨干，以 clean 教师回答和当前学生生成回答做排序训练 | 本实验的 Warmup actor 和 critic |
| KGW GAD | 上一步 actor，以生成回答和 critic 奖励进行 GAD 更新 | 上一步 critic，以 KGW 教师回答和当前学生生成回答继续排序训练 | GAD actor 和 critic |

critic 的任务是提高教师回答相对学生回答的分数，不是分类 clean 与 KGW。
没有使用已有 SeqKD baseline 或已有 KGW Warmup checkpoint 初始化。

训练文件：
- Warmup：`data/dolly15k_qwen2_5_14b_clean_train.parquet`
- GAD：`data/dolly15k_qwen2_5_14b_kgw_train.parquet`

实地检查：两份训练文件均为 14,511 条，提示词逐行一致。
两阶段默认验证均使用 KGW test，与原实验保持相同的 ROUGE-L 参考；
验证不更新参数，因此不会把 KGW 回答加入 clean Warmup 的训练损失。
若想改验证参考，可以使用 `--warmup_val_file` / `--gad_val_file`，
但改后不要直接与原来不同参考的 ROUGE-L 曲线比较。

## 运行

先确认选中的显卡可用，并在需要代理时保留 SSH 反向隧道。
脚本沿用原脚本的 SwanLab 配置，正式训练前执行 `swanlab verify`；
认证或网络失败就退出。不要用 `bash -x` 输出含密钥的环境设置。

```bash
cd /app/wwx/EasyGAD
conda activate wm

# 配置检查，不启动训练、不初始化 GPU、不访问 SwanLab。
CUDA_VISIBLE_DEVICES=0,3 bash scripts/train/run_full_gad_clean_warmup_optimized.sh \
  --model /shared/public_models/Qwen2.5-0.5B \
  --exp_name kgw_gad_05b_cleanwarmup_control \
  --nnodes 1 --gpus_per_node 2 \
  --warmup_epochs 1 --gad_epochs 1 --dry_run

# 正式训练：去掉 --dry_run。
CUDA_VISIBLE_DEVICES=0,3 bash scripts/train/run_full_gad_clean_warmup_optimized.sh \
  --model /shared/public_models/Qwen2.5-0.5B \
  --exp_name kgw_gad_05b_cleanwarmup_control \
  --nnodes 1 --gpus_per_node 2 \
  --warmup_epochs 1 --gad_epochs 1
```

可将 `CUDA_VISIBLE_DEVICES=0,3` 换成经确认可用的两张卡，例如 `2,3`。
脚本尊重外部显卡选择，不会覆盖它；未设置时默认 0,3。
`--nnodes 1` 表示一台服务器，`--gpus_per_node 2` 表示这台服务器上两张卡。

单卡方案：
```bash
CUDA_VISIBLE_DEVICES=3 bash scripts/train/run_full_gad_clean_warmup_optimized.sh \
  --exp_name kgw_gad_05b_cleanwarmup_control_single \
  --nnodes 1 --gpus_per_node 1 \
  --warmup_epochs 1 --gad_epochs 1
```

单卡自动启用 actor offload 并降低 vLLM 内存比例；它是资源降级方案，
正式对照优先采用相同的双卡配置。脚本默认设置 `NCCL_P2P_DISABLE=1`，
对应此前该服务器双卡通信排查的绕行设置；它不是额外训练算法变更。

## 保留的训练配置

- Warmup 1 epoch，GAD 1 epoch；这是与已有实验一致的预算，不代表保证最优。
- global train batch=8，Warmup rollout n=1，GAD rollout n=2。
- actor Warmup LR=1e-6，actor GAD LR=1e-6，critic LR=1e-5。
- max prompt length=2048，max response length=1536，temperature=0.8。
- Warmup critic_warmup=10，GAD critic_warmup=0；与原 GAD 脚本相同。
- test_freq=250，save_freq=500；双卡 vLLM memory utilization=0.45。
- 阶段切换时用 CPU 上的 `scripts/model_merger.py merge --backend fsdp`
  导出本次 Warmup 的 actor 和 critic，再传入 GAD；兼容普通 Tensor 和 DTensor。
- 不覆盖旧实验目录；同名目录已存在时必须换一个新的 `--exp_name`。

## 输出与评估

默认输出：
```text
checkpoints/kgw_gad_05b_cleanwarmup_control/
├── warmup/global_step_*/actor/
├── warmup/global_step_*/critic/
├── gad/global_step_*/actor/
└── gad/global_step_*/critic/
```

Warmup 的最新 actor/critic 会自动导出到对应的 `huggingface/` 子目录。
GAD 最终 checkpoint 仍是训练分片，要独立调用 actor 生成文本时再导出。
critic 是评分模型，不作为普通文本生成模型调用。

SwanLab 分别记录 `<exp_name>_warmup` 与 `<exp_name>_gad`。

建议对照原实验，使用同一组 500 条提示词、相同解码配置、检测器和 clean 负样本：
比较 Warmup 与 GAD actor 的 AUROC、TPR@FPR≤5%/10%、
对共同 teacher clean / Dolly 参考的 ROUGE-L，以及严重重复输出。
主实验生成时不要另外显式注入 KGW，否则无法区分训练学到的水印与采样器水印。

## 本次检查范围

已完成脚本语法检查和双卡默认配置 dry-run。
尚未启动本实验训练，没有验证它的实际训练结果或耗时。
