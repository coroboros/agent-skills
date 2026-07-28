/*
 * type-tester — form enhancer (winner: Exat — SOTD + FWA + CSSDA WOTM; the
 * operable-proof beat of specimen-tour-exat). What a dead script cannot do:
 * the controls WRITE the live axis vars — the gap's own names, --ff / --fs /
 * --fw / --lh / --ls — onto the preview block as the visitor drags or
 * arrow-keys the native ranges, each control's readout reflecting the value;
 * and the preview becomes an editable plaintext sample (spellcheck off,
 * named for assistive tech) so the visitor sets their own words in the
 * type — proof-by-operation, the type-tester canon. The linked form CSS
 * owns layout and the composed rest; this file injects nothing and creates
 * no nodes (the layering law). State rides data attributes on the form root
 * (data-tester-live) — never role classes.
 * prefers-reduced-motion: every write is direct state manipulation — zero
 * animation exists in this enhancer, so reduce has nothing to strip; the
 * mechanic stays fully operable (direct manipulation is exempt).
 * No JS: the composed static specimen stands; controls rest inert.
 *
 * Control contract: any [data-tester-axis="ff|fs|fw|lh|ls"] input/select in
 * the controls slot; data-tester-unit ("px", "em", …) suffixes the written
 * value; a sibling [data-tester-value] (inside the same [data-tester-control]
 * label) takes the readout. Values sync once at init so authored control
 * positions and the preview agree.
 *
 * Usage:  awardTypeTester.init(root, opts)
 *   root      Element|Document  scope (default document)
 *   selector  string  form roots (default '[data-ad-form="type-tester"]')
 * Returns { destroy() }. Idempotent per form root. destroy() unbinds,
 * restores the preview (contenteditable off, prior inline axis vars back),
 * and drops the live flag.
 */
(function (global) {
  'use strict';
  var AXES = { ff: 1, fs: 1, fw: 1, lh: 1, ls: 1 };

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-form="type-tester"]';

    var forms = [];
    Array.prototype.forEach.call(root.querySelectorAll(selector), function (el) {
      if (el.__adTypeTester) return; // idempotent per form root
      var preview = el.querySelector('[data-slot="preview"]');
      if (!preview) return;
      var controls = Array.prototype.slice.call(
        el.querySelectorAll('[data-tester-axis]')
      ).filter(function (c) { return AXES[c.getAttribute('data-tester-axis')]; });
      if (!controls.length) return;

      var f = { el: el, preview: preview, controls: controls, bindings: [], prior: {} };

      function apply(control) {
        var axis = control.getAttribute('data-tester-axis');
        var unit = control.getAttribute('data-tester-unit') || '';
        var value = control.value + (axis === 'ff' ? '' : unit);
        if (f.prior[axis] === undefined) {
          f.prior[axis] = preview.style.getPropertyValue('--' + axis);
        }
        preview.style.setProperty('--' + axis, value);
        var wrap = control.closest('[data-tester-control]');
        var out = wrap && wrap.querySelector('[data-tester-value]');
        if (out) out.textContent = value;
      }

      controls.forEach(function (control) {
        var onInput = function () { apply(control); };
        control.addEventListener('input', onInput);
        f.bindings.push({ control: control, fn: onInput });
        apply(control); // sync: authored control positions drive the rest state
      });

      // The editable sample — plaintext only, no formatting paste artifacts;
      // engines without 'plaintext-only' fall back to plain contenteditable.
      f.priorEditable = preview.getAttribute('contenteditable');
      preview.setAttribute('contenteditable', 'plaintext-only');
      if (preview.contentEditable !== 'plaintext-only') {
        preview.setAttribute('contenteditable', 'true');
      }
      preview.setAttribute('spellcheck', 'false');
      if (!preview.hasAttribute('aria-label')) {
        preview.setAttribute('aria-label', 'Type your own sample');
        f.labeled = true;
      }
      el.setAttribute('data-tester-live', '');
      el.__adTypeTester = f;
      forms.push(f);
    });
    if (!forms.length) return { destroy: function () {} };

    return {
      destroy: function () {
        forms.forEach(function (f) {
          f.bindings.forEach(function (b) {
            b.control.removeEventListener('input', b.fn);
          });
          Object.keys(f.prior).forEach(function (axis) {
            if (f.prior[axis]) f.preview.style.setProperty('--' + axis, f.prior[axis]);
            else f.preview.style.removeProperty('--' + axis);
          });
          if (f.priorEditable == null) f.preview.removeAttribute('contenteditable');
          else f.preview.setAttribute('contenteditable', f.priorEditable);
          f.preview.removeAttribute('spellcheck');
          if (f.labeled) f.preview.removeAttribute('aria-label');
          f.el.removeAttribute('data-tester-live');
          delete f.el.__adTypeTester;
        });
        forms.length = 0;
      }
    };
  }

  global.awardTypeTester = { init: init };
})(typeof window !== 'undefined' ? window : this);
