# 本地 LLM 裁判评测历史

由 `run_soft_win_rate.py` 追加各次运行结果。默认使用固定 Clean-KD 参照、本地 Qwen3-32B、双顺序匿名比较，以及平局半分的 Soft Win Rate。

每条记录包含输入和参照指纹、有效样本数、95% CI、单轮胜／平／负、顺序一致率、缓存复用情况与实际 GPU 配置。不同测试题目、参照或裁判协议的结果不应混为同一比较组。

## 评测记录：2026-10-29T22:07:47+08:00（20261029T140747Z_839bb744）

- 待测 JSONL：`/shared/wwx/EasyGAD/wm_test/cleanD_dipperparaSFT_dipperparagad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl`；SHA256 `b6a1c151b66159f7d008c57d2b3b29282beb7dd5d8c0df69cbf24b9432139f54`
- 固定 Clean-KD 参照：`/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl`；SHA256 `dd4cfdbe540e2227bbad3b46f6a64e34bb1a46b7e7d24860ef8be90ec03efd48`
- 本地裁判：`/shared/public_models/Qwen3-32B`；协议 `local-fixed-reference-half-tie-preferences-v1`
- 只评已保存完整回答，不生成学生或参照回答，不调用外部 API。

| Soft Win Rate ↑（平局半分） | 95% CI | 有效/计划题目 | 单轮胜/平/负 | 双顺序一致率 | 本次复用/新增判断 |
|---:|---|---:|---|---:|---:|
| N/A | N/A | 0/500 | N/A / N/A / N/A | N/A | 0/0 |

每题匿名交换 A/B 顺序两次。每轮映射胜=1、平=0.5、负=0，先取同题两轮均值，再对完整题目算术平均。这不是 PostMark 将平局算全胜的 Soft Win Rate；本报告明确采用半分。
单轮胜/平/负只统计双顺序均成功题目的 2N 次判定。交换顺序导致的相反选择不伪装成真实平局，另报顺序一致率。解析失败、拒答、超长及截断输出不计平；缺少任一顺序的题目不进入主指标。
CI 按题目成对 bootstrap，不覆盖裁判偏差或训练种子变异。50% 是相对固定参照的偏好平衡，不是正确率。
覆盖率 0.00%；本次完整评测：False；缓存：`/shared/wwx/EasyGAD/soft-win-rate/results/cleanD_dipperparaSFT_dipperparagad_gad_gamma0.5_qwen2_5_0_5b_dol.7cb370afc1b804b8/judgments.jsonl`；本次归档：`/shared/wwx/EasyGAD/soft-win-rate/results/cleanD_dipperparaSFT_dipperparagad_gad_gamma0.5_qwen2_5_0_5b_dol.7cb370afc1b804b8/runs/20261029T140747Z_839bb744.json`。

**本次未完成：All feasible GPU plans failed from memory pressure; completed results remain reusable** 成功判断已缓存，重新运行可续跑。

评分配置及实际执行配置：

```json
{
  "judge_configuration": {
    "model_path": "/shared/public_models/Qwen3-32B",
    "dtype": "bfloat16",
    "max_model_len": 8192,
    "max_num_seqs": 2,
    "max_num_batched_tokens": 4096,
    "enable_chunked_prefill": true,
    "max_output_tokens": 512,
    "seed": 42,
    "temperature": 0.0,
    "enable_thinking": false,
    "bootstrap": 2000,
    "retries": 2,
    "startup_timeout": 1200
  },
  "execution_plans": [],
  "input_generation": {
    "samples": 500,
    "empty_answers": 1,
    "mean_answer_characters": 612.564,
    "student_model_paths": [
      "/shared/wwx/EasyGAD/checkpoints/kgwD_paraSFT_paraGAD_v1/gad/global_step_1813/actor/huggingface"
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
  "rubric_sha256": "23b028957f3cb38f4dc24706108fd73156ba747fc37203dfc7d87e8ead8e61dd",
  "model_fingerprint": {
    "path": "/shared/public_models/Qwen3-32B",
    "assets": [
      {
        "name": "config.json",
        "sha256": "8034152c9180e4b08ca1f656efa7bf52e117766fc2a09c126db394a473f557a0"
      },
      {
        "name": "configuration.json",
        "sha256": "f888421726665e8a84b738eed42a64875aed79de8be7daade851ac8bf4c0cef9"
      },
      {
        "name": "generation_config.json",
        "sha256": "90373e8a092a7abb965d3fea4671ef129bb9f4ee5a3005f0ab8a95b9716812cb"
      },
      {
        "name": "merges.txt",
        "sha256": "b8e04af9c950e393054010dcef499c3f005e803e9b2da1a09b96a26c33266eb1"
      },
      {
        "name": "model.safetensors.index.json",
        "sha256": "68e066a65be872628751f5603243a94ddf9f923340e81d245944f66f5b6a03e1"
      },
      {
        "name": "tokenizer.json",
        "sha256": "aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4"
      },
      {
        "name": "tokenizer_config.json",
        "sha256": "c27ef18dae7dccaee951f6066f71a1b35ca9ec4ff3168b097dbda7905a036324"
      },
      {
        "name": "vocab.json",
        "sha256": "ca10d7e9fb3ed18575dd1e277a2579c16d108e32f27439684afa0e10b1440910"
      }
    ],
    "weight_stats": [
      {
        "name": "model-00001-of-00017.safetensors",
        "size": 3957109648,
        "mtime_ns": 1748403884759368838
      },
      {
        "name": "model-00002-of-00017.safetensors",
        "size": 3900791760,
        "mtime_ns": 1748403843500367073
      },
      {
        "name": "model-00003-of-00017.safetensors",
        "size": 3900791760,
        "mtime_ns": 1748403802698365327
      },
      {
        "name": "model-00004-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403764242363681
      },
      {
        "name": "model-00005-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403722468361894
      },
      {
        "name": "model-00006-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403681711360150
      },
      {
        "name": "model-00007-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403639311358336
      },
      {
        "name": "model-00008-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403582299355896
      },
      {
        "name": "model-00009-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403530985353700
      },
      {
        "name": "model-00010-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403477210351399
      },
      {
        "name": "model-00011-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403422707349067
      },
      {
        "name": "model-00012-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403367315346697
      },
      {
        "name": "model-00013-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403315147344465
      },
      {
        "name": "model-00014-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403263569342258
      },
      {
        "name": "model-00015-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403212487340072
      },
      {
        "name": "model-00016-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403157024337699
      },
      {
        "name": "model-00017-of-00017.safetensors",
        "size": 3055341992,
        "mtime_ns": 1748403103933335427
      }
    ],
    "weight_contents_hashed": false,
    "software": {
      "python": "3.10.21",
      "torch": "2.6.0",
      "transformers": "4.51.3",
      "tokenizers": "0.21.4",
      "vllm": "0.8.5"
    }
  }
}
```

## 评测记录：2026-10-29T22:59:32+08:00（20261029T145932Z_0e6b2e6a）

- 待测 JSONL：`/shared/wwx/EasyGAD/wm_test/cleanD_dipperparaSFT_dipperparagad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl`；SHA256 `b6a1c151b66159f7d008c57d2b3b29282beb7dd5d8c0df69cbf24b9432139f54`
- 固定 Clean-KD 参照：`/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl`；SHA256 `dd4cfdbe540e2227bbad3b46f6a64e34bb1a46b7e7d24860ef8be90ec03efd48`
- 本地裁判：`/shared/public_models/Qwen3-32B`；协议 `local-fixed-reference-half-tie-preferences-v1`
- 只评已保存完整回答，不生成学生或参照回答，不调用外部 API。

| Soft Win Rate ↑（平局半分） | 95% CI | 有效/计划题目 | 单轮胜/平/负 | 双顺序一致率 | 本次复用/新增判断 |
|---:|---|---:|---|---:|---:|
| 28.20% | [25.25%, 31.40%] | 500/500 | 19.70% / 17.00% / 63.30% | 78.80% | 0/1000 |

每题匿名交换 A/B 顺序两次。每轮映射胜=1、平=0.5、负=0，先取同题两轮均值，再对完整题目算术平均。这不是 PostMark 将平局算全胜的 Soft Win Rate；本报告明确采用半分。
单轮胜/平/负只统计双顺序均成功题目的 2N 次判定。交换顺序导致的相反选择不伪装成真实平局，另报顺序一致率。解析失败、拒答、超长及截断输出不计平；缺少任一顺序的题目不进入主指标。
CI 按题目成对 bootstrap，不覆盖裁判偏差或训练种子变异。50% 是相对固定参照的偏好平衡，不是正确率。
覆盖率 100.00%；本次完整评测：True；缓存：`/shared/wwx/EasyGAD/soft-win-rate/results/cleanD_dipperparaSFT_dipperparagad_gad_gamma0.5_qwen2_5_0_5b_dol.7cb370afc1b804b8/judgments.jsonl`；本次归档：`/shared/wwx/EasyGAD/soft-win-rate/results/cleanD_dipperparaSFT_dipperparagad_gad_gamma0.5_qwen2_5_0_5b_dol.7cb370afc1b804b8/runs/20261029T145932Z_0e6b2e6a.json`。

评分配置及实际执行配置：

```json
{
  "judge_configuration": {
    "model_path": "/shared/public_models/Qwen3-32B",
    "dtype": "bfloat16",
    "max_model_len": 8192,
    "max_num_seqs": 2,
    "max_num_batched_tokens": 4096,
    "enable_chunked_prefill": true,
    "max_output_tokens": 512,
    "seed": 42,
    "temperature": 0.0,
    "enable_thinking": false,
    "bootstrap": 2000,
    "retries": 2,
    "startup_timeout": 1200
  },
  "execution_plans": [
    {
      "gpu_ids": [
        1
      ],
      "gpu_uuids": [
        "GPU-aaaa1e22-8585-bcee-bf44-4dbbb57365ea"
      ],
      "tensor_parallel_size": 1,
      "gpu_memory_utilization": 0.98,
      "estimated_per_gpu_mib": 68632.79,
      "enforce_eager": true,
      "memory_accounting": "legacy_v1_total",
      "available_per_gpu_mib": 68999.6,
      "max_num_seqs": 2,
      "max_model_len": 8192,
      "distributed_executor_backend": "mp",
      "cuda_visible_devices": "1",
      "cuda_device_order": "PCI_BUS_ID",
      "vllm_use_v1": "1",
      "max_num_batched_tokens": 4096,
      "enable_chunked_prefill": true,
      "worker_directory": "/shared/wwx/EasyGAD/soft-win-rate/results/cleanD_dipperparaSFT_dipperparagad_gad_gamma0.5_qwen2_5_0_5b_dol.7cb370afc1b804b8/workers/20261029T222939_3aa08b15/plan_00",
      "gpu_inventory": [
        {
          "index": 1,
          "uuid": "GPU-aaaa1e22-8585-bcee-bf44-4dbbb57365ea",
          "name": "NVIDIA A100 80GB PCIe",
          "total_mib": 81920,
          "free_mib": 70638,
          "utilization": 0
        }
      ]
    }
  ],
  "input_generation": {
    "samples": 500,
    "empty_answers": 1,
    "mean_answer_characters": 612.564,
    "student_model_paths": [
      "/shared/wwx/EasyGAD/checkpoints/kgwD_paraSFT_paraGAD_v1/gad/global_step_1813/actor/huggingface"
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
  "rubric_sha256": "23b028957f3cb38f4dc24706108fd73156ba747fc37203dfc7d87e8ead8e61dd",
  "model_fingerprint": {
    "path": "/shared/public_models/Qwen3-32B",
    "assets": [
      {
        "name": "config.json",
        "sha256": "8034152c9180e4b08ca1f656efa7bf52e117766fc2a09c126db394a473f557a0"
      },
      {
        "name": "configuration.json",
        "sha256": "f888421726665e8a84b738eed42a64875aed79de8be7daade851ac8bf4c0cef9"
      },
      {
        "name": "generation_config.json",
        "sha256": "90373e8a092a7abb965d3fea4671ef129bb9f4ee5a3005f0ab8a95b9716812cb"
      },
      {
        "name": "merges.txt",
        "sha256": "b8e04af9c950e393054010dcef499c3f005e803e9b2da1a09b96a26c33266eb1"
      },
      {
        "name": "model.safetensors.index.json",
        "sha256": "68e066a65be872628751f5603243a94ddf9f923340e81d245944f66f5b6a03e1"
      },
      {
        "name": "tokenizer.json",
        "sha256": "aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4"
      },
      {
        "name": "tokenizer_config.json",
        "sha256": "c27ef18dae7dccaee951f6066f71a1b35ca9ec4ff3168b097dbda7905a036324"
      },
      {
        "name": "vocab.json",
        "sha256": "ca10d7e9fb3ed18575dd1e277a2579c16d108e32f27439684afa0e10b1440910"
      }
    ],
    "weight_stats": [
      {
        "name": "model-00001-of-00017.safetensors",
        "size": 3957109648,
        "mtime_ns": 1748403884759368838
      },
      {
        "name": "model-00002-of-00017.safetensors",
        "size": 3900791760,
        "mtime_ns": 1748403843500367073
      },
      {
        "name": "model-00003-of-00017.safetensors",
        "size": 3900791760,
        "mtime_ns": 1748403802698365327
      },
      {
        "name": "model-00004-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403764242363681
      },
      {
        "name": "model-00005-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403722468361894
      },
      {
        "name": "model-00006-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403681711360150
      },
      {
        "name": "model-00007-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403639311358336
      },
      {
        "name": "model-00008-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403582299355896
      },
      {
        "name": "model-00009-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403530985353700
      },
      {
        "name": "model-00010-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403477210351399
      },
      {
        "name": "model-00011-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403422707349067
      },
      {
        "name": "model-00012-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403367315346697
      },
      {
        "name": "model-00013-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403315147344465
      },
      {
        "name": "model-00014-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403263569342258
      },
      {
        "name": "model-00015-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403212487340072
      },
      {
        "name": "model-00016-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403157024337699
      },
      {
        "name": "model-00017-of-00017.safetensors",
        "size": 3055341992,
        "mtime_ns": 1748403103933335427
      }
    ],
    "weight_contents_hashed": false,
    "software": {
      "python": "3.10.21",
      "torch": "2.6.0",
      "transformers": "4.51.3",
      "tokenizers": "0.21.4",
      "vllm": "0.8.5"
    }
  }
}
```

