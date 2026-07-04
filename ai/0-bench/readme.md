# Qwen 3.6 27B dense 8bit vllm

started 2026-06-24T09:37:15Z
stopped 2026-06-24T16:28:05Z

## Slots

| slot | branch | topic | status | last_updated | commits | notes |
|------|--------|-------|--------|--------------|---------|-------|
| 1 | auto/slot-1-user-controls | rps-sim: pause/play toggle button | in-progress | 2026-06-25T12:00Z | 15 | guarded autoReplay — prevents game restart when user pauses during replay overlay countdown |
| 2 | auto/slot-2-input-validation | Add input validation and error handling in sync-player | done | 2026-06-24T23:30:00Z | 7 | all 3 message types (selected, canPlay, play) now have type guards, plus JSONDecodeError/InvalidMessage handling and finally-block crash fix |
| 3 | auto/slot-3-ws-leak | Fix workspace directory leak in agent-task.sh ERR trap | done | 2026-06-24T23:30:00Z | 1 | changed trap from ERR to EXIT — ERR only fires on non-zero exits, not signals, so timeouts left /work dirs accumulating |
| 4 | auto/slot-4-normalize-subprocess | Normalize subprocess stdout/stderr with _norm helper | done | 2026-06-25T00:15:00Z | 3 | helper created, all inline decode patterns in main.py replaced, README updated |
| 5 | auto/slot-5-chess-fix | Fix NameError (undefined game) and set.insert() crashes in chess game | done | 2026-06-25T00:15:00Z | 1 | fixed undefined `game` reference on line 23 and set.insert() on line 39 (no python available for validation) |
| 6 | auto/slot-6-fix-db-stats | Fix NameError in Index.print_db_stats (missing self, broken LMDB cursor) | done | 2026-06-24T10:28:20Z | 3 | added ZeroDivisionError guard in utils_dashboard.py print_db_stats — all db stats functions now safe with empty db |
| 7 | auto/slot-7-inline-log-fix | Harden vecsearch bot: protect Telegram API answer() calls | done | 2026-06-24T10:54:04Z | 17 | wrapping inline_query.answer() in try/except in both bots — all API calls now protected: search, reply_text, log, model loading, and inline_query answer |
| 8 | auto/slot-8-payload-sanitization | Fix command injection in p-agent PAYLOAD via shell chars | done | 2026-06-25T01:20Z | 3 | sanitization + negative test (bad chars stripped) + positive test (safe text preserved) — complete |
| 9 | auto/slot-9-broken-json-robustness | Add error handling for malformed JSON in benchmark log loader | done | 2026-06-25T03:00Z | 8 | 8 defensive checks: JSONDecodeError guard, isinstance guards for prompt_id, .get() for missing fields, OSError on open/write, IOError flush handling |
| 10 | auto/slot-10-printdb-guard | Add ZeroDivisionError guard in print_db_stats | done | 2026-06-24T11:37:19Z | 6 | all ZD guards complete: print_db_stats, token_limit_efficiency (empty + total_size), uniqs (empty array), plot_worktimes (empty stats) — both public and private bots fully guarded |

## Notes
- rps-sim.html: single-file HTML with no test toolchain; changes are conservative and verified by manual reading
- slot-1 had regressed to a 41-line skeleton; this commit restored the ~114 commits of working simulation logic
- No Python toolchain available to validate vecsearch changes; fixes are purely structural guards (divide-by-zero)

## Branches

https://github.com/tgr-rs/monorepo/compare/auto/slot-1-fix-except
https://github.com/tgr-rs/monorepo/compare/auto/slot-1-rps-fix
https://github.com/tgr-rs/monorepo/compare/auto/slot-1-rps-fix-2
https://github.com/tgr-rs/monorepo/compare/auto/slot-1-rps-restructure
https://github.com/tgr-rs/monorepo/compare/auto/slot-1-rps-sim
https://github.com/tgr-rs/monorepo/compare/auto/slot-1-user-controls
https://github.com/tgr-rs/monorepo/compare/auto/slot-10-printdb-guard
https://github.com/tgr-rs/monorepo/compare/auto/slot-2-input-validation
https://github.com/tgr-rs/monorepo/compare/auto/slot-3-ws-leak
https://github.com/tgr-rs/monorepo/compare/auto/slot-4-normalize-subprocess
https://github.com/tgr-rs/monorepo/compare/auto/slot-5-chess-fix
https://github.com/tgr-rs/monorepo/compare/auto/slot-6-fix-db-stats
https://github.com/tgr-rs/monorepo/compare/auto/slot-7-inline-log-fix
https://github.com/tgr-rs/monorepo/compare/auto/slot-8-payload-sanitization
https://github.com/tgr-rs/monorepo/compare/auto/slot-9-broken-json-robustness

## Verdicts

### slot-1-rps-fix

good: no
accepted: no

Rock Paper Scissors Simulator

it was unfinished file

some changes made, not works

### slot-1-rps-fix-2

good: no
accepted: no

Rock Paper Scissors Simulator

it was unfinished file

some changes made, not works

### slot-1-rps-restructure

good: kinda
accepted: maybe

some not useful changes to vector search

some changes to rock paper scisors

### slot-1-user-controls (accept)

