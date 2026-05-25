# Atmosphere Calibration

After selecting an archetype, calibrate its atmosphere on three axes (1-10). This makes design choices measurable rather than intuitive, and prevents drift during implementation.

## Axes

| Axis | 1-3 | 4-6 | 7-10 |
|------|-----|-----|------|
| **Density** | Gallery airy — generous whitespace, few elements per viewport | Balanced — clear hierarchy with moderate content | Cockpit dense — information-rich, tight spacing |
| **Variance** | Predictable — symmetric grids, uniform spacing, expected flow | Structured surprise — asymmetric grids, varied rhythm | Artsy chaotic — broken grids, overlapping zones, rule-breaking |
| **Motion** | Static — minimal transitions, opacity-only reveals | Purposeful — scroll-triggered sequences, hover states | Cinematic — continuous animation, parallax depth, WebGL layers |

## Default scores per archetype

Adjust ±2 based on the brief.

| Archetype | Density | Variance | Motion |
|-----------|---------|----------|--------|
| Minimalist | 2 | 3 | 3 |
| Brutalist | 4 | 7 | 3 |
| Editorial | 5 | 5 | 4 |
| Bold / Maximal | 6 | 8 | 8 |
| Immersive / Cinematic | 3 | 6 | 9 |
| Experimental | 5 | 9 | 7 |
| Corporate Luxury | 2 | 4 | 5 |
| Bento / Card | 7 | 4 | 4 |
| Spatial Organic | 4 | 6 | 6 |

Use these to resolve design ambiguity: "More whitespace here?" → check Density. "Break the grid?" → check Variance. "Need scroll animation?" → check Motion. Record final calibrated scores in `DESIGN.md`.

## Dial → CSS heuristics

Concrete starting points per band; the archetype reference refines them.

- **Density 2-3** → `py-32` to `py-48` section padding (128-192px), 60-75ch reading measure, ample gutters. **Density 7-10** → `py-12` to `py-16` (48-64px), `gap-2` to `gap-4`, monospace numerics with `tabular-nums`.
- **Variance 1-3** → 12-column grid centered, `max-w-screen-xl mx-auto`, symmetric padding. **Variance 7-10** → broken-grid `grid-template-columns: repeat(11, 1fr)` with intentional `grid-row` overlap, off-axis hero, asymmetric image-text pairs.
- **Motion 1-3** → `transition: opacity 0.4s` only; avoid scroll-triggered. **Motion 7-10** → GSAP ScrollTrigger pin/scrub on hero, View Transitions on navigation, perpetual micro-interactions on signature elements (memoized per `premium-patterns.md` performance locks).
