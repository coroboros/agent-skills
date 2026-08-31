# Pre-flight — the mechanical floor

A chunk's Verify, and the review chunk whole. Runs on the built pages, before the fresh-context review (R2). Everything here is countable or binary — no taste lives in this file: quality is R2's job, and clearing this floor is necessary, never sufficient. Every box ticks or the build is not done — fix, re-run, then proceed. Where a rule offers an override, the override is written into the verdict and tied to the brief; an unstated override is a fail.

`anti-patterns.md` is the catalog behind the tells (rationale, fixes, failure modes). When a box is unclear, read its catalog entry — never guess it away.

## 1. Mechanical scan (run first)

```bash
python3 scripts/preflight_scan.py <build-dir> --archetype <archetype>
```

(Path relative to this skill's root. **The archetype is reviewer-supplied — `--archetype` is its only source**, derived from the brief and the DESIGN.md and passed on the command line, so the audited build never chooses which archetype-scoped checks run. It applies declared archetype grammar: `editorial` and `corporate-luxury` suppress EMDASH; `brutalist` suppresses META-LABEL. The scanner skips `DESIGN.md` — the spec legitimately quotes banned phrases as prohibitions.)

- Read the `N files scanned` line before the summary: zero files scanned means the path was wrong — the run proves nothing; rerun on the real build dir.
- The gate rides the hit report, not the shell: a piped `$?` reports the pipe's last command — read the exit code from a direct invocation, or trust the printed summary.
- Every **FAIL** hit: fix it, or write a one-line justification tied to the brief into the verdict block.
- Every **REVIEW** hit: judge it against the catalog and record the call.
- The scanner **catches, it never clears** — a clean scan ticks no box below.

**The detector runs beside the scanner.** With a browser rung that evaluates JS, inject `assets/detector.js` into the rendered page and run `awardDetector.run({face, archetype})` (`references/detector.md`). Detector FAILs are fix-only: no prose override clears one. Its REVIEW findings (dead sections, homeopathic responses, unmeasured elements) are evidence handed to R2, not boxes here — and the elements R2 drives are sampled by the reviewer from the detector's substrate census, never the builder's shortlist.

## 2. Tells

Catalog: `anti-patterns.md`. One violation reads as AI-generated regardless of everything else.

- [ ] No AI-purple gradient anywhere `(scanner: AI-PURPLE)`
- [ ] No Inter / Roboto / Arial / system font as the display face `(scanner: DISPLAY-FONT)`
- [ ] No pure `#000` / `#FFF` `(scanner: PURE-BW)`
- [ ] No placeholder names, no fake round statistics `(scanner: PLACEHOLDER-NAME, FAKE-STAT)`
- [ ] No centered-hero-over-dark-image-with-generic-headline template
- [ ] No 3 equal cards as the feature section
- [ ] No emojis as UI icons `(scanner: EMOJI-UI)`
- [ ] Zero `SECTION 01` / index meta-labels `(scanner: META-LABEL)` — Brutalist's ASCII process flags are the declared exception
- [ ] No generic avatars, no startup-slop brand names (Acme, Nexus, SmartFlow)
- [ ] Hero carries a real visual (photography / generated / 3D / deliberate type-as-image)
- [ ] No fake-div product screenshots — real capture or honest labeled placeholder
- [ ] Zero 2px+ colored side-stripe accents on cards `(scanner: SIDE-STRIPE)`
- [ ] Hero H1 lands in ≤2 lines (3 takes a written override) `(detector: H1-LINES)`

## 3. Consistency locks (page-wide, binary)

- [ ] **Theme lock** — one theme for the whole page; no section flips light↔dark mid-scroll. Override: a single deliberate color-block device, declared in the DESIGN.md.
- [ ] **Accent lock** — one accent color, identical role everywhere. Bold/Maximal and Experimental run multi-hue by design — there the lock is role consistency, not count.
- [ ] **Shape lock** — one corner-radius system applied everywhere.
- [ ] **Emphasis lock** — in-headline emphasis uses italic or bold of the same family.
- [ ] **Register lock** — one copy register per page, unless the DESIGN.md declares the mix; one motion register page-wide `(scanner: EASE-OVERSHOOT names every overshoot/elastic curve — judge each against the declared register)`

## 4. Countable

Each is a number computed from the rendered page. Cite the count in the verdict.

- [ ] **Eyebrows** — default none; when used, ≤ `ceil(sectionCount / 3)`, hero counts as one `(scanner: EYEBROW-DENSITY)`
- [ ] **Fonts** — ≤ 3 families page-wide, plus at most one mono outlier `(scanner: FONT-COUNT)`
- [ ] **Marquees** — ≤ 1 per page; any auto-moving strip pauses on hover and focus (WCAG 2.2.2)
- [ ] **Zigzag** — ≤ 2 consecutive image-text split rows; a third only if it inverts composition
- [ ] **Grid fill** — N items render as exactly N cells, zero filler cells
- [ ] **Hero stack** — ≤ 4 stacked text elements; no trust-strip, logo wall, or pricing teaser inside the hero
- [ ] **CTA wrap** — every interactive text holds one line at every width 320–1920
- [ ] **CTA intent** — one label per intent across the page
- [ ] **Em-dash density** — body copy ≤ ~1 per 100 words `(scanner: EMDASH — suppressed for editorial / corporate-luxury)`
- [ ] **Middle dots** — `·` ≤ 1 per metadata line
- [ ] **Legibility floor** — no text below ~11px effective at 1440; every string over photography passes AA at its worst rendered point
- [ ] **Layout variety** — ≥ 4 distinct section layout families per 8 sections (suppressed for single-fold pages)
- [ ] **Long lists** — every list > 5 items uses a designed component, never bare rows with hairlines
- [ ] **Italic descenders** — every italic display word with `y g j p q` has line-height ≥ 1.1 and bottom reserve
- [ ] **Interaction coherence** — ≥3 element classes (CTA, link, figure, nav) carry distinct state mechanics under the one declared register; within a class every instance carries the identical treatment; no bare-brightness, lone-lift, or pale-tint primary hover (the documented product-UI default)

## 5. Craft floor

Catalog: `ship-ready-floor.md` (Impose tier) + `modern-web-baseline.md` + `foundations.md` UX Quality and Accessibility. The final code pass (`code-review.md`) enforces token discipline, OKLCH + rem, native-control and cursor lint — its result is one line in the verdict.

- [ ] **8-state contract** — every interactive element ships its applicable states (default, hover, focus-visible, active, disabled, loading, empty/error, success)
- [ ] Custom `:focus-visible` on every interactive element — designed, keyboard-only, instant; skip link present; no `outline: none` without replacement `(scanner: OUTLINE-NONE)`
- [ ] Semantic landmarks, exactly one `<h1>`, ordered headings `(scanner: H1-COUNT, MAIN-LANDMARK)`
- [ ] Touch targets ≥ 44×44 at every breakpoint; `touch-action: manipulation` on tap targets `(detector: TAP-TARGET)`
- [ ] WCAG AA contrast in every state; non-text UI holds 3:1 `(detector: CONTRAST)`
- [ ] Async feedback announced — toasts and validation errors carry `aria-live="polite"` or `role="status"`
- [ ] Every color and font value resolves to a named token `(detector: TOKEN-CONFORM)`
- [ ] No horizontal scroll at any width 320–1920; page clipping uses `overflow-x: clip`, never `hidden` `(detector: H-OVERFLOW)`
- [ ] `prefers-reduced-motion` branch exists: it zeroes the durations or removes the motion, never an element or its end state — a static opacity state is fine, a blank page is not (`foundations.md` Accessibility) `(scanner: REDUCED-MOTION)`
- [ ] Every animated fill, sheen, or reveal clips to its container's shape; full-bleed decorative layers clip to their bounds
- [ ] **No-JS floor** — a JS-disabled render shows every section's content; canvas/3D heroes carry a static fallback `(scanner: NOJS-HIDDEN)`
- [ ] `dvh` units — zero `h-screen` / bare `100vh` heroes `(scanner: H-SCREEN)`
- [ ] Zero `window.addEventListener('scroll')`; zero ScrollTrigger debug markers `(scanner: SCROLL-LISTENER, MARKERS)`
- [ ] Every `<img>` has explicit dimensions and an `alt` `(scanner: IMG-ALT, IMG-DIMENSIONS)` `(detector: IMG-BROKEN)`
- [ ] One icon family, standardized stroke width
- [ ] **State-colour commitment** — every colour in a `:hover`/`:focus`/`:active` rule resolves to a token and carries the committed accent at full strength, never a paler wash of it; the nav bar carries zero `border-bottom` in any state and its solid surface is the page ground or the dominant primary `(detector: NAV-BORDER)`
- [ ] Every imported package exists in `package.json` (or the install command was output first)
- [ ] Zero truncation tells in shipped code `(scanner: TRUNCATION)`

## 6. Copy floor

Re-read every visible string — headlines, buttons, captions, alt text, errors.

- [ ] No broken grammar, no unclear referents; zero lorem `(scanner: LOREM)`; zero scroll cues `(scanner: SCROLL-CUE)`
- [ ] No AI copy clichés (Elevate, Seamless, Unleash, Next-Gen, Delve) `(scanner: CLICHE-COPY)`
- [ ] No kicker+heading or heading+first-line word echo — brand proper nouns exempt `(scanner: COPY-ECHO)`
- [ ] No self-narration — the site never describes itself or credits its own fonts and tools
- [ ] **Specificity floor** — every headline and subhead carries ≥1 concrete from the build's world; category-words-only fails (`copy-recipes.md`)
- [ ] Numbers are real or explicitly labeled mock; no invented spec-precision; no dead `#` links `(scanner: DEADLINK)`
- [ ] One copy language, English unless the brief asks — and then total `(scanner: COPY-LANG)`
- [ ] No quoted catalog string ships verbatim `(scanner: QUOTED-EXEMPLAR)`

## 7. Assets

- [ ] Every heavy layer cites the source it was truth-sourced from (step 7) with one checkable freshness token (current version or a recently-changed API fact)
- [ ] Assets follow the acquisition protocol; no stock hotlinks — downloaded, optimized, graded `(scanner: UNSPLASH)`
- [ ] **Asset fidelity, measured** — every signature asset (full-bleed, scrubbed, zoomed) holds ≥ device pixels at its worst rendered moment, numbers from the machine readout `(scanner: IMG-NATIVE-RES)`, the rule in `imagery.md` §Native resolution or nothing; scrubbed sequences are distinct real frames at ~90+ per section
- [ ] Brand logos are real SVG marks with light + dark variants; the same mark drives the favicon, both verified rendered

## 8. Driven in the browser

Resolve the browser rung (`external-truth.md`). Full-page captures never fire scroll-gated reveals and render fixed canvases at y=0 — scroll-verify those sections or substitute viewport-frame captures, and declare the substitution. Sub-500px widths need device *emulation*.

- [ ] Full-page screenshots at 375px, 768px, 1024px, 1440px, 1920px — the render-floor sweep (`assets/render-floor.js`) — taken and read, one line per screenshot; fold check at 1280×800 (H1, subtext, CTA inside the first viewport)
- [ ] Computed `font-family` on display text resolves to the committed face `(detector: FONT-RESOLVE)`
- [ ] The signature driven live: fires, completes, holds frame — 60fps target on a sustained ≥55fps floor (`stack-facts.md`) and LCP < 1.5s, from a trace with its provenance cited; an asserted number is a fail. Its own text overlay (readings, captions, HUD labels) holds at every width 320–1920. A pointer/scroll-tracked window (loupe, torch, follow-reveal) is driven under a trace: Composite-only frames, zero per-frame paint `(scanner: MOVING-BG-POS, BG-ATTACH-FIXED, TRACKED-CLIP, TRACKED-ORIGIN)`
- [ ] Every animated control driven hover→leave (and focus→blur): the fill enters and retracts inside its shape — the spill shows only mid-transition. The wordmark follows the enrollment rule (live-probed: 0/6 winners build a bespoke wordmark hover) — a live-text wordmark joins the site's one link-hover grammar verbatim; a drawn logo rests static under hover
- [ ] Section seams captured, footer included: no decorative layer bleeds across a boundary; a full-bleed image grades into its neighbour, never a hard cut into a flat band
- [ ] **Loader handoff** (when present) — the fold behind the curtain or counter is already composed when it lifts, verified in the browser
- [ ] **Route change** (multi-route builds) — one real route change driven live: the committed transition plays, back-button and scroll restoration hold
- [ ] **Nav over the hero** — captured at rest and driven past the hero: transparent, scrim, or frost over hero media; the owned ground arrives at the hero's bottom sentinel `(detector: NAV-HERO-OPAQUE, NAV-HERO-SURFACE)`
- [ ] **Nav under momentum** — one inertial scroll-down plus a ±3px jitter burst: zero hide/show flips, the sampled flip count pasted; the bar stays hidden on scroll-stop
- [ ] **Touch emulation** — press elements answer the tap on `:active`/pointerdown; hover-revealed secondaries stay reachable; pointer-only classes rest dormant (that is the winner answer, not a gap); the signature's discovery beat is also driven under touch emulation — a fine-pointer-only invitation fails
- [ ] **Overlay menu** (when present) — opened and closed live: icon-only toggle, real transition, `Esc` closes, focus returns, body scroll locks; every drawer link driven with the drawer open — a rest-state detector run misses them by design
- [ ] **Motion model** — content reveals persist on scroll-up; decorative/scrubbed motion reverses; looping video watched through ≥2 cycles with no seam jump
- [ ] **Degraded renders** — one JS-disabled render (every section's content visible) and one modern-CSS-degraded render: every scroll-driven animation is `@supports (animation-timeline: …)`-guarded with the safe state as the base; with motion off (`prefers-reduced-motion` + JS kill) every section frame reads as a deliberately composed layout, the climax resolving to a poster frame
- [ ] Console clean at every width

No browser tooling on the harness → this section's boxes convert to **declared gaps** in the verdict, each with the code-level fallback noted and the verbatim failed probe (ToolSearch for the browser MCP is the mandatory first probe on an MCP-capable harness). Gaps cap the ship label per `gate/review.md` §The ship label. Falsely ticking a browser box is worse than declaring the gap; declaring a gap the harness could have closed is the same fail.

## Verdict block

Emit this block, filled, as the review chunk's artifact. `NOT DONE` blocks ship until the listed items clear.

```markdown
## Pre-flight verdict — <build name>

**Scanner:** <N files scanned> · <N> FAIL (<all fixed | K justified below>) · <M> REVIEW (judged)
**Detector:** <N> FAIL (fix-only) · <M> REVIEW — or "no JS-evaluating rung"
**Open with:** <command — a module build needs a server; `file://` runs zero JS>
**Boxes:** <ticked>/<total> — every unticked, overridden, or gap box listed by its bold name
**Perf:** LCP <n>s · CLS <n> · INP <n>ms · signature fps <n> — provenance: <trace/tool ref>
**Justified overrides:** <rule → one-line, brief-tied justification — or "none">
**Tooling gaps:** <verbatim failed probe → declared gaps — or "none">
**Status:** READY | REVIEWED-SAME-CONTEXT | NOT DONE — <blocking items> (browser gates dark → listed under Tooling gaps; caps per `gate/review.md` §The ship label)
```

Blocking is defined, not felt: any unticked box or any FAIL without a written justification → NOT DONE. READY requires §8 evidence. The R2 review receives this verdict but reads the pixels first — its desire read outranks a clean floor.
