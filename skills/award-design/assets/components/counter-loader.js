/*
 * counter-loader — numeric counter preloader (winners: Terminal Industries,
 * Bruno Simon, Depo Luxe). A full-viewport overlay whose mono count rolls
 * 0→100 as the page loads — the brand's first beat. Authored `hidden` and
 * un-hidden by JS, so no-JS or a dead script never blocks the page (the
 * gated-splash law). The roll stays honest: it eases toward 90 over
 * `minDuration`, holds until the real window `load`, then settles to 100 and
 * the overlay wipes up off the viewport. From 90 the count recolors to the
 * accent. Body scroll is locked only while the overlay is visible.
 * reduced-motion skips the loader entirely — no roll, no wipe, onDone fires.
 *
 * Expected markup — authored `hidden`; JS un-hides and runs it:
 *   <div data-ad-loader hidden><span data-ad-loader-count>0</span></div>
 *
 * Usage:  awardCounterLoader.init(root, { selector, minDuration, sessionOnce, onDone })
 *   root         Element|Document  scope (default document)
 *   selector     string    the overlay (default '[data-ad-loader]')
 *   minDuration  ms        floor for the 0→90 roll (default 1400)
 *   sessionOnce  boolean   skip after the first completed run this session
 *                          (default false; sessionStorage)
 *   onDone       function  run once after the lift — start the hero here. Also
 *                          fires immediately when the loader is skipped
 *                          (reduced-motion, sessionOnce), so the first beat
 *                          never depends on the roll having played.
 * Returns { destroy() }. Idempotent — while rolling it returns the live handle;
 * once done (or skipped) a re-init is a no-op. destroy() cancels the roll and
 * lift, restores `hidden` + body scroll + the authored count text, and removes
 * the stylesheet.
 *
 * Tokens: --ad-ground (oklch(14% 0.01 260)) + --ad-ink (oklch(96% 0 0)) paint
 * the overlay; --ad-font-mono sets the count; --ad-accent recolors it from 90;
 * --ad-dur-base (420ms) times the 90→100 settle; --ad-dur-reveal (800ms) +
 * --ad-ease-signature (cubic-bezier(.16,1,.3,1)) time the lift.
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-counter-loader-css';
  var SEEN_KEY = 'ad-counter-loader-done';

  var reduce = function () {
    return global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches;
  };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    // Scoped under .ad-loader — the class JS adds after removing `hidden`.
    // No-JS never gets the class, so the UA `[hidden]` display:none stands.
    s.textContent =
      '.ad-loader{position:fixed;inset:0;z-index:100000;display:flex;' +
        'align-items:center;justify-content:center;' +
        'background:var(--ad-ground,oklch(14% 0.01 260));' +
        'color:var(--ad-ink,oklch(96% 0 0));will-change:transform;}' +
      '.ad-loader[data-ad-done]{display:none;}' +
      '.ad-loader [data-ad-loader-count]{' +
        'font-family:var(--ad-font-mono,ui-monospace,monospace);' +
        'font-size:clamp(3rem,10vw,8rem);line-height:1;' +
        'font-variant-numeric:tabular-nums;' +
        'transition:color var(--ad-dur-base,420ms) ' +
        'var(--ad-ease-signature,cubic-bezier(.16,1,.3,1));}' +
      '.ad-loader[data-ad-near] [data-ad-loader-count]{' +
        'color:var(--ad-accent,oklch(62% 0.2 25));}';
    document.head.appendChild(s);
  }

  function styles() {
    var cs = getComputedStyle(document.documentElement);
    function v(name, fallback) {
      return (cs.getPropertyValue(name) || '').trim() || fallback;
    }
    return {
      durReveal: v('--ad-dur-reveal', '800ms'),
      durBase: v('--ad-dur-base', '420ms'),
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

  function easeOutCubic(p) { return 1 - Math.pow(1 - p, 3); }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-loader]';
    var minDuration = opts.minDuration != null ? opts.minDuration : 1400;
    var sessionOnce = !!opts.sessionOnce;
    var onDone = typeof opts.onDone === 'function' ? opts.onDone : null;

    var loader = root.querySelector(selector);
    if (!loader) return { destroy: function () {} };

    // Idempotent: done → no-op; still rolling → the live handle (no rebind).
    var prev = loader.__adCounterLoader;
    if (prev) return prev.done ? { destroy: function () {} } : prev.handle;

    // Skip paths — the overlay keeps its authored `hidden`, the page just shows.
    if (reduce() || (sessionOnce && seen())) {
      var skipState = { done: true, handle: null };
      loader.__adCounterLoader = skipState; // a re-init must not re-fire onDone
      skipState.handle = { destroy: function () { delete loader.__adCounterLoader; } };
      if (onDone) onDone();
      return skipState.handle;
    }

    injectCss();
    var countEl = loader.querySelector('[data-ad-loader-count]');
    var countText0 = countEl ? countEl.textContent : '';
    var hadHidden = loader.hasAttribute('hidden');
    var prevOverflow = document.body.style.overflow;
    var state = { done: false, raf: 0, anim: null, handle: null };
    loader.__adCounterLoader = state;

    var loaded = document.readyState === 'complete';
    function onLoad() { loaded = true; }
    if (!loaded) global.addEventListener('load', onLoad);

    // Open: un-hide, promote to the JS-only class, announce busy, lock scroll.
    loader.removeAttribute('hidden');
    loader.classList.add('ad-loader');
    loader.setAttribute('aria-busy', 'true');
    document.body.style.overflow = 'hidden';

    var lastShown = -1;
    function setCount(v) {
      var n = Math.round(v);
      if (n === lastShown) return; // write only on change — no per-frame paint at hold
      lastShown = n;
      if (countEl) countEl.textContent = String(n);
      if (n >= 90) loader.setAttribute('data-ad-near', '');
    }

    function finalize() {
      state.anim = null;
      state.done = true;
      global.removeEventListener('load', onLoad);
      document.body.style.overflow = prevOverflow;
      loader.removeAttribute('aria-busy');
      loader.setAttribute('aria-hidden', 'true');
      loader.setAttribute('data-ad-done', ''); // → display:none
      markSeen();
      if (onDone) onDone();
    }

    function lift() {
      setCount(100);
      if (reduce() || !loader.animate) { finalize(); return; }
      var s = styles();
      state.anim = loader.animate(
        [{ transform: 'translateY(0)' }, { transform: 'translateY(-100%)' }],
        { duration: parseFloat(s.durReveal), easing: s.ease, fill: 'forwards' }
      );
      state.anim.onfinish = finalize;
    }

    // Roll: ease 0→90 over minDuration; hold at 90 until the real load; then a
    // short --ad-dur-base settle to 100 and the lift. rAF stops in background
    // tabs on its own; the roll is clock-based so it stays honest on return.
    var start = 0;
    var settle = null;
    function tick(now) {
      if (!start) start = now;
      if (settle) {
        var q = Math.min(1, (now - settle.t0) / settle.dur);
        setCount(90 + 10 * q);
        if (q >= 1) { state.raf = 0; lift(); return; }
      } else {
        var p = Math.min(1, (now - start) / minDuration);
        setCount(easeOutCubic(p) * 90);
        if (p >= 1 && loaded) {
          settle = { t0: now, dur: parseFloat(styles().durBase) || 420 };
        }
      }
      state.raf = global.requestAnimationFrame(tick);
    }
    state.raf = global.requestAnimationFrame(tick);

    var handle = {
      destroy: function () {
        if (state.raf) { global.cancelAnimationFrame(state.raf); state.raf = 0; }
        if (state.anim) { state.anim.cancel(); state.anim = null; }
        global.removeEventListener('load', onLoad);
        document.body.style.overflow = prevOverflow;
        loader.classList.remove('ad-loader');
        loader.removeAttribute('aria-busy');
        loader.removeAttribute('aria-hidden');
        loader.removeAttribute('data-ad-near');
        loader.removeAttribute('data-ad-done');
        if (countEl) countEl.textContent = countText0;
        if (hadHidden) loader.setAttribute('hidden', '');
        else loader.removeAttribute('hidden');
        delete loader.__adCounterLoader;
        var st = document.getElementById(CSS_ID);
        if (st && st.parentNode) st.parentNode.removeChild(st);
      }
    };
    state.handle = handle;
    return handle;
  }

  global.awardCounterLoader = { init: init };
})(typeof window !== 'undefined' ? window : this);
