---
name: write-clear-readme
description: Author, audit, or polish a project README — clarity, structure (Pattern A per-section collapse / Pattern B grouped / Pattern C per-entry), wording concision, anchor integrity. Reads the repo first, proposes diffs, applies on approval.
when_to_use: When the user wants to create, restructure, audit, or polish a README for clarity, conciseness, or scannable structure. Keywords — write readme, author readme, audit readme, polish readme, clarify readme, optimize readme, restructure readme, README clarity, README wording, scannable readme. Useful for long human-facing docs (config READMEs, plugin monorepos), skill libraries, npm SDK references, CLI manuals, or any README showing scroll fatigue, unclear writing, or verbose passages. Skip when the user wants only spelling/grammar corrections — use `/fix-grammar` instead.
argument-hint: "[author|audit|polish] [optional path — defaults to ./README.md]"
model: opus
disable-model-invocation: true
allowed-tools: Read Write Edit Grep Glob Bash(git *) Bash(jq *)
license: MIT
compatibility: "Claude Code CLI (per Agent Skills spec). Graceful degradation in other environments supporting the open standard."
metadata:
  author: coroboros
---

<!--
Exception — `disable-model-invocation: true`. READMEs are high-stakes, user-facing
artifacts; Claude should never autonomously decide to rewrite one based on a casual
keyword. The user must explicitly invoke via `/write-clear-readme`. The `when_to_use`
keywords still help the user discover the skill in the `/` menu listing (per
`claude-code-skills.md`, skill listing is independent from model auto-invocation).
-->

# Write Clear README

<!-- canonical:writing-rules:start -->
## Important — Writing rules

These rules govern every prose artifact this skill emits — READMEs, CHANGELOGs, commit messages, PR bodies, release notes, doc paragraphs, non-trivial comments. Apply them at draft time, verify before output.

- Match the surrounding style — punctuation, capitalization, backtick conventions, em-dash vs parens, bullet style.
- Every sentence changes the reader's understanding. Cut it otherwise.
- Front-load the verb — "Creates", not "This helps you create".
- Concrete over abstract. Lists for ≥3 enumerable items.
- Assert positively. Reserve negation for real constraints (`NEVER commit secrets`).
- No marketing words: powerful, robust, seamlessly, leverage, unlock, comprehensive, delightful.
- No AI tells: delve, tapestry, intricate, pivotal, testament, underscore, crucial, garner, showcase, additionally, moreover, furthermore, indeed.
- After drafting English prose, invoke `/humanize-en` if installed.
<!-- canonical:writing-rules:end -->

Author, audit, or polish a README.md for clarity, conciseness, and scannable structure. Reads the repo state first; picks a collapse pattern by doc type; proposes diffs and applies on approval.

Additional context from the user: $ARGUMENTS

## Context

- Repo: !`basename $(git rev-parse --show-toplevel 2>/dev/null || echo unknown)`
- Existing README: !`test -f README.md && wc -l < README.md | awk '{print $1 " lines"}' || echo "none"`
- Package manifest: !`test -f package.json && jq -r '.name + "@" + .version' package.json 2>/dev/null || echo "none"`
- Top-level folders: !`ls -d */ 2>/dev/null | head -20 | tr '\n' ' '`

## Doc type → pattern

Long READMEs cause scroll fatigue. The fix is a structural decision before any prose: pick one collapse pattern for the whole doc and apply it uniformly. Selective collapse driven by per-section judgment — some sections visible, some hidden — creates a minefield. Readers cannot infer the rule, every heading becomes a guess.

| Doc type | Default pattern | Why |
|----------|-----------------|-----|
| Short single-purpose (<5 sections, <300 lines) | **No collapse** | Adds clicks for no scroll savings |
| Long human-facing, mixed-audience (config docs, personal `~/.claude/` companions, internal index READMEs) | **Pattern A — Per-section collapse** | One file, audiences self-select via expand; h2s read as scan-line |
| Skill library / plugin monorepo / package index (5+ peers, ≤7 groups) | **Pattern B — Grouped collapse** | Groups stay visible as scan-map; details hide |
| Library / SDK / CLI reference (dozens of API entries) | **Pattern C — Per-entry collapse** | Each function/command independently expandable |

