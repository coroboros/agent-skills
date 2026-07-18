/*
 * scroll-speed-oscillator — the velocity décor channel (winners: Exat —
 * exat.hottype.co, Awwwards SOTD + FWA of the Day + CSSDA Website of the
 * Month 8.83 — large numerals oscillate in a sine wave whose AMPLITUDE
 * tracks scroll speed; Ponpon Mania — SOTM 2025-10 + Dev Award — a rendered
 * object's position takes a velocity*0.01 feedback nudge; 21 TSI — SOTD
 * 2025-04-12 + FWA + CSSDA — velocity/inertia distortion on media). Every
 * other scrubbed channel in the library binds to scroll POSITION; this one
 * reads VELOCITY — the page's own momentum made visible, settling back to
 * the composed rest as the scroll stops. Three declared modes:
 *
 *   data-ad-sso / data-ad-sso="wave"   the Exat TYPE variant: the component
 *     splits the text into glyph cells (or takes authored [data-sso-unit]
 *     units) and rides each on translateY = amp * sin(t + i*stride), the
 *     amplitude tracking smoothed scroll speed — a standing wave that swells
 *     with the flick and dies with it.
 *
 *   data-ad-sso="nudge"   the Ponpon feedback: the whole element translates
 *     by velocity * 0.01 (the winner's factor), clamped, easing back to rest
 *     through the same smoothing.
 *
 *   data-ad-sso="shift"   the 21 TSI MEDIA variant, DOM-expressed as
 *     displacement: skewY + a vertical stretch proportional to velocity on
 *     imagery/surfaces. The RGB-shift expression of the same signal is
 *     WebGL-delegated (21 TSI runs OGL) — this component ships the
 *     transform-only displacement half. The host parent is clipped while
 *     live (JS-applied class — a stretched figure never paints over
 *     neighboring sections; a dead script leaves nothing clipped).
 *
 * Compositor-only: every write is a transform on a promoted unit; velocity
 * is sampled per frame from pageYOffset (one read, no layout). The one rAF
 * arms on scroll, runs while the smoothed velocity or any amplitude is
 * unsettled, then writes every unit back to rest and parks.
 * IntersectionObserver gates writes per element off-screen (leaving the
 * viewport rests the element so it never re-enters frozen mid-wave);
 * visibilitychange parks a hidden tab. NOT pointer-gated: scroll is the
 * input, so the channel stays live on touch — depth that came from the
 * pointer comes from scroll (the archetype's mobile answer).
 * reduced-motion: fully dormant — the authored composition stands, the text
 * is never split, nothing is armed.
 *
 * Expected markup:
 *   <div data-ad-sso>0123456789</div>
 *   <div data-ad-sso="wave"><span data-sso-unit>Aa</span>…</div>
 *   <h2 data-ad-sso="nudge">…</h2>
 *   <figure><img data-ad-sso="shift" …></figure>
 *
 * Usage:  awardScrollSpeedOscillator.init(root, opts)
 *   root      Element|Document  scope (default document)
 *   selector  string  driven elements (default '[data-ad-sso]')
 * Returns { destroy() }. Idempotent per element. destroy() rests every unit,
 * restores split DOM, and removes the stylesheet.
 *
 * A11y + perf: split roots keep their accessible name via aria-label; spaces
 * stay real text nodes so glyph rows re-wrap; the layer is décor — it never
 * carries content of its own.
 *
 * Tokens: --ad-sso-amp (wave amplitude ceiling, default 18px). The nudge
 * factor 0.01 is the winner's number; the skew/stretch ceilings are
 * illustrative.
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-scroll-speed-oscillator-css';
  var NUDGE = 0.01;        // Ponpon's velocity*0.01 — the winner's factor
  var NUDGE_MAX = 48;      // px clamp on the nudge offset
  var SKEW_MAX = 6;        // deg — the shift ceiling (illustrative)
  var STRETCH_MAX = 0.06;  // scaleY over 1 at full velocity (illustrative)
  var V_FULL = 3000;       // px/s that reads as "full speed" for normalization
  var SMOOTH = 0.14;       // velocity lerp per frame — the inertia feel
  var WAVE_HZ = 1.1;       // standing-wave cycles per second
  var STRIDE = 0.85;       // phase offset between neighboring units (rad)
  var EPS = 0.4;           // settled below this smoothed px/s

  var reduce = function () {
    return !!(global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches);
  };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      '.ad-sso__u{display:inline-block;will-change:transform;}' +
      '.ad-sso--shift{will-change:transform;}' +
      // the full-bleed overlay law: a stretched figure stays inside its frame
      '.ad-sso-frame{overflow:hidden;}';
    document.head.appendChild(s);
  }

  // Split into glyph cells — spaces stay real text nodes so rows keep their
  // break opportunities; the root keeps its accessible name.
  function splitGlyphs(el) {
    if (el.__adSsoHTML == null) el.__adSsoHTML = el.innerHTML;
    else el.innerHTML = el.__adSsoHTML;
    var text = el.textContent.replace(/\s+/g, ' ').trim();
    if (!el.hasAttribute('aria-label')) { el.setAttribute('aria-label', text); el.__adSsoLabeled = true; }
    el.textContent = '';
    var units = [];
    for (var c = 0; c < text.length; c++) {
      var ch = text.charAt(c);
      if (ch === ' ') { el.appendChild(document.createTextNode(' ')); continue; }
      var box = document.createElement('span');
      box.className = 'ad-sso__u';
      box.textContent = ch;
      el.appendChild(box);
      units.push(box);
    }
    return units;
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-sso]';

    // Dormant under reduce — the décor channel is motion by definition; the
    // authored composition stands, the text is never split.
    if (reduce()) return { destroy: function () {} };

    injectCss();
    var amp = parseFloat(getComputedStyle(document.documentElement)
      .getPropertyValue('--ad-sso-amp')) || 18;

    var fields = [];
    Array.prototype.forEach.call(root.querySelectorAll(selector), function (el) {
      if (el.__adSsoField) return; // idempotent per element
      var mode = el.getAttribute('data-ad-sso') || 'wave';
      if (mode !== 'nudge' && mode !== 'shift') mode = 'wave';
      var f = { el: el, mode: mode, units: null, on: true, atRest: true, frame: null };
      if (mode === 'wave') {
        var authored = el.querySelectorAll('[data-sso-unit]');
        if (authored.length) {
          f.units = Array.prototype.slice.call(authored);
          f.units.forEach(function (u) { u.classList.add('ad-sso__u'); });
        } else {
          f.units = splitGlyphs(el);
        }
      } else {
        el.classList.add('ad-sso--shift');
        if (mode === 'shift' && el.parentElement) {
          f.frame = el.parentElement;
          f.frame.classList.add('ad-sso-frame');
        }
      }
      el.__adSsoField = f;
      fields.push(f);
    });
    if (!fields.length) return { destroy: function () {} };

    var v = 0;           // smoothed velocity, px/s (signed)
    var lastY = global.pageYOffset;
    var lastT = 0;
    var raf = 0;

    function rest(f) {
      if (f.atRest) return;
      f.atRest = true;
      if (f.mode === 'wave') f.units.forEach(function (u) { u.style.transform = ''; });
      else f.el.style.transform = '';
    }

    function write(f, now) {
      var v01 = Math.max(-1, Math.min(1, v / V_FULL));
      if (f.mode === 'wave') {
        var a = Math.abs(v01) * amp;
        if (a < 0.05) { rest(f); return; }
        var t = now * 0.001 * WAVE_HZ * 2 * Math.PI;
        for (var i = 0; i < f.units.length; i++) {
          f.units[i].style.transform =
            'translate3d(0,' + (a * Math.sin(t + i * STRIDE)).toFixed(2) + 'px,0)';
        }
      } else if (f.mode === 'nudge') {
        var off = Math.max(-NUDGE_MAX, Math.min(NUDGE_MAX, v * NUDGE));
        if (Math.abs(off) < 0.05) { rest(f); return; }
        f.el.style.transform = 'translate3d(0,' + off.toFixed(2) + 'px,0)';
      } else {
        var sk = v01 * SKEW_MAX;
        var st = 1 + Math.abs(v01) * STRETCH_MAX;
        if (Math.abs(sk) < 0.02) { rest(f); return; }
        f.el.style.transform = 'skewY(' + sk.toFixed(3) + 'deg) scaleY(' + st.toFixed(4) + ')';
      }
      f.atRest = false;
    }

    function frame(now) {
      raf = 0;
      if (document.hidden) return;
      var y = global.pageYOffset;
      var dt = lastT ? (now - lastT) / 1000 : 0.016;
      lastT = now;
      if (dt > 0) {
        var inst = (y - lastY) / Math.max(dt, 0.004);
        v += (inst - v) * SMOOTH;
      }
      lastY = y;
      var live = Math.abs(v) > EPS;
      var unsettled = false;
      fields.forEach(function (f) {
        if (!f.on) { rest(f); return; }
        write(f, now);
        if (!f.atRest) unsettled = true;
      });
      if (live || unsettled) raf = global.requestAnimationFrame(frame);
      else { v = 0; lastT = 0; }
    }
    function arm() {
      if (!raf && !document.hidden) raf = global.requestAnimationFrame(frame);
    }

    var io = null;
    if ('IntersectionObserver' in global) {
      io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          var f = e.target.__adSsoField;
          if (!f) return;
          f.on = e.isIntersecting;
          if (!f.on) rest(f); // never re-enter frozen mid-wave
        });
      });
      fields.forEach(function (f) { io.observe(f.el); });
    }

    var onScroll = function () { arm(); };
    var onVis = function () { if (!document.hidden) { lastT = 0; lastY = global.pageYOffset; arm(); } };
    global.addEventListener('scroll', onScroll, { passive: true });
    document.addEventListener('visibilitychange', onVis);

    return {
      destroy: function () {
        if (raf) global.cancelAnimationFrame(raf);
        if (io) io.disconnect();
        global.removeEventListener('scroll', onScroll);
        document.removeEventListener('visibilitychange', onVis);
        fields.forEach(function (f) {
          rest(f);
          if (f.mode === 'wave') {
            if (f.el.__adSsoHTML != null) { f.el.innerHTML = f.el.__adSsoHTML; delete f.el.__adSsoHTML; }
            else f.units.forEach(function (u) { u.classList.remove('ad-sso__u'); });
            if (f.el.__adSsoLabeled) { f.el.removeAttribute('aria-label'); delete f.el.__adSsoLabeled; }
          } else {
            f.el.classList.remove('ad-sso--shift');
            if (f.frame) f.frame.classList.remove('ad-sso-frame');
          }
          delete f.el.__adSsoField;
        });
        fields.length = 0;
        var s = document.getElementById(CSS_ID);
        if (s && s.parentNode) s.parentNode.removeChild(s);
      }
    };
  }

  global.awardScrollSpeedOscillator = { init: init };
})(typeof window !== 'undefined' ? window : this);
