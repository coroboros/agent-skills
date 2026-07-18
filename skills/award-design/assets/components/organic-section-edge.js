/*
 * organic-section-edge — the anti-grid flow boundary (winners: Cyd Stumpel —
 * the contact footer's clip-path edge with an offset shadow riding the
 * accent; the spatial-organic reference DNA — 'shapes flow rather than snap
 * to grids; soft clip-path curves replace rectangular sections'). A
 * section-wrapper utility that carves a soft convex curve into a section's
 * top and/or bottom edge with clip-path: shape(): a quadratic arc whose
 * apex reaches the section's own box edge while the sides sit one curve
 * depth lower — and the SEAM LAW that makes it gapless: the clipped section
 * pulls itself over its neighbor by exactly the curve depth (negative
 * margin) and pads its content clear by the same depth, so the whole curve
 * band is double-painted — the neighbor's ground shows through above the
 * curve, this section's below, and the clip's anti-aliased edge blends into
 * painted ground on BOTH sides at every width (never a hairline of page
 * background). ONE CURVE PER SEAM (drive-caught): two adjacent sections
 * curving INTO the same seam clip each other away near the sides and the
 * inter-curve void exposes the page background — give each seam exactly one
 * curved edge (a data-ad-edge="top bottom" section wants flat neighbors,
 * the winner's own usage: Cyd curves the footer's top only). A still
 * material: no motion, nothing for reduced-motion to disable, and a dead
 * script (or a browser without shape()) leaves a plain straight-edged
 * section — the gap's own degrade.
 *
 * Ruled DISTINCT from clip-reveal (a fire-once MEDIA uncover — this is a
 * SECTION boundary, pure geometry, nothing ever animates) and from the close-panel /
 * form rectangles it wraps (no form owns organic section clipping; this
 * utility composes with any of them). The gap's ellipse() variants were
 * dropped for shape(): a single basic ellipse clips all four corners of a
 * tall section — only a per-edge path curves ONE edge and leaves the rest
 * of the box whole.
 *
 * Markup: any section/wrapper —
 *   <footer data-ad-edge="top">…</footer>
 *   <section data-ad-edge="top bottom" data-ad-edge-shadow>…</section>
 * Attributes:
 *   data-ad-edge          "top" | "bottom" | "top bottom" — which edges curve
 *   data-ad-edge-shadow   opt-in: an accent crescent hugging each curved
 *                         edge (Cyd's offset shadow riding the curve) — two
 *                         same-curve clips intersected, painted in
 *                         --ad-accent, offset by --ad-edge-shadow-offset
 * Stacking: the host gets position:relative + z-index:1 so its curve paints
 * over the neighbor it overlaps.
 *
 * Usage:  awardOrganicSectionEdge.init(root, opts)
 *   root      Element|Document  scope (default document; the stylesheet is
 *                               attribute-driven, one injection serves all)
 * Returns { destroy() }. Idempotent. destroy() removes the stylesheet.
 *
 * Tokens: --ad-edge-depth (curve depth, default clamp(2.5rem, 7vw, 6rem)),
 * --ad-edge-shadow-offset (crescent thickness, default 10px), --ad-accent
 * (the crescent's ink).
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-organic-section-edge-css';
  var DEPTH = 'var(--ad-edge-depth,clamp(2.5rem,7vw,6rem))';
  var OFFSET = 'var(--ad-edge-shadow-offset,10px)';
  var ACCENT = 'var(--ad-accent,oklch(62% 0.2 25))';

  // One curve, defined once: a quadratic from (0,d+lift) to (100%,d+lift)
  // with control (50%, -d+lift) — apex exactly at lift, sides at d+lift.
  // lift shifts the same curve down (the shadow crescent rides on it).
  function topCurve(lift) {
    var d = 'calc(' + DEPTH + ' + ' + lift + ')';
    var c = 'calc(-1 * ' + DEPTH + ' + ' + lift + ')';
    return 'from 0% ' + d + ',curve to 100% ' + d + ' with 50% ' + c;
  }
  function bottomCurve(lift) {
    var d = 'calc(100% - ' + DEPTH + ' - ' + lift + ')';
    var c = 'calc(100% + ' + DEPTH + ' - ' + lift + ')';
    return 'curve to 0% ' + d + ' with 50% ' + c;
  }
  // Full clip shapes — the region the section keeps.
  var SHAPE_TOP =
    'shape(' + topCurve('0px') + ',line to 100% 100%,line to 0% 100%,close)';
  var SHAPE_BOTTOM =
    'shape(from 0% 0%,line to 100% 0%,line to 100% calc(100% - ' + DEPTH + '),' +
    bottomCurve('0px') + ',close)';
  var SHAPE_BOTH =
    'shape(' + topCurve('0px') + ',line to 100% calc(100% - ' + DEPTH + '),' +
    bottomCurve('0px') + ',close)';
  // Crescent caps — everything ABOVE (below) the same curve shifted by the
  // offset; intersected with the host clip they leave only the accent band.
  var CAP_TOP =
    'shape(' + topCurve(OFFSET) + ',line to 100% 0%,line to 0% 0%,close)';
  var CAP_BOTTOM =
    'shape(from 0% 100%,line to 100% 100%,line to 100% calc(100% - ' + DEPTH +
    ' - ' + OFFSET + '),' + bottomCurve(OFFSET) + ',close)';

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      // no shape() support -> none of this applies: straight edges, no
      // overlap (an unclipped overlap would paint over the neighbor)
      '@supports (clip-path: shape(from 0% 0%,line to 100% 100%)){' +
        '[data-ad-edge]{position:relative;z-index:1;}' +
        '[data-ad-edge~="top"]{margin-top:calc(-1 * ' + DEPTH + ');' +
          'padding-top:' + DEPTH + ';clip-path:' + SHAPE_TOP + ';}' +
        '[data-ad-edge~="bottom"]{margin-bottom:calc(-1 * ' + DEPTH + ');' +
          'padding-bottom:' + DEPTH + ';clip-path:' + SHAPE_BOTTOM + ';}' +
        '[data-ad-edge~="top"][data-ad-edge~="bottom"]{clip-path:' + SHAPE_BOTH + ';}' +
        // the accent crescents — absolutely positioned pseudo layers whose
        // own cap clip intersects the host clip into a band on the curve
        '[data-ad-edge-shadow][data-ad-edge~="top"]::before,' +
        '[data-ad-edge-shadow][data-ad-edge~="bottom"]::after{' +
          'content:"";position:absolute;inset:0;pointer-events:none;' +
          'background:' + ACCENT + ';}' +
        '[data-ad-edge-shadow][data-ad-edge~="top"]::before{clip-path:' + CAP_TOP + ';}' +
        '[data-ad-edge-shadow][data-ad-edge~="bottom"]::after{clip-path:' + CAP_BOTTOM + ';}' +
      '}';
    document.head.appendChild(s);
  }

  function init(root, opts) {
    // root/opts kept for the shared init signature; the sheet is
    // attribute-driven so scoping needs no per-element work.
    injectCss();
    return {
      destroy: function () {
        var s = document.getElementById(CSS_ID);
        if (s && s.parentNode) s.parentNode.removeChild(s);
      }
    };
  }

  global.awardOrganicSectionEdge = { init: init };
})(typeof window !== 'undefined' ? window : this);
