# Setup — astro-cloudflare scaffold

Per-scaffold steps for the `astro-cloudflare` scaffold. Invoked from `SKILL.md` § *Workflow > Install*. The shared overlay (`scripts/overlay_templates.sh`) runs after these steps and writes the opinionated configs.

Treat every relative path below as relative to `{project_dir}`. Execute each shell block with an explicit `--dir "{project_dir}"` or equivalent cwd; never rely on a previous shell call preserving `cd` state.

Runtime gotchas (image service, assets directory, pre-build shim, Sharp pitfall) live in [`astro-cloudflare-notes.md`](./astro-cloudflare-notes.md) — read it when editing `astro.config.mjs` or `wrangler.jsonc` later.

## 1. Run the framework CLI

```bash
pnpm create astro@5 "{project_dir}" --template minimal --no-install --no-git --no-ai
```

## 2. Remove conflicts

The framework CLI may or may not have created these — delete idempotently:

- `.eslintrc*`, `eslint.config.*`, `.prettierrc*`, `prettier.config.*`
- `astro.config.mjs` — the shared overlay replaces the minimal template's empty config with the Cloudflare adapter configuration.
- `tsconfig.json` — the shared overlay replaces it with `astro/tsconfigs/strict`.
- `src/pages/index.astro` — the shared overlay replaces it with a minimal page that imports the global stylesheet.

## 3. Install additional dependencies

```bash
pnpm --dir "{project_dir}" add astro@6 @astrojs/cloudflare@13 @astrojs/sitemap@3 tailwindcss@4 @tailwindcss/vite@4
pnpm --dir "{project_dir}" add -D @astrojs/check typescript wrangler @biomejs/biome @google/design.md
```

## 4. CSS tokens

The shared overlay creates `{project_dir}/src/styles/global.css` with `@import "tailwindcss";` and imports it from the generated page. Tailwind v4 CSS custom properties and `@theme` tokens stay in that stylesheet.

## 5. Shared overlay

The shared overlay writes `.node-version`, `.dev.vars.example`, and the strict Astro `tsconfig.json` after the generator step. It merges shared ignore rules into the generator's `.gitignore` instead of replacing framework-specific entries.
