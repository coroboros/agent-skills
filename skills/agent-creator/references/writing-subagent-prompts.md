# Writing subagent prompts

Write a task contract that the delegate can act on and the lead can verify. Explain consequential constraints instead of adding a generic procedure to every role.

## Description and input

The description states what the agent does and when to select it. Keep it specific enough to exclude adjacent tasks. The body defines the accepted result, source inputs, tools and output. Use existing session decisions rather than asking the same permission again.

A delegated brief includes the user's accepted scope and corrections, relevant file paths, pre-existing changes to preserve, and an observable acceptance check. A non-forked agent does not automatically receive the parent's conversation.

## Example: review a bounded change

```markdown
Review the supplied diff for exploitable security regressions.
Read the accepted brief and relevant callers before judging behavior.
Return each supported finding with source location, trigger, impact and
reproduction evidence. Return zero findings when none survives validation.
Do not edit files or contact external systems.
Name any unexamined paths or unavailable checks.
```

This prompt establishes the review boundary without promising that a checklist proves absence of vulnerabilities. Grant only tools needed for the role; prompt instructions complement actual enforcement.

## Output and recovery

Request the artifact the next step needs: changed files and tests for implementation, a decision with evidence for research, or actionable findings for review. Avoid fixed minimum findings, arbitrary task counts and mandatory logs unrelated to the result.

If a prerequisite fails, preserve its exact error and continue independent authorized work. Ask the lead for missing user-owned decisions. After corrections, verify the final artifact and identify any unresolved acceptance criterion.
