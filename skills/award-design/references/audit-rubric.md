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

- **Anti-anchoring order**: form the design judgment from the rendered evidence (screenshots, driven interactions) FIRST; run `scripts/preflight_scan.py` and read any preflight verdict SECOND. Mechanical findings received early anchor the eye on the countable and blind it to composition — the scan sharpens a judgment, it never seeds one.
- **Evidence, not opinion**: cite selectors, cite values. "The hero uses `linear-gradient(135deg, #a855f7, #ec4899)`" beats "the colors feel AI".
- **Exemplar gap read**: close every audit with three concrete gaps between this build and the archetype's canonical winner (the DNA list in its reference file), each with a fix. Comparative judgment calibrates better than absolute scoring — a gap names what the winner does that this build doesn't.
- **No hedge scores**: 6/10 and 7/10 are different. Pick one. If you can't decide, look harder.
- **Fixes, not observations**: every P0/P1 must include a concrete CSS snippet or content rewrite. "Improve contrast" is not a fix; `color: #595959` is.
- **Don't recommend what you can't verify**: if you haven't checked it, say so rather than guess.
- **Value consistency** (token trace is a bonus, not a prerequisite): every motion duration, shadow, aspect ratio, viewport height, container width, z-index, opacity, and scroll trigger should come from a coherent, reused scale — not ad-hoc one-offs scattered across files. *When a DESIGN.md exists*, each must resolve to one of its namespaces (canonical or extension), and `/design-system audit-extensions` automates that check (full namespace list at [design-system's extended-tokens reference](https://github.com/coroboros/agent-skills/blob/main/skills/design-system/references/extended-tokens.md)). *Without a DESIGN.md*, the bar is internal consistency: a named scale in the stylesheet, no stray magic numbers. Either way, ad-hoc values are the anti-pattern — flag them.

## Relation to `anti-patterns.md`

`anti-patterns.md` is the binary catalog (present/absent). This rubric is the calibrated measurement. In practice: run `anti-patterns.md` first as a quick pre-flight — any axiomatic rejection triggers a stop-and-fix. Then score with this rubric for everything that passes the binary filter. This catalog-first sequencing governs the *self-audit during a build*; in a fresh-context review the anti-anchoring rule above wins — pixels and judgment first, mechanical output (the scanner, a preflight verdict) second.
