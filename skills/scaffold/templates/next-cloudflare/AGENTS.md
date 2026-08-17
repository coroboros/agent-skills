# Project: [Project Name]

See @package.json for available scripts.

## Rule Index
Read the matching rule before planning or editing that surface:

- `.agents/rules/cloudflare-tooling.md` — Cloudflare CLI scope, authentication, images, and destructive-command policy

## Architecture
- Framework: Next.js 16 (App Router) on Cloudflare Workers via @opennextjs/cloudflare
- Styling: Tailwind CSS v4 — tokens in the `@theme` block of `src/app/globals.css` (Tailwind v4 has no `tailwind.config.ts`)
- DB: Neon Postgres via Drizzle ORM — schema in `src/db/schema/`
- Auth: Better-Auth — config in `src/lib/auth.ts`
- Validation: Zod schemas colocated with features in `src/features/[name]/schemas.ts`

## Next.js 16 — read the docs, not training data
APIs moved in 16 and most training data predates it. Before writing routing / cache / config code, read `node_modules/next/dist/docs/`:
- `middleware.ts` → `proxy.ts`, forced to the Node runtime (the `runtime` option throws if set; Edge is gone). It *does* run on OpenNext/Workers (Node — the adapter's default). But Next 16 calls proxy a last resort — do locale/redirect/auth-gate RSC-native (layouts + Route Handlers, per-Server-Function auth), not in `proxy.ts`.
- `params` / `searchParams` are async — `await params`.
- `experimental.ppr` → top-level `cacheComponents` (one flag controls ppr + useCache + dynamicIO). Not nested under `experimental`.

## UI
- Source of truth: DESIGN.md at project root (Google DESIGN.md format — YAML frontmatter tokens + 8 prose sections)
- If `/design-system` is installed (`npx skills add coroboros/agent-skills --skill design-system`): auto-activates on UI edits to enforce tokens; subcommands `audit` / `audit --strict` / `diff` / `export tailwind` / `migrate` / `init` / `audit-extensions`
- Otherwise validate directly with the installed project CLI: `pnpm design:audit`
- IMPORTANT: Read DESIGN.md BEFORE creating or modifying any component
- Tailwind utilities map to DESIGN.md tokens via the `@theme` block + CSS custom properties in `src/app/globals.css` (Tailwind v4 — no `tailwind.config.ts`)
- Component library: shadcn/ui (`src/components/ui/`) — NEVER install full UI frameworks

## Commands
```bash
pnpm dev              # Next.js dev server (Turbopack)
pnpm build            # next build (portable — Vercel / Node / self-host)
pnpm build:cf         # opennextjs-cloudflare build → .open-next/ (CF Workers artifact)
pnpm preview          # build:cf + local Workers preview (Miniflare)
pnpm deploy:cf        # opennextjs-cloudflare deploy (no build — pushes .open-next/ live)
pnpm upload:cf        # opennextjs-cloudflare upload (non-live version — branch previews)
pnpm ship             # build:cf + deploy:cf (local one-shot)
pnpm cf-typegen       # regenerate cloudflare-env.d.ts from wrangler bindings
pnpm db:push          # Push Drizzle schema
pnpm check            # biome check --write
pnpm typecheck        # tsc --noEmit
pnpm test             # Vitest
pnpm design:audit     # Validate DESIGN.md with the project-local canonical CLI
```

## Build & deploy on Cloudflare Workers
- **`:cf` script naming is deliberate.** `pnpm deploy` is a pnpm built-in (workspace deploy) that shadows a `deploy` script → `ERR_PNPM_NOTHING_TO_DEPLOY`. `deploy:cf` / `upload:cf` / `build:cf` dodge the built-in and stay symmetric.
- **`build` vs `build:cf` are separate.** `build` = plain `next build` (portability / Plan B). `build:cf` = the OpenNext transform that emits `.open-next/`. Deploy never rebuilds.
- **CF Workers Build (CI) is command-based**, no GitHub Actions: Build command `pnpm build:cf`, Deploy command `pnpm deploy:cf`, non-production deploy `pnpm upload:cf` (per-PR preview). CF auto-installs deps from `pnpm-lock.yaml` (no Install field).
- **`prebuild:cf` is the pnpm pre-hook for `build:cf`** — pnpm runs it automatically before `build:cf`. Put Cloudflare-only codegen that must precede the OpenNext build here (`cf-typegen`), kept off the portable `prebuild`/`build` path (Vercel / Node). Note: `opennextjs-cloudflare build` runs `pnpm run build` as a subprocess, so `prebuild` *also* fires inside `build:cf` — don't duplicate heavy codegen across both.
- **Build vars vs runtime secrets — triage, do not bulk-encrypt everything:**
  - `NEXT_PUBLIC_*` → **build-time, plain.** Next inlines them into the client bundle at `next build`; they reach the browser regardless. CF Workers Build dashboard (plain) or `wrangler.jsonc` `vars`.
  - Build-only tokens (e.g. a sourcemap-upload token) → **build var, not a runtime secret.** Used during `next build`, absent at request time.
  - True runtime secrets (DB URL, API keys) → `wrangler secret put NAME` (or `wrangler secret bulk .dev.vars`). Encrypted, request-time only.
- **Zone-level CF Rules, not wrangler:** `www.` → apex redirect and `http://` → `https://` upgrade are dashboard Rules. Bind the Worker to the apex only.
- **`wrangler` defaults to LOCAL Miniflare resources.** One-off ops against live R2/KV/D1 need `--remote` (e.g. `wrangler r2 object put <bucket>/<key> --file=<f> --remote`).

## Key decisions
- Feature-based colocation: `src/features/[name]/` groups components, actions, schemas, hooks
- Server Actions + Zod for mutations, NOT API routes (unless consumed by external clients)
- Default to Server Components — `use client` only when strictly required
- Images: R2 + custom subdomain + custom `next/image` loader → `/cdn-cgi/image/` (Image Transformations, NOT the Cloudflare Images product — see `.agents/rules/cloudflare-tooling.md` § Images)
- ISR: OpenNext R2 incremental cache + KV tag cache — bindings use OpenNext's hardcoded names (`NEXT_INC_CACHE_R2_BUCKET`, `NEXT_TAG_CACHE_KV`); wrong names fail silently (see `open-next.config.ts`)

## Environment
- `.dev.vars` for local Cloudflare bindings + secrets (gitignored)
- Regenerate types via `pnpm cf-typegen` after any binding change

## Testing
- Vitest for unit/integration, Playwright for E2E (`pnpm test:e2e`)
- Write a failing test before fixing a bug
