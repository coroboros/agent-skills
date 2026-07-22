/*
 * index-row-hover — the living index: hovered row lights, siblings dim, metadata
 * surfaces (winner: Depo Luxe, Son Daven, Terminal, Siena Film Foundation).
 * [data-ad-index] containers get .ad-idx and their rows .ad-idx__row; CSS draws
 * hairline dividers (14% ink border-top per row, border-bottom on the container),
 * dims every row to 45% while the container is hovered except the hovered row,
 * grows a 2px accent rule up the hovered row, seated in a reserved left gutter
 * (--ad-idx-gutter) so it stays clear of the row number (::before scaleY), and
 * cross-fades any [data-ad-row-meta] inside it from 55% to full ink with a 4px
 * shift right. :focus-within mirrors hover so a focused row link gets the same
 * spotlight; keyboard order is untouched. Coarse pointers see the clean, fully
 * legible list — the dim exists only under :hover/:focus-within.
 * Under reduced motion states apply instantly and the metadata never translates.
 *
 * Usage:  awardIndexRows.init(root, { selector, rowSelector })
 *   root         Element|Document  scope (default document)
 *   selector     string            containers to tag (default '[data-ad-index]')
 *   rowSelector  string            rows inside a container (default '[data-ad-row]');
 *                                  when it matches nothing, direct children are used
 * Returns { destroy() }. Idempotent. destroy() untags and removes the stylesheet.
 *
 * Tokens: --ad-accent, --ad-ink, --ad-idx-gutter (1.5rem — the accent-rule gutter),
 *         --ad-dur-base (420ms), --ad-ease-signature (cubic-bezier(.16,1,.3,1)).
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-index-rows-css';
  var ACCENT = 'var(--ad-accent,oklch(62% 0.2 25))';
  var INK = 'var(--ad-ink,oklch(96% 0 0))';
  var HAIR = 'color-mix(in oklab,' + INK + ' 14%,transparent)';
  var TRANSIT = 'var(--ad-dur-base,420ms) var(--ad-ease-signature,cubic-bezier(.16,1,.3,1))';

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      '.ad-idx{border-bottom:1px solid ' + HAIR + ';}' +
      // A reserved left gutter seats the accent rule clear of the row number:
      // the ::before sits at the padding-box edge (left:0) while padding-inline-start
      // insets the row content, so the rule never butts the numeral.
      '.ad-idx__row{position:relative;border-top:1px solid ' + HAIR + ';' +
      'padding-inline-start:var(--ad-idx-gutter,1.5rem);' +
      'transition:opacity ' + TRANSIT + ';}' +
      '.ad-idx__row::before{content:"";position:absolute;left:0;top:0;bottom:0;' +
      'width:2px;background:' + ACCENT + ';transform:scaleY(0);' +
      'transition:transform ' + TRANSIT + ';}' +
      '.ad-idx__row [data-ad-row-meta]{display:inline-block;opacity:.55;' +
      'transition:opacity ' + TRANSIT + ',transform ' + TRANSIT + ';}' +
      // Spotlight-dim: the container dims every row, then the lit row wins by
      // source order (equal specificity). Coarse pointers never hover → clean list.
      '.ad-idx:hover .ad-idx__row,.ad-idx:focus-within .ad-idx__row{opacity:.45;}' +
      '.ad-idx .ad-idx__row:hover,.ad-idx .ad-idx__row:focus-within{opacity:1;}' +
      '.ad-idx__row:hover::before,.ad-idx__row:focus-within::before{transform:scaleY(1);}' +
      '.ad-idx__row:hover [data-ad-row-meta],' +
      '.ad-idx__row:focus-within [data-ad-row-meta]{opacity:1;transform:translateX(4px);}' +
      // Reduced motion → opacity states land instantly, metadata never translates.
      '@media (prefers-reduced-motion:reduce){' +
      '.ad-idx__row,.ad-idx__row::before,.ad-idx__row [data-ad-row-meta]{transition:none;}' +
      '.ad-idx__row:hover [data-ad-row-meta],' +
      '.ad-idx__row:focus-within [data-ad-row-meta]{transform:none;}}';
    document.head.appendChild(s);
  }

  function rowsOf(container, rowSelector) {
    var rows = Array.prototype.slice.call(container.querySelectorAll(rowSelector));
    if (!rows.length) rows = Array.prototype.slice.call(container.children);
    return rows;
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-index]';
    var rowSelector = opts.rowSelector || '[data-ad-row]';
    injectCss();

    var containers = Array.prototype.slice.call(root.querySelectorAll(selector));
    var rows = [];
    containers.forEach(function (c) {
      c.classList.add('ad-idx');
      rowsOf(c, rowSelector).forEach(function (r) {
        r.classList.add('ad-idx__row');
        rows.push(r);
      });
    });

    return {
      destroy: function () {
        containers.forEach(function (c) { c.classList.remove('ad-idx'); });
        rows.forEach(function (r) { r.classList.remove('ad-idx__row'); });
        var s = document.getElementById(CSS_ID);
        if (s) s.parentNode.removeChild(s);
      }
    };
  }

  global.awardIndexRows = { init: init };
})(typeof window !== 'undefined' ? window : this);
