#!/usr/bin/env python3
"""Fetch expected SHA256 hashes from HF API.

Input:  repo ID on command line, or one per line from stdin.
Output: TSV to stdout —  model\tfilename\tsha256\tsize
        (only LFS files with known SHA256; non-LFS skipped)

Usage:
  python3 hf-remote-hashes.py Qwen/Qwen3.8-27B-FP8
  # or piped:
  python3 hf-discover.py /path/to/huggingface.co/ | python3 hf-remote-hashes.py
"""
import sys
import json
import urllib.request
import urllib.error

def fetch(repo_id):
    url = f"https://huggingface.co/api/models/{repo_id}/tree/main"
    req = urllib.request.Request(url, headers={"User-Agent": "hf-audit/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            tree = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"  WARN: HTTP {e.code} for {repo_id}", file=sys.stderr)
        return
    except Exception as e:
        print(f"  WARN: {e} for {repo_id}", file=sys.stderr)
        return

    for entry in tree:
        lfs = entry.get("lfs")
        if lfs:
            h = lfs.get("oid") or lfs.get("sha256", "")
            if h:
                h = h.removeprefix("0000000000000000")
                print(f"{repo_id}\t{entry['path']}\t{h}\t{entry.get('size', '')}")

def main():
    if len(sys.argv) > 1:
        for repo in sys.argv[1:]:
            fetch(repo)
    else:
        for line in sys.stdin:
            repo = line.strip()
            if repo:
                fetch(repo)

if __name__ == '__main__':
    main()
