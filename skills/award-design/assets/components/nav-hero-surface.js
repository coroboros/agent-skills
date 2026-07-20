/*
 * nav-hero-surface — the SURFACE axis for a minimal PERSISTENT bar, the winner norm
 * (navigation-patterns.md: "A quiet persistent bar is the first choice"). The bar never
 * hides; it floats transparent over the hero and gains an owned, backdrop-blurred
 * --ad-ground once the hero's bottom crosses the bar. This is the id the persistent-bar
 * pattern needs and the library lacked — show-on-scroll-up-nav owns visibility (hide/
 * reveal), nav-context-ink owns the ink axis (publish-only). Orthogonal machines,
 * never conflated: this one touches is-grounded and nothing else.
 *
 * Grounding is driven by an IntersectionObserver on the hero SENTINEL, not a fixed
 * scrollY (a hard threshold grounds the bar while it still floats over the hero — the
 * decapitation tell NAV-HERO-OPAQUE catches). A page with no hero forces the solid
 * state (navigation-patterns.md). Hover gains a faint surface so light-on-light links
 * stay legible over bright imagery. Background and backdrop-filter only — zero layout,
 * zero CLS. The grounded state lives in a JS-toggled class, so a dead script or no-JS
 * render leaves a normal, fully-visible bar; a hero-less page renders solid at once.
 *
 * Usage:  awardNavHeroSurface.init(root, { selector, hero })
 *   root      Element|Document  scope (default document)
 *   selector  string            the nav to drive (default '[data-ad-nav]')
 *   hero      string            the hero to sentinel (default '[data-ad-hero]');
 *                               absent → the bar renders permanently grounded
 * Returns { destroy() }. Idempotent. Reduced-motion snaps the ground in with no transition.
 *
 * Tokens: --ad-ground (oklch(14% 0.01 260)), --ad-dur-base (420ms),
 *         --ad-ease-signature (cubic-bezier(.16,1,.3,1)).
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-nav-hero-surface-css';

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      '[data-ad-nav]{' +
        'position:fixed;top:0;left:0;right:0;background-color:transparent;' +
        'transition:background-color var(--ad-dur-base,420ms) var(--ad-ease-signature,cubic-bezier(.16,1,.3,1));' +
      '}' +
      // Hover over the hero: a faint scrim so light-on-light links stay legible.
      '[data-ad-nav]:hover{' +
        'background-color:color-mix(in oklab,var(--ad-ground,oklch(14% 0.01 260)) 32%,transparent);' +
      '}' +
      // is-grounded is JS-toggled only → no class, no owned surface at rest over the hero.
      '[data-ad-nav].is-grounded,[data-ad-nav].is-grounded:hover{' +
        'background-color:var(--ad-ground,oklch(14% 0.01 260));' +
        'background-color:color-mix(in oklab,var(--ad-ground,oklch(14% 0.01 260)) 88%,transparent);' +
        '-webkit-backdrop-filter:blur(12px);backdrop-filter:blur(12px);' +
      '}' +
      // Reduced motion: the ground snaps in with no transition (surface, not motion).
      '@media (prefers-reduced-motion:reduce){' +
        '[data-ad-nav]{transition:none!important;}' +
      '}';
    document.head.appendChild(s);
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-nav]';
    injectCss();

    var navs = Array.prototype.slice.call(root.querySelectorAll(selector))
      .filter(function (nav) { return !nav.__adNavSurfaceBound; });
    if (!navs.length) return { destroy: function () {} };
    navs.forEach(function (nav) { nav.__adNavSurfaceBound = true; });

    function setGrounded(on) {
      navs.forEach(function (nav) { nav.classList.toggle('is-grounded', on); });
    }

    var hero = (root.querySelector ? root : document).querySelector(opts.hero || '[data-ad-hero]');
    var observer = null;
    if (hero && typeof IntersectionObserver !== 'undefined') {
      var barH = navs[0].getBoundingClientRect().height || 64;
      observer = new IntersectionObserver(function (entries) {
        // Grounded once the hero stops intersecting the top band (its bottom
        // passes one bar-height below the viewport top) — the hero-bottom sentinel.
        setGrounded(!entries[entries.length - 1].isIntersecting);
      }, { rootMargin: '-' + Math.round(barH) + 'px 0px 0px 0px', threshold: 0 });
      observer.observe(hero);
    } else {
      setGrounded(true); // no hero → the solid state is forced
    }

    return {
      destroy: function () {
        if (observer) observer.disconnect();
        navs.forEach(function (nav) {
          nav.classList.remove('is-grounded');
          delete nav.__adNavSurfaceBound;
        });
      }
    };
  }

  global.awardNavHeroSurface = { init: init };
})(typeof window !== 'undefined' ? window : this);
