/*
 * valediction-footer — cinematic bookend footer (winner: Lando Norris).
 * The page's closing <footer>. When it scrolls into view the palette flips once
 * to the inverse of the page — ground/ink swap to ink/ground — and the oversized
 * [data-ad-valediction-mark] rises out of a hard mask. A single, deliberate close,
 * never a loop. Content is fully legible at rest and under reduced-motion: the flip
 * and the reveal are JS-added, so a dead script or no-JS render shows a plain,
 * readable footer. The ground/ink pair inverts onto itself, so contrast holds
 * identically in both palette states.
 *
 * Expected markup:
 *   <footer data-ad-valediction>
 *     <h2 data-ad-valediction-mark>Until the next reel.</h2>
 *     <div class="signature">— The Foundation, since 1961</div>
 *     <nav>… contact links …</nav>
 *     <div data-ad-valediction-baseline>© 2025</div>
 *   </footer>
 *
 * Usage:  awardValediction.init(root, { selector, threshold })
 *   root      Element|Document  scope (default document)
 *   selector  string            footers to arm (default '[data-ad-valediction]')
 *   threshold IO threshold      (default 0.3)
 * Returns { destroy() }. Idempotent. Flips once on enter, then unobserves.
 *
 * Tokens: --ad-ground (oklch(14% 0.01 260)), --ad-ink (oklch(96% 0 0)),
 *         --ad-dur-reveal (800ms), --ad-ease-signature (cubic-bezier(.16,1,.3,1)).
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-valediction-css';
  var FLIP = 'is-flipped';
  var REVEALED = 'data-ad-revealed';
  var MARK_SEL = '[data-ad-valediction-mark]';
  var INNER_CLASS = 'ad-valediction-mark__in';
  var GROUND = 'var(--ad-ground,oklch(14% 0.01 260))';
  var INK = 'var(--ad-ink,oklch(96% 0 0))';
  var TRANSIT = 'var(--ad-dur-reveal,800ms) var(--ad-ease-signature,cubic-bezier(.16,1,.3,1))';
  var reduce = function () {
    return global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches;
  };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      // Rest = page palette (ground ground, ink text); the class flips to the inverse.
      // Both states are the same ink/ground pair, so contrast is identical either way.
      '[data-ad-valediction]{background-color:' + GROUND + ';color:' + INK + ';' +
      'transition:background-color ' + TRANSIT + ',color ' + TRANSIT + ';}' +
      '[data-ad-valediction].' + FLIP + '{background-color:' + INK + ';color:' + GROUND + ';}' +
      // Links follow the foreground pole so they stay legible through the flip.
      '[data-ad-valediction] a{color:inherit;}' +
      // The mark is a clip box; its inner line rises out of the mask on reveal.
      '[data-ad-valediction] ' + MARK_SEL + '{overflow:hidden;}' +
      '[data-ad-valediction] .' + INNER_CLASS + '{display:block;}' +
      // Reduced motion → land on the finished (flipped) state with no animation.
      '@media (prefers-reduced-motion:reduce){[data-ad-valediction]{transition:none;}}';
    document.head.appendChild(s);
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-valediction]';
    var threshold = opts.threshold != null ? opts.threshold : 0.3;
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

    function arm(footer) {
      if (reduce()) {
        // Finished state instantly: flipped palette, mark shown, nothing to observe.
        footer.classList.add(FLIP);
        footer.setAttribute(REVEALED, '');
        return;
      }
      var mark = footer.querySelector(MARK_SEL);
      if (!mark || footer.__adMarkHTML != null) return;
      // Preserve the original so destroy() rebuilds from truth.
      footer.__adMarkHTML = mark.innerHTML;
      var inner = document.createElement('span');
      inner.className = INNER_CLASS;
      while (mark.firstChild) inner.appendChild(mark.firstChild);
      mark.appendChild(inner);
      footer.__adMarkInner = inner;
      // JS-applied hidden state → no-JS/dead-script render stays visible.
      inner.style.transform = 'translateY(100%)';
    }

    function play(footer) {
      if (footer.getAttribute(REVEALED) != null) return;
      footer.setAttribute(REVEALED, '');
      footer.classList.add(FLIP); // pure-CSS palette transition
      var inner = footer.__adMarkInner;
      if (!inner) return;
      var s = styles();
      inner.style.willChange = 'transform';
      function settle() {
        inner.style.transform = 'translateY(0)';
        inner.style.willChange = '';
      }
      if (inner.animate) {
        inner.animate(
          [{ transform: 'translateY(100%)' }, { transform: 'translateY(0)' }],
          { duration: parseFloat(s.dur), easing: s.ease, fill: 'forwards' }
        ).onfinish = settle;
      } else {
        inner.addEventListener('transitionend', settle, { once: true });
        inner.style.transition = 'transform ' + s.dur + ' ' + s.ease;
        inner.style.transform = 'translateY(0)';
      }
    }

    els.forEach(arm);

    if (reduce()) {
      // arm() already applied the finished state; observe nothing.
    } else if ('IntersectionObserver' in global) {
      io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) { play(e.target); io.unobserve(e.target); }
        });
      }, { threshold: threshold });
      els.forEach(function (footer) { io.observe(footer); });
    } else {
      els.forEach(play); // no IO → show finished immediately
    }

    return {
      destroy: function () {
        if (io) io.disconnect();
        els.forEach(function (footer) {
          footer.classList.remove(FLIP);
          footer.removeAttribute(REVEALED);
          var mark = footer.querySelector(MARK_SEL);
          if (mark && footer.__adMarkHTML != null) { mark.innerHTML = footer.__adMarkHTML; }
          delete footer.__adMarkHTML;
          delete footer.__adMarkInner;
        });
        var s = document.getElementById(CSS_ID);
        if (s) s.parentNode.removeChild(s);
      }
    };
  }

  global.awardValediction = { init: init };
})(typeof window !== 'undefined' ? window : this);
