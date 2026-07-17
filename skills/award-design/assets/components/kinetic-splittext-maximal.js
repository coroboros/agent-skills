/*
 * kinetic-splittext-maximal — the characterful display-type entrance
 * (winners: Warhol Arts — SOTD 2025-04; Ponpon Mania — SOTM 2025-10).
 * Distinct from the tier's monochrome line/char masks (kinetic-reveal's
 * uniform mask, char-assemble's positional stagger): here the characters
 * enter IN CHARACTER, two winner-verified modes:
 *   scale    Warhol — per-char scale 0 -> 1 on a back.out overshoot with a
 *            0.1s stagger, colored by the SINGLE-HUE array (the winner runs
 *            #FB4E2B ×7 + one lighter #FFE5D5 — an 8-char cycle where the
 *            eighth char pops light; NOT a multi-hue color-cycle). Fires
 *            once on enter, like the winner's page-wide reveals.
 *   elastic  Ponpon — per-char enter from x:100% with skewX random(-25,25),
 *            rotation 5deg and an elastic.out(0.7,0.7) settle at a 0.06s
 *            stagger, REVERSIBLE on scroll-back: leaving the viewport
 *            reverses the run so re-entry replays (the winner's verified
 *            scroll-back behavior). Monochrome — Ponpon's type inherits.
 * The elastic curve ships as a CSS linear() approximation of
 * elastic.out(0.7,0.7) (GSAP is never required); where linear() is
 * unsupported the settle falls back to a single overshoot bezier. Per-char
 * durations are illustrative — the verified values are the staggers, eases,
 * transforms and the color array. One register page-wide stays the law: the
 * elastic mode IS the playful-elastic register — never mix it with
 * strict-mechanical entrances on the same page.
 * Split and hidden states are JS-applied — no-JS or a dead script shows
 * plain legible text; spaces stay real text nodes so lines re-wrap;
 * aria-label preserves the accessible name. Reduced motion: never splits —
 * whole, visible, instant.
 *
 * Expected markup — the attribute value picks the mode (default 'scale'):
 *   <h1 data-ad-ksm="scale">WARHOL ARTS</h1>
 *   <h2 data-ad-ksm="elastic">PONPON MANIA</h2>
 *
 * Usage:  awardKineticSplittextMaximal.init(root, opts)
 *   root      Element|Document  scope (default document)
 *   selector  string  elements (default '[data-ad-ksm]')
 *   threshold IO threshold (default 0.3)
 * Returns { destroy() }. Idempotent. destroy() restores the authored DOM.
 *
 * Perf: transform/opacity only via WAAPI on inline-block char spans; the IO
 * stays connected only for elastic elements (the reversal needs the exit);
 * scale elements unobserve after their single fire.
 *
 * Tokens: --ad-ksm-hue (the array hue — falls back to --ad-accent),
 * --ad-ksm-pop (the eighth-char light pop — falls back to a white-raised
 * mix of the hue), --ad-dur-reveal (the per-char duration base).
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-kinetic-splittext-maximal-css';
  var CYCLE = 8;             // the winner's array length: 7 hue chars + 1 pop
  var STAGGER_SCALE = 100;   // Warhol 0.1s (verified)
  var STAGGER_ELASTIC = 60;  // Ponpon 0.06s (verified)
  var SKEW_MAX = 25;         // Ponpon skewX random(-25,25) (verified)
  var ROT = 5;               // Ponpon rotation 5deg (verified)
  var BACK_OUT = 'cubic-bezier(.34,1.56,.64,1)'; // back.out
  var OVERSHOOT = 'cubic-bezier(.22,1.6,.36,1)'; // no-linear() elastic stand-in

  var reduce = function () {
    return !!(global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches);
  };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var hue = 'var(--ad-ksm-hue,var(--ad-accent,oklch(62% 0.2 25)))';
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      '.ad-ksm__c{display:inline-block;will-change:transform;}' +
      // the single-hue array: every char takes the hue, each CYCLEth pops light
      '[data-ad-ksm="scale"] .ad-ksm__c{color:' + hue + ';}' +
      '[data-ad-ksm="scale"] .ad-ksm__c--pop{' +
      'color:var(--ad-ksm-pop,color-mix(in oklab,' + hue + ' 22%,white));}';
    document.head.appendChild(s);
  }

  // elastic.out(0.7,0.7) sampled into a CSS linear() easing — amplitude
  // clamps to 1 (GSAP does the same below 1), period 0.7.
  function elasticLinear() {
    var p = 0.7, pts = [];
    for (var i = 0; i <= 40; i++) {
      var t = i / 40;
      var v = t === 0 ? 0 : t === 1 ? 1
        : Math.pow(2, -10 * t) * Math.sin(((t - p / 4) * (2 * Math.PI)) / p) + 1;
      pts.push(v.toFixed(4) + (i > 0 && i < 40 ? ' ' + (t * 100).toFixed(1) + '%' : ''));
    }
    return 'linear(' + pts.join(',') + ')';
  }
  function elasticEase() {
    var lin = elasticLinear();
    try {
      if (global.CSS && global.CSS.supports &&
          global.CSS.supports('animation-timing-function', lin)) return lin;
    } catch (e) {}
    return OVERSHOOT;
  }

  function splitChars(el) {
    if (el.__adKsmHTML == null) el.__adKsmHTML = el.innerHTML;
    else el.innerHTML = el.__adKsmHTML;
    var text = el.textContent.replace(/\s+/g, ' ').trim();
    if (!text) return [];
    if (!el.hasAttribute('aria-label')) { el.setAttribute('aria-label', text); el.__adKsmLabeled = true; }
    el.textContent = '';
    var chars = [], n = 0;
    for (var c = 0; c < text.length; c++) {
      var ch = text.charAt(c);
      if (ch === ' ') { el.appendChild(document.createTextNode(' ')); continue; }
      var box = document.createElement('span');
      box.className = 'ad-ksm__c' + (n % CYCLE === CYCLE - 1 ? ' ad-ksm__c--pop' : '');
      box.textContent = ch;
      el.appendChild(box);
      chars.push(box);
      n++;
    }
    return chars;
  }

  function baseMs() {
    var cs = getComputedStyle(document.documentElement);
    return parseFloat((cs.getPropertyValue('--ad-dur-reveal') || '').trim()) || 800;
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-ksm]';
    var threshold = opts.threshold != null ? opts.threshold : 0.3;

    var els = Array.prototype.slice.call(root.querySelectorAll(selector));
    if (reduce() || !els.length) return { destroy: function () {} }; // whole, visible, instant

    injectCss();
    var ease = elasticEase();

    els.forEach(function (el) {
      if (el.__adKsmChars) return; // idempotent per element
      var mode = el.getAttribute('data-ad-ksm') === 'elastic' ? 'elastic' : 'scale';
      var chars = splitChars(el);
      el.__adKsmChars = chars;
      el.__adKsmMode = mode;
      el.__adKsmAnims = [];
      // JS-applied hidden state → no-JS/dead-script render stays visible
      chars.forEach(function (span) {
        if (mode === 'scale') span.style.transform = 'scale(0)';
        else {
          var skew = (Math.random() * 2 - 1) * SKEW_MAX;
          span.__adKsmFrom =
            'translateX(100%) skewX(' + skew.toFixed(1) + 'deg) rotate(' + ROT + 'deg)';
          span.style.transform = span.__adKsmFrom;
          span.style.opacity = '0';
        }
      });
    });

    function play(el) {
      var mode = el.__adKsmMode;
      var dur = mode === 'scale' ? baseMs() * 0.75 : baseMs() * 1.1;
      var stagger = mode === 'scale' ? STAGGER_SCALE : STAGGER_ELASTIC;
      // a replay replaces the old run — stale fill:'both' animations would
      // otherwise stack forever on the same properties
      (el.__adKsmAnims || []).forEach(function (anim) { if (anim) anim.cancel(); });
      el.__adKsmAnims = el.__adKsmChars.map(function (span, i) {
        if (!span.animate) { span.style.transform = ''; span.style.opacity = ''; return null; }
        var frames = mode === 'scale'
          ? [{ transform: 'scale(0)' }, { transform: 'scale(1)' }]
          : [{ transform: span.__adKsmFrom, opacity: 0 },
             { transform: 'translateX(0) skewX(0deg) rotate(0deg)', opacity: 1 }];
        return span.animate(frames, {
          duration: dur,
          delay: i * stagger,
          easing: mode === 'scale' ? BACK_OUT : ease,
          fill: 'both'
        });
      });
    }

    // Elastic reversal: the run rewinds from wherever it is, so a scroll-back
    // retracts the line and the next entry replays it (the Ponpon behavior).
    function unplay(el) {
      (el.__adKsmAnims || []).forEach(function (anim) {
        if (anim) anim.reverse();
      });
    }

    var io = null;
    if ('IntersectionObserver' in global) {
      io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          var el = e.target;
          if (e.isIntersecting) {
            play(el);
            if (el.__adKsmMode === 'scale') io.unobserve(el); // fire once
          } else if (el.__adKsmMode === 'elastic' && el.__adKsmAnims.length) {
            unplay(el);
          }
        });
      }, { threshold: threshold });
      els.forEach(function (el) { io.observe(el); });
    } else {
      els.forEach(play); // no IO → show assembled immediately
    }

    return {
      destroy: function () {
        if (io) io.disconnect();
        els.forEach(function (el) {
          (el.__adKsmAnims || []).forEach(function (anim) { if (anim) anim.cancel(); });
          if (el.__adKsmHTML != null) { el.innerHTML = el.__adKsmHTML; delete el.__adKsmHTML; }
          if (el.__adKsmLabeled) { el.removeAttribute('aria-label'); delete el.__adKsmLabeled; }
          delete el.__adKsmChars;
          delete el.__adKsmMode;
          delete el.__adKsmAnims;
        });
        var s = document.getElementById(CSS_ID);
        if (s && s.parentNode) s.parentNode.removeChild(s);
      }
    };
  }

  global.awardKineticSplittextMaximal = { init: init };
})(typeof window !== 'undefined' ? window : this);
