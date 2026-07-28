/*
 * continuous-work-transition — the curtain-LESS work-to-work morph (winner:
 * Bisous). A route/section transition that leads 'seamlessly into the next
 * work': the outgoing figure FLOWS into the incoming one — a shared-element
 * geometry morph under a cross-dissolve, 'fluid and almost imperceptible',
 * with NO cover phase — the opposite of curtain-transition's ground-colored
 * wipe, and distinct from route-view-transition-carrier's whole-view
 * crossfade (whose fallback dips the view through blank): here one work
 * figure stays continuously on stage while the rest dissolves around it.
 * Built on native View Transitions: the component names the paired figures
 * (outgoing before the swap, incoming inside it) so the browser morphs them,
 * and retunes old/new/group to the slow signature register. The imposed
 * fallback ladder is short by verdict: reduced motion OR no
 * startViewTransition → an INSTANT CUT — never a fade-to-ground, never a
 * hand-rolled morph.
 *
 * An imperative tool like curtain-transition, not an observer: the builder
 * calls go(fn) and swaps DOM, scrolls, or rewrites the view inside fn. The
 * figures are found by selector — the outgoing one queried before fn runs,
 * the incoming one after — so the same call serves SPA route swaps and
 * in-page section swaps alike. No authored markup beyond the figure hook;
 * nothing renders at rest.
 *
 * Usage:  var cwt = awardContinuousWorkTransition.init(root, { selector })
 *   root      Element|Document  scope the figures are queried in (default document)
 *   selector  string  the work figure hook (default '[data-ad-work-figure]';
 *                     with several matches the first visible pair morphs)
 * Returns { go(fn, opts2), destroy() } — the extended handle.
 *
 *   go(fn, { timeout })
 *     Names the outgoing figure, starts the transition, runs fn inside it,
 *     names the incoming figure the swap produced. fn may return a promise;
 *     the swap is capped by `timeout` (default 2000ms) so a hung fetch never
 *     strands the transition. Returns a promise resolving when the morph
 *     completes. A go() during a go() is a no-op returning the in-flight
 *     promise. An fn that throws or rejects still completes the transition;
 *     its error surfaces through the returned promise.
 *
 * Idempotent — one instance per page; a second init returns the live handle.
 * destroy() skips any run (its promise resolves), clears the figure names,
 * and removes the stylesheet.
 *
 * Tokens: --ad-cwt-dur (900ms — the 'almost imperceptible' tempo) +
 * --ad-cwt-ease (falls back to --ad-ease-signature, then
 * cubic-bezier(.16,1,.3,1)).
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-continuous-work-transition-css';
  var NAME = 'ad-work';
  var DEFAULT_TIMEOUT = 2000;
  var DUR = 'var(--ad-cwt-dur,900ms)';
  var EASE = 'var(--ad-cwt-ease,var(--ad-ease-signature,cubic-bezier(.16,1,.3,1)))';
  var instance = null;

  var reduce = function () {
    return global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches;
  };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      // the figure pair: geometry morph + cross-dissolve at the signature tempo;
      // snapshots fill the morphing group so mid-flight frames never letterbox
      '::view-transition-group(' + NAME + '){' +
      'animation-duration:' + DUR + ';animation-timing-function:' + EASE + ';}' +
      '::view-transition-old(' + NAME + '),::view-transition-new(' + NAME + '){' +
      'animation-duration:' + DUR + ';animation-timing-function:' + EASE + ';' +
      'height:100%;width:100%;object-fit:cover;}' +
      // the rest of the page cross-dissolves on the same clock — no cover phase
      '::view-transition-old(root),::view-transition-new(root){' +
      'animation-duration:' + DUR + ';animation-timing-function:' + EASE + ';}';
    document.head.appendChild(s);
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    if (instance) return instance.handle;
    injectCss();

    var selector = opts.selector || '[data-ad-work-figure]';
    var state = { playing: null, timer: 0, abort: null, vt: null, named: [], destroyed: false };

    function figure() {
      var els = (root.querySelectorAll ? root : document).querySelectorAll(selector);
      for (var i = 0; i < els.length; i++) {
        var r = els[i].getBoundingClientRect();
        if (r.width > 0 && r.height > 0) return els[i]; // the first visible one morphs
      }
      return null;
    }
    function name(el) {
      if (!el) return;
      el.style.viewTransitionName = NAME;
      state.named.push(el);
    }
    function unname() {
      state.named.forEach(function (el) { el.style.viewTransitionName = ''; });
      state.named = [];
    }

    // Run fn with a settle cap. Never rejects — {error} rides back so the
    // transition always completes; go() re-throws after the names are cleared.
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

    function go(fn, opts2) {
      if (state.destroyed) return Promise.resolve();
      if (state.playing) return state.playing;
      var timeout = opts2 && opts2.timeout != null ? opts2.timeout : DEFAULT_TIMEOUT;

      // The imposed ladder: reduce OR no View Transitions → instant cut.
      if (reduce() || typeof document.startViewTransition !== 'function') {
        state.playing = callFn(fn, timeout).then(function (r) {
          state.playing = null;
          if (r.error) throw r.error;
        });
        return state.playing;
      }

      name(figure()); // the outgoing figure, before the browser snapshots
      var result = null;
      var vt = document.startViewTransition(function () {
        return callFn(fn, timeout).then(function (r) {
          result = r;
          name(figure()); // the incoming figure the swap produced
        });
      });
      state.vt = vt;
      state.playing = vt.finished
        .catch(function () {}) // a skipped transition is not a swap failure
        .then(function () {
          state.vt = null;
          unname();
          state.playing = null;
          if (result && result.error) throw result.error;
        });
      return state.playing;
    }

    var handle = {
      go: go,
      destroy: function () {
        state.destroyed = true;
        if (state.vt) { try { state.vt.skipTransition(); } catch (e) {} state.vt = null; }
        if (state.abort) state.abort();
        if (state.timer) { clearTimeout(state.timer); state.timer = 0; }
        unname();
        instance = null;
        var st = document.getElementById(CSS_ID);
        if (st && st.parentNode) st.parentNode.removeChild(st);
      }
    };
    instance = { handle: handle };
    return handle;
  }

  global.awardContinuousWorkTransition = { init: init };
})(typeof window !== 'undefined' ? window : this);
