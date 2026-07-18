/*
 * physics-tumble-field — the grab-and-throw rigid-body field (winner:
 * MoMoney by Jordan Gilroy — SOTD 2026-03-13, the corpus's ONE clean
 * verified Matter.js throw-field; Bruno's Portfolio is ADJACENT ONLY — a
 * bump-able vehicle-collision world, not a grab-and-throw DOM field — and
 * Valentin Gassend was removed from the physics group as miscredited. The
 * manifest's first physics component, shipped on ONE winner and saying so).
 * Every field element becomes a physical body with weight, restitution and
 * drag: grab one and drag it (a spring constraint — the body keeps its
 * momentum), release and the cursor's instantaneous velocity flies it off
 * to collide, bounce and settle; bodies stack and jostle under gravity and
 * the engine keeps simulating between inputs until the pile is at rest —
 * the field is never frozen mid-air. On touch the same grab-drag-fling maps
 * to tap/drag/flick (a strength, not a fallback — touch-action:none rides
 * the field). Repo law: dependency-free — the gap names Matter.js, so this
 * is the minimal hand-rolled subset it needs (semi-implicit Euler, circle
 * proxies per element, impulse + positional contact resolution, spring
 * mouse-constraint, sleep states), never the library. restitution 0.6 is
 * the documented Matter.js technique default, NOT a per-site read —
 * MoMoney's shipped values were never published; every number here is a
 * DEFAULT.
 *
 * Discipline (binding): DOM transforms only (translate + rotate on
 * promoted layers — no canvas, so the DPR/context-loss floors do not
 * apply); layout is never touched — bodies move relative to their authored
 * layout seats, and the field container clips (overflow:clip) so a thrown
 * body never paints over neighboring sections. The rAF loop runs only
 * while the field is on-screen (IntersectionObserver), the tab visible,
 * and at least one body awake — a settled pile parks the loop cold and any
 * grab wakes it. A drag starts only past a 6px threshold, so links and
 * buttons inside a body keep their click (a post-drag click is swallowed
 * once). Keyboard/focus order is untouched — the physics is a pointer
 * enhancement over real DOM content.
 * prefers-reduced-motion: fully dormant — bodies rest at their laid-out
 * positions, no simulation, no transforms, no listeners; the authored
 * layout IS the reduced state (the gap's own reduce answer). No-JS: the
 * authored layout, untouched.
 *
 * Expected markup — the field and its throwable children:
 *   <div data-ad-tumble>
 *     <article>…card…</article>
 *     <article>…card…</article>
 *   </div>
 *
 * Usage:  awardPhysicsTumbleField.init(root, opts)
 *   root         Element|Document  scope (default document)
 *   selector     string  fields (default '[data-ad-tumble]')
 *   itemSelector string  bodies inside a field (default ':scope > *')
 *   gravity      px/s²   (default 1800)
 *   restitution  0-1     bounce (default 0.6 — the Matter.js doc default)
 *   maxSpeed     px/s    fling clamp (default 3600)
 * Returns { getState(), destroy() }. getState() → per-field arrays of
 * { x, y, vx, vy, angle, asleep } plus { running } — the drive/test
 * readout. Idempotent per field. destroy() clears transforms, restores
 * listeners and removes the stylesheet.
 *
 * Tokens: none read directly — the bodies are the builder's own styled
 * elements; --ad-* stays their business.
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-physics-tumble-css';
  var DRAG_THRESHOLD = 6;    // px before a press becomes a grab
  var SAMPLE_MS = 80;        // release-velocity window
  var SLEEP_SPEED = 8;       // px/s below which a body may sleep
  var SLEEP_FRAMES = 30;
  var SPRING = 18;           // mouse-constraint stiffness (1/s)
  var reduce = function () {
    return !!(global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches);
  };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      // the clip law: a thrown body never paints over a neighboring section
      '.ad-tumble{position:relative;overflow:clip;touch-action:none;}' +
      '.ad-tumble__body{will-change:transform;cursor:grab;}' +
      '.ad-tumble__body.is-held{cursor:grabbing;}';
    document.head.appendChild(s);
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-tumble]';

    // reduced-motion: the authored layout IS the field at rest — dormant.
    if (reduce()) {
      return { getState: function () { return { running: false, fields: [] }; },
               destroy: function () {} };
    }

    var itemSelector = opts.itemSelector || ':scope > *';
    var GRAVITY = opts.gravity != null ? +opts.gravity : 1800;
    var REST = opts.restitution != null ? +opts.restitution : 0.6;
    var VMAX = opts.maxSpeed != null ? +opts.maxSpeed : 3600;

    injectCss();
    var fields = [];

    function makeField(el) {
      if (el.__adTumble) return;
      el.__adTumble = true;
      el.classList.add('ad-tumble');

      var field = {
        el: el, bodies: [], raf: 0, last: 0,
        onScreen: true, held: null, io: null, listeners: []
      };

      Array.prototype.forEach.call(el.querySelectorAll(itemSelector), function (item) {
        var r = item.getBoundingClientRect();
        var host = el.getBoundingClientRect();
        item.classList.add('ad-tumble__body');
        field.bodies.push({
          el: item,
          w: r.width, h: r.height,
          // circle proxy: mean half-extent reads truest on card-shaped bodies
          r: Math.max(12, (r.width + r.height) / 4),
          restX: r.left - host.left + r.width / 2,
          restY: r.top - host.top + r.height / 2,
          x: r.left - host.left + r.width / 2,
          y: r.top - host.top + r.height / 2,
          vx: 0, vy: 0, angle: 0, va: 0,
          asleep: false, still: 0
        });
      });
      if (!field.bodies.length) { delete el.__adTumble; return; }

      function bounds() {
        return { w: el.clientWidth, h: el.clientHeight };
      }

      function render(b) {
        b.el.style.transform = 'translate3d(' + (b.x - b.restX).toFixed(2) + 'px,' +
          (b.y - b.restY).toFixed(2) + 'px,0) rotate(' + b.angle.toFixed(3) + 'rad)';
      }

      function wakeAll() {
        field.bodies.forEach(function (b) { b.asleep = false; b.still = 0; });
        arm();
      }

      function step(dt) {
        var box = bounds();
        var awake = false;
        field.bodies.forEach(function (b) {
          if (b.asleep) return;
          if (field.held && field.held.body === b) {
            // spring mouse-constraint: the body chases the pointer, keeping
            // momentum for the release
            b.vx += (field.held.px - b.x) * SPRING * dt * 10;
            b.vy += (field.held.py - b.y) * SPRING * dt * 10;
            b.vx *= 0.72; b.vy *= 0.72; // heavy damping while held
          } else {
            b.vy += GRAVITY * dt;
          }
          var sp0 = Math.hypot(b.vx, b.vy);
          if (sp0 > VMAX) { b.vx *= VMAX / sp0; b.vy *= VMAX / sp0; sp0 = VMAX; }
          b.x += b.vx * dt;
          b.y += b.vy * dt;
          if (b.va > 3) b.va = 3; else if (b.va < -3) b.va = -3;
          b.angle += b.va * dt;
          // keep the angle wrapped so the settle torque has a near side
          if (b.angle > Math.PI) b.angle -= Math.PI * 2;
          else if (b.angle < -Math.PI) b.angle += Math.PI * 2;
          b.va *= 0.985;
          // the settle read: once slow, a weighted-base torque rights the
          // card toward upright — flight never fakes it (speed-gated)
          if (sp0 < 90) { b.va += -b.angle * 7 * dt; b.va *= 0.96; }
          // walls: floor + sides + ceiling; tangential slip spins the body
          var minX = b.w / 2, maxX = box.w - b.w / 2;
          var maxY = box.h - b.h / 2, minY = b.h / 2;
          if (b.y > maxY) { b.y = maxY; if (b.vy > 0) { b.vy = -b.vy * REST; b.va += b.vx * 0.004; } b.vx *= 0.94; }
          if (b.y < minY) { b.y = minY; if (b.vy < 0) b.vy = -b.vy * REST; }
          if (b.x < minX) { b.x = minX; if (b.vx < 0) { b.vx = -b.vx * REST; b.va -= b.vy * 0.004; } }
          if (b.x > maxX) { b.x = maxX; if (b.vx > 0) { b.vx = -b.vx * REST; b.va += b.vy * 0.004; } }
        });
        // pairwise contacts: impulse + positional correction — the stack/jostle
        for (var i = 0; i < field.bodies.length; i++) {
          for (var j = i + 1; j < field.bodies.length; j++) {
            var a = field.bodies[i], c = field.bodies[j];
            var dx = c.x - a.x, dy = c.y - a.y;
            var dist = Math.hypot(dx, dy) || 0.001;
            var overlap = a.r + c.r - dist;
            if (overlap <= 0) continue;
            var nx = dx / dist, ny = dy / dist;
            a.x -= nx * overlap / 2; a.y -= ny * overlap / 2;
            c.x += nx * overlap / 2; c.y += ny * overlap / 2;
            var rvx = c.vx - a.vx, rvy = c.vy - a.vy;
            var rel = rvx * nx + rvy * ny;
            if (rel < 0) {
              var jI = -(1 + REST) * rel / 2;
              a.vx -= jI * nx; a.vy -= jI * ny;
              c.vx += jI * nx; c.vy += jI * ny;
              // tangential slip → spin, the tumble read
              var tv = rvx * -ny + rvy * nx;
              a.va += tv * 0.002; c.va -= tv * 0.002;
              if (Math.abs(jI) > 4) { a.asleep = false; c.asleep = false; a.still = 0; c.still = 0; }
            }
          }
        }
        field.bodies.forEach(function (b) {
          if (b.asleep) return;
          var held = field.held && field.held.body === b;
          if (!held && Math.hypot(b.vx, b.vy) < SLEEP_SPEED && Math.abs(b.va) < 0.05) {
            b.still++;
            if (b.still > SLEEP_FRAMES) { b.asleep = true; b.vx = 0; b.vy = 0; b.va = 0; }
          } else b.still = 0;
          render(b);
          if (!b.asleep) awake = true;
        });
        return awake;
      }

      function frame(now) {
        field.raf = 0;
        if (!field.onScreen || document.hidden) { field.last = 0; return; }
        if (!field.last) field.last = now;
        var dt = Math.min(1 / 30, (now - field.last) / 1000);
        field.last = now;
        var awake = false;
        // two substeps keep fast flings from tunneling through neighbors
        awake = step(dt / 2);
        awake = step(dt / 2) || awake;
        if (awake || field.held) field.raf = global.requestAnimationFrame(frame);
        else field.last = 0; // the pile settled — the loop parks cold
      }

      function arm() {
        if (!field.raf && field.onScreen && !document.hidden) {
          field.last = 0;
          field.raf = global.requestAnimationFrame(frame);
        }
      }

      function fieldPoint(e) {
        var host = el.getBoundingClientRect();
        return { x: e.clientX - host.left, y: e.clientY - host.top };
      }

      function on(target, ev, fn, o) {
        target.addEventListener(ev, fn, o);
        field.listeners.push([target, ev, fn, o]);
      }

      on(el, 'pointerdown', function (e) {
        if (e.button != null && e.button !== 0 && e.pointerType === 'mouse') return;
        var item = e.target.closest('.ad-tumble__body');
        if (!item || !el.contains(item)) return;
        var body = null;
        field.bodies.forEach(function (b) { if (b.el === item) body = b; });
        if (!body) return;
        var p = fieldPoint(e);
        field.held = {
          body: body, id: e.pointerId, px: p.x, py: p.y,
          startX: p.x, startY: p.y, engaged: false, dragged: false,
          trail: [{ t: e.timeStamp, x: p.x, y: p.y }]
        };
      });
      on(el, 'pointermove', function (e) {
        var h = field.held;
        if (!h || e.pointerId !== h.id) return;
        var p = fieldPoint(e);
        h.px = p.x; h.py = p.y;
        h.trail.push({ t: e.timeStamp, x: p.x, y: p.y });
        while (h.trail.length > 2 && e.timeStamp - h.trail[0].t > SAMPLE_MS) h.trail.shift();
        if (!h.engaged && Math.hypot(p.x - h.startX, p.y - h.startY) > DRAG_THRESHOLD) {
          h.engaged = true; h.dragged = true;
          h.body.asleep = false; h.body.still = 0;
          h.body.el.classList.add('is-held');
          try { el.setPointerCapture(e.pointerId); } catch (err) {}
          arm();
        }
      });
      var release = function (e) {
        var h = field.held;
        if (!h || (e && e.pointerId !== h.id)) return;
        if (h.engaged && h.trail.length > 1) {
          // the cursor's instantaneous velocity becomes the throw
          var a0 = h.trail[0], a1 = h.trail[h.trail.length - 1];
          var span = (a1.t - a0.t) / 1000;
          if (span > 0.004) {
            h.body.vx = (a1.x - a0.x) / span;
            h.body.vy = (a1.y - a0.y) / span;
            var sp = Math.hypot(h.body.vx, h.body.vy);
            if (sp > VMAX) { h.body.vx *= VMAX / sp; h.body.vy *= VMAX / sp; }
            h.body.va = h.body.vx / (h.body.r * 40);
          }
        }
        h.body.el.classList.remove('is-held');
        if (h.dragged) {
          // swallow exactly the click this drag fires (synchronously after
          // pointerup) — disarm on the next task so a later real click,
          // when the drag produced none, is never eaten (drive-caught)
          var once = function (ce) { ce.stopPropagation(); ce.preventDefault(); };
          el.addEventListener('click', once, { capture: true, once: true });
          global.setTimeout(function () {
            el.removeEventListener('click', once, { capture: true });
          }, 0);
        }
        field.held = null;
        arm();
      };
      on(el, 'pointerup', release);
      on(el, 'pointercancel', release);

      if ('IntersectionObserver' in global) {
        field.io = new IntersectionObserver(function (entries) {
          field.onScreen = entries[0].isIntersecting;
          if (field.onScreen) arm();
        });
        field.io.observe(el);
      }
      field.wakeAll = wakeAll;
      field.arm = arm;
      fields.push(field);
    }

    Array.prototype.forEach.call(root.querySelectorAll(selector), makeField);

    var onVis = function () {
      if (!document.hidden) fields.forEach(function (f) { f.arm(); });
    };
    document.addEventListener('visibilitychange', onVis);

    return {
      getState: function () {
        return {
          running: fields.some(function (f) { return !!f.raf; }),
          fields: fields.map(function (f) {
            return f.bodies.map(function (b) {
              return { x: Math.round(b.x), y: Math.round(b.y),
                       vx: Math.round(b.vx), vy: Math.round(b.vy),
                       angle: +b.angle.toFixed(3), asleep: b.asleep };
            });
          })
        };
      },
      destroy: function () {
        document.removeEventListener('visibilitychange', onVis);
        fields.forEach(function (f) {
          if (f.raf) global.cancelAnimationFrame(f.raf);
          if (f.io) f.io.disconnect();
          f.listeners.forEach(function (l) { l[0].removeEventListener(l[1], l[2], l[3]); });
          f.bodies.forEach(function (b) {
            b.el.style.transform = '';
            b.el.classList.remove('ad-tumble__body', 'is-held');
          });
          f.el.classList.remove('ad-tumble');
          delete f.el.__adTumble;
        });
        fields = [];
        var s = document.getElementById(CSS_ID);
        if (s && s.parentNode) s.parentNode.removeChild(s);
      }
    };
  }

  global.awardPhysicsTumbleField = { init: init };
})(typeof window !== 'undefined' ? window : this);
