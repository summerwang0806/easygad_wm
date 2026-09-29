# EasyGAD 文本质量评测：原始 0.5B / warmup / GAD

本目录只读取已经生成的文本，不加载学生模型，不使用 GPU、Ray 或 SwanLab，不改变 checkpoint。
评测默认裁判为你选择的 **GPT-4o**。需要单独的模型 API 密钥，SwanLab 密钥不能用在这里。
Python 3.10+，只使用标准库，无需 pip 安装评测依赖。

服务器 `/app/wwx/EasyGAD` 实际指向 `/shared/wwx/EasyGAD`，两个路径访问的是同一份项目。

## 文件

- `evaluate_quality.py`：数据检查、参考回答生成、双顺序评分、缓存、汇总和置信区间。
- `run_quality.sh`：启动包装脚本，默认只检查，不调用 API。
- `test_evaluate_quality.py`：模拟接口的离线测试，不使用真实密钥或外部网络。

## 默认读取的已有结果

| 标签 | 项目根目录下的文件 |
|---|---|
| base | `wm_test/base_qwen2_5_0_5b_dolly15k_test.jsonl` |
| warmup | `wm_test/kgw_warmup_qwen2_5_0_5b_dolly15k_test.jsonl` |
| gad | `wm_test/kgw_gad_qwen2_5_0_5b_dolly15k_test.jsonl` |

每行需有 `id`、`prompt`（消息列表或文本）和 `answer`。直接兼容 `generate_compare_score.py` 的输出。
模型文件顺序可以不同：按 ID 对齐；但 ID 集合、同题 prompt 必须一致，不会静默取交集。
`generation` 参数不一致默认报错；确实要比较不同设置时显式加 `--allow-generation-mismatch` 并如实报告。
若所有文件都没有 `generation` 字段，无法自动确认生成参数，需自行核对。
源文件里的水印分数、KGW 标签和模型路径不会交给裁判。

## 模式及指标

### paper：论文式参考回答评分（默认）

为每个问题生成一份 GPT-4o 参考回答，固定缓存，然后分别比较各模型回答与该参考。
裁判给 helpfulness、relevance、accuracy、detail 和 overall 各 1～10 分。
每次比较都交换 A/B 顺序再评一次，将结果映射回原模型后汇总。

每条样本的相对分数是两个顺序下 `100 * 模型overall / (模型overall + 参考overall)` 的平均，最后再对样本取平均。
50 表示模型与参考评分相等，**不是 50% 正确率**。
输出每个模型的相对分数、分维度均值、95% bootstrap 区间，以及相同问题上模型之间的相对分差。
模型间分差是分别对同一参考评分后的配对差值，不等同于直接两模型对战胜率。

采用原论文的参考回答比较与归一化公式；增加了 JSON 输出、细分维度、双顺序和缓存，
而且当前文件的生成温度为 0.7，论文最新版使用贪心生成。因此这是**论文式评测扩展，不是原论文结果的严格复现**。
裁判和参考回答都不是真实事实验证器，需要人工抽样核查；裁判为自己生成的参考打分也可能有偏差。

### pairwise：直接检验 GAD 是否比 warmup 更好

默认比较 `gad:warmup`，不生成参考回答，裁判看匿名 A/B 回答，交换顺序各评分一次。
按两次评分平均后的 overall 比较，输出 GAD 胜率、平率、warmup 胜率、overall 分差、
胜率+半平率及其区间、两次展示顺序的结论一致率。
平局是两份回答平均 overall 相等，并非把平局算作 GAD 胜利。顺序一致率低时要人工复核。

这更直接回答本次 warmup→GAD 是否改善质量。论文式评分与直接对战结果必须分开报告。
字符数、token 数和空回答数量只是描述性指标，不证明质量提升。
bootstrap 区间按 prompt 重采样，不覆盖裁判系统误差、训练随机种子或参考回答偏差。

## 第一步：无费用检查

```bash
cd /app/wwx/EasyGAD
conda activate wm
bash text_quality/run_quality.sh
```

默认不写结果、不发请求、不需要 API 密钥。三模型各 500 条时 paper 上限为 3500 次逻辑调用：
500 次参考回答 + 3 模型 × 500 条 × 2 个顺序。成功缓存可减少后续调用，重试会增加实际调用。
pairwise 的 GAD/warmup 全量是 1000 次逻辑调用。两种模式请使用不同输出目录。

## 第二步：设置 API 密钥与网络

```bash
read -rsp 'OpenAI API key: ' OPENAI_API_KEY
echo
export OPENAI_API_KEY
export OPENAI_BASE_URL=https://api.openai.com/v1
```

上述方式不把密钥写进 shell 历史或报告。若使用自己的兼容服务，将 `OPENAI_BASE_URL` 改为其 `/v1` 地址；
但服务必须真实提供你选择的 GPT-4o，脚本不会验证服务商是否替换了模型。
默认严格 JSON Schema；兼容服务不支持时可显式改 `--response-format json_object`，不自动降级或换模型。
如使用 GPT-4o 固定快照，所有试跑和全量命令统一加 `--judge-model <实际可访问的快照名>`，新型号使用新结果目录。

如果服务器不能直连，先在本地代理运行且监听 56734 的前提下，建立并保持 SSH 隧道：

