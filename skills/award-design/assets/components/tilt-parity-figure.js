/*
 * tilt-parity-figure — alternating rest tilts with a sticker un-peel hover
 * (winner: FlowFest). Direct children of a [data-ad-tilt-parity] container
 * get alternating rest rotations by nth-child parity — odd -2.5deg, even
 * 2.5deg, every third -1deg for organic variance — so a run of cards reads as
 * hand-placed, not machine-set. On :hover/:focus-within a child straightens
 * to 0 and scales 1.03 under the strike easing — the sticker un-peels. The
 * component owns rotation only: the child keeps its own styling, and a child
 * carrying its own transform doesn't belong in a tilt-parity container.
 *
 * Touch: the rest tilts ARE the identity — the composition reads with no
 * pointer at all, so no tap behavior is needed.
 * Reduced motion: rest tilts remain (they are static composition, not
 * motion); only the hover/focus straighten becomes instant.
 * Content-visible at rest: with no JS the container is untagged and its
 * children sit straight — fully legible, just untilted.
 *
 * Usage:  awardTiltParity.init(root, { selector })
 *   root      Element|Document  scope (default document)
 *   selector  string            containers to tag (default '[data-ad-tilt-parity]')
 * Returns { destroy() }. Idempotent. destroy() untags the containers and
 * removes the stylesheet.
 *
 * Tokens: --ad-dur-base (420ms), --ad-ease-strike (cubic-bezier(.7,.02,.28,1)).
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-tilt-parity-css';
  var TRANSIT = 'var(--ad-dur-base,420ms) var(--ad-ease-strike,cubic-bezier(.7,.02,.28,1))';

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      '.ad-tilt-parity>*{transform-origin:center;transition:transform ' + TRANSIT + ';}' +
      '.ad-tilt-parity>:nth-child(odd){transform:rotate(-2.5deg);}' +
      '.ad-tilt-parity>:nth-child(even){transform:rotate(2.5deg);}' +
      // Ordered after the parity rules (equal specificity) so every 3rd wins.
      '.ad-tilt-parity>:nth-child(3n){transform:rotate(-1deg);}' +
      // Last so the straighten beats every rest tilt.
      '.ad-tilt-parity>:hover,.ad-tilt-parity>:focus-within{' +
      'transform:rotate(0) scale(1.03);}' +
      '@media (prefers-reduced-motion:reduce){.ad-tilt-parity>*{transition:none;}}';
    document.head.appendChild(s);
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-tilt-parity]';
    injectCss();
    var containers = Array.prototype.slice.call(root.querySelectorAll(selector));
    containers.forEach(function (el) { el.classList.add('ad-tilt-parity'); });
    return {
      destroy: function () {
        containers.forEach(function (el) { el.classList.remove('ad-tilt-parity'); });
        var s = document.getElementById(CSS_ID);
        if (s) s.parentNode.removeChild(s);
      }
    };
  }

  global.awardTiltParity = { init: init };
})(typeof window !== 'undefined' ? window : this);
