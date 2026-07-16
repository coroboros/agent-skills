# Audit Rubric

Quantitative scoring rubric review mode (R1/R2 and standalone) applies. Use alongside `anti-patterns.md` — that file gives you the catalog of failures, this one gives you a score you can act on.

Anti-patterns is the binary filter — "did I do X?" The rubric forces calibration — "how well did I do X, 3/10 or 8/10?" A 6/10 on Typography with a 9/10 on Motion ships differently than the reverse. Scoring surfaces what to fix first.

**This rubric is advisory** — the calibrated half of the review pass. It is commentary that points at the next pass — never a pass/fail verdict, and never a self-graded number presented as "shipped at 9/10". The pass/fail decision belongs to the stop-and-fix filter (the axiomatic rejections in `anti-patterns.md` + the countable boxes in `preflight.md` §4, plus tooling thresholds). Invoked standalone by the user, it scores an existing page the same way: a diagnosis, not a certificate.

## When to run this

- At Phase 6 (R2) before ship — before requesting review or submitting to Awwwards/FWA/CSSDA
- When the user says "review this", "audit this page", or "is this award-ready?"
- When iterating after negative feedback and you need a structured comparison

Can also be invoked standalone by the user (without going through the full workflow) to audit an existing page or implementation.

## Categories (scored 0–10)

Each category has anchors at 0, 5, 10. Interpolate honestly — don't inflate to avoid difficult conversations with the user.

### 0. Concept — with veto

The spine itself: is there one world, felt in layout, type, color, motion, and copy?

- **0** — No spine. A literal restatement of the product dressed in tokens. Any competent template could wear this design.
- **5** — Coherent but expected: the direction is what the category invites, executed cleanly. Recognizable as "the obvious answer, done well".
- **10** — One committed world; remove the copy and the design still says what the product is. The signature moment is the world's climax, not an effect bolted on.

**Concept veto:** Concept ≤ 5 caps the overall score at 6.0 — below SOTD, whatever the other categories earn. Polish cannot rescue a templated idea; the fix is Phase 1 (regenerate the spine), never more execution. State the cap explicitly in the output when it fires.

**The desire read opens every review, and it is comparative — never absolute.** Pull up the archetype's canonical winner (`exemplars.md`) and judge the build *beside it*: would a jury pick this over the current Site of the Day, or would you apologize while showing it? "Would a stranger screenshot the hero" is the floor; the bar is "would you be proud to ship this as your best work next to [the winner]". An honest no caps Concept at 5 — the veto fires, and box compliance cannot buy it back. This framing matters because an absolute judgment grades leniently ("this is nice" → 7); only the comparison to the best is strict enough to catch a spec-sheet in costume. The comparison is the *primary* driver of this score, not a closing footnote. With browser tooling, *pull up* means the winner's live URL opened and screenshotted beside the build — a comparison run from `exemplars.md`'s one-line description compares pixels to a remembered sentence, and it is declared in the output as "comparison from description", never presented as the real read.

**The predictability probe (R1):** before reading the universe artifact, the fresh reviewer states the direction it predicts from the category and the two rejected defaults alone; then it reads. A matched prediction means the direction is still a default — Concept caps at 5 and the verdict is OFF-TRACK. The probe is void in a degraded same-context run (the context already knows the universe) — say so instead of performing it.

**The primary-verb check (R1):** state the world's primary verb yourself — the loop the world is built around — then read the artifact: did it choose that verb, or justify the edge-verb swap in writing? An unjustified edge-verb signature is OFF-TRACK (`signature-invention.md`). At R2, the discovery beat is driven fresh: hands off from load, the invitation perceptible within ~5 s, the gesture nameable within 10 s.

**The static and driven reads are both taken, scoped by archetype.** On jury-screenshot archetypes (editorial, corporate-luxury, minimalist, bento) the comparative read includes the fold *at rest* beside the canon's fold — what a jury screenshot sees, interaction weight zero. On interactive-signature builds the static read asks only: is the invitation visible at rest? Both reads are cited in the verdict; neither substitutes for the other.

