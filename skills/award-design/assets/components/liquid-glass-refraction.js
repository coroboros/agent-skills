/*
 * liquid-glass-refraction — the refraction end of the glass register
 * (style anchor: Apple Liquid Glass / Vision Pro — the WWDC-2025 surface the
 * DNA credentials; Igloo Inc's frost panels are the frost END this component
 * deliberately exceeds). An SVG feDisplacementMap lens BENDS the content
 * behind the glass: a red/green ramp lens map displaces the backdrop
 * radially through backdrop-filter:url(), so straight lines behind the
 * panel visibly kink at the rim — genuine refraction, never just
 * backdrop-filter:blur. The pane is wrapped in the Doppelrand nested-radius
 * shell: outer hairline border at the outer radius, an inner core inset
 * highlight at the concentric inner radius (outer minus inset — the
 * glass-card rule, restated here). Ruled DISTINCT from glass-card: that
 * surface ships backdrop blur(24px) saturate(1.2) + the inset highlight and
 * "no displacement/refraction" (its own header) — glass-card IS this
 * component's declared floor, and the frost fallback below restates its
 * recipe under this namespace so the two never co-init on one element.
 * Floors (the gap's own order — fine-pointer/high-power only): coarse
 * pointers, Save-Data, and engines that cannot resolve an SVG url() in
 * backdrop-filter all get the plain frost; where even backdrop-filter is
 * missing the ground mix rises so text stays readable. The surface has no
 * motion of its own, so prefers-reduced-motion needs nothing disabled — the
 * refraction is a still material, fully legible at rest, and a dead script
 * leaves the builder's own panel styling standing.
 *
 * Expected markup — the builder authors the panel and its contents:
 *   <div data-ad-refract> … content … </div>
 *
 * Usage:  awardLiquidGlassRefraction.init(root, { selector, strength })
 *   root      Element|Document  scope (default document)
 *   selector  string  panels (default '[data-ad-refract]')
 *   strength  number  displacement as a fraction of the panel box
 *                     (default 0.16 — drive-verified the visible-bend floor;
 *                     negative flips bend direction)
 * Returns { destroy() }. Idempotent per panel.
 *
 * Tokens: --ad-ground-2 (pane ground mixes), --ad-ink (hairline + highlight).
 *
 * A11y + perf: the filter defs node is aria-hidden and zero-sized; the
 * displacement is a static material (no per-frame work, nothing animates);
 * the builder keeps body text on glass at >= 72% ink for contrast.
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-liquid-glass-refraction-css';
  var DEFS_ID = 'ad-lgr-defs';
  var FILTER_ID = 'ad-lgr-displace';
  var GROUND2 = 'var(--ad-ground-2,oklch(18% 0.01 260))';
  var INK = 'var(--ad-ink,oklch(96% 0 0))';

  var saveData = function () {
    var c = global.navigator && global.navigator.connection;
    return !!(c && c.saveData);
  };
  var finePointer = function () {
    return global.matchMedia && global.matchMedia('(hover: hover) and (pointer: fine)').matches;
  };
  var supportsRefraction = function () {
    return !!(global.CSS && CSS.supports && (
      CSS.supports('backdrop-filter', 'url(#' + FILTER_ID + ')') ||
      CSS.supports('-webkit-backdrop-filter', 'url(#' + FILTER_ID + ')')));
  };

  // The lens map: R ramps 0->255 across x, G ramps 0->255 across y (screen-
  // blended), so the displacement is a linear field — a uniform lens whose
  // bend is read where the pane's rim breaks the continuity of what is behind.
  var LENS_MAP = 'data:image/svg+xml,' + encodeURIComponent(
    '<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512">' +
    '<defs>' +
    '<linearGradient id="r" x1="0" y1="0" x2="1" y2="0">' +
    '<stop offset="0" stop-color="#000"/><stop offset="1" stop-color="#f00"/>' +
    '</linearGradient>' +
    '<linearGradient id="g" x1="0" y1="0" x2="0" y2="1">' +
    '<stop offset="0" stop-color="#000"/><stop offset="1" stop-color="#0f0"/>' +
    '</linearGradient>' +
    '</defs>' +
    '<rect width="512" height="512" fill="url(#r)"/>' +
    '<rect width="512" height="512" fill="url(#g)" style="mix-blend-mode:screen"/>' +
    '</svg>');

  function injectDefs(strength) {
    if (document.getElementById(DEFS_ID)) return;
    var NS = 'http://www.w3.org/2000/svg';
    var svg = document.createElementNS(NS, 'svg');
    svg.id = DEFS_ID;
    svg.setAttribute('aria-hidden', 'true');
    svg.setAttribute('width', '0');
    svg.setAttribute('height', '0');
    svg.style.cssText = 'position:absolute;width:0;height:0;overflow:hidden;';
    var filter = document.createElementNS(NS, 'filter');
    filter.id = FILTER_ID;
    // objectBoundingBox primitives: the map stretches to each pane's own box
    // and the displacement scale reads as a fraction of it — one filter
    // serves every pane at every size
    filter.setAttribute('primitiveUnits', 'objectBoundingBox');
    filter.setAttribute('x', '0%');
    filter.setAttribute('y', '0%');
    filter.setAttribute('width', '100%');
    filter.setAttribute('height', '100%');
    var img = document.createElementNS(NS, 'feImage');
    img.setAttribute('href', LENS_MAP);
    img.setAttribute('x', '0');
    img.setAttribute('y', '0');
    img.setAttribute('width', '1');
    img.setAttribute('height', '1');
    img.setAttribute('preserveAspectRatio', 'none');
    img.setAttribute('result', 'map');
    var disp = document.createElementNS(NS, 'feDisplacementMap');
    disp.setAttribute('in', 'SourceGraphic');
    disp.setAttribute('in2', 'map');
    disp.setAttribute('scale', String(strength));
    disp.setAttribute('xChannelSelector', 'R');
    disp.setAttribute('yChannelSelector', 'G');
    var sat = document.createElementNS(NS, 'feColorMatrix');
    sat.setAttribute('type', 'saturate');
    sat.setAttribute('values', '1.12');
    filter.appendChild(img);
    filter.appendChild(disp);
    filter.appendChild(sat);
    svg.appendChild(filter);
    document.body.appendChild(svg);
  }

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      // the Doppelrand shell — outer hairline at 22px, inner core at 18px
      // (outer minus the 4px inset: the concentric-radius rule)
      '.ad-lgr{position:relative;border-radius:22px;' +
        'border:1px solid color-mix(in oklch,' + INK + ' 24%,transparent);' +
        'background:color-mix(in oklch,' + GROUND2 + ' 12%,transparent);}' +
      '.ad-lgr::before{content:"";position:absolute;inset:4px;border-radius:18px;' +
        'pointer-events:none;' +
        'box-shadow:inset 0 1px 0 color-mix(in oklch,' + INK + ' 30%,transparent),' +
        'inset 0 0 18px color-mix(in oklch,' + INK + ' 5%,transparent);}' +
      '.ad-lgr--refract{' +
        '-webkit-backdrop-filter:url(#' + FILTER_ID + ');' +
        'backdrop-filter:url(#' + FILTER_ID + ');}' +
      // the frost floor — the glass-card recipe restated under this
      // namespace (never co-init glass-card on the same element)
      '.ad-lgr--frost{' +
        'background:color-mix(in oklch,' + GROUND2 + ' 55%,transparent);' +
        '-webkit-backdrop-filter:blur(24px) saturate(1.2);' +
        'backdrop-filter:blur(24px) saturate(1.2);}' +
      '@supports not ((backdrop-filter:blur(1px)) or (-webkit-backdrop-filter:blur(1px)))' +
      '{.ad-lgr--frost{background:color-mix(in oklch,' + GROUND2 + ' 82%,transparent);}}';
    document.head.appendChild(s);
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-refract]';
    // 0.16 is the drive-verified floor where the bend is READ in a still
    // frame (0.055 tested imperceptible at a glance over a night plate)
    var strength = opts.strength != null ? opts.strength : 0.16;
    injectCss();

    var refract = supportsRefraction() && finePointer() && !saveData();
    if (refract) injectDefs(strength);

    var panels = [];
    Array.prototype.forEach.call(root.querySelectorAll(selector), function (el) {
      if (el.__adLgr) return;
      el.__adLgr = true;
      el.classList.add('ad-lgr', refract ? 'ad-lgr--refract' : 'ad-lgr--frost');
      panels.push(el);
    });

    return {
      destroy: function () {
        panels.forEach(function (el) {
          el.classList.remove('ad-lgr', 'ad-lgr--refract', 'ad-lgr--frost');
          delete el.__adLgr;
        });
        panels = [];
        var d = document.getElementById(DEFS_ID);
        if (d && d.parentNode) d.parentNode.removeChild(d);
        var s = document.getElementById(CSS_ID);
        if (s) s.parentNode.removeChild(s);
      }
    };
  }

  global.awardLiquidGlassRefraction = { init: init };
})(typeof window !== 'undefined' ? window : this);
