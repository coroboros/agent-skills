# Pre-Flight — the ship gate

Phase 5 of the protocol. Runs on the built site, before the fresh-context review (R2). Binary: every box ticks or the build is not done — fix, re-run, then proceed. No sampling, no compression, no "mostly". Where a rule offers an override, the override is written into the verdict and tied to the brief; an unstated override is a fail.

This file is the checklist; `anti-patterns.md` is the catalog behind it (rationale, fixes, full failure modes). When a box is unclear, read its catalog entry — never guess it away.

## 1. Mechanical scan (run first)

```bash
python3 scripts/preflight_scan.py <build-dir> --archetype <archetype>
```

(Path relative to this skill's root. `--archetype` applies declared archetype grammar: `editorial` and `corporate-luxury` suppress EMDASH; `brutalist` suppresses META-LABEL. The scanner skips `DESIGN.md` — the spec legitimately quotes banned phrases as prohibitions.)

- The gate rides the hit report, not the shell: a piped `$?` reports the pipe's last command, not the scanner — read the exit code from a direct invocation, or trust the printed summary.
- Every **FAIL** hit: fix it, or write a one-line justification tied to the brief into the verdict block.
- Every **REVIEW** hit: judge it against the catalog and record the call.
- The scanner **catches, it never clears** — a clean scan ticks no box below. It cannot see composition, hierarchy, or intent; the boxes and the R2 review carry that weight.
- Scanner severities don't mirror the box tiers: a REVIEW rule can feed an axiomatic box when the regex can't distinguish legitimate use (emoji in copy vs emoji as icons, a licensed unsplash asset vs a hotlink). The box is the gate; the scanner is the flashlight.

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
- [ ] Hero H1 lands in the lines the design_plan proved (≤2 committed; 3 is the absolute ceiling and takes a written override)
- [ ] Zero `SECTION 01` / index meta-labels `(scanner: META-LABEL)` — Brutalist's ASCII process flags are the declared exception (`brutalist.md`)
- [ ] No generic avatars (SVG eggs, stock "diverse team")
- [ ] No startup-slop brand names (Acme, Nexus, SmartFlow)
- [ ] Hero carries a real visual (photography / generated / 3D / deliberate type-as-image)
- [ ] No fake-div product screenshots — real capture or honest labeled placeholder

## 3. Consistency locks (page-wide, binary)

- [ ] **Theme lock** — one theme for the whole page; no section flips light↔dark mid-scroll. Override: a single deliberate color-block device, declared in the DESIGN.md.
- [ ] **Accent lock** — one accent color, identical role everywhere, present once per viewport, never twice. Archetype scope: Bold/Maximal and Experimental run multi-hue by design — there the lock is *role consistency* (each hue keeps one job, declared in the DESIGN.md), not count.
- [ ] **Shape lock** — one corner-radius system (all-sharp, all-soft, or a documented mixed rule applied everywhere). Round buttons in a square layout is a fail.
- [ ] **Emphasis lock** — in-headline emphasis uses italic or bold of the SAME family; no foreign-family word injected for visual interest.
- [ ] **Register lock** — one copy register per page (technical mono, editorial prose, or marketing punch — not a blend), unless the DESIGN.md declares the mix.

## 4. Countable boxes

Each is a number computed from the rendered page against a threshold. Cite the count in the verdict. Every row declares its scope — **Global** runs on every archetype; **Archetype-conditional** names its suppression. Overrides exist so no ban is a dead end, but an override is written into the verdict, tied to the brief.

| Box | Rule | Scope / Override |
|---|---|---|
| [ ] **Eyebrow density** | Eyebrow tags ≤ `ceil(sectionCount / 3)`; hero counts as one `(scanner: EYEBROW-DENSITY)` | Global — eyebrows punctuate, they don't label every section. Card-internal category labels (Bento tile anatomy) are not section eyebrows — but uniform labels on every tile get judged for sameness at R2 |
| [ ] **Bento fill** | N items render as exactly N cells — zero empty or filler cells; ≥2 cells in any multi-cell grid carry real visual variation (image, gradient, pattern, tint); on the Bento archetype every tile *demonstrates* its claim (live, animated, or visual), never a mini spec-sheet | Global |
| [ ] **Zigzag cap** | ≤ 2 consecutive image-text split rows | Global — Override: a third is admissible only if it inverts composition, never a fourth |
| [ ] **Marquee cap** | ≤ 1 marquee / infinite ticker per page; any auto-moving strip pauses on hover AND on focus (WCAG 2.2.2) | Global — one signature ticker is fine; a logo wall *and* a testimonial ribbon is the tell |
| [ ] **Layout-family variety** | ≥ 4 distinct section layout families per 8 sections | Archetype-conditional — suppressed for single-fold portfolios and pure docs |
| [ ] **Hero-stack cap** | ≤ 4 stacked text elements (eyebrow OR brand strip · H1 · subtext ≤ 20 words · one CTA cluster); no trust-strip, logo wall, or pricing teaser inside the hero | Global — Override: a long editorial standfirst counts as one element — cap the stack, not the sentence |
| [ ] **CTA-intent consistency** | one label per intent across the page ("Get in touch" + "Let's talk" = same intent = fail) | Global — repeating the *same* label for the same intent is fine |
| [ ] **Em-dash density** | body-copy density ≤ ~1 per 100 words, en dashes count `(scanner: EMDASH)` | Archetype-conditional — suppressed for `editorial` and `corporate-luxury`, where the em-dash is a deliberate typographic choice |
| [ ] **Hero top padding** | ≤ 6rem (`pt-24`) at desktop | Global — needs more breathing room → scale the type or the asset, never the padding |
| [ ] **Nav discipline** | one line at ≥1024px, height ≤ 80px | Global — condense labels, drop secondary items, or go hamburger; a two-line desktop nav is broken |
| [ ] **CTA wrap** | every interactive text (CTAs, nav links, footer links, tabs, breadcrumbs) holds one line at every width 320–1920 | Global — shorten the label (≤3 words for primary) or widen the button |
| [ ] **Quote length** | quote bodies ≤ 3 lines; attribution is name + role, never name alone | Global — footer-size testimonials may stretch slightly; the spirit is "fits in a glance" |
| [ ] **Middle-dot rationing** | `·` ≤ 1 per metadata line | Global — prefer line breaks, hairlines, or columns as the separator family |
| [ ] **Split-header** | zero "left big headline + right floating explainer" section headers — stack vertically | Global — Override: the right column carries a real visual or interactive element, never filler text |
| [ ] **Long-list component** | every list > 5 items uses a designed component (grouped chunks, card grid, tabs, scroll-snap, marquee) | Global — bare rows with a hairline under each is the fail |
| [ ] **Italic descenders** | every italic display word containing `y g j p q` has line-height ≥ 1.1 and bottom reserve | Global — clipped descenders are a rendering bug, not a style |
| [ ] **Pacing curve** | the design_plan's per-section intensity holds on the page: exactly one climax (the signature) and ≥ 1 rest; every section within ±1 of the others is a flat curve | Global — a page of equally loud sections is a template |
| [ ] **Quiet layer** | ≥ 2 second-read details shipped from the `optical-craft.md` menu (`::selection`, palette favicon, voice-written `<title>`, designed 404, …), in palette and voice | Global |
| [ ] **Side-stripe ban** | zero 2px+ colored left/right accent borders on cards or callouts `(scanner: SIDE-STRIPE)` | Global — the 2018-SaaS tell |
| [ ] **Font-family cap** | ≤ 3 families page-wide, plus at most one mono outlier `(scanner: FONT-COUNT)` | Global — more reads as collage |
| [ ] **Motion motivated** | every animation names what it communicates (one sentence, in the design_plan or the code comment) | Global — unexplained motion is decoration |

## 5. Craft floor

Catalog: `ship-ready-floor.md` (Impose tier) + `foundations.md` UX Quality and Accessibility.

- [ ] **8-state contract** — every interactive element ships its applicable states: default, hover, focus-visible, active, disabled, loading, empty/error, success. Async surfaces carry skeletons (matching final layout), empty, and error states.
- [ ] Custom `:focus-visible` on every interactive element; skip link present; no `outline: none` without a visible replacement `(scanner: OUTLINE-NONE)`; the ring appears instantly — never animated in
- [ ] Semantic landmarks (`header/nav/main/footer`), exactly one `<h1>` per page, ordered headings `(scanner: H1-COUNT, MAIN-LANDMARK)`
- [ ] Touch targets ≥ 44×44 on mobile; `touch-action: manipulation` on tap targets
- [ ] WCAG AA contrast in every state — including button text vs button background (no white-on-white CTA), form placeholders, focus rings, glassmorphic surfaces
- [ ] Non-text UI holds 3:1 — icons, input borders, accent-on-surface, focus indicators (WCAG 1.4.11), on top of the AA text checks
- [ ] Async feedback is announced — toasts and validation errors carry `aria-live="polite"` (or `role="status"`); a silent visual toast is invisible to screen readers
- [ ] Every color and font value resolves to a named token (`var(--…)` / `@theme`) — an inline hex mid-file is drift
- [ ] No horizontal scroll at any width 320–1920: grid image tracks use `minmax(0, 1fr)`, display headlines carry `overflow-wrap: anywhere`, page clipping uses `overflow-x: clip` (never `hidden` — it kills `position: sticky`)
- [ ] `prefers-reduced-motion` branch exists and swaps motion for opacity `(scanner: REDUCED-MOTION)`
- [ ] **Fill / overlay clip** — every animated fill, sheen, or reveal inside a shaped container clips to its shape (`overflow: hidden` or `clip-path` on the clip parent), and every full-bleed / negative-`inset` decorative layer clips to its bound; `scaleX` fills on rounded shapes are ruled out in favor of `translateX` / `clip-path`. Verified in the browser at §8 (hover→leave), where the spill actually shows
- [ ] **No-JS floor** — a JS-disabled render shows every section's content: initial hidden states applied via JS-added classes only, never in base CSS; canvas/3D heroes carry a static fallback `(scanner: NOJS-HIDDEN)`
- [ ] `min-h-[100dvh]` / `dvh` units — zero `h-screen` / bare `100vh` heroes `(scanner: H-SCREEN)`
- [ ] Zero `window.addEventListener('scroll')` — ScrollTrigger, `useScroll`, IntersectionObserver, or CSS scroll-driven only `(scanner: SCROLL-LISTENER)`
- [ ] Zero ScrollTrigger debug markers in shipped code `(scanner: MARKERS)`
- [ ] Every `<img>` has explicit dimensions and an `alt` `(scanner: IMG-ALT, IMG-DIMENSIONS)`
- [ ] **Icon discipline** — one icon family for the whole page, standardized stroke width, zero hand-rolled icon paths
- [ ] Every imported package exists in `package.json` (or the install command was output first)
- [ ] Zero truncation tells in shipped code — `// ...`, `[remaining`, "for brevity" `(scanner: TRUNCATION)`
- [ ] Dual-mode builds: both modes actually rendered and checked, hierarchy parity holds

## 6. Copy audit

Re-read **every visible string** on the page — headlines, subheads, eyebrows, buttons, body, captions, alt text, footer, error messages.

- [ ] No broken grammar, no unclear referents, no cute-but-wrong AI phrasing — flagged strings rewritten plain
- [ ] Every eyebrow passes the buyer-learn test — it names something the reader needs (category, value, place in the page); registration meta ("PROOF COPY", "No. 114", edition strings) is decoration that signals AI, unless the number IS the product's name
- [ ] Every data visual decodes at a glance — marks self-evident in context, or named by a one-line legend; the loop screenshot is the test (a stranger can say what each mark is)
- [ ] Numbers are real, or explicitly labeled as mock — no invented spec-precision
- [ ] Zero lorem ipsum `(scanner: LOREM)`; zero scroll cues ("Scroll to explore", bouncing chevrons) `(scanner: SCROLL-CUE)`
- [ ] No AI copy clichés in site copy (Elevate, Seamless, Unleash, Next-Gen, Delve)
- [ ] Content realism holds: no identical dates across posts, no duplicate avatars across different names, no dead `#` links, the nav marks the active state

## 7. Truth & assets

- [ ] Every heavy layer (GSAP, Three/R3F, Lenis, View Transitions, Web Audio) cites its Phase 3 source — skill or docs, named
- [ ] Heavy layers are used *well*, not just cited — the WebGL scene runs a physical material + HDRI environment (never a primitive on flat lights), the motion layer uses the sourced GSAP/official-skill path; "sourced but low-effort" is a fidelity fail `(ref: ingredients/web3d-for-sites.md)`
- [ ] Assets follow the acquisition protocol (generate → curated stock → seed → honest placeholder); no stock **hotlinks** — a downloaded, optimized, graded curated pick is fine, a live `images.unsplash.com` src is not `(scanner: UNSPLASH)`; curated-stock slots are flagged in the asset list to replace with commissioned/generated finals
- [ ] Brand logos are real SVG marks (Simple Icons / devicon / official kit) with light + dark variants; logo walls are logos only
- [ ] The rotation stamp is the stylesheet's first line (`/* award-design · … */` — format defined at Phase 4; on first contact with a project this skill didn't build, write it now from the adopted universe)

