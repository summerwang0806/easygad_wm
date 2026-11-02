# LAMBADA：上下文末词预测

修改 `run_lambada.py` 顶部的 `MODEL_PATH` 后即可运行。相对模型路径以整个项目根目录为基准；
默认学生是 `checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_new/gad/global_step_1813/actor/huggingface`。
`TOKENIZER_PATH` 默认指向服务器 `/shared/public_models/Qwen2.5-0.5B`，也可设为 `None` 使用导出目录。
它必须与学生基座相同，不能使用教师 tokenizer。

## 运行

Python >= 3.10，使用已有可用 CUDA PyTorch 环境。以下命令在项目根目录执行：

```bash
python -m pip install -r down/LAMBADA/requirements.txt

# 只准备数据，不加载模型或占用 GPU。
python down/LAMBADA/run_lambada.py --prepare-data

# 检查依赖、本地权重文件、tokenizer 和设备，不加载权重或数据。
CUDA_VISIBLE_DEVICES=3 python down/LAMBADA/run_lambada.py --check-only

# 前 8 题试跑。
CUDA_VISIBLE_DEVICES=3 python down/LAMBADA/run_lambada.py --limit 8

# 正式评测完整 5153 题，顶部 LIMIT 保持 None。
CUDA_VISIBLE_DEVICES=3 python down/LAMBADA/run_lambada.py
```

也可进入 `down/LAMBADA/` 执行 `python run_lambada.py`。显存不足先将顶部 `BATCH_SIZE` 从 8 降为 1；
对比时固定 `MAX_LENGTH`（默认 2048）和 tokenizer。采用单进程单卡，不使用 torchrun。

数据通过 Hugging Face 标准缓存下载，`--prepare-data` 和正式评测需使用相同环境、用户与缓存目录。
首次运行需能访问 Hugging Face。模型和 tokenizer 只从指定的本地目录加载，不自动下载权重。

## 固定评测协议与指标

- 官方 `lm-evaluation-harness==0.4.9.2`，任务 `lambada_openai`。
- 数据 `EleutherAI/lambada_openai` / `default` 的 **test，5153 题**；不是原始 `lambada_standard` 变体。
- 0-shot、纯 completion；不添加聊天模板，不要求学生生成解释或严格格式的回答。
- 题目文本的最后一个空格分隔词为目标（带前导空格），其余文本为上下文，完全沿用官方任务。
- **acc 越高越好**：目标词对应的所有模型 token 都是其条件下的 greedy 首选时记为正确；一个词可以含多个 subword token。
- **perplexity（PPL）越低越好**：`exp(-mean(log P(目标末词 | 上下文)))`。每个词的对数概率为其所有 token 对数概率之和。
- 这里的 PPL 是**末词预测困惑度**，不是整篇文本的 PPL，也不是按模型 token 数归一化的 PPL，不能与其他口径直接比较。
- 附带保存 `mean_target_word_nll`：上述末词平均负对数似然，也是越低越好。

`acc` 同时保存 `[0,1]` 小数、百分数和正确题数；PPL 不乘 100，没有 100 分上限。
逐题日志中官方字段 `perplexity` 实际保存该末词的 **loglikelihood（通常为负数）**，不是该题已经指数变换后的 PPL。
程序用这些原始分数重新核对总体 PPL，避免误算为 `mean(exp(-ll))`。

## 结果

保存到 `down/LAMBADA/results/<模型标识>/<时间与运行标识>/`，每次独立归档：

| 文件 | 内容 |
|---|---|
| `summary.json` | acc/PPL、正确数、样本数、模型路径、生成协议、版本、种子等 |
| `report.md` | 可读指标汇总与定义 |
| `harness_results.json` | 官方 harness 汇总、任务配置和元数据 |
| `samples.jsonl` | 逐题文档、目标、条件似然、greedy 匹配等官方日志 |

保存前检查完整样本数、重复 ID、逐题分数与汇总的一致性；不完整或非有限结果会报错。
`--limit` 试跑标注 `LIMITED RUN`，不能当作全量论文结果。此入口不做断点续跑，每次执行完整的指定范围。

## WN 的适用范围

本入口测量 **checkpoint 自身的标准条件概率**，不调用 `generate`，也不启用 WN logits processor。
WN 若只在推理时改变解码、没有改变权重，这里的原始 acc/PPL 不会体现其影响。
需要评估 WN 时应另设实际启用该处理器的评测协议，并在论文中说明；不能把此入口的结果称为 WN 解码结果。

## 来源与本地测试

- [LAMBADA 原论文，Paperno et al., ACL 2016](https://aclanthology.org/P16-1144/)
- [固定版本官方任务配置](https://github.com/EleutherAI/lm-evaluation-harness/blob/v0.4.9.2/lm_eval/tasks/lambada/lambada_openai.yaml)
- [固定版本评分与 greedy 定义](https://github.com/EleutherAI/lm-evaluation-harness/blob/v0.4.9.2/lm_eval/api/task.py)
- [固定版本 PPL 聚合函数](https://github.com/EleutherAI/lm-evaluation-harness/blob/v0.4.9.2/lm_eval/api/metrics.py)

```bash
python -m unittest discover -s down/LAMBADA -p 'test_*.py' -v
```

测试使用模拟推理后端，验证评分聚合、数据划分、模型调用协议及结果保存，不代表真实 checkpoint 的评测分数。
