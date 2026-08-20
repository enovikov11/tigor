// Minimax AI with alpha-beta pruning
const ai = (function() {
  const MAX_DEPTH = settings.aiDepth || 6;

  function getEmptyIds(state) {
    const ids = [];
    for (let i = 0; i < state.length; i++) {
      if (state[i] === -1) ids.push(i);
    }
    return ids;
  }

  function checkWin(state) {
    for (const t of settings.winningTriplets) {
      if (state[t[0]] >= 1 && state[t[0]] === state[t[1]] && state[t[1]] === state[t[2]]) {
        return state[t[0]];
      }
    }
    return -1;
  }

  function evaluate(state, player, opp) {
    let score = 0;
    for (const t of settings.winningTriplets) {
      const a = state[t[0]], b = state[t[1]], c = state[t[2]];
      const pCount = (a === player) + (b === player) + (c === player);
      const oCount = (a === opp) + (b === opp) + (c === opp);

      if (pCount === 3) return 10000;
      if (oCount === 3) return -10000;
      if (pCount > 0 && oCount === 0) score += Math.pow(10, pCount);
      if (oCount > 0 && pCount === 0) score -= Math.pow(10, oCount);
    }
    return score;
  }

  function minimax(state, depth, alpha, beta, isMax, player, opp) {
    const winner = checkWin(state);
    if (winner === player) return 10000 + (MAX_DEPTH - depth);
    if (winner === opp) return -10000 - (MAX_DEPTH - depth);
    if (depth >= MAX_DEPTH) return evaluate(state, player, opp);

    const empties = getEmptyIds(state);
    if (empties.length === 0) return 0;

    if (isMax) {
      let best = -Infinity;
      for (const id of empties) {
        state[id] = player;
        best = Math.max(best, minimax(state, depth + 1, alpha, beta, false, player, opp));
        state[id] = -1;
        alpha = Math.max(alpha, best);
        if (beta <= alpha) break;
      }
      return best;
    } else {
      let best = Infinity;
      for (const id of empties) {
        state[id] = opp;
        best = Math.min(best, minimax(state, depth + 1, alpha, beta, true, player, opp));
        state[id] = -1;
        beta = Math.min(beta, best);
        if (beta <= alpha) break;
      }
      return best;
    }
  }

  return {
    getMove(state, aiPlayer) {
      const opp = aiPlayer === 1 ? 2 : 1;
      const newState = Array.from(state);
      let bestScore = -Infinity;
      let bestMove = -1;

      const empties = getEmptyIds(newState);
      for (const id of empties) {
        newState[id] = aiPlayer;
        const sc = minimax(newState, 0, -Infinity, Infinity, false, aiPlayer, opp);
        newState[id] = -1;
        if (sc > bestScore) {
          bestScore = sc;
          bestMove = id;
        }
      }
      return bestMove;
    },
  };
})();
