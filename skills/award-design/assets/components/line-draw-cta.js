/*
 * line-draw-cta — the drawn-line CTA for photographic / 3D / frosted surfaces
 * (winners: Brunello Cucinelli AI — SOTD Jul 9 2026; Depo Luxe — SOTD Jul 7
 * 2026; Louis Vuitton Collectibles — SOTD Feb 2024). Where a fill flood or a
 * roll would be too heavy over imagery, the hover answer is a LINE: either an
 * SVG ring stroke-draws around a circular CTA (stroke-dashoffset easing to 0
 * over ~.6-.8s on the corpus easing) or a hairline currentColor underline
 * fades in at height .5px, opacity 0->1 over .1-.2s (the Depo Luxe link
 * answer). NO fill flood, NO colour flip of the label — the label never
 * changes; only the line arrives. Leaving mid-draw retracts the line along
 * the same transition (the reversal is CSS's, symmetric by construction).
 * The manifest's other CTA moves are ruled distinct, not aliases:
 * fill-invert-cta floods a solid token, masked-label-swap rolls the label —
 * both too loud for corporate-luxury's photography; this is the third,
 * quieter expression the element canon lacked.
 * Touch: the line is the tap answer — it arrives on :active over a fast
 * flash floor (~140ms), no hover required. Reduced motion: the ring and the
 * underline are PRESENT AT REST (the gap's own order) and nothing animates.
 * No-JS: the CTA is the builder's own styled control — nothing hides, the
 * drawn line is additive chrome.
 *
 * Expected markup — the builder's real controls declare their expression:
 *   <a data-ad-line-cta="ring" class="…circular CTA…">Reserve</a>
 *   <a data-ad-line-cta="underline" href="…">Discover</a>
 *
 * Usage:  awardLineDrawCta.init(root, opts)
 *   root      Element|Document  scope (default document)
 *   selector  string  CTA hosts (default '[data-ad-line-cta]')
 * Returns { destroy() }. Idempotent per host (a second init skips hosts that
 * already carry their ring). destroy() removes the rings, host classes, and
 * the stylesheet.
 *
 * A11y + perf: the ring SVG is aria-hidden and pointer-events:none — the
 * host keeps its own hit area, focus order, and :focus-visible ring;
 * :focus-visible draws the same line as hover (never hover-only). The draw
 * animates stroke-dashoffset and opacity only — no layout, no paint storm.
 *
 * Tokens: --ad-ease-signature (the draw's curve), --ad-ldc-draw (ring draw
 * duration, default 700ms), --ad-ldc-underline (underline fade, default
 * 160ms). The line inks in currentColor — the component never invents color.
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-line-draw-cta-css';
  var SVG_NS = 'http://www.w3.org/2000/svg';

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var ease = 'var(--ad-ease-signature,cubic-bezier(.16,1,.3,1))';
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      '.ad-ldc-host{position:relative;}' +
      // ---- ring: pathLength-normalized circle, drawn from 12 o'clock ------
      '.ad-ldc__ring{position:absolute;inset:0;width:100%;height:100%;' +
      'pointer-events:none;overflow:visible;}' +
      '.ad-ldc__ring circle{fill:none;stroke:currentColor;stroke-width:1.5;' +
      'stroke-linecap:round;stroke-dasharray:1;stroke-dashoffset:1;' +
      'transform:rotate(-90deg);transform-origin:center;' +
      'transition:stroke-dashoffset var(--ad-ldc-draw,700ms) ' + ease + ';}' +
      '[data-ad-line-cta="ring"]:hover .ad-ldc__ring circle,' +
      '[data-ad-line-cta="ring"]:focus-visible .ad-ldc__ring circle{' +
      'stroke-dashoffset:0;}' +
      // ---- underline: hairline currentColor :before that APPEARS ----------
      '[data-ad-line-cta="underline"]{position:relative;}' +
      '[data-ad-line-cta="underline"]::before{content:"";position:absolute;' +
      'left:0;right:0;bottom:-0.15em;height:0.5px;background:currentColor;' +
      'opacity:0;transition:opacity var(--ad-ldc-underline,160ms) ' + ease + ';}' +
      '[data-ad-line-cta="underline"]:hover::before,' +
      '[data-ad-line-cta="underline"]:focus-visible::before{opacity:1;}' +
      // ---- touch: the line is the tap answer — :active over a flash floor -
      '@media (hover:none){' +
      '[data-ad-line-cta="ring"]:active .ad-ldc__ring circle{' +
      'stroke-dashoffset:0;transition-duration:140ms;}' +
      '[data-ad-line-cta="underline"]:active::before{opacity:1;' +
      'transition-duration:140ms;}}' +
      // ---- reduced motion: the line is present at rest, nothing animates --
      '@media (prefers-reduced-motion: reduce){' +
      '.ad-ldc__ring circle{stroke-dashoffset:0;transition:none;}' +
      '[data-ad-line-cta="underline"]::before{opacity:1;transition:none;}}';
    document.head.appendChild(s);
  }

  function makeRing() {
    var svg = document.createElementNS(SVG_NS, 'svg');
    svg.setAttribute('class', 'ad-ldc__ring');
    svg.setAttribute('viewBox', '0 0 100 100');
    svg.setAttribute('aria-hidden', 'true');
    svg.setAttribute('focusable', 'false');
    var c = document.createElementNS(SVG_NS, 'circle');
    c.setAttribute('cx', '50');
    c.setAttribute('cy', '50');
    // stroke centered on r=49 stays inside the 100-box — the draw never
    // spills past the CTA's own circle
    c.setAttribute('r', '49');
    c.setAttribute('pathLength', '1');
    svg.appendChild(c);
    return svg;
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-line-cta]';

    injectCss();
    var mounted = [];
    Array.prototype.forEach.call(root.querySelectorAll(selector), function (el) {
      if (el.getAttribute('data-ad-line-cta') !== 'ring') return; // underline is pure CSS
      if (el.querySelector('.ad-ldc__ring')) return; // idempotent per host
      var hadHostClass = el.classList.contains('ad-ldc-host');
      el.classList.add('ad-ldc-host');
      var ring = makeRing();
      el.appendChild(ring);
      mounted.push({ el: el, ring: ring, hadHostClass: hadHostClass });
    });

    return {
      destroy: function () {
        mounted.forEach(function (m) {
          if (m.ring.parentNode) m.ring.parentNode.removeChild(m.ring);
          if (!m.hadHostClass) m.el.classList.remove('ad-ldc-host');
        });
        mounted = [];
        var s = document.getElementById(CSS_ID);
        if (s && s.parentNode) s.parentNode.removeChild(s);
      }
    };
  }

  global.awardLineDrawCta = { init: init };
})(typeof window !== 'undefined' ? window : this);
