# Minimax Game AI — Spherium pattern

## Architecture
- Pure JS, no DOM access. Takes `state[]` (per-face owner: -1/1/2), returns face index.
- Minimax with alpha-beta pruning, depth-limited.
- Evaluation counts player/opponent occupancy in each winning triplet.

## Evaluation heuristic
```js
function evaluate(state, player, opp) {
  let score = 0;
  for (const t of winningTriplets) {
    const pCount = (state[t[0]]===player)+(state[t[1]]===player)+(state[t[2]]===player);
    const oCount = (state[t[0]]===opp)+(state[t[1]]===opp)+(state[t[2]]===opp);
    if (pCount === 3) return 10000;
    if (oCount === 3) return -10000;
    if (pCount > 0 && oCount === 0) score += Math.pow(10, pCount);
    if (oCount > 0 && pCount === 0) score -= Math.pow(10, oCount);
  }
  return score;
}
```

Weight formula: `10^n` where n = number of claimed faces in an unblocked triplet. This heavily favors moves that create 2-of-3 threats over isolated 1-of-3 claims.

## Alpha-beta search
```js
function minimax(state, depth, alpha, beta, isMax, player, opp) {
  const winner = checkWin(state);
  if (winner === player) return 10000 + (MAX_DEPTH - depth);
  if (winner === opp) return -10000 - (MAX_DEPTH - depth);
  if (depth >= MAX_DEPTH) return evaluate(state, player, opp);

  for (const id of getEmptyIds(state)) {
    state[id] = isMax ? player : opp;
    const sc = minimax(state, depth+1, alpha, beta, !isMax, player, opp);
    state[id] = -1;
    if (isMax) { alpha = Math.max(alpha, sc); } else { beta = Math.min(beta, sc); }
    if (beta <= alpha) break;
  }
  return isMax ? alpha : beta;
}
```

## Performance notes
- Depth 6 works fine on desktop for 20-face icosahedron (~20^n branching, heavily pruned).
- For mobile, reduce to 4–5.
- State is mutated in-place for performance (set → recurse → undo).
