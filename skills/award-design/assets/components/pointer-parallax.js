/*
 * pointer-parallax — multi-layer depth under the pointer (winners: Dennis
 * Snellenberg, Wix Mouse Parallax Wonderland; the hero-depth staple).
 * Layers inside a scene shift at differential rates as the pointer moves —
 * a few px of depth, never a drift. Fine pointers only: on touch the layers
 * REST at zero (the winner convention — depth comes from scroll instead),
 * and reduced-motion never binds. Content-visible always; the shift is décor.
 *
 * Usage:  awardPointerParallax.init(root, { selector, maxShift, lerp })
 *   <section data-ad-parallax>
 *     <img data-depth="0.04" …>        far — barely moves
 *     <h1  data-depth="-0.08">…</h1>   negative = moves opposite (foreground)
 *     <div data-depth="0.12">…</div>   near — moves most
 *   </section>
 *   maxShift  px at full pointer offset (default 20 — depth, not drift)
 *   lerp      per-frame smoothing (default 0.1, the tier's house value)
 * Returns { destroy() }. Idempotent. Layers settle back to rest on leave.
 *
 * Perf: one pointermove writing two numbers; one rAF loop while a scene is
 * hovered or settling, transform-only writes on promoted layers.
 */
(function (global) {
  'use strict';
  var reduce = function () {
    return global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches;
  };
  var fine = function () {
    return global.matchMedia && global.matchMedia('(pointer: fine)').matches;
  };

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-parallax]';
    var maxShift = opts.maxShift != null ? opts.maxShift : 20;
    var lerp = opts.lerp != null ? opts.lerp : 0.1;

    var scenes = [];
    var rafId = 0;

    if (fine() && !reduce()) {
      Array.prototype.slice.call(root.querySelectorAll(selector)).forEach(function (el) {
        var layers = Array.prototype.slice.call(el.querySelectorAll('[data-depth]')).map(function (l) {
          l.style.willChange = 'transform';
          return { el: l, depth: parseFloat(l.getAttribute('data-depth')) || 0, x: 0, y: 0 };
        });
        if (!layers.length) return;
        var scene = { el: el, layers: layers, nx: 0, ny: 0, active: false };
        scene.onMove = function (e) {
          var r = el.getBoundingClientRect();
          scene.nx = (e.clientX - r.left) / Math.max(1, r.width) - 0.5;
          scene.ny = (e.clientY - r.top) / Math.max(1, r.height) - 0.5;
          scene.active = true;
          kick();
        };
        scene.onLeave = function () {
          scene.nx = 0; scene.ny = 0;   // settle home
          kick();
        };
        el.addEventListener('pointermove', scene.onMove, { passive: true });
        el.addEventListener('pointerleave', scene.onLeave);
        scenes.push(scene);
      });
    }

    function frame() {
      rafId = 0;
      var settling = false;
      scenes.forEach(function (scene) {
        scene.layers.forEach(function (l) {
          var tx = l.depth * scene.nx * maxShift * 2;
          var ty = l.depth * scene.ny * maxShift * 2;
          l.x += (tx - l.x) * lerp;
          l.y += (ty - l.y) * lerp;
          if (Math.abs(tx - l.x) > 0.05 || Math.abs(ty - l.y) > 0.05) settling = true;
          l.el.style.transform = 'translate3d(' + l.x.toFixed(2) + 'px,' + l.y.toFixed(2) + 'px,0)';
        });
      });
      if (settling && !document.hidden) rafId = global.requestAnimationFrame(frame);
    }
    function kick() { if (!rafId) rafId = global.requestAnimationFrame(frame); }

    return {
      destroy: function () {
        if (rafId) global.cancelAnimationFrame(rafId);
        scenes.forEach(function (scene) {
          scene.el.removeEventListener('pointermove', scene.onMove);
          scene.el.removeEventListener('pointerleave', scene.onLeave);
          scene.layers.forEach(function (l) {
            l.el.style.transform = '';
            l.el.style.willChange = '';
          });
        });
        scenes = [];
      }
    };
  }

  global.awardPointerParallax = { init: init };
})(typeof window !== 'undefined' ? window : this);
