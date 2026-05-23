# Aggregation — A2, sub-80 iteration, dedup, severity tiers

Aggregation is thin glue between lens subagents and the report template. It
applies the no-silent-drop contract, runs the sub-80
iteration pass, deduplicates cross-lens hits, and maps confidence + severity
to the report's tier labels.

## A2 — no silent drop

The earlier `code-review` implementation dropped any finding with
`confidence < 80` — a structural hole: real findings were lost to a heuristic
filter. **A2 replaces drop with routing.**

Rules:

- Any finding with `confidence < 80` AND `confidence > 0` is **surfaced**, not dropped.
- Its `finding` text is prefixed `[unverified]`.
- Its `recommendation` text is prefixed with the routing rationale: `Sub-80 confidence ({score}) — verify locally before action.`
- Severity is downgraded to `Low` (regardless of original severity).
- It appears in the report under `### ⚠️ Unverified` (a sub-section of `## 🔎 Findings`), separate from verified findings.

`confidence == 0` is still a drop — by rubric, 0 means "doesn't survive light scrutiny, or pre-existing." Drops include rationale in the synthesizer's debug output (never in the user-facing report).

## A1 — spec-claim triggering

`bugs-drift` lens runs the A1 check on every dispatch. When the diff,
README, or `CLAUDE.md` cites a named normative spec, the lens:

1. Detects the spec via regex (same as `scripts/audit_signals.py`).
2. Fetches the spec body via `WebFetch` (Claude Code tool).
3. Caches the response under `~/.claude/cache/code-ultrareview/specs/{spec-slug}-{date}.txt` with ETag-aware refresh ≥7 days.
4. Quotes the governing clause verbatim into the finding's `recommendation`.
5. Diffs the code against the quoted clause.

A verifiable divergence scores **≥80** — the spec itself is the evidence,
so the finding does not depend on heuristic judgment. Fetch failure with
no cache → finding surfaces as `[unverified — needs network]` and routes
per A2.

`scripts/spec_claim.py` exposes a `trigger_a1_finding(spec_name,
spec_excerpt, diff_excerpt, location)` helper that returns a canonical
`Finding` with confidence 85 and the spec quote in the recommendation.
Subagents call this after `WebFetch` returns the cached body.

## Iteration on sub-80 findings

Iteration is always-on: whenever the dispatcher supplies a `builder_fn`,
every sub-80 finding gets one verification pass. The subagent:

1. Detects the repo's build/test tool (`scripts/build_detect.py`).
2. Runs the canonical test command on a fixture or test neighbor.
3. Interprets the result:
   - Build confirms the finding → promote confidence to ≥80 (originally-scored confidence + 30, capped at 95). Move to verified.
   - Build disproves the finding → drop with rationale. The drop is logged but not surfaced in the user report (it was unverified anyway).
   - Build fails to run (env missing) → no promotion, no drop. Finding stays in Unverified.
4. Cap: **one iteration per finding** — bounds the cost increase to roughly 2× the first-pass tokens.

`aggregation.iterate_unverified(findings, builder_fn)` exposes the
orchestration. The `builder_fn` is supplied by the dispatcher and returns
one of `"confirmed"`, `"disproved"`, or `"inconclusive"` per finding.
Pass `builder_fn=None` to `synthesize()` when no build harness is
available — the unverified set surfaces without promotion attempts.

## Deduplication

Cross-lens duplicates collapse to a single row:

- Key: `(file:line, finding-key)` where `finding-key` is the first 6 tokens of the finding text (normalized, lowercase).
- Keep the highest-confidence finding; merge the other lens's name into a `meta.secondary_lens` field.
- A finding from `coherence-graph` and a finding from `bugs-drift` on the same line collapse with both lens names noted.

## Severity tier mapping

Two severity schemes coexist in the report — Anthropic's Managed Code Review
tiers (`Important / Nit / Pre-existing`) and the existing
`High / Medium / Low`. The synthesizer adds the Anthropic tier from
confidence + severity:

| Confidence | Severity | Anthropic tier |
|-----------|----------|----------------|
| ≥80 | High | Important |
| ≥80 | Medium | Important |
| ≥80 | Low | Nit |
| < 80 | any | (omitted — finding is in `### ⚠️ Unverified` sub-section) |
| (out of diff) | any | Pre-existing |

