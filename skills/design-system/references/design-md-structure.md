# DESIGN.md Structure (Stitch standard)

Read this when creating a new `DESIGN.md` from scratch, re-architecting an existing one, or auditing an existing file for completeness. Not needed for day-to-day token lookups — those go through the main SKILL.md flow.

A `DESIGN.md` follows the Google Stitch standard with 9 sections. Each section below includes guidance on what separates good from excellent content.

## 1. Visual Theme & Atmosphere

The personality of the entire design captured in prose. This is the section an agent reads first to understand *what this design feels like* before touching any code.

**Must include:**
- Key characteristics list with exact values (not vague adjectives)
- Atmosphere scores (Density, Variance, Motion — from `/award-design` calibration if available)
- Visual DNA: composition type (grid/freeform), content width strategy (contained/full-bleed), framing style (sharp/glassy/organic), grid character (rigid/broken/fluid)

**Good vs. bad:**
- Bad: "Clean, modern design with a professional feel"
- Good: "A literary salon reimagined as a product page — warm parchment canvas (#f5f4ed) with custom serif headlines at weight 500, creating a reading experience closer to a book than a dashboard"

## 2. Color Palette & Roles

Every color in the system with its semantic name, exact value, and usage context.

**Must include:**
- Primary, secondary, accent colors with hex/rgba/oklch values
- Surface and background hierarchy (page → card → elevated)
- Neutral scale with warm/cool characterization
- Border and shadow colors as explicit tokens
- Gradient system (or explicit statement if gradient-free)
- Dark mode variants if applicable

**Key rule:** Group by role (Primary, Surface, Neutral, Semantic), not by hue. Every entry needs: semantic name + exact value + when to use it.

## 3. Typography Rules

The complete type system with font families, hierarchy table, and design principles.

**Must include:**
- Font families with full stacks and fallbacks
- Hierarchy table: Role | Font | Size | Weight | Line Height | Letter Spacing | Notes
- Cover every level from Display/Hero down to Micro/Overline
- OpenType features if applicable (`tnum`, `ss01`, etc.)
- Principles explaining the *why* behind choices (weight strategy, line-height philosophy, spacing logic)

## 4. Component Stylings

Exact specifications for every reusable component.

**Must include:**
- Buttons (all variants: primary, secondary, ghost, destructive — with background, text, padding, radius, shadow, hover)
- Cards & containers (background, border, radius, shadow by elevation)
- Inputs & forms (border, focus ring, label style, error state)
- Navigation (structure, link styles, CTA placement, sticky behavior)
- Icons: provider/set (Phosphor, Radix, Lucide, Iconify), treatment style (linear/filled/duotone), sizing scale
- Badges, tags, pills if used
- Image treatment (radius, shadow, aspect ratios)

## 5. Layout Principles

Spacing system, grid strategy, and whitespace philosophy.

**Must include:**
- Base unit and spacing scale with exact values
- Grid and container strategy (max-width, column logic)
- Whitespace philosophy in prose (what the spacing *communicates*)
- Border radius scale with named levels (sharp → pill)
- Section padding values

## 6. Depth, Elevation & Material

The shadow system and surface treatment that creates physical depth.

**Must include:**
- Shadow levels table: Level | Treatment | Use
- Shadow philosophy (neutral vs. chromatic, single vs. multi-layer)
- Surface material: glass (backdrop-filter blur), matte (flat), textured — with exact CSS
- Decorative depth techniques (gradient borders, inset shadows, background alternation)
- If the design uses blur, grain, noise, or other material effects — document with values

## 7. Do's and Don'ts

Explicit guardrails for maintaining the design identity. This is the enforcement section — what agents check before committing code.

**Must include:**
- 8-12 Do's with specific values (not "use brand colors" but "use Terracotta #c96442 only for primary CTAs")
- 8-12 Don'ts with explanations (not "don't use bold" but "don't use weight 700+ on serif headlines — weight 500 is the ceiling")
- Each rule should be testable — an agent can verify compliance without judgment calls

## 8. Responsive Behavior

How the design adapts across viewports.

**Must include:**
- Breakpoint table: Name | Width | Key Changes
- Touch target minimums (44×44px)
- Collapsing strategy for each major component (nav, grids, hero, cards)
- Typography scaling across breakpoints
- Image behavior (art direction changes, aspect ratio preservation)

## 9. Agent Prompt Guide

Direct instructions for AI agents generating components in this design system.

**Must include:**
- Quick color reference (one-liner per key color: role + name + hex)
- 4-5 example component prompts with every relevant value spelled out
- Iteration guide: numbered rules for how to work within this system
- **Bias toward** — 4-7 single-line cues the agent should instinctively reach for (e.g., "warm tones over cool", "asymmetric grids over centered", "negative tracking at display sizes"). The Do's section lists rules; Bias distills those rules into reflexes the agent reaches for under token pressure.
- **Reject** — 4-7 explicit don'ts phrased as hard lines (e.g., "pure white page background", "generic gradient heroes", "Inter as the display face"). Some overlap with the Don'ts section is expected — this block is optimized for a one-glance scan during generation, not completeness.
- **Self-test question** — one question the agent asks itself before committing a component: "Could this ship on any SaaS homepage?" If yes, the component isn't in the system yet. Rewrite until the answer is no. Pick a question that makes the design's identity unmistakable.

**This section is what makes a DESIGN.md AI-native.** Without it, agents will approximate. With it, they reproduce the design accurately from the first generation. The Bias / Reject / Self-test block is specifically calibrated for one-shot generation — the agent doesn't always re-read the full DESIGN.md mid-task, but it can always check against three lines.

See `design-system-claude-example.md` and `design-system-stripe-example.md` (same `references/` folder) for complete examples demonstrating all 9 sections.
