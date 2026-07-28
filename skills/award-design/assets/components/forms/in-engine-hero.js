/*
 * in-engine-hero enhancer — the mount gate for the in-engine-hero section
 * form (winners: Depo Luxe, Lusion v3). The form's CSS owns the stage; this
 * enhancer owns WHEN an engine may take it: it probes the floors — reduced
 * motion, Save-Data, a missing WebGL context — and only past all three hands
 * the mount slot to the builder's engine factory. The engine reports its
 * first ready frame; the enhancer then fades the poster out (an inline WAAPI
 * opacity — the one motion here is enhancer-driven, the stylesheet ships
 * none) and sets data-engine="live" on the root, whose CSS keeps the poster
 * hidden and grants the mount the pointer. Poster-first LCP by construction:
 * the plate paints from first paint and nothing waits on the engine; on
 * every refused floor the poster simply IS the hero — never a blank canvas,
 * never a spinner.
 *
 * Layering law: the enhancer toggles the state ATTRIBUTE on the form root,
 * animates the poster slot element only, and creates NO nodes — the mount's
 * inner DOM belongs to the builder's engine.
 *
 * Usage:  awardInEngineHero.init(root, opts)
 *   root      Element|Document  scope (default document)
 *   selector  string    form roots (default '[data-ad-form="in-engine-hero"]')
 *   mount     function  mount(mountEl, ready, fail) — the builder mounts its
 *                       engine into mountEl and calls ready() on the first
 *                       rendered frame, or fail() to stand down. Required —
 *                       without it the enhancer is a no-op (poster hero).
 * Returns { destroy() }. Idempotent per root. destroy() cancels the fade,
 * clears the live state, and restores the poster; tearing the engine itself
 * down is its owner's job.
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

  function styles() {
    var cs = getComputedStyle(document.documentElement);
    function v(name, fallback) {
      return (cs.getPropertyValue(name) || '').trim() || fallback;
    }
    return {
      durReveal: parseFloat(v('--ad-dur-reveal', '800ms')) || 800,
      ease: v('--ad-ease-signature', 'cubic-bezier(.16,1,.3,1)')
    };
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-form="in-engine-hero"]';
    var mount = typeof opts.mount === 'function' ? opts.mount : null;

    // The floors: no engine under reduce or Save-Data, none without WebGL —
    // the poster hero stands, whole, on every one of them.
    if (!mount || reduce() || saveData() || !webgl()) {
      return { destroy: function () {} };
    }

    if (root.__adInEngineHero) return root.__adInEngineHero;

    var units = [];
    Array.prototype.forEach.call(root.querySelectorAll(selector), function (section) {
      var mountEl = section.querySelector('[data-slot="mount"]');
      var poster = section.querySelector('[data-slot="poster"]');
      if (!mountEl) return;
      var unit = { section: section, poster: poster, anim: null, live: false, dead: false };
      units.push(unit);
      mount(mountEl, function ready() {
        if (unit.live || unit.dead) return; // one hand-off, ever
        unit.live = true;
        function land() {
          unit.anim = null;
          section.setAttribute('data-engine', 'live'); // CSS routes the pointer
          // the hide is a JS write, never a stylesheet state (no-JS floor)
          if (poster) poster.style.visibility = 'hidden';
        }
        if (poster && poster.animate) {
          unit.anim = poster.animate(
            [{ opacity: 1 }, { opacity: 0 }],
            { duration: styles().durReveal, easing: styles().ease, fill: 'forwards' }
          );
          unit.anim.onfinish = land;
        } else {
          land();
        }
      }, function fail() {
        unit.dead = true; // the poster floor stands — nothing to undo
      });
    });

    var handle = {
      destroy: function () {
        units.forEach(function (u) {
          if (u.anim) { u.anim.cancel(); u.anim = null; }
          u.dead = true;
          u.section.removeAttribute('data-engine');
          if (u.poster) u.poster.style.visibility = '';
        });
        if (root.__adInEngineHero === handle) delete root.__adInEngineHero;
      }
    };
    root.__adInEngineHero = handle;
    return handle;
  }

  global.awardInEngineHero = { init: init };
})(typeof window !== 'undefined' ? window : this);
