#!/usr/bin/env python3
"""Compute SHA256 for all files under HF model root, multithreaded.

Output: TSV — model\tfilename\tsha256\tsize
(Same format as hf-remote-hashes.py — just sort | diff.)

Usage:
  python3 hf-local-hashes.py /path/to/huggingface.co/
  python3 hf-local-hashes.py /path/to/huggingface.co/ -j 16
  python3 hf-local-hashes.py /path/to/huggingface.co/ --skip-below 1M

Compare:
  sort remote.tsv > /tmp/r.tsv
  python3 hf-local-hashes.py /path | sort > /tmp/l.tsv
  diff /tmp/l.tsv /tmp/r.tsv
"""
import argparse
import hashlib
import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

SKIP_DIRS = {'.cache', '.eval_results', '__pycache__', '.git', '.locks'}
SKIP_FILES = {'crc32.txt', '.gitkeep'}
CHUNK = 8 * 1024 * 1024


def hash_one(args):
    """Hash a single file. Returns (model, filename, sha256, size) or None on error."""
    model, filepath = args
    try:
        size = os.path.getsize(filepath)
        h = hashlib.sha256()
        with open(filepath, 'rb') as f:
            while True:
                chunk = f.read(CHUNK)
                if not chunk:
                    break
                h.update(chunk)
        return (model, filepath, h.hexdigest(), size)
    except Exception as e:
        print(f"  ERR: {filepath}: {e}", file=sys.stderr)
        return None


def collect_files(root, model_prefix, min_size=0):
    """Walk a model dir, yield (model, filepath) tuples."""
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if fn in SKIP_FILES:
                continue
            fp = os.path.join(dirpath, fn)
            try:
                sz = os.path.getsize(fp)
            except OSError:
                continue
            if min_size > 0 and sz < min_size:
                continue
            files.append((model_prefix, fp))
    return files


def main():
    p = argparse.ArgumentParser(description="SHA256 hash all files in HF model tree")
    p.add_argument("root", help="Path to huggingface.co root")
    p.add_argument("-j", "--workers", type=int, default=0,
                    help="Parallel workers (0 = CPU count, default)")
    p.add_argument("--skip-below", default="0",
                    help="Skip files smaller than this (e.g. 1M, 100K, 1G)")
    args = p.parse_args()

    workers = args.workers or os.cpu_count() or 4
    min_size = parse_size(args.skip_below)

    root = Path(args.root).resolve()
    all_tasks = []
    for owner in sorted(root.iterdir()):
        if not owner.is_dir() or owner.name.startswith('.'):
            continue
        for model in sorted(owner.iterdir()):
            if not model.is_dir() or model.name.startswith('.'):
                continue
            repo = f"{owner.name}/{model.name}"
            all_tasks.extend(collect_files(model, repo, min_size))

    total = len(all_tasks)
    print(f"# {total} files, {workers} workers", file=sys.stderr)

    if not all_tasks:
        return

    done = 0
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(hash_one, task): task for task in all_tasks}
        for fut in as_completed(futures):
            result = fut.result()
            done += 1
            if done % 50 == 0 or done == total:
                print(f"# {done}/{total}", file=sys.stderr)
            if result:
                model, fp, sha, size = result
                fname = os.path.relpath(fp, Path(args.root).resolve())
                print(f"{model}\t{fname}\t{sha}\t{size}")


def parse_size(s):
    """Parse '1M', '100K', '1G' etc to bytes."""
    s = s.strip().upper()
    if s.isdigit():
        return int(s)
    units = {'K': 1024, 'M': 1024**2, 'G': 1024**3}
    for suffix, mult in units.items():
        if s.endswith(suffix):
            return int(s[:-1]) * mult
    return 0


if __name__ == '__main__':
    main()
