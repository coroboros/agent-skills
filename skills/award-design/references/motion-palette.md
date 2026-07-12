# Motion Palette

The codified library of proven, execution-correct motion mechanics — the recipes an award build draws from so it stops re-deriving (and re-breaking) the same interactions. Each entry is a mechanic proven in production, with the one implementation that gets it right and the gotcha that version closes. The palette is the *how*; the *what* — the signature that carries the world — is `signature-invention.md`. This file is the scroll/scene/reveal vocabulary; its two siblings complete the set — `text-effects.md` for type as a motion surface, `interaction-signatures.md` for the low-amplitude hover/pointer substrate that keeps every element alive past the hero. Pick a coherent ingredient-set across the three, or invent a mechanic, but ground it in a real reference and the story (the bespoke test), never in novelty for its own sake.

Load at Phase 3 (source the mechanics the signature and the motion model need) and Phase 4 (build under them).

## Story leads — technique serves, never substitutes

The palette is vocabulary; the story is the sentence. A build wins on **one unforgettable signature moment that serves a real world** — an atmosphere, a narrative, a soul — not on technique piled high. The award reference is blunt: *"The formula is not maximum spectacle. It is one unforgettable signature moment, executed with precision across every device, loading in under two seconds"* — *"everything else is decoration."* A jury of working designers reads hollow spectacle and AI-slop in seconds and scores it down; a WebGL scene empty of meaning wins nothing. Terminal Industries took Site of the Month on fades, `Lenis`, and type alone — restraint outperforming decoration — because the restraint served the story.

So reach for a mechanic because the world needs it, never because it impresses. We want both — real atmosphere **and** precise execution — but when they trade off, the story wins. When the world's verb is thin, no mechanic here rescues it; regenerate the concept (`signature-invention.md`), do not reach for a louder effect.

## The winning signature — one moment, medium by archetype

The signature that wins is one dominant **climax** — distributed over the page as a few section-tied echoes on a live low-amplitude substrate (`interaction-signatures.md`), never a lone hero effect on a page that dies below it. Its **medium is archetype-dependent**, and grabbing the wrong medium because it is flashy is the failure. The verified 2023–2026 winners split clean:

- **Immersive / Cinematic → 3D WebGL** is the one archetype where a heavy 3D signature is the win-condition. Verified named winners: Lando Norris (Awwwards **Site of the Year 2025**), ERA, Montfort, Oryzo, Cartier W&W, Igloo Inc, EverSwap — all **Three.js + GSAP + GLSL, frequently Lenis**. No verified winner ran OGL, React-Three-Fiber, CSS-native `animation-timeline`, or the View Transitions API as its signature medium; those are craft-layer and portability tools, not the winning-signature stack. Routes through the WebGL delegation (`ingredients/web3d-for-sites.md`).
- **The quieter archetypes win without 3D.** Minimalist on type + restraint (Terminal Industries, SOTM); Editorial on editorial craft + parallax storytelling (Siena, SOTM); Bento on tiles that demonstrate their claim (Anime.js, SOTM); Corporate Luxury on slow tasteful motion (Cartier). Their signature is the type, the restraint, the pacing — not a shader.

Per-archetype signature register and the full winner roster: `award-imperatives.md` + `exemplars.md`. This file supplies the motion vocabulary each one draws from.

## The motion model — split by what moves

Motion splits by *what* is moving, and the two halves have opposite defaults. Conflating them — making everything reversible, or everything fire-once — is the error.

- **Content-revealing motion** — a heading, paragraph, card, or content image arriving as you reach it. **Default: fire-once, then persist.** It animates in once and *stays*; scrolling back up neither re-hides nor re-plays it. This is the documented norm: Nielsen Norman Group's empirical scroll-fading study reads "Fade In Content Only Once" and measured the replaying model as a usability failure — users lose the thread and cannot find the scroll position that brings the content back, and re-hiding text harms reading. **Content that re-hides on scroll-up is the tell — not the fire-once reveal.**
- **Decorative / ambient / scrubbed motion** — parallax layers, a pinned scrubbed video or 3D scene, a curtain wipe on a *decorative* image, a progress-driven transform, ambient WebGL, a scroll-progress rail. **Default: reversible, scroll-linked** — progress welded to scroll position, plays both ways, via native `animation-timeline`. It never hides content, so the fire-once rule does not apply; here reversibility is free, correct, and alive.

