# Tigor AI Monorepo

> **Note:** Tigor AI Monorepo is autonomously edited by an AI agent under human direction and self-feedback loops. It is not a security boundary or source of truth. Control is primarily retroactive, with traceability enforced by linear git history.

> **Note:** Tigor no AI Monorepo requires human review for all commits. It contains authoritative specifications and security-critical code enforcing compartmentalization, virtualization, ACLs and specifications to build AI code upon.

See also https://github.com/enovikov11/tigor-no-ai

## Highly Notable

| Project | Why |
|---------|-----|
| `specs/tigorc` | Self-compiling markdown → code via local LLM — deterministic compiler prototype |
| `infra/0-macbook` | Authoritative MacBook setup reference (moved to [tigor-no-ai](https://github.com/enovikov11/tigor-no-ai)) |

## Legend
- **#** — highly notable (coolness ≥ 8)
- **!** — interesting but incomplete (coolness ≥ 6, < 50%)
- **dead** — complete but obsolete/superseded

---

## 🤖 AI (14 projects)

| # | Project | Description | Done | Cool |
|---|---------|-------------|------|------|
| # | `0-bench` | Autonomous coding agent benchmark — 10 parallel slots, opencode loop | 85% | 9/10 |
|   | `0-llmchat` | Prototype Telegram chatbot with local LLM (character bot) | 35% | 5/10 |
|   | `0-p-agent` | Production Telegram coding agent — dispatches tasks, review branches | 90% | 8/10 |
| # | `0-p-vllm` | GPU inference service (RTX PRO 6000 Blackwell) + vLLM tuning KB | 95% | 9/10 |
| # | `0-wan` | Telegram video generation bot (Wan2.2, text/image-to-video) | 95% | 9/10 |
|   | `2-box-roi` | ROI analysis: home server vs API costs, Qwen3-235B on CPU | 70% | 6/10 |
|   | `2-gpt-hotkeys` | ~~Chrome extension for ChatGPT shortcuts (obsolete)~~ | dead | 3/10 |
|   | `2-home-benchmark` | ~~M3 Max vs Vast.ai LLM benchmark (superseded)~~ | dead | 5/10 |
|   | `2-llama-server` | Over-engineered llama.cpp server: HMAC auth, rate limiting, 671B on CPU | 75% | 8/10 |
|   | `2-llm-hardware` | LLM hardware benchmark (15+ rigs, 10 models, public) | 90% | 8/10 |
|   | `3-beam-search` | Beam search into LLM probability space — security / hallucination research | 60% | 7/10 |
|   | `3-image-gen` | Local image generation experiments (Z-Image, Qwen-Image, SD) | 20% | 4/10 |
| ! | `3-internet-proxy` | Content-only internet diode for AI agents (design doc) | 10% | 6/10 |
|   | `3-vecsearch` | ~~Telegram semantic search bot (FAISS + OpenAI, dead)~~ | dead | 5/10 |

## 📊 Analytics (9 projects)

| # | Project | Description | Done | Cool |
|---|---------|-------------|------|------|
|   | `0-monero` | Monero mining profitability calculator + XMRig Dockerfile | 100% | 3/10 |
|   | `0-tech-talks` | Tech talk presentation + automated QA pipeline + video production | 100% | 8/10 |
|   | `2-belgrade-apartments` | Belgrade real estate: price-to-rent ratio + ML rent prediction | 50% | 7/10 |
|   | `2-mortality` | US SSA mortality "1 in N" heatmaps by age/gender | 100% | 7/10 |
|   | `2-raiffeisen-analytics` | Empty project shell | 0% | 1/10 |
| # | `2-stocks` | Quant finance: Black-Scholes, portfolios, market timing, Serbian bonds | 80% | 9/10 |
|   | `3-math` | Algorithm sandbox: Fibonacci in 5 langs (incl. X86-64 asm) | 70% | 6/10 |
|   | `3-wolt-lowcarb` | Browser JS skeleton for Wolt API data extraction | 10% | 4/10 |
|   | `3-word-vectors` | GloVe word embedding analogy explorer | 60% | 7/10 |

## 🏗️ Infrastructure (3 projects)

> `infra/0-stateless` moved to [tigor-no-ai](https://github.com/enovikov11/tigor-no-ai)

| # | Project | Description | Done | Cool |
|---|---------|-------------|------|------|
| # | `0-box` | NixOS home AI workstation: vLLM + Podman, GPU passthrough, ZFS, UKI | 85% | 9/10 |
|   | `0-hermes` | Provision DigitalOcean droplet with Hermes Agent + Telegram | 90% | 6/10 |
|   | `0-tgr` | VPS: Caddy, MariaDB, 3 TG bots, WireGuard VPN hub | 90% | 5/10 |
|   | `1-utils` | Toolbox: CI checks, hashing, GitHub sync, Chia, C++ deduplicator | 70% | 5/10 |

## 🎮 Games (14 projects)

| # | Project | Description | Done | Cool |
|---|---------|-------------|------|------|
|   | `0-gravity` | Gravity simulation | TBD | TBD |
|   | `0-spherium` | Sphere physics demo | TBD | TBD |
|   | `0-tess-tac-toe.github.io` | Tic-Tac-Toe on GitHub Pages | 100% | 3/10 |
|   | `2-mousemove` | Mouse movement visualizer | TBD | TBD |
|   | `3-rcon-maze` | RCON maze game | TBD | TBD |
|   | `3-rps-sim` | Browser physics: 🪨📄✂️ elimination | 100% | 6/10 |
|   | `3-world-generator` | Procedural world/terrain generation | 70% | 5/10 |
|   | `4-art-fractals` | Fractal art generator | TBD | TBD |
|   | `4-cluster-plot` | Cluster plot visualization | 100% | 4/10 |
|   | `4-codeworld` | Educational coding world | 100% | 4/10 |
|   | `4-morse` | Morse code tool | TBD | TBD |
|   | `4-qr-snake` | QR Snake game | TBD | TBD |
|   | `4-random-point` | Random point generator | TBD | TBD |
|   | `4-skyline-simulator` | Skyline simulation | TBD | TBD |

## 🔧 Maker (15 projects)

| # | Project | Description | Done | Cool |
|---|---------|-------------|------|------|
|   | `0-models` | 3D models library | TBD | TBD |
|   | `0-rf-cv-car` | RF-controlled car with computer vision | 80% | 6/10 |
|   | `0-rf-cv-car-controllers` | RF car controllers | TBD | TBD |
|   | `0-rpi-realtime` | Raspberry Pi realtime project | TBD | TBD |
| # | `0-t100-gpt` | 1963 Siemens Teleprinter + AI integration (Arduino, PCB, server) | 70% | 9/10 |
|   | `0-teletype` | Teletype project | TBD | TBD |
|   | `1-hackrf` | HackRF SDR project | TBD | TBD |
|   | `2-3d-scan` | 3D scanner | TBD | TBD |
|   | `2-platformio` | PlatformIO embedded projects | TBD | TBD |
|   | `3-Arduino` | Arduino sketches (ant_led, palladium, etc.) | TBD | TBD |
|   | `3-cctv` | CCTV surveillance system | 100% | 5/10 |
|   | `3-palladium` | Palladium project (android, arduino, server) | TBD | TBD |
|   | `4-arduino-bluetooth` | Arduino Bluetooth projects | TBD | TBD |

## 🔒 Security (5 projects)

| # | Project | Description | Done | Cool |
|---|---------|-------------|------|------|
|   | `0-libreboot` | Libreboot firmware research | TBD | TBD |
|   | `0-xkpass` | XKCD password manager | TBD | TBD |
|   | `2-bmc` | BMC management tools | TBD | TBD |
|   | `2-password` | Password utilities (SHA3, formats) | TBD | TBD |
|   | `2-poco-aes` | POCO AES implementation | TBD | TBD |
|   | `4-zerotrust` | Zero trust security architecture | 100% | 5/10 |

## 💬 Telegram Bots (10 projects)

| # | Project | Description | Done | Cool |
|---|---------|-------------|------|------|
|   | `0-101bot` | 101 bot | TBD | TBD |
|   | `0-101bot-prod` | 101 bot (production) | TBD | TBD |
|   | `0-no-inline` | Non-inline Telegram bot | TBD | TBD |
|   | `2-NeuroImgBot` | AI image generation bot | TBD | TBD |
|   | `2-memesearch` | Meme search bot | TBD | TBD |
|   | `2-stltoolbot` | STL tool bot | TBD | TBD |
|   | `2-the-tigor-bot` | Tigor bot | TBD | TBD |
|   | `4-MemeSearch-sharp` | Meme search (C# port) | TBD | TBD |
|   | `4-this-manool-doesnt-exist` | "This person doesn't exist" bot | TBD | TBD |

## 🌐 Web (11 projects)

| # | Project | Description | Done | Cool |
|---|---------|-------------|------|------|
|   | `0-eth-luck.github.io` | Ethereum luck checker | TBD | TBD |
|   | `0-hardwave` | Hardwave project | TBD | TBD |
|   | `0-stun` | STUN server | TBD | TBD |
|   | `0-tgr.rs` | tgr.rs website | TBD | TBD |
|   | `0-xkpass.github.io` | XKCD password web app | TBD | TBD |
|   | `1-sync-player` | Sync player | TBD | TBD |
|   | `1-tg-heatmap` | Telegram heatmap | TBD | TBD |
|   | `2-shri` | Shri web project | TBD | TBD |
|   | `2-udp-broadband-test` | UDP broadband test | TBD | TBD |
|   | `3-enovikov11.github.io` | Personal website | TBD | TBD |
|   | `4-redux-img` | Redux image project | TBD | TBD |

## 📝 Specs (1 project)

| # | Project | Description | Done | Cool |
|---|---------|-------------|------|------|
| ! | `tigorc` | Self-compiling markdown spec → code via local LLM (prototype) | 10% | 8/10 |

---

## Summary

- **Total projects**: ~94 across 10 domains
- **Top 5** (by coolness × completion): `0-p-vllm` (95%, 9/10), `0-wan` (95%, 9/10), `2-stocks` (80%, 9/10), `0-box` (85%, 9/10), `0-t100-gpt` (70%, 9/10)
- **AI-generated READMEs** marked with disclaimer; original deep-dives preserved as `README-tech.md`
- **Infra/0-stateless** moved to [tigor-no-ai](https://github.com/enovikov11/tigor-no-ai) (security-critical, human-reviewed only)
