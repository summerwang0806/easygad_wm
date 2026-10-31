#!/usr/bin/env bash
# Warmup: clean discriminator positives + KGW student SFT.
# GAD: KGW teacher positives, inheriting both warmup checkpoints.
set -euo pipefail

PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
cd -- "$PROJECT_ROOT"

usage() {
    cat <<'USAGE'
Usage:
  CUDA_VISIBLE_DEVICES=0,1 bash scripts/train/run_full_gad_cleanD_kgwSFT_kgwGAD_optimized.sh [options]

Defaults (training settings inherited from run_full_gad_optimized.sh):
  --model /shared/public_models/Qwen2.5-0.5B
  --exp_name cleanD_kgwSFT_kgwGAD_gamma0.5_delta3
  --nnodes 1 --gpus_per_node 2 --warmup_epochs 1 --gad_epochs 1
  --logger swanlab             Console + SwanLab; both stages show training progress.

Data options:
  --clean_train_file PATH      Warmup discriminator positives: specified clean_train.
  --kgw_train_file PATH        Student warmup SFT and GAD: gamma0.5_delta3_newtrain.
  --val_file PATH              Original KGW gamma0.5_delta3_newtest.
  --merged_file PATH           Generated paired warmup Parquet; inputs stay intact.

Training options forwarded to run_full_gad_optimized.sh:
  --model PATH --reward_model PATH --exp_name NAME --nnodes N --gpus_per_node N
  --warmup_epochs N --gad_epochs N --save_freq N --test_freq N
  --train_batch_size N --lr FLOAT --work_dir PATH --gpu_memory_utilization FLOAT
  --ray_tmpdir PATH --ray_num_cpus N --constrained_2gpu --resume --skip_warmup
  --dry_run                    Prepare/validate CPU data and check configuration;
                               do not load models, start Ray or contact SwanLab.

Requires the split-target Python changes and base launcher from the same checkout.
See GAD_CLEAN_D_KGW_SFT.md for data verification and run commands.
USAGE
}

fail() { printf 'Error: %s\n' "$*" >&2; exit 2; }
require_value() {
    [[ $# -ge 2 && -n "$2" && "$2" != --* ]] || fail "$1 requires a value"
}

CLEAN_TRAIN_FILE=data/dolly15k_qwen2_5_14b_clean_train.parquet
KGW_TRAIN_FILE=data/dolly15k_qwen2_5_14b_kgw_gamma0.5_delta3_newtrain.parquet
VAL_FILE=data/dolly15k_qwen2_5_14b_kgw_gamma0.5_delta3_newtest.parquet
MERGED_FILE=data/dolly15k_qwen2_5_14b_cleanD_kgwSFT_gamma0.5_delta3_newtrain.parquet
EXP_NAME=cleanD_kgwSFT_kgwGAD_gamma0.5_delta3
NNODES=1
GPUS_PER_NODE=2
LOGGER=swanlab
FORWARDED=()
declare -A SEEN=()

while [[ $# -gt 0 ]]; do
    OPTION="$1"
    [[ -z "${SEEN[$OPTION]+present}" ]] || fail "Duplicate option: $OPTION"
    SEEN["$OPTION"]=1
    case "$OPTION" in
        --help|-h) usage; exit 0 ;;
        --clean_train_file) require_value "$@"; CLEAN_TRAIN_FILE="$2"; shift 2 ;;
        --kgw_train_file) require_value "$@"; KGW_TRAIN_FILE="$2"; shift 2 ;;
        --val_file) require_value "$@"; VAL_FILE="$2"; shift 2 ;;
        --merged_file) require_value "$@"; MERGED_FILE="$2"; shift 2 ;;
        --exp_name) require_value "$@"; EXP_NAME="$2"; shift 2 ;;
        --nnodes) require_value "$@"; NNODES="$2"; shift 2 ;;
        --gpus_per_node) require_value "$@"; GPUS_PER_NODE="$2"; shift 2 ;;
        --logger) require_value "$@"; LOGGER="$2"; shift 2 ;;
        --model|--reward_model|--warmup_epochs|--gad_epochs|--save_freq|--test_freq|--train_batch_size|--lr|--work_dir|--gpu_memory_utilization|--ray_tmpdir|--ray_num_cpus)
            require_value "$@"; FORWARDED+=("$1" "$2"); shift 2 ;;
        --dry_run|--resume|--skip_warmup|--constrained_2gpu)
            FORWARDED+=("$1"); shift ;;
        *) fail "Unknown option: $OPTION (see --help)" ;;
    esac
done

[[ "$EXP_NAME" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]] || fail "--exp_name must contain only letters, digits, dot, underscore or hyphen"
[[ "$NNODES" =~ ^[1-9][0-9]*$ ]] || fail "--nnodes must be a positive integer"
[[ "$GPUS_PER_NODE" == 1 || "$GPUS_PER_NODE" == 2 ]] || fail "--gpus_per_node must be 1 or 2"
[[ "$LOGGER" == console || "$LOGGER" == swanlab ]] || fail "--logger must be console or swanlab"
[[ -n "${CUDA_VISIBLE_DEVICES:-}" ]] || fail "Set CUDA_VISIBLE_DEVICES explicitly, e.g. CUDA_VISIBLE_DEVICES=0,1"

for feature in \
    'verl/utils/dataset/rl_dataset.py:build_sft_response_tensors' \
    'verl/workers/actor/dp_actor.py:select_warmup_sft_targets' \
    'scripts/train/run_full_gad_optimized.sh:--warmup_train_file' \
    'tools/prepare_split_warmup_data.py:--discriminator_train_file'; do
    file="${feature%%:*}"
    marker="${feature#*:}"
    grep -q -- "$marker" "$file" || fail "Update the companion file in this checkout: $file"
done

printf 'Warmup discriminator (clean): %s\nWarmup student SFT (KGW): %s\nGAD training (KGW): %s\nValidation: %s\n' \
    "$CLEAN_TRAIN_FILE" "$KGW_TRAIN_FILE" "$KGW_TRAIN_FILE" "$VAL_FILE"
python3 tools/prepare_split_warmup_data.py \
    --discriminator_train_file "$CLEAN_TRAIN_FILE" \
    --sft_train_file "$KGW_TRAIN_FILE" \
    --val_file "$VAL_FILE" \
    --output_file "$MERGED_FILE"

exec bash scripts/train/run_full_gad_optimized.sh \
    "${FORWARDED[@]}" \
    --exp_name "$EXP_NAME" --nnodes "$NNODES" --gpus_per_node "$GPUS_PER_NODE" \
    --logger "$LOGGER" \
    --warmup_train_file "$MERGED_FILE" \
    --gad_train_file "$KGW_TRAIN_FILE" \
    --val_file "$VAL_FILE"
