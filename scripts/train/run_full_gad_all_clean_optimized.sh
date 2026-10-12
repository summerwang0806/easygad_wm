#!/bin/bash
# Independent CLEAN Warmup -> CLEAN GAD control experiment.
# Existing scripts preserved; see GAD_ALL_CLEAN.md for stages and commands.
# Usage: bash run_full_gad_all_clean_optimized.sh --exp_name <name> --nnodes 1 [--dry_run]
set -o pipefail

export NCCL_TIMEOUT=36000
export TOKENIZERS_PARALLELISM=true
export HYDRA_FULL_ERROR=1
export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0,3}"
export CUDA_DEVICE_ORDER="${CUDA_DEVICE_ORDER:-PCI_BUS_ID}"
export NCCL_P2P_DISABLE="${NCCL_P2P_DISABLE:-1}"
export VLLM_USE_V1=0
export RAY_TMPDIR=/shared/wwx/EasyGAD/ray_tmp


export SWANLAB_PROJECT='easyGAD-wm'
export SWANLAB_API_KEY='fJM4mt47P1Zxo1KEipLWe'
export SWANLAB_MODE='cloud'
# export http_proxy=http://127.0.0.1:7890
# export https_proxy=http://127.0.0.1:7890
# export HTTP_PROXY="$http_proxy"
# export HTTPS_PROXY="$https_proxy"
# export NO_PROXY="${NO_PROXY:+$NO_PROXY,}127.0.0.1,localhost,10.107.6.60"
# export no_proxy="$NO_PROXY"


# One epoch per stage is an initial run; select later checkpoints by validation.
MODEL_PATH="/shared/public_models/Qwen2.5-0.5B"
REWARD_MODEL_PATH=""
EXP_NAME=""
NNODES=""
N_GPUS_PER_NODE=2
WORK_BASE_DIR=checkpoints
WARMUP_EPOCHS=1
GAD_EPOCHS=1
SAVE_FREQ=500
TEST_FREQ=250
TRAIN_BATCH_SIZE=8
VAL_BATCH_SIZE=8
MAX_PROMPT_LENGTH=2048
MAX_RESPONSE_LENGTH=1536
# LR_warmup=5e-6
LR_warmup=1e-6
LR=1e-6
CRITIC_LR=1e-5
KL_COEF=0.001
TEMPERATURE=0.8
WARMUP_N_SAMPLES=1
GAD_N_SAMPLES=2
CONSTRAINED_2GPU=False
ENFORCE_EAGER=False
GPU_MEMORY_OVERRIDE=""
RESUME=False
SKIP_WARMUP=False
RESUME_MODE=disable
WARMUP_TRAIN_FILE=data/dolly15k_qwen2_5_14b_clean_train.parquet
GAD_TRAIN_FILE=data/dolly15k_qwen2_5_14b_clean_train.parquet
# All-clean defaults include validation; use CLI overrides for a shared KGW reference.
WARMUP_VAL_FILE=data/dolly15k_qwen2_5_14b_clean_test.parquet
GAD_VAL_FILE=data/dolly15k_qwen2_5_14b_clean_test.parquet
DRY_RUN=False

