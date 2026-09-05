# Web 3D for sites — Three.js / R3F specialist cheat

You author one self-contained scene module — props in, canvas out, no shared files. The build is a marketing or portfolio site, not a game: the 3D earns the page memory, then gets out of the way. You are handed the project's `DESIGN.md`. The scene is an expression of that committed universe — its palette, easing, mood, and type — never generic 3D defaults. A studio-lit chrome torus on a `#202020` stage with `OrbitControls` is the slop tell judges read in seconds.

## The delegation contract

This section is the caller's half of the contract; everything after it is the specialist's.

One subagent owns the scene, and only the scene. Its brief is the project's `DESIGN.md` quoted verbatim plus the matching cheat under `references/ingredients/` (`web3d-for-sites.md`, `ogl-shaders.md`, `web-audio.md`); it returns a self-contained scene module — props in, canvas out. The scene clears the fidelity floor below (physical materials, an HDRI environment, no primitive geometry as the hero object) and the input-correctness floor further down (no native drag-ghost, hit-area on the object), and it meets the measured perf budget through the poster-first path. Integrate the returned module yourself; never co-write a file — a shared file is where the scene's disposal and the page's lifecycle silently disagree.

## Read the universe first

Before any geometry, pull from `DESIGN.md` and bind to it:

- **Color** — `colors.*`. Scene background, light colors, material base, fog, accent emissive all resolve from tokens. No black void unless the palette is dark. Feed hex into `new THREE.Color(token)`; interpolate in OKLCH where the DESIGN.md gradient story does.
- **Motion** — `motion.ease-*` and `motion.duration-*`. Camera moves, hover springs, and transition timing reuse the page's easing curves, not `THREE.MathUtils.lerp` at an ad-hoc rate. Match the site's motion signature so the canvas feels of-a-piece.
- **Mood + density** — the Overview atmosphere scores (Density / Variance / Motion) set particle count, fog thickness, light count, and idle drift amplitude. A calm editorial brief gets near-still; a high-energy brief earns sustained motion.
- **Type** — real headings stay in the DOM (see SSR boundary). 3D text is rare; when the signature needs it, match the DESIGN.md display face via `troika-three-text`, never a default helvetiker.

The discipline that separates winners: fog instead of textures, light instead of detail. Lean scenes lit well beat busy scenes.

## Fidelity floor — the object must read premium

The delegation's job is not "a scene renders" — it is *a scene a jury reads as premium*. A studio-lit primitive is the slop tell. When the signature is a real object (a product, a vehicle, a figure), it clears these or it is not shipped as the signature:

- **Physical material, not a toy shader.** Glass/liquid: `MeshPhysicalMaterial` with `transmission`, `roughness`, `ior` (~1.5 glass), `thickness`, and `attenuationColor`/`attenuationDistance` for the tint — never a flat `MeshStandardMaterial` with an opacity hack. Metal (a cap, a bezel): `metalness: 1`, low `roughness`, a real environment to reflect. A plastic-looking cap is the tell that sinks the whole object.
- **An HDRI environment does the lighting.** Reflections and specular life come from `<Environment>` (Drei) or an equirect `.hdr` via `RGBELoader` — not three `pointLight`s on a black void. A *dark* scene still needs an env map; that is where the edge-light and the glass depth come from. `ACESFilmicToneMapping`, sRGB output.
- **No primitive geometry as the hero object.** A lathe/extrude/box silhouette reads as placeholder at close range (`imagery.md` silhouette test). Prefer a real `.glb` (modelled, DRACO-compressed); if hand-built, push the profile past the primitive — chamfers, real shoulders, a filleted base, a debossed label — until the silhouette is nameable as *that* product, not "a bottle shape."
- **Grade the render into the page.** Subtle post (bloom only on genuinely emissive, vignette, grain) tuned to the DESIGN.md, so the render seats in the page's treatment like every photograph does (`imagery.md` one-treatment).

