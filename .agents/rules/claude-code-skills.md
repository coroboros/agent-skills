# Claude Code Skill Extensions

Claude Code extends the [Agent Skills open standard](./agentskills-spec.md) with host-specific fields. Support depends on both the runtime and the installation path.

Reference: [Claude Code skills](https://code.claude.com/docs/en/skills), checked 2026-09-05. Verify a mirror's source URL before using it; the local `code-skills.md` currently describes Agent SDK skills.

## Claude Code-specific frontmatter

| Field | Purpose |
|-------|---------|
| `when_to_use` | Additional trigger context. Current Claude Code listings truncate combined text at 1,536 characters. Keep `description` self-sufficient for other hosts. |
| `argument-hint` | Autocomplete hint for arguments. Example: `"[-s] <topic>"`. |
| `disable-model-invocation` | `true` = only the user can invoke via `/name`. Use for commit/deploy/PR skills. |
| `user-invocable` | `false` = hide from `/` menu, only Claude auto-invokes. Use for background knowledge skills. |
| `model` | Runtime model override; this repository leaves it unset to inherit the session. |
| `effort` | Runtime effort override, with model-dependent levels; this repository leaves it unset. |
| `context` | `fork` = run in a forked subagent context. |
| `agent` | With `context: fork`, which subagent type to use (`Explore`, `Plan`, `general-purpose`, or a custom agent). |
| `hooks` | Registers session hooks when invoked; consult the current lifecycle and `once` behavior. |
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

Claude.ai uploads, the Skills API, and official packaging accept the specification's six fields and can reject extensions. The Agent SDK documents its own loading behavior, including support for `allowed-tools` on project and personal skills. This differs from the Skills API. See [Agent SDK skills](https://code.claude.com/docs/en/agent-sdk/skills).

**Repository convention:**

- Name actual tool and host requirements in `compatibility`; a subagent or MCP requirement is not inherently exclusive to Claude Code.
- When optional host mechanics are unavailable, state the supported fallback and its limits. A self-review is not an isolated reviewer.
- Do not assume unknown fields are ignored everywhere or that shell substitutions execute on another host. Verify the target loader and adapt argument and script-path handling through its available tools.

See `skill-authoring.md` for conformance and behavioral verification. A valid folder layout alone does not prove runtime compatibility.
