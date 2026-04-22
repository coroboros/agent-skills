---
name: scaffold
description: Bootstrap a new web project with an opinionated Cloudflare Workers stack — Next.js 16 or Astro 6, TypeScript strict, pnpm, Biome, Tailwind. Use when the user says "start a new project", "bootstrap", "init", "scaffold", "create a new site", or is working in an empty directory and wants production-ready foundations.
when_to_use: When the user wants to start a new web project from scratch with a production-ready stack on Cloudflare Workers. Keywords — scaffold, bootstrap, init, start, new project, create site, new app, empty directory, greenfield. Works on empty dirs or brand-new ones. Skip when the project already has `package.json` / `astro.config.*` / `next.config.*` — use `/design-system` or `/award-design` on existing projects. Skip when the user wants a non-Cloudflare stack — this skill is opinionated toward Workers.
argument-hint: "<scaffold> [project-name]  — scaffolds: next-cloudflare, astro-cloudflare"
model: haiku
license: MIT
metadata:
  author: coroboros
---

# Scaffold

Bootstrap `$ARGUMENTS` with the opinionated stack.

## Available scaffolds

| Scaffold | Framework | Infra | Stack highlights |
|----------|-----------|-------|-----------------|
| `next-cloudflare` | Next.js 16 (App Router) | Cloudflare Workers via OpenNext | Drizzle + Neon, Better-Auth, shadcn/ui, Vitest + Playwright |
| `astro-cloudflare` | Astro 6 (SSG-first, islands) | Cloudflare Workers | Zero JS by default, Content Collections, SEO rules |

**Shared across all scaffolds:** TypeScript strict, pnpm, Biome (no ESLint/Prettier), Tailwind CSS, `.node-version` 22.

If the user does not specify a scaffold or is ambiguous, show this table and ask which one.

## Workflow

### 0. Verify requirements

Before running any CLI, confirm the required tools are available. Never auto-install — ask the user.

- `command -v pnpm` → if missing, suggest: `! corepack enable && corepack prepare pnpm@latest --activate`
- `node --version` → must be ≥ 22; if lower, stop and ask the user to upgrade (suggest `fnm`, `nvm`, or Volta)

Stop if anything is missing or below the minimum version.

### 1. Parse arguments

Extract `{scaffold}` and `{project_name}` from `$ARGUMENTS`.

- If `{scaffold}` is missing or not recognized, show the table above and ask.
- If `{project_name}` is missing, derive from current directory name or ask.
- Accept aliases: `next-cf` → `next-cloudflare`, `astro-cf` → `astro-cloudflare`.
- `{project_dir}` defaults to `.` (current directory). If the user specifies a path, use it.

### 2. Run the official scaffolding CLI

Use the framework's official CLI to create the project boilerplate. This handles tsconfig, tailwind config, directory structure, and framework-version-specific files.

**next-cloudflare:**
```bash
pnpm create next-app@latest {project_dir} --typescript --tailwind --eslint=false --app --src-dir --import-alias "@/*" --turbopack
```

**astro-cloudflare:**
```bash
pnpm create astro@latest {project_dir} -- --template minimal --typescript strictest --install --no-git
```
Then add Cloudflare and Tailwind integrations:
```bash
cd {project_dir} && pnpm astro add cloudflare tailwind sitemap --yes
```

### 3. Clean up conflicting files

Remove files that conflict with the opinionated stack:

- Delete: `.eslintrc*`, `eslint.config.*`, `.prettierrc*`, `prettier.config.*`
- Delete default CSS that will be replaced: `src/app/globals.css` content (keep file, empty it), `src/app/page.module.css`
- For Astro: remove any default `src/pages/index.astro` content (replace with minimal placeholder)

### 4. Overlay shared config and rules

Read template files from `{skill_dir}/templates/shared/` and write to the project:

