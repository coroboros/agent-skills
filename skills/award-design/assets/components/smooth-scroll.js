/*
 * smooth-scroll — the scroll rig (winner: nearly every immersive/editorial line; Lenis).
 * Smoothed scrolling is what lets scrubbed media and pinned reveals feel like film
 * rather than notched wheel steps. This rig does NOT ship a hand-rolled lerp — a
 * home-grown smooth-scroll hijacks the keyboard, anchor jumps, and focus scrolling
 * and reads worse than the platform. Instead it enhances ONLY when the build already
 * includes Lenis: it constructs the instance, drives it on rAF, and wires GSAP
 * ScrollTrigger correctly when present. No Lenis, or reduced-motion → native scroll,
 * untouched. The instance is exposed so scrub/pin components can share one loop.
 *
 * Usage:  var rig = awardSmoothScroll.init(root, { lerp, wheelMultiplier })
 *   lerp             number  Lenis smoothing (default 0.1)
 *   wheelMultiplier  number  wheel speed (default 1)
 * Returns { destroy(), lenis }. `lenis` is the instance, or null when native scroll
 * is in effect (no Lenis present, or reduced-motion) — callers must null-check it.
 */
(function (global) {
  'use strict';
  var reduce = function () {
    return global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches;
  };

  function init(root, opts) {
    opts = opts || {};
    var Lenis = global.Lenis;
    var gsap = global.gsap;
    var ScrollTrigger = gsap && gsap.core && global.ScrollTrigger ? global.ScrollTrigger : null;

    // Native scroll is the correct behaviour when the build ships no Lenis or the
    // visitor asked for less motion — return a null instance, not a fake one.
    if (!Lenis || reduce()) {
      return { destroy: function () {}, lenis: null };
    }

    var lenis = new Lenis({
      lerp: opts.lerp != null ? opts.lerp : 0.1,
      wheelMultiplier: opts.wheelMultiplier != null ? opts.wheelMultiplier : 1
    });

    var rafId = 0;
    var tickerFn = null;

    if (ScrollTrigger) {
      // The documented Lenis+GSAP wiring: Lenis notifies ScrollTrigger, and gsap's
      // ticker (one rAF for the whole page) drives Lenis, in ms.
      lenis.on('scroll', ScrollTrigger.update);
      tickerFn = function (time) { lenis.raf(time * 1000); };
      gsap.ticker.add(tickerFn);
      gsap.ticker.lagSmoothing(0);
    } else {
      var loop = function (time) { lenis.raf(time); rafId = global.requestAnimationFrame(loop); };
      rafId = global.requestAnimationFrame(loop);
    }

    return {
      lenis: lenis,
      destroy: function () {
        if (rafId) global.cancelAnimationFrame(rafId);
        if (tickerFn && gsap) gsap.ticker.remove(tickerFn);
        lenis.destroy();
      }
    };
  }

  global.awardSmoothScroll = { init: init };
})(typeof window !== 'undefined' ? window : this);
