# Brutalist — tier 1

**Voice.** Typography is the design, never decoration around imagery — display faces at 80–200px+ carry scale, character and emotion alone. Flat fills hold the surface, shadows carry no blur, gradients do not interpolate; geometry is hard and structural, so the composition reads as built rather than rendered. Density oscillates bimodally — tightly packed monospace clusters against vast calculated void, binary not gradual; a page holding steady mid-density reads as restraint without conviction. The system coheres through one physical metaphor (objects-on-a-table, terminal-runtime, CRT-film, print-shop), one easing family, one border/shadow/radius system. When a control fills it takes the full saturated accent, never a pale tint. The fil rouge is continuous motion at rest: the page never becomes a bank of fire-once reveals with silence between them.

**Register licence.** The loud register governs the surface grammar — type, fills, borders — not the idle amplitude, which is a per-brief choice. Naked City Films takes SOTD 2026-01-23 at 7.34 on a single rAF loop its makers frame as "restraint paired with intensity … movement without chaos"; FlowFest sits at the opposite end with a marquee and a cursor-tracked mascot, Animations/Transitions 8.20 its top developer sub-score. Both win, so never force a loud marquee onto a restraint brief. Where the register actually binds is usability: Naked City's Usability 6.99 sits half a point under its own Design 7.51 and is the corpus's lowest sub-score — keyboard reach, visible focus and contrast are what the aggression costs, and they are not negotiable. The jarring `steps(n)` register is reserved for hero type and micro-toggles; scroll reveals ride `expo.out` / `power3`.

**Anti-signals — these disqualify.**
- A pale `color-mix(accent, white)` wash on a primary control. Fills take the full accent, or the button presses instead.
- One hover rule reused across button, link, card and nav. Each element class owns a distinct (trigger × property) pair.
- A scrolled nav growing a solid surface with a differently-colored `border-bottom`, or a `backdrop-filter: blur()` frosted bar — all four live-read winners stay transparent, borderless and un-blurred at rest.
- A smooth lerped `mix-blend-mode: difference` follower blob: that cursor belongs to the smooth-agency line.
- Pure `#000` on `#FFF`. Even the starkest winner ships `#000F1D` on `#F7F7F7`.
- A uniform `fade-up 0.6s` on every section; rounded soft-shadow cards — radius is `0` or a committed pill, shadows are hard offset `0 4px 0`.
- Opening on a card or bento grid, a product-shot carousel, a functional link-list footer, a generic cross-fade route transition.
- The dead middle: entrance reveals with nothing welded to the scrollbar behind them.

**Macrostructures it runs.**
- `studio-index` — loader-into-navbar or char-diff identity hero, no in-fold CTA, hover-charged work index, footer-as-finale where the single peak lands last. The primary spine, and the only one grounded in a source that calls its site brutalist. Route here when the work is the argument. (Eloy Benoffi, winner-verified; Treize Grammes supporting)
- `argument-scroll` — in-character loader → drawn-SVG type-as-image hero → the lineup as the capped peak at ~40% → community band → FAQ rest → oversized reprise close. Route here when the brief has a bill to prove: festival, conference, event. (FlowFest 2025, SOTD-verified order, brutalist-adjacent)
- `studio-reel` — a stepped-counter loader Flipping into a showreel, a vertical case slider scrubbed by scroll, contact close. Route here when a reel is the product. (Joffrey Spitzer, technique — no award verified)

**Exemplar.**

| site | award | signature |
|---|---|---|
| Eloy Benoffi · `eloyb.design` | Awwwards Honorable Mention + GSAP Site of the Day + CSSDA Best UI / Best UX / Best Innovation / Special Kudos — an HM carries no published overall score; the line's scored anchors are Sui Overflow 7.48 (SOTD 2025-04-15) and Naked City 7.34 (SOTD 2026-01-23) | The spectacle is deferred to the footer: mousemove clones the CTA up to 200 copies under `mix-blend-mode:difference`, exiting on `back.in(1.7)`. A scrubbed flower-pluck field (`scrub:8`) and different-speed title rows (`yPercent -300`, `scrub:0.6`) shear the entire scroll beneath it, so the loudest interaction lands last. |

**Reflexes — enumerate, then reject by name before committing.**
1. Hot pink `#FF90E8` on white, 3px black borders, 6px hard shadows: the Gumroad screenshot.
2. Archivo Black uppercase over Space Mono, chosen in ten seconds and left to stand in for art direction.
3. The same `box-shadow: 8px 8px 0` and the same border stamped on every card in the grid.
4. A full-width marquee band pasted at every section break as the proof of aliveness.
5. `steps()` sprayed across every transition, so the whole page stutters instead of the hero type.
6. A glitch / RGB-split loop running continuously on the headline rather than in bursts.
7. `[ SECTION 01 ]` and `>>>` scattered as texture, with no manifest, unit or revision behind them.
8. Deliberate ugliness as the whole idea — clashing sizes, no grid, conviction claimed after the fact.
