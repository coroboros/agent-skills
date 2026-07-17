/*
 * section-scale-momentum — momentum carried at SECTION scale (winner: Sui —
 * the 'Gradient transition' and 'Interactive footer' submission-highlighted
 * captures). The co-equal second momentum channel beside the per-tile loops:
 * the page itself stays alive between sections, not just inside tiles. Two
 * channels, each opt-in by markup:
 *
 *   [data-ad-ssm-bg="<color>"]   the GRADIENT TRANSITION: as scroll advances,
 *     the page ground morphs continuously between consecutive sections'
 *     declared colors — a pure function of scroll position (the viewport
 *     center walking the section midpoints), reversible by construction.
 *     The mix rides CSS color-mix(in oklab) through three custom properties
 *     on the target ground; JS writes only --ad-ssm-from/-to/-p per frame.
 *
 *   [data-ad-ssm-footer]   the INTERACTIVE FOOTER: a live surface, not a
 *     static link column — a pointer-tracked accent glow (component-owned
 *     overlay, aria-hidden, pointer-events:none, promoted) drifts after the
 *     cursor, and opt-in [data-ssm-rise] children scrub up (translate +
 *     opacity) with the footer's own arrival ratio — reversible, re-fires
 *     every pass. Touch keeps the scroll channel; the glow answers the last
 *     touch point through the same pointer events.
 *
 * One rAF serves both channels, armed by scroll/pointer and self-parking
 * when values settle; IntersectionObserver gates the footer work off-screen
 * and visibilitychange parks a hidden tab. Reduced motion: no morph, no glow,
 * no rise — each declaring section takes its own declared color as a STATIC
 * ground (the documented static-end-color answer). No JS: the authored page
 * stands untouched.
 *
 * Usage:  awardSectionScaleMomentum.init(root, { target, selector, footerSelector })
 *   root            Element|Document  scope (default document)
 *   target          Element  the ground that morphs (default document.body)
 *   selector        string   sections (default '[data-ad-ssm-bg]')
 *   footerSelector  string   footers (default '[data-ad-ssm-footer]')
 * Returns { destroy() }. Idempotent per root.
 *
 * Tokens: --ad-accent (the glow).
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-section-scale-momentum-css';
  var ACCENT = 'var(--ad-accent,oklch(62% 0.2 25))';
  var RISE_PX = 24;

  var reduce = function () {
    return global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches;
  };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      // the morphing ground: three JS-fed props, one color-mix — no per-frame
      // style-string parsing, the browser interpolates in oklab
      '.ad-ssm-ground{background:color-mix(in oklab,' +
      'var(--ad-ssm-to) calc(var(--ad-ssm-p)*100%),var(--ad-ssm-from));}' +
      '.ad-ssm-footer{position:relative;}' +
      '.ad-ssm__glow{position:absolute;inset:0;overflow:hidden;' +
      'pointer-events:none;z-index:0;transform:translateZ(0);}' +
      '.ad-ssm__glow::before{content:"";position:absolute;left:0;top:0;' +
      'width:52rem;height:52rem;margin:-26rem 0 0 -26rem;border-radius:50%;' +
      'background:radial-gradient(closest-side,' +
      'color-mix(in oklch,' + ACCENT + ' 16%,transparent),transparent);' +
      'transform:translate3d(var(--_gx,50%),var(--_gy,100%),0);will-change:transform;}' +
      '@media (prefers-reduced-motion:reduce){.ad-ssm__glow{display:none;}}';
    document.head.appendChild(s);
  }

  function clamp01(v) { return v < 0 ? 0 : v > 1 ? 1 : v; }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var target = opts.target || document.body;
    var selector = opts.selector || '[data-ad-ssm-bg]';
    var footerSelector = opts.footerSelector || '[data-ad-ssm-footer]';

    var sections = Array.prototype.slice.call(root.querySelectorAll(selector));

    // Reduced motion: the static end colors — each declaring section takes its
    // own declared ground; no morph, no glow, no rise.
    if (reduce()) {
      sections.forEach(function (sec) {
        sec.style.backgroundColor = sec.getAttribute('data-ad-ssm-bg');
      });
      return {
        destroy: function () {
          sections.forEach(function (sec) { sec.style.backgroundColor = ''; });
        }
      };
    }

    injectCss();
    if (root.__adSectionScaleMomentum) root.__adSectionScaleMomentum.destroy();

    var listeners = [];
    function listen(el, ev, fn, o) {
      el.addEventListener(ev, fn, o);
      listeners.push([el, ev, fn, o]);
    }

    // ---- channel A: the gradient transition -------------------------------
    var stops = null; // [{ y (doc midpoint), color }] sorted
    if (sections.length) target.classList.add('ad-ssm-ground');

    function measure() {
      stops = sections.map(function (sec) {
        var r = sec.getBoundingClientRect();
        return { y: r.top + global.pageYOffset + r.height / 2, color: sec.getAttribute('data-ad-ssm-bg') };
      }).sort(function (a, b) { return a.y - b.y; });
    }

    function applyGround() {
      if (!stops || !stops.length) return;
      var center = global.pageYOffset + global.innerHeight / 2;
      var i = 0;
      while (i < stops.length - 1 && stops[i + 1].y < center) i++;
      var a = stops[i];
      var b = stops[Math.min(i + 1, stops.length - 1)];
      var p = b.y === a.y ? 0 : clamp01((center - a.y) / (b.y - a.y));
      if (center < stops[0].y) { a = b = stops[0]; p = 0; }
      target.style.setProperty('--ad-ssm-from', a.color);
      target.style.setProperty('--ad-ssm-to', b.color);
      target.style.setProperty('--ad-ssm-p', p.toFixed(4));
    }

    // ---- channel B: the interactive footer --------------------------------
    var footers = Array.prototype.slice.call(root.querySelectorAll(footerSelector))
      .map(function (footer) {
        var glow = document.createElement('div');
        glow.className = 'ad-ssm__glow';
        glow.setAttribute('aria-hidden', 'true');
        footer.insertBefore(glow, footer.firstChild);
        footer.classList.add('ad-ssm-footer');
        return {
          footer: footer, glow: glow, on: false,
          gx: 0.5, gy: 1, tx: 0.5, ty: 1,
          risers: Array.prototype.slice.call(footer.querySelectorAll('[data-ssm-rise]'))
        };
      });

    footers.forEach(function (f) {
      listen(f.footer, 'pointermove', function (e) {
        var r = f.footer.getBoundingClientRect();
        f.tx = clamp01((e.clientX - r.left) / Math.max(1, r.width));
        f.ty = clamp01((e.clientY - r.top) / Math.max(1, r.height));
        arm();
      });
    });

    function applyFooters() {
      var settled = true;
      footers.forEach(function (f) {
        if (!f.on) return;
        f.gx += (f.tx - f.gx) * 0.08;
        f.gy += (f.ty - f.gy) * 0.08;
        if (Math.abs(f.tx - f.gx) > 0.001 || Math.abs(f.ty - f.gy) > 0.001) settled = false;
        f.glow.style.setProperty('--_gx', (f.gx * 100).toFixed(2) + '%');
        f.glow.style.setProperty('--_gy', (f.gy * 100).toFixed(2) + '%');
        // the arrival scrub: identity at fully-in-view, reversible on the way out
        var r = f.footer.getBoundingClientRect();
        var vh = global.innerHeight || 1;
        var v = clamp01((vh - r.top) / Math.min(r.height, vh));
        f.risers.forEach(function (el) {
          el.style.transform = 'translate3d(0,' + ((1 - v) * RISE_PX).toFixed(1) + 'px,0)';
          el.style.opacity = (0.25 + 0.75 * v).toFixed(3);
        });
      });
      return settled;
    }

    // ---- the one rAF ------------------------------------------------------
    var raf = 0;
    var lastY = -1;
    function frame() {
      raf = 0;
      if (document.hidden) return;
      var y = global.pageYOffset;
      var scrolled = y !== lastY;
      lastY = y;
      if (scrolled) applyGround();
      var settled = applyFooters();
      if (scrolled || !settled) raf = global.requestAnimationFrame(frame);
    }
    function arm() {
      if (!raf && !document.hidden) raf = global.requestAnimationFrame(frame);
    }

    listen(global, 'scroll', arm, { passive: true });
    listen(global, 'resize', function () { measure(); lastY = -1; arm(); });

    var io = null;
    if ('IntersectionObserver' in global && footers.length) {
      io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          footers.forEach(function (f) {
            if (f.footer === e.target) { f.on = e.isIntersecting; if (f.on) arm(); }
          });
        });
      });
      footers.forEach(function (f) { io.observe(f.footer); });
    } else {
      footers.forEach(function (f) { f.on = true; });
    }

    function onVisibility() {
      if (!document.hidden) { lastY = -1; arm(); }
    }
    document.addEventListener('visibilitychange', onVisibility);

    measure();
    applyGround();
    arm();

    var handle = {
      destroy: function () {
        if (raf) global.cancelAnimationFrame(raf);
        if (io) io.disconnect();
        document.removeEventListener('visibilitychange', onVisibility);
        listeners.forEach(function (l) { l[0].removeEventListener(l[1], l[2], l[3]); });
        target.classList.remove('ad-ssm-ground');
        target.style.removeProperty('--ad-ssm-from');
        target.style.removeProperty('--ad-ssm-to');
        target.style.removeProperty('--ad-ssm-p');
        footers.forEach(function (f) {
          if (f.glow.parentNode) f.glow.parentNode.removeChild(f.glow);
          f.footer.classList.remove('ad-ssm-footer');
          f.risers.forEach(function (el) {
            el.style.transform = '';
            el.style.opacity = '';
          });
        });
        var s = document.getElementById(CSS_ID);
        if (s && s.parentNode) s.parentNode.removeChild(s);
        if (root.__adSectionScaleMomentum === handle) delete root.__adSectionScaleMomentum;
      }
    };
    root.__adSectionScaleMomentum = handle;
    return handle;
  }

  global.awardSectionScaleMomentum = { init: init };
})(typeof window !== 'undefined' ? window : this);
