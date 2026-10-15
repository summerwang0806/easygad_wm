记录 γ=0.5 下的八份运行结果；每份 KGW 500 条、clean 500 条。其中 δ=3 的两份 dipper2stage 运行因脚本修改未保存，标记为 DIPPER 未生效、待重跑，不计入有效 DIPPER 前后对照。

原表 δ=2 两行来自无 dipper 前缀的 kgwwarmup_kgwgad_* 文件，对应教师未经过 DIPPER 的结果；本次补入 dipper_upkgwwarmup_upkgwgad_* 的 δ=2 教师 para warmup/gad 两行。两组 checkpoint 路径分别为 gamma0.5_delta2 和 gamma0.5_delta2_dipper2stage。

教师 para 指训练所用教师文本经过 DIPPER 改写；δ=3 的四份记录均对应 new 配置。dipper2stage 目录名记录的是原定实验设置，不能代表实际使用了 DIPPER 数据。文件名、checkpoint 路径与评估时间列在下方来源中。

核对补充：用户确认服务器训练 sh 修改未保存。按未保存前的磁盘脚本，warmup 和 gad 均使用未para的 delta3_newtrain.parquet；因此撤回这两行的“教师para”分类，保留实际输出指标并标注待重跑。该判断依据用户确认及磁盘脚本，尚无当次运行配置可独立复核。详见 [δ=3 new 对照核对](delta3_new_verification.md)。

| 模型/方式 | AUROC | TPR@FPR≤5% | TPR@FPR≤10% | ROUGE-L（原始Dolly，500条） | ROUGE-L（clean教师，500条） | 严重重复输出¹ | p-value（均值） | p-value去重后（均值） |
| :---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| warmup（δ=2，教师未para） | 0.635794 | 12.80% | 21.60% | 0.206096 | 0.303203 | 26/500（5.20%） | 0.379972 | 0.380593 |
| gad（δ=2，教师未para） | 0.575170 | 4.80% | 12.20% | 0.214492 | 0.320875 | 12/500（2.40%） | 0.452520 | 0.434624 |
| warmup（δ=2，教师para） | 0.546198 | 7.60% | 11.80% | 0.203002 | 0.255151 | 52/500（10.40%） | 0.486092 | 0.516226 |
| gad（δ=2，教师para） | 0.555228 | 5.20% | 11.40% | 0.192682 | 0.266186 | 28/500（5.60%） | 0.474719 | 0.494142 |
| warmup（δ=3，教师未para） | 0.679584 | 19.00% | 30.00% | 0.204170 | 0.300920 | 28/500（5.60%） | 0.329666 | 0.338577 |
| gad（δ=3，教师未para） | 0.647688 | 11.40% | 22.80% | 0.198494 | 0.309174 | 11/500（2.20%） | 0.365777 | 0.347472 |
| warmup（δ=3，DIPPER未生效，待重跑） | 0.680012 | 21.80% | 31.00% | 0.199697 | 0.298178 | 29/500（5.80%） | 0.329854 | 0.326485 |
| gad（δ=3，DIPPER未生效，待重跑） | 0.641034 | 11.00% | 19.60% | 0.212690 | 0.304432 | 7/500（1.40%） | 0.373018 | 0.370250 |

¹ 严重重复：回答内部相邻 token 对的重复比例 >50%，即 1 − 唯一相邻 token 对数量 / 全部相邻 token 对数量 >0.5；不计 prompt 与回答之间的边界 token 对。使用本地 Qwen tokenizer JSON 及仓库既有 BPE 实现检查全部 4000 条回答，分词长度均与保存结果一致。

p-value 两列均为各模型 500 条回答的逐条单侧正态近似 p-value 的算术均值，不是 AUROC 的显著性检验。去重后仅按唯一 (previous_token_id, token_id) 对重算检测统计，不删除回答或修改文本。