## 评测记录：2026-10-29T23:06:16+08:00（20261029T150616Z_5ae21a95）

- 待测 JSONL：`/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.jsonl`；SHA256 `618df1162dbd1bbf770b90baabfd23226ef52fd3028f5fdb6490919cca78b92e`
- 固定 Clean-KD 参照：`/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl`；SHA256 `dd4cfdbe540e2227bbad3b46f6a64e34bb1a46b7e7d24860ef8be90ec03efd48`
- 本地裁判：`/shared/public_models/Qwen3-32B`；协议 `local-fixed-reference-half-tie-preferences-v1`
- 只评已保存完整回答，不生成学生或参照回答，不调用外部 API。

| Soft Win Rate ↑（平局半分） | 95% CI | 有效/计划题目 | 单轮胜/平/负 | 双顺序一致率 | 本次复用/新增判断 |
|---:|---|---:|---|---:|---:|
| N/A | N/A | 0/500 | N/A / N/A / N/A | N/A | 0/0 |

每题匿名交换 A/B 顺序两次。每轮映射胜=1、平=0.5、负=0，先取同题两轮均值，再对完整题目算术平均。这不是 PostMark 将平局算全胜的 Soft Win Rate；本报告明确采用半分。
单轮胜/平/负只统计双顺序均成功题目的 2N 次判定。交换顺序导致的相反选择不伪装成真实平局，另报顺序一致率。解析失败、拒答、超长及截断输出不计平；缺少任一顺序的题目不进入主指标。
CI 按题目成对 bootstrap，不覆盖裁判偏差或训练种子变异。50% 是相对固定参照的偏好平衡，不是正确率。
覆盖率 0.00%；本次完整评测：False；缓存：`/shared/wwx/EasyGAD/soft-win-rate/results/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_t.3f9b9cdd137cd71b/judgments.jsonl`；本次归档：`/shared/wwx/EasyGAD/soft-win-rate/results/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_t.3f9b9cdd137cd71b/runs/20261029T150616Z_5ae21a95.json`。

**本次未完成：Local judge failed: preflight: ValueError: Judge input too long for task d68b9d910c33ec16de6a702d6d8744c539110ed4a89368ff05755072a6219023: prompt=8646, output_budget=512, window=8192; no text was truncated
Worker log: /shared/wwx/EasyGAD/soft-win-rate/results/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_t.3f9b9cdd137cd71b/workers/20261029T230612_203960f1/plan_00/worker.log** 成功判断已缓存，重新运行可续跑。

评分配置及实际执行配置：

```json
{
  "judge_configuration": {
    "model_path": "/shared/public_models/Qwen3-32B",
    "dtype": "bfloat16",
    "max_model_len": 8192,
    "max_num_seqs": 2,
    "max_num_batched_tokens": 4096,
    "enable_chunked_prefill": true,
    "max_output_tokens": 512,
    "seed": 42,
    "temperature": 0.0,
    "enable_thinking": false,
    "bootstrap": 2000,
    "retries": 2,
    "startup_timeout": 1200
  },
  "execution_plans": [],
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
  "rubric_sha256": "23b028957f3cb38f4dc24706108fd73156ba747fc37203dfc7d87e8ead8e61dd",
  "model_fingerprint": {
    "path": "/shared/public_models/Qwen3-32B",
    "assets": [
      {
        "name": "config.json",
        "sha256": "8034152c9180e4b08ca1f656efa7bf52e117766fc2a09c126db394a473f557a0"
      },
      {
        "name": "configuration.json",
        "sha256": "f888421726665e8a84b738eed42a64875aed79de8be7daade851ac8bf4c0cef9"
      },
      {
        "name": "generation_config.json",
        "sha256": "90373e8a092a7abb965d3fea4671ef129bb9f4ee5a3005f0ab8a95b9716812cb"
      },
      {
        "name": "merges.txt",
        "sha256": "b8e04af9c950e393054010dcef499c3f005e803e9b2da1a09b96a26c33266eb1"
      },
      {
        "name": "model.safetensors.index.json",
        "sha256": "68e066a65be872628751f5603243a94ddf9f923340e81d245944f66f5b6a03e1"
      },
      {
        "name": "tokenizer.json",
        "sha256": "aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4"
      },
      {
        "name": "tokenizer_config.json",
        "sha256": "c27ef18dae7dccaee951f6066f71a1b35ca9ec4ff3168b097dbda7905a036324"
      },
      {
        "name": "vocab.json",
        "sha256": "ca10d7e9fb3ed18575dd1e277a2579c16d108e32f27439684afa0e10b1440910"
      }
    ],
    "weight_stats": [
      {
        "name": "model-00001-of-00017.safetensors",
        "size": 3957109648,
        "mtime_ns": 1748403884759368838
      },
      {
        "name": "model-00002-of-00017.safetensors",
        "size": 3900791760,
        "mtime_ns": 1748403843500367073
      },
      {
        "name": "model-00003-of-00017.safetensors",
        "size": 3900791760,
        "mtime_ns": 1748403802698365327
      },
      {
        "name": "model-00004-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403764242363681
      },
      {
        "name": "model-00005-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403722468361894
      },
      {
        "name": "model-00006-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403681711360150
      },
      {
        "name": "model-00007-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403639311358336
      },
      {
        "name": "model-00008-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403582299355896
      },
      {
        "name": "model-00009-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403530985353700
      },
      {
        "name": "model-00010-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403477210351399
      },
      {
        "name": "model-00011-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403422707349067
      },
      {
        "name": "model-00012-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403367315346697
      },
      {
        "name": "model-00013-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403315147344465
      },
      {
        "name": "model-00014-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403263569342258
      },
      {
        "name": "model-00015-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403212487340072
      },
      {
        "name": "model-00016-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403157024337699
      },
      {
        "name": "model-00017-of-00017.safetensors",
        "size": 3055341992,
        "mtime_ns": 1748403103933335427
      }
    ],
    "weight_contents_hashed": false,
    "software": {
      "python": "3.10.21",
      "torch": "2.6.0",
      "transformers": "4.51.3",
      "tokenizers": "0.21.4",
      "vllm": "0.8.5"
    }
  }
}
```

## 评测记录：2026-10-29T23:33:39+08:00（20261029T153339Z_dbdc5156）

- 待测 JSONL：`/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta3_new1_qwen2_5_0_5b_dolly15k_test.jsonl`；SHA256 `b1c02a02c9e074669d99cc9965618971b50b81e66d62c386002cdde73652f192`
- 固定 Clean-KD 参照：`/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl`；SHA256 `dd4cfdbe540e2227bbad3b46f6a64e34bb1a46b7e7d24860ef8be90ec03efd48`
- 本地裁判：`/shared/public_models/Qwen3-32B`；协议 `local-fixed-reference-half-tie-preferences-v1`
- 只评已保存完整回答，不生成学生或参照回答，不调用外部 API。

| Soft Win Rate ↑（平局半分） | 95% CI | 有效/计划题目 | 单轮胜/平/负 | 双顺序一致率 | 本次复用/新增判断 |
|---:|---|---:|---|---:|---:|
| 29.00% | [26.05%, 31.95%] | 500/500 | 21.30% / 15.40% / 63.30% | 76.80% | 0/1000 |

每题匿名交换 A/B 顺序两次。每轮映射胜=1、平=0.5、负=0，先取同题两轮均值，再对完整题目算术平均。这不是 PostMark 将平局算全胜的 Soft Win Rate；本报告明确采用半分。
单轮胜/平/负只统计双顺序均成功题目的 2N 次判定。交换顺序导致的相反选择不伪装成真实平局，另报顺序一致率。解析失败、拒答、超长及截断输出不计平；缺少任一顺序的题目不进入主指标。
CI 按题目成对 bootstrap，不覆盖裁判偏差或训练种子变异。50% 是相对固定参照的偏好平衡，不是正确率。
覆盖率 100.00%；本次完整评测：True；缓存：`/shared/wwx/EasyGAD/soft-win-rate/results/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta3_new1_qwen2_5_0_5.d5bf1ff1da3c4875/judgments.jsonl`；本次归档：`/shared/wwx/EasyGAD/soft-win-rate/results/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta3_new1_qwen2_5_0_5.d5bf1ff1da3c4875/runs/20261029T153339Z_dbdc5156.json`。

评分配置及实际执行配置：

