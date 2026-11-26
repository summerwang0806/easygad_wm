# WM-Basin 复现代码（EasyGAD / KGW 适配版）

本目录实现了论文 *Watermark Basins: Black-Box Detection of Distilled LLMs* 的黑盒检测流程，专门适配你的 EasyGAD 实验配置：
- **教师模型**：`/app/public_models/Qwen2.5-14B-Instruct`
- **水印方案**：KGW (`gamma=0.5, delta=3.0, simple_1`, CUDA RNG, `k*=15485863`)，直接复用 `wm_data/kgw.py`
- **最佳探针模型**：`/app/public_models/Qwen2.5-0.5B` 基座版（LoRA `r=128, alpha=256, epochs=4` 预热后冻结）+ `proj_dim=131072` 随机投影
- **学生模型**：你的微调 `Qwen2.5-0.5B` 及各类对照模型
- **数据划分**：外部通用指令集（`yahma/alpaca-cleaned`，与 Dolly 去重）划出互不重叠的 `X_build` 与同源测试集 `X_test_ext.jsonl`（500 条 × 4 次采样，推荐主用）；同时保留 `data/dolly15k_test.parquet` 作跨源测试集 `X_test.jsonl`

所有脚本均支持**断点续跑**和**增量扩充**（先跑 40 密钥 + 10 Clean 模型 Pilot，确认有效后再追加到 100 密钥 + 20 Clean 模型，前面算好的全部复用）。

---

## 一、Pilot 阶段（40 密钥 + 10 Clean 模型，半天出第一批结果）

在服务器 `EasyGAD` 根目录执行（按你的 `nvidia-smi`：**GPU1=80G 跑 14B 教师，GPU0=40G 跑探针和中小模型**）：

```bash
conda activate wm
cd ~/EasyGAD
```

### Step 0：准备 Prompt 池与密钥表（CPU，几十秒）
```bash
# 如果服务器能连 HF（或已设 HF_ENDPOINT=https://hf-mirror.com）：
python wm_basin/00_prepare_pools.py \
  --work-dir wm_basin_work \
  --num-keys 40

# 如果本地已有 alpaca_data_cleaned.json，直接传 --alpaca-path 即可：
# python wm_basin/00_prepare_pools.py --work-dir wm_basin_work --num-keys 40 --alpaca-path /path/to/alpaca_data_cleaned.json
```

### Step 1：教师生成干净预热集 + 40 个密钥的 KGW 参考库（GPU1，约 1–2 小时）
```bash
CUDA_VISIBLE_DEVICES=1 python wm_basin/01_gen_teacher.py \
  --work-dir wm_basin_work \
  --mode both \
  --teacher-model /app/public_models/Qwen2.5-14B-Instruct \
  --key-start 0 --key-end 40 \
  --gpu-memory-utilization 0.72
```
> 提示：可先跑 `--mode warm`（约 3 分钟）让 GPU0 提前开始 Step 3 预热探针，同时 GPU1 并行跑 `--mode bank`。

### Step 2：生成 Clean PCA 池（Pilot 10 模型 × 3 温度 = 30 cell，GPU0，约 30–50 分钟）
```bash
CUDA_VISIBLE_DEVICES=0 python wm_basin/02_gen_clean_pool.py \
  --work-dir wm_basin_work \
  --models-dir /app/public_models \
  --preset pilot \
  --gpu-memory-utilization 0.72
```

### Step 3：LoRA 预热探针模型（GPU0，约 10–15 分钟）
```bash
CUDA_VISIBLE_DEVICES=0 python wm_basin/03_warm_probe.py \
  --work-dir wm_basin_work \
  --probe-model /app/public_models/Qwen2.5-1.5B-Instruct \
  --lora-r 32 --epochs 2 --lr 2e-4
```

### Step 4：提取 Bank 与 Clean Pool 的 8,192 维梯度（GPU0，约 40–60 分钟）
```bash
CUDA_VISIBLE_DEVICES=0 python wm_basin/04_extract_grads.py \
  --work-dir wm_basin_work \
  --target both \
  --batch-size 4
```

### Step 5：拟合 Clean 任务子空间 PCA & 交叉验证 FPR 校准（CPU，几秒）
```bash
python wm_basin/05_fit_pca.py \
  --work-dir wm_basin_work \
  --q 15 \
  --sweep-q 0 5 10 15 20
```
查看打印的 `median_FPR / p90 / worst`，确认在 `alpha=0.05` 下校准正常。

### Step 6：审计你的待测学生与阴性对照（GPU0，每个模型约 5–10 分钟）
```bash
# 示例 1：阴性对照（原始 0.5B 基座）
CUDA_VISIBLE_DEVICES=0 python wm_basin/06_gen_and_score_suspect.py \
  --work-dir wm_basin_work \
  --suspect-name base_qwen25_05b \
  --suspect-model /app/public_models/Qwen2.5-0.5B

# 示例 2：阴性对照（clean warmup + clean GAD）
CUDA_VISIBLE_DEVICES=0 python wm_basin/06_gen_and_score_suspect.py \
  --work-dir wm_basin_work \
  --suspect-name clean_gad_control \
  --suspect-model checkpoints/<你的clean对照路径>/actor/huggingface

# 示例 3：待测水印学生（KGW warmup + KGW GAD / SeqKD / 改写攻击等）
CUDA_VISIBLE_DEVICES=0 python wm_basin/06_gen_and_score_suspect.py \
  --work-dir wm_basin_work \
  --suspect-name kgw_gad_student \
  --suspect-model checkpoints/<你的KGW学生路径>/actor/huggingface
```
结果保存在 `wm_basin_work/suspects/<suspect-name>/score.json`，同时会在终端打印 `rank`、`p_rank`、`z_score` 及 5% 档判定。

---

## 二、正式版增量扩充（40 → 100 密钥，10 → 20 Clean 模型，零返工）

Pilot 跑通后，直接按下面命令**增量补齐**（已存在的文件全部自动跳过）：

```bash
# 1. 把 keys.json 从 40 扩到 100（保留前 40 个不变，只追加 60 个新诱饵）
python wm_basin/00_prepare_pools.py --work-dir wm_basin_work --num-keys 100 --only-expand-keys

# 2. 只生成新增的 60 个诱饵密钥（GPU1）
CUDA_VISIBLE_DEVICES=1 python wm_basin/01_gen_teacher.py \
  --work-dir wm_basin_work --mode bank --key-start 40 --key-end 100

# 3. 补齐剩余 10 个 Clean 模型（GPU0/GPU1）
CUDA_VISIBLE_DEVICES=0 python wm_basin/02_gen_clean_pool.py \
  --work-dir wm_basin_work --preset full

# 4. 只提取新增密钥与新增 Clean 模型的梯度（自动跳过已算过的）
CUDA_VISIBLE_DEVICES=0 python wm_basin/04_extract_grads.py \
  --work-dir wm_basin_work --target both

# 5. 重新拟合 PCA（60 cell 支持 q=20~30）
python wm_basin/05_fit_pca.py --work-dir wm_basin_work --q 20 --sweep-q 0 5 10 15 20 30

# 6. 一秒重算所有已采样学生的分数（无需重新生成文本或重算梯度！）
python wm_basin/06_gen_and_score_suspect.py \
  --work-dir wm_basin_work --suspect-name kgw_gad_student --only-score
```

---

## 三、本地单元测试
```bash
python -m unittest wm_basin/tests/test_wm_basin.py -v
```
