# claude-md optimize

Optimize the requested instruction files while preserving their accepted behavior. `$SKILL_DIR` means the directory containing this skill's SKILL.md, or `${CLAUDE_SKILL_DIR}` in Claude Code.

## Inspect the scope

Read the target and relevant owner instructions. For a repository-wide audit, inventory all requested instruction files; for a focused edit, do not force unrelated reading.

Run `python3 "$SKILL_DIR"/scripts/audit_claude_md.py <path>` and read `references/optimize-guide.md`. The JSON contains heuristic candidates, not a fix list. Inspect applicable tooling and source files before deciding a rule is redundant.

## Edit the owner

Remove obsolete or duplicated instructions only after confirming the retained source covers their purpose. Keep useful commands, tool choices, boundaries and reasons. Preserve path-scoped loading with ordinary links; reserve eager imports for universal content.

Apply the authorized edits. If the request was assessment-only, return the proposed diff instead. Retain explicit checkpoints and ask only for an unresolved user-owned decision or scope expansion.

## Verify and report

Check imports, scoped-rule parsing and command accuracy. Exercise representative behavior for changed routing or authorization rules. Report material removals and verification limits. Under 200 lines is a guideline; line reduction alone does not prove improved adherence.
