# 两种 KGW p-value

继续按原流程运行 `generate_compare_score.py`，再运行 `evaluate_compare_metrics.py`。
生成脚本保存原始检测分数和相邻 token 对去重分数；评估脚本保留原 AUROC/F1/TPR@FPR，
并在 `wm_test/detection_metrics_history.md` 追加 KGW、clean 两组的两种 p-value 统计。

```bash
cd /shared/wwx/EasyGAD
conda activate wm
python wm_test/evaluate_compare_metrics.py \
  --kgw-file wm_test/你的模型采样.jsonl \
  --clean-file wm_test/base_qwen2_5_0_5b_dolly15k_test.jsonl
```

每条文本的结果保存在输入文件旁的 `<文件名>.p_values.jsonl`，字段包括
`p_value_raw`、`p_value_dedup`、两种 z 分数、两种有效 token 数量。
不修改原采样文件。统计包括均值、中位数、最小/最大值，以及 p≤0.01、0.05、0.10 的数量和比例；
后者对 clean 是实测误报率，对 KGW 是理论阈值下的检出率。

旧 JSONL 没有去重分数时，第一次评估需使用一张可用 GPU 重现原 CUDA 随机数算法，
只加载 tokenizer，不加载或运行语言模型：

```bash
CUDA_VISIBLE_DEVICES=3 python wm_test/evaluate_compare_metrics.py \
  --kgw-file wm_test/你的旧模型采样.jsonl \
  --clean-file wm_test/base_qwen2_5_0_5b_dolly15k_test.jsonl
```

GPU 3 只是示例，运行前按当前资源情况选择。后续相同文件直接使用缓存，无需 GPU。
检测默认使用教师 `/shared/public_models/Qwen2.5-14B-Instruct` 的 tokenizer，原命令、输出字段和旧结果读取流程保持不变。
原 `--tokenizer` 参数仍可指定检测 tokenizer，必须与教师加水印时的 token 编码一致；旧对话 prompt 的模板和截断仍由记录中 `model_path` 的生成 tokenizer 还原。
重算原始 z 分数与保存值不一致时会停止，避免生成错误的去重结果。
缓存按源文件 SHA256 和检测版本核对，采样文件变化后自动重算。

这里是每条回答的单侧正态近似 p-value：`0.5 * erfc(z / sqrt(2))`，不是 AUROC 的检验 p 值，
也不是文本质量分数。去重按相同 `(previous_token_id, token_id)` 只计一次，不修改回答文本。
空回答 p=null，不纳入有效样本统计。去重可减少重复导致的失真，但仍需查看 clean 的实测误报率，
不能把 p≤0.05 自动理解为实际 FPR=5%。不同长度、文本结构及固定密钥可能影响校准。

## 固定 token 分组 p-value（普通中位数）

仍运行原来的 `python wm_test/evaluate_compare_metrics.py ...`，不用新增参数。
原有 AUROC、TPR、ROUGE-L 和逐回答 raw/dedup p-value 的计算保持原样，
在终端及 `--output` 指定的追加式 Markdown 报告中另增一张表：
**1000、2000、3000、10000、20000、30000 tokens** 六个预算，分别报告
KGW/clean 的完整组数、分组 p 普通中位数和丢弃尾部 token 数。

新增部分用教师 tokenizer 分别编码回答（不加特殊 token），无分隔拼接后精确切块，
末尾不足一块丢弃。每块的第一个 token 只作上下文，因此计分数为预算减 1；
保留重复及跨回答边界，使用本项目生成时的 simple_1 CUDA 绿表，
不替换成 Pan 的另一套 KGW 哈希实现。各组 p 升序后取普通中位数：
奇数组取中间一个值；偶数组取中间两个 p 的算术平均。这是 p 本身的中位数，
不是 z 分数或 log10(p) 的中位数，也不是逐回答 p 的均值。
分组流程参照 Pan，但汇总采用普通中位数，区别于其公开代码的上中位数。

首次计算需要可用 CUDA 和原教师 tokenizer，只加载 tokenizer、不加载语言模型：

```bash
CUDA_VISIBLE_DEVICES=3 python wm_test/evaluate_compare_metrics.py \
  --kgw-file wm_test/你的模型采样.jsonl \
  --clean-file wm_test/同检测配置的clean采样.jsonl \
  --tokenizer /shared/public_models/Qwen2.5-14B-Instruct \
  --score-device cuda
```

逐组详细结果另存 `<文件名>.grouped_p_values.json`，原回答及原 p-value 缓存不覆盖。
缓存按源文件 SHA256、教师 tokenizer 文件指纹、gamma/key/seeding 和版本核对；
后续相同输入可直接读缓存，无需 GPU。输入或 tokenizer 改变会重新计分。
有效的旧版上中位数缓存会用保存的逐组 p 自动转换为普通中位数并更新版本，
无需重新计分。终端、追加式 Markdown 及其中 JSON 都采用普通中位数，
JSON 标记 `aggregation: ordinary_median`；历史文档中已经写入的旧记录保留原样。
不足一组显示 N/A，不伪造为 0 或 1；极小 p 保留科学计数法和 log10(p)，避免下溢。
主表仍需与同一预算的 clean 结果一起解释；组数为 1–2 时应查看缓存中的逐组值。
