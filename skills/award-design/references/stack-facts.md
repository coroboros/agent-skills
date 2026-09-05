# Stack facts — the dated single source

Every version, package name, Baseline status, support percentage, and performance threshold this skill cites lives here, once, with the date it was last checked. No other reference may state one of these numbers — they point here, and a number quoted from memory anywhere else is a bug.

## How to read a row

- **checked** — when the row was last verified. `STACK-FACTS-STALE` (`scripts/preflight_scan.py`) emits a REVIEW notice once any row passes 180 days.
- **verdict** — the refresh ladder. **fetch** = re-verify before relying on it, every time, via `external-truth.md`'s ladder; the value moves fast enough that a stale row is a wrong row. **trust** = the shape is stable; re-check on a major version or when something breaks.
- **fetch-class is narrow on purpose**: Three.js and its WebGPU surface, GSAP SplitText's API and licensing, and every browser-support figure. Everything else earns **trust** — treating it as fetch-class burns a lookup on an answer that has not changed in two years.

## Motion libraries

| Fact | Value | Checked | Verdict | Source |
|---|---|---|---|---|
| GSAP current version | 3.15.0 (published 2026-04-13) | checked: 2026-07 | trust | registry.npmjs.org/gsap |
| GSAP licensing | 100% free for all users, Webflow-funded — every former Club plugin ships in the public package | checked: 2026-07 | trust | gsap.com/pricing |
| GSAP package / import | `gsap`, plugins at `gsap/ScrollTrigger`, `gsap/SplitText` | checked: 2026-07 | trust | gsap.com/docs/v3 |
| GSAP plugin registration | `gsap.registerPlugin(ScrollTrigger)` required before any trigger | checked: 2026-07 | trust | gsap.com/docs/v3 |
| SplitText bundled free since | GSAP 3.13.0 (`dist/SplitText.js` inside the public tarball; absent at 3.12.7) | checked: 2026-07 | fetch | gsap.com/pricing · npm tarball |
| SplitText current factory | `SplitText.create(target, vars)` — static, the documented form | checked: 2026-07 | fetch | gsap.com/docs/v3/Plugins/SplitText |
| SplitText `autoSplit` / `mask` / `onSplit` | all current; introduced in the 3.13.0 rewrite. `mask` takes `"lines" \| "words" \| "chars"` | checked: 2026-07 | fetch | gsap.com/docs/v3/Plugins/SplitText |
| SplitText a11y | `aria: "auto"` keeps the source string readable after the split | checked: 2026-07 | fetch | gsap.com/docs/v3/Plugins/SplitText |
| Lenis current version | 1.3.25 | checked: 2026-07 | trust | registry.npmjs.org/lenis |
| Lenis package name | `lenis`. `@studio-freight/lenis` is **deprecated** (frozen at 1.0.42, carries a rename notice) | checked: 2026-07 | trust | registry.npmjs.org/lenis |
| Lenis `autoRaf` | real constructor option, **defaults to `false`** — pass it only when nothing else drives `raf()` | checked: 2026-07 | trust | github.com/darkroomengineering/lenis |
| Lenis + GSAP wiring | `lenis.on('scroll', ScrollTrigger.update)` · `gsap.ticker.add(t => lenis.raf(t * 1000))` · `gsap.ticker.lagSmoothing(0)` — one clock, never two (`skeletons.md` §A) | checked: 2026-07 | trust | github.com/darkroomengineering/lenis |
| Motion (ex-Framer Motion) import | package `motion`, React entry `motion/react`. `framer-motion` is the stale name | checked: 2026-07 | trust | motion.dev/docs |
| GSAP bundle size | ~23 KB min+gzip — 2025 figure, **not re-measured**; measure before quoting it in a budget | checked: 2026-07 | fetch | pkg-size / bundlephobia |
| Motion bundle size | ~34 KB, ~4.6 KB lazy — 2025 figure, **not re-measured** | checked: 2026-07 | fetch | pkg-size / bundlephobia |
| Lenis bundle size | ~2 KB — 2025 figure, **not re-measured** | checked: 2026-07 | fetch | pkg-size / bundlephobia |
| Motion One | package `@motionone/dom` — the lightweight vanilla animator when neither GSAP nor Motion is warranted. ~3.8 KB, 2025 figure, **not re-measured** | checked: 2026-07 | fetch | motion.dev |
| Locomotive v5 | parallax + scroll detection; Lenis superseded it for smoothing, so it is a legacy encounter, not a choice. ~9.4 KB, 2025 figure, **not re-measured** | checked: 2026-07 | fetch | github.com/locomotivemtl/locomotive-scroll |

