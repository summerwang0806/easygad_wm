# Reading mode 检测

入口：`python new_detect/run_reading.py`。按 `new_detect/experiments.json` 的原始结果记录，
读取准确的 checkpoint、gamma/key、WN 规则和强度，覆盖五组 warmup/GAD、两个 WN 和 base 对照。
原有黑盒入口保持独立。

默认现为 `--protocol official`：按作者固定版本打乱、拼接教师文本后切完整256-token块，
使用原始`torch.topk(k=1)`和原始预测位置切片。协议逐项核对及必须披露的适配见 [READING_PROTOCOL.md](READING_PROTOCOL.md)。
旧按回答切段实现保留为 `--protocol documents` 敏感性分析，两个模式的结果及缓存不混用。

**正式结果需要在服务器运行。** 当前本地只有 CPU PyTorch，没有 CUDA、Transformers、学生权重或教师 tokenizer。
已有回答及旧 z/p 不能恢复模型在教师上下文中的预测。首次需加载学生权重，依次运行各 checkpoint，不加载教师模型。

## 一次运行

在服务器项目根目录，使用原 `wm` 环境：

```bash
cd /shared/wwx/EasyGAD
conda activate wm

# 核对输入、准确模型路径、权重是否存在，以及本机环境；不加载模型。
python new_detect/run_reading.py --preflight

# 先检查一组的端到端流程；limit=8 只是运行检查，不作为正式实验结果。
CUDA_VISIBLE_DEVICES=0 python new_detect/run_reading.py \
  --experiments kgw_gad --limit 8

# 全部实验，默认500条教师测试回答，1k/2k/3k预算。
CUDA_VISIBLE_DEVICES=0 python new_detect/run_reading.py

# 同一全量运行也可用封装脚本，GPU 0 替换为可用卡。
CUDA_VISIBLE_DEVICES=0 bash new_detect/run_reading_all.sh
```

GPU 0 替换为当前可用卡。依赖原环境 `torch`（CUDA）、`transformers`、`scipy`、`pyarrow`，
不使用 vLLM。默认 batch=1、float16、attention span=256、probe seed=0。Qwen2.5-0.5B 逐个加载；
可显式使用 `--batch-size 2` 或 `--dtype bfloat16`，这些设置记入结果及缓存，改变精度可能改变top-1，正式对比须统一。

默认模型根目录是当前项目的 `checkpoints/`，默认 base 是 `/shared/public_models/Qwen2.5-0.5B`。
默认教师 tokenizer 是 `/shared/public_models/Qwen2.5-14B-Instruct`。
路径不同用 `--checkpoint-root`、`--base-model`、`--tokenizer` 覆盖。

## 准确的实验映射

只使用原 JSONL 的 `model_path`，不按目录名猜测最新 checkpoint。以下路径均相对于 `checkpoints/`，
每个阶段末尾均为 `global_step_1813/actor/huggingface`：

| 清单名称 | 实验目录 | 阶段 |
|---|---|---|
| clean_warmup / clean_gad | gad_05b_cleanwarmup_cleangad_control | warmup / gad |
| kgw_warmup / kgw_gad | te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_new | warmup / gad |
| cleanD_kgwSFT_warmup / cleanD_kgwSFT_gad | cleanD_kgwSFT_kgwGAD_v1 | warmup / gad |
| dipper_warmup / dipper_gad | te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_new1_dipper2stage | warmup / gad |
| kgwD_paraSFT_warmup / kgwD_paraSFT_gad | kgwD_paraSFT_paraGAD_v1 | warmup / gad |
| wn_2_5 / wn_3 | te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_new | gad |

如果这些历史 step 的已合并 Hugging Face 权重已经删除，只能显式选择其他 checkpoint 做新实验，
不能把新 step 的结果当作原表对应值。可用 JSON 文件指定精确覆盖：

```json
{"kgw_gad":"/actual/checkpoints/experiment/gad/global_step_1813/actor/huggingface"}
```

通过 `--model-overrides /path/overrides.json` 传入。要一起替换 WN 对应权重，也需列出 `wn_2_5`、`wn_3`。
结果同时记录旧结果来源和实际加载路径，避免混淆。

默认与旧表一样使用 `base` 为ROC负对照。采用匹配的clean训练学生，可另跑：

```bash
CUDA_VISIBLE_DEVICES=0 python new_detect/run_reading.py \
  --experiments kgw_gad --reference clean_gad
```

warmup 对照可选 `--reference clean_warmup`。不同reference结果分别标注。
全量运行还自动在报告中补充同阶段 `clean_warmup` / `clean_gad` 的ROC比较。
预检要求已合并HF权重，并检查shard index所列分片是否完整。