**The category-headline test:** at R1 and in every review, the hero promise line is read beside the archetype's quoted winner strings — its Page recipe *Copy voice* row and `copy-recipes.md`. Same specificity class (a named place, a count, a material, a refusal), or a headline that would sit unchanged on a rival's site? The latter is the **category headline**: OFF-TRACK, regenerate at the concept, never filed as a gap — a promise any competitor could sign is a concept defect, not a copy edit.

**Copy is inside the desire read, not below it.** A page whose words read as a dev draft — narrating itself ("a feature on…", "set in Bodoni Moda"), over-written into walls of text, or three label layers deep on one section — fails the read however resolved the type and grid are. Craft does not buy back bad copy: a beautiful build with weak copy is a weak build, and a reviewer dazzled by the motion and the tokens who scores the copy as "polish" has mis-weighted it. Read every visible string as strictly as the pixels, and let a copy failure cap the score the way a concept failure does.

**The interaction layer is judged driven, not read.** A `:hover` rule in the CSS is not a response — a response is what the pointer *feels*. Reading that the rule exists is the single mistake that scores a dead site as alive. Drive every interactive element — the wordmark, every link, every figure, every control, the accent word — through hover / focus / leave, and judge two things. **Perceptibility:** a ~3% image scale, a barely-there tint, a fire-once effect that leaves a static frame behind is *homeopathic* — it reads as dead, not as restraint; the response must register to a real pointer. **Carry:** one signature behaviour recurs and builds through the *whole* scroll, not a hero climax over an otherwise inert page. A build that goes still after the hero, or whose responses are too faint to notice, fails the desire read however clean its code and however many `:hover` rules it declares. This is where craft-anchored review inflates worst — the reviewer credits life the user never feels; when in doubt, the honest read is the *lived* one, and the honest score for "gorgeous hero, dead body" is low.

**The placement pass — composition is judged in stills, beside the exemplar.** Driving proves response; it never proves composition — the defect class that ships correct components with misplaced text is visible only in captures judged NEXT TO the canon's frame. Take the standard capture set (hero at rest, each section centered, the footer — at 1440 and 375), put each beside the archetype exemplar's corresponding frame, and hunt six named defects, each measurable in the frame, never felt: **crowding** — two text blocks (a data-strip under a CTA row is the canonical case) separated by less than one `--ad-space` unit / one line-height of the smaller block; **baseline misalignment** — equivalent content across one visual row starting at drifting Y; **stretched meta-line** — a label/meta line spanning its full container or exceeding ~40ch for its class; **orphan label** — a kicker/eyebrow/caption sitting equidistant or nearer the *preceding* block; **text-over-image contrast** — the overlay read at its worst point (the detector's contrast rule covers solid grounds only — this is the eye's row); **dead-zone / sprawl** — a block stretched across columns it doesn't own, or a void more than twice its neighbours' rhythm. One ledger row per capture: capture ref · exemplar ref · six verdicts · fix/filed. At Phase 6, Assessor A regenerates its own placement ledger from fresh captures — never reading the builder's first — and a divergence between the two ledgers is itself a finding. The reviewer emits the ledger and the comparative verdict; it emits no absolute score for composition — the verdict is comparative or it is nothing.

**The premise veto (restraint):** a clever concept must earn each literal prop it invites — a registration line, a table-of-contents nav, a tipped-in card, a masthead rule. Each survives one question or it is cut: "would a real brand at this tier ship this, or is it art-directed cleverness that reads as trying-too-hard?" (`award-imperatives.md`). Props that fail are removed, not polished; if most of them fail, the *premise* is the defect — regenerate at Phase 1. This veto attacks the idea, not its execution, and it is the check a coherence-scored category otherwise misses: a metaphor can be perfectly coherent and still manufacture anti-luxury clutter.

### 1. Hierarchy

How clearly the eye moves from most to least important. Type scale contrast, visual weight, scan path.

- **0** — Everything looks equally important. H1/H2/body separation < 1.3×. No clear primary CTA.
- **5** — Decent scale (1.5–2×) but weight and color don't reinforce it. CTA findable but not magnetic.
- **10** — Scale, weight, and color all compound. Primary action is unmistakable within 2 seconds.

