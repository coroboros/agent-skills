# Anti-Patterns

Validation catalog for the HARD gate (Phase 4 — the two-gate close). Read before submitting or requesting review. Grouped by the kind of failure mode they create.

## Axiomatic rejections

Non-negotiable. If the design contains any of these, stop and fix — don't argue the edge case. These are the fingerprints of AI-generated work that every experienced judge recognizes in under three seconds. A single axiomatic violation is enough to score below Honorable Mention, no matter how strong the rest is.

1. **Never use the AI-purple gradient.** `linear-gradient(135deg, #a855f7|#8b5cf6, #ec4899|#6366f1)` — any variant pairing purple with pink or purple with blue. The moment judges see it, they stop looking.
2. **Never use Inter, Roboto, Arial, or system fonts as the display face.** They work as fallbacks and body. At the hero, they signal "no type decision was made". Pick deliberately — a custom face, a quality paid font (Söhne, Tiempos, GT, Apoc), or a distinctive free one (Geist, PP Editorial New). Instrument Serif and Fraunces are the two overexposed LLM-favorite display serifs — reach past them or justify (see *AI Tells → Typography*). Don't ship `font-family: 'Inter'` on an H1.
3. **Never use pure black (`#000`) or pure white (`#FFF`).** Off-black (`#0a0a0a`, `#141413`, `#1a1a1a`) and off-white (`#fafafa`, `#f5f4ed`, `#faf9f5`). The shift is 1% on a color picker and 100% of the atmosphere.
4. **Never use placeholder names or fake statistics.** "John Doe", "Sarah Chen", "Acme Corp", "99.99% uptime", "10,000+ happy customers", "50% faster". If content isn't real, write something specific and plausible — or keep the placeholder honest (`[client name]`, `[metric]`). The realistic-data rule: prefer `47.2%` to `99.99%`, `+1 (312) 847-1928` to `1234567`, `$99.00` to `$100.00`. Real data has texture; round numbers betray placeholder fill.
5. **Never ship the centered-hero-over-dark-image-with-generic-headline template.** The canonical AI landing page. Break one of those three: off-center the layout, use flat color or typographic hero, or write a headline that couldn't apply to another product.
6. **Never ship 3 equal cards in a row as your feature section.** The "feature row" is the most recognized AI template. Vary card sizes, move to editorial or bento layouts, or use a dominant card with supporting detail — not equal thirds.
7. **Never use emojis as UI icons.** Icon sets exist (Phosphor, Radix, Lucide, Iconify, custom SVG). Emojis in UI signal no design system.
8. **Never ship without a signature moment.** One interaction, one visual, one typographic decision that someone will remember after 30 seconds. Scattered micro-animations fail; one choreographed hero reveal succeeds. If you can remove every effect and the page reads the same, there is no signature. The signature is the loud one (a hero reveal, a kinetic headline). Premium pages also carry a *second-read moment* — a quiet detail noticed only on a return visit (an unexpected punctuation, an asymmetric bleed, an off-rhythm whitespace zone). Loud + quiet is the full premium pair; either alone is incomplete.
9. **Never wrap an H1 across 4–6 lines.** Use ultra-wide containers (`max-w-5xl`, `max-w-6xl`, or `w-full`) and scale type with `clamp()` so the headline lands in 2–3 lines maximum. The narrow-container 6-line wall is the canonical AI-headline failure. See `premium-patterns.md` for the 2-Line Iron Rule.
10. **Never use meta-labels like "SECTION 01" or "QUESTION 05".** Eyebrow tags carry meaning ("PRINCIPLES", "OUR APPROACH", "RECENT WORK"); meta-labels carry index numbers and read cheap. If the section needs a tag, write the category — not the count.
11. **Never use generic avatars.** Standard SVG "egg" placeholders, Lucide user icons, or stock "diverse team" photography signal "AI placeholder filled in last". Use real photography, candid shots, or a consistent illustration style. For demos, use `https://picsum.photos/seed/{context}/W/H` with contextual seeds.
12. **Never use startup-slop names.** "Acme", "Nexus", "SmartFlow", "FlowKit", "ProSync" are the AI-generated brand-naming default. Invent contextual, plausible brand names tied to the project's domain. The placeholder honesty rule applies — `[client name]` beats a fake brand.
13. **Never ship a hero with no real visual.** A headline floating over a flat gradient is the canonical placeholder hero. The hero needs photography, generated imagery, 3D/canvas, a textured surface — or a *deliberate* typographic treatment that IS the visual (kinetic display, type-as-image). A centered headline over a purple/blue or beige gradient does not clear the floor. Full protocol and the typographic-hero override: `imagery.md`.
14. **Never hand-roll fake product screenshots out of divs.** Simulating a dashboard or app UI with divs, borders, and gradients reads as AI filler and never matches the real product. Use a real capture; failing that, an honest labeled placeholder sized to the final aspect ratio. An honest placeholder beats a CSS pastiche. Full protocol: `imagery.md`.

