# Skeletons — the executable forms

Seven wirings a build gets wrong from memory. Each is the whole file, not a fragment: copy it, rename the selectors, delete the beats you don't need. The comments mark only the lines that decide whether the thing works — everything uncommented is ordinary code.

Versions, support percentages, and package names are **not** repeated here — every such fact lives once in `stack-facts.md`, dated. Read that file before pinning a dependency.

Loads when the first technique is wired, by heading, for the mechanics the design_plan committed. The *what* (which mechanic serves the world) is `motion-palette.md` and `signature-invention.md`; this file is only the *how*.

## Rules that bind every skeleton below

- **`start: 'top top'`** on anything pinned. `'top center'` and `'top 80%'` fire the pin halfway down the viewport and the visitor watches half a slide slide.
- **One cleanup path per rig.** Every skeleton that holds state — an instance, an observer, a ticker function, a timeline — returns exactly one teardown, and never two overlapping ones. In React that teardown is `useEffect`'s return; a rig that survives unmount stacks a second copy on remount.
- **`ScrollTrigger.refresh()` after anything that moves layout post-measure** — a `font-display: swap` face landing, lazy content, an accordion opening. Trigger positions drift silently otherwise, and the drift only shows on a slow connection.
- **A ScrollTrigger lives on the timeline itself or on a top-level tween** — never on a tween nested inside a parent timeline, where it is measured against the wrong element.
- **`scrub` and `toggleActions` never share a trigger.** Scrub wins silently and the toggle config reads as dead code.
- **`markers: true` never ships.**
- **One `position: sticky; top: 0` per stacking context.** A second sticky element under a sticky nav paints over it — offset the later one by the nav height (`top: var(--nav-height)`) and split the z-index scale.

## A. Lenis + GSAP — the fixed wiring

```javascript
import Lenis from 'lenis';

// GSAP is read off the runtime rather than imported, because this rig has to work
// on a page that never loaded it — a static import would make the fallback below
// unreachable dead code.
export function initSmoothScroll({ lerp = 0.1, wheelMultiplier = 1 } = {}) {
  const gsap = globalThis.gsap;
  const ScrollTrigger = gsap ? globalThis.ScrollTrigger : null;

  // Native scroll IS the reduced-motion contract — return a null instance, never a fake one.
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) {
    return { lenis: null, destroy() {} };
  }

  const lenis = new Lenis({ lerp, wheelMultiplier });   // no autoRaf — one driver only, chosen below
  let tickerFn = null;
  let rafId = 0;

  if (ScrollTrigger) {
    lenis.on('scroll', ScrollTrigger.update);           // Lenis reports; ScrollTrigger never listens itself
    tickerFn = (time) => lenis.raf(time * 1000);        // gsap.ticker passes seconds, lenis.raf wants ms
    gsap.ticker.add(tickerFn);
    gsap.ticker.lagSmoothing(0);                        // no frame-skipping mid-scrub
  } else {
    const loop = (time) => { lenis.raf(time); rafId = requestAnimationFrame(loop); };
    rafId = requestAnimationFrame(loop);                // GSAP absent: one own rAF, same single clock
  }

  return {
    lenis,
    destroy() {
      if (rafId) cancelAnimationFrame(rafId);
      if (tickerFn) {
        gsap.ticker.remove(tickerFn);
        gsap.ticker.lagSmoothing(500, 33);              // restore the default; it is a page-wide setting
      }
      lenis.destroy();
    },
  };
}
```

Critical points: exactly one rAF clock drives Lenis — `gsap.ticker` when GSAP is on the page, an own `requestAnimationFrame` when it is not — `lenis.on('scroll', ScrollTrigger.update)` is what keeps every trigger in step, `lagSmoothing(0)` stops GSAP from swallowing a slow frame mid-scrub and is restored on teardown because it is global, and `destroy()` removes the ticker function and the loop it created, not just the instance.

Common failure: `new Lenis({ autoRaf: true })` *plus* `gsap.ticker.add((t) => lenis.raf(t * 1000))` — two rAF clocks advance the same instance twice per frame, scrub positions land between the two reads and every pinned section jitters; the fix is `autoRaf` omitted (it defaults off) with the ticker as the sole driver, exactly as above.

## B. ScrollTrigger pin + scrub

