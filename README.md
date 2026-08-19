# Tigor AI Monorepo

> **Note:** Tigor AI Monorepo is being automatically edited by autonomous AI agent with human direction and agent self-feedback loops. It must not be relied upon as a security boundary or source of truth. Control is primarily retroactive, traceability is enforced by linear git history.

> **Note:** Tigor no AI Monorepo requires human review of all commits. It contains the authoritative specifications and security-critical code that enforces compartmentalization, virtualization, and ACLs and contains specs. 

## Legend
- **Priority**: `#` marks highly notable projects (coolness ≥ 8)
- **Priority**: `!` marks interesting but incomplete (coolness ≥ 6, < 50% completion)
- **Status**: `dead` = complete but obsolete/superseded

---

## 🤖 AI (14 projects)

| # | Project | Description | Done | Cool |
|---|---------|-------------|------|------|
| # | `0-bench` | Autonomous coding agent benchmark — 10 parallel slots, opencode loop, SIQ-1-35B | 85% | 9/10 |
|   | `0-llmchat` | Prototype Telegram chatbot with local LLM (character bot) | 35% | 5/10 |
|   | `0-p-agent` | Production Telegram coding agent — dispatches tasks, pushes review branches | 90% | 8/10 |
| # | `0-p-vllm` | GPU inference service (RTX PRO 6000 Blackwell) + vLLM tuning KB | 95% | 9/10 |
| # | `0-wan` | Telegram video generation bot (Wan2.2, text/image-to-video) | 95% | 9/10 |
|   | `2-box-roi` | ROI analysis: home server vs API costs, Qwen3-235B on CPU | 70% | 6/10 |
|   | `2-gpt-hotkeys` | ~~Chrome extension for ChatGPT shortcuts (obsolete, GPT-3.5 era)~~ | dead | 3/10 |
|   | `2-home-benchmark` | ~~M3 Max vs Vast.ai LLM benchmark (superseded)~~ | dead | 5/10 |
|   | `2-llama-server` | Over-engineered llama.cpp server: HMAC auth, rate limiting, 671B on CPU | 75% | 8/10 |
|   | `2-llm-hardware` | Comprehensive LLM hardware benchmark (15+ rigs, 10 models, public) | 90% | 8/10 |
|   | `3-beam-search` | Beam search into LLM probability space — security / hallucination research | 60% | 7/10 |
|   | `3-image-gen` | Local image generation experiments (Z-Image, Qwen-Image, SD) | 20% | 4/10 |
| ! | `3-internet-proxy` | Content-only internet diode for AI agents (design doc) | 10% | 6/10 |
|   | `3-vecsearch` | ~~Telegram semantic search bot (FAISS + OpenAI, dead)~~ | dead | 5/10 |

## 📊 Analytics (9 projects)

| # | Project | Description | Done | Cool |
|---|---------|-------------|------|------|
|   | `0-monero` | Monero mining profitability calculator + XMRig Dockerfile | 100% | 3/10 |
| # | `0-tech-talks` | Tech talk presentation + automated QA pipeline (Selenium+Claude) + video production | 100% | 8/10 |
|   | `2-belgrade-apartments` | Belgrade real estate: price-to-rent ratio + ML rent prediction + Vision verification | 50% | 7/10 |
|   | `2-mortality` | US SSA mortality "1 in N" heatmaps by age/gender | 100% | 7/10 |
|   | `2-raiffeisen-analytics` | Empty project shell | 0% | 1/10 |
| # | `2-stocks` | Quant finance: Black-Scholes, portfolios, market timing, Serbian bonds | 80% | 9/10 |
|   | `3-math` | Algorithm sandbox: Fibonacci in 5 langs (incl. X86-64 asm), string algorithms | 70% | 6/10 |
|   | `3-wolt-lowcarb` | Browser JS skeleton for Wolt API data extraction | 10% | 4/10 |
|   | `3-word-vectors` | GloVe word embedding analogy explorer | 60% | 7/10 |

## 🏗️ Infrastructure (6 projects)

| # | Project | Description | Done | Cool |
|---|---------|-------------|------|------|
| # | `0-box` | NixOS home AI workstation: vLLM + Podman, GPU passthrough, ZFS, UKI boot | 85% | 9/10 |
|   | `0-hermes` | Provision DigitalOcean droplet with Hermes Agent + Telegram | 90% | 6/10 |
|   | `0-macbook` | MacBook setup reference: Homebrew, GPG/YubiKey, VS Code | 100% | 3/10 |
| # | `0-stateless` | Stateless NixOS + diskless UKI VM images, XSL generator, GPU passthrough, SEV | 80% | 9/10 |
|   | `0-tgr` | VPS: Caddy, MariaDB, 3 TG bots, WireGuard VPN hub | 90% | 5/10 |
|   | `1-utils` | Utility toolbox: CI checks, SHA256 hashing, GitHub sync, Chia, C++ deduplicator | 70% | 5/10 |

## 🎮 Games (1 project)

| Project | Description | Done | Cool |
|---------|-------------|------|------|
| `3-rps-sim` | Browser physics sim: 100 bouncing 🪨📄✂️ eliminate each other | 100% | 6/10 |

## 📝 Specs (1 project)

| # | Project | Description | Done | Cool |
|---|---------|-------------|------|------|
| ! | `tigorc` | Self-compiling markdown spec → code via local LLM (prototype) | 10% | 8/10 |

---

## Summary

- **Total projects**: 31
- **Highly notable** (coolness ≥ 8): 12
- **Complete** (≥ 80%): 13
- **Dead/obsolete**: 3 (`2-gpt-hotkeys`, `2-home-benchmark`, `3-vecsearch`)
- **Empty shells**: 1 (`2-raiffeisen-analytics`)

## Top 5 (by coolness × completion)

1. **0-p-vllm** — GPU inference stack + vLLM knowledge base (95%, 9/10)
2. **0-wan** — Production video generation bot (95%, 9/10)
3. **2-stocks** — Quantitative finance toolkit (80%, 9/10)
4. **0-box** — NixOS AI workstation with ZFS/UKI (85%, 9/10)
5. **0-stateless** — Stateless NixOS + diskless VMs (80%, 9/10)
