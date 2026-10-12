# Dolly-15k 教师数据生成

本目录只做一件事：使用 Qwen2.5-14B-Instruct 为 Dolly-15k 生成无水印或 KGW
水印回答，同时保存每条回答的 KGW z-score。

## 1. 准备 Dolly-15k

原始数据已经下载到：

```text
wm_data/raw/databricks-dolly-15k
```

重新构建基础数据时运行：

```bash
python wm_data/prepare_dolly.py --overwrite
```

得到：

```text
data/dolly15k_train.parquet    # 14,511条
data/dolly15k_test.parquet     # 500条
```

`content` 使用 Dolly 的 `instruction` 和可选 `context` 构建。教师生成只替换
`teacher_response`，不会修改 prompt、ID或其他字段。

## 2. 生成无水印数据

单卡：

```bash
CUDA_VISIBLE_DEVICES=0 python wm_data/generate_clean.py \
  --input data/dolly15k_train.parquet \
  --output data/dolly15k_qwen2_5_14b_clean_train.parquet



```

多卡只增加 `--num-gpus`。例如使用0、1、2号三张卡：

```bash
CUDA_VISIBLE_DEVICES=0,1,2 python wm_data/generate_clean.py \
  --input data/dolly15k_train.parquet \
  --output data/dolly15k_qwen2_5_14b_clean_train.parquet \
  --num-gpus 3

CUDA_VISIBLE_DEVICES=2,3 python wm_data/generate_clean.py \
  --input data/dolly15k_test.parquet \
  --output data/dolly15k_qwen2_5_0.5b_clean_test.parquet \
  --num-gpus 2
```

## 3. 生成 KGW 水印数据

单卡：

```bash
# 教师模型的指令 
CUDA_VISIBLE_DEVICES=0 python wm_data/generate_kgw.py \
  --input data/dolly15k_train.parquet \
  --output data/dolly15k_qwen2_5_14b_kgw_train.parquet \
  --gamma 0.25 \
  --delta 2.0 \
  --hash-key 15485863

# 学生模型直接KGW的指令
CUDA_VISIBLE_DEVICES=2 python wm_data/generate_kgw.py \
  --input data/dolly15k_test.parquet \
  --output data/dolly15k_qwen2_5_0.5b_kgw_test.parquet \
  --gamma 0.5 \
  --delta 3.0 \
  --hash-key 15485863


```

0、1、2号三张卡：

```bash
CUDA_VISIBLE_DEVICES=0,1,2 python wm_data/generate_kgw.py \
  --input data/dolly15k_train.parquet \
  --output data/dolly15k_qwen2_5_14b_kgw_train.parquet \
  --num-gpus 3 \
  --gamma 0.25 \
  --delta 2.0 \
  --hash-key 15485863

CUDA_VISIBLE_DEVICES=0,1,2 python wm_data/generate_kgw.py \
  --input data/dolly15k_test.parquet \
  --output data/dolly15k_qwen2_5_0.5b_kgw_test.parquet \
  --num-gpus 3 \
  --gamma 0.25 \
  --delta 2.0 \
  --hash-key 15485863


CUDA_VISIBLE_DEVICES=0,1 python wm_data/generate_kgw.py \
  --input data/dolly15k_test.parquet \
  --output data/dolly15k_qwen2_5_14b_kgw_gamma0.5_delta2_test.parquet \
  --num-gpus 2 \
  --gamma 0.5 \
  --delta 2.0 \
  --hash-key 15485863


```

`CUDA_VISIBLE_DEVICES` 用于指定允许使用的物理卡，`--num-gpus` 表示实际并行数量，
两者数量应保持一致。如果不写 `CUDA_VISIBLE_DEVICES`，程序会根据实时空闲显存
自动选择能够放下模型的 GPU。程序按各卡可用能力切分数据，在内部完成并行生成、
逐条检测和顺序合并。单卡与多卡的最终文件格式完全相同。

模型加载前会检查 GPU 是否存在、可见卡数量和实时空闲显存。如果没有可用卡、
`--num-gpus` 请求的卡数不足，或者某张卡放不下模型，程序会立即报错并提示对应
GPU的空闲显存和预计需求；此时不会加载模型、删除旧输出或启动部分 worker。

