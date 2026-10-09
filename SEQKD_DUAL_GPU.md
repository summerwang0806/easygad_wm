# SeqKD 双卡运行说明（2026-10-03）

## 已定位的问题

在 wm 环境里，GPU 2+3 使用默认 NCCL P2P/CUMEM 传输时，最小 all-reduce 测试超时；仅禁用 cuMem、改走 P2P/IPC 也未完成。
设置 NCCL_P2P_DISABLE=1 后，同一组 GPU 的 all-reduce 和 broadcast 都通过，实际传输改为 SHM/direct/direct。
因此已确认本机这组卡的 NCCL P2P 传输路径存在运行问题；这不等于已经确认底层驱动、PCIe 或 BIOS 的具体故障。

0+3 默认通信测试也通过。检查时 0 号卡空闲，优先建议 0+3。GPU 占用会变化。

## 脚本修复

修改文件：scripts/train/run_full_seqkd_optimized.sh

- 默认导出 NCCL_P2P_DISABLE=1，绕过有问题的 P2P 路径；只对本次启动的进程生效。
- 默认 CUDA_DEVICE_ORDER=PCI_BUS_ID，稳定 GPU 编号。
- CUDA_VISIBLE_DEVICES 未设置时默认 0,3；明确设置时尊重指定卡号。
- 自动根据可见 GPU 列表确定每台卡数，也支持 --gpus_per_node。
- --nnodes 1 仍表示一台服务器，不要因为用两张卡而改成 2。
- Ray 临时目录仍在 /shared/wwx/EasyGAD/ray_tmp。
- 保留 SwanLab 凭据及 logger；关闭 shell 命令回显，避免输出密钥。
- -- 后可追加 Hydra 参数覆盖，用于短测等场景。

原脚本备份：scripts/train/run_full_seqkd_optimized.sh.bak.20261003_dualgpu

## 正式训练指令

在服务器执行，实验名请使用新的名称，避免自动恢复旧的单卡 checkpoint：

```bash
cd /app/wwx/EasyGAD
conda activate wm

CUDA_VISIBLE_DEVICES=0,3 bash scripts/train/run_full_seqkd_optimized.sh \
  --model /shared/public_models/Qwen2.5-0.5B \
  --exp_name te_old_st_Qwen2.5-0.5B_SeqKD_kgwdata_epoch2_dualgpu_03 \
  --nnodes 1 \
  --gpus_per_node 2 \
  --total_epochs 2
```

如果使用 2+3，只需将 CUDA_VISIBLE_DEVICES 改为 2,3，并使用另一个新的实验名；无需再编辑脚本中的卡数。
如果使用单卡，例如 0 号卡，设置 CUDA_VISIBLE_DEVICES=0 和 --gpus_per_node 1。

## 训练设置与测试范围

学习率 1e-6、全局 batch size 8、默认 2 epoch、CRITIC_WARMUP=10 均保持原值。
CRITIC_WARMUP=10 会使 SeqKD 前 9 个 step 不更新学生；这是此前选择的实验设置，与双卡通信故障无关。
如果要与已有 1 epoch Warmup 比较，需要将 --total_epochs 改为 1，并使用相应的新实验名。

0+3 和 2+3 均完成 12 步真实训练短测、退出码均为 0；第 10–12 步均有 actor loss、梯度范数和参数更新耗时。
短测禁用了验证、checkpoint 保存和 SwanLab 上传，只使用 console，未创建正式训练实验。
日志：diagnostics/seqkd_dualgpu_smoke_20261003_0_3.log
日志：diagnostics/seqkd_dualgpu_smoke_20261003_2_3.log

双卡不保证速度翻倍。0.5B 模型、batch size 8 下，通信有额外开销，而且此实现仍执行学生文本生成。
0+3 短测第 10–12 步约 4.8–7.0 秒/步，其中生成约 4.3–6.1 秒；这些短测不是与单卡严格匹配的速度对照。
正式运行至少观察几十个更新 step 后，再用平均耗时估算整轮时间。
2+3 短测第 10–12 步约 7.4–10.0 秒/步；本次短测优先推荐 0+3，但不将少量 step 的差异视为固定加速比。
