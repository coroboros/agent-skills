# Issue creation

Load this only when `-i` is set. Turns the artifact's workstreams into GitHub issues — a parent epic plus one issue per workstream, labelled and cross-referenced. Never modify code or the artifact body; only append a `## GitHub Issues` section.

## 1. Verify prerequisites

```bash
gh auth status
gh repo view --json nameWithOwner -q '.nameWithOwner'
```

If `gh` is unauthenticated or no repo is detected: tell the user to run `gh auth login`, show the `/apex -f <output_file> implement WS-N` bridge as the fallback, and stop.

## 2. Create labels (idempotent)

`$SKILL_DIR` = this skill's folder — `${CLAUDE_SKILL_DIR}` in Claude Code, the directory containing the skill's SKILL.md elsewhere.

```bash
bash "$SKILL_DIR"/scripts/setup-labels.sh
```

Creates priority (`P0`/`P1`/`P2`), complexity (`size:S`/`size:M`/`size:L`/`size:XL`), and type (`forge`) labels with `--force`, so re-runs are safe.

## 3. Choose strategy

- **1 workstream** → one issue, no parent epic — it would be pointless overhead.
- **2+ workstreams** → parent epic + one child per workstream, created in dependency order (no-dependency workstreams first).

In every `gh issue create`, `{priority}` is the digit only (`0`/`1`/`2`) and `{complexity}` is `S`/`M`/`L`/`XL` — the `P` and `size:` prefixes already live in the label names.

## 4. Create issues

**Single workstream** — one `gh issue create --label "P{priority},size:{complexity},forge"` with a body of `## Description`, `## Tasks` (`- [ ]` items), `## Acceptance Criteria` (`- [ ]` items), and `## Technical Notes` only if present. Footer: `Implement: /apex -f #{issue_number}`. Capture the number, skip to step 5.

**Parent epic** (multi) — `gh issue create --title "Spec: {title}" --label "forge"` with a body of `## Overview`, a `## Workstreams` checklist (`- [ ] WS-N: {title} — P{N}, {complexity}`), and `## Execution Order`. Capture the parent number from the output URL.

**Child issues** (multi) — one per workstream in dependency order, `--label "P{priority},size:{complexity},forge"`. Open the body with `Parent: #{parent_number}` and, when applicable, `Depends on: #{dependency_issue_number}`, then `## Description`, `## Tasks`, `## Acceptance Criteria` (+ `## Technical Notes` if present). After each, store the mapping `WS-N → #issue_number` and use it for cross-references in later issues. If one creation fails: log it, continue the batch, report partial success at the end.

**Update the parent** — `gh issue edit {parent_number}` to replace each `WS-N` in the checklist with its real `#issue_number`.

## 5. Append to the artifact

Read `{output_file}`, append the mapping, write it back.

**Single workstream:**

```markdown

---

## GitHub Issue

**Issue:** #{42} — {title}
**Created:** {YYYY-MM-DD}
```

**Multiple workstreams:**

```markdown

---

## GitHub Issues

| Workstream | Issue | Priority | Complexity |
|------------|-------|----------|------------|
| WS-1: {title} | #{42} | P0 | M |
| WS-2: {title} | #{43} | P0 | L |

**Parent issue:** #{parent_number}
**Created:** {YYYY-MM-DD}
```

## 6. Present summary

Show the created issues and the actionable bridge — `/apex -f "#{issue_number}"` per workstream (single) or per child (multi).

## Failure modes

- Skipping the `gh` auth check.
- Creating a parent epic for a single workstream (overhead).
- Missing cross-references (parent ↔ children, dependencies).
- Aborting the whole batch on one failure instead of reporting partial success.
- Creating children before their dependencies.
- Not appending the `## GitHub Issues` section to the artifact.
