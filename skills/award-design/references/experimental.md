# Experimental / Art-Directed

No template, no repeatable pattern — each site is bespoke. The archetype's defining trait is a navigation metaphor or spatial concept that replaces conventional grids, pages, and menus. Mixed media combines photography, illustration, 3D, and generative art; creative coding (custom GLSL, p5.js, Matter.js, hand-coded Three.js) replaces framework templates. The site is the medium, not the messenger.

## Canonical reference — Bruno Simon's Portfolio

**Site.** Bruno's Portfolio
**URL.** `bruno-simon.com`
**Award.** Awwwards Site of the Month, January 2026 (+ Developer Award, Portfolio Honors December 2025)
**Studio.** None — solo creative developer (Bruno Simon).

Navigation is performed by driving a vehicle across a hand-coded Three.js landscape. Conventional grids, pages, and menus are abandoned in favor of spatialized audio, custom physics-based interactions, and unique per-area rooms. The ceiling of craft for the archetype — a solo creative developer outranking studios. Substitutable peers: `resn.co.nz` (60 SOTD, gooey interactive experiences with game design sensibility), `thesephist.com` (research-publication aesthetic with self-built typography), `inkandswitch.com` (academic-paper-as-web with custom diagrams), `aristidebenoist.com` (WebGL mastery in solo portfolio form).

## DNA — non-negotiable

- One bespoke navigation metaphor or spatial concept replaces conventional structure — the metaphor IS the design
- The site is hand-coded from primitives — framework templates do not produce this archetype
- Mixed media (photography, illustration, 3D, generative art) coexists within the same metaphor
- Every unconventional pattern has a discoverable fallback — Awwwards Usability is 30% of the score and tanks pure-discovery navigation
- Internal coherence holds — the site reads as one project's logic, not as a collage of effects

The archetype keeps its identity across spatial-world (Bruno Simon's drive-through portfolio), generative-canvas (Resn's gooey interactions), research-publication (Thesephist, Ink & Switch), and physical-metaphor (Matter.js-driven sites where elements have weight and bounce). The expression depends on the project's conceptual core.

## Common expressions

Four stacks fit the DNA, distinguished by their spatial and interactive concept.

### Spatial world — Bruno Simon profile

Hand-coded Three.js environment with playful primitives — isometric town, low-poly characters, hand-drawn UI annotations ("CLICK TO START" arrow). Vehicle, walker, or camera as the navigation primitive. Per-area rooms with bespoke interactions. Spatialized audio ties the world together. Ideal for solo developer portfolios, agency identity microsites, conference experiential pages, brand worlds.

### Generative canvas — Resn / Active Theory profile

WebGL or canvas-driven generative art as the entire canvas. Particle systems, fluid simulations, shader-based image transitions, GLSL noise functions. Navigation lives at the edges or as gestural triggers. Ideal for studio portfolios, interactive campaigns, art institutions, festival microsites.

### Research publication — Thesephist / Ink & Switch profile

Custom typography system, academic-paper structure, hand-built diagrams as primary content. Long-form deeply-cross-linked text. Interactive citations, sidenotes, and annotation layers. The site is an essay or paper, not a marketing surface. Ideal for research labs, technical thinkers, individual essayists, knowledge bases.

### Physical metaphor — Matter.js / draggable / gooey profile

Elements have weight, bounce, drag. Cards stack like physical objects, menus detach like droplets, navigation is gestural. Matter.js, Cannon.js, or custom physics drive interaction. Ideal for creative campaigns, kids' brands with conceptual ambition, music releases, art-tech crossover projects.

## Typography

Anything goes — but with intent. The choice serves the conceptual core.

