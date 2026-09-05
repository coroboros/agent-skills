---
name: agent-creator
description: Create or update Claude Code subagent definitions in .claude/agents/, including prompts, tools, model inheritance and permissions. Use for agent configuration or Claude Code delegation mechanics, not routine delegation in another host.
when_to_use: When the user wants to create, edit, configure, or orchestrate a Claude Code subagent. Keywords — subagent, agent, delegate, specialist, `/agents`, `.claude/agents/`, agent config, background agent, parallel agents, orchestration, multi-agent workflow. Also trigger when the user asks how subagents work, which tools/models to choose, or how to restrict agent permissions. Skip when the user is working on a non-delegating skill or an API-level tool that has no subagent primitive.
license: MIT
compatibility: "Authors Claude Code agent definitions. Other agents can edit the files; runtime validation requires the target Claude Code version and its actual tools."
metadata:
  author: coroboros
  sources: "code.claude.com/docs/en/sub-agents; github.com/Melvynx/aiblueprint"
---

# Agent Creator

<!-- canonical:writing-rules:start -->
## Important — Writing rules

Apply these rules to emitted prose: docs, comments, commit messages, PR bodies, and release notes.

- Match surrounding punctuation, capitalization, and formatting.
- Every sentence changes the reader's understanding. Cut it otherwise.
- Lead with the action or outcome.
- Use concrete language and lists when they improve comparison or sequence.
- Assert positively. Reserve negation for real constraints (`NEVER commit secrets`).
- No marketing words: powerful, robust, seamlessly, leverage, unlock, comprehensive, delightful.
- No AI tells: delve, tapestry, intricate, pivotal, testament, underscore, crucial, garner, showcase, additionally, moreover, furthermore, indeed.
- For substantive English prose, use `/humanize-en` if installed with the existing scope and authorization. It adds no approval stage; skip redundant passes over short status text.
<!-- canonical:writing-rules:end -->

Subagents are specialized Claude instances that run in isolated contexts with focused roles and limited tool access. This skill covers how to create effective subagents, write strong system prompts, configure tool access, and orchestrate multi-agent workflows.

Delegate bounded independent tasks and verify the returned artifact. Interaction and nesting depend on the host's active tools and execution mode.

## Capture Intent

Resolve the four contract questions from the brief. Ask only for missing decisions that materially affect the result, using an available interaction tool or the lead:

1. **What should this agent do?** — the specific task and role (e.g., "review TypeScript PRs for security regressions"), not a generic description.
2. **When should it be invoked?** — trigger conditions, keywords, file patterns. Goes into the `description` field for routing.
3. **Which tools does it need?** — least-privilege allowlist. Read-only analysis vs write-capable.
4. **What's the expected output format?** — structured report, file edits, list of findings, etc.

The `description` field carries triggers; the system prompt body carries workflow + output format. Both are derived from these answers.

## Quick Start

