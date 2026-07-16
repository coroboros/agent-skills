/*
 * glitch-type — RGB channel-split display type (winners: Eloy Benoffi, Naked
 * City). Two aria-hidden ghost copies sit exactly over the heading — one
 * accent-colored and shifted left, one mixed toward ink and shifted right —
 * and clip-jitter through steps() keyframes. The glitch fires in BURSTS: a
 * 600ms burst every 5–9s (plus on hover for the hover variant), never
 * continuously — continuous glitch is noise, bursts are punctuation. Between
 * bursts the ghosts are opacity:0 and the heading is its plain self; ::before/
 * ::after can't carry dynamic text, so the ghosts are real JS-built clones —
 * no-JS renders a plain heading, prefers-reduced-motion builds no ghosts at all.
 *
 * Usage:  awardGlitchType.init(root, { selector })
 *   root      Element|Document  scope (default document)
 *   selector  string            headings to split (default '[data-ad-glitch]')
 * Per-element: data-ad-glitch="hover" also bursts on pointer enter.
 * Returns { destroy() }. Idempotent. Ghosts animate transform/clip-path/opacity
 * only; burst timers stop off-screen (IO-gated) and on hidden tabs.
 *
 * Tokens: --ad-accent, --ad-ink (ghost B = color-mix of the two).
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-glitch-type-css';
  var BURST_MS = 600;
  var GAP_MIN = 5000;
  var GAP_MAX = 9000;
  var reduce = function () {
    return global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches;
  };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      '.ad-glitch__base{position:relative;display:block;}' +
      '.ad-glitch__ghost{position:absolute;inset:0;opacity:0;mix-blend-mode:screen;' +
        'pointer-events:none;user-select:none;}' +
      '.is-glitching .ad-glitch__ghost{opacity:.55;}' +
      '.ad-glitch__ghost--a{color:var(--ad-accent,oklch(62% 0.2 25));}' +
      '.ad-glitch__ghost--b{color:color-mix(in oklch,' +
        'var(--ad-accent,oklch(62% 0.2 25)) 40%,var(--ad-ink,oklch(96% 0 0)));}' +
      // steps(1,end) holds each stop then jumps — discrete slices, no tween.
      '.is-glitching .ad-glitch__ghost--a{animation:ad-glitch-a .6s steps(1,end);}' +
      '.is-glitching .ad-glitch__ghost--b{animation:ad-glitch-b .6s steps(1,end);}' +
      '@keyframes ad-glitch-a{' +
        '0%{clip-path:inset(8% 0 78% 0);transform:translate3d(-2px,0,0);}' +
        '14%{clip-path:inset(62% 0 12% 0);transform:translate3d(-3px,0,0);}' +
        '28%{clip-path:inset(30% 0 52% 0);transform:translate3d(-1px,0,0);}' +
        '42%{clip-path:inset(84% 0 2% 0);transform:translate3d(-2px,0,0);}' +
        '57%{clip-path:inset(4% 0 86% 0);transform:translate3d(-3px,0,0);}' +
        '71%{clip-path:inset(48% 0 34% 0);transform:translate3d(-2px,0,0);}' +
        '85%{clip-path:inset(70% 0 16% 0);transform:translate3d(-1px,0,0);}' +
        '100%{clip-path:inset(22% 0 64% 0);transform:translate3d(-2px,0,0);}}' +
      '@keyframes ad-glitch-b{' +
        '0%{clip-path:inset(72% 0 14% 0);transform:translate3d(2px,0,0);}' +
        '14%{clip-path:inset(18% 0 70% 0);transform:translate3d(3px,0,0);}' +
        '28%{clip-path:inset(56% 0 28% 0);transform:translate3d(1px,0,0);}' +
        '42%{clip-path:inset(6% 0 82% 0);transform:translate3d(2px,0,0);}' +
        '57%{clip-path:inset(40% 0 44% 0);transform:translate3d(3px,0,0);}' +
        '71%{clip-path:inset(88% 0 4% 0);transform:translate3d(1px,0,0);}' +
        '85%{clip-path:inset(26% 0 58% 0);transform:translate3d(2px,0,0);}' +
        '100%{clip-path:inset(60% 0 24% 0);transform:translate3d(2px,0,0);}}';
    document.head.appendChild(s);
  }

  function build(el) {
    // Preserve the original markup so re-init and destroy rebuild from truth.
    if (el.__adGlitchHTML == null) el.__adGlitchHTML = el.innerHTML;
    else el.innerHTML = el.__adGlitchHTML;
    var base = document.createElement('span');
    base.className = 'ad-glitch__base';
    while (el.firstChild) base.appendChild(el.firstChild);
    // Snapshot before the ghosts land in base, or they'd clone themselves.
    var html = base.innerHTML;
    ['a', 'b'].forEach(function (k) {
      var g = document.createElement('span');
      g.className = 'ad-glitch__ghost ad-glitch__ghost--' + k;
      // The clones would triple screen-reader output — visual layers only.
      g.setAttribute('aria-hidden', 'true');
      g.innerHTML = html;
      base.appendChild(g);
    });
    el.appendChild(base);
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-glitch]';

    // reduce → no ghosts at all; the plain heading IS the finished state.
    if (reduce()) return { destroy: function () {} };

    injectCss();

    var recs = Array.prototype.slice.call(root.querySelectorAll(selector))
      .map(function (el) {
        build(el);
        return { el: el, gapTimer: 0, burstTimer: 0, visible: false, onEnter: null };
      });
    var io = null;

    function burst(rec) {
      if (rec.burstTimer) return; // a burst in flight ignores new triggers
      rec.el.classList.add('is-glitching');
      rec.burstTimer = setTimeout(function () {
        rec.burstTimer = 0;
        rec.el.classList.remove('is-glitching');
      }, BURST_MS);
    }

    function schedule(rec) {
      clearTimeout(rec.gapTimer);
      rec.gapTimer = setTimeout(function () {
        rec.gapTimer = 0;
        burst(rec);
        schedule(rec);
      }, GAP_MIN + Math.random() * (GAP_MAX - GAP_MIN));
    }

    function halt(rec) {
      if (rec.gapTimer) { clearTimeout(rec.gapTimer); rec.gapTimer = 0; }
      if (rec.burstTimer) { clearTimeout(rec.burstTimer); rec.burstTimer = 0; }
      rec.el.classList.remove('is-glitching');
    }

    if ('IntersectionObserver' in global) {
      io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          for (var i = 0; i < recs.length; i++) {
            if (recs[i].el !== e.target) continue;
            recs[i].visible = e.isIntersecting;
            if (e.isIntersecting) { if (!document.hidden) schedule(recs[i]); }
            else halt(recs[i]);
            return;
          }
        });
      }, { threshold: 0.2 });
      recs.forEach(function (rec) { io.observe(rec.el); });
    } else {
      recs.forEach(function (rec) { rec.visible = true; schedule(rec); });
    }

    recs.forEach(function (rec) {
      if (rec.el.getAttribute('data-ad-glitch') !== 'hover') return;
      rec.onEnter = function () { burst(rec); };
      rec.el.addEventListener('mouseenter', rec.onEnter);
    });

    function onVisibility() {
      if (document.hidden) recs.forEach(halt);
      else recs.forEach(function (rec) { if (rec.visible) schedule(rec); });
    }
    document.addEventListener('visibilitychange', onVisibility);

    return {
      destroy: function () {
        if (io) io.disconnect();
        document.removeEventListener('visibilitychange', onVisibility);
        recs.forEach(function (rec) {
          halt(rec);
          if (rec.onEnter) rec.el.removeEventListener('mouseenter', rec.onEnter);
          if (rec.el.__adGlitchHTML != null) {
            rec.el.innerHTML = rec.el.__adGlitchHTML;
            delete rec.el.__adGlitchHTML;
          }
        });
        var s = document.getElementById(CSS_ID);
        if (s) s.parentNode.removeChild(s);
      }
    };
  }

  global.awardGlitchType = { init: init };
})(typeof window !== 'undefined' ? window : this);
