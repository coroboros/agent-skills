# Immersive / Cinematic

The visual is the medium. Full-screen video heroes, WebGL 3D environments, and scroll-controlled storytelling carry the brief. Body copy is sparse — what stays after the visit is one cinematic sequence executed with precision.

## Canonical reference — Lando Norris

**Site.** Lando Norris
**URL.** `landonorris.com`
**Award.** Awwwards Site of the Year 2025
**Studio.** OFF+BRAND

Webflow as foundation. WebGL-powered 3D — rotating helmet, full 3D scenes — combined with Rive motion graphics, GSAP scroll-driven cinematic sequences, full-bleed video, and lime-on-dark accents. The highest credential in this entire reference. Substitutable peer: `messenger.network` (Awwwards Developer Site of the Year 2025) — a Three.js miniature-planet experience, darker and moodier than Lando.

## DNA — non-negotiable

- Full-viewport sections; minimal chrome, no visible scrollbars
- 3D, full-bleed video, or live-rendered canvas as the primary communicative medium — not decoration over a static layout
- Scroll progression drives narrative pacing — content unfolds, it isn't merely revealed
- One signature cinematic sequence per page, choreographed in timing, easing, and sequencing — the moment that carries the page's memory weight

The archetype keeps its identity across dark canvases, cream daylight, and twilight neutrals. Background lightness is an expression choice, not a definition.

## Common expressions

Three stacks fit the DNA. Pick the one that matches the brief, atmosphere scores, and brand voice.

### Cinematic dark — Active Theory profile

Pitch-black canvas (`#0A0A0A` to `#1A1A2E`) with oversized Monument Grotesk display in white. Neon or lime accents pop against the void; bloom and lens-flare shaders create dramatic lighting. Fog instead of textures, light instead of detail. Active Theory's signature, evolved through proprietary engines (Hydra, Aura). Ideal for gaming, premium tech launches, automotive concept reveals, music releases.

### Editorial portrait — Lando Norris profile

Light cream foundation (off-white in the `#F5F2EC` to `#FAF7F0` range) with a single 3D figure — character bust, helmet, signature object — anchored to full-bleed photography or topographic-line backgrounds. Serif wordmark sits in the corner; one saturated accent (Lando uses lime `#CCFF00`) carries the brand voice as a single CTA. Ideal for athlete and personality portfolios, single-product showcases, founder-led launches.

### Daylight automotive — Porsche / luxury hardware profile

Mid-tone backgrounds, daylight studio lighting, scroll-controlled product showcases. The hero is the object — car, watch, sneaker — rotated and lit through scroll. Cinematic camera moves over still environments rather than full-bleed video. Cartier Watches & Wonders 2025 sits at the seam between this profile and Corporate Luxury (sumptuous cream 3D pavilion, slow tasteful motion). Ideal for luxury automotive, premium hardware, watchmaking, fragrance launches.

## Typography

Display faces serve the cinematic register and shift by stack.

- **Cinematic dark**: Monument Grotesk (XXL), GT Flexa, Sharp Grotesk, Druk Wide — 80–200px, weight 700–900
- **Editorial portrait**: GT Sectra, Tiempos, Editorial New, GT Super at 60–120px paired with a clean grotesque (PP Neue Montreal, ABC Diatype) for body
- **Daylight automotive**: refined sans (Apercu, Founders Grotesk) at display sizes, occasional custom serif for the wordmark

Body copy stays tight at 14–18px and never competes with the visual. `mix-blend-mode: difference` overlays text on bright video. `text-shadow` glows hero copy against motion. `view-transition-name` enables thumbnail-to-hero morphs at navigation.

## Color

Background spans three families:

- **Pitch dark**: `#0A0A0A` to `#1A1A2E` — cinematic dark stack
- **Cream / off-white**: `#F5F2EC` to `#FAF7F0` — editorial portrait stack
- **Mid-tone / daylight**: warm grays in the `#9A8F7E` to `#C8B89A` range — daylight automotive stack

Text in off-white (`#E0E0E0`) on dark, off-black (`#1A1A1A`) on cream. Accents are vivid and singular — neon lime, electric cyan, single brand color used as punctuation. Effects layer through radial gradients, bloom, and lens-flare shaders. OKLCH interpolation everywhere — `linear-gradient(in oklch, …)` — to eliminate the muddy middle that kills sRGB gradients.

