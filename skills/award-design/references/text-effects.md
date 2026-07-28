# Text Effects — type as a motion surface

Type is a first-class interaction surface, not static copy waiting for a layout. The mechanics here are the award vocabulary for making text *read to* the visitor — the scroll-emphasis fill that recurs down a copy-heavy page, the per-letter reveals of a kinetic build — paced so the eye is guided, never fought. Load at Phase 3/4 with `motion-palette.md`; a text-emphasis moment is a distributed-signature echo (`interaction-signatures.md`), not a blanket effect on every paragraph.

## The safe framing — binding

A scroll-linked text effect is award-grade only inside these constraints. They come from the Nielsen Norman Group scroll-animation findings and are non-negotiable:

- **Emphasize already-legible text — never reveal from invisible.** The base state is fully readable (dim ink, low-contrast-but-AA, or plain weight); the effect brightens, colors, or weights it as it enters the reading zone. Text that animates from `opacity: 0` / invisible → visible is a content reveal and falls under the fire-once rule (`motion-palette.md`); an *emphasis* fill on legible text does not hide anything.
- **The finished state is the CSS default.** Author the emphasized/visible state as the resting CSS; the effect is layered on inside `@supports`. So a browser without scroll timelines, a reduced-motion user, and a reader scrolling back up all see fully legible, fully emphasized text — nothing to hunt for.
- **Fire-once-persist is the default; reversible is a declared exception.** A scrubbed emphasis reverses on scroll-up by default (dim again). That is tolerable only because the base is legible — but prefer fire-once-persist (emphasize as it arrives, then hold). A reversible emphasis is an Editorial/Immersive choice declared in the DESIGN.md and `cover`-phase-ranged (`motion-palette.md`), never the silent default.

## Browser reality — the Firefox tax

CSS scroll-driven animation is **not Baseline** — Firefox stable is the hold-out, and the engine versions and current support figure are one dated row in `stack-facts.md`. So a CSS-only scroll-emphasis effect needs a progressive-enhancement fallback, and **GSAP SplitText + ScrollTrigger, smoothed with Lenis, is the cross-engine path** when the effect must run everywhere. Either way the resting, emphasized state is the base (above); the animation lives only inside `@supports (animation-timeline: view())` or behind the JS feature check.

## The palette — text mechanics

Pick what the world's voice calls for; do not run all of them, and never on every block. Tags as in `motion-palette.md`.

| Mechanic | Moves | Reversible? | Stack path | Evidence |
|---|---|---|---|---|
| **Scroll emphasis-fill** (dim → bright as the line enters the reading zone) | emphasis on legible text | prefer fire-once | GSAP SplitText words + ScrollTrigger scrub, or CSS `view()` on line-wrapped spans | shipped |
| **Semantic accent word** (key terms carry the brand accent, the rest neutral) | emphasis | fire-once | color on marked spans, rationed to real key terms | shipped |
| **Per-word / per-line reveal stagger** (arriving heading or standfirst) | content | fire-once, persist | GSAP SplitText + IO trigger (`motion-palette.md`) | shipped |
| **Per-letter font / weight swap** (letters shift weight or face on scroll or hover) | emphasis / décor | either | variable-font `font-variation-settings` per glyph, GSAP or `@property` | technique |
| **Heading clip / gradient wipe** (as emphasis on an already-legible heading) | emphasis | fire-once | CSS `clip-path` / masked gradient + IO | shipped |
| **Kinetic climax** (char choreography as the signature beat) | content | fire-once | GSAP SplitText | technique |
| **Character-typed-by-scroll** (per-glyph reveal welded to scroll) | décor | reversible | JS-rAF `--type` + `@property <number>` (`motion-palette.md`) | shipped |
| **`::selection` in the accent** (a quiet second-read detail) | static | — | `::selection { background }` (`optical-craft.md`) | shipped |

## The semantic accent layer

The strongest text signature is meaning, not motion: the key terms of a line carry the brand accent while the rest stays neutral, so the copy is *read* — the eye lands on what matters. Ration it to genuine key terms (a product name, the verb of the sentence, the one number that matters); an accent on every third word is noise, and the accent stays the page's single accent (`preflight.md` accent lock). This is the layer that made Terminal Industries' walls of copy feel authored rather than dumped — the color did the reading.

```css
/* emphasis-fill: legible base, brightened on scroll — visible default, motion inside the gate */
.line { color: var(--ink-2); }                               /* AA-legible at rest */
@supports (animation-timeline: view()) {
  @media (prefers-reduced-motion: no-preference) {
    .line { color: var(--ink-1); animation: warm linear both;
      animation-timeline: view(); animation-range: entry 20% cover 45%; }
  }
}
@keyframes warm { from { color: var(--ink-2); } to { color: var(--ink-1); } }
.line .key { color: var(--accent); }                          /* semantic accent, rationed */
```

## The craft lever — two channels, staggered (art vs a mechanical fade)

A single property fading globally reads as mechanical. What makes a text effect feel *authored* — the reason Terminal Industries' copy looks like art and a plain reveal does not — is **two channels moving together, staggered per unit** (char / word / line):

