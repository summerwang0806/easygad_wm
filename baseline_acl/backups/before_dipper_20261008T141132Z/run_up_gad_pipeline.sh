#!/usr/bin/env bash
# Shared, CPU-preflighted entrypoint for the two UP training branches.
set -euo pipefail

PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
BASE_PIPELINE="${PROJECT_ROOT}/scripts/train/run_full_gad_all_clean_optimized.sh"
VALIDATOR="${PROJECT_ROOT}/baseline_acl/validate_up_data.py"

usage() {
    cat <<'USAGE'
Usage:
  bash scripts/train/run_full_gad_up_up_optimized.sh [options]
  bash scripts/train/run_full_gad_up_kgw_optimized.sh [options]

Branches (both Warmup 1 epoch + GAD 1 epoch):
  up_up   Warmup uses UP teacher responses; GAD uses UP teacher responses.
  up_kgw  Warmup uses UP teacher responses; GAD uses original KGW responses.
Both stages evaluate on the unchanged original KGW test file.

Data options (relative paths are resolved from the EasyGAD project root):
  --up_train_file PATH   Default: data/dolly15k_qwen2_5_14b_kgw_up_train.parquet
  --kgw_train_file PATH  Default: data/dolly15k_qwen2_5_14b_kgw_train.parquet
  --val_file PATH        Default: data/dolly15k_qwen2_5_14b_kgw_test.parquet

Options forwarded to the existing optimized full pipeline:
  --model PATH                 --reward_model PATH
  --exp_name NAME              --nnodes N                 --gpus_per_node 1|2
  --save_freq N                --test_freq N              --train_batch_size N
  --lr RATE                    --gpu_memory_utilization FRACTION
  --work_dir PATH              --constrained_2gpu         --dry_run
  --warmup_epochs 1            --gad_epochs 1
  -h, --help

The experiment name defaults to kgw_up_up_1ep / kgw_up_kgw_1ep; nnodes defaults
to 1. Model, reward model and all other training settings inherit the existing
run_full_gad_all_clean_optimized.sh defaults. Its work-directory collision
checks and actor/critic checkpoint merging remain authoritative.

CUDA_VISIBLE_DEVICES defaults to 1,3. For one GPU, set it to one available GPU
and pass --gpus_per_node 1. The underlying pipeline checks the visible GPU count.
--dry_run still validates data on CPU, but requires no GPU or SwanLab access.
Stage file overrides are reserved; use the three data options above instead.
USAGE
}

fail() { printf 'Error: %s\n' "$*" >&2; exit 2; }

require_value() {
    [[ $# -ge 2 && -n "$2" && "$2" != --* ]] || fail "$1 requires a value."
}

BRANCH=""
UP_TRAIN_FILE="data/dolly15k_qwen2_5_14b_kgw_up_train.parquet"
KGW_TRAIN_FILE="data/dolly15k_qwen2_5_14b_kgw_train.parquet"
VAL_FILE="data/dolly15k_qwen2_5_14b_kgw_test.parquet"
EXP_NAME=""
NNODES=1
GPUS_PER_NODE=2
CONSTRAINED_2GPU=false
FORWARDED=()
declare -A SEEN=()

while [[ $# -gt 0 ]]; do
    OPTION="$1"
    case "$OPTION" in
        -h|--help) usage; exit 0 ;;
        --warmup_train_file|--gad_train_file|--warmup_val_file|--gad_val_file)
            fail "$OPTION is fixed by the branch; use --up_train_file, --kgw_train_file and --val_file."
            ;;
        --branch|--up_train_file|--kgw_train_file|--val_file|--exp_name|--nnodes|--gpus_per_node|--warmup_epochs|--gad_epochs|--model|--reward_model|--save_freq|--test_freq|--train_batch_size|--lr|--gpu_memory_utilization|--work_dir|--constrained_2gpu|--dry_run)
            ;;
        *)
            fail "Unknown option: $OPTION (see --help)."
            ;;
    esac
    [[ -z "${SEEN[$OPTION]+present}" ]] || fail "Duplicate option: $OPTION"
    SEEN["$OPTION"]=1
    case "$OPTION" in
        --branch)
            require_value "$@"; BRANCH="$2"; shift 2 ;;
        --up_train_file)
            require_value "$@"; UP_TRAIN_FILE="$2"; shift 2 ;;
        --kgw_train_file)
            require_value "$@"; KGW_TRAIN_FILE="$2"; shift 2 ;;
        --val_file)
            require_value "$@"; VAL_FILE="$2"; shift 2 ;;
        --exp_name)
            require_value "$@"; EXP_NAME="$2"; shift 2 ;;
        --nnodes)
            require_value "$@"; NNODES="$2"; shift 2 ;;
        --gpus_per_node)
            require_value "$@"; GPUS_PER_NODE="$2"; shift 2 ;;
        --warmup_epochs|--gad_epochs)
            require_value "$@"
            [[ "$2" == 1 ]] || fail "$OPTION is pinned to 1 for this experiment."
            shift 2
            ;;
        --model|--reward_model|--save_freq|--test_freq|--train_batch_size|--lr|--gpu_memory_utilization|--work_dir)
            require_value "$@"; FORWARDED+=("$1" "$2"); shift 2 ;;
        --constrained_2gpu)
            CONSTRAINED_2GPU=true; FORWARDED+=("$1"); shift ;;
        --dry_run)
            FORWARDED+=("$1"); shift ;;
        *)
            fail "Unknown option: $OPTION (see --help)."
            ;;
    esac
