/*
 * flip-handoff-loader — the master-preloader whose logo FLIPs into the header
 * (winner: Son Daven — SOTD Jun 5 2026, 7.62 + Developer Award 8.09; the
 * master-preloader scene → 'logo Flips into the header' hook is
 * winner-verified, interior numbers are executable defaults). A full-viewport
 * scene carries the builder's wordmark center-stage over an honest progress
 * hairline; on completion the SAME mark travels — First/Last/Invert/Play —
 * from center-stage into the header's real wordmark slot while the scene
 * ground dissolves, so the loader's watched element BECOMES the page's brand
 * mark with no hard cut. Ruled distinct, not an alias: loader-into-navbar
 * (Eloy Benoffi) makes the NAV ITSELF the progress bar that grows into the
 * navbar — nothing travels; branded-preloader recedes in place — no element
 * continuity into the chrome. Here the continuity IS the traveling mark.
 * The fill stays honest (the library's loader law): it eases toward 90% over
 * `minDuration`, holds until the real window `load`, then settles to full
 * and the FLIP plays.
 *
 * Content-visible at rest: the scene is authored `hidden` (a dead script
 * never blocks the page), and the header wordmark is authored VISIBLE — JS
 * hides it only for the flight via [data-ad-flip-wait], so no-JS shows the
 * ordinary header. Reduced motion: the scene never shows — the header
 * wordmark stands and onDone fires immediately (the loader-into-navbar skip
 * path; the beat is stylistic, never load-bearing).
 *
 * Expected markup — the builder authors BOTH marks in the same face/size
 * grammar (the flight scales between their real rects):
 *   <div data-ad-flip-loader hidden>
 *     <div data-flip-mark>MAISON</div>
 *   </div>
 *   <header>… <a href="/" data-ad-flip-target>MAISON</a> …</header>
 *
 * Usage:  awardFlipHandoffLoader.init(root, opts)
 *   root         Element|Document  scope (default document)
 *   selector     string    the scene (default '[data-ad-flip-loader]')
 *   target       string    the header mark (default '[data-ad-flip-target]')
 *   minDuration  ms        floor for the 0→90% fill (default 1600)
 *   sessionOnce  boolean   skip after the first completed run this session
 *   onDone       function  runs once after the mark lands — start the hero
 *                          here. Fires on every skip path too, so the first
 *                          beat never depends on the flight having played.
 * Returns { destroy() }. Idempotent — while running it returns the live
 * handle; once done (or skipped) a re-init is a no-op. destroy() cancels the
 * fill and flight, restores the scene's `hidden`, the target, and the body
 * scroll lock, and removes the stylesheet.
 *
 * A11y + perf: the scene announces aria-busy with a real progressbar; the
 * flight is transform + opacity only (translate + uniform scale between the
 * two measured rects — compositor-clean); scroll is locked only while the
 * scene is the only UI. No target on the page → the scene simply recedes in
 * place (never a stranded overlay).
 *
 * Tokens: --ad-ground + --ad-ink paint the scene and mark; --ad-ground-2
 * the progress track; --ad-accent the fill; --ad-font-display the mark;
 * --ad-dur-reveal + --ad-ease-signature time the flight and dissolve;
 * --ad-dur-base the settle.
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-flip-handoff-loader-css';
  var SEEN_KEY = 'ad-flip-handoff-loader-done';

  var reduce = function () {
    return !!(global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches);
  };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    // Scoped under .ad-fhl — the class JS adds after removing `hidden`;
    // no-JS never gets the class, so nothing at rest covers the page.
    s.textContent =
      '.ad-fhl{position:fixed;inset:0;z-index:100000;display:grid;' +
      'place-items:center;color:var(--ad-ink,oklch(96% 0 0));overflow:hidden;}' +
      // the ground is its own layer so the dissolve is an opacity fade under
      // the flight — compositor-only, never a backgroundColor paint
      '.ad-fhl__ground{position:absolute;inset:0;' +
      'background:var(--ad-ground,oklch(14% 0.01 260));will-change:opacity;}' +
      '.ad-fhl [data-flip-mark]{position:relative;' +
      'font-family:var(--ad-font-display,inherit);' +
      'line-height:1;will-change:transform;transform-origin:top left;}' +
      '.ad-fhl__bar{position:absolute;left:50%;bottom:14svh;' +
      'transform:translateX(-50%);width:min(32vw,18rem);height:1px;' +
      'background:var(--ad-ground-2,oklch(18% 0.01 260));overflow:hidden;}' +
      '.ad-fhl__fill{position:absolute;inset:0;transform:scaleX(0);' +
      'transform-origin:left;background:var(--ad-accent,oklch(62% 0.2 25));' +
      'will-change:transform;}' +
      // the header mark waits out the flight — JS-applied, so no-JS keeps
      // the header whole
      '[data-ad-flip-wait]{visibility:hidden;}';
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
    var selector = opts.selector || '[data-ad-flip-loader]';
    var targetSel = opts.target || '[data-ad-flip-target]';
    var minDuration = opts.minDuration != null ? opts.minDuration : 1600;
    var sessionOnce = !!opts.sessionOnce;
    var onDone = typeof opts.onDone === 'function' ? opts.onDone : null;

    var scene = root.querySelector(selector);
    if (!scene) return { destroy: function () {} };
    var mark = scene.querySelector('[data-flip-mark]');
    var target = root.querySelector(targetSel);

    // Idempotent: done → no-op; still running → the live handle (no rebind).
    var prev = scene.__adFlipHandoff;
    if (prev) return prev.done ? { destroy: function () {} } : prev.handle;

    // Skip paths — the header wordmark simply stands in its authored state.
    if (reduce() || (sessionOnce && seen())) {
      var skipState = { done: true, handle: null };
      scene.__adFlipHandoff = skipState; // a re-init must not re-fire onDone
      skipState.handle = { destroy: function () { delete scene.__adFlipHandoff; } };
      if (onDone) onDone();
      return skipState.handle;
    }

    injectCss();
    var prevOverflow = document.body.style.overflow;
    var state = { done: false, removed: false, raf: 0, anims: [], handle: null };
    scene.__adFlipHandoff = state;

    var loaded = document.readyState === 'complete';
    function onLoad() { loaded = true; }
    if (!loaded) global.addEventListener('load', onLoad);

    // Open: un-hide, promote, hold the header mark for the hand-off,
    // lock scroll while the scene is the only UI.
    scene.removeAttribute('hidden');
    scene.classList.add('ad-fhl');
    scene.setAttribute('aria-busy', 'true');
    if (target) target.setAttribute('data-ad-flip-wait', '');
    document.body.style.overflow = 'hidden';

    var ground = document.createElement('div');
    ground.className = 'ad-fhl__ground';
    ground.setAttribute('aria-hidden', 'true');
    scene.insertBefore(ground, scene.firstChild);

    var bar = document.createElement('div');
    bar.className = 'ad-fhl__bar';
    bar.setAttribute('role', 'progressbar');
    bar.setAttribute('aria-label', 'Loading');
    bar.setAttribute('aria-valuemin', '0');
    bar.setAttribute('aria-valuemax', '100');
    bar.setAttribute('aria-valuenow', '0');
    var fill = document.createElement('span');
    fill.className = 'ad-fhl__fill';
    fill.setAttribute('aria-hidden', 'true');
    bar.appendChild(fill);
    scene.appendChild(bar);

    var lastShown = -1;
    function setFill(q) {
      fill.style.transform = 'scaleX(' + q + ')';
      var n = Math.round(q * 100);
      if (n !== lastShown) { lastShown = n; bar.setAttribute('aria-valuenow', String(n)); }
    }

    function finalize() {
      state.anims.forEach(function (a) { a.cancel(); });
      state.anims = [];
      state.done = true;
      global.removeEventListener('load', onLoad);
      document.body.style.overflow = prevOverflow;
      if (target) target.removeAttribute('data-ad-flip-wait');
      if (scene.parentNode) scene.parentNode.removeChild(scene);
      state.removed = true;
      markSeen();
      if (onDone) onDone();
    }

    // The FLIP: measure the mark where it stands (First) and the header slot
    // (Last), then Play translate + uniform scale between the two real rects
    // while the scene ground dissolves underneath the flight.
    function flip() {
      setFill(1);
      if (!scene.animate || !mark) { finalize(); return; }
      var s = styles();
      if (target && mark) {
        var first = mark.getBoundingClientRect();
        var last = target.getBoundingClientRect();
        var scale = first.width > 0 ? last.width / first.width : 1;
        var dx = last.left - first.left;
        var dy = last.top - first.top;
        state.anims.push(mark.animate(
          [{ transform: 'translate(0,0) scale(1)' },
           { transform: 'translate(' + dx.toFixed(1) + 'px,' + dy.toFixed(1) + 'px) ' +
             'scale(' + scale.toFixed(4) + ')' }],
          { duration: s.durReveal, easing: s.ease, fill: 'forwards' }
        ));
      }
      // the ground and the spent bar dissolve under the flight — the page is
      // already painted beneath, never a blackout hand-off
      var dissolve = ground.animate(
        [{ opacity: 1 }, { opacity: 0 }],
        { duration: s.durReveal, easing: s.ease, fill: 'forwards' }
      );
      state.anims.push(dissolve);
      state.anims.push(bar.animate(
        [{ opacity: 1 }, { opacity: 0 }],
        { duration: s.durBase, easing: 'linear', fill: 'forwards' }
      ));
      dissolve.onfinish = function () {
        // the landed mark swaps for the real header wordmark on the same frame
        finalize();
      };
    }

    // The fill: ease 0→0.9 over minDuration; hold at 0.9 until the real
    // load; then a short settle to 1 and the flight. Transform-only writes.
    var start = 0;
    var settle = null;
    function tick(now) {
      if (!start) start = now;
      if (settle) {
        var q = Math.min(1, (now - settle.t0) / settle.dur);
        setFill(0.9 + 0.1 * q);
        if (q >= 1) { state.raf = 0; flip(); return; }
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
        if (target) target.removeAttribute('data-ad-flip-wait');
        if (!state.removed && scene.parentNode) {
          scene.classList.remove('ad-fhl');
          scene.removeAttribute('aria-busy');
          if (bar.parentNode) bar.parentNode.removeChild(bar);
          if (ground.parentNode) ground.parentNode.removeChild(ground);
          scene.setAttribute('hidden', '');
        }
        delete scene.__adFlipHandoff;
        var st = document.getElementById(CSS_ID);
        if (st && st.parentNode) st.parentNode.removeChild(st);
      }
    };
    state.handle = handle;
    return handle;
  }

  global.awardFlipHandoffLoader = { init: init };
})(typeof window !== 'undefined' ? window : this);
