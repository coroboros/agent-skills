# Modern-web baseline — the code discipline AI skips

Award winners are not separated from AI-generated code by spectacle. They are separated by the **baseline discipline of modern web** — the CSS/HTML/JS/React best practices a working studio applies by default and a model skips. The reference article puts it plainly: *"one unforgettable signature moment, executed with precision across every device, loading in under two seconds. Everything else is decoration."* Precision is this file.

These are **best practices to adopt**, not tells to ban — the opposite list from `anti-patterns.md`. Adopt: OKLCH, `rem` + fluid `clamp()`, CSS custom properties, factorization, modern CSS primitives, semantic HTML, GPU-composited motion. Ban (separate list, `anti-patterns.md`): native controls, `not-allowed`, the AI-purple gradient, `#000`/`#fff`. This file is the adopt side; the code-craft pass (`code-review.md`) enforces it.

Loads at the build step with `foundations.md` (the deep implementation is there — this file is the discipline and the adopt-vs-guard law, not a re-derivation).

## The adopt-vs-guard law — follow current Baseline, never memory

A feature's adoption tier is its **current Baseline status**, and Baseline moves. Verify status before adopting anything not in the table below — `find-docs` / `context7-cli` against web.dev Baseline or MDN — and never assume from training memory (a model's "it's supported" is stale). Three tiers:

- **Widely available → adopt unguarded.** The default.
- **Newly available → progressive enhancement.** Ship it, but the resting state is correct *without* it (it degrades or is feature-detected); ~30 months from Newly to Widely, so a Newly feature is not an unguarded default yet.
- **Not Baseline → progressive enhancement only.** Behind `@supports` or a JS feature-detect, with a content-complete fallback.

| Feature (mid-2026) | Baseline | Ship it | Source |
|---|---|---|---|
| `oklch()` authoring colour | **Widely** (since 2023) | adopt, unguarded | web.dev Baseline · MDN |
| Container queries | **Widely** | adopt, unguarded | chrome.dev/css-wrapped-2025 |
| `:has()`, `@property`, subgrid | supported, major browsers | adopt (re-verify current) | reference article §5.1 |
| GPU-composited props: `transform` `opacity` `filter` (+`backdrop-filter`) | — | animate **only** these for 60fps | developer.chrome.com |
| `content-visibility: auto` | **Newly** (2025-09) | adopt — no-ops where unsupported | web.dev Baseline |
| Relative colour `oklch(from …)`, `linear-gradient(in oklch …)` | **Newly** (2024-09) | PE — author a cascade fallback | MDN · developer.chrome.com |
| Same-document View Transitions | **Newly** (2025-10) | PE — JS feature-detect (`startViewTransition` guard) | web.dev |
| Scroll-driven `animation-timeline` | **not Baseline** (Firefox flag-gated) | PE — content visible at base, motion inside `@supports` | article §3.2 (`motion-palette.md`) |
| Cross-document View Transitions, `animation-trigger` | **not Baseline** | PE / future primitive | web.dev · article §8 |
| anything not listed | **unknown** | verify Baseline first, then place it | `find-docs` |

## Factorize — define once, reference

The single strongest code-quality signal, and the one AI code most consistently misses. Every repeated value — colour, spacing, radius, duration, font, breakpoint — is a CSS custom property (or a design token) defined once and referenced; a literal that appears twice is a bug the moment the two must change together (`~/.agents/rules/behavior.md` single-source-of-truth). Derive where the platform lets you: a brand ramp flows from one `--base-color` via relative colour and `color-mix()` (`oklch(from var(--base) l c calc(h + N))`) so a rebrand edits one line — but relative colour is Newly, so the derived output carries a cascade fallback. Keep `--background` and `--text` as their own base variables rather than deriving everything from one. Token governance is `/design-system`'s job after the build; author to it here.

## Units — rem and fluid scales

