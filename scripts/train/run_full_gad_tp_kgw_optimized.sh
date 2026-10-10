#!/usr/bin/env bash
# Targeted student-model paraphrasing for Warmup, original KGW responses for GAD.
set -euo pipefail
PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
exec bash "${PROJECT_ROOT}/baseline_acl/run_tp_gad_pipeline.sh" --branch tp_kgw "$@"
