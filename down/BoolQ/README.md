# BoolQ：阅读理解 yes/no，自动计算 acc

只修改 `run_boolq.py` 顶部 `MODEL_PATH`，即可在项目根目录运行：

```bash
python -m pip install -r down/BoolQ/requirements.txt
python down/BoolQ/run_boolq.py --prepare-data
CUDA_VISIBLE_DEVICES=3 python down/BoolQ/run_boolq.py --check-only
CUDA_VISIBLE_DEVICES=3 python down/BoolQ/run_boolq.py --limit 8
CUDA_VISIBLE_DEVICES=3 python down/BoolQ/run_boolq.py
```

Python >= 3.10，使用已有 CUDA PyTorch。`MODEL_PATH` 支持服务器绝对路径和相对于项目根目录的路径；
默认学生为原来的 `te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_new/gad/global_step_1813/actor/huggingface`。
`TOKENIZER_PATH` 默认显式设置为服务器 `/shared/public_models/Qwen2.5-0.5B`；若导出目录已经完整，改为 `None`。
必须使用同一学生基座的 tokenizer，不能用教师 tokenizer。
也可进入 `down/BoolQ` 后执行 `python run_boolq.py`。

## 评分协议

- 固定 `lm-evaluation-harness==0.4.9.2` 的官方 `boolq` 任务，数据来源 `super_glue` / `boolq`。
- 使用有标签的 **validation，3270 题**。test 集没有公开标签，不用于此入口。
- 0-shot、原生 completion 提示，比较候选 `no`、`yes` 的条件对数似然；不让模型自由生成再匹配。
- 不使用 chat template、LLM judge 或付费 API，不需要 SQuAD 式答案抽取。
- 保存 `acc`（0–1）、`acc_percent`（0–100）、正确题数和 harness 标准误；越高越好。
- 同时按实际评测的题目计算多数类基线。BoolQ 标签不平衡，不能只与 50% 比较。
  全量结果的 baseline scope 为 `full_validation`；试跑为 `evaluated_subset`，不能当成全量基线。
- **本入口测 checkpoint 本身的概率，不启用推理时 WN processor。** 如果 WN 只改变解码、权重完全相同，
  本入口不会测出该处理器的影响；结果中的 `watermark_at_inference=false` 明确记录这一点。

模型显式通过 Transformers `torch_dtype` 加载，再交给 HFLM，兼容原服务器 Transformers 4.x。
脚本只读取本地完整 HF 权重；`--check-only` 不加载权重或数据、不推理。
`--prepare-data` 下载数据到通常的 Hugging Face 缓存并验证 validation 标签，不加载模型/GPU。
正式运行使用相同环境、用户和缓存目录。显存不足先将 `BATCH_SIZE=1`；正式评测 `LIMIT=None`。
`MAX_LENGTH=2048` 是 harness 上下文预算，过长输入按该版本 harness 行为保留末端上下文；所有对照保持相同设置。

## 保存结果

每次运行保存到独立的 `down/BoolQ/results/<模型标识>/<时间-标识>/`：

| 文件 | 内容 |
|---|---|
| `summary.json` | acc、小数/百分数、正确题数、标签分布和多数类基线、配置、依赖版本 |
| `samples.jsonl` | 每题文档、标签、候选响应及实际逐题指标 |
| `harness_results.json` | harness 汇总、配置和元数据，不重复保存 samples |
| `report.md` | 可读报告，试跑标明 LIMITED RUN |

重复运行创建新目录，不覆盖结果；样本缺失、重复、汇总与逐题指标不一致或总数不符时明确失败。
前 8 题仅用于检查运行，不代表完整任务能力。

## 原始来源与检查

- [Clark et al., 2019，BoolQ 原论文](https://arxiv.org/abs/1905.10044)
- [官方数据说明](https://github.com/google-research-datasets/boolean-questions)
- [固定版本任务配置](https://github.com/EleutherAI/lm-evaluation-harness/blob/v0.4.9.2/lm_eval/tasks/super_glue/boolq/default.yaml)

```bash
python -m unittest discover -s down/BoolQ -p 'test_*.py' -v
```

测试使用模拟推理后端核对调用协议、标签/多数类基线和保存流程，不能代替服务器真实 checkpoint 推理。
