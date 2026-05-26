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

### Phase 1 — Discovery

Intake the brief: what is being built, for whom, what must it communicate, what's the one thing someone will remember? If `-u <url>` was passed, read `references/brand-extraction.md` first and reverse-engineer a DESIGN.md observation from the live site (it seeds the archetype recommendation; it does not replace the brief). If the URL is the user's own legacy site and the intent is "upgrade without rebuilding", switch to `references/retrofit.md` for the seven-step priority order (font swap → color → hover/active → layout → component swap → empty/error/loading → typography polish).

Recommend the single best archetype from the *Archetype Selector* table — product of four independent picks (**archetype × expression × atmosphere band × signature-moment type**, treating all four as variables prevents the canonical AI same-output failure). Present the archetype's DNA + signature trait + named expression matching the brief, why-this-fit reasoning, default Density/Variance/Motion scores, and 2-3 real-world exemplars from `references/exemplars.md`. **Ask the user to validate before proceeding.** The user can pick any archetype — the recommendation is guidance, not a constraint.

### Phase 2 — Decision

Once the archetype is confirmed, read its reference file from the *Archetype Selector* table. Calibrate atmosphere on three axes (1-10): **Density** (Gallery airy → Cockpit dense), **Variance** (Predictable → Artsy chaotic), **Motion** (Static → Cinematic) — adjust ±2 from the archetype's defaults based on the brief. Defaults per archetype + dial-to-CSS heuristics: `references/atmosphere-calibration.md`. Present calibrated scores for validation. Load `references/foundations.md` for cross-cutting technical implementation (typography, color, animation, performance, UX quality, accessibility).

**Mid-project changes:** to switch archetype after selection, recalibrate atmosphere and regenerate DESIGN.md from the new archetype's foundations (token interconnections forbid patching the old file). For hybrid briefs that refuse a single archetype, read `references/remixing.md` — arbitration framework (parent DNA percentage, 7 rules per dimension, identity declaration) keeps the remix coherent rather than blended. Default is still to pick one archetype.

### Phase 3 — Tokens

Before drafting DESIGN.md content, output a five-bullet **pre-plan** (brief restated, archetype + signature expression + why-this-fit, calibrated atmosphere scores Density / Variance / Motion, signature moment intent — the one unforgettable interaction, photography + copy register). If it doesn't ring true, restart from Phase 1 rather than drafting tokens that won't hold up.

Produce DESIGN.md per the [Google DESIGN.md open standard](https://github.com/google-labs-code/design.md) — YAML frontmatter with canonical 5 namespaces (`colors`, `typography`, `rounded`, `spacing`, `components`) plus extension namespaces (`motion`, `shadows`, `aspectRatios`, `heights`, `containers`, `breakpoints`, `zIndex`, `borderWidths`, `opacity`, `scrollTriggers`) and eight ordered prose sections (Overview, Colors, Typography, Layout, Elevation & Depth, Shapes, Components, Do's and Don'ts). Components bind ONLY to the 8 canonical property tokens (`backgroundColor`, `textColor`, `typography`, `rounded`, `padding`, `size`, `height`, `width`) — extension tokens are referenced from prose only, never as `components:` keys (empirical lint-failure mode). Two-stage validation: `/design-system audit DESIGN.md` (broken-ref + contrast — fall back to `npx @google/design.md lint` if absent) and `/design-system audit-extensions DESIGN.md` (bidirectional drift between YAML extensions, prose, and the `globals.css` `@theme` mirror). Legacy Stitch 9-section file → recommend `/design-system migrate <path>` first. Full spec: `references/design-md-anatomy.md`. Cross-skill extension convention: `skills/design-system/references/extended-tokens.md`.

Apply premium components (`references/premium-patterns.md`) — Doppelrand nested cards, Button-in-Button trailing icons, eyebrow tags, hero 2-line iron rule, mobile-collapse mandates, Liquid Glass Refraction, Perpetual Micro-Interactions when Motion ≥ 5. For multi-section pages, apply composition variety mandates from `references/foundations.md` (≥3 composition anchors, varied background mode per section, CTA shape varied at least once, mixed section ambition). Push at least three axes beyond the generic SaaS template — if the design could pass for default Tailwind output, escalate.

### Phase 4 — Production

When implementation touches video, scroll-driven cinematic reveals, or full-screen heroes on mobile, read `references/production-hardening.md` (viewport units, autoplay belt-and-suspenders, fail-safe reveal logic, proportional layout, iOS Safari quirks). Skip if desktop-only with no video or scroll choreography.

Validate against `references/anti-patterns.md` (axiomatic rejections → AI tells → performance failures → UX) and `references/foundations.md` UX Quality + Accessibility sections. For a calibrated score with an actionable punch list, run `references/audit-rubric.md` (7 categories, 0-10 each, P0/P1 fixes with CSS snippets). Verify against the *Judging Criteria* below.

**Visual review** *(optional)*: if `dev-browser` CLI is available, screenshot key states (hero, mobile, signature interaction, dark mode) and iterate. Install from `https://github.com/SawyerHood/dev-browser` if absent — visual verification catches issues code review alone misses.

## DESIGN.md anatomy

The DESIGN.md produced by Phase 3 carries content across two layers — YAML frontmatter for tokens (canonical 5 + 10 extension namespaces) and eight ordered prose sections for narrative and intent. Full spec — namespace types, prose-section mapping, minimal valid fragment, `@theme` mirror: `references/design-md-anatomy.md`.

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

After selecting an archetype, calibrate atmosphere on three axes (1-10): **Density** (Gallery airy → Cockpit dense), **Variance** (Predictable → Artsy chaotic), **Motion** (Static → Cinematic). Defaults per archetype + dial-to-CSS heuristics: `references/atmosphere-calibration.md`.

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
