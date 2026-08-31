# Ship-Ready Floor

The completeness floor under every build. It sits *below* the signature moment, never above it — the floor is what keeps a built page from reading as a prototype; the signature moment is what makes it memorable. Three tiers, sorted by cost and risk:

- **Impose** — cheap, pure upside, no design cost. Auto-authored during the build and enforced by the review filter.
- **Offer** — real production weight that can smother a small build. Surfaced as one opt-in question, gated on brief / archetype. Never auto-built.
- **Template** — structured data the designer fills in. Provided as an archetype template, opted into.

Most of the Impose tier already lives in `foundations.md` UX Quality + Accessibility; this file names and tiers it so the filter can cite one floor. It organizes those rules, it does not re-derive them.

## Impose — the craft floor (cheap, pure upside)

Present on every build, gated. None competes with the design; all is floor. An item the harness genuinely blocks (no raster tooling for the OG image, no domain for the canonical on a local build) is declared in the pre-flight verdict, never faked and never silently dropped.

- **The no-JS floor** — the page's resting state renders its content. Initial hidden states (`opacity: 0` reveals, gated sections) are applied by JS only (`html.no-js` → visible; a boot script swaps the class), never in base CSS; a canvas/3D hero carries a static fallback layer (poster or CSS composition) shown when JS is absent. A module build opened over `file://` runs zero JS — a base-CSS-hidden page ships a blackout to anyone the JS fails for.
- **Full interactive cycles — the 8-state contract** — every interactive element ships its applicable states: default, hover, focus-visible, active, disabled, loading, empty/error, success. Async surfaces carry loading (skeletons matching the final layout, not a spinner), empty, and error states; `:active` gives tactile press feedback (`-translate-y-[1px]` or `scale-[0.98]`). Async results are announced (`aria-live="polite"` / `role="status"`). A control with only a resting state is unfinished. Prove it by construction where cheap: a throwaway preview that forces each state via classes makes the contract decidable instead of claimed.
- **Contrast on controls** — buttons and form fields meet WCAG AA in every state (rest, hover, disabled, focus). Glassmorphic and tinted controls are the usual failures — test them.
- **Cursor-affordance discipline** — `pointer` on actionable, `text` on text, `default` elsewhere. A disabled control drops opacity and keeps `cursor: default` — **never `not-allowed`**: the OS "no-entry" icon defaces a premium surface (a `div` button with a default cursor reads as broken, but the native blocked cursor reads worse).
- **Form controls uplifted, never native** — `<select>`, checkbox, radio, and every other control ship `appearance: none` + a custom affordance (a drawn chevron, a styled box/tick). Raw native OS chrome inside a bespoke surface is the tell the whole build otherwise avoids.
- **Colour in OKLCH, sizing in rem** — opaque authored colour is `oklch()` / relative-color `oklch(from …)` (`foundations.md`); translucent borders, scrims, and glass may stay `rgb(… / α)` where the alpha is the point (`optical-craft.md`). px is for borders, hairlines, and touch-target minimums only, spacing and type ride the rem scale. Opaque hex mid-file and px spacing are drift the code-craft pass flags (`code-review.md`).
- **One coherent interaction substrate** — a single hover/reveal vocabulary (underline reveal, contained figure lift, color shift) applied to *every* interactive element at low amplitude; mixed or absent hover behaviours read unfinished, and a page inert past the hero reads as a prototype (`interaction-signatures.md`).
- **Skip-link + `:focus-visible`** — a keyboard skip-to-content link and a custom, visible focus ring on every interactive element. Never `outline: none` without a replacement.
- **Semantic HTML + landmarks** — `<header> <nav> <main> <footer>`, one `<h1>`, ordered headings. No `<div onClick>` navigation.
- **Canonical + hreflang** — a `<link rel="canonical">`; `hreflang` when the site is localized.
- **Favicon + `icon.svg` + OG image** — a real favicon, an SVG icon, and an Open Graph image so shared links render.
- **`theme-color`** — light and dark `theme-color` meta so mobile chrome matches the surface.
- **`prefers-reduced-motion`** — durations zeroed or the motion removed; the element and its end state never are. A static opacity state is fine, a blank page is not.
- **Focus ring at t=0** — `:focus-visible` indicators appear instantly; transitioning them in leaves keyboard users unmarked mid-animation.
- **Reveal safety** — scroll/entry reveals *enhance* an already-visible default; hidden tabs and headless renderers never fire IntersectionObserver, and a reveal that gates visibility ships blank sections there. (The no-JS floor's JS-alive sibling.)

Detail and code for each: `foundations.md` UX Quality + Accessibility. This list is the filter's checklist; that file is the implementation.

## Offer — opt-in, gated on brief / archetype (never auto-built)

Real production weight. Each can pull effort toward "compliant" and away from the design, so each is surfaced as a question, never imposed. Offer it; build it only on a yes.

- **Force-static / prerender** — for catalog and content archetypes (Bento product pages, Editorial, large marketing sites). A single-fold portfolio does not need it — never impose it there.
- **Blur-up placeholders** — LQIP / blurhash on image-heavy heroes and galleries. Earns its weight only when imagery is the detail.
- **Per-script font rebinding** — distinct font stacks per writing system, for multi-script locales. Skip for single-script sites.
- **Web manifest** — a PWA manifest, for installable / app-like products.
- **`sitemap.xml` + `robots.txt`** — for sites with crawlable depth; noise on a one-pager.

## Template — structured data, opted in

- **JSON-LD** — schema.org structured data (Organization, Product, Article, BreadcrumbList). Provided as an archetype template the designer fills with real values, never auto-generated with placeholder data — placeholder JSON-LD is worse than none.

## Prominence rule

The floor never leads. In the skill body and in the build, the signature moment and the push-three-axes driver come first; this floor holds under them. A build that nails the floor and has no signature moment fails the bar — the floor is necessary, never sufficient.
