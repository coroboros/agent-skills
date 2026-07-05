# External Truth — capability gates

Award-grade builds live or die on library APIs that move faster than any training corpus: GSAP's plugins went free and its SplitText syntax changed, Three.js shipped WebGPU, View Transitions went Baseline, Tailwind v4 dropped its PostCSS plugin. Code written from memory for these layers is where confident-looking builds silently break — so each heavy layer passes this gate before its first line of code.

## The ladder — walk in order, stop at the first rung that resolves

1. **Installed skill.** Check the available-skills list for a match (candidates below). Present → load it and follow it; it outranks memory and this file.
2. **Offer the install.** No skill present and the layer is load-bearing for the signature → offer the user the install once, as one line with the exact command. Yes → install, load, follow. No, or no answer → next rung. Never stall the build on the offer.
3. **Fetch current docs.** Resolve and read official documentation before coding: the `find-docs` or `context7-cli` skill when installed, the `ctx7` CLI, or the official URL below via web fetch. Cite what was actually read.

The rung used is stated per layer in the Phase 3 artifact; the pre-flight fails any heavy layer without a declared source. The bundled `references/ingredients/` cheats are the offline floor — read them for architecture and patterns; they never replace current docs for API signatures.

## Capability map — gate only what the build actually uses

A static minimalist page loads none of this; an Immersive scrolltelling build may load four rows. The trigger column decides.

| Capability | Triggered by | Installed-skill candidates | Install offer | Docs fallback |
|---|---|---|---|---|
| GSAP core / ScrollTrigger / SplitText | any pinned or scrubbed scroll signature, kinetic type — Bold, Immersive, Experimental | the official GSAP skills (`gsap-core`, `gsap-scrolltrigger`, `gsap-react`, …) | `npx skills add https://github.com/greensock/gsap-skills` | gsap.com/docs/v3 |
| Three.js / R3F / drei | 3D scenes — Immersive, Experimental | any Three.js / React Three Fiber skill present | — | threejs.org/docs · r3f.docs.pmnd.rs |
| Lenis | smooth-scroll foundation | — | — | github.com/darkroomengineering/lenis |
| Motion (Framer Motion) | React UI motion, layout animations | any Motion skill present | — | motion.dev/docs |
| View Transitions · scroll-driven CSS · popover/anchor · modern CSS | page morphs, off-thread reveals, any cutting-edge CSS the build leans on | `modern-web-guidance` | `npx skills add https://github.com/GoogleChrome/modern-web-guidance` | `npx -y modern-web-guidance@latest search "<query>"` then `retrieve "<id>"` (runs without the skill) · MDN |
| Web Audio / Howler | sound layer — Immersive, Experimental | `audio-loop` for ambient loop beds | — | `references/ingredients/web-audio.md` · howlerjs.com |
| Raw WebGL / GLSL (OGL) | custom shader signatures | — | — | `references/ingredients/ogl-shaders.md` · github.com/oframe/ogl |

## Stale-signature tripwires

Writing any of these from memory means the ladder was skipped — stop and resolve the layer first:

- `import { motion } from "framer-motion"` in new code — the current package is `motion`, imported from `motion/react`.
- Treating a GSAP plugin (SplitText, MorphSVG, ScrollSmoother) as paid Club territory — all plugins ship free in the public `gsap` npm package.
- `tailwindcss` as a PostCSS plugin on Tailwind v4 — v4 uses `@tailwindcss/postcss` or the Vite plugin.
- A `ScrollTrigger` timeline without `gsap.registerPlugin(ScrollTrigger)`.
- Hand-rolled `element.animate` page transitions where the View Transitions API is Baseline and one CSS line does it.

## Install-offer protocol

One line, once, with the command — e.g. *"This signature leans on ScrollTrigger; install the official GSAP skills? `npx skills add https://github.com/greensock/gsap-skills`"*. Decline or silence → rung 3, note the rung in the artifact, keep building.
