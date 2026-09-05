# Cloudflare Tooling

Use the project's declared Wrangler dependency through `pnpm exec wrangler`. The optional `cf` CLI is for platform operations when installed and documented by the project; inspect its help before use. Do not install a second global Wrangler to bypass a missing project dependency.

## Scope

Wrangler reads `wrangler.jsonc` for Workers development, builds, bindings and deployment. Zone/DNS operations may require the platform CLI or API. Select the command for the requested resource and inspect its current help; local and remote flags vary by subcommand.

## Authentication

Reuse existing authorized credentials and inspect account identity before a write. If authentication is missing, explain the required interactive setup and let the user complete it. These are ordinary shell commands; Claude Code's optional `!` prefix is not required by other hosts:

```bash
pnpm exec wrangler whoami
pnpm exec wrangler login
```

For an installed `cf` CLI, consult `cf auth --help` for its supported login flow. Do not print tokens or switch accounts without authorization.

## Images

Choose image storage and transformation only when the brief needs them. Cloudflare Images, Image Transformations and R2 are distinct products; verify current limits, pricing, cache behavior and account configuration in the [official documentation](https://developers.cloudflare.com/images/) before activation. A scaffold does not provision public buckets, domains or paid products.

## Mutations

Inspect the exact resource first and preserve the user's approved scope. Destructive commands, publication, provider activation and credential changes require applicable authorization. A prior explicit approval for a named operation remains valid within that scope; unrelated destructive actions need a new decision. Local fixture validation does not authorize production writes.