## 3D

| Fact | Value | Checked | Verdict | Source |
|---|---|---|---|---|
| Three.js current release | r185 (2026-07-01), npm `three@0.185.1` | checked: 2026-07 | fetch | github.com/mrdoob/three.js/releases |
| Three.js WebGPU import path | `import * as THREE from 'three/webgpu'` — a real `package.json` export | checked: 2026-07 | fetch | threejs.org/manual (WebGPURenderer) |
| Three.js WebGPU minimum revision | **r167** — the `./webgpu` export and async `Renderer.init()` both landed there (absent in 0.166.0) | checked: 2026-07 | fetch | three.js Migration Guide · npm exports diff |
| WebGPURenderer maturity | **still officially experimental** — "greatly improved" but not graduated. Ship it behind a poster and the WebGL2 fallback | checked: 2026-07 | fetch | threejs.org/manual (WebGPURenderer) |
| WebGPURenderer init | `await renderer.init()` before the first render — requests the adapter, or falls back to WebGL2 | checked: 2026-07 | fetch | threejs.org/manual |
| React Three Fiber / drei | Requires a React rendering context; use only where the existing project supplies one, including an intentional React island. Do not add React solely for a copied example | checked: 2026-09 | trust | r3f.docs.pmnd.rs/getting-started/introduction |
| OGL | the light shader path when Three.js is more engine than the signature needs | checked: 2026-07 | trust | github.com/oframe/ogl |
| Three.js bundle size | ~150 KB — 2025 figure, **not re-measured**; tree-shaking moves it a lot | checked: 2026-07 | fetch | pkg-size / bundlephobia |
| OGL bundle size | ~29 KB — 2025 figure, **not re-measured** | checked: 2026-07 | fetch | pkg-size / bundlephobia |
| WebGPU-vs-WebGL throughput | **no verified figure.** The "200K objects at 60fps vs 15K at 15fps" line carried in foundations.md was an unreproduced vendor benchmark and is retired — measure your own scene | checked: 2026-07 | fetch | — (retired claim) |

## Browser support — the Baseline ladder

Tiers per `modern-web-baseline.md`: **Widely** → adopt unguarded · **Newly** → progressive enhancement (~30 months from Newly to Widely) · **Limited / not Baseline** → progressive enhancement only, behind `@supports` or a feature detect, with a content-complete fallback.

