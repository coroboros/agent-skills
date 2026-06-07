# Ship-Ready Floor

The completeness floor under every build. It sits *below* the signature moment, never above it — the floor is what keeps a built page from reading as a prototype; the signature moment is what makes it memorable. Three tiers, sorted by cost and risk:

- **Impose** — cheap, pure upside, no design cost. Wired into the Phase 4 HARD gate.
- **Offer** — real production weight that can smother a small build. Surfaced as one opt-in question, gated on brief / archetype. Never auto-built.
- **Template** — structured data the designer fills in. Provided as an archetype template, opted into.

Most of the Impose tier already lives in `foundations.md` UX Quality + Accessibility; this file names and tiers it so the gate can cite one floor. It organizes those rules, it does not re-derive them.

## Impose — the HARD-gate floor (cheap, pure upside)

Present on every build, gated. None competes with the design; all is floor.

- **Full interactive cycles** — every async surface has loading (skeletons matching the final layout, not a spinner), empty, and error states; `:active` gives tactile press feedback. A control with only a resting state is unfinished.
- **Contrast on controls** — buttons and form fields meet WCAG AA in every state (rest, hover, disabled, focus). Glassmorphic and tinted controls are the usual failures — test them.
- **Cursor-affordance discipline** — `pointer` on actionable, `text` on text, `not-allowed` on disabled, default elsewhere. A `div` button with a default cursor reads as broken.
- **One consistent link-hover signature** — a single hover treatment (underline reveal, color shift) applied everywhere. Mixed hover behaviors read as unfinished.
- **Skip-link + `:focus-visible`** — a keyboard skip-to-content link and a custom, visible focus ring on every interactive element. Never `outline: none` without a replacement.
- **Semantic HTML + landmarks** — `<header> <nav> <main> <footer>`, one `<h1>`, ordered headings. No `<div onClick>` navigation.
- **Canonical + hreflang** — a `<link rel="canonical">`; `hreflang` when the site is localized.
- **Favicon + `icon.svg` + OG image** — a real favicon, an SVG icon, and an Open Graph image so shared links render.
- **`theme-color`** — light and dark `theme-color` meta so mobile chrome matches the surface.
- **`prefers-reduced-motion`** — motion replaced with opacity, never removed.

Detail and code for each: `foundations.md` UX Quality + Accessibility. This list is the gate's checklist; that file is the implementation.

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
