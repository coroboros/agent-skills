/*
 * divided-capability-strip enhancer — the mobile MARQUEE for the divided
 * capability strip (winner: Endex — divide-x at desktop, a continuous marquee
 * under 768px). Desktop is untouched: the divide-x row is the complete
 * appearance and this enhancer stands aside. On mobile it promotes the
 * native-pan strip to a continuous glide: the authored cells are cloned once
 * into the cells slot (enhancer-owned children, the swipe-snap-dots
 * precedent; clones carry aria-hidden + data-ad-dcs-clone), and the slot
 * itself rides ONE WAAPI transform loop 0→−50% — linear stays legal on
 * continuous loops; duration derives from measured width at a constant px/s
 * so five cells and three glide at the same tempo. The loop pauses off-screen
 * (IntersectionObserver) and in a hidden tab (visibilitychange); crossing the
 * 768px line re-arbitrates live. Reduced motion: full stand-aside — the
 * form's static pannable strip IS the mobile answer. A dead script leaves
 * the same pannable strip: nothing is hidden, nothing is lost.
 *
 * Usage:  awardDividedCapabilityStrip.init(root, { selector, speed })
 *   root      Element|Document  scope (default document)
 *   selector  string  form roots (default '[data-ad-form="divided-capability-strip"]')
 *   speed     number  glide speed in px/s (default 36)
 * Returns { destroy() }. Idempotent per root. Styling lives in
 * forms/divided-capability-strip.css (linked, not injected — the form's
 * layout must survive a dead script).
 *
 * Tokens: none of its own — the strip's look is the form CSS's.
 */
(function (global) {
  'use strict';
  var MOBILE_MQ = '(max-width: 768px)';

  var reduce = function () {
    return global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches;
  };

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-form="divided-capability-strip"]';
    var speed = opts.speed || 36; // px/s — the constant tempo

    // Reduced motion: the static pannable strip is the complete mobile answer.
    if (reduce()) return { destroy: function () {} };

    if (root.__adDividedCapabilityStrip) root.__adDividedCapabilityStrip.destroy();

    var mq = global.matchMedia ? global.matchMedia(MOBILE_MQ) : null;
    var units = [];

    Array.prototype.forEach.call(root.querySelectorAll(selector), function (strip) {
      var cells = strip.querySelector('[data-slot="cells"]');
      if (!cells || cells.children.length < 2) return;
      units.push({ strip: strip, cells: cells, anim: null, onScreen: true });
    });
    if (!units.length) return { destroy: function () {} };

    function start(unit) {
      if (unit.anim || !unit.cells.animate) return;
      if (!unit.cells.querySelector('[data-ad-dcs-clone]')) {
        // one clone set: the authored half plus its double makes −50% seamless
        Array.prototype.slice.call(unit.cells.children).forEach(function (cell) {
          var c = cell.cloneNode(true);
          c.setAttribute('aria-hidden', 'true');
          c.setAttribute('data-ad-dcs-clone', '');
          unit.cells.appendChild(c);
        });
      }
      unit.strip.setAttribute('data-dcs-marquee', '');
      var half = unit.cells.scrollWidth / 2;
      if (half <= 0) return;
      unit.anim = unit.cells.animate(
        [{ transform: 'translate3d(0,0,0)' }, { transform: 'translate3d(-50%,0,0)' }],
        { duration: (half / speed) * 1000, iterations: Infinity, easing: 'linear' }
      );
      sync(unit);
    }

    function stop(unit) {
      if (unit.anim) { unit.anim.cancel(); unit.anim = null; }
      unit.strip.removeAttribute('data-dcs-marquee');
      Array.prototype.slice
        .call(unit.cells.querySelectorAll('[data-ad-dcs-clone]'))
        .forEach(function (c) { c.parentNode.removeChild(c); });
    }

    function sync(unit) {
      if (!unit.anim) return;
      var run = unit.onScreen && !document.hidden;
      if (run && unit.anim.playState === 'paused') unit.anim.play();
      if (!run && unit.anim.playState === 'running') unit.anim.pause();
    }

    function arbitrate() {
      var mobile = mq ? mq.matches : false;
      units.forEach(function (u) { if (mobile) start(u); else stop(u); });
    }

    var io = null;
    if ('IntersectionObserver' in global) {
      io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          units.forEach(function (u) {
            if (u.strip !== e.target) return;
            u.onScreen = e.isIntersecting;
            sync(u);
          });
        });
      });
      units.forEach(function (u) { io.observe(u.strip); });
    }

    function onVisibility() { units.forEach(sync); }
    document.addEventListener('visibilitychange', onVisibility);
    var onMq = arbitrate;
    if (mq && mq.addEventListener) mq.addEventListener('change', onMq);

    arbitrate();

    var handle = {
      destroy: function () {
        if (io) io.disconnect();
        document.removeEventListener('visibilitychange', onVisibility);
        if (mq && mq.removeEventListener) mq.removeEventListener('change', onMq);
        units.forEach(stop);
        units.length = 0;
        if (root.__adDividedCapabilityStrip === handle) delete root.__adDividedCapabilityStrip;
      }
    };
    root.__adDividedCapabilityStrip = handle;
    return handle;
  }

  global.awardDividedCapabilityStrip = { init: init };
})(typeof window !== 'undefined' ? window : this);
