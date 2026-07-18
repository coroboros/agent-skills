# code-ultrareview test + script migration

Reference for the WS-7 merge gate. Deleted before merge.

The rebuild swaps the 7-lens taxonomy for an 8-axis pipeline. This file documents every legacy surface's fate (DELETED / KEPT / DELETED-LATER) and the new test coverage that pins the same behaviours, so reviewers can verify no contract was silently dropped.

## Legacy scripts — deleted in this PR

| Script | Why deleted | Behaviour preserved by |
|--------|-------------|------------------------|
| `aggregation.py` | A2 routing, severity attachment, verdict, dedup, iterate_unverified, anthropic tier classification, severity counts, action plan, lens summary | `synthesis_core.py` (A2, iterate_unverified, severity, verdict, dedup-by-precedence, anthropic tier, severity counts) — pinned by `test_synthesis_core.py`. Action plan + lens summary are dropped concepts: the 8-axis pipeline emits axis-level findings + verdict, not lens-clustered action plans. |
| `audit_signals.py` | Repo-kind detection (9 kinds + signals + override precedence) | `scope.py:classify_repo` re-implements the same algorithm — pinned by `test_scope.py` (40 tests; the 9 kinds + compound cases + override mechanism + CLI exit-2 ported from the legacy `test_classify_repo.py`). |
| `audit_summary.py` | Confidence-tier aggregator feeding scope output | `synthesis_core.assign_anthropic_tier` — pinned by `test_synthesis_core.py`. |
| `check_prose_hygiene.py` | Deterministic prose-hygiene scanner (PR body + commits + user-facing `*.md`) | Documentation axis brief (`references/axes/documentation.md`) describes the same Tier 1 / Tier 2 patterns, leak table, AI vocabulary list, em-dash density rules — the LLM judge applies them in Phase 3. The deterministic-script implementation is dropped intentionally; the 8-axis design moves judgment-heavy prose checks to the LLM subagent. |
| `detect_skills.py` | Skill-routing detection (used by the legacy lens-summary path) | No replacement — concept dropped. The new pipeline does not route findings through skill-detection; opt-in `--apply-safe` writers have their own entry point. |
| `harness_synth.py` | Property-test skeleton synthesiser (fast-check / hypothesis) | No replacement — concept dropped. The new pipeline does not generate test skeletons; the Tests axis surfaces gaps and recommends fixes. |
| `remote_stub.py` | Stub harness for the `gh`-bypass code paths used by the old `coherence/` and `derivation/` orchestrators | No replacement needed — the live `coherence/` and `derivation/` orchestrators degrade gracefully when `gh` is absent without a stub layer. |
| `spec_claim.py` | A1 spec-claim extraction used by the legacy aggregation flow | No replacement — concept dropped. The Intent axis subagent owns spec-vs-diff reconciliation now (via `--reconcile`). |
| `spec_conformance.py` | WebFetch + cache layer for spec-conformance findings | Not part of MVP. The Coherence axis's `spec-conformance` sub-graph is a stub placeholder (`scripts/coherence/spec_conformance_graph.py`) per `references/axes/coherence.md`. Full grammar inference + cache layer remains parked. |

## Legacy references — deleted in this PR

`aggregation.md` · `audit-phase.md` · `lens-bugs-drift.md` · `lens-coherence-graph.md` · `lens-derivation.md` · `lens-docs-version.md` · `lens-prose-hygiene.md` · `lens-rules.md` · `lens-tests-blindspots.md` · `lenses.md` · `remote-escalation-design.md` · `skill-routing.md` · `verdict-logic.md`

The 8-axis equivalents are in `references/axes-overview.md` + `references/axes/<axis>.md` (one brief per axis + Coherence). Verdict logic moves to the `synthesis_core.compute_verdict` docstring + `references/axes-overview.md` § *Inter-axis precedence*. Coherence sub-graphs are documented in `references/axes/coherence.md`.

## Legacy tests — deleted in this PR

| Test file | Reason | Equivalent coverage now in |
|-----------|--------|-----------------------------|
| `test_aggregation.py` | Tested `aggregation.py` (deleted) | `test_synthesis_core.py` (A2, iterate_unverified, tier, ordering) + `test_synthesis.py` (end-to-end) |
| `test_audit_signals.py` | Tested `audit_signals.py` (deleted) | `test_scope.py` covers the surviving public surface (`classify_repo`); the legacy script's lens-summary + action-plan helpers are dropped concepts |
| `test_audit_summary.py` | Tested `audit_summary.py` (deleted) | `test_synthesis_core.py` (`assign_anthropic_tier`) |
| `test_classify_repo.py` | Tested `audit_signals.classify_repo` (deleted) | Edge cases ported into `test_scope.py` — `TestRepoKindCompoundCases`, `TestRepoKindOverrideMechanism`, `TestRepoKindCLI` (10 ported tests, all GREEN). |
| `test_detect_skills.py` | Tested `detect_skills.py` (deleted; concept dropped) | None — surface intentionally removed |
| `test_prose_hygiene.py` | Tested `check_prose_hygiene.py` (deleted) | Documentation axis brief documents the patterns as LLM judgment inputs (no longer deterministic) |
| `test_remote_stub.py` | Tested `remote_stub.py` (deleted) | None — surface intentionally removed |
| `test_verdict.py` | Tested `aggregation.compute_verdict` (deleted; new verdict in `synthesis_core.compute_verdict` returns "Eight axes ran clean" instead of "Six lenses ran clean") | `test_synthesis_core.py` (`TestComputeVerdict`) — 5 verdict tests pin the new algorithm |

## Legacy test classes — pruned from kept files

