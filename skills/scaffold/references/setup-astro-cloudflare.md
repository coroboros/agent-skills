# Setup — astro-cloudflare scaffold

Per-scaffold steps for the `astro-cloudflare` scaffold. Invoked from `SKILL.md` § *Workflow > Install*. The shared overlay (`scripts/overlay_templates.sh`) runs after these steps and writes the opinionated configs.

Treat every relative path below as relative to `{project_dir}`. Execute each shell block with an explicit `--dir "{project_dir}"` or equivalent cwd; never rely on a previous shell call preserving `cd` state.

Runtime gotchas (image service, assets directory, pre-build shim, Sharp pitfall) live in [`astro-cloudflare-notes.md`](./astro-cloudflare-notes.md) — read it when editing `astro.config.mjs` or `wrangler.jsonc` later.

## 1. Run the framework CLI

```bash
pnpm create astro@latest {project_dir} -- --template minimal --typescript strictest --install --no-git
pnpm --dir "{project_dir}" exec astro add cloudflare tailwind sitemap --yes
```

## 2. Remove conflicts

The framework CLI may or may not have created these — delete idempotently:

- `.eslintrc*`, `eslint.config.*`, `.prettierrc*`, `prettier.config.*`
- Replace the default `src/pages/index.astro` with a minimal placeholder.

## 3. Install additional dependencies

```bash
pnpm --dir "{project_dir}" add -D wrangler @biomejs/biome @google/design.md
```

## 4. CSS tokens

Create `{project_dir}/src/styles/global.css` (empty — for CSS custom properties) if absent.

## 5. Helper files

Write `{project_dir}/.node-version` containing `22`. Write `{project_dir}/.dev.vars.example` with a short comment explaining it's a placeholder for Cloudflare bindings.
