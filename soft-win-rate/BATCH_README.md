# 四文件连续评测

新增入口 `run_four_soft_win_rate.py`，原来的单文件脚本与默认输入不变。批量入口复用原程序的固定 clean 参照、Qwen3-32B 裁判、评分协议、自动选卡、进度条及缓存。

默认按以下顺序运行，不需要修改参数：

| 顺序 | 方法 | 相对于项目根目录的输入 |
|---|---|---|
| 1 | 未清洗（KGW GAD） | `wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.jsonl` |
| 2 | Para | `wm_test/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta3_new1_qwen2_5_0_5b_dolly15k_test.jsonl` |
| 3 | WN strength=2.5 | `wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new.jsonl` |
| 4 | WN strength=3 | `wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new_strength3.jsonl` |

固定参照继承单文件程序的 `REFERENCE_JSONL`，当前为 `wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl`。四份方法都与同一个参照比较；不会用前一个待测文件作为后一个的参照。每份 500 题、每题交换 A/B 两次，未缓存时共需 4000 次判断。

## 在服务器运行

把新脚本放在现有 `soft-win-rate/` 中，与 `run_soft_win_rate.py` 同级。在项目根目录、已有 `wm` 环境运行：

```bash
python soft-win-rate/run_four_soft_win_rate.py
```

要断开 SSH 后继续夜间运行：

```bash
nohup python -u soft-win-rate/run_four_soft_win_rate.py >> soft-win-rate/four_soft_win_rate_overnight.log 2>&1 &
```

查看进度：

```bash
tail -f soft-win-rate/four_soft_win_rate_overnight.log
```

程序先检查四份输入、ID 和完整问题都与参照严格匹配，再开始评分。每次只评测一个文件；当前文件结束后清理自己的模型 worker，再根据实时空闲显存为下一个文件选卡、加载裁判。进度包含当前文件编号与单文件判断数量。

单个文件启动报错、评分未完成时会记录状态，继续后面的文件。Ctrl+C 会停止整个批次并保存当前汇总；不会继续启动下一个文件。脚本不会结束其他 GPU 任务。

## 结果位置

- `soft-win-rate/four_soft_win_rate_history.md`：每次批量运行追加四种方法的比较表，包含完成状态、Soft Win Rate、95% CI、有效题目数和复用/新增判断数量。
- `soft-win-rate/soft_win_rate_history.md`：沿用单文件程序，逐文件追加完整结果、输入生成配置、裁判配置和实际 GPU 执行配置。
- `soft-win-rate/results/<输入名>.<协议哈希>/`：沿用单文件缓存；各方法有各自的逐判断缓存和 `runs/*.json` 独立结果。
- `soft-win-rate/results/batches/<本轮编号>/summary.json`：四份结果的完整汇总，包括独立结果路径、错误和耗时。
- 同目录 `summary.md`、`batch.log`：本轮可读汇总与完整父进程日志。具体 vLLM 日志路径仍由每份单文件评测打印。

本轮 `summary.json` 和 `summary.md` 在每份开始、结束时更新，异常中断时也能查看已经完成到哪一步。历史比较文档在本轮结束或 Ctrl+C 后追加；强制杀进程、关机时仍可从已有缓存续跑。

重新运行相同命令会自动读取已有成功缓存：已完成文件不会重新启动裁判；部分完成文件只补缺失判断。每次汇总保留为新记录，不覆盖旧结果。

表中的“未完成/失败”和 N/A 不代表胜率为零；有部分有效题目时会标注“部分”。正式比较应检查每行都为“完成”、完整题目数均为 `500/500`。退出码 0 表示本次选择的题目全部完成，1 表示仍有未完成/失败，130 表示 Ctrl+C 中断。

## 可选检查

```bash
# 检查四份数据与当前可行选卡方案，不加载裁判、不写结果
python soft-win-rate/run_four_soft_win_rate.py --check-only

# 每份先跑 5 题；之后全量运行会复用这些判断
python soft-win-rate/run_four_soft_win_rate.py --limit 5

# 仅从四份已有缓存生成汇总，不启动 GPU worker
python soft-win-rate/run_four_soft_win_rate.py --summary-only
```

批量入口与单文件入口共享成功缓存；同一批量结果目录有进程锁，避免误启动两份批次。Windows 本地已验证数据匹配与模拟评分流程；实际显存、模型启动和总耗时仍以服务器运行结果为准。
