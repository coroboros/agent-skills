# claude-md revise

Capture session learnings into CLAUDE.md. Triggered when `$ARGUMENTS` contains "revise".

## Step 1: Reflect on the session

Review the conversation for knowledge that would help future sessions:

- Commands discovered or used
- Code patterns followed
- Testing approaches that worked
- Environment or configuration quirks
- Gotchas and warnings encountered
- Repeated corrections the user made

## Step 2: Find target files

Locate all `CLAUDE.md` and `CLAUDE.local.md` files. Decide where each addition belongs:

- `CLAUDE.md` — Team-shared (checked into git)
- `CLAUDE.local.md` — Personal/local only (gitignored)
- `.claude/rules/` — If the learning is path-scoped

## Step 3: Draft additions

Keep concise — one line per concept. Format: `` `<command or pattern>` — `<brief description>` ``

Skip:

- Obvious information the agent discovers itself
- One-off fixes unlikely to recur
- Verbose explanations (one-liner suffices)

## Step 4: Present diffs

For each proposed addition, show:

````
### Update: ./CLAUDE.md
**Why:** [one-line reason]
```diff
+ [the addition]
```
````

## Step 5: Apply with approval

Ask the user what to apply. Only edit files they approve.
