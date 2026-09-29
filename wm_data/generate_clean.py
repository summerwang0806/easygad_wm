#!/usr/bin/env python3
"""Generate non-watermarked Qwen teacher responses in EasyGAD format."""

from generate_teacher_data import main


if __name__ == "__main__":
    main(default_watermark="none")
