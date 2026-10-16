# TP / WN 运行步骤

在项目根目录、已配置好的 GAD 环境中依次运行。模型路径和 GPU 编号按实际修改。

```bash
MODEL=models/Qwen2.5-0.5B
TRAIN=data/dolly15k_qwen2_5_14b_kgw_train.parquet
TEST=data/dolly15k_qwen2_5_14b_kgw_test.parquet
RULES=data/acl_estimated_rules.json
TP_DATA=data/dolly15k_qwen2_5_14b_kgw_tp_student_train.parquet
```

## 1. 原始水印数据跑完整 GAD，得到 W

Warmup 和 GAD 均用原始水印数据，默认各 1 epoch。

```bash
CUDA_VISIBLE_DEVICES=1,3 bash scripts/train/run_full_gad_all_clean_optimized.sh \
  --model "$MODEL" --exp_name kgw_reference --nnodes 1 \
  --warmup_train_file "$TRAIN" --gad_train_file "$TRAIN" \
  --warmup_val_file "$TEST" --gad_val_file "$TEST"
```

训练结束后，将 `NNN` 换成已保存完整的 GAD checkpoint 步数，合并 actor：

```bash
W_CKPT=checkpoints/kgw_reference/gad/global_step_NNN/actor
CUDA_VISIBLE_DEVICES="" python scripts/model_merger.py merge --backend fsdp \
  --local_dir "$W_CKPT" --target_dir "$W_CKPT/huggingface"
W="$W_CKPT/huggingface"
```

已有水印 GAD 模型可跳过本步，直接将 `W` 设置为合并后的模型目录。

这里的 `MODEL` 始终指 Warmup 之前的原始学生 O；`W` 指完整 GAD 训练后的 actor，且训练中未使用 UP/TP 改写数据。`TRAIN` 需对应这个 W 的原始水印训练集，也支持 `*_newtrain.parquet` 文件名。

## 2. 窃取规则，TP / WN 共用

```bash
CUDA_VISIBLE_DEVICES=1 python baseline_acl/steal_watermark.py \
  --input "$TRAIN" --model-before "$MODEL" --model-after "$W" \
  --output "$RULES" --device cuda
```

## 3. TP：转述 → 全程 GAD → 正常生成

使用原始学生 O 转述，输出新的训练数据：

```bash
CUDA_VISIBLE_DEVICES=1,2 python baseline_acl/paraphrase_tp.py \
  --input "$TRAIN" --output "$TP_DATA" --rules "$RULES" \
  --model "$MODEL" --num-gpus 2 --inverse-strength 2.5
```

重新从原始学生 O 开始，Warmup 和 GAD 均使用 TP 数据：

```bash
CUDA_VISIBLE_DEVICES=1,3 bash scripts/train/run_full_gad_tp_tp_optimized.sh \
  --model "$MODEL" --exp_name kgw_tp_student_tp_1ep \
  --kgw_train_file "$TRAIN" --tp_train_file "$TP_DATA" --val_file "$TEST"
```

训练结束后，替换 `NNN`，合并 TP 学生并正常生成测试回答：

```bash
TP_CKPT=checkpoints/kgw_tp_student_tp_1ep/gad/global_step_NNN/actor
CUDA_VISIBLE_DEVICES="" python scripts/model_merger.py merge --backend fsdp \
  --local_dir "$TP_CKPT" --target_dir "$TP_CKPT/huggingface"
VLLM_USE_V1=0 CUDA_VISIBLE_DEVICES=1 python wm_test/generate_compare_score.py \
  --input "$TEST" --student-model "$TP_CKPT/huggingface" --base-model "$MODEL" \
  --student-output wm_test/student_tp.jsonl --base-output wm_test/base_for_tp.jsonl
```

## 4. WN：用 W 生成时施加反向偏置

复用第 1 步的 W 和第 2 步的规则，生成入口统一放在 `wm_test`：

```bash
CUDA_VISIBLE_DEVICES=1 VLLM_USE_V1=0 python wm_test/generate_wn_score.py \
  --student-model "$W" --rules "$RULES" --input "$TEST" \
  --output wm_test/student_wn.jsonl --strength 2.5
```

无偏置对照：同一命令改为 `--strength 0 --output wm_test/student_wn_off.jsonl`。

## 常用操作

- 窃取、TP 转述、WN 生成的命令加 `--preflight` 可先做 CPU 预检；TP 训练命令加 `--dry_run`。
- TP 转述中断后，在原命令加 `--resume`；保留输出对应的 `.progress.jsonl` 和 `.audit.json`。
- 规则、TP 数据和生成结果重跑时使用新的输出文件名；训练重跑使用新的实验名。
- 检测参数默认为 KGW `gamma=0.25, delta=2.0`；其它设置在 WN 加 `--gamma/--kgw-delta`，TP 正常生成加 `--gamma/--delta`。

混合 TP→KGW 分支、旧 Dipper 备用命令和实现细节见 [TP_WN_DETAILS.md](TP_WN_DETAILS.md)；结果评估见 [wm_test/README.md](../wm_test/README.md)。
