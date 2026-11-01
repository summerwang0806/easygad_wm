# 学生模型下游能力评测

两个任务分别维护入口、顶部模型配置及结果目录。平时只修改对应脚本顶部的 `MODEL_PATH`。
相对路径始终相对于项目根目录，不受当前工作目录影响。两个入口默认都使用：

```text
checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_new/gad/global_step_1813/actor/huggingface
```

| 任务 | 入口 | 数据划分 | 指标 | 使用说明 |
|---|---|---|---|---|
| ARC-Easy | `ARC-Easy/run_arc_easy.py` | test，2376 题 | acc、acc_norm | [ARC-Easy](ARC-Easy/README.md) |
| HellaSwag | `HellaSwag/run_hellaswag.py` | validation，10042 题 | acc、acc_norm | [HellaSwag](HellaSwag/README.md) |

固定使用官方 `lm-evaluation-harness==0.4.9.2`，均为 0-shot、候选答案条件对数似然评分，不添加聊天模板或推理时水印。
HellaSwag 的公开 test 集没有可用于本评测的答案标签，采用官方 harness 配置的 validation 集。

模型加载使用 Transformers 的 `torch_dtype` 参数，加载后再交给 HFLM 评分。
这避免了 lm-eval 0.4.9.2 内部使用 `dtype` 与较旧 Transformers 4.x 的接口冲突。
遇到 `Qwen2ForCausalLM.__init__() got an unexpected keyword argument 'dtype'` 时，
同步修复后的两个入口脚本即可，无需为此升级服务器训练环境中的 Transformers。
若服务器已修改 `MODEL_PATH` / `TOKENIZER_PATH`，同步时保留这些本地配置。

## 服务器运行

Python >= 3.10，并使用已有可用 CUDA PyTorch 的环境。在项目根目录安装一次即可用于两个任务：

```bash
python -m pip install -r down/requirements.txt

# 第一次提前下载数据，不加载模型/GPU。
python down/ARC-Easy/run_arc_easy.py --prepare-data
python down/HellaSwag/run_hellaswag.py --prepare-data

# 各取前 8 题试跑。
CUDA_VISIBLE_DEVICES=3 python down/ARC-Easy/run_arc_easy.py --limit 8
CUDA_VISIBLE_DEVICES=3 python down/HellaSwag/run_hellaswag.py --limit 8

# 正式全量评测，确保各入口顶部 LIMIT = None。
CUDA_VISIBLE_DEVICES=3 python down/ARC-Easy/run_arc_easy.py
CUDA_VISIBLE_DEVICES=3 python down/HellaSwag/run_hellaswag.py
```

也可进入各任务目录后直接运行 `python run_arc_easy.py` 或 `python run_hellaswag.py`。
`--check-only` 仅检查环境、模型文件与 tokenizer，不推理。若 tokenizer 不在模型导出目录，
将入口的 `TOKENIZER_PATH` 指向同一学生基座目录；显存不足则降低入口顶部 `BATCH_SIZE`。

## 输出与迁移

- ARC-Easy 保存到 `down/ARC-Easy/results/`。
- HellaSwag 保存到 `down/HellaSwag/results/`。
- 每次单独创建模型/运行子目录，保存 `summary.json`、`report.md`、`harness_results.json`、`samples.jsonl`。
- 两项指标同时保存小数、百分数和正确题数。试跑明确标注 `LIMITED RUN`。
- 旧入口 `down/run_arc_easy.py` 已移动到 `down/ARC-Easy/run_arc_easy.py`。
  如服务器原先已有 `down/results/`，历史结果可以保留；新运行使用任务子目录。

## 本地开发检查

无需真实权重或 CUDA：

```bash
python -m unittest discover -s down/ARC-Easy -p test_run_arc_easy.py -v
python -m unittest discover -s down/HellaSwag -p test_run_hellaswag.py -v
```

这些测试使用模拟推理后端，检查路径、数据划分、调用协议和结果保存，不能替代服务器真实模型试跑。
