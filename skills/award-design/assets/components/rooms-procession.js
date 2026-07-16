/*
 * rooms-procession — the staged-rooms camera rig (winner: Cartier Watches &
 * Wonders 2025 by Immersive Garden + 60fps — six self-contained 3D alcoves
 * "like rooms in a museum after hours", one per watch, a persistent Web Audio
 * score threading them; Hubtown by Unseen Studio; Shopify Editions).
 * An ordered array of DISCRETE staged scenes shares ONE canvas + ONE camera
 * rig; scroll drives the inter-room transitions (a camera move or a cross-
 * dissolve) while each room owns its own lighting and composition. Distinct
 * from engine-world (one continuous scene) and portrait-procession (DOM
 * sections over one static-framed canvas): here every section is its own room
 * and scroll walks the camera from one to the next.
 *
 * The rig owns ONLY the scroll -> room-index / progress / transition math and
 * emits it through callbacks + a CustomEvent; the SCENE owns all rendering
 * (no Three import ever lives here). Cache rects on init/resize, read only
 * scrollY per frame — no per-frame layout thrash.
 *
 * Structure the component drives:
 *   <div data-ad-rooms>                     the track (pass as root)
 *     <section data-room> … </section>      room 0  (typically 100vh+)
 *     <section data-room> … </section>      room 1
 *     …
 *   </div>
 * The shared canvas is the builder's own fixed/sticky layer BEHIND the rooms;
 * the rooms carry the real, legible copy over it (content-visible at rest).
 *
 * Usage:  var rig = awardRoomsProcession.init(root, {
 *           onRoom:       function (index, prevIndex) {},   // active room changed
 *           onProgress:   function (index, t) {},           // t 0..1 within the room
 *           onTransition: function (from, to, t) {},        // t 0..1 across the hand-off
 *           window: 0.2,                                    // transition window fraction
 *           ease:   0.1                                     // differential lerp on the t's
 *         });
 *   root         the [data-ad-rooms] track; its direct [data-room] children are the rooms
 *   onRoom       fires when the active room changes — a room's CENTRE crossing the
 *                viewport centre (raw, not eased, so the stamp/event are crisp)
 *   onProgress   the active room's own progress, eased by `ease` (inertial, not stepped)
 *   onTransition the hand-off window straddling a room boundary: the last `window`
 *                fraction of a room plus the first `window` of the next, t=0.5 at the
 *                boundary — where the scene cross-dissolves or moves its camera
 *   window       fraction of a room's scroll that is the transition (default 0.2, 0<w<=0.5)
 *   ease         differential lerp applied to the emitted t values (default 0.1)
 * Returns { destroy() }. Idempotent.
 *
 * The active index is stamped on the track as data-ad-active-room (a styling
 * hook) and a bubbling CustomEvent `ad:room` (detail:{index,prevIndex}) fires
 * for decoupled listeners.
 *
 * Reduced-motion: the callbacks still fire, but with SNAPPED values — t jumps
 * 0->1 with no lerp, transitions are hard cuts — so the scene renders discrete
 * composed rooms (a slideshow), never a scrub. No-JS: the rooms are plain
 * document flow and stay fully legible; only the camera math is missing.
 *
 * Perf: one rAF, self-rescheduling only while the eased position is still
 * catching up; woken by scroll/resize, paused on hidden tabs; rects cached and
 * recomputed on resize/load, never per frame.
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-rooms-procession-css';
  var EPS = 0.0004;
  var reduce = function () {
    return global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches;
  };
  var clamp = function (v, lo, hi) { return v < lo ? lo : v > hi ? hi : v; };
  var scrollTop = function () {
    return global.pageYOffset != null ? global.pageYOffset : (document.documentElement.scrollTop || 0);
  };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    // Logic-first rig: the CSS only establishes the stacking so the builder's
    // fixed canvas shows through, floors each room to the viewport, and pre-
    // wires the data-ad-active-room hook to the signature timing. It sets no
    // background (that would occlude the canvas) and no opacity (rooms stay
    // legible at rest) — the reduced-motion guard keeps the hook honest.
    s.textContent =
      '[data-ad-rooms]{position:relative;}' +
      '[data-ad-rooms]>[data-room]{position:relative;z-index:1;min-block-size:100svh;}' +
      '@media (prefers-reduced-motion:no-preference){' +
      '[data-ad-rooms]>[data-room]{transition:opacity var(--ad-dur-base,420ms) var(--ad-ease-signature,cubic-bezier(.16,1,.3,1));}}';
    document.head.appendChild(s);
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    injectCss();

    // root IS the track when it carries data-ad-rooms, else the first one within.
    var track = (root.getAttribute && root.getAttribute('data-ad-rooms') !== null)
      ? root
      : (root.querySelector ? root.querySelector('[data-ad-rooms]') : null);
    var roomEls = track
      ? Array.prototype.filter.call(track.children, function (el) { return el.hasAttribute('data-room'); })
      : [];

    if (!track || !roomEls.length) {
      return { destroy: function () {} };
    }

    var win = clamp(opts.window != null ? opts.window : 0.2, 0.001, 0.5);
    var ease = opts.ease != null ? opts.ease : 0.1;
    var snap = reduce();
    var n = roomEls.length;

    var rooms = [];          // cached geometry per room, doc-space
    var smoothPos = 0;       // eased procession position in [0, n-1]
    var curActive = -1;      // last active index emitted through onRoom
    var txActive = false;    // a transition window is currently open
    var txK = -1;            // the boundary (room index) that window straddles
    var rafId = 0;

    // Recompute rects only here (init/resize/load), never per frame.
    function measure() {
      var sy = scrollTop();
      rooms = roomEls.map(function (el) {
        var r = el.getBoundingClientRect();
        var top = r.top + sy;
        return { center: top + r.height / 2 };
      });
    }

    // Procession position from scroll: viewport centre walked over the room
    // centres, piecewise-linear and monotonic across [0, n-1]. Room i's centre
    // sits at integer i, so floor(pos) is the centre-crossing active index and
    // integer boundaries are exactly the room hand-offs.
    function rawPos() {
      var vh = global.innerHeight || document.documentElement.clientHeight;
      var v = scrollTop() + vh / 2;
      if (v <= rooms[0].center) return 0;
      if (v >= rooms[n - 1].center) return n - 1;
      for (var i = 0; i < n - 1; i++) {
        var c1 = rooms[i + 1].center;
        if (v < c1) {
          var c0 = rooms[i].center;
          return i + clamp((v - c0) / Math.max(1, c1 - c0), 0, 1);
        }
      }
      return n - 1;
    }

    function frame() {
      rafId = 0;
      var target = rawPos();
      smoothPos = snap ? target : smoothPos + (target - smoothPos) * ease;

      var active = clamp(Math.floor(target), 0, n - 1);
      if (active !== curActive) {
        var prev = curActive;
        curActive = active;
        track.setAttribute('data-ad-active-room', String(active));
        if (opts.onRoom) opts.onRoom(active, prev);
        track.dispatchEvent(new CustomEvent('ad:room', {
          bubbles: true, detail: { index: active, prevIndex: prev }
        }));
        // Snapped hand-off: a hard cut into the newly-composed room.
        if (snap && opts.onTransition && prev !== -1) opts.onTransition(prev, active, 1);
      }

      if (opts.onProgress) {
        opts.onProgress(active, snap ? 1 : clamp(smoothPos - active, 0, 1));
      }

      // Eased cross-boundary hand-off. Only interior boundaries (1..n-1) carry a
      // transition; t=0.5 sits on the boundary, 0/1 at the window edges.
      if (!snap && opts.onTransition) {
        var k = Math.round(smoothPos);
        if (k >= 1 && k <= n - 1 && Math.abs(smoothPos - k) <= win) {
          opts.onTransition(k - 1, k, clamp(0.5 + (smoothPos - k) / (2 * win), 0, 1));
          txActive = true;
          txK = k;
        } else if (txActive) {
          // Settle the window that just closed to its terminal, once.
          opts.onTransition(txK - 1, txK, smoothPos >= txK ? 1 : 0);
          txActive = false;
        }
      }

      if (!snap && Math.abs(target - smoothPos) > EPS) rafId = global.requestAnimationFrame(frame);
    }

    function kick() { if (!rafId) rafId = global.requestAnimationFrame(frame); }

    var onScroll = function () { if (!document.hidden) kick(); };
    var onResize = function () { measure(); kick(); };
    var onVis = function () { if (!document.hidden) kick(); };

    measure();
    smoothPos = rawPos();   // start converged — no lurch from 0 on a deep-linked load
    global.addEventListener('scroll', onScroll, { passive: true });
    global.addEventListener('resize', onResize, { passive: true });
    global.addEventListener('load', onResize);
    document.addEventListener('visibilitychange', onVis);
    kick();

    return {
      destroy: function () {
        if (rafId) global.cancelAnimationFrame(rafId);
        rafId = 0;
        global.removeEventListener('scroll', onScroll);
        global.removeEventListener('resize', onResize);
        global.removeEventListener('load', onResize);
        document.removeEventListener('visibilitychange', onVis);
        track.removeAttribute('data-ad-active-room');
        rooms = [];
        var s = document.getElementById(CSS_ID);
        if (s) s.parentNode.removeChild(s);
      }
    };
  }

  global.awardRoomsProcession = { init: init };
})(typeof window !== 'undefined' ? window : this);
