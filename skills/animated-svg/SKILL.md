---
name: animated-svg
description: Author high-end self-contained animated SVGs — SMIL + CSS-in-SVG, zero JavaScript — that stay animated where scripts never run, GitHub READMEs and profiles first (SVG-as-image never executes scripts), plus package-registry pages, docs sites, and inline web use. Redraws artwork as semantic paths, choreographs the motion (draw-on, morph, shimmer, orbit), then proves it with a deterministic frame-capture verification loop. Use whenever the user wants a logo, banner, hero, loader, badge, or diagram that moves — even if they just say "animate our logo", "make the README pop", or hand over a PNG to bring to life.
when_to_use: When the user wants an animated SVG or animated vector asset — logo, README banner, hero, loader, spinner, icon, diagram — or motion that must survive GitHub README/registry embedding where JavaScript never runs. Keywords — animated svg, SMIL, animate logo, README banner, draw-on, seamless loop, morph, shimmer. Skip for video assets (/video-loop), full frontend builds (/award-design), GIF exports, and Lottie/dotLottie players (JS runtimes — out of scope by design).
argument-hint: "<what to animate> [-o <output.svg>] [-p readme|web]"
license: MIT
metadata:
  author: coroboros
---

# Animated SVG

<!-- canonical:adversarial-verification:start -->
## Critical — Adversarial verification

These rules govern how this skill trusts its own output — apply them whenever it verifies a claim, a defect, a source, or a decision before acting on it.

- Refute by default. Treat each non-trivial finding as unproven until a fresh-context check fails to refute it — the context that produced a claim cannot reliably clear it.
- No silent drop. Every finding flips the conclusion, is refuted in writing, or is filed as a risk or open question. A finding that vanishes without a verdict is a defect.
- Don't re-litigate settled facts. Spend adversarial effort on load-bearing or contested claims; let established facts pass. Over-refutation manufactures false doubt — it does not add rigor.
- Stay selective and cost-aware. Scale verification to the stakes; reversible, low-impact work gets a light touch, not a full adversarial sweep.
- Concede only to a strong rebuttal. A weak counter folds into the finding or gets filed; it does not overturn it.
<!-- canonical:adversarial-verification:end -->

<!-- canonical:execution-discipline:start -->
## Important — Engineering discipline

These rules govern how this skill changes code — apply them whenever it writes, edits, or proposes a fix.

- Minimal scope. Only what's directly requested or clearly necessary — no extra files, no abstraction for one use, no configurability nobody asked for, no error handling for states that can't happen. Validate at system boundaries; trust internal code.
- General solution, not the test cases. Implement the real logic for all valid inputs; never hard-code to inputs or bolt on workaround scripts to make a test pass. Tests verify the solution; they don't define it. A test is wrong? Say so — don't bend correct code to a broken test.
- Investigate before claiming. Never speculate about code you haven't opened; read the referenced file before answering. Ground every claim in what you actually read, not a plausible guess.
<!-- canonical:execution-discipline:end -->

Produce animated SVGs at the quality bar of the best open-source project heroes: hand-authored semantic paths, choreographed SMIL + CSS-in-SVG motion, a few KB, no runtime. The defining constraint and the reason this skill exists: in `<img>` context (every GitHub README, profile, and registry page) scripts never execute, external resources never load, and pointer events never fire — only self-contained SMIL and CSS animation survives. Anything built on a JS player (Lottie, GSAP, anime.js) is dead on arrival there; decline that route and build the pure-SVG equivalent instead.

## Parameters

| Flag | Default | Description |
|------|---------|-------------|
| `-o <path>` | asked or inferred from the brief | Output file |
| `-p readme\|web` | `readme` | Delivery profile — README/registry `<img>` context vs inline-on-page |

> **No `-s/-S` save-mode flag.** Like `/video-loop`, the output is a project asset the user places directly (`assets/`, `docs/`, `.github/`) — no downstream skill consumes it via `-f`.

Profile `readme` is the strict default: self-containment violations are errors. Profile `web` relaxes external references and allows interactivity (`:hover`, class toggles) because the SVG is inlined into a page the user controls. When the destination is unclear, ask — the profiles produce different constraints, not just different warnings.

## 1 — Design the motion before touching markup

Motion is designed, not sprinkled. Commit to a plan first:

- **One signature motion** (the draw-on, the morph, the orbit) plus at most one quiet second-read detail (a shimmer, a blink). Scattered micro-movement reads as noise.
- **Physical easing** — entrances decelerate, exits accelerate, nothing linear except constant spins. Curves and their SMIL/CSS forms: `references/techniques.md` § Easing.
- **README assets whisper.** A loop that lives next to prose runs 2–8 s per cycle at small amplitude. It must reward a glance, not hijack reading.
- **Seamless by construction** — last keyframe equals first; the verification loop proves it at the pixel level.

