# 固定 clean 教师参照的本地 Soft Win Rate

日常只修改 `run_teacher_soft_win_rate.py` 顶部的 **`INPUT_JSONL`**，然后在服务器已有的 `wm` 环境运行：

```bash
python soft-win-rate/run_teacher_soft_win_rate.py
```

也可以进入 `soft-win-rate/` 后运行 `python run_teacher_soft_win_rate.py`。相对输入路径始终以项目根目录为基准。

默认待评文件为 `wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl`，因此 clean 学生也能得到对同一教师参照的实测胜率。更换待评配置时只改 `INPUT_JSONL`。

固定参照为 **`data/dolly15k_qwen2_5_14b_clean_test.parquet`**，直接读取 `id`、`content`、`teacher_response`，对应待测 JSONL 的 `id`、`prompt`、`answer`。不重新生成参照、不修改 Parquet，也不需要手动转换文件。全部 ID 和完整问题必须一致；即使使用 `--limit`，仍先检查全量对齐。

沿用原程序的本地 `/shared/public_models/Qwen3-32B` 裁判、自动选卡、显存不足重试、完整文本窗口自动扩展、匿名 A/B 双顺序评分、按题目 bootstrap 95% CI、成功判断缓存及断点续跑。胜=1、平=0.5、负=0，先平均同题两轮，再平均全部完整题目；失败或截断不计平局。不会调用 API。

胜率表示相对固定教师回答的偏好，不是绝对质量分；clean 是否最高由实测决定。文件名及 clean 标记不构成实际生成模型身份的证明，本入口不额外断言已核实生成时使用的模型。

## 结果位置

- `soft-win-rate/teacher_soft_win_rate_history.md`：每次追加胜率、CI、覆盖率、输入及原始 Parquet 的 SHA256、裁判和执行配置。
- `soft-win-rate/results/teacher/<输入名>.<协议哈希>/judgments.jsonl`：逐轮成功判断；相同输入重跑直接续跑。
- 同目录 `runs/*.json`：每次运行的结果归档及逐题分数；`workers/`：本轮 worker 日志。
- `soft-win-rate/results/teacher/context_plans/`：当前输入需要的自动窗口记录。

这些位置与原来的 clean 学生参照评测分开。更换输入、原始 Parquet 内容或评分协议会产生不同缓存。

## 可选检查

```bash
# 只检查数据；服务器有本地裁判时也检查选卡方案，不推理、不写结果
python soft-win-rate/run_teacher_soft_win_rate.py --check-only

# 先试跑前 5 题，之后不带参数运行会复用已完成判断
python soft-win-rate/run_teacher_soft_win_rate.py --limit 5

# 仅从已有缓存追加汇总，不启动 GPU；仍需本地裁判文件核对指纹
python soft-win-rate/run_teacher_soft_win_rate.py --summary-only
```

新增 Parquet 读取依赖 `pyarrow`，使用服务器已有环境即可。原 JSONL 入口不需要导入此依赖。部署时同步 `run_teacher_soft_win_rate.py` 和更新后的 `run_soft_win_rate.py`，保留原有 `judge_worker.py`、`gpu_runtime.py` 等配套文件。