```json
{
  "judge_configuration": {
    "model_path": "/shared/public_models/Qwen3-32B",
    "dtype": "bfloat16",
    "max_model_len": 8192,
    "max_num_seqs": 2,
    "max_num_batched_tokens": 4096,
    "enable_chunked_prefill": true,
    "max_output_tokens": 512,
    "seed": 42,
    "temperature": 0.0,
    "enable_thinking": false,
    "bootstrap": 2000,
    "retries": 2,
    "startup_timeout": 1200
  },
  "execution_plans": [
    {
      "gpu_ids": [
        1,
        3
      ],
      "gpu_uuids": [
        "GPU-aaaa1e22-8585-bcee-bf44-4dbbb57365ea",
        "GPU-cf0eb97d-d714-dfe3-034e-f00037747988"
      ],
      "tensor_parallel_size": 2,
      "gpu_memory_utilization": 0.98,
      "estimated_per_gpu_mib": 35340.4,
      "enforce_eager": true,
      "memory_accounting": "legacy_v1_total",
      "available_per_gpu_mib": 39608.8,
      "max_num_seqs": 2,
      "max_model_len": 8192,
      "distributed_executor_backend": "mp",
      "cuda_visible_devices": "1,3",
      "cuda_device_order": "PCI_BUS_ID",
      "vllm_use_v1": "1",
      "max_num_batched_tokens": 4096,
      "enable_chunked_prefill": true,
      "worker_directory": "/shared/wwx/EasyGAD/soft-win-rate/results/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta3_new1_qwen2_5_0_5.d5bf1ff1da3c4875/workers/20261029T230618_eab279f8/plan_00",
      "gpu_inventory": [
        {
          "index": 1,
          "uuid": "GPU-aaaa1e22-8585-bcee-bf44-4dbbb57365ea",
          "name": "NVIDIA A100 80GB PCIe",
          "total_mib": 81920,
          "free_mib": 54985,
          "utilization": 0
        },
        {
          "index": 3,
          "uuid": "GPU-cf0eb97d-d714-dfe3-034e-f00037747988",
          "name": "NVIDIA A100-PCIE-40GB",
          "total_mib": 40960,
          "free_mib": 40428,
          "utilization": 0
        }
      ]
    }
  ],
  "input_generation": {
    "samples": 500,
    "empty_answers": 0,
    "mean_answer_characters": 600.578,
    "student_model_paths": [
      "/shared/wwx/EasyGAD/checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_new1_dipper2stage/gad/global_step_1813/actor/huggingface"
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
  "rubric_sha256": "23b028957f3cb38f4dc24706108fd73156ba747fc37203dfc7d87e8ead8e61dd",
  "model_fingerprint": {
    "path": "/shared/public_models/Qwen3-32B",
    "assets": [
      {
        "name": "config.json",
        "sha256": "8034152c9180e4b08ca1f656efa7bf52e117766fc2a09c126db394a473f557a0"
      },
      {
        "name": "configuration.json",
        "sha256": "f888421726665e8a84b738eed42a64875aed79de8be7daade851ac8bf4c0cef9"
      },
      {
        "name": "generation_config.json",
        "sha256": "90373e8a092a7abb965d3fea4671ef129bb9f4ee5a3005f0ab8a95b9716812cb"
      },
      {
        "name": "merges.txt",
        "sha256": "b8e04af9c950e393054010dcef499c3f005e803e9b2da1a09b96a26c33266eb1"
      },
      {
        "name": "model.safetensors.index.json",
        "sha256": "68e066a65be872628751f5603243a94ddf9f923340e81d245944f66f5b6a03e1"
      },
      {
        "name": "tokenizer.json",
        "sha256": "aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4"
      },
      {
        "name": "tokenizer_config.json",
        "sha256": "c27ef18dae7dccaee951f6066f71a1b35ca9ec4ff3168b097dbda7905a036324"
      },
      {
        "name": "vocab.json",
        "sha256": "ca10d7e9fb3ed18575dd1e277a2579c16d108e32f27439684afa0e10b1440910"
      }
    ],
    "weight_stats": [
      {
        "name": "model-00001-of-00017.safetensors",
        "size": 3957109648,
        "mtime_ns": 1748403884759368838
      },
      {
        "name": "model-00002-of-00017.safetensors",
        "size": 3900791760,
        "mtime_ns": 1748403843500367073
      },
      {
        "name": "model-00003-of-00017.safetensors",
        "size": 3900791760,
        "mtime_ns": 1748403802698365327
      },
      {
        "name": "model-00004-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403764242363681
      },
      {
        "name": "model-00005-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403722468361894
      },
      {
        "name": "model-00006-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403681711360150
      },
      {
        "name": "model-00007-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403639311358336
      },
      {
        "name": "model-00008-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403582299355896
      },
      {
        "name": "model-00009-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403530985353700
      },
      {
        "name": "model-00010-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403477210351399
      },
      {
        "name": "model-00011-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403422707349067
      },
      {
        "name": "model-00012-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403367315346697
      },
      {
        "name": "model-00013-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403315147344465
      },
      {
        "name": "model-00014-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403263569342258
      },
      {
        "name": "model-00015-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403212487340072
      },
      {
        "name": "model-00016-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403157024337699
      },
      {
        "name": "model-00017-of-00017.safetensors",
        "size": 3055341992,
        "mtime_ns": 1748403103933335427
      }
    ],
    "weight_contents_hashed": false,
    "software": {
      "python": "3.10.21",
      "torch": "2.6.0",
      "transformers": "4.51.3",
      "tokenizers": "0.21.4",
      "vllm": "0.8.5"
    }
  }
}
```

## 评测记录：2026-10-30T00:05:28+08:00（20261029T160528Z_fdf4bb0f）

- 待测 JSONL：`/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new.jsonl`；SHA256 `a6cb5b53fe168f08def87ed1c4ebb6a5e038e93fe2ba6ba94044adbb8ff9d034`
- 固定 Clean-KD 参照：`/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl`；SHA256 `dd4cfdbe540e2227bbad3b46f6a64e34bb1a46b7e7d24860ef8be90ec03efd48`
- 本地裁判：`/shared/public_models/Qwen3-32B`；协议 `local-fixed-reference-half-tie-preferences-v1`
- 只评已保存完整回答，不生成学生或参照回答，不调用外部 API。

| Soft Win Rate ↑（平局半分） | 95% CI | 有效/计划题目 | 单轮胜/平/负 | 双顺序一致率 | 本次复用/新增判断 |
|---:|---|---:|---|---:|---:|
| 45.60% | [42.20%, 48.80%] | 500/500 | 36.30% / 18.60% / 45.10% | 70.20% | 0/1000 |

每题匿名交换 A/B 顺序两次。每轮映射胜=1、平=0.5、负=0，先取同题两轮均值，再对完整题目算术平均。这不是 PostMark 将平局算全胜的 Soft Win Rate；本报告明确采用半分。
单轮胜/平/负只统计双顺序均成功题目的 2N 次判定。交换顺序导致的相反选择不伪装成真实平局，另报顺序一致率。解析失败、拒答、超长及截断输出不计平；缺少任一顺序的题目不进入主指标。
CI 按题目成对 bootstrap，不覆盖裁判偏差或训练种子变异。50% 是相对固定参照的偏好平衡，不是正确率。
覆盖率 100.00%；本次完整评测：True；缓存：`/shared/wwx/EasyGAD/soft-win-rate/results/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new.749dd5f83f50df52/judgments.jsonl`；本次归档：`/shared/wwx/EasyGAD/soft-win-rate/results/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new.749dd5f83f50df52/runs/20261029T160528Z_fdf4bb0f.json`。

评分配置及实际执行配置：

```json
{
  "judge_configuration": {
    "model_path": "/shared/public_models/Qwen3-32B",
    "dtype": "bfloat16",
    "max_model_len": 8192,
    "max_num_seqs": 2,
    "max_num_batched_tokens": 4096,
    "enable_chunked_prefill": true,
    "max_output_tokens": 512,
    "seed": 42,
    "temperature": 0.0,
    "enable_thinking": false,
    "bootstrap": 2000,
    "retries": 2,
    "startup_timeout": 1200
  },
  "execution_plans": [
    {
      "gpu_ids": [
        1
      ],
      "gpu_uuids": [
        "GPU-aaaa1e22-8585-bcee-bf44-4dbbb57365ea"
      ],
      "tensor_parallel_size": 1,
      "gpu_memory_utilization": 0.98,
      "estimated_per_gpu_mib": 68632.79,
      "enforce_eager": true,
      "memory_accounting": "legacy_v1_total",
      "available_per_gpu_mib": 69129.6,
      "max_num_seqs": 2,
      "max_model_len": 8192,
      "distributed_executor_backend": "mp",
      "cuda_visible_devices": "1",
      "cuda_device_order": "PCI_BUS_ID",
      "vllm_use_v1": "1",
      "max_num_batched_tokens": 4096,
      "enable_chunked_prefill": true,
      "worker_directory": "/shared/wwx/EasyGAD/soft-win-rate/results/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new.749dd5f83f50df52/workers/20261029T233341_cfd31fb9/plan_00",
      "gpu_inventory": [
        {
          "index": 1,
          "uuid": "GPU-aaaa1e22-8585-bcee-bf44-4dbbb57365ea",
          "name": "NVIDIA A100 80GB PCIe",
          "total_mib": 81920,
          "free_mib": 70768,
          "utilization": 0
        }
      ]
    }
  ],
  "input_generation": {
    "samples": 500,
    "empty_answers": 0,
    "mean_answer_characters": 1264.472,
    "student_model_paths": [
      "/shared/wwx/EasyGAD/checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_new/gad/global_step_1813/actor/huggingface"
    ],
    "generation_configurations": [
      {
        "configuration": {
          "kgw_enabled_during_generation": false,
          "max_new_tokens": 1536,
          "max_prompt_tokens": 6144,
          "prompt_truncated": false,
          "temperature": 0.7,
          "top_p": 0.9,
          "wn_enabled_during_generation": true
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
  "rubric_sha256": "23b028957f3cb38f4dc24706108fd73156ba747fc37203dfc7d87e8ead8e61dd",
  "model_fingerprint": {
    "path": "/shared/public_models/Qwen3-32B",
    "assets": [
      {
        "name": "config.json",
        "sha256": "8034152c9180e4b08ca1f656efa7bf52e117766fc2a09c126db394a473f557a0"
      },
      {
        "name": "configuration.json",
        "sha256": "f888421726665e8a84b738eed42a64875aed79de8be7daade851ac8bf4c0cef9"
      },
      {
        "name": "generation_config.json",
        "sha256": "90373e8a092a7abb965d3fea4671ef129bb9f4ee5a3005f0ab8a95b9716812cb"
      },
      {
        "name": "merges.txt",
        "sha256": "b8e04af9c950e393054010dcef499c3f005e803e9b2da1a09b96a26c33266eb1"
      },
      {
        "name": "model.safetensors.index.json",
        "sha256": "68e066a65be872628751f5603243a94ddf9f923340e81d245944f66f5b6a03e1"
      },
      {
        "name": "tokenizer.json",
        "sha256": "aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4"
      },
      {
        "name": "tokenizer_config.json",
        "sha256": "c27ef18dae7dccaee951f6066f71a1b35ca9ec4ff3168b097dbda7905a036324"
      },
      {
        "name": "vocab.json",
        "sha256": "ca10d7e9fb3ed18575dd1e277a2579c16d108e32f27439684afa0e10b1440910"
      }
    ],
    "weight_stats": [
      {
        "name": "model-00001-of-00017.safetensors",
        "size": 3957109648,
        "mtime_ns": 1748403884759368838
      },
      {
        "name": "model-00002-of-00017.safetensors",
        "size": 3900791760,
        "mtime_ns": 1748403843500367073
      },
      {
        "name": "model-00003-of-00017.safetensors",
        "size": 3900791760,
        "mtime_ns": 1748403802698365327
      },
      {
        "name": "model-00004-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403764242363681
      },
      {
        "name": "model-00005-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403722468361894
      },
      {
        "name": "model-00006-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403681711360150
      },
      {
        "name": "model-00007-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403639311358336
      },
      {
        "name": "model-00008-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403582299355896
      },
      {
        "name": "model-00009-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403530985353700
      },
      {
        "name": "model-00010-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403477210351399
      },
      {
        "name": "model-00011-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403422707349067
      },
      {
        "name": "model-00012-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403367315346697
      },
      {
        "name": "model-00013-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403315147344465
      },
      {
        "name": "model-00014-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403263569342258
      },
      {
        "name": "model-00015-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403212487340072
      },
      {
        "name": "model-00016-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403157024337699
      },
      {
        "name": "model-00017-of-00017.safetensors",
        "size": 3055341992,
        "mtime_ns": 1748403103933335427
      }
    ],
    "weight_contents_hashed": false,
    "software": {
      "python": "3.10.21",
      "torch": "2.6.0",
      "transformers": "4.51.3",
      "tokenizers": "0.21.4",
      "vllm": "0.8.5"
    }
  }
}
```

## 评测记录：2026-10-30T00:34:13+08:00（20261029T163413Z_2b1d21cd）

- 待测 JSONL：`/shared/wwx/EasyGAD/wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new_strength3.jsonl`；SHA256 `b8eb3e5748736faeb53e3df2749af258cbaab7288da6a9eebedf771ac7db747d`
- 固定 Clean-KD 参照：`/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl`；SHA256 `dd4cfdbe540e2227bbad3b46f6a64e34bb1a46b7e7d24860ef8be90ec03efd48`
- 本地裁判：`/shared/public_models/Qwen3-32B`；协议 `local-fixed-reference-half-tie-preferences-v1`
- 只评已保存完整回答，不生成学生或参照回答，不调用外部 API。

| Soft Win Rate ↑（平局半分） | 95% CI | 有效/计划题目 | 单轮胜/平/负 | 双顺序一致率 | 本次复用/新增判断 |
|---:|---|---:|---|---:|---:|
| 41.30% | [38.00%, 44.60%] | 500/500 | 32.20% / 18.20% / 49.60% | 72.00% | 0/1000 |

每题匿名交换 A/B 顺序两次。每轮映射胜=1、平=0.5、负=0，先取同题两轮均值，再对完整题目算术平均。这不是 PostMark 将平局算全胜的 Soft Win Rate；本报告明确采用半分。
单轮胜/平/负只统计双顺序均成功题目的 2N 次判定。交换顺序导致的相反选择不伪装成真实平局，另报顺序一致率。解析失败、拒答、超长及截断输出不计平；缺少任一顺序的题目不进入主指标。
CI 按题目成对 bootstrap，不覆盖裁判偏差或训练种子变异。50% 是相对固定参照的偏好平衡，不是正确率。
覆盖率 100.00%；本次完整评测：True；缓存：`/shared/wwx/EasyGAD/soft-win-rate/results/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new_strength3.5583d512fdbd114a/judgments.jsonl`；本次归档：`/shared/wwx/EasyGAD/soft-win-rate/results/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new_strength3.5583d512fdbd114a/runs/20261029T163413Z_2b1d21cd.json`。

