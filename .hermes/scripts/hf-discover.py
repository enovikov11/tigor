#!/usr/bin/env python3
"""Walk HF model tree and emit one 'owner/model' per line.

Usage:
  python3 hf-discover.py /path/to/huggingface.co/
  # Output:
  # MiniMaxAI/MiniMax-H3
  # Qwen/Qwen3.8-27B
  # Qwen/Qwen3.8-27B-FP8
"""
import sys
from pathlib import Path

SKIP = {'.cache', '.eval_results', '__pycache__', '.git', '.locks'}

def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(sys.argv[0]).parent / '..'
    for owner in sorted(root.iterdir()):
        if not owner.is_dir() or owner.name.startswith('.'):
            continue
        for model in sorted(owner.iterdir()):
            if not model.is_dir() or model.name.startswith('.'):
                continue
            # Only emit if it has at least one file (not empty dir)
            has_file = any(f.is_file() for f in model.iterdir() if f.name not in SKIP)
            if has_file:
                print(f"{owner.name}/{model.name}")

if __name__ == '__main__':
    main()
