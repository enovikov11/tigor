#!/usr/bin/env python3
"""Verify local HF model file hashes against the HF API.

Usage:
  python3 hf-hash-audit.py /path/to/huggingface.co/
  python3 hf-hash-audit.py /path/to/huggingface.co/ --model Qwen/Qwen3.8-27B-FP8
  python3 hf-hash-audit.py /path/to/huggingface.co/ --check  # only report mismatches
  python3 hf-hash-audit.py /path/to/huggingface.co/ --json    # output JSON
"""
import argparse
import hashlib
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

CHUNK = 8 * 1024 * 1024  # 8 MB reads
SKIP_DIRS = {'.cache', '.eval_results', '__pycache__', '.git'}
SKIP_FILES = {'crc32.txt', '.gitkeep'}


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            chunk = f.read(CHUNK)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def fetch_remote_hashes(repo_id: str, revision: str = "main") -> dict:
    """Return {filename: {hash, lfs, size, oid}} from HF API tree endpoint."""
    url = f"https://huggingface.co/api/models/{repo_id}/tree/{revision}"
    req = urllib.request.Request(url, headers={"User-Agent": "hf-hash-audit/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            tree = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"  HTTP {e.code} for {repo_id} ({revision}) — skipping", file=sys.stderr)
        return {}
    result = {}
    for entry in tree:
        lfs = entry.get("lfs")
        if lfs:
            h = lfs.get("oid") or lfs.get("sha256", "")
            if h:
                result[entry["path"]] = {"hash": h.removeprefix("0000000000000000"), "lfs": True, "size": entry.get("size")}
        else:
            oid = entry.get("oid")
            if oid:
                result[entry["path"]] = {"hash": None, "lfs": False, "oid": oid, "size": entry.get("size")}
    return result


def discover_models(root: str, model_filter: str = None) -> list[str]:
    """Find model dirs (owner/name/) and return as 'owner/name'."""
    models = []
    root = Path(root)
    for owner in sorted(root.iterdir()):
        if not owner.is_dir():
            continue
        for name in sorted(owner.iterdir()):
            if not name.is_dir():
                continue
            repo = f"{owner.name}/{name.name}"
            if model_filter and repo != model_filter:
                continue
            models.append(repo)
    return models


def scan_local_files(model_path: Path) -> list[str]:
    """Return relative file paths, skipping cache/dot dirs."""
    files = []
    for dirpath, dirnames, filenames in os.walk(model_path):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if fn in SKIP_FILES:
                continue
            rel = os.path.relpath(os.path.join(dirpath, fn), model_path)
            files.append(rel)
    return sorted(files)


def audit(root: str, model_filter: str = None, check_only: bool = False, json_out: bool = False, quick: bool = False):
    root = Path(root).resolve()
    models = discover_models(root, model_filter)
    if not models:
        print(f"No models found under {root}" + (f" (filter: {model_filter})" if model_filter else ""))
        return

    all_results = []
    total_files = 0
    total_ok = 0
    total_mismatch = 0
    total_missing_remote = 0
    total_missing_local = 0

    for repo_id in models:
        model_path = root / repo_id
        if not model_path.is_dir():
            continue

        print(f"\n{'='*60}")
        print(f"  {repo_id}")
        print(f"{'='*60}")

        remote = fetch_remote_hashes(repo_id)
        if not remote:
            print(f"  No remote info — skipping")
            continue

        local_files = scan_local_files(model_path)
        all_files = sorted(set(list(remote.keys()) + local_files))
        model_ok = 0
        model_bad = 0
        model_miss_remote = 0
        model_miss_local = 0
        details = []

        for fname in all_files:
            local_path = model_path / fname
            info = remote.get(fname)
            if info is None:
                if not check_only:
                    print(f"  [NO REF]  {fname}")
                model_miss_remote += 1
                details.append({"file": fname, "status": "no_remote_ref"})
                continue
            if not local_path.is_file():
                print(f"  [MISSING] {fname}")
                details.append({"file": fname, "status": "missing_local", "remote_sha256": info.get("hash")})
                model_miss_local += 1
                continue

            if info.get("lfs") and info.get("hash"):
                # Fast check: size mismatch = corrupted/truncated file
                remote_size = info.get("size")
                if remote_size is not None:
                    local_size = local_path.stat().st_size
                    if local_size != remote_size:
                        print(f"  [SIZE]   {fname} local={local_size} remote={remote_size}")
                        details.append({"file": fname, "status": "size_mismatch", "local_size": local_size, "remote_size": remote_size, "remote_sha256": info["hash"]})
                        model_bad += 1
                        continue

                local_hash = sha256_file(str(local_path)) if not quick else "skipped"
                if quick:
                    if not check_only:
                        print(f"  [SIZE OK] {fname}")
                    model_ok += 1
                    details.append({"file": fname, "status": "size_ok"})
                elif local_hash == info["hash"]:
                    if not check_only:
                        print(f"  [OK]      {fname}")
                    model_ok += 1
                    details.append({"file": fname, "status": "ok", "sha256": local_hash})
                else:
                    print(f"  [MISMATCH] {fname}")
                    print(f"             local  0x{local_hash}")
                    print(f"             remote 0x{info['hash']}")
                    model_bad += 1
                    details.append({"file": fname, "status": "mismatch", "local_sha256": local_hash, "remote_sha256": info["hash"]})
            else:
                # Non-LFS file — just track existence (size check could be added)
                if not check_only:
                    print(f"  [OK]      {fname} (non-lfs)")
                model_ok += 1
                details.append({"file": fname, "status": "ok", "lfs": False})

        total_files += len(all_files)
        total_ok += model_ok
        total_mismatch += model_bad
        total_missing_remote += model_miss_remote
        total_missing_local += model_miss_local

        all_results.append({
            "model": repo_id,
            "total": len(all_files),
            "ok": model_ok,
            "mismatch": model_bad,
            "missing_local": model_miss_local,
            "no_remote_ref": model_miss_remote,
            "details": details if json_out else None
        })

        print(f"\n  Summary: {model_ok} ok, {model_bad} mismatch, {model_miss_local} missing, {model_miss_remote} no remote ref")

    # Final summary
    if json_out:
        print(json.dumps(all_results, indent=2))
    else:
        print(f"\n{'#'*60}")
        print(f"  TOTAL: {len(models)} models, {total_files} files")
        print(f"  OK: {total_ok}  |  MISMATCH: {total_mismatch}  |  MISSING: {total_missing_local}  |  NO REF: {total_missing_remote}")
        print(f"{'#'*60}")

    if total_mismatch > 0 or total_missing_local > 0:
        sys.exit(1)


def main():
    p = argparse.ArgumentParser(description="Verify HF model file hashes against remote API")
    p.add_argument("root", help="Path to huggingface.co root (e.g. /ssd/internet/huggingface.co/)")
    p.add_argument("--model", help="Single model to check (owner/name)")
    p.add_argument("--check", action="store_true", help="Only print mismatches (skip OK lines)")
    p.add_argument("--json", action="store_true", help="Output full results as JSON")
    p.add_argument("--quick", action="store_true", help="Only check file sizes — skip slow SHA256 hashes")
    args = p.parse_args()
    audit(args.root, args.model, args.check, args.json, args.quick)


if __name__ == "__main__":
    main()