评分配置及实际执行配置：

```json
{
  "judge_configuration": {
    "model_path": "/shared/public_models/Qwen3-32B",
    "dtype": "bfloat16",
    "max_model_len": 8192,
    "max_num_seqs": 2,
    "max_num_batched_tokens": 4096,
    "enable_chunked_prefill": true,
    "max_output_tokens": 512,
    "seed": 42,
    "temperature": 0.0,
    "enable_thinking": false,
    "bootstrap": 2000,
    "retries": 2,
    "startup_timeout": 1200
  },
  "execution_plans": [
    {
      "gpu_ids": [
        1,
        3
      ],
      "gpu_uuids": [
        "GPU-aaaa1e22-8585-bcee-bf44-4dbbb57365ea",
        "GPU-cf0eb97d-d714-dfe3-034e-f00037747988"
      ],
      "tensor_parallel_size": 2,
      "gpu_memory_utilization": 0.98,
      "estimated_per_gpu_mib": 35340.4,
      "enforce_eager": true,
      "memory_accounting": "legacy_v1_total",
      "available_per_gpu_mib": 39608.8,
      "max_num_seqs": 2,
      "max_model_len": 8192,
      "distributed_executor_backend": "mp",
      "cuda_visible_devices": "1,3",
      "cuda_device_order": "PCI_BUS_ID",
      "vllm_use_v1": "1",
      "max_num_batched_tokens": 4096,
      "enable_chunked_prefill": true,
      "worker_directory": "/shared/wwx/EasyGAD/soft-win-rate/results/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new_strength3.5583d512fdbd114a/workers/20261030T000532_6b5cfa92/plan_00",
      "gpu_inventory": [
        {
          "index": 1,
          "uuid": "GPU-aaaa1e22-8585-bcee-bf44-4dbbb57365ea",
          "name": "NVIDIA A100 80GB PCIe",
          "total_mib": 81920,
          "free_mib": 54973,
          "utilization": 0
        },
        {
          "index": 3,
          "uuid": "GPU-cf0eb97d-d714-dfe3-034e-f00037747988",
          "name": "NVIDIA A100-PCIE-40GB",
          "total_mib": 40960,
          "free_mib": 40428,
          "utilization": 0
        }
      ]
    }
  ],
  "input_generation": {
    "samples": 500,
    "empty_answers": 0,
    "mean_answer_characters": 1330.452,
    "student_model_paths": [
      "/shared/wwx/EasyGAD/checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_new/gad/global_step_1813/actor/huggingface"
    ],
    "generation_configurations": [
      {
        "configuration": {
          "kgw_enabled_during_generation": false,
          "max_new_tokens": 1536,
          "max_prompt_tokens": 6144,
          "prompt_truncated": false,
          "temperature": 0.7,
          "top_p": 0.9,
          "wn_enabled_during_generation": true
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
  "rubric_sha256": "23b028957f3cb38f4dc24706108fd73156ba747fc37203dfc7d87e8ead8e61dd",
  "model_fingerprint": {
    "path": "/shared/public_models/Qwen3-32B",
    "assets": [
      {
        "name": "config.json",
        "sha256": "8034152c9180e4b08ca1f656efa7bf52e117766fc2a09c126db394a473f557a0"
      },
      {
        "name": "configuration.json",
        "sha256": "f888421726665e8a84b738eed42a64875aed79de8be7daade851ac8bf4c0cef9"
      },
      {
        "name": "generation_config.json",
        "sha256": "90373e8a092a7abb965d3fea4671ef129bb9f4ee5a3005f0ab8a95b9716812cb"
      },
      {
        "name": "merges.txt",
        "sha256": "b8e04af9c950e393054010dcef499c3f005e803e9b2da1a09b96a26c33266eb1"
      },
      {
        "name": "model.safetensors.index.json",
        "sha256": "68e066a65be872628751f5603243a94ddf9f923340e81d245944f66f5b6a03e1"
      },
      {
        "name": "tokenizer.json",
        "sha256": "aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4"
      },
      {
        "name": "tokenizer_config.json",
        "sha256": "c27ef18dae7dccaee951f6066f71a1b35ca9ec4ff3168b097dbda7905a036324"
      },
      {
        "name": "vocab.json",
        "sha256": "ca10d7e9fb3ed18575dd1e277a2579c16d108e32f27439684afa0e10b1440910"
      }
    ],
    "weight_stats": [
      {
        "name": "model-00001-of-00017.safetensors",
        "size": 3957109648,
        "mtime_ns": 1748403884759368838
      },
      {
        "name": "model-00002-of-00017.safetensors",
        "size": 3900791760,
        "mtime_ns": 1748403843500367073
      },
      {
        "name": "model-00003-of-00017.safetensors",
        "size": 3900791760,
        "mtime_ns": 1748403802698365327
      },
      {
        "name": "model-00004-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403764242363681
      },
      {
        "name": "model-00005-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403722468361894
      },
      {
        "name": "model-00006-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403681711360150
      },
      {
        "name": "model-00007-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403639311358336
      },
      {
        "name": "model-00008-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403582299355896
      },
      {
        "name": "model-00009-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403530985353700
      },
      {
        "name": "model-00010-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403477210351399
      },
      {
        "name": "model-00011-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403422707349067
      },
      {
        "name": "model-00012-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403367315346697
      },
      {
        "name": "model-00013-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403315147344465
      },
      {
        "name": "model-00014-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403263569342258
      },
      {
        "name": "model-00015-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403212487340072
      },
      {
        "name": "model-00016-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403157024337699
      },
      {
        "name": "model-00017-of-00017.safetensors",
        "size": 3055341992,
        "mtime_ns": 1748403103933335427
      }
    ],
    "weight_contents_hashed": false,
    "software": {
      "python": "3.10.21",
      "torch": "2.6.0",
      "transformers": "4.51.3",
      "tokenizers": "0.21.4",
      "vllm": "0.8.5"
    }
  }
}
```

## 评测记录：2026-10-30T15:18:01+08:00（20261030T071801Z_a7033a56）

- 待测 JSONL：`/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.jsonl`；SHA256 `618df1162dbd1bbf770b90baabfd23226ef52fd3028f5fdb6490919cca78b92e`
- 固定 Clean-KD 参照：`/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl`；SHA256 `dd4cfdbe540e2227bbad3b46f6a64e34bb1a46b7e7d24860ef8be90ec03efd48`
- 本地裁判：`/shared/public_models/Qwen3-32B`；协议 `local-fixed-reference-half-tie-preferences-v1`
- 只评已保存完整回答，不生成学生或参照回答，不调用外部 API。

| Soft Win Rate ↑（平局半分） | 95% CI | 有效/计划题目 | 单轮胜/平/负 | 双顺序一致率 | 本次复用/新增判断 |
|---:|---|---:|---|---:|---:|
| N/A | N/A | 0/500 | N/A / N/A / N/A | N/A | 0/0 |

每题匿名交换 A/B 顺序两次。每轮映射胜=1、平=0.5、负=0，先取同题两轮均值，再对完整题目算术平均。这不是 PostMark 将平局算全胜的 Soft Win Rate；本报告明确采用半分。
单轮胜/平/负只统计双顺序均成功题目的 2N 次判定。交换顺序导致的相反选择不伪装成真实平局，另报顺序一致率。解析失败、拒答、超长及截断输出不计平；缺少任一顺序的题目不进入主指标。
CI 按题目成对 bootstrap，不覆盖裁判偏差或训练种子变异。50% 是相对固定参照的偏好平衡，不是正确率。
覆盖率 0.00%；本次完整评测：False；缓存：`/shared/wwx/EasyGAD/soft-win-rate/results/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_t.966cdc4683e9bb20/judgments.jsonl`；本次归档：`/shared/wwx/EasyGAD/soft-win-rate/results/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_t.966cdc4683e9bb20/runs/20261030T071801Z_a7033a56.json`。

**本次未完成：Judge startup timed out; inspect /shared/wwx/EasyGAD/soft-win-rate/results/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_t.966cdc4683e9bb20/workers/20261030T145755_7778f319/plan_00/worker.log** 成功判断已缓存，重新运行可续跑。

自动窗口调整：8192 → 16384 token；已发现的输入及输出预留至少需要 9158 token。保留完整文本，实际并发与 GPU 见执行配置。

评分配置及实际执行配置：

```json
{
  "judge_configuration": {
    "model_path": "/shared/public_models/Qwen3-32B",
    "dtype": "bfloat16",
    "max_model_len": 16384,
    "max_num_seqs": 2,
    "max_num_batched_tokens": 4096,
    "enable_chunked_prefill": true,
    "max_output_tokens": 512,
    "seed": 42,
    "temperature": 0.0,
    "enable_thinking": false,
    "bootstrap": 2000,
    "retries": 2,
    "startup_timeout": 1200
  },
  "execution_plans": [],
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
  "rubric_sha256": "23b028957f3cb38f4dc24706108fd73156ba747fc37203dfc7d87e8ead8e61dd",
  "model_fingerprint": {
    "path": "/shared/public_models/Qwen3-32B",
    "assets": [
      {
        "name": "config.json",
        "sha256": "8034152c9180e4b08ca1f656efa7bf52e117766fc2a09c126db394a473f557a0"
      },
      {
        "name": "configuration.json",
        "sha256": "f888421726665e8a84b738eed42a64875aed79de8be7daade851ac8bf4c0cef9"
      },
      {
        "name": "generation_config.json",
        "sha256": "90373e8a092a7abb965d3fea4671ef129bb9f4ee5a3005f0ab8a95b9716812cb"
      },
      {
        "name": "merges.txt",
        "sha256": "b8e04af9c950e393054010dcef499c3f005e803e9b2da1a09b96a26c33266eb1"
      },
      {
        "name": "model.safetensors.index.json",
        "sha256": "68e066a65be872628751f5603243a94ddf9f923340e81d245944f66f5b6a03e1"
      },
      {
        "name": "tokenizer.json",
        "sha256": "aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4"
      },
      {
        "name": "tokenizer_config.json",
        "sha256": "c27ef18dae7dccaee951f6066f71a1b35ca9ec4ff3168b097dbda7905a036324"
      },
      {
        "name": "vocab.json",
        "sha256": "ca10d7e9fb3ed18575dd1e277a2579c16d108e32f27439684afa0e10b1440910"
      }
    ],
    "weight_stats": [
      {
        "name": "model-00001-of-00017.safetensors",
        "size": 3957109648,
        "mtime_ns": 1748403884759368838
      },
      {
        "name": "model-00002-of-00017.safetensors",
        "size": 3900791760,
        "mtime_ns": 1748403843500367073
      },
      {
        "name": "model-00003-of-00017.safetensors",
        "size": 3900791760,
        "mtime_ns": 1748403802698365327
      },
      {
        "name": "model-00004-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403764242363681
      },
      {
        "name": "model-00005-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403722468361894
      },
      {
        "name": "model-00006-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403681711360150
      },
      {
        "name": "model-00007-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403639311358336
      },
      {
        "name": "model-00008-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403582299355896
      },
      {
        "name": "model-00009-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403530985353700
      },
      {
        "name": "model-00010-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403477210351399
      },
      {
        "name": "model-00011-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403422707349067
      },
      {
        "name": "model-00012-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403367315346697
      },
      {
        "name": "model-00013-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403315147344465
      },
      {
        "name": "model-00014-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403263569342258
      },
      {
        "name": "model-00015-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403212487340072
      },
      {
        "name": "model-00016-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403157024337699
      },
      {
        "name": "model-00017-of-00017.safetensors",
        "size": 3055341992,
        "mtime_ns": 1748403103933335427
      }
    ],
    "weight_contents_hashed": false,
    "software": {
      "python": "3.10.21",
      "torch": "2.6.0",
      "transformers": "4.51.3",
      "tokenizers": "0.21.4",
      "vllm": "0.8.5"
    }
  },
  "context_adjustment": {
    "base_protocol_sha256": "3f9b9cdd137cd71bc06c659c14711d87c4f45a5045292baacb00f91659713b59",
    "base_window": 8192,
    "required_model_len": 9158,
    "max_model_len": 16384,
    "selected_at": "2026-10-30T14:57:54+08:00"
  }
}
```

## 评测记录：2026-10-30T23:11:28+08:00（20261030T151128Z_77358733）

