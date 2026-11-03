# SQuAD 1.1：生成式阅读理解，EM / F1

只修改 `run_squad.py` 顶部的 `MODEL_PATH`，然后在项目根目录执行：

```bash
CUDA_VISIBLE_DEVICES=3 python down/SQuAD/run_squad.py
```

常用模型路径示例（以脚本中你当前设置的路径为准）：

```text
checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_new/gad/global_step_1813/actor/huggingface
```

相对路径始终相对于项目根目录；也支持服务器绝对路径。`TOKENIZER_PATH=None` 时使用模型目录中的 tokenizer；
显式设置时使用该目录。导出目录缺少 tokenizer 时，将其指向同一个学生基座的本地目录，并保持所有对照一致。

## 准备与试跑

使用 Python >= 3.10、已安装可用 CUDA PyTorch 的环境。一张空闲 GPU 即可，不需要教师、裁判模型或 API。
以下命令均在项目根目录运行：

```bash
python -m pip install -r down/SQuAD/requirements.txt

# 默认只准备官方 dev 数据，不需要训练集或 GPU。
python down/SQuAD/run_squad.py --prepare-data

# 仅检查数据、模型/tokenizer 和设备；不加载权重或推理。
CUDA_VISIBLE_DEVICES=3 python down/SQuAD/run_squad.py --check-only

# 前 8 题试跑。
CUDA_VISIBLE_DEVICES=3 python down/SQuAD/run_squad.py --limit 8

# 进一步检查短答格式；前 100 题只用于格式/运行检查，不代表总体能力。
CUDA_VISIBLE_DEVICES=3 python down/SQuAD/run_squad.py --limit 100

# 全量 10570 题；顶部 LIMIT 保持 None。
CUDA_VISIBLE_DEVICES=3 python down/SQuAD/run_squad.py
```

也可以进入 `down/SQuAD` 后运行 `python run_squad.py`。需要同步上一级 `down/generation_utils.py`；
只有显式开启 few-shot 时才需要本目录的 `fewshot.py`。
开启 WN 时还需要项目现有 `baseline_acl/inverse_watermark.py`。

首次下载需要能访问 Stanford 官方站点。默认只使用 `down/SQuAD/data/dev-v1.1.json`；
也可在联网机器从下面的官方链接下载该文件，再复制到服务器。已有文件只读取核验，不覆盖。
默认正式运行在缺少数据时也会下载；`--check-only` 不下载。

## 当前默认：恢复原始 0-shot 评测

当前 `NUM_FEWSHOT = 0`。直接运行即可使用原来的段落/问题提示、chat 模板和 greedy 解码；
不加载训练集、不插入示例，标准 EM/F1 公式与原始版本一致。模型路径和 tokenizer 配置以脚本当前设置为准。
已有的 0-shot / 3-shot 结果保留，缓存按协议区分。

### 可选：复现此前的 3-shot 实验

只有显式设置 `--num-fewshot 3` 或修改顶部配置才会使用训练示例。以下规则仅适用于该可选模式：

- 示例从官方 **SQuAD 1.1 train 的 87599 题**中选取，不使用 dev 参考答案或 dev 得分挑选。
- 固定排序后按种子抽取，选自不同文章/段落；上下文最多 1800 字符、问题最多 300 字符、首个标注答案最多 8 个词，并且是原文连续片段。
- 所有学生必须使用相同 `NUM_FEWSHOT`、`FEWSHOT_SEED`、示例顺序、模板和生成设置。
- chat 模式使用真实的 user/assistant 示范对话，最后仅给出待测段落和问题；completion 模式用相同的训练示例拼接。
- `protocol.json` 和 `fewshot_examples.json` 保存示例原文、ID、训练文件 SHA256、选择代码指纹等。
- 输入长度检查包含全部示例和测试段落，过长会报错，不自动丢弃示例或截断上下文。
- 结果增加预测/参考答案词数的诊断字段，帮助检查模型是否仍然输出长句；它们不是新的准确率指标。

复现该实验的命令：

```bash
python down/SQuAD/run_squad.py --prepare-data --num-fewshot 3
CUDA_VISIBLE_DEVICES=3 python down/SQuAD/run_squad.py --num-fewshot 3
```

零样例不需要 train 文件，`--score-only` 也不需要训练集或模型。新协议使用新的缓存标识，旧结果不会被覆盖或混入。
论文中应分别标注 0-shot / 3-shot。先在小样本检查格式和运行，再以同一固定设置完整评测所有模型。

## 固定协议

- 数据为 **SQuAD 1.1 dev**，不是 SQuAD 2.0，也不是训练集。程序校验 1.1 版本、10570 个唯一问题、人工答案和位置字段；评分采用标注答案文本，不依赖字符偏移。
- 将文章和问题直接提供给学生，要求只输出最短答案片段。默认不展示示例，待测题目的参考答案不会发送给模型。
- 默认 `PROMPT_STYLE = "chat"`，使用学生自身 tokenizer 的聊天模板；缺少模板时明确报错。
  若要评测纯 completion 模型，可以把该配置显式改成 `"completion"`，所有对照都保持相同设置。
