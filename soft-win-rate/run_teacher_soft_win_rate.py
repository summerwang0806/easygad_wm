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
# INPUT_JSONL = ROOT / "wm_test/cleanwarmup_cleangad_gad_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl"


# kgwwarmup_kgwgad
INPUT_JSONL = ROOT / "wm_test/kgwwarmup_kgwgad_gad_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.jsonl"
# INPUT_JSONL = ROOT / "wm_test/kgwwarmup_kgwgad_warmup_gamma0.5_delta3_new_qwen2_5_0_5b_dolly15k_test.jsonl"

# INPUT_JSONL = ROOT / "wm_test/kgwwarmup_kgwgad_gad1500_gamma0.5_qwen2_5_0_5b_dolly15k_test.jsonl"


# parawarmup_paragad
# INPUT_JSONL = ROOT / "wm_test/dipper_upkgwwarmup_upkgwgad_gad_gamma0.5_delta3_new1_qwen2_5_0_5b_dolly15k_test.jsonl"


# wn的两个结果
# INPUT_JSONL = ROOT / "wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new.jsonl"
# INPUT_JSONL = ROOT / "wn/wn_Qwen2.5-0.5B_gamma0.5_delta3_gad_new_strength3.jsonl"


# 固定读取 content 作为问题、teacher_response 作为参照回答。
# REFERENCE_PARQUET = ROOT / "data/dolly15k_qwen2_5_14b_clean_test.parquet"
REFERENCE_PARQUET = ROOT /"data/dolly15k_qwen2_5_14b_kgw_gamma0.5_delta3_newtest.parquet"
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