Pre-existing is flagged by the lens itself when the finding is on an
unchanged line — the synthesizer never re-classifies.

## Order

Within each sub-section of `## 🔎 Findings` (`### 🔴 High`, `### 🟠 Medium`,
`### 🟢 Low`, `### ⚠️ Unverified`), order findings by:

1. Confidence: high → low.
2. Location (lexicographic) — stable tiebreak.

Severity ordering is implicit in the sub-section split itself, so the High →
Medium → Low → Unverified sequence is enforced by the template, not by the
sort key.

## "Clean" notes

A lens that returns zero findings contributes a `Lens <name>: clean.` line
under `## 🔎 Findings`, not silence. Silence is ambiguous (did the lens run?);
an explicit clean note is unambiguous. Per-severity sub-sections with zero
findings render as `_None._` under their heading (same reason — silence is
ambiguous).

## Implementation

`scripts/aggregation.py` exposes:

- `apply_a2(findings) -> tuple[verified, unverified]` — A2 routing; also attaches `meta.marker` to every retained finding.
- `iterate_unverified(unverified, builder_fn) -> tuple[promoted, remaining, dropped]` — sub-80 iteration; one call per finding.
- `dedupe(findings) -> findings` — cross-lens dedup.
- `assign_anthropic_tier(finding) -> str` — Important / Nit / Pre-existing.
- `order(findings) -> findings` — canonical ordering.
- `compute_severity_counts(verified) -> dict[str, int]` — verified-finding counts by marker (🔴 / 🟠 / 🟢).
- `compute_lens_summary(verified, unverified, ran_lenses) -> list[dict]` — per-lens status snapshot for every canonical lens (clean ones included; skipped lenses marked).
- `compute_verdict(verified) -> dict` — deterministic Ship / Fix-then-ship / Needs work with rationale + drivers. Spec: `references/verdict-logic.md`.
- `compute_action_plan(verified, unverified, installed_skills, route_fn) -> dict` — per-cluster paste-ready delegation prompts, severity-ordered. Spec: `references/skill-routing.md`.

The orchestrator composes them in this order:

```
findings = collect_from_all_lenses()
findings = dedupe(findings)
verified, unverified = apply_a2(findings)   # attaches meta.marker
if builder_fn is not None:
    promoted, unverified, _ = iterate_unverified(unverified, builder_fn)
    verified.extend(promoted)
verified = order([assign_anthropic_tier(f) for f in verified])
unverified = order(unverified)

severity_counts = compute_severity_counts(verified)
lens_summary    = compute_lens_summary(verified, unverified, ran_lenses)
verdict         = compute_verdict(verified)
action_plan     = compute_action_plan(verified, unverified, installed_skills, route_fn)
```

Subagent prompts never see the synthesizer — they emit findings; the
orchestrator handles A2, iteration, dedup, ordering, and the four
closing-block computations.

## Closing-block extension (synthesize() return keys)

`synthesize()` returns a dict with seven keys. The first three are the
original wire format; the last four are the closing-block extensions
consumed by `templates/code-ultrareview.md`.

| Key | Type | Shape |
|-----|------|-------|
| `verified` | `list[dict]` | Findings ≥80 confidence, ordered. |
| `unverified` | `list[dict]` | A2-routed sub-80 findings, marker always 🟢. |
| `iteration_dropped` | `list[dict]` | Findings disproved by build verification (logging only). |
| `severity_counts` | `dict[str, int]` | `{"🔴": N, "🟠": N, "🟢": N}` — verified set only. Keys always present. |
| `lens_summary` | `list[dict]` | Six rows, canonical lens order. Each: `{lens, status, verified_count, unverified_count, top_finding}`. Status ∈ `🔴 / 🟠 / 🟢 / skipped`. |
| `verdict` | `dict` | `{label, rationale, drivers}` — label ∈ `Ship / Fix-then-ship / Needs work`. |
| `action_plan` | `dict` | `{zero_findings, clusters, unverified_block}` — clusters severity-ordered (🔴 → 🟠 → 🟢 cross-lens). |

Backward-compatible: existing callers reading only `verified`, `unverified`, `iteration_dropped` are unaffected.
