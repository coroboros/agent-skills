/*
 * morph-tile-grid enhancer — the Cyd figure signature as inline writes
 * (winner: Cyd Stumpel .work-thumb: border-radius morph rounder + a resting
 * circle/graphic crossfading to the full image + caption slide-up; the
 * form's CSS owns layout + the resting radius, this enhancer owns the whole
 * state machine so the stylesheet ships zero motion and hides nothing). The
 * morph runs as a CLIP morph — clip-path: inset(0 round <radius>) written
 * inline on the media box, morphing the resting radius language to the
 * rounder hover shape — so the crossfading layers can never spill past the
 * shape mid-morph. Perf note: a radius/clip morph is not compositor-only —
 * it is the winner's own mechanic, scoped to ONE bounded tile box per
 * response, pointer-driven (never a scroll channel).
 *
 * Pointer classes (the archetype's mobile answer):
 *   fine pointer  the enhancer ARMS the rest — caption slid down + faded
 *                 (inline write; the CSS never hides it) — then
 *                 hover/focus-within morphs the clip rounder, crossfades
 *                 [data-tile-rest] 1->0 over the full image, slides the
 *                 caption up; leave reverses. Geometry carries it, no accent.
 *   coarse/reduce the REVEALED state is the rest: full image, caption up,
 *                 overlay crossfaded away (applied instantly — the finished
 *                 state, per the init contract); taps just navigate.
 *   dead script   the authored tile stands whole — image, resting graphic,
 *                 caption all legible (nothing was ever hidden in CSS).
 *
 * Usage:  awardMorphTileGrid.init(root, opts)
 *   root      Element|Document  scope (default document)
 *   selector  string  form roots (default '[data-ad-form="morph-tile-grid"]')
 * Returns { destroy() }. Idempotent per root. destroy() removes every inline
 * write and listener — the authored grid returns.
 *
 * Layering law kept: inline style writes on authored hooks only
 * ([data-tile-media] / [data-tile-rest] / [data-tile-caption]); no nodes
 * created, no inner-DOM surgery, no stylesheet injected.
 * Tokens read: --ad-mtg-radius / --ad-mtg-hover-radius (the form's radius
 * language), --ad-dur-base + --ad-ease-signature (the inline transitions).
 */
(function (global) {
  'use strict';
  var TRANSIT = 'var(--ad-dur-base,420ms) var(--ad-ease-signature,cubic-bezier(.16,1,.3,1))';
  var REST_RADIUS = '34% 66% 52% 48% / 48% 40% 60% 52%';
  var HOVER_RADIUS = '50% 50% 50% 50% / 50% 50% 50% 50%';

  var reduce = function () {
    return !!(global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches);
  };
  var finePointer = function () {
    return !!(global.matchMedia && global.matchMedia('(hover: hover) and (pointer: fine)').matches);
  };

  function clip(radius) { return 'inset(0 round ' + radius + ')'; }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-form="morph-tile-grid"]';
    if (root.__adMorphTileGrid) return root.__adMorphTileGrid;

    var still = reduce();
    var fine = finePointer();
    var tiles = [];

    Array.prototype.forEach.call(root.querySelectorAll(selector), function (section) {
      var cs = getComputedStyle(section);
      var rest = (cs.getPropertyValue('--ad-mtg-radius') || '').trim() || REST_RADIUS;
      var hover = (cs.getPropertyValue('--ad-mtg-hover-radius') || '').trim() || HOVER_RADIUS;
      Array.prototype.forEach.call(
        section.querySelectorAll('[data-slot="tile"]'), function (tile) {
          var media = tile.querySelector('[data-tile-media]');
          var overlay = tile.querySelector('[data-tile-rest]');
          var caption = tile.querySelector('[data-tile-caption]');
          if (!media) return;
          var t = { tile: tile, media: media, overlay: overlay, caption: caption,
                    rest: rest, hover: hover, enter: null, leave: null };

          if (still || !fine) {
            // the finished state, applied instantly: full image, caption up
            if (overlay) overlay.style.opacity = '0';
            tiles.push(t);
            return;
          }

          // arm the rest (fine pointers only; the CSS itself hides nothing)
          media.style.clipPath = clip(rest);
          media.style.transition = 'clip-path ' + TRANSIT;
          if (overlay) {
            overlay.style.opacity = '1';
            overlay.style.transition = 'opacity ' + TRANSIT;
          }
          if (caption) {
            caption.style.opacity = '0';
            caption.style.transform = 'translate3d(0,0.6em,0)';
            caption.style.transition = 'opacity ' + TRANSIT + ', transform ' + TRANSIT;
          }

          t.enter = function () {
            media.style.clipPath = clip(hover);
            if (overlay) overlay.style.opacity = '0';
            if (caption) {
              caption.style.opacity = '1';
              caption.style.transform = 'translate3d(0,0,0)';
            }
          };
          t.leave = function () {
            // never leave the reveal open while focus is still inside
            if (tile.matches(':focus-within')) return;
            media.style.clipPath = clip(rest);
            if (overlay) overlay.style.opacity = '1';
            if (caption) {
              caption.style.opacity = '0';
              caption.style.transform = 'translate3d(0,0.6em,0)';
            }
          };
          tile.addEventListener('pointerenter', t.enter);
          tile.addEventListener('pointerleave', t.leave);
          tile.addEventListener('focusin', t.enter);
          tile.addEventListener('focusout', t.leave);
          tiles.push(t);
        });
    });

    var handle = {
      destroy: function () {
        tiles.forEach(function (t) {
          if (t.enter) {
            t.tile.removeEventListener('pointerenter', t.enter);
            t.tile.removeEventListener('pointerleave', t.leave);
            t.tile.removeEventListener('focusin', t.enter);
            t.tile.removeEventListener('focusout', t.leave);
          }
          t.media.style.clipPath = '';
          t.media.style.transition = '';
          if (t.overlay) { t.overlay.style.opacity = ''; t.overlay.style.transition = ''; }
          if (t.caption) {
            t.caption.style.opacity = '';
            t.caption.style.transform = '';
            t.caption.style.transition = '';
          }
        });
        tiles = [];
        if (root.__adMorphTileGrid === handle) delete root.__adMorphTileGrid;
      }
    };
    root.__adMorphTileGrid = handle;
    return handle;
  }

  global.awardMorphTileGrid = { init: init };
})(typeof window !== 'undefined' ? window : this);
