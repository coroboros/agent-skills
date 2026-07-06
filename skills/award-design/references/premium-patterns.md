# Premium Patterns

A library of concrete component techniques that lift a design from "template with nice fonts" to agency-tier execution. Each pattern is implementation-ready and traces to a specific failure mode it solves. Cross-cutting across archetypes — load this when component architecture matters.

## When to load this

- While committing the universe — these patterns inform the component definitions in the DESIGN.md
- As you build under the universe — when components feel generic and a concrete technique is needed
- When auditing existing UI through `audit-rubric.md` and a Hierarchy / Spacing / Color score sits below 8
- When the brief calls for archetypes that benefit most: Corporate Luxury, Spatial Organic, Bento (motion-engine variant), Bold/Maximal

## 1. Doppelrand — the Double-Bezel

Premium components do not sit flat on the background. They look like physical, machined hardware — a glass plate sitting in an aluminum tray. The technique nests two enclosures with concentric radii and complementary surface treatments.

### Architecture

- **Outer shell**: subtle background fill (`bg-black/5` light, `bg-white/5` dark), hairline outer border (`ring-1 ring-black/5` or `border border-white/10`), padding around the inner core (e.g., `p-1.5` or `p-2`), large outer radius (e.g., `rounded-[2rem]`)
- **Inner core**: distinct background color, optional inner highlight (`shadow-[inset_0_1px_1px_rgba(255,255,255,0.15)]`), mathematically calculated smaller radius for concentric curves: `rounded-[calc(2rem-0.375rem)]` (outer radius minus shell padding)

### Token mapping

```yaml
# DESIGN.md fragment
rounded:
  shell-lg: "32px"
  core-lg: "calc(32px - 6px)"
borderWidths:
  hairline: "1px"
opacity:
  shell-fill-light: "0.05"
  shell-fill-dark: "0.05"
  shell-border: "0.05"
shadows:
  inner-highlight: "inset 0 1px 1px rgba(255, 255, 255, 0.15)"
```

### Why it works

Single-radius cards read as flat tiles. Concentric radii read as physical objects with material thickness. The inner highlight simulates ambient light catching the upper edge — the eye perceives depth without explicit drop shadow. Particularly powerful in Spatial Organic (glass surfaces), Corporate Luxury (premium product cards), and Bento 2.0 (motion-engine cards).

### Anti-pattern

A flat card with `border: 1px solid #EAEAEA` and no inner treatment. This reads as default Tailwind output — exactly the failure mode this pattern eliminates.

## 2. Button-in-Button — the Nested Trailing Icon

Trailing icons (arrows, chevrons) on premium CTAs do not sit naked next to the label. They live inside their own circular wrapper, flush with the button's right inner padding, scaled visually distinct from the text.

### Architecture

- **Primary button**: fully rounded pill (`rounded-full`), generous padding (`px-6 py-3`), label in display weight
- **Inner icon wrapper**: `w-8 h-8 rounded-full bg-black/5` (light) or `bg-white/10` (dark), `flex items-center justify-center`, sits flush with button's right inner padding
- **Icon**: ultra-light stroke weight (Phosphor Light, Remix Line), centered inside wrapper

### Hover physics

- Whole button scales down on press: `active:scale-[0.98]`
- Inner icon wrapper translates and scales on hover: `group-hover:translate-x-1 group-hover:-translate-y-[1px] group-hover:scale-105`
- Creates internal kinetic tension — the icon "wants" to leave the button

### Token mapping

```yaml
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.surface}"
    rounded: "{rounded.full}"
    padding: "12px 24px"
  button-primary-hover:
    backgroundColor: "{colors.primary-hover}"
```

The trailing icon nesting is documented in prose because it's a structural pattern, not a single-token override.

### Why it works

Naked arrow icons next to text read as "icon kerned next to label" — a typographic afterthought. The nested wrapper signals the icon as a discrete affordance with its own micro-state. The hover physics close the loop: the user feels the click before pressing it.

### Register-appropriate fill

The button's *fill* is chosen for the page's register, not maxed for contrast. On a refined minimalist or luxury surface, a saturated color-block CTA — a solid ochre slab, a bright accent brick — reads louder than the page and cheapens it; a brief that says "subtle gold accents" means exactly this. The luxury CTA is a thin outline that fills on hover, a low-chroma solid at the accent's *muted* end, or near-black / near-white with the accent kept to a hairline or the trailing icon — never a saturated slab. Match the CTA's loudness to the page's restraint; the accent is punctuation, not a highlighter. (Reach for a louder solid only where the register is loud — Bold/Maximal, a Gen-Z launch.)