Run this list first when validating. Anything it catches is stop-and-fix, not nice-to-have.

## Countable checks

The deterministic core of award-design's HARD gate. Unlike the axiomatic rejections (binary present/absent) and the rubric (subjective 0-10), these are *mechanically countable* — a number computed from the rendered page, compared against a threshold. Each declares its scope: **global** (every build) or **archetype-conditional** (suppressed for the named archetypes where the pattern is a legitimate choice). A failed check is stop-and-fix, cited with the count.

| Check | Rule | Scope |
|---|---|---|
| **Eyebrow density** | Eyebrow tags ≤ `ceil(sectionCount / 3)` — eyebrows punctuate, they don't label every section | Global |
| **Bento fill** | N list items render as exactly N cells — zero empty or filler cells (`grid-auto-flow: dense`, verified `col-span`/`row-span` interlock) | Global |
| **Banned palette** | No hex in the AI-purple set (`#a855f7`, `#8b5cf6`, `#ec4899`, `#6366f1`, and the `135deg` purple→pink/blue gradients); no pure `#000` / `#fff` | Global |
| **Heading lines** | Hero H1 wraps in ≤ 3 lines (2-Line Iron Rule, 3 the hard ceiling) | Global |
| **Meta-labels** | Zero `SECTION 01` / `QUESTION 05` index labels | Global |
| **Em-dash density** | Body-copy em-dash density ≤ ~1 per 100 words — high density reads as AI-generated prose | Archetype-conditional — **suppressed for `editorial` and `corporate-luxury`**, where the em-dash is a deliberate typographic choice |
| **Hero-stack cap** | Hero carries ≤ 4 stacked elements (eyebrow + H1 + subtext + one CTA cluster); subtext ≤ 20 words; no trust-strip or logo-wall inside the hero. Override: a long editorial standfirst counts as one element — cap the stack, not the sentence | Global |
| **CTA-intent consistency** | One label per intent across the page — `Get Started` + `Start Free` + `Try Now` for the same signup is the tell. Repeating the *same* label for the same intent is fine | Global |
| **Zigzag cap** | ≤ 2 consecutive image-text split rows before the layout breaks pattern. Override: a third is admissible only if it inverts composition, never a fourth left/right repeat | Global |
| **Marquee cap** | ≤ 1 marquee / infinite-scroll ticker per page — a single signature ticker is fine; a logo wall *and* a testimonial ribbon is the tell | Global |
| **Layout-family variety** | ≥ 4 distinct section layout families per 8 sections (hero, feature-split, bento, full-bleed media, editorial column, stat band, CTA band…) | Archetype-conditional — **suppressed for single-fold portfolios and pure docs** (see `foundations.md` Composition variety mandates) |

Scope note: the em-dash check targets **generated site copy**, not the codebase or this skill's own prose. Count it in the rendered body text; suppress entirely for the two archetypes above. The global checks run on every archetype, no exception. Countability is the upgrade over a context-blind blocklist — award-design scores *from* an archetype, it does not subtract *toward* a generic ban.

## Design failures

- **Template / AI layouts** — judges are working professionals who recognize these instantly. Single fastest way to fail.
- **Inconsistent systems** — polished homepage but weaker inner pages signals incomplete craft.
- **Stock photography** — signals generic thinking and tanks scores.
- **Desktop-first** — judges check mobile first. Usability is 30% of the score.
- **Cookie-cutter minimalism ("blanding")** — the safe muted geometric sans default everyone adopted is being actively rejected.

## Performance failures

- LCP > 2s, total weight > 3MB, animation dropping below 60fps.
- Videos loaded without lazy loading, 20+ font file requests.
- Images loaded twice due to poor `<picture>` implementation.
- Award-winner targets: **LCP < 1.5s**, **CLS < 0.05**, **INP < 100ms**.

