const controller = (function() {
  let onClick = () => {};
  let onHover = () => {};
  let enabled = false;

  const raycaster = new THREE.Raycaster();
  const pointer = new THREE.Vector2();
  let isDragging = false;
  let pointerDown = { x: 0, y: 0 };

  function updatePointer(x, y) {
    pointer.x = (x / window.innerWidth) * 2 - 1;
    pointer.y = -(y / window.innerHeight) * 2 + 1;
  }

  function getIntersect(e) {
    updatePointer(e.clientX || e.pageX, e.clientY || e.pageY);
    raycaster.setFromCamera(pointer, view.camera);
    const hits = raycaster.intersectObject(view.mesh);
    return hits.length > 0 ? hits[0] : null;
  }

  // Mouse events
  window.addEventListener('pointerdown', e => {
    if (!enabled) return;
    isDragging = false;
    pointerDown = { x: e.clientX, y: e.clientY };
  });

  window.addEventListener('pointermove', e => {
    if (!enabled) return;
    const dx = e.clientX - pointerDown.x;
    const dy = e.clientY - pointerDown.y;
    if (Math.abs(dx) > 5 || Math.abs(dy) > 5) {
      isDragging = true;
    }

    // Hover detection
    const hit = getIntersect(e);
    if (hit && !isDragging) {
      view.setHighlightVisible(true);
      view.setHighlightPosition(
        hit.point,
        hit.face.normal.clone().transformDirection(view.mesh.matrixWorld).normalize(),
        3.5
      );
      onHover(hit.faceIndex);
    } else {
      view.setHighlightVisible(false);
      onHover(-1);
    }
  });

  window.addEventListener('pointerup', e => {
    if (!enabled) return;
    if (isDragging) {
      isDragging = false;
      view.setHighlightVisible(false);
      return;
    }
    const hit = getIntersect(e);
    if (hit) {
      onClick(hit.faceIndex);
    }
  });

  // Touch: prevent scroll
  view.canvas.addEventListener('touchstart', e => e.preventDefault(), { passive: false });
  view.canvas.addEventListener('touchmove', e => e.preventDefault(), { passive: false });

  return {
    setOnClick(cb) { onClick = cb; },
    setOnHover(cb) { onHover = cb; },
    enable() { enabled = true; },
    disable() { enabled = false; view.setHighlightVisible(false); },
    isEnabled() { return enabled; },
  };
})();
