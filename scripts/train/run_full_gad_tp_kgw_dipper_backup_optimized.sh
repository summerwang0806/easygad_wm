#!/usr/bin/env bash
# Backup Dipper projection TP for Warmup, original KGW responses for GAD.
set -euo pipefail
PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
exec bash "${PROJECT_ROOT}/baseline_acl/run_tp_gad_pipeline_dipper_backup.sh" --branch tp_kgw "$@"
