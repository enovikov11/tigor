---
name: github-repo-inventory
description: "Scan GitHub repositories for a user/org, classify (fork/own, public/private), compare against monorepo structure, and identify migration candidates."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [github, repos, inventory, audit, monorepo, migration]
    related: [github-pr-workflow, github-repo-management, tigor-monorepo]
---

# GitHub Repo Inventory & Monorepo Audit

Scan all repositories belonging to a user and their organizations, classify them, and compare against monorepo directories.

## When to use

- User asks "what repos do I have and which are in the monorepo?"
- Auditing standalone repos for monorepo migration
- Finding orphaned repos or identifying fork-vs-own repos
- Checking if a user corrected your classification logic

## Prerequisites

- GitHub PAT stored in `git config --global github.token` (for server-side scan)
- For private repos + orgs: use the browser JS script in `scripts/gh-org-scan.js`
- Monorepo bare repos accessible (e.g. `~/.hermes/tigor/`)

## Step 1: Enumerate user repos (server-side, public only)

```bash
TOKEN=$(git config --global github.token)
curl -s -H "Authorization: token $TOKEN" \
  "https://api.github.com/users/<user>/repos?per_page=100" | \
  jq '[.[] | {name, fork, private, parent: .parent.full_name}]'
```

Paginate with `&page=2` if needed.

## Step 2: Classify each repo

- **Own repos** (`fork: false`) → pet projects, keep
- **Forks** → check if user has actual commits:
  ```bash
  curl -s -H "Authorization: token $TOKEN" \
    "https://api.github.com/repos/<user>/<repo>/commits?per_page=1" | \
    jq '.[0].author.login'
  ```
  Use `search/commits?q=repo:<user>/<repo>+author:<user>` for exact count.
- **Organizational forks** (parent is xecut-me, company org, etc.) → exclude as corporate
- **Profile repos** (`<user>/<user>`) → exclude
- **The monorepo itself** → exclude from comparison

## Step 3: Enumerate org repos (browser script)

Server-side API can't see user's org memberships via bot token. Use the browser script:

```bash
cat scripts/gh-org-scan.js
# Then paste into browser DevTools Console (F12) on github.com
```

Script prompts for PAT, iterates all orgs + all repos (private included), outputs table.

## Step 4: Compare against monorepo

List all projects at depth 2 in monorepo:

```bash
git -C /path/to/bare/repo ls-tree -d -r --name-only HEAD | \
  awk -F/ '{print $1"/"$2}' | sort -u
```

Search for standalone repo name in monorepo paths:

```bash
git -C /path/to/bare/repo ls-tree -r --name-only HEAD | \
  grep -iE '<repo_name>'
```

## Step 5: Report

Present results as a table:

| Repo | Description | In monorepo? | Path |
|---|---|---|---|
| `gravity` | Gravity simulator | ✅ Yes | `games/0-gravity` |
| `stun` | STUN server | ❌ No | — |

Mark as 🟡 Partial if content exists under a different name.

## Pitfalls

1. **Bot token has no org access** — `enovikov11-ai-agent` token returns empty org list. Use browser script instead.
2. **Forks can have zero user commits** — always check `search/commits` with author filter, not just `commits` endpoint.
3. **Commit author login can be null** — some commits use email-only authors. Fall back to `commit.author.name`.
4. **Monorepo projects may differ from repo names** — `NeuroImgBot` standalone vs `ai/3-image-gen` in monorepo. Check content, not just names.
5. **Bare repos need `ls-tree` not `find`** — `~/.hermes/tigor/` is bare, filesystem listing doesn't work.
6. **`ls-tree` truncates deep paths** — use `-r` for recursive, then `sed` or `awk` to extract depth-2 directories.
