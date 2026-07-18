/*
 * diegetic-nav — the in-world steering rail (winners: OceanX 2025 — the
 * exploration ship guiding a free-scroll timeline, forwards or backwards at
 * any point, Awwwards-tagged 'Unusual Navigation' + 'Horizontal Layout';
 * Fluid Glass — Awwwards-tagged 'Unusual Navigation'). Spatial/diegetic
 * primary navigation for the engine/nature register: the visit is steered by
 * an in-world object the user moves along a path, not a top bar. The four
 * gap slots in one fixed rail: the moving avatar/vehicle (builder-authored
 * [data-dnav-stop]-sibling [data-dnav-avatar], or a component dot), the
 * scrubbable path (drag the avatar — its position maps straight onto
 * document scroll, both directions, any point), milestone markers (one per
 * stop link, placed at its target's true document fraction), and the
 * wayfinding minimap (the rail itself: the traveled portion fills behind
 * the avatar). IT STAYS A NAV: the element is the builder's real <nav> of
 * real anchor links — the component only mounts aria-hidden chrome around
 * them, never intercepts a click, and the keyboard path is the links
 * themselves. The current stop publishes as aria-current="true" + a
 * data-ad-dnav-active index on the root — discrete writes, only on change
 * (zero-flip: active = the last stop whose section the viewport centre has
 * passed, a pure accumulator of scroll position).
 * Degrade (the gap's own order): on touch and under reduced motion the drag
 * channel stays dormant and the SAME rail reads as a conventional anchored
 * nav + progress indicator — anchors jump, the fill and avatar still track
 * scroll (instant writes under reduce, no lerp glide).
 *
 * Expected markup — real links; the avatar is optional authored chrome:
 *   <nav data-ad-dnav aria-label="Journey">
 *     <a href="#surface"  data-dnav-stop>Surface</a>
 *     <a href="#midwater" data-dnav-stop>Midwater</a>
 *     …
 *     <span data-dnav-avatar aria-hidden="true">(svg vessel)</span>
 *   </nav>
 *
 * Usage:  awardDiegeticNav.init(root, { selector })
 *   root      Element|Document  scope (default document)
 *   selector  string            nav roots (default '[data-ad-dnav]')
 * Returns { destroy() }. Idempotent per nav.
 *
 * Tokens: --ad-accent (fill + active stop), --ad-ink (rail/labels),
 * --ad-font-mono (labels), --ad-ease-signature (CSS label ease).
 *
 * PERF: scroll/drag writes are rAF-batched transforms (avatar translate,
 * fill scaleX) on promoted layers; the loop parks when the lerp settles and
 * on hidden tabs; fractions recompute on resize only. A dead script leaves
 * the plain anchor list — the nav never depended on the chrome.
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-diegetic-nav-css';
  var ACCENT = 'var(--ad-accent,oklch(62% 0.2 25))';
  var INK = 'var(--ad-ink,oklch(96% 0 0))';
  var LERP = 0.12;   // the vessel's decelerating glide toward its scroll berth
  var SETTLE = 0.4;  // px — under this the loop parks

  var reduce = function () {
    return global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches;
  };
  var finePointer = function () {
    return global.matchMedia && global.matchMedia('(hover: hover) and (pointer: fine)').matches;
  };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      '.ad-dnav{position:fixed;left:50%;transform:translateX(-50%);' +
        'bottom:calc(1.1rem + env(safe-area-inset-bottom,0px));z-index:60;' +
        'width:min(64vw,640px);height:3.4rem;}' +
      '.ad-dnav__rail{position:absolute;left:0;right:0;bottom:.55rem;height:2px;' +
        'background:color-mix(in oklch,' + INK + ' 22%,transparent);border-radius:1px;}' +
      '.ad-dnav__fill{position:absolute;inset:0;transform-origin:left center;' +
        'transform:scaleX(0);background:' + ACCENT + ';border-radius:inherit;' +
        'will-change:transform;}' +
      '.ad-dnav__mark{position:absolute;top:50%;width:6px;height:6px;margin:-3px 0 0 -3px;' +
        'border-radius:50%;background:color-mix(in oklch,' + INK + ' 55%,transparent);}' +
      '.ad-dnav a[data-dnav-stop]{position:absolute;bottom:1.15rem;transform:translateX(-50%);' +
        'font-family:var(--ad-font-mono,ui-monospace,monospace);font-size:.62rem;' +
        'text-transform:uppercase;letter-spacing:.12em;text-decoration:none;' +
        'color:color-mix(in oklch,' + INK + ' 62%,transparent);' +
        'transition:color .3s var(--ad-ease-signature,cubic-bezier(.16,1,.3,1));}' +
      '.ad-dnav a[data-dnav-stop]:hover,.ad-dnav a[data-dnav-stop]:focus-visible{' +
        'color:' + INK + ';}' +
      '.ad-dnav a[data-dnav-stop]:focus-visible{outline:2px solid ' + ACCENT + ';' +
        'outline-offset:3px;}' +
      '.ad-dnav a[data-dnav-stop][aria-current="true"]{color:' + ACCENT + ';}' +
      '.ad-dnav__avatar{position:absolute;left:0;bottom:.55rem;width:14px;height:14px;' +
        'margin:0 0 -6px -7px;border-radius:50%;background:' + ACCENT + ';' +
        'box-shadow:0 0 12px color-mix(in oklch,' + ACCENT + ' 55%,transparent);' +
        'will-change:transform;}' +
      // steering is the fine-pointer channel; touch keeps the anchored nav
      '.ad-dnav.is-steerable .ad-dnav__avatar{pointer-events:auto;cursor:grab;' +
        'touch-action:none;}' +
      '.ad-dnav.is-steering .ad-dnav__avatar{cursor:grabbing;}' +
      '@media (prefers-reduced-motion: reduce){' +
        '.ad-dnav a[data-dnav-stop]{transition:none;}}';
    document.head.appendChild(s);
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-dnav]';
    injectCss();

    var units = [];
    Array.prototype.forEach.call(root.querySelectorAll(selector), function (nav) {
      if (nav.__adDnav) return;
      nav.__adDnav = true;
      nav.classList.add('ad-dnav');

      var stops = Array.prototype.slice.call(nav.querySelectorAll('[data-dnav-stop]'));
      var rail = document.createElement('span');
      rail.className = 'ad-dnav__rail';
      rail.setAttribute('aria-hidden', 'true');
      var fill = document.createElement('span');
      fill.className = 'ad-dnav__fill';
      rail.appendChild(fill);
      stops.forEach(function () {
        var m = document.createElement('span');
        m.className = 'ad-dnav__mark';
        rail.appendChild(m);
      });
      nav.insertBefore(rail, nav.firstChild);

      var avatar = nav.querySelector('[data-dnav-avatar]');
      var made = null;
      if (!avatar) {
        made = document.createElement('span');
        made.setAttribute('aria-hidden', 'true');
        nav.appendChild(made);
        avatar = made;
      }
      avatar.classList.add('ad-dnav__avatar');

      units.push({
        nav: nav, stops: stops, rail: rail, fill: fill, avatar: avatar, made: made,
        marks: Array.prototype.slice.call(rail.querySelectorAll('.ad-dnav__mark')),
        fractions: [], active: -1, x: 0, tx: 0, dragging: false
      });
    });

    if (!units.length) return { destroy: function () {} };

    var still = reduce();

    function docMax() {
      return Math.max(1, document.documentElement.scrollHeight - global.innerHeight);
    }

    function measure(u) {
      var max = docMax();
      u.fractions = u.stops.map(function (a) {
        var id = (a.getAttribute('href') || '').slice(1);
        var t = id && document.getElementById(id);
        if (!t) return 0;
        return Math.min(1, Math.max(0, (t.getBoundingClientRect().top + global.scrollY) / max));
      });
      var w = u.rail.clientWidth;
      u.stops.forEach(function (a, i) { a.style.left = (u.fractions[i] * 100).toFixed(3) + '%'; });
      u.marks.forEach(function (m, i) { m.style.left = (u.fractions[i] * 100).toFixed(3) + '%'; });
      u.railWidth = w;
    }

    function progress() {
      return Math.min(1, Math.max(0, global.scrollY / docMax()));
    }

    // active = last stop whose section start the viewport centre has passed —
    // a pure accumulator of scroll position, written only on change
    function publish(u, p) {
      var centre = p + (global.innerHeight / 2) / docMax();
      var idx = 0;
      for (var i = 0; i < u.fractions.length; i++) {
        if (centre >= u.fractions[i] - 0.001) idx = i;
      }
      if (idx !== u.active) {
        if (u.active >= 0) u.stops[u.active].removeAttribute('aria-current');
        u.stops[idx].setAttribute('aria-current', 'true');
        u.nav.setAttribute('data-ad-dnav-active', String(idx));
        u.active = idx;
      }
    }

    var rafId = 0;
    function frame() {
      rafId = 0;
      var moving = false;
      units.forEach(function (u) {
        u.tx = progress() * u.railWidth;
        if (still) u.x = u.tx;
        else u.x += (u.tx - u.x) * LERP;
        if (Math.abs(u.tx - u.x) > SETTLE) moving = true;
        u.avatar.style.transform = 'translate3d(' + u.x.toFixed(2) + 'px,0,0)';
        u.fill.style.transform = 'scaleX(' + (u.railWidth ? u.x / u.railWidth : 0).toFixed(4) + ')';
        publish(u, progress());
      });
      if (moving && !document.hidden) rafId = global.requestAnimationFrame(frame);
    }
    function kick() { if (!rafId && !document.hidden) rafId = global.requestAnimationFrame(frame); }

    var onScroll = function () { kick(); };
    var onResize = function () { units.forEach(measure); kick(); };
    var onVis = function () { kick(); };
    global.addEventListener('scroll', onScroll, { passive: true });
    global.addEventListener('resize', onResize);
    document.addEventListener('visibilitychange', onVis);
    // late image/font loads move the section anchors — re-measure once settled
    if (document.readyState !== 'complete') {
      global.addEventListener('load', onResize, { once: true });
    }

    // the steering channel — fine pointer only; touch keeps the anchored nav
    var steer = [];
    if (finePointer() && !still) {
      units.forEach(function (u) {
        u.nav.classList.add('is-steerable');
        var onDown = function (e) {
          u.dragging = true;
          u.nav.classList.add('is-steering');
          u.avatar.setPointerCapture(e.pointerId);
          e.preventDefault();
        };
        var onMove = function (e) {
          if (!u.dragging) return;
          var r = u.rail.getBoundingClientRect();
          var p = Math.min(1, Math.max(0, (e.clientX - r.left) / Math.max(1, r.width)));
          global.scrollTo(0, p * docMax());
          kick();
        };
        var onUp = function (e) {
          u.dragging = false;
          u.nav.classList.remove('is-steering');
          if (u.avatar.hasPointerCapture && u.avatar.hasPointerCapture(e.pointerId)) {
            u.avatar.releasePointerCapture(e.pointerId);
          }
        };
        u.avatar.addEventListener('pointerdown', onDown);
        u.avatar.addEventListener('pointermove', onMove);
        u.avatar.addEventListener('pointerup', onUp);
        u.avatar.addEventListener('pointercancel', onUp);
        steer.push({ u: u, down: onDown, move: onMove, up: onUp });
      });
    }

    units.forEach(measure);
    units.forEach(function (u) { u.x = progress() * u.railWidth; });
    kick();

    return {
      destroy: function () {
        if (rafId) global.cancelAnimationFrame(rafId);
        global.removeEventListener('scroll', onScroll);
        global.removeEventListener('resize', onResize);
        document.removeEventListener('visibilitychange', onVis);
        steer.forEach(function (s) {
          s.u.avatar.removeEventListener('pointerdown', s.down);
          s.u.avatar.removeEventListener('pointermove', s.move);
          s.u.avatar.removeEventListener('pointerup', s.up);
          s.u.avatar.removeEventListener('pointercancel', s.up);
        });
        units.forEach(function (u) {
          if (u.rail.parentNode) u.rail.parentNode.removeChild(u.rail);
          if (u.made && u.made.parentNode) u.made.parentNode.removeChild(u.made);
          else {
            u.avatar.classList.remove('ad-dnav__avatar');
            u.avatar.style.transform = '';
          }
          u.stops.forEach(function (a) {
            a.removeAttribute('aria-current');
            a.style.left = '';
          });
          u.nav.removeAttribute('data-ad-dnav-active');
          u.nav.classList.remove('ad-dnav', 'is-steerable', 'is-steering');
          delete u.nav.__adDnav;
        });
        units = [];
        var s = document.getElementById(CSS_ID);
        if (s) s.parentNode.removeChild(s);
      }
    };
  }

  global.awardDiegeticNav = { init: init };
})(typeof window !== 'undefined' ? window : this);
