const view = (function() {
  const canvas = document.getElementById('gl');
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(window.innerWidth, window.innerHeight);

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(
    settings.colors.bg[0],
    settings.colors.bg[1],
    settings.colors.bg[2]
  );

  const camera = new THREE.PerspectiveCamera(
    50, window.innerWidth / window.innerHeight, 0.1, 1000
  );
  camera.position.set(0, 0, 28);

  const controls = new THREE.OrbitControls(camera, canvas);
  controls.enablePan = false;
  controls.enableZoom = false;
  controls.enableDamping = true;
  controls.dampingFactor = 0.08;
  controls.rotateSpeed = 0.5;

  // ---- Geometry (unindexed for per-face colors) ----
  const baseGeo = new THREE.IcosahedronGeometry(10, 0);
  const faceCount = baseGeo.faces.length;

  // ToNonIndexed so each face has its own 3 vertices → per-face colors work
  const geo = baseGeo.toNonIndexed();

  const colorArr = geo.attributes.color ? geo.attributes.color.array : null;
  if (!colorArr) {
    const c = settings.colors.neutral;
    const cols = new Float32Array(geo.attributes.position.count * 3);
    for (let i = 0; i < cols.length; i += 3) {
      cols[i] = c[0]; cols[i + 1] = c[1]; cols[i + 2] = c[2];
    }
    geo.addAttribute('color', new THREE.BufferAttribute(cols, 3));
  }
  geo.computeVertexNormals();

  // Main mesh shader material
  const mainMat = new THREE.ShaderMaterial({
    vertexShader: shaders.vertexShader,
    fragmentShader: shaders.fragmentShader,
    uniforms: {
      uTime: { value: 0 },
      uPulse: { value: 0.0 },
      uLightDir1: { value: new THREE.Vector3(1, 1, 1).normalize() },
      uLightDir2: { value: new THREE.Vector3(-1, -0.5, 0.5).normalize() },
      uCamPos: { value: camera.position.clone() },
      uBgColor: { value: new THREE.Vector3(
        settings.colors.bg[0], settings.colors.bg[1], settings.colors.bg[2]
      )},
      uEmissive: { value: 0.0 },
    },
  });

  const mesh = new THREE.Mesh(geo, mainMat);
  scene.add(mesh);

  // Wireframe overlay
  const edgesGeo = new THREE.EdgesGeometry(baseGeo);
  const wireMat = new THREE.ShaderMaterial({
    vertexShader: shaders.wireVertexShader,
    fragmentShader: shaders.wireFragmentShader,
    uniforms: {
      uTime: { value: 0 },
      uWireColor: { value: new THREE.Vector3(0.25, 0.3, 0.35) },
    },
    transparent: true,
  });
  const wireMesh = new THREE.LineSegments(edgesGeo, wireMat);
  scene.add(wireMesh);

  // Highlight mesh (for hover)
  // Create a small transparent plane that sits over the hovered face
  const highlightGeo = new THREE.PlaneGeometry(1, 1);
  const highlightMat = new THREE.ShaderMaterial({
    vertexShader: shaders.highlightVertexShader,
    fragmentShader: shaders.highlightFragmentShader,
    uniforms: {
      uCamPos: { value: camera.position.clone() },
      uTime: { value: 0 },
    },
    transparent: true,
    depthWrite: false,
    side: THREE.DoubleSide,
  });
  const highlightMesh = new THREE.Mesh(highlightGeo, highlightMat);
  highlightMesh.visible = false;
  scene.add(highlightMesh);

  // State
  let state = new Array(faceCount).fill(-1);
  let winFaces = []; // faces to highlight on win
  let time = 0;

  function updateFaceColor(faceId, player) {
    state[faceId] = player;
    const col = player === 1
      ? settings.colors.player1
      : player === 2
        ? settings.colors.player2
        : settings.colors.neutral;

    // NonIndexed: each face = 3 consecutive vertices
    for (let v = 0; v < 3; v++) {
      const idx = (faceId * 3 + v) * 3;
      geo.attributes.color.array[idx] = col[0];
      geo.attributes.color.array[idx + 1] = col[1];
      geo.attributes.color.array[idx + 2] = col[2];
    }
    geo.attributes.color.needsUpdate = true;
  }

  // Animate
  function animate() {
    requestAnimationFrame(animate);
    time += 0.016;

    controls.update();

    // Update shader uniforms
    mainMat.uniforms.uTime.value = time;
    mainMat.uniforms.uCamPos.value.copy(camera.position);
    mainMat.uniforms.uPulse.value = winFaces.length > 0 ? 1.0 : 0.0;
    mainMat.uniforms.uEmissive.value = state.filter(s => s >= 0).length / faceCount;

    wireMat.uniforms.uTime.value = time;
    highlightMat.uniforms.uTime.value = time;
    highlightMat.uniforms.uCamPos.value.copy(camera.position);

    renderer.render(scene, camera);
  }
  animate();

  window.addEventListener('resize', () => {
    renderer.setSize(window.innerWidth, window.innerHeight);
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
  });

  return {
    mesh,
    wireMesh,
    camera,
    controls,
    canvas,

    getState() { return Array.from(state); },
    getFaceCount() { return faceCount; },

    paintFace(id, player) {
      updateFaceColor(id, player);
    },

    reset() {
      state = new Array(faceCount).fill(-1);
      winFaces = [];
      camera.position.set(0, 0, 28);
      controls.reset();

      const c = settings.colors.neutral;
      for (let i = 0; i < faceCount * 3; i++) {
        const idx = i * 3;
        geo.attributes.color.array[idx] = c[0];
        geo.attributes.color.array[idx + 1] = c[1];
        geo.attributes.color.array[idx + 2] = c[2];
      }
      geo.attributes.color.needsUpdate = true;
    },

    setHighlightVisible(v) {
      highlightMesh.visible = v;
    },

    setHighlightPosition(pos, normal, scale) {
      highlightMesh.position.copy(pos);
      highlightMesh.lookAt(pos.clone().add(normal));
      highlightMesh.scale.setScalar(scale || 3);
    },

    // Animate win faces
    highlightWinFaces(faceIds) {
      winFaces = faceIds;
      // Flash them brighter
      for (const id of faceIds) {
        const player = state[id];
        if (player < 0) continue;
        const col = player === 1
          ? settings.colors.player1
          : settings.colors.player2;
        for (let v = 0; v < 3; v++) {
          const idx = (id * 3 + v) * 3;
          geo.attributes.color.array[idx] = Math.min(1, col[0] + 0.15);
          geo.attributes.color.array[idx + 1] = Math.min(1, col[1] + 0.15);
          geo.attributes.color.array[idx + 2] = Math.min(1, col[2] + 0.15);
        }
      }
      geo.attributes.color.needsUpdate = true;
    },

    getScene() { return scene; },
    getRenderer() { return renderer; },
  };
})();
