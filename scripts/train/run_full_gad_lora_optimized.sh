#!/bin/bash
# Full GAD Training Pipeline with LoRA - Warmup + GAD stages combined
# LoRA mode for parameter-efficient fine-tuning
# Usage: bash run_full_gad_lora_optimized.sh --exp_name <name> --nnodes <num_nodes> [--model <original_student_path>] [--reward_model <critic_init_path>]
set -o pipefail

export NCCL_TIMEOUT=36000
export TOKENIZERS_PARALLELISM=true
export SWANLAB_PROJECT='easyGAD-wm'
export SWANLAB_API_KEY='YOUR_SWANLAB_API_KEY'
export SWANLAB_MODE='cloud'
export HYDRA_FULL_ERROR=1

# One epoch per stage is an initial run; select later checkpoints by validation.
MODEL_PATH="/shared/public_models/Qwen2.5-1.5B-Instruct"
REWARD_MODEL_PATH=""
EXP_NAME=""
NNODES=""
N_GPUS_PER_NODE=2
WARMUP_EPOCHS=1
GAD_EPOCHS=1
SAVE_FREQ=500
TEST_FREQ=250
TRAIN_BATCH_SIZE=8
VAL_BATCH_SIZE=8
MAX_PROMPT_LENGTH=2048
MAX_RESPONSE_LENGTH=1536
LR=5e-6
CRITIC_LR=1e-5
KL_COEF=0.001
TEMPERATURE=0.8
WARMUP_N_SAMPLES=1
GAD_N_SAMPLES=2
LORA_RANK=16
WORK_BASE_DIR=checkpoints
TRAIN_FILE=data/dolly15k_qwen2_5_14b_kgw_train.parquet
VAL_FILE=data/dolly15k_qwen2_5_14b_kgw_test.parquet

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
        --test_freq)
            TEST_FREQ="$2"
            shift 2
            ;;
        --lora_rank)
            LORA_RANK="$2"
            shift 2
            ;;
        --work_dir)
            WORK_BASE_DIR="$2"
            shift 2
            ;;
        *)
            break
            ;;
    esac
done

if [ -z "$EXP_NAME" ] || [ -z "$NNODES" ]; then
    echo "Error: --exp_name and --nnodes are required; --model defaults to the original student model"
    exit 1
fi
# Initialize a separate critic backbone from the same original student model by default.
REWARD_MODEL_PATH=${REWARD_MODEL_PATH:-$MODEL_PATH}
if [ "$N_GPUS_PER_NODE" != 1 ] && [ "$N_GPUS_PER_NODE" != 2 ]; then
    echo "Error: --gpus_per_node must be 1 or 2"
    exit 1
fi
for required_path in "$MODEL_PATH/config.json" "$REWARD_MODEL_PATH/config.json" "$TRAIN_FILE" "$VAL_FILE"; do
    if [ ! -f "$required_path" ]; then
        echo "Error: missing $required_path (run from the EasyGAD root)"
        exit 1
    fi
done
MAX_TOKENS_PER_GPU=8192
GPU_MEMORY_UTILIZATION=0.30
if [ "$N_GPUS_PER_NODE" = 1 ]; then
    MAX_TOKENS_PER_GPU=4096
    GPU_MEMORY_UTILIZATION=0.20
fi
WORK_DIR=${WORK_BASE_DIR}/${EXP_NAME}
WARMUP_WORK_DIR=${WORK_DIR}/warmup
GAD_WORK_DIR=${WORK_DIR}/gad
if [ -e "$WORK_DIR" ]; then
    echo "Error: $WORK_DIR already exists; choose a new --exp_name"
    exit 1
fi
echo "=============================================="
echo "Starting Full GAD Training Pipeline with LoRA"
echo "Model: $MODEL_PATH"
echo "Reward Model: $REWARD_MODEL_PATH"
echo "Experiment Name: $EXP_NAME"
echo "Nodes: $NNODES"
echo "LoRA Rank: $LORA_RANK"
echo "Work Directory: $WORK_DIR"
echo "=============================================="

# ============================================
# Stage 1: Warmup - Initialize Discriminator and Warm up Student
# ============================================
echo ""
echo "=============================================="
echo "Stage 1: Warmup Phase (LoRA)"
echo "=============================================="

