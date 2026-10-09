# UP 普通改写：两组 GAD 实验

本实验先对 KGW 教师训练回答做一次普通改写，再由你手动启动训练。不会覆盖原数据，不修改原训练脚本，也不会自动启动训练。

这里是 **UP 的 Qwen 改写器版本**：使用服务器已有的 `Qwen2.5-14B-Instruct`，而不是 ACL 论文的 Dipper。改写时不加载 KGW 处理器，不使用检测器或水印密钥；但“普通改写后”不等于“水印已经完全洗掉”，需要用原检测流程验证。

## 实验设置

| 入口脚本 | Warmup 教师回答 | GAD 教师回答 | 训练轮数 |
| --- | --- | --- | --- |
| `scripts/train/run_full_gad_up_up_optimized.sh` | UP 改写后的 KGW 回答 | 同一份 UP 改写回答 | 1 + 1 epoch |
| `scripts/train/run_full_gad_up_kgw_optimized.sh` | UP 改写后的 KGW 回答 | 原始 KGW 回答 | 1 + 1 epoch |

两组学生都从 `/shared/public_models/Qwen2.5-0.5B` 初始化，**不是**从之前的 SeqKD/GAD 学生初始化。未指定 `--reward_model` 时，独立 critic 骨干也从这份原始模型初始化。Warmup 完成后，脚本自动合并该组的 actor 和 critic checkpoint，再分别作为该组 GAD 阶段的初始 actor 和 critic；不是重新初始化，也不是复用另一组实验的 checkpoint。

两组验证集都保留 `data/dolly15k_qwen2_5_14b_kgw_test.parquet`，不改写 test。这样保持原有验证口径；验证 ROUGE-L 是对原 KGW 教师回答的相似度，不等同于独立的通用回答质量评分。之后对生成文本计算水印指标和文本质量时，也应使用相同的 test 问题、解码参数和参考答案。

## 1. 进入环境、先检查数据

```bash
cd /app/wwx/EasyGAD
conda activate wm

python baseline_acl/paraphrase_up.py \
  --input data/dolly15k_qwen2_5_14b_kgw_train.parquet \
  --output data/dolly15k_qwen2_5_14b_kgw_up_train.parquet \
  --model /shared/public_models/Qwen2.5-14B-Instruct \
  --inspect
```

`--inspect` 只检查数据格式，不加载生成模型、不占 GPU、不生成训练数据；精确 token 预算会在真正改写前由 tokenizer 检查。服务器实际原训练集是 **14,511 行**，验证集是 500 行。程序只替换 `teacher_response`，保留问题、ID、顺序、其余列以及 Parquet schema/metadata。改写提示只包含原教师回答，不重新回答问题，也不把过长的问题截断后塞入改写提示。

## 2. 手动运行一次普通改写

下面以 **3 号卡**为例。运行前确认该卡有足够空闲显存，或者改成你获准使用的其他卡。本改写入口一次使用一张卡；不要同时在同一张卡上启动后面的训练。

```bash
CUDA_VISIBLE_DEVICES=3 python baseline_acl/paraphrase_up.py \
  --input data/dolly15k_qwen2_5_14b_kgw_train.parquet \
  --output data/dolly15k_qwen2_5_14b_kgw_up_train.parquet \
  --model /shared/public_models/Qwen2.5-14B-Instruct \
  --engine vllm \
  --batch-size 4 \
  --max-context-length 4096 \
  --max-new-tokens 2048 \
  --temperature 0.8 \
  --top-p 0.95 \
  --seed 42 \
  --max-attempts 3 \
  --gpu-memory-utilization 0.85
```

`0.85` 是 vLLM 的显存预算比例，不是独占/锁定 GPU。先确认该卡可用；显存不足时降低该值或 batch size，但比例太低也可能装不下 14B 权重。若改变生成参数，应换一个新输出文件名，避免把不同配置混进同一份断点数据。

输出文件：

- `data/dolly15k_qwen2_5_14b_kgw_up_train.parquet`：全部完成后才能用于训练。
- `data/dolly15k_qwen2_5_14b_kgw_up_train.parquet.progress.jsonl`：逐行结果与断点记录。
- `data/dolly15k_qwen2_5_14b_kgw_up_train.parquet.audit.json`：数据、参数和结果审计。

中断后，使用**同一条命令加上 `--resume`**继续。它会核验原数据和参数指纹，不会重新生成已成功记录的行。不要在续跑时改输入、模型或生成配置。

默认每行最多尝试 3 次，重试使用不同且可复现的种子，记录每次尝试。空输出、拒答、长度截断等持续失败时会报错，不静默丢行，也不悄悄用原文补齐。程序不会覆盖原文件或已有的最终输出。只有显式指定 `--on-failure keep-original` 才允许失败行保留原 KGW 回答，并记录到审计中；**正式 UP 实验不建议使用该选项**，否则这是混合了未改写回答的数据，不能当作完整改写处理。成功改写也可能偶尔与原文相同，需检查审计并抽查文本。

