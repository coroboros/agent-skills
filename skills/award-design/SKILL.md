---
name: award-design
description: Build award-winning websites (Awwwards SOTD 7.5+, FWA, CSSDA). Code-first — ships a built site fast, no DESIGN.md required. Recommends the best archetype for the brief, calibrates atmosphere, commits an inline token block, then builds against real judging criteria with anti-AI-slop rules. Adapts to an existing DESIGN.md when one is present; offers to crystallize one after the build. Use for landing pages, portfolios, product sites, or any web interface that must look exceptional — not for dashboards or internal tools.
when_to_use: When the user wants a website built or designed — "design this", "make it look great", "award-winning", "premium design", "build me a landing page", or asks for a visual identity. Default path needs no DESIGN.md; it builds first and offers to persist tokens after. When a DESIGN.md already exists, award-design adapts to it. When the user wants to change the entire visual direction of a project (not token tweaks — use `/design-system` for those). award-design creates and crystallizes the DESIGN.md; `/design-system` governs it. For empty directories, run `/scaffold` first to bootstrap the stack, then return here.
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

## Extension tokens dependency

For tokens beyond the Google DESIGN.md spec's base five (motion, shadows, aspect ratios, z-index, breakpoints, opacity ramps), the curated namespace list and component-binding rules live in design-system's extended-tokens reference — see [github.com/coroboros/agent-skills/blob/main/skills/design-system/references/extended-tokens.md](https://github.com/coroboros/agent-skills/blob/main/skills/design-system/references/extended-tokens.md). With design-system installed, the file lives at `~/.claude/skills/design-system/references/extended-tokens.md`; read it before committing motion, effects, or extension tokens — whether to the inline token block, or to a DESIGN.md `## Animation` / `## Effects` section on Adapt or Persist. Without `/design-system` installed, the patterns still apply: Google's CLI preserves the YAML namespaces (`motion:`, `breakpoints:`) unchanged.

## Workflow

The deliverable is a built site; a DESIGN.md is optional. No design file is authored before pixels — the inline token block (Phase 3) carries value coherence, and the full eight-section DESIGN.md is opt-in (see *Persist*). The build starts after the brief read and a compact token block, not after a long token file.

**Mode detect — first action.** Check for `DESIGN.md` at the project root:

- **present → Adapt.** Load it as the source of truth, skip archetype selection, build consistent with its tokens — craft applied on top, never re-authored from scratch. Token-level changes (one color, a radius) route to `/design-system`, not here. A legacy Stitch 9-section file (no YAML frontmatter) → `/design-system migrate <path>` first, then Adapt the ported file.
- **absent → Instant (default).** Run the four phases below, then offer *Persist*. At most one optional archetype confirm (Phase 1); under a fast or headless run, take the recommendation and proceed without asking.

### Phase 1 — Discovery

Intake the brief: what is being built, for whom, what must it communicate, what's the one thing someone will remember? If `-u <url>` was passed, read `references/brand-extraction.md` first and reverse-engineer a DESIGN.md observation from the live site (it seeds the archetype recommendation; it does not replace the brief). If the URL is the user's own legacy site and the intent is "upgrade without rebuilding", switch to `references/retrofit.md` for the seven-step priority order (font swap → color → hover/active → layout → component swap → empty/error/loading → typography polish).

Recommend the single best archetype from the *Archetype Selector* table — product of four independent picks (**archetype × expression × atmosphere band × signature-moment type**, treating all four as variables prevents the canonical AI same-output failure). Present the archetype's DNA + signature trait + named expression matching the brief, why-this-fit reasoning, default Density/Variance/Motion scores, and 2-3 real-world exemplars from `references/exemplars.md`. **One optional confirm** — the user can accept, redirect to any archetype, or stay silent; the recommendation is guidance, not a constraint. Under a fast or headless run, take it and move on. This is the only checkpoint before building, and it never blocks the build.

### Phase 2 — Decision

Read the chosen archetype's reference file from the *Archetype Selector* table. Calibrate atmosphere on three axes (1-10): **Density** (Gallery airy → Cockpit dense), **Variance** (Predictable → Artsy chaotic), **Motion** (Static → Cinematic) — adjust ±2 from the archetype's defaults based on the brief. Defaults per archetype + dial-to-CSS heuristics: `references/atmosphere-calibration.md`. Calibrate internally and proceed; surface the scores only if the user asked to steer atmosphere, or fold them into the Phase 1 confirm. Load `references/foundations.md` for cross-cutting technical implementation (typography, color, animation, performance, UX quality, accessibility).

**Mid-project changes:** to switch archetype after selection, recalibrate atmosphere and emit a fresh token block from the new archetype's foundations (token interconnections forbid patching the old set; if a DESIGN.md exists, regenerate it whole rather than patching). For hybrid briefs that refuse a single archetype, read `references/remixing.md` — arbitration framework (parent DNA percentage, 7 rules per dimension, identity declaration) keeps the remix coherent rather than blended. Default is still to pick one archetype.

### Phase 3 — Tokens

Output a five-bullet **pre-plan** (brief restated, archetype + signature expression + why-this-fit, calibrated atmosphere scores Density / Variance / Motion, signature moment intent — the one unforgettable interaction, photography + copy register). If it doesn't ring true, restart from Phase 1 rather than committing tokens that won't hold up.

Commit the pre-plan to an **inline YAML token block** before any JSX — the value-coherence forcing function that keeps color, type, and spacing decisions consistent across every component. It is compact: roles and a scale, not prose sections. Use the [Google DESIGN.md](https://github.com/google-labs-code/design.md) token shape so it drops straight into a DESIGN.md later — canonical 5 namespaces (`colors`, `typography`, `rounded`, `spacing`, `components`) plus only the extension namespaces actually in use from the available set (`motion`, `shadows`, `aspectRatios`, `heights`, `containers`, `breakpoints`, `zIndex`, `borderWidths`, `opacity`, `scrollTriggers`). Components bind ONLY to the 8 canonical property tokens (`backgroundColor`, `textColor`, `typography`, `rounded`, `padding`, `size`, `height`, `width`) — extension tokens are referenced from prose/CSS only, never as `components:` keys (empirical lint-failure mode). The full DESIGN.md (eight ordered prose sections — Overview, Colors, Typography, Layout, Elevation & Depth, Shapes, Components, Do's and Don'ts — wrapped around this YAML) is deferred to *Persist* (opt-in), or already present in *Adapt* mode. Whenever a DESIGN.md exists, validate it: `/design-system audit <path>` (broken-ref + contrast — fall back to `npx @google/design.md lint` if absent) and `/design-system audit-extensions <path>` (bidirectional drift between YAML extensions, prose, and the `globals.css` `@theme` mirror); a legacy Stitch 9-section file → `/design-system migrate <path>` first. Full spec: `references/design-md-anatomy.md`. Cross-skill extension convention: [design-system's extended-tokens reference](https://github.com/coroboros/agent-skills/blob/main/skills/design-system/references/extended-tokens.md).

Apply premium components (`references/premium-patterns.md`) — Doppelrand nested cards, Button-in-Button trailing icons, eyebrow tags, hero 2-line iron rule, mobile-collapse mandates, Liquid Glass Refraction, Perpetual Micro-Interactions when Motion ≥ 5. For multi-section pages, apply composition variety mandates from `references/foundations.md` (≥3 composition anchors, varied background mode per section, CTA shape varied at least once, mixed section ambition). Push at least three axes beyond the generic SaaS template — if the design could pass for default Tailwind output, escalate.

### Phase 4 — Production

When implementation touches video, scroll-driven cinematic reveals, or full-screen heroes on mobile, read `references/production-hardening.md` (viewport units, autoplay belt-and-suspenders, fail-safe reveal logic, proportional layout, iOS Safari quirks). Skip if desktop-only with no video or scroll choreography.

Build mobile-first, then close with the **two-gate quality check** — one gate that can fail, one that only advises. A model grading its own JSX "9/10" is theater, so the pass/fail rests on externally-checkable signals; the subjective rubric stays commentary.

**HARD gate — must pass to ship.** Deterministic, pass/fail:

- The countable checks in `references/anti-patterns.md` § *Countable checks* (eyebrow ≤ ceil(sections/3), N items → N bento cells, archetype-scoped em-dash density, per-hex banned palette) plus every axiomatic rejection — any violation is stop-and-fix, cited with the count.
- `references/foundations.md` UX Quality + Accessibility (touch targets, focus-visible, safe areas) — met.
- **Only when a DESIGN.md exists:** `/design-system audit <path>` and `audit-extensions <path>` clean. Skipped with no penalty otherwise — an Instant build is judged on its own output, never failed for lacking a token file.
- Where tooling exists: Lighthouse Performance + Accessibility ≥ 90; LCP < 1.5s, CLS < 0.05, INP < 100ms. With `dev-browser` installed, screenshot key states (hero, mobile, signature interaction, dark mode); install from `https://github.com/SawyerHood/dev-browser` if absent.

A failed HARD check blocks shipping — fix and re-run.

**SOFT gate — advisory only.** Run `references/audit-rubric.md` (7 categories, 0-10) as commentary with cited evidence and a P0/P1 punch list, fed into the next pass. Never present a self-graded number as a pass or claim a site "iterated to 20/20" — the rubric guides, the HARD gate decides. Verify against the *Judging Criteria* below.

## Persist — crystallize a DESIGN.md (opt-in, after the build)

After the site ships, offer to lock the design in for future work: *"Want a DESIGN.md so `/design-system` keeps this consistent across later changes? It takes a few moments."* Opt-in — it never blocks completion. Decline and the run is already done; no file is written.

On accept, author the full DESIGN.md from the build's own decisions: the inline token block becomes the YAML frontmatter, and the in-context archetype, atmosphere, signature moment, photography direction, and copy register become the eight ordered prose sections (`references/design-md-anatomy.md`). award-design owns this crystallization — it alone holds the archetype rationale that code cannot recover. Then `/design-system audit <path>` it. From there, `/design-system` governs the file; token-level changes route there, not back through award-design.

## DESIGN.md anatomy

The DESIGN.md (adapted, or crystallized by *Persist*) carries tokens (YAML: canonical 5 + 10 extension namespaces) and eight ordered prose sections. Full spec — namespace types, prose mapping, `@theme` mirror: `references/design-md-anatomy.md`.

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

**Handoff to design-system (reversed bridge).** award-design builds first; a DESIGN.md is optional. When one exists — adapted at the start or crystallized by *Persist* after the build — `/design-system` governs it: enforcing tokens, handling updates, preventing drift. Ownership is clean: award-design creates and crystallizes the DESIGN.md (it alone holds the archetype rationale code cannot recover); `/design-system` governs it and never authors a from-scratch design file. award-design covers the build, a complete re-architect, and crystallization; token-level changes (adjust a color, tweak spacing) go through `/design-system`.

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

Build order, once the archetype, atmosphere, and reference are set:

1. Design system first — CSS custom properties from the token block (type scale, palette, spacing).
2. Mobile-first, then enhance for desktop; collapse asymmetric layouts to single-column.
3. Premium patterns where they earn it (`premium-patterns.md`); animation last — choreograph, don't scatter, memoize perpetual animations.
4. The one-interaction test: remove all but one animation — the one that stays is the signature moment.

Production checks (Lighthouse 90+, mobile viewports 375/414/768px, `dev-browser` screenshots) run at the Phase 4 close.

## Output discipline

DESIGN.md crystallization (*Persist*) is long-form. **Never** ship placeholder shortcuts — `[remaining sections similar]`, `// ...`, `// TODO`, "for brevity", "the rest follows the same pattern". Each of the eight prose sections is complete or marked paused, never in-between. Full banned-phrase list: `references/anti-patterns.md` *Output discipline*.

**Continuation marker for split outputs.** At the response token ceiling, finish at a clean section boundary and end with `[PAUSED — N of 8 sections complete. Send "continue" to resume from: <next section name>]`. On `continue`, resume exactly there — no recap, no rewrite. The marker is the resume contract.

## Gotchas

1. **Archetype flip mid-project poisons the token set.** Tokens and components calibrated for one archetype (editorial) carry forward when the archetype changes (product); the result is a hybrid that fails the archetype-coherence judging criterion. Fix: emit a fresh inline token block from the new archetype — and if a DESIGN.md exists, regenerate it whole and mark the old one superseded in its preamble. Never patch in place.
2. **Atmosphere calibration written as YAML keys instead of Overview prose breaks `/design-system audit`.** Atmosphere scores (Density, Variance, Motion) belong in the **Signature moment intent** prose under Overview, not as top-level YAML keys. The audit lints YAML for the canonical token taxonomy and rejects unknown keys. Fix: treat atmosphere as metadata describing intent; never serialize it as a token group.
3. **Missing continuation marker on truncated output reads as "complete" to the user.** Output discipline (above) requires `[PAUSED — N of 8 sections complete...]` at every clean break. The model sometimes omits it when truncation lands mid-paragraph; the user gets a half-finished file with no resume signal. Fix: always end at a clean `##` boundary; emit the marker even when it feels redundant.
4. **Premium patterns assume framework features that may not exist in the target stack.** Doppelrand cards assume nested-shadow CSS; Button-in-Button assumes nested interactive elements. Stricter component libraries reject these. Fix: verify framework capability before recommending a premium pattern; fall back to foundational tokens if it won't render.
