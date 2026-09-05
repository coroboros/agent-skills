# Claude Code subagents

Use this reference when authoring a Claude Code agent definition. Check the installed CLI version and the current [official subagent documentation](https://code.claude.com/docs/en/sub-agents) before relying on version-sensitive fields.

## Definition and scope

Create a Markdown file in `.claude/agents/` for a shared project agent, or `~/.claude/agents/` for a personal agent. The frontmatter requires `name` and `description`; the body is its system prompt. Use the established scope when updating an existing agent. Do not move personal instructions into a shared repository without authorization.

`/agents` no longer provides the creation wizard in Claude Code v2.1.198+. Author the file directly or ask Claude to create it. `claude agents` lists definitions. Project definitions override user definitions of the same name; verify managed and session overrides when diagnosing selection.

## Model and effort

Omit `model` or use `inherit` unless the user requests another supported model. Current aliases include `fable`, `opus`, `sonnet` and `haiku`; aliases and effort support depend on the installed release and selected model. Current effort vocabulary includes `low`, `medium`, `high`, `xhigh`, `max`; verify the selected model accepts the value.

Since v2.1.251, model selection follows invocation override, frontmatter, `CLAUDE_CODE_SUBAGENT_MODEL`, then main model. v2.1.257+ adds `CLAUDE_CODE_SUBAGENT_MODEL_FORCE` for an explicit environment override. Do not assume an ambient variable always wins.

## Tools and enforcement

Omit `tools` to inherit, or name the actual required tools. `tools: Read, Grep, Glob` suits file inspection; adding Bash grants shell capabilities, so it is not a read-only security boundary by itself. Denylists and allowlists do not override the host sandbox or approval policy.

Plugin agents ignore `hooks`, `mcpServers` and `permissionMode`. When these are required, use a supported project/user definition or external enforcement. Prompt text can explain a policy but cannot replace a hook.

## Execution capabilities

Current Claude Code can nest subagents, with a default depth of three below main since v2.1.219. The actual depth limit and allowed tool pool govern availability. Ordinary subagents cannot use AskUserQuestion; fork mode retains the parent's exact tools. Route missing user input back to the lead when direct interaction is unavailable.

Inspect the active Agent schema before passing background/fork options. Current background defaults and fork mode differ from older foreground behavior, and fork mode may omit `run_in_background`. Preserve the agent ID and use the available continuation mechanism instead of restarting unnecessarily.

## Acceptance check

Test a relevant task and a near-miss routing request. Confirm the definition loads, intended tools are available, the selected model is inherited or explicitly authorized, required enforcement exists, and the output satisfies the brief. A valid YAML file alone does not verify behavior.
