# Clean 判别器 + KGW 学生 Warmup → KGW GAD

入口：`scripts/train/run_full_gad_cleanD_kgwSFT_kgwGAD_optimized.sh`。

## 已核对的数据

| 文件 | 用途 | 核对结果 |
| --- | --- | --- |
| `data/dolly15k_qwen2_5_14b_clean_train.parquet` | Warmup 判别器正样本 | 14,511 行，对应评分文件全部为 `label=clean`、`is_watermarked=false` |
| `data/dolly15k_qwen2_5_14b_kgw_gamma0.5_delta3_newtrain.parquet` | Warmup 学生 SFT、后续 GAD | 14,511 行，对应评分文件全部为 `label=kgw`、`is_watermarked=true` |
| `data/dolly15k_qwen2_5_14b_kgw_gamma0.5_delta3_newtest.parquet` | 两阶段验证，不更新梯度 | 500 行，与训练集无 ID 重叠 |

两份训练 Parquet 的 ID 唯一，行顺序、提示 `content` 和全部非回答字段完全一致，无空回答，可以逐条配对。clean 生成入口 `wm_data/generate_clean.py` 使用 `watermark=none`；KGW 生成入口使用 `watermark=kgw`。`wm_data/README.md` 中的 `newtrain` 命令显式指定 Qwen2.5-14B-Instruct、gamma=0.5、delta=3、hash_key=15485863。

数据来源边界：最终 Parquet 和评分 JSONL 没有保留完整历史模型与采样参数，不能仅凭 clean 文件名独立证明它当时使用的模型大小和生成参数。当前生成脚本默认模型已是 0.5B；若以后重新生成 14B clean 数据，应显式传 `--model /shared/public_models/Qwen2.5-14B-Instruct`。

## 训练行为

| 阶段 | 判别器正样本 | 学生更新 |
| --- | --- | --- |
| Warmup | 上述 clean_train 的回答 | 在上述 KGW newtrain 回答上 SFT |
| GAD | 上述 KGW newtrain 的回答 | 学生 rollout + PPO |

两阶段判别器负样本均来自当前学生生成。初始学生默认从 `/shared/public_models/Qwen2.5-0.5B` 权重加载，随后在 warmup 内用 KGW 回答做 SFT；Parquet 是训练目标，不是模型权重。GAD 继承 warmup 的学生和判别器权重。

新脚本最终调用现有 `scripts/train/run_full_gad_optimized.sh`，沿用相同训练超参数：单节点双 GPU，warmup/GAD 各 1 epoch，batch size 8，学生学习率均为 `1e-6`，判别器学习率 `1e-5`。保留 `critic_warmup=10`，warmup 前 9 步只更新判别器，第 10 步起学生参与 SFT。两阶段均有进度条，默认记录控制台 + SwanLab。

## 运行

在服务器仓库根目录、激活训练环境后执行，将 `0,1` 换为实际 GPU：

```bash
CUDA_VISIBLE_DEVICES=0,1 bash scripts/train/run_full_gad_cleanD_kgwSFT_kgwGAD_optimized.sh \
  --model /shared/public_models/Qwen2.5-0.5B \
  --exp_name cleanD_kgwSFT_kgwGAD_v1
```

需要先检查数据和配置时，在同一命令后加 `--dry_run`。这个检查只做 CPU 数据准备，不启动训练、模型、Ray 或 SwanLab。正常训练使用服务器已有的 SwanLab 登录或 `SWANLAB_API_KEY`，项目默认 `easyGAD-wm`，两个实验分别为 `<exp_name>_warmup` 和 `<exp_name>_gad`。

中断后用相同配置、相同实验名加 `--resume`，从已完整保存的 checkpoint 继续。本配置使用新的实验名，避免继承其他配置的 checkpoint。

```text
checkpoints/<exp_name>/warmup/
checkpoints/<exp_name>/gad/
```

脚本自动按唯一 ID 配对，并生成独立的 warmup 文件：

```text
data/dolly15k_qwen2_5_14b_cleanD_kgwSFT_gamma0.5_delta3_newtrain.parquet
```

其中 `teacher_response` 保留 clean 回答，供判别器使用；新增 `sft_response` 保存对应 KGW 回答，只供 warmup 学生 SFT 使用。原始输入文件保持不变。后续 GAD 直接读取原始 KGW newtrain。重复运行会检查并复用一致的配对文件；若输入变化，用 `--merged_file` 指定新文件名。

可用 `--clean_train_file`、`--kgw_train_file`、`--val_file` 覆盖默认数据路径，其他可选参数见脚本的 `--help`。本入口需要同时具备当前版本的 `tools/prepare_split_warmup_data.py`、基础训练脚本，以及先前已加入的 dataset/actor 分离 SFT 目标支持。
