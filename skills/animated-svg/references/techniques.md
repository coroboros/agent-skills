# Animation techniques — SMIL + CSS-in-SVG

Durable techniques only. SMIL animation and CSS animations are frozen, universally shipped specs — everything here is stable knowledge. For property-level depth, consult the living sources rather than a copy that ages: [MDN SVG animation with SMIL](https://developer.mozilla.org/en-US/docs/Web/SVG/Guides/SVG_animation_with_SMIL), [MDN CSS animations](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_animations), [SVG 1.1 §19 Animation](https://www.w3.org/TR/SVG11/animate.html).

## Contents

- [SMIL or CSS — choosing](#smil-or-css--choosing)
- [Draw-on (line drawing)](#draw-on-line-drawing)
- [Mask reveal — draw-on for filled artwork](#mask-reveal--draw-on-for-filled-artwork)
- [Transforms — the origin gotcha](#transforms--the-origin-gotcha)
- [Easing](#easing)
- [Choreography — stagger and sequence](#choreography--stagger-and-sequence)
- [Seamless loops](#seamless-loops)
- [Path morphing](#path-morphing)
- [Gradient motion — shimmer](#gradient-motion--shimmer)
- [Motion along a path](#motion-along-a-path)
- [Reduced motion](#reduced-motion)
- [Dark / light adaptation](#dark--light-adaptation)
- [Size discipline](#size-discipline)

## SMIL or CSS — choosing

Both run in `<img>` context. Mix freely — pick per property, not per file.

| Need | Use | Why |
|------|-----|-----|
| Animate `d`, `points`, gradient stops, any XML attribute | SMIL `<animate>` | CSS cannot reach most presentation attributes |
| Motion along a path | SMIL `<animateMotion>` | No CSS equivalent inside a standalone SVG file |
| Sequencing (`begin="a.end"`) | SMIL | Declarative chaining; CSS needs delay math |
| transform/opacity loops, keyframed multi-property choreography | CSS `@keyframes` | Terser, media-gateable (`prefers-reduced-motion`) |
| Anything that must respect reduced-motion | CSS | SMIL ignores media queries |

## Draw-on (line drawing)

The classic "the shape draws itself". Normalize with `pathLength` so the dash math never depends on real path length:

```xml
<path d="…" pathLength="100" stroke-dasharray="100" stroke-dashoffset="100"
      fill="none" stroke="currentColor" stroke-width="4">
  <animate attributeName="stroke-dashoffset" from="100" to="0"
           dur="1.6s" fill="freeze" calcMode="spline"
           keyTimes="0;1" keySplines="0.4 0 0.2 1"/>
</path>
```

`stroke-dashoffset="100"` hides the stroke entirely; animating to `0` reveals it tip-to-tail. Reverse (`to="200"`) draws from the other end. `fill="freeze"` holds the final state.

## Mask reveal — draw-on for filled artwork

Strokes cannot taper. To "draw" filled or calligraphic shapes (a logo body that thins into a tail), reveal the filled artwork through a fat stroked path that follows its centerline:

```xml
<defs>
  <mask id="reveal">
    <path d="…centerline…" pathLength="100" fill="none" stroke="#fff"
          stroke-width="60" stroke-linecap="round"
          stroke-dasharray="100" stroke-dashoffset="100">
      <animate attributeName="stroke-dashoffset" from="100" to="0"
               dur="2s" fill="freeze"/>
    </path>
  </mask>
</defs>
<g mask="url(#reveal)"><path d="…filled artwork…" fill="#c6a15b"/></g>
```

The mask stroke must be wide enough to cover the artwork's fattest cross-section. This is the technique for animating real logos — the artwork keeps its exact silhouette.

## Transforms — the origin gotcha

The #1 field failure: a rotation/scale that flies off-screen. SVG transforms default their origin to the **viewport origin (0,0)**, not the element's center.

- **CSS fix** — always pair the two properties:

  ```css
  .spin { transform-box: fill-box; transform-origin: center; animation: spin 4s linear infinite; }
  @keyframes spin { to { transform: rotate(360deg); } }
  ```

- **SMIL fix** — pass the center explicitly in the values:

  ```xml
  <animateTransform attributeName="transform" type="rotate"
                    from="0 330 330" to="360 330 330" dur="4s" repeatCount="indefinite"/>
  ```

  (`330 330` = the rotation center in viewBox coordinates.)

## Easing

Linear easing reads as mechanical; eased motion reads as designed. Standard curves:

| Feel | CSS | SMIL (`calcMode="spline"` + `keySplines`) |
|------|-----|-------------------------------------------|
| standard / settle | `cubic-bezier(0.4, 0, 0.2, 1)` | `0.4 0 0.2 1` |
| decelerate (enter) | `cubic-bezier(0, 0, 0.2, 1)` | `0 0 0.2 1` |
| accelerate (exit) | `cubic-bezier(0.4, 0, 1, 1)` | `0.4 0 1 1` |
| overshoot | `cubic-bezier(0.34, 1.56, 0.64, 1)` | *(SMIL splines cannot overshoot — add an extra keyframe past the target instead)* |

SMIL needs `keyTimes` with one entry per value and one spline per segment: `keyTimes="0;1" keySplines="0.4 0 0.2 1"`.

## Choreography — stagger and sequence

- **SMIL offsets**: `begin="0.3s"`, `begin="0.3s; loop.end+0.3s"` for repeat scheduling.
- **SMIL chaining**: give an animation `id="draw"`, start the next with `begin="draw.end"` — declarative sequencing, survives duration edits.
- **CSS stagger**: `animation-delay: .3s` per element; **negative delays** (`animation-delay: -1s`) phase-shift copies of the same loop — the idiom for wave effects across repeated elements.
- Stagger sibling entrances 60–120 ms apart; simultaneous entrances read as a blink, long gaps read as lag.

## Seamless loops

A loop is seamless when the rendered frame at `t = duration` is identical to `t = 0`.

- SMIL: make the last entry in `values` equal the first — `values="0; -6; 0"` — with `repeatCount="indefinite"`.
- CSS: `100%` keyframe = `0%` keyframe (or animate a symmetric property with `animation-direction: alternate`).
- Verify it: capture frames at `t=0` and `t=duration` — they must be pixel-identical (see SKILL.md verification loop).
- Multiple loops of different durations only resolve in-phase at their durations' least common multiple — either align durations or accept the drift deliberately.

## Path morphing

SMIL animates `d` directly, but **only between paths with the same command sequence** (same commands, same order, same point count):

```xml
<path d="M10 80 Q 95 10 180 80">
  <animate attributeName="d" dur="1.2s" repeatCount="indefinite"
           values="M10 80 Q 95 10 180 80;
                   M10 80 Q 95 150 180 80;
                   M10 80 Q 95 10 180 80"/>
</path>
```

Author both endpoint shapes with identical structure from the start — retrofitting structure onto mismatched paths is the painful path. Prefer SMIL over CSS `d:` animation here (CSS path interpolation support is uneven; SMIL is not).

## Gradient motion — shimmer

Gradients are animatable XML like everything else. A light sweep across a gold shape:

```xml
<linearGradient id="sheen" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0"   stop-color="#c6a15b"/>
  <stop offset="0.5" stop-color="#e8cf9a">
    <animate attributeName="offset" values="0.1;0.9;0.1" dur="5s" repeatCount="indefinite"/>
  </stop>
  <stop offset="1"   stop-color="#c6a15b"/>
</linearGradient>
```

Also animatable: `gradientTransform` (rotate a sweep), `stop-color`, `stop-opacity`. Subtle beats loud — a shimmer is a second-read detail, not the signature.

## Motion along a path

```xml
<circle r="4" fill="#c6a15b">
  <animateMotion dur="6s" repeatCount="indefinite" rotate="auto"
                 path="M …same d as the track…"/>
</circle>
```

`rotate="auto"` orients the element along the tangent — particles, comets, orbiting accents. `<mpath href="#track"/>` reuses an existing path instead of duplicating `d`.

## Reduced motion

CSS animations gate cleanly; SMIL cannot be media-gated (it ignores CSS media queries):

```css
@media (prefers-reduced-motion: reduce) {
  * { animation-duration: 0.01s !important; animation-iteration-count: 1 !important; }
}
```

Doctrine: put large or sustained motion in CSS so the gate works; keep any SMIL that remains gentle — no flashing, no large translations, nothing vestibular. If the piece is *only* large motion, ship the CSS variant.

## Dark / light adaptation

Two mechanisms, both README-safe:

1. **In-SVG media query** — one file adapts by itself (works in `<img>` because the media query evaluates in the viewer's browser):

   ```css
   :root { --ink: #1a1a1a; }
   @media (prefers-color-scheme: dark) { :root { --ink: #e8e2d5; } }
   ```

   Reference `var(--ink)` from `fill`/`stroke` via CSS rules (presentation attributes cannot read variables — style the elements with CSS selectors).

2. **`<picture>` pair** — two files, GitHub's documented mechanism:

   ```html
   <picture>
     <source media="(prefers-color-scheme: dark)" srcset="logo-dark.svg">
     <img src="logo-light.svg" alt="Project" width="280">
   </picture>
   ```

Prefer 1 for a single self-adapting asset; use 2 when the two modes need genuinely different artwork. Caveat for both: `prefers-color-scheme` tracks the OS/browser preference, not GitHub's theme picker — a user forcing dark GitHub on a light OS gets the light artwork. Favor palettes that read on both backgrounds; verify with a dark-background frame pass.

## Size discipline

- Hand-authored paths, coordinates rounded to ≤1 decimal in a sensibly sized viewBox.
- Reuse geometry with `<use href="#id">` and share `<defs>` — never duplicate paths.
- Machine exports (Lottie-to-SVG, autotrace) run 100–600 KB for what hand authoring does in 3–15 KB. Bloat is a smell that the source wasn't authored for animation.
- If a minifier runs on the file afterwards, confirm it preserves `<style>`, `id` attributes, and animation elements — default SVGO-style configs strip what the animation depends on. Diff before/after and re-run the verification loop.
