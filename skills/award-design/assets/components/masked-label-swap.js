/*
 * masked-label-swap — clipped two-line label swap (winner: Siena Film Foundation, CTA hover).
 * A button/link's text label sits in an overflow-clip box over two stacked copies —
 * the real label on top, an aria-hidden duplicate directly below. On hover or
 * :focus-visible the pair translates up one line: the top label wipes out while the
 * duplicate rises into place, a hard-edged swap. Content is fully legible at rest and
 * under reduced-motion; the clip + duplicate are added by JS only, so a dead script or
 * no-JS render shows the plain label.
 *
 * Usage:  awardLabelSwap.init(root, { selector })
 *   root      Element|Document  scope (default document)
 *   selector  string            controls to wrap (default '[data-ad-swap]')
 * Returns { destroy() }. Idempotent.
 *
 * Tokens: --ad-dur-base (420ms), --ad-ease-strike (cubic-bezier(.7,.02,.28,1)),
 *         --ad-accent (oklch(62% 0.2 25), the reduced-motion hover color).
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-masked-label-swap-css';
  var ACCENT_FALLBACK = 'oklch(62% 0.2 25)';
  var reduce = function () {
    return global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches;
  };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      '.ad-swap{display:inline-block;overflow:hidden;white-space:nowrap;vertical-align:top;}' +
      '.ad-swap__in{display:block;position:relative;will-change:transform;' +
        'transition:transform var(--ad-dur-base,420ms) var(--ad-ease-strike,cubic-bezier(.7,.02,.28,1));}' +
      '.ad-swap__b{position:absolute;left:0;top:100%;}' +
      '@media (prefers-reduced-motion:reduce){.ad-swap__in{transition:none;}}';
    document.head.appendChild(s);
  }

  function accent(el) {
    var v = getComputedStyle(el).getPropertyValue('--ad-accent').trim();
    return v || ACCENT_FALLBACK;
  }

  function wrap(el) {
    // Preserve the original so destroy()/re-init can rebuild from truth.
    if (el.__adSwapHTML == null) el.__adSwapHTML = el.innerHTML;
    else el.innerHTML = el.__adSwapHTML;

    var label = el.textContent.replace(/\s+/g, ' ').trim();
    if (!label) return null;

    el.textContent = '';
    var clip = document.createElement('span');
    clip.className = 'ad-swap';
    var inner = document.createElement('span');
    inner.className = 'ad-swap__in';

    var a = document.createElement('span'); // resting label — the real, accessible text
    a.className = 'ad-swap__a';
    a.textContent = label;

    var b = document.createElement('span'); // duplicate that rises into place, hidden from AT
    b.className = 'ad-swap__b';
    b.setAttribute('aria-hidden', 'true');
    b.textContent = label;

    inner.appendChild(a);
    inner.appendChild(b);
    clip.appendChild(inner);
    el.appendChild(clip);
    return inner;
  }

  function bind(el, inner) {
    var state = { hover: false, focus: false };

    function render() {
      var on = state.hover || state.focus;
      if (on && reduce()) {
        // reduced motion: no translate, an instant color shift toward the accent.
        inner.style.transform = '';
        el.style.color = accent(el);
      } else if (on) {
        el.style.color = '';
        inner.style.transform = 'translateY(-100%)';
      } else {
        inner.style.transform = '';
        el.style.color = '';
      }
    }

    // Touch focus/hover is not :focus-visible and not a fine pointer → resting label stays.
    function onEnter(e) { if (e.pointerType === 'touch') return; state.hover = true; render(); }
    function onLeave(e) { if (e.pointerType === 'touch') return; state.hover = false; render(); }
    function onFocus() { if (el.matches(':focus-visible')) { state.focus = true; render(); } }
    function onBlur() { state.focus = false; render(); }

    el.addEventListener('pointerenter', onEnter);
    el.addEventListener('pointerleave', onLeave);
    el.addEventListener('focus', onFocus);
    el.addEventListener('blur', onBlur);

    el.__adSwapUnbind = function () {
      el.removeEventListener('pointerenter', onEnter);
      el.removeEventListener('pointerleave', onLeave);
      el.removeEventListener('focus', onFocus);
      el.removeEventListener('blur', onBlur);
      inner.style.transform = '';
      el.style.color = '';
    };
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-swap]';
    injectCss();

    var els = Array.prototype.slice.call(root.querySelectorAll(selector));
    els.forEach(function (el) {
      if (el.__adSwapUnbind) { el.__adSwapUnbind(); delete el.__adSwapUnbind; }
      var inner = wrap(el);
      if (inner) bind(el, inner);
    });

    return {
      destroy: function () {
        els.forEach(function (el) {
          if (el.__adSwapUnbind) { el.__adSwapUnbind(); delete el.__adSwapUnbind; }
          if (el.__adSwapHTML != null) { el.innerHTML = el.__adSwapHTML; delete el.__adSwapHTML; }
        });
        var s = document.getElementById(CSS_ID);
        if (s && s.parentNode) s.parentNode.removeChild(s);
      }
    };
  }

  global.awardLabelSwap = { init: init };
})(typeof window !== 'undefined' ? window : this);
