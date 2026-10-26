#!/usr/bin/env bash
# Warmup: original KGW discriminator positives + para student SFT.
# GAD: para teacher positives, starting from both warmup checkpoints.
set -euo pipefail

PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
cd -- "$PROJECT_ROOT"

usage() {
    cat <<'USAGE'
Usage:
  CUDA_VISIBLE_DEVICES=0,1 bash scripts/train/run_full_gad_kgwD_paraSFT_paraGAD_optimized.sh [options]

Defaults:
  --model /shared/public_models/Qwen2.5-0.5B
  --exp_name kgwD_paraSFT_paraGAD_gamma0.5_delta3
  --nnodes 1 --gpus_per_node 2 --warmup_epochs 1 --gad_epochs 1
  --logger swanlab             Same console + SwanLab logging as the base pipeline.

Data options (defaults are the requested gamma0.5_delta3 newtrain/newtest files):
  --original_train_file PATH   Original KGW discriminator positives for warmup.
  --para_train_file PATH       Student warmup SFT and GAD training data.
  --val_file PATH              Original KGW newtest, used only for validation.
  --merged_file PATH           Generated paired warmup Parquet; inputs stay intact.

Training options forwarded to run_full_gad_optimized.sh:
  --model PATH --reward_model PATH --exp_name NAME --nnodes N --gpus_per_node N
  --warmup_epochs N --gad_epochs N --save_freq N --test_freq N
  --train_batch_size N --lr FLOAT --work_dir PATH --gpu_memory_utilization FLOAT
  --ray_tmpdir PATH --ray_num_cpus N --constrained_2gpu --resume --skip_warmup
  --dry_run                    Prepare/validate CPU data and check configuration;
                               do not load models, start Ray or contact SwanLab.

Requires the companion Python changes and base launcher from the same checkout.
See GAD_SPLIT_WARMUP.md for git pull and run commands.
USAGE
}

fail() { printf 'Error: %s\n' "$*" >&2; exit 2; }
require_value() {
    [[ $# -ge 2 && -n "$2" && "$2" != --* ]] || fail "$1 requires a value"
}

ORIGINAL_TRAIN_FILE=data/dolly15k_qwen2_5_14b_kgw_gamma0.5_delta3_newtrain.parquet
PARA_TRAIN_FILE=data/dolly15k_qwen2_5_14b_kgw_gamma0.5_delta3_up_dipper_newtrain.parquet
VAL_FILE=data/dolly15k_qwen2_5_14b_kgw_gamma0.5_delta3_newtest.parquet
MERGED_FILE=data/dolly15k_qwen2_5_14b_kgw_gamma0.5_delta3_kgwD_paraSFT_newtrain.parquet
EXP_NAME=kgwD_paraSFT_paraGAD_gamma0.5_delta3
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
        --original_train_file) require_value "$@"; ORIGINAL_TRAIN_FILE="$2"; shift 2 ;;
        --para_train_file) require_value "$@"; PARA_TRAIN_FILE="$2"; shift 2 ;;
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

# Fail clearly if a checkout is missing the companion split-target changes.
for feature in \
    'verl/utils/dataset/rl_dataset.py:build_sft_response_tensors' \
    'verl/workers/actor/dp_actor.py:select_warmup_sft_targets' \
    'scripts/train/run_full_gad_optimized.sh:--warmup_train_file'; do
    file="${feature%%:*}"
    marker="${feature#*:}"
    grep -q -- "$marker" "$file" || fail "Update the companion file in this checkout: $file"
done

printf 'Warmup discriminator: %s\nWarmup student SFT: %s\nGAD training: %s\nValidation: %s\n' \
    "$ORIGINAL_TRAIN_FILE" "$PARA_TRAIN_FILE" "$PARA_TRAIN_FILE" "$VAL_FILE"
python3 tools/prepare_split_warmup_data.py \
    --original_train_file "$ORIGINAL_TRAIN_FILE" \
    --para_train_file "$PARA_TRAIN_FILE" \
    --val_file "$VAL_FILE" \
    --output_file "$MERGED_FILE"

exec bash scripts/train/run_full_gad_optimized.sh \
    "${FORWARDED[@]}" \
    --exp_name "$EXP_NAME" --nnodes "$NNODES" --gpus_per_node "$GPUS_PER_NODE" \
    --logger "$LOGGER" \
    --warmup_train_file "$MERGED_FILE" \
    --gad_train_file "$PARA_TRAIN_FILE" \
    --val_file "$VAL_FILE"
