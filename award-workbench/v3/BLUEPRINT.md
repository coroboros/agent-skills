# Award-design v3 — blueprint v2 (post-refutation, decided)

Supersedes BLUEPRINT.md. Every change below traces to an adjudicated refutation finding (three refuters: economics, ceiling, ops) or to the primary-evidence adjudication of inter-agent conflicts. Verdict authority: Fable 5 as session decision-maker; refutations judged on merit, no single-refuter veto.

## 0. Mission (unchanged)

Any capable coding model designs and builds web frontends at the Awwwards SOTD bar (7.5+), per archetype, creativity intact — universal across model strengths, durable across generations. North star, article §9.6 verbatim: "one unforgettable signature moment, executed with precision across every device, loading in under two seconds."

## 1. The laws (revised)

**Law 1 — Evidence classes govern authority.** Classes: `winner` · `shipped` · `technique` · `theory` — plus the refuter-forced refinement: `vendor` (measured by a vendor, cited from their history/site, not reproduced by us). A `theory` OR unreproduced `vendor` claim can never become a gate, threshold, or FAIL. Applied to this document first: "30/35 concepts identical" and "Fraunces 92%→0%" are `vendor` (commit-body-sourced, adjudicated real); "188 worlds" is `vendor-claimed`; the amplification band was `theory` and is retired below.

