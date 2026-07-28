/*
 * chapter-select enhancer — grab-drag + snapped-tile marking for the
 * chapter-select section form (winner: Ponpon Mania — chapters as album
 * covers, 'drag/scroll/click, snap-to-place'). The rail already pans, snaps
 * and clicks with zero script (native CSS scroll-snap); this enhancer adds
 * the two moves a mouse cannot make natively:
 *   grab-drag   fine pointers drag the rail directly (pointer capture,
 *               scrollLeft follows the hand). Snap is released for the
 *               drag's duration (data-cs-dragging on the form root — the
 *               form's CSS swaps scroll-snap-type off) and re-engages
 *               through a centered settle on release: the tile nearest the
 *               rail's center scrolls into place, smooth by default,
 *               instant under reduced motion. A real drag suppresses the
 *               click it would otherwise fire, so dragging across a cover
 *               never navigates — click stays click, drag stays drag.
 *   marking     the cover nearest the rail's center is marked as the
 *               picked-up record (data-cs-active + aria-current="true") so
 *               paired components and the build's nav can read the
 *               selection — rAF-throttled on the rail's own scroll, written
 *               only on change (an IO threshold misreads a wide rail where
 *               several covers sit fully visible).
 * Touch: untouched — the native pan + snap IS the winner interaction there;
 * the enhancer's drag path arms on fine pointers only. Layering law: this
 * enhancer toggles attributes on the form root and tiles, creates nothing,
 * and never restructures a slot's inner DOM.
 *
 * Usage:  awardChapterSelect.init(root, { selector })
 *   root      Element|Document  scope (default document)
 *   selector  string  form roots (default '[data-ad-form="chapter-select"]')
 * Returns { destroy() }. Idempotent per form root. Styling lives in
 * forms/chapter-select.css (linked, not injected — the rail must survive a
 * dead script).
 *
 * Tokens: none of its own — reads only prefers-reduced-motion for the
 * settle behavior; the form's stylesheet carries the visual states.
 */
