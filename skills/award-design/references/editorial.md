# Editorial / Magazine

The web as print. Multi-column grids, asymmetric measure, pull quotes breaking flow. The defining characteristic is the serif-meets-sans pairing — a high-contrast typographic dialogue that signals reading-first hierarchy. Photography and illustration earn full bleeds; text retains its measure.

## Canonical reference — Siena Film Foundation

**Site.** Siena Film Foundation
**URL.** `siena.film`
**Award.** Awwwards Site of the Day, March 18, 2025 + Site of the Month, March 2025 (refuter-corrected from an earlier April read)
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
- **Full-fill + ink inversion (primary/secondary).** Outline or light button fills a *solid* brand value, label flips to the opposite ink — never a pale tint. Truekind `.btn.outline:hover { background:#3b3b3b; color:#fff }`; Siena `.all-work-cta-w:hover { background:#000; color:#fff }`, nested arrow inverting the opposite way, `transition:.5s` on `--easeOutQuint`; Anthropic play button bg↔text at `.2s`. Default for the main CTA. (Siena SOTM Mar 2025; Truekind SOTD Apr 2025; Anthropic control)
- **Two-layer kinetic label roll (signature hero CTA).** Siena `[data-btn=explore]`: SVG shape fills transparent→white, stroke flips to black, and the label *rolls* — visible copy slides `translate(100%)` out while a duplicate below rolls `translateY(-150%)` in, both recolouring to the ink, staggered `.1s`; `--duration:.8s` on `--easeOutQuint`. The loud move — fill *and* kinetic label. (Siena SOTM Mar 2025) (single-source)
- **Kinetic marquee label.** Truekind `.btn`: static label fades to `0` while `.marquee__inner` starts scrolling on hover, `.4s`. Pick when the word itself should feel alive. (Truekind SOTD Apr 2025)
- **Accent-token fill (persistent nav CTA).** Anthropic nav CTA fills the full clay accent (`--swatch--clay`), text via `-hover` tokens; Truekind `.navbar-cta` is a charcoal `#333` pill, `background 1s cubic-bezier(.18,.71,.11,1)`. The one neutral one-step (`cloud-light`) is reserved for secondary/code buttons — never the primary. (Anthropic control; Truekind SOTD Apr 2025)

**Links**
- **Underline drawn from origin-left.** Truekind `.link:hover:before { transform:scaleX(1); transform-origin:0 50% }`, retracting rightward when already active. A drawn line, never a snap. (Truekind SOTD Apr 2025)
- **`text-decoration-color` fade with context-varying offset.** Anthropic holds `text-decoration-color:transparent` at rest, transitions to ink at `.2s`, `text-underline-offset` tuned per context — `.2em` nav, `.18em` dropdown, `.25em` footer. The varied offset is itself a coherence tell. (Anthropic control)

**Figures / cards**
- **Contained zoom.** Siena `.previousnext-item:hover .full-img-w { transform:scale(1.1) }` inside `overflow:hidden`. Baseline, present everywhere. (Siena SOTM Mar 2025)
- **Focus / defocus siblings.** The hovered figure sharpens while neighbours blur and dim, so attention is *directed* — Dondre stories page, WebGL displacement. Pick for a gallery where one item should win the eye. (Dondre Green, Codrops case study)

**Nav** — three verified treatments, none frosted, none with a contrasting `border-bottom`:
- **Transparent + gradient scrim + ink-inversion by section (dark cinematic).** Siena `.nav-w`: `position:fixed`, `pointer-events:none`, no bar; legibility from a `linear-gradient(#000,#fff0)` top scrim; a section class flips ink (`.on-dark .logo { color:#000 }`). (Siena SOTM Mar 2025)
- **Solid theme-bg bar + same-family hairline (light editorial).** Anthropic `.nav_wrap { background: theme-background }` ivory, hairline as a `border-top` in `--swatch--ivory-medium`, links set in the display serif — the chrome carries the editorial voice. (Anthropic control)
- Winners never frost the bar or hang a contrasting-accent underline; contrast comes from ink inversion tied to the section behind.

**Text** — one signature type move per site, everything else quiet entrance.
- **Variable-font axis morph (peak).** Exat: real-time `wght`/width transition on hover, one axis at a time; a proximity glyph grid where cursor distance drives per-glyph weight `200–900`. `opsz` — the axis that redraws outlines — is the highest-leverage editorial peak; Anthropic ships `font-variation-settings:"opsz" 50` on its base `.button` in production. (Exat, Codrops case study) (single-source)
- **Type-as-image masthead.** One display word owning the frame; Siena's vintage-poster masthead over cinematic stills is the dark-register expression. (Siena SOTM Mar 2025)
- **Char-assemble entrance (supporting).** Stefan: chars come together, masked for glass-like parallax, `duration 1.25 + index*0.025`s, stagger `.025`s, `easeExpOut`. The rare fully-specified reveal. (Stefan Vitasović, Codrops case study)

