/*
 * cursor-verb-label — the cursor teaches the operable verb (canon: Awwwards
 * cursor resources — 'Customize your mouse cursor', 'Hovers, Cursors and
 * Cute Interactions', 'Drag, Gestures & Other Interactions' collections;
 * canon-documented, not single-winner-verified). Over an operable field — a
 * filmstrip, a drag-scrub video, a reel — the cursor morphs from default to
 * a verb label or glyph ('DRAG', 'HOLD', 'VIEW', '▶') that tracks the
 * pointer with a slight trail, retracting on exit. The visual teacher for
 * the verb the editorial-dark thesis hands the reader; the field-scoped
 * sibling of magnetic-cursor (which is page-level pointer chrome — the two
 * never run on the same field).
 * Touch (the documented answer): no cursor — each field carries a small
 * persistent hint chip with the same verb, so the surface is never dead.
 * Reduced motion: full stand-aside — static default cursor, the build's
 * onboarding copy alone carries the verb.
 *
 * Expected markup — operable fields declare their verb:
 *   <section data-ad-drag-scrub data-ad-cursor-verb="DRAG">…</section>
 *
 * Usage:  awardCursorVerbLabel.init(root, opts)
 *   root      Element|Document  scope (default document)
 *   selector  string  verb fields (default '[data-ad-cursor-verb]')
 *   lerp      number  pointer-follow smoothing (default 0.22)
 * Returns { destroy() }. Idempotent — one label layer per page; a second
 * init returns the live handle. destroy() restores the native cursor and
 * removes the layer, hint chips, listeners, and the stylesheet.
 *
 * A11y + perf: the label is aria-hidden and pointer-events:none — it never
 * intercepts a click or takes focus; the native cursor is hidden only while
 * a verb field is under the pointer (JS-applied class, so a dead script
 * never strands a cursorless surface). Compositor-only: one promoted fixed
 * element, transform/opacity, a rAF loop that runs only while visible or
 * still traveling.
 *
 * Tokens: --ad-ink + --ad-ground-2 (label chrome), --ad-font-mono (label
 * face), --ad-dur-base + --ad-ease-signature (morph in/out).
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-cursor-verb-label-css';

  var reduce = function () {
    return !!(global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches);
  };
  var finePointer = function () {
    return !!(global.matchMedia && global.matchMedia('(hover: hover) and (pointer: fine)').matches);
  };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      '.ad-cvl{position:fixed;left:0;top:0;z-index:2147483646;pointer-events:none;' +
      'display:inline-block;padding:.55em .9em;border-radius:999px;' +
      'background:var(--ad-ground-2,oklch(18% 0.01 260));color:var(--ad-ink,oklch(96% 0 0));' +
      'font-family:var(--ad-font-mono,ui-monospace,monospace);font-size:.7rem;' +
      'letter-spacing:.12em;text-transform:uppercase;white-space:nowrap;' +
      'will-change:transform;opacity:0;' +
      'transition:opacity var(--ad-dur-base,420ms) ' +
      'var(--ad-ease-signature,cubic-bezier(.16,1,.3,1));}' +
      '.ad-cvl.is-on{opacity:1;}' +
      // the inner span owns the morph scale so the outer transform stays the tracker's
      '.ad-cvl span{display:inline-block;transform:scale(.5);' +
      'transition:transform var(--ad-dur-base,420ms) ' +
      'var(--ad-ease-signature,cubic-bezier(.16,1,.3,1));}' +
      '.ad-cvl.is-on span{transform:scale(1);}' +
      // native cursor hides only while the label is live over a field
      '.ad-cvl-hide,.ad-cvl-hide *{cursor:none!important;}' +
      // coarse pointer: the persistent verb hint chip inside the field
      '.ad-cvl-host{position:relative;}' +
      '.ad-cvl__hint{position:absolute;left:50%;bottom:1rem;transform:translateX(-50%);' +
      'z-index:5;pointer-events:none;padding:.45em .8em;border-radius:999px;' +
      'background:var(--ad-ground-2,oklch(18% 0.01 260));color:var(--ad-ink,oklch(96% 0 0));' +
      'font-family:var(--ad-font-mono,ui-monospace,monospace);font-size:.65rem;' +
      'letter-spacing:.12em;text-transform:uppercase;white-space:nowrap;}';
    document.head.appendChild(s);
  }

  var current = null; // page-level singleton — one label layer keeps init idempotent

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    if (current) return current;
    var selector = opts.selector || '[data-ad-cursor-verb]';
    var lerpK = opts.lerp != null ? opts.lerp : 0.22;

    // Reduced motion: static default cursor + the onboarding copy alone.
    if (reduce()) return { destroy: function () {} };

    injectCss();
    var fields = Array.prototype.slice.call(root.querySelectorAll(selector));

    if (!finePointer()) {
      // ---- coarse pointer: the persistent hint chip, never a dead surface --
      var chips = [];
      fields.forEach(function (el) {
        if (el.querySelector('.ad-cvl__hint')) return;
        var chip = document.createElement('span');
        chip.className = 'ad-cvl__hint';
        chip.setAttribute('aria-hidden', 'true');
        chip.textContent = el.getAttribute('data-ad-cursor-verb') || '';
        el.classList.add('ad-cvl-host');
        el.appendChild(chip);
        chips.push({ el: el, chip: chip });
      });
      current = {
        destroy: function () {
          chips.forEach(function (c) {
            if (c.chip.parentNode) c.chip.parentNode.removeChild(c.chip);
            c.el.classList.remove('ad-cvl-host');
          });
          var s = document.getElementById(CSS_ID);
          if (s && s.parentNode) s.parentNode.removeChild(s);
          current = null;
        }
      };
      return current;
    }

    // ---- fine pointer: one trailing verb label ---------------------------
    var label = document.createElement('div');
    label.className = 'ad-cvl';
    label.setAttribute('aria-hidden', 'true');
    var text = document.createElement('span');
    label.appendChild(text);
    (document.body || document.documentElement).appendChild(label);

    var tx = 0, ty = 0, cx = 0, cy = 0, on = false;
    var raf = 0, activeField = null;

    function apply() {
      // trailing just below-right of the pointer, centered on it
      label.style.transform =
        'translate3d(' + cx.toFixed(1) + 'px,' + cy.toFixed(1) + 'px,0) translate(-50%,-50%)';
    }
    function frame() {
      raf = 0;
      cx += (tx - cx) * lerpK;
      cy += (ty - cy) * lerpK;
      apply();
      var settled = Math.abs(tx - cx) < 0.3 && Math.abs(ty - cy) < 0.3;
      // the loop runs only while shown or still traveling — no idle rAF
      if (on || !settled) raf = global.requestAnimationFrame(frame);
    }
    function wake() {
      if (!raf) raf = global.requestAnimationFrame(frame);
    }

    var bindings = [];
    fields.forEach(function (el) {
      var onEnter = function (e) {
        activeField = el;
        text.textContent = el.getAttribute('data-ad-cursor-verb') || '';
        el.classList.add('ad-cvl-hide');
        if (!on) {
          on = true;
          // first show lands at the pointer, not lerped in from 0,0
          cx = tx = e.clientX; cy = ty = e.clientY;
          apply();
          label.classList.add('is-on');
        }
        wake();
      };
      var onLeave = function () {
        el.classList.remove('ad-cvl-hide');
        if (activeField === el) {
          activeField = null;
          on = false;
          label.classList.remove('is-on'); // retract; the native cursor returns
        }
      };
      var onMove = function (e) {
        if (!on) return;
        tx = e.clientX; ty = e.clientY;
        wake();
      };
      el.addEventListener('pointerenter', onEnter);
      el.addEventListener('pointerleave', onLeave);
      el.addEventListener('pointermove', onMove, { passive: true });
      bindings.push({ el: el, enter: onEnter, leave: onLeave, move: onMove });
    });

    var onVis = function () { if (!document.hidden && (on || raf)) wake(); };
    document.addEventListener('visibilitychange', onVis);

    current = {
      destroy: function () {
        if (raf) global.cancelAnimationFrame(raf);
        document.removeEventListener('visibilitychange', onVis);
        bindings.forEach(function (b) {
          b.el.removeEventListener('pointerenter', b.enter);
          b.el.removeEventListener('pointerleave', b.leave);
          b.el.removeEventListener('pointermove', b.move);
          b.el.classList.remove('ad-cvl-hide');
        });
        if (label.parentNode) label.parentNode.removeChild(label);
        var s = document.getElementById(CSS_ID);
        if (s && s.parentNode) s.parentNode.removeChild(s);
        current = null;
      }
    };
    return current;
  }

  global.awardCursorVerbLabel = { init: init };
})(typeof window !== 'undefined' ? window : this);
