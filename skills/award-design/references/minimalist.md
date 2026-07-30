# Minimalist

Two to three colors maximum. Every element justifies its existence. Typography carries the design where decoration would otherwise smuggle in. The archetype's discipline is subtraction — what remains is what matters.

Tier 1 (DNA, anti-signals, macrostructures, reflexes) is `references/archetype/minimalist.md`, pushed into context by `scripts/direction_roll.py`. This file is tier 2: it loads at the design_plan commit, BY HEADING, never whole.

## Contents

- [Canonical reference — Terminal Industries](#canonical-reference--terminal-industries)
- [DNA — non-negotiable](#dna--non-negotiable)
- [Common expressions](#common-expressions)
- [Typography](#typography) · [Color](#color) · [Layout](#layout) · [Motion](#motion)
- [What makes it award-worthy](#what-makes-it-award-worthy) · [Ideal for](#ideal-for) · [Cross-references](#cross-references)
- [Effect palette — what this line's winners ship](#effect-palette--what-this-lines-winners-ship) — per-element-class recipes, the grammar, tap/focus/dormancy
- [Mid-page life](#mid-page-life) · [Scroll texture](#scroll-texture) · [Idle band](#idle-band) · [Channel calibration](#channel-calibration)
- [Page recipe — how this line's winners build the page](#page-recipe--how-this-lines-winners-build-the-page) — anatomy, hero, footer, arrival, copy, imagery, section chain, mobile, variation
- [Spectacle menu](#spectacle-menu) — the hero beat, the continuation beats, the peak law
- [Component index](#component-index) — the library ids this archetype reaches for

## Canonical reference — Terminal Industries

**Site.** Terminal Industries
**URL.** `terminal-industries.com`
**Award.** Awwwards Site of the Month, September 2025 (+ Developer Award)
**Studio.** REJOUICE® and PROPAGANDE.

Operates a B2B yard-management OS. The textbook minimalist reference for 2025: two-color system, type-driven, generous whitespace, scroll-driven storytelling carried by a single cinematic photograph (a black truck silhouette against amber sky). One of the rare logistics-SaaS sites to crack SOTM tier — proof that restraint outperforms decoration in a category prone to overdesign. Substitutable peers: `linear.app` (Swiss-grid airy minimalism), `stripe.com` (off-white pages with surgical purple), `vercel.com` (pure grayscale with single emphasis weight), `mintlify.com` (reading-optimized Inter with green accent).

## DNA — non-negotiable

- Two to three colors maximum carry the entire system
- Macro whitespace (120–200px+ section padding on desktop) is active design, not absence
- Typography carries hierarchy through scale, weight, and color — never through chrome
- Single accent functions as punctuation — present once per viewport, never twice
- Every element answers the question "what would break if this disappeared"

The archetype keeps its identity across airy-Swiss (Linear, Stripe, Vercel), warm editorial-light (Notion, Anthropic adjacency), cinematic photography-led (Terminal Industries), and dark monochrome (Linear's dark mode). Background register is an expression choice, not a definition.

## Common expressions

Three stacks fit the DNA. Pick the one matching brand voice and content type.

### Airy Swiss-grid — Linear / Stripe / Vercel profile

Off-white foundation (`#FAFAFA`, `#F7F6F3`, `#FBFBFA`). Swiss typographic discipline — Geist, Söhne, or PP Neue Montreal at 48–96px headlines with surgical letter-spacing. Single accent (Linear violet, Stripe purple, Vercel pure grayscale with weight contrast only). Hairline dividers (`#EAEAEA`) where structure demands. Ideal for SaaS, developer tooling, design platforms, technical product marketing.

### Cinematic photography-led — Terminal Industries profile

Off-white or warm cream foundation (`#FAFAF5`, `#E8E4DF`) with one dominant cinematic photograph occupying full viewport — golden-hour silhouette, industrial scale, dramatic light. Glass-pill nav with one CTA in a single saturated hue (Terminal uses lime green). Type holds a supporting role; the photograph is the hero. Ideal for industrial brands, logistics, architecture studios, automotive marketing pages, single-product showcases.

### Dark monochrome — Linear dark / portfolio profile

Near-black foundation (`#0A0A0A`, `#0E0E12`) with off-white type, single saturated accent. Same Swiss discipline inverted. Ideal for high-end portfolios, design tool dark themes, technical documentation, developer-focused launch pages. Verified live at the tier on Pacome Pertant (`#0a0a0a`/`#fafafa`, Awwwards SOTD 2026-06-09, 7.76) and Clou (`#101114` + `#ffffff`, SOTD 2025-09-05, 7.29).

## Typography

Single family with weight contrast, or geometric sans (display) paired with humanist sans (body).

- **Headlines**: Suisse Int'l, Neue Haas Grotesk, Söhne, PP Neue Montreal, Geist — 48–120px, weight 500–700
- **Body**: same family at 16–18px, weight 300–400, line-height 1.6–1.7
- **Tracking**: tight on display (`-0.02em`), neutral on body
- **Variable-font features**: `tnum` for tabular numbers in dashboards and pricing, `ss01`–`ss04` where the typeface offers stylistic alternates

The "Inter everywhere" anti-pattern lives in this archetype's failure mode — pick a face with character. Terminal Industries uses Söhne; Linear uses Inter (paired with discipline that earns it); Anthropic uses its custom Anthropic Serif (Georgia fallback) for warmth. Inter as default H1 tells judges that no type decision was made.

## Color

Two to three colors carry the entire system.

- **Foundation**: warm neutrals (`#FAFAF5`, `#E8E4DF`, `#F7F6F3`) or cool neutrals (`#F5F5F0`, `#F8FAFC`) or near-black (`#0A0A0A`, `#0E0E12`)
- **Text primary**: `#2D2D2D` to `#111111` on light, `#E0E0E0` to `#FAFAFA` on dark
- **Text secondary**: warm gray `#787774` or cool gray `#6B7280`
- **Single accent**: electric blue `#007BFF`, sage `#87A98F`, terracotta `#C67D5B`, lime green (Terminal Industries), Linear's violet, Stripe's purple, sustainability sage
- **Borders**: `rgba(0,0,0,0.06)` or `#EAEAEA`

If you can remove a color and nothing breaks, remove it.

Terminal's specific hue names — the "cream + lime" pair and the odometer's gray→lime→dark-green run — are read from local notes, not from a swatch source that survived re-verification (the Awwwards page returns no swatches). Build the *mechanic* generically: foundation, one accent, one closing ground, the counter recoloring gray → accent → ground. The named hues are an illustrative reading, never a spec to match.

## Layout

Single-column or asymmetric broken-grid. One bold focal point per viewport. Generous macro-whitespace.

```css
.wrapper {
  display: grid;
  grid-template-columns: 1fr min(65ch, 100%) 1fr;
  gap: clamp(3rem, 8vw, 12rem);
  padding: clamp(2rem, 5vw, 8rem);
}
.wrapper > * { grid-column: 2; }
.full-bleed { grid-column: 1 / -1; }
```

The Josh W. Comeau full-bleed pattern is the standard for long-form content with breakout sections. Section padding pulls from `containers.section-padding` and scales through `clamp()`. The reading measure binds to `containers.read-measure` (typically 65ch).

## Motion

Restraint extends to motion — opacity-led, never showy.

- Reveals: `clip-path` / masked `inset()` wipes, 0.7–1s under `cubic-bezier(0.19, 1, 0.22, 1)` — the 20px translate fade-up is the AI default this line's winners avoid; keep `cubic-bezier(0.16, 1, 0.3, 1)` at ~0.25s for dropdowns and overlays
- `Lenis` smooth scroll
- `GSAP Flip` for state transitions
- Hover: perceptible single-property moves — a drawn underline, a growing accent dot, an inverting fill; no examined winner hover-scales a card, and a 1.02 twitch reads dead (`interaction-signatures.md`)
- Optional: variable-font weight micro-shift on hover (`wght` 400→500)

```css
.minimal-card {
  clip-path: inset(0 0 100% 0);
  transition: clip-path var(--duration-reveal) var(--ease-out-expo);
}
.minimal-card.is-revealed { clip-path: inset(0 0 0 0); }
```

Durations bind to `motion.duration-*`, easings to `motion.ease-*`. The Motion atmosphere score sits at 3 by default (±2 per the brief); pushing higher means the archetype is leaning toward Editorial or Immersive, and the recommendation should be revisited.

## What makes it award-worthy

A minimalist site scores 8+ when restraint reads as decision rather than emptiness — when the single accent is placed with surgical precision, when the type pairing is felt before it's noticed, when the whitespace itself signals confidence. Terminal Industries succeeds because the cinematic photograph and the lime CTA are anchored against generous void; the page is composed, not arranged.

The archetype loses identity in two failure modes: blanding (cookie-cutter geometric sans with safe muted palette — actively rejected by judges in 2025–2026), and cargo-cult Swiss (Inter at default tracking with no character behind the choice). Restraint without conviction collapses into corporate template.

## Ideal for

SaaS (Linear, Stripe, Vercel adjacency), luxury brands with quiet voice, architecture and design studios, high-end portfolios, design-tool landing pages, technical documentation, developer marketing, founder-led product launches.

## Cross-references

Read alongside `foundations.md` (typography systems, OKLCH single-accent strategy, animation toolkit), `anti-patterns.md` (blanding is rejected; pure `#FFF` with no character is rejected; Inter as display font is rejected), `audit-rubric.md` (Hierarchy 9+, Color 9+ are entry bars in this archetype), `exemplars.md` (Linear, Stripe, Vercel, Mintlify).

Provenance for every claim below — the researcher rounds and the fresh-context refutations that corrected them — lives in the public research corpus of `github.com/coroboros/research`, under `articles/award-winning-websites-2025-2030/`: `archetypes/minimalist.md`.

## Effect palette — what this line's winners ship

Corpus — Terminal Industries (Awwwards SOTD 2025-09-03 + SOTM 2025-09, 7.68 overall, Design 7.95 / Usability 7.36 / Creativity 7.65 / Content 7.57, Developer Award 7.89 with Animations/Transitions 8.80; also CSSDA; Vue.js/Vercel), Stefan Vitasović Portfolio25 (SOTD 2025-09-20, 7.25 overall, Developer Award 8.04, Animations/Transitions 8.80; Codrops case study), Gabriel Contassot (SOTD 2024-04-14, 7.34 overall, Developer Award 7.63; also CSSDA; Codrops case study), Treize Grammes (Awwwards HM 2024-10-11), Clou Agency Portfolio (SOTD 2025-09-05, 7.29, Developer Award 7.02; Webflow), Pacome Pertant (SOTD 2026-06-09, 7.76, Developer Award 7.62; GSAP/Three.js/Nuxt), Cyd Stumpel Portfolio 2025 (SOTD 2025-03-09, 7.22; View Transitions + Scroll-Driven Animations), Rogier de Boevé (Codrops case study, single-source). Terminal is the anchor — live stylesheet read rule-by-rule; the rest mix live-CSS reads and the authors' own Codrops case studies.

**The grammar** — Vary the *geometry* per element class, hold three things constant: one accent, one easing family, one origin logic ("everything resolves toward the accent, drawing/wiping/growing from a fixed edge"). Content reveals and fills run easeOutExpo `cubic-bezier(.19,1,.22,1)` at `.7–1s`; color/opacity fades run easeInSine `cubic-bezier(.39,.575,.565,1)` at `.2–.3s`; dropdowns/overlays run `cubic-bezier(.16,1,.3,1)` at `~.25s`. Two speed registers, never one. If two classes share a geometry, one is redundant — differentiate or merge.

**Buttons / CTA**
- **Directional token-wipe inversion** — a `:before` in the dark token sits `translate3d(0,100%,0)` inside an `overflow:hidden` pill; hover wipes it up and *inverts the token pair* (accent bg/dark ink → dark bg/accent ink), `transform .7s cubic-bezier(.19,1,.22,1)`, ink recolors over `.3s` with a `.2s` delay. Full-strength color the whole way · pick for the single hero CTA in a photographic or high-contrast system · (Terminal Industries, Awwwards SOTM 2025).
- **Full-token bg shift, ink held** — hover swaps `background-color` to a dedicated hover *shade of the same hue*, no motion, a real darker/lighter step never a transparency wash · pick for airy Swiss-grid SaaS where a moving fill reads as noise · (Stripe, reference-tier; corroborated by Terminal's `.drawer-cta-button:hover` token swap).
- **Ghost pale-tint fill (the only sanctioned wash)** — transparent button fills to a `5%` tint of the dark token (`rgba(5,36,36,.05)`), text held · tertiary/ghost only, never the hero · (Terminal Industries, Awwwards SOTM 2025).

**Links**
- **Underline draw under the label** — a 1px `:after`, `scaleX(0)` origin `right` → `scaleX(1)` flipping to `left` on hover, slow `.7s cubic-bezier(.19,1,.22,1)` · the one place the classic underline-slide belongs, on links not buttons · (Terminal Industries, Awwwards SOTM 2025).
- **Strike-through on hover** — `a:hover{text-decoration:line-through}` guarded by `@media(any-hover:hover)`, no motion, editorial confidence · pick for typographic portfolios where links are body-set · (technique-class: a plausible minimal-hover pattern, carried with no winner attribution — the Stefan Vitasović claim did not survive re-verification and the live CSS was not readable this run).
- **Arrow nudge** — inline arrow glyph translates `translate(2px,-2px)` up-right, opacity → 1, layered under the underline draw · micro-amplitude · pick for read-more/external/resource links · (Terminal Industries, Awwwards SOTM 2025).

**Figures / cards**
- **clip-path / masked reveal** — reveal media by moving an `inset()` mask, not opacity alone: `inset(0 0 100% 0)` → `inset(0 0 0 0)` bottom-up, or `inset(0 100% 0 0)` left-to-right · (Terminal Industries + Gabriel Contassot, both CSS-verified).
- **Inverse-scale parallax** — image scales *inversely* to scroll progress as a masked `inset()` opens; a clip-path inset synced to a scroll Track that also controls the scaling of the inner image. Amplitude stays small and never becomes a 50%-translate parallax; the often-quoted `scale(1.2 + track * -0.2)` figures are illustrative, not verified — Codrops states the mechanic, no numbers · (Gabriel Contassot, Awwwards SOTD 2024; mechanic Codrops-verified, amplitude unverified).

**Nav** — Float fully transparent over the hero (`position:fixed`, `background:transparent`, `pointer-events:none` on the shell, children re-enable), or frost translucent (`rgba(…,.8)` + `backdrop-filter:blur(5px)`), gaining ground when the hero-bottom sentinel crosses — never an opaque band from pixel 0. The nav-item indicator is a growing `5px` accent dot centered below the label (`opacity:0; scale(0)` → `scale(1.01)`, `transform 1s cubic-bezier(.075,.82,.165,1)`), not an underline — the dot itself is single-source on Terminal, the "nav ≠ the link underline" principle holds across the corpus. Winners never hang a colored `border-bottom` under a solid bar. Library ids: `show-on-scroll-up-nav` (scroll-aware) or `nav-hero-surface` (persistent bar). (Terminal Industries, Awwwards SOTM 2025; frost from Stripe, reference-tier).

**Text** — Per-char masked reveal is the signature: each glyph in its own `overflow:clip` wrapper (`char-wrapper+char-wrapper{margin-left:-.05em}` keeps kerning), `.char` set `opacity:0` then translated up with an *indexed* stagger under expo — that scaffold is Terminal's (Terminal Industries, Awwwards SOTM 2025, CSS-verified). Stefan lands the same read through masked segments positioned by `left` and `x` transforms — not per-char clip wrappers — timed `duration: 1.25 + index * 0.025s` under `easeExpOut` via Framer Motion (Stefan Vitasović, Awwwards SOTD 2025, Codrops-verified); Codrops calls the characters-to-word assemble the site's repeating motion motif, reused across sections by design. Use once, on the hero headline or load-time wordmark. Supporting: scramble/decode text with hardcoded per-index timing (Gabriel Contassot, `ScrambleText` durations `[1.2,1.5,0.4,0.2,1,0.6,0.6]`, `expo.out`, Codrops-verified) and clip-path line reveals for headings where per-char would be too busy.

**Cursor** — Keep the system cursor by default. `cursor:pointer` on interactives, `cursor:default` elsewhere — no follower, no `cursor:none`; CSS-verified across three winners, so canon not a note. One restraint-compatible exception is verified: a small monochrome dot that scales over interactive targets, or a lightweight trailing lens (Pacome Pertant ships a mouse trail, Awwwards feature tag, SOTD 2026). Keep it quiet — monochrome, no color spectacle — pointer-only, fully dormant on touch, never gating content or an accessible name. Library id: `minimal-cursor-signature`.

**Loader / intro** — Either instant paint that lets the per-char/clip reveals *be* the intro (observed, implementation unverified), or a `≤2.8s` minimal preloader in one of two verified forms: an accelerating 1→100 numeric counter (Gabriel Contassot, 2.8s, values `[1..100]`, "more stylistic than functional", fade-out `slow.in` ~`.8s`, Codrops-verified), or a two-panel split-curtain (`50svh` masks) retracting to uncover the page, paired with a counter recoloring through the accent (Terminal Industries, single-source on the curtain geometry). Never a spinner or a blocking brand-color splash.

**Element states — tap, focus, dormancy.** The pointer layer is one costume of the state; the tap and focus answers are not optional and not a degraded copy.
- **CTA** — `:active` flash 90–160ms; the wipe collapses to an instant token swap, no hover intermediary on touch. `:focus-visible` mirrors hover (same token inversion) plus a visible ring.
- **Link** — plain tap target on touch; the underline draw and the strike are `@media(any-hover:hover)`-gated so no content is ever trapped behind a hover. `:focus-visible` fires the draw plus the accent recolor, accessible name preserved.
- **Figure** — hover adds a contained zoom to 1.1 (felt, never a 1–3% twitch) plus one companion cue (tint / scrim lift / caption rise) on top of the resting scrubbed reveal; `focus-within` mirrors the cue so keyboard users reach the caption; tap surfaces the caption, swipe-snap cells enlarge on tap.
- **Index row** — hovered row lights an accent rule and surfaces metadata while siblings dim to 45%, `.3–.42s` under the signature easing. On touch it is a plain tap target: the dim reads as broken without a pointer. `:focus-visible` lights the row identically.
- **Heading / prose** — near-zero by design; the effect is the masked entrance or the scrubbed recolor, not a pointer response. No touch answer, no focus state beyond default.
- **Nav** — current-section dot shows as state, not as hover; the bar reveals on scroll-up and hides on scroll-down. `:focus-visible` shows the dot plus a ring, source order preserved.
- **Cursor** — fully dormant on touch (the pointer layer is simply absent); never focus-driven.

**Anti-signals** — Absent from every winner examined: a pale-tint fill on a *primary* CTA (the `5–10%` wash is quarantined to ghost buttons only — primaries move the full token); a contrasting `border-bottom` under a solid nav bar on scroll (bars float transparent or frost translucent); the same underline-slide smeared across buttons, links, and nav (winners split it — wipe/shift on buttons, draw on links, dot on nav); a magnetic-blob or decorative circle-follower cursor added by reflex; a blocking splash or spinner preloader; one global `fade-up 20px, .6s ease` on every section (reveals are masked/clip-path under expo with indexed timing); Tailwind's default `cubic-bezier(.4,0,.2,1) .15s` left as the site's motion identity; Inter as the display face.

## Mid-page life

The prose zone between hero and footer is carried by one positional décor channel riding under fire-once content reveals: canvas frame-sequence, scroll-scrubbed `clip-path:var()`, or masked inverse-scale figure reveals — positional means no fired state, so it re-fires every pass while the masked reveals and the odometer count-up persist; merely-good builds fire everything once on an IntersectionObserver and read inert on the second pass (Terminal Industries 7.68 + Gabriel Contassot 7.34, winner-verified mechanism). Hover on text is near-absent on prose and standalone headings tier-wide, and that absence is the register: the verified surface is `color` to the accent over `transition:color .3s` on nav/logo/phone links, `filter:brightness(1.05)` on one number, and one card-title `text-shadow` deepen (Terminal, winner-verified), plus a guarded `a:hover{text-decoration:line-through}` as the editorial variant (technique-class, no winner attribution) — no per-char rise, no weight shift, no highlight on reading copy. Gabriel's hover surface is minimal and the life is carried elsewhere entirely: scroll-position-driven masked reveals, not pointer response (Codrops-verified; the earlier "ships zero `:hover` rules" reading did not survive re-verification). The recoloring stat odometer — digits sliding inside `overflow:hidden`, gray → accent → ink — is the sanctioned mid-page climax (Terminal, winner-verified).

## Scroll texture

What carries the eye down the page between interactions: a masked figure reveal riding inverse scroll-scale (Gabriel Contassot, winner-verified), canvas frame-sequence photography scrubbed by the scrollbar, or the scroll-scrubbed per-char recolor sustained top-to-bottom — Terminal runs it the full page height, so the text substrate itself is the carry (Terminal Industries, winner-verified). The design_plan names one: the committed carry, never a hoped-for side effect of the section reveals. Wheel smoothing is near-universal at the tier — Lenis on 3 of 4 winners (Terminal live-verified `html.lenis`; Treize `lenis@1.1.13`; Gabriel `1.0.42` surfaced in the shipped bundle on adversarial re-read — only Stefan runs without it, on a custom virtual-scroll controller); ship Lenis by default.

On multi-view builds a second carrier exists and is easy to miss: the route transition itself. Home → project-detail is a momentum beat, not a cut — native View Transitions plus Scroll-Driven Animations (Cyd Stumpel, SOTD 2025-03-09, CSS-native and JS-light), Motion `AnimatePresence` in a shared layout crossfading opacity `.5s easeQuadInOut` (Stefan, Codrops-verified), or a Taxi single-page loop carrying the dark-home → bright-detail color shift under GSAP (Gabriel, Codrops-verified). Input-agnostic, so it fires on tap-navigation exactly as on click. Library id: `route-view-transition-carrier`.

## Idle band

Near-zero canon, and that IS the evidence: ~1 quiet channel across the corpus. Winners hold the page still *between inputs* — the life lives in the masked reveals and the scrubbed carry, not in ambient loops — so commit one quiet channel or its declared absence and let stillness read as the register, never as coverage skipped. **This stillness is the AMBIENT idle loop only** — the page is otherwise rich in scroll-driven reveals, the scrubbed carry, and the signature medium; the restraint archetype wins on motion craft, not on stillness (Terminal's Animations/Transitions score is 8.80). A page that reads still *overall* — an image here and there over inert type — is the "empty and dead" failure, not the quiet register. The stillness is the resting ambient channel, beneath a page alive with driven motion and a rendered-medium climax.

## Channel calibration

Channel calibration — this line's winners run 3–4 distinct interaction channels (per-class states, display-type effects, cursor, idle, scroll texture, replayable spectacle); the pre-emit critique's Aliveness axis reads against that band, never against bare coverage.

## Page recipe — how this line's winners build the page

Corpus — Terminal Industries (live CSS+DOM), Gabriel Contassot (live DOM + Codrops), Treize Grammes (live DOM), Stefan Vitasović (live + Codrops), Cyd Stumpel (Awwwards feature tags), Pacome Pertant (Awwwards feature tags), Rogier de Boevé (media-only, Codrops).

**Anatomy** — *Product-narrative scroll* (`argument-scroll`; Terminal, winner-verified order; Treize softer): hero statement · attention → logo strip · proof → stat odometer · understanding → "That's the Yard Operating System. YOS™" reveal · climax, mid-page → three benefits · understanding → executive quote · proof → contact + oversized-wordmark footer · close; rest is the void gap, seams masked, never hard cuts. *Gallery-index stack* (`gallery-stack`; Gabriel, Stefan, winner-verified): a scramble-decode type intro assembling over a MAIN GALLERY of figures on the homepage · attention → one full-bleed project per viewport, masked inverse-scale reveals · proof (the first still below the fold is the climax) → home↔detail route transition as the cross-view beat → bare "SCROLL UP" close. *Rendered-medium scroll* (`scene-scroll`; Terminal's `<canvas>` frame-sequence hero, Pacome's Three.js showreel): the hero carries the loud climax at intensity 9 with `scrub-film` in its media slot — a composed static first frame, the dissolve on scroll — then a proof strip, an operable `type-tester` beat and the odometer band carry the mid-page over a void-gap rest. Restraint holds in the type and the palette; the richness is the medium and one operable beat. Reach here when the brief has a transformation to show, not only an argument to make. The exemplar-proven pieces `scrub-film`, `shader-surface`, `scramble-decode` and `flicker-reveal` are all minimalist-reachable. *Single-canvas monolith* (`engine-world`; Rogier, technique / single-source): one WebGL scene is the page, screens rotated on a circular path.

Route on the brief's declared inputs, never on a taste read. One held product claim → `argument-scroll`, `<h1>` deferred to the footer. A body of visual work to show → `gallery-stack`, type-forward homepage over the gallery plus a route-transition SPA. Something to show *transforming* → `scene-scroll`. Reading-first AND spectacle explicitly forbidden → `standfirst-stack`, even intensity, voice in the chrome. All four are decidable from stated brief facts; never blend two spines.

**Hero architectures** — *Sequenced statement over cinematic still* (Terminal, winner-verified): the headline is `h2.title-sequence` (`min(5.729vw,146.667px)`, w400, lh .95) cycling four statements; the only `<h1>` waits in the footer; one CTA. (Easings verified; durations shipped.)

| element | order | transform | duration | easing |
|---|---|---|---|---|
| curtain, `#ededed` 50svh halves | 1 | retract | ~0.8–1.2s | easeOutExpo `(.19,1,.22,1)` |
| odometer | 2 | 1→100, gray→accent→closing ground | load-tied | linear |
| H2 chars (`overflow:clip` wrappers) | 3 | translateY up, +0.025s/char (technique) | ~1–1.25s | same |
| nav | 4 | opacity 0→1 | ~0.25s | `(.16,1,.3,1)` |

*Type intro over the gallery* (Gabriel, Stefan — Codrops-verified): a numeric 1→100 preloader hands off to a scramble-decode type assembly of the name/role block, playing OVER a main gallery of figures whose first cells open on masked inverse-scale reveals; scroll cue as the affordance, no CTA. Treize's softer variant: imperative `<h1>` + subhead + warm CTA "Programmer une visio" (winner-verified copy).

**Section chain** — the winner-verified order with its intensity map and the state each section owes. Pick forms by role; never hand-write hero or section layout CSS.

| role | form | pairs | intensity | state it owes |
|---|---|---|---|---|
| hero | `hero-masthead(media:back, align:start)` — argument; type intro over `full-bleed-figure` — gallery | h1 `kinetic-reveal` \| `scramble-decode`; cta-row `masked-label-swap`+`fill-invert-cta`; media `clip-reveal` \| `image-curtain` \| `scrubbed-inverse-scale-figure` | 8 | the argument hero's CTA MUST answer the pointer (token-wipe inversion) — a pointer-dead hero is a defect; the entrance fires on load; on touch the entrance still plays and the CTA answers `:active` |
| proof | `logo-wall` | — | 4 | grayscale at rest → color on hover, one logo at a time; never a marquee, never autoplay — this is the designed REST |
| index | `index-reel-header` + `index-list` | h2 `kinetic-reveal`; rows `index-row-hover`; actions `accent-link` | 5 | hovered row lights an accent rule and surfaces metadata, siblings dim to 45%; plain tap target on touch |
| stat-band | `stat-band` | stat `counter-odometer` | 5 | rolls on scroll-into-view (positional, re-fires); the markup carries the true final value with no JS; a QUIET micro-climax |
| mechanism-climax | `type-as-image`; `full-bleed-figure` (gallery variant) | caption `text-emphasis-fill`; media `clip-reveal` \| `image-curtain` riding inverse-scale | 9 | THE one loud peak — giant type carries the product noun, or the first full-bleed figure lands; scroll-scrubbed so it re-fires on pass, never a fire-once flash |
| chapters | `editorial-split` (×3, media alternating) | h2 `kinetic-reveal`; prose `text-emphasis-fill`+`semantic-accent`; media `clip-reveal` \| `figure-hover` | 5 | prose brightens dim-to-bright as the block traverses (reversible, re-fires); `[data-ad-term]` key terms ignite to accent on first view; standalone headings carry near-zero hover |
| close | `close-panel` | ask `kinetic-reveal`; channels `accent-link`+`masked-label-swap` | 6 | one imperative, decisive channel rows (accent recolor + underline wipe on hover/focus); no media slot, so the close cannot become a mood reel |
| footer | `oversized-wordmark` (argument — deferred h1); `bare-cue` (gallery) | wordmark `kinetic-reveal` | 6 | the OPTIONAL second quiet peak — the h1 lands last on a sticky reveal, legible with no JS; the portfolio close is just the bare cue |

**Footer** — the award lever (Terminal, winner-verified): dark ground; the `<h1>` lives here — `.footer-title{font-size:max(4.375rem,min(4.688vw,120px))}`, line-height .95, chars de-emphasized to `#fff3`; sticky reveal — `.footer__wrapper{position:fixed;bottom:0;transform:translateY(100%)}` over a 50vh holder, a pure-black overlay darkening the outgoing page. Portfolio norm: the bare cue — "SCROLL UP" (Gabriel), "2025." (Stefan).

**Arrival** — the Loader row families (`ingredients/preloaders.md`): curtain + counter recoloring into the footer's closing ground (Terminal, winner-verified); bare 1→100 counter (Gabriel, Codrops-verified); instant paint, reveals-as-intro (Treize, observed). Route transitions (`ingredients/page-transitions.md`): the route loader swaps the light curtain for `rgba(0,0,0,.7)` (winner-verified); in-page swaps ride Vue `reveal-y`, enter from `translate3d(0,100%,0)`, opacity `.6s` easeInSine + transform `1.2s` easeOutExpo (winner-verified).

**Copy voice** — Quoted to calibrate, never to ship — imitate the specificity (the named place, the count, the refusal), never the wording. First-plural visionary or bare name in the hero, second-person imperative at the CTA; fragments — the line break is the punctuation; TM on the product noun; the period as weight; refuses adjective stacks and self-narration. "No exclamation" fails corpus-wide: Treize ships "Activez votre marque !".
- "We have reinvented the future of logistics" / "through the yard." (Terminal) — vision, then the fragment turn.
- "Powering the yards behind the  brands you know" (Terminal, double space [sic]) — proof named in the reader's world.
- "GABRIEL CONTASSOT" / "FREELANCE DESIGN DIRECTOR" / "18.24" (Gabriel) — name, role, number: the whole type block.
- "Awwwards Jury member since 2020." (Stefan, live DOM) — proof by dated credential, no self-praise.

**Imagery art direction** — one grade per page. Cinematic (Terminal): industrial-scale subject, full-bleed horizon-anchored crop, golden-hour single warm source, amber/cream low-saturation grade — a `<canvas>` frame-sequence under an SVG gradient mask (mechanism winner-verified; grade shipped). Gallery (Gabriel, Stefan): full-bleed stills one per viewport in a single grade — Gabriel strict pure-black monochrome (winner-verified layout; grade shipped).

**Mobile / touch** — the strategy is carry-by-scroll. The entire signature thread is scroll-position-driven (scrubbed per-char recolor, masked inverse-scale reveals, recoloring odometer, WebGL grid), so it survives touch UNCHANGED — the momentum most at risk on mobile is exactly the channel that persists, because none of it depends on the pointer. Route and view transitions are input-agnostic and fire on tap-navigation. Pointer-only classes (underline draw, strike-through, nav accent dot, index-row spotlight, custom cursor) go dormant behind `@media(any-hover:hover)`, and that dormancy is the winner answer, not a gap. Press-class elements answer the tap with a 90–160ms `:active` flash. Image sets swap the desktop pinned/hold-drag strip for `swipe-snap-gallery` — native scroll-snap on OS momentum, next-cell peek, tap-to-enlarge, the scored Mobile Excellence line. Depth on touch comes from scroll, never pointer-parallax.

**Variation** — this section chain is one legal costume of the archetype, never THE skeleton. Structure is story-native: the body's sections derive from the universe's spine, then check against these roles for coverage — never the reverse. The axes serial winners measurably rotate between builds (21-artifact corpus, 5 studios): body content archetype and item counts, the ONE signature device (never reused across builds), the close mechanism, the hero medium, the index/HUD costume. What persists as DNA: type grammar, the motion register (the register itself, never the named reading/interaction kit — that kit is a device, rotated per build like the signature), annotation grammar as a form, engineering architecture. The same content archetype + item count + close mechanism recurring across two different-brand builds has zero winner precedent.

**Anti-signals** — no winner in this line opens on a card or bento grid; no hero carousel; no stacked hero CTAs; the `<h1>` is not assumed hero-bound — Terminal's is the footer statement; no second accent visible per viewport (an unspent orange token exists); no mixed-grade imagery; no imageless withholding hero on a gallery build — the type intro plays over the gallery, it does not hide it.

## Spectacle menu

*Terminal load*: curtains retract → odometer climbs gray → accent → closing ground → chars cascade over the truck photo; payoff — the intro pre-states the palette: the final ground is the footer, the accent is the CTA (winner-verified mechanism). *Gallery intro*: a 1→100 numeric preloader hands off to a scramble-decode type assembly over the main gallery, whose figures open on inverse-scale masks synced to a scroll Track (Codrops-verified mechanic); payoff — the work arrives already moving. *Rendered medium*: the `<canvas>` frame-sequence dissolve under an SVG gradient mask, or a Three.js showreel (Terminal, Pacome) — restraint holds in the type and palette while the richness moves into the signature medium.

**The hero beat.** A COMMITTED spectacle scene, never a quiet opener — the first impression forms here. `argument-scroll`: split curtain + recoloring odometer + per-char cascade over the cinematic still + exactly one CTA. `gallery-stack`: numeric preloader → scramble-decode type intro over the main gallery, first cells opening on masked inverse-scale reveals.

**The continuation beats** — the page is diffed against these, section by section.
- *logo / proof strip* — REST: a quiet static wall, grayscale at rest → color on hover as the only micro-state; intensity drops to ~4 (Terminal).
- *stat band* — QUIET MICRO-CLIMAX: digits slide inside `overflow:hidden` recoloring gray → accent → ink on scroll-in (Terminal, winner-verified).
- *mechanism / first figure* — THE ONE LOUD CLIMAX: Terminal's "YOS™" type-as-image reveal at intensity 9; the first full-bleed figure on its masked inverse-scale reveal; or a rendered-medium transformation. Exactly one loud peak.
- *editorial chapters* — CONTINUES QUIET: masked line and char reveals fire per section while the positional thread runs UNDER them; `text-emphasis-fill` scrub brightens words as each block traverses. Never silence.
- *route transition* (multi-view only) — CROSS-VIEW CARRIER: home → detail crossfades or morphs; the navigation is a momentum beat, not a cut.
- *footer* — OPTIONAL SECOND QUIET PEAK: the deferred `<h1>` lands on a sticky reveal over a 50vh holder, chars de-emphasized to `#fff3`, a pure-black overlay darkening the outgoing page (Terminal). Portfolio norm: a bare cue.

**The peak law** — verdict REFINED, from the winner evidence. The hero is a committed spectacle scene. Cap LOUD peaks at ONE mid-page climax, plus an OPTIONAL second QUIET peak where the deferred `<h1>` lands in the footer; a portrait-procession may run two loud peaks and no more. Cross-cutting mandate: commit exactly one POSITIONAL continuation channel — scroll-scrubbed per-char recolor, masked inverse-scale figure reveals, or a persistent WebGL grid — and live it hero-to-footer so the page never falls silent after the hero; on multi-view builds add the route transition as the cross-navigation carrier. "Peaks are capped" is not "quiet after the hero": restraint means the continuation vocabulary is QUIET, one scrubbed/masked/grid channel, rather than a second loud spectacle. The failure mode is a bank of fire-once IntersectionObserver reveals reading inert on the second pass; the winning move is a scroll-position-driven channel that re-fires the whole scroll.

Evidence: Terminal Industries does NOT go quiet after the hero — one loud mid-page peak, a quiet odometer micro-climax before it, an optional quiet footer peak, and a scrubbed per-char recolor sustained the whole page height; Animations/Transitions is its highest sub-score at 8.80 (winner-verified). Gabriel Contassot takes SOTD on a scroll-driven monochrome portfolio whose momentum is positional — clip-path masked inverse-scale reveals synced to a scroll Track, plus an Astro+Taxi page-transition loop across views — not fire-once entrance reveals (Codrops-verified). Stefan Vitasović reuses the characters-to-word motif across sections over a persistent WebGL grid, with Motion `AnimatePresence` crossfading between views: continuation by design (Codrops-verified; the continuity reading is inference from the verified motifs, not a quotation). Cross-archetype counter-evidence: Lando Norris (SOTY 2025, immersive) runs a DOUBLE loud climax — mid-page 3D helmet gallery plus inverted valediction footer — with rest bridges between and a momentum thread that never falls to silence; peaks can be two in a procession and even there they stay capped at ~2.

## Component index

Generated from `assets/components/manifest.json` — the authority for slots, variants, tokens, deps and `init` signatures, and the only place 11 of the 103 components record facts their file headers omit. Each row is the id plus the opening of its `whenToUse`, clipped: enough to pick, never enough to build. Grep the manifest for the chosen id to get its contract. Forms are the page skeletons (CSS, slots, variants); components are the behaviours that mount into their slots.

**Forms** (14) — page skeletons
- `bare-cue` — The gallery-stack's minimal close (Contassot / Vitasovic): no footer chrome, just a back-to-top cue ('SCROLL UP') and a year/edition mark on one slim baseline…
- `card-list` — Release/journal/blog cards in a 2-3 column grid: media 3/2, kicker/title/date at fixed rhythm; minmax(0,1fr) columns so a long title wraps instead of blowing…
- `close-panel` — The funnel's close: one imperative (18ch cap), decisive channel rows, a quiet trust line a full rest below — no media slot exists, so the close cannot become a…
- `editorial-split` — The editorial half + evidence half: heading and prose beside a figure and/or spec-table — the spec rows measure-capped at 44ch so they never sprawl.
- `feature-card-grid` — The 12-col asymmetric feature grid — cards carry REAL product-UI slices (never icons), spans 4-12 with dense backfill; the bento-fatigue correction.
- `full-bleed-figure` — One project per viewport: full-bleed media with a corner (or centered) caption over a structural contrast scrim — the gallery-stack unit; stack several for the…
- `hero-masthead` — The statement hero: kicker/h1/standfirst/CTA row/data-strip/media, every placement owned by the form — the builder fills slots and pairs components, never…
- `index-list` — The row-list body under index-reel-header: index/title/meta/thumb locked to one shared grid so column edges cannot drift and the meta cannot sprawl.
- `index-reel-header` — The header band introducing an index/reel/archive: the meta-line is grid-placed off the heading's columns and hard-capped at 40ch — full-width sprawl has no…
- `logo-wall` — The restrained proof strip: a static wrapped wall of height-capped, quieted logos (grayscale at rest, colour on hover — the one micro-state the form owns).
- `name-card` — The gallery-stack's opening slot: a type-forward name card — the name as the fold's whole argument, a role line, mono meta + scroll cue pinned to the bottom…
- `oversized-wordmark` — The argument-scroll / minimalist footer where the page's ONE deferred <h1> finally lands (Terminal's close): a viewport-height sticky holder with an oversized…
- `stat-band` — The standalone big-number strip: display-scale tabular values over mono captions, hairline-divided columns that never crowd (8ch floors).
- `swipe-snap-gallery` — The mobile-first image gallery: native scroll-snap track riding OS momentum (zero JS physics), next-cell peek, enhancer-fed snap dots.

**Components** (31) — behaviours
- `accent-link` — Inline text links: accent recolor + underline wipe on hover/focus.
- `border-glow-bloom` — The blurred accent under-glow that lifts a card — breathes up on hover/focus; the blur never animates, only opacity (compositor-clean).
- `char-assemble` — Masked per-char assemble entrance for short display headings — the richer second reveal beyond kinetic-reveal's line mask.
- `clip-reveal` — Media uncover on scroll-in: animated clip-path (inset or ellipse) with a scale settle.
- `conic-border-shine` — The cursor-tracked border light: an accent glow masked to the card's 1px edge follows the pointer.
- `counter-odometer` — Stat/counter roll on scroll-into-view — the markup carries the true final value (visible with no JS), tabular-nums, format-preserving (1,344 · 99.7% · +412 yr).
- `curtain-transition` — The cover wipe that rhymes with the loader: play(fn) covers the viewport, runs the swap at full cover, wipes away.
- `figure-hover` — The default figure response: contained zoom to 1.1 (felt, never a 1-3% twitch) + a companion cue — tint, scrim lift, or caption rise — on hover and…
- `fill-invert-cta` — The universal primary-CTA move: full-token flood + label inversion on hover/focus — fill (direct pole swap) or wipe (a panel rises from the bottom edge).
- `flicker-reveal` — Stochastic per-letter opacity settle — every letter on its own randomized delay, duration, and mid-flight dips before resting at 1, echoing a 3D render's…
- `focus-defocus` — Gallery spotlight: the hovered item sharpens while siblings blur and dim.
- `full-page-scrub-recolor-carry` — The sustained substrate carry: every char of the opted-in blocks joins one document-ordered sequence brightened dim→ink by GLOBAL page progress — the reading…
- `hover-preview-video` — The production-house index reveal: hovering a project row surfaces its MUTED FOOTAGE in one cursor-attached floating layer (lerped toward the pointer), an…
- `image-curtain` — The treated-image reveal: a clip wipe arrives grayscale, colour floods in late — two beats.
- `index-hover-preview` — The canonical studio-index hover: hovering a project row surfaces its thumbnail in ONE cursor-attached floating layer (lerped toward the pointer) — this…
- `index-row-hover` — The living index: hovered row lights with an accent rule and surfaced metadata while siblings dim to 45% — the spotlight list for archives, work indexes…
- `kinetic-reveal` — Headline/statement entrance: masked line reveal, staggered.
- `masked-label-swap` — CTA/button label two-line wipe swap on hover/focus.
- `minimal-cursor-signature` — The restraint-compatible cursor slot: a small monochrome ink dot (mode 'dot' — replaces the native cursor, grows over interactive targets, compresses on press)…
- `nav-hero-surface` — The SURFACE axis for a minimal PERSISTENT bar (the winner-norm nav that never hides): floats transparent over the hero, gains owned --ad-ground when the…
- `route-view-transition-carrier` — Multi-view portfolio momentum carrier: the home→project-detail swap crossfades/morphs instead of hard-cutting — native View Transitions when available (shared…
- `scramble-decode` — Short labels/links/data-chrome decode from charset noise to the true string (entrance once; hover replay variant).
- `scrub-film` — A film still the visitor drives — scroll or pointer maps to video currentTime.
- `scrubbed-inverse-scale-figure` — The gallery-stack's continuation carry: a clip-path inset opens bottom-up WHILE the media scales inversely to scroll progress — welded to scroll position…
- `semantic-accent` — Key terms marked [data-ad-term] carry the accent — colour does the reading; terms ignite on first view.
- `shader-surface` — The token-driven WebGL texture layer — gradient-mesh, noise-field, or pointer-ripple painted from the DESIGN.md palette.
- `show-on-scroll-up-nav` — Scroll-aware fixed nav: transparent over the hero, gains ground when the hero-bottom sentinel crosses (not a scrollY threshold), hides on scroll-down and…
- `smooth-scroll` — Smoothed-scroll foundation for scrubbed/pinned reveals.
- `split-rollover` — Nav links / short labels: per-character rollover on hover/focus, staggered.
- `text-emphasis-fill` — The tier's text signature, two channels: scrub (words brighten dim-to-bright as the block traverses the viewport — reversible emphasis on always-legible copy)…
- `type-forward-intro-loader` — The gallery-stack loader/intro: a stylistic linear 1→100 count (2.8s), an ~.8s slow-in fade, then a scramble-decode type assembly over the main gallery…