**Cursor** — the editorial default is the real system pointer: Siena, Truekind, Anthropic all ship `cursor:pointer` on interactives, `grab` on sliders, no custom sprite. When a winner touches the pointer it *does work* — a lens that unblurs text (Dondre 404) or proximity that drives glyph weight (Exat) — never a `mix-blend-mode` follower.

**Loader / intro** — register split. Dark cinematic seeds the first frame: Siena's neo-romanesque stripes transition *into* the first section; Bisous's cinematic loader becomes the homepage slider; Dondre's letter-grid resolves into the hero wordmark. Light editorial paints instantly — Truekind and Anthropic ship no preloader layer; reading starts on load (observed, implementation unverified). Never a generic percentage spinner.

**Mid-page life** — sparse by law, and the sparseness is the tier's data: the reader's eye cadence is the effect; the prose carries almost no animation. Warm magazine keeps the passage alive on four thin channels — the eased wheel, one masked `translateY` line-reveal per heading that fires once and holds (opacity stays 1 — a mask, never a fade), hover on the links/CTAs/cards that punctuate the prose, and imagery seated at rest `scale(1.2)` inside `overflow:hidden` (Truekind 7.47, winner-verified). Dark cinematic refuses the prose middle outright — Siena 7.9 ships no tall reading zone; the middle is a hand-dragged filmstrip, an interaction not a passage (winner-verified). Hover-on-text is card-triggered `text-decoration:underline` on titles, full stop — of Truekind's 47 `:hover` rules, zero touch body prose, in-flow headings, or numerals (winner-verified enumeration, single research pass). The reading *text* never scrubs — but figures may: Truekind runs reversible image parallax mid-page (`ingredients__image` translateY, returning on scroll-back — 6 of 400 sampled elements, refuter-driven); prose stays un-scrubbed, and what re-plays on text re-plays on hand input (drag, hover), never on scroll passes.

**Scroll texture** — floating-product parallax, layers drifting at offset rates so the objects feel suspended (Truekind, winner-verified); the hold-and-drag filmstrip, lateral motion earned by the reader's own hand (Siena, winner-verified); WebGL displacement passing over stills. The design_plan names one — the story needs a physical carry between scenes, not chapter-break fades alone. Smoothing is Lenis on both the warm and the cinematic registers — Truekind `html.lenis` live-verified; Siena runs Lenis for input smoothing synced to its OGL canvas (the document never grows; `lenisVersion` live, refuter-verified) — native scroll only on the pure light register (Anthropic, control).

**Idle band** — thin by canon, ~1 channel: reading is the activity, so winners keep at most one quiet ambient channel alive between inputs. Commit it — or its declared absence — in the design_plan, so the stillness reads as editorial confidence rather than an unbuilt substrate.

**Anti-signals** — absent from every winner examined: a pale / low-opacity accent-tint fill on a primary control (winners fill the full token and invert the label); a frosted `backdrop-filter:blur()` bar with a contrasting-colour `border-bottom`; the `mix-blend-mode:difference` circular follower; uniform fire-once `y:30, .6s, ease-out` reveals on everything (winners run slower expo/quint eases, mask by line/word, keep panels reversible, author one scroll mechanic per story); a generic percentage-counter preloader; and the same interaction mechanism cloned across button, link, image and nav. Reversible panels carry conditions: a reversible *content* reveal stays a declared DESIGN.md choice, `cover`-phase-ranged so nothing vanishes mid-read (motion-palette.md).

Channel calibration — this line's winners run 3–4 distinct interaction channels (per-class states, display-type effects, cursor, idle, scroll texture, replayable spectacle); the pre-emit critique's Aliveness axis reads against that band, never against bare coverage.

## Page recipe — how this line's winners build the page

Corpus — Siena Film Foundation (live DOM + CSS + JS), Truekind Skincare (live SSR + Codrops), Anthropic (live control), Bisous + Stefan Vitasović + Dondre Green (media-only, Codrops).

