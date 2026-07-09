# Interaction Signatures — the live substrate

The signature carries the hero; this file keeps the *rest* of the page alive. The dominant build failure it closes is the one a fresh visitor names in one breath — **the page dies after the hero**: a loud hero moment, then static editorial to the footer, every link and image and card inert. A jury reads that as a prototype with a good first slide. Load at Phase 4 alongside `motion-palette.md` and `text-effects.md`; the interaction ingredient-set is committed in the design_plan.

## Two layers — a distributed signature over a live substrate

The winning architecture is **not** one hero climax, and **not** one effect sustained unchanged across the whole scroll. Both were refuted against the award record; the strongest verified quiet/luxury winner (Cartier '365', Awwwards SOTD 7.64 + CSS Design Awards) runs a third model:

- **Layer 1 — a distributed signature.** A small set of bespoke moments, each **tied to the meaning of its own section**, over the scroll — one dominant climax (the hero, `signature-invention.md`) plus two or three quieter section-specific echoes. Cartier ships distinct per-chapter components (jewellery steps assemble on scroll; a chapter mimics a film reel; another splits and reverses its layout) — *not* one reusable effect stamped everywhere. A single generic fade-in on every element is itself an AI-slop tell (`anti-patterns.md`).
- **Layer 2 — a low-amplitude interaction substrate.** Every interactive element responds — link, image, card, control, nav — in **one coherent, quiet vocabulary applied identically everywhere**. This is the connective tissue that keeps the world breathing between the distributed moments.

*Transfer caveat:* Cartier '365' is a chaptered editorial magazine, a different archetype from a single-scroll landing page — the distributed model transfers by inference, not proof. What is proven and binding is Layer 2: the substrate is never optional.

## Restraint lowers amplitude, never coverage

The register calibrates **how much** each element moves, never **whether** it moves. A quiet build — near-white minimalist, corporate luxury — keeps **full coverage at very low amplitude**: everything responds, nothing shouts. Stillness itself is not the craft; a page that strips interaction off its elements to feel "calm" reads inert, not refined. The opposite failure is real too — a busy animation on *every* hover and scroll reads chaotic (`anti-patterns.md` UX). Restraint is the amplitude dial (`atmosphere-calibration.md` Motion), turned low; coverage stays total.

- **Minimalist** — coverage total, amplitude minimal, and **pointer/focus, not scroll-triggered** (Minimalist sits at Motion 3 — `atmosphere-calibration.md` keeps it to `transition: opacity` on hover/focus, not scroll motion): a hairline underline drawing under a link, a contained 1–2% figure lift on hover, a focus ring at t=0. Every element still responds; it just responds to the pointer, quietly.
- **Corporate Luxury** — the same coverage with a touch more licence (Motion 5): slow tasteful hover reveals, a considered cursor. No parallax pile, no cursor circus.
- **Editorial** — the substrate plus a few reading-tied text-emphasis moments (`text-effects.md`).
- **Immersive / Bold / Experimental** — higher amplitude is licensed, but the *coverage* rule is identical; the loud cinematic tactics of a maximal winner (neon-on-near-black, gesture-3D) never generalize onto a quiet build.

## The interaction ingredient-set — declared, coherent, everywhere

At Phase 4 the design_plan **names the interaction vocabulary** — the same way it names type and color — drawn from this file, `text-effects.md`, and `motion-palette.md`, and derived from the spine. Three rules hold it together:

1. **One vocabulary, applied identically.** The same hover language on every image, the same treatment on every link, the same reveal on every secondary. Consistency is the luxury; a different micro-move per element reads unfinished.
2. **Bespoke moments are per-section, not per-element.** The distributed signature moments are content-tied and few; the substrate is uniform and everywhere. Do not stamp one signature effect onto every element, and never ship the same generic fade on all of them.
3. **Subordinate to the signature.** The substrate is quiet by design — it is the tissue, not a second climax. If a substrate move competes with the hero for attention, lower its amplitude.

## Hide-reveal — a secondary is earned, never static

