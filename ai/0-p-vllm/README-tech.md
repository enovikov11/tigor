# p-vllm

hf download unsloth/GLM-5.1-GGUF --include "UD-Q4_K_M/*" --local-dir /ssd/internet/huggingface.co/unsloth/GLM-5.1-GGUF

https://benchlm.ai/
https://opencode.ai/
https://docs.openhands.dev/sdk

https://github.com/NVIDIA/NemoClaw
https://github.com/nousresearch/hermes-agent
https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro

https://opencode.ai/docs/tools/
https://github.com/anomalyco/opencode/blob/c8ecd640220331ce7695d72ea8c618dd8909eab1/packages/opencode/src/session/prompt/default.txt

https://huggingface.co/Wan-AI/Wan2.2-T2V-A14B
https://github.com/comfy-org/ComfyUI

https://github.com/enovikov11/wpex

Current GPU inference stack for the RTX PRO box.

Production source of truth:
- NixOS/Compose definition: `../../infra/0-box/configuration.nix`
- General inference rules: `inference.md`
- Raw reference dumps: `qwen-122-docs.md`, `qwen-80-docs.md`, `vllm-docs.md`

## Current Stack

`configuration.nix` generates `/etc/podman-compose/compose.yaml` and runs it through `podman-compose.service`.

| Service | Port | Image | Data |
|---|---:|---|---|
| `p-vllm` | 8000 | `docker.io/vllm/vllm-openai:nightly` | `/ssd/internet/huggingface.co:ro`, `/ssd/private/podman/p-vllm-cache` |
| `p-chat` | 8080 | `ghcr.io/open-webui/open-webui:main` | `/hdd/private/podman/p-chat` |

Current important details:
- The service is root-owned system Podman, not the old dedicated rootless `podman` user design.
- The current Compose YAML has no explicit `internal: true` network. If egress isolation matters, add it in `configuration.nix`; do not rely on app flags.
- `p-vllm` uses NVIDIA CDI (`nvidia.com/gpu=all`), `shm_size: 16g`, `no-new-privileges:true`, and `cpuset: "0-63"`.
- `p-chat` has `WEBUI_AUTH=false`, disables Ollama, and points to `http://p-vllm:8000/v1`.

Ops on box:

```sh
systemctl status podman-compose
journalctl -f -a -u podman-compose
podman ps -a
podman logs -f p-vllm
```

## Current Model

Current served model in `configuration.nix`: `Qwen3.6-27B-FP8`.

```text
/huggingface.co/Qwen/Qwen3.6-27B-FP8 --served-model-name Qwen3.6-27B-FP8 --host 0.0.0.0 --port 8000 --max-model-len 262144 --gpu-memory-utilization 0.95 --kv-cache-dtype fp8 --optimization-level 3 --performance-mode interactivity --reasoning-parser qwen3 --enable-auto-tool-choice --tool-call-parser qwen3_coder --speculative-config '{"method":"qwen3_next_mtp","num_speculative_tokens":2}'
```

Useful Qwen3.x defaults:
- Use vLLM nightly for new architectures until stable catches up.
- Keep context at 128k+ when possible; native context is 262,144 tokens.
- Use `--reasoning-parser qwen3`.
- For tool calls: `--enable-auto-tool-choice --tool-call-parser qwen3_coder`.
- For MTP: prefer `--speculative-config '{"method":"mtp","num_speculative_tokens":2}'`; `qwen3_next_mtp` is the older alias still present in current config.
- Thinking is on by default. Disable per request with `extra_body.chat_template_kwargs.enable_thinking = false`; do not depend on `/think` or `/nothink`.

Debug mode: temporarily add `VLLM_LOGGING_LEVEL=DEBUG` and `--enable-log-requests`.

## Measured / Actionable Learnings

Keep long tuning rules in `inference.md`. Highest-value reminders:
- RTX PRO 6000 Blackwell has 96 GB VRAM and supports fp8 KV cache, FlashAttention, and CUDA graphs.
- `--gpu-memory-utilization` caps model weights + runtime overhead + KV cache, not only KV cache.
- `--max-model-len` is a per-request cap, not a vLLM memory lever.
- MTP matters when CUDA graphs do not fit.
- Measure direct API throughput before blaming the model; UI/streaming can understate backend speed.
- Avoid `--trust-remote-code` for community model repos unless there is a proven need.
- Persisting `/root/.cache/vllm` saves cold-start compile time, not steady-state tokens/sec.

