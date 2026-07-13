# Corporate Luxury

Quiet luxury. Sophisticated restraint where generosity of whitespace signals exclusivity. Custom serifs at display, refined sans-serifs at body, palette anchored in neutral foundations punctuated by jewel tones or muted golds. Animation curves are long; nothing hurries. The voice is inherited rather than chosen.

## Canonical reference — Cartier Watches & Wonders 2025

**Site.** Cartier Watches & Wonders 2025
**URL.** `cartier-waw-0225.dev.60fps.fr`
**Award.** Awwwards Site of the Month, August 2025 (+ Developer Award)
**Studio.** Immersive Garden, with `60fps` and `Mooders`, for Cartier.

Built around Cartier's Geneva pavilion. Six contemplative 3D alcove universes around iconic timepieces. Slow tasteful motion. Refined typography. Hidden gestures. Bespoke cinematic soundscape. The platonic case for quiet-luxury restraint with sumptuous detail. The URL lives on the build studio's `dev.60fps.fr` subdomain rather than a Cartier-owned domain — unusual, but the canonical Awwwards-referenced location. Substitutable peers: `hermes.com` (orange and ivory with custom serif), `rolex.com` (dark greens and golds, editorial photography, slow pacing), `aesop.com` (warm neutrals, single custom serif, product-as-still-life), `bugatti.com` (deep blues and chrome, automotive gravitas), `immersive-g.com` (agency-as-luxury-brand).

## DNA — non-negotiable

