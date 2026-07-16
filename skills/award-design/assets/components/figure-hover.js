/*
 * figure-hover — contained figure zoom with a companion cue (winner: Siena Film
 * Foundation, Truekind).
 * [data-ad-figure] wrappers (an img/video, optionally a figcaption) get .ad-fig;
 * the media is wrapped in its OWN clip box (.ad-fig__box) and scales to 1.1 on
 * hover/focus-within — a felt zoom, never a 1-3% twitch — clipped at the media's
 * box, so a flow figcaption below is never painted over (the scaled layer used
 * to bleed across it when the clip sat on the whole figure). A cue confirms the
 * state: tint (accent scrim to 18%), lift (a resting 25% ground scrim fades out),
 * or caption (bottom mono figcaption rises from 60%). Pick the cue with the
 * attribute value: data-ad-figure="tint|lift|caption" (default tint).
 * The rest state is complete: coarse pointers get the caption state permanently,
 * and :active flashes the zoom + cue as the tap answer. Under reduced motion the
 * media never scales and the cue applies instantly. No-JS: a plain figure.
 *
 * Usage:  awardFigureHover.init(root, { selector })
 *   root      Element|Document  scope (default document)
 *   selector  string            wrappers to tag (default '[data-ad-figure]')
 * Returns { destroy() }. Idempotent. destroy() unwraps the media, untags, and
 * removes the stylesheet.
 *
 * Tokens: --ad-accent, --ad-ink, --ad-ground, --ad-font-mono,
 *         --ad-dur-base (420ms), --ad-ease-signature (cubic-bezier(.16,1,.3,1)).
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-figure-hover-css';
  var ACCENT = 'var(--ad-accent,oklch(62% 0.2 25))';
  var GROUND = 'var(--ad-ground,oklch(14% 0.01 260))';
  var INK = 'var(--ad-ink,oklch(96% 0 0))';
  var MONO = 'var(--ad-font-mono,ui-monospace,monospace)';
  var TRANSIT = 'var(--ad-dur-base,420ms) var(--ad-ease-signature,cubic-bezier(.16,1,.3,1))';

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      '.ad-fig{position:relative;}' +
      // the media's own clip box — the scaled paint stops HERE, never over a caption
      '.ad-fig__box{display:block;position:relative;overflow:hidden;}' +
      '.ad-fig__box img,.ad-fig__box video{display:block;width:100%;transform:scale(1);' +
      'transition:transform ' + TRANSIT + ';}' +
      // 1.1 is the felt floor — anything under 1.06 reads as a twitch, not a zoom.
      '.ad-fig:hover .ad-fig__box img,.ad-fig:hover .ad-fig__box video,' +
      '.ad-fig:focus-within .ad-fig__box img,.ad-fig:focus-within .ad-fig__box video,' +
      '.ad-fig:active .ad-fig__box img,.ad-fig:active .ad-fig__box video{' +
      'transform:scale(1.1);will-change:transform;}' +
      // the tap answer under hover:none — the press flashes the zoom + cue fast
      // enough to be felt before navigation (tap-to-open stays the action)
      '.ad-fig:active .ad-fig__box img,.ad-fig:active .ad-fig__box video,' +
      '.ad-fig--tint:active .ad-fig__box::after{transition-duration:160ms;}' +
      '.ad-fig--tint .ad-fig__box::after,.ad-fig--lift .ad-fig__box::after{' +
      'content:"";position:absolute;inset:0;pointer-events:none;' +
      'transition:opacity ' + TRANSIT + ';}' +
      '.ad-fig--tint .ad-fig__box::after{background:' + ACCENT + ';opacity:0;}' +
      '.ad-fig--tint:hover .ad-fig__box::after,.ad-fig--tint:focus-within .ad-fig__box::after,' +
      '.ad-fig--tint:active .ad-fig__box::after{opacity:.18;}' +
      '.ad-fig--lift .ad-fig__box::after{background:' + GROUND + ';opacity:.25;}' +
      '.ad-fig--lift:hover .ad-fig__box::after,.ad-fig--lift:focus-within .ad-fig__box::after{opacity:0;}' +
      '.ad-fig--caption figcaption{position:absolute;left:0;right:0;bottom:0;' +
      'padding:.75rem 1rem;font-family:' + MONO + ';font-size:.75rem;' +
      'letter-spacing:.02em;color:' + INK + ';opacity:.6;transform:translateY(6px);' +
      'transition:opacity ' + TRANSIT + ',transform ' + TRANSIT + ';}' +
      '.ad-fig--caption:hover figcaption,.ad-fig--caption:focus-within figcaption{' +
      'opacity:1;transform:translateY(0);}' +
      // No hover under touch → the caption state is permanent, readable at rest.
      '@media (pointer:coarse){' +
      '.ad-fig--caption figcaption{opacity:1;transform:none;}}' +
      // Reduced motion → no scale at all; the cue still applies, instantly.
      '@media (prefers-reduced-motion:reduce){' +
      '.ad-fig__box img,.ad-fig__box video,.ad-fig--tint .ad-fig__box::after,' +
      '.ad-fig--lift .ad-fig__box::after,.ad-fig--caption figcaption{transition:none;}' +
      '.ad-fig--caption figcaption{transform:none;}' +
      '.ad-fig:hover .ad-fig__box img,.ad-fig:hover .ad-fig__box video,' +
      '.ad-fig:focus-within .ad-fig__box img,.ad-fig:focus-within .ad-fig__box video{' +
      'transform:none;will-change:auto;}}';
    document.head.appendChild(s);
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-figure]';
    injectCss();

    var figs = Array.prototype.slice.call(root.querySelectorAll(selector));
    figs.forEach(function (fig) {
      var cue = fig.getAttribute('data-ad-figure');
      if (cue !== 'lift' && cue !== 'caption') cue = 'tint';
      fig.classList.add('ad-fig', 'ad-fig--' + cue);
      if (!fig.querySelector('.ad-fig__box')) {
        var media = fig.querySelector('img,video');
        if (media) {
          var box = document.createElement('span');
          box.className = 'ad-fig__box';
          media.parentNode.insertBefore(box, media);
          box.appendChild(media);
        }
      }
    });

    return {
      destroy: function () {
        figs.forEach(function (fig) {
          var box = fig.querySelector('.ad-fig__box');
          if (box) {
            while (box.firstChild) box.parentNode.insertBefore(box.firstChild, box);
            box.parentNode.removeChild(box);
          }
          fig.classList.remove('ad-fig', 'ad-fig--tint', 'ad-fig--lift', 'ad-fig--caption');
        });
        var s = document.getElementById(CSS_ID);
        if (s) s.parentNode.removeChild(s);
      }
    };
  }

  global.awardFigureHover = { init: init };
})(typeof window !== 'undefined' ? window : this);
