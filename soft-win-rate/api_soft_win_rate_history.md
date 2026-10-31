
## API 评测记录：2026-10-30T16:37:53+08:00（20261030T083753Z_c4e4b1c7）

- 待测文件：`/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.jsonl`；SHA256 `618df1162dbd1bbf770b90baabfd23226ef52fd3028f5fdb6490919cca78b92e`
- 固定 clean 参照：`/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl`；SHA256 `dd4cfdbe540e2227bbad3b46f6a64e34bb1a46b7e7d24860ef8be90ec03efd48`
- API 裁判：`gpt-5.5`；接口：`http://43.159.131.189:8080/v1/responses`
- 返回的模型标识：`未提供`；只评已保存回答，无本地模型加载。

| 半平局胜率 ↑ | 95% CI | 胜＋平比例 ↑ | 完整题目 | 单轮胜/平/负 | 双顺序一致率 | 复用/新增判断 | API请求数 |
|---:|---|---:|---:|---|---:|---:|---:|
| N/A | N/A | N/A | 0/500 | N/A / N/A / N/A | N/A | 0/0 | 494 |

每题匿名交换 A/B 两次。每轮胜=1、平=0.5、负=0，先平均同题两轮，再平均完整题目。胜＋平比例另按单轮胜和平都记 1 计算；两者不是同一指标，50% 也不是正确率。
本次完整评测：False；覆盖率：0.00%。拒答、截断、无效 JSON 和缺少任一顺序的题目均不记为平局。
逐条缓存：`/shared/wwx/EasyGAD/soft-win-rate/results/api/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_t.f298c189a1236abd/judgments.jsonl`；本轮完整 JSON：`/shared/wwx/EasyGAD/soft-win-rate/results/api/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_t.f298c189a1236abd/runs/20261030T083753Z_c4e4b1c7.json`。

本次未完成：Interrupted by user; saved judgments can be resumed。成功判断已经保存。

API 配置、生成配置与使用量（不含密钥）：

```json
{
  "api_configuration": {
    "base_url": "http://43.159.131.189:8080/v1",
    "judge_model": "gpt-5.5",
    "api_style": "responses",
    "api_key_file": "/shared/wwx/EasyGAD/text_quality/.relay_api.key",
    "reasoning_effort": "low",
    "response_format": "json_schema",
    "max_output_tokens": 4096,
    "concurrency": 4,
    "max_api_calls": 1500,
    "timeout": 120,
    "retries": 2,
    "bootstrap": 2000,
    "seed": 42
  },
  "input_generation": {
    "samples": 500,
    "empty_answers": 0,
    "mean_answer_characters": 1149.63,
    "student_model_paths": [
      "/shared/wwx/EasyGAD/checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_new/gad/global_step_1813/actor/huggingface"
    ],
    "generation_configurations": [
      {
        "configuration": {
          "kgw_enabled_during_generation": false,
          "max_new_tokens": 1536,
          "max_prompt_tokens": 2048,
          "temperature": 0.7,
          "top_p": 0.9
        },
        "samples": 500
      }
    ]
  },
  "reference_generation": {
    "samples": 500,
    "empty_answers": 0,
    "mean_answer_characters": 990.018,
    "student_model_paths": [
      "/shared/wwx/EasyGAD/checkpoints/gad_05b_cleanwarmup_cleangad_control/gad/global_step_1813/actor/huggingface"
    ],
    "generation_configurations": [
      {
        "configuration": {
          "kgw_enabled_during_generation": false,
          "max_new_tokens": 1536,
          "max_prompt_tokens": 2048,
          "temperature": 0.7,
          "top_p": 0.9
        },
        "samples": 500
      }
    ]
  },
  "usage_in_successful_cache": {
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "total_tokens": 0
  },
  "elapsed_seconds": 899.21,
  "failed_orders_this_run": 163,
  "rubric_sha256": "23b028957f3cb38f4dc24706108fd73156ba747fc37203dfc7d87e8ead8e61dd"
}
```
