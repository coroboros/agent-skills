/*
 * loader-into-navbar — progress-becomes-UI (winner: Eloy Benoffi; the thin
 * primary-fill bar pinned to the hero top is winner-verified, the
 * becomes-navbar hand-off is single-source). The studio-index loader: the nav
 * element ITSELF is the loading bar — armed, it rides up out of view leaving
 * only its bottom sliver at the viewport top, and an accent fill in that
 * sliver tracks the real load left→right; on complete the bar GROWS INTO the
 * navbar (the nav drops to its full height, its content fades up, the fill
 * dissolves) — the watched element becomes furniture, never a discarded
 * overlay. Single-source by construction: one element plays bar and navbar.
 * The fill stays honest: it eases toward 90% over `minDuration`, holds until
 * the real window `load`, then settles to full and the arrival plays. The
 * page behind stays painted (the pre-composed-fold trick) — this is a bar
 * over the hero, not a blackout.
 *
 * Content-visible at rest: the nav is authored VISIBLE (never `hidden` — a
 * nav must survive no-JS), and the armed state exists only under the JS-set
 * data-ad-navload-armed attribute. Mount the init call right after the nav
 * element so the armed state lands before first paint. The nav is expected at
 * the top of the page (its natural place); the component only transforms it.
 *
 * Expected markup — the builder's real nav, styled by the build:
 *   <header data-ad-navloader> … nav content … </header>
 *
 * Usage:  awardLoaderIntoNavbar.init(root, opts)
 *   root         Element|Document  scope (default document)
 *   selector     string    the nav (default '[data-ad-navloader]')
 *   minDuration  ms        floor for the 0→90% fill (default 1400)
 *   sessionOnce  boolean   skip after the first completed run this session
 *   onDone       function  runs once after the nav lands — start the hero
 *                          here. Also fires immediately on the skip paths
 *                          (reduced-motion, sessionOnce), so the first beat
 *                          never depends on the fill having played.
 * Returns { destroy() }. Idempotent — while filling it returns the live
 * handle; once done (or skipped) a re-init is a no-op. destroy() cancels the
 * fill and arrival, removes the fill element + armed state + body scroll
 * lock, and removes the stylesheet.
 *
 * Tokens: --ad-accent paints the fill; --ad-navload-bar sets the sliver
 * height (default 3px); --ad-dur-reveal (800ms) + --ad-ease-signature
 * (cubic-bezier(.16,1,.3,1)) time the drop; --ad-dur-base (420ms) times the
 * settle and the content fade.
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-loader-into-navbar-css';
  var SEEN_KEY = 'ad-loader-into-navbar-done';

  var reduce = function () {
    return global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches;
  };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      // armed: the nav rides up leaving its bottom sliver — the bar IS the nav
      '[data-ad-navload-armed]{' +
        'transform:translateY(calc(-100% + var(--ad-navload-bar,3px)));' +
        'will-change:transform;}' +
      '[data-ad-navload-armed]>:not(.ad-navload__fill){opacity:0;}' +
      '.ad-navload__fill{position:absolute;left:0;bottom:0;width:100%;' +
        'height:var(--ad-navload-bar,3px);' +
        'background:var(--ad-accent,oklch(62% 0.2 25));' +
        'transform:scaleX(0);transform-origin:left;will-change:transform;' +
        'pointer-events:none;}';
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

  function easeOutCubic(p) { return 1 - Math.pow(1 - p, 3); }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-navloader]';
    var minDuration = opts.minDuration != null ? opts.minDuration : 1400;
    var sessionOnce = !!opts.sessionOnce;
    var onDone = typeof opts.onDone === 'function' ? opts.onDone : null;

    var nav = root.querySelector(selector);
    if (!nav) return { destroy: function () {} };

    // Idempotent: done → no-op; still filling → the live handle (no rebind).
    var prev = nav.__adNavLoader;
    if (prev) return prev.done ? { destroy: function () {} } : prev.handle;

    // Skip paths — the nav simply rests in its authored, visible state.
    if (reduce() || (sessionOnce && seen())) {
      var skipState = { done: true, handle: null };
      nav.__adNavLoader = skipState; // a re-init must not re-fire onDone
      skipState.handle = { destroy: function () { delete nav.__adNavLoader; } };
      if (onDone) onDone();
      return skipState.handle;
    }

    injectCss();
    var prevPosition = nav.style.position;
    var prevOverflow = document.body.style.overflow;
    var state = { done: false, raf: 0, anims: [], handle: null };
    nav.__adNavLoader = state;

    var loaded = document.readyState === 'complete';
    function onLoad() { loaded = true; }
    if (!loaded) global.addEventListener('load', onLoad);

    // Arm: ride the nav up to its sliver, mount the fill, lock scroll while
    // the bar is the only UI. The fill is component chrome, aria-hidden.
    if (getComputedStyle(nav).position === 'static') nav.style.position = 'relative';
    nav.setAttribute('data-ad-navload-armed', '');
    nav.setAttribute('aria-busy', 'true');
    document.body.style.overflow = 'hidden';
    var fill = document.createElement('i');
    fill.className = 'ad-navload__fill';
    fill.setAttribute('aria-hidden', 'true');
    nav.appendChild(fill);

    function setFill(q) {
      fill.style.transform = 'scaleX(' + q + ')';
    }

    function finalize() {
      // un-arming restores the natural state the filled animations ended on,
      // so the anims can be released instead of held forwards forever
      nav.removeAttribute('data-ad-navload-armed');
      state.anims.forEach(function (a) { a.cancel(); });
      state.anims = [];
      state.done = true;
      global.removeEventListener('load', onLoad);
      document.body.style.overflow = prevOverflow;
      nav.removeAttribute('aria-busy');
      if (fill.parentNode) fill.parentNode.removeChild(fill);
      markSeen();
      if (onDone) onDone();
    }

    // The arrival: the bar grows into the navbar — the nav drops to its full
    // height while its content fades up and the spent fill dissolves.
    function arrive() {
      setFill(1);
      if (!nav.animate) { finalize(); return; }
      var s = styles();
      var drop = nav.animate(
        [{ transform: 'translateY(calc(-100% + var(--ad-navload-bar,3px)))' },
         { transform: 'translateY(0)' }],
        { duration: s.durReveal, easing: s.ease, fill: 'forwards' }
      );
      state.anims.push(drop);
      Array.prototype.forEach.call(nav.children, function (child) {
        if (child === fill || !child.animate) return;
        state.anims.push(child.animate(
          [{ opacity: 0 }, { opacity: 1 }],
          { duration: s.durBase, easing: s.ease, fill: 'forwards',
            delay: s.durReveal * 0.5 }
        ));
      });
      state.anims.push(fill.animate(
        [{ opacity: 1 }, { opacity: 0 }],
        { duration: s.durBase, easing: 'linear', fill: 'forwards',
          delay: s.durReveal * 0.5 }
      ));
      drop.onfinish = function () {
        // let the content fade land before the attribute flip snaps opacity
        global.setTimeout(finalize, styles().durBase);
      };
    }

    // The fill: ease 0→0.9 over minDuration; hold at 0.9 until the real load;
    // then a short settle to 1 and the arrival. Writes are transform-only.
    var start = 0;
    var settle = null;
    function tick(now) {
      if (!start) start = now;
      if (settle) {
        var q = Math.min(1, (now - settle.t0) / settle.dur);
        setFill(0.9 + 0.1 * q);
        if (q >= 1) { state.raf = 0; arrive(); return; }
      } else {
        var p = Math.min(1, (now - start) / minDuration);
        setFill(easeOutCubic(p) * 0.9);
        if (p >= 1 && loaded) settle = { t0: now, dur: styles().durBase };
      }
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
        nav.removeAttribute('data-ad-navload-armed');
        nav.removeAttribute('aria-busy');
        nav.style.position = prevPosition;
        if (fill.parentNode) fill.parentNode.removeChild(fill);
        delete nav.__adNavLoader;
        var st = document.getElementById(CSS_ID);
        if (st && st.parentNode) st.parentNode.removeChild(st);
      }
    };
    state.handle = handle;
    return handle;
  }

  global.awardLoaderIntoNavbar = { init: init };
})(typeof window !== 'undefined' ? window : this);
