# Derivation lens — code↔plan reconciliation

Apex's step-04 examine compares the actual diff against the saved plan (`02-plan.md`) and classifies each divergence. Catches the failure class typecheck/lint/tests cannot: "implemented the wrong thing" or "added scope creep".

**Canonical taxonomy** lives at `skills/code-ultrareview/references/axes/intent.md` — the Intent axis owns the derivation sub-mode. This file is apex's standalone profile of that taxonomy plus the detection + inline-fallback protocol so apex's examine stays runnable when code-ultrareview is not installed.

## Classifications

| Tag | Meaning | Default severity | Apex behaviour |
|-----|---------|------------------|----------------|
| `GAP` | Plan said X; diff does not deliver X | High | **Block completion**. Surface planned-but-missing items. |
| `SCOPE-ADD` | Diff includes X; plan is silent on X | Low | Advisory. Escalate to **Medium and require user ack** when the addition matches a `## Not Included` entry from step-01's negative scope. |
| `DECISION-OVERRIDE` | Plan resolved decision X; diff implements Y instead | Medium | Surface for user judgment. Do **not** block — the override may be intentional. |
| `CONSISTENT` | Claim verified in the diff | — | Counted in coverage. No finding row. |

Minor scaffolding in service of a planned change (test helpers, small extractions) is NOT a SCOPE-ADD finding — the planned claim implicitly covers its implementation needs.

## Detection protocol

Step-04 first detects whether code-ultrareview's Python orchestrator is available:

```bash
ORCHESTRATOR=""
if [ -f "${HOME}/.claude/skills/code-ultrareview/scripts/derivation/run.py" ]; then
  ORCHESTRATOR="${HOME}/.claude/skills/code-ultrareview/scripts/derivation/run.py"
elif [ -f "$(git rev-parse --show-toplevel)/skills/code-ultrareview/scripts/derivation/run.py" ]; then
  ORCHESTRATOR="$(git rev-parse --show-toplevel)/skills/code-ultrareview/scripts/derivation/run.py"
fi
```

If `$ORCHESTRATOR` is set, invoke it for deterministic findings:

```bash
python3 "$ORCHESTRATOR" \
  --repo "$(git rev-parse --show-toplevel)" \
  --reconcile "$output_dir/02-plan.md" \
  --json
```

Parse the JSON output. Each finding carries `classification`, `severity`, `finding`, `recommendation`, `location`. Apply the apex severity rules above.

If no orchestrator is found, run the inline protocol below.

## Inline protocol (fallback)

When code-ultrareview is not installed:

1. **Read** `{output_dir}/02-plan.md` from the current apex task workspace.
2. **Compute the diff**:
   - If `{branch_mode}` was true: `git diff main...HEAD` (or `develop...HEAD` per the repo's source branch — check the repo's `CLAUDE.md` to confirm).
   - Otherwise: `git diff $(git merge-base HEAD origin/HEAD)...HEAD`, falling back to `git diff HEAD` if no upstream is tracked.
3. **Extract plan claims** from `02-plan.md`:
   - Acceptance criteria (Given/When/Then bullets, from step-01 § 5 or the spec's workstreams when § 0a Spec AC closure applied).
   - Negative scope (`## Not Included` entries).
   - File-level changes (paths called out in the file-by-file plan).
4. **Classify each claim** against the diff:
   - Plan AC matched in diff → CONSISTENT.
   - Plan AC absent from diff → GAP.
   - Diff change with no matching AC AND not adjacent to a planned change → SCOPE-ADD. If the change matches a `## Not Included` entry → escalate severity per the table.
   - Plan said approach A but diff shows approach B → DECISION-OVERRIDE.
5. **Surface findings** to step-04 output (`04-examine.md`):

```
**Derivation lens:** GAP: <n> · SCOPE-ADD: <n> (advisory) · DECISION-OVERRIDE: <n> · CONSISTENT: <n>
```

## Step-04 gating

After the lens runs:

- GAP findings → workflow **blocks**. User addresses each GAP (implement the missing piece OR amend the plan + AC) before step-04 completes.
- SCOPE-ADD findings → workflow **continues**. Surface for awareness. Medium escalations (matched negative scope) require user acknowledgement.
- DECISION-OVERRIDE findings → workflow **continues**. Surface for user judgment.
- All-CONSISTENT → no findings; step-04 proceeds to typecheck/lint/tests.

## See also

- `skills/code-ultrareview/references/axes/intent.md` — canonical Intent axis brief; carries the four classifications, default severities, freshness rules, and allowlist (`.derivation-ignore`). Apex inherits the taxonomy verbatim.
- `skills/code-ultrareview/references/ultra-execution.md` — operational details for `--reconcile`: orchestrator entry point, `@auto` / `@pr` / `gh:pr:` input modes, freshness caps, full finding schema.
- `skills/code-ultrareview/scripts/derivation/run.py` — Python orchestrator apex invokes when available.
