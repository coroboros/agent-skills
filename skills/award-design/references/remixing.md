# Remixing archetypes

Most briefs land cleanly on a single archetype. Some don't — a creative agency that serves luxury clients wants Brutalist character but Corporate Luxury restraint; a data product for a cultural institution wants Editorial pacing over Bento density. When two archetypes genuinely belong together, a remix beats forcing one.

Read this when the archetype recommendation step reveals tension — when the brief refuses to pick.

## When to remix (signals)

- The user rejects the first two archetype recommendations, not because they're wrong but because each captures only half the brief.
- The audience the product serves and the personality of the brand making it pull in different directions (enterprise tool from a playful company, luxury experience from an engineering team).
- The user names two references from different archetypes ("I want Linear rigor but Anthropic warmth").
- Two categories in the atmosphere calibration end up at odds (Density 7 + Motion 9 — typical of a dense editorial stacked with cinematic reveals, which single archetypes rarely handle).

If you're uncertain — just pick one archetype, calibrate atmosphere, and ship. Remixes add complexity; reach for them only when a single archetype leaves the user unsatisfied.

## The framework

A remix is not a blend — it's an **arbitration**. You pick which parent contributes which token, and you justify each pick. The output has to read as a third brand that could stand on its own.

### Parent DNA

Declare a percentage split up front. It's a forcing function: "Brutalist × Corporate Luxury 60/40" sets the dominant parent and tells you which direction to lean when the two disagree. Count tokens at the end and verify the declared split matches what you built.

Typical splits:
- **70/30** — one archetype dominates, the other adds character (minor accent, typography at display only, specific component).
- **60/40** — primary identity clear, secondary parent visible in multiple places.
- **50/50** — rare and hard. Only when the brief is genuinely dual-nature (e.g., an agency site where the marketing pages and the case studies need different characters).

### Arbitration rules

Apply these in order. Each rule picks one parent for that dimension — never both.

1. **Typography from A or B, never both.** If you need two typefaces (headline + body), they can come from different parents, but the *system* — scale, weight logic, letter-spacing — comes from one. Justify: which parent's type system is denser/looser, and which does the brief need?
2. **Color: neutrals from one parent, accent from the other.** Never mix two accents. Pick the neutral base first (affects readability and atmosphere), then layer the other parent's accent as punctuation.
3. **Spacing: the stricter scale wins.** A loose scale over a tight one is always a mismatch. If parent A has `4/8/12/16/24/32/48/64` and parent B has `8/16/24/40/64/96`, pick A unless B's whitespace character is load-bearing for the brief.
4. **Radii: match the chosen typography.** Serif-heavy typography pairs with smaller radii (0–6px); rounded sans pairs with larger (8–16px). Don't mix pill-shaped buttons with a Tiempos headline.
5. **Depth: the more restrained parent wins.** If one parent uses flat surfaces and the other uses glassmorphism, take flat. You can always add depth later; you can't subtract it without redesigning every component.
6. **Components: annotate every pick.** For each component (button, card, input, nav), state which parent contributed geometry and which contributed color. This is the receipts trail — without it, the remix drifts.
7. **Do's and Don'ts: merge, then prune contradictions.** Both parents' rules go in. Contradictions get resolved ("terracotta won over purple") or flagged as "creative tension — document for team" (for contextual rules like app-mode vs editorial-mode).

### The one-paragraph declaration

Before writing tokens, write the remix identity in one paragraph. It should read like a brand statement:

> Brutalist × Corporate Luxury, 60/40. Creative agency for heritage brands. Hard geometry and flat color do the statement work; restrained whitespace, custom serifs at display, and considered photography keep it from being aggressive. The client is luxury; the voice is confident.

This paragraph is your guardrail. Every token decision downstream gets tested against it.

## Worked example: Brutalist × Corporate Luxury (60/40)

Brief: design studio that positions itself for luxury clients (fashion, hotels, fragrance). The studio wants to signal confidence and craft, not polite sterility. Luxury clients need to feel the brand won't dilute their own.

### Identity

