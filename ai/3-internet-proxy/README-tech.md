# internet-proxy

Content-only internet diode for AI agents.

## Problem

LLMs cannot reliably separate control and data planes. An agent with unrestricted internet access is one prompt injection away from:
- Sending spam or scam messages
- Establishing a reverse shell
- Posting bomb threats or other harmful content
- Participating in botnets

## Idea

A hard-wired read-only proxy that sits between an AI agent and the internet. The agent requests content by type and identifier; the proxy fetches it through purpose-built, content-stripping adapters and returns only the text/data — never raw HTML, never executable content, never arbitrary URLs.

The proxy is a **data diode**: it can only read, never act. There is no general HTTP fetch endpoint.

## Supported content sources

| Source | Tool | Endpoint type |
|---|---|---|
| Web search | SearXNG | `GET /search?q=...` → titles + snippets |
| Web articles | Mercury Parser (Postlight) / Mozilla Readability / trafilatura | `GET /article?url=...` → extracted text |
| YouTube videos | yt-dlp | `GET /youtube?id=...` → transcript / metadata |
| Wikipedia | Wikipedia API | `GET /wikipedia?title=...` → article text |
| Reddit posts | PRAW (Reddit API) | `GET /reddit?url=...` → post + top comments |
| GitHub repos | GitHub API | `GET /github?repo=owner/repo` → README + file tree |
| Telegram channels | Pyrogram / MTProto (read-only session) | `GET /telegram?channel=...&limit=N` → recent posts text |
| PyPI packages | devpi (PyPI mirror) | read-only mirror |
| npm packages | Sonatype Nexus OSS / JFrog Artifactory OSS | read-only mirror |
| apt packages | apt-cacher-ng | read-only cache |

## Design constraints

- No raw HTTP proxy — all endpoints are typed and strip non-content
- No cookies, sessions, or state stored on behalf of callers
- No write operations to any external service
- Network-level isolation: proxy container on `internal: true` network toward the agent, only the proxy itself reaches the internet
- Response format: plain text or structured JSON — never raw HTML or binary

## Architecture

```
Agent (air-gapped net) → internet-proxy API → per-adapter fetchers → internet
                                ↓
                      content-only response
                      (text / JSON / metadata)
```

The agent communicates only with the proxy API. The proxy has no general-purpose fetch — each adapter is a narrow pipe hardwired to one source type.

## TODO

- [ ] FastAPI skeleton with typed endpoints
- [ ] SearXNG adapter (self-hosted instance or public)
- [ ] Article extraction: try trafilatura first, fall back to Mercury Parser
- [ ] YouTube: yt-dlp transcript extraction, no video download
- [ ] Wikipedia: official API wrapper
- [ ] Reddit: PRAW read-only (no auth required for public posts)
- [ ] GitHub: REST API, read-only token
- [ ] Telegram: Pyrogram with a read-only user session, public channels only, strip media
- [ ] Package mirrors: apt-cacher-ng, devpi, Nexus/Artifactory evaluation
- [ ] Docker Compose service with `internal: true` network toward agent
- [ ] Rate limiting and request logging for audit trail
