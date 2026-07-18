/*
 * scrub-parallax-bed — the executable form of the corporate-luxury
 * continuation law (winners: Son Daven — SOTD Jun 5 2026, 7.62 + Developer
 * Award 8.09, the reversible scrubbed décor bed under the entire mid-page;
 * award-verified, the interior numbers — layer count, differential rates,
 * the film's scrub:.25 catch-up — are executable defaults, not
 * source-verified; Urban Jürgensen — SOTD Oct 2025, the never-resting
 * scroll). A multi-layer parallax/film bed welded to SCROLL that runs UNDER
 * the whole mid-page while fire-once reveals play over it: [data-depth]
 * layers translate at differential rates as a PURE function of the bed's
 * viewport progress (ease:none — zero lag, the weld; reversible by
 * construction, re-fires every pass), plus an optional film channel whose
 * currentTime chases that progress through a 0.25s catch-up (the scrub:.25
 * register — the film breathes a beat behind the hand).
 * Ruled DISTINCT, not an alias: pointer-parallax is POINTER-driven,
 * fine-pointer only, dormant on touch — this bed is SCROLL-driven,
 * always-on, and works on touch because the thread must survive the pointer
 * going dormant (the playbook's mobile answer); scrubbed-decor-draw welds
 * SVG stroke-draw / pluck / shear channels to scroll — no translate-depth
 * layer and no film lives there; dolly-zoom is a pinned focal push, not an
 * under-page bed.
 *
 * Structure the component drives:
 *   <section data-ad-parallax-bed>            the bed section (mid-page tall)
 *     <div data-depth="0.06">…far plate…</div>     barely moves
 *     <div data-depth="-0.1">…foreground…</div>    negative = moves opposite
 *     <video data-ad-bed-film muted playsinline preload="auto" poster="…">
 *   </section>
 * Layers and film are the build's own media — REAL plates, the bed only
 * moves them. Content over the bed is the section's normal flow; the bed
 * never owns copy.
 *
 * Usage:  awardScrubParallaxBed.init(root, { selector, amplitude })
 *   root       Element|Document  scope (default document)
 *   selector   string  bed roots (default '[data-ad-parallax-bed]')
 *   amplitude  number  px of travel at depth 1 over the bed's full pass
 *                      (default 0.5 * viewport height — LOW amplitude, the
 *                      luxury tell: felt, never announced)
 * Returns { destroy() }. Idempotent per root. destroy() resets every layer
 * transform, releases the film, and removes the stylesheet.
 *
 * Serving: the film channel scrubs currentTime, which needs HTTP Range
 * support; on a server without it the video reports empty seekable ranges —
 * the component self-heals by pulling the source into an in-memory blob
 * (the scrub-film law).
 *
 * Reduced motion: layers stand at their authored rest, the film holds its
 * poster — the bed is décor, the finished state is the authored one. No-JS:
 * identical (the component only ever adds motion to an authored-visible
 * bed). Perf: one rAF per bed while it is on-screen and unsettled, gated by
 * IntersectionObserver and visibilitychange; reads batched (rects cached on
 * resize, only scrollY per frame), transform-only writes on promoted
 * layers; seeks rAF-throttled, skipped in-flight and under one frame.
 *
 * Tokens: none — the bed is the build's own media; color and grade stay the
 * author's.
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-scrub-parallax-bed-css';
  var FILM_TAU = 0.25;       // s — the scrub:.25 catch-up (executable default)
  var FRAME = 1 / 30;        // s — seek floor: never chase under one frame
  var AMP_VH = 0.5;          // default amplitude: half a viewport at depth 1

  var reduce = function () {
    return !!(global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches);
  };
  var clamp01 = function (v) { return v < 0 ? 0 : v > 1 ? 1 : v; };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    // promotion rides the JS-applied live class — no-JS pays nothing
    s.textContent =
      '[data-ad-parallax-bed].ad-spb-live [data-depth]{will-change:transform;}' +
      '[data-ad-parallax-bed].ad-spb-live [data-ad-bed-film]{will-change:auto;}';
    document.head.appendChild(s);
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-parallax-bed]';

    // The finished state IS the authored rest — under reduce nothing binds.
    if (reduce()) return { destroy: function () {} };

    var beds = Array.prototype.slice.call(root.querySelectorAll(selector));
    if (root.matches && root.matches(selector)) beds.unshift(root);
    beds = beds.filter(function (el) { return !el.__adSpb; });
    if (!beds.length) return { destroy: function () {} };

    injectCss();

    var units = beds.map(function (el) {
      var layers = Array.prototype.map.call(el.querySelectorAll('[data-depth]'), function (l) {
        return { el: l, depth: parseFloat(l.getAttribute('data-depth')) || 0 };
      });
      var film = el.querySelector('[data-ad-bed-film]');
      var u = {
        el: el, layers: layers, film: film,
        top: 0, height: 0, amp: 0,
        p: 0, filmT: -1, seeking: false, healed: false,
        visible: false, raf: 0, lastNow: 0
      };
      el.__adSpb = u;
      el.classList.add('ad-spb-live');

      if (film) {
        film.muted = true; // a décor film is never a sound source
        // Range-less serving self-heal: empty seekable after metadata means
        // currentTime writes would no-op — pull the source into a blob.
        film.addEventListener('loadedmetadata', function onMeta() {
          film.removeEventListener('loadedmetadata', onMeta);
          if (u.healed || film.seekable.length) return;
          u.healed = true;
          var src = film.currentSrc || film.src;
          if (!src || src.indexOf('blob:') === 0 || !global.fetch) return;
          global.fetch(src)
            .then(function (r) { return r.blob(); })
            .then(function (b) { film.src = URL.createObjectURL(b); })
            .catch(function () {}); // the poster stands — décor never errors loud
        });
        film.addEventListener('seeked', function () { u.seeking = false; });
      }
      return u;
    });

    function measure() {
      var sy = global.pageYOffset || 0;
      var vh = global.innerHeight || document.documentElement.clientHeight;
      units.forEach(function (u) {
        var r = u.el.getBoundingClientRect();
        u.top = r.top + sy;
        u.height = r.height;
        u.amp = opts.amplitude != null ? opts.amplitude : vh * AMP_VH;
      });
    }

    // Bed progress: 0 the moment its top enters the viewport bottom, 1 when
    // its bottom leaves the top — the full pass, so the weld spans every
    // pixel the bed is on screen. Pure function of scroll: reversible.
    function progress(u) {
      var sy = global.pageYOffset || 0;
      var vh = global.innerHeight || document.documentElement.clientHeight;
      return clamp01((sy + vh - u.top) / (vh + u.height));
    }

    function frame(u, now) {
      u.raf = 0;
      var dt = u.lastNow ? Math.min(0.1, (now - u.lastNow) / 1000) : 0;
      u.lastNow = now;
      u.p = progress(u);

      // Layers: ease:none — the raw weld, differential by depth. Centered so
      // the authored composition is exact at the bed's midpoint pass.
      var offset = u.p - 0.5;
      for (var i = 0; i < u.layers.length; i++) {
        var L = u.layers[i];
        L.el.style.transform =
          'translate3d(0,' + (-offset * L.depth * u.amp).toFixed(2) + 'px,0)';
      }

      // Film: chase p through the .25s catch-up, seek-throttled.
      var busy = false;
      if (u.film && u.film.duration) {
        if (u.filmT < 0) u.filmT = u.p; // first frame converges instantly
        u.filmT += (u.p - u.filmT) * (dt ? 1 - Math.exp(-dt / FILM_TAU) : 1);
        busy = Math.abs(u.p - u.filmT) > 0.001;
        var t = u.filmT * u.film.duration;
        if (!u.seeking && Math.abs(u.film.currentTime - t) > FRAME) {
          u.seeking = true;
          u.film.currentTime = t;
        }
      }
      if (u.visible && busy) u.raf = global.requestAnimationFrame(function (n) { frame(u, n); });
    }

    function wake(u) {
      if (!u.raf && u.visible && !document.hidden) {
        u.lastNow = 0;
        u.raf = global.requestAnimationFrame(function (n) { frame(u, n); });
      }
    }

    var io = null;
    if (global.IntersectionObserver) {
      io = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          var u = en.target.__adSpb;
          if (!u) return;
          u.visible = en.isIntersecting;
          if (u.visible) wake(u);
          else if (u.raf) { global.cancelAnimationFrame(u.raf); u.raf = 0; }
        });
      }, { rootMargin: '10% 0px' });
      units.forEach(function (u) { io.observe(u.el); });
    } else {
      units.forEach(function (u) { u.visible = true; });
    }

    var onScroll = function () { units.forEach(wake); };
    var onResize = function () { measure(); units.forEach(wake); };
    var onVis = function () { if (!document.hidden) units.forEach(wake); };

    measure();
    units.forEach(function (u) { u.visible = u.visible || !io; wake(u); });
    global.addEventListener('scroll', onScroll, { passive: true });
    global.addEventListener('resize', onResize, { passive: true });
    global.addEventListener('load', onResize);
    document.addEventListener('visibilitychange', onVis);

    return {
      destroy: function () {
        global.removeEventListener('scroll', onScroll);
        global.removeEventListener('resize', onResize);
        global.removeEventListener('load', onResize);
        document.removeEventListener('visibilitychange', onVis);
        if (io) io.disconnect();
        units.forEach(function (u) {
          if (u.raf) global.cancelAnimationFrame(u.raf);
          u.layers.forEach(function (L) { L.el.style.transform = ''; });
          u.el.classList.remove('ad-spb-live');
          delete u.el.__adSpb;
        });
        units = [];
        var s = document.getElementById(CSS_ID);
        if (s && s.parentNode) s.parentNode.removeChild(s);
      }
    };
  }

  global.awardScrubParallaxBed = { init: init };
})(typeof window !== 'undefined' ? window : this);
