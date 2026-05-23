# Derivation lens — reconcile planning artifacts vs the diff

The sixth lens in the code-ultrareview family. Closes the code↔internal-plan
axis (parallel to bugs-drift / code↔own-docstring, coherence-graph /
code↔manifest, spec-conformance / code↔external-spec). Activates on
`--reconcile <input>` and compares planning artifacts (forge, apex plan,
PR body, issue body) against the diff, classifying each
divergence as **GAP** (planning said X, code missing), **SCOPE-ADD** (code
has X, planning silent), **DECISION-OVERRIDE** (planning resolved X, code
does Y), or **CONSISTENT**.

## Dispatch protocol

One `Explore` subagent per derivation lens run. The subagent invokes the
orchestrator:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/derivation/run.py" \
  --repo "<repo>" --reconcile "<inputs>" [--strict] --json
```

The Python orchestrator owns the **deterministic** half — resolving
`--reconcile` inputs to a list of artifacts, extracting claims (AC items,
Goals, Decisions, Tasks) from each, applying freshness rules + the
`.derivation-ignore` allowlist, and emitting one `UNCLASSIFIED` finding
per claim.

The LLM subagent reads the orchestrator output, compares each claim against
the diff, and rewrites the finding's `classification` field to GAP /
SCOPE-ADD / DECISION-OVERRIDE / CONSISTENT, adjusting `severity` and
`confidence` accordingly. The Python module does **not** make the semantic
comparison — that's the subagent's contract.

## Input forms (`--reconcile`)

| Token | Meaning |
|-------|---------|
| `@auto` | Auto-detect at conventional paths (see below) |
| `@pr` | Current branch's PR body, via `gh pr view --json body` |
| `<path>` | Explicit file or directory of `.md` files |
| `gh:pr:<N>` | PR by number (current repo) |
| `gh:issue:<owner>/<repo>#<N>` | Issue by reference |
| `https://github.com/<o>/<r>/issues/<N>` | Issue URL (parsed → gh api) |

Multiple inputs may be comma-separated: `--reconcile @auto,gh:pr:42`.

## Auto-detection set (`@auto`)

```
~/.claude/output/{project}/forge/forge-*.md
~/.claude/output/{project}/apex/{NN-task}/02-plan.md  (latest task only)
docs/proposals/*.md  docs/design/*.md  docs/rfcs/*.md  docs/adr/*.md
gh pr view (current branch's PR body)
```

`{project}` resolves to the kebab-case basename of `git rev-parse --show-toplevel`
(see `.claude/rules/repo-conventions.md` § Output paths).

The APEX glob is intentionally narrow: APEX writes an ordered task tree
(`NN-feature-name/`), and only the latest task's `02-plan.md` matters for
the current state of intent. Older plans are out-of-scope.

Sources that don't exist are silently skipped. Missing `gh` cli, no PR for
the current branch, or no `~/.claude/output/{project}/` directory all
degrade silently — the orchestrator only returns the sources it found.

## Interactive launch prompt

When `--reconcile @auto` resolves to multiple candidates **and** stdin is
a TTY, the dispatching skill surfaces the candidate list and prompts the
user before fan-out:

```
Found 3 planning artifacts:
  1. ~/.claude/output/{project}/forge/forge-derivation-lens.md (2d)
  2. ~/.claude/output/{project}/apex/03-derivation-lens/02-plan.md (1d)
  3. PR #43 body (0d)

Use these for the derivation lens? [Y/n/list other]
```

Non-TTY (CI, batch) skips the prompt — the auto-detected set is used
verbatim. When `--reconcile` resolves to nothing, the prompt asks for an
explicit path/URL; the lens skips silently when the user declines.

## Classification taxonomy

| Tag | Meaning | Default severity |
|-----|---------|------------------|
| `GAP` | Planning artifact specified X; the diff does not deliver X | Medium |
| `SCOPE-ADD` | The diff includes X; planning artifact is silent on X | Low |
| `DECISION-OVERRIDE` | Planning resolved decision X; the diff implements Y instead | Medium |
| `CONSISTENT` | Claim verified in the diff (no finding row; counted in coverage) | — |

Severity for GAP escalates to High when the artifact is a forge plan and
the claim is a numbered acceptance criterion. Severity for DECISION-OVERRIDE
varies by artifact authority: forge plan < explicit AC.

