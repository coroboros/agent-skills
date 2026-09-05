# Production Hardening

Battle-tested patterns for shipping immersive web design to real devices, distilled from production incidents — not lab testing. Load this when implementing any project with video, scroll-driven cinematic reveals, or full-screen heroes. These guards are boundary validations of documented browser behavior, not speculative error handling.

**Scope note.** Test the actual browser/device paths. iOS Safari is a useful stress case for autoplay, viewport changes and restoration; passing it does not establish Chrome or Firefox behavior. The incident notes below identify observed triggers, not universal timing guarantees.

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

Code samples in this file use literal values (durations, opacities, viewport units, scroll offsets) for clarity. In production, these must bind to DESIGN.md token namespaces — `motion.duration-*` for durations, `motion.ease-*` for easings, `opacity.*` for overlays, `heights.*` for viewport heights, `scrollTriggers.*` for fold offsets. Consume them as CSS custom properties (`var(--duration-reveal-slow)`) or Tailwind v4 utilities (`duration-reveal-slow`). Magic numbers in JS (`SPACER_MULTIPLIER`, scroll thresholds) read the corresponding `var(--scroll-*)` at startup, never hardcode. Full convention: [design-system's extended-tokens reference](https://github.com/coroboros/agent-skills/blob/main/skills/design-system/references/extended-tokens.md). Validate with `/design-system audit-extensions DESIGN.md`.

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
.hero { min-height: 100svh; }                       /* stable floor — Baseline 2022, same as dvh */
@supports (height: 100dvh) { .hero { min-height: 100dvh; } }  /* dynamic where wanted */
```

A bare `100vh` fallback line would trip the pre-flight scanner and misbehave on iOS anyway — engines old enough to lack `svh` also lack `dvh`; omit the legacy line.

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

**Scope:** autoplay can be refused under browser or user policy. Keep an intentional poster and handle the play promise on every target browser. Source order is a delivery choice, not a claim that Safari lacks WebM; support facts belong in `stack-facts.md`.

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
- `preload="auto"` requests buffering; the browser may ignore the hint or refuse playback

### Source order — MP4 first, WebM second

The example prefers MP4 as its delivery choice. Safari supports WebM; source selection and codec support vary by target, and source order alone is not a playback guarantee. Verify the actual encoded files and retain the poster on failure. See the [WebKit Safari 17.4 media notes](https://webkit.org/blog/15063/webkit-features-in-safari-17-4/) and the dated support owner.

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

No award jury publishes a byte cap (`stack-facts.md`, `award-imperatives.md` #7), and the poster carries first paint either way — but a hero video past ~5 MB spends the connection's headroom on the critical path, so the loop starts late and the poster sits there on a median link. Compress toward 3 MB before trading any fidelity. `ffmpeg -crf 28 -preset slow`. Loop 8–15s. Longer = bandwidth for frames nobody watches.

## Scroll-driven cinematic sequences

**Scope:** an explicitly committed cinematic glide, where the page advances through an authored sequence after forward input. Ordinary content scrolling keeps native control. A numeric threshold crossing alone does not establish user intent: restoration, focus, anchors and scripts can all move the page.

Preserve the chosen restoration policy. Use `history.scrollRestoration = 'manual'` only when the application owns restoration, and restore its state on back/forward navigation. Resetting every visit to the top is an explicit arrival choice, not a universal fix for animation state.

### Input, settling and cancellation

The example requires recent trusted forward input before arming a crossing. It waits for the input/scroll burst to settle before beginning its glide, so the initiating wheel gesture does not immediately cancel its own animation. Once running, fresh wheel, keyboard or pointer interaction cancels it. Reduced motion and cleanup cancel both pending and active work.

Input correlation is bounded evidence, not a browser-provided scroll-cause flag. Call the returned `cancel()` before programmatic navigation, focus or scroll changes; use direct user activation instead when the application cannot distinguish those paths. The thresholds, destination, duration and easing below come from the committed motion/scroll tokens.

```javascript
export function initCinematicScroll({ threshold, target, duration, ease }) {
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  let lastY = scrollY, forwardUntil = 0, touchY = null;
  let armed = true, active = false, frame = 0, pending = 0;

  function cancel() {
    clearTimeout(pending);
    cancelAnimationFrame(frame);
    pending = frame = 0;
    active = false;
    forwardUntil = 0;
  }

  function start() {
    pending = 0;
    if (motion.matches) return;
    const from = scrollY, to = target(), started = performance.now();
    if (![from, to, duration].every(Number.isFinite) || duration <= 0) return;
    active = true;
    function tick(now) {
      if (!active) return;
      const progress = Math.min((now - started) / duration, 1);
      window.scrollTo({ top: from + (to - from) * ease(progress), behavior: 'instant' });
      if (progress < 1) frame = requestAnimationFrame(tick);
      else { active = false; frame = 0; }
    }
    frame = requestAnimationFrame(tick);
  }

  function afterSettle() {
    clearTimeout(pending);
    pending = setTimeout(start, 150); // gesture-settle debounce, not authored motion duration
  }

  function onInput(event) {
    if (!event.isTrusted) return;
    if (event.type === 'pointermove' && event.pointerType !== 'touch' && !event.buttons) return;
    if (active) { cancel(); return; }
    let forward = false;
    if (event.type === 'wheel') forward = event.deltaY > 0;
    if (event.type === 'keydown') {
      forward = ['ArrowDown', 'PageDown', 'End'].includes(event.key)
        || (event.key === ' ' && !event.shiftKey);
    }
    if (event.type === 'pointerdown') touchY = event.clientY;
    if (event.type === 'pointermove') {
      forward = touchY !== null && event.clientY < touchY;
      touchY = event.clientY;
    }
    if (forward && !motion.matches) {
      forwardUntil = performance.now() + 200;
      if (pending) afterSettle();
    } else {
      cancel();
    }
  }

  function onScroll() {
    const y = scrollY, boundary = threshold();
    if (!Number.isFinite(boundary) || boundary <= 0) { cancel(); lastY = y; return; }
    if (y < boundary * 0.5) { armed = true; if (!active) cancel(); }
    if (!active && armed && !motion.matches && forwardUntil > performance.now()
        && lastY < boundary && y >= boundary) {
      armed = false;
      afterSettle();
    } else if (pending) {
      afterSettle();
    }
    lastY = y;
  }

  const inputs = ['wheel', 'keydown', 'pointerdown', 'pointermove'];
  inputs.forEach(type => addEventListener(type, onInput, { passive: true }));
  addEventListener('scroll', onScroll, { passive: true });
  const onMotion = () => { if (motion.matches) cancel(); };
  motion.addEventListener('change', onMotion);
  return {
    cancel,
    destroy() {
      cancel();
      inputs.forEach(type => removeEventListener(type, onInput));
      removeEventListener('scroll', onScroll);
      motion.removeEventListener('change', onMotion);
    },
  };
}
```

The controller re-arms only after returning below half the trigger distance. It does not block native input. Validate wheel, touch, keyboard interruption, restored navigation and preference changes on the target devices; no fixed native smooth-scroll duration is assumed.

## Fail-safe reveal logic

**Scope:** content stays readable when initialization is late, blocked or broken. Decorative cinematic layers may disappear on failure, but the information they accompany remains in the normal document flow.

### Readiness belongs to the actual engine

Use `skeletons.md` §G for fire-once content reveals: visible base CSS, a reduced-motion gate, then per-element `data-reveal-ready` only after the observer successfully registers that element. Already-visible copy stays visible when initialization arrives late. The lifecycle restores all content on setup/update failure, teardown or a reduced-motion change.

A generic `html.js` flag set by an independent head script cannot protect against failure of the later reveal bundle. Do not pre-hide the page under that marker or under unconditional base opacity. An authored hero entrance can initialize before its first paint when possible; a delayed entrance must yield to readable content.

### Invalid measurements restore the static composition

Check each measurement before using it. Zero can be a valid start offset; non-finite values, a nonpositive viewport reference, or an end before its start are not valid ranges.

```javascript
function updateReveal({ svh, startPx, endPx }, restoreStaticLayout, renderProgress) {
  if (![svh, startPx, endPx].every(Number.isFinite) || svh <= 0 || endPx <= startPx) {
    restoreStaticLayout(); // visible copy in normal flow, with the poster if needed
    console.error('Invalid reveal range; using the static composition.');
    return;
  }
  const progress = Math.max(0, Math.min(1, (scrollY - startPx) / (endPx - startPx)));
  renderProgress(progress);
}
```

The project supplies `restoreStaticLayout` and `renderProgress`; the former removes cinematic positioning/readiness and shows the committed static layout. Wrap project-specific rendering errors with the same restoration and a visible diagnostic. Reduced motion takes this static branch before any animation setup and when the preference changes. Do not solve stacked cinematic overlays by hiding reader content on error.

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

### When breakpoints are correct

Genuine structural change only: column-stack → side-by-side, nav hamburger → horizontal, hide/show different compositions. If you're only adjusting a spacing value, use a proportional unit.

## Mobile browser quirks

Quirks surfaced by shipping to real devices. The **Scope** column flags where each is iOS-only vs. broader.

| Thing | Behavior | Scope | Workaround |
|-------|----------|-------|------------|
| `autoplay` HTML attribute | Often ignored in low-power / data-saver states | iOS strictest; Chrome/Firefox also block | Set `muted`/`defaultMuted` from JS, call `play()` explicitly |
| Native smooth-scroll duration | Browser-controlled timing | Cross-browser | Use an explicitly committed cancellable glide only when authored timing is needed |
| `position: fixed` + `bottom-0` | Anchors to layout viewport, not visual | All mobile browsers with animated URL bar | `h-dvh` container + explicit bottom padding |
| `100vh` | = `lvh` — too tall when URL bar shows | All mobile browsers | `svh` or `dvh` based on use |
| Scroll changes without new intent | Restoration, viewport changes, anchors or scripts can move the page | Cross-browser | A threshold alone cannot authorize an automatic glide; correlate input and cancel programmatic paths |
| `history.scrollRestoration` | Browser restoration can resume mid-page | Cross-browser | Preserve restoration or implement an explicit application-owned policy |
| bfcache preserves scene state | Navigation can resume mid-animation | Cross-browser | Reconcile restored state on the return path; test the chosen policy |
| `clientHeight` of svh-sized element | Can return `0` on first script tick | **iOS-specific** layout-timing quirk | Fallback to `innerHeight`, re-measure in `rAF` + `load` |
| Stray `touchmove` | Tap-to-open, edge-swipe-back all fire it | iOS-dominant; Android rarer | Never use sticky `userHasInteracted` flag for destructive behavior |
| Video source selection | Codec/container support depends on the target | Cross-browser | Verify actual encodes and poster fallback; Safari supports WebM |
| `touch-action: manipulation` | Sometimes swallows taps on `<a>` | iOS-specific | Test real device, not emulator |
| `webkit-playsinline` | Required for inline video in older WebViews | iOS-specific | Always include; harmless elsewhere |

## Real-device test workflow

**Scope:** test the mobile browsers and devices required by the project. iOS and Android exercise different rendering, media and navigation behavior; passing on one does not establish support for the other. Prioritize the audience's devices and record any untested targets.

Desktop browser resize does not reproduce mobile browser chrome. Test URL-bar expansion and collapse on a real device because they change the visible viewport.

- Preview via LAN URL (local dev server + wifi, or an HTTPS tunnel like ngrok / Cloudflare Tunnel for PWA and service-worker tests) and open on your actual phone
- Test with URL bar expanded and collapsed — scroll up to re-show it
- Test in Low Power Mode / data-saver — triggers autoplay rejection you can't catch in dev (iOS Low Power, Android data-saver)
- Test portrait and landscape — landscape phone is ~400px tall, breaks most centered layouts
- **Test the return path.** Scroll to bottom, tap an external link, hit back. When eligible for bfcache, a page may resume with preserved animation and inline-style state; verify the actual restored result
- **Test a cold re-open with scroll history.** Scroll down, close the tab (not just the page), reopen the URL — any browser may restore `scrollY` from session storage
- **Test from a URL you've previously scrolled on.** Both localhost and deployed origins can have scroll history. Compare fresh navigation, reload and restored navigation before attributing a deployment-only failure to scroll restoration

### Fix at the right layer

Keep the visible fallback in CSS and readiness in the engine that owns the effect. Delays and unconditional `.scroll-reveal { opacity: 0 }` can conceal timing problems while making initialization failures blank the content. Use the verified lifecycle in `skeletons.md` §G.

## Source

Battle-tested on a production immersive-cinematic site (coroboros.com) — full-screen hero video, scroll-driven cinematic reveal, zero-JS-by-default Astro stack. Every rule here traces to a specific production incident on real devices.