python3 -m verl.trainer.main_ppo \
    algorithm.adv_estimator=grpo \
    trainer.training_stage=warmup \
    data.prompt_key=content \
    data.train_files=${TRAIN_FILE} \
    data.val_files=${VAL_FILE} \
    data.train_batch_size=${TRAIN_BATCH_SIZE} \
    data.val_batch_size=${VAL_BATCH_SIZE} \
    data.max_prompt_length=${MAX_PROMPT_LENGTH} \
    data.max_response_length=${MAX_RESPONSE_LENGTH} \
    data.truncation=right \
    actor_rollout_ref.model.path=${MODEL_PATH} \
    actor_rollout_ref.model.use_shm=True \
    actor_rollout_ref.model.lora_rank=${LORA_RANK} \
    actor_rollout_ref.model.lora_alpha=${LORA_RANK} \
    actor_rollout_ref.model.target_modules=all-linear \
    actor_rollout_ref.actor.optim.lr=${LR} \
    actor_rollout_ref.actor.grad_clip=0.2 \
    actor_rollout_ref.model.use_remove_padding=True \
    actor_rollout_ref.actor.ppo_mini_batch_size=${TRAIN_BATCH_SIZE} \
    actor_rollout_ref.actor.use_dynamic_bsz=True \
    actor_rollout_ref.actor.ppo_max_token_len_per_gpu=${MAX_TOKENS_PER_GPU} \
    actor_rollout_ref.actor.use_kl_loss=False \
    actor_rollout_ref.actor.entropy_coeff=0.0 \
    actor_rollout_ref.actor.ulysses_sequence_parallel_size=1 \
    actor_rollout_ref.model.enable_gradient_checkpointing=True \
    actor_rollout_ref.actor.fsdp_config.param_offload=True \
    actor_rollout_ref.actor.fsdp_config.optimizer_offload=True \
    actor_rollout_ref.rollout.tensor_model_parallel_size=1 \
    actor_rollout_ref.rollout.name=vllm \
    actor_rollout_ref.rollout.temperature=${TEMPERATURE} \
    actor_rollout_ref.rollout.gpu_memory_utilization=${GPU_MEMORY_UTILIZATION} \
    actor_rollout_ref.rollout.n=${WARMUP_N_SAMPLES} \
    actor_rollout_ref.rollout.load_format=safetensors \
    actor_rollout_ref.rollout.layered_summon=True \
    actor_rollout_ref.ref.fsdp_config.param_offload=True \
    critic.model.path=${REWARD_MODEL_PATH} \
    critic.model.lora_rank=${LORA_RANK} \
    critic.model.lora_alpha=${LORA_RANK} \
    critic.model.target_modules=all-linear \
    critic.optim.lr=${CRITIC_LR} \
    critic.model.use_remove_padding=True \
    critic.model.enable_gradient_checkpointing=True \
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
    actor_rollout_ref.rollout.enforce_eager=False \
    actor_rollout_ref.rollout.free_cache_engine=False \
    trainer.default_local_dir=${WARMUP_WORK_DIR} \
    trainer.resume_mode=disable

# Check if warmup succeeded
if [ $? -ne 0 ]; then
    echo "Error: Warmup stage failed!"
    exit 1
fi

echo "Warmup stage completed successfully!"

# ============================================
# Prepare for GAD stage
# ============================================
echo ""
echo "=============================================="
echo "Preparing for GAD stage..."
echo "=============================================="

# Find the latest checkpoint from warmup
WARMUP_CHECKPOINT=$(ls -d ${WARMUP_WORK_DIR}/global_step_* 2>/dev/null | sort -V | tail -1)
if [ -z "$WARMUP_CHECKPOINT" ]; then
    echo "Error: No warmup checkpoint found!"
    exit 1
fi
RESUME_STEP=$(basename $WARMUP_CHECKPOINT | sed 's/global_step_//')
echo "Using warmup checkpoint: $WARMUP_CHECKPOINT (step $RESUME_STEP)"

# For LoRA, actor and critic checkpoints are used by the trainer's resume mechanism
# We use the base model paths for initialization
ACTOR_CHECKPOINT_PATH=${WARMUP_CHECKPOINT}/actor
CRITIC_CHECKPOINT_PATH=${WARMUP_CHECKPOINT}/critic

echo "Actor checkpoint: ${ACTOR_CHECKPOINT_PATH}"
echo "Critic checkpoint: ${CRITIC_CHECKPOINT_PATH}"
echo "Actor base model: ${MODEL_PATH}"
echo "Critic base model: ${REWARD_MODEL_PATH}"

