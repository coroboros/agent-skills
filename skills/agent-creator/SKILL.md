---
name: agent-creator
description: Create, configure, and orchestrate Claude Code subagents — specialized Claude instances with focused roles and limited tool access. Covers YAML frontmatter (name, description, tools, model, permissions, hooks, MCP servers), system prompt design, tool restriction patterns, background execution, and multi-agent orchestration. Use whenever the user mentions subagents, delegation, specialists, agent configs, `.claude/agents/`, the `/agents` command, or wants to parallelize work — even when they just say "background agent" or "delegate this".
when_to_use: When the user wants to create, edit, configure, or orchestrate a Claude Code subagent. Keywords — subagent, agent, delegate, specialist, `/agents`, `.claude/agents/`, agent config, background agent, parallel agents, orchestration, multi-agent workflow. Also trigger when the user asks how subagents work, which tools/models to choose, or how to restrict agent permissions. Skip when the user is working on a non-delegating skill or an API-level tool that has no subagent primitive.
model: opus
license: MIT
compatibility: "Claude Code CLI (per Agent Skills spec). Graceful degradation in other environments supporting the open standard."
metadata:
  author: coroboros
---

# Agent Creator

Subagents are specialized Claude instances that run in isolated contexts with focused roles and limited tool access. This skill covers how to create effective subagents, write strong system prompts, configure tool access, and orchestrate multi-agent workflows.

Subagents enable delegation of complex tasks to specialized agents that operate autonomously without user interaction, returning their final output to the main conversation.

## Quick Start

1. Run `/agents` command
2. Select "Create New Agent"
3. Choose project-level (`.claude/agents/`) or user-level (`~/.claude/agents/`)
4. Define the agent:
   - **name**: lowercase-with-hyphens
   - **description**: When should this agent be used?
   - **tools**: Optional comma-separated list (inherits all if omitted)
   - **model**: Optional (`sonnet`, `opus`, `haiku`, full model ID, or `inherit`)
5. Write the system prompt (the agent's instructions)

**Example:**

```markdown
---
name: code-reviewer
description: Expert code reviewer. Use proactively after code changes to review for quality, security, and best practices.
tools: Read, Grep, Glob, Bash
model: sonnet
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

All supported YAML frontmatter fields. Only `name` and `description` are required.

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique identifier, lowercase letters and hyphens |
| `description` | Yes | When Claude should delegate to this agent. Write clear trigger conditions |
| `tools` | No | Comma-separated allowlist. Inherits all tools if omitted |
| `disallowedTools` | No | Comma-separated denylist, removed from inherited tools |
| `model` | No | `sonnet`, `opus`, `haiku`, full model ID (e.g. `claude-opus-4-6`), or `inherit`. Defaults to `inherit` |
| `permissionMode` | No | `default`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, or `plan` |
| `maxTurns` | No | Maximum agentic turns before auto-stop |
| `skills` | No | Skills to load into agent context at startup (full content injected) |
| `mcpServers` | No | MCP servers: string references or inline definitions |
| `hooks` | No | Lifecycle hooks scoped to this agent |
| `memory` | No | Persistent memory scope: `user`, `project`, or `local` |
| `background` | No | `true` to always run as background task. Default: `false` |
| `effort` | No | Effort level override: `low`, `medium`, `high`, `max` |
| `isolation` | No | `worktree` to run in a temporary git worktree |
| `color` | No | Display color: `red`, `blue`, `green`, `yellow`, `purple`, `orange`, `pink`, `cyan` |
| `initialPrompt` | No | Auto-submitted first user turn when agent runs as main session (via `--agent`) |

**Model resolution order**: `CLAUDE_CODE_SUBAGENT_MODEL` env var > per-invocation model > frontmatter model > main conversation model.

**Tool restriction patterns**:

- `tools: Read, Grep, Glob` — read-only analysis
- `disallowedTools: Write, Edit` — inherit all except writes
- `tools: Agent(worker, researcher), Read` — restrict which subagents can be spawned (main thread only)
- If both set: `disallowedTools` applied first, then `tools` resolved against remainder

**Plugin agents** do not support `hooks`, `mcpServers`, or `permissionMode` (ignored for security).

## Execution Model

**Subagents are black boxes that cannot interact with users.**

- Can use tools: Read, Write, Edit, Bash, Grep, Glob, MCP tools
- **Cannot** use AskUserQuestion or any interactive tool
- User never sees intermediate steps — only the final output

**Workflow pattern:**

```
Main chat: Gather requirements (AskUserQuestion)
  -> Agent: Research/build autonomously (no user interaction)
  -> Main chat: Present results, confirm approach
  -> Agent: Generate code based on confirmed plan
  -> Main chat: Present results, handle deployment
```

**Subagents cannot spawn other subagents.** Don't include `Agent` in a subagent's tools. This restriction only applies to subagents — main thread agents (via `--agent`) can spawn subagents.

## System Prompt Guidelines

Write the system prompt as the markdown body after frontmatter. The agent receives only this prompt (plus environment details), not the full Claude Code system prompt.

- **Be specific**: Define exactly what the agent does. "You are a React performance optimizer specializing in hooks and memoization" not "You are a helpful coding assistant".
- **Include a workflow**: Step-by-step process for consistency.
- **Set constraints**: Use NEVER/MUST/ALWAYS for critical boundaries.
- **Define output format**: Specify expected deliverable structure.
- **Structure is flexible**: Use markdown headings, XML tags, or a combination — whatever is clearest. The official docs show agents with standard markdown headings.

## Background Execution

Agents can run in the background using the `run_in_background` parameter on the Agent tool, enabling parallel execution while the main conversation continues.

**Launching**: Set `run_in_background: true` on the Agent tool call. Returns an `agent_id`.

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

- Long-running analysis (security audits, comprehensive reviews)
- Multiple independent tasks that can parallelize
- Research tasks that take significant time

**When NOT to use**:

- Quick operations (< 10 seconds)
- Sequential dependencies between tasks
- Tasks where immediate results are needed for next step

## Management

- **Recommended**: `/agents` command for interactive management (view, create, edit, delete)
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