A decorative or atmospheric element sitting beside a primary — a coordinate beside the wordmark, a caption, a meta line — is **never left static**. Its default exit is to cut it; the reveal is the rare exception, not the reflex.

1. **Cut it** (default) — if it adds nothing even when revealed, it was set-dressing. Remove it. Most secondaries end here.
2. **Fold it into an interaction** (rare, justified, subtle) — for the few secondaries that genuinely earn their place: hidden at rest, revealed on hover/press with a *quiet* ingredient from `text-effects.md`. This is an occasional move, never a pattern stamped on every secondary — a page that hides-and-reveals several elements reads as a gimmick. And it is **not itself a marker of award quality**: the wordmark-coordinate reveal is a small, quiet reward, not a signature; justify each use against "would cutting it lose anything?" or it does not ship.

Used sparingly, this converts a genuine secondary — a coordinate that earns a second glance — into a quiet reward. A directional arrow that only appears on a CTA's hover is the same idea: it never sits as resting decoration, and if the CTA reads without it, it is cut, not revealed.

**Touch is mandatory, and content is never trapped.** The hide is a progressive enhancement for fine pointers only — `@media (hover: hover) and (pointer: fine)` gates the hidden state; a coarse pointer (touch) gets the element in a considered resting state or revealed on a deliberate press. Content is never left permanently unreachable behind a hover that a finger cannot trigger. Verify on a touch emulation, not desktop hover alone.

```css
.coord { opacity: 1; }                              /* touch + no-hover: always reachable */
@media (hover: hover) and (pointer: fine) {
  .coord { opacity: 0; transform: translateX(-0.4em);
    transition: opacity .3s var(--ease), transform .3s var(--ease); }
  .brand:hover .coord, .brand:focus-visible .coord { opacity: 1; transform: none; }
}
```

## The palette — substrate mechanics

Pick a coherent subset for the ingredient-set; amplitude is set by register. Evidence tags read as in `motion-palette.md` (**winner** / **shipped** / **technique**).

| Mechanic | Amplitude by register | Notes | Evidence |
|---|---|---|---|
| **Link underline / label draw** (`::after` scaleX or clip, one direction) | all — hairline, quiet | one treatment reused on every link; the `::after` clips to the shape (`anti-patterns.md`) | shipped |
| **Figure hover — contained lift / Ken-Burns** | quiet 1–3%, loud up to 6% | the frame stays put and the image scales *slowly and slightly inside* its `overflow: hidden` bound (a contained Ken-Burns), or the figure lifts — never a raw uncontained `:hover{scale}` on a bare `<img>` (the stock tell, carved out in `anti-patterns.md`); pair with a hairline frame or scrim | shipped |
| **Hide-reveal secondary** (coordinate, caption) | all | `@media (hover)` gated, touch-reachable fallback; reveal ingredient from `text-effects.md` | shipped |
| **Directional arrow — appear / translate on hover** | all | never a resting static ornament; the hover echoes the signature gesture, not a stock nudge (`premium-patterns.md`) | technique |
| **Focus ring at t=0** | all | custom `:focus-visible`, never animated in (`ship-ready-floor.md`) | shipped |
| **Custom or considered cursor** | quiet: none/minimal; loud: bespoke | never the native `grab`/`not-allowed` as an affordance (`anti-patterns.md`) | shipped |
| **Magnetic / tilt element** | loud registers only | Framer `useMotionValue` off the render cycle; not on a minimalist build | technique |
| **Section-tied bespoke moment** (a distributed-signature echo) | per archetype | one per relevant section, content-derived, not one effect reused | winner — Cartier '365' (distributed) |

## Reduced motion and the still state

Under `prefers-reduced-motion: reduce`, the substrate strips transitions and keeps state — a hover still changes color, it just does not ease; a reveal shows its final state. Coverage survives reduced motion; only amplitude goes to zero. Every hover-revealed secondary is reachable without a pointer (the touch fallback above doubles as the reduced-motion and keyboard path).
