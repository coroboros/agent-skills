# Premium Patterns

A library of concrete component techniques that lift a design from "template with nice fonts" to agency-tier execution. Each pattern is implementation-ready and traces to a specific failure mode it solves. Cross-cutting across archetypes — load this when component architecture matters.

The patterns originate from the `Leonxlnx/taste-skill` library (Awwwards-tier UI generation) and have been adapted to align with the canonical Awwwards-FWA-CSSDA reference article and the Google DESIGN.md token system.

## When to load this

- During step 6 of the workflow (Produce DESIGN.md) — these patterns inform component definitions
- During step 7 (Design with intent) — when components feel generic and a concrete technique is needed
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
- Button text contrast is non-negotiable: dark background → white text, light background → dark text

### Hero layout options

Pick one based on Density / Variance scores from the Atmosphere Calibration:

1. **Cinematic Center** (Density 2–4, Variance 2–4): text centered, massive width, two CTAs below, full-bleed background image with subtle radial wash
2. **Artistic Asymmetry** (Density 4–6, Variance 6–8): text offset left, artistic floating image overlapping from bottom right
3. **Editorial Split** (Density 4–6, Variance 4–6): text left, image right, massive negative space between

### Banned in hero

Stamp/badge icons floating on the headline; pill tags directly under the H1 (use eyebrow tags ABOVE instead); raw stats / numbers as hero content (those belong in the Interest section).

## 5. Mobile Collapse Mandates

Asymmetric layouts above the `md` breakpoint MUST collapse aggressively below 768px. Half the Awwwards Usability score lives on mobile; layouts that "work technically" but visibly drift on phones tank scores.

### Universal collapse rules

- All asymmetric `col-span` overrides reset to `col-span-1` below `md`
- Layouts default to `w-full px-4 py-8` on viewports under 768px
- All `transform`-based rotations and negative-margin overlaps are removed below `md` — they cause touch-target conflicts
- `min-h-[100dvh]` replaces `h-screen` everywhere — `h-screen` jumps catastrophically on iOS Safari URL-bar toggle

### Layout-specific collapse

- **Asymmetrical Bento**: falls back to single-column stack with generous vertical gaps (`gap-6`)
- **Z-Axis Cascade**: rotations and overlaps disappear; vertical stack with standard spacing
- **Editorial Split**: full-width vertical stack, typography block on top, interactive content below

### Verification checklist

Before shipping, confirm at viewport widths 375px (iPhone SE), 414px (iPhone 14), 768px (iPad portrait):

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

## 7. Mac OS Window Chrome (mockup pattern)

For mocking software interfaces (dashboards, apps, command palettes) inside marketing pages, wrap the mockup in a minimalist container with a thin top bar containing three small light-gray circles. Replicates macOS window controls without overcomplicating.

```html
<div class="rounded-xl bg-white shadow-[0_20px_40px_-15px_rgba(0,0,0,0.05)]">
  <div class="flex items-center gap-1.5 border-b border-slate-200/50 px-4 py-3">
    <span class="h-3 w-3 rounded-full bg-slate-300"></span>
    <span class="h-3 w-3 rounded-full bg-slate-300"></span>
    <span class="h-3 w-3 rounded-full bg-slate-300"></span>
  </div>
  <div class="p-6"><!-- mockup content --></div>
</div>
```

The convention is so universally readable that it requires no caption. Every variant — colored circles, traffic-light circles, plain dots — works.

## 8. Eyebrow + Headline + CTA — the section opener

Section openers benefit from a three-element rhythm:

1. Eyebrow tag (24–32px above headline)
2. Headline (the section's primary message, 2 lines max)
3. One CTA below — Button-in-Button pattern, never two competing CTAs in a section opener

Section spacing pulls from `spacing.section-*` extension tokens — `py-24` (96px) minimum on marketing pages, `py-32` to `py-48` (128–192px) on luxury and editorial.

## Cross-references

Read alongside `foundations.md` (typography systems, OKLCH, animation toolkit), `production-hardening.md` (mobile performance, iOS Safari traps), `audit-rubric.md` (these patterns lift Hierarchy and Spacing scores by 1–2 points each), `anti-patterns.md` (each pattern here solves a specific anti-pattern).

## Source

Patterns adapted from `github.com/Leonxlnx/taste-skill` (taste-skill, soft-skill, gpt-tasteskill, brutalist-skill — MIT). Calibrated against the article's anti-pattern section and aligned to the Google DESIGN.md token namespaces.
