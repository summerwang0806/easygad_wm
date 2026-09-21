#!/usr/bin/env python3
"""
Export LMSYS GPT-5 Chat Response dataset to parquet files.

This script downloads the teacher data from HuggingFace and saves it
in parquet format for training.
"""
from pathlib import Path
from datasets import load_dataset


def main():
    # 以脚本所在目录为基准，创建 data 文件夹（已存在也不会报错）
    data_dir = Path(__file__).resolve().parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    print("Loading dataset ytz20/LMSYS-Chat-GPT-5-Chat-Response ...")
    ds = load_dataset("ytz20/LMSYS-Chat-GPT-5-Chat-Response")

    train_path = "data/lmsys_gpt5_chat_filtered_train.parquet"
    test_path = "data/lmsys_gpt5_chat_filtered_test.parquet"

    print(f"Saving train split to: {train_path}")
    ds["train"].to_parquet(train_path)

    print(f"Saving test split to: {test_path}")
    ds["test"].to_parquet(test_path)

    print("All done.")


if __name__ == "__main__":
    main()