- Generous whitespace (128–200px+ section padding) signals exclusivity, not waste
- Custom or premium serif at display sizes is the typographic mark of the archetype
- Color rests on neutral foundations punctuated by jewel tones, muted golds, or single deep brand color
- Motion uses long easing curves (1–1.5s, easeOutQuart `cubic-bezier(0.25, 1, 0.5, 1)` — verified independently on two of the line's winners; `cubic-bezier(0.16, 1, 0.3, 1)` is the snappier alternative) — nothing rushes
- Photography is treated and considered — every shot frames the product as object, not commodity

The archetype keeps its identity across flat editorial luxury (Hermès, Aesop), cinematic 3D pavilion (Cartier WAW), dark luxury (Rolex, Bugatti), and warm neutral lifestyle (Aesop, Loro Piana). Background register is an expression choice, not a definition.

## Common expressions

Three stacks fit the DNA. Pick the one matching brand voice and product type.

### Flat editorial luxury — Hermès / Aesop profile

Warm white or cream foundation (`#F8F5F0`, `#FAF8F5`) with custom serif headlines (Didot, Bodoni-adjacent), considered photography, generous gutters. Single jewel-tone accent (Hermès orange, Aesop sage, Loro Piana camel). Asymmetric image-text pairs. Hover is a 1.05 scale, opacity 0.7→1. Ideal for fashion houses, fragrance, premium lifestyle, artisan and craft brands.

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

Inter, Roboto, Arial as display fonts signal "no type decision". This archetype either commissions a custom serif or pairs a known premium serif (Tiempos, Sectra) with discipline. The luxury is in the choice and its execution, not the budget.

## Color

Color rests on neutral foundations.

- **Backgrounds**: warm whites `#F8F5F0`, `#FAF8F5`, cream `#FAF7F0`; deep neutrals `#1A1A1A`, `#0E1A1B`
- **Text primary**: charcoal `#2D2D2D` on cream, off-white `#E8E0D0` on dark
- **Text secondary**: warm gray `#8B8580`
- **Accent — jewel tones**: muted gold `#C5A572`, deep emerald `#006D5B`, sapphire `#1B365D`, ruby `#8B2E2E`
- **Signature 2025**: Pantone Mocha Mousse `#A47764`
- **Borders**: `#E8E4DF` or `rgba(0,0,0,0.06)`

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

- Easing: easeOutQuart `cubic-bezier(0.25, 1, 0.5, 1)`, duration 1–1.5s — Delvaux ships it byte-identical across CSS and GSAP; `cubic-bezier(0.16, 1, 0.3, 1)` is the snappier alternative
- Subtle parallax (5% maximum differential)
- Hover: gentle opacity shifts (0.7→1) and scale 1.05 over 600–800ms
- Image reveals: clip-path inset with long duration (0.8–1.2s)
- Page transitions: View Transitions API with slow cross-fades (400–600ms)
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

## What makes it award-worthy

A corporate-luxury site scores 8+ when the restraint feels chosen rather than generic — when the serif is felt before it's noticed, when the whitespace itself signals confidence, when the photography frames every product as an object worth looking at. Cartier WAW succeeds because the 3D pavilion and the slow tasteful motion are the brand's voice, not a layer of polish over a stock template.

The archetype loses identity at three failure modes: cookie-cutter minimalism (the safe muted geometric default that every brand adopted, actively rejected by judges), corporate sterility (whitespace without warmth, serif without conviction), and luxury costume (premium fonts bolted onto a generic SaaS template). Quiet luxury without the underlying craft reads as expensive theater.

## Ideal for

High-end fashion, luxury hotels, fine jewelry, premium automotive, wealth management, private banking, premium real estate, fragrance, watchmaking, artisan and craft brands, lifestyle direct-to-consumer with story.

## Cross-references

Read alongside `foundations.md` (typography systems, OKLCH for jewel tones, animation toolkit), `premium-patterns.md` (Doppelrand nested containers, button-in-button trailing icons, eyebrow tags), `anti-patterns.md` (no neon, no high saturation; jewel tones only), `audit-rubric.md` (Spacing 9+, Typography 9+, Motion 8+ are entry bars), `exemplars.md` (Hermès, Rolex, Aesop, Bugatti, Immersive Garden).

## Effect palette — what this line's winners ship

Seven award pages — Cartier (Awwwards SOTM Aug 2025), Longines (SOTD Nov 2023), Omega (SOTD Jan 2026), Son Daven (SOTD Jun 2026), Delvaux (Awwwards HM Jun 2026), Brunello Cucinelli (SOTD Jul 2026), Depo Luxe (SOTD Jul 2026). Four read at the source level (shipped CSS/JS of Son Daven, Delvaux, Brunello via its `.ai` sibling, Depo Luxe); the 3D watchmaking trio is bundle-grep plus case-study prose.

**The grammar** — pick one easing and one reveal primitive, reuse both at every scale, and give each element class its own geometry. The corpus easing is easeOutQuart `cubic-bezier(0.25,1,0.5,1)` — it turns up independently on Son Daven and Delvaux (byte-identical in Delvaux's CSS var and its GSAP `CustomEase`), which makes it arguably more canonical for this line than the DNA's `cubic-bezier(0.16,1,0.3,1)` easeOutExpo (still valid, snappier tail — keep it for a Brunello-style snap). The reveal primitive is reveal-from-behind-a-clip: masked `translate` for type, `clip-path:inset()` for media and overlays. Change the axis and geometry per element, never the curve or the primitive without a brief-tied reason.

**Buttons / CTA** — four verified moves, no pale-tint fill among them:
- **Label roll-swap** — two label copies in an `overflow:hidden` clip; hover rolls both `translateY(-100%)` together, `transform .2s cubic-bezier(.65,0,.35,1)`, no color event · pick as the default primary-CTA move for editorial maisons · (Delvaux, Awwwards HM Jun 2026; Son Daven, SOTD Jun 2026 — observed, implementation unverified).
- **Invert to the full section token** — CTA fills with the *solid* section token, geometry extended `-4px` past the label with a 2px outline in the bg colour — never `rgba(token,0.1)` · pick when one hero CTA needs weight · (Son Daven, SOTD Jun 2026).
- **Line / stroke-draw** — draw an SVG ring, or fade a `currentColor` `:before` underline at `height:.5px` opacity 0→1 · pick over any fill when the surface is photographic or 3D · (Brunello Cucinelli, SOTD Jul 2026; Depo Luxe, SOTD Jul 2026).
- **Spotlight-dim siblings** — hovering one list/nav item drops the others to `opacity:.2`, not itself; Depo Luxe also swaps the hovered row's metadata · pick when a nav index is the primary interaction · (Son Daven, SOTD Jun 2026; Depo Luxe, SOTD Jul 2026).

**Links** — cross-fade `color 1s cubic-bezier(.65,0,.35,1)` between ink and a muted brand tone, with a 2px bullet dot fading in beside the label rather than an underline grow (Delvaux, Awwwards HM Jun 2026). Or an underline that *appears* — `currentColor` `:before`, opacity 0→1 over `.1–.2s` — instead of growing from a point (Depo Luxe, SOTD Jul 2026).

**Figures / cards** — reveal with a `clip-path:inset()` wipe, `1s cubic-bezier(.25,1,.5,1)` (Delvaux, Awwwards HM Jun 2026). Hover zoom stays `scale(1.02–1.05)` over `0.8–1.5s`, guarded by `@media (hover:hover)` — never a fast 1.1× snap; Delvaux's only zoom in the whole sheet is `scale(1.02)` on a swatch (Brunello Cucinelli, SOTD Jul 2026; Delvaux).

**Nav** — four verified surfaces, zero contrasting border-bottoms: the section's own colour faded in past a scroll threshold (Son Daven, SOTD Jun 2026); an opaque plate plus a same-ink `border-bottom:1px solid rgba(29,29,27,.03)` ~3% hairline (Delvaux, Awwwards HM Jun 2026); a photographic top-down gradient scrim, no fill (Brunello Cucinelli, SOTD Jul 2026); `backdrop-filter:blur(40px)` over a ≤5% tint that flips with the section (Depo Luxe, SOTD Jul 2026). Never a contrasting-accent `border-bottom`; frosted-white glass is not a default — two of the four use no blur at all. The Delvaux hairline is the ONE sanctioned exception path to the zero-nav-`border-bottom` gate — reusing it takes a written override in the design_plan citing this row; same-ink at ≤5–6% alpha only, never a contrasting line.

**Text** — masked per-line or per-word reveals only. SplitText lines under an `overflow:hidden` mask, sliding up behind the clip (`power4.inOut`, dur 2, `stagger .2` on Delvaux; `yPercent 250→0`, `durL 1.2s` on Son Daven). Word scatter-in from alternating `yPercent` is a warmer variation for craft brands (single-source, Son Daven, SOTD Jun 2026). Never a per-letter typewriter.

**Cursor** — two poles, no page-wide blob. Native cursor + magnetic pull for editorial/e-com: elements translate toward the pointer and spring back with `elastic.out(1,0.3)`, applied to circular CTAs only — the elastic overshoot is the tell (Son Daven, SOTD Jun 2026); Delvaux ships no custom cursor at all. Or a minimal custom cursor scoped to the WebGL surface, `cursor:none` over that surface only (Brunello Cucinelli, SOTD Jul 2026; Cartier, SOTM Aug 2025). Set `grab`→`grabbing` wherever horizontal drag exists.

**Loader / intro** — content-driven, no fake timers. WebGL or frame-sequence heroes gate a real-progress counter on `Promise.all([assets, scenes, fonts.ready])` and Flip the logo into the header slot (Son Daven, SOTD Jun 2026; Cartier, SOTM Aug 2025), or reveal a logo whose SVG paths fill in as the loader advances (Depo Luxe, SOTD Jul 2026). A pure-CSS editorial DOM paints instantly — the scroll reveals carry the entrance (Delvaux, Awwwards HM Jun 2026).

**Mid-page life** — three welded channels, never decorated paragraphs: a fire-once reveal on every content block (`data-scroll-reveal="h|p|ctn|line"` on `ScrollTrigger.create({start:"top bottom", once:!0})`), a reversible scrubbed décor bed running under the whole mid-page — five parallax layers at `ease:"none"`, a frame-sequence film at `scrub:.25`, WebGL blackPoint/whitePoint grades — and one idle touch welded to the wheel, the marquee speeding with `timeScale(1+.01*velocity)` (Son Daven, 7.62, winner-verified). The one sanctioned way prose itself stays alive is a scrubbed reading wash, not a hover: `[data-highlight-text]` splits to chars and `.from(chars,{opacity:.1})` scrubs from `top 75%` to `bottom 50%`, re-firing every pass because it is décor over reading, never a reveal (Son Daven, winner-verified). Hover-on-text lives on nav, index, and links only — a per-char nav roll-swap staggered `{each:.025,from:"random"}`, siblings spotlight-dimmed to `opacity:.2` (Son Daven, winner-verified), an index-row metadata cross-fade where client and counter fade out as director and title arrive (Depo Luxe, 7.62, winner-verified) — with zero `font-variation-settings` shifts on hover across every readable sheet. Delvaux, the stillest register, ships no idle channel in 318 KB of CSS and lands HM below SOTD — stillness is a deliberate choice the jury reads as least alive (winner-verified). Wheel smoothing is universal at the tier, 5/5, library varies — Son Daven runs Lenis `duration:1.2, smoothWheel` off `gsap.ticker` with `lagSmoothing(0)`; Delvaux takes ScrollSmoother (`effects`, `normalizeScroll`, zero Lenis); Depo Luxe hand-rolls a VirtualScroll so scroll and WebGL render share one clock (winner-verified).

**Scroll texture** — clip-path figure reveals riding the scroll plus `data-scroll-displace` on footage, so the film itself shifts under the reader's hand (Son Daven, winner-verified), or swiper processions moving product laterally at a measured pace (Delvaux, winner-verified). The design_plan names one — the carry stays slow and material, on the corpus easing, never a bolted-on parallax.

**Idle band** — a bespoke soundscape behind a sound toggle where the brief earns it; otherwise ~1 quiet channel. Restraint is the luxury register — commit the soundscape deliberately or hold to the one quiet channel, never ambient décor.

**Anti-signals** — absent from every winner examined: a pale/washed tint fill on a CTA hover (they roll, invert to a full token, or draw a line); a contrasting-accent `border-bottom` under the scrolled nav; one uniform hover repeated across all element classes; generic fade-up-20px for everything; per-letter typewriter headlines; a fake timed spinner or fixed-duration progress bar; a large page-wide cursor blob with mix-blend-difference; frosted-white glass nav as a default; a neon or high-saturation accent (palettes stay two-tone warm-neutral or monochrome); a fast 1.1×+ image pop.

Channel calibration — this line's winners run 4–5 distinct interaction channels (per-class states, display-type effects, cursor, idle, scroll texture, replayable spectacle); the pre-emit critique's Aliveness axis reads against that band, never against bare coverage.

## Page recipe — how this line's winners build the page

Corpus — Son Daven (SOTD Jun 2026, live), Delvaux (HM Jun 2026, live), Depo Luxe (SOTD Jul 2026 + Dev Award, live), Brunello Cucinelli AI (SOTD Jul 2026, live shell; voice from `brunellocucinelli.com`), Cartier WAW 2025 (SOTM Aug 2025, media-only).

**Anatomy** — *Editorial maison scroll* (`maison-scroll`; Delvaux, winner-verified) — commerce behind "Discover": slider hero [attention] → triple-image swiper [understanding] → dual-image emblematic product [proof] → tabular footer [close, rest]; no climax spike — restraint is the register. *Argument long-scroll* (`argument-scroll`; Son Daven, winner-verified) — 15+ sections: preloader Flips into eyebrow+display hero [attention] → prologue → place tour [proof beats] → financials → "Become part of the legend" [climax, close] → contact footer [rest]. *Cinematic engine* (`engine-world`) — 3a pavilion (Cartier, shipped/case-study + seed): in-engine loader → glide through 3D universes (six alcoves, seed-only) [climax = gesture-revealed detail] → in-world sign-off; 3b folio (Depo Luxe, winner-verified): loader → H1 over a WebGL field [attention] → nav-index, spotlight-dim [understanding] → signed logo footer [rest].

**Hero architectures** — *H-A slider maison* (Delvaux — classes/copy winner-verified; easings technique/seed): visual + scrim → serif SplitText title up behind a mask (dur 2, stagger .2, `power4.inOut`) → roll-swap/`--stroke` CTAs (~.2s) → figure `clip-path:inset()` wipe (1s). *H-B eyebrow + display Flip-handoff* (Son Daven — tech hooks winner-verified; numbers technique/seed): `master-preloader` scene → logo Flips into the header → eyebrow rise → display `yPercent 250→0` behind mask, ~1.2s, easeOutQuart → magnetic CTA, `elastic.out(1,0.3)`. *H-C in-engine statement* (Depo Luxe winner-verified; Cartier shipped): loader → SVG logo fill → dissolve, no hard cut → H1 / universe settles. No fold CTA in Shape 3.

**Footer** — tabular/contact-first carrying the maison tagline, never a spectacle (winner-verified). Delvaux: newsletter + accordion nav + "The Oldest Fine Leather Goods House in the World"; CSS-level: `footer__newsletter-holder{margin-bottom:clamp(3.75rem,…)}` keeps the page's generous rhythm. "Sales departments" by city (Son Daven). Depo Luxe, signed: oversized wordmark + "All work © DEPO LUXE (and respective owners), 2026".

**Arrival** — the Effect palette Loader row's families hold (`ingredients/preloaders.md`): Flip handoff (Son Daven), SVG-path-fill (Depo Luxe), in-engine boot (Cartier, shipped/case-study), instant paint (Delvaux — only `nuxt-loading-indicator`, winner-verified absence). Routes (`ingredients/page-transitions.md`): quiet — Delvaux Nuxt routing, no curtain (observed, implementation unverified); Cartier's scene changes run the loader's shader pipeline (Animations/Transitions 9.00).

**Copy voice** — Quoted to calibrate, never to ship — imitate the specificity (the named place, the count, the refusal), never the wording. Third-person inherited; founder brands go first-person-plural. One elevated tagline or one long lyrical sentence; CTAs 2–4 words. Verbs invitational — Discover, Explore, Step inside — never a transaction. Heritage signatures ("Since 1829"); sentence case except product names. Refuses price-forward CTAs, urgency, feature bullets, self-narration.
- "The Oldest Fine Leather Goods House in the World" (Delvaux) — a superlative earned by a date.
- "investment project" / "Design Resort Hotel" (Son Daven) — the offer named before any poetry.
- "Become part of the legend" (Son Daven) — the buy moment as joining a heritage.
- "Beauty is the symbol of the morally good" (Brunello `.com`) — Kant stands in for product talk.

**Imagery art direction** — one grade page-wide, split by brand never within a page, never stock. Delvaux: product-as-hero campaign stills + boutique interiors. Son Daven: real photo + film — 3 videos, 68 images, zero CSS background-image (winner-verified counts) — warm+dark grade (shipped/jury). Depo Luxe: monochrome, pure white on pure black, WebGL-displaced footage (winner-verified). Cartier: real-time 3D renders — the render is the photograph (shipped/case-study); engraved type as 3D objects is seed-only (single-source/seed).

**Spectacle menu** — *Cartier, gesture-revealed timepiece* (shipped/case-study): gesture into a universe → scored glide → a watch worth contemplating. *Son Daven, the place tour* (winner-verified): scroll → landmark reveals + walk-time counters → a distance map you explore, not a reel. *Depo Luxe, the entrance* (winner-verified): video-preloader → SVG fill → WebGL field + audio — the film is the navigation.

**Anti-signals** — no product card grid above the fold; no "Shop now" hero CTA, no urgency; nav surfaces follow the Effect palette Nav row — its Delvaux same-ink hairline is the ONE sanctioned override to the zero-nav-`border-bottom` gate; no fake timed spinner; no stock; no neon accent; no per-letter typewriter; no page-wide cursor blob; copy never feature-lists.
