---
name: notion
description: Read, search, update or organize Notion pages and databases using available Notion MCP tools. Use ntn for requested scripts or capabilities missing from the connector; verify target schema and authorization before writes.
when_to_use: When the user wants to read, write, query, search, or organize Notion content (pages, databases, data sources, views, comments, blocks, properties, schemas, wikis, files), build a Notion Worker, or script Notion non-interactively. Skip when the user is in the claude.ai web app (different surface, native handling), has explicitly disabled the Notion MCP connector AND has not installed the `ntn` CLI, when the input is a local Notion export (ZIP/HTML/MD) — use /markitdown — or when the request targets a different knowledge tool (Linear, Confluence, Coda, Obsidian).
license: MIT
compatibility: "Requires available Notion MCP tools or an installed, authenticated ntn CLI. Tool schemas and connector capabilities vary by host; no Claude-specific runtime is required."
metadata:
  author: coroboros
  sources: "developers.notion.com/guides/mcp/overview; developers.notion.com/cli/reference/commands; developers.notion.com/page/changelog; developers.notion.com/reference"
---

# Notion

Prefer the official Notion MCP connector when it exposes the requested operation. Notion supports Codex and other clients as well as Claude Code; route by actual tools, not client identity. Use the optional `ntn` CLI for supported capabilities missing from the connector or a requested script. Run the [Pre-flight](#pre-flight-do-once-per-session-before-any-content-write), preserve the user's write scope and verify resulting content.

## Pre-flight (do once per session before any content write)

MCP path only — on the `ntn` CLI branch, skip this and validate shapes against the REST API responses instead.

1. Read the MCP resource `notion://docs/enhanced-markdown-spec` — the canonical reference for Notion-flavored Markdown used by `notion-create-pages` `content` and `notion-update-page` `update_content` / `replace_content`. Don't guess Markdown syntax — Notion's flavor diverges from CommonMark in non-obvious ways.
2. For database row CRUD — `notion-fetch` the target data source first. The fetch returns the current SQLite-style schema. Property names are case-sensitive; expanded keys apply (`date:<col>:start | :end | :is_datetime`, `place:<col>:name | address | latitude | longitude | google_place_id`, checkbox `__YES__` / `__NO__`, properties literally named `id` or `url` → prefix `userDefined:`).

## Routing — MCP vs CLI

### Default — MCP

Inspect the active tool descriptions. Depending on the connector, supported operations can include:

- SQL DDL for schemas — `notion-create-database` / `notion-update-data-source`
- View DSL — `notion-create-view` / `notion-update-view`
- Block-level comments — `selection_with_ellipsis` against rendered Markdown
- Batch up to 100 rows in one `notion-create-pages` call
- Semantic search across connected sources (Slack, GDrive, GitHub, Jira, MS Teams, Sharepoint, OneDrive, Linear)

### Use the `ntn` CLI when its capabilities fit:

- **File upload to Notion** — `ntn files create` when the active MCP lacks upload support.
- **Notion Workers / serverless** — `ntn workers …` when needed tools are absent from the MCP.
- **Headless / CI / non-interactive** — use the supported CLI authentication and output flags for the requested script. A CI job need not have a Claude session; absence of Claude does not imply absence of MCP elsewhere.
- **Raw API discovery** — `ntn api ls` enumerates every endpoint. Useful when an action isn't covered by any high-level MCP tool.
- **Shell piping** — `ntn pages get <id> --json | jq …` for ad-hoc data wrangling.

If the available MCP supports the requested operation and no CLI script is requested, stay on the MCP. If its tools are unavailable, use an installed, authenticated CLI or report the concrete missing capability. Authentication or connection setup needs the user's applicable authorization.

### When the CLI path is required but `ntn` is missing

Print the install + auth URLs from [References](#references) and stop. Never auto-install on the user's behalf — auth setup needs an interactive token decision.

## References

Defer to these — do not embed their content in the skill body. Each is the single source of truth and stays current without any skill update.

| What | Where |
|---|---|
| MCP overview + setup (start here for newcomers) | https://developers.notion.com/guides/mcp/overview |
| MCP capability evolution | https://developers.notion.com/page/changelog |
| MCP tool DSL syntax (per tool) | The tool's own description in the active session — read it before first use |
| Notion-flavored Markdown spec | MCP resource `notion://docs/enhanced-markdown-spec` |
| `ntn` CLI installation | https://developers.notion.com/cli/get-started/installation |
| `ntn` CLI authentication (OAuth + `NOTION_API_TOKEN`) | https://developers.notion.com/cli/get-started/authentication |
| `ntn` CLI command reference | https://developers.notion.com/cli/reference/commands · `ntn <command> --help` |
| Notion REST API reference | https://developers.notion.com/reference |

## Gotchas

These operational checks supplement the live tool schemas. Verify version-sensitive limits and returned shapes before relying on them.

1. **Targeted edits match fetched Markdown exactly.** Read the active update tool's schema; `update_content` currently uses `content_updates[].old_str` and `new_str`. Copy the existing snippet from a fresh `notion-fetch`, preserve whitespace, and narrow ambiguous matches. Use the returned error to correct a mismatch; never assume a rejected or queued edit completed.
2. **New databases may land at the bottom of the parent page's children.** Verify placement with a fetch. For an authorized move, preserve the exact fetched child-page/database tags and follow the active edit schema. If child-deletion validation refuses an edit, preserve the error and read back the page before retrying; never enable `allow_deleting_content` to bypass a placement problem. An intended child deletion follows the tool's named-child confirmation requirement.
3. **Batch limits follow the active schema.** Some `notion-create-pages` schemas allow 100 rows; verify the actual limit and use batching only within the user's write and readback constraints.
4. **Discover the current tool set.** Read available descriptions and the changelog when something looks missing; release cadence is not a capability guarantee.
5. **Writes fail with `archived ancestor` if any parent (page / database / data source) is in the trash.** `notion-fetch` against the data source still returns the schema, masking this during pre-flight — the failure only surfaces at write time. Before trusting pre-flight to greenlight writes on an unfamiliar target, `notion-fetch <page_id>` and check for the `deleted` attribute on the returned `<page>` tag.

## Maintenance

This skill encodes routing rules, the pre-flight, and the operational checks above. Per-tool syntax → tool descriptions; CLI commands → `ntn --help`; Markdown rules → the `notion://docs/enhanced-markdown-spec` resource; capability evolution → https://developers.notion.com/page/changelog; auth → the CLI docs URL. A new MCP tool or `ntn` subcommand requires no skill update — discovery happens via the tool or CLI itself.

## Privacy

Never echo a Notion API token (prefix `ntn_…` for `ntn` OAuth or `secret_…` for integration tokens) in tool output, logs, commits, or PR bodies. The token belongs in `.envrc` (gitignored, `chmod 600`) or `~/.config/ntn/`, never in tracked files.