### The immersive / luxury CTA drops the ornament

The nested trailing icon (above) and a drawn underline are SaaS-and-product moves — legible affordances for a busy page. On an immersive or quiet-luxury surface they read as fuss: an arrow *and* an underline *and* a border stacked on one control is three affordances doing one job. Strip to one. The refined CTA is a word or two in a thin outline (or bare, with a hairline), and its *hover* carries the moment — and the strongest hover **echoes the page's signature gesture**, not a generic slide. If the signature rakes warm light across a black object, the CTA's hover rakes the same light across its label; if the world is ink-in-water, the fill blooms like ink. The button that moves like the world coheres; the button with a stock arrow-nudge is another site's control dropped in. Keep the fill inside the shape (`anti-patterns.md` Technical — unclipped fills), verified hover→leave (`preflight.md` §8).

## 3. Eyebrow Tags

Section openers benefit from a microscopic typographic preamble — a pill-shaped tag in monospace or wide-tracked sans, signaling category before the headline lands.

### Architecture

- Pill shape: `rounded-full`
- Compact padding: `px-3 py-1`
- Tiny type: `text-[10px]` or `text-[11px]`
- Uppercase with wide tracking: `uppercase tracking-[0.2em]`
- Medium weight: `font-medium`
- Subtle background: `bg-foreground/5` or `bg-accent/10`
- Sits 24–32px above the headline

### Token mapping

```yaml
typography:
  eyebrow:
    fontSize: "10px"
    fontWeight: 500
    letterSpacing: "0.2em"
    textTransform: "uppercase"
components:
  eyebrow-tag:
    typography: "{typography.eyebrow}"
    backgroundColor: "{colors.foreground-subtle}"
    rounded: "{rounded.full}"
    padding: "4px 12px"
```

### Why it works

Eyebrow tags solve the "hierarchy stutter" problem — when the first heading on a section needs to land but lacks scaffolding above it. The tag pre-frames the section ("FEATURES", "PRICING", "MANIFESTO"), so the headline arrives with weight rather than as the first word of the paragraph.

### Anti-pattern

The Meta-Label trap — labels like "SECTION 01", "QUESTION 05", "ABOUT US" without semantic value. Eyebrow tags carry meaning ("PRINCIPLES", "OUR APPROACH", "RECENT WORK"); meta-labels carry index numbers. The numbered version reads cheap.

## 4. Hero Architecture — the 2-Line Iron Rule

The H1 is the page's first visual decision. LLMs default to narrow containers and 6-line wrapped headlines, which signal "AI output" instantly. The remedy:

### Container width

- Use ultra-wide containers for the H1: `max-w-5xl`, `max-w-6xl`, or `w-full`
- Allow words to flow horizontally before wrapping
- The H1 must NEVER exceed 2–3 lines; 4-, 5-, or 6-line wraps are catastrophic

### Scaling

- `clamp(3rem, 5vw, 5.5rem)` is the sweet spot for SaaS marketing
- For luxury and editorial, push higher: `clamp(4rem, 7vw, 8rem)`
- For brutalist and bold/maximal: `clamp(5rem, 10vw, 15rem)`

### CTA pairing

- Two CTAs maximum below the headline — primary and secondary
- Primary uses the Button-in-Button pattern
- Button text contrast is non-negotiable: dark background → off-white text, light background → near-black text

### Hero layout options

Pick one based on Density / Variance scores from the Atmosphere Calibration:

1. **Cinematic Center** (Density 2–4, Variance 2–4): text centered, massive width, two CTAs below, full-bleed background image with subtle radial wash
2. **Artistic Asymmetry** (Density 4–6, Variance 6–8): text offset left, artistic floating image overlapping from bottom right
3. **Editorial Split** (Density 4–6, Variance 4–6): text left, image right, massive negative space between

### Hero Scale taxonomy

Three scales fit the brief, archetype, and atmosphere band. Pick before scaling type — switching scale mid-design forces a token rewrite.

