# Astro on Cloudflare — implementation notes

Read this before adjusting `astro.config.mjs` or the `wrangler.jsonc` for an `astro-cloudflare` scaffold. These are the non-obvious settings that trip up most Astro-on-Workers setups.

## `imageService: 'compile'`

Default for all Astro on Workers projects. Uses Sharp at build time to emit optimized WebP variants into `dist/client/_astro/`. Free tier compatible — no Cloudflare Images binding required.

Do NOT use `'cloudflare'` or `'cloudflare-binding'` unless the user has Cloudflare Images on their plan and explicitly asks.

## `assets.directory: "./dist/client"` (not `./dist`)

The Astro Cloudflare adapter splits output into:

- `dist/client/` — static assets (CSS, images, client JS)
- `dist/server/` — the Worker entry bundle

Pointing `assets.directory` at `./dist` would expose the server bundle as a public file.

## `main: "@astrojs/cloudflare/entrypoints/server"`

Canonical pre-build shim. Lets `wrangler deploy` and type-checking succeed before the build has produced `dist/server/entry.mjs`. Without it, a fresh clone + `wrangler deploy` fails because the entry file doesn't exist yet.

## Sharp

Comes transitively via Astro. Do NOT install it explicitly — duplicates the dependency tree and can cause version mismatches on Workers.