| Fact | Value | Checked | Verdict | Source |
|---|---|---|---|---|
| Scroll-driven animations (`animation-timeline`) | **Limited — not Baseline** | checked: 2026-07 | fetch | webstatus.dev/features/scroll-driven-animations |
| Scroll-driven — global support | **83.66%** (dataset 2026-07-16). This is the **only** figure the skill quotes; the old ~85% and ~82% claims are dead | checked: 2026-07 | fetch | caniuse.com/mdn-css_properties_animation-timeline |
| Scroll-driven — engines | Chrome/Edge 115 · Safari 26 (2025-09-15) · **Firefox stable: off** (pref `layout.css.scroll-driven-animations.enabled`, Nightly-only). It is an Interop priority, so the fallback tax is temporary, not structural | checked: 2026-07 | fetch | MDN BCD · Firefox StaticPrefList.yaml |
| Same-document View Transitions | **Newly available, 2025-10-14** (Firefox 144 completed it) — guard with `document.startViewTransition` | checked: 2026-07 | fetch | webstatus.dev/features/view-transitions |
| Cross-document View Transitions | **Limited — not Baseline.** Chrome 126 · Safari 18.2 · no Firefox. `@view-transition { navigation: auto }` degrades to a plain navigation | checked: 2026-07 | fetch | webstatus.dev/features/cross-document-view-transitions |
| Scoped view transitions | **Limited** — Chromium 147 only (2026-04-07) | checked: 2026-07 | fetch | webstatus.dev/features/view-transitions-element-scoped |
| `animation-trigger` | **Limited, status "Proposed"** — Chrome 146 only, no Firefox or Safari signal. The future fire-once primitive, not a shippable one. No MDN BCD key and no web-features id yet, so Chrome Platform Status is the only re-verifiable source | checked: 2026-07 | fetch | chromestatus.com/api/v0/features/5181996801982464 |
| `text-box-trim` / `text-box-edge` | **Limited** — Chrome 133 · Safari 18.2 · Firefox 154 in beta (stable 153.0.1; 154 ships 2026-08-14, which flips this to Newly). caniuse 81.25% | checked: 2026-07 | fetch | webstatus.dev/features/text-box · caniuse.com/mdn-css_properties_text-box-trim |
| `content-visibility` | **Newly available, 2025-09-15** (Safari 26 completed it) — no-ops where unsupported | checked: 2026-07 | fetch | webstatus.dev/features/content-visibility |
| Relative colour syntax (`oklch(from …)`) | **Newly available, 2024-09-16** — author a cascade fallback | checked: 2026-07 | fetch | webstatus.dev/features/relative-color |
| `@property` | **Newly available, 2024-07-09** (feature `registered-custom-properties`) | checked: 2026-07 | fetch | webstatus.dev/features/registered-custom-properties |
| `:has()` | **Widely available** — Newly 2023-12-19, Widely **2026-06-19**. Recently graduated; adopt unguarded | checked: 2026-07 | fetch | webstatus.dev/features/has |
| CSS subgrid | **Widely available** — Newly 2023-09-15, Widely **2026-03-15**. Recently graduated; adopt unguarded | checked: 2026-07 | fetch | webstatus.dev/features/subgrid |
| Container queries | **Widely available** — Newly 2023-02-14, Widely 2025-08-14 | checked: 2026-07 | fetch | webstatus.dev/features/container-queries |
| `oklch()` authoring colour | **Widely available** (since 2023) — adopt unguarded | checked: 2026-07 | fetch | web.dev Baseline · MDN |
| `svh` / `lvh` / `dvh` | **Widely available** — adopt unguarded; never `vh` in new code (`foundations.md` Layout) | checked: 2026-07 | fetch | web.dev Baseline · MDN |
| Speculation Rules (`prerender`) | Chromium only; a no-op elsewhere, so it ships unguarded as pure enhancement | checked: 2026-07 | fetch | developer.chrome.com/speculation-rules |
| Anything not listed | **unknown** — verify Baseline first, then place it in a tier | checked: 2026-07 | fetch | `external-truth.md` ladder |

## Performance thresholds

| Fact | Value | Checked | Verdict | Source |
|---|---|---|---|---|
| Core Web Vitals — official "good" at p75 | LCP ≤ 2.5s · INP ≤ 200ms · CLS ≤ 0.1 | checked: 2026-07 | trust | web.dev/articles/vitals |
| This skill's award-grade stretch | LCP < 1.5s · CLS < 0.05 · INP < 100ms · ≥55fps sustained | checked: 2026-07 | trust | `award-imperatives.md` #7 |
| The two are not the same | State the stretch as the studio target it is — never as "Google's baseline" | checked: 2026-07 | trust | `modern-web-baseline.md` |
| Transfer budget | **no byte cap** — weight is phased (critical path lean, heavy assets streamed behind a designed loader) | checked: 2026-07 | trust | `award-imperatives.md` #7 |
| WCAG interactive target minimum | 24×24 CSS px (SC 2.5.8, Level AA) — the one place CSS px is the normative unit | checked: 2026-07 | trust | W3C WCAG 2.2 |
| Legal accessibility floor | EAA 2025 / EN 301 549 = WCAG **AA** | checked: 2026-07 | trust | `modern-web-baseline.md` |
| Device pixel ratio cap for 3D | 2 — above it, fill rate is spent for no visible sharpness. A house heuristic, not a vendor figure; `skeletons.md` §E applies it | checked: 2026-07 | trust | house rule (this file is its origin) |