```javascript
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

export function initPinnedChapter(section) {
  const mm = gsap.matchMedia();

  mm.add('(prefers-reduced-motion: no-preference)', () => {
    const tl = gsap.timeline({
      scrollTrigger: {
        trigger: section,
        start: 'top top',           // pin the instant the section top meets the viewport top
        end: '+=100%',
        pin: section,               // pin the WRAPPER; the children are what move
        pinSpacing: true,           // false ⇒ panels stack in shared scroll space (sticky-stack)
        scrub: 1,
      },
    });

    tl.to(section.querySelector('.chapter-media'), { scale: 1.12, ease: 'none' })
      .to(section.querySelector('.chapter-copy'), { yPercent: -18, ease: 'none' }, 0);

    return () => tl.kill();         // matchMedia tears this down on the query flip
  });

  mm.add('(prefers-reduced-motion: reduce)', () => {
    gsap.set(section.querySelectorAll('.chapter-media, .chapter-copy'), { clearProps: 'all' });
  });

  document.fonts.ready.then(() => ScrollTrigger.refresh());   // the web face landing moves every trigger

  return () => mm.revert();
}
```

Critical points: `gsap.matchMedia()` owns both branches so the reduced-motion flip sets up and tears down on its own, the pin target is the section and the tweens target its children, `ease: 'none'` keeps a scrubbed tween welded to the scrollbar, `document.fonts.ready` is what re-measures after the web face lands, and `pinSpacing: false` is the single line that turns this into a sticky-stack — panels share scroll space instead of pushing the page taller.

Common failure: `scale: 1.12` written with the default `ease` on a `scrub` trigger — the curve double-applies against the scroll's own progress and the media lurches at both ends of the pin; the fix is `ease: 'none'` on every scrubbed property, with the character coming from the choreography rather than the curve.

## C. Horizontal pan

```javascript
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

export function initHorizontalPan(wrap, track) {
  const mm = gsap.matchMedia();

  mm.add('(prefers-reduced-motion: no-preference)', () => {
    const distance = () => track.scrollWidth - window.innerWidth;

    gsap.to(track, {
      x: () => -distance(),       // function value: re-read on refresh, never frozen at init
      ease: 'none',               // 1:1 with the scrollbar
      scrollTrigger: {
        trigger: wrap,
        pin: wrap,                // pin the wrapper — pinning the animated element drifts and jitters
        start: 'top top',
        end: () => '+=' + distance(),   // scroll distance EQUALS the horizontal travel
        scrub: 1,
        invalidateOnRefresh: true,      // flush the tween's recorded start x, so the function value re-runs
      },
    });
    // No cleanup returned and none needed: matchMedia reverts every tween and
    // trigger created inside this callback when the query stops matching.
  });

  document.fonts.ready.then(() => ScrollTrigger.refresh());

  return () => mm.revert();
}
```

Critical points: `distance()` is a function so `x` and `end` both recompute on refresh — `end` would re-run anyway, but the tween's recorded start `x` only re-runs because of `invalidateOnRefresh` — `end` equal to the travel is what locks the pan to the scrollbar, the wrapper is pinned while the track is animated, and `mm.revert()` is the single teardown for everything the rig created.

Common failure: `end: '+=2000'` (or any literal) with a track whose width is content-driven — the pan finishes early and the visitor scrolls through dead pinned space, or it never finishes and the last panel is unreachable; the fix is the function-valued `end` above, paired with `invalidateOnRefresh: true`.

## D. SplitText — the current API

```javascript
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { SplitText } from 'gsap/SplitText';   // ships in the public package; see stack-facts.md

gsap.registerPlugin(SplitText, ScrollTrigger);

export function initHeadlineReveal(headline) {    // an element, so it can also be the trigger
  const mm = gsap.matchMedia();
  mm.add('(prefers-reduced-motion: no-preference)', () => {
    const split = SplitText.create(headline, {
    type: 'lines, words',
    mask: 'lines',        // per-line overflow wrapper — the clean rise, no hand-rolled clip-path
    autoSplit: true,      // re-splits when the web font lands or the container width changes
    aria: 'auto',         // the source string stays readable to assistive tech after the split
    onSplit(self) {
      return gsap.from(self.words, {   // RETURN the tween — autoSplit reverts it before re-splitting
        yPercent: 110,
        autoAlpha: 0,
        stagger: 0.045,
        duration: 0.9,
        ease: 'expo.out',
        scrollTrigger: { trigger: headline, start: 'top 80%', once: true },
      });
    },
    });

    return () => split.revert(); // query flip restores readable, unsplit markup
  });
  return () => mm.revert();
}
```

Critical points: `SplitText.create()` is the current factory, `autoSplit` plus a *returned* tween from `onSplit` survives a late font load, `mask: 'lines'` supplies the overflow wrapper, `aria: 'auto'` preserves accessible text, and `once: true` persists the reveal. `gsap.matchMedia()` skips splitting under reduced motion and reverts the split when that preference changes; `mm.revert()` owns unmount cleanup.