while [[ $# -gt 0 ]]; do
    case $1 in
        --model)
            MODEL_PATH="$2"
            shift 2
            ;;
        --reward_model)
            REWARD_MODEL_PATH="$2"
            shift 2
            ;;
        --exp_name)
            EXP_NAME="$2"
            shift 2
            ;;
        --nnodes)
            NNODES="$2"
            shift 2
            ;;
        --warmup_epochs)
            WARMUP_EPOCHS="$2"
            shift 2
            ;;
        --gad_epochs)
            GAD_EPOCHS="$2"
            shift 2
            ;;
        --save_freq)
            SAVE_FREQ="$2"
            shift 2
            ;;
        --train_batch_size)
            TRAIN_BATCH_SIZE="$2"
            shift 2
            ;;
        --lr)
            LR="$2"
            shift 2
            ;;
        --gpus_per_node)
            N_GPUS_PER_NODE="$2"
            shift 2
            ;;
        --gpu_memory_utilization)
            GPU_MEMORY_OVERRIDE="$2"
            shift 2
            ;;
        --constrained_2gpu)
            CONSTRAINED_2GPU=True
            shift
            ;;
        --work_dir)
            WORK_BASE_DIR="$2"
            shift 2
            ;;
        --test_freq)
            TEST_FREQ="$2"
            shift 2
            ;;
        --resume)
            RESUME=True
            RESUME_MODE=auto
            shift
            ;;
        --skip_warmup)
            SKIP_WARMUP=True
            shift
            ;;
        --warmup_train_file) WARMUP_TRAIN_FILE="$2"; shift 2 ;;
        --gad_train_file) GAD_TRAIN_FILE="$2"; shift 2 ;;
        --warmup_val_file) WARMUP_VAL_FILE="$2"; shift 2 ;;
        --gad_val_file) GAD_VAL_FILE="$2"; shift 2 ;;
        --dry_run) DRY_RUN=True; shift ;;
        *)
            echo "Error: unknown argument $1" >&2
            exit 1
            ;;
    esac
done

if [ -z "$EXP_NAME" ] || [ -z "$NNODES" ]; then
    echo "Error: --exp_name and --nnodes are required; --model defaults to the original student model"
    exit 1
fi
# Initialize a separate critic backbone from the same original student model by default.
REWARD_MODEL_PATH=${REWARD_MODEL_PATH:-$MODEL_PATH}
if [ "$SKIP_WARMUP" = True ] && [ "$RESUME" != True ]; then
    echo "Error: --skip_warmup requires --resume and an existing warmup checkpoint" >&2
    exit 1
fi
if [ "$N_GPUS_PER_NODE" != 1 ] && [ "$N_GPUS_PER_NODE" != 2 ]; then
    echo "Error: --gpus_per_node must be 1 or 2"
    exit 1
fi
for required_path in "$MODEL_PATH/config.json" "$REWARD_MODEL_PATH/config.json" "$WARMUP_TRAIN_FILE" "$GAD_TRAIN_FILE" "$WARMUP_VAL_FILE" "$GAD_VAL_FILE"; do
    if [ ! -f "$required_path" ]; then
        echo "Error: missing $required_path (run from the EasyGAD root)"
        exit 1
    fi
done
VISIBLE_GPU_COUNT=$(awk -F, '{print NF}' <<< "$CUDA_VISIBLE_DEVICES")
if [ "$VISIBLE_GPU_COUNT" != "$N_GPUS_PER_NODE" ]; then
    echo "Error: CUDA_VISIBLE_DEVICES count must match --gpus_per_node" >&2
    exit 1
fi
MAX_TOKENS_PER_GPU=8192
GPU_MEMORY_UTILIZATION=0.45
ACTOR_OFFLOAD=False
if [ "$N_GPUS_PER_NODE" = 1 ]; then
    MAX_TOKENS_PER_GPU=4096
    GPU_MEMORY_UTILIZATION=0.20
    ACTOR_OFFLOAD=True
fi
if [ "$CONSTRAINED_2GPU" = True ]; then
    if [ "${CUDA_VISIBLE_DEVICES:-}" != "2,3" ] || [ "$N_GPUS_PER_NODE" != 2 ] || [ "$NNODES" != 1 ]; then
        echo "Error: --constrained_2gpu requires CUDA_VISIBLE_DEVICES=2,3, --gpus_per_node 2 and --nnodes 1"
        exit 1
    fi
    MAX_TOKENS_PER_GPU=4096
    GPU_MEMORY_UTILIZATION=0.45
    ACTOR_OFFLOAD=True
    ENFORCE_EAGER=True
    export VLLM_USE_V1=0
fi
if [ -n "$GPU_MEMORY_OVERRIDE" ]; then
    GPU_MEMORY_UTILIZATION="$GPU_MEMORY_OVERRIDE"
