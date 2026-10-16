# TP / WN 实现细节与备用方案

实现依据：[ACL 2025 论文](https://aclanthology.org/2025.acl-long.648.pdf) §3.3–3.5，以及[官方代码](https://github.com/THU-BPM/Watermark-Radioactivity-Attack)。作者公开实现只包含 WN。正式 TP 现改用窃取阶段的原始学生模型 O 做转述，与规则使用相同 tokenizer，按 token ID 直接施加反向偏置；TP 和 WN 共用同一份规则 JSON。论文 TP 使用 Dipper，这里的同模型转述是本项目选择，解决 token ID 对齐问题，不能称为原实验的逐项复现。

原来的 Dipper 文本投影 TP 保留为独立备用入口，不参与正式 TP 训练脚本。普通 UP 仍使用 Dipper，保持原流程。

本次只编辑本地 `my_easygad`，没有 SSH、实验服务器连接、模型推理或训练。下面是代码使用说明，命令不会自动执行。模型、checkpoint 和数据路径均须换成本机实际存在的资产目录。

## 文件职责

| 文件 | 职责 |
| --- | --- |
| `steal_watermark.py` | 使用原始训练回答和学生训练前后的概率，离线估计规则 |
| `inverse_watermark.py` | TP/WN 共用的规则校验、tokenizer 身份检查、加权查表和反向 logits processor |
| `paraphrase_tp.py` | 使用原始学生 O 的因果语言模型完成全回答 TP，直接按 ID 扣分，生成新的训练 Parquet |
| `student_parallel.py` | 正式 TP 的学生模型多 GPU worker 调度，每卡一个完整模型 |
| `paraphrase_tp_dipper_backup.py` | 原 Dipper 全回答 TP 备用入口，沿用文本投影近似 |
| `tokenizer_bridge_dipper_backup.py` | 备用 Dipper 候选续写到学生规则空间的文本投影算法 |
| `../wm_test/generate_wn_score.py` | 使用参考学生 W 生成测试回答，施加 WN 反向偏置并检测回答 |
| `run_tp_gad_pipeline.sh` | TP 数据及审计校验后，调用现有 Warmup → GAD 训练流程 |
| `run_tp_gad_pipeline_dipper_backup.sh` | 旧 Dipper TP 数据校验和训练流水线，独立保留为备用 |
| `../scripts/train/run_full_gad_tp_tp_optimized.sh` | TP Warmup + TP GAD |
| `../scripts/train/run_full_gad_tp_kgw_optimized.sh` | TP Warmup + 原始 KGW GAD |
| `../scripts/train/run_full_gad_tp_*_dipper_backup_optimized.sh` | 两个备用 Dipper TP 训练分支，使用独立文件名及实验名 |

规则窃取和 TP 数据预处理放在 `baseline_acl`；GAD 训练启动器放在 `scripts/train`；测试回答生成和检测放在 `wm_test`。WN 直接调用 `wm_test/generate_wn_score.py`，作用于训练后的解码，无需修改 GAD/verl 训练器。

## 1. 规则窃取

输入是同一学生的原始基座 **O**、使用原始带水印数据且未经 UP/TP 攻击训练的 **W**，以及该原始训练集 **C**。TP 同样需要这个 W 作为规则提取的参考；最终 TP 学生再从 O 开始训练。

用于本项目 GAD 实验时，`--model-before` 传入 **Warmup 之前的原始学生模型**，`--model-after` 传入完整 Warmup → GAD 后已合并的 **actor Hugging Face 模型目录**（如 `gad/global_step_NNN/actor/huggingface`）。不要把 critic、原始 FSDP 分片目录或仅完成 Warmup 的模型作为最终 GAD W。`--input` 应与该 W 使用的原始水印训练集对应，支持项目中的 `*_train.parquet` 和 `*_newtrain.parquet` 命名。若 W 使用过 UP/TP 数据，应标明为组合攻击实验，不能当作标准无攻击参考 W。

程序只读取 `teacher_response`，不使用真实 KGW 密钥或检测器。O/W 的 tokenizer 必须在词表、token IDs、特殊 token 和分词配置上匹配，路径名称不参与身份判断。

Hugging Face 的 `save_pretrained()` 可能在无损保存 tokenizer 时补入 `extra_special_tokens: {}`，或将已经生效的特殊 token 配置重新序列化。仅哈希原始 `init_kwargs` 会把这种情况误判为不一致。当前保留原严格指纹供旧规则验证，同时为新规则记录带版本的兼容指纹：规范化空的额外特殊 token 映射及已通过实际属性校验的重复配置。词表、token ID、特殊 token、AddedToken 标志、完整分词后端、chat template 和未知配置仍需匹配；不直接跳过检查。窃取、TP 和 WN 使用同一校验逻辑。若仍有真实差异，错误会列出 `differing components` 或 `differing init_kwargs`，而不打印完整词表或模板。同步到服务器时需一起更新 `inverse_watermark.py` 和 `steal_watermark.py`；无须重新训练 GAD 模型。

已用官方 Qwen2.5-0.5B 的真实 tokenizer（151665 个 token，Transformers 4.51.3 / tokenizers 0.21.4）复现：保存后仅新增空的 `extra_special_tokens`，分词后端和测试文本编码保持一致，但旧指纹改变。新版窃取及规则消费校验均通过，实际更改 EOS 仍被拒绝。此验证未加载模型权重；服务器 checkpoint 若存在其它差异，需以新版错误中的差异项为准。

前缀频率统计对每条回答先完成 tokenizer 编码，再去掉最后一个 token（`answer_ids[:-1]`）。分别统计长度为 1、2 的前缀，每种长度使用各自的有效前缀总数作为分母，保留相对频率严格大于 `5e-5` 的前缀。这一统计边界与官方 `analyze_prefix_frequency.py` 一致。

条件前缀规则只收集回答前 200 token 范围内以该前缀结尾的非空上下文；送入模型的上下文保留此前的完整回答，不裁成尾部窗口。先收集每个前缀的全部有效上下文，超过 1000 个时才调用 `random.shuffle()` 打乱并截取前 1000 个，否则全部保留；不显式设置抽样 seed。这与官方 `calculate_d_n.py` 的选择方式一致；重复运行可能选到不同的上下文，但同一次窃取中 O/W 始终使用同一批样本。此处的随机抽样与生成水印时的 seed 无关。

全局规则 `d_0` 使用全部回答前 200 token 范围内的所有有效预测位置，不做上下文抽样，也不限制 top-50。对 O/W 的完整 next-token 概率分别求平均后，为规则 tokenizer 词表中的每个 token 计算并保存分数，包括分数为 0 的 token。这与官方 `calculate_d_0.py` 的全局评分范围一致。

模型仍顺序加载：先加载 W，平均概率；条件前缀项此时才选 W 平均概率 top-50，全局项保留整个规则词表。卸载 W 后加载 O，使用相同上下文计算对应平均概率。每个候选计算 `d = min(2, mean_PW / mean_PO) / 2`，只有 `mean_PW > mean_PO` 时得分非零，其余为 0。全局项与各前缀项按论文频率权重组合，合成 D 不额外截到 1。

默认 `n'=3`、`alpha=0.3`。窃取入口不提供 `--seed`，也不设置固定抽样 seed；TP/WN 自身的生成 seed 与此独立，仍保留。模型顺序加载避免同时占用两份模型显存。规则 JSON 保存训练数据 SHA-256、checkpoint manifest、tokenizer fingerprint、精度、抽样参数和来源；不覆盖旧规则文件。

核心统计定义与官方 `analyze_prefix_frequency.py`、`calculate_d_n.py`、`calculate_d_0.py` 和 `calculate_w.py` 对齐。工程适配包括：默认 CUDA 精度按硬件选择 BF16/FP32、FP32 softmax 与 FP64 累加、显式 padding/position IDs，以及只为真实 tokenizer token ID 保存规则（模型额外的词表填充槽仍参与 softmax 分母）。因此不保证与官方多 GPU 程序逐位一致；需要控制精度时可显式加 `--dtype float32`。论文中的 W 通过 SFT 得到，本项目以 GAD 训练 W 后应用相同窃取算法，属于训练协议适配。

以上三处已按官方实现调整；现有 Qwen 模型、项目训练协议和同模型 TP 转述仍是项目适配，不能据此宣称原论文全部实验设置已复现。窃取程序和 WN 不因此次 TP 模型切换而改变；已使用当前窃取协议产生的匹配规则可同时给 TP/WN 使用。若规则是在上述三处修正以前产生的，需要使用更新后的窃取程序重新估计并写入新的文件；已有 TP 数据或生成结果也不会被自动更新。

从项目根目录先做 CPU 预检（不加载权重，不写文件）：

```bash
python baseline_acl/steal_watermark.py \
  --input data/dolly15k_qwen2_5_14b_kgw_train.parquet \
  --model-before models/Qwen2.5-0.5B \
  --model-after checkpoints/no_attack_student/actor/huggingface \
  --preflight
```

在已具备兼容 CUDA 环境且明确选好空闲 GPU 时，实际估计命令示例：

```bash
CUDA_VISIBLE_DEVICES=1 python baseline_acl/steal_watermark.py \
  --input data/dolly15k_qwen2_5_14b_kgw_train.parquet \
  --model-before models/Qwen2.5-0.5B \
  --model-after checkpoints/no_attack_student/actor/huggingface \
  --output data/acl_estimated_rules.json --device cuda



CUDA_VISIBLE_DEVICES=3 python baseline_acl/steal_watermark.py \
  --model-before /shared/public_models/Qwen2.5-0.5B \
  --model-after checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_new/gad/global_step_1813/actor/huggingface \
  --input data/dolly15k_qwen2_5_14b_kgw_gamma0.5_delta3_newtrain.parquet \
  --output wn/acl_rules_gad_Qwen2.5-0.5B_gamma0.5_delta3_fp32.json \
  --device cuda \
  --dtype float32 \
  --batch-size 16  
```

`--device cpu` 也可执行实际估计，但仍需要 PyTorch 和模型权重；它与 `--preflight` 不同。

## 2. TP 数据预处理

正式入口的 `--model` 必须使用窃取时 `--model-before` 指定的原始学生 **O**，例如 `models/Qwen2.5-0.5B`。`--tokenizer` 可选，默认同一模型目录。程序验证模型来源和规则 tokenizer 的词表、ID、特殊 token、分词配置；不以目录名相同代替校验，也不接受任意词表相似的转述模型。

流程为：用原始水印数据 C 训练参考学生 W → 从 O/W/C 窃取规则 D → 由 O 在转述指令下改写 C，并在解码时反向扣分 → 得到 C_TP → 最终学生再从 O 开始，用 C_TP 训练。WN 则直接在参考学生 W 的生成阶段使用同一份 D；这两个入口无需再生成两套规则。

每步采样前执行 `logit -= inverse_strength * D`，默认强度 2.5，直接使用生成上下文的学生 token ID 查表。正式 TP 不使用 Dipper、T5、NLTK、候选文本投影、投影 top-k 或投影上下文窗口。转述 prompt 使用完整原回答；默认 `--prompt-mode completion` 使用纯文本转述指令，适用于原始 base 学生 O。只有模型经过 chat/instruct 训练时才适合显式选择 `chat`；`auto` 作为可选项，仅按 chat template 是否存在选择格式，模板存在本身不证明模型有对话能力。

保留完整回答一次改写、top_p=0.75、temperature=1、逐行 seed、断点恢复和严格 Parquet 数据契约。只替换 `teacher_response`，保护其余字段、schema metadata、ID 和行顺序；默认遇到失败停止，不默默保留原回答。`--max-input-tokens 4096` 限制包含转述指令的输入长度；`--max-new-tokens 4096` 仅表示新生成回答的上限，不含 prompt。程序还检查输入加输出预算是否超过模型 context window，不静默截断回答；可用 `--context-window` 指定更小的窗口上限，但不得超过模型配置的 `max_position_embeddings`。

```bash
python baseline_acl/paraphrase_tp.py \
  --input data/dolly15k_qwen2_5_14b_kgw_train.parquet \
  --rules data/acl_estimated_rules.json \
  --model models/Qwen2.5-0.5B --preflight

CUDA_VISIBLE_DEVICES=1,2 python baseline_acl/paraphrase_tp.py \
  --input data/dolly15k_qwen2_5_14b_kgw_train.parquet \
  --output data/dolly15k_qwen2_5_14b_kgw_tp_student_train.parquet \
  --rules data/acl_estimated_rules.json \
  --model models/Qwen2.5-0.5B --num-gpus 2
```

每张显式选中的 GPU 加载完整学生 O，显存不会合并。断点加 `--resume`；模型、tokenizer、规则文件内容、反向强度、转述 prompt、采样预算或原数据改变时，拒绝继续旧断点。旧 Dipper TP 断点不能在新入口继续；请使用新的输出路径。每个 worker 校验规则 SHA-256，确保使用同一份规则。默认审计文件是 `<output>.audit.json`，方法标签是 `targeted_student_paraphrasing`，其中 `cross_tokenizer=false`、`projection=null`，并记录原始学生 O 角色及 tokenizer 身份校验。

训练启动器复用现有流程，每组默认 Warmup 1 epoch + GAD 1 epoch：

```bash
# CPU 数据及 TP audit 校验，只打印训练命令
bash scripts/train/run_full_gad_tp_tp_optimized.sh --dry_run

# TP Warmup + TP GAD
CUDA_VISIBLE_DEVICES=1,3 bash scripts/train/run_full_gad_tp_tp_optimized.sh \
  --model models/Qwen2.5-0.5B \
  --exp_name kgw_tp_student_tp_1ep

# TP Warmup + 原 KGW GAD
CUDA_VISIBLE_DEVICES=1,3 bash scripts/train/run_full_gad_tp_kgw_optimized.sh \
  --model models/Qwen2.5-0.5B \
  --exp_name kgw_tp_student_kgw_1ep
```

默认训练文件现为 `data/dolly15k_qwen2_5_14b_kgw_tp_student_train.parquet`；可用 `--tp_train_file` 指定正式入口生成的其它文件。训练前检查完整源行数、全部保护字段及 TP audit 的方法、原始 O 角色、tokenizer 校验、无投影声明、完成状态和输入/输出哈希。普通 UP 和备用 Dipper TP 的 audit 均会被拒绝。TP→KGW 分支在 GAD 阶段重新使用带水印数据，应单独标注，不等同于全程 TP。这里的 Warmup+GAD 是项目实验协议；原论文采用 SFT 蒸馏。

训练命令的 `--model` 同样指定原始学生 O；上例显式覆盖父训练脚本历史默认的资产路径。未指定 `--reward_model` 时，critic 按现有训练流程从同一原始 O 初始化独立骨干。

### Dipper 投影备用入口

旧方案现命名为 `paraphrase_tp_dipper_backup.py` / `tokenizer_bridge_dipper_backup.py`，仍沿用 Dipper L60/O0、top_p=0.75 和完整回答一次改写。它将“Dipper 历史 + 候选”解码为文本，再用规则 tokenizer 编码，对新增或重分词后改变的学生 token 后缀求 D 均值，作为 Dipper 候选的罚分。

默认只投影原始 logits 最高的 128 个候选，并使用末尾 64 个 Dipper decoder token；`--candidate-top-k 0 --projection-context-tokens 0` 表示全部普通候选和完整 decoder 历史，速度可能明显变慢。这始终是本项目补充的跨 tokenizer 近似，不能当作作者未公开的 TP 实现。

```bash
python baseline_acl/paraphrase_tp_dipper_backup.py \
  --input data/dolly15k_qwen2_5_14b_kgw_train.parquet \
  --rules data/acl_estimated_rules.json \
  --rule-tokenizer models/Qwen2.5-0.5B --preflight

CUDA_VISIBLE_DEVICES=1,2 python baseline_acl/paraphrase_tp_dipper_backup.py \
  --input data/dolly15k_qwen2_5_14b_kgw_train.parquet \
  --output data/dolly15k_qwen2_5_14b_kgw_tp_dipper_backup_train.parquet \
  --rules data/acl_estimated_rules.json \
  --rule-tokenizer models/Qwen2.5-0.5B --num-gpus 2
```

备用入口的审计标签仍为 `targeted_dipper_paraphrasing`，保留投影参数及 Dipper 身份信息；正式 TP 训练包装脚本明确拒绝此标签。备用生成仍需要已准备好的本地 Dipper、T5 tokenizer 和 NLTK 资源。旧 Dipper 投影算法可供后续独立实验使用。

旧训练流水线也保留为 `run_tp_gad_pipeline_dipper_backup.sh`，两个分支入口均带 `_dipper_backup`，只接受旧 Dipper audit，不接受正式学生 TP audit。默认读取 `data/dolly15k_qwen2_5_14b_kgw_tp_dipper_backup_train.parquet`，实验名默认 `kgw_tp_dipper_backup_tp_1ep` / `kgw_tp_dipper_backup_kgw_1ep`。已有旧数据文件可通过 `--tp_train_file` 指定，但其 audit 和输入/输出哈希必须仍匹配。

```bash
# 备用 Dipper TP 数据预检
bash scripts/train/run_full_gad_tp_tp_dipper_backup_optimized.sh --dry_run

# 备用 Dipper TP Warmup + TP GAD
CUDA_VISIBLE_DEVICES=1,3 bash scripts/train/run_full_gad_tp_tp_dipper_backup_optimized.sh \
  --model models/Qwen2.5-0.5B --exp_name kgw_tp_dipper_backup_tp_1ep

# 备用 Dipper TP Warmup + 原 KGW GAD
CUDA_VISIBLE_DEVICES=1,3 bash scripts/train/run_full_gad_tp_kgw_dipper_backup_optimized.sh \
  --model models/Qwen2.5-0.5B --exp_name kgw_tp_dipper_backup_kgw_1ep
```

## 3. WN 推理

WN 在 vLLM V0 的三参数 `logits_processors` 接口中，以 prompt 和已生成 token 的末尾上下文查 D 并扣分；不足两个生成 token 时使用 prompt 补足。默认强度 2.5，`--strength 0` 可生成同一学生的无攻击控制组。不会自动训练学生或改写训练数据。

```bash
W=checkpoints/kgw_reference/gad/global_step_NNN/actor/huggingface

python wm_test/generate_wn_score.py \
  --student-model "$W" \
  --rules data/acl_estimated_rules.json \
  --input data/dolly15k_qwen2_5_14b_kgw_test.parquet \
  --output wm_test/student_wn.jsonl --preflight

CUDA_VISIBLE_DEVICES=1 VLLM_USE_V1=0 python wm_test/generate_wn_score.py \
  --student-model "$W" \
  --rules data/acl_estimated_rules.json \
  --input data/dolly15k_qwen2_5_14b_kgw_test.parquet \
  --output wm_test/student_wn.jsonl --strength 2.5
```

将 `NNN` 换成已保存完整、合并后的参考学生 W checkpoint 步数；完整前序流程见 [TP_WN_BASELINE.md](TP_WN_BASELINE.md)。

输出兼容现有 `wm_test/evaluate_compare_metrics.py`，包含规则哈希、攻击参数、逐行 seed、原始和去重 KGW 分数/p-value。`label=kgw` 表示来自带水印数据训练的学生，不表示该回答检测成功。真实 KGW key 只用于生成后的检测，未参与攻击扣分。

比较同一 checkpoint 的 WN 开/关结果时，使用相同 prompt、seed 和采样参数；同时检查回答质量。prompt 超预算会提前失败，不静默截断。输出默认防覆盖，全部生成成功后才发布最终 JSONL。

## 验证范围

本地测试使用标准库 unittest、真实小 Parquet 数据和假的模型/采样后端，覆盖数学、直接 ID 扣分、tokenizer 错配、因果模型 prompt/预算、采样 hook、保护字段、数据审计、恢复及异常发布；另验证正式 writer 实际生成的 audit 能通过训练脚本中的原始 Python gate。备用测试另覆盖投影与边界重分词，以及正式/备用 audit 的互斥。模型资产加载均限定本地目录。

真实预检需要 PyArrow、Transformers 和对应学生 tokenizer 依赖；正式 TP 无需 Dipper 或 NLTK。真实生成需要 PyTorch/CUDA；WN 需要项目兼容的 vLLM V0 环境。当前本机未加载模型或运行 GPU，因此没有验证实际 GPU 改写、推理吞吐量、转述质量或去水印效果。

```bash
python -m unittest tests.test_inverse_watermark tests.test_steal_watermark \
  tests.test_tokenizer_bridge_dipper_backup tests.test_paraphrase_tp_dipper_backup \
  tests.test_paraphrase_tp tests.test_generate_wn \
  tests.test_tp_training_pipeline tests.test_paraphrase_up tests.test_dipper_parallel
```