## AI Tells (patterns that betray AI generation)

### Model default house style

Current models carry a persistent default aesthetic that judges now read as its own tell: warm cream backgrounds (~`#F4F1EA`), serif display type (Georgia, Fraunces, Playfair), italic word-accents, terracotta / amber accent. It suits editorial, hospitality, and portfolio briefs — and feels off for dashboards, dev tools, fintech, healthcare, or enterprise. It surfaces unprompted, in slide decks as well as web UIs. (The warm-cream cluster is the tell; the neutral off-whites endorsed below are not.)

A sibling overexposed cluster is the **premium-consumer palette** — sand/beige base (`#E7DFD3`, `#D8C7B0`), brass or gold accent (`#B08D57`, `#C9A227`), espresso text (`#3B2F2A`). The DTC-luxury monoculture, the Aesop-clone look. The hexes name the *family*, not a blocklist. Rotate at least one of the three roles — swap brass for oxblood, espresso for ink, sand for bone — or justify the palette against the brief.

Generic negation does not fix it. "Don't use cream", "make it clean and minimal" shift the model to a *different* fixed palette, not to variety. Two counters work:

- **Specify a concrete alternative** — exact palette hexes, typeface, corner radius, motion timing. The model follows explicit specs precisely.
- **Propose directions first** — surface 2-4 distinct directions (bg hex / accent hex / typeface + one-line rationale) and let the user pick, instead of committing to the default silently. Phase 1 already works this way — it recommends an archetype and offers one optional confirm; surface that choice rather than committing to the default silently.

### Visual

