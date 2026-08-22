#!/bin/bash
set -e
export PYTHONUNBUFFERED=1
export HF_HUB_CACHE="/mnt/vm/.hf_cache"
exec /opt/data/hermes-agent/venv/bin/python /opt/data/scripts/hf_download/phase12.py
