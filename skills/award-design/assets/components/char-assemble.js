/*
 * char-assemble — masked per-character heading assemble (winner: Stefan Vitasović).
 * Each character of a short display line sits in its own overflow-clip box; the
 * glyph starts translated below its mask with a slight bottom-left rotation and
 * rises to rest on scroll-into-view, staggered left to right, rotation settling
 * to 0. The split and hidden state are applied by JS only, so a dead script or
 * no-JS render shows plain legible text. No resize re-split: spaces stay real
 * text nodes between the char boxes, so the heading re-wraps naturally at any
 * width and a char box never spans a line break — nothing needs re-measuring.
 *
 * Usage:  awardCharAssemble.init(root, { selector, stagger, threshold })
 *   root      Element|Document  scope (default document)
 *   selector  string            elements to split (default '[data-ad-assemble]')
 *   stagger   ms per character  (default 28)
 *   threshold IO threshold      (default 0.3)
 * Returns { destroy() }. Idempotent. Plays once per element.
 *
 * Tokens: --ad-dur-reveal (800ms), --ad-ease-signature (cubic-bezier(.16,1,.3,1)).
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-char-assemble-css';
  var HIDDEN = 'translate3d(0,110%,0) rotate(6deg)';
  var SHOWN = 'translate3d(0,0,0) rotate(0deg)';
  var reduce = function () {
    return global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches;
  };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      '.ad-asm__char{display:inline-block;overflow:hidden;vertical-align:top;}' +
      '.ad-asm__in{display:inline-block;will-change:transform;transform-origin:0% 100%;}';
    document.head.appendChild(s);
  }

  function splitChars(el) {
    // Preserve the original so destroy()/re-init rebuild from truth, not from an
    // already-split DOM.
    if (el.__adAsmHTML == null) el.__adAsmHTML = el.innerHTML;
    else el.innerHTML = el.__adAsmHTML;

    var text = el.textContent.replace(/\s+/g, ' ').trim();
    if (!text) return [];
    // Per-char boxes fragment the accessible name into "W o r k"; name the element
    // with the whole text so a screen reader reads it intact. Respect an author label.
    if (!el.hasAttribute('aria-label')) { el.setAttribute('aria-label', text); el.__adAsmLabeled = true; }
    el.textContent = '';

    var inners = [];
    for (var c = 0; c < text.length; c++) {
      var ch = text.charAt(c);
      if (ch === ' ') {
        // Real space text node BETWEEN the boxes — a space inside an inline-block
        // is not a break opportunity, so word gaps stay outside the clip boxes.
        el.appendChild(document.createTextNode(' '));
        continue;
      }
      var box = document.createElement('span');
      box.className = 'ad-asm__char';
      var inner = document.createElement('span');
      inner.className = 'ad-asm__in';
      inner.textContent = ch;
      box.appendChild(inner);
      el.appendChild(box);
      inners.push(inner);
    }
    return inners;
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-assemble]';
    var stagger = opts.stagger != null ? opts.stagger : 28;
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

    function arm(el) {
      el.__adAsmInners = splitChars(el);
      // JS-applied hidden state → no-JS/dead-script render stays visible.
      el.__adAsmInners.forEach(function (inner) { inner.style.transform = HIDDEN; });
    }

    function play(el) {
      if (el.getAttribute('data-ad-revealed') != null) return;
      el.setAttribute('data-ad-revealed', '');
      var s = styles();
      (el.__adAsmInners || []).forEach(function (inner, i) {
        if (inner.animate) {
          inner.animate(
            [{ transform: HIDDEN }, { transform: SHOWN }],
            { duration: parseFloat(s.dur), easing: s.ease, delay: i * stagger, fill: 'forwards' }
          ).onfinish = function () { inner.style.transform = SHOWN; };
        } else {
          inner.style.transition = 'transform ' + s.dur + ' ' + s.ease + ' ' + (i * stagger) + 'ms';
          inner.style.transform = SHOWN;
        }
      });
    }

    // Under reduce the text is never split — it stays whole and visible at rest.
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
    }

    return {
      destroy: function () {
        if (io) io.disconnect();
        els.forEach(function (el) {
          if (el.__adAsmHTML != null) { el.innerHTML = el.__adAsmHTML; delete el.__adAsmHTML; }
          if (el.__adAsmLabeled) { el.removeAttribute('aria-label'); delete el.__adAsmLabeled; }
          el.removeAttribute('data-ad-revealed');
          delete el.__adAsmInners;
        });
        var css = document.getElementById(CSS_ID);
        if (css) css.parentNode.removeChild(css);
      }
    };
  }

  global.awardCharAssemble = { init: init };
})(typeof window !== 'undefined' ? window : this);
