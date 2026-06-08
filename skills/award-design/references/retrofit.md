# Retrofit

Upgrading an existing site to award-grade quality is not the same job as designing one from scratch. The brand identity, the tech stack, and the user expectations are already set; the work is *targeted lift*, not greenfield architecture. This reference is the priority order — what to fix first, what to fix next, what to leave alone.

Use this when:

- The user runs `/award-design -u <url>` to upgrade an existing site (not just to extract its tokens — see `brand-extraction.md` for the extraction-only flow).
- The user says "make this site look premium" or "refresh the design without rebuilding".
- The user has an existing DESIGN.md but the rendered site fails axiomatic rejections in `anti-patterns.md`.
- A judging-axis audit (`audit-rubric.md`) returns scores below 6 on Hierarchy, Spacing, Typography, or Color, and a full rebuild isn't on the table.

## Why a fixed priority order

LLMs presented with a long list of design problems tend to fix the most visible one (the hero image, the color palette) and stop. The real lift comes from fixing the cheapest, most pervasive problems first — typography and color cleanup propagate across every page, while a hero redesign improves only one viewport. Working in priority order means each fix sets the foundation for the next, and the cumulative score lift compounds.

## The seven-step priority order

Apply in order. Do not skip ahead unless the brief explicitly carves out a step (e.g., "don't touch the fonts, the brand owns those" — note the exception, then continue from step 2).

### 1. Font swap

Biggest instant lift, lowest risk. If the display face is Inter, Roboto, Arial, or any system font, the page is failing axiom #2 of `anti-patterns.md` from the first hero. Swap to a deliberate face — a custom mark, a quality paid font (Söhne, Tiempos, GT, Apoc), or a distinctive free one (Instrument Serif, Geist, PP Editorial New). Keep the body sans-serif if it's reasonable; the display change alone moves Typography 0/10 → 6/10 in a single deploy.

The swap pulls from the archetype reference's typography section. If no archetype is set yet, run the brand-extraction flow first (`brand-extraction.md`) to seed the archetype hypothesis.

### 2. Color palette cleanup

After typography. Pure `#000` and pure `#FFF` are axiom #3 violations and signal "no color decision was made" — replace with off-blacks (`#0a0a0a`, `#141413`, `#1a1a1a`) and off-whites (`#fafafa`, `#f5f4ed`, `#faf9f5`). Reduce accent colors to one per viewport — competing accents tank Color audit scores. If the AI-purple gradient (axiom #1) is anywhere on the page, remove it before any other color work; nothing else matters until that gradient is gone.

Bind the new palette to `colors.*` canonical tokens in DESIGN.md. The `/design-system audit` lint catches broken references; run it after the cleanup to confirm.

### 3. Hover and active states

Every interactive element needs a hover state and an active/pressed state. The most common audit-rubric failure on retrofits: buttons with no `:hover` transform, links with no underline change, cards with no `:hover` lift. The fix is universal — add the missing states using transitions on `transform` and `opacity` only (per `foundations.md` Performance section). Spring physics canonical values (`stiffness: 100, damping: 20`) for any Framer Motion springs.

This step alone lifts Motion from 0/10 to 5/10 by demonstrating the page acknowledges user input.

### 4. Layout and spacing

The deepest lift; also the slowest. After typography and color are right, asymmetric layouts and intentional spacing become visible. Apply in this order:

