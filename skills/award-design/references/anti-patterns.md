# Anti-Patterns

Validation catalog the build holds itself to and the review mode enforces. Read before submitting or requesting review. Grouped by the kind of failure mode they create.

## Axiomatic rejections

Non-negotiable. If the design contains any of these, stop and fix — don't argue the edge case. These are the fingerprints of AI-generated work that every experienced judge recognizes in under three seconds. A single axiomatic violation is enough to score below Honorable Mention, no matter how strong the rest is.

1. **Never use the AI-purple gradient.** `linear-gradient(135deg, #a855f7|#8b5cf6, #ec4899|#6366f1)` — any variant pairing purple with pink or purple with blue. The moment judges see it, they stop looking.
2. **Never use Inter, Roboto, Arial, or system fonts as the display face.** They work as fallbacks and body. At the hero, they signal "no type decision was made". Pick deliberately — a custom face, a quality paid font (Söhne, Tiempos, GT, Apoc), or a distinctive free one (Geist, PP Editorial New). Instrument Serif and Fraunces are the two overexposed LLM-favorite display serifs — reach past them or justify (see *AI Tells → Typography*). Don't ship `font-family: 'Inter'` on an H1.
3. **Never use pure black (`#000`) or pure white (`#FFF`).** Off-black (`#0a0a0a`, `#141413`, `#1a1a1a`) and off-white (`#fafafa`, `#f5f4ed`, `#faf9f5`). The shift is 1% on a color picker and 100% of the atmosphere.
4. **Never use placeholder names or fake statistics.** "John Doe", "Sarah Chen", "Acme Corp", "99.99% uptime", "10,000+ happy customers", "50% faster". If content isn't real, write something specific and plausible — or keep the placeholder honest (`[client name]`, `[metric]`). The realistic-data rule: prefer `47.2%` to `99.99%`, `+1 (312) 847-1928` to `1234567`, `$99.00` to `$100.00`. Real data has texture; round numbers betray placeholder fill.
5. **Never ship the centered-hero-over-dark-image-with-generic-headline template.** The canonical AI landing page. Break one of those three: off-center the layout, use flat color or typographic hero, or write a headline that couldn't apply to another product.
6. **Never ship 3 equal cards in a row as your feature section.** The "feature row" is the most recognized AI template. Vary card sizes, move to editorial or bento layouts, or use a dominant card with supporting detail — not equal thirds.
7. **Never use emojis as UI icons.** Icon sets exist (Phosphor, Radix, Lucide, Iconify, custom SVG). Emojis in UI signal no design system.
8. **Never ship without a signature moment — and never let the page die after it.** One interaction, one visual, one typographic decision that someone will remember after 30 seconds. The failure is *incoherent* scatter — a different unrelated effect on every element — not motion itself; and the equal failure is a loud hero over a page that goes inert below it (every link, image, and card static to the footer). The winning shape is a **distributed signature over a live substrate**: one dominant climax plus a few section-tied echoes, over a coherent low-amplitude interaction vocabulary applied to *every* interactive element (`interaction-signatures.md`). Restraint lowers that substrate's amplitude, never its coverage — a quiet build still has everything respond. If you can remove every effect and the page reads the same, there is no signature; if the page reads dead once you pass the hero, the substrate is missing. Premium pages also carry a *second-read moment* — a quiet detail noticed only on a return visit (an unexpected punctuation, an asymmetric bleed, an off-rhythm whitespace zone). Loud climax + live substrate + quiet detail is the full pair; a hero alone is incomplete.
9. **Never wrap an H1 across 4–6 lines.** Use ultra-wide containers (`max-w-5xl`, `max-w-6xl`, or `w-full`) and scale type with `clamp()` so the headline lands in 2–3 lines maximum. The narrow-container 6-line wall is the canonical AI-headline failure. See `premium-patterns.md` for the 2-Line Iron Rule.
10. **Never use meta-labels like "SECTION 01" or "QUESTION 05".** Eyebrow tags carry meaning ("PRINCIPLES", "OUR APPROACH", "RECENT WORK"); meta-labels carry index numbers and read cheap. If the section needs a tag, write the category — not the count.
11. **Never use generic avatars.** Standard SVG "egg" placeholders, Lucide user icons, or stock "diverse team" photography signal "AI placeholder filled in last". Use real photography, candid shots, or a consistent illustration style. For demos, use `https://picsum.photos/seed/{context}/W/H` with contextual seeds.
12. **Never use startup-slop names.** "Acme", "Nexus", "SmartFlow", "FlowKit", "ProSync" are the AI-generated brand-naming default. Invent contextual, plausible brand names tied to the project's domain. The placeholder honesty rule applies — `[client name]` beats a fake brand.
13. **Never ship a hero with no real visual.** A headline floating over a flat gradient is the canonical placeholder hero. The hero needs photography, generated imagery, 3D/canvas, a textured surface — or a *deliberate* typographic treatment that IS the visual (kinetic display, type-as-image). A centered headline over a purple/blue or beige gradient does not clear the floor. Full protocol and the typographic-hero override: `imagery.md`.
14. **Never hand-roll fake product screenshots out of divs.** Simulating a dashboard or app UI with divs, borders, and gradients reads as AI filler and never matches the real product. Use a real capture; failing that, an honest labeled placeholder sized to the final aspect ratio. An honest placeholder beats a CSS pastiche. Full protocol: `imagery.md`.

