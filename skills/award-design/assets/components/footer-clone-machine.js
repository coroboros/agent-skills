/*
 * footer-clone-machine — the studio-index deferred peak (winner: Eloy
 * Benoffi, Codrops-verified to the number — the best-sourced mechanic in the
 * brutalist corpus). Mousemove inside the footer clones the primary CTA up
 * to 200 copies, positioned absolutely at random offsets quantized to ~200px
 * steps, each under mix-blend-mode:difference so the copies interfere; on
 * mouseleave the clones animate out — opacity 0, scale 0.6, duration 0.2s,
 * ease back.in(1.7), stagger {amount:0.4, from:'random'}. The payoff is an
 * unbounded interference field where the loudest interaction lands LAST —
 * the withheld CTA the identity-terminal hero deferred finally activates
 * here. Fine-pointer only: on touch (and under reduced motion) the footer
 * is simply its authored static reprised CTA — the component is a no-op.
 * The field clips its own storm (overflow:hidden — clones never bleed
 * across the section boundary) and every clone is presentation-only:
 * aria-hidden, pointer-events:none, untabbable, ids stripped. The real CTA
 * keeps its focus and action untouched.
 *
 * Expected markup — the CTA is the builder's real link, never invented:
 *   <footer data-ad-clone-machine>
 *     <a data-ad-clone-cta href="…">Let's talk</a>
 *   </footer>
 *
 * Usage:  awardFooterCloneMachine.init(root, opts)
 *   root         Element|Document  scope (default document)
 *   selector     string  the field (default '[data-ad-clone-machine]')
 *   ctaSelector  string  the CTA to clone (default '[data-ad-clone-cta]')
 *   max          number  clone cap (default 200 — the winner's ceiling)
 *   step         px      offset quantum (default 200 — the winner's grid)
 *   travel       px      pointer travel between spawns (default 48)
 * Returns { destroy() }. Idempotent per field. destroy() removes every
 * clone, the listeners, and the stylesheet.
 *
 * Tokens: none — the clones are the build's own CTA, verbatim; the
 * interference is mix-blend-mode's, not a palette invention.
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-footer-clone-machine-css';
  var EXIT_MS = 200;                     // the winner's duration 0.2
  var EXIT_STAGGER_MS = 400;             // the winner's stagger amount 0.4, from random
  var EXIT_EASE = 'cubic-bezier(0.36, 0, 0.66, -0.56)'; // back.in(1.7)

  var reduce = function () {
    return global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches;
  };
  var finePointer = function () {
    return global.matchMedia && global.matchMedia('(hover: hover) and (pointer: fine)').matches;
  };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      // the field clips its own storm — clones never cross the section boundary
      '.ad-clonem{position:relative;overflow:hidden;}' +
      '.ad-clonem__clone{position:absolute;left:0;top:0;margin:0;' +
      'mix-blend-mode:difference;pointer-events:none;will-change:transform,opacity;}';
    document.head.appendChild(s);
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    // Touch and reduced motion get the authored footer: a static reprised CTA.
    if (reduce() || !finePointer()) return { destroy: function () {} };

    var selector = opts.selector || '[data-ad-clone-machine]';
    var ctaSelector = opts.ctaSelector || '[data-ad-clone-cta]';
    var max = opts.max != null ? opts.max : 200;
    var step = opts.step != null ? opts.step : 200;
    var travel = opts.travel != null ? opts.travel : 48;

    injectCss();

    var fields = [];
    Array.prototype.forEach.call(root.querySelectorAll(selector), function (field) {
      if (field.__adCloneMachine) return; // idempotent
      var cta = field.querySelector(ctaSelector);
      if (!cta) return;

      field.classList.add('ad-clonem');
      var clones = [];
      var lastX = 0, lastY = 0, armed = false;

      function spawn(x, y) {
        if (clones.length >= max) return; // the winner's 200-copy ceiling
        var clone = cta.cloneNode(true);
        clone.classList.add('ad-clonem__clone');
        clone.setAttribute('aria-hidden', 'true');
        clone.setAttribute('tabindex', '-1');
        clone.removeAttribute('id');
        Array.prototype.forEach.call(clone.querySelectorAll('[id]'), function (n) {
          n.removeAttribute('id');
        });
        // random offsets in ~step-sized quanta around the pointer
        var ox = (Math.floor(Math.random() * 3) - 1) * step;
        var oy = (Math.floor(Math.random() * 3) - 1) * step;
        var place = 'translate3d(' + Math.round(x + ox) + 'px,' + Math.round(y + oy) + 'px,0)';
        clone.style.transform = place;
        clone.__adPlace = place;
        field.appendChild(clone);
        clones.push(clone);
      }

      function onMove(e) {
        var r = field.getBoundingClientRect();
        var x = e.clientX - r.left, y = e.clientY - r.top;
        if (!armed) { armed = true; lastX = x; lastY = y; spawn(x, y); return; }
        var dx = x - lastX, dy = y - lastY;
        // distance-throttled: one clone per `travel` px of pointer travel
        if (dx * dx + dy * dy >= travel * travel) {
          lastX = x; lastY = y;
          spawn(x, y);
        }
      }

      function onLeave() {
        armed = false;
        var out = clones;
        clones = [];
        out.forEach(function (clone) {
          if (!clone.animate) {
            if (clone.parentNode) clone.parentNode.removeChild(clone);
            return;
          }
          var place = clone.__adPlace || '';
          var anim = clone.animate(
            [{ opacity: 1, transform: place + ' scale(1)' },
             { opacity: 0, transform: place + ' scale(0.6)' }],
            { duration: EXIT_MS, easing: EXIT_EASE, fill: 'forwards',
              delay: Math.random() * EXIT_STAGGER_MS }
          );
          anim.onfinish = function () {
            if (clone.parentNode) clone.parentNode.removeChild(clone);
          };
        });
      }

      field.addEventListener('pointermove', onMove, { passive: true });
      field.addEventListener('pointerleave', onLeave);

      field.__adCloneMachine = true;
      fields.push({
        field: field,
        destroy: function () {
          field.removeEventListener('pointermove', onMove);
          field.removeEventListener('pointerleave', onLeave);
          clones.forEach(function (c) { if (c.parentNode) c.parentNode.removeChild(c); });
          Array.prototype.forEach.call(field.querySelectorAll('.ad-clonem__clone'), function (c) {
            if (c.parentNode) c.parentNode.removeChild(c);
          });
          field.classList.remove('ad-clonem');
          delete field.__adCloneMachine;
        }
      });
    });

    return {
      destroy: function () {
        fields.forEach(function (f) { f.destroy(); });
        var s = document.getElementById(CSS_ID);
        if (s && s.parentNode) s.parentNode.removeChild(s);
      }
    };
  }

  global.awardFooterCloneMachine = { init: init };
})(typeof window !== 'undefined' ? window : this);
