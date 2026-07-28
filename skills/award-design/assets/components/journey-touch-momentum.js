/*
 * journey-touch-momentum — the touch model for the wheel-driven in-engine
 * journey (winners: Lusion v3 — Dev SOTY 2023, responsive 8.40; Shader
 * Development Studio — SOTD 2026-04-20, responsive 8.40; both verified
 * wheel-driven no-native-scroll scenes — plus Igloo Inc). The archetype's
 * most common stack has NO native scroll: the wheel feeds a camera-lerp
 * through a bespoke scrub. This component IS that scrub with touch as a
 * first-class citizen: touchmove feeds the SAME position the wheel drives,
 * a fling captures the gesture's release velocity and decays it as momentum,
 * and the scrub position SURVIVES the gesture — there is no native scroll
 * to fall back to and none is created. Keyboard rides the same scrub
 * (arrows / PageUp/Down / Home/End on the focused surface — the usability
 * floor). Exact winner parameters were never published (Lusion's driver is
 * corroborated by its public WebGL Scroll Sync repo, numbers
 * reference-carried): every default below is a DEFAULT, not a measured
 * winner value.
 *
 * Ruled DISTINCT from smooth-scroll (Lenis wraps the NATIVE document
 * scroll — this stack has none), from horizontal-scroll-chain (welded to
 * CONSUMED native page scroll), and from drag-scrub-video (pointer delta →
 * a bounded media currentTime, no inertia — this drives a world position
 * with fling momentum). The two other touch answers the manifest encodes
 * stay theirs: physics-tap belongs to the physics field, raycast-recreated
 * input to the playable world (in-3d-dom-input-bridge).
 *
 * Usage:  awardJourneyTouchMomentum.init(root, opts)
 *   root       the journey surface carrying data-ad-journey (or an ancestor)
 *   length     virtual journey length in px (default 4000)
 *   wheelRate  wheel px -> journey px (default 1)
 *   touchRate  touch px -> journey px (default 1.5 — touch travels farther
 *              per gesture; a default, not a winner read)
 *   lerp       camera chase factor per 60fps frame (default 0.1)
 *   decay      momentum decay per 60fps frame (default 0.95)
 *   keyStep    px per arrow key (default 120; PageUp/Down = one viewport)
 *   onProgress function (p, pos, v)  per frame while the scrub settles —
 *              p 0..1, pos px, v px/frame; the engine maps p to its camera
 * Returns { destroy(), position() }. Idempotent per surface.
 *
 * The gesture contract: touch-action:none on the surface (the journey owns
 * the gesture; vertical pans must not rubber-band a page that is 1vh tall
 * anyway), wheel non-passive + preventDefault (the wheel drives the camera,
 * not a document). Velocity is sampled over the last ~80ms of the gesture;
 * released, it decays exponentially until under half a px/frame. Gates: the
 * settle loop runs only while the surface is on-screen (IO) and the tab
 * visible — going hidden freezes the scrub in place and the position
 * survives (never resets). reduced-motion: the journey stays NAVIGABLE
 * (interaction is not decoration) but the GLIDE goes — inputs set the
 * position directly, no lerp chase, no fling inertia; the engine receives
 * discrete steps.
 *
 * Tokens: --ad-accent (the surface's :focus-visible ring).
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-journey-touch-momentum-css';
  var SAMPLE_MS = 80;   // velocity window at touchend
  var REST_V = 0.5;     // px/frame — under this the momentum is spent
  var REST_D = 0.5;     // px — under this the chase has settled

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      '[data-ad-journey]{touch-action:none;overscroll-behavior:none;}' +
      '[data-ad-journey]:focus-visible{outline:2px solid var(--ad-accent,oklch(62% 0.2 25));' +
        'outline-offset:2px;}';
    document.head.appendChild(s);
  }

  var reduce = function () {
    return !!(global.matchMedia &&
      global.matchMedia('(prefers-reduced-motion: reduce)').matches);
  };

  function init(root, opts) {
    root = root || document;
    opts = opts || {};

    var surface = (root.getAttribute && root.getAttribute('data-ad-journey') != null)
      ? root
      : (root.querySelector ? root.querySelector('[data-ad-journey]') : null);
    if (!surface) return { destroy: function () {}, position: function () { return 0; } };
    if (surface.__adJourney) return surface.__adJourney.handle;

    var length = opts.length != null ? +opts.length : 4000;
    var wheelRate = opts.wheelRate != null ? +opts.wheelRate : 1;
    var touchRate = opts.touchRate != null ? +opts.touchRate : 1.5;
    var lerp = opts.lerp != null ? +opts.lerp : 0.1;
    var decay = opts.decay != null ? +opts.decay : 0.95;
    var keyStep = opts.keyStep != null ? +opts.keyStep : 120;
    var onProgress = typeof opts.onProgress === 'function' ? opts.onProgress : function () {};
    var still = reduce();

    injectCss();
    if (!surface.hasAttribute('tabindex')) surface.setAttribute('tabindex', '0');

    var target = 0, pos = 0, v = 0;
    var rafId = 0, last = 0;
    var touch = null;             // { id, y, samples: [{t, y}] }
    var onScreen = false;

    function clamp(x) { return Math.max(0, Math.min(length, x)); }

    function emit() { onProgress(length ? pos / length : 0, pos, v); }

    function wake() {
      if (still) {
        // no glide: the scrub answers the input directly, one discrete step
        pos = target; v = 0; emit();
        return;
      }
      if (!rafId && onScreen && !document.hidden) {
        last = 0;
        rafId = global.requestAnimationFrame(frame);
      }
    }

    function frame(now) {
      rafId = 0;
      if (!onScreen || document.hidden) return; // frozen in place — the position survives
      if (!last) last = now;
      var dt = Math.max(1, now - last);
      last = now;
      var f = dt / (1000 / 60); // frames of nominal 60fps elapsed
      if (v !== 0) {
        target = clamp(target + v * f);
        v *= Math.pow(decay, f);
        if (Math.abs(v) < REST_V || target === 0 || target === length) v = 0;
      }
      pos += (target - pos) * (1 - Math.pow(1 - lerp, f));
      if (Math.abs(target - pos) < REST_D && v === 0) {
        pos = target;
        emit();
        return; // settled — the loop sleeps until the next input
      }
      emit();
      rafId = global.requestAnimationFrame(frame);
    }

    // --- the wheel drives the camera, not a document ---
    function onWheel(e) {
      e.preventDefault();
      var d = e.deltaY;
      if (e.deltaMode === 1) d *= 16; else if (e.deltaMode === 2) d *= global.innerHeight;
      v = 0; // a fresh hand on the wheel overrides spent momentum
      target = clamp(target + d * wheelRate);
      wake();
    }

    // --- touch feeds the SAME scrub; release velocity becomes momentum ---
    function onTouchStart(e) {
      if (touch) return;
      var t = e.changedTouches[0];
      touch = { id: t.identifier, y: t.clientY, samples: [] };
      v = 0; // the finger catches the world — momentum yields to the hand
      wake();
    }
    function onTouchMove(e) {
      if (!touch) return;
      for (var i = 0; i < e.changedTouches.length; i++) {
        var t = e.changedTouches[i];
        if (t.identifier !== touch.id) continue;
        e.preventDefault();
        var dy = touch.y - t.clientY; // drag up = advance (the scroll convention)
        touch.y = t.clientY;
        target = clamp(target + dy * touchRate);
        touch.samples.push({ t: global.performance.now(), y: t.clientY });
        wake();
      }
    }
    function onTouchEnd(e) {
      if (!touch) return;
      for (var i = 0; i < e.changedTouches.length; i++) {
        if (e.changedTouches[i].identifier !== touch.id) continue;
        // the fling: velocity over the last SAMPLE_MS window becomes momentum
        var now = global.performance.now();
        var s = touch.samples.filter(function (x) { return now - x.t <= SAMPLE_MS; });
        if (!still && s.length >= 2) {
          var a = s[0], b = s[s.length - 1];
          var dt = Math.max(1, b.t - a.t);
          var pxPerMs = (a.y - b.y) / dt; // up-drag positive
          v = pxPerMs * (1000 / 60) * touchRate; // px per nominal frame
        }
        touch = null;
        wake(); // the scrub position survives the gesture — decay from here
      }
    }

    // --- keyboard rides the same scrub (the usability floor) ---
    function onKeyDown(e) {
      var d = null;
      if (e.code === 'ArrowDown' || e.code === 'ArrowRight') d = keyStep;
      else if (e.code === 'ArrowUp' || e.code === 'ArrowLeft') d = -keyStep;
      else if (e.code === 'PageDown') d = global.innerHeight;
      else if (e.code === 'PageUp') d = -global.innerHeight;
      else if (e.code === 'Home') { e.preventDefault(); v = 0; target = 0; wake(); return; }
      else if (e.code === 'End') { e.preventDefault(); v = 0; target = length; wake(); return; }
      if (d == null) return;
      e.preventDefault();
      v = 0;
      target = clamp(target + d);
      wake();
    }

    var io = null;
    if (global.IntersectionObserver) {
      io = new global.IntersectionObserver(function (entries) {
        onScreen = entries[entries.length - 1].isIntersecting;
        wake();
      });
      io.observe(surface);
    } else {
      onScreen = true;
    }
    function onVis() { wake(); }

    surface.addEventListener('wheel', onWheel, { passive: false });
    surface.addEventListener('touchstart', onTouchStart, { passive: true });
    surface.addEventListener('touchmove', onTouchMove, { passive: false });
    surface.addEventListener('touchend', onTouchEnd);
    surface.addEventListener('touchcancel', onTouchEnd);
    surface.addEventListener('keydown', onKeyDown);
    document.addEventListener('visibilitychange', onVis);

    emit(); // the resting truth: p=0 reported once so the engine paints frame zero

    var handle = {
      position: function () { return pos; },
      destroy: function () {
        if (rafId) { global.cancelAnimationFrame(rafId); rafId = 0; }
        surface.removeEventListener('wheel', onWheel);
        surface.removeEventListener('touchstart', onTouchStart);
        surface.removeEventListener('touchmove', onTouchMove);
        surface.removeEventListener('touchend', onTouchEnd);
        surface.removeEventListener('touchcancel', onTouchEnd);
        surface.removeEventListener('keydown', onKeyDown);
        document.removeEventListener('visibilitychange', onVis);
        if (io) io.disconnect();
        delete surface.__adJourney;
      }
    };
    surface.__adJourney = { handle: handle };
    return handle;
  }

  global.awardJourneyTouchMomentum = { init: init };
})(typeof window !== 'undefined' ? window : this);
