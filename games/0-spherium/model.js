const model = (function() {
  let currentPlayer = 1;
  let vsAI = false;
  let gameActive = false;
  let scores = { p1: 0, p2: 0 };
  let aiTimeout = null;

  // DOM elements
  const $mainMenu = document.getElementById('main-menu');
  const $pauseMenu = document.getElementById('pause-menu');
  const $winOverlay = document.getElementById('win-overlay');
  const $tutorial = document.getElementById('tutorial');
  const $turnText = document.getElementById('turn-text');
  const $scoreP1 = document.getElementById('score-p1-val');
  const $scoreP2 = document.getElementById('score-p2-val');
  const $dotP1 = document.getElementById('dot-p1');
  const $dotP2 = document.getElementById('dot-p2');
  const $winText = document.getElementById('win-text');

  // Tutorial state
  let tutPage = 0;
  const tutSteps = settings.tutorial;

  // ---- Overlay management ----
  function hideAll() {
    $mainMenu.classList.remove('active');
    $pauseMenu.classList.remove('active');
    $winOverlay.classList.remove('active');
    $tutorial.classList.remove('active');
  }

  function show(id) {
    hideAll();
    document.getElementById(id).classList.add('active');
  }

  // ---- Turn UI ----
  function updateTurnUI() {
    $turnText.textContent = currentPlayer === 1 ? settings.lang.turnP1 : settings.lang.turnP2;
    $dotP1.style.opacity = currentPlayer === 1 ? '1' : '0.3';
    $dotP2.style.opacity = currentPlayer === 2 ? '1' : '0.3';
    $turnText.style.color = currentPlayer === 1
      ? `rgb(${settings.colors.player1.join(',')})`
      : `rgb(${settings.colors.player2.join(',')})`;
  }

  // ---- Win check ----
  function checkWin(state) {
    for (const t of settings.winningTriplets) {
      if (state[t[0]] >= 1 && state[t[0]] === state[t[1]] && state[t[1]] === state[t[2]]) {
        return { winner: state[t[0]], faces: t };
      }
    }
    const hasEmpty = state.some(s => s === -1);
    return hasEmpty ? null : { winner: 0, faces: [] };
  }

  // ---- Face click ----
  function onFaceClick(faceId) {
    if (!gameActive) return;
    const state = view.getState();
    if (state[faceId] !== -1) return;

    // Apply move
    view.paintFace(faceId, currentPlayer);
    const result = checkWin(view.getState());

    if (result) {
      gameActive = false;
      controller.disable();
      view.highlightWinFaces(result.faces);

      if (result.winner === 0) {
        $winText.textContent = settings.lang.winner3;
      } else {
        scores['p' + result.winner]++;
        $scoreP1.textContent = scores.p1;
        $scoreP2.textContent = scores.p2;
        $winText.textContent = result.winner === 1
          ? settings.lang.winner1
          : settings.lang.winner2;
      }

      setTimeout(() => show('win-overlay'), 600);
      return;
    }

    // Switch turn
    currentPlayer = currentPlayer === 1 ? 2 : 1;
    updateTurnUI();

    // AI move
    if (vsAI && currentPlayer === 2 && gameActive) {
      controller.disable();
      aiTimeout = setTimeout(() => {
        const move = ai.getMove(view.getState(), 2);
        if (move >= 0) {
          view.paintFace(move, 2);
          const aiResult = checkWin(view.getState());
          if (aiResult) {
            gameActive = false;
            view.highlightWinFaces(aiResult.faces);
            if (aiResult.winner === 0) {
              $winText.textContent = settings.lang.winner3;
            } else {
              scores['p' + aiResult.winner]++;
              $scoreP1.textContent = scores.p1;
              $scoreP2.textContent = scores.p2;
              $winText.textContent = aiResult.winner === 1
                ? settings.lang.winner1
                : settings.lang.winner2;
            }
            setTimeout(() => show('win-overlay'), 600);
          } else {
            currentPlayer = 1;
            updateTurnUI();
            controller.enable();
          }
        }
      }, 400);
    }
  }

  // ---- New game ----
  function newGame(aiMode) {
    if (aiTimeout) clearTimeout(aiTimeout);
    vsAI = !!aiMode;
    currentPlayer = 1;
    gameActive = true;
    view.reset();
    updateTurnUI();
    hideAll();
    controller.enable();
    controller.setOnClick(onFaceClick);

    if (vsAI) {
      $turnText.textContent = settings.lang.turnP1;
      document.getElementById('btn-again').textContent = settings.lang.again;
    }
  }

  // ---- Tutorial ----
  function updateTutorial() {
    const step = tutSteps[tutPage];
    document.getElementById('tut-title').textContent = step.title;
    document.getElementById('tut-body').innerHTML = `<p>${step.text}</p>`;
    document.getElementById('tut-page').textContent = `${tutPage + 1} / ${tutSteps.length}`;
    document.getElementById('tut-prev').style.visibility = tutPage === 0 ? 'hidden' : 'visible';
    document.getElementById('tut-next').textContent = tutPage === tutSteps.length - 1 ? 'Начать' : '→';
  }

  // ---- Event bindings ----
  document.getElementById('btn-start').onclick = () => newGame(false);
  document.getElementById('btn-ai').onclick = () => newGame(true);
  document.getElementById('btn-tutorial').onclick = () => {
    tutPage = 0;
    updateTutorial();
    show('tutorial');
  };

  document.getElementById('btn-restart').onclick = () => {
    newGame(vsAI);
  };

  document.getElementById('btn-menu').onclick = () => {
    if (gameActive) {
      gameActive = false;
      controller.disable();
      show('pause-menu');
    }
  };

  document.getElementById('btn-resume').onclick = () => {
    gameActive = true;
    controller.enable();
    hideAll();
  };

  document.getElementById('btn-new-game').onclick = () => newGame(vsAI);
  document.getElementById('btn-main-menu').onclick = () => {
    gameActive = false;
    controller.disable();
    show('main-menu');
  };

  document.getElementById('btn-again').onclick = () => newGame(vsAI);
  document.getElementById('btn-win-menu').onclick = () => {
    gameActive = false;
    show('main-menu');
  };

  // Tutorial navigation
  document.getElementById('tut-prev').onclick = () => {
    if (tutPage > 0) { tutPage--; updateTutorial(); }
  };
  document.getElementById('tut-next').onclick = () => {
    if (tutPage < tutSteps.length - 1) { tutPage++; updateTutorial(); }
    else { newGame(false); }
  };

  // Hover handler
  controller.setOnHover(() => {});

  // Init: show main menu
  updateTurnUI();
  updateTutorial();
  show('main-menu');
  controller.disable();

  return { refresh: () => newGame(vsAI), setAI: (v) => { vsAI = v; } };
})();
