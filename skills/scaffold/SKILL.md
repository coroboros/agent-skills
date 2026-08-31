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

`bash "$SKILL_DIR"/scripts/preflight.sh "{project_dir}" "{project_name}"` → check `RESULT:` lines. Stop on `error=invalid-project-name`, `error=invalid-cloudflare-service-name`, or `error=invalid-target-name` and request the named constraint; on `pnpm=no`, `jq=no`, or `node=no|too-old|unsupported`, provide the official install or version remediation; on `target=occupied`, require an empty target including dotfiles. Continue only on `ok=true`.

### 3. Install

Per-scaffold steps (framework CLI, conflict removal, dependency installs, CSS-token setup): `references/setup-{scaffold}.md`. Then apply the shared overlay:

```bash
bash "$SKILL_DIR"/scripts/overlay_templates.sh "{scaffold}" "{project_name}" "{project_dir}"
```

Writes opinionated configs (`biome.json`, `.worktreeinclude`, canonical `AGENTS.md`, thin `CLAUDE.md`, `.agents/rules/`, `.node-version`, `.dev.vars.example`, `wrangler.jsonc`, framework configs), ensures Tailwind is imported, merges the shared rules into the generator's `.gitignore`, and applies the validated name plus scripts and module settings to `package.json`. Every publication uses a same-directory temporary file and rejects destination or parent symlinks. Idempotent — skips existing files unless `--force`; `ok=partial` → show the skipped list, ask whether to rerun or keep partial.

### 4. Verify and summarize

`bash "$SKILL_DIR"/scripts/verify_scaffold.sh "{project_dir}"` runs `pnpm biome check --write .` and `pnpm typecheck`. On failure, surface the first 60 diagnostic lines + a fix; do not mark the scaffold complete. On success, report files created and next steps: configure `.dev.vars`, optionally hand off to `/award-design <brief>` (award-level direction, then `/design-system audit DESIGN.md`) or `/frontend-dev` (everyday UI) when those skills are installed, then run `pnpm dev`.

## Rules

- Use Biome for linting and formatting.
- Use ES modules (`"type": "module"`).
- Use pnpm.
- Treat `target=occupied` as a hard stop; this skill creates new projects only.
- Preserve framework-generated `README.md`; leave project-specific documentation and Git initialization to the user.
- For project-level decisions the scaffold deliberately does not make (i18n, dual auth, search, rich text, OG, MT, theme persistence, cache invalidation, admin uploads, CRM sync), read `"$SKILL_DIR"/references/decisions.md` and surface the relevant ones to the user after the summary report.

### astro-cloudflare specifics

When scaffolding `astro-cloudflare` or later editing its `astro.config.mjs` / `wrangler.jsonc`, read `"$SKILL_DIR"/references/astro-cloudflare-notes.md` — covers `imageService`, `assets.directory`, the pre-build shim, and the Sharp pitfall.