### 2. Spacing

Rhythm discipline. Does the page have a scale or ad-hoc values?

- **0** — More than 8 unique spacing values detected (8, 10, 12, 14, 20, 24, 28, 32, 40, 48…). No discernible base unit.
- **5** — A scale exists (4/8/12/16/24/32) but edges violate it occasionally.
- **10** — Single scale, strictly enforced (e.g., 4 / 8 / 12 / 16 / 24 / 32 / 48 / 64). Vertical rhythm is visible even when you squint. *Bonus when a DESIGN.md exists:* values trace to its `spacing:` namespace, with `containers:` / `heights:` extensions where layout demands — but a no-file build reaches 10 on a self-consistent stylesheet scale alone.

### 3. Typography

Font stack quality, pairing logic, hierarchy precision.

- **0** — Inter or Roboto on every surface. Two generic sans-serifs paired with no reason. Letter-spacing left at default.
- **5** — One distinctive font chosen for display, sensible fallback for body. Hierarchy uses size only.
- **10** — Font pairing earns its place (weight/style contrast, not accidental). Letter-spacing tuned per size. Optical features (`ss01`, `tnum`) applied where they matter.

### 4. Color

Palette coherence, contrast, role clarity.

- **0** — More than one accent competing. Purple-gradient hero. Pure #000/#FFF everywhere. No role assignment (which color is primary? nobody knows).
- **5** — Palette is restrained and roles are implicit. Contrast meets AA. No standout accent moment.
- **10** — Every color has an explicit role (primary, surface, text, accent, semantic). One accent, used as punctuation. Off-blacks and off-whites. Dark mode considered, not bolted on.

### 5. Motion

Purpose, reduced-motion handling, timing precision.

- **0** — Motion everywhere (every element fades in on scroll). Or none at all. `prefers-reduced-motion` not respected. Easing is default `ease`.
- **5** — Motion is restrained but generic — opacity reveals, default easings. Reduced-motion respected.
- **10** — One signature motion moment carries the page. Timing is tuned — deliberate durations, never 0.3s everywhere; easing is chosen and named, not `ease-in-out`; scroll choreography is paced, not uniform. *Bonus when a DESIGN.md exists:* durations trace to `motion.duration-*`, easings to `motion.ease-*`, scroll pacing to `scrollTriggers.*` — a no-file build reaches 10 on consistent, named CSS values alone.

### 6. Accessibility

WCAG AA baseline + interaction details.

- **0** — Text fails contrast in the footer or on hover states. No focus-visible styles. Touch targets under 40px on mobile. No skip link.
- **5** — Core text meets AA. Focus states exist but are browser defaults. Touch targets mostly OK.
- **10** — AA everywhere including hover/disabled. `:focus-visible` is custom and visible. Skip link present. Semantic HTML (no `<div>`-button soup). `aria-hidden` on decorative SVG. Touch targets ≥ 44×44.

### 7. Anti-slop

Composite check against `anti-patterns.md`. Score inverts — fewer AI-tells = higher score.

- **0** — 5+ AI tells present (purple gradient + Inter + centered hero + 3 equal cards + generic names). Reads as ChatGPT output.
- **5** — 1–2 AI tells slipped through (maybe Inter, maybe a fake round number). Fixable in a pass.
- **10** — Zero axiomatic rejections violated. No template shapes. Content feels real.

## Usability — Nielsen's 10 heuristics (0–4 each)

Usability is 30% of the Awwwards score and the bulk of what `review` mode checks on a live site. Score each heuristic 0 (absent) to 4 (exemplary); a marketing site rarely needs all ten at 4, but a 0 or 1 on a load-bearing one is a stop-and-fix.