## Frameworks and build

| Fact | Value | Checked | Verdict | Source |
|---|---|---|---|---|
| Astro | the content/perf path (Minimalist, Editorial, Corporate-Luxury, Bento) — zero JS by default is the LCP win | checked: 2026-07 | trust | docs.astro.build |
| TanStack Start | the motion/3D path (Immersive, Experimental, Bold, Spatial-Organic) — React on Vite + Nitro. **No release number carried**: the previous claim ("v1 RC, API-stable") was an undated memory quote, and a framework version pinned into a lockfile is the one fact worth resolving live every time. Resolve it before scaffolding | checked: 2026-07 | fetch | tanstack.com/start |
| Host portability | Nitro, 40+ deploy presets — hosting stays orthogonal to the build | checked: 2026-07 | trust | nitro.build |
| Tailwind v4 PostCSS | `@tailwindcss/postcss` or the Vite plugin. Bare `tailwindcss` as a PostCSS plugin is the v3 shape | checked: 2026-07 | trust | tailwindcss.com/docs |
| Vite-path font loading | Fontsource / unplugin-fonts (the `next/font` replacement) | checked: 2026-07 | trust | fontsource.org |
| Vite-path images | vite-imagetools / unpic, or a host image loader | checked: 2026-07 | trust | github.com/JonasKruckenberg/imagetools |
| React `<ViewTransition />` | React's own wrapper over the same-document API on the React path — **status not re-verified**; resolve it before use, the vanilla guard (`skeletons.md` §F) works everywhere | checked: 2026-07 | fetch | react.dev |
| Existing project's stack | always wins — adapt, never migrate | checked: 2026-07 | trust | `foundations.md` Stack |

## Assets and delivery

| Fact | Value | Checked | Verdict | Source |
|---|---|---|---|---|
| Raster cascade | AVIF > WebP > JPEG via `<picture>`; AVIF ~50% smaller than JPEG | checked: 2026-07 | trust | web.dev/serve-images-avif |
| Font delivery | self-host (or the framework's font module) + `font-display: swap` + `<link rel="preload" as="font" crossorigin>` | checked: 2026-07 | trust | web.dev/font-best-practices |
| Google Fonts `<link>` in production | a third-party request on the critical path and a GDPR exposure — never | checked: 2026-07 | trust | `foundations.md` Performance |
| Above/below-fold image hints | `fetchpriority="high"` above the fold, `loading="lazy"` below; explicit `width`/`height` on every `<img>` | checked: 2026-07 | trust | web.dev/lcp |
| Animation cost | Prefer `transform` and `opacity`; compositor execution depends on the effect and rendering context. Measure filters, backdrop filters, and other animated properties on target devices | checked: 2026-09 | trust | developer.chrome.com/docs/css-ui/scroll-driven-animations |
| Audit viewport range | 320–1920 CSS px; 1920 is the full-bleed resolution floor the scanner measures against | checked: 2026-07 | trust | `scripts/preflight_scan.py` IMG-NATIVE-RES |

## Refreshing this file

Re-verify through `external-truth.md`'s ladder — installed skill, then the install offer, then `find-docs` / `context7-cli` / the official URL. Update the **value** and the **checked** date together; a date bumped without a lookup is worse than a stale row, because the staleness notice then lies. Rows marked **fetch** are the ones a refresh pass exists for; the **trust** rows are swept on a major version or when a build breaks against them.
