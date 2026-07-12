# Pre-Flight — the ship gate

Phase 5 of the protocol. Runs on the built site, before the fresh-context review (R2). Binary: every box ticks or the build is not done — fix, re-run, then proceed. No sampling, no compression, no "mostly". Where a rule offers an override, the override is written into the verdict and tied to the brief; an unstated override is a fail.

This file is the checklist; `anti-patterns.md` is the catalog behind it (rationale, fixes, full failure modes). When a box is unclear, read its catalog entry — never guess it away.

## 0. Pre-emit critique — enters Phase 5 with it done

The Phase 4 closer, scored before any box below. Six axes, 1–5, each score naming its weakest concrete instance on the page (an element, a string, a beat) — a score with no named instance is not a score:

- **World** — the spine felt in layout, type, color, motion, copy. 1 = tokens on a template; 3 = coherent but expected; 5 = remove the copy and the design still says the world.
- **Hierarchy** — the eye's path. 1 = everything equal; 3 = size-only; 5 = scale, weight, and color compound.
- **Craft** — optical discipline. 1 = drift and magic numbers; 3 = clean but untuned; 5 = tuned per size, seams graded, states clipped.
- **Specificity** — concrete anchors in copy and image. 1 = category words; 3 = one real anchor per fold; 5 = names, counts, places, gestures throughout.
- **Restraint** — every prop earns its place. 1 = clutter; 3 = one questionable device; 5 = subtraction reads deliberate.
- **Aliveness** — the substrate as *felt*. 1 = static after the hero; 3 = responses exist, some homeopathic; 5 = every element answers perceptibly, one thread carries.

The lowest axis always takes one named, targeted revision before the boxes run — there is always a lowest, so this cannot be scored around. Scores append to the stamp (`· critique: W4 H3 C4 S4 R5 A3`) as the calibration ledger a later UAT reads against.

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

- Read the `N files scanned` line before the summary: zero files scanned means the path was wrong — the run proves nothing (the scanner exits 2); rerun on the real build dir before reading any count as clean.

Boxes tagged with a scanner rule below have mechanical help; the scan count feeds the box, the box still needs the honest tick.

**The detector runs beside the scanner.** With a browser rung that evaluates JS, inject `assets/detector.js` into the rendered page and run `awardDetector.run({face, archetype})` — computed-style findings feed the tagged boxes below (`references/detector.md`: injection per rung, floors, tier-2 driving). Same doctrine: the detector catches, it never clears. Its `UNMEASURED: n → driven: m` accounting is binding — `m < n` on any element the design_plan names (the signature, a substrate class, the nav) converts that box to NOT DONE, never to a declared gap. Detector FAILs are fix-only: no prose override clears one.

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
- [ ] Hero H1 lands in the lines the design_plan proved (≤2 committed; 3 is the absolute ceiling and takes a written override) `(detector: H1-LINES)`
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

## Surface roster

The seven surfaces the design_plan committed by catalog name (`award-imperatives.md` roster) — each shipped as committed, or its declared-out reason standing in the design_plan. An unconsidered surface is a gap, never a style choice.

