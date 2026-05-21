# Aggregation — A2, sub-80 iteration, dedup, severity tiers

Aggregation is thin glue between lens subagents and the report template. It
applies the postmortem A2 contract (no silent drop), runs the sub-80
iteration pass, deduplicates cross-lens hits, and maps confidence + severity
to the report's tier labels.

## A2 — no silent drop

The earlier `code-review` implementation dropped any finding with
`confidence < 80`. The postmortem at
`~/.claude/output/agent-skills/postmortem/postmortem-code-ultrareview.md`
identified this as a structural hole: real findings were lost to a heuristic
filter. **A2 replaces drop with routing.**

Rules:

- Any finding with `confidence < 80` AND `confidence > 0` is **surfaced**, not dropped.
- Its `finding` text is prefixed `[unverified]`.
- Its `recommendation` text is prefixed with the routing rationale: `Sub-80 confidence ({score}) — verify locally before action.`
- Severity is downgraded to `Low` (regardless of original severity).
- It appears in the report under `### Unverified` (a sub-section of `## Findings`), separate from verified findings.

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
| < 80 | any | (omitted — finding is in Unverified sub-section) |
| (out of diff) | any | Pre-existing |

Pre-existing is flagged by the lens itself when the finding is on an
unchanged line — the synthesizer never re-classifies.

## Order

Within each section (Verified, Unverified), order by:

1. Severity: High → Medium → Low.
2. Confidence: high → low.
3. Location (lexicographic) — stable tiebreak.

## "Clean" notes

A lens that returns zero findings contributes a `Lens <name>: clean.` line
under `## Findings`, not silence. Silence is ambiguous (did the lens run?);
an explicit clean note is unambiguous.

## Implementation

`scripts/aggregation.py` exposes:

- `apply_a2(findings) -> tuple[verified, unverified]` — A2 routing.
- `iterate_unverified(unverified, builder_fn) -> tuple[promoted, remaining, dropped]` — sub-80 iteration; one call per finding.
- `dedupe(findings) -> findings` — cross-lens dedup.
- `assign_anthropic_tier(finding) -> str` — Important / Nit / Pre-existing.
- `order(findings) -> findings` — canonical ordering.

The orchestrator composes them in this order:

```
findings = collect_from_all_lenses()
findings = dedupe(findings)
verified, unverified = apply_a2(findings)
if builder_fn is not None:
    promoted, unverified, _ = iterate_unverified(unverified, builder_fn)
    verified.extend(promoted)
verified = order([assign_anthropic_tier(f) for f in verified])
unverified = order(unverified)
```

Subagent prompts never see the synthesizer — they emit findings; the
orchestrator handles A2, iteration, dedup, ordering.
