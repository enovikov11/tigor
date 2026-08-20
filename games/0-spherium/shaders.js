// Custom shader materials for Spherium
const shaders = {
  // Vertex shader — outputs face color, normal, world pos
  vertexShader: `
    attribute vec3 color;
    varying vec3 vFaceColor;
    varying vec3 vNormal;
    varying vec3 vWorldPos;
    uniform float uTime;
    uniform float uPulse;

    void main() {
      vFaceColor = faceColor;
      vNormal = normalize(normalMatrix * normal);
      vec4 world = modelMatrix * vec4(position, 1.0);

      // Subtle breathing pulse
      float pulse = 1.0 + uPulse * 0.015 * sin(uTime * 2.0);
      world.xyz *= pulse;

      vWorldPos = world.xyz;
      gl_Position = projectionMatrix * viewMatrix * world;
    }
  `,

  // Fragment shader — fake PBR + fresnel rim + edge glow
  fragmentShader: `
    varying vec3 vFaceColor;
    varying vec3 vNormal;
    varying vec3 vWorldPos;

    uniform vec3 uLightDir1;
    uniform vec3 uLightDir2;
    uniform vec3 uCamPos;
    uniform vec3 uBgColor;
    uniform float uEmissive;
    uniform float uTime;

    void main() {
      vec3 N = normalize(vNormal);
      vec3 V = normalize(uCamPos - vWorldPos);

      // Two-tone lighting (hemisphere-ish)
      float diff1 = max(dot(N, uLightDir1), 0.0) * 0.7;
      float diff2 = max(dot(N, -uLightDir1), 0.0) * 0.15;

      // Fake specular (Blinn-Phong)
      vec3 H = normalize(uLightDir1 + V);
      float spec = pow(max(dot(N, H), 0.0), 32.0) * 0.5;

      // Fresnel rim
      float fresnel = pow(1.0 - max(dot(N, V), 0.0), 3.0);

      // Subtle animated color shift for non-neutral faces
      vec3 col = vFaceColor;
      if (uEmissive > 0.01) {
        col += vec3(0.05) * sin(uTime * 1.5 + vWorldPos.x * 0.5);
      }

      // Compose
      vec3 ambient = uBgColor * 0.15 + col * 0.1;
      vec3 lit = col * (diff1 + diff2) + spec + fresnel * col * 0.6;
      vec3 final = ambient + lit;

      // Boost colored faces slightly
      if (uEmissive > 0.01) {
        final += col * 0.08;
      }

      gl_FragColor = vec4(final, 1.0);
    }
  `,

  // Wireframe overlay shader — bright edges
  wireVertexShader: `
    uniform float uTime;
    varying float vAlpha;

    void main() {
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      vAlpha = 0.3 + 0.1 * sin(uTime * 0.5 + position.x * 0.3);
    }
  `,

  wireFragmentShader: `
    varying float vAlpha;
    uniform vec3 uWireColor;

    void main() {
      gl_FragColor = vec4(uWireColor, vAlpha);
    }
  `,

  // Highlight face shader — shown on hover
  highlightVertexShader: `
    uniform float uTime;
    varying vec3 vNormal;
    varying vec3 vWorldPos;

    void main() {
      vNormal = normalize(normalMatrix * normal);
      vWorldPos = (modelMatrix * vec4(position, 1.0)).xyz;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,

  highlightFragmentShader: `
    varying vec3 vNormal;
    varying vec3 vWorldPos;
    uniform vec3 uCamPos;
    uniform float uTime;

    void main() {
      vec3 N = normalize(vNormal);
      vec3 V = normalize(uCamPos - vWorldPos);
      float rim = pow(1.0 - max(dot(N, V), 0.0), 2.0);
      float pulse = 0.5 + 0.5 * sin(uTime * 4.0);
      vec3 col = mix(vec3(0.6, 0.8, 0.4), vec3(1.0, 0.95, 0.8), pulse * 0.5);
      float alpha = 0.25 + rim * 0.3;
      gl_FragColor = vec4(col, alpha);
    }
  `,
};
