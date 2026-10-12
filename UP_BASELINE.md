# Dipper UP 普通改写：两组 GAD 实验

本入口已改用 **Dipper**，不再使用 Qwen 或通用聊天模型改写。先由你准备模型、改写 KGW 教师训练回答，再手动启动训练。原始数据不覆盖，test 不改写，不自动启动训练。

## 与 baseline 的一致性

[ACL 2025 论文 §4.1](https://aclanthology.org/2025.acl-long.648.pdf)明确使用 Dipper，但未公开 UP 的完整超参数，[官方仓库](https://github.com/THU-BPM/Watermark-Radioactivity-Attack#attack-pipeline)也只发布 WN。因此这里对齐 **Dipper 改写器与普通 UP 方法**，其余参数参考 [Dipper 作者示例](https://huggingface.co/kalpeshk2011/dipper-paraphraser-xxl#using-dipper)。本入口每条教师回答一次送入 Dipper，超过输入上限时截去尾部；不使用作者示例的三句窗口。这是本项目配置，不声称逐项精确复现 ACL 原实验。

| 设置 | 本入口 | 参数出处/说明 |
| --- | --- | --- |
| 模型 | `kalpeshk2011/dipper-paraphraser-xxl` | 作者发布的完整上下文版本，11B T5 |
| Tokenizer | `google/t5-v1_1-xxl` 的 T5Tokenizer | Dipper 官方用法 |
| lexical / order diversity | 60 / 0 | 作者模型卡采样示例，并非 ACL 公布的参数 |
| 改写范围 | NLTK 英文分句后拼接，一次改写；超长截去尾部 | 按你的要求适配；不按三句分组 |
| prefix | 始终为空 | 不使用滚动 prefix，不跨样本，不塞入原问题 |
| 采样 | do_sample=True，top_p=0.75，禁用 top-k | 作者示例 |
| temperature | 1.0 | 明确采用 Transformers 默认值，非 ACL 指定值 |
| decoder 输出 | max_length=4096，每条完整回答 | 整条改写的长度预算，区别于作者示例的每窗口 512 |
| encoder 输入 | 最大 4096 token，超长保留开头、截去尾部 | 包含完整控制模板和 EOS，记录截断审计 |
| 精度 | 默认 auto；可显式 float32 / bfloat16 | auto 在所有选中卡均支持 BF16 时统一 BF16，否则统一 FP32；属于项目资源适配 |
| 尝试次数 | 默认每条累计最多 3 次；失败耗尽时删行 | 仅重试空输出等生成异常，不按水印或质量分数挑结果 |

内部控制码是 `100-diversity`，L60/O0 输入为 `lexical = 40, order = 100`，使用 `<sent> 回答文本 </sent>`。分句用于规范化和审计；每条回答调用一次 Dipper，失败时最多重试两次。生成不使用 KGW 处理器、检测器、密钥或逆水印。是否洗净仍需事后检测。

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

inspect 只检查 Parquet；preflight 只加载小 tokenizer 和 NLTK，不加载 Dipper 权重、不占 GPU。完整输入超过 encoder 预算时自动保留回答开头、截去尾部，保留完整控制模板和 EOS；预检显示截断条数及前后长度，正式运行把对应行号、ID、长度和文本哈希写入审计。未超长的回答与原流程一致，旧断点可继续使用。每条仍只调用一次 Dipper，不切成窗口；实际生成再次核对输入及输出长度。

原训练集 **14,511 行**，验证集 500 行。保留行只替换 teacher_response，问题、ID、顺序、其余列和 schema/metadata 均保持；默认 `--on-failure drop` 会删去重试耗尽的整条样本。按作者用法归一化空白、分句、拼接，因此换行/排版可能改变；正式实验应抽查数字、事实、列表和代码，不能假定改写天然保真。

## 3. Dipper 普通改写

未设置 `CUDA_VISIBLE_DEVICES` 时，`--num-gpus 3` 自动按空闲显存选择 3 张卡并并行改写。

```bash
unset CUDA_VISIBLE_DEVICES

# KGW gamma=0.25, delta=2
python baseline_acl/paraphrase_up.py \
  --input data/dolly15k_qwen2_5_14b_kgw_train.parquet \
  --output data/dolly15k_qwen2_5_14b_kgw_up_dipper_train.parquet \
  --num-gpus 3

# KGW gamma=0.5, delta=3
python baseline_acl/paraphrase_up.py \
  --input data/dolly15k_qwen2_5_14b_kgw_gamma0.5_delta3_train.parquet \
  --output data/dolly15k_qwen2_5_14b_kgw_gamma0.5_delta3_up_dipper_train.parquet \
  --num-gpus 3
```

每张卡由一个独立进程加载完整 Dipper，动态领取回答，快卡领取更多样本。父进程统一管理断点、审计和最终 Parquet，按原始行序汇总。`--batch-size` 默认 1 即可；超长自动截断、三次失败删行的策略保持一致。

自动模式省略 `--num-gpus` 时选 1 张卡。显存初筛估计每卡需至少 30000 MiB，FP32 需至少 50000 MiB；选卡后再次检查实际精度与显存，模型加载及生成仍可能受其他进程占用影响。无法找到指定数量时直接报错。手动选卡使用 `CUDA_VISIBLE_DEVICES=1,2,3`；显式卡数须匹配，省略则使用全部指定卡，不会自动加入其他卡。`--inspect`、`--preflight` 仍只使用 CPU。

`--dtype auto` 先确定所有选中卡的能力：全部支持 BF16 则统一 BF16，否则统一 FP32。显式 `--dtype float32` 或 `--dtype bfloat16` 会严格执行；不支持或显存不足时失败，不自动切换精度。每卡都需要加载完整模型及推理状态，显存不能跨卡合并。单卡选择 `CUDA_VISIBLE_DEVICES=1`，命令加 `--dtype float32` 可保留作者示例默认精度；40GB 卡通常需 BF16，但仍须足够空闲显存。最终审计记录实际精度。

某个 worker 失败会停止本次改写启动的其他 worker，保留已写入的断点；不会停止其他用户或其他任务的进程。

旧的 `--engine`、`--gpu-memory-utilization` 等 Qwen/vLLM 参数，以及三句版本的 `--window-size` 均不再适用。Dipper 使用 Transformers T5 encoder-decoder；训练阶段的 vLLM 显存设置是另一件事，保持原样。整条回答的 encoder 和 decoder 序列可能更长，显存与运行时间不能直接沿用旧三句版本的估计。

输出：最终 Parquet、`<output>.progress.jsonl`、`<output>.audit.json`。全部源行处理完成才发布 Parquet，最终行数减去失败删行数。中断后重新运行同一命令会自动续跑，成功行不重做；`--resume` 仍可使用。模型、tokenizer、分句资源、整条改写模式、实际精度、参数和输入均纳入指纹。GPU 数量可在续跑时改变；默认 `--dtype auto` 在续跑时沿用断点记录的实际精度，选中的卡须支持该精度。显式精度和其他具体改写参数须匹配。保留 v3 格式，可续用参数与输入匹配的既有整条断点，**不能续用旧 Qwen 或三句滚动断点**。跨 GPU 型号或硬件环境不保证逐位相同。

默认输出文件名保持不变，便于后续训练入口读取。如果该位置已有旧 Qwen/三句结果或不匹配的 progress/audit，不要覆盖或混接；请选择新的 --output 文件名，并在两个训练命令中都用 --up_train_file 指向新文件。匹配的 v3 整条断点可直接续跑。也可自行确认后将本实验的旧文件移到备份目录，再使用默认路径；不要移动其他同学的文件。

默认 `--max-attempts 3 --on-failure drop`：失败行自动换采样 seed 重试，累计三次仍失败就删除整条样本并继续，不把空回答写入训练集。删行 ID、源行号、尝试次数和原因保存在审计 JSON，训练前自动核对原始输入与输出哈希、保留行及删行记录；请保留最终 Parquet 旁的 `.audit.json`。旧的单次尝试、失败即停断点也可用同一普通命令续跑，重试策略变更追加到原断点，不改旧记录。此策略是项目异常处理配置，不是 ACL 公布的超参。需要失败即停时可显式使用 `--max-attempts 1 --on-failure error`；`--on-failure keep-original` 会混入未改写回答，正式纯 UP 实验不建议开启。

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

CPU 回归测试使用模拟生成器，验证整条改写、字段/schema 保护、断点恢复与失败处理；不能替代真实多 GPU Dipper 推理或训练验证。临时测试数据不会替换原训练数据。

已在服务器 `wm` 环境对原训练集完成整条模式 CPU 预检：**14,511 条回答对应 14,511 个完整输入**，每条只有一个输入；最多 119 句的回答也不分块。完整控制码输入最长 **2,149 个 T5 token**，原回答最长（含 EOS）2,131 token，无输入超预算，原回答长度也均低于当前 decoder 允许的 4,095 个生成 token。该检查未加载 Dipper 权重、未占 GPU，不能据此保证生成时的输出长度、语义保真或显存充足。

旧三句版本的窗口数量、窗口 token 长度和 CPU 回归结果不能直接充当整条模式的验证证据。更换数据或预算后，应使用上面的 --preflight 重新检查完整输入；T5 的 token 长度也不能用 Qwen tokenizer 的长度替代。CPU 检查、单元测试和合成数据 dry-run 不代表真实 Dipper GPU 改写或两阶段训练已跑通。

本模式将 max_length 提高到 4096，并会检查 EOS 和触顶情况，但**正常输出 EOS 不保证没有遗漏、压缩或事实改动**。应抽查完整长回答的数字、事实、列表和代码，并在正式实验中单独评价改写质量及水印检测指标。ACL 未公开参数无法证明逐项一致，应透明报告上表配置，尤其注明整条改写和输出预算这两项适配。当前只准备了小 tokenizer 与英文分句资源，45 GB Dipper 权重未下载，正式改写数据也未生成。