60% Brutalist (studio voice: confident, non-apologetic, typographically aggressive), 40% Corporate Luxury (client reassurance: generous whitespace, custom serif for display, no gimmicks).

### Tokens

**Typography** (Brutalist system, Corporate Luxury face)
- Display: a custom serif (or GT Sectra if off-shelf) at weight 400. Large scale jumps (48 → 88px on hero).
- UI/body: a brutalist sans (GT America or Polysans) at weight 400. Tight tracking.
- Rationale: Brutalist's typographic *system* (aggressive mixing, scale jumps) wins. Corporate Luxury's serif character wins at display.

**Color** (Brutalist palette rule, Luxury neutrals)
- Neutrals: off-white (`#f5f3ee`) and near-black (`#1a1a1a`) — from Corporate Luxury (warm, not clinical).
- Accent: a single saturated hue used as a 2px rule or a full-bleed section background — Brutalist treatment.
- Rationale: Corporate Luxury's warm neutrals reassure clients; Brutalist's single-accent-as-rule keeps it assertive.

**Spacing**
- Base 8. Scale `8/16/24/32/48/64/96/128` — tight Brutalist rhythm in UI, luxury breathing at section breaks (96+).
- Rationale: Brutalist discipline wins for density; luxury pacing wins for section breaks.

**Radii**
- 0 everywhere except inputs (2px).
- Rationale: Brutalist geometry dominates. Serif display at weight 400 does not want rounded company.

**Depth**
- Flat. 2px rules replace shadows. One exception: editorial photography overlaps with text via `mix-blend-mode`.
- Rationale: both parents agree on restraint here.

**Component example — primary button**
- Geometry from Brutalist: 0 radius, uppercase label, tight tracking, 12/24 padding.
- Color from Corporate Luxury: near-black fill, off-white text. Hover: inverts.
- Annotation: geometry 70% Brutalist, color 100% Corporate Luxury.

**Do's**
- Use one accent hue and use it as a 2px rule or full-bleed section, never as decoration (Brutalist rule).
- Let editorial photography breathe — `max-width: 1280px`, generous top/bottom padding (Corporate Luxury rule).
- Headlines land at 48, 64, or 88. Nothing in between (Brutalist rule).

**Don'ts**
- Drop shadows on any surface (both parents agree).
- Pill buttons or radii above 2px (Brutalist rule).
- More than one accent per viewport (Brutalist rule).
- Sans-serif at display sizes above 48px — the serif owns display (remix-specific rule — this is where the identity lives).

### Parent DNA verification

Tokens traced:
- From Brutalist: 14 (typography system, accent rule, spacing base, radii, component geometry, do's 1 and 3, all don'ts)
- From Corporate Luxury: 9 (neutrals, display serif, section-break spacing, color component fills, do's 2, "no gimmicks" spirit)

Net: Brutalist 61%, Corporate Luxury 39%. Declared 60/40 — close enough.

## How this feeds DESIGN.md

A remix produces a single DESIGN.md, not two. All sections are written as if the remix is one system. The only visible trace of the remix in the DESIGN.md itself should be:

- Section 1 (Overview) mentions both parents in the atmosphere paragraph.
- Section 8 (Do's and Don'ts) has a few rules explicitly about the tension (the remix-specific rule above).
- An optional final section (after Do's and Don'ts) called **Parent DNA** that records the arbitration decisions for future maintainers. Unknown sections are preserved by the spec; they don't break `@google/design.md lint`.

This section is for team memory, not agent instruction. The YAML tokens and prose still read like a single system — the agent shouldn't be deciding which parent to invoke at render time; that decision is frozen into the tokens.

## Adapted from

The arbitration framework is adapted from the `remix-two-brands` prompt in [`rohitg00/awesome-claude-design`](https://github.com/rohitg00/awesome-claude-design/blob/main/prompts/remix-two-brands.md) (MIT), retuned for archetypes rather than brand DESIGN.md files. See also the worked example `linear-x-claude.md` in that repo for a different style of remix (Editorial × Warm Editorial).
