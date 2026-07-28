/*
 * in-engine-intro enhancer — the arrival clock (winner: Igloo Inc; see
 * forms/in-engine-intro.css for the full seam ruling). The SAME mount gate
 * law as in-engine-hero / in-engine-hud-fold, mirrored under its own guard
 * (each enhancer holds one handle per root): past the floors — reduced
 * motion, Save-Data, a missing WebGL context — the builder's engine factory
 * takes the mount and reports readiness with an ARRIVE DRIVER, not a bare
 * signal: ready(arrive) where arrive(p) maps one 0→1 progress value onto
 * the engine's own arrival choreography (camera settle, exposure, assembly
 * — the engine's business, never this file's). The enhancer then runs ONE
 * decelerating clock over arriveMs, feeding arrive(p) and the poster's
 * inline opacity from the same value each frame — the plate is frame zero
 * of the choreography, so the scene resolves out of the photograph with no
 * cut and no loader boundary. At p=1 the poster hides (inline write) and
 * data-engine="live" lands; a hidden tab pauses the clock and resumes where
 * it left. On every refused floor — and with a dead script — the poster
 * fold stands whole and the HUD chrome is simply the authored DOM.
 *
 * arriveMs default 2000 is a DEFAULT, not a measured winner value (Igloo's
 * intro timings were never published); the ease is the decelerating cubic.
 *
 * Usage:  awardInEngineIntro.init(root, opts)
 *   root      Element|Document  scope (default document)
 *   selector  string    form roots (default '[data-ad-form="in-engine-intro"]')
 *   mount     function  mount(mountEl, ready, fail) — the builder mounts its
 *                       engine and calls ready(arrive) once its first frame
 *                       is rendered (arrive(p) optional but the point), or
 *                       fail() to stand down. Required.
 *   arriveMs  ms        the arrival clock (default 2000)
 * Returns { destroy() }. Idempotent per root. destroy() cancels the clock
 * and restores the poster; tearing the engine down is its owner's job.
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
    var selector = opts.selector || '[data-ad-form="in-engine-intro"]';
    var mount = typeof opts.mount === 'function' ? opts.mount : null;
    var arriveMs = opts.arriveMs != null ? +opts.arriveMs : 2000;

    // the floors: the poster fold stands, whole, on every one of them
    if (!mount || reduce() || saveData() || !webgl()) {
      return { destroy: function () {} };
    }

    if (root.__adInEngineIntro) return root.__adInEngineIntro;

    var units = [];
    var onVis = null;

    Array.prototype.forEach.call(root.querySelectorAll(selector), function (section) {
      var mountEl = section.querySelector('[data-slot="mount"]');
      var poster = section.querySelector('[data-slot="poster"]');
      if (!mountEl) return;
      var unit = {
        section: section, poster: poster,
        rafId: 0, elapsed: 0, last: 0, arrive: null,
        live: false, dead: false, arriving: false
      };
      units.push(unit);

      function frame(now) {
        unit.rafId = 0;
        unit.elapsed += now - unit.last;
        unit.last = now;
        var t = Math.min(1, unit.elapsed / arriveMs);
        var p = 1 - Math.pow(1 - t, 3);   // the decelerating arrival
        if (unit.arrive) unit.arrive(p);
        if (unit.poster) unit.poster.style.opacity = String(1 - p);
        if (t >= 1) {
          unit.arriving = false;
          unit.live = true;
          if (unit.poster) unit.poster.style.visibility = 'hidden'; // inline write, never a stylesheet state
          unit.section.setAttribute('data-engine', 'live');         // CSS routes the pointer
          return;
        }
        unit.rafId = global.requestAnimationFrame(frame);
      }

      mount(mountEl, function ready(arrive) {
        if (unit.live || unit.dead || unit.arriving) return; // one arrival, ever
        unit.arriving = true;
        unit.arrive = typeof arrive === 'function' ? arrive : null;
        unit.section.setAttribute('data-engine', 'arriving');
        unit.last = global.performance.now();
        unit.rafId = global.requestAnimationFrame(frame);
      }, function fail() {
        unit.dead = true; // the poster floor stands — nothing to undo
      });

      unit.resume = function () {
        if (unit.arriving && !unit.rafId) {
          unit.last = global.performance.now();
          unit.rafId = global.requestAnimationFrame(frame);
        }
      };
      unit.pause = function () {
        if (unit.rafId) { global.cancelAnimationFrame(unit.rafId); unit.rafId = 0; }
      };
    });

    // a hidden tab pauses the arrival where it stands; visible resumes it
    onVis = function () {
      units.forEach(function (u) {
        if (document.hidden) u.pause(); else u.resume();
      });
    };
    document.addEventListener('visibilitychange', onVis);

    var handle = {
      destroy: function () {
        document.removeEventListener('visibilitychange', onVis);
        units.forEach(function (u) {
          u.pause();
          u.dead = true;
          u.arriving = false;
          u.section.removeAttribute('data-engine');
          if (u.poster) {
            u.poster.style.opacity = '';
            u.poster.style.visibility = '';
          }
        });
        if (root.__adInEngineIntro === handle) delete root.__adInEngineIntro;
      }
    };
    root.__adInEngineIntro = handle;
    return handle;
  }

  global.awardInEngineIntro = { init: init };
})(typeof window !== 'undefined' ? window : this);
