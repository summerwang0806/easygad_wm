# 文本质量评测使用说明

本目录评估已经生成的回答，比较 SeqKD、warmup、GAD 和原始学生模型的文本质量。当前默认使用 **GPT-5.5 中转 API 裁判 + Dolly 测试题对应的原始人工回答**。

每次只评测一个 JSONL 文件，手动换文件名评测下一份。每份文件有自己的结果目录和 SwanLab 实验，不会自动合并四个模型。不加载学生模型，不使用 GPU 或 Ray，也不修改训练 checkpoint。

## 1. 快速开始

以下 Bash 命令在服务器执行，均以项目根目录为起点：

```bash
cd /app/wwx/EasyGAD
conda activate wm
```

服务器上 `/app/wwx/EasyGAD` 与 `/shared/wwx/EasyGAD` 指向同一项目。若当前终端没有 `conda` 命令，可改用：

```bash
source /app/wwx/miniconda3/bin/activate wm
```

### 网络与代理

需要通过本地代理联网时，先确保 Windows 本地代理监听 `127.0.0.1:56734`，在 Windows PowerShell 建立 SSH 隧道并保持窗口开启：

```powershell
ssh -F NUL -o ExitOnForwardFailure=yes -R 127.0.0.1:7890:127.0.0.1:56734 -p 3389 wwx@10.107.6.60
```

然后在运行评测的服务器终端设置：

```bash
export http_proxy=http://127.0.0.1:7890
export https_proxy=http://127.0.0.1:7890
export no_proxy=127.0.0.1,localhost
```

每个新终端都需要重新设置代理变量。隧道存在不代表本地代理正在工作；服务器能直接访问服务时可以不用代理。

### 第一步：只检查，不调用 API

```bash
bash text_quality/run_quality.sh \
  --input-file wm_test/kgw_gad_qwen2_5_0_5b_dolly15k_test.jsonl
```

检查输入、参考匹配和输出配置；不会评分、创建 SwanLab 实验或写结果。正常会看到 `Aligned 500 IDs`、`selected 500` 和 `CHECK ONLY`。脚本必须指定 `--input-file`，不能空参数启动。

### 第二步：先评测 5 条

```bash
bash text_quality/run_quality.sh \
  --input-file wm_test/kgw_gad_qwen2_5_0_5b_dolly15k_test.jsonl \
  --limit 5 --concurrency 8 \
  --run-api --max-api-calls 30
```

`--run-api` 才会真正提交题目、模型回答和人工参考给中转站，可能产生费用。5 条正常需要 10 次评分请求，预算 30 为失败重试留余量。

### 第三步：全量评测 500 条

```bash
bash text_quality/run_quality.sh \
  --input-file wm_test/kgw_gad_qwen2_5_0_5b_dolly15k_test.jsonl \
  --concurrency 4 --run-api --max-api-calls 1500
```

不指定 `--limit` 就评测全文件。500 条正常需要 **1000 次评分请求**：每条交换回答顺序评分两次，不生成参考回答。与试跑保持同一配置、同一结果目录，已有成功缓存会复用。

### 手动换文件

只修改上面命令的 `--input-file`，其余参数可以保持不变：

| 待评模型 | `--input-file` 的值 |
|---|---|
| SeqKD | `wm_test/kgw_seqKD_full_kgwdata_qwen2_5_0_5b_dolly15k_test.jsonl` |
| warmup | `wm_test/kgw_warmup_qwen2_5_0_5b_dolly15k_test.jsonl` |
| GAD | `wm_test/kgw_gad_qwen2_5_0_5b_dolly15k_test.jsonl` |
| 原始学生模型 | `wm_test/base_qwen2_5_0_5b_dolly15k_test.jsonl` |

输入每行需要 `id`、`prompt` 和 `answer`，兼容 `wm_test/generate_compare_score.py` 的输出。`prompt` 可以是消息列表或文本；ID 不能重复，问题必须与参考文件中对应 ID 的完整 prompt 匹配。

## 2. 参考回答来自哪里？

固定读取 `text_quality/references/dolly_human_500.jsonl`，来源是原始 Dolly 数据的人工 `response`，不是 GPT-5.5 新生成的回答，也不是 KGW 教师生成回答。

准备工具核对了原始数据、`data/dolly15k_test.parquet` 和四份模型输出的 ID、instruction、context 与答案。在这份基础 test parquet 中，字段虽然叫 `teacher_response`，其内容已核验为 Dolly 原始人工回答；不能仅凭字段名换成 KGW 数据中的同名字段。

服务器已准备好参考文件。需要重新核验时运行：

```bash
python text_quality/prepare_dolly_references.py
```

这一步不调用 API、不使用 GPU，但依赖服务器已有的 `datasets` 和 `pyarrow`，且会读取四份模型文件做一致性检查。已有参考文件若内容一致则只核验；不一致会报错，不覆盖旧文件。

评测时参考缺失或问题不匹配会停止，不会自动退回 API 生成参考。人工回答也可能有遗漏或错误，不视为唯一正确答案。

