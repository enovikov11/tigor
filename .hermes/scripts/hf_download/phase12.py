#!/usr/bin/env python3
"""HF downloads: cache on SSHFS via cache_dir param, VPS disk untouched."""
import os, sys, time, shutil, signal, glob

HF_TOKEN = "hf_TOKEN_PLACEHOLDER"
HF_CACHE = "/mnt/vm/.hf_cache"
VM = "/mnt/vm/huggingface.co"

from huggingface_hub import HfApi, login, hf_hub_download
login(token=HF_TOKEN)
api = HfApi()

def _handler(sig, frame):
    sys.exit(1)
signal.signal(signal.SIGTERM, _handler)

def gb(b): return b / (1024**3)

SKIP_FILES = {"README.md", "LICENSE", ".gitattributes", "ONNX.md"}
SKIP_PREFIX = {"docs/", "examples/", "tests/", "assets/", "src/", "media/", "scripts/"}
WANT_EXT = {".safetensors", ".bin", ".pth", ".gguf", ".json", ".jinja", ".yaml", ".yml", ".cfg", ".h5"}

REPOS = [
    ("google/gemma-4-31B-it", "google/gemma-4-31B-it", "gemma-4-31B-it"),
    ("heretic-org/Qwen3.8-27B-heretic-ara", "heretic-org/Qwen3.8-27B-heretic-ara", "qwen3.8-heretic-ara"),
    ("wangzhang/Qwen3.8-27B-abliterated", "wangzhang/Qwen3.8-27B-abliterated", "qwen3.8-abliterated"),
    ("trohrbaugh/gemma-4-31b-it-heretic-ara", "trohrbaugh/gemma-4-31b-it-heretic-ara", "gemma-heretic-ara"),
    ("wangzhang/gemma-4-31B-it-abliterated", "wangzhang/gemma-4-31B-it-abliterated", "gemma-abliterated"),
]

def get_files(repo_id):
    files = list(api.list_repo_files(repo_id))
    return [f for f in files
            if f not in SKIP_FILES
            and not any(f.startswith(p) for p in SKIP_PREFIX)
            and any(f.endswith(e) for e in WANT_EXT)]

def clean_cache(fname):
    """Remove downloaded file from cache to free space."""
    for root, _, files in os.walk(HF_CACHE):
        for f in files:
            if f == fname and not f.endswith((".lock", ".metadata")):
                fp = os.path.join(root, f)
                try:
                    os.remove(fp)
                    return os.path.getsize(fp) if False else True
                except:
                    pass
    return False

def dl(repo_id, vm_path, label):
    target = f"{VM}/{vm_path}"
    os.makedirs(target, exist_ok=True)
    files = get_files(repo_id)
    total_dl = 0; start = time.time()
    print(f"\n{'='*60}\n{label} ({len(files)} files)\n{'='*60}", flush=True)
    for i, f in enumerate(files):
        out = os.path.join(target, f)
        if os.path.exists(out) and os.path.getsize(out) > 1024:
            print(f"  [{i+1}/{len(files)}] {f} (exists)", flush=True)
            continue
        try:
            os.makedirs(os.path.dirname(out), exist_ok=True)
            dl_path = hf_hub_download(repo_id=repo_id, filename=f, cache_dir=HF_CACHE)
            sz = os.path.getsize(dl_path)
            shutil.copy2(dl_path, out)
            if os.path.getsize(out) != sz:
                print(f"  WARN: size mismatch {f}", flush=True)
            # Clean cache file
            clean_cache(f)
            total_dl += sz
            t = time.time() - start
            sp = total_dl / t / (1024**3) if t > 0 else 0
            print(f"  [{i+1}/{len(files)}] {f} ({gb(sz):.1f}GB) | {gb(total_dl):.0f}GB | {sp:.1f} GB/s", flush=True)
        except Exception as e:
            print(f"  FAIL [{i+1}/{len(files)}] {f}: {e}", flush=True)
    print(f"  Done: {gb(total_dl):.0f}GB", flush=True)

if __name__ == "__main__":
    print(f"Start: {time.strftime('%H:%M:%S')} | cache={HF_CACHE}", flush=True)
    st = os.statvfs("/")
    print(f"VPS free: {st.f_bavail * st.f_frsize / 1e9:.0f}GB", flush=True)
    for repo_id, vm_rel, label in REPOS:
        dl(repo_id, vm_rel, label)
    print(f"\nDONE: {time.strftime('%H:%M:%S')}", flush=True)
