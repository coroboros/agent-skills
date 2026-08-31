# Editorial / Magazine

The web as print. Multi-column grids, asymmetric measure, pull quotes breaking flow. The defining characteristic is the serif-meets-sans pairing — a high-contrast typographic dialogue that signals reading-first hierarchy. Photography and illustration earn full bleeds; text retains its measure.

Tier 1 (DNA, anti-signals, macrostructures, reflexes) is `references/archetype/editorial.md`, pushed into context by `scripts/direction_roll.py`. This file is tier 2: it loads at the design_plan commit, by heading, never whole.

## Contents

- [Canonical reference — Siena Film Foundation](#canonical-reference--siena-film-foundation)
- [DNA — non-negotiable](#dna--non-negotiable)
- [Common expressions](#common-expressions)
- [Typography](#typography) · [Color](#color) · [Layout](#layout) · [Motion](#motion)
- [The words — copy is composed, not poured](#the-words--copy-is-composed-not-poured)
- [What makes it award-worthy](#what-makes-it-award-worthy) · [Ideal for](#ideal-for) · [Cross-references](#cross-references)
- [Effect palette — what this line's winners ship](#effect-palette--what-this-lines-winners-ship) — per-element-class recipes, the grammar, tap/focus/dormancy
- [Mid-page life](#mid-page-life) · [Scroll texture](#scroll-texture) · [Idle band](#idle-band) · [Channel calibration](#channel-calibration)
- [Page recipe — how this line's winners build the page](#page-recipe--how-this-lines-winners-build-the-page) — anatomy, hero, section chain, footer, arrival, copy, imagery, mobile, variation
- [Spectacle menu](#spectacle-menu) — the hero beat, the continuation beats, the peak law

## Canonical reference — Siena Film Foundation

**Site.** Siena Film Foundation
**URL.** `siena.film`
**Award.** Awwwards Site of the Day, 2025-03-18 + Developer Award — 7.9 overall (Design 7.99 / Usability 7.61 / Creativity 8.13 / Content 8). Site of the Month March 2025 per the sites_of_the_month listing; the site's own Awwwards page carries no SOTM badge.
**Studio.** G-NS Studio.

The strongest editorial reference in the 2024–2026 window. Awwwards' own case study describes its design as editorial typography in a minimalist filmic structure, and names its mechanics: Film Strip Slider, Dynamic Menu, Contact Type Lettering, Procedural Slider Re-Arrangement. Grotesque-serif voice, cinematic filmstrip slider, vintage-poster type, dual-menu editorial navigation, parallax photo-driven storytelling. Translates the magazine grammar of a print monograph into the browser more cleanly than any 2025 SOTY contender. Substitutable peers: `anthropic.com` (terracotta-on-cream warm editorial), `newyorker.com` (canonical magazine grammar), `substack.com` (writer-centric warm editorial).

Evidence bar for everything cited from this site below: the mechanic families are verified by the Awwwards entry; the exact selectors, transforms, durations, and the "no semantic `<h1>`" reading come from an internal teardown, not from any source reachable without the live DOM. Build the mechanic, treat the values as illustrative.

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
- **Compose the type as the image** — one display word owning the frame at 20–40vw, tight negative leading, a deliberate overlap or second layer; scale, not decoration, carries the peak (the Brody / *The Face* move).
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

Provenance for every claim below — the researcher rounds and the fresh-context refutations that corrected them — lives in the public research corpus of `github.com/coroboros/research`, under `articles/award-winning-websites-2025-2030/`: `archetypes/editorial.md`.

## Effect palette — what this line's winners ship

Corpus — Siena Film Foundation (Awwwards SOTD 2025-03-18 + Developer Award, 7.9 overall — Design 7.99 / Usability 7.61 / Creativity 8.13 / Content 8, by G-NS Studio; SOTM March 2025, listing-verified), Bloom Paris (SOTD 2025-05-07, 7.52 overall — Design 7.67 / Usability 7.22 / Creativity 7.73 / Content 7.41, by Beaucoup.; Codrops case study 2025-07-08), Bisous (Awwwards HM 2026-04-08, by Beaucoup.; Codrops case study 2026-06-29), KAI Design Dept. (Awwwards HM; Codrops technical case study 2025-11-20), Grit Pictures (Awwwards HM 2025-09-05, 7.5 community average — register evidence only, its interaction mechanics undocumented), Harvard Film Archive (SOTD 2019-09-18, 7.43 — pre-window institutional-archive precedent, no rule rests on it), Anthropic (brand-site control), Truekind Skincare (SOTD 2025-04-29 + Developer Award — a light skincare brand, carried here as generic micro-interaction reference with no editorial-dark evidentiary weight), plus case-study reads on Exat, Cartier 365, Dondre Green, Stefan Vitasović. Bloom and Bisous are the same studio (Beaucoup.), so the loader-as-first-scene and continuous-surface arcs lean on one house style — legal resolutions, thin as canon. Provenance splits: Anthropic's mechanics are read live from its CSS; Siena's are named by its Awwwards entry with the selectors, transforms and durations internal-source; motion, loaders and text choreography come from studio case studies.

**The grammar** — variety coheres because each element class runs a *different* mechanism over a shared substrate, tied by one gesture that rhymes: something rolls, swaps, or inverts. Siena reuses a named ease library — `--easeOutQuint: cubic-bezier(.23,1,.32,1)`, `--customEase: cubic-bezier(.19,1,.22,1)`, `--easeOut: cubic-bezier(.77,0,.175,1)` — quiet feedback at `~.2s`, signature moves at `.5–.8s` (internal-source values; the two-register split is the transferable part); Truekind converges on `cubic-bezier(.18,.71,.11,1)` at `.8–1s`. Both land on slow expo/quint out-eases (`~.8–1.1s`), well past the AI-default `.6s`/power2. Accent logic is ink-inversion tied to the section behind — cream ↔ black with one red for emphasis (Siena), token-swap on a single `.2s` transition (Anthropic) — never a decorative line. Cohere on easing + palette + one gesture, or on a token system + one timing + a serif voice in the chrome.

**Buttons / CTA**
- **Full-fill + ink inversion (primary/secondary).** Outline or light button fills a *solid* brand value, label flips to the opposite ink — never a pale tint. Siena's all-work CTA floods to solid with its nested arrow inverting the opposite way (mechanic verified, selector and `.5s` timing internal-source); Anthropic play button bg↔text at `.2s`; Truekind `.btn.outline:hover { background:#3b3b3b; color:#fff }` as the generic cross-archetype form. Default for the main CTA. (Siena SOTD 2025-03-18; Anthropic control; Truekind cross-archetype)
- **Two-layer kinetic label roll (signature hero CTA).** Siena `[data-btn=explore]`: SVG shape fills transparent→white, stroke flips to black, and the label *rolls* — visible copy slides `translate(100%)` out while a duplicate below rolls `translateY(-150%)` in, both recolouring to the ink, staggered `.1s`; `--duration:.8s` on `--easeOutQuint`. The loud move — fill *and* kinetic label. (Siena SOTD 2025-03-18; mechanic named by the Awwwards entry, transforms and durations internal-source, single-source)
- **Kinetic marquee label.** Truekind `.btn`: static label fades to `0` while `.marquee__inner` starts scrolling on hover, `.4s`. Pick when the word itself should feel alive. (Truekind SOTD 2025-04-29, cross-archetype borrow)
- **Accent-token fill (persistent nav CTA).** Anthropic nav CTA fills the full clay accent (`--swatch--clay`), text via `-hover` tokens; Truekind `.navbar-cta` is a charcoal `#333` pill, `background 1s cubic-bezier(.18,.71,.11,1)`. The one neutral one-step (`cloud-light`) is reserved for secondary/code buttons — never the primary. (Anthropic control; Truekind cross-archetype)

**Links**
- **Underline drawn from origin-left.** `.link:hover:before { transform:scaleX(1); transform-origin:0 50% }`, retracting rightward when already active. A drawn line, never a snap. (Truekind — a light skincare SOTD; the mechanic is generic, the citation carries no editorial-dark weight)
- **`text-decoration-color` fade with context-varying offset.** Anthropic holds `text-decoration-color:transparent` at rest, transitions to ink at `.2s`, `text-underline-offset` tuned per context — `.2em` nav, `.18em` dropdown, `.25em` footer. The varied offset is itself a coherence tell. (Anthropic control)
- **Randomized per-letter transformation on hover.** Bisous menu links replay the stochastic letter settle rather than drawing a line — the dark-cinematic variant, rhyming with the page's type texture. (Bisous, Codrops 2026-06-29; easings and durations described qualitatively, never published)

**Figures / cards**
- **Contained zoom.** Siena `.previousnext-item:hover .full-img-w { transform:scale(1.1) }` inside `overflow:hidden`. Baseline, present everywhere — felt, never a 1–3% twitch. (Siena SOTD 2025-03-18; selector internal-source)
- **Focus / defocus siblings.** The hovered figure sharpens while neighbours blur and dim, so attention is *directed* — Dondre stories page, WebGL displacement. Pick for a gallery where one item should win the eye. (Dondre Green, Codrops case study)
- **Index footage preview.** For a body of film work the canonical row reveal is the footage itself: hovering a project title surfaces its muted video in one cursor-attached floating layer, a marquee title gliding over it. Stronger than the text-only spotlight-dim on this archetype's content. (Bloom "Hover listing archives", SOTD 2025-05-07 + Codrops 2025-07-08)

**Nav** — three verified treatments, none frosted, none with a contrasting `border-bottom`:
- **Transparent + gradient scrim + ink-inversion by section (dark cinematic).** Siena `.nav-w`: `position:fixed`, `pointer-events:none`, no bar; legibility from a `linear-gradient(#000,#fff0)` top scrim; a section class flips ink (`.on-dark .logo { color:#000 }`). (Siena SOTD 2025-03-18; selectors internal-source)
- **Solid theme-bg bar + same-family hairline (light editorial).** Anthropic `.nav_wrap { background: theme-background }` ivory, hairline as a `border-top` in `--swatch--ivory-medium`, links set in the display serif — the chrome carries the editorial voice. (Anthropic control)
- **Labeled-tag secondary nav (diegetic craft).** Bisous dresses its secondary nav as production-software tags. The one sanctioned register break: it reads as craft chrome, and it never enters the prose. (Bisous, Codrops 2026-06-29)
- Winners never frost the bar or hang a contrasting-accent underline; contrast comes from ink inversion tied to the section behind.

**Text** — one signature type move per site, everything else quiet entrance.
- **Variable-font axis morph (peak).** Exat: real-time `wght`/width transition on hover, one axis at a time; a proximity glyph grid where cursor distance drives per-glyph weight `200–900`. `opsz` — the axis that redraws outlines — is the highest-leverage editorial peak; Anthropic ships `font-variation-settings:"opsz" 50` on its base `.button` in production. (Exat, Codrops case study) (single-source)
- **Type-as-image masthead.** One display word owning the frame; Siena's vintage-poster masthead over cinematic stills is the dark-register expression. (Siena SOTD 2025-03-18)
- **Stochastic per-letter opacity settle.** Every letter on its own randomized delay and duration, dipping mid-flight before resting at 1 — the imperfection of a film grade applied to type, and distinct from a positional stagger or charset noise. Recurs on every title, caption and link to the footer. (Bisous, Codrops 2026-06-29)
- **Char-assemble entrance (supporting).** Stefan: chars come together, masked for glass-like parallax, `duration 1.25 + index*0.025`s, stagger `.025`s, `easeExpOut`. The rare fully-specified reveal. (Stefan Vitasović, Codrops case study)

**Cursor** — the editorial default is the real system pointer: Siena, Truekind, Anthropic all ship `cursor:pointer` on interactives, `grab` on sliders, no custom sprite. When a winner touches the pointer it *does work* — a lens that unblurs text (Dondre 404) or proximity that drives glyph weight (Exat) — never a `mix-blend-mode` follower. On an operable field the sanctioned exception is the verb label: over a filmstrip, drag-scrub video, or reel the cursor morphs to the verb it teaches — DRAG, HOLD, VIEW, a play triangle — and retracts to default on exit, so the affordance is taught visually rather than only by onboarding copy. (pattern-class: Awwwards cursor-customization resources and the Hovers/Cursors + Drag/Gestures collections; no single pinned winner this run)

**Loader / intro** — register split. Dark cinematic seeds the first frame, and the strongest form is diegetic: the curated visuals during load are the opening scene, dissolving into the first live frame with no separate intro (Bisous, Codrops 2026-06-29; Bloom's animated loader opens directly on the showreel, SOTD 2025-05-07 — both Beaucoup., so the arc rests on one studio). Siena's neo-romanesque stripes transition *into* the first section, the ENTER gate doubling as loader and sound gate; Dondre's letter-grid resolves into the hero wordmark. Light editorial paints instantly — Truekind and Anthropic ship no preloader layer; reading starts on load (observed, implementation unverified). Never a generic percentage spinner.

**Element states — tap, focus, dormancy.** The pointer layer is one costume of the state; the tap and focus answers are not optional and not a degraded copy.
- **CTA** — the full-token ink-inversion fill is the tap answer, `:active` flash 90–160ms floor, no hover intermediary on touch. `:focus-visible` mirrors hover — same fill and inversion — plus an ink or accent ring, reachable in keyboard order.
- **Link** — instant recolor with the underline already present on touch, no drawn animation. `:focus-visible` shows the underline plus the accent, offset matching its context.
- **Figure** — hover pairs the contained zoom with one companion cue (caption rise, scrim lift, tint); the gallery variant sharpens the hovered figure while siblings blur and dim; the operable variant scrubs the footage under hover or drag. Tap enlarges or navigates, and drag scrubs natively on touch. `focus-within` fires the same zoom and cue so keyboard users reach revealed captions.
- **Index row** — on a body of film work the reveal is the footage (the index footage preview, commonly cursor-tracking); text-only lists fall back to the row lighting an accent rule with siblings dimmed to ~45%, `~.3s` on the signature ease. Touch navigates on tap or plays inline, with a brief press flash and no sibling dim. `:focus-visible` lights the row — or shows a poster frame — identically.
- **Heading** — no hover on in-flow headings; hover on a title happens only inside a card or index-row context. The entrance is the whole motion — masked line reveal, per-char assemble, or the stochastic per-letter settle — fire-once, opacity holding 1, a mask never a fade.
- **Nav** — links recolor and underline, or roll per character; the bar is a `pointer-events:none` gradient scrim over the hero that gains ground on scroll and inverts ink by the section behind. Tap opens the dual-menu overlay. Scrolling up reveals the bar, focus rings sit on the links, and the scrim never traps focus.
- **Cursor** — the verb label lives on pointer-over of an operable field only. No touch equivalent, never focus-driven: the keyboard reaches the operable content through its underlying controls, and touch gets a persistent swipe/drag hint or a next-cell peek instead.

**Anti-signals** — absent from every winner examined: a pale / low-opacity accent-tint fill on a primary control (winners fill the full token and invert the label); a frosted `backdrop-filter:blur()` bar with a contrasting-colour `border-bottom`; the `mix-blend-mode:difference` circular follower; uniform fire-once `y:30, .6s, ease-out` reveals on everything (winners run slower expo/quint eases, mask by line/word, keep panels reversible, author one scroll mechanic per story); a generic percentage-counter preloader; and the same interaction mechanism cloned across button, link, image and nav. Reversible panels carry conditions: a reversible *content* reveal stays a declared DESIGN.md choice, `cover`-phase-ranged so nothing vanishes mid-read (motion-palette.md).

## Mid-page life

The prose carries almost no animation and that sparseness is the tier's data — the reader's eye cadence is the effect — but no section after the hero is static: the failure this line punishes is silence, not a second peak (structurally verified across Siena, Bloom, KAI, Bisous). Every section past the hero owes at least one of the chosen thread applied to its imagery, the operable-drag verb, or an entrance/hover on its type and figures; a section with no entrance motion, no hover state, and no operable media is illegal. Dark cinematic refuses the prose middle outright — Siena 7.9 ships no tall reading zone; the middle is a hand-dragged filmstrip, an interaction not a passage (winner-verified). Bloom re-spends hero momentum in two distinct mid-page mechanics — a stacked-card scroll in the services band and a project-grid hover where a marquee title glides over the preview footage — before the operable reel (SOTD 2025-05-07 + Codrops 2025-07-08). KAI drops the hero/middle seam entirely: the whole body is one drag-scrubbed touchable video field at even-high amplitude (Codrops 2025-11-20). Bisous runs the per-letter opacity flicker on every title and link to the footer (Codrops 2026-06-29). Warm magazine keeps the passage alive on four thin channels — the eased wheel, one masked `translateY` line-reveal per heading that fires once and holds (opacity stays 1 — a mask, never a fade), hover on the links/CTAs/cards that punctuate the prose, and imagery seated at rest `scale(1.2)` inside `overflow:hidden` (Truekind 7.47, SOTD 2025-04-29 + Developer Award — a light skincare brand: the mechanics transfer, the citation carries no editorial-dark evidentiary weight). Hover-on-text is card-triggered `text-decoration:underline` on titles, full stop: the corpus's published hover rules touch no body prose, in-flow heading, or numeral (the per-selector enumeration of Truekind's 47 `:hover` rules is internal-source, single research pass). The reading *text* never scrubs — but figures may: Truekind runs reversible image parallax mid-page (`ingredients__image` translateY, returning on scroll-back — 6 of 400 sampled elements, refuter-driven); prose stays un-scrubbed, and what re-plays on text re-plays on hand input (drag, hover), never on scroll passes.

## Scroll texture

What carries the eye between scenes: floating-product parallax, layers drifting at offset rates so the objects feel suspended (Truekind, cross-archetype borrow); the hold-and-drag filmstrip, lateral motion earned by the reader's own hand (Siena, mechanic named by the Awwwards entry); a whole-section drag-scrub video field where pointer or touch delta maps to `video.currentTime` — release momentum is an optional implementation choice the source never documents, so never assert inertia (KAI, Codrops 2025-11-20); the infinite bidirectional vertical reel that is the page, wheel or drag on desktop under eased momentum, native swipe on touch (Bisous, Codrops 2026-06-29); WebGL displacement passing over stills. The design_plan names one — the story needs a physical carry between scenes, not chapter-break fades alone.

On multi-view builds the seam itself is the second carrier, and this line's dark register runs it curtain-*less*: the outgoing figure flows into the incoming one, fluid and almost imperceptible, immersion never broken by a cover phase (Bisous, Codrops 2026-06-29). Smoothing is Lenis on both the warm and the cinematic registers — Truekind `html.lenis` live-verified; Siena runs Lenis for input smoothing synced to its OGL canvas (the document never grows; `lenisVersion` live, refuter-verified) — native scroll only on the pure light register (Anthropic, control).

## Idle band

Thin by canon, ~1 channel: reading is the activity, so winners keep at most one quiet ambient channel alive between inputs. In the dark register that channel is the ground itself — a fixed film-grain and vignette overlay holding the poster grade under everything, which survives on touch at reduced amplitude rather than switching off. Commit the channel — or its declared absence — in the design_plan, so the stillness reads as editorial confidence rather than an unbuilt substrate.

## Channel calibration

Channel calibration — this line's winners run 3–4 distinct interaction channels (per-class states, display-type effects, cursor, idle, scroll texture, replayable spectacle); the pre-emit critique's Aliveness axis reads against that band, never against bare coverage.

## Page recipe — how this line's winners build the page

Corpus — Siena Film Foundation (live DOM + CSS + JS via an internal teardown; mechanics named by the Awwwards entry), Bloom Paris (Awwwards entry + Codrops), Bisous (Codrops), KAI Design Dept. (Codrops), Grit Pictures (register evidence only), Harvard Film Archive (pre-window precedent), Anthropic (live control), Truekind Skincare (live SSR + Codrops, cross-archetype), Stefan Vitasović + Dondre Green (media-only, Codrops).

**Anatomy** — *The Reel Index* (`gated-reel`; Siena, winner-verified structure): ENTER gate + onboarding → featured-film masthead · attention (climax) → hold-and-drag filmstrip, 8 works, jury pull-quotes · proof → per-work case study · proof, rest → contact close; lateral length, not tall. *The Standfirst Stack* (`standfirst-stack`; Anthropic, winner-verified): serif-statement hero · attention → belief index · understanding → release cards · proof → mission close · close → tabular footer; even intensity, reading-first. *The Floating Editorial Scroll* (`maison-scroll`; Truekind, winner-verified sections): type-pledge hero · attention → value chapters, floating product · proof → product index · proof/close → journal teaser · rest → social-grid connect · close; float Codrops-documented, parallax (observed, implementation unverified). *The Continuous Surface* (Bisous, Codrops-verified; KAI a single-product variant): a loader that is the opening scene → one infinite bidirectional vertical reel or one operable drag-scrub video field as the entire body → curtain-less work-to-work seams → bare-cue or costumed-credits footer. It has no hero-then-sections seam: the macrostructure is the continuation. No page-anatomy catalog slug names it yet, and both instances trace to one studio or one single-product page — a legal resolution, thin as canon.

Route on the brief's declared inputs, never on a taste read: an archive or body of work (film foundation, production house, cinematographer) → `gated-reel`, threshold then masthead then an archive the reader drives. An institution, reading-first, spectacle explicitly forbidden → `standfirst-stack`, even intensity, voice in the chrome. Editorial commerce that hides the shop behind "Discover" → `maison-scroll`. A single continuous material — one CGI reel, one craft object → the continuous-surface resolution. A rough or DIY brand → the monochrome rough-cut montage, torn-edge collage sequenced like a scrapbook (Grit Pictures, HM 2025-09-05, register evidence only). Default to `gated-reel` when the brief decides nothing else. All are decidable from stated brief facts; never blend two spines.

**Hero architectures** — *Featured-work masthead* (Siena): oversized display title over a full-bleed treated still, metadata stamp (DOCUMENTARY · 2022 · MIN.77); display face Neue Brucke, eyebrow P22 Parrish Roman (corrected — TNY appears in none of its assets); nav a `pointer-events:none` scrim; the `<h1>` is reportedly absent (internal teardown, not independently verified); entrance = the two-layer kinetic label roll:

| element | order | transform | duration | easing |
|---|---|---|---|---|
| headline chars, visible / duplicate | 1 (stagger .1s) | `translate(100%)` out / `translateY(-150%)` in | .8s | `--easeOutQuint` |
| panels / stills | 2 | clip/scale reveal | `--panels-duration .9s` | `--customEase` |

The Awwwards entry names the mechanic (Contact Type Lettering, Film Strip Slider); every transform, stagger and duration in the table is internal-source — build the doubled-label roll, treat the numbers as illustrative. *Statement-serif split* (Anthropic, winner-verified): serif H1 in custom 'Anthropic Serif' (Georgia fallback) + sans standfirst. *Type-pledge + floating product* (Truekind, winner-verified fonts/H1): Editorial New over PP Mori, product floats in cream space. *Loader-scene hero* (Bisous, Codrops-verified): the cinematic loader resolves straight into the first live panel and the title lands on the stochastic per-letter settle. On any drag or operable page the hero also hands over the verb — the cursor morphs to its label the moment the pointer crosses the operable field.

**Section chain** — the section roles with their intensity map and the state each owes. The intensity numbers are ordinal authoring targets, not measured DOM reads; the shape they encode (hero dominant, reel near-hero, detail reduced-but-nonzero, close a single re-expression, no silence) is what is verified. Build each role as its row describes; never improvise the hero or a section layout outside the chain.

| role | form | pairs | intensity | state it owes |
|---|---|---|---|---|
| threshold | ENTER gate splash; loader-scene (continuous-surface) | overlay grain-and-vignette; enter full-fill ink inversion \| two-layer kinetic label roll | 7 | the ENTER control must answer hover/focus — a dead ENTER hover is the first impression lost; doubles as the sound gate; authored hidden so no-JS shows the page |
| hero | full-bleed treated still behind an oversized display masthead; type-as-image (poster masthead) | h1 masked line reveal \| doubled two-layer label roll \| stochastic per-letter settle; media scrubbed footage \| clip-path reveal; grade grain-and-vignette; data-strip mono stamp; cursor verb label | 9 | `pointer-events:none` gradient-scrim nav over the still, never a bar; the entrance is the signature; the hero hands over the verb reused below — a pointer-dead hero is a defect |
| reel / proof | hold-and-drag filmstrip (desktop); fullscreen vertical reel; drag-scrub video field | caption prose emphasis fill; media grayscale-to-colour curtain wipe; rows index footage preview; cursor verb label; mobile native scroll-snap swipe | 8 | the operable-drag verb sustains at near-hero amplitude — grab-drag on desktop, native scroll-snap on touch; rows reveal their muted footage on hover; titles roll on the same doubled label; jury pull-quotes borrowed, never claimed |
| feature / detail | text/media split (media left/right); stacked-card scroll | h2 char-assemble entrance; prose emphasis fill + key-term accent; media grayscale-to-colour curtain wipe; spec counter roll | 6 | rest but not silent — the grade and one text signature stay alive; figures answer hover with contained zoom; no hover on in-flow headings; measure held at 60–75ch; reversible image parallax legal, prose never scrubs |
| close | closing panel: one imperative + channel rows; contact modal (Bloom) | ask masked line reveal; channels accent recolor + underline + label roll; trust mono line | 6 | re-spends the thread exactly once — one imperative (18ch cap), decisive channel rows answering hover and tap, a quiet trust line a full rest below; no media slot, so the close cannot become a mood reel |
| footer | oversized wordmark; bare cue / costumed credits (continuous-surface) | wordmark masked line reveal | 6 | the grade and the thread reach the footer; an oversized signed wordmark, or a designed thin credits refusal when the body already spent the spectacle; the palette may flip once here |

**Footer** — *wordmark-contact-close* (Siena, winner-verified copy): "LET'S TALK" / "EMAIL US" / lee@siena.film / "©2024. SIENA FILM FOUNDATION.". *Tabular-index* (Anthropic, winner-verified columns): ivory wrap, same-family hairline `border-top` (`--swatch--ivory-medium`), serif links (technique). *Social-grid-functional* (Truekind, winner-verified copy): "Connect With Us" / "on instagram" grid, "Website By:" credit. *Costumed credits* (continuous-surface): a thin credits close is a designed refusal, not an omission, once the body has already spent the spectacle. Author the tabular-index and contact-first footers with the same care as the oversized wordmark rather than improvising chrome.

**Arrival** — register split per the Loader row; named handoffs (`ingredients/preloaders.md`): gate-into-fold, where the gate is the arrival and doubles as loader and sound gate (Siena, winner-verified copy — ENTER dismissing into the composed masthead); loader-as-first-scene, the curated load visuals reading as the opening shot before they dissolve into the live frame (Bisous + Bloom, Codrops-verified — both Beaucoup.); grid-flip-into-wordmark (Dondre, technique); instant paint, a winner-verified absence on the light register (Anthropic + Truekind, observed). Route transitions (`ingredients/page-transitions.md`) rhyme with subject: curtain-less continuous unfold (Bisous, Codrops-verified); product-colour flood (Truekind, technique); camera-shutter mask, Barba.js (Dondre, technique).

**Copy voice** — Quoted to calibrate, never to ship — imitate the specificity (the named place, the count, the refusal), never the wording. Three registers, one refusal — proof is borrowed, never claimed; the page never describes itself or credits its own build. Dark cinematic: impersonal curator, fragments, imperatives confined to chrome. Light editorial: first-plural institution, cool mission verbs, full-stop headings. Warm magazine: reader-directed pledge, fragment headings, lowercase affectations. Metadata is stamped as mono fact (DISCIPLINE · YEAR · RUNTIME). Kicker default absent — it ships only when it carries a real category or date. Apostrophes: Siena straight ', Anthropic curly ’ — copy the source glyph, and the dark register takes the straight one. The single sanctioned register break is diegetic craft chrome (Bisous' production-software tags), which never enters the prose.
- "BreathtakiNg cinematography" (Siena jury quote, casing [sic]) — borrowed proof, exact chars.
- "Hold and drag to navigate the content" (Siena onboarding) — instruction as invitation.
- "Anthropic is built on hard questions." (Anthropic) — a full stop turns a heading into a statement.
- "Radical Transparency. Hide Nothing." (Truekind) — two fragments, one refusal.

**Imagery art direction** — subject owned, never stock; one treated grade page-wide; full bleed for image, protected measure for text. Siena: film stills, desaturated high-contrast duotone lean, edge-to-edge, source light kept; substrate pure black (Webflow `var(--black)`), `#0e0e0e` secondary, cream `#faf7ef` type (corrected — #141413 appears nowhere in its assets; keep the off-black floor). Grit: monochrome torn-edge collage, video and illustration under one black-and-white grade — the rough-cut variant, proof the archetype is not only the polished poster. Truekind: product-as-still-life in cream space, warm soft light. Anthropic: terracotta/clay on cream, illustration not photography (observed). Every graded image reveals through a grayscale-to-colour curtain wipe — the wipe arrives grayscale and the colour floods late, so the reveal itself runs the grade transition.

**Mobile / touch** — pointer classes go dormant and that dormancy is the winner answer, not a gap: pointer-parallax, magnetic cursor, the focus / defocus sibling blur, and the conic border shine are fine-pointer only, and depth comes from scroll. Press-class elements carry the load — the full-fill ink inversion answers the tap with a 90–160ms flash floor, index rows navigate on a brief press flash with no sibling dim. The desktop hold-and-drag filmstrip and every horizontal reel switch to native scroll-snap on OS momentum (next-cell peek, enhancer-fed snap dots, zero JS physics — the scored Mobile Excellence line). Drag-scrub video answers touch-drag natively; the infinite vertical reel is a native swipe. The index footage preview becomes tap-to-play-inline versus navigate. The cursor verb label has no touch equivalent — replace it with a persistent swipe/drag hint or a next-cell peek that teaches the same verb. Figures switch to tap-to-enlarge. Grain-grade and any shader ground stay but drop amplitude, and reduced-motion degrades scrubbed media to a static graded poster.

**Variation** — this section chain is one legal costume of the archetype, never *the* skeleton. Structure is story-native: the body's sections derive from the universe's spine, then check against these roles for coverage — never the reverse. The axes serial winners measurably rotate between builds (21-artifact corpus, 5 studios): body content archetype and item counts, the one signature device (never reused across builds), the close mechanism, the hero medium, the index/HUD costume. What persists as DNA: type grammar, the motion register (the register itself, never the named reading/interaction kit — that kit is a device, rotated per build like the signature), annotation grammar as a form, engineering architecture. The same content archetype + item count + close mechanism recurring across two different-brand builds has zero winner precedent.

**Anti-signals** — no card-grid opener; no percentage-counter preloader; no hero carousel (lateral motion is hand-dragged or is the content); no centered-hero + twin-CTA; no poured-text wall; no self-narration; no raw stock; no mixed copy register.

## Spectacle menu

*Siena hold-and-drag filmstrip*: grab the reel → stills slide, titles roll via the doubled-char label → EXPLORE opens the case; payoff — a reel threaded by hand (mechanic named by the Awwwards entry; timings internal-source). *Bisous infinite reel*: the loader resolves into a full-screen vertical slider looping in both directions with no start and no end, one treated work per panel, seams that dissolve rather than cut; payoff — the material never stops arriving (Codrops-verified). *KAI touchable video*: grab-drag across a whole video field maps delta to `currentTime` under a WebGL line depth-of-field; payoff — the craft object turns under the reader's own hand (Codrops-verified). *Truekind product-colour flood*: click a product → its background colour floods full-screen, the page resolving in it (technique).

**The hero beat.** The first viewport commits the grade and the thread in one frame: a full-bleed treated still or a live cinematic loader-scene, an oversized display title as type-as-image, a mono metadata stamp, a `pointer-events:none` scrim nav. The entrance move is the signature — the two-layer doubled-char label roll, or the stochastic per-letter opacity settle. The hero does not merely display: it hands the reader the verb they will reuse below, and on an operable page the cursor morphs to name that verb.

**The continuation beats** — the page is diffed against these, section by section.
- *reel / archive* — **sustained near-hero**: an operable spectacle the reader drives by hand, titles rolling on the same doubled label, jury pull-quotes borrowed. Not a second wow, the same thread at working amplitude (Siena).
- *services / proof band* — **re-spent momentum**: a stacked-card deck pinning and peeling, plus a project-grid hover where a marquee title glides over the preview footage (Bloom).
- *per-work detail* — **rest, never silent**: a char-assemble heading, treated stills, spec counters; the grade and one text signature stay alive while the amplitude drops (Siena).
- *continuous surface* — **no discrete beats at all**: the infinite reel or the drag-scrub field is the whole body, amplitude even-high first frame to last, so the continuation is the macrostructure (Bisous verified; KAI a single-product variant).
- *work-to-work seam* (multi-view only) — **cross-view carrier**: curtain-less, the outgoing figure flowing into the incoming one, immersion unbroken.
- *close and footer* — **single re-expression**: one imperative, decisive channel rows, the thread spent once more; the grade reaches the wordmark.

**The peak law** — verdict refined, from the winner evidence. Two structural facts hold. First, the hero carries the single most dominant novel mechanic and no later section introduces a rival of equal or greater visual dominance, ranked by animated area × displacement — later sections re-express the one thread rather than adding a second wow. Second, no section after the hero is fully static: the failure this archetype punishes is silence, not a second peak. Cross-cutting mandate: choose exactly **one** thread family at the hero and carry it to the footer — the film grade (one desaturated high-contrast duotone or mono on every image, edge-to-edge, source light kept), the operable-drag verb (the reader's pointer or touch drives every still and video), or the type texture (a doubled two-line label roll, or a stochastic per-letter flicker on every heading, caption and link). The checkable constraint: the chosen family appears in the first viewport and recurs in every subsequent section; the other two may appear at most once, locally, and never as a page-wide system. In the continuous-surface expression the hero and body fuse into one operable or looping reel with no discrete peak at all — a legal resolution, thin as canon.

Evidence: Siena's hold-and-drag filmstrip after the masthead is a second operable spectacle at near-hero amplitude — the reader threads the reel by hand and the page is never silent after the hero (Awwwards SOTD 2025-03-18 entry naming Film Strip Slider + Dynamic Menu; exact timings internal-source). KAI runs no hero-then-quiet at all: the whole page is one drag-scrubbed touchable video, spectacle as a continuous operable surface (Codrops 2025-11-20). Bisous makes an infinite bidirectional vertical reel the home, with per-letter opacity flicker on every title and link to the footer — the thread structural and unbroken (Codrops 2026-06-29). Bloom re-spends hero momentum mid-page through a stacked-card scroll and a project-grid hover-preview before its operable reel, neither of them a rival to the hero (SOTD 2025-05-07 + Codrops 2025-07-08). Cross-archetype counter-evidence: Lando Norris (Awwwards SOTD 2025-11-17, 8.18; the monthly and annual titles unverified; by OFF+BRAND — immersive, not editorial) runs a double loud climax with rest bridges and a thread that never falls to silence; peaks can be two in a procession and even there they stay capped at ~2.
