核对范围：旧 `kgw_gad_05b_14b_full`（γ=0.25、δ=2）与当前 `te_old_st_Qwen2.5-0.5B_gamma0.5_delta3`（γ=0.5、δ=3）。用户确认进入 GAD 时崩溃、随后添加断点恢复的是当前实验。只核对新旧配置及恢复代码，没有修改训练代码，也没有按原论文修复实现。

目前结论：旧、新 warmup 的实际训练配置一致，仅数据路径与实验名称/目录有四处差异；没有发现断点恢复补丁修改训练算法或超参数。当前 GAD 的实际恢复日志仍在服务器，尚不能宣告整个实验严格只改变了 γ、δ。

从三份 TaskRunner 日志解析完整 Hydra 配置，每份比较 342 个安全叶字段。旧、新 warmup 只有：

| 字段 | 旧 | 当前 |
|---|---|---|
| data.train_files | data/dolly15k_qwen2_5_14b_kgw_train.parquet | data/dolly15k_qwen2_5_14b_kgw_gamma0.5_delta3_train.parquet |
| data.val_files | data/dolly15k_qwen2_5_14b_kgw_test.parquet | data/dolly15k_qwen2_5_14b_kgw_gamma0.5_delta3_test.parquet |
| trainer.default_local_dir | checkpoints/kgw_gad_05b_14b_full/warmup | checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta3/warmup |
| trainer.experiment_name | kgw_gad_05b_14b_full_warmup | te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_warmup |

两者 actor LR=1e-6、critic LR=1e-5、batch=8、warmup rollout n=1、temperature=0.8、两张 GPU、1 epoch、prompt/response 上限 2048/1536，resume_mode=disable。新 warmup 从头完成 1813 步。旧 GAD 日志也证明旧实验执行了真正的 GAD 更新并保存到 1813，并非把 warmup 文件误标为 GAD。

可核对的 Git 归因：

- `328b937 → 8d151db`：换到 γ=0.5、δ=3 数据路径；拆出 LR_warmup=1e-6，但此前 LR 也是 1e-6，实际学习率没有改变。这在恢复补丁之前。
- `8d151db → a0aab6b`：加入 resume/skip_warmup、按 tracker 选保存点、warmup 完成标记、HF merge 完成后复用、Ray 临时目录与 CPU 参数、完成阶段提前返回。Ray 默认目录改变可以解释恢复日志未在旧 ray_tmp 路径中找到。
- actor、critic、GRPO/PPO core、FSDP worker、HF merge 五个核心文件在三个版本中 Git blob 完全一致。ray_trainer 仅增加六行“加载后已完成则直接返回”，没有改变 optimizer、scheduler 或 RNG 的恢复算法。

恢复路径：

1. 如果只有 warmup 保存点、没有 GAD tracker：GAD 从选定 warmup HF actor/critic 权重初始化，再创建 GAD 自己的新 optimizer/scheduler；GAD 的 auto 模式只查当前 `/gad`，不会误读 warmup 的 optimizer/data.pt。
2. 如果已有 GAD 保存点：从当前 `/gad/global_step_N` 恢复模型、optimizer、scheduler、RNG 与 dataloader；不会把 warmup 优化器当成 GAD 优化器。
3. tracker 在 actor、critic 和 data.pt 保存后写入；最大编号目录本身不能代替 tracker。HF merge 算法未变，没有训练操作；首次恢复旧目录没有 marker 时重新导出一次，之后复用该 checkpoint 目录内的完成导出。

截图新增证据：用户服务器目录显示 warmup/gad 均有 500、1000、1500、1813，warmup 有 `.stage_completed`，两阶段有 tracker。尚未读到 tracker 的数字、实际文件内容及恢复日志，所以不能仅凭截图确认加载源或整个训练轨迹。

此前诊断需修正：KL 缺失、UID 去重等行为在旧实验也存在，不能解释为这次恢复补丁引入的新差异。新 warmup 严重重复已经由旧实验 5.2% 变成 20.8%，而它尚未进入 GAD 恢复，因此不能把全部退化归于 GAD 续传。

下一步只需服务器的小型证据：两阶段 tracker/完成标记、选中保存点的 actor/critic config、恢复后 TaskRunner 实际配置与加载记录。`wm_test/collect_resume_audit.py` 只读收集这些并导出 JSON，不加载大权重、不修改 checkpoint。另需新旧教师实际生成参数，才能确认数据文件虽然名称不同，实际是否仅改变 γ、δ；文件名中的 14b 不能证明实际教师模型。当前本地没有原教师 parquet 或命令记录。

完整配置比较与代码 blob 证据见同目录 `old_new_config_comparison.json`。

本地验证：现有断点恢复回归测试 19 项通过（临时目录及模拟训练，不运行 GPU 训练）；采集脚本在本地旧 Ray 目录试运行，提取当前 warmup 的 342 个安全字段，与上述实际配置白名单逐项一致。它未找到当前成功 GAD 的配置，符合现有日志只包含 GAD 启动失败的情况。上述验证不能代替服务器真实恢复日志或物理权重核验。
