# Detector — the measured half of the browser proof

`assets/detector.js` turns the worst documented review failure into a number: a `:hover` rule read in the CSS and credited as "alive" while a human experienced the page as dead. The detector probes every state rule against the live DOM, measures the computed delta per channel, and holds it to perceptibility floors — so "the substrate responds" is evidence, not a code-read.

**Doctrine: the detector catches, it never clears.** A clean report proves the absence of the measured failures and nothing else — composition, desire, fidelity, copy, pacing, and seams stay judgment. Never cite a clean run as a quality claim.

## Measured vs judged

| Tier | Owner | Scope |
|---|---|---|
| 1 — measured | `awardDetector.run()` | state-rule deltas vs floors, font resolution, contrast on solid grounds, nav border ink, token conformance, h1 wrap, ambient animations at rest, broken images, horizontal overflow, tap targets |
| 2 — driven | you + the browser tooling | real hovers on every UNMEASURED-JS selector, then `awardDetector.measure(sel)`; scroll-up persistence; reduced-motion rerun |
| judged | you, preflight §8 | composition, desire, fidelity, copy, pacing, seams — never delegated to the detector |

## Injection — per browser rung

- **Chrome DevTools MCP** — one `evaluate_script` call whose function body is the full `detector.js` source followed by `return await awardDetector.run({ face: '<committed display face>', archetype: '<archetype>' })`. The file attaches `window.awardDetector`, so later calls (`measure`, reruns) are one-line evaluations.
- **dev-browser** — same two steps through its page-eval: evaluate the file source once, then evaluate `await window.awardDetector.run({ face, archetype })` and read the JSON.
- **No rung** — the detector never runs. Every box it feeds converts to a declared gap in the verdict (preflight §8), never to a tick.

## Floors

`FLOORS` in `detector.js` is the single source of truth; this table mirrors it. A channel at or above its floor is perceptible; every channel under → HOMEOPATHIC.

| Channel | Floor | Under it |
|---|---|---|
| scale | 1.04 | a 1.02 "zoom" reads as no move |
| ΔL (OKLab) | 0.04 | a barely-there tint reads as no tint |
| translate | 2px | a sub-2px shift never registers |
| opacity | 0.1 | a 5% fade is invisible |

Box-shadow, clip-path, underline, outline, background sweep, filter, and pseudo-element appearance have no floor — any change counts as perceptible.

## Rules

| Rule | Severity | Fires when |
|---|---|---|
| FONT-RESOLVE | FAIL | the committed face fails the width probe (`fonts.check` reports true for undeclared families, so metrics are the test), or a display element's first computed family is a system/generic or a never-rendering name — the silent-fallback bug |
| SUBSTRATE-DEAD | FAIL | among measured interactive elements, zero classify OK, or DEAD + HOMEOPATHIC exceed half — the page-wide dead pattern |
| DEAD | REVIEW | per element: pointer affordance, no state rule, zero delta, no JS to drive it |
| HOMEOPATHIC | REVIEW | per element: state rules fire but every channel lands under the floors — imperceptible, not restrained |
| UNMEASURED-JS | REVIEW | affordance with zero CSS delta on a scripted page — possibly JS-driven; queued for tier 2 |
| CONTRAST | FAIL | WCAG ratio under 4.5:1 (3:1 at ≥24px, or bold ≥18.66px) against the composited solid ground |
| UNCOMPUTABLE-BG | REVIEW | text over an image / gradient / media ground — never OK, never FAIL; judge it in §8 |
| NAV-BORDER | FAIL | a bar's border-bottom draws a contrasting line (ΔL > 0.05 against its own surface) |
| NAV-BORDER-HAIRLINE | REVIEW | ΔL ≤ 0.05 — same-ink hairline, allowed only as a written override citing the archetype palette row |
| TOKEN-CONFORM | REVIEW | a computed color/background resolves to no `--*` token value (skipped when the page declares no color tokens) |
| H1-LINES | FAIL | an h1 wraps past 2 line boxes at the current viewport |
| IDLE-CHANNEL | REVIEW | zero animations running at rest — a running animation proves presence, not perceptibility; skipped entirely under `prefers-reduced-motion: reduce` |
| IMG-BROKEN | FAIL | an image completed loading with zero natural width |
| H-OVERFLOW | FAIL | `scrollWidth` exceeds the viewport — horizontal scroll |
| TAP-TARGET | REVIEW | an interactive element under 24×24 CSS px at the current viewport (44×44 is the target) |

## Tier 2 — drive what CSS cannot show

Every selector in `substrate.selectors.unmeasuredJs` is driven with a **real** hover through the tooling (never a synthetic event), bracketed by `measure`: call `awardDetector.measure(sel)` once at rest (stores the snapshot), drive the hover and hold it past the declared transition duration (~400ms covers most), then call it again to get the classified delta; a mid-transition read measures zero. Write the result into the verdict as `UNMEASURED: n → driven: m`. When m < n on any element the design_plan names — the signature, the substrate classes, the nav — that preflight box is **NOT DONE**, never a declared gap: the tooling was present and the work was skipped.

## Reruns

- **Per width** — rerun at 375, 768, and 1440: resize, re-inject, `run()` again. H1-LINES, TAP-TARGET, H-OVERFLOW, and CONTRAST are width-dependent; one desktop pass proves nothing about mobile.
- **Scroll-up persistence** — scroll a content section past, scroll back, then `measure` its content elements' opacity against the rest snapshot taken before the scroll: content that re-hides on scroll-up is the motion-model FAIL (content persists, décor reverses — `motion-palette.md`). Verified in tier 2; the detector cannot scroll for you.
- **Reduced-motion** — emulate `prefers-reduced-motion: reduce` and rerun. IDLE-CHANNEL is exempt by design: `run()` skips it there because a silent page under reduce is the guard working, not a failure.

## Reading the report

`findings` carry `{ id, severity, box, selector, evidence }`; the box names the preflight line each finding feeds. `substrate` counts probed / ok / dead / homeopathic / unmeasuredJs with capped selector lists per class. `coverage.opaqueSheets > 0` means cross-origin stylesheets could not be probed — say so in the verdict; that coverage hole is never silent. Severity is binary. **FAIL is fix-only** — the fatal five are SUBSTRATE-DEAD, FONT-RESOLVE, NAV-BORDER (the contrasting line), CONTRAST, and content re-hide verified in tier 2. **REVIEW is judged and recorded**, never auto-cleared and never auto-failed. The report footer restates the doctrine; carry it into the verdict: the detector catches, it never clears.
