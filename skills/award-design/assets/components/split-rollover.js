/*
 * split-rollover — per-character clip rollover (winner: Lando Norris, Cuberto).
 * Each character of a nav link or short label sits in its own overflow-clip box
 * holding the glyph twice, the real face above an aria-hidden duplicate below. On
 * hover or :focus-visible the stack rolls up translateY(-100%) with a left-to-right
 * per-char stagger, so the label turns over character by character and reverses on
 * leave. The split is applied by JS only, so a dead script or no-JS render shows
 * plain legible text; the motion lives entirely in one CSS :hover/:focus-visible
 * rule, so there are no per-frame JS listeners to leak.
 *
 * Usage:  awardSplitRollover.init(root, { selector, stagger })
 *   root      Element|Document  scope (default document)
 *   selector  string            elements to split (default '[data-ad-rollover]')
 *   stagger   ms per character   (default 22)
 * Returns { destroy() }. Idempotent.
 *
 * Tokens: --ad-dur-base (420ms), --ad-ease-signature (cubic-bezier(.16,1,.3,1)),
 *   --ad-accent (reduced-motion hover/focus color).
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-split-rollover-css';
  var reduce = function () {
    return global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches;
  };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      '.ad-roll__char{display:inline-block;overflow:hidden;vertical-align:top;}' +
      '.ad-roll__inner{display:inline-block;position:relative;will-change:transform;' +
      'transition:transform var(--ad-dur-base,420ms) ' +
      'var(--ad-ease-signature,cubic-bezier(.16,1,.3,1));' +
      'transition-delay:calc(var(--ad-i,0) * var(--ad-roll-stagger,22ms));}' +
      '.ad-roll__face{display:block;}' +
      '.ad-roll__face--dup{position:absolute;left:0;top:100%;}' +
      '[data-ad-rollover]:hover .ad-roll__inner,' +
      '[data-ad-rollover]:focus-visible .ad-roll__inner{transform:translateY(-100%);}' +
      '@media (prefers-reduced-motion:reduce){' +
      '.ad-roll__inner{transition:none;}' +
      '[data-ad-rollover]:hover .ad-roll__inner,' +
      '[data-ad-rollover]:focus-visible .ad-roll__inner{transform:none;}' +
      '[data-ad-rollover]:hover,[data-ad-rollover]:focus-visible' +
      '{color:var(--ad-accent,oklch(62% 0.2 25));}}';
    document.head.appendChild(s);
  }

  function splitChars(el) {
    // Preserve the original so destroy()/re-init rebuild from truth, not from an
    // already-split DOM.
    if (el.__adRollHTML == null) el.__adRollHTML = el.innerHTML;
    else el.innerHTML = el.__adRollHTML;

    var text = el.textContent.replace(/\s+/g, ' ').trim();
    if (!text) return;
    // Per-char boxes fragment the accessible name into "W o r k"; name the element
    // with the whole word so a screen reader reads it intact. Respect an author label.
    if (!el.hasAttribute('aria-label')) { el.setAttribute('aria-label', text); el.__adRollLabeled = true; }
    el.textContent = '';

    var i = 0; // rolling-char index — drives the left-to-right stagger; spaces skip it
    for (var c = 0; c < text.length; c++) {
      var ch = text.charAt(c);
      if (ch === ' ') {
        el.appendChild(document.createTextNode(' ')); // non-clipped word gap
        continue;
      }
      var box = document.createElement('span');
      box.className = 'ad-roll__char';
      var inner = document.createElement('span');
      inner.className = 'ad-roll__inner';
      inner.style.setProperty('--ad-i', String(i));
      var real = document.createElement('span');
      real.className = 'ad-roll__face';
      real.textContent = ch;
      var dup = document.createElement('span');
      dup.className = 'ad-roll__face ad-roll__face--dup';
      dup.setAttribute('aria-hidden', 'true'); // visible copy must not double SR text
      dup.textContent = ch;
      inner.appendChild(real);
      inner.appendChild(dup);
      box.appendChild(inner);
      el.appendChild(box);
      i++;
    }
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-rollover]';
    var stagger = opts.stagger != null ? opts.stagger : 22;
    injectCss();

    var els = Array.prototype.slice.call(root.querySelectorAll(selector));
    // Under reduce the resting text stays whole (no split) — CSS shifts color on
    // hover/focus instead. Otherwise split into per-char clip boxes.
    if (!reduce()) {
      els.forEach(function (el) {
        el.style.setProperty('--ad-roll-stagger', stagger + 'ms');
        splitChars(el);
      });
    }

    return {
      destroy: function () {
        els.forEach(function (el) {
          if (el.__adRollHTML != null) { el.innerHTML = el.__adRollHTML; delete el.__adRollHTML; }
          if (el.__adRollLabeled) { el.removeAttribute('aria-label'); delete el.__adRollLabeled; }
          el.style.removeProperty('--ad-roll-stagger');
        });
        var css = document.getElementById(CSS_ID);
        if (css) css.parentNode.removeChild(css);
      }
    };
  }

  global.awardSplitRollover = { init: init };
})(typeof window !== 'undefined' ? window : this);
