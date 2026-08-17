# Project: [Project Name] — Acquisition Site

See @package.json for available scripts.

## Rule Index
Read the matching rule before planning or editing that surface:

- `.agents/rules/cloudflare-tooling.md` — Cloudflare CLI scope, authentication, images, and destructive-command policy
- `.agents/rules/seo.md` — required metadata, structured data, sitemap, robots, and performance budgets

## Architecture
- Framework: Astro 6 (SSG-first, islands architecture) on Cloudflare Workers
- Runtime: workerd — dev and prod use the same engine
- Styling: Tailwind CSS
- Content: Astro Content Collections or MDX in `src/content/`

## UI
- Source of truth: DESIGN.md at project root (Google DESIGN.md format — YAML frontmatter tokens + 8 prose sections)
- If `/design-system` is installed (`npx skills add coroboros/agent-skills --skill design-system`): auto-activates on UI edits to enforce tokens; subcommands `audit` / `audit --strict` / `diff` / `export tailwind` / `migrate` / `init`
- Otherwise validate directly with the installed project CLI: `pnpm design:audit`
- IMPORTANT: Read DESIGN.md BEFORE creating or modifying any component
- Tailwind v4 theme tokens and CSS custom properties in `src/styles/global.css`
- No component library — Astro components are the components

## Commands
```bash
pnpm dev              # Astro dev server (runs on workerd)
pnpm build            # Production build
pnpm preview          # Preview built app locally (workerd)
pnpm deploy           # Build + wrangler deploy
pnpm check            # biome check --write
pnpm typecheck        # astro check && tsc --noEmit
pnpm design:audit     # Validate DESIGN.md with the project-local canonical CLI
```

## Key decisions
- Zero JS by default — every KB of JS must be justified
- Use `.astro` components for everything static — NOT React
- React islands ONLY for interactive widgets (`client:visible` preferred over `client:load`)
- Images: Astro `<Image>` component, NOT `<img>` tags
- Astro 6 bindings: `env.MY_BINDING` directly, NOT deprecated `Astro.locals.runtime`
- Astro Actions (`defineAction`) + Zod for form handling in SSR routes

## Middleware in production — non-negotiable

Astro middleware runs **at build-time only for prerendered routes**, and at runtime only for on-demand-rendered ones. With the default `output: 'static'`, middleware-set **response headers** (CSP, HSTS, `Link`, content negotiation, easter eggs) are silently dropped in prod — even though they work in `pnpm dev`, which always runs middleware. `pnpm dev` will mask the bug; verify in `pnpm preview` (workerd, same runtime as prod).

Two patterns to make middleware apply:

**1. Pages that need middleware-set headers** — opt the page into SSR per-route:
```astro
---
export const prerender = false;
// ... rest of frontmatter
---
```

**2. Non-page endpoints** (well-known paths, JSON APIs) — create an explicit Astro route, not a middleware pathname branch. The `@astrojs/cloudflare` handler short-circuits to `env.ASSETS.fetch()` for paths with no matching `routeData`, so middleware never sees the request and the asset binding returns `404.html`.
```ts
// src/pages/.well-known/example.ts
import type { APIRoute } from 'astro';
export const prerender = false;
export const GET: APIRoute = () => new Response(JSON.stringify({}), {
  headers: { 'Content-Type': 'application/json' },
});
```

The `@astrojs/cloudflare` adapter does not (yet) expose `middlewareMode: 'edge'` or `staticHeaders: true` — these only exist on the Netlify, Vercel, and Node adapters.

## Environment
- `.dev.vars` for local Cloudflare bindings (gitignored)
- Types generated via `pnpm cf-typegen`
