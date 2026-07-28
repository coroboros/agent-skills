/*
 * semantic-accent — key terms carry the accent; colour does the reading (winner: Terminal
 * Industries). The build marks key terms inline (<em data-ad-term>ancient light</em>); the JS
 * tags each with .ad-term and one IntersectionObserver ignites them on first scroll-into-view:
 * .is-lit transitions the term from the page ink to --ad-accent and sets a 1px baseline rule
 * in accent at 40%, so scanning the accent words alone tells the story. Fires once per term.
 * Content is fully legible at rest with no JS: an untagged term is plain body text. With JS,
 * pre-ignite terms inherit the body ink — still plain text, still legible.
 * Under reduced motion terms are accent-coloured immediately, no transition — the semantic
 * layer persists, only the arrival motion is dropped. No IntersectionObserver → lit at once.
 *
 * Usage:  awardSemanticAccent.init(root, { selector, threshold })
 *   root       Element|Document  scope (default document)
 *   selector   string            terms to tag (default '[data-ad-term]')
 *   threshold  number            IO ignite threshold (default 0.6)
 * Returns { destroy() }. Idempotent. destroy() disconnects the observer, untags the terms
 * and removes the stylesheet.
 *
 * Tokens: --ad-accent (oklch(62% 0.2 25)), --ad-dur-base (420ms),
 *         --ad-ease-signature (cubic-bezier(.16,1,.3,1)).
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-semantic-accent-css';
  var ACCENT = 'var(--ad-accent,oklch(62% 0.2 25))';
  var TRANSIT = 'var(--ad-dur-base,420ms) var(--ad-ease-signature,cubic-bezier(.16,1,.3,1))';
  // Baseline rule as a bottom gradient (not border-bottom): zero layout impact, and
  // box-decoration-break:clone repeats it under each line when a term wraps.
  var RULE = 'background-image:linear-gradient(to top,' +
    'color-mix(in oklab,' + ACCENT + ' 40%,transparent) 1px,transparent 1px);';
  var LIT = 'color:' + ACCENT + ';' + RULE;

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      // Pre-ignite the term matches body ink (em italic killed) — plain, legible text.
      '.ad-term{font-style:normal;color:inherit;transition:color ' + TRANSIT + ';' +
      '-webkit-box-decoration-break:clone;box-decoration-break:clone;}' +
      '.ad-term.is-lit{' + LIT + '}' +
      // Reduced motion → the semantic layer applies immediately, no arrival.
      '@media (prefers-reduced-motion:reduce){' +
      '.ad-term{transition:none;' + LIT + '}}';
    document.head.appendChild(s);
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-term]';
    var threshold = opts.threshold == null ? 0.6 : opts.threshold;
    injectCss();

    var terms = Array.prototype.slice.call(root.querySelectorAll(selector));
    terms.forEach(function (t) { t.classList.add('ad-term'); });

    var io = null;
    if (typeof IntersectionObserver === 'undefined') {
      terms.forEach(function (t) { t.classList.add('is-lit'); });
    } else if (terms.length) {
      io = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          entry.target.classList.add('is-lit');
          io.unobserve(entry.target);
        });
      }, { threshold: threshold });
      terms.forEach(function (t) { io.observe(t); });
    }

    return {
      destroy: function () {
        if (io) io.disconnect();
        terms.forEach(function (t) { t.classList.remove('ad-term', 'is-lit'); });
        var s = document.getElementById(CSS_ID);
        if (s) s.parentNode.removeChild(s);
      }
    };
  }

  global.awardSemanticAccent = { init: init };
})(typeof window !== 'undefined' ? window : this);
