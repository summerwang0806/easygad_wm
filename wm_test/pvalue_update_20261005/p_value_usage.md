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
若旧 checkpoint tokenizer 已移除，可加 `--tokenizer /shared/public_models/Qwen2.5-0.5B`，
必须与采样时使用的 tokenizer 相同。重算原始 z 分数与保存值不一致时会停止，避免生成错误的去重结果。
缓存按源文件 SHA256 和检测版本核对，采样文件变化后自动重算。

这里是每条回答的单侧正态近似 p-value：`0.5 * erfc(z / sqrt(2))`，不是 AUROC 的检验 p 值，
也不是文本质量分数。去重按相同 `(previous_token_id, token_id)` 只计一次，不修改回答文本。
空回答 p=null，不纳入有效样本统计。去重可减少重复导致的失真，但仍需查看 clean 的实测误报率，
不能把 p≤0.05 自动理解为实际 FPR=5%。不同长度、文本结构及固定密钥可能影响校准。
