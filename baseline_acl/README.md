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
CUDA_VISIBLE_DEVICES=1,2 python baseline_acl/paraphrase_up.py \
  --input data/dolly15k_qwen2_5_14b_kgw_train.parquet \
  --output data/dolly15k_qwen2_5_14b_kgw_up_dipper_train.parquet \
  --num-gpus 2
```

GPU 编号只写在 `CUDA_VISIBLE_DEVICES`；`--num-gpus` 可省略，显式值须与可见卡数一致。每卡一个完整 Dipper，动态领取整条回答，不切分模型；`--batch-size` 不是 GPU 数，默认 1 即可。

默认 `--dtype auto`：所有选中卡都支持 BF16 时统一用 BF16，否则统一 FP32。可显式指定精度，不会自动退回 FP32；每卡均需足够空闲显存加载完整模型。

父进程统一写有序 Parquet、进度 JSONL 和审计 JSON。中断加 `--resume`，可改变卡数，但精度和改写参数须匹配；兼容匹配的 v3 整条断点，不兼容旧三句断点。改写后需抽查。

若报空输出或尝试次数耗尽，保留原断点，用下面命令续跑。成功行不重做，失败行换采样 seed 重试；`3` 是每条累计最多三次，后续续跑也带这两个参数。

```bash
CUDA_VISIBLE_DEVICES=1,2 python baseline_acl/paraphrase_up.py \
  --input data/dolly15k_qwen2_5_14b_kgw_train.parquet \
  --output data/dolly15k_qwen2_5_14b_kgw_up_dipper_train.parquet \
  --num-gpus 2 --resume --max-attempts 3
```

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
- 改写默认 L60/O0、top_p=0.75，输入/输出上限均为 4096 token；跨硬件不保证逐位一致。
- 失败只停止本次启动的改写 worker，不停止其他任务。
- 单卡训练加 `--gpus_per_node 1`；重跑使用新实验名。
- CPU 检查与模拟测试不代表真实 GPU 改写或训练已跑通。

详细参数、恢复与故障说明见 [UP_BASELINE.md](../UP_BASELINE.md)。

TP / WN 按顺序运行的命令见 [TP_WN_BASELINE.md](TP_WN_BASELINE.md)，测试生成入口在 `wm_test`。
