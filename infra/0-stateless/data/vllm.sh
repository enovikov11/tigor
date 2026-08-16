podman run --restart=unless-stopped -d --name vllm \
  --device nvidia.com/gpu=all \
  -e NVIDIA_VISIBLE_DEVICES=all \
  -e NVIDIA_DRIVER_CAPABILITIES=compute,utility \
  -e PYTORCH_ALLOC_CONF=expandable_segments:True \
  -v /ssd/internet/huggingface.co:/huggingface.co:ro \
  -v /root/data/vllm-cache:/root/.cache/vllm \
  --shm-size 16g \
  -p 0.0.0.0:8000:8000 \
  docker.io/vllm/vllm-openai:nightly \
  /huggingface.co/Qwen/Qwen3.6-27B-FP8 \
  --served-model-name Qwen3.6-27B-FP8 \
  --host 0.0.0.0 \
  --port 8000 \
  --max-model-len 262144 \
  --max-num-seqs 512 \
  --gpu-memory-utilization 0.95 \
  --kv-cache-dtype fp8 \
  --optimization-level 3 \
  --performance-mode interactivity \
  --reasoning-parser qwen3 \
  --enable-auto-tool-choice \
  --tool-call-parser qwen3_coder \
  --speculative-config '{"method":"qwen3_next_mtp","num_speculative_tokens":2}'

