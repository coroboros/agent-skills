# Bold / Maximal

Every viewport inch carries content, and every element earns it. Layered compositions mix photography, illustration, 3D, and kinetic typography. Fills resolve to full role colors, never tints; type functions as art rather than communication; motion is constant and choreographed. Restraint belongs to other archetypes — here, more is more, but organized.

Tier 1 (DNA, anti-signals, macrostructures, reflexes) is `references/archetype/bold-maximal.md`, pushed into context by `scripts/direction_roll.py`. This file is tier 2: it loads at the design_plan commit, BY HEADING, never whole.

## Contents

- [Canonical reference — Ponpon Mania](#canonical-reference--ponpon-mania)
- [DNA — non-negotiable](#dna--non-negotiable)
- [Common expressions](#common-expressions)
- [Typography](#typography) · [Color](#color) · [Layout](#layout) · [Motion](#motion)
- [What makes it award-worthy](#what-makes-it-award-worthy) · [Ideal for](#ideal-for) · [Cross-references](#cross-references)
- [Effect palette — what this line's winners ship](#effect-palette--what-this-lines-winners-ship) — per-element-class recipes, the grammar, tap/focus/dormancy
- [Mid-page life](#mid-page-life) · [Scroll texture](#scroll-texture) · [Idle band](#idle-band) · [Channel calibration](#channel-calibration)
- [Page recipe — how this line's winners build the page](#page-recipe--how-this-lines-winners-build-the-page) — anatomy, hero, section chain, footer, arrival, copy, imagery, mobile, variation
- [Spectacle menu](#spectacle-menu) — the hero beat, the continuation beats, the peak law
- [Component index](#component-index) — the library ids this archetype reaches for

## Canonical reference — Ponpon Mania

**Site.** Ponpon Mania
**URL.** `ponpon-mania.com`
**Award.** Awwwards Site of the Month, October 2025 (+ Developer Award); in the running for GSAP Site of the Year 2025
**Studio.** Independent project.

An interactive comic about a megalomaniac sheep DJ. Built with `OGL` WebGL, `Nuxt`, `GSAP`, and `Matter.js` physics (Codrops case study 2025-10-07). Every hallmark of the archetype is dialed up: oversized animated panels, kinetic illustrated typography, overlapping comic compositions, a near-black illustrated world lit by two panel hues, music-player navigation metaphor. The reference for designers who think bold means timid. Substitutable peers: `figma.com` (five brand hues rotated per section), `playstation.com` (full-spectrum prism with kinetic typography), `mailchimp.com` (Cavendish yellow with Cooper Hewitt display).

## DNA — non-negotiable

- One motion metaphor — a single input mapped to a single verb — forged in the hero and reused as the page's whole grammar; every planned mechanic binds to that same input or it is décor, capped at one secondary channel
- Kinetic typography functions as art, not as caption — display sizes 100–300px+, variable-font animation
- Layered composition mixes media (photography, illustration, 3D, video) with intentional overlap and z-index choreography
- Constant choreographed motion — staggered reveals, parallax depth, scroll-triggered sequences; no section falls below two live channels
- One signature kinetic moment per page — the hero typography reform, the panel sequence, the specimen grid, the closing clone-storm — that holds the page's identity

The archetype keeps its identity across bright illustrated (Ponpon, Mailchimp), dark neon-saturated (PlayStation, Figma Config), warm pastel maximal (kids' brands, gaming-adjacent), and full-spectrum prism (rotating-per-section brand hues). Background register is an expression choice, not a definition.

## Common expressions

Three stacks fit the DNA. Pick the one matching brand personality and audience.

### Bright illustrated — Ponpon Mania profile

The illustrated world is the maximalism; the shipped palettes run tighter than the register's name suggests — Ponpon holds a near-black `#171717` base with `#FEECE3` type and two panel hues (`#7E7EFF` + `#F894C0`), and Warhol Arts holds one warm hue in multiple tones (`#FB4E2B`) rather than a multi-hue spread (Awwwards SOTD 2025-04, 7.37). Cartoon characters, illustrated panels, hand-drawn type accents. Kinetic illustrated typography with overlapping comic compositions. Music-player or comic-strip navigation metaphors. Ideal for entertainment microsites, kids and family brands, animated content showcases, interactive narratives, festival lineups.

### Dark neon-saturated — PlayStation / Figma Config profile

Dark base (`#0A0A0A`, `#1A1A2E`) with electric lime (`#CCFF00`), hot magenta (`#FF00FF`), cyan (`#00FFFF`) as primary accents. Multi-layer parallax, oversized brand colors that pop against the void. Glow effects, OKLCH multi-hue gradients. Variable font weight animation on scroll (weight 100→900). Ideal for gaming launches, tech conferences, music releases, esports brands, developer-tooling marketing.

### Full-spectrum prism — Figma / brand-rotation profile

Multiple brand hues rotated per section. Each section claims its own color world — magenta hero, orange features, lime testimonials, cyan footer — optionally as a per-section visual temperature rather than a flat hue swap. Restraint sits in the discipline of the rotation rather than the palette. This is the saturated register's expression only, and it rests on one corpus winner (DICH™ Fashion, Awwwards SOTD 2025-06-09 + Developer Award) plus Figma — never the archetype's default. Library id: `section-accent-rotation`. Ideal for design tools, multi-product platforms, agency portfolios, brand-system showcases.

## Typography

Display faces are art objects, not labels.

- **Display**: Monument Extended, Clash Display, Satoshi Black, Druk Wide, Reckless Variable — 100–300px+, variable weight (100→900) and width (75→150) animated through scroll. Clash and Satoshi are overexposed kit picks — rotate or justify (`inspiration.md`)
- **Body**: Satoshi, PP Neue Montreal, Inter (variable) — 16–18px, weight 400, line-height 1.5
- **Kinetic**: GSAP SplitText for splitting and reforming, weight/width interpolation tied to scroll position — the characterful variant, not the tier's monochrome line mask (`kinetic-splittext-maximal`)
- **Decorative type**: hand-drawn or custom letterforms in the bright illustrated stack

Scale contrast is extreme — display at 200–300px next to body at 16px. The contrast itself signals the archetype.

## Color

The color rule is binary; pick the register before the palette.

- **Saturated register** — 4–6 simultaneous hues, each claiming a fixed role (primary, secondary, signature accent, semantic states), or one rotated per section. Sourced to a single corpus winner (DICH) plus Figma; ship it only when the brief sells sensory maximalism
- **Kinetic register** — a restrained palette where the TYPE motion is the maximalism. Most of the verified corpus lives here: strictly monochromatic (21 TSI, Awwwards SOTD 2025-04-12, 7.38 + FWA + CSSDA), single warm hue in tones (Warhol `#FB4E2B` ×7 plus a lighter `#FFE5D5`), two hues (Exat `#0000cb → #FF0B00`), cream monochrome (Mat Voyce)

Background register per stack: bright illustrated takes saturated warm bases (`#FFC107` yellow, `#E91E63` pink) or off-white anchoring multi-color compositions; dark neon-saturated takes pitch dark `#0A0A0A` to `#1A1A2E` with neon accents; full-spectrum prism rotates per section, each its own world.

Fills resolve to FULL role colors, never tints — Cuberto's live CSS floods `#ce1352`, never a `hover:bg/10` wash. OKLCH multi-hue gradients animated via `@property` replace flat sRGB.

```css
@property --hue { syntax: "<number>"; inherits: false; initial-value: 0; }
.shifting-bg {
  background: oklch(50% 0.2 var(--hue));
  animation: hue-shift 8s linear infinite;
}
@keyframes hue-shift { to { --hue: 360; } }
```

## Layout

Layered compositions mix photography, illustration, and 3D with intentional overlap and z-index choreography.

```css
.maximal-hero {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  grid-template-rows: repeat(8, 1fr);
  min-height: 100dvh;
}
.hero-image { grid-area: 1/1/9/8; z-index: 1; }
.hero-title {
  grid-area: 3/4/7/13;
  z-index: 2;
  mix-blend-mode: difference;
  font-size: clamp(4rem, 10vw, 15rem);
}
.hero-tag { grid-area: 7/9/9/13; z-index: 3; }
```

`mix-blend-mode: difference` on text overlaying images creates dynamic visual effects with one CSS property. Z-index uses `zIndex.*` extension tokens — `hero`, `panel-front`, `panel-back`. Container widths and column counts bind to `containers.*` and `breakpoints.*`.

## Motion

Constant, choreographed motion is the archetype's heartbeat.

- Stagger 200–400ms between elements in sequences
- Variable font animation on scroll — weight 100→900, width 75→150
- Multi-layer parallax at different speeds
- GSAP timelines with pinned scroll sections
- Animated `@property` gradients
- Matter.js physics for tangible interactions (Ponpon's signature)

```javascript
gsap.to('.display-text', {
  fontVariationSettings: "'wght' 900, 'wdth' 150",
  scrollTrigger: { trigger: '.section', scrub: 1 }
});
```

Durations bind to `motion.duration-*`, easings to `motion.ease-*`. Stagger offsets bind to `motion.stagger-*` extension tokens. Scroll-pinned section thresholds bind to `scrollTriggers.*`. `Lenis` smooth scroll keeps the kinetic layer in sync with the page. Commit one easing camp and never mix: elastic/back-out (Warhol `back.out(2)`, Ponpon `elastic.out(0.7,0.7)`) OR expo-out (Cuberto `cubic-bezier(.16,1,.3,1)`).

## What makes it award-worthy

A bold/maximal site scores 8+ when the saturation reads as choreography rather than chaos — when every color is anchored to a role, when 200px display type is paced against scroll progression, when three layered media types coexist without competing. Ponpon succeeds because every kinetic decision serves the comic-narrative metaphor; the page is read as much as it is consumed.

The archetype loses identity when "bold" becomes color randomness, when kinetic type fires without a story, when overlapping compositions trap the eye instead of guiding it. Maximalism without choreography is noise.

## Ideal for

Creative agencies, entertainment microsites, music festivals, Gen Z brands, campaign and product launches, gaming releases, design conferences, illustrated commerce, comic-narrative microsites, type foundries and typography products.

## Cross-references

Read alongside `foundations.md` (variable fonts, kinetic type, OKLCH, GSAP SplitText), `production-hardening.md` (motion of this density tests mobile performance budgets), `anti-patterns.md` (Density 6+ doesn't excuse missing accessibility — `prefers-reduced-motion` swap is mandatory), `exemplars.md` (Figma, Duolingo, Mailchimp, PlayStation).

Provenance for every claim below — the researcher rounds and the fresh-context refutations that corrected them — lives in the public deep-research corpus of `github.com/coroboros/research`, under `articles/award-winning-websites-2025-2030/deep-research/`: `archetypes/bold-maximal.md`, refutations folded under its `## Refuted` heading, the raw reports preserved verbatim at commit `fd5d1b6`.

## Effect palette — what this line's winners ship

Corpus — Ponpon Mania (Awwwards SOTM 2025-10 + Developer Award, in the running for GSAP SOTY 2025; OGL/Nuxt/GSAP/Matter.js), Warhol Arts (Awwwards SOTD 2025-04, 7.37, BL/S® / Serhii Polyvanyi; Webflow/GSAP), DICH™ Fashion (Awwwards SOTD 2025-06-09 + Developer Award + PRO; Webflow/GSAP/Spline/Unicorn Studio), Exat / Hot Type specimen (Awwwards SOTD 7.73 + FWA of the Day + CSSDA Website of the Month 8.83, Best UI at CSSDA Website of the Year 2025; Studio Size & RISE2 for Hot Type), 21 TSI (Awwwards SOTD 2025-04-12, 7.38 + CSSDA WOTD + FWA of the Day; type8 studio + DEPARTMENT Maison de Création; OGL/Anime.js/Locomotive — a BOUNDARY member, strictly monochromatic and maximal on the motion axis only, kept as a floor witness and never as saturated-color canon), Mat Voyce (Awwwards SOTD + FWA SOTD + Webby honouree + Awwwards SOTM nominee 2025-01; studio Uncommon), Eloy Benoffi (Awwwards Honorable Mention + GSAP SOTD + CSSDA Best UI / Best UX / Best Innovation / Special Kudos; glitch-maximal folio, ASCII-flower décor), Cuberto (Awwwards SOTD 2018-06-22, 7.37 — reference-tier, outside the 2024–2026 window), Lando Norris (SOTD 2025, 8.18), plus Maxima Therapy, Stefan Vitasović, Obys. Lando was read from live CSS (computed rules quoted); Warhol, DICH, Exat, Ponpon, Eloy and 21 TSI come from their Codrops case studies plus Awwwards entries; the rest from Awwwards/FWA entries and studio writeups; every Cuberto amplitude below is carried-verified from a prior run's live-CSS read, not re-fetched.

**The grammar** — Variety coheres when one shared law binds visibly different mechanics. Cuberto runs four interactions — dome fill, skewed roll, scaling underline, contextual cursor — all on one expo-out curve (`cubic-bezier(0.16,1,0.3,1)` ≈ `(0.19,1,0.22,1)`), with fills resolving to *full* role colors, never tints (carried-verified live CSS). Ponpon binds physics, type, scroll, and nav to one comic/music metaphor: scroll is a playhead, nav a track list. Pick one easing family (expo-out or elastic, not both) and one loud signature per element class — CTA ≠ link ≠ image ≠ nav — then run secondary elements as quieter variants at 40–60% of the signature's transform distance AND duration. Unity is the shared curve + color rule + loud/quiet hierarchy, not a cloned hover.

**Buttons / CTA** —
- **Rising dome fill → inversion** — a pill (`border-radius: 1000px`, `overflow: hidden`) holds a fill layer parked below (`transform: translateY(101%)`, `background: currentcolor`, domed leading edge `border-radius: 50% 50% 0 0`) that rises and flattens on hover, `transition: transform 0.5s cubic-bezier(0.4,0,0,1)`; the solid variant fills with a full token (`#ce1352`, `0.5s Power3.easeOut`, retract `0.4s`) and inverts the icon. Pair it with a label swap-slide synced to the fill — rest label out (`opacity: 0, y: -20%`, `0.15s Power2.easeIn`), duplicate up (`y: 100%→0%`, `0.2s Expo.easeOut`), clipped. The curved leading edge is the signature; a flat wipe reads generic. *Primary CTA.* (Cuberto, reference-tier; amplitudes carried-verified). Library id: `fill-invert-cta`.
- **Magnetic pull** — the button or its label translates toward the cursor inside a proximity radius on `mousemove` and elastic-settles back on leave. A distinct mechanic from the fill, and a no-op on touch — commit one CTA signature per build, never both. (Cuberto, carried-verified). Library id: `magnetic-cursor`.
- **Darker same-hue shift** — where a saturated button recolors, go *darker*, never paler: Stripe `#533afd → #4434d4` + `translateY(-2px)` lift; Tailwind `bg-blue-500 → hover:bg-blue-700`; Geist keeps the primary a full solid `#171717` with no wash. *Dark-neon / brand-solid builds where a directional fill is too much.* (design-system corroboration).
- **Accent-swap face** — button carries `overflow: hidden` and swaps label/nav color to the one hot hue on hover (`#D2FF00` against `#111112`). *Dark-neon builds where the accent is the whole identity.* (Lando Norris, SOTD 2025) — Rive-canvas face is observed, implementation unverified.
- **Physical clone-storm** — the closing connect-CTA spawns duplicates as the cursor moves (two per `200px` of travel, up to `200`, `mix-blend-mode: difference`), exiting `opacity: 0, scale: 0.6, ease: 'back.in(1.7)'` on leave. *One maximalist button per page, spent at the page close, never repeated UI.* (Eloy Benoffi, Awwwards HM + GSAP SOTD) — single-source. Library id: `cursor-spawn-trail`.
- **Hard press** — an offset shadow lifts on hover and collapses on press, `125ms linear`: a mechanism, not a gesture, and the honest touch answer where no fill exists. Library id: `hard-press-button`.

**Links** —
- **Skewed text-roll** — label sits in a clipped box with a duplicate below; on hover the pair translates `-105%` while each layer resolves a `skewY(0deg) ↔ skewY(7deg)` peel, `transition: transform 1.2s cubic-bezier(0.19,1,0.22,1)`. The 7° skew lifts it above a plain vertical roll. *Overlay menu items and large nav labels.* (Cuberto, reference-tier; amplitudes carried-verified).
- **Scaling underline / marker draw** — a pseudo-element underline scales in `scaleX(0)→scaleX(1)`, `transition 1s cubic-bezier(0.16,1,0.3,1)`. Keep it the *quiet* treatment so the CTA fill and menu roll stay loud. *Utility and footer links.* (Cuberto, reference-tier).
- **Per-char rollover** — the nav variant: each character rolls on hover/focus, staggered, with the accessible name preserved by `aria-label` (Mat Voyce ships the per-letter roll on its nav). Library id: `split-rollover`; the decode variant is `scramble-decode` (DICH section-nav).

**Figures / cards** —
- **Graded / random-stagger reveal** — reveals are choreographed, not uniform: rows graded per easing (`power3.in` / `power2.in` / `power1.in`), cards scaling in steps (`1.75→1.25→1`) with `stagger: { from: 'random' }` and randomized `transform-origin`. `from: 'random'` is the maximalist tell. *Dense grids where uniform stagger feels mechanical.* (Eloy Benoffi, GSAP SOTD; Ponpon Mania, SOTM).
- **Shared DOM+WebGL scene under one scroll** — scroll drives a WebGL camera/uniforms, scroll velocity fed into depth (`z = 5 + velocity * 0.01`), reversible on scroll-back. *The one section that must feel three-dimensional — the medium that separates 8.5+ scorers; use once.* (Ponpon Mania, SOTM; Stefan Vitasović; 21 TSI, Awwwards SOTD 7.38 + CSSDA + FWA).

**Nav** — Default is a `position: fixed` bar kept transparent through scroll — `background: rgba(0,0,0,0)`, `backdrop-filter: none`, `border-bottom: 0`, at the top *and* after scrolling — so the maximal canvas reads through; opening the menu drops a full-viewport curtain, the bar itself never solidifies (Ponpon stays transparent after scroll, winner-verified; Cuberto reference-tier, Lando live CSS). When a surface is genuinely needed, frost it — `background: hsl(0 0% 100% / 0.5)` + `backdrop-filter: blur(16px)`, no border or a neutral low-opacity hairline (Aqtos, Blend — blur/opacity values observed, implementation unverified) — or blend-invert with `mix-blend-mode: difference` over alternating sections (Blind Barber, single-source). Winners never solidify to an opaque bar with a contrasting brand-colored border-bottom.

**Text** — Spend one signature headline and keep the rest quiet. SplitText with a *characterful* per-unit transform: Warhol enters per-char `scale 0→1` on a warm single-hue array (`#FB4E2B` ×7 plus a lighter `#FFE5D5` final char — one hue in tones, not a multi-hue cycle), `back.out`, `0.1s` stagger, fired post-preloader (winner-verified); Ponpon enters lines from `x: "100%"` with `skewX: random(-25,25)`, `rotation: 5`, `ease: "elastic.out(0.7,0.7)"`, `stagger: 0.06`, reversible on scroll-back (winner-verified); Stefan splits per-character with index-scaled expo (`1.25s + index*0.025s`, `ease: easeExpOut`). Elastic camp ≠ expo camp — pick one per build. Oversized type animated beyond viewport bounds as the whole interface is signature-grade for type portfolios (Mat Voyce, SOTD + FWA — observed, implementation unverified; copy no params). Library id: `kinetic-splittext-maximal`; the RGB channel-split heading that punctuates in 600ms bursts is `glitch-type`.

**Cursor** — The pointer chrome is a first-class element on this line, not only a trail: a lerped dot or ring (`lerp ~0.1–0.2` toward the real pointer) that morphs by CONTEXT — grows and surfaces a label (`VIEW` / `DRAG` / `OPEN`) over media and drag zones, shrinks to a dot over text, and can swap shape or color per section (DICH runs three variants: landing minimal-hypnotic, case denser-electric, transitions barely-there glimmer — winner-verified). Cuberto's contextual state cursor is the canonical spec — `::before` rescales and re-modes per target (`-pointer` `scale(0.3)`, `-text` `scale(0.8)`, `-lg` `scale(1.15)`; over interactive elements `×4` scale, drop to `opacity: 0.2`), driven by `mouse-follower` defaults `speed: 0.55`, `ease: 'expo.out'`, magnetic `stickDelta: 0.15` (carried-verified live CSS, not re-fetched). The state changes carry meaning; the lag alone does not. Dropping it deliberately when the page already runs heavy WebGL/Rive motion is a real choice, not an omission (Lando Norris) — kill it on small screens either way. Library ids: `custom-contextual-cursor`, `magnetic-cursor`, `pointer-parallax`.

**Loader / intro** — Winners split on preloader vs instant paint, but never a decorative counter+curtain over a static hero. Resolve the intro into live UI: the loading bar *becomes* the navbar (Eloy Benoffi, Codrops-verified — single-source), the intro IS scene one of the narrative (Ponpon Mania, SOTM; library id `narrative-scene-one-loader`), or a mood gate sets the temperature before chapter one (DICH's After Effects → Lottie animation, winner-verified). An asset-gated `0→100` counter is legitimate only when the hero genuinely ships heavy media, and the numerals should carry the concept (`steps(n)` progression; GT America, Black Messiah, Naya). Instant first paint with no full-screen counter is defensible on editorial-leaning maximal (Locomotive, SOTM). Hand off into the hero's entrance SplitText once fonts and assets are ready; under reduced-motion, skip the gate and paint a static branded frame.

**Element states — tap, focus, dormancy.** The pointer layer is one costume of the state; the tap and focus answers are not optional and not a degraded copy.
- **CTA** — the fill IS the tap answer on touch (press-driven), or a hard-press offset-shadow collapse at `125ms`; flash floor `90–160ms`. Magnetic pull is a no-op on touch, with no pointer to attract to. `:focus-visible` mirrors hover exactly — full flood plus inversion, so the fill is reachable by keyboard.
- **Link** — instant accent color swap on tap, no roll; the underline snaps to full. `:focus-visible` fires the underline wipe plus the accent recolor, and rolled nav links keep an accessible name via `aria-label`.
- **Figure** — tap-to-enlarge (the scored Mobile Excellence line) or caption reveal; the zoom does not fire on touch. `focus-within` triggers the same zoom + companion cue so keyboard users reach the caption. On dense grids the spotlight variant sharpens the hovered figure while siblings blur and dim — keep those galleries under ~10 items.
- **Index row** — the row highlights on tap-active and its metadata stays visible, so no content is trapped behind a hover. `:focus-visible` lights the same spotlight; the row is a real `<a>`, so focus order is preserved.
- **Heading** — hover ONLY on interactive headings (Exat's design-space names morphing specimen weight and width live; Warhol's Elvis section mapping cursor-x to `font-size` `1.375→2.875em`, `power3.out 0.3s`, return `0.4s`) — never on prose, body copy, or numbers. On touch the heading rests at its composed static frame; the entrance is the state that matters.
- **Nav** — the menu toggle drops a full-viewport curtain and links answer with an instant color swap; the bar never solidifies. Links keep a clean accessible name under the per-char split, `:focus-visible` shows the accent state, and the open menu is focus-trapped.
- **Cursor** — no custom cursor on `pointer: coarse`; the chrome is hidden entirely and the affordance it signalled degrades to the underlying element's tap answer. Cursor chrome never carries keyboard focus, and any label it surfaces on hover must be reachable without the pointer.

**Anti-signals** — Absent from every winner examined. The pale-tint fill on a primary control — no winner washes a saturated button with `hover:bg-primary/10` (the shadcn leak); that low-opacity tint is correct *only* on a ghost/outline variant that starts transparent. A solid nav bar with a contrasting brand-colored border-bottom on scroll — on no named winner. One universal hover cloned across buttons *and* links *and* cards — winners vary mechanic by element class. Fire-once uniform `IntersectionObserver` fade-up on every section — winners scrub, reverse, and grade stagger. Kinetic type with no story, the archetype's named failure mode. A lagging-dot cursor with no state, left running on mobile.

## Mid-page life

The prose zone between hero and footer runs two engines, never neither: content reveals fire once (`IntersectionObserver {once:!0}`) while a separate scrubbed décor channel keeps running underneath (`start:"top bottom", end:"bottom top", scrub:!0`) (Cuberto, reference-tier); the type-specimen register welds even its titles to scroll — each about-line re-spins `rotateX:-360` on enter and back to `0` on `onEnterBack`, per-char rises ride `scrub:!0` (Exat, Awwwards SOTD 7.73 + FWA + CSSDA WOTM 8.83, winner-verified) — so the fire-once law is register-conditional on this line. The operable mid-scroll spectacle is the centrepiece: Exat's cursor-proximity glyph field maps seven distance rings to `--fw` 42→228 plus a hex-lerped color per glyph in a viewport-gated 16ms rAF loop, beside a type tester whose sliders write `--ff/--fs/--fw/--lh/--ls` live (winner-verified; library ids `cursor-proximity-typefield`, `type-tester`). Warhol carries the same floor without WebGL: after the hero EVERY section moves on page-wide scroll reveals — per-char rotation entrances (`-45deg`, `back.out(2)`, `0.03s` stagger, `top 85%`) and mask-fill words (`width 100→0`, `scrub:1`) — with two section-local cursor channels on top (winner-verified). Hover-on-text lands only on interactive text — skewed nav roll, footer-link dim, Warhol's cursor-driven Elvis type — never on prose, headings, or numbers (winner-verified, 5 sites). A prose section whose content faded in once with nothing else moving is the merely-good tell; the tier always runs at least one scrubbed or looping channel through that zone. Wheel smoothing is table stakes here, not a differentiator — Lenis on Cuberto (41 refs, `smoothWheel` + `lerp`), Exat, Eloy Benoffi (1.3.3) and Lando, Locomotive Scroll on 21 TSI; Ponpon layers a VirtualScroll (10 refs) over the OGL scene so scroll can scrub it (Mat Voyce observed, implementation unverified).

## Scroll texture

Scroll-as-playhead chaptered physics — the page is a timeline and scroll scrubs its scenes (Ponpon Mania, winner-verified) — or oversized type running past the viewport so the overflow itself is the texture (Mat Voyce, winner-verified). The design_plan names one; on this line the carry is loud and structural, never a drifting background layer. A second, distinct carrier reads scroll VELOCITY rather than position: numerals and glyphs oscillate in a sine wave whose amplitude tracks scroll speed (Exat, winner-verified), a rendered object takes a `velocity * 0.01` feedback nudge (Ponpon, winner-verified), or the same signal drives RGB-shift and displacement distortion on imagery and surfaces (21 TSI, winner-verified) — compositor-only, viewport-gated, settling to the composed rest when the wheel stops. Library id: `scroll-speed-oscillator`.

On multi-route builds the transition between views is peak-adjacent and counts as one channel in the momentum floor: Ponpon renders the outgoing and incoming WebGL pages and mixes them through a custom shader driven by a GSAP tween (winner-verified), 21 TSI morphs its section transitions (winner-verified), Mat Voyce wipes "like chapters" (observed). Under touch or reduced-motion it degrades to a fast crossfade or an instant cut, never a sub-30fps blocking blend. Library id: `page-transition-choreography`.

## Idle band

~1 channel despite the volume: winners spend the energy on scroll and input, not on ambient churn. Commit one idle channel and let the rest of the page hold still, so the loud moves keep their contrast. The verified instances are chrome, not decoration — DICH's persistent coordinate HUD (rAF, zero-padded 4-digit, disabled under 768px) and its 40s marquee frame loop (winner-verified) — plus two spectacle channels that belong to the section that earns them: the cursor-spawn trail where images or accent pixels spawn on pointer travel, each tweening `scale 0→1` with a `brightness/contrast 300%→100%` decay then `opacity 1→0` over ~`0.4s` (Warhol runs it in the footer only, winner-verified; library id `cursor-spawn-trail`), and an opt-in audio bed muted until an explicit gesture behind one persistent, always-reachable toggle (21 TSI, single boundary-corpus source — library id `sound-channel`; ship only when the brief sells sensory maximalism).

## Channel calibration

Channel calibration — this line's winners run 4–5 distinct interaction channels (per-class states, display-type effects, cursor field or trail, idle, scroll texture, replayable spectacle); the pre-emit critique's Aliveness axis reads against that band, never against bare coverage. The count is a corpus-derived heuristic, not a scored juror rubric — read it as the shape of the floor, not as an award-body measurement.

## Page recipe — how this line's winners build the page

Corpus — Ponpon Mania (SOTM 2025-10 + Developer Award, live + Codrops), Warhol Arts (SOTD 2025-04, 7.37, live + Codrops), DICH™ Fashion (SOTD 2025-06-09 + Developer Award + PRO, live + Codrops), Exat (SOTD + FWA + CSSDA WOTM 8.83, live + Codrops), Eloy Benoffi (Awwwards HM + GSAP SOTD + CSSDA, live + Codrops), Mat Voyce (SOTD + FWA + Webby honouree, live), 21 TSI (SOTD 2025-04-12, 7.38 + CSSDA + FWA, Codrops), Cuberto (SOTD 2018, 7.37 — reference-tier, live copy carried-verified).

**Anatomy** — *Specimen Tour* (`specimen-tour`; Exat, winner-verified nav): oversized self-naming hero (attention) → About, one clause (understanding) → type tester (understanding+proof) → specimen glyph grid (climax, mid-page) → one capability per section, design space and stylistic sets (proof, quieting) → CTA reprise + credits (close); the proximity recolor is the signature, driven by the cursor and not by scroll. *Agency Statement* (`argument-scroll`; Cuberto, reference-tier ordering): the line's only true funnel — declarative hero (attention) → featured projects (proof, climax ~30% down) → services (understanding) → blog (texture, rest) → "Have an idea?" reprise + footer (close); Eloy compresses it to one scroll and defers the climax to the closing connect-CTA. Playground variant (Warhol Arts, DICH Fashion, both winner-verified): hero → named or color-temperature chapters, each owning one signature effect → modal or word-reveal CTA → spectacle footer. *Narrative Chapters* (`chapter-world`; Ponpon, winner-verified cover): the cover IS scene one — wordmark, "read now", chapter nav over live WebGL (attention) → chapter select, album covers on drag/scroll/snap (understanding) → panel scenes, camera moves, physics (proof+spectacle, climax) → About (rest/close); requires a WebGL path.

Route on the brief's declared inputs, never on a taste read. A story brand, comic or exhibition the reader operates, with a WebGL path available → `chapter-world`. A type foundry or typography product whose specimen can perform itself → `specimen-tour`. A studio or agency pitching, work-as-proof up front → `argument-scroll`; a cast of named subjects instead of a funnel → its playground variant. Never re-sequence a winner's ordering, never blend two shells, and never reuse the shell the last build committed — diverge inside the chosen one through variants and content. Then name the ONE motion metaphor before any layout: a mechanic-concept bound to a single input, not a palette (scroll-position-is-a-playhead, cursor-distance-drives-type, cursor-position-reshapes-canvases, section-enter-rotates-color, one-expo-curve-resolves-every-transition). Enumerate every planned mechanic and confirm each binds to that same primary input — or, for the curve-driven case, the same easing family; anything bound to a different input is décor, capped at one secondary channel.

**Hero architectures** — *Wordmark-as-hero* (Ponpon, winner-verified): the name is the largest object, rendered as art full-bleed; the DOM `<h1>` is a 9px credit, `#FEECE3` on `#171717`; header fixed, transparent; entrance = the Ponpon SplitText signature (Text row above), over cover physics — mask deform on proximity, balloon collision, cloud repulsion `radius=2 strength=1.5`. *Specimen-as-hero* (Exat, winner-verified): the cursor-proximity glyph grid IS the hero, opening the mechanic the mid-page climax will amplify. *Kinetic wordmark on a warm ground* (Warhol, winner-verified): SplitText `scale 0→1` on the `#FB4E2B` tone array, `back.out`, `0.1s` stagger, fired once the preloader hands off. *Pitch-statement hero* (Cuberto, reference-tier): `hero-masthead(media:none, align:start)` — declarative `<h1>` on `kinetic-reveal`, one-sentence standfirst on `text-emphasis-fill`, a low-key CTA row on `masked-label-swap`, proof one scroll below. *Loader-expands-into-hero* (Eloy, technique): the fold starts scaled-down while the loading bar grows into the navbar; cards enter via the graded random-stagger reveal (Figures row above). In every case the pointer layer must be live — a pointer-dead maximal hero is a defect.

**Section chain** — the winner-verified roles with their intensity map and the state each owes. Pick forms by role; never hand-write hero or section layout CSS.

| role | form | pairs | intensity | state it owes |
|---|---|---|---|---|
| loader | `narrative-scene-one-loader` (cover-as-scene-one); loader-bar-becomes-navbar; Lottie mood-gate | first-scene WebGL warm-up; progress-bar morph into the fixed nav | 7 | the engineered first-impression channel feeding the ~50ms verdict; hands off into the hero's entrance SplitText once fonts and assets are ready. Never add perceived latency past asset-ready without the mood payoff; under reduced-motion paint a static branded frame |
| hero | `chapter-cover` (world); `type-as-image` (specimen); `hero-masthead(media:none/back)` (pitch) | display `kinetic-splittext-maximal`; `cursor-proximity-typefield` when the hero IS the mechanic; ground `shader-surface` or physics | 8 | the pointer layer MUST be live — hero type reacts to the cursor (Warhol's Elvis scale, Exat's proximity) or physics reacts to proximity (Ponpon); the entrance fires once after the loader hand-off |
| proof / featured | `full-bleed-figure` (×N); `card-list`; feature grids | media `clip-reveal` \| `image-curtain` + `figure-hover`; caption `masked-label-swap`; graded random-stagger reveal | 9 | often THE climax (Cuberto ~30% down): figures answer with contained zoom to 1.1 (felt, never a 1–3% twitch) plus a companion cue, reveals are graded and `from:'random'` rather than a uniform fade-up, and the scrubbed décor channel runs under the whole zone |
| index / chapter-select | `index-reel-header` + `index-list`; `chapter-select` | rows `index-row-hover`; tiles snap-to-place on drag/scroll/click | 5 | hovered row lights an accent rule and surfaces metadata while siblings dim to 45% (the `index-row-hover` canon: Depo Luxe, Son Daven, Terminal); chapter tiles snap to place. Rows are the living index, never a static list |
| spectacle / specimen | `specimen-grid`; `type-tester`; delegated WebGL scene | `cursor-proximity-typefield`; `scroll-speed-oscillator` numerals; 3D X-axis line rotation on enter; Matter.js physics | 9 | the operable centrepiece — cursor drives type by distance (7 rings, `wght` 200→900, blue→red), tester sliders write the axis vars live, scroll velocity oscillates the numerals, lines rotate on a full X axis as they enter (sparingly, as punctuation). On touch: a static composed grid |
| chapters / capability | `editorial-split` (×N); `section-accent-rotation` chapters (saturated register only) | h2 `char-assemble` \| `kinetic-reveal`; prose `text-emphasis-fill` + `semantic-accent`; media `figure-hover`; scroll-driven 3D companion | 6 | each chapter shifts color temperature while a 3D companion — monster, orbital stone — follows the cursor or the scroll through them, and headings assemble on enter. Quiets after the peak, never below the floor |
| close / CTA-reprise | `close-panel`; modal CTA (Warhol's ticket); CTA reprise (Exat's "Get Exat →") | ask `kinetic-reveal`; channels `fill-invert-cta` + `masked-label-swap` + `accent-link` | 6 | one imperative and decisive channel rows; the CTA answers hover with a full flood plus inversion, "→" on the acquisition ask. No media slot, so the close cannot become a mood reel |
| footer | footer-spectacle (Eloy's clone-storm); contact-first (Cuberto); canvas word-reveal (DICH); kinetic social roll (Mat Voyce) | `cursor-spawn-trail`; clone-storm; canvas brightness reveal | 9 | a designed moment, never bare chrome — often the DEFERRED climax: the cursor spawns an image or particle trail, a hidden word reveals on hover through brightness sampling, and the loudest interaction of the page can land last |

**Footer** — designed moments, never bare chrome, and on this line frequently the deferred peak: contact reprise (Cuberto "Have an idea?" → "Tell us" + dual real addresses + index, reference-tier; Mat Voyce "CONTACT MAT" + kinetic social roll, winner-verified); acquisition reprise (Exat "Get Exat →" + credits, winner-verified); canvas word-reveal, where a hidden "DICH" surfaces on hover via brightness sampling (DICH, winner-verified); cursor image-trail finale (Warhol, winner-verified); or spectacle — the Buttons-row clone-storm, spent once on the connect CTA (Eloy, winner-verified). Ponpon keeps legal chrome minimal on a `bare-cue`.

**Arrival** — same law as the Loader row above: no decorative counter+curtain. Families (`ingredients/preloaders.md`): none/instant — the glyph grid IS the intro (Exat, technique); narrative scene-one — "read now" hands the live cover into the reader (Ponpon, winner-verified; library id `narrative-scene-one-loader`); mood gate — an After Effects → Lottie animation sets the temperature before chapter one (DICH, winner-verified); progress-becomes-UI — the bar scales down and becomes the navbar (Eloy, Codrops-verified); "LOADING…" gate only for heavy assets (Mat Voyce, winner-verified). Cuberto ships none/instant, single-source — commit none. Routes (`ingredients/page-transitions.md`): persistent-canvas panel moves with per-transition WebGL shader mixes (Ponpon, winner-verified); morphing section transitions (21 TSI, winner-verified); wipes "like chapters" (Mat Voyce, observed). Library id: `page-transition-choreography`.

**Copy voice** — Quoted to calibrate, never to ship — imitate the specificity (the named place, the count, the refusal), never the wording. Person tracks the maker (third-person portfolio, first-person attitude, no-person product); one-clause heroes, caps labels; warm imperatives at CTAs; "→" on acquisition CTAs; refuses feature-benefit padding — the motion argues, the copy labels. Self-narration ("we craft immersive experiences") is a scored defect even under high craft.
- "Exat strikes a balance between form and function, neutrality and character." (Exat, winner-verified) — one clause does all the explaining.
- "Digital design & development agency" (Cuberto, reference-tier) — the whole pitch in four words.
- "maximalist, little monster, a latinx baddie, kitsch, brat, legibitiqua" (Eloy, shipped) — attitude list, zero credentials.
- "Hey you ✨ This site uses cookies to measure the traffic." (Cuberto, reference-tier; buttons ship lowercase "accept"/"decline") — compliance chrome stays in character.

**Imagery art direction** — the image is the treatment. Illustrated world: hand-drawn cast in WebGL panels, `#171717` base, `#FEECE3` type, panels `#7E7EFF` + `#F894C0` (Ponpon; panels shipped). Type-as-image: black on white, blue `#0000cb` → orange `#FFAE00` → red `#FF0B00` recolored by cursor proximity, not scroll (Exat, technique recolor); kinetic type in F37 Judge variable widths on cream `#FFFEF8` (Mat Voyce — design micro-details, not independently confirmed). Pop-art playground: one warm hue in tones (`#FB4E2B`) across named-icon canvases, the footer trail pushing `brightness/contrast 300%→100%` on each spawn (Warhol, winner-verified). One treatment page-wide; on the saturated register, a 2–4 hue signature on one anchor base.

**Mobile / touch** — pointer classes go dormant, press and scroll carry the load. Cursor FIELDS freeze to static composed grids (Exat is explicit: touch devices receive static grid versions); cursor TRAILS, pointer-parallax and the custom cursor chrome go dormant or hidden; DICH hides its coordinate HUD under 768px. Press-class elements answer the tap with a `90–160ms` flash floor, and the CTA fill or the hard-press offset-shadow collapse IS the tap answer — magnetic pull is a no-op. Depth that came from the pointer now comes from SCROLL, and kinetic type keeps its scroll-driven channel so the maximal floor survives touch. Swap the desktop hold-and-drag or proximity gallery for a native scroll-snap `swipe-snap-gallery` with tap-to-enlarge (the scored Mobile Excellence line). Any audio stays muted until an explicit gesture, behind a persistent toggle. The single peak degrades to a strong composed static frame, never a sub-30fps render — jurors test on real devices, and sites that break on iPhone lose immediately.

**Variation** — this section chain is one legal costume of the archetype, never THE skeleton. Structure is story-native: the body's sections derive from the universe's spine, then check against these roles for coverage — never the reverse. The axes serial winners measurably rotate between builds (21-artifact corpus, 5 studios): body content archetype and item counts, the ONE signature device (never reused across builds), the close mechanism, the hero medium, the index/HUD costume. What persists as DNA: type grammar, the motion register (the register itself, never the named reading/interaction kit — that kit is a device, rotated per build like the signature), annotation grammar as a form, engineering architecture. The same content archetype + item count + close mechanism recurring across two different-brand builds has zero winner precedent.

**Anti-signals** — page-level absences across the corpus: no card/bento-grid fold (grids are proof, never the hero); no decorative `0→100` counter+curtain; no photographic hero on a type portfolio; the nav never solidifies to an opaque bar with a brand-colored border-bottom (Ponpon stays transparent after scroll, winner-verified); no functional-chrome footer; no feature-benefit paragraphs — copy is labels plus one imperative.

## Spectacle menu

*Chaptered reader* (Ponpon, winner-verified engine): "read now" → camera pans, physics shoves, pagination → a comic you operate; scroll is a playhead, replays differ. *Proximity grid* (Exat, winner-verified): lines enter on a full X-axis rotation, glyphs react by distance rings → the specimen performs itself. *Pop-art canvases* (Warhol, winner-verified): each named section reacts to the cursor in its own dialect — Elvis maps cursor-x to `font-size` `1.375→2.875em` (`power3.out 0.3s`, return `0.4s`) — closing on a footer image-trail. *Sensory chapters* (DICH, winner-verified): a mood-gate preloader hands into color-temperature chapters carried by a 3D monster following the cursor and a scroll-driven orbital stone. *Clone-storm* (Eloy, winner-verified): hover the closing connect-CTA → duplicates swarm, collide through `difference` → spent once, at the page close.

**The hero beat.** The hero fires the first-impression spectacle hard — the verdict forms in ~50ms and halos the rest of the score — and it renders the thread as reusable motion vocabulary rather than a one-off flourish. `chapter-world`: the cover IS scene one, live physics plus the character intro under the wordmark. `specimen-tour`: the cursor-proximity glyph grid itself, opening the mechanic the mid-page climax amplifies. `argument-scroll`: a declarative pitch statement whose CTA answers the pointer with the full flood. Playground variant: the SplitText wordmark on its tone array, post-preloader, or the mood-gate handing into color-chapter one. On this line, though, the hero is not necessarily where the single peak sits.

**The continuation beats** — the page is diffed against these, section by section.
- *named / color chapters* — NEVER SILENT: every section moves on page-wide scroll reveals (per-char rotation entrances, mask-fill words on `scrub:1`) with one or two section-local cursor channels on top (Warhol, winner-verified).
- *persistent chrome* — ALWAYS-ON: a coordinate HUD on rAF, a scramble section-nav, three cursor-trail variants swapped by section, a 3D companion, a 40s marquee frame (DICH, winner-verified). Input, scroll and idle channels, all sections, all the way down.
- *operable chapters* — REPEATING SAME-MECHANIC PEAKS: cover physics → chapter-select drag/scroll/snap → panel scenes (`elastic.out`, `i*1.6` stagger, 1–2 random flashes) → About on a scroll-driven WebGL camera with `velocity*0.01` feedback and kinetic type reversing on scroll-back (Ponpon, winner-verified).
- *specimen sections* — CONTINUES OPERABLE: design-space hover-morph interpolating weights and widths live, scroll-stacked panels with sine-wave numerals reading scroll SPEED, 3D X-axis line entrances deployed sparingly as punctuation (Exat, winner-verified).
- *prose zone* — TWO ENGINES: fire-once content reveals `{once:true}` PLUS a scrubbed décor channel `{scrub:true}` running underneath the whole zone (Cuberto, reference-tier).
- *route transition* (multi-view only) — CROSS-VIEW CARRIER: outgoing and incoming scenes blended through a custom shader mix driven by a GSAP tween, or a morphing curtain; peak-adjacent, and it counts as one channel in the floor.
- *footer* — FREQUENTLY THE DEFERRED PEAK: the connect-CTA clone-storm, the canvas word-reveal, the cursor image-trail. The loudest interaction is allowed to land last.

**The peak law** — verdict REFINED, from the winner evidence. Fire ONE signature spectacle and place it where the payoff logic wants it: the hero for first-impression-led builds (Ponpon's cover, Warhol's wordmark), freely mid-page (Exat's specimen grid, Cuberto's featured projects ~30% down), or at the close (Eloy's connect-CTA clone-storm) when the narrative earns it — the hero fires hard regardless, because of the ~50ms verdict and its halo. Then never fall below the maximal floor: 4–5 continuous channels — per-element-class hover states, one display-type effect, one cursor field OR trail, one idle channel, one scroll texture — all bound to ONE easing family, ONE color rule and ONE loud/quiet hierarchy per element class, so density reads as choreography and not noise. The peak re-fires the SAME mechanic amplified; it never introduces a competing second spectacle. Every non-peak section runs at least 2 channels and at most one fewer than the peak; no section runs zero. On multi-route builds the page transition counts as one of those channels. Under reduced-motion the peak degrades to a strong static composed frame while the transform/opacity/scroll channels stay alive; on touch, cursor fields freeze to static grids.

Evidence: the peak-count cap is SUPPORTED as an observation — across the verified corpus no winner stacks a second spectacle equal to its signature moment; Exat deploys the 3D line-rotation "sparingly to punctuate", Ponpon reserves color for key moments, Cuberto has one featured-projects proof peak. "One wow then quiet" is REFUTED outright: zero bold-maximal winners go silent after the hero — Warhol moves every section through page-wide scroll reveals and mask-fill, DICH runs HUD plus trail plus 3D companion plus color rotation continuously, Ponpon's physics is live from cover to About close. A quiet section here betrays the maximalist premise itself. Two archetype-specific refinements follow: the single peak is NOT hero-bound (Exat mid-page, Eloy at the close, Cuberto ~30% down), and the continuation floor runs dense-but-graded, sitting just below the peak rather than at the micro level editorial and B2B lines hold. Ponpon is the boundary case that most stresses the cap — like Bruno Simon's driving, its chaptered scenes read as near-equal repeating peaks; the cap holds only because each scene re-fires the SAME mechanic rather than introducing a new competing spectacle. The law is a synthesized design heuristic: the peak-count cap is a corpus observation, the 4–5 channel count and the floor's ranking against other archetypes are extrapolations, not measurements against a scored juror rubric.

## Component index

Generated from `assets/components/manifest.json` — the authority for slots, variants, tokens, deps and `init` signatures, and the only place 11 of the 103 components record facts their file headers omit. Each row is the id plus the opening of its `whenToUse`, clipped: enough to pick, never enough to build. Grep the manifest for the chosen id to get its contract. Forms are the page skeletons (CSS, slots, variants); components are the behaviours that mount into their slots.

**Forms** (10) — page skeletons
- `bare-cue` — The gallery-stack's minimal close (Contassot / Vitasovic): no footer chrome, just a back-to-top cue ('SCROLL UP') and a year/edition mark on one slim baseline…
- `card-list` — Release/journal/blog cards in a 2-3 column grid: media 3/2, kicker/title/date at fixed rhythm; minmax(0,1fr) columns so a long title wraps instead of blowing…
- `chapter-cover` — The cover-is-scene-one hero for chaptered story worlds: a full-viewport stage (100svh) whose ground slot is the live scene — poster plate above the…
- `chapter-select` — The record-collection chapter index: square album-cover tiles (real links) in one edge-bleed rail, native CSS scroll-snap with snap-align center (snap-to-place…
- `full-bleed-figure` — One project per viewport: full-bleed media with a corner (or centered) caption over a structural contrast scrim — the gallery-stack unit; stack several for the…
- `logo-wall` — The restrained proof strip: a static wrapped wall of height-capped, quieted logos (grayscale at rest, colour on hover — the one micro-state the form owns).
- `specimen-grid` — The specimen glyph grid that performs itself — the specimen-tour macrostructure's single peak, re-firing the hero's own mechanic amplified.
- `swipe-snap-gallery` — The mobile-first image gallery: native scroll-snap track riding OS momentum (zero JS physics), next-cell peek, enhancer-fed snap dots.
- `type-as-image` — The beats-SOTD statement band: giant display type carrying the image inside its letterforms (background-clip:text with a solid-ink @supports fallback).
- `type-tester` — The operable specimen widget — proof-by-operation: native range/select controls write the gap's own axis vars (--ff/--fs/--fw/--lh/--ls) onto the preview…

**Components** (15) — behaviours
- `cursor-proximity-typefield` — The archetype's signature operable spectacle: a grid of glyphs (the component splits) or authored word units where each unit's font-weight and color are driven…
- `cursor-spawn-trail` — The maximalist spawn channel for the section that earns it (Warhol runs it in the footer only): images (authored pool, cycled in order) or accent pixels (no…
- `custom-contextual-cursor` — The pointer chrome as a first-class element: a tight dot plus a lagging ring (lerp 0.16 — the winner's ~0.1-0.2 window) that morphs by context — grows +…
- `fill-invert-cta` — The universal primary-CTA move: full-token flood + label inversion on hover/focus — fill (direct pole swap) or wipe (a panel rises from the bottom edge).
- `glitch-type` — The RGB channel-split display heading — token-clean ghost clones clip-jitter in 600ms BURSTS every 5-9s (never continuous; bursts are punctuation), IO- and…
- `hard-press-button` — The physical press: hard offset shadow that lifts on hover and collapses on press — 125ms linear, a mechanism not a gesture.
- `kinetic-splittext-maximal` — The characterful display-type entrance, distinct from the tier's monochrome masks (kinetic-reveal, char-assemble): mode 'scale' = Warhol's per-char scale on…
- `magnetic-cursor` — Earned custom cursor that does real work: magnetic snap to [data-ad-magnetic].
- `narrative-scene-one-loader` — The chapter-world arrival: NOT an overlay gate — the visitor lands ON scene one.
- `page-transition-choreography` — The between-view spectacle channel for multi-route maximal builds (peak-adjacent — count it in the momentum floor): go(fn) runs the route/view swap inside one…
- `pointer-parallax` — Multi-layer depth under the pointer: [data-depth] layers shift a few px at differential rates (lerp 0.1, ~20px max — depth, never drift; negative depth moves…
- `scroll-speed-oscillator` — The velocity décor channel — every other scrubbed channel binds to scroll POSITION, this one reads smoothed VELOCITY and settles to the composed rest when the…
- `section-accent-rotation` — ONLY on a saturated / warm-maximal register (never kinetic-register builds): each [data-ad-sar] section claims its accent (and optional ground temperature)…
- `sound-channel` — The opt-in audio channel + its designed mute affordance in one component: UI cues and/or an ambient bed (each a URL or a synth factory — zero bytes) behind ONE…
- `tilt-parity-figure` — The sticker sheet: children rest at alternating rotations (-2.5/2.5/-1 by parity) and straighten on hover — the brutalist figure identity, legible with no…
