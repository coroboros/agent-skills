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
  type: "lines",
  mask: "lines",
  autoSplit: true,
  onSplit(self) {
    return gsap.from(self.lines, {
      yPercent: 100, stagger: 0.1,
      duration: 1.0, ease: "power4.out", // easeOutQuint — the winners' register; y:40 fade-ups at power3 are the AI default
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
- **Default is no kicker — the section title stands alone.** A mono all-caps eyebrow stamped above every h2 ("THE CURRENT NUMBER" over *Weathers*, "SUBSCRIBE" over *Have it sent.*) is ornamental sameness: the reader already knows where they are. A kicker ships only when it carries information the title and the section's position do not (a real category, a date). Stacking an eyebrow *and* a folio *and* a device readout on one section compounds the tell.
- **Register holds.** One copy voice per page (`preflight.md` register lock) — an editorial standfirst and a technical HUD readout are two registers; declare the mix or pick one.

## What makes it award-worthy

An editorial site scores 8+ when the typographic dialogue feels intentional — every serif weight, every tracking value, every gutter resolved through the same hand. When the multi-column grid breaks for a pull quote and the break feels surprising rather than mechanical. When photography is treated, framed, and paced so the reader's eye moves through the article like a ribbon. Siena succeeds because the filmstrip slider is editorial pacing, not decoration.

The archetype loses identity when serif is bolted onto a generic landing page (it reads as costume), when body measure exceeds 75 characters (reading collapses), or when image treatment is forgotten and stock photography sneaks in (signals generic thinking — single fastest way to fail per Awwwards judge feedback). It also caps hard on **copy**: a page that over-writes (dense text poured before any rest or visual), narrates or credits itself, or stacks three label layers on one section reads as a dev draft — and no amount of resolved type and grid buys that back. In this archetype the copy is scored as heavily as the type.

## Ideal for

Media and publishing, fashion brands with story-driven commerce, cultural institutions, film foundations and festivals, luxury e-commerce with editorial integration, long-form storytelling, online magazines, writer platforms, gallery websites.

## Cross-references

Read alongside `foundations.md` (typography systems, OKLCH, animation toolkit), `anti-patterns.md` (no `<div>`-button soup, no stock photography, no centered-hero-with-generic-headline template), `audit-rubric.md` (Typography 8+ is the entry bar in this archetype), `exemplars.md` (Anthropic, Substack, The New Yorker, Notion).

## Effect palette — what this line's winners ship

Corpus — Siena Film Foundation (Awwwards Site of the Month, Apr 2025), Truekind Skincare (Awwwards SOTD, Apr 2025), Anthropic (brand-site control), plus case-study reads on Bisous, Exat, Cartier 365, Dondre Green, Stefan Vitasović. Button/link/nav mechanics below are read live from the first three's CSS; motion, loaders, and text choreography come from studio case studies.

**The grammar** — variety coheres because each element class runs a *different* mechanism over a shared substrate, tied by one gesture that rhymes: something rolls, swaps, or inverts. Siena reuses a named ease library — `--easeOutQuint: cubic-bezier(.23,1,.32,1)`, `--customEase: cubic-bezier(.19,1,.22,1)`, `--easeOut: cubic-bezier(.77,0,.175,1)` — quiet feedback at `~.2s`, signature moves at `.5–.8s`; Truekind converges on `cubic-bezier(.18,.71,.11,1)` at `.8–1s`. Two sites land on slow expo/quint out-eases (`~.8–1.1s`), well past the AI-default `.6s`/power2. Accent logic is ink-inversion tied to the section behind — cream ↔ black with one red for emphasis (Siena), token-swap on a single `.2s` transition (Anthropic) — never a decorative line. Cohere on easing + palette + one gesture, or on a token system + one timing + a serif voice in the chrome.

**Buttons / CTA**
- **Full-fill + ink inversion (primary/secondary).** Outline or light button fills a *solid* brand value, label flips to the opposite ink — never a pale tint. Truekind `.btn.outline:hover { background:#3b3b3b; color:#fff }`; Siena `.all-work-cta-w:hover { background:#000; color:#fff }`, nested arrow inverting the opposite way, `transition:.5s` on `--easeOutQuint`; Anthropic play button bg↔text at `.2s`. Default for the main CTA. (Siena SOTM Apr 2025; Truekind SOTD Apr 2025; Anthropic control)
- **Two-layer kinetic label roll (signature hero CTA).** Siena `[data-btn=explore]`: SVG shape fills transparent→white, stroke flips to black, and the label *rolls* — visible copy slides `translate(100%)` out while a duplicate below rolls `translateY(-150%)` in, both recolouring to the ink, staggered `.1s`; `--duration:.8s` on `--easeOutQuint`. The loud move — fill *and* kinetic label. (Siena SOTM Apr 2025) (single-source)
- **Kinetic marquee label.** Truekind `.btn`: static label fades to `0` while `.marquee__inner` starts scrolling on hover, `.4s`. Pick when the word itself should feel alive. (Truekind SOTD Apr 2025)
- **Accent-token fill (persistent nav CTA).** Anthropic nav CTA fills the full clay accent (`--swatch--clay`), text via `-hover` tokens; Truekind `.navbar-cta` is a charcoal `#333` pill, `background 1s cubic-bezier(.18,.71,.11,1)`. The one neutral one-step (`cloud-light`) is reserved for secondary/code buttons — never the primary. (Anthropic control; Truekind SOTD Apr 2025)

**Links**
- **Underline drawn from origin-left.** Truekind `.link:hover:before { transform:scaleX(1); transform-origin:0 50% }`, retracting rightward when already active. A drawn line, never a snap. (Truekind SOTD Apr 2025)
- **`text-decoration-color` fade with context-varying offset.** Anthropic holds `text-decoration-color:transparent` at rest, transitions to ink at `.2s`, `text-underline-offset` tuned per context — `.2em` nav, `.18em` dropdown, `.25em` footer. The varied offset is itself a coherence tell. (Anthropic control)

**Figures / cards**
- **Contained zoom.** Siena `.previousnext-item:hover .full-img-w { transform:scale(1.1) }` inside `overflow:hidden`. Baseline, present everywhere. (Siena SOTM Apr 2025)
- **Focus / defocus siblings.** The hovered figure sharpens while neighbours blur and dim, so attention is *directed* — Dondre stories page, WebGL displacement. Pick for a gallery where one item should win the eye. (Dondre Green, Codrops case study)

**Nav** — three verified treatments, none frosted, none with a contrasting `border-bottom`:
- **Transparent + gradient scrim + ink-inversion by section (dark cinematic).** Siena `.nav-w`: `position:fixed`, `pointer-events:none`, no bar; legibility from a `linear-gradient(#000,#fff0)` top scrim; a section class flips ink (`.on-dark .logo { color:#000 }`). (Siena SOTM Apr 2025)
- **Solid theme-bg bar + same-family hairline (light editorial).** Anthropic `.nav_wrap { background: theme-background }` ivory, hairline as a `border-top` in `--swatch--ivory-medium`, links set in the display serif — the chrome carries the editorial voice. (Anthropic control)
- Winners never frost the bar or hang a contrasting-accent underline; contrast comes from ink inversion tied to the section behind.

**Text** — one signature type move per site, everything else quiet entrance.
- **Variable-font axis morph (peak).** Exat: real-time `wght`/width transition on hover, one axis at a time; a proximity glyph grid where cursor distance drives per-glyph weight `200–900`. `opsz` — the axis that redraws outlines — is the highest-leverage editorial peak; Anthropic ships `font-variation-settings:"opsz" 50` on its base `.button` in production. (Exat, Codrops case study) (single-source)
- **Type-as-image masthead.** One display word owning the frame; Siena's vintage-poster masthead over cinematic stills is the dark-register expression. (Siena SOTM Apr 2025)
- **Char-assemble entrance (supporting).** Stefan: chars come together, masked for glass-like parallax, `duration 1.25 + index*0.025`s, stagger `.025`s, `easeExpOut`. The rare fully-specified reveal. (Stefan Vitasović, Codrops case study)

**Cursor** — the editorial default is the real system pointer: Siena, Truekind, Anthropic all ship `cursor:pointer` on interactives, `grab` on sliders, no custom sprite. When a winner touches the pointer it *does work* — a lens that unblurs text (Dondre 404) or proximity that drives glyph weight (Exat) — never a `mix-blend-mode` follower.

**Loader / intro** — register split. Dark cinematic seeds the first frame: Siena's neo-romanesque stripes transition *into* the first section; Bisous's cinematic loader becomes the homepage slider; Dondre's letter-grid resolves into the hero wordmark. Light editorial paints instantly — Truekind and Anthropic ship no preloader layer; reading starts on load (observed, implementation unverified). Never a generic percentage spinner.

**Anti-signals** — absent from every winner examined: a pale / low-opacity accent-tint fill on a primary control (winners fill the full token and invert the label); a frosted `backdrop-filter:blur()` bar with a contrasting-colour `border-bottom`; the `mix-blend-mode:difference` circular follower; uniform fire-once `y:30, .6s, ease-out` reveals on everything (winners run slower expo/quint eases, mask by line/word, keep panels reversible, author one scroll mechanic per story); a generic percentage-counter preloader; and the same interaction mechanism cloned across button, link, image and nav.
