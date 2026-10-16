δ=3 new / DIPPER new 对照核对，2026-10-15。

表格取用的是 `gamma0.5_delta3_new` 和 `gamma0.5_delta3_new_dipper2stage` 两组 checkpoint，没有混入旧 `gamma0.5_delta3`。用户最新确认服务器训练脚本在启动前没有保存修改，因此两份 `new_dipper2stage` 结果现标为“DIPPER 设置未生效／待重跑”，不能视为有效的 DIPPER 前后对照。本结论依据用户确认与当前磁盘脚本，未获得当次实际运行的 Hydra 配置或日志。

| 方式 | 无 DIPPER 前缀 AUROC | new_dipper2stage AUROC（DIPPER 设置未生效／待重跑） | 两次运行之差 | TPR@FPR≤5% | TPR@FPR≤10% |
| --- | ---: | ---: | ---: | --- | --- |
| warmup | 0.679584 | 0.680012 | +0.000428 | 19.0% → 21.8%（95 → 109 条） | 30.0% → 31.0%（150 → 155 条） |
| gad | 0.647688 | 0.641034 | -0.006654 | 11.4% → 11.0%（57 → 55 条） | 22.8% → 19.6%（114 → 98 条） |

现有两次运行中，warmup 的 AUROC 增加 0.000428，gad 下降 0.006654；这些数值保留为已经完成的运行结果，不归因于 DIPPER。原配对 bootstrap（10000 次，seed=20261015；同一正类 ID 抽样索引用于两个模型，另独立重抽共享 clean 样本）得到 AUROC 差的 95% 百分位区间：warmup [-0.0180224, 0.0192702]，gad [-0.0303404, 0.01685445]。两区间均包含 0。该分析只评估两个已保存输出之间的差异及测试样本抽样不确定性，不涵盖训练随机性，也不能解释 DIPPER 效果。

四份结果各有 500 条，ID、顺序、prompt 与共享 clean 对照一致；逐 ID seed 均为 42–541。生成参数一致：temperature=0.7、top_p=0.9、max_new_tokens=1536、max_prompt_tokens=2048，生成时均未额外施加 KGW。检测 gamma=0.5、hash_key=15485863、simple_1 一致。保存 z/p 公式、缓存源文件 SHA-256（统一 LF 换行）、缓存 ID/z/p 均核对一致。warmup 的 5% 工作点实际 FPR 为 4.8% → 5.0%，其余 5% 工作点为 5.0%，所有 10% 工作点为 10.0%。

结果文件对应的 checkpoint：

- 未带 DIPPER 前缀的 warmup/gad：`checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_new/{warmup,gad}/global_step_1813/actor/huggingface`。
- 带 DIPPER 前缀的 warmup/gad（DIPPER 设置未生效／待重跑）：`checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_new_dipper2stage/{warmup,gad}/global_step_1813/actor/huggingface`。

DIPPER 数据本身的 new 谱系已核实：[数据审计](C:/Users/wenxin/Desktop/distall-watermark/my_easygad/data/dolly15k_qwen2_5_14b_kgw_gamma0.5_delta3_up_dipper_newtrain.parquet.audit.json:9) 明确输入 `delta3_newtrain.parquet`，输出 `delta3_up_dipper_newtrain.parquet`。重新计算输入/输出文件 SHA-256，与审计完全一致。14511 条保留原 ID 和顺序，其中 14461 条教师回答改变，50 条相同，无丢弃。旧 `delta3_up_dipper_train.parquet` 的审计输入则是旧 `delta3_train.parquet`，并非同一个数据文件。

训练来源的缺口：[README 启动示例](C:/Users/wenxin/Desktop/distall-watermark/my_easygad/README.md:145) 调用 `run_full_gad_optimized.sh`，仅用 `--exp_name` 指定 `delta3_new_dipper2stage`。当前本地脚本 [第 58 行](C:/Users/wenxin/Desktop/distall-watermark/my_easygad/scripts/train/run_full_gad_optimized.sh:58) 仍将 TRAIN_FILE 设为未改写的 `delta3_newtrain.parquet`；两阶段分别在第 287、417 行使用该变量。实验名字不选择训练数据。

用户最新确认：服务器 `run_full_gad_optimized.sh` 的修改在启动训练前没有保存。若服务器磁盘上的 `TRAIN_FILE` 与当前本地脚本一样仍是 `data/dolly15k_qwen2_5_14b_kgw_gamma0.5_delta3_newtrain.parquet`，则 warmup 和 gad 两阶段都会读取未 para 的 new 数据；它不是旧版 `delta3_train.parquet`。因此，实验名中的 `dipper2stage` 不能证明使用了 DIPPER 文本，本次将其按 DIPPER 设置未生效处理并等待重跑。此判断来自用户对未保存的确认和当前磁盘脚本，未声称取得当次实际运行日志。本地未找到 new/new_dipper2stage 当次训练的 Hydra 配置。

之前表格中的“教师 para”依据实验说明及文件/checkpoint 命名，未独立核实当次训练输入。最新结论是这两份结果不能作为有效 DIPPER 前后对照；本记录保留全部数值，标明“DIPPER 设置未生效／待重跑”，不删除现有结果，不将数值变化归因于 DIPPER。有效重跑应在启动前保存 `TRAIN_FILE=data/dolly15k_qwen2_5_14b_kgw_gamma0.5_delta3_up_dipper_newtrain.parquet`，并以两阶段运行时记录的 `data.train_files` 核实。

后续修正（2026-10-15，git pull 后 commit `0b29ec5`）：当前本地 `run_full_gad_optimized.sh:58` 已保存为 `delta3_up_dipper_newtrain.parquet`，第59行验证集仍为 `delta3_newtest.parquet`，两阶段均使用这一训练/验证路径。先前关于“当前脚本仍指向未para”的描述记录的是修正前版本。已核对新命令使用 GPU 0,3、默认双卡单节点、新实验名 `te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_new1_dipper2stage`，默认不续训，从原始 Qwen2.5-0.5B 进行 warmup，再用本次 warmup checkpoint 进入 GAD。DIPPER parquet 哈希仍与审计匹配。新命令的静态配置正确；旧两份 DIPPER 未生效结果的历史标记保留，新结果尚待实际训练与评估。


2026-10-16：new1 补跑结果

本次拉取的 warmup/gad 输出均指向 te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_new1_dipper2stage，对应已修正 TRAIN_FILE 后提交的新实验。按已保存脚本、用户提交命令及结果路径归类为教师 DIPPER para；未独立取得服务器当次运行配置。

| 模型/方式 | AUROC | TPR@FPR≤5% | TPR@FPR≤10% | ROUGE-L（原始Dolly，500条） | ROUGE-L（clean教师，500条） | 严重重复输出¹ | p-value（均值） | p-value去重后（均值） |
| :---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| warmup（δ=3，教师para，new1） | 0.546344 | 5.20% | 11.00% | 0.195773 | 0.251185 | 42/500（8.40%） | 0.484232 | 0.503516 |
| gad（δ=3，教师para，new1） | 0.531456 | 3.80% | 8.40% | 0.211098 | 0.262207 | 15/500（3.00%） | 0.505501 | 0.516716 |

已复核样本、源文件哈希、AUROC/TPR、原始与去重 p-value；ROUGE-L 取匹配历史记录。new1 逐条分词复核 1000/1000 通过，严重重复 warmup 42/500、gad 15/500。旧 delta3_new_dipper2stage 两份保留为历史误跑，主表对应位置由 new1 填入。
