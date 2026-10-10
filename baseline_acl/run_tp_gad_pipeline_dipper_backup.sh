#!/usr/bin/env bash
# Backup Dipper projection TP: retained independently from formal student TP.
set -euo pipefail

PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
BASE_PIPELINE="${PROJECT_ROOT}/scripts/train/run_full_gad_all_clean_optimized.sh"
VALIDATOR="${PROJECT_ROOT}/baseline_acl/validate_up_data.py"

usage() {
    cat <<'USAGE'
Usage:
  bash scripts/train/run_full_gad_tp_tp_dipper_backup_optimized.sh [options]
  bash scripts/train/run_full_gad_tp_kgw_dipper_backup_optimized.sh [options]

Backup only: Dipper text projection is a project approximation.
Branches (both Warmup 1 epoch + GAD 1 epoch):
  tp_tp   Warmup and GAD use targeted Dipper paraphrasing (TP) responses.
  tp_kgw  Warmup uses TP responses; GAD uses original KGW responses.
Both stages evaluate on the original KGW test file.

Data options (relative paths are resolved from the EasyGAD project root):
  --tp_train_file PATH   Default: data/dolly15k_qwen2_5_14b_kgw_tp_dipper_backup_train.parquet
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

Experiment names default to kgw_tp_dipper_backup_tp_1ep / kgw_tp_dipper_backup_kgw_1ep.
nnodes defaults to 1; gpus_per_node defaults to 2. Model, reward model and
other training settings inherit run_full_gad_all_clean_optimized.sh defaults.
Stage file overrides are reserved; use the three data options above instead.

Preflight requires pyarrow and a complete TP audit at <tp_train_file>.audit.json.
The audit must identify targeted_dipper_paraphrasing and match both data hashes.
The historical UP validator is reused because its schema/row checks also apply to TP.

Set CUDA_VISIBLE_DEVICES explicitly when training; this wrapper selects no GPU.
--dry_run validates the data and audit on CPU, then prints the parent command.
It does not run the parent script or check/load models, contact SwanLab, or start training.
USAGE
}

fail() { printf 'Error: %s\n' "$*" >&2; exit 2; }
require_value() {
    [[ $# -ge 2 && -n "$2" && "$2" != --* ]] || fail "$1 requires a value."
}

BRANCH=""
TP_TRAIN_FILE="data/dolly15k_qwen2_5_14b_kgw_tp_dipper_backup_train.parquet"
KGW_TRAIN_FILE="data/dolly15k_qwen2_5_14b_kgw_train.parquet"
VAL_FILE="data/dolly15k_qwen2_5_14b_kgw_test.parquet"
EXP_NAME=""
NNODES=1
GPUS_PER_NODE=2
CONSTRAINED_2GPU=false
DRY_RUN=false
FORWARDED=()
declare -A SEEN=()

while [[ $# -gt 0 ]]; do
    OPTION="$1"
    case "$OPTION" in
        -h|--help) usage; exit 0 ;;
        --warmup_train_file|--gad_train_file|--warmup_val_file|--gad_val_file)
            fail "$OPTION is fixed by the branch; use --tp_train_file, --kgw_train_file and --val_file."
            ;;
        --branch|--tp_train_file|--kgw_train_file|--val_file|--exp_name|--nnodes|--gpus_per_node|--warmup_epochs|--gad_epochs|--model|--reward_model|--save_freq|--test_freq|--train_batch_size|--lr|--gpu_memory_utilization|--work_dir|--constrained_2gpu|--dry_run) ;;
        *) fail "Unknown option: $OPTION (see --help)." ;;
    esac
    [[ -z "${SEEN[$OPTION]+present}" ]] || fail "Duplicate option: $OPTION"
    SEEN["$OPTION"]=1
    case "$OPTION" in
        --branch) require_value "$@"; BRANCH="$2"; shift 2 ;;
        --tp_train_file) require_value "$@"; TP_TRAIN_FILE="$2"; shift 2 ;;
        --kgw_train_file) require_value "$@"; KGW_TRAIN_FILE="$2"; shift 2 ;;
        --val_file) require_value "$@"; VAL_FILE="$2"; shift 2 ;;
        --exp_name) require_value "$@"; EXP_NAME="$2"; shift 2 ;;
        --nnodes) require_value "$@"; NNODES="$2"; shift 2 ;;
        --gpus_per_node) require_value "$@"; GPUS_PER_NODE="$2"; shift 2 ;;
        --warmup_epochs|--gad_epochs)
            require_value "$@"
            [[ "$2" == 1 ]] || fail "$OPTION is pinned to 1 for this experiment."
            shift 2 ;;
        --model|--reward_model|--save_freq|--test_freq|--train_batch_size|--lr|--gpu_memory_utilization|--work_dir)
            require_value "$@"; FORWARDED+=("$1" "$2"); shift 2 ;;
        --constrained_2gpu) CONSTRAINED_2GPU=true; FORWARDED+=("$1"); shift ;;
        --dry_run) DRY_RUN=true; FORWARDED+=("$1"); shift ;;
    esac
done

case "$BRANCH" in
    tp_tp)  GAD_TRAIN_FILE="$TP_TRAIN_FILE"; EXP_NAME="${EXP_NAME:-kgw_tp_dipper_backup_tp_1ep}" ;;
    tp_kgw) GAD_TRAIN_FILE="$KGW_TRAIN_FILE"; EXP_NAME="${EXP_NAME:-kgw_tp_dipper_backup_kgw_1ep}" ;;
    *) fail "Use a branch entrypoint, or pass --branch tp_tp|tp_kgw." ;;
