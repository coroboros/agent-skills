# Detector — the measured half of the browser proof

`assets/detector.js` turns the worst documented review failure into a number: a `:hover` rule read in the CSS and credited as "alive" while a human experienced the page as dead. The detector probes every state rule against the live DOM, measures the computed delta per channel, and holds it to perceptibility floors — so "the substrate responds" is evidence, not a code-read.

**Doctrine: the detector catches, it never clears.** A clean report proves the absence of the measured failures and nothing else — composition, desire, fidelity, copy, pacing, and seams stay judgment. Never cite a clean run as a quality claim.

## Measured vs judged

| Tier | Owner | Scope |
|---|---|---|
| 1 — measured | `awardDetector.run()` | state-rule deltas vs floors, font resolution, contrast on solid grounds, nav border ink, token conformance, h1 wrap, ambient animations at rest, broken images, horizontal overflow, tap targets, per-section void |
| 2 — driven | you + the browser tooling | real hovers on every UNMEASURED-JS selector, then `awardDetector.measure(sel)`; contact presses via `measureContact`; the open-drawer recount; scroll-up persistence; reduced-motion rerun; taps under touch emulation |
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

The substrate probe measures the **pointer (`:hover`) response only**. `:focus-visible` rules are excluded: the universal focus ring (`:focus-visible { outline }`, which every accessible build carries) would otherwise paint its outline onto every focusable element under the probe and score it alive on that structural change alone — a scale-only "designer shrink" hover reads OK because the ring, not the hover, moved. A purely focus-driven element therefore reads UNMEASURED-JS (drive it in tier 2), never a free OK from the ring. The keyboard focus affordance is a separate concern, checked by the `:focus-visible` scanner/preflight boxes, not the substrate-dead gate.

## Rules

| Rule | Severity | Fires when |
|---|---|---|
| FONT-RESOLVE | FAIL | the committed face fails the width probe (`fonts.check` reports true for undeclared families, so metrics are the test), or a display element's first computed family is a system/generic or a never-rendering name — the silent-fallback bug |
| SUBSTRATE-DEAD | FAIL | among measured interactive elements, zero classify OK, or DEAD + HOMEOPATHIC exceed half — the page-wide dead pattern |
| DEAD | REVIEW | per element: pointer affordance, no state rule, zero delta, no JS to drive it |
| HOMEOPATHIC | REVIEW | per element: state rules fire but every channel lands under the floors — imperceptible, not restrained |
| SECTION-DEAD | REVIEW | a tall top-level section (≥ 1.4 viewports) whose largest empty rectangle swallows > 45% of it — sparse text stranded in a corner over a void, the "empty and dead" beat a code-read never sees |
| UNMEASURED-JS | REVIEW | affordance with zero CSS delta on a scripted page — possibly JS-driven; queued for tier 2 |
| CONTACT-GLOBAL-SQUASH | FAIL | tier 2 only, via `measureContact`: the struck object's peak response is a whole-element scale/opacity and nothing else — no secondary above a floor, no structural channel — the paper-cutout squash; `run()` never fires it |
| CONTRAST | FAIL | WCAG ratio under 4.5:1 (3:1 at ≥24px, or bold ≥18.66px) against the composited solid ground |
| UNCOMPUTABLE-BG | REVIEW | text over an image / gradient / media ground — never OK, never FAIL; judge it in §8 |
| NAV-BORDER | FAIL | a bar's border-bottom draws a contrasting line (ΔL > 0.05 against its own surface) |
| NAV-BORDER-HAIRLINE | REVIEW | ΔL ≤ 0.05 — same-ink hairline, allowed only as a written override citing the archetype palette row |
| NAV-HERO-OPAQUE | FAIL | at rest (scrollY 0), a top bar over hero media paints an opaque (α ≥ 0.9), unblurred surface off the page ground — the decapitation band; transparent, scrim, or frost-with-blur over the hero is the winner norm |
| NAV-HERO-SURFACE | REVIEW | any other owned surface over hero media at rest (frost + blur, translucent, or opaque same-ground) — judged in §8 against the archetype canon, never auto-cleared |
| TOKEN-CONFORM | REVIEW | a computed color/background resolves to no `--*` token value (skipped when the page declares no color tokens) |
| H1-LINES | FAIL | an h1 wraps past 2 line boxes at the current viewport |
| IDLE-CHANNEL | REVIEW | zero animations running at rest — a running animation proves presence, not perceptibility; skipped entirely under `prefers-reduced-motion: reduce` |
| IMG-BROKEN | FAIL | an image completed loading with zero natural width |
| H-OVERFLOW | FAIL | `scrollWidth` exceeds the viewport — horizontal scroll |
| TAP-TARGET | REVIEW | an interactive element under 24×24 CSS px at the current viewport (44×44 is the target) |

