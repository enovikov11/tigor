# Shader Patterns — Spherium (icosahedron game)

## Vertex shader — per-face color + pulse
```glsl
attribute vec3 color;        // from BufferAttribute('color')
varying vec3 vFaceColor;
varying vec3 vNormal;
varying vec3 vWorldPos;
uniform float uTime;
uniform float uPulse;

void main() {
  vFaceColor = color;
  vNormal = normalize(normalMatrix * normal);
  vec4 world = modelMatrix * vec4(position, 1.0);
  float pulse = 1.0 + uPulse * 0.015 * sin(uTime * 2.0);
  world.xyz *= pulse;
  vWorldPos = world.xyz;
  gl_Position = projectionMatrix * viewMatrix * world;
}
```

## Fragment shader — fake PBR + fresnel
```glsl
varying vec3 vFaceColor;
varying vec3 vNormal;
varying vec3 vWorldPos;

uniform vec3 uLightDir1;
uniform vec3 uCamPos;
uniform vec3 uBgColor;
uniform float uEmissive;
uniform float uTime;

void main() {
  vec3 N = normalize(vNormal);
  vec3 V = normalize(uCamPos - vWorldPos);

  float diff1 = max(dot(N, uLightDir1), 0.0) * 0.7;
  float diff2 = max(dot(N, -uLightDir1), 0.0) * 0.15;

  vec3 H = normalize(uLightDir1 + V);
  float spec = pow(max(dot(N, H), 0.0), 32.0) * 0.5;

  float fresnel = pow(1.0 - max(dot(N, V), 0.0), 3.0);

  vec3 col = vFaceColor;
  if (uEmissive > 0.01) {
    col += vec3(0.05) * sin(uTime * 1.5 + vWorldPos.x * 0.5);
  }

  vec3 ambient = uBgColor * 0.15 + col * 0.1;
  vec3 lit = col * (diff1 + diff2) + spec + fresnel * col * 0.6;
  vec3 final = ambient + lit;
  if (uEmissive > 0.01) final += col * 0.08;

  gl_FragColor = vec4(final, 1.0);
}
```

## Wireframe overlay shader
```glsl
// Vertex
uniform float uTime;
varying float vAlpha;
void main() {
  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  vAlpha = 0.3 + 0.1 * sin(uTime * 0.5 + position.x * 0.3);
}

// Fragment
varying float vAlpha;
uniform vec3 uWireColor;
void main() {
  gl_FragColor = vec4(uWireColor, vAlpha);
}
```

## Key uniforms to update each frame
| Uniform | Source | Why |
|---------|--------|-----|
| `uTime` | `+= 0.016` | Animation driver |
| `uCamPos` | `camera.position` | Fresnel/specular depend on view direction |
| `uPulse` | `0` or `1` | Breathing effect on win faces |
| `uEmissive` | `coloredFaces / totalFaces` | Color shift intensity |