```powershell
ssh -R 7890:127.0.0.1:56734 -p 3389 wwx@10.107.6.60
```

在服务器同一终端设置代理；不需要代理时不要设置这些变量：

```bash
export http_proxy=http://127.0.0.1:7890
export https_proxy=http://127.0.0.1:7890
export HTTP_PROXY="$http_proxy"
export HTTPS_PROXY="$https_proxy"
export NO_PROXY=127.0.0.1,localhost
export no_proxy="$NO_PROXY"
```

**加 `--run-api` 会将题目、回答发送到所配置的服务，可能产生费用。这里没有替你实际运行 API。**
密钥有效性、账户余额、模型权限和代理可达性需要你运行时验证；ChatGPT 界面登录不代替这里的 API 密钥。

## 第三步：先试 5 条（需要真实 API，会产生费用）

论文式模式，默认三个模型，计划 35 次逻辑调用：

```bash
bash text_quality/run_quality.sh --mode paper --limit 5 \
  --output-dir text_quality/results/paper_gpt4o \
  --run-api --max-api-calls 100
```

或直接对战，计划 10 次逻辑调用：

```bash
bash text_quality/run_quality.sh --mode pairwise --pair gad:warmup --limit 5 \
  --output-dir text_quality/results/pairwise_gpt4o \
  --run-api --max-api-calls 30
```

API 调用数量不是 token 或金额预算；长题、长回答、重试均会影响费用。先检查小样本评分和账单，再决定全量。
达到预算会保存已有成功结果并以退出码 2 结束，不自动突破预算。

## 第四步：确认后全量 500 条

不指定 `--limit`，会读取全部 500 条；与 5 条试跑使用同目录、同设置，已完成的请求不会重复计费：

```bash
# 论文式三模型比较
bash text_quality/run_quality.sh --mode paper \
  --output-dir text_quality/results/paper_gpt4o \
  --run-api --max-api-calls 4000

# 或：GAD 与 warmup 直接盲评
bash text_quality/run_quality.sh --mode pairwise --pair gad:warmup \
  --output-dir text_quality/results/pairwise_gpt4o \
  --run-api --max-api-calls 1200
```

预算是每次启动的请求上限（包括失败请求和重试），第二次启动会重新计算本次预算。
再次执行相同命令即可续跑；更改输入文件、裁判、endpoint、模式或评分设置必须使用新目录。
如果只想比较 warmup/GAD，不含 base，可重复传入两次 `--model` 覆盖默认三个文件：

```bash
bash text_quality/run_quality.sh --mode paper \
  --model warmup=wm_test/kgw_warmup_qwen2_5_0_5b_dolly15k_test.jsonl \
  --model gad=wm_test/kgw_gad_qwen2_5_0_5b_dolly15k_test.jsonl \
  --output-dir text_quality/results/paper_two_models
```

上面仍是无费用检查；真正运行时另加 `--run-api` 和足够的预算。
可用 `--reference-file references.jsonl` 提供现成参考（id/prompt/answer），必须逐 ID 匹配问题并使用新输出目录。

## 看结果与重新汇总

输出目录中有：

- `report.md`：可直接阅读的比较表、完整性说明、置信区间。
- `metrics.json`：机器可读的质量指标、覆盖率、分维度评分、配对差值。
- `per_sample.jsonl`：每题两次顺序评分和简短理由，方便人工复核。
- `references.jsonl`：paper 模式的固定参考回答。
- `cache.jsonl`：已成功请求的缓存、实际返回模型 ID、token 用量；不要删除它后重新运行。
- `errors.jsonl`：失败请求的类型（若有），失败样本不会按 0 分加入平均。
- `manifest.json`：输入与评测设置指纹，无 API 密钥。

```bash
# 不调用 API，仅从已有缓存重建报告；模式和目录要与原运行一致
bash text_quality/run_quality.sh --mode paper \
  --output-dir text_quality/results/paper_gpt4o --summary-only
```

`complete=false` 或有效样本少于 500 时，结果是部分评测，不要直接与完整评测比较。
异常强制退出若留下 `.evaluation.lock`，先确认其中 PID 对应的任务已结束，才可手动移除本目录的锁；不要停止其他同学的进程。
报告没有“GAD 一定更好”的预设，允许结果为退化、持平或不确定。

现有 Dolly 测试集已用于训练期验证和挑模型，可先做探索性质量比较；正式结论应另留未参与模型选择的测试问题。
本次 0.5B 模型不能与此前 1.5B SeqKD 直接作公平模型对照。
水印 AUROC、TPR@FPR 应独立报告，本目录不把水印 z-score 当作内容质量。

## 离线测试

```bash
python -m unittest discover -s text_quality -p 'test_*.py' -v
bash -n text_quality/run_quality.sh
```

测试使用模拟裁判，并没有验证真实 API 可达性或 GPT-4o 判断是否正确。

## 依据

- GAD 论文最新版 §3.1、附录 A.3：https://arxiv.org/html/2511.10643v3
- API Structured Outputs：https://developers.openai.com/api/docs/guides/structured-outputs
- GPT-4o 模型接口说明：https://developers.openai.com/api/docs/models/gpt-4o
