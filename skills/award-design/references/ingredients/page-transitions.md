# Page Transitions

The choreography over the URL change — distinct from the intro loader (`preloaders.md`) and in-page scroll reveals. Fifteen multi-page winners read live: every route transition is JS-orchestrated; zero ship the native View Transitions API as their signature. Router split: Taxi ×3 · Barba ×2 · Nuxt ×4 · Next ×3 · custom SPA ×3. Load at Phase 3/4 with `preloaders.md` — the two commit as one arrival language.

Tags as in `preloaders.md`; (grounded) = re-checked against library docs, MDN, web.dev — not memory.

## Transition forms — beat tables

### 1. Curtain / cover — Cuberto, Terminal, Truekind (winner-verified)

The panel is the page's own arrival color, never a neutral grey; z-index a decisive 998–999.

| Beat | What shows · value |
|---|---|
| rest | fixed full-viewport panel, hidden — Terminal `opacity:0; visibility:hidden; overflow:clip`; Truekind white sheet `pointer-events:none` |
| cover | panel in — opacity→1, JS/GSAP; Cuberto dims a backdrop under its white fill |
| swap | route DOM replaced behind the panel |
| uncover | panel out — opacity→0, hidden again |

### 2. Shared-element morph — Truekind (winner-verified)

The clicked thumbnail becomes the next page's hero: a clone in a fixed layer (`.clone-transition`, `data-flip-id="fullscreen"` — **GSAP Flip's signature attribute**) animates its box to fullscreen (`.is--cloned`) while the page swaps beneath; the white sheet covers the seam.

### 3. Asymmetric cross-fade — Immersive Garden, Nuxt (winner-verified)

| Beat | Value |
|---|---|
| leave | `transition:opacity 0s linear` — the outgoing page vanishes instantly |
| enter | `transition:opacity .7s cubic-bezier(.445,.05,.55,.95)` from `opacity:0` — the entrance gets the whole budget |
| overlap | successive pages `position:absolute; inset:0; transition-delay:.4s` — stacked during the dissolve |

A symmetric 0.3s fade-both is the AI default the winner out-designs.

### 4. Wipe-with-wordmark — Mat Voyce (winner-verified), Dennis (observed)

The panel is a designed screen naming the **destination**: Mat Voyce's fixed `#bcf3ff` layer wipes open via an animated `mask-image` gradient, carrying a giant variable-font heading (`min(16.66vh,9.375vw)`, weight 1000) and a looping texture. Dennis renders the project title per Barba namespace.

### 5. Router-managed custom (winner-verified)

The plumbing under forms 1/4 — a PJAX router hands the timeline to GSAP or Rive: Siena's Taxi `onLeave({from,done})` awaits `transitionOut` before `done()`; Lando swaps `data-taxi-view` under a Rive overlay; Locomotive and Dennis run Barba + Locomotive Scroll.

### 6. Persistent-canvas morph — Active Theory (winner-verified live)

No DOM to swap: one canvas renders every page; a nav click morphs the WebGL scene ~1s while the History API updates the URL mid-morph; `history.back()` reverses the scene — same canvas node, no reload.

A deliberate **hard cut** appears in zero winners — anti-signal only.

## Tech paths — what each costs

