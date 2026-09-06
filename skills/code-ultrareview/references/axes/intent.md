# Axis: Intent (key `intent`)

Drift between what the diff DOES and what it CLAIMS to do — PR description vs diff, code vs comment, code vs spec, lockfile vs manifest, generator output vs source. Optional planning-artifact reconciliation activates via `--reconcile`.

## In scope (HIGH SIGNAL)

### Always on

- **PR description vs diff** — PR body claims X; diff does Y (or Y + Z). Compare the PR's `## Summary` bullets against the actual change set.
- **Code vs comment drift** — comment on a changed block states behavior the new code does not exhibit.
- **Code vs spec drift** — code references a normative spec (`RFC <N>`, OpenAPI clause) and contradicts the cited section.
- **Lockfile drift** — `package.json` changed but `package-lock.json` / `pnpm-lock.yaml` did not (or vice versa); `pyproject.toml` vs `uv.lock` / `poetry.lock`; `Cargo.toml` vs `Cargo.lock`.
- **Generator drift** — generated file (`*.generated.*`, `openapi.json` from spec, prisma client) committed without matching source change, or source changed without regenerating.

### Activated by `--reconcile <input>`

Reconcile planning artifacts (forge plans, apex plans, PR body, issue body, `docs/proposals|design|rfcs|adr/`) against the diff. The orchestrator (`scripts/derivation/run.py`) extracts claims; the LLM classifies each as:

| Tag | Meaning | Default severity |
|-----|---------|------------------|
| `GAP` | Planning artifact specified X; the diff does not deliver X | Medium |
| `SCOPE-ADD` | The diff includes X; planning artifact is silent on X | Low |
| `DECISION-OVERRIDE` | Planning resolved decision X; the diff implements Y instead | Medium |
| `CONSISTENT` | Claim verified in the diff (no finding row; the result schema does not emit a per-claim count) | — |

Severity for `GAP` escalates to High when the artifact is a forge plan AND the claim is a numbered acceptance criterion.

#### `--reconcile` input forms

| Token | Meaning |
|-------|---------|
| `@auto` | Auto-detect at conventional paths (forge / apex / PR body) |
| `@pr` | Current branch's PR body via `gh pr view` |
| `<path>` | Explicit file or directory |
| `gh:pr:<N>` | PR by number |
| `gh:issue:<owner>/<repo>#<N>` | Issue by reference |
| GitHub issue URL | Parsed → `gh api` |

Multiple inputs: `--reconcile @auto,gh:pr:42`.

#### Freshness caps

| Age | Behavior |
|-----|----------|
| ≤ 30 days | Default severity from the table above |
| 31–90 days | Auto-discovered historical context: cap at `Low`; explicitly accepted criteria retain consequence-based severity |
| > 90 days | Auto-discovered history is summary-only; explicitly selected or currently accepted criteria remain in scope |

The `--strict` flag disables both caps. Per-repo `.derivation-ignore` overrides allow path or claim allowlists (parser in `scripts/derivation/_common.py:load_ignore`).

## Out of scope (false positives — silence at source)

Anchor: `references/anthropic-verbatim.md` § False-positive taxonomy.

- **Pre-existing drift** on unchanged paragraphs or unchanged code.
- **Intentional decision overrides** the PR body explicitly calls out.
- **Generated-file drift the project explicitly tolerates** (e.g., a `.generated.*` file marked "regenerated in CI on merge").
- **Style drift in PR body** — those belong to the Documentation axis.

## Tool inputs (Phase 2)

No deterministic tool findings route to this axis. The Intent axis is pure LLM judgment against PR metadata, comments, lockfiles, and (when `--reconcile` is set) planning artifacts.

## Severity calibration

- 🔴 High — PR body claims a behavior the diff actively contradicts; `GAP` on a numbered AC in a forge plan; lockfile inconsistency that would break `npm ci` / `pnpm install --frozen-lockfile`.
- 🟠 Medium — comment drift on a changed block; `DECISION-OVERRIDE` against a recent (≤ 30d) planning artifact; minor PR-body / diff mismatch.
- 🟢 Low — `SCOPE-ADD` on a fresh planning artifact; stale planning artifact (31–90d) with any classification; PR-body summary missing a minor side change.

## Repo-kind branches

No branches — planning artifacts (forge, apex, PR/issue bodies, repo `docs/`) are repo-kind-independent. The axis reads the auto-detect set uniformly.

## Subagent inputs

- `scope.json` — repo kind, files touched.
- `tool-findings.jsonl` filtered to `axis: intent` — always empty.
- The diff itself.
- This brief.
- `references/anthropic-verbatim.md` — rubric + false-positive list.
- PR metadata (when `gh` is on PATH and a PR exists for the current branch).
- When `--reconcile` is set: the orchestrator output (`scripts/derivation/run.py --json`) carrying artifact claims as `UNCLASSIFIED` placeholders for the subagent to classify.
