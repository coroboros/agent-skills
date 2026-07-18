/*
 * pinned-media-stepthrough enhancer — the scroll engine for the
 * pinned-media-stepthrough section form (general luxury award canon — the
 * playbook's own order, not corpus-source-verified against a specific winner
 * this run). NATIVE scroll: one rAF armed by scroll reads the section's
 * rect, maps overall progress onto the step line, and scrubs each step's
 * copy/detail-plate opacity as a PURE FUNCTION of scroll position —
 * reversible in both directions, no tween, no timeline. THE MEDIA IS NEVER
 * WRITTEN: the held object stays at full opacity for the entire pin — that
 * is the ruled distinction from pinned-demo-panels, whose stage content
 * cross-fades panel to panel. The pinned layers ride the form CSS's
 * live-mode regions; at the section's boundaries the enhancer swaps fixed
 * for the absolute parks (data-pms-park="start|end") so the layers scroll
 * in with the section and release after it — never overlaying the
 * neighbors. The active step publishes as data-ad-pms-step on the root (a
 * discrete write, only on change) so wayfinding can read the story's beat.
 *
 * Layering law: the enhancer toggles state ATTRIBUTES on the form root,
 * writes inline opacity/pointer-events on the step sub-elements, and
 * creates NO nodes; a step's inner DOM belongs to the builder and the
 * paired components.
 *
 * Usage:  awardPinnedMediaStepthrough.init(root, { selector, fade })
 *   root      Element|Document  scope (default document)
 *   selector  string  form roots (default '[data-ad-form="pinned-media-stepthrough"]')
 *   fade      number  cross-fade sharpness (default 1.6 — higher = tighter)
 * Returns { destroy() }. Idempotent per root. Reduced motion / no JS: the
 * form's rest state stands — the static stacked layout the gap orders,
 * media band then every caption legible.
 */
(function (global) {
  'use strict';

  var reduce = function () {
    return global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches;
  };

  function clamp01(v) { return v < 0 ? 0 : v > 1 ? 1 : v; }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-form="pinned-media-stepthrough"]';
    var fade = opts.fade || 1.6;

    // Reduced motion: the static stacked layout IS the section.
    if (reduce()) return { destroy: function () {} };

    if (root.__adPinnedMediaStepthrough) root.__adPinnedMediaStepthrough.destroy();

    var units = [];
    Array.prototype.forEach.call(root.querySelectorAll(selector), function (section) {
      var steps = Array.prototype.slice.call(section.querySelectorAll('[data-step]'));
      if (steps.length < 2) return; // one step has nothing to step through
      section.setAttribute('data-pms-live', '');
      section.setAttribute('data-pms-park', 'start');
      units.push({
        section: section,
        steps: steps.map(function (s) {
          return {
            el: s,
            copy: s.querySelector('[data-step-copy]'),
            figure: s.querySelector('[data-step-figure]')
          };
        }),
        active: -1,
        on: true
      });
    });
    if (!units.length) return { destroy: function () {} };

    function applyUnit(unit) {
      var rect = unit.section.getBoundingClientRect();
      var vh = global.innerHeight || 1;

      // boundary parks: fixed only while the section covers the viewport
      if (rect.top > 0) unit.section.setAttribute('data-pms-park', 'start');
      else if (rect.bottom < vh) unit.section.setAttribute('data-pms-park', 'end');
      else unit.section.removeAttribute('data-pms-park');

      var travel = Math.max(1, rect.height - vh);
      var P = clamp01(-rect.top / travel);
      var x = P * (unit.steps.length - 1);

      var nearest = Math.round(x);
      unit.steps.forEach(function (step, k) {
        var o = clamp01(1 - Math.abs(x - k) * fade);
        var oStr = o.toFixed(3);
        if (step.copy) {
          step.copy.style.opacity = oStr;
          step.copy.style.pointerEvents = k === nearest ? '' : 'none';
        }
        if (step.figure) {
          step.figure.style.opacity = oStr;
          step.figure.style.pointerEvents = k === nearest ? '' : 'none';
        }
        // the media slot is deliberately untouched — the held object never
        // fades; only the story steps over it
      });

      if (nearest !== unit.active) {
        unit.active = nearest;
        unit.section.setAttribute('data-ad-pms-step', String(nearest));
      }
    }

    var raf = 0;
    function frame() {
      raf = 0;
      if (document.hidden) return;
      units.forEach(function (u) { if (u.on) applyUnit(u); });
    }
    function arm() {
      if (!raf && !document.hidden) raf = global.requestAnimationFrame(frame);
    }

    var onScroll = arm;
    var onResize = arm;
    var onVisibility = function () { if (!document.hidden) arm(); };
    global.addEventListener('scroll', onScroll, { passive: true });
    global.addEventListener('resize', onResize);
    document.addEventListener('visibilitychange', onVisibility);

    var io = null;
    if ('IntersectionObserver' in global) {
      io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          units.forEach(function (u) {
            if (u.section !== e.target) return;
            u.on = e.isIntersecting;
            if (u.on) arm();
          });
        });
      });
      units.forEach(function (u) { io.observe(u.section); });
    }

    arm();

    var handle = {
      destroy: function () {
        if (raf) global.cancelAnimationFrame(raf);
        if (io) io.disconnect();
        global.removeEventListener('scroll', onScroll);
        global.removeEventListener('resize', onResize);
        document.removeEventListener('visibilitychange', onVisibility);
        units.forEach(function (u) {
          u.section.removeAttribute('data-pms-live');
          u.section.removeAttribute('data-pms-park');
          u.section.removeAttribute('data-ad-pms-step');
          u.steps.forEach(function (s) {
            if (s.copy) { s.copy.style.opacity = ''; s.copy.style.pointerEvents = ''; }
            if (s.figure) { s.figure.style.opacity = ''; s.figure.style.pointerEvents = ''; }
          });
        });
        if (root.__adPinnedMediaStepthrough === handle) delete root.__adPinnedMediaStepthrough;
      }
    };
    root.__adPinnedMediaStepthrough = handle;
    return handle;
  }

  global.awardPinnedMediaStepthrough = { init: init };
})(typeof window !== 'undefined' ? window : this);