- **Two channels, not one.** Opacity *and* a colour pass; or weight *and* tracking; or a clip *and* a slide. Terminal's signature, confirmed by inspection, is the canonical case: each character fades in **as the accent colour** (`opacity: 0 → 1` while `color` is the lime accent), then settles **accent → base** (`lime → white`). The accent *entrance* is the craft; a plain `opacity: 0 → 1` is the fade everyone writes. A grey→black, single-channel, fire-once emphasis (what falls short) changes one property once, then sits static — correct but inert. Add the second channel, the stagger, and a persist-or-scrub, and the same copy reads alive.
- **Staggered in reading order.** Chars/words resolve left-to-right, not all at once — at any mid-scroll frame the head is already settled while the tail is still arriving, so the eye follows the sweep.
- **Scrubbed over a sticky pin = the sustained top-to-bottom feel.** The "continuous transformation the whole way down" is not a bigger one-shot fade — it is the effect **scrubbed to scroll over a `position: sticky` pin** (a 2–3-viewport-tall section), one headline handing to the next. Pin with CSS `sticky`, **not** ScrollTrigger's `pin`, under Lenis, to avoid smooth-scroll jank.

**The stack.** Cross-engine: GSAP `SplitText` (now free; its `mask` option and `aria:"auto"` handle the split-span a11y) + `ScrollTrigger` (`scrub`, `pin:false`) + Lenis. Lighter but Firefox-gated: the pure-CSS `animation-timeline: view()` path with a per-span `animation-range` stagger (fallback = the resting emphasized state, above). A fire-once accent flash needs no library — a per-char `@keyframes color` (`pale → accent → final`) with `animation-delay: var(--stagger)` set in JS. **The through-line for all of them:** two channels + a stagger; a single-property global fade is the tell.

## Hover on text — what the tier ships

The nine-line evidence pass read every winner's stylesheet for one question: what happens when the pointer crosses text? The answer is narrow, and the narrowness is the law — **hover life lives on interactive text (nav labels, links, index rows, controls); headings, body prose, and standalone numbers stay inert in every register.** The forms that ship, with the score-cited winner per form:

- **Underline materials on links** — the tier's dominant form, in four verified materials: the leading-edge `scaleX(0→1)` draw (FlowFest 7.36 adds `rotate(0.001deg)` for crisp rasterization; Exo Ape reuses one rule across nav, list, and footer links); the width-grow bar (Meridian 7.89: `width` 0→100%, `transition: width .5s cubic-bezier(.165,.84,.44,1)`); the fade-in hairline (Depo Luxe 7.62: `height:.5px`, `opacity` 0→1 on `currentColor`); the `background-size` gradient highlight (Cyd Stumpel; Ink & Switch). All winner-verified.
- **Color shift on links and utility copy** — a plain `color`/`opacity` transition, never a sweep along the glyphs: Terminal Industries 7.68 (`color: var(--c-lime)`, `.3s`); Delvaux (`opacity:.7`); Stefan Vitasović's strike-through `a:hover{text-decoration:line-through}` gated by `@media(any-hover:hover)`.
- **Per-char or clone roll-swap — nav labels only** — Son Daven 7.62 (outgoing chars `yPercent:0→-75`, incoming `75→0`, `stagger:{each:.025, from:"random"}`, desktop-only); Cuberto's skewed roll (`translateY(-150%) skewY(5deg)`); Lusion's clone-swap (word-level clone stacked in markup, refutation-corrected). The one genuine per-character hover in the corpus, and it never touches prose.
- **Row-level response on index/list rows** — the hover answers on the *row*, not the type: Depo Luxe's metadata cross-fade (client/counter out, title brightens, director in), Son Daven's spotlight-dim (siblings drop to `opacity:.2`), Terminal's drawer highlight (`background-color:#ffffff1a`), Siena's `:has()` sibling-dim.
- **Heading accent recolor — Immersive's licence** — the one register that hovers a heading: Siena 7.9 recolors a review heading to the page's single accent (`.8s` easeOutQuint) and ships a dedicated per-char rollover split. Sparingly, as the accent doing the reading — never a generic effect per block.
- **Character scramble — Brutalist glitch register only** — Eloy (HM): JS on `[scrambleText]`-labeled elements, charset `'*&@#%$-_:/;'`, 100ms interval, original restored on leave. Labeled elements only, never blanket.

**The absences are canon, not gaps.** No winner in any line shifts `font-weight` or `font-variation-settings` on hover (corporate-luxury grep: zero) — variable-font motion lives on scroll or idle time, or a control retargeting a display title (Exat), never the pointer on the glyphs. No color sweep along a paragraph, no per-char rise on hovered prose, no background highlight on reading copy — anywhere. And the quiet registers ship almost nothing at all: Bento's sanctioned kit is link brighten + underline draw + arrow nudge with headings and metrics untouched; Editorial's entire vocabulary is `text-decoration: underline` on a card title via container hover (Truekind 7.47: 47 hover rules, zero on prose); Minimalist, Spatial-Organic, and Brutalist leave prose still and spend the budget on the scroll-welded décor channel. A quiet register's still prose is the register — adding heading/prose hover there is above-tier invention, not a fix. **"Prose still" scopes to the PARAGRAPH body — the DISPLAY entrance still carries a felt reveal**: Terminal's minimalist hero cascades its H2 per-char (+0.025s/char) and its chapter headings arrive masked on scroll-in. So the quiet register means no per-char rise on hovered *body copy*, never a page with no felt display text — a heading that only clip-wipes in, or a page whose sole "text effect" is a static colour accent, is the dead page (the Cennini failure), not the restrained register. The felt text moment lives on the heading/display reveal on scroll-in; the prose stays still beneath it.

**The misfire guard — binding.** Hover-on-text never impedes reading or selection: the response never reflows the line (no size/weight change on the hovered glyphs), never blocks selecting or copying the text, and never hijacks a link's activation. If a pointer pass makes the sentence harder to read than rest, cut the effect.
