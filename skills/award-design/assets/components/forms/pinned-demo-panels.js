/*
 * pinned-demo-panels enhancer — the scroll engine for the pinned-demo-panels
 * section form (winner: Anime.js v4). NATIVE scroll only (the tier's verdict —
 * no smoother): one rAF armed by scroll reads the section's rect, maps overall
 * progress onto the panel line, and scrubs each panel's copy/demo opacity as a
 * PURE FUNCTION of scroll position — reversible by construction, no tween, no
 * timeline. The pinned layers ride the form CSS's live-mode regions; at the
 * section's boundaries the enhancer swaps fixed for the absolute parks
 * (data-pdp-park="start|end") so the layer scrolls in with the section and
 * scrolls away after it — never overlaying the neighbors. The active panel's
 * data-panel-accent publishes page-wide as --ad-pdp-accent on <html> (the
 * --hex-current analog; a discrete swap, consumable by the build's own CSS).
 * Only the ACTIVE panel's demo keeps pointer-events, so a mounted operable
 * demo (live-demo-tile) stays drivable and the peak replays.
 *
 * Layering law: the enhancer toggles state ATTRIBUTES on the form root (the
 * forms namespace styles through [data-ad-form], never role classes), writes
 * inline opacity/pointer-events on the slot sub-elements, and creates NO
 * nodes; a panel's inner DOM belongs to the builder and the paired components.
 *
 * Usage:  awardPinnedDemoPanels.init(root, { selector, fade })
 *   root      Element|Document  scope (default document)
 *   selector  string  form roots (default '[data-ad-form="pinned-demo-panels"]')
 *   fade      number  cross-fade sharpness (default 1.6 — higher = tighter)
 * Returns { destroy() }. Idempotent per root. Reduced motion / no JS: the
 * form's rest state stands — stacked static panels, every band legible.
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
    var selector = opts.selector || '[data-ad-form="pinned-demo-panels"]';
    var fade = opts.fade || 1.6;

    // Reduced motion: stacked static panels — the rest state IS the section.
    if (reduce()) return { destroy: function () {} };

    if (root.__adPinnedDemoPanels) root.__adPinnedDemoPanels.destroy();

    var units = [];
    Array.prototype.forEach.call(root.querySelectorAll(selector), function (section) {
      var panels = Array.prototype.slice.call(section.querySelectorAll('[data-panel]'));
      if (panels.length < 2) return; // one panel has nothing to cross-fade
      section.setAttribute('data-pdp-live', '');
      section.setAttribute('data-pdp-park', 'start');
      units.push({
        section: section,
        panels: panels.map(function (p) {
          return {
            el: p,
            copy: p.querySelector('[data-panel-copy]'),
            demo: p.querySelector('[data-panel-demo]'),
            accent: p.getAttribute('data-panel-accent')
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
      if (rect.top > 0) unit.section.setAttribute('data-pdp-park', 'start');
      else if (rect.bottom < vh) unit.section.setAttribute('data-pdp-park', 'end');
      else unit.section.removeAttribute('data-pdp-park');

      var travel = Math.max(1, rect.height - vh);
      var P = clamp01(-rect.top / travel);
      var x = P * (unit.panels.length - 1);

      var nearest = Math.round(x);
      unit.panels.forEach(function (panel, k) {
        var o = clamp01(1 - Math.abs(x - k) * fade);
        var oStr = o.toFixed(3);
        if (panel.copy) {
          panel.copy.style.opacity = oStr;
          panel.copy.style.pointerEvents = k === nearest ? '' : 'none';
        }
        if (panel.demo) {
          panel.demo.style.opacity = oStr;
          // only the active demo stays operable — the peak keeps replaying
          panel.demo.style.pointerEvents = k === nearest ? '' : 'none';
        }
      });

      if (nearest !== unit.active) {
        unit.active = nearest;
        var accent = unit.panels[nearest].accent;
        if (accent) document.documentElement.style.setProperty('--ad-pdp-accent', accent);
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
          u.section.removeAttribute('data-pdp-live');
          u.section.removeAttribute('data-pdp-park');
          u.panels.forEach(function (p) {
            if (p.copy) { p.copy.style.opacity = ''; p.copy.style.pointerEvents = ''; }
            if (p.demo) { p.demo.style.opacity = ''; p.demo.style.pointerEvents = ''; }
          });
        });
        document.documentElement.style.removeProperty('--ad-pdp-accent');
        if (root.__adPinnedDemoPanels === handle) delete root.__adPinnedDemoPanels;
      }
    };
    root.__adPinnedDemoPanels = handle;
    return handle;
  }

  global.awardPinnedDemoPanels = { init: init };
})(typeof window !== 'undefined' ? window : this);
