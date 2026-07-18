/*
 * horizontal-scroll-chain — the chained lateral macrostructure (winners:
 * OceanX 2025 and Fluid Glass, both carrying the Awwwards 'Horizontal
 * Layout' tag, verified on their own Awwwards pages). The macrostructure the
 * vertical-only grammar omits: a pinned full-viewport section whose inner
 * track translates HORIZONTALLY as vertical scroll distance is consumed —
 * translateX is a PURE function of the section's scroll progress (ease:none,
 * zero lag), so the run is reversible by construction and section seams read
 * as horizontal wipes. The pin is CSS position:sticky (never a scroll
 * hijack): wheel, keyboard, scrollbar and trackpad stay native the whole
 * way, so vertical intent always escapes — the chain simply releases when
 * its consumed distance is spent, in either direction. The section's height
 * is set to travel + one viewport so consumed vertical px equal lateral px
 * 1:1. The panel under the viewport centre publishes as
 * data-ad-hchain-panel on the root (a discrete write, only on change) for
 * wayfinding. Ruled DISTINCT, not an alias: infinite-scroll-loop's x-axis is
 * a drag/wheel CAROUSEL that recycles modulo one copy width and never
 * bottoms out — this chain is FINITE, driven by consumed page scroll, and
 * releasing IS its design; pinned-filmstrip is a native overflow-x row the
 * visitor grabs (self-contained, no pin, page scroll untouched);
 * swipe-snap-gallery is the finite native snap row — which is exactly this
 * component's own touch floor, not its mechanic (the mechanic is the
 * pin+scrub weld).
 * Touch / reduced motion (the gap's own degrade): no pin — the track becomes
 * a native horizontal swipe-snap scroller (touch-action pans both axes, so a
 * vertical swipe over the chain scrolls the page). No-JS: the stylesheet
 * dies with the script and the authored panels stack as normal flow — every
 * panel reachable.
 *
 * Expected markup — the builder authors the finite chain, panel widths free:
 *   <section data-ad-hchain aria-label="…">
 *     <div data-hchain-track>
 *       <article data-hchain-panel>…</article> … more panels …
 *     </div>
 *   </section>
 *
 * Usage:  awardHorizontalScrollChain.init(root, { selector })
 *   root      Element|Document  scope (default document)
 *   selector  string            chain roots (default '[data-ad-hchain]')
 * Returns { destroy() }. Idempotent per section.
 *
 * Tokens: none — the chain is pure structure; panels carry the build's own
 * surfaces.
 *
 * PERF: one passive scroll listener, rAF-batched, early-returns while the
 * section is outside an IntersectionObserver margin; the only per-frame
 * write is the track's translate3d on a will-change layer promoted while
 * live; sizes recompute on resize only. overflow:clip on the root (never
 * hidden — hidden makes a scroll container and kills the sticky pin).
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-horizontal-scroll-chain-css';

  var reduce = function () {
    return global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches;
  };
  var coarse = function () {
    return global.matchMedia && global.matchMedia('(pointer: coarse)').matches;
  };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      // clip, not hidden: hidden creates a scroll container and breaks sticky
      '.ad-hchain{position:relative;overflow:clip;}' +
      '.ad-hchain [data-hchain-track]{position:sticky;top:0;height:100svh;' +
        'display:flex;width:max-content;}' +
      '.ad-hchain [data-hchain-panel]{flex:0 0 auto;height:100%;}' +
      '.ad-hchain.is-live [data-hchain-track]{will-change:transform;}' +
      // the touch / reduced-motion floor: a native swipe-snap scroller
      '.ad-hchain--swipe [data-hchain-track]{position:static;height:auto;' +
        'width:auto;max-width:100%;overflow-x:auto;scroll-snap-type:x mandatory;' +
        'touch-action:pan-x pan-y;-webkit-overflow-scrolling:touch;}' +
      '.ad-hchain--swipe [data-hchain-panel]{scroll-snap-align:start;height:auto;}' +
      '@media (prefers-reduced-motion: reduce){' +
        '.ad-hchain [data-hchain-track]{will-change:auto;}}';
    document.head.appendChild(s);
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-hchain]';
    injectCss();

    var sections = Array.prototype.slice.call(root.querySelectorAll(selector));
    var units = [];
    sections.forEach(function (el) {
      if (el.__adHchain) return;
      el.__adHchain = true;
      el.classList.add('ad-hchain');
      var track = el.querySelector('[data-hchain-track]');
      if (!track) return;
      units.push({ el: el, track: track, top: 0, travel: 0, near: true, panel: -1 });
    });

    // the gap's degrade: swipe-snap on touch, and the same finite native
    // track under reduced motion — user-initiated pan only, zero animation
    if (reduce() || coarse()) {
      units.forEach(function (u) { u.el.classList.add('ad-hchain--swipe'); });
      return {
        destroy: function () {
          units.forEach(function (u) {
            u.el.classList.remove('ad-hchain', 'ad-hchain--swipe');
            delete u.el.__adHchain;
          });
          var s = document.getElementById(CSS_ID);
          if (s) s.parentNode.removeChild(s);
        }
      };
    }

    function measure(u) {
      u.el.style.height = '';
      u.travel = Math.max(0, u.track.scrollWidth - global.innerWidth);
      u.el.style.height = (u.travel + global.innerHeight) + 'px';
      var r = u.el.getBoundingClientRect();
      u.top = r.top + global.scrollY;
      // panel centres in track coordinates, for the wayfinding publish
      u.centres = Array.prototype.map.call(
        u.track.querySelectorAll('[data-hchain-panel]'),
        function (p) { return p.offsetLeft + p.offsetWidth / 2; });
    }

    var rafId = 0;
    function frame() {
      rafId = 0;
      units.forEach(function (u) {
        if (!u.near || !u.travel) return;
        // ease:none — the raw weld; reversible because it is position, not state
        var p = Math.min(1, Math.max(0, (global.scrollY - u.top) / u.travel));
        var x = -(p * u.travel);
        u.track.style.transform = 'translate3d(' + x.toFixed(2) + 'px,0,0)';
        u.el.classList.add('is-live');
        // the panel under the viewport centre — a discrete write, on change only
        var centre = -x + global.innerWidth / 2;
        var idx = 0;
        for (var i = 0; i < u.centres.length; i++) {
          if (Math.abs(u.centres[i] - centre) < Math.abs(u.centres[idx] - centre)) idx = i;
        }
        if (idx !== u.panel) {
          u.panel = idx;
          u.el.setAttribute('data-ad-hchain-panel', String(idx));
        }
      });
    }
    function kick() {
      if (!rafId && !document.hidden) rafId = global.requestAnimationFrame(frame);
    }

    var io = null;
    if ('IntersectionObserver' in global) {
      io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          var u = units.filter(function (x) { return x.el === e.target; })[0];
          if (u) { u.near = e.isIntersecting; if (u.near) kick(); }
        });
      }, { rootMargin: '50% 0px' });
      units.forEach(function (u) { io.observe(u.el); });
    }

    var onScroll = function () { kick(); };
    var onResize = function () { units.forEach(measure); kick(); };
    var onVis = function () { kick(); };
    global.addEventListener('scroll', onScroll, { passive: true });
    global.addEventListener('resize', onResize);
    document.addEventListener('visibilitychange', onVis);
    // late image/font loads change the track's width — re-measure once settled
    if (document.readyState !== 'complete') {
      global.addEventListener('load', onResize, { once: true });
    }

    units.forEach(measure);
    kick();

    return {
      destroy: function () {
        if (rafId) global.cancelAnimationFrame(rafId);
        if (io) io.disconnect();
        global.removeEventListener('scroll', onScroll);
        global.removeEventListener('resize', onResize);
        document.removeEventListener('visibilitychange', onVis);
        units.forEach(function (u) {
          u.el.style.height = '';
          u.track.style.transform = '';
          u.el.removeAttribute('data-ad-hchain-panel');
          u.el.classList.remove('ad-hchain', 'is-live');
          delete u.el.__adHchain;
        });
        units = [];
        var s = document.getElementById(CSS_ID);
        if (s) s.parentNode.removeChild(s);
      }
    };
  }

  global.awardHorizontalScrollChain = { init: init };
})(typeof window !== 'undefined' ? window : this);
