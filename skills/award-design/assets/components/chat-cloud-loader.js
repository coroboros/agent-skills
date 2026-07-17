/*
 * chat-cloud-loader — the in-character typed loader for the argument spine
 * (winner: FlowFest 2025 — boundary-adjacent; the beat/param details live in
 * the winner's Slater/GSAP JS and were not re-read, so the exact values here
 * are illustrative — the PATTERN is the verified part). A mascot's chat cloud
 * types successive beats at a constant per-char cadence (the winner runs GSAP
 * TextPlugin all ease:none — typing never eases, the flat cadence IS the
 * character), an optional mono counter steps 0→100 across the same timeline,
 * then the overlay fades out (the winner's autoAlpha:0 over 0.3s) and the
 * handoff plays: the nav drops in (yPercent −102→0) and the welcome cards
 * stagger up. The loader SIGNS its character rather than showing a bare
 * count. Authored `hidden` and un-hidden by JS, so no-JS or a dead script
 * never blocks the page (the gated-splash law). The typing stays honest: the
 * last beat holds until the real window `load` before the exit fires.
 *
 * Expected markup — authored `hidden`; the mascot is the builder's mark, the
 * component never invents it; the counter span is optional:
 *   <div data-ad-chat-loader hidden>
 *     <div data-ad-chat-mascot><!-- builder's mascot / mark --></div>
 *     <p data-ad-chat-cloud></p>
 *     <span data-ad-chat-count>0</span>
 *   </div>
 *
 * Usage:  awardChatCloudLoader.init(root, opts)
 *   root         Element|Document  scope (default document)
 *   selector     string    the overlay (default '[data-ad-chat-loader]')
 *   beats        string[]  the typed beats (default ['...', 'Hi Friends!',
 *                          'We are back...'] — illustrative FlowFest beats;
 *                          give the build's own in-character lines)
 *   heroLine     string    the hero's resident line, appended as the final
 *                          beat so the cloud hands its last words to the hero
 *   charMs       ms        per-char cadence, constant (default 45)
 *   holdMs       ms        hold on each completed beat (default 350)
 *   nav          string    selector for the nav that drops −102%→0 after the
 *                          fade (default '[data-ad-chat-nav]'; absent → skipped)
 *   stagger      string    selector for the welcome cards that stagger up
 *                          (default '[data-ad-chat-stagger]'; absent → skipped)
 *   sessionOnce  boolean   skip after the first completed run this session
 *   onDone       function  runs once after the handoff. Also fires immediately
 *                          on the skip paths (reduced-motion, sessionOnce), so
 *                          the first beat never depends on the roll.
 * Returns { destroy() }. Idempotent — while typing it returns the live handle;
 * once done (or skipped) a re-init is a no-op. destroy() cancels everything,
 * restores `hidden` + body scroll + the authored cloud/count text, and removes
 * the stylesheet. Nav and cards are authored in their FINAL state — the
 * component only animates them FROM offset when it actually runs, so the skip
 * paths and no-JS never leave them displaced.
 *
 * Tokens: --ad-ground + --ad-ink paint the overlay; --ad-ground-2 the cloud
 * bubble; --ad-font-display sets the cloud, --ad-font-mono the counter;
 * --ad-accent recolors the counter at 100; --ad-dur-reveal +
 * --ad-ease-signature time the nav drop and card stagger; --ad-dur-base the
 * counter recolor.
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-chat-cloud-loader-css';
  var SEEN_KEY = 'ad-chat-cloud-loader-done';
  var FADE_MS = 300; // the winner's autoAlpha:0 0.3s exit (illustrative)

  var reduce = function () {
    return global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches;
  };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    // Scoped under .ad-chat — the class JS adds after removing `hidden`.
    // No-JS never gets the class, so the UA `[hidden]` display:none stands.
    s.textContent =
      '.ad-chat{position:fixed;inset:0;z-index:100000;display:flex;' +
        'flex-direction:column;align-items:center;justify-content:center;' +
        'gap:1.25rem;background:var(--ad-ground,oklch(14% 0.01 260));' +
        'color:var(--ad-ink,oklch(96% 0 0));}' +
      '.ad-chat[data-ad-done]{display:none;}' +
      '.ad-chat [data-ad-chat-cloud]{position:relative;margin:0;' +
        'padding:.9em 1.3em;border-radius:1.4em;' +
        'background:var(--ad-ground-2,oklch(18% 0.01 260));' +
        'font-family:var(--ad-font-display,inherit);' +
        'font-size:clamp(1.1rem,3vw,1.8rem);line-height:1.3;' +
        'min-height:1.3em;min-width:3ch;text-align:center;}' +
      // the cloud's tail — chrome the bubble needs to read as speech, not décor
      '.ad-chat [data-ad-chat-cloud]::after{content:"";position:absolute;' +
        'left:1.6em;top:100%;border:.55em solid transparent;' +
        'border-top-color:var(--ad-ground-2,oklch(18% 0.01 260));}' +
      '.ad-chat [data-ad-chat-count]{' +
        'font-family:var(--ad-font-mono,ui-monospace,monospace);' +
        'font-size:.8rem;letter-spacing:.12em;' +
        'font-variant-numeric:tabular-nums;opacity:.7;' +
        'transition:color var(--ad-dur-base,420ms) ' +
        'var(--ad-ease-signature,cubic-bezier(.16,1,.3,1));}' +
      '.ad-chat[data-ad-near] [data-ad-chat-count]{' +
        'color:var(--ad-accent,oklch(62% 0.2 25));opacity:1;}';
    document.head.appendChild(s);
  }

  function styles() {
    var cs = getComputedStyle(document.documentElement);
    function v(name, fallback) {
      return (cs.getPropertyValue(name) || '').trim() || fallback;
    }
    return {
      durReveal: parseFloat(v('--ad-dur-reveal', '800ms')) || 800,
      ease: v('--ad-ease-signature', 'cubic-bezier(.16,1,.3,1)')
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

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-chat-loader]';
    var beats = (opts.beats || ['...', 'Hi Friends!', 'We are back...']).slice();
    if (opts.heroLine) beats.push(opts.heroLine);
    var charMs = opts.charMs != null ? opts.charMs : 45;
    var holdMs = opts.holdMs != null ? opts.holdMs : 350;
    var navSel = opts.nav || '[data-ad-chat-nav]';
    var staggerSel = opts.stagger || '[data-ad-chat-stagger]';
    var sessionOnce = !!opts.sessionOnce;
    var onDone = typeof opts.onDone === 'function' ? opts.onDone : null;

    var loader = root.querySelector(selector);
    if (!loader) return { destroy: function () {} };

    // Idempotent: done → no-op; still typing → the live handle (no rebind).
    var prev = loader.__adChatLoader;
    if (prev) return prev.done ? { destroy: function () {} } : prev.handle;

    // Skip paths — the overlay keeps its authored `hidden`; nav and cards are
    // authored in place, so the page is simply its finished self.
    if (reduce() || (sessionOnce && seen())) {
      var skipState = { done: true, handle: null };
      loader.__adChatLoader = skipState; // a re-init must not re-fire onDone
      skipState.handle = { destroy: function () { delete loader.__adChatLoader; } };
      if (onDone) onDone();
      return skipState.handle;
    }

    injectCss();
    var cloud = loader.querySelector('[data-ad-chat-cloud]');
    var countEl = loader.querySelector('[data-ad-chat-count]');
    var cloudText0 = cloud ? cloud.textContent : '';
    var countText0 = countEl ? countEl.textContent : '';
    var hadHidden = loader.hasAttribute('hidden');
    var prevOverflow = document.body.style.overflow;
    var state = { done: false, raf: 0, anims: [], timer: 0, handle: null };
    loader.__adChatLoader = state;

    var loaded = document.readyState === 'complete';
    function onLoad() { loaded = true; }
    if (!loaded) global.addEventListener('load', onLoad);

    // Open: un-hide, promote to the JS-only class, announce busy, lock scroll.
    loader.removeAttribute('hidden');
    loader.classList.add('ad-chat');
    loader.setAttribute('aria-busy', 'true');
    document.body.style.overflow = 'hidden';

    // The timeline is one flat clock: per beat, chars land every charMs (the
    // ease:none tell — a typing curve would break character), then holdMs.
    var beatDurs = beats.map(function (b) { return b.length * charMs + holdMs; });
    var total = beatDurs.reduce(function (a, b) { return a + b; }, 0);

    var lastShownCount = -1;
    function setCount(v) {
      if (!countEl) return;
      var n = Math.round(v);
      if (n === lastShownCount) return; // write only on change — no per-frame paint
      lastShownCount = n;
      countEl.textContent = String(n);
      if (n >= 100) loader.setAttribute('data-ad-near', '');
    }

    var lastTyped = null;
    function setCloud(text) {
      if (!cloud || text === lastTyped) return;
      lastTyped = text;
      cloud.textContent = text;
    }

    function finalize() {
      state.anims = [];
      state.done = true;
      global.removeEventListener('load', onLoad);
      document.body.style.overflow = prevOverflow;
      loader.removeAttribute('aria-busy');
      loader.setAttribute('aria-hidden', 'true');
      loader.setAttribute('data-ad-done', ''); // → display:none
      markSeen();
      if (onDone) onDone();
    }

    // The handoff: fade the screen, then the nav drops and the cards stagger.
    function exit() {
      setCount(100);
      if (!loader.animate) { finalize(); return; }
      var s = styles();
      var fade = loader.animate(
        [{ opacity: 1 }, { opacity: 0 }],
        { duration: FADE_MS, easing: 'linear', fill: 'forwards' }
      );
      state.anims.push(fade);
      fade.onfinish = function () {
        var nav = root.querySelector(navSel);
        var cards = Array.prototype.slice.call(root.querySelectorAll(staggerSel));
        var last = null;
        if (nav && nav.animate) {
          // the winner's nav drop — yPercent −102→0
          last = nav.animate(
            [{ transform: 'translateY(-102%)' }, { transform: 'translateY(0)' }],
            { duration: s.durReveal, easing: s.ease, fill: 'backwards' }
          );
          state.anims.push(last);
        }
        cards.forEach(function (card, i) {
          if (!card.animate) return;
          last = card.animate(
            [{ opacity: 0, transform: 'translateY(24px)' },
             { opacity: 1, transform: 'translateY(0)' }],
            { duration: s.durReveal, easing: s.ease, fill: 'backwards', delay: i * 80 }
          );
          state.anims.push(last);
        });
        if (last) last.onfinish = finalize;
        else finalize();
      };
    }

    // One rAF clock walks beats, chars and the counter together — linear
    // everywhere; the final beat holds until the real load before the exit.
    var start = 0;
    function tick(now) {
      if (!start) start = now;
      var t = now - start;
      var p = Math.min(1, t / total);
      setCount(p * 100);

      var acc = 0, i = 0;
      for (; i < beats.length; i++) {
        if (t < acc + beatDurs[i]) break;
        acc += beatDurs[i];
      }
      if (i >= beats.length) {
        setCloud(beats[beats.length - 1]);
        if (loaded) { state.raf = 0; exit(); return; }
      } else {
        var chars = Math.min(beats[i].length, Math.floor((t - acc) / charMs));
        setCloud(beats[i].slice(0, chars));
      }
      state.raf = global.requestAnimationFrame(tick);
    }
    state.raf = global.requestAnimationFrame(tick);

    var handle = {
      destroy: function () {
        if (state.raf) { global.cancelAnimationFrame(state.raf); state.raf = 0; }
        state.anims.forEach(function (a) { a.cancel(); });
        state.anims = [];
        global.removeEventListener('load', onLoad);
        document.body.style.overflow = prevOverflow;
        loader.classList.remove('ad-chat');
        loader.removeAttribute('aria-busy');
        loader.removeAttribute('aria-hidden');
        loader.removeAttribute('data-ad-near');
        loader.removeAttribute('data-ad-done');
        if (cloud) cloud.textContent = cloudText0;
        if (countEl) countEl.textContent = countText0;
        if (hadHidden) loader.setAttribute('hidden', '');
        else loader.removeAttribute('hidden');
        delete loader.__adChatLoader;
        var st = document.getElementById(CSS_ID);
        if (st && st.parentNode) st.parentNode.removeChild(st);
      }
    };
    state.handle = handle;
    return handle;
  }

  global.awardChatCloudLoader = { init: init };
})(typeof window !== 'undefined' ? window : this);
