/*
 * focus-defocus — gallery spotlight (winners: Dondre Green, Son Daven).
 * Hovering a [data-ad-gallery] container softens every direct child —
 * blur(3px) brightness(.75), opacity .7 — except the item under the cursor,
 * which stays crisp and lifts to scale(1.02). Keyboard gets the same
 * spotlight through :focus-within on an item's link. Motion is pure CSS —
 * the JS only injects the stylesheet and tags the containers — and the whole
 * effect is gated to (pointer:fine): touch sees the fully crisp resting
 * gallery, which is also the no-JS state. Under reduced motion, transitions
 * are off and the blur never applies (a filter shifting under the cursor is
 * vestibular-adjacent); only the opacity dim runs.
 *
 * Perf: blur repaints every softened item — keep galleries to 8-10 items.
 * The effect is hover-transient, so no persistent will-change and no
 * permanent layer promotion.
 *
 * Usage:  awardFocusDefocus.init(root, { selector })
 *   root      Element|Document  scope (default document)
 *   selector  string            galleries to tag (default '[data-ad-gallery]')
 * Returns { destroy() }. Idempotent. destroy() untags the galleries and
 * removes the stylesheet.
 *
 * Tokens: --ad-ease-signature (cubic-bezier(.16,1,.3,1)).
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-focus-defocus-css';
  var T = '300ms var(--ad-ease-signature,cubic-bezier(.16,1,.3,1))';

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      // Hover-capable pointers only — touch keeps the crisp resting gallery.
      '@media (pointer:fine){' +
      '.ad-focus>*{transition:filter ' + T + ',opacity ' + T + ',transform ' + T + ';}' +
      '.ad-focus:hover>*,.ad-focus:focus-within>*{' +
      'filter:blur(3px) brightness(.75);opacity:.7;}' +
      // Same specificity as the dim rules — source order makes the exception win.
      '.ad-focus>:hover,.ad-focus>:focus-within{filter:none;opacity:1;transform:scale(1.02);}' +
      '}' +
      // Reduce: transitions off and no blur — only the opacity dim spotlights.
      '@media (pointer:fine) and (prefers-reduced-motion:reduce){' +
      '.ad-focus>*{transition:none;}' +
      '.ad-focus:hover>*,.ad-focus:focus-within>*{filter:none;}' +
      '.ad-focus>:hover,.ad-focus>:focus-within{transform:none;}' +
      '}';
    document.head.appendChild(s);
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-gallery]';
    injectCss();

    var galleries = Array.prototype.slice.call(root.querySelectorAll(selector));
    galleries.forEach(function (g) { g.classList.add('ad-focus'); });

    return {
      destroy: function () {
        galleries.forEach(function (g) { g.classList.remove('ad-focus'); });
        var s = document.getElementById(CSS_ID);
        if (s) s.parentNode.removeChild(s);
      }
    };
  }

  global.awardFocusDefocus = { init: init };
})(typeof window !== 'undefined' ? window : this);