## 2 — Author semantic paths

Animation quality is decided by the geometry it runs on.

- Every animatable unit is its own path or group with a stable `id` — a body, an eye, a letterform. Name them for what they are.
- **From a raster reference (logo PNG, screenshot): redraw, never autotrace.** Autotrace emits thousands of anonymous micro-paths that cannot animate meaningfully and weigh 50–100× more. Sample the palette from the source, rebuild the silhouette as clean paths, and check fidelity against the reference in the verification loop.
- Text becomes paths for the `readme` profile — custom fonts never load in `<img>` context.
- Techniques — draw-on (`pathLength` trick), mask reveal for filled/tapered artwork, transform-origin gotcha, morphing constraints, gradient shimmer, motion-along-path, stagger/sequencing, dark-mode patterns, size discipline: read `references/techniques.md` before authoring; it is the difference between textbook motion and field-failure motion.
- Accessibility floor: `<title>` on the root, `viewBox` always, respect reduced motion (`references/techniques.md` § Reduced motion — CSS gates cleanly, SMIL cannot be gated, so keep SMIL amplitude modest).

## 3 — Verify: claimed = shown

An animation you have not rendered is a claim, not a deliverable. `$SKILL_DIR` = this skill's folder — `${CLAUDE_SKILL_DIR}` in Claude Code, the directory containing this SKILL.md elsewhere.

1. **Static gate** — deterministic checks (well-formed, viewBox, animation present, no script/handlers, self-contained, fonts, reduced-motion, interactivity, `<title>`, size budget):

   ```bash
   python3 "$SKILL_DIR"/scripts/check_svg.py out.svg -p readme
   ```

   Exit 1 = fix the `status=fail` lines before proceeding. Treat `status=warn` as review items, not noise.

2. **Frame captures** — freeze the animation at chosen instants and render stills:

   ```bash
   python3 "$SKILL_DIR"/scripts/frame_harness.py out.svg -t 0,0.8,1.6,2.4 -o "$(mktemp -d)"
   ```

   Frames are verification scratch — keep them in a temp dir, never in the working tree.

   Always include `0` and exactly the loop duration — those two frames must match for a seamless loop. Add 2–3 midpoints where the choreography is busiest. Screenshot each generated page with whatever browser surface is available (dev-browser CLI, Chrome DevTools MCP, Playwright — any works; the pages are plain local HTML). No browser surface available → say so explicitly and fall back to a code-level read; never imply the frames were seen.

3. **Refute the stills** — read the screenshots and try to fail the work:
   - Midpoint frames differ from each other — the asset actually moves.
   - `t=0` and `t=duration` match — the loop is seamless.
   - Composition holds at every instant — nothing clips, collides, or collapses mid-flight.
   - Re-run one frame with `--bg "#0d1117"` — still legible on dark.
   - Redrawn from a raster: silhouette still reads as the original mark.

   Any failure → fix, re-run from step 1. Deliver only what survived.

## 4 — Deliver

Write the file where the user's project needs it and hand over the embed:

```html
<!-- README: plain, self-adapting SVG -->
<p align="center"><img src="assets/logo-animated.svg" width="280" alt="Project"></p>

<!-- README: distinct dark/light artwork -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/logo-dark.svg">
  <img src="assets/logo-light.svg" width="280" alt="Project">
</picture>
```

For the `web` profile, offer inline embedding when the page should style or trigger the SVG (class toggles, `currentColor`), `<img>` otherwise. If the user's pipeline minifies SVGs, warn: the minifier must preserve `<style>`, `id`s, and animation elements — then re-run the verification loop on the minified output.

## Rules

- NEVER ship JavaScript, event handlers, or external references in a `readme`-profile asset — check_svg.py enforces this; do not argue with it.
- NEVER autotrace a raster reference — redraw semantic paths.
- NEVER deliver without the frame-capture loop (or an explicit statement that no browser surface was available).
- NEVER convert to GIF/video as a workaround unless the user asks — it abandons resolution independence, dark-mode adaptation, and 10–100× the weight.
- Requests for hover/click behavior in a README → explain that pointer events never reach `<img>` content, then offer the autonomous-loop equivalent or the `web` profile.

## Gotchas

1. **Snap-back at the end** — SMIL defaults to removing the effect when an animation ends. Entrance animations need `fill="freeze"` or the artwork jumps back to its start state.
2. **Rotation flies off-screen** — SVG transform origin defaults to the viewport origin, not the element center. Fix per `references/techniques.md` § Transforms before debugging anything else.
3. **Composed transforms drift** — a parent group's animated transform multiplies with children's. Animate transform at one level per subtree, or budget the composition deliberately.
4. **ID collisions when inlining** (`web` profile) — two inlined SVGs sharing `id="glow"` silently cross-wire masks and gradients. Prefix every `id` with the asset name.
