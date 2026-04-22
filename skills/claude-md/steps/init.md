# claude-md init

Scaffold a minimal CLAUDE.md with only the essential sections. Triggered when `$ARGUMENTS` contains "init".

## Step 1: Detect project context

Read `package.json` (or equivalent: `pyproject.toml`, `Cargo.toml`, `go.mod`, etc.) to detect:

- Project name
- Tech stack (framework, language)
- Available scripts/commands (dev, build, test)

Also check for existing linter configs (ESLint, Biome, Prettier, tsconfig). Do NOT include rules they already enforce — a generated CLAUDE.md that duplicates linter rules burns tokens without adding value.

## Step 2: Identify important files

Scan for non-obvious architecture-critical files. Look for:

- Auth config files
- Server action wrappers, API helpers
- Database schema files
- Custom middleware or shared utilities

Skip standard framework files (`package.json`, `tsconfig`, `next.config`, etc.) — the agent discovers these itself.

## Step 3: Generate CLAUDE.md

Create the file with ONLY these sections. Each section should be compact — the whole file should be under 50 lines.

```markdown
# [Project Name]
[One-line description of what this project is]

## Tech Stack
- [Only non-obvious technologies — skip deps detectable from config files]

## Commands
- `[dev command]` - Dev server
- `[build command]` - Build
- `[test command]` - Tests
- [Any non-obvious commands like db:push, seed, etc.]

## Important Files
- [Only files the agent wouldn't discover naturally]

## Rules
- [Leave empty with a comment: "Add project-specific rules as you encounter friction"]
```

## Step 4: Present and write

Show the generated file to the user. Write it to `./CLAUDE.md` after approval.

## Rules

- NEVER include directory structure, code style rules, generic best practices, or marketing text
- NEVER include anything a linter or TypeScript already enforces
- Target: 20–50 lines. If it's longer, you're including too much
- The Rules section starts empty — it gets populated over time as mistakes happen