**A. PJAX routers — Taxi.js, Barba.js (the award default).** Intercept clicks, fetch real HTML, swap a marked container (`data-taxi-view` / `data-barba="container"`), run the JS transition. Taxi.js (`@unseenco/taxi`) is the maintained Highway.js replacement — never reach for Highway (grounded). Back-button works (History API); SSR-friendly — real server HTML per route. **Scroll restoration is the pain point**: default `history.scrollRestoration` `"auto"` fights the transition — set `"manual"` and restore by hand (grounded — MDN; Barba #423/#133).

**B. Framework-native — Nuxt `<Transition>`, Next client components.** Nuxt drives routes through named CSS transition classes (Immersive Garden, Terminal, Truekind, Ponpon); Next winners hand-build the overlay (Mat Voyce). Costs hydration and a JS-owned scroll; the router fires the transition in both directions, so back works.

**C. Native View Transitions API — the verified absence.** Zero of 15 winners ship `@view-transition` or `document.startViewTransition()` as their route transition (winner-verified negative). Baseline as verified: same-document = **Baseline Newly available** (2025-10, Firefox 144 completed the set); cross-document = **not Baseline** (no Firefox) as of mid-2026. Its default cross-fade is what this tier out-designs. Legitimate award use: the editorial thumbnail→hero `view-transition-name` morph as the progressive-enhancement floor — never the signature.

## The loader-coherence rule

**One arrival language per site — the route transition rhymes with the loader family.** Winner-verified wherever a site ships both (Cuberto's reuse single-source):

- Terminal — intro loader and route overlay are the same primitive: both fixed, full-viewport, `z-index:999`.
- Truekind — preloader, base overlay, and clone layer are one white arrival family.
- Immersive Garden — loader and transitions share one ease family (`.445,.05,.55,.95`).
- Cuberto — one white curtain serves intro and route.

The build rule: whatever the loader's gesture — a fill, a wipe, a color, an ease — the route transition uses the same gesture. Arriving on a curtain then cross-fading between routes speaks two arrival languages — the tell this rule closes.

## MPA / SPA notes

- **MPA continuity** = what survives the swap: the persistent parent (`data-taxi` / `data-barba="wrapper"`) keeps nav, scroll shell, canvas, audio mounted through the swap. Real HTML per route keeps SSR/SEO; scroll restoration is yours to wire.
- **SPA back-button** — drive the transition off the router's navigation event (it fires on popstate too), never the click handler alone; a click-wired transition animates forward and blanks on back.
- **Focus and pointer-events** — the cover goes `pointer-events:none` once it stops masking (Terminal, Mat Voyce — winner-verified); focus moves to the new page's top.
- **Reduced motion** — under `prefers-reduced-motion: reduce` the transition collapses to an instant swap or a ≤150ms opacity, never a 1s wipe.

## Archetype-fit map

| Archetype | Route form — record |
|---|---|
| Minimalist | quiet cover in the page ground or asymmetric fade, ≤500ms — Terminal, Gabriel |
| Editorial | cross-fade or named wipe; Flip morph for thumbnail→hero — Siena, Truekind |
| Corporate-luxury | slow asymmetric fade, one ease family — Immersive Garden |
| Bold / maximal | wipe-with-wordmark in the display face — Mat Voyce; Ponpon (narrative) |
| Immersive / cinematic | persistent-canvas morph, or Taxi + Rive overlay — Active Theory, Lando |
| Experimental | bespoke — the route obeys the world's physics, real URL underneath — Eloy |
| Brutalist | near-cut, deliberately un-eased — on-brand here only (skill reference) |
| Bento / card | none / instant; the layout is the continuity (skill reference) |
| Spatial-organic | soft cross-fade or depth morph in the depth-and-blur register |

## Anti-signals

1. **A hard cut on a site that choreographs everything else** — breaks its own contract; only Brutalist earns a near-cut.
2. **A blocking wipe ≥1.5s on every click** — a tax on every navigation; budget the entrance, keep the exit cheap.
3. **Broken scroll restoration** — a PJAX router left on `"auto"` lands the reader wrong on back/forward. The PJAX tell.
4. **Broken back-button** — a click-wired transition that blanks on popstate; wire the navigation event.
5. **Focus trapped behind the cover** — the panel stays interactive after masking; go `pointer-events:none` and move focus.
6. **A transition that does not rhyme with the loader** — two arrival languages on one site.
7. **Cross-document View Transitions as the signature** — not Baseline; PE floor only.
8. **A wordmark wipe naming the site, not the destination** — a logo card on every click says nothing.

## Cross-references

- `preloaders.md` — the arrival sibling; commit loader and transition as one language.
- `../motion-palette.md` — Physics of motion times the beats; its View-Transition morph row is the PE-floor technique.
- `../modern-web-baseline.md` — Baseline status for View Transitions.
