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

The "Inter everywhere" anti-pattern lives in this archetype's failure mode — pick a face with character. Terminal Industries uses Söhne; Linear uses Inter (paired with discipline that earns it); Anthropic uses Tiempos for warmth. Inter as default H1 tells judges that no type decision was made.

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
  transition: opacity var(--duration-hover) var(--ease-standard),
              transform var(--duration-hover) var(--ease-standard);
}
.minimal-card:hover { opacity: 1; transform: scale(1.02); }
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

**Text** — Per-char masked reveal is the signature: each glyph in its own `overflow:clip` wrapper (`char-wrapper+char-wrapper{margin-left:-.05em}` keeps kerning), `.char` set `opacity:0` then translated up with an *indexed* stagger under expo — Stefan runs `duration: 1.25 + index * 0.025s` per char with `easeExpOut`. Use once, on the hero headline or load-time wordmark. (Stefan Vitasović, Awwwards SOTD 2025, Codrops-verified; Terminal ships the same scaffold). Supporting: scramble/decode text with hardcoded per-index timing (Gabriel Contassot, single-source on the exact durations) and clip-path line reveals for headings where per-char would be too busy.

**Cursor** — Keep the system cursor. `cursor:pointer` on interactives, `cursor:default` elsewhere — no follower, no `cursor:none`. CSS-verified across three winners, so canon not a note. The only blend trick lives on a text/overlay element (`mix-blend-mode:difference` on an oversized label crossing light/dark sections), never a cursor follower (Gabriel Contassot, single-source).

**Loader / intro** — Either instant paint that lets the per-char/clip reveals *be* the intro (observed, implementation unverified), or a `≤2.8s` minimal preloader in one of two verified forms: an accelerating 1→100 numeric counter (Gabriel Contassot, Codrops-verified), or a two-panel split-curtain (`50svh` masks) retracting to uncover the page, paired with a counter recoloring through the accent (Terminal Industries, single-source on the curtain). Never a spinner or a blocking brand-color splash.

**Anti-signals** — Absent from every winner examined: a pale-tint fill on a *primary* CTA (the `5–10%` wash is quarantined to ghost buttons only — primaries move the full token); a contrasting `border-bottom` under a solid nav bar on scroll (bars float transparent or frost translucent); the same underline-slide smeared across buttons, links, and nav (winners split it — wipe/shift on buttons, draw on links, dot on nav); a custom circle-follower or magnetic-blob cursor; a blocking splash or spinner preloader; one global `fade-up 20px, .6s ease` on every section (reveals are masked/clip-path under expo with indexed timing); Tailwind's default `cubic-bezier(.4,0,.2,1) .15s` left as the site's motion identity; Inter as the display face.
