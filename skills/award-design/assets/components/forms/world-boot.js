/*
 * world-boot enhancer — the gated diegetic boot clock (winner: Bruno's
 * Portfolio; see forms/world-boot.css for the full alias ruling and seams).
 * The stage law is mirrored from in-engine-intro under this enhancer's own
 * guard, with ONE deliberate divergence per seam:
 *   THE GATE — nothing moves until the visitor's start gesture. The
 *   builder's engine mounts and reports ready(boot) — boot(p) maps one
 *   0→1 value onto the engine's own assembly choreography (objects rising
 *   from the ground, exposure, the diegetic material — the engine's
 *   business, never this file's). ready() un-hides the authored
 *   [data-slot="start"] control (an attribute write — the corner-boot
 *   law); its click — or handle.start() called inside gated-splash's
 *   onEnter — fires onStart(event) SYNCHRONOUSLY in the gesture, which is
 *   where the build unlocks its audio carrier (spatial-audio-world's
 *   unlock — the start gate doubles as the audio unlock, a hard browser
 *   constraint), then runs ONE decelerating clock over bootMs feeding
 *   boot(p) and the poster's inline opacity together. At p=1 the poster
 *   hides (inline write) and data-engine="live" routes the pointer to the
 *   world.
 *   prefers-reduced-motion — the CHOREOGRAPHY is decoration and is
 *   skipped, but the WORLD is interaction and still boots: the start
 *   gesture lands boot(1) once, the poster hides instantly, the stage
 *   goes live (the input-bridge precedent — interaction is never traded
 *   for calm; the assembly animation is). Save-Data / no WebGL / no mount
 *   → the poster fold stands whole, the start control stays hidden, and a
 *   dead script shows the same page (no-JS floor by authoring).
 * A hidden tab pauses the boot clock and resumes where it left. One boot,
 * ever; one stage per page.
 *
 * bootMs default 2400 is a DEFAULT, not a measured winner value (Bruno's
 * boot timings were never published); the ease is the decelerating cubic.
 *
 * Usage:  awardWorldBoot.init(root, opts)
 *   root      Element|Document  scope (default document)
 *   selector  string    the stage (default '[data-ad-form="world-boot"]')
 *   mount     function  mount(mountEl, ready, fail) — call ready(boot)
 *                       once the engine's first frame is rendered, or
 *                       fail() to stand down. Required.
 *   bootMs    ms        the assembly clock (default 2400)
 *   onStart   function  fired synchronously INSIDE the start gesture —
 *                       unlock the page's audio carrier here.
 * Returns { start(), destroy() }. start() is the gated-splash seam — call
 * it inside the overlay gate's onEnter. Idempotent per root. destroy()
 * cancels the clock and restores the poster; the engine's teardown is its
 * owner's job.
 */
(function (global) {
  'use strict';

  var reduce = function () {
    return !!(global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches);
  };
  var saveData = function () {
    var c = global.navigator && global.navigator.connection;
    return !!(c && c.saveData);
  };
  var webgl = function () {
    try {
      var probe = document.createElement('canvas');
      return !!(probe.getContext('webgl2') || probe.getContext('webgl'));
    } catch (e) { return false; }
  };

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-form="world-boot"]';
    var mount = typeof opts.mount === 'function' ? opts.mount : null;
    var bootMs = opts.bootMs != null ? +opts.bootMs : 2400;
    var onStart = typeof opts.onStart === 'function' ? opts.onStart : null;

    // the hard floors: the poster page stands whole on every one of them
    // (reduce is NOT here — a calm world still boots, without choreography)
    if (!mount || saveData() || !webgl()) {
      return { start: function () {}, destroy: function () {} };
    }

    if (root.__adWorldBoot) return root.__adWorldBoot;

    var section = root.querySelector(selector);
    if (!section) return { start: function () {}, destroy: function () {} };

    var mountEl = section.querySelector('[data-slot="mount"]');
    var poster = section.querySelector('[data-slot="poster"]');
    var startBtn = section.querySelector('[data-slot="start"]');
    if (!mountEl) return { start: function () {}, destroy: function () {} };

    var unit = {
      boot: null, ready: false, dead: false,
      armedStart: false, booting: false, live: false,
      rafId: 0, elapsed: 0, last: 0, pausedMid: false
    };

    function frame(now) {
      unit.rafId = 0;
      unit.elapsed += now - unit.last;
      unit.last = now;
      var t = Math.min(1, unit.elapsed / bootMs);
      var p = 1 - Math.pow(1 - t, 3);   // the decelerating assembly
      if (unit.boot) unit.boot(p);
      if (poster) poster.style.opacity = String(1 - p);
      if (t >= 1) {
        unit.booting = false;
        unit.live = true;
        if (poster) poster.style.visibility = 'hidden'; // inline write, never a stylesheet state
        section.setAttribute('data-engine', 'live');    // CSS routes the pointer
        return;
      }
      unit.rafId = global.requestAnimationFrame(frame);
    }

    function begin(e) {
      if (!unit.ready || unit.dead || unit.booting || unit.live) return;
      if (onStart) onStart(e || null); // synchronous — the gesture carries the audio unlock
      if (startBtn) startBtn.hidden = true; // the gate is spent
      if (reduce()) {
        // the world is interaction; the assembly animation is decoration
        if (unit.boot) unit.boot(1);
        if (poster) {
          poster.style.opacity = '0';
          poster.style.visibility = 'hidden';
        }
        unit.live = true;
        section.setAttribute('data-engine', 'live');
        return;
      }
      unit.booting = true;
      section.setAttribute('data-engine', 'booting');
      unit.elapsed = 0;
      unit.last = global.performance.now();
      unit.rafId = global.requestAnimationFrame(frame);
    }

    mount(mountEl, function ready(boot) {
      if (unit.ready || unit.dead) return;
      unit.ready = true;
      unit.boot = typeof boot === 'function' ? boot : null;
      // the gate appears only over a world that can actually start
      if (startBtn) startBtn.hidden = false;
    }, function fail() {
      unit.dead = true; // the poster floor stands — nothing to undo
    });

    var onClick = null;
    if (startBtn) {
      onClick = function (e) { begin(e); };
      startBtn.addEventListener('click', onClick);
    }

    // a hidden tab pauses the boot where it stands; visible resumes it
    var onVis = function () {
      if (document.hidden) {
        if (unit.rafId) {
          global.cancelAnimationFrame(unit.rafId);
          unit.rafId = 0;
          unit.pausedMid = unit.booting;
        }
      } else if (unit.pausedMid && unit.booting && !unit.rafId) {
        unit.pausedMid = false;
        unit.last = global.performance.now();
        unit.rafId = global.requestAnimationFrame(frame);
      }
    };
    document.addEventListener('visibilitychange', onVis);

    var handle = {
      start: function () { begin(null); }, // the gated-splash onEnter seam
      destroy: function () {
        document.removeEventListener('visibilitychange', onVis);
        if (onClick && startBtn) startBtn.removeEventListener('click', onClick);
        if (unit.rafId) { global.cancelAnimationFrame(unit.rafId); unit.rafId = 0; }
        unit.dead = true;
        unit.booting = false;
        section.removeAttribute('data-engine');
        if (poster) {
          poster.style.opacity = '';
          poster.style.visibility = '';
        }
        if (root.__adWorldBoot === handle) delete root.__adWorldBoot;
      }
    };
    root.__adWorldBoot = handle;
    return handle;
  }

  global.awardWorldBoot = { init: init };
})(typeof window !== 'undefined' ? window : this);