fi
WORK_DIR=${WORK_BASE_DIR}/${EXP_NAME}
WARMUP_WORK_DIR=${WORK_DIR}/warmup
GAD_WORK_DIR=${WORK_DIR}/gad
if [ -e "$WORK_DIR" ] && [ "$RESUME" != True ]; then
    echo "Error: $WORK_DIR already exists; use --resume to continue, or choose a new --exp_name"
    exit 1
fi
if [ "$RESUME" = True ] && [ ! -d "$WORK_DIR" ]; then
    echo "Error: --resume requires an existing experiment directory: $WORK_DIR" >&2
    exit 1
fi

# This tracker is written after actor, critic and dataloader have been saved.
# A newer global_step_* directory may be an interrupted save; do not select it.
find_saved_checkpoint() {
    local stage_dir="$1" tracker step checkpoint
    tracker="$stage_dir/latest_checkpointed_iteration.txt"
    [ -f "$tracker" ] || return 0
    step=$(< "$tracker")
    if ! [[ "$step" =~ ^[0-9]+$ ]]; then
        echo "Error: invalid checkpoint tracker: $tracker" >&2
        return 1
    fi
    checkpoint="$stage_dir/global_step_$step"
    if [ ! -d "$checkpoint/actor" ] || [ ! -d "$checkpoint/critic" ] || [ ! -f "$checkpoint/data.pt" ]; then
        echo "Error: incomplete checkpoint recorded by $tracker: $checkpoint (actor, critic and data.pt are required)" >&2
        return 1
    fi
    echo "$checkpoint"
}

if [ "$RESUME" = True ]; then
    WARMUP_CHECKPOINT=$(find_saved_checkpoint "$WARMUP_WORK_DIR") || exit 1
    GAD_CHECKPOINT=$(find_saved_checkpoint "$GAD_WORK_DIR") || exit 1
    if [ -f "$WARMUP_WORK_DIR/.stage_completed" ]; then
        COMPLETED_STEP=$(< "$WARMUP_WORK_DIR/.stage_completed")
        if ! [[ "$COMPLETED_STEP" =~ ^[0-9]+$ ]] || [ -z "$WARMUP_CHECKPOINT" ] || \
            [ "$COMPLETED_STEP" != "${WARMUP_CHECKPOINT##*/global_step_}" ]; then
            echo "Error: invalid warmup completion marker: $WARMUP_WORK_DIR/.stage_completed (must match the saved checkpoint step)" >&2
            exit 1
        fi
        SKIP_WARMUP=True
    fi
    if [ -n "$GAD_CHECKPOINT" ]; then
        SKIP_WARMUP=True
    fi
    if [ "$SKIP_WARMUP" = True ] && [ -z "$WARMUP_CHECKPOINT" ]; then
        echo "Error: skipping warmup requires a saved warmup checkpoint in $WARMUP_WORK_DIR" >&2
        exit 1
    fi
    if [ -n "$GAD_CHECKPOINT" ]; then
        echo "Resuming GAD from: $GAD_CHECKPOINT"
    elif [ "$SKIP_WARMUP" != True ]; then
        echo "Resuming warmup from: ${WARMUP_CHECKPOINT:-no saved checkpoint; restarting warmup}"
    fi
fi
echo "=============================================="
echo "Starting independent CLEAN Warmup -> CLEAN GAD pipeline"
echo "Model: $MODEL_PATH"
echo "Reward Model: $REWARD_MODEL_PATH"
echo "Experiment Name: $EXP_NAME"
echo "Nodes: $NNODES"
echo "Work Directory: $WORK_DIR"
echo "Resume mode: $RESUME_MODE; skip warmup: $SKIP_WARMUP"
echo "CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES; NCCL_P2P_DISABLE=$NCCL_P2P_DISABLE"
echo "Warmup: train=$WARMUP_TRAIN_FILE; val=$WARMUP_VAL_FILE; epochs=$WARMUP_EPOCHS"
echo "GAD: train=$GAD_TRAIN_FILE; val=$GAD_VAL_FILE; epochs=$GAD_EPOCHS"
echo "Learning rates: warmup_actor=$LR_warmup; gad_actor=$LR; critic=$CRITIC_LR"
echo "GPU profile: constrained_2gpu=$CONSTRAINED_2GPU, vLLM fraction=$GPU_MEMORY_UTILIZATION, actor offload=$ACTOR_OFFLOAD, eager=$ENFORCE_EAGER"
echo "=============================================="

