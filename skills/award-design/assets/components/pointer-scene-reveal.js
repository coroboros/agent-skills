/*
 * pointer-scene-reveal — the fine pointer DRIVES the scene's reveal (winners:
 * Hubtown by Unseen Studio — the cursor uncovers detail in the geometry and
 * lighting, a reveal mask/light bound to pointer position; ERA by Vide Infra —
 * the splash camera reacts to cursor movement giving dynamic angles). The
 * immersive playbook's committed-pointer-layer law made executable for the
 * hero: the pointer is not chrome-deep (magnetic buttons) or DOM-deep
 * (parallax layers) — it reaches INTO the medium.
 *
 * Two channels, one pointer machine (differential lerp ~0.1, bounded):
 *   · ENGINE — opts.onPoint(nx, ny, engaged) receives the lerped pointer as
 *     normalized device coords (-1..1, y up — the Three raycaster convention)
 *     every frame while engaged, then eases back to center on leave and stops
 *     after one final onPoint(0, 0, false). The delegated scene binds it to a
 *     reveal-mask uniform, a spotlight, or a camera orbit offset — the SCENE
 *     owns rendering; no Three import crosses this boundary.
 *   · DOM LENS (built-in, no engine needed) — the root holds a resting plate
 *     [data-psr-base] and a decorative detail layer [data-psr-detail] authored
 *     `hidden` (the treated/annotated double). The component wraps the detail
 *     in a circular lens it creates ([data-psr-lens], aria-hidden,
 *     pointer-events:none), TRANSLATES the lens to the pointer and
 *     counter-translates the detail inside it so the two plates stay
 *     registered — the classic compositor-clean reveal: two transforms per
 *     frame, zero per-frame paint (the moving-window law; a moving mask/
 *     clip-path would repaint the layer every frame). The lens scales in on
 *     enter and settles out on leave. The root is clipped (overflow:hidden)
 *     so the lens never bleeds past the hero's bound.
 *
 * Ruled DISTINCT, not an alias, on the seam the gap names:
 *   · raycast-object-state is the per-MESH input state machine — discrete
 *     hover/hit verbs through the caller's hitTest (the OBJECT axis). This
 *     drives ONE CONTINUOUS SCENE-WIDE parameter — no objects, no verbs, no
 *     hit cue (the SCENE axis). Hubtown runs both: object states over a
 *     global pointer reveal; a page ships both without contention.
 *   · pointer-parallax shifts DOM LAYERS at differential rates — depth décor
 *     on the DOM plane. This DRIVES THE MEDIUM: the reveal mask / camera
 *     parameter lives inside the scene (or the lens uncovers a second plate),
 *     which is exactly what the manifest lacked ('nothing that drives the 3D
 *     medium with the pointer').
 *
 * Expected markup (lens channel):
 *   <section data-ad-psr>
 *     <img data-psr-base src="plate.jpg" alt="…">
 *     <div data-psr-detail hidden><img src="plate-detail.jpg" alt=""></div>
 *   </section>
 *
 * Usage:  awardPointerSceneReveal.init(root, opts)
 *   root      Element|Document  scope (default document)
 *   selector  string    scene roots (default '[data-ad-psr]')
 *   onPoint   function  (nx, ny, engaged) — the engine channel; when given
 *                       and no [data-psr-detail] exists, no lens is built.
 *   lerp      number    differential lerp per frame (default 0.1)
 *   radius    px        lens radius (default 150)
 * Returns { destroy() }. Idempotent per root (the lens unwraps, the detail
 * re-hides).
 *
 * Gating — the committed degrade ladder: FINE POINTER ONLY (matchMedia
 * '(any-hover: hover) and (pointer: fine)'); on touch the channel is DORMANT
 * — no lens, no onPoint, the scene runs on scroll alone (the gap's own
 * verdict). Content-visible at rest: the base plate is the content and the
 * detail is authored `hidden` — no-JS and dead-script renders stand whole.
 * prefers-reduced-motion: the channel never binds (the pointer-parallax
 * precedent — this is décor amplitude, not state): no lens, no onPoint, no
 * rAF; the scene rests at its authored frame. The rAF loop runs only while
 * engaged or settling — zero idle work, nothing to pause on visibilitychange
 * because leaving the tab leaves the root and settles the loop.
 *
 * Tokens: --ad-dur-base + --ad-ease-signature (lens scale-in/out only —
 * the tracking itself is the lerp, never a CSS transition).
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-pointer-scene-reveal-css';

  var reduce = function () {
    return !!(global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches);
  };
  var fine = function () {
    return !!(global.matchMedia
      && global.matchMedia('(any-hover: hover) and (pointer: fine)').matches);
  };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      '[data-ad-psr]{position:relative;overflow:hidden;}' + // the clip law — the lens never bleeds
      // translate rides `transform` (JS, per frame); the engage pop rides the
      // independent `scale` property so the two never fight.
      '[data-psr-lens]{position:absolute;top:0;left:0;border-radius:50%;' +
        'overflow:hidden;pointer-events:none;' +
        'will-change:transform;z-index:2;' +
        'transition:scale var(--ad-dur-base,420ms) var(--ad-ease-signature,cubic-bezier(.16,1,.3,1));' +
        'scale:0;}' +
      '[data-psr-lens].is-engaged{scale:1;}' +
      '[data-psr-lens] [data-psr-detail]{position:absolute;top:0;left:0;will-change:transform;}';
    document.head.appendChild(s);
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-psr]';
    var lerp = opts.lerp != null ? opts.lerp : 0.1;
    var radius = opts.radius != null ? opts.radius : 150;

    var scenes = Array.prototype.slice.call(root.querySelectorAll(selector))
      .filter(function (el) { return !el.__adPsrBound; });
    if (!scenes.length) return { destroy: function () {} };

    // Dormant ladder: touch/coarse and reduced-motion never bind — the scene
    // rests at its authored frame and the detail stays hidden.
    if (!fine() || reduce()) {
      return { destroy: function () {} };
    }

    injectCss();
    scenes.forEach(function (el) { el.__adPsrBound = true; });

    var instances = scenes.map(function (el) {
      var inst = {
        el: el, lens: null, detail: null, detailHome: null,
        x: 0, y: 0, tx: 0, ty: 0,       // lens px (current / target)
        engaged: false, running: false, rafId: 0,
        w: 1, h: 1
      };

      var detail = el.querySelector('[data-psr-detail]');
      if (detail && !opts.onPoint) {
        // Build the lens; move the authored detail inside it (inner-DOM
        // surgery — the interaction component's right; destroy restores).
        inst.detail = detail;
        inst.detailHome = { parent: detail.parentNode, next: detail.nextSibling };
        var lens = document.createElement('div');
        lens.setAttribute('data-psr-lens', '');
        lens.setAttribute('aria-hidden', 'true');
        lens.style.width = (radius * 2) + 'px';
        lens.style.height = (radius * 2) + 'px';
        lens.appendChild(detail);
        detail.removeAttribute('hidden');
        el.appendChild(lens);
        inst.lens = lens;
      }

      inst.measure = function () {
        inst.w = el.clientWidth || 1;
        inst.h = el.clientHeight || 1;
        if (inst.detail) {
          inst.detail.style.width = inst.w + 'px';
          inst.detail.style.height = inst.h + 'px';
        }
      };
      inst.measure();

      inst.paint = function () {
        if (inst.lens) {
          inst.lens.style.transform = 'translate3d(' + (inst.x - radius).toFixed(1) + 'px,'
            + (inst.y - radius).toFixed(1) + 'px,0)';
          // Counter-translate: the detail stays registered with the base plate.
          inst.detail.style.transform = 'translate3d(' + (radius - inst.x).toFixed(1) + 'px,'
            + (radius - inst.y).toFixed(1) + 'px,0)';
        }
        if (opts.onPoint) {
          // Normalized device coords: -1..1, y up (the Three convention).
          var nx = (inst.x / inst.w) * 2 - 1;
          var ny = -((inst.y / inst.h) * 2 - 1);
          opts.onPoint(nx, ny, inst.engaged);
        }
      };

      inst.frame = function () {
        inst.x += (inst.tx - inst.x) * lerp;
        inst.y += (inst.ty - inst.y) * lerp;
        inst.paint();
        var settled = !inst.engaged
          && Math.abs(inst.tx - inst.x) < 0.3 && Math.abs(inst.ty - inst.y) < 0.3;
        if (settled) {
          inst.running = false;
          if (opts.onPoint) opts.onPoint((inst.x / inst.w) * 2 - 1, -((inst.y / inst.h) * 2 - 1), false);
          return;
        }
        inst.rafId = requestAnimationFrame(inst.frame);
      };

      inst.run = function () {
        if (inst.running) return;
        inst.running = true;
        inst.rafId = requestAnimationFrame(inst.frame);
      };

      inst.onEnter = function (e) {
        inst.measure();
        var r = el.getBoundingClientRect();
        inst.engaged = true;
        inst.tx = e.clientX - r.left;
        inst.ty = e.clientY - r.top;
        inst.x = inst.tx; inst.y = inst.ty; // no fly-in from a stale corner
        if (inst.lens) inst.lens.classList.add('is-engaged');
        inst.run();
      };
      inst.onMove = function (e) {
        if (!inst.engaged) return;
        var r = el.getBoundingClientRect();
        inst.tx = e.clientX - r.left;
        inst.ty = e.clientY - r.top;
        inst.run();
      };
      inst.onLeave = function () {
        inst.engaged = false;
        // Settle toward center — the reveal parameter eases home.
        inst.tx = inst.w / 2;
        inst.ty = inst.h / 2;
        if (inst.lens) inst.lens.classList.remove('is-engaged');
        inst.run();
      };

      el.addEventListener('pointerenter', inst.onEnter);
      el.addEventListener('pointermove', inst.onMove);
      el.addEventListener('pointerleave', inst.onLeave);
      return inst;
    });

    function onResize() {
      instances.forEach(function (inst) { inst.measure(); });
    }
    global.addEventListener('resize', onResize, { passive: true });

    return {
      destroy: function () {
        global.removeEventListener('resize', onResize);
        instances.forEach(function (inst) {
          cancelAnimationFrame(inst.rafId);
          inst.el.removeEventListener('pointerenter', inst.onEnter);
          inst.el.removeEventListener('pointermove', inst.onMove);
          inst.el.removeEventListener('pointerleave', inst.onLeave);
          if (inst.lens) {
            inst.detail.setAttribute('hidden', '');
            inst.detail.style.transform = '';
            inst.detail.style.width = '';
            inst.detail.style.height = '';
            if (inst.detailHome.next) inst.detailHome.parent.insertBefore(inst.detail, inst.detailHome.next);
            else inst.detailHome.parent.appendChild(inst.detail);
            inst.lens.remove();
          }
          delete inst.el.__adPsrBound;
        });
      }
    };
  }

  global.awardPointerSceneReveal = { init: init };
})(typeof window !== 'undefined' ? window : this);
