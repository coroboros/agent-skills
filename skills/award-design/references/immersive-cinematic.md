# Immersive / Cinematic

The visual is the medium. Full-screen video heroes, WebGL 3D environments, and scroll-controlled storytelling carry the brief. Body copy is sparse — what stays after the visit is one cinematic sequence executed with precision.

Tier 1 (DNA, anti-signals, macrostructures, reflexes) is `references/archetype/immersive-cinematic.md`, pushed into context by `scripts/direction_roll.py`. This file is tier 2: it loads at the design_plan commit, BY HEADING, never whole.

## Contents

- [Canonical reference — Lando Norris](#canonical-reference--lando-norris)
- [DNA — non-negotiable](#dna--non-negotiable)
- [Common expressions](#common-expressions)
- [Typography](#typography) · [Color](#color) · [Layout](#layout) · [Motion](#motion)
- [Production hardening](#production-hardening) — the iOS minefield, the loop law, the legible-fold law
- [What makes it award-worthy](#what-makes-it-award-worthy) · [Ideal for](#ideal-for) · [Cross-references](#cross-references)
- [Effect palette — what this line's winners ship](#effect-palette--what-this-lines-winners-ship) — per-element-class recipes, the grammar, tap/focus/dormancy
- [Mid-page life](#mid-page-life) · [Scroll texture](#scroll-texture) · [Idle band](#idle-band) · [Channel calibration](#channel-calibration)
- [Page recipe — how this line's winners build the page](#page-recipe--how-this-lines-winners-build-the-page) — anatomy, hero, section chain, footer, arrival, copy, imagery, mobile, variation
- [Spectacle menu](#spectacle-menu) — the hero beat, the continuation beats, the peak law
- [Component index](#component-index) — the library ids this archetype reaches for

## Canonical reference — Lando Norris

**Site.** Lando Norris
**URL.** `landonorris.com`
**Award.** Awwwards SOTD 2025-11 + Site of the Year 2025 — the widely-quoted 8.18 overall and the Users' Choice sub-badge were not re-confirmed on the last verification pass; SOTD and Site of the Year are.
**Studio.** OFF+BRAND

Webflow as foundation. WebGL-powered 3D — helmet rotations in the intro plus a discrete "Helmets Hall of Fame" 3D gallery mid-page — combined with Rive motion graphics, GSAP scroll-driven cinematic sequences, full-bleed video, and lime-on-cream accents. The shape is a portrait procession: DOM sections over a recurring 3D feature, not one continuous in-engine scene tracked hero-to-footer. The highest credential in this entire reference. Substitutable peer: Messenger at `messenger.abeto.co` (Awwwards SOTD 2025-11-10, 7.92, + Developer Award 8.21 — animations 9.00, responsive 8.40, WPO 8.80; by abeto; the old `messenger.network` host now redirects off-brand) — a Three.js tiny-planet experience with WebSocket multiplayer, darker and moodier than Lando, and apparently fully in-engine with no DOM page beneath (not directly confirmed against the live build).

## DNA — non-negotiable

- Full-viewport sections; minimal chrome, no visible scrollbars
- 3D, full-bleed video, or live-rendered canvas as the primary communicative medium — not decoration over a static layout
- **The medium is rendered or scrubbed and DRIVEN, never displayed.** The "or" above carries a fidelity floor, and it is the line the archetype most often fails: the primary medium is the surface the narrative rides on and it is *driven* by the visit — a real-time scene the scroll (and, where it earns it, the pointer) moves through; a scroll-scrubbed real sequence where the scroll drives `video.currentTime`; a full-bleed cinematic video composed as the hero. What does NOT count as the primary medium: a procession of static photographs that fade in on scroll with a decorative particle canvas drifting behind and a short clip autoplay-looping in one section — that is a well-set editorial page wearing an immersive costume, the exact build that reads "aucune immersion." The test: name the surface the narrative rides on; if it is a stack of static images and the only motion is décor, the medium was never built. A live-rendered canvas counts only when it IS the world (a shader field, a 3D scene the scroll drives), not particles over a static layout.
- Scroll progression drives narrative pacing — content unfolds, it isn't merely revealed
- One signature cinematic sequence per page, choreographed in timing, easing, and sequencing — the moment that carries the page's memory weight

The archetype keeps its identity across dark canvases, cream daylight, and twilight neutrals. Background lightness is an expression choice, not a definition.

## Common expressions

Three stacks fit the DNA. Pick the one that matches the brief, atmosphere scores, and brand voice.

### Cinematic dark — Active Theory profile

Pitch-black canvas (`#0A0A0A` to `#1A1A2E`) with oversized Monument Grotesk display in white. Neon or lime accents pop against the void; bloom and lens-flare shaders create dramatic lighting. Fog instead of textures, light instead of detail. Active Theory's signature, evolved through proprietary engines (Hydra, Aura). Ideal for gaming, premium tech launches, automotive concept reveals, music releases.

### Editorial portrait — Lando Norris profile

Light cream foundation (off-white in the `#F5F2EC` to `#FAF7F0` range) with a single 3D figure — character bust, helmet, signature object — anchored to full-bleed photography or topographic-line backgrounds. Serif wordmark sits in the corner; one saturated accent (Lando uses lime `#D2FF00`, publicly corroborated) carries the brand voice as a single CTA. Ideal for athlete and personality portfolios, single-product showcases, founder-led launches.

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

`Three.js` (~150KB) for full control, `React Three Fiber` + `Drei` for React projects, `OGL` (29KB) for shader-only effects. WebGPU support became production-ready in `Three.js r171+` (September 2025) with automatic WebGL fallback — 200,000 objects at 60fps versus WebGL's 15,000. IVRESS ships the two-backend path at the tier: a `WebGPURenderer` scene with WebGL fallback, shaders authored once in TSL and compiled to both (FWA Site of the Month May 2026 + CSS Design Awards; Utsubo, case-study-verified).

Sound is rare and differentiating. Howler.js or the Web Audio API for management. A splash gate or persistent mute toggle is mandatory; browser autoplay policies block unmuted audio. Micro-interaction sounds stay under 0.3s; ambient at 0.05–0.15 volume. WebM/Opus first, MP3 fallback. Bruno Simon and Messenger demonstrate sound as a sensory layer rather than gimmick, and Cartier proves it can be narrative: a bespoke Mooders soundscape threads all six rooms unbroken (case-study-verified).

Time durations and easings consume `motion.duration-*` and `motion.ease-*` extension tokens from `DESIGN.md`. Pinned-section thresholds and fold offsets bind to `scrollTriggers.*`. See [design-system's extended-tokens reference](https://github.com/coroboros/agent-skills/blob/main/skills/design-system/references/extended-tokens.md).

## Production hardening

Every implementation in this archetype hits the iOS Safari minefield: viewport-unit traps, autoplay restrictions, scroll-restoration synthesizing events, `clientHeight = 0` on first tick, bfcache freezing animations mid-state. **Read `production-hardening.md` before writing any code in this archetype** — most rules are cross-browser, with iOS as the sharpest test case.

Performance targets are strict:

- Lazy-load videos via `requestIdleCallback`; Draco-compress 3D meshes
- Hero video under 5MB (ideally under 3MB), `ffmpeg -crf 28 -preset slow`, 8–15s loop
- **A looping video loops seamlessly, or it does not loop.** A clip set to `loop` whose last frame does not resolve into its first jump-cuts at the seam on every cycle — the reader's eye catches the stutter and the spell breaks (a 14s medusa clip hard-looping is the tell). Cut the loop point on matched motion, crossfade the seam, or boomerang it (`/video-loop` produces seamless loops); if none is possible, play once and hold the last frame, never loop a hitch. Seamlessness is the reviewer's driven judgment — watch the video through ≥2 full cycles and name the hitch or clear it, in the verdict; a self-ticked "loops cleanly" over a stuttering clip is the failure a static box cannot catch. The detector's first/last-frame ΔE is a flashlight only — it catches gross mismatches, it never clears a loop.
- **The hero frame reads as one legible idea at a glance.** Whatever the medium, a first-time viewer grasps the hero in one beat — Lando's driver-and-helmet is felt instantly; a murky, low-contrast frame the viewer must decode (dark machinery, an under-lit interior) fails the make-or-break surface however atmospheric, because a jury forms its verdict on the fold. The silhouette/legibility test (`imagery.md`) applies to the immersive hero, rendered or shot.
- All HTML video attributes (`autoplay muted loop playsinline webkit-playsinline disableRemotePlayback preload="auto" poster="…"`), MP4 source before WebM (Safari only plays MP4 and picks the first supported source)
- JS belt-and-suspenders: re-assert `video.muted = true` from script and call `play()` explicitly with `.catch(() => {})`
- `prefers-reduced-motion` swaps to static poster images
- `content-visibility: auto` on non-visible sections; progressive quality from low-poly to high

Active Theory hits LCP ~1.3s on shader-heavy sites — proof the budget holds. Messenger holds the other end: 5.7MB init / 17.5MB max on a full Three.js world, WPO 8.80 and responsive 8.40 on its Developer Award (winner-verified scores). Weight is survivable at this tier; a dead surface is not.

## What makes it award-worthy

An immersive site scores 8+ when one signature cinematic sequence is unforgettable, mobile is reconsidered (not merely responsive), and the heavy visual stack still loads under 1.5s on mid-range devices. Cross-device parity matters here more than in any other archetype — judges check mobile first, and a desktop-only WebGL hero tanks the Usability score (30%) regardless of how impressive the canvas is.

The archetype loses identity when scroll hijacking covers for poor pacing, when the cinematic hero is the only content (no narrative beneath), or when the WebGL bundle exceeds the performance budget. Active Theory's discipline — fog instead of textures, light instead of detail — separates winners from spectacle.

## Ideal for

Automotive launches, luxury brands with a sensory story, entertainment and film, gaming, museums, athlete and personality portfolios, premium product reveals, fragrance and watchmaking microsites.

## Cross-references

Read alongside `foundations.md` (typography, OKLCH, animation toolkit), `production-hardening.md` (cross-browser shipping, iOS as canary), `web3d-for-sites.md` (the material and lighting fidelity floor), `audit-rubric.md` (Awwwards judging criteria), `exemplars.md` (broader visual catalog).

Provenance for every claim below — the researcher rounds and the fresh-context refutations that corrected them — lives in the public deep-research corpus of `github.com/coroboros/research`, under `articles/award-winning-websites-2025-2030/deep-research/`: `archetypes/immersive-cinematic.md` and `verdicts/scrub-fidelity-floor.md`, refutations folded under their `## Refuted` headings, the raw reports preserved verbatim at commit `fd5d1b6`.

## Effect palette — what this line's winners ship

Corpus — Lando Norris (Awwwards SOTD 2025-11 + Site of the Year 2025; OFF+BRAND, Webflow + WebGL + Rive), Siena Film Foundation (SOTD 2025-03-18, 7.9, + Developer Award 7.51; Niccolò Miranda / Federico Valla / G-NS Studio), Messenger (SOTD 2025-11-10, 7.92, + Developer Award 8.21 — animations 9.00, responsive 8.40, WPO 8.80; abeto), Cartier Watches & Wonders 2025 (Awwwards SOTD 7.64 + Awwwards SOTM 2025 + CSS Design Awards; Immersive Garden + 60fps, Agency of the Year 2025), Oryzo AI (Awwwards SOTM April 2026 + Developer Award 7.86 + CSSDA WOTD 2026-04-09 at judge 9.22; Lusion, vanilla Three.js), ERA (Awwwards SOTD + FWA SOTD + CSSDA SOTD, January 2025 — triple SOTD; Vide Infra, for the real-estate client Tekta), Hubtown (Awwwards SOTD June 2026; Unseen Studio), Explore Primland (SOTD 2026-02-04, 7.35, + Developer Award 7.05; Outpost, ~12,000 rendered acres), IVRESS (FWA Site of the Month May 2026 + CSS Design Awards; Utsubo), Bruno Simon Portfolio (Awwwards SOTM January 2026; Three.js + Cannon.js + spatial audio), Egg Hunt (Awwwards SOTD + Developer Award 2023, FWA of the Day, CSSDA Website of the Year 2023 nominee; Merci-Michel — pre-window, retained as the cleanest one-verb playable exemplar), Lusion v3 (SOTD Oct 2023, live), Active Theory (live chrome; copy canvas-rendered; award unverified). Lando and Siena are the CSS anchors, read rule-by-rule on an earlier pass; the rest are case-study and teardown evidence with the shipped CSS unread.

Lando's shipped-CSS specifics — the named selectors, the exact chrome bezier, `.btn-w`'s transform-on-hover, the valediction's computed cream→dark-olive flip — were not re-read on the last verification pass. The mechanics are standard-pattern and carried here as recipe; the exact values are illustrative. The lime accent `#D2FF00` is publicly corroborated. The same caveat covers hover amplitudes, durations, and easings on Oryzo, Hubtown, Primland, ERA, and IVRESS: their mechanics are named in case studies and reputable teardowns, their CSS was never read.

**The grammar** — one scarce saturated accent means "active" on every element class (Lando lime `#D2FF00`, muted `#B2C73A` on hover; Siena holds red for the live slider state only). One named easing family carries nearly every transition — Siena `--easeOutQuint: cubic-bezier(.23,1,.32,1)` (CSS-verified); Lando's chrome `cubic-bezier(.65,.05,0,1)` at `.75s` is reported, not re-read. One gesture grammar — inversion, or reveal-from-edge — repeats while the *mechanic* differs per class. Cohesion lives in the constants; variety lives in the mechanics. Never one hover everywhere; never a different ease per element. The camera is the through-line the three constants ride on: transitions between sections read as camera moves, never fades (Oryzo, Cartier, Primland — case-study-verified).

**Buttons / CTA**
- **Full-token flood + text inversion** — hover jumps the background to a solid, full-saturation token and flips text/icon to the contrast token; the flood is chosen per context, not global. Lando `.f1-highlight-grid:hover { background: lime; color: black }`, schedule variant floods dark-green with lime text; Siena `.all-work-cta-w:hover { background:#000; color:#fff }` at `.5s` easeOutQuint. Pick on a photographic or dark canvas that needs one decisive state (Lando, SOTY 2025; Siena, SOTD 2025-03).
- **Already-solid CTA, motion-only hover** — ship the primary filled with the accent at rest, no color change on hover, only a press/scale/icon nudge. Lando `.btn-w` rests solid `#D2FF00` / `#282C20` text / `.54rem` radius with no `:hover` color rule (transform observed, implementation unverified). The strongest antidote to the pale-tint reflex — the button is already the loudest object (Lando, SOTY 2025).
- **Masked label swap** — duplicate the label in an `overflow:clip` box; hover translates the pair so a fresh copy slides in. Siena `[data-btn=explore]` swaps `translateY(-150%)` + `translate(100%)` at `.8s`, staggered `.1s`; Lando doubles nav-link DOM text. Pick for text CTAs where motion must not shift layout (Siena, SOTD 2025-03; Lando, SOTY 2025).
- **Magnetic pull** — the button follows the cursor a fraction of the offset inside its bounds, snapping back on leave. Cuberto `mouse-follower` `stickDelta: 0.15` (single-source). One magnet per view, never a page of them.

**Links**
- **Adopt-the-accent recolor** — hover takes the site's one saturated accent, otherwise reserved for the CTA. Lando nav-link → `#B2C73A`, metadata → lime; Siena `.review-he` → red. The recolor reads as "alive" because that color means active everywhere else — the default for text links and metadata rows (Lando, SOTY 2025; Siena, SOTD 2025-03).
- **Plain underline, supporting only** — animated underline-draw is absent here: Lando rich-text links use a bare `text-decoration: underline`, Siena footer links reveal via `opacity` + an arrow rotate `-135deg`. Kinetic underline belongs to editorial; use it sparingly inside body copy.

**Figures / cards**
- **Inner scale 1.1** — the image scales to `1.1` inside a fixed frame that clips the overflow. Lando `.helmet-grid-item:hover img`; Siena `.previousnext-item:hover .full-img-w`. Amplitude is 10%, never a dead `1.03` — the default media hover (Lando, SOTY 2025; Siena, SOTD 2025-03).
- **Clip-path ellipse uncover** — a top-anchored elliptical mask grows to reveal media: `clip-path: ellipse(100% 120% at 50% 0%)`. The same `… at 50% 0` geometry recurs across Lando's scroll reveals, making it a whole-site shape motif (single-source for the hover trigger). Pick when the reveal itself must carry brand shape — visor curve, lens (Lando, SOTY 2025).
- **Edge-anchored panel wipe** — a real color panel wipes in via `transform: scaleY(0→1)` from an edge, full-opacity and directional. Siena `[data-hover=bggrow]:hover:before` (single-source). The honest fill — targeted, not a fade (Siena, SOTD 2025-03).

**Nav** — `position: fixed`, `background: transparent`, no `backdrop-filter`, `border-bottom: 0 none`. The text/icon color transitions to stay legible over whatever section scrolls under it (Lando `color .75s cubic-bezier(.65,.05,0,1)`); verified on both. Winners never hang a border-bottom of any color, nor flood a frosted panel on scroll — reserve a solid nav for the corporate/SaaS archetypes (Lando, SOTY 2025; Siena, SOTD 2025-03). Library id: `nav-context-ink` (section-driven ink adaptation for a fixed bar crossing dark hero → light chapter → dark close).

**Text**
- **Variable-font axis animation** — display type animates `font-variation-settings` (weight/width), so letters thicken and widen in place. Lando `.text-nav-link` transitions `"wght" 660, "wdth" 93` at `5.25rem` (single-source, strong signature). The hero's one signature type move — it reads bespoke because almost nobody ships it (Lando, SOTY 2025).
- **Masked line reveal** — lines sit in `overflow: clip` boxes and translate in from below, a hard mask edge with no fade. The default headline entrance, cleaner than a per-char fade (Lando & Siena).
- **Kinetic type as image** — letters scale, split, and morph on scroll; type *is* the hero, not a caption over one. The highest-leverage move for beating Site-of-the-Day when there is no photographic hero (Obys "Typography Principles", Awwwards SOTD; Shopify Editions, SOTD). Hubtown scatters and reforms its type across scroll-sequenced stages (case-study-verified).

**Cursor** — keep the OS cursor by default: the two deepest-evidence winners ship no `cursor: none` and no follower (CSS-verified on both). An earned custom cursor must do real work ON THE MEDIUM, not decorate it — a cursor-reactive camera giving dynamic scene angles (ERA, case-study-verified), a mouse-reveal that uncovers detail in geometry and lighting (Hubtown, case-study-verified), or magnetic snap to `[data-ad-magnetic]` (Lando via Cuberto `mouse-follower`: `speed: 0.55`, `ease: "expo.out"`, `stickDelta: 0.15`, states `-hidden/-pointer/-text/-icon/-media`; single-source). The committed pointer layer lives here — a pointer-dead hero fails. Library ids: `pointer-scene-reveal` (one pointer machine, differential lerp 0.1, streaming NDC into the delegated scene's reveal mask, spotlight, or camera offset — dormant on touch), `magnetic-cursor`.

**Loader / intro**
- **Brand-object assembly → reveal wipe** — the preloader builds the signature object (helmet, wordmark) while assets stream, then clip-reveals into the live hero via the top-anchored `ellipse(… at 50% 0)` hand-off mask so there is no cut. Lando Rive + GSAP intro (choreography observed, implementation unverified). Pick when the brand has one iconic object (Lando, SOTY 2025). Library id: `brand-object-assembly-loader`.
- **Progress-as-narrative** — the load percentage drives a real visual (a value counting, a scene lightening, a camera pulling back) so the counter is diegetic. Active Theory boots into a full-screen WebGL intro that dissolves into navigation (numeric choreography observed, implementation unverified). Pick for shader-heavy sites where the wait is unavoidable — make it the opening shot (Active Theory, Awwwards SOTD).
- **Progress tied to real asset load** — this is the most asset-heavy line of the nine, so the load screen is the first impression, not a gap before it. Progress tracks actual bytes (a Three.js `LoadingManager`-style adapter, counted assets, `document.fonts.ready`), an in-brand mark sits where a spinner would (Lando puts the wait in-brand: "Load Norris"), and the hand-off to the hero is a camera or reveal move rather than a hard cut. When a Web Audio score is used, this screen doubles as the sound-unlock gate. Library id: `branded-preloader` (Lando copy-verified; Messenger's 5.7MB init makes it structural, weight-verified).

**Element states — tap, focus, dormancy.** The pointer layer is one costume of the state; the tap and focus answers are not optional and not a degraded copy. This line adds a class the DOM canon omits — the interactive mesh inside the scene.
- **CTA** — `:active` flash 90–160ms to the solid state; on touch the press carries the whole answer because the pointer layer is dormant. `:focus-visible` mirrors hover (the flood plus the label inversion) with a visible ring.
- **Link** — accent flash on `:active` at 90–160ms; `:focus-visible` fires the accent recolor plus a ring.
- **Figure** — hover is the contained 1.1 zoom plus one companion cue (scrim lift, tint, caption rise); tap enlarges (the scored Mobile Excellence line) or surfaces the caption; `:focus-within` mirrors the cue so the hover-revealed meta is keyboard-reachable. The static hairline and caption are the complete rest look.
- **Index row** — hovered row lights an accent rule and surfaces metadata while siblings dim 45–70%, `:has()` doing the dimming. On tap the row expands or navigates, and the metadata that hover surfaces is already present in the resting DOM. `:focus-within` lights the row identically.
- **Heading** — near-zero by design. The variable-font axis move is reserved for one non-link display heading; ordinary headings carry the masked-line or per-char entrance and nothing on hover. Dormant on touch; no focus analog, and the accessible name stays clean via `aria-label` when the entrance splits chars or lines.
- **Nav** — the bar is fixed, transparent, unbordered, with the ink transitioning per section. Menu toggle answers the tap; link taps flash the accent. `:focus-visible` shows a ring, and a hidden bar stays keyboard-reachable.
- **Cursor** — the custom cursor and every pointer-camera or pointer-reveal class go native and dormant on touch; the tap is answered by the press-class element or the scene raycast, never by the cursor. No focus analog — keyboard users get the finished revealed state without the pointer choreography.
- **Scene object** — the class the DOM canon omits. On fine pointer, a ray-hit interactive mesh answers with a bounded highlight (emissive lift, thin outline, or scale ≈1.05) and the cursor adopts a pointer or grab affordance; non-interactive meshes never light. On touch the raycast fires on tap and the mesh performs its verb — dash, grab, open, drive-to — with a hit cue under 160ms. Interactive meshes reach the keyboard through a focusable DOM proxy that mirrors the raycast highlight. Library id: `raycast-object-state` (Messenger object taps, Egg Hunt click-to-dash, Bruno project objects, Cartier hidden gestures — winner-verified).

**Anti-signals** — absent from every winner examined: a pale/low-opacity tint fill on a primary control (`background: rgba(accent, .1)`) — winners flood full-token + invert or ship already solid, zero pale tints found; a frosted-glass nav on scroll (`backdrop-filter: blur()` + tinted panel) and a nav `border-bottom` of any color (`border-bottom: 0 none` verified on both); one universal hover for every element class (winners differentiate button ≠ card ≠ image ≠ link ≠ nav ≠ mesh); imperceptible hover amplitude (`scale 1.02–1.03`) and a bare spinner or naked % counter that hard-cuts to the page; a different easing per element — everything routes through 2–3 named beziers; a section whose only motion is decorative over a static base — the silence defect, the one failure this line names before all others.

## Mid-page life

The tier barely ships prose between hero and footer; the middle is interactive indexes, scrubbed media, and never-idle canvas, and every content row answers the cursor: schedule rows flood lime and invert their text (Lando, SOTY 2025, winner-verified), film rows hide the bullet and fade a direct-link in at `.2s ease-out` (Siena, 7.9, winner-verified), award rows slide their text `translate3d(1.3em,0,0)` to expose the arrow (Lusion, 8.25, winner-verified). Hover on non-link text exists, sparingly, as the one accent doing the reading — a heading recolors to the site accent over `--slider-dur:.8s` easeOutQuint, a dedicated `split-rollover` chars class carries the per-char play, and `:has()` dims unhovered menu siblings to 70% (Siena, winner-verified) — never a generic effect on every block. The operable mid-scroll spectacle is a hand-scrubbed film still: `[data-videoplayer='scrub']` maps cursor x to `video.currentTime` on mousemove (Siena, winner-verified). Content reveals run `toggleActions:"play"` and persist while dozens of concurrent `scrub:` channels reverse with the wheel; the only `play none none reverse` triggers found sit on WebGL décor — the content-persists/décor-reverses law holding at the bundle level (Lando, read in the shipped bundle on an earlier pass; the "29 channels" count is that single reading, the law is the durable finding). Wheel smoothing is universal and the library tracks the stack — Webflow/GSAP builds ship Lenis (`html.lenis` on Lando and Siena, winner-verified) while the bespoke-WebGL studio rolls its own lerp so the scroll value drives the scene (Lusion: 38 `lerp(` calls into `scrollManager`, zero Lenis, winner-verified); an unsmoothed wheel starves every scrub channel.

## Scroll texture

What carries the eye down the page: in this line the scroll carry is a camera move, never a fade schedule, and it is the spine rather than a garnish. Four verified spine mechanics, one committed per build — camera Z-dive through true depth around and into one object (Oryzo, case-study-verified; library id `scroll-camera-dive`, with `dolly-zoom` as the 2.5D cousin when the medium is a media element rather than a scene), room-to-room camera transition across discrete staged alcoves (Cartier, winner-verified; library id `rooms-procession`), continuous aerial flythrough over rendered terrain (Primland, case-study-verified), and object-track over a DOM page (Lando's helmet feature recurring across sections, SOTY-verified structure). Two texture devices ride on top: a pinned horizontal-track interlude that locks the viewport and pans sideways under vertical scroll (Lando, winner-verified), and the `ellipse(… at 50% 0)` seam recurring at section hand-offs so one brand shape carries the eye across every boundary. The design_plan names one spine — a hoped-for side effect of section reveals is not a carry.

A long scroll-jacked procession or flythrough owes the visitor orientation: a room or chapter index of real anchor links, a zero-padded scene counter, a progress rail welded to the procession span, keyboard- and skip-reachable (library id `procession-wayfinding`; evidence is inferential from Cartier's discrete six-room architecture and Primland's beat structure, MEDIUM confidence). The scroll HUD variant for a driven descent is `telemetry-readout`.

## Idle band

Strong — the deepest idle register of the nine lines. Rive and canvas idles keep the world alive between inputs on the DOM-page variant, layered under ambient audio and a live status card (Lando, SOTY 2025; the qualitative Rive-plus-canvas-plus-ambient-motion channel is supported by OFF+BRAND's own service list, the often-quoted "35 Rive instances plus 21 canvas loops" is a single live-DOM reading with no public source — illustrative, never a target). Inside a rendered world the same job falls to self-animating scene detail: ERA's particle-object traffic follows road paths between inputs, Jordan Breton's butterflies and wind, Messenger's other players drifting through the same planet (library id `in-scene-ambient-life`, IO- and visibilitychange-gated, compositor-cheap). Physics carries it for free where the medium has weight — Oryzo's inertial easing keeps the object moving between scroll ticks, so it is never static (case-study-verified).

Audio is the fourth idle channel and the one this line earns more than any other: a gated ambient bed treated as a narrative layer rather than wallpaper, unlocked by the arrival gate, held at 0.05–0.15 with stings under 0.3s, paused on `visibilitychange`, silent under `prefers-reduced-motion`. Cartier's bespoke Mooders score plays unbroken across all six rooms (case-study-verified); Primland is reported to ship ambient birdsong over its terrain (not confirmed from the shipped build). The library carries the channel under sibling archetype scopes — `sound-channel` (the gate plus its always-reachable mute affordance), `spatial-audio-world` (positional bed for a playable world), `scored-scene-procession` (the continuous score welded onto the rooms rig). Commit several named idle channels; a cinematic page that freezes between inputs breaks the fiction.

## Channel calibration

Channel calibration — this line's winners run 4–5 distinct interaction channels (per-class states, display-type effects, cursor, idle, scroll texture, replayable spectacle); the pre-emit critique's Aliveness axis reads against that band, never against bare coverage. Where the scene carries interactive meshes, the in-scene raycast state is the channel that weighs most — it is the archetype's own hover surface, and a build that ships four DOM channels over a mesh field nobody can touch has miscounted.

## Page recipe — how this line's winners build the page

Corpus — Lando Norris (SOTY 2025, live), Siena Film Foundation (SOTD 2025-03-18 + Developer Award, live), Lusion v3 (SOTD Oct 2023, live), Messenger (SOTD 2025-11-10 + Developer Award 8.21, `messenger.abeto.co` — media-only), Cartier Watches & Wonders 2025 (SOTD + SOTM 2025 + CSSDA, teardown), Oryzo AI (SOTM April 2026 + Developer Award, studio BTS blog), ERA (triple SOTD January 2025, case study), Hubtown (SOTD June 2026, case study), Explore Primland (SOTD 2026-02-04, case study), Bruno Simon (SOTM January 2026), Egg Hunt (2023, pre-window), Active Theory (live chrome; copy canvas-rendered; award unverified).

**Anatomy** — *Portrait procession* (`portrait-procession`; Lando, winner-verified; 12 sections ≈ 16.5vh): corner wordmark over a full-bleed portrait (attention) → pinned horizontal gallery (proof) → on/off split (understanding, the one rest) → live 3D helmet gallery (proof+spectacle, mid climax) → honours/partners with counter rolls (proof) → inverted valediction footer (close, second climax; bridges rest). The 3D feature recurs across DOM sections; it is not one continuously tracked scene — and it is still delegated WebGL, so this shape too requires a WebGL path. *Rooms procession* (`rooms-procession`; Cartier, winner-verified via the utsubo teardown; Hubtown adjacent): load → establishing atrium → staged alcoves, one per artifact, the camera transitioning room to room rather than the page fading (Cartier ships six, "like rooms in a museum after hours") → centerpiece room at the closest push-in (the one capped peak) → valediction as the museum lights come up. Each alcove reframes rather than repeats — one owns the lighting, one the spec detail on a `counter-odometer`, one the heritage note, one an operable still — while the rig and camera stay shared. Requires a WebGL path: the rooms rig owns the scroll→room math, the delegated scene owns rendering. Every room sits at spectacle amplitude; there is no quiet section. *Gated index* (`gated-reel`; Siena, winner-verified): splash gate (attention) → eight film cards, titles DOM-doubled ("SSaavvooyy") (proof) → thin credits (close/rest); the gate and masthead stack the attention climax up front, the filmstrip sustains, and the thin close is a designed refusal because the body already spent the spectacle. *Studio manifesto → reel* (`studio-reel`; Lusion, winner-verified): statement hero over live 3D (attention) → manifesto line (the one understanding beat) → discipline-tagged 3D reel (proof) → contact-first footer (close); intensity runs even-high, carried by the live ground — never commit the live-3D hero without a WebGL path. *Single-scene world* (`engine-world`): the engine is the page and all funnel jobs collapse into it — a camera Z-dive on one object (Oryzo, winner-verified), an aerial flythrough over real terrain (Primland, winner-verified), or free-roam under one verb (Messenger and Bruno Simon, winner-verified; Egg Hunt 2023, pre-window). Budget-gated; never commit without a WebGL path.

Route on the brief's declared inputs, never on a taste read. A single person or personality → `portrait-procession`. A single object or product → `engine-world` in its single-object-dive mode, the camera diving through Z-depth around and into it. A set of discrete artifacts — a collection, a product line, a capsule, a chaptered archive → `rooms-procession`: over `portrait-procession` when the subject is a set of objects rather than one person, over `engine-world` when the rooms are discrete staged scenes rather than one continuous space. A physical place → `engine-world` as a location flythrough. A brand idea that reduces to one verb → `engine-world` free-roam, the site as its own replay. A treated archive or festival → `gated-reel`. A studio selling the medium → `studio-reel`. Pick exactly one; never blend two arcs.

**Hero architectures** — *Corner-lockup portrait* (Lando, winner-verified): `<h1>` "Lando Norris" top-left, subhead beneath, the face fills the fold; body computes `#282C20` / `#F4F4ED`, Mona Sans Variable (values not re-read on the last pass). Beat (seed easings, observed): brand-object assembly loader → `ellipse(… at 50% 0)` wipe ~0.8–1.2s → lines `translateY` in `overflow:clip`, no fade → nav color `.75s`, all on `cubic-bezier(.65,.05,0,1)`. *Statement-over-canvas* (Lusion, winner-verified copy): we-declarative over the live scene, scroll cue; Active Theory keeps the statement in-canvas. *Costumed splash gate* (Siena, winner-verified copy): oversized vintage serif "SIENA" on pure black, one ticket-stub "ENTER →". *Pointer-armed scene* (ERA and Hubtown, case-study-verified): the fold is a live scene already answering the cursor before a single scroll — ERA's splash camera reacts to cursor movement for dynamic angles, Hubtown's mouse-reveal uncovers detail in the monolith's geometry and lighting. Whatever the architecture, the medium is armed on the fold: pointer-driven on fine pointer, scroll-armed for the spine. A pointer-dead, motion-dead WebGL hero is the archetype's first-impression defect.

**Section chain** — the role order with its intensity map and the state each section owes. Pick forms by role; never hand-write hero or section layout CSS. Where a winner's original shape fits the world better than the merged library form, author the mechanic directly at library quality — the form is the first reach, not the ceiling.

| role | form | pairs | intensity | state it owes |
|---|---|---|---|---|
| load | `branded-preloader` | wordmark `kinetic-reveal`; enter `fill-invert-cta` | 4 | progress tracks REAL asset bytes, never a fake timer; an in-brand mark sits where a spinner would; the hand-off to the hero is a camera or reveal move, not a cut; doubles as the sound-unlock gate when audio is used. A raw spinner is illegal on this line |
| hero | `hero-masthead(media:back)` · `in-engine-hero` · `gated-splash` | h1 `kinetic-reveal`; media `clip-reveal`; ground `shader-surface` or a delegated scene; enter/CTA `fill-invert-cta` | 8 | the medium is ARMED on the fold — pointer drives the camera or a reveal on fine pointer, scroll commits the spine; nav is fixed and transparent over it; a pointer-dead hero is a defect |
| continuation-spine | `scroll-camera-dive` · `rooms-procession` · `dolly-zoom` (2.5D cousin) · delegated `webgl-scene` | `smooth-scroll` (Lenis or a bespoke lerp); `in-scene-ambient-life`; `procession-wayfinding` | 8 | scroll progress maps to a camera path (position + lookAt) or a room-to-room transition, reversible and compositor-driven; ambient scene life runs between ticks; long processions expose a room index or progress rail, keyboard- and skip-reachable |
| proof / reel | `pinned-filmstrip` · `index-reel-header` + `index-list` · `full-bleed-figure` procession | media `figure-hover`; rows `index-row-hover`; caption `text-emphasis-fill`; still `scrub-film` | 7 | figure hover is the contained 1.1 zoom plus a companion cue, never a 1.02 twitch; index rows flood-and-invert or slide to expose the arrow with siblings dimmed 45–70%; the operable beat is a hand-scrubbed film still, cursor x → `video.currentTime` |
| feature / understanding (rest) | `editorial-split` · `type-as-image` | h2 `char-assemble`; prose `text-emphasis-fill`; terms `semantic-accent`; media `image-curtain` | 5 | the one rest beat — but the medium behind it still moves; the shader ground or tracked object does not park. Headings enter masked or per-char; key terms take the accent on first view |
| spectacle peak | delegated `webgl-scene` · `scroll-camera-dive` at the closest push-in | `shader-surface`; the ambient audio score as an optional narrative layer | 9 | the one mid-page maximal moment — camera closest push-in, physics release, or reveal apex. Fully driven, never a static frame. Capped at one, plus the optional close |
| close | `valediction-footer` · `close-panel` (contact-first) · in-world sign-off | wordmark `kinetic-reveal`; channels `accent-link` + `masked-label-swap` | 9 | two modes, neither bare chrome: a valediction that flips the palette once and returns the opening subject recontextualized, a contact-first close with a real address, or an in-world sign-off. Often the second capped peak |

**Footer** — two modes, neither bare chrome. Valediction fold (Lando): full-bleed helmet portrait, split-color "ALWAYS BRINGING THE FIGHT."; `.is-footer` computes `#F4F4ED` under a `#282C20` overlay with a `#D2FF00` baseline — the close inverts the hero (structure SOTY-verified; the cream→dark-olive computed values were not re-read on the last pass). The `valediction-footer` component IS the footer, and the palette flips exactly once, at the close; Cartier runs the same beat as the museum lights coming up. Contact-first (Lusion, winner-verified): "Let's talk" + "Suite 2, 9 Marsh Street, Bristol, BS1 4AA, United Kingdom" + socials + newsletter — the library has no dedicated contact-first footer form, so compose it from `close-panel`. Thin costumed credits on the `bare-cue` form (Siena, shipped): "©2024. SIENA FILM FOUNDATION."

**Arrival** — Brand-object assembly → reveal wipe (Lando, `brand-object-assembly-loader`): the object assembles, an ellipse wipe hands off, and the curtain unmounts — no loader/preload/curtain node survives post-load (winner-verified; "intro"-named content nodes remain). Asset-tracked branded load (`branded-preloader`): progress tied to real Three.js asset load, handing off to the first scene with a camera move rather than a hard cut, doubling as the Web Audio sound-unlock gate — the rooms-procession default and the answer for any multi-megabyte scene. Held costumed gate (Siena ticket, Active Theory audio — winner-verified): one in-character click that unlocks sound, with the grain grade and shader surface already running behind it, so the gate IS the arrival and no loader is needed. None/instant (Lusion, winner-verified): scroll cue + scene settle (families: `ingredients/preloaders.md`). Routes (`ingredients/page-transitions.md`) rhyme with the loader — Siena card→case study via the overlay stack (single-source); Lusion card→project as WebGL cover/morph (observed).

**Copy voice** — Quoted to calibrate, never to ship — imitate the specificity (the named place, the count, the refusal), never the wording. Person tracks the subject (third-person personality, we-studio, in-character for a world, caps catalog); label-length lines, one long declarative at most; idiomatic-warm verbs; emphatic terminal period on a fragment; refuses explanation, bullets, exclamations, hype. Title-cards, never paragraphs — the medium carries the story and the words punctuate it.
- "Always bringing the fight." (Lando, winner-verified) — a fragment with a full stop carries the close.
- "Load Norris" (Lando, winner-verified) — the wait put in-brand; a pun where a spinner would sit.
- "2025 Mclaren Formula 1 Driver" (Lando, winner-verified) — [sic], the DOM lowercases the "c"; a title card, not a bio.
- "ADMIT ONE" / "004" (Siena, winner-verified) — costume lexicon plus a count.
- "It's a small planet, but someone's gotta make the deliveries." (Messenger, winner-verified) — the world's premise in one wry line.

**Imagery art direction** — Lando: tight, centered, symmetric head-and-shoulders; high-key shadowless light; neutral-warm grade on cream over a topo-contour field; register flips once — hero cream, body dark olive (composition shipped; the computed palette values were not re-read on the last pass). Siena: film stills in a dark high-contrast poster grade (shipped). ERA: a custom shader grade over the render — noise, fisheye, chromatic aberration as one treatment (case-study-verified). Lusion/Messenger/Active Theory/Oryzo/Primland: no photography — live-rendered 3D; Lusion is light-key on a white body, only Active Theory and Messenger run dark (winner-verified). One treatment page-wide, or none.

**Mobile / touch** — reconsider, do not downgrade. Pointer-driven classes (cursor-camera, mouse-reveal, magnetic, pointer-parallax) go dormant on touch and scroll alone drives the scene: on mobile the depth and the camera move come from scroll, which is the winner convention. The WebGL medium is reconsidered, not dropped — lower poly, fewer concurrent channels, progressive quality low→high, budget under ~5MB init (Messenger ships 5.7MB init / 17.5MB max and still scores responsive 8.40 and animations 9.00, winner-verified). Press-class controls answer the tap with a 90–160ms flash floor; interactive scene meshes answer via raycast-on-tap with a hit cue under 160ms. Galleries become native scroll-snap swipe tracks with tap-to-enlarge, the scored Mobile Excellence line. Cross-device parity is weighted higher here than in any other archetype — judges check mobile first, and a desktop-only WebGL hero tanks the Usability score (30%) however impressive the canvas. `prefers-reduced-motion` swaps scrubbed media to a static poster and freezes the scene on a legible frame.

**Variation** — this section chain is one legal costume of the archetype, never THE skeleton. Structure is story-native: the body's sections derive from the universe's spine, then check against these roles for coverage — never the reverse. The axes serial winners measurably rotate between builds (21-artifact corpus, 5 studios): body content archetype and item counts, the ONE signature device (never reused across builds), the close mechanism, the hero medium, the index/HUD costume. What persists as DNA: type grammar, the motion register (the register itself, never the named reading/interaction kit — that kit is a device, rotated per build like the signature), annotation grammar as a form, engineering architecture. The same content archetype + item count + close mechanism recurring across two different-brand builds has zero winner precedent.

**Anti-signals** — page-level absences across the corpus: no card-grid/bento fold — the fold is a portrait, a gate, or a live scene; no hero carousel; no stock mosaic; no functional-only footer; no visible scrollbar or boxed hero (`scrollHeight ≈ vh` on three of five, winner-verified); no explanatory hero paragraph; no unmuted autoplay without a costumed gate; no purely static or DOM-only section, which on this line is the silence defect rather than a rest.

## Spectacle menu

*Footer valediction* (Lando, shipped): scroll to base → the split headline resolves over the helmet portrait, the palette flips once → the opening face returns helmeted; replay = recontextualization. *Ticket admission* (Siena, gate winner-verified): "ENTER" → the index assembles → entry as ritual. *Museum after hours* (Cartier, winner-verified): the camera walks room to room through six staged alcoves under an unbroken score, hidden gestures rewarding the curious. *Delivery loop* (Messenger, award winner-verified, mechanic media-only): pilot the tiny planet → GPU-physics courier runs → agency; the site is the replay.

**The hero beat.** The first viewport commits the DRIVEN MEDIUM: a real-time scene the visit moves through (Oryzo object, Cartier alcove, Hubtown monolith, Primland terrain), a scroll- or pointer-scrubbed real sequence (Siena film still), or a full-bleed cinematic composed as the fold (Lando portrait plus a live helmet feature). The commitment is legibility-in-one-beat AND aliveness-in-one-beat: the hero must read as one idea at a glance — Lando's driver-and-helmet is felt instantly — and it must already be driven, pointer-reactive or scroll-armed, because a pointer-dead, motion-dead WebGL hero is the archetype's first-impression defect (ERA's splash camera reacts to the cursor before a single scroll). The asset-heavy medium reaches the hero THROUGH a designed load state, never a raw spinner. The scrubbed-sequence route carries the sequence-fidelity floor (`imagery.md` — native resolution or nothing): every frame a distinct REAL sample (footage, render, or drawn; corpus norm 30fps extraction, 89–1,182 frames per section) delivered at ≥ device pixels on the signature surface — the one 2×-upscaled winner ever measured (OPTIKKA, 1440px frames on retina) scored 7.3, the SOTD floor, and synthetic in-betweens baked from a handful of stills have ZERO winner precedent. A live-animated full-resolution still (the Siena route) satisfies the FIDELITY floor only — it never satisfies this archetype's hero-medium verdict, which is dense and moving: on an immersive brief, stills-only material forces the re-scope conversation — the failed acquisition walk quoted back (SKILL.md, "DESIGN.md and truth") and the medium re-decided with the user back at the concept steps — never a baked-down or single-still hero.

**The continuation beats** — the page is diffed against these, section by section.
- *portrait procession* (Lando) — the 3D feature recurs across the DOM page: pinned horizontal gallery (proof, ~7) → on/off editorial split (the one rest, ~5) → live 3D helmet gallery (mid PEAK, ~9) → honours/partners with counter rolls (~6) → valediction returning the opening face helmeted (second PEAK, ~9). Rive and canvas ambient loops plus ambient audio keep the page from freezing between inputs (exact idle counts and whole-scroll helmet tracking unverified).
- *single-object dive* (Oryzo) — there is no "after": scroll IS the spectacle. The camera moves through Z-depth on the one object every section, and inertial physics keeps the object in motion between scroll ticks so it is never static. Amplitude peaks at the closest push-in and never drops to silence.
- *rooms procession* (Cartier) — every section is peak-tier: scroll transitions the camera alcove to alcove, each a fully staged 3D room, the Mooders Web Audio score playing unbroken as a narrative layer rather than wallpaper, hidden gestures keeping the pointer live throughout. No quiet section — a sustained procession of staged moments.
- *location flythrough* (Primland) — the aerial camera glides continuously over terrain as you scroll, one uninterrupted move; each beat advances camera and narrative together, atmospheric fog and terrain always moving.
- *chained scenes* (ERA) — cursor-reactive splash camera → interactive 3D map with particle traffic animating on its own between inputs → parallax light path over a starfield → camera zooming into architectural render detail on scroll. The scene is never a static backdrop.
- *playable world* (Messenger, Bruno Simon) — the continuation IS the whole page: one operable scene with ambient world life (other players, physics, drift). The visit sustains itself because there is nowhere to scroll to that leaves the medium.

**The peak law** — the "exactly one climax" law is REFUTED for this archetype and replaced by the SPECTACLE-SPINE law. One continuous driven medium spans hero → footer — the spine, driven every section by scroll (camera Z-dive, room-to-room, flythrough, object-track) and, where earned, by pointer, and alive between inputs through ambient scene life and an optional audio score. Within that spine, CAP the amplitude PEAKS at one or two: a mid-page maximal camera, physics, or reveal moment, plus an optional inverted or returning close. Peaks stay scarce. The vocabulary of continuation is NOT capped — every section keeps the medium driven. The failure mode to forbid is the reverse of the other archetypes' over-peaking: here it is SILENCE. A section where the medium goes static or purely decorative — a stack of static images fading in with a particle canvas drifting behind — is "aucune immersion", the defect. Peaks are capped; the spine is mandatory; a still section is the sin.

Evidence: Oryzo's spectacle is the continuous scroll-driven camera Z-dive on one object, with no quiet section after the hero (Lusion BTS blog: vanilla Three.js, inertial physics, Z-axis camera). Primland runs one uninterrupted scroll-driven aerial flythrough over rendered terrain for the whole page — continuation is the mechanic, not an afterthought (Outpost case study). Cartier stages six sequential 3D rooms, each at spectacle amplitude, threaded by an unbroken Mooders score: sustained multi-peak, not one-peak-then-silence (utsubo teardown). Messenger and Bruno Simon make the whole page one operable 3D scene, so there is no "after the hero" to fall quiet into (SOTD and SOTM verified; Three.js + Cannon.js). Lando, the portrait-procession variant, still reads as sectional multi-peak — a mid-page 3D helmet gallery plus a palette-returning valediction over a Rive- and canvas-animated DOM page; the never-idle instance counts and the whole-scroll tracking legs are unverified and the thesis does not rest on them. The archetype codifies the counter-law: a cinematic page that freezes between inputs breaks the fiction, so silence after the hero is the defining defect, not restraint.

## Component index

Generated from `assets/components/manifest.json` — the authority for slots, variants, tokens, deps and `init` signatures, and the only place 11 of the 103 components record facts their file headers omit. Each row is the id plus the opening of its `whenToUse`, clipped: enough to pick, never enough to build. Grep the manifest for the chosen id to get its contract. Forms are the page skeletons (CSS, slots, variants); components are the behaviours that mount into their slots.

**Forms** (7) — page skeletons
- `bare-cue` — The gallery-stack's minimal close (Contassot / Vitasovic): no footer chrome, just a back-to-top cue ('SCROLL UP') and a year/edition mark on one slim baseline…
- `full-bleed-figure` — One project per viewport: full-bleed media with a corner (or centered) caption over a structural contrast scrim — the gallery-stack unit; stack several for the…
- `hero-masthead` — The statement hero: kicker/h1/standfirst/CTA row/data-strip/media, every placement owned by the form — the builder fills slots and pairs components, never…
- `in-engine-hero` — The DOM shell for an engine-mounted hero — NOT a 3D scene: the form owns the svh stage (svh deliberately, a dvh stage re-rasterizes the engine's render target…
- `index-list` — The row-list body under index-reel-header: index/title/meta/thumb locked to one shared grid so column edges cannot drift and the meta cannot sprawl.
- `logo-wall` — The restrained proof strip: a static wrapped wall of height-capped, quieted logos (grayscale at rest, colour on hover — the one micro-state the form owns).
- `type-as-image` — The beats-SOTD statement band: giant display type carrying the image inside its letterforms (background-clip:text with a solid-ink @supports fallback).

**Components** (35) — behaviours
- `ambient-idle` — The third channel — the page breathes at rest: glow, float, shimmer, or pulse at ambient amplitude, paused off-screen and on hidden tabs.
- `brand-object-assembly-loader` — The brand object that builds itself out of the wait: authored [data-assembly-part]s travel from scatter offsets (data-part-from="dx,dy,rot", or a deterministic…
- `branded-preloader` — The immersive archetype's designed first-load state: progress tied to REAL asset loading (opts.assets counted, a Three.js LoadingManager-like { onProgress }…
- `char-assemble` — Masked per-char assemble entrance for short display headings — the richer second reveal beyond kinetic-reveal's line mask.
- `clip-reveal` — Media uncover on scroll-in: animated clip-path (inset or ellipse) with a scale settle.
- `counter-loader` — The numeric counter loader: rolls with real load progress, recolors to the accent near 100, lifts as a curtain.
- `curtain-transition` — The cover wipe that rhymes with the loader: play(fn) covers the viewport, runs the swap at full cover, wipes away.
- `dolly-zoom` — The scroll dive: a pinned full-bleed media scales toward a targeted focal point (the moon, the product, the plate) as the track scrolls — reversible…
- `drag-scrub-video` — Grab-drag over a whole video SECTION maps pointer/touch delta to currentTime — extends scrub-film's scroll/pointer-position modes with a drag verb, horizontal…
- `fill-invert-cta` — The universal primary-CTA move: full-token flood + label inversion on hover/focus — fill (direct pole swap) or wipe (a panel rises from the bottom edge).
- `focus-defocus` — Gallery spotlight: the hovered item sharpens while siblings blur and dim.
- `gated-splash` — Section form.
- `glass-card` — The spatial-organic signature surface: backdrop-blur glass with the inset highlight and concentric nested radii (Doppelrand); opaque fallback keeps text…
- `grain-grade` — Fixed film-grain + optional vignette overlay for a poster grade.
- `in-scene-ambient-life` — Self-animating life INSIDE the rendered world so the spine never freezes between inputs — the in-canvas sibling of the DOM idle channel.
- `kinetic-reveal` — Headline/statement entrance: masked line reveal, staggered.
- `magnetic-cursor` — Earned custom cursor that does real work: magnetic snap to [data-ad-magnetic].
- `masked-label-swap` — CTA/button label two-line wipe swap on hover/focus.
- `nav-context-ink` — Section-driven nav ink/theme adaptation for a fixed bar crossing dark hero → light chapter → dark close.
- `nav-hero-surface` — The SURFACE axis for a minimal PERSISTENT bar (the winner-norm nav that never hides): floats transparent over the hero, gains owned --ad-ground when the…
- `pinned-filmstrip` — Section form.
- `pointer-parallax` — Multi-layer depth under the pointer: [data-depth] layers shift a few px at differential rates (lerp 0.1, ~20px max — depth, never drift; negative depth moves…
- `pointer-scene-reveal` — The fine pointer DRIVING the scene's reveal — one pointer machine (differential lerp 0.1), two channels.
- `procession-wayfinding` — Orientation chrome for the long driven procession: a room/chapter index of REAL anchor links + a scene counter ('02 / 06', zero-padded into an authored…
- `raycast-object-state` — Per-object hover/tap/hit states for interactive meshes INSIDE a WebGL scene — the axis the DOM-element canon omits.
- `rooms-procession` — The staged-rooms spine: an ordered array of discrete 3D scenes sharing one canvas + one camera rig, scroll transitioning the camera room-to-room 'like a museum…
- `scroll-camera-dive` — The true-3D camera dive: scroll progress scrubs a real camera PATH — position + lookAt (+ optional FOV) keyframes, linearly interpolated, inertially eased so…
- `scrub-film` — A film still the visitor drives — scroll or pointer maps to video currentTime.
- `shader-surface` — The token-driven WebGL texture layer — gradient-mesh, noise-field, or pointer-ripple painted from the DESIGN.md palette.
- `show-on-scroll-up-nav` — Scroll-aware fixed nav: transparent over the hero, gains ground when the hero-bottom sentinel crosses (not a scrollY threshold), hides on scroll-down and…
- `smooth-scroll` — Smoothed-scroll foundation for scrubbed/pinned reveals.
- `split-rollover` — Nav links / short labels: per-character rollover on hover/focus, staggered.
- `telemetry-readout` — The scroll-progress HUD instrument for a driven descent/procession: builder-authored channels inside [data-ad-telemetry] — [data-tel-value] on a piecewise…
- `text-emphasis-fill` — The tier's text signature, two channels: scrub (words brighten dim-to-bright as the block traverses the viewport — reversible emphasis on always-legible copy)…
- `valediction-footer` — Section form.