esac
[[ "$EXP_NAME" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]] || fail "--exp_name must contain only letters, digits, dot, underscore or hyphen and start with a letter or digit."
[[ "$NNODES" =~ ^[1-9][0-9]*$ ]] || fail "--nnodes must be a positive integer."
[[ "$GPUS_PER_NODE" == 1 || "$GPUS_PER_NODE" == 2 ]] || fail "--gpus_per_node must be 1 or 2."
[[ "$CONSTRAINED_2GPU" == false || "$GPUS_PER_NODE" == 2 ]] || fail "--constrained_2gpu requires --gpus_per_node 2."
[[ -f "$BASE_PIPELINE" ]] || fail "Required existing pipeline is missing: $BASE_PIPELINE"
[[ -f "$VALIDATOR" ]] || fail "CPU data validator is missing: $VALIDATOR"
if [[ "$DRY_RUN" == false ]]; then
    [[ -n "${CUDA_VISIBLE_DEVICES:-}" ]] || fail "Set CUDA_VISIBLE_DEVICES explicitly before starting TP training."
    IFS=',' read -r -a VISIBLE_GPUS <<< "$CUDA_VISIBLE_DEVICES"
    [[ "${#VISIBLE_GPUS[@]}" == "$GPUS_PER_NODE" ]] || fail "CUDA_VISIBLE_DEVICES count must match --gpus_per_node."
    for GPU in "${VISIBLE_GPUS[@]}"; do
        [[ -n "${GPU//[[:space:]]/}" && "$GPU" != -1 ]] || fail "CUDA_VISIBLE_DEVICES contains an empty or disabled GPU."
    done
fi

cd -- "$PROJECT_ROOT"
printf 'Dipper backup TP branch: %s (Warmup 1 epoch + GAD 1 epoch)\n' "$BRANCH"
printf 'Warmup training: %s\nGAD training: %s\nValidation (both stages): %s\n' "$TP_TRAIN_FILE" "$GAD_TRAIN_FILE" "$VAL_FILE"
printf 'CPU preflight source: %s\nExperiment: %s\n' "$KGW_TRAIN_FILE" "$EXP_NAME"
printf '%s\n' 'Reusing validate_up_data.py for TP schema, metadata, full-source rows and protected-column checks.'

python3 "$VALIDATOR" \
    --original_train_file "$KGW_TRAIN_FILE" \
    --up_train_file "$TP_TRAIN_FILE" \
    --val_file "$VAL_FILE"

python3 - "$KGW_TRAIN_FILE" "$TP_TRAIN_FILE" <<'TP_AUDIT_PY'
import hashlib
import json
from pathlib import Path
import sys


def file_hash(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


try:
    source, output = (Path(value).resolve() for value in sys.argv[1:])
    audit_path = output.with_suffix(output.suffix + ".audit.json")
    with audit_path.open("r", encoding="utf-8") as handle:
        audit = json.load(handle)
    if not isinstance(audit, dict):
        raise ValueError("TP audit must be a JSON object")
    if audit.get("complete") is not True:
        raise ValueError("TP audit is incomplete; interrupted or smoke results cannot be trained")
    if audit.get("method") != "targeted_dipper_paraphrasing":
        raise ValueError("TP audit method must be targeted_dipper_paraphrasing; ordinary UP is not TP")
    changed = audit.get("changed_teacher_responses")
    if isinstance(changed, bool) or not isinstance(changed, int) or changed < 1:
        raise ValueError("TP audit must record changed_teacher_responses > 0")
    if audit.get("input_sha256") != file_hash(source):
        raise ValueError("TP audit input_sha256 does not match the original KGW training file")
    if audit.get("output_sha256") != file_hash(output):
        raise ValueError("TP audit output_sha256 does not match the TP training file")
except (OSError, ValueError, TypeError) as exc:
    print(f"TP audit preflight failed: {exc}", file=sys.stderr)
    raise SystemExit(2)

print(f"TP audit preflight passed: complete targeted paraphrasing, {changed} changed responses, verified input/output SHA-256 ({audit_path}).")
TP_AUDIT_PY

COMMAND=(bash "$BASE_PIPELINE"
    "${FORWARDED[@]}"
    --exp_name "$EXP_NAME"
    --nnodes "$NNODES"
    --gpus_per_node "$GPUS_PER_NODE"
    --warmup_epochs 1
    --gad_epochs 1
    --warmup_train_file "$TP_TRAIN_FILE"
    --gad_train_file "$GAD_TRAIN_FILE"
    --warmup_val_file "$VAL_FILE"
    --gad_val_file "$VAL_FILE")

if [[ "$DRY_RUN" == true ]]; then
    printf '%s\n' 'TP CPU preflight passed. Parent command preview (model/checkpoint/training checks occur on an actual run):'
    printf '%q ' "${COMMAND[@]}"
    printf '\n%s\n' 'No parent pipeline, model loading, GPU initialization, training or SwanLab calls were started.'
    exit 0
fi
printf '%s\n' 'The parent CLEAN labels are historical; the explicit stage-file arguments determine the data used.'
exec "${COMMAND[@]}"
