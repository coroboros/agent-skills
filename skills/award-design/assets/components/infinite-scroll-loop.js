/*
 * infinite-scroll-loop — the track that never bottoms out (winner: Urban
 * Jürgensen — SOTD Oct 2025; the infinite vertical storytelling spine and the
 * infinite horizontal product carousel, both award-page-verified). Content
 * recycles so the scroll — and therefore the signature thread — never rests.
 * Two axes in one component: data-ad-loop="y" wraps a NATIVE vertical
 * scroller by one content period (momentum survives — the jump lands on
 * identical pixels, so the wrap is invisible); data-ad-loop="x" runs a
 * transform-driven drag/wheel carousel whose position wraps modulo the copy
 * width with a decelerating glide (friction, the luxury register — measured,
 * never springy). Index-mapped: the item under the viewport center publishes
 * as data-ad-loop-index on the root (a discrete write, only on change) so
 * wayfinding can read where the loop is. Ruled distinct, not an alias:
 * swipe-snap-gallery is a FINITE native-snap row — it bottoms out by design;
 * no manifest component recycles a track.
 * Touch: live — scroll/drag IS the input (the horizontal track keeps
 * touch-action:pan-y so page scroll never traps). Reduced motion: the gap's
 * own order — a FINITE track; init returns a no-op and the authored markup
 * stands (author it as an ordinary finite scroller/stack, the component only
 * adds the loop). No-JS: the same authored finite track.
 *
 * Expected markup — one period of real content; the component makes copies:
 *   <section data-ad-loop="y" style="height:100svh">   the builder sizes the scroller
 *     <div data-loop-track>
 *       <article data-loop-item>…</article> …
 *     </div>
 *   </section>
 *   <section data-ad-loop="x">
 *     <div data-loop-track> <figure data-loop-item>…</figure> … </div>
 *   </section>
 *
 * Usage:  awardInfiniteScrollLoop.init(root, opts)
 *   root      Element|Document  scope (default document)
 *   selector  string  loop roots (default '[data-ad-loop]')
 *   friction  number  horizontal glide decay per frame (default 0.94)
 * Returns { destroy() }. Idempotent per root element (a live root re-inits
 * to the same handle). destroy() removes clones, restores scroll positions,
 * inline styles, listeners, and the stylesheet.
 *
 * A11y + perf: clones are aria-hidden with every focusable inside them at
 * tabindex -1 — assistive tech and the tab order read ONE copy while a
 * visible clone stays fully clickable (driven finding: `inert` dead-zones
 * every wrapped copy — a clone link would never fire); when keyboard focus
 * lands on a canonical item the horizontal track glides it into view (a
 * transform track defeats native scroll-into-view, so the component answers
 * focus itself). Vertical wrap is a scrollTop period-jump on the scroll event;
 * horizontal writes transform only, on one rAF that parks when velocity
 * settles and while the root is off-screen (IntersectionObserver).
 *
 * Tokens: none painted — the loop is pure mechanics; register and easing
 * live in the builder's own item styling.
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-infinite-scroll-loop-css';
  var FRICTION_DEFAULT = 0.94;
  var WHEEL_GAIN = 1;      // wheel delta → px of horizontal travel
  var SETTLE = 0.05;       // px/frame under which the glide parks

  var reduce = function () {
    return !!(global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches);
  };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      // vertical: the root becomes its own native scroller — the loop never
      // hijacks the document scroll
      '[data-ad-loop="y"].ad-isl-live{overflow-y:auto;overscroll-behavior:contain;}' +
      // horizontal: one flex row ridden by transform; pan-y keeps the page
      // scrollable over the track on touch
      '[data-ad-loop="x"].ad-isl-live{overflow:hidden;touch-action:pan-y;}' +
      '[data-ad-loop="x"].ad-isl-live > [data-loop-track]{display:flex;' +
      'width:max-content;will-change:transform;}' +
      '[data-ad-loop="x"].ad-isl-live.is-dragging{cursor:grabbing;}' +
      '[data-ad-loop="x"].ad-isl-live.is-dragging > [data-loop-track]{' +
      'pointer-events:none;}'; // a drag is a drag — never a click storm
    document.head.appendChild(s);
  }

  // Driven finding: `inert` dead-zones every wrapped copy — elementFromPoint
  // (and every click) falls through a visible clone, so a link in it never
  // fires. Clones stay HIT-TESTABLE (a clone link navigates the same href);
  // assistive tech and the tab order are deduped instead: aria-hidden on the
  // clone, tabindex -1 on everything focusable inside it.
  var FOCUSABLE = 'a[href],area[href],button,input,select,textarea,iframe,' +
    '[tabindex],[contenteditable="true"]';
  function neutralize(clone) {
    clone.setAttribute('aria-hidden', 'true');
    clone.setAttribute('data-loop-clone', '');
    if (clone.matches && clone.matches(FOCUSABLE)) clone.setAttribute('tabindex', '-1');
    Array.prototype.forEach.call(clone.querySelectorAll(FOCUSABLE), function (el) {
      el.setAttribute('tabindex', '-1');
    });
    return clone;
  }
  function makeClone(track) {
    return neutralize(track.cloneNode(true));
  }

  function publishIndex(rootEl, items, coord) {
    // the canonical item whose band holds the viewport-center coordinate;
    // a discrete write, only on a real change (zero-flip)
    for (var i = 0; i < items.length; i++) {
      if (coord >= items[i].start && coord < items[i].end) {
        if (rootEl.getAttribute('data-ad-loop-index') !== String(i)) {
          rootEl.setAttribute('data-ad-loop-index', String(i));
        }
        return;
      }
    }
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-loop]';
    var friction = opts.friction != null ? opts.friction : FRICTION_DEFAULT;

    // Reduced motion: the finite authored track stands — the gap's fallback.
    if (reduce()) return { destroy: function () {} };

    injectCss();
    var units = [];

    Array.prototype.forEach.call(root.querySelectorAll(selector), function (el) {
      if (el.__adLoop) return; // idempotent per root
      var track = el.querySelector('[data-loop-track]');
      if (!track) return;
      var axis = el.getAttribute('data-ad-loop') === 'x' ? 'x' : 'y';
      var unit = { el: el, track: track, axis: axis, clones: [], on: true };
      el.classList.add('ad-isl-live');

      if (axis === 'y') {
        // period = one copy's height; clone until there is a full period of
        // runway on either side of the wrap band
        var period = track.offsetHeight;
        if (!period) { el.classList.remove('ad-isl-live'); return; }
        var need = period + 2 * el.clientHeight;
        while (el.scrollHeight < need + period) {
          var c = makeClone(track);
          el.appendChild(c);
          unit.clones.push(c);
        }
        unit.period = period;
        // rect-based, in track space — offsetTop's offsetParent is not
        // guaranteed to be the track
        var tRect = track.getBoundingClientRect();
        unit.items = Array.prototype.map.call(
          track.querySelectorAll('[data-loop-item]'),
          function (it) {
            var r = it.getBoundingClientRect();
            return { start: r.top - tRect.top, end: r.bottom - tRect.top };
          }
        );
        unit.onScroll = function () {
          // the seam: jump by one period onto identical pixels — the wrap is
          // invisible and native momentum carries straight across it
          var st = el.scrollTop;
          if (st < period * 0.5) el.scrollTop = st + period;
          else if (st > period * 1.5) el.scrollTop = st - period;
          if (unit.items.length) {
            // the center coordinate wraps too — without the modulo the
            // period's first items are unreachable as the published index
            publishIndex(el, unit.items,
              (el.scrollTop + el.clientHeight / 2) % period);
          }
        };
        el.scrollTop = period; // start mid-runway so the first gesture can go UP
        el.addEventListener('scroll', unit.onScroll, { passive: true });
      } else {
        var copy = track.scrollWidth;
        if (!copy) { el.classList.remove('ad-isl-live'); return; }
        // one period of per-item clones rides the SAME flex track as
        // trailing siblings, so a single transform moves both copies; each
        // clone is individually neutralized (see the driven finding above)
        Array.prototype.slice.call(track.children).forEach(function (child) {
          var c = neutralize(child.cloneNode(true));
          track.appendChild(c);
          unit.clones.push(c);
        });
        unit.copy = copy;
        unit.pos = 0; unit.vel = 0; unit.raf = 0;
        unit.dragging = false; unit.lastX = 0;
        var tRectX = track.getBoundingClientRect();
        unit.items = Array.prototype.map.call(
          track.querySelectorAll('[data-loop-item]:not([data-loop-clone])'),
          function (it) {
            var r = it.getBoundingClientRect();
            return { start: r.left - tRectX.left, end: r.right - tRectX.left };
          }
        );

        unit.apply = function () {
          // modulo wrap: pos lives on [0, copy) forever — never bottoms out
          unit.pos = ((unit.pos % unit.copy) + unit.copy) % unit.copy;
          track.style.transform = 'translate3d(' + (-unit.pos).toFixed(2) + 'px,0,0)';
          publishIndex(el, unit.items, (unit.pos + el.clientWidth / 2) % unit.copy);
        };
        unit.frame = function () {
          unit.raf = 0;
          if (!unit.dragging) {
            unit.pos += unit.vel;
            unit.vel *= friction; // the decelerating glide — measured, luxury
            if (Math.abs(unit.vel) < SETTLE) unit.vel = 0;
          }
          unit.apply();
          if ((unit.vel !== 0 || unit.dragging) && unit.on) {
            unit.raf = global.requestAnimationFrame(unit.frame);
          }
        };
        unit.wake = function () {
          if (!unit.raf && unit.on) unit.raf = global.requestAnimationFrame(unit.frame);
        };
        unit.onDown = function (e) {
          if (e.pointerType === 'mouse' && e.button !== 0) return;
          unit.dragging = true;
          unit.lastX = e.clientX;
          unit.vel = 0;
          el.classList.add('is-dragging');
          unit.wake();
          // capture can throw (a pointer released between events, a pen id
          // mismatch) — a failed capture must never abort the drag
          try { if (el.setPointerCapture) el.setPointerCapture(e.pointerId); }
          catch (err) {}
        };
        unit.onMovePtr = function (e) {
          if (!unit.dragging) return;
          var dx = e.clientX - unit.lastX;
          unit.lastX = e.clientX;
          unit.pos -= dx;
          unit.vel = -dx; // release inherits the hand's speed
        };
        unit.onUp = function () {
          if (!unit.dragging) return;
          unit.dragging = false;
          el.classList.remove('is-dragging');
          unit.wake();
        };
        unit.onWheel = function (e) {
          // a horizontal surface answers the wheel too — vertical intent
          // still scrolls the page (no preventDefault on dominant-Y wheels
          // unless the track owns the gesture via shift/deltaX)
          var d = Math.abs(e.deltaX) > Math.abs(e.deltaY) ? e.deltaX : (e.shiftKey ? e.deltaY : 0);
          if (!d) return;
          e.preventDefault();
          unit.vel += d * WHEEL_GAIN * 0.1;
          unit.pos += d * WHEEL_GAIN;
          unit.wake();
        };
        unit.onFocusIn = function (e) {
          // a transform track defeats native scroll-into-view — glide the
          // focused canonical item into the viewport ourselves
          var item = e.target.closest ? e.target.closest('[data-loop-item]') : null;
          if (!item || item.closest('[data-loop-clone]')) return;
          var ir = item.getBoundingClientRect();
          var tr = track.getBoundingClientRect();
          var want = (ir.left - tr.left) - (el.clientWidth - ir.width) / 2;
          // clamp, never wrap: a negative pos would modulo to the far end and
          // center the CLONE while the focused canonical item (and its focus
          // ring) sits off-screen — driven finding
          unit.pos = want < 0 ? 0 : want;
          unit.vel = 0;
          // the browser also focus-scrolls the hidden overflow — that
          // scrollLeft write fights the transform; the track owns position
          el.scrollLeft = 0;
          unit.apply();
        };
        el.addEventListener('pointerdown', unit.onDown);
        el.addEventListener('pointermove', unit.onMovePtr);
        el.addEventListener('pointerup', unit.onUp);
        el.addEventListener('pointercancel', unit.onUp);
        el.addEventListener('wheel', unit.onWheel, { passive: false });
        el.addEventListener('focusin', unit.onFocusIn);
        unit.apply();
      }

      el.__adLoop = unit;
      units.push(unit);
    });

    if (!units.length) return { destroy: function () {} };

    var io = null;
    if ('IntersectionObserver' in global) {
      io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          units.forEach(function (u) {
            if (u.el !== e.target) return;
            u.on = e.isIntersecting;
            if (u.on && u.wake) u.wake(); // off-screen parks the glide
          });
        });
      });
      units.forEach(function (u) { io.observe(u.el); });
    }
    var onVis = function () {
      if (document.hidden) return;
      units.forEach(function (u) { if (u.wake) u.wake(); });
    };
    document.addEventListener('visibilitychange', onVis);

    return {
      destroy: function () {
        if (io) io.disconnect();
        document.removeEventListener('visibilitychange', onVis);
        units.forEach(function (u) {
          u.el.classList.remove('ad-isl-live', 'is-dragging');
          u.el.removeAttribute('data-ad-loop-index');
          if (u.axis === 'y') {
            u.el.removeEventListener('scroll', u.onScroll);
            u.clones.forEach(function (c) {
              if (c.parentNode) c.parentNode.removeChild(c);
            });
            u.el.scrollTop = 0;
          } else {
            if (u.raf) global.cancelAnimationFrame(u.raf);
            u.el.removeEventListener('pointerdown', u.onDown);
            u.el.removeEventListener('pointermove', u.onMovePtr);
            u.el.removeEventListener('pointerup', u.onUp);
            u.el.removeEventListener('pointercancel', u.onUp);
            u.el.removeEventListener('wheel', u.onWheel);
            u.el.removeEventListener('focusin', u.onFocusIn);
            u.track.style.transform = '';
            // the horizontal clone items were folded into the track — drop
            // everything cloned
            Array.prototype.forEach.call(
              u.track.querySelectorAll('[data-loop-clone]'),
              function (c) { if (c.parentNode) c.parentNode.removeChild(c); }
            );
          }
          delete u.el.__adLoop;
        });
        var s = document.getElementById(CSS_ID);
        if (s && s.parentNode) s.parentNode.removeChild(s);
      }
    };
  }

  global.awardInfiniteScrollLoop = { init: init };
})(typeof window !== 'undefined' ? window : this);
