# WN：探针选强度与固定 baseline

## 新增的最简选强度代码

入口是 `wn/probe_strength.py`，统计实现是 `wn/probe_score.py`。只测一次目标学生和参考学生；不遍历 WN 强度，不对探针施加 WN，也不读取真实 KGW 密钥。

### 输入：什么模型，什么数据

| 输入 | 具体含义 |
|---|---|
| `--student-model` | 待选强度的已蒸馏学生。默认是当前 Qwen2.5-0.5B GAD checkpoint，路径见下方固定 baseline 命令 |
| `--reference-model` | 同模型、同 tokenizer、可比较蒸馏设置的参考学生；已知某个 WN 强度对它有效。例如已验证 WN=2.5 有效的教师 delta=3 参考学生 |
| `--reference-strength` | 参考学生已知有效的 WN 强度，默认 2.5；这是已有实验知识，探针不会验证它 |
| `--tokenizer` | 两个学生共用的 tokenizer，默认 `/shared/public_models/Qwen2.5-0.5B` |
| 数据 | 已随代码附带的官方 `wn/prompts/ngram-p1.txt`、`ngram-p2.txt`，无需准备 Dolly、C4 或 test JSONL |

参考学生不是原始未蒸馏基座、clean 学生或教师 14B。需要的是“探针分数与已知 WN 强度对应”的参考锚点；不能直接把 Pan 的 Llama-7B 分数当作 Qwen 的标定值。只有目标 checkpoint 而没有参考学生或同设置已测参考分数时，无法独立校准出强度。

两个学生按顺序加载。使用官方原始 continuation 提示词，不套 chat template；自由采样 1040 种合法前缀，保留前缀后第一个 token。统计采用官方 local Water-Probe-v2 的全词表 min rank、top-50 交集、符号排名差与余弦均值。原始样本和计数均保存，非法前缀丢弃。

### 输出：一个具体的 WN 强度

```text
目标学生 + 官方探针 prompts → student_score
参考学生 + 相同探针 prompts → reference_score
selected_strength = reference_strength × student_score / reference_score
```

比例式是对 Pan 附录 F “proportionally increase”的最简工程化补全，**不是作者公布的精确公式**。例如论文中的分数代入会得到 `2.5 × 0.1694 / 0.1366 ≈ 3.1003`，而论文实际举例选用 3.0；这里不再补加离散取整、阈值带、强度下限或网格搜索。

输出 `student_score`、`reference_score` 和具体的 `selected_strength`。参考分数或目标分数非正、样本不足或完全无排名差信号时会报错并记录 `selected_strength=null`，不会伪造一个推荐值。这个值是比例估计，不代表已验证为最优或已完全去除水印，最终仍需原有独立测试集评估。

### 服务器运行

在项目根目录，使用已有 PyTorch、Transformers、NumPy 环境：

```bash
# REF 必须换成你的同配置参考学生真实路径；不能与目标使用同一个 checkpoint。
REF=/absolute/path/to/qwen2.5_0.5b_reference_student_known_wn2.5

python wn/probe_strength.py --reference-model "$REF" --dry-run

CUDA_VISIBLE_DEVICES=1 python wn/probe_strength.py \
  --reference-model "$REF" --reference-strength 2.5
```

目标默认当前 GAD checkpoint；切换模型用 `--student-model /actual/checkpoint`。如果已有完全相同探针设置得到的参考分数，可用 `--reference-score YOUR_MEASURED_SCORE` 替代 `--reference-model`，只采目标模型。

默认每模型、每提示词采样 20000 次，两模型共 **80000 次短生成**，batch=32、温度=1、top_p=1、top_k=0，单次测量；每个前缀在两条提示词下均至少有 20 个有效样本才参与统计。20000/20 来自 Water-Probe 官方本地脚本，单次运行是本工具的简化，**这些不是 Pan 附录 F 已披露的完整实验预算**。如需先确认环境能跑，可显式设 `--samples-per-prompt 128`；这只是运行检查，通常不足以估计强度，不能作为正式结果。

每次运行自动保存：

| 路径 | 内容 |
|---|---|
| `wn/probe_runs/<run_id>/result.json` | 模型路径、配置、提示词哈希、两个探针分数、最终强度与状态 |
| 同目录的 `*.samples.jsonl`、`*.counts.json` | 原始生成 token、有效样本及计数 |
| `wn/probe_strength_history.md` | 每次运行追加完整记录，失败也记录状态；实际运行时自动创建 |

