# Editorial / Magazine

The web as print. Multi-column grids, asymmetric measure, pull quotes breaking flow. The defining characteristic is the serif-meets-sans pairing — a high-contrast typographic dialogue that signals reading-first hierarchy. Photography and illustration earn full bleeds; text retains its measure.

## Canonical reference — Siena Film Foundation

**Site.** Siena Film Foundation
**URL.** `siena.film`
**Award.** Awwwards Site of the Month, April 2025
**Studio.** Undisclosed in the public Awwwards entry.

The strongest editorial reference in the 2024–2026 window. Awwwards' own case study describes its design as editorial typography in a minimalist filmic structure. Grotesque-serif voice, cinematic filmstrip slider, vintage-poster type, dual-menu editorial navigation, parallax photo-driven storytelling. Translates the magazine grammar of a print monograph into the browser more cleanly than any 2025 SOTY contender. Substitutable peers: `anthropic.com` (terracotta-on-cream warm editorial), `newyorker.com` (canonical magazine grammar), `substack.com` (writer-centric warm editorial).

## DNA — non-negotiable

- High-contrast serif headline paired with sans-serif body — the typographic dialogue carries the archetype
- Multi-column grid (six to twelve columns) with asymmetric column widths
- Pull quotes break flow; full-bleed imagery alternates with text-heavy sections
- Reading-first measure protected at all sizes — body copy holds 60–75 characters per line
- Image treatment is high-contrast B&W, duotone, or desaturated with one accent — photography is treated, never raw

The archetype keeps its identity across light editorial (NYT, Substack, Anthropic), dark cinematic poster (Siena Film), warm cream (Hermès magazine pages), and high-density grid (Pitchfork-adjacent zines). Background register is an expression choice, not a definition.

## Common expressions

Three stacks fit the DNA. Pick the one matching brand voice and content type.

### Light editorial — NYTimes / Substack / Anthropic profile

Off-white or warm cream foundation (`#FCFCFC` to `#F8F5F0`). Body sits in deep charcoal (`#111111` or `#2F3437`); secondary text in warm gray (`#787774`). Restrained accents — terracotta, deep red, ink black, navy. Hairline dividers (`#EAEAEA`) separate sections. Photography is high-contrast B&W or desaturated color. Ideal for media and publishing, long-form storytelling, writer platforms, premium content sites.

### Dark cinematic poster — Siena Film profile

Near-black foundation (`#0A0A0A` to `#141413`) with cream off-white type, vintage-poster typography overlaid on cinematic film stills, serif-grotesque mixing, ticket-stub or filmstrip metaphors as structural elements. 5-star rating chrome, dual-menu editorial navigation. Ideal for cultural institutions, film foundations, festivals, music labels with editorial gravity.

### Warm magazine — fashion / lifestyle profile

Cream backgrounds (`#F8F5F0`, `#FAF7F0`) with warm photography, GT Sectra or Editorial New at 60–120px, generous gutters, Burberry-style serif return. Mixed serif-sans pairings, monospace metadata for credits and dates. Ideal for fashion editorial, luxury e-commerce with story content, lifestyle brands, coffee-table-book digital companions.

## Typography

The pairing is the design.

- **Display serif**: GT Sectra, Playfair Display, Editorial New, GT Super, Tiempos Headline — 60–120px, weight 600–700, tight tracking (`-0.02em` to `-0.04em`), tight leading (`1.05`–`1.1`)
- **Body sans**: Inter, Neue Haas Grotesk, ABC Diatype, PP Neue Montreal — 16–18px, weight 400, line-height 1.6
- **Pull quote**: display serif at xl size, italic, with `border-left` accent rule
- **Metadata** (dates, categories, reading time, credits): monospace (Geist Mono, JetBrains Mono, IBM Plex Mono) at 11–14px, uppercase, wide tracking (`0.05em`)
- **Drop caps and small caps**: variable-font opentype features (`ss01`, `smcp`) where the typeface supports them

Serifs returned hard in 2025–2026. Burberry's switch back to serif signaled the broader shift.

**The pairing is the floor; the signature is treating the display type as an image, not a picked font.** A high-contrast Didone at its default optical size — Bodoni Moda, Editorial New, Playfair — is the jury's "obvious answer done well": it clears the serif reflex but reads as font-*selection*, not art direction, and caps Typography around 8. To beat that, push the display type past a retail default:

- **Optical-size (`opsz`) custom instancing** — the one axis that redraws glyph outlines for size. A variable display serif built for art direction (Fraunces exposes `opsz 9–144`, plus `SOFT` and `WONK` alternates) set with `font-variation-settings: 'opsz' 144, …` *decoupled* from `font-size` gains a contrast and refinement a static cut cannot. Highest-leverage bespoke read, zero commission.
- **Draw the one masthead word as SVG outlines** — a single hero wordmark hand-set as paths (a custom ligature, a bespoke ampersand or numeral) reads as commissioned lettering while the body stays retail. Most of the "exclusive alphabet" read for one word of effort.
- **Compose the type AS the image** — one display word owning the frame at 20–40vw, tight negative leading, a deliberate overlap or second layer; scale, not decoration, carries the peak (the Brody / *The Face* move).
- **Kinetic axis on scroll as accent only** — interpolate `wght` / `opsz` / `GRAD` via `font-variation-settings` (GRAD shifts weight without reflowing), paused off-screen; never the whole idea.

