/*
 * hard-press-button — the hard offset-shadow press (winners: FlowFest,
 * Anime.js, Sui). The brutalist/bento press: the control sits on a 4px hard
 * shadow (an 85% ink mix — or the accent under the accent tone), hover lifts
 * it 1px while the shadow grows to 5px, and the press drops it 3px as the
 * shadow collapses to 1px — travel plus collapse read as the control
 * physically landing. The mechanic is physical, not tonal: no color change,
 * only transform + box-shadow.
 *
 * Timing is 125ms linear, NOT the signature easing: a press is a mechanism,
 * not a gesture — linear travel reads as hardware, an eased press reads as
 * animation.
 * Touch: :active fires natively on tap, so the press IS the tap answer — no
 * coarse-pointer carve-out needed. A build may add .is-pressed to hold the
 * pressed state programmatically; it styles identically to :active.
 * Reduced motion: transitions off — states swap instantly, and a press with
 * no travel still reads through the shadow collapse.
 * Focus: the component sets no outline rules — the build's :focus-visible
 * outline applies untouched.
 *
 * Usage:  awardHardPress.init(root, { selector })
 *   <button data-ad-press>Label</button>                       ink shadow
 *   <button data-ad-press data-ad-press-tone="accent">…        accent shadow
 *   root      Element|Document  scope (default document)
 *   selector  string            controls to tag (default '[data-ad-press]')
 * The resting chrome (border, padding, face) stays the build's own CSS — the
 * component owns only the press. Content-visible at rest: an untagged control
 * is a plain legible button; the class is JS-added.
 * Returns { destroy() }. Idempotent. destroy() untags the controls and
 * removes the stylesheet.
 *
 * Tokens: --ad-ink (oklch(96% 0 0)), --ad-accent (oklch(62% 0.2 25)).
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-hard-press-css';
  var INK = 'var(--ad-ink,oklch(96% 0 0))';
  var ACCENT = 'var(--ad-accent,oklch(62% 0.2 25))';

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      '.ad-press{--ad-press-shadow:color-mix(in oklch,' + INK + ' 85%,transparent);' +
      'transform:translateY(0);box-shadow:0 4px 0 var(--ad-press-shadow);' +
      'transition:transform 125ms linear,box-shadow 125ms linear;}' +
      '.ad-press--accent{--ad-press-shadow:color-mix(in oklch,' + ACCENT + ' 85%,transparent);}' +
      '.ad-press:hover{transform:translateY(-1px);box-shadow:0 5px 0 var(--ad-press-shadow);}' +
      // Ordered after :hover (equal specificity) so a landed press beats the lift.
      '.ad-press:active,.ad-press.is-pressed{transform:translateY(3px);' +
      'box-shadow:0 1px 0 var(--ad-press-shadow);}' +
      '@media (prefers-reduced-motion:reduce){.ad-press{transition:none;}}';
    document.head.appendChild(s);
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-press]';
    injectCss();
    var els = Array.prototype.slice.call(root.querySelectorAll(selector));
    els.forEach(function (el) {
      el.classList.add('ad-press');
      if ((el.getAttribute('data-ad-press-tone') || '').trim() === 'accent') {
        el.classList.add('ad-press--accent');
      }
    });
    return {
      destroy: function () {
        els.forEach(function (el) {
          el.classList.remove('ad-press', 'ad-press--accent', 'is-pressed');
        });
        var s = document.getElementById(CSS_ID);
        if (s) s.parentNode.removeChild(s);
      }
    };
  }

  global.awardHardPress = { init: init };
})(typeof window !== 'undefined' ? window : this);