- [ ] **Loader / intro** — shipped as the committed family with its handoff beat, or declared out; the handoff verified in the browser — the fold behind the curtain or counter is already composed when it lifts (`ingredients/preloaders.md`)
- [ ] **Navigation** — the committed pattern shipped and driven (`navigation-patterns.md`)
- [ ] **Cursor** — the committed decision shipped: system, designed follower, or designed affordance — never a native special-state glyph (archetype Effect palette, Cursor row)
- [ ] **Hero architecture** — the named skeleton shipped with its entrance beats (archetype Page recipe)
- [ ] **Footer moment** — the named footer archetype shipped (`page-anatomy.md`); functional chrome only where declared
- [ ] **Route transitions** — a multi-route build drove one real route change live: the committed family plays, back-button and scroll restoration hold (`ingredients/page-transitions.md`); a single-route build declares out
- [ ] **Sound** — the committed channel behind its unlock gate, or declared out (`ingredients/web-audio.md`)
- [ ] **Medium arbitration anchored** — when the primary verb is a physical action on a world-object: the arbitration is quoted verbatim in the pre-build R1 verdict (a Phase-5 paste is retroactive fiction) AND Assessor B's declared-vs-code check confirms the shipped code carries the arbitrated medium's fingerprint; this box is never self-ticked alone (`signature-invention.md`, `audit-rubric.md`)

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
- [ ] Custom `:focus-visible` on every interactive element — designed, never the browser-default ring, and keyboard-only: a mouse click or tap never shows an outline (style `:focus-visible`, never a `:focus` ring that fires on click); inputs take a designed focus state in the committed accent (a border/underline shift, never the OS blue); skip link present; no `outline: none` without a visible replacement `(scanner: OUTLINE-NONE)`; the ring appears instantly — never animated in
- [ ] Semantic landmarks (`header/nav/main/footer`), exactly one `<h1>` per page, ordered headings `(scanner: H1-COUNT, MAIN-LANDMARK)`
- [ ] Touch targets ≥ 44×44 on mobile, measured at **every** breakpoint — a control whose text label is hidden at a width (icon-only below a breakpoint) still meets the target *there*, not just at its desktop rest size; a hit area shrunk under 24×24 by a `display:none` label is a fail even when the desktop control passed; `touch-action: manipulation` on tap targets `(detector: TAP-TARGET)`
- [ ] WCAG AA contrast in every state — including button text vs button background (no white-on-white CTA), form placeholders, focus rings, glassmorphic surfaces `(detector: CONTRAST)`
- [ ] Non-text UI holds 3:1 — icons, input borders, accent-on-surface, focus indicators (WCAG 1.4.11), on top of the AA text checks
- [ ] Async feedback is announced — toasts and validation errors carry `aria-live="polite"` (or `role="status"`); a silent visual toast is invisible to screen readers
- [ ] Every color and font value resolves to a named token (`var(--…)` / `@theme`) — an inline hex mid-file is drift (the mechanical token-drift, OKLCH/rem, native-control, and cursor checks live in §9)
- [ ] No horizontal scroll at any width 320–1920: grid image tracks use `minmax(0, 1fr)`, display headlines carry `overflow-wrap: anywhere`, page clipping uses `overflow-x: clip` (never `hidden` — it kills `position: sticky`) `(detector: H-OVERFLOW)`
- [ ] `prefers-reduced-motion` branch exists and swaps motion for opacity `(scanner: REDUCED-MOTION)`
- [ ] **Fill / overlay clip** — every animated fill, sheen, or reveal inside a shaped container clips to its shape (`overflow: hidden` or `clip-path` on the clip parent), and every full-bleed / negative-`inset` decorative layer clips to its bound; `scaleX` fills on rounded shapes are ruled out in favor of `translateX` / `clip-path`. Verified in the browser at §8 (hover→leave), where the spill actually shows
- [ ] **No-JS floor** — a JS-disabled render shows every section's content: initial hidden states applied via JS-added classes only, never in base CSS; canvas/3D heroes carry a static fallback `(scanner: NOJS-HIDDEN)`
- [ ] `min-h-[100dvh]` / `dvh` units — zero `h-screen` / bare `100vh` heroes `(scanner: H-SCREEN)`
- [ ] Zero `window.addEventListener('scroll')` — ScrollTrigger, `useScroll`, IntersectionObserver, or CSS scroll-driven only `(scanner: SCROLL-LISTENER)`
- [ ] Zero ScrollTrigger debug markers in shipped code `(scanner: MARKERS)`
- [ ] Every `<img>` has explicit dimensions and an `alt` `(scanner: IMG-ALT, IMG-DIMENSIONS)` `(detector: IMG-BROKEN)`
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
- [ ] **The page answers the desire arc** — why this exists (the belief), for whom, who is there, what makes it exceptional, why come now — answered in the content with named sections behind them, never implied by tone; and the hero leads with the promise (where it takes you), never the category description `(ref: anti-patterns.md)`
- [ ] Every data visual decodes at a glance — marks self-evident in context, or named by a one-line legend; the loop screenshot is the test (a stranger can say what each mark is); a drawn in-world object passes the same test — its whole real anatomy, in one glance (a barbell has both sleeves)
- [ ] Numbers are real, or explicitly labeled as mock — no invented spec-precision
- [ ] Zero lorem ipsum `(scanner: LOREM)`; zero scroll cues ("Scroll to explore", bouncing chevrons) `(scanner: SCROLL-CUE)`
- [ ] No AI copy clichés in site copy (Elevate, Seamless, Unleash, Next-Gen, Delve) `(scanner: CLICHE-COPY)`
- [ ] Content realism holds: no identical dates across posts, no duplicate avatars across different names, no dead `#` links `(scanner: DEADLINK)`, the nav marks the active state
- [ ] **Specificity floor** — every headline and subhead carries ≥1 concrete from the build's world (a name, count, place, material, gesture, refusal); category-words-only fails (`copy-recipes.md`)
- [ ] **Voice formula named** — the DESIGN.md names the voice formula (person, length habit, punctuation, refusals) and every visible string conforms to it
- [ ] **No exemplar reuse** — no quoted catalog string ships verbatim `(scanner: QUOTED-EXEMPLAR)`

