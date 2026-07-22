---
name: scaffold
description: 'Bootstrap a new web project on a strictly opinionated Cloudflare Workers stack — Next.js 16 or Astro 6, TypeScript strict, pnpm, Biome, Tailwind. Use whenever the user asks to start, bootstrap, initialize, or scaffold a site/app in an empty or new directory. No fallbacks: skip for existing projects with package.json or framework config, non-Cloudflare deployments, Vercel/Netlify, ESLint/Prettier, or stack substitutions.'
license: MIT
metadata:
  author: coroboros
---

# Scaffold

Bootstrap the requested project with the opinionated stack.

The deterministic work — environment preflight, template overlay, `package.json` merge, post-scaffold verification — happens in three bundled scripts. Parse the invocation arguments, run the framework CLI, invoke the scripts in order, and turn their `RESULT:` lines into a concise report.

## Available scaffolds

| Scaffold | Framework | Infra | Stack highlights |
|----------|-----------|-------|-----------------|
| `next-cloudflare` | Next.js 16 (App Router) | Cloudflare Workers via OpenNext | Drizzle + Neon, Better-Auth, shadcn/ui, Vitest + Playwright |
| `astro-cloudflare` | Astro 6 (SSG-first, islands) | Cloudflare Workers | Zero JS by default, Content Collections, SEO rules |

**Shared across all scaffolds:** TypeScript strict, pnpm, Biome (no ESLint/Prettier), Tailwind CSS, `.node-version` 22.12.0.

If the user does not specify a scaffold or is ambiguous, show this table and ask which one.

## Workflow

`$SKILL_DIR` = this skill's folder — `${CLAUDE_SKILL_DIR}` in Claude Code, the directory containing this SKILL.md elsewhere.

### 1. Parse arguments

Extract `{scaffold}` and `{project_name}` from the invocation arguments. Aliases: `next-cf` → `next-cloudflare`, `astro-cf` → `astro-cloudflare`. Missing `{scaffold}` → show the *Available scaffolds* table and ask. Missing `{project_name}` → derive from cwd or ask. `{project_dir}` defaults to `.`.

### 2. Preflight

`bash "$SKILL_DIR"/scripts/preflight.sh "{project_dir}" "{project_name}"` → check `RESULT:` lines. Stop-conditions: `error=invalid-project-name` → ask for a valid lowercase npm package name whose Cloudflare slug is at most 63 characters; `error=invalid-target-name` → ask for a target whose final directory name is a valid lowercase npm package name; `pnpm=no` → provide the official pnpm installation command and stop; `jq=no` → point to https://jqlang.org/download/ and stop; `node=too-old` or `node=unsupported` → require a stable even-numbered Node release at 22.12.0 or newer; `target=occupied` → stop because this skill does not modify existing projects; `ok=true` → continue.

### 3. Install

Per-scaffold steps (framework CLI, conflict removal, dependency installs, CSS-token setup): `references/setup-{scaffold}.md`. Then apply the shared overlay:

```bash
bash "$SKILL_DIR"/scripts/overlay_templates.sh "{scaffold}" "{project_name}" "{project_dir}"
```

Writes opinionated configs (`biome.json`, `.worktreeinclude`, canonical `AGENTS.md`, thin `CLAUDE.md`, `.agents/rules/`, `.node-version`, `.dev.vars.example`, `wrangler.jsonc`, framework configs), ensures Tailwind is imported, merges the shared rules into the generator's `.gitignore`, and applies the validated name plus scripts and module settings to `package.json`. Every publication uses a same-directory temporary file and rejects destination or parent symlinks. Idempotent — skips existing files unless `--force`; `ok=partial` → show the skipped list, ask whether to rerun or keep partial.

### 4. Verify and summarize

`bash "$SKILL_DIR"/scripts/verify_scaffold.sh "{project_dir}"` runs `pnpm biome check --write .` and `pnpm typecheck`. On failure, surface the first 60 diagnostic lines + a fix; do not mark the scaffold complete. On success, report files created and next steps: configure `.dev.vars`, optionally hand off to `/award-design <brief>` and `/design-system audit DESIGN.md` when those skills are installed, then run `pnpm dev`.

## Rules

- NEVER install ESLint or Prettier — Biome handles everything.
- NEVER use CommonJS — ES modules only (`"type": "module"`).
- ALWAYS use pnpm as package manager.
- `target=occupied` is a hard stop. Never overlay or migrate an existing project with this skill.
- Do NOT author or replace `README.md` — preserve a framework-generated README; the user owns project-specific documentation.
- Do NOT initialize git — the user manages their own git workflow.
- For project-level decisions the scaffold deliberately does not make (i18n, dual auth, search, rich text, OG, MT, theme persistence, cache invalidation, admin uploads, CRM sync), read `"$SKILL_DIR"/references/decisions.md` and surface the relevant ones to the user after the summary report.

### astro-cloudflare specifics

When scaffolding `astro-cloudflare` or later editing its `astro.config.mjs` / `wrangler.jsonc`, read `"$SKILL_DIR"/references/astro-cloudflare-notes.md` — covers `imageService`, `assets.directory`, the pre-build shim, and the Sharp pitfall.
