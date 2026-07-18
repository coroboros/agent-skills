/*
 * procession-wayfinding — orientation chrome for the long driven procession
 * (winners: Cartier Watches & Wonders 2025 — six discrete rooms walked by one
 * long scroll-jacked procession, the immersive playbook's gap: the spectacle
 * spine mandates the drive but gives it no wayfinding; Explore Primland — a
 * flythrough carved into beats). A room/chapter index + scene counter +
 * progress rail bound to scroll, telling the visitor WHERE they are in the
 * non-standard scroll and offering real jump targets — keyboard- and
 * skip-reachable by construction because IT STAYS A NAV: the element is the
 * builder's real <nav> of real anchor links; the component mounts aria-hidden
 * chrome around them and NEVER intercepts a click (anchors jump natively, or
 * ride the page's own smooth-scroll layer).
 *
 * Ruled DISTINCT, not an alias, on three seams:
 *   · diegetic-nav (spatial-organic) is a STEERING instrument — the in-world
 *     avatar/vehicle is DRAGGED and its position maps back onto document
 *     scroll, both directions. Wayfinding is READ-ONLY orientation + jump
 *     links: nothing here scrubs the scroll, there is no avatar, no drag
 *     channel — the procession itself (rooms-procession / scroll-camera-dive)
 *     owns the drive.
 *   · telemetry-readout is the continuous INSTRUMENT panel (numeric/text
 *     values welded to progress, no navigation affordance); wayfinding is the
 *     DISCRETE index — n stops, an active one, a counter, jump affordances.
 *   · the corpses' trace-rail inventions (AVALANCHE's SIGNAL rail) carried a
 *     riding readout and no jump targets — that mechanic is telemetry-
 *     readout's; this one is the index Cartier's six-room architecture implies.
 *
 * Active stop — zero-flip by the diegetic-nav law: active = the last stop
 * whose target the viewport CENTER has passed, a pure function of scrollY —
 * discrete writes, only on change. Published as aria-current="true" on the
 * active link and data-ad-wf-active="<index>" on the nav root (-1 before the
 * first target). Crossing forward advances it; scrolling back recedes it —
 * both directions, no hysteresis needed because the reference is a point
 * passing fixed document offsets, never a band fight.
 *
 * Chrome the component mounts (aria-hidden, pointer-events:none):
 *   · a progress rail ([data-wf-rail] > [data-wf-rail-fill]) appended to the
 *     nav — fill scaleY (or scaleX under data-wf-orient="horizontal") welded
 *     directly to progress through the procession span (first target top →
 *     last target bottom), both directions, no easing lag.
 *   · a scene counter written into a builder-authored [data-wf-counter]
 *     ("02 / 06", zero-padded to the stop count) — skipped when not authored.
 *
 * Expected markup — real links; targets resolved from each href:
 *   <nav data-ad-wayfinding aria-label="Rooms">
 *     <a href="#approach" data-wf-stop>Approach</a>
 *     <a href="#hall"     data-wf-stop>Hall</a>
 *     …
 *     <span data-wf-counter aria-hidden="true"></span>
 *   </nav>
 *
 * Usage:  awardProcessionWayfinding.init(root, { selector })
 *   root      Element|Document  scope (default document)
 *   selector  string            nav roots (default '[data-ad-wayfinding]')
 * Returns { destroy() }. Idempotent per nav. Target offsets are measured at
 * init and on resize — never per frame.
 *
 * Content-visible at rest: with no JS the nav is a plain list of working
 * anchors — orientation degrades, navigation never does. prefers-reduced-
 * motion: everything still tracks with INSTANT writes (knowing where you are
 * is state, not decoration) — the fill and counter snap, and the injected
 * stylesheet's one color transition is stripped under the reduce media query.
 *
 * Tokens: --ad-accent (active stop + fill), --ad-ink (rail track),
 *         --ad-dur-base + --ad-ease-signature (the active-color ease only).
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-procession-wayfinding-css';
  // reduced-motion lives entirely in the injected CSS guard below: every JS
  // write here is already instant (no lerp, no rAF loop at rest).

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      '[data-ad-wayfinding] [data-wf-stop]{' +
        'transition:color var(--ad-dur-base,420ms) var(--ad-ease-signature,cubic-bezier(.16,1,.3,1));}' +
      '[data-ad-wayfinding] [data-wf-stop][aria-current="true"]{color:var(--ad-accent,oklch(62% 0.2 25));}' +
      // :where() — zero specificity, so the builder's rail placement always
      // wins over these defaults (the telemetry-readout drive-caught lesson).
      ':where([data-wf-rail]){position:relative;pointer-events:none;' +
        'background:color-mix(in oklab,var(--ad-ink,oklch(96% 0 0)) 18%,transparent);}' +
      '[data-wf-rail-fill]{position:absolute;inset:0;display:block;' +
        'background:var(--ad-accent,oklch(62% 0.2 25));' +
        'transform-origin:top left;transform:scaleY(0);will-change:transform;}' +
      '[data-ad-wayfinding][data-wf-orient="horizontal"] [data-wf-rail-fill]{transform:scaleX(0);}' +
      '@media (prefers-reduced-motion:reduce){' +
        '[data-ad-wayfinding] [data-wf-stop]{transition:none!important;}' +
      '}';
    document.head.appendChild(s);
  }

  function clamp01(v) { return v < 0 ? 0 : (v > 1 ? 1 : v); }

  function pad(n, width) { return String(n).padStart(width, '0'); }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-wayfinding]';
    injectCss();

    var navs = Array.prototype.slice.call(root.querySelectorAll(selector))
      .filter(function (nav) { return !nav.__adWfBound; });
    if (!navs.length) return { destroy: function () {} };

    var instances = [];
    navs.forEach(function (nav) {
      var stops = Array.prototype.slice.call(nav.querySelectorAll('[data-wf-stop]'));
      var targets = [];
      stops = stops.filter(function (a) {
        var href = a.getAttribute('href') || '';
        if (href.charAt(0) !== '#' || href.length < 2) return false;
        var t = document.getElementById(href.slice(1));
        if (!t) return false;
        targets.push(t);
        return true;
      });
      if (!stops.length) return;
      nav.__adWfBound = true;

      var counter = nav.querySelector('[data-wf-counter]');
      var padWidth = String(stops.length).length > 1 ? String(stops.length).length : 2;

      var rail = document.createElement('div');
      rail.setAttribute('data-wf-rail', '');
      rail.setAttribute('aria-hidden', 'true');
      var fill = document.createElement('i');
      fill.setAttribute('data-wf-rail-fill', '');
      rail.appendChild(fill);
      nav.appendChild(rail);

      var horizontal = nav.getAttribute('data-wf-orient') === 'horizontal';
      var tops = [], spanStart = 0, spanEnd = 1;
      function measure() {
        var y = global.scrollY || 0;
        tops = targets.map(function (t) { return t.getBoundingClientRect().top + y; });
        var lastT = targets[targets.length - 1];
        spanStart = tops[0];
        spanEnd = lastT.getBoundingClientRect().top + y + lastT.offsetHeight;
        if (spanEnd - spanStart < 1) spanEnd = spanStart + 1;
      }
      measure();

      var active = -2, lastQ = -1;
      function apply() {
        var ref = (global.scrollY || 0) + global.innerHeight / 2;
        var idx = -1;
        for (var i = 0; i < tops.length; i++) if (tops[i] <= ref) idx = i;
        if (idx !== active) {
          active = idx;
          nav.setAttribute('data-ad-wf-active', String(idx));
          stops.forEach(function (a, i) {
            if (i === idx) a.setAttribute('aria-current', 'true');
            else a.removeAttribute('aria-current');
          });
          if (counter) {
            counter.textContent = (idx < 0 ? pad(0, padWidth) : pad(idx + 1, padWidth))
              + ' / ' + pad(stops.length, padWidth);
          }
        }
        var q = Math.round(clamp01((ref - spanStart) / (spanEnd - spanStart)) * 1e4) / 1e4;
        if (q !== lastQ) {
          lastQ = q;
          fill.style.transform = horizontal ? 'scaleX(' + q + ')' : 'scaleY(' + q + ')';
        }
      }

      instances.push({ nav: nav, rail: rail, stops: stops, measure: measure, apply: apply });
    });
    if (!instances.length) return { destroy: function () {} };

    var ticking = false, rafId = 0, destroyed = false;
    function onScroll() {
      if (ticking) return;
      ticking = true;
      rafId = requestAnimationFrame(function () {
        ticking = false;
        if (destroyed) return;
        instances.forEach(function (inst) { inst.apply(); });
      });
    }
    function onResize() {
      instances.forEach(function (inst) { inst.measure(); });
      onScroll();
    }

    instances.forEach(function (inst) { inst.apply(); }); // seed
    global.addEventListener('scroll', onScroll, { passive: true });
    global.addEventListener('resize', onResize, { passive: true });
    // reduced-motion note: writes above are instant by construction (no lerp,
    // no rAF loop at rest) — reduce needs no separate path beyond the CSS guard.

    return {
      destroy: function () {
        destroyed = true;
        cancelAnimationFrame(rafId);
        global.removeEventListener('scroll', onScroll);
        global.removeEventListener('resize', onResize);
        instances.forEach(function (inst) {
          inst.rail.remove();
          inst.nav.removeAttribute('data-ad-wf-active');
          inst.stops.forEach(function (a) { a.removeAttribute('aria-current'); });
          delete inst.nav.__adWfBound;
        });
      }
    };
  }

  global.awardProcessionWayfinding = { init: init };
})(typeof window !== 'undefined' ? window : this);
