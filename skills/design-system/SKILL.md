---
name: design-system
description: Enforce DESIGN.md tokens when creating or modifying UI components. Ensures brand consistency across all code touching styles, components, layouts, or pages. When a UI/UX change is requested, DESIGN.md must be updated first — then propagate to code.
when_to_use: When the user asks to change colors, typography, spacing, shadows, component styles, layout, or any visual aspect of the UI. When creating new components or pages. When editing existing UI files. When the user says "redesign", "restyle", "update the look", "change the theme", or references visual tokens.
paths:
  - src/components/**
  - src/app/**
  - src/pages/**
  - src/layouts/**
  - src/styles/**
  - src/features/*/components/**
  - DESIGN.md
  - tailwind.config.*
model: opus
license: MIT
metadata:
  author: coroboros
---

# Design System

## Source of truth

Read `DESIGN.md` at the project root **before** writing any UI code. Every color, font, spacing value, and component style must come from this file.

If no `DESIGN.md` exists and you are building a new project, use `/award-design` to create the design — it will produce a DESIGN.md as part of its workflow. If `/award-design` is not available, create the DESIGN.md manually following the Stitch standard (see `references/design-md-structure.md` for the full 9-section spec and `references/design-system-*-example.md` for complete examples).

## Writing Principles

A DESIGN.md is written for both AI agents and human designers. These principles govern every section:

- **Descriptive over technical**: Write `"whisper-soft shadow"` alongside the exact value, not just `box-shadow: ...`. Translate CSS concepts into spatial language — `rounded-full` becomes "pill-shaped", `rounded-lg` becomes "subtly rounded corners". This gives AI agents semantic intent, not just values to copy.
- **Every value has a role**: Never list a color without explaining when and why to use it. `#5e5d59` means nothing; `Olive Gray (#5e5d59): secondary body text — warm medium-dark gray` is actionable.
- **Name tokens semantically**: `Parchment`, `Border Cream`, `Whisper Shadow` — not `bg-primary`, `border-1`, `shadow-sm`. Semantic names carry design intent across contexts.
- **Show the personality**: Section 1 sets the tone for the entire file. If it reads like a template, every section after it will be generic. Describe what makes this design *this design* — what would a human designer notice first?
- **Exact values are non-negotiable**: Prose without values is a mood board. Values without prose are a spreadsheet. Both are required for every token.

## DESIGN.md structure (Stitch standard)

A DESIGN.md follows the Google Stitch standard with 9 sections:

1. Visual Theme & Atmosphere
2. Color Palette & Roles
3. Typography Rules
4. Component Stylings
5. Layout Principles
6. Depth, Elevation & Material
7. Do's and Don'ts
8. Responsive Behavior
9. Agent Prompt Guide

When creating a new DESIGN.md, re-architecting an existing one, or auditing completeness, read `references/design-md-structure.md` — it covers what each section must include, good/bad examples, and the enforcement rationale. Day-to-day token lookups (colors, spacing, component specs) don't need it — they go through the Rules and UI/UX change flow below.

Complete example files: `references/design-system-claude-example.md` and `references/design-system-stripe-example.md`.

## Rules

- Colors, fonts, and spacing come **only** from DESIGN.md tokens
- Map tokens to CSS custom properties in the global stylesheet
- Map tokens to `tailwind.config.ts` `theme.extend` when using Tailwind
- Never use arbitrary Tailwind values (`text-[13px]`, `bg-[#abc]`) when a token exists
- Never introduce values not in DESIGN.md — if a case isn't covered, use the closest token and flag it to the user
- Dark mode: define variants in DESIGN.md, implement with `dark:` or `prefers-color-scheme`
- Shared brand across projects: same DESIGN.md tokens, framework-specific implementation

## Framework behavior

Detect the framework from config files (`astro.config.*`, `next.config.*`, etc.), then follow the project's instructions (CLAUDE.md, AGENTS.md, or equivalent) for implementation specifics (component library, font loading, file structure).

## Creating a new DESIGN.md

### 1. Gather context

Ask for brand direction: reference site, mood, target audience, archetype preference. If the user provides a reference site, analyze its visual language before writing.

### 2. Establish foundations

If `/award-design` is available and an archetype applies → use it. It will produce the archetype selection, atmosphere calibration (Density/Variance/Motion scores), and design foundations. These feed into all 9 sections of the DESIGN.md — see the mapping table below.

If `/award-design` is not available → ask the user to describe the atmosphere in concrete terms (not "modern and clean" but "dark surfaces, single accent, editorial typography, motion score 6/10").

**How award-design feeds into DESIGN.md sections:**

| award-design output | DESIGN.md section |
|---------------------|-------------------|
| Archetype selection + atmosphere prose | **1. Visual Theme & Atmosphere** — key characteristics, atmosphere scores (Density/Variance/Motion), visual DNA |
| Color palette from archetype reference | **2. Color Palette & Roles** — semantic names, exact values, usage context |
| Typography from archetype reference | **3. Typography Rules** — font families, hierarchy table, principles |
| Component specs from archetype reference | **4. Component Stylings** — buttons, cards, inputs, navigation, icons |
| Layout patterns from archetype reference | **5. Layout Principles** — spacing scale, grid strategy, whitespace philosophy |
| Shadow/material from archetype reference | **6. Depth, Elevation & Material** — shadow levels, surface treatment |
| Anti-patterns + archetype guardrails | **7. Do's and Don'ts** — testable rules from archetype constraints + AI tells |
| Responsive strategy | **8. Responsive Behavior** — breakpoints, touch targets, collapsing strategy |
| Atmosphere scores + color/type quick ref | **9. Agent Prompt Guide** — quick reference, example prompts, iteration rules |

Every section must be complete for the design-system skill to govern ongoing changes. Incomplete sections lead to token gaps that agents fill with defaults — defeating the purpose.

### 3. Write the DESIGN.md

Follow the 9-section structure with the writing principles above. Work through sections in order — section 1 establishes the voice, and every section after it should feel like it was written by the same person.

**Refinement process** (adapted from Google Stitch):
- Replace vague language with design-specific terminology: "nice header" → "sticky navigation with glassmorphism and centered wordmark"
- Every color, every spacing value, every shadow must be an explicit token with a semantic name
- Test the Agent Prompt Guide (section 9) mentally: could an agent build a correct component from these prompts alone?

### 4. Place and configure

- Place at the project root
- Configure `tailwind.config.ts` to map all tokens under `theme.extend` (if Tailwind is used)
- Set up CSS custom properties in the global stylesheet
- Verify the first component built matches the DESIGN.md exactly

## When UI/UX changes are requested

When the user asks for any visual change — colors, typography, spacing, shadows, component styles, layout, theme, or responsive behavior — follow this mandatory flow:

### 1. Check if the change affects DESIGN.md tokens

Ask: does this change introduce a new value, modify an existing token, or alter the visual system? If yes → DESIGN.md must be updated first.

Examples that require DESIGN.md updates:
- "Change the CTA color to blue" → update Color Palette & Roles
- "Make the cards more rounded" → update Component Stylings + Layout Principles
- "Switch to a darker theme" → update Visual Theme & Atmosphere + Color Palette + Depth/Elevation
- "Add a new badge component" → update Component Stylings
- "Increase section spacing" → update Layout Principles

Examples that do NOT require DESIGN.md updates:
- "Fix the button alignment on mobile" → layout bug, no token change
- "Add alt text to images" → accessibility, no visual token
- "Move the CTA above the fold" → content reordering, not a design system change

### 2. Update DESIGN.md first — it is the source of truth

1. Open DESIGN.md, locate the affected section(s)
2. Update the token values, semantic names, and usage descriptions
3. If the change cascades (e.g., a primary color change affects buttons, links, focus rings), update all affected sections
4. If the change conflicts with Do's and Don'ts (section 7), update the guardrails to match

### 3. Propagate to code

1. Update `tailwind.config.ts` to match the new tokens (if Tailwind is used)
2. Update CSS custom properties in the global stylesheet
3. Update components that use the changed tokens
4. Verify existing components still render correctly with the new values

### 4. Shared brand propagation

If the design is shared across projects: propagate DESIGN.md changes to all related projects, then run step 3 in each.

### Re-architecting the design

If the user wants a fundamental visual change (new archetype, different atmosphere, complete restyle), this is not a token update — it's a new design. Use `/award-design` to restart the archetype selection and produce a new DESIGN.md. The old DESIGN.md is replaced entirely.
