## 四文件评测 20261029T150611Z_7a5e258c

开始：2026-10-29T23:06:11+08:00；结束：2026-10-30T00:34:14+08:00；范围：全量。
本轮状态：尚未全部完成；固定参照：`/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl`。
裁判：`/shared/public_models/Qwen3-32B`；胜=1、平=0.5、负=0，逐题双顺序平均。

| 方法 | 状态 | Soft Win Rate ↑ | 95% CI | 完整题目 | 复用/新增判断 |
|---|---|---:|---|---:|---:|
| kgw_gad | 未完成 | N/A | N/A | 0/500 | 0/0 |
| Para | 完成 | 29.00% | [26.05%, 31.95%] | 500/500 | 0/1000 |
| WN strength=2.5 | 完成 | 45.60% | [42.20%, 48.80%] | 500/500 | 0/1000 |
| WN strength=3 | 完成 | 41.30% | [38.00%, 44.60%] | 500/500 | 0/1000 |

未完成行的分数只覆盖已完成双顺序的题目；N/A 表示没有有效胜率。

- kgw_gad：`/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.jsonl`
  错误：Local judge failed: preflight: ValueError: Judge input too long for task d68b9d910c33ec16de6a702d6d8744c539110ed4a89368ff05755072a6219023: prompt=8646, output_budget=512, window=8192; no text was truncated Worker log: /shared/wwx/EasyGAD/soft-win-rate/results/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_t.3f9b9cdd137cd71b/workers/20261029T230612_203960f1/plan_00/worker.log
  独立结果 JSON：`/shared/wwx/EasyGAD/soft-win-rate/results/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_t.3f9b9cdd137cd71b/runs/20261029T150616Z_5ae21a95.json`
- Para：`/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta3_new1_qwen2_5_0_5b_dolly15k_test.jsonl`
  独立结果 JSON：`/shared/wwx/EasyGAD/soft-win-rate/results/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta3_new1_qwen2_5_0_5.d5bf1ff1da3c4875/runs/20261029T153339Z_dbdc5156.json`
- WN strength=2.5：`/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new.jsonl`
  独立结果 JSON：`/shared/wwx/EasyGAD/soft-win-rate/results/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new.749dd5f83f50df52/runs/20261029T160528Z_fdf4bb0f.json`
- WN strength=3：`/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new_strength3.jsonl`
  独立结果 JSON：`/shared/wwx/EasyGAD/soft-win-rate/results/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new_strength3.5583d512fdbd114a/runs/20261029T163413Z_2b1d21cd.json`

逐文件详细记录：`/shared/wwx/EasyGAD/soft-win-rate/soft_win_rate_history.md`。
本轮汇总 JSON：`/shared/wwx/EasyGAD/soft-win-rate/results/batches/20261029T150611Z_7a5e258c/summary.json`。
本轮完整日志：`/shared/wwx/EasyGAD/soft-win-rate/results/batches/20261029T150611Z_7a5e258c/batch.log`。

