# tigorc — Deterministic Markdown-to-Code Compiler with Local LLM (v0.1)

## Yes, it can compile itself, usage: run "bash README.md" (this is also a valid python code)

## Stage 0: tigorc bootstrap (GPU mode)

""":"    
export TIGORC_MODEL="ggml-org/Qwen2.5-1.5B-Instruct-GGUF:Q4_K_M"

exec bash -c 'python3 README.md | docker run --rm --name tigorc-llama --gpus all -v ./README.md:/input/README.md:ro -v tigorc-llama-cache:/root/.cache ghcr.io/ggml-org/llama.cpp:light-cuda -hf $TIGORC_MODEL -f /input/README.md --n-gpu-layers 999 --single-turn --no-display-prompt --no-show-timings --log-disable -n 512 --seed 42'  

## How tigorc is useful?

- We store not implementation, but compressed version of a code
- Intelligence is a compression, we intentionally skip boilerplate
- Prompt as a source allows you change underlying tech easily
- It makes shuffling architectual frameworks and patterns delightful to explore
- Codebase do not rots in a traditional sense, from compatibility layers
- When spec is semantic enough, switching programming language not an issue

## Stage 1: tigorc source prompt

Please output a python code that being passed a markdown file, generates a project of files and puts them to `generated-not-edit` folder

### How determinism is achieved

- Model weights are pinned and checked by sha256
- Model seed is pinned

### Architecture requirements

tigorc.py == README.md before PROMPT_PAYLOAD_CUTOFF_POINT + Stage0(README.md)
Stage2(tigorc.py) == tigorc.py

":"""
## Stage 2: tigorc compiler python code

import argparse

print("123")  

# PROMPT_END
