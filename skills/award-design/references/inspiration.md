# Inspiration

Where to look, and what to copy versus what to route around. This file ships URLs, never a vendored corpus — reference the live sources, don't snapshot them. Distinct from `exemplars.md` (per-archetype real-site anchors): this is the cross-archetype gallery plus the motion canon and the component-kit honesty list.

## Galleries — study composition, not components

Browse for direction during Discovery; capture the *character*, never the tokens — token-copying produces clones (see `exemplars.md`).

| Source | URL | Use for |
|---|---|---|
| **Awwwards** | awwwards.com | The bar — SOTD / SOTM / SOTY, jury scores, the judging signal this skill targets |
| **Godly** | godly.website | Curated modern web, sorted by section (hero, footer, pricing) |
| **SiteInspire** | siteinspire.com | Clean editorial / minimal canon, filterable by style + type |
| **Codrops** | tympanus.net/codrops | Technique tutorials + the demo archive — motion patterns with source |

## Motion canon — the libraries the winners actually use

Reference docs, cited as optional deep-dives. None is mandated — CSS-native-first, per `foundations.md`.

| Library | URL | Role |
|---|---|---|
| **GSAP** | gsap.com/docs | ScrollTrigger, SplitText, timelines — the scroll / scrub standard |
| **Lenis** | lenis.darkroom.engineering | Smooth scroll (~2KB), preserves sticky + IntersectionObserver |
| **Motion** | motion.dev | React UI transitions, springs, layout animation |

## Component kits — scaffold only, then restyle past their defaults

These ship fast but carry a recognizable default look — the exact source of the 2026 AI-landing-page monoculture (beams, sparkles, spotlight cards, animated gradients, 3D-tilt cards). Scaffold structure from them, then restyle hard past their defaults: swap the font, kill the stock gradient, retime the motion, re-token the color. Shipped unmodified, they are the tell.

| Kit / asset | URL | The default to restyle past |
|---|---|---|
| **Aceternity UI** | ui.aceternity.com | Beams, spotlight, 3D-tilt cards — the canonical AI-landing look |
| **Magic UI** | magicui.design | Animated gradients, marquees, shimmer borders |
| **shadcn/ui** (raw) | ui.shadcn.com | Neutral primitives — usable, but the un-themed default reads as template |
| **Cult UI** | cult-ui.com | Trendy motion components, heavy default flourish |
| **Motion-Primitives** | motion-primitives.com | Motion building blocks — restyle the canned timings |
| **21st.dev** | 21st.dev/community/components | Community shadcn-style registry + Magic MCP — same kit-default risk; mine for structure, restyle past the registry look |

The **Satoshi / Clash / General Sans** trio (Fontshare) is the type-side equivalent — free, good, and so defaulted-to that they read as AI-picked. Use them, but know they signal "kit build" the way Inter does; rotate or justify.

## Anti-sameness rule

Scaffolding from a kit is fine; shipping its defaults is the tell. The build must clear the **component-kit-sameness** check in `anti-patterns.md` — a dropped-in Aceternity hero or a Magic UI gradient wall, unmodified, fails it. The override is the work: scaffold, then restyle past the default.
