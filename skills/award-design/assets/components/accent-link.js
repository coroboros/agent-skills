/*
 * accent-link — inked link with an accent underline wipe (winner: Siena Film Foundation).
 * Inline links tagged [data-ad-link] get a JS-added .ad-link class; CSS then draws a 1px
 * baseline rule via a ::after scaleX (in from the left on hover/focus, out to the right on
 * leave) and warms the text toward --ad-accent. Motion is pure CSS — the JS only injects the
 * stylesheet and tags the links, so a build just adds data-ad-link to its links.
 * Content is fully legible at rest with no JS: an untagged link keeps its default underline.
 * Under reduced motion the underline and color apply instantly, with no transition.
 *
 * Usage:  awardAccentLink.init(root, { selector })
 *   root      Element|Document  scope (default document)
 *   selector  string            links to tag (default '[data-ad-link]')
 * Returns { destroy() }. Idempotent. destroy() untags the links and removes the stylesheet.
 *
 * Tokens: --ad-accent (oklch(62% 0.2 25)), --ad-dur-base (420ms),
 *         --ad-ease-signature (cubic-bezier(.16,1,.3,1)).
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-accent-link-css';
  var ACCENT = 'var(--ad-accent,oklch(62% 0.2 25))';
  var TRANSIT = 'var(--ad-dur-base,420ms) var(--ad-ease-signature,cubic-bezier(.16,1,.3,1))';

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      // Resting link matches body text, no default underline — the ::after rule replaces it.
      '.ad-link{color:inherit;text-decoration:none;position:relative;' +
      'transition:color ' + TRANSIT + ';}' +
      // 1px baseline rule, collapsed to the right so hover wipes it in from the left.
      '.ad-link::after{content:"";position:absolute;left:0;right:0;bottom:-0.1em;height:1px;' +
      'background:' + ACCENT + ';transform:scaleX(0);transform-origin:right center;' +
      'transition:transform ' + TRANSIT + ';}' +
      '.ad-link:hover,.ad-link:focus-visible{color:' + ACCENT + ';}' +
      '.ad-link:hover::after,.ad-link:focus-visible::after{transform:scaleX(1);' +
      'transform-origin:left center;}' +
      // Reduced motion → the state still applies on hover/focus, just instantly.
      '@media (prefers-reduced-motion:reduce){' +
      '.ad-link,.ad-link::after{transition:none;}}';
    document.head.appendChild(s);
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-link]';
    injectCss();

    var links = Array.prototype.slice.call(root.querySelectorAll(selector));
    links.forEach(function (a) { a.classList.add('ad-link'); });

    return {
      destroy: function () {
        links.forEach(function (a) { a.classList.remove('ad-link'); });
        var s = document.getElementById(CSS_ID);
        if (s) s.parentNode.removeChild(s);
      }
    };
  }

  global.awardAccentLink = { init: init };
})(typeof window !== 'undefined' ? window : this);
