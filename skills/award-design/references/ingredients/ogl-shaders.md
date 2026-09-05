# OGL Shaders for Sites

GLSL on a single full-screen quad — animated gradient mesh, noise background, image-to-image transition, hover displacement. OGL uses a `Renderer`, a `Program`, and a screen triangle without a full scene graph. Resolve versions through `../stack-facts.md` and measure the actual bundle.

**Drive every uniform from the committed `DESIGN.md`** — palette hexes as `vec3`, motion speed from the motion tokens, mood from the atmosphere scores. A shader keyed to the universe reads art-directed; the stock animated-rainbow (`cos(uv.xyx + t)`) reads like a template. Never ship the default.

## OGL vs Three.js

- **OGL** — the visual is one quad with a fragment shader: gradient mesh, noise field, grain, image transition, pointer ripple. A screen triangle needs no scene lighting or camera; a full 3D scene graph may be unnecessary.
- **Three.js / R3F** — real 3D is the signature: meshes, lighting, depth, a model that rotates through scroll. See `web3d-for-sites.md`.

Decide by the *medium*: a gradient breathing behind a hero is a quad; a rotating helmet is geometry.

## Canonical setup

A screen `Triangle` (cheaper than a `Plane` — one tri, excess clipped), a `Program`, a gated rAF loop, resize.

```javascript
import { Renderer, Program, Mesh, Triangle, Color, Vec2 } from 'ogl';

// vertex: passes uv through; position is the screen-space triangle, clip-space already
const vertex = /* glsl */ `attribute vec2 uv; attribute vec2 position; varying vec2 vUv;
  void main() { vUv = uv; gl_Position = vec4(position, 0.0, 1.0); }`;

// The palette lives in DESIGN.md and exports to `@theme` as hex custom properties
// (`../design-md-anatomy.md`), which is what OGL's Color parses. Read it off the root:
// one source, no second copy of the palette to drift.
const token = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();

const renderer = new Renderer({ dpr: Math.min(window.devicePixelRatio, 2), alpha: true });
const gl = renderer.gl;
canvasHost.appendChild(gl.canvas); // a positioned wrapper, not document.body
const program = new Program(gl, {
  vertex,
  fragment, // see patterns below
  uniforms: {
    uTime: { value: 0 },
    uRes: { value: new Vec2() },
    uPointer: { value: new Vec2(0.5, 0.5) },
    uColorA: { value: new Color(token('--color-surface')) }, // whichever two `colors.*` keys
    uColorB: { value: new Color(token('--color-accent')) },  // the palette commits — never literals
  },
});
const mesh = new Mesh(gl, { geometry: new Triangle(gl), program });

function resize() {
  renderer.setSize(canvasHost.clientWidth, canvasHost.clientHeight);
  program.uniforms.uRes.value.set(gl.canvas.width, gl.canvas.height);
}
window.addEventListener('resize', resize);
resize();

let raf;
const loop = (t) => {
  program.uniforms.uTime.value = t * 0.001;
  renderer.render({ scene: mesh }); // no camera needed for a screen quad
  raf = requestAnimationFrame(loop);
};
raf = requestAnimationFrame(loop); // gate this on reduced-motion + visibility — see below
```

## Patterns

**Gradient mesh from tokens.** Mix two-to-three palette colors across a slow-warping field; `smoothstep` keeps bands soft. Pick palette stops that already read clean (`../foundations.md` on OKLCH) so the middle never muddies.

```glsl
float f = 0.5 + 0.5 * sin(vUv.x * 3.0 + uTime * 0.2) * cos(vUv.y * 2.0 - uTime * 0.15);
gl_FragColor = vec4(mix(uColorA, uColorB, smoothstep(0.2, 0.8, f)), 1.0);
```