- 默认 greedy（temperature=0）、最多生成 64 token；最大输入 4096 token。输入过长会报错，不静默截断。
- **完整生成文本直接评分**，不只选第一行、不搜索最优 span、不用参考答案清理模型输出。
- 命中生成上限的答案仍保留并评分，同时在结果中报告数量；不是删掉失败样本。

### 两个指标

- **EM（Exact Match）**：小写、去 ASCII 标点、去英语冠词 `a/an/the`、合并空白后，与任一人工答案完全匹配。
- **F1**：采用同样归一化后的英文词切分，计算词计数重合的 precision / recall 的调和平均值。
  多个人工参考分别评分，取最高分；不是使用学生 tokenizer 的 token 来计算。
- 汇总 `exact_match`、`f1` 均为 **0～100 分**；另存 `[0,1]` 的 fraction 字段。

例：参考 `New York`、生成 `New York City`，EM=0、F1=80。
这是使用官方 v1.1 评分定义进行的生成式测评，不是另外训练一个 span-extraction 任务头。

## WN 组如何评测

未洗组、UP/TP 训练后的学生：

```python
WN_RULES_PATH = None
WN_STRENGTH = 0.0
```

WN 组只需在同一入口改为项目已经估计好的规则文件和实验强度：

```python
WN_RULES_PATH = "wn/你的规则文件.json"
WN_STRENGTH = 2.5
```

WN 在学生每步生成时实际修改 logits，沿用项目现有 inverse-watermark 实现；它不读取真正 KGW 检测密钥。
规则与学生 tokenizer 必须一致，否则报错。WN 与不启用 WN 的对照应使用同一个 checkpoint、相同提示和生成设置。
更换模型、tokenizer、提示或 WN 配置后，自动使用不同的结果/缓存目录。

## 保存、续跑和重新评分

保存到 `down/SQuAD/results/<模型标识.协议哈希>/`：

| 文件 | 内容 |
|---|---|
| `protocol.json` | 模型与 tokenizer 指纹、依赖版本/运行时代码指纹、数据 SHA256、提示、生成和 WN 配置 |
| `fewshot_examples.json` | 固定训练示例、选择种子和规则、来源哈希；零样例时示例为空 |
| `generations.jsonl` | 每题完整原始预测与生成信息，完成一题即刷新到磁盘 |
| `runs/<时间-标识>/predictions.json` | 标准 `question_id -> 完整生成答案`，可交给其他 SQuAD 评分程序 |
| 同目录 `scores.jsonl` | 每题原始预测、归一化预测、参考答案、EM 与 F1 |
| 同目录 `summary.json` / `report.md` | 总体 EM/F1、shot 数、试跑标志、答案词数、长度上限命中数量和配置 |

每次独立创建 `runs` 归档，不覆盖旧汇总。相同协议下重新运行会复用成功答案；8 题试跑到全量也可续用。
同一配置不能同时运行；异常退出通常会释放 `.lock`，若进程被强制结束，只能在确认旧进程已结束后手动移除对应锁。
若末尾缓存 JSON 因断电等原因写坏，程序明确报错，不静默丢弃或伪造该题。
模型权重指纹使用路径/文件大小/修改时间与小文件哈希，不会重复读取整个大模型权重。

已有完整预测可不加载模型直接评分：

```bash
python down/SQuAD/run_squad.py --score-only --predictions-file /path/to/predictions.json
```

预测 ID 必须与本次全部问题完全匹配；8 题预测需再加 `--limit 8`。空预测会按其实际文本评分，不从分母排除。
所有试跑明确标注 `LIMITED RUN`，不要作为全量论文结果。对比多模型时保持相同数据、模板、生成上限和精度。

## 来源与本地检查

- [SQuAD 官方任务与数据说明](https://rajpurkar.github.io/SQuAD-explorer/)
- [官方 dev-v1.1.json](https://rajpurkar.github.io/SQuAD-explorer/dataset/dev-v1.1.json)
- [官方 train-v1.1.json](https://rajpurkar.github.io/SQuAD-explorer/dataset/train-v1.1.json)
- [SQuAD 原始论文](https://aclanthology.org/D16-1264/)

```bash
python -m unittest discover -s down/SQuAD -p 'test_*.py' -v
```

本地测试覆盖归一化、多参考、重复词、缺失预测、训练示例选择、提示无测试答案、协议缓存隔离及续跑/归档流程，使用模拟生成后端。
当前开发环境没有服务器 checkpoint/CUDA，不能据此声称已完成真实模型全量评测。