Run this list first when validating. Anything it catches is stop-and-fix, not nice-to-have.

## Countable checks

The deterministic core of the stop-and-fix filter — a number computed from the rendered page, compared against a threshold. The boxes live in **`preflight.md` §4** (the Phase 5 gate), one row per check with its formula, scope, and override; `scripts/preflight_scan.py` machine-counts the ones it can. One home, no drift: this catalog keeps the axioms, tells, and rationale the boxes point back to.

Scope note: the em-dash check targets **generated site copy**, not the codebase or this skill's own prose — count it in rendered body text, suppressed for `editorial` and `corporate-luxury`. Countability is the upgrade over a context-blind blocklist — award-design scores *from* an archetype, it does not subtract *toward* a generic ban.

## Cross-build anti-default

Anti-default is not only within a build (reject the lazy first option) — it holds across builds. The same brief type must never converge on one house look.

- **Rotation memory** — do not reuse the previous build's palette family, type pairing, or hero layout. If the last premium-consumer build ran sand+brass, this one runs a different family. Two sources feed it: the previous build's stamp (first line of the main stylesheet, written at Phase 4 — format defined there, once) and this session's builds. State the rotation out loud in the Phase 1 artifact — rotating in your head is how the house look creeps back.
- **Per-build invention** — every build introduces ≥1 mechanic it has not used before: a novel layout anchor, an unseen motion, a fresh type treatment, a new interaction. A build that reuses only known moves is a default in disguise.
- **Deterministic non-default selection** — seed the choice off the brief (page kind, audience, brand-name length), never the first option the model reaches for.

## Design failures

- **Template / AI layouts** — judges are working professionals who recognize these instantly. Single fastest way to fail.
- **Inconsistent systems** — polished homepage but weaker inner pages signals incomplete craft.
- **Stock-feeling photography** — generic, unselected, ungraded shots scattered across color temperatures signal generic thinking and tank scores. A surgically-curated, on-palette photograph passed through the one treatment is not this — see `imagery.md` acquisition order (curated stock is a rigorous fallback, downloaded and graded, flagged to replace).
- **Desktop-first** — judges check mobile first. Usability is 30% of the score.
- **Cookie-cutter minimalism ("blanding")** — the safe muted geometric sans default everyone adopted is being actively rejected.
- **Motif repeated into filler** — a brand motif (a coordinate, a word, a colour, a glyph) is identity while it stays purposeful and hierarchically placed, and tips into filler the moment it is sprinkled without hierarchy or the layout goes monotonous and every element looks the same. Repetition is two-sided: too little reads incoherent, too much reads padded. Keep the motif deliberate — one strong placement beats the same mark echoed on every line.

## Performance failures