Common failure: `new SplitText('.headline', { type: 'chars' })` followed by a separate `gsap.from(split.chars, …)` — the split is measured before `font-display: swap` swaps the face, so the lines re-flow under already-positioned characters and the headline reveals in the wrong shape; the fix is the `autoSplit` + `onSplit`-returns-the-tween form above, which re-splits and re-runs on the swap.

## E. Three.js scene — WebGPU path, WebGL fallback

```javascript
import * as THREE from 'three/webgpu';   // the WebGPU build; see stack-facts.md before pinning

export async function initScene(canvas, { poster } = {}) {
  // The poster is the LCP element and the reduced-motion scene — it is already painted;
  // the renderer only ever replaces it, never blocks it.
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return { destroy() {} };

  const renderer = new THREE.WebGPURenderer({ canvas, antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));   // 3× costs fill rate and buys no sharpness
  try {
    await renderer.init(); // requests WebGPU, or falls back to WebGL2
  } catch (error) {
    renderer.dispose();
    console.error('Scene initialization failed; keeping the poster.', error);
    return { destroy() {} };
  }

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 100);
  camera.position.z = 4;
  const geometry = new THREE.IcosahedronGeometry(1, 3); // wiring demo; replace with the committed asset
  const material = new THREE.MeshStandardNodeMaterial({ roughness: 0.35 });
  scene.add(new THREE.Mesh(geometry, material));
  scene.add(new THREE.DirectionalLight(0xffffff, 2.5));

  const resize = () => {
    const { clientWidth: w, clientHeight: h } = canvas;
    if (w <= 0 || h <= 0) return;
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h, false);   // false: never write inline style onto the canvas
  };
  resize();
  addEventListener('resize', resize);

  let failed = false;
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  const frame = () => {
    try {
      if (canvas.clientWidth <= 0 || canvas.clientHeight <= 0) return;
      renderer.render(scene, camera);
      if (poster) poster.dataset.sceneReady = ''; // only after a successful render
    } catch (error) {
      failed = true;
      if (poster) delete poster.dataset.sceneReady;
      sync();
      console.error('Scene rendering failed; keeping the poster.', error);
    }
  };

  // Off-screen AND background tabs pay nothing. Two independent booleans, ANDed:
  // one shared flag would let a tab-return restart the loop on an off-screen
  // canvas, because the observer only fires again when intersection changes.
  let onScreen = false;
  let visible = document.visibilityState === 'visible';
  let running = false;
  function sync() {
    const next = onScreen && visible && !motion.matches && !failed;
    if (next === running) return;
    running = next;
    renderer.setAnimationLoop(running ? frame : null);
  }
  const io = new IntersectionObserver(([entry]) => { onScreen = entry.isIntersecting; sync(); });
  const onVisibility = () => { visible = document.visibilityState === 'visible'; sync(); };
  const onMotion = () => {
    if (motion.matches && poster) delete poster.dataset.sceneReady;
    sync();
  };
  io.observe(canvas);
  document.addEventListener('visibilitychange', onVisibility);
  motion.addEventListener('change', onMotion);

  return {
    destroy() {
      renderer.setAnimationLoop(null);
      io.disconnect();
      document.removeEventListener('visibilitychange', onVisibility);
      motion.removeEventListener('change', onMotion);
      removeEventListener('resize', resize);
      geometry.dispose();
      material.dispose();
      renderer.dispose();
      if (poster) delete poster.dataset.sceneReady;
    },
  };
}
```

Critical points: await `renderer.init()`, retain the poster through the first successful render and on failure, cap pixel ratio, and leave CSS sizing intact. Intersection, visibility and reduced-motion state jointly govern the loop. `destroy()` removes listeners and disposes the renderer and its owned geometry/material; dispose additional scene assets through this same path.

Common failure: `new THREE.WebGPURenderer(...)` followed immediately by `renderer.render(scene, camera)` with no `await renderer.init()` — the backend is not up, so `render()` throws outright (`.render() called before the backend is initialized`) and the page is blank, not merely stuttering; the fix is the awaited `init()` above, with the poster holding the frame until it resolves.

## F. View Transitions — the progressive-enhancement floor

