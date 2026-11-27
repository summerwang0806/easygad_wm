#!/usr/bin/env bash
set -euo pipefail
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_DIR}"

if [ -f "/app/wwx/miniconda3/etc/profile.d/conda.sh" ]; then
  # shellcheck disable=SC1091
  source "/app/wwx/miniconda3/etc/profile.d/conda.sh"
  conda activate wm
fi

echo "=== Waiting for running 'run_mw100.sh gpu1' to finish on GPU 1 ==="
while pgrep -f "run_mw100.sh gpu1" >/dev/null 2>&1; do
  sleep 5
done

echo "=== GPU 1 is free! Immediately taking GPU 1 for remaining 5 models ==="
REMAINING_MODELS=(
  "up_dipper_delta6_gad:/app/wwx/EasyGAD/checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta6_dipper2stage/gad/global_step_1813/actor/huggingface"
  "tp_delta3_warmup:/app/wwx/EasyGAD/checkpoints/tp_warmup_rules_g05_d3_s25_tp_tp_keeplast/warmup/global_step_1813/actor/huggingface"
  "tp_delta3_gad:/app/wwx/EasyGAD/checkpoints/tp_warmup_rules_g05_d3_s25_tp_tp_keeplast/gad/global_step_1813/actor/huggingface"
  "tp_delta6_warmup:/app/wwx/EasyGAD/checkpoints/tp_gad_rules_g5_d6_s4_te_old_st_Qwen2.5-0.5B/warmup/global_step_1813/actor/huggingface"
  "tp_delta6_gad:/app/wwx/EasyGAD/checkpoints/tp_gad_rules_g5_d6_s4_te_old_st_Qwen2.5-0.5B/gad/global_step_1813/actor/huggingface"
)

for item in "${REMAINING_MODELS[@]}"; do
  name="${item%%:*}"
  path="${item#*:}"
  echo "=== [GPU 1 Relay] Auditing ${name} ==="
  CUDA_VISIBLE_DEVICES=1 python wm_basin/09_audit_multi_window.py \
    --work-dir wm_basin_work \
    --windows-dir wm_basin_work/pools/audit_windows_100x450 \
    --suspects-subdir suspects_mw100 \
    --reuse-responses-from suspects_mw \
    --suspect-name "${name}" \
    --suspect-model "${path}" \
    --gpu-memory-utilization 0.35 \
    --batch-size 6 \
    --gen-chunk-windows 10
done

echo "=== All 14 models done! Summarizing & pushing mw100 results ==="
python wm_basin/07_summarize_results.py --work-dir wm_basin_work
git add wm_basin/results/
git commit -m "add 200-key 100x450 TPR@5% TPR@1% and AUROC results" || true
git push
echo "=== ALL 100x450 RELAY JOBS DONE ==="
