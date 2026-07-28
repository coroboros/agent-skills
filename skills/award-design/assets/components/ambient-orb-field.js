/*
 * ambient-orb-field — the WebGL-free living ground (style anchors: Arc /
 * Granola / Apple Vision Pro; Igloo Inc's ambient scene drift is the winner
 * register it echoes). The DNA-core spatial substrate for the no-WebGL
 * register: a FIXED, pointer-events:none layer of 2-3 large-radius OKLCH
 * radial-gradient orbs at low opacity (.15-.25), filter:blur(80px), each
 * drifting on a 15-25s ease-in-out alternate cycle (translate a few vw +
 * scale 1->1.1). The blur and each orb's gradient rasterize once; every
 * animated property is transform/opacity — compositor-only by construction.
 * A soft fine-pointer response rides on top: each orb leans toward the
 * pointer at its own depth rate through a decelerating lerp (the
 * spatial-organic register — soft, warm, never snapping); dormant on touch,
 * where the drift alone is the substrate. Ruled DISTINCT from ambient-idle
 * (opts single EXISTING elements into glow/float/shimmer — it cannot compose
 * a multi-orb atmosphere layer) and from shader-surface (the WebGL/canvas
 * ground — this field is the gap's explicit WebGL-free answer: no context to
 * lose, no DPR to cap, the static frame IS the markup).
 *
 * Expected markup — the builder authors the empty layer, the component
 * composes the orbs inside it (chrome, aria-hidden by construction):
 *   <div data-ad-orbfield aria-hidden="true"></div>       (count via
 *   data-ad-orbfield="2" — default 3)
 *
 * Usage:  awardAmbientOrbField.init(root, { selector, amplitude })
 *   root       Element|Document  scope (default document)
 *   selector   string  layer containers (default '[data-ad-orbfield]')
 *   amplitude  number  pointer-lean reach in px (default 48; fine pointer only)
 * Returns { destroy() }. Idempotent per container.
 *
 * Tokens: --ad-accent, --ad-ink, --ad-ground-2 (the three orb hues, mixed).
 *
 * PERF + floors: animations are authored paused; ONE IntersectionObserver
 * flips `is-drifting` per layer so an off-screen field costs zero, and a
 * visibilitychange root class re-pauses everything in a hidden tab. The
 * pointer rAF runs only while a fine pointer is actually moving and stops
 * once the lerp settles. reduced-motion: the composed static field stands —
 * no drift, no pointer channel, orbs at their authored rest.
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-ambient-orb-field-css';
  var HIDDEN_CLASS = 'ad-orbfield-page-hidden';
  var ACCENT = 'var(--ad-accent,oklch(62% 0.2 25))';
  var INK = 'var(--ad-ink,oklch(96% 0 0))';
  var GROUND2 = 'var(--ad-ground-2,oklch(18% 0.01 260))';
  var LERP = 0.06;          // per-frame pointer chase — decelerating, never a snap
  var SETTLE = 0.15;        // px delta under which the pointer loop parks itself

  // three orb characters: hue, geometry, drift cycle, pointer depth rate
  var ORBS = [
    { color: 'color-mix(in oklch,' + ACCENT + ' 70%,transparent)',
      size: '72vmin', pos: 'top:-14%;left:-10%;', opacity: 0.22,
      anim: 'ad-orb-a 17s', rate: 1 },
    { color: 'color-mix(in oklch,' + ACCENT + ' 45%,' + INK + ' 12%)',
      size: '58vmin', pos: 'bottom:-16%;right:-8%;', opacity: 0.18,
      anim: 'ad-orb-b 23s', rate: -0.7 },
    { color: 'color-mix(in oklch,' + INK + ' 55%,' + GROUND2 + ' 30%)',
      size: '64vmin', pos: 'top:32%;left:52%;', opacity: 0.15,
      anim: 'ad-orb-c 20s', rate: 0.45 }
  ];

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
    var css =
      '.ad-orbfield{position:fixed;inset:0;z-index:0;pointer-events:none;overflow:clip;}' +
      '.ad-orbfield__o{position:absolute;}' +
      '.ad-orbfield__i{width:100%;height:100%;border-radius:50%;' +
        'filter:blur(80px);animation-play-state:paused;}' +
      '.ad-orbfield.is-drifting .ad-orbfield__i{animation-play-state:running;' +
        'will-change:transform;}' +
      'html.' + HIDDEN_CLASS + ' .ad-orbfield__i{animation-play-state:paused;}';
    ORBS.forEach(function (o, i) {
      css +=
        '.ad-orbfield__o[data-orb="' + i + '"]{width:' + o.size + ';height:' + o.size + ';' +
          o.pos + '}' +
        '.ad-orbfield__o[data-orb="' + i + '"] .ad-orbfield__i{' +
          'background:radial-gradient(closest-side,' + o.color + ',transparent 72%);' +
          'opacity:' + o.opacity + ';' +
          'animation-name:ad-orb-' + 'abc'[i] + ';' +
          'animation-duration:' + o.anim.split(' ')[1] + ';' +
          'animation-timing-function:ease-in-out;' +
          'animation-iteration-count:infinite;animation-direction:alternate;}';
    });
    css +=
      '@keyframes ad-orb-a{from{transform:translate3d(0,0,0) scale(1);}' +
        'to{transform:translate3d(4vw,2vh,0) scale(1.1);}}' +
      '@keyframes ad-orb-b{from{transform:translate3d(0,0,0) scale(1);}' +
        'to{transform:translate3d(-3vw,-3vh,0) scale(1.08);}}' +
      '@keyframes ad-orb-c{from{transform:translate3d(0,0,0) scale(1.05);}' +
        'to{transform:translate3d(-2.5vw,3vh,0) scale(1);}}' +
      '@media (prefers-reduced-motion: reduce){' +
        '.ad-orbfield__i{animation:none;will-change:auto;}}';
    s.textContent = css;
    document.head.appendChild(s);
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-orbfield]';
    var amplitude = opts.amplitude != null ? opts.amplitude : 48;
    injectCss();

    var units = [];
    Array.prototype.forEach.call(root.querySelectorAll(selector), function (el) {
      if (el.__adOrbField) return;
      el.__adOrbField = true;
      el.classList.add('ad-orbfield');
      var count = Math.max(2, Math.min(3, parseInt(el.getAttribute('data-ad-orbfield'), 10) || 3));
      var orbs = [];
      for (var i = 0; i < count; i++) {
        var o = document.createElement('div');
        o.className = 'ad-orbfield__o';
        o.setAttribute('data-orb', String(i));
        var inner = document.createElement('div');
        inner.className = 'ad-orbfield__i';
        o.appendChild(inner);
        el.appendChild(o);
        orbs.push({ el: o, x: 0, y: 0, tx: 0, ty: 0, rate: ORBS[i].rate });
      }
      units.push({ el: el, orbs: orbs, inView: true });
    });

    var io = null, onVis = null, onMove = null, rafId = 0;

    function frame() {
      rafId = 0;
      var moving = false;
      units.forEach(function (u) {
        if (!u.inView) return;
        u.orbs.forEach(function (orb) {
          orb.x += (orb.tx - orb.x) * LERP;
          orb.y += (orb.ty - orb.y) * LERP;
          if (Math.abs(orb.tx - orb.x) > SETTLE || Math.abs(orb.ty - orb.y) > SETTLE) moving = true;
          orb.el.style.transform =
            'translate3d(' + orb.x.toFixed(2) + 'px,' + orb.y.toFixed(2) + 'px,0)';
        });
      });
      if (moving && !document.hidden) rafId = global.requestAnimationFrame(frame);
    }
    function kick() { if (!rafId) rafId = global.requestAnimationFrame(frame); }

    if (units.length && !reduce()) {
      if ('IntersectionObserver' in global) {
        io = new IntersectionObserver(function (entries) {
          entries.forEach(function (e) {
            var u = units.filter(function (x) { return x.el === e.target; })[0];
            if (u) u.inView = e.isIntersecting;
            e.target.classList.toggle('is-drifting', e.isIntersecting);
          });
        }, { threshold: 0 });
        units.forEach(function (u) { io.observe(u.el); });
      } else {
        units.forEach(function (u) { u.el.classList.add('is-drifting'); });
      }
      onVis = function () {
        document.documentElement.classList.toggle(HIDDEN_CLASS, document.hidden);
        if (!document.hidden) kick();
      };
      document.addEventListener('visibilitychange', onVis);
      onVis();

      if (finePointer()) {
        onMove = function (e) {
          // normalized pointer offset from viewport center, -1..1 each axis
          var nx = (e.clientX / Math.max(1, global.innerWidth)) * 2 - 1;
          var ny = (e.clientY / Math.max(1, global.innerHeight)) * 2 - 1;
          units.forEach(function (u) {
            u.orbs.forEach(function (orb) {
              orb.tx = nx * amplitude * orb.rate;
              orb.ty = ny * amplitude * orb.rate;
            });
          });
          kick();
        };
        global.addEventListener('pointermove', onMove, { passive: true });
      }
    }

    return {
      destroy: function () {
        if (rafId) global.cancelAnimationFrame(rafId);
        if (io) io.disconnect();
        if (onVis) document.removeEventListener('visibilitychange', onVis);
        if (onMove) global.removeEventListener('pointermove', onMove);
        document.documentElement.classList.remove(HIDDEN_CLASS);
        units.forEach(function (u) {
          u.orbs.forEach(function (orb) {
            if (orb.el.parentNode) orb.el.parentNode.removeChild(orb.el);
          });
          u.el.classList.remove('ad-orbfield', 'is-drifting');
          delete u.el.__adOrbField;
        });
        units = [];
        var s = document.getElementById(CSS_ID);
        if (s) s.parentNode.removeChild(s);
      }
    };
  }

  global.awardAmbientOrbField = { init: init };
})(typeof window !== 'undefined' ? window : this);
