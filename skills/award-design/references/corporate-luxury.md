# Corporate Luxury

Quiet luxury. Sophisticated restraint where generosity of whitespace signals exclusivity. Custom serifs at display, refined sans-serifs at body, palette anchored in neutral foundations punctuated by jewel tones or muted golds. Animation curves are long; nothing hurries. The voice is inherited rather than chosen.

Tier 1 (DNA, anti-signals, macrostructures, reflexes) is `references/archetype/corporate-luxury.md`, pushed into context by `scripts/direction_roll.py`. This file is tier 2: it loads at the design_plan commit, by heading, never whole.

## Contents

- [Canonical reference — Cartier Watches & Wonders 2025](#canonical-reference--cartier-watches--wonders-2025)
- [DNA — non-negotiable](#dna--non-negotiable)
- [Common expressions](#common-expressions)
- [Typography](#typography) · [Color](#color) · [Layout](#layout) · [Motion](#motion) · [E-commerce patterns](#e-commerce-patterns)
- [What makes it award-worthy](#what-makes-it-award-worthy) · [Ideal for](#ideal-for) · [Cross-references](#cross-references)
- [Effect palette — what this line's winners ship](#effect-palette--what-this-lines-winners-ship) — per-element-class recipes, the grammar, tap/focus/dormancy
- [Mid-page life](#mid-page-life) · [Scroll texture](#scroll-texture) · [Idle band](#idle-band) · [Channel calibration](#channel-calibration)
- [Page recipe — how this line's winners build the page](#page-recipe--how-this-lines-winners-build-the-page) — anatomy, hero, section chain, footer, arrival, copy, imagery, mobile, variation
- [Spectacle menu](#spectacle-menu) — the hero beat, the continuation beats, the peak law

## Canonical reference — Cartier Watches & Wonders 2025

**Site.** Cartier Watches & Wonders 2025
**URL.** `cartier-waw-0225.dev.60fps.fr`
**Award.** Awwwards Site of the Day, 18 August 2025 — 7.64 overall, Developer Award 7.55 with Animations/Transitions 9.00
**Studio.** Immersive Garden, with `60fps` and `Mooders`, for Cartier.

Built around Cartier's Geneva pavilion: six self-contained 3D alcoves, one per watch, scrolled through like rooms in a museum after hours. Slow tasteful motion, refined typography, hidden gestures in every scene, a bespoke Mooders soundscape running as a continuous narrative layer, GSAP and Lenis on one clock. The platonic case for quiet-luxury restraint with sumptuous detail. The URL lives on the build studio's `dev.60fps.fr` subdomain rather than a Cartier-owned domain — unusual, but the canonical Awwwards-referenced location.

Immersive Garden re-won the pavilion a year on: Cartier Watches & Wonders 2026, SOTD 25 May 2026, 7.53 with Developer Award 7.85, on Three.js / GLSL / Blender. The award page describes it only as "an immersive journey through refined worlds, highlighting iconic timepieces" — the six-alcove structure above is read from the 2025 pavilion and does not transfer to 2026 as observed fact.

Substitutable peers: `hermes.com` (orange and ivory with custom serif), `rolex.com` (dark greens and golds, editorial photography, slow pacing), `aesop.com` (warm neutrals, single custom serif, product-as-still-life), `bugatti.com` (deep blues and chrome, automotive gravitas), `immersive-g.com` (agency-as-luxury-brand).

## DNA — non-negotiable

- Generous whitespace (128–200px+ section padding) signals exclusivity, not waste
- Custom or premium serif at display sizes is the typographic mark of the archetype
- Color rests on neutral foundations punctuated by jewel tones, muted golds, or single deep brand color
- Motion uses long easing curves (1–1.5s, easeOutQuart `cubic-bezier(0.25, 1, 0.5, 1)` as the page-wide consistency default; `cubic-bezier(0.16, 1, 0.3, 1)` is the snappier alternate) — nothing rushes
- Photography is treated and considered — every shot frames the product as object, not commodity
- One continuous, low-amplitude, reversible signature thread runs under every viewport from hero to footer; the hero opens it and never closes it

The archetype keeps its identity across flat editorial luxury (Hermès, Aesop), cinematic 3D pavilion (Cartier WAW), dark luxury (Rolex, Bugatti), and warm neutral lifestyle (Aesop, Loro Piana). Background register is an expression choice, not a definition.

## Common expressions

Three stacks fit the DNA. Pick the one matching brand voice and product type.

### Flat editorial luxury — Hermès / Aesop profile

Warm white or cream foundation (`#F8F5F0`, `#FAF8F5`) with custom serif headlines (Didot, Bodoni-adjacent), considered photography, generous gutters. Single jewel-tone accent (Hermès orange, Aesop sage, Loro Piana camel). Asymmetric image-text pairs. Hover is a contained scale, opacity 0.7→1. Ideal for fashion houses, fragrance, premium lifestyle, artisan and craft brands.

### Cinematic 3D pavilion — Cartier WAW profile

Cream or warm-neutral foundation (`#F2EBDC` to `#FAF7F0`) with rendered 3D pavilion architecture as the immersive surface. Type is engraved or embossed (chunky serif "WATCHES & WONDERS" rendered as 3D objects). Slow tasteful motion through 3D alcoves. Hidden gestures reveal product detail. Bespoke soundscape. Ideal for luxury launches, watchmaking, automotive concept reveals, jewelry openings, premium architecture and hotels.

### Dark luxury — Rolex / Bugatti profile

Deep neutral foundation (`#1A1A1A`, `#0E1A1B`) with custom serif in cream type, gold accent (`#C5A572`), or chrome silver. Editorial photography lit dramatically. Long easing on every transition. Ideal for premium automotive, fine timepieces, premium spirits, private banking and wealth management.

## Typography

The serif is the mark.

- **Display serif**: Didot, Bodoni, GT Sectra, Tiempos Headline, Editorial New, custom commissioned serifs at weight 400–600 — 60–120px, tight tracking (`-0.02em` to `-0.04em`)
- **Body sans**: Apercu, Founders Grotesk, PP Neue Montreal, Söhne — 16–18px, weight 400, line-height 1.6
- **Casing**: uppercase sparingly — navigation labels, category tags, metadata. Title Case avoided in headers (sentence case reads more refined)
- **Micro-typography**: tabular numbers (`tnum`) for prices, sizes, edition numbers; non-breaking spaces in unit pairs (`10&nbsp;mm`, `750&nbsp;ml`)

Winner faces on record: Genath serif over Atlas Grotesk (Delvaux), KTF Metro (Son Daven), EB Garamond (Depo Luxe). Inter, Roboto, Arial as display fonts signal "no type decision". This archetype either commissions a custom serif or pairs a known premium serif (Tiempos, Sectra) with discipline. The luxury is in the choice and its execution, not the budget.

## Color

Color rests on neutral foundations.

- **Backgrounds**: warm whites `#F8F5F0`, `#FAF8F5`, cream `#FAF7F0`; deep neutrals `#1A1A1A`, `#0E1A1B`
- **Text primary**: charcoal `#2D2D2D` on cream, off-white `#E8E0D0` on dark
- **Text secondary**: warm gray `#8B8580`
- **Accent — jewel tones**: muted gold `#C5A572`, deep emerald `#006D5B`, sapphire `#1B365D`, ruby `#8B2E2E`
- **Signature 2025**: Pantone Mocha Mousse `#A47764`
- **Borders**: `#E8E4DF` or `rgba(0,0,0,0.06)`

Winner grades on record: warm-tan `#A89474` over dark-brown `#2C2824` (Son Daven), cream `#f8f5f0` over charcoal `#040810` (Urban Jürgensen), pure white on pure black (Depo Luxe).

This warm-cream + muted-gold + charcoal family is the overexposed premium-consumer cluster (`anti-patterns.md` *AI Tells*). Rotate at least one of the three roles per build — bone for cream, oxblood or deep emerald for gold, ink for charcoal — or write the brief-tied justification for keeping all three.

Colors feel inherited — neither neon nor primary, never high saturation. One accent per surface, used as signal rather than decoration.

## Layout

Generous whitespace, content centered or asymmetrically paired within constrained widths.

```css
.luxury-section {
  padding-block: clamp(6rem, 12vw, 14rem);
  max-width: 1200px;
  margin-inline: auto;
}
.luxury-split {
  display: grid;
  grid-template-columns: 1fr 1.2fr;
  gap: clamp(3rem, 6vw, 8rem);
  align-items: center;
}
```

Content widths bind to `containers.luxury-page` (~1200–1280px) and `containers.read-measure` (~65ch). Section spacing pulls from `spacing.section-luxury` (the largest scale step). The Doppelrand technique (nested concentric containers — outer shell with hairline border, inner core with tighter radius) lifts cards from "flat tile" to "machined hardware" — see `premium-patterns.md`.

## Motion

Long, deliberate curves. Nothing hurried.

- Easing: easeOutQuart `cubic-bezier(0.25, 1, 0.5, 1)`, duration 1–1.5s — the page-wide consistency default for this line; `cubic-bezier(0.16, 1, 0.3, 1)` is the snappier alternative
- Subtle parallax (5% maximum differential)
- Hover: gentle opacity shifts (0.7→1) and a contained `scale(1.02–1.05)` over 800–1500ms
- Image reveals: clip-path inset with long duration (0.8–1.2s)
- Page transitions: a curtain/overlay wipe plus loader re-entry, or View Transitions with slow cross-fades (400–600ms)
- 3D alcove archetype: scroll-controlled camera moves through architectural scenes (Cartier WAW)

```css
.luxury-card {
  transition: opacity 800ms var(--ease-luxury),
              transform 800ms var(--ease-luxury);
}
.luxury-image-reveal {
  clip-path: inset(0 100% 0 0);
  transition: clip-path 1200ms cubic-bezier(0.77, 0, 0.175, 1);
}
.luxury-image-reveal.visible { clip-path: inset(0 0 0 0); }
```

Durations bind to `motion.duration-luxury-*`. Easings to `motion.ease-luxury` (long-ease curve).

## E-commerce patterns

When the archetype carries commerce, the buying experience is intentional rather than transactional.

- Storytelling product pages (Apple model) — narrative before price
- Cart as slide-in panel, no page navigation
- Every visible product is shoppable
- Generous spacing signals exclusivity — products never packed tight
- No modals on page load
- Radical transparency for materials and pricing (Everlane model) where brand voice supports it
- Real-time customization previews (configurators) for premium hardware and watchmaking
- Aspirational imagery where the product is contextual (worn, placed, lit) rather than catalog-flat
- Product cards answer the pointer by swapping to a second angle or a short muted craft video (~.3–.5s cross-fade, first frame preloaded, guarded by `@media (hover:hover)`), never by a fast pop
- Three of the eight corpus sites are multi-page commerce (Delvaux, Urban Jürgensen, Brunello) — the signature thread has to survive the route change, so a navigation plays the curtain/overlay wipe plus loader re-entry, not a hard cut

## What makes it award-worthy

A corporate-luxury site scores 8+ when the restraint feels chosen rather than generic — when the serif is felt before it's noticed, when the whitespace itself signals confidence, when the photography frames every product as an object worth looking at. Cartier WAW succeeds because the 3D pavilion and the slow tasteful motion are the brand's voice, not a layer of polish over a stock template.

The archetype loses identity at three failure modes: cookie-cutter minimalism (the safe muted geometric default that every brand adopted, actively rejected by judges), corporate sterility (whitespace without warmth, serif without conviction), and luxury costume (premium fonts bolted onto a generic SaaS template). Quiet luxury without the underlying craft reads as expensive theater.

## Ideal for

High-end fashion, luxury hotels, fine jewelry, premium automotive, wealth management, private banking, premium real estate, fragrance, watchmaking, artisan and craft brands, lifestyle direct-to-consumer with story.

## Cross-references

Read alongside `foundations.md` (typography systems, OKLCH for jewel tones, animation toolkit), `premium-patterns.md` (Doppelrand nested containers, button-in-button trailing icons, eyebrow tags), `anti-patterns.md` (no neon, no high saturation; jewel tones only), `audit-rubric.md` (Spacing 9+, Typography 9+, Motion 8+ are entry bars), `exemplars.md` (Hermès, Rolex, Aesop, Bugatti, Immersive Garden).

Provenance for every claim below — the researcher rounds and the fresh-context refutations that corrected them — lives in the public research corpus of `github.com/coroboros/research`, under `articles/award-winning-websites-2025-2030/`: `archetypes/corporate-luxury.md`, with the live stylesheet reads in `winners/delvaux.md`, `winners/brunello-cucinelli.md`, and `winners/depo-luxe.md`.

## Effect palette — what this line's winners ship

Corpus — Cartier Watches & Wonders 2025 (Awwwards SOTD 2025-08-18, 7.64, Developer Award 7.55 with Animations/Transitions 9.00; Immersive Garden + 60fps + Mooders; WebGL/Three.js/GLSL), Cartier Watches & Wonders 2026 (SOTD 2026-05-25, 7.53, Developer Award 7.85; Three.js/GLSL/Blender), Delvaux Digital Flagship Store (Awwwards HM 2026-06-15; 51North; GSAP + Craft CMS — a high community craft score, directionally the corpus's highest, though the exact figure returned three different readings and is not reliably re-derived), Son Daven (SOTD 2026-06-05, 7.62, Developer Award 8.09; The First The Last; WebGL + GSAP + Webflow), Depo Luxe (SOTD + Developer Award 2026-07-07, 7.62, Animations 8.40; Cuchillo; 11ty), Brunello Cucinelli AI E-com (SOTD 2026-07-09, 7.19, Developer Award 7.01; makemepulse), Urban Jürgensen (SOTD + Developer Award 2025-10-30, 7.27 / Dev 7.22; Digital Luxury Group + Numbered; WebGL + Sanity + Vercel), Louis Vuitton Collectibles (SOTD 2024-02-20, 7.79, Animations 9.4; Immersive Garden + Reflet), plus Longines (SOTD Nov 2023) and Omega (SOTD Jan 2026) carried from the earlier round with their award facts not re-derived. Award dates, scores, studios and stacks are read from the award body's own site pages. Interior mechanics carry their own tag per row: Son Daven's and Depo Luxe's numeric mechanics are executable defaults rather than source reads, and the earlier round's "four read at the source level" framing did not survive re-verification.

**The grammar** — pick one easing and one reveal primitive, reuse both at every scale, and give each element class its own geometry. The corpus easing is easeOutQuart `cubic-bezier(0.25,1,0.5,1)` — carry it as the page-wide consistency default; the claim that it turns up byte-identical across Delvaux's CSS var, its GSAP `CustomEase` and Son Daven was asserted without shipped-CSS access and is not re-verified, so it competes with the DNA's `cubic-bezier(0.16,1,0.3,1)` easeOutExpo on taste, not on measurement (keep the expo for a Brunello-style snap). The reveal primitive is reveal-from-behind-a-clip: masked `translate` for type, `clip-path:inset()` for media and overlays. Change the axis and geometry per element, never the curve or the primitive without a brief-tied reason.

**Buttons / CTA** — four moves, no pale-tint fill among them:
- **Label roll-swap** — two label copies in an `overflow:hidden` clip; hover rolls both `translateY(-100%)` together, `transform .2s cubic-bezier(.65,0,.35,1)`, no color event · pick as the default primary-CTA move for editorial maisons · (Delvaux, Awwwards HM 2026-06-15; Son Daven, SOTD 2026-06-05 — observed, implementation unverified).
- **Invert to the full section token** — CTA fills with the *solid* section token, geometry extended `-4px` past the label with a 2px outline in the bg colour — never `rgba(token,0.1)` · pick when one hero CTA needs weight · (Son Daven, SOTD 2026-06-05).
- **Line / stroke-draw** — draw an SVG ring (`stroke-dashoffset` to 0 over ~`.6–.8s` on the corpus easing), or fade a `currentColor` `:before` underline at `height:.5px` opacity 0→1 · pick over any fill when the surface is photographic, 3D, or frosted · reduced-motion keeps the ring or underline present at rest · (Brunello Cucinelli, SOTD 2026-07-09; Depo Luxe, SOTD 2026-07-07; Louis Vuitton Collectibles, SOTD 2024-02-20).
- **Spotlight-dim siblings** — hovering one list/nav item drops the others to `opacity:.2`, not itself; Depo Luxe also swaps the hovered row's metadata · pick when a nav index is the primary interaction · (Son Daven, SOTD 2026-06-05; Depo Luxe, SOTD 2026-07-07).

**Links** — cross-fade `color 1s cubic-bezier(.65,0,.35,1)` between ink and a muted brand tone, with a 2px bullet dot fading in beside the label rather than an underline grow (Delvaux, Awwwards HM 2026-06-15). Or an underline that *appears* — `currentColor` `:before`, opacity 0→1 over `.1–.2s` — instead of growing from a point (Depo Luxe, SOTD 2026-07-07). Never a fast underline slide.

**Figures / cards** — reveal with a `clip-path:inset()` wipe, `1s cubic-bezier(.25,1,.5,1)` (Delvaux; the numbers are carried from the skill's earlier source-level reads, not re-verified from shipped CSS this run). Editorial hover zoom stays `scale(1.02–1.05)` over `0.8–1.5s`, guarded by `@media (hover:hover)` — never a fast 1.1× snap; Delvaux's only zoom in the whole sheet is `scale(1.02)` on a swatch (Brunello Cucinelli, SOTD 2026-07-09; Delvaux). Commerce product cards take a different move entirely: on hover the card swaps to a second angle or a short muted craft video, cross-faded `~.3–.5s` with the first frame preloaded, video `muted loop playsinline`, the same `@media (hover:hover)` guard — the prevailing luxury e-com convention for the corpus's commerce grids (Delvaux, Urban Jürgensen, Brunello), integrated as an executable default rather than verified against a specific corpus card.

**Nav** — four verified surfaces, zero contrasting border-bottoms: the section's own colour faded in past a scroll threshold (Son Daven, SOTD 2026-06-05); an opaque plate plus a same-ink `border-bottom:1px solid rgba(29,29,27,.03)` ~3% hairline (Delvaux, Awwwards HM 2026-06-15); a photographic top-down gradient scrim, no fill (Brunello Cucinelli, SOTD 2026-07-09 — the frosted-glass and hand-drawn craft skin are read from the makemepulse case study, not the award page); `backdrop-filter:blur(40px)` over a ≤5% tint that flips with the section (Depo Luxe, SOTD 2026-07-07). Never a contrasting-accent `border-bottom`; frosted-white glass is not a default — two of the four use no blur at all. The Delvaux hairline is the one sanctioned exception path to the zero-nav-`border-bottom` gate — reusing it takes a written override in the design_plan citing this row; same-ink at ≤5–6% alpha only, never a contrasting line.

**Text** — masked per-line or per-word reveals only. SplitText lines under an `overflow:hidden` mask, sliding up behind the clip (`power4.inOut`, dur 2, `stagger .2` on Delvaux, carried from earlier source reads; `yPercent 250→0`, `durL 1.2s` on Son Daven, an executable default). Word scatter-in from alternating `yPercent` is a warmer variation for craft brands (single-source, Son Daven, SOTD 2026-06-05). Urban Jürgensen's award page names unconventional text-loading transitions as its entrance signature (SOTD 2025-10-30). Never a per-letter typewriter.

**Cursor** — two poles, no page-wide blob. Native cursor + magnetic pull for editorial/e-com: elements translate toward the pointer and spring back with `elastic.out(1,0.3)`, applied to circular CTAs only — the elastic overshoot is the tell (Son Daven, SOTD 2026-06-05; amplitudes are executable defaults, not source-verified); Delvaux ships no custom cursor at all. Or a minimal custom cursor scoped to the WebGL surface, `cursor:none` over that surface only (Brunello Cucinelli, SOTD 2026-07-09; Cartier, SOTD 2025-08-18). Over an interactive or hidden-gesture object that scoped cursor morphs to a verb label — HOLD / DRAG / VIEW / EXPLORE — plus an outline ring or a size shift; without it the archetype's confirmed gestures are undiscoverable (Louis Vuitton Collectibles click-and-hold, SOTD 2024-02-20; Cartier's hidden gestures, SOTD 2025-08-18). Pair it with a press-and-hold reveal on the object side. Set `grab`→`grabbing` wherever horizontal drag exists.

**Loader / intro** — content-driven, no fake timers. WebGL or frame-sequence heroes gate a real-progress counter on `Promise.all([assets, scenes, fonts.ready])` and Flip the logo into the header slot (Son Daven, SOTD 2026-06-05; Cartier, SOTD 2025-08-18), or reveal a logo whose SVG paths fill in as the loader advances (Depo Luxe, SOTD 2026-07-07). A pure-CSS editorial DOM paints instantly — the scroll reveals carry the entrance (Delvaux, Awwwards HM 2026-06-15, winner-verified absence: only `nuxt-loading-indicator`).

**Element states — tap, focus, dormancy.** The pointer layer is one costume of the state; the tap and focus answers are not optional and not a degraded copy.
- **CTA** — the roll, fill or draw fires on `:active` as the tap answer, 90–160ms flash floor; magnetic pull is native on touch. `:focus-visible` mirrors the hover exactly — roll, fill and draw are all keyboard-reachable, never hover-only.
- **Link** — on touch the underline or bullet dot sits in its resting-present state and the tap navigates. `:focus-visible` shows the same accent recolor plus the underline, present rather than animated under reduced motion.
- **Figure** — tap opens the detail or enlarges; a commerce card's tap advances to the alternate view; the resting figure is fully legible with no hover. `focus-within` fires the same companion cue so keyboard users reach the caption or the second angle.
- **Index row** — plain tap target on touch, no sibling dim (the dim reads as broken without a pointer). `:focus-visible` lights the focused row identically; the dim is decorative and never hides content.
- **Heading** — no pointer answer at all, and zero `font-variation-settings` shift on hover across every readable sheet. The effect is the entrance: masked per-line or per-word, fire-once.
- **Cursor** — no custom cursor on touch; the gesture is surfaced instead by an on-object hint (icon or short label). Keyboard reaches it through focus + Enter/Space, and the contextual label carries an accessible-name equivalent so the affordance is never pointer-only.
- **Nav** — the surface tint is the resting state on touch, hamburger or plate answering the tap, no blur required. Links keep a clean accessible name; `:focus-visible` shows the roll's target string.

**Anti-signals** — absent from every winner examined: a pale/washed tint fill on a CTA hover (they roll, invert to a full token, or draw a line); a contrasting-accent `border-bottom` under the scrolled nav; one uniform hover repeated across all element classes; generic fade-up-20px for everything; per-letter typewriter headlines; a fake timed spinner or fixed-duration progress bar; a large page-wide cursor blob with mix-blend-difference; frosted-white glass nav as a default; a neon or high-saturation accent (palettes stay two-tone warm-neutral or monochrome); a fast 1.1×+ image pop.

## Mid-page life

Three welded channels, never decorated paragraphs: a fire-once reveal on every content block (`data-scroll-reveal="h|p|ctn|line"` on `ScrollTrigger.create({start:"top bottom", once:!0})`), a reversible scrubbed décor bed running under the whole mid-page — five parallax layers at `ease:"none"`, a frame-sequence film at `scrub:.25`, WebGL blackPoint/whitePoint grades — and one idle touch welded to the wheel, the marquee speeding with `timeScale(1+.01*velocity)`. Son Daven's award is verified (SOTD 2026-06-05, 7.62, Developer Award 8.09) and the three-channel structure is its lived hero-to-footer thread; every number in that bed is an executable default, not a source read — the award page exposes none of them and no public teardown does either. The bed is the executable form of the continuation law.

The one sanctioned way prose itself stays alive is a scrubbed reading wash, not a hover: `[data-highlight-text]` splits to chars and `.from(chars,{opacity:.1})` scrubs from `top 75%` to `bottom 50%`, re-firing every pass because it is décor over reading, never a reveal (Son Daven, executable default). Hover-on-text lives on nav, index, and links only — a per-char nav roll-swap staggered `{each:.025,from:"random"}` with siblings spotlight-dimmed to `opacity:.2` (Son Daven), an index-row metadata cross-fade where client and counter fade out as director and title arrive (Depo Luxe, SOTD + Developer Award 2026-07-07, 7.62) — with zero `font-variation-settings` shifts on hover across every readable sheet.

Delvaux is the control case: the stillest register in the corpus, no always-on idle channel (a reading of the shipped experience, not a sourced count), a community craft score directionally the corpus's highest, and Honorable Mention — a lower jury tier than Son Daven's Site of the Day. Community voters rated Delvaux's craft above Son Daven's 7.62, so the inversion is real and the continuity signal lives on the award-tier axis, not the raw score: moderate, caveated evidence that the jury reads stillness as least alive, never proof that stillness alone cost the tier.

Wheel smoothing is common across the corpus but not measured as universal — Cartier's GSAP + Lenis on one clock is the confirmed case; Delvaux tags GSAP + Craft CMS and Son Daven tags WebGL + GSAP + Webflow with no smoother on either award page, and GSAP ScrollSmoother can go untagged. Ship Lenis by default (`skeletons.md` §A) and claim nothing about the corpus's libraries.

## Scroll texture

What carries the eye down the page between interactions: clip-path figure reveals riding the scroll plus `data-scroll-displace` on footage, so the film itself shifts under the reader's hand (Son Daven, structure lived, numbers an executable default), swiper processions moving product laterally at a measured pace (Delvaux, winner-verified), or a WebGL displacement ground under every image and the nav index (Depo Luxe — reported, and the interior mechanic appears in no award description or teardown found on re-verification). The design_plan names one — the carry stays slow and material, on the corpus easing, never a bolted-on parallax. On a revived-house spine the carry is the scroll refusing to bottom out: an infinite vertical track plus an infinite horizontal product carousel (Urban Jürgensen, SOTD 2025-10-30, winner-verified).

On multi-page maisons a second carrier is mandatory and easy to miss: the route change itself. Three of the eight corpus sites are multi-page commerce (Delvaux, Urban Jürgensen, Brunello), and a single-scroll continuity model dies at the first page jump. Intercept same-origin navigation, play a full-bleed curtain or overlay wipe (`clip-path:inset()` sweep or a covering transform panel) over `~.6–1s`, fetch and swap the container at full cover, then re-enter the loader briefly so the thread — décor bed, WebGL ground, scored drift — is re-established on the incoming page. Compositor-only; reduced motion swaps the container instantly under a short cross-fade. Input-agnostic, so it fires on tap-navigation exactly as on click. The exact per-site mechanic (Barba/Taxi-style versus bespoke) was not exposed, so the hole is evidenced, the implementation is ours.

## Idle band

A bespoke soundscape behind a sound toggle where the brief earns it — Cartier runs a continuous Mooders score as a narrative layer rather than wallpaper, Depo Luxe keeps audio behind a gesture-unlocked toggle; otherwise ~1 quiet channel. Restraint is the luxury register — commit the soundscape deliberately or hold to the one quiet channel, never ambient décor. The stillness that costs award tier is stillness in the *thread*, not in the ambient loop: an idle band held to one channel over a page carrying a live scrubbed bed is the register, while an idle band and a dead thread together are the least-alive read.

## Channel calibration

Channel calibration — this line's winners run 4–5 distinct interaction channels (per-class states, display-type effects, cursor, idle, scroll texture, replayable spectacle); the pre-emit critique's Aliveness axis reads against that band, never against bare coverage.

## Page recipe — how this line's winners build the page

Corpus — Son Daven (SOTD 2026-06-05, live), Delvaux (HM 2026-06-15, live), Depo Luxe (SOTD + Developer Award 2026-07-07, live), Brunello Cucinelli AI (SOTD 2026-07-09, live shell; voice from `brunellocucinelli.com`), Urban Jürgensen (SOTD + Developer Award 2025-10-30, award-page structure), Cartier WAW 2025 (SOTD 2025-08-18, media + case study), Louis Vuitton Collectibles (SOTD 2024-02-20, award-page gestures).

**Anatomy** — *Editorial maison scroll* (`maison-scroll`; Delvaux, winner-verified) — commerce behind "Discover": slider hero [attention] → triple-image swiper [understanding] → dual-image emblematic product [proof] → tabular footer [close, rest]; no climax spike — restraint is the register. *Argument long-scroll* (`argument-scroll`; Son Daven, winner-verified) — 15+ sections: preloader Flips into eyebrow+display hero [attention] → prologue → place tour with walk-time counters [proof beats] → financials → "Become part of the legend" [climax fused with the close] → contact footer [rest]. *Cinematic engine* (`engine-world`) — pavilion-glide variant, built on the rooms procession under a continuous score (Cartier, shipped + case study): in-engine loader → a scored camera procession through six self-contained alcoves, one watch per room and one charged gesture each, scenes disposing and loading as you cross between them → the object held still on a pinned media step-through → in-world sign-off. Walking the pavilion is mixing the score — the stems cross per room, the wayfinding recedes between rooms and the score never stops; one charged gesture per alcove, never two. Needs a WebGL path: author the scene through the delegated WebGL build (`ingredients/web3d-for-sites.md` §The delegation contract). Folio variant (Depo Luxe, winner-verified): loader → H1 over a WebGL field [attention] → nav-index, spotlight-dim [understanding] → signed wordmark footer [rest]. *Heritage-revival long-scroll* (Urban Jürgensen, winner-verified; no catalog slug of its own) — unconventional text-load entrance → an infinite vertical storytelling spine that never bottoms out → an infinite horizontal product carousel → a rotatable 3D watch on the product page as the only late spike.

Route on the brief's declared inputs, never on a taste read: an established house with a catalog and commerce behind "Discover" → `maison-scroll`, zero peak, even restrained intensity. A venture with an ask — investment, membership, a joining moment → `argument-scroll`, the one late peak fused with the close. An object worth walking around, with a WebGL path declared → `engine-world`, spectacle distributed room by room. A revived storied house → the heritage-revival spine, which takes `argument-scroll`'s shape with an infinite vertical track in place of a bottom and the 3D-object interaction as its only spike. The arc fixes the macrostructure and the climax count downstream; all four are decidable from stated brief facts, and two are never blended.

**Hero architectures** — *H-A slider maison* (Delvaux — classes and copy winner-verified; the easing numbers carried from earlier source reads, not re-verified this run): visual + scrim → serif SplitText title up behind a mask (dur 2, stagger .2, `power4.inOut`) → roll-swap / `--stroke` CTAs (~.2s) → figure `clip-path:inset()` wipe (1s). *H-B eyebrow + display Flip-handoff* (Son Daven — award, studio and stack winner-verified; every number below an executable default): `master-preloader` scene → logo Flips into the header → eyebrow rise → display `yPercent 250→0` behind a mask, ~1.2s, easeOutQuart → magnetic CTA, `elastic.out(1,0.3)`. *H-C in-engine statement* (Depo Luxe winner-verified; Cartier shipped + case study): loader → SVG logo fill → dissolve, no hard cut → H1 / universe settles, hidden gestures live from frame one. No fold CTA in shape H-C.

**Section chain** — example roles, intensity targets and states for this register. Choose the applicable rows and derive their order and form from the brief's story; this is a reference composition, not a mandatory page template. Intensity numbers are authoring targets, not measured jury scores.

| role | form | pairs | intensity | state it owes |
|---|---|---|---|---|
| hero | full-bleed media behind the masthead (maison / argument); in-engine hero (engine); slider-maison (fullscreen visual + scrim) | h1 masked per-line reveal \| word scatter-in; media clip-path inset wipe \| grayscale-to-colour curtain wipe; CTA row label roll-swap \| invert to the full section token \| line / stroke-draw; loader real-progress Flip handoff \| SVG-path fill \| in-engine brand-object assembly | 8 | pointer-alive on desktop — a dead hero is a defect: the CTA answers hover, the media answers the pointer wherever a magnetic or parallax layer exists; the signature thread is live from frame one, never introduced later |
| proof | text/media split (media alternating); native scroll-snap swipe / lateral swiper; place tour; pinned media step-through; commerce product card | h2 word scatter-in; prose scrubbed reading wash + key-term accent; media clip-path inset wipe \| editorial hover zoom \| grayscale-to-colour curtain wipe; counters walk-time counter roll | 6 | editorial figures answer hover with a contained `scale(1.02–1.05)` plus one companion cue; commerce cards swap to a second angle or a short muted craft video; the scrubbed thread runs under the whole band; prose may carry the scrubbed reading wash |
| index | index header + row list; nav-index over a WebGL field | rows spotlight-dim siblings; h2 word scatter-in | 6 | the hovered row lights with an accent rule and cross-faded metadata while siblings drop to `opacity:.2`; plain tap target on touch — this is the primary interaction wherever the index is the page's spine |
| feature / room | scored rooms procession (delegated 3D); full-bleed figure; text/media split | ground WebGL shader field \| the scored drift; media clip-path inset wipe \| dolly zoom; object raycast hover and tap state; wayfinding room index; in-scene ambient life; curtain transition between rooms; hidden detail press-hold reveal + cursor verb label | 7 | in the procession arc each room is a contemplative beat at even-high intensity with hidden gestures live from frame one and scroll driving the camera; the custom cursor is scoped to the WebGL surface and morphs to its verb label so the gesture is discoverable |
| close | closing panel: one imperative + channel rows; the join-the-legend climax panel | ask masked per-line reveal; channels link cross-fade + bullet dot + label roll-swap | 6 | one imperative and decisive channel rows, no media slot — the close cannot become a mood reel; the `argument-scroll` arc spends its **one** peak here at intensity 9, every other arc keeps the close quiet |
| footer | tabular index (newsletter + accordion nav + house tagline); oversized wordmark (signed); contact-first (departments by city) | wordmark masked per-line reveal, quiet; links cross-fade + bullet dot | 4 | tabular or contact-first carrying the house tagline; rest, never a spectacle — the palette may flip once at the very close and stays legible in both states |

**Footer** — tabular/contact-first carrying the maison tagline, never a spectacle (winner-verified). Delvaux: newsletter + accordion nav + "The Oldest Fine Leather Goods House in the World"; CSS-level: `footer__newsletter-holder{margin-bottom:clamp(3.75rem,…)}` keeps the page's generous rhythm. "Sales departments" by city (Son Daven). Depo Luxe, signed: oversized wordmark + "All work © DEPO LUXE (and respective owners), 2026". Build all three from the notes above.

**Arrival** — the Effect palette Loader row's families hold (`ingredients/preloaders.md`): Flip handoff (family 3, wordmark / logo assembly; Son Daven); SVG-path-fill (family 3; Depo Luxe); in-engine boot (family 3, brand-object assembly; Cartier, shipped + case study); instant paint (Delvaux — only `nuxt-loading-indicator`, winner-verified absence). Routes (`ingredients/page-transitions.md`): Delvaux runs Nuxt routing with no curtain (observed, implementation unverified) and Cartier's scene changes run the loader's shader pipeline (Animations/Transitions 9.00) — on any multi-page build the route swap plays the curtain/overlay wipe plus loader re-entry so the thread survives the navigation.

**Copy voice** — Quoted to calibrate, never to ship — imitate the specificity (the named place, the count, the refusal), never the wording. Third-person inherited; founder brands go first-person-plural. One elevated tagline or one long lyrical sentence per surface; CTAs 2–4 words. Verbs invitational — Discover, Explore, Step inside — never a transaction. Heritage signatures earned by a date ("Since 1829"); sentence case except product names; tabular numerals for prices, editions and counts. Refuses price-forward CTAs, urgency, feature bullets, self-narration of the interaction.
- "The Oldest Fine Leather Goods House in the World" (Delvaux) — a superlative earned by a date.
- "investment project" / "Design Resort Hotel" (Son Daven) — the offer named before any poetry.
- "Become part of the legend" (Son Daven) — the buy moment as joining a heritage.
- "Beauty is the symbol of the morally good" (Brunello `.com`) — Kant stands in for product talk.
- "250-year-old" Swiss-Danish house (Urban Jürgensen) — the revival led by the count, not the adjective.

**Imagery art direction** — one grade page-wide, split by brand never within a page, never stock. Delvaux: product-as-hero campaign stills + boutique interiors. Son Daven: real photo + film — 3 videos, 68 images, zero CSS background-image (winner-verified counts) — warm+dark grade (shipped/jury). Depo Luxe: monochrome, pure white on pure black (winner-verified); the WebGL-displaced footage reading is reported and appears in no award description or teardown found on re-verification. Cartier: real-time 3D renders — the render is the photograph (shipped/case-study); engraved type as 3D objects is seed-only (single-source/seed). Brunello: frosted glass, soft blur and hand-drawn sketch detail, from the makemepulse case study rather than the award page.

**Mobile / touch** — the scroll-driven signature thread is the touch strategy, because it is exactly what survives the pointer going dormant. The décor bed, clip and curtain reveals, the WebGL displacement ground, the infinite scroll and the scored 3D drift all work on touch, so the continuation thread is never lost on mobile; the route-transition overlay is scroll- and time-driven, so it fires on tap-navigation too. Pointer classes go dormant: magnetic pull returns to native, pointer-parallax off (depth comes from scroll), any custom cursor stays scoped to the WebGL surface and its contextual label is replaced by an on-object hint. Figure hover-zoom degrades to tap-opens-detail; a commerce card's second-image or video swap degrades to tap-advances-view; CTAs answer `:active` with a 90–160ms flash floor; index rows become plain tap targets with no sibling dim. A native OS-momentum scroll-snap swipe gallery — next-cell peek, enhancer-fed dots — is the mobile gallery signature and the scored Awwwards Mobile Excellence line; drag surfaces set `grab`→`grabbing`. The bespoke soundscape stays behind a gesture-unlocked toggle.

**Variation** — this section chain is one legal costume of the archetype, never *the* skeleton. Structure is story-native: the body's sections derive from the universe's spine, then check against these roles for coverage — never the reverse. The axes serial winners measurably rotate between builds (21-artifact corpus, 5 studios): body content archetype and item counts, the one signature device (never reused across builds), the close mechanism, the hero medium, the index/HUD costume. What persists as DNA: type grammar, the motion register (the register itself, never the named reading/interaction kit — that kit is a device, rotated per build like the signature), annotation grammar as a form, engineering architecture. The same content archetype + item count + close mechanism recurring across two different-brand builds has zero winner precedent.

**Anti-signals** — no product card grid above the fold; no "Shop now" hero CTA, no urgency; nav surfaces follow the Effect palette Nav row — its Delvaux same-ink hairline is the one sanctioned override to the zero-nav-`border-bottom` gate; no fake timed spinner; no stock; no neon accent; no per-letter typewriter; no page-wide cursor blob; copy never feature-lists.

## Spectacle menu

*Cartier, gesture-revealed timepiece* (shipped/case-study): gesture into a universe → scored glide → a watch worth contemplating. *Son Daven, the place tour* (structure lived, numbers an executable default): scroll → landmark reveals + walk-time counters → a distance map you explore, not a reel. *Depo Luxe, the entrance* (winner-verified award, reported mechanics): video-preloader → SVG fill → WebGL field + audio — the film is the navigation. *Louis Vuitton Collectibles, the charged gesture* (winner-verified): click-and-hold opens the object, and a scroll-driven "Change Universe" move carries the visitor between distinct environments.

**The hero beat.** The first viewport commits the material register and the entrance ritual at a high but never-loud amplitude, and it opens the thread rather than spending a firework. Three commit-shapes: *in-engine statement* — a scored 3D room settles out of the loader with no hard cut, hidden gestures live from frame one (Cartier, Louis Vuitton Collectibles, Depo Luxe's SVG-fill dissolve). *Eyebrow + display Flip-handoff* — a real-progress preloader Flips its logo into the header, the display type rises `yPercent 250→0` behind a mask over ~1.2s easeOutQuart, one magnetic circular CTA overshoots on `elastic.out(1,0.3)` (Son Daven). *Slider maison* — visual + scrim, serif SplitText title up behind a mask (dur ~2, stagger ~.2, `power4.inOut`), roll-swap or stroke CTAs, figure `clip-path:inset()` wipe over ~1s (Delvaux).

**The continuation beats** — the page is diffed against these, section by section.
- *pavilion rooms* (procession arc) — **distributed presence**: after alcove one the scored camera keeps drifting, five more self-contained rooms disposing and loading as the visitor crosses between them, each with its own horizons, water, mirrors and hidden gestures under a continuous score. Zero silence, no single peak (Cartier, six-room structure and score confirmed; per-scene transition timings not exposed).
- *décor bed under the mid-page* (argument arc) — **the thread**: fire-once block reveals play over a reversible scrubbed parallax/film bed while one idle touch stays welded to the wheel; prose keeps its scrubbed reading wash. The bed is the continuation (Son Daven; structure lived, numbers executable defaults).
- *living ground* (folio arc) — **the floor**, not a spike: every figure and the nav index sit on the WebGL displacement field, the spotlight-dim index carries the middle, audio runs behind a toggle throughout (Depo Luxe; interior mechanics reported, not sourced).
- *never-bottoming scroll* (heritage arc) — **continuity by refusing to rest**: infinite vertical spine plus infinite horizontal product carousel, unconventional text-loading transitions between beats, the rotatable 3D object arriving late on the product page (Urban Jürgensen, winner-verified).
- *lateral procession* (maison arc, the control) — **quiet carry**: a triple-image swiper moves product laterally at a measured pace, then the dual-image emblematic product; clip-path reveals and swiper motion, no always-on idle channel. The stillest continuation on record — and it took HM, not SOTD (Delvaux).
- *route change* (multi-page only) — **cross-navigation carrier**: the curtain/overlay wipe plus loader re-entry re-establishes the thread on the incoming page; without it the continuity law dies at the first page jump.

**The peak law** — verdict refined, from the winner evidence. Peaks stay capped at 0–1 in the luxury register, and a continuous, low-amplitude, reversible signature thread must run under every viewport from hero to footer; the hero opens the thread and never closes it. The luxury lever is the thread's amplitude — a scored 3D drift, a scrubbed parallax/film bed, a living WebGL displacement ground, a frosted craft skin, kept quiet, reversible and material — never its peak count. Escalating peaks belong to other archetypes; corporate-luxury escalates presence, not volume. Per arc: procession runs even-high intensity with no peak, each room its own contemplative beat; argument-scroll spends **one** late peak fused with the close; editorial maison runs zero peak at even restrained intensity; heritage-revival keeps the late 3D-object interaction as its only spike. Going silent after the hero is the defect the jury reads as least alive.

Evidence: the canonical exemplar is built as six equal self-contained rooms with hidden gestures in every scene and a continuous score, which reads as distributed presence rather than one climactic reveal — a structural inference from the confirmed six-room shape, not an award-body statement. Louis Vuitton Collectibles takes SOTD 2024-02-20 at 7.79 with Animations 9.4 on click-and-hold plus scroll-driven navigation between distinct environments, and Urban Jürgensen takes SOTD 2025-10-30 on a scroll that never bottoms out — both escalate presence, neither escalates volume. Son Daven takes SOTD 2026-06-05 at 7.62 with Developer Award 8.09 on a hero-to-footer thread whose late join-the-legend moment fuses climax and close. Delvaux, the stillest register, carries a community craft score directionally the corpus's highest and lands at Honorable Mention, a lower jury tier than Son Daven's Site of the Day; community voters rated its craft higher, so the inversion is real and the signal lives on the award-tier axis — moderate, caveated evidence, never proof that stillness alone caused the tier.