The line is **content vs decoration**, not scrubbed vs triggered. A curtain wipe on a hero *photograph* is decorative (reversible fine); the same wipe on a *paragraph* is a content reveal (fire-once). The test: does scrolling back up hide something a reader wanted? If yes, persist it. The model is imposed; the *amount* of motion stays governed by the archetype's restraint (`atmosphere-calibration.md` Motion dial) — a Minimalist build moves little.

### The editorial reversible content-reveal — declared, not default

A reversible *content* reveal (copy that re-rolls on scroll-up for an alive feel) is legitimate for the Editorial and Immersive registers — but it is **opted into and declared in the DESIGN.md**, never the silent default, because it carries the NN/g cost. When taken, guard it with the **`cover`-phase range rule**: `animation-range: cover N% cover M%` — both endpoints inside the `cover` phase, so the element is fully on-screen the whole time it animates and only softens at the viewport edges, never vanishing while it is read. That rule keeps the reversible reveal from the jitter and content-hunting NN/g documents; it mitigates the cost, it does not erase it.

## Browser reality — progressive enhancement is mandatory

Native `animation-timeline` is **not Baseline** (mid-2026: Chrome/Edge since 115, Safari since 26, Firefox still flag-gated — ~85% support, a Firefox fallback tax). So the resting state is **content visible**, and motion is layered on top only inside the `@supports (animation-timeline: view())` gate. A browser without the timeline, and a reduced-motion user, both render every element fully revealed with zero extra code — because the hidden / pre-animation state is defined *only inside* the gate, never in base CSS. This single discipline is what makes every scroll mechanic below safe to ship.

Off-main-thread holds only for the compositor properties — `transform`, `opacity`, `filter`, `clip-path`. A scroll-driven animation of `width` / `top` / `height` janks like any other.

A second native primitive is emerging — **`animation-trigger`** (scroll-*triggered*, not scrubbed: a time-based animation fired when a scroll offset is crossed, `play-forwards` on activate, optional `play-backwards` on deactivate). It is the clean native way to do a fire-once content reveal *and* an opt-in reversible one — a declarative IntersectionObserver replacement. But it is Chrome-145-fresh and its cross-browser status is unsettled; treat it as the future default, not a shippable primitive yet.

## Mechanism by intent

### Decoration / scrubbed → native CSS scroll-driven (reversible, the centerpiece)

`animation-timeline: view()` / `scroll()` + `animation-range`, `animation: <name> linear both`. Progress *is* scroll position, so it plays both ways for free — no library, no rAF, no scroll listener (`preflight.md` §5 bans `window.addEventListener('scroll')`; this needs none). The right tool for anything decorative.

```css
@supports (animation-timeline: view()) {
  @media (prefers-reduced-motion: no-preference) {
    .hero-media {                     /* a decorative image — reversible is fine */
      view-timeline-name: --media; view-timeline-axis: block;
      clip-path: inset(0 100% 0 0);
      animation: curtain linear both;
      animation-timeline: --media;
      animation-range: entry 35% cover 40%;
    }
    .layer-back {                     /* parallax — transform only, off the main thread */
      animation: drift linear both; animation-timeline: scroll(root block); animation-range: 0 100%;
    }
  }
}
@keyframes curtain { from { clip-path: inset(0 100% 0 0); } to { clip-path: inset(0); } }
@keyframes drift   { to { transform: translateY(-12%); } }
```

