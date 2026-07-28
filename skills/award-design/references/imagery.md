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

## Native resolution or nothing — the fidelity floor

Soft pixels read as broken before anything else on the page is judged — a real photograph upscaled past its pixels is the fake-div of resolution. The floor is measured (`rendered device px / shipped source px` at the asset's worst moment — deepest scrub zoom, largest cover-fit, hover scale — computed, never eyeballed) and it is **two floors, because the winner corpus measures as two asset classes**:

- **Scrubbed / zoomed sequence frames: delivered pixels ≥ device pixels (ratio ≤ 1.0).** The scrub magnifies past cover-fit and motion holds the eye on the surface. Apple's current tier is 3600×2100 — *supersampled* above desktop retina; the 7.9-scoring film site ships 1920–3900px textures; the one 2×-upscaled sequence winner ever measured scored 7.3, the SOTD floor.
- **Static full-bleed photography: ≥ 1.0× of CSS pixels, and zero visible softness at rendered scale.** Winners routinely carry film-treated stills to ~1.5–2.8× of device pixels (a 7.62 SOTD serves 1024px stills full-bleed) — *survivable only under a committed grain/grade/motion treatment on a cinematic register*, judged at arm's length in the browser, never assumed.
- **Below 1.0× of CSS pixels: disqualifying anywhere** — no measured winner ships principal photography narrower than the viewport's CSS width.
- **A scrubbed sequence is real frames or it is not a sequence.** Every frame is a distinct real sample — a footage frame, a render frame, a drawn frame; 30fps extraction from real video is the corpus norm, and **~90 distinct frames per scrubbed section is the floor** (the smallest measured winner sequence is 89; typical 148–1,182). Baking synthetic in-betweens from a handful of stills has **zero winner precedent** — holding only stills, animate the full-resolution still live (transform/WebGL push — the Siena route, every source pixel preserved) and never bake it down. **The live-animated still satisfies this fidelity floor only — it never satisfies an immersive brief's hero-medium verdict** (dense and moving): on an immersive world, a stills-only library forces the re-scope conversation, and the re-scope is not the builder's call — it requires the failed footage-acquisition walk quoted verbatim (the video-generation probe and stock-footage search outputs, per the Tooling-gaps standard) AND the user's confirmation, because it changes the brief's committed archetype.
- **Treatment never buys back resolution on a scrubbed sequence, and never below the CSS floor.** On static full-bleed stills a committed grain/grade/motion treatment is the only thing that legitimately carries them past CSS-parity (the 7.62 precedent above) — but it never legalizes a sub-CSS source, and it never applies to scrub frames: motion + zoom re-expose every soft pixel the grade hid.
- **Emitting below a source you hold is negligence, not optimization.** The phased budget (`award-imperatives.md` #7) streams heavy tiers behind the loader precisely so fidelity is never traded to bytes — a 6000px original in the working directory and a 1280px derivative on the wire is the exact trade it bans. And acquire at the maximum resolution the rung offers: requesting assets pre-shrunk to slot size is the same trade made one step earlier.

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

The build has to *show* the universe alive — a first-launch design the user opens to see the direction working, without having to supply finals first. A brief that literally asks for "placeholder images" is asking for real stand-ins that let the design be judged, not gray boxes or CSS gradients — read it as this order, and reserve rung 4's labeled placeholder for a slot that genuinely cannot be filled. So when a slot needs an asset and none was supplied, walk the order; never skip ahead to inventing one. **The order is class-scoped**: hero, signature-product, and campaign-class slots never take a generated asset — those classes come from the client pack, a covering reference scene, or licensed pro media, and when none of the three exists the slot ships a labeled, aspect-true placeholder plus a precise asset request upward (a scene spec or sources-tried list) — never primitives, never a stand-in, never a generic marketplace object posing as the signature product. Signature assets come from dedicated production capability — the client, a commissioned professional, or the library pipeline; the build never fakes one at composition time.

1. **Generate it — atmospheric and secondary slots only** — an image-generation tool available: produce a contextual asset (brief-matched subject, palette, crop) for texture, background, and secondary slots. Never for a hero, signature-product, or campaign-class slot (see the class scoping above); the ledger row carries class `generated` and the curation floor applies unchanged.
2. **Curated stock, chosen surgically** — no generation tool and the slot needs real photographic immersion (a hero, a plated dish, a portrait): hand-pick from a free-license library (Pexels, Unsplash) held to the bar of a commissioned shot. Not "a stock photo" — *this* one: on-subject, on-palette (the universe's darkness, warmth, temperature), exceptional composition, negative space where the layout needs type. Reject on sight anything stock-feeling — flat studio light, smiling-team generic, mismatched temperature, the shot everyone has seen. **Download and optimize it — never hotlink** (a live `images.unsplash.com` src breaks often, reads stock, and fails the perf gate + scanner). Pass every pick through the one treatment (below), and flag it in the asset list as a placeholder to replace with a commissioned or generated final before a real award submission. A surgically-chosen, graded photograph does not read as stock; an unselected scatter does — that distinction is the whole rule.
3. **Seed a real source** — `https://picsum.photos/seed/{context}/{w}/{h}` with a contextual seed, for secondary or background slots where curation isn't worth the effort, or when a stable deterministic image per slot matters more than subject fit. Deterministic seed, never `random`.
4. **Labeled placeholder + tell the user** — none of the above fits: ship a placeholder sized to the final aspect ratio and emit the asset list — what each slot needs, its dimensions, where it lands. Never block the build; never fake it with a CSS-gradient illustration.

The failure the reference names is *stock-feeling* photography — generic, unselected, ungraded, scattered across three color temperatures — which tanks scores (`anti-patterns.md` *Design failures*, `award-imperatives.md` #9). A single exceptional photograph chosen for this universe and graded into it is the opposite, and for a build the user launches to *see* the design it beats a random seed or an empty slot.

## Provenance — the asset ledger

Every shipped texture, model, frame, and photograph traces to a **provenance ledger** row, written at acquisition time (post-hoc rows rationalize). The classes are a closed set — `reference-scene` · `client-pack` · `licensed-media` — plus `generated`, legal for atmospheric/secondary slots only; "generated at build" is not a value for anything else, which is what mechanically kills procedural hero objects, fBm stand-in worlds, and frames baked from stills: they have no legal row to cite. Row fields: slot (page + section + role) · provenance class · source (scene id, pack path, or library + URL) · license (name + one terms line + proof) · native px, measured with a pasted command, never read from a filename · worst-moment rendered px + ratio · DA-match sentence · the four curation-axis verdicts · the acquired-at-max attestation. **Every binary in the shipped asset dir traces to a row — an orphan file is a FAIL.**

**The curation floor — the second gate beside the fidelity floor**, judged at 1:1 native pixels, binary per axis, one FAIL = the asset is out: (1) **background control** — the environment is a decision (seamless, built set, or on-universe location); any incidental context — shop fixtures, potted plants, price tags, passersby — fails; (2) **styling and props** — every object in frame is placed on purpose and on-universe; an unaccountable object fails; (3) **lighting intent vs the declared DA** — direction and quality match the DESIGN.md photography direction BEFORE grading; grade unifies, it never rescues wrong light; (4) **subject match** — the thing in frame IS the brief's thing (material, era, category, state); "a pendant" never satisfies THE pendant. The floor in one line: *a shot you could not run in a print ad is banned* — all four axes pass AND zero incidental elements. The pixel floor stays a separate, automatable gate; content-blindness there is by design, this floor is its pair.

**Pro sourcing routes (fictional brands included)**: environments/footage — Artgrid, Filmsupply, KitBash3D, Fab/Megascans, Poly Haven (CC0), NASA SVS (public domain); people — release-guaranteed sources (Stocksy United, Getty/iStock); free-tier libraries stay legal for non-people secondary slots under the curated-stock rung. **Signature product objects have no marketplace route** — marketplaces sell pre-existing SKUs; the class ships in the client pack or as a campaign reference scene, and its absence is the asset-request case above. The asset request carries: the failed acquisition walk quoted verbatim (sources tried), the license that could not be resolved named ("probably fine" is not a provenance class), and the scene spec (object, materials, camera path, states) when the gap is the hero medium. The build continues either way — the slot ships its labeled placeholder and the request; the request is what turns it into a final.

## One treatment

Sourcing is half the job; unification is the other half. Every image on the page passes through the universe's treatment — the grade, duotone, grain, or crop language named in the DESIGN.md photography direction. Three technically good images with three different color temperatures read as stock scatter; the same three under one grade read as art direction. When assets arrive mismatched, unify in CSS (`filter`, blend modes, an overlay tint in the surface hue) rather than shipping the scatter.

## The art-direction brief

Every asset is acquired under a one-sentence art-direction brief — subject, crop, light, grade — taken from the archetype's Page recipe imagery formula and recorded in the asset list (Phase 3). An asset sourced without its brief is improvised art direction: the scatter the one-treatment rule then has to rescue in CSS. The brief comes first; the filter is the fallback.

## Seams grade, never cut

A full-bleed image or video meets its neighbour with a **graded transition**, never a hard horizontal cut into a flat band. The hero's bottom edge dissolves into the next section — a gradient `mask-image` on the media, or a scrim in the surface hue fading it into the ground — so the boundary reads as one continuous descent, not two stacked rectangles. A crisp edge where a photographed sky meets a flat near-black block is the tell: the eye catches the rectangle, and a hero that ends there "fades too brutally" into the section below. Same rule between two adjacent full-bleed images — cross-fade or share the treatment, never butt them edge-to-edge. **The footer boundary is the one most often missed**: a full-bleed image whose bottom is a crisp horizontal edge dropped onto a flat footer band — especially a grey one a shade off the page — is the same tell at the end of the scroll. Grade the image into the footer's *own* colour (a mask or scrim resolving to the footer surface), and a clean near-white footer the image dissolves into beats an accidental grey step. Verify the seam in the browser at the boundary, not just section centers, and the last seam into the footer as deliberately as the first out of the hero (`preflight.md` §8).

## Filter wiring

Two checks feed the stop-and-fix filter, carried as axiomatic rejections in `anti-patterns.md`:

- **Hero carries a real visual** — fails on a text-over-gradient hero with no visual decision; the deliberate-typographic-hero path is the override.
- **No fake-div screenshots** — fails on any div-built simulated UI; an honest labeled placeholder passes.
