# 已有回答的黑盒 Radioactivity 检测

只读取 `wm_test`、`wn` 的已有回答，不训练、不生成、不加载模型权重，不修改原结果。
方法参考 [Watermarking Makes Language Models Radioactive §4](https://arxiv.org/html/2402.14904v2#S4)，
适配本项目的 `simple_1`、gamma=0.5、hash_key=15485863、CUDA 绿名单。
这是对已有 Dolly 回答的回溯检测；没有重新生成论文中的主动探测问题，不能称为完整实验复现。

## 一次运行全部实验

在服务器 EasyGAD 根目录、原 `wm` 环境中运行：

```bash
conda activate wm
python new_detect/run_blackbox.py --preflight
CUDA_VISIBLE_DEVICES=0 python new_detect/run_blackbox.py
```

GPU 0 请替换为可用卡。无需 vLLM，也无需载入任何 checkpoint 权重。
依赖原环境的 `torch`（CUDA 版）、`transformers`、`scipy`、`pyarrow`。
默认教师 tokenizer：`/shared/public_models/Qwen2.5-14B-Instruct`。
对话提示默认用记录的生成 tokenizer 恢复（普通结果用 `model_path` 目录下 tokenizer，WN 用已记录 tokenizer 路径）。
因此 checkpoint 目录只用到 tokenizer 文件，不读取权重。

若所有实验的实际生成 tokenizer 确实相同，可显式指定公共 tokenizer，避免依赖多个 checkpoint 目录：

```bash
CUDA_VISIBLE_DEVICES=0 python new_detect/run_blackbox.py \
  --tokenizer /shared/public_models/Qwen2.5-14B-Instruct \
  --generation-tokenizer /shared/public_models/Qwen2.5-0.5B
```

只有确认公共 tokenizer 的模板和编码与原生成设置相同才使用此覆盖。旧版 base 生成曾复用学生 tokenizer，
单凭 base 的 model_path 不能证明原模板。程序复现原截断策略，并逐条校验回答长度、原始绿 token 数；
不一致立即停止。WN 还校验保存的实际 prompt token 数。校验不是所有模板内容一致性的数学证明。

## 文件选择

`experiments.json` 显式列出 13 个输入：5 组各 warmup/GAD、2 个 WN、1 个原始 base。

| 名称前缀 | 用户实验 | 选择依据 |
|---|---|---|
| clean | cleanwarmup_cleangad | gamma0.5 文件 |
| kgw | kgwwarmup_kgwgad | delta3_new；GAD 原 AUROC=0.647688 |
| cleanD_kgwSFT | kgwwarmup(cleanD-kgwSFT)_kgwgad | cleanD_kgwSFT 文件 |
| dipper | dipper_para-kgwwarmup_dipper_para-kgwgad | delta3_new1；GAD 原 AUROC=0.531456 |
| kgwD_paraSFT | para-kgwwarmup(kgwD-paraSFT)_para-kgwgad | 文件名虽为 cleanD_dipperparaSFT，model_path 为 kgwD_paraSFT_paraGAD_v1 |
| wn_2_5 / wn_3 | 两个 WN | 校验 attack.strength=2.5/3.0 |

不自动混入旧 delta3、delta2 或 gad1500 结果。默认与原表相同，使用 base 为负对照。
clean 文件旧 label 也可能是 kgw；实验角色以清单为准。clean 的 delta=2 元数据保留，
因为 delta 不参与检测公式；水印/攻击组严格要求 delta=3。所有输入严格要求 gamma=0.5、相同 key 和 simple_1。

可以单独试跑一组（会自动包括 reference）：

```bash
CUDA_VISIBLE_DEVICES=0 python new_detect/run_blackbox.py --experiments kgw_gad
```

采用经过 clean 训练的模型为负对照可另跑：

```bash
CUDA_VISIBLE_DEVICES=0 python new_detect/run_blackbox.py --reference clean_gad
```

不要把两个对照下的 ROC 混在一列；warmup 的匹配对照可以指定 `--reference clean_warmup`。

## 两个默认检测版本

默认 `--filter-mode both`，同批回答同时输出：

1. `dedup`：排除 prompt 中出现过的上下文窗口，再对 `(previous_token, token)` 去重。
2. `teacher_filtered`：额外保留教师原始水印训练文本中出现的上下文窗口。

默认教师窗口语料是 `data/dolly15k_qwen2_5_14b_kgw_gamma0.5_delta3_newtrain.parquet`，字段 `teacher_response`。
该语料只用于构建过滤器，不加载教师模型。所有实验共享过滤器，便于比较；这不宣称每个学生都见过同一份原始训练文本。
程序拒绝教师过滤语料与评估集 ID 重叠。k=1 时窗口为单个 token，过滤可能较宽松；保留率和剔除数量会记录。
默认窗口出现至少 1 次，可预先固定 `--filter-min-count`，不要根据测试结果反复选最优阈值。
自定义过滤器可指定 `--teacher-filter`（parquet/JSONL）和 `--teacher-field`。
仅严格去重版本：`--filter-mode none`，不需要教师语料或 pyarrow。

## 检测单位与统计口径

- **逐回答**：每条回答单独检验，保留原表的回答级比较口径，但检测分数已改变。
- **1k/2k/3k**：按 reference 文件的样本顺序累计回答 token，精确切成互不重叠的预算组，丢弃不足一组的尾部。
  预算指过滤前 token 数；不把不同回答拼成虚构上下文。分组切入某条回答中间时，保留其真实前一个 token。
  每组作为一次检测，组内跨回答全局去重；下一组重置去重集合。这些组不是独立训练模型，且组间可能重复同一 token 对。
- **全语料**：另建一个贯穿所有回答的去重集合，包含尾部，输出单次模型级检验。不能把组 p 简单平均当作整体 p。
- k=1 时，任何在该回答原始 prompt 中出现的上下文 token 都排除，包括首个回答 token 对应的窗口。
  不剔除整条“严重重复回答”，由 token 对去重控制重复贡献，避免改变实验样本总体。

计分使用本项目原始 CUDA 绿名单，不使用论文默认哈希算法。
零假设概率使用真实绿名单比例 `floor(vocab_size * gamma)/vocab_size`（Qwen 词表若为奇数，不恰好等于0.5）。
给定有效 N、命中 G，使用包含观测值的二项右尾 `P[Binomial(N,q) >= G]`，而非正态近似。
极小 p 以科学计数字符串保留，同时始终提供 log10(p)，不写伪造的 p=0。
理论尾概率依赖随机绿表及近似独立性假设；固定密钥/k=1 下仍需查看 clean 实际误报。

AUROC 和 TPR 用 `-log10(p)`；正负组数可不同，分数并列整体处理，不插值到不存在的 FPR。
TPR@FPR≤5%/10% 是这批数据的描述性经验 ROC，输出实际 FPR、阈值、TP、FP、样本数。
不声称阈值已在独立校准集选取。零有效 N 记 N/A 并排除统计，明确报告有效组数。
p 均值为算术平均；偶数组中位数为中间两个 p 的算术平均，均在概率尺度计算。
log10 字段表示这些汇总概率的对数，不是各组 log10(p) 的均值。
各预算另报 p≤0.05、p≤1e-5 的组比例；clean 的这些比例用于误报诊断。
组数量太少时，5% FPR 分辨率有限，应查看负样本组数和实际 FPR。

## 输出与本地再计算

每次运行创建独立 `new_detect/runs/<时间戳>/`：

- `preflight.json`：实验映射、源 SHA256、配置、数量、本地运行条件。
- `<实验>.<模式>.json`：逐回答/逐组明细、组对应回答 ID、过滤计数、尾部数量和全语料结果。
- `summary.json`：全部 ROC、p均值/中位数、对照、输入及 tokenizer 指纹。
- `summary.md`：可直接阅读的汇总表。

使用 `--output-dir` 可指定一个空目录；拒绝覆盖既有运行。
首次在 CUDA 上生成 `new_detect/cache/*.tokens.json`，保存每条回答的真实 token 对和绿名单标记。
缓存按源内容、tokenizer 文件、torch 版本和协议校验，不复用旧的 p-value 汇总缓存。

将整个 `new_detect/cache` 复制回本地（保持原 JSONL 和教师语料相同），便可不依赖 CUDA/transformers/tokenizer 目录重新汇总：

```bash
python new_detect/run_blackbox.py --from-cache-only
```

此模式依赖服务器记录的 tokenizer/CUDA 计算及其指纹；本地不重新验证 tokenizer 文件。
它校验源 SHA256、协议、token 范围/数量和原始绿 token 总数，缺少/失效缓存时报错，不回退到 CPU 绿名单。
缓存可能较大；只需阅读结果时复制 `summary.md` 和 `summary.json` 即可。

当前本地检查：13 个源文件、6500 条回答可读，配置/ID/prompt 检查通过；CPU PyTorch，无 CUDA、transformers 和教师 tokenizer。
因此尚未产生真实新检测指标。服务器首次运行无需模型权重，但需要正确的 tokenizer 文件及 CUDA。

## 验证

```bash
python -m unittest discover -s new_detect -p 'test_*.py' -v
```

测试覆盖二项右尾、极小 p、概率尺度均值/中位数、prompt 排除、跨回答去重、预算边界、尾部、ROC并列/误报约束、
缓存失效和 CPU 汇总完整流程。测试使用合成 token 夹具，不是实验结果；真实 CUDA/教师 tokenizer 一致性须在服务器验证。
