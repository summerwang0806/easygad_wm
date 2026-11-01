# HellaSwag 学生模型下游能力评测

兼容较旧 Transformers 4.x：入口先通过 `AutoModelForCausalLM.from_pretrained(torch_dtype=...)`
加载本地模型，再把模型对象交给 HFLM。若旧脚本报 `unexpected keyword argument 'dtype'`，
更新本入口即可，无需为该问题升级依赖；保留服务器上自己配置的 `MODEL_PATH` 和 `TOKENIZER_PATH`。

只修改 `run_hellaswag.py` 顶部的 `MODEL_PATH`，然后在项目根目录运行：

```bash
CUDA_VISIBLE_DEVICES=3 python down/HellaSwag/run_hellaswag.py
```

或进入 `down/HellaSwag` 后运行 `python run_hellaswag.py`。相对模型路径始终以项目根目录为基准。
默认模型为 `checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_new/gad/global_step_1813/actor/huggingface`。

## 服务器准备与试跑

需要 Python >= 3.10、可用的 CUDA PyTorch、一张空闲 GPU，以及完整的本地 Hugging Face 模型权重。
模型目录需包含 `config.json`、单文件权重或完整分片及索引、tokenizer。
若 tokenizer 缺失，将顶部 `TOKENIZER_PATH` 改为同一学生基座的本地目录，如 `/shared/public_models/Qwen2.5-0.5B`。
不使用教师 tokenizer，不需要教师模型、裁判 API、vLLM，也不会自动下载模型权重。

在项目根目录执行：

```bash
# 如果已经安装 down 的 ARC-Easy 依赖，无需重复安装。
python -m pip install -r down/HellaSwag/requirements.txt

# 首次需要联网下载公开数据，不加载模型，不占 GPU。
python down/HellaSwag/run_hellaswag.py --prepare-data

# 可选：检查依赖、模型文件、tokenizer 和设备，不加载权重/数据。
CUDA_VISIBLE_DEVICES=3 python down/HellaSwag/run_hellaswag.py --check-only

# 前 8 题试跑，结果会注明 LIMITED RUN。
CUDA_VISIBLE_DEVICES=3 python down/HellaSwag/run_hellaswag.py --limit 8

# 全量评测：保持代码顶部 LIMIT = None。
CUDA_VISIBLE_DEVICES=3 python down/HellaSwag/run_hellaswag.py
```

`CUDA_VISIBLE_DEVICES=3` 下，脚本的 `DEVICE` 保持 `cuda:0`。显存不足可将 `BATCH_SIZE` 从 8 降到 1。
直接使用单进程 `python` 启动，不使用多卡 torchrun/accelerate。依赖固定为 `lm_eval==0.4.9.2`、Transformers 4.x，
与 ARC-Easy 共用同一环境即可。脚本沿用已有 Hugging Face 缓存；首次联网情况取决于服务器代理配置。
已缓存完整数据后可设置 `HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1` 离线运行。两次运行必须使用相同用户和缓存目录。

## 数据划分和评测协议

- 采用官方 harness 的 `hellaswag` 任务和 `Rowan/hellaswag` 数据集。
- 使用有答案标签的 **validation split**（标准为 **10042 题**）。公开 test 集的答案标签不用于该准确率评测。
- **0-shot**，没有聊天模板、system prompt、示例、推理时水印或自由采样。
- 官方预处理会清理 WikiHow 标记、方括号内容等，并对上下文和候选结尾执行相同的清洗。
  上下文由 `activity_label` 和 `ctx_a + ctx_b.capitalize()` 拼接，经预处理后作为 query。
- 对四个候选结尾逐一计算条件对数似然；不要求模型生成 A/B/C/D。
- 使用学生 tokenizer，固定 seed=42、默认最大上下文 2048。不同模型比较时保持相同协议。

设第 j 个候选结尾的总条件对数似然为 s_j，官方清洗后候选结尾的字符数为 L_j：

```text
acc      = mean(argmax_j(s_j)       == gold)
acc_norm = mean(argmax_j(s_j / L_j) == gold)
```

`acc_norm` 按答案字符串的字符数归一化，不是按 token 数归一化。两个指标都越高越好。
标准实现会处理候选答案前导空格与 tokenizer 边界，不在本脚本中另写评分逻辑。

官方定义与论文：

- [HellaSwag 官方任务配置](https://github.com/EleutherAI/lm-evaluation-harness/blob/v0.4.9.2/lm_eval/tasks/hellaswag/hellaswag.yaml)
- [官方预处理](https://github.com/EleutherAI/lm-evaluation-harness/blob/v0.4.9.2/lm_eval/tasks/hellaswag/utils.py)
- [官方 acc / acc_norm 评分](https://github.com/EleutherAI/lm-evaluation-harness/blob/v0.4.9.2/lm_eval/api/task.py)
- [HellaSwag 原始论文，ACL 2019](https://aclanthology.org/P19-1472/)

## 结果保存

每次保存到 `down/HellaSwag/results/<模型路径标识>/<北京时间-随机标识>/`，不覆盖旧结果：

| 文件 | 内容 |
|---|---|
| `summary.json` | acc、acc_norm 的小数、百分数、正确题数，以及 validation 样本量、模型路径、评测设置和依赖版本 |
| `report.md` | 可读结果表，明确写明 validation 划分 |
| `harness_results.json` | 官方汇总、任务配置、任务版本等元数据 |
| `samples.jsonl` | 官方逐题题目、标签、候选项、条件对数似然和两项 0/1 得分 |

会核对样本覆盖和逐题分数，失败不会报告成功。`--limit` 或顶部 `LIMIT` 非 None 时明确标注试跑，
不要作为正式全量结果；试跑到全量会重新推理，仅复用数据下载缓存。

当前开发环境没有服务器 checkpoint 和 CUDA。本地模拟测试通过不等于真实模型评测完成。