(function (global) {
  'use strict';
  var DRAG_MIN = 6;      // px before a press becomes a drag (click stays click)
  var SETTLE_MS = 600;   // scrollend fallback before snap re-engages

  var reduce = function () {
    return !!(global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches);
  };
  var finePointer = function () {
    return !!(global.matchMedia && global.matchMedia('(hover: hover) and (pointer: fine)').matches);
  };

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-form="chapter-select"]';

    var units = [];
    Array.prototype.forEach.call(root.querySelectorAll(selector), function (form) {
      if (form.__adChapterSelect) return; // idempotent per form root
      var rows = form.querySelector('[data-slot="rows"]');
      if (!rows) return;
      var tiles = Array.prototype.slice.call(rows.querySelectorAll('[data-chapter]'));
      if (!tiles.length) return;

      var u = {
        form: form, rows: rows, tiles: tiles, active: null, raf: 0,
        dragging: false, justDragged: false,
        startX: 0, startLeft: 0, pointerId: null, settleTimer: 0
      };
      form.__adChapterSelect = u;

      // ---- snapped-tile marking — the cover nearest the rail's center is
      // the picked-up record (an IO threshold misreads a wide rail where
      // several covers sit fully visible); rAF-throttled on the rail's own
      // scroll, written only on change
      u.mark = function () {
        u.raf = 0;
        var mid = rows.getBoundingClientRect();
        var cx = mid.left + mid.width / 2;
        var best = null, bestD = Infinity;
        tiles.forEach(function (tile) {
          var r = tile.getBoundingClientRect();
          var d = Math.abs(r.left + r.width / 2 - cx);
          if (d < bestD) { bestD = d; best = tile; }
        });
        if (best === u.active) return;
        if (u.active) {
          u.active.removeAttribute('data-cs-active');
          u.active.removeAttribute('aria-current');
        }
        u.active = best;
        best.setAttribute('data-cs-active', '');
        best.setAttribute('aria-current', 'true');
      };
      u.onScroll = function () {
        if (!u.raf) u.raf = global.requestAnimationFrame(u.mark);
      };
      rows.addEventListener('scroll', u.onScroll, { passive: true });
      u.mark();

      // ---- grab-drag — fine pointers only --------------------------------
      if (finePointer()) {
        form.setAttribute('data-cs-grab', '');

        u.onDown = function (e) {
          if (e.button !== 0) return;
          u.pointerId = e.pointerId;
          u.startX = e.clientX;
          u.startLeft = rows.scrollLeft;
          u.dragging = false;    // arms on real travel, so a plain click never drags
          u.justDragged = false; // a new press is a new gesture — a stale echo
                                 // (pointercancel left no click) never eats it
          if (u.settleTimer) { global.clearTimeout(u.settleTimer); u.settleTimer = 0; }
        };
        u.onMove = function (e) {
          if (u.pointerId !== e.pointerId) return;
          var dx = e.clientX - u.startX;
          if (!u.dragging) {
            if (Math.abs(dx) < DRAG_MIN) return;
            u.dragging = true;
            form.setAttribute('data-cs-dragging', ''); // snap released
            if (rows.setPointerCapture) rows.setPointerCapture(e.pointerId);
          }
          rows.scrollLeft = u.startLeft - dx;
        };
        u.onUp = function (e) {
          if (u.pointerId !== e.pointerId) return;
          u.pointerId = null;
          if (!u.dragging) return;
          u.dragging = false;
          u.justDragged = true; // the release's click is the drag's echo — eat it
          // snap-to-place: settle the tile nearest the rail's center, then
          // hand the rail back to native snap
          var center = rows.getBoundingClientRect();
          var cx = center.left + center.width / 2;
          var best = null, bestD = Infinity;
          tiles.forEach(function (tile) {
            var r = tile.getBoundingClientRect();
            var d = Math.abs(r.left + r.width / 2 - cx);
            if (d < bestD) { bestD = d; best = tile; }
          });
          if (best) best.scrollIntoView({
            behavior: reduce() ? 'auto' : 'smooth', inline: 'center', block: 'nearest'
          });
          var settle = function () {
            if (u.settleTimer) { global.clearTimeout(u.settleTimer); u.settleTimer = 0; }
            rows.removeEventListener('scrollend', settle);
            form.removeAttribute('data-cs-dragging'); // snap re-engages in place
          };
          rows.addEventListener('scrollend', settle);
          u.settleTimer = global.setTimeout(settle, SETTLE_MS);
        };
        u.onClick = function (e) {
          if (!u.justDragged) return;
          u.justDragged = false;
          e.preventDefault(); // a drag is not a navigation
          e.stopPropagation();
        };
        rows.addEventListener('pointerdown', u.onDown);
        rows.addEventListener('pointermove', u.onMove);
        rows.addEventListener('pointerup', u.onUp);
        rows.addEventListener('pointercancel', u.onUp);
        rows.addEventListener('click', u.onClick, true);
      }

      units.push(u);
    });

    return {
      destroy: function () {
        units.forEach(function (u) {
          u.rows.removeEventListener('scroll', u.onScroll);
          if (u.raf) global.cancelAnimationFrame(u.raf);
          if (u.settleTimer) global.clearTimeout(u.settleTimer);
          if (u.onDown) {
            u.rows.removeEventListener('pointerdown', u.onDown);
            u.rows.removeEventListener('pointermove', u.onMove);
            u.rows.removeEventListener('pointerup', u.onUp);
            u.rows.removeEventListener('pointercancel', u.onUp);
            u.rows.removeEventListener('click', u.onClick, true);
          }
          u.form.removeAttribute('data-cs-grab');
          u.form.removeAttribute('data-cs-dragging');
          u.tiles.forEach(function (tile) {
            tile.removeAttribute('data-cs-active');
            tile.removeAttribute('aria-current');
          });
          delete u.form.__adChapterSelect;
        });
        units.length = 0;
      }
    };
  }

  global.awardChapterSelect = { init: init };
})(typeof window !== 'undefined' ? window : this);
