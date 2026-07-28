/*
 * border-glow-bloom — blurred accent under-glow that lifts a card (winners: Supabase, Linear).
 * Elements tagged [data-ad-glow-card] get a JS-added .ad-glow-card class; CSS then parks a
 * ::before behind the card (inset -1px, z-index -1, radius inherited) carrying a radial
 * accent gradient under blur(18px) at 0.35 opacity at rest, blooming to 0.7 on hover or
 * :focus-within over --ad-dur-base. The card itself gets a 10%-ink hairline border plus a
 * ground-2 background — unless the attribute value is "bare" (data-ad-glow-card="bare"
 * keeps the element's own background).
 * Perf: the blur lives on a pseudo whose filter never animates — only opacity transitions,
 * so the bloom is compositor-clean. Under reduced motion the bloom applies instantly.
 * Touch: the rest state (0.35 glow) is the complete look; hover only breathes it up.
 *
 * Usage:  awardBorderGlow.init(root, { selector })
 *   root      Element|Document  scope (default document)
 *   selector  string            elements to tag (default '[data-ad-glow-card]')
 * Returns { destroy() }. Idempotent. destroy() untags the elements and removes the stylesheet.
 *
 * Tokens: --ad-accent (oklch(62% 0.2 25)), --ad-ink (oklch(96% 0 0)),
 *         --ad-ground-2 (oklch(18% 0.01 260)), --ad-dur-base (420ms),
 *         --ad-ease-signature (cubic-bezier(.16,1,.3,1)).
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-border-glow-css';
  var ACCENT = 'var(--ad-accent,oklch(62% 0.2 25))';
  var INK = 'var(--ad-ink,oklch(96% 0 0))';
  var GROUND2 = 'var(--ad-ground-2,oklch(18% 0.01 260))';
  var TRANSIT = 'var(--ad-dur-base,420ms) var(--ad-ease-signature,cubic-bezier(.16,1,.3,1))';

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      // isolation keeps the z-index:-1 pseudo inside the card's own stacking context,
      // so it can't slide under an opaque ancestor background.
      '.ad-glow-card{position:relative;isolation:isolate;' +
      'border:1px solid color-mix(in oklch,' + INK + ' 10%,transparent);}' +
      '.ad-glow-card:not([data-ad-glow-card="bare"]){background:' + GROUND2 + ';}' +
      '.ad-glow-card::before{content:"";position:absolute;inset:-1px;z-index:-1;' +
      'border-radius:inherit;' +
      'background:radial-gradient(ellipse at 50% 50%,' +
      'color-mix(in oklch,' + ACCENT + ' 50%,transparent),transparent 70%);' +
      'filter:blur(18px);opacity:.35;transition:opacity ' + TRANSIT + ';}' +
      '.ad-glow-card:hover::before,.ad-glow-card:focus-within::before{opacity:.7;}' +
      '@media (prefers-reduced-motion:reduce){.ad-glow-card::before{transition:none;}}';
    document.head.appendChild(s);
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-glow-card]';
    injectCss();

    var cards = Array.prototype.slice.call(root.querySelectorAll(selector));
    cards.forEach(function (el) { el.classList.add('ad-glow-card'); });

    return {
      destroy: function () {
        cards.forEach(function (el) { el.classList.remove('ad-glow-card'); });
        var s = document.getElementById(CSS_ID);
        if (s) s.parentNode.removeChild(s);
      }
    };
  }

  global.awardBorderGlow = { init: init };
})(typeof window !== 'undefined' ? window : this);
