#!/usr/bin/env bash
# No shell tracing: do not echo API credentials. Default is a no-network check.
set -euo pipefail
QUALITY_ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
cd "$QUALITY_ROOT"
exec python text_quality/evaluate_quality.py "$@"
