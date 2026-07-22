# Setup — next-cloudflare scaffold

Per-scaffold steps for the `next-cloudflare` scaffold. Invoked from `SKILL.md` § *Workflow > Install*. The shared overlay (`scripts/overlay_templates.sh`) runs after these steps and writes the opinionated configs.

Treat every relative path below as relative to `{project_dir}`. Execute each shell block with an explicit `--dir "{project_dir}"` or equivalent cwd; never rely on a previous shell call preserving `cd` state.

## 1. Run the framework CLI

```bash
pnpm create next-app@16 "{project_dir}" --typescript --tailwind --no-linter --no-react-compiler --app --src-dir --import-alias "@/*" --turbopack --use-pnpm --disable-git --no-agents-md --yes
```

## 2. Remove conflicts

The framework CLI may or may not have created these — delete idempotently:

- `.eslintrc*`, `eslint.config.*`, `.prettierrc*`, `prettier.config.*`
- `src/app/page.module.css`

Keep `src/app/globals.css`. The generator creates the Tailwind import and the shadcn initializer extends that file.

## 3. Install additional dependencies

```bash
pnpm --dir "{project_dir}" add @opennextjs/cloudflare drizzle-orm @neondatabase/serverless zod better-auth
pnpm --dir "{project_dir}" add -D wrangler @biomejs/biome @google/design.md drizzle-kit vitest @playwright/test shadcn@4
pnpm --dir "{project_dir}" exec shadcn init --defaults --base base --no-rtl
```

## 4. CSS tokens

Tailwind v4 and shadcn tokens live in `src/app/globals.css`. The shared overlay preserves the generated theme and restores `@import "tailwindcss";` if an upstream initializer removes it. No `tailwind.config.ts` or `src/styles/` is created.

## 5. Shared overlay

The shared overlay writes `.node-version` and `.dev.vars.example` after the generator step. It merges the shared ignore rules into create-next-app's existing `.gitignore`, retaining framework entries such as `.next/` and any future generator-specific rules.
