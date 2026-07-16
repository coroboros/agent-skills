/*
 * counter-odometer — stat number roll-up (winners: Terminal Industries, Bruno Simon,
 * Depo Luxe loader counters). The markup carries the FINAL value, so no-JS,
 * reduced-motion, and a dead script all show the true stat — never a 0. On first
 * scroll-into-view the number rolls from 0 (or data-ad-counter-from) to that value
 * with an expo ease-out, preserving the original format: thousands separators
 * (1,344), decimal precision (99.7), and any prefix/suffix (+, %, $, " yr").
 *
 * Usage:  awardCounter.init(root, { selector, threshold })
 *   root      Element|Document  scope (default document)
 *   selector  string            elements to count (default '[data-ad-counter]')
 *   threshold IO threshold      (default 0.5)
 * Per-element: data-ad-counter-from="120"   start value (default 0)
 *              data-ad-counter-dur="1200"   duration ms (default --ad-dur-reveal)
 * Returns { destroy() }. Idempotent. Plays once per element.
 *
 * Tokens: --ad-dur-reveal (800ms). Digits render tabular-nums so width never jitters.
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-counter-css';
  var NUM_RE = /-?\d[\d,]*(?:\.\d+)?/;
  var reduce = function () {
    return global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches;
  };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent = '.ad-counter{font-variant-numeric:tabular-nums;}';
    document.head.appendChild(s);
  }

  // WAAPI can't animate textContent, so the roll is a rAF loop with a JS
  // ease-out-expo — the closest closed-form approximation of --ad-ease-signature.
  function easeOut(t) {
    return t >= 1 ? 1 : 1 - Math.pow(2, -10 * t);
  }

  function parse(el) {
    // Re-init restores from the stored truth instead of parsing mid-roll text.
    if (el.__adCounter) { el.textContent = el.__adCounter.original; return el.__adCounter; }
    var original = el.textContent;
    var m = NUM_RE.exec(original);
    if (!m) return null;
    var num = m[0];
    el.__adCounter = {
      original: original,
      prefix: original.slice(0, m.index),
      suffix: original.slice(m.index + num.length),
      to: parseFloat(num.replace(/,/g, '')),
      commas: num.indexOf(',') !== -1,
      decimals: (num.split('.')[1] || '').length
    };
    return el.__adCounter;
  }

  function format(rec, v) {
    var s = rec.commas
      ? v.toLocaleString('en-US', {
          minimumFractionDigits: rec.decimals,
          maximumFractionDigits: rec.decimals
        })
      : v.toFixed(rec.decimals);
    return rec.prefix + s + rec.suffix;
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-counter]';
    var threshold = opts.threshold != null ? opts.threshold : 0.5;
    injectCss();

    var els = Array.prototype.slice.call(root.querySelectorAll(selector))
      .filter(function (el) { return parse(el) != null; });
    var io = null;
    var anims = [];

    els.forEach(function (el) { el.classList.add('ad-counter'); });

    function tokenDur() {
      var v = parseFloat(
        getComputedStyle(document.documentElement).getPropertyValue('--ad-dur-reveal')
      );
      return v > 0 ? v : 800;
    }

    function finish(anim) {
      anim.el.textContent = anim.rec.original;
      anim.el.removeAttribute('aria-label');
      var i = anims.indexOf(anim);
      if (i !== -1) anims.splice(i, 1);
    }

    function tick(anim) {
      anim.raf = 0;
      if (document.hidden) {
        anim.elapsed = performance.now() - anim.start;
        anim.paused = true;
        return;
      }
      var t = Math.min((performance.now() - anim.start) / anim.dur, 1);
      if (t >= 1) { finish(anim); return; }
      anim.el.textContent =
        format(anim.rec, anim.from + (anim.rec.to - anim.from) * easeOut(t));
      anim.raf = requestAnimationFrame(function () { tick(anim); });
    }

    function play(el) {
      if (el.getAttribute('data-ad-counted') != null) return;
      el.setAttribute('data-ad-counted', '');
      var dur = parseFloat(el.getAttribute('data-ad-counter-dur'));
      if (!(dur > 0)) dur = tokenDur();
      var from = parseFloat(el.getAttribute('data-ad-counter-from'));
      if (isNaN(from)) from = 0;
      // Rolling digits are noise for screen readers — announce the final value
      // for the animation's lifetime, then drop back to the real text.
      el.setAttribute('aria-label', el.__adCounter.original);
      var anim = {
        el: el, rec: el.__adCounter, from: from, dur: dur,
        start: performance.now(), elapsed: 0, paused: false, raf: 0
      };
      anims.push(anim);
      tick(anim);
    }

    // Hidden tabs throttle rAF to zero, so wall-clock progress would jump the
    // roll to its end on return — freeze elapsed time instead and resume.
    function onVisibility() {
      if (document.hidden) {
        anims.forEach(function (anim) {
          if (anim.raf) { cancelAnimationFrame(anim.raf); anim.raf = 0; }
          anim.elapsed = performance.now() - anim.start;
          anim.paused = true;
        });
      } else {
        anims.forEach(function (anim) {
          if (!anim.paused) return;
          anim.paused = false;
          anim.start = performance.now() - anim.elapsed;
          anim.raf = requestAnimationFrame(function () { tick(anim); });
        });
      }
    }
    document.addEventListener('visibilitychange', onVisibility);

    if (!reduce() && 'IntersectionObserver' in global) {
      io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) { play(e.target); io.unobserve(e.target); }
        });
      }, { threshold: threshold });
      els.forEach(function (el) { io.observe(el); });
    } else if (!reduce()) {
      els.forEach(play); // no IO → roll immediately
    }
    // reduce → the markup's final value simply stays; nothing to animate.

    return {
      destroy: function () {
        if (io) io.disconnect();
        document.removeEventListener('visibilitychange', onVisibility);
        anims.forEach(function (anim) { if (anim.raf) cancelAnimationFrame(anim.raf); });
        anims.length = 0;
        els.forEach(function (el) {
          if (el.__adCounter) { el.textContent = el.__adCounter.original; delete el.__adCounter; }
          el.classList.remove('ad-counter');
          el.removeAttribute('data-ad-counted');
          el.removeAttribute('aria-label');
        });
        var s = document.getElementById(CSS_ID);
        if (s) s.parentNode.removeChild(s);
      }
    };
  }

  global.awardCounter = { init: init };
})(typeof window !== 'undefined' ? window : this);