模型加载完成后，终端会显示两个总体进度条：

```text
Generating responses: 生成回答的完成数量和速度
Scoring responses:    计算 KGW z-score 的完成数量和速度
```

单卡时进度会按 batch 更新；多卡时主进程会汇总所有 GPU worker 的进度。检测通常
紧跟在每个生成分片之后，因此两个进度条可能交替前进。断点续跑时，已经完成的分片
也会自动计入进度。

## 4. 最终输出

每条生成命令最终只保留两个文件。例如无水印训练集：

```text
data/dolly15k_qwen2_5_14b_clean_train.parquet
data/dolly15k_qwen2_5_14b_clean_train_kgw_scores.jsonl
```

第一个文件用于 GAD 和 SFT，严格保持七列：

```text
id, content, teacher_response, category, grounded, flaw, agreement
```

第二个文件是便于直接查看的 JSONL，用于水印检测和 AUROC。每行对应一条生成
回答，并通过 `id` 与训练 parquet 一一对应：

```text
id, label, is_watermarked, num_tokens, green_tokens, green_fraction, z_score
```

示例：

```json
{"id":"dolly-13384","label":"kgw","is_watermarked":true,"num_tokens":120,"green_tokens":46,"green_fraction":0.38333333333333336,"z_score":3.3730961708462712}
```

可以直接查看前几条：

```bash
head -n 5 data/dolly15k_qwen2_5_14b_kgw_train_kgw_scores.jsonl
```

后续计算 AUROC 时使用：

```text
真实标签：is_watermarked
预测分数：z_score
```

生成和检测在同一次生成任务中使用完全相同的 tokenizer、prompt、`gamma`、
`hash-key` 和 CUDA RNG，不需要再运行其他检测命令。

## 5. 中断恢复和临时文件

运行期间只使用一个临时目录：

```text
<输出文件>.parts/
```

任务中断后，使用完全相同的命令即可继续。最终 parquet 和 JSONL 成功写入后，临时目录
会自动删除。如果需要保留分片用于排查问题，可增加 `--keep-parts`。

已有最终输出时，程序不会覆盖；确认需要从头生成时增加：

```text
--overwrite
```

## 6. 常用参数

- `--num-gpus`：并行使用的 GPU 数量，默认1。
- `--batch-size`：每个 GPU 的请求批大小，默认8。
- `--shard-size`：断点分片大小，默认256，必须能被 batch size整除。
- `--max-prompt-tokens`：输入 prompt 最大长度，默认2048。
- `--max-new-tokens`：每条回答最大生成长度，默认1536。
- `--limit`：只处理前N条，仅用于单卡小规模测试；正式生成时不要设置。
- `--gpu-memory-utilization`：每个 worker 允许使用的显存比例上限，默认0.85。

正式比较 clean 与 KGW 时，两次生成应使用相同的采样参数、`seed`、`gamma` 和
`hash-key`。正式秘密水印实验不要公开真实使用的 `hash-key`。

## 7. 计算 KGW 检测指标

训练集和测试集的 clean、KGW 数据都生成完成后运行：

```bash
python wm_data/evaluate_kgw_scores.py
```

程序读取四个默认的 `_kgw_scores.jsonl` 文件，分别计算：

- `kgw_train` 对 `clean_train`
- `kgw_test` 对 `clean_test`

输出 AUROC、TPR@FPR=1%/5%/10%、固定阈值 F1、best F1 及其阈值。固定 F1 默认
使用 `z_score >= 4.0`，可通过 `--f1-threshold` 修改。完整指标会追加保存到：

```text
wm_data/kgw_detection_results.md
```

结果文件不会被覆盖。每次运行都会在末尾新增一个带时间戳的实验记录，包括输入文件、
汇总指标、各 FPR 工作点、F1 详细指标和混淆矩阵。

例如将固定 F1 阈值改为3：

```bash
python wm_data/evaluate_kgw_scores.py --f1-threshold 3.0
```
