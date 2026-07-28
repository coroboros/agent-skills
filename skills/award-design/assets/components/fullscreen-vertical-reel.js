/*
 * fullscreen-vertical-reel — the slider that IS the home (winner: Bisous).
 * A full-screen vertical reel of full-bleed treated works, infinite in BOTH
 * directions — the panels loop, there is no start and no end, so the scroll
 * (and the archetype's continuous-surface arc) never bottoms out. Wheel and
 * grab-drag drive a virtual offset that eases toward its target each frame
 * (the Lenis-smoothed feel, dependency-free); a released drag throws with
 * its velocity projected into the ease, and touch swipes ride the exact same
 * pointer path. Titles composed as studio-name + client-name are the build's
 * authored panel content — the component owns only the surface.
 * At rest the panels are ordinary stacked full-height sections in normal
 * flow, so a dead script or no-JS render is a legible page; reduced motion
 * never takes over — static stacked panels, native scroll (the documented
 * answer), which is exactly that resting state.
 *
 * Expected markup — one panel per work, media and titles authored inside:
 *   <section data-ad-reel aria-label="Selected works">
 *     <article data-ad-reel-panel> … full-bleed media + title … </article>
 *   </section>
 *
 * Usage:  awardFullscreenVerticalReel.init(root, opts)
 *   root      Element|Document  scope (default document)
 *   selector  string  reel roots (default '[data-ad-reel]')
 *   ease      number  per-frame lerp toward the target (default 0.09)
 *   fling     ms      release-velocity projection horizon (default 320)
 * Returns { destroy() }. Idempotent per reel. destroy() restores the static
 * stacked flow and removes listeners, transforms, and the stylesheet.
 *
 * A11y: the reel root is a keyboard stop — ArrowDown/ArrowUp and PageDown/
 * PageUp advance one panel; focus moving into a panel's link snaps that
 * panel into view, so sequential focus never lands off-screen. Links inside
 * panels keep their action: a press that travels engages the drag, a clean
 * tap/click falls through.
 * Perf: transform-only on promoted panels, one rAF loop that sleeps when the
 * offset settles, wakes on input, and pauses off-screen (IO) and on hidden
 * tabs. Wrap math re-centers the offset so numbers never grow unbounded.
 *
 * Tokens: --ad-accent (the root's :focus-visible ring).
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-fullscreen-vertical-reel-css';
  var SETTLE = 0.05;        // px — below this the loop sleeps
  var DRAG_THRESHOLD = 6;   // px of travel before a press becomes a drag
  var STALE_MS = 80;        // a release this long after the last move carries no throw

  var reduce = function () {
    return !!(global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches);
  };
  var nowMs = function () {
    return (global.performance && global.performance.now) ? global.performance.now() : Date.now();
  };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      // rest state: ordinary stacked full-height sections — legible with no JS
      '[data-ad-reel-panel]{position:relative;min-height:100svh;overflow:hidden;}' +
      // live state: the reel owns the viewport, panels ride transforms
      '.ad-vreel--live{position:relative;height:100dvh;overflow:hidden;' +
      'touch-action:none;overscroll-behavior:contain;user-select:none;' +
      '-webkit-user-select:none;}' +
      '.ad-vreel--live [data-ad-reel-panel]{position:absolute;inset:0;min-height:0;' +
      'height:100%;will-change:transform;}' +
      '.ad-vreel--live:focus-visible{outline:2px solid var(--ad-accent,oklch(62% 0.2 25));' +
      'outline-offset:-2px;}';
    document.head.appendChild(s);
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-reel]';
    var easeK = opts.ease != null ? opts.ease : 0.09;
    var flingMs = opts.fling != null ? opts.fling : 320;

    injectCss();
    var reels = [];

    // Reduced motion: static stacked panels, native scroll — the rest state
    // is already exactly that, so the component stands aside entirely.
    if (reduce()) return { destroy: function () {} };

    Array.prototype.forEach.call(root.querySelectorAll(selector), function (reel) {
      if (reel.__adVreel) return; // idempotent
      var panels = Array.prototype.slice.call(reel.querySelectorAll('[data-ad-reel-panel]'));
      if (panels.length < 2) return; // one panel cannot loop

      reel.classList.add('ad-vreel--live');
      if (!reel.hasAttribute('tabindex')) reel.setAttribute('tabindex', '0');

      var H = reel.clientHeight || global.innerHeight;
      var N = panels.length;
      var current = 0, target = 0;
      var raf = 0, running = false, inView = true;

      // pointer drag state
      var pending = false, dragging = false, pointerId = null;
      var startY = 0, startX = 0, startTarget = 0;
      var lastY = 0, lastT = 0, vel = 0; // px/ms of offset, EMA-smoothed

      function wrap(v, total) { return ((v % total) + total) % total; }

      function paint() {
        var total = N * H;
        for (var i = 0; i < N; i++) {
          var y = wrap(i * H - current, total);
          // the band just above the viewport holds the incoming upward panel
          if (y > total - H) y -= total;
          panels[i].style.transform = 'translate3d(0,' + y.toFixed(2) + 'px,0)';
        }
      }

      function frame() {
        raf = 0;
        current += (target - current) * easeK;
        if (Math.abs(target - current) < SETTLE && !dragging) {
          current = target;
          // re-center so offsets never grow unbounded — same wrap, no visual jump
          var total = N * H;
          var shift = Math.floor(current / total) * total;
          if (shift) { current -= shift; target -= shift; }
          paint();
          running = false;
          return;
        }
        paint();
        if (running) raf = global.requestAnimationFrame(frame);
      }
      function kick() {
        if (!inView || document.hidden) return;
        running = true;
        if (!raf) raf = global.requestAnimationFrame(frame);
      }

      function onWheel(e) {
        e.preventDefault(); // the reel IS the page — wheel drives the loop
        var unit = e.deltaMode === 1 ? 16 : e.deltaMode === 2 ? H : 1;
        target += e.deltaY * unit;
        kick();
      }

      function onPointerDown(e) {
        if (e.button != null && e.button !== 0) return;
        pending = true; dragging = false;
        pointerId = e.pointerId;
        startY = lastY = e.clientY; startX = e.clientX;
        startTarget = target;
        lastT = e.timeStamp || nowMs();
        vel = 0;
      }
      function onPointerMove(e) {
        if (!pending && !dragging) return;
        var y = e.clientY;
        if (!dragging) {
          var dy = y - startY, dx = e.clientX - startX;
          if (Math.abs(dy) < DRAG_THRESHOLD && Math.abs(dx) < DRAG_THRESHOLD) return;
          dragging = true;
          try { reel.setPointerCapture(pointerId); } catch (err) { /* capture optional */ }
        }
        e.preventDefault();
        var now = e.timeStamp || nowMs();
        var dt = now - lastT || 16;
        target = startTarget + (startY - y); // finger up → the reel advances
        var instV = (lastY - y) / dt;
        vel = vel * 0.7 + instV * 0.3;
        lastY = y; lastT = now;
        kick();
      }
      function onPointerUp(e) {
        if (pointerId != null) { try { reel.releasePointerCapture(pointerId); } catch (err) {} }
        var wasDragging = dragging;
        pending = false; dragging = false; pointerId = null;
        if (wasDragging && (nowMs() - lastT) < STALE_MS) {
          target += vel * flingMs; // the throw rides the same ease — no second physics
        }
        vel = 0;
        if (wasDragging) kick();
      }
      // a drag that traveled swallows the trailing click so links stay taps
      function onClick(e) {
        if (Math.abs(target - startTarget) > DRAG_THRESHOLD && (nowMs() - lastT) < 300) {
          e.preventDefault(); e.stopPropagation();
        }
      }
      function onDragStart(e) { e.preventDefault(); }

      function snapBy(dir) {
        target = (Math.round(target / H) + dir) * H;
        kick();
      }
      function onKeyDown(e) {
        if (e.key === 'ArrowDown' || e.key === 'PageDown') { e.preventDefault(); snapBy(1); }
        else if (e.key === 'ArrowUp' || e.key === 'PageUp') { e.preventDefault(); snapBy(-1); }
      }
      // sequential focus lands inside a panel → snap that panel into view
      function onFocusIn(e) {
        var panel = e.target && e.target.closest ? e.target.closest('[data-ad-reel-panel]') : null;
        if (!panel) return;
        var i = panels.indexOf(panel);
        if (i < 0) return;
        var total = N * H;
        // nearest wrapped congruent of i*H to the current target
        var want = i * H + Math.round((target - i * H) / total) * total;
        target = want;
        kick();
      }

      function onResize() {
        var h = reel.clientHeight || global.innerHeight;
        if (h && h !== H) {
          current = (current / H) * h;
          target = (target / H) * h;
          H = h;
        }
        paint();
        kick();
      }
      function onVis() { if (!document.hidden) kick(); }

      var io = null;
      if ('IntersectionObserver' in global) {
        io = new IntersectionObserver(function (entries) {
          entries.forEach(function (en) {
            inView = en.isIntersecting;
            if (inView) kick();
          });
        }, { threshold: 0 });
        io.observe(reel);
      }

      reel.addEventListener('wheel', onWheel, { passive: false });
      reel.addEventListener('pointerdown', onPointerDown, { passive: true });
      global.addEventListener('pointermove', onPointerMove, { passive: false });
      global.addEventListener('pointerup', onPointerUp, { passive: true });
      global.addEventListener('pointercancel', onPointerUp, { passive: true });
      reel.addEventListener('click', onClick, true);
      reel.addEventListener('dragstart', onDragStart);
      reel.addEventListener('keydown', onKeyDown);
      reel.addEventListener('focusin', onFocusIn);
      global.addEventListener('resize', onResize, { passive: true });
      document.addEventListener('visibilitychange', onVis);

      paint();

      reel.__adVreel = true;
      reels.push({
        destroy: function () {
          if (raf) global.cancelAnimationFrame(raf);
          running = false;
          if (io) io.disconnect();
          reel.removeEventListener('wheel', onWheel);
          reel.removeEventListener('pointerdown', onPointerDown);
          global.removeEventListener('pointermove', onPointerMove);
          global.removeEventListener('pointerup', onPointerUp);
          global.removeEventListener('pointercancel', onPointerUp);
          reel.removeEventListener('click', onClick, true);
          reel.removeEventListener('dragstart', onDragStart);
          reel.removeEventListener('keydown', onKeyDown);
          reel.removeEventListener('focusin', onFocusIn);
          global.removeEventListener('resize', onResize);
          document.removeEventListener('visibilitychange', onVis);
          panels.forEach(function (p) { p.style.transform = ''; });
          reel.classList.remove('ad-vreel--live');
          reel.removeAttribute('tabindex');
          delete reel.__adVreel;
        }
      });
    });

    return {
      destroy: function () {
        reels.forEach(function (r) { r.destroy(); });
        reels = [];
        var s = document.getElementById(CSS_ID);
        if (s && s.parentNode) s.parentNode.removeChild(s);
      }
    };
  }

  global.awardFullscreenVerticalReel = { init: init };
})(typeof window !== 'undefined' ? window : this);
