/*
 * index-hover-preview — the canonical studio-index hover (canon: the
 * Awwwards 'index module' — a list of links each with an image that reveals
 * on hover; documented against Olivier Gillaizeau and Kirschberg nominee
 * entries, canon-documented rather than single-winner-verified). Hovering a
 * project row surfaces its thumbnail in ONE floating preview layer that is
 * cursor-attached — lerped toward the pointer, trailing it — previewing the
 * WORK. Distinct from index-row-hover (spotlight-dim, which lights the ROW)
 * and scramble-decode (which decodes the label): this surfaces the work
 * itself; the two compose on the same index.
 * Mobile fallback (the documented one): the index flips vertical and each
 * row carries its image inline, revealed as the row centers under scroll —
 * an IntersectionObserver banded to the viewport's middle toggles it; no
 * hover is ever required to reach the work. Reduced motion keeps coverage
 * and drops amplitude: the preview still appears and follows, it snaps
 * instead of trailing, and nothing scales or fades.
 *
 * Expected markup — rows opt in with their artwork; the preview img is
 * presentation (alt="", aria-hidden layer), the row's text IS the accessible
 * name:
 *   <div data-ad-index-preview>
 *     <a data-ad-preview-row data-ad-preview-src="…/plate.jpg" href="…">…</a>
 *   </div>
 *
 * Usage:  awardIndexHoverPreview.init(root, opts)
 *   root         Element|Document  scope (default document)
 *   selector     string  index roots (default '[data-ad-index-preview]')
 *   rowSelector  string  rows (default '[data-ad-preview-row]')
 *   lerp         number  pointer-follow smoothing (default 0.14)
 * Returns { destroy() }. Idempotent per index. destroy() removes the float
 * layers, inline figures, observers, listeners, and the stylesheet.
 *
 * Tokens: --ad-ground-2 (the layer's loading ground), --ad-dur-base +
 * --ad-ease-signature (show/hide), --ad-dur-reveal (the centered reveal).
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-index-hover-preview-css';

  var reduce = function () {
    return global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches;
  };
  var finePointer = function () {
    return global.matchMedia && global.matchMedia('(hover: hover) and (pointer: fine)').matches;
  };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      // the one floating layer — fixed, promoted, never interactive
      '.ad-idxprev__float{position:fixed;left:0;top:0;z-index:60;' +
      'width:clamp(200px,22vw,320px);aspect-ratio:4/3;overflow:hidden;' +
      'pointer-events:none;opacity:0;will-change:transform;' +
      'background:var(--ad-ground-2,oklch(18% 0.01 260));' +
      'transition:opacity var(--ad-dur-base,420ms) ' +
      'var(--ad-ease-signature,cubic-bezier(.16,1,.3,1));}' +
      '.ad-idxprev__float.is-on{opacity:1;}' +
      '.ad-idxprev__float img{display:block;width:100%;height:100%;object-fit:cover;}' +
      // inline figures exist only for the coarse-pointer index
      '.ad-idxprev__inline{display:none;margin:0;overflow:hidden;}' +
      '@media (hover: none), (pointer: coarse){' +
      '.ad-idxprev__float{display:none;}' +
      '.ad-idxprev__inline{display:block;}' +
      '.ad-idxprev__inline img{display:block;width:100%;aspect-ratio:16/10;' +
      'object-fit:cover;opacity:.25;filter:grayscale(60%);' +
      'transition:opacity var(--ad-dur-reveal,800ms) ' +
      'var(--ad-ease-signature,cubic-bezier(.16,1,.3,1)),' +
      'filter var(--ad-dur-reveal,800ms) ' +
      'var(--ad-ease-signature,cubic-bezier(.16,1,.3,1));}' +
      '.is-centered .ad-idxprev__inline img{opacity:1;filter:none;}}' +
      // reduced motion: coverage stays, amplitude goes — everything instant/static
      '@media (prefers-reduced-motion:reduce){' +
      '.ad-idxprev__float{transition:none;}' +
      '.ad-idxprev__inline img{transition:none;opacity:1;filter:none;}}';
    document.head.appendChild(s);
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-index-preview]';
    var rowSelector = opts.rowSelector || '[data-ad-preview-row]';
    var lerpK = opts.lerp != null ? opts.lerp : 0.14;

    injectCss();
    var fine = finePointer();
    var indexes = [];

    Array.prototype.forEach.call(root.querySelectorAll(selector), function (index) {
      if (index.__adIdxPrev) return; // idempotent
      var rows = Array.prototype.slice.call(index.querySelectorAll(rowSelector));
      if (!rows.length) return;

      var unit = { index: index, io: null, float: null, raf: 0, listeners: [] };

      if (fine) {
        // ---- fine pointer: one cursor-attached floating preview ----------
        var float = document.createElement('figure');
        float.className = 'ad-idxprev__float';
        float.setAttribute('aria-hidden', 'true');
        var img = document.createElement('img');
        img.alt = '';
        img.decoding = 'async';
        float.appendChild(img);
        index.appendChild(float);
        unit.float = float;

        var tx = 0, ty = 0, cx = 0, cy = 0, on = false;

        function apply() {
          // centered on the pointer, slightly ahead of it
          float.style.transform =
            'translate3d(' + (cx + 20).toFixed(1) + 'px,' + (cy - 40).toFixed(1) + 'px,0) ' +
            'translate(0,-50%)';
        }
        function frame() {
          unit.raf = 0;
          if (reduce()) { cx = tx; cy = ty; } // snap — no trailing under reduce
          else { cx += (tx - cx) * lerpK; cy += (ty - cy) * lerpK; }
          apply();
          var settledNow = Math.abs(tx - cx) < 0.3 && Math.abs(ty - cy) < 0.3;
          // the loop runs only while shown or still traveling — no idle rAF
          if (on || !settledNow) unit.raf = global.requestAnimationFrame(frame);
        }
        function wake() {
          if (!unit.raf) unit.raf = global.requestAnimationFrame(frame);
        }

        var onOver = function (e) {
          var row = e.target && e.target.closest ? e.target.closest(rowSelector) : null;
          if (!row || !index.contains(row)) return;
          var src = row.getAttribute('data-ad-preview-src');
          if (!src) return;
          if (img.getAttribute('src') !== src) img.src = src;
          if (!on) {
            on = true;
            // first show lands at the pointer, not lerped in from 0,0
            cx = tx = e.clientX; cy = ty = e.clientY;
            apply();
            float.classList.add('is-on');
          }
          wake();
        };
        var onMove = function (e) {
          if (!on) return;
          tx = e.clientX; ty = e.clientY;
          wake();
        };
        var onLeave = function () {
          if (!on) return;
          on = false;
          float.classList.remove('is-on');
        };
        index.addEventListener('pointerover', onOver);
        index.addEventListener('pointermove', onMove, { passive: true });
        index.addEventListener('pointerleave', onLeave);
        unit.listeners.push(['pointerover', onOver], ['pointermove', onMove], ['pointerleave', onLeave]);
      } else {
        // ---- coarse pointer: inline figures revealed as rows center ------
        rows.forEach(function (row) {
          var src = row.getAttribute('data-ad-preview-src');
          if (!src || row.querySelector('.ad-idxprev__inline')) return;
          var fig = document.createElement('figure');
          fig.className = 'ad-idxprev__inline';
          var im = document.createElement('img');
          im.alt = '';
          im.loading = 'lazy';
          im.decoding = 'async';
          im.src = src;
          fig.appendChild(im);
          row.appendChild(fig);
        });
        if ('IntersectionObserver' in global) {
          // the viewport's middle band: a row is "centered" inside it
          unit.io = new IntersectionObserver(function (entries) {
            entries.forEach(function (e) {
              e.target.classList.toggle('is-centered', e.isIntersecting);
            });
          }, { rootMargin: '-40% 0px -40% 0px' });
          rows.forEach(function (row) { unit.io.observe(row); });
        } else {
          rows.forEach(function (row) { row.classList.add('is-centered'); });
        }
      }

      index.__adIdxPrev = unit;
      indexes.push(unit);
    });

    return {
      destroy: function () {
        indexes.forEach(function (unit) {
          if (unit.raf) global.cancelAnimationFrame(unit.raf);
          unit.listeners.forEach(function (l) {
            unit.index.removeEventListener(l[0], l[1]);
          });
          if (unit.io) unit.io.disconnect();
          if (unit.float && unit.float.parentNode) unit.float.parentNode.removeChild(unit.float);
          Array.prototype.forEach.call(
            unit.index.querySelectorAll('.ad-idxprev__inline'),
            function (fig) { if (fig.parentNode) fig.parentNode.removeChild(fig); }
          );
          Array.prototype.forEach.call(
            unit.index.querySelectorAll('.is-centered'),
            function (row) { row.classList.remove('is-centered'); }
          );
          delete unit.index.__adIdxPrev;
        });
        var s = document.getElementById(CSS_ID);
        if (s && s.parentNode) s.parentNode.removeChild(s);
      }
    };
  }

  global.awardIndexHoverPreview = { init: init };
})(typeof window !== 'undefined' ? window : this);
