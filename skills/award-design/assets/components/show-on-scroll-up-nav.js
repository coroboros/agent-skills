/*
 * show-on-scroll-up-nav — fixed top nav, transparent over the hero, that grounds and
 * reveals-on-scroll-up (winner: Siena Film Foundation, Lando Norris). Two decoupled
 * axes (navigation-patterns.md). SURFACE: the bar floats transparent over the hero and
 * gains a translucent, backdrop-blurred --ad-ground once the hero's bottom crosses the
 * bar — driven by an IntersectionObserver on the hero SENTINEL, not a fixed scrollY
 * (a hard threshold grounds the bar while it still floats over the hero — the tell the
 * sentinel closes). A page with no hero falls back to the top-guard threshold (the solid
 * state is forced). VISIBILITY: scrolling down hides it (translateY(-100%)), scrolling
 * up brings it back, always shown at the very top. Direction comes from ACCUMULATORS,
 * never a raw per-frame delta: cumulative down-travel past HIDE_TOL hides, cumulative
 * up-travel past SHOW_TOL shows, a direction change resets the opposite accumulator,
 * and dy == 0 (scroll-stop, smooth-scroll settle) holds the current state — so
 * sub-tolerance jitter and inertial settles produce zero hide/show flips.
 * One passive scroll listener, scrollY read once per rAF frame; transform and
 * background only. The hidden/grounded state lives in JS-toggled classes, so a dead
 * script or no-JS render leaves a normal, fully-visible fixed nav.
 *
 * Usage:  awardShowNav.init(root, { selector, hero, threshold, hideTol, showTol })
 *   root      Element|Document  scope (default document)
 *   selector  string            the nav to drive (default '[data-ad-nav]')
 *   hero      string            the hero to sentinel for the surface axis (default
 *                               '[data-ad-hero]'); absent → threshold fallback
 *   threshold px                 top guard: hide/show engage past this; surface fallback
 *   hideTol   px                 cumulative down-travel before hiding
 *   showTol   px                 cumulative up-travel before showing
 * Each numeric option falls back to a CSS custom property on :root, then a default:
 *   --ad-nav-top-guard (64) · --ad-nav-hide-tol (8) · --ad-nav-show-tol (8)
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

  function cssNumber(name) {
    if (!global.getComputedStyle || !document.documentElement) return NaN;
    return parseFloat(global.getComputedStyle(document.documentElement).getPropertyValue(name));
  }
  function setting(optValue, cssProp, fallback) {
    if (optValue != null) return optValue;
    var fromCss = cssNumber(cssProp);
    return isNaN(fromCss) ? fallback : fromCss;
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-nav]';
    var threshold = setting(opts.threshold, '--ad-nav-top-guard', 64);
    var hideTol = setting(opts.hideTol, '--ad-nav-hide-tol', 8);
    var showTol = setting(opts.showTol, '--ad-nav-show-tol', 8);
    injectCss();

    var navs = Array.prototype.slice.call(root.querySelectorAll(selector))
      .filter(function (nav) { return !nav.__adNavBound; });
    if (!navs.length) return { destroy: function () {} };
    navs.forEach(function (nav) { nav.__adNavBound = true; });

    function scrollTop() {
      return global.scrollY || global.pageYOffset || 0;
    }

    // Surface axis: the hero-bottom sentinel owns is-scrolled when a hero is
    // present. The bar grounds when the hero stops intersecting the top band
    // (its bottom passes one bar-height below the viewport top) — transparent
    // over the whole hero, solid past it. No hero → apply() drives is-scrolled
    // from the top-guard threshold (fallback).
    var hero = (root.querySelector ? root : document).querySelector(opts.hero || '[data-ad-hero]');
    var surfaceObserver = null;
    function setScrolled(on) {
      navs.forEach(function (nav) { nav.classList.toggle('is-scrolled', on); });
    }
    if (hero && typeof IntersectionObserver !== 'undefined') {
      var barH = navs[0].getBoundingClientRect().height || threshold;
      surfaceObserver = new IntersectionObserver(function (entries) {
        setScrolled(!entries[entries.length - 1].isIntersecting);
      }, { rootMargin: '-' + Math.round(barH) + 'px 0px 0px 0px', threshold: 0 });
      surfaceObserver.observe(hero);
    }

    var lastY = scrollTop();
    var downAcc = 0;
    var upAcc = 0;
    var hidden = false;
    var ticking = false;
    var rafId = 0;
    var destroyed = false;

    function apply(y) {
      var dy = y - lastY;
      if (y <= threshold) {
        downAcc = 0; upAcc = 0; hidden = false;           // top zone: always shown
      } else if (dy > 0) {
        upAcc = 0; downAcc += dy;                          // downward intent accumulates
        if (downAcc > hideTol) hidden = true;
      } else if (dy < 0) {
        downAcc = 0; upAcc -= dy;                          // upward intent accumulates
        if (upAcc > showTol) hidden = false;
      }
      // dy == 0 — a scroll-stop or smooth-scroll settle frame: hold the current state.
      if (reduce()) hidden = false;
      navs.forEach(function (nav) {
        // The sentinel observer owns is-scrolled when a hero is present; the
        // threshold drives it only in the no-hero fallback.
        if (!surfaceObserver) nav.classList.toggle('is-scrolled', y > threshold);
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
        if (surfaceObserver) surfaceObserver.disconnect();
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
