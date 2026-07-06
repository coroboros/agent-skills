# Motion Palette

The codified library of proven, execution-correct motion mechanics — the recipes an award build draws from so it stops re-deriving (and re-breaking) the same interactions. Each entry is a mechanic that has shipped on a Site-of-the-Day-tier build, with the one implementation that gets it right and the gotcha that version closes. Pick from the palette, or invent a new mechanic — but an invented one earns its place only when it is grounded in a real, named reference and approved (the bespoke test in `signature-invention.md`), never conjured from nothing.

Load at Phase 3 (source the mechanics the signature and the motion model need) and Phase 4 (build under them). The palette is the *how* — correct, reusable motion; the *what* (the one bespoke signature) is still governed by `signature-invention.md`. A palette pick can carry a section's motion; the make-or-break signature is bespoke or a palette mechanic bent to this world.

## The default motion model — reversible, scroll-linked, never fire-once

The motion model is imposed, not a taste choice. **When something animates on scroll, it is tied to scroll position and reversible** — it unrolls as the page scrolls down and re-rolls as it scrolls up, replayable every pass. A fire-once reveal (an IntersectionObserver that `unobserve`s after the first intersection) is the competent default and the tell this closes: it plays once, never again, so a second pass down the page shows dead, static content that already spent its one animation.

The model is imposed; the *quantity* is governed by the archetype's restraint (`atmosphere-calibration.md` Motion dial). A Minimalist build moves little — but that little is scroll-linked and reversible, not a one-shot fade. "Animate everything" is not the rule; "when it moves, it moves with the scroll and can replay" is.

## The centerpiece — native CSS scroll-driven animation

The reversible scroll-linked mechanic is a **browser primitive, not a library**: `animation-timeline: view()` / `scroll()` + `animation-range`, with `animation: <name> linear both`. The animation's progress *is* the scroll position, so scroll-down plays it forward and scroll-up plays it backward, for free — reversible and infinitely replayable, no JS, off the main thread. For the common case this beats a GSAP `ScrollTrigger` scrub: no library weight, no rAF loop, and no scroll listener (`preflight.md` §5 bans `window.addEventListener('scroll')`; this mechanic needs none).

The canonical grammar is a three-part gate, always in this order:

```css
@supports (animation-timeline: view()) {
  @media (prefers-reduced-motion: no-preference) {
    .section {                       /* the container defines a named timeline */
      view-timeline-name: --sec;
      view-timeline-axis: block;
    }
    .section .index   { animation: rise linear both; animation-timeline: --sec; animation-range: cover 10% cover 36%; }
    .section h2       { animation: rise linear both; animation-timeline: --sec; animation-range: cover 24% cover 50%; }
    .section .summary { animation: rise linear both; animation-timeline: --sec; animation-range: cover 14% cover 42%; }
    /* an element that scrolls in later reads off its OWN view() timeline, not the section's,
       so its curtain opens as the element itself enters — not when the section fired above it */
    .section img { clip-path: inset(0 100% 0 0); animation: curtain linear both; animation-timeline: view(); animation-range: entry 35% cover 40%; }
  }
}
@keyframes rise    { from { opacity: 0; transform: translateY(1.25rem); } 20% { opacity: 1; } to { opacity: 1; transform: none; } }
@keyframes curtain { from { clip-path: inset(0 100% 0 0); } to { clip-path: inset(0); } }
```

Load-bearing details, each a real defect the naive version ships:

- **`linear` is deliberate.** The easing comes from the scroll, not a timing function — a `cubic-bezier` on a scroll-driven animation double-applies the curve and stutters.
- **`both` fill** holds the from-state before the range and the to-state after, so the element is never caught mid-keyframe outside the scrub window.
- **Stagger with `animation-range`, not delays.** Several children scrub off one shared `view-timeline-name` at offset ranges — that is how a whole section cascades on scroll with zero JS orchestration. `animation-delay` does not apply to scroll timelines.
- **`view()` vs `scroll(root block)`.** `view()` ties progress to an element entering the viewport (the common case). `scroll(root block)` ties it to absolute page-scroll distance — use it for a pin-dissolve or a hero that fades over the first `30svh`, where the trigger is "how far down the page," not "is this element visible."

