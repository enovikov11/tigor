# HuggingFace Models to Download

Downloaded to VM via VPS+SSHFS pipeline. VM has no direct internet.

**Target:** `/ssd/vm/hermes/huggingface.co/` on VM (INFERENCE_HOST)
**Script:** `~/.hermes/scripts/hf_download/phase12.py` on VPS

---

## Already on VM (read-write)

| # | HF Repo | Path on VM | Size | Status |
|---|---|---|---|---|
| 1 | `Qwen/Qwen3.8-27B` | `/ssd/vm/hermes/huggingface.co/Qwen/Qwen3.8-27B/` | 52G | ✅ Complete (BF16) |
| 2 | `Qwen/Qwen3.8-27B-FP8` | `/ssd/vm/hermes/huggingface.co/Qwen/Qwen3.8-27B-FP8/` | 29G | ✅ Complete (FP8) |
| 3 | `MiniMaxAI/MiniMax-H3` | `/ssd/vm/hermes/huggingface.co/MiniMaxAI/MiniMax-H3/` | 19M | ⚠️ Partial |

## Already on VM (read-only, /ssd/internet)

Old models. GGUF quantizations. Pre-existing before 2026-08-18.

## Pending (not yet downloaded)

| # | Label | HF Repo | Est. Size | Priority | Files |
|---|---|---|---|---|---|
| 1 | gemma-4-31B-it | `google/gemma-4-31B-it` | ~90G (2x safetensors) | Phase 1 | 10 (2 safetensors + config/tokenizer) |
| 2 | qwen-heretic-ara | `heretic-org/Qwen3.8-27B-heretic-ara` | ~29G (FP8 base) | Phase 1 | 17 |
| 3 | qwen-abliterated | `wangzhang/Qwen3.8-27B-abliterated` | ~54G (BF16) | Phase 1 | 21 |
| 4 | gemma-heretic-ara | `trohrbaugh/gemma-4-31b-it-heretic-ara` | ~63G (BF16) | Phase 2 | 14 |
| 5 | gemma-abliterated | `wangzhang/gemma-4-31B-it-abliterated` | ~63G (BF16) | Phase 2 | 10 |

**Total pending:** ~299G across 5 repos (72 files)

## Tools for Abliteration

| # | Tool | Repo | Description |
|---|---|---|---|
| 1 | heretic | [p-e-w/heretic](https://github.com/p-e-w/heretic) | Framework for model ablation/alignment repair |
| 2 | abliterix | [wuwangzhang1216/abliterix](https://github.com/wuwangzhang1216/abliterix) | Abliteration pipeline for removing unwanted model behaviors |

## Abliterated Model Examples

| # | Model | HF Repo | Base | Size |
|---|---|---|---|---|
| 1 | Qwen3.6-27B abliterated | [wangzhang/Qwen3.6-27B-abliterated](https://huggingface.co/wangzhang/Qwen3.6-27B-abliterated) | Qwen3.6-27B | ~54G (BF16) |
| 2 | gemma-4-31B-it abliterated | [wangzhang/gemma-4-31B-it-abliterated](https://huggingface.co/wangzhang/gemma-4-31B-it-abliterated) | gemma-4-31B-it | ~63G (BF16) |

## Notes

- gemma-4-31B-it is gated — requires HF auth token
- All abliterated/derivative repos are based on Qwen3.8-27B or gemma-4-31B-it
- FP8 variants are half the size of BF16