`UNCLASSIFIED` is the Python-stage placeholder before the subagent fills
in the classification. Consumers should treat it as in-flight, not as
final lens output.

## Freshness signal

Each artifact carries a `freshness_days` value from `git log -1 --format=%ct`
(or `mtime` outside a repo). The lens uses two thresholds:

| Age | Behavior |
|-----|----------|
| ≤30 days | Default severity from the table above |
| 31–90 days | Cap severity at `Low` regardless of classification |
| >90 days | Skip findings entirely — artifact appears in the coverage summary only |

The `--strict` flag disables both freshness caps. Per-repo overrides live
in `.derivation-ignore` (see below).

## `.derivation-ignore` allowlist

Per-repo allowlist at repo root. Same minimal YAML subset as
`.coherence-ignore`:

```yaml
# Skip specific planning artifacts (full or substring path match).
paths:
  ignore_paths:
    - ~/.claude/output/{project}/forge/forge-legacy.md
  ignore_kinds:
    - rfc

# Suppress specific claim text (exact match).
claims:
  ignore_text:
    - "out of scope per the v2 milestone"
```

Parser lives in `scripts/derivation/_common.py` (`load_ignore`). Unknown
keys are tolerated (forward-compat); malformed indentation raises
`ValueError`.

## Finding schema

Each finding matches the canonical lens schema, with derivation-specific
extras:

```json
{
  "lens": "derivation",
  "classification": "GAP | SCOPE-ADD | DECISION-OVERRIDE | CONSISTENT | UNCLASSIFIED",
  "severity": "High | Medium | Low",
  "location": "<artifact-path>:<source_line>",
  "finding": "<claim text — what the artifact asked for>",
  "recommendation": "<what to do — fill in by subagent during classification>",
  "confidence": 0,
  "artifact_path": "<resolved path or gh: reference>",
  "artifact_freshness_days": 12
}
```

Confidence is `0` until the subagent classifies (then `≥80` for GAP /
DECISION-OVERRIDE with evidence, lower for SCOPE-ADD on judgment).

## Orchestrator output

```json
{
  "lens": "derivation",
  "artifacts": [
    {"path": "...", "kind": "spec", "freshness_days": 2, "claim_count": 54}
  ],
  "findings": [...]
}
```

The `## 📐 Derivation coverage` section in the report template renders:

- Artifacts compared (with freshness)
- AC coverage (verified vs total)
- Classifications: GAP <n> · SCOPE-ADD <n> · DECISION-OVERRIDE <n> · CONSISTENT <n>
- Notable callouts (top 1-3 if any)

## Graceful degradation

- `gh` missing → PR/issue inputs skipped; auto-detected set excludes the PR body. Header notes the skip.
- `~/.claude/output/{project}/` missing → auto-detect returns only the repo-local `docs/` artifacts.
- `git` missing → freshness falls back to `mtime`; `_in_git_repo` returns False silently.
- Empty input set after resolution → lens skips entirely (no finding rows, no coverage section); the orchestrator notes "no planning artifacts found" in the header.

## Caveats

- The Python scaffold extracts AC / Goals / Decisions / Tasks. Other claim
  shapes (prose paragraphs, tables) are out of scope at MVP. Subagents
  may identify additional implicit claims at classification time.
- `gh:pr:current` is a sentinel path — the body is fetched at run time.
- Cap of 5 findings per artifact (Risk #2 — overcorrection guard) bounds
  the report size; `--strict` removes the cap.
- Auto-detect's APEX path expects the canonical `NN-feature-name/` task
  shape (per `skills/apex/SKILL.md`). Custom apex output paths are out
  of scope.

## Fixtures

Derivation fixtures live under `tests/code-ultrareview/fixtures/derivation/`,
one directory per classification scenario:

| Fixture | Expected behavior |
|---------|-------------------|
| `gap/` | One planning artifact with an AC the diff doesn't implement |
| `scope-add/` | Diff implements a feature the artifact is silent on |
| `decision-override/` | Artifact resolves decision X; diff does Y |
| `consistent/` | Every claim has a matching reference in the diff |
| `stale-artifact/` | Artifact freshness >30d — severity capped to Low |
| `allowlisted/` | Claim matches `.derivation-ignore` — no finding emitted |

The fixtures exercise the Python orchestrator's deterministic shape — the
LLM-driven classification is mocked at the subagent boundary (tests assert
the UNCLASSIFIED scaffolding, not the final classification).