- Read `{skill_dir}/templates/shared/biome.json.template` → write as `biome.json`
- Read `{skill_dir}/templates/shared/gitignore` → write as `.gitignore`
- Read `{skill_dir}/templates/shared/worktreeinclude` → write as `.worktreeinclude`. Tells Claude Code which gitignored files to copy into fresh worktrees — see [common-workflows](https://code.claude.com/docs/en/common-workflows#copy-gitignored-files-to-worktrees).
- Read `{skill_dir}/templates/shared/cloudflare-tooling.md` → write to `.claude/rules/cloudflare-tooling.md` (create `.claude/rules/` directory if needed). Applies to both `next-cloudflare` and `astro-cloudflare` — both ship on Workers and share the `wrangler` + `cf` CLI workflow.

### 5. Overlay framework-specific files

Read template files from `{skill_dir}/templates/{scaffold}/` and write to the project:

**next-cloudflare:**
- Read `CLAUDE.md` → write to project root, replace `[Project Name]` with `{project_name}`
- Read `wrangler.jsonc.template` → write as `wrangler.jsonc`, replace `project-name` with `{project_name}`
- Read `open-next.config.ts.template` → write as `open-next.config.ts`

**astro-cloudflare:**
- Read `CLAUDE.md` → write to project root, replace `[Project Name]` with `{project_name}`
- Read `seo.md` → write to `.claude/rules/seo.md` (create `.claude/rules/` directory)
- Read `astro.config.mjs.template` → write as `astro.config.mjs` (overwrite the CLI's default), replace `project-name.example` with the project's real domain if known, else leave as placeholder for the user
- Read `wrangler.jsonc.template` → write as `wrangler.jsonc`, replace `project-name` with `{project_name}`

### 6. Configure package.json scripts

Read the existing `package.json` created by the CLI, read the scripts template for the selected scaffold, then merge the scripts into `package.json`:

- `next-cloudflare` → `{skill_dir}/templates/next-cloudflare/scripts.json`
- `astro-cloudflare` → `{skill_dir}/templates/astro-cloudflare/scripts.json`

Also ensure `"type": "module"` and `"private": true` are set.

### 7. Install additional dependencies

**next-cloudflare:**
```bash
pnpm add @opennextjs/cloudflare drizzle-orm @neondatabase/serverless zod better-auth
pnpm add -D wrangler @biomejs/biome drizzle-kit vitest @playwright/test
```

**astro-cloudflare:**
```bash
pnpm add -D wrangler @biomejs/biome
```

### 8. Final setup

- Write `.node-version` containing `22`
- Write `.dev.vars.example` with a comment explaining its purpose
- Create `src/styles/global.css` if it doesn't exist (empty, for CSS custom properties)
- Run `pnpm biome check --write .` to format everything
- Run `pnpm typecheck` to verify clean state

### 9. Summary

Print a concise summary:

```
## Scaffolded: {project_name} ({scaffold})

**Files created/modified:**
- CLAUDE.md, biome.json, .gitignore, .worktreeinclude, .node-version
- [framework-specific files list]
- .claude/rules/ [if applicable]

**Next steps:**
1. Configure `.dev.vars` with your Cloudflare bindings
2. Run `/award-design` to create your DESIGN.md (the `/design-system` skill will auto-enforce its tokens during development)
3. `pnpm dev` to start developing
```

## Rules

- NEVER install ESLint or Prettier — Biome handles everything
- NEVER use CommonJS — ES modules only (`"type": "module"`)
- ALWAYS use pnpm as package manager
- If the target directory is not empty, warn the user and ask before proceeding
- Do NOT create README.md — the user will write it
- Do NOT initialize git — the user manages their own git workflow

### astro-cloudflare specifics

When scaffolding `astro-cloudflare` or later editing its `astro.config.mjs` / `wrangler.jsonc`, read `{skill_dir}/references/astro-cloudflare-notes.md` — covers `imageService`, `assets.directory`, the pre-build shim, and the Sharp pitfall.
