#!/usr/bin/env bash
# No shell tracing: do not echo API credentials. Default is a no-network check.
set -euo pipefail
QUALITY_ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
cd "$QUALITY_ROOT"
# One file per invocation; do not implicitly load the four-model defaults.
QUALITY_SINGLE_INPUT=false
for QUALITY_ARGUMENT in "$@"; do
  if [[ "$QUALITY_ARGUMENT" == "--input-file" || "$QUALITY_ARGUMENT" == --input-file=* ]]; then
    QUALITY_SINGLE_INPUT=true
  fi
done
if [[ "$QUALITY_SINGLE_INPUT" != true ]]; then
  echo "Usage: bash text_quality/run_quality.sh --input-file wm_test/<answers>.jsonl [--run-api ...]" >&2
  exit 2
fi
exec python text_quality/evaluate_quality.py \
  --backend api \
  --reference-file "$QUALITY_ROOT/text_quality/references/dolly_human_500.jsonl" \
  --swanlab-mode cloud --swanlab-project easyGAD-wm \
  --swanlab-key-from-script "$QUALITY_ROOT/scripts/train/run_full_gad_optimized.sh" \
  --base-url http://43.159.131.189:8080/v1 \
  --api-style responses --judge-model gpt-5.5 \
  --api-key-file "$QUALITY_ROOT/text_quality/.relay_api.key" \
  --reasoning-effort low --judge-max-tokens 4096 --reference-max-tokens 4096 \
  --max-api-calls 1500 \
  "$@"
