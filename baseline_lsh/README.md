# Token级语义LSH水印 baseline

生成教师：`/shared/public_models/Qwen2.5-14B-Instruct`。训练输入：`data/dolly15k_train.parquet`（扩展名为 `.parquet`）。
在项目根目录运行以下命令；沿用服务器的 `wm` 环境，不替换现有 vLLM/Transformers。

## 方法范围

参考 [Context-aware Watermark with Semantic Balanced Green-red Lists for Large Language Models，EMNLP 2024](https://aclanthology.org/2024.emnlp-main.1260.pdf) §3.2/3.3：

1. 从教师 **input embedding** 取每个token的静态向量，以固定高斯超平面LSH生成桶ID。
2. 上一token的桶ID作为下一token绿红划分的上下文种子。相同桶共享规则。
3. 默认对每个语义桶分别随机划绿/红，再合并，使绿名单语义分布均衡。
4. 对绿色token的logit **加固定delta**，与本项目KGW的强度参数形式一致。

这是**论文LSH种子+语义均衡划分的固定加法适配版**，不是完整原论文复现：不含其动态强度、熵过滤和附录中的乘法logit处理；PRNG和整数取整规则是此实现明确固定的约定。本次未获得可直接核对的作者代码。不要将本实现称为官方原版或直接引用原论文性能。

默认 `gamma=0.5, delta=3, lsh-bits=4, lsh-seed=42, hash-key=15485863`。
4个超平面来自论文的参数选择；其余随机种子是本项目实验约定。
`delta=3/6` 可分别运行；同样数值不代表与KGW有相同水印强度或质量代价。
`--partition global` 仅取消语义均衡划分，仍使用LSH种子，可作为消融。

## 1. 一次性准备映射（CPU，不加载14B模型）

依赖：NumPy、PyTorch、Transformers、safetensors；生成另需PyArrow和现有vLLM 0.8.x V0环境。
脚本只按chunk读取HF safetensors里的 `model.embed_tokens.weight`，支持分片checkpoint，不会把整个14B模型载入内存或占GPU。

```bash
conda activate wm

python baseline_lsh/prepare.py \
  --model /shared/public_models/Qwen2.5-14B-Instruct \
  --output baseline_lsh/assets/qwen2_5_14b_lsh4_seed42.npz \
  --lsh-bits 4 --lsh-seed 42
```

映射固定后，delta=3/6、不同学生和检测都复用**同一份npz**；不要用学生embedding重新准备映射。
映射含tokenizer指纹、超平面、token→桶表、embedding内容摘要和桶大小。已有资产不覆盖；更换LSH参数必须新建文件。
特殊token参与词表，与普通token一起划分；模型padding出来、tokenizer中没有的logit位置被屏蔽。
初次CPU投影结果会被冻结，后续检测不再受CPU/CUDA矩阵计算的微小差异影响。

## 2. CPU预检与小批试跑

```bash
python baseline_lsh/generate.py \
  --model /shared/public_models/Qwen2.5-14B-Instruct \
  --input data/dolly15k_train.parquet \
  --output data/dolly15k_qwen2_5_14b_lsh_gamma0.5_delta3_train.parquet \
  --gamma 0.5 --delta 3 --preflight
```

预检读取本地tokenizer、输入、映射和模型文件目录，不加载模型权重，不调用CUDA或vLLM生成。
它会列出缺失的运行包；预检成功不代表显存足够或GPU推理已验证。

```bash
CUDA_VISIBLE_DEVICES=0 python baseline_lsh/generate.py \
  --model /shared/public_models/Qwen2.5-14B-Instruct \
  --input data/dolly15k_train.parquet \
  --output baseline_lsh/outputs/smoke_delta3.parquet \
  --gamma 0.5 --delta 3 --limit 16 --batch-size 2 --shard-size 8
```

显存不足时降低 `--gpu-memory-utilization` 不能让模型权重自动变小；可降低batch，或单进程使用 `--tensor-parallel-size 2` 配合两张可见卡。

## 3. 全量生成：delta=3或6

```bash
CUDA_VISIBLE_DEVICES=0 python baseline_lsh/generate.py \
  --model /shared/public_models/Qwen2.5-14B-Instruct \
  --input data/dolly15k_train.parquet \
  --output data/dolly15k_qwen2_5_14b_lsh_gamma0.5_delta3_train.parquet \
  --gamma 0.5 --delta 3

CUDA_VISIBLE_DEVICES=0 python baseline_lsh/generate.py \
  --model /shared/public_models/Qwen2.5-14B-Instruct \
  --input data/dolly15k_train.parquet \
  --output data/dolly15k_qwen2_5_14b_lsh_gamma0.5_delta6_train.parquet \
  --gamma 0.5 --delta 6
```

一次只运行需要的配置；上面两条是不同实验，不必同时跑。
默认采样沿用KGW：temperature=0.7、top_p=0.9、top_k=-1、seed=42+原始行号、最大prompt=2048、最大生成=1536。
默认不设最小输出长度，不强制扩写回答。`finish_reason=length` 单独计数，需抽查截断与回答质量。

多卡数据并行，每张卡各载一份14B：

```bash
CUDA_VISIBLE_DEVICES=0,1 python baseline_lsh/generate.py \
  --model /shared/public_models/Qwen2.5-14B-Instruct \
  --input data/dolly15k_train.parquet \
  --output data/dolly15k_qwen2_5_14b_lsh_gamma0.5_delta3_train.parquet \
  --gamma 0.5 --delta 3 --num-gpus 2
```

只使用明确指定的卡，不自动占用其他GPU；`--num-gpus` 必须等于可见卡数量。数据并行与tensor parallel不能同时开启。
worker日志在 `<output>.parts/worker-XX.log`；控制台定期报告已提交分片数。

## 4. 输出、GAD接入和断点

- `<output>.parquet`：完全保留源schema、Arrow field metadata、其他列和ID顺序，仅替换 `teacher_response`。可作为现有warmup/SeqKD/GAD的教师数据，训练配置中的教师数据路径改为该文件。
- `<output stem>_lsh_scores.jsonl`：每条回答的绿色计数、比例、诊断z、去重分数、真实生成token IDs、结束原因；不修改训练schema。
- `<output>.parquet.metadata.json`：完整运行配置、输入/映射/输出摘要、版本、截断数量等；只有该文件标记complete且摘要匹配时才视为发布完成。
- `<output>.parquet.parts/`：保留manifest和已提交分片，便于断点恢复；默认不删。

中断后**原命令重跑**：重用通过hash和源列校验的完整分片，未完成分片重跑；已完整发布且hash一致则直接结束，不重新加载模型。未提交分片内的少量进度可能重做。
修改gamma/delta、资产、输入、模型文件、代码、采样/分片配置或依赖版本会拒绝混入旧断点，请换输出路径。仅改变数据并行卡数可重分配尚未完成分片；不同硬件/批调度不保证浮点逐位相同。
同时运行同一输出路径会被锁阻止。异常kill留下run.lock时，先确认旧job和其workers全部停止，再仅删除 `<output>.parts/run.lock` 后原命令恢复。不要删除其他实验目录。
本目录不提供覆盖已有实验的开关。

训练阶段默认按原有GAD流程使用带水印回答，**不要在学生推理时重新打开LSH处理器**，否则测到的是新加的水印。

## 5. 无水印生成学生/基座回答并测残留

下面示例将模型路径替换为实际学生HF checkpoint，输出必须新建。始终使用教师的LSH资产和tokenizer。

```bash
CUDA_VISIBLE_DEVICES=0 python baseline_lsh/generate.py \
  --model /path/to/student/checkpoint/actor/huggingface \
  --tokenizer /shared/public_models/Qwen2.5-14B-Instruct \
  --input data/dolly15k_test.parquet \
  --output baseline_lsh/outputs/student_gad_delta3_test.parquet \
  --watermark none --gamma 0.5 --delta 3
```

`--watermark none` 不给学生logits加偏置，delta仅记录其训练设置；它不等于“学生没有继承水印”。此时sidecar的 `is_watermarked=null`，`label=none`只表示生成模式，不是水印真值标签。相同提示/采样条件下，也对无水印微调学生和base运行此命令，输出另命名。脚本会核对学生tokenizer的实际词表/编码与教师兼容；只允许聊天模板不同，生成统一使用指定教师模板。

## 6. 对已有回答离线检测（CPU、不加载LLM）

```bash
python baseline_lsh/detect.py \
  --input data/dolly15k_qwen2_5_14b_lsh_gamma0.5_delta3_train.parquet \
  --output baseline_lsh/outputs/teacher_delta3_rescore.jsonl \
  --gamma 0.5

python baseline_lsh/detect.py \
  --input /path/to/saved_student_answers.jsonl \
  --output baseline_lsh/outputs/student_gad_rescore.jsonl \
  --text-field answer --gamma 0.5
```

支持Parquet的`teacher_response`，或JSONL的`teacher_response/answer/text/generated_text`（可指定 `--text-field`）。JSONL可用 `content` / `prompt` 的messages；字符串prompt必须已经套好模板，不自动猜测。
默认使用prompt末token判断回答首token；只有回答没有prompt时，显式用 `--context answer-only`，跳过首token。不得把两个模式的token预算混在一起。
检测不需要delta；只需相同资产、gamma、hash-key和partition。`--max-tokens` 可固定回答检测预算。

## 7. 统计与一致性约定

绿名单使用PCG64的稳定raw64位流、SHA256派生种子，按随机优先级排序选择token；不依赖NumPy高级permutation算法。CPU/CUDA使用同一份名单；**不声称与原KGW的CUDA randperm相同**。
语义均衡模式用最大余数法分配整数绿数量，总数恰为 `floor(gamma*真实词表大小)`，每个语义组误差小于1。
诊断z使用当前上下文桶、当前目标token语义组的实际绿比例q，计算 `(G-sum(q))/sqrt(sum(q*(1-q)))`，避免把取整误差当残留。
去重按 **(上下文LSH桶, 目标token)**；不同原始token落在同一个桶时不视为独立密钥。

这些z都是诊断统计，**不输出未经校准的精确p值**。共享桶/重复文本存在相关性；应使用匹配的clean输出做独立阈值校准。GAD后是否残留尚待服务器实验。

生成时同时记录两种分数：顶层字段为保存文本重新tokenize后的分数，便于和学生文本公平比较；`generation_score` 基于vLLM真实生成token IDs。去除特殊/EOS或tokenizer解码往返可能令两者不同，`text_token_ids_match`记录是否一致，不默默声称相同。

## 8. 本地检查

```bash
python -m unittest discover -s baseline_lsh/tests -v
```

测试用合成embedding/词表、CPU Torch及伪生成引擎覆盖规则和IO，不需要教师权重。GPU推理、服务器vLLM兼容性、实际吞吐/质量与GAD效果需按上面的16条smoke先验证。
