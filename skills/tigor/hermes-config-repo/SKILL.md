---
name: hermes-config-repo
description: Manage the ~/.hermes git repo (hermes-config) — what's tracked vs gitignored, secret sanitization for publication, and the .env/auth.json/secrets/ isolation pattern.
category: infrastructure
tags:
  - hermes
  - git
  - config
  - secrets
  - publication
---

# Hermes Config Repo

The `~/.hermes/` directory is a git repo (`hermes-config`) that tracks Hermes configuration, skills, dashboards, and scripts. It is intended for publication. Secrets must never live in tracked files.

## Repo Structure

### Tracked (committed)

| Path | Content |
|------|---------|
| `config.yaml` | Hermes configuration (IPs are NOT secrets — committed as-is) |
| `SOUL.md` | Agent identity prompt |
| `dashboards/` | HTML dashboards, test files, reports |
| `scripts/` | Python utilities, download scripts |
| `skills/` | Skill library (SKILL.md + references/ + scripts/ + templates/) |
| `.gitignore` | Rules for what to exclude |

### .gitignore strategy

**Whitelist approach** — `*` at top ignores everything; tracked files are explicitly allowed with `!` rules. New files are ignored by default and only enter tracking when explicitly un-ignored.

**What's tracked** (explicitly `!`-allowed):
- `config.yaml`, `SOUL.md`, `.gitignore`
- `cron/jobs.json` — job definitions
- `dashboards/**`
- `scripts/**`
- `memories/MEMORY.md`
- `hermes-agent` (git submodule, mode 160000)
- `skills/` (parent dir) + `skills/tigor/**` (user-only custom skills)

**User custom skills live ONLY in `skills/tigor/`.** All other `skills/` contents are bundled or third-party and must remain gitignored. Do not add other skill paths to `.gitignore` — they will be ignored by `*`.

**What's implicitly ignored** (caught by `*`):
- Secrets: `.env`, `auth.json`, `auth.lock`, `secrets/`
- Runtime: `sessions/`, `state/`, `*.db`, `*.lock`, `*.pid`, `gateway/`, `kanban/`, `cache/`, `logs/`, `channel_directory.json`, `processes.json`, `*.cache.json`, `.hermes_history`, `.update_check`, `.skills_prompt_snapshot.json`
- Hermes-internal: `skills/.curator_state`, `skills/.bundled_manifest`, `skills/.usage.json`
- Heavy dirs: `tigor/`, `tigor.worktrees/`, `tigor-no-ai/`, `tigor-no-ai.worktrees/`, `services/forgejo/`, `bin/`, `node/`, `lsp/`
- Cron runtime: `cron/output/`, `cron/executions.db`, `cron/ticker_*`, `cron/.hb_*.tmp`

**Candidates** (commented-out `!` rules at bottom of `.gitignore`, uncomment to track):
- `config.yaml.bak`, `.env.example`, `auth.json.example`, `README.md`, `CHANGELOG.md`, `memories/*.md`, `cron/output/`, `skills/spec-to-code/**`

## Golden Rules

1. **Files stay in-place** — no symlinks, no separate data directories. Config files live in `~/.hermes/` and are tracked in git.
2. **Secrets isolated** — actual secrets go in `.env`, `auth.json`, or `secrets/`. Never hardcoded in tracked files.
3. **Sanitize before commit** — tokens, passwords, API keys replaced with placeholders in tracked files. IPs are NOT sanitized — they are committed as-is.
4. `redact_secrets: true` in config.yaml — never set to false in the committed version.
5. `channel_directory.json` is gitignored — contains Telegram chat IDs (PII).

## Sanitization Workflow

When preparing the repo for publication or after adding new files:

### 1. Find secrets

```bash
cd ~/.hermes
# Internal IPs
grep -rn '10\.67\.69\.' config.yaml SOUL.md skills/ scripts/ dashboards/ 2>/dev/null
# Tokens, passwords, API keys
grep -rniE 'password|api[_-]?key|secret|token|bearer' skills/ scripts/ dashboards/ config.yaml SOUL.md 2>/dev/null
```

### 2. Replace with placeholders (tokens only — NOT IPs)

```bash
# Hardcoded tokens → placeholders
sed -i 's|hf_ACTUAL_TOKEN|hf_TOKEN_PLACEHOLDER|g' skills/ scripts/
```

