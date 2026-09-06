# External Truth — capability gates

Award-grade builds live or die on library APIs that move faster than any training corpus: GSAP's plugins went free and its SplitText syntax changed, Three.js shipped WebGPU, same-document View Transitions went Newly available, Tailwind v4 dropped its PostCSS plugin. Code written from memory for these layers is where confident-looking builds silently break — so each heavy layer passes this gate before its first line of code.

## The rung ladder — walk in order, stop at the first rung that resolves

1. **Available capability and installed skill.** Inspect the harness's actual tools and installed skill adapters. Use a suitable capability through its documented interface; a vendor or model name does not prove availability. Record exact errors for unusable tools before selecting another supported path.
2. **Fetch current docs.** For APIs, use the installed documentation flow (`find-docs`, `context7-cli` / `ctx7`, then official web docs) before coding. Cite what was actually read. A missing optional skill does not block an available official-docs path.
3. **Missing prerequisite.** If the required capability remains unavailable, name it and the exact supported install/rerun route. Use existing installation authorization; otherwise installation needs the user's decision. Continue unaffected work without treating silence as approval or unsupported verification as complete.

The rung used is stated per layer at truth sourcing (step 7); the pre-flight fails any heavy layer without a declared source. The bundled `references/ingredients/` cheats are the offline floor — read them for architecture and patterns; they never replace current docs for API signatures.

## Capability map — gate only what the build actually uses

A static minimalist page loads none of this; an Immersive scrolltelling build may load four rows. The trigger column decides.

| Capability | Triggered by | Installed-skill candidates | Install offer | Docs fallback |
|---|---|---|---|---|
| GSAP core / ScrollTrigger / SplitText | any pinned or scrubbed scroll signature, kinetic type — Bold, Immersive, Experimental | the official GSAP skills (`gsap-core`, `gsap-scrolltrigger`, `gsap-react`, …) | `npx skills add https://github.com/greensock/gsap-skills` | gsap.com/docs/v3 |
| Three.js / R3F / drei | 3D scenes — Immersive, Experimental | any Three.js / React Three Fiber skill present | — | threejs.org/docs · r3f.docs.pmnd.rs |
| Lenis | smooth-scroll foundation | — | — | github.com/darkroomengineering/lenis |
| Motion (Framer Motion) | React UI motion, layout animations | any Motion skill present | — | motion.dev/docs |
| View Transitions · scroll-driven CSS · popover/anchor · modern CSS | page morphs, off-thread reveals, any cutting-edge CSS, form UX, or a Core Web Vitals miss the build must debug | `modern-web-guidance` | `npx skills add https://github.com/GoogleChrome/modern-web-guidance` | Current MDN and official browser-platform documentation; do not resolve a documentation package at runtime |
| Web Audio / Howler | sound layer — Immersive, Experimental | `audio-loop` for ambient loop beds | — | `references/ingredients/web-audio.md` · howlerjs.com |
| Raw WebGL / GLSL (OGL) | custom shader signatures | — | — | `references/ingredients/ogl-shaders.md` · github.com/oframe/ogl |

## Browser verification — a gated capability too

Rendering proof is not optional tooling — resolve it like a heavy layer, before the first chunk runs. A build that never rendered is a build nobody looked at.

| Capability | Candidates (first present wins) | Install offer | Fallback |
|---|---|---|---|
| Screenshot · drive · console · supported measurements | Harness-native browser through its skill/tool contract · Chrome DevTools MCP · installed `dev-browser` or `webwright` | Follow the selected adapter's documented prerequisites only when needed | Code-level analysis remains partial; missing rendered proof or required measurements limits the verdict |

Every chunk's Verify and browser proof (pre-flight §8) use this capability check. Distinguish screenshots, interaction, console access, performance traces, LCP and frame-rate measurement: one available browser tool does not prove all of them. Run applicable checks the selected tool supports; report exact unsupported/erroring checks and preserve the review gate's verdict ceiling. Independent-review requirements likewise depend on an actual isolated reviewer capability.

## Product facts are gated too

A brief naming a real product, brand, or place gates its facts like a heavy layer: verify existence, release status, current version, and price via live web sources before designing claims around them — never assert from training memory. One documented failure: a build claimed a shipped product was unreleased; it had launched four days earlier — two hours of rework. Record verified facts beside the truth-sourcing artifact; the copy audit (§6) checks the page against them.

## Stale-signature tripwires

Writing any of these from memory means the rung ladder was skipped — stop and resolve the layer first:

- `import { motion } from "framer-motion"` in new code — the current package is `motion`, imported from `motion/react`.
- Treating a GSAP plugin (SplitText, MorphSVG, ScrollSmoother) as paid Club territory — all plugins ship free in the public `gsap` npm package.
- `tailwindcss` as a PostCSS plugin on Tailwind v4 — v4 uses `@tailwindcss/postcss` or the Vite plugin.
- A `ScrollTrigger` timeline without `gsap.registerPlugin(ScrollTrigger)`.
- Hand-rolled `element.animate` page transitions where same-document View Transitions are Newly available and a guarded `document.startViewTransition` does it. Cross-document `@view-transition { navigation: auto }` is *not* Baseline — it ships as progressive enhancement and degrades to a plain navigation (`stack-facts.md`).

## Install-offer protocol

Offer an install only for a missing capability that affects the requested result, with the adapter's exact command and rerun step. Existing authorization can cover installation; silence cannot. Use available docs or tools for unaffected work and record the unresolved capability in the existing report.
