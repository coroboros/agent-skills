# Optical Craft — the last 10%

What separates 7.5 from 8+ once the universe, layout, and motion are right: decisions measured in optical units, not tokens. Model defaults are geometrically correct and optically wrong — none of this gets applied unless it is applied deliberately. Load at Phase 4; build with it, never retrofit it.

## Type optics

- **The scale ratio is an archetype decision, stated once.** Reading-led archetypes (Editorial, Corporate Luxury, Minimalist) build the ramp on a minor third (1.2) to perfect fourth (1.333) — headlines stay related to body. Display-led archetypes (Brutalist, Bold/Maximal, Immersive) jump a perfect fifth (1.5) or wider — headlines become objects. One ratio drives the whole ramp; record it in the DESIGN.md typography section.
- **Tracking is a curve, not a value.** Tighten as size grows: display ≥64px → `-0.03em` to `-0.045em` · headings 24–48px → `-0.01em` to `-0.02em` · body → `0` · uppercase labels and small caps → `+0.05em` to `+0.12em`. A single tracking value across sizes is the tell that no optical pass happened.
- **`text-wrap: balance` on every headline; `text-wrap: pretty` on body.** Kills widows and lonely last words mechanically — the single cheapest line of typographic polish on the platform.
- **Numbers that hold still.** `font-variant-numeric: tabular-nums` on stats, prices, counters, tables — proportional figures jitter when values change and never align in columns. Oldstyle figures for editorial running text where the face offers them.
- **`font-optical-sizing: auto`** whenever the variable font carries an `opsz` axis — display cuts at display sizes, text cuts at text sizes, one file.
- **`text-box-trim`** (leading-trim) aligns cap height to the container edge instead of the line box — check current support via the external-truth gate before leaning on it; ship it as progressive enhancement.
- Italic descender clearance is catalogued in `anti-patterns.md` — this pass is where it actually gets applied, word by word.
- **All-caps display floors at `line-height: 1.0`** — below it, cap-height collides with the line above at the first long word. Tight is the look; collision is a bug.

## Spatial optics

- **Optical centering beats geometric centering.** A glyph or icon geometrically centered in a button sits visually low — nudge up 1–2px. A play triangle centers on its visual mass — nudge right. Trust the screenshot, not the math.
- **Circles next to squares run ~2% larger**, or they read smaller at equal bounding box. Same for diamonds and acute shapes.
- **Headings belong to what follows.** `margin-top` ≥ 2× `margin-bottom` on section headings — a heading floating equidistant between two blocks orphans itself and flattens the rhythm.
- **A divider is punctuation, not a section.** A rule, ruler, or ornament sits inside the section rhythm — at most one `--space-xl` of air on each side, and never overlapping content at any width. A divider floating in more than twice its own visual height of emptiness reads as a missing section, not as whitespace.
- **Diagram labels are type, not texture.** Dimension callouts and figure annotations hold ≥10px equivalent at AA contrast — a drawing whose numbers can't be read is a texture pretending to be a figure.
- **Borders take the surface's temperature.** On light: `rgb(0 0 0 / 0.06–0.10)`; on dark: `rgb(255 255 255 / 0.08–0.14)`; both nudged toward the surface hue (`oklch(from var(--surface) …)`). The same foreign gray on both sides of a theme is the mismatch tell.
- **Shadows are colored.** Tint every shadow with the surface hue at low alpha — pure-black shadows on a warm page read as stickers. Elevation reads as light, and light has a temperature.
- **Cross-card alignment.** In any card row, CTAs pin to the card bottom and equivalent content starts at the same Y across columns — drifting baselines read as broken, not organic.

## Interaction personality — states express the universe

The 8-state contract (ship-ready floor) guarantees states exist; this table gives them character. A generic `opacity: 0.8` hover is a resting-state page wearing a costume. The table summarizes the archetype references — pick the row, tune within its band per the archetype file, bind values to `motion.*` tokens.

| Archetype | Hover feel | Timing | Displacement |
|---|---|---|---|
| Minimalist | breath — weight or opacity shift | 150–200ms, ease-out | card scale 1.02–1.05; otherwise none |
| Brutalist | snap — instant invert or color swap | 0–80ms state snaps (glitch bursts may run ~200ms) | hard 2–4px jumps |
| Editorial | ink — underline reveal, italic lean | 200–300ms, ease | baseline-anchored |
| Bold / Maximal | bounce — spring overshoot | spring `stiffness: 300, damping: 15` | playful 4–8px |
| Immersive / Cinematic | drift — parallax pull, glow bloom | 300–500ms, `expo.out` | z-depth, never bare x/y |
| Experimental | bespoke — its own physics, consistent with the metaphor | derived from the world | derived from the world |
| Corporate Luxury | glide — slow, weighted | 400–800ms, `cubic-bezier(0.16, 1, 0.3, 1)` | scale ceiling 1.05 |
| Bento / Card | lift — shadow deepens, card rises | 200–250ms, ease-out | 2px rise, shadow +1 step |
| Spatial Organic | morph — radius or blob shift | 300–400ms, spring | shape, not position |

## The quiet layer — second-read details, pick ≥2

The signature is the loud moment; these are what a judge notices on the return visit. Ship at least two, in the universe's palette and copy register:

- `::selection` styled — accent background, surface text
- the `:focus-visible` ring designed in the accent (the floor requires it exists; making it beautiful is the detail)
- favicon and `theme-color` drawn from the palette (the favicon is the real brand mark, not a hand-doodled inline glyph or a colored dot), never a default blue (the floor ships them; drawing them from the universe is the detail)
- `<title>` written as microcopy in the copy register, never "Home | Brand"
- an OG image designed inside the universe, not a screenshot (the floor ships one; designing it is the detail)
- `alt` text written in voice — accurate first, alive second
- a 404 page in the same universe
- form placeholder microcopy in voice
- scrollbar styled only where the archetype earns it (Brutalist, Experimental)
- print / reader-mode holding up (Editorial)

## Cross-references

`foundations.md` (type ramps, OKLCH derivation, spring registers) · `premium-patterns.md` (component architecture the optics polish) · `anti-patterns.md` (the failures these rules pre-empt) · `preflight.md` (the quiet-layer and font-resolution boxes).