- **Spatial world**: hand-drawn or pixel typefaces (Bruno's site uses hand-drawn arrows), oversized sans-serif at world UI level
- **Generative canvas**: custom or modified typefaces designed for the site, often fluid (variable font weight tied to mouse or audio amplitude — observed on the line, exact parameters unverified)
- **Research publication**: bespoke serifs or hybrid typefaces, custom small caps, marginalia treatments — Thesephist's typography is hand-built
- **Physical metaphor**: rounded geometric sans paired with the physics personality (heavy, bouncy, draggable type)

The archetype loses identity when the type is "off the shelf with one weird animation". A custom or distinctive typeface is the entry bar.

## Color

Project-specific — no universal rules. Internally coherent within the project's own logic.

Bruno Simon's site uses dark navy with grid-dot patterns and warm-light landmarks. Resn's portfolio shifts atmosphere per project (every case study has its own world). Thesephist holds warm cream with one accent. The discipline is internal coherence: a concept defined upfront and carried through every surface.

For OKLCH-driven palette generation in this archetype, derive accents from a single brand token via CSS color-mix or `oklch(from var(--brand) ...)` — see `foundations.md`. For the spatial world stack, color often serves world-building (dawn light, dusk light, moonlit) rather than UI hierarchy.

## Layout

Unconventional by definition. Spatial exploration, physics-based interfaces, playground navigation, non-linear storytelling. Conventional grids exist only where they serve the metaphor (Thesephist's reading column is conventional, but everything around it is bespoke).

**Critical**: every unconventional pattern needs a discoverable fallback. Awwwards Usability is 30% of the total score. A site that requires three discovery actions to find primary content scores below Honorable Mention regardless of creativity. Bruno's site succeeds because driving the car is intuitive within seconds; "click to start" anchors the unfamiliar.

## Motion & creative coding

The medium, not the decoration.

- **Three.js / R3F**: hand-coded scenes with physics, lighting, post-processing. WebGPU support in Three.js r171+ for high-density particle work
- **p5.js**: generative art, interactive sketches, code-as-design
- **Matter.js / Cannon.js**: physics engines for tangible interactions
- **3D Gaussian Splatting**: hyperreal environments via Luma AI + PlayCanvas SuperSplat — emerging frontier
- **Custom GLSL**: noise functions, shader-based image-to-image transitions, particle systems
- **AR face tracking** and spatialized audio: sensory layers Resn integrates as core elements
- **WebAudio + Howler.js**: spatial audio that ties the world together

```javascript
const engine = Matter.Engine.create();
const menuItems = items.map(item => {
  const body = Matter.Bodies.rectangle(x, y, w, h, { restitution: 0.6 });
  Matter.World.add(engine.world, body);
  return { body, element: item };
});
Matter.Engine.run(engine);
```

This archetype demands custom tooling. Frameworks templates do not produce it. The consistently winning studios in this category have proprietary engines (Active Theory's Hydra, Resn's internal tools). Solo creative developers like Bruno Simon and Aristide Benoist build from primitives every project.

## What makes it award-worthy

An experimental site scores 8+ when the metaphor is felt before it's understood, when the bespoke nav is intuitive within ten seconds, when the technical craft (60fps, low LCP) holds despite the heavy stack, and when the site is unmistakably one project — not a portfolio of effects. Bruno succeeds because driving-the-car-is-the-portfolio is a single idea executed across every interaction.

The archetype loses identity when "experimental" becomes "template + one custom shader", when the navigation metaphor traps users instead of guiding them, or when the technical implementation breaks on mid-range devices (Awwwards judges check mobile; experimental sites that work only on M-series Macs fail Usability).

FWA rewards this archetype more aggressively than Awwwards — 500+ jury members who value unconventional, experimental work. Strategic submission path: FWA first, use wins as credibility for Awwwards.

## Ideal for

Creative developer portfolios, art institutions, experimental campaigns, design festival sites, music releases with conceptual ambition, agency identity microsites, research publications, individual thinker / essayist platforms, brand worlds, conference experiential pages.

## Cross-references

Read alongside `foundations.md` (WebGL framework selection, OKLCH, custom GLSL), `production-hardening.md` (heavy WebGL stacks need iOS Safari hardening), `anti-patterns.md` (experimental navigation requiring three discovery actions tanks Usability — discoverable fallback is non-negotiable), `audit-rubric.md` (Creativity 9+ is the entry bar; Accessibility cannot drop below 7), `exemplars.md` (Bruno Simon, Resn, Thesephist, Ink & Switch).

## Effect palette — what this line's winners ship

Corpus read live and cross-checked against case studies: Bruno Simon (Awwwards SOTM Jan 2026 + Developer Award + FWA + CSSDA), Igloo Inc (Site of the Year 2024), Lusion v3 (Site of the Year 2023), Aristide Benoist (SOTD 2018/2019/2021, 2021 scored 8.01), Obys Agency (Studio of the Year 2023), Active Theory, Resn — awarded sites anchor every recipe; Thibault Guignand's portfolio (award-unverified, Codrops-documented, May 2026) supplies the exact parameters the awarded sites never publish.

**The grammar** — the interaction layer is rendered *inside* the WebGL/canvas engine, not stamped on the DOM with CSS. One substrate — Bruno's physics-and-matcap world, Igloo's ice-and-chromatic shader — renders every element class, so button ≠ link ≠ image ≠ nav can each behave differently yet read as one authored world. The lazy build inverts this: one CSS trick (a pale fill-sweep, a scrolled nav bar) cloned onto a normal DOM, which reads as sameness *and* as bolted-on. Pick the substrate first, then let each element class express it.

**Buttons / CTA** —
- **Full-token fill, never pale tint** — the surviving HTML button (contact, "view work") animates to a *solid* token with a shadow layer for depth, label inverting to the page background — never a low-alpha wash · pick when one conventional button sits in an otherwise-WebGL page · (Cuberto, Codrops *Magnetic Buttons* — documented technique, not a named winner).
- **Magnetic pull + label-follow** — the button or its inner label translates toward the cursor with elastic easing, snapping back on leave while the custom cursor scales to wrap it; this replaces the fill entirely · the archetype's default CTA on typography/agency builds · (Obys, Studio of the Year 2023; Lusion v3, SOTY 2023; Cuberto `mouse-follower`).
- **WebGL scramble/flowmap** — a button baked into the canvas resolves through an SDF-offset scramble or warps under a velocity flowmap, never a CSS treatment · pick inside a generative-canvas hero · (Igloo Inc, SOTY 2024).

**Links** — **scramble-to-resolve decode** — characters cycle a punctuation-heavy set then settle, run *in parallel* with a clip-path wipe (not after). Verified charset `A!B@C#D$E%F&G*H?J[K]L{M}N=O+P-QRS…`, clip-path `inset(0 0% 0 0)` at `0.6s power2.out`, parent height locked via `getBoundingClientRect().height` before split to stop reflow (Guignand, single-source); Igloo does the same via SDF-texture-offset scramble, which avoids style recalculations (Igloo Inc, SOTY 2024).

**Figures / cards** — **scrub-linked clip-path morph** — a preview unclips full-bleed as you scroll to page bottom: `ScrollTrigger scrub: 1`; `insetV = max(0, 20 − 20·p)`, `insetH = max(0, 40 − 40·p)` → `inset(insetV% insetH% insetV% insetH%)`; background scale `1.3 − 0.3·p`; SVG counter via `stroke-dashoffset = p·circumference`; skip auto-nav if `getVelocity() > 2000` (Guignand, single-source; the gesture is corpus-common). For image hover, a **velocity flowmap** writes cursor speed into an off-screen RG texture and splits RGB along the mouse→pixel vector — R ×1.5, G ×0.5, B ×1.8, rainbow above `uVelo > 0.01` (Guignand, single-source; the chromatic-hover family recurs on Igloo, Active Theory).

**Nav** — winners mostly ship **no persistent HTML nav bar**: the menu lives in-engine (Bruno drives to sections; Igloo renders the entire UI in WebGL; Active Theory nav is in-canvas). Where an HTML nav survives it is a **transparent fixed corner** — logo + one menu word, no background fill, no border, opening a full-screen overlay rather than the bar gaining a surface (Obys; Aristide Benoist, SOTD — observed, exact CSS unverified). The scrolled-solid-bar with a contrasting `border-bottom` is a corporate pattern that never ports here; there is usually no bar to give a surface to.

**Text** — **SplitText stagger scaled to element count** so a line lands tight: lines `duration 0.8 / stagger 0.08`, words `0.6 / 0.06`, letters `0.4 / 0.008`, `yPercent 110→0`, ease `cubic-bezier(0.625, 0.05, 0, 1)` (Codrops/Osmo, documented; the count-scaled reveal is universal in the corpus). Kinetic type — letters scale/split/morph on scroll, type carrying the layout instead of images — is signature for the typography stack (Obys, Studio of the Year 2023 — single named winner). Variable-font weight driven by mouse/audio amplitude is observed, implementation unverified — do not ship exact numbers.

**Cursor** — **magnetic elastic follower** is the default: a dot/ring/blob trails with spring easing, then snaps onto and scales around hoverables, pulling them slightly toward it (Obys; Lusion v3, SOTY 2023; Cuberto `mouse-follower`). The equal-and-opposite move is the **deliberate no-cursor** when the mechanic *is* the pointer — Bruno Simon drives a car, so a lag-dot would fight the physics and the "click to start" + floor-tile path do the wayfinding (Bruno Simon, SOTM 2026). A meaningless bespoke cursor is worse than none.

**Loader / intro** — the intro renders *in the engine* and *is* the concept booting: a real-time animation in the site's own shaders (Igloo Inc, SOTY 2024), or objects rising from the ground with a paper-unwrap sound (Bruno Simon). A required **start button doubles as the audio-unlock gate** since browsers block autoplay until interaction (Bruno Simon, single-source — a hard constraint, not a taste choice). No heavy engine → no loader; the text-first sub-stack ships instant first paint.

**Anti-signals** — absent from every winner examined: the **pale/washed-out tint fill** on button hover (a 10–20% brand-alpha sweep — the single clearest tell); the **scrolled solid nav bar + contrasting `border-bottom`**; one identical hover cloned onto every element class; CSS underline-draw as the link move; generic `fade-up 20px` as the only reveal; a spinner or bare `%` counter preloader with no tie to the concept; a `mix-blend-mode` lag-dot cursor that adds no mechanic; a single `background-clip: text` gradient sold as "kinetic type."
