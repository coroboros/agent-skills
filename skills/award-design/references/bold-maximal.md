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

- **Display**: Monument Extended, Clash Display, Satoshi Black, Druk Wide, Reckless Variable — 100–300px+, variable weight (100→900) and width (75→150) animated through scroll
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
