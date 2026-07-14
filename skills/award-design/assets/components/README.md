# Award component library

Real, drop-in, production-grade components the model **composes** into a build — not prose describing what winners did. Each is derived from a specific award winner, framework-agnostic (vanilla JS + CSS custom properties, GSAP/Lenis used only when present), token-driven so it adopts the build's `DESIGN.md` palette, and ships accessible + reduced-motion-safe + perf-budgeted by construction.

This is the studio model: a curated palette of ingredients that already win, so the model can only pick a sub-optimal *combination*, never a bad ingredient. Composition (which 3–5 fit this world, in restraint) stays the model's job under the existing forcing; the human gives the composition verdict.

## The token contract

Every component reads CSS custom properties with sensible fallbacks, so it works standalone AND adopts the build's tokens when the `DESIGN.md` defines them. Never hardcode a brand value; read the token, fall back to a neutral default.

| Token | Role | Fallback |
|---|---|---|
| `--ad-accent` | the one saturated accent (active/hover) | `oklch(62% 0.2 25)` |
| `--ad-ink` | primary text/foreground | `oklch(96% 0 0)` |
| `--ad-ground` | page ground | `oklch(14% 0.01 260)` |
| `--ad-ground-2` | raised surface | `oklch(18% 0.01 260)` |
| `--ad-font-display` | display face | `inherit` |
| `--ad-font-mono` | mono/label face | `ui-monospace, monospace` |
| `--ad-ease-signature` | the build's signature easing | `cubic-bezier(.16,1,.3,1)` |
| `--ad-ease-strike` | fast attack/settle | `cubic-bezier(.7,.02,.28,1)` |
| `--ad-dur-reveal` | reveal duration | `800ms` |
| `--ad-dur-base` | control duration | `420ms` |

A build maps its `DESIGN.md` tokens onto these once (an alias block), or sets them directly. Components never invent color/type.

## Quality floor — non-negotiable, verified per component

- **Content-visible at rest** — the resting DOM is fully legible with no JS and with `prefers-reduced-motion: reduce`; motion is added, never required to read. No blackout if the script dies.
- **`prefers-reduced-motion: reduce`** — every component degrades to its finished state instantly (no transform/opacity animation, scrubbed media becomes a static poster).
- **A11y** — semantic elements, `:focus-visible`, focus order preserved, no keyboard trap; hover-revealed content reachable under touch; ARIA only where it earns it.
- **Perf** — animates only `transform`/`opacity`/`filter`; no layout thrash; observers disconnect when done; rAF loops pause on `visibilitychange` and `IntersectionObserver` off-screen.
- **Compositor-clean** — pointer/scroll-tracked layers are promoted, no per-frame paint (the moving-window law).
- **Dependency-optional** — vanilla by default; if a component can use GSAP/Lenis it detects `window.gsap`/`window.Lenis` and enhances, else falls back to WAAPI/CSS.

## Manifest

`manifest.json` lists every component: `id`, `file`, `winner` (the site it's derived from), `archetypes` (where it fits), `tokens` (which it reads), `deps` (optional libs it enhances with), `whenToUse`, `init` (the exported init signature). The model reads the manifest to compose; it imports only the components its recipe names.

## Init contract

Each component exports `init(root, opts)` — idempotent, returns a `{ destroy() }` handle, scopes to `root` (default `document`), and is a no-op under `reduce` beyond applying the finished state. Components self-register nothing global except their one namespaced stylesheet (injected once, `id="ad-<component>-css"`).
