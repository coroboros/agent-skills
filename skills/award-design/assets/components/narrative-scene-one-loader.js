/*
 * narrative-scene-one-loader — the cover IS scene one (winner: Ponpon Mania —
 * SOTM 2025-10 + Dev Award; 'cover-as-scene-one, no separate loader' is the
 * verified corpus fact; the recipes ref reads 'read-now hands the live cover
 * into the reader'). NOT an overlay gate: the visitor arrives ON the story's
 * first scene — the cover's poster stands from first paint, the live ground
 * (WebGL / shader-surface / physics) warms up UNDER it, and when the build
 * signals ready the poster crossfades away and the READ-NOW affordance rises.
 * Activating it is the in-character handoff: the cover scrolls into the
 * reader (the chapter flow) and the build's entrance choreography fires via
 * onRead. Scroll is NEVER locked — the cue is an invitation, not a gate; a
 * visitor who scrolls past it has simply started reading (the gated-splash
 * component is the consent gate, this is the opposite move). Never adds
 * perceived latency past asset-ready: the swap fires the moment ready
 * resolves, with no minimum hold.
 * No-JS / dead script: the poster and the authored cue stand, the cue is a
 * plain anchor jump — nothing is gated. Reduced motion: the poster STANDS as
 * the scene (the scrubbed-media-becomes-poster floor), the cue is visible
 * immediately, activation is an instant jump.
 *
 * Expected markup — typically the chapter-cover form's slots; the cue is a
 * real link so the no-JS path works:
 *   <section data-ad-form="chapter-cover">
 *     <figure data-slot="ground">
 *       <img data-ad-scene-poster src="…" alt="…">
 *       <div data-ad-scene-live>…canvas / scene mount…</div>
 *     </figure>
 *     …
 *     <div data-slot="read-cue"><a data-ad-read-now href="#reader">Read now</a></div>
 *   </section>
 *
 * Usage:  awardNarrativeSceneOneLoader.init(root, opts)
 *   root      Element|Document  scope (default document)
 *   selector  string   the cover (default '[data-ad-scene-one]', falling back
 *                      to '[data-ad-form="chapter-cover"]')
 *   ready     Promise  resolves when the live scene is warm (default: the
 *                      window 'load' event — tie it to the engine's real
 *                      asset manager when there is one)
 *   target    string   reader selector (default: the cue's own href hash,
 *                      else the cover's next section sibling)
 *   onRead    function fires once on the handoff — mount the reader's
 *                      entrance choreography here
 * Returns { destroy() }. Idempotent per cover. destroy() restores the
 * authored attributes and removes the stylesheet.
 *
 * A11y + perf: while warming the cover is aria-busy and the cue is
 * visibility-hidden (out of the tab order, JS-applied so a dead script never
 * hides it); the poster crossfade is opacity-only on a promoted layer; there
 * is no rAF at all — the component is event-driven end to end.
 *
 * Tokens: --ad-dur-reveal + --ad-ease-signature (poster fade and cue rise).
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-narrative-scene-one-loader-css';

  var reduce = function () {
    return !!(global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches);
  };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var t = 'var(--ad-dur-reveal,800ms) var(--ad-ease-signature,cubic-bezier(.16,1,.3,1))';
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      // warming: cue held out of view AND out of the tab order (JS-applied)
      '.ad-nso--warming [data-ad-read-now]{visibility:hidden;opacity:0;' +
      'transform:translateY(12px);}' +
      '[data-ad-read-now]{transition:opacity ' + t + ',transform ' + t + ';}' +
      // live: the poster lifts off the running scene
      '[data-ad-scene-poster]{transition:opacity ' + t + ';will-change:opacity;}' +
      '.ad-nso--live [data-ad-scene-poster]{opacity:0;}';
    document.head.appendChild(s);
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-scene-one]';
    var onRead = typeof opts.onRead === 'function' ? opts.onRead : null;

    var cover = root.querySelector(selector) ||
      root.querySelector('[data-ad-form="chapter-cover"]');
    if (!cover) return { destroy: function () {} };
    if (cover.__adNso) return cover.__adNso; // idempotent per cover

    var cue = cover.querySelector('[data-ad-read-now]');

    function readerTarget() {
      if (opts.target) return root.querySelector(opts.target);
      if (cue) {
        var href = cue.getAttribute('href') || '';
        if (href.charAt(0) === '#' && href.length > 1) {
          var t = document.getElementById(href.slice(1));
          if (t) return t;
        }
      }
      return cover.nextElementSibling;
    }

    var readFired = false;
    function handoff(e) {
      var target = readerTarget();
      if (target) {
        if (e) e.preventDefault();
        target.scrollIntoView({ behavior: reduce() ? 'auto' : 'smooth', block: 'start' });
      } // no target → a real link keeps its native jump
      cover.setAttribute('data-ad-nso-read', '');
      if (onRead && !readFired) { readFired = true; onRead(); }
    }

    // Reduced motion: the poster IS the scene, the cue is live immediately —
    // only the in-character handoff (instant jump + onRead) remains.
    if (reduce()) {
      var onClickRM = function (e) { handoff(e); };
      if (cue) cue.addEventListener('click', onClickRM);
      var rmHandle = {
        destroy: function () {
          if (cue) cue.removeEventListener('click', onClickRM);
          cover.removeAttribute('data-ad-nso-read');
          delete cover.__adNso;
        }
      };
      cover.__adNso = rmHandle;
      return rmHandle;
    }

    injectCss();
    var live = false;

    // warming — the poster stands, the scene warms under it, the cue holds
    cover.classList.add('ad-nso--warming');
    cover.setAttribute('aria-busy', 'true');

    function goLive() {
      if (live) return;
      live = true;
      cover.removeAttribute('aria-busy');
      cover.classList.remove('ad-nso--warming'); // the cue rises
      cover.classList.add('ad-nso--live');       // the poster lifts off
    }

    var onLoad = null;
    if (opts.ready && typeof opts.ready.then === 'function') {
      opts.ready.then(goLive, goLive); // a failed warm-up never strands the cover
    } else if (document.readyState === 'complete') {
      goLive();
    } else {
      onLoad = function () { goLive(); };
      global.addEventListener('load', onLoad);
    }

    var onClick = function (e) { handoff(e); };
    if (cue) cue.addEventListener('click', onClick);

    var handle = {
      destroy: function () {
        if (onLoad) global.removeEventListener('load', onLoad);
        if (cue) cue.removeEventListener('click', onClick);
        cover.classList.remove('ad-nso--warming', 'ad-nso--live');
        cover.removeAttribute('aria-busy');
        cover.removeAttribute('data-ad-nso-read');
        delete cover.__adNso;
        var s = document.getElementById(CSS_ID);
        if (s && s.parentNode) s.parentNode.removeChild(s);
      }
    };
    cover.__adNso = handle;
    return handle;
  }

  global.awardNarrativeSceneOneLoader = { init: init };
})(typeof window !== 'undefined' ? window : this);
