# p-agent

Telegram-facing coding-agent runner.

## Current Shape

The bot receives Telegram commands, runs `agent-task.sh`, clones the monorepo into a fresh `/work/<timestamp>` directory, runs the selected agent/model, commits the result, pushes a branch, and prints compare/cherry-pick links.

Main files:
- `main.py` - Telegram handlers, command menu, halt, timeout.
- `agent-task.sh` - clone, run, commit, push.
- `opencode.json` - OpenCode providers, model names, tool permissions.
- `test_security.py` - security-focused tests.

Model references are split across `opencode.json`, `agent-task.sh`, and `main.py` command descriptions. When the served model changes in `../../infra/0-box/configuration.nix`, update these together. Current known mismatch: `/qwen` is still named `Qwen3-Next 80B`, while `p-vllm` currently serves `Qwen3.6-27B-FP8`.

## Security Direction

An agent with unrestricted internet can be prompt-injected into spam, scam, reverse shells, botnet activity, or other externally visible actions.

Target direction:
- No Docker/podman socket inside the agent.
- Fresh disposable workspace per run.
- Network disabled by default.
- If internet data is needed, fetch through typed read-only adapters, not general browser/HTTP access.
- Allowed transition shape: trusted request -> untrusted content -> sandboxed execution.

Related design: `../3-internet-proxy/README.md`.

## Non-Prod Isolation Notes

k3s is too much surface area for this isolation problem. Candidates worth reusing ideas from:
- Firecracker microVMs
- gVisor/runsc
- Kata containers
- firecracker-containerd
- Ignite
- Nomad as an orchestrator option

Old Firecracker setup commands, if needed again:

```sh
sudo apt update
sudo apt install -y qemu-utils curl jq iproute2 iptables nftables util-linux strace tcpdump
sudo usermod -aG kvm box
```

```sh
su box
cd /hdd/firecracker/
wget https://github.com/firecracker-microvm/firecracker/releases/download/v1.14.1/firecracker-v1.14.1-x86_64.tgz
tar -xzf firecracker-v1.14.1-x86_64.tgz
wget https://cloud-images.ubuntu.com/noble/20260108/noble-server-cloudimg-amd64.img
qemu-img convert -f qcow2 -O raw noble-server-cloudimg-amd64.img ubuntu-20260108-rootfs.raw
qemu-img resize -f raw ubuntu-20260108-rootfs.raw 10G
/hdd/firecracker/firecracker-v1.14.1-x86_64 --api-sock /hdd/firecracker/ubuntu-20260108.sock
```

References:
- https://github.com/firecracker-microvm/firecracker-containerd
- https://github.com/weaveworks/ignite

## Python Patterns

### Test isolation

If code depends on a library only present in Docker, mock it before importing:

```python
from unittest.mock import MagicMock
import sys

_tg = MagicMock()
sys.modules.setdefault("telegram", _tg)
sys.modules.setdefault("telegram.ext", _tg)

import main
```

Use `setdefault` so re-imports in the same process do not double-register.

### Keep tests in sync with handler names

Renaming handlers, for example `handle_local` to `handle_flash`, requires updating tests and docs. AST checks do not catch runtime `AttributeError`s in tests.

### Subprocess timestamps

```python
subprocess.run(
    "bash agent-task.sh 2>&1 | ts '[%H:%M]'",
    shell=True,
    stdout=subprocess.PIPE,
    text=True,
    check=False,
)
```

`TimeoutExpired.stdout` can be `bytes` even with `text=True` if raised mid-stream:

```python
out = e.stdout.decode() if isinstance(e.stdout, bytes) else (e.stdout or "")
```

## Telegram Bot Startup Pattern

Python bots use `python-telegram-bot`. Reference: `telegram/yahonkbot/main.py`.

Use `post_init` to register `/` menu commands and notify admin:

```python
from telegram import BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler

async def on_startup(app):
    await app.bot.set_my_commands([BotCommand("cmd", "Description")])
    await app.bot.send_message(chat_id=ADMIN_ID, text="Bot started.")

app = ApplicationBuilder().token(TOKEN).post_init(on_startup).build()
app.add_handler(CommandHandler("cmd", handle_cmd))
app.run_polling(allowed_updates=["message"])
```