## 3. 评分逻辑与指标含义

默认 `paper` 模式：把待评回答和人工参考作为匿名 A/B 给裁判，分别打分，再交换顺序重新评分。裁判不会收到模型名称、水印标签、checkpoint 路径或水印 z-score。

五个维度均为 1～10 分：

| 维度 | 含义 |
|---|---|
| `helpfulness` | 是否有效帮助用户完成任务 |
| `relevance` | 是否切题、遵循题目要求 |
| `accuracy` | 内容是否准确 |
| `detail` | 细节是否充分且适当，不等于越长越好 |
| `overall` | 总体质量判断 |

两次评分映射回原回答后取平均。每条题目的相对分数为：

```text
每个顺序的相对分数 = 100 × 模型 overall / (模型 overall + 参考 overall)
该题相对分数 = 两个顺序的相对分数平均
最终相对分数 = 所有有效题目的相对分数平均
```

50 表示评分上与参考持平，**不是 50% 正确率**。参考不强制给 10 分。报告还包含分维度均值、胜/平/负比例、顺序一致率和按题目 bootstrap 的 95% 置信区间。

这里的胜率是“模型回答对人工参考”的胜率，不是 GAD 对 warmup 的直接对战胜率。每份文件单独运行时也不会自动生成跨模型配对分差。

### 如何比较模型？

四份文件用相同题目、生成设置、裁判和参考分别评测后，比较完整报告中的 `overall`、相对分数、分维度评分与覆盖率，并抽查逐题理由。少量样本或区间重叠时，不宜只凭均分断言显著提升。

文本质量与水印能力需要分别报告：本目录的裁判评分衡量内容质量；KGW 的 AUROC、TPR@FPR 衡量水印可检测性；训练中的 ROUGE-L 衡量与参考文本的词序重合，不能替代这些指标。证明 GAD 有用，应展示水印能力改善以及文本质量的变化或保持情况，不能只看训练奖励。

当前 GPT-5.5 裁判与人工参考设置不等于论文 GPT-4o 设置的严格复现，分数不能直接与论文数值比较。置信区间不覆盖裁判偏差或训练随机种子差异；已用于训练验证、选 checkpoint 的测试题也不能当作完全独立的最终测试集。

## 4. 并发、预算与常用参数

| 参数 | 作用 |
|---|---|
| `--input-file 路径` | 必填，每次只评测这一份文件 |
| `--limit 5` | 只评测排序后前 5 个 ID；省略则全量 |
| `--concurrency 8` | 并行处理题目，上限为 8 个在途请求；API 默认 4 |
| `--run-api` | 真正调用 API；省略则仅检查 |
| `--max-api-calls 1500` | 本次启动的实际请求上限，包含失败请求和重试 |
| `--timeout 90` | 单次请求超时秒数，默认 90 |
| `--retries 2` | 失败后的最大重试次数，默认 2 |
| `--output-dir 路径` | 覆盖自动结果目录；不同配置不要混用目录 |
| `--live-interval 15` | 实时快照更新间隔秒数，默认 15 |
| `--swanlab-mode disabled` | 关闭云端记录；也可选 `cloud` 或 `offline` |
| `--summary-only` | 只从已有缓存重建报告，不调用裁判 |

API 裁判不使用 CUDA，增加显卡数量不会提速。并发不减少请求数量或费用；频繁遇到 429 时先降低到 4 或 2。

粗略耗时为 `未缓存请求数 × 平均请求耗时 ÷ 并发数`，还要加限流、重试和收尾时间。例如 1000 次请求、平均 20 秒、8 并发，理想约 42 分钟；这不是完成时间保证，应以小样本测速为准。

1500 是请求次数上限，不是 token 或金额预算，也不保证足够完成所有重试。达到预算会保存已完成结果，以退出码 2 结束；再次启动可继续。

## 5. API 与 SwanLab 配置

`run_quality.sh` 已配置中转地址 `http://43.159.131.189:8080/v1`、Responses 接口、`gpt-5.5`、推理强度 `low`、`store=false` 和最多 4096 输出 token。密钥从 `text_quality/.relay_api.key` 读取，不需要修改 Codex 设置。

密钥文件已被 Git 忽略，不要放入报告或命令行参数。更换服务可追加 `--base-url`、`--judge-model`、`--api-key-file`，并使用新的输出目录。当前 HTTP 地址会明文传输密钥和文本；`store=false` 不能保证中转站不记录。程序保留返回的模型标识，但不能独立验证中转站实际使用的模型。

### SwanLab 实时记录

脚本默认开启云端记录，项目为 `easyGAD-wm`，每份输入对应独立实验，启动时会输出实验链接。

SwanLab 密钥与裁判 API 密钥不是同一个。脚本读取 `scripts/train/run_full_gad_optimized.sh` 中已有的字面量 `SWANLAB_API_KEY`，不会执行训练脚本。也可通过环境变量 `SWANLAB_API_KEY` 或 `--swanlab-key-file` 覆盖。

