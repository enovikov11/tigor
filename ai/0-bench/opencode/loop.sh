#!/usr/bin/env bash
set -euo pipefail

# opencode + git + ripgrep + fd + jq are pre-installed in the image.
# Runtime has no internet. Running as container root which maps to
# host box (uid 1000) in rootless podman, so /repo is writable.
#
# Layout:
#   /monorepo-ro   canonical monorepo (read-only)
#   /monorepo-rw   working copy (read-write) — all edits + commits here
#   /loop-state    loop state (read-write), persists across iterations

RO=/monorepo-ro
RW=/monorepo-rw
STATE_DIR=/loop-state
STATE="$STATE_DIR/loop-state.md"
LOG="$STATE_DIR/loop-driver.log"
BENCH_CFG_SRC="$RO/ai/0-bench/opencode/opencode.jsonc"
BENCH_CFG_DST="$RW/opencode.jsonc"

ts() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
log() { echo "[loop] $(ts) $*"; }

mkdir -p "$STATE_DIR"

# Initialize state file on first run.
if [ ! -f "$STATE" ]; then
  cat > "$STATE" <<'EOF'
# Loop State

## Slots

| slot | branch | topic | status | last_updated | commits | notes |
|------|--------|-------|--------|--------------|---------|-------|
| 1 | auto/slot-1 | undecided | planning | - | 0 | |
| 2 | auto/slot-2 | undecided | planning | - | 0 | |
| 3 | auto/slot-3 | undecided | planning | - | 0 | |
| 4 | auto/slot-4 | undecided | planning | - | 0 | |
| 5 | auto/slot-5 | undecided | planning | - | 0 | |
| 6 | auto/slot-6 | undecided | planning | - | 0 | |
| 7 | auto/slot-7 | undecided | planning | - | 0 | |
| 8 | auto/slot-8 | undecided | planning | - | 0 | |
| 9 | auto/slot-9 | undecided | planning | - | 0 | |
| 10 | auto/slot-10 | undecided | planning | - | 0 | |

## Notes

EOF
  log "initialized $STATE"
fi

# Ensure git identity is set (also set via env, but be explicit).
git -C "$RW" config user.name >/dev/null 2>&1 || git -C "$RW" config user.name "opencode-bench"
git -C "$RW" config user.email >/dev/null 2>&1 || git -C "$RW" config user.email "opencode-bench@localhost"

clean_worktree() {
  # Reset any uncommitted state left behind by a previous crashed iteration.
  # We never discard committed work on slot branches — only the working tree
  # of the current branch (which the agent is supposed to commit before
  # exiting, but may not have on a crash).
  git -C "$RW" checkout -- . 2>/dev/null || true
  git -C "$RW" clean -fd 2>/dev/null || true
  # Return to main so the next agent starts from a clean base.
  git -C "$RW" checkout main 2>/dev/null || git -C "$RW" checkout master 2>/dev/null || true
  git -C "$RW" checkout -- . 2>/dev/null || true
  git -C "$RW" clean -fd 2>/dev/null || true
}

ITERATION=0
while true; do
  ITERATION=$((ITERATION + 1))
  START=$(ts)
  log "=== iteration $ITERATION start ==="

  clean_worktree
  log "worktree cleaned, on $(git -C "$RW" rev-parse --abbrev-ref HEAD 2>/dev/null || echo '?')"

  # Overwrite the repo's own opencode.jsonc with the bench config so opencode
  # picks up the p-vllm provider and permissive permissions.
  cp "$BENCH_CFG_SRC" "$BENCH_CFG_DST"
  log "copied bench opencode.jsonc -> $BENCH_CFG_DST"

  set +e
  opencode run --model p-vllm/siq-1-35b \
    "You are an autonomous improvement agent running one iteration of a long loop. Read $RO/ai/0-bench/opencode/meta.md now — it defines all your rules, the slot model, the state file format, and exclusions. Read $RO/AGENTS.md for repo conventions and structure. Then read $STATE to see slot states.

Your job this iteration:
1. Pick one slot following meta.md's slot-picking rules. Prefer in-progress slots to keep momentum; if none, set a topic on an undecided slot (explore the repo first to find a meaningful, bounded target).
2. Check out that slot's branch. If it does not exist, create it from main.
3. Spend real effort: explore the relevant code across $RO and $RW, understand the problem, consider approaches. Do not rush to a trivial diff.
4. Make ONE focused change (ideally <30 lines diff, reviewable in under 60 seconds) that meaningfully advances the slot's topic. One change = one commit.
5. Validate: re-read what you changed; run the project's typecheck/lint/test if one exists.
6. Commit on the slot branch with message 'slot-<N>: <short description>'. Stage only files you changed.
7. Update $STATE: bump commits, set last_updated to the current ISO timestamp, add a one-line note.
8. Stay on the slot branch (the loop driver resets to main before the next run).

Do NOT push. Do NOT touch anything in the exclusions list. If the slot's plan no longer makes sense, mark it blocked in the state file and exit. If you cannot make a meaningful change, exit cleanly — do not force a shallow change."
  RC=$?
  set -e

  END=$(ts)
  log "iteration $ITERATION exited rc=$RC (start=$START end=$END)"
  {
    printf -- "- %s iter=%d rc=%d start=%s end=%s\n" "$(ts)" "$ITERATION" "$RC" "$START" "$END"
  } >> "$LOG" 2>/dev/null || log "could not write to $LOG"

  # Brief pause between iterations to avoid a tight crash-loop.
  sleep 5
done
