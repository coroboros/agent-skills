/*
 * brand-object-assembly-loader — the brand object that ASSEMBLES, then the
 * scene ellipse-wipes away and the loader node UNMOUNTS (winner: Lando Norris
 * — the portrait-procession recipe's own loader annotation, flagged
 * MISSING:brand-object-assembly-loader in recipes.json: 'object assembles,
 * ellipse wipe; loader node unmounts'). The builder's brand object stands
 * center-stage as scattered PARTS; load progress SEATS them — each part
 * travels from its scatter offset into place over its own window of the
 * progress, so the mark visibly *builds itself* out of the wait and the
 * finished object IS the '100%'. One held beat at full, then the whole scene
 * collapses through an ellipse clip-path wipe and the node is REMOVED from
 * the DOM — not hidden: unmounted, scroll restored, zero loader residue.
 *
 * Ruled DISTINCT, not an alias, against all three sibling loaders:
 *   · branded-preloader seats a brand mark BESIDE a real-progress readout and
 *     recedes in place — the mark never measures. Here the parts ARE the
 *     instrument (seated fraction = progress) and there is no bar, no counter.
 *   · svg-path-fill-loader's mark is the gauge via a FILL rising through its
 *     paths, exiting by an in-place dissolve. Here nothing fills — parts
 *     TRAVEL (transform-only) into a whole, and the exit is an ellipse WIPE
 *     followed by a true unmount.
 *   · flip-handoff-loader's mark TRAVELS INTO THE HEADER (element continuity
 *     into the chrome). Here the object completes center-stage, nothing lands
 *     in the header, and the node ceases to exist.
 *
 * The fill stays honest (the library's loader law): assembly eases toward 90%
 * over `minDuration`, HOLDS until the real window `load` (plus opts.track, a
 * LoadingManager-like { onProgress } source, when given — both must land),
 * then settles to full and the wipe plays.
 *
 * Expected markup — authored `hidden`; the builder authors the object's parts
 * (spans/imgs/svgs — anything positioned by the builder's own CSS):
 *   <div data-ad-assembly-loader hidden>
 *     <div data-assembly-object aria-label="Maison">
 *       <span data-assembly-part data-part-from="-140,90,-24">…</span>
 *       <span data-assembly-part>…</span>   <!-- no data-part-from: deterministic
 *                                                golden-angle scatter by index -->
 *     </div>
 *   </div>
 * data-part-from = "dx,dy,rot" (px, px, deg) — the part's scatter start.
 * Scatter without it is index-derived and deterministic (no randomness — the
 * same mark assembles the same way every load).
 *
 * Usage:  awardBrandObjectAssemblyLoader.init(root, opts)
 *   root         Element|Document  scope (default document)
 *   selector     string    the scene (default '[data-ad-assembly-loader]')
 *   minDuration  ms        floor for the 0→90% ease (default 1800)
 *   track        object    { onProgress(cb) } — a real load source; progress
 *                          holds at 90% until it reports 1 AND window load.
 *   sessionOnce  boolean   skip after the first completed run this session
 *   onDone       function  runs once after the unmount — start the hero here.
 *                          Fires on every skip path too.
 * Returns { destroy() }. Idempotent — while running it returns the live
 * handle; once done a re-init is a no-op. destroy() cancels the run, unmounts
 * the scene and restores the body scroll lock.
 *
 * Content-visible at rest: the scene is authored `hidden` — no-JS or a dead
 * script never covers the page (the gated-splash law). prefers-reduced-motion:
 * the scene never shows and onDone fires immediately — the rAF assembly clock
 * and the wipe simply never run; the beat is stylistic, never load-bearing.
 * The rAF clock pauses on visibilitychange (background tabs pay nothing) and
 * resumes without a time jump.
 *
 * A11y + perf: the object wrapper announces a real progressbar (aria-valuenow
 * tracks the assembly) and the scene aria-busy; parts move on transform +
 * opacity only; the wipe is a WAAPI clip-path animation on the scene layer;
 * scroll is locked only while the scene is the only UI.
 *
 * Tokens: --ad-ground (scene ground), --ad-dur-reveal + --ad-ease-signature
 * (the wipe), --ad-dur-base (the held beat).
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-brand-object-assembly-loader-css';
  var SEEN_KEY = 'ad-brand-object-assembly-loader-done';
  var EASE_TO = 0.9; // the honest ceiling until the real bytes land

  var reduce = function () {
    return !!(global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches);
  };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    // Scoped under .ad-boal — the class JS adds after removing `hidden`;
    // no-JS never gets the class, so nothing at rest covers the page.
    s.textContent =
      '.ad-boal{position:fixed;inset:0;z-index:100000;display:grid;' +
        'place-items:center;background:var(--ad-ground,oklch(14% 0.01 260));' +
        'will-change:clip-path;}' +
      '.ad-boal [data-assembly-part]{display:inline-block;will-change:transform,opacity;}';
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
  function clamp01(v) { return v < 0 ? 0 : (v > 1 ? 1 : v); }

  // Deterministic scatter for parts without data-part-from: golden-angle
  // spread — reproducible, never Math.random.
  function scatterFor(part, i) {
    var attr = part.getAttribute('data-part-from');
    if (attr) {
      var bits = attr.split(',').map(parseFloat);
      return { dx: bits[0] || 0, dy: bits[1] || 0, rot: bits[2] || 0 };
    }
    var angle = i * 2.39996; // ~137.5° in radians
    var radius = 110 + (i % 3) * 46;
    return {
      dx: Math.cos(angle) * radius,
      dy: Math.sin(angle) * radius,
      rot: ((i * 47) % 90) - 45
    };
  }

  var state = null; // running | done — one loader beat per page

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    if (state) return state.handle || { destroy: function () {} };

    var selector = opts.selector || '[data-ad-assembly-loader]';
    var minDuration = opts.minDuration != null ? opts.minDuration : 1800;
    var scene = root.querySelector(selector);
    var object = scene && scene.querySelector('[data-assembly-object]');
    var parts = object
      ? Array.prototype.slice.call(object.querySelectorAll('[data-assembly-part]'))
      : [];

    function fireDone() { if (opts.onDone) opts.onDone(); }

    // Skip paths: no scene/parts, reduce, or an already-seen session — the
    // page stands and the first beat never depends on the flight.
    if (!scene || !parts.length || reduce() || (opts.sessionOnce && seen())) {
      if (scene) scene.remove(); // even skipped, the loader leaves no node
      state = { handle: { destroy: function () { state = null; } } };
      fireDone();
      return state.handle;
    }

    injectCss();
    var t = styles();
    var scatters = parts.map(scatterFor);
    var n = parts.length;

    // Progress model: eased floor toward 90%; the real sources gate the settle.
    var eased = 0, tracked = opts.track ? 0 : 1, winLoaded = document.readyState === 'complete';
    var raf = 0, lastTick = 0, settled = false, destroyed = false;
    var value = 0, lastShown = -1;

    if (opts.track && typeof opts.track.onProgress === 'function') {
      opts.track.onProgress(function (p) { tracked = clamp01(p); });
    }
    function onLoad() { winLoaded = true; }
    global.addEventListener('load', onLoad, { once: true });

    // Scroll lock while the scene is the only UI.
    var prevOverflow = document.documentElement.style.overflow;
    document.documentElement.style.overflow = 'hidden';
    function unlock() { document.documentElement.style.overflow = prevOverflow; }

    scene.removeAttribute('hidden');
    scene.classList.add('ad-boal');
    scene.setAttribute('aria-busy', 'true');
    object.setAttribute('role', 'progressbar');
    object.setAttribute('aria-valuemin', '0');
    object.setAttribute('aria-valuemax', '100');

    function paint(P) {
      // Part i seats over its own window of the assembly: [0.75·i/n, 0.75·i/n + 0.25].
      for (var i = 0; i < n; i++) {
        var start = 0.75 * (i / n);
        var local = easeOutCubic(clamp01((P - start) / 0.25));
        var s = scatters[i];
        parts[i].style.transform = 'translate3d(' + (s.dx * (1 - local)).toFixed(1) + 'px,'
          + (s.dy * (1 - local)).toFixed(1) + 'px,0) rotate(' + (s.rot * (1 - local)).toFixed(1) + 'deg)';
        parts[i].style.opacity = (0.2 + 0.8 * local).toFixed(3);
      }
      var shown = Math.round(P * 100);
      if (shown !== lastShown) { object.setAttribute('aria-valuenow', String(shown)); lastShown = shown; }
    }

    function wipe() {
      markSeen();
      var anim = scene.animate(
        [{ clipPath: 'ellipse(142% 142% at 50% 50%)' }, { clipPath: 'ellipse(0% 0% at 50% 50%)' }],
        { duration: t.durReveal, easing: t.ease, fill: 'forwards' }
      );
      anim.onfinish = function () {
        if (destroyed) return;
        scene.remove(); // the unmount — the loader node ceases to exist
        unlock();
        state = { handle: { destroy: function () { state = null; } } };
        fireDone();
      };
    }

    function tick(now) {
      if (destroyed) return;
      if (!lastTick) lastTick = now;
      var dt = now - lastTick;
      lastTick = now;
      eased = Math.min(EASE_TO, eased + (dt / minDuration) * EASE_TO);
      var real = winLoaded && tracked >= 1;
      if (eased >= EASE_TO && real) {
        // Settle 90→100 over a short strike, then the held beat, then the wipe.
        value = Math.min(1, value + dt / 400);
      }
      value = Math.max(value, Math.min(eased, real ? 1 : EASE_TO));
      paint(value);
      if (value >= 1 && !settled) {
        settled = true;
        setTimeout(function () { if (!destroyed) wipe(); }, t.durBase);
        return;
      }
      raf = requestAnimationFrame(tick);
    }

    // Background tabs pay nothing; the clock resumes without a jump.
    function onVis() {
      if (document.hidden) { cancelAnimationFrame(raf); lastTick = 0; }
      else if (!settled && !destroyed) raf = requestAnimationFrame(tick);
    }
    document.addEventListener('visibilitychange', onVis);

    paint(0);
    raf = requestAnimationFrame(tick);

    var handle = {
      destroy: function () {
        destroyed = true;
        cancelAnimationFrame(raf);
        document.removeEventListener('visibilitychange', onVis);
        global.removeEventListener('load', onLoad);
        scene.remove();
        unlock();
        state = null;
      }
    };
    state = { handle: handle };
    return handle;
  }

  global.awardBrandObjectAssemblyLoader = { init: init };
})(typeof window !== 'undefined' ? window : this);
