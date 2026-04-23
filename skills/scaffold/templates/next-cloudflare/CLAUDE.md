# Project: [Project Name]

See @README.md for project overview and @package.json for available scripts.

## Architecture
- Framework: Next.js 16 (App Router) on Cloudflare Workers via @opennextjs/cloudflare
- Styling: Tailwind CSS
- DB: Neon Postgres via Drizzle ORM — schema in `src/db/schema/`
- Auth: Better-Auth — config in `src/lib/auth.ts`
- Validation: Zod schemas colocated with features in `src/features/[name]/schemas.ts`

## UI
- Design: see DESIGN.md at project root (Google DESIGN.md format — YAML frontmatter tokens + 8 prose sections; lint with `npx @google/design.md lint DESIGN.md`)
- IMPORTANT: Read DESIGN.md BEFORE creating or modifying any component
- Tailwind utilities mapped to DESIGN.md tokens via `tailwind.config.ts`
- CSS custom properties in `src/styles/global.css`
- Component library: shadcn/ui (`src/components/ui/`) — NEVER install full UI frameworks

## Commands
```bash
pnpm dev              # Next.js dev server (Turbopack)
pnpm build            # Production build
pnpm preview          # Local Workers preview (opennextjs-cloudflare)
pnpm deploy           # Build + deploy to Cloudflare Workers
pnpm db:push          # Push Drizzle schema to Neon
pnpm db:generate      # Generate Drizzle migrations
pnpm db:studio        # Open Drizzle Studio
pnpm check            # biome check --write
pnpm typecheck        # tsc --noEmit
```

## Key decisions
- Feature-based colocation: `src/features/[name]/` groups components, actions, schemas, hooks
- Server Actions + Zod for mutations, NOT API routes (unless consumed by external clients)
- Default to Server Components — `use client` only when strictly required
- Images: Cloudflare R2 + Images transformation
- ISR: OpenNext R2 incremental cache

## Environment
- `.dev.vars` for local Cloudflare bindings (gitignored)
- Types generated via `pnpm cf-typegen`

## Cloudflare tooling — non-negotiable
@.claude/rules/cloudflare-tooling.md

## Testing
- Vitest for unit/integration, Playwright for E2E (`pnpm test:e2e`)
- Write a failing test before fixing a bug
