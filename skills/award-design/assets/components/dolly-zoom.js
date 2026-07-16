/*
 * dolly-zoom — the scroll dive into a focal point (winner class: the cosmic
 * push-in — scroll down and the camera plunges INTO the moon/plate/product;
 * Apple-lineage pinned scrub, MERIDIAN v2 validation).
 * A pinned full-bleed media scales toward a targeted origin as a tall track
 * scrolls behind it — reversible and scroll-linked (décor-channel legal: the
 * media is fully visible at every point of the travel). Optionally the frame
 * fades near the end of the dive to hand off into the next section.
 *
 * Structure:
 *   <div data-ad-dolly-track style="height:300vh">      the scroll distance
 *     <div data-ad-dolly data-ad-dolly-origin="62% 38%" data-ad-dolly-zoom="5">
 *       <img src="plate.avif" alt="…">                   or <video>
 *     </div>
 *   </div>
 * data-ad-dolly-origin — the focal point the dive targets (default 50% 50%)
 * data-ad-dolly-zoom   — scale at full travel (default 4)
 * data-ad-dolly-fade   — present: the media eases to transparent over the
 *                        last 15% of travel (the hand-off)
 *
 * Usage:  awardDollyZoom.init(root, { selector })
 * Returns { destroy() }. Idempotent. No-JS: a plain full-bleed image (the pin
 * is CSS sticky, harmless; the scale is JS-applied only). Reduced-motion: the
 * frame holds at rest scale — present, not driven.
 *
 * Perf: transform + opacity only on a promoted layer; one rAF gated by
 * IntersectionObserver on the track and document visibility.
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-dolly-zoom-css';
  var reduce = function () {
    return global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches;
  };
  var clamp = function (v, lo, hi) { return v < lo ? lo : v > hi ? hi : v; };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      '[data-ad-dolly-track]{position:relative;}' +
      '[data-ad-dolly]{position:sticky;top:0;height:100vh;height:100dvh;overflow:hidden;}' +
      '[data-ad-dolly]>img,[data-ad-dolly]>video,[data-ad-dolly]>picture img{' +
      'display:block;width:100%;height:100%;object-fit:cover;will-change:transform;}';
    document.head.appendChild(s);
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-dolly]';
    injectCss();

    var units = [];
    var rafId = 0;
    var io = null, onScroll = null, onVis = null;

    Array.prototype.slice.call(root.querySelectorAll(selector)).forEach(function (el) {
      var media = el.querySelector('img,video');
      if (!media) return;
      var track = el.closest('[data-ad-dolly-track]') || el.parentElement;
      media.style.transformOrigin = (el.getAttribute('data-ad-dolly-origin') || '50% 50%').trim();
      units.push({
        el: el, media: media, track: track,
        zoom: parseFloat(el.getAttribute('data-ad-dolly-zoom')) || 4,
        fade: el.hasAttribute('data-ad-dolly-fade'),
        inView: false, applied: -1
      });
    });

    // Travel 0..1 through the track: pinned from track top to bottom-minus-viewport.
    function travel(u) {
      var vh = global.innerHeight || document.documentElement.clientHeight;
      var r = u.track.getBoundingClientRect();
      return clamp(-r.top / Math.max(1, r.height - vh), 0, 1);
    }

    function frame() {
      rafId = 0;
      units.forEach(function (u) {
        if (!u.inView) return;
        var p = travel(u);
        if (Math.abs(p - u.applied) < 0.0005) return;
        u.applied = p;
        var scale = 1 + (u.zoom - 1) * p;
        u.media.style.transform = 'scale(' + scale.toFixed(4) + ')';
        if (u.fade) {
          u.media.style.opacity = p > 0.85 ? String(clamp(1 - (p - 0.85) / 0.15, 0, 1)) : '1';
        }
      });
    }
    function kick() { if (!rafId) rafId = global.requestAnimationFrame(frame); }

    if (units.length && !reduce()) {
      if ('IntersectionObserver' in global) {
        io = new IntersectionObserver(function (entries) {
          entries.forEach(function (e) {
            var u = units.filter(function (x) { return x.track === e.target; })[0];
            if (u) { u.inView = e.isIntersecting; if (u.inView) kick(); }
          });
        }, { threshold: 0 });
        units.forEach(function (u) { io.observe(u.track); });
      } else {
        units.forEach(function (u) { u.inView = true; });
      }
      onScroll = function () { if (!document.hidden) kick(); };
      global.addEventListener('scroll', onScroll, { passive: true });
      global.addEventListener('resize', onScroll, { passive: true });
      onVis = function () { if (!document.hidden) kick(); };
      document.addEventListener('visibilitychange', onVis);
      kick();
    }

    return {
      destroy: function () {
        if (rafId) global.cancelAnimationFrame(rafId);
        if (io) io.disconnect();
        if (onScroll) {
          global.removeEventListener('scroll', onScroll);
          global.removeEventListener('resize', onScroll);
        }
        if (onVis) document.removeEventListener('visibilitychange', onVis);
        units.forEach(function (u) {
          u.media.style.transform = '';
          u.media.style.transformOrigin = '';
          u.media.style.opacity = '';
        });
        units = [];
        var s = document.getElementById(CSS_ID);
        if (s) s.parentNode.removeChild(s);
      }
    };
  }

  global.awardDollyZoom = { init: init };
})(typeof window !== 'undefined' ? window : this);
