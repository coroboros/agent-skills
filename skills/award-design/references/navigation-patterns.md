# Navigation Patterns

The canonical implementation behind `award-imperatives.md` #2. The imperative states the *rule* — a real nav that hides on scroll-down and returns on scroll-up, or a full-screen overlay that is itself an editorial moment. This file is the *proven pattern* for the show-on-scroll-up header, so the build reproduces award-grade behavior instead of re-deriving it (and re-shipping a fixed, always-visible hero-anchor bar — the tell this closes).

Load when the design_plan commits a scroll-aware header. A full-screen overlay menu is the alternative register (see the archetype table at the bottom); the two are not mixed on one build.

## The one idea: two orthogonal axes, never conflated

A show-on-scroll-up header runs **two independent state machines** off the same scroll, each writing its own attribute, each owning a different concern:

- **Visibility** (headroom) — is the bar on screen or slid away? Driven by scroll *direction*.
- **Surface** (paint) — is the bar transparent over the hero or solid over content? Driven by scroll *position* relative to the hero.

Conflating them is the common failure: a bar that only solidifies when it hides, or reappears transparent over content. Keep them decoupled — a `data-nav-hidden` attribute and a `data-nav-surface` attribute, resolved separately, composed in CSS.

## Visibility — the headroom state machine

Fixed-position bar. One `passive`, rAF-coalesced scroll handler; **direction from an accumulator, never a raw delta.** Four cases, in order:

1. `scrollY ≤ TOP_GUARD` → **shown**, reset both accumulators. A band at the top of every page where the nav is always present — the user never has to scroll up to find it on arrival.
2. Scrolling **down** past the guard → reset the up-accumulator, add to the down-accumulator; **hide** once cumulative down-travel exceeds `HIDE_TOL`. Accumulate across frames rather than testing the instantaneous delta, so a slow drift still eventually hides and a one-frame jitter does not.
3. Scrolling **up** → reset the down-accumulator, add to the up-accumulator; **show** once cumulative up-travel exceeds `SHOW_TOL`. Symmetric to the hide: a genuine upward intent shows the bar; a sub-pixel wobble does not.
4. **`dy == 0` — a scroll-stop or a smooth-scroll settle frame → hold the current state**, change nothing. This is the case the naive `else { show }` gets wrong (gotcha 5): treating "stopped" as "up" flashes the bar back every time the scroll comes to rest.

Defaults that read well: `TOP_GUARD = 64px`, `HIDE_TOL = 8px`, `SHOW_TOL = 8px`. Expose them as CSS custom properties so the values live in one place.

**Hidden = `translateY(-100%)`, shown = `translateY(0)`.** Transform and paint only — never animate `height` / `top` / `display`, which trigger layout and cost you CLS. Transition ~300–400ms on a decelerating ease (`cubic-bezier(0.16, 1, 0.3, 1)`), matching the imperative's window.

## Surface — the hero crossing

Transparent over the hero (light text, a top scrim for legibility over bright imagery); solid past it (owned background, dark text, an `@supports`-gated `backdrop-filter`).

**The owned background is the page ground (or the dominant primary) — and the bar hangs no hairline.** The solid surface reuses the exact token the page stands on (`--bg` / `--ground`) or the declared dominant primary, so a solid bar melts into the page it serves — on a white site the bar goes white. A neutral one step off the ground (`--ground-2`, a grey nobody chose over a white page) reads as a grey strip stuck onto the design, not a surface. And the bar never takes a `border-bottom` — in the hairline color or any other — as its separation affordance, at rest, on scroll, or on hover: the opaque ground itself is the separation, plus the register's declared shadow when one exists. A different-colored line lighting up under the bar on hover is the same class of tell as the AI-nav fingerprint's divider (`anti-patterns.md` Layout).