1. **Visibility of system status** — loading, hover, active, submitted states are always shown; nothing leaves the user guessing.
2. **Match to the real world** — language and metaphors fit the audience; no internal jargon.
3. **User control & freedom** — back, undo, escape from modals/menus; no scroll-hijack trap.
4. **Consistency & standards** — one pattern per action; links navigate, buttons act; platform conventions held.
5. **Error prevention** — forms guard against mistakes before they happen (input types, inline validation).
6. **Recognition over recall** — options are visible; the user never memorizes across steps.
7. **Flexibility & efficiency** — keyboard paths, deep-linkable state, shortcuts for repeat users.
8. **Aesthetic & minimalist design** — every element earns its place; no decoration competing with the signature.
9. **Error recovery** — clear, inline, human error messages with a way forward.
10. **Help & documentation** — discoverable when the task needs it; never required for the happy path.

Feed the total into the Accessibility read above and into the `review` verdict, citing an example per low score.

## Cognitive load (quick pass)

Score alongside the heuristics: one primary action per screen zone; navigation ≤ 5 top-level items; pricing ≤ 3 tiers; a first-time visitor can say what the product is, for whom, and what to do next within 10 seconds of the hero; no zone asks the eye to track more than ~4 simultaneous elements (working-memory ceiling). A miss here is a P1 with a named fix.

## Output format

Present results as a compact scored audit.

```markdown
# Design Audit — <page or URL>

## Scores
| Category | Score | Verdict |
|---|---|---|
| Concept | 7/10 | One world, felt in type and motion; second-read detail thin |
| Hierarchy | 7/10 | H1/H2 separation tight; weight contrast works |
| Spacing | 5/10 | Scale drifts — 10px and 14px appear |
| Typography | 8/10 | Good pairing; body letter-spacing untuned |
| Color | 6/10 | Accent appears twice per viewport |
| Motion | 4/10 | Every section fades; no signature moment |
| Accessibility | 7/10 | Focus-visible missing on links |
| Anti-slop | 9/10 | Minor: one stock-feeling headline |

**Overall: 6.6/10 — Honorable Mention range. SOTD needs 7.5+.**
*(Overall = the mean of the eight category scores, then the concept veto applies: Concept ≤ 5 caps the line at 6.0 — when it fires, state it here explicitly.)*

## Top Issues

### P0 — Motion lacks a signature moment (4/10)
Every section has `opacity: 0 → 1` fade on scroll. No hierarchy in motion.
Fix: kill all but one. Choose the hero product reveal as the signature. Everything else is instant or transform-only.

### P0 — Spacing scale drifts
Found values: 8, 10, 12, 14, 20, 24, 28, 32, 48. 10 and 14 are violations.
Fix: lock to `4 / 8 / 12 / 16 / 24 / 32 / 48 / 64`. Replace offenders.

### P1 — Accent used twice per viewport
Terracotta CTA + terracotta icon in the same hero. One accent moment per viewport is the rule.
Fix: keep the CTA terracotta, demote the icon to `--text-secondary`.

### P1 — Focus-visible defaults
Links fall back to browser focus ring.
Fix: `:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }`

## Punch List (ordered by impact × effort)
1. [P0] Kill secondary scroll fades — 20 min
2. [P0] Spacing scale lock — 1 hour
3. [P1] Double-accent cleanup — 10 min
4. [P1] Focus-visible styles — 15 min
```

## Rules when running the audit

