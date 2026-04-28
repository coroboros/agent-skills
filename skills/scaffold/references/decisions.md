# Decisions Beyond the Scaffold

The scaffold ships an opinionated foundation (Next.js or Astro on Cloudflare Workers, pnpm, Biome, Tailwind, Drizzle + Better-Auth on `next-cloudflare`). The questions below are **not** answered by the scaffold — they vary too much project-to-project, and pre-coding them creates drift.

After the scaffold completes, surface the relevant ones to the user. Format per question: 2–4 canonical options + one trade-off line. No prescription.

## 1. Internationalization

**Multi-locale routing and translated content?**

- **Paraglide** (Inlang) — compile-time tree-shake, ~0.5 KB per route, JSON message files.
- **next-intl** — runtime, richer ICU formatting, larger bundle.
- **None** — single-locale shipping.

Trade-off: Paraglide scales with *used keys per route*; next-intl with *total messages*. Paraglide wins on edge bundle budgets; next-intl wins on dynamic message DX.

## 2. Dual auth (public + admin)

**Same auth surface for end-users and operators?**

- **Better-Auth (public) + Cloudflare Zero Trust (admin)** — public sessions in Better-Auth; `/admin/*` gated by ZT JWT (`Cf-Access-Jwt-Assertion`).
- **Better-Auth + role-based** — single provider, admin guarded by user role.
- **Auth.js / NextAuth** — broader provider catalog, heavier client.

Trade-off: ZT-for-admin removes custom session code on the operator surface (2FA, allow-list, 24h sessions handled by the CF dashboard, free up to 50 users).

## 3. Search

**Listings, posts, or document search?**

- **Postgres FTS + pg_trgm** — zero external service, native dictionaries (en/fr/de/...), trigram for languages without inter-word spaces (e.g. Thai). DB load grows with traffic.
- **Cloudflare Vectorize** — semantic ranking, separate billing, async indexing.
- **Algolia / Typesense** — managed, fast, expensive at scale.

Trade-off: an `adapter.ts` interface keeps the swap cheap. Start with FTS, escalate to Vectorize on language-quality complaints or semantic-ranking demand.

## 4. Rich text (admin)

**Editor for editorial / CMS content?**

- **TipTap** — ProseMirror-based, JSON storage, code-split admin only.
- **Lexical** — Meta's, performant, smaller community.
- **Plate** — Slate-based, plugin ecosystem, heavier.

Trade-off: store JSON in `jsonb`. Render server-side via `@tiptap/html` (or equivalent) through a `sanitize-html` allowlist. Never render raw user HTML.

## 5. OG image generation

**Strategy for `og:image` previews?**

- **Eager-on-publish** — Server Action fires `after()` → Satori SVG → ResvG to PNG (1200×630) → R2 cache per locale.
- **On-demand route handler** — `/og/.../route.tsx` renders lazily, ~1.5s first hit.
- **Static** — designer hand-export per page.

Trade-off: social platforms scrape within minutes of publish. Lazy Satori = ~1.5s first hit = broken preview window. Eager covers it; on-demand is a fine fallback for legacy / cache eviction.

## 6. Machine translation (admin)

**Auto-fill translations for editorial content?**

- **DeepL API** — best EN ↔ FR / DE / ES quality, paid.
- **Google Translate** — broader language coverage, lower quality on nuance.
- **None** — manual translation only.

Trade-off: never publish unreviewed MT. Gate via a state machine (`draft` → `translated` → `reviewed` → `published`) in admin.

## 7. Theme persistence (light / dark)

**SSR-correct dark mode with no flash?**

- **Cookie + localStorage + `<html data-theme>` SSR'd** — read cookie in middleware / `proxy.ts`, render `<html data-theme="...">` server-side, mirror in `localStorage` client-side.
- **Client-only with FOUC** — flash of wrong theme on first paint.
- **No toggle** — `prefers-color-scheme` only.

Trade-off: SSR'd attribute avoids the flash and stays compatible with cached HTML. The same pattern works for currency and locale.

## 8. Cache invalidation

**Strategy for revalidating cached pages on mutation?**

- **`revalidateTag` per mutation** — tag `listing:{id}`, `listings:list:{locale}`, `home:featured`; mutate → revalidate affected tags.
- **Full purge** — invalidate everything on any write.
- **TTL only** — let entries expire naturally.

Trade-off: tagged invalidation hits the best precision/perf compromise. Failures should log to `audit_log` and not block the write.

## 9. Admin image upload

**Upload path for media?**

- **Signed R2 URL direct** — admin requests `/api/admin/upload-url` (short expiry, content-type + size enforced) → client `PUT` to R2 directly.
- **Stream via Worker** — file flows through the Worker, then `R2.put`.
- **Client-side resize + signed PUT** — pre-process before upload.

Trade-off: signed-URL-direct bypasses Worker CPU and streaming limits — mandatory past a few MB. Variants generated on-demand via `/cdn-cgi/image/`, edge-cached forever.

## 10. CRM sync

**Lead distribution to a sales tool?**

- **Webhook fire-and-forget via `after()` + retry queue** — store lead in DB (source of truth), spawn `after()`, retry on failure with exponential backoff.
- **Direct synchronous** — block the lead form on CRM success.
- **Batch nightly** — cron sync, lower freshness.

Trade-off: fire-and-forget keeps the form fast and resilient to CRM outages. Persist `crm_sync_status` in the DB and surface failures in admin for manual retry.
