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

Light cream foundation (off-white in the `#F5F2EC` to `#FAF7F0` range) with a single 3D figure — character bust, helmet, signature object — anchored to full-bleed photography or topographic-line backgrounds. Serif wordmark sits in the corner; one saturated accent (Lando uses lime `#D2FF00`) carries the brand voice as a single CTA. Ideal for athlete and personality portfolios, single-product showcases, founder-led launches.

### Daylight automotive — Porsche / luxury hardware profile

Mid-tone backgrounds, daylight studio lighting, scroll-controlled product showcases. The hero is the object — car, watch, sneaker, flacon — rotated and lit through scroll. Cinematic camera moves over still environments rather than full-bleed video. Cartier Watches & Wonders 2025 sits at the seam between this profile and Corporate Luxury (sumptuous cream 3D pavilion, slow tasteful motion). Ideal for luxury automotive, premium hardware, watchmaking, fragrance launches.

**Fidelity governs the medium, not prestige.** "The object rotated through scroll" is a mechanic, not a mandate to hand-build 3D. Choose by honest fidelity: a modelled/DRACO `.glb` rendered to the `web3d-for-sites.md` floor (physical material, HDRI env) *or* a **scroll-scrubbed real video / turntable photo-sequence** of the actual product (the code below). For a real product with no premium 3D asset, the scrubbed real footage wins every time — real light on real glass beats a lathe-turned primitive that reads CGI. A primitive 3D shipped because it was the first idea is the fidelity trap this profile most often falls into (`signature-invention.md`).

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

## Effect palette — what this line's winners ship

Two live-CSS reads anchor this — Lando Norris (Awwwards Site of the Year 2025; OFF+BRAND) and Siena Film Foundation (Awwwards Site of the Month, March 2025 + Developer Award) — backed by case-study evidence from Lusion v3, Oryzo, Messenger, Cartier, Bruno Simon, and Active Theory. Recipes below are read from the winners' own CSS unless tagged otherwise.

**The grammar** — one scarce saturated accent means "active" on every element class (Lando lime `#D2FF00`, muted `#B2C73A` on hover; Siena holds red for the live slider state only). One named easing family carries nearly every transition — Siena `--easeOutQuint: cubic-bezier(.23,1,.32,1)`, Lando chrome `cubic-bezier(.65,.05,0,1)` at `.75s`. One gesture grammar — inversion, or reveal-from-edge — repeats while the *mechanic* differs per class. Cohesion lives in the constants; variety lives in the mechanics. Never one hover everywhere; never a different ease per element.

**Buttons / CTA**
- **Full-token flood + text inversion** — hover jumps the background to a solid, full-saturation token and flips text/icon to the contrast token; the flood is chosen per context, not global. Lando `.f1-highlight-grid:hover { background: lime; color: black }`, schedule variant floods dark-green with lime text; Siena `.all-work-cta-w:hover { background:#000; color:#fff }` at `.5s` easeOutQuint. Pick on a photographic or dark canvas that needs one decisive state (Lando, SOTY 2025; Siena, SOTM Mar 2025).
- **Already-solid CTA, motion-only hover** — ship the primary filled with the accent at rest, no color change on hover, only a press/scale/icon nudge. Lando `.btn-w` rests solid `#D2FF00` / `#282C20` text / `.54rem` radius with no `:hover` color rule (transform observed, implementation unverified). The strongest antidote to the pale-tint reflex — the button is already the loudest object (Lando, SOTY 2025).
- **Masked label swap** — duplicate the label in an `overflow:clip` box; hover translates the pair so a fresh copy slides in. Siena `[data-btn=explore]` swaps `translateY(-150%)` + `translate(100%)` at `.8s`, staggered `.1s`; Lando doubles nav-link DOM text. Pick for text CTAs where motion must not shift layout (Siena, SOTM Mar 2025; Lando, SOTY 2025).
- **Magnetic pull** — the button follows the cursor a fraction of the offset inside its bounds, snapping back on leave. Cuberto `mouse-follower` `stickDelta: 0.15` (single-source). One magnet per view, never a page of them.

**Links**
- **Adopt-the-accent recolor** — hover takes the site's one saturated accent, otherwise reserved for the CTA. Lando nav-link → `#B2C73A`, metadata → lime; Siena `.review-he` → red. The recolor reads as "alive" because that color means active everywhere else — the default for text links and metadata rows (Lando, SOTY 2025; Siena, SOTM Mar 2025).
- **Plain underline, supporting only** — animated underline-draw is absent here: Lando rich-text links use a bare `text-decoration: underline`, Siena footer links reveal via `opacity` + an arrow rotate `-135deg`. Kinetic underline belongs to editorial; use it sparingly inside body copy.

