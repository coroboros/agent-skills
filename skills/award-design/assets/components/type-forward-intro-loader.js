/*
 * type-forward-intro-loader — the gallery-stack's verified loader/intro
 * (winner: Gabriel Contassot). A numeric 1→100 preloader (Gabriel: 2.8s,
 * values [1..100], "more stylistic than functional") fades out (~.8s, slow-in)
 * and hands off to a scramble-decode type assembly over the MAIN GALLERY —
 * charset noise resolving to the true strings, per-element durations cycling
 * Gabriel's verified ScrambleText list [1.2,1.5,.4,.2,1,.6,.6]s with an
 * expo-out lock progression. Distinct from counter-loader: that roll is
 * honest (eases to 90, holds for the real window load, curtain-wipes); this
 * one is the STYLISTIC beat — a fixed-duration linear 1→100 count and an
 * opacity fade, decoupled from asset load by winner design. The refuted
 * "imageless withholding hero" framing is NOT encoded here — the intro plays
 * over whatever the recipe put under it (Codrops verifies a main image
 * gallery on Gabriel's homepage).
 *
 * Expected markup — authored `hidden`; JS un-hides and runs it (the
 * gated-splash law: no-JS or a dead script never blocks the page):
 *   <div data-ad-intro hidden><span data-ad-intro-count>1</span></div>
 * Intro targets (short strings only — a name, a role line, index labels)
 * carry data-ad-intro-decode; their markup text is the resting truth.
 *
 * Usage:  awardTypeIntroLoader.init(root, { selector, decodeSelector,
 *                                           duration, charset, sessionOnce, onDone })
 *   selector        string   the overlay (default '[data-ad-intro]')
 *   decodeSelector  string   handoff targets (default '[data-ad-intro-decode]')
 *   duration        ms       the 1→100 count (default 2800 — Gabriel's 2.8s)
 *   charset         string   churn glyphs (default '*&@#%$-_:/;01')
 *   sessionOnce     boolean  skip after the first completed run this session
 *   onDone          function fires once after the fade lands (and immediately
 *                            on every skip path), so the first beat never
 *                            depends on the roll having played
 * Returns { destroy() }. Idempotent — while running it returns the live
 * handle; once done (or skipped) a re-init is a no-op. reduced-motion skips
 * everything: no count, no fade, no scramble — the page and its plain text
 * are the finished state, and onDone fires.
 *
 * Tokens: --ad-ground + --ad-ink paint the overlay; --ad-font-mono +
 * --ad-space set the count corner; --ad-dur-reveal (800ms) times the fade
 * (the ~.8s slow-in is the ease default).
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-type-intro-css';
  var SEEN_KEY = 'ad-type-intro-done';
  var FADE_EASE = 'cubic-bezier(.55,.06,.68,.19)'; // slow-in approximation
  var DECODE_DURS = [1200, 1500, 400, 200, 1000, 600, 600]; // Gabriel-verified
  var TICK = 80;

  var reduce = function () {
    return global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches;
  };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    // Scoped under .ad-intro — the class JS adds after removing `hidden`.
    // No-JS never gets the class, so the UA `[hidden]` display:none stands.
    s.textContent =
      '.ad-intro{position:fixed;inset:0;z-index:100000;display:flex;' +
        'align-items:flex-end;justify-content:flex-start;' +
        'padding:calc(var(--ad-space,clamp(1.25rem,2.5vw,2rem))*1.5);' +
        'background:var(--ad-ground,oklch(14% 0.01 260));' +
        'color:var(--ad-ink,oklch(96% 0 0));will-change:opacity;}' +
      '.ad-intro[data-ad-done]{display:none;}' +
      '.ad-intro [data-ad-intro-count]{' +
        'font-family:var(--ad-font-mono,ui-monospace,monospace);' +
        'font-size:clamp(2rem,7vw,5rem);line-height:1;' +
        'font-variant-numeric:tabular-nums;}';
    document.head.appendChild(s);
  }

  // sessionStorage throws in some privacy modes — a loader must never.
  function seen() {
    try { return global.sessionStorage.getItem(SEEN_KEY) === '1'; }
    catch (e) { return false; }
  }
  function markSeen() {
    try { global.sessionStorage.setItem(SEEN_KEY, '1'); } catch (e) {}
  }

  function easeOutExpo(p) { return p >= 1 ? 1 : 1 - Math.pow(2, -10 * p); }
  function glyph(charset) {
    return charset.charAt(Math.floor(Math.random() * charset.length));
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-intro]';
    var decodeSelector = opts.decodeSelector || '[data-ad-intro-decode]';
    var duration = opts.duration != null ? opts.duration : 2800;
    var charset = opts.charset || '*&@#%$-_:/;01';
    var sessionOnce = !!opts.sessionOnce;
    var onDone = typeof opts.onDone === 'function' ? opts.onDone : null;

    var loader = root.querySelector(selector);
    if (!loader) return { destroy: function () {} };

    // Idempotent: done → no-op; still running → the live handle (no rebind).
    var prev = loader.__adTypeIntro;
    if (prev) return prev.done ? { destroy: function () {} } : prev.handle;

    // Skip paths — the overlay keeps its authored `hidden`, the page just
    // shows with its plain resting text (the finished state).
    if (reduce() || (sessionOnce && seen())) {
      var skipState = { done: true, handle: null };
      loader.__adTypeIntro = skipState; // a re-init must not re-fire onDone
      skipState.handle = { destroy: function () { delete loader.__adTypeIntro; } };
      if (onDone) onDone();
      return skipState.handle;
    }

    injectCss();
    var countEl = loader.querySelector('[data-ad-intro-count]');
    var countText0 = countEl ? countEl.textContent : '';
    var hadHidden = loader.hasAttribute('hidden');
    var prevOverflow = document.body.style.overflow;
    var state = { done: false, raf: 0, anim: null, handle: null, decodes: [] };
    loader.__adTypeIntro = state;

    // Open: un-hide, promote to the JS-only class, announce busy, lock scroll.
    loader.removeAttribute('hidden');
    loader.classList.add('ad-intro');
    loader.setAttribute('aria-busy', 'true');
    document.body.style.overflow = 'hidden';

    var lastShown = -1;
    function setCount(v) {
      var n = Math.round(v);
      if (n === lastShown) return; // write only on change
      lastShown = n;
      if (countEl) countEl.textContent = String(n);
    }

    // ---- the handoff: scramble-decode over the revealed gallery ------------
    function finishDecode(rec) {
      rec.el.textContent = rec.original;
      rec.el.removeAttribute('aria-label');
      var i = state.decodes.indexOf(rec);
      if (i !== -1) state.decodes.splice(i, 1);
    }

    function decodeFrame(now) {
      state.raf = 0;
      for (var i = state.decodes.length - 1; i >= 0; i--) {
        var rec = state.decodes[i];
        var t = now - rec.start;
        if (t >= rec.dur) { finishDecode(rec); continue; }
        // expo-out lock: fast early locks, a slow settle (Gabriel's register)
        var locked = Math.floor(easeOutExpo(t / rec.dur) * rec.chars.length);
        var shuffle = now - rec.last >= TICK;
        if (!shuffle && locked === rec.locked) continue;
        if (shuffle) rec.last = now;
        rec.locked = locked;
        var out = '';
        for (var j = 0; j < rec.chars.length; j++) {
          var ch = rec.chars[j];
          if (j < locked || /\s/.test(ch)) { out += ch; continue; }
          if (shuffle || rec.frame[j] == null) rec.frame[j] = glyph(charset);
          out += rec.frame[j];
        }
        rec.el.textContent = out;
      }
      if (state.decodes.length) state.raf = global.requestAnimationFrame(decodeFrame);
    }

    function startDecodes() {
      var els = Array.prototype.slice.call(root.querySelectorAll(decodeSelector));
      els.forEach(function (el, i) {
        var original = el.textContent;
        if (!original) return;
        // Churn glyphs are visual noise — pin the accessible name to the truth.
        el.setAttribute('aria-label', original);
        var rec = {
          el: el, original: original, chars: original.split(''),
          dur: DECODE_DURS[i % DECODE_DURS.length],
          start: performance.now(), last: performance.now(),
          locked: 0, frame: []
        };
        var out = '';
        for (var j = 0; j < rec.chars.length; j++) {
          out += /\s/.test(rec.chars[j]) ? rec.chars[j] : (rec.frame[j] = glyph(charset));
        }
        el.textContent = out;
        state.decodes.push(rec);
      });
      if (state.decodes.length) state.raf = global.requestAnimationFrame(decodeFrame);
    }

    // Hidden tabs freeze rAF; churn left on screen would read as garbage on
    // return — resolve every in-flight decode to the truth instead.
    function onVisibility() {
      if (!document.hidden) return;
      for (var i = state.decodes.length - 1; i >= 0; i--) finishDecode(state.decodes[i]);
      if (state.raf) { global.cancelAnimationFrame(state.raf); state.raf = 0; }
    }
    document.addEventListener('visibilitychange', onVisibility);

    // ---- the count and the fade -------------------------------------------
    function finalize() {
      state.anim = null;
      document.body.style.overflow = prevOverflow;
      loader.removeAttribute('aria-busy');
      loader.setAttribute('aria-hidden', 'true');
      loader.setAttribute('data-ad-done', ''); // → display:none
      markSeen();
      state.done = true;
      if (onDone) onDone();      // the hero starts as the decode plays over it
      startDecodes();
    }

    function fadeOut() {
      var cs = getComputedStyle(document.documentElement);
      var dur = parseFloat((cs.getPropertyValue('--ad-dur-reveal') || '').trim()) || 800;
      if (!loader.animate) { finalize(); return; }
      state.anim = loader.animate(
        [{ opacity: 1 }, { opacity: 0 }],
        { duration: dur, easing: FADE_EASE, fill: 'forwards' }
      );
      state.anim.onfinish = finalize;
    }

    // The roll: linear 1→100 over `duration` — stylistic by winner design,
    // never gated on the real asset load. Clock-based, so a frozen background
    // tab lands on the right value when the user returns.
    var start = 0;
    function tick(now) {
      if (!start) start = now;
      var p = Math.min(1, (now - start) / duration);
      setCount(1 + p * 99);
      if (p >= 1) { state.raf = 0; fadeOut(); return; }
      state.raf = global.requestAnimationFrame(tick);
    }
    state.raf = global.requestAnimationFrame(tick);

    var handle = {
      destroy: function () {
        if (state.raf) { global.cancelAnimationFrame(state.raf); state.raf = 0; }
        if (state.anim) { state.anim.cancel(); state.anim = null; }
        for (var i = state.decodes.length - 1; i >= 0; i--) finishDecode(state.decodes[i]);
        document.removeEventListener('visibilitychange', onVisibility);
        document.body.style.overflow = prevOverflow;
        loader.classList.remove('ad-intro');
        loader.removeAttribute('aria-busy');
        loader.removeAttribute('aria-hidden');
        loader.removeAttribute('data-ad-done');
        loader.style.opacity = '';
        if (countEl) countEl.textContent = countText0;
        if (hadHidden) loader.setAttribute('hidden', '');
        else loader.removeAttribute('hidden');
        delete loader.__adTypeIntro;
        var st = document.getElementById(CSS_ID);
        if (st && st.parentNode) st.parentNode.removeChild(st);
      }
    };
    state.handle = handle;
    return handle;
  }

  global.awardTypeIntroLoader = { init: init };
})(typeof window !== 'undefined' ? window : this);
