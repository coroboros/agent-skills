/*
 * drag-scrub-video — grab-drag over a video field maps pointer delta to
 * video.currentTime (winner: KAI Design Dept.; still-scrub cousin: Siena via
 * scrub-film). Extends scrub-film's scroll/pointer-position mapping with a
 * DRAG: the whole SECTION is the operable field, horizontal or vertical, and
 * the footage advances exactly as far as the hand pulls — the verified core
 * is `video.currentTime = sec`, nothing more. Release momentum is an OPT-IN
 * enhancement (opts.momentum) documented as unverified on the winner — the
 * KAI Codrops source shows no inertia; default off.
 * The frame is legible at rest as its poster; reduced motion holds the
 * poster with no seeking and binds nothing. Native touch keeps its page
 * scroll: axis x fields declare touch-action:pan-y (vertical intent pans the
 * page, horizontal drags scrub), axis y the inverse.
 *
 * Scrub encoding (cross-browser seek responsiveness):
 *   ffmpeg -i in.mp4 -c:v libx264 -profile:v baseline -g 12 -keyint_min 12 \
 *     -sc_threshold 0 -pix_fmt yuv420p -movflags +faststart -an out.mp4
 *   H.264 baseline + a ~12-frame keyframe interval trades bytes for seek
 *   granularity. Firefox seeks land on keyframes; sample-accurate scrubbing
 *   there needs a WebCodecs decode path (mediabunny) — noted, not built.
 *   The winner's WebGL line depth-of-field is a delegated shader layer —
 *   noted, not built.
 *
 * Expected markup — the field wraps the video plus any caption/labels; the
 * whole box is grabbable:
 *   <section data-ad-drag-scrub data-ad-drag-scrub-axis="x">
 *     <video data-ad-drag-scrub-video muted playsinline preload="auto"
 *            poster="…" src="…"></video>
 *   </section>
 *
 * Usage:  awardDragScrubVideo.init(root, opts)
 *   root      Element|Document  scope (default document)
 *   selector  string  fields (default '[data-ad-drag-scrub]')
 *   axis      string  'x' | 'y' (default reads data-ad-drag-scrub-axis, else 'x')
 *   gain      number  drag distance = one full duration, as a multiple of the
 *                     field's axis size (default 1 — one field-length scrubs
 *                     the whole clip)
 *   momentum  0..1    per-frame velocity decay on release; OFF when absent
 *                     (unverified enhancement — see header)
 * Returns { destroy() }. Idempotent per field.
 *
 * A11y: the field is a keyboard stop — ArrowLeft/ArrowRight (axis y: Up/
 * Down) step the footage ±0.5s, so the scrub is operable without a pointer.
 * A clean click/tap inside the field stays a click; only travel past the
 * threshold engages the drag, and the native image/text drag ghost is
 * suppressed. Pair with cursor-verb-label for the DRAG affordance — never
 * the native grab cursor.
 * Perf: seeks are rAF-throttled, skipped mid-seek and under one frame of
 * change (scrub-film's discipline), paused off-screen and on hidden tabs.
 * Serving: scrubbing needs HTTP Range support — on a server without it the
 * component self-heals by pulling the source into an in-memory blob
 * (scrub-film's established fallback).
 *
 * Tokens: --ad-accent (the field's :focus-visible ring).
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-drag-scrub-video-css';
  var DRAG_THRESHOLD = 6;   // px of travel before a press becomes a drag
  var KEY_STEP = 0.5;       // s per arrow press
  var MIN_VELOCITY = 0.001; // duration-fraction/ms — momentum below this stops
  var STALE_MS = 80;        // a release this long after the last move carries no throw

  var reduce = function () {
    return global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches;
  };
  var nowMs = function () {
    return (global.performance && global.performance.now) ? global.performance.now() : Date.now();
  };
  var clamp = function (v, lo, hi) { return v < lo ? lo : v > hi ? hi : v; };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      '[data-ad-drag-scrub]{position:relative;overflow:hidden;' +
      'touch-action:pan-y pinch-zoom;user-select:none;-webkit-user-select:none;}' +
      '[data-ad-drag-scrub-axis="y"]{touch-action:pan-x pinch-zoom;}' +
      '[data-ad-drag-scrub] video{display:block;width:100%;height:100%;object-fit:cover;' +
      'pointer-events:none;-webkit-user-drag:none;}' +
      '[data-ad-drag-scrub]:focus-visible{outline:2px solid ' +
      'var(--ad-accent,oklch(62% 0.2 25));outline-offset:-2px;}';
    document.head.appendChild(s);
  }

  // A server without HTTP Range support (python -m http.server, some static
  // hosts) leaves the video's seekable ranges empty even when fully buffered —
  // currentTime writes silently no-op and the scrub is dead. Self-heal: pull
  // the source into an in-memory blob, which is always fully seekable.
  function ensureSeekable(video) {
    var check = function () {
      if (video.__adBlobbed) return;
      var d = video.duration;
      var dead = !video.seekable.length ||
        (d && isFinite(d) && video.seekable.end(video.seekable.length - 1) < d * 0.5);
      if (!dead || typeof global.fetch !== 'function') return;
      video.__adBlobbed = true;
      var src = video.currentSrc || video.src;
      if (!src || src.indexOf('blob:') === 0) return;
      global.fetch(src)
        .then(function (r) { return r.blob(); })
        .then(function (b) {
          var t = video.currentTime;
          video.src = URL.createObjectURL(b);
          video.load();
          video.addEventListener('loadedmetadata', function () {
            try { video.currentTime = t; } catch (e) { /* not seekable yet */ }
          }, { once: true });
        })
        .catch(function () { video.__adBlobbed = false; });
    };
    if (video.readyState >= 1) check();
    else video.addEventListener('loadedmetadata', check, { once: true });
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-drag-scrub]';
    var gain = opts.gain != null ? opts.gain : 1;
    injectCss();

    var fields = [];

    Array.prototype.forEach.call(root.querySelectorAll(selector), function (el) {
      if (el.__adDragScrub) return; // idempotent
      var video = el.querySelector('[data-ad-drag-scrub-video], video');
      if (!video) return;
      var axis = opts.axis || el.getAttribute('data-ad-drag-scrub-axis') || 'x';

      // We own currentTime: muted, inline, never autoplaying.
      video.muted = true;
      video.setAttribute('playsinline', '');
      video.pause();
      if (!video.getAttribute('preload')) video.preload = 'auto';

      if (reduce()) return; // hold the poster; no seeking, no listeners

      ensureSeekable(video);
      if (!el.hasAttribute('tabindex')) el.setAttribute('tabindex', '0');

      var target = 0;       // 0..1 fraction of duration
      var applied = -1;     // seconds last written
      var raf = 0, running = false, inView = true;

      // drag state
      var pending = false, dragging = false, pointerId = null;
      var startX = 0, startY = 0, startTarget = 0;
      var lastP = 0, lastT = 0, vel = 0; // fraction/ms, EMA-smoothed
      var momRAF = 0, momPrev = 0;

      function duration() {
        var d = video.duration;
        return d && isFinite(d) ? d : 0;
      }
      function span() {
        var r = el.getBoundingClientRect();
        return Math.max(1, (axis === 'y' ? r.height : r.width) * gain);
      }

      // Seek only when buffered, in view, not mid-seek, and the target moved
      // at least ~one frame — a naive per-event seek thrashes the decoder.
      function apply() {
        var d = duration();
        if (!d) return;
        var t = clamp(target, 0, 1) * d;
        if (video.seeking) return;
        var minStep = Math.max(1 / 30, d / 600);
        if (Math.abs(t - applied) < minStep) return;
        applied = t;
        try { video.currentTime = t; } catch (e) { /* not seekable yet */ }
      }
      function frame() {
        raf = 0;
        if (!inView) { running = false; return; }
        apply();
        if (running && (dragging || momRAF)) raf = global.requestAnimationFrame(frame);
        else running = false;
      }
      function kick() {
        if (document.hidden) return;
        running = true;
        if (!raf) raf = global.requestAnimationFrame(frame);
      }

      function stopMomentum() {
        if (momRAF) { global.cancelAnimationFrame(momRAF); momRAF = 0; }
        vel = 0;
      }
      function momentumTick(now) {
        momRAF = 0;
        var dt = now - momPrev; momPrev = now;
        if (dt > 64) dt = 64; // a backgrounded tab must not fling on return
        target = clamp(target + vel * dt, 0, 1);
        vel *= Math.pow(opts.momentum, dt / 16.667);
        apply();
        if (Math.abs(vel) < MIN_VELOCITY || target <= 0 || target >= 1) { stopMomentum(); return; }
        momRAF = global.requestAnimationFrame(momentumTick);
      }

      function onPointerDown(e) {
        if (e.button != null && e.button !== 0) return;
        stopMomentum();
        pending = true; dragging = false;
        pointerId = e.pointerId;
        startX = e.clientX; startY = e.clientY;
        startTarget = target;
        lastP = axis === 'y' ? e.clientY : e.clientX;
        lastT = e.timeStamp || nowMs();
        vel = 0;
      }
      function onPointerMove(e) {
        if (!pending && !dragging) return;
        var p = axis === 'y' ? e.clientY : e.clientX;
        var cross = axis === 'y' ? e.clientX - startX : e.clientY - startY;
        var along = p - (axis === 'y' ? startY : startX);
        if (!dragging) {
          if (Math.abs(along) < DRAG_THRESHOLD && Math.abs(cross) < DRAG_THRESHOLD) return;
          // cross-axis intent → the page keeps its native pan, no scrub engages
          if (Math.abs(cross) > Math.abs(along)) { pending = false; return; }
          dragging = true;
          try { el.setPointerCapture(pointerId); } catch (err) { /* capture optional */ }
        }
        e.preventDefault();
        var now = e.timeStamp || nowMs();
        var dt = now - lastT || 16;
        target = clamp(startTarget + along / span(), 0, 1);
        var instV = (p - lastP) / span() / dt;
        vel = vel * 0.7 + instV * 0.3;
        lastP = p; lastT = now;
        kick();
      }
      function onPointerUp() {
        if (pointerId != null) { try { el.releasePointerCapture(pointerId); } catch (err) {} }
        var wasDragging = dragging;
        pending = false; dragging = false; pointerId = null;
        // opt-in only — the winner documents currentTime = sec, no inertia
        if (opts.momentum != null && wasDragging &&
            (nowMs() - lastT) < STALE_MS && Math.abs(vel) > MIN_VELOCITY) {
          momPrev = nowMs();
          momRAF = global.requestAnimationFrame(momentumTick);
          kick();
        } else {
          vel = 0;
          apply(); // land the final frame of the drag
        }
      }
      function onDragStart(e) { e.preventDefault(); } // no native drag ghost
      function onKeyDown(e) {
        var back = axis === 'y' ? 'ArrowUp' : 'ArrowLeft';
        var fwd = axis === 'y' ? 'ArrowDown' : 'ArrowRight';
        if (e.key !== back && e.key !== fwd) return;
        e.preventDefault();
        var d = duration();
        if (!d) return;
        target = clamp(target + (e.key === fwd ? KEY_STEP : -KEY_STEP) / d, 0, 1);
        // a deliberate step always lands — written past the drag stream's
        // mid-seek/min-step throttle, which would swallow a rapid second press
        applied = target * d;
        try { video.currentTime = applied; } catch (err) { /* not seekable yet */ }
      }
      function onVis() { if (!document.hidden && (dragging || momRAF)) kick(); }

      var io = null;
      if ('IntersectionObserver' in global) {
        io = new IntersectionObserver(function (entries) {
          entries.forEach(function (en) { inView = en.isIntersecting; });
        }, { threshold: 0 });
        io.observe(el);
      }

      el.addEventListener('pointerdown', onPointerDown, { passive: true });
      global.addEventListener('pointermove', onPointerMove, { passive: false });
      global.addEventListener('pointerup', onPointerUp, { passive: true });
      global.addEventListener('pointercancel', onPointerUp, { passive: true });
      el.addEventListener('dragstart', onDragStart);
      el.addEventListener('keydown', onKeyDown);
      document.addEventListener('visibilitychange', onVis);

      el.__adDragScrub = true;
      fields.push({
        destroy: function () {
          if (raf) global.cancelAnimationFrame(raf);
          stopMomentum();
          if (io) io.disconnect();
          el.removeEventListener('pointerdown', onPointerDown);
          global.removeEventListener('pointermove', onPointerMove);
          global.removeEventListener('pointerup', onPointerUp);
          global.removeEventListener('pointercancel', onPointerUp);
          el.removeEventListener('dragstart', onDragStart);
          el.removeEventListener('keydown', onKeyDown);
          document.removeEventListener('visibilitychange', onVis);
          el.removeAttribute('tabindex');
          delete el.__adDragScrub;
        }
      });
    });

    return {
      destroy: function () {
        fields.forEach(function (f) { f.destroy(); });
        fields = [];
        var s = document.getElementById(CSS_ID);
        if (s && s.parentNode) s.parentNode.removeChild(s);
      }
    };
  }

  global.awardDragScrubVideo = { init: init };
})(typeof window !== 'undefined' ? window : this);
