---
name: step-02-specify
description: Write the structured spec document with workstreams, priorities, dependencies, and acceptance criteria
prev_step: steps/step-01-discover.md
next_step: steps/step-03-issues.md
---

# Step 2: Specify

## Role

You are a specifier. Transform the discovery findings from step-01 into a complete, actionable spec with prioritized workstreams and testable acceptance criteria. Do not implement anything — no code changes, no file creation except the spec itself. Issue creation is step-03's job.

Focus on the question "What needs to be done, in what order, and how will we know it's done?"

## Available state

From previous steps:

| Variable | Description |
|----------|-------------|
| `{idea}` | Feature description |
| `{project}` | Repo basename — keys the output dir |
| `{slug}` | Kebab of the idea (≤5 words) — names the spec file |
| `{auto_mode}` | Skip confirmations |
| `{save_mode}` | Save spec to file |
| `{issues_mode}` | Create GitHub issues |
| `{output_dir}` | Output directory path |
| `{output_file}` | `{output_dir}spec-{slug}.md` (fully-expanded absolute path) |
| Discovery findings | From step-01 (codebase context, requirements, constraints, assumptions) |

## Reference: priority & complexity

**Priority:**
- **P0** — Must have. Without this, the feature doesn't function. Ship first.
- **P1** — Should have. Important for completeness. Ship in the same release.
- **P2** — Nice to have. Can be deferred. Ship when convenient.

**Complexity** (AI coder time via `/apex`):
- **S** — Under 1 hour. Single file, straightforward change following existing patterns.
- **M** — 1-4 hours. Multiple files, some decision-making required.
- **L** — 4-8 hours. Cross-cutting changes, new patterns needed.
- **XL** — Over 1 day. Major feature spanning multiple subsystems.

## Execution

### 1. ULTRA THINK: decompose the work

Before writing anything, mentally decompose `{idea}` into natural workstreams:

- What are the distinct units of deliverable work?
- What must come first (foundational, blocking others)?
- What's the minimum viable path (all P0 workstreams)?
- What can be deferred without blocking the core (P1, P2)?
- Are there cross-cutting concerns (auth, validation, error handling) that deserve their own workstream?

**Workstream guidelines:**

- **Target 3-7 workstreams.**
- Fewer than 3: the idea is probably simple enough for `/oneshot` or a direct `/apex` — note this but produce a lean spec anyway.
- More than 7: the idea may need to be split into multiple specs — suggest this to the user.
- Each workstream should be independently implementable via a single `/apex` run.
- Each workstream should have a clear, single deliverable.

**Before finalizing priorities and goals:**

- **P0 ruthlessness** — if everything is P0, nothing is. For each P0, ask: would we genuinely refuse to ship without this? If the core problem is still solved without it, it is P1.
- **Goals are outcomes, not outputs** — "cut X from N to M", not "build the wizard". A goal markable done by merging a PR is a task, not a goal.

Reach for `references/spec-craft.md` (read on demand, don't inline) when acceptance criteria, priorities, or goal phrasing need hardening — it carries the Given/When/Then discipline, the negative-case rule, the non-goal rationale tags, and the full P0 test.

### 2. Write the spec document

Use the canonical format in `templates/spec.md` (read it from `${CLAUDE_SKILL_DIR}/templates/spec.md`). Every section is required unless marked optional. Key rules:

- **Every workstream** gets: priority (P0/P1/P2), complexity (S/M/L/XL), description, tasks, acceptance criteria. Acceptance criteria use Given/When/Then inside each `- [ ]` item, cover happy + error + edge, and include ≥1 negative — see `references/spec-craft.md`.
- **Technical notes** are optional — include only when there are specific codebase references, patterns, or non-obvious hints. Omit entirely if nothing genuinely helpful to add.
- **Dependencies** section: include only if workstreams actually depend on each other.
- **Risks table**: only genuine risks, not filler like "things might change".
- **Assumptions**: if `{auto_mode}` was used, specific assumptions were necessary, or an Assumption ledger was carried forward from a brainstorm. Tag each (verified fact / assumption / inherited convention); flag the shakiest.
- **Open questions**: only items that genuinely need human decision. Split blocking (must answer before the dependent workstream starts) vs non-blocking.
- **Parking lot**: only if good ideas surfaced that are deliberately out of scope — capture them so they neither get lost nor creep into workstreams. Omit if empty.
- **Execution order**: always include — respects dependencies, orders by priority.

### 3. Quality checks

Before presenting, verify:

- [ ] Every workstream has priority, complexity, description, tasks, AC
- [ ] Acceptance criteria use Given/When/Then, include ≥1 negative, and contain no vague words (fast, intuitive, robust)
- [ ] Goals are outcomes (measurable change), not outputs (artifacts built)
- [ ] P0 set is ruthless — every P0 would genuinely block ship
- [ ] Assumptions are tagged; the shakiest is surfaced as an open question or risk
- [ ] Blocking open questions are marked and linked to the workstream they block
- [ ] Dependencies are explicit and consistent
- [ ] Execution order respects dependencies
- [ ] Non-goals are genuinely out of scope, not things we forgot
- [ ] No workstream is XL+ — if something feels bigger, split it
- [ ] Tasks are concrete enough to implement without guessing

### 4. Save the spec

If `{save_mode}` = true, write the spec to `{output_file}` using the Write tool.

### 5. Present and bridge

**Always:** display the full spec in conversation.

**If `{auto_mode}` = false:**

After showing the spec, ask:

```
Spec ready. Want to revise anything before we proceed?
```

Wait for confirmation or revision requests. Apply revisions, then re-save.

**If `{auto_mode}` = true:** skip the revision prompt and continue to §6.

### 6. Next step

**If `{issues_mode}` = true:** load `./step-03-issues.md`.

**If `{issues_mode}` = false:** show bridge commands and end the workflow:

```
## Next steps

Implement workstreams with apex:

/apex -f {output_file} implement WS-1: {title}
/apex -f {output_file} implement WS-2: {title}
...

Or create issues later:

/spec -i -f {output_file}
```

If `{save_mode}` = false (spec only shown, not saved), suggest saving first:

```
Save this spec for later use:

/spec -s {idea}
```

## Success

- Complete spec document in the canonical format
- 3-7 workstreams with full metadata and testable AC
- Dependencies mapped, execution order defined
- Spec saved if `{save_mode}`
- User approved if not `{auto_mode}`
- Bridge to `/apex` shown

## Common failure modes

- Workstreams without acceptance criteria
- Vague tasks ("implement feature", "add functionality")
- Missing priority or complexity
- Ignoring dependencies between workstreams
- More than 7 workstreams without suggesting a split
- Generic risks that apply to anything ("timeline might slip")
- Starting to implement — that's `/apex`'s job
- Blocking with unnecessary confirmations when `{auto_mode}` is true

## Next step

- `{issues_mode}` = true → `./step-03-issues.md`
- `{issues_mode}` = false → show bridge commands, end workflow

The spec must be detailed enough that `/apex -f {output_file}` (the absolute path, inlined) can execute each workstream without guessing.