## Qwen3.6-35B-A3B Experiment

Host path: `/ssd/internet/huggingface.co/Qwen/Qwen3.6-35B-A3B`

BF16 weights are about 67.0 GiB. On 96 GB VRAM it should fit with fp8 KV cache if `--gpu-memory-utilization` stays below all-memory settings such as `0.99`; `0.95` leaves headroom for KV cache, CUDA/PyTorch overhead, MTP, and vision overhead.

Direct API baseline before adding `--optimization-level 3 --performance-mode interactivity`: 8,876 completion tokens in 98.81s, about 89.8 tok/s, measured with non-streaming curl to `http://10.69.42.2:8000/v1/chat/completions`.

Interpretation: `nvidia-smi dmon` showed about 51-53% SM and 34-35% memory utilization with about 94 GiB VRAM used, pointing to kernel/runtime/sparse-MoE limits rather than HBM saturation. Do not switch to dense 27B just to make GPU utilization look prettier.

Fallbacks if BF16 + 262k OOMs:
- Add `--language-model-only` for text-only serving.
- Reduce to `--max-model-len 131072`.
- Try official `Qwen/Qwen3.6-35B-A3B-FP8`.

## Qwen3.5-122B-A10B Experiment

Non-prod but high-value because it explains why the current stack favors models where CUDA graphs fit.

Tested path:

```text
/huggingface.co/cyankiwi/Qwen3.5-122B-A10B-AWQ-4bit
```

Workable config:

```yaml
image: vllm/vllm-openai:nightly
command: /huggingface.co/cyankiwi/Qwen3.5-122B-A10B-AWQ-4bit --served-model-name qwen3.5-122b --host 0.0.0.0 --port 8000 --max-model-len 65536 --gpu-memory-utilization 0.97 --skip-mm-profiling --kv-cache-dtype fp8 --enforce-eager --override-generation-config '{"max_new_tokens":16384}' --enable-auto-tool-choice --tool-call-parser qwen3_coder --reasoning-parser qwen3 --speculative-config '{"method":"mtp","num_speculative_tokens":3}'
```

Key numbers:
- Model weights: 74.67 GiB including MTP draft model.
- PyTorch allocated: about 88.7 GiB with enforce-eager and no torch.compile.
- KV cache: about 7.8 GiB, roughly 156k fp8 tokens.
- MTP rejection sampler: about 970 MiB outside KV budget.
- Enforce-eager without MTP: 14 tok/s.
- Enforce-eager plus MTP x2: 33 tok/s.
- FlashInfer GDN prefill regressed to 29 tok/s; use default Triton/FLA.

Conclusion: config tuning ceiling looked like 40-50 tok/s. Getting 100+ tok/s likely requires a different model where CUDA graphs fit.

## Wan2.2 Video Gen

Wan2.2 T2V-A14B fits on RTX PRO 6000 single GPU at about 54 GiB bf16 weights. Preferred workflow is ComfyUI on p-devbox for prompt iteration; native fallback:

```sh
python generate.py --task t2v-A14B --size 1280*720 --ckpt_dir ./Wan2.2-T2V-A14B
```

Safe fallback flags: `--offload_model True --convert_model_dtype --t5_cpu`.

Links:
- https://wan.video/blog/wan2.2
- https://github.com/Wan-Video/Wan2.2
- https://huggingface.co/Wan-AI/Wan2.2-T2V-A14B

No open video model here generates audio natively. Practical path: Wan2.2 video, MMAudio V2A audio, ffmpeg mux.

## llama.cpp on RTX 3090

RTX 3090 has 24 GiB VRAM. llama.cpp overhead is hundreds of MiB, while vLLM/PyTorch costs several GiB. On tight VRAM, llama.cpp can keep much more room for context and is usually better for single-user GGUF chat.
