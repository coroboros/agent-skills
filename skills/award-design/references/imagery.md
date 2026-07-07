# Imagery

The largest single imposition most AI builds miss. Judges read empty visual zones as "unfinished" before they read anything else, so a page with no real images is a placeholder, not a design. This protocol is asset discipline: what to use, in what priority, and what never to fake.

Load while building under the universe, and again at the Phase 5 gate before ship.

## Zero images is a bug

Even a minimalist build carries 2–3 real images. A hero that is a headline floating over a flat gradient with no visual decision is the canonical placeholder hero — not a minimalist one. The visual can be:

- Photography (real or generated), 3D / canvas, or a textured / illustrated surface.
- A *deliberate* typographic treatment that IS the visual — kinetic SplitText, oversized editorial display, type-as-image. Brutalist and Editorial heroes earn the floor on type alone when the type is the art. The bar for "the type is the art": display-scale presence (the composition would hang as a poster), kinetic or compositional intent — body-scale text inside a card never qualifies, however good the copy. A page shipping zero imagery clears the floor only over this bar.
- A consistent illustration system the universe decrees — drafting plates, diagrams, hand-drawn figures. The bug is *empty visual zones*, not the absence of photographs specifically.

What does not clear the floor: a centered headline over a purple/blue or beige gradient, stock-feeling hero slabs, or a single icon standing in for a hero image.

**The silhouette test.** The hero object is nameable from its first frame by someone who hasn't read the copy. An exploded, abstracted, or assembling state may carry the narrative — but it keeps an anchor of legibility (a readable sub-assembly, a ghost outline of the whole, one completed detail at recognizable scale). Drama that costs recognition costs the sale. Same bar for the model itself: push definition past primitive stand-ins (profiles, bevels, material breaks) — a box-built object reads as placeholder at close range.

## No fake-div screenshots

Never hand-roll a fake product UI out of divs, borders, and gradients to simulate a screenshot or dashboard. It reads as AI filler instantly and never matches the real product. Order of preference:

1. A real screenshot or export of the actual product.
2. An honest, labeled placeholder (`[dashboard — replace with real capture]`) sized to the final aspect ratio.
3. A genuine illustration in a consistent style — never a CSS pastiche of an interface.

An honest labeled placeholder beats a hand-rolled CSS illustration of a UI: the placeholder tells the user exactly what to supply; the fake screenshot pretends the work is done.

## Real brand logos

- Source marks from **Simple Icons** (simpleicons.org) or **devicon** (devicon.dev) — real SVG wordmarks and glyphs, never a text span styled to look like a logo.
- Ship **light and dark variants** — a single-tone mark disappears against half the surfaces it lands on.
- A logo wall is **logos only** — no mixed text labels, no "and 200+ more" filler. Size by visual weight, not bounding box.
- An invented brand gets an invented mark — a considered monogram or geometric SVG glyph in the page's own style, drawn with intent and **verified rendered in the browser**; a plain text wordmark posing as a logo, or a generic colored dot / status-tick beside the wordmark, reads as placeholder. The *same* mark drives the favicon and `icon.svg` (`ship-ready-floor.md`) — one identity across the tab and the page, never a random dot at either.

## Branded builds — acquire and verify real assets

When the brief names a real brand, product, or place, the design is built around real assets — search before you invent:

1. **Search official sources** — the brand's own site or press kit, the product's real screenshots, the place's real photography. Real assets read as "made"; CSS silhouettes read as filler.
2. **Verify before use** — resolution sufficient for the slot, usage rights clear, the version current (last season's packaging or an old UI dates the build on sight).
3. **Record source and slot** — note each asset's origin and where it lands, so the build is reproducible and the user can swap in finals.

For a generic or unnamed brand, skip to the order below (generate / seed / placeholder). Never fake a named brand's assets out of divs.

## Acquisition priority order

The build has to *show* the universe alive — a first-launch design the user opens to see the direction working, without having to supply finals first. A brief that literally asks for "placeholder images" is asking for real stand-ins that let the design be judged, not gray boxes or CSS gradients — read it as this order (generate / curated stock), and reserve rung 4's labeled placeholder for a slot that genuinely cannot be filled. So when a slot needs an asset and none was supplied, walk the order; never skip ahead to inventing one.

1. **Generate it** — an image-generation tool available: produce a contextual asset (brief-matched subject, palette, crop). First choice — on-brief and rights-clean.
2. **Curated stock, chosen surgically** — no generation tool and the slot needs real photographic immersion (a hero, a plated dish, a portrait): hand-pick from a free-license library (Pexels, Unsplash) held to the bar of a commissioned shot. Not "a stock photo" — *this* one: on-subject, on-palette (the universe's darkness, warmth, temperature), exceptional composition, negative space where the layout needs type. Reject on sight anything stock-feeling — flat studio light, smiling-team generic, mismatched temperature, the shot everyone has seen. **Download and optimize it — never hotlink** (a live `images.unsplash.com` src breaks often, reads stock, and fails the perf gate + scanner). Pass every pick through the one treatment (below), and flag it in the asset list as a placeholder to replace with a commissioned or generated final before a real award submission. A surgically-chosen, graded photograph does not read as stock; an unselected scatter does — that distinction is the whole rule.
3. **Seed a real source** — `https://picsum.photos/seed/{context}/{w}/{h}` with a contextual seed, for secondary or background slots where curation isn't worth the effort, or when a stable deterministic image per slot matters more than subject fit. Deterministic seed, never `random`.
4. **Labeled placeholder + tell the user** — none of the above fits: ship a placeholder sized to the final aspect ratio and emit the asset list — what each slot needs, its dimensions, where it lands. Never block the build; never fake it with a CSS-gradient illustration.

The failure the reference names is *stock-feeling* photography — generic, unselected, ungraded, scattered across three color temperatures — which tanks scores (`anti-patterns.md` *Design failures*, `award-imperatives.md` #9). A single exceptional photograph chosen for this universe and graded into it is the opposite, and for a build the user launches to *see* the design it beats a random seed or an empty slot.

## One treatment

Sourcing is half the job; unification is the other half. Every image on the page passes through the universe's treatment — the grade, duotone, grain, or crop language named in the DESIGN.md photography direction. Three technically good images with three different color temperatures read as stock scatter; the same three under one grade read as art direction. When assets arrive mismatched, unify in CSS (`filter`, blend modes, an overlay tint in the surface hue) rather than shipping the scatter.

## Seams grade, never cut

A full-bleed image or video meets its neighbour with a **graded transition**, never a hard horizontal cut into a flat band. The hero's bottom edge dissolves into the next section — a gradient `mask-image` on the media, or a scrim in the surface hue fading it into the ground — so the boundary reads as one continuous descent, not two stacked rectangles. A crisp edge where a photographed sky meets a flat near-black block is the tell: the eye catches the rectangle, and a hero that ends there "fades too brutally" into the section below. Same rule between two adjacent full-bleed images — cross-fade or share the treatment, never butt them edge-to-edge. Verify the seam in the browser at the boundary, not just section centers (`preflight.md` §8).

## Filter wiring

Two checks feed the stop-and-fix filter, carried as axiomatic rejections in `anti-patterns.md`:

- **Hero carries a real visual** — fails on a text-over-gradient hero with no visual decision; the deliberate-typographic-hero path is the override.
- **No fake-div screenshots** — fails on any div-built simulated UI; an honest labeled placeholder passes.