done

case "$BRANCH" in
    up_up)  GAD_TRAIN_FILE="$UP_TRAIN_FILE"; EXP_NAME="${EXP_NAME:-kgw_up_up_1ep}" ;;
    up_kgw) GAD_TRAIN_FILE="$KGW_TRAIN_FILE"; EXP_NAME="${EXP_NAME:-kgw_up_kgw_1ep}" ;;
    *) fail "Use a branch entrypoint, or pass --branch up_up|up_kgw." ;;
esac
[[ "$EXP_NAME" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]] || fail "--exp_name must be a name containing only letters, digits, dot, underscore or hyphen."
[[ "$NNODES" =~ ^[1-9][0-9]*$ ]] || fail "--nnodes must be a positive integer."
[[ "$GPUS_PER_NODE" == 1 || "$GPUS_PER_NODE" == 2 ]] || fail "--gpus_per_node must be 1 or 2."
[[ "$CONSTRAINED_2GPU" == false || "$GPUS_PER_NODE" == 2 ]] || fail "--constrained_2gpu requires --gpus_per_node 2."
[[ -f "$BASE_PIPELINE" ]] || fail "Required existing pipeline is missing: $BASE_PIPELINE. Deploy these wrappers into the EasyGAD checkout that already contains it."
[[ -f "$VALIDATOR" ]] || fail "CPU data validator is missing: $VALIDATOR"

cd -- "$PROJECT_ROOT"
export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-1,3}"

printf 'UP branch: %s (Warmup 1 epoch + GAD 1 epoch)\n' "$BRANCH"
printf 'Warmup training: %s\nGAD training: %s\nValidation (both stages): %s\n' "$UP_TRAIN_FILE" "$GAD_TRAIN_FILE" "$VAL_FILE"
printf 'CPU preflight source: %s\nExperiment: %s\n' "$KGW_TRAIN_FILE" "$EXP_NAME"
printf '%s\n' 'The parent script name and CLEAN log labels are historical; the explicit stage-file arguments below determine the data used.'

python3 "$VALIDATOR" \
    --original_train_file "$KGW_TRAIN_FILE" \
    --up_train_file "$UP_TRAIN_FILE" \
    --val_file "$VAL_FILE"

exec bash "$BASE_PIPELINE" \
    "${FORWARDED[@]}" \
    --exp_name "$EXP_NAME" \
    --nnodes "$NNODES" \
    --gpus_per_node "$GPUS_PER_NODE" \
    --warmup_epochs 1 \
    --gad_epochs 1 \
    --warmup_train_file "$UP_TRAIN_FILE" \
    --gad_train_file "$GAD_TRAIN_FILE" \
    --warmup_val_file "$VAL_FILE" \
    --gad_val_file "$VAL_FILE"
