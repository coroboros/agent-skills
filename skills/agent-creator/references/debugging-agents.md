# Debugging Claude Code agents

Start from the actual failing task and installed host. Use [official subagent documentation](https://code.claude.com/docs/en/sub-agents) for moving runtime details.

## Isolate the failure

Check whether the definition loads, the intended agent is selected, required tools are present, and the failure reproduces with the same input. Inspect scope precedence, malformed frontmatter, permissions and the selected model before changing the prompt. Preserve stderr and terminal status; accepted or queued work is not completion.

Reduce the failing input while retaining the behavior being investigated. Compare the final artifact with acceptance criteria rather than scoring the agent's explanation. For routing problems, include a near-miss request that should select another workflow.

## Observe only what is useful

Use host-provided task status, tool traces and error output. Avoid secrets in logs. Add temporary task-local diagnostics when they distinguish competing causes, then remove them when verified. Do not install dashboards, collectors or a retention system for a local debugging question.

A tool returning the same verdict on heterogeneous inputs needs its own negative control. Confirm the checker detects a known failure before trusting its clean result.

## Close the issue

Report the trigger, root cause supported by evidence, correction, verification and remaining limits. Preserve prior user changes. A successful prompt example is evidence for that case, not proof of general reliability.
