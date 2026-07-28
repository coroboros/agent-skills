/*
 * spotlight-expand-tile — the layout-AWARE row expand (winners: Vercel
 * spotlight, design-canonical; Apple highlights scrub, shipped-canonical;
 * Codrops technique with verified params). NOT a contained zoom and NOT a
 * card lift: the hovered tile's preview expands ACROSS its row while the
 * row's siblings lean away to clear it, a de-saturated preview restores to
 * color, and the tile's copy fades up. The verified Codrops params carry:
 * siblings shift ~2.5vw; the preview opens through a 12-POINT clip-path whose
 * horizontal arm morphs from the tile box out to the expanded bounds (the
 * cross opening); the resting preview sits at (dim − 5vw)/dim of the expanded
 * dim (JS computes the per-tile scale); ease is the power2.inOut analog on
 * the --ad-dur-base clock. Everything is transform/clip-path/filter/opacity —
 * the grid NEVER reflows layout; the expansion is composited.
 *
 * Markup: <div data-ad-spotlight>            the grid (any row-wrapping grid/flex)
 *           <a data-ad-spot-tile href="…">   or any element; repeated
 *             <figure data-spot-media><img …></figure>
 *             <div data-spot-copy>…</div>    fades up on expand
 *           </a>
 *         </div>
 *
 * Pointer classes: fine pointers de-saturate at rest and expand on
 * hover/focus-within; COARSE pointers keep the complete color surface at rest
 * (pointer vocabulary dormant — the archetype's mobile answer) and the first
 * tap IS the expand (a tap on an expanded link falls through and navigates;
 * a tap elsewhere collapses). Keyboard: focus expands, Escape collapses.
 * Rows are measured (offsetTop groups), re-measured on resize — the shift
 * direction knows which side of the spotlight each sibling sits on.
 * Reduced motion / no JS: the authored grid stands — full color, copy
 * visible, no de-saturation, no expansion.
 *
 * Usage:  awardSpotlightExpandTile.init(root, { selector, grow })
 *   root      Element|Document  scope (default document)
 *   selector  string            grids (default '[data-ad-spotlight]')
 *   grow      string            total expansion (default '5vw' — 2.5vw a side)
 * Returns { destroy() }. Idempotent per root.
 *
 * Tokens: --ad-dur-base, --ad-spot-ease (default cubic-bezier(.45,0,.55,1),
 * the power2.inOut analog — override to the build's register).
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-spotlight-expand-tile-css';
  var TRANSIT = 'var(--ad-dur-base,420ms) var(--ad-spot-ease,cubic-bezier(.45,0,.55,1))';

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
    // The 12-point pair: at rest the four arm points sit collapsed on the side
    // edges (a plain rectangle inset by --_arm each side); on expand they land
    // on the layer edges — the horizontal arm of a cross morphing open across
    // the row. Equal point counts keep the morph interpolable.
    var restClip =
      'polygon(var(--_arm) 0%,calc(100% - var(--_arm)) 0%,' +
      'calc(100% - var(--_arm)) 30%,calc(100% - var(--_arm)) 30%,' +
      'calc(100% - var(--_arm)) 70%,calc(100% - var(--_arm)) 70%,' +
      'calc(100% - var(--_arm)) 100%,var(--_arm) 100%,' +
      'var(--_arm) 70%,var(--_arm) 70%,var(--_arm) 30%,var(--_arm) 30%)';
    var openClip =
      'polygon(var(--_arm) 0%,calc(100% - var(--_arm)) 0%,' +
      'calc(100% - var(--_arm)) 30%,100% 30%,' +
      '100% 70%,calc(100% - var(--_arm)) 70%,' +
      'calc(100% - var(--_arm)) 100%,var(--_arm) 100%,' +
      'var(--_arm) 70%,0% 70%,0% 30%,var(--_arm) 30%)';
    s.textContent =
      '.ad-spot--live [data-ad-spot-tile]{position:relative;z-index:1;' +
      'transform:translate3d(0,0,0);transition:transform ' + TRANSIT + ';}' +
      // the media layer is OVERSIZED by the grow so the opened arm has pixels
      // to reveal — sized once (a static layout fact, never animated)
      '.ad-spot--live [data-spot-media]{position:relative;margin:0;' +
      'width:calc(100% + var(--_grow,5vw));margin-left:calc(var(--_grow,5vw)/-2);' +
      '--_arm:calc(var(--_grow,5vw)/2);' +
      'clip-path:' + restClip + ';transition:clip-path ' + TRANSIT + ';}' +
      '.ad-spot--live [data-spot-media] img,.ad-spot--live [data-spot-media] video{' +
      'display:block;width:100%;height:100%;object-fit:cover;' +
      'transform:scale(var(--_ps,.94));transform-origin:50% 50%;' +
      'transition:transform ' + TRANSIT + ',filter ' + TRANSIT + ';}' +
      // the expand: arm opens, preview restores to full scale and color,
      // spotlight rises over the yielded siblings
      '.ad-spot--live .is-spot{z-index:3;}' +
      '.ad-spot--live .is-spot [data-spot-media]{clip-path:' + openClip + ';}' +
      '.ad-spot--live .is-spot [data-spot-media] img,' +
      '.ad-spot--live .is-spot [data-spot-media] video{transform:scale(1);filter:none;}' +
      '.ad-spot--live .is-yield-l{transform:translate3d(calc(var(--_grow,5vw)/-2),0,0);}' +
      '.ad-spot--live .is-yield-r{transform:translate3d(calc(var(--_grow,5vw)/2),0,0);}' +
      // fine pointers earn the rest de-saturation + hidden copy; coarse keeps
      // the complete color surface (pointer vocabulary dormant on touch)
      '@media (hover:hover) and (pointer:fine){' +
      '.ad-spot--live [data-spot-media] img,.ad-spot--live [data-spot-media] video{' +
      'filter:grayscale(1);}' +
      '.ad-spot--live [data-spot-copy]{opacity:0;transform:translate3d(0,10px,0);' +
      'transition:opacity ' + TRANSIT + ',transform ' + TRANSIT + ';}' +
      '.ad-spot--live .is-spot [data-spot-copy]{opacity:1;transform:translate3d(0,0,0);}}' +
      '@media (prefers-reduced-motion:reduce){' +
      '.ad-spot--live [data-ad-spot-tile],.ad-spot--live [data-spot-media],' +
      '.ad-spot--live [data-spot-media] img,.ad-spot--live [data-spot-media] video,' +
      '.ad-spot--live [data-spot-copy]{transition:none;}}';
    document.head.appendChild(s);
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-spotlight]';
    var grow = opts.grow || '5vw';

    // Reduced motion: the authored grid IS the finished state — full color,
    // copy visible, nothing expands, nothing binds.
    if (reduce()) return { destroy: function () {} };

    injectCss();
    if (root.__adSpotlightExpand) root.__adSpotlightExpand.destroy();

    var grids = [];
    Array.prototype.forEach.call(root.querySelectorAll(selector), function (grid) {
      var tiles = Array.prototype.slice.call(grid.querySelectorAll('[data-ad-spot-tile]'));
      if (tiles.length < 2) return; // one tile has no row to expand across
      grid.classList.add('ad-spot--live');
      grid.style.setProperty('--_grow', grow);

      var unit = { grid: grid, tiles: tiles, rows: null, active: null, listeners: [] };

      function measure() {
        // the verified ratio: resting preview = (dim − grow)/dim of the
        // expanded dim — i.e. tile width over the oversized media layer
        tiles.forEach(function (t) {
          var media = t.querySelector('[data-spot-media]');
          if (!media) return;
          var mediaW = media.getBoundingClientRect().width;
          var tileW = t.getBoundingClientRect().width;
          if (mediaW > 0 && tileW > 0) {
            media.style.setProperty('--_ps', (tileW / mediaW).toFixed(4));
          }
        });
        unit.rows = null; // recomputed lazily
      }

      function rowOf(tile) {
        if (!unit.rows) {
          unit.rows = [];
          var byTop = {};
          tiles.forEach(function (t) {
            var top = Math.round(t.offsetTop / 8) * 8; // tolerance for subpixel rows
            (byTop[top] = byTop[top] || []).push(t);
          });
          Object.keys(byTop).forEach(function (k) { unit.rows.push(byTop[k]); });
        }
        for (var i = 0; i < unit.rows.length; i++) {
          if (unit.rows[i].indexOf(tile) !== -1) return unit.rows[i];
        }
        return [tile];
      }

      function collapse() {
        if (!unit.active) return;
        tiles.forEach(function (t) { t.classList.remove('is-spot', 'is-yield-l', 'is-yield-r'); });
        unit.active = null;
      }

      function spot(tile) {
        if (unit.active === tile) return;
        collapse();
        unit.active = tile;
        tile.classList.add('is-spot');
        var row = rowOf(tile);
        var i = row.indexOf(tile);
        row.forEach(function (t, j) {
          if (t === tile) return;
          t.classList.add(j < i ? 'is-yield-l' : 'is-yield-r');
        });
      }

      function listen(el, ev, fn, o) {
        el.addEventListener(ev, fn, o);
        unit.listeners.push([el, ev, fn, o]);
      }

      if (finePointer()) {
        listen(grid, 'pointerover', function (e) {
          var tile = e.target.closest && e.target.closest('[data-ad-spot-tile]');
          if (tile && grid.contains(tile)) spot(tile);
        });
        listen(grid, 'pointerleave', collapse);
      } else {
        // touch: the first tap IS the expand; a tap on the expanded link
        // falls through and navigates; a tap outside collapses. The decision
        // reads the PRE-tap state (pointerdown) — the tap's own focusin spots
        // the tile before click fires and must not count as "already open".
        listen(grid, 'pointerdown', function (e) {
          var tile = e.target.closest && e.target.closest('[data-ad-spot-tile]');
          unit.tapArmed = !!tile && unit.active === tile;
        });
        listen(grid, 'click', function (e) {
          var tile = e.target.closest && e.target.closest('[data-ad-spot-tile]');
          if (!tile) { collapse(); return; }
          // e.detail 0 = keyboard activation — Enter on a focused link navigates
          if (e.detail > 0 && !unit.tapArmed) {
            e.preventDefault();
            spot(tile);
          }
        });
        listen(document, 'click', function (e) {
          if (!grid.contains(e.target)) collapse();
        });
      }
      listen(grid, 'focusin', function (e) {
        var tile = e.target.closest && e.target.closest('[data-ad-spot-tile]');
        if (tile) spot(tile);
      });
      listen(grid, 'focusout', function (e) {
        if (!e.relatedTarget || !grid.contains(e.relatedTarget)) collapse();
      });
      listen(grid, 'keydown', function (e) {
        if (e.key === 'Escape') collapse();
      });
      listen(global, 'resize', function () { unit.rows = null; measure(); });

      measure();
      grids.push(unit);
    });

    var handle = {
      destroy: function () {
        grids.forEach(function (u) {
          u.listeners.forEach(function (l) { l[0].removeEventListener(l[1], l[2], l[3]); });
          u.tiles.forEach(function (t) {
            t.classList.remove('is-spot', 'is-yield-l', 'is-yield-r');
            var media = t.querySelector('[data-spot-media]');
            if (media) media.style.removeProperty('--_ps');
          });
          u.grid.classList.remove('ad-spot--live');
          u.grid.style.removeProperty('--_grow');
        });
        var s = document.getElementById(CSS_ID);
        if (s && s.parentNode) s.parentNode.removeChild(s);
        if (root.__adSpotlightExpand === handle) delete root.__adSpotlightExpand;
      }
    };
    root.__adSpotlightExpand = handle;
    return handle;
  }

  global.awardSpotlightExpandTile = { init: init };
})(typeof window !== 'undefined' ? window : this);
