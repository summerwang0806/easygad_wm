# PIQA：物理常识二选一，acc / acc_norm

修改 `run_piqa.py` 顶部的 `MODEL_PATH` 后即可运行。相对路径始终以项目根目录为基准；也支持服务器绝对路径。
默认学生路径是：

```text
checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_new/gad/global_step_1813/actor/huggingface
```

`TOKENIZER_PATH` 默认是服务器同一学生基座 `/shared/public_models/Qwen2.5-0.5B`。
若导出的模型目录已包含完整 tokenizer，可改为 `None`；不要使用教师 tokenizer。

## 服务器运行

使用 Python >= 3.10 和已安装可用 CUDA PyTorch 的环境，从项目根目录执行：

```bash
python -m pip install -r down/PIQA/requirements.txt

# 只下载和检查数据，不加载模型或 GPU。
python down/PIQA/run_piqa.py --prepare-data

# 只检查依赖、本地模型文件、tokenizer 和设备，不加载模型权重或推理。
CUDA_VISIBLE_DEVICES=3 python down/PIQA/run_piqa.py --check-only

# 前 8 题试跑。
CUDA_VISIBLE_DEVICES=3 python down/PIQA/run_piqa.py --limit 8

# 全量 validation 1838 题；顶部 LIMIT 保持 None。
CUDA_VISIBLE_DEVICES=3 python down/PIQA/run_piqa.py
```

也可进入 `down/PIQA` 后直接执行 `python run_piqa.py`。
`CUDA_VISIBLE_DEVICES=3` 时脚本中的 `DEVICE` 仍为 `cuda:0`；单进程单卡运行，显存不足先把 `BATCH_SIZE` 降为 1。
模型仅从本地目录读取，不自动下载权重；需要完整 Hugging Face 导出，不能直接使用 FSDP 分片。

## 数据与评分协议

- 固定 `lm-evaluation-harness==0.4.9.2` 官方任务 `piqa`，**0-shot、plain completion、不使用聊天模板**。
- 该固定版本的官方配置使用 **`baber/piqa`**、`dataset_name=None`，评测 **validation 的 1838 题**；不使用未公开标签的 test。
- `--prepare-data` 使用相同仓库和正常 Hugging Face 缓存，检查题数、`goal` / `sol1` / `sol2` 文本与 `label` 的 0/1 标签。
- 该数据仓库为 Parquet，无需执行远程 dataset Python 脚本，不需要 `trust_remote_code=True` 或为 PIQA 特意降级 datasets。
- 输入格式是 `Question: {goal}\nAnswer:`，比较两个完整候选方案在上下文下的条件对数似然；不要求模型生成 A/B 字母，也不调用 LLM 裁判。
- **acc** 取总条件对数似然较高的候选；**acc_norm** 在该固定版本按候选字符串的**字符数**归一化后选择，不是按 tokenizer token 数。
- 两项均越高越好。结果同时保存 0～1 小数、0～100 百分数与正确题数。建议预先固定一个主指标，并对所有模型保持一致。
- 使用 Transformers 的 `torch_dtype` 参数先加载模型，再把预加载模型交给 HFLM，兼容现有服务器环境中较旧的 Transformers 4.x 接口。

**本入口测 checkpoint 本身的能力，没有启用 WN 等推理阶段 logits processor。**
若两个实验使用同一组权重，只在生成时启用不同 WN 设置，本入口的标准似然分数不会反映该处理器的影响；不能将本结果标成“已启用 WN 的生成质量”。

## 输出与检查

结果保存于 `down/PIQA/results/<模型标识>/<时间-随机标识>/`，每次运行独立归档：

| 文件 | 内容 |
|---|---|
| `summary.json` | 两项指标、正确题数、试跑标志、模型/数据/设备/依赖版本配置 |
| `report.md` | 可读的百分制结果表 |
| `harness_results.json` | 官方任务配置、汇总分数、版本等 harness 元数据 |
| `samples.jsonl` | 逐题问题、候选答案、模型响应与两项得分 |

程序校验官方题数、完整覆盖率、重复/意外的题目 ID、逐题二值分数和汇总一致性。
覆盖不完整时明确失败；`--limit` 结果标记 `LIMITED RUN`，不能作为完整论文结果。当前不自动续跑中断任务。
数据准备失败先检查 Hugging Face 网络与缓存；正式运行需使用准备数据时相同的环境、用户和缓存位置。

无需模型或 GPU 的开发检查：

```bash
python -m unittest discover -s down/PIQA -p test_run_piqa.py -v
```

测试使用模拟推理后端验证调用协议与结果保存，不代表已经完成真实模型能力评测。

## 来源

- [PIQA 原论文：Bisk et al., 2020](https://arxiv.org/abs/1911.11641)
- [作者任务主页](https://yonatanbisk.com/piqa/)
- [固定版本官方任务配置](https://github.com/EleutherAI/lm-evaluation-harness/blob/v0.4.9.2/lm_eval/tasks/piqa/piqa.yaml)
- [实际使用的 Parquet 数据仓库](https://huggingface.co/datasets/baber/piqa)
