/*
 * minimal-cursor-signature — the restraint-compatible cursor slot (winner:
 * Pacome Pertant, Awwwards 'Mouse trail' feature tag). A small MONOCHROME dot
 * for the quiet registers — the pointer layer the minimalist element_states
 * lacked. Two modes:
 *   dot    one ink dot rides the pointer on a soft lerp and becomes the
 *          cursor (native hidden); over interactive targets it scales up,
 *          on press it compresses — the whole response lives in one dot.
 *   trail  a short chain of decaying ink dots lerps behind the NATIVE cursor
 *          (kept visible) — the lightweight mouse-trail expression.
 * Deliberately no color spectacle: reads --ad-ink only, never the accent —
 * the quiet is the archetype. Fine-pointer only (matchMedia('(pointer:fine)'));
 * coarse/touch and reduced-motion never build a single node — fully dormant.
 * The layers are pointer-events:none + aria-hidden, so the cursor never gates
 * content, intercepts a click, or touches focus order; mix-blend difference
 * keeps the monochrome dot legible over any ground.
 *
 * Usage:  awardMinimalCursor.init(root, { mode, targetSelector, lerp })
 *   root            Element|Document  kept for the library contract
 *   mode            string  'dot' | 'trail' (default 'dot')
 *   targetSelector  string  interactive targets that grow the dot
 *                           (default 'a,button,[data-ad-cursor]')
 *   lerp            0..1    follow easing per frame (default 0.4 dot / 0.3 trail)
 * Returns { destroy() }. Idempotent — one page-level cursor; repeat init
 * calls return it. The rAF loop pauses when the tab hides and when the
 * pointer leaves the window; transform-only on promoted layers.
 *
 * Tokens: --ad-ink (the dot — the component's only color read).
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-minimal-cursor-css';
  var TRAIL_N = 6;
  var GROW = 2.6;   // over an interactive target
  var PRESS = 0.6;  // while the button is down — the quiet press answer

  var reduce = function () {
    return !!(global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches);
  };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      '.ad-mincur{position:fixed;top:0;left:0;width:10px;height:10px;' +
      'margin:-5px 0 0 -5px;border-radius:50%;' +
      'background:var(--ad-ink,oklch(96% 0 0));mix-blend-mode:difference;' +
      'pointer-events:none;z-index:2147483647;opacity:0;will-change:transform;' +
      'transition:opacity 220ms ease;}' +
      '.ad-mincur--on{opacity:1;}' +
      // dot mode replaces the native cursor; trail mode never sets this class
      '.ad-mincur-hide,.ad-mincur-hide *{cursor:none!important;}';
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

  var current = null; // page-level singleton — one cursor keeps init idempotent

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    if (current) return current;
    if (!global.matchMedia) return { destroy: function () {} }; // no gate → native cursor

    var mode = opts.mode === 'trail' ? 'trail' : 'dot';
    var targetSelector = opts.targetSelector || 'a,button,[data-ad-cursor]';
    var lerp = opts.lerp != null ? opts.lerp : (mode === 'trail' ? 0.3 : 0.4);

    var finePointer = global.matchMedia('(pointer: fine)');
    var reduceMQ = global.matchMedia('(prefers-reduced-motion: reduce)');
    var docEl = document.documentElement;

    var active = false;
    var dots = [];        // [{el,x,y}] — index 0 is the lead
    var raf = 0, running = false, inside = false, havePos = false;
    var px = 0, py = 0;
    var scale = 1, targetScale = 1;
    var over = false, pressed = false;

    function want() { return finePointer.matches && !reduce(); }

    function retarget() {
      targetScale = pressed ? PRESS : (over ? GROW : 1);
    }

    function tick() {
      if (!running) { raf = 0; return; }
      scale += (targetScale - scale) * 0.2;
      var tx = px, ty = py;
      for (var i = 0; i < dots.length; i++) {
        var d = dots[i];
        d.x += (tx - d.x) * lerp;
        d.y += (ty - d.y) * lerp;
        // decay through the chain: each dot chases the one before it
        var s = i === 0 ? scale : Math.max(0.15, 1 - i / TRAIL_N);
        d.el.style.transform = 'translate3d(' + d.x + 'px,' + d.y + 'px,0) scale(' + s + ')';
        tx = d.x; ty = d.y;
      }
      raf = requestAnimationFrame(tick);
    }

    function start() {
      if (running || !active || !inside || !havePos || document.hidden) return;
      running = true;
      raf = requestAnimationFrame(tick);
    }
    function stop() {
      running = false;
      if (raf) { cancelAnimationFrame(raf); raf = 0; }
    }

    function show() { dots.forEach(function (d) { d.el.classList.add('ad-mincur--on'); }); }
    function hide() { dots.forEach(function (d) { d.el.classList.remove('ad-mincur--on'); }); }

    function onMove(e) {
      px = e.clientX; py = e.clientY;
      if (!havePos) {
        dots.forEach(function (d) { d.x = px; d.y = py; }); // snap on first sight
        havePos = true;
      }
      inside = true;
      show();
      start();
    }
    function onDocLeave() { inside = false; havePos = false; hide(); stop(); }
    function onDocEnter() { inside = true; start(); }
    function onVis() { if (document.hidden) stop(); else start(); }

    // Delegated — the growth survives DOM swaps with zero rebinding.
    function onOver(e) {
      var t = e.target.closest && e.target.closest(targetSelector);
      if (t) { over = true; retarget(); }
    }
    function onOut(e) {
      var t = e.target.closest && e.target.closest(targetSelector);
      if (!t) return;
      var to = e.relatedTarget;
      if (to && t.contains(to)) return; // still inside the same target
      over = false; retarget();
    }
    function onDown() { pressed = true; retarget(); }
    function onUp() { pressed = false; retarget(); }

    function activate() {
      if (active) return;
      active = true;
      injectCss();
      var body = document.body || docEl;
      var n = mode === 'trail' ? TRAIL_N : 1;
      for (var i = 0; i < n; i++) {
        var el = document.createElement('div');
        el.className = 'ad-mincur';
        el.setAttribute('aria-hidden', 'true');
        body.appendChild(el);
        dots.push({ el: el, x: 0, y: 0 });
      }
      if (mode === 'dot') docEl.classList.add('ad-mincur-hide');
      havePos = false; inside = true; scale = 1; targetScale = 1;
      over = false; pressed = false;
      document.addEventListener('mousemove', onMove);
      docEl.addEventListener('mouseleave', onDocLeave);
      docEl.addEventListener('mouseenter', onDocEnter);
      document.addEventListener('visibilitychange', onVis);
      document.addEventListener('pointerover', onOver);
      document.addEventListener('pointerout', onOut);
      document.addEventListener('pointerdown', onDown);
      document.addEventListener('pointerup', onUp);
    }

    function deactivate() {
      if (!active) return;
      active = false;
      stop();
      document.removeEventListener('mousemove', onMove);
      docEl.removeEventListener('mouseleave', onDocLeave);
      docEl.removeEventListener('mouseenter', onDocEnter);
      document.removeEventListener('visibilitychange', onVis);
      document.removeEventListener('pointerover', onOver);
      document.removeEventListener('pointerout', onOut);
      document.removeEventListener('pointerdown', onDown);
      document.removeEventListener('pointerup', onUp);
      docEl.classList.remove('ad-mincur-hide'); // restore native cursor
      dots.forEach(function (d) {
        if (d.el.parentNode) d.el.parentNode.removeChild(d.el);
      });
      dots = [];
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

  global.awardMinimalCursor = { init: init };
})(typeof window !== 'undefined' ? window : this);