**Multi-octave noise.** Raw noise reads as blobs; sum 3–4 octaves at halving amplitude for an organic field, amplitude/speed from the Motion score. OGL ships no noise function, so prepend a `snoise`/`cnoise` GLSL string (e.g. Stefan Gustavson's) to the fragment.

```glsl
float fbm(vec2 p) {
  float v = 0.0, a = 0.5;
  for (int i = 0; i < 4; i++) { v += a * noise(p); p *= 2.0; a *= 0.5; }
  return v;
}
```

**Image-to-image transition, noise-masked.** Two textures, a `uProgress` driven 0→1 by scroll or hover; warp the threshold with noise so the wipe dissolves instead of sliding.

```glsl
float edge = smoothstep(uProgress - 0.1, uProgress + 0.1, fbm(vUv * 3.0) * 0.5 + vUv.x * 0.5);
gl_FragColor = mix(texture2D(tNext, vUv), texture2D(tPrev, vUv), edge);
```

```javascript
import { TextureLoader } from 'ogl';
const tPrev = TextureLoader.load(gl, { src: '/hero.webp' }); // handles Image + upload
// then a uniform per texture: tPrev: { value: tPrev }, tNext: { value: tNext }
```

**Subtle grain.** A per-frame hash over `vUv` at low opacity kills banding and adds tactility. Keep it under ~0.04.

```glsl
float g = fract(sin(dot(vUv * uRes, vec2(12.9898, 78.233)) + uTime) * 43758.5453);
color += (g - 0.5) * 0.04;
```

**Hover / pointer displacement.** Feed normalized pointer in; offset UVs by falloff from the cursor for a magnetic ripple. Lerp the uniform toward the target each frame for inertia; never snap.

```glsl
vec2 d = vUv - uPointer;
float distanceToPointer = length(d);
vec2 direction = d / max(distanceToPointer, 0.0001);
vec2 warp = vUv - direction * 0.03 * (1.0 - smoothstep(0.0, 0.4, distanceToPointer));
```

## Uniforms from the universe

- **Colors** — every `vec3` is a `new Color('#hex')` from the DESIGN.md palette roles (parses straight to a normalized `vec3`, no manual `/255`). No hardcoded stops.
- **Motion** — speed multipliers and amplitudes map to the motion tokens / atmosphere Motion score (1–3 = barely drifting; 7–10 = active). See `../atmosphere-calibration.md`.
- **Pointer / time** — `uTime` and `uPointer` are the only always-on inputs; everything visible traces to a committed token.

## Performance

- One quad keeps geometry and draw-call count constant. Fragment cost still grows with rendered pixels and shader complexity; keep loops bounded and branches few.
- Cap DPR at 2 in the `Renderer` constructor — retina past 2× burns fill rate for no visible gain.
- Gate the loop with an `IntersectionObserver` on the canvas: `e.isIntersecting` resumes (`raf ??= requestAnimationFrame(loop)`), offscreen cancels (`cancelAnimationFrame(raf); raf = null`). Pause on `visibilitychange` too.
- No per-frame allocations: mutate `uPointer.value.set(...)`, never assign a fresh `Vec2`. Reuse colors and vectors.

## Reduced motion + accessibility

- `prefers-reduced-motion: reduce` → before the first rAF, either render one static frame (`renderer.render({ scene: mesh })`, no loop) or skip WebGL and paint a CSS gradient from the same palette.

```javascript
if (matchMedia('(prefers-reduced-motion: reduce)').matches) { renderer.render({ scene: mesh }); }
else raf = requestAnimationFrame(loop); // only animate when motion is allowed
```

- The canvas is decoration → `aria-hidden="true"`, `pointer-events: none` unless pointer displacement is the interaction, behind real content, never the LCP element. Provide a CSS-gradient fallback for no-WebGL contexts; the page must read complete without the canvas.

## Cross-references

`web3d-for-sites.md` (real 3D — when a quad isn't enough), `../atmosphere-calibration.md` (Motion score → shader speed), `../foundations.md` (palette, OKLCH, the animation toolkit), `../production-hardening.md` (canvas sizing, iOS, perf budgets).
