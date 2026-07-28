/*
 * scroll-camera-dive — the immersive archetype's true-3D spine (winners: Oryzo
 * AI by Lusion — a camera through real Z-depth around and into one object;
 * Explore Primland — an aerial camera over terrain; ERA by Vide Infra — a
 * scroll-zoom into architectural detail). Scroll PROGRESS scrubs a real camera
 * PATH — position + lookAt (+ optional FOV) keyframes, linearly interpolated,
 * inertially eased so the subject keeps moving between scroll ticks, reversible,
 * driven entirely inside the rAF loop (no per-frame layout write). An optional
 * fade hand-off dissolves the pinned frame over the last of the travel.
 *
 * The library's dolly-zoom is the 2.5D DOM cousin — a pinned media SCALED toward
 * a focal point. This is the true-3D rig: it drives a camera, not a transform.
 * Bring your own engine — hand it a Three.js-compatible camera, an engine-
 * agnostic onUpdate(state), or both. It NEVER imports Three; the caller owns it.
 *
 * Structure (the component wraps + pins for you, like dolly-zoom's track):
 *   <section data-ad-camera-dive data-ad-dive-travel="2">
 *     <canvas> … your 3D viewport … </canvas>   the children become a sticky frame
 *   </section>
 * data-ad-dive-travel — scroll distance in viewport heights (default 2).
 *
 * Usage:
 *   awardScrollCameraDive.init(section, {
 *     keyframes: [{ at: 0, position: [0,0,6], lookAt: [0,0,0], fov: 60 }, …],
 *     camera,          // optional Three.js camera: position.set + lookAt + fov
 *     onUpdate,        // optional (state) => void — the engine-agnostic hook
 *     travel: 2, ease: 0.1, fadeLast: 0
 *   })
 * At least one of camera / onUpdate is required (else it warns and no-ops).
 * Returns { destroy() }. Idempotent per section. No-JS: the viewport is a plain
 * block, no pin. Reduced-motion: the FINAL keyframe is applied once — a static
 * composed frame, no rAF, no pin.
 *
 * Perf: transform/opacity only on the DOM (the frame); all camera math in one
 * rAF gated by IntersectionObserver on the section and document visibility.
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-scroll-camera-dive-css';
  var reduce = function () {
    return global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches;
  };
  var clamp = function (v, lo, hi) { return v < lo ? lo : v > hi ? hi : v; };
  var lerp = function (a, b, t) { return a + (b - a) * t; };
  var lerp3 = function (a, b, t) {
    return [lerp(a[0], b[0], t), lerp(a[1], b[1], t), lerp(a[2], b[2], t)];
  };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      '[data-ad-camera-dive]{position:relative;display:block;}' +
      '.ad-camera-dive__frame{position:sticky;top:0;height:100dvh;' +
      'overflow:hidden;will-change:transform,opacity;}' +
      '.ad-camera-dive__frame>canvas,.ad-camera-dive__frame>img,' +
      '.ad-camera-dive__frame>video{display:block;width:100%;height:100%;}';
    document.head.appendChild(s);
  }

  // Linear camera path: lerp position + lookAt between the bracketing keyframes;
  // lerp fov only where both ends define it — carry the defined side otherwise,
  // and leave fov undefined (camera untouched) where neither does.
  function pathState(kfs, p) {
    var a = kfs[0], b = kfs[kfs.length - 1], t = 0;
    if (p <= a.at) { b = a; }
    else if (p >= b.at) { a = b; }
    else {
      for (var i = 0; i < kfs.length - 1; i++) {
        if (p >= kfs[i].at && p <= kfs[i + 1].at) {
          a = kfs[i]; b = kfs[i + 1];
          var span = b.at - a.at;
          t = span > 0 ? (p - a.at) / span : 0;
          break;
        }
      }
    }
    var fov = (a.fov != null && b.fov != null) ? lerp(a.fov, b.fov, t)
            : (a.fov != null ? a.fov : b.fov);
    return {
      progress: p,
      position: lerp3(a.position, b.position, t),
      lookAt: lerp3(a.lookAt, b.lookAt, t),
      fov: fov
    };
  }

  function init(root, opts) {
    opts = opts || {};
    var section = (root && root.nodeType === 1 && root.hasAttribute('data-ad-camera-dive'))
      ? root
      : (root || document).querySelector('[data-ad-camera-dive]');
    if (!section) return { destroy: function () {} };
    if (section.__adCameraDive) return section.__adCameraDive;

    var camera = opts.camera || null;
    var onUpdate = typeof opts.onUpdate === 'function' ? opts.onUpdate : null;
    if (!camera && !onUpdate) {
      if (global.console) global.console.warn(
        'awardScrollCameraDive: opts.camera or opts.onUpdate is required — no-op.');
      return { destroy: function () {} };
    }

    var kfs = (opts.keyframes || []).slice().sort(function (x, y) { return x.at - y.at; });
    if (!kfs.length) {
      if (global.console) global.console.warn(
        'awardScrollCameraDive: opts.keyframes is required — no-op.');
      return { destroy: function () {} };
    }

    var travel = opts.travel != null ? opts.travel
      : (parseFloat(section.getAttribute('data-ad-dive-travel')) || 2);
    var ease = opts.ease != null ? opts.ease : 0.1;
    var fadeLast = opts.fadeLast != null ? opts.fadeLast : 0;

    injectCss();

    var frame = null;
    var lastFov = null;
    function apply(p) {
      var st = pathState(kfs, p);
      if (camera) {
        camera.position.set(st.position[0], st.position[1], st.position[2]);
        camera.lookAt(st.lookAt[0], st.lookAt[1], st.lookAt[2]);
        // updateProjectionMatrix is the expensive one — call it only on real fov change.
        if (st.fov != null && st.fov !== lastFov) {
          camera.fov = st.fov;
          if (camera.updateProjectionMatrix) camera.updateProjectionMatrix();
          lastFov = st.fov;
        }
      }
      if (onUpdate) onUpdate(st);
      if (fadeLast > 0 && frame) {
        var edge = 1 - fadeLast;
        frame.style.opacity = p > edge ? clamp(1 - (p - edge) / fadeLast, 0, 1).toFixed(4) : '';
      }
    }

    // Reduced-motion: the final keyframe, composed once. No wrap, no pin, no loop.
    if (reduce()) {
      apply(1);
      var rmHandle = {
        destroy: function () {
          section.__adCameraDive = null;
          var s = document.getElementById(CSS_ID);
          if (s) s.parentNode.removeChild(s);
        }
      };
      section.__adCameraDive = rmHandle;
      return rmHandle;
    }

    // Wrap: the section's existing children become the pinned sticky frame, the
    // section itself becomes the tall scroll track.
    frame = document.createElement('div');
    frame.className = 'ad-camera-dive__frame';
    while (section.firstChild) frame.appendChild(section.firstChild);
    section.appendChild(frame);
    section.style.minHeight = ((travel + 1) * 100) + 'vh';

    var vh = function () { return global.innerHeight || document.documentElement.clientHeight; };
    // Travel 0..1: pinned from the section top to its bottom-minus-viewport.
    function targetProgress() {
      var r = section.getBoundingClientRect();
      return clamp(-r.top / Math.max(1, r.height - vh()), 0, 1);
    }

    var cur = targetProgress();
    var rafId = 0, inView = false;
    // Inertial scrub: cur chases the scroll-derived target so the subject keeps
    // moving between ticks; the loop self-terminates once it has settled.
    function frameLoop() {
      rafId = 0;
      if (!inView) return;
      var target = targetProgress();
      cur += (target - cur) * ease;
      if (Math.abs(target - cur) < 0.0002) cur = target;
      apply(cur);
      if (cur !== target && !document.hidden) rafId = global.requestAnimationFrame(frameLoop);
    }
    function kick() {
      if (!rafId && !document.hidden) rafId = global.requestAnimationFrame(frameLoop);
    }

    apply(cur); // first composed frame at the current scroll position

    var io = null, onScroll = null, onVis = null;
    if ('IntersectionObserver' in global) {
      io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          inView = e.isIntersecting;
          if (inView) kick();
        });
      }, { threshold: 0 });
      io.observe(section);
    } else {
      inView = true;
    }
    onScroll = function () { if (!document.hidden && inView) kick(); };
    global.addEventListener('scroll', onScroll, { passive: true });
    global.addEventListener('resize', onScroll, { passive: true });
    onVis = function () { if (!document.hidden && inView) kick(); };
    document.addEventListener('visibilitychange', onVis);
    kick();

    var handle = {
      destroy: function () {
        if (rafId) global.cancelAnimationFrame(rafId);
        if (io) io.disconnect();
        if (onScroll) {
          global.removeEventListener('scroll', onScroll);
          global.removeEventListener('resize', onScroll);
        }
        if (onVis) document.removeEventListener('visibilitychange', onVis);
        // Unwrap: return the frame's children to the section, drop the frame.
        while (frame.firstChild) section.insertBefore(frame.firstChild, frame);
        if (frame.parentNode) section.removeChild(frame);
        section.style.minHeight = '';
        section.__adCameraDive = null;
        var s = document.getElementById(CSS_ID);
        if (s) s.parentNode.removeChild(s);
      }
    };
    section.__adCameraDive = handle;
    return handle;
  }

  global.awardScrollCameraDive = { init: init };
})(typeof window !== 'undefined' ? window : this);
