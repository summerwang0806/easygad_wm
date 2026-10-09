# Dipper-UP 基线

用 Dipper 改写 KGW 教师训练回答，再跑两组蒸馏实验。每条回答全部句子一次改写，只替换 `teacher_response`，不改问题和 test 数据。

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

## 2. 改写训练集

```bash
CUDA_VISIBLE_DEVICES=1 python baseline_acl/paraphrase_up.py \
  --input data/dolly15k_qwen2_5_14b_kgw_train.parquet \
  --output data/dolly15k_qwen2_5_14b_kgw_up_dipper_train.parquet \
  --dtype float32
```

默认：lexical/order=60/0，top_p=0.75，输入/输出上限均为 4096 token。

输出为改写 Parquet、进度 JSONL 和审计 JSON。中断后同一命令加 `--resume`；不能续用旧三句版本断点。改写可能合并句子或遗漏信息，生成后需抽查。

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

- 先确认 GPU 可用，不用 0 号卡，不停止他人任务。
- 40GB 卡改写需显式使用 `--dtype bfloat16`，仍需足够空闲显存。
- 单卡训练加 `--gpus_per_node 1`；重跑使用新实验名。
- 37 项 CPU 测试和全量输入预检已通过，不代表真实 GPU 改写已跑通。

详细参数、恢复与故障说明见 [UP_BASELINE.md](../UP_BASELINE.md)。