```css
/* Cross-document: opt in per document, on BOTH ends of the navigation, and only
   same-origin with no cross-origin redirect. Not Baseline — see stack-facts.md.
   A browser without it performs the ordinary navigation, the correct floor. */
@view-transition { navigation: auto; }

::view-transition-group(*) { animation-duration: 0.45s; }

/* Reduced motion kills the animation, never the swap — the new view still arrives. */
@media (prefers-reduced-motion: reduce) {
  ::view-transition-group(*),
  ::view-transition-old(*),
  ::view-transition-new(*) { animation: none; }
}

.card__media { view-transition-name: var(--vt-name); }   /* unique per snapshot, set inline per card */
```

```javascript
// Same-document: the guard IS the fallback. No polyfill, no duplicated branch —
// `update()` performs the DOM change either way; only the animation is conditional.
export function withViewTransition(update) {
  if (!document.startViewTransition) return Promise.resolve(update());
  const transition = document.startViewTransition(update);
  transition.ready.catch(() => {});   // `ready` REJECTS on a skipped transition; unhandled it logs
  return transition.finished;         // `finished` resolves either way, so the caller proceeds
}

// Only the morphing pair carries a name, and only while the transition runs —
// two live elements sharing one view-transition-name abort the whole transition.
export async function openDetail(card, render) {
  card.style.setProperty('--vt-name', 'detail-media');
  await withViewTransition(() => render(card.dataset.id));
  card.style.removeProperty('--vt-name');
}
```

Critical points: the CSS at-rule and the JS `startViewTransition` check are two independent features with two independent guards, `update()` runs unconditionally so a browser without the API still changes the page, `view-transition-name` is assigned per element from a custom property and cleared after, and the reduced-motion block zeroes the animation while leaving the swap intact.

Common failure: `view-transition-name: detail-media` written as a static rule on a card *class* — every card in the grid claims the same name, so the API skips the whole transition and rejects `ready`, which surfaces as an unhandled rejection rather than a visible clue; the fix is the per-element custom property set on the one card being opened and removed when `finished` resolves, with `ready` caught as above.

## G. Fire-once IO reveal

```css
/* Base state is visible. Readiness belongs to the initialized observer,
   not an unrelated head script that merely proves JavaScript is enabled. */
.reveal { opacity: 1; }

@media (prefers-reduced-motion: no-preference) {
  .reveal[data-reveal-ready]:not([data-shown]) { opacity: 0; transform: translateY(1.25rem); }
  .reveal[data-shown] {
    opacity: 1;
    transform: none;
    transition: opacity 0.8s var(--ease-out-expo), transform 0.8s var(--ease-out-expo);
  }
}
```

```javascript
export function initReveals(root = document) {
  const elements = [...root.querySelectorAll('.reveal')];
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  let io;
  const showAll = () => {
    if (io) io.disconnect();
    for (const el of elements) {
      el.setAttribute('data-shown', '');
      el.removeAttribute('data-reveal-ready');
    }
  };
  const onMotion = () => { if (motion.matches) showAll(); };
  try {
    if (motion.matches) { showAll(); return showAll; }
    io = new IntersectionObserver((entries) => {
      try {
        for (const entry of entries) {
          if (!entry.isIntersecting) continue;
          entry.target.setAttribute('data-shown', '');
          io.unobserve(entry.target); // fire once, then persist
        }
      } catch (error) {
        showAll();
        console.error('Reveal update failed; showing content.', error);
      }
    }, { rootMargin: '0px 0px -10% 0px' });
    for (const el of elements) {
      if (el.getBoundingClientRect().top < innerHeight) {
        el.setAttribute('data-shown', ''); // delayed initialization never hides visible copy
      } else {
        io.observe(el);
        el.setAttribute('data-reveal-ready', ''); // only after registration succeeds
      }
    }
    motion.addEventListener('change', onMotion);
  } catch (error) {
    showAll();
    console.error('Reveal initialization failed; showing content.', error);
  }
  return () => { motion.removeEventListener('change', onMotion); showAll(); };
}
```

Critical points: hide only offscreen elements registered with the live observer, under `prefers-reduced-motion: no-preference`. Already-visible text stays shown if initialization arrives late. `unobserve` makes the reveal persist; failure, teardown and a reduced-motion change restore all content. No head readiness marker or scroll listener is needed.

Common failure: hiding under a head script's `html.js` marker while a later observer bundle fails leaves content blank despite JavaScript being enabled; the fix is visible base CSS plus readiness owned by successful observer initialization and fail-visible cleanup.

## Cross-references

`stack-facts.md` (every version, package, and support number these skeletons depend on) · `motion-palette.md` (which mechanic the world calls for, and the CSS scroll-driven path for décor) · `text-effects.md` (type as a motion surface) · `foundations.md` (type ramps, easing lexicon, spring registers, UX and a11y floors).
