# Axis: Correctness (key `correctness`)

Bugs the diff introduces — logic errors, off-by-one, unhandled `null` / empty, mishandled errors, races, resource leaks, regressions, type errors that a typechecker would NOT catch (because they pass static analysis but break at runtime). Code that no longer matches its own docstring, inline comment, or invariant.

## In scope (HIGH SIGNAL)

Anchor: `references/anthropic-verbatim.md` § HIGH SIGNAL review criteria (Agent #2 — obvious bugs; Agent #5 — comment compliance).

- Logic errors on changed lines — wrong condition, off-by-one, swapped operands, broken iteration bounds.
- Unhandled error classes — `null`, empty, `undefined`, missing key, exception swallowed.
- Race conditions and resource leaks — unawaited promises, unclosed handles, missing locks.
- Single-source-of-truth violations — a literal (path, URL, endpoint, constant, version, env-var name) duplicated by the diff in two or more places, where divergence would break behavior. Cite both sites.
- Docstring / comment drift — the diff makes code disagree with the comment on the same line or block.
- Spec-claim divergence — when the diff, README, or CLAUDE.md cites a named normative spec (`RFC <N>`, `WHATWG`, `ISO/IEC <N>`, `OpenAPI`), and the implementation contradicts a quoted clause. Spec text is the evidence; confidence ≥ 80.

## Out of scope (false positives — silence at source)

Anchor: `references/anthropic-verbatim.md` § False-positive taxonomy.

- Pre-existing bugs on lines the diff does not touch — surfaces as `Pre-existing` tier, never flips the verdict.
- Anything a typechecker / compiler / linter would catch — type errors, missing imports, formatting. CI handles those.
- Stylistic preferences without a CLAUDE.md rule — `style` axis owns those.
- Intentional behavior changes related to the diff's purpose — not bugs.
- Real bugs on unchanged lines — out of scope; the diff did not cause them.

## Tool inputs (Phase 2)

From `scripts/battery_ingest.py:TOOL_TO_AXIS`:

- No deterministic tool findings route to Correctness from the standard battery.
- Semgrep runs only the bundled `code-ultrareview-*` performance rules; every accepted Semgrep finding routes to the Performance axis. Generic or mismatched Semgrep rules invalidate the report instead of falling back to Correctness.

Correctness is an LLM-judgment axis and always runs even though its filtered tool input is empty.

## Severity calibration

- 🔴 High — runtime crash, silent data corruption, security implication on a changed line.
- 🟠 Medium — wrong result under realistic input, recoverable but visible, regression in a tested code path.
- 🟢 Low — edge case unlikely in practice, minor inconsistency, comment drift without functional impact.

## Repo-kind branches

| `repo_kind` | Behavior |
|-------------|----------|
| `skills` | Docstring drift reframes from "code vs docstring" to "bundled `scripts/` vs SKILL.md spec". SKILL.md is the canonical spec — it cannot drift from itself. Fire when SKILL.md declares a flag absent from a script's parser, or an output schema the script doesn't emit. Pure-prompt skills (no `scripts/`) emit zero drift findings. |
| `app`, `library` | Existing behavior — code vs docstring vs README claim. |
| `python` | Triple-quoted docstrings are the surface. |
| `rust` | `///` doc comments are the surface. |
| `go` | `// godoc` comments are the surface. |
| `docs` | No executable surface — axis emits zero findings; the report's `Repo: docs` header carries the context. |
| `monorepo` | Per-workspace specialization parked at MVP; subagent applies the most-permissive ruleset (treat as code repo). |
| `unknown` | Existing behavior. |

## Subagent inputs

The Phase 3 orchestrator passes:

- `scope.json` — repo kind, languages, files touched, CLAUDE.md chain.
- `tool-findings.jsonl` filtered to `axis: correctness` — empty under the standard battery.
- The diff itself (resolved by Phase 1).
- This brief.
- `references/anthropic-verbatim.md` — rubric + false-positive list.
