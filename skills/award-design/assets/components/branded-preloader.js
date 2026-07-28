/*
 * branded-preloader — the designed first-load state (winners: Lando Norris
 * "Load Norris" in-brand loader; Messenger's 5.7MB Three.js init gate; Oryzo /
 * Cartier / ERA heavy WebGL scenes). The immersive medium is the most
 * asset-heavy of all, so the load screen is the first impression, never a
 * spinner: a full-viewport overlay carrying the brand's own mark whose progress
 * is tied to REAL asset loading (0->1), handed off to the hero with a reveal —
 * not a hard cut. Authored `hidden` and un-hidden by JS, so no-JS or a dead
 * script never blocks the page (the gated-splash law). Rhymes with
 * curtain-transition: the loader's exit reveal and the curtain's wipe are the
 * same cover-and-hand-off grammar.
 *
 * Progress stays honest: the real load fraction on one axis, a time-eased floor
 * (opts.min) on the other, and the bar shows the SLOWER of the two — a fast load
 * still fills over the floor (never a flash), a slow load never runs ahead of
 * the bytes. Sources combine: opts.assets (count-based), opts.track (a Three.js
 * LoadingManager-like { onProgress } adapter, one fractional unit), opts.fonts
 * (document.fonts.ready, one unit). When opts.enter is set the filled loader
 * becomes an ENTER gate whose gesture unlocks audio (autoplay policy needs a
 * user gesture); onComplete then reports { userGesture: true }.
 *
 * Expected markup — authored `hidden`; JS un-hides and runs it. The component
 * never invents the mark; the builder authors it (and an optional counter):
 *   <div data-ad-preloader hidden>
 *     <div data-preloader-mark><!-- brand motif: wordmark / monogram / logo --></div>
 *     <span data-preloader-counter>0</span>   <!-- optional numeric readout -->
 *   </div>
 *
 * Usage:  awardBrandedPreloader.init(root, opts)
 *   root            Element|Document  scope (default document)
 *   opts.selector   string    the overlay (default '[data-ad-preloader]')
 *   opts.assets     string[]  URLs to preload — images via Image(), the rest via
 *                             fetch; each is one unit of count-based progress. A
 *                             failed asset still counts (the loader never hangs).
 *   opts.track      object    { onProgress(cb) } — a LoadingManager-like source;
 *                             cb(p) reports 0->1 for one fractional unit.
 *   opts.fonts      boolean   true folds document.fonts.ready in as one unit.
 *   opts.min        ms        time-eased floor for the beat (default 600).
 *   opts.enter      false | { label }  when set, at progress 1 the loader becomes
 *                             a focusable ENTER button (label); completion waits
 *                             for the gesture and onComplete gets userGesture:true.
 *   opts.onComplete function  runs once after the exit reveal, with { userGesture }.
 * Returns { destroy() }. Idempotent — while loading it returns the live handle;
 * once complete (overlay removed) a re-init is a no-op. destroy() cancels the
 * roll and the exit, restores the overlay's authored `hidden` + body scroll (or,
 * if the exit already removed the overlay, just unwinds scroll + listeners), and
 * removes the stylesheet.
 *
 * Tokens: --ad-ground + --ad-ink paint the overlay and mark; --ad-ground-2 the
 * progress track; --ad-accent the fill, the near-complete recolor, and the ENTER
 * hover; --ad-font-display sets the mark, --ad-font-mono the counter and label;
 * --ad-dur-reveal + --ad-ease-signature time the exit; --ad-dur-base the counter
 * and control transitions. reduced-motion: a static branded frame, the counter
 * and bar snap (no roll), and an instant hand-off (no exit choreography).
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-branded-preloader-css';
  // Tab-reachable focusables — used to trap focus while the ENTER gate is up.
  var FOCUSABLE = 'a[href],area[href],button:not([disabled]),input:not([disabled]),' +
    'select:not([disabled]),textarea:not([disabled]),iframe,' +
    '[tabindex]:not([tabindex="-1"]),[contenteditable="true"]';

  var reduce = function () {
    return global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches;
  };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    // Every rule is scoped under .ad-preloader — the class JS adds after removing
    // `hidden`. No-JS never gets the class, so the UA `[hidden]` display:none
    // stands and the page shows with no overlay (nothing at rest hides the page).
    s.textContent =
      '.ad-preloader{position:fixed;inset:0;z-index:100000;display:flex;' +
        'flex-direction:column;align-items:center;justify-content:center;gap:2rem;' +
        'padding:8vmin;background:var(--ad-ground,oklch(14% 0.01 260));' +
        'color:var(--ad-ink,oklch(96% 0 0));overflow:hidden;' +
        'will-change:transform,opacity;}' +
      '.ad-preloader [data-preloader-mark]{font-family:var(--ad-font-display,inherit);' +
        'line-height:1;text-align:center;}' +
      '.ad-preloader [data-preloader-counter]{' +
        'font-family:var(--ad-font-mono,ui-monospace,monospace);' +
        'font-variant-numeric:tabular-nums;font-size:.8rem;letter-spacing:.2em;opacity:.7;' +
        'transition:color var(--ad-dur-base,420ms) ' +
        'var(--ad-ease-signature,cubic-bezier(.16,1,.3,1));}' +
      '.ad-preloader[data-ad-near] [data-preloader-counter]{' +
        'color:var(--ad-accent,oklch(62% 0.2 25));}' +
      // Component-owned chrome: the progress track + fill (where a spinner would
      // sit). scaleX rides a CSS var the roll writes each frame — compositor-only.
      '.ad-preloader [data-ad-preloader-bar]{position:relative;width:min(38vw,22rem);' +
        'height:2px;background:var(--ad-ground-2,oklch(18% 0.01 260));overflow:hidden;}' +
      '.ad-preloader [data-ad-preloader-fill]{position:absolute;inset:0;' +
        'transform-origin:left center;transform:scaleX(var(--ad-preloader-progress,0));' +
        'background:var(--ad-accent,oklch(62% 0.2 25));will-change:transform;}' +
      // ENTER gate: inert and invisible until the loader completes with opts.enter.
      '.ad-preloader [data-ad-preloader-enter]{opacity:0;pointer-events:none;cursor:pointer;' +
        'color:inherit;font-family:var(--ad-font-mono,ui-monospace,monospace);font-size:.8rem;' +
        'letter-spacing:.18em;text-transform:uppercase;background:transparent;' +
        'border:1px solid currentColor;border-radius:0;padding:1em 2.4em;' +
        'transition:opacity var(--ad-dur-base,420ms) var(--ad-ease-signature,cubic-bezier(.16,1,.3,1)),' +
        'color var(--ad-dur-base,420ms) var(--ad-ease-signature,cubic-bezier(.16,1,.3,1)),' +
        'background-color var(--ad-dur-base,420ms) var(--ad-ease-signature,cubic-bezier(.16,1,.3,1)),' +
        'border-color var(--ad-dur-base,420ms) var(--ad-ease-signature,cubic-bezier(.16,1,.3,1));}' +
      '.ad-preloader[data-ad-enter-ready] [data-ad-preloader-enter]{opacity:1;pointer-events:auto;}' +
      '.ad-preloader [data-ad-preloader-enter]:hover,' +
      '.ad-preloader [data-ad-preloader-enter]:focus-visible{' +
        'background:var(--ad-accent,oklch(62% 0.2 25));border-color:var(--ad-accent,oklch(62% 0.2 25));' +
        'color:var(--ad-ground,oklch(14% 0.01 260));}' +
      '@media (prefers-reduced-motion: reduce){' +
        '.ad-preloader [data-preloader-counter],' +
        '.ad-preloader [data-ad-preloader-enter]{transition:none;}}';
    document.head.appendChild(s);
  }

  function styles() {
    var cs = getComputedStyle(document.documentElement);
    function v(name, fallback) {
      return (cs.getPropertyValue(name) || '').trim() || fallback;
    }
    return {
      durReveal: v('--ad-dur-reveal', '800ms'),
      ease: v('--ad-ease-signature', 'cubic-bezier(.16,1,.3,1)')
    };
  }

  function isVisible(el) {
    // getClientRects (not offsetParent) — the overlay is position:fixed, whose
    // descendants report offsetParent null yet are on-screen.
    return !el.disabled && el.getClientRects().length > 0;
  }

  function focusablesIn(container) {
    var out = [];
    var list = container.querySelectorAll(FOCUSABLE);
    for (var i = 0; i < list.length; i++) {
      if (isVisible(list[i])) out.push(list[i]);
    }
    return out;
  }

  function isImage(url) {
    if (typeof url !== 'string') return false;
    if (url.indexOf('data:image') === 0) return true;
    return /\.(png|jpe?g|gif|webp|avif|svg|bmp|ico)(\?|#|$)/i.test(url);
  }

  function easeOutCubic(p) { return 1 - Math.pow(1 - p, 3); }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-preloader]';

    var overlay = root.querySelector(selector);
    if (!overlay) return { destroy: function () {} };

    // Idempotent: complete → no-op; still loading → the live handle (no rebind).
    var prev = overlay.__adBrandedPreloader;
    if (prev) return prev.done ? { destroy: function () {} } : prev.handle;

    var minMs = opts.min != null && opts.min > 0 ? opts.min : (opts.min === 0 ? 0 : 600);
    var enterOpt = opts.enter && typeof opts.enter === 'object' ? opts.enter : null;
    var onComplete = typeof opts.onComplete === 'function' ? opts.onComplete : null;

    injectCss();
    var counterEl = overlay.querySelector('[data-preloader-counter]');
    var counterText0 = counterEl ? counterEl.textContent : '';
    var hadHidden = overlay.hasAttribute('hidden');
    var prevOverflow = document.body.style.overflow;

    // Component-owned progress track + fill (the affordance that replaces a spinner).
    var bar = document.createElement('div');
    bar.setAttribute('data-ad-preloader-bar', '');
    bar.setAttribute('role', 'progressbar');
    bar.setAttribute('aria-label', 'Loading');
    bar.setAttribute('aria-valuemin', '0');
    bar.setAttribute('aria-valuemax', '100');
    bar.setAttribute('aria-valuenow', '0');
    var fill = document.createElement('span');
    fill.setAttribute('data-ad-preloader-fill', '');
    fill.setAttribute('aria-hidden', 'true');
    bar.appendChild(fill);
    overlay.appendChild(bar);

    // The ENTER control is created only when opts.enter is set — its label is the
    // sole content the component adds, and the API hands it in (never invented).
    var enterBtn = null;
    if (enterOpt) {
      enterBtn = document.createElement('button');
      enterBtn.type = 'button';
      enterBtn.setAttribute('data-ad-preloader-enter', '');
      enterBtn.textContent = enterOpt.label != null ? String(enterOpt.label) : 'Enter';
      overlay.appendChild(enterBtn);
    }

    var state = { done: false, removed: false, gate: false, raf: 0, anim: null,
      minTimer: 0, handle: null };
    overlay.__adBrandedPreloader = state;

    // Progress model: assets are whole units, the track a fractional unit, fonts a
    // whole unit. real = loaded / total, honest and monotonic (each term only rises).
    var assets = Array.isArray(opts.assets) ? opts.assets : [];
    var trackActive = !!(opts.track && typeof opts.track.onProgress === 'function');
    var fontsActive = opts.fonts === true && document.fonts && document.fonts.ready;
    var totalUnits = assets.length + (trackActive ? 1 : 0) + (fontsActive ? 1 : 0);
    var loadedUnits = 0;
    var trackProgress = 0;

    function realProgress() {
      if (totalUnits === 0) return 1;
      var p = (loadedUnits + trackProgress) / totalUnits;
      return p > 1 ? 1 : p;
    }

    var start = 0;
    var lastShown = -1;
    var minElapsed = false;

    function render(d) {
      overlay.style.setProperty('--ad-preloader-progress', String(d));
      var n = Math.round(d * 100);
      if (n === lastShown) return; // write text/aria only on integer change
      lastShown = n;
      if (counterEl) counterEl.textContent = String(n);
      bar.setAttribute('aria-valuenow', String(n));
      if (n >= 90) overlay.setAttribute('data-ad-near', '');
    }

    // reduced-motion has no roll — completion is event-driven: once real load is
    // in AND the floor has elapsed, snap to 100 and hand off.
    function checkDone() {
      if (state.done || state.gate) return;
      if (reduce() && minElapsed && realProgress() >= 1) { render(1); onLoaded(); }
    }

    function onLoaded() {
      if (state.done || state.gate) return;
      if (enterOpt) { openGate(); return; }
      exit(false);
    }

    // Motion path: show the slower of real load and the eased time floor, so a
    // fast load still fills over the floor and a slow load never outruns the bytes.
    function tick(now) {
      if (!start) start = now;
      var elapsed = now - start;
      var floor = minMs > 0 ? easeOutCubic(Math.min(1, elapsed / minMs)) : 1;
      var real = realProgress();
      var d = real < floor ? real : floor;
      render(d);
      if (real >= 1 && elapsed >= minMs) { state.raf = 0; onLoaded(); return; }
      state.raf = global.requestAnimationFrame(tick);
    }

    function trapKeydown(e) {
      if (e.key !== 'Tab' && e.keyCode !== 9) return;
      var f = focusablesIn(overlay);
      if (!f.length) { e.preventDefault(); return; }
      var first = f[0], last = f[f.length - 1];
      var active = document.activeElement;
      if (e.shiftKey) {
        if (active === first || !overlay.contains(active)) { e.preventDefault(); last.focus(); }
      } else {
        if (active === last || !overlay.contains(active)) { e.preventDefault(); first.focus(); }
      }
    }

    function openGate() {
      state.gate = true;
      render(1);
      overlay.removeAttribute('aria-busy');
      overlay.setAttribute('data-ad-enter-ready', '');
      document.addEventListener('keydown', trapKeydown, true);
      enterBtn.addEventListener('click', onActivate);
      enterBtn.focus();
    }

    // A native button dispatches click on pointer, Enter, and Space — one listener
    // covers all three; the gesture is what unlocks audio in onComplete.
    function onActivate() {
      if (state.done) return;
      enterBtn.removeEventListener('click', onActivate);
      document.removeEventListener('keydown', trapKeydown, true);
      exit(true);
    }

    function exit(userGesture) {
      if (state.done) return;
      state.done = true; // re-entrancy no-op from here
      if (state.raf) { global.cancelAnimationFrame(state.raf); state.raf = 0; }
      if (state.minTimer) { global.clearTimeout(state.minTimer); state.minTimer = 0; }
      var meta = { userGesture: !!userGesture };
      if (reduce() || !overlay.animate) { finish(meta); return; }
      var s = styles();
      // The exit reveal: the overlay recedes and fades to expose the hero beneath —
      // transform + opacity only (compositor-clean), never a hard cut.
      state.anim = overlay.animate(
        [{ opacity: 1, transform: 'scale(1)' },
         { opacity: 0, transform: 'scale(1.04)' }],
        { duration: parseFloat(s.durReveal), easing: s.ease, fill: 'forwards' }
      );
      state.anim.onfinish = function () { finish(meta); };
    }

    function finish(meta) {
      state.anim = null;
      // Drop focus off the ENTER control before the node leaves the DOM.
      if (document.activeElement === enterBtn && enterBtn && enterBtn.blur) enterBtn.blur();
      document.body.style.overflow = prevOverflow;
      if (overlay.parentNode) overlay.parentNode.removeChild(overlay);
      state.removed = true;
      delete overlay.__adBrandedPreloader;
      if (onComplete) onComplete(meta);
    }

    function removeCss() {
      var st = document.getElementById(CSS_ID);
      if (st && st.parentNode) st.parentNode.removeChild(st);
    }

    function loadOne(url) {
      var settled = false;
      function done() { if (settled) return; settled = true; loadedUnits++; checkDone(); }
      if (isImage(url)) {
        var img = new global.Image();
        img.onload = done;
        img.onerror = done; // a failed asset still counts — the loader never hangs
        img.src = url;
      } else if (typeof global.fetch === 'function') {
        global.fetch(url).then(done, done);
      } else {
        done();
      }
    }

    // Open: un-hide, promote to the JS-only class, announce busy, lock scroll.
    overlay.removeAttribute('hidden');
    overlay.removeAttribute('aria-hidden');
    overlay.classList.add('ad-preloader');
    overlay.setAttribute('aria-busy', 'true');
    document.body.style.overflow = 'hidden';

    if (reduce()) {
      render(0);
      state.minTimer = global.setTimeout(function () { minElapsed = true; checkDone(); }, minMs);
    } else {
      state.raf = global.requestAnimationFrame(tick);
    }

    // Wire the real sources after opening — their callbacks feed the model above.
    for (var i = 0; i < assets.length; i++) loadOne(assets[i]);
    if (trackActive) {
      opts.track.onProgress(function (p) {
        p = +p;
        if (!(p >= 0)) p = 0;
        if (p > 1) p = 1;
        if (p > trackProgress) { trackProgress = p; checkDone(); }
      });
    }
    if (fontsActive) {
      document.fonts.ready.then(function () { loadedUnits++; checkDone(); });
    }

    var handle = {
      destroy: function () {
        if (state.raf) { global.cancelAnimationFrame(state.raf); state.raf = 0; }
        if (state.anim) { state.anim.cancel(); state.anim = null; }
        if (state.minTimer) { global.clearTimeout(state.minTimer); state.minTimer = 0; }
        document.removeEventListener('keydown', trapKeydown, true);
        if (enterBtn) enterBtn.removeEventListener('click', onActivate);
        document.body.style.overflow = prevOverflow;
        // Only restore the overlay if the exit has not already removed it.
        if (!state.removed && overlay.parentNode) {
          overlay.classList.remove('ad-preloader');
          overlay.style.removeProperty('--ad-preloader-progress');
          overlay.removeAttribute('aria-busy');
          overlay.removeAttribute('aria-hidden');
          overlay.removeAttribute('data-ad-near');
          overlay.removeAttribute('data-ad-enter-ready');
          if (bar.parentNode) bar.parentNode.removeChild(bar);
          if (enterBtn && enterBtn.parentNode) enterBtn.parentNode.removeChild(enterBtn);
          if (counterEl) counterEl.textContent = counterText0;
          if (hadHidden) overlay.setAttribute('hidden', '');
          else overlay.removeAttribute('hidden');
        }
        delete overlay.__adBrandedPreloader;
        removeCss();
      }
    };
    state.handle = handle;
    return handle;
  }

  global.awardBrandedPreloader = { init: init };
})(typeof window !== 'undefined' ? window : this);
