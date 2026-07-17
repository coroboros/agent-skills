/*
 * flicker-reveal — stochastic per-letter opacity settle (winner: Bisous).
 * Characters fade in on RANDOMIZED opacity transitions — each letter gets
 * its own random delay, duration, and mid-flight opacity dips before
 * settling at 1 — echoing the imperfection of a 3D render / film grain on
 * type. NOT a uniform mask (kinetic-reveal), not a positional stagger
 * (char-assemble), not charset noise (scramble-decode): the letters never
 * move and never change — only their opacity flickers alive. Entrance plays
 * once per element on scroll-into-view; elements marked
 * data-ad-flicker-hover re-fire a short randomized re-flicker on
 * pointerenter/focus (Bisous' menu-link 'randomized letter transformations').
 * The split and hidden state are applied by JS only, so a dead script or
 * no-JS render shows plain legible text; spaces stay real text nodes between
 * the char boxes so the line re-wraps naturally at any width. aria-label
 * preserves the accessible name; reduced motion never splits — instant full
 * opacity.
 *
 * Usage:  awardFlickerReveal.init(root, opts)
 *   root      Element|Document  scope (default document)
 *   selector  string  elements to settle (default '[data-ad-flicker]';
 *                     '[data-ad-flicker-hover]' adds the hover replay)
 *   spread    ms      random-delay window across the line (default 400)
 *   threshold IO threshold (default 0.3)
 * Returns { destroy() }. Idempotent. Entrance plays once per element.
 *
 * Perf: opacity-only (compositor-clean), WAAPI per char with a transition
 * fallback, IO disconnects as elements play; the hover replay animates the
 * already-split spans — zero relayout.
 *
 * Tokens: --ad-dur-reveal (the base settle duration each letter randomizes
 * around).
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-flicker-reveal-css';
  var HOVER_MS = 320;       // hover re-flicker base duration
  var HOVER_SPREAD = 140;   // hover re-flicker random-delay window

  var reduce = function () {
    return global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches;
  };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      '.ad-flick__char{display:inline-block;}';
    document.head.appendChild(s);
  }

  function splitChars(el) {
    // Preserve the original so destroy()/re-init rebuild from truth, not from
    // an already-split DOM.
    if (el.__adFlickHTML == null) el.__adFlickHTML = el.innerHTML;
    else el.innerHTML = el.__adFlickHTML;

    var text = el.textContent.replace(/\s+/g, ' ').trim();
    if (!text) return [];
    // Per-char boxes fragment the accessible name into "W o r k"; name the
    // element with the whole text so a screen reader reads it intact.
    if (!el.hasAttribute('aria-label')) { el.setAttribute('aria-label', text); el.__adFlickLabeled = true; }
    el.textContent = '';

    var chars = [];
    for (var c = 0; c < text.length; c++) {
      var ch = text.charAt(c);
      if (ch === ' ') {
        // Real space text node BETWEEN the boxes — word gaps stay break
        // opportunities, so the line re-wraps naturally.
        el.appendChild(document.createTextNode(' '));
        continue;
      }
      var box = document.createElement('span');
      box.className = 'ad-flick__char';
      box.textContent = ch;
      el.appendChild(box);
      chars.push(box);
    }
    return chars;
  }

  // The stochastic settle: from → dips → 1, every value and clock randomized
  // per letter. `deep` is the entrance (starts at 0); the hover replay starts
  // at 1 and only dips.
  function flicker(span, baseMs, delayMs, deep) {
    var from = deep ? 0 : 1;
    var hi = 0.55 + Math.random() * 0.45;  // a bright pop…
    var lo = 0.05 + Math.random() * 0.35;  // …then a deep dip, per letter
    var dur = baseMs * (0.6 + Math.random() * 0.8);
    var frames = [
      { opacity: from },
      { opacity: hi },
      { opacity: lo },
      { opacity: 1 }
    ];
    if (span.animate) {
      var anim = span.animate(frames, {
        duration: dur, delay: delayMs, easing: 'linear', fill: 'backwards'
      });
      anim.onfinish = function () { span.style.opacity = ''; };
    } else {
      // no WAAPI → a plain randomized fade lands the same resting state
      span.style.transition = 'opacity ' + dur + 'ms linear ' + delayMs + 'ms';
      span.style.opacity = '1';
    }
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-flicker]';
    var spread = opts.spread != null ? opts.spread : 400;
    var threshold = opts.threshold != null ? opts.threshold : 0.3;
    injectCss();

    var els = Array.prototype.slice.call(root.querySelectorAll(selector));
    var io = null;
    var hoverBindings = [];

    function baseMs() {
      var cs = getComputedStyle(document.documentElement);
      return parseFloat((cs.getPropertyValue('--ad-dur-reveal') || '').trim()) || 800;
    }

    function arm(el) {
      el.__adFlickChars = splitChars(el);
      // JS-applied hidden state → no-JS/dead-script render stays visible.
      el.__adFlickChars.forEach(function (span) { span.style.opacity = '0'; });
    }

    function play(el) {
      if (el.getAttribute('data-ad-revealed') != null) return;
      el.setAttribute('data-ad-revealed', '');
      var base = baseMs();
      (el.__adFlickChars || []).forEach(function (span) {
        span.style.opacity = ''; // WAAPI fill:'backwards' owns the hidden start
        flicker(span, base, Math.random() * spread, true);
      });
    }

    // Hover replay (menu links): a short randomized dip-and-settle — the
    // letters are already visible, so the flicker starts and ends at 1.
    function replay(el) {
      var t = global.performance && global.performance.now ? global.performance.now() : Date.now();
      if (el.__adFlickBusyUntil && t < el.__adFlickBusyUntil) return;
      el.__adFlickBusyUntil = t + HOVER_MS + HOVER_SPREAD;
      (el.__adFlickChars || []).forEach(function (span) {
        flicker(span, HOVER_MS, Math.random() * HOVER_SPREAD, false);
      });
    }

    // Under reduce the text is never split — whole, visible, instant.
    if (!reduce()) {
      els.forEach(arm);
      if ('IntersectionObserver' in global) {
        io = new IntersectionObserver(function (entries) {
          entries.forEach(function (e) {
            if (e.isIntersecting) { play(e.target); io.unobserve(e.target); }
          });
        }, { threshold: threshold });
        els.forEach(function (el) { io.observe(el); });
      } else {
        els.forEach(play); // no IO → show finished immediately
      }

      els.forEach(function (el) {
        if (el.getAttribute('data-ad-flicker-hover') == null) return;
        var onEnter = function () { replay(el); };
        el.addEventListener('pointerenter', onEnter);
        el.addEventListener('focusin', onEnter);
        hoverBindings.push({ el: el, handler: onEnter });
      });
    }

    return {
      destroy: function () {
        if (io) io.disconnect();
        hoverBindings.forEach(function (b) {
          b.el.removeEventListener('pointerenter', b.handler);
          b.el.removeEventListener('focusin', b.handler);
        });
        hoverBindings = [];
        els.forEach(function (el) {
          if (el.__adFlickHTML != null) { el.innerHTML = el.__adFlickHTML; delete el.__adFlickHTML; }
          if (el.__adFlickLabeled) { el.removeAttribute('aria-label'); delete el.__adFlickLabeled; }
          el.removeAttribute('data-ad-revealed');
          delete el.__adFlickChars;
          delete el.__adFlickBusyUntil;
        });
        var css = document.getElementById(CSS_ID);
        if (css && css.parentNode) css.parentNode.removeChild(css);
      }
    };
  }

  global.awardFlickerReveal = { init: init };
})(typeof window !== 'undefined' ? window : this);
