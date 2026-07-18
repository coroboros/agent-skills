/*
 * type-index-grid enhancer — the boot and the index→ground bridge (union
 * order: Aristide Benoist / Obys / Lusion v3, the experimental gap's
 * masked-row grammar, over the spatial-organic type-index arc). The form's
 * CSS owns the layout; this enhancer owns the two mechanics so the
 * stylesheet ships zero motion and hides nothing:
 *
 * (1) BOOT — each row's cells rise masked, translate3d(0,101%,0) -> 0 (the
 *     gap's own reveal), staggered per row and per cell, fire-ONCE when the
 *     index enters the viewport; done as a WAAPI play with fill:backwards
 *     (the fill covers only the stagger delay; past the finish each cell
 *     rests on its authored CSS) — a dead or absent script leaves the
 *     whole index standing (nothing was ever hidden in CSS).
 *     The root carries data-ad-tig-boot only while the reveal runs (the
 *     CSS scopes will-change to that window).
 *
 * (2) BRIDGE — 'the whole page is the index': on row pointerenter/focusin
 *     the enhancer publishes the row's index on the ROOT as
 *     data-ad-tig-hover="<i>" (removed on leave), a discrete write on
 *     change only, so the live ground (shader-surface skin, image field,
 *     build CSS) keys its imagery off the hovered row. The row HOVER
 *     grammar itself — material line, sibling dim, surfaced meta — is the
 *     paired index-row-hover's job (the recipes' own pairing), never
 *     duplicated here.
 *
 * Rows stay REAL links: no click handler exists in this file — the on-click
 * route-morph climax is webgl-scene(delegated) territory, wired by the
 * build, and navigation is never intercepted (the diegetic-nav law).
 *
 * Usage:  awardTypeIndexGrid.init(root, opts)
 *   root      Element|Document  scope (default document)
 *   selector  string  form roots (default '[data-ad-form="type-index-grid"]')
 * Returns { destroy() }. Idempotent per root. destroy() cancels the boot,
 * clears the published attributes, and unbinds.
 *
 * Reduced motion: init binds only the bridge — no boot, no seed, the
 * authored index IS the fold from the first frame.
 * Layering law kept: attribute writes on the root + WAAPI plays on authored
 * row cells only; no nodes created, no inner-DOM surgery, no stylesheet
 * injected.
 * Tokens read: --ad-dur-reveal + --ad-ease-signature (the boot's clock).
 */
(function (global) {
  'use strict';
  var ROW_STAGGER = 70;   // ms between row starts — the cascade reads as one wall rising
  var CELL_STAGGER = 45;  // ms between a row's no/title/meta cells

  var reduce = function () {
    return !!(global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches);
  };

  function styles() {
    var cs = getComputedStyle(document.documentElement);
    function v(name, fallback) {
      return (cs.getPropertyValue(name) || '').trim() || fallback;
    }
    return {
      dur: parseFloat(v('--ad-dur-reveal', '800')) || 800,
      ease: v('--ad-ease-signature', 'cubic-bezier(.16,1,.3,1)')
    };
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-form="type-index-grid"]';
    if (root.__adTypeIndexGrid) return root.__adTypeIndexGrid;

    var still = reduce();
    var units = [];

    Array.prototype.forEach.call(root.querySelectorAll(selector), function (section) {
      var rows = Array.prototype.slice.call(
        section.querySelectorAll('[data-slot="row"]'));
      var u = { section: section, rows: rows, anims: [], booted: still, io: null,
                hovers: [] };
      units.push(u);

      // (2) the bridge — discrete root writes, one per change
      rows.forEach(function (row, i) {
        var over = function () {
          if (section.getAttribute('data-ad-tig-hover') !== String(i)) {
            section.setAttribute('data-ad-tig-hover', String(i));
          }
        };
        var out = function () {
          if (row.matches(':focus-within')) return;
          if (section.getAttribute('data-ad-tig-hover') === String(i)) {
            section.removeAttribute('data-ad-tig-hover');
          }
        };
        row.addEventListener('pointerenter', over);
        row.addEventListener('pointerleave', out);
        row.addEventListener('focusin', over);
        row.addEventListener('focusout', out);
        u.hovers.push({ row: row, over: over, out: out });
      });

      if (still) return; // the authored index IS the fold

      // (1) the boot — seed inline, play once on first view
      var s = styles();
      function boot() {
        if (u.booted) return;
        u.booted = true;
        section.setAttribute('data-ad-tig-boot', '');
        var pending = 0;
        u.rows.forEach(function (row, r) {
          Array.prototype.forEach.call(row.children, function (cell, c) {
            if (!cell.animate) { return; }
            pending++;
            var a = cell.animate(
              [{ transform: 'translate3d(0,101%,0)' },
               { transform: 'translate3d(0,0,0)' }],
              { duration: s.dur, delay: r * ROW_STAGGER + c * CELL_STAGGER,
                easing: s.ease, fill: 'backwards' });
            u.anims.push(a);
            a.onfinish = function () {
              if (--pending === 0) section.removeAttribute('data-ad-tig-boot');
            };
          });
        });
        if (!pending) section.removeAttribute('data-ad-tig-boot');
        if (u.io) { u.io.disconnect(); u.io = null; }
      }
      if ('IntersectionObserver' in global) {
        u.io = new IntersectionObserver(function (entries) {
          entries.forEach(function (e) { if (e.isIntersecting) boot(); });
        }, { threshold: 0.15 });
        u.io.observe(section);
      } else {
        boot();
      }
    });

    var handle = {
      destroy: function () {
        units.forEach(function (u) {
          if (u.io) u.io.disconnect();
          u.anims.forEach(function (a) { a.onfinish = null; a.cancel(); });
          u.hovers.forEach(function (h) {
            h.row.removeEventListener('pointerenter', h.over);
            h.row.removeEventListener('pointerleave', h.out);
            h.row.removeEventListener('focusin', h.over);
            h.row.removeEventListener('focusout', h.out);
          });
          u.section.removeAttribute('data-ad-tig-boot');
          u.section.removeAttribute('data-ad-tig-hover');
        });
        units = [];
        if (root.__adTypeIndexGrid === handle) delete root.__adTypeIndexGrid;
      }
    };
    root.__adTypeIndexGrid = handle;
    return handle;
  }

  global.awardTypeIndexGrid = { init: init };
})(typeof window !== 'undefined' ? window : this);
