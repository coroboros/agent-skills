/*
 * glass-card — credentialed frost surface (winners: Igloo Inc's frost panels (SOTY); the
 * Liquid Glass / Doppelrand surface canon). Elements tagged [data-ad-glass] get a JS-added
 * .ad-glass class; CSS then delivers the full recipe: a 55% ground-2 color-mix ground,
 * backdrop blur(24px) saturate(1.2), a 14%-ink hairline border, and the inset 1px top
 * highlight that sells the glass. Radius is 16px; a glass element nested inside another
 * gets 10px — the Doppelrand rule (concentric radii: outer minus padding). No motion of
 * its own, so reduced motion needs nothing disabled; the surface is fully legible at rest.
 * Where backdrop-filter is unsupported the ground mix rises to 82% so text stays readable
 * without blur. A11y: the builder must keep body text on glass at >= 72% ink for contrast.
 *
 * Usage:  awardGlassCard.init(root, { selector })
 *   root      Element|Document  scope (default document)
 *   selector  string            elements to tag (default '[data-ad-glass]')
 * Returns { destroy() }. Idempotent. destroy() untags the elements and removes the stylesheet.
 *
 * Tokens: --ad-ground-2 (oklch(18% 0.01 260)), --ad-ink (oklch(96% 0 0)).
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-glass-card-css';
  var GROUND2 = 'var(--ad-ground-2,oklch(18% 0.01 260))';
  var INK = 'var(--ad-ink,oklch(96% 0 0))';

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      '.ad-glass{' +
      'background:color-mix(in oklch,' + GROUND2 + ' 55%,transparent);' +
      '-webkit-backdrop-filter:blur(24px) saturate(1.2);' +
      'backdrop-filter:blur(24px) saturate(1.2);' +
      'border:1px solid color-mix(in oklch,' + INK + ' 14%,transparent);' +
      'box-shadow:inset 0 1px 0 color-mix(in oklch,' + INK + ' 12%,transparent);' +
      'border-radius:16px;}' +
      '.ad-glass .ad-glass{border-radius:10px;}' +
      // Older Safari only knows the -webkit- form — the or-test keeps its blur alive.
      '@supports not ((backdrop-filter:blur(1px)) or (-webkit-backdrop-filter:blur(1px)))' +
      '{.ad-glass{background:color-mix(in oklch,' + GROUND2 + ' 82%,transparent);}}';
    document.head.appendChild(s);
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-glass]';
    injectCss();

    var panels = Array.prototype.slice.call(root.querySelectorAll(selector));
    panels.forEach(function (el) { el.classList.add('ad-glass'); });

    return {
      destroy: function () {
        panels.forEach(function (el) { el.classList.remove('ad-glass'); });
        var s = document.getElementById(CSS_ID);
        if (s) s.parentNode.removeChild(s);
      }
    };
  }

  global.awardGlassCard = { init: init };
})(typeof window !== 'undefined' ? window : this);
