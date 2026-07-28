/*
 * scrubbed-decor-draw — the 'dead middle' fix (winners: Eloy Benoffi,
 * Codrops-verified to the number; FlowFest 2025, reference-carried,
 * boundary-adjacent). A décor layer welded to GLOBAL scroll that runs the
 * full page height behind the prose, so the page is never a bank of
 * fire-once reveals with silence between. Positional by construction —
 * every channel is a pure function of scroll position, so it re-fires on
 * every pass and reverses on the way back up. Three proven channels, each
 * opt-in by markup:
 *   [data-ad-decor-draw]   an SVG whose <path>s stroke-draw/undraw with page
 *                          progress (FlowFest's rainbow arches, scrub:0 —
 *                          the weld: zero lag, the line IS the scrollbar).
 *   [data-ad-decor-pluck]  a pixel/SVG field whose children pluck out
 *                          element-by-element as the page scrolls — the Eloy
 *                          flower-pluck: scrub 8 (a heavily lagged catch-up),
 *                          stagger each:0.1 from:'random', to opacity 0, ease
 *                          bounce.inOut — all Codrops-verified numbers.
 *   [data-ad-decor-shear]  title rows sheared by speed: each child travels
 *                          yPercent up to -300 through the viewport on
 *                          staggered power3.in/power2.in/power1.in curves,
 *                          scrub 0.6 (Eloy, Codrops-verified).
 * One rAF applies all channels — reads batched before writes, transform/
 * opacity only (the draw moves stroke-dashoffset, SVG-local paint, the
 * canonical line-draw cost) — gated by IntersectionObserver so off-screen
 * layers cost zero, paused on visibilitychange. Distinct from dolly-zoom
 * (a pinned focal push) and shader-surface (a WebGL ground): this is the
 * scroll-welded line-draw/pluck décor the manifest lacked.
 *
 * Usage:  awardScrubbedDecorDraw.init(root, opts)
 *   root   Element|Document  scope (default document)
 *   scrub  seconds the pluck lags its target (default 8 — the verified value)
 * Returns { destroy() }. Idempotent per root. No-JS and reduced motion show
 * the finished state: paths fully drawn, the field at rest, rows unsheared —
 * the component only ever subtracts from an authored-visible layer.
 *
 * Tokens: none — the décor is the build's own SVG/type; color stays the
 * author's.
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-scrubbed-decor-draw-css';
  var PLUCK_EACH = 0.1;   // the verified stagger {each:0.1, from:'random'}
  var SHEAR_Y = -300;     // the verified yPercent
  var SHEAR_SCRUB = 0.6;  // the verified scrub
  // power3.in / power2.in / power1.in cycling across rows (GSAP powerN.in = p^(N+1))
  var SHEAR_EXPS = [4, 3, 2];

  var reduce = function () {
    return global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches;
  };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      '[data-ad-decor-draw],[data-ad-decor-pluck],[data-ad-decor-shear]{pointer-events:none;}' +
      '[data-ad-decor-pluck] > *,[data-ad-decor-shear] > *{will-change:transform,opacity;}' +
      '@media (prefers-reduced-motion:reduce){' +
      '[data-ad-decor-pluck] > *,[data-ad-decor-shear] > *{' +
      'transform:none;opacity:1;will-change:auto;}}';
    document.head.appendChild(s);
  }

  function clamp01(v) { return Math.max(0, Math.min(1, v)); }

  // Robert Penner bounce, composed inOut — the verified pluck ease.
  function bounceOut(p) {
    if (p < 1 / 2.75) return 7.5625 * p * p;
    if (p < 2 / 2.75) { p -= 1.5 / 2.75; return 7.5625 * p * p + 0.75; }
    if (p < 2.5 / 2.75) { p -= 2.25 / 2.75; return 7.5625 * p * p + 0.9375; }
    p -= 2.625 / 2.75; return 7.5625 * p * p + 0.984375;
  }
  function bounceInOut(p) {
    return p < 0.5 ? (1 - bounceOut(1 - 2 * p)) / 2 : (1 + bounceOut(2 * p - 1)) / 2;
  }

  // deterministic per-index shuffle — from:'random' without a reseed per load
  function shuffledOrder(n) {
    var order = [];
    for (var i = 0; i < n; i++) order.push(i);
    var seed = 42;
    for (var j = n - 1; j > 0; j--) {
      seed = (seed * 9301 + 49297) % 233280;
      var k = Math.floor((seed / 233280) * (j + 1));
      var tmp = order[j]; order[j] = order[k]; order[k] = tmp;
    }
    return order;
  }

  function pageProgress() {
    var doc = document.documentElement;
    var max = (doc.scrollHeight - global.innerHeight) || 1;
    return clamp01((global.scrollY || doc.scrollTop || 0) / max);
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    // Reduced motion → the finished state IS the authored layer; nothing runs.
    if (reduce()) return { destroy: function () {} };

    var scrub = opts.scrub != null ? opts.scrub : 8;

    var host = root === document ? document.documentElement : root;
    if (host.__adDecorDraw) host.__adDecorDraw.destroy();

    injectCss();
    var layers = [];

    // ---- draw: paths welded to page progress (scrub:0) --------------------
    Array.prototype.forEach.call(root.querySelectorAll('[data-ad-decor-draw]'), function (svg) {
      var paths = Array.prototype.slice.call(svg.querySelectorAll('path'));
      if (!paths.length) return;
      var units = paths.map(function (path, i) {
        var len = 1;
        try { len = path.getTotalLength() || 1; } catch (e) {}
        path.style.strokeDasharray = String(len);
        return {
          path: path, len: len,
          // windows spread across the page so the draw travels hero→footer
          start: paths.length > 1 ? (i / paths.length) * 0.6 : 0,
          dur: paths.length > 1 ? 0.4 : 1
        };
      });
      layers.push({
        el: svg, visible: true,
        apply: function (gp) {
          units.forEach(function (u) {
            var p = clamp01((gp - u.start) / u.dur);
            u.path.style.strokeDashoffset = String(u.len * (1 - p));
          });
        }
      });
    });

    // ---- pluck: children ease out in random order, heavily lagged ---------
    Array.prototype.forEach.call(root.querySelectorAll('[data-ad-decor-pluck]'), function (field) {
      var kids = Array.prototype.slice.call(field.children);
      if (!kids.length) return;
      var order = shuffledOrder(kids.length);
      var span = 1 + (kids.length - 1) * PLUCK_EACH;
      var layer = {
        el: field, visible: true, sp: pageProgress(),
        apply: function (gp, dt) {
          // the scrub-8 lag: the field takes ~scrub seconds to catch the bar
          layer.sp += (gp - layer.sp) * Math.min(1, (dt * 3) / scrub);
          kids.forEach(function (kid, i) {
            var start = (order[i] * PLUCK_EACH) / span;
            var p = clamp01((layer.sp - start) / (1 / span));
            var v = bounceInOut(p);
            kid.style.opacity = String(1 - v);
            kid.style.transform =
              'translate3d(0,' + (-24 * v).toFixed(2) + 'px,0) scale(' + (1 - 0.4 * v).toFixed(3) + ')';
          });
        }
      };
      layers.push(layer);
    });

    // ---- shear: rows at different speeds through the viewport -------------
    Array.prototype.forEach.call(root.querySelectorAll('[data-ad-decor-shear]'), function (block) {
      var rows = Array.prototype.slice.call(block.children);
      if (!rows.length) return;
      var layer = {
        el: block, visible: true, sp: 0, seeded: false,
        apply: function (gp, dt, rect) {
          var vh = global.innerHeight || 1;
          // the block's own viewport traversal, not page progress
          var p = clamp01((vh - rect.top) / (vh + rect.height));
          if (!layer.seeded) { layer.sp = p; layer.seeded = true; }
          layer.sp += (p - layer.sp) * Math.min(1, (dt * 3) / SHEAR_SCRUB);
          rows.forEach(function (row, i) {
            var exp = SHEAR_EXPS[i % SHEAR_EXPS.length];
            var y = SHEAR_Y * Math.pow(layer.sp, exp);
            row.style.transform = 'translate3d(0,' + y.toFixed(2) + '%,0)';
          });
        },
        needsRect: true
      };
      layers.push(layer);
    });

    if (!layers.length) return { destroy: function () {} };

    var io = null;
    if ('IntersectionObserver' in global) {
      var byEl = new Map();
      layers.forEach(function (l) { byEl.set(l.el, l); });
      io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          var l = byEl.get(e.target);
          if (l) l.visible = e.isIntersecting;
        });
      }, { rootMargin: '25% 0px' });
      layers.forEach(function (l) { io.observe(l.el); });
    }

    var rafId = 0;
    var lastT = 0;
    function frame(now) {
      rafId = global.requestAnimationFrame(frame);
      if (!lastT) { lastT = now; return; }
      var dt = Math.min(0.05, (now - lastT) / 1000);
      lastT = now;
      var gp = pageProgress();
      // batch the reads, then the writes — no interleaved layout thrash
      var rects = layers.map(function (l) {
        return l.visible && l.needsRect ? l.el.getBoundingClientRect() : null;
      });
      layers.forEach(function (l, i) {
        if (l.visible) l.apply(gp, dt, rects[i]);
      });
    }
    function start() {
      if (!rafId && !document.hidden) { lastT = 0; rafId = global.requestAnimationFrame(frame); }
    }
    function stop() {
      if (rafId) { global.cancelAnimationFrame(rafId); rafId = 0; }
    }
    var onVisibility = function () { if (document.hidden) stop(); else start(); };
    document.addEventListener('visibilitychange', onVisibility);
    start();

    var handle = {
      destroy: function () {
        stop();
        document.removeEventListener('visibilitychange', onVisibility);
        if (io) io.disconnect();
        layers.forEach(function (l) {
          Array.prototype.forEach.call(l.el.querySelectorAll('path'), function (p) {
            p.style.strokeDasharray = '';
            p.style.strokeDashoffset = '';
          });
          Array.prototype.forEach.call(l.el.children, function (kid) {
            kid.style.opacity = '';
            kid.style.transform = '';
          });
        });
        delete host.__adDecorDraw;
        var s = document.getElementById(CSS_ID);
        if (s && s.parentNode) s.parentNode.removeChild(s);
      }
    };
    host.__adDecorDraw = handle;
    return handle;
  }

  global.awardScrubbedDecorDraw = { init: init };
})(typeof window !== 'undefined' ? window : this);