两列 ROUGE-L 均取对应文件与评估时间匹配的本地历史记录，使用同批 500 条样本、逐条 F1 等权平均，use_stemmer=True；未独立重算 ROUGE-L。原始 Dolly 列参考 text_quality/references/dolly_human_500.jsonl（databricks/databricks-dolly-15k 的人工 response）；clean 教师列参考 data/dolly15k_qwen2_5_14b_clean_test.parquet。教师训练文本是否 para 不改变这两列的评估参考。

AUROC、TPR、原始/去重 p-value 均从本地保存结果复核；核对了样本 ID、prompt、检测配置、z-score/p-value 公式和 p-value 缓存源文件 SHA-256（统一 LF 换行后）。八组指标均与本地评估历史一致。

5% 工作点的实际 FPR：

- warmup（δ=2，教师未para）：4.80%。
- gad（δ=2，教师未para）：5.00%。
- warmup（δ=2，教师para）：4.60%。
- gad（δ=2，教师para）：4.60%。
- warmup（δ=3，教师未para）：4.80%。
- gad（δ=3，教师未para）：5.00%。
- warmup（δ=3，DIPPER未生效，待重跑）：5.00%。
- gad（δ=3，DIPPER未生效，待重跑）：5.00%。

八个 10% 工作点实际 FPR 均为 10.0%。

来源：

- warmup（δ=2，教师未para），2026-10-15T11:14:06+08:00：`kgwwarmup_kgwgad_warmup_gamma0.5_delta2_qwen2_5_0_5b_dolly15k_test.jsonl`；checkpoint：`/shared/wwx/EasyGAD/checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta2/warmup/global_step_1813/actor/huggingface`。
- gad（δ=2，教师未para），2026-10-15T11:21:37+08:00：`kgwwarmup_kgwgad_gad_gamma0.5_delta2_qwen2_5_0_5b_dolly15k_test.jsonl`；checkpoint：`/shared/wwx/EasyGAD/checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta2/gad/global_step_1813/actor/huggingface`。
- warmup（δ=2，教师para），2026-10-15T16:05:11+08:00：`dipper_upkgwwarmup_upkgwgad_warmup_gamma0.5_delta2_qwen2_5_0_5b_dolly15k_test.jsonl`；checkpoint：`/shared/wwx/EasyGAD/checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta2_dipper2stage/warmup/global_step_1813/actor/huggingface`。
- gad（δ=2，教师para），2026-10-15T16:12:14+08:00：`dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta2_qwen2_5_0_5b_dolly15k_test.jsonl`；checkpoint：`/shared/wwx/EasyGAD/checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta2_dipper2stage/gad/global_step_1813/actor/huggingface`。
- warmup（δ=3，教师未para），2026-10-15T11:38:32+08:00：`kgwwarmup_kgwgad_warmup_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.jsonl`；checkpoint：`/shared/wwx/EasyGAD/checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_new/warmup/global_step_1813/actor/huggingface`。
- gad（δ=3，教师未para），2026-10-15T12:01:50+08:00：`kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.jsonl`；checkpoint：`/shared/wwx/EasyGAD/checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_new/gad/global_step_1813/actor/huggingface`。
- warmup（δ=3，DIPPER未生效，待重跑），2026-10-15T20:08:49+08:00：`dipper_upkgwwarmup_upkgwgad_warmup_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.jsonl`；checkpoint：`/shared/wwx/EasyGAD/checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_new_dipper2stage/warmup/global_step_1813/actor/huggingface`。
- gad（δ=3，DIPPER未生效，待重跑），2026-10-15T19:57:15+08:00：`dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.jsonl`；checkpoint：`/shared/wwx/EasyGAD/checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_new_dipper2stage/gad/global_step_1813/actor/huggingface`。

原始评估历史：`wm_test/detection_metrics_history.md`。完整精度数值、checkpoint 路径与来源哈希保存在同目录 `metrics.json`。
