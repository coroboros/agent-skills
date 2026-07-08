# Code-craft review — the final mechanical pass

A short, deterministic code pass at Phase 5, after the pre-flight boxes and before the R2 review. The build can look pixel-perfect and still carry a finish layer that only shows in the source: raw hex where a token exists, px where the scale says rem, a native control the design step actively asked for. This pass catches that band — mechanically, so it is cheap and repeatable.

**This gate can override the DESIGN.md.** The design-authoring step can *prescribe* the very tells the build then ships — a native select, a `not-allowed` cursor, a hardcoded color. When a DESIGN.md instruction collides with a rule here, this pass wins and the DESIGN.md line is corrected (`design-md-anatomy.md` forbids those prescriptions at the source). A gate that defers to a wrong spec is not a gate.

Run each check across the shipped CSS/JS/HTML. A hit is fixed or written into the verdict with a brief-tied justification.

## The five checks

1. **Token-drift / SSOT scan.** No raw color literal equal to a defined token's value (grep the token's hex/oklch channels across the CSS — a surface color duplicated as a literal in six scrims is the canonical break). No duration or dimension hardcoded in JS that also exists as a CSS custom property. No token defined and never referenced. A value that must change in two places to stay correct is a defect.
2. **OKLCH + rem enforcement.** Authored color is OKLCH — allow `oklch()`, relative-color `oklch(from …)`, and gradients; flag raw hex/`rgb()` in *opaque* authored color (`foundations.md` OKLCH). Translucent overlays, borders, and scrims where the alpha is the point may stay `rgb(… / α)` / `rgba()` (the surface-temperature borders of `optical-craft.md`, glass fills) — the flag targets opaque fills, not translucency. Sizing is rem — px allowed only for borders, `1px` hairlines, and WCAG touch-target `min-height`; flag px spacing/type, and cross-check emitted spacing against the declared scale (off-scale literals like 6/7/10/14px bypass the ramp).
3. **Native-control + cursor lint.** No `<select>`, checkbox, radio, or other form control without `appearance: none` and a custom affordance. No `cursor: not-allowed` or any native blocked/disabled cursor — a disabled control drops opacity and keeps `cursor: default`, never the OS "no-entry" icon. Run this against the DESIGN.md too: if the spec prescribes either tell, the spec is wrong and gets fixed.
4. **Accessibility floor.** Compute contrast for every text rule at its *actual* font-size against its background; fail sub-4.5:1 on anything under ~18px regardless of a "decorative only" annotation (small captions and labels carry real content). Every full-screen overlay sets `inert` / `aria-hidden` on its siblings and traps focus; `Esc` closes and returns focus to the trigger (`navigation-patterns.md`).
5. **JS lifecycle refutation.** A render loop (WebGL, rAF) resumes only when its target is both visible *and* in the viewport — resume gated on `visibilitychange` alone restarts full-tilt on an off-screen canvas. Every `setTimeout` guarding a visibility or `hidden` toggle is stored and cleared by its inverse action — an unguarded close-timer fires on a reopened menu and re-hides it.

## Verdict line

Fold the result into the Phase 5 verdict block as one line: `Code-craft: <N> fixed · <K> justified · <clean | issues>`. An un-run pass is a skipped gate, not a pass.
