#!/usr/bin/env bash
# UP teacher responses for Warmup, original KGW responses for GAD.
set -euo pipefail
PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
exec bash "${PROJECT_ROOT}/baseline_acl/run_up_gad_pipeline.sh" --branch up_kgw "$@"