## Tier 2 — drive what CSS cannot show

Every selector in `substrate.selectors.unmeasuredJs` is driven with a **real** hover through the tooling (never a synthetic event), bracketed by `measure`: call `awardDetector.measure(sel)` once at rest (stores the snapshot), drive the hover and hold it past the declared transition duration (~400ms covers most), then call it again to get the classified delta; a mid-transition read measures zero. Write the result into the verdict as `UNMEASURED: n → driven: m`. When m < n on any element the design_plan names — the signature, the substrate classes, the nav — that preflight box is **NOT DONE**, never a declared gap: the tooling was present and the work was skipped.

**Peak-hold — transients that settle before a read.** A click/press response on a spring (~140ms) is back at rest before any post-drive call lands, so a single `measure` read reports zero. `measurePeak(sel, windowMs)` shares the two-call protocol: the first call stores the rest snapshot; drive the transient; the second call samples every frame for `windowMs` (default 600ms) and returns the max per-channel delta — the crest, not the residue.

**Contact presses.** For every design_plan-named struck object: `measureContact(sel, { secondaries: ['<selector>', …] })` at rest stores snapshots of the object and each declared secondary and arms the peak sampler on the object's next `pointerdown`; drive a **real** click/press; call `measureContact(sel)` again to read the peak-held channels and the classification. Because the sampler starts on the press itself, tool-call latency between the click and the read never loses the transient. `GLOBAL-SQUASH` returns a ready CONTACT-GLOBAL-SQUASH finding — carry it into the verdict: the only above-floor response is a whole-element scale/opacity on the object, the paper-cutout. `LOCAL` means something beyond the squash responded (a secondary, a structural channel, a translate/color on the object) — its quality stays judgment. `CANVAS` means the object is a canvas medium: pixels are invisible to computed style, so the deformation stays judgment — drive the press and watch.

**Open-drawer recount.** A closed drawer or overlay is invisible to `isRendered`, so a rest-state `run()` never censuses its links — by design. Drive the overlay open, then re-run `run()` (or `measure` each link) with it rendered: the drawer links join the substrate census and the `UNMEASURED: n → driven: m` accounting. A rest-state pass alone under-counts the nav.

## Reruns

- **Per width** — rerun across the render-floor sweep (`assets/render-floor.js`), 375, 768, 1024, 1440, and 1920: resize, re-inject, `run()` again. H1-LINES, TAP-TARGET, H-OVERFLOW, and CONTRAST are width-dependent; one desktop pass proves nothing about mobile.
- **Scroll-up persistence** — scroll a content section past, scroll back, then `measure` its content elements' opacity against the rest snapshot taken before the scroll: content that re-hides on scroll-up is the motion-model FAIL (content persists, décor reverses — `motion-palette.md`). Verified in tier 2; the detector cannot scroll for you.
- **Reduced-motion** — emulate `prefers-reduced-motion: reduce` and rerun. IDLE-CHANNEL is exempt by design: `run()` skips it there because a silent page under reduce is the guard working, not a failure.
- **Touch emulation** — under `(hover: none)` the hover probes are void: a correctly touch-gated build hides its `:hover` rules behind `@media (hover: hover)` and would read dead. `run()` skips the substrate probe there and reports `substrate: { skipped: … }`; SUBSTRATE-DEAD never fires on that pass. The touch channel is judged by driving real taps (tier 2), never by `run()`.

## Reading the report

`findings` carry `{ id, severity, box, selector, evidence }`; the box names the preflight line each finding feeds. `substrate` counts probed / ok / dead / homeopathic / unmeasuredJs with capped selector lists per class — or `{ skipped }` under touch emulation. `coverage.opaqueSheets > 0` means cross-origin stylesheets could not be probed — say so in the verdict; that coverage hole is never silent. Severity is binary. **FAIL is fix-only** — the fatal nine are FONT-RESOLVE, SUBSTRATE-DEAD, CONTRAST, NAV-BORDER (the contrasting line), NAV-HERO-OPAQUE (the decapitation band), H1-LINES, IMG-BROKEN, H-OVERFLOW, and CONTACT-GLOBAL-SQUASH (tier 2 only, via `measureContact`). Content re-hide on scroll-up is fix-only too and is not among them — no detector rule fires it, tier 2 verifies it (`motion-palette.md`). **REVIEW is judged and recorded**, never auto-cleared and never auto-failed. The report footer restates the doctrine; carry it into the verdict: the detector catches, it never clears.
