# ARC-Easy 学生模型下游能力评测

平时只修改 `run_arc_easy.py` 顶部的 `MODEL_PATH`，然后运行：

```bash
python down/ARC-Easy/run_arc_easy.py
```

相对模型路径始终以项目根目录为基准；在项目根目录使用上面的命令，或进入 `down/ARC-Easy` 后运行 `python run_arc_easy.py`。
脚本默认评测这一份服务器 checkpoint：

```text
checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_new/gad/global_step_1813/actor/huggingface
```

## 服务器提前准备

1. 使用 Python **3.10 或以上**、已有可用 CUDA PyTorch 的环境。一张空闲 GPU 即可。
2. 把整个 `down` 目录同步到服务器项目下。进入服务器项目根目录并激活环境，例如 `conda activate wm`。
3. 安装评测依赖，不需要 vLLM、裁判模型或 API key：

```bash
python -m pip install -r down/ARC-Easy/requirements.txt
```

固定 `lm_eval==0.4.9.2`，并使用支持 Qwen2.5 的 Transformers 4.x。安装时不使用 `--upgrade`；
若旧训练环境的依赖出现冲突，可为评测单独准备环境并安装适配服务器 CUDA 的 PyTorch。
不要为了运行这个脚本重装整个项目的训练依赖。

4. 确保模型目录包含 `config.json`、完整权重和 tokenizer。分片权重还需要索引中列出的全部文件。
   若 `actor/huggingface` 只有配置/tokenizer，没有权重，需要先用项目训练导出流程合并 FSDP checkpoint。
   若只有 tokenizer 缺失，将顶部 `TOKENIZER_PATH` 改成同一学生基座的本地目录：

```python
TOKENIZER_PATH = "/shared/public_models/Qwen2.5-0.5B"
```

请使用学生自己的 tokenizer，不要使用 14B 教师 tokenizer。模型权重必须位于本地，不自动下载模型。

5. 第一次需要能访问 Hugging Face 以下载公开的 ARC 数据，无需手工整理或切分：

```bash
python down/ARC-Easy/run_arc_easy.py --prepare-data
```

此命令不加载模型，不占 GPU；缓存标准数据集 `allenai/ai2_arc` 的 `ARC-Easy` 配置。
脚本沿用环境原有的 Hugging Face 缓存设置，默认通常位于 `~/.cache/huggingface`。
服务器需按实际网络条件配置代理。无法联网时，可在联网机器使用相同依赖、同一命令准备数据，
再复制完整 Hugging Face 缓存到服务器对应缓存目录（HF_HOME / HF_DATASETS_CACHE 等保持一致）。
离线运行可以设置 `HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1`，但前提是该环境已经缓存了此数据集。

## 推荐运行顺序

在项目根目录：

```bash
# 可选：只检查模型文件、依赖可导入、tokenizer 和 GPU 可用性。
# 不加载权重，不下载数据，不代表权重已成功推理。
CUDA_VISIBLE_DEVICES=3 python down/ARC-Easy/run_arc_easy.py --check-only

# 先试跑前 8 题。
CUDA_VISIBLE_DEVICES=3 python down/ARC-Easy/run_arc_easy.py --limit 8

# 全量测试：确保代码顶部 LIMIT = None。
CUDA_VISIBLE_DEVICES=3 python down/ARC-Easy/run_arc_easy.py
```

`CUDA_VISIBLE_DEVICES=3` 将物理 GPU 3 映射为进程的 `cuda:0`；脚本顶部 `DEVICE` 仍保持 `cuda:0`。
也可以不设置这个环境变量，默认使用 GPU 0。请直接使用 `python` 启动，不用 `torchrun` 或多卡 accelerate。
显存不足时，把顶部 `BATCH_SIZE = 8` 改成 `1`；需要 CPU 调试时可设置 `DEVICE = "cpu"` 和 `DTYPE = "float32"`。

换模型只需改一行，例如：

```python
MODEL_PATH = "checkpoints/另一个实验/gad/global_step_1813/actor/huggingface"
# 也接受服务器上的绝对路径：
# MODEL_PATH = "/shared/public_models/Qwen2.5-0.5B"
```

## 固定评测协议与指标

- 直接调用官方 `lm-evaluation-harness 0.4.9.2` 的 `arc_easy` 任务。
- 使用 **test split**（标准数据为 2376 题），**0-shot**，没有示例、system prompt 或聊天模板。
- prompt 为 `Question: {question}\nAnswer:`，逐个评分候选答案文本（带 harness 的默认前导空格），不是生成 A/B/C/D 后解析。
- 使用模型本身的条件对数似然；不添加推理时 KGW 水印，不使用教师模型或裁判评分。
- `acc`：选择候选答案**总条件对数似然**最大的选项，计算正确率。
- `acc_norm`：先将各候选答案总条件对数似然除以其**原始答案字符串的字符数**，再选最大值并计算正确率。
  这是指定 harness 版本的实现，不是按 tokenizer token 数归一化，也不是把准确率再除以长度。
- 两个分数均以 `[0,1]` 和百分数输出。固定 seed=42、最大上下文 2048，不采样生成答案。
  若更改 dtype、上下文上限、tokenizer 或模板，比较实验也要保持一致。

设第 j 个答案的总条件对数似然为 s_j，字符长度为 L_j，则：

```text
acc      = mean(argmax_j(s_j)       == gold)
acc_norm = mean(argmax_j(s_j / L_j) == gold)
```

参考实现：

- [官方 ARC-Easy 任务配置](https://github.com/EleutherAI/lm-evaluation-harness/blob/v0.4.9.2/lm_eval/tasks/arc/arc_easy.yaml)
- [官方评分实现（completion_len / pred_norm）](https://github.com/EleutherAI/lm-evaluation-harness/blob/v0.4.9.2/lm_eval/api/task.py)
- [ARC 原始论文](https://arxiv.org/abs/1803.05457)

## 结果保存

每次独立保存到 `down/ARC-Easy/results/<模型路径标识>/<北京时间-随机标识>/`，换模型或重跑不会覆盖历史结果：

| 文件 | 内容 |
|---|---|
| `summary.json` | 模型/tokenizer 路径、acc、acc_norm、正确题数、样本量、评测设置、依赖版本 |
| `report.md` | 可读的百分数结果表 |
| `harness_results.json` | 官方结果及任务配置、任务版本、执行元数据 |
| `samples.jsonl` | 每题原始题目、候选项、目标、对数似然、acc 与 acc_norm 等官方逐题记录 |

脚本会核对样本覆盖率，并用逐题 0/1 结果核验汇总分数。`--limit` 或顶部 `LIMIT` 非 None 的结果
明确标注 `LIMITED RUN`，只用于试跑，不能作为正式全量论文结果。试跑缓存不复用到全量推理；数据集缓存会复用。
这里只给出评测题目上的点估计；如使用标准误输出，其单位为 `[0,1]`，不是百分数，也不包含训练随机种子的差异。

本地开发机器缺少服务器 checkpoint 与 CUDA，不能在此声称已得到真实模型分数；服务器 8 题试跑通过后再运行全量。