A solid bar carrying `backdrop-filter` stutters on iOS Safari during scroll — the OS re-samples the moving backdrop each frame its toolbar repositions the fixed bar. Scroll-gate it: set a `data-scrolling` flag on `<html>` while a scroll is in flight (clear it on the exact `scrollend` event, with a ~140ms debounce fallback for browsers without it) and drop the blur to a flat fill mid-scroll, easing it back at rest — `:root[data-scrolling] [data-nav-surface="solid"] { backdrop-filter: none }`.

Detect the crossing with a **zero-size sentinel at the hero's bottom edge**, not a `scrollY` threshold. Measure the sentinel's distance to the viewport top against the bar height. This is resolution-independent — it works with a fluid `dvh` hero whose pixel height you don't know at author time, where a hard-coded `scrollY > 700` silently breaks. Solidify the bar when the sentinel reaches one bar-height from the top (the bar goes solid the instant it would otherwise straddle the hero/content seam, so light text never lands on content); drop the legibility scrim one bar-height deeper. A page with no hero forces the solid state and mounts no observer.

### Surface on hover — legibility-on-demand (default)

By default, **the bar takes its solid surface the instant the pointer enters it (or it gains focus, or a touch lands), and drops back to transparent on leave** — even over the hero. Hovering or tapping the nav is intent to read it; giving it its owned background on that intent guarantees legibility over any hero imagery and doubles as the nav's own substrate response (an inert bar on hover is a dead element). Gate it like the scroll surface, OR'd with a hover/focus-within state:

```css
[data-nav]:hover, [data-nav]:focus-within { background: var(--surface); color: var(--on-surface); }
```

`--surface` obeys the rule above — the page ground or the dominant primary, never a derived neutral, and no `border-bottom` comes with it.

The one exception is a bar **declared always-solid** in the DESIGN.md (a register that never runs transparent over the hero): there the surface is permanent and the hover rule is a no-op. A bar that stays transparent while the pointer sits on it — forcing the reader to squint at light-on-light links — is the tell this closes.

## The wordmark is the home affordance — and it never writes `#top` into the URL

