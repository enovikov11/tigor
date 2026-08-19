# TODO ideas

- Make SSL e2e with pinning
- Log ram as different event
- Endpoint for models reset, unload, move inference to a separate class
- Make auth separate class
- Make simple page for tasks, API key handling, CORS

## Pre-launch

- Analyze code
- Write tests
- Publish repo and ask for review

## Launch

- Update telegram bot
- Update xecut
- Make a post
- Add tiers

# Post launch

- https://huggingface.co/zai-org/GLM-4.5
- Eliminate 

# Draft of readme for testing purposes

curl http://192.168.1.3:8080/v1/chat/completions-async -H "Content-Type: application/json" -H "Authorization: Bearer ${LLAMA_BEARER_TOKEN}" -d '{"model": "qwen3-235b", "messages": [{"role": "user", "content": "What do Zheka Tigor mean??"}]}'

llama_perf_context_print:        load time =    1057.54 ms
llama_perf_context_print: prompt eval time =     506.21 ms /     7 tokens (   72.32 ms per token,    13.83 tokens per second)
llama_perf_context_print:        eval time =    1156.03 ms /     9 runs   (  128.45 ms per token,     7.79 tokens per second)
llama_perf_context_print:       total time =    1678.05 ms /    16 tokens

s.t_load_ms, s.t_p_eval_ms, s.t_eval_ms, s.n_p_eval, s.n_eval
(1057.54, 506.212, 1156.031, 7, 9)


Data Retention Policy:
- Messages are RAM-only 1 day max
- Anonymous stats saved and stored indefinitely (task id, model name, token usage, timings)
- In case of abuse, network traffic may be logged for incident response purposes

Price: free

SLA guarantees: not provided, for commercial access text me https://t.me/enovikov11

API key: request here https://t.me/the_tigor_bot or get anonymously from a Xecut Belgrade Hackspace door https://t.me/xecut_bg

API is idempotent: Your request is queued, you can and should periodically poll endpoint with same payload until got a result
