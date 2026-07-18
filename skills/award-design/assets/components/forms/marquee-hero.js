/*
 * marquee-hero enhancer — the fold's three winner mechanics (winner: Cyd
 * Stumpel; the form's CSS owns the layout, this enhancer owns the motion so
 * the stylesheet ships none). (1) STRIP DRIFT: the overflowing wordmark
 * strip translates horizontally as a PURE function of scroll — the page's
 * own scroll texture, reversible by construction, clamped so the strip's
 * far edge never enters the viewport; rAF-batched, parked while the fold is
 * off-screen and on hidden tabs. (2) BADGE ENTRANCE: the plain badge
 * scale-ins 0->1 over 400ms at a 200ms delay on the bouncy ease — the
 * winner's timing — as an inline WAAPI play (fill:backwards, so a dead or
 * absent script leaves the badge standing: the resting CSS never hides
 * it). (3) BADGE RETIME: a badge carrying data-retime is scroll-retimed
 * instead — the enhancer writes --ad-mh-badge-tilt/--ad-mh-badge-shift on
 * the slot element as a pure function of the fold's exit progress (the
 * animation-timeline idiom as inline var writes; the form CSS composes them
 * in its resting transform). Layering law kept: attribute/style writes on
 * slot elements only, no nodes created, no inner-DOM surgery.
 *
 * Usage:  awardMarqueeHero.init(root, opts)
 *   root      Element|Document  scope (default document)
 *   selector  string  form roots (default '[data-ad-form="marquee-hero"]')
 *   rate      number  strip px per scrolled px (default 0.35)
 * Returns { destroy() }. Idempotent per root.
 *
 * Reduced motion: init is a no-op — no drift, no entrance, no retime; the
 * authored fold IS the hero (prefers-reduced-motion, the live source).
 */
(function (global) {
  'use strict';
  var BOUNCE = 'cubic-bezier(.34,1.56,.64,1)'; // the winner's .4s @.2s bouncy ease

  var reduce = function () {
    return !!(global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches);
  };

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-form="marquee-hero"]';
    var rate = opts.rate != null ? opts.rate : 0.35;

    if (reduce()) return { destroy: function () {} };
    if (root.__adMarqueeHero) return root.__adMarqueeHero;

    var units = [];
    Array.prototype.forEach.call(root.querySelectorAll(selector), function (section) {
      var strip = section.querySelector('[data-slot="strip"]');
      var badges = Array.prototype.slice.call(
        section.querySelectorAll('[data-slot="badge"]'));
      var unit = {
        section: section, strip: strip,
        retime: badges.filter(function (b) { return b.hasAttribute('data-retime'); }),
        enter: badges.filter(function (b) { return !b.hasAttribute('data-retime'); }),
        anims: [], near: true, max: 0
      };
      section.setAttribute('data-ad-mh-live', '');
      units.push(unit);

      // (2) the entrance — inline WAAPI; backwards fill covers only the delay
      unit.enter.forEach(function (b) {
        if (!b.animate) return;
        var tilt = getComputedStyle(b).getPropertyValue('--ad-mh-badge-tilt').trim() || '-8deg';
        unit.anims.push(b.animate(
          [{ transform: 'rotate(' + tilt + ') scale(0)' },
           { transform: 'rotate(' + tilt + ') scale(1)' }],
          { duration: 400, delay: 200, easing: BOUNCE, fill: 'backwards' }));
      });
    });

    function measure(u) {
      if (!u.strip) return;
      u.max = Math.max(0, u.strip.scrollWidth - u.section.clientWidth);
    }

    var rafId = 0;
    function frame() {
      rafId = 0;
      units.forEach(function (u) {
        if (!u.near) return;
        // (1) the drift — a pure function of scroll, clamped at the far edge
        if (u.strip && u.max) {
          var x = Math.min(global.scrollY * rate, u.max);
          u.strip.style.transform = 'translate3d(' + (-x).toFixed(2) + 'px,0,0)';
        }
        // (3) the retime — keyed to how far the fold has scrolled out
        if (u.retime.length) {
          var h = Math.max(1, u.section.offsetHeight);
          var p = Math.min(1, Math.max(0, global.scrollY / h));
          u.retime.forEach(function (b) {
            b.style.setProperty('--ad-mh-badge-tilt', (7 - p * 22).toFixed(2) + 'deg');
            b.style.setProperty('--ad-mh-badge-shift', (-p * 26).toFixed(2) + 'px');
          });
        }
      });
    }
    function kick() { if (!rafId && !document.hidden) rafId = global.requestAnimationFrame(frame); }

    var io = null;
    if ('IntersectionObserver' in global) {
      io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          var u = units.filter(function (x) { return x.section === e.target; })[0];
          if (u) { u.near = e.isIntersecting; if (u.near) kick(); }
        });
      }, { rootMargin: '20% 0px' });
      units.forEach(function (u) { io.observe(u.section); });
    }

    var onScroll = function () { kick(); };
    var onResize = function () { units.forEach(measure); kick(); };
    global.addEventListener('scroll', onScroll, { passive: true });
    global.addEventListener('resize', onResize);
    // a late webfont changes the strip's width — re-measure once settled
    if (document.readyState !== 'complete') {
      global.addEventListener('load', onResize, { once: true });
    }

    units.forEach(measure);
    kick();

    var handle = {
      destroy: function () {
        if (rafId) global.cancelAnimationFrame(rafId);
        if (io) io.disconnect();
        global.removeEventListener('scroll', onScroll);
        global.removeEventListener('resize', onResize);
        units.forEach(function (u) {
          u.anims.forEach(function (a) { a.cancel(); });
          if (u.strip) u.strip.style.transform = '';
          u.retime.forEach(function (b) {
            b.style.removeProperty('--ad-mh-badge-tilt');
            b.style.removeProperty('--ad-mh-badge-shift');
          });
          u.section.removeAttribute('data-ad-mh-live');
        });
        units = [];
        if (root.__adMarqueeHero === handle) delete root.__adMarqueeHero;
      }
    };
    root.__adMarqueeHero = handle;
    return handle;
  }

  global.awardMarqueeHero = { init: init };
})(typeof window !== 'undefined' ? window : this);
