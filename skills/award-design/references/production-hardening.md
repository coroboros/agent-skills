# Production Hardening

Battle-tested patterns for shipping immersive web design to real devices, distilled from production incidents — not lab testing. Load this when implementing any project with video, scroll-driven cinematic reveals, or full-screen heroes.

**Scope note.** Most of the patterns here apply cross-browser (Chrome, Firefox, Safari on desktop; Chrome, Firefox, Safari on mobile). iOS Safari is the *sharpest test case* — it exposes these bugs first and hardest because of its strictest autoplay policy, aggressive bfcache restoration, synthetic scroll events during URL-bar settling, and layout timing quirks. **Passing iOS means passing everything else.** Each section below flags where a rule is genuinely iOS-only vs. where iOS is just the canary.

## Contents

- [Viewport units — svh / dvh / lvh / vh](#viewport-units)
- [Reading svh from JS — the clientHeight = 0 trap](#reading-svh-from-js)
- [Cross-browser video autoplay](#cross-browser-video-autoplay)
- [Scroll-driven cinematic sequences](#scroll-driven-cinematic-sequences)
- [Fail-safe reveal logic](#fail-safe-reveal-logic)
- [Proportional layout vs breakpoint jumps](#proportional-layout)
- [Mobile browser quirks cheat-sheet](#mobile-browser-quirks)
- [Real-device test workflow](#real-device-test-workflow)

## Tokenization

Code samples in this file use literal values (durations, opacities, viewport units, scroll offsets) for clarity. In production, these MUST bind to DESIGN.md token namespaces — `motion.duration-*` for durations, `motion.ease-*` for easings, `opacity.*` for overlays, `heights.*` for viewport heights, `scrollTriggers.*` for fold offsets. Consume them as CSS custom properties (`var(--duration-reveal-slow)`) or Tailwind v4 utilities (`duration-reveal-slow`). Magic numbers in JS (`SPACER_MULTIPLIER`, scroll thresholds) read the corresponding `var(--scroll-*)` at startup, never hardcode. Full convention: `skills/design-system/references/extended-tokens.md`. Validate with `/design-system audit-extensions DESIGN.md`.

## Viewport units

**Scope:** all mobile browsers (iOS Safari, Chrome Android, Firefox Mobile all have animated URL bars that change the visual viewport). Universal CSS concern.

Every award-design hero uses viewport-relative heights. Picking the wrong unit is the single most common source of mobile jitter, content-below-fold, and scroll-reveal desync.

| Unit | What it is | Behavior on mobile URL-bar toggle |
|------|------------|-----------------------------------|
| `vh`  | Legacy. In most mobile browsers = `lvh` (largest) | Constant but too tall when bar shown → content clipped |
| `svh` | 1% of **smallest** viewport (URL bar expanded) | **Constant** — never changes |
| `lvh` | 1% of **largest** viewport (URL bar collapsed) | **Constant** — never changes |
| `dvh` | 1% of **current** viewport | **Changes** as the bar animates in/out |

**Rules:**

- **Scroll-driven elements → `svh`.** Anything whose height feeds `scrollY` math (scroll spacers, pinned sections, fold triggers) must be stable. `svh` guarantees `document.scrollHeight` does not mutate when the bar toggles.
- **Fixed-position full-screen containers → `dvh`.** A `position: fixed` hero with `h-dvh` smoothly tracks the visible area, so footer/CTA spacing stays constant whether the bar is up or down.
- **Centered must-see-now content → `svh`.** Hero text, CTA, logo. Using `svh` guarantees it always fits the smallest viewport.

**Never mix units on elements that relate to each other** (spacer in `dvh` + JS reading `svh` from `innerHeight`). Pick one reference per relationship.

**Never use `vh` in new code** — ambiguous and always wrong on iOS.

**CSS fallback:**

```css
.hero { height: 100vh; }
@supports (height: 100svh) { .hero { height: 100svh; } }
```

## Reading svh from JS

**Scope:** mobile (iOS most aggressive; Chrome Android varies less but `innerHeight` still fluctuates). The defensive guard pattern is universally good code.

JS needs svh in pixels for scroll math. Two traps:

1. `window.innerHeight` varies with URL bar on all mobile browsers — not stable as a reference
2. `clientHeight` of an svh-sized box **occasionally returns `0` on iOS Safari first script tick**, before layout stabilizes. A `0` propagates: `startPx = range.start * svh` collapses all thresholds to 0, every reveal falls through to fully-composed branch, paints on top of hero.

**Rule:** guard with fallback + re-measure in `rAF` + `load` + `resize`.

```js
function measureSvh() {
  const h = spacer?.clientHeight ?? 0;
  if (h > 0 && Number.isFinite(h)) return h / SPACER_MULTIPLIER; // e.g. 3 if spacer is height: 300svh
  return window.innerHeight || 1;
}

let svh = measureSvh();
requestAnimationFrame(() => { svh = measureSvh(); update(); });
window.addEventListener('load', () => { svh = measureSvh(); update(); }, { once: true });
window.addEventListener('resize', () => { svh = measureSvh(); update(); }, { passive: true });
```

Never let a corrupt svh (`0` or `NaN`) reach reveal math — see [Fail-safe reveal logic](#fail-safe-reveal-logic).

## Cross-browser video autoplay

**Scope:** truly cross-browser. Chrome and Firefox also block autoplay in data-saver / low-battery / strict-privacy modes; iOS Safari is just the strictest default. `playsinline` is iOS-specific (harmless elsewhere); MP4-before-WebM is Safari-wide (desktop + iOS); `disableRemotePlayback` is a desktop Safari fix. Belt-and-suspenders works everywhere.

Autoplay policy diverges across engines. HTML attributes alone are not enough.

### HTML — all attributes, every time

```html
<video
  autoplay muted loop
  playsinline webkit-playsinline
  disableRemotePlayback
  preload="auto"
  poster="/videos/poster.jpg"
>
  <source src="/videos/dunes.mp4" type="video/mp4" />
  <source src="/videos/dunes.webm" type="video/webm" />
</video>
```

- `muted` + `playsinline` = minimum for iOS autoplay
- `webkit-playsinline` = legacy iOS attribute, harmless elsewhere
- `disableRemotePlayback` stops AirPlay/Cast picker on hover (desktop Safari)
- `preload="auto"` ensures enough buffer for the `play()` promise to resolve

### Source order — MP4 first, WebM second

Safari only plays MP4. Browsers pick the first supported source. WebM first means Safari never looks at the MP4.

### JS — harden autoplay

HTML `muted` can be overridden by extensions, user settings, or lost across page navigations; most unreliable on iOS but not iOS-only. Re-assert from script, then call `play()` explicitly:

```js
const video = document.getElementById('bg-video');
video.muted = true;
video.defaultMuted = true;

const tryPlay = () => video.play().catch(() => {});

if (video.readyState >= 2) {
  tryPlay();
} else {
  video.addEventListener('loadeddata', tryPlay, { once: true });
  video.addEventListener('canplay', tryPlay, { once: true });
}
```

Catch the `play()` promise silently. If the browser refuses (Low Power Mode, data-saver, strict policy), the poster is the graceful fallback — never throw.

### File size

Hero video < 5 MB, ideally < 3 MB. `ffmpeg -crf 28 -preset slow`. Loop 8–15s. Longer = bandwidth for frames nobody watches.

## Scroll-driven cinematic sequences

**Scope:** mixed — see per-rule scope below. The *patterns* (threshold crossings, cancellable glides, custom smooth scroll) are universal. The *triggers* that expose the bugs are mobile-dominant, with iOS Safari as the sharpest case.

Trivial on desktop, minefield on mobile. iOS fires spurious `scroll` events during URL-bar settling and rubber-band bounces — with zero touch/wheel input.

### The synthetic-event trap

**Scope:** primarily iOS Safari (most aggressive). Chrome Android can fire stray scroll events during URL-bar animation too, but less frequently. `history.scrollRestoration = 'auto'` is the default in **all major browsers** (Chrome, Firefox, Safari) — the scroll-restoration bug is fully cross-browser, not iOS-specific.

On page load:

- iOS emits `scroll` events while the URL bar animates — no user input (Android Chrome does this milder)
- iOS can fire a stray `touchmove` from tap-to-open, edge-swipe-back, or a finger brush (Android rarer)
- **All browsers** restore previous `scrollY` by default (`history.scrollRestoration = 'auto'`) — lands the user mid-animation on reload. Chrome and Firefox bfcache also preserves this state across back-navigation, not only iOS

Any of these triggers a naive "auto-scroll to end" before the user has intentionally scrolled.

### Rule 1 — kill scroll restoration first

**Scope:** universal — default `'auto'` in Chrome, Firefox, Safari. bfcache preserves scroll+animation state in all three engines since ~2022.

Before any cinematic logic:

```js
if ('scrollRestoration' in history) history.scrollRestoration = 'manual';
window.scrollTo(0, 0);
```

**Why:** without this, a user who previously scrolled past reveal ranges lands on reload with `scrollY` already there — every reveal computes into the fully-revealed branch at opacity 1, stacked on top of the still-full hero. The first scroll "fixes" it, which is how the bug first shows up.

**How to apply:** also matters for bfcache (navigate back from external link → any modern browser restores with `scrollY` + inline styles preserved). Explains the classic *"works on local preview, broken on production"* — localhost has no scroll history, production does. The symptom appears on **any** browser with history; iOS surfaces it most often because iOS users hit bfcache constantly via app-switcher.

### Rule 2 — detect threshold *crossings*, not thresholds *above*

**Scope:** pattern is universal and robust on every browser. The trigger that makes this *necessary* (stray events before real user scroll) is mobile-dominant and iOS-sharpest, but even on desktop a programmatic `scrollTo` from focus/hash-change can set a "has scrolled" flag falsely.

A sticky `userHasInteracted` flag is not sufficient — a stray `touchmove` (or any programmatic scroll) can set it before the user has actually scrolled. The robust signal: fire auto-scroll only when `scrollY` **crosses** the threshold between two frames. Only a real forward scroll produces a crossing.

```js
let lastScrollY = 0;
let autoScrollArmed = true;
let isGliding = false;

function update() {
  const scrollY = window.scrollY;

  if (
    autoScrollArmed && !isGliding &&
    svh > 0 &&
    lastScrollY < svh && scrollY >= svh   // crossed from below
  ) {
    autoScrollArmed = false;
    smoothScrollTo(maxScroll, 5000);
  }
  if (scrollY < svh * 0.5) autoScrollArmed = true;   // re-arm on scroll-back

  lastScrollY = scrollY;
}
```

No interaction flag, no spurious firing, re-armable. Works *only because* scroll restoration is manual and initial `scrollY = 0` — the two rules are paired.

### Rule 3 — cancellable glides, carefully

**Scope:** universal desktop. The "same continuous gesture kills its own glide" trap happens on Chrome, Firefox, Safari identically — not browser-specific.

Users must interrupt a running auto-scroll. But the event that triggered it (typically `wheel`) will fire again and cancel its own effect if you're not careful.

```js
// Safe: touchstart cancels. DO NOT add wheel — same gesture kills its own glide.
window.addEventListener('touchstart', cancelGlide, { passive: true });
```

### Rule 4 — re-triggerable, not one-shot

Users scroll back to re-watch. Let the cinematic re-fire:

```js
if (scrollY < threshold * 0.5) autoScrollTriggered = false;
```

### Custom smooth-scroll (cancellation + cinematic easing)

**Scope:** the hard ~3s cap is iOS Safari specifically. On desktop the cap is softer/absent, but the other reasons to roll your own (control over duration, easing, interruptibility) are universal — `scrollTo({ behavior: 'smooth' })` and CSS `scroll-behavior: smooth` give you neither anywhere.

```js
function smoothScrollTo(target, duration) {
  const start = window.scrollY;
  const distance = target - start;
  const startTime = performance.now();
  glideCancelled = false;
  isGliding = true;

  function step(now) {
    if (glideCancelled) { isGliding = false; return; }
    const t = Math.min((now - startTime) / duration, 1);
    const eased = t < 0.5 ? 4*t**3 : 1 - (-2*t + 2)**3 / 2; // easeInOutCubic
    window.scrollTo(0, start + distance * eased);
    if (t < 1) requestAnimationFrame(step);
    else isGliding = false;
  }
  requestAnimationFrame(step);
}
```

`easeInOutCubic` feels cinematic; linear feels robotic.

## Fail-safe reveal logic

**Scope:** universal. Every browser has a paint-before-JS window; mobile Safari just has the widest (slower JS startup = the flash is a full second), but the fix applies everywhere.

Scroll-driven reveals hide elements via JS on first frame. Between first paint and script execution, they flash at full opacity.

### Hide at the CSS layer (the floor)

```css
.scroll-reveal {
  opacity: 0;
  transform: translateY(16px);
  will-change: opacity, transform;
}
#video-wrapper { opacity: 0; }
```

JS then takes over and animates these inline. CSS is the floor; JS is the driver.

### Handle `prefers-reduced-motion` synchronously

```js
if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
  for (const el of revealElements) {
    el.style.opacity = '1';
    el.style.transform = 'translateY(0)';
  }
  // Skip the scroll observer setup entirely
}
```

### Make corrupt measurements fail-safe, not fail-visible

Progressive reveal logic typically has three branches:

```js
if (scrollY < startPx)    { /* opacity = 0 */ }
else if (scrollY < endPx) { /* interpolate */ }
else                      { /* opacity = 1 */ }
```

If `startPx` or `endPx` is `0` or `NaN` (corrupt svh, missed range lookup), **every element falls through to the `else` branch** — visible on top of the hero. The CSS `opacity: 0` floor only helps until JS runs; after that, bad JS paints over good CSS.

Guard `update()` so bad data can never paint the revealed state:

```js
function update() {
  const scrollY = window.scrollY;

  if (svh <= 0 || !Number.isFinite(svh) || scrollY <= SCROLL_THRESHOLD) {
    hideReveals();   // measurement corrupt OR still at top → hide
    return;
  }
  // normal branch logic
}
```

**Rule of thumb:** the happy path must be *proven-correct* before the code can reach the fully-revealed branch. If any ingredient is missing, default to hidden. "Invisible on bug" is infinitely better than "everything stacked on top of the hero on bug".

### Don't

- Don't use `display: none` — won't contribute to layout, flex centering shifts when reveals appear
- Don't use `visibility: hidden` — breaks opacity transitions
- Don't put reveal init inside `DOMContentLoaded` + a 50ms "safety" timeout — that timeout *is* the flash
- Don't trust the CSS `opacity: 0` floor alone — the JS that overwrites it must also refuse to write `opacity: 1` on corrupt inputs

## Proportional layout

**Scope:** universal CSS layout concern, no browser dependency.

Breakpoints for hero positioning produce visible jumps when resizing across the threshold. Reads as "broken" even if each side is technically correct.

### Prefer flex ratios

```html
<main class="flex h-dvh flex-col items-center pb-20">
  <div class="flex-1" aria-hidden="true"></div>
  <div class="flex flex-col items-center"><!-- content --></div>
  <div class="flex-[2]" aria-hidden="true"></div>
</main>
```

Two spacers in a 1:2 ratio place content in the upper third **proportionally** at every viewport. No breakpoint, no jump.

### Prefer `clamp()` with limits

```css
.hero-padding { padding-top: clamp(4rem, 15svh, 10rem); }
```

### Don't

- Don't introduce a breakpoint to nudge a value by 40px — use `clamp()` or a flex ratio
- Don't layer `rem` on top of `vh` on top of `%` — pick one system per axis
- Don't `justify-center` when you mean "upper third" — the math works but the result drifts on tall vs short viewports

### When breakpoints ARE correct

Genuine structural change only: column-stack → side-by-side, nav hamburger → horizontal, hide/show different compositions. If you're only adjusting a spacing value, use a proportional unit.

## Mobile browser quirks

Quirks surfaced by shipping to real devices. The **Scope** column flags where each is iOS-only vs. broader.

| Thing | Behavior | Scope | Workaround |
|-------|----------|-------|------------|
| `autoplay` HTML attribute | Often ignored in low-power / data-saver states | iOS strictest; Chrome/Firefox also block | Set `muted`/`defaultMuted` from JS, call `play()` explicitly |
| `scrollTo({ behavior: 'smooth' })` | Capped at ~3s for any distance | **iOS-specific hard cap** | Custom rAF-based smooth scroll |
| `position: fixed` + `bottom-0` | Anchors to layout viewport, not visual | All mobile browsers with animated URL bar | `h-dvh` container + explicit bottom padding |
| `100vh` | = `lvh` — too tall when URL bar shows | All mobile browsers | `svh` or `dvh` based on use |
| `scroll` events at page load | 5–10 synthetic events during URL-bar settling | iOS most aggressive; Chrome Android milder | Gate auto-behaviors on `scrollY` *crossings* |
| `history.scrollRestoration` | Defaults to `'auto'` — restores across reloads | **Universal** (Chrome + Firefox + Safari) | `'manual'` + `scrollTo(0, 0)` at boot |
| bfcache preserves inline styles + scrollY | Frozen mid-animation on back-navigation | Chrome, Firefox, Safari since ~2022 | Same fix as above — manual scroll restoration + re-run init |
| `clientHeight` of svh-sized element | Can return `0` on first script tick | **iOS-specific** layout-timing quirk | Fallback to `innerHeight`, re-measure in `rAF` + `load` |
| Stray `touchmove` | Tap-to-open, edge-swipe-back all fire it | iOS-dominant; Android rarer | Never use sticky `userHasInteracted` flag for destructive behavior |
| MP4 required before WebM in sources | Safari won't fall through source list | **Safari desktop + iOS** | MP4 first, WebM second |
| `touch-action: manipulation` | Sometimes swallows taps on `<a>` | iOS-specific | Test real device, not emulator |
| `webkit-playsinline` | Required for inline video in older WebViews | iOS-specific | Always include; harmless elsewhere |

## Real-device test workflow

**Scope:** the workflow applies to any mobile browser. iOS is the priority target because it surfaces the widest set of bugs fastest — if your scroll-driven hero survives an iOS device with bfcache restore and scroll history, it almost certainly survives Chrome Android too. Don't skip Android — but if you only have time for one, choose iOS.

Desktop browser resize is not a mobile test. URL-bar toggle is the source of 80% of mobile-only bugs and no desktop browser reproduces it.

- Preview via LAN URL (local dev server + wifi, or an HTTPS tunnel like ngrok / Cloudflare Tunnel for PWA and service-worker tests) and open on your actual phone
- Test with URL bar expanded AND collapsed — scroll up to re-show it
- Test in Low Power Mode / data-saver — triggers autoplay rejection you can't catch in dev (iOS Low Power, Android data-saver)
- Test portrait AND landscape — landscape phone is ~400px tall, breaks most centered layouts
- **Test the return path.** Scroll to bottom, tap an external link, hit back. Chrome, Firefox, and Safari all bfcache-restore the page frozen mid-animation with inline styles preserved
- **Test a cold re-open with scroll history.** Scroll down, close the tab (not just the page), reopen the URL — any browser may restore `scrollY` from session storage
- **Test from a URL you've previously scrolled on.** Localhost has no scroll history for the origin; production does. The infamous *"works on local preview, broken on deployed"* symptom is almost always scroll restoration — reproducible on any browser, but iOS users trigger it constantly via app-switcher

### Fix at the right layer

When debugging a visual bug, resist fixing at JS if it's really a CSS concern. Scroll-reveal FOUC feels like JS timing (add a delay, wait for load), but the correct fix is four lines of CSS (`.scroll-reveal { opacity: 0 }`). JS workarounds for CSS problems always come back.

## Source

Battle-tested on a production immersive-cinematic site (coroboros.com) — full-screen hero video, scroll-driven cinematic reveal, zero-JS-by-default Astro stack. Every rule here traces to a specific production incident on real devices.