## Color

Background spans three families per stack:

- **Light editorial**: `#FCFCFC` or warm cream `#F8F5F0` to `#FAF7F0`
- **Dark cinematic poster**: near-black `#0A0A0A` to `#141413`
- **Warm magazine**: cream `#F8F5F0` to `#FAF7F0` with warm photography overlays

Text colors map to background — off-black on cream, off-white on dark. Accents stay restrained — deep red (`#8B0000`), navy (`#1B365D`), ink black, terracotta (`#C67D5B`). One accent per article, never two competing. Image treatment is B&W, duotone, or desaturation — full-color photography belongs to other archetypes.

## Layout

Six to twelve column grids with asymmetric widths. Pull quotes break flow at columns 3–11. Full-bleed images escape the measure entirely.

```css
.editorial-layout {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 1.5rem;
}
.feature-article { grid-column: 1 / 8; }
.sidebar { grid-column: 9 / 13; }
.pull-quote {
  grid-column: 3 / 11;
  font-style: italic;
  font-size: var(--fs-xl);
  border-left: 3px solid currentColor;
  padding-left: 2rem;
}
.full-bleed-image { grid-column: 1 / -1; }
```

Container widths bind to `containers.read-measure` (~65ch for body) and `containers.editorial-page` (~1280–1440px max). Column counts shift through `breakpoints.*`. CSS Subgrid keeps card titles and timestamps aligned across rows.

## Motion

Understated, content-respectful, never competes with reading.

- Scroll reveals: opacity + `translateY(12px)`, 0.6–0.8s, `cubic-bezier(0.16, 1, 0.3, 1)`
- Image clip-path reveals on full-bleed entries
- Subtle parallax (5–10% differential) on hero photography only
- View Transitions API for thumbnail-to-hero morphs at navigation
- Staggered list reveals (80ms cascade) on article indexes

```javascript
SplitText.create(".article-headline", {
  type: "lines, words",
  mask: "lines",
  autoSplit: true,
  onSplit(self) {
    return gsap.from(self.words, {
      y: 40, autoAlpha: 0, stagger: 0.05,
      duration: 0.8, ease: "power3.out",
      scrollTrigger: { trigger: self.elements[0], start: "top 80%" }
    });
  }
});
```

Durations and easings pull from `motion.duration-*` and `motion.ease-*` extension tokens. Long-form articles benefit from `view-transition-name` on hero images for thumbnail-to-hero morphs at click.

## The words — copy is composed, not poured

Reading-*first* is the archetype's identity; text-*dense* is its failure mode. In a copy-heavy build the copy is designed as ruthlessly as the grid — this is where editorial most often collapses into a dev draft.

- **Cut to what earns its place.** A section is not a container to fill. Four long paragraphs before the first image, rest, or turn is a wall, not a feature. Break dense passages with a pull-quote, a full-bleed, or white space; *place* the text, never pour it.
- **The site never narrates or credits itself.** No "a feature on…", no "an essay about…", no listing the typefaces it is set in. Production copy speaks as the brand to its reader; a piece that describes its own construction reads as a portfolio draft (`anti-patterns.md`).
- **One informative label per section.** An eyebrow, a kicker/folio, an in-world device readout, and a title that all name the same thing is ornamental redundancy — and a count costume ("first / second / third casting") dressed as a chapter label is set-dressing. Keep the one label that informs; cut or differentiate the rest.
- **Register holds.** One copy voice per page (`preflight.md` register lock) — an editorial standfirst and a technical HUD readout are two registers; declare the mix or pick one.

## What makes it award-worthy

An editorial site scores 8+ when the typographic dialogue feels intentional — every serif weight, every tracking value, every gutter resolved through the same hand. When the multi-column grid breaks for a pull quote and the break feels surprising rather than mechanical. When photography is treated, framed, and paced so the reader's eye moves through the article like a ribbon. Siena succeeds because the filmstrip slider is editorial pacing, not decoration.

The archetype loses identity when serif is bolted onto a generic landing page (it reads as costume), when body measure exceeds 75 characters (reading collapses), or when image treatment is forgotten and stock photography sneaks in (signals generic thinking — single fastest way to fail per Awwwards judge feedback). It also caps hard on **copy**: a page that over-writes (dense text poured before any rest or visual), narrates or credits itself, or stacks three label layers on one section reads as a dev draft — and no amount of resolved type and grid buys that back. In this archetype the copy is scored as heavily as the type.

## Ideal for

Media and publishing, fashion brands with story-driven commerce, cultural institutions, film foundations and festivals, luxury e-commerce with editorial integration, long-form storytelling, online magazines, writer platforms, gallery websites.

## Cross-references

Read alongside `foundations.md` (typography systems, OKLCH, animation toolkit), `anti-patterns.md` (no `<div>`-button soup, no stock photography, no centered-hero-with-generic-headline template), `audit-rubric.md` (Typography 8+ is the entry bar in this archetype), `exemplars.md` (Anthropic, Substack, The New Yorker, Notion).
