# No Attack 与 Pan 的 p-value 差异诊断

日期：2026-10-18。只核算保存的计数，没有加载模型或重跑 CUDA 检测。

**结论：本地未清洗 warmup 的逐回答 p 均值虽然为 0.330，但累计检测计数后已有很小的名义 p。逐回答 p 均值不是聚合水印显著性。**

## 本地结果

| 模型 | 逐回答 raw p 均值 | 逐回答 raw p 中位数 | 全部输出 N | G/N | 全部计数汇总名义 p |
|---|---:|---:|---:|---:|---:|
| No Attack warmup: gamma=.5 delta=3 new, teacher text not paraphrased | 0.329666 | 0.219151 | 113530 | 52.543821% | 3.58101e-66 |
| GAD: gamma=.5 delta=3 new, teacher text not paraphrased | 0.365777 | 0.238373 | 124556 | 52.091429% | 1.28104e-49 |
| Original base negative reference | 0.538121 | 0.57157 | 159765 | 46.092073% | 1 |

## 约固定预算的完整回答分组诊断

**这是近似计数诊断，不是 Pan 的精确分组复现。** 从原始顺序逐条累加完整回答，首次达到目标 token 数就结束一组，尾部不足目标丢弃。保留已有回答边界计数，不重建拼接边界。

| 模型 | 目标预算 | 组数 | 实际 N 范围 | 分组 p 中位数 | 上中位数（Pan 使用此选择规则） |
|---|---:|---:|---|---:|---:|
| No Attack warmup: gamma=.5 delta=3 new, teacher text not paraphrased | 10000 | 11 | 10001–10579 | 5.71983e-12 | 5.71983e-12 |
| No Attack warmup: gamma=.5 delta=3 new, teacher text not paraphrased | 20000 | 5 | 20021–20429 | 1.69324e-20 | 1.69324e-20 |
| No Attack warmup: gamma=.5 delta=3 new, teacher text not paraphrased | 30000 | 3 | 30044–30488 | 5.79281e-34 | 5.79281e-34 |
| GAD: gamma=.5 delta=3 new, teacher text not paraphrased | 10000 | 12 | 10003–10517 | 0.000116052 | 0.000223573 |
| GAD: gamma=.5 delta=3 new, teacher text not paraphrased | 20000 | 6 | 20048–20540 | 6.06167e-09 | 1.20639e-08 |
| GAD: gamma=.5 delta=3 new, teacher text not paraphrased | 30000 | 4 | 30080–30508 | 4.24952e-11 | 8.37447e-11 |
| Original base negative reference | 10000 | 15 | 10001–11307 | 1 | 1 |
| Original base negative reference | 20000 | 7 | 20034–21415 | 1 | 1 |
| Original base negative reference | 30000 | 5 | 30007–30926 | 1 | 1 |

## 必须保留的边界

- 小 p 受检测预算、重复和理论零分布校准影响，不能直接理解为水印残留百分比。
- base 负例约 10k 分组中有 2/15 组出现 p≤.05；有一组 p≈7.58e-74，提示 raw 理论 p 的误报与重复敏感性。
- 逐回答去重后再累加的 warmup 约 10k 诊断中位 p≈1.69e-8，说明小 p 不仅存在于 raw 统计；但这仍未做跨回答全局去重。
- Pan 的 200k QA、3 epochs、LR=1e-5 与本地约14511条数据、脚本默认1 epoch及LR=1e-6存在差异；本地历史 delta3_new 完整运行配置未在本轮取得，脚本默认不能代替运行证据。
- 本地学生 Qwen2.5-0.5B；Pan 学生 Llama-7b/Llama-3.2-1b。评测提示为 Dolly vs C4。
- 本地教师实际模型来源尚不能仅凭文件名含14b确认；保存的教师 scores 显示训练文本加权绿比例约69.17%，warmup输出约52.54%。

## 数据来源

- C:\Users\wenxin\Desktop\distall-watermark\my_easygad\wm_test\kgwwarmup_kgwgad_warmup_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.jsonl
- C:\Users\wenxin\Desktop\distall-watermark\my_easygad\wm_test\kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.jsonl
- C:\Users\wenxin\Desktop\distall-watermark\my_easygad\wm_test\base_qwen2_5_0_5b_dolly15k_test_gamma0.5.jsonl

Pan: https://aclanthology.org/2025.acl-long.648.pdf
官方分组流程: https://github.com/THU-BPM/Watermark-Radioactivity-Attack/blob/main/detect.py
