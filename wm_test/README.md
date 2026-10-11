# KGW 学生模型与基座模型：Dolly-15k 测试集评测

本实验使用 `data/dolly15k_test.parquet` 中的 500 条测试 prompt，分别让 KGW 训练后的学生模型和未训练的 Qwen2.5-0.5B 基座模型生成回答。

推理时不会额外施加 KGW 水印。脚本检测的是学生模型是否从 KGW 训练数据中学到了水印信号。两个模型使用相同的 prompt、采样参数和逐条随机种子。

## 运行方法

在 EasyGAD 根目录激活 `wm` 环境后运行：

```bash
cd /shared/wwx/EasyGAD
conda activate wm
VLLM_USE_V1=0 CUDA_VISIBLE_DEVICES=3 python wm_test/generate_compare_score.py \
  --gamma 0.5 --delta 3
```

脚本默认处理测试集全部 500 条数据。可通过 `CUDA_VISIBLE_DEVICES` 指定一张空闲 GPU。

`--gamma` 和 `--delta` 现在必须显式填写，匹配该模型训练数据的水印设置。旧的 gamma=0.25、delta=2 实验仍可传 `--gamma 0.25 --delta 2`。这些参数只用于检测及记录元数据，不会在学生采样时额外加水印。模型和输出路径可通过 `--student-model`、`--student-output`、`--base-output` 指定。

脚本使用的 vLLM 0.8.5 在本环境中需关闭 V1 引擎。未设置 `VLLM_USE_V1=0` 时，V1 的子进程可能因 CUDA `fork` 初始化冲突而启动失败；这与选择哪张 GPU 无关。此设置与 `wm_data` 的兼容处理一致。

## 输出文件

运行后生成两个 JSONL 文件，每行对应一条测试 prompt：

```text
wm_test/kgwwarmup_kgwgad_warmup_gamma0.5_delta3_qwen2_5_0_5b_dolly15k_test.jsonl
wm_test/base_qwen2_5_0_5b_dolly15k_test.jsonl
```

两个文件分开保存，不会把两个模型的结果合并。学生模型文件中 `label` 为 `kgw`、
`is_watermarked` 为 `true`；基座模型文件中 `label` 为 `clean`、`is_watermarked` 为
`false`，可直接按标签统计水印存活率和基座误报率。

每条记录包含样本 ID、原始对话 prompt、模型回答、回答 token 数、绿名单 token 数及比例、KGW z-score，以及生成和检测参数。检测只对回答打分，不把 prompt 本身计入回答分数；第一个回答 token 的 KGW 上下文使用 prompt 的最后一个 token。

## 小规模试跑

先用前 8 条检查流程：

```bash
VLLM_USE_V1=0 CUDA_VISIBLE_DEVICES=2 python wm_test/generate_compare_score.py --limit 8 \
  --gamma 0.5 --delta 3 \
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

生成脚本现在要求显式参数；当前 gamma=0.5、delta=3 的实验使用：

```text
gamma = 0.5
delta = 3.0
hash_key = 15485863
seeding = simple_1：根据前一个 token 的 ID 和 hash_key 生成绿名单
```

项目现有的固定检测阈值是 `z_score >= 4.0`。可用学生模型中达到阈值的回答数除以 500 计算水印存活率；同时查看基座模型达到阈值的比例，作为误报对照。建议也保留并比较原始 z-score，而不只报告阈值后的比例。

## 2026-10-11：纠正已有 gamma0.5 / delta3 结果的检测参数

本地拉取的两个新实验文件（warmup、GAD）各 500 条记录，实际都保存了 `kgw.gamma=0.25`、`kgw.delta=2`。记录的 `model_path` 指向正确的 gamma0.5/delta3 checkpoint，但生成打分脚本沿用了旧检测默认值。保存的 z 分数也逐条符合 gamma=0.25 的公式，并非只有元数据写错。此前报告的 GAD AUROC=0.652642、warmup AUROC=0.664956 都来自这些旧配置分数，不能当作 gamma=0.5 的正确检测结果。

`evaluate_compare_metrics.py` 使用输入中已保存的 z-score；它不会根据文件名自动重算。现在评估入口会校验同一文件内的检测配置、配置与保存分数是否一致，以及学生和 clean 的 gamma/hash key/seeding 是否一致，并在报告中展示实际配置。水印名称与保存元数据不符时也会停止，提示重新检测。delta 是生成 logits 偏置，不出现在检测 z 公式中，因此 delta 本身不同不会让正负两组 z 无法比较。

修改 gamma 会同时改变绿名单大小和 z 的零假设。必须重新判定每个 token 是否属于新的绿名单；不能直接修改 JSON 参数或沿用旧 `green_tokens`。无需重训，也无需重新生成回答。用户在服务器自行拉取新代码后，对原 GAD、warmup 和 base 回答一起重评分：

```bash
GAD_FILE=wm_test/kgwwarmup_kgwgad_gamma0.5_delta3_qwen2_5_0_5b_dolly15k_test.jsonl
WARMUP_FILE=wm_test/kgwwarmup_kgwgad_warmup_gamma0.5_delta3_qwen2_5_0_5b_dolly15k_test.jsonl
BASE_FILE=wm_test/base_qwen2_5_0_5b_dolly15k_test.jsonl

