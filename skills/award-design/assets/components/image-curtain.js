/*
 * image-curtain — two-beat treated-image reveal (motion-palette canon: the
 * era's grayscale-to-colour curtain). A wrapper around an <img>/<video>
 * uncovers on scroll-in: beat 1 wipes the media open with a clip-path inset
 * from one edge (data-ad-curtain="left|right|top|bottom", default left→right)
 * over --ad-dur-reveal, arriving grayscale(1) contrast(1.05); beat 2 floods
 * the colour in late — the filter releases over --ad-dur-base, delayed to
 * ~70% of beat 1. Both states are JS-applied at arm time, so no-JS or a dead
 * script shows the full-colour unclipped image; reduced motion shows it
 * instantly and observes nothing.
 *
 * The IntersectionObserver watches the WRAPPER while the clip-path rides the
 * inner media: a clip-path on the observed element zeroes its intersection
 * rect, so it would never report as intersecting and the reveal would never
 * fire.
 *
 * Usage:  awardImageCurtain.init(root, { selector, threshold })
 *   root      Element|Document  scope (default document)
 *   selector  string            wrappers to reveal (default '[data-ad-curtain]')
 *   threshold IO threshold      (default 0.25)
 * Returns { destroy() }. Idempotent. Plays once on enter, then unobserves;
 * the observer disconnects once every wrapper has played. destroy() clears
 * inline styles, disconnects, and removes the stylesheet — the media stays
 * in place.
 *
 * Tokens: --ad-dur-reveal (800ms), --ad-dur-base (420ms),
 *         --ad-ease-signature (cubic-bezier(.16,1,.3,1)).
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-image-curtain-css';
  var GRAY = 'grayscale(1) contrast(1.05)';
  var COLOUR = 'grayscale(0) contrast(1)';
  var OPEN = 'inset(0 0 0 0)';
  // Closed clip states keyed by the edge the reveal starts from.
  var CLOSED = {
    left: 'inset(0 100% 0 0)',
    right: 'inset(0 0 0 100%)',
    top: 'inset(0 0 100% 0)',
    bottom: 'inset(100% 0 0 0)'
  };
  var reduce = function () {
    return global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches;
  };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    // Guards subpixel bleed while the inner clip wipes; JS-injected, so no-JS
    // is untouched.
    s.textContent = '.ad-curtain{overflow:hidden;}';
    document.head.appendChild(s);
  }

  function closedFor(el) {
    var edge = (el.getAttribute('data-ad-curtain') || '').trim();
    return CLOSED[edge] || CLOSED.left;
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-curtain]';
    var threshold = opts.threshold != null ? opts.threshold : 0.25;
    injectCss();

    var els = Array.prototype.slice.call(root.querySelectorAll(selector))
      .filter(function (el) { return el.querySelector('img,video'); });
    var io = null;
    var remaining = els.length;

    function styles() {
      var cs = getComputedStyle(document.documentElement);
      var durReveal = parseFloat(cs.getPropertyValue('--ad-dur-reveal')) || 800;
      var durBase = parseFloat(cs.getPropertyValue('--ad-dur-base')) || 420;
      var ease = (cs.getPropertyValue('--ad-ease-signature') || '').trim() ||
        'cubic-bezier(.16,1,.3,1)';
      return {
        durReveal: durReveal,
        durBase: durBase,
        ease: ease,
        delay: Math.round(durReveal * 0.7)
      };
    }

    function arm(el) {
      el.classList.add('ad-curtain');
      el.__adMedia = el.querySelector('img,video');
      if (reduce()) { el.setAttribute('data-ad-revealed', ''); return; }
      // JS-applied closed+grayscale state → no-JS/dead-script render stays
      // full-colour and unclipped.
      el.__adMedia.style.clipPath = closedFor(el);
      el.__adMedia.style.filter = GRAY;
    }

    function play(el) {
      if (el.getAttribute('data-ad-revealed') != null) return;
      el.setAttribute('data-ad-revealed', '');
      var media = el.__adMedia;
      var s = styles();
      var from = closedFor(el);
      var pending = 2;

      media.style.willChange = 'clip-path,filter';

      function settle() {
        if (--pending > 0) return;
        // The finished state is the natural one — clear the inline styles so
        // the settled DOM matches a no-JS render.
        media.style.clipPath = '';
        media.style.filter = '';
        media.style.willChange = '';
        media.style.transition = '';
      }

      if (media.animate) {
        media.animate(
          [{ clipPath: from }, { clipPath: OPEN }],
          { duration: s.durReveal, easing: s.ease, fill: 'forwards' }
        ).onfinish = settle;
        media.animate(
          [{ filter: GRAY }, { filter: COLOUR }],
          { duration: s.durBase, delay: s.delay, easing: s.ease, fill: 'forwards' }
        ).onfinish = settle;
      } else {
        var onEnd = function () {
          settle();
          if (pending <= 0) media.removeEventListener('transitionend', onEnd);
        };
        media.addEventListener('transitionend', onEnd);
        media.style.transition =
          'clip-path ' + s.durReveal + 'ms ' + s.ease + ',' +
          'filter ' + s.durBase + 'ms ' + s.ease + ' ' + s.delay + 'ms';
        media.style.clipPath = OPEN;
        media.style.filter = COLOUR;
      }
    }

    els.forEach(arm);

    if (!reduce() && 'IntersectionObserver' in global) {
      io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (!e.isIntersecting) return;
          play(e.target);
          io.unobserve(e.target);
          if (--remaining <= 0) io.disconnect();
        });
      }, { threshold: threshold });
      els.forEach(function (el) { io.observe(el); });
    } else {
      els.forEach(play); // reduce or no IO → finished state (play no-ops under reduce)
    }

    return {
      destroy: function () {
        if (io) io.disconnect();
        els.forEach(function (el) {
          var media = el.__adMedia;
          if (media) {
            media.style.clipPath = '';
            media.style.filter = '';
            media.style.willChange = '';
            media.style.transition = '';
          }
          el.classList.remove('ad-curtain');
          el.removeAttribute('data-ad-revealed');
          delete el.__adMedia;
        });
        var s = document.getElementById(CSS_ID);
        if (s) s.parentNode.removeChild(s);
      }
    };
  }

  global.awardImageCurtain = { init: init };
})(typeof window !== 'undefined' ? window : this);
