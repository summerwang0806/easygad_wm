# clean Warmup → clean GAD 全 clean 对照实验

独立脚本：`scripts/train/run_full_gad_all_clean_optimized.sh`。
本次只新增脚本与本文档，不修改已有分支，不启动或停止训练任务。

## 两阶段

| 阶段 | 初始化 | 教师目标与训练方式 |
| --- | --- | --- |
| clean Warmup | 原始 Qwen2.5-0.5B；actor 与 critic 独立骨干 | clean 教师回答监督训练 actor；critic 比较 clean 教师与学生生成回答 |
| clean GAD | 本次 Warmup 导出的 actor、critic | actor 使用 critic 奖励做 GAD 更新；critic 继续以 clean 教师与学生回答学习排序 |

两阶段训练均使用：
`data/dolly15k_qwen2_5_14b_clean_train.parquet`。
默认验证均使用：
`data/dolly15k_qwen2_5_14b_clean_test.parquet`。

没有使用已有 SeqKD 或 KGW Warmup 模型；两阶段使用 clean 教师回答。
GAD 仍是原来的对抗训练，而不是第二轮 SeqKD。
clean 数据与 clean 训练不保证水印检测分数严格为零，也不保证质量提高，
需要统一的实际评估确认。

## 运行

等现有实验完成后，确认选中的显卡可用；下面 2,3 是示例，不表示已检查实时占用。

```bash
cd /app/wwx/EasyGAD
conda activate wm

CUDA_VISIBLE_DEVICES=2,3 \
bash scripts/train/run_full_gad_all_clean_optimized.sh \
  --model /shared/public_models/Qwen2.5-0.5B \
  --exp_name gad_05b_cleanwarmup_cleangad_control \
  --nnodes 1 --gpus_per_node 2 \
  --warmup_epochs 1 --gad_epochs 1
```

末尾加 `--dry_run` 只检查配置，不训练、不初始化 GPU、不访问 SwanLab。
显卡可换成其他已确认可用的两张卡，脚本尊重外部显卡选择。
单卡用 `CUDA_VISIBLE_DEVICES=3` 和 `--gpus_per_node 1`，
建议另取实验名；单卡会启用 actor offload 并降低 vLLM 内存比例。

## 验证参考和跨分支比较

默认 ROUGE-L 对 clean 教师 test 回答计算，不能直接与此前对 KGW 回答的 ROUGE-L 曲线比较。
若希望沿用共同 KGW 参考，在上面的命令中追加以下两个参数：

```bash
  --warmup_val_file data/dolly15k_qwen2_5_14b_kgw_test.parquet \
  --gad_val_file data/dolly15k_qwen2_5_14b_kgw_test.parquet
```

追加时上一行末尾也要加续行反斜杠。
验证不参与参数更新；即便改为 KGW 验证，训练仍然是 clean → clean。
最终公平评估应固定提示词、解码、检测器及 clean 负样本，
比较 AUROC、TPR@FPR≤5%/10%、对共同 clean/Dolly 参考的 ROUGE-L 及严重重复输出。
生成评估文本时不要额外注入 KGW 采样器。

## 参数和保存

沿用已有分支的训练预算与超参数：
Warmup/GAD 各 1 epoch，batch=8；
actor 两阶段 LR=1e-6，critic LR=1e-5；
rollout n 分别为 1、2；critic_warmup 分别为 10、0；
prompt/response 上限 2048/1536，temperature=0.8；
save_freq=500，test_freq=250；双卡 vLLM 内存比例=0.45。
各 1 epoch 是对照预算，不代表已证明足够或最优。

默认 `NCCL_P2P_DISABLE=1`，阶段间 CPU 合并两份 Warmup 模型后进入 GAD。
SwanLab 沿用已有脚本配置，正式训练前执行认证/网络检查；
需要代理时保持 SSH 反向隧道及代理环境。不要用 `bash -x` 暴露密钥。

输出：
`checkpoints/gad_05b_cleanwarmup_cleangad_control/warmup/`、
`checkpoints/gad_05b_cleanwarmup_cleangad_control/gad/`。
同名目录存在时退出，必须换新实验名，不覆盖旧结果。
SwanLab 实验名为 `<exp_name>_warmup` 和 `<exp_name>_gad`。

已通过语法检查及单卡/双卡 dry-run；尚未启动实际训练。
