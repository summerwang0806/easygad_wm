# KGW 学生模型与基座模型：Dolly-15k 测试集评测

本实验使用 `data/dolly15k_test.parquet` 中的 500 条测试 prompt，分别让 KGW 训练后的学生模型和未训练的 Qwen2.5-0.5B 基座模型生成回答。

推理时不会额外施加 KGW 水印。脚本检测的是学生模型是否从 KGW 训练数据中学到了水印信号。两个模型使用相同的 prompt、采样参数和逐条随机种子。

水印检测默认使用教师 `/shared/public_models/Qwen2.5-14B-Instruct` 的 tokenizer 编码实际 prompt 和回答；生成时的学生 tokenizer、聊天模板和截断方式保持原样。原运行命令、输出字段和已有 JSONL 的评估流程不变。

## 运行方法

在 EasyGAD 根目录激活 `wm` 环境后运行：

```bash
cd /shared/wwx/EasyGAD
conda activate wm
VLLM_USE_V1=0 CUDA_VISIBLE_DEVICES=3 python wm_test/generate_compare_score.py \
  --gamma 0.5 --delta 3


VLLM_USE_V1=0 CUDA_VISIBLE_DEVICES=2 python wm_test/generate_compare_score.py \
  --gamma 0.5 --delta 2


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



CUDA_VISIBLE_DEVICES=2 python wm_test/evaluate_compare_metrics.py


```

默认读取上面的学生模型与基座模型 JSONL，并将每次结果追加到 `wm_test/detection_metrics_history.md`，不会覆盖之前记录。脚本会检查两边样本 ID 是否一致、标签是否正确，再根据 `z_score`（分数越高越像带水印）计算：

- AUROC；
- 全部经验阈值中使 F1 最大的 best F1，并报告对应阈值、TPR、FPR；
- `TPR@FPR=1%/5%/10%`，并报告各工作点的实际 FPR、TPR、F1 和 z-score 阈值。脚本只选择实际 FPR 不超过目标值的经验阈值；分数相同的样本作为一个阈值组，因此实际 FPR 可能略低于目标值。

这里的 best F1 和目标 FPR 工作点是在这 500 对测试样本上直接选择阈值的描述性结果；若要报告泛化性能，应另留校准集选阈值，再在独立测试集上评估。脚本也可用 `--kgw-file`、`--clean-file` 和 `--output` 指定自定义文件。

## 默认同时评测已保存回答的 PPL

`evaluate_compare_metrics.py` 默认在同一次评估中，给当前 `DEFAULT_KGW` 和
`DEFAULT_CLEAN` 指定的完整回答分别计算参考模型 PPL。无需每次添加 PPL 参数，
在项目根目录直接运行：

```bash
python wm_test/evaluate_compare_metrics.py
```

PPL 固定配置集中在 `evaluate_compare_metrics.py` 顶部，按需要编辑即可；更换待测文本
仍然修改原有的 `DEFAULT_KGW`、`DEFAULT_CLEAN`，PPL 与水印检测使用同一批 JSONL。

| 顶部配置 | 默认值 | 用途 |
|---|---|---|
| `DEFAULT_PPL_ENABLED` | `True` | 默认启用 PPL |
| `DEFAULT_PPL_MODEL` | `/shared/public_models/Llama-3-8B` | 固定 Base 评分模型及其 tokenizer |
| `DEFAULT_PPL_GENERATION_TOKENIZER` | `/shared/public_models/Qwen2.5-0.5B` | 恢复原生成时的消息模板与截断 |
| `DEFAULT_PPL_DEVICE` | `cuda` | 评分设备 |
| `DEFAULT_PPL_DTYPE` | `bfloat16` | 评分精度 |
| `DEFAULT_PPL_MAX_LENGTH` | `None` | 使用参考模型配置的上下文窗口 |
| `DEFAULT_PPL_OVERFLOW` | `error` | 超出参考上下文窗口时报错 |

仍可用 CLI 参数临时覆盖顶部配置。只想运行原有水印和 ROUGE 评估时：

```bash
python wm_test/evaluate_compare_metrics.py --no-ppl
```

