#!/usr/bin/env bash
set -euo pipefail
QUALITY_ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
cd "$QUALITY_ROOT"
exec python text_quality/evaluate_quality.py \
  --backend local --api-style chat_completions \
  --judge-model /shared/public_models/Qwen2.5-14B-Instruct \
  --judge-max-tokens 768 --timeout 180 --max-api-calls 1500 \
  --swanlab-mode cloud --swanlab-project easyGAD-wm \
  --swanlab-key-from-script "$QUALITY_ROOT/scripts/train/run_full_gad_optimized.sh" \
  "$@"
