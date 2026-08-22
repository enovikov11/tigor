---
name: threejs-interactive-3d
description: "Build interactive 3D web apps (games, visualizations) with Three.js: custom shaders, geometry manipulation, input handling, and UI overlays. Covers the full stack from index.html to deployable single-file or multi-file projects."
---

# Three.js Interactive 3D Development

Build interactive 3D experiences in the browser — games, data visualizations, interactive demos — using Three.js with custom GLSL shaders, modern vanilla JS (no jQuery), and overlay CSS for UI.

## Triggers
- Building a 3D web game, interactive visualization, or WebGL demo
- Needing custom shaders for PBR, glow, fresnel, or other effects
- Per-face or per-vertex coloring on Three.js meshes
- Modernizing legacy Three.js projects (removing jQuery, upgrading patterns)

## File structure
```
index.html        # Canvas + overlay divs + script includes
shaders.js        # GLSL source strings
view.js           # Scene, camera, renderer, geometry, materials, render loop
controller.js     # Input: raycaster, pointer events, hover/click
model.js          # Game logic / state / UI state machine
settings.js       # Config: colors, constants, language strings, rules
style.css         # Overlay UI, menus, HUD, animations
vendor/           # three.min.js, OrbitControls.js (keep minimal)
```

Include scripts in order: settings → shaders → view → controller → ai (optional) → model.

## Core patterns

### Scene setup (view.js)
```js
const canvas = document.getElementById('gl');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(50, w/h, 0.1, 1000);
const controls = new THREE.OrbitControls(camera, canvas);
controls.enableDamping = true;
```

### Per-face coloring: use NON-INDEXED geometry
**Critical pitfall:** Indexed geometry shares vertices across faces — per-vertex color on one face bleeds to neighbors. Always use `geo.toNonIndexed()` when each face needs its own color.

```js
const baseGeo = new THREE.IcosahedronGeometry(10, 0);
const geo = baseGeo.toNonIndexed();
const cols = new Float32Array(geo.attributes.position.count * 3);
// fill cols...
geo.addAttribute('color', new THREE.BufferAttribute(cols, 3));
```

### Shader material with uniforms
```js
const mat = new THREE.ShaderMaterial({
  vertexShader: shaders.vertexShader,
  fragmentShader: shaders.fragmentShader,
  uniforms: {
    uTime: { value: 0 },
    uCamPos: { value: camera.position.clone() },
    uLightDir: { value: new THREE.Vector3(1,1,1).normalize() },
  },
});
```

In the render loop, update `uTime`, `uCamPos` every frame. Vertex shader must declare `attribute vec3 color` (not `faceColor`) to match BufferAttribute name.

### Raycaster input (controller.js)
```js
const raycaster = new THREE.Raycaster();
const pointer = new THREE.Vector2();

function getIntersect(e) {
  pointer.x = (e.clientX / window.innerWidth) * 2 - 1;
  pointer.y = -(e.clientY / window.innerHeight) * 2 + 1;
  raycaster.setFromCamera(pointer, camera);
  return raycaster.intersectObject(mesh)[0] || null;
}
```

Use `pointerdown`/`pointermove`/`pointerup` for unified mouse+touch. Detect drag vs click by comparing `pointerdown` position to `pointerup` position.

### Hover highlight
Create a secondary mesh (plane or the face itself) that sits at the intersection point, oriented to the face normal:
```js
highlightMesh.position.copy(hit.point);
highlightMesh.lookAt(hit.point.clone().add(hit.face.normal));
```

## Shaders (see references/shader-patterns.md)
- Vertex: pass `color` attribute + world pos + normal to fragment
- Fragment: Blinn-Phong specular + Fresnel rim + hemisphere lighting
- Wireframe overlay: separate `EdgesGeometry` + transparent shader
- Use `uniform float uTime` for animated effects (pulse, shimmer)

## Input handling
- Use `pointer` events, not `mouse` events — covers touch natively
- Prevent default on `touchstart`/`touchmove` to block page scroll
- Separate drag (camera orbit) from click (game action) by distance threshold

## UI overlays
- Pure CSS overlay divs with `backdrop-filter: blur()` for frosted glass
- Toggle visibility via `classList.toggle('active')` + CSS opacity transition
- Never use jQuery/jQuery UI — vanilla DOM manipulation is lighter

## Mobile considerations
- `touch-action: none` on the canvas
- `devicePixelRatio` capped at 2 for performance
- CSS `@media (max-width: 500px)` for smaller overlays
- Reduce `aiDepth` for mobile if compute-bound

## Pitfalls
1. **Indexed geometry + per-face color = bleed.** Always `toNonIndexed()`.
2. **Shader attribute name mismatch.** BufferAttribute('color') → GLSL `attribute vec3 color`.
3. **OrbitControls steals pointer events.** Disable during game clicks or use `controls.enabled = false`.
4. **Uniforms don't auto-update.** `uCamPos.value.copy(camera.position)` every frame.
5. **`geo.attributes.color.needsUpdate = true`** after any color change — otherwise GPU keeps stale data.
6. **Three.js r92 (bundled) ≠ latest.** `toNonIndexed()` exists in r92+. If on older, use `THREE.GeometryUtils.toNonIndexed()`.

## AI opponents
For game logic, implement minimax with alpha-beta pruning. Store win/loss evaluation in `model.js` or `ai.js` — keep it pure (no DOM access). See references/minimax-game-ai.md for the evaluated pattern.
