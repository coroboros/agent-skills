# Pre-Flight — the ship gate

Phase 5 of the protocol. Runs on the built site, before the fresh-context review (R2). Binary: every box ticks or the build is not done — fix, re-run, then proceed. No sampling, no compression, no "mostly". Where a rule offers an override, the override is written into the verdict and tied to the brief; an unstated override is a fail.

This file is the checklist; `anti-patterns.md` is the catalog behind it (rationale, fixes, full failure modes). When a box is unclear, read its catalog entry — never guess it away.

## 1. Mechanical scan (run first)

```bash
python3 scripts/preflight_scan.py <build-dir> --archetype <archetype>
```

(Path relative to this skill's root. `--archetype editorial|corporate-luxury` suppresses the em-dash rule where it is a legitimate typographic choice.)

- Every **FAIL** hit: fix it, or write a one-line justification tied to the brief into the verdict block.
- Every **REVIEW** hit: judge it against the catalog and record the call.
- The scanner **catches, it never clears** — a clean scan ticks no box below. It cannot see composition, hierarchy, or intent; the boxes and the R2 review carry that weight.

Boxes tagged with a scanner rule below have mechanical help; the scan count feeds the box, the box still needs the honest tick.

## 2. Axiomatic boxes

Catalog: `anti-patterns.md` *Axiomatic rejections* (numbered 1–14). One violation scores below Honorable Mention regardless of everything else.

- [ ] No AI-purple gradient anywhere `(scanner: AI-PURPLE)`
- [ ] No Inter / Roboto / Arial / system font as the display face `(scanner: DISPLAY-FONT)`
- [ ] No pure `#000` / `#FFF` `(scanner: PURE-BW)`
- [ ] No placeholder names, no fake round statistics `(scanner: PLACEHOLDER-NAME, FAKE-STAT)`
- [ ] No centered-hero-over-dark-image-with-generic-headline template
- [ ] No 3 equal cards as the feature section
- [ ] No emojis as UI icons `(scanner: EMOJI-UI)`
- [ ] Signature moment present — the loud one AND the quiet second-read detail
- [ ] Hero H1 lands in ≤3 lines at desktop (2 is the rule, 3 the ceiling)
- [ ] Zero `SECTION 01` / index meta-labels `(scanner: META-LABEL)`
- [ ] No generic avatars (SVG eggs, stock "diverse team")
- [ ] No startup-slop brand names (Acme, Nexus, SmartFlow)
- [ ] Hero carries a real visual (photography / generated / 3D / deliberate type-as-image)
- [ ] No fake-div product screenshots — real capture or honest labeled placeholder

## 3. Consistency locks (page-wide, binary)

- [ ] **Theme lock** — one theme for the whole page; no section flips light↔dark mid-scroll. Override: a single deliberate color-block device, declared in the DESIGN.md.
- [ ] **Accent lock** — one accent color, identical role everywhere, present once per viewport, never twice.
- [ ] **Shape lock** — one corner-radius system (all-sharp, all-soft, or a documented mixed rule applied everywhere). Round buttons in a square layout is a fail.
- [ ] **Emphasis lock** — in-headline emphasis uses italic or bold of the SAME family; no foreign-family word injected for visual interest.
- [ ] **Register lock** — one copy register per page (technical mono, editorial prose, or marketing punch — not a blend), unless the DESIGN.md declares the mix.

## 4. Countable boxes

Each is a number computed from the rendered page against a threshold. Cite the count in the verdict. Every row declares its scope — **Global** runs on every archetype; **Archetype-conditional** names its suppression. Overrides exist so no ban is a dead end, but an override is written into the verdict, tied to the brief.

| Box | Rule | Scope / Override |
|---|---|---|
| [ ] **Eyebrow density** | Eyebrow tags ≤ `ceil(sectionCount / 3)`; hero counts as one `(scanner: EYEBROW-DENSITY)` | Global — eyebrows punctuate, they don't label every section |
| [ ] **Bento fill** | N items render as exactly N cells — zero empty or filler cells | Global |
| [ ] **Zigzag cap** | ≤ 2 consecutive image-text split rows | Global — Override: a third is admissible only if it inverts composition, never a fourth |
| [ ] **Marquee cap** | ≤ 1 marquee / infinite ticker per page | Global — one signature ticker is fine; a logo wall *and* a testimonial ribbon is the tell |
| [ ] **Layout-family variety** | ≥ 4 distinct section layout families per 8 sections | Archetype-conditional — suppressed for single-fold portfolios and pure docs |
| [ ] **Hero-stack cap** | ≤ 4 stacked text elements (eyebrow OR brand strip · H1 · subtext ≤ 20 words · one CTA cluster); no trust-strip, logo wall, or pricing teaser inside the hero | Global — Override: a long editorial standfirst counts as one element — cap the stack, not the sentence |
| [ ] **CTA-intent consistency** | one label per intent across the page ("Get in touch" + "Let's talk" = same intent = fail) | Global — repeating the *same* label for the same intent is fine |
| [ ] **Em-dash density** | body-copy density ≤ ~1 per 100 words `(scanner: EMDASH)` | Archetype-conditional — suppressed for `editorial` and `corporate-luxury`, where the em-dash is a deliberate typographic choice |
| [ ] **Hero top padding** | ≤ 6rem (`pt-24`) at desktop | Global — needs more breathing room → scale the type or the asset, never the padding |
| [ ] **Nav discipline** | one line at ≥1024px, height ≤ 80px | Global — condense labels, drop secondary items, or go hamburger; a two-line desktop nav is broken |
| [ ] **CTA wrap** | every CTA label fits one line at desktop | Global — shorten the label (≤3 words for primary) or widen the button |
| [ ] **Quote length** | quote bodies ≤ 3 lines; attribution is name + role, never name alone | Global — footer-size testimonials may stretch slightly; the spirit is "fits in a glance" |
| [ ] **Middle-dot rationing** | `·` ≤ 1 per metadata line | Global — prefer line breaks, hairlines, or columns as the separator family |
| [ ] **Split-header** | zero "left big headline + right floating explainer" section headers — stack vertically | Global — Override: the right column carries a real visual or interactive element, never filler text |
| [ ] **Long-list component** | every list > 5 items uses a designed component (grouped chunks, card grid, tabs, scroll-snap, marquee) | Global — bare rows with a hairline under each is the fail |
| [ ] **Italic descenders** | every italic display word containing `y g j p q` has line-height ≥ 1.1 and bottom reserve | Global — clipped descenders are a rendering bug, not a style |

## 5. Craft floor

Catalog: `ship-ready-floor.md` (Impose tier) + `foundations.md` UX Quality and Accessibility.

- [ ] **8-state contract** — every interactive element ships its applicable states: default, hover, focus-visible, active, disabled, loading, empty/error, success. Async surfaces carry skeletons (matching final layout), empty, and error states.
- [ ] Custom `:focus-visible` on every interactive element; skip link present; no `outline: none` without a visible replacement `(scanner: OUTLINE-NONE)`
- [ ] Semantic landmarks (`header/nav/main/footer`), exactly one `<h1>` per page, ordered headings `(scanner: H1-COUNT, MAIN-LANDMARK)`
- [ ] Touch targets ≥ 44×44 on mobile; `touch-action: manipulation` on tap targets
- [ ] WCAG AA contrast in every state — including button text vs button background (no white-on-white CTA), form placeholders, focus rings, glassmorphic surfaces
- [ ] `prefers-reduced-motion` branch exists and swaps motion for opacity `(scanner: REDUCED-MOTION)`
- [ ] `min-h-[100dvh]` / `dvh` units — zero `h-screen` / bare `100vh` heroes `(scanner: H-SCREEN)`
- [ ] Zero `window.addEventListener('scroll')` — ScrollTrigger, `useScroll`, IntersectionObserver, or CSS scroll-driven only `(scanner: SCROLL-LISTENER)`
- [ ] Every `<img>` has explicit dimensions and an `alt` `(scanner: IMG-ALT)`
- [ ] **Icon discipline** — one icon family for the whole page, standardized stroke width, zero hand-rolled icon paths
- [ ] Every imported package exists in `package.json` (or the install command was output first)
- [ ] Zero truncation tells in shipped code — `// ...`, `[remaining`, "for brevity" `(scanner: TRUNCATION)`
- [ ] Dual-mode builds: both modes actually rendered and checked, hierarchy parity holds

## 6. Copy audit

Re-read **every visible string** on the page — headlines, subheads, eyebrows, buttons, body, captions, alt text, footer, error messages.

- [ ] No broken grammar, no unclear referents, no cute-but-wrong AI phrasing — flagged strings rewritten plain
- [ ] Numbers are real, or explicitly labeled as mock — no invented spec-precision
- [ ] Zero lorem ipsum `(scanner: LOREM)`; zero scroll cues ("Scroll to explore", bouncing chevrons) `(scanner: SCROLL-CUE)`
- [ ] No AI copy clichés in site copy (Elevate, Seamless, Unleash, Next-Gen, Delve)

## 7. Truth & assets

- [ ] Every heavy layer (GSAP, Three/R3F, Lenis, View Transitions, Web Audio) cites its Phase 3 source — skill or docs, named
- [ ] Assets follow the acquisition protocol (generate → seed → honest placeholder); no stock hotlinks `(scanner: UNSPLASH)`
- [ ] Brand logos are real SVG marks (Simple Icons / devicon / official kit) with light + dark variants; logo walls are logos only
- [ ] The rotation stamp is the stylesheet's first line (`/* award-design · … */` — format defined at Phase 4)

## 8. Browser proof

- [ ] Full-page screenshots at **375px, 768px, 1440px**, taken and actually read — every universe claim visible in the pixels, not just coded
- [ ] The signature interaction driven live: it fires, completes, and holds frame
- [ ] Console clean at every width
- [ ] No browser tooling available → the gap is declared in the verdict, with the code-level fallback noted

## Verdict block

Emit this block, filled, as the Phase 5 artifact. `NOT DONE` blocks ship until the listed items clear.

```markdown
## Pre-flight verdict — <build name>

**Scanner:** <N> FAIL (<all fixed | K justified below>) · <M> REVIEW (judged)
**Boxes:** <ticked>/<total>
**Counts:** eyebrows <n>/<max> · sections <n> · layout families <n> · marquees <n> · CTA intents <n>
**Justified overrides:** <rule → one-line, brief-tied justification — or "none">
**Tooling gaps:** <browser verification unavailable → declared — or "none">
**Status:** READY | NOT DONE — <blocking items>
```
