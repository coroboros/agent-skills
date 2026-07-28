/*
 * cursor-proximity-typefield — the operable glyph field (winner: Exat —
 * exat.hottype.co, Awwwards SOTD + FWA of the Day + CSSDA Website of the
 * Month 8.83). A grid of glyphs/words where each unit's weight and color are
 * driven by the EUCLIDEAN DISTANCE from the cursor to the unit's center:
 * 7 concentric distance rings map font-weight 900 (innermost) -> 200
 * (outermost) and a color lerp hot -> cold (the winner runs #FF0B00 inner ->
 * #0000cb outer; this component reads the build's tokens instead — hot falls
 * back to --ad-accent, cold to the ink). The archetype's signature operable
 * spectacle: the mechanic that opens Exat's hero AND is its mid-page specimen
 * climax — one mechanic, re-fired, never a competing second spectacle.
 * Ring membership is QUANTIZED — a unit restyles only when it crosses a ring
 * boundary, every style lives in per-ring CSS (JS writes one data attribute),
 * unit centers are cached in client coordinates and re-measured in one
 * batched read pass on scroll/resize, and the field root is contained, so the
 * ~16ms rAF loop never causes page-wide layout. A short linear snap
 * transition on the cells renders the ring steps as the concentric-falloff
 * feel (linear stays legal on continuous channels).
 * Touch (the winner's own answer): 'touch devices receive static grid
 * versions' — the field never splits, the authored composition stands, fully
 * dormant. Reduced motion: the same static composed grid.
 *
 * Expected markup — either glyph mode (the component splits the text) or
 * word-unit mode (the builder authors units, e.g. specimen style names):
 *   <div data-ad-typefield>ABCDEFGHIJKLMNOPQRSTUVWXYZ…</div>
 *   <div data-ad-typefield><span data-tf-unit>Thin</span>…</div>
 *
 * Usage:  awardCursorProximityTypefield.init(root, opts)
 *   root      Element|Document  scope (default document)
 *   selector  string  fields (default '[data-ad-typefield]')
 *   radius    px      the outermost ring's reach (default 480; the 7-ring
 *                     count and the 200->900 sweep are the winner's values
 *                     and are not options)
 * Returns { destroy() }. Idempotent per field. destroy() restores the
 * authored DOM and removes the stylesheet.
 *
 * A11y + perf: split roots keep their accessible name via aria-label; spaces
 * stay real text nodes so glyph rows re-wrap; the loop runs only while the
 * pointer is inside AND the field is on-screen (IntersectionObserver) AND the
 * tab is visible. Writes are attribute flips on ring transitions only.
 *
 * Tokens: --ad-accent (hot fallback), --ad-ink (cold fallback); extensions
 * --ad-tf-hot / --ad-tf-cold (the two color poles), --ad-tf-cell (glyph cell
 * width, default .85em), --ad-tf-snap (ring snap duration, default 160ms).
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-cursor-proximity-typefield-css';
  var RINGS = 7;          // the winner's ring count — a verdict, not a knob
  var W_MIN = 200, W_MAX = 900;

  var reduce = function () {
    return !!(global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches);
  };
  var finePointer = function () {
    return !!(global.matchMedia && global.matchMedia('(hover: hover) and (pointer: fine)').matches);
  };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var hot = 'var(--ad-tf-hot,var(--ad-accent,oklch(62% 0.2 25)))';
    var cold = 'var(--ad-tf-cold,var(--ad-ink,oklch(96% 0 0)))';
    var rules =
      // contain: a weight change reflows inside the field, never the page
      '.ad-tf{contain:layout style;}' +
      '.ad-tf__u{display:inline-block;font-weight:' + W_MIN + ';' +
      'transition:font-weight var(--ad-tf-snap,160ms) linear,' +
      'color var(--ad-tf-snap,160ms) linear;}' +
      // glyph cells sit in em-sized boxes so the weight morph never shifts
      // the grid rhythm (em is weight-independent; ch is not)
      '.ad-tf--glyphs .ad-tf__u{inline-size:var(--ad-tf-cell,.85em);text-align:center;}';
    for (var r = 0; r < RINGS; r++) {
      var w = Math.round(W_MAX - (r * (W_MAX - W_MIN)) / (RINGS - 1));
      var mix = Math.round(100 - (r * 100) / (RINGS - 1));
      rules +=
        '.ad-tf__u[data-tf-ring="' + r + '"]{font-weight:' + w + ';' +
        'color:color-mix(in oklab,' + hot + ' ' + mix + '%,' + cold + ');}';
    }
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent = rules;
    document.head.appendChild(s);
  }

  // Split the field's text into glyph cells — spaces stay real text nodes so
  // rows keep their break opportunities; the root is named with the whole
  // text so a screen reader never spells "E X A T".
  function splitGlyphs(el) {
    if (el.__adTfHTML == null) el.__adTfHTML = el.innerHTML;
    else el.innerHTML = el.__adTfHTML;
    var text = el.textContent.replace(/\s+/g, ' ').trim();
    if (!el.hasAttribute('aria-label')) { el.setAttribute('aria-label', text); el.__adTfLabeled = true; }
    el.textContent = '';
    var units = [];
    for (var c = 0; c < text.length; c++) {
      var ch = text.charAt(c);
      if (ch === ' ') { el.appendChild(document.createTextNode(' ')); continue; }
      var box = document.createElement('span');
      box.className = 'ad-tf__u';
      box.textContent = ch;
      el.appendChild(box);
      units.push(box);
    }
    return units;
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-typefield]';
    var radius = opts.radius != null ? opts.radius : 480;

    // Static composed grid on touch AND under reduce — the authored text
    // stands untouched; the winner ships exactly this.
    if (reduce() || !finePointer()) return { destroy: function () {} };

    injectCss();
    var fields = [];
    // ring thresholds, squared — the loop compares dist² and never sqrts
    var bounds2 = [];
    for (var r = 1; r <= RINGS; r++) {
      var d = (radius * r) / RINGS;
      bounds2.push(d * d);
    }

    Array.prototype.forEach.call(root.querySelectorAll(selector), function (el) {
      if (el.__adTfField) return; // idempotent per field
      var authored = el.querySelectorAll('[data-tf-unit]');
      var units, glyphs = authored.length === 0;
      if (glyphs) units = splitGlyphs(el);
      else {
        units = Array.prototype.slice.call(authored);
        units.forEach(function (u) { u.classList.add('ad-tf__u'); });
      }
      el.classList.add('ad-tf');
      if (glyphs) el.classList.add('ad-tf--glyphs');

      var f = {
        el: el, units: units, glyphs: glyphs,
        centers: null,        // [{x,y,ring}] in client coords
        dirty: true,          // re-measure before the next frame
        px: 0, py: 0,
        inside: false, onScreen: true,
        raf: 0
      };
      el.__adTfField = f;
      fields.push(f);
    });
    if (!fields.length) return { destroy: function () {} };

    // one batched read pass — all rects, then all writes happen in CSS
    function measure(f) {
      f.centers = f.units.map(function (u) {
        var r = u.getBoundingClientRect();
        return { x: r.left + r.width / 2, y: r.top + r.height / 2, ring: -1 };
      });
      f.dirty = false;
    }

    function frame(f) {
      f.raf = 0;
      if (!f.inside || !f.onScreen || document.hidden) return;
      if (f.dirty || !f.centers) measure(f);
      for (var i = 0; i < f.centers.length; i++) {
        var c = f.centers[i];
        var dx = f.px - c.x, dy = f.py - c.y;
        var d2 = dx * dx + dy * dy;
        var ring = RINGS; // outside every ring → rest
        for (var b = 0; b < RINGS; b++) {
          if (d2 <= bounds2[b]) { ring = b; break; }
        }
        if (ring !== c.ring) { // quantized: write only on a ring transition
          c.ring = ring;
          if (ring === RINGS) f.units[i].removeAttribute('data-tf-ring');
          else f.units[i].setAttribute('data-tf-ring', String(ring));
        }
      }
      f.raf = global.requestAnimationFrame(function () { frame(f); });
    }
    function wake(f) {
      if (!f.raf) f.raf = global.requestAnimationFrame(function () { frame(f); });
    }
    function release(f) {
      // pointer gone → every unit settles back to the composed rest state
      if (f.raf) { global.cancelAnimationFrame(f.raf); f.raf = 0; }
      if (!f.centers) return;
      f.centers.forEach(function (c, i) {
        if (c.ring !== RINGS) { c.ring = RINGS; f.units[i].removeAttribute('data-tf-ring'); }
      });
    }

    var bindings = [];
    fields.forEach(function (f) {
      var onEnter = function (e) { f.inside = true; f.px = e.clientX; f.py = e.clientY; wake(f); };
      var onMove = function (e) { f.px = e.clientX; f.py = e.clientY; if (f.inside) wake(f); };
      var onLeave = function () { f.inside = false; release(f); };
      f.el.addEventListener('pointerenter', onEnter);
      f.el.addEventListener('pointermove', onMove, { passive: true });
      f.el.addEventListener('pointerleave', onLeave);
      bindings.push({ f: f, enter: onEnter, move: onMove, leave: onLeave });
    });

    var io = null;
    if ('IntersectionObserver' in global) {
      io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          var f = e.target.__adTfField;
          if (!f) return;
          f.onScreen = e.isIntersecting;
          if (f.onScreen && f.inside) wake(f); else release(f);
        });
      });
      fields.forEach(function (f) { io.observe(f.el); });
    }

    // scroll/resize invalidate the cached centers — one flag, re-read next frame
    var onDirty = function () {
      fields.forEach(function (f) { f.dirty = true; if (f.inside) wake(f); });
    };
    var onVis = function () {
      fields.forEach(function (f) { if (!document.hidden && f.inside) wake(f); });
    };
    global.addEventListener('scroll', onDirty, { passive: true });
    global.addEventListener('resize', onDirty);
    document.addEventListener('visibilitychange', onVis);

    return {
      destroy: function () {
        if (io) io.disconnect();
        global.removeEventListener('scroll', onDirty);
        global.removeEventListener('resize', onDirty);
        document.removeEventListener('visibilitychange', onVis);
        bindings.forEach(function (b) {
          b.f.el.removeEventListener('pointerenter', b.enter);
          b.f.el.removeEventListener('pointermove', b.move);
          b.f.el.removeEventListener('pointerleave', b.leave);
        });
        fields.forEach(function (f) {
          if (f.raf) global.cancelAnimationFrame(f.raf);
          f.el.classList.remove('ad-tf', 'ad-tf--glyphs');
          if (f.el.__adTfHTML != null) { f.el.innerHTML = f.el.__adTfHTML; delete f.el.__adTfHTML; }
          else f.units.forEach(function (u) {
            u.classList.remove('ad-tf__u');
            u.removeAttribute('data-tf-ring');
          });
          if (f.el.__adTfLabeled) { f.el.removeAttribute('aria-label'); delete f.el.__adTfLabeled; }
          delete f.el.__adTfField;
        });
        fields.length = 0;
        var s = document.getElementById(CSS_ID);
        if (s && s.parentNode) s.parentNode.removeChild(s);
      }
    };
  }

  global.awardCursorProximityTypefield = { init: init };
})(typeof window !== 'undefined' ? window : this);