## 7. Truth & assets

- [ ] Every heavy layer (GSAP, Three/R3F, Lenis, View Transitions, Web Audio) cites its Phase 3 source — skill or docs, named — and carries one retrieved **freshness token** (the layer's current version, or one recently-changed API fact); a citation with no checkable token is an undeclared rung-skip, cheap to write and never fetched
- [ ] Heavy layers are used *well*, not just cited — the WebGL scene runs a physical material + HDRI environment (never a primitive on flat lights), the motion layer uses the sourced GSAP/official-skill path; "sourced but low-effort" is a fidelity fail `(ref: ingredients/web3d-for-sites.md)`
- [ ] Assets follow the acquisition protocol (generate → curated stock → seed → honest placeholder); no stock **hotlinks** — a downloaded, optimized, graded curated pick is fine, a live `images.unsplash.com` src is not `(scanner: UNSPLASH)`; curated-stock slots are flagged in the asset list to replace with commissioned/generated finals
- [ ] Brand logos are real SVG marks (Simple Icons / devicon / official kit) with light + dark variants; logo walls are logos only
- [ ] The rotation stamp is the stylesheet's first line (`/* award-design · … */` — format defined at Phase 4; on first contact with a project this skill didn't build, write it now from the adopted universe) `(scanner: STAMP)`
- [ ] **The world is inhabited** — the asset corpus shows the world's presence in motion (its people, creatures, machines — or the moving element itself, wind through dust), not only its objects and rooms; a genuinely still register declares the exception in the verdict `(ref: anti-patterns.md)`

## 8. Browser proof

- [ ] **The desire read** — a stranger would screenshot the hero and send it to someone; and at least one passage on the page is show-someone spectacular — a sequence a judge would replay (clean everywhere, spectacular nowhere is the structural 6.5). An honest no is not a fix-forward: regenerate the visual concept (Phases 1/4), not the tokens

