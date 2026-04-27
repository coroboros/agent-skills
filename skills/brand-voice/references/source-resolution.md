# Source resolution

Each source flag (`-u`, `-n`, `-d`, `-f`) resolves to a body of Markdown text the LLM then synthesises into the canonical format. Flags are combinable; the skill aggregates all sources into a single working draft, then extracts the voice doc once.

## Resolution by flag

### `-u <url>` — URL via WebFetch

1. Validate the URL parses as `http(s)://...`.
2. Call `WebFetch` with a prompt of:
   > "Extract the writing voice signals from this page: paragraph rhythm, sentence length, vocabulary preferences, forbidden patterns, examples. Output Markdown with H2 sections for each signal type."
3. If `WebFetch` returns:
   - A complete Markdown document → use as a source contribution.
   - HTML or non-Markdown → treat the response as raw text; rely on the LLM to extract signals during synthesis.
   - An error (4xx, 5xx, timeout, binary content) → fall back to delegating to `/markitdown -s <url>` if installed; otherwise tell the user to fetch the URL manually and retry with `-f <local-path>`.

`WebFetch` rate-limits per host. If the user passes multiple `-u` to the same host, batch sequentially with a short delay (the tool handles this automatically; do not implement manual sleeps).

### `-n <id|url>` — Notion via MCP

1. Detect input shape:
   - Bare ID (UUID-like) → treat as a page ID.
   - `https://www.notion.so/...` URL → extract the trailing ID (last 32-char hex segment).
2. Call `mcp__claude_ai_Notion__notion-fetch` with the page ID.
3. If the page has linked sub-pages, fetch them at depth 1 (no recursion). The agent decides whether to include sub-page content based on whether the title looks voice-related (`voice`, `writing`, `style`, `tone`, `editorial`).
4. If the Notion MCP is not installed, error out:
   > "The Notion MCP is not installed. Install it from the Claude Code MCP catalog, or export the Notion page to Markdown and pass `-d <export-folder>` instead."
   Do not invent a workaround. Do not retry.

The MCP tool is authorised through Claude Code's permission layer, not via the skill's `allowed-tools` frontmatter.

### `-d <dir>` — Folder of Markdown

1. Validate the path resolves and is a directory.
2. `Glob <dir>/**/*.md` — list MD/MDX files.
3. If empty, error:
   > "No Markdown files in `<dir>`."
4. If the count is ≤ 5, read each file directly with `Read`.
5. If the count is > 5, dispatch a `general-purpose` subagent with:
   > "Read every `.md` file under `<dir>` and produce a single Markdown document concatenating their content with a `## <relative-path>` heading per file. Skip files with no prose (less than 50 chars of non-frontmatter content)."

The subagent is used past 5 files to keep the main skill's context clean — the aggregated draft can be 10K+ lines for a large brand archive.

### `-f <file>` — Single MD file

1. Validate extension: `.md`, `.mdx`, `.markdown`, or `.txt`. Other extensions are refused with:
   > "`<path>` has unsupported extension. Pass a Markdown or plain-text file."
2. `Read` the file directly.
3. The file becomes one source contribution.

Symbolic links are followed — there is no special handling. Files larger than 500KB trigger a warning ("source file is unusually large; voice extraction will summarise") but proceed.

### Interview mode (no flag)

When no source flag is present, dispatch `references/interview-questions.md` and ask the eight canonical questions one at a time via `AskUserQuestion`. The aggregated answers become the single source contribution.

## Aggregating multiple sources

When two or more sources are passed:

1. Resolve each independently per the above.
2. Concatenate into a single working draft, ordered by flag precedence: `-f`, `-d`, `-u`, `-n`, `(interview)`. The LLM receives the working draft with explicit headers per source.
3. Synthesise the canonical format. When sources conflict (e.g., one says "use 'we'", another says "never 'we'"), the skill flags the conflict to the user via `AskUserQuestion`. No silent override.
4. Record contributing sources in `voice.source_urls` (URL or path) for audit and for future `update` runs.

## Per-source contribution summary

After synthesis, the skill prints a contribution table to the user:

```
Source contribution summary
---------------------------
URL  https://example.com/voice           → 12 rules, 24 lexicon terms, 5 attributes
File ~/notes/style/house-style.md        → 4 rules, 8 lexicon terms, 1 context
Dir  ~/style-archive/                    → 7 rules, 12 lexicon terms, 3 contexts
                                            (skipped: 2 files under 50 chars)
```

The table makes it easy to spot a source that contributed nothing useful (typo in URL, empty Notion page, etc.) before the user accepts the draft.

## Failure modes

- **All sources fail** — skill aborts with the list of errors and a suggestion to retry interview mode.
- **One source fails, others succeed** — skill proceeds with the survivors and prints the failure inline. The user can re-run later with the failed source corrected.
- **Conflict the user can't decide** — skill saves both interpretations and lets the user pick post-hoc. The draft is marked `voice.source: "extract:unresolved"` to flag for review.
