#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-all}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_DIR}"

if [ -f "/app/wwx/miniconda3/etc/profile.d/conda.sh" ]; then
  # shellcheck disable=SC1091
  source "/app/wwx/miniconda3/etc/profile.d/conda.sh"
  conda activate wm
fi

GPU1_MODELS=(
  "base_qwen25_05b:/app/public_models/Qwen2.5-0.5B"
  "clean_gad_control:/app/wwx/EasyGAD/checkpoints/gad_05b_cleanwarmup_cleangad_control/gad/global_step_1813/actor/huggingface"
  "kgw_delta3_warmup:/app/wwx/EasyGAD/checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_new/warmup/global_step_1813/actor/huggingface"
  "kgw_delta3_gad:/app/wwx/EasyGAD/checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_new/gad/global_step_1813/actor/huggingface"
  "kgw_delta6_warmup:/app/wwx/EasyGAD/checkpoints/kgwwarmup_kgwgad_gamma0.5_delta6/warmup/global_step_1813/actor/huggingface"
  "kgw_delta6_gad:/app/wwx/EasyGAD/checkpoints/kgwwarmup_kgwgad_gamma0.5_delta6/gad/global_step_1813/actor/huggingface"
  "up_dipper_delta6_warmup:/app/wwx/EasyGAD/checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta6_dipper2stage/warmup/global_step_1813/actor/huggingface"
)

GPU2_MODELS=(
  "up_dipper_delta3_warmup:/app/wwx/EasyGAD/checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_new1_dipper2stage/warmup/global_step_1813/actor/huggingface"
  "up_dipper_delta3_gad:/app/wwx/EasyGAD/checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta3_new1_dipper2stage/gad/global_step_1813/actor/huggingface"
  "up_dipper_delta6_gad:/app/wwx/EasyGAD/checkpoints/te_old_st_Qwen2.5-0.5B_gamma0.5_delta6_dipper2stage/gad/global_step_1813/actor/huggingface"
  "tp_delta3_warmup:/app/wwx/EasyGAD/checkpoints/tp_warmup_rules_g05_d3_s25_tp_tp_keeplast/warmup/global_step_1813/actor/huggingface"
  "tp_delta3_gad:/app/wwx/EasyGAD/checkpoints/tp_warmup_rules_g05_d3_s25_tp_tp_keeplast/gad/global_step_1813/actor/huggingface"
  "tp_delta6_warmup:/app/wwx/EasyGAD/checkpoints/tp_gad_rules_g5_d6_s4_te_old_st_Qwen2.5-0.5B/warmup/global_step_1813/actor/huggingface"
  "tp_delta6_gad:/app/wwx/EasyGAD/checkpoints/tp_gad_rules_g5_d6_s4_te_old_st_Qwen2.5-0.5B/gad/global_step_1813/actor/huggingface"
)

run_prep() {
  echo "=== [Step 1] Building 100 x 450 disjoint Alpaca audit windows ==="
  python wm_basin/08_prepare_audit_windows.py \
    --work-dir wm_basin_work \
    --windows-dir wm_basin_work/pools/audit_windows_100x450 \
    --num-windows 100 \
    --prompts-per-window 450
}

run_list() {
  local gpu_id="$1"
  local gpu_util="$2"
  shift 2
  local items=("$@")
  for item in "${items[@]}"; do
    local name="${item%%:*}"
    local path="${item#*:}"
    echo "=== [GPU ${gpu_id}] Auditing ${name} ==="
    CUDA_VISIBLE_DEVICES="${gpu_id}" python wm_basin/09_audit_multi_window.py \
      --work-dir wm_basin_work \
      --windows-dir wm_basin_work/pools/audit_windows_100x450 \
      --suspects-subdir suspects_mw100 \
      --reuse-responses-from suspects_mw \
      --suspect-name "${name}" \
      --suspect-model "${path}" \
      --gpu-memory-utilization "${gpu_util}" \
      --batch-size 16 \
      --gen-chunk-windows 10
  done
}

run_finish() {
  echo "=== [Step 3] Summarizing & pushing mw100 results ==="
  python wm_basin/07_summarize_results.py --work-dir wm_basin_work
  git add wm_basin/results/
  git commit -m "add 200-key 100x450 TPR@5% TPR@1% and AUROC results" || true
  git push
  echo "=== ALL 100x450 JOBS DONE ==="
}

case "${MODE}" in
  prep)
    run_prep
    ;;
  gpu1)
    run_prep
    run_list 1 0.35 "${GPU1_MODELS[@]}"
    ;;
  gpu2)
    run_prep
    run_list 2 0.70 "${GPU2_MODELS[@]}"
    ;;
  finish)
    run_finish
    ;;
  all)
    run_prep
    run_list 1 0.35 "${GPU1_MODELS[@]}" > wm_basin_work/log_mw100_gpu1.txt 2>&1 &
    PID1=$!
    run_list 2 0.70 "${GPU2_MODELS[@]}" > wm_basin_work/log_mw100_gpu2.txt 2>&1 &
    PID2=$!
    wait "${PID1}" "${PID2}"
    run_finish
    ;;
  *)
    echo "Usage: bash wm_basin/run_mw100.sh [prep|gpu1|gpu2|finish|all]"
    exit 1
    ;;
esac