## 读取什么数据

原 `wm_test/wn` 的13份JSONL用于实验映射、500个测试ID/顺序及配置审计，
**Reading输入是所有模型共用的原教师水印回答**：

```text
data/dolly15k_qwen2_5_14b_kgw_gamma0.5_delta3_newtest.parquet
field = teacher_response
```

这500个ID与原始教师 `...delta3_newtrain.parquet` 的14511个ID不重叠。
输入只使用教师回答文本，`add_special_tokens=False`，不额外套chat template或添加BOS/EOS。
教师文本保持固定，预测token不接回输入。默认official协议先按源文件顺序读取，用Python
`Random(0).shuffle`打乱，再无分隔拼接，切成完整256-token块；不足整块的尾部丢弃。
每块独立前向，不携带上一块KV。忠实保留官方k=1切片：首个窗口是`x[1]`，配对
`logits[1]`预测的token，最后窗口是`x[L-2]`，故每块有L-2=254个候选位置。
输入可跨教师回答边界，这与官方TextDataset一致；缓存记录块来源ID和流偏移。
`--protocol documents`才按回答分别切段、保留至少2-token短尾、从`x[0]`开始检测。
两种协议都检查所有模型读取的token块完全一致。布局/丢弃输入量写入summary.json的layouts。

`--probe /path/data.parquet`（也支持JSONL）、`--probe-field`可选其他教师水印文本。
程序检查字段和ID；自定义文本的实际gamma/key/delta需由实验者保证匹配，不能从文本自动证明。
默认 `--probe-split heldout` 拒绝与原教师训练ID重叠；如故意检测已知训练文本，使用
`--probe-split supervised`，结果会标明训练内探测。ID不重叠不等于完成近重复检查，
也不保证与所有变换后的训练语料不重叠。默认不裁剪回答；`--max-probe-tokens`可显式截短并记录。

## tokenizer、绿名单和去重

加载teacher及checkpoint tokenizer，检查完整token-ID词表和全部实际探测文本的编码一致性。
不根据tokenizer文件字节相同与否代替语义检查。若ID或编码不同，停止；此实现不提供跨tokenizer概率投影。
official协议在完整模型输出层使用原dtype的`torch.topk(k=1)`，包括其并列选择行为；
若预测词表外padding ID则停止，避免悄悄改选其他token。documents协议排除padding行后取argmax。

使用项目原 `wm_data.kgw.KGWLogitsProcessor` 的 CUDA `simple_1` 绿名单，gamma=.5、delta=3、key=15485863。
delta仅为水印配置；检测时不给模型额外加KGW。零假设命中概率使用实际绿名单大小/词表大小，
即 `max(1, floor(V*gamma))/V`，奇数词表时不恰好等于.5。

窗口长度k=1。official模式按作者target=x[1:]循环维护attention tape：从x[1]开始，
窗口在该块更早已扫描窗口中出现则排除，x[0]不进入这个tape；这是原代码的索引约定。
documents模式从x[0]开始。当前窗口自身不算重复；规则不因预算分组重置，只随实际attention块重置。
随后对 `(教师窗口token, 学生预测token)` 去重。

- 逐单元：official为完整attention块，documents为一条教师回答；单元内使用一个pair去重集合。
- 固定预算组：每组使用独立集合，组与组之间重置。
- 全语料单次检验：所有回答使用同一个全局集合，包含最后不足预算组的尾部。

读取256-token段是计算协议；1k/2k/3k是统计预算，两者不是同一概念。
预算数的是过滤前的候选预测位置，例如official的256-token块提供254个候选位置（documents为255）。
另报实际读取token数、候选数、过滤后的有效N、attention重复和全局重复剔除数。
k=1严格过滤后有效N可能远小于预算，不能用原始token数代替N提高显著性。

## WN的两种含义

两个WN结果没有新权重：它们使用同一个 `kgw_gad` checkpoint，只在推理时用不同强度逆向偏置。
因此输出明确区分：

| 结果名 | 含义 |
|---|---|
| wn_2_5 / wn_3（intrinsic） | 原始权重的Reading，与相同checkpoint的kgw_gad应一致；预测缓存复用 |
| wn_2_5_adjusted / wn_3_adjusted | 教师固定上下文下，先施加旧WN规则/强度，再取top-1；是受攻击推理行为的适配评估 |
| base_wn_control_2_5 / base_wn_control_3_0 | 对clean reference施加相同WN规则和强度的匹配对照 |

