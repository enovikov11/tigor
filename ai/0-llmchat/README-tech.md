# LLM Chat

Telegram chatbot (honkbot) that reads exported chat history and replies using local LLM inference.

## Data

Chat archives are loaded from a configured export directory (`public/`, `semi-private/`). Telegram JSON export format.

**Message format caveats:**
- `text` field can be a list of entity objects (`[{"type":"link","text":"..."}]`), not just a string
- Messages with photos/videos may have empty or missing `text` — include them with `"text": false`
- No username (`login`) field; only `from` (full name) and `from_id` (e.g. `user<TELEGRAM_USER_ID>`)
- `reply_to_message_id` is optional — absent if message doesn't reply

## Prompt Format (learned)

- System prompt + 100 messages sliding window with configurable skip offset
- Skip last N messages to control which message the bot replies to
- Each message: one JSON line with `id`, `author_name`, `text`, optionally `reply_to_id`
- Bot outputs one JSON object: `thinking`, `id`, `author_name: honkbot`, `text`, `reply_to_id`, `confidence_score`
- **Confidence calibration**: models default to 0.9+; must explicitly instruct ranges (0.9+ simple, 0.5-0.8 opinions/jokes, <0.5 uncertain)

## Inference

p-vllm on box, VPN IP `http://10.69.42.2:8000/v1/chat/completions`, model `Qwen3.6-27B-FP8`.

## Telegram API

Chat ID from export JSON `id` field → supergroup API needs `-100` prefix. E.g. `<TELEGRAM_CHAT_ID>` becomes `-100<TELEGRAM_CHAT_ID>`.

## Status

Prototype: `build_prompt.py` constructs prompt and sends to LLM. No Telegram bot yet.
