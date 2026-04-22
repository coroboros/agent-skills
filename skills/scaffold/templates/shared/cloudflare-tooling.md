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

## Destructive commands

Never run without explicit user confirmation:

- `wrangler delete`, `wrangler kv key delete`, `wrangler r2 object delete`, `wrangler d1 execute` with DDL
- `cf dns records delete`, `cf zones delete`, `cf registrar ... transfer`

Prefer read-only inspection first (`wrangler tail`, `cf dns records list`) before any mutation.