若顶部关闭了 PPL，可用 `--ppl` 临时打开。评分不加载学生权重、不重新生成回答，
不向评分概率施加 KGW 或 WN 偏置。使用服务器现有的 `torch` 和 `transformers` 环境，
所有模型及 tokenizer 都只从本地目录读取。CPU 调试可将顶部设备和精度改为
`cpu`、`float32`，或临时传 `--ppl-device cpu --ppl-dtype float32`。
评分期间显示逐文件进度、速度与预计剩余时间，缓存命中时会明确提示复用结果。

PPL 的输入字段是 `id`、`prompt`、`answer` 和 `generation`。每条消息列表先按
**原生成 tokenizer 的 chat template** 恢复当时实际使用的提示，再复现
`generation.max_prompt_tokens` 的开头截取；旧记录缺少此字段时按原生成脚本的 2048
预算处理并记录。恢复出的提示文本由参考 tokenizer 重新编码，参考模型不额外套一层
chat template。仅回答 token 参与损失，不计 prompt、BOS 或 padding，也不额外添加
EOS 计分。不同回答之间不拼接。该协议固定后，所有实验组都用同一参考模型和格式评分。

默认用顶部固定的 Qwen2.5-0.5B tokenizer 恢复原生成提示（不加载该学生的模型权重），
前提是训练 checkpoint 保留了同一模板。这个目录的 tokenizer 和聊天模板必须与实际
生成时一致，不能直接换成评分模型的 tokenizer。
旧的 `generate_compare_score.py` 会让 student 和 base 共用 student tokenizer，
但 base 记录只保存 base 的权重路径，所以单凭 base 的 `model_path` 无法证明原模板。
若 checkpoint 改过模板，应修改顶部 `DEFAULT_PPL_GENERATION_TOKENIZER`，或临时传
`--ppl-generation-tokenizer /原生成tokenizer目录`。仅当顶部将该项设为 `None` 且没有
CLI 覆盖时，才从每条记录的 `model_path` 推定 tokenizer；报告会注明这种推定的限制。
`--tokenizer` 仍是原有水印检测 tokenizer 参数，与 PPL 的两个 tokenizer 角色不同。

默认使用参考模型配置的上下文窗口。修改顶部 `DEFAULT_PPL_MAX_LENGTH` 或使用
`--ppl-max-length` 可指定更小的评分窗口；超过窗口默认报错，避免静默改变评测文本。
只有将顶部 `DEFAULT_PPL_OVERFLOW` 改为 `truncate_prompt`，或显式使用
`--ppl-overflow truncate_prompt` 时，才从提示左侧移除上下文，保留完整回答和至少一个上下文
token；若回答本身无法完整评分仍会报错。空回答记为跳过，不按 PPL=0 或 1 加入汇总。

每个输入文件会得到独立、带配置指纹的 `*.ppl.*.jsonl` 逐条明细，包含 NLL、
参考 tokenizer 计分 token 数、逐条 PPL 与实际截断情况。重复评估同样的输入和评分配置
可复用有效缓存；输入内容、模型/tokenizer 指纹或评分配置改变后不会混用旧结果。
原始 JSONL 与水印检测缓存保持原样。

每次 evaluate 仍然在 `--output` 指定的 Markdown 结果文档末尾追加记录，默认是
`wm_test/detection_metrics_history.md`。启用 PPL 后，该次记录还会包含：

- 评分模型、tokenizer、设备、精度及上下文处理协议；
- 测试 JSONL 的路径和 SHA256、学生模型来源、样本 ID 与生成设置的追溯信息；
- 学生与 clean 两组的总体 PPL、有效/跳过样本数、平均回答长度、总计分 token 数；
- 逐条明细路径及缓存是否复用。

总体 PPL 为 `exp(所有有效回答的 NLL 总和 / 回答计分 token 总数)`，
不是逐条 PPL 的算术平均。它使用完整原始回答，不使用水印统计中的重复过滤或 token 对
去重。PPL 只支持参考模型下的语言流畅性比较，不能替代下游能力或事实正确性评测；
不同参考模型/tokenizer 的绝对 PPL 应分开报告。

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
  --tokenizer /shared/public_models/Qwen2.5-14B-Instruct
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

正式运行自动显示 WN 总进度条：已生成并完成 KGW 评分的回答数、百分比、耗时、平均速度和预计剩余时间，并标明 `generate`（生成）、`score`（评分）、`saving`（保存）阶段。在交互终端中，每批生成还显示 vLLM 自带进度条，可查看当前批次的生成进展。模型加载先显示提示，加载完成后才开始统计生成进度；最终文件成功保存后显示 `[WN done]` 和 `Saved ...`。重定向到日志时改用逐行进度记录；`--preflight` 仅执行检查，不显示生成进度。无需添加参数或安装新依赖。