# Load warmup actor and critic weights without reusing its exhausted data iterator.
RESUME_DIR=${WORK_DIR}/resume/global_step_${RESUME_STEP}
mkdir -p "$RESUME_DIR"
ln -s "$(realpath "$ACTOR_CHECKPOINT_PATH")" "$RESUME_DIR/actor"
ln -s "$(realpath "$CRITIC_CHECKPOINT_PATH")" "$RESUME_DIR/critic"
if [ ! -L "$RESUME_DIR/actor" ] || [ ! -L "$RESUME_DIR/critic" ]; then
    echo "Error: could not prepare stage transition checkpoint"
    exit 1
fi

# ============================================
# Stage 2: GAD - Main Adversarial Training
# ============================================
echo ""
echo "=============================================="
echo "Stage 2: GAD Phase (LoRA)"
echo "=============================================="

python3 -m verl.trainer.main_ppo \
    algorithm.adv_estimator=grpo \
    trainer.training_stage=gad \
    data.prompt_key=content \
    data.train_files=${TRAIN_FILE} \
    data.val_files=${VAL_FILE} \
    data.train_batch_size=${TRAIN_BATCH_SIZE} \
    data.val_batch_size=${VAL_BATCH_SIZE} \
    data.max_prompt_length=${MAX_PROMPT_LENGTH} \
    data.max_response_length=${MAX_RESPONSE_LENGTH} \
    data.truncation=right \
    actor_rollout_ref.model.path=${MODEL_PATH} \
    actor_rollout_ref.model.use_shm=True \
    actor_rollout_ref.model.lora_rank=${LORA_RANK} \
    actor_rollout_ref.model.lora_alpha=${LORA_RANK} \
    actor_rollout_ref.model.target_modules=all-linear \
    actor_rollout_ref.actor.optim.lr=${LR} \
    actor_rollout_ref.actor.grad_clip=0.2 \
    actor_rollout_ref.model.use_remove_padding=True \
    actor_rollout_ref.actor.ppo_mini_batch_size=${TRAIN_BATCH_SIZE} \
    actor_rollout_ref.actor.use_dynamic_bsz=True \
    actor_rollout_ref.actor.ppo_max_token_len_per_gpu=${MAX_TOKENS_PER_GPU} \
    actor_rollout_ref.actor.use_kl_loss=False \
    actor_rollout_ref.actor.entropy_coeff=0.0 \
    actor_rollout_ref.actor.ulysses_sequence_parallel_size=1 \
    actor_rollout_ref.model.enable_gradient_checkpointing=True \
    actor_rollout_ref.actor.fsdp_config.param_offload=True \
    actor_rollout_ref.actor.fsdp_config.optimizer_offload=True \
    actor_rollout_ref.rollout.tensor_model_parallel_size=1 \
    actor_rollout_ref.rollout.name=vllm \
    actor_rollout_ref.rollout.temperature=${TEMPERATURE} \
    actor_rollout_ref.rollout.gpu_memory_utilization=${GPU_MEMORY_UTILIZATION} \
    actor_rollout_ref.rollout.n=${GAD_N_SAMPLES} \
    actor_rollout_ref.rollout.load_format=safetensors \
    actor_rollout_ref.rollout.layered_summon=True \
    actor_rollout_ref.ref.fsdp_config.param_offload=True \
    critic.model.path=${REWARD_MODEL_PATH} \
    critic.model.lora_rank=${LORA_RANK} \
    critic.model.lora_alpha=${LORA_RANK} \
    critic.model.target_modules=all-linear \
    critic.optim.lr=${CRITIC_LR} \
    critic.model.use_remove_padding=True \
    critic.model.enable_gradient_checkpointing=True \
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
    trainer.total_epochs=$((WARMUP_EPOCHS + GAD_EPOCHS)) \
    actor_rollout_ref.rollout.enforce_eager=False \
    actor_rollout_ref.rollout.free_cache_engine=False \
    trainer.default_local_dir=${GAD_WORK_DIR} \
    trainer.resume_from_path=${RESUME_DIR} \
    trainer.resume_mode=resume_path

if [ $? -eq 0 ]; then
    echo ""
    echo "=============================================="
    echo "Full GAD Training Pipeline with LoRA Completed!"
    echo "Checkpoints saved to: ${GAD_WORK_DIR}"
    echo "=============================================="
else
    echo "Error: GAD stage failed!"
    exit 1
fi
