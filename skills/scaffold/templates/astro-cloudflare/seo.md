# SEO Requirements

- Every page MUST have: unique `<title>`, meta description, canonical URL.
- Structured data (JSON-LD) on every content page — schema type depends on content.
- Open Graph + Twitter Card meta on every page.
- `sitemap.xml` generated via `@astrojs/sitemap` (static routes only — SSR routes need a custom sitemap endpoint).
- `robots.txt` at root.

## Performance budget (Core Web Vitals)
- LCP < 1.5s
- CLS < 0.05
- INP < 100ms
- TBT < 100ms (lab proxy for INP)
