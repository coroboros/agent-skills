/*
 * faq-accordion enhancer — smooth open/close for the faq-accordion section
 * form. The rows work natively with zero script (<details>/<summary> — the
 * no-JS render is fully operable); this enhancer only eases the disclosure:
 * on open the answer grows from 0 to its measured height and fades in, on
 * close it shrinks back before [open] is removed. Height is animated here by
 * exception to the transform/opacity rule — a disclosure IS a layout change;
 * the animation is a one-shot on a user action, never a per-frame or
 * scroll-tied write, so there is no thrash to avoid. Layering law: the
 * enhancer toggles [open] and animates the documented answer slot; it never
 * restructures a slot's inner DOM. Under reduced motion (or without WAAPI)
 * it stands aside entirely — native instant disclosure.
 *
 * Usage:  awardFaqAccordion.init(root, { selector })
 *   root      Element|Document  scope (default document)
 *   selector  string            form roots (default '[data-ad-form="faq-accordion"]')
 * Returns { destroy() }. Idempotent per form root. destroy() unhooks the
 * click interception and cancels any in-flight animation; open state is left
 * as the user set it. Styling lives in forms/faq-accordion.css (linked, not
 * injected — the form's layout must survive a dead script).
 *
 * Tokens: --ad-dur-base (420ms) + --ad-ease-signature
 * (cubic-bezier(.16,1,.3,1)) time the disclosure.
 */
(function (global) {
  'use strict';

  var reduce = function () {
    return global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches;
  };

  function styles() {
    var cs = getComputedStyle(document.documentElement);
    function v(name, fallback) {
      return (cs.getPropertyValue(name) || '').trim() || fallback;
    }
    return {
      dur: parseFloat(v('--ad-dur-base', '420ms')) || 420,
      ease: v('--ad-ease-signature', 'cubic-bezier(.16,1,.3,1)')
    };
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-form="faq-accordion"]';

    var forms = [];
    Array.prototype.forEach.call(root.querySelectorAll(selector), function (form) {
      if (form.__adFaq) return;
      form.__adFaq = true;

      function onClick(e) {
        var summary = e.target.closest ? e.target.closest('summary') : null;
        if (!summary || !form.contains(summary)) return;
        var item = summary.parentElement;
        if (!item || item.getAttribute('data-slot') !== 'item') return;
        var answer = item.querySelector('[data-item-a]');
        // native instant disclosure when motion is off or WAAPI is missing
        if (!answer || !answer.animate || reduce()) return;
        e.preventDefault();
        if (item.__adFaqAnim) item.__adFaqAnim.cancel();
        var s = styles();
        // paddings ride the keyframes too: with border-box the height floor
        // is the padding, so height alone would stop short and snap the tail
        var pb = getComputedStyle(answer).paddingBottom;
        if (item.open) {
          // close: shrink first, then drop [open] so content never snaps away
          var h0 = answer.getBoundingClientRect().height;
          var closing = answer.animate(
            [{ height: h0 + 'px', paddingBottom: pb, opacity: 1, overflow: 'hidden' },
             { height: '0px', paddingBottom: '0px', opacity: 0, overflow: 'hidden' }],
            { duration: s.dur, easing: s.ease }
          );
          item.__adFaqAnim = closing;
          closing.onfinish = function () {
            item.__adFaqAnim = null;
            item.open = false;
          };
        } else {
          item.open = true;
          var h1 = answer.getBoundingClientRect().height;
          var opening = answer.animate(
            [{ height: '0px', paddingBottom: '0px', opacity: 0, overflow: 'hidden' },
             { height: h1 + 'px', paddingBottom: pb, opacity: 1, overflow: 'hidden' }],
            { duration: s.dur, easing: s.ease }
          );
          item.__adFaqAnim = opening;
          opening.onfinish = function () { item.__adFaqAnim = null; };
        }
      }

      form.addEventListener('click', onClick);
      forms.push({ form: form, onClick: onClick });
    });

    return {
      destroy: function () {
        forms.forEach(function (f) {
          f.form.removeEventListener('click', f.onClick);
          Array.prototype.forEach.call(
            f.form.querySelectorAll('[data-slot="item"]'),
            function (item) {
              if (item.__adFaqAnim) { item.__adFaqAnim.cancel(); item.__adFaqAnim = null; }
            }
          );
          delete f.form.__adFaq;
        });
        forms.length = 0;
      }
    };
  }

  global.awardFaqAccordion = { init: init };
})(typeof window !== 'undefined' ? window : this);