- [ ] The conformance loop exited clean on every section — both core widths passing in the same iteration; drift left standing at the 5-loop cap is filed below, never silently accepted
- [ ] Full-page screenshots at **375px, 768px, 1440px**, taken and read — one line per screenshot on what it showed; every universe claim visible in the pixels, not just coded — plus a fold check at 1280×800: the hero's essential content (H1, subtext, CTA) sits inside the first viewport
- [ ] Computed `font-family` on display text resolves to the committed face — a silent fallback to a system font is invisible in the code and voids the typography `(detector: FONT-RESOLVE)`
- [ ] The signature interaction driven live: it fires, completes, and holds frame — with Chrome DevTools MCP connected the performance trace is mandatory (signature at 60fps, LCP measured against < 1.5s; a miss is a finding, not a gap; a surface with no per-frame fps readout declares the proxy — a clean trace over the animation window, compositor-only properties); with `dev-browser` only, both numbers go to declared gaps. Every measured number carries its **provenance** — the trace or tool-call reference — because a written "LCP 1.18s" is byte-identical to a measured one; a number with no provenance is an asserted number, and an asserted budget is a fail
- [ ] **Interactive signature driven as a real user** — a pointer / drag / 3D signature driven with a real mouse drag AND a touch drag (not synthetic events, which hide the native-drag-ghost bug): the *object* responds (not the headline), no native drag-ghost, no text selection, `touch-action: none` / `draggable="false"` / `user-select: none` set on the canvas and any poster; and the render reads *premium* against a real product of its category — a primitive-on-flat-lights or a CGI-clocked object is a fidelity fail, and a mechanic that bent the brand's core identity (a NOIRE flacon gone brown) is a concept fail; and it **reads at a glance** — a stranger notices the effect without the hint text, and one so subtle it needs its own label to be found is under-tuned, not restrained `(refs: ingredients/web3d-for-sites.md, signature-invention.md)`
- [ ] **Interactive states driven, hover→leave** — every animated control (CTA fill, nav link, card, magnetic button) driven through hover AND the mouse-leave retract (and focus→blur): the fill/sheen enters and exits inside its shape, no spill on either transition. The retract-frame spill past a `border-radius` is invisible to a static screenshot — it only shows mid-transition
- [ ] **Section seams captured** — the transition between sections screenshotted, not only section centers: no decorative layer (a hero light sweep, an oversized glow, a negative-`inset` band) bleeds across a boundary into the next section — **and a full-bleed image or video grades into its neighbour, never a hard horizontal cut into a flat band** (a crisp rectangle edge where sky meets a flat block is the crude-transition tell; grade it with a `mask-image` or a scrim, `imagery.md`). **The last seam into the footer is checked as deliberately as the first**: a full-bleed image butting a hard edge onto a flat footer band (especially a grey one) grades into the footer's own colour instead
- [ ] **Live substrate — every element responds, perceptibly** — driven (not code-read) at every section, not just the hero: each interactive element (the wordmark, every link, image/figure, card, nav, control, the accent word) carries a state you can *feel* in one coherent vocabulary. A ~3% image scale, a barely-there tint, or a fire-once effect that leaves a static frame is homeopathic — it reads as dead, not restrained; the response must register to a real pointer. The wordmark and the accent word are not exempt. A hover-revealed secondary stays reachable under touch emulation, never trapped behind a fine-pointer hover. **On a press/strike-verb build, the input channel is driven too**: elements sampled by the reviewer from the detector's substrate census — never the builder's shortlist — answer a tap/click with the quiet verb instance, read at peak-hold `(ref: interaction-signatures.md)` `(detector: SUBSTRATE-DEAD)` `(detector: CONTACT-GLOBAL-SQUASH)`
- [ ] **One signature carries the whole scroll** — a recognizable signature behaviour recurs and builds from hero to footer, so the page reads of-a-piece; a loud hero moment over an otherwise inert body is the "dead after the hero" failure, driven and confirmed, not inferred from the code; and at least one signature element travels — persists, accumulates, or progresses across sections — entrance-only echoes are episodes, not a thread `(ref: interaction-signatures.md, signature-invention.md)`
- [ ] **Echoes driven as the mechanic transformed** — each of the design_plan's claimed signature echoes is driven and named in the ledger: the mechanic re-expressed in that surface's own terms (the nav's hover moving the way the hero moves, a figure answering with the hero's physics, the footer re-racking the climax) in ≥2 non-hero sections; a persistent emblem that follows the scroll (chip, rail marker, badge) is presence, never an echo `(ref: interaction-signatures.md)`
- [ ] **The discovery beat, driven fresh** — at rest, hands off from page load: the signature's invitation appears within ~5 s and is *perceptible* (the existing floors apply to the beat itself — a sub-perceptible impulse or insider phrasing fails), and a first-time driver can name the gesture within 10 s of arriving; driven and logged, never assumed. The invitation is diegetic — motion, cursor identity, a taught beat that shows the gesture; a written instruction label stays the under-tuned tell. **The beat is also driven under touch emulation** — a fine-pointer-only invitation (a cursor with no touch-side taught beat) fails; the detector's hover census is void under `(hover: none)`, so the touch drive is real taps, never a `run()` read `(ref: signature-invention.md, interaction-signatures.md)`
- [ ] **The scroll texture carries the eye** — the committed Scroll texture (archetype Effect palette row) is driven: something moves the page down between interactions (a marquee, a parallax layer, a scrubbed cross-section transformation, a pinned scrub) — or its declared absence stands in the design_plan with the archetype-canon reason `(ref: interaction-signatures.md)`
- [ ] **The page breathes at rest** — hands off at mid-scroll: at least one declared ambient channel still lives (a drift, a breath, a ticker), `prefers-reduced-motion`-guarded; zero motion between interactions is the embalmed page, however responsive the substrate `(ref: interaction-signatures.md)` `(detector: IDLE-CHANNEL)`
- [ ] **Text emphasis is legible-first** — any scroll-linked text effect emphasizes already-legible copy (dim→bright, never invisible→visible), its finished state is the CSS default, and it does not re-hide on scroll-up; a Firefox / unsupported render still shows fully legible, emphasized text `(ref: text-effects.md)`
- [ ] **Signature text driven responsive** — the signature's own text overlay (readings, captions, kinetic lines, HUD labels) holds at every width 320–1920, mono and overlay strings included; a reading that overflows its column or clips over the hero is a fail the centered desktop frame hides
- [ ] **Hero collision — no absolute affordance over the H1** — at 320–430px (emulated), every absolutely / fixed-positioned hero element (a signature affordance, badge, decoration, the strike / play control) is box-checked against the H1: the two do not overlap. The desktop placement is *reconsidered* for narrow widths — reflowed into the stack or below the standfirst — never left in its desktop position where it clears the headline only by whitespace luck (a clearance that depends on the H1's wrap and the font-load is a fail even when the glyphs happen to miss). Mobile reconsidered, not the desktop layout shrunk
- [ ] **Overlay menu toggle** — the full-screen menu, opened and closed live: icon-only hamburger ↔ cross (zero visible "MENU"/"CLOSE" text — the name lives in `aria-label`), the cross rendered at the exact point of the hamburger so opening without moving the mouse leaves the pointer on the close, each state swap carried by a real transition and a substrate response; `Esc` closes, focus returns to the trigger, body scroll locks (`navigation-patterns.md`)
- [ ] **Drawer floor — every link driven, with the drawer open** — the overlay opened, then EVERY link hovered/tapped: each answers in the substrate vocabulary above the floors, the open is staggered; the detector re-runs with the drawer OPEN so its links join the census and the UNMEASURED accounting (a rest-state run misses them by design); the toggle-only drive is insufficient (`navigation-patterns.md`, `references/detector.md`)
- [ ] **Wordmark home behavior** — driven: mid-scroll on the homepage the wordmark smooth-scrolls to top with no `#fragment` appearing in the URL; on an inner page it navigates home; already at top it reloads; the footer back-to-top scrolls by script under the same rule (`navigation-patterns.md`)
- [ ] **Brand mark + favicon real** — the logo is a designed SVG/PNG glyph or a clean typographic wordmark (no random dot / status-tick), the *same* mark drives the favicon / `icon.svg`, both verified rendered in the browser (`imagery.md`)
- [ ] **Modern-CSS-degraded render** — beyond the no-JS floor: a scroll-timeline / `@supports`-unsupported render checked, so no `animation: … both` snaps to its end state and obscures content — the class of bug where a scroll-linked scrim darkens the whole page, or a reveal stays hidden, on a browser without the timeline. Every scroll-driven opacity/scrim animation is `@supports (animation-timeline: …)`-guarded, with the safe state as the base an unsupported browser holds
- [ ] **Motion model — content persists, décor reverses** — content reveals (headings, copy, cards) fire once and STAY on scroll-up; scroll a section past, then back up — the copy does not fade out (re-hiding content is the NN/g failure). Decorative / scrubbed motion (parallax, curtain-on-image, pinned video) is reversible scroll-linked and never hides content. A reversible content reveal is allowed only where the DESIGN.md declares it, `cover`-phase-ranged `(refs: motion-palette.md)`
- [ ] **Nav holds on scroll-stop** — flick down (bar hides), stop, and let a smooth-scroll layer settle: the bar stays hidden, it does not flash back at rest; scroll up past `SHOW_TOL` and it returns. A bar that reappears every time the scroll stops is the settle-frame bug `(ref: navigation-patterns.md gotcha 5)`
- [ ] Console clean at every width

Full-page captures never fire scroll-gated reveals (IntersectionObserver sees no scroll) and render fixed canvases at y=0 — scroll-verify those sections or substitute viewport-frame captures at key positions, and declare the substitution. Sub-500px widths need device *emulation* — a desktop window silently floors its width and verifies the wrong layout.

No browser tooling on the harness → this section's boxes convert to **declared gaps** in the verdict (Tooling gaps field), each with the code-level fallback noted — and the field carries the **verbatim failed probe** (the ToolSearch or `command -v` output), never a bare claim. Gaps cap the status: with this section dark the ceiling is **READY-UNVERIFIED** (the label travels verbatim into the ship message), and a design_plan that committed an interactive signature caps at **NOT DONE — unverified render**. Falsely ticking a browser box is worse than declaring the gap; declaring a gap the harness could have closed is the same fail.

## 9. Code-craft review

The final mechanical code pass (`code-review.md`), run across the shipped CSS/JS/HTML — it enforces adoption of the modern-web baseline (`modern-web-baseline.md`) and bans the tells. It **overrides the DESIGN.md** — a spec that prescribes a tell (a native control, a `not-allowed` cursor) is corrected, not deferred to.

- [ ] **Token-drift / SSOT** — no token value duplicated as a raw literal; no CSS custom property redeclared as a hardcoded JS constant; no token defined and never used; no token value drifting from its DESIGN.md declaration `(detector: TOKEN-CONFORM)`
- [ ] **OKLCH + rem** — opaque authored colour in `oklch()` / relative-color (translucent overlays / borders / scrims may stay `rgb(… / α)`); px only for borders, hairlines, touch-targets; spacing/type on the rem scale, no off-scale literals
- [ ] **Native-control + cursor lint** — zero native `<select>`/checkbox/radio without `appearance: none`; zero `cursor: not-allowed` or any special-state native cursor (`zoom-in/out`, `wait`, `progress`, `help`); zero `:focus` ring firing on mouse click (focus styling is `:focus-visible`, custom; inputs in the committed accent); run against the DESIGN.md too
- [ ] **State-colour commitment** — every colour in a `:hover`/`:focus`/`:active` rule resolves to a token, and a control's state colour is the committed interactive accent, never a paler wash of it (a tint on the button fill while links carry the full accent is the pale-hover fail); the nav bar carries zero `border-bottom` in any state, and its solid surface token is the page ground or the dominant primary (`navigation-patterns.md`, `interaction-signatures.md`) `(detector: NAV-BORDER)`
- [ ] **A11y floor** — contrast computed at each rule's actual font-size (sub-4.5:1 under ~18px fails regardless of a "decorative" note); tap targets measured at each breakpoint (a label hidden below a width can shrink a control under 24×24, and bare text links — footer, contact, inline mailto — are measured too: a 20px-tall link fails the floor); every full-screen overlay sets `inert`/`aria-hidden` on siblings and traps focus, `Esc` returns focus to the trigger
- [ ] **JS lifecycle** — a render loop resumes only when its target is visible AND in-viewport (not on `visibilitychange` alone); every `setTimeout` guarding a visibility/`hidden` toggle is cleared by its inverse action

## Verdict block

Emit this block, filled, as the Phase 5 artifact. `NOT DONE` blocks ship until the listed items clear.

```markdown
## Pre-flight verdict — <build name>

**Scanner:** <N files scanned> · <N> FAIL (<all fixed | K justified below>) · <M> REVIEW (judged)
**Detector:** <N> FAIL (fix-only) · <M> REVIEW · UNMEASURED <n> → driven <m> — or "no JS-evaluating rung"
**Open with:** <command — a module build needs a server; `file://` runs zero JS>
**Boxes:** <ticked>/<total> — every unticked, overridden, or gap box listed by its bold name
**Counts:** eyebrows <n>/<max> · sections <n> · layout families <named, not counted> · marquees <n> · CTA intents <labels listed>
**Ledger:** <sections> sections · <iterations> loops · <captures> capture refs — uniform first-try anomaly: <none | noted>
**Justified overrides:** <rule → one-line, brief-tied justification — or "none">
**Suppressions:** <--allow flag or archetype suppression → justification — or "none">
**Tooling gaps:** <verbatim failed probe → declared gaps — or "none">
**Code-craft:** <per-check one-line counts — the §9 pass>
**Status:** READY | READY-UNVERIFIED — <browser gates dark, label ships with the build> | NOT DONE — <blocking items>
```

Blocking is defined, not felt: any unticked box, filed drift on a make-or-break surface, any fatal-class FAIL (scanner or detector), or `m < n` in the UNMEASURED accounting → NOT DONE. READY requires §8 evidence. Three or more justified overrides — or any override on an axiomatic box — is a named attention item handed to R2, the overrides quoted in the reviewer's input.