Every click on the wordmark resolves by state: elsewhere on the site → navigate to the homepage; on the homepage mid-scroll → **smooth scroll to top by script** (`window.scrollTo({ top: 0, behavior: "smooth" })`, or the smooth-scroll layer's own `scrollTo`), never an `href="#top"` anchor — a fragment appearing in the address bar on a chrome click reads unfinished, not pro; already at the top of the homepage → reload the page. Implement as a link to `/` (the semantic home URL for middle-click, SEO, and no-JS) whose click handler intercepts on the homepage to scroll or reload. The footer's back-to-top follows the same discipline: script scroll, no fragment.

## The five things a competent version misses

These are what separate an award header from a working one — each is a real defect the naive version ships.

1. **SSR / first-paint is already the correct surface.** Emit the initial `transparent` / `solid` state server-side (or inline before first paint) so there is no transparent→solid flash on load, and none on a mid-hero deep-link. A client-only observer paints transparent for a frame on every load — a visible flicker judges read as jank.
2. **Freeze-revealed on interaction and focus.** Pin the bar shown whenever a drawer / menu / lightbox / modal is open, and whenever the bar contains `:focus-visible` (`:has(:focus-visible)`, or the JS equivalent). Focus must never land behind a hidden bar — a keyboard user tabbing into a slid-away nav is a **WCAG 2.4.11** failure; tabbing in must reveal it.
3. **Reduced motion flips the state instantly — it does not disable the behavior.** Under `prefers-reduced-motion: reduce`, keep the full machine, strip only the transitions. The bar still hides, shows, and swaps surface; it just snaps. Removing the behavior entirely strands the nav or leaves it always-on; the imperative still holds.
4. **JS writes state, CSS owns motion.** The script only toggles data-attributes; every transform, color, and opacity transition lives in CSS. Coalesce reads with `requestAnimationFrame` (one measurement per frame, a guard against double-scheduling) rather than a throttle, and dirty-check — write the attribute only when the resolved state actually changes, so CSS transitions do not retrigger every frame. This keeps the logic testable and the work off the main thread. `window.addEventListener('scroll')` writing `style.transform` on every event is the anti-pattern (`anti-patterns.md` Technical).
5. **A scroll-stop is not a scroll-up.** Under a smooth-scroll layer (Lenis, ScrollTrigger), the `scroll` event keeps firing as inertia settles — the final frames carry `dy == 0` or a sub-pixel easing overshoot to negative. A handler that shows on *any* `dy ≤ 0` (the naive `else { show }`) reads every settle as an upward intent and flashes the bar back the instant the scroll comes to rest. Gate the show on an accumulated up-travel past `SHOW_TOL`, and let `dy == 0` hold the current state. Native scroll sidesteps this — it fires no event at rest, so the bar simply holds — which is why a build reading native `scrollY` can show on any `dy < 0`, but one reading from a smooth-scroll layer must carry the up-accumulator. The whole hide/show mechanic needs no library; native `scrollY` is enough.

Uniform across breakpoints: one threshold set for mobile and desktop, the visibility logic never special-cases hero vs content. Only the bar height (desktop under 10% of viewport, mobile under 60px) and its inner content differ by width — desktop carries the full link set; below ~1024px it collapses to a wordmark plus a menu trigger, the links moving into the overlay/drawer.

## Minimal reference — vanilla, any stack adapts

```js
// visibility — headroom (direction from accumulators; dy==0 holds state)
const bar = document.querySelector('[data-nav]');
const css = getComputedStyle(document.documentElement);
const TOP_GUARD = parseFloat(css.getPropertyValue('--nav-top-guard')) || 64;
const HIDE_TOL  = parseFloat(css.getPropertyValue('--nav-hide-tol')) || 8;
const SHOW_TOL  = parseFloat(css.getPropertyValue('--nav-show-tol')) || 8;
let lastY = scrollY, downAcc = 0, upAcc = 0, ticking = false;
function onScroll() {
  if (ticking) return;
  ticking = true;
  requestAnimationFrame(() => {
    const y = scrollY, dy = y - lastY;
    let hidden = bar.dataset.navHidden === 'true';                  // default: hold
    if (y <= TOP_GUARD) { downAcc = upAcc = 0; hidden = false; }
    else if (dy > 0)    { upAcc = 0; downAcc += dy; if (downAcc > HIDE_TOL) hidden = true; }
    else if (dy < 0)    { downAcc = 0; upAcc -= dy; if (upAcc > SHOW_TOL) hidden = false; }
    // dy === 0 (scroll-stop / smooth-scroll settle frame) falls through: `hidden` unchanged
    const next = String(hidden);
    if (bar.dataset.navHidden !== next) bar.dataset.navHidden = next; // dirty-check
    lastY = y; ticking = false;
  });
}
// Native scroll fires no event at rest, so dy==0 rarely occurs on it. A smooth-scroll layer
// (Lenis, ScrollTrigger) fires on every settle frame — read from it AND keep the dy==0 hold,
// or the bar flashes shown at the end of every downward flick (gotcha 5).
if (window.lenis) window.lenis.on('scroll', onScroll);
else addEventListener('scroll', onScroll, { passive: true });

// surface — hero crossing (sentinel is a 1px marker at the hero's bottom edge)
const sentinel = document.querySelector('[data-hero-sentinel]');
if (sentinel) {
  let last = '';
  addEventListener('scroll', () => requestAnimationFrame(() => {
    const solid = sentinel.getBoundingClientRect().top <= bar.offsetHeight ? 'solid' : 'transparent';
    if (solid !== last) { bar.dataset.navSurface = solid; last = solid; }
  }), { passive: true });
}
```

```css
[data-nav] { position: fixed; inset: 0 0 auto; transition: transform .36s cubic-bezier(.16,1,.3,1); }
[data-nav][data-nav-hidden="true"] { transform: translateY(-100%); }
[data-nav]:has(:focus-visible), [data-nav][data-menu-open] { transform: translateY(0); } /* freeze revealed */
[data-nav][data-nav-surface="transparent"] { background: transparent; color: var(--on-hero); }
/* --surface = the page ground or the dominant primary — never a derived grey, never a border-bottom */
[data-nav][data-nav-surface="solid"] { background: var(--surface); color: var(--on-surface); }
@supports (backdrop-filter: blur(1px)) {
  [data-nav][data-nav-surface="solid"] { backdrop-filter: blur(20px) saturate(1.1); }
}
@media (prefers-reduced-motion: reduce) { [data-nav] { transition: none; } } /* state still flips */
```

React / framework builds: keep the same shape — a hook writes the two attributes off a coalesced scroll read, the component renders them, and the transitions stay in CSS. Do not drive `translateY` through React state (a re-render per frame); write the attribute and let CSS animate. If a heavy layer already owns scroll (Lenis, ScrollTrigger), read position from it rather than adding a second listener.

## The overlay alternative, and per-archetype fit

The full-screen overlay menu is the other rewarded pattern — mandatory when the archetype's register calls for it (Bold/Maximal, Experimental) and legitimate anywhere the menu itself becomes an editorial moment: 60–120px type, a staggered reveal (50–100ms per item), a `clip-path` or transform wipe, hover-preview of the destination where it earns it. It composes *with* the scroll-aware bar (the trigger lives in the headroom bar) rather than replacing it.

**The drawer floor and the scene ceiling — split, never conflated.** The **floor is universal**: any collapsed drawer or overlay is never a dead list — every link answers in the page's substrate vocabulary (a link with no state is a dead element on the site's most theatrical click), the open is staggered, and the focus machinery (trap, `inert` siblings, `Esc`-to-trigger) is intact. The floor is mechanically checkable: the detector runs with the drawer OPEN, so its links join the substrate census and the UNMEASURED accounting — a rest-state run misses them by design (`references/detector.md`). The **ceiling is archetype-conditional**: the full scene — per-link bespoke mechanics, an ambient touch living inside the overlay, the open staged as an event — binds where the register stages it (Bold/Maximal, Experimental, the editorial dual-menu) and calibrates to the Motion dial elsewhere; a utility drawer on a scan-and-click register stays fast and scannable. "A spectacular drawer, always" over-produces the quiet registers — the floor is the always; the scene is the register's call.

