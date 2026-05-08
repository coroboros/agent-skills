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
- **Generative canvas**: custom or modified typefaces designed for the site, often fluid (variable font weight tied to mouse or audio amplitude)
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