- LCP > 2s, total weight > 3MB, animation dropping below 60fps.
- Videos loaded without lazy loading, 20+ font file requests.
- Images loaded twice due to poor `<picture>` implementation.
- Award-winner targets: **LCP < 1.5s**, **CLS < 0.05**, **INP < 100ms**.

## AI Tells (patterns that betray AI generation)

### Model default house style

Current models carry a persistent default aesthetic that judges now read as its own tell: warm cream backgrounds (~`#F4F1EA`), serif display type (Georgia, Fraunces, Playfair), italic word-accents, terracotta / amber accent. It suits editorial, hospitality, and portfolio briefs — and feels off for dashboards, dev tools, fintech, healthcare, or enterprise. It surfaces unprompted, in slide decks as well as web UIs. (The warm-cream cluster is the tell; the neutral off-whites endorsed below are not.)

A sibling overexposed cluster is the **premium-consumer palette** — sand/beige base (`#E7DFD3`, `#D8C7B0`), brass or gold accent (`#B08D57`, `#C9A227`), espresso text (`#3B2F2A`). The DTC-luxury monoculture, the Aesop-clone look. The hexes name the *family*, not a blocklist. Rotate at least one of the three roles — swap brass for oxblood, espresso for ink, sand for bone — or justify the palette against the brief.

Generic negation does not fix it. "Don't use cream", "make it clean and minimal" shift the model to a *different* fixed palette, not to variety. Two counters work:

- **Specify a concrete alternative** — exact palette hexes, typeface, corner radius, motion timing. The model follows explicit specs precisely.
- **Propose directions first** — surface 2-4 distinct directions (bg hex / accent hex / typeface + one-line rationale) and let the user pick, instead of committing to the default silently. Conceiving the universe already works this way — it recommends an archetype and offers one optional confirm; surface that choice rather than committing to the default silently.

### Visual

