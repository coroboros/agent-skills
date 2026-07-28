/*
 * cursor-spawn-trail — the maximalist spawn channel (winners: Warhol Arts —
 * SOTD 2025-04, footer cursor image-trail; DICH Fashion — SOTD+Dev 2025-06,
 * pixel tracer). Images or particles SPAWN at the cursor position as it
 * travels across a declared field, throttled by travel distance; each spawn
 * plays the winner-verified decay — scale 0 -> 1 while filter
 * brightness/contrast fall 300% -> 100%, then opacity 1 -> 0 over ~0.4s
 * after a short hold — on a recycled node pool with a rising z-index counter
 * so spawns stack newest-on-top without accumulating DOM (Warhol's z-index
 * recycling). Two modes decided by the markup: image mode cycles the
 * builder's authored pool in order; pixel mode (no pool) spawns small
 * accent squares — the DICH tracer. A footer/idle spectacle channel, NOT a
 * page-wide cursor: scope it to the section that earns it (Warhol runs it in
 * the footer only). The adjacent Eloy Benoffi connect-CTA clone-storm is a
 * different mechanic and already ships as footer-clone-machine.
 * Touch (the winners' own answer): the channel is fully dormant on coarse
 * pointers — the trail is décor over the field's real content, which is
 * never gated, so the surface stays complete without it. Reduced motion:
 * dormant, nothing spawns.
 *
 * Expected markup — the field declares itself; image mode adds an authored
 * hidden pool (the builder's art, the component never invents imagery):
 *   <footer data-ad-spawn-trail>
 *     <div data-ad-spawn-pool hidden><img src="…" alt="">…</div>
 *     …the field's real content…
 *   </footer>
 *
 * Usage:  awardCursorSpawnTrail.init(root, opts)
 *   root      Element|Document  scope (default document)
 *   selector  string  fields (default '[data-ad-spawn-trail]')
 *   step      px      pointer travel between spawns (default 90 — the
 *                     throttle-by-distance pattern is winner-verified, the
 *                     exact step is illustrative)
 *   pool      number  recycled node count / max concurrent (default 18)
 * Returns { destroy() }. Idempotent per field. destroy() removes the layer,
 * listeners, and the stylesheet.
 *
 * A11y + perf: the spawn layer is aria-hidden and pointer-events:none — it
 * never intercepts a click or takes focus; the field is clipped while the
 * channel is live (JS-applied class — the full-bleed overlay law: spawns
 * never paint over neighboring sections). Compositor-only: transform +
 * filter + opacity via WAAPI on promoted nodes; spawning is event-driven, so
 * there is no idle rAF at all.
 *
 * Tokens: --ad-accent (pixel mode ink), --ad-ease-signature (the enter
 * curve); extension --ad-cst-size (spawn size, default clamp(56px,9vw,120px)
 * image / 10px pixel).
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-cursor-spawn-trail-css';
  var ENTER_MS = 400;  // scale 0->1 + brightness/contrast 300->100% (verified)
  var HOLD_MS = 200;   // the short delay before the fade (illustrative)
  var FADE_MS = 400;   // opacity 1->0 over ~0.4s (verified)
  var Z_WRAP = 500;    // z counter wraps far above pool size, far below chrome

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
      // the clip is JS-applied with the layer — a dead script never leaves a
      // section clipped for a channel that is not running
      '.ad-cst-host{position:relative;overflow:hidden;}' +
      '.ad-cst__layer{position:absolute;inset:0;pointer-events:none;z-index:1;}' +
      '.ad-cst__s{position:absolute;left:0;top:0;opacity:0;will-change:transform,filter,opacity;}' +
      '.ad-cst__s img{display:block;inline-size:var(--ad-cst-size,clamp(56px,9vw,120px));' +
      'block-size:auto;}' +
      '.ad-cst__s--px{inline-size:var(--ad-cst-size,10px);aspect-ratio:1;' +
      'background:var(--ad-accent,oklch(62% 0.2 25));}';
    document.head.appendChild(s);
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-spawn-trail]';
    var step = opts.step != null ? opts.step : 90;
    var poolN = opts.pool != null ? opts.pool : 18;

    // Dormant on touch and under reduce — the field's content stands complete.
    if (reduce() || !finePointer()) return { destroy: function () {} };

    injectCss();
    var ease = (getComputedStyle(document.documentElement)
      .getPropertyValue('--ad-ease-signature') || '').trim() || 'cubic-bezier(.16,1,.3,1)';

    var fields = [];
    Array.prototype.forEach.call(root.querySelectorAll(selector), function (el) {
      if (el.__adCstField) return; // idempotent per field
      var poolBox = el.querySelector('[data-ad-spawn-pool]');
      var srcs = [];
      if (poolBox) {
        Array.prototype.forEach.call(poolBox.querySelectorAll('img'), function (img) {
          srcs.push(img.currentSrc || img.src);
        });
      }
      var layer = document.createElement('div');
      layer.className = 'ad-cst__layer';
      layer.setAttribute('aria-hidden', 'true');
      el.classList.add('ad-cst-host');
      el.appendChild(layer);

      var nodes = [];
      for (var i = 0; i < poolN; i++) {
        var n = document.createElement(srcs.length ? 'div' : 'i');
        n.className = 'ad-cst__s' + (srcs.length ? '' : ' ad-cst__s--px');
        if (srcs.length) {
          var img = document.createElement('img');
          img.alt = '';
          n.appendChild(img);
        }
        layer.appendChild(n);
        nodes.push({ el: n, anim: null });
      }

      var f = {
        el: el, layer: layer, srcs: srcs, nodes: nodes,
        next: 0, srcAt: 0, z: 0,
        rect: null, lx: 0, ly: 0, travel: 0, primed: false,
        anims: []
      };
      el.__adCstField = f;
      fields.push(f);
    });
    if (!fields.length) return { destroy: function () {} };

    function spawn(f, x, y) {
      var slot = f.nodes[f.next];
      f.next = (f.next + 1) % f.nodes.length;
      if (slot.anim) slot.anim.cancel();
      var el = slot.el;
      if (f.srcs.length) {
        el.firstChild.src = f.srcs[f.srcAt];
        f.srcAt = (f.srcAt + 1) % f.srcs.length; // the pool cycles in order
      }
      f.z = (f.z % Z_WRAP) + 1; // z recycling: newest rides on top, no runaway
      el.style.zIndex = String(f.z);
      var at = 'translate3d(' + x.toFixed(1) + 'px,' + y.toFixed(1) + 'px,0) translate(-50%,-50%)';
      if (!el.animate) return; // no WAAPI → the channel quietly stands down
      var total = ENTER_MS + HOLD_MS + FADE_MS;
      slot.anim = el.animate([
        { transform: at + ' scale(0)', filter: 'brightness(3) contrast(3)', opacity: 1,
          easing: ease },
        { transform: at + ' scale(1)', filter: 'brightness(1) contrast(1)', opacity: 1,
          offset: ENTER_MS / total },
        { transform: at + ' scale(1)', filter: 'brightness(1) contrast(1)', opacity: 1,
          offset: (ENTER_MS + HOLD_MS) / total, easing: 'linear' },
        { transform: at + ' scale(1)', filter: 'brightness(1) contrast(1)', opacity: 0 }
      ], { duration: total, fill: 'forwards' });
    }

    var bindings = [];
    fields.forEach(function (f) {
      var onEnter = function (e) {
        f.rect = f.el.getBoundingClientRect();
        f.lx = e.clientX; f.ly = e.clientY;
        f.travel = 0; f.primed = true;
      };
      var onMove = function (e) {
        if (!f.primed || !f.rect) return;
        var dx = e.clientX - f.lx, dy = e.clientY - f.ly;
        f.lx = e.clientX; f.ly = e.clientY;
        f.travel += Math.sqrt(dx * dx + dy * dy);
        if (f.travel < step) return;
        f.travel = 0; // one spawn per threshold crossing, even on a teleport
        spawn(f, e.clientX - f.rect.left, e.clientY - f.rect.top);
      };
      var onLeave = function () { f.primed = false; }; // running decays finish
      var onDirty = function () { if (f.primed) f.rect = f.el.getBoundingClientRect(); };
      f.el.addEventListener('pointerenter', onEnter);
      f.el.addEventListener('pointermove', onMove, { passive: true });
      f.el.addEventListener('pointerleave', onLeave);
      global.addEventListener('scroll', onDirty, { passive: true });
      global.addEventListener('resize', onDirty);
      bindings.push({ f: f, enter: onEnter, move: onMove, leave: onLeave, dirty: onDirty });
    });

    return {
      destroy: function () {
        bindings.forEach(function (b) {
          b.f.el.removeEventListener('pointerenter', b.enter);
          b.f.el.removeEventListener('pointermove', b.move);
          b.f.el.removeEventListener('pointerleave', b.leave);
          global.removeEventListener('scroll', b.dirty);
          global.removeEventListener('resize', b.dirty);
        });
        fields.forEach(function (f) {
          f.nodes.forEach(function (slot) { if (slot.anim) slot.anim.cancel(); });
          if (f.layer.parentNode) f.layer.parentNode.removeChild(f.layer);
          f.el.classList.remove('ad-cst-host');
          delete f.el.__adCstField;
        });
        fields.length = 0;
        var s = document.getElementById(CSS_ID);
        if (s && s.parentNode) s.parentNode.removeChild(s);
      }
    };
  }

  global.awardCursorSpawnTrail = { init: init };
})(typeof window !== 'undefined' ? window : this);
