#!/usr/bin/env python3
"""Local Qwen3-32B soft win rate against saved clean teacher Parquet answers.

Run without arguments; normally change only INPUT_JSONL below.
Reuses the original local judge, automatic GPU selection and resumable cache.
"""
from pathlib import Path
import sys

import run_soft_win_rate as common

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

# 日常只修改这一行；相对路径始终以项目根目录为基准。
INPUT_JSONL = ROOT / "wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl"

# 固定读取 content 作为问题、teacher_response 作为参照回答。
REFERENCE_PARQUET = ROOT / "data/dolly15k_qwen2_5_14b_clean_test.parquet"
RESULTS_DIR = HERE / "results" / "teacher"
HISTORY_FILE = HERE / "teacher_soft_win_rate_history.md"


def main(argv=None) -> int:
    return common.main(argv, input_jsonl=INPUT_JSONL, reference_file=REFERENCE_PARQUET,
                       results_dir=RESULTS_DIR, history_file=HISTORY_FILE, description=__doc__)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, RuntimeError, FileNotFoundError, OSError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
