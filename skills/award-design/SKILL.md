---
name: award-design
description: Build award-winning websites (Awwwards SOTD 7.5+, FWA, CSSDA). Recommends the best design archetype for the brief, calibrates atmosphere, and produces a complete DESIGN.md. Applies anti-AI-slop rules and targets real judging criteria. Use when building landing pages, portfolios, product sites, or any web interface that needs to look exceptional — not for dashboards or internal tools.
when_to_use: When starting a new web project that needs a design direction. When the user says "design this", "make it look great", "award-winning", "premium design", or asks for a visual identity. When no DESIGN.md exists and UI work is about to begin. When the user wants to change the entire visual direction of an existing project (not just token tweaks — use `/design-system` for those). For empty directories, run `/scaffold` first to bootstrap the project stack, then return here.
argument-hint: "[-u <url>] <what to build>"
model: opus
license: MIT
compatibility: "Claude Code CLI (per Agent Skills spec). Graceful degradation in other environments supporting the open standard."
metadata:
  author: coroboros
  sources:
    - github.com/coroboros/research/blob/main/articles/award-winning-websites-2025-2030/award-winning-websites-2025-2030.md
    - github.com/Leonxlnx/taste-skill
    - github.com/rohitg00/awesome-claude-design
    - github.com/google-labs-code/design.md
    - github.com/google-labs-code/stitch-skills
    - github.com/vercel-labs/web-interface-guidelines
    - github.com/SawyerHood/dev-browser
---

# Award Design

<!-- canonical:writing-rules:start -->
## Important — Writing rules

These rules govern every prose artifact this skill emits — READMEs, CHANGELOGs, commit messages, PR bodies, release notes, doc paragraphs, non-trivial comments. Apply them at draft time, verify before output.

- Match the surrounding style — punctuation, capitalization, backtick conventions, em-dash vs parens, bullet style.
- Every sentence changes the reader's understanding. Cut it otherwise.
- Front-load the verb — "Creates", not "This helps you create".
- Concrete over abstract. Lists for ≥3 enumerable items.
- Assert positively. Reserve negation for real constraints (`NEVER commit secrets`).
- No marketing words: powerful, robust, seamlessly, leverage, unlock, comprehensive, delightful.
- No AI tells: delve, tapestry, intricate, pivotal, testament, underscore, crucial, garner, showcase, additionally, moreover, furthermore, indeed.
- After drafting English prose, invoke `/humanize-en` if installed.
<!-- canonical:writing-rules:end -->

Build websites that score 8+ on Awwwards. AI-generated designs are immediately recognizable to experienced judges and score poorly — this skill exists to beat that.

## Workflow

1. **Understand the brief**: What is being built? For whom? What must it communicate? What's the one thing someone will remember?
   - If `-u <url>` was passed, read `references/brand-extraction.md` first and reverse-engineer a DESIGN.md observation from the live site — that observation seeds the archetype recommendation in step 2, it doesn't replace the brief.
   - If the URL is the user's own legacy site and the intent is "upgrade without rebuilding", read `references/retrofit.md` instead — it carries the seven-step priority order (font swap → color cleanup → hover/active → layout → component replacement → empty/error/loading → typography polish) for targeted lift without re-architecting.
2. **Recommend an archetype**: Analyze the brief and recommend the single best archetype from the table below. The recommendation is the product of four independent picks — **archetype × expression × atmosphere band × signature-moment type**. Treating all four as variables (not defaults) is what prevents the canonical AI same-output failure. Present it with:
   - The archetype name and its signature trait — defined by DNA, not by a single style lock. Each archetype carries 2–4 named common expressions in its reference file (e.g., Immersive splits into cinematic-dark / editorial-portrait / daylight-automotive). The user picks the expression that matches the brief.
   - Why it fits this brief specifically (not generic reasoning)
   - The default Density/Variance/Motion scores
   - **Ask the user to validate before proceeding.** Do not continue until confirmed.
   - If the user wants to explore alternatives, present all 9 archetypes as a compact list:
     - **Minimalist** — extreme whitespace, typography carries everything
     - **Brutalist** — typography is the design, deliberate anti-polish
     - **Editorial** — serif + sans-serif pairing, magazine grids, pull quotes
     - **Bold / Maximal** — organized chaos, kinetic typography as art
     - **Immersive / Cinematic** — full-screen video, WebGL 3D, scroll as narrative
     - **Experimental** — bespoke navigation metaphor, creative coding, no template
     - **Corporate Luxury** — quiet sophistication, custom serifs, generous whitespace
     - **Bento / Card** — modular asymmetric tiles, self-contained units
     - **Spatial Organic** — dimensional depth, organic shapes, tactile textures *(forward archetype — trend-credentialed, no SOTM-tier reference yet)*
   - The user is free to pick any archetype — the recommendation is guidance, not a constraint.
   - See `references/exemplars.md` for 2–4 real-world brands per archetype. Share 2–3 alongside the recommendation — exemplars travel faster than prose and give the user a concrete "that feel" to react to.