**CRITICAL: DO NOT replace internal IP addresses with placeholders.** IPs like `10.67.69.2` are not secrets — they are committed as-is. Replacing them with `INFERENCE_HOST` breaks config at runtime and the user explicitly forbade this.

### 4. Remove bundled skills from tracking

`skills/.bundled_manifest` lists all Hermes-bundled skills as `name:hash`. To clean the repo so only user's custom skills remain tracked:

```bash
cd ~/.hermes
# List bundled skills
cat skills/.bundled_manifest | cut -d: -f1
# Find each on disk
find skills/ -maxdepth 3 -type d -name "<skill_name>"
# Add to .gitignore (category or specific skill dir)
git rm --cached -r skills/<category>/<skill>/
# Also remove internal files
git rm --cached skills/.usage.json skills/.bundled_manifest
```

Categories where ALL skills are bundled can be gitignored entirely (e.g. `skills/creative/`). Mixed categories (like `infrastructure/` or `mlops/`) need per-skill entries. User categories to NEVER ignore: `infrastructure/`, `computer-use/`, `dogfood/`, `hermes-desktop-plugins/`, `yuanbao/`.

### 5. Commit and push

```bash
cd ~/.hermes
git add -A
git commit -m "Sanitize for publication: redact tokens, expand .gitignore"
git push forgejo main
```

## Forgejo Remote

The repo lives at `http://forgejo:3000/hermes/hermes-config` (Forgejo container, DNS name `forgejo`).
Credentials are embedded directly in the URL:

```
origin  http://hermes:polio-paramedic-dweeb@forgejo:3000/hermes/hermes-config.git
```

Forgejo user: `hermes`, password: `polio-paramedic-dweeb` (admin access).

**`hermes-config` exists ONLY on Forgejo, by design** — it is not published to GitHub.

### VPS paths

On the VPS (hermes user, uid=10000, HOME=/opt/data/home):
- Working tree: `/opt/data/hermes-config/` (cloned from Forgejo)
- The original `~/.hermes/` (at `/root/.hermes/`) is the Hermes runtime config — root-owned, not the git working tree.

## Pitfalls

- **Don't move files to a separate directory with symlinks** — user rejected this approach. Keep everything in `~/.hermes/`, sanitize in-place.
- **`channel_directory.json` looks like config but contains chat IDs** — gitignore it, don't commit.
- **`config.yaml.bak.*` files** — check if gitignored. They may contain old secrets.
- **Skills reference internal IPs in examples** — sanitize those too, not just config.yaml.
- **Hardcoded HF tokens in download scripts** — common pattern, always grep for `hf_` prefix.
- **NEVER replace IP addresses with placeholders** — IPs are not secrets. The user explicitly forbade replacing `10.67.69.x` with `INFERENCE_HOST` or similar. Doing so breaks config at runtime.
- **`skills/.bundled_manifest` and `.usage.json` are Hermes-internal** — they track bundled skill hashes and usage stats. Gitignore them and remove from tracking.
- **`git rm --cached` aborts on first bad path** — even with exit code 0, a single non-existent pathspec (e.g. `skills/hermes-agent/` that isn't tracked) causes the entire batch to abort silently. ALL files remain tracked. Always verify with `git ls-files -- skills/` after the command before committing. Or verify each path exists first: `for p in paths; do git ls-files -- "$p" | grep -q . || echo "SKIP: $p"; done`.
- **`skills/.curator_state` is Hermes-internal** — gitignore it. Also `.usage.json` and `.bundled_manifest`.
- **`memories/MEMORY.md` IS tracked** — it's the user's persistent memory (compact, ~14 lines). Only `memories/*.lock` is gitignored.
- **`.gitignore` uses whitelist (`*` + `!` rules)** — ignore everything by default, explicitly allow tracked files. Never revert to blacklist. Comments are allowed for section markers and candidates.
- **`hermes-agent` is a submodule (mode 160000)** — `!hermes-agent` keeps it tracked despite `*`. May show as `?` in `git status` — that's cosmetic; verify with `git ls-files -s hermes-agent`.
- **Bundled skill categories can be gitignored as whole directories** — when ALL skills in a category are bundled (e.g. `skills/creative/`, `skills/mlops/`), use `skills/<category>/` in `.gitignore` rather than per-skill entries. This is cleaner and survives future skill additions within the category.
- **User-only categories to never ignore** — `infrastructure/`, `computer-use/`, `dogfood/`, `hermes-desktop-plugins/`, `yuanbao/` contain custom skills that must stay tracked.
