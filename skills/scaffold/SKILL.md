---
name: scaffold
description: 'Bootstrap a new web project on a strictly opinionated Cloudflare Workers stack — Next.js 16 or Astro 6, TypeScript strict, pnpm, Biome, Tailwind. No fallbacks: no Vercel/Netlify, no ESLint/Prettier, no swap. Skip if the user wants any of these. Use when the user says "start a new project", "bootstrap", "init", "scaffold", "create a new site", or is working in an empty directory and wants production-ready foundations.'
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

### 1. Preflight

`bash ${CLAUDE_SKILL_DIR}/scripts/preflight.sh {project_dir}` → check `RESULT:` lines. Stop-conditions: `pnpm=no` → suggest `corepack enable && corepack prepare pnpm@latest --activate`; `node=too-old` → ask user to upgrade; `target=occupied` → confirm before proceeding; `ok=true` → continue.

### 2. Parse arguments

Extract `{scaffold}` and `{project_name}` from `$ARGUMENTS`. Aliases: `next-cf` → `next-cloudflare`, `astro-cf` → `astro-cloudflare`. Missing `{scaffold}` → show the *Available scaffolds* table and ask. Missing `{project_name}` → derive from cwd or ask. `{project_dir}` defaults to `.`.

### 3. Install

Per-scaffold steps (framework CLI, conflict removal, dependency installs, CSS-token setup): `references/setup-{scaffold}.md`. Then apply the shared overlay:

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/overlay_templates.sh {scaffold} {project_name} {project_dir}
```

Writes opinionated configs (`biome.json`, `.gitignore`, `.worktreeinclude`, `CLAUDE.md`, `wrangler.jsonc`, framework configs), merges `package.json` scripts, sets `"type": "module"` / `"private": true`. Idempotent — skips existing files unless `--force`; `ok=partial` → show the skipped list, ask whether to rerun or keep partial. Requires `jq`.

### 4. Verify and summarize

`bash ${CLAUDE_SKILL_DIR}/scripts/verify_scaffold.sh {project_dir}` runs `pnpm biome check --write .` and `pnpm typecheck`. On failure, surface the first 60 diagnostic lines + a fix; do not mark the scaffold complete. On success, report files created and next steps: configure `.dev.vars`, run `/award-design <brief>`, then `/design-system audit DESIGN.md`, finally `pnpm dev`.

## Rules

- NEVER install ESLint or Prettier — Biome handles everything.
- NEVER use CommonJS — ES modules only (`"type": "module"`).
- ALWAYS use pnpm as package manager.
- `target=occupied` is a warning, not a hard stop — ask before proceeding.
- Do NOT create `README.md` — the user writes it.
- Do NOT initialize git — the user manages their own git workflow.
- For project-level decisions the scaffold deliberately does not make (i18n, dual auth, search, rich text, OG, MT, theme persistence, cache invalidation, admin uploads, CRM sync), read `${CLAUDE_SKILL_DIR}/references/decisions.md` and surface the relevant ones to the user after the summary report.

### astro-cloudflare specifics

When scaffolding `astro-cloudflare` or later editing its `astro.config.mjs` / `wrangler.jsonc`, read `${CLAUDE_SKILL_DIR}/references/astro-cloudflare-notes.md` — covers `imageService`, `assets.directory`, the pre-build shim, and the Sharp pitfall.

## Gotchas (empirical — not in tool descriptions or SKILL.md body)

These three facts are stable: production-observed preflight and overlay failure modes. Cite file:line or a reproducible condition.

1. **Node version-string parsing rejects bare `22.x` and `-rc` suffixes.** `tests/scaffold/test_preflight.py:97-110` confirms: a version reported as `22.11.0` (no leading `v`) or `v22.0.0-rc.1` may be silently accepted-or-rejected depending on the regex path taken. Fix: normalize the string before parsing — strip a leading `v`, strip `-rc*` suffixes, accept any `22.x` variant.
2. **`target=occupied` warns but does not block.** The skill proceeds and may overwrite `package.json` or `biome.json` without explicit confirmation when the target directory is non-empty. Fix: when target is occupied, ask for confirmation before proceeding — make it a blocking gate; do not rely on the warning being noticed.
3. **`jq` missing from PATH silently skips the overlay step.** The scaffold uses `jq` to merge configuration; if `jq` is not installed, the overlay step is no-op and the user gets a partial scaffold without obvious indication. Fix: check `command -v jq` in preflight; fail hard if absent with the install instructions.
