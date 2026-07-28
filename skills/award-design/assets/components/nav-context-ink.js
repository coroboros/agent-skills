/*
 * nav-context-ink — section-driven nav ink/theme adaptation (corpse-derived:
 * the campaign's own record, not a winner citation — CALDERA's footerNavSwap
 * toggling is-over-light on the nav when the light dawn footer rises under it,
 * AVALANCHE's data-nav-phase attribute set from section [data-phase] via an
 * IntersectionObserver band; both builds invented the swap because the library
 * had no ink axis for the fixed bar). A fixed nav crossing dark hero → light
 * section → dark close needs its ink to follow the ground it floats over.
 *
 * THE CONTRACT: this component only PUBLISHES — it stamps data-ad-nav-ink=
 * "<theme>" on the nav root and touches NOTHING else. It never restyles the
 * nav, never writes a class, and never goes near the accumulator machine's
 * is-hidden / is-scrolled axes (show-on-scroll-up-nav owns visibility and
 * surface; navigation-patterns.md — orthogonal axes, never conflated). The
 * builder's CSS consumes the attribute — and restyles the WHOLE context
 * costume, ink AND the grounded surface (drive-caught: retargeting ink alone
 * leaves the accumulator's dark is-scrolled ground under dark ink over a
 * light chapter — CALDERA's is-over-light swapped mark, links AND scrim):
 *   nav[data-ad-nav][data-ad-nav-ink="light"] { --nav-ink: var(--ad-ground); }
 *   nav[data-ad-nav][data-ad-nav-ink="light"].is-scrolled {
 *     background-color: <the light chapter's ground>; }
 * with its own transition, under its own reduced-motion guard.
 *
 * ZERO-FLIP BY CONSTRUCTION — the two-line agreement machine: two
 * IntersectionObservers watch two 1px horizontal lines, hys px above and below
 * the nav's reference line (its vertical center). The ink commits ONLY when
 * both lines agree on the same theme; while a section boundary sits inside the
 * 2·hys dead zone the state holds. Scroll jitter smaller than the dead zone
 * (±3px against the default 12px hys) can never flip the ink, in either
 * direction — the same invariant the accumulator gives hide/show, delivered
 * IO-based with no scroll listener at all (the corpses' own transport).
 *
 * Expected markup — the builder declares each section's ground:
 *   <header data-ad-nav>…</header>
 *   <section data-ink="dark">…</section>
 *   <section data-ink="light">…</section>
 * Theme names are the builder's vocabulary ("light"/"dark"/anything); the
 * component moves strings, never colors. Sections are expected to tile; in a
 * gap between inked sections the last committed theme holds.
 *
 * Usage:  awardNavContextInk.init(root, { navSelector, sectionSelector, line, hys })
 *   root             Element|Document  scope (default document)
 *   navSelector      string  the nav root (default '[data-ad-nav]')
 *   sectionSelector  string  inked sections (default '[data-ink]')
 *   line             px      reference line from viewport top (default: half
 *                            the nav's height, fallback 32)
 *   hys              px      half-height of the dead zone; falls back to
 *                            --ad-ink-hys on :root, then 12
 * Returns { destroy() } (removes the attribute). Idempotent per nav.
 *
 * No stylesheet is injected — the component paints nothing. No-JS / dead
 * script: the attribute never appears and the builder's default ink stands.
 * prefers-reduced-motion: the state machine still runs — ink over the wrong
 * ground is a legibility failure, not decoration; any easing of the swap is
 * the builder's CSS transition, stripped there under reduce (the
 * navigation-patterns law: reduce snaps state, never disables it).
 */
(function (global) {
  'use strict';

  function cssNumber(name) {
    if (!global.getComputedStyle || !document.documentElement) return NaN;
    return parseFloat(global.getComputedStyle(document.documentElement).getPropertyValue(name));
  }
  function setting(optValue, cssProp, fallback) {
    if (optValue != null) return optValue;
    var fromCss = cssNumber(cssProp);
    return isNaN(fromCss) ? fallback : fromCss;
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var nav = root.querySelector(opts.navSelector || '[data-ad-nav]');
    var sections = Array.prototype.slice.call(
      root.querySelectorAll(opts.sectionSelector || '[data-ink]'));
    if (!nav || !sections.length || nav.__adInkBound) return { destroy: function () {} };
    nav.__adInkBound = true;

    var hys = setting(opts.hys, '--ad-ink-hys', 12);
    var line = opts.line != null ? opts.line
      : (nav.offsetHeight ? nav.offsetHeight * 0.5 : 32);
    if (hys < 1) hys = 1;

    var low = new Map(), high = new Map();   // section -> intersecting the line?
    var ioLow = null, ioHigh = null;
    var current = null;

    function themeOn(map) {
      // A 1px line intersects one tiling section; on overlap, the last in
      // document order wins (deterministic).
      var winner = null;
      for (var i = 0; i < sections.length; i++) if (map.get(sections[i])) winner = sections[i];
      return winner ? winner.getAttribute('data-ink') : null;
    }

    function publish(theme) {
      if (!theme || theme === current) return;
      current = theme;
      nav.setAttribute('data-ad-nav-ink', theme);
    }

    function commit() {
      var tl = themeOn(low), th = themeOn(high);
      if (tl && tl === th) publish(tl); // disagreement (a boundary in the dead zone) holds
    }

    function lineObserver(y, map) {
      var vh = global.innerHeight || 1;
      if (y < 0) y = 0;
      if (y > vh - 1) y = vh - 1;
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) { map.set(en.target, en.isIntersecting); });
        commit();
      }, { rootMargin: -y + 'px 0px ' + -(vh - y - 1) + 'px 0px', threshold: 0 });
      sections.forEach(function (s) { io.observe(s); });
      return io;
    }

    function build() {
      if (ioLow) ioLow.disconnect();
      if (ioHigh) ioHigh.disconnect();
      low.clear(); high.clear();
      // Observing re-fires initial entries, so the maps reseed themselves.
      ioLow = lineObserver(line - hys, low);
      ioHigh = lineObserver(line + hys, high);
    }

    // Sync seed off the nav's own reference line — the first paint carries the
    // correct ink, deep links included (no transparent-frame class of flash).
    (function seed() {
      var winner = null;
      for (var i = 0; i < sections.length; i++) {
        var r = sections[i].getBoundingClientRect();
        if (r.top <= line && r.bottom > line) winner = sections[i];
      }
      if (winner) publish(winner.getAttribute('data-ink'));
    })();

    build();

    // Rebuild on viewport resize — the px rootMargins are viewport-derived.
    var resizeRaf = 0;
    function onResize() {
      cancelAnimationFrame(resizeRaf);
      resizeRaf = requestAnimationFrame(build);
    }
    global.addEventListener('resize', onResize, { passive: true });

    return {
      destroy: function () {
        cancelAnimationFrame(resizeRaf);
        global.removeEventListener('resize', onResize);
        if (ioLow) ioLow.disconnect();
        if (ioHigh) ioHigh.disconnect();
        nav.removeAttribute('data-ad-nav-ink');
        delete nav.__adInkBound;
      }
    };
  }

  global.awardNavContextInk = { init: init };
})(typeof window !== 'undefined' ? window : this);
