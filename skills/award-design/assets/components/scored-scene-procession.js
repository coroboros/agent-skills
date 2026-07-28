/*
 * scored-scene-procession — the cinematic-pavilion conductor (winners:
 * Cartier Watches & Wonders 2025 — SOTD Aug 18 2025, 7.64 + Dev Award; six
 * self-contained 3D alcoves 'like rooms in a very expensive museum after
 * hours', scenes dispose/load as you cross between them, a continuous
 * Mooders score threading them — structure + score confirmed via
 * webgpu.com, per-scene timings not exposed; Cartier WAW 2026 — SOTD May
 * 2026, the same studio's re-win; Louis Vuitton Collectibles — SOTD Feb
 * 2024, change-universe navigation between distinct environments).
 * The two halves of the pavilion the library could not execute, welded onto
 * the rooms-procession rig:
 *   1. SCENE LIFECYCLE — the dispose/load policy: only the active room and
 *      its `margin` neighbors stay mounted; onSceneLoad fires as a room
 *      enters that live window (mount/prepare the alcove there),
 *      onSceneDispose as it leaves (dispose GPU resources there). The live
 *      window is stamped data-ad-ssp-load on each room element.
 *   2. THE SCORE — a continuous scored soundscape as a NARRATIVE layer: a
 *      looping bed plus one stem per room, each stem's gain keyed to the
 *      procession position (gain = 1 - distance to that room), so walking
 *      the pavilion IS mixing the score — the Cartier register, not
 *      wallpaper. The unlock law is absolute: the AudioContext is created
 *      and resumed ONLY inside the user's gesture on the one fixed,
 *      always-reachable toggle (aria-pressed, muted by default).
 * Ruled DISTINCT, not an alias, on mechanism: rooms-procession (merged
 * after this gap was written) owns ONLY the scroll → room-index / progress
 * / transition math — no lifecycle policy, no audio; this conductor
 * REQUIRES it (window.awardRoomsProcession — it constructs the rig, passes
 * the builder's callbacks through untouched, and never re-derives the
 * scroll math). sound-channel is bold-maximal's page-level UI-SFX/ambient
 * costume — its bed is scene-agnostic by design; here every stem is keyed
 * to the walk. One audio carrier per page, ever: on a pavilion page this
 * component IS that carrier — never beside sound-channel.
 *
 * Markup is the rig's own contract ([data-ad-rooms] > [data-room] …); the
 * builder's engine listens to the callbacks. The rig reads scrollY, so a
 * Lenis-smoothed page drives it on the same clock (the GSAP + Lenis
 * one-clock register — smoother-agnostic by construction).
 *
 * Usage:  awardScoredSceneProcession.init(track, {
 *   margin:         1,                      // rooms kept live each side
 *   onSceneLoad:    function (i, el) {},    // entered the live window
 *   onSceneDispose: function (i, el) {},    // left it — free the GPU here
 *   onRoom: fn, onProgress: fn, onTransition: fn, window: n, ease: n,
 *                                           // → passed through to the rig
 *   score: {
 *     bed:   url | factory(ctx),            // the continuous ground layer
 *     stems: [url | factory(ctx), …],       // one per room, position-keyed
 *     volume: 0.55                          // master ceiling when unlocked
 *   }
 * })
 * Returns { destroy() }. Idempotent — one conductor per page; a second
 * init returns the live handle. destroy() closes the audio graph, removes
 * the toggle and stamps, and destroys the rig it constructed.
 *
 * A URL source is fetched + decoded lazily on first unlock and looped; a
 * factory is called with the AudioContext inside the unlock gesture and
 * returns a producing AudioNode (zero bytes — the sound-channel source
 * grammar). Stem gains move on short ramps (zipper-safe); under reduced
 * motion the rig snaps by its own law and the stem mix snaps with it —
 * the toggle stays fully operable (audio is not motion) and its chrome is
 * static. No-JS: the rooms are plain legible flow (the rig's floor) and no
 * toggle exists — nothing is gated.
 *
 * Tokens: --ad-ink, --ad-ground-2, --ad-font-mono (toggle chrome),
 * --ad-dur-base + --ad-ease-signature (toggle state morph).
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-scored-scene-procession-css';
  var MARGIN_DEFAULT = 1;    // active alcove + neighbors — the dispose/load default
  var VOLUME_DEFAULT = 0.55; // a score under the page, never over it
  var RAMP = 0.08;           // s — zipper-safe gain ramps
  var UNLOCK_SWEEP = 1.2;    // s — the unlocked score arrives, decelerating

  var reduce = function () {
    return !!(global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches);
  };
  var clamp01 = function (v) { return v < 0 ? 0 : v > 1 ? 1 : v; };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var ink = 'var(--ad-ink,oklch(96% 0 0))';
    var morph = 'var(--ad-dur-base,420ms) var(--ad-ease-signature,cubic-bezier(.16,1,.3,1))';
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      // the one fixed, always-reachable unlock toggle — quiet chrome, no
      // keyframes anywhere so reduce needs no carve-out
      '.ad-ssp-toggle{position:fixed;right:1.4rem;bottom:1.4rem;z-index:9997;' +
      'appearance:none;border:1px solid color-mix(in oklch,' + ink + ' 30%,transparent);' +
      'border-radius:999px;padding:.55em 1.1em;cursor:pointer;' +
      'background:color-mix(in oklch,var(--ad-ground-2,oklch(18% 0.01 260)) 82%,transparent);' +
      'color:' + ink + ';font-family:var(--ad-font-mono,ui-monospace,monospace);' +
      'font-size:.62rem;letter-spacing:.16em;text-transform:uppercase;}' +
      '.ad-ssp-toggle::after{content:"";display:block;height:1px;margin-top:.35em;' +
      'background:currentColor;opacity:.25;transform:scaleX(.35);transform-origin:left;' +
      'transition:transform ' + morph + ',opacity ' + morph + ';}' +
      '.ad-ssp-toggle[aria-pressed="true"]::after{opacity:.9;transform:scaleX(1);}';
    document.head.appendChild(s);
  }

  var current = null; // one conductor (and one audio carrier) per page, ever

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    if (current) return current;

    var rigLib = global.awardRoomsProcession;
    if (!rigLib) {
      // fail loud, degrade legible: the rooms remain plain readable flow
      if (global.console) console.warn(
        'scored-scene-procession: rooms-procession is required (load rooms-procession.js first)');
      return { destroy: function () {} };
    }

    var track = (root.getAttribute && root.getAttribute('data-ad-rooms') !== null)
      ? root
      : (root.querySelector ? root.querySelector('[data-ad-rooms]') : null);
    if (!track) return { destroy: function () {} };
    var roomEls = Array.prototype.filter.call(track.children, function (el) {
      return el.hasAttribute('data-room');
    });
    if (!roomEls.length) return { destroy: function () {} };

    injectCss();

    var margin = opts.margin != null ? opts.margin : MARGIN_DEFAULT;
    var score = opts.score || null;
    var n = roomEls.length;

    // ---- scene lifecycle: the dispose/load window --------------------------
    var live = roomEls.map(function () { return false; });
    function applyWindow(active) {
      for (var i = 0; i < n; i++) {
        var want = Math.abs(i - active) <= margin;
        if (want && !live[i]) {
          live[i] = true;
          roomEls[i].setAttribute('data-ad-ssp-load', '');
          if (opts.onSceneLoad) opts.onSceneLoad(i, roomEls[i]);
        } else if (!want && live[i]) {
          live[i] = false;
          roomEls[i].removeAttribute('data-ad-ssp-load');
          if (opts.onSceneDispose) opts.onSceneDispose(i, roomEls[i]);
        }
      }
    }

    // ---- the score: bed + position-keyed stems -----------------------------
    var audio = {
      ctx: null, master: null, bedGain: null,
      stems: [],       // { gain, started }
      on: false, built: false, pos: 0
    };

    function connectSource(src, gainNode) {
      if (typeof src === 'function') {
        var node = src(audio.ctx); // the factory produces; we only mix
        if (node && node.connect) node.connect(gainNode);
        return Promise.resolve();
      }
      return global.fetch(String(src))
        .then(function (r) { return r.arrayBuffer(); })
        .then(function (ab) { return audio.ctx.decodeAudioData(ab); })
        .then(function (buf) {
          var bs = audio.ctx.createBufferSource();
          bs.buffer = buf;
          bs.loop = true;
          bs.connect(gainNode);
          bs.start();
        })
        .catch(function () {}); // a lost stem thins the mix, never breaks the walk
    }

    function buildGraph() {
      if (audio.built || !score) return;
      audio.built = true;
      audio.master = audio.ctx.createGain();
      audio.master.gain.value = 0;
      audio.master.connect(audio.ctx.destination);
      if (score.bed) {
        audio.bedGain = audio.ctx.createGain();
        audio.bedGain.gain.value = 1;
        audio.bedGain.connect(audio.master);
        connectSource(score.bed, audio.bedGain);
      }
      (score.stems || []).slice(0, n).forEach(function (src, i) {
        var g = audio.ctx.createGain();
        g.gain.value = 0;
        g.connect(audio.master);
        audio.stems.push(g);
        connectSource(src, g);
      });
      mixStems(audio.pos, true);
    }

    // The narrative mix: each stem's gain is its room's proximity to the
    // walker — crossing a boundary IS the crossfade.
    function mixStems(pos, snap) {
      audio.pos = pos;
      if (!audio.ctx) return;
      var t = audio.ctx.currentTime;
      for (var i = 0; i < audio.stems.length; i++) {
        var g = clamp01(1 - Math.abs(pos - i));
        var p = audio.stems[i].gain;
        if (snap || reduce()) p.setValueAtTime(g, t);
        else { p.cancelScheduledValues(t); p.setValueAtTime(p.value, t); p.linearRampToValueAtTime(g, t + RAMP); }
      }
    }

    function setMaster(onNow) {
      var vol = score && score.volume != null ? score.volume : VOLUME_DEFAULT;
      var t = audio.ctx.currentTime;
      var p = audio.master.gain;
      p.cancelScheduledValues(t);
      p.setValueAtTime(p.value, t);
      if (reduce()) p.setValueAtTime(onNow ? vol : 0, t);
      else p.linearRampToValueAtTime(onNow ? vol : 0, t + (onNow ? UNLOCK_SWEEP : 0.4));
    }

    // ---- the unlock toggle — the ONLY place the context is created ---------
    var toggle = null;
    if (score) {
      toggle = document.createElement('button');
      toggle.type = 'button';
      toggle.className = 'ad-ssp-toggle';
      toggle.setAttribute('aria-pressed', 'false');
      toggle.textContent = 'Sound';
      toggle.setAttribute('aria-label', 'Play the score');
      toggle.addEventListener('click', function () {
        if (!audio.ctx) {
          var AC = global.AudioContext || global.webkitAudioContext;
          if (!AC) return;
          audio.ctx = new AC(); // inside the gesture — the unlock law
          buildGraph();
        }
        audio.on = !audio.on;
        toggle.setAttribute('aria-pressed', String(audio.on));
        toggle.setAttribute('aria-label', audio.on ? 'Mute the score' : 'Play the score');
        if (audio.on) audio.ctx.resume().then(function () { setMaster(true); });
        else setMaster(false);
      });
      (document.body || document.documentElement).appendChild(toggle);
    }

    // a hidden tab suspends the score; return resumes only a still-ON mix
    var onVis = function () {
      if (!audio.ctx) return;
      if (document.hidden) {
        if (audio.ctx.state === 'running') audio.ctx.suspend();
      } else if (audio.on && audio.ctx.state === 'suspended') {
        audio.ctx.resume().then(function () {}, function () {});
      }
    };
    document.addEventListener('visibilitychange', onVis);

    // ---- the rig: constructed here, builder callbacks pass through ---------
    var rig = rigLib.init(track, {
      window: opts.window,
      ease: opts.ease,
      onRoom: function (index, prev) {
        applyWindow(index);
        if (opts.onRoom) opts.onRoom(index, prev);
      },
      onProgress: function (index, t) {
        mixStems(index + t, false);
        if (opts.onProgress) opts.onProgress(index, t);
      },
      onTransition: opts.onTransition
    });

    current = {
      destroy: function () {
        rig.destroy();
        document.removeEventListener('visibilitychange', onVis);
        if (audio.ctx) { try { audio.ctx.close(); } catch (e) {} }
        if (toggle && toggle.parentNode) toggle.parentNode.removeChild(toggle);
        roomEls.forEach(function (el) { el.removeAttribute('data-ad-ssp-load'); });
        var s = document.getElementById(CSS_ID);
        if (s && s.parentNode) s.parentNode.removeChild(s);
        current = null;
      }
    };
    return current;
  }

  global.awardScoredSceneProcession = { init: init };
})(typeof window !== 'undefined' ? window : this);
