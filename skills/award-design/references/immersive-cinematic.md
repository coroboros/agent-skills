# Immersive / Cinematic

The visual is the medium. Full-screen video heroes, WebGL 3D environments, and scroll-controlled storytelling carry the brief. Body copy is sparse — what stays after the visit is one cinematic sequence executed with precision.

## Canonical reference — Lando Norris

**Site.** Lando Norris
**URL.** `landonorris.com`
**Award.** Awwwards Site of the Year 2025
**Studio.** OFF+BRAND

Webflow as foundation. WebGL-powered 3D — rotating helmet, full 3D scenes — combined with Rive motion graphics, GSAP scroll-driven cinematic sequences, full-bleed video, and lime-on-dark accents. The highest credential in this entire reference. Substitutable peer: Messenger at `messenger.abeto.co` (Awwwards SOTD Nov 10 2025 + Developer Award, by abeto; the old `messenger.network` host now redirects off-brand) — a Three.js miniature-planet experience, darker and moodier than Lando.

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
- **A looping video loops seamlessly, or it does not loop.** A clip set to `loop` whose last frame does not resolve into its first jump-cuts at the seam on every cycle — the reader's eye catches the stutter and the spell breaks (a 14s medusa clip hard-looping is the tell). Cut the loop point on matched motion, crossfade the seam, or boomerang it (`/video-loop` produces seamless loops); if none is possible, play once and hold the last frame, never loop a hitch. Seamlessness is Assessor-A driven judgment — watch the video through ≥2 full cycles and name the hitch or clear it, in the verdict; a self-ticked "loops cleanly" over a stuttering clip is the failure a static box cannot catch. The detector's first/last-frame ΔE is a flashlight only — it catches gross mismatches, it never clears a loop.
- **The hero frame reads as one legible idea at a glance.** Whatever the medium, a first-time viewer grasps the hero in one beat — Lando's driver-and-helmet is felt instantly; a murky, low-contrast frame the viewer must decode (dark machinery, an under-lit interior) fails the make-or-break surface however atmospheric, because a jury forms its verdict on the fold. The silhouette/legibility test (`imagery.md`) applies to the immersive hero, rendered or shot.
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

