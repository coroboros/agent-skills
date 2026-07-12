# Minimalist

Two to three colors maximum. Every element justifies its existence. Typography carries the design where decoration would otherwise smuggle in. The archetype's discipline is subtraction — what remains is what matters.

## Canonical reference — Terminal Industries

**Site.** Terminal Industries
**URL.** `terminal-industries.com`
**Award.** Awwwards Site of the Month, September 2025 (+ Developer Award)
**Studio.** REJOUICE® and PROPAGANDE.

Operates a B2B yard-management OS. The textbook minimalist reference for 2025: two-color system, type-driven, generous whitespace, scroll-driven storytelling carried by a single cinematic photograph (a black truck silhouette against amber sky). One of the rare logistics-SaaS sites to crack SOTM tier — proof that restraint outperforms decoration in a category prone to overdesign. Substitutable peers: `linear.app` (Swiss-grid airy minimalism), `stripe.com` (off-white pages with surgical purple), `vercel.com` (pure grayscale with single emphasis weight), `mintlify.com` (reading-optimized Inter with green accent).

## DNA — non-negotiable

- Two to three colors maximum carry the entire system
- Macro whitespace (120–200px+ section padding on desktop) is active design, not absence
- Typography carries hierarchy through scale, weight, and color — never through chrome
- Single accent functions as punctuation — present once per viewport, never twice
- Every element answers the question "what would break if this disappeared"

