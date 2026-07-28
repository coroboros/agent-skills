/*
 * hover-preview-video — the production-house index reveal (winner: Bloom
 * 'Hover listing archives'; Awwwards catalog canon: 'Video Hover Preview',
 * 'Project hover preview' (Olivier Gillaizeau), Bittercreek.Studio index
 * hover). Hovering a project row surfaces its MUTED FOOTAGE in one floating
 * cursor-attached layer — lerped toward the pointer — with an optional
 * marquee title gliding over the frame (Bloom's marquee-over-preview). The
 * video sibling of index-hover-preview (which surfaces a still): this one
 * plays the work; the row's text stays the accessible name, the layer is
 * presentation only.
 * Touch answer (the documented one): no hover — each row carries its poster
 * inline and the first tap plays the footage in place instead of navigating;
 * a second tap (or a tap on a playing row) navigates. Rows opting out with
 * data-ad-hpv-touch="poster" keep a plain poster frame and navigate on first
 * tap. Reduced motion: the layer still appears and follows (coverage stays),
 * it snaps instead of trailing, and footage NEVER plays — a static poster
 * frame on every pointer class.
 *
 * Expected markup — rows opt in with their footage; posters are mandatory so
 * the resting/reduced state is always a real frame:
 *   <div data-ad-hover-preview>
 *     <a data-ad-hpv-row data-ad-hpv-video="…/clip.mp4"
 *        data-ad-hpv-poster="…/frame.jpg" data-ad-hpv-label="Studio — Client"
 *        href="…">…</a>
 *   </div>
 *
 * Usage:  awardHoverPreviewVideo.init(root, opts)
 *   root         Element|Document  scope (default document)
 *   selector     string  index roots (default '[data-ad-hover-preview]')
 *   rowSelector  string  rows (default '[data-ad-hpv-row]')
 *   lerp         number  pointer-follow smoothing (default 0.14)
 * Returns { destroy() }. Idempotent per index. destroy() removes the float
 * layer, inline figures, listeners, and the stylesheet.
 *
 * Perf: one <video> total on fine pointers, muted + playsinline + loop,
 * paused the instant the pointer leaves; inline touch videos preload nothing
 * until tapped. The float animates transform/opacity only, on a promoted
 * layer; the rAF loop runs only while shown or still traveling.
 *
 * Tokens: --ad-ground-2 (the layer's loading ground), --ad-ink +
 * --ad-font-mono (marquee title), --ad-dur-base + --ad-ease-signature
 * (show/hide).
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-hover-preview-video-css';

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
      // the one floating layer — fixed, promoted, never interactive
      '.ad-hpv__float{position:fixed;left:0;top:0;z-index:60;' +
      'width:clamp(220px,24vw,360px);aspect-ratio:16/9;overflow:hidden;' +
      'pointer-events:none;opacity:0;will-change:transform;' +
      'background:var(--ad-ground-2,oklch(18% 0.01 260));' +
      'transition:opacity var(--ad-dur-base,420ms) ' +
      'var(--ad-ease-signature,cubic-bezier(.16,1,.3,1));}' +
      '.ad-hpv__float.is-on{opacity:1;}' +
      '.ad-hpv__float video{display:block;width:100%;height:100%;object-fit:cover;}' +
      // the marquee title gliding over the frame (Bloom) — a continuous loop,
      // so linear stays legal; two copies wrap seamlessly at -50%
      '.ad-hpv__marquee{position:absolute;left:0;right:0;bottom:0;overflow:hidden;' +
      'padding:.35em 0;display:none;color:var(--ad-ink,oklch(96% 0 0));' +
      'font-family:var(--ad-font-mono,ui-monospace,monospace);font-size:.7rem;' +
      'letter-spacing:.08em;text-transform:uppercase;}' +
      '.ad-hpv__marquee.is-labeled{display:block;}' +
      '.ad-hpv__marquee span{display:inline-block;white-space:nowrap;padding-right:2em;' +
      'will-change:transform;animation:ad-hpv-glide 9s linear infinite;}' +
      '@keyframes ad-hpv-glide{to{transform:translate3d(-50%,0,0);}}' +
      // inline figures exist only for the coarse-pointer index
      '.ad-hpv__inline{display:none;margin:0;position:relative;overflow:hidden;}' +
      '@media (hover: none), (pointer: coarse){' +
      '.ad-hpv__float{display:none;}' +
      '.ad-hpv__inline{display:block;}' +
      '.ad-hpv__inline video{display:block;width:100%;aspect-ratio:16/9;object-fit:cover;}}' +
      // reduced motion: coverage stays, amplitude goes — no glide, no fade
      '@media (prefers-reduced-motion:reduce){' +
      '.ad-hpv__float{transition:none;}' +
      '.ad-hpv__marquee span{animation:none;}}';
    document.head.appendChild(s);
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-hover-preview]';
    var rowSelector = opts.rowSelector || '[data-ad-hpv-row]';
    var lerpK = opts.lerp != null ? opts.lerp : 0.14;

    injectCss();
    var fine = finePointer();
    var indexes = [];

    Array.prototype.forEach.call(root.querySelectorAll(selector), function (index) {
      if (index.__adHpv) return; // idempotent
      var rows = Array.prototype.slice.call(index.querySelectorAll(rowSelector));
      if (!rows.length) return;

      var unit = { index: index, float: null, raf: 0, listeners: [] };

      if (fine) {
        // ---- fine pointer: one cursor-attached floating footage layer -----
        var float = document.createElement('figure');
        float.className = 'ad-hpv__float';
        float.setAttribute('aria-hidden', 'true');
        var video = document.createElement('video');
        video.muted = true;
        video.loop = true;
        video.setAttribute('playsinline', '');
        video.preload = 'metadata';
        float.appendChild(video);
        var marquee = document.createElement('div');
        marquee.className = 'ad-hpv__marquee';
        var glide = document.createElement('span');
        marquee.appendChild(glide);
        float.appendChild(marquee);
        index.appendChild(float);
        unit.float = float;

        var tx = 0, ty = 0, cx = 0, cy = 0, on = false;

        function apply() {
          // centered on the pointer, slightly ahead of it
          float.style.transform =
            'translate3d(' + (cx + 20).toFixed(1) + 'px,' + (cy - 40).toFixed(1) + 'px,0) ' +
            'translate(0,-50%)';
        }
        function frame() {
          unit.raf = 0;
          if (reduce()) { cx = tx; cy = ty; } // snap — no trailing under reduce
          else { cx += (tx - cx) * lerpK; cy += (ty - cy) * lerpK; }
          apply();
          var settledNow = Math.abs(tx - cx) < 0.3 && Math.abs(ty - cy) < 0.3;
          // the loop runs only while shown or still traveling — no idle rAF
          if (on || !settledNow) unit.raf = global.requestAnimationFrame(frame);
        }
        function wake() {
          if (!unit.raf) unit.raf = global.requestAnimationFrame(frame);
        }

        var onOver = function (e) {
          var row = e.target && e.target.closest ? e.target.closest(rowSelector) : null;
          if (!row || !index.contains(row)) return;
          var src = row.getAttribute('data-ad-hpv-video');
          if (!src) return;
          if (video.getAttribute('src') !== src) {
            video.setAttribute('src', src);
            video.poster = row.getAttribute('data-ad-hpv-poster') || '';
          }
          var label = row.getAttribute('data-ad-hpv-label') || '';
          // two copies back-to-back so the -50% glide wraps without a gap
          glide.textContent = label ? label + ' — ' + label + ' — ' : '';
          marquee.classList.toggle('is-labeled', !!label);
          if (!on) {
            on = true;
            // first show lands at the pointer, not lerped in from 0,0
            cx = tx = e.clientX; cy = ty = e.clientY;
            apply();
            float.classList.add('is-on');
          }
          // footage never plays under reduce — the poster IS the preview
          if (!reduce()) {
            var p = video.play();
            if (p && p.catch) p.catch(function () { /* autoplay policy → poster stands */ });
          }
          wake();
        };
        var onMove = function (e) {
          if (!on) return;
          tx = e.clientX; ty = e.clientY;
          wake();
        };
        var onLeave = function () {
          if (!on) return;
          on = false;
          video.pause();
          float.classList.remove('is-on');
        };
        index.addEventListener('pointerover', onOver);
        index.addEventListener('pointermove', onMove, { passive: true });
        index.addEventListener('pointerleave', onLeave);
        unit.listeners.push(['pointerover', onOver], ['pointermove', onMove], ['pointerleave', onLeave]);
      } else {
        // ---- coarse pointer: inline posters; tap plays in place ----------
        rows.forEach(function (row) {
          var src = row.getAttribute('data-ad-hpv-video');
          if (!src || row.querySelector('.ad-hpv__inline')) return;
          var fig = document.createElement('figure');
          fig.className = 'ad-hpv__inline';
          fig.setAttribute('aria-hidden', 'true');
          var v = document.createElement('video');
          v.muted = true;
          v.loop = true;
          v.setAttribute('playsinline', '');
          v.preload = 'none';
          v.poster = row.getAttribute('data-ad-hpv-poster') || '';
          v.setAttribute('data-src', src);
          fig.appendChild(v);
          row.appendChild(fig);
        });
        // tap-to-play-inline vs navigate: the first tap on a resting row
        // plays its footage in place; a tap on a playing row falls through
        // to the link. Rows marked data-ad-hpv-touch="poster" (and every
        // row under reduce) keep the poster and navigate on first tap.
        var onClick = function (e) {
          var row = e.target && e.target.closest ? e.target.closest(rowSelector) : null;
          if (!row || !index.contains(row)) return;
          if (reduce()) return; // static poster, no playback — navigate
          if (row.getAttribute('data-ad-hpv-touch') === 'poster') return;
          var v = row.querySelector('.ad-hpv__inline video');
          if (!v || !v.paused) return; // already playing → the tap navigates
          e.preventDefault();
          if (!v.getAttribute('src')) v.setAttribute('src', v.getAttribute('data-src'));
          var p = v.play();
          if (p && p.catch) p.catch(function () { /* poster stands */ });
        };
        index.addEventListener('click', onClick);
        unit.listeners.push(['click', onClick]);
      }

      index.__adHpv = unit;
      indexes.push(unit);
    });

    return {
      destroy: function () {
        indexes.forEach(function (unit) {
          if (unit.raf) global.cancelAnimationFrame(unit.raf);
          unit.listeners.forEach(function (l) {
            unit.index.removeEventListener(l[0], l[1]);
          });
          if (unit.float && unit.float.parentNode) {
            var v = unit.float.querySelector('video');
            if (v) v.pause();
            unit.float.parentNode.removeChild(unit.float);
          }
          Array.prototype.forEach.call(
            unit.index.querySelectorAll('.ad-hpv__inline'),
            function (fig) {
              var v = fig.querySelector('video');
              if (v) v.pause();
              if (fig.parentNode) fig.parentNode.removeChild(fig);
            }
          );
          delete unit.index.__adHpv;
        });
        var s = document.getElementById(CSS_ID);
        if (s && s.parentNode) s.parentNode.removeChild(s);
      }
    };
  }

  global.awardHoverPreviewVideo = { init: init };
})(typeof window !== 'undefined' ? window : this);
