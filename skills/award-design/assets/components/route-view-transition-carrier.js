/*
 * route-view-transition-carrier — cross-navigation momentum carrier (winners:
 * Cyd Stumpel — Portfolio 2025; Stefan Vitasovic; Pacome Pertant). Multi-view
 * portfolios are SPAs where the home→project-detail transition is a signature
 * beat — this carrier crossfades/morphs the view swap instead of a hard cut.
 * Two expressions, picked by capability:
 *   native   document.startViewTransition wraps the swap (Cyd Stumpel's
 *            CSS-native expression) — the injected stylesheet retunes the
 *            default root crossfade to the carrier's tokens, and any
 *            view-transition-name the builder sets on shared elements morphs
 *            for free.
 *   fallback a WAAPI opacity crossfade on the view container — out over half
 *            the duration, swap under cover, in over the other half (Stefan's
 *            Codrops-verified AnimatePresence crossfade, .5s easeQuadInOut,
 *            is the duration/ease default).
 * An imperative tool like curtain-transition, not an observer: the builder
 * calls go(fn) and swaps DOM, scrolls, or rewrites the view inside fn — so the
 * carry is input-agnostic (a tap navigates through the same beat as a click).
 * No authored markup, nothing rendered at rest; reduced-motion runs fn
 * immediately with no animation (the swap is instant, never blocked).
 *
 * Usage:  var carrier = awardRouteCarrier.init(root, { container })
 *   root       Element|Document  kept for the library contract
 *   container  string  fallback-path view root selector (default
 *                      '[data-ad-view]'; falls back to document.body)
 * Returns { go(fn, opts2), destroy() } — the extended handle.
 *
 *   go(fn, { timeout })
 *     Runs the swap inside the transition. fn may return a promise; the
 *     carrier holds until it settles, capped by `timeout` (default 2000ms) so
 *     a hung fetch never strands a faded view. Returns a promise resolving
 *     when the transition completes. A go() during a go() is a no-op
 *     returning the in-flight promise. An fn that throws or rejects still
 *     restores the view; its error surfaces through the returned promise.
 *
 * Idempotent — one carrier per page; a second init returns the live handle.
 * destroy() cancels any run (its promise resolves), restores the container,
 * and removes the stylesheet.
 *
 * Tokens: --ad-route-dur (500ms) + --ad-route-ease (cubic-bezier(.45,0,.55,1),
 * easeQuadInOut) — Stefan's verified crossfade is the default register.
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-route-carrier-css';
  var DEFAULT_TIMEOUT = 2000;
  var DUR = 'var(--ad-route-dur,500ms)';
  var EASE = 'var(--ad-route-ease,cubic-bezier(.45,0,.55,1))';
  var instance = null;

  var reduce = function () {
    return global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches;
  };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    // Native path: retune the UA's root crossfade to the carrier's register.
    s.textContent =
      '::view-transition-old(root),::view-transition-new(root){' +
      'animation-duration:' + DUR + ';' +
      'animation-timing-function:' + EASE + ';}';
    document.head.appendChild(s);
  }

  function styles() {
    var cs = getComputedStyle(document.documentElement);
    return {
      dur: parseFloat((cs.getPropertyValue('--ad-route-dur') || '').trim()) || 500,
      ease: (cs.getPropertyValue('--ad-route-ease') || '').trim() ||
        'cubic-bezier(.45,0,.55,1)'
    };
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    if (instance) return instance.handle;
    injectCss();

    var containerSel = opts.container || '[data-ad-view]';
    var state = { playing: null, anim: null, timer: 0, abort: null, vt: null, destroyed: false };

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

    function fade(el, from, to, dur, ease) {
      return new Promise(function (resolve) {
        if (state.destroyed || !el.animate) { resolve(); return; }
        var anim = el.animate([{ opacity: from }, { opacity: to }],
          { duration: dur, easing: ease, fill: 'forwards' });
        state.anim = anim;
        var settled = false;
        var done = function () {
          // the cancel() below re-fires done via the async cancel event — a
          // re-run would re-write the inline opacity AFTER go()'s cleanup
          if (settled) return;
          settled = true;
          if (state.anim === anim) state.anim = null;
          el.style.opacity = String(to);
          try { anim.cancel(); } catch (e) {}
          resolve();
        };
        anim.onfinish = done;
        anim.oncancel = done; // destroy() cancels mid-fade → the run still settles
      });
    }

    function go(fn, opts2) {
      if (state.destroyed) return Promise.resolve();
      if (state.playing) return state.playing;
      var timeout = opts2 && opts2.timeout != null ? opts2.timeout : DEFAULT_TIMEOUT;

      if (reduce()) {
        state.playing = callFn(fn, timeout).then(function (r) {
          state.playing = null;
          if (r.error) throw r.error;
        });
        return state.playing;
      }

      // Native: the browser snapshots, fn swaps, old/new crossfade under the
      // injected register; shared view-transition-name elements morph.
      if (typeof document.startViewTransition === 'function') {
        var result = null;
        var vt = document.startViewTransition(function () {
          return callFn(fn, timeout).then(function (r) { result = r; });
        });
        state.vt = vt;
        state.playing = vt.finished
          .catch(function () {}) // a skipped transition is not a swap failure
          .then(function () {
            state.vt = null;
            state.playing = null;
            if (result && result.error) throw result.error;
          });
        return state.playing;
      }

      // Fallback: out over half the duration, swap under cover, in over the rest.
      var el = container();
      var s = styles();
      state.playing = fade(el, 1, 0, s.dur / 2, s.ease)
        .then(function () { return callFn(fn, timeout); })
        .then(function (r) {
          return fade(el, 0, 1, s.dur / 2, s.ease).then(function () {
            if (!state.destroyed) el.style.opacity = '';
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
        if (state.anim) { state.anim.cancel(); state.anim = null; }
        if (state.vt) { try { state.vt.skipTransition(); } catch (e) {} state.vt = null; }
        if (state.abort) state.abort();
        if (state.timer) { clearTimeout(state.timer); state.timer = 0; }
        var el = container();
        if (el) el.style.opacity = '';
        instance = null;
        var st = document.getElementById(CSS_ID);
        if (st && st.parentNode) st.parentNode.removeChild(st);
      }
    };
    instance = { handle: handle };
    return handle;
  }

  global.awardRouteCarrier = { init: init };
})(typeof window !== 'undefined' ? window : this);