## 3. 检查两组训练配置，不启动训练

改写完整数据生成成功后：

```bash
CUDA_VISIBLE_DEVICES=1,3 bash scripts/train/run_full_gad_up_up_optimized.sh \
  --exp_name kgw_up_up_1ep \
  --nnodes 1 \
  --dry_run

CUDA_VISIBLE_DEVICES=1,3 bash scripts/train/run_full_gad_up_kgw_optimized.sh \
  --exp_name kgw_up_kgw_1ep \
  --nnodes 1 \
  --dry_run
```

入口会在 CPU 上核对原始数据和改写数据的完整行数、ID、顺序、schema 及其余列，拒绝误把小样本试跑数据作为完整训练集。dry-run 不加载模型、不启动 Ray、不连接 SwanLab、不占用 GPU。

## 4. 分别运行两组训练

先运行第一组，完成后再运行第二组；不要在同样的两张卡上同时启动。

```bash
# A：UP Warmup 1 epoch -> UP GAD 1 epoch
CUDA_VISIBLE_DEVICES=1,3 bash scripts/train/run_full_gad_up_up_optimized.sh \
  --exp_name kgw_up_up_1ep \
  --nnodes 1

# B：UP Warmup 1 epoch -> 原 KGW GAD 1 epoch
CUDA_VISIBLE_DEVICES=1,3 bash scripts/train/run_full_gad_up_kgw_optimized.sh \
  --exp_name kgw_up_kgw_1ep \
  --nnodes 1
```

默认使用 1、3 号卡，不使用 0 号卡；`CUDA_VISIBLE_DEVICES` 可以按你获准使用的空闲卡修改。单卡示例：

```bash
CUDA_VISIBLE_DEVICES=3 bash scripts/train/run_full_gad_up_up_optimized.sh \
  --exp_name kgw_up_up_1ep_single_gpu \
  --nnodes 1 \
  --gpus_per_node 1
```

单卡会沿用已有优化入口的单卡 offload 配置。是否能运行仍取决于可用显存和服务器资源；这些入口不负责清理或停止任何已有进程。

## 检查点、日志与复现边界

默认检查点互相隔离：

```text
checkpoints/kgw_up_up_1ep/{warmup,gad}/global_step_*/{actor,critic}/
checkpoints/kgw_up_kgw_1ep/{warmup,gad}/global_step_*/{actor,critic}/
```

SwanLab 分别记录 `<exp_name>_warmup` 和 `<exp_name>_gad`。新入口调用服务器已有的 `scripts/train/run_full_gad_all_clean_optimized.sh`，复用之前的 SwanLab 设置和已跑通的显存、学习率、batch、长度、critic warmup、验证/保存设置；不会把密钥复制到新文件。若鉴权或网络检查失败，训练会停止，需先恢复登录/代理。

被复用入口的文件名和旧日志里含 `CLEAN`，这是历史标签，**不代表本次使用 clean 教师数据**；请以新入口打印的分支和实际 `train=...` 路径为准。这里的 UP 数据来源始终是原 KGW 回答的普通改写，绝不是直接换成 clean 教师回答。

原训练入口的 `max_prompt_length=2048`、`max_response_length=1536`、右截断设置保持不变。改写文件本身保留完整回答，但实际训练时超出 1536 token 的教师回答仍会被原训练加载器截断；两组使用相同长度上限。不要把改写文件的“完整保留”误解成训练一定使用每条全文。

重复运行要使用新的 `--exp_name`，已有检查点目录不会被覆盖。两个入口固定 Warmup 和 GAD 各 1 epoch，不接受改成其他轮数。14,511 行配合 batch 8 时，旧训练流程约为每阶段 1,813 个 batch step；实际训练步数以训练日志为准，不手动用 `1500` 来代替一整个 epoch。

两组各自独立跑一次 UP Warmup，不共享同一个 Warmup checkpoint。若要严格比较“同一 Warmup 模型之后，两种 GAD 数据的因果差异”，后续应另做共享同一 Warmup checkpoint 的受控分支实验；当前入口实现的是你要求的两套独立两阶段训练。

本次服务器验证：19 项 CPU 回归测试全部通过；三份 shell 文件语法检查通过；两组用临时合成数据完成 dry-run，确认 1+1 epoch 和数据路由；原始全量数据的格式预检查通过。实际 14B tokenizer 检查 14,511 条源回答：最长原答案 1,567 token、最长改写提示 1,683 token，配合 2,048 新 token 和 4,096 上下文，没有超预算行。

以上不表示已经替你完成 14B 改写或 GPU 训练。正式 UP 数据尚未生成，需由你运行第 2 步。
