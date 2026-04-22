# Brand Extraction

Reverse-engineer a DESIGN.md from an existing live site. Use this when the user passes `-u <url>` — they're pointing at a reference they want to style *like* (their competitor, their inspiration, or their own legacy site they're modernizing).

The extracted DESIGN.md then flows through the normal workflow: you propose an archetype based on the observation, calibrate atmosphere, and produce the final DESIGN.md. The URL is the starting observation, not the destination.

## When to use

- User runs `/award-design -u https://<url> <what to build>` — the URL is an inspiration reference or a legacy site to modernize.
- User asks "design the site like [URL] but for my product" mid-conversation.
- User hands over a site they want audited into a DESIGN.md before restyling.

Do NOT use this to clone a site. The goal is to capture visual language, then evolve it into something that fits the user's actual brief.

## Inspection checklist

Observe the live site before writing anything. If `dev-browser` CLI is available (see main SKILL.md), use it to screenshot and inspect computed styles. If not, ask the user to paste computed CSS, or describe what they see.

For each item, record what you verified:

### Typography
- Body computed font-family and the fallback chain
- H1 computed font-family, size, weight, letter-spacing, line-height
- Whether display and body share a family or are paired
- Mono font presence and usage

### Color
- Body `background-color` and `color`
- Primary button fill and text color
- Primary link color (and hover)
- Border color where visible
- Whether the site uses hex, oklch, or rgba — record what's actually in the computed styles
- Accent usage pattern — once per viewport? scattered? functional-only?

### Layout
- Max content width (sample the main container)
- Grid strategy — 12-col visible gutters? freeform? bento tiles?
- Spacing scale — sample 5+ distinct spacing values and check if they form a scale
- Section padding sizes

### Components
- Button: padding, radius, shadow (if any), hover transform
- Card: background, border, radius, shadow, whether hover changes it
- Input: border, focus ring, radius

### Distinctive signatures
- Anything that breaks the generic template — custom cursors, kinetic type, scroll-driven video, 3D elements, unusual navigation, mix-blend-mode photography, 2px rules as depth, full-bleed sections, etc.
- Note the *one thing* someone would remember about this site after 30 seconds.

## Hard rules

- **Only describe what you verified.** Don't hallucinate a font name because the letterforms look like Neue Haas. Mark "unknown — probably custom" if unclear.
- **Hex values only.** Convert rgba/oklch to hex for the DESIGN.md. If the site uses alpha that can't be flattened (overlays), note it inline with the hex.
- **Semantic roles, not observations.** Write "primary CTA color" not "this color I saw on the button". DESIGN.md tokens live on after you've forgotten the source site.
- **No hallucinated completeness.** If the site doesn't show dark mode, don't invent a dark palette. Mark "Dark mode: not observed on source; extend if target brief requires it."

## Reverse-engineering → archetype

After observation, propose an archetype based on what you saw. Map common signatures to archetypes:

| Observed pattern | Likely archetype |
|---|---|
| Warm neutrals + serif display + long reading measure | **Editorial** or **Corporate Luxury** |
| Pure grayscale + single accent + tight Inter/Geist | **Minimalist** |
| Hard geometry + 2px rules + uppercase + single saturated hue | **Brutalist** |
| Full-screen video/WebGL + dark bg + oversized display | **Immersive / Cinematic** |
| Frosted blur + pastel gradients + rounded soft shapes | **Spatial Organic** |
| Modular tiles with distinct colors per cell, feature-grid layouts | **Bento / Card** |
| 4+ brand hues rotated per section + illustrated accents | **Bold / Maximal** |
| Custom cursors, creative-code, rule-breaking nav | **Experimental** |

If the site spans two archetypes, acknowledge it and propose a remix — read `remixing.md` and offer the remix alongside single-archetype options.

## Atmosphere calibration from observation

Estimate Density, Variance, and Motion from what you observed:

- **Density** — count elements per above-the-fold viewport. <5 = Density 2–3. 5–10 = Density 4–6. 10+ = Density 7+.
- **Variance** — does the grid break? Are sections symmetric or asymmetric? Symmetric = Variance 2–4. Mixed = Variance 5–7. Broken/overlapping = Variance 8+.
- **Motion** — inspect the scroll behavior. Static or opacity-only = Motion 2–3. Scroll-triggered with hover states = Motion 4–6. Continuous animation, scroll-driven video, WebGL = Motion 7+.

Present these scores with the archetype proposal. The user validates both before you proceed.

## Then flow back to normal workflow

Once you have the observed archetype + atmosphere + palette + typography:

1. Present archetype + atmosphere recommendation to the user — they validate or adjust.
2. Continue with step 3 of the main workflow (`Read archetype reference`), step 4 (`Calibrate atmosphere`) — the user can refine what you extracted, add what's specific to their brief.
3. Step 6 produces the final DESIGN.md — the *target* design, informed by the observation but not constrained to it.

The extracted observation is the *seed*. The brief is the *destination*.

## Output when the user wants the extracted DESIGN.md directly

If the user's intent is "give me a DESIGN.md that captures site X so I can use it later" (not "design my site in the style of X"), skip steps 2+ of the main workflow and produce the DESIGN.md directly from the observation, using all 9 sections (per `/design-system`'s `design-md-structure.md`). Include a final note:

> ## Source
> Extracted from <URL> on <date>. Observed values only — no invented tokens. Brands belong to their respective owners; this DESIGN.md is for design analysis and inspiration.

The user chooses which workflow to follow — clarify if the intent isn't obvious from the original invocation.

## Adapted from

The inspection checklist and "observe, don't invent" discipline are adapted from the `brand-to-design-md` prompt in [`rohitg00/awesome-claude-design`](https://github.com/rohitg00/awesome-claude-design/blob/main/prompts/brand-to-design-md.md) (MIT).
