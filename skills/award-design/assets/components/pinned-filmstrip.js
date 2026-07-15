/*
 * pinned-filmstrip — hold-and-drag filmstrip of treated stills (winner: Siena Film Foundation).
 * A horizontal row of jury stills, each carrying a pull-quote, that the visitor pulls across by
 * grabbing it. The row is a NATIVE overflow-x scroller, so with no JS it already scrolls and every
 * still is reachable by trackpad, wheel, scrollbar, and keyboard — the drag is pure enhancement on
 * top of that, never a JS-only transform that a dead script could blank. On a fine pointer the row
 * becomes grab-draggable (cursor:grab, grabbing while held) and a release throws it with inertia
 * that decays by `momentum` each frame; shift+wheel (and horizontal trackpad) map to horizontal
 * travel. Touch is left entirely to native panning and its own fling. Reduced-motion keeps the
 * drag but drops the inertia — a release stops where it is; the wheel maps 1:1.
 *
 * Expected markup (the component drives this exact skeleton):
 *   <div data-ad-filmstrip>
 *     <figure data-ad-still>
 *       <img src="…" alt="…">
 *       <figcaption><blockquote>"…"</blockquote><cite>— Name, role</cite></figcaption>
 *     </figure>
 *     … more <figure data-ad-still> …
 *   </div>
 *
 * Usage:  awardFilmstrip.init(root, { selector, momentum })
 *   root      Element|Document  scope (default document)
 *   selector  string            filmstrip containers (default '[data-ad-filmstrip]')
 *   momentum  0..1              per-frame velocity decay on release (default 0.92)
 * Returns { destroy() }. Idempotent per element.
 *
 * A11y: each still is given tabindex=0 (removed on destroy), so it is a keyboard stop that the
 * browser scrolls into view on focus; native arrow-key/Tab scrolling of the row is never
 * intercepted. Vertical intent always passes through — a vertical drag or plain vertical wheel
 * scrolls the page, only horizontal intent moves the strip, and the wheel never traps at the edges.
 * Perf: drag and wheel writes go through scrollLeft, rAF-batched and write-only; the momentum loop
 * integrates a JS position (no per-frame layout read) and stops at ~0 velocity or a boundary.
 *
 * Tokens: --ad-ink (quote text), --ad-accent (cite + scrollbar + focus ring),
 *   --ad-font-display (blockquote), --ad-font-mono (cite).
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-filmstrip-css';
  var DRAG_THRESHOLD = 6;   // px of travel before a press becomes a drag (a click/tap stays a click)
  var MIN_VELOCITY = 0.02;  // px/ms — momentum below this is imperceptible, so stop
  var STALE_MS = 80;        // a release this long after the last move carries no throw

  var active = 0;           // live strips across all init() calls — the last one out removes the CSS

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
      '[data-ad-filmstrip]{display:flex;flex-wrap:nowrap;gap:clamp(1rem,3vw,2.5rem);' +
      'overflow-x:auto;overflow-y:hidden;-webkit-overflow-scrolling:touch;padding-bottom:.75rem;' +
      'scrollbar-width:thin;scrollbar-color:var(--ad-accent,oklch(62% 0.2 25)) transparent;}' +
      '[data-ad-filmstrip]::-webkit-scrollbar{height:6px;}' +
      '[data-ad-filmstrip]::-webkit-scrollbar-track{background:transparent;}' +
      '[data-ad-filmstrip]::-webkit-scrollbar-thumb{background:var(--ad-accent,oklch(62% 0.2 25));' +
      'border-radius:999px;}' +
      '@media (pointer:fine){.ad-filmstrip{cursor:grab;}}' +
      '.ad-filmstrip.ad-filmstrip--drag{cursor:grabbing;user-select:none;-webkit-user-select:none;}' +
      '[data-ad-still]{margin:0;flex:0 0 auto;width:min(80vw,34rem);display:flex;' +
      'flex-direction:column;}' +
      '[data-ad-still] img{display:block;width:100%;height:auto;-webkit-user-drag:none;' +
      'user-select:none;}' +
      '[data-ad-still] figcaption{margin-top:1rem;color:var(--ad-ink,oklch(96% 0 0));}' +
      '[data-ad-still] blockquote{margin:0;font-family:var(--ad-font-display,inherit);' +
      'font-size:clamp(1rem,1.4vw,1.35rem);line-height:1.3;}' +
      '[data-ad-still] cite{display:block;margin-top:.6rem;font-style:normal;letter-spacing:.04em;' +
      'font-family:var(--ad-font-mono,ui-monospace,monospace);font-size:.8rem;opacity:.75;' +
      'color:var(--ad-accent,oklch(62% 0.2 25));}' +
      '[data-ad-still]:focus-visible{outline:2px solid var(--ad-accent,oklch(62% 0.2 25));' +
      'outline-offset:4px;}';
    document.head.appendChild(s);
  }

  function removeCss() {
    var css = document.getElementById(CSS_ID);
    if (css && css.parentNode) css.parentNode.removeChild(css);
  }

  function makeStrip(track, momentum) {
    if (track.__adFilmstrip) return null; // already enhanced — keep init idempotent
    track.classList.add('ad-filmstrip');

    // Each still becomes a keyboard stop; the browser reveals it horizontally on focus.
    var tabbed = [];
    Array.prototype.slice.call(track.querySelectorAll('[data-ad-still]')).forEach(function (fig) {
      if (!fig.hasAttribute('tabindex')) { fig.setAttribute('tabindex', '0'); tabbed.push(fig); }
    });

    function maxScroll() { return Math.max(0, track.scrollWidth - track.clientWidth); }

    var pending = false;   // pointer down, drag not yet engaged (still could be a click)
    var dragging = false;  // engaged drag past the threshold
    var moved = false;     // this gesture crossed the threshold → swallow the trailing click
    var pointerId = null;
    var startX = 0, startY = 0, startScroll = 0, dragMax = 0;
    var lastX = 0, lastT = 0, vel = 0;         // vel = scrollLeft px/ms, EMA-smoothed
    var targetScroll = 0, moveRAF = 0;
    var wheelDelta = 0, wheelRAF = 0;
    var momRAF = 0, momPos = 0, momMax = 0, momPrev = 0;

    function clampDrag(v) { return v < 0 ? 0 : v > dragMax ? dragMax : v; }

    function applyDrag() { moveRAF = 0; track.scrollLeft = targetScroll; }

    function stopMomentum() {
      if (momRAF) { global.cancelAnimationFrame(momRAF); momRAF = 0; }
      vel = 0;
    }

    function momentumTick(now) {
      var dt = now - momPrev; momPrev = now;
      if (dt > 64) dt = 64;                    // a backgrounded tab must not fling on return
      momPos += vel * dt;
      if (momPos <= 0) { track.scrollLeft = 0; stopMomentum(); return; }
      if (momPos >= momMax) { track.scrollLeft = momMax; stopMomentum(); return; }
      track.scrollLeft = momPos;
      vel *= Math.pow(momentum, dt / 16.667); // frame-rate-independent decay of the 60fps factor
      if (Math.abs(vel) < MIN_VELOCITY) { stopMomentum(); return; }
      momRAF = global.requestAnimationFrame(momentumTick);
    }

    function startMomentum() {
      momPos = track.scrollLeft;
      momMax = maxScroll();
      momPrev = nowMs();
      momRAF = global.requestAnimationFrame(momentumTick);
    }

    function suppressClick(e) {
      e.preventDefault(); e.stopPropagation();
      track.removeEventListener('click', suppressClick, true);
    }

    function onPointerDown(e) {
      if (e.pointerType === 'touch') return;   // native touch panning + fling own this gesture
      if (e.button != null && e.button !== 0) return;
      track.removeEventListener('click', suppressClick, true);
      stopMomentum();
      pending = true; dragging = false; moved = false;
      pointerId = e.pointerId;
      startX = lastX = e.clientX; startY = e.clientY;
      startScroll = targetScroll = track.scrollLeft;
      lastT = e.timeStamp || nowMs();
      vel = 0;
    }

    function engage() {
      dragging = true; moved = true;
      dragMax = maxScroll();
      track.classList.add('ad-filmstrip--drag');
      try { track.setPointerCapture(pointerId); } catch (err) { /* capture optional */ }
    }

    function onPointerMove(e) {
      if (!pending && !dragging) return;
      var x = e.clientX;
      if (!dragging) {
        var dx = x - startX, dy = e.clientY - startY;
        if (Math.abs(dx) < DRAG_THRESHOLD && Math.abs(dy) < DRAG_THRESHOLD) return;
        if (Math.abs(dy) > Math.abs(dx)) { pending = false; return; } // vertical intent → page scrolls
        engage();
      }
      e.preventDefault(); // engaged drag: no text selection, no native image drag
      var now = e.timeStamp || nowMs();
      var dt = now - lastT || 16;
      targetScroll = clampDrag(startScroll - (x - startX));
      var instV = (-(x - lastX)) / dt;         // scrollLeft moves opposite the pointer
      vel = vel * 0.7 + instV * 0.3;
      lastX = x; lastT = now;
      if (!moveRAF) moveRAF = global.requestAnimationFrame(applyDrag);
    }

    function endDrag(fling) {
      if (pointerId != null) { try { track.releasePointerCapture(pointerId); } catch (err) {} }
      var wasDragging = dragging;
      pending = false; dragging = false; pointerId = null;
      track.classList.remove('ad-filmstrip--drag');
      if (moveRAF) { global.cancelAnimationFrame(moveRAF); moveRAF = 0; track.scrollLeft = targetScroll; }
      if (moved) track.addEventListener('click', suppressClick, true);
      if (fling && wasDragging && !reduce() &&
          (nowMs() - lastT) < STALE_MS && Math.abs(vel) > MIN_VELOCITY) {
        startMomentum();
      } else {
        vel = 0;
      }
    }
    function onPointerUp() { endDrag(true); }
    function onPointerCancel() { endDrag(false); }

    function applyWheel() {
      wheelRAF = 0;
      var max = maxScroll();
      var next = track.scrollLeft + wheelDelta;
      track.scrollLeft = next < 0 ? 0 : next > max ? max : next;
      wheelDelta = 0;
    }

    function onWheel(e) {
      var absX = Math.abs(e.deltaX), absY = Math.abs(e.deltaY), raw;
      if (absX > absY) raw = e.deltaX;         // horizontal intent (trackpad)
      else if (e.shiftKey) raw = e.deltaY;     // shift turns a vertical wheel horizontal
      else return;                              // vertical intent → let the page scroll
      if (!raw) return;
      var unit = e.deltaMode === 1 ? 16 : e.deltaMode === 2 ? track.clientWidth : 1;
      var delta = raw * unit;
      var max = maxScroll();
      if ((delta < 0 && track.scrollLeft <= 0) || (delta > 0 && track.scrollLeft >= max)) return; // edge: no trap
      e.preventDefault();
      stopMomentum();
      wheelDelta += delta;
      if (!wheelRAF) wheelRAF = global.requestAnimationFrame(applyWheel);
    }

    function onDragStart(e) { e.preventDefault(); } // kill native image/text drag inside the strip

    track.addEventListener('pointerdown', onPointerDown, { passive: true });
    global.addEventListener('pointermove', onPointerMove, { passive: false });
    global.addEventListener('pointerup', onPointerUp, { passive: true });
    global.addEventListener('pointercancel', onPointerCancel, { passive: true });
    track.addEventListener('wheel', onWheel, { passive: false });
    track.addEventListener('dragstart', onDragStart);

    active++;
    var controller = {
      destroy: function () {
        track.removeEventListener('pointerdown', onPointerDown);
        global.removeEventListener('pointermove', onPointerMove);
        global.removeEventListener('pointerup', onPointerUp);
        global.removeEventListener('pointercancel', onPointerCancel);
        track.removeEventListener('wheel', onWheel);
        track.removeEventListener('dragstart', onDragStart);
        track.removeEventListener('click', suppressClick, true);
        if (moveRAF) global.cancelAnimationFrame(moveRAF);
        if (wheelRAF) global.cancelAnimationFrame(wheelRAF);
        stopMomentum();
        track.classList.remove('ad-filmstrip', 'ad-filmstrip--drag');
        tabbed.forEach(function (fig) { fig.removeAttribute('tabindex'); });
        delete track.__adFilmstrip;
        if (--active <= 0) { active = 0; removeCss(); }
      }
    };
    track.__adFilmstrip = controller;
    return controller;
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-filmstrip]';
    var momentum = opts.momentum != null ? opts.momentum : 0.92;
    injectCss();

    var strips = Array.prototype.slice.call(root.querySelectorAll(selector))
      .map(function (track) { return makeStrip(track, momentum); })
      .filter(Boolean);

    return {
      destroy: function () {
        strips.forEach(function (s) { s.destroy(); });
        strips = [];
        if (active <= 0) removeCss(); // no strips matched → the injected CSS is still ours to clear
      }
    };
  }

  global.awardFilmstrip = { init: init };
})(typeof window !== 'undefined' ? window : this);