- Purple/blue gradients on white — the "AI purple" aesthetic.
- Pure black (#000) or pure white (#FFF) — use off-blacks and off-whites.
- Outer glow box-shadows, oversaturated neon accents.
- Gradient text on large headers.
- Static gradients as primary design elements (no longer differentiated).

### Typography

- Inter, Roboto, Arial, system fonts as primary choices.
- Space Grotesk (converging AI default) — vary between generations.
- Instrument Serif and Fraunces — the two LLM-favorite display serifs, now overexposed. Rotate to a less-defaulted face or justify. Editorial and Corporate Luxury may run a serif display, but pick past these two or state why.
- Oversized H1 that screams — control hierarchy with weight and color, not just scale.
- Serif on dashboards/software UI (serif is for editorial/luxury only).

### Layout

- Centered hero with generic headline over dark image.
- Split-screen 50/50 hero — solid text panel beside a photo panel with a hard vertical seam. A recognized template. Override: an editorial diptych where both panels are in compositional dialogue, not just text | image.
- 3 equal cards in a row (the "feature row" cliché).
- Predictable symmetric layouts at every section.
- `h-screen` instead of `min-h-[100dvh]` (breaks on mobile — iOS Safari URL-bar toggle).
- Cards-inside-cards-inside-cards. Nested containers compete for visual hierarchy. Use Doppelrand (concentric outer-shell + inner-core) where elevation is needed; otherwise let spacing carry the structure (see `premium-patterns.md`).
- Asymmetric layouts that don't collapse below 768px — touch-target conflicts, horizontal scroll, drift. Mobile collapse to single-column (`w-full px-4 py-8`) is mandatory.
- Empty bento cells. Apply `grid-auto-flow: dense` and verify `col-span` / `row-span` interlock leaves zero voids.
- Hero H1 wrapped across 4–6 lines (the 2-Line Iron Rule violation).

### Content

- Generic names: "John Doe", "Sarah Chen", "Jack Su" — use diverse, realistic-sounding names with cultural variety.
- Fake round numbers: "99.99%", "10,000+", "50% faster" — use organic, messy data: `47.2%`, `+1 (312) 847-1928`, `$99.00`.
- AI copywriting clichés: "Elevate", "Seamless", "Unleash", "Next-Gen", "Game-changer", "Delve", "Tapestry", "In the world of...", exclamation marks in success messages, "Oops!" error handling.
- Title Case On Every Header — sentence case reads more refined.
- Emojis in UI — use icons (Phosphor, Radix, or custom SVG).
- Broken Unsplash links — use `picsum.photos/seed/{context}/W/H` or SVG placeholders.
- Lorem Ipsum — write real draft copy. Latin placeholder text never ships.
- Filler UI text — "Scroll to explore", "Swipe down", scroll-arrow indicators, bouncing chevrons. They signal "AI couldn't decide what to put here" and add visual noise that competes with the hero. If the user needs the cue, design the affordance into the layout (rhythm, depth, asymmetric reveal); don't bolt on an instruction.

### Technical

- Mixing GSAP and Framer Motion in the same component tree. Use Framer Motion for UI/Bento interactions; reserve GSAP/Three.js for full-page scrolltelling or canvas backgrounds, wrapped in strict `useEffect` cleanup blocks.
- `window.addEventListener('scroll')` for scroll effects — use ScrollTrigger or CSS Scroll-Driven Animations.
- Complex flexbox percentage math — use CSS Grid.
- Animating `width`, `height`, `top`, `left` — use `transform` and `opacity` only.
- React `useState` for magnetic hover or continuous animation. Use Framer Motion's `useMotionValue` and `useTransform` outside the React render cycle (see `premium-patterns.md` performance locks).
- `backdrop-filter: blur()` on scrolling content. Apply blur only to fixed/sticky elements (navbars, modal overlays). Otherwise mobile Safari drops to 15–20fps.
- Static PNG grain overlays on scrolling containers — continuous GPU repaints. Apply procedural noise (Canvas/WebGL) to fixed `pointer-events: none` layers.
- Perpetual animations not memoized in their own microscopic Client Component — re-renders the parent layout 60×/second and breaks performance budget.

## UX anti-patterns disguised as creativity

- **Scroll hijacking** on text-heavy content — use scroll-*triggered* animations instead (user retains speed control).
- **Experimental navigation** requiring discovery — tanks usability even when creativity scores high. Every unconventional pattern needs a discoverable fallback.
- **Illusion of completeness** — scroll animations that pause, making users think they've reached the end.
- **Style over substance** — beautiful animations that slow task completion, custom cursors that obscure click targets, impressive loading screens covering 10+ second loads.
- **Cards inside cards inside cards** — nested container chrome that competes with the content it claims to elevate. One concentric Doppelrand is craft; three nested borders is noise.

## Component clichés (replace with intentional alternatives)

- **Generic card** (border + shadow + white background) — remove the border, use only background, or use only spacing. Cards exist when elevation communicates hierarchy.
- **Always one filled button + one ghost button** — add tertiary text links to vary visual noise.
- **Pill-shaped "New" / "Beta" badges** — try square badges, flags, or plain text labels.
- **Accordion FAQ sections** — try side-by-side lists, searchable help, or inline progressive disclosure.
- **3-card carousel testimonials with dots** — replace with masonry walls, embedded social posts, or single rotating quotes.
- **Pricing table with 3 towers** — highlight the recommended tier with color and emphasis, not extra height.
- **Avatar circles exclusively** — try squircles or rounded squares.
- **Light/dark toggle as sun/moon switch** — try a dropdown, system preference detection, or settings integration.
- **Footer link farm with 4 columns** — focus on main paths and legally required links.

## Output discipline

The DESIGN.md is long-form — eight prose sections plus YAML. Truncation is the highest-frequency way a high-effort plan ships as a half-empty file. Two banned-phrase categories make truncation visible and stoppable.

**Banned in code blocks** (any token group, any DESIGN.md fragment, any CSS sample):

- `// ...`, `// rest of code`, `// implement here`, `// TODO`, `/* ... */`, `// similar to above`, `// continue pattern`, `// add more as needed`
- bare `...` standing in for omitted tokens, fragments, or rule sets
- `[remaining tokens similar]`, `[other shadows similar]`, `[etc.]`

**Banned in prose** (DESIGN.md sections, anti-pattern explanations, reasoning blocks):

- "for brevity", "the rest follows the same pattern", "similarly for the remaining"
- "and so on" used to replace content, "I'll leave that as an exercise"
- "let me know if you want me to continue", "I can provide more details if needed"
- "[remaining sections similar]" — the canonical AI-truncation tell

**Banned structural shortcuts**:

- Outputting a token-namespace skeleton when the request is for full DESIGN.md
- Showing the first and last sections while skipping the middle
- Describing what a section *would* contain instead of writing it
- Ending mid-section without the continuation marker

**Continuation marker** for legitimate token-ceiling splits: finish at a clean section boundary, then end with `[PAUSED — N of 8 sections complete. Send "continue" to resume from: <next section name>]`. On `continue`, pick up exactly there with no recap, no rewrite, no compression. The marker is the only acceptable form of split output.
