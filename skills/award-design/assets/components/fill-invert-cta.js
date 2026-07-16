/*
 * fill-invert-cta — the full-token fill + ink inversion (winners: Truekind,
 * Siena Film Foundation, Terminal Industries, Son Daven, Lando Norris, Sui).
 * The single most universal winner button move: on hover/focus the control
 * floods with a full token (never a pale wash of it) and its label inverts to
 * the opposite pole. Two mechanics:
 *   fill — the ground and label swap poles directly (Truekind, Siena)
 *   wipe — a ::before panel wipes up from the bottom edge under the strike
 *          easing, the label inverting as it passes (Terminal)
 * Two tones: ink (default — ink flood, ground label) and accent (accent flood,
 * ground label — Sui's structural accent). State colours are committed tokens
 * at full strength; a tinted hover is the pale-hover fail this component bans.
 *
 * Usage:  awardFillCta.init(root, { selector })
 *   <a data-ad-cta href="…">Label</a>                 fill mechanic, ink tone
 *   <a data-ad-cta="wipe" …>                          wipe mechanic
 *   <a data-ad-cta data-ad-cta-tone="accent" …>       accent tone
 * The resting chrome (border, padding, face) stays the build's own CSS — the
 * component owns only the interaction: flood + inversion on :hover and
 * :focus-visible. Content-visible at rest: an untagged control is a plain
 * legible link/button; the class is JS-added. Reduced-motion: the swap is
 * instant — no wipe travel, state change only.
 *
 * Tokens: --ad-ink, --ad-ground, --ad-accent, --ad-dur-base, --ad-ease-strike.
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-fill-cta-css';

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      '.ad-cta{position:relative;overflow:hidden;isolation:isolate;' +
      'transition:color var(--ad-dur-base,420ms) var(--ad-ease-strike,cubic-bezier(.7,.02,.28,1)),' +
      'background-color var(--ad-dur-base,420ms) var(--ad-ease-strike,cubic-bezier(.7,.02,.28,1));}' +
      // fill mechanic: direct pole swap
      '.ad-cta--fill:hover,.ad-cta--fill:focus-visible{' +
      'background-color:var(--ad-ink,oklch(96% 0 0));color:var(--ad-ground,oklch(14% 0.01 260));}' +
      '.ad-cta--fill.ad-cta--accent:hover,.ad-cta--fill.ad-cta--accent:focus-visible{' +
      'background-color:var(--ad-accent,oklch(62% 0.2 25));}' +
      // wipe mechanic: a full-token panel rises from the bottom edge
      '.ad-cta--wipe::before{content:"";position:absolute;inset:0;z-index:-1;' +
      'background:var(--ad-ink,oklch(96% 0 0));transform:translateY(101%);' +
      'transition:transform var(--ad-dur-base,420ms) var(--ad-ease-strike,cubic-bezier(.7,.02,.28,1));}' +
      '.ad-cta--wipe.ad-cta--accent::before{background:var(--ad-accent,oklch(62% 0.2 25));}' +
      '.ad-cta--wipe:hover,.ad-cta--wipe:focus-visible{color:var(--ad-ground,oklch(14% 0.01 260));}' +
      '.ad-cta--wipe:hover::before,.ad-cta--wipe:focus-visible::before{transform:translateY(0);}' +
      '@media (prefers-reduced-motion:reduce){' +
      '.ad-cta{transition:none;}' +
      '.ad-cta--wipe::before{transition:none;}}';
    document.head.appendChild(s);
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-cta]';
    injectCss();
    var els = Array.prototype.slice.call(root.querySelectorAll(selector));
    els.forEach(function (el) {
      var mechanic = (el.getAttribute('data-ad-cta') || '').trim() === 'wipe' ? 'wipe' : 'fill';
      el.classList.add('ad-cta', 'ad-cta--' + mechanic);
      if ((el.getAttribute('data-ad-cta-tone') || '').trim() === 'accent') {
        el.classList.add('ad-cta--accent');
      }
    });
    return {
      destroy: function () {
        els.forEach(function (el) {
          el.classList.remove('ad-cta', 'ad-cta--fill', 'ad-cta--wipe', 'ad-cta--accent');
        });
        var s = document.getElementById(CSS_ID);
        if (s) s.parentNode.removeChild(s);
      }
    };
  }

  global.awardFillCta = { init: init };
})(typeof window !== 'undefined' ? window : this);
