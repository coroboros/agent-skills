/*
 * conic-border-shine — the cursor-tracked border light (winners: Vercel,
 * Supabase — the bento/product card edge that lights where the pointer is).
 * A radial accent glow lives INSIDE the card's border ring (masked to the
 * 1px edge, never the fill) and follows the pointer across the card; it
 * fades in on enter and out on leave. Fine-pointer only — under touch the
 * card keeps its static hairline, which is the complete resting look.
 *
 * Usage:  awardBorderShine.init(root, { selector, radius })
 *   <article data-ad-shine> … </article>
 *   radius  px of the glow spot (default 220)
 * Returns { destroy() }. Idempotent. No-JS: the static hairline border only.
 * Reduced-motion: no shine at all (a pointer-tracked light is motion).
 *
 * Perf: pointermove writes two CSS custom properties, rAF-batched; the ring
 * paints via mask-composite on a ::before that only transitions opacity.
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-border-shine-css';
  var reduce = function () {
    return global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches;
  };
  var fine = function () {
    return global.matchMedia && global.matchMedia('(pointer: fine)').matches;
  };

  function injectCss(radius) {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      '.ad-shine{position:relative;border:1px solid ' +
      'color-mix(in oklch, var(--ad-ink,oklch(96% 0 0)) 12%, transparent);}' +
      '.ad-shine::before{content:"";position:absolute;inset:-1px;border-radius:inherit;' +
      'padding:1px;opacity:0;pointer-events:none;' +
      'background:radial-gradient(' + radius + 'px circle at var(--_sx,50%) var(--_sy,50%),' +
      'var(--ad-accent,oklch(62% 0.2 25)),transparent 70%);' +
      '-webkit-mask:linear-gradient(#fff 0 0) content-box,linear-gradient(#fff 0 0);' +
      '-webkit-mask-composite:xor;' +
      'mask:linear-gradient(#fff 0 0) content-box,linear-gradient(#fff 0 0);' +
      'mask-composite:exclude;' +
      'transition:opacity var(--ad-dur-base,420ms) var(--ad-ease-signature,cubic-bezier(.16,1,.3,1));}' +
      '.ad-shine.is-lit::before{opacity:1;}' +
      '@media (prefers-reduced-motion:reduce){.ad-shine::before{display:none;}}';
    document.head.appendChild(s);
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-shine]';
    injectCss(opts.radius != null ? opts.radius : 220);

    var els = Array.prototype.slice.call(root.querySelectorAll(selector));
    var bindings = [];
    els.forEach(function (el) { el.classList.add('ad-shine'); });

    if (fine() && !reduce()) {
      els.forEach(function (el) {
        var rafId = 0, px = 0, py = 0;
        var move = function (e) {
          px = e.clientX; py = e.clientY;
          if (!rafId) rafId = global.requestAnimationFrame(function () {
            rafId = 0;
            var r = el.getBoundingClientRect();
            el.style.setProperty('--_sx', ((px - r.left) / Math.max(1, r.width) * 100).toFixed(2) + '%');
            el.style.setProperty('--_sy', ((py - r.top) / Math.max(1, r.height) * 100).toFixed(2) + '%');
          });
        };
        var enter = function () { el.classList.add('is-lit'); };
        var leave = function () { el.classList.remove('is-lit'); };
        el.addEventListener('pointermove', move, { passive: true });
        el.addEventListener('pointerenter', enter);
        el.addEventListener('pointerleave', leave);
        bindings.push({ el: el, move: move, enter: enter, leave: leave, raf: function () { return rafId; } });
      });
    }

    return {
      destroy: function () {
        bindings.forEach(function (b) {
          b.el.removeEventListener('pointermove', b.move);
          b.el.removeEventListener('pointerenter', b.enter);
          b.el.removeEventListener('pointerleave', b.leave);
          if (b.raf()) global.cancelAnimationFrame(b.raf());
        });
        els.forEach(function (el) {
          el.classList.remove('ad-shine', 'is-lit');
          el.style.removeProperty('--_sx');
          el.style.removeProperty('--_sy');
        });
        var s = document.getElementById(CSS_ID);
        if (s) s.parentNode.removeChild(s);
      }
    };
  }

  global.awardBorderShine = { init: init };
})(typeof window !== 'undefined' ? window : this);
