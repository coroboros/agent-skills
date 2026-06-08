# Web 3D for sites — Three.js / R3F specialist cheat

You author ONE self-contained scene module — props in, canvas out, no shared files. The build is a marketing or portfolio site, not a game: the 3D earns the page memory, then gets out of the way. You are handed the project's `DESIGN.md`. The scene is an expression of that committed universe — its palette, easing, mood, and type — never generic 3D defaults. A studio-lit chrome torus on a `#202020` stage with `OrbitControls` is the slop tell judges read in seconds.

## Read the universe first

Before any geometry, pull from `DESIGN.md` and bind to it:

- **Color** — `colors.*`. Scene background, light colors, material base, fog, accent emissive all resolve from tokens. No black void unless the palette is dark. Feed hex into `new THREE.Color(token)`; interpolate in OKLCH where the DESIGN.md gradient story does.
- **Motion** — `motion.ease-*` and `motion.duration-*`. Camera moves, hover springs, and transition timing reuse the page's easing curves, not `THREE.MathUtils.lerp` at an ad-hoc rate. Match the site's motion signature so the canvas feels of-a-piece.
- **Mood + density** — the Overview atmosphere scores (Density / Variance / Motion) set particle count, fog thickness, light count, and idle drift amplitude. A calm editorial brief gets near-still; a high-energy brief earns sustained motion.
- **Type** — real headings stay in the DOM (see SSR boundary). 3D text is rare; when the signature needs it, match the DESIGN.md display face via `troika-three-text`, never a default helvetiker.

The discipline that separates winners: fog instead of textures, light instead of detail. Lean scenes lit well beat busy scenes.

## Three.js vs R3F + Drei

- **R3F + Drei** — default for any React build (this skill's TanStack Start path). Declarative scene graph, `useFrame` for per-frame work, automatic disposal of objects the reconciler owns, and Drei's site-grade helpers (`<Environment>`, `<Float>`, `<Instances>`, `<Detailed>`, `<View>`, `<AdaptiveDpr>`, `<PerformanceMonitor>`). Author against this unless told otherwise.
- **Raw Three.js** — reach for it when there is no React in the target stack (an Astro island holding a single imperative canvas), or for a hand-tuned render loop / custom WebGLRenderTarget pipeline R3F would fight. ~150KB. You own the dispose graph yourself.
- **OGL** (~29KB) — shader-only effects (a fragment-shader gradient field, an image-distortion plane) where a full scene graph is dead weight.

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

With `frameloop="demand"`, nothing renders until you call `invalidate()`. Any mutation outside React — `OrbitControls`, a scroll handler, a tween — must request a frame:

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
- **Pause offscreen** — gate the loop on tab visibility and viewport intersection; a hidden canvas burning the GPU drains battery and trips thermal throttling.

  ```tsx
  useEffect(() => {
    const onVis = () => (document.hidden ? gl.setAnimationLoop(null) : invalidate())
    document.addEventListener('visibilitychange', onVis)
    return () => document.removeEventListener('visibilitychange', onVis)
  }, [])
  ```

- **Keep draw calls low** — merge static geometry, share materials, atlas textures. Watch the count in `r3f-perf`.

**LCP** — a hydrating canvas is never the LCP element and must not block it. Ship a **poster-first** hero: render a static image (a frame of the scene, AVIF) as the real LCP paint, then mount and crossfade the canvas in after hydration on viewport intersection. The DOM heading paints immediately; the WebGL arrives second. This is how shader-heavy sites still hit LCP ~1.3s.

## SSR / island boundary

The canvas is **client-only** — WebGL has no server render.

- **Astro** — `<Scene client:only="react" />`. Never `client:load` (the canvas has no SSR HTML to hydrate).
- **TanStack Start** — a client component, dynamically imported so it stays out of the server bundle and the critical path.
- **Real content lives in the DOM** — headings, copy, links, and CTAs are HTML behind or beside the canvas, never drawn inside it. The canvas is an `aria-hidden` visual layer over a fully functional page.

## Reduced motion + accessibility

- **`prefers-reduced-motion`** — render a static poster frame or a still scene: no autoplay camera drift, no idle particle motion, no scroll-driven rotation. Branch at mount; if a GSAP skill drives the motion, its `matchMedia` reduced branch governs the scene too.

  ```tsx
  const reduced = useReducedMotion()  // @react-three/drei
  useFrame((_, dt) => { if (!reduced) mesh.rotation.y += dt * 0.1 })
  ```

- **`aria-hidden="true"`** on the canvas wrapper — it is decoration to assistive tech.
- **Never put information only in 3D** — any text, number, or navigation a user needs exists in the accessible DOM. The scene adds atmosphere, never sole-source content. Keyboard and screen-reader users get the whole page without the canvas.

## Defer by name

If an official GSAP or R3F skill is installed, use it for the motion layer rather than re-deriving timelines and scroll wiring here — `github.com/greensock/gsap-skills` for GSAP/ScrollTrigger, the pmndrs R3F skill for scene scaffolding. This cheat is the fallback and the integration contract; a maintained skill is the current source for that library's API.

## Cross-references

`../immersive-cinematic.md` (the archetype this scene usually serves), `../foundations.md` (WebGL toolkit, OKLCH, easing curves), `../production-hardening.md` (iOS Safari, viewport units, autoplay), `../premium-patterns.md` (procedural noise discipline, motion budget).
