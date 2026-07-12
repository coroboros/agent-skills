# Bold / Maximal

Every viewport inch carries content, and every element earns it. Layered compositions mix photography, illustration, 3D, and kinetic typography. Color is at full saturation; type functions as art rather than communication; motion is constant and choreographed. Restraint belongs to other archetypes — here, more is more, but organized.

## Canonical reference — Ponpon Mania

**Site.** Ponpon Mania
**URL.** `ponpon-mania.com`
**Award.** Awwwards Site of the Month, October 2025 (+ Developer Award, SOTY 2025 nominee)
**Studio.** Independent project.

An interactive comic about a megalomaniac sheep DJ. Built with `WebGL`, `GSAP`, `Matter.js` physics, and `Lenis`. Every hallmark of the archetype is dialed up: oversized animated panels, kinetic illustrated typography, overlapping comic compositions, saturated multi-color palette, music-player navigation metaphor. The reference for designers who think bold means timid. Substitutable peers: `figma.com` (five brand hues rotated per section), `playstation.com` (full-spectrum prism with kinetic typography), `mailchimp.com` (Cavendish yellow with Cooper Hewitt display).

## DNA — non-negotiable

- Four to six simultaneous high-saturation colors carry the system — restraint is not the brief
- Kinetic typography functions as art, not as caption — display sizes 100–300px+, variable-font animation
- Layered composition mixes media (photography, illustration, 3D, video) with intentional overlap and z-index choreography
- Constant choreographed motion — staggered reveals, parallax depth, scroll-triggered sequences
- One signature kinetic moment per page — the hero typography reform, the panel sequence, the color-pulse on scroll — that holds the page's identity

