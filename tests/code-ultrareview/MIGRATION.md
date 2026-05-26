# code-ultrareview test migration

Reference for the WS-7 merge gate. Deleted before merge.

The rebuild swaps the 7-lens taxonomy for an 8-axis pipeline. This file maps every legacy test file to its fate so reviewers can verify no coverage was silently dropped. Status reflects what's in `tests/code-ultrareview/` on the merge candidate.

## Mapping

| Test file | Fate | Rationale |
|-----------|------|-----------|
| `test_aggregation.py` | REUSE | A2 no-silent-drop primitives still pin behavior carried into `synthesis_core.py`. |
| `test_verdict.py` | REUSE | `aggregation.compute_verdict` carries forward; `synthesis_core.compute_verdict` builds on the same algorithm. |
| `test_classify_repo.py` | REUSE | Repo-kind detection feeds `scope.py`. |
| `test_resolve_base.py` | REUSE | Clean-tree base resolver — Phase 1 input. |
| `test_audit_signals.py` | REUSE | `scope.py` imports `audit_signals` for manifest delta / public-API / security-path detection. |
| `test_audit_summary.py` | REUSE | Confidence-tier aggregator feeding scope output. |
| `test_prose_hygiene.py` | REUSE | Carried into the Documentation axis via `check_prose_hygiene.py`. |
| `test_fetch_commits.py` | REUSE | Phase 1 input for the Intent axis. |
| `test_fetch_pr_meta.py` | REUSE | Phase 1 input for the Intent axis. |
| `test_detect_skills.py` | REUSE | `aggregation.py` lazy-loads `detect_skills.py` for skill routing in the carry-along path. |
| `test_remote_stub.py` | REUSE | Stub harness for the `gh`-bypass code paths used by `coherence/` and `derivation/`. |
| `test_coherence_graph.py` | KEEP — deviates from spec | Spec said DROP and replace with `test_axis_coherence.py`. The `coherence/` orchestrator (six sub-graphs) is still live code that the Coherence axis brief routes through; per-graph tests pin behavior the axis brief depends on. `test_axis_briefs.py` covers brief-doc presence and structure; `test_coherence_graph.py` covers the script-level orchestrator. Both surfaces matter. |
| `test_derivation_graph.py` | KEEP — deviates from spec | Spec said carry as `test_optional_reconcile.py`. The file already pins the live `derivation/` orchestrator (auto-detect, extractor, classification taxonomy) that `--reconcile` routes through. Renaming would add churn for no behavioral change; `test_optional_features.py` covers the flag wiring, and this file covers the orchestrator internals. |
| `test_section_emoji_drift.py` | KEEP — deviates from spec | Spec said carry as `test_report_template.py`. Both files coexist — `test_report_template.py` pins the template itself; `test_section_emoji_drift.py` pins every other doc (SKILL.md, references, evals) against plain-heading drift. Distinct regression guards for distinct surfaces; both stay. |
| `test_lens_repo_kind_sections.py` | DROP | Tests the legacy `references/lens-*.md` repo-kind tables. The 8-axis briefs at `references/axes/*.md` replace the lenses and pin their own structure via `test_axis_briefs.py`. |
| `test_lens_summary.py` | DROP | Tests `aggregation.compute_lens_summary` against the 7-lens canonical list. The new pipeline emits an axis summary via `synthesize.py`, covered by `test_synthesis.py`. |
| `test_severity_markers.py` | DROP | Tests `aggregation._attach_marker` / `apply_a2` / `synthesize` marker propagation. Superseded by `synthesis_core.SEVERITY_MARKERS` + `test_synthesis_core.py`. |
| `test_action_plan.py` | DROP | Tests `aggregation.compute_action_plan` — the new architecture emits axis-level findings + verdict, not lens-clustered action plans. The closing report layout is pinned by `test_report_template.py`. |

## New tests added by WS-1 through WS-6

| File | Workstream | Coverage |
|------|------------|----------|
| `test_scope.py` | WS-1 | `scope.py` — diff resolution, repo-kind classification, CLAUDE.md chain, Coherence activation. |
| `test_anthropic_verbatim.py` | WS-1 | Byte-parity check between `references/anthropic-verbatim.md` and the upstream `claude-plugins-official` blocks. |
| `test_battery.py` | WS-2 | `run_battery.sh` per-language dispatch, graceful skip on missing tools, no auto-install. |
| `test_battery_ingest.py` | WS-2 | Per-tool axis routing in `battery_ingest.py` + canonical finding schema. |
| `test_axis_briefs.py` | WS-3 | Eight axis brief files + Coherence conditional — structure, repo-kind branches, anthropic-verbatim citation. |
| `test_axis_dispatch.py` | WS-3 | `axis_dispatch.py prepare` — bundle generation, per-axis finding filter, Coherence gating. |
| `test_validators.py` | WS-4 | `run_validators.py` — Haiku batching ≤10, CLAUDE.md re-check, A2 promote/demote, 100-confidence skip. |
| `test_synthesis_core.py` | WS-5 | `synthesis_core.py` primitives — `SEVERITY_MARKERS`, `AXIS_PRIORITY`, `compute_verdict`, `iterate_unverified`. |
| `test_synthesis.py` | WS-5 | `synthesize.py` end-to-end — dedup, inter-axis precedence, A2 routing, "What I did NOT check" closing. |
| `test_findings_jsonl.py` | WS-5 | `findings_to_jsonl.py` — Conventional Comments label mapping + permalink format. |
| `test_report_template.py` | WS-5 | `templates/code-ultrareview.md` — section order, emoji discipline, terminal-echo rule. |
| `test_optional_features.py` | WS-6 | Flag wiring — `--verify-build`, `--mutation-test`, `--reconcile`, `--apply-safe`. No flag → feature off. |

## Per-axis split decision

WS-3 task list suggested per-axis test files (`test_axis_simplification.py`, `test_axis_correctness.py`, etc.). The implementation consolidates these into `test_axis_briefs.py` (24 test methods across 13 test classes, one class per axis plus structural classes). Rationale: each axis brief is a markdown reference doc, so the tests pin doc structure rather than runtime behavior. One file with per-axis classes reads naturally and avoids 9 nearly-identical test modules. Runtime-level axis behavior (dispatch, filtering, finding emission) lives in `test_axis_dispatch.py`.

## Removal

Delete this file with the squash commit on merge. Until then it carries the WS-7 reviewer's mapping.
