# DESIGN.md anatomy — token namespaces + prose mapping

The DESIGN.md is the committed universe — award-design writes it when none exists (the constant reference for every build pass and every subagent), and adapts to it when one is present; `/design-system` governs it after. It carries award-grade content across two layers: YAML frontmatter for tokens, eight ordered prose sections for narrative and intent. Both layers are required; an empty layer makes the file useless to its consumer. The depth bar is mcll-grade: every spacing value, type-ramp step, color role, motion duration, and signature beat is specified, not gestured at.

## YAML namespaces

| Type | Namespaces | Validated by Google CLI |
|---|---|---|
| Canonical | `colors`, `typography`, `rounded`, `spacing`, `components` | yes (broken-ref, contrast-ratio, missing-primary, etc.) |
| Extension (preserved) | `motion`, `shadows`, `aspectRatios`, `heights`, `containers`, `breakpoints`, `zIndex`, `borderWidths`, `opacity`, `scrollTriggers` | no (preserved-but-unvalidated per spec); validated by `/design-system audit-extensions` against the `globals.css` `@theme` mirror |

Components bind ONLY to the 8 canonical property tokens — `backgroundColor`, `textColor`, `typography`, `rounded`, `padding`, `size`, `height`, `width`. Extension tokens are referenced from prose only (e.g., `{motion.duration-reveal-slow}`), never as `components:` keys. The closed property-token set is the empirical lint-failure mode.

## Award-grade prose mapping

Every vital narrative element from `/award-design` maps to one of the eight ordered sections — nothing is dropped:

| Award-grade narrative | DESIGN.md section |
|---|---|
| Atmosphere scores (Density / Variance / Motion) | 1. Overview |
| Archetype identity + remix declaration | 1. Overview |
| Signature moment (the one unforgettable interaction) | 1. Overview |
| Photography direction (cinematic / editorial / flat-lay register) | 1. Overview |
| Copy register (tone of voice) | 1. Overview |
| Colour narrative + photography colour guidance | 2. Colors |
| Kinetic typography intent (variable-font behaviour, text-reveal) | 3. Typography |
| Layout grid + responsive strategy | 4. Layout |
| Scroll choreography (scroll-driven reveals, narrative pacing) | 4. Layout (cross-reference `motion.*`, `scrollTriggers.*`) |
| Shadow language + depth narrative | 5. Elevation & Depth (cross-reference `shadows.*`, `borderWidths.*`, `opacity.*`) |
| Geometric / radius language | 6. Shapes |
| Component patterns + variants | 7. Components |
| Micro-interactions (hover / pressed / active states) | 7. Components (variant entries: `button-primary-hover`) |
| Motion philosophy | 7. Components + cross-reference 1. Overview |
| Award-grade rules + AI-tells anti-patterns + production-hardening guardrails | 8. Do's and Don'ts |

Production-hardening implementation guardrails (viewport units, autoplay belt-and-suspenders, iOS Safari quirks) host as one-line testable rules in Do's and Don'ts; full detail stays in `production-hardening.md`. Full extension convention: `../../design-system/references/extended-tokens.md`.

## Motion & 3D depth (motion/3D archetypes)

For Immersive, Experimental, Bold, and Spatial-Organic builds, the universe carries enough motion and dimensional detail that a specialist subagent can build the signature scene from this file alone:

- **Signature scene spec** — what renders, the camera or material behavior, and the scroll/pointer linkage that drives it (Section 1 Overview + Section 7 Components).
- **Scroll choreography** — the pacing and the skeleton (sticky-stack, horizontal-pan, scrub) keyed to `scrollTriggers.*`, named in Section 4 Layout. Patterns: `foundations.md` *Signature scroll skeletons*.
- **View-Transitions morphs** — named element morphs (thumbnail → hero) and the reduced-motion fallback, in Section 4.
- **Easing lexicon** — the signature curve(s) pinned to `motion.ease-*`, never ad-hoc per component (`foundations.md` *Signature easing lexicon*).
- **3D / shader build notes** — when the signature is WebGL, point the builder to `references/ingredients/web3d-for-sites.md` (or `ogl-shaders.md`); the scene expresses these tokens, never generic defaults.

## Minimal valid fragment

Canonical (validated) and extension (preserved-but-unvalidated) namespaces side by side; components stay within the eight property tokens; prose names extensions canonically:

```yaml
colors:
  primary: "#1a1c1e"
  surface: "#f7f5f1"
components:
  modal:
    backgroundColor: "{colors.surface}"   # canonical property token — accepted
    rounded: "{rounded.md}"
    padding: 32px
    # `shadow: "{shadows.lifted}"` would be rejected — `shadow` is not in the 8
    # canonical property tokens; the lint flags unknown component properties.
motion:
  duration-reveal-slow: 1200ms
  ease-standard: cubic-bezier(0.16, 1, 0.3, 1)
shadows:
  lifted: 0 20px 40px -16px rgb(0 0 0 / 0.08)
```

```markdown
## Elevation & Depth

Modals lift on `{shadows.lifted}` — referenced from prose. Reveal motion uses `{motion.duration-reveal-slow}` paced by `{motion.ease-standard}`.
```

The mirror in `globals.css` (auto-generated by `/design-system export tailwind`):

```css
@theme {
  --color-primary: #1a1c1e;
  --color-surface: #f7f5f1;
  --duration-reveal-slow: 1200ms;
  --ease-standard: cubic-bezier(0.16, 1, 0.3, 1);
  --shadow-lifted: 0 20px 40px -16px rgb(0 0 0 / 0.08);
}
```
