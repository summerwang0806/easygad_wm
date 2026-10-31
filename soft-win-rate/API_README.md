# API 固定参照文本质量评测

入口为 `run_api_soft_win_rate.py`。本地只需 Python 标准库和已有项目文件，不加载 Qwen3 权重、不查询 GPU、不启动 vLLM，也不需要安装 OpenAI SDK。

复用 `text_quality/evaluate_quality.py` 的 HTTP 客户端和代理处理；评分提示与统计逻辑复用 `run_soft_win_rate.py` 的纯函数。两份原评测程序的入口都不会被执行。默认沿用 `text_quality/run_quality.sh` 中的中转地址、`gpt-5.5`、Responses API、`reasoning.effort=low`、4096 输出 token 和 `store=false`。本入口的新密钥独立保存，不回退到旧 `text_quality` 账号。中转返回的模型标识会保存，但程序不能独立验证中转站实际使用的模型。

## 直接运行

日常只修改脚本顶部的 `INPUT_JSONL`，当前已设为待补测的：

```python
INPUT_JSONL = ROOT / "wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.jsonl"
```

在服务器项目根目录运行：

```bash
python soft-win-rate/run_api_soft_win_rate.py
```

**这个命令会真正提交题目和回答到配置的 API，并可能产生费用。** 先验证 1 个实际待评判断，成功并写入缓存后才启动默认并发 4；不会额外购买一条合成健康检查。每次请求超时 120 秒、最多重试 2 次，每轮执行最多发出 1500 次请求（含失败与重试）。500 道题在没有缓存时正常需要 1000 次请求。1500 是请求次数上限，不能解释为金额或 token 上限。首次判断重试后仍失败，会停止全量队列，而非再把所有文本逐条试一遍。

新密钥读取位置为 **`soft-win-rate/.api_judge.key`**，文件里只放一行密钥，不放 JSON、引号或 `OPENAI_API_KEY=`。该文件已加入 Git 忽略，需单独同步到服务器同一路径。配置的密钥文件缺失或为空会直接停止，不自动改用旧文件或环境变量。仅当你显式把 `API_KEY_FILE` 改为 `None` 时，才从 `OPENAI_API_KEY` 环境变量读取。

密钥不写入源代码、日志或结果。更换服务时修改顶部的 `API_BASE_URL`、`JUDGE_MODEL`、`API_STYLE`、`API_KEY_FILE` 等常量。密钥和评测文本会发往 `API_BASE_URL`；当前地址的 HTTP 协议沿用旧配置，可按服务方提供的 HTTPS 地址更新。启动时显示接口、模型和密钥文件路径，不显示密钥内容。

沿用 Python 的代理环境变量。若服务器仍需要此前的 SSH 代理隧道，保持旧 API 评测时相同的网络配置即可。

后台运行：

```bash
nohup python -u soft-win-rate/run_api_soft_win_rate.py >> soft-win-rate/api_soft_win_rate.log 2>&1 &
tail -f soft-win-rate/api_soft_win_rate.log
```

## 评分口径

固定参照仍是：

```text
wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl
```

每题把待测回答与这个 clean 学生回答匿名给裁判，再交换 A/B 顺序评判一次。裁判输出 `winner=A/B/tie` 和简短 `reason`，不输出原 `text_quality` 的五维打分，也不会改用 Dolly 人工参考或额外生成参考。

- 主指标：每轮胜=1、平=0.5、负=0；先平均同题双顺序，再对所有完整题目取平均。
- 同时报告“胜＋平比例”，对应平局计满分的口径；与半平局胜率分开标注。
- 报告胜/平/负、95% 成对题目 bootstrap CI、双顺序一致率、覆盖率及有效题目数。
- 拒答、截断、解析失败不算平局。缺少任一顺序的题目不进入主指标，保留已成功的那一轮以供续跑。
- 50% 不是正确率。只更换了调用后端也不代表两个裁判的数值可直接混用；比较四种方法时应使用同一 API 裁判、参照、提示和请求配置。