Content shape comes before collapse. See [Author mode — Step 0](#author-mode).

### Pattern A — Per-section collapse

**When**: long human-facing doc serving more than one audience in one file (install + reference + meta-instructions). Per-section collapse turns the h2 list into a scan-line; readers expand only the section that matches their job.

H2 stays uncollapsed (scan-line + anchor target). Every sub-section inside h2 wraps in a `<details>` with the section label as `<summary>`. Drop the h3 above the disclosure — the `<summary>` carries the label.

```markdown
## Section name

Short intro paragraph (optional, visible).

<details>
<summary><em>Sub-section one</em></summary>

<br>

Content for sub-section one. Tables, paragraphs, code blocks.

</details>

<details>
<summary><em>Sub-section two</em></summary>

<br>

Content for sub-section two.

</details>
```

Two acceptable variants — pick one per h2 and stay consistent across the file:

- **Full per-section collapse** — no visible intro, every sub-section in `<details>`.
- **Intro + per-section collapse** — one short paragraph visible under each h2, then every sub-section in `<details>`. Use when the intro carries enough signal for the reader to decide whether to click.

What does NOT work: ad-hoc selective collapse where some sub-sections are visible and others hidden based on length or "frequency of use." The rule must be self-evident from the structure.

**Trade-off** — dropping the h3 loses the per-sub-section anchor. Acceptable for internal-facing docs with h2-only TOCs. When deep anchors matter (cross-doc links, external bookmarks), keep the h3 inside the `<details>` — GitHub auto-expands on hash navigation and the anchor resolves.

### Pattern B — Grouped collapse

**When**: 5+ peer items cluster into ≤7 logical groups. Typical: skill libraries, plugin ecosystems, monorepo package indexes, component catalogs.

Group heading stays OUTSIDE `<details>` so `#group-name` anchors keep working. Per-item content goes inside.

```markdown
### Group Name

<details>
<summary><em>item1 · item2 · item3</em></summary>

<br>

#### item1
...

#### item2
...

</details>
```

Keep an overview table at the top listing all items with anchor links — users see the full scope without clicking.

### Pattern C — Per-entry collapse

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
- **One rule per level** — when applying any collapse pattern, every peer at the chosen level collapses or none does. Selective collapse driven by per-section judgment ("collapse if length > N") is forbidden — mixed visibility without an obvious rule turns the page into a minefield.
- **No `Expand —` prefix** — the disclosure triangle is the universal affordance. `<summary><em>Files installed</em></summary>` reads cleanly; `<summary><em>Expand — files installed</em></summary>` adds a word of noise on every block and signals the author distrusts the reader.
- **No h3 directly above `<details>` that repeats the `<summary>` label** — duplicate signal. Drop the h3 and let the `<summary>` carry the label, OR move the h3 inside the `<details>` if the deep anchor matters.
- **No stale counts in `<summary>` or prose** — "25 symlinks", "14 tasks", "8 imports" rot the moment a row is added. Use qualitative descriptors: "symlinks installed by `install.sh`", "declared periodic tasks".
- **`<br>` after `<summary>`** — markdown rendering inside `<details>` can be flaky; the explicit break is defensive and consistent.
- **No deep nesting** — one level of `<details>` max; nested collapsibles confuse navigation.
- **Signature-first summary (Pattern C)** — put the most identifying token first (function signature, command name, option name) so `Ctrl+F` hits the right entry immediately.

## When NOT to collapse

- Short docs (<5 major sections, <300 lines) — adds clicks for no scroll savings.
- Install / Quick Start / Requirements — users need these instantly visible.
- Single-purpose tools where the README is already concise.
- Cases where no self-evident rule connects the choices — leave everything visible rather than ship a minefield.

## Subcommands

| Invocation | Mode |
|------------|------|
| `/write-clear-readme` | Default — if `README.md` exists, audit. Else, author from repo state. |
| `/write-clear-readme author [path]` | Create or fully restructure a README from scratch. |
| `/write-clear-readme audit [path]` | Review existing README for collapse opportunities + anchor/overview integrity + clarity issues. |
| `/write-clear-readme polish [path]` | Tighten wording, drop filler, clarify ambiguous passages — preserve structure, change only the prose. |

## README-specific style

The canonical *Writing rules* block above carries the universal prose rules. The bullets below add what is specific to authoring a README:

- **First-3-lines test.** A reader given only the first three lines must be able to (a) decide whether the doc is for them, and (b) predict the next section. A generic tagline followed by a list-of-contents fails the test — it asks for positioning, not enumeration.
- **Backtick code-like tokens** — file paths, command names, function names, env vars. `~/.claude/rules/` not ~/.claude/rules/.
- **Em-dashes for context, not parentheses** — `(also see foo)` → `— also see foo`. Reads less aside-y.
- **Headings as questions or commands**, not topics. "Installation" is fine; "How do I install?" or "Install" reads quicker than "About installation".
- **Qualitative over quantitative** — describe what content is, not how much of it. "Symlinks created by `install.sh`" beats "25 symlinks created by `install.sh`"; the count rots on add.

## Adjacent skills

- **`/fix-grammar`** — optional typo / spelling pre-pass before authoring, or post-pass after polish when the source has obvious errors. Skip when the text is already clean — this skill never introduces grammar errors.
- **`/humanize-en`** — AI-tell stripping. Called by `author` and `polish` modes after clarity edits; `audit` mode flags AI tells without rewriting. Also usable standalone.

## AI-tell removal — skill-specific notes

The canonical *Writing rules* block already requires invoking `/humanize-en` after any English-prose draft. The notes below pin two skill-specific behaviors:

- **Audit mode:** flag suspected AI tells in the findings but do not auto-rewrite.
- **Non-English content:** skip the humanize-en pass entirely — it is English-only.

## Author mode

1. **Inspect repo** — read `package.json` / `Cargo.toml`, top-level folders, entry points, `CLAUDE.md` if present. Identify what the README must cover (install, usage, API surface, architecture, license).
2. **Map audiences** — list the implicit reader for each major section (first-time installer, daily user, maintainer, agent reading CLAUDE.md context). Multi-audience files are candidates for Pattern A.
3. **Step 0 — Content shape** (BEFORE picking a collapse pattern):
   - Can content be cut? Sections that no longer earn their place.
   - Can a thin section merge into its parent?
   - Can a long table split by category into micro-tables?
   - Can a redundant column drop? (e.g. a `Source` column that just repeats the file path already in the row label.)
   - Can six bullets become one sentence? Or a long paragraph become bullets?
   - Only after shape is settled: pick a collapse pattern.
4. **Pick a pattern** — use the *Doc type → pattern* table. Confirm one rule per level applies cleanly; if not, simplify the structure further or fall back to no collapse.
5. **Draft** — overview table at top with anchor links, Install / Quick Start / Requirements uncollapsed, chosen collapse pattern applied uniformly below. Apply the canonical *Writing rules* + *README-specific style* as you write.
6. **Strip AI traces** — for English content, invoke `/humanize-en` on the draft (see *AI-tell removal — skill-specific notes* above). Skip if the skill is unavailable or the content is non-English.
7. **Verify structure** — every TOC anchor resolves. Every `<details>` has a `<br>` after `<summary>`. No nested collapsibles. Install block is never inside `<details>`. Pattern applied uniformly across all peers at the chosen level. No `Expand —` in `<summary>`. No h3 above a `<details>` that repeats the `<summary>` label. No numeric counts adjacent to content nouns.
8. **Verify rendering** — view the rendered output (GitHub preview, IDE markdown preview, or ask the user to confirm visually). Source-only checks miss visual monotony and inconsistent collapse patterns.
9. **Write** — overwrite or create `README.md`. Present the diff if it existed before.

## Audit mode

> **Silent assumption — name it.** This audit evaluates structure, anchor integrity, collapse uniformity, and prose tells. It does NOT evaluate whether the right content is in this file. For that, consider whether sections should be cut, merged, reshaped, or split into adjacent files — and ask the user before rewriting scope.

1. **Read existing README** in full.
2. **Run the structural audit script**: `${CLAUDE_SKILL_DIR}/scripts/audit_readme.py <path>` emits a JSON report covering unresolved anchors, nested `<details>`, missing `<br>` after `<summary>`, bloat tokens, `Expand —` prefixes, stale counts adjacent to nouns, h3-above-details redundancy, and a visual-rhythm signal (callout + image density). Exit 1 on hard findings; the JSON is your hit-list.
3. **Score against Universal rules** (structure — use the script output first):
   - Is the overview (TOC / index / table) visible without clicking?
   - Do all anchors resolve?
   - Are any `<details>` blocks nested?
   - Is `<br>` present after every `<summary>`?
   - Is the chosen collapse pattern applied uniformly at one level? (No mixed-visibility peers.)
   - Any `<summary>` starting with `Expand —`?
   - Any h3 directly above a `<details>` whose `<summary>` repeats the label?
   - Any numeric counts adjacent to content nouns ("25 X", "14 Y") that would rot on add?
4. **Score against the canonical *Writing rules* + *README-specific style*** (prose — the script covers mechanical bloat, you cover the rest):
   - First-3-lines test — can a reader decide if the doc is for them AND predict the next section?
   - Verbose passages where bullets would do?
   - Code-like tokens unbacktick'd?
5. **Map audiences** — for each major section, identify the implicit reader. When the file serves more than two audiences, flag as a Pattern A candidate.
6. **Visual rhythm** — soft signal from the script. Long user-facing READMEs with zero GitHub callouts (`> [!NOTE|TIP|WARNING|IMPORTANT|CAUTION]`) and zero images read as flat. Surface as a suggestion, not a finding.
7. **Detect anti-patterns**:
   - Flat signature list 50+ lines deep → recommend Pattern C.
   - 5+ peer sub-sections under one h2 in a long human-facing doc → recommend Pattern A.
   - 10+ peer sections clustering into groups → recommend Pattern B.
   - Selective `<details>` — some peers collapsed, others not, no inferable rule → call out as minefield; recommend uniform collapse or none.
   - `<details>` wrapping a group/section heading → broken anchor, must move heading outside.
   - Nested `<details>` → flatten to one level (flagged by the script).
   - Install / Quick Start / Requirements inside a `<details>` → must surface.
8. **Report** — bullet list of findings (split structure vs clarity vs content-shape suggestions) + proposed diff.
9. **Verify rendering after edits** — view the rendered output before declaring done.
10. **Apply on request** — edit `README.md` only after explicit user approval.

## Polish mode

Wording-only pass. Structure stays as-is — only the prose changes.

1. **Read existing README** in full.
2. **Apply the canonical *Writing rules* + *README-specific style*** sentence by sentence:
   - Drop filler phrases.
   - Replace marketing voice with concrete verbs.
   - Split compound sentences.
   - Tighten verbose passages into bullets when enumerable.
   - Backtick code-like tokens.
   - Replace `(parens)` with em-dashes where they are aside-context.
   - Replace numeric content-counts with qualitative descriptors.
3. **Strip AI traces** — for English content, invoke `/humanize-en` on the result (see *AI-tell removal — skill-specific notes* above). Skip if the skill is unavailable or the content is non-English.
4. **Preserve** all anchors, headings, code blocks, diagrams, badges, and link URLs verbatim.
5. **Report** — propose a diff. NEVER apply without explicit approval.

## Rules

- NEVER auto-apply changes without user approval.
- NEVER collapse Install / Quick Start / Requirements.
- NEVER nest `<details>` blocks.
- NEVER wrap a group heading or a TOC anchor target inside `<details>`.
- NEVER apply Pattern A or B partially — every peer at the chosen level collapses or none does.
- NEVER prefix `<summary>` with `Expand —` (or `Expand –`, `Expand -`).
- NEVER put a numeric content-count adjacent to a noun in prose or `<summary>` — qualitative descriptors only.
- NEVER change anchors, code blocks, or link URLs in polish mode (those are content, not prose).
- ALWAYS add `<br>` after `<summary>`.
- ALWAYS match the existing README's style (quote convention, heading hierarchy, badge format) when editing.
- ALWAYS verify the rendered output before declaring done (GitHub preview, IDE preview, or user confirmation).
- Empty `$ARGUMENTS` follows the *Subcommands* default row above. Non-empty: first token is the subcommand, second is the path.