| Scale | clamp() | Best for | Feels |
|---|---|---|---|
| **Mini Minimalist** | `clamp(2.5rem, 4vw, 4rem)` | SaaS, product pages, dashboards-adjacent marketing | Quiet, considered, restrained |
| **Mid Editorial** | `clamp(4rem, 7vw, 8rem)` | Editorial, Corporate Luxury, premium narrative | Confident, magazine-grade, intentional |
| **Giant Statement** | `clamp(5rem, 10vw, 15rem)` | Brutalist, Bold/Maximal, Immersive cinematic | Loud, declarative, type-as-art |

Hero Scale is independent of Hero Architecture — a Cinematic Center hero can run Mini Minimalist for restraint or Giant Statement for impact. The pairing is a deliberate choice, not a default.

### Banned in hero

Stamp/badge icons floating on the headline; pill tags directly under the H1 (use eyebrow tags ABOVE instead); raw stats / numbers as hero content (those belong in the Interest section).

## 5. Mobile Collapse Mandates

Asymmetric layouts above the `md` breakpoint MUST collapse aggressively below 768px. Half the Awwwards Usability score lives on mobile; layouts that "work technically" but visibly drift on phones tank scores.

### Universal collapse rules

- All asymmetric `col-span` overrides reset to `col-span-1` below `md`
- Layouts default to `w-full px-4 py-8` on viewports under 768px
- All `transform`-based rotations and negative-margin overlaps are removed below `md` — they cause touch-target conflicts
- `min-h-[100dvh]` replaces `h-screen` everywhere — `h-screen` jumps catastrophically on iOS Safari URL-bar toggle
- Grid tracks holding images use `minmax(0, 1fr)` — bare `1fr` resolves to `minmax(auto,1fr)` and a large image forces horizontal scroll on phones. Display headlines carry `overflow-wrap: anywhere`. Page-level clipping is `overflow-x: clip`, never `hidden` (kills `position: sticky`). Sweep 320–1920px.

### Layout-specific collapse

- **Asymmetrical Bento**: falls back to single-column stack with generous vertical gaps (`gap-6`)
- **Z-Axis Cascade**: rotations and overlaps disappear; vertical stack with standard spacing
- **Editorial Split**: full-width vertical stack, typography block on top, interactive content below

### Verification checklist

Before shipping, confirm at viewport widths 375px (iPhone SE), 414px (iPhone 14), 768px (iPad portrait) — the mobile-collapse subset; the pre-flight browser proof runs 375/768/1440:

- No horizontal scroll bars
- No overlapping touch targets (44×44 minimum)
- All text readable without zoom
- All CTAs visible above fold

## 6. Performance Locks

Three concrete rules that prevent the highest-impact mobile performance failures.

### Magnetic micro-physics

When implementing magnetic-button or cursor-following effects, NEVER use React `useState` for the continuous animation. Use exclusively Framer Motion's `useMotionValue` and `useTransform` outside the React render cycle. Each `useState` update triggers a re-render of the component tree; on a continuous mouse-move, this collapses mobile frame rate.

```javascript
// Wrong — re-renders 60×/second on mouse move
const [pos, setPos] = useState({ x: 0, y: 0 });

// Right — bypasses React render cycle
const x = useMotionValue(0);
const y = useMotionValue(0);
useEffect(() => {
  const handleMove = (e) => { x.set(e.clientX); y.set(e.clientY); };
  window.addEventListener('mousemove', handleMove);
  return () => window.removeEventListener('mousemove', handleMove);
}, []);
```

### Backdrop-blur scope

`backdrop-filter` is GPU-expensive. Apply it ONLY to fixed or sticky elements — navbars, modal overlays, command palettes. Never to scrolling content or large content areas. Mobile Safari drops to 15–20fps on a scrolling page with full-section `backdrop-blur`.

### Perpetual animation isolation

Any infinite loop or perpetual micro-animation MUST be:

1. Memoized via `React.memo`
2. Isolated in its own microscopic Client Component (`"use client"` at the top)
3. Never trigger re-renders in the parent layout
4. Use `transform` and `opacity` exclusively — no layout-triggering properties (`top`, `left`, `width`, `height`)

For lists with `staggerChildren`, the parent (`variants`) and children MUST live in the identical Client Component tree. If data is fetched asynchronously, pass it as props to a centralized Parent Motion wrapper. Mismatched trees break the orchestration silently.

### Grain and noise overlays

Apply procedural noise filters EXCLUSIVELY to fixed `pointer-events: none` pseudo-elements (e.g., `position: fixed; inset: 0; z-index: 50; pointer-events: none`). Never to scrolling containers — continuous GPU repaints collapse mobile frame rate. Static PNG grain overlays read as the AI version; procedural Canvas or WebGL noise is the credentialed alternative.