复制 JSON 中的 `selected_strength` 传给原有 `wm_test/generate_wn_score.py --strength ...` 即可，原有 evaluate 继续追加评估记录。

方法来源：[Pan 附录 F](https://aclanthology.org/2025.acl-long.648.pdf#page=21)、[Water-Probe 官方本地实现](https://github.com/THU-BPM/Watermarked_LLM_Identification/blob/f946e4d93d6f3e8e308e86d6c6cd95170792a70b/scripts/experiment.py)。提示词、许可证和固定版本信息见 [prompts/SOURCE.md](prompts/SOURCE.md)。Pan 附录 F 的案例是 KGW n=1，而本项目是 previous-token KGW、Qwen2.5-0.5B，因此属于将其探测思路迁移到当前配置。

## Pan 主实验的固定逆向强度

本项目复现 Pan 等人的 WN 主实验设置：逆向水印强度固定为 `strength=2.5`，生成过程中不自动调整强度。教师 KGW 的 `delta=3` 与 WN 的逆向强度是两个独立参数，不要求取相同值。

依据：[论文第 4.1 节及附录 F](https://aclanthology.org/2025.acl-long.648.pdf#page=21)、[官方仓库](https://github.com/THU-BPM/Watermark-Radioactivity-Attack)。官方 README 的 WN 流程通过 `generate_test_data_neutralization.py` 读取 `reverse_watermark_config`。

附录 F 使用 Water-Probe-v2 测量 Llama-7B 学生的分数，参考不同教师水印强度的结果，在教师 `delta=5` 的例子中将 WN 强度从 `2.5` 调为 `3.0`。截至 2026-10-19，在已核查的公开 WN 入口和文档中未找到这套探测与自动选强度的集成实现；论文也未给出完整的分数到强度的自动换算规则。

此前本地添加的候选强度网格、48 万条探针采样、参考匹配阈值和自动选参规则均为自行扩展，不属于 Pan baseline，现已撤回相应脚本、测试和空白记录文档。

### 当前 Qwen2.5-0.5B 固定强度实验

现有 WN 实现位于 [generate_wn_score.py](../wm_test/generate_wn_score.py)，默认 `--strength 2.5`。以下使用本项目 Qwen 学生、Dolly 测试集和已有估计规则；这是将 WN baseline 迁移到本项目实验配置，不表示模型、数据集和 KGW 实现与原论文完全相同。

在服务器项目根目录运行：

```bash
W=/shared/wwx/EasyGAD/checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_new/gad/global_step_1813/actor/huggingface
RULES=wn/acl_rules_gad_Qwen2.5-0.5B_gamma0.5_delta3_fp32.json
TEST=data/dolly15k_qwen2_5_14b_kgw_gamma0.5_delta3_newtest.parquet
OUT=wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_pan_baseline_strength2.5.jsonl

python wm_test/generate_wn_score.py \
  --student-model "$W" --tokenizer /shared/public_models/Qwen2.5-0.5B \
  --rules "$RULES" --input "$TEST" --output "$OUT" \
  --strength 2.5 --gamma 0.5 --kgw-delta 3 \
  --max-prompt-tokens 6144 --preflight

VLLM_USE_V1=0 CUDA_VISIBLE_DEVICES=1 python wm_test/generate_wn_score.py \
  --student-model "$W" --tokenizer /shared/public_models/Qwen2.5-0.5B \
  --rules "$RULES" --input "$TEST" --output "$OUT" \
  --strength 2.5 --gamma 0.5 --kgw-delta 3 \
  --max-prompt-tokens 6144

CUDA_VISIBLE_DEVICES=1 python wm_test/evaluate_compare_metrics.py \
  --kgw-file "$OUT"
```

`--gamma 0.5 --kgw-delta 3` 供生成后 KGW 检测及元数据使用；WN 使用已有估计规则，不根据检测结果选择强度。以上采样参数沿用项目生成器设置。

评估继续使用原有 history 追加机制，包含此前已实现的 1K、2K、3K、10K、20K、30K 分组 p-value，以及排除严重重复回答的分组结果；这些评估代码未在此次调整中修改。已有 `strength=3` 结果可作为额外强度对照，主 baseline 使用 `2.5`。
