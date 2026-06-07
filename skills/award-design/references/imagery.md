# Imagery

The largest single imposition most AI builds miss. Judges read empty visual zones as "unfinished" before they read anything else, so a page with no real images is a placeholder, not a design. This protocol is asset discipline: what to use, in what priority, and what never to fake.

Load during the build (Phase 3) and at the close (Phase 4 gate).

## Zero images is a bug

Even a minimalist build carries 2–3 real images. A hero that is a headline floating over a flat gradient with no visual decision is the canonical placeholder hero — not a minimalist one. The visual can be:

- Photography (real or generated), 3D / canvas, or a textured / illustrated surface.
- A *deliberate* typographic treatment that IS the visual — kinetic SplitText, oversized editorial display, type-as-image. Brutalist and Editorial heroes earn the floor on type alone when the type is the art.

What does not clear the floor: a centered headline over a purple/blue or beige gradient, stock-feeling hero slabs, or a single icon standing in for a hero image.

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

## Acquisition priority order

When the build needs an asset and none was supplied, walk the order — never skip ahead to inventing one:

1. **Generate it** — if an image-generation tool is available, produce a contextual asset (brief-matched subject, palette, crop).
2. **Seed a real source** — `https://picsum.photos/seed/{context}/{w}/{h}` with a contextual seed keyed to the section, so reruns stay stable and each slot differs. Use a deterministic seed, never `random`.
3. **Labeled placeholder + tell the user** — when neither is available, ship a placeholder sized to the final aspect ratio and emit an explicit asset list: what each slot needs, its dimensions, and where it lands. Never block the build; never fake it.

Stock photography is not on this list — it tanks scores (see `anti-patterns.md` *Design failures*). The protocol reaches for generated, seeded, or honest-placeholder assets, never a stock library.

## Gate wiring

Two checks feed the Phase 4 HARD gate, carried as axiomatic rejections in `anti-patterns.md`:

- **Hero carries a real visual** — fails on a text-over-gradient hero with no visual decision; the deliberate-typographic-hero path is the override.
- **No fake-div screenshots** — fails on any div-built simulated UI; an honest labeled placeholder passes.
