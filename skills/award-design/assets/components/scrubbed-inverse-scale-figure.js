/*
 * scrubbed-inverse-scale-figure — scroll-POSITION-driven masked figure reveal
 * (winners: Gabriel Contassot; Stefan Vitasovic, video-grid variant). The
 * gallery-stack's CONTINUATION carry: a clip-path inset opens from
 * inset(100% 0 0 0) toward inset(0) WHILE the media scales inversely to the
 * same scroll progress (Codrops-verified mechanic: "clip-path inset combined
 * with a Track to sync it with the scroll that also controls the scaling of
 * the inner image"). Welded to scroll position — it re-fires on EVERY pass,
 * both directions, so the stack never reads inert on the second scroll.
 * Distinct from clip-reveal (fire-once, IntersectionObserver-triggered) and
 * dolly-zoom (pinned scale toward a focal point). The scale amplitude default
 * (0.2 → scale 1.2 closed, 1 open) is illustrative, not source-verified —
 * retune via --ad-inverse-amp or opts.amplitude.
 *
 * The clip rides a generated inner box (.ad-invfig__box), never the observed
 * wrapper — a clip-path on the IntersectionObserver target zeroes its
 * intersection rect (the clip-reveal lesson) — and a flow figcaption outside
 * the box is never clipped. Closed state is JS-applied inline, so no-JS and
 * dead-script renders show a plain visible figure; reduced-motion never arms
 * (fully open, scale 1, zero listeners).
 *
 * Usage:  awardInverseScaleFigure.init(root, { selector, amplitude, origin })
 *   root       Element|Document  scope (default document)
 *   selector   string   wrappers to drive (default '[data-ad-inverse]')
 *   amplitude  number   closed-state extra scale (default 0.2; CSS
 *                       --ad-inverse-amp overrides the default)
 *   origin     edge the reveal opens FROM: 'bottom'|'top'|'left'|'right'
 *              (default 'bottom' — the verified inset(100% 0 0 0) start)
 * Returns { destroy() }. Idempotent — re-init on the same root replaces the
 * prior instance. No easing token: the weld to scroll position IS the easing
 * (a scrubbed channel never runs its own clock).
 *
 * Tokens: none required; --ad-inverse-amp is the optional amplitude override.
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-inverse-figure-css';
  var reduce = function () {
    return global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches;
  };
  var clamp = function (v, lo, hi) { return v < lo ? lo : v > hi ? hi : v; };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      '.ad-invfig__box{display:block;position:relative;}' +
      '.ad-invfig__box img,.ad-invfig__box video{display:block;width:100%;}' +
      // promoted only while the unit is actually in view and scrubbing
      '.ad-invfig.is-live .ad-invfig__box{will-change:clip-path;}' +
      '.ad-invfig.is-live .ad-invfig__box img,.ad-invfig.is-live .ad-invfig__box video{' +
      'will-change:transform;}' +
      '@media (prefers-reduced-motion:reduce){' +
      '.ad-invfig .ad-invfig__box{clip-path:none!important;will-change:auto;}' +
      '.ad-invfig .ad-invfig__box img,.ad-invfig .ad-invfig__box video{' +
      'transform:none!important;will-change:auto;}}';
    document.head.appendChild(s);
  }

  // Closed clip per origin; open is always inset(0 0 0 0). `p` is 0 closed → 1 open.
  function clipFor(origin, p) {
    var v = ((1 - p) * 100).toFixed(2) + '%';
    if (origin === 'top') return 'inset(0 0 ' + v + ' 0)';
    if (origin === 'left') return 'inset(0 ' + v + ' 0 0)';
    if (origin === 'right') return 'inset(0 0 0 ' + v + ')';
    return 'inset(' + v + ' 0 0 0)'; // bottom — the verified default
  }

  function cssNumber(name) {
    if (!global.getComputedStyle || !document.documentElement) return NaN;
    return parseFloat(global.getComputedStyle(document.documentElement).getPropertyValue(name));
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-inverse]';
    var fromCss = cssNumber('--ad-inverse-amp');
    var amplitude = opts.amplitude != null ? opts.amplitude
      : (isNaN(fromCss) ? 0.2 : fromCss);
    var origin = opts.origin || 'bottom';
    injectCss();

    if (root.__adInverseFigure) root.__adInverseFigure.destroy();

    var els = Array.prototype.slice.call(root.querySelectorAll(selector));
    var units = [];
    var io = null;
    var rafId = 0;
    var onScroll = null;

    function arm(el) {
      el.classList.add('ad-invfig');
      var box = el.querySelector('.ad-invfig__box');
      if (!box) {
        var media = el.querySelector('img,video');
        if (!media) return null;
        box = document.createElement('span');
        box.className = 'ad-invfig__box';
        media.parentNode.insertBefore(box, media);
        box.appendChild(media);
      }
      return { el: el, box: box, media: box.querySelector('img,video'),
               inView: false, applied: -1 };
    }

    // Progress: enter-bottom → fully open by the time the wrapper is centred
    // (the text-emphasis-fill mapping — the reveal completes at the eye line,
    // then holds; scrolling back re-closes it the same way).
    function progress(u) {
      var vh = global.innerHeight || document.documentElement.clientHeight;
      var r = u.el.getBoundingClientRect();
      return clamp((vh - r.top) / (vh * 0.6 + r.height), 0, 1);
    }

    function apply(u, p) {
      // quantized: a sub-0.2% move writes nothing — no per-frame churn at rest
      var q = Math.round(p * 500) / 500;
      if (q === u.applied) return;
      u.applied = q;
      u.box.style.clipPath = clipFor(origin, q);
      u.media.style.transform = 'scale(' + (1 + amplitude * (1 - q)).toFixed(4) + ')';
    }

    function frame() {
      rafId = 0;
      units.forEach(function (u) {
        if (u.inView) apply(u, progress(u));
      });
    }
    function kick() { if (!rafId) rafId = global.requestAnimationFrame(frame); }

    if (!reduce()) {
      units = els.map(arm).filter(Boolean);
      units.forEach(function (u) {
        u.media.style.transformOrigin = 'center';
        apply(u, progress(u)); // seed the positional state before first scroll
      });

      if ('IntersectionObserver' in global) {
        io = new IntersectionObserver(function (entries) {
          entries.forEach(function (e) {
            var u = units.filter(function (x) { return x.el === e.target; })[0];
            if (!u) return;
            u.inView = e.isIntersecting;
            u.el.classList.toggle('is-live', u.inView);
            if (u.inView) kick();
          });
        }, { threshold: 0 });
        units.forEach(function (u) { io.observe(u.el); });
      } else {
        units.forEach(function (u) { u.inView = true; u.el.classList.add('is-live'); });
        kick();
      }

      onScroll = function () { kick(); };
      global.addEventListener('scroll', onScroll, { passive: true });
      global.addEventListener('resize', onScroll, { passive: true });
    }
    // reduce(): nothing armed — the plain figure IS the finished state.

    var handle = {
      destroy: function () {
        if (rafId) global.cancelAnimationFrame(rafId);
        if (io) io.disconnect();
        if (onScroll) {
          global.removeEventListener('scroll', onScroll);
          global.removeEventListener('resize', onScroll);
        }
        units.forEach(function (u) {
          u.box.style.clipPath = '';
          u.media.style.transform = '';
          u.media.style.transformOrigin = '';
          while (u.box.firstChild) u.box.parentNode.insertBefore(u.box.firstChild, u.box);
          if (u.box.parentNode) u.box.parentNode.removeChild(u.box);
          u.el.classList.remove('ad-invfig', 'is-live');
        });
        units = [];
        els.forEach(function (el) { el.classList.remove('ad-invfig', 'is-live'); });
        var s = document.getElementById(CSS_ID);
        if (s && s.parentNode) s.parentNode.removeChild(s);
        if (root.__adInverseFigure === handle) delete root.__adInverseFigure;
      }
    };
    root.__adInverseFigure = handle;
    return handle;
  }

  global.awardInverseScaleFigure = { init: init };
})(typeof window !== 'undefined' ? window : this);
