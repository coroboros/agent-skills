/*
 * show-on-scroll-up-nav — fixed top nav, transparent over the hero, that grounds and
 * reveals-on-scroll-up (winner: Siena Film Foundation, Lando Norris). Past a scroll
 * threshold the bar gains a translucent, backdrop-blurred --ad-ground; scrolling down
 * hides it (translateY(-100%)), scrolling up brings it back, and it is always shown at
 * the very top. One passive scroll listener, scrollY read once per rAF frame; transform
 * and background only. The hidden/grounded state lives in JS-toggled classes, so a dead
 * script or no-JS render leaves a normal, fully-visible fixed nav.
 *
 * Usage:  awardShowNav.init(root, { selector, threshold })
 *   root      Element|Document  scope (default document)
 *   selector  string            the nav to drive (default '[data-ad-nav]')
 *   threshold px scrolled        ground + hide/show engage past this (default 80)
 * Returns { destroy() }. Idempotent. Reduced-motion never auto-hides (ground still applies).
 *
 * Tokens: --ad-ground (oklch(14% 0.01 260)), --ad-dur-base (420ms),
 *         --ad-ease-signature (cubic-bezier(.16,1,.3,1)).
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-show-on-scroll-up-nav-css';
  var reduce = function () {
    return global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches;
  };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      '[data-ad-nav]{' +
        'position:fixed;top:0;left:0;right:0;' +
        'transform:translateY(0);background-color:transparent;will-change:transform;' +
        'transition:transform var(--ad-dur-base,420ms) var(--ad-ease-signature,cubic-bezier(.16,1,.3,1)),' +
        'background-color var(--ad-dur-base,420ms) var(--ad-ease-signature,cubic-bezier(.16,1,.3,1));' +
      '}' +
      // is-hidden / is-scrolled are JS-toggled only → no class, no hidden state at rest.
      '[data-ad-nav].is-hidden{transform:translateY(-100%);}' +
      '[data-ad-nav].is-scrolled{' +
        'background-color:var(--ad-ground,oklch(14% 0.01 260));' +
        'background-color:color-mix(in oklab,var(--ad-ground,oklch(14% 0.01 260)) 88%,transparent);' +
        '-webkit-backdrop-filter:blur(12px);backdrop-filter:blur(12px);' +
      '}' +
      // Reduced motion: kill the transform+transition live (wins over is-hidden via
      // !important), so the nav never auto-hides and the ground snaps in instantly.
      '@media (prefers-reduced-motion:reduce){' +
        '[data-ad-nav]{transition:none!important;transform:none!important;}' +
      '}';
    document.head.appendChild(s);
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-nav]';
    var threshold = opts.threshold != null ? opts.threshold : 80;
    injectCss();

    var navs = Array.prototype.slice.call(root.querySelectorAll(selector))
      .filter(function (nav) { return !nav.__adNavBound; });
    if (!navs.length) return { destroy: function () {} };
    navs.forEach(function (nav) { nav.__adNavBound = true; });

    function scrollTop() {
      return global.scrollY || global.pageYOffset || 0;
    }

    var lastY = scrollTop();
    var ticking = false;
    var rafId = 0;
    var destroyed = false;

    function apply(y) {
      var scrolled = y > threshold;
      // Hide only while scrolling down past the threshold; the top zone always shows.
      var hidden = !reduce() && y > threshold && y > lastY;
      navs.forEach(function (nav) {
        nav.classList.toggle('is-scrolled', scrolled);
        nav.classList.toggle('is-hidden', hidden);
      });
      lastY = y < 0 ? 0 : y; // clamp rubber-band overscroll
    }

    function onScroll() {
      if (ticking) return;
      ticking = true;
      rafId = requestAnimationFrame(function () {
        ticking = false;
        if (destroyed) return;
        apply(scrollTop());
      });
    }

    apply(lastY); // seed classes for a page loaded already scrolled
    global.addEventListener('scroll', onScroll, { passive: true });

    return {
      destroy: function () {
        destroyed = true;
        cancelAnimationFrame(rafId);
        global.removeEventListener('scroll', onScroll);
        navs.forEach(function (nav) {
          nav.classList.remove('is-scrolled', 'is-hidden');
          delete nav.__adNavBound;
        });
      }
    };
  }

  global.awardShowNav = { init: init };
})(typeof window !== 'undefined' ? window : this);