- 待测 JSONL：`/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.jsonl`；SHA256 `618df1162dbd1bbf770b90baabfd23226ef52fd3028f5fdb6490919cca78b92e`
- 固定 Clean-KD 参照：`/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl`；SHA256 `dd4cfdbe540e2227bbad3b46f6a64e34bb1a46b7e7d24860ef8be90ec03efd48`
- 本地裁判：`/shared/public_models/Qwen3-32B`；协议 `local-fixed-reference-half-tie-preferences-v1`
- 只评已保存完整回答，不生成学生或参照回答，不调用外部 API。

| Soft Win Rate ↑（平局半分） | 95% CI | 有效/计划题目 | 单轮胜/平/负 | 双顺序一致率 | 本次复用/新增判断 |
|---:|---|---:|---|---:|---:|
| 51.15% | [47.85%, 54.30%] | 500/500 | 41.30% / 19.70% / 39.00% | 67.80% | 0/1000 |

每题匿名交换 A/B 顺序两次。每轮映射胜=1、平=0.5、负=0，先取同题两轮均值，再对完整题目算术平均。这不是 PostMark 将平局算全胜的 Soft Win Rate；本报告明确采用半分。
单轮胜/平/负只统计双顺序均成功题目的 2N 次判定。交换顺序导致的相反选择不伪装成真实平局，另报顺序一致率。解析失败、拒答、超长及截断输出不计平；缺少任一顺序的题目不进入主指标。
CI 按题目成对 bootstrap，不覆盖裁判偏差或训练种子变异。50% 是相对固定参照的偏好平衡，不是正确率。
覆盖率 100.00%；本次完整评测：True；缓存：`/shared/wwx/EasyGAD/soft-win-rate/results/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_t.966cdc4683e9bb20/judgments.jsonl`；本次归档：`/shared/wwx/EasyGAD/soft-win-rate/results/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_t.966cdc4683e9bb20/runs/20261030T151128Z_77358733.json`。

自动窗口调整：8192 → 16384 token；已发现的输入及输出预留至少需要 9158 token。保留完整文本，实际并发与 GPU 见执行配置。

评分配置及实际执行配置：

```json
{
  "judge_configuration": {
    "model_path": "/shared/public_models/Qwen3-32B",
    "dtype": "bfloat16",
    "max_model_len": 16384,
    "max_num_seqs": 2,
    "max_num_batched_tokens": 4096,
    "enable_chunked_prefill": true,
    "max_output_tokens": 512,
    "seed": 42,
    "temperature": 0.0,
    "enable_thinking": false,
    "bootstrap": 2000,
    "retries": 2,
    "startup_timeout": 1200
  },
  "execution_plans": [
    {
      "gpu_ids": [
        1,
        3
      ],
      "gpu_uuids": [
        "GPU-aaaa1e22-8585-bcee-bf44-4dbbb57365ea",
        "GPU-cf0eb97d-d714-dfe3-034e-f00037747988"
      ],
      "tensor_parallel_size": 2,
      "gpu_memory_utilization": 0.98,
      "estimated_per_gpu_mib": 37388.4,
      "enforce_eager": true,
      "memory_accounting": "legacy_v1_total",
      "available_per_gpu_mib": 39608.8,
      "max_num_seqs": 2,
      "max_model_len": 16384,
      "communication_mode": "local_pcie_compatible",
      "disable_custom_all_reduce": true,
      "communication_environment": {
        "NCCL_P2P_DISABLE": "1",
        "NCCL_IB_DISABLE": "1",
        "NCCL_SHM_DISABLE": "0",
        "NCCL_SOCKET_IFNAME": "lo",
        "GLOO_SOCKET_IFNAME": "lo",
        "VLLM_HOST_IP": "127.0.0.1",
        "NCCL_DEBUG": "INFO"
      },
      "communication_timeout_seconds": 180,
      "distributed_executor_backend": "mp",
      "cuda_visible_devices": "1,3",
      "cuda_device_order": "PCI_BUS_ID",
      "vllm_use_v1": "1",
      "max_num_batched_tokens": 4096,
      "enable_chunked_prefill": true,
      "worker_directory": "/shared/wwx/EasyGAD/soft-win-rate/results/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_t.966cdc4683e9bb20/workers/20261030T224404_8848fee1/plan_00",
      "gpu_inventory": [
        {
          "index": 1,
          "uuid": "GPU-aaaa1e22-8585-bcee-bf44-4dbbb57365ea",
          "name": "NVIDIA A100 80GB PCIe",
          "total_mib": 81920,
          "free_mib": 66399,
          "utilization": 0
        },
        {
          "index": 3,
          "uuid": "GPU-cf0eb97d-d714-dfe3-034e-f00037747988",
          "name": "NVIDIA A100-PCIE-40GB",
          "total_mib": 40960,
          "free_mib": 40428,
          "utilization": 0
        }
      ]
    }
  ],
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
  "rubric_sha256": "23b028957f3cb38f4dc24706108fd73156ba747fc37203dfc7d87e8ead8e61dd",
  "model_fingerprint": {
    "path": "/shared/public_models/Qwen3-32B",
    "assets": [
      {
        "name": "config.json",
        "sha256": "8034152c9180e4b08ca1f656efa7bf52e117766fc2a09c126db394a473f557a0"
      },
      {
        "name": "configuration.json",
        "sha256": "f888421726665e8a84b738eed42a64875aed79de8be7daade851ac8bf4c0cef9"
      },
      {
        "name": "generation_config.json",
        "sha256": "90373e8a092a7abb965d3fea4671ef129bb9f4ee5a3005f0ab8a95b9716812cb"
      },
      {
        "name": "merges.txt",
        "sha256": "b8e04af9c950e393054010dcef499c3f005e803e9b2da1a09b96a26c33266eb1"
      },
      {
        "name": "model.safetensors.index.json",
        "sha256": "68e066a65be872628751f5603243a94ddf9f923340e81d245944f66f5b6a03e1"
      },
      {
        "name": "tokenizer.json",
        "sha256": "aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4"
      },
      {
        "name": "tokenizer_config.json",
        "sha256": "c27ef18dae7dccaee951f6066f71a1b35ca9ec4ff3168b097dbda7905a036324"
      },
      {
        "name": "vocab.json",
        "sha256": "ca10d7e9fb3ed18575dd1e277a2579c16d108e32f27439684afa0e10b1440910"
      }
    ],
    "weight_stats": [
      {
        "name": "model-00001-of-00017.safetensors",
        "size": 3957109648,
        "mtime_ns": 1748403884759368838
      },
      {
        "name": "model-00002-of-00017.safetensors",
        "size": 3900791760,
        "mtime_ns": 1748403843500367073
      },
      {
        "name": "model-00003-of-00017.safetensors",
        "size": 3900791760,
        "mtime_ns": 1748403802698365327
      },
      {
        "name": "model-00004-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403764242363681
      },
      {
        "name": "model-00005-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403722468361894
      },
      {
        "name": "model-00006-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403681711360150
      },
      {
        "name": "model-00007-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403639311358336
      },
      {
        "name": "model-00008-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403582299355896
      },
      {
        "name": "model-00009-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403530985353700
      },
      {
        "name": "model-00010-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403477210351399
      },
      {
        "name": "model-00011-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403422707349067
      },
      {
        "name": "model-00012-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403367315346697
      },
      {
        "name": "model-00013-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403315147344465
      },
      {
        "name": "model-00014-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403263569342258
      },
      {
        "name": "model-00015-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403212487340072
      },
      {
        "name": "model-00016-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403157024337699
      },
      {
        "name": "model-00017-of-00017.safetensors",
        "size": 3055341992,
        "mtime_ns": 1748403103933335427
      }
    ],
    "weight_contents_hashed": false,
    "software": {
      "python": "3.10.21",
      "torch": "2.6.0",
      "transformers": "4.51.3",
      "tokenizers": "0.21.4",
      "vllm": "0.8.5"
    }
  },
  "context_adjustment": {
    "base_protocol_sha256": "3f9b9cdd137cd71bc06c659c14711d87c4f45a5045292baacb00f91659713b59",
    "base_window": 8192,
    "required_model_len": 9158,
    "max_model_len": 16384,
    "selected_at": "2026-10-30T14:57:54+08:00"
  }
}
```

## 评测记录：2026-10-30T23:52:30+08:00（20261030T155230Z_ec1d4bdf）

- 待测 JSONL：`/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_warmup_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.jsonl`；SHA256 `eccdb602ca9bcbdc0a01cca653bf5f8242fccddecda2225359a0b98e74ff535c`
- 固定 Clean-KD 参照：`/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl`；SHA256 `dd4cfdbe540e2227bbad3b46f6a64e34bb1a46b7e7d24860ef8be90ec03efd48`
- 本地裁判：`/shared/public_models/Qwen3-32B`；协议 `local-fixed-reference-half-tie-preferences-v1`
- 只评已保存完整回答，不生成学生或参照回答，不调用外部 API。

| Soft Win Rate ↑（平局半分） | 95% CI | 有效/计划题目 | 单轮胜/平/负 | 双顺序一致率 | 本次复用/新增判断 |
|---:|---|---:|---|---:|---:|
| 38.00% | [34.80%, 41.20%] | 500/500 | 27.90% / 20.20% / 51.90% | 71.80% | 0/1000 |

每题匿名交换 A/B 顺序两次。每轮映射胜=1、平=0.5、负=0，先取同题两轮均值，再对完整题目算术平均。这不是 PostMark 将平局算全胜的 Soft Win Rate；本报告明确采用半分。
单轮胜/平/负只统计双顺序均成功题目的 2N 次判定。交换顺序导致的相反选择不伪装成真实平局，另报顺序一致率。解析失败、拒答、超长及截断输出不计平；缺少任一顺序的题目不进入主指标。
CI 按题目成对 bootstrap，不覆盖裁判偏差或训练种子变异。50% 是相对固定参照的偏好平衡，不是正确率。
覆盖率 100.00%；本次完整评测：True；缓存：`/shared/wwx/EasyGAD/soft-win-rate/results/kgwwarmup_kgwgad_warmup_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15.8cec771a767e15a4/judgments.jsonl`；本次归档：`/shared/wwx/EasyGAD/soft-win-rate/results/kgwwarmup_kgwgad_warmup_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15.8cec771a767e15a4/runs/20261030T155230Z_ec1d4bdf.json`。

自动窗口调整：8192 → 16384 token；已发现的输入及输出预留至少需要 9171 token。保留完整文本，实际并发与 GPU 见执行配置。

评分配置及实际执行配置：