Type and spacing ride a **fluid `rem` scale with `clamp()`**, not px breakpoints (reference article §2.1, §2.4 — the type ramp and spacing tokens; already in `foundations.md`). `rem` scales with the user's root font-size; px spacing does not, and px type breaks reader zoom. px is correct in bounded places: `1px` hairline borders, sub-pixel decoration, and the **WCAG 2.2 SC 2.5.8 24×24 CSS-px minimum interactive target** — the one spot where CSS px is the normative unit (W3C WCAG 2.2).

## Colour — OKLCH

Author colour in **OKLCH** (Widely available; adopt unguarded). Its `L` is *perceived* lightness, so lightening is predictable and hue rotates without side effects — the reason it is the recommended space for programmatic colour (MDN, developer.chrome.com). Derive neutrals and ramps from the brand token at low chroma (`foundations.md` OKLCH). Translucent overlays, borders, scrims, and glass stay `rgb(… / α)` / `rgba()` where an alpha-over-background composite is what you actually want — that is not a violation, it is the correct tool; the code-craft pass flags only *opaque* hardcoded colour (`code-review.md`).

## Semantic HTML + the accessibility floor

Native semantics first — the **first rule of ARIA**: a role on a `<div>`-as-button is a promise you also wrote the keyboard JS, so reach for the real element (`<button>`, `<nav>`, `<main>`) before a role (W3C ARIA APG). The legally load-bearing floor (EAA 2025 / EN 301 549 = WCAG **AA**): 4.5:1 / 3:1 contrast including on glass (SC 1.4.3), a visible focus indicator with no global `outline: none` (SC 2.4.7), 24×24 CSS-px targets (SC 2.5.8), `aria-live` for dynamic content. The 2px/3:1 focus-appearance (SC 2.4.13) and the reduced-motion swap basis (SC 2.3.3) are Level **AAA** — best-practice targets this skill still ships, above the legal minimum, not the minimum itself. The full imposed floor + code: `ship-ready-floor.md`, `foundations.md` Accessibility; debug with the `a11y-debugging` skill.

## Performance

Animate only the GPU-composited set (above); offscreen work goes behind `content-visibility: auto` and IntersectionObserver-gated lazy-load + dynamic import of heavy layers; images ship the AVIF > WebP > JPEG `<picture>` cascade; fonts preload + `font-display: swap` (reference article §5.4; `foundations.md`). The budget this skill holds — **LCP < 1.5s · CLS < 0.05 · INP < 100ms**, ≥55fps — is a deliberate **award-grade stretch**, tighter than Google's official "good" Core Web Vitals floor (LCP ≤ 2.5s · INP ≤ 200ms · CLS ≤ 0.1 at p75, web.dev/vitals); total transfer carries **no cap** — weight is phased instead (critical-path lean, heavy assets streamed behind a designed loader, `award-imperatives.md` #7), the model measured winners actually ship. State the stretch as the studio target it is, never as "Google's baseline." Deeper: the `web-perf` skill.

## React builds

Composition and factorization carry over: extract a component when markup repeats, keep motion values off the render cycle (`useMotionValue`/`useTransform`, not `useState` per frame — `anti-patterns.md` Technical), and lazy-load heavy client components. The current React/Next patterns are the `vercel-react-best-practices` and `vercel-composition-patterns` skills — resolve them by name when installed, the same ladder the heavy layers use (`SKILL.md`, truth sourcing).

## The AI-code gap (inference, confirmed on real builds)

No external source names the *code-level* AI tells, so this list is an inference from the baselines above — corroborated by what a code review of a generated build actually surfaces (inline literals in six scrims, px spacing off the scale, zero OKLCH, a native `<select>`, no `@supports` guard). Treat it as a checklist, not a cited fact:

- inline hex/px literals instead of tokens; the same value hardcoded in two places
- px spacing and type instead of a `rem` fluid scale
- opaque hex/`rgb()` instead of OKLCH
- `<div>` soup instead of landmarks and real controls
- missing `prefers-reduced-motion`, missing `@supports` guard on a non-Baseline feature
- repeated un-factored blocks; one generic fade-in on every element (`interaction-signatures.md`)
- a render loop or timer that never cleans up (`code-review.md` JS lifecycle)

The code-craft pass (`code-review.md`, preflight §9) is where these are caught mechanically.
