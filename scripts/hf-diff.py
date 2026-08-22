#!/usr/bin/env python3
"""Compare remote vs local SHA256 hashes.

Both files have the same format: model\tfilename\tsha256\tsize
Just sort and diff. This script gives colored output.

Usage:
  python3 hf-diff.py remote.tsv local.tsv
"""
import argparse
import sys

def load(path):
    d = {}
    with open(path) as f:
        for line in f:
            if line.startswith('#'):
                continue
            parts = line.rstrip('\n').split('\t')
            if len(parts) < 4:
                continue
            model, fname, sha, size = parts[0], parts[1], parts[2], parts[3]
            d[(model, fname)] = {"sha": sha, "size": size}
    return d

def main():
    p = argparse.ArgumentParser()
    p.add_argument("remote", help="Remote hashes TSV")
    p.add_argument("local", help="Local hashes TSV")
    p.add_argument("--only-bad", action="store_true")
    args = p.parse_args()

    remote = load(args.remote)
    local = load(args.local)

    all_keys = sorted(set(list(remote.keys()) + list(local.keys())))
    ok = bad = missing = extra = 0

    for model, fname in all_keys:
        key = (model, fname)
        in_r = key in remote
        in_l = key in local

        if in_r and not in_l:
            missing += 1
            print(f"[MISSING] {model}/{fname}")
            continue
        if not in_r and in_l:
            extra += 1
            if not args.only_bad:
                print(f"[EXTRA]   {model}/{fname}")
            continue

        r, l = remote[key], local[key]
        if r["size"] and l["size"] and r["size"] != l["size"]:
            bad += 1
            print(f"[SIZE]    {model}/{fname}  remote={r['size']}  local={l['size']}")
            continue
        if r["sha"] == l["sha"]:
            ok += 1
            if not args.only_bad:
                print(f"[OK]      {model}/{fname}")
        else:
            bad += 1
            print(f"[MISMATCH] {model}/{fname}")
            print(f"  remote {r['sha']}")
            print(f"  local  {l['sha']}")

    print(f"\nOK: {ok}  MISMATCH: {bad}  MISSING: {missing}  EXTRA: {extra}", file=sys.stderr)
    if bad or missing:
        sys.exit(1)

if __name__ == '__main__':
    main()