1. Inspect the installed version and [official subagent documentation](https://code.claude.com/docs/en/sub-agents) for supported fields.
2. Create a Markdown definition directly; the `/agents` creation wizard was removed in v2.1.198.
3. Use project-level (`.claude/agents/`) or user-level (`~/.claude/agents/`) scope matching the request.
4. Define the agent:
   - **name**: lowercase-with-hyphens
   - **description**: When should this agent be used?
   - **tools**: Optional comma-separated list (inherits all if omitted)
   - **model**: Optional; inherit the user's selection unless a supported override was requested.
5. Write the system prompt (the agent's instructions)

**Example:**

```markdown
---
name: code-reviewer
description: Review a supplied code diff for correctness and security defects when a code review is requested.
tools: Read, Grep, Glob
model: inherit
---

You are a senior code reviewer focused on quality, security, and best practices.

## Focus Areas

- Code quality and maintainability
- Security vulnerabilities
- Performance issues
- Best practices adherence

## Output

Provide specific, actionable feedback with file:line references.
```

## Scope and Priority

| Priority | Location | Scope |
|----------|----------|-------|
| 1 (highest) | Managed settings | Organization-wide |
| 2 | `--agents` CLI flag | Current session |
| 3 | `.claude/agents/` | Current project (git-shared) |
| 4 | `~/.claude/agents/` | All your projects |
| 5 (lowest) | Plugin's `agents/` dir | Where plugin is enabled |

When names conflict, higher priority wins. Project agents override user-level agents.

## Configuration

Common YAML frontmatter fields. Only `name` and `description` are required; verify version-sensitive fields against the target CLI.

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique identifier, lowercase letters and hyphens |
| `description` | Yes | When Claude should delegate to this agent. Write clear trigger conditions |
| `tools` | No | Comma-separated allowlist. Inherits all tools if omitted |
| `disallowedTools` | No | Comma-separated denylist, removed from inherited tools |
| `model` | No | `inherit` by default; current aliases include `fable`, `sonnet`, `opus`, `haiku`, or a supported full model ID |
| `permissionMode` | No | `default`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, or `plan` |
| `maxTurns` | No | Maximum agentic turns before auto-stop |
| `skills` | No | Skills to load into agent context at startup (full content injected) |
| `mcpServers` | No | MCP servers: string references or inline definitions |
| `hooks` | No | Lifecycle hooks scoped to this agent |
| `memory` | No | Persistent memory scope: `user`, `project`, or `local` |
| `background` | No | Requests background execution; defaults and availability depend on the current execution mode |
| `effort` | No | Model-dependent override; current values include `low`, `medium`, `high`, `xhigh`, `max` |
| `isolation` | No | `worktree` to run in a temporary git worktree |
| `color` | No | Display color: `red`, `blue`, `green`, `yellow`, `purple`, `orange`, `pink`, `cyan` |
| `initialPrompt` | No | Auto-submitted first user turn when agent runs as main session (via `--agent`) |

**Model resolution order** since v2.1.251: invocation override > frontmatter > `CLAUDE_CODE_SUBAGENT_MODEL` > main model. v2.1.257+ supports `CLAUDE_CODE_SUBAGENT_MODEL_FORCE` for an explicit environment override. Inspect the installed version when diagnosing older behavior.

**Tool restriction patterns**:

- `tools: Read, Grep, Glob` — read-only analysis
- `disallowedTools: Write, Edit` — inherit all except writes
- `tools: Agent(worker, researcher), Read` — restrict delegated agent types where the host exposes nesting
- If both set: `disallowedTools` applied first, then `tools` resolved against remainder

**Plugin agents** do not support `hooks`, `mcpServers`, or `permissionMode` (ignored for security).

## Execution Model

Inspect the actual tool pool. Ordinary Claude Code subagents cannot use AskUserQuestion; fork mode retains the parent's exact tools. Route missing user-owned decisions through the lead when direct interaction is unavailable.

Claude Code supports nested subagents, defaulting to three levels below main since v2.1.219. Installed settings, depth and tools govern availability. Other hosts can differ; do not infer their capabilities from a model name. Intermediate visibility also depends on the host.

## System Prompt Guidelines

Write the system prompt as the markdown body after frontmatter. The agent receives only this prompt (plus environment details), not the full Claude Code system prompt.

- **Be specific**: Define exactly what the agent does. "You are a React performance optimizer specializing in hooks and memoization" not "You are a helpful coding assistant".
- **Define completion**: Accepted outcome, relevant inputs, observable checks and failure reporting.
- **Set constraints**: State scope and permission boundaries plainly; keep implementation detail proportional.
- **Define output format**: Specify expected deliverable structure.
- **Structure is flexible**: Use markdown headings, XML tags, or a combination — whatever is clearest. The official docs show agents with standard markdown headings.

## Background Execution

Use the active Agent tool schema. Current background defaults differ from older releases; fork mode may omit `run_in_background`. Set that field only when exposed and needed. Preserve the returned agent identifier.

**Retrieving results**: The main conversation is automatically notified when background agents complete.

**Parallel pattern**: Launch multiple independent agents in a single message, then collect results:

```
Agent 1: code-reviewer (background)
Agent 2: security-scanner (background)
Agent 3: test-analyzer (background)
-> All run in parallel
-> Results collected when each completes
```

**Resuming**: Use `SendMessage` with the agent's ID to resume with full context preserved.

**When to use background**:

- Long-running analysis (security audits, full-codebase reviews)
- Multiple independent tasks that can parallelize
- Research tasks that take significant time

**When NOT to use**:

- Operations a direct local tool call can complete more simply
- Sequential dependencies between tasks
- Tasks where immediate results are needed for next step

## Management

- **Creation and edits**: Ask Claude to author the definition or edit the file directly; do not rely on the removed `/agents` wizard
- **CLI listing**: `claude agents` to list all configured agents from the command line
- **Manual editing**: Edit files directly in `.claude/agents/` or `~/.claude/agents/`
- **Session-only**: Pass `--agents '{...}'` JSON for temporary agents that aren't saved to disk

## Reference

**Core references:**

- **Agent configuration and usage**: [references/subagents.md](references/subagents.md) — file format, storage locations, tool security, model selection, orchestration strategies, background execution, complete examples
- **Writing effective prompts**: [references/writing-subagent-prompts.md](references/writing-subagent-prompts.md) — specificity, clarity, constraints, description field optimization, anti-patterns, examples

**Advanced topics:**

- [references/orchestration-patterns.md](references/orchestration-patterns.md) — sequential, parallel, hierarchical, coordinator patterns
- [references/evaluation-and-testing.md](references/evaluation-and-testing.md) — evaluation metrics, testing strategies
- [references/error-handling-and-recovery.md](references/error-handling-and-recovery.md) — failure modes, recovery strategies
- [references/context-management.md](references/context-management.md) — memory architecture, context strategies
- [references/debugging-agents.md](references/debugging-agents.md) — logging, tracing, diagnostic procedures

## Gotchas

1. **`tools` + `disallowedTools` resolution is counterintuitive when both are set.** Per § Configuration, `disallowedTools` applies first, then `tools` resolves against the remainder. Setting `tools: Read, Write` + `disallowedTools: Write` yields an agent with only `Read`; Write is denied before the allowlist sees it. Fix: use one mechanism, not both; prefer the allowlist for fine-grained control.
2. **Plugin fields may be ignored.** Use project/user scope or applicable external enforcement when hooks, MCP configuration or permission mode are required. Prompt text cannot replace a deterministic hook.
3. **Nesting is bounded.** Schedule within actual depth and concurrency limits; flatten ownership when the host cannot nest.
4. **Model precedence is version-sensitive.** Inspect the selected model, invocation, definition and applicable environment overrides; inherit by default instead of imposing a generic tier matrix.

## Success Criteria

A well-configured agent has:

- Valid YAML frontmatter (name matches file, description includes triggers)
- Clear role definition in system prompt
- Appropriate tool restrictions (least privilege)
- Structured prompt with workflow and constraints
- Description field optimized for automatic routing
- Model selection appropriate for task complexity
- Successfully tested on representative tasks

## See also

- **`/claude-md`** — author and optimize `CLAUDE.md` / `.claude/rules/*.md`. Project-wide instructions pair naturally with `.claude/agents/*.md` definitions; use this skill for the agent specs and `/claude-md` for the surrounding project memory.
