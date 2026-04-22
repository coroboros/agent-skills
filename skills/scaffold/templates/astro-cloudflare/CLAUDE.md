# Project: [Project Name] — Acquisition Site

See @README.md for project overview and @package.json for available scripts.

## Architecture
- Framework: Astro 6 (SSG-first, islands architecture) on Cloudflare Workers
- Runtime: workerd — dev and prod use the same engine
- Styling: Tailwind CSS
- Content: Astro Content Collections or MDX in `src/content/`

## UI
- Design: see DESIGN.md at project root (Google Stitch format)
- IMPORTANT: Read DESIGN.md BEFORE creating or modifying any component
- Tailwind utilities mapped to DESIGN.md tokens via `tailwind.config.ts`
- CSS custom properties in `src/styles/global.css`
- No component library — Astro components are the components

## Commands
```bash
pnpm dev              # Astro dev server (runs on workerd)
pnpm build            # Production build
pnpm preview          # Preview built app locally (workerd)
pnpm deploy           # Build + wrangler deploy
pnpm check            # biome check --write
pnpm typecheck        # astro check && tsc --noEmit
```

## Key decisions
- Zero JS by default — every KB of JS must be justified
- Use `.astro` components for everything static — NOT React
- React islands ONLY for interactive widgets (`client:visible` preferred over `client:load`)
- Images: Astro `<Image>` component, NOT `<img>` tags
- Astro 6 bindings: `env.MY_BINDING` directly, NOT deprecated `Astro.locals.runtime`
- Astro Actions (`defineAction`) + Zod for form handling in SSR routes

## SEO — non-negotiable
@.claude/rules/seo.md

## Environment
- `.dev.vars` for local Cloudflare bindings (gitignored)
- Types generated via `pnpm cf-typegen`

## Cloudflare tooling — non-negotiable
@.claude/rules/cloudflare-tooling.md
