# Clean 判别器 + Para 学生 Warmup → Para GAD

入口：`scripts/train/run_full_gad_cleanD_paraSFT_paraGAD_optimized.sh`。

| 用途 | 默认数据（相对仓库根目录） |
| --- | --- |
| Warmup 判别器正样本 | `data/dolly15k_qwen2_5_14b_clean_train.parquet` |
| Warmup 学生 SFT | `data/dolly15k_qwen2_5_14b_kgw_gamma0.5_delta3_up_dipper_newtrain.parquet` |
| GAD 教师正样本及提示 | 同一份 DIPPER 改写 `up_dipper_newtrain` |
| 两阶段验证 | `data/dolly15k_qwen2_5_14b_kgw_gamma0.5_delta3_newtest.parquet` |

Para 是 KGW 教师回答经 DIPPER 改写的数据。训练中只有 warmup 判别器的教师正样本使用 clean；学生 SFT 和 GAD 教师目标均使用 Para。验证沿用原始 KGW newtest，不参与梯度更新，可用 `--val_file` 覆盖。

判别器负样本在两阶段均来自当前学生生成。GAD 继承本次 warmup 的学生和判别器权重，并继续更新两者；判别器进入 GAD 后使用 Para 正样本。默认初始学生与独立判别器骨干均加载 `/shared/public_models/Qwen2.5-0.5B`，不是加载已有的 clean checkpoint。

## 服务器运行

先将新增脚本及当前版本的配套代码同步到服务器仓库，激活原有训练环境，并确认三份输入 Parquet 与模型存在。在服务器仓库根目录执行（将 `0,1` 替换为实际 GPU）：

```bash
CUDA_VISIBLE_DEVICES=0,1 bash scripts/train/run_full_gad_cleanD_paraSFT_paraGAD_optimized.sh
```

默认实验名 `cleanD_paraSFT_paraGAD_v1`，单节点双 GPU，warmup/GAD 各 1 epoch，batch size 8；学生两个阶段学习率均为 `1e-6`，判别器为 `1e-5`。沿用基础训练入口的其他超参数、进度条及控制台 + SwanLab 日志，使用服务器已有登录或环境变量凭据。保留 `critic_warmup=10`：warmup 前 9 步只更新判别器，第 10 步起学生参与 SFT。

先做 CPU 数据与配置检查：

```bash
CUDA_VISIBLE_DEVICES=0,1 bash scripts/train/run_full_gad_cleanD_paraSFT_paraGAD_optimized.sh --dry_run
```

`--dry_run` 会生成或校验配对数据，检查模型目录下的 `config.json`，但不加载模型、不启动 Ray 或 GPU 训练、不联系 SwanLab。

单 GPU：

```bash
CUDA_VISIBLE_DEVICES=0 bash scripts/train/run_full_gad_cleanD_paraSFT_paraGAD_optimized.sh --gpus_per_node 1
```

中断后保持相同数据与参数，加 `--resume`。新一轮独立实验用 `--exp_name cleanD_paraSFT_paraGAD_v2` 等新名字。默认输出：

```text
checkpoints/cleanD_paraSFT_paraGAD_v1/warmup/
checkpoints/cleanD_paraSFT_paraGAD_v1/gad/
```

## 数据配对与依赖

脚本按唯一 ID、相同提示配对 clean 与 Para，检查训练/验证 ID 无重叠，生成独立文件：

```text
data/dolly15k_qwen2_5_14b_cleanD_paraSFT_gamma0.5_delta3_newtrain.parquet
```

其中 `teacher_response` 保留 clean 回答供判别器使用；新增 `sft_response` 保存对应 Para 回答供学生 SFT 使用。GAD 直接读取 Para 输入文件。重复执行会校验并复用一致的配对文件；数据改变时使用 `--merged_file` 指定新路径。可用 `--clean_train_file`、`--para_train_file` 覆盖输入，其余选项见 `--help`。

运行依赖同一 checkout 的 `tools/prepare_split_warmup_data.py`、`scripts/train/run_full_gad_optimized.sh`、`verl/utils/dataset/rl_dataset.py` 和 `verl/workers/actor/dp_actor.py` 中的分离 SFT 目标支持，以及原训练环境（含 `pyarrow`）。
