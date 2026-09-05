# Evaluating subagents

Evaluate the task's observable outcome, tool boundaries and failure behavior. Valid frontmatter establishes loadability; it does not establish task quality.

## Representative cases

Start with a normal accepted task, a meaningful edge case and a near miss that should not route to the agent. For a SQL generator, use a supplied schema and read-only fixtures: verify selected columns, joins, parameter handling and results. Compare equivalent query behavior rather than requiring identical SQL text.

Include a missing prerequisite and an explicit scope boundary where relevant. Seed a plausible false finding and a real defect when evaluating reviewers. The reviewer should challenge both author and tool claims using source evidence.

## Comparison

For an existing agent, keep an immutable baseline and compare the candidate under the same model, effort, tools, input and acceptance criteria. Use fresh runs when evaluating independence. Blind artifact review to agent identity and author rationale where practical.

Record successful outcomes, defects, unnecessary interruptions and unauthorized actions. Record time, tokens and cost only when actually measured by the host. Missing metrics remain missing; confidence is not a measured probability.

## Interpretation

Separate deterministic assertions from qualitative judgment. A security checklist cannot prove there are no vulnerabilities; report the examined source/sink paths and limits. One successful case does not establish reliability across models.

When evaluating a skill that authors agents, use the official skill-creator's existing evaluation tools. Keep the pilot bounded to the decisions it needs to resolve.