good: yes
accepted: yes

some changes to rock paper scisors

### slot-10-printdb-guard

good: kinda
accepted: no

vector search additional guards

not sure change useful, no tests

### slot-2-input-validation

good: kinda
accepted: no

sync player

some guardrails

not sure change useful, no tests

### slot-3-ws-leak

good: no
accepted: no

stupid change on bash script, not useful

### slot-4-normalize-subprocess

good: kinda
accepted: no

agent normalizer

### slot-5-chess-fix

good: no
accepted: no

breaks code

### slot-6-fix-db-stats

good: kinda
accepted: no

useless guardrails on vector search

### slot-7-inline-log-fix

good: kinda
accepted: no

vector search guardrails, additional interface items

### slot-8-payload-sanitization

good: kinda
accepted: no

guardrails for agents bad chars

### slot-9-broken-json-robustness

good: kinda
accepted: no

useless guardrails on benchmark

# SIQ-1-35B MoE llama-cpp

started 2026-07-04T09:09:44Z
stopped 2026-07-04T16:21:32Z

## Slots

| slot | branch | topic | status | last_updated | commits | notes |
|------|--------|-------|--------|--------------|---------|-------|
| 1 | auto/slot-1 | Add input validation to handle_settimeout to reject 0 and excessively large timeouts | in-progress | 2026-07-04T17:05:00Z | 9 | Added float-string rejection test (30.5 → rejected via int() ValueError) |
| 2 | auto/slot-2-input-validation | Remove redundant empty-string TELEGRAM_BOT_TOKEN replace in handle_agent | done | 2026-07-04T16:30:00Z | 1 | Fixed: TELEGRAM_BOT_TOKEN env value is "" so replace("", "[MASKED]") corrupts output by inserting [MASKED] at every char position |
| 3 | auto/slot-3 | undecided | planning | - | 0 | |
| 4 | auto/slot-4 | undecided | planning | - | 0 | |
| 5 | auto/slot-5 | undecided | planning | - | 0 | |
| 6 | auto/slot-6 | undecided | planning | - | 0 | |
| 7 | auto/slot-7 | undecided | planning | - | 0 | |
| 8 | auto/slot-8 | undecided | planning | - | 0 | |
| 9 | auto/slot-9 | undecided | planning | - | 0 | |
| 10 | auto/slot-10 | undecided | planning | - | 0 | |

## Branches

https://github.com/tgr-rs/monorepo/compare/auto/slot-1
https://github.com/tgr-rs/monorepo/compare/auto/slot-1-53-unit-tests
https://github.com/tgr-rs/monorepo/compare/auto/slot-1-ai-wan-bot-test
https://github.com/tgr-rs/monorepo/compare/auto/slot-1-improved
https://github.com/tgr-rs/monorepo/compare/auto/slot-1-parse-gen-params
https://github.com/tgr-rs/monorepo/compare/auto/slot-1-trailing-chars
https://github.com/tgr-rs/monorepo/compare/auto/slot-1-unit-tests
https://github.com/tgr-rs/monorepo/compare/auto/slot-2
https://github.com/tgr-rs/monorepo/compare/auto/slot-2-add-bounds-validation
https://github.com/tgr-rs/monorepo/compare/auto/slot-2-add-timeout-bounds-validation
https://github.com/tgr-rs/monorepo/compare/auto/slot-2-input-validation
https://github.com/tgr-rs/monorepo/compare/auto/slot-3-add-per-field-validation
https://github.com/tgr-rs/monorepo/compare/auto/slot-3-input-validation-main-payload-truncation
https://github.com/tgr-rs/monorepo/compare/auto/slot-4
https://github.com/tgr-rs/monorepo/compare/auto/slot-4-add-duplicate-param-detection
https://github.com/tgr-rs/monorepo/compare/auto/slot-4-dup-param-detect
https://github.com/tgr-rs/monorepo/compare/auto/slot-4-duplicate-param-detection
https://github.com/tgr-rs/monorepo/compare/auto/slot-5
https://github.com/tgr-rs/monorepo/compare/auto/slot-5-agent-command-validation
https://github.com/tgr-rs/monorepo/compare/auto/slot-5-handle-agent-sanitization
https://github.com/tgr-rs/monorepo/compare/auto/slot-5-input-validation-agent-payload
https://github.com/tgr-rs/monorepo/compare/auto/slot-5-shell-injection-prevention
https://github.com/tgr-rs/monorepo/compare/auto/slot-6

## Verdicts

### slot-1

good: yes
accepted: maybe

agent guardrails and tests

### slot-1-parse-gen-params

good: yes
accepted: maybe

tests for video generation code

### slot-2-add-bounds-validation

good: no
accepted: no

limits on time for agent to work

### slot-2-input-validation

good: kinda
accepted: no

removed some masking of secrets

### slot-3-input-validation-main-payload-truncation

good: no
accepted: no

limits on time for agent to work

### slot-4-duplicate-param-detection

good: no
accepted: no

was removing duplicate frames, may be worse than doing nothing

### slot-5

good: yes
accepted: maybe

agents tests and guardrails

### slot-5-agent-command-validation

good: yes
accepted: maybe

agents safe input guardrails

### slot-6

good: kinda
accepted: no

params deduplication
