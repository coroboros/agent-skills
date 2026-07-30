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
 * When the instance is live, the rig also owns the two travels every build kept
 * re-inventing by hand (one dead build's anchor loop, another's wordmarkHome):
 * in-page anchor clicks ride lenis.scrollTo so the jumps agree with the wheel,
 * and the home wordmark / back-to-top links (homeSelector) follow
 * navigation-patterns' wordmark rule — mid-scroll → script scroll to top, at the
 * top with a real same-page URL → native reload, elsewhere on the site → native
 * navigation.
 * Neither travel ever writes a #fragment into the URL (a fragment appearing on
 * a chrome click reads unfinished). Modified clicks (new-tab intent), off-page
 * links, and targets that don't exist stay native.
 *
 * Usage:  var rig = awardSmoothScroll.init(root, { lerp, wheelMultiplier,
 *                                                  anchors, anchorOffset, homeSelector })
 *   lerp             number   Lenis smoothing (default 0.1)
 *   wheelMultiplier  number   wheel speed (default 1)
 *   anchors          boolean  route same-page anchor clicks through Lenis (default true)
 *   anchorOffset     number   px offset added to anchor travel (default 0)
 *   homeSelector     string   wordmark/back-to-top links (default '[data-ad-home]';
 *                             null disables the home branch)
 * Returns { destroy(), lenis }. `lenis` is the instance, or null when native scroll
 * is in effect (no Lenis present, or reduced-motion) — callers must null-check it.
 * On the native path no routing is bound either: platform anchors already jump
 * instantly, which is exactly the reduced-motion contract.
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

    var anchors = opts.anchors != null ? opts.anchors : true;
    var anchorOffset = opts.anchorOffset != null ? opts.anchorOffset : 0;
    var homeSelector = opts.homeSelector !== undefined ? opts.homeSelector : '[data-ad-home]';
    var listenRoot = root && root.addEventListener ? root : document;
    var onClick = null;

    // Same document, ignoring the hash — the platform resolves relative hrefs.
    function samePage(a) {
      return a.pathname === global.location.pathname && a.search === global.location.search;
    }

    if (anchors || homeSelector) {
      onClick = function (e) {
        if (e.defaultPrevented || e.button !== 0) return;
        if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
        var a = e.target && e.target.closest ? e.target.closest('a[href]') : null;
        if (!a || a.target || a.hasAttribute('download')) return;

        if (homeSelector && a.matches(homeSelector)) {
          if (!samePage(a)) return; // elsewhere on the site → real navigation
          if ((global.scrollY || 0) > 1) {
            e.preventDefault();
            lenis.scrollTo(0); // script scroll — never an href="#top" jump
          } else if (a.getAttribute('href').charAt(0) === '#') {
            e.preventDefault(); // hash-only home at the top: never write a fragment
          }
          // same-page real URL at the top → native reload (the wordmark rule)
          return;
        }

        if (!anchors || !samePage(a)) return;
        var hash = a.hash;
        if (!hash || hash.length < 2) return;
        var target = document.getElementById(decodeURIComponent(hash.slice(1)));
        if (!target) return;
        e.preventDefault(); // Lenis owns the travel; the URL keeps no fragment
        lenis.scrollTo(target, { offset: anchorOffset });
        // Sequential focus must land where the visitor was sent — the platform
        // only moves it on the native jump this handler just prevented.
        if (target.tabIndex < 0 && !target.hasAttribute('tabindex')) {
          target.setAttribute('tabindex', '-1');
        }
        target.focus({ preventScroll: true });
      };
      listenRoot.addEventListener('click', onClick);
    }

    return {
      lenis: lenis,
      destroy: function () {
        if (rafId) global.cancelAnimationFrame(rafId);
        if (tickerFn && gsap) gsap.ticker.remove(tickerFn);
        if (onClick) listenRoot.removeEventListener('click', onClick);
        lenis.destroy();
      }
    };
  }

  global.awardSmoothScroll = { init: init };
})(typeof window !== 'undefined' ? window : this);
