/*
 * page-transition-choreography — the between-view spectacle channel (winners:
 * Ponpon Mania — SOTM 2025-10 + Dev Award, per-transition WebGL shader mixes:
 * previous AND next pages render simultaneously while a tween drives the
 * blend; 21 TSI — SOTD 2025-04-12 + FWA + CSSDA, morphing section
 * transitions; Mat Voyce — SOTD + FWA, seamless page transitions). The
 * momentum model was scroll-within-page only — this is the between-view
 * grammar: on a multi-route maximal build the transition is peak-adjacent,
 * one channel in the momentum floor. NOT an alias of the existing transition
 * tools, ruled on the winners' mechanics: route-view-transition-carrier is
 * the quiet whole-view crossfade (minimalist register), curtain-transition
 * wipes a FLAT ground bar, continuous-work-transition morphs one shared
 * figure — none blends two live scenes and none morphs its leading edge.
 * Two expressions, picked by capability:
 *
 *   mix   the Ponpon delegation — the builder's engine renders BOTH scenes
 *         and exposes one blend uniform; this file owns only the clock.
 *         go(fn) calls fn FIRST (mount the incoming scene; may return a
 *         promise), then drives opts.mix(p) 0->1 through the signature ease,
 *         then resolves so the engine can dispose the outgoing scene. The
 *         component never touches WebGL — the shader is the engine's. A
 *         failed mount skips the blend entirely (the outgoing scene stands,
 *         the error surfaces) — never a blend into garbage. On coarse
 *         pointers the double-render is the fps risk the gap names: the mix
 *         path degrades to a FAST container crossfade, never a sub-30fps
 *         blocking blend.
 *
 *   wipe  the 21 TSI register, DOM-expressed (the default when no mix is
 *         given): a fixed panel covers the view with a MORPHING leading edge
 *         — an oversized ellipse lip, anchored on the panel edge, that
 *         swells with the launch velocity and relaxes flat as the panel
 *         decelerates into cover (the inertia morph IS the tell; a flat bar
 *         is curtain-transition's move) — fn swaps the world at full cover,
 *         then the panel exits upward with the same morph on the trailing
 *         edge. Transform-only on two promoted layers; cheap enough to keep
 *         on touch.
 *
 * No authored markup, nothing rendered at rest; the panel is JS-created,
 * aria-hidden, inert at rest, and blocks clicks only mid-wipe.
 * reduced-motion: go(fn) is an INSTANT CUT — fn runs immediately, no panel,
 * no blend (the gap's own degrade order).
 *
 * Usage:  var ptc = awardPageTransitionChoreography.init(root, opts)
 *   root       Element|Document  kept for the library contract
 *   mix        function(p)  the engine's blend hook (0..1) — presence picks
 *                           the mix expression
 *   container  string  crossfade-fallback view root (default '[data-ad-view]',
 *                      then document.body) — used only by the coarse-pointer
 *                      mix degrade
 *   color      string  wipe panel ground (default var(--ad-ptc-ground), then
 *                      --ad-ground-2)
 *   zIndex     number  wipe panel stacking (default 9998)
 * Returns { go(fn, opts2), destroy() } — the extended handle.
 *
 *   go(fn, { timeout })
 *     Runs the route/view swap inside the choreography. fn may return a
 *     promise; it is capped by `timeout` (default 2000ms) so a hung fetch
 *     never strands a covered view or an unblended stage. Returns a promise
 *     resolving when the transition completes. A go() during a go() is a
 *     no-op returning the in-flight promise. An fn that throws or rejects
 *     still restores the view; its error surfaces through the promise.
 *
 * Idempotent — one choreography per page; a second init returns the live
 * handle. destroy() cancels any run (its promise resolves), removes the
 * panel and the stylesheet.
 *
 * Tokens: --ad-ptc-dur (per-phase / blend duration, default 640ms — the
 * tempo default is illustrative, no winner published interior numbers) +
 * --ad-ptc-ease (falls back to --ad-ease-signature, then
 * cubic-bezier(.16,1,.3,1)); --ad-ptc-ground (falls back to --ad-ground-2).
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-page-transition-choreography-css';
  var DEFAULT_TIMEOUT = 2000;
  var LIP_FLAT = 0.12;   // the edge at rest/arrival — near-flat
  var LIP_FULL = 1;      // the edge at full speed — the bulge
  var LIP_PEAK = 0.25;   // phase offset where the bulge peaks (launch velocity)
  var FAST_FADE = 0.35;  // coarse-pointer mix degrade: dur * this per side
  var instance = null;

  var reduce = function () {
    return global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches;
  };
  var coarse = function () {
    return global.matchMedia && global.matchMedia('(pointer: coarse)').matches;
  };

  function injectCss(zIndex) {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    // The rail carries lip + body + lip (30/100/30lvh) and travels 160lvh —
    // at 0 the body covers the viewport exactly, both lips just offscreen.
    s.textContent =
      '.ad-ptc{position:fixed;inset:0;z-index:' + zIndex + ';overflow:hidden;' +
      'pointer-events:none;visibility:hidden;}' +
      '.ad-ptc[data-live]{visibility:visible;pointer-events:auto;}' +
      '.ad-ptc__rail{position:absolute;left:0;width:100%;top:-30lvh;height:160lvh;' +
      'transform:translate3d(0,160lvh,0);will-change:transform;}' +
      '.ad-ptc__body{position:absolute;left:0;right:0;top:30lvh;height:100lvh;}' +
      // lips center ON the body edges (origin center) so the bulge stays
      // anchored to the edge as it scales — never dipping under the body
      '.ad-ptc__lip{position:absolute;left:-20%;width:140%;height:30lvh;' +
      'border-radius:50%;transform-origin:center;will-change:transform;}' +
      '.ad-ptc__lip--top{top:15lvh;transform:scaleY(' + LIP_FLAT + ');}' +
      '.ad-ptc__lip--bot{top:115lvh;transform:scaleY(' + LIP_FLAT + ');}';
    document.head.appendChild(s);
  }

  function styles() {
    var cs = getComputedStyle(document.documentElement);
    var dur = parseFloat((cs.getPropertyValue('--ad-ptc-dur') || '').trim()) || 640;
    var ease = (cs.getPropertyValue('--ad-ptc-ease') || '').trim() ||
      (cs.getPropertyValue('--ad-ease-signature') || '').trim() ||
      'cubic-bezier(.16,1,.3,1)';
    return { dur: dur, ease: ease };
  }

  // Newton-Raphson cubic-bezier solve — the mix tween honors the same CSS
  // ease token the wipe rides, without a GSAP dependency.
  function bezier(x1, y1, x2, y2) {
    function calc(t, c1, c2) {
      return ((1 - 3 * c2 + 3 * c1) * t + (3 * c2 - 6 * c1)) * t * t + 3 * c1 * t;
    }
    function slope(t, c1, c2) {
      return 3 * (1 - 3 * c2 + 3 * c1) * t * t + 2 * (3 * c2 - 6 * c1) * t + 3 * c1;
    }
    return function (x) {
      if (x <= 0) return 0;
      if (x >= 1) return 1;
      var t = x;
      for (var i = 0; i < 5; i++) {
        var s = slope(t, x1, x2);
        if (!s) break;
        t -= (calc(t, x1, x2) - x) / s;
      }
      return calc(t, y1, y2);
    };
  }
  function easeFn(css) {
    var m = /cubic-bezier\(\s*([-\d.]+)\s*,\s*([-\d.]+)\s*,\s*([-\d.]+)\s*,\s*([-\d.]+)\s*\)/.exec(css);
    if (m) return bezier(+m[1], +m[2], +m[3], +m[4]);
    if (/^linear$/.test(css)) return function (x) { return x; };
    return bezier(0.16, 1, 0.3, 1);
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    if (instance) return instance.handle;

    var mix = typeof opts.mix === 'function' ? opts.mix : null;
    var containerSel = opts.container || '[data-ad-view]';
    var zIndex = opts.zIndex != null ? opts.zIndex : 9998;
    var color = opts.color ||
      'var(--ad-ptc-ground,var(--ad-ground-2,oklch(18% 0.01 260)))';

    var state = { playing: null, anims: [], raf: 0, timer: 0, abort: null, destroyed: false };
    var panel = null, rail = null, lipTop = null, lipBot = null;

    function ensurePanel() {
      if (panel) return;
      injectCss(zIndex);
      panel = document.createElement('div');
      panel.className = 'ad-ptc';
      panel.setAttribute('aria-hidden', 'true');
      rail = document.createElement('div');
      rail.className = 'ad-ptc__rail';
      var body = document.createElement('div');
      body.className = 'ad-ptc__body';
      lipTop = document.createElement('div');
      lipTop.className = 'ad-ptc__lip ad-ptc__lip--top';
      lipBot = document.createElement('div');
      lipBot.className = 'ad-ptc__lip ad-ptc__lip--bot';
      body.style.background = color;
      lipTop.style.background = color;
      lipBot.style.background = color;
      rail.appendChild(lipTop);
      rail.appendChild(body);
      rail.appendChild(lipBot);
      panel.appendChild(rail);
      (document.body || document.documentElement).appendChild(panel);
    }

    function container() {
      return document.querySelector(containerSel) || document.body;
    }

    // Run fn with a settle cap. Never rejects — {error} rides back so the
    // restore always plays; go() re-throws after the view is whole again.
    function callFn(fn, ms) {
      return new Promise(function (resolve) {
        var settled = false;
        var finish = function (error) {
          if (settled) return;
          settled = true;
          if (state.timer) { clearTimeout(state.timer); state.timer = 0; }
          state.abort = null;
          resolve({ error: error || null });
        };
        state.abort = function () { finish(null); };
        state.timer = setTimeout(function () { finish(null); }, ms);
        var out;
        try { out = fn ? fn() : undefined; }
        catch (err) { finish(err); return; }
        Promise.resolve(out).then(
          function () { finish(null); },
          function (err) { finish(err); }
        );
      });
    }

    function animate(el, keyframes, dur, ease) {
      return new Promise(function (resolve) {
        if (state.destroyed || !el.animate) { resolve(); return; }
        var anim = el.animate(keyframes, { duration: dur, easing: ease, fill: 'forwards' });
        state.anims.push(anim);
        var settled = false;
        var done = function () {
          if (settled) return;
          settled = true;
          var i = state.anims.indexOf(anim);
          if (i !== -1) state.anims.splice(i, 1);
          var last = keyframes[keyframes.length - 1];
          for (var k in last) if (k !== 'offset') el.style[k] = last[k];
          try { anim.cancel(); } catch (e) {}
          resolve();
        };
        anim.onfinish = done;
        anim.oncancel = done; // destroy() cancels mid-phase → the run still settles
      });
    }

    // rAF tween for the delegated shader mix — clamped, monotonic, and a
    // destroy() mid-blend snaps to 1 so the engine is never stranded mid-mix.
    function tweenMix(dur, ease) {
      return new Promise(function (resolve) {
        var fn = easeFn(ease);
        var t0 = 0;
        var step = function (now) {
          if (state.destroyed) { mix(1); state.raf = 0; resolve(); return; }
          if (!t0) t0 = now;
          var p = Math.min(1, (now - t0) / dur);
          mix(fn(p));
          if (p < 1) state.raf = global.requestAnimationFrame(step);
          else { state.raf = 0; resolve(); }
        };
        state.raf = global.requestAnimationFrame(step);
      });
    }

    function go(fn, opts2) {
      if (state.destroyed) return Promise.resolve();
      if (state.playing) return state.playing;
      var timeout = opts2 && opts2.timeout != null ? opts2.timeout : DEFAULT_TIMEOUT;

      // The gap's degrade order: reduced motion is an instant cut.
      if (reduce()) {
        state.playing = callFn(fn, timeout).then(function (r) {
          state.playing = null;
          if (r.error) throw r.error;
        });
        return state.playing;
      }

      var s = styles();

      if (mix) {
        // Coarse pointer: fast crossfade on the view container — the engine
        // still swaps scenes inside fn, but never double-renders a blend.
        if (coarse()) {
          var el = container();
          state.playing = animate(el, [{ opacity: 1 }, { opacity: 0 }], s.dur * FAST_FADE, s.ease)
            .then(function () { return callFn(fn, timeout); })
            .then(function (r) {
              return animate(el, [{ opacity: 0 }, { opacity: 1 }], s.dur * FAST_FADE, s.ease)
                .then(function () {
                  if (!state.destroyed) el.style.opacity = '';
                  state.playing = null;
                  if (r.error) throw r.error;
                });
            });
          return state.playing;
        }
        // The Ponpon shape: mount the incoming scene, then blend 0 -> 1.
        state.playing = callFn(fn, timeout).then(function (r) {
          if (r.error) { state.playing = null; throw r.error; }
          return tweenMix(s.dur, s.ease).then(function () { state.playing = null; });
        });
        return state.playing;
      }

      // The wipe: cover with the leading edge morphing — the bulge swells as
      // the panel launches (velocity) and relaxes flat as it decelerates into
      // cover (inertia); the exit mirrors it on the trailing edge.
      ensurePanel();
      panel.setAttribute('data-live', '');
      lipTop.style.transform = 'scaleY(' + LIP_FLAT + ')';
      lipBot.style.transform = 'scaleY(' + LIP_FLAT + ')';
      rail.style.transform = 'translate3d(0,160lvh,0)';
      state.playing = Promise.all([
        animate(rail, [
          { transform: 'translate3d(0,160lvh,0)' },
          { transform: 'translate3d(0,0,0)' }
        ], s.dur, s.ease),
        animate(lipTop, [
          { transform: 'scaleY(' + LIP_FLAT + ')', easing: s.ease },
          { transform: 'scaleY(' + LIP_FULL + ')', offset: LIP_PEAK, easing: s.ease },
          { transform: 'scaleY(' + LIP_FLAT + ')' }
        ], s.dur, 'linear')
      ])
        .then(function () { return callFn(fn, timeout); })
        .then(function (r) {
          return Promise.all([
            animate(rail, [
              { transform: 'translate3d(0,0,0)' },
              { transform: 'translate3d(0,-160lvh,0)' }
            ], s.dur, s.ease),
            animate(lipBot, [
              { transform: 'scaleY(' + LIP_FLAT + ')', easing: s.ease },
              { transform: 'scaleY(' + LIP_FULL + ')', offset: LIP_PEAK, easing: s.ease },
              { transform: 'scaleY(' + LIP_FLAT + ')' }
            ], s.dur, 'linear')
          ]).then(function () {
            if (!state.destroyed) {
              panel.removeAttribute('data-live');
              rail.style.transform = 'translate3d(0,160lvh,0)';
            }
            state.playing = null;
            if (r.error) throw r.error;
          });
        });
      return state.playing;
    }

    var handle = {
      go: go,
      destroy: function () {
        state.destroyed = true;
        state.anims.slice().forEach(function (a) { try { a.cancel(); } catch (e) {} });
        state.anims.length = 0;
        if (state.raf) { global.cancelAnimationFrame(state.raf); state.raf = 0; }
        if (state.abort) state.abort();
        if (state.timer) { clearTimeout(state.timer); state.timer = 0; }
        var el = document.querySelector(containerSel) || document.body;
        if (el) el.style.opacity = '';
        if (panel && panel.parentNode) panel.parentNode.removeChild(panel);
        panel = rail = lipTop = lipBot = null;
        instance = null;
        var st = document.getElementById(CSS_ID);
        if (st && st.parentNode) st.parentNode.removeChild(st);
      }
    };
    instance = { handle: handle };
    return handle;
  }

  global.awardPageTransitionChoreography = { init: init };
})(typeof window !== 'undefined' ? window : this);
