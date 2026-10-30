# API 固定参照文本质量评测

入口为 `run_api_soft_win_rate.py`。本地只需 Python 标准库和已有项目文件，不加载 Qwen3 权重、不查询 GPU、不启动 vLLM，也不需要安装 OpenAI SDK。

复用 `text_quality/evaluate_quality.py` 的 API 客户端、密钥读取和代理处理；评分提示与统计逻辑复用 `run_soft_win_rate.py` 的纯函数。两份原评测程序的入口都不会被执行。默认沿用 `text_quality/run_quality.sh` 中的中转地址、`gpt-5.5`、Responses API、`reasoning.effort=low`、4096 输出 token 和 `store=false`。中转返回的模型标识会保存，但程序不能独立验证中转站实际使用的模型。

## 直接运行

日常只修改脚本顶部的 `INPUT_JSONL`，当前已设为待补测的：

```python
INPUT_JSONL = ROOT / "wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.jsonl"
```

在服务器项目根目录运行：

```bash
python soft-win-rate/run_api_soft_win_rate.py
```

**这个命令会真正提交题目和回答到配置的 API，并可能产生费用。** 默认并发 4、每次请求超时 120 秒、最多重试 2 次，每轮执行最多发出 1500 次请求（含失败与重试）。500 道题在没有缓存时正常需要 1000 次请求。1500 是请求次数上限，不能解释为金额或 token 上限。

密钥继续从 `text_quality/.relay_api.key` 读取；文件不存在时使用 `OPENAI_API_KEY`，也兼容旧客户端的默认密钥文件回退。密钥不写入源代码、日志或结果。更换服务时修改顶部的 `API_BASE_URL`、`JUDGE_MODEL`、`API_STYLE`、`API_KEY_FILE` 等常量。密钥和评测文本会发往 `API_BASE_URL`；当前地址的 HTTP 协议沿用旧配置，可按服务方提供的 HTTPS 地址更新。

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

再次执行原命令会只补缺失判断。Ctrl+C 后停止新请求，让已在途的回复写入缓存再退出（最多需等待一次请求超时）。身份验证错误、明确额度耗尽或本轮请求次数用尽会停止新请求，成功判断仍保留。普通失败按有限次数退避重试，重试耗尽后继续其余题目。

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

默认运行不需要追加上述参数。实现仅完成无网络模拟测试，尚未向真实中转发送评测请求。