**The toggle is icon-only, and the close lands under the pointer that opened it.** Hamburger and cross carry no visible text label — no "MENU" beside the burger, no "CLOSE" beside the `✕`; the words live in `aria-label="Open menu"` / `aria-label="Close menu"`, never on screen. The two states are one control at one point: the cross renders exactly where the hamburger was — same button, morphed or swapped in place with a real transition — so the click that opens leaves the pointer already on the close. A `✕` that appears across the viewport from the trigger forces a pointer hunt and reads as two unrelated controls. The toggle keeps the page's substrate response (a hover/tap effect like any control), AA contrast, a ≥44px hit-area. `Esc` closes it, focus returns to the trigger (WCAG 2.4.3), and body scroll locks while it is open. Verify by opening and closing it in the browser without moving the mouse — the second click must land on the cross.

The archetype default is the show-on-scroll-up header unless the register says otherwise (`award-imperatives.md` per-archetype table): Corporate Luxury and Minimalist run a quiet scroll-aware bar; Editorial a scroll-aware header or a dual-menu editorial nav; Bold/Maximal an overlay staged as an event; Immersive a minimal HUD-like bar or overlay; Experimental makes the bespoke navigation metaphor the signature itself, with a conventional escape hatch. Whichever register, the axes above still hold — a nav that never hides, or reappears transparent over content, is the tell regardless of flavor.
