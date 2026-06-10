# Claude Code Skill Extensions

Claude Code extends the [Agent Skills open standard](./agentskills-spec.md) with harness-specific frontmatter fields. These are **Claude Code only** — skills relying on them are not portable to Claude.ai or the Claude API without degradation.

Reference: `coroboros/archivist/docs/code/code-skills.md`.

## Claude Code-specific frontmatter

| Field | Purpose |
|-------|---------|
| `when_to_use` | Additional trigger context, appended to `description` in the per-turn skill listing. The combined `description` + `when_to_use` text is capped by the `maxSkillDescriptionChars` setting (default 1536; requires Claude Code v2.1.105+ — see `code-settings.md`). Keep `description` self-sufficient for triggering: `when_to_use` does not travel to other agents. |
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

**Repo scope convention** — two tiers, declared in frontmatter (not in the README table):

- **Portable** — no Claude-only runtime mechanics in the body (subagents, MCP tools, interactive UI). Claude-only *frontmatter* extensions may remain: spec-lenient clients ignore unknown fields, so they are inert elsewhere.
- **Harness-coupled** — the body leans on Claude Code mechanics, each with a graceful-degradation clause.

Harness-coupled skills declare their intended environment via the top-level spec-canonical `compatibility:` field; portable skills omit it. See `skill-authoring.md` → *Post-generation conformance → Frontmatter* for the canonical text and the tier rule.
