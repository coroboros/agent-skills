---
name: scaffold
description: Bootstrap a new web project with an opinionated Cloudflare Workers stack — Next.js 16 or Astro 6, TypeScript strict, pnpm, Biome, Tailwind. Use when the user says "start a new project", "bootstrap", "init", "scaffold", "create a new site", or is working in an empty directory and wants production-ready foundations.
when_to_use: When the user wants to start a new web project from scratch with a production-ready stack on Cloudflare Workers. Keywords — scaffold, bootstrap, init, start, new project, create site, new app, empty directory, greenfield. Works on empty dirs or brand-new ones. Skip when the project already has `package.json` / `astro.config.*` / `next.config.*` — use `/design-system` or `/award-design` on existing projects. Skip when the user wants a non-Cloudflare stack — this skill is opinionated toward Workers.
argument-hint: "<scaffold> [project-name]  — scaffolds: next-cloudflare, astro-cloudflare"
model: haiku
license: MIT
compatibility: "Claude Code CLI (per Agent Skills spec). Graceful degradation in other environments supporting the open standard."
metadata:
  author: coroboros
---

# Scaffold

Bootstrap `$ARGUMENTS` with the opinionated stack.

The deterministic work — environment preflight, template overlay, `package.json` merge, post-scaffold verification — happens in three bundled scripts. This skill parses `$ARGUMENTS`, runs the framework CLI, invokes the scripts in order, and turns their `RESULT:` lines into a concise report.

## Available scaffolds

| Scaffold | Framework | Infra | Stack highlights |
|----------|-----------|-------|-----------------|
| `next-cloudflare` | Next.js 16 (App Router) | Cloudflare Workers via OpenNext | Drizzle + Neon, Better-Auth, shadcn/ui, Vitest + Playwright |
| `astro-cloudflare` | Astro 6 (SSG-first, islands) | Cloudflare Workers | Zero JS by default, Content Collections, SEO rules |

**Shared across all scaffolds:** TypeScript strict, pnpm, Biome (no ESLint/Prettier), Tailwind CSS, `.node-version` 22.

If the user does not specify a scaffold or is ambiguous, show this table and ask which one.

## Workflow

### 1. Preflight — environment check

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/preflight.sh {project_dir}
```

Parse `RESULT:` lines. Stop-conditions:
- `pnpm=no` → suggest `corepack enable && corepack prepare pnpm@latest --activate`, then ask the user to retry.
- `node=too-old` → ask the user to upgrade (suggest `fnm`, `nvm`, or Volta). Do not auto-install.
- `target=occupied` → warn that `package.json` / framework config already exists; ask before proceeding.
- `ok=true` → continue.

### 2. Parse arguments

Extract `{scaffold}` and `{project_name}` from `$ARGUMENTS`.

- `{scaffold}` missing or unknown → show the table and ask.
- `{project_name}` missing → derive from current directory name or ask.
- Aliases: `next-cf` → `next-cloudflare`, `astro-cf` → `astro-cloudflare`.
- `{project_dir}` defaults to `.`; respect a user-supplied path.

### 3. Run the framework CLI

Use the framework's own CLI to create the boilerplate — `tsconfig`, Tailwind config, directory structure, version-specific files.

**next-cloudflare:**
```bash
pnpm create next-app@latest {project_dir} --typescript --tailwind --eslint=false --app --src-dir --import-alias "@/*" --turbopack
```

**astro-cloudflare:**
```bash
pnpm create astro@latest {project_dir} -- --template minimal --typescript strictest --install --no-git
cd {project_dir} && pnpm astro add cloudflare tailwind sitemap --yes
```

### 4. Remove conflicts

Delete files that conflict with the opinionated stack. The framework CLI may or may not have created them — delete idempotently.

- `.eslintrc*`, `eslint.config.*`, `.prettierrc*`, `prettier.config.*`
- Empty `src/app/globals.css` (keep the file, clear its contents)
- `src/app/page.module.css`
- For astro: replace the default `src/pages/index.astro` with a minimal placeholder

### 5. Overlay templates + merge package.json scripts

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/overlay_templates.sh {scaffold} {project_name} {project_dir}
```

Writes `biome.json`, `.gitignore`, `.worktreeinclude`, `.claude/rules/cloudflare-tooling.md`, `CLAUDE.md`, `wrangler.jsonc`, framework-specific configs; merges opinionated scripts into `package.json` and sets `"type": "module"` / `"private": true`. Idempotent — skips existing files unless called with `--force`. Requires `jq` (brew install jq).

Parse `RESULT:` lines:
- `ok=true` → proceed.
- `ok=partial` → some files existed; show the skipped list, ask the user whether to rerun with `--force` or keep the partial overlay.

### 6. Install additional dependencies

**next-cloudflare:**
```bash
pnpm add @opennextjs/cloudflare drizzle-orm @neondatabase/serverless zod better-auth
pnpm add -D wrangler @biomejs/biome drizzle-kit vitest @playwright/test
```

**astro-cloudflare:**
```bash
pnpm add -D wrangler @biomejs/biome
```

### 7. Init remaining files

- Write `.node-version` containing `22`.
- Write `.dev.vars.example` with a short comment explaining its purpose.
- Create `src/styles/global.css` (empty — for CSS custom properties) if absent.

### 8. Verify

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/verify_scaffold.sh {project_dir}
```

Runs `pnpm biome check --write .` and `pnpm typecheck`. On failure, surfaces the first 60 diagnostic lines on stderr. `biome=fail` or `typecheck=fail` → report the diagnostics to the user with a suggested fix. Do not mark the scaffold as complete.

### 9. Summary

Print:

```
## Scaffolded: {project_name} ({scaffold})

**Files created/modified:**
- CLAUDE.md, biome.json, .gitignore, .worktreeinclude, .node-version
- [framework-specific list from overlay_templates output]
- .claude/rules/ [if applicable]

**Next steps:**
1. Configure `.dev.vars` with your Cloudflare bindings.
2. Run `/award-design` to create DESIGN.md; `/design-system` will auto-enforce its tokens during development.
3. `pnpm dev` to start developing.
```

## Rules

- NEVER install ESLint or Prettier — Biome handles everything.
- NEVER use CommonJS — ES modules only (`"type": "module"`).
- ALWAYS use pnpm as package manager.
- `target=occupied` is a warning, not a hard stop — ask before proceeding.
- Do NOT create `README.md` — the user writes it.
- Do NOT initialize git — the user manages their own git workflow.

### astro-cloudflare specifics

When scaffolding `astro-cloudflare` or later editing its `astro.config.mjs` / `wrangler.jsonc`, read `${CLAUDE_SKILL_DIR}/references/astro-cloudflare-notes.md` — covers `imageService`, `assets.directory`, the pre-build shim, and the Sharp pitfall.
