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
| [ ] **Interaction-palette distinctness** | ≥3 element classes (CTA, link, figure/card, nav) carry distinct state mechanics, each named in the design_plan from the archetype's *Effect palette*, bound by one declared grammar (easing family + accent role) | Global — one mechanic recycled across classes is the fail; distinct mechanics, one grammar (`interaction-signatures.md`) |

## 5. Craft floor

Catalog: `ship-ready-floor.md` (Impose tier) + `foundations.md` UX Quality and Accessibility.

- [ ] **8-state contract** — every interactive element ships its applicable states: default, hover, focus-visible, active, disabled, loading, empty/error, success. Async surfaces carry skeletons (matching final layout), empty, and error states.
- [ ] Custom `:focus-visible` on every interactive element; skip link present; no `outline: none` without a visible replacement `(scanner: OUTLINE-NONE)`; the ring appears instantly — never animated in
- [ ] Semantic landmarks (`header/nav/main/footer`), exactly one `<h1>` per page, ordered headings `(scanner: H1-COUNT, MAIN-LANDMARK)`
- [ ] Touch targets ≥ 44×44 on mobile, measured at **every** breakpoint — a control whose text label is hidden at a width (icon-only below a breakpoint) still meets the target *there*, not just at its desktop rest size; a hit area shrunk under 24×24 by a `display:none` label is a fail even when the desktop control passed; `touch-action: manipulation` on tap targets
- [ ] WCAG AA contrast in every state — including button text vs button background (no white-on-white CTA), form placeholders, focus rings, glassmorphic surfaces
- [ ] Non-text UI holds 3:1 — icons, input borders, accent-on-surface, focus indicators (WCAG 1.4.11), on top of the AA text checks
- [ ] Async feedback is announced — toasts and validation errors carry `aria-live="polite"` (or `role="status"`); a silent visual toast is invisible to screen readers
- [ ] Every color and font value resolves to a named token (`var(--…)` / `@theme`) — an inline hex mid-file is drift (the mechanical token-drift, OKLCH/rem, native-control, and cursor checks live in §9)
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
- [ ] **Adversarial copy pass** — for every visible string ask *what does this add here, at this spot?*; a phrase, eyebrow, or stat that survives only as texture is cut. Numbered diegetic labels (`READING 01`, `01 / 03`) and atmospheric stat strips (`KP INDEX 5 · active`, `SEASON NIGHTS CLEAR 47%`, `Season 2026/27 · open`) read as registration set-dressing however in-world — cut the number or the strip unless the count is load-bearing
- [ ] Every eyebrow passes the buyer-learn test — **default is no kicker; the H1 stands alone.** An eyebrow ships only if it names something the reader needs (a real category among several, a date, place in a long index) that neither the H1 *nor the section's own position* already carries; one that restates the subject, or labels what's obvious from where it sits ("THE CURRENT NUMBER" over the issue, "SUBSCRIBE" over the signup), is cut; a mono all-caps kicker stamped above every section reads as ornamental sameness however individually worded; registration meta ("PROOF COPY", "No. 114", edition strings) signals AI unless the number IS the product's name
- [ ] **No self-narration / no process credits** — the site never describes itself ("a feature on…", "an essay about…") or names how it was made (the typefaces it is set in, the tools/process); production copy addresses the reader as the brand. A colophon crediting its own fonts, or an eyebrow calling the page "a feature", is a dev-draft tell `(ref: anti-patterns.md)`
- [ ] **Label-layer collapse** — per section, the stacked labels (eyebrow, kicker/folio, in-world device readout, title) each carry distinct information or are cut; a device readout or folio that re-states the title ("BUILDING THE MOULD" beside a "The mould" title), or a count costume ("first / second / third casting") dressed as a chapter label, is one layer too many
- [ ] **Copy volume — composed, not poured** — no section opens with a wall (4+ dense paragraphs before any image, rest, or turn); reading blocks are cut to what earns its place and broken by a pull-quote, full-bleed, or white space. Reading-first is the archetype; text-dense is the failure
- [ ] **Footer carries no presentation copy** — brand-story / provenance / edition facts ("set by hand", "printed in an edition of N", founding lines) live in the body presenting the subject, not orphaned in the footer; the footer is functional (nav, contact, legal, mark) `(ref: anti-patterns.md)`
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
- [ ] **Interactive signature driven as a real user** — a pointer / drag / 3D signature driven with a real mouse drag AND a touch drag (not synthetic events, which hide the native-drag-ghost bug): the *object* responds (not the headline), no native drag-ghost, no text selection, `touch-action: none` / `draggable="false"` / `user-select: none` set on the canvas and any poster; and the render reads *premium* against a real product of its category — a primitive-on-flat-lights or a CGI-clocked object is a fidelity fail, and a mechanic that bent the brand's core identity (a NOIRE flacon gone brown) is a concept fail; and it **reads at a glance** — a stranger notices the effect without the hint text, and one so subtle it needs its own label to be found is under-tuned, not restrained `(refs: ingredients/web3d-for-sites.md, signature-invention.md)`
- [ ] **Interactive states driven, hover→leave** — every animated control (CTA fill, nav link, card, magnetic button) driven through hover AND the mouse-leave retract (and focus→blur): the fill/sheen enters and exits inside its shape, no spill on either transition. The retract-frame spill past a `border-radius` is invisible to a static screenshot — it only shows mid-transition
- [ ] **Section seams captured** — the transition between sections screenshotted, not only section centers: no decorative layer (a hero light sweep, an oversized glow, a negative-`inset` band) bleeds across a boundary into the next section — **and a full-bleed image or video grades into its neighbour, never a hard horizontal cut into a flat band** (a crisp rectangle edge where sky meets a flat block is the crude-transition tell; grade it with a `mask-image` or a scrim, `imagery.md`). **The last seam into the footer is checked as deliberately as the first**: a full-bleed image butting a hard edge onto a flat footer band (especially a grey one) grades into the footer's own colour instead
- [ ] **Live substrate — every element responds, perceptibly** — driven (not code-read) at every section, not just the hero: each interactive element (the wordmark, every link, image/figure, card, nav, control, the accent word) carries a state you can *feel* in one coherent vocabulary. A ~3% image scale, a barely-there tint, or a fire-once effect that leaves a static frame is homeopathic — it reads as dead, not restrained; the response must register to a real pointer. The wordmark and the accent word are not exempt. A hover-revealed secondary stays reachable under touch emulation, never trapped behind a fine-pointer hover `(ref: interaction-signatures.md)`
- [ ] **One signature carries the whole scroll** — a recognizable signature behaviour recurs and builds from hero to footer, so the page reads of-a-piece; a loud hero moment over an otherwise inert body is the "dead after the hero" failure, driven and confirmed, not inferred from the code `(ref: interaction-signatures.md, signature-invention.md)`
- [ ] **Text emphasis is legible-first** — any scroll-linked text effect emphasizes already-legible copy (dim→bright, never invisible→visible), its finished state is the CSS default, and it does not re-hide on scroll-up; a Firefox / unsupported render still shows fully legible, emphasized text `(ref: text-effects.md)`
- [ ] **Signature text driven responsive** — the signature's own text overlay (readings, captions, kinetic lines, HUD labels) holds at every width 320–1920, mono and overlay strings included; a reading that overflows its column or clips over the hero is a fail the centered desktop frame hides
- [ ] **Hero collision — no absolute affordance over the H1** — at 320–430px (emulated), every absolutely / fixed-positioned hero element (a signature affordance, badge, decoration, the strike / play control) is box-checked against the H1: the two do not overlap. The desktop placement is *reconsidered* for narrow widths — reflowed into the stack or below the standfirst — never left in its desktop position where it clears the headline only by whitespace luck (a clearance that depends on the H1's wrap and the font-load is a fail even when the glyphs happen to miss). Mobile reconsidered, not the desktop layout shrunk
- [ ] **Overlay menu close** — the full-screen menu, opened and closed live, carries a visible labeled `✕` (not a faint glyph beside a still-"MENU" label); `Esc` closes, focus returns to the trigger, body scroll locks (`navigation-patterns.md`)
- [ ] **Brand mark + favicon real** — the logo is a designed SVG/PNG glyph or a clean typographic wordmark (no random dot / status-tick), the *same* mark drives the favicon / `icon.svg`, both verified rendered in the browser (`imagery.md`)
- [ ] **Modern-CSS-degraded render** — beyond the no-JS floor: a scroll-timeline / `@supports`-unsupported render checked, so no `animation: … both` snaps to its end state and obscures content — the class of bug where a scroll-linked scrim darkens the whole page, or a reveal stays hidden, on a browser without the timeline. Every scroll-driven opacity/scrim animation is `@supports (animation-timeline: …)`-guarded, with the safe state as the base an unsupported browser holds
- [ ] **Motion model — content persists, décor reverses** — content reveals (headings, copy, cards) fire once and STAY on scroll-up; scroll a section past, then back up — the copy does not fade out (re-hiding content is the NN/g failure). Decorative / scrubbed motion (parallax, curtain-on-image, pinned video) is reversible scroll-linked and never hides content. A reversible content reveal is allowed only where the DESIGN.md declares it, `cover`-phase-ranged `(refs: motion-palette.md)`
- [ ] **Nav holds on scroll-stop** — flick down (bar hides), stop, and let a smooth-scroll layer settle: the bar stays hidden, it does not flash back at rest; scroll up past `SHOW_TOL` and it returns. A bar that reappears every time the scroll stops is the settle-frame bug `(ref: navigation-patterns.md gotcha 5)`
- [ ] Console clean at every width

Full-page captures never fire scroll-gated reveals (IntersectionObserver sees no scroll) and render fixed canvases at y=0 — scroll-verify those sections or substitute viewport-frame captures at key positions, and declare the substitution. Sub-500px widths need device *emulation* — a desktop window silently floors its width and verifies the wrong layout.

No browser tooling on the harness → this section's boxes convert to **declared gaps** in the verdict (Tooling gaps field), each with the code-level fallback noted; the status may still read READY when everything else holds. Falsely ticking a browser box is worse than declaring the gap.

## 9. Code-craft review

The final mechanical code pass (`code-review.md`), run across the shipped CSS/JS/HTML — it enforces adoption of the modern-web baseline (`modern-web-baseline.md`) and bans the tells. It **overrides the DESIGN.md** — a spec that prescribes a tell (a native control, a `not-allowed` cursor) is corrected, not deferred to.

- [ ] **Token-drift / SSOT** — no token value duplicated as a raw literal; no CSS custom property redeclared as a hardcoded JS constant; no token defined and never used; no token value drifting from its DESIGN.md declaration
- [ ] **OKLCH + rem** — opaque authored colour in `oklch()` / relative-color (translucent overlays / borders / scrims may stay `rgb(… / α)`); px only for borders, hairlines, touch-targets; spacing/type on the rem scale, no off-scale literals
- [ ] **Native-control + cursor lint** — zero native `<select>`/checkbox/radio without `appearance: none`; zero `cursor: not-allowed`; run against the DESIGN.md too
- [ ] **State-colour commitment** — every colour in a `:hover`/`:focus`/`:active` rule resolves to a token, and a control's state colour is the committed interactive accent, never a paler wash of it (a tint on the button fill while links carry the full accent is the pale-hover fail); the nav bar carries zero `border-bottom` in any state, and its solid surface token is the page ground or the dominant primary (`navigation-patterns.md`, `interaction-signatures.md`)
- [ ] **A11y floor** — contrast computed at each rule's actual font-size (sub-4.5:1 under ~18px fails regardless of a "decorative" note); tap targets measured at each breakpoint (a label hidden below a width can shrink a control under 24×24); every full-screen overlay sets `inert`/`aria-hidden` on siblings and traps focus, `Esc` returns focus to the trigger
- [ ] **JS lifecycle** — a render loop resumes only when its target is visible AND in-viewport (not on `visibilitychange` alone); every `setTimeout` guarding a visibility/`hidden` toggle is cleared by its inverse action

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
**Code-craft:** <N fixed · K justified · clean | issues — the §9 pass>
**Status:** READY | NOT DONE — <blocking items>
```