**Law 2 (replaced) — Absolute core cap + priced loads.** The ratio law is dead (measured scale-invariant and monolith-rewarding: taste-skill scores 1.0× *because* it is a monolith; impeccable's flagship path runs ~8.9×). Replacement, two parts:
- Always-on core ≤ **5,000 tokens** (the repo spec's actual number; today's v2 file is 7,473 — already over).
- Every reference file carries its token cost in the core's load map, and loads are commitment-triggered with hallmark's budgeted-prohibition phrasing (verbatim precedent on disk: "Loading the cookbook end-to-end … is the single biggest token waste in the skill — don't"). No "≤2 techniques" cap: a build loads what its design_plan commits, each load priced.

**Law 3 (new, from the ceiling refutation) — The ceiling corpus is untouchable.** Both donor systems are floor-escape systems (impeccable v4: zero aliveness instruments, 61/61 negative detector rules; Anthropic docs: zero ceiling guidance). The only ceiling corpus in the evidence base is ours — the archetype files' Mid-page life / Scroll texture / Idle band / Channel calibration / Spectacle menus, `winner`-class. v3 loads it smarter; it never deletes it.

## 2. Architecture (revised sizes — all byte figures re-derived at measured density, 103.6 B/line)

```
award-design/
  SKILL.md                    ≤ 5,000 tokens (~180 lines at this corpus's density)
                              Content: mission + laws + routing + the 9-step path
                              (names only; detail lives in gate files) + hard
                              constraints (v2's 10, verbatim, unconditional) +
                              priced load map + verdict-label tiers.
  scripts/                    python3 stdlib ONLY (repo runtime contract)
    direction_roll.py         SHA-256 floor-of-3 roll over the model's written
                              SPINES list; stdout = key + index + the selected
                              archetype tier-1 content + its reflex list
                              (push-don't-pull: one invocation places the
                              load-bearing material in context)
    scan.py                   static defect+tell rules (~720 lines honest
                              estimate) + OPTICAL-* REVIEW family (decidable
                              craft facts) + STACK-FACTS-STALE notice (>180d)
  assets/                     browser-evaluated PAYLOADS, injected by the
                              harness rung (detector.js mold) — never runtime
                              scripts, never own a browser process
    detector.js               census + computed-style truth (aliveness floors
                              demoted to evidence per Law 1)
    render-floor.js           NEW payload: text-overlap boxes, clipped glyphs,
                              zero-width grid children with content, CTA-in-fold,
                              mobile-nav presence, console errors; harness
                              resizes viewport and re-invokes per width
    pixel-metrics.js          NEW payload: quadrant emptiness, ink profile,
                              ground commitment, accent-frequency per viewport,
                              idle/scroll pixel-diff — EVIDENCE ONLY
  reference/
    register/  brand.md · product.md            (per-surface, not per-project)
    archetype/                9 files, TWO-TIER (economics fix):
                              tier 1 ~40 lines (DNA, anti-signals, macrostructures)
                              — loads at Phase 0–1 via the roll's stdout;
                              tier 2 (effect palette + page recipe + Mid-page life +
                              Scroll texture + Idle band + Spectacle menu, ~15 KB)
                              — loads at the design_plan commit, BY HEADING.
                              No 2.5 KB cap. Nothing deleted; heading indexes added.
    technique/  skeletons.md (~330) · stack-facts.md (~60, every row `checked: YYYY-MM`)
                + the verbatim survivors (preloaders, page-transitions, text-effects,
                motion-palette, navigation-patterns, web3d, imagery, copy-recipes,
                production-hardening, optical-craft — the §8/§2 reconciliation is
                one-to-one: every protected file has a path here or a written grave)
    gate/       concept.md (R1 detail) · review.md (R2 detail + routing + the
                exemplar-device guard: closing gaps state deficits against the
                brief's own world, never the exemplar's device)
    exemplars.md              dated rows, `checked:` field, same staleness notice
  assets/components/          ON DISK, never read whole. Discovery layer: a
                              GENERATED per-archetype index (~1.2k tokens,
                              id + whenToUse first sentence) inside the archetype's
                              tier-2 load; grep is fallback only. Manifest stays
                              authoritative (it is NOT regenerable from headers:
                              11/103). One gap to close: a Three.js scene
                              component (WebGPU path).
```

## 3. The generative path (revised)

1. **Read the room** — mode, register (per surface), archetype (loading map + exemplar naming; the direction never comes from the table), dials.
2. **SPINES before SEED (proof-by-construction, ops fix):** the model writes 5–7 candidate spines into the design_plan under `SPINES:`, one line each, each with a one-line replayable-moment viability note (filters the padded tail). THEN `direction_roll.py <count>` runs; its stdout (key + assigned index + archetype tier-1 + reflex list) is pasted verbatim. Anyone can reproduce the hash offline; the eval harness can test the mechanism.
3. **The local challenger contest (ceiling F2, answers old open-Q8):** the roll also deals 2–3 challengers from OTHER archetypes' Spectacle menus + `exemplars.md`; each is fused with the brief's truth and weighed against the assigned spine on impeccable's two axes (audience identification, product clarity). A challenger winning both becomes the build. External deal + must-win contest = safe against catalog-picks-the-vision.
4. **The standing exit** — the category standard, played straight, never recommended; after a second re-roll refusal it is offered by name as a two-item menu (ops fix: the taste-dispute terminator).
5. **Anti-attractor procedure** inside the assigned direction (vendor-verified commit a5db8214: "reduce monoculture from negative prescriptions"): enumerate reflexes, reject by name; `anchor.py` (stdlib) draws the material/color seed.
6. **Spine → signature by the world's verb**, with `signature-invention.md`'s map loaded (the file survives; it was orphaned in blueprint v1).
7. **The direction contract — SIX blocks, ≤180 words** (ceiling F3): THESIS · OWN-WORLD · STORY · FIRST-VIEWPORT · FORM+SEED · **SIGNATURE (verb · medium · trigger · replay behavior)** · closed by FINISH. Replay is decidable: fire-once-leaving-a-static-frame is an entrance, not a signature.
8. **R1** fresh-context refutation (gate/concept.md).
9. **Hero-first cheap judge** (comparative framing = remedy routing; shared render frame across candidates).
10. **Build under pacing** — pace like a score (RESTORED — it was silently absent from blueprint v1): per-section intensity, one climax (trigger scroll/load), one rest, award surfaces committed or declared out; `render-floor.js` runs PER CHAPTER as built (ceiling F7); optical-craft.md loaded at build time (installed, not detected).

## 4. Verification stack (revised — the defensible 5-layer stack, ~450k tokens, 54% cheaper than blueprint v1)

L0 `scan.py` (static, seconds) → L1 `render-floor.js` per chapter + full sweep (deterministic, ~1 min — catches 4 of Undercurrent's 6 P0s) → L2 `pixel-metrics.js` (evidence pack) → L3a hero judge early (comparative, 10–15 min) → L3b driven audit ONCE, late (the only instrument for responsive reachability, interaction truth, spec-fiction; isolated browser context within the single session). L3a-late and finish-reviewer-pass-2 are DELETED (economics: four full-render reads of one artifact, two with no detection value). **L3b's report IS the verdict artifact** — it already produces the ordered P0 list, desire read, and score.

Ordering laws kept: builder cannot write READY; reviewer read-only by tool grant; reviewer inventories the render in its own words before reading the contract; turn-budget realism clause; tree-hash freeze, mid-review edits void; one fix batch + one recheck, second verdict ends work; findings dismissed only with a measurement; P0s cleared before subtle layers judged; **LOSES carries a reason class — concept | execution | craft — and routes accordingly** (ceiling F6; the only complete R2 on record: "the cap is execution, not idea").

**Browser economics (ops A1, blocking fix):** ONE browser session per run — judges reuse by sequential navigation, never parallel instances; payloads never own the process; the harness rung owns lifecycle and teardown. (The v1 stack implied 12 concurrent browsers — the measured melt.)

**Verdict-label tiers (ops A4):** subagents present → READY by synthesis of independent returns · no subagents + human → the human gate IS the independent return (two-line ask) · headless single-context → terminal label REVIEWED-SAME-CONTEXT, never READY. Every tier terminates.

## 5. Cross-model service (revised)

- Same judgment prose for all; delivery is structural (the roll's stdout push), not prose strengthening (the vendor's measured lesson, correctly attributed: gpt-5.4-mini failed reference-loading; Haiku passed 8/8; prose strengthening didn't move it — script-side injection did).
- v2's 10 hard constraints survive verbatim and unconditional (defect-class bans don't relocate; taste-class monoculture is handled by the anti-attractor + roll).
- NO per-model block slots in v3.0 (the mechanism exists at the vendor — adjudicated: craft-floor.md carries `<codex>`/`<gemini>` blocks — but ours would be unmeasured; blocks come later WITH our own bias measurement).
- Weak models: the per-archetype component index is their selection layer; no WebGL attempts; the roll still binds them (it's a script, not judgment).

## 6. The eval harness (re-ordered by falsification cost — economics fix)

- **Tier 0, $0, before any distillation:** wire per-rule IDs to the EXISTING 1,634-test suite and run the ablation as a gate (already demonstrated: the v1 reference move breaks 396 tests; best-case 45-line distillation still breaks 16). No file moves until tier 0 is green.
- **Tier 1, ~1M tokens:** concept-only convergence — Phase 0–1 across 16 brief framings × skill-on/off; measures duplicate-direction rate; falsifies the roll's central claim directly.
- **Tier 2, 10 builds, one model:** defect-rate on the L1 floor (script-scored, near-zero variance — the only build-level comparison resolvable at n=5).
- Blind judge: single confirmatory pass on best/worst arms only. (The n=5 judge-scored design was unresolvable: ~3-point judge noise vs ~1-point effect.)

## 7. What dies / what survives (reconciled one-to-one)

Dies: taste-as-number gates (theory-class thresholds), closed world, BLOCKED, imposed verdicts, playbooks-as-law (data merges into archetype tier-2 after the stale-vs-refuted merge), recipes.json (folds into playbooks first), protocol-adherence evals, the 18–24× Load: lists, the ratio law, L3a-late + reviewer-pass-2, per-model empty slots, `anchor.mjs` (→ .py), Playwright runtime scripts (→ payloads).

Survives with a named path: every file in the capital audit's protected list — including `production-hardening.md`, `signature-invention.md`, `interaction-signatures.md`, `optical-craft.md`, `anti-patterns.md` (core subset), `foundations.md` (split per the technique-delivery spec) — plus the component annex untouched, detector as census, the 24 recovered refutation dossiers archived in `research/…/deep-research/` as the epistemic record the archetype distillation links to.

## 8. Construction order

1. Tier-0 harness (rule IDs ↔ existing tests) — the distillation gate.
2. `direction_roll.py` + `anchor.py` + SPINES/SEED contract format (mechanically testable).
3. Payload rewrites (`render-floor.js`, `pixel-metrics.js`) in the detector.js mold.
4. Archetype two-tier restructure (merge playbook refutations, add heading indexes + component indexes) — under the tier-0 gate.
5. Technique layer (skeletons.md with the FIXED Lenis wiring, stack-facts.md with dates).
6. New SKILL.md last — it routes to everything above; ≤5,000 tokens.
7. Tier-1 + tier-2 evals; blind confirmatory pass; ship v3.0.
