# Award Imperatives

The non-negotiables that separate an 8+ (Site of the Day) from a 6–7 (Honorable Mention), distilled from the 2025–2030 award reference (Awwwards / FWA / CSSDA winners). These are **gates, not suggestions**: a build that skips them is competent, and competent is the ceiling this file exists to break.

Load at Phase 3 (source the layers each imperative needs), enforce at Phase 4 (build), and gate at Phase 5–6. The per-archetype files refine *how* each imperative expresses; this file is the floor under all of them.

## The line that decides it

A jury of working designers reads 6–7 vs 8+ in seconds. The tells are measurable.

- **6–7 (competent, the failure to avoid):** generic grid layouts, stock-feeling photography, desktop-first with mobile bolted on, **no single interaction worth discussing**. Template and AI-generated layouts are recognized instantly — the fastest way to fail.
- **8+ (what wins):** one signature unforgettable interaction; mobile *reconsidered*, not merely responsive; complex visuals that load fast on mid-range devices; real content with genuine photography; scroll as narrative, content unfolding with purpose and pacing; precise animation choreography in timing, easing, and sequencing.

The north star is not maximum spectacle. It is **one unforgettable signature moment, executed with precision across every device, loading in under two seconds.**

## Transverse imperatives — every build, every archetype

Each is a gate. A build missing one is filed in the Phase 5 verdict as a named gap, never silently shipped.

1. **One signature interaction — bespoke, named, on the make-or-break surface.** Not a load fade, and not a menu pick: a scroll-driven reveal, a parallax, a magnetic button, a kinetic type beat are *categories* — each sits unchanged on any rival's site in the archetype. The signature is a mechanic invented for THIS brand's world, one a stranger describes by its verb, not its mood: *the site where you drive the car* (Bruno Simon), *where you move through the pavilion* (Cartier), *where the filmstrip scrubs the archive* (Siena) — never "the one with nice scroll reveals." **The bespoke test:** could this exact interaction sit on a rival's site in the same archetype, unchanged? If yes, it is a category — regenerate it, never file it as a gap. **And it lands on the make-or-break surface** — the hero, the first impression, not a reward buried below the fold: a bespoke moment in section four while a category medium (a scrubbed stock clip, a parallax) carries the hero is a gap, however good the moment. Either the hero's own medium *is* the signature, or the signature is pulled up into the hero. Ambition is fixed at concept, before buildability — a mechanic that needs WebGL/R3F, canvas, or a scrubbed video routes through Phase 3 sourcing and the one WebGL delegation; a signature downgraded to a safe reveal *because it was easier to build* is a skipped gate. The signature is judged on **execution fidelity**, driven as a real user — a primitive 3D that reads CGI, or a drag that fights the pointer and shows the browser's native ghost, fails however novel the idea — and it **serves the identity, never bends it** (a NOIRE flacon stays black; the reveal never turns it brown to make itself work). For a real product with no premium 3D path, a scroll-scrubbed real video beats a hand-built primitive. Method, the world's-verb derivation, fidelity routing, and the identity gate: `signature-invention.md` (with `ingredients/web3d-for-sites.md` for the 3D floors). This is the single strongest predictor of 8+ and the axis competent builds miss.
2. **A real navigation pattern.** Never "no nav." The two rewarded patterns: a **sticky header that hides on scroll-down and slides back on any scroll-up** (~300–400ms — the gold standard, and the mobile default), or a **full-screen overlay menu** that is itself an editorial moment (60–120px type, staggered reveal). Desktop header under 10% of viewport height; mobile under 60px. A hero-only list of anchors that scrolls away is not a navigation system — and a fixed bar that never hides is the same tell inverted. Canonical implementation (the two decoupled axes, the hero-sentinel crossing, SSR-correct first paint, freeze-on-focus for WCAG 2.4.11, reduced-motion flips instantly, and the show gate distinguishing a scroll-*stop* from a scroll-*up* so the bar never flashes back at rest): `navigation-patterns.md`.
3. **Smooth scroll + scroll-as-narrative, motion split by what it moves.** Content unfolds with pacing, not uniform per-section fades. The model splits (`motion-palette.md`): **content reveals fire once and persist** — content that re-hides on scroll-up is a documented NN/g usability failure (users lose the thread hunting the scroll position that brings the copy back); **decorative / scrubbed motion is reversible and scroll-linked** via native `animation-timeline: view()/scroll()`, which never hides content. A reversible content reveal is a declared Editorial/Immersive choice guarded by the `cover`-phase range rule, not the default. `Lenis` (or an equivalent that preserves native `position: sticky`) smooths the scroll where the register wants it. One climax, at least one rest — never every element fading in on scroll.
4. **Image reveals via `clip-path`, not opacity.** The `clip-path: inset(...)` wipe (hardware-accelerated, zero layout shift) is the signature image technique of the era. Plain `opacity: 0 → 1` on every image reads as the default nobody chose.
5. **Micro-interactions — the details judges notice.** At least the ones the archetype earns: a magnetic primary CTA, an underline that draws on hover (`scaleX(0 → 1)` on `::after`), a lerp-eased custom cursor on creative/immersive builds, image-preview-on-hover for portfolio links. A page with only resting states reads unfinished.
6. **Modern CSS where it earns its place.** OKLCH for color (perceptually uniform, no muddy gradient middle; derive tints/shades from one brand token). Container queries for self-aware components. `:has()` for conditional styling without JS. `@property` for animatable custom properties. These are the current edge; hex-only and viewport-only breakpoints are the tell of a dated build.
7. **Performance budget — measured, not declared.** A gate at Phase 5, read from the browser tooling, never asserted: **LCP < 1.5s · CLS < 0.05 · INP < 100ms · total weight < 3 MB · sustained 60fps.** Serve **AVIF > WebP > JPEG** via `<picture>` (AVIF is ~50% smaller than JPEG at equal quality); variable fonts (one file replacing 20+ requests); `loading="lazy"` and `content-visibility: auto` below the fold. Animate only `transform` / `opacity` / `filter` / `backdrop-filter` — the four GPU-composited properties.
8. **Mobile reconsidered, not responsive-bolted-on.** The mobile layout is a re-thought performance of the same idea (touch-first, thumb-zone, bottom-reachable actions, the show-on-scroll-up header), not the desktop grid narrowed. Usability is 30% of the Awwwards score and jurors check mobile first.
9. **Real, genuine photography — never stock-feeling.** The hero image is the make-or-break first impression; a generic or stock-scatter image caps the whole page. One art-directed treatment across every image (`imagery.md`). Where photography is unavailable, a deliberate typographic or generated visual — never a filler slab.
10. **Accessibility from day one** (already carried by `foundations.md` + `ship-ready-floor.md`): `prefers-reduced-motion` replaces motion with opacity (never removes it), custom `:focus-visible`, skip link, semantic landmarks, AA contrast on every state including hover/disabled, kinetic split-text carries an `aria-label` on the parent, custom cursors are `aria-hidden`. Award-winning-and-inaccessible is the endemic failure; do not join it.

