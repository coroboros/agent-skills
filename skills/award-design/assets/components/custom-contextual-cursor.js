/*
 * custom-contextual-cursor — the pointer chrome as a first-class element
 * (winners: DICH Fashion — SOTD+Dev 2025-06, three section-swapped cursor
 * variants: landing 'minimal hypnotic', case 'denser electric', transitions
 * 'barely-there glimmer'; Cuberto — contextual labelled state over media,
 * carried-verified; Warhol Arts drives type from the same pointer position).
 * A two-part chrome — a tight dot plus a LAGGING ring (the ring lerps
 * ~0.1-0.2 toward the real pointer; the lag IS the character) — that morphs
 * by CONTEXT: it grows and surfaces a label over declared media/drag zones,
 * shrinks to a dot over text, takes a modest grow over links and buttons,
 * compresses on press, and swaps its whole costume per section via the
 * DICH-verified variant swap. The bold-maximal defining hover affordance —
 * distinct from the trail/field channels (cursor-spawn-trail,
 * cursor-proximity-typefield) and from the quiet registers' chrome
 * (minimal-cursor-signature is the monochrome minimalist slot;
 * cursor-verb-label is the field-scoped verb teacher beside specific
 * operables). One cursor component per page, ever.
 * Touch: hidden entirely (pointer:coarse never builds a node) — the
 * affordances it signals degrade to each element's own tap/press answer, and
 * any label it surfaces must exist as the zone's own visible affordance too,
 * so nothing is gated behind the chrome. Reduced motion: fully dormant,
 * native cursor stands.
 *
 * Context + variant markup (all optional — bare init gives dot+ring):
 *   <section data-ad-cursor-variant="electric">…</section>
 *   <figure data-ad-cursor-zone="VIEW">…</figure>
 *
 * Usage:  awardContextualCursor.init(root, opts)
 *   root          Element|Document  kept for the library contract
 *   lerp          0..1    ring follow per frame (default 0.16 — the winner's
 *                         ~0.1-0.2 window; the dot rides at 0.42)
 *   textSelector  string  elements the dot shrinks over
 *                         (default 'p,h1,h2,h3,h4,h5,h6,li,blockquote')
 *   linkSelector  string  targets that grow the ring modestly
 *                         (default 'a,button,[data-ad-cursor]')
 * Returns { destroy() }. Idempotent — one page-level chrome; repeat init
 * calls return it. Re-evaluates its own gate on pointer/reduce media-query
 * changes (a convertible flipping to touch tears the chrome down).
 *
 * A11y + perf: both layers are aria-hidden and pointer-events:none — the
 * chrome never intercepts a click or carries focus (the element's own
 * focus-visible does); the native cursor hides only via a JS-applied class.
 * Compositor-only: two promoted fixed nodes, transform/opacity, one rAF that
 * parks when the pointer leaves or the tab hides. Delegated pointerover
 * handles context — zero rebinding when sections re-render.
 *
 * Tokens: --ad-ink (dot + ring ink), --ad-accent (electric variant + label
 * chrome), --ad-ground (label text), --ad-font-mono (label face),
 * --ad-dur-base + --ad-ease-signature (the morph register).
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-contextual-cursor-css';
  var DOT_LERP = 0.42;
  var GROW_ZONE = 2.4;   // over a declared media/drag zone
  var GROW_LINK = 1.5;   // over links/buttons
  var SHRINK_TEXT = 0.5; // over prose — the reading state
  var PRESS = 0.65;      // pointerdown compress

  var reduce = function () {
    return !!(global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches);
  };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var ink = 'var(--ad-ink,oklch(96% 0 0))';
    var accent = 'var(--ad-accent,oklch(62% 0.2 25))';
    var morph = 'var(--ad-dur-base,420ms) var(--ad-ease-signature,cubic-bezier(.16,1,.3,1))';
    var s = document.createElement('style');
    s.id = CSS_ID;
    // Outer nodes are pure trackers (rAF writes their transform); every morph
    // rides an INNER element, so a scale transition never fights the tracker.
    s.textContent =
      '.ad-ccc{position:fixed;left:0;top:0;pointer-events:none;z-index:2147483646;' +
      'opacity:0;will-change:transform;transition:opacity 220ms ease;}' +
      '.ad-ccc.is-on{opacity:1;}' +
      '.ad-ccc__dot i{position:absolute;left:-4px;top:-4px;width:8px;height:8px;' +
      'border-radius:50%;background:' + ink + ';' +
      'transition:transform ' + morph + ',background-color ' + morph + ';}' +
      '.ad-ccc__ring i{position:absolute;left:-18px;top:-18px;width:36px;height:36px;' +
      'border-radius:999px;border:1.5px solid ' + ink + ';opacity:.55;box-sizing:border-box;' +
      'transition:transform ' + morph + ',opacity ' + morph + ',background-color ' + morph +
      ',border-color ' + morph + ';}' +
      '.ad-ccc__ring span{position:absolute;left:-18px;top:-18px;' +
      'width:36px;height:36px;display:grid;place-items:center;' +
      'font-family:var(--ad-font-mono,ui-monospace,monospace);' +
      'font-size:.62rem;letter-spacing:.12em;text-transform:uppercase;white-space:nowrap;' +
      'color:var(--ad-ground,oklch(14% 0.01 260));opacity:0;transform:scale(.6);' +
      'transition:opacity ' + morph + ',transform ' + morph + ';}' +
      // context morphs — the scale rides the inner ring, label fades atop it
      '.ad-ccc__ring[data-ctx="zone"] i{transform:scale(' + GROW_ZONE + ');' +
      'background:' + accent + ';border-color:' + accent + ';opacity:1;}' +
      '.ad-ccc__ring[data-ctx="zone"] span{opacity:1;transform:scale(1);}' +
      '.ad-ccc__ring[data-ctx="link"] i{transform:scale(' + GROW_LINK + ');opacity:.9;}' +
      '.ad-ccc__ring[data-ctx="text"] i{transform:scale(' + SHRINK_TEXT + ');opacity:.3;}' +
      // zone state: the ring + label ARE the cursor — the dot collapses so it
      // never sits over the label's own center
      '.ad-ccc__dot[data-ctx="zone"] i{transform:scale(0);}' +
      // section-swapped costumes — the DICH three (calm is the default above)
      '.ad-ccc__dot[data-variant="electric"] i{background:' + accent + ';}' +
      '.ad-ccc__ring[data-variant="electric"] i{border-color:' + accent + ';' +
      'border-width:2px;opacity:.85;}' +
      '.ad-ccc__dot[data-variant="glimmer"] i{transform:scale(.5);}' +
      '.ad-ccc__ring[data-variant="glimmer"] i{transform:scale(.55);opacity:.22;}' +
      '.ad-ccc__ring[data-variant="glimmer"][data-ctx="zone"] i{transform:scale(' +
      GROW_ZONE * 0.7 + ');opacity:1;}' +
      // press compress wins over any variant rest scale — declared last
      '.ad-ccc__dot[data-press] i{transform:scale(' + PRESS + ');}' +
      '.ad-ccc-hide,.ad-ccc-hide *{cursor:none!important;}';
    document.head.appendChild(s);
  }

  function mqOn(mq, fn) {
    if (mq.addEventListener) mq.addEventListener('change', fn);
    else if (mq.addListener) mq.addListener(fn);
  }
  function mqOff(mq, fn) {
    if (mq.removeEventListener) mq.removeEventListener('change', fn);
    else if (mq.removeListener) mq.removeListener(fn);
  }

  var current = null; // page-level singleton — one chrome keeps init idempotent

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    if (current) return current;
    if (!global.matchMedia) return { destroy: function () {} }; // no gate → native cursor

    var ringLerp = opts.lerp != null ? opts.lerp : 0.16;
    var textSelector = opts.textSelector || 'p,h1,h2,h3,h4,h5,h6,li,blockquote';
    var linkSelector = opts.linkSelector || 'a,button,[data-ad-cursor]';

    var finePointer = global.matchMedia('(hover: hover) and (pointer: fine)');
    var reduceMQ = global.matchMedia('(prefers-reduced-motion: reduce)');
    var docEl = document.documentElement;

    var active = false;
    var dot = null, ring = null, label = null;
    var raf = 0, running = false, inside = false, havePos = false;
    var px = 0, py = 0, dx = 0, dy = 0, rx = 0, ry = 0;

    function want() { return finePointer.matches && !reduce(); }

    function place(el, x, y) {
      el.style.transform = 'translate3d(' + x.toFixed(1) + 'px,' + y.toFixed(1) + 'px,0)';
    }

    function tick() {
      if (!running) { raf = 0; return; }
      dx += (px - dx) * DOT_LERP;
      dy += (py - dy) * DOT_LERP;
      rx += (px - rx) * ringLerp;
      ry += (py - ry) * ringLerp;
      place(dot, dx, dy);
      place(ring, rx, ry);
      raf = global.requestAnimationFrame(tick);
    }
    function start() {
      if (running || !active || !inside || !havePos || document.hidden) return;
      running = true;
      raf = global.requestAnimationFrame(tick);
    }
    function stop() {
      running = false;
      if (raf) { global.cancelAnimationFrame(raf); raf = 0; }
    }
    function show() { dot.classList.add('is-on'); ring.classList.add('is-on'); }
    function hide() { dot.classList.remove('is-on'); ring.classList.remove('is-on'); }

    function onMove(e) {
      px = e.clientX; py = e.clientY;
      if (!havePos) { dx = rx = px; dy = ry = py; havePos = true; }
      inside = true;
      show();
      start();
    }
    function onDocLeave() { inside = false; havePos = false; hide(); stop(); }
    function onVis() { if (document.hidden) stop(); else start(); }

    // Delegated context read — one pass decides zone > link > text, and the
    // section variant rides along; DOM swaps cost zero rebinding.
    function onOver(e) {
      var t = e.target;
      if (!t.closest) return;
      var zone = t.closest('[data-ad-cursor-zone]');
      var ctx = '', text = '';
      if (zone) { ctx = 'zone'; text = zone.getAttribute('data-ad-cursor-zone') || ''; }
      else if (t.closest(linkSelector)) ctx = 'link';
      else if (t.closest(textSelector)) ctx = 'text';
      if (ctx) { ring.setAttribute('data-ctx', ctx); dot.setAttribute('data-ctx', ctx); }
      else { ring.removeAttribute('data-ctx'); dot.removeAttribute('data-ctx'); }
      if (text) label.textContent = text;
      var sec = t.closest('[data-ad-cursor-variant]');
      var v = sec ? sec.getAttribute('data-ad-cursor-variant') : null;
      if (v) { ring.setAttribute('data-variant', v); dot.setAttribute('data-variant', v); }
      else { ring.removeAttribute('data-variant'); dot.removeAttribute('data-variant'); }
    }
    function onDown() { dot.setAttribute('data-press', ''); }
    function onUp() { dot.removeAttribute('data-press'); }

    function activate() {
      if (active) return;
      active = true;
      injectCss();
      var body = document.body || docEl;
      dot = document.createElement('div');
      dot.className = 'ad-ccc ad-ccc__dot';
      dot.setAttribute('aria-hidden', 'true');
      dot.appendChild(document.createElement('i'));
      ring = document.createElement('div');
      ring.className = 'ad-ccc ad-ccc__ring';
      ring.setAttribute('aria-hidden', 'true');
      ring.appendChild(document.createElement('i'));
      label = document.createElement('span');
      ring.appendChild(label);
      body.appendChild(ring);
      body.appendChild(dot); // dot above the ring
      docEl.classList.add('ad-ccc-hide');
      havePos = false; inside = true;
      document.addEventListener('mousemove', onMove);
      docEl.addEventListener('mouseleave', onDocLeave);
      document.addEventListener('visibilitychange', onVis);
      document.addEventListener('pointerover', onOver);
      document.addEventListener('pointerdown', onDown);
      document.addEventListener('pointerup', onUp);
    }

    function deactivate() {
      if (!active) return;
      active = false;
      stop();
      document.removeEventListener('mousemove', onMove);
      docEl.removeEventListener('mouseleave', onDocLeave);
      document.removeEventListener('visibilitychange', onVis);
      document.removeEventListener('pointerover', onOver);
      document.removeEventListener('pointerdown', onDown);
      document.removeEventListener('pointerup', onUp);
      docEl.classList.remove('ad-ccc-hide'); // restore the native cursor
      if (dot && dot.parentNode) dot.parentNode.removeChild(dot);
      if (ring && ring.parentNode) ring.parentNode.removeChild(ring);
      dot = ring = label = null;
    }

    function evaluate() { if (want()) activate(); else deactivate(); }

    mqOn(finePointer, evaluate);
    mqOn(reduceMQ, evaluate);
    evaluate();

    current = {
      destroy: function () {
        mqOff(finePointer, evaluate);
        mqOff(reduceMQ, evaluate);
        deactivate();
        var css = document.getElementById(CSS_ID);
        if (css && css.parentNode) css.parentNode.removeChild(css);
        current = null;
      }
    };
    return current;
  }

  global.awardContextualCursor = { init: init };
})(typeof window !== 'undefined' ? window : this);
