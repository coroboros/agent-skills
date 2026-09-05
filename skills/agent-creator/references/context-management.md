# Subagent context management

Use this reference for long delegated tasks. Claude Code maintains a subagent's conversation across tool calls and resumptions; a tool call does not reset context. See [subagent documentation](https://code.claude.com/docs/en/sub-agents) for current compaction and fork behavior.

## Brief the actual work

Give a non-forked agent the accepted task, relevant source paths, user corrections, authorization boundaries and an observable acceptance check. It does not automatically inherit the original request. A fork can carry the parent's history; use it only when the host exposes that capability and the history is useful.

Read source files relevant to the pending change. Locate symbols first and expand context when uncertainty requires it. Do not load a full repository map merely because the task has many tool calls.

## Preserve continuity

Let the harness manage compaction. If notes are available and authorized, retain the accepted outcome, decisions, verified artifacts, current errors and remaining work. Point to durable source evidence instead of copying all tool output. Respect the user's memory permissions; task-local state is not authorization to write persistent personal memory.

After compaction, recover the current state before repeating work. Resume an existing agent when continuity matters. Use a fresh independent reviewer when independence matters; those are different purposes.

## Verify the handoff

A handoff names files changed, evidence obtained, outstanding blockers and the next concrete check. The lead verifies the artifact rather than trusting a completion claim. Never drop acceptance criteria to fit a summary.

There is no universal 75% context threshold, fifteen-turn reset or five-tool-call limit. Use actual host signals and progress. When building API integrations, preserve conversation history according to the provider contract; Fable 5.1 guidance specifies append-only history.
