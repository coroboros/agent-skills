/*
 * curtain-transition — reusable cover wipe (winners: Cuberto, Terminal
 * Industries, Truekind). An imperative transition tool, not an observer: one
 * fixed ground-colored panel that wipes IN from the bottom, swaps the world
 * behind it while fully covering, then wipes OUT upward — the beat that
 * rhymes with the counter loader. The panel is created by JS (no authored
 * markup, so no-JS renders nothing), always `aria-hidden` (decorative), inert
 * at rest (`pointer-events:none`), and blocks clicks only mid-wipe.
 *
 * Usage:  var curtain = awardCurtain.init(root, { zIndex, color })
 *   root    Element|Document  kept for the library contract; the panel itself
 *                             is body-level
 *   zIndex  number  panel stacking (default 9998 — under loader and gate)
 *   color   string  overrides the panel ground (default var(--ad-ground-2))
 * Returns { play(fn, opts2), destroy() } — the extended handle.
 *
 *   play(fn, { timeout })
 *     Wipes in; at full cover calls fn() — swap content, scroll, or navigate
 *     inside it. fn may return a promise: the cover holds until it settles,
 *     capped by `timeout` (default 2000ms) so a hung swap never strands the
 *     panel over the page. Then wipes out and resets. Returns a promise that
 *     resolves when the wipe-out completes. A play() during a play() is a
 *     no-op returning the in-flight promise. An fn that throws or rejects
 *     still wipes out; its error then surfaces through the returned promise.
 *
 * reduced-motion: play(fn) calls fn immediately, shows no panel, resolves.
 * Idempotent — one curtain per page; a second init returns the live handle
 * (destroy first to reconfigure). destroy() cancels any run (its promise
 * resolves), removes the panel and the stylesheet.
 *
 * Tokens: --ad-ground-2 (oklch(18% 0.01 260)) paints the panel; --ad-dur-base
 * (420ms) + --ad-ease-strike (cubic-bezier(.7,.02,.28,1)) time each wipe.
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-curtain-transition-css';
  var DEFAULT_TIMEOUT = 2000;
  var instance = null;

  var reduce = function () {
    return global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches;
  };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      '.ad-curtain{position:fixed;inset:0;pointer-events:none;' +
        'background:var(--ad-ground-2,oklch(18% 0.01 260));' +
        'transform:translateY(100%);will-change:transform;}';
    document.head.appendChild(s);
  }

  function styles() {
    var cs = getComputedStyle(document.documentElement);
    return {
      dur: (cs.getPropertyValue('--ad-dur-base') || '420ms').trim() || '420ms',
      ease: (cs.getPropertyValue('--ad-ease-strike') || '').trim() ||
        'cubic-bezier(.7,.02,.28,1)'
    };
  }

  function init(root, opts) {
    opts = opts || {};
    if (instance) return instance.handle;

    injectCss();
    var panel = document.createElement('div');
    panel.className = 'ad-curtain';
    panel.setAttribute('aria-hidden', 'true');
    panel.style.zIndex = String(opts.zIndex != null ? opts.zIndex : 9998);
    if (opts.color) panel.style.background = opts.color;
    document.body.appendChild(panel);

    var state = { playing: null, anim: null, timer: 0, abort: null, destroyed: false };

    // Animate from→to, then pin `restTo` as inline style and drop the fill —
    // an active fill:forwards would override any later inline reset. Jumping
    // -100% → 100% at wipe-out end is invisible: both are off-viewport.
    function wipe(from, to, restTo) {
      return new Promise(function (resolve) {
        if (state.destroyed || !panel.animate) {
          panel.style.transform = restTo;
          resolve();
          return;
        }
        var s = styles();
        var anim = panel.animate(
          [{ transform: from }, { transform: to }],
          { duration: parseFloat(s.dur), easing: s.ease, fill: 'forwards' }
        );
        state.anim = anim;
        var done = function () {
          if (state.anim === anim) state.anim = null;
          panel.style.transform = restTo;
          try { anim.cancel(); } catch (e) {}
          resolve();
        };
        anim.onfinish = done;
        anim.oncancel = done; // destroy() cancels mid-wipe → the run still settles
      });
    }

    // Run fn under the cover. Never rejects — {error} rides back so the
    // wipe-out always plays; play() re-throws after the reset.
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

    function play(fn, opts2) {
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

      panel.style.pointerEvents = 'auto';
      state.playing = wipe('translateY(100%)', 'translateY(0)', 'translateY(0)')
        .then(function () { return callFn(fn, timeout); })
        .then(function (r) {
          return wipe('translateY(0)', 'translateY(-100%)', 'translateY(100%)')
            .then(function () {
              if (!state.destroyed) panel.style.pointerEvents = '';
              state.playing = null;
              if (r.error) throw r.error;
            });
        });
      return state.playing;
    }

    var handle = {
      play: play,
      destroy: function () {
        state.destroyed = true;
        if (state.anim) { state.anim.cancel(); state.anim = null; }
        if (state.abort) state.abort();
        if (state.timer) { clearTimeout(state.timer); state.timer = 0; }
        if (panel.parentNode) panel.parentNode.removeChild(panel);
        instance = null;
        var st = document.getElementById(CSS_ID);
        if (st && st.parentNode) st.parentNode.removeChild(st);
      }
    };
    instance = { handle: handle };
    return handle;
  }

  global.awardCurtain = { init: init };
})(typeof window !== 'undefined' ? window : this);
