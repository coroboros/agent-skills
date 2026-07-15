/*
 * scrub-film — the operable film still (winner: Siena Film Foundation).
 * A <video> the visitor DRIVES instead of watching: its currentTime is mapped
 * from scroll progress (the still develops as the section passes) or from the
 * pointer's horizontal position (drag your eye across the frame and it plays).
 * The spectacle is that the medium is live and under the visitor's hand, never
 * an autoplaying loop. The frame is legible at rest as its poster, so a dead
 * script or no-JS render shows a static still, and reduced-motion holds the
 * poster with no seeking.
 *
 * Structure the component drives:
 *   <div data-ad-scrub>                          scroll mode, element's own progress
 *     <video data-ad-scrub-video muted playsinline preload="auto" poster="…">
 *   </div>
 * Pinned scroll (the still holds while a tall track scrolls behind it):
 *   <div data-ad-scrub-track style="height:250vh">
 *     <div data-ad-scrub data-ad-scrub-pin> <video …> </div>   (goes position:sticky)
 *   </div>
 * Pointer mode: add data-ad-scrub-mode="pointer" (or pass opts.mode).
 *
 * Usage:  awardScrubFilm.init(root, { selector, mode, axis, range })
 *   selector  string   scrub roots (default '[data-ad-scrub]')
 *   mode      string   'scroll' | 'pointer' (default reads data-ad-scrub-mode, else 'scroll')
 *   axis      string   pointer axis 'x' | 'y' (default 'x')
 *   range     [n,n]    scroll-progress window mapped to 0..duration (default [0,1])
 * Returns { destroy() }. Idempotent.
 *
 * Perf: currentTime is a decode, not a transform — seeks are rAF-throttled, skipped
 * while a prior seek is in flight and when the target moves less than one frame, and
 * paused when the frame is off-screen (IntersectionObserver) or the tab is hidden.
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-scrub-film-css';
  var reduce = function () {
    return global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches;
  };
  var clamp = function (v, lo, hi) { return v < lo ? lo : v > hi ? hi : v; };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      '[data-ad-scrub]{position:relative;overflow:hidden;}' +
      '[data-ad-scrub] video{display:block;width:100%;height:100%;object-fit:cover;}' +
      '[data-ad-scrub-pin]{position:sticky;top:0;height:100vh;}';
    document.head.appendChild(s);
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-scrub]';
    injectCss();

    var roots = Array.prototype.slice.call(root.querySelectorAll(selector));
    var units = [];
    var rafId = 0;
    var running = false;

    function makeUnit(el) {
      var video = el.matches('video') ? el : el.querySelector('[data-ad-scrub-video], video');
      if (!video) return null;
      var mode = opts.mode || el.getAttribute('data-ad-scrub-mode') || 'scroll';
      var axis = opts.axis || el.getAttribute('data-ad-scrub-axis') || 'x';
      var range = opts.range || [0, 1];
      // Seek target manual playback needs: muted + no autoplay; we own currentTime.
      video.muted = true;
      video.setAttribute('playsinline', '');
      video.pause();
      if (!video.getAttribute('preload')) video.preload = 'auto';
      var track = el.closest ? el.closest('[data-ad-scrub-track]') : null;
      return {
        el: el, video: video, mode: mode, axis: axis, range: range,
        track: track, inView: false, target: 0, applied: -1
      };
    }

    // Progress 0..1 of this unit given the current scroll position.
    function scrollProgress(u) {
      var vh = global.innerHeight || document.documentElement.clientHeight;
      var p;
      if (u.track) {
        var t = u.track.getBoundingClientRect();
        p = -t.top / Math.max(1, t.height - vh);          // pinned: travel through the track
      } else {
        var r = u.el.getBoundingClientRect();
        p = (vh - r.top) / Math.max(1, vh + r.height);    // free: enter-bottom to exit-top
      }
      p = clamp(p, 0, 1);
      var lo = u.range[0], hi = u.range[1];
      return clamp((p - lo) / Math.max(0.0001, hi - lo), 0, 1);
    }

    function duration(u) {
      var d = u.video.duration;
      return d && isFinite(d) ? d : 0;
    }

    // Seek only when the frame is buffered, in view, not mid-seek, and the target
    // moved at least ~one frame — a naive per-event seek thrashes the decoder.
    function apply(u) {
      var d = duration(u);
      if (!d) return;
      var t = u.target * d;
      if (u.video.seeking) return;
      var minStep = Math.max(1 / 30, d / 600);
      if (Math.abs(t - u.applied) < minStep) return;
      u.applied = t;
      try { u.video.currentTime = t; } catch (e) { /* not seekable yet */ }
    }

    function frame() {
      rafId = 0;
      var any = false;
      units.forEach(function (u) {
        if (!u.inView) return;
        any = true;
        if (u.mode === 'scroll') u.target = scrollProgress(u);
        apply(u);
      });
      if (any && running) schedule();
      else running = false;
    }
    function schedule() {
      running = true;
      if (!rafId) rafId = global.requestAnimationFrame(frame);
    }
    function kick() { if (!rafId) rafId = global.requestAnimationFrame(frame); running = true; }

    // Pointer mode drives target off the cursor; scroll mode wakes the loop.
    function onPointerMove(u, e) {
      var r = u.el.getBoundingClientRect();
      u.target = u.axis === 'y'
        ? clamp((e.clientY - r.top) / Math.max(1, r.height), 0, 1)
        : clamp((e.clientX - r.left) / Math.max(1, r.width), 0, 1);
      kick();
    }

    var io = null, onScroll = null, onVis = null;
    var pointerBindings = [];

    function start() {
      units = roots.map(makeUnit).filter(Boolean);
      if (!units.length) return;

      if (reduce()) return;   // hold the poster; no seeking, no listeners

      if ('IntersectionObserver' in global) {
        io = new IntersectionObserver(function (entries) {
          entries.forEach(function (e) {
            var u = units.filter(function (x) { return x.el === e.target; })[0];
            if (u) { u.inView = e.isIntersecting; if (u.inView) kick(); }
          });
        }, { threshold: 0 });
        units.forEach(function (u) { io.observe(u.el); });
      } else {
        units.forEach(function (u) { u.inView = true; });
      }

      units.forEach(function (u) {
        if (u.mode !== 'pointer') return;
        var handler = function (e) { onPointerMove(u, e); };
        u.el.addEventListener('pointermove', handler, { passive: true });
        pointerBindings.push({ el: u.el, handler: handler });
      });

      onScroll = function () { kick(); };
      global.addEventListener('scroll', onScroll, { passive: true });
      global.addEventListener('resize', onScroll, { passive: true });

      onVis = function () { if (!document.hidden) kick(); };
      document.addEventListener('visibilitychange', onVis);

      kick();
    }

    start();

    return {
      destroy: function () {
        if (rafId) global.cancelAnimationFrame(rafId);
        rafId = 0; running = false;
        if (io) io.disconnect();
        if (onScroll) { global.removeEventListener('scroll', onScroll); global.removeEventListener('resize', onScroll); }
        if (onVis) document.removeEventListener('visibilitychange', onVis);
        pointerBindings.forEach(function (b) { b.el.removeEventListener('pointermove', b.handler); });
        pointerBindings = [];
        units = [];
      }
    };
  }

  global.awardScrubFilm = { init: init };
})(typeof window !== 'undefined' ? window : this);
