---
name: award-design
description: Build award-winning websites (Awwwards SOTD 7.5+, FWA, CSSDA). Recommends the best design archetype for the brief, calibrates atmosphere, and produces a complete DESIGN.md. Applies anti-AI-slop rules and targets real judging criteria. Use when building landing pages, portfolios, product sites, or any web interface that needs to look exceptional — not for dashboards or internal tools.
when_to_use: When starting a new web project that needs a design direction. When the user says "design this", "make it look great", "award-winning", "premium design", or asks for a visual identity. When no DESIGN.md exists and UI work is about to begin. When the user wants to change the entire visual direction of an existing project (not just token tweaks — use /design-system for those).
argument-hint: "[-u <url>] <what to build>"
model: opus
license: MIT
compatibility: "Claude Code CLI (per Agent Skills spec). Graceful degradation in other environments supporting the open standard."
metadata:
  author: coroboros
  sources:
    - awwwards.com
    - thefwa.com
    - cssdesignawards.com
    - github.com/vercel-labs/web-interface-guidelines
    - github.com/google-labs-code/stitch-skills
    - github.com/rohitg00/awesome-claude-design
    - github.com/SawyerHood/dev-browser
    - locomotive.ca
    - activetheory.net
    - resn.co.nz
    - immersive-g.com
    - cuberto.com
---

# Award Design

Build websites that score 8+ on Awwwards. AI-generated designs are immediately recognizable to experienced judges and score poorly — this skill exists to beat that.

## Workflow

1. **Understand the brief**: What is being built? For whom? What must it communicate? What's the one thing someone will remember? If `-u <url>` was passed, read `references/brand-extraction.md` first and reverse-engineer a DESIGN.md observation from the live site — that observation seeds the archetype recommendation in step 2, it doesn't replace the brief.
2. **Recommend an archetype**: Analyze the brief and recommend the single best archetype from the table below. Present it with:
   - The archetype name and its signature trait
   - Why it fits this brief specifically (not generic reasoning)
   - The default Density/Variance/Motion scores
   - **Ask the user to validate before proceeding.** Do not continue until confirmed.
   - If the user wants to explore alternatives, present all 9 archetypes as a compact list:
     - **Minimalist** — extreme whitespace, typography carries everything
     - **Brutalist** — thick borders, flat colors, deliberate anti-polish
     - **Editorial** — serif + sans-serif pairing, magazine grids, pull quotes
     - **Bold / Maximal** — organized chaos, kinetic typography as art
     - **Immersive / Cinematic** — full-screen video, WebGL 3D, dark backgrounds
     - **Experimental** — bespoke, no template, creative coding, mixed media
     - **Corporate Luxury** — quiet sophistication, custom serifs, generous whitespace
     - **Bento / Card** — modular tiles, container queries, self-contained units
     - **Spatial Organic** — dimensional depth, organic shapes, tactile textures
   - The user is free to pick any archetype — the recommendation is guidance, not a constraint.
   - See `references/exemplars.md` for 2–4 real-world brands per archetype. Share 2–3 alongside the recommendation — exemplars travel faster than prose and give the user a concrete "that feel" to react to.
3. **Read archetype reference**: Once the archetype is confirmed, read its reference file from the table below.
4. **Calibrate atmosphere**: Set Density, Variance, and Motion scores using the Atmosphere Calibration table. Adjust ±2 from defaults based on the brief. Present the calibrated scores to the user for validation.
5. **Load foundations**: Read `references/foundations.md` for cross-cutting technical implementation (typography systems, color theory, animation toolkit, performance, UX quality, accessibility).
6. **Produce DESIGN.md**: If the project has no `DESIGN.md`, create one following the Stitch standard (9 sections). This captures all design decisions as tokens for ongoing consistency — include the calibrated atmosphere scores. If the `/design-system` skill is installed, follow its section-by-section guidance and use its example references as templates; otherwise, follow the standard sections listed in the archetype reference files. Every section must be complete — the `/design-system` skill governs this file for all future UI changes, and incomplete sections create token gaps that agents fill with defaults.
7. **Design with intent**: Every visual choice serves communication. One signature unforgettable moment outperforms scattered effects everywhere.
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

## Archetype Selector

| Archetype | Signature | Ideal for | Reference |
|-----------|-----------|-----------|-----------|
| **Minimalist** | Extreme whitespace, 2-3 colors, typography carries everything | SaaS, luxury, architecture, portfolios | `references/minimalist.md` |
| **Brutalist** | Thick borders, flat colors, deliberate anti-polish | Creative agencies, indie tech, streetwear | `references/brutalist.md` |
| **Editorial** | Serif + sans-serif pairing, magazine grids, pull quotes | Media, fashion, cultural institutions | `references/editorial.md` |
| **Bold / Maximal** | Organized chaos, 4-6+ colors, kinetic typography as art | Entertainment, music, Gen Z brands | `references/bold-maximal.md` |
| **Immersive / Cinematic** | Full-screen video, WebGL 3D, dark backgrounds | Automotive, luxury, gaming, museums | `references/immersive-cinematic.md` + `references/production-hardening.md` |
| **Experimental** | Bespoke, no template, creative coding, mixed media | Developer portfolios, art institutions | `references/experimental.md` |
| **Corporate Luxury** | Quiet sophistication, custom serifs, generous whitespace | High-end fashion, hotels, jewelry, wealth | `references/corporate-luxury.md` |
| **Bento / Card** | Modular tiles, container queries, self-contained units | SaaS product pages, feature comparisons | `references/bento-card.md` |
| **Spatial Organic** | Dimensional depth, organic shapes, tactile textures, native APIs | Sustainability brands, post-2025 creative studios | `references/spatial-organic.md` |

**Selection guide**: Match the archetype to the brand's personality, not to what's trending. A luxury hotel should never be brutalist. A creative agency should never be generic minimalist. When in doubt, the brief's tone decides.

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
4. Add animation last — choreograph deliberately, don't scatter. Check Motion score before adding effects
5. The one-interaction test: if you remove all but one animation, which one stays? That's your signature moment
6. Validate: Lighthouse 90+ on Performance and Accessibility, test on mid-range devices
7. If `dev-browser` is available: screenshot hero, mobile viewport, and signature interaction — compare against archetype expectations and iterate