## 7. Window Chrome — real captures only

CSS-rebuilt browser bars and traffic-light dots are one of the strongest AI tells, and they contradict the fake-screenshot axiom (`anti-patterns.md` axiom #14) — chrome drawn in divs promises a product the page cannot show. Product UI ships as a real capture inside a plain elevated frame: a radius, a shadow, a 1px border — no fake chrome. When no capture exists, ship an honest labeled placeholder sized to the final aspect ratio per `imagery.md`.

## 8. Eyebrow + Headline + CTA — the section opener

Section openers benefit from a three-element rhythm:

1. Eyebrow tag (24–32px above headline)
2. Headline (the section's primary message, 2 lines max)
3. One CTA below — Button-in-Button pattern, never two competing CTAs in a section opener

Section spacing pulls from `spacing.section-*` extension tokens — `py-24` (96px) minimum on marketing pages, `py-32` to `py-48` (128–192px) on luxury and editorial; a cockpit-dense build (Density 7+ in the DESIGN.md) follows its calibrated tighter band instead.

## 9. Liquid Glass Refraction

Glass surfaces sit flat by default — a translucent panel with `backdrop-filter: blur()` reads as "blurred backdrop", not as glass. The Apple WWDC 2025 "Liquid Glass" register adds a 1px inner highlight that simulates the upper edge catching ambient light. The eye perceives refraction without an explicit highlight gradient.

### Architecture

- **Surface**: `bg-white/4` (dark mode) or `bg-black/3` (light mode), `backdrop-filter: blur(24px) saturate(1.2)`
- **Hairline outer**: `border border-white/10` (dark) or `border border-black/8` (light)
- **Inner highlight**: `shadow-[inset_0_1px_0_rgba(255,255,255,0.12)]` — the edge of the glass plate
- **Outer lift** (optional): `shadow-[0_20px_40px_-15px_rgba(0,0,0,0.3)]` for elevation off the canvas

### Token mapping

```yaml
borderWidths:
  glass-hairline: "1px"
shadows:
  glass-inner-highlight: "inset 0 1px 0 rgba(255, 255, 255, 0.12)"
  glass-outer-lift: "0 20px 40px -15px rgba(0, 0, 0, 0.3)"
opacity:
  glass-surface-light: "0.04"
  glass-surface-dark: "0.04"
  glass-border-light: "0.08"
  glass-border-dark: "0.10"
```

### Why it works

A flat translucent panel reads as a digital effect. The inner highlight tells the eye "this is a physical material with thickness and a top edge." Pair with the Doppelrand technique (pattern 1) for the highest premium register — a glass plate sitting in a frame, both with concentric radii.

### Anti-pattern

`backdrop-filter: blur()` applied to scrolling content. Continuous GPU repaints collapse mobile frame rate (Safari drops to 15–20fps). Glass surfaces apply only to fixed or sticky elements (navbars, modal overlays, command palettes) — never to scrolling cards. See `production-hardening.md` and pattern 6 (Performance Locks). Ship the `prefers-reduced-transparency` solid-fill fallback — glass with no fallback fails the users who asked for less.

Particularly powerful in Spatial Organic (the canonical context), Corporate Luxury (premium product cards on dark backgrounds), and any modal/command-palette surface across archetypes.

## 10. Inline Typography Images

Embed small, contextual photos directly between words or letters in a headline. The images sit inline with text at type-height, with rounded corners, acting as visual punctuation. The word and the image share the same baseline; the image *is* a glyph in that line.

### Architecture

```css
.hero-text img.inline-photo {
  display: inline-block;
  height: 1em;
  width: auto;
  aspect-ratio: 3 / 2;
  object-fit: cover;
  border-radius: 0.2em;
  vertical-align: baseline;
  margin-inline: 0.1em;
}
```

```html
<h1 class="hero-text">
  We shape <img class="inline-photo" src="/seed-1.jpg" alt="" /> digital
  spaces for <img class="inline-photo" src="/seed-2.jpg" alt="" /> brands.
</h1>
```

### Token mapping

```yaml
typography:
  hero-inline:
    fontSize: "{typography.hero}"
    lineHeight: "1.05"
aspectRatios:
  inline-photo: "3 / 2"
borderWidths:
  inline-photo-radius: "0.2em"  # relative to type size
```

### Why it works

A headline carrying an inline photo demonstrates that the system *plans for* imagery as part of the typographic hierarchy — not as decoration around it. The image becomes part of the reading experience instead of competing with it. Best for high-Variance archetypes (Editorial, Bold/Maximal, Experimental, Bento at motion-engine register). Avoid on Minimalist or Corporate Luxury where it competes with whitespace.

### Anti-pattern

Images that overlap text or float free of the line baseline. Once the image stops behaving like a glyph, the technique breaks — the eye reads "design element" rather than "punctuation". The line height must accommodate the image without breaking the text rhythm above and below.

## 11. Perpetual Micro-Interactions — the Motion ≥ 5 mandate

When the calibrated Motion atmosphere is **5 or higher**, ship at least one perpetual micro-interaction on a hero or signature component. A page that scores Motion 7 in DESIGN.md but ships only opacity reveals reads as "scored ambitious, designed cautious" — judges see the gap immediately.

### Choose one (or layer two) per signature surface

- **Pulse** — opacity or scale breathing on a status dot, live-data indicator, or accent badge (cycle 1.6–2.4s)
- **Typewriter** — caret blink + character reveal on a placeholder, command input, or kinetic headline (caret 530ms blink, characters 40–80ms each)
- **Float** — subtle Y-axis drift on a hero asset or floating panel (1.5–3% of viewport height, cycle 4–8s, ease-in-out)
- **Shimmer** — gradient sweep across a skeleton, loading state, or premium card edge (cycle 2–3s, low-opacity gradient)
- **Orbit / Drift** — slow ambient gradient orb motion on Spatial Organic backgrounds (cycle 15–25s, large radius, opacity 0.15–0.25)

### Performance lock (mandatory)

Per pattern 6, every perpetual animation **must** be:

1. Memoized via `React.memo`
2. Isolated in its own microscopic Client Component (`"use client"`)
3. Animating `transform` and `opacity` only — never `top`, `left`, `width`, `height`, `filter` (except `backdrop-filter` on a fixed layer)
4. Wrapped in a `prefers-reduced-motion: reduce` swap that pauses the loop and serves a static frame

### Token mapping

```yaml
motion:
  duration-pulse:    1800ms
  duration-float:    6000ms
  duration-shimmer:  2400ms
  duration-orbit:    20000ms
  ease-perpetual:    cubic-bezier(0.45, 0, 0.55, 1)  # gentle ease-in-out
```

### Why it works

One choreographed perpetual motion on a hero element keeps the page "alive" without the scattered-micro-animations failure mode. The motion proves the page is a designed surface, not a static screenshot — the signature moment of axiom #8 made continuously legible. Particularly powerful on Bento (motion-engine variant), Spatial Organic (ambient orbs), Bold/Maximal (kinetic type).

### Anti-pattern

Three or four perpetual motions running together — pulse on the badge, typewriter in the input, shimmer on the card, orbit in the background. The eye loses anchor; the page reads as visual chaos rather than craft. One perpetual motion per fold; two only when they reinforce the same focal point.

## 12. Navigation as a designed component

The nav is the first component judged — and the default edge-to-edge sticky bar with a hairline border is the template fingerprint. Three premium moves:

- **Floating island** — a glass pill detached from the edges: `mt-6 mx-auto w-max rounded-full`, content-width, never viewport-width
- **Morphing hamburger** — the icon morphs to an X and opens a full-screen overlay with staggered mask reveals
- **Inherited surface** — the nav's surface inherits the section behind it instead of carrying its own chrome

Whatever the move: one line at desktop, ≤80px tall, active state marked, instant focus rings.

### Token mapping

Bind the nav height to `heights.nav` and its transitions to `motion.*` extension tokens — never ad-hoc values in the nav component.

### Anti-pattern

The AI-nav fingerprint — wordmark hard-left, 4–5 inline text links, CTA button hard-right, 1px hairline border-bottom (`anti-patterns.md` AI Tells → Layout). Break at least one element: placement, container, or divider.

## Cross-references

Read alongside `foundations.md` (typography systems, OKLCH, animation toolkit, spring physics canonical values), `production-hardening.md` (mobile performance, iOS Safari traps, backdrop-filter scope), `audit-rubric.md` (these patterns lift Hierarchy and Spacing scores by 1–2 points each), `anti-patterns.md` (each pattern here solves a specific anti-pattern), `spatial-organic.md` (Liquid Glass is the canonical context).
