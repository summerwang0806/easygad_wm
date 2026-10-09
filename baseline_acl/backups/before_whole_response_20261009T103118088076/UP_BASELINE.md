# Dipper UP 普通改写：两组 GAD 实验

本入口已改用 **Dipper**，不再使用 Qwen 或通用聊天模型改写。先由你准备模型、改写 KGW 教师训练回答，再手动启动训练。原始数据不覆盖，test 不改写，不自动启动训练。

## 与 baseline 的一致性

[ACL 2025 论文 §4.1](https://aclanthology.org/2025.acl-long.648.pdf)明确使用 Dipper，但未公开 UP 的完整超参数，[官方仓库](https://github.com/THU-BPM/Watermark-Radioactivity-Attack#attack-pipeline)也只发布 WN。因此这里对齐 **Dipper 改写器与普通 UP 方法**，未公开部分采用 [Dipper 作者示例](https://huggingface.co/kalpeshk2011/dipper-paraphraser-xxl#using-dipper)，不声称逐项精确复现 ACL 原实验。

| 设置 | 本入口 | 参数出处/说明 |
| --- | --- | --- |
| 模型 | `kalpeshk2011/dipper-paraphraser-xxl` | 作者发布的完整上下文版本，11B T5 |
| Tokenizer | `google/t5-v1_1-xxl` 的 T5Tokenizer | Dipper 官方用法 |
| lexical / order diversity | 60 / 0 | 作者模型卡采样示例，并非 ACL 公布的参数 |
| 窗口 | 每次 3 句，NLTK 英文分句 | 作者示例默认值 |
| prefix | 初始为空；追加本条回答之前已改写的窗口 | 行内滚动，不跨样本；不塞入原问题 |
| 采样 | do_sample=True，top_p=0.75，禁用 top-k | 作者示例 |
| temperature | 1.0 | 明确采用 Transformers 默认值，非 ACL 指定值 |
| decoder 输出 | max_length=512，每个窗口 | 作者示例；不是整条回答的上限 |
| encoder 输入 | 最大 4096 token，超长报错 | 本项目安全边界，不静默截断 |
| 精度 | 默认 float32；可显式 bfloat16 | 官方最小脚本默认 FP32；BF16 是资源适配 |
| 尝试次数 | 默认每条 1 次 | 不按水印或质量分数挑结果；可显式异常重试 |

内部控制码是 `100-diversity`，L60/O0 输入为 `lexical = 40, order = 100`，使用 `<sent> ... </sent>`，不是聊天模板。生成不使用 KGW 处理器、检测器、密钥或逆水印。是否洗净仍需事后检测。

## 1. 下载模型（CPU，不占 GPU）

```bash
cd /app/wwx/EasyGAD
conda activate wm

python baseline_acl/download_dipper.py
python baseline_acl/download_dipper.py --check
```

下载固定官方版本，仅取一套 safetensors 权重（约 **45.07 GB**），另取小型 T5 tokenizer 和 NLTK 分句资源。不重复下载 .bin，不下载 T5 原模型权重，不写实验室 public_models。

```text
baseline_acl/models/dipper-paraphraser-xxl/
baseline_acl/models/t5-v1_1-xxl-tokenizer/
baseline_acl/nltk_data/
```

固定版本：Dipper `c1fbf7a958a2aab022e9e6f81f7a3139f9e6ee3c`；T5 tokenizer `3db67ab1af984cf10548a73467f0e5bca2aaaeb2`。中断后重新运行下载命令可利用已有文件；`--check` 离线检查，不加载模型。入口不会擅自安装或升级共享环境依赖。

若 Hugging Face 不可达，先恢复你自己的反向隧道和代理。只有隧道实际存在时才设置：

```bash
export http_proxy=http://127.0.0.1:7890
export https_proxy=http://127.0.0.1:7890
curl -I --connect-timeout 5 https://huggingface.co
```

大权重下载不自动启动，需你执行上述命令。

## 2. CPU 检查

```bash
python baseline_acl/paraphrase_up.py \
  --input data/dolly15k_qwen2_5_14b_kgw_train.parquet --inspect

python baseline_acl/paraphrase_up.py \
  --input data/dolly15k_qwen2_5_14b_kgw_train.parquet --preflight
```

inspect 只检查 Parquet；preflight 只加载小 tokenizer 和 NLTK，检查源文本分窗，不加载 Dipper 权重、不占 GPU。实际改写后的滚动 prefix 长度仍需生成时逐窗口检查。

原训练集 **14,511 行**，验证集 500 行。只替换 teacher_response，保留问题、ID、顺序、其余列和 schema/metadata。按作者用法归一化空白、分句、拼接，因此换行/排版可能改变；正式实验应抽查数字、事实、列表和代码，不能假定改写天然保真。

## 3. Dipper 普通改写

服务器 1 号卡是 A100 80GB，其他为 40GB。下面用 **1 号卡 + float32** 保持作者示例默认精度；运行前确认显存空闲或已协调使用。不会停止已有进程，不使用 0 号卡。

```bash
CUDA_VISIBLE_DEVICES=1 python baseline_acl/paraphrase_up.py \
  --input data/dolly15k_qwen2_5_14b_kgw_train.parquet \
  --output data/dolly15k_qwen2_5_14b_kgw_up_dipper_train.parquet \
  --model baseline_acl/models/dipper-paraphraser-xxl \
  --tokenizer baseline_acl/models/t5-v1_1-xxl-tokenizer \
  --dtype float32 \
  --lex-diversity 60 --order-diversity 0 --window-size 3 \
  --top-p 0.75 --temperature 1.0 \
  --max-output-length 512 --max-input-tokens 4096 \
  --max-attempts 1 --seed 42
```

若只能用空闲 40GB 卡，可例如改成 `CUDA_VISIBLE_DEVICES=3` 与 `--dtype bfloat16`。这是同一份 Dipper 权重的数值精度适配，报告要注明；是否装得下取决于实际空闲显存。不要在 40GB 卡硬加载 float32。

旧的 `--engine`、`--gpu-memory-utilization` 等 Qwen/vLLM 参数不再适用。Dipper 使用 Transformers T5 encoder-decoder；训练阶段的 vLLM 显存设置是另一件事，保持原样。

输出：完整 Parquet、`<output>.progress.jsonl`、`<output>.audit.json`。全部行成功才发布最终 Parquet；中断后使用**同一命令加 --resume**，成功行不重做。模型、tokenizer、分句资源、窗口、精度、参数和输入均纳入指纹；不能沿用旧 Qwen 断点。

默认失败时停止，不丢行、不偷偷补原文。可显式 `--max-attempts 3` 做有记录的异常重试，但这不是 ACL 公布的超参；改变配置需新输出名。`--on-failure keep-original` 会混入未改写回答，正式纯 UP 实验不建议开启。

## 4. 两组训练（各阶段 1 epoch）

两个入口的默认输入已改为 `data/dolly15k_qwen2_5_14b_kgw_up_dipper_train.parquet`，避免误用旧 Qwen 改写数据。

| 入口 | Warmup 教师回答 | GAD 教师回答 | epoch |
| --- | --- | --- | --- |
| run_full_gad_up_up_optimized.sh | Dipper-UP | 同一份 Dipper-UP | 1 + 1 |
| run_full_gad_up_kgw_optimized.sh | Dipper-UP | 原 KGW | 1 + 1 |

完整改写成功后先检查配置：

```bash
CUDA_VISIBLE_DEVICES=1,3 bash scripts/train/run_full_gad_up_up_optimized.sh \
  --exp_name kgw_up_dipper_up_1ep --nnodes 1 --dry_run

CUDA_VISIBLE_DEVICES=1,3 bash scripts/train/run_full_gad_up_kgw_optimized.sh \
  --exp_name kgw_up_dipper_kgw_1ep --nnodes 1 --dry_run
```

去掉 --dry_run 正式运行。**先结束改写，再依次跑两组训练**，不要在相同卡上并行启动：

```bash
# A：Dipper-UP Warmup -> Dipper-UP GAD
CUDA_VISIBLE_DEVICES=1,3 bash scripts/train/run_full_gad_up_up_optimized.sh \
  --exp_name kgw_up_dipper_up_1ep --nnodes 1

# B：Dipper-UP Warmup -> 原 KGW GAD
CUDA_VISIBLE_DEVICES=1,3 bash scripts/train/run_full_gad_up_kgw_optimized.sh \
  --exp_name kgw_up_dipper_kgw_1ep --nnodes 1
```

学生仍从 `/shared/public_models/Qwen2.5-0.5B` 初始化，独立 critic 未指定时也从原模型初始化。各组 Warmup 完成后自动合并本组 actor/critic 并衔接 GAD，不加载旧 SeqKD 学生，不复用另一组 checkpoint。Dipper **仅用于改写**，不是训练学生或 critic。

验证均保留原 KGW test；原学习率、batch、长度、critic warmup、显存设置和 SwanLab 不变。训练教师回答超过 1536 个学生 token 时仍按原加载器右截断。CPU 预检拒绝部分数据、ID/顺序错乱或其他字段变化。

单卡训练需显式选一个卡并加 `--gpus_per_node 1`。重跑需新实验名，已有 checkpoint 不覆盖。

```text
checkpoints/kgw_up_dipper_up_1ep/{warmup,gad}/global_step_*/{actor,critic}/
checkpoints/kgw_up_dipper_kgw_1ep/{warmup,gad}/global_step_*/{actor,critic}/
```

SwanLab 为 <exp_name>_warmup 和 <exp_name>_gad。复用服务器已跑通的 run_full_gad_all_clean_optimized.sh 并明确覆盖数据；其历史 CLEAN 标签不代表本次数据，请以实际路径为准。

两组各自独立 Warmup。若要严格比较同一 Warmup 起点的因果差异，需另做共享 checkpoint 的受控分支；这里保留你要求的两套独立 1+1 epoch。

## 验证边界

本次服务器 30 项 CPU 回归测试通过。实际 T5 tokenizer 和英文 PunktTab 对 14,511 行训练回答做了前置检查，共 54,261 个窗口：最大无 prefix 输入 1,949 token，原文 prefix 估计最大 2,149 token，未发现超出 encoder 4,096 预算的源窗口。

其中 **20 个源窗口长于 decoder 的 511 个新 token 额度**。这不必然等于生成截断（改写可能更短），但存在压缩、遗漏或触顶风险。默认仍保持作者示例 max_length=512，实际生成会检查 EOS/长度并拒绝截断输出；需要抽查这些长窗口的语义保留。若显式提高 --max-output-length（例如 2048），需新输出文件名，并在报告中注明不同于作者公开示例，不能默默当成相同设置。

CPU 回归测试、合成数据 dry-run 不代表真实 Dipper GPU 改写/训练已跑通。之前 Qwen tokenizer 的长度结论不适用于 Dipper，改用 T5 preflight 与逐窗口检查。ACL 未公开参数无法证明逐项一致，应透明报告上表配置。当前只准备了小 tokenizer 与英文分句资源，45 GB Dipper 权重未下载，正式改写数据也未生成。