1. **Mobile collapse mandates** (`premium-patterns.md` pattern 5) — every asymmetric desktop layout collapses to single-column below 768px, all `transform`-rotation and negative-margin overlaps removed below `md`.
2. **`min-h-[100dvh]`** replaces `h-screen` everywhere — `h-screen` jumps catastrophically on iOS Safari URL-bar toggle.
3. **Section spacing** — push to `py-24` minimum on marketing pages, `py-32` to `py-48` on luxury and editorial. Density bias (`foundations.md` Layout) applies — under-spacing is the AI default.
4. **Hero 2-Line Iron Rule** (`premium-patterns.md` pattern 4) — wide containers (`max-w-5xl` to `max-w-6xl`), `clamp()` scaling, H1 in 2–3 lines maximum.
5. **Three equal cards** (axiom #6) — never. Vary card sizes, move to bento or editorial layouts, or use a dominant card with supporting detail.

### 5. Replace generic components

Now the page can carry distinctive components. Replace the generic card (`border + shadow + white background`) with one of: Doppelrand (pattern 1), Liquid Glass (pattern 9), or a flat editorial card with hairline rules. Replace the always-pill-button with a Button-in-Button (pattern 2) on the primary CTA. Add eyebrow tags (pattern 3) above section headlines. The components are loaded from `premium-patterns.md`; pick by archetype and atmosphere band.

### 6. Empty / error / loading states

Most retrofitted sites have polished happy paths and no error states. Empty states, error states, and loading skeletons are 30% of the Usability score. Add them — even if they're minimal placeholders rendered with the new typography and color tokens. A "no items yet" state in the right type and color reads as designed; a `<div></div>` reads as broken.

Loading skeletons use the Shimmer perpetual micro-interaction (pattern 11) at the system's canonical `motion.duration-shimmer`.

### 7. Typography polish

After everything else. The polish layer: `letter-spacing` adjustments on display type (`-0.02em` to `-0.04em` on serifs and grotesks), `font-feature-settings: 'tnum'` on tabular numbers, `font-variation-settings` micro-shifts on hover for variable fonts, drop caps via `::first-letter`. Optical alignment, baseline grid lock, OpenType features. The kind of work that takes Typography from 8/10 to 10/10 — and that has no value until the underlying typography choice (step 1) and component architecture (step 5) are correct.

## What NOT to retrofit

Some interventions cost more than they return. Skip these unless the brief explicitly requires them:

- **Full archetype change** mid-retrofit. If the existing site is Bento and the user wants Spatial Organic, that's not a retrofit — that's a re-architect. Run the SKILL.md "Changing archetype mid-project" sub-flow instead, which regenerates the entire DESIGN.md from new foundations.
- **Migrating animation libraries** (GSAP → Framer Motion or vice versa) for the sake of "modernization". Use whichever the codebase already runs; mixing the two in the same component tree is an axiom-#15 anti-pattern (`foundations.md` AI Tells technical).
- **Adding a signature moment to a page that doesn't have a focal point**. Axiom #8 requires a signature, but bolting a kinetic typography reveal onto a generic centered hero just emphasizes the underlying template. Fix the hero composition first (step 4); the signature can ride on top.
- **WebGL or 3D additions** to a site that doesn't carry the cinematic register. Performance cost is high; payoff is low if the rest of the site is SaaS-rhythm.
- **Replacing all icons with custom SVGs** when the existing icon set is consistent and the brand has no icon-system stake. A library swap (Lucide → Phosphor) is a rounding error; a full custom-icon program is a six-week project. Pick one.

## After the retrofit

Run the same validation as a new project — the review pass (filter + rubric):

1. `references/anti-patterns.md` — axiomatic rejections first; if any present, the retrofit isn't done.
2. `references/audit-rubric.md` — score the seven categories. The retrofit target is +2 points per category from the pre-fix baseline.
3. `references/foundations.md` UX Quality and Accessibility sections — these are easy to defer during retrofit and easy to break.
4. Visual review via `dev-browser` if available — screenshot before/after for the user to compare.

Update DESIGN.md to reflect the post-retrofit state. The token diff between pre and post is a useful artifact for the team; export it via `/design-system diff DESIGN.md@HEAD~1 DESIGN.md`.

## Cross-references

- `brand-extraction.md` — the URL-based observation flow; runs *before* this retrofit if no DESIGN.md exists yet
- `anti-patterns.md` — axiomatic rejections (the floor) and full failure-mode catalog
- `audit-rubric.md` — quantitative scoring; the retrofit aims to lift each category 2+ points
- `premium-patterns.md` — components that replace the generic ones in step 5
- `foundations.md` — typography, color, motion, and performance fundamentals applied throughout
- SKILL.md "Changing archetype mid-project" — the alternative when the retrofit needs to become a re-architect
