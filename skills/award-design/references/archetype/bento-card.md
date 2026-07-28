# Bento-card — tier 1

**Voice.** Modular asymmetric tiles, each a self-contained information unit carrying its own visual treatment, its own typographic register and its own state. Every tile *demonstrates* its claim in one of three proof registers — a running demo, a slice of the real product UI, or a custom illustration where no UI exists to slice — because a label-and-body stamp that never shows the claim is the failure this archetype exists to avoid. Container queries make tiles self-aware of their own span rather than the viewport; consistent corner radii (12–32px) and equal gutters (12–24px) hold the rhythm while spans vary hard (1×1, 2×1, 2×2, 3×1). Cohesion is one binder physics expressed differently per element class — motion, edge-light or border-glow — never one hover stamped on every tile. The structure teaches itself.

**Register licence.** The hero under-commits on purpose: copy-led, a ≤7-word category claim beside one anchor that is already running, and no card-grid fold — the spectacle budget is spent downstream. Excess is legal and expected inside the tiles and at section scale. Anime.js v4 takes SOTD 2025-05-06 at 7.62 with Animations/Transitions 9.00 on its Developer Award (7.84): this line wins on motion, and the motion lives in the grid. Restraint binds the page ground — native pointer, native scroll (0 of 3 winners ship a wheel smoother), one accent role per tile, one hover affordance for the whole grid. A diffuse climax is fully legal: Endex takes an Awwwards Honorable Mention (2025-03-24, 15/17 jury votes) with no spectacle peak anywhere on the page.

**Anti-signals — these disqualify.**
- Three equal cards in a row with rounded corners called a bento; uniform tile treatment where spans never vary.
- A tile that names its capability in a label and a body line and never shows it.
- One universal card hover — `translateY(-4px) scale(1.02)` plus a grey `box-shadow` — repeated on every tile.
- A washed pale-tint button fill: the accent at ~10% alpha fading in, which reads as a disabled hover.
- A contrasting-colored `border-bottom` under the nav; winners' borders, when present, are same-family hairlines at ≤5–6% alpha.
- A global custom cursor — a lagging dot or ring sitewide — over a grid that is scanned and clicked.
- A per-letter kinetic headline on a non-motion brand; uniform `fade-up-on-everything` with linear per-element delays.
- The dead grid: proof tiles whose only animation is a single-run on-scroll reveal, with no section-scale momentum either.
- Heavy hero parallax, and a wheel smoother (Lenis, Locomotive) fighting the grid's scan-and-click read.

**Macrostructures it runs.**
- `specimen-tour` — one capability per tile, the artifact demonstrating itself, a run of pinned `100lvh` demo panels as the one designed peak. Route here when the product is a developer tool, library or API that can run itself. (Anime.js v4, winner-verified)
- `capability-grid` — editorial 12-col feature grid carrying concrete proof, climax diffuse, even build to a single CTA close. Route here when the brief has a SaaS or AI product with real product UI to show. (Endex, winner-verified)
- `structural-decomposition` — the platform broken into named modular tiles rendered as custom illustrations, then the audience segmented into expandable cards. Route here when the product is a platform of named modules with no UI to slice. (Sui, winner-verified)
- `highlights-bento` — N claims in one screen, tiles scrubbing into place after the fold, then per-theme full-bleed deep-dives. Route here when the brief supplies N discrete highlights. (Apple, shipped-canonical)

**Exemplar.**

| site | award | signature |
|---|---|---|
| Anime.js v4 · `animejs.com` | Awwwards SOTD 2025-05-06 — 7.62 overall, Developer Award 7.84 with Animations/Transitions 9.00 | Left-copy / right-demo hero whose red-dot period pulses and whose subject word swaps on a loop — that IS the intro. Then a run of pinned `100lvh` panels over one persistent `position:fixed` demo layer: copy cross-fades while the demo runs the heading's claim and you drag or scrub it, page-wide token recolor per section. The peak replays instead of spending. |

**Reflexes — enumerate, then reject by name before committing.**
1. Three equal cards in a row, an icon on top of each, rounded corners — the feature row wearing a bento label.
2. `translateY(-4px) scale(1.02)` with a grey shadow as the hover, on all twelve tiles.
3. A Heroicons glyph, a heading and two lines of body as the whole tile: describing the claim instead of showing it.
4. The card grid as the fold, before the page has made a claim.
5. `fade-up` on every tile with a linear `delay: index * 100ms` as the entrance choreography.
6. Purple-to-blue gradient blobs behind glassy cards standing in for per-tile art direction.
7. Placeholder metrics — "10k+ users", "99.9% uptime" — in the stat tile, tabular figures forgotten.
8. Lenis dropped in for smooth scroll and a sitewide custom cursor, both added before the grid has any life of its own.
