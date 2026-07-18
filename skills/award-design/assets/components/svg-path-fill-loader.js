/*
 * svg-path-fill-loader — the mark that fills, then dissolves (winner: Depo
 * Luxe — SOTD + Developer Award Jul 7 2026, 7.62, Animations 8.40; the
 * video-preloader + SVG-logo fill, and the recipe's own annotation: 'SVG
 * logo fill then dissolve, no hard cut'. Already flagged
 * MISSING:svg-path-fill-loader in recipes.json — engine-world-depoluxe's
 * loader field. The award page names the SVG-fill entrance; interior
 * timings are executable defaults). The builder's SVG wordmark stands
 * center-stage as a faint ghost; its FILL RISES through the paths with
 * honest load progress — the mark ITSELF is the progress instrument, no
 * bar, no counter — then holds one beat at full and the whole scene
 * DISSOLVES over the already-painted hero: no hard cut, the fill's
 * completion IS the handoff.
 * Ruled DISTINCT, not an alias: branded-preloader seats a brand mark
 * BESIDE a real-progress readout and recedes — the mark never measures;
 * counter-loader / stepped-counter-loader are numeric instruments;
 * flip-handoff-loader's mark TRAVELS into the header (element continuity);
 * type-forward-intro-loader is a type intro. Here the mark is the gauge
 * and it dissolves in place.
 * The fill stays honest (the library's loader law): it eases toward 90%
 * over `minDuration`, holds until the real window `load`, then settles to
 * full and the dissolve plays.
 *
 * Content-visible at rest: the scene is authored `hidden` — a dead script
 * never covers the page (no-JS paints the hero directly). Reduced motion
 * (or a repeat visit under sessionOnce): the scene never shows and onDone
 * fires immediately — the beat is stylistic, never load-bearing.
 *
 * Expected markup — the builder authors the scene with the REAL mark
 * (any paths/shapes, its own fills):
 *   <div data-ad-svg-loader hidden>
 *     <svg viewBox="…" aria-label="Maison">…paths…</svg>
 *   </div>
 *
 * Usage:  awardSvgPathFillLoader.init(root, opts)
 *   root         Element|Document  scope (default document)
 *   selector     string    the scene (default '[data-ad-svg-loader]')
 *   minDuration  ms        floor for the 0→90% ease (default 1600)
 *   sessionOnce  boolean   skip after the first completed run this session
 *   onDone       function  runs once after the dissolve — start the hero
 *                          here. Fires on every skip path too.
 * Returns { destroy() }. Idempotent — while running it returns the live
 * handle; once done (or skipped) a re-init is a no-op. destroy() cancels
 * the run, restores the scene's `hidden` and the body scroll lock, and
 * removes the stylesheet and the built fill layer.
 *
 * A11y + perf: the mark wrapper announces a real progressbar
 * (aria-valuenow tracks the fill) and the scene aria-busy; the rising fill
 * is a clip-path inset on a GHOST+FILL pair the component builds from the
 * authored svg (one clone — the author's mark is never mutated); the
 * dissolve is opacity-only on the scene layer. Scroll is locked only while
 * the scene is the only UI.
 *
 * Tokens: --ad-ground (scene ground), --ad-ink (ghost tint reference —
 * the mark's own fills stay the author's), --ad-dur-reveal +
 * --ad-ease-signature (the dissolve), --ad-dur-base (the held beat).
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-svg-path-fill-loader-css';
  var SEEN_KEY = 'ad-svg-path-fill-loader-done';
  var GHOST_OPACITY = 0.16; // the unfilled mark — present, never absent

  var reduce = function () {
    return !!(global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches);
  };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    // Scoped under .ad-spfl — the class JS adds after removing `hidden`;
    // no-JS never gets the class, so nothing at rest covers the page.
    s.textContent =
      '.ad-spfl{position:fixed;inset:0;z-index:100000;display:grid;' +
      'place-items:center;background:var(--ad-ground,oklch(14% 0.01 260));' +
      'will-change:opacity;}' +
      '.ad-spfl.is-leaving{opacity:0;transition:opacity ' +
      'var(--ad-dur-reveal,800ms) var(--ad-ease-signature,cubic-bezier(.16,1,.3,1));}' +
      '.ad-spfl__mark{position:relative;width:min(46vw,22rem);}' +
      '.ad-spfl__mark svg{display:block;width:100%;height:auto;}' +
      // the ghost: the author's mark, faint — the gauge's empty state
      '.ad-spfl__mark > svg:first-child{opacity:' + GHOST_OPACITY + ';}' +
      // the fill: the same mark, clipped from the bottom, JS-risen
      '.ad-spfl__fill{position:absolute;inset:0;' +
      'clip-path:inset(100% 0 0 0);will-change:clip-path;}' +
      '.ad-spfl__fill svg{opacity:1;}';
    document.head.appendChild(s);
  }

  function styles() {
    var cs = getComputedStyle(document.documentElement);
    function v(name, fallback) {
      return (cs.getPropertyValue(name) || '').trim() || fallback;
    }
    return {
      durReveal: parseFloat(v('--ad-dur-reveal', '800ms')) || 800,
      durBase: parseFloat(v('--ad-dur-base', '420ms')) || 420
    };
  }

  // sessionStorage throws in some privacy modes — a loader must never.
  function seen() {
    try { return global.sessionStorage.getItem(SEEN_KEY) === '1'; }
    catch (e) { return false; }
  }
  function markSeen() {
    try { global.sessionStorage.setItem(SEEN_KEY, '1'); } catch (e) {}
  }

  function easeOutCubic(p) { return 1 - Math.pow(1 - p, 3); }

  var state = null; // running | done — one loader beat per page

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    if (state) return state.handle || { destroy: function () {} };

    var selector = opts.selector || '[data-ad-svg-loader]';
    var minDuration = opts.minDuration != null ? opts.minDuration : 1600;
    var scene = root.querySelector(selector);
    var svg = scene && scene.querySelector('svg');

    function finish(fired) {
      if (!fired && opts.onDone) opts.onDone();
    }

    // Skip paths: no scene, reduce, or an already-seen session — the page
    // stands and the first beat never depends on the flight.
    if (!scene || !svg || reduce() || (opts.sessionOnce && seen())) {
      state = { handle: { destroy: function () { state = null; } } };
      finish(false);
      return state.handle;
    }

    injectCss();
    var t = styles();

    // Build the gauge: wrap the authored svg in a mark box and lay ONE
    // clone over it as the rising fill — the author's mark is never mutated.
    var mark = document.createElement('div');
    mark.className = 'ad-spfl__mark';
    mark.setAttribute('role', 'progressbar');
    mark.setAttribute('aria-valuemin', '0');
    mark.setAttribute('aria-valuemax', '100');
    mark.setAttribute('aria-valuenow', '0');
    var fillLayer = document.createElement('div');
    fillLayer.className = 'ad-spfl__fill';
    fillLayer.setAttribute('aria-hidden', 'true');
    var clone = svg.cloneNode(true);
    clone.removeAttribute('aria-label');
    fillLayer.appendChild(clone);
    svg.parentNode.insertBefore(mark, svg);
    mark.appendChild(svg);
    mark.appendChild(fillLayer);

    scene.removeAttribute('hidden');
    scene.classList.add('ad-spfl');
    scene.setAttribute('aria-busy', 'true');
    var prevOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden'; // the scene is the only UI

    var loaded = document.readyState === 'complete';
    var onLoad = function () { loaded = true; };
    global.addEventListener('load', onLoad);

    var start = performance.now();
    var raf = 0;
    var fill = 0;

    function setFill(v) {
      fill = v;
      fillLayer.style.clipPath = 'inset(' + ((1 - v) * 100).toFixed(2) + '% 0 0 0)';
      mark.setAttribute('aria-valuenow', String(Math.round(v * 100)));
    }

    function teardown(restoreScene) {
      if (raf) { global.cancelAnimationFrame(raf); raf = 0; }
      global.removeEventListener('load', onLoad);
      document.body.style.overflow = prevOverflow;
      if (restoreScene) {
        scene.classList.remove('ad-spfl', 'is-leaving');
        scene.setAttribute('hidden', '');
        scene.removeAttribute('aria-busy');
        // unwrap: the authored svg returns to the scene as it was
        if (mark.parentNode) {
          mark.parentNode.insertBefore(svg, mark);
          mark.parentNode.removeChild(mark);
        }
      }
      var s = document.getElementById(CSS_ID);
      if (s && s.parentNode) s.parentNode.removeChild(s);
    }

    function dissolve() {
      // the handoff beat: full mark held for one base duration, then the
      // scene dissolves over the painted hero — no hard cut
      setTimeout(function () {
        scene.classList.add('is-leaving');
        setTimeout(function () {
          if (!state) return; // destroyed mid-dissolve — teardown already ran
          teardown(true);
          markSeen();
          state.done = true;
          finish(false);
        }, t.durReveal + 60);
      }, t.durBase);
    }

    function frame(now) {
      raf = 0;
      var p = Math.min(1, (now - start) / minDuration);
      // honest: ease to 90%, hold for the real window load, settle
      var target = easeOutCubic(p) * 0.9;
      if (p >= 1 && loaded) target = 1;
      if (target > fill) setFill(target);
      if (fill >= 1) { dissolve(); return; }
      raf = global.requestAnimationFrame(frame);
    }
    raf = global.requestAnimationFrame(frame);

    state = {
      done: false,
      handle: {
        destroy: function () {
          if (!state) return;
          teardown(!state.done);
          state = null;
        }
      }
    };
    return state.handle;
  }

  global.awardSvgPathFillLoader = { init: init };
})(typeof window !== 'undefined' ? window : this);