CUDA_VISIBLE_DEVICES=1 python wm_test/rescore_compare_scores.py \
  --inputs "$GAD_FILE" "$WARMUP_FILE" "$BASE_FILE" \
  --gamma 0.5 --delta 3 --hash-key 15485863 \
  --tokenizer /shared/public_models/Qwen2.5-0.5B
```

选择当前可用 GPU；示例只使用一张卡。脚本只加载本地 tokenizer，使用原 CUDA 随机数算法重新打分，不加载模型权重。CPU 与 CUDA 的随机数实现不同，不能用 CPU 结果替代本实验的 CUDA 绿名单。输出在原文件旁另存为 `*.rescored_gamma0.5_delta3_key15485863.jsonl`，保留回答、原配置和来源 SHA256；原文件不改。已有重评分输出默认拒绝覆盖，确认要替换时加 `--overwrite`。

然后分别评估两个阶段，clean 也使用重评分后的文件：

```bash
SCORE_SUFFIX=.rescored_gamma0.5_delta3_key15485863.jsonl
python wm_test/evaluate_compare_metrics.py \
  --kgw-file "${GAD_FILE%.jsonl}${SCORE_SUFFIX}" \
  --clean-file "${BASE_FILE%.jsonl}${SCORE_SUFFIX}"
python wm_test/evaluate_compare_metrics.py \
  --kgw-file "${WARMUP_FILE%.jsonl}${SCORE_SUFFIX}" \
  --clean-file "${BASE_FILE%.jsonl}${SCORE_SUFFIX}"
```

新分数对应新的源文件和 p-value 缓存，不会复用原 gamma=0.25 的分数。仅删除原 `.p_values.jsonl` 或重复运行原 evaluate 无法纠正参数。

另一个独立发现：GAD 回答重复严重，评分长度中位数为 1536，但不同相邻 token 对数量中位数只有 40；493/500 条的不同 token 对占比低于 10%。其原始 p≤0.01 比例为 58%，去重后仅 9%；Dolly ROUGE-L=0.017157。warmup 的 Dolly ROUGE-L=0.198672。纠正检测配置后仍须检查回答质量和去重信号，不能预先保证 AUROC 会提高。

本地没有 CUDA、PyTorch 和模型 tokenizer，无法直接得到修正后的真实指标；这里只核实了原分数及统计。实际 gamma=0.5 重评分由用户在服务器自行执行，不通过 SSH 连接服务器。

## WN 生成与检测

先按 [TP / WN 运行步骤](../baseline_acl/TP_WN_BASELINE.md) 得到参考学生 W 和规则，再从项目根目录运行。将 `NNN` 换成实际 checkpoint 步数，`W` 必须是已合并的模型目录。

WN 的检测设置也必须匹配模型训练水印。对新的 gamma=0.5、delta=3 模型，给 `generate_wn_score.py` 显式加 `--gamma 0.5 --kgw-delta 3`；其原有默认值仍用于旧 gamma=0.25、delta=2 实验。

```bash
W=checkpoints/kgw_reference/gad/global_step_NNN/actor/huggingface
RULES=data/acl_estimated_rules.json
TEST=data/dolly15k_qwen2_5_14b_kgw_test.parquet

# CPU 预检
python wm_test/generate_wn_score.py \
  --student-model "$W" --rules "$RULES" --input "$TEST" \
  --output wm_test/student_wn.jsonl --preflight

# 生成回答并计算 KGW 分数
VLLM_USE_V1=0 CUDA_VISIBLE_DEVICES=1 python wm_test/generate_wn_score.py \
  --student-model "$W" --rules "$RULES" --input "$TEST" \
  --output wm_test/student_wn.jsonl --strength 2.5
```

小规模试跑加 `--limit 8`；无偏置对照改为 `--strength 0 --output wm_test/student_wn_off.jsonl`。结果评估用下文的 `python wm_test/evaluate_compare_metrics.py`，设置 `--kgw-file wm_test/student_wn.jsonl` 和对应基座结果的 `--clean-file`。
