/*
 * stepped-counter-loader — the ratcheting brutalist counter (source: Joffrey
 * Spitzer — technique, award-unverified). The brutalist VARIANT of
 * counter-loader: the number never rolls — it ratchets 0→100 in n discrete
 * jumps (the winner's ease steps(14); the JUMP is the brutalist tell, vs the
 * smooth roll) over ~3s, then the overlay wipes away through a clip-path
 * inset() collapse. The ratchet stays honest: it climbs to the second-to-last
 * step over `minDuration`, holds there until the real window `load`, then
 * takes the final jump to 100 (recoloring to the accent) and wipes. Optional
 * Flip hand-off for the studio-reel spine: a full-bleed plate inside the
 * overlay FLIPs (first/last/invert/play, WAAPI — the winner's tool is GSAP
 * Flip) to match the showreel element's size/position while the overlay wipes,
 * so the watched image becomes the hero's media. Authored `hidden` and
 * un-hidden by JS, so no-JS or a dead script never blocks the page (the
 * gated-splash law). reduced-motion skips the loader entirely — no ratchet,
 * no wipe, onDone fires.
 *
 * Expected markup — authored `hidden`; the plate figure is optional and only
 * used when opts.flipTo names a target:
 *   <div data-ad-stepped-loader hidden>
 *     <figure data-ad-stepped-fig><img src="…" alt=""></figure>
 *     <span data-ad-stepped-count>0</span>
 *   </div>
 *
 * Usage:  awardSteppedCounterLoader.init(root, opts)
 *   root         Element|Document  scope (default document)
 *   selector     string    the overlay (default '[data-ad-stepped-loader]')
 *   steps        number    discrete jumps for the 0→100 ratchet (default 14)
 *   minDuration  ms        floor for the ratchet (default 3000 — the ~3s beat)
 *   flipTo       string    selector for the showreel element the plate Flips
 *                          into (no target or no plate → plain inset wipe)
 *   sessionOnce  boolean   skip after the first completed run this session
 *   onDone       function  runs once after the wipe (and Flip) land — start the
 *                          hero here. Also fires immediately on the skip paths
 *                          (reduced-motion, sessionOnce).
 * Returns { destroy() }. Idempotent — while ratcheting it returns the live
 * handle; once done (or skipped) a re-init is a no-op. destroy() cancels the
 * ratchet, wipe and Flip, restores `hidden` + body scroll + the authored count
 * text, and removes the stylesheet.
 *
 * Tokens: --ad-ground + --ad-ink paint the overlay; --ad-font-mono sets the
 * count; --ad-accent recolors it on the final jump; --ad-dur-base (420ms)
 * times the recolor and the 100-beat; --ad-dur-reveal (800ms) +
 * --ad-ease-signature time the wipe and the Flip.
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-stepped-counter-loader-css';
  var SEEN_KEY = 'ad-stepped-counter-loader-done';

  var reduce = function () {
    return global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches;
  };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    // Scoped under .ad-stepped — the class JS adds after removing `hidden`.
    // No-JS never gets the class, so the UA `[hidden]` display:none stands.
    s.textContent =
      '.ad-stepped{position:fixed;inset:0;z-index:100000;display:flex;' +
        'align-items:flex-end;justify-content:flex-end;' +
        'padding:clamp(1rem,4vw,3rem);box-sizing:border-box;' +
        'background:var(--ad-ground,oklch(14% 0.01 260));' +
        'color:var(--ad-ink,oklch(96% 0 0));}' +
      '.ad-stepped[data-ad-done]{display:none;}' +
      '.ad-stepped [data-ad-stepped-fig]{position:absolute;inset:0;margin:0;}' +
      '.ad-stepped [data-ad-stepped-fig] img{display:block;width:100%;height:100%;' +
        'object-fit:cover;}' +
      '.ad-stepped [data-ad-stepped-count]{position:relative;' +
        'font-family:var(--ad-font-mono,ui-monospace,monospace);' +
        'font-size:clamp(3rem,10vw,8rem);line-height:1;' +
        'font-variant-numeric:tabular-nums;' +
        'transition:color var(--ad-dur-base,420ms) ' +
        'var(--ad-ease-signature,cubic-bezier(.16,1,.3,1));}' +
      '.ad-stepped[data-ad-near] [data-ad-stepped-count]{' +
        'color:var(--ad-accent,oklch(62% 0.2 25));}';
    document.head.appendChild(s);
  }

  function styles() {
    var cs = getComputedStyle(document.documentElement);
    function v(name, fallback) {
      return (cs.getPropertyValue(name) || '').trim() || fallback;
    }
    return {
      durReveal: parseFloat(v('--ad-dur-reveal', '800ms')) || 800,
      durBase: parseFloat(v('--ad-dur-base', '420ms')) || 420,
      ease: v('--ad-ease-signature', 'cubic-bezier(.16,1,.3,1)')
    };
  }

  // sessionStorage throws in some privacy modes — a loader must never.
  function seen() {
    try { return global.sessionStorage.getItem(SEEN_KEY) === '1'; }
    catch (e) { return false; }
  }
  function markSeen() {
    try { global.sessionStorage.setItem(SEEN_KEY, '1'); } catch (e) {}
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-stepped-loader]';
    var steps = opts.steps != null ? opts.steps : 14;
    var minDuration = opts.minDuration != null ? opts.minDuration : 3000;
    var flipTo = opts.flipTo || null;
    var sessionOnce = !!opts.sessionOnce;
    var onDone = typeof opts.onDone === 'function' ? opts.onDone : null;

    var loader = root.querySelector(selector);
    if (!loader) return { destroy: function () {} };

    // Idempotent: done → no-op; still ratcheting → the live handle (no rebind).
    var prev = loader.__adSteppedLoader;
    if (prev) return prev.done ? { destroy: function () {} } : prev.handle;

    // Skip paths — the overlay keeps its authored `hidden`, the page just shows.
    if (reduce() || (sessionOnce && seen())) {
      var skipState = { done: true, handle: null };
      loader.__adSteppedLoader = skipState; // a re-init must not re-fire onDone
      skipState.handle = { destroy: function () { delete loader.__adSteppedLoader; } };
      if (onDone) onDone();
      return skipState.handle;
    }

    injectCss();
    var countEl = loader.querySelector('[data-ad-stepped-count]');
    var fig = loader.querySelector('[data-ad-stepped-fig]');
    var countText0 = countEl ? countEl.textContent : '';
    var hadHidden = loader.hasAttribute('hidden');
    var prevOverflow = document.body.style.overflow;
    var state = { done: false, raf: 0, anims: [], handle: null };
    loader.__adSteppedLoader = state;

    var loaded = document.readyState === 'complete';
    function onLoad() { loaded = true; }
    if (!loaded) global.addEventListener('load', onLoad);

    // Open: un-hide, promote to the JS-only class, announce busy, lock scroll.
    loader.removeAttribute('hidden');
    loader.classList.add('ad-stepped');
    loader.setAttribute('aria-busy', 'true');
    document.body.style.overflow = 'hidden';

    var lastStep = -1;
    function setStep(step) {
      if (step === lastStep) return; // write only on the jump — the ratchet tell
      lastStep = step;
      if (countEl) countEl.textContent = String(Math.round((step / steps) * 100));
      if (step >= steps) loader.setAttribute('data-ad-near', '');
    }

    function finalize() {
      state.anims = [];
      state.done = true;
      global.removeEventListener('load', onLoad);
      document.body.style.overflow = prevOverflow;
      loader.removeAttribute('aria-busy');
      loader.setAttribute('aria-hidden', 'true');
      loader.setAttribute('data-ad-done', ''); // → display:none
      markSeen();
      if (onDone) onDone();
    }

    // The Flip hand-off: first/last/invert/play — the plate leaves the overlay
    // (fixed at its current rect), lands on the showreel's rect, then unmounts;
    // the target's own media takes over underneath.
    function flipPlate(s) {
      var target = flipTo ? root.querySelector(flipTo) : null;
      if (!fig || !target || !fig.animate) return null;
      var first = fig.getBoundingClientRect();
      var last = target.getBoundingClientRect();
      if (!last.width || !last.height) return null;
      fig.style.position = 'fixed';
      fig.style.left = first.left + 'px';
      fig.style.top = first.top + 'px';
      fig.style.width = first.width + 'px';
      fig.style.height = first.height + 'px';
      fig.style.transformOrigin = 'top left';
      fig.style.zIndex = '100001';
      document.body.appendChild(fig); // out of the wiping overlay
      var anim = fig.animate(
        [{ transform: 'translate(0,0) scale(1,1)' },
         { transform: 'translate(' + (last.left - first.left) + 'px,' +
           (last.top - first.top) + 'px) scale(' +
           (last.width / first.width) + ',' + (last.height / first.height) + ')' }],
        { duration: s.durReveal, easing: s.ease, fill: 'forwards' }
      );
      anim.onfinish = function () {
        if (fig.parentNode) fig.parentNode.removeChild(fig);
      };
      return anim;
    }

    // The exit: hold the 100 for one base beat, then the inset wipe (the
    // clip-path collapses bottom-up) with the optional Flip riding alongside.
    function exit() {
      setStep(steps);
      if (!loader.animate) { finalize(); return; }
      var s = styles();
      global.setTimeout(function () {
        if (state.done) return;
        var flip = flipPlate(s);
        if (flip) state.anims.push(flip);
        var wipe = loader.animate(
          [{ clipPath: 'inset(0 0 0 0)' }, { clipPath: 'inset(0 0 100% 0)' }],
          { duration: s.durReveal, easing: s.ease, fill: 'forwards' }
        );
        state.anims.push(wipe);
        wipe.onfinish = finalize;
      }, s.durBase);
    }

    // The ratchet: floor(p * steps) on a flat clock — value only ever jumps
    // (no easing inside a step). The last step is gated on the real load.
    var start = 0;
    function tick(now) {
      if (!start) start = now;
      var p = Math.min(1, (now - start) / minDuration);
      var step = Math.min(steps - 1, Math.floor(p * steps));
      setStep(step);
      if (p >= 1 && loaded) { state.raf = 0; exit(); return; }
      state.raf = global.requestAnimationFrame(tick);
    }
    state.raf = global.requestAnimationFrame(tick);

    var handle = {
      destroy: function () {
        if (state.raf) { global.cancelAnimationFrame(state.raf); state.raf = 0; }
        state.anims.forEach(function (a) { a.cancel(); });
        state.anims = [];
        global.removeEventListener('load', onLoad);
        document.body.style.overflow = prevOverflow;
        if (fig && fig.parentNode === document.body) {
          fig.removeAttribute('style');
          loader.insertBefore(fig, loader.firstChild);
        }
        loader.classList.remove('ad-stepped');
        loader.removeAttribute('aria-busy');
        loader.removeAttribute('aria-hidden');
        loader.removeAttribute('data-ad-near');
        loader.removeAttribute('data-ad-done');
        if (countEl) countEl.textContent = countText0;
        if (hadHidden) loader.setAttribute('hidden', '');
        else loader.removeAttribute('hidden');
        delete loader.__adSteppedLoader;
        var st = document.getElementById(CSS_ID);
        if (st && st.parentNode) st.parentNode.removeChild(st);
      }
    };
    state.handle = handle;
    return handle;
  }

  global.awardSteppedCounterLoader = { init: init };
})(typeof window !== 'undefined' ? window : this);
