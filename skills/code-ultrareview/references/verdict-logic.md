# Verdict logic

The closing `## Verdict` line in every report is computed deterministically from the verified-finding set, not chosen by an LLM. This document specifies the algorithm.

## Inputs

Verified findings only. Unverified findings (sub-80 confidence, routed to `### Unverified`) are excluded by design — sub-80 is not load-bearing for a ship decision. Documented in `aggregation.py::compute_verdict` and pinned by `tests/code-ultrareview/test_verdict.py::TestVerdictExclusions`.

Each finding carries:

- `meta.marker` ∈ {🔴, 🟠, 🟢} — attached by `_attach_marker`.
- `meta.anthropic_tier` ∈ {Important, Nit, Pre-existing, None} — attached by `assign_anthropic_tier`.

A finding is **Important** when `tier == "Important"` (≥80 confidence + High/Medium severity, and not `pre_existing=True`). Pre-existing findings on unchanged lines are excluded from the ship decision.

## Algorithm

```
red_important    = [f for f in verified if f.marker == "🔴" and f.tier == "Important"]
orange_important = [f for f in verified if f.marker == "🟠" and f.tier == "Important"]

if red_important:
    label = "Needs work"
elif orange_important:
    label = "Fix-then-ship"
else:
    label = "Ship"
```

Severity-wins: a single 🔴 Important flips the verdict to Needs work regardless of how many 🟠 or 🟢 findings exist. A 🟠 Important raises the verdict to Fix-then-ship only when no 🔴 Important is present.

## Rationale templates

| Verdict | Trigger | Rationale |
|---------|---------|-----------|
| Ship | No verified findings | `Six lenses ran clean. Ship.` |
| Ship | Only Nits / Pre-existing | `Only Nits — no blockers. Ship.` |
| Fix-then-ship | One or more 🟠 Important | `{N} 🟠 Important ({lens-list}) — fix before ship.` |
| Needs work | One or more 🔴 Important | `{N} 🔴 Important ({lens-list}) — fix red before ship.` |

`{lens-list}` is the comma-separated list of `{count} in {lens}` items, one per distinct lens with Important findings.

## Drivers

The `drivers` field is the same `{count} in {lens}` list as a top-level array (already inlined in the rationale string). The template renders it as a bullet list under the verdict line when length ≥ 2 — useful for multi-lens incidents.

For `Ship`, `drivers` is the empty list.

## Worked examples

### Clean review

Input: zero verified findings.
Output: `Ship — Six lenses ran clean. Ship.`, `drivers: []`.

### Only nits

Input: three Low-severity findings, all confidence ≥ 80 → `tier: Nit`.
Output: `Ship — Only Nits — no blockers. Ship.`, `drivers: []`.

### One Medium Important in docs-version

Input: one `docs-version` finding, severity Medium, confidence 88 → `tier: Important`, `marker: 🟠`.
Output: `Fix-then-ship — 1 🟠 Important (1 in docs-version) — fix before ship.`, `drivers: ["1 in docs-version"]`.

### One High Important in bugs-drift

Input: one `bugs-drift` finding, severity High, confidence 92 → `tier: Important`, `marker: 🔴`.
Output: `Needs work — 1 🔴 Important (1 in bugs-drift) — fix red before ship.`, `drivers: ["1 in bugs-drift"]`.

### Mixed High + Medium + Low

Input: 1 High (bugs-drift), 2 Medium (docs-version + rules), 5 Low. All ≥80 confidence.
Output: `Needs work — 1 🔴 Important (1 in bugs-drift) — fix red before ship.`, `drivers: ["1 in bugs-drift"]`. The Medium and Low findings do not appear in the verdict — they appear in the action plan instead.

### Sub-80 High routed to Unverified

Input: one High-severity finding, confidence 65. A2 downgrades to Low/🟢, routes to `### Unverified`.
Output: `Ship — Six lenses ran clean. Ship.`. The unverified finding still shows in the report; it just does not flip the verdict.

### Pre-existing High

Input: one High-severity finding on an unchanged line, `pre_existing: True` → `tier: Pre-existing`.
Output: `Ship — Six lenses ran clean. Ship.` (assuming no other Important findings). Pre-existing is informational, never a ship blocker.

## Cross-references

- `aggregation.py::compute_verdict` — implementation.
- `tests/code-ultrareview/test_verdict.py` — full assertion set.
- `templates/code-ultrareview.md` — `## Verdict` section consumes the dict directly.
- `references/skill-routing.md` — companion routing for the action plan that follows.

## Why not LLM-judged?

The original template emitted `**{Ship | Fix-then-ship | Needs work}** — {one-line rationale}` as a literal placeholder, leaving the synthesizer subagent to pick a verdict implicitly. Outcomes drifted across runs and were not auditable. The deterministic algorithm above is reproducible: the same finding set always yields the same verdict.

If the verdict surprises you, check `meta.marker` and `meta.anthropic_tier` on the verified findings — those are the only inputs.
