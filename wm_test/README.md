# KGW 学生模型与基座模型：Dolly-15k 测试集评测

本实验使用 `data/dolly15k_test.parquet` 中的 500 条测试 prompt，分别让 KGW 训练后的学生模型和未训练的 Qwen2.5-1.5B-Instruct 基座模型生成回答。

推理时不会额外施加 KGW 水印。脚本检测的是学生模型是否从 KGW 训练数据中学到了水印信号。两个模型使用相同的 prompt、采样参数和逐条随机种子。

## 运行方法

在 EasyGAD 根目录激活 `wm` 环境后运行：

```bash
cd /shared/wwx/EasyGAD
conda activate wm
VLLM_USE_V1=0 CUDA_VISIBLE_DEVICES=2 python wm_test/generate_compare_score.py
```

脚本默认处理测试集全部 500 条数据。可通过 `CUDA_VISIBLE_DEVICES` 指定一张空闲 GPU。

脚本使用的 vLLM 0.8.5 在本环境中需关闭 V1 引擎。未设置 `VLLM_USE_V1=0` 时，V1 的子进程可能因 CUDA `fork` 初始化冲突而启动失败；这与选择哪张 GPU 无关。此设置与 `wm_data` 的兼容处理一致。

## 输出文件

运行后生成两个 JSONL 文件，每行对应一条测试 prompt：

```text
wm_test/kgw_student_dolly15k_test.jsonl
wm_test/base_qwen2_5_1_5b_dolly15k_test.jsonl
```

两个文件分开保存，不会把两个模型的结果合并。学生模型文件中 `label` 为 `kgw`、
`is_watermarked` 为 `true`；基座模型文件中 `label` 为 `clean`、`is_watermarked` 为
`false`，可直接按标签统计水印存活率和基座误报率。

每条记录包含样本 ID、原始对话 prompt、模型回答、回答 token 数、绿名单 token 数及比例、KGW z-score，以及生成和检测参数。检测只对回答打分，不把 prompt 本身计入回答分数；第一个回答 token 的 KGW 上下文使用 prompt 的最后一个 token。

## 小规模试跑

先用前 8 条检查流程：

```bash
VLLM_USE_V1=2 CUDA_VISIBLE_DEVICES=2 python wm_test/generate_compare_score.py --limit 8 \
  --student-output wm_test/kgw_student_smoke.jsonl \
  --base-output wm_test/base_smoke.jsonl
```

如果目标输出文件已经存在，脚本会停止以避免覆盖。确认需要重新生成时加上 `--overwrite`。

## 两个 JSONL 的水印检测指标

两份生成结果完成后，在 EasyGAD 根目录运行：

```bash
conda activate wm
python wm_test/evaluate_compare_metrics.py
```

默认读取上面的学生模型与基座模型 JSONL，并将每次结果追加到 `wm_test/detection_metrics_history.md`，不会覆盖之前记录。脚本会检查两边样本 ID 是否一致、标签是否正确，再根据 `z_score`（分数越高越像带水印）计算：

- AUROC；
- 全部经验阈值中使 F1 最大的 best F1，并报告对应阈值、TPR、FPR；
- `TPR@FPR=1%/5%/10%`，并报告各工作点的实际 FPR、TPR、F1 和 z-score 阈值。脚本只选择实际 FPR 不超过目标值的经验阈值；分数相同的样本作为一个阈值组，因此实际 FPR 可能略低于目标值。

这里的 best F1 和目标 FPR 工作点是在这 500 对测试样本上直接选择阈值的描述性结果；若要报告泛化性能，应另留校准集选阈值，再在独立测试集上评估。脚本也可用 `--kgw-file`、`--clean-file` 和 `--output` 指定自定义文件。

## KGW 参数

默认参数与 `wm_data/kgw.py` 和 `wm_data/generate_teacher_data.py` 一致：

```text
gamma = 0.25
delta = 2.0
hash_key = 15485863
seeding = simple_1：根据前一个 token 的 ID 和 hash_key 生成绿名单
```

项目现有的固定检测阈值是 `z_score >= 4.0)。可用学生模型中达到阈值的回答数除以 500 计算水印存活率；同时查看基座模型达到阈值的比例，作为误报对照。建议也保留并比较原始 z-score，而不只报告阈值后的比例。
