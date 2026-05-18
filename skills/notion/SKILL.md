---
name: notion
description: Notion access from Claude Code via the official MCP connector (default path, ~95% of intents) or the `ntn` CLI (only for file uploads, Notion Workers, headless/CI scripts, raw API discovery, shell piping). Routes intent to the right transport, pre-flights the Notion-flavored Markdown spec and target data-source schema, and pins the empirical gotchas not surfaced by tool descriptions or `ntn --help`. Use whenever the user wants to read, fetch, search, create, update, query, or organize Notion content — pages, databases, data sources, views, comments, blocks, properties, schemas, wikis, docs — or upload a file to Notion, build a Notion Worker, or script Notion non-interactively. Triggers on Notion, Notion page, Notion database, Notion DB, Notion wiki, Notion doc, Notion comment, Notion view, Notion property, Notion schema, Notion file, Notion Worker, NOTION_API_TOKEN, ntn, ntn api.
when_to_use: When the user wants to read, write, query, search, or organize Notion content (pages, databases, data sources, views, comments, blocks, properties, schemas, wikis, files), build a Notion Worker, or script Notion non-interactively. Skip when the user is in the claude.ai web app (different surface, native handling), has explicitly disabled the Notion MCP connector AND has not installed the `ntn` CLI, or when the request targets a different knowledge tool (Linear, Confluence, Coda, Obsidian).
model: opus
license: MIT
compatibility: "Claude Code CLI (per Agent Skills spec). Graceful degradation in other environments supporting the open standard."
metadata:
  author: coroboros
  sources:
    - developers.notion.com/guides/mcp/overview
    - developers.notion.com/cli/reference/commands
    - developers.notion.com/page/changelog
    - developers.notion.com/reference
---

# Notion

Default path is the official Notion MCP connector — covers ~95% of intents (pages, databases, views, comments, search, blocks, users, teams). The `ntn` CLI is optional and used only for the five cases listed under [Routing](#routing--mcp-vs-cli) below. The skill routes the user's intent to the right transport, runs the [Pre-flight](#pre-flight-do-once-per-session-before-any-content-write) before the first content write, and applies the [Gotchas](#gotchas-empirical--not-in-tool-descriptions-or-ntn---help) — empirical facts not surfaced by tool descriptions or `--help`.

## Pre-flight (do once per session before any content write)

1. Read the MCP resource `notion://docs/enhanced-markdown-spec` — the canonical reference for Notion-flavored Markdown used by `notion-create-pages` `content` and `notion-update-page` `update_content` / `replace_content`. Don't guess Markdown syntax — Notion's flavor diverges from CommonMark in non-obvious ways.
2. For database row CRUD — `notion-fetch` the target data source first. The fetch returns the current SQLite-style schema. Property names are case-sensitive; expanded keys apply (`date:<col>:start | :end | :is_datetime`, `place:<col>:name | address | latitude | longitude | google_place_id`, checkbox `__YES__` / `__NO__`, properties literally named `id` or `url` → prefix `userDefined:`).

## Routing — MCP vs CLI

### Default — MCP

For ~95% of Notion intents. The MCP wraps the API in DSLs that have no CLI equivalent:

- SQL DDL for schemas — `notion-create-database` / `notion-update-data-source`
- View DSL — `notion-create-view` / `notion-update-view`
- Block-level comments — `selection_with_ellipsis` against rendered Markdown
- Batch up to 100 rows in one `notion-create-pages` call
- Semantic search across connected sources (Slack, GDrive, GitHub, Jira, MS Teams, Sharepoint, OneDrive, Linear)

### Use the `ntn` CLI when (and only when):

- **File upload to Notion** — `ntn files create`. The MCP has no upload tool.
- **Notion Workers / serverless** — `ntn workers …`. The MCP has no Workers tools.
- **Headless / CI / non-interactive** — `NOTION_API_TOKEN=…` plus `--json` and `--yes`. The MCP requires an interactive Claude session.
- **Raw API discovery** — `ntn api ls` enumerates every endpoint. Useful when an action isn't covered by any high-level MCP tool.
- **Shell piping** — `ntn pages get <id> --json | jq …` for ad-hoc data wrangling.

If none of the five apply: stay on the MCP.

### When the CLI path is required but `ntn` is missing

Print the install + auth URLs from [References](#references) and stop. Never auto-install on the user's behalf — auth setup needs an interactive token decision.

## References

Defer to these — do not embed their content in the skill body. Each is the single source of truth and stays current without any skill update.

| What | Where |
|---|---|
| MCP overview + setup (start here for newcomers) | https://developers.notion.com/guides/mcp/overview |
| MCP capability evolution (monthly cadence) | https://developers.notion.com/page/changelog |
| MCP tool DSL syntax (per tool) | The tool's own description in the active session — read it before first use |
| Notion-flavored Markdown spec | MCP resource `notion://docs/enhanced-markdown-spec` |
| `ntn` CLI installation | https://developers.notion.com/cli/get-started/installation |
| `ntn` CLI authentication (OAuth + `NOTION_API_TOKEN`) | https://developers.notion.com/cli/get-started/authentication |
| `ntn` CLI command reference | https://developers.notion.com/cli/reference/commands · `ntn <command> --help` |
| Notion REST API reference | https://developers.notion.com/reference |

## Gotchas (empirical — not in tool descriptions or `ntn --help`)

These five facts are stable, repeatedly observed in production sessions, and not surfaced by any tool description or CLI help text. They earn their place in the skill body — everything else defers.

1. **`selection_with_ellipsis` matches rendered Markdown verbatim.** Copy the snippet from a fresh `notion-fetch`. Never paraphrase — Notion's validator rejects on first-character mismatch and the failure mode is silent.
2. **New databases land at the bottom of the parent page's children.** To reposition: a two-op `notion-update-page update_content` call — prepend `<database url="…" data-source-url="…">` at the anchor block, then remove the original. Keep at least one reference present in the page so the child-deletion validator doesn't trip, or pass `allow_deleting_content: true` explicitly.
3. **`notion-create-pages` batches up to 100 rows in a single call.** Prefer the batch over a per-row loop — Notion rate-limits aggressively on chatty calls.
4. **The MCP shipped 2026-01-15 and gains tools roughly monthly** (views 2026-03-11, block-level comments 2026-02-26). Don't trust training-data recall for the current tool set — read the changelog when something looks missing.
5. **Writes fail with `archived ancestor` if any parent (page / database / data source) is in the trash.** `notion-fetch` against the data source still returns the schema, masking this during pre-flight — the failure only surfaces at write time. Before trusting pre-flight to greenlight writes on an unfamiliar target, `notion-fetch <page_id>` and check for the `deleted` attribute on the returned `<page>` tag.

## Maintenance

This skill encodes only routing rules, the pre-flight, and the five stable gotchas above. Per-tool syntax → tool descriptions; CLI commands → `ntn --help`; Markdown rules → the `notion://docs/enhanced-markdown-spec` resource; capability evolution → https://developers.notion.com/page/changelog; auth → the CLI docs URL. A new MCP tool or `ntn` subcommand requires no skill update — discovery happens via the tool or CLI itself.

## Privacy

Never echo a Notion API token (prefix `ntn_…` for `ntn` OAuth or `secret_…` for integration tokens) in tool output, logs, commits, or PR bodies. The token belongs in `.envrc` (gitignored, `chmod 600`) or `~/.config/ntn/`, never in tracked files.