if [ "$DRY_RUN" = True ]; then
    echo "Configuration checks passed. No training, GPU initialization, or SwanLab calls were started."
    exit 0
fi
if ! timeout 30 swanlab verify; then
    echo "Error: SwanLab authentication/network check failed. Check login and proxy tunnel." >&2
    exit 1
fi

# ============================================
# Stage 1: CLEAN teacher responses train both student and ranking critic
# ============================================
echo ""
echo "=============================================="
echo "Stage 1: CLEAN Warmup Phase"
echo "=============================================="

if [ "$SKIP_WARMUP" != True ]; then
python3 -m verl.trainer.main_ppo \
    algorithm.adv_estimator=grpo \
    trainer.training_stage=warmup \
    data.prompt_key=content \
    data.train_files=${WARMUP_TRAIN_FILE} \
    data.val_files=${WARMUP_VAL_FILE} \
    data.train_batch_size=${TRAIN_BATCH_SIZE} \
    data.val_batch_size=${VAL_BATCH_SIZE} \
    data.max_prompt_length=${MAX_PROMPT_LENGTH} \
    data.max_response_length=${MAX_RESPONSE_LENGTH} \
    data.truncation=right \
    actor_rollout_ref.model.path=${MODEL_PATH} \
    actor_rollout_ref.actor.optim.lr=${LR_warmup} \
    actor_rollout_ref.actor.grad_clip=0.2 \
    actor_rollout_ref.model.use_remove_padding=True \
    actor_rollout_ref.actor.ppo_mini_batch_size=${TRAIN_BATCH_SIZE} \
    actor_rollout_ref.actor.use_dynamic_bsz=True \
    actor_rollout_ref.actor.ppo_max_token_len_per_gpu=${MAX_TOKENS_PER_GPU} \
    actor_rollout_ref.actor.use_kl_loss=False \
    actor_rollout_ref.actor.entropy_coeff=0.0 \
    actor_rollout_ref.actor.ulysses_sequence_parallel_size=1 \
    actor_rollout_ref.model.enable_gradient_checkpointing=True \
    actor_rollout_ref.actor.fsdp_config.param_offload=${ACTOR_OFFLOAD} \
    actor_rollout_ref.actor.fsdp_config.optimizer_offload=${ACTOR_OFFLOAD} \
    actor_rollout_ref.rollout.tensor_model_parallel_size=1 \
    actor_rollout_ref.rollout.name=vllm \
    actor_rollout_ref.rollout.temperature=${TEMPERATURE} \
    actor_rollout_ref.rollout.gpu_memory_utilization=${GPU_MEMORY_UTILIZATION} \
    actor_rollout_ref.rollout.n=${WARMUP_N_SAMPLES} \
    actor_rollout_ref.ref.fsdp_config.param_offload=False \
    critic.model.path=${REWARD_MODEL_PATH} \
    critic.optim.lr=${CRITIC_LR} \
    critic.model.use_remove_padding=True \
    critic.model.enable_gradient_checkpointing=True \
    critic.model.fsdp_config.param_offload=True \
    critic.model.fsdp_config.optimizer_offload=True \
    critic.ppo_max_token_len_per_gpu=${MAX_TOKENS_PER_GPU} \
    critic.grad_clip=0.2 \
    algorithm.kl_ctrl.kl_coef=${KL_COEF} \
    trainer.val_before_train=True \
    trainer.critic_warmup=10 \
    trainer.logger=['console','swanlab'] \
    trainer.project_name=${SWANLAB_PROJECT} \
    trainer.experiment_name=${EXP_NAME}_warmup \
    trainer.n_gpus_per_node=${N_GPUS_PER_NODE} \
    trainer.nnodes=${NNODES} \
    trainer.save_freq=${SAVE_FREQ} \
    trainer.max_actor_ckpt_to_keep=2 \
    trainer.max_critic_ckpt_to_keep=2 \
    trainer.test_freq=${TEST_FREQ} \
    trainer.default_hdfs_dir=null \
    trainer.total_epochs=${WARMUP_EPOCHS} \
    actor_rollout_ref.rollout.enforce_eager=${ENFORCE_EAGER} \
    actor_rollout_ref.rollout.free_cache_engine=False \
    trainer.default_local_dir=${WARMUP_WORK_DIR} \
    trainer.resume_mode=${RESUME_MODE}