The archetype keeps its identity across airy-Swiss (Linear, Stripe, Vercel), warm editorial-light (Notion, Anthropic adjacency), cinematic photography-led (Terminal Industries), and dark monochrome (Linear's dark mode). Background register is an expression choice, not a definition.

## Common expressions

Three stacks fit the DNA. Pick the one matching brand voice and content type.

### Airy Swiss-grid — Linear / Stripe / Vercel profile

Off-white foundation (`#FAFAFA`, `#F7F6F3`, `#FBFBFA`). Swiss typographic discipline — Geist, Söhne, or PP Neue Montreal at 48–96px headlines with surgical letter-spacing. Single accent (Linear violet, Stripe purple, Vercel pure grayscale with weight contrast only). Hairline dividers (`#EAEAEA`) where structure demands. Ideal for SaaS, developer tooling, design platforms, technical product marketing.

### Cinematic photography-led — Terminal Industries profile

Off-white or warm cream foundation (`#FAFAF5`, `#E8E4DF`) with one dominant cinematic photograph occupying full viewport — golden-hour silhouette, industrial scale, dramatic light. Glass-pill nav with one CTA in a single saturated hue (Terminal uses lime green). Type holds a supporting role; the photograph is the hero. Ideal for industrial brands, logistics, architecture studios, automotive marketing pages, single-product showcases.

### Dark monochrome — Linear dark / portfolio profile

Near-black foundation (`#0A0A0A`, `#0E0E12`) with off-white type, single saturated accent. Same Swiss discipline inverted. Ideal for high-end portfolios, design tool dark themes, technical documentation, developer-focused launch pages.

## Typography

Single family with weight contrast, or geometric sans (display) paired with humanist sans (body).

- **Headlines**: Suisse Int'l, Neue Haas Grotesk, Söhne, PP Neue Montreal, Geist — 48–120px, weight 500–700
- **Body**: same family at 16–18px, weight 300–400, line-height 1.6–1.7
- **Tracking**: tight on display (`-0.02em`), neutral on body
- **Variable-font features**: `tnum` for tabular numbers in dashboards and pricing, `ss01`–`ss04` where the typeface offers stylistic alternates

The "Inter everywhere" anti-pattern lives in this archetype's failure mode — pick a face with character. Terminal Industries uses Söhne; Linear uses Inter (paired with discipline that earns it); Anthropic uses its custom Anthropic Serif (Georgia fallback) for warmth. Inter as default H1 tells judges that no type decision was made.

## Color

Two to three colors carry the entire system.

- **Foundation**: warm neutrals (`#FAFAF5`, `#E8E4DF`, `#F7F6F3`) or cool neutrals (`#F5F5F0`, `#F8FAFC`) or near-black (`#0A0A0A`, `#0E0E12`)
- **Text primary**: `#2D2D2D` to `#111111` on light, `#E0E0E0` to `#FAFAFA` on dark
- **Text secondary**: warm gray `#787774` or cool gray `#6B7280`
- **Single accent**: electric blue `#007BFF`, sage `#87A98F`, terracotta `#C67D5B`, lime green (Terminal Industries), Linear's violet, Stripe's purple, sustainability sage
- **Borders**: `rgba(0,0,0,0.06)` or `#EAEAEA`

If you can remove a color and nothing breaks, remove it.

## Layout

Single-column or asymmetric broken-grid. One bold focal point per viewport. Generous macro-whitespace.

```css
.wrapper {
  display: grid;
  grid-template-columns: 1fr min(65ch, 100%) 1fr;
  gap: clamp(3rem, 8vw, 12rem);
  padding: clamp(2rem, 5vw, 8rem);
}
.wrapper > * { grid-column: 2; }
.full-bleed { grid-column: 1 / -1; }
```

The Josh W. Comeau full-bleed pattern is the standard for long-form content with breakout sections. Section padding pulls from `containers.section-padding` and scales through `clamp()`. The reading measure binds to `containers.read-measure` (typically 65ch).

## Motion

Restraint extends to motion — opacity-led, never showy.

- Reveals: `clip-path` / masked `inset()` wipes, 0.7–1s under `cubic-bezier(0.19, 1, 0.22, 1)` — the 20px translate fade-up is the AI default this line's winners avoid; keep `cubic-bezier(0.16, 1, 0.3, 1)` at ~0.25s for dropdowns and overlays
- `Lenis` smooth scroll
- `GSAP Flip` for state transitions
- Hover: perceptible single-property moves — a drawn underline, a growing accent dot, an inverting fill; no examined winner hover-scales a card, and a 1.02 twitch reads dead (`interaction-signatures.md`)
- Optional: variable-font weight micro-shift on hover (`wght` 400→500)

```css
.minimal-card {
  clip-path: inset(0 0 100% 0);
  transition: clip-path var(--duration-reveal) var(--ease-out-expo);
}
.minimal-card.is-revealed { clip-path: inset(0 0 0 0); }
```

Durations bind to `motion.duration-*`, easings to `motion.ease-*`. The Motion atmosphere score sits at 3 by default (±2 per the brief); pushing higher means the archetype is leaning toward Editorial or Immersive, and the recommendation should be revisited.

## What makes it award-worthy

A minimalist site scores 8+ when restraint reads as decision rather than emptiness — when the single accent is placed with surgical precision, when the type pairing is felt before it's noticed, when the whitespace itself signals confidence. Terminal Industries succeeds because the cinematic photograph and the lime CTA are anchored against generous void; the page is composed, not arranged.

The archetype loses identity in two failure modes: blanding (cookie-cutter geometric sans with safe muted palette — actively rejected by judges in 2025–2026), and cargo-cult Swiss (Inter at default tracking with no character behind the choice). Restraint without conviction collapses into corporate template.

## Ideal for

SaaS (Linear, Stripe, Vercel adjacency), luxury brands with quiet voice, architecture and design studios, high-end portfolios, design-tool landing pages, technical documentation, developer marketing, founder-led product launches.

## Cross-references

Read alongside `foundations.md` (typography systems, OKLCH single-accent strategy, animation toolkit), `anti-patterns.md` (blanding is rejected; pure `#FFF` with no character is rejected; Inter as display font is rejected), `audit-rubric.md` (Hierarchy 9+, Color 9+ are entry bars in this archetype), `exemplars.md` (Linear, Stripe, Vercel, Mintlify).

## Effect palette — what this line's winners ship

Corpus — Terminal Industries (Awwwards SOTM Sep 2025 + CSSDA WOTD), Stefan Vitasović Portfolio25 (Awwwards SOTD 7.25, 2025), Gabriel Contassot (Awwwards SOTD Apr 2024 + CSSDA), Treize Grammes (Awwwards HM Oct 2024), Rogier de Boevé (Codrops case study, single-source). Terminal is the anchor — live stylesheet read rule-by-rule; the rest mix live-CSS reads and the authors' own Codrops case studies.

**The grammar** — Vary the *geometry* per element class, hold three things constant: one accent, one easing family, one origin logic ("everything resolves toward the accent, drawing/wiping/growing from a fixed edge"). Content reveals and fills run easeOutExpo `cubic-bezier(.19,1,.22,1)` at `.7–1s`; color/opacity fades run easeInSine `cubic-bezier(.39,.575,.565,1)` at `.2–.3s`; dropdowns/overlays run `cubic-bezier(.16,1,.3,1)` at `~.25s`. Two speed registers, never one. If two classes share a geometry, one is redundant — differentiate or merge.

**Buttons / CTA**
- **Directional token-wipe inversion** — a `:before` in the dark token sits `translate3d(0,100%,0)` inside an `overflow:hidden` pill; hover wipes it up and *inverts the token pair* (lime bg/dark ink → dark bg/lime ink), `transform .7s cubic-bezier(.19,1,.22,1)`, ink recolors over `.3s` with a `.2s` delay. Full-strength color the whole way · pick for the single hero CTA in a photographic or high-contrast system · (Terminal Industries, Awwwards SOTM 2025).
- **Full-token bg shift, ink held** — hover swaps `background-color` to a dedicated hover *shade of the same hue*, no motion, a real darker/lighter step never a transparency wash · pick for airy Swiss-grid SaaS where a moving fill reads as noise · (Stripe, reference-tier; corroborated by Terminal's `.drawer-cta-button:hover` token swap).
- **Ghost pale-tint fill (the only sanctioned wash)** — transparent button fills to a `5%` tint of the dark token (`rgba(5,36,36,.05)`), text held · tertiary/ghost only, never the hero · (Terminal Industries, Awwwards SOTM 2025).

**Links**
- **Underline draw under the label** — a 1px `:after`, `scaleX(0)` origin `right` → `scaleX(1)` flipping to `left` on hover, slow `.7s cubic-bezier(.19,1,.22,1)` · the one place the classic underline-slide belongs, on links not buttons · (Terminal Industries, Awwwards SOTM 2025).
- **Strike-through on hover** — `a:hover{text-decoration:line-through}` guarded by `@media(any-hover:hover)`, no motion, editorial confidence · pick for typographic portfolios where links are body-set · (Stefan Vitasović, Awwwards SOTD 2025; single-source).
- **Arrow nudge** — inline arrow glyph translates `translate(2px,-2px)` up-right, opacity → 1, layered under the underline draw · micro-amplitude · pick for read-more/external/resource links · (Terminal Industries, Awwwards SOTM 2025).

**Figures / cards**
- **clip-path / masked reveal** — reveal media by moving an `inset()` mask, not opacity alone: `inset(0 0 100% 0)` → `inset(0 0 0 0)` bottom-up, or `inset(0 100% 0 0)` left-to-right · (Terminal Industries + Gabriel Contassot, both CSS-verified).
- **Inverse-scale parallax** — image scales *inversely* to scroll progress (`scale(1.2 + track * -0.2)`) as a masked inset opens; amplitude small (±0.2), never a 50%-translate parallax · (Gabriel Contassot, Awwwards SOTD 2024; Codrops-verified).

**Nav** — Float fully transparent over the hero (`position:fixed`, `background:transparent`, `pointer-events:none` on the shell, children re-enable), or frost translucent (`rgba(…,.8)` + `backdrop-filter:blur(5px)`). The nav-item indicator is a growing `5px` accent dot centered below the label (`opacity:0; scale(0)` → `scale(1.01)`, `transform 1s cubic-bezier(.075,.82,.165,1)`), not an underline — the dot itself is single-source on Terminal, the "nav ≠ the link underline" principle holds across the corpus. Winners never hang a colored `border-bottom` under a solid bar. (Terminal Industries, Awwwards SOTM 2025; frost from Stripe, reference-tier).

**Text** — Per-char masked reveal is the signature: each glyph in its own `overflow:clip` wrapper (`char-wrapper+char-wrapper{margin-left:-.05em}` keeps kerning), `.char` set `opacity:0` then translated up with an *indexed* stagger under expo — that scaffold is Terminal's (Terminal Industries, Awwwards SOTM 2025, CSS-verified). Stefan lands the same read through masked segments positioned by `left` and `x` transforms — not per-char clip wrappers — timed `duration: 1.25 + index * 0.025s` under `easeExpOut` via Framer Motion (Stefan Vitasović, Awwwards SOTD 2025, Codrops-verified). Use once, on the hero headline or load-time wordmark. Supporting: scramble/decode text with hardcoded per-index timing (Gabriel Contassot, single-source on the exact durations) and clip-path line reveals for headings where per-char would be too busy.

**Cursor** — Keep the system cursor. `cursor:pointer` on interactives, `cursor:default` elsewhere — no follower, no `cursor:none`. CSS-verified across three winners, so canon not a note. The only blend trick lives on a text/overlay element (`mix-blend-mode:difference` on an oversized label crossing light/dark sections), never a cursor follower (Gabriel Contassot, single-source).

**Loader / intro** — Either instant paint that lets the per-char/clip reveals *be* the intro (observed, implementation unverified), or a `≤2.8s` minimal preloader in one of two verified forms: an accelerating 1→100 numeric counter (Gabriel Contassot, Codrops-verified), or a two-panel split-curtain (`50svh` masks) retracting to uncover the page, paired with a counter recoloring through the accent (Terminal Industries, single-source on the curtain). Never a spinner or a blocking brand-color splash.

**Scroll texture** — What carries the eye down the page between interactions: a masked figure reveal riding inverse scroll-scale (Gabriel Contassot, winner-verified), canvas frame-sequence photography scrubbed by the scrollbar, or the scroll-scrubbed per-char recolor sustained top-to-bottom — Terminal runs it the full page height, so the text substrate itself is the carry (Terminal Industries, winner-verified). The design_plan names one: the committed carry, never a hoped-for side effect of the section reveals.

**Idle band** — Near-zero canon, and that IS the evidence: ~1 quiet channel across the corpus. Winners hold the page still between inputs — the life lives in the masked reveals and the scrubbed carry, not in ambient loops — so commit one quiet channel or its declared absence and let stillness read as the register, never as coverage skipped.

**Anti-signals** — Absent from every winner examined: a pale-tint fill on a *primary* CTA (the `5–10%` wash is quarantined to ghost buttons only — primaries move the full token); a contrasting `border-bottom` under a solid nav bar on scroll (bars float transparent or frost translucent); the same underline-slide smeared across buttons, links, and nav (winners split it — wipe/shift on buttons, draw on links, dot on nav); a custom circle-follower or magnetic-blob cursor; a blocking splash or spinner preloader; one global `fade-up 20px, .6s ease` on every section (reveals are masked/clip-path under expo with indexed timing); Tailwind's default `cubic-bezier(.4,0,.2,1) .15s` left as the site's motion identity; Inter as the display face.

Channel calibration — this line's winners run 3–4 distinct interaction channels (per-class states, display-type effects, cursor, idle, scroll texture, replayable spectacle); the pre-emit critique's Aliveness axis reads against that band, never against bare coverage.

## Page recipe — how this line's winners build the page

Corpus — Terminal Industries (live CSS+DOM), Gabriel Contassot (live DOM), Treize Grammes (live DOM), Stefan Vitasović (live + Codrops), Rogier de Boevé (media-only, Codrops).

**Anatomy** — *Product-narrative scroll* (`argument-scroll`; Terminal, winner-verified order; Treize softer): hero statement · attention → logo strip · proof → stat odometer · understanding → "That's the Yard Operating System. YOS™" reveal · climax, mid-page → three benefits · understanding → executive quote · proof → contact + oversized-wordmark footer · close; rest is the void gap, seams masked, never hard cuts. *Gallery-index stack* (`gallery-stack`; Gabriel, Stefan, winner-verified): text-only name card · attention → one full-bleed project per viewport, masked reveals · proof (the first still below the fold is the climax) → bare "SCROLL UP" close. *Single-canvas monolith* (`engine-world`; Rogier, technique / single-source): one WebGL scene is the page, screens rotated on a circular path.

**Hero architectures** — *Sequenced statement over cinematic still* (Terminal, winner-verified): the headline is `h2.title-sequence` (`min(5.729vw,146.667px)`, w400, lh .95) cycling four statements; the only `<h1>` waits in the footer; one CTA. (Easings verified; durations shipped.)

| element | order | transform | duration | easing |
|---|---|---|---|---|
| curtain, `#ededed` 50svh halves | 1 | retract | ~0.8–1.2s | easeOutExpo `(.19,1,.22,1)` |
| odometer | 2 | 1→100, gray→lime→dark-green | load-tied | linear |
| H2 chars (`overflow:clip` wrappers) | 3 | translateY up, +0.025s/char (technique) | ~1–1.25s | same |
| nav | 4 | opacity 0→1 | ~0.25s | `(.16,1,.3,1)` |

*Text-only name card* (Gabriel, Stefan — copy winner-verified, motion shipped): oversized name `<h1>`, role line, void, scroll cue as sole affordance, no CTA. Treize's softer variant: imperative `<h1>` + subhead + warm CTA "Programmer une visio" (winner-verified copy).

**Footer** — the award lever (Terminal, winner-verified): dark-green ground; the `<h1>` lives here — `.footer-title{font-size:max(4.375rem,min(4.688vw,120px))}`, line-height .95, chars de-emphasized to `#fff3`; sticky reveal — `.footer__wrapper{position:fixed;bottom:0;transform:translateY(100%)}` over a 50vh holder, a pure-black overlay darkening the outgoing page. Portfolio norm: the bare cue — "SCROLL UP" (Gabriel), "2025." (Stefan).

**Arrival** — the Loader row families (`ingredients/preloaders.md`): curtain + counter recoloring into the footer's dark-green (Terminal, winner-verified); bare 1→100 counter (Gabriel, Codrops-verified); instant paint, reveals-as-intro (Treize, observed). Route transitions (`ingredients/page-transitions.md`): the route loader swaps the light curtain for `rgba(0,0,0,.7)` (winner-verified); in-page swaps ride Vue `reveal-y`, enter from `translate3d(0,100%,0)`, opacity `.6s` easeInSine + transform `1.2s` easeOutExpo (winner-verified).

**Copy voice** — Quoted to calibrate, never to ship — imitate the specificity (the named place, the count, the refusal), never the wording. First-plural visionary or bare name in the hero, second-person imperative at the CTA; fragments — the line break is the punctuation; TM on the product noun; the period as weight; refuses adjective stacks and self-narration. "No exclamation" fails corpus-wide: Treize ships "Activez votre marque !".
- "We have reinvented the future of logistics" / "through the yard." (Terminal) — vision, then the fragment turn.
- "Powering the yards behind the  brands you know" (Terminal, double space [sic]) — proof named in the reader's world.
- "GABRIEL CONTASSOT" / "FREELANCE DESIGN DIRECTOR" / "18.24" (Gabriel) — name, role, number: the whole hero.
- "Awwwards Jury member since 2020." (Stefan, live DOM) — proof by dated credential, no self-praise.

**Imagery art direction** — one grade per page. Cinematic (Terminal): industrial-scale subject, full-bleed horizon-anchored crop, golden-hour single warm source, amber/cream low-saturation grade — a `<canvas>` frame-sequence under an SVG gradient mask (mechanism winner-verified; grade shipped). Gallery (Gabriel, Stefan): full-bleed stills one per viewport in a single grade — Gabriel strict pure-black monochrome (winner-verified layout; grade shipped).

**Spectacle menu** — *Terminal load*: curtains retract → odometer climbs gray→lime→dark-green → chars cascade over the truck photo; payoff — the intro pre-states the palette: final green = footer ground, lime = CTA (winner-verified mechanism). *Gabriel seams*: scroll a light/dark boundary → oversized label crosses under `mix-blend-mode:difference` (live CSS-verified), figures open on inverse-scale masks `scale(1.2 + track*-0.2)` (Codrops); payoff — the seam is the show.

**Anti-signals** — no winner in this line opens on a card or bento grid; no hero carousel; no stacked hero CTAs; the `<h1>` is not assumed hero-bound — Terminal's is the footer statement; no second accent visible per viewport (an unspent orange token exists); no mixed-grade imagery.