3. **Read archetype reference**: Once the archetype is confirmed, read its reference file from the table below.
4. **Calibrate atmosphere**: Set Density, Variance, and Motion scores using the Atmosphere Calibration table. Adjust ±2 from defaults based on the brief. Present the calibrated scores to the user for validation.
5. **Load foundations**: Read `references/foundations.md` for cross-cutting technical implementation (typography systems, color theory, animation toolkit, performance, UX quality, accessibility).
6. **Produce DESIGN.md**: Before drafting any DESIGN.md content, output a five-bullet **pre-plan** — brief restated in one sentence, archetype + signature expression + why-this-fit, calibrated Density/Variance/Motion scores, signature moment intent (the one unforgettable interaction), photography and copy register. The plan is the contract for what follows. If it doesn't ring true, restart from step 1 rather than drafting tokens that won't hold up. Then, if the project has no `DESIGN.md`, create one following the [Google DESIGN.md open standard](https://github.com/google-labs-code/design.md) — YAML frontmatter with design tokens (`colors`, `typography`, `rounded`, `spacing`, `components`) plus eight ordered prose sections (Overview, Colors, Typography, Layout, Elevation & Depth, Shapes, Components, Do's and Don'ts). Record the calibrated atmosphere scores as prose in the Overview section — the spec does not define atmosphere tokens. If the `/design-system` skill is installed, follow its `references/design-md-spec.md` and the example files for shape; otherwise, the sections listed in the archetype reference files cover the same ground. **Extension boundary** — beyond the canonical 5 namespaces, top-level extension namespaces are spec-blessed and required at award-grade register: `motion`, `shadows`, `aspectRatios`, `heights`, `containers`, `breakpoints`, `zIndex`, `borderWidths`, `opacity`, `scrollTriggers` (full namespace × prose-section map below). **Components bind ONLY to the 8 canonical property tokens** (`backgroundColor`, `textColor`, `typography`, `rounded`, `padding`, `size`, `height`, `width`) — extension tokens are referenced canonically in prose, never as `components:` keys (the empirical lint-failure mode). **Two-stage validation pipeline** — both must exit 0 before shipping: (a) `/design-system audit DESIGN.md` (preferred — human-readable report with fix proposals per finding) catches broken token references (`broken-ref`) and contrast violations below WCAG AA; fall back to `npx @google/design.md lint DESIGN.md` if `/design-system` is unavailable; (b) `/design-system audit-extensions DESIGN.md` is the bidirectional drift check between YAML extensions, prose references, and the `globals.css` `@theme` mirror — extensions are preserved-but-unvalidated by the Google CLI, this subcommand closes the loop. If the user hands you an existing legacy DESIGN.md with the Stitch 9-section format, recommend `/design-system migrate <path>` first to port it, then resume. Every applicable section must be complete — the `/design-system` skill governs this file for all future UI changes, and incomplete sections create token gaps that agents fill with defaults. Full extension convention: `skills/design-system/references/extended-tokens.md`.
7. **Design with intent**: Every visual choice serves communication. One signature unforgettable moment outperforms scattered effects everywhere. **Do not ship the first obvious solution** — push at least three axes beyond the generic SaaS template (composition, typography, hero scale, image treatment, section rhythm, framing). If the design could pass for default Tailwind output, escalate. For concrete component techniques (Doppelrand nested architecture, Button-in-Button trailing icons, eyebrow tags, hero 2-line iron rule, mobile-collapse mandates, performance locks for perpetual animation, Liquid Glass Refraction, Inline Typography Images, Perpetual Micro-Interactions when Motion ≥ 5), read `references/premium-patterns.md`. For multi-section pages, also apply the **composition variety mandates** in `references/foundations.md` (≥3 different composition anchors across the page, varied background mode per section, CTA shape varied at least once, mixed section ambition) — uniform per-section treatment reads as templated even when each section is individually strong. These cross-cutting patterns lift Hierarchy and Spacing audit scores by 1–2 points each and apply across archetypes — particularly Corporate Luxury, Spatial Organic, Bento (motion-engine variant), and Bold/Maximal.
8. **Production hardening**: When implementation touches video, scroll-driven cinematic reveals, or full-screen heroes on mobile browsers, read `references/production-hardening.md`. Most patterns are cross-browser (viewport units, scroll-restoration, autoplay belt-and-suspenders, fail-safe reveal logic, proportional layout) with iOS Safari flagged as the sharpest test case. Each section states its scope — genuinely iOS-only rules are marked. Skip if the project is desktop-only with no video or scroll choreography.
9. **Validate**: Read `references/anti-patterns.md` and check the design against it — axiomatic rejections first (any hit is stop-and-fix), then AI tells, performance failures, UX anti-patterns. Cross-check `references/foundations.md` UX Quality and Accessibility sections. For a calibrated score with an actionable punch list, run `references/audit-rubric.md` (7 categories, 0–10 each, P0/P1 fixes with CSS snippets). Verify against the judging criteria below.
10. **Visual review** *(optional)*: If `dev-browser` CLI is available, screenshot key states (hero, mobile, signature interaction, dark mode) and iterate. If not available, suggest installing it from `https://github.com/SawyerHood/dev-browser` — the skill works without it, but visual verification catches issues that code review alone misses.

### Changing archetype mid-project

If the user wants to switch archetypes after initial selection (during design or even after implementation has started):

1. Confirm the new archetype choice
2. Read the new archetype's reference file
3. **Recalibrate atmosphere** — the new archetype has different default scores. Present the recalibrated scores for validation
4. **Regenerate DESIGN.md** — the entire file must be rewritten from the new archetype's foundations. Do not patch the old file — archetype tokens are deeply interconnected
5. If code already exists, flag which components need updating based on the token diff between old and new DESIGN.md

### Combining archetypes (remix)

If the brief refuses to pick a single archetype — "Linear rigor but Anthropic warmth", "Brutalist character for luxury clients", a creative studio serving enterprise — read `references/remixing.md`. It gives an arbitration framework (parent DNA percentage, 7 rules that pick one parent per dimension, one-paragraph identity declaration) so the remix reads as a third coherent brand rather than a blend. Default is still to pick one archetype; reach for a remix only when a single archetype leaves the brief unsatisfied after two attempts.

## DESIGN.md anatomy — token namespaces + prose mapping

The DESIGN.md produced by step 6 carries award-grade content across two layers — YAML frontmatter for tokens, eight ordered prose sections for narrative and intent. Both layers are required; an empty layer makes the file useless to its consumer.

### YAML namespaces

| Type | Namespaces | Validated by Google CLI |
|---|---|---|
| Canonical | `colors`, `typography`, `rounded`, `spacing`, `components` | yes (broken-ref, contrast-ratio, missing-primary, etc.) |
| Extension (preserved) | `motion`, `shadows`, `aspectRatios`, `heights`, `containers`, `breakpoints`, `zIndex`, `borderWidths`, `opacity`, `scrollTriggers` | no (preserved-but-unvalidated per spec); validated by `/design-system audit-extensions` against the `globals.css` `@theme` mirror |

Components bind ONLY to the 8 canonical property tokens — `backgroundColor`, `textColor`, `typography`, `rounded`, `padding`, `size`, `height`, `width`. Extension tokens are referenced from prose only (e.g., `{motion.duration-reveal-slow}`), never as `components:` keys. The closed property-token set is the empirical lint-failure mode.

### Award-grade prose mapping

Every vital narrative element from this skill maps to one of the eight ordered sections — nothing is dropped:

| Award-grade narrative | DESIGN.md section |
|---|---|
| Atmosphere scores (Density / Variance / Motion) | 1. Overview |
| Archetype identity + remix declaration | 1. Overview |
| Signature moment (the one unforgettable interaction) | 1. Overview |
| Photography direction (cinematic / editorial / flat-lay register) | 1. Overview |
| Copy register (tone of voice) | 1. Overview |
| Colour narrative + photography colour guidance | 2. Colors |
| Kinetic typography intent (variable-font behaviour, text-reveal) | 3. Typography |
| Layout grid + responsive strategy | 4. Layout |
| Scroll choreography (scroll-driven reveals, narrative pacing) | 4. Layout (cross-reference `motion.*`, `scrollTriggers.*`) |
| Shadow language + depth narrative | 5. Elevation & Depth (cross-reference `shadows.*`, `borderWidths.*`, `opacity.*`) |
| Geometric / radius language | 6. Shapes |
| Component patterns + variants | 7. Components |
| Micro-interactions (hover / pressed / active states) | 7. Components (variant entries: `button-primary-hover`) |
| Motion philosophy | 7. Components + cross-reference 1. Overview |
| Award-grade rules + AI-tells anti-patterns + production-hardening guardrails | 8. Do's and Don'ts |

Production-hardening implementation guardrails (viewport units, autoplay belt-and-suspenders, iOS Safari quirks) host as one-line testable rules in Do's and Don'ts; full detail stays in `references/production-hardening.md`. Full extension convention: `skills/design-system/references/extended-tokens.md`.

### Minimal valid fragment

Canonical (validated) and extension (preserved-but-unvalidated) namespaces side by side; components stay within the eight property tokens; prose names extensions canonically:

```yaml
colors:
  primary: "#1a1c1e"
  surface: "#f7f5f1"
components:
  modal:
    backgroundColor: "{colors.surface}"   # canonical property token — accepted
    rounded: "{rounded.md}"
    padding: 32px
    # `shadow: "{shadows.lifted}"` would be rejected — `shadow` is not in the 8
    # canonical property tokens; the lint flags unknown component properties.
motion:
  duration-reveal-slow: 1200ms
  ease-standard: cubic-bezier(0.16, 1, 0.3, 1)
shadows:
  lifted: 0 20px 40px -16px rgb(0 0 0 / 0.08)
```

```markdown
## Elevation & Depth

Modals lift on `{shadows.lifted}` — referenced from prose. Reveal motion uses `{motion.duration-reveal-slow}` paced by `{motion.ease-standard}`.
```

The mirror in `globals.css` (auto-generated by `/design-system export tailwind`):

```css
@theme {
  --color-primary: #1a1c1e;
  --color-surface: #f7f5f1;
  --duration-reveal-slow: 1200ms;
  --ease-standard: cubic-bezier(0.16, 1, 0.3, 1);
  --shadow-lifted: 0 20px 40px -16px rgb(0 0 0 / 0.08);
}
```

## Archetype Selector

| Archetype | Canonical reference (article-credentialed) | Signature | Ideal for | Reference |
|-----------|---------|-----------|-----------|-----------|
| **Minimalist** | Terminal Industries (SOTM Sept 2025) | Two to three colors max, typography carries everything | SaaS, luxury, architecture, portfolios | `references/minimalist.md` |
| **Brutalist** | FlowFest 2025 (SOTD July 2025) | Typography is the design, deliberate anti-polish | Creative agencies, indie tech, streetwear, festivals | `references/brutalist.md` |
| **Editorial** | Siena Film Foundation (SOTM April 2025) | Serif + sans-serif pairing, magazine grids, reading-first | Media, fashion, cultural institutions, film foundations | `references/editorial.md` |
| **Bold / Maximal** | Ponpon Mania (SOTM Oct 2025) | Organized chaos, 4–6 saturated colors, kinetic type as art | Entertainment, music, Gen Z brands, comic narratives | `references/bold-maximal.md` |
| **Immersive / Cinematic** | Lando Norris (Site of the Year 2025) | Full-screen 3D / video, scroll as narrative — dark, cream, or daylight | Automotive, luxury, gaming, museums, athlete portfolios | `references/immersive-cinematic.md` + `references/production-hardening.md` |
| **Experimental** | Bruno Simon (SOTM Jan 2026) | Bespoke navigation metaphor, hand-coded primitives | Developer portfolios, art institutions, conferences | `references/experimental.md` |
| **Corporate Luxury** | Cartier WAW 2025 (SOTM Aug 2025) | Quiet sophistication, custom serifs, generous whitespace | High-end fashion, hotels, jewelry, wealth, watchmaking | `references/corporate-luxury.md` |
| **Bento / Card** | Anime.js v4 (SOTM May 2025) | Modular asymmetric tiles, self-contained units | SaaS product pages, feature comparisons, AI products | `references/bento-card.md` |
| **Spatial Organic** | *trend-credentialed (Arc, Granola)* | Dimensional depth, organic shapes, tactile textures, native APIs | Sustainability, wellness, post-2025 creative studios | `references/spatial-organic.md` |

**Each archetype reference is structured as:** DNA (non-negotiable identity, mood-agnostic), Common expressions (2–4 named stacks — pick the one matching brand voice), Typography / Color / Layout / Motion specifics, What makes it award-worthy, Cross-references. The split prevents force-fitting a single style lock onto an archetype that admits multiple valid expressions.

**Selection guide**: Match the archetype to the brand's personality, not to what's trending. A luxury hotel should never be brutalist. A creative agency should never be generic minimalist. When in doubt, the brief's tone decides.

**Brief signal → first-pass routing.** When the brief uses a vocabulary, the first-pass archetype hypothesis is usually one of these. Validate with the user; treat the routing as a starting question, not an answer.

| Brief signal | First-pass archetype |
|---|---|
| "luxury", "high-end", "exclusive", "wealth", "fashion house" | **Corporate Luxury** |
| "minimal", "clean", "restrained", "Notion-like", "Linear-like" | **Minimalist** |
| "editorial", "magazine", "long-form", "publication", "reading-first" | **Editorial** |
| "raw", "indie", "agency with attitude", "anti-polish", "Gumroad" | **Brutalist** |
| "bold", "loud", "saturated", "Gen Z", "music", "comic" | **Bold / Maximal** |
| "cinematic", "video hero", "3D", "scrolltelling", "athlete portfolio" | **Immersive / Cinematic** |
| "bespoke", "creative coding", "no template", "art-directed nav" | **Experimental** |
| "modular", "feature grid", "tiles", "SaaS product page", "AI product" | **Bento / Card** |
| "spatial", "glass", "depth", "organic", "post-grid", "vision-pro feel" | **Spatial Organic** |

**Handoff to design-system**: The DESIGN.md produced by this skill becomes the single source of truth for all future UI work. Once created, the `/design-system` skill governs it — enforcing tokens, handling updates, and preventing drift. This skill (award-design) is for initial creation and complete re-architecting only. Token-level changes (adjust a color, tweak spacing) go through `/design-system`.

### Atmosphere Calibration

After selecting an archetype, calibrate its atmosphere on three axes (1–10). This makes design choices measurable rather than intuitive, and prevents drift during implementation.

| Axis | 1–3 | 4–6 | 7–10 |
|------|-----|-----|------|
| **Density** | Gallery airy — generous whitespace, few elements per viewport | Balanced — clear hierarchy with moderate content | Cockpit dense — information-rich, tight spacing |
| **Variance** | Predictable — symmetric grids, uniform spacing, expected flow | Structured surprise — asymmetric grids, varied rhythm | Artsy chaotic — broken grids, overlapping zones, rule-breaking |
| **Motion** | Static — minimal transitions, opacity-only reveals | Purposeful — scroll-triggered sequences, hover states | Cinematic — continuous animation, parallax depth, WebGL layers |

**Default scores per archetype** (adjust ±2 based on brief):

| Archetype | Density | Variance | Motion |
|-----------|---------|----------|--------|
| Minimalist | 2 | 3 | 3 |
| Brutalist | 4 | 7 | 3 |
| Editorial | 5 | 5 | 4 |
| Bold / Maximal | 6 | 8 | 8 |
| Immersive / Cinematic | 3 | 6 | 9 |
| Experimental | 5 | 9 | 7 |
| Corporate Luxury | 2 | 4 | 5 |
| Bento / Card | 7 | 4 | 4 |
| Spatial Organic | 4 | 6 | 6 |

Use these scores to resolve design ambiguity: "Should this section have more whitespace?" → check Density score. "Should I break the grid here?" → check Variance score. "Does this element need scroll animation?" → check Motion score. Record the final calibrated scores in the project's `DESIGN.md`.

**Dial → CSS heuristics.** Concrete starting points per band; the archetype reference refines them.

- **Density 2-3** → `py-32` to `py-48` section padding (128–192px), 60–75ch reading measure, ample gutters. **Density 7-10** → `py-12` to `py-16` (48–64px), `gap-2` to `gap-4`, monospace numerics with `tabular-nums`.
- **Variance 1-3** → 12-column grid centered, `max-w-screen-xl mx-auto`, symmetric padding. **Variance 7-10** → broken-grid `grid-template-columns: repeat(11, 1fr)` with intentional `grid-row` overlap, off-axis hero, asymmetric image–text pairs.
- **Motion 1-3** → `transition: opacity 0.4s` only; avoid scroll-triggered. **Motion 7-10** → GSAP ScrollTrigger pin/scrub on hero, View Transitions on navigation, perpetual micro-interactions on signature elements (memoized per `premium-patterns.md` performance locks).

## Judging Criteria

Awwwards evaluates: **Design 40%** · **Usability 30%** · **Creativity 20%** · **Content 10%**. Honorable Mention requires 6.5+. SOTD requires ~7.5+.

**What separates 8+ from 6-7:**

- One signature unforgettable interaction (not scattered micro-animations everywhere)
- Mobile **reconsidered**, not just responsive breakpoints bolted on
- Complex visuals that load fast on mid-range devices (LCP < 1.5s)
- Real content with genuine photography — no stock
- Scroll as narrative — content unfolds with purpose and pacing
- Precise animation choreography (timing, easing, sequencing)

**Strategic path**: CSSDA first (most accessible, WOTD > 8.0) → FWA (rewards experimental boldly) → Awwwards (highest bar). Best submission months: Feb-Apr, Sep-Nov.

## Implementation Checklist

After selecting an archetype, calibrating atmosphere, and reading its reference:

1. Establish the design system first (CSS custom properties: typography scale, color palette, spacing tokens)
2. Build mobile-first, then enhance for desktop
3. Apply UX quality rules from foundations (touch targets, safe areas, form behavior, deep-linking)
4. Apply premium component patterns (`premium-patterns.md`) where relevant — Doppelrand for cards, Button-in-Button for primary CTAs, eyebrow tags above section headlines, hero 2-line iron rule for the H1, mobile-collapse mandates for asymmetric layouts above `md`
5. Add animation last — choreograph deliberately, don't scatter. Check Motion score before adding effects. Memoize and isolate any perpetual animations per `premium-patterns.md` performance locks
6. The one-interaction test: if you remove all but one animation, which one stays? That's your signature moment
7. Validate: Lighthouse 90+ on Performance and Accessibility, test on mid-range devices. Mobile viewports 375px / 414px / 768px must hold without horizontal scroll
8. If `dev-browser` is available: screenshot hero, mobile viewport, and signature interaction — compare against archetype expectations and iterate

## Output discipline

DESIGN.md generation is long-form — eight prose sections plus YAML can run thousands of tokens. Two rules prevent silent truncation, the most common way a high-effort plan ships as a half-empty file.

**No placeholder shortcuts.** **NEVER** ship `[remaining sections similar]`, `// ...`, `// TODO`, "for brevity", "and so on", "the rest follows the same pattern", or "let me know if you want to continue". Each of the eight prose sections is either complete or marked paused — there is no in-between. The `/design-system audit` lint catches token-side gaps; the prose-side gap is on you. See `references/anti-patterns.md` *Output discipline* for the full banned-phrase list.

**Continuation marker for split outputs.** When approaching the response token ceiling, finish at a clean section boundary (never mid-section, never mid-token-group) and end with `[PAUSED — N of 8 sections complete. Send "continue" to resume from: <next section name>]`. On `continue`, pick up exactly there — no recap, no rewrite of prior sections, no compression. The marker is the resume contract.