```json
{
  "judge_configuration": {
    "model_path": "/shared/public_models/Qwen3-32B",
    "dtype": "bfloat16",
    "max_model_len": 16384,
    "max_num_seqs": 2,
    "max_num_batched_tokens": 4096,
    "enable_chunked_prefill": true,
    "max_output_tokens": 512,
    "seed": 42,
    "temperature": 0.0,
    "enable_thinking": false,
    "bootstrap": 2000,
    "retries": 2,
    "startup_timeout": 1200
  },
  "execution_plans": [
    {
      "gpu_ids": [
        1,
        3
      ],
      "gpu_uuids": [
        "GPU-aaaa1e22-8585-bcee-bf44-4dbbb57365ea",
        "GPU-cf0eb97d-d714-dfe3-034e-f00037747988"
      ],
      "tensor_parallel_size": 2,
      "gpu_memory_utilization": 0.98,
      "estimated_per_gpu_mib": 37388.4,
      "enforce_eager": true,
      "memory_accounting": "legacy_v1_total",
      "available_per_gpu_mib": 39608.8,
      "max_num_seqs": 2,
      "max_model_len": 16384,
      "communication_mode": "local_pcie_compatible",
      "disable_custom_all_reduce": true,
      "communication_environment": {
        "NCCL_P2P_DISABLE": "1",
        "NCCL_IB_DISABLE": "1",
        "NCCL_SHM_DISABLE": "0",
        "NCCL_SOCKET_IFNAME": "lo",
        "GLOO_SOCKET_IFNAME": "lo",
        "VLLM_HOST_IP": "127.0.0.1",
        "NCCL_DEBUG": "INFO"
      },
      "communication_timeout_seconds": 180,
      "distributed_executor_backend": "mp",
      "cuda_visible_devices": "1,3",
      "cuda_device_order": "PCI_BUS_ID",
      "vllm_use_v1": "1",
      "max_num_batched_tokens": 4096,
      "enable_chunked_prefill": true,
      "worker_directory": "/shared/wwx/EasyGAD/soft-win-rate/results/kgwwarmup_kgwgad_warmup_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15.8cec771a767e15a4/workers/20261030T232516_9ad8f88f/plan_00",
      "gpu_inventory": [
        {
          "index": 1,
          "uuid": "GPU-aaaa1e22-8585-bcee-bf44-4dbbb57365ea",
          "name": "NVIDIA A100 80GB PCIe",
          "total_mib": 81920,
          "free_mib": 66413,
          "utilization": 0
        },
        {
          "index": 3,
          "uuid": "GPU-cf0eb97d-d714-dfe3-034e-f00037747988",
          "name": "NVIDIA A100-PCIE-40GB",
          "total_mib": 40960,
          "free_mib": 40428,
          "utilization": 0
        }
      ]
    }
  ],
  "input_generation": {
    "samples": 500,
    "empty_answers": 0,
    "mean_answer_characters": 1037.756,
    "student_model_paths": [
      "/shared/wwx/EasyGAD/checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_new/warmup/global_step_1813/actor/huggingface"
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
  "rubric_sha256": "23b028957f3cb38f4dc24706108fd73156ba747fc37203dfc7d87e8ead8e61dd",
  "model_fingerprint": {
    "path": "/shared/public_models/Qwen3-32B",
    "assets": [
      {
        "name": "config.json",
        "sha256": "8034152c9180e4b08ca1f656efa7bf52e117766fc2a09c126db394a473f557a0"
      },
      {
        "name": "configuration.json",
        "sha256": "f888421726665e8a84b738eed42a64875aed79de8be7daade851ac8bf4c0cef9"
      },
      {
        "name": "generation_config.json",
        "sha256": "90373e8a092a7abb965d3fea4671ef129bb9f4ee5a3005f0ab8a95b9716812cb"
      },
      {
        "name": "merges.txt",
        "sha256": "b8e04af9c950e393054010dcef499c3f005e803e9b2da1a09b96a26c33266eb1"
      },
      {
        "name": "model.safetensors.index.json",
        "sha256": "68e066a65be872628751f5603243a94ddf9f923340e81d245944f66f5b6a03e1"
      },
      {
        "name": "tokenizer.json",
        "sha256": "aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4"
      },
      {
        "name": "tokenizer_config.json",
        "sha256": "c27ef18dae7dccaee951f6066f71a1b35ca9ec4ff3168b097dbda7905a036324"
      },
      {
        "name": "vocab.json",
        "sha256": "ca10d7e9fb3ed18575dd1e277a2579c16d108e32f27439684afa0e10b1440910"
      }
    ],
    "weight_stats": [
      {
        "name": "model-00001-of-00017.safetensors",
        "size": 3957109648,
        "mtime_ns": 1748403884759368838
      },
      {
        "name": "model-00002-of-00017.safetensors",
        "size": 3900791760,
        "mtime_ns": 1748403843500367073
      },
      {
        "name": "model-00003-of-00017.safetensors",
        "size": 3900791760,
        "mtime_ns": 1748403802698365327
      },
      {
        "name": "model-00004-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403764242363681
      },
      {
        "name": "model-00005-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403722468361894
      },
      {
        "name": "model-00006-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403681711360150
      },
      {
        "name": "model-00007-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403639311358336
      },
      {
        "name": "model-00008-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403582299355896
      },
      {
        "name": "model-00009-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403530985353700
      },
      {
        "name": "model-00010-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403477210351399
      },
      {
        "name": "model-00011-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403422707349067
      },
      {
        "name": "model-00012-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403367315346697
      },
      {
        "name": "model-00013-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403315147344465
      },
      {
        "name": "model-00014-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403263569342258
      },
      {
        "name": "model-00015-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403212487340072
      },
      {
        "name": "model-00016-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403157024337699
      },
      {
        "name": "model-00017-of-00017.safetensors",
        "size": 3055341992,
        "mtime_ns": 1748403103933335427
      }
    ],
    "weight_contents_hashed": false,
    "software": {
      "python": "3.10.21",
      "torch": "2.6.0",
      "transformers": "4.51.3",
      "tokenizers": "0.21.4",
      "vllm": "0.8.5"
    }
  },
  "context_adjustment": {
    "base_protocol_sha256": "b9ba8e04dae90df89c8e344e35f495e1ab390c42b9f45af6d753ea1d99de3dd7",
    "base_window": 8192,
    "required_model_len": 9171,
    "max_model_len": 16384,
    "selected_at": "2026-10-30T23:25:16+08:00"
  }
}
```

## 评测记录：2026-10-31T00:22:12+08:00（20261030T162212Z_cb6ab7a4）

- 待测 JSONL：`/shared/wwx/EasyGAD/wm_test/cleanD_dipperparaSFT_dipperparagad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl`；SHA256 `3d35e43ee786d40ea166608bbea1bab245425c775b54ae5212007fe879431738`
- 固定 Clean-KD 参照：`/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl`；SHA256 `dd4cfdbe540e2227bbad3b46f6a64e34bb1a46b7e7d24860ef8be90ec03efd48`
- 本地裁判：`/shared/public_models/Qwen3-32B`；协议 `local-fixed-reference-half-tie-preferences-v1`
- 只评已保存完整回答，不生成学生或参照回答，不调用外部 API。

| Soft Win Rate ↑（平局半分） | 95% CI | 有效/计划题目 | 单轮胜/平/负 | 双顺序一致率 | 本次复用/新增判断 |
|---:|---|---:|---|---:|---:|
| 23.30% | [20.55%, 26.30%] | 500/500 | 15.60% / 15.40% / 69.00% | 79.20% | 0/1000 |

每题匿名交换 A/B 顺序两次。每轮映射胜=1、平=0.5、负=0，先取同题两轮均值，再对完整题目算术平均。这不是 PostMark 将平局算全胜的 Soft Win Rate；本报告明确采用半分。
单轮胜/平/负只统计双顺序均成功题目的 2N 次判定。交换顺序导致的相反选择不伪装成真实平局，另报顺序一致率。解析失败、拒答、超长及截断输出不计平；缺少任一顺序的题目不进入主指标。
CI 按题目成对 bootstrap，不覆盖裁判偏差或训练种子变异。50% 是相对固定参照的偏好平衡，不是正确率。
覆盖率 100.00%；本次完整评测：True；缓存：`/shared/wwx/EasyGAD/soft-win-rate/results/cleanD_dipperparaSFT_dipperparagad_warmup_gamma0.5_qwen2_5_0_5b_.a1934bd545c826eb/judgments.jsonl`；本次归档：`/shared/wwx/EasyGAD/soft-win-rate/results/cleanD_dipperparaSFT_dipperparagad_warmup_gamma0.5_qwen2_5_0_5b_.a1934bd545c826eb/runs/20261030T162212Z_cb6ab7a4.json`。

评分配置及实际执行配置：

```json
{
  "judge_configuration": {
    "model_path": "/shared/public_models/Qwen3-32B",
    "dtype": "bfloat16",
    "max_model_len": 8192,
    "max_num_seqs": 2,
    "max_num_batched_tokens": 4096,
    "enable_chunked_prefill": true,
    "max_output_tokens": 512,
    "seed": 42,
    "temperature": 0.0,
    "enable_thinking": false,
    "bootstrap": 2000,
    "retries": 2,
    "startup_timeout": 1200
  },
  "execution_plans": [
    {
      "gpu_ids": [
        1,
        3
      ],
      "gpu_uuids": [
        "GPU-aaaa1e22-8585-bcee-bf44-4dbbb57365ea",
        "GPU-cf0eb97d-d714-dfe3-034e-f00037747988"
      ],
      "tensor_parallel_size": 2,
      "gpu_memory_utilization": 0.98,
      "estimated_per_gpu_mib": 35340.4,
      "enforce_eager": true,
      "memory_accounting": "legacy_v1_total",
      "available_per_gpu_mib": 39608.8,
      "max_num_seqs": 2,
      "max_model_len": 8192,
      "communication_mode": "local_pcie_compatible",
      "disable_custom_all_reduce": true,
      "communication_environment": {
        "NCCL_P2P_DISABLE": "1",
        "NCCL_IB_DISABLE": "1",
        "NCCL_SHM_DISABLE": "0",
        "NCCL_SOCKET_IFNAME": "lo",
        "GLOO_SOCKET_IFNAME": "lo",
        "VLLM_HOST_IP": "127.0.0.1",
        "NCCL_DEBUG": "INFO"
      },
      "communication_timeout_seconds": 180,
      "distributed_executor_backend": "mp",
      "cuda_visible_devices": "1,3",
      "cuda_device_order": "PCI_BUS_ID",
      "vllm_use_v1": "1",
      "max_num_batched_tokens": 4096,
      "enable_chunked_prefill": true,
      "worker_directory": "/shared/wwx/EasyGAD/soft-win-rate/results/cleanD_dipperparaSFT_dipperparagad_warmup_gamma0.5_qwen2_5_0_5b_.a1934bd545c826eb/workers/20261030T235416_751231d3/plan_00",
      "gpu_inventory": [
        {
          "index": 1,
          "uuid": "GPU-aaaa1e22-8585-bcee-bf44-4dbbb57365ea",
          "name": "NVIDIA A100 80GB PCIe",
          "total_mib": 81920,
          "free_mib": 50624,
          "utilization": 0
        },
        {
          "index": 3,
          "uuid": "GPU-cf0eb97d-d714-dfe3-034e-f00037747988",
          "name": "NVIDIA A100-PCIE-40GB",
          "total_mib": 40960,
          "free_mib": 40428,
          "utilization": 0
        }
      ]
    }
  ],
  "input_generation": {
    "samples": 500,
    "empty_answers": 0,
    "mean_answer_characters": 797.598,
    "student_model_paths": [
      "/shared/wwx/EasyGAD/checkpoints/kgwD_paraSFT_paraGAD_v1/warmup/global_step_1813/actor/huggingface"
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
  "rubric_sha256": "23b028957f3cb38f4dc24706108fd73156ba747fc37203dfc7d87e8ead8e61dd",
  "model_fingerprint": {
    "path": "/shared/public_models/Qwen3-32B",
    "assets": [
      {
        "name": "config.json",
        "sha256": "8034152c9180e4b08ca1f656efa7bf52e117766fc2a09c126db394a473f557a0"
      },
      {
        "name": "configuration.json",
        "sha256": "f888421726665e8a84b738eed42a64875aed79de8be7daade851ac8bf4c0cef9"
      },
      {
        "name": "generation_config.json",
        "sha256": "90373e8a092a7abb965d3fea4671ef129bb9f4ee5a3005f0ab8a95b9716812cb"
      },
      {
        "name": "merges.txt",
        "sha256": "b8e04af9c950e393054010dcef499c3f005e803e9b2da1a09b96a26c33266eb1"
      },
      {
        "name": "model.safetensors.index.json",
        "sha256": "68e066a65be872628751f5603243a94ddf9f923340e81d245944f66f5b6a03e1"
      },
      {
        "name": "tokenizer.json",
        "sha256": "aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4"
      },
      {
        "name": "tokenizer_config.json",
        "sha256": "c27ef18dae7dccaee951f6066f71a1b35ca9ec4ff3168b097dbda7905a036324"
      },
      {
        "name": "vocab.json",
        "sha256": "ca10d7e9fb3ed18575dd1e277a2579c16d108e32f27439684afa0e10b1440910"
      }
    ],
    "weight_stats": [
      {
        "name": "model-00001-of-00017.safetensors",
        "size": 3957109648,
        "mtime_ns": 1748403884759368838
      },
      {
        "name": "model-00002-of-00017.safetensors",
        "size": 3900791760,
        "mtime_ns": 1748403843500367073
      },
      {
        "name": "model-00003-of-00017.safetensors",
        "size": 3900791760,
        "mtime_ns": 1748403802698365327
      },
      {
        "name": "model-00004-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403764242363681
      },
      {
        "name": "model-00005-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403722468361894
      },
      {
        "name": "model-00006-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403681711360150
      },
      {
        "name": "model-00007-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403639311358336
      },
      {
        "name": "model-00008-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403582299355896
      },
      {
        "name": "model-00009-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403530985353700
      },
      {
        "name": "model-00010-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403477210351399
      },
      {
        "name": "model-00011-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403422707349067
      },
      {
        "name": "model-00012-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403367315346697
      },
      {
        "name": "model-00013-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403315147344465
      },
      {
        "name": "model-00014-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403263569342258
      },
      {
        "name": "model-00015-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403212487340072
      },
      {
        "name": "model-00016-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403157024337699
      },
      {
        "name": "model-00017-of-00017.safetensors",
        "size": 3055341992,
        "mtime_ns": 1748403103933335427
      }
    ],
    "weight_contents_hashed": false,
    "software": {
      "python": "3.10.21",
      "torch": "2.6.0",
      "transformers": "4.51.3",
      "tokenizers": "0.21.4",
      "vllm": "0.8.5"
    }
  },
  "context_adjustment": null
}
```

