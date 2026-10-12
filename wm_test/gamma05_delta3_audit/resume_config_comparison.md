核对范围：旧 `kgw_gad_05b_14b_full`（γ=0.25、δ=2）与当前 `te_old_st_Qwen2.5-0.5B_gamma0.5_delta3`（γ=0.5、δ=3）。用户确认进入 GAD 时崩溃、随后添加断点恢复的是当前实验。只核对新旧配置及恢复代码，没有修改训练代码，也没有按原论文修复实现。

更新结论（服务器记录已核对）：新旧 warmup、GAD 的训练超参数一致。恢复后 GAD 从当前 warmup 1813 的 actor/critic 权重初始化，再从第 1 步开始；没有加载旧 GAD optimizer/data.pt，没有误用 warmup optimizer，也没有重复训练完整 warmup。补丁实际改变了恢复模式和 Ray CPU 配置，未改变 actor/critic/GRPO/PPO/merge 核心代码。尚未读取服务器原教师数据文件，不能把参数一致等同于所有实验输入已逐字节验证。

从四份 TaskRunner 日志解析完整 Hydra 配置，每份比较 342 个安全叶字段。旧、新 warmup 只有：

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

服务器 `resume_audit.json` 新增证据：两阶段 tracker 均为 1813，warmup `.stage_completed` 为 1813，两阶段选中目录的 `data.pt` 及 actor/critic 两个 rank 的 model、optimizer、extra state 文件均存在。warmup actor/critic HF 完成标记均存在；GAD 缺少同名 merge 标记不表示训练失败，这个标记由训练脚本准备 warmup HF 导出时写入。

新旧 GAD 的完整实际配置 342 项中 332 项相同，10 项差异为：4 个 actor/critic/tokenizer 初始化路径换到当前 warmup 1813、2 个 train/val 数据路径、实验名与输出目录、`trainer.resume_mode: disable → auto`、`ray_init.num_cpus: null → 8`。Ray CPU 的 null 传给 ray.init 表示不显式限定 CPU 数；不能把 null 与显式 8 写成相同。以下训练参数均一致：

| 参数 | 旧、新 GAD 实际值 |
|---|---|
| actor / critic 学习率 | 1e-6 / 1e-5 |
| train batch / PPO mini-batch | 8 / 8 |
| rollout n / temperature / top_p / top_k | 2 / 0.8 / 1 / -1 |
| prompt / response 上限 | 2048 / 1536 |
| epoch / 总训练步数 | 1 / 1813 |
| loss / advantage | clip_cov / GRPO |
| use_kl_loss / use_kl_in_reward / entropy_coeff | false / false / 0 |
| critic_warmup（GAD） | 0 |

关键实际日志是 `/tmp/easygad-wwx/ray/session_2026-10-10_10-37-55_080570_642631/logs/worker-fa3e63716174a0aa78d8a9011ff47206dbaa52519d833b6b3cd61980-01000000-644781.out`：354 行总步数 1813，365 行 `Training from scratch`，559 行首个更新 step 1，3893 行保存 GAD 1813，3894 行最后更新 step 1813。配置中的 actor、critic 初始化都指向当前实验 warmup 1813。auto 查不到 GAD 保存点后从头启动 GAD，是这个流程预期的行为；它不会从基座重新做 warmup，也不会加载 warmup optimizer。收集到的当前 GAD 会话没有模型/optimizer checkpoint 恢复事件。

服务器当前 7 个源码 LF SHA256 与本地完全相同；其中 actor、critic、core_algos、fsdp_workers、merge_model2hf 也与旧实验版本及补丁前版本相同。源码 hash 记录的是采集时版本，不单独证明任意历史时刻的代码；结合实际配置和日志，没有发现本次恢复引入训练参数漂移或错误阶段状态加载。

此前诊断需修正：KL 缺失、UID 去重等行为在旧实验也存在，不能解释为这次恢复补丁引入的新差异。新 warmup 严重重复已经由旧实验 5.2% 变成 20.8%，而它尚未进入 GAD 恢复，因此不能把全部退化归于 GAD 续传。

训练日志也独立证明质量恶化：旧、新 GAD 首批 prompt_length 的均值/最大/最小同为 52.750/61/47；新首批回答均长 470.125、长度截断比例 25%，旧为 331.250、0%。这不是首批文本重复率，只能证明新 warmup 初始策略已有长度异常。新 step1812 所有回答均达 1536 上限；最终 step1813 截断比例 87.5%，训练验证 ROUGE-L=.035，旧最终截断比例 0、验证 ROUGE-L=.323。训练验证以 KGW 教师为参考，与表格中的 500 条采样对 clean 教师的 ROUGE 不是同一列。新最终 critic 学生评分 -45.5、教师 16.094，不能说 critic 给崩溃学生很高的绝对评分。

用户已提供两组教师生成命令：均为 wm_data/generate_kgw.py，均不显式传 --model，hash_key 均为 15485863；旧 gamma=.25/delta=2，新 gamma=.5/delta=3，新示例 num_gpus=2。按已保存的 9/29 版本及当前版本默认值，两条命令默认教师为 `/shared/public_models/Qwen2.5-0.5B`；14b 是输出文件名，不决定模型。没有从命令中发现教师模型切换；尚不能用后来保存的源码单独认证历史执行文件。默认采样和 prompt 渲染代码一致。多 GPU 实现按 global_start+offset 计算逐条索引，以 base_seed+global_index 设 seed，并合并连续分片后检查 ID 顺序；没有因 worker 分片重置 seed 或错配顺序的代码。并行批形状和硬件执行不同不保证逐字采样相同。实际 train/test 文件的 id/content/顺序仍需一次只读摘要核对。

已准备 `wm_test/collect_teacher_comparison.py`：在服务器 wm 环境运行即可比较四个默认教师 parquet，保存 `teacher_comparison.json`。它仅读取 id/content/teacher_response、schema 及可用生成 metadata，输出对齐/分布摘要，没有 GPU 模型加载。文本词 4-gram 重复诊断与表中的 token-bigram 严重重复不是同一口径。脚本本地语法与 CLI 验证通过；本机没有真实教师文件和 pyarrow，未假称完成真实数据审计。

完整 warmup 旧证据见同目录 `old_new_config_comparison.json`；包含服务器 GAD 实际配置、精确差异、路径记录与源码 hash 的更新证据见 `server_gad_config_comparison.json`。

本地验证：现有断点恢复回归测试 19 项通过（临时目录及模拟训练，不运行 GPU 训练）；服务器返回记录另包含实际成功 GAD 的 342 项配置与首末训练指标。没有加载/重算物理模型权重，也没有编辑训练代码。
