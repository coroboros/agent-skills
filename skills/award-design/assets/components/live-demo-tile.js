/*
 * live-demo-tile — the tile IS the product demo (winners: Anime.js v4, SOTD
 * 2025-05-06 7.62 + Developer Award — every tile a running capability demo;
 * Endex — awarded-artifact product-UI tiles, live-site unconfirmed this run;
 * Attio product-UI tiles, design-canonical). The bento DNA 'every tile shows
 * its claim' made executable: the tile's CONTENT is a running canvas demo,
 * never a passive image, and there is NO card chrome or lift at all — the
 * tile reacts because the demo reacts. The component owns the machinery
 * (mount, DPR sizing, drive inputs, gating, the poster fallback); the BUILDER
 * supplies the real demo as a draw function — a working micro-demo of the
 * actual claim, never a faked screen recording.
 *
 * Markup:
 *   <figure data-ad-live-demo="<name>" data-ad-live-demo-drive="auto|hover|drag|scroll">
 *     <canvas data-demo-canvas></canvas>
 *     <img data-demo-poster src="…" alt="…">    the reduced-motion / no-JS truth
 *     …optional flow copy below…
 *   </figure>
 *
 * Demos: opts.demos[name] = function draw(ctx, w, h, state) — one frame in CSS
 * pixels (the canvas is DPR-scaled behind the scenes). state:
 *   t         seconds this demo has actually run (gating-aware clock)
 *   progress  0..1 from the drive input
 *   pointer   { x, y, in } tile-local 0..1
 *   accent / ink  resolved token colors, so demos ink in the build's palette
 * Drives: auto (progress loops on data-ad-live-demo-period ms, default 4000),
 * hover (progress eases toward pointer.x), drag (pointer delta accumulates
 * progress — the tile takes tabindex and arrows step it; touch drags on the
 * x axis while vertical pan stays native), scroll (progress is the tile's
 * viewport traversal — a pure scroll function, reversible by construction).
 *
 * Drag tiles get a tile-SCOPED cursor chip ('DRAG', lerped after the pointer,
 * fine pointers only); the native cursor hides via a JS-applied class, never
 * a bare selector — do not pair cursor-verb-label on the same tile. No card
 * chrome by contract: the component styles no border, no shadow, no hover
 * lift — pairing figure-hover on a live tile is a composition error.
 *
 * PERF: one rAF per tile, running only while the tile intersects and the tab
 * is visible (IntersectionObserver + visibilitychange); canvas resizes via
 * ResizeObserver. Reduced motion / no JS: the authored poster stands, the
 * canvas never arms, nothing binds.
 *
 * Usage:  awardLiveDemoTile.init(root, { selector, demos })
 *   root      Element|Document  scope (default document)
 *   selector  string            tiles (default '[data-ad-live-demo]')
 *   demos     object            name → draw(ctx, w, h, state)
 * Returns { destroy() }. Idempotent per root.
 *
 * Tokens: --ad-accent, --ad-ink, --ad-ground-2, --ad-font-mono.
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-live-demo-tile-css';
  var HIDDEN_CLASS = 'ad-ldt-page-hidden';
  var INK = 'var(--ad-ink,oklch(96% 0 0))';
  var GROUND2 = 'var(--ad-ground-2,oklch(18% 0.01 260))';
  var MONO = 'var(--ad-font-mono,ui-monospace,monospace)';

  var reduce = function () {
    return global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches;
  };
  var finePointer = function () {
    return global.matchMedia && global.matchMedia('(hover: hover) and (pointer: fine)').matches;
  };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      // no chrome by contract: position + the canvas/poster swap, nothing else
      '.ad-ldt{position:relative;}' +
      '.ad-ldt [data-demo-canvas]{display:block;width:100%;height:100%;}' +
      '.ad-ldt--live{overflow:hidden;}' +
      '.ad-ldt--live [data-demo-canvas]{position:absolute;inset:0;}' +
      // the poster is the rest truth; only the ARMED tile trades it for the canvas
      '.ad-ldt--live [data-demo-poster]{opacity:0;visibility:hidden;}' +
      '.ad-ldt--drag{touch-action:pan-y pinch-zoom;}' +
      // the native cursor hides only via this JS-applied class — a dead script
      // never strands a cursorless tile
      '.ad-ldt-hide,.ad-ldt-hide *{cursor:none!important;}' +
      '.ad-ldt__cursor{position:absolute;left:0;top:0;pointer-events:none;z-index:2;' +
      'padding:.3em .65em;font-family:' + MONO + ';font-size:.62rem;' +
      'letter-spacing:.14em;color:' + INK + ';background:' + GROUND2 + ';' +
      'border-radius:999px;transform:translate(-50%,-50%);will-change:transform;}' +
      '@media (prefers-reduced-motion:reduce){.ad-ldt__cursor{display:none;}}';
    document.head.appendChild(s);
  }

  function clamp01(v) { return v < 0 ? 0 : v > 1 ? 1 : v; }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-live-demo]';
    var demos = opts.demos || {};

    // Reduced motion: the poster IS the tile — nothing arms, nothing binds.
    if (reduce()) return { destroy: function () {} };

    injectCss();
    if (root.__adLiveDemoTile) root.__adLiveDemoTile.destroy();

    var units = [];
    Array.prototype.forEach.call(root.querySelectorAll(selector), function (tile) {
      var name = tile.getAttribute('data-ad-live-demo');
      var draw = demos[name];
      var canvas = tile.querySelector('[data-demo-canvas]');
      if (typeof draw !== 'function' || !canvas) return; // no demo → the poster stands

      var drive = tile.getAttribute('data-ad-live-demo-drive') || 'auto';
      var period = parseFloat(tile.getAttribute('data-ad-live-demo-period')) || 4000;
      var ctx = canvas.getContext('2d');
      var unit = {
        tile: tile, canvas: canvas, ctx: ctx, draw: draw, drive: drive,
        period: period, on: false, raf: 0, last: 0, frames: 0, t: 0, w: 0, h: 0, dpr: 1,
        progress: drive === 'hover' ? 0.5 : 0,
        pointer: { x: 0.5, y: 0.5, in: false },
        accent: '', ink: '', chip: null, chipX: 0, chipY: 0,
        dragging: false, dragX: 0, listeners: []
      };

      tile.classList.add('ad-ldt', 'ad-ldt--live');
      if (drive === 'drag') tile.classList.add('ad-ldt--drag');

      function tokens() {
        var cs = getComputedStyle(tile);
        unit.accent = (cs.getPropertyValue('--ad-accent') || '').trim() || 'oklch(62% 0.2 25)';
        unit.ink = (cs.getPropertyValue('--ad-ink') || '').trim() || 'oklch(96% 0 0)';
      }
      function size() {
        var r = tile.getBoundingClientRect();
        unit.dpr = Math.min(2, global.devicePixelRatio || 1);
        unit.w = Math.max(1, r.width);
        unit.h = Math.max(1, r.height);
        canvas.width = Math.round(unit.w * unit.dpr);
        canvas.height = Math.round(unit.h * unit.dpr);
        tokens();
      }
      size();
      unit.size = size;

      function frame(now) {
        unit.raf = 0;
        if (!unit.on) return;
        var dt = unit.last ? Math.min(0.05, (now - unit.last) / 1000) : 0;
        unit.last = now;
        unit.t += dt;
        // tokens can move under a live demo (pinned-demo-panels recolors the
        // page per panel) — re-resolve at ~2Hz, never per frame
        if (++unit.frames % 30 === 0) tokens();

        if (unit.drive === 'auto') {
          unit.progress = (unit.t * 1000 % unit.period) / unit.period;
        } else if (unit.drive === 'hover') {
          var target = unit.pointer.in ? unit.pointer.x : 0.5;
          unit.progress += (target - unit.progress) * 0.1;
        } else if (unit.drive === 'scroll') {
          var r = unit.tile.getBoundingClientRect();
          var vh = global.innerHeight || 1;
          unit.progress = clamp01((vh - r.top) / (vh + r.height));
        } // drag: pointer/keyboard writes progress directly

        if (unit.chip) {
          unit.chipX += (unit.pointer.x * unit.w - unit.chipX) * 0.18;
          unit.chipY += (unit.pointer.y * unit.h - unit.chipY) * 0.18;
          unit.chip.style.transform =
            'translate3d(' + unit.chipX.toFixed(1) + 'px,' + unit.chipY.toFixed(1) + 'px,0)' +
            ' translate(-50%,-50%)';
        }

        unit.ctx.setTransform(unit.dpr, 0, 0, unit.dpr, 0, 0);
        unit.draw(unit.ctx, unit.w, unit.h, {
          t: unit.t, progress: unit.progress, pointer: unit.pointer,
          accent: unit.accent, ink: unit.ink
        });
        unit.raf = global.requestAnimationFrame(frame);
      }
      unit.frame = frame;

      function listen(el, ev, fn, o) {
        el.addEventListener(ev, fn, o);
        unit.listeners.push([el, ev, fn, o]);
      }

      listen(tile, 'pointermove', function (e) {
        var r = tile.getBoundingClientRect();
        unit.pointer.x = clamp01((e.clientX - r.left) / Math.max(1, r.width));
        unit.pointer.y = clamp01((e.clientY - r.top) / Math.max(1, r.height));
        unit.pointer.in = true;
        if (unit.dragging) {
          unit.progress = clamp01(unit.progress + (e.clientX - unit.dragX) / Math.max(1, r.width));
          unit.dragX = e.clientX;
        }
      });
      listen(tile, 'pointerleave', function () { unit.pointer.in = false; });

      if (drive === 'drag') {
        listen(tile, 'pointerdown', function (e) {
          unit.dragging = true;
          unit.dragX = e.clientX;
          if (tile.setPointerCapture) tile.setPointerCapture(e.pointerId);
        });
        listen(tile, 'pointerup', function () { unit.dragging = false; });
        listen(tile, 'pointercancel', function () { unit.dragging = false; });
        // the operable tile is keyboard-operable: arrows step the timeline
        if (!tile.hasAttribute('tabindex')) tile.setAttribute('tabindex', '0');
        listen(tile, 'keydown', function (e) {
          if (e.key === 'ArrowRight') { unit.progress = clamp01(unit.progress + 0.05); e.preventDefault(); }
          if (e.key === 'ArrowLeft') { unit.progress = clamp01(unit.progress - 0.05); e.preventDefault(); }
        });
        if (finePointer()) {
          var chip = document.createElement('span');
          chip.className = 'ad-ldt__cursor';
          chip.textContent = tile.getAttribute('data-ad-live-demo-verb') || 'DRAG';
          chip.setAttribute('aria-hidden', 'true');
          chip.style.opacity = '0';
          tile.appendChild(chip);
          unit.chip = chip;
          listen(tile, 'pointerenter', function () {
            chip.style.opacity = '1';
            tile.classList.add('ad-ldt-hide');
          });
          listen(tile, 'pointerleave', function () {
            chip.style.opacity = '0';
            tile.classList.remove('ad-ldt-hide');
          });
        }
      }

      var canvasEl = canvas;
      canvasEl.setAttribute('aria-hidden', 'true'); // the poster's alt is the name

      units.push(unit);
    });

    var io = null;
    if ('IntersectionObserver' in global) {
      io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          var unit = null;
          for (var i = 0; i < units.length; i++) if (units[i].tile === e.target) unit = units[i];
          if (!unit) return;
          unit.on = e.isIntersecting && !document.hidden;
          unit.last = 0;
          if (unit.on && !unit.raf) unit.raf = global.requestAnimationFrame(unit.frame);
        });
      }, { rootMargin: '10%' });
      units.forEach(function (u) { io.observe(u.tile); });
    } else {
      units.forEach(function (u) {
        u.on = true;
        u.raf = global.requestAnimationFrame(u.frame);
      });
    }

    var ro = null;
    if ('ResizeObserver' in global) {
      ro = new ResizeObserver(function (entries) {
        entries.forEach(function (e) {
          for (var i = 0; i < units.length; i++) if (units[i].tile === e.target) units[i].size();
        });
      });
      units.forEach(function (u) { ro.observe(u.tile); });
    }

    function onVisibility() {
      document.documentElement.classList.toggle(HIDDEN_CLASS, document.hidden);
      if (document.hidden) {
        units.forEach(function (u) { u.on = false; });
      } else if (io) {
        // re-observing refires the callback with the current intersection state
        units.forEach(function (u) { io.unobserve(u.tile); io.observe(u.tile); });
      } else {
        units.forEach(function (u) {
          u.on = true;
          u.last = 0;
          if (!u.raf) u.raf = global.requestAnimationFrame(u.frame);
        });
      }
    }
    document.addEventListener('visibilitychange', onVisibility);

    var handle = {
      destroy: function () {
        document.removeEventListener('visibilitychange', onVisibility);
        if (io) io.disconnect();
        if (ro) ro.disconnect();
        units.forEach(function (u) {
          u.on = false;
          if (u.raf) global.cancelAnimationFrame(u.raf);
          u.listeners.forEach(function (l) { l[0].removeEventListener(l[1], l[2], l[3]); });
          if (u.chip && u.chip.parentNode) u.chip.parentNode.removeChild(u.chip);
          u.tile.classList.remove('ad-ldt', 'ad-ldt--live', 'ad-ldt--drag', 'ad-ldt-hide');
        });
        document.documentElement.classList.remove(HIDDEN_CLASS);
        var s = document.getElementById(CSS_ID);
        if (s && s.parentNode) s.parentNode.removeChild(s);
        if (root.__adLiveDemoTile === handle) delete root.__adLiveDemoTile;
      }
    };
    root.__adLiveDemoTile = handle;
    return handle;
  }

  global.awardLiveDemoTile = { init: init };
})(typeof window !== 'undefined' ? window : this);