## Layout

Full-viewport sections pinned through scroll. Content reveals through scroll progression rather than visible chrome. Bind viewport heights to extension tokens — `heights.viewport-stable` for spacers (svh-based) and `heights.viewport-current` for fixed full-screen containers (dvh-based) per `production-hardening.md`.

```css
.cinematic-section {
  height: 100svh;
  position: sticky;
  top: 0;
}
.cinematic-fixed {
  position: fixed;
  inset: 0;
  height: 100dvh;
}
```

## Motion

Scroll-controlled storytelling is the core mechanic.

```javascript
const video = document.querySelector('video');
gsap.to(video, {
  currentTime: video.duration,
  scrollTrigger: {
    trigger: '.video-section',
    start: 'top top', end: 'bottom bottom',
    scrub: 1, pin: true
  }
});
```

`Three.js` (~150KB) for full control, `React Three Fiber` + `Drei` for React projects, `OGL` (29KB) for shader-only effects. WebGPU support became production-ready in `Three.js r171+` (September 2025) with automatic WebGL fallback — 200,000 objects at 60fps versus WebGL's 15,000.

Sound is rare and differentiating. Howler.js for management. A splash gate or persistent mute toggle is mandatory; browser autoplay policies block unmuted audio. Micro-interaction sounds stay under 0.3s; ambient at 0.05–0.15 volume. WebM/Opus first, MP3 fallback. Bruno Simon and Messenger demonstrate sound as a sensory layer rather than gimmick.

Time durations and easings consume `motion.duration-*` and `motion.ease-*` extension tokens from `DESIGN.md`. Pinned-section thresholds and fold offsets bind to `scrollTriggers.*`. See [design-system's extended-tokens reference](https://github.com/coroboros/agent-skills/blob/main/skills/design-system/references/extended-tokens.md).

## Production hardening

Every implementation in this archetype hits the iOS Safari minefield: viewport-unit traps, autoplay restrictions, scroll-restoration synthesizing events, `clientHeight = 0` on first tick, bfcache freezing animations mid-state. **Read `production-hardening.md` before writing any code in this archetype** — most rules are cross-browser, with iOS as the sharpest test case.

Performance targets are strict:

- Lazy-load videos via `requestIdleCallback`; Draco-compress 3D meshes
- Hero video under 5MB (ideally under 3MB), `ffmpeg -crf 28 -preset slow`, 8–15s loop
- All HTML video attributes (`autoplay muted loop playsinline webkit-playsinline disableRemotePlayback preload="auto" poster="…"`), MP4 source before WebM (Safari only plays MP4 and picks the first supported source)
- JS belt-and-suspenders: re-assert `video.muted = true` from script and call `play()` explicitly with `.catch(() => {})`
- `prefers-reduced-motion` swaps to static poster images
- `content-visibility: auto` on non-visible sections; progressive quality from low-poly to high

Active Theory hits LCP ~1.3s on shader-heavy sites — proof the budget holds.

## What makes it award-worthy

An immersive site scores 8+ when one signature cinematic sequence is unforgettable, mobile is reconsidered (not merely responsive), and the heavy visual stack still loads under 1.5s on mid-range devices. Cross-device parity matters here more than in any other archetype — judges check mobile first, and a desktop-only WebGL hero tanks the Usability score (30%) regardless of how impressive the canvas is.

The archetype loses identity when scroll hijacking covers for poor pacing, when the cinematic hero is the only content (no narrative beneath), or when the WebGL bundle exceeds the performance budget. Active Theory's discipline — fog instead of textures, light instead of detail — separates winners from spectacle.

## Ideal for

Automotive launches, luxury brands with a sensory story, entertainment and film, gaming, museums, athlete and personality portfolios, premium product reveals, fragrance and watchmaking microsites.

## Cross-references

Read alongside `foundations.md` (typography, OKLCH, animation toolkit), `production-hardening.md` (cross-browser shipping, iOS as canary), `audit-rubric.md` (Awwwards judging criteria), `exemplars.md` (broader visual catalog).