记录内容包括累计质量评分、有效样本数、覆盖率、顺序一致率、请求进度、耗时和粗估 ETA。默认约每 15 秒更新，结束时强制更新；均分仅纳入完成两次顺序评分的题目。

同一输出目录续跑会使用 `swanlab_state.json` 中的实验 ID，接着追加云端曲线。不要随意删除这个文件或更换同目录的项目、workspace。云端连接异常会警告，本地评测缓存和实时记录仍保留。服务器环境已有 `tqdm` 与 `swanlab`；无费用检查不会创建实验。

## 6. 结果位置与实时查看

默认目录规则：`text_quality/results/<输入文件名去掉.jsonl>__api_gpt-5.5/`。

例如 GAD 写入 `text_quality/results/kgw_gad_qwen2_5_0_5b_dolly15k_test__api_gpt-5.5/`：

```bash
# 最终报告或最近一次汇总
cat text_quality/results/kgw_gad_qwen2_5_0_5b_dolly15k_test__api_gpt-5.5/report.md
# 运行中的最新进度与累计评分
cat text_quality/results/kgw_gad_qwen2_5_0_5b_dolly15k_test__api_gpt-5.5/live_status.json
# 最近的实时历史
tail -n 1 text_quality/results/kgw_gad_qwen2_5_0_5b_dolly15k_test__api_gpt-5.5/live_metrics.jsonl
```

| 文件 | 内容与保存方式 |
|---|---|
| `report.md`、`metrics.json` | 最新报告与机器可读指标，续跑后更新 |
| `per_sample.jsonl` | 最新逐题结果、评分与简短理由 |
| `references.jsonl` | 本次使用的人工参考 |
| `cache.jsonl` | 成功且有效的请求结果，追加写，用于断点续跑 |
| `errors.jsonl` | 错误日志，追加写（发生错误时） |
| `manifest.json` | 输入及评分配置指纹，不含密钥 |
| `results_index.jsonl` | 每次结束/汇总的运行索引，追加写 |
| `runs/<run_id>/` | 各次报告与指标快照，后续运行不覆盖 |
| `live_status.json` | 最新实时快照 |
| `live_metrics.jsonl` | 实时指标历史，追加写 |
| `swanlab_state.json`、`swanlog/` | 云端续跑状态及 SDK 日志 |

顶层文件是“最新视图”，历史结果通过追加索引和独立快照保留。`complete=false` 或有效题目不足 500 表示部分评测，不能当作完整结果。失败或只完成一次顺序的题目不会按 0 分加入均值。

## 7. 中断续跑与重新汇总

按一次 Ctrl+C 会停止发起新请求，等待在途请求返回或超时，保存已有结果。不要连续强制中断。每次有效请求成功后即追加保存缓存；强制杀进程可能来不及写最终报告，但已保存缓存仍可复用。

再次执行原命令即可续跑。输入、标签、参考、裁判、地址和评分配置要保持一致；并发与本次请求预算可以调整，`--limit 5` 也可以去掉扩展到全量。更换输入内容或评分设置应使用新结果目录。

仅从缓存重新汇总、完全关闭网络记录：

```bash
bash text_quality/run_quality.sh \
  --input-file wm_test/kgw_gad_qwen2_5_0_5b_dolly15k_test.jsonl \
  --summary-only --swanlab-mode disabled
```

这会更新最新报告并追加一次汇总索引，不是新的独立实验。不要加 `--run-api`，也不要删除缓存。若原运行指定了 `--output-dir` 或其他评分设置，汇总命令要同样指定。

不能同时启动两个进程写同一结果目录。异常退出留下 `.evaluation.lock` 时，先确认锁中的 PID 对应任务已结束，才处理自己这个目录的残留锁；不要停止其他人的进程。

## 8. 常见问题与代码入口

- 参考匹配失败：核对 ID、prompt 和 context，使用对应 test 数据生成的回答，不要跳过检查。
- 网络超时：检查本地代理、SSH 隧道和当前终端的代理变量；不要先增加重试堆积请求。
- 401/403：核对裁判 API 密钥、余额与模型权限；SwanLab 密钥不能用来调用裁判。
- 429：降低 `--concurrency`，稍后从缓存续跑。
- 输出目录配置不匹配：使用新目录，不要删除旧索引或修改 manifest 强行复用。
- JSON 格式不支持：默认严格 JSON Schema；兼容服务可显式使用 `--response-format json_object`，使用新的结果目录，不会自动降级。

代码入口：`evaluate_quality.py`（评测、缓存、汇总）、`run_quality.sh`（当前默认启动脚本）、`prepare_dolly_references.py`（参考核验）、`live_monitor.py`（进度与 SwanLab）。本地 GPU 裁判保留在 `run_local_quality.sh` / `local_judge.py`，是显式可选工具，不是本文默认流程。

离线测试与脚本语法检查，不调用真实裁判：

```bash
python -m unittest discover -s text_quality -p 'test_*.py' -v
bash -n text_quality/run_quality.sh
```
