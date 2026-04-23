---
name: write-clear-readme
description: Author, audit, or polish a project README — clarity, structure (Pattern A grouped collapse / Pattern B per-entry collapse), wording concision, anchor integrity. Reads the repo first, proposes diffs, applies on approval.
when_to_use: When the user wants to create, restructure, audit, or polish a README for clarity, conciseness, or scannable structure. Keywords — write readme, author readme, audit readme, polish readme, clarify readme, optimize readme, restructure readme, README clarity, README wording, scannable readme. Useful for skill libraries, plugin monorepos, npm SDK references, CLI manuals, or any README showing scroll fatigue, unclear writing, or verbose passages. Skip when the user wants only spelling/grammar corrections — use `/fix-grammar` instead.
argument-hint: "[author|audit|polish] [optional path — defaults to ./README.md]"
model: opus
disable-model-invocation: true
allowed-tools: Read Write Edit Grep Glob Bash(git *) Bash(jq *)
license: MIT
compatibility: "Claude Code CLI (per Agent Skills spec). Graceful degradation in other environments supporting the open standard."
metadata:
  author: coroboros
---

# Write Clear README

Author, audit, or polish a README.md for clarity, conciseness, and scannable structure. Reads the repo state first; uses `<details>` collapse patterns where appropriate; proposes diffs and applies on approval.

Additional context from the user: $ARGUMENTS

## Context

- Repo: !`basename $(git rev-parse --show-toplevel 2>/dev/null || echo unknown)`
- Existing README: !`test -f README.md && wc -l < README.md | awk '{print $1 " lines"}' || echo "none"`
- Package manifest: !`test -f package.json && jq -r '.name + "@" + .version' package.json 2>/dev/null || echo "none"`
- Top-level folders: !`ls -d */ 2>/dev/null | head -20 | tr '\n' ' '`

## Two patterns

Long READMEs cause scroll fatigue — readers skim past important sections, lose their place, or give up. Collapse structural details with HTML `<details>` blocks. GitHub and most markdown renderers support them natively.

### Pattern A — Grouped collapse

**When**: a doc lists 5+ peer items that cluster into a small number of logical groups (≤7). Typical: skill libraries, plugin ecosystems, monorepo package indexes, component catalogs.

Group heading OUTSIDE `<details>` so `#group-name` anchors keep working, per-item headings inside:

```markdown
### Group Name

<details>
<summary><em>Expand — item1 · item2 · item3</em></summary>

<br>

#### item1
...

#### item2
...

</details>
```

Keep an overview table at the top listing all items with anchor links — users see the full scope without clicking.

### Pattern B — Per-entry collapse

**When**: reference docs with dozens of API entries, functions, CLI commands, or config options. Typical: npm package READMEs, SDK references, CLI manuals.

Signature in `<summary>` (inside `<code>` for monospace), one-line description after an em-dash, full detail hidden until expanded:

````markdown
## API

<details>
<summary><code>functionName(arg: T, opts?: Options): Result</code> — one-line description</summary>

<br>

Longer explanation. Params table, return value, edge cases, examples.

```ts
// usage
```

</details>

<details>
<summary><code>anotherFunction(x: X): Y</code> — what it does</summary>
...
</details>
````

Underused pattern — most npm READMEs list signatures as flat headings and force a 3000-line scroll. The `<details>` version is dramatically more scannable for reference-heavy docs.

## Universal rules

- **Overview visible** — TOC, tables, API index stay uncollapsed. Collapse *details*, not the *list*.
- **Anchors preserved** — navigation targets (group headings, API section heading) go OUTSIDE `<details>`. Headings inside still auto-anchor, and GitHub auto-expands the parent `<details>` on hash navigation.
- **`<br>` after `<summary>`** — markdown rendering inside `<details>` can be flaky; the explicit break is defensive and consistent.
- **No deep nesting** — one level of `<details>` max; nested collapsibles confuse navigation.
- **Signature-first summary (Pattern B)** — put the most identifying token first (function signature, command name, option name) so `Ctrl+F` hits the right entry immediately.

## When NOT to use

- Short docs (< 5 major sections) — adds clicks for no scroll savings
- Install / Quick Start / Requirements — users need these instantly visible
- Single-purpose tools where the README is already concise

## Subcommands

| Invocation | Mode |
|------------|------|
| `/write-clear-readme` | Default — if `README.md` exists, audit. Else, author from repo state. |
| `/write-clear-readme author [path]` | Create or fully restructure a README from scratch. |
| `/write-clear-readme audit [path]` | Review existing README for collapse opportunities + anchor/overview integrity + clarity issues. |
| `/write-clear-readme polish [path]` | Tighten wording, drop filler, clarify ambiguous passages — preserve structure, change only the prose. |

## Clarity rules

Whether authoring, auditing, or polishing — the prose itself follows these:

- **One idea per sentence.** Compound sentences with multiple clauses get split.
- **Front-load the verb.** "This skill helps you create" → "Create [...] with this skill" or simply "Creates [...]".
- **Drop filler.** "In order to" → "to". "It's important to note that" → delete. "Please make sure to" → imperative.
- **Concrete over abstract.** "Various improvements" → list 2-3 specific ones. "Optimized" → say *what* was optimized.
- **No marketing voice.** No "powerful", "robust", "delightful", "seamlessly", "leverage", "unlock". Replace with the actual capability or remove.
- **Show the shape early.** First 3 lines should let a reader decide if this README is for them — what the project is, who it's for, what it does (one verb).
- **Backtick code-like tokens** — file paths, command names, function names, env vars. `~/.claude/rules/` not ~/.claude/rules/.
- **Em-dashes for context, not parentheses** — `(also see foo)` → `— also see foo`. Reads less aside-y.
- **Lists over paragraphs** when the content is enumerable (≥3 items of the same kind).
- **Headings as questions or commands**, not topics. "Installation" is fine; "How do I install?" or "Install" reads quicker than "About installation".

## Remove AI traces

After any author or polish pass on English content, strip residual AI tells (em-dash overuse, rule of three, negative parallelisms, AI vocabulary, vague attributions, promotional tone, conjunctive padding like "moreover", "furthermore", "indeed").

- **Invoke `/humanize-en` if installed** — detects and fixes all 29 patterns in a single pass. Run it after clarity edits land but before presenting the diff. The skill preserves structure, code blocks, links, anchors, and frontmatter.
- **If the skill is not available**, scan manually for those patterns (see `humanize-en` or [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) for the full list) before shipping. Do not block on a missing skill.
- **Audit mode:** flag suspected AI tells in the findings but do not auto-rewrite.
- **Non-English content** — skip this step entirely; `humanize-en` is English-only.

## Author mode

1. **Inspect repo** — read `package.json` / `Cargo.toml`, top-level folders, entry points, `CLAUDE.md` if present. Identify what the README must cover (install, usage, API surface, architecture, license).
2. **Pick a pattern** —
   - Pattern A if 5+ peer items cluster into ≤7 groups (skill library, plugin list, monorepo packages)
   - Pattern B if the doc is reference-heavy (dozens of API entries, CLI commands, config options)
   - Short doc (< 5 sections) → no collapse
3. **Draft** — overview table at top with anchor links, Install / Quick Start / Requirements uncollapsed, grouped or per-entry collapse below. Apply Clarity rules as you write.
4. **Remove AI traces** — for English content, invoke `/humanize-en` on the draft (see *Remove AI traces* below). Skip if the skill is unavailable or the content is non-English.
5. **Verify** — every TOC anchor resolves. Every `<details>` has a `<br>` after `<summary>`. No nested collapsibles. Install block is never inside `<details>`.
6. **Write** — overwrite or create `README.md`. Present the diff if it existed before.

## Audit mode

1. **Read existing README** in full.
2. **Score against Universal rules** (structure):
   - Is the overview (TOC / index / table) visible without clicking?
   - Do all anchors resolve? (Every heading referenced in the TOC must exist and be outside `<details>`.)
   - Are any `<details>` blocks nested?
   - Is `<br>` present after every `<summary>`?
3. **Score against Clarity rules** (prose):
   - First 3 lines tell the reader what/who/why?
   - Filler phrases present? ("in order to", "it's important to note", "please make sure to")
   - Marketing voice present? ("powerful", "robust", "leverage", "seamlessly")
   - Verbose passages where bullets would do?
   - Code-like tokens unbacktick'd?
4. **Detect anti-patterns**:
   - Flat signature list 50+ lines deep → recommend Pattern B
   - 10+ peer sections without grouping → recommend Pattern A
   - `<details>` wrapping a group/section heading → broken anchor, must move heading outside
   - Nested `<details>` → flatten to one level
   - Install / Quick Start / Requirements inside a `<details>` → must surface
5. **Report** — bullet list of findings (split structure vs clarity) + proposed diff.
6. **Apply on request** — edit `README.md` only after explicit user approval.

## Polish mode

Wording-only pass. Structure stays as-is — only the prose changes.

1. **Read existing README** in full.
2. **Apply Clarity rules** sentence by sentence:
   - Drop filler phrases
   - Replace marketing voice with concrete verbs
   - Split compound sentences
   - Tighten verbose passages into bullets when enumerable
   - Backtick code-like tokens
   - Replace `(parens)` with em-dashes where they're aside-context
3. **Remove AI traces** — for English content, invoke `/humanize-en` on the result (see *Remove AI traces* below). Skip if the skill is unavailable or the content is non-English.
4. **Preserve** all anchors, headings, code blocks, diagrams, badges, and link URLs verbatim.
5. **Report** — propose a diff. NEVER apply without explicit approval.

## Rules

- NEVER auto-apply changes without user approval
- NEVER collapse Install / Quick Start / Requirements
- NEVER nest `<details>` blocks
- NEVER wrap a group heading or a TOC anchor target inside `<details>`
- NEVER change anchors, code blocks, or link URLs in polish mode (those are content, not prose)
- ALWAYS add `<br>` after `<summary>`
- ALWAYS match the existing README's style (quote convention, heading hierarchy, badge format) when editing
- Ignore `$ARGUMENTS` only if empty — otherwise treat first token as subcommand and second as path
