# Claude Code Skill Extensions

Claude Code extends the [Agent Skills open standard](./agentskills-spec.md) with harness-specific frontmatter fields. These are **Claude Code only** — skills relying on them are not portable to Claude.ai or the Claude API without degradation.

Reference: `coroboros/archivist/docs/code/code-skills.md`.

## Claude Code-specific frontmatter

| Field | Purpose |
|-------|---------|
| `when_to_use` | Additional trigger context. Appended to `description` in the skill listing. Counts toward the 1,536-char cap. |
| `argument-hint` | Autocomplete hint for arguments. Example: `"[-s] <topic>"`. |
| `disable-model-invocation` | `true` = only the user can invoke via `/name`. Use for commit/deploy/PR skills. |
| `user-invocable` | `false` = hide from `/` menu, only Claude auto-invokes. Use for background knowledge skills. |
| `model` | Force a specific model (`haiku`, `sonnet`, `opus`) for the skill session. |
| `effort` | `low`, `medium`, `high`, `xhigh`, `max`. Overrides session effort. |
| `context` | `fork` = run in a forked subagent context. |
| `agent` | With `context: fork`, which subagent type to use (`Explore`, `Plan`, `general-purpose`, or a custom agent). |
| `hooks` | PreToolUse/PostToolUse hooks scoped to the skill's lifecycle. |
| `paths` | Glob patterns — skill auto-loads only when working with matching files. |
| `shell` | `bash` (default) or `powershell` for inline `` !`cmd` `` execution. |

## String substitutions

- `$ARGUMENTS` — full arg string
- `$ARGUMENTS[N]` or `$N` — positional arg (0-indexed)
- `${CLAUDE_SESSION_ID}` — current session ID
- `${CLAUDE_SKILL_DIR}` — the skill's directory (use for referencing bundled scripts)

## Inline shell execution

`` !`command` `` runs the command before the skill is sent to Claude. Output replaces the placeholder. For multi-line, use a fenced block opened with ` ```! `.

## Portability note

Claude Code-only extensions (`argument-hint`, `when_to_use`, `$ARGUMENTS`, `paths`, `hooks`, `` !`cmd` ``, `shell`, `context`, `agent`, `model`, `effort`, `disable-model-invocation`, `user-invocable`) do not travel to Claude.ai, Claude desktop, or the SDK. `allowed-tools` is also Claude Code CLI-only per the SDK skills doc. Per the official spec, skills are portable by default (`name` + `description` only); any extension narrows scope.

**Repo scope convention** for the root README skills table:

- **`All agents`** — uses only open-standard fields (`name`, `description`, `license`, `compatibility`, `metadata`). Portable across any agent honoring the Agent Skills spec.
- **`Claude`** — uses Claude Code-specific extensions. Optimized for Claude Code CLI per Anthropic's docs; degrades gracefully in Claude.ai, Claude desktop, and other agents supporting the open standard.

Every SKILL.md declares its intended environment via the top-level spec-canonical `compatibility:` field. See `skill-authoring.md` → *Post-generation conformance → Frontmatter* for the exact text to use.
