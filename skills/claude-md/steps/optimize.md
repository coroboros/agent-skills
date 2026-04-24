# claude-md optimize

Deep cleanup of a bloated CLAUDE.md file. Triggered when `$ARGUMENTS` contains "optimize".

## Step 0: Read the optimization guide (REQUIRED FIRST)

Use the Read tool on `${CLAUDE_SKILL_DIR}/references/optimize-guide.md` BEFORE doing anything else. This file contains the research data (ETH Zurich study), the 6 bloat categories with specific examples, target metrics, and before/after examples. Skipping it produces a subpar optimization — the guide's concrete examples are what make the removal criteria unambiguous.

## Step 1: Inventory

Read every `CLAUDE.md`, `CLAUDE.local.md`, and `.claude/rules/*.md` in the project. Count total lines.

## Step 2: Read linter configs

Read ESLint / Biome / Prettier / TypeScript configs. Any CLAUDE.md line duplicating an enforced rule → delete.

## Step 3: Apply the 6 bloat categories

For each line ask: "Can the agent discover this by reading the project, or does a linter enforce this?" If yes → delete.

The 6 categories (full examples in the guide):

1. **Linter-enforced rules** (ESLint, Prettier, Biome, TypeScript strict) — the tool enforces it, the agent doesn't need a reminder
2. **Marketing / goals / vision** — zero code value
3. **Obvious info the agent discovers itself** — directory structure, framework defaults, deps from `package.json`
4. **Verbose explanations** — paragraphs where 1 line suffices, tutorials, history
5. **Redundant specs** — copies of config files, schema descriptions, env var lists
6. **Generic best practices** — "write clean code", "DRY", "SOLID"

## Step 4: Keep only essentials

- Project purpose (1–3 lines)
- Tech stack (compact, non-obvious only)
- Commands including testing (non-obvious only)
- Important files (non-obvious only)
- Project-specific rules (prohibitions + constraints)
- Workflow (only if non-standard)

## Step 5: Compress

- Paragraphs → bullet points
- 3-line rules → 1-line rules
- Zero filler words ("In order to", "It's important to note that")
- Merge related items

## Step 6: Present diff

Show before/after with line counts. For each removal, cite which bloat category it falls under. Let the user approve before applying changes.

**Target:** under 200 lines per file (current Claude Code guidance). Shorter is better — adherence drops measurably past 200.
