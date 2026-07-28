/*
 * idle-attract-auto-demo — the verb-teaching attract mode (source: a
 * DESIGN-LOGIC gap, NOT winner-canon — derived from the experimental
 * archetype's own 30% Usability weighting; Bruno Simon's 'click to start' +
 * floor path is the STATIC discoverability aid this motion-taught variant
 * companions. Lower confidence by the playbook's own flag: present it as a
 * usability device, never as winner law). After idleMs with NO input the
 * world auto-performs ONE scripted pass of its core verb — a lap, a tumble,
 * a hover-preview — to TEACH the non-standard interaction inside the
 * ten-second window, then hands control back; the FIRST real input during a
 * pass cancels it instantly (the visitor always wins the wheel).
 *
 * Ruled DISTINCT from the décor idle channels: ambient-idle (unstructured
 * breathing of authored elements) and perpetual-tile-machines (content
 * machines on period clocks) animate DECOR regardless of input — this is an
 * INPUT-STATE MACHINE that drives the scene's PRIMARY VERB only while input
 * is absent, and yields to it. It renders nothing itself: the scene owns
 * the verb; this component owns idle detection, the demo clock, and the
 * hand-back.
 *
 * Usage:  awardIdleAttractAutoDemo.init(root, opts)
 *   root      Element|Document  scope (default document)
 *   selector  string   the scene surface to gate on (default '[data-ad-attract]')
 *   idleMs    ms       inputless time before a pass engages (default 5000 —
 *                      a default tuned to the ten-second window, not a
 *                      measured winner value)
 *   demoMs    ms       one pass's duration (default 3000 — a default)
 *   maxRuns   number   engagements before the component trusts the visitor
 *                      and disarms (default 2 — teach twice, then trust; a
 *                      default choice, not law)
 *   onStart   function ()            a pass begins
 *   onFrame   function (p)           per frame, p 0→1 on the decelerating ease —
 *                                    the scene maps it onto its verb
 *   onEnd     function (completed)   the pass ended — true ran out, false was
 *                                    cancelled by real input
 * Returns { destroy() }. Idempotent per root.
 *
 * Gates: a pass only engages while the surface is on-screen
 * (IntersectionObserver) AND the tab is visible; going hidden or off-screen
 * mid-pass cancels it (a background tab never performs). Input listened:
 * pointerdown/pointermove/wheel/keydown/touchstart/scroll — all passive.
 * reduced-motion: fully dormant — motion that plays unrequested is exactly
 * what reduce forbids; the static anchor ('click to start') carries
 * discoverability alone. Zero per-frame work at rest — one timer between
 * inputs, rAF only while a pass runs.
 */
(function (global) {
  'use strict';

  var reduce = function () {
    return !!(global.matchMedia &&
      global.matchMedia('(prefers-reduced-motion: reduce)').matches);
  };

  var INPUT_EVENTS = ['pointerdown', 'pointermove', 'wheel', 'keydown', 'touchstart', 'scroll'];

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    if (reduce()) return { destroy: function () {} };

    var selector = opts.selector || '[data-ad-attract]';
    var surface = (root.matches && root.matches(selector))
      ? root
      : (root.querySelector ? root.querySelector(selector) : null);
    if (!surface) return { destroy: function () {} };
    if (surface.__adIdleAttract) return surface.__adIdleAttract;

    var idleMs = opts.idleMs != null ? +opts.idleMs : 5000;
    var demoMs = opts.demoMs != null ? +opts.demoMs : 3000;
    var maxRuns = opts.maxRuns != null ? +opts.maxRuns : 2;
    var onStart = typeof opts.onStart === 'function' ? opts.onStart : function () {};
    var onFrame = typeof opts.onFrame === 'function' ? opts.onFrame : function () {};
    var onEnd = typeof opts.onEnd === 'function' ? opts.onEnd : function () {};

    var timer = 0, rafId = 0, t0 = 0;
    var running = false, runs = 0, onScreen = false, destroyed = false;

    function arm() {
      if (timer) { clearTimeout(timer); timer = 0; }
      if (destroyed || running || runs >= maxRuns) return;
      if (!onScreen || document.hidden) return;
      timer = setTimeout(engage, idleMs);
    }

    function engage() {
      timer = 0;
      if (destroyed || running || !onScreen || document.hidden) return;
      running = true;
      runs++;
      t0 = 0;
      onStart();
      rafId = global.requestAnimationFrame(frame);
    }

    function frame(now) {
      rafId = 0;
      if (!t0) t0 = now;
      var t = Math.min(1, (now - t0) / demoMs);
      onFrame(1 - Math.pow(1 - t, 3));
      if (t >= 1) { settle(true); return; }
      rafId = global.requestAnimationFrame(frame);
    }

    function settle(completed) {
      if (!running) return;
      running = false;
      if (rafId) { global.cancelAnimationFrame(rafId); rafId = 0; }
      onEnd(completed);
      arm(); // the next idle period may teach again, up to maxRuns
    }

    // any real input: cancel a running pass at once, re-arm the idle clock
    function onInput() {
      if (running) settle(false);
      else arm();
    }

    var io = null;
    if (global.IntersectionObserver) {
      io = new global.IntersectionObserver(function (entries) {
        onScreen = entries[entries.length - 1].isIntersecting;
        if (!onScreen && running) settle(false);
        arm();
      });
      io.observe(surface);
    } else {
      onScreen = true;
      arm();
    }

    function onVis() {
      if (document.hidden && running) settle(false);
      arm();
    }

    INPUT_EVENTS.forEach(function (ev) {
      global.addEventListener(ev, onInput, { passive: true, capture: true });
    });
    document.addEventListener('visibilitychange', onVis);

    var handle = {
      destroy: function () {
        destroyed = true;
        if (running) settle(false);
        if (timer) { clearTimeout(timer); timer = 0; }
        INPUT_EVENTS.forEach(function (ev) {
          global.removeEventListener(ev, onInput, { capture: true });
        });
        document.removeEventListener('visibilitychange', onVis);
        if (io) io.disconnect();
        delete surface.__adIdleAttract;
      }
    };
    surface.__adIdleAttract = handle;
    return handle;
  }

  global.awardIdleAttractAutoDemo = { init: init };
})(typeof window !== 'undefined' ? window : this);