Load-bearing details:
- **`linear` is deliberate** — the easing comes from the scroll; a `cubic-bezier` double-applies and stutters.
- **`both` fill** holds the from-state before the range and the to-state after.
- **Stagger with `animation-range`, not `animation-delay`** (delays don't apply to scroll timelines): children scrub off one shared `view-timeline-name` at offset ranges, cascading a section with zero JS.
- **`view()` vs `scroll(root block)`** — `view()` ties progress to an element's visibility (the common case); `scroll(root block)` to absolute page distance (a pin-dissolve, a hero fading over the first `30svh`, a progress rail).

### Content → fire-once, then persist

Do NOT scrub a content reveal with `animation-timeline` — bound to visibility, it re-hides on scroll-up (`view()` reverses as the element leaves). Fire it once and hold:

```css
@media (prefers-reduced-motion: no-preference) {
  .reveal { opacity: 0; transform: translateY(1.25rem); }          /* pre-state, motion-safe branch only */
  .reveal[data-shown] { opacity: 1; transform: none;
    transition: opacity .8s var(--ease), transform .8s var(--ease); }
}
```
```js
const io = new IntersectionObserver((entries) => {
  for (const e of entries) if (e.isIntersecting) {
    e.target.setAttribute('data-shown', ''); io.unobserve(e.target);   // arrives and stays
  }
}, { rootMargin: '0px 0px -10% 0px' });
```
The pre-state lives inside `prefers-reduced-motion: no-preference`, so a reduced-motion user and a no-JS load both see the content immediately. `animation-trigger: --t play-forwards` is the native replacement once it ships.

### The reversible content-reveal (editorial, declared only)

Only when the DESIGN.md declares it: the `animation-timeline` scrub above, applied to content, ranged `cover N% cover M%` (both endpoints in `cover`) so the copy never vanishes while read. The one place a content reveal is reversible — a deliberate register choice, not the default.

## Reduced motion — three layers, always

1. Every scroll-driven / pre-hidden block sits inside `@media (prefers-reduced-motion: no-preference)`.
2. An explicit `@media (prefers-reduced-motion: reduce)` block (where needed) forces the resting state.
3. Any JS scrubber early-returns on `matchMedia('(prefers-reduced-motion: reduce)').matches`.

Reduced motion strips motion, never content. WCAG 2.2.2: any autoplaying or looping motion over five seconds, shown in parallel with content (a pinned scrubbed video, an ambient loop), carries a pause / stop / hide control.

## The palette — mechanics, with an honest evidence tag

Pick what the world's verb calls for (`signature-invention.md`); do not run all of them. Each row names whether it moves **content** (fire-once) or **décor** (reversible), its stack path, and an **evidence tag**: **winner** (a named Awwwards / FWA / CSSDA site was verified shipping it), **shipped** (proven in a real premium build), or **technique** (a real, documented API with no named winner verified).

The tag measures **how proven the execution is — not whether the build wins.** Winning is the story's job: a technique-tag mechanic carrying a real world beats a winner-tag mechanic that is hollow — Terminal Industries took SOTM on humbler motion than several technique rows below. "No named winner" means *unconfirmed on a winner*, never *cannot win*, and the negative was a bounded search, not proof none exists.

| Mechanic | Moves | Reversible? | Stack path | Evidence |
|---|---|---|---|---|
| **Staggered content cascade** (heading / body / hairline rise) | content | fire-once | CSS IO-trigger → `animation-trigger` when it ships | shipped |
| **Text / heading curtain** (`clip-path: inset` wipe on copy) | content | fire-once | CSS `clip-path` + IO | shipped |
| **Kinetic SplitText climax** (char / word choreography) | content | fire-once | GSAP SplitText | technique |
| **Grayscale→colour image curtain** (wipe + late colour flood) | décor | reversible | CSS `view()` | shipped |
| **Pinned scroll-scrubbed video / sequence** (product "breathes") | décor | reversible | GSAP ScrollTrigger pin, or `scroll()` | technique |
| **Parallax depth layers** (transform-only) | décor | reversible | CSS `scroll()` / `view()` | technique |
| **Pin-dissolve / sticky-distance reveal** | décor | reversible | CSS `scroll(root block)` | shipped |
| **SVG stroke-draw** (frame draws itself) | décor | either | CSS `@property <length>` + `stroke-dashoffset` | shipped |
| **Conic-gradient border-trace** (`oklch(from … / 0)`, not `transparent`) | décor | fire-once | CSS `@property <angle>` | shipped |
| **WebGL 3D scene / transition** (interactive scene, inertial product, room-scrub) | signature | — | Three.js + GSAP + GLSL (+ Lenis) | winner — Lando (SOTY), ERA, Montfort, Oryzo, Igloo |
| **WebGL displacement / flowmap image transition** | signature | either | Three.js + custom GLSL (OGL for light builds) | technique |
| **Scroll-velocity skew / RGB-shift** | décor | reversible | Lenis velocity → transform or shader | technique |
| **Cursor-trailing mask / blob reveal** | signature | — | canvas / shader mask | technique |
| **Character-typed-by-scroll** (per-glyph `clamp`) | décor | reversible | JS-rAF `--type` + `@property <number>` | shipped |
| **View-Transition morph** (element / view) | transition | — | View Transitions API (native) | technique |

The **winner** tag is verified on named Awwwards / FWA / CSSDA pages (roster above; the immersive 3D family is the only one that carried a named winner in verification). The **shipped** rows are distilled from a real premium build (exact code in its stylesheet). The **technique** rows are documented and buildable; a build leaning on one states the evidence gap in the Phase 5 verdict and earns the moment through the story, not the novelty.

## Inventing a new mechanic

The palette is a floor, not a ceiling. A build may invent a mechanic the palette does not carry — but invention is grounded, never conjured: it derives from the world's verb (`signature-invention.md`), it is built on a real, named technique (a documented API, a shipped reference, an official skill resolved at Phase 3), and its ambition is approved before it routes through the WebGL delegation. An invented mechanic that is really a category with a new coat of paint fails the bespoke test at R1. The palette raises the floor on execution; the story decides whether the result is a signature or a dressed-up default.

## Physics of motion (technique — product-film analysis)

Distilled from frame-level analysis of studio-grade product films — how any *authored sequence* (a loader exit, a hero entrance, a spectacle beat) allocates time and weight. These rules govern authored timelines; scrubbed motion above stays welded to scroll. The premise: pixels read as objects with mass, not numbers — every easing choice answers "how heavy is this element, and how much friction does it land on?"

**Slow-Fast-Boom-Stop — the time allocation.** Even pacing is a tech demo; rhythm is narrative. An authored sequence splits its runtime:

- **Slow trigger** (~15%) — the eye's on-ramp; establish that something is about to happen.
- **First arrival** (~15%) — the opening visual lands at medium speed.
- **Fast dense middle** (~40%) — the work happens here: detail, density, control.
- **Boom** (~20%) — the one burst: the pull-back, the pop-out, the climax.
- **Stop** (~10%) — end on a hard stop with the final frame held — never a fade-out; the fade reads as indecision, the stop as a verdict.

**The easing → scenario map.** `linear` is a number; expo-out is an object.

- **Expo-out (`cubic-bezier(0.16, 1, 0.3, 1)`) — the default for reveals**: card rise-ins, panel entrances, directional fades. Fast launch, long brake — the weight tell. Plain ease-out starts too soft and stops too loose.
- **Overshoot (`cubic-bezier(0.34, 1.56, 0.64, 1)`) — toggles and arrivals**: a control that flips, a button that pops, an element announcing itself past its rest point before settling.
- **Spring — physical settles**: geometry falling into place, a card landing with follow-through. The element *lands* rather than stops. A key entrance earns the full three-beat: a small anticipation dip, the main action, a settling follow-through — action alone reads as slideware.
- **Ease-in-out — continuous symmetric motion only** (a cursor path, a camera drift); everywhere else it reads mechanical.

**The pre-beat hold.** 300–500ms of stillness before a key result lands — give the eye its reaction time. The no-pause, full-density sequence is the amateur default: the result appears and the viewer never saw it arrive. Hold on the pending state, then let the result surface.

**Focus-switch = brightness + saturation + blur together, never opacity alone.** Dimming keeps the background sharp — it never recedes. Push the non-focus layer back in real depth: drop brightness (~−50% at full focus), drop saturation (~−30%), add 4–8px of blur — the blur is the load-bearing channel. A ~150ms highlight flash on the focus target leads the eye back in.

These rules time the *inside* of a beat; the archetype's restraint dial (`atmosphere-calibration.md`) still governs how many beats the page affords.