In `tests/code-ultrareview/test_ultra_execution.py`:

| Class | Why pruned | Replacement |
|-------|-----------|-------------|
| `TestSpecConformanceCache` | Tested the deleted `spec_conformance.py` cache layer | None — surface dropped (MVP) |
| `TestHarnessSynth` | Tested the deleted `harness_synth.py` skeleton generator | None — concept dropped |

Kept in `test_ultra_execution.py`: `TestBuildDetect`, `TestVersionSync`, `TestDescriptionSync`, `TestFailingTestWriter`, `TestApplySafeConfirm` — all exercise live carried code (`scripts/build_detect.py`, `scripts/apply_safe/*`).

## Legacy tests — kept (deviates from original spec, justified)

| Test file | Why kept | Live target |
|-----------|----------|-------------|
| `test_coherence_graph.py` | Spec said DROP; the `scripts/coherence/` orchestrator is still live code that the Coherence axis brief routes through. Per-graph tests pin behaviour the axis brief depends on. `test_axis_briefs.py` covers brief-doc presence; this file covers the script-level orchestrator. | `scripts/coherence/*.py` |
| `test_derivation_graph.py` | Spec said carry as `test_optional_reconcile.py`. Renaming adds churn for no behavioural change. `test_optional_features.py` covers the `--reconcile` flag wiring; this file covers the orchestrator internals. | `scripts/derivation/*.py` |
| `test_section_emoji_drift.py` | Spec said carry as `test_report_template.py`. Both files coexist with distinct regression surfaces: `test_report_template.py` pins the template; this file pins every other doc (SKILL.md, references, evals) against plain-heading drift. | `skills/code-ultrareview/SKILL.md`, `references/*.md`, `evals/evals.json` |
| `test_ultra_execution.py` (kept classes — see above) | Pins the live carried opt-in scripts (`build_detect.py`, `apply_safe/*`) | `scripts/build_detect.py`, `scripts/apply_safe/*.py` |
| `test_fetch_commits.py` · `test_fetch_pr_meta.py` · `test_resolve_base.py` | Pin the live carried shell scripts used by Phase 1 scope + Intent axis | `scripts/fetch_commits.sh`, `scripts/fetch_pr_meta.sh`, `scripts/resolve_base.sh` |

## New tests added by WS-1 through WS-7

| File | Workstream | Coverage |
|------|------------|----------|
| `test_scope.py` | WS-1 | `scope.py` — diff resolution, repo-kind classification (9 kinds + compound + override + CLI), CLAUDE.md chain, Coherence activation, languages detection (40 tests) |
| `test_anthropic_verbatim.py` | WS-1 | Byte-parity between `references/anthropic-verbatim.md` and the upstream `claude-plugins-official` blocks |
| `test_battery.py` | WS-2 | `run_battery.sh` per-language dispatch, atomic missing/invalid-tool gates, no auto-install |
| `test_battery_ingest.py` | WS-2 | Per-tool axis routing + canonical finding schema for all 14 parsers |
| `test_axis_briefs.py` | WS-3 | Eight axis briefs + Coherence conditional — structure, repo-kind branches, anthropic-verbatim citation |
| `test_axis_dispatch.py` | WS-3 | `axis_dispatch.py prepare` — bundle generation, per-axis filter, Coherence gating, parallel cap |
| `test_validators.py` | WS-4 | `run_validators.py` — Haiku batching ≤10, CLAUDE.md re-check, A2 promote/demote, 100-confidence skip |
| `test_synthesis_core.py` | WS-5 | `synthesis_core.py` primitives — `SEVERITY_MARKERS`, `AXIS_PRIORITY`, `compute_verdict`, `iterate_unverified`, `assign_anthropic_tier`, `dedup_by_precedence` |
| `test_synthesis.py` | WS-5 | `synthesize.py` end-to-end — dedup, inter-axis precedence, A2 routing, "What I did NOT check" closing |
| `test_findings_jsonl.py` | WS-5 | `findings_to_jsonl.py` — Conventional Comments label mapping + permalink format |
| `test_report_template.py` | WS-5 | `templates/code-ultrareview.md` — section order, emoji discipline, terminal-echo rule |
| `test_optional_features.py` | WS-6 | Flag wiring — `--verify-build`, `--mutation-test`, `--reconcile`, `--apply-safe`. No flag → feature off |

## Per-axis split decision

WS-3 task list suggested per-axis test files (`test_axis_simplification.py`, `test_axis_correctness.py`, …). The implementation consolidates these into `test_axis_briefs.py` (24 test methods across 13 test classes — one class per axis plus structural classes). Rationale: each axis brief is a markdown reference doc, so the tests pin doc structure rather than runtime behaviour. One file with per-axis classes reads naturally and avoids 9 nearly-identical test modules. Runtime axis behaviour (dispatch, filtering, finding emission) lives in `test_axis_dispatch.py`.

## Carried-live (not deleted, not legacy)

Live scripts the new pipeline calls explicitly (per `SKILL.md` § References):

- `scripts/resolve_base.sh` — Phase 1 base resolver
- `scripts/fetch_commits.sh` · `scripts/fetch_pr_meta.sh` — Phase 1 Intent axis input
- `scripts/build_detect.py` — Phase 3.5 `--verify-build` input
- `scripts/coherence/*.py` — Coherence axis orchestrator (six sub-graphs)
- `scripts/derivation/*.py` — Intent axis `--reconcile` orchestrator
- `scripts/apply_safe/*.py` — `--apply-safe` writers (version_sync, description_sync, failing_test_writer)

## Removal

Delete this file with the squash commit on merge. Until then it carries the WS-7 reviewer's mapping + the cleanup-pass audit trail.
