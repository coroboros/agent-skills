# Cloudflare Tooling

Two CLIs drive Cloudflare work on this project. Install globally if missing: `pnpm add -g wrangler cf`.

## Scope split

- `wrangler` — Workers-scoped. Reads `wrangler.jsonc`. Commands: `deploy`, `tail`, `dev`, `kv`, `r2`, `d1`, `secret`, `types`, `whoami`.
- `cf` — Platform-scoped, agent-optimized. Commands: `zones`, `dns`, `registrar`, `accounts`, `agent-context`, `schema`, `auth`.

Rule of thumb: **code → `wrangler`, infra/platform → `cf`**.

## Authentication

The user owns auth. Never attempt to authenticate on the user's behalf.

Suggest these interactive commands (prefix `! ` so the user's shell runs them in-session):

```
! wrangler login
! cf auth login
```

Verify:

```
! wrangler whoami
! cf accounts list
```

## Images

Two distinct Cloudflare products — pick the right one.

- **Image Transformations** (`/cdn-cgi/image/...`) — URL-driven transforms over any HTTP origin. **Default choice.** Pricing: 5K/mo free + $0.50/1K transformations. First hit per URL billable, edge-cached forever after.
- **Cloudflare Images** (the product) — premium UI + storage + delivery, separate billing. Costlier at our scale. **Avoid unless the user explicitly opts in** for the dashboard UX.

Pattern for R2-backed media:

1. Upload originals to R2 (e.g. `r2://MEDIA/listings/{uuid}/hero.jpg`).
2. Bind the bucket to a public custom domain via R2 → Public Access → Custom Domain (`cdn.<tld>`). $0 egress.
3. Serve transformed variants from the main domain via `next/image` + a custom loader hitting `/cdn-cgi/image/`.

```ts
// src/lib/cf-image-loader.ts
const ORIGIN = process.env.NEXT_PUBLIC_IMAGE_ORIGIN; // "https://cdn.<tld>"
export default function cfLoader({ src, width, quality }) {
  return `/cdn-cgi/image/width=${width},quality=${quality ?? 80},format=auto/${ORIGIN}${src}`;
}
```

Cache-Control on transformed URLs: `public, max-age=31536000, immutable` — width + quality in the URL make every variant a unique cache key.

## Destructive commands

Never run without explicit user confirmation:

- `wrangler delete`, `wrangler kv key delete`, `wrangler r2 object delete`, `wrangler d1 execute` with DDL
- `cf dns records delete`, `cf zones delete`, `cf registrar ... transfer`

Prefer read-only inspection first (`wrangler tail`, `cf dns records list`) before any mutation.
