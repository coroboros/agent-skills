# Setup — next-cloudflare scaffold

Per-scaffold steps for the `next-cloudflare` scaffold. Invoked from `SKILL.md` § *Workflow > Install*. The shared overlay (`scripts/overlay_templates.sh`) runs after these steps and writes the opinionated configs.

Treat every relative path below as relative to `{project_dir}`. Execute each shell block with an explicit `--dir "{project_dir}"` or equivalent cwd; never rely on a previous shell call preserving `cd` state.

## 1. Run the framework CLI

```bash
pnpm create next-app@latest {project_dir} --typescript --tailwind --eslint=false --app --src-dir --import-alias "@/*" --turbopack
```

## 2. Remove conflicts

The framework CLI may or may not have created these — delete idempotently:

- `.eslintrc*`, `eslint.config.*`, `.prettierrc*`, `prettier.config.*`
- `src/app/page.module.css`
- Empty `src/app/globals.css` — keep the file, clear its contents. `/design-system` later rewrites it from DESIGN.md, re-adding `@import "tailwindcss"` + the `@theme` token block.

## 3. Install additional dependencies

```bash
pnpm --dir "{project_dir}" add @opennextjs/cloudflare drizzle-orm @neondatabase/serverless zod better-auth
pnpm --dir "{project_dir}" add -D wrangler @biomejs/biome @google/design.md drizzle-kit vitest @playwright/test
```

## 4. CSS tokens

Tailwind v4 keeps tokens in `src/app/globals.css` — `create-next-app` created it; step 2 emptied it. No `tailwind.config.ts`, no `src/styles/`. Nothing to create here.

## 5. Helper files

Write `{project_dir}/.node-version` containing `22`. Write `{project_dir}/.dev.vars.example` with a short comment explaining it's a placeholder for Cloudflare bindings.
