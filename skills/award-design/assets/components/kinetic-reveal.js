/*
 * kinetic-reveal — masked line reveal (winner: Siena Film Foundation, Lando Norris).
 * Lines sit in an overflow-clip box and translate up from below with a hard mask
 * edge, staggered — the tier's default headline entrance, cleaner than a per-char
 * fade. Content is fully visible at rest and under reduced-motion; the clip+offset
 * is applied by JS only, so a dead script or no-JS render shows plain legible text.
 *
 * Usage:  awardKineticReveal.init(root, { selector, stagger, threshold })
 *   root      Element|Document  scope (default document)
 *   selector  string            elements to split (default '[data-ad-reveal]')
 *   stagger   ms per line       (default 60)
 *   threshold IO threshold      (default 0.2)
 * Returns { destroy() }. Idempotent. Re-splits on resize.
 *
 * Tokens: --ad-dur-reveal (800ms), --ad-ease-signature (cubic-bezier(.16,1,.3,1)).
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-kinetic-reveal-css';
  var reduce = function () {
    return global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches;
  };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      '.ad-line{display:block;overflow:hidden;}' +
      '.ad-line__in{display:block;will-change:transform;}';
    document.head.appendChild(s);
  }

  function splitToLines(el) {
    // Preserve the original so destroy()/resize can rebuild from truth.
    if (el.__adRevealHTML == null) el.__adRevealHTML = el.innerHTML;
    else el.innerHTML = el.__adRevealHTML;

    var text = el.textContent.replace(/\s+/g, ' ').trim();
    if (!text) return [];
    el.textContent = '';
    var words = text.split(' ');
    // Word boxes with a real space text node BETWEEN them (not baked inside the
    // box) so the browser breaks lines exactly as it would for normal flowing
    // text — a space inside an inline-block is not a break opportunity, which
    // collapses a wrapping headline onto one measured line and defeats the mask.
    var probes = words.map(function (w, i) {
      var span = document.createElement('span');
      span.textContent = w;
      span.style.display = 'inline-block';
      el.appendChild(span);
      if (i < words.length - 1) el.appendChild(document.createTextNode(' '));
      return span;
    });

    // Group words into visual lines by vertical offset.
    var lines = [];
    var current = null;
    var lastTop = null;
    probes.forEach(function (span) {
      var top = span.offsetTop;
      if (lastTop === null || Math.abs(top - lastTop) > 1) {
        current = [];
        lines.push(current);
        lastTop = top;
      }
      current.push(span.textContent);
    });

    // Rebuild as clip lines.
    el.innerHTML = '';
    var inners = [];
    lines.forEach(function (words) {
      var line = document.createElement('span');
      line.className = 'ad-line';
      var inner = document.createElement('span');
      inner.className = 'ad-line__in';
      inner.textContent = words.join(' ');
      line.appendChild(inner);
      el.appendChild(line);
      inners.push(inner);
    });
    return inners;
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-reveal]';
    var stagger = opts.stagger != null ? opts.stagger : 60;
    var threshold = opts.threshold != null ? opts.threshold : 0.2;
    injectCss();

    var els = Array.prototype.slice.call(root.querySelectorAll(selector));
    var io = null;
    var resizeRAF = 0;

    function styles() {
      var cs = getComputedStyle(document.documentElement);
      return {
        dur: (cs.getPropertyValue('--ad-dur-reveal') || '800ms').trim() || '800ms',
        ease: (cs.getPropertyValue('--ad-ease-signature') || '').trim() ||
          'cubic-bezier(.16,1,.3,1)'
      };
    }

    function arm(el) {
      var inners = splitToLines(el);
      el.__adInners = inners;
      if (reduce()) { el.setAttribute('data-ad-revealed', ''); return; }
      // JS-applied hidden state → no-JS/dead-script render stays visible.
      inners.forEach(function (inner) { inner.style.transform = 'translate3d(0,110%,0)'; });
    }

    function play(el) {
      if (el.getAttribute('data-ad-revealed') != null) return;
      el.setAttribute('data-ad-revealed', '');
      var s = styles();
      (el.__adInners || []).forEach(function (inner, i) {
        if (inner.animate) {
          inner.animate(
            [{ transform: 'translate3d(0,110%,0)' }, { transform: 'translate3d(0,0,0)' }],
            { duration: parseFloat(s.dur), easing: s.ease, delay: i * stagger, fill: 'forwards' }
          ).onfinish = function () { inner.style.transform = 'translate3d(0,0,0)'; };
        } else {
          inner.style.transition = 'transform ' + s.dur + ' ' + s.ease + ' ' + (i * stagger) + 'ms';
          inner.style.transform = 'translate3d(0,0,0)';
        }
      });
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

    function onResize() {
      cancelAnimationFrame(resizeRAF);
      resizeRAF = requestAnimationFrame(function () {
        els.forEach(function (el) {
          var wasRevealed = el.getAttribute('data-ad-revealed') != null;
          el.removeAttribute('data-ad-revealed');
          el.__adInners = splitToLines(el);
          if (reduce()) return;
          el.__adInners.forEach(function (inner) {
            inner.style.transform = wasRevealed ? 'translate3d(0,0,0)' : 'translate3d(0,110%,0)';
          });
          if (wasRevealed) el.setAttribute('data-ad-revealed', '');
          else if (io) io.observe(el);
        });
      });
    }
    global.addEventListener('resize', onResize);

    return {
      destroy: function () {
        if (io) io.disconnect();
        global.removeEventListener('resize', onResize);
        els.forEach(function (el) {
          if (el.__adRevealHTML != null) { el.innerHTML = el.__adRevealHTML; delete el.__adRevealHTML; }
          el.removeAttribute('data-ad-revealed');
          delete el.__adInners;
        });
      }
    };
  }

  global.awardKineticReveal = { init: init };
})(typeof window !== 'undefined' ? window : this);
