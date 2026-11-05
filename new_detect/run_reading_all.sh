#!/usr/bin/env bash
# Select a free GPU: CUDA_VISIBLE_DEVICES=0 bash new_detect/run_reading_all.sh.
set -euo pipefail
task_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd -- "$task_root"
python new_detect/run_reading.py --protocol official "$@"
