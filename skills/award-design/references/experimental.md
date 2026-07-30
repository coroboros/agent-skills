# Experimental / Art-Directed

No template, no repeatable pattern — each site is bespoke. The archetype's defining trait is a navigation metaphor or spatial concept that replaces conventional grids, pages, and menus. Mixed media combines photography, illustration, 3D, and generative art; creative coding (custom GLSL, p5.js, Matter.js, hand-coded Three.js) replaces framework templates. The site is the medium, not the messenger.

Tier 1 (DNA, anti-signals, macrostructures, reflexes) is `references/archetype/experimental.md`, pushed into context by `scripts/direction_roll.py`. This file is tier 2: it loads at the design_plan commit, BY HEADING, never whole.

## Contents

- [Canonical reference — Bruno's Portfolio](#canonical-reference--brunos-portfolio)
- [DNA — non-negotiable](#dna--non-negotiable)
- [Common expressions](#common-expressions)
- [Typography](#typography) · [Color](#color) · [Layout](#layout) · [Motion & creative coding](#motion--creative-coding)
- [What makes it award-worthy](#what-makes-it-award-worthy) · [Ideal for](#ideal-for) · [Cross-references](#cross-references)
- [Effect palette — what this line's winners ship](#effect-palette--what-this-lines-winners-ship) — per-element-class recipes, the grammar, tap/focus/dormancy
- [Mid-page life](#mid-page-life) · [Scroll texture](#scroll-texture) · [Idle band](#idle-band) · [Channel calibration](#channel-calibration)
- [Page recipe — how this line's winners build the page](#page-recipe--how-this-lines-winners-build-the-page) — anatomy, hero, section chain, footer, arrival, copy, imagery, mobile, variation
- [Spectacle menu](#spectacle-menu) — the hero beat, the continuation beats, the peak law
- [Component index](#component-index) — the library ids this archetype reaches for

## Canonical reference — Bruno's Portfolio

**Site.** Bruno's Portfolio (folio-2025)
**URL.** `bruno-simon.com`
**Award.** Awwwards SOTD 2026-01-21 — 8.11 overall, Creativity 8.62; Developer Award 7.65 (Animations 8.60, Responsive 8.20); Site of the Month January 2026
**Studio.** None — solo creative developer (Bruno Simon).

Navigation is performed by driving a vehicle across a hand-coded Three.js landscape — the town modelled in Blender, physics bodies auto-tagged by naming convention, rendering on the WebGPU path via Three.js TSL. Conventional grids, pages, and menus are abandoned in favor of spatialized audio, custom physics-based interactions, and unique per-area rooms; the standard DOM interactions (click, scroll, keyboard, touch, gamepad) are recreated as 3D raycasts so the world stays navigable off a mouse. The ceiling of craft for the archetype — a solo creative developer outranking studios. Substitutable peers: `resn.co.nz` (Site of the Year 2022 for KPR, the first Web3 SOTY, awarded 2023-03-03; a 60-SOTD tally, an SOTM in December and two Agency-of-the-Year wins are carried from the earlier round and were not re-verified — gooey interactive experiences with a game-design sensibility), `thesephist.com` (research-publication aesthetic with self-built typography), `inkandswitch.com` (academic-paper-as-web with custom diagrams), `aristidebenoist.com` (WebGL mastery in solo portfolio form).

## DNA — non-negotiable

- One bespoke navigation metaphor or spatial concept replaces conventional structure — the metaphor IS the design
- The site is hand-coded from primitives — framework templates do not produce this archetype
- Mixed media (photography, illustration, 3D, generative art) coexists within the same metaphor
- Every unconventional pattern has a discoverable fallback — Awwwards Usability is 30% of the score and tanks pure-discovery navigation
- Internal coherence holds — the site reads as one project's logic, not as a collage of effects

The archetype keeps its identity across spatial-world (Bruno Simon's drive-through portfolio), generative-canvas (Igloo's ice shader, Resn's gooey interactions), type-index-over-WebGL (Aristide Benoist, Obys), physical-metaphor (MoMoney's Matter.js field, where elements have weight and bounce), and research-publication (Thesephist, Ink & Switch — documented, award-unverified). The expression depends on the project's conceptual core.

## Common expressions

Five stacks fit the DNA, distinguished by their spatial and interactive concept.

### Spatial world — Bruno Simon profile

Hand-coded Three.js environment with playful primitives — isometric town, low-poly characters, hand-drawn UI annotations ("CLICK TO START" arrow). Vehicle, walker, or camera as the navigation primitive. Per-area rooms with bespoke interactions. Spatialized audio ties the world together. Ideal for solo developer portfolios, agency identity microsites, conference experiential pages, brand worlds.

### Generative canvas — Igloo / Resn / Active Theory profile

WebGL or canvas-driven generative art as the entire canvas — Igloo renders the whole UI in-engine with procedurally grown ice, one block per project. Particle systems, fluid simulations, shader-based image transitions, GLSL noise functions. Navigation lives at the edges or as gestural triggers. Ideal for studio portfolios, interactive campaigns, art institutions, festival microsites.

### Type index over WebGL — Aristide Benoist / Obys profile

A dense index of oversized title rows over a live WebGL image field is the whole page: no marketing hero, no prose column, proof by density. Two colours and no colour accent are normal here — the live state is tonal. A corner counter boots straight into the index, a click plays an in-engine route morph, an About overlay doubles as the footer. Ideal for developer and designer folios, agency identity pages, work archives with named clients.

### Research publication — Thesephist / Ink & Switch profile

Custom typography system, academic-paper structure, hand-built diagrams as primary content. Long-form deeply-cross-linked text. Interactive citations, sidenotes, and annotation layers. The site is an essay or paper, not a marketing surface. Documented from live CSS reads; no award crown surfaced for either site, so this stack is corpus-documented rather than winner-verified. Ideal for research labs, technical thinkers, individual essayists, knowledge bases.

### Physical metaphor — MoMoney / Matter.js profile

Elements have weight, bounce, drag. Cards stack like physical objects, menus detach like droplets, navigation is gestural. Matter.js, Cannon.js, or custom physics drive interaction — MoMoney carries a two-colour build (`#00592B` / `#1CE585`) entirely on a rigid-body field of draggable, throwable coins and tokens that collide, bounce and settle. Ideal for creative campaigns, kids' brands with conceptual ambition, music releases, art-tech crossover projects.

## Typography

Anything goes — but with intent. The choice serves the conceptual core.

- **Spatial world**: hand-drawn or pixel typefaces (Bruno's site uses hand-drawn arrows), oversized sans-serif at world UI level
- **Generative canvas**: custom or modified typefaces designed for the site, often fluid (variable font weight tied to mouse or audio amplitude — observed on the line, exact parameters unverified)
- **Type index**: one display face carrying the entire page at index scale, set in the site's own voice down to the counter and status labels (Aristide runs the whole page in `"TNY"`)
- **Research publication**: bespoke serifs or hybrid typefaces, custom small caps, marginalia treatments — Thesephist's typography is hand-built
- **Physical metaphor**: rounded geometric sans paired with the physics personality (heavy, bouncy, draggable type)

The archetype loses identity when the type is "off the shelf with one weird animation". A custom or distinctive typeface is the entry bar.

## Color

Project-specific — no universal rules. Internally coherent within the project's own logic.

Bruno Simon's site uses dark navy with grid-dot patterns and warm-light landmarks. Resn's portfolio shifts atmosphere per project (every case study has its own world). Thesephist holds warm cream with one accent. MoMoney runs two saturated greens and nothing else. The discipline is internal coherence: a concept defined upfront and carried through every surface.

Where the palette has an accent, that accent is the one signal meaning *active/live* on every element class (Igloo's chromatic accent). Where it has none, the live state is tonal: Aristide's index is black and white, and its live signal is the per-entry material line plus the siblings dimming — not a colour. Both answers are legal; a build with neither has no live state at all.

For OKLCH-driven palette generation in this archetype, derive accents from a single brand token via CSS color-mix or `oklch(from var(--brand) ...)` — see `foundations.md`. For the spatial world stack, color often serves world-building (dawn light, dusk light, moonlit) rather than UI hierarchy.

## Layout

Unconventional by definition. Spatial exploration, physics-based interfaces, playground navigation, non-linear storytelling. Conventional grids exist only where they serve the metaphor (Thesephist's reading column is conventional, but everything around it is bespoke).

**Critical**: every unconventional pattern needs a discoverable fallback. Awwwards Usability is 30% of the total score. A site that requires three discovery actions to find primary content scores below Honorable Mention regardless of creativity. Bruno's site succeeds because driving the car is intuitive within seconds; "click to start" anchors the unfamiliar.

## Motion & creative coding

The medium, not the decoration.

- **Three.js / R3F**: hand-coded scenes with physics, lighting, post-processing. WebGPU support in Three.js r171+ for high-density particle work — Bruno's world renders on the WebGPU path via TSL
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

This archetype demands custom tooling. Framework templates do not produce it. The consistently winning studios in this category have proprietary engines (Active Theory's Hydra, Resn's internal tools, Lusion's own scroll driver — published as the open-source WebGL Scroll Sync repository). Solo creative developers like Bruno Simon and Aristide Benoist build from primitives every project.

## What makes it award-worthy

An experimental site scores 8+ when the metaphor is felt before it's understood, when the bespoke nav is intuitive within ten seconds, when the technical craft (60fps, low LCP) holds despite the heavy stack, and when the site is unmistakably one project — not a portfolio of effects. Bruno succeeds because driving-the-car-is-the-portfolio is a single idea executed across every interaction.

The archetype loses identity when "experimental" becomes "template + one custom shader", when the navigation metaphor traps users instead of guiding them, or when the technical implementation breaks on mid-range devices (Awwwards judges check mobile; experimental sites that work only on M-series Macs fail Usability).

FWA rewards this archetype more aggressively than Awwwards — 500+ jury members who value unconventional, experimental work. Strategic submission path: FWA first, use wins as credibility for Awwwards.

## Ideal for

Creative developer portfolios, art institutions, experimental campaigns, design festival sites, music releases with conceptual ambition, agency identity microsites, research publications, individual thinker / essayist platforms, brand worlds, conference experiential pages.

## Cross-references

Read alongside `foundations.md` (WebGL framework selection, OKLCH, custom GLSL), `production-hardening.md` (heavy WebGL stacks need iOS Safari hardening), `anti-patterns.md` (experimental navigation requiring three discovery actions tanks Usability — discoverable fallback is non-negotiable), `audit-rubric.md` (Creativity 9+ is the entry bar; Accessibility cannot drop below 7), `exemplars.md` (Bruno Simon, Resn, Thesephist, Ink & Switch).

Provenance for every claim below — the researcher rounds and the fresh-context refutations that corrected them — lives in the public deep-research corpus of `github.com/coroboros/research`, under `articles/award-winning-websites-2025-2030/deep-research/`: `archetypes/experimental.md`, refutations folded under its `## Refuted` heading, the raw reports preserved verbatim at commit `fd5d1b6`.

## Effect palette — what this line's winners ship

Corpus — Bruno's Portfolio (Awwwards SOTD 2026-01-21, 8.11 overall, Creativity 8.62; Developer Award 7.65 with Animations 8.60 and Responsive 8.20; Site of the Month January 2026; plus FWA, CSSDA and Portfolio Honors December 2025 carried from the earlier round and not re-verified this run), Igloo Inc (Site of the Year 2024 + Developer Site of the Year 2024; built by Abeto + Bureaux), Lusion v3 (SOTD 2023-10-02, 8.25; **Developer** Site of the Year 2023 with Developer Award 8.41 and Animations 10.00; FWA case; CSSDA Website of the Year 2023 nominee, judge score 9.27), Aristide Benoist Portfolio 2021 (SOTD 2021-06-24, 8.01, Animations/Transitions 9.20; Site of the Month June 2021 — earlier SOTDs in 2018 and 2019 belong to prior portfolios and were not re-verified this run), Shader Development Studio (SOTD 2026-04-20, 7.73; Developer Award 8.12 with Animations/Transitions 9.40 and Responsive 8.40), MoMoney by Jordan Gilroy (SOTD + Developer Award 2026-03-13, 7.39; Codrops designer spotlight), Resn (Site of the Year 2022 for KPR — the first Web3 SOTY, awarded 2023-03-03), Valentin Gassend (Honorable Mention 2026-05-18, community 15/20 — an immersive scroll-driven WebGL/GSAP portfolio, kept as a fresh in-engine signal), Obys Agency (Studio of the Year 2023). Carried as sources, not as shipped reads: Igloo's own Awwwards and webgpu.com case studies (its SDF scramble and footer particle sim are case-study evidence, never read from source), Thibault Guignand's portfolio (award-unverified, Codrops-documented May 2026 — it supplies the exact parameters the awarded sites never publish), Ink & Switch and Thesephist (live CSS read; no award crown surfaced for either), Cuberto and Osmo/Codrops for the documented button and SplitText techniques.

**The grammar** — the interaction layer is rendered *inside* the WebGL/canvas/physics engine, not stamped on the DOM with CSS. One substrate — Bruno's physics-and-matcap world, Igloo's ice-and-SDF shader canvas, Aristide's type-over-WebGL field, MoMoney's Matter.js field — renders every element class, so button ≠ link ≠ image ≠ nav can each behave differently yet read as one authored world. The lazy build inverts this: one CSS trick (a pale fill-sweep, a scrolled nav bar) cloned onto a normal DOM, which reads as sameness *and* as bolted-on. Pick the substrate first, then let each element class express it. Cohesion over that surface is manufactured by three constants: ONE signal meaning *active/live* on every class (a colour accent where the palette has one, a tonal state where it does not); ONE easing/motion family used everywhere (Lusion's char-split `cubic-bezier(.625,.05,0,1)`; the Osmo/Codrops count-scaled SplitText); and, on the spatial-world stack, ONE positional audio bed as the literal through-line. Never a different ease per element.

**Buttons / CTA** —
- **Full-token fill, never pale tint** — the surviving HTML button (contact, "view work") animates to a *solid* token with a shadow layer for depth, label inverting to the page background — never a low-alpha wash · pick when one conventional button sits in an otherwise-WebGL page · (Cuberto, Codrops *Magnetic Buttons* — documented technique, not a named winner).
- **Magnetic pull + label-follow** — the button or its inner label translates toward the cursor with elastic easing, snapping back on leave while the custom cursor scales to wrap it; this replaces the fill entirely · the archetype's default CTA on typography/agency builds · (Obys, Studio of the Year 2023; Lusion v3, Developer SOTY 2023; Cuberto `mouse-follower`).
- **WebGL scramble/flowmap** — a button baked into the canvas resolves through an SDF-offset scramble or warps under a velocity flowmap, never a CSS treatment · pick inside a generative-canvas hero · (Igloo Inc, SOTY 2024, case-study evidence). Library id: `sdf-scramble-substrate`.
- **Physics-body press** — on a rigid-body build the control is a body: it depresses under the pointer and nudges away from it, and the press reads as weight rather than as a state change · pick when the whole page is a physics field · (MoMoney, SOTD 2026 — mechanic verified, shipped parameters not read).

**Links** — **scramble-to-resolve decode** — characters cycle a punctuation-heavy set then settle, run *in parallel* with a clip-path wipe (not after). The documented parameters are charset `A!B@C#D$E%F&G*H?J[K]L{M}N=O+P-QRS…`, clip-path `inset(0 0% 0 0)` at `0.6s power2.out`, parent height locked via `getBoundingClientRect().height` before split to stop reflow (Guignand, single-source, award-unverified — treat every Guignand number as a starting default, never a measured spec, and never ship them as archetype law). Igloo does the same by swapping SDF-texture offsets, which avoids style recalculation entirely (Igloo Inc, SOTY 2024, case-study evidence). Kinetic CSS underline-draw is absent on this line — it belongs to editorial.

**Figures / cards** — **scrub-linked clip-path morph** — a preview unclips full-bleed as you scroll to page bottom: `ScrollTrigger scrub: 1`; `insetV = max(0, 20 − 20·p)`, `insetH = max(0, 40 − 40·p)` → `inset(insetV% insetH% insetV% insetH%)`; background scale `1.3 − 0.3·p`; SVG counter via `stroke-dashoffset = p·circumference`; skip auto-nav if `getVelocity() > 2000` (Guignand, single-source, starting defaults; the gesture itself is corpus-common). For image hover, a **velocity flowmap** writes cursor speed into an off-screen RG texture and splits RGB along the mouse→pixel vector — R ×1.5, G ×0.5, B ×1.8, rainbow above `uVelo > 0.01` (Guignand, single-source; the chromatic-hover family recurs on Igloo and Active Theory). Library id: `velocity-flowmap-hover`. On a physics build the figure is instead a draggable, throwable body (`physics-tumble-field`).

**Nav** — winners mostly ship **no persistent HTML nav bar**: the menu lives in-engine (Bruno drives to sections; Igloo renders the entire UI in WebGL; Active Theory nav is in-canvas; Aristide's giant-type index IS the nav). Where an HTML nav survives it is a **transparent fixed corner** — logo + one menu word, no background fill, no border, opening a full-screen overlay rather than the bar gaining a surface (Obys; Aristide Benoist, SOTD — observed, exact CSS unverified). The scrolled-solid-bar with a contrasting `border-bottom` is a corporate pattern that never ports here; there is usually no bar to give a surface to.

**Text** — **SplitText stagger scaled to element count** so a line lands tight: lines `duration 0.8 / stagger 0.08`, words `0.6 / 0.06`, letters `0.4 / 0.008`, `yPercent 110→0`, ease `cubic-bezier(0.625, 0.05, 0, 1)` (Codrops/Osmo, documented; the count-scaled reveal is universal in the corpus). Kinetic type — letters scale/split/morph on scroll, type carrying the layout instead of images — is signature for the typography stack (Obys, Studio of the Year 2023 — single named winner). In a fully-WebGL build the same text is rendered from an SDF glyph atlas so the decode costs no relayout (`sdf-scramble-substrate`). Variable-font weight driven by mouse/audio amplitude is observed, implementation unverified — do not ship exact numbers.

**Cursor** — three modes, chosen by what the pointer already does.
- **Magnetic elastic follower** — a dot/ring/blob trails with spring easing, then snaps onto and scales around hoverables, pulling them slightly toward it · the default on typography and agency builds · (Obys; Lusion v3, Developer SOTY 2023; Cuberto `mouse-follower`). Library id: `magnetic-cursor`.
- **State-morphing cursor** — when the world is chrome-less WebGL, the cursor grows or swaps to a per-target label or arrow ("drag", "view", "hold") so the cursor state carries the hover affordance the absent DOM chrome would have carried · documented on chrome-less agency and experimental winners, Lusion among them.
- **Deliberate no-cursor** — when the mechanic *is* the pointer. Bruno Simon drives a car, so a lag-dot would fight the physics and the "click to start" arrow plus the floor-tile path do the wayfinding (Bruno Simon, SOTD + SOTM 2026). A meaningless bespoke cursor is worse than none.

**Loader / intro** — the intro renders *in the engine* and *is* the concept booting: a real-time animation in the site's own shaders resolving straight into the first scene with no loader DOM and the HUD live from frame one (Igloo Inc, SOTY 2024, case-study evidence), or objects rising from the ground with a paper-unwrap sound (Bruno Simon). A required **start button doubles as the audio-unlock gate** since browsers block autoplay until interaction (Bruno Simon, single-source — a hard constraint, not a taste choice). The type-index variant is a fixed corner counter ticking 0→100 while the page stands visible and armed behind it. No heavy engine → no loader; the text-first sub-stack ships instant first paint. Library ids: `world-boot` and `gated-splash` (the Bruno spelling), `in-engine-intro` (the Igloo spelling), `corner-counter-boot`.

**Element states — tap, focus, dormancy.** The pointer layer is one costume of the state; the tap and focus answers are not optional and not a degraded copy.
- **CTA** — the flood, the press or the depress IS the tap answer, with a 90–160ms flash floor on `:active`; on a physics build the body reacts to the touch directly. `:focus-visible` shows the same solid flooded/inverted state plus a visible ring — the hover-revealed state must be keyboard-reachable.
- **Link** — scramble replay or accent flash on `:active` (90–160ms). `:focus-visible` runs the decode-to-resolve plus the accent recolor plus a visible ring.
- **Figure** — tap to enlarge, or grab-drag-fling the body on touch (native to the physics stack); the resting caption or still is the complete no-pointer look. `:focus-within` shows the finished revealed state. Amplitude is felt — a full-bleed unclip, a visible chromatic split — never a 1.02–1.03 twitch.
- **Index row** — the row navigates or plays the route-morph on tap, and the metadata that hover surfaces is present in the resting DOM so touch reaches it. `:focus-within` lights the same spotlight (material line plus siblings dimming).
- **Heading** — no touch answer; the entrance reveal is the mobile expression. No hover analog, and the accessible name stays clean via `aria-label` when chars or lines are split for the entrance.
- **Nav** — the in-engine nav or the overlay toggle answers the tap, link taps flash the accent. Focus rings on links and the overlay control; the in-engine menu stays keyboard-reachable (Bruno recreates DOM nav events in 3D — `in-3d-dom-input-bridge`).
- **Cursor** — every pointer-only class (magnetic follower, state-morph cursor, velocity flowmap, pointer-parallax) goes fully dormant on touch. That dormancy is the winner answer, not a gap.

**Anti-signals** — absent from every winner examined: the **pale/washed-out tint fill** on button hover (a 10–20% brand-alpha sweep — the single clearest tell); the **scrolled solid nav bar + contrasting `border-bottom`**; one identical hover cloned onto every element class; CSS underline-draw as the link move; generic `fade-up 20px` as the only reveal; a spinner or bare `%` counter preloader with no tie to the concept; a `mix-blend-mode` lag-dot cursor that adds no mechanic; a single `background-clip: text` gradient sold as "kinetic type."

## Mid-page life

Three registers, three answers, none of them decorating a prose column. Spectacle deletes the middle: Lusion's body does not natively scroll — the wheel feeds the WebGL journey through the studio's own `scrollManager` lerp, a bespoke driver corroborated by Lusion's public WebGL Scroll Sync repository, not an off-the-shelf smooth-scroll library — and the engine keeps rendering with zero input while hundreds of single-char split spans land the sparse text per-char (Lusion, 8.25, winner-verified mechanic; the earlier one-viewport `scrollHeight` and idle tick-rate figures are reference-carried, were not re-measured, and are no part of *this* claim — the shape's own `scrollHeight` hedge lives in the page-anatomy catalog, not in a Lusion measurement). Index converts it into a hover-live giant-type index over WebGL: masked `translate3d(0,101%,0)` row reveals, a `:hover::after` material line per entry, `:has()` dimming the unhovered siblings, click-morph routes, no scroll spine at all (Aristide Benoist, 8.01, winner-verified mechanism; the per-element values carry from the earlier `d.css`/`d.js` read and were not re-measured this run). Quiet keeps real prose and makes it live typographically with near-zero motion — hanging marginalia at `margin-left:-1.8em`, sidenotes aligned to their reference line via `calc(-24px * var(--move-up) - 13px)`, hand-stamps randomized per instance with `rotate: calc(var(--randA)*5deg - 4deg)` (Ink & Switch, live CSS read; award-unverified). Hover-on-text is a word-level clone roll-swap on nav labels — `.header-menu-link-text` plus `-text-clone` pre-stacked in the markup, rolling on `.4s transform cubic-bezier(.4,0,.1,1)` (Lusion, winner-verified) — never on running prose. And never an off-the-shelf smoothing library on this line: the smoothing is bespoke or in-engine — Lusion's own driver, Aristide click-routing around scroll entirely (his shipped bundle carried no scroll tokens on the earlier read, not re-measured this run), the quiet register staying on native `scroll-behavior:smooth`.

## Scroll texture

A sliced-filmstrip scrub with a ruler-tick scrubber marking progress (Aristide Benoist, winner-verified on the earlier read — his index itself click-routes with no scroll spine, so this carrier belongs to whichever view actually scrolls, never to the index), or a scroll-scrubbed real-time simulation — the scene assembles itself as the page advances (Igloo, case-study evidence). A third channel renders the momentum itself: whole-scene distortion driven by scroll SPEED, one smoothed signed velocity uniform warping the plate and decaying back to rest when scrolling stops — documented technique (Codrops, *Distortion and Grain Effects on Scroll with Shaders in Three.js*, 2024-07-18) with soft attribution only (Lusion scored Animations 10.00 and ships a public scroll driver, but no shipped read pins the effect to it); library id `scroll-velocity-scene-distortion`. The design_plan names one, rendered in-engine like everything else on this line. On touch the same carrier is `journey-touch-momentum` — touchmove feeds the camera-lerp the wheel drives, never a fallback to native scroll.

## Idle band

Mandatory and uncapped — the strongest single signal of the archetype, and the one channel this line never trades away. The substrate never sleeps: a live weather + day/night + seasons system runs for every visitor simultaneously (wind animates a dense procedural grass field and foliage, rain splashes, snow accumulates, lightning storms fire), up to 30 Whispers — other visitors' flames carrying a short message and a country flag — drift through the shared space, a global cookie counter ticks, and spatialized audio pans with the camera (Bruno Simon, SOTD + SOTM 2026, winner-verified). Igloo's canvas renders continuously and the camera drifts between ice zones with no static frame anywhere (case-study evidence). Lusion's engine keeps rendering at zero input (winner-verified mechanic; the exact tick rate is reference-carried, not re-measured). MoMoney's rigid bodies settle between inputs instead of freezing (winner-verified mechanic). Commit the idle channels the engine already affords — engine ticks at idle, physics settle, weather or day/night values, a presence feed, a node-graph's live values, a clock ticking in the chrome. The mechanical gate is checkable with no taste read: every section carrying the substrate owns at least ONE continuously-updating channel — a rAF or engine loop that mutates rendered state with zero user input. A canvas that updates only on scroll-in or on pointer input, then parks, is a frozen canvas and is illegal; fix it before proceeding. Library ids: `living-presence-layer` (the inhabited feed), `spatial-audio-world` (the positional bed), and — kept distinct — `idle-attract-auto-demo`, the verb-teaching attract pass that auto-performs the primary verb after real idle. That last one is a design-logic entry derived from the 30% Usability weighting rather than a site-verified mechanic; never present it as winner canon.

## Channel calibration

Channel calibration — this line's winners run 4–5 distinct interaction channels (per-class states, display-type effects, cursor, idle, scroll texture, replayable spectacle); the pre-emit critique's Aliveness axis reads against that band, never against bare coverage.

## Page recipe — how this line's winners build the page

Corpus — Bruno Simon (SOTD + Developer Award 2026-01-21 + SOTM January 2026, live copy; engine seed), Igloo Inc (SOTY 2024 + Developer SOTY 2024 — media-only, Awwwards and webgpu.com case studies), Lusion v3 (SOTD 2023-10-02 at 8.25, Developer SOTY 2023 — live ©2026 build), Aristide Benoist (SOTD 2021-06-24 at 8.01, Transitions 9.20 — live DOM + `d.css`, not re-read this run), Obys (Studio of the Year 2023, live), MoMoney (SOTD + Developer Award 2026-03-13 at 7.39, Matter.js confirmed, shipped parameters unread), Shader Development Studio (SOTD 2026-04-20 at 7.73, Responsive 8.40 — award page verified; its named set-pieces are reference-carried), Guignand (award-unverified Codrops — media-only, technique/single-source).

**Anatomy** — never commit any of these without a WebGL path. *World-as-page* (`engine-world`; Bruno, winner-verified copy + seed engine): no scroll — world boot (attention) → spawn + "click to start" (understanding in ten seconds) → landmarks + secret rooms by driving (proof) → in-world sign-off (close); the world is the climax. Its composed variant, when the primary verb is one physical action performed in-engine: world boot → a playable stage pairing `raycast-object-state` per object, `in-3d-dom-input-bridge` for the world's channels, one charged gesture (`press-hold-reveal`), `idle-attract-auto-demo` teaching after real idle, `spatial-audio-world` and `in-scene-ambient-life` keeping it inhabited → a findings index of what the visitor turned up (`index-list` + `index-row-hover`) → `about-overlay-footer` as the close; world-boot is the arrival, so there is no loader. Needs a WebGL path and a covering scene — reach for a covering reference scene first, and where none covers, author the scene at library quality through the delegated WebGL build. *In-engine scroll journey* (`engine-world`; Igloo case study; Lusion copy winner-verified): all pixels render in-engine, shader seams — intro (attention) → ice-encased zones, one per project (proof) → links particle sim (climax) → footer (rest); `scrollHeight` may pin at ~1vh on this shape — the page-anatomy catalog's hedge for the engine lines, never a Lusion measurement — since the wheel drives a camera and not a document; Lusion runs a softer seven-zone variant with a late CTA climax (©2026 copy). *Counter-boot index* (`type-index`; Aristide winner-verified; Obys grid variant): corner counter (attention) → giant-type index over WebGL, no marketing hero, no prose (proof) → click route morph (climax) → About overlay anywhere (close). *Physics field* (the `engine-world` shape on a 2D engine; MoMoney, winner-verified): the page is a tactile surface of rigid bodies you grab, throw and tumble, navigation is gestural and the simulation is both medium and reward; the library form is `physics-tumble-field`. *Single-canvas monolith* (`engine-world`; Rogier de Boevé, technique / single-source): one WebGL scene is the page, screens rotated on a circular path.

Route on the brief's declared inputs, never on a taste read: a bespoke navigation metaphor or operable space the visitor drives, walks or pilots → world-as-page. A fully in-engine continuous scene scrubbed or drifted by the wheel → in-engine journey. A giant-type index that IS the argument → counter-boot index. Elements with weight you throw and drag → physics field. A long-form essay or paper as the content → the quiet research-publication register. Where the brief names one physical action the visitor performs in-engine, the world-as-page runs its composed variant. Pick exactly one; the metaphor is the design, and two metaphors in one page is two pages.

**Hero architectures** — *World-boot hero* (Bruno): no DOM `<h1>`; the Loader-row start-gate opens the world; landmarks are the nav; beats shipped/seed. *In-engine statement hero* (Igloo technique; Lusion copy winner-verified): shader intro resolves into the scene, or statement H1 over the live field; entrance = the Text row's SplitText reveal (technique). *Giant-type index hero* (Aristide, `d.css` read on the earlier round, not re-measured this run): `#load` (TNY 50px, top 35px/left 38px) counts 0→100, digits exit `translate3d(-110%,0,0)` → `#a-nif-w` title at `calc(17.5vh + 100px)` over WebGL → `.e` indicator (dot `.e-s` 14×14) reveals `translate3d(0,-110%,0)`.

**Section chain** — the winner-verified order with its intensity map and the state each section owes. It is one costume, not the skeleton; pick forms by role and delegate the heavy scene.

| role | form | pairs | intensity | state it owes |
|---|---|---|---|---|
| world-boot / hero | `world-boot` · `gated-splash` · `in-engine-intro` | gate `gated-splash` (start gate doubles as sound-unlock); ground `shader-surface` \| `webgl-scene`(delegated); counter `corner-counter-boot` (type-index only); enter control `fill-invert-cta` | 8 | the substrate is present, simulating and pointer/physics-armed from frame one, before any input; a discoverable anchor (the "click to start" arrow plus a floor path, or a corner counter) delivers understanding in ten seconds; the intro renders IN the engine and IS the concept booting. A frozen or inert boot is the defining defect |
| spine (the live substrate) | `webgl-scene`(delegated) free-roam · in-engine journey with shader-seam zones · `physics-tumble-field` | `shader-surface`; `spatial-audio-world`; `living-presence-layer`; ambient-idle (the DOM cousin) | 8 | for a world, the WHOLE page: the medium simulates continuously — free-roam by drive/walk/pilot, or a wheel-driven camera through shader-seamed zones, or a live physics field. The idle band runs here: weather/day-night, engine ticks at idle, physics settle, presence drift, spatialized audio. Never a static frame |
| proof (index / zones) | `type-index-grid` (over WebGL) · `webgl-scene`(delegated), one zone per project · `index-list` | rows `index-row-hover`; labels `scramble-decode` \| `sdf-scramble-substrate`; imagery behind type `shader-surface` | 8 | argument by density: rows stay hover-live (masked reveal + per-entry material line + siblings dimming), or one procedurally-encased zone per project drifts past the camera. No marketing hero, no prose column |
| spectacle peak (replayable) | `webgl-scene`(delegated) route-morph · `webgl-scene`(delegated) particle-sim | `sdf-scramble-substrate`; `velocity-flowmap-hover` | 9 | the one or two capped peaks, and they are STATEFUL PLAY: an on-click route-morph carrying an index title and its imagery into the case study, a footer particle sim coalescing into a different model per link, a secret room, a leaderboard run. A scripted hero animation that plays once is the anti-pattern |
| close / sign-off | in-world sign-off · `about-overlay-footer` · contact-first `close-panel` | `accent-link`; awards ledger `counter-odometer` | 5 | never an oversized-wordmark close and never a footer sitemap: the world signs off in place (Bruno), or a HUD copyright rides the engine (Igloo), or an About overlay doubles as the footer typeset in the site's own voice (Aristide: clients wall + awards ledger), or contact-first with a real address (Lusion) |

**Footer** — identity + contact in the site's own voice; never the oversized-wordmark close, never a sitemap. Functional-plus (Lusion, winner-verified ©2026): "©2026 LUSION Creative Studio", `hello@` + `business@`, the Bristol address, "Built by Lusion with ❤️". About-overlay-as-footer (Aristide, winner-verified): clients list, awards tally (Site of the Day ×30, Developer Award ×27), "ARISTIDE BENOIST 2026®" — sign-off, counter, status all in `"TNY"`; typeset, not templated; library form `about-overlay-footer`. In-world sign-off (Bruno, winner-verified): no DOM footer at all — the world closes in place. Igloo's footer particle simulation coalesces into a different 3D model per link on hover and is the build's late interactive climax (case-study evidence — the Awwwards and webgpu.com studies, not a shipped-source read).

**Arrival** — the Loader row above already holds this line's families (in-engine boot, start-gate, corner counter, none for text-first; map: `ingredients/preloaders.md`); the boot shares the site's type and shaders with the first fold. Bruno: `gated-splash` — the start gate IS the sound gate, no numeric counter, paper-unwrap sound (shipped/seed). Igloo: no loader at all, no boundary — the intro flows into the scene and the HUD is live from frame one (case-study evidence). Aristide: the corner counter 0→100 boots straight into the index (winner-verified). Routes (`ingredients/page-transitions.md`): Aristide click-navs with no scroll-jacking, and his `d.css` (~9.5KB min) shipped no clip-path and no transition rules — the 9.20-scored morphs live in `d.js` (~68KB); that bundle read is carried from the earlier round and was not re-measured this run. Igloo seams: chromatic aberration + displacement + frost (case study). Guignand's route values: the Links and Figures rows above (technique/single-source, starting defaults).

**Copy voice** — Quoted to calibrate, never to ship — imitate the specificity (the named place, the count, the refusal), never the wording. Two poles — warm first person (the makers) vs near-personless caps labels (the index stack) — plus refusal-as-position for studios; one humane sentence or none; imperatives hand over the mechanic, never a purchase; minimal punctuation; refuses feature lists, adjective stacks, and above all explaining the medium.
- "My name is Bruno Simon, and I'm a creative developer (mostly for the web)." (winner-verified) — the parenthetical shrug does the humanizing.
- "please don't break anything!" (winner-verified) — the imperative hands over the mechanic and asks nothing else.
- "Start chating" [sic] (winner-verified) — a shipped typo left in — the register is human.
- "We do not chase trends or produce work that looks like everyone else." (Lusion, winner-verified, ©2026) — refusal stated as position.
- "INDEPENDENT DEVELOPER" / "AVAILABLE APR. 2023" (Aristide, winner-verified; stale status left in) — identity and availability as stamped labels.

**Imagery art direction** — generated or real-time in the engine, never stock. Igloo: procedurally grown ice, one block per project, chromatic/frost grade (case study). Bruno: low-poly matcap world, warm-light landmarks on dark navy (shipped/seed). Aristide: WebGL imagery behind display type, per-project color and letter positioning across 30 case studies, TNY as image (winner-verified + case study). Shader Development Studio: bespoke shader set-pieces in near-pure black, the scene itself carrying the narrative section to section (award page verified; the set-piece names are reference-carried, not independently confirmed). Worlds split per project; the substrate stays single so the site reads as one authored world.

**Mobile / touch** — reconsider the medium, never downgrade it away. Keep the WebGL or physics substrate on a LOWER quality preset — Bruno auto-switches presets on mobile, holding the init budget with geometry instancing, frustum culling, DRACO compression and ETC1S/UASTC textures. Pointer-only classes (magnetic cursor, pointer-parallax, velocity flowmap, state-morph cursor) go dormant, and the touch model is chosen by stack. *Physics field*: tap, drag and fling on a rigid body is native — a touch strength, not a fallback. *Spatial / playable world*: click, scroll, keyboard, touch and gamepad are recreated as 3D raycasts so the world stays fully navigable off desktop (Bruno, winner-verified). *Wheel-driven in-engine journey* — the archetype's most common stack and its biggest touch hole: touchmove feeds the SAME camera-lerp the wheel drives, with fling inertia captured at touchend plus momentum decay, and the scrub position survives the gesture; never fall back to native scroll, because the journey has none to fall back to (Lusion and Shader Development Studio both score Responsive 8.40 on wheel-driven no-native-scroll scenes). Library id: `journey-touch-momentum`. Press-class controls answer the tap with a 90–160ms flash floor. Cross-device parity is weighted higher here than in any other archetype: Usability is 30% of the score, judges check mobile first, a desktop-only WebGL world tanks it however impressive the canvas, and every unconventional pattern needs a discoverable fallback that reads within ten seconds. `prefers-reduced-motion` freezes the scene to a legible static frame and swaps scrubbed media to a poster; the resting DOM and HUD stay fully legible with no JS.

**Variation** — this section chain is one legal costume of the archetype, never THE skeleton. Structure is story-native: the body's sections derive from the universe's spine, then check against these roles for coverage — never the reverse. The axes serial winners measurably rotate between builds (21-artifact corpus, 5 studios): body content archetype and item counts, the ONE signature device (never reused across builds), the close mechanism, the hero medium, the index/HUD costume. What persists as DNA: type grammar, the motion register (the register itself, never the named reading/interaction kit — that kit is a device, rotated per build like the signature), annotation grammar as a form, engineering architecture. The same content archetype + item count + close mechanism recurring across two different-brand builds has zero winner precedent.

**Anti-signals** — page-level absences across the corpus: no card-grid fold; no persistent solid nav bar (nav is in-engine or a transparent corner); no pale tint hover; no concept-less spinner or bare-percent loader; no stock photography; no default lag-dot — Aristide's only follower is the `.e` explore indicator, Bruno's pointer is the car; no feature-list copy; no footer sitemap.

## Spectacle menu

Drive-and-discover (Bruno, winner-verified copy): start gesture → physics driving, secret rooms, whispers → play you can push against; replays differ. Links-as-particle-sim (Igloo, case-study evidence): select a link → particles reassemble into a different model per link → matter forming meaning. Click-into-project morph (Aristide, winner-verified structure): an index title and its WebGL imagery morph into the case study, per-project color → 30 distinct entries. Grab-and-throw (MoMoney, winner-verified): a body caught by a pointer constraint flies off at cursor velocity, collides, bounces and settles.

**The hero beat.** The first frame commits the MEDIUM AS THE WHOLE PAGE — not a spectacular hero above a quieter body, but the entire bespoke substrate present, simulating and armed from frame one: a physics world you can already bump (Bruno), an in-engine HUD scene with no loader boundary and the UI already rendering in WebGL (Igloo), a giant-type index over a live WebGL field (Aristide), a tactile surface you can already throw (MoMoney). The commitment is twofold — legibility in ten seconds through a discoverable anchor (Bruno's hand-drawn "click to start" arrow plus the floor-tile path; Aristide's corner counter booting straight into the index), since Usability is 30% and a pure-discovery nav lands below Honorable Mention; and aliveness from frame one, the substrate already pointer- or physics-armed and simulating. A frozen, motion-dead, non-interactive canvas is this archetype's defining defect — worse here than anywhere.

**The continuation beats** — the page is diffed against these, section by section.
- *Bruno* — there is no "after the hero": the world IS the page and it never sleeps. Live weather, day/night and seasons run for everyone at once, Whispers drift through the shared space, a global counter ticks, spatialized audio pans with the camera. Amplitude never drops to silence, and the peaks (secret rooms, the altar, the daily-resetting circuit leaderboard, achievement-unlocked vehicle skins) differ per visit — statefulness, not a one-shot animation.
- *Igloo* — no boundary anywhere: the intro renders in-engine and flows straight into the scene, the HUD is live from frame one, the camera drifts between ice zones with chromatic-aberration and frost-dissolve seams instead of section cuts, and the footer particle simulation coalesces into a different 3D model per link on hover — the interactive climax. No section is ever a static frame.
- *Aristide* — the WebGL image field behind the type renders continuously and the index rows stay hover-live at all times; the single amplitude peak is ON-CLICK, the route-morph carrying an index title and its imagery into the case study. Between clicks the substrate is never parked.
- *Lusion* — the body does not natively scroll: the wheel feeds the WebGL journey through the studio's own bespoke `scrollManager` lerp, and the engine keeps rendering at idle with zero input while hundreds of single-char split spans land the sparse text. The one understanding beat, the manifesto, sits over a still-moving 3D ground; contact-first close.
- *MoMoney* — the rigid-body field is live throughout: grabbed bodies drag under a pointer constraint, released bodies fly off at cursor velocity, collide, bounce and settle. The page stays a tactile physics surface between inputs, never a static image.
- *Shader Development Studio* — bespoke shader set-pieces chain section to section as narrated transitions; the scene is the connective tissue, never a backdrop. Animations/Transitions scored 9.40.

**The peak law** — verdict REFUTED and replaced, from the winner evidence: "exactly one climax" does not hold on this line. The LIVE-SUBSTRATE law stands in its place. ONE bespoke medium or metaphor IS the whole page — present, simulating and interactive from frame one to sign-off, with no hero-then-quiet separation, and often no scroll and no page beneath at all. The MANDATORY, UNCAPPED channel is the idle band: the substrate simulates continuously between inputs (weather and day/night, engine ticks at idle, physics settle, presence drift, node-graph values, a live clock), and its aliveness is not capped. Inside that live substrate, CAP the amplitude peaks at one or two REPLAYABLE, STATEFUL spectacles — an on-click route-morph, a footer particle sim, a secret room, a leaderboard run. Peaks stay scarce and they are stateful play, never a one-shot scripted animation. The forbidden failure mode is the FROZEN CANVAS: any moment where the substrate goes static, non-interactive or purely decorative — a hero shader that stops after boot, a WebGL field that renders on scroll-in then parks. Verdict test: if the canvas could be replaced by a still image without losing anything, the substrate was never built.

Evidence: Bruno's Portfolio (SOTD + SOTM 2026, winner-verified) has no hero/body separation to cap — the world is the entire page and a live weather/day-night/seasons system plus drifting Whispers plus spatialized audio keep it simulating between every input, with replayable state as the reward rather than a scripted wow-then-quiet. Igloo Inc (SOTY 2024, winner-verified award; case-study evidence for the mechanics) renders its whole UI in-engine with no loader boundary and no DOM page beneath, the camera drifting continuously and the footer particle sim landing as a late interactive peak. Aristide Benoist (SOTD 2021, winner-verified) puts the climax ON-CLICK, not in a hero animation that then goes quiet, with the substrate rendering and the rows hover-live throughout. Lusion v3 (Developer SOTY 2023, winner-verified) drives its journey from a bespoke scroll driver and keeps the engine rendering at idle with zero input, so the medium never resolves into a static page. The counter-law is already codified above — the substrate never sleeps, a frozen canvas is the one thing this archetype cannot show, and replayability is statefulness. Silence here is the defect, not restraint.

## Component index

Generated from `assets/components/manifest.json` — the authority for slots, variants, tokens, deps and `init` signatures, and the only place 11 of the 103 components record facts their file headers omit. Each row is the id plus the opening of its `whenToUse`, clipped: enough to pick, never enough to build. Grep the manifest for the chosen id to get its contract. Forms are the page skeletons (CSS, slots, variants); components are the behaviours that mount into their slots.

**Forms** (7) — page skeletons
- `about-overlay-footer` — The type-index close: the site's ONE prose surface is BOTH the page's real in-flow footer (a dead script leaves it standing whole — drive-verified under ?nojs…
- `bare-cue` — The gallery-stack's minimal close (Contassot / Vitasovic): no footer chrome, just a back-to-top cue ('SCROLL UP') and a year/edition mark on one slim baseline…
- `corner-counter-boot` — The DIEGETIC boot for the type-index arc: a fixed corner counter ticks 0→100 while the page stands VISIBLE and armed behind it — drive-verified from a cold…
- `in-engine-intro` — The engine's own ARRIVAL CHOREOGRAPHY: the first fold is the scene waking — the enhancer hands the builder's engine an arrive(p) driver via ready(arrive) and…
- `index-list` — The row-list body under index-reel-header: index/title/meta/thumb locked to one shared grid so column edges cannot drift and the meta cannot sprawl.
- `type-index-grid` — No marketing hero, no prose — the 100svh fold IS a dense index of oversized title rows locked to ONE shared grid (--_cols defined once, every row locks to it)…
- `world-boot` — The gated diegetic boot of the playable world — the Bruno spelling of the world-boot-gate gap (the Igloo spelling shipped in rung 8A as in-engine-intro; see…

**Components** (23) — behaviours
- `branded-preloader` — The immersive archetype's designed first-load state: progress tied to REAL asset loading (opts.assets counted, a Three.js LoadingManager-like { onProgress }…
- `counter-loader` — The numeric counter loader: rolls with real load progress, recolors to the accent near 100, lifts as a curtain.
- `dolly-zoom` — The scroll dive: a pinned full-bleed media scales toward a targeted focal point (the moon, the product, the plate) as the track scrolls — reversible…
- `drag-scrub-video` — Grab-drag over a whole video SECTION maps pointer/touch delta to currentTime — extends scrub-film's scroll/pointer-position modes with a drag verb, horizontal…
- `fill-invert-cta` — The universal primary-CTA move: full-token flood + label inversion on hover/focus — fill (direct pole swap) or wipe (a panel rises from the bottom edge).
- `gated-splash` — Section form.
- `grain-grade` — Fixed film-grain + optional vignette overlay for a poster grade.
- `idle-attract-auto-demo` — The verb-teaching attract mode for a non-standard world: after idleMs of REAL inputless idle (drive-verified engaging at t=5064/5085/5092 on a 5000ms setting)…
- `in-3d-dom-input-bridge` — The world-level input bridge, BOTH directions.
- `journey-touch-momentum` — The scrub for the wheel-driven in-engine journey with touch first-class: touchmove feeds the SAME position the wheel drives, release velocity becomes momentum…
- `living-presence-layer` — The inhabited idle band: a websocket (or injected source with an onDown death signal) feeds peer marks drifting in a pointer-events:none aria-hidden decor…
- `magnetic-cursor` — Earned custom cursor that does real work: magnetic snap to [data-ad-magnetic].
- `physics-tumble-field` — The manifest's first physics component: every field child becomes a body with weight, restitution and drag — grab, drag (a spring constraint keeps momentum)…
- `raycast-object-state` — Per-object hover/tap/hit states for interactive meshes INSIDE a WebGL scene — the axis the DOM-element canon omits.
- `rooms-procession` — The staged-rooms spine: an ordered array of discrete 3D scenes sharing one canvas + one camera rig, scroll transitioning the camera room-to-room 'like a museum…
- `scramble-decode` — Short labels/links/data-chrome decode from charset noise to the true string (entrance once; hover replay variant).
- `scroll-camera-dive` — The true-3D camera dive: scroll progress scrubs a real camera PATH — position + lookAt (+ optional FOV) keyframes, linearly interpolated, inertially eased so…
- `scroll-velocity-scene-distortion` — Whole-SCENE distortion driven by scroll/scrub SPEED — the post-hero momentum made visible: one smoothed signed velocity uniform warps the plate (center-lag…
- `scrub-film` — A film still the visitor drives — scroll or pointer maps to video currentTime.
- `sdf-scramble-substrate` — In-engine text for the fully-WebGL build: glyphs baked ONCE into a runtime signed-distance atlas (2D raster + exact euclidean distance transform), labels…
- `shader-surface` — The token-driven WebGL texture layer — gradient-mesh, noise-field, or pointer-ripple painted from the DESIGN.md palette.
- `spatial-audio-world` — The POSITIONAL audio bed of the playable world: each source a PannerNode tied to its object's world coordinates, the listener riding the camera, so sounds pan…
- `velocity-flowmap-hover` — Image hover that reacts to cursor SPEED, not just position: per-frame velocity splatted into a decaying off-screen RG flowmap (ping-pong framebuffers), the…