完整 prompt 默认预算为 2048 token。长度校验现在先扫描所有选中的样本，再一次报告超限数量、`maximum_prompt_tokens` 和最长的五条样本，避免逐条增加预算后反复失败。根据报告显式设置 `--max-prompt-tokens`，先预检再正式生成；检查整个测试集时不要加 `--limit`。prompt 保留完整文本，输出上限仍由 `--max-new-tokens` 控制，vLLM 的上下文窗口按两项预算之和配置。WN 开关对照应使用相同的 prompt 预算和采样参数。

2026-10-16 全量核对本地 `data/dolly15k_qwen2_5_14b_kgw_gamma0.5_delta3_newtest.parquet`：500 条样本的最大完整 prompt 为 5148 token（`dolly-13445`），3 条超过 2048，1 条超过 4096。使用与窃取规则匹配的 Qwen 分词后端和 chat template，`--max-prompt-tokens 6144` 可通过这份数据的全部长度检查；WN 开关对照均应使用该预算。

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

## 2026-10-19：剔除严重重复回答后的固定 token 分组 p-value

`evaluate_compare_metrics.py` 现在默认追加一套质量筛选后的分组结果，无需新增参数。原有 AUROC、TPR、逐回答 p-value（含 token 对去重版本）和未筛选的分组 p-value 均保留。这套新结果是质量筛选补充指标，不是 Pan 原论文的去重协议，也不是对每个分组的 token 对去重。

筛选和统计顺序如下：

1. 用教师 tokenizer 单独编码每条回答，不含 prompt；计算回答内部相邻 token 对重复率 `1 - 不同 token 对数量 / 全部 token 对数量`。重复率严格大于 50% 时，剔除整条回答；恰好 50% 保留。少于两个 token 的回答重复率记为 0。
2. KGW 和 clean 各自独立按相同标准筛选，保留剩余回答的原始顺序，将各回答 token ID 无分隔拼接。
3. 分别切成不重叠的 1K、2K、3K、10K、20K、30K 原始 token 块；每块首 token 只提供上下文，其余 token 计分，最后不足一块的尾部丢弃。保留块内重复 token 对的正常计数。
4. 每个预算报告各块 p-value 的普通中位数；偶数组取中间两个 p-value 的算术平均。完整块不足一组时报告 `N/A`。

终端和追加的 `wm_test/detection_metrics_history.md`（含该次记录内的 JSON）会同时记录各组 p-value 中位数、有效分组数、尾部丢弃 token 数，以及 KGW/clean 各自的原始回答数、剔除数、保留数和移除 token 数。比较方法时应同时报告剔除比例，不能只比较筛选后的 p-value；原有文本质量指标仍使用完整测试集。

新缓存独立保存为输入文件旁的 `*.nonrepetitive_grouped_p_values.json`，不覆盖原始 JSONL、逐回答缓存或 `*.grouped_p_values.json`。缓存包含筛选统计及逐回答筛选明细；源文件、检测配置或教师 tokenizer 等不匹配时会重算。首次精确评分需要 CUDA 和教师 tokenizer，不加载模型权重，也不重新生成回答；全部所需缓存有效后可直接复用，无需 CUDA。

服务器同步以下三个文件后，在项目根目录激活原评估环境并运行：

```text
wm_test/evaluate_compare_metrics.py
wm_test/grouped_pvalues.py
wm_test/nonrepetitive_grouped_pvalues.py
```

```bash
conda activate wm

CUDA_VISIBLE_DEVICES=1 python wm_test/evaluate_compare_metrics.py \
  --kgw-file wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new.jsonl

CUDA_VISIBLE_DEVICES=1 python wm_test/evaluate_compare_metrics.py \
  --kgw-file wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new_strength3.jsonl
```

两条命令分别对应 WN strength=2.5 和 3，继续使用既有的默认 clean 文件 `wm_test/base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl`、Dolly 参考和 clean 教师参考；需要更换时仍用原有 `--clean-file`、`--dolly-reference-file`、`--teacher-clean-reference-file` 参数。选择当前空闲的 GPU；教师 tokenizer 路径不同则显式传 `--tokenizer`。