## The re-arming IntersectionObserver fallback (Safari / Firefox)

`animation-timeline` ships only in Chromium. Pair *every* scroll-driven scrub with an IO fallback under `@supports not (animation-timeline: view())`, and **the fallback re-arms** — it removes its reveal attribute on exit so the animation replays on re-entry, matching the reversible spirit. A `once: true` fire-once path is reserved for the rare element that must reveal a single time (a hero wordmark); it is never the default reveal mechanism.

```js
// fallback only — Chromium runs the CSS scrub above and never reaches this
const io = new IntersectionObserver((entries) => {
  for (const e of entries) {
    if (e.isIntersecting) e.target.setAttribute('data-revealed', '');
    else e.target.removeAttribute('data-revealed');   // re-arm: replays on the next entry
  }
}, { rootMargin: '0px 0px -10% 0px' });
```

Where CSS scroll-timelines cannot express the effect (text typed character-by-character by scroll), replicate the same reversible scrub in rAF: map an element's `getBoundingClientRect().top` to a progress `p ∈ [0,1]`, write it to a CSS custom property (`--type`), and let CSS reveal each unit as `--type` passes its index — and un-write on scroll-up. Register the property with `@property … syntax:'<number>'` so it animates.

## Reduced motion — three layers, always

1. Every scroll-driven block sits inside `@media (prefers-reduced-motion: no-preference)` — reduced-motion users never get the scrub.
2. An explicit `@media (prefers-reduced-motion: reduce)` block resets each animated element to its final resting state (`clip-path: inset(0); transform: none; animation: none`) — the content is present and composed, just static.
3. Any JS scrubber early-returns on `matchMedia('(prefers-reduced-motion: reduce)').matches`.

Reduced motion strips the motion, never the content — the page reads whole either way (`ship-ready-floor.md`, `preflight.md` §8 degraded render).

## The palette — mechanics and where each lives

Each is a proven recipe; the canonical implementation lives in the named file. Pick what the world's verb calls for (`signature-invention.md`); do not run all of them.

| Mechanic | What it is | Where it fits | Canonical impl |
|---|---|---|---|
| **Reversible scroll scrub** | element state driven by scroll position, replays both ways | the default reveal for any on-scroll motion | this file |
| **Scroll-aware navbar** | fixed bar hides on scroll-down, shows on scroll-up | every build (the imposed nav) | `navigation-patterns.md` |
| **Scroll-scrubbed media** | a real video's `currentTime` (or a photo-sequence frame) driven by scroll — the product "breathes" | an immersive hero of a real product | `immersive-cinematic.md` |
| **`clip-path` curtain wipe** | an image reveals by an inset wipe, not opacity | any image reveal (imperative #4) | this file + `award-imperatives.md` #4 |
| **Cursor-reveal / blob** | a soft pointer-following mask unveils a second layer, with trailing blobs on fast movement | a playful or immersive signature (the Lando register) | `references/ingredients/` shader cheat |
| **WebGL relight / 3D object** | light rakes a real object's surface, or a modelled object turns | an object-world signature (turn / hold) | `ingredients/web3d-for-sites.md` |
| **Magnetic / fill-sweep CTA** | the primary control answers the pointer, or fills on hover within its shape | the close, at the page's register | `premium-patterns.md` §2 |

## Inventing a new mechanic

The palette is a floor, not a ceiling. A build may invent a mechanic the palette does not carry — but invention is grounded, never conjured: it derives from the world's verb (`signature-invention.md`), it is built on a real, named technique (a documented API, a shipped reference, an official skill resolved at Phase 3), and its ambition is approved before it routes through the WebGL delegation. An invented mechanic that is really a category with a new coat of paint fails the bespoke test at R1. The palette raises the floor on execution; the bespoke test decides whether the result is a signature or a dressed-up default.
