/*
 * scramble-decode — text decode scramble (winners: Eloy Benoffi [scrambleText]
 * '*&@#%$-_:/;' churn, Guignand scramble+resolve, Igloo SDF decode). Characters
 * churn through a hacker charset and lock to the true glyph left-to-right — the
 * brutalist/experimental data-chrome signature. For SHORT strings only: labels,
 * nav links, stat captions, index numbers. NEVER paragraphs — a scrambled
 * sentence is unreadable noise; a scrambled label is punctuation. Proportional
 * faces shimmy in width while glyphs churn — target mono (--ad-font-mono)
 * elements for a rock-steady box. The rest state is the plain markup text, so
 * no-JS and dead-script renders read normally, and prefers-reduced-motion
 * never scrambles.
 *
 * Usage:  awardScramble.init(root, { selector, charset, tick })
 *   root      Element|Document  scope (default document)
 *   selector  string            elements to decode (default '[data-ad-scramble]')
 *   charset   string            churn glyphs (default '*&@#%$-_:/;01')
 *   tick      ms per re-randomize of unresolved positions (default 80)
 * Per-element: data-ad-scramble="hover" replays a fast decode on each hover.
 * Entrance decode fires once on first scroll-into-view (~600ms); hover replays
 * run ~300ms; an in-flight decode ignores new triggers. Returns { destroy() }.
 * Idempotent.
 *
 * Tokens: none read directly — pair with --ad-font-mono targets for width
 * stability.
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-scramble-css';
  var ENTER_MS = 600;
  var HOVER_MS = 300;
  var WS = /\s/;
  var reduce = function () {
    return global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches;
  };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    // Width-stability hint for digit churn; real stability comes from mono targets.
    s.textContent = '.ad-scramble{font-variant-numeric:tabular-nums;}';
    document.head.appendChild(s);
  }

  // One shared rAF loop drives every in-flight decode — never per-element timers.
  var active = [];
  var rafId = 0;

  function glyph(charset) {
    return charset.charAt(Math.floor(Math.random() * charset.length));
  }

  function finish(rec) {
    rec.el.textContent = rec.original;
    rec.el.removeAttribute('aria-label');
    rec.el.__adScrambling = false;
    var i = active.indexOf(rec);
    if (i !== -1) active.splice(i, 1);
  }

  function step(rec, now) {
    var t = now - rec.start;
    if (t >= rec.dur) { finish(rec); return; }
    var n = rec.chars.length;
    var locked = Math.floor((t / rec.dur) * n);
    var shuffle = now - rec.last >= rec.tick;
    // No lock advanced and no churn due → skip the textContent write entirely.
    if (!shuffle && locked === rec.locked) return;
    if (shuffle) rec.last = now;
    rec.locked = locked;
    var out = '';
    for (var i = 0; i < n; i++) {
      var ch = rec.chars[i];
      // Whitespace stays literal so multi-word labels keep their word shape.
      if (i < locked || WS.test(ch)) { out += ch; continue; }
      if (shuffle || rec.frame[i] == null) rec.frame[i] = glyph(rec.charset);
      out += rec.frame[i];
    }
    rec.el.textContent = out;
  }

  function loop(now) {
    rafId = 0;
    for (var i = active.length - 1; i >= 0; i--) step(active[i], now);
    if (active.length) rafId = requestAnimationFrame(loop);
  }

  function start(el, dur, charset, tick) {
    if (el.__adScrambling || reduce()) return;
    el.__adScrambling = true;
    var original = el.__adScrambleText;
    // The churn glyphs are visual noise — pin the accessible name to the true
    // text for the decode's lifetime (the counter-odometer pattern).
    el.setAttribute('aria-label', original);
    var rec = {
      el: el, original: original, chars: original.split(''),
      dur: dur, charset: charset, tick: tick,
      start: performance.now(), last: performance.now(),
      locked: 0, frame: []
    };
    var out = '';
    for (var i = 0; i < rec.chars.length; i++) {
      out += WS.test(rec.chars[i]) ? rec.chars[i] : (rec.frame[i] = glyph(charset));
    }
    el.textContent = out;
    active.push(rec);
    if (!rafId) rafId = requestAnimationFrame(loop);
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-scramble]';
    var charset = opts.charset || '*&@#%$-_:/;01';
    var tick = opts.tick != null ? opts.tick : 80;

    // reduce → the plain markup text already IS the finished state; arm nothing.
    if (reduce()) return { destroy: function () {} };

    injectCss();

    var els = Array.prototype.slice.call(root.querySelectorAll(selector))
      .filter(function (el) {
        // Preserve the exact original so re-init and destroy restore from truth.
        if (el.__adScrambleText == null) el.__adScrambleText = el.textContent;
        else el.textContent = el.__adScrambleText;
        return el.__adScrambleText.length > 0;
      });
    var io = null;
    var hovers = [];

    els.forEach(function (el) { el.classList.add('ad-scramble'); });

    function entrance(el) {
      if (el.getAttribute('data-ad-decoded') != null) return;
      el.setAttribute('data-ad-decoded', '');
      start(el, ENTER_MS, charset, tick);
    }

    if ('IntersectionObserver' in global) {
      io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) { entrance(e.target); io.unobserve(e.target); }
        });
      }, { threshold: 0.5 });
      els.forEach(function (el) { io.observe(el); });
    } else {
      els.forEach(entrance); // no IO → decode immediately
    }

    els.forEach(function (el) {
      if (el.getAttribute('data-ad-scramble') !== 'hover') return;
      var onEnter = function () { start(el, HOVER_MS, charset, tick); };
      el.addEventListener('mouseenter', onEnter);
      hovers.push({ el: el, fn: onEnter });
    });

    // Hidden tabs freeze rAF; a churn frame left on screen would read as
    // garbage when the user returns — resolve everything to the truth instead.
    function onVisibility() {
      if (!document.hidden) return;
      for (var i = active.length - 1; i >= 0; i--) finish(active[i]);
      if (rafId) { cancelAnimationFrame(rafId); rafId = 0; }
    }
    document.addEventListener('visibilitychange', onVisibility);

    return {
      destroy: function () {
        if (io) io.disconnect();
        document.removeEventListener('visibilitychange', onVisibility);
        hovers.forEach(function (h) { h.el.removeEventListener('mouseenter', h.fn); });
        for (var i = active.length - 1; i >= 0; i--) {
          if (els.indexOf(active[i].el) !== -1) finish(active[i]);
        }
        if (!active.length && rafId) { cancelAnimationFrame(rafId); rafId = 0; }
        els.forEach(function (el) {
          if (el.__adScrambleText != null) {
            el.textContent = el.__adScrambleText;
            delete el.__adScrambleText;
          }
          delete el.__adScrambling;
          el.classList.remove('ad-scramble');
          el.removeAttribute('data-ad-decoded');
          el.removeAttribute('aria-label');
        });
        var s = document.getElementById(CSS_ID);
        if (s) s.parentNode.removeChild(s);
      }
    };
  }

  global.awardScramble = { init: init };
})(typeof window !== 'undefined' ? window : this);