## 评测记录：2026-10-31T00:22:34+08:00（20261030T162234Z_e504bf1e）

- 待测 JSONL：`/shared/wwx/EasyGAD/wm_test/cleanD_dipperparaSFT_dipperparagad_warmup_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl`；SHA256 `3d35e43ee786d40ea166608bbea1bab245425c775b54ae5212007fe879431738`
- 固定 Clean-KD 参照：`/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl`；SHA256 `dd4cfdbe540e2227bbad3b46f6a64e34bb1a46b7e7d24860ef8be90ec03efd48`
- 本地裁判：`/shared/public_models/Qwen3-32B`；协议 `local-fixed-reference-half-tie-preferences-v1`
- 只评已保存完整回答，不生成学生或参照回答，不调用外部 API。

| Soft Win Rate ↑（平局半分） | 95% CI | 有效/计划题目 | 单轮胜/平/负 | 双顺序一致率 | 本次复用/新增判断 |
|---:|---|---:|---|---:|---:|
| 23.30% | [20.55%, 26.30%] | 500/500 | 15.60% / 15.40% / 69.00% | 79.20% | 1000/0 |

每题匿名交换 A/B 顺序两次。每轮映射胜=1、平=0.5、负=0，先取同题两轮均值，再对完整题目算术平均。这不是 PostMark 将平局算全胜的 Soft Win Rate；本报告明确采用半分。
单轮胜/平/负只统计双顺序均成功题目的 2N 次判定。交换顺序导致的相反选择不伪装成真实平局，另报顺序一致率。解析失败、拒答、超长及截断输出不计平；缺少任一顺序的题目不进入主指标。
CI 按题目成对 bootstrap，不覆盖裁判偏差或训练种子变异。50% 是相对固定参照的偏好平衡，不是正确率。
覆盖率 100.00%；本次完整评测：True；缓存：`/shared/wwx/EasyGAD/soft-win-rate/results/cleanD_dipperparaSFT_dipperparagad_warmup_gamma0.5_qwen2_5_0_5b_.a1934bd545c826eb/judgments.jsonl`；本次归档：`/shared/wwx/EasyGAD/soft-win-rate/results/cleanD_dipperparaSFT_dipperparagad_warmup_gamma0.5_qwen2_5_0_5b_.a1934bd545c826eb/runs/20261030T162234Z_e504bf1e.json`。

评分配置及实际执行配置：

```json
{
  "judge_configuration": {
    "model_path": "/shared/public_models/Qwen3-32B",
    "dtype": "bfloat16",
    "max_model_len": 8192,
    "max_num_seqs": 2,
    "max_num_batched_tokens": 4096,
    "enable_chunked_prefill": true,
    "max_output_tokens": 512,
    "seed": 42,
    "temperature": 0.0,
    "enable_thinking": false,
    "bootstrap": 2000,
    "retries": 2,
    "startup_timeout": 1200
  },
  "execution_plans": [
    {
      "available_per_gpu_mib": 39608.8,
      "communication_environment": {
        "GLOO_SOCKET_IFNAME": "lo",
        "NCCL_DEBUG": "INFO",
        "NCCL_IB_DISABLE": "1",
        "NCCL_P2P_DISABLE": "1",
        "NCCL_SHM_DISABLE": "0",
        "NCCL_SOCKET_IFNAME": "lo",
        "VLLM_HOST_IP": "127.0.0.1"
      },
      "communication_mode": "local_pcie_compatible",
      "communication_timeout_seconds": 180,
      "cuda_device_order": "PCI_BUS_ID",
      "cuda_visible_devices": "1,3",
      "disable_custom_all_reduce": true,
      "distributed_executor_backend": "mp",
      "enable_chunked_prefill": true,
      "enforce_eager": true,
      "estimated_per_gpu_mib": 35340.4,
      "gpu_ids": [
        1,
        3
      ],
      "gpu_inventory": [
        {
          "free_mib": 50624,
          "index": 1,
          "name": "NVIDIA A100 80GB PCIe",
          "total_mib": 81920,
          "utilization": 0,
          "uuid": "GPU-aaaa1e22-8585-bcee-bf44-4dbbb57365ea"
        },
        {
          "free_mib": 40428,
          "index": 3,
          "name": "NVIDIA A100-PCIE-40GB",
          "total_mib": 40960,
          "utilization": 0,
          "uuid": "GPU-cf0eb97d-d714-dfe3-034e-f00037747988"
        }
      ],
      "gpu_memory_utilization": 0.98,
      "gpu_uuids": [
        "GPU-aaaa1e22-8585-bcee-bf44-4dbbb57365ea",
        "GPU-cf0eb97d-d714-dfe3-034e-f00037747988"
      ],
      "max_model_len": 8192,
      "max_num_batched_tokens": 4096,
      "max_num_seqs": 2,
      "memory_accounting": "legacy_v1_total",
      "tensor_parallel_size": 2,
      "vllm_use_v1": "1",
      "worker_directory": "/shared/wwx/EasyGAD/soft-win-rate/results/cleanD_dipperparaSFT_dipperparagad_warmup_gamma0.5_qwen2_5_0_5b_.a1934bd545c826eb/workers/20261030T235416_751231d3/plan_00"
    }
  ],
  "input_generation": {
    "samples": 500,
    "empty_answers": 0,
    "mean_answer_characters": 797.598,
    "student_model_paths": [
      "/shared/wwx/EasyGAD/checkpoints/kgwD_paraSFT_paraGAD_v1/warmup/global_step_1813/actor/huggingface"
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
  "rubric_sha256": "23b028957f3cb38f4dc24706108fd73156ba747fc37203dfc7d87e8ead8e61dd",
  "model_fingerprint": {
    "path": "/shared/public_models/Qwen3-32B",
    "assets": [
      {
        "name": "config.json",
        "sha256": "8034152c9180e4b08ca1f656efa7bf52e117766fc2a09c126db394a473f557a0"
      },
      {
        "name": "configuration.json",
        "sha256": "f888421726665e8a84b738eed42a64875aed79de8be7daade851ac8bf4c0cef9"
      },
      {
        "name": "generation_config.json",
        "sha256": "90373e8a092a7abb965d3fea4671ef129bb9f4ee5a3005f0ab8a95b9716812cb"
      },
      {
        "name": "merges.txt",
        "sha256": "b8e04af9c950e393054010dcef499c3f005e803e9b2da1a09b96a26c33266eb1"
      },
      {
        "name": "model.safetensors.index.json",
        "sha256": "68e066a65be872628751f5603243a94ddf9f923340e81d245944f66f5b6a03e1"
      },
      {
        "name": "tokenizer.json",
        "sha256": "aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4"
      },
      {
        "name": "tokenizer_config.json",
        "sha256": "c27ef18dae7dccaee951f6066f71a1b35ca9ec4ff3168b097dbda7905a036324"
      },
      {
        "name": "vocab.json",
        "sha256": "ca10d7e9fb3ed18575dd1e277a2579c16d108e32f27439684afa0e10b1440910"
      }
    ],
    "weight_stats": [
      {
        "name": "model-00001-of-00017.safetensors",
        "size": 3957109648,
        "mtime_ns": 1748403884759368838
      },
      {
        "name": "model-00002-of-00017.safetensors",
        "size": 3900791760,
        "mtime_ns": 1748403843500367073
      },
      {
        "name": "model-00003-of-00017.safetensors",
        "size": 3900791760,
        "mtime_ns": 1748403802698365327
      },
      {
        "name": "model-00004-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403764242363681
      },
      {
        "name": "model-00005-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403722468361894
      },
      {
        "name": "model-00006-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403681711360150
      },
      {
        "name": "model-00007-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403639311358336
      },
      {
        "name": "model-00008-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403582299355896
      },
      {
        "name": "model-00009-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403530985353700
      },
      {
        "name": "model-00010-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403477210351399
      },
      {
        "name": "model-00011-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403422707349067
      },
      {
        "name": "model-00012-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403367315346697
      },
      {
        "name": "model-00013-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403315147344465
      },
      {
        "name": "model-00014-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403263569342258
      },
      {
        "name": "model-00015-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403212487340072
      },
      {
        "name": "model-00016-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403157024337699
      },
      {
        "name": "model-00017-of-00017.safetensors",
        "size": 3055341992,
        "mtime_ns": 1748403103933335427
      }
    ],
    "weight_contents_hashed": false,
    "software": {
      "python": "3.10.21",
      "torch": "2.6.0",
      "transformers": "4.51.3",
      "tokenizers": "0.21.4",
      "vllm": "0.8.5"
    }
  },
  "context_adjustment": null
}
```

## 评测记录：2026-10-31T00:28:33+08:00（20261030T162833Z_9baf05b2）

- 待测 JSONL：`/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta3_new1_qwen2_5_0_5b_dolly15k_test.jsonl`；SHA256 `b1c02a02c9e074669d99cc9965618971b50b81e66d62c386002cdde73652f192`
- 固定 Clean-KD 参照：`/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl`；SHA256 `dd4cfdbe540e2227bbad3b46f6a64e34bb1a46b7e7d24860ef8be90ec03efd48`
- 本地裁判：`/shared/public_models/Qwen3-32B`；协议 `local-fixed-reference-half-tie-preferences-v1`
- 只评已保存完整回答，不生成学生或参照回答，不调用外部 API。

| Soft Win Rate ↑（平局半分） | 95% CI | 有效/计划题目 | 单轮胜/平/负 | 双顺序一致率 | 本次复用/新增判断 |
|---:|---|---:|---|---:|---:|
| 29.00% | [26.05%, 31.95%] | 500/500 | 21.30% / 15.40% / 63.30% | 76.80% | 1000/0 |

每题匿名交换 A/B 顺序两次。每轮映射胜=1、平=0.5、负=0，先取同题两轮均值，再对完整题目算术平均。这不是 PostMark 将平局算全胜的 Soft Win Rate；本报告明确采用半分。
单轮胜/平/负只统计双顺序均成功题目的 2N 次判定。交换顺序导致的相反选择不伪装成真实平局，另报顺序一致率。解析失败、拒答、超长及截断输出不计平；缺少任一顺序的题目不进入主指标。
CI 按题目成对 bootstrap，不覆盖裁判偏差或训练种子变异。50% 是相对固定参照的偏好平衡，不是正确率。
覆盖率 100.00%；本次完整评测：True；缓存：`/shared/wwx/EasyGAD/soft-win-rate/results/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta3_new1_qwen2_5_0_5.d5bf1ff1da3c4875/judgments.jsonl`；本次归档：`/shared/wwx/EasyGAD/soft-win-rate/results/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta3_new1_qwen2_5_0_5.d5bf1ff1da3c4875/runs/20261030T162833Z_9baf05b2.json`。

评分配置及实际执行配置：