- Purple/blue gradients on white — the "AI purple" aesthetic.
- Pure black (#000) or pure white (#FFF) — use off-blacks and off-whites.
- Outer glow box-shadows, oversaturated neon accents.
- Gradient text on large headers.
- Static gradients as primary design elements (no longer differentiated).
- Ghost cards — 1px border plus a large soft shadow (blur ≥16px) on the same element; pick one elevation language.
- Card radius ≥32px — over-rounding reads as a kit default; cap cards at 12–16px unless the shape lock documents otherwise.
- Decorative grid-line/graph-paper backgrounds and `repeating-linear-gradient` stripes as section wallpaper.
- Sketchy/doodle SVG decorations — hand-drawn squiggles read as clip-art unless the universe is genuinely illustrated.
- The GitHub-dark default: uniform `#0D1117`-family surfaces with generic cyan/purple neon glow — the third overexposed cluster beside warm-cream and sand/brass. Authored darks (one hue temperature, one owned accent) stay legitimate.

### Typography

- Inter, Roboto, Arial, system fonts as primary choices.
- Space Grotesk (converging AI default) — vary between generations.
- Instrument Serif and Fraunces — the two LLM-favorite display serifs, now overexposed. Rotate to a less-defaulted face or justify. Editorial and Corporate Luxury may run a serif display, but pick past these two or state why.
- Oversized H1 that screams — control hierarchy with weight and color, not just scale.
- Serif on dashboards/software UI (serif is for editorial/luxury only).
- Clipped italic descenders — an italic display word containing `y g j p q` under `line-height: 1` loses its tails. Use ≥1.1 line-height plus bottom reserve on the wrapper; audit every italic display word before ship.
- Serif as a reflex — "creative brief = serif" is the most-tested type tell. A serif needs the brief to name one, or a genuinely editorial/luxury register plus a written why. Rotate the pool; never the same serif twice running.
- The reflex-reject procedure: name the first three faces that come to mind and reject them; a final pick that matches the reflex needs its rationale written. Extended overexposed pool beyond Fraunces/Instrument Serif: Playfair Display, Cormorant, Lora, Crimson, Syne.
- A single italicized word dropped into an upright headline as the only emphasis — recognized tell; earn it (editorial voice, declared) or skip it.

### Layout

- Centered hero with generic headline over dark image.
- Split-screen 50/50 hero — solid text panel beside a photo panel with a hard vertical seam. A recognized template. Override: an editorial diptych where both panels are in compositional dialogue, not just text | image.
- 3 equal cards in a row (the "feature row" cliché).
- Predictable symmetric layouts at every section.
- `h-screen` instead of `min-h-[100dvh]` (breaks on mobile — iOS Safari URL-bar toggle).
- Cards-inside-cards-inside-cards. Nested containers compete for visual hierarchy. Use Doppelrand (concentric outer-shell + inner-core) where elevation is needed; otherwise let spacing carry the structure (see `premium-patterns.md`).
- Asymmetric layouts that don't collapse below 768px — touch-target conflicts, horizontal scroll, drift. Mobile collapse to single-column (`w-full px-4 py-8`) is mandatory.
- Empty bento cells. Apply `grid-auto-flow: dense` and verify `col-span` / `row-span` interlock leaves zero voids.
- Hero H1 wrapped across 4–6 lines (the 2-Line Iron Rule violation).
- Split-header sections — left big headline, right small explainer paragraph floating with no compositional anchor. Stack vertically (headline, body at 65ch). Override: the right column carries a real visual or interactive element, never filler text.
- Theme flip mid-page — a light-warm section sandwiched between dark sections (or vice versa) reads as walking into a different website mid-scroll. One theme per page. Override: a single deliberate color-block device, declared in the DESIGN.md.
- Two-line desktop navigation, or a nav bar taller than 80px eating the viewport. Condense labels, drop secondary items, or go hamburger.
- Hero top padding past `pt-24` (≈6rem) — the content floats halfway down the viewport and reads as a bug, not as space. Scale the type or the asset instead.
- CTA labels wrapping to 2+ lines at desktop — shorten to ≤3 words or widen the button; never clamp a primary CTA's `max-width`.
- Mixed corner-radius systems with no documented rule — round buttons in a square layout, square cards on a pill-button page. One radius system, or a written rule applied everywhere.
- Vertical rotated text ("INDEX OF WORK 2018–2026" at 90°) — agency cliché; only when the composition genuinely needs the spine.
- Crosshair or hairline grid lines as pure decoration — lines organize content or they go.
- Scoring/progress bars with filled background tracks as comparison visuals on marketing pages.
- `<br>`-broken-and-italicized headlines ("for thirty<br><em>years.</em>") as a default design move.
- The AI-nav fingerprint: wordmark hard-left, 4–5 inline text links, CTA button hard-right, 1px hairline border-bottom — the most-recognized template nav. Break at least one element (placement, container, or divider).
- A letter-monogram glued to the spelled-out wordmark — a gilded "A" set beside "Maison Aurèle" reads as a stray character or a typo, not a mark. A letter IS text; a monogram earns its place standing alone (a favicon, a bare nav mark, a loader), never doubled against the same name it abbreviates. Either the monogram carries the brand or the wordmark does — not both, locked together.
- A decorative dot, tick, or status glyph beside the wordmark posing as the logo — a green dot, an aurora tick, a colored bullet read as a leftover UI element, not an identity. The brand mark is a designed, considered SVG/PNG glyph (or a clean typographic wordmark with no ornament), verified rendered in the browser; the *same* mark drives the favicon — a random dot at either spot is the tell (`imagery.md`).
- Tag-beside-heading two-column section head (eyebrow left, heading right) — the templated-editorial tell; stack them.
- Side-stripe accent border — a 2px+ colored `border-left`/`border-right` on cards or callouts; the 2018-SaaS tell.

### Content

- Generic names: "John Doe", "Sarah Chen", "Jack Su" — use diverse, realistic-sounding names with cultural variety.
- Fake round numbers: "99.99%", "10,000+", "50% faster" — use organic, messy data: `47.2%`, `+1 (312) 847-1928`, `$99.00`.
- AI copywriting clichés: "Elevate", "Seamless", "Unleash", "Next-Gen", "Game-changer", "Delve", "Tapestry", "In the world of...", exclamation marks in success messages, "Oops!" error handling.
- Title Case On Every Header — sentence case reads more refined.
- Emojis in UI — use icons (Phosphor, Radix, or custom SVG).
- Broken Unsplash links — use `picsum.photos/seed/{context}/W/H` or SVG placeholders.
- Lorem Ipsum — write real draft copy. Latin placeholder text never ships.
- Filler UI text — "Scroll to explore", "Swipe down", scroll-arrow indicators, bouncing chevrons. They signal "AI couldn't decide what to put here" and add visual noise that competes with the hero. If the user needs the cue, design the affordance into the layout (rhythm, depth, asymmetric reveal); don't bolt on an instruction.
- Quotes running past 3 lines, or attribution by name alone ("- Sarah"). A landing-page quote is a snippet: cut it, attribute with name + role.
- The middle-dot (`·`) as the default separator — "foo · bar · baz · qux" strips. Ration to ≤1 per metadata line; prefer line breaks, hairlines, or columns.
- Generic step labels — "Stage 1 / Stage 2", "Step 1 / Step 2", "Phase 01". The verb-noun is the label ("Install", "Configure", "Ship"); the count adds nothing.
- Atmospheric locale / time / weather strips ("LIS 14:23 · 18°C", "Lisbon, working with founders") — agency-portfolio decoration. A contact address in the footer is fine; an atmospheric strip is not. Override: genuinely place-focused or timezone-distributed brands.
- Decoration text strips at the hero bottom — `BRAND. MOTION. SPATIAL.`, `TYPE / FORM / MOTION` mono-caps bands. Only when the strip carries real navigable links or real status.
- Version labels and footers on marketing pages — `V0.6`, `BETA`, `INVITE-ONLY` hero eyebrows; `v1.4.2 · last sync 4s ago` footers. Devtool fixtures, not landing-page content. Override: the brief is explicitly a launch/preview announcement.
- Pills, tags, or photo-credit captions overlaid on images — `Plate 03 · House archive`, `Field study no. 12`. Let the image speak, or caption below it in one functional line. Credit only a real photographer, with permission.
- Decorative status dots — a colored dot before every nav item, list row, or badge. Only for real semantic state (a live availability flag), at most one per section.
- Micro-meta sentences under eyebrows ("Each of these is a feature we ship today, not a roadmap promise."). Eyebrow + headline + body is enough.
- Registration-meta eyebrows — "PROOF COPY, GRINDER NO. 114", "Brand · No. 01", edition and catalogue strings. They tell the buyer nothing and read as AI set-dressing, however diegetic the universe. Override: the number IS the product's name (Meridian K2, Porsche 911).
- Eyebrow / section kicker that restates the H1 — **or labels what the section already makes obvious.** "SMALL EXPEDITIONS · THE GEOGRAPHIC NORTH POLE" over an H1 that says the same; "THE CURRENT NUMBER" over the issue's cover; "SUBSCRIBE" over a signup form; "Our services" over "What we do". **The default is no kicker — the H1 stands alone.** An eyebrow earns its place only by carrying information the reader needs that neither the headline nor the section's own position and content already supply (a real category among several, a date, the reader's place in a long index). Restating the subject *or* naming what context already makes obvious is filler — "obvious from where it sits" counts as restating, not just word-for-word repetition. And a mono all-caps kicker stamped above *every* section — however individually worded — reads as ornamental sameness: cut them all to the few that genuinely inform.
- **Copy that narrates the artifact or credits its own making** — the site never calls itself "a feature", "an essay", "a study", never names the typefaces it is set in, never annotates its own construction. "A feature on the founding of one bell. Set in Bodoni Moda, Archivo, and IBM Plex Mono." is two tells in one line: it *describes* the piece, then *credits the tools*. A shipped brand site speaks to its reader as the brand — production copy, not a colophon about the build. Applies everywhere: hero eyebrows ("A feature in five castings"), colophons, footers, alt text. The lone exception is a house whose own credit IS its brand convention (a type foundry, a print house) — declared in the DESIGN.md, never defaulted.
- **Stacked label layers that restate each other** — a section carrying an eyebrow AND a kicker/folio AND an in-world device readout AND a title that all name the same thing is ornamental redundancy: a "The mould" title beside a "BUILDING THE MOULD" gauge beside a "The making, first casting" folio says the same word three times before the prose. One label carries the section; the others carry *distinct* information or are cut. A folio that counts ("first / second / third casting") dressed as a chapter label is registration set-dressing in diegetic costume — and a count that misfits ("third casting" for a cooling step that casts nothing) is the tell the costume was never load-bearing.
- **Over-written reading copy** — editorial is reading-*first*, never text-*dense*: a section that opens with four long paragraphs before any image, rest, or turn is a wall, not a feature. Winners compose the words — cut to what earns its place, break dense passages with a pull-quote or a full-bleed, and place the text, not pour it. "Too much text, badly structured and placed" is the fastest way an editorial build reads as a dev draft rather than a shipped page.
- **Story copy orphaned in the footer** — how the thing is made, its edition size, its provenance ("set by hand each season", "printed in an edition of 2,400", "founded 1868") belongs in the body, presenting the subject where the reader meets it — not dumped in the footer. The footer is functional: navigation, contact, legal, the wordmark. Brand-story facts parked in the footer read as leftovers the page found no place for; if a fact is worth telling, tell it where it earns the reader's attention (the issue intro, an about strip), not as fine print at the bottom.
- Undecodable data marks — dots, bars, or glyphs a stranger can't name. Self-evident marks need nothing; ambiguous ones take a one-line legend. The loop's screenshot is the test: can someone who didn't build it say what each mark is?
- A foreign-family word injected into a headline for visual interest — a serif word inside a sans H1. Emphasis is italic or bold of the same family.
- "Quietly in use at" / "Quietly trusted by" social-proof headers — use plain "Trusted by" or let the logos speak.
- Poetic section labels — "From the field", "Field notes", "On our desks", "Currently on the bench" as section headers read performative-craftsman; plain functional labels or none. (A diegetic universe may earn one — declared, not defaulted.)
- Live-stock counters as decoration ("Reservation 412 of 800") — only real data on a genuinely limited run.
- Charts where humans belong — sparklines and stat-graphics on briefs that need human proof (quotes, receipts, screenshots); and the three-identical-stat-columns KPI row.

### Technical

- Mixing GSAP and Framer Motion in the same component tree. Use Framer Motion for UI/Bento interactions; reserve GSAP/Three.js for full-page scrolltelling or canvas backgrounds, wrapped in strict `useEffect` cleanup blocks.
- `window.addEventListener('scroll')` for scroll effects — use ScrollTrigger or CSS Scroll-Driven Animations.
- Content reveals that re-hide on scroll-up — scrubbing a heading or paragraph with `animation-timeline: view()` (or any scroll-position-bound reveal) fades the copy back out as you scroll up, a documented NN/g usability failure (users can't find the scroll position that brings it back, and re-hiding text harms reading). Content reveals fire once and persist; reversible scroll-linked motion is for *decoration* that never hides content (`motion-palette.md`). A reversible content reveal is an Editorial/Immersive exception — declared in the DESIGN.md and `cover`-phase-ranged so the copy never vanishes while read.
- Complex flexbox percentage math — use CSS Grid.
- Animating `width`, `height`, `top`, `left` — use `transform` and `opacity` only.
- Unclipped animated fills and full-bleed layers. A fill / sheen / reveal inside a shaped container (a `::before` sweep on a rounded pill or card, an image wipe) that doesn't clip to the shape spills past the `border-radius` — on hover and again on the mouse-leave retract, where a static screenshot never catches it. Clip the shaped ancestor (`overflow: hidden` or `clip-path`), and prefer `translateX` / `clip-path` over `scaleX` for the fill — `scaleX` on a rounded box distorts the corners as it scales. Same rule for a full-bleed or negative-`inset` decorative layer (a hero light sweep, an oversized glow): it lives inside an `overflow: hidden` bound, or it bleeds into the adjacent section.
- React `useState` for magnetic hover or continuous animation. Use Framer Motion's `useMotionValue` and `useTransform` outside the React render cycle (see `premium-patterns.md` performance locks).
- `backdrop-filter: blur()` on scrolling content. Apply blur only to fixed/sticky elements (navbars, modal overlays). Otherwise mobile Safari drops to 15–20fps.
- Static PNG grain overlays on scrolling containers — continuous GPU repaints. Apply procedural noise (Canvas/WebGL) to fixed `pointer-events: none` layers.
- Perpetual animations not memoized in their own microscopic Client Component — re-renders the parent layout 60×/second and breaks performance budget.
- Importing a package absent from `package.json` — check first; if missing, output the install command before the import. Assumed dependencies are broken builds.
- Raw `<img>` hover scale on a bare photo (`group-hover:scale`, `:hover { transform: scale }` with no containment) — the stock image-zoom tell. The legitimate version is *contained*: the image scales slowly and slightly (≤3–6%) inside a non-moving `overflow: hidden` frame — a Ken-Burns held by the frame, paired with the frame's own treatment (`interaction-signatures.md`) — never a bare uncontained `scale` on the `<img>` itself.
- A draggable poster / `<img>` under an interactive canvas — dragging to rotate grabs the image and shows the browser's native drag-ghost (a gray box with a ghost image). Set `draggable="false"`, `user-select: none`, `-webkit-user-drag: none`, `touch-action: none` on the canvas and every underlying img (`ingredients/web3d-for-sites.md` input floor).
- The native grab-hand cursor (`cursor: grab` / `grabbing`) as the interaction affordance on a luxury 3D or drag surface — reads as a raw dev default; ship a custom cursor or a designed one-time hint. A drag hit-area that responds over the headline while the object ignores the pointer is a mislaid interactive layer.
- Native form controls left unstyled — a `<select>`, checkbox, or radio shipping raw OS chrome inside a bespoke surface. Every control carries `appearance: none` and a custom affordance (a drawn chevron, a styled box/tick); the native dropdown or checkbox is the tell the rest of the build avoids. The DESIGN.md must not prescribe a "native, styled" control — the code-craft pass overrides it if it does (`code-review.md`, `design-md-anatomy.md`).
- `cursor: not-allowed` (or any native blocked/disabled cursor) on a disabled control — the OS "no-entry" icon defaces a premium design. A disabled control drops opacity and keeps `cursor: default`; the not-allowed cursor never ships, however the DESIGN.md phrases the disabled state.

## UX anti-patterns disguised as creativity

- **Scroll hijacking** on text-heavy content — use scroll-*triggered* animations instead (user retains speed control).
- **Experimental navigation** requiring discovery — tanks usability even when creativity scores high. Every unconventional pattern needs a discoverable fallback.
- **Illusion of completeness** — scroll animations that pause, making users think they've reached the end.
- **Style over substance** — beautiful animations that slow task completion, custom cursors that obscure click targets, impressive loading screens covering 10+ second loads.
- **Cards inside cards inside cards** — nested container chrome that competes with the content it claims to elevate. One concentric Doppelrand is craft; three nested borders is noise.

## Component clichés (replace with intentional alternatives)

- **Generic card** (border + shadow + white background) — remove the border, use only background, or use only spacing. Cards exist when elevation communicates hierarchy.
- **Always one filled button + one ghost button** — add tertiary text links to vary visual noise.
- **Saturated color-block CTA on a refined page** — a solid ochre / bright-accent slab as the button on a minimalist or luxury surface reads louder than the page and cheapens it (a brief asking for "subtle gold accents" means the opposite). Match the CTA fill to the register: outline-that-fills-on-hover, a muted-chroma solid, or near-black/near-white with the accent kept to a hairline or the trailing icon (`premium-patterns.md` register-appropriate fill). A loud solid is for a loud register only.
- **Over-ornamented CTA on a refined page** — an arrow *and* a drawn underline *and* a border stacked on one control is three affordances doing one job; on an immersive or quiet-luxury surface it reads fussy. Strip to one, and let the hover carry the moment — the strongest hover echoes the page's signature gesture, not a stock arrow-nudge (`premium-patterns.md` §2).
- **Static decorative secondary** — a directional arrow, a coordinate, a meta label sitting as resting ornament beside a primary and never responding. Two exits, not three: fold it into an interaction (hidden at rest, revealed or animated on hover, with a touch-reachable fallback so a finger never loses it — `interaction-signatures.md`), or cut it. A directional arrow *appears or translates* on hover; it does not sit static as decoration. The redundant always-on coordinate beside the wordmark reveals on the wordmark's hover, or it goes.
- **Pill-shaped "New" / "Beta" badges** — try square badges, flags, or plain text labels.
- **Accordion FAQ sections** — try side-by-side lists, searchable help, or inline progressive disclosure.
- **3-card carousel testimonials with dots** — replace with masonry walls, embedded social posts, or single rotating quotes.
- **Pricing table with 3 towers** — highlight the recommended tier with color and emphasis, not extra height.
- **Avatar circles exclusively** — try squircles or rounded squares.
- **Light/dark toggle as sun/moon switch** — try a dropdown, system preference detection, or settings integration.
- **Footer link farm with 4 columns** — focus on main paths and legally required links.
- **Long list as bare rows** — >5 items with a hairline under each is the laziest layout. Reach for grouped chunks (3 clusters, one soft divider each), a 2-col card grid (spec name + display value + one-line why), tabs/accordion for categorisables, scroll-snap pills, or featured-vs-rest (3–4 hero specs large, the rest behind a disclosure). The 10-row spec table with `border-b` on every row is the canonical fail.
- **Emoji or hand-rolled SVG paths as icons** — one icon family per page (Phosphor, Radix, Tabler, HugeIcons), standardized stroke width, missing glyph → compose from primitives or add a second library, never draw paths from scratch.
- **Trendy-component-kit sameness** — beams, sparkles, spotlight cards, animated-gradient heroes, 3D-tilt cards dropped in from Aceternity / Magic UI / Cult unmodified. The 2026 AI-landing-page monoculture; judges flag it on sight. Override: scaffold from the kit, then restyle past its defaults — font, gradient, motion timing, color (see `inspiration.md`).
- **Edge-to-edge sticky navbar glued to the top** — the default chrome; consider a floating island nav (glass pill, `w-max` centered), a morphing hamburger, or a full-screen overlay with staggered reveal (`premium-patterns.md` navigation pattern).

## Output discipline

The DESIGN.md is long-form — eight prose sections plus YAML. Truncation is the highest-frequency way a high-effort plan ships as a half-empty file. Two banned-phrase categories make truncation visible and stoppable.

**Banned in code blocks** (any token group, any DESIGN.md fragment, any CSS sample):

- `// ...`, `// rest of code`, `// implement here`, `// TODO`, `/* ... */`, `// similar to above`, `// continue pattern`, `// add more as needed`
- bare `...` standing in for omitted tokens, fragments, or rule sets
- `[remaining tokens similar]`, `[other shadows similar]`, `[etc.]`

**Banned in prose** (DESIGN.md sections, anti-pattern explanations, reasoning blocks):

- "for brevity", "the rest follows the same pattern", "similarly for the remaining"
- "and so on" used to replace content, "I'll leave that as an exercise"
- "let me know if you want me to continue", "I can provide more details if needed"
- "[remaining sections similar]" — the canonical AI-truncation tell

**Banned structural shortcuts**:

- Outputting a token-namespace skeleton when the request is for full DESIGN.md
- Showing the first and last sections while skipping the middle
- Describing what a section *would* contain instead of writing it
- Ending mid-section without the continuation marker

**Continuation marker** for legitimate token-ceiling splits: finish at a clean section boundary, then end with `[PAUSED — N of 8 sections complete. Send "continue" to resume from: <next section name>]`. On `continue`, pick up exactly there with no recap, no rewrite, no compression. The marker is the only acceptable form of split output.