`wn_adjusted` 使用现有 `VLLMInverseWatermarkProcessor` 的稀疏逆向偏置实现，
在FP32 logits上按真实教师前缀施加规则，不使用KGW秘密密钥来决定WN惩罚，也不重新估计规则或选择强度。
原始raw检测及规则调整后的检测均不进行自由采样，因此不复现旧WN采样文本。
`intrinsic`判断权重残留，`wn_adjusted`判断应用WN后的预测行为，不能混称权重已净化。

规则默认从原attack.rules_path的文件名定位到本项目 `wn/`，
核对记录中的SHA256、规则tokenizer身份和探测编码。Windows CRLF导致字节哈希变化时，
只允许将CRLF转LF后**恰好匹配原SHA256**，不忽略其他内容差异；同时记录两种哈希，不改规则文件。
规则目录不同用 `--rules` 覆盖，内容仍须匹配。原WN tokenizer位置不同用 `--wn-tokenizer` 覆盖，仍验证规则身份。

主ROC对比同WN处理的clean reference，另在JSON的`metrics_vs_unmodified_reference`中保留与原始clean的补充比较。
这些p是同一二项统计量的尾概率；WN规则本身来自模型/数据估计，其调整版本不自动继承原论文的全部统计保证，
应结合匹配clean的误报率解释。

## 输出和复用

每次创建 `new_detect/runs/reading_<时间戳>/`，或指定一个尚不存在的 `--output-dir`：

| 文件 | 内容 |
|---|---|
| preflight.json | 旧结果来源、checkpoint映射、探测来源/训练重叠、硬件/资产检查 |
| 各实验.json | 每条教师回答、每个预算组的N/G/z/p/log10(p)、剔除数量、来源ID和全语料结果 |
| summary.json | 全部实验/对照、AUROC、实际FPR及TPR、p普通中位数和算术平均数、模型/tokenizer身份 |
| summary.md | 可直接抄入表格的结果，及整体模型单次检验 |
| failure.json | 若失败，保留具体原因；修好后重新运行，已完成预测缓存可复用 |

official逐单元指标为`per_chunk`，单位是完整attention块；documents的`per_probe`才是教师探测回答。
JSON内部per_probe明细键为兼容保留，unit_definition及表格标明实际单位。
1k/2k/3k指标的单位是预测预算组。AUROC采用`-log10(p)`，TPR工作点按实际FPR不超过5%/10%选取；
它们是当前探测单元的描述性经验ROC，不是独立训练模型的检出率，也不是独立校准集确定阈值后的结果。
有效N=0的单元记为N/A并报告数量。组数不足时实际FPR分辨率有限。

计分使用包含观测值的二项右尾 `P[Binomial(N,q) >= G]`。p中位数/算术平均在概率尺度计算，
偶数中位数取中间两个p的算术平均；极小p保留科学计数形式及log10，不写成伪造的0。
汇总p不是全语料合并检验p。小p表示水印偏好证据，较大p仅表示这次未检出。

预测缓存保存在 `new_detect/cache/reading/`，包含教师输入ID、学生预测ID和CUDA绿名单命中标记。
v2与先前实现缓存隔离；protocol、probe-seed、topk/argmax选择均进入身份。
正常运行核对源内容、协议、精度、batch、torch/transformers/CUDA环境、模型配置及权重文件大小/mtime、tokenizer文件哈希。
权重未逐字节全量哈希，这个资产标识不等于完整权重内容证明。

服务器完成后，可把整个 `new_detect/cache/reading/` 复制回本地，保留相同输入与选项，再计算统计：

```bash
python new_detect/run_reading.py --from-cache-only
```

此时不加载权重/tokenizer、不调用CUDA；仍需要本地torch/scipy/pyarrow读取和汇总。
该模式检查探测内容/选项、probe ID顺序、token范围/数量和CUDA缓存来源信息，信任服务器记录的模型资产身份，
不会在本地重新验证服务器权重。若服务器改过`--dtype`、`--sequence-length`、`--limit`等，
本地传相同参数。只阅读结果时复制summary.md/json即可。

## 验证和来源

```bash
python -m unittest discover -s new_detect -p 'test_*.py' -v
```

CPU合成夹具覆盖下一token对齐、teacher forcing、attention窗口排除、跨回答/预算去重、padding、
WN与原逆向处理器一致性、heldout审计、极小p及概率尺度汇总、便携缓存和CPU统计。
合成测试不是正式实验指标；真实权重前向、CUDA绿名单及实际tokenizer一致性仍需服务器验证。

方法：[论文§4](https://arxiv.org/html/2402.14904v2#S4)、
[官方Reading实现](https://github.com/facebookresearch/radioactive-watermark/blob/main/main_reed_wm.py)。
本实现沿用项目水印PRNG，默认采用response-only、官方shuffle/拼接/完整切块的协议；WN调整是本项目扩展。