**Fidelity self-check before integration:** put a frame of the scene beside a real product render of the same category and ask the `imagery.md` silhouette question — *would a stranger read this as a premium product photo, or clock it as CGI?* CGI-clocked → fix material/lighting/geometry, or drop to the real-media signature (a scroll-scrubbed real video, `signature-invention.md`). A 60fps primitive is still a fail.

## Three.js vs R3F + Drei

- **R3F + Drei** — default for any React build (this skill's TanStack Start path). Declarative scene graph, `useFrame` for per-frame work, automatic disposal of objects the reconciler owns, and Drei's site-grade helpers (`<Environment>`, `<Float>`, `<Instances>`, `<Detailed>`, `<View>`, `<AdaptiveDpr>`, `<PerformanceMonitor>`). Author against this unless told otherwise.
- **Raw Three.js** — reach for it when there is no React in the target stack (an Astro island holding a single imperative canvas), or for a hand-tuned render loop / custom WebGLRenderTarget pipeline R3F would fight. You own the dispose graph yourself.
- **OGL** — shader-only effects (a fragment-shader gradient field, an image-distortion plane) where a full scene graph is unnecessary. Resolve versions through `../stack-facts.md`; bundle cost comes from the actual build.

Signature vs noise: 3D is the signature when it carries the brief — the product rotated through scroll, a generative hero that is the brand. It is noise when it floats behind real content as ambient decoration that costs LCP and battery for no memory gain. If a CSS gradient + grain would read the same, do that instead and skip the canvas.

## Canonical R3F setup (site-tilted)

Keep the canvas off the critical path and idle when nothing moves.

```tsx
// Scene.tsx — client-only module, dynamically imported by the page
import { Canvas } from '@react-three/fiber'
import { AdaptiveDpr } from '@react-three/drei'

export default function Scene() {
  return (
    <Canvas
      dpr={[1, 2]}                 // clamp pixelRatio; never raw devicePixelRatio
      frameloop="demand"           // render only on change; see invalidate below
      gl={{ antialias: true, powerPreference: 'high-performance' }}
      camera={{ position: [0, 0, 6], fov: 35 }}
    >
      <AdaptiveDpr pixelated />     {/* drop resolution under load, restore when idle */}
      {/* lights + meshes resolve their colors from DESIGN.md tokens */}
    </Canvas>
  )
}
```

```tsx
// Page island — dynamic import keeps Three off the initial bundle,
// lazy-init defers mount until the hero scrolls into view.
import { lazy, Suspense, useEffect, useRef, useState } from 'react'
const Scene = lazy(() => import('./Scene'))

export function Hero() {
  const ref = useRef<HTMLDivElement>(null)
  const [show, setShow] = useState(false)
  useEffect(() => {
    const io = new IntersectionObserver(([e]) => e.isIntersecting && (setShow(true), io.disconnect()), {
      rootMargin: '200px',
    })
    ref.current && io.observe(ref.current)
    return () => io.disconnect()
  }, [])
  return (
    <div ref={ref} aria-hidden="true">
      {show && <Suspense fallback={null}><Scene /></Suspense>}
    </div>
  )
}
```

With `frameloop="demand"`, Fiber renders React changes as needed. Mutations outside React — an imperative control, a scroll handler, a tween — must request a frame:

```tsx
const { invalidate } = useThree()
controls.current.addEventListener('change', invalidate)  // and on every scroll/tween tick
```

A continuously animating scene (idle particle drift) uses `frameloop="always"` instead; reserve `demand` for scenes static between interactions. Both pause offscreen via the page-visibility gate below.

## Site-tilted patterns

- **Scroll-linked camera / material** — drive from the page's existing scroll source, never a second listener. If a GSAP or Lenis skill is installed, **defer the motion layer to it by name** (`github.com/greensock/gsap-skills`) and consume the progress it produces. Read scroll progress, write to scene state, `invalidate()`:

  ```tsx
  useFrame(() => {                          // or a Lenis/ScrollTrigger callback
    camera.position.z = THREE.MathUtils.lerp(6, 2, scroll.current)  // ease via DESIGN.md curve
  })
  ```

- **Vertex displacement on hover** — push verts along normals by a noise field in the vertex shader; ramp the amplitude uniform toward the pointer with the DESIGN.md hover easing. Cheaper and more organic than swapping geometry.
- **GPU particles** — one `THREE.Points` (or Drei `<Instances>` for lit meshes) with a custom GLSL `ShaderMaterial`; animate position in the vertex shader from a `uTime` uniform. Count comes from the atmosphere Density score. CPU-side per-particle updates do not scale — keep motion on the GPU.
- **Image-to-image transition via noise** — two textures in a fragment shader, mixed by a `step`/`smoothstep` over a noise texture against a `uProgress` uniform. Drive `uProgress` from scroll or hover. The signature dissolve for portfolio thumbnails.
- **Post-processing** — `@react-three/postprocessing`, subtle. Bloom only on genuinely emissive material; vignette and grain to seat the render in the page's mood. Tune intensities to the DESIGN.md, not the demo defaults.

  ```tsx
  import { EffectComposer, Bloom, Vignette, Noise } from '@react-three/postprocessing'
  <EffectComposer>
    <Bloom intensity={0.4} luminanceThreshold={0.9} mipmapBlur />
    <Vignette eskil={false} offset={0.3} darkness={0.5} />
    <Noise opacity={0.025} />
  </EffectComposer>
  ```

## Performance discipline

- **Instance repeated geometry** — `<Instances>` / `InstancedMesh` for any geometry drawn more than a handful of times. One draw call for thousands.
- **LOD** — Drei `<Detailed distances={[0, 10, 20]}>` swaps mesh density by camera distance; serve a low-poly `.glb` far out.
- **Dispose on unmount** — R3F auto-disposes objects in its tree. Objects you create imperatively (geometries, materials, `WebGLRenderTarget`, manually loaded textures held in refs) you dispose yourself in the effect cleanup. Leaked GPU memory is the most common 3D regression.
- **Cap pixelRatio** — `dpr={[1, 2]}`; a retina phone at raw DPR renders 9× the pixels for no visible gain.
- **Pause offscreen** — mount the activity component below inside `<Canvas>`. Fiber owns its render loop: use `setFrameloop`, not `gl.setAnimationLoop`. Intersection and tab visibility are ANDed; reduced motion allows a still demand-rendered scene. Every animation/scroll mutator must also honor the reduced branch below.

```javascript
import { useEffect, useState } from 'react';
import { useThree } from '@react-three/fiber';

export function useReducedMotion() {
  const [reduced, setReduced] = useState(true); // static during server render and hydration
  useEffect(() => {
    const query = matchMedia('(prefers-reduced-motion: reduce)');
    const update = () => setReduced(query.matches);
    update();
    query.addEventListener('change', update);
    return () => query.removeEventListener('change', update);
  }, []);
  return reduced;
}

export function SceneActivity() {
  const { gl, get, setFrameloop, invalidate } = useThree();
  const reduced = useReducedMotion();
  useEffect(() => {
    const previousMode = get().frameloop;
    let onScreen = false;
    let visible = !document.hidden;
    const sync = () => {
      const active = onScreen && visible;
      setFrameloop(active ? (reduced ? 'demand' : previousMode) : 'never');
      if (active) invalidate();
    };
    const io = new IntersectionObserver(([entry]) => { onScreen = entry.isIntersecting; sync(); });
    const onVisibility = () => { visible = !document.hidden; sync(); };
    io.observe(gl.domElement);
    document.addEventListener('visibilitychange', onVisibility);
    sync();
    return () => {
      io.disconnect();
      document.removeEventListener('visibilitychange', onVisibility);
      setFrameloop(previousMode);
    };
  }, [gl, get, setFrameloop, invalidate, reduced]);
  return null;
}
```

This uses the documented Fiber render-mode API; verify the installed version's behavior through `stack-facts.md`, especially when multiple canvases share a scheduler. A poster-only reduced branch may instead unmount the scene and its activity component.

- **Keep draw calls low** — merge static geometry, share materials, atlas textures. Watch the count in `r3f-perf`.

**LCP** — a hydrating canvas is never the LCP element and must not block it. Ship a **poster-first** hero: render a static image (a frame of the scene, AVIF) as the real LCP paint, then mount and crossfade the canvas in after hydration on viewport intersection. The DOM heading paints immediately; the WebGL arrives second. This is how shader-heavy sites still hit LCP ~1.3s.

## Two-tier texture streaming — the hold-gate

A scroll journey that closes in on a textured surface faces a fork with one tier: load the fine texture up front (arrival gates blow) or load the coarse one only (the close frames render soft — a fidelity-floor violation the user reads instantly). Stream two tiers and gate the camera:

- **Base tier through the tracked `LoadingManager`** — a ~2k color map the branded loader counts; arrival stays instant and the wide framing reads sharp on it.
- **Fine tier after `ready`** — the 8k color + displacement maps load through a *separate, untracked* `TextureLoader` on `requestIdleCallback`, fine-pointer + wide viewports only (at touch pixel density the base tier is indistinguishable — never spend the bytes).
- **Atomic swap, off the hot path** — pre-upload with `renderer.initTexture()` so the GPU decode never lands on an animation frame; swap material maps (and re-tessellate the geometry if displacement joins, e.g. 96→192 segments) during a calm early phase of the journey, never mid-peak.
- **The camera hold-gate** — until the swap, camera progress is clamped: `pCam = min(progress, HOLD + (1 − HOLD) · gateT)`, where `HOLD` is the deepest point at which the base tier still reads sharp and `gateT` eases 0→1 once the fine tier lands. The scrollbar stays honest; only the camera's depth waits, and the inertial lerp absorbs the catch-up. Fidelity never chases the scroll — the scroll waits for fidelity.

Verify on a throttled network: drive to the deepest frame and screenshot the **compositor** (`preserveDrawingBuffer: false` makes canvas readback lie — a black probe on a rendering scene). The close-up must never show the base tier.

## SSR / island boundary

The canvas is **client-only** — WebGL has no server render.

- **Astro** — `<Scene client:only="react" />`. Never `client:load` (the canvas has no SSR HTML to hydrate).
- **TanStack Start** — a client component, dynamically imported so it stays out of the server bundle and the critical path.
- **Real content lives in the DOM** — headings, copy, links, and CTAs are HTML behind or beside the canvas, never drawn inside it. The canvas is an `aria-hidden` visual layer over a fully functional page.

## Interactive input-correctness floor

A rotate/drag/pointer signature that fights the browser reads as broken, however good the render. Every one of these holds before it ships — this is the class of bug that has shipped:

- **Kill native drag and selection on the interactive surface.** The canvas and *any* poster/fallback `<img>` under it: `draggable="false"` (the attribute, on every img), `user-select: none`, `-webkit-user-drag: none`, `-webkit-touch-callout: none`. A draggable poster under the canvas hijacks the drag and shows the browser's native ghost image — the ugliest artifact in this set.
- **`touch-action: none`** on the interactive element so a drag rotates instead of scrolling the page on touch; `preventDefault()` on `pointerdown` / `touchstart` in the handler.
- **The hit-area is the object, not the neighbourhood.** The listener target (canvas or an overlay) covers the *visible object* and does not bleed onto the headline or CTAs. A grab cursor that responds over the title while the object ignores the pointer is a mislaid hit-area — size and position the interactive layer to the object, and verify by dragging *on the object* and *on the title*.
- **A designed affordance, not the native grab-hand.** The system `cursor: grab`/`grabbing` hand is a tell on a luxury surface — ship a custom cursor, a one-time hint that fades on first interaction, or a subtle rig in the DESIGN.md voice.
- **Verified as a real user drags.** Synthetic pointer events bypass native drag-and-drop and hide the ghost bug; the review drives a *real* mouse drag and a touch drag (`gate/review.md`) and confirms no native ghost, no text selection, the object (not the title) responding, smooth on both.

## Reduced motion + accessibility

- **`prefers-reduced-motion`** — render a static poster frame or a still scene: no autoplay camera drift, no idle particle motion, no scroll-driven rotation. Branch at mount; if a GSAP skill drives the motion, its `matchMedia` reduced branch governs the scene too.

  ```tsx
  const reduced = useReducedMotion()  // the local matchMedia hook above
  useFrame((_, dt) => { if (!reduced) mesh.rotation.y += dt * 0.1 })
  ```

- **`aria-hidden="true"`** on the canvas wrapper — it is decoration to assistive tech.
- **Never put information only in 3D** — any text, number, or navigation a user needs exists in the accessible DOM. The scene adds atmosphere, never sole-source content. Keyboard and screen-reader users get the whole page without the canvas.

## Defer by name

If an official GSAP or R3F skill is installed, use it for the motion layer rather than re-deriving timelines and scroll wiring here — `github.com/greensock/gsap-skills` for GSAP/ScrollTrigger, the pmndrs R3F skill for scene scaffolding. This cheat is the fallback and the integration contract; a maintained skill is the current source for that library's API.

Sourcing the API is not the same as *using the medium well*. A scene that imports Three.js but ships a primitive on three point-lights has consulted the docs and ignored their craft. Use the premium path the docs and Drei give you — `<Environment>`, `MeshPhysicalMaterial`, `<Instances>`, post-processing — never the first-example primitive. "Sourced but low-effort" fails the fidelity floor above, and the review chunk judges the craft level, not the citation.

## Contact rigs — the object that reacts where you touch it

A press whose only response is a whole-element `scale()` reads as a paper cutout — the object moves as one rigid sticker, and the detector fails it (`CONTACT-GLOBAL-SQUASH`, `detector.md`). A contact rig deforms the object *at the impact point*. Two rigs keep real photography while gaining contact physics:

- **Mesh-warp-on-photo** — a subdivided plane (`PlaneGeometry`, ~64×64 segments) textured with the real photograph, never a generated stand-in. On `pointerdown`, raycast the hit to UV space, pass it as a uniform, and displace vertices toward the impact point in the vertex shader — amplitude falls off with distance from the hit UV and decays on a spring. The photo dents where it is struck: material truth stays intact (`imagery.md` still governs the source image) and the surface gains physics. Keep the displacement on the GPU; the CPU only writes the hit uniform and the spring state.
- **Depth-mapped 2.5D** — the photograph plus a depth map (shot, or estimated offline and exported as a grayscale texture) sampled in the shader: pointer position drives parallax between depth layers, and the press pushes the near layers locally around the hit point. Cheaper than a modelled mesh, and the object reads as a body with volume rather than a sticker.

**Register.** The deformation obeys the archetype DNA like every other motion: easing and shading resolve from `DESIGN.md`, never a default fleshy spring. A raw register wants a hard, stepped displacement — quantized falloff, no smoothing; a couture register wants a slow, damped settle. The default spring constant is the 3D equivalent of the default ease — a tell.

**Perf.** One small scene: a single plane, one texture (plus the depth map), one draw call. Poster-first LCP is unchanged — the static photograph stays the LCP paint and the rig mounts behind it on intersection, like every canvas here. `frameloop="demand"`, `invalidate()` from the pointer handlers, and the spring loop stops requesting frames once displacement falls under a visible threshold.

## Cross-references

`../immersive-cinematic.md` (the archetype this scene usually serves), `../foundations.md` (WebGL toolkit, OKLCH, easing curves), `../production-hardening.md` (iOS Safari, viewport units, autoplay), `../premium-patterns.md` (procedural noise discipline, motion budget).
