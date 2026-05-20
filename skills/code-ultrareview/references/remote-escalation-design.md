# Remote-escalation design (phase 2)

`--remote` is reserved for an MVP-next iteration. In-session Ultra tier
covers the current scope: build verification, property-fuzz harness,
spec-conformance fetch, `--apply-safe` writers — all running on the
user's Claude Code subscription. Phase 2 escalates to a remote sandbox
when in-session Ultra runs prove cost-inadequate vs Anthropic's
Code Sandbox + multi-agent fleet.

## Why phase 2 exists

In-session subagents share the orchestrator's working tree and shell
context — fast for read-only review, fine for `--apply-safe`'s additive
writers, but limited for:

- Long-running test suites (Ultra's build step is bounded at 120s).
- Untrusted code execution (`/security-review` overlap when malicious diffs land).
- Multi-agent fan-out beyond what one Claude Code session can hold without context pressure.
- Property-fuzz runs that need bigger budgets than in-session timeouts allow.

Anthropic's `/ultrareview` already covers this surface — billed,
remote, 3-per-month rate-limited. `--remote` is the bridge: same skill,
same flags, but the lens fan-out and Ultra execution run in Anthropic's
Code Sandbox via the planned MCP integration.

## Planned architecture

```
user → /code-ultrareview --remote
       ↓
       remote_stub.py prints redirect (current MVP)
       ↓
       (phase 2) → MCP client to Anthropic Code Sandbox
                  ↓
                  Sandbox starts a fresh ephemeral repo clone
                  ↓
                  Standard + Deep + Ultra lenses fan out in parallel
                  ↓
                  Results stream back as JSON; aggregation runs locally
                  ↓
                  Report emitted to ~/.claude/output/{project}/code-ultrareview/
```

## Open design questions

- **Auth.** OAuth + `claude.ai` token vs the `wrangler`-style local CLI
  flow. The user's existing Claude Code subscription should cover
  remote runs; no separate billing.
- **JSON wire schema.** Match the in-session finding shape exactly so
  `aggregation.py` consumes both verbatim. The schema is already in
  `references/aggregation.md`.
- **Timeout management.** Sandbox runs may take 10+ minutes. The
  orchestrator needs a streaming progress channel (vs a single
  block-until-done call).
- **Billing surface.** Phase-2 runs likely count against the user's
  `/ultrareview` quota. Surface this in the audit-phase output:
  "tier=ultra remote — will count against /ultrareview quota".
- **Cache reuse.** The 7-day spec-conformance cache (`~/.claude/cache/code-ultrareview/specs/`)
  should be sharable between local and remote runs — sync via tarball
  push or volume mount.

## Triggering criteria for phase 2

Phase 2 prioritizes when the eval set (post-launch) shows:

- Ultra in-session lags Anthropic remote by >20% on finding-rate or accuracy.
- Users report Ultra's 120s build timeout consistently insufficient.
- Multi-agent fan-out hits the in-session context ceiling.

Until then, in-session Ultra is the default and `--remote` redirects.

## Reference

- Anthropic upstream `/ultrareview` docs: `docs.claude.com/en/docs/claude-code/commands` (covers built-in remote review semantics)
- Managed Code Review by Anthropic (sibling reference for the remote-sandbox posture).
- `references/ultra-execution.md` (the in-session Ultra design phase 2 supersedes for remote runs).

## Current behavior

Pass `--remote` and the orchestrator invokes
`scripts/remote_stub.py`, which prints the redirect and exits 0. No
network call, no billing implication, no error — users get the
phase-2 plan inline.