**Mid-page life** — the tier barely ships prose between hero and footer; the middle is interactive indexes, scrubbed media, and never-idle canvas, and every content row answers the cursor: schedule rows flood lime and invert their text (Lando, 8.18, winner-verified), film rows hide the bullet and fade a direct-link in at `.2s ease-out` (Siena, 7.9, winner-verified), award rows slide their text `translate3d(1.3em,0,0)` to expose the arrow (Lusion, 8.25, winner-verified). Hover on non-link text exists, sparingly, as the one accent doing the reading — a heading recolors to the site accent over `--slider-dur:.8s` easeOutQuint, a dedicated `split-rollover` chars class carries the per-char play, and `:has()` dims unhovered menu siblings to 70% (Siena, winner-verified) — never a generic effect on every block. The operable mid-scroll spectacle is a hand-scrubbed film still: `[data-videoplayer='scrub']` maps cursor x to `video.currentTime` on mousemove (Siena, winner-verified). Content reveals run `toggleActions:"play"` and persist while dozens of concurrent `scrub:` channels (29 read in Lando's shipped bundle) reverse with the wheel; the only `play none none reverse` triggers found sit on WebGL décor — the content-persists/décor-reverses law holding at the bundle level (winner-verified). Wheel smoothing is universal and the library tracks the stack — Webflow/GSAP builds ship Lenis (`html.lenis` on Lando and Siena, winner-verified) while the bespoke-WebGL studio rolls its own lerp so the scroll value drives the scene (Lusion: 38 `lerp(` calls into `scrollManager`, zero Lenis, winner-verified); an unsmoothed wheel starves every scrub channel.

**Scroll texture** — a pinned horizontal-track interlude that locks the viewport and pans sideways under vertical scroll (Lando, winner-verified), and the `ellipse(… at 50% 0)` seam recurring at section hand-offs so one brand shape carries the eye across every boundary. The design_plan names one — in a cinematic world the scroll carry is a camera move, never a fade schedule.

**Idle band** — strong, the deepest idle register of the nine lines: Rive and canvas idles keep the world alive between inputs — Lando ships 35 Rive instances plus 21 canvas loops — with ambient audio and a live status card layered over them (Lando, winner-verified). Commit several named idle channels; a cinematic page that freezes between inputs breaks the fiction.

**Anti-signals** — absent from every winner examined: a pale/low-opacity tint fill on a primary control (`background: rgba(accent, .1)`) — winners flood full-token + invert or ship already solid, zero pale tints found; a frosted-glass nav on scroll (`backdrop-filter: blur()` + tinted panel) and a nav `border-bottom` of any color (`border-bottom: 0 none` verified on both); one universal hover for every element class (winners differentiate button ≠ card ≠ image ≠ link ≠ nav); imperceptible hover amplitude (`scale 1.02–1.03`) and a bare spinner or naked % counter that hard-cuts to the page; a different easing per element — everything routes through 2–3 named beziers.

Channel calibration — this line's winners run 4–5 distinct interaction channels (per-class states, display-type effects, cursor, idle, scroll texture, replayable spectacle); the pre-emit critique's Aliveness axis reads against that band, never against bare coverage.

## Page recipe — how this line's winners build the page

Corpus — Lando Norris (SOTY 2025, live), Siena Film Foundation (SOTM Mar 2025 + Developer Award, live), Lusion v3 (SOTD Oct 2023, live), Messenger (SOTD Nov 2025, `messenger.abeto.co` — media-only), Active Theory (live chrome; copy canvas-rendered; award unverified).

**Anatomy** — *Portrait Procession* (`portrait-procession`; Lando, winner-verified; 12 sections ≈ 16.5vh): corner wordmark over a full-bleed portrait (attention) → pinned horizontal gallery (proof) → on/off split (understanding) → 3D helmet gallery (proof+spectacle, mid climax) → honours/partners (proof) → inverted valediction footer (close, second climax; bridges rest). *Gated Index* (`gated-reel`; Siena, winner-verified): splash gate (attention) → eight film cards, titles DOM-doubled ("SSaavvooyy") (proof) → thin credits (close/rest). *Studio Manifesto → Reel* (`studio-reel`; Lusion, winner-verified): statement hero over live 3D (attention) → manifesto line (understanding) → discipline-tagged 3D reel (proof) → contact footer (close). Single-scene world (Messenger, Active Theory — technique): all funnel jobs in one WebGL scene; budget-gated.

**Hero architectures** — *Corner-lockup portrait* (Lando, winner-verified): `<h1>` "Lando Norris" top-left, subhead beneath, the face fills the fold; body computes `#282C20` / `#F4F4ED`, Mona Sans Variable. Beat (seed easings, observed): Loader-row brand-object assembly → `ellipse(… at 50% 0)` wipe ~0.8–1.2s → lines `translateY` in `overflow:clip`, no fade → nav color `.75s`, all on `cubic-bezier(.65,.05,0,1)`. *Statement-over-canvas* (Lusion, winner-verified copy): we-declarative over the live scene, scroll cue; Active Theory keeps the statement in-canvas. *Costumed splash gate* (Siena, winner-verified copy): oversized vintage serif "SIENA" on pure black, one ticket-stub "ENTER →".

**Footer** — two modes, neither bare chrome. Valediction fold (Lando, winner-verified CSS): full-bleed helmet portrait, split-color "ALWAYS BRINGING THE FIGHT."; `.is-footer` computes `#F4F4ED` under a `#282C20` overlay, `#D2FF00` baseline — the close inverts the hero. Contact-first (Lusion, winner-verified): "Let's talk" + "Suite 2, 9 Marsh Street, Bristol, BS1 4AA, United Kingdom" + socials + newsletter. Thin costumed credits (Siena, shipped): "©2024. SIENA FILM FOUNDATION."

**Arrival** — Brand-object assembly → reveal wipe (Lando, the Loader row above): the curtain unmounts — no loader/preload/curtain node survives post-load (winner-verified; "intro"-named content nodes remain). Held costumed gate (Siena ticket, Active Theory audio — winner-verified): one in-character click that unlocks sound. None/instant (Lusion, winner-verified): scroll cue + scene settle (families: `ingredients/preloaders.md`). Routes (`ingredients/page-transitions.md`) rhyme with the loader — Siena card→case study via the overlay stack (single-source); Lusion card→project as WebGL cover/morph (observed).

**Copy voice** — Quoted to calibrate, never to ship — imitate the specificity (the named place, the count, the refusal), never the wording. Person tracks the subject (third-person personality, we-studio, caps catalog); label-length lines, one long declarative at most; idiomatic-warm verbs; emphatic terminal period on a fragment; refuses explanation, bullets, exclamations, hype.
- "Always bringing the fight." (winner-verified) — a fragment with a full stop carries the close.
- "Load Norris" (winner-verified) — the wait put in-brand; a pun where a spinner would sit.
- "2025 Mclaren Formula 1 Driver" (winner-verified) — [sic], the DOM lowercases the "c"; a title card, not a bio.
- "ADMIT ONE" / "004" (winner-verified) — costume lexicon plus a count.

**Imagery art direction** — Lando: tight, centered, symmetric head-and-shoulders; high-key shadowless light; neutral-warm grade on cream over a topo-contour field; register flips once — hero cream, body dark olive (winner-verified palette, shipped grade). Siena: film stills in a dark high-contrast poster grade (shipped). Lusion/Messenger/Active Theory: no photography — live-rendered 3D; Lusion is light-key on a white body, only Active Theory and Messenger run dark (winner-verified). One treatment page-wide, or none.

**Spectacle menu** — Footer valediction (Lando, shipped): scroll to base → the split headline resolves over the helmet portrait, palette flips cream→dark-olive → the opening face returns helmeted; replay = recontextualization. Ticket admission (Siena, gate winner-verified): "ENTER" → the index assembles → entry as ritual. Delivery loop (Messenger, technique): pilot the tiny planet → GPU-physics courier runs → agency; the site is the replay.

**Anti-signals** — page-level absences across the corpus: no card-grid/bento fold — the fold is a portrait, a gate, or a live scene; no hero carousel; no stock mosaic; no functional-only footer; no visible scrollbar or boxed hero (`scrollHeight ≈ vh` on three of five, winner-verified); no explanatory hero paragraph; no unmuted autoplay without a costumed gate.
