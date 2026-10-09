#!/usr/bin/env bash
# UP teacher responses for both Warmup and GAD; original KGW validation.
set -euo pipefail
PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
exec bash "${PROJECT_ROOT}/baseline_acl/run_up_gad_pipeline.sh" --branch up_up "$@"
