/*
 * swipe-snap-gallery enhancer — snap-state dots for the swipe-snap-gallery
 * section form. The track scrolls and snaps with zero script (native CSS
 * scroll-snap + OS momentum — no JS physics); this enhancer only mirrors the
 * snap state into the enhancer-owned [data-slot="dots"] slot: one <i> per
 * [data-cell], .is-active following the cell in view. Layering law: it creates
 * children only inside the dots slot (documented enhancer-owned) and never
 * restructures the track's inner DOM. No scroll hijack, no buttons, no
 * autoplay, no listeners — one IntersectionObserver per gallery does the
 * tracking; everything is passive. Reduced-motion: no behavioral difference —
 * scroll-snap is a stop, not an animation, so there is nothing to suppress.
 *
 * Usage:  awardSwipeGallery.init(root, { selector })
 *   root      Element|Document  scope (default document)
 *   selector  string            gallery roots (default '[data-ad-form="swipe-snap-gallery"]')
 * Returns { destroy() }. Idempotent — a re-init rebuilds each gallery's dots
 * and observer. Styling lives in forms/swipe-snap-gallery.css (linked, not
 * injected — the form's layout must survive a dead script).
 */
(function (global) {
  'use strict';

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-form="swipe-snap-gallery"]';

    var galleries = [];
    Array.prototype.forEach.call(root.querySelectorAll(selector), function (gallery) {
      var dotsSlot = gallery.querySelector('[data-slot="dots"]');
      var track = gallery.querySelector('[data-slot="track"]');
      if (!dotsSlot || !track) return;
      var cells = Array.prototype.slice.call(track.querySelectorAll('[data-cell]'));
      if (!cells.length) return;

      if (gallery.__adSwipeIO) gallery.__adSwipeIO.disconnect();
      dotsSlot.textContent = '';

      var dots = cells.map(function (cell, i) {
        var dot = document.createElement('i');
        // static default until the observer's first pass lands
        if (i === 0) dot.className = 'is-active';
        dotsSlot.appendChild(dot);
        return dot;
      });

      var io = null;
      if ('IntersectionObserver' in global) {
        // 0.6 discriminates: the snapped cell is fully in the track's box,
        // the peeking neighbor shows ~22% and never crosses.
        io = new IntersectionObserver(function (entries) {
          entries.forEach(function (entry) {
            if (!entry.isIntersecting) return;
            var index = cells.indexOf(entry.target);
            if (index < 0) return;
            dots.forEach(function (dot, i) {
              dot.classList.toggle('is-active', i === index);
            });
          });
        }, { root: track, threshold: 0.6 });
        cells.forEach(function (cell) { io.observe(cell); });
        gallery.__adSwipeIO = io;
      }

      galleries.push({ gallery: gallery, dotsSlot: dotsSlot, io: io });
    });

    return {
      destroy: function () {
        galleries.forEach(function (g) {
          if (g.io) g.io.disconnect();
          if (g.gallery.__adSwipeIO === g.io) delete g.gallery.__adSwipeIO;
          g.dotsSlot.textContent = '';
        });
        galleries.length = 0;
      }
    };
  }

  global.awardSwipeGallery = { init: init };
})(typeof window !== 'undefined' ? window : this);
