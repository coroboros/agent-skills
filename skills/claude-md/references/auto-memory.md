# Auto Memory

Claude Code v2.1.59+ adds a parallel memory system: **auto memory**. Claude saves notes for itself (build commands, debugging insights, preferences) as it works. You don't write anything — Claude decides what's worth remembering.

## Layout and loading

- **Location**: `~/.claude/projects/<project>/memory/MEMORY.md` — machine-local, per git repo, shared across worktrees of the same repo.
- **Loaded per session**: first 200 lines (or 25 KB) of `MEMORY.md`. Topic files (`debugging.md`, `patterns.md`, …) load on-demand when Claude reads them.
- **Toggle**: `/memory` exposes an auto-memory toggle. Setting-level: `autoMemoryEnabled` (default `true`). Env override: `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`.
- **Custom location**: `autoMemoryDirectory` in user or local settings (rejected from project settings for safety).

## How it pairs with CLAUDE.md

Auto memory and CLAUDE.md complement each other:

- **CLAUDE.md** is for "always do X" rules you author.
- **Auto memory** is for "Claude noticed Y" notes Claude writes.

Run `/memory` to see both in one place.

## Subagent memory

Subagents can maintain their own memory too — configure via `memory: user|project|local` in the subagent frontmatter. Stored at `~/.claude/agent-memory/<name>/`. See Claude Code subagent docs (`/en/sub-agents#enable-persistent-memory`) for details.

## Drift note

Version pins, file caps, and setting keys here drift across Claude Code releases. When in doubt, verify against `code.claude.com/docs/en/memory` — listed in the SKILL.md `metadata.sources`.