## The comparative bar — how these get judged

The imperatives above are countable. The verdict on whether the build *wins* is not, and it is where competent work slips through: **an absolute judgment grades leniently** ("this is nice" → 7), **a judgment relative to the best is brutal and accurate** ("does this beat the current Site of the Day for this archetype? what does the winner do that this doesn't?").

So every review — R1, R2, standalone — scores the build **against the archetype's canonical winner** (`exemplars.md`: Cartier for Corporate Luxury, Siena for Editorial, Lando Norris for Immersive, Anime.js for Bento, and so on), never against "is this good in a vacuum." The comparison is the primary driver of the Concept and desire verdict, not a closing footnote. Pull the winner up, put the build beside it, and answer: *would a jury pick this over that? what would they dock?*

## The restraint veto — a clever concept must earn its props

A metaphor or high concept ("the homepage is tonight's magazine issue") is an asset only until it starts *manufacturing* clutter. Each literal prop the concept invites — a registration line, a table-of-contents nav, a tipped-in paper card, a masthead rule — must independently survive one question: **would a real brand at this tier ship this, or is it art-directed cleverness that reads as trying-too-hard?** Quiet luxury is subtraction; a concept that adds ornament to prove itself is inverting the archetype. When props fail this test, the fix is to cut them, not to polish them — and if most of them fail, the concept itself is the defect (regenerate at Phase 1). This veto attacks the *premise*, not the execution, and it is the check the coherence-focused rubric misses.

## The judging weights

Mirror the Awwwards allocation when prioritizing fixes: **Design 40% · Usability 30% · Creativity 20% · Content 10%.** Usability is larger than creativity — a stunning build that traps the scroll or hides its nav loses more than a restrained one that flows. CSSDA weights UI 40 / UX 30 / Innovation 30; FWA rewards experimental work harder. A P0 on a Usability heuristic outranks a P1 on Creativity.

## Anti-patterns that cap the score

Beyond `anti-patterns.md`, the award reference names era-specific expiries — treat each as a stop-and-fix when it is load-bearing:

- Template / AI-generated layouts (recognized instantly).
- Scroll-hijacking on text-heavy content (extreme frustration in NN/g testing); the illusion-of-completeness pause that makes users think they hit the end.
- Static gradient as the primary design element; bento grid past saturation; heavy parallax as the primary effect.
- Glassmorphism failing 4.5:1 contrast; `outline: none` applied globally; generic chatbot widgets loading on render.
- Inconsistent craft — a polished homepage over weaker inner surfaces reads as incomplete.

## Per-archetype expression

The transverse imperatives hold for every build; how the signature and the navigation *express* is archetype-specific. Each archetype's own reference file refines this — the row below is the floor and the winner to measure against. The navigation default is a show-on-scroll-up header unless the archetype's register calls for an overlay or a bespoke metaphor.

| Archetype | Signature interaction register | Navigation flavor | Winner to beat |
|---|---|---|---|
| **Minimalist** | one restrained scroll-reveal or a type-scale moment that carries the page | minimal top bar, show-on-scroll-up | Terminal Industries |
| **Brutalist** | kinetic / glitch type beat, deliberate jar | raw fixed block or hard overlay | FlowFest 2025 |
| **Editorial** | scroll-driven article reveal, pull-quote choreography, or a `clip-path` image wipe | show-on-scroll-up header, or a dual-menu editorial nav | Siena Film Foundation |
| **Bold / Maximal** | kinetic SplitText climax, layered parallax, staggered reveals | full-screen overlay staged as an event | Ponpon Mania |
| **Immersive / Cinematic** | scroll-scrubbed 3D or video sequence on a pinned section | minimal HUD-like top bar or overlay | Lando Norris |
| **Experimental** | the bespoke navigation metaphor *is* the signature | the metaphor itself, plus a conventional escape hatch | Bruno Simon |
| **Corporate Luxury** | one slow tasteful reveal or hover on the hero object, long easing (`cubic-bezier(0.16,1,0.3,1)`, 1–1.5s) | quiet show-on-scroll-up header | Cartier WAW 2025 |
| **Bento / Card** | a tile that *demonstrates* its claim (a live demo), or tiles morphing between configurations | simple top bar | Anime.js v4 |
| **Spatial Organic** | depth and parallax layers, glass, organic motion easing | floating glass bar | Arc / Granola |
