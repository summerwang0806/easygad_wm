#!/usr/bin/env bash
# Targeted student-model paraphrasing responses for Warmup and GAD; KGW validation.
set -euo pipefail
PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
exec bash "${PROJECT_ROOT}/baseline_acl/run_tp_gad_pipeline.sh" --branch tp_tp "$@"
