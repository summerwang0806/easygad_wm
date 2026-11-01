
## 评测记录：2026-11-01T15:39:39+08:00（20261101T073939Z_504ffae6）

- 待测 JSONL：`/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl`；SHA256 `dd4cfdbe540e2227bbad3b46f6a64e34bb1a46b7e7d24860ef8be90ec03efd48`
- 固定 clean 教师参照（Parquet）：`/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_clean_test.parquet`；SHA256 `72baa80098525f22402cbaf3a97659bf41534008724f98981b16a04cccc222ef`
- 本地裁判：`/shared/public_models/Qwen3-32B`；协议 `local-fixed-reference-half-tie-preferences-v1`
- 只评已保存完整回答，不生成学生或参照回答，不调用外部 API。

| Soft Win Rate ↑（平局半分） | 95% CI | 有效/计划题目 | 单轮胜/平/负 | 双顺序一致率 | 本次复用/新增判断 |
|---:|---|---:|---|---:|---:|
| 7.40% | [5.75%, 9.20%] | 500/500 | 4.30% / 6.20% / 89.50% | 90.80% | 0/1000 |

每题匿名交换 A/B 顺序两次。每轮映射胜=1、平=0.5、负=0，先取同题两轮均值，再对完整题目算术平均。这不是 PostMark 将平局算全胜的 Soft Win Rate；本报告明确采用半分。
单轮胜/平/负只统计双顺序均成功题目的 2N 次判定。交换顺序导致的相反选择不伪装成真实平局，另报顺序一致率。解析失败、拒答、超长及截断输出不计平；缺少任一顺序的题目不进入主指标。
CI 按题目成对 bootstrap，不覆盖裁判偏差或训练种子变异。50% 是相对固定参照的偏好平衡，不是正确率。
覆盖率 100.00%；本次完整评测：True；缓存：`/shared/wwx/EasyGAD/soft-win-rate/results/teacher/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.5ba8bbbf7c215e15/judgments.jsonl`；本次归档：`/shared/wwx/EasyGAD/soft-win-rate/results/teacher/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.5ba8bbbf7c215e15/runs/20261101T073939Z_504ffae6.json`。

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
      "worker_directory": "/shared/wwx/EasyGAD/soft-win-rate/results/teacher/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.5ba8bbbf7c215e15/workers/20261101T151216_66a90f8e/plan_00",
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
  "reference_generation": {
    "samples": 500,
    "empty_answers": 0,
    "mean_answer_characters": 1056.632,
    "student_model_paths": [],
    "generation_configurations": [
      {
        "configuration": {},
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

## 评测记录：2026-11-01T16:08:46+08:00（20261101T080846Z_68aa4d9b）

- 待测 JSONL：`/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.jsonl`；SHA256 `618df1162dbd1bbf770b90baabfd23226ef52fd3028f5fdb6490919cca78b92e`
- 固定 clean 教师参照（Parquet）：`/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_clean_test.parquet`；SHA256 `72baa80098525f22402cbaf3a97659bf41534008724f98981b16a04cccc222ef`
- 本地裁判：`/shared/public_models/Qwen3-32B`；协议 `local-fixed-reference-half-tie-preferences-v1`
- 只评已保存完整回答，不生成学生或参照回答，不调用外部 API。

| Soft Win Rate ↑（平局半分） | 95% CI | 有效/计划题目 | 单轮胜/平/负 | 双顺序一致率 | 本次复用/新增判断 |
|---:|---|---:|---|---:|---:|
| 7.50% | [5.85%, 9.35%] | 500/500 | 4.30% / 6.40% / 89.30% | 91.40% | 0/1000 |

每题匿名交换 A/B 顺序两次。每轮映射胜=1、平=0.5、负=0，先取同题两轮均值，再对完整题目算术平均。这不是 PostMark 将平局算全胜的 Soft Win Rate；本报告明确采用半分。
单轮胜/平/负只统计双顺序均成功题目的 2N 次判定。交换顺序导致的相反选择不伪装成真实平局，另报顺序一致率。解析失败、拒答、超长及截断输出不计平；缺少任一顺序的题目不进入主指标。
CI 按题目成对 bootstrap，不覆盖裁判偏差或训练种子变异。50% 是相对固定参照的偏好平衡，不是正确率。
覆盖率 100.00%；本次完整评测：True；缓存：`/shared/wwx/EasyGAD/soft-win-rate/results/teacher/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_t.73cd95e570cacc53/judgments.jsonl`；本次归档：`/shared/wwx/EasyGAD/soft-win-rate/results/teacher/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_t.73cd95e570cacc53/runs/20261101T080846Z_68aa4d9b.json`。

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
      "worker_directory": "/shared/wwx/EasyGAD/soft-win-rate/results/teacher/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_t.73cd95e570cacc53/workers/20261101T154025_ab4c62a5/plan_00",
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
    "mean_answer_characters": 1056.632,
    "student_model_paths": [],
    "generation_configurations": [
      {
        "configuration": {},
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

## 评测记录：2026-11-01T16:39:02+08:00（20261101T083902Z_5bd1c8d3）

- 待测 JSONL：`/shared/wwx/EasyGAD/wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl`；SHA256 `dd4cfdbe540e2227bbad3b46f6a64e34bb1a46b7e7d24860ef8be90ec03efd48`
- 固定 clean 教师参照（Parquet）：`/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_kgw_gamma0.5_delta3_newtest.parquet`；SHA256 `1898c482896665b7f21b04987b8687b1975ea004fdf7cd3b77f2f4539751406f`
- 本地裁判：`/shared/public_models/Qwen3-32B`；协议 `local-fixed-reference-half-tie-preferences-v1`
- 只评已保存完整回答，不生成学生或参照回答，不调用外部 API。

| Soft Win Rate ↑（平局半分） | 95% CI | 有效/计划题目 | 单轮胜/平/负 | 双顺序一致率 | 本次复用/新增判断 |
|---:|---|---:|---|---:|---:|
| 7.85% | [6.10%, 9.70%] | 500/500 | 4.80% / 6.10% / 89.10% | 91.00% | 0/1000 |

每题匿名交换 A/B 顺序两次。每轮映射胜=1、平=0.5、负=0，先取同题两轮均值，再对完整题目算术平均。这不是 PostMark 将平局算全胜的 Soft Win Rate；本报告明确采用半分。
单轮胜/平/负只统计双顺序均成功题目的 2N 次判定。交换顺序导致的相反选择不伪装成真实平局，另报顺序一致率。解析失败、拒答、超长及截断输出不计平；缺少任一顺序的题目不进入主指标。
CI 按题目成对 bootstrap，不覆盖裁判偏差或训练种子变异。50% 是相对固定参照的偏好平衡，不是正确率。
覆盖率 100.00%；本次完整评测：True；缓存：`/shared/wwx/EasyGAD/soft-win-rate/results/teacher/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.890d85bc8fb5f085/judgments.jsonl`；本次归档：`/shared/wwx/EasyGAD/soft-win-rate/results/teacher/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.890d85bc8fb5f085/runs/20261101T083902Z_5bd1c8d3.json`。

自动窗口调整：8192 → 16384 token；已发现的输入及输出预留至少需要 9144 token。保留完整文本，实际并发与 GPU 见执行配置。

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
      "worker_directory": "/shared/wwx/EasyGAD/soft-win-rate/results/teacher/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.890d85bc8fb5f085/workers/20261101T161052_09d1debe/plan_00",
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
  "reference_generation": {
    "samples": 500,
    "empty_answers": 0,
    "mean_answer_characters": 1113.068,
    "student_model_paths": [],
    "generation_configurations": [
      {
        "configuration": {},
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
    "base_protocol_sha256": "0a0111563e99e1f50dd32e234dd19597a5711c05c17ab7b14b737777e6118a04",
    "base_window": 8192,
    "required_model_len": 9144,
    "max_model_len": 16384,
    "selected_at": "2026-11-01T16:10:52+08:00"
  }
}
```

## 评测记录：2026-11-01T17:10:45+08:00（20261101T091045Z_05b974c4）

- 待测 JSONL：`/shared/wwx/EasyGAD/wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.jsonl`；SHA256 `618df1162dbd1bbf770b90baabfd23226ef52fd3028f5fdb6490919cca78b92e`
- 固定 clean 教师参照（Parquet）：`/shared/wwx/EasyGAD/data/dolly15k_qwen2_5_14b_kgw_gamma0.5_delta3_newtest.parquet`；SHA256 `1898c482896665b7f21b04987b8687b1975ea004fdf7cd3b77f2f4539751406f`
- 本地裁判：`/shared/public_models/Qwen3-32B`；协议 `local-fixed-reference-half-tie-preferences-v1`
- 只评已保存完整回答，不生成学生或参照回答，不调用外部 API。

| Soft Win Rate ↑（平局半分） | 95% CI | 有效/计划题目 | 单轮胜/平/负 | 双顺序一致率 | 本次复用/新增判断 |
|---:|---|---:|---|---:|---:|
| 8.25% | [6.45%, 10.20%] | 500/500 | 5.30% / 5.90% / 88.80% | 90.60% | 0/1000 |

每题匿名交换 A/B 顺序两次。每轮映射胜=1、平=0.5、负=0，先取同题两轮均值，再对完整题目算术平均。这不是 PostMark 将平局算全胜的 Soft Win Rate；本报告明确采用半分。
单轮胜/平/负只统计双顺序均成功题目的 2N 次判定。交换顺序导致的相反选择不伪装成真实平局，另报顺序一致率。解析失败、拒答、超长及截断输出不计平；缺少任一顺序的题目不进入主指标。
CI 按题目成对 bootstrap，不覆盖裁判偏差或训练种子变异。50% 是相对固定参照的偏好平衡，不是正确率。
覆盖率 100.00%；本次完整评测：True；缓存：`/shared/wwx/EasyGAD/soft-win-rate/results/teacher/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_t.9028fe9f58f0de9c/judgments.jsonl`；本次归档：`/shared/wwx/EasyGAD/soft-win-rate/results/teacher/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_t.9028fe9f58f0de9c/runs/20261101T091045Z_05b974c4.json`。

自动窗口调整：8192 → 16384 token；已发现的输入及输出预留至少需要 9135 token。保留完整文本，实际并发与 GPU 见执行配置。

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
      "worker_directory": "/shared/wwx/EasyGAD/soft-win-rate/results/teacher/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_t.9028fe9f58f0de9c/workers/20261101T164131_c0a3bca7/plan_00",
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
    "mean_answer_characters": 1113.068,
    "student_model_paths": [],
    "generation_configurations": [
      {
        "configuration": {},
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
    "base_protocol_sha256": "77db43b6fb32d2bcbc737e1ede66962474c7620e21d313504f1027efa0bf6650",
    "base_window": 8192,
    "required_model_len": 9135,
    "max_model_len": 16384,
    "selected_at": "2026-11-01T16:41:31+08:00"
  }
}
```
