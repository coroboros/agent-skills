/*
 * ambient-idle — perpetual-micro idle breathing (winner: Terminal Industries'
 * radial glow; the premium-patterns perpetual-micro canon). The third motion
 * channel: the page breathes at rest, between inputs. Elements opt in via
 * data-ad-idle="<mode>":
 *   glow     a slow radial glow breathes behind the element (::before, ~9s)
 *   float    the element drifts vertically ±5px (~7s)
 *   shimmer  a soft highlight sweeps across text/a card (~2s sweep, ~6s rest)
 *   pulse    opacity 1↔.75 (~5s) — labels, live-dots
 * Amplitudes are ambient by contract — idle breathing, never an attention
 * grab. Pure decoration: overlays are pointer-events:none, nothing is
 * announced, host semantics untouched.
 *
 * Usage:  awardAmbientIdle.init(root, { selector })
 *   root      Element|Document  scope (default document)
 *   selector  string            opted-in elements (default '[data-ad-idle]')
 * Returns { destroy() }. Idempotent — re-init on the same root replaces the
 * prior instance.
 *
 * Tokens: --ad-accent (glow), --ad-ink (shimmer highlight).
 *
 * PERF: transform/opacity only — the glow gradient rasterizes once and is
 * scale/opacity-animated; the shimmer is a translated overlay, never a moving
 * background-position. Every animation is authored paused; ONE
 * IntersectionObserver flips `is-idling` (running) per element so off-screen
 * elements cost zero, and a visibilitychange root class re-pauses everything
 * in a hidden tab. will-change applies only while an element is actually
 * idling. reduced-motion (CSS @media, the live source of truth) disables all
 * idle animation — static rest state.
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-ambient-idle-css';
  var HIDDEN_CLASS = 'ad-idle-page-hidden';

  var reduce = function () {
    return global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches;
  };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      // glow — a breathing radial halo behind the element (z-index:-1).
      '.ad-idle[data-ad-idle=glow]{position:relative;}' +
      '.ad-idle[data-ad-idle=glow]::before{content:"";position:absolute;inset:-30%;z-index:-1;' +
        'pointer-events:none;opacity:.6;' +
        'background:radial-gradient(closest-side,' +
          'color-mix(in oklch,var(--ad-accent,oklch(62% 0.2 25)) 14%,transparent),transparent);' +
        'animation:ad-idle-glow 9s ease-in-out infinite alternate paused;}' +
      // float — negative half-period delay so the paused pose is the neutral 0px.
      '.ad-idle[data-ad-idle=float]{' +
        'animation:ad-idle-float 7s ease-in-out -3.5s infinite alternate paused;}' +
      // shimmer — overlay parked off-canvas at rest; the host clips the sweep.
      '.ad-idle[data-ad-idle=shimmer]{position:relative;overflow:hidden;}' +
      '.ad-idle[data-ad-idle=shimmer]::after{content:"";position:absolute;inset:0;' +
        'pointer-events:none;transform:translateX(-120%);' +
        'background:linear-gradient(105deg,transparent 40%,' +
          'color-mix(in oklch,var(--ad-ink,oklch(96% 0 0)) 18%,transparent) 50%,transparent 60%);' +
        'animation:ad-idle-shimmer 8s ease-in-out infinite paused;}' +
      '.ad-idle[data-ad-idle=pulse]{' +
        'animation:ad-idle-pulse 5s ease-in-out infinite alternate paused;}' +
      '.ad-idle.is-idling,.ad-idle.is-idling::before,.ad-idle.is-idling::after{' +
        'animation-play-state:running;}' +
      '.ad-idle.is-idling[data-ad-idle=float]{will-change:transform;}' +
      '.ad-idle.is-idling[data-ad-idle=pulse]{will-change:opacity;}' +
      '.ad-idle.is-idling[data-ad-idle=glow]::before{will-change:transform,opacity;}' +
      '.ad-idle.is-idling[data-ad-idle=shimmer]::after{will-change:transform;}' +
      // html.<hidden> outranks .is-idling (0,2,1 vs 0,2,0) — no !important needed.
      'html.' + HIDDEN_CLASS + ' .ad-idle,' +
      'html.' + HIDDEN_CLASS + ' .ad-idle::before,' +
      'html.' + HIDDEN_CLASS + ' .ad-idle::after{animation-play-state:paused;}' +
      '@keyframes ad-idle-glow{' +
        'from{transform:scale(1);opacity:.6;}to{transform:scale(1.12);opacity:1;}}' +
      '@keyframes ad-idle-float{' +
        'from{transform:translateY(-5px);}to{transform:translateY(5px);}}' +
      // 2s sweep, then rest: 25%→100% holds the off-canvas end value.
      '@keyframes ad-idle-shimmer{' +
        '0%{transform:translateX(-120%);}25%{transform:translateX(120%);}' +
        '100%{transform:translateX(120%);}}' +
      // 1→.75 (not .75→1): same cycle, but the paused pose is full opacity.
      '@keyframes ad-idle-pulse{from{opacity:1;}to{opacity:.75;}}' +
      '@media (prefers-reduced-motion: reduce){' +
        '.ad-idle,.ad-idle::before,.ad-idle::after{animation:none;will-change:auto;}}';
    document.head.appendChild(s);
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-idle]';
    injectCss();

    // Idempotent: a re-init on the same root replaces the prior instance.
    if (root.__adAmbientIdle) root.__adAmbientIdle.destroy();

    var els = Array.prototype.slice.call(root.querySelectorAll(selector));
    els.forEach(function (el) { el.classList.add('ad-idle'); });

    var io = null;
    var onVisibility = null;

    if (!reduce()) {
      if ('IntersectionObserver' in global) {
        io = new IntersectionObserver(function (entries) {
          entries.forEach(function (e) {
            e.target.classList.toggle('is-idling', e.isIntersecting);
          });
        });
        els.forEach(function (el) { io.observe(el); });
      } else {
        els.forEach(function (el) { el.classList.add('is-idling'); });
      }
      onVisibility = function () {
        document.documentElement.classList.toggle(HIDDEN_CLASS, document.hidden);
      };
      document.addEventListener('visibilitychange', onVisibility);
      onVisibility(); // adopt the current state — init may run in a hidden tab
    }

    var handle = {
      destroy: function () {
        if (io) io.disconnect();
        if (onVisibility) document.removeEventListener('visibilitychange', onVisibility);
        els.forEach(function (el) {
          el.classList.remove('ad-idle');
          el.classList.remove('is-idling');
        });
        document.documentElement.classList.remove(HIDDEN_CLASS);
        var s = document.getElementById(CSS_ID);
        if (s && s.parentNode) s.parentNode.removeChild(s);
        if (root.__adAmbientIdle === handle) delete root.__adAmbientIdle;
      }
    };
    root.__adAmbientIdle = handle;
    return handle;
  }

  global.awardAmbientIdle = { init: init };
})(typeof window !== 'undefined' ? window : this);
