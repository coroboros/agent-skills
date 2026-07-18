/*
 * place-tour enhancer — publishes the walked station (winner: Son Daven —
 * SOTD Jun 5 2026; the place-tour proof beats — see forms/place-tour.css
 * for the full contract). The station whose centre sits nearest the
 * viewport centre publishes as data-ad-place-station on the form root and
 * data-ad-place-active on that station — a pure function of scroll, so the
 * walk is reversible and re-publishes on every pass. Zero-flip: attributes
 * write only on change. The builder pairs against these hooks (fire a
 * counter, lift a plate); the enhancer itself toggles attributes ONLY —
 * never restructures a slot's inner DOM, never injects style.
 *
 * Usage:  awardPlaceTour.init(root, { selector })
 *   root      Element|Document  scope (default document)
 *   selector  string  form roots (default '[data-ad-form="place-tour"]')
 * Returns { destroy() }. Idempotent per root. destroy() removes the
 * published attributes and listeners.
 *
 * Reduced motion / no-JS: the static itinerary stands fully legible (the
 * form CSS owns the layout); under reduce the enhancer is a no-op — the
 * publish exists to drive motion pairings, and none may fire.
 * Perf: rects cached on init/resize/load, only scrollY read per frame; one
 * rAF woken by scroll, parked when settled.
 */
(function (global) {
  'use strict';

  var reduce = function () {
    return !!(global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches);
  };

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-form="place-tour"]';

    if (reduce()) return { destroy: function () {} };

    var forms = Array.prototype.filter.call(
      root.querySelectorAll(selector),
      function (el) { return !el.__adPlaceTour; }
    );
    if (!forms.length) return { destroy: function () {} };

    var units = forms.map(function (form) {
      var u = {
        form: form,
        stations: Array.prototype.slice.call(form.querySelectorAll('[data-station]')),
        centers: [],
        active: -1,
        raf: 0
      };
      form.__adPlaceTour = u;
      return u;
    });

    function measure() {
      var sy = global.pageYOffset || 0;
      units.forEach(function (u) {
        u.centers = u.stations.map(function (el) {
          var r = el.getBoundingClientRect();
          return r.top + sy + r.height / 2;
        });
      });
    }

    function frame() {
      units.forEach(function (u) {
        u.raf = 0;
        if (!u.stations.length) return;
        var vc = (global.pageYOffset || 0) +
          (global.innerHeight || document.documentElement.clientHeight) / 2;
        var nearest = 0, best = Infinity;
        for (var i = 0; i < u.centers.length; i++) {
          var d = Math.abs(u.centers[i] - vc);
          if (d < best) { best = d; nearest = i; }
        }
        if (nearest !== u.active) {
          if (u.active !== -1) u.stations[u.active].removeAttribute('data-ad-place-active');
          u.active = nearest;
          u.stations[nearest].setAttribute('data-ad-place-active', '');
          u.form.setAttribute('data-ad-place-station', String(nearest));
        }
      });
    }

    function kick() {
      units.forEach(function (u) {
        if (!u.raf) u.raf = global.requestAnimationFrame(frame);
      });
    }

    var onScroll = function () { if (!document.hidden) kick(); };
    var onResize = function () { measure(); kick(); };

    measure();
    kick();
    global.addEventListener('scroll', onScroll, { passive: true });
    global.addEventListener('resize', onResize, { passive: true });
    global.addEventListener('load', onResize);

    return {
      destroy: function () {
        global.removeEventListener('scroll', onScroll);
        global.removeEventListener('resize', onResize);
        global.removeEventListener('load', onResize);
        units.forEach(function (u) {
          if (u.raf) global.cancelAnimationFrame(u.raf);
          u.form.removeAttribute('data-ad-place-station');
          u.stations.forEach(function (el) { el.removeAttribute('data-ad-place-active'); });
          delete u.form.__adPlaceTour;
        });
        units = [];
      }
    };
  }

  global.awardPlaceTour = { init: init };
})(typeof window !== 'undefined' ? window : this);