**Anatomy** — *The Reel Index* (`gated-reel`; Siena, winner-verified structure): ENTER gate + onboarding → featured-film masthead · attention (climax) → hold-and-drag filmstrip, 8 works, jury pull-quotes · proof → per-work case study · proof, rest → contact close; lateral length, not tall. *The Standfirst Stack* (`standfirst-stack`; Anthropic, winner-verified): serif-statement hero · attention → belief index · understanding → release cards · proof → mission close · close → tabular footer; even intensity, reading-first. *The Floating Editorial Scroll* (`maison-scroll`; Truekind, winner-verified sections): type-pledge hero · attention → value chapters, floating product · proof → product index · proof/close → journal teaser · rest → social-grid connect · close; float Codrops-documented, parallax (observed, implementation unverified).

**Hero architectures** — *Featured-work masthead* (Siena): no `<h1>`; oversized display title over a full-bleed treated still, metadata stamp (DOCUMENTARY · 2022 · MIN.77); display face Neue Brucke, eyebrow P22 Parrish Roman (corrected — TNY appears in none of its assets); nav a `pointer-events:none` scrim; entrance = the two-layer kinetic label roll (eases winner-verified):

| element | order | transform | duration | easing |
|---|---|---|---|---|
| headline chars, visible / duplicate | 1 (stagger .1s) | `translate(100%)` out / `translateY(-150%)` in | .8s | `--easeOutQuint` |
| panels / stills | 2 | clip/scale reveal | `--panels-duration .9s` | `--customEase` |

*Statement-serif split* (Anthropic, winner-verified): serif H1 in custom 'Anthropic Serif' (Georgia fallback) + sans standfirst. *Type-pledge + floating product* (Truekind, winner-verified fonts/H1): Editorial New over PP Mori, product floats in cream space.

**Footer** — *wordmark-contact-close* (Siena, winner-verified copy): "LET'S TALK" / "EMAIL US" / lee@siena.film / "©2024. SIENA FILM FOUNDATION.". *Tabular-index* (Anthropic, winner-verified columns): ivory wrap, same-family hairline `border-top` (`--swatch--ivory-medium`), serif links (technique). *Social-grid-functional* (Truekind, winner-verified copy): "Connect With Us" / "on instagram" grid, "Website By:" credit.

**Arrival** — register split per the Loader row; named handoffs (`ingredients/preloaders.md`): gate-into-fold (Siena, winner-verified copy — ENTER dismissing into the composed masthead); grid-flip-into-wordmark (Dondre, technique); loader-into-slider (Bisous, technique / media-only); instant paint (Anthropic + Truekind, observed). Route transitions (`ingredients/page-transitions.md`) rhyme with subject: product-colour flood (Truekind, technique); camera-shutter mask, Barba.js (Dondre, technique); continuous unfold (Bisous, technique / media-only).

**Copy voice** — Quoted to calibrate, never to ship — imitate the specificity (the named place, the count, the refusal), never the wording. Three registers, one refusal — proof is borrowed, never claimed; the page never describes itself. Dark cinematic: impersonal curator, fragments, imperatives in chrome only. Light editorial: first-plural institution, cool mission verbs, full-stop headings. Warm magazine: reader-directed pledge, fragment headings, lowercase affectations. Apostrophes: Siena straight ', Anthropic curly ’ — copy the source glyph.
- "BreathtakiNg cinematography" (Siena jury quote, casing [sic]) — borrowed proof, exact chars.
- "Hold and drag to navigate the content" (Siena onboarding) — instruction as invitation.
- "Anthropic is built on hard questions." (Anthropic) — a full stop turns a heading into a statement.
- "Radical Transparency. Hide Nothing." (Truekind) — two fragments, one refusal.

**Imagery art direction** — subject owned, never stock; one treated grade page-wide; full bleed for image, protected measure for text. Siena: film stills, desaturated high-contrast duotone lean, edge-to-edge, source light kept; substrate pure black (Webflow `var(--black)`), `#0e0e0e` secondary, cream `#faf7ef` type (corrected — #141413 appears nowhere in its assets; keep the off-black floor). Truekind: product-as-still-life in cream space, warm soft light. Anthropic: terracotta/clay on cream, illustration not photography (observed).

**Spectacle menu** — *Siena hold-and-drag filmstrip*: grab the reel → stills slide, titles roll via the doubled-char label (.8s `--easeOutQuint`) → EXPLORE opens the case; payoff — a reel threaded by hand (shipped; eases winner-verified). *Truekind product-colour flood*: click a product → its background colour floods full-screen, the page resolving in it (technique).

**Anti-signals** — no card-grid opener; no percentage-counter preloader; no hero carousel (lateral motion is hand-dragged or is the content); no centered-hero + twin-CTA; no poured-text wall; no self-narration; no raw stock; no mixed copy register.