# Check if warmup succeeded
if [ $? -ne 0 ]; then
    echo "Error: Warmup stage failed!"
    exit 1
fi

echo "Warmup stage completed successfully!"
else
    echo "Skipping completed warmup; using checkpoint: $WARMUP_CHECKPOINT"
fi

# ============================================
# Prepare models for GAD stage
# ============================================
echo ""
echo "=============================================="
echo "Preparing models for GAD stage..."
echo "=============================================="

# Find the latest checkpoint whose save completed.
WARMUP_CHECKPOINT=$(find_saved_checkpoint "$WARMUP_WORK_DIR") || exit 1
if [ -z "$WARMUP_CHECKPOINT" ]; then
    echo "Error: No warmup checkpoint found!"
    exit 1
fi
RESUME_STEP=${WARMUP_CHECKPOINT##*/global_step_}
printf '%s\n' "$RESUME_STEP" > "$WARMUP_WORK_DIR/.stage_completed" || exit 1
echo "Using warmup checkpoint: $WARMUP_CHECKPOINT (step $RESUME_STEP)"

# Reuse completed exports. Legacy exports without markers are safely merged
# once using the same CPU merger as the original pipeline.
prepare_model() {
    local checkpoint_dir="$1" hf_dir="$1/huggingface" marker="$1/huggingface/.merge_completed"
    if [ -f "$marker" ] && [ -f "$hf_dir/config.json" ] && \
        { [ -f "$hf_dir/model.safetensors" ] || [ -f "$hf_dir/model.safetensors.index.json" ] || \
          [ -f "$hf_dir/pytorch_model.bin" ] || [ -f "$hf_dir/pytorch_model.bin.index.json" ]; }; then
        echo "Reusing merged model: $hf_dir"
        return 0
    fi
    mkdir -p "$hf_dir" || return 1
    find "$checkpoint_dir/" -maxdepth 1 -type f ! -name "*.pt" -exec cp {} "$hf_dir/" \; || return 1
    CUDA_VISIBLE_DEVICES="" python3 scripts/model_merger.py merge --backend fsdp --local_dir "$checkpoint_dir" --target_dir "$hf_dir" || return 1
    touch "$marker"
}

# Merge actor model
ACTOR_MODEL_PATH=${WARMUP_CHECKPOINT}/actor/huggingface
if ! prepare_model "$WARMUP_CHECKPOINT/actor"; then
    echo "Error: Failed to merge actor model!"
    exit 1
fi
echo "Actor model prepared at: ${ACTOR_MODEL_PATH}"
ls ${ACTOR_MODEL_PATH}

# Merge critic model
CRITIC_MODEL_PATH=${WARMUP_CHECKPOINT}/critic/huggingface
if ! prepare_model "$WARMUP_CHECKPOINT/critic"; then
    echo "Error: Failed to merge critic model!"
    exit 1
fi
echo "Critic model prepared at: ${CRITIC_MODEL_PATH}"
ls ${CRITIC_MODEL_PATH}

# ============================================
# Stage 2: CLEAN teacher responses as the GAD teacher target
# ============================================
echo ""
echo "=============================================="
echo "Stage 2: CLEAN GAD Phase"
echo "=============================================="

python3 -m verl.trainer.main_ppo \
    algorithm.adv_estimator=grpo \
    trainer.training_stage=gad \
    data.prompt_key=content \
    data.train_files=${GAD_TRAIN_FILE} \
    data.val_files=${GAD_VAL_FILE} \
    data.train_batch_size=${TRAIN_BATCH_SIZE} \
    data.val_batch_size=${VAL_BATCH_SIZE} \
    data.max_prompt_length=${MAX_PROMPT_LENGTH} \
    data.max_response_length=${MAX_RESPONSE_LENGTH} \
    data.truncation=right \
    actor_rollout_ref.model.path=${ACTOR_MODEL_PATH} \
    actor_rollout_ref.actor.optim.lr=${LR} \
    actor_rollout_ref.actor.grad_clip=0.2 \
    actor_rollout_ref.model.use_remove_padding=True \
    actor_rollout_ref.actor.ppo_mini_batch_size=${TRAIN_BATCH_SIZE} \
    actor_rollout_ref.actor.use_dynamic_bsz=True \
    actor_rollout_ref.actor.ppo_max_token_len_per_gpu=${MAX_TOKENS_PER_GPU} \
    actor_rollout_ref.actor.use_kl_loss=False \
    actor_rollout_ref.actor.entropy_coeff=0.0 \
    actor_rollout_ref.actor.policy_loss.loss_mode=clip_cov \
    actor_rollout_ref.actor.ulysses_sequence_parallel_size=1 \
    actor_rollout_ref.model.enable_gradient_checkpointing=True \
    actor_rollout_ref.actor.fsdp_config.param_offload=${ACTOR_OFFLOAD} \
    actor_rollout_ref.actor.fsdp_config.optimizer_offload=${ACTOR_OFFLOAD} \
    actor_rollout_ref.rollout.tensor_model_parallel_size=1 \
    actor_rollout_ref.rollout.name=vllm \
    actor_rollout_ref.rollout.temperature=${TEMPERATURE} \
    actor_rollout_ref.rollout.gpu_memory_utilization=${GPU_MEMORY_UTILIZATION} \
    actor_rollout_ref.rollout.n=${GAD_N_SAMPLES} \
    actor_rollout_ref.ref.fsdp_config.param_offload=False \
    critic.model.path=${CRITIC_MODEL_PATH} \
    critic.optim.lr=${CRITIC_LR} \
    critic.model.use_remove_padding=True \
    critic.model.enable_gradient_checkpointing=True \
    critic.model.fsdp_config.param_offload=True \
    critic.model.fsdp_config.optimizer_offload=True \
    critic.ppo_max_token_len_per_gpu=${MAX_TOKENS_PER_GPU} \
    critic.grad_clip=0.2 \
    algorithm.kl_ctrl.kl_coef=${KL_COEF} \
    trainer.val_before_train=True \
    trainer.critic_warmup=0 \
    trainer.logger=['console','swanlab'] \
    trainer.project_name=${SWANLAB_PROJECT} \
    trainer.experiment_name=${EXP_NAME}_gad \
    trainer.n_gpus_per_node=${N_GPUS_PER_NODE} \
    trainer.nnodes=${NNODES} \
    trainer.save_freq=${SAVE_FREQ} \
    trainer.max_actor_ckpt_to_keep=2 \
    trainer.max_critic_ckpt_to_keep=2 \
    trainer.test_freq=${TEST_FREQ} \
    trainer.default_hdfs_dir=null \
    trainer.total_epochs=${GAD_EPOCHS} \
    actor_rollout_ref.rollout.enforce_eager=${ENFORCE_EAGER} \
    actor_rollout_ref.rollout.free_cache_engine=False \
    trainer.default_local_dir=${GAD_WORK_DIR} \
    trainer.resume_mode=${RESUME_MODE}

if [ $? -eq 0 ]; then
    echo ""
    echo "=============================================="
    echo "Full GAD Training Pipeline Completed!"
    echo "Checkpoints saved to: ${GAD_WORK_DIR}"
    echo "=============================================="
else
    echo "Error: GAD stage failed!"
    exit 1
fi
