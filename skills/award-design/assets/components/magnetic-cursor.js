/*
 * magnetic-cursor — two-layer custom cursor with magnetic snap (winner: Lando Norris, Cuberto).
 * A small dot tracks the pointer 1:1; a larger ring lerps behind it each rAF tick. Over any
 * [data-ad-magnetic] element the ring grows and snaps to that element's box centre while the
 * element itself is nudged a few px toward the pointer — an earned cursor that does real work.
 * Fine-pointer only (matchMedia('(pointer:fine)')); coarse/touch and reduced-motion keep the
 * native pointer untouched — no custom cursor is drawn. The layers are pointer-events:none and
 * aria-hidden, so they never intercept clicks, hijack activation, or trap focus. cursor:none is
 * applied only while active and restored on destroy / when the pointer becomes coarse.
 *
 * Usage:  awardMagneticCursor.init(root, { magnetSelector, ringLerp, pull, pullMax })
 *   root           Element|Document  scope for magnet elements (default document)
 *   magnetSelector string            elements that pull the cursor (default '[data-ad-magnetic]')
 *   ringLerp       0..1              ring follow/snap easing per frame (default 0.15)
 *   pull           0..1              fraction of the pointer offset the element is nudged (default 0.3)
 *   pullMax        px                cap on the element nudge (default 12)
 * Returns { destroy() }. Idempotent — one page-level cursor; repeat init calls return it. The
 * rAF loop pauses on visibilitychange when hidden and when the pointer leaves the window; it
 * animates transform only, on promoted layers.
 *
 * Tokens: --ad-accent (dot + snapped ring), --ad-ink (ring), --ad-dur-base (420ms),
 *         --ad-ease-signature (cubic-bezier(.16,1,.3,1)).
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-magnetic-cursor-css';
  var RING_GROW = 1.7; // ring scale while snapped to a magnet

  var reduce = function () {
    return !!(global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches);
  };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      '.ad-mcur{position:fixed;top:0;left:0;border-radius:50%;pointer-events:none;' +
      'z-index:2147483647;will-change:transform;opacity:0;}' +
      '.ad-mcur--dot{width:8px;height:8px;margin:-4px 0 0 -4px;' +
      'background:var(--ad-accent,oklch(62% 0.2 25));transition:opacity 220ms ease;}' +
      '.ad-mcur--ring{width:40px;height:40px;margin:-20px 0 0 -20px;' +
      'border:1.5px solid var(--ad-ink,oklch(96% 0 0));transition:opacity 220ms ease,' +
      'border-color var(--ad-dur-base,420ms) var(--ad-ease-signature,cubic-bezier(.16,1,.3,1));}' +
      '.ad-mcur--on{opacity:1;}' +
      '.ad-mcur--ring.ad-mcur--snap{border-color:var(--ad-accent,oklch(62% 0.2 25));}' +
      '.ad-mcur-active,.ad-mcur-active *{cursor:none!important;}';
    document.head.appendChild(s);
  }

  function clamp(v, m) { return v < -m ? -m : v > m ? m : v; }

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
    if (!global.matchMedia) return { destroy: function () {} }; // no feature gate → native cursor

    var magnetSelector = opts.magnetSelector || '[data-ad-magnetic]';
    var ringLerp = opts.ringLerp != null ? opts.ringLerp : 0.15;
    var pull = opts.pull != null ? opts.pull : 0.3;
    var pullMax = opts.pullMax != null ? opts.pullMax : 12;

    var finePointer = global.matchMedia('(pointer: fine)');
    var reduceMQ = global.matchMedia('(prefers-reduced-motion: reduce)');
    var docEl = document.documentElement;

    var active = false;
    var dot = null, ring = null, magnets = [], activeMagnet = null;
    var raf = 0, running = false, inside = false, havePos = false;
    var px = 0, py = 0, rx = 0, ry = 0, rs = 1;

    function want() { return finePointer.matches && !reduce(); }

    function tick() {
      if (!running) { raf = 0; return; }
      var tx, ty, ts;
      if (activeMagnet) {
        var rect = activeMagnet.getBoundingClientRect();
        // Subtract the applied nudge to recover the element's rest centre (no feedback drift).
        var cx = rect.left + rect.width / 2 - activeMagnet.__adNx;
        var cy = rect.top + rect.height / 2 - activeMagnet.__adNy;
        var nx = clamp((px - cx) * pull, pullMax);
        var ny = clamp((py - cy) * pull, pullMax);
        activeMagnet.__adNx = nx;
        activeMagnet.__adNy = ny;
        activeMagnet.style.transform = 'translate3d(' + nx + 'px,' + ny + 'px,0)';
        tx = cx; ty = cy; ts = RING_GROW;
      } else {
        tx = px; ty = py; ts = 1;
      }
      rx += (tx - rx) * ringLerp;
      ry += (ty - ry) * ringLerp;
      rs += (ts - rs) * ringLerp;
      ring.style.transform = 'translate3d(' + rx + 'px,' + ry + 'px,0) scale(' + rs + ')';
      dot.style.transform = 'translate3d(' + px + 'px,' + py + 'px,0)';
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

    function show() { dot.classList.add('ad-mcur--on'); ring.classList.add('ad-mcur--on'); }
    function hide() { if (dot) dot.classList.remove('ad-mcur--on'); if (ring) ring.classList.remove('ad-mcur--on'); }

    function onMove(e) {
      px = e.clientX; py = e.clientY;
      if (!havePos) { rx = px; ry = py; havePos = true; } // snap on first sight, then lerp
      inside = true;
      show();
      start();
    }
    function onDocLeave() { inside = false; havePos = false; hide(); stop(); }
    function onDocEnter() { inside = true; start(); }
    function onVis() { if (document.hidden) stop(); else start(); }

    function onMagnetEnter(e) {
      activeMagnet = e.currentTarget;
      if (activeMagnet.__adNx == null) { activeMagnet.__adNx = 0; activeMagnet.__adNy = 0; }
      ring.classList.add('ad-mcur--snap');
    }
    function onMagnetLeave(e) {
      var el = e.currentTarget;
      el.style.transform = '';
      el.__adNx = 0; el.__adNy = 0;
      if (activeMagnet === el) { activeMagnet = null; ring.classList.remove('ad-mcur--snap'); }
    }

    function bindMagnets() {
      magnets = Array.prototype.slice.call(root.querySelectorAll(magnetSelector));
      magnets.forEach(function (el) {
        el.__adNx = 0; el.__adNy = 0;
        el.addEventListener('mouseenter', onMagnetEnter);
        el.addEventListener('mouseleave', onMagnetLeave);
      });
    }
    function unbindMagnets() {
      magnets.forEach(function (el) {
        el.removeEventListener('mouseenter', onMagnetEnter);
        el.removeEventListener('mouseleave', onMagnetLeave);
        el.style.transform = '';
        delete el.__adNx; delete el.__adNy;
      });
      magnets = [];
      activeMagnet = null;
    }

    function activate() {
      if (active) return;
      active = true;
      injectCss();
      var body = document.body || docEl;
      dot = document.createElement('div');
      ring = document.createElement('div');
      dot.className = 'ad-mcur ad-mcur--dot';
      ring.className = 'ad-mcur ad-mcur--ring';
      dot.setAttribute('aria-hidden', 'true');
      ring.setAttribute('aria-hidden', 'true');
      body.appendChild(ring);
      body.appendChild(dot);
      docEl.classList.add('ad-mcur-active');
      havePos = false; inside = true; rs = 1;
      document.addEventListener('mousemove', onMove);
      docEl.addEventListener('mouseleave', onDocLeave);
      docEl.addEventListener('mouseenter', onDocEnter);
      document.addEventListener('visibilitychange', onVis);
      bindMagnets();
    }

    function deactivate() {
      if (!active) return;
      active = false;
      stop();
      document.removeEventListener('mousemove', onMove);
      docEl.removeEventListener('mouseleave', onDocLeave);
      docEl.removeEventListener('mouseenter', onDocEnter);
      document.removeEventListener('visibilitychange', onVis);
      unbindMagnets();
      docEl.classList.remove('ad-mcur-active'); // restore native cursor
      if (ring && ring.parentNode) ring.parentNode.removeChild(ring);
      if (dot && dot.parentNode) dot.parentNode.removeChild(dot);
      dot = null; ring = null;
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

  global.awardMagneticCursor = { init: init };
})(typeof window !== 'undefined' ? window : this);