**Figures / cards**
- **Inner scale 1.1** — the image scales to `1.1` inside a fixed frame that clips the overflow. Lando `.helmet-grid-item:hover img`; Siena `.previousnext-item:hover .full-img-w`. Amplitude is 10%, never a dead `1.03` — the default media hover (Lando, SOTY 2025; Siena, SOTM Mar 2025).
- **Clip-path ellipse uncover** — a top-anchored elliptical mask grows to reveal media: `clip-path: ellipse(100% 120% at 50% 0%)`. The same `… at 50% 0` geometry recurs across Lando's scroll reveals, making it a whole-site shape motif (single-source for the hover trigger). Pick when the reveal itself must carry brand shape — visor curve, lens (Lando, SOTY 2025).
- **Edge-anchored panel wipe** — a real color panel wipes in via `transform: scaleY(0→1)` from an edge, full-opacity and directional. Siena `[data-hover=bggrow]:hover:before` (single-source). The honest fill — targeted, not a fade (Siena, SOTM Mar 2025).

**Nav** — `position: fixed`, `background: transparent`, no `backdrop-filter`, `border-bottom: 0 none`. The text/icon color transitions to stay legible over whatever section scrolls under it (Lando `color .75s cubic-bezier(.65,.05,0,1)`); verified on both. Winners never hang a border-bottom of any color, nor flood a frosted panel on scroll — reserve a solid nav for the corporate/SaaS archetypes (Lando, SOTY 2025; Siena, SOTM Mar 2025).

**Text**
- **Variable-font axis animation** — display type animates `font-variation-settings` (weight/width), so letters thicken and widen in place. Lando `.text-nav-link` transitions `"wght" 660, "wdth" 93` at `5.25rem` (single-source, strong signature). The hero's one signature type move — it reads bespoke because almost nobody ships it (Lando, SOTY 2025).
- **Masked line reveal** — lines sit in `overflow: clip` boxes and translate in from below, a hard mask edge with no fade. The default headline entrance, cleaner than a per-char fade (Lando & Siena).
- **Kinetic type as image** — letters scale, split, and morph on scroll; type *is* the hero, not a caption over one. The highest-leverage move for beating Site-of-the-Day when there is no photographic hero (Obys "Typography Principles", Awwwards SOTD; Shopify Editions, SOTD).

**Cursor** — keep the OS cursor by default: the two deepest-evidence winners ship no `cursor: none` and no follower. A custom cursor must be earned by a mechanic. When justified, Cuberto `mouse-follower` state-morphing — `speed: 0.55`, `ease: "expo.out"`, `stickDelta: 0.15`, states `-hidden/-pointer/-text/-icon/-media` (Lando, SOTY 2025; Siena, SOTM Mar 2025).

**Loader / intro**
- **Brand-object assembly → reveal wipe** — the preloader builds the signature object (helmet, wordmark) while assets stream, then clip-reveals into the live hero via the top-anchored `ellipse(… at 50% 0)` hand-off mask so there is no cut. Lando Rive + GSAP intro (choreography observed, implementation unverified). Pick when the brand has one iconic object (Lando, SOTY 2025).
- **Progress-as-narrative** — the load percentage drives a real visual (a value counting, a scene lightening, a camera pulling back) so the counter is diegetic. Active Theory boots into a full-screen WebGL intro that dissolves into navigation (numeric choreography observed, implementation unverified). Pick for shader-heavy sites where the wait is unavoidable — make it the opening shot (Active Theory, Awwwards SOTD).

**Anti-signals** — absent from every winner examined: a pale/low-opacity tint fill on a primary control (`background: rgba(accent, .1)`) — winners flood full-token + invert or ship already solid, zero pale tints found; a frosted-glass nav on scroll (`backdrop-filter: blur()` + tinted panel) and a nav `border-bottom` of any color (`border-bottom: 0 none` verified on both); one universal hover for every element class (winners differentiate button ≠ card ≠ image ≠ link ≠ nav); imperceptible hover amplitude (`scale 1.02–1.03`) and a bare spinner or naked % counter that hard-cuts to the page; a different easing per element — everything routes through 2–3 named beziers.