```json
{
  "judge_configuration": {
    "model_path": "/shared/public_models/Qwen3-32B",
    "dtype": "bfloat16",
    "max_model_len": 8192,
    "max_num_seqs": 2,
    "max_num_batched_tokens": 4096,
    "enable_chunked_prefill": true,
    "max_output_tokens": 512,
    "seed": 42,
    "temperature": 0.0,
    "enable_thinking": false,
    "bootstrap": 2000,
    "retries": 2,
    "startup_timeout": 1200
  },
  "execution_plans": [
    {
      "available_per_gpu_mib": 39608.8,
      "cuda_device_order": "PCI_BUS_ID",
      "cuda_visible_devices": "1,3",
      "distributed_executor_backend": "mp",
      "enable_chunked_prefill": true,
      "enforce_eager": true,
      "estimated_per_gpu_mib": 35340.4,
      "gpu_ids": [
        1,
        3
      ],
      "gpu_inventory": [
        {
          "free_mib": 54985,
          "index": 1,
          "name": "NVIDIA A100 80GB PCIe",
          "total_mib": 81920,
          "utilization": 0,
          "uuid": "GPU-aaaa1e22-8585-bcee-bf44-4dbbb57365ea"
        },
        {
          "free_mib": 40428,
          "index": 3,
          "name": "NVIDIA A100-PCIE-40GB",
          "total_mib": 40960,
          "utilization": 0,
          "uuid": "GPU-cf0eb97d-d714-dfe3-034e-f00037747988"
        }
      ],
      "gpu_memory_utilization": 0.98,
      "gpu_uuids": [
        "GPU-aaaa1e22-8585-bcee-bf44-4dbbb57365ea",
        "GPU-cf0eb97d-d714-dfe3-034e-f00037747988"
      ],
      "max_model_len": 8192,
      "max_num_batched_tokens": 4096,
      "max_num_seqs": 2,
      "memory_accounting": "legacy_v1_total",
      "tensor_parallel_size": 2,
      "vllm_use_v1": "1",
      "worker_directory": "/shared/wwx/EasyGAD/soft-win-rate/results/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta3_new1_qwen2_5_0_5.d5bf1ff1da3c4875/workers/20261029T230618_eab279f8/plan_00"
    }
  ],
  "input_generation": {
    "samples": 500,
    "empty_answers": 0,
    "mean_answer_characters": 600.578,
    "student_model_paths": [
      "/shared/wwx/EasyGAD/checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_new1_dipper2stage/gad/global_step_1813/actor/huggingface"
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
  "rubric_sha256": "23b028957f3cb38f4dc24706108fd73156ba747fc37203dfc7d87e8ead8e61dd",
  "model_fingerprint": {
    "path": "/shared/public_models/Qwen3-32B",
    "assets": [
      {
        "name": "config.json",
        "sha256": "8034152c9180e4b08ca1f656efa7bf52e117766fc2a09c126db394a473f557a0"
      },
      {
        "name": "configuration.json",
        "sha256": "f888421726665e8a84b738eed42a64875aed79de8be7daade851ac8bf4c0cef9"
      },
      {
        "name": "generation_config.json",
        "sha256": "90373e8a092a7abb965d3fea4671ef129bb9f4ee5a3005f0ab8a95b9716812cb"
      },
      {
        "name": "merges.txt",
        "sha256": "b8e04af9c950e393054010dcef499c3f005e803e9b2da1a09b96a26c33266eb1"
      },
      {
        "name": "model.safetensors.index.json",
        "sha256": "68e066a65be872628751f5603243a94ddf9f923340e81d245944f66f5b6a03e1"
      },
      {
        "name": "tokenizer.json",
        "sha256": "aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4"
      },
      {
        "name": "tokenizer_config.json",
        "sha256": "c27ef18dae7dccaee951f6066f71a1b35ca9ec4ff3168b097dbda7905a036324"
      },
      {
        "name": "vocab.json",
        "sha256": "ca10d7e9fb3ed18575dd1e277a2579c16d108e32f27439684afa0e10b1440910"
      }
    ],
    "weight_stats": [
      {
        "name": "model-00001-of-00017.safetensors",
        "size": 3957109648,
        "mtime_ns": 1748403884759368838
      },
      {
        "name": "model-00002-of-00017.safetensors",
        "size": 3900791760,
        "mtime_ns": 1748403843500367073
      },
      {
        "name": "model-00003-of-00017.safetensors",
        "size": 3900791760,
        "mtime_ns": 1748403802698365327
      },
      {
        "name": "model-00004-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403764242363681
      },
      {
        "name": "model-00005-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403722468361894
      },
      {
        "name": "model-00006-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403681711360150
      },
      {
        "name": "model-00007-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403639311358336
      },
      {
        "name": "model-00008-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403582299355896
      },
      {
        "name": "model-00009-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403530985353700
      },
      {
        "name": "model-00010-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403477210351399
      },
      {
        "name": "model-00011-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403422707349067
      },
      {
        "name": "model-00012-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403367315346697
      },
      {
        "name": "model-00013-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403315147344465
      },
      {
        "name": "model-00014-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403263569342258
      },
      {
        "name": "model-00015-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403212487340072
      },
      {
        "name": "model-00016-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403157024337699
      },
      {
        "name": "model-00017-of-00017.safetensors",
        "size": 3055341992,
        "mtime_ns": 1748403103933335427
      }
    ],
    "weight_contents_hashed": false,
    "software": {
      "python": "3.10.21",
      "torch": "2.6.0",
      "transformers": "4.51.3",
      "tokenizers": "0.21.4",
      "vllm": "0.8.5"
    }
  },
  "context_adjustment": null
}
```

## 评测记录：2026-10-31T00:56:15+08:00（20261030T165615Z_3983f003）

- 待测 JSONL：`/shared/wwx/EasyGAD/wm_test/dipper_upkgwwarmup_upkgwgad_warmup_gamma0.5_delta3_new1_qwen2_5_0_5b_dolly15k_test.jsonl`；SHA256 `14216367ab935fa4c3126262a6850b971306e95dfd3c984d361c53d3acbc5936`
- 固定 Clean-KD 参照：`/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl`；SHA256 `dd4cfdbe540e2227bbad3b46f6a64e34bb1a46b7e7d24860ef8be90ec03efd48`
- 本地裁判：`/shared/public_models/Qwen3-32B`；协议 `local-fixed-reference-half-tie-preferences-v1`
- 只评已保存完整回答，不生成学生或参照回答，不调用外部 API。

| Soft Win Rate ↑（平局半分） | 95% CI | 有效/计划题目 | 单轮胜/平/负 | 双顺序一致率 | 本次复用/新增判断 |
|---:|---|---:|---|---:|---:|
| 23.10% | [20.20%, 26.10%] | 500/500 | 16.00% / 14.20% / 69.80% | 80.60% | 0/1000 |

每题匿名交换 A/B 顺序两次。每轮映射胜=1、平=0.5、负=0，先取同题两轮均值，再对完整题目算术平均。这不是 PostMark 将平局算全胜的 Soft Win Rate；本报告明确采用半分。
单轮胜/平/负只统计双顺序均成功题目的 2N 次判定。交换顺序导致的相反选择不伪装成真实平局，另报顺序一致率。解析失败、拒答、超长及截断输出不计平；缺少任一顺序的题目不进入主指标。
CI 按题目成对 bootstrap，不覆盖裁判偏差或训练种子变异。50% 是相对固定参照的偏好平衡，不是正确率。
覆盖率 100.00%；本次完整评测：True；缓存：`/shared/wwx/EasyGAD/soft-win-rate/results/dipper_upkgwwarmup_upkgwgad_warmup_gamma0.5_delta3_new1_qwen2_5_.ee2082e3d13a593c/judgments.jsonl`；本次归档：`/shared/wwx/EasyGAD/soft-win-rate/results/dipper_upkgwwarmup_upkgwgad_warmup_gamma0.5_delta3_new1_qwen2_5_.ee2082e3d13a593c/runs/20261030T165615Z_3983f003.json`。

评分配置及实际执行配置：

```json
{
  "judge_configuration": {
    "model_path": "/shared/public_models/Qwen3-32B",
    "dtype": "bfloat16",
    "max_model_len": 8192,
    "max_num_seqs": 2,
    "max_num_batched_tokens": 4096,
    "enable_chunked_prefill": true,
    "max_output_tokens": 512,
    "seed": 42,
    "temperature": 0.0,
    "enable_thinking": false,
    "bootstrap": 2000,
    "retries": 2,
    "startup_timeout": 1200
  },
  "execution_plans": [
    {
      "gpu_ids": [
        1,
        3
      ],
      "gpu_uuids": [
        "GPU-aaaa1e22-8585-bcee-bf44-4dbbb57365ea",
        "GPU-cf0eb97d-d714-dfe3-034e-f00037747988"
      ],
      "tensor_parallel_size": 2,
      "gpu_memory_utilization": 0.98,
      "estimated_per_gpu_mib": 35340.4,
      "enforce_eager": true,
      "memory_accounting": "legacy_v1_total",
      "available_per_gpu_mib": 39608.8,
      "max_num_seqs": 2,
      "max_model_len": 8192,
      "communication_mode": "local_pcie_compatible",
      "disable_custom_all_reduce": true,
      "communication_environment": {
        "NCCL_P2P_DISABLE": "1",
        "NCCL_IB_DISABLE": "1",
        "NCCL_SHM_DISABLE": "0",
        "NCCL_SOCKET_IFNAME": "lo",
        "GLOO_SOCKET_IFNAME": "lo",
        "VLLM_HOST_IP": "127.0.0.1",
        "NCCL_DEBUG": "INFO"
      },
      "communication_timeout_seconds": 180,
      "distributed_executor_backend": "mp",
      "cuda_visible_devices": "1,3",
      "cuda_device_order": "PCI_BUS_ID",
      "vllm_use_v1": "1",
      "max_num_batched_tokens": 4096,
      "enable_chunked_prefill": true,
      "worker_directory": "/shared/wwx/EasyGAD/soft-win-rate/results/dipper_upkgwwarmup_upkgwgad_warmup_gamma0.5_delta3_new1_qwen2_5_.ee2082e3d13a593c/workers/20261031T002848_865774dd/plan_00",
      "gpu_inventory": [
        {
          "index": 1,
          "uuid": "GPU-aaaa1e22-8585-bcee-bf44-4dbbb57365ea",
          "name": "NVIDIA A100 80GB PCIe",
          "total_mib": 81920,
          "free_mib": 66411,
          "utilization": 0
        },
        {
          "index": 3,
          "uuid": "GPU-cf0eb97d-d714-dfe3-034e-f00037747988",
          "name": "NVIDIA A100-PCIE-40GB",
          "total_mib": 40960,
          "free_mib": 40428,
          "utilization": 0
        }
      ]
    }
  ],
  "input_generation": {
    "samples": 500,
    "empty_answers": 0,
    "mean_answer_characters": 788.112,
    "student_model_paths": [
      "/shared/wwx/EasyGAD/checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_new1_dipper2stage/warmup/global_step_1813/actor/huggingface"
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
  "rubric_sha256": "23b028957f3cb38f4dc24706108fd73156ba747fc37203dfc7d87e8ead8e61dd",
  "model_fingerprint": {
    "path": "/shared/public_models/Qwen3-32B",
    "assets": [
      {
        "name": "config.json",
        "sha256": "8034152c9180e4b08ca1f656efa7bf52e117766fc2a09c126db394a473f557a0"
      },
      {
        "name": "configuration.json",
        "sha256": "f888421726665e8a84b738eed42a64875aed79de8be7daade851ac8bf4c0cef9"
      },
      {
        "name": "generation_config.json",
        "sha256": "90373e8a092a7abb965d3fea4671ef129bb9f4ee5a3005f0ab8a95b9716812cb"
      },
      {
        "name": "merges.txt",
        "sha256": "b8e04af9c950e393054010dcef499c3f005e803e9b2da1a09b96a26c33266eb1"
      },
      {
        "name": "model.safetensors.index.json",
        "sha256": "68e066a65be872628751f5603243a94ddf9f923340e81d245944f66f5b6a03e1"
      },
      {
        "name": "tokenizer.json",
        "sha256": "aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4"
      },
      {
        "name": "tokenizer_config.json",
        "sha256": "c27ef18dae7dccaee951f6066f71a1b35ca9ec4ff3168b097dbda7905a036324"
      },
      {
        "name": "vocab.json",
        "sha256": "ca10d7e9fb3ed18575dd1e277a2579c16d108e32f27439684afa0e10b1440910"
      }
    ],
    "weight_stats": [
      {
        "name": "model-00001-of-00017.safetensors",
        "size": 3957109648,
        "mtime_ns": 1748403884759368838
      },
      {
        "name": "model-00002-of-00017.safetensors",
        "size": 3900791760,
        "mtime_ns": 1748403843500367073
      },
      {
        "name": "model-00003-of-00017.safetensors",
        "size": 3900791760,
        "mtime_ns": 1748403802698365327
      },
      {
        "name": "model-00004-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403764242363681
      },
      {
        "name": "model-00005-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403722468361894
      },
      {
        "name": "model-00006-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403681711360150
      },
      {
        "name": "model-00007-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403639311358336
      },
      {
        "name": "model-00008-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403582299355896
      },
      {
        "name": "model-00009-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403530985353700
      },
      {
        "name": "model-00010-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403477210351399
      },
      {
        "name": "model-00011-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403422707349067
      },
      {
        "name": "model-00012-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403367315346697
      },
      {
        "name": "model-00013-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403315147344465
      },
      {
        "name": "model-00014-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403263569342258
      },
      {
        "name": "model-00015-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403212487340072
      },
      {
        "name": "model-00016-of-00017.safetensors",
        "size": 3900791800,
        "mtime_ns": 1748403157024337699
      },
      {
        "name": "model-00017-of-00017.safetensors",
        "size": 3055341992,
        "mtime_ns": 1748403103933335427
      }
    ],
    "weight_contents_hashed": false,
    "software": {
      "python": "3.10.21",
      "torch": "2.6.0",
      "transformers": "4.51.3",
      "tokenizers": "0.21.4",
      "vllm": "0.8.5"
    }
  },
  "context_adjustment": null
}
```