The archetype keeps its identity across bright illustrated (Ponpon, Mailchimp), dark neon-saturated (PlayStation, Figma Config), warm pastel maximal (kids' brands, gaming-adjacent), and full-spectrum prism (rotating-per-section brand hues). Background register is an expression choice, not a definition.

## Common expressions

Three stacks fit the DNA. Pick the one matching brand personality and audience.

### Bright illustrated — Ponpon Mania profile

Saturated warm palette (orange `#F39C12`, hot pink `#E91E63`, electric purple `#9C27B0`, sun yellow `#FFC107`). Cartoon characters, illustrated panels, hand-drawn type accents. Kinetic illustrated typography with overlapping comic compositions. Music-player or comic-strip navigation metaphors. Ideal for entertainment microsites, kids and family brands, animated content showcases, interactive narratives, festival lineups.

### Dark neon-saturated — PlayStation / Figma Config profile

Dark base (`#0A0A0A`, `#1A1A2E`) with electric lime (`#CCFF00`), hot magenta (`#FF00FF`), cyan (`#00FFFF`) as primary accents. Multi-layer parallax, oversized brand colors that pop against the void. Glow effects, OKLCH multi-hue gradients. Variable font weight animation on scroll (weight 100→900). Ideal for gaming launches, tech conferences, music releases, esports brands, developer-tooling marketing.

### Full-spectrum prism — Figma / brand-rotation profile

Multiple brand hues rotated per section. Each section claims its own color world — magenta hero, orange features, lime testimonials, cyan footer. Restraint sits in the discipline of the rotation rather than the palette. Ideal for design tools, multi-product platforms, agency portfolios, brand-system showcases.

## Typography

Display faces are art objects, not labels.

- **Display**: Monument Extended, Clash Display, Satoshi Black, Druk Wide, Reckless Variable — 100–300px+, variable weight (100→900) and width (75→150) animated through scroll. Clash and Satoshi are overexposed kit picks — rotate or justify (`inspiration.md`)
- **Body**: Satoshi, PP Neue Montreal, Inter (variable) — 16–18px, weight 400, line-height 1.5
- **Kinetic**: GSAP SplitText for splitting and reforming, weight/width interpolation tied to scroll position
- **Decorative type**: hand-drawn or custom letterforms in the bright illustrated stack

Scale contrast is extreme — display at 200–300px next to body at 16px. The contrast itself signals the archetype.

## Color

Background spans three families per stack:

- **Bright illustrated**: saturated warm bases (`#FFC107` yellow, `#E91E63` pink) or off-white anchoring multi-color compositions
- **Dark neon-saturated**: pitch dark `#0A0A0A` to `#1A1A2E` with neon accents
- **Full-spectrum prism**: rotating per-section, each its own world

Four to six simultaneous high-saturation hues are the standard, never two. Each color claims a role — primary, secondary, signature accent, semantic states. OKLCH multi-hue gradients animated via `@property` replace flat sRGB.

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

Durations bind to `motion.duration-*`, easings to `motion.ease-*`. Stagger offsets bind to `motion.stagger-*` extension tokens. Scroll-pinned section thresholds bind to `scrollTriggers.*`. `Lenis` smooth scroll keeps the kinetic layer in sync with the page.

## What makes it award-worthy

A bold/maximal site scores 8+ when the saturation reads as choreography rather than chaos — when four to six colors are anchored to roles, when 200px display type is paced against scroll progression, when three layered media types coexist without competing. Ponpon succeeds because every kinetic decision serves the comic-narrative metaphor; the page is read as much as it is consumed.

The archetype loses identity when "bold" becomes color randomness, when kinetic type fires without a story, when overlapping compositions trap the eye instead of guiding it. Maximalism without choreography is noise.

## Ideal for

Creative agencies, entertainment microsites, music festivals, Gen Z brands, campaign and product launches, gaming releases, design conferences, illustrated commerce, comic-narrative microsites.

## Cross-references

Read alongside `foundations.md` (variable fonts, kinetic type, OKLCH, GSAP SplitText), `production-hardening.md` (motion of this density tests mobile performance budgets), `anti-patterns.md` (Density 6+ doesn't excuse missing accessibility — `prefers-reduced-motion` swap is mandatory), `exemplars.md` (Figma, Duolingo, Mailchimp, PlayStation).

## Effect palette — what this line's winners ship

Corpus of verified winners: Ponpon Mania (Awwwards SOTM 2025 + Developer Award), Lando Norris (SOTD 2025, 8.18), Cuberto (SOTD / Developer Award), Eloy Benoffi (Honorable Mention + GSAP SOTD + CSSDA), Mat Voyce (SOTD + FWA), 21 TSI (CSSDA + FWA), plus Maxima Therapy, Stefan Vitasović, Obys. Cuberto and Lando were read from live CSS (computed rules quoted); the rest come from Codrops case studies and Awwwards entries.

**The grammar** — Variety coheres when one shared law binds visibly different mechanics. Cuberto runs four interactions — dome fill, skewed roll, scaling underline, contextual cursor — all on one expo-out curve (`cubic-bezier(0.16,1,0.3,1)` ≈ `(0.19,1,0.22,1)`), with fills resolving to *full* role colors, never tints. Ponpon binds physics, type, scroll, and nav to one comic/music metaphor: scroll is a playhead, nav a track list. Pick one easing family (expo-out or elastic, not both) and one loud signature per element class — CTA ≠ link ≠ image ≠ nav — then run secondary elements as quieter variants. Unity is the shared curve + color rule + loud/quiet hierarchy, not a cloned hover.

**Buttons / CTA** —
- **Rising dome fill → inversion** — a pill (`border-radius: 1000px`, `overflow: hidden`) holds a fill layer parked below (`transform: translateY(101%)`, `background: currentcolor`, domed leading edge `border-radius: 50% 50% 0 0`) that rises and flattens on hover, `transition: transform 0.5s cubic-bezier(0.4,0,0,1)`; the solid variant fills with a full token (`#ce1352`, `0.5s Power3.easeOut`, retract `0.4s`) and inverts the icon. Pair it with a label swap-slide synced to the fill — rest label out (`opacity: 0, y: -20%`, `0.15s Power2.easeIn`), duplicate up (`y: 100%→0%`, `0.2s Expo.easeOut`), clipped. The curved leading edge is the signature; a flat wipe reads generic. *Primary CTA.* (Cuberto, SOTD / Developer Award).
- **Darker same-hue shift** — where a saturated button recolors, go *darker*, never paler: Stripe `#533afd → #4434d4` + `translateY(-2px)` lift; Tailwind `bg-blue-500 → hover:bg-blue-700`; Geist keeps the primary a full solid `#171717` with no wash. *Dark-neon / brand-solid builds where a directional fill is too much.* (design-system corroboration).
- **Accent-swap face** — button carries `overflow: hidden` and swaps label/nav color to the one hot hue on hover (`#D2FF00` against `#111112`). *Dark-neon builds where the accent is the whole identity.* (Lando Norris, SOTD 2025) — Rive-canvas face is observed, implementation unverified.
- **Physical clone-storm** — one hero CTA spawns duplicates as the cursor moves (two per `200px` of travel, up to `200`, `mix-blend-mode: difference`), exiting `opacity: 0, scale: 0.6, ease: 'back.in(1.7)'` on leave. *One maximalist button per page, never repeated UI.* (Eloy Benoffi, GSAP SOTD) — single-source.

**Links** —
- **Skewed text-roll** — label sits in a clipped box with a duplicate below; on hover the pair translates `-105%` while each layer resolves a `skewY(0deg) ↔ skewY(7deg)` peel, `transition: transform 1.2s cubic-bezier(0.19,1,0.22,1)`. The 7° skew lifts it above a plain vertical roll. *Overlay menu items and large nav labels.* (Cuberto, SOTD / Developer Award).
- **Scaling underline / marker draw** — a pseudo-element underline scales in `scaleX(0)→scaleX(1)`, `transition 1s cubic-bezier(0.16,1,0.3,1)`. Keep it the *quiet* treatment so the CTA fill and menu roll stay loud. *Utility and footer links.* (Cuberto, SOTD / Developer Award).

**Figures / cards** —
- **Graded / random-stagger reveal** — reveals are choreographed, not uniform: rows graded per easing (`power3.in` / `power2.in` / `power1.in`), cards scaling in steps (`1.75→1.25→1`) with `stagger: { from: 'random' }` and randomized `transform-origin`. `from: 'random'` is the maximalist tell. *Dense grids where uniform stagger feels mechanical.* (Eloy Benoffi, GSAP SOTD; Ponpon Mania, SOTM).
- **Shared DOM+WebGL scene under one scroll** — scroll drives a WebGL camera/uniforms, scroll velocity fed into depth (`z = 5 + velocity * 0.01`), reversible on scroll-back. *The one section that must feel three-dimensional — the medium that separates 8.5+ scorers; use once.* (Ponpon Mania, SOTM; Stefan Vitasović; 21 TSI, CSSDA + FWA).

**Nav** — Default is a `position: fixed` bar kept transparent through scroll — `background: rgba(0,0,0,0)`, `backdrop-filter: none`, `border-bottom: 0`, at the top *and* after scrolling — so the maximal canvas reads through; opening the menu drops a full-viewport curtain, the bar itself never solidifies (Cuberto, Lando Norris, live CSS). When a surface is genuinely needed, frost it — `background: hsl(0 0% 100% / 0.5)` + `backdrop-filter: blur(16px)`, no border or a neutral low-opacity hairline (Aqtos, Blend — blur/opacity values observed, implementation unverified) — or blend-invert with `mix-blend-mode: difference` over alternating sections (Blind Barber, single-source). Winners never solidify to an opaque bar with a contrasting brand-colored border-bottom.

**Text** — Spend one signature headline and keep the rest quiet. SplitText with a *characterful* per-unit transform: Ponpon enters lines from `x: "100%"` with `skewX: random(-25,25)`, `rotation: 5`, `ease: "elastic.out(0.7,0.7)"`, `stagger: 0.06`; Stefan splits per-character with index-scaled expo (`1.25s + index*0.025s`, `ease: easeExpOut`). Elastic camp ≠ expo camp — pick one per build. Oversized type animated beyond viewport bounds as the whole interface is signature-grade for type portfolios (Mat Voyce, SOTD + FWA — observed, implementation unverified; copy no params).

**Cursor** — The one legitimate home of the bespoke cursor is a *contextual state* cursor: one follower whose `::before` rescales and re-modes per target (`-pointer` `scale(0.3)`, `-text` `scale(0.8)`, `-lg` `scale(1.15)`; over interactive elements `×4` scale, drop to `opacity: 0.2`), driven by `mouse-follower` defaults `speed: 0.55`, `ease: 'expo.out'`, magnetic `stickDelta: 0.15` (Cuberto). The state changes carry meaning; the lag alone does not. Dropping it deliberately when the page already runs heavy WebGL/Rive motion is a real choice, not an omission (Lando Norris) — kill it on small screens either way.

**Loader / intro** — Winners split on preloader vs instant paint, but never a decorative counter+curtain over a static hero. Resolve the intro into live UI — the loading bar *becomes* the navbar (Eloy Benoffi — single-source) — or make it scene one of the narrative (Ponpon Mania, SOTM). An asset-gated `0→100` counter is legitimate only when the hero genuinely ships heavy media, and the numerals should carry the concept (`steps(n)` progression; GT America, Black Messiah, Naya). Instant first paint with no full-screen counter is defensible on editorial-leaning maximal (Locomotive, SOTM).

**Anti-signals** — Absent from every winner examined. The pale-tint fill on a primary control — no winner washes a saturated button with `hover:bg-primary/10` (the shadcn leak); that low-opacity tint is correct *only* on a ghost/outline variant that starts transparent. A solid nav bar with a contrasting brand-colored border-bottom on scroll — on no named winner. One universal hover cloned across buttons *and* links *and* cards — winners vary mechanic by element class. Fire-once uniform `IntersectionObserver` fade-up on every section — winners scrub, reverse, and grade stagger. Kinetic type with no story, the archetype's named failure mode. A lagging-dot cursor with no state, left running on mobile.

## Page recipe — how this line's winners build the page

Corpus — Ponpon Mania (SOTM Oct 2025 + Developer Award, live), Cuberto (SOTD + Developer Award, live copy), Mat Voyce (SOTD Jan 2025, live; other honors unconfirmed), Exat (SOTD Apr 2025 + CSSDA WOTM, live + Codrops; other honors unconfirmed), Eloy Benoffi (GSAP SOTD + CSSDA, live + Codrops).

**Anatomy** — *Specimen Tour* (`specimen-tour`; Exat, winner-verified nav): oversized self-naming hero (attention) → About (understanding) → type tester (understanding+proof) → one capability per section — specimen grids, design space, stylistic sets (proof, quieting) → CTA reprise + credits (close); climax at the glyph grid, rest at the close. *Agency Statement* (`argument-scroll`; Cuberto, shipped): the line's only true funnel — declarative hero (attention) → featured projects (proof, climax) → services (understanding) → blog (texture, rest) → "Have an idea?" reprise + footer (close); Eloy compresses it to one scroll. *Narrative Chapters* (`chapter-world`; Ponpon, winner-verified cover): the cover IS scene one — wordmark, "read now", chapter nav over live WebGL (attention) → chapter select (understanding) → panel scenes, camera moves, physics (proof+spectacle, climax) → About (rest/close).

**Hero architectures** — *Wordmark-as-hero* (Ponpon, winner-verified): the name is the largest object, rendered as art full-bleed; the DOM `<h1>` is a 9px credit, `#FEECE3` on `#171717`; header fixed, transparent; entrance = the Ponpon SplitText signature (Text row above). *Pitch-statement hero* (Cuberto, shipped): declarative `<h1>` + one-sentence subhead + low-key CTA, proof one scroll below. *Loader-expands-into-hero* (Eloy, technique): the fold starts scaled-down while the loading bar grows into the navbar; cards enter via the graded random-stagger reveal (Figures row above).

**Footer** — designed moments, never bare chrome: contact reprise (Cuberto "Have an idea?" → "Tell us" + dual addresses + index, shipped; Mat Voyce "CONTACT MAT" + kinetic social roll, winner-verified); acquisition reprise (Exat "Get Exat →" + credits, winner-verified); or spectacle — the Buttons-row clone-storm, spent once on the connect CTA (Eloy, technique/seed). Ponpon keeps legal chrome minimal.

**Arrival** — same law as the Loader row above — no decorative counter+curtain. Families (`ingredients/preloaders.md`): none/instant — the glyph grid IS the intro (Exat, technique); narrative scene-one — "read now" hands the cover into the reader (Ponpon, winner-verified); progress-becomes-UI — the bar becomes the navbar (Eloy, technique); "LOADING..." gate only for heavy assets (Mat Voyce, winner-verified). Routes (`ingredients/page-transitions.md`): persistent-canvas panel moves (Ponpon, shipped); wipes "like chapters" (Mat Voyce, observed); Cuberto timings unread — commit none (single-source).

**Copy voice** — Quoted to calibrate, never to ship — imitate the specificity (the named place, the count, the refusal), never the wording. Person tracks the maker (third-person portfolio, first-person attitude, no-person product); one-clause heroes, caps labels; warm imperatives at CTAs; "→" on acquisition CTAs; refuses feature-benefit padding — the motion argues, the copy labels.
- "Exat strikes a balance between form and function, neutrality and character." (winner-verified) — one clause does all the explaining.
- "Digital design & development agency" (shipped) — the whole pitch in four words.
- "maximalist, little monster, a latinx baddie, kitsch, brat, legibitiqua" (shipped) — attitude list, zero credentials.
- "Hey you ✨ This site uses cookies to measure the traffic." (winner-verified; buttons ship lowercase "accept"/"decline") — compliance chrome stays in character.

**Imagery art direction** — the image is the treatment. Illustrated world: hand-drawn cast in WebGL panels, `#171717` base, `#FEECE3` type, panels `#7E7EFF` + `#F894C0` (Ponpon; panels shipped). Type-as-image: black on white, blue `#0000cb` → orange `#FFAE00` → red `#FF0B00` recolored by cursor proximity, not scroll (Exat, technique recolor); kinetic type on cream `#FFFEF8` (Mat Voyce, winner-verified). One treatment page-wide; 2–4 hue signature on one anchor base.

**Spectacle menu** — Chaptered reader (Ponpon, winner-verified engine): "read now" → camera pans, physics shoves, pagination → a comic you operate; scroll is a playhead, replays differ. Proximity grid (Exat, technique): lines enter on a full X-axis rotation, glyphs react by distance rings → the specimen performs itself. Clone-storm (Eloy, technique/seed): hover → duplicates swarm, collide through `difference` → spent once.

**Anti-signals** — page-level absences across the corpus: no card/bento-grid fold (grids are proof, never the hero); no decorative `0→100` counter+curtain; no photographic hero on a type portfolio; the nav never solidifies to an opaque bar with a brand-colored border-bottom (Ponpon stays transparent after scroll, winner-verified); no functional-chrome footer; no feature-benefit paragraphs — copy is labels plus one imperative.
