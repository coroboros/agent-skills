/*
 * grain-grade — film-grain + vignette grade overlay (winner: Siena Film Foundation).
 * One fixed, full-viewport, decorative layer that lays a tiled fractalNoise grain
 * (and an optional darkened-corner vignette) over the whole page for the
 * editorial-dark poster grade. Purely additive: pointer-events:none and aria-hidden,
 * so it never blocks a click, never takes focus, and dies gracefully — no script,
 * no overlay, content fully legible at rest.
 *
 * Usage:  awardGrainGrade.init(root, { opacity, animate, blend, vignette, zIndex })
 *   root      Element|Document  mount scope (default document → body)
 *   opacity   0..1              grain strength (default 0.06)
 *   animate   boolean           shimmer the grain (default true)
 *   blend     mix-blend-mode    grain blend (default 'soft-light')
 *   vignette  boolean           add darkened-corner vignette (default false)
 *   zIndex    number            stack above content, below modals (default 9999)
 * Returns { destroy() }. Idempotent — re-init replaces the prior overlay on the mount.
 *
 * Tokens: --ad-ground (oklch(14% 0.01 260)) tints the vignette toward the page ground.
 *
 * PERF: the grain layer is oversized to 200%×200% and shimmered with a steps(8)
 * translate3d keyframe loop — never background-position. Animating background-position
 * on a fixed full-viewport layer repaints the whole layer every frame; a promoted
 * transform (will-change) composites the same jitter with zero per-frame paint, and
 * the SVG filter rasterizes once into the cached tile. reduced-motion removes the
 * animation (CSS @media, the live source of truth) — the grain stays, just static.
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-grain-grade-css';

  // Grayscale fractalNoise tile — rasterized once by the browser, then tiled and
  // transform-animated; the filter never re-runs per frame.
  var GRAIN_SVG =
    "<svg xmlns='http://www.w3.org/2000/svg' width='160' height='160'>" +
    "<filter id='g'>" +
    "<feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/>" +
    "<feColorMatrix type='saturate' values='0'/>" +
    "</filter>" +
    "<rect width='160' height='160' filter='url(#g)'/>" +
    "</svg>";
  var GRAIN_URI = 'url("data:image/svg+xml,' + encodeURIComponent(GRAIN_SVG) + '")';

  var reduce = function () {
    return global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches;
  };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      '.ad-grain-grade{position:fixed;inset:0;pointer-events:none;overflow:hidden;z-index:9999;}' +
      '.ad-grain-grade__grain{position:absolute;top:-50%;left:-50%;width:200%;height:200%;' +
        'background-image:' + GRAIN_URI + ';background-repeat:repeat;' +
        'opacity:.06;mix-blend-mode:soft-light;will-change:transform;' +
        'animation:ad-gg-shift .8s steps(8) infinite;}' +
      '.ad-grain-grade__vignette{position:absolute;inset:0;' +
        'background:radial-gradient(ellipse at center,transparent 45%,' +
        'color-mix(in oklab,var(--ad-ground,oklch(14% 0.01 260)),black 45%) 125%);}' +
      '.ad-grain-grade[data-ad-static] .ad-grain-grade__grain{animation:none;will-change:auto;}' +
      '@keyframes ad-gg-shift{' +
        '0%{transform:translate3d(0,0,0);}' +
        '12.5%{transform:translate3d(-4%,-3%,0);}' +
        '25%{transform:translate3d(3%,-4%,0);}' +
        '37.5%{transform:translate3d(-3%,4%,0);}' +
        '50%{transform:translate3d(4%,3%,0);}' +
        '62.5%{transform:translate3d(-4%,-2%,0);}' +
        '75%{transform:translate3d(2%,4%,0);}' +
        '87.5%{transform:translate3d(-2%,-4%,0);}' +
        '100%{transform:translate3d(0,0,0);}}' +
      '@media (prefers-reduced-motion: reduce){' +
        '.ad-grain-grade__grain{animation:none;will-change:auto;}}';
    document.head.appendChild(s);
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var opacity = opts.opacity != null ? opts.opacity : 0.06;
    var animate = opts.animate !== false;
    var blend = opts.blend || 'soft-light';
    var vignette = !!opts.vignette;
    var zIndex = opts.zIndex != null ? opts.zIndex : 9999;
    injectCss();

    // Fixed positioning wants a viewport-relative containing block; body is the
    // safe mount (an arbitrary root may be transformed and would trap the overlay).
    var mount = root.nodeType === 9 ? (root.body || root.documentElement) : root;

    // Idempotent: drop any prior overlay this init placed on the same mount.
    if (mount.__adGrainGrade && mount.__adGrainGrade.parentNode) {
      mount.__adGrainGrade.parentNode.removeChild(mount.__adGrainGrade);
    }

    var container = document.createElement('div');
    container.className = 'ad-grain-grade';
    container.setAttribute('aria-hidden', 'true');
    container.style.zIndex = zIndex;
    if (!animate || reduce()) container.setAttribute('data-ad-static', '');

    var grain = document.createElement('div');
    grain.className = 'ad-grain-grade__grain';
    grain.style.opacity = opacity;
    grain.style.mixBlendMode = blend;
    container.appendChild(grain);

    if (vignette) {
      var vig = document.createElement('div');
      vig.className = 'ad-grain-grade__vignette';
      container.appendChild(vig);
    }

    mount.appendChild(container);
    mount.__adGrainGrade = container;

    return {
      destroy: function () {
        if (container.parentNode) container.parentNode.removeChild(container);
        if (mount.__adGrainGrade === container) delete mount.__adGrainGrade;
        // Shared stylesheet: pull it only once the last overlay is gone.
        if (!document.querySelector('.ad-grain-grade')) {
          var s = document.getElementById(CSS_ID);
          if (s && s.parentNode) s.parentNode.removeChild(s);
        }
      }
    };
  }

  global.awardGrainGrade = { init: init };
})(typeof window !== 'undefined' ? window : this);
