/*
 * continuous-idle-carry — the brutalist never-silent carry (winners: Eloy
 * Benoffi, maximalist register; Naked City Films, restraint register —
 * 'movement without chaos'; FlowFest 2025, loud register, boundary-adjacent,
 * params reference-carried). A décor/idle channel run continuously
 * hero→footer so the page is never a bank of fire-once reveals with dead
 * silence between. Amplitude is PER-BRIEF — the component ships three
 * opt-in channels and the build picks its register, never all three by
 * default:
 *   [data-ad-carry-marquee]   a repeating band drifting on one rAF clock.
 *                             Default couples speed AND skew to scroll
 *                             velocity — the documented Osmo winner variant:
 *                             skew target = velocity / -300, clamped, easing
 *                             back to 0 at rest — and survives touch as a
 *                             scroll-driven channel. ="constant" is the tamer
 *                             fixed px/s fallback.
 *   [data-ad-carry-idle]      ONE in-character idle element (mascot, face,
 *                             mark) that leans toward the cursor via a lerped
 *                             translate on fine pointers (the quickTo
 *                             pattern) and falls back to a time-driven idle
 *                             bob on touch.
 *   [data-ad-carry-drift]     the restraint register: sections kept subtly
 *                             moving by a single perpetual loop — a slow
 *                             per-element sine drift at ambient amplitude.
 * One shared rAF drives every channel (the Naked City 'single perpetual
 * loop'); it pauses on visibilitychange and each element stands down
 * off-screen via IntersectionObserver. Distinct from ambient-idle
 * (glow/float/shimmer décor) — this channel renders the archetype's own
 * metaphor in-character.
 *
 * Usage:  awardContinuousIdleCarry.init(root, opts)
 *   root       Element|Document  scope (default document)
 *   speed      px/s marquee base drift (default 80)
 *   skewMax    deg velocity-skew clamp (default 6)
 *   idleAmp    px idle-element lean radius (default 28)
 *   driftAmp   px restraint drift amplitude (default 4)
 * Returns { destroy(), pause(), resume() } — pause/resume is the hook a
 * build wires to its WCAG 2.2.2 pause control (any idle channel running
 * past five seconds carries the pause/stop path). Idempotent per root.
 * Reduced motion → no-op: every channel's rest pose is the authored DOM.
 *
 * Tokens: none — the carry moves the build's own elements; color and type
 * stay the author's.
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-continuous-idle-carry-css';
  var SKEW_DIVISOR = -300; // the Osmo winner variant: skew = velocity / -300

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
      '[data-ad-carry-marquee].ad-carry{overflow:hidden;white-space:nowrap;}' +
      '.ad-carry__track{display:inline-flex;white-space:nowrap;will-change:transform;}' +
      '.ad-carry__copy{display:inline-block;flex:none;white-space:nowrap;}' +
      '[data-ad-carry-idle].ad-carry,[data-ad-carry-drift].ad-carry{will-change:transform;}' +
      '@media (prefers-reduced-motion:reduce){' +
      '.ad-carry__track,[data-ad-carry-idle].ad-carry,[data-ad-carry-drift].ad-carry{' +
      'transform:none;will-change:auto;}}';
    document.head.appendChild(s);
  }

  function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }
  function lerp(a, b, t) { return a + (b - a) * t; }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    // Reduced motion → the carry never runs; the authored DOM is the rest pose.
    if (reduce()) return { destroy: function () {}, pause: function () {}, resume: function () {} };

    var speed = opts.speed != null ? opts.speed : 80;
    var skewMax = opts.skewMax != null ? opts.skewMax : 6;
    var idleAmp = opts.idleAmp != null ? opts.idleAmp : 28;
    var driftAmp = opts.driftAmp != null ? opts.driftAmp : 4;

    var host = root === document ? document.documentElement : root;
    if (host.__adCarry) host.__adCarry.destroy();

    injectCss();

    var fine = finePointer();
    var units = []; // every animated element, with its per-frame update

    // ---- marquee bands: authored content duplicated into a drifting track --
    var marquees = Array.prototype.slice.call(root.querySelectorAll('[data-ad-carry-marquee]'));
    marquees.forEach(function (band) {
      band.classList.add('ad-carry');
      var track = document.createElement('div');
      track.className = 'ad-carry__track';
      var copy = document.createElement('div');
      copy.className = 'ad-carry__copy';
      while (band.firstChild) copy.appendChild(band.firstChild);
      track.appendChild(copy);
      band.appendChild(track);
      var copyW = copy.getBoundingClientRect().width || 1;
      // enough copies that the wrap point is never on screen
      var need = Math.max(2, Math.ceil((band.clientWidth * 2) / copyW) + 1);
      for (var i = 1; i < need; i++) {
        var dup = copy.cloneNode(true);
        dup.setAttribute('aria-hidden', 'true');
        track.appendChild(dup);
      }
      units.push({
        kind: 'marquee',
        el: band, track: track,
        constant: band.getAttribute('data-ad-carry-marquee') === 'constant',
        copyW: copyW, x: 0, skew: 0, mult: 1,
        visible: true
      });
    });

    // ---- idle element: cursor-lerped on fine pointers, time bob on touch ---
    var idles = Array.prototype.slice.call(root.querySelectorAll('[data-ad-carry-idle]'));
    idles.forEach(function (el) {
      el.classList.add('ad-carry');
      units.push({ kind: 'idle', el: el, x: 0, y: 0, tx: 0, ty: 0, seen: false, visible: true });
    });

    // ---- restraint drift: the single perpetual loop, per-element phase -----
    var drifts = Array.prototype.slice.call(root.querySelectorAll('[data-ad-carry-drift]'));
    drifts.forEach(function (el, i) {
      el.classList.add('ad-carry');
      units.push({ kind: 'drift', el: el, phase: i * 1.7, visible: true });
    });

    if (!units.length) return { destroy: function () {}, pause: function () {}, resume: function () {} };

    // one IO stands every unit down off-screen — off-screen costs zero
    var io = null;
    if ('IntersectionObserver' in global) {
      var byEl = new Map();
      units.forEach(function (u) { byEl.set(u.el, u); });
      io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          var u = byEl.get(e.target);
          if (u) u.visible = e.isIntersecting;
        });
      }, { rootMargin: '10% 0px' });
      units.forEach(function (u) { io.observe(u.el); });
    }

    // pointer feed for the idle channel (fine pointers only)
    var px = 0, py = 0;
    var onPointer = null;
    if (fine && idles.length) {
      onPointer = function (e) {
        px = e.clientX; py = e.clientY;
        units.forEach(function (u) { if (u.kind === 'idle') u.seen = true; });
      };
      global.addEventListener('pointermove', onPointer, { passive: true });
    }

    // scroll velocity in px/s, smoothed — feeds marquee speed and skew
    var lastY = global.scrollY || 0;
    var vel = 0;

    var rafId = 0;
    var paused = false;
    var lastT = 0;

    function frame(now) {
      rafId = global.requestAnimationFrame(frame);
      if (!lastT) { lastT = now; return; }
      var dt = Math.min(0.05, (now - lastT) / 1000);
      lastT = now;

      var y = global.scrollY || 0;
      var raw = (y - lastY) / (dt || 0.016);
      lastY = y;
      vel = lerp(vel, raw, 0.12); // smooth the per-frame noise

      var t = now / 1000;
      units.forEach(function (u) {
        if (!u.visible) return;
        if (u.kind === 'marquee') {
          if (u.constant) {
            u.x -= speed * dt;
          } else {
            // speed AND skew couple to scroll velocity; both ease back at rest
            var multTarget = 1 + Math.min(Math.abs(vel) / 600, 3);
            u.mult = lerp(u.mult, multTarget, 0.08);
            var skewTarget = clamp(vel / SKEW_DIVISOR, -skewMax, skewMax);
            u.skew = lerp(u.skew, skewTarget, 0.08); // ease back to 0
            u.x -= speed * u.mult * dt;
          }
          if (u.x <= -u.copyW) u.x += u.copyW; // modular wrap — seamless band
          u.track.style.transform =
            'translate3d(' + u.x.toFixed(2) + 'px,0,0) skewX(' + u.skew.toFixed(2) + 'deg)';
        } else if (u.kind === 'idle') {
          if (fine && u.seen) {
            // lean toward the cursor — the lerped quickTo pattern
            var r = u.el.getBoundingClientRect();
            var cx = r.left + r.width / 2, cy = r.top + r.height / 2;
            var dx = px - cx, dy = py - cy;
            var d = Math.sqrt(dx * dx + dy * dy) || 1;
            var reach = Math.min(d, idleAmp);
            u.tx = (dx / d) * reach; u.ty = (dy / d) * reach;
          } else {
            // touch (or an untouched pointer): the time-driven idle bob
            u.tx = Math.sin(t * 0.9) * idleAmp * 0.25;
            u.ty = Math.sin(t * 1.3) * idleAmp * 0.35;
          }
          u.x = lerp(u.x, u.tx, 0.08);
          u.y = lerp(u.y, u.ty, 0.08);
          u.el.style.transform = 'translate3d(' + u.x.toFixed(2) + 'px,' + u.y.toFixed(2) + 'px,0)';
        } else {
          // drift — movement without chaos: slow sine at ambient amplitude
          var gx = Math.sin(t * 0.35 + u.phase) * driftAmp;
          var gy = Math.sin(t * 0.22 + u.phase * 1.3) * driftAmp;
          u.el.style.transform = 'translate3d(' + gx.toFixed(2) + 'px,' + gy.toFixed(2) + 'px,0)';
        }
      });
    }

    function start() {
      if (!rafId && !paused && !document.hidden) {
        lastT = 0;
        rafId = global.requestAnimationFrame(frame);
      }
    }
    function stop() {
      if (rafId) { global.cancelAnimationFrame(rafId); rafId = 0; }
    }

    var onVisibility = function () { if (document.hidden) stop(); else start(); };
    document.addEventListener('visibilitychange', onVisibility);
    start();

    var handle = {
      pause: function () { paused = true; stop(); },
      resume: function () { paused = false; start(); },
      destroy: function () {
        stop();
        document.removeEventListener('visibilitychange', onVisibility);
        if (onPointer) global.removeEventListener('pointermove', onPointer);
        if (io) io.disconnect();
        units.forEach(function (u) {
          u.el.style.transform = '';
          u.el.classList.remove('ad-carry');
          if (u.kind === 'marquee') {
            // unwrap: the first copy holds the authored nodes
            var first = u.track.firstChild;
            while (first && first.firstChild) u.el.insertBefore(first.firstChild, u.track);
            u.el.removeChild(u.track);
          }
        });
        delete host.__adCarry;
        var s = document.getElementById(CSS_ID);
        if (s && s.parentNode) s.parentNode.removeChild(s);
      }
    };
    host.__adCarry = handle;
    return handle;
  }

  global.awardContinuousIdleCarry = { init: init };
})(typeof window !== 'undefined' ? window : this);
