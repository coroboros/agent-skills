/*
 * clip-reveal — media uncover (winner: Siena Film Foundation, Lando Norris).
 * A wrapper around an <img>/<video> reveals on scroll-in: an animated clip-path
 * opens the media from one edge (inset, default from the bottom) or as an
 * expanding ellipse, while the inner media settles from scale(1.08) to scale(1)
 * for a slight push. Content is fully visible at rest and under reduced-motion;
 * the clip+scale is applied by JS only, so a dead script or no-JS render shows
 * plain visible media.
 *
 * Usage:  awardClipReveal.init(root, { selector, threshold, origin })
 *   root      Element|Document  scope (default document)
 *   selector  string            wrappers to reveal (default '[data-ad-clip]')
 *   threshold IO threshold      (default 0.2)
 *   origin    edge for inset     'bottom'|'top'|'left'|'right' (default 'bottom')
 * Per-element: data-ad-clip="ellipse" expands an ellipse from center instead.
 * Returns { destroy() }. Idempotent. Plays once on enter, then unobserves.
 *
 * Tokens: --ad-dur-reveal (800ms), --ad-ease-signature (cubic-bezier(.16,1,.3,1)).
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-clip-reveal-css';
  var reduce = function () {
    return global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches;
  };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    // Clips the scaled-up media to the wrapper box; JS-injected, so no-JS is untouched.
    s.textContent = '.ad-clip{overflow:hidden;}';
    document.head.appendChild(s);
  }

  // clip-path endpoints: `from` is the closed state, `to` the fully-open one.
  function clipShape(origin, mode) {
    if (mode === 'ellipse') {
      return { from: 'ellipse(0% 0% at 50% 50%)', to: 'ellipse(75% 75% at 50% 50%)' };
    }
    var closed = {
      bottom: 'inset(100% 0 0 0)',
      top: 'inset(0 0 100% 0)',
      left: 'inset(0 100% 0 0)',
      right: 'inset(0 0 0 100%)'
    };
    return { from: closed[origin] || closed.bottom, to: 'inset(0 0 0 0)' };
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-clip]';
    var threshold = opts.threshold != null ? opts.threshold : 0.2;
    var origin = opts.origin || 'bottom';
    injectCss();

    var els = Array.prototype.slice.call(root.querySelectorAll(selector));
    var io = null;

    function styles() {
      var cs = getComputedStyle(document.documentElement);
      return {
        dur: (cs.getPropertyValue('--ad-dur-reveal') || '800ms').trim() || '800ms',
        ease: (cs.getPropertyValue('--ad-ease-signature') || '').trim() ||
          'cubic-bezier(.16,1,.3,1)'
      };
    }

    function geoFor(el) {
      var mode = (el.getAttribute('data-ad-clip') || '').trim() === 'ellipse' ? 'ellipse' : 'inset';
      return clipShape(origin, mode);
    }

    function arm(el) {
      el.classList.add('ad-clip');
      var media = el.querySelector('img,video');
      var target;
      if (media) {
        target = media;
        media.style.transformOrigin = 'center';
      } else {
        // No replaced media: clip a generated inner wrapper, never the observed
        // element itself. A clip-path ON the IntersectionObserver target zeroes
        // its intersection rect, so the browser reports it as never intersecting
        // and the reveal would never fire.
        target = el.__adInner;
        if (!target) {
          target = document.createElement('span');
          target.className = 'ad-clip__inner';
          target.style.display = 'block';
          while (el.firstChild) target.appendChild(el.firstChild);
          el.appendChild(target);
          el.__adInner = target;
        }
      }
      el.__adMedia = media;
      el.__adTarget = target;
      if (reduce()) { el.setAttribute('data-ad-revealed', ''); return; }
      // JS-applied clipped+scaled state → no-JS/dead-script render stays visible.
      var geo = geoFor(el);
      target.style.clipPath = geo.from;
      if (media) media.style.transform = 'scale(1.08)';
    }

    function play(el) {
      if (el.getAttribute('data-ad-revealed') != null) return;
      el.setAttribute('data-ad-revealed', '');
      var s = styles();
      var geo = geoFor(el);
      var media = el.__adMedia;
      var target = el.__adTarget;
      var pending = 1 + (media ? 1 : 0);

      target.style.willChange = 'clip-path';
      if (media) media.style.willChange = 'transform';

      function settle() {
        if (--pending > 0) return;
        target.style.clipPath = geo.to;
        target.style.willChange = '';
        if (media) { media.style.transform = 'scale(1)'; media.style.willChange = ''; }
      }

      if (target.animate) {
        var o = { duration: parseFloat(s.dur), easing: s.ease, fill: 'forwards' };
        target.animate([{ clipPath: geo.from }, { clipPath: geo.to }], o).onfinish = settle;
        if (media) {
          media.animate([{ transform: 'scale(1.08)' }, { transform: 'scale(1)' }], o).onfinish = settle;
        }
      } else {
        var trans = ' ' + s.dur + ' ' + s.ease;
        target.addEventListener('transitionend', settle, { once: true });
        target.style.transition = 'clip-path' + trans;
        target.style.clipPath = geo.to;
        if (media) {
          media.addEventListener('transitionend', settle, { once: true });
          media.style.transition = 'transform' + trans;
          media.style.transform = 'scale(1)';
        }
      }
    }

    els.forEach(arm);

    if (!reduce() && 'IntersectionObserver' in global) {
      io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) { play(e.target); io.unobserve(e.target); }
        });
      }, { threshold: threshold });
      els.forEach(function (el) { io.observe(el); });
    } else {
      els.forEach(play); // reduce or no IO → show finished immediately
    }

    return {
      destroy: function () {
        if (io) io.disconnect();
        els.forEach(function (el) {
          var target = el.__adTarget;
          if (target) {
            target.style.clipPath = '';
            target.style.willChange = '';
            target.style.transition = '';
          }
          var media = el.__adMedia;
          if (media) {
            media.style.transform = '';
            media.style.transformOrigin = '';
            media.style.willChange = '';
            media.style.transition = '';
          }
          // unwrap a generated inner, restoring the original children in place
          if (el.__adInner) {
            var inner = el.__adInner;
            while (inner.firstChild) el.insertBefore(inner.firstChild, inner);
            if (inner.parentNode) inner.parentNode.removeChild(inner);
            delete el.__adInner;
          }
          el.classList.remove('ad-clip');
          el.removeAttribute('data-ad-revealed');
          delete el.__adMedia;
          delete el.__adTarget;
        });
        var s = document.getElementById(CSS_ID);
        if (s) s.parentNode.removeChild(s);
      }
    };
  }

  global.awardClipReveal = { init: init };
})(typeof window !== 'undefined' ? window : this);