请求采用完整问题和完整回答，不在本地截断，没有本地 8192/16384 窗口或显存限制。远程服务的上下文上限、输出预算、速率限制和账号额度仍然有效。Responses 结构化输出使用 `text.format`，Chat Completions 使用 `response_format`，依据 [OpenAI 官方结构化输出文档](https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses)；第三方中转的兼容情况需以实际运行确认。

## 保存与续跑

- `soft-win-rate/api_soft_win_rate_history.md`：每次运行追加主指标、胜＋平比例、置信区间、输入及参照指纹、文本生成配置、API 配置及返回模型标识。
- `soft-win-rate/results/api/<输入名>.<协议哈希>/judgments.jsonl`：每次成功判断立即 flush/fsync，一行一条，包含题目 ID、A/B 顺序、原始输出、判定、0/0.5/1 分、理由、请求耗时、使用量及响应 ID。
- 同目录 `tasks.jsonl`：完整匿名裁判输入；`manifest.json`：输入/参照/API/提示的协议指纹。
- `runs/*.json`：每次运行独立归档，`per_sample` 包含每题两轮数值分和该题平均分。
- `errors.jsonl`：失败判断的 ID、顺序、尝试次数和错误类型；不输出提供方可能包含敏感文本的 HTTP 错误正文。

API 缓存与本地 Qwen3 缓存分开。换模型、接口、提示、输入或参考会生成不同缓存；调整并发、超时、请求预算或先 `--limit` 试跑不改变已有成功缓存。改变 API 密钥也不会强制重算同一协议的成功判断。

再次执行原命令会只补缺失判断。Ctrl+C 后停止新请求，让已在途的回复写入缓存再退出（最多需等待一次请求超时）。身份验证错误、明确额度耗尽或本轮请求次数用尽会停止新请求，成功判断仍保留。完成首次验证后的普通单题失败按有限次数重试，失败不记平局。

HTTP 429 使用共享的 HTTP 请求入口处理：全部线程共同冷却，默认从 30 秒指数退避，尊重 `Retry-After`（支持秒数和 HTTP 日期）；之后整个本轮保持实际 HTTP 并发 1、请求启动间隔至少 5 秒。单个判断重试耗尽仍是 429，或全局连续 429 达阈值时停止新请求，避免换下一条文本继续重复。服务端要求的等待时间超过自动等待上限时直接停止，不提前重试。迟到的旧请求成功仍保存，但不能提前解除新的全局冷却。

日志只给出安全的提供方 `code/type` 和固定类别，不输出原始错误正文或密钥。类别包括速率限制、额度/余额/支出上限、可用通道不足、单次请求超过 TPM、未知 429；单凭 429 不推断需要充值。若提示 `provider_reason=all_upstream_accounts_rate_limited`，表示中转返回“所有可用上游账号均限流”，应等待通道恢复或联系服务方。运行参数不改变评分缓存身份。

使用量只汇总成功缓存的记录，包含复用判断；未返回或失败请求的提供方计费不能从这些记录完整推断，不应把该汇总当作账单。

## 可选检查

```bash
# 只检查数据与配置，不读取密钥、不联网、不写结果
python soft-win-rate/run_api_soft_win_rate.py --check-only

# 每次只测试前 5 题；后续全量执行会复用判断
python soft-win-rate/run_api_soft_win_rate.py --limit 5

# 仅从 API 缓存追加汇总，不读密钥、不调用 API
python soft-win-rate/run_api_soft_win_rate.py --summary-only
```

默认运行不需要追加上述参数。2026-10-30 的新密钥现场验证共发出 2 次真实请求：一次使用本入口，一次使用原 `text_quality` 客户端和评分格式，均收到 429；原格式返回的具体消息为“所有可用上游账号均处于限流”。因此该次没有得到有效评判，不能认定真实服务已调用成功。现场记录保存在本地忽略的 `results/api_connection_checks/`。
