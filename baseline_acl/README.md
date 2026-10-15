# Dipper-UP 基线

用 Dipper 改写 KGW 教师训练回答，再跑两组蒸馏实验。每条回答一次改写；输入超长时保留开头、截去尾部。只替换 `teacher_response`，不改问题和 test 数据。

ACL 论文指定使用 Dipper，但未披露改写粒度；当前整篇模式是本项目配置，不是原论文已确认的设置。

## 1. 下载与检查

```bash
cd /app/wwx/EasyGAD
conda activate wm
python baseline_acl/download_dipper.py
python baseline_acl/download_dipper.py --check

python baseline_acl/paraphrase_up.py \
  --input data/dolly15k_qwen2_5_14b_kgw_train.parquet --preflight
```

模型约 45 GB；预检只用 CPU，不加载模型权重。

默认完整输入上限为 4096 token（含 Dipper 模板和 EOS）。超长回答自动截断，预检显示截断条数，正式运行在 `.audit.json` 中记录行号和截断前后长度；未超长的回答沿用原流程，下面命令无需增加参数。

## 2. 改写训练集

```bash
# 自动选择空闲 GPU；清除以前手动指定的卡号
unset CUDA_VISIBLE_DEVICES

# 这个是0.25/2的kgw参数配置
python baseline_acl/paraphrase_up.py \
  --input data/dolly15k_qwen2_5_14b_kgw_gamma0.5_delta2_train.parquet \
  --output data/dolly15k_qwen2_5_14b_kgw_up_dipper_gamma0.5_delta2_train.parquet \
  --num-gpus 3

# 这个是0.5/2的kgw参数配置
CUDA_VISIBLE_DEVICES=1,2 python baseline_acl/paraphrase_up.py \
  --input data/dolly15k_qwen2_5_14b_kgw_gamma0.5_delta3_newtrain.parquet \
  --output data/dolly15k_qwen2_5_14b_kgw_gamma0.5_delta3_up_dipper_newtrain.parquet \
  --num-gpus 2

CUDA_VISIBLE_DEVICES=2,3 python baseline_acl/paraphrase_up.py \
  --input data/dolly15k_qwen2_5_14b_kgw_gamma0.5_delta3_newtrain.parquet \
  --output data/dolly15k_qwen2_5_14b_kgw_gamma0.5_delta3_up_dipper_newtrain.parquet \
  --num-gpus 2

CUDA_VISIBLE_DEVICES=3 python baseline_acl/paraphrase_up.py \
  --input data/dolly15k_qwen2_5_14b_kgw_gamma0.5_delta3_newtrain.parquet \
  --output data/dolly15k_qwen2_5_14b_kgw_gamma0.5_delta3_up_dipper_newtrain.parquet \
  --num-gpus 1
```

`--num-gpus 3` 自动按空闲显存选择 3 张卡，每卡一个完整 Dipper，动态领取回答；快卡会领取更多样本，最终按原始顺序输出。可改为其他卡数，省略默认自动选 1 张卡。`--batch-size` 默认 1 即可。

要手动选卡，可在命令前加 `CUDA_VISIBLE_DEVICES=1,2,3`，此时 `--num-gpus` 必须匹配指定卡数（省略则使用全部指定卡）。自动选卡估计每卡至少需 30000 MiB 空闲显存，FP32 至少 50000 MiB；不足所需卡数时会报错，不会悄悄减少卡数。

默认 `--dtype auto`：所有选中卡都支持 BF16 时统一用 BF16，否则统一 FP32。可显式指定精度，不会自动退回 FP32；每卡均需足够空闲显存加载完整模型。

默认每条累计最多尝试三次，失败时换采样 seed；仍失败就删除整条样本并继续，不写空回答。若进程中断，重新运行同一条命令会自动读取断点、跳过成功行。保留输出旁的 `.progress.jsonl` 和 `.audit.json`，后续训练需用审计文件核对删行记录。最终 Parquet 已存在时不会覆盖。

## 3. 两组训练

先完成改写，再依次运行；每组都是 Warmup 1 epoch + GAD 1 epoch。

```bash
# A：改写数据 Warmup + 改写数据 GAD
CUDA_VISIBLE_DEVICES=1,3 bash scripts/train/run_full_gad_up_up_optimized.sh \
  --exp_name kgw_up_dipper_up_1ep --nnodes 1

# B：改写数据 Warmup + 原 KGW 数据 GAD
CUDA_VISIBLE_DEVICES=1,3 bash scripts/train/run_full_gad_up_kgw_optimized.sh \
  --exp_name kgw_up_dipper_kgw_1ep --nnodes 1
```

训练命令加 `--dry_run` 可先检查配置与完整 UP 数据，不启动训练。学生为原始 Qwen2.5-0.5B，验证集均用原 KGW test；沿用现有 SwanLab 配置。

## 注意

- 先选择空闲 GPU，不停止他人任务。
- 改写默认 L60/O0、top_p=0.75，输入/输出上限均为 4096 token；跨硬件不保证逐位一致。
- 失败只停止本次启动的改写 worker，不停止其他任务。
- 单卡训练加 `--gpus_per_node 1`；中断后使用原实验名并加 `--resume`。已有 GAD 断点时自动跳过 Warmup；只有旧版已完成 Warmup、尚无 GAD 断点时，可再加 `--skip_warmup`。恢复时保持原 GPU 数量和训练配置；从头重跑使用新实验名。
- CPU 检查与模拟测试不代表真实 GPU 改写或训练已跑通。

详细参数、恢复与故障说明见 [UP_BASELINE.md](../UP_BASELINE.md)。

TP / WN 按顺序运行的命令见 [TP_WN_BASELINE.md](TP_WN_BASELINE.md)，测试生成入口在 `wm_test`。
