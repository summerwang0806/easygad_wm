# 原始 KGW 判别器 + Para 学生 Warmup → Para GAD

入口：`scripts/train/run_full_gad_kgwD_paraSFT_paraGAD_optimized.sh`。

| 阶段 | 判别器正样本 | 学生更新 |
| --- | --- | --- |
| Warmup | 原始 `data/dolly15k_qwen2_5_14b_kgw_gamma0.5_delta3_newtrain.parquet` | 在 Para `data/dolly15k_qwen2_5_14b_kgw_gamma0.5_delta3_up_dipper_newtrain.parquet` 上 SFT |
| GAD | Para `data/dolly15k_qwen2_5_14b_kgw_gamma0.5_delta3_up_dipper_newtrain.parquet` | 学生 rollout + PPO |

两阶段判别器的负样本均为当前学生生成的回答。初始学生默认从原始 `/shared/public_models/Qwen2.5-0.5B` 加载，然后在 warmup 内用 Para 数据做 SFT；Parquet 是训练数据，不是模型权重路径。GAD 会继承 warmup 的学生和判别器权重，不会重新初始化。

默认每阶段 1 epoch，batch size 8；warmup 学生学习率 `1e-6`、GAD 学生学习率 `1e-6`、判别器学习率 `1e-5`，其余参数沿用现有优化版。保留 `trainer.critic_warmup=10`：warmup 前 9 步只更新判别器，第 10 步起学生参与 SFT。若要改变轮数，可传 `--warmup_epochs` 和 `--gad_epochs`。

验证集默认是原始 `data/dolly15k_qwen2_5_14b_kgw_gamma0.5_delta3_newtest.parquet`，不参与梯度更新。

## 对比实验的一致性

新入口最终调用同一份 `scripts/train/run_full_gad_optimized.sh`，不另设训练超参数。在模型路径、GPU 数量、环境和命令行覆盖参数相同的情况下，学习率、batch size、epoch、prompt/response 长度、采样温度与数量、损失函数、优化器、随机种子、shuffle、保存/验证频率、checkpoint 衔接和日志设置均与原入口一致。

当前原入口的训练文件已经是 Para `up_dipper_newtrain`：因此本对比唯一预期的训练差异是 **warmup 判别器正样本改为原始 KGW**；warmup 学生 SFT、GAD 数据和验证集均不变。已核对这两份指定训练文件的 ID 顺序和全部非回答字段完全相同，合并不会改变提示与采样顺序。请给两组实验不同的实验名，以保存各自 checkpoint。

## 服务器运行

代码提交并推送后，在服务器的现有仓库拉取更新：

```bash
cd /shared/wwx/EasyGAD
git pull
conda activate wm
```

本配置涉及以下 5 个文件，拉取更新时会一起获取：

```text
scripts/train/run_full_gad_kgwD_paraSFT_paraGAD_optimized.sh
scripts/train/run_full_gad_optimized.sh
tools/prepare_split_warmup_data.py
verl/utils/dataset/rl_dataset.py
verl/workers/actor/dp_actor.py
```

服务器需要已有训练依赖、上述三份 Parquet 和学生模型。新增数据准备步骤使用 `pyarrow`，通常已包含在原训练环境中。

## 先检查，再训练

将下面 `0,1` 换成实际使用的 GPU。默认双卡；单卡使用单个 GPU 编号并加 `--gpus_per_node 1`。

```bash
# CPU 配对数据并检查配置；不启动训练、Ray、模型或 SwanLab。
CUDA_VISIBLE_DEVICES=0,1 bash scripts/train/run_full_gad_kgwD_paraSFT_paraGAD_optimized.sh \
  --model /shared/public_models/Qwen2.5-0.5B \
  --exp_name kgwD_paraSFT_paraGAD_gamma0.5_delta3_v1 \
  --dry_run

# 正式训练；默认与原脚本一样使用控制台 + SwanLab 日志。
CUDA_VISIBLE_DEVICES=0,1 bash scripts/train/run_full_gad_kgwD_paraSFT_paraGAD_optimized.sh \
  --model /shared/public_models/Qwen2.5-0.5B \
  --exp_name kgwD_paraSFT_paraGAD_gamma0.5_delta3_v1
```

默认与原脚本一样使用控制台 + SwanLab 日志，使用服务器已有登录或环境变量中的凭据。若只需控制台日志，可显式加 `--logger console`。脚本不内置 API key。

中断后用相同参数和实验名，加 `--resume`，从已经保存完整的 checkpoint 继续。若是旧实验已完成 warmup 但没有完成标记，可加 `--resume --skip_warmup`。请为本配置使用新的实验名，避免继承其他数据配置的 checkpoint。

输出目录：

```text
checkpoints/<exp_name>/warmup/
checkpoints/<exp_name>/gad/
```

脚本按唯一 `id` 配对，并检查两份数据的提示一致，生成：

```text
data/dolly15k_qwen2_5_14b_kgw_gamma0.5_delta3_kgwD_paraSFT_newtrain.parquet
```

生成文件中 `teacher_response` 是原始 KGW，新增 `sft_response` 是对应 Para。原始输入文件保持不变；重复运行会检查并复用一致的生成文件。输入变化但生成文件已存在时会报错，可用 `--merged_file` 指定新路径。GAD 直接读取原始 Para 文件。

## 验证范围

本地已检查两份实际训练数据：各 14,511 行，可完整配对；14,461 条 Para 回答与原始回答不同，50 条相同；500 条验证样本与训练样本无 ID 重叠。通过 CPU 配对、目标隔离、EOS/padding/position、启动参数和 checkpoint 衔接测试，以及 Bash/Python 语法检查。未启动 GPU 训练。

可在服务器复查 CPU 测试（无需模型）：

```bash
python3 -m unittest discover -s tests/scripts -p 'test_split_warmup_*.py'
python3 -m unittest discover -s tests/scripts -p 'test_full_gad_resume.py'
```