- **Anti-anchoring order**: form the design judgment from the rendered evidence (screenshots, driven interactions) FIRST; run `scripts/preflight_scan.py` and read any preflight verdict SECOND. Mechanical findings received early anchor the eye on the countable and blind it to composition — the scan sharpens a judgment, it never seeds one. Where the harness has subagents, isolation supersedes ordering: Assessor A judges pixels and driven interactions and never sees the mechanical output; Assessor B reads only the scanner, detector, and verdict; the parent synthesizes (SKILL.md Phase 6). The ordering rule is the labeled degraded form, not an equivalent. Assessor B verifies claims against artifacts, never the run's narration — and where the DESIGN.md carries a medium arbitration, B runs the **declared-vs-code check**: the arbitrated medium leaves a fingerprint the shipped code must carry (a scene → a canvas/WebGL layer or `.glb`; scrubbed real media → the video and its scrub handler); bare CSS transforms under a scene arbitration mean the arbitration is fiction — NOT DONE, not a note. **B's fingerprint is a presence gate, not the liveness clear**: a `<canvas>` with a `getContext('webgl')` call, or a `<video>`, proves the medium is *present*, not that it *renders and responds* — a token canvas that clears one frame, or a decorative particle canvas re-labelled "the scene," passes the code-read while the world stays dead. The liveness clear is Assessor A's driven medium box (`preflight.md` §8) — canvas and video pixels are invisible to computed style, so only the driven eye owns it; B confirms presence, A confirms life, and B's read alone never clears the medium.
- **Archetype is reviewer-supplied, never read from the build's stamp**: the fresh-context assessor derives the archetype from the brief / DESIGN.md and passes it to `scripts/preflight_scan.py --archetype` and `awardDetector.run({archetype})` (both accept it). The CSS rotation stamp is builder-written and, being a CSS comment, is invisible to the detector's CSSOM read anyway — so it is never the archetype source for the audit; the scanner's `STAMP-ARCHETYPE-MISMATCH` flags when the stamp's archetype disagrees with the reviewer's, catching a mis-stamped or mis-selected archetype rather than obeying it. Never let the audited artifact choose whether its own archetype-scoped checks run.
- **R1 refutes the medium's ambition, not only the spine**: for an immersive-cinematic / experimental brief, a committed medium that is static display (a photo procession fading in on scroll, décor over a static layout) is a **medium-ambition failure** — refused at concept and regenerated, quoted in the pre-build R1 verdict, exactly as a category spine is. A gorgeous concept over a slideshow medium fails R1 on the medium; the rendered/scrubbed/driven world is committed at concept or the spine does not pass.
- **Evidence, not opinion**: cite selectors, cite values. "The hero uses `linear-gradient(135deg, #a855f7, #ec4899)`" beats "the colors feel AI".
- **Exemplar gap read (primary, not a closer)**: the review *opens* by pulling up the archetype's canonical winner (`exemplars.md`) and anchoring the Concept and desire scores against it, then *closes* with three concrete gaps between this build and that winner, each with a fix. Comparative judgment stays strict where absolute scoring inflates — a gap names what the winner does that this build doesn't. This comparison is the strictness the concept and desire vetoes depend on.
- **Award-imperatives check**: verify the transverse gates in `award-imperatives.md` — a named signature interaction, a real navigation pattern (never "no nav"), smooth-scroll narrative, `clip-path` image reveals, micro-interactions, measured performance budget (LCP/CLS/INP/weight/fps), AVIF/WebP, mobile reconsidered. A missing imperative is a named P0/P1 with its fix, not a silent pass.
- **No hedge scores**: 6/10 and 7/10 are different. Pick one. If you can't decide, look harder.
- **Fixes, not observations**: every P0/P1 must include a concrete CSS snippet or content rewrite. "Improve contrast" is not a fix; `color: #595959` is.
- **Don't recommend what you can't verify**: if you haven't checked it, say so rather than guess.
- **Value consistency** (token trace is a bonus, not a prerequisite): every motion duration, shadow, aspect ratio, viewport height, container width, z-index, opacity, and scroll trigger should come from a coherent, reused scale — not ad-hoc one-offs scattered across files. *When a DESIGN.md exists*, each must resolve to one of its namespaces (canonical or extension), and `/design-system audit-extensions` automates that check (full namespace list at [design-system's extended-tokens reference](https://github.com/coroboros/agent-skills/blob/main/skills/design-system/references/extended-tokens.md)). *Without a DESIGN.md*, the bar is internal consistency: a named scale in the stylesheet, no stray magic numbers. Either way, ad-hoc values are the anti-pattern — flag them.

## Relation to `anti-patterns.md`

`anti-patterns.md` is the binary catalog (present/absent). This rubric is the calibrated measurement. In practice: run `anti-patterns.md` first as a quick pre-flight — any axiomatic rejection triggers a stop-and-fix. Then score with this rubric for everything that passes the binary filter. This catalog-first sequencing governs the *self-audit during a build*; in a fresh-context review the anti-anchoring rule above wins — pixels and judgment first, mechanical output (the scanner, a preflight verdict) second.