## 8. Browser proof

- [ ] **The desire read** — a stranger would screenshot the hero and send it to someone. An honest no is not a fix-forward: regenerate the visual concept (Phases 1/4), not the tokens

- [ ] The conformance loop exited clean on every section — both core widths passing in the same iteration; drift left standing at the 5-loop cap is filed below, never silently accepted
- [ ] Full-page screenshots at **375px, 768px, 1440px**, taken and read — one line per screenshot on what it showed; every universe claim visible in the pixels, not just coded — plus a fold check at 1280×800: the hero's essential content (H1, subtext, CTA) sits inside the first viewport
- [ ] Computed `font-family` on display text resolves to the committed face — a silent fallback to a system font is invisible in the code and voids the typography
- [ ] The signature interaction driven live: it fires, completes, and holds frame — with Chrome DevTools MCP connected the performance trace is mandatory (signature at 60fps, LCP measured against < 1.5s; a miss is a finding, not a gap; a surface with no per-frame fps readout declares the proxy — a clean trace over the animation window, compositor-only properties); with `dev-browser` only, both numbers go to declared gaps
- [ ] **Interactive signature driven as a real user** — a pointer / drag / 3D signature driven with a real mouse drag AND a touch drag (not synthetic events, which hide the native-drag-ghost bug): the *object* responds (not the headline), no native drag-ghost, no text selection, `touch-action: none` / `draggable="false"` / `user-select: none` set on the canvas and any poster; and the render reads *premium* against a real product of its category — a primitive-on-flat-lights or a CGI-clocked object is a fidelity fail, and a mechanic that bent the brand's core identity (a NOIRE flacon gone brown) is a concept fail `(refs: ingredients/web3d-for-sites.md, signature-invention.md)`
- [ ] **Interactive states driven, hover→leave** — every animated control (CTA fill, nav link, card, magnetic button) driven through hover AND the mouse-leave retract (and focus→blur): the fill/sheen enters and exits inside its shape, no spill on either transition. The retract-frame spill past a `border-radius` is invisible to a static screenshot — it only shows mid-transition
- [ ] **Section seams captured** — the transition between sections screenshotted, not only section centers: no decorative layer (a hero light sweep, an oversized glow, a negative-`inset` band) bleeds across a boundary into the next section
- [ ] **Modern-CSS-degraded render** — beyond the no-JS floor: a scroll-timeline / `@supports`-unsupported render checked, so no `animation: … both` snaps to its end state and obscures content — the class of bug where a scroll-linked scrim darkens the whole page, or a reveal stays hidden, on a browser without the timeline. Every scroll-driven opacity/scrim animation is `@supports (animation-timeline: …)`-guarded, with the safe state as the base an unsupported browser holds
- [ ] Console clean at every width

Full-page captures never fire scroll-gated reveals (IntersectionObserver sees no scroll) and render fixed canvases at y=0 — scroll-verify those sections or substitute viewport-frame captures at key positions, and declare the substitution. Sub-500px widths need device *emulation* — a desktop window silently floors its width and verifies the wrong layout.

No browser tooling on the harness → this section's boxes convert to **declared gaps** in the verdict (Tooling gaps field), each with the code-level fallback noted; the status may still read READY when everything else holds. Falsely ticking a browser box is worse than declaring the gap.

## Verdict block

Emit this block, filled, as the Phase 5 artifact. `NOT DONE` blocks ship until the listed items clear.

```markdown
## Pre-flight verdict — <build name>

**Scanner:** <N> FAIL (<all fixed | K justified below>) · <M> REVIEW (judged)
**Open with:** <command — a module build needs a server; `file://` runs zero JS>
**Boxes:** <ticked>/<total>
**Counts:** eyebrows <n>/<max> · sections <n> · layout families <n> · marquees <n> · CTA intents <n>
**Justified overrides:** <rule → one-line, brief-tied justification — or "none">
**Tooling gaps:** <browser verification unavailable → declared — or "none">
**Status:** READY | NOT DONE — <blocking items>
```
