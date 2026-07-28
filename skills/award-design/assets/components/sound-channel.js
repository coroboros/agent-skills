/*
 * sound-channel — the opt-in audio channel + its designed mute affordance
 * (winner: 21 TSI — SOTD 2025-04-12 + FWA + CSSDA, the corpus's ONE sound
 * carrier and a boundary member — thin evidence by design; ship only when
 * the brief sells sensory maximalism. The gate/discipline laws are the
 * references/ingredients/web-audio.md canon). A reusable channel: UI cues
 * and/or an ambient bed behind ONE persistent toggle, muted by default.
 *
 * THE UNLOCK GATE IS LAW — never autoplay: the AudioContext starts
 * suspended and resumes ONLY inside a real user gesture (pointerdown /
 * keydown / click — mousemove and scroll never count). Enabling sound is
 * itself a gesture (the toggle click), so the opt-in resumes directly; a
 * visitor whose previous visit opted in still needs this page's first
 * gesture before anything sounds (a per-navigation browser constraint —
 * the channel primes on it silently).
 * OFF BY DEFAULT, OPT-IN: nothing loads, decodes, or plays until the
 * visitor enables sound — cue fetch + decode are lazy behind the opt-in.
 * The preference persists across visits (localStorage); reduced-motion and
 * Save-Data are calm signals — a persisted ON is NOT auto-restored under
 * either (the toggle still works; the choice stays the visitor's, made
 * again this visit).
 * THE AFFORDANCE: one fixed, always-reachable toggle (JS-created — the
 * channel is pure enhancement, no-JS renders nothing) — a designed
 * four-bar meter glyph, not chrome: bars dance while sound is on (CSS
 * keyframes, no rAF; static under reduced-motion — the on-state then reads
 * by accent + bar height alone), rest low while muted. aria-pressed tracks
 * state, aria-label names the ACTION (Enable sound / Mute sound),
 * focus-visible ring, 44px tap target. Mute RAMPS the master gain (0.4s,
 * never a cut — a cut clicks), then suspends the context.
 * Sound never carries information alone — every play(name) pairs with a
 * visible state change on the calling surface; the channel enforces the
 * gate, the build keeps that law.
 *
 * Cue + bed spec (values are a URL or a factory):
 *   cues: { hover: '/audio/tick.mp3', send: fn }   fn(ctx, out) plays a
 *     synthesized cue into `out` — zero bytes, in-world material.
 *   bed: '/audio/loop.flac' | fn(ctx, out)   URL loops gaplessly
 *     (AudioBufferSourceNode loop:true); a factory builds a generative bed
 *     into `out` and may return { stop() }. Bed gain ramps to 0.1 over 2s
 *     on opt-in — felt, not heard. Keep micro-cues ≤ 0.3s, low gain.
 *
 * Usage:  var sc = awardSoundChannel.init(root, opts)
 *   root        Element|Document  kept for the library contract
 *   cues        { name: url|fn }  discrete UI cues (optional)
 *   bed         url|fn            the ambient bed (optional)
 *   storageKey  string            preference key (default 'ad-sound-on')
 * Returns { play(name), on(), toggle(force), getState(), destroy() }.
 *   play(name)  fires a cue — a silent no-op while muted or locked.
 *   toggle()    flips the channel (must run inside a user event to unlock).
 *   getState()  { on, context, bed, level } — level is an RMS read off the
 *               master analyser, the "did it actually sound" verification
 *               readout for drives and tests.
 * Idempotent — one channel per page; a second init returns the live handle.
 * destroy() removes the toggle, closes the context, removes the stylesheet.
 *
 * Tokens: --ad-ink + --ad-ground-2 (toggle chrome), --ad-accent (on-state
 * bars + focus ring), --ad-dur-base + --ad-ease-signature (the morph).
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-sound-channel-css';
  var STORE_DEFAULT = 'ad-sound-on';
  var MUTE_RAMP = 0.4;   // s — the web-audio.md ramp, never a cut
  var BED_GAIN = 0.1;    // the 0.05-0.15 band
  var BED_RAMP = 2;      // s — opt-in swell
  var CUE_GAIN = 0.4;    // discrete-cue bus level
  var instance = null;

  var reduce = function () {
    return !!(global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches);
  };
  var saveData = function () {
    var c = global.navigator && global.navigator.connection;
    return !!(c && c.saveData);
  };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var ink = 'var(--ad-ink,oklch(96% 0 0))';
    var accent = 'var(--ad-accent,oklch(62% 0.2 25))';
    var morph = 'var(--ad-dur-base,420ms) var(--ad-ease-signature,cubic-bezier(.16,1,.3,1))';
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      '.ad-sc{position:fixed;inset-block-end:1.1rem;inset-inline-end:1.1rem;' +
      'z-index:10000;inline-size:44px;block-size:44px;padding:0;border:0;' +
      'border-radius:999px;cursor:pointer;display:grid;place-items:center;' +
      'background:color-mix(in oklch,var(--ad-ground-2,oklch(18% 0.01 260)) 82%,transparent);' +
      'backdrop-filter:blur(6px);transition:transform ' + morph + ';}' +
      '.ad-sc:hover{transform:scale(1.08);}' +
      '.ad-sc:focus-visible{outline:2px solid ' + accent + ';outline-offset:3px;}' +
      '.ad-sc__bars{display:flex;align-items:flex-end;gap:2.5px;block-size:14px;}' +
      '.ad-sc__bars i{inline-size:2.5px;block-size:4px;border-radius:1px;' +
      'background:' + ink + ';opacity:.55;transition:block-size ' + morph +
      ',background-color ' + morph + ',opacity ' + morph + ';}' +
      // on: accent bars dance — CSS keyframes, no rAF; the stagger is the meter read
      '.ad-sc[data-on] .ad-sc__bars i{background:' + accent + ';opacity:1;' +
      'animation:ad-sc-dance .9s ease-in-out infinite alternate;}' +
      '.ad-sc[data-on] .ad-sc__bars i:nth-child(1){block-size:8px;animation-delay:0s;}' +
      '.ad-sc[data-on] .ad-sc__bars i:nth-child(2){block-size:13px;animation-delay:-.3s;}' +
      '.ad-sc[data-on] .ad-sc__bars i:nth-child(3){block-size:10px;animation-delay:-.6s;}' +
      '.ad-sc[data-on] .ad-sc__bars i:nth-child(4){block-size:6px;animation-delay:-.15s;}' +
      '@keyframes ad-sc-dance{from{transform:scaleY(.45);}to{transform:scaleY(1);}}' +
      // reduced motion: the on-state reads by accent + height alone
      '@media (prefers-reduced-motion:reduce){.ad-sc__bars i{animation:none!important;}}';
    document.head.appendChild(s);
  }

  function store(key, val) {
    try {
      if (val === undefined) return global.localStorage.getItem(key);
      global.localStorage.setItem(key, val);
    } catch (e) { return null; } // private mode → session-only behavior
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    if (instance) return instance.handle;

    var cues = opts.cues || {};
    var bed = opts.bed || null;
    var key = opts.storageKey || STORE_DEFAULT;

    var ctx = null, master = null, analyser = null, sfxBus = null, bedBus = null;
    var buffers = {};   // decoded cue buffers by name
    var bedState = { started: false, source: null, stop: null };
    var on = false;
    var suspendTimer = 0;
    var destroyed = false;

    injectCss();
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'ad-sc';
    btn.setAttribute('aria-pressed', 'false');
    btn.setAttribute('aria-label', 'Enable sound');
    var bars = document.createElement('span');
    bars.className = 'ad-sc__bars';
    bars.setAttribute('aria-hidden', 'true');
    for (var i = 0; i < 4; i++) bars.appendChild(document.createElement('i'));
    btn.appendChild(bars);
    (document.body || document.documentElement).appendChild(btn);

    function ensureCtx() {
      if (ctx) return ctx;
      var AC = global.AudioContext || global.webkitAudioContext;
      if (!AC) return null;
      ctx = new AC(); // created suspended outside a gesture — resume is gated
      master = ctx.createGain();
      master.gain.value = 0;
      analyser = ctx.createAnalyser();
      analyser.fftSize = 256;
      master.connect(analyser);
      analyser.connect(ctx.destination);
      sfxBus = ctx.createGain();
      sfxBus.gain.value = CUE_GAIN;
      sfxBus.connect(master);
      bedBus = ctx.createGain();
      bedBus.gain.value = 0;
      bedBus.connect(master);
      return ctx;
    }

    function loadCues() {
      Object.keys(cues).forEach(function (name) {
        var src = cues[name];
        if (typeof src !== 'string' || buffers[name] !== undefined) return;
        buffers[name] = null; // in flight
        global.fetch(src)
          .then(function (r) { return r.arrayBuffer(); })
          .then(function (ab) { return ctx.decodeAudioData(ab); })
          .then(function (buf) { buffers[name] = buf; })
          .catch(function (err) {
            delete buffers[name];
            if (global.console) console.warn('sound-channel: cue "' + name + '" failed to load', err);
          });
      });
    }

    function startBed() {
      if (!bed || bedState.started || !ctx) return;
      bedState.started = true;
      if (typeof bed === 'function') {
        bedState.stop = (bed(ctx, bedBus) || {}).stop || null;
        bedBus.gain.setTargetAtTime(BED_GAIN, ctx.currentTime, BED_RAMP / 3);
        return;
      }
      global.fetch(bed)
        .then(function (r) { return r.arrayBuffer(); })
        .then(function (ab) { return ctx.decodeAudioData(ab); })
        .then(function (buf) {
          if (destroyed || !bedState.started) return;
          var src = ctx.createBufferSource();
          src.buffer = buf;
          src.loop = true;
          src.connect(bedBus);
          src.start();
          bedState.source = src;
          bedBus.gain.setTargetAtTime(BED_GAIN, ctx.currentTime, BED_RAMP / 3);
        })
        .catch(function (err) {
          bedState.started = false;
          if (global.console) console.warn('sound-channel: bed failed to load', err);
        });
    }

    // Resume ONLY inside a real gesture — the callers below are all gated.
    function unlock() {
      if (!on || !ensureCtx()) return;
      if (suspendTimer) { clearTimeout(suspendTimer); suspendTimer = 0; }
      var up = function () {
        master.gain.cancelScheduledValues(ctx.currentTime);
        master.gain.setTargetAtTime(1, ctx.currentTime, MUTE_RAMP / 3);
        loadCues();
        startBed();
      };
      if (ctx.state === 'suspended') ctx.resume().then(up, function () {});
      else up();
    }

    function reflect() {
      if (on) {
        btn.setAttribute('data-on', '');
        btn.setAttribute('aria-pressed', 'true');
        btn.setAttribute('aria-label', 'Mute sound');
      } else {
        btn.removeAttribute('data-on');
        btn.setAttribute('aria-pressed', 'false');
        btn.setAttribute('aria-label', 'Enable sound');
      }
    }

    function toggle(force) {
      var next = force != null ? !!force : !on;
      if (next === on) return;
      on = next;
      store(key, on ? '1' : '0');
      reflect();
      if (on) unlock(); // the toggle event IS the gesture
      else if (ctx) {
        // ramp, never cut — then park the context after the tail
        master.gain.cancelScheduledValues(ctx.currentTime);
        master.gain.setTargetAtTime(0, ctx.currentTime, MUTE_RAMP / 3);
        suspendTimer = setTimeout(function () {
          suspendTimer = 0;
          if (!on && ctx && ctx.state === 'running') ctx.suspend();
        }, MUTE_RAMP * 1000 + 100);
      }
    }

    function play(name) {
      if (!on || !ctx || ctx.state !== 'running') return; // silent no-op
      var src = cues[name];
      if (typeof src === 'function') { src(ctx, sfxBus); return; }
      var buf = buffers[name];
      if (!buf) return; // not loaded (yet) — never queue, never throw
      var node = ctx.createBufferSource();
      node.buffer = buf;
      node.connect(sfxBus);
      node.start();
    }

    function getState() {
      var level = 0;
      if (analyser) {
        var data = new Uint8Array(analyser.fftSize);
        analyser.getByteTimeDomainData(data);
        var sum = 0;
        for (var i = 0; i < data.length; i++) {
          var d = (data[i] - 128) / 128;
          sum += d * d;
        }
        level = Math.sqrt(sum / data.length);
      }
      return {
        on: on,
        context: ctx ? ctx.state : 'none',
        bed: bedState.started,
        level: level
      };
    }

    // A persisted ON still waits for THIS page's first gesture; calm signals
    // (reduced-motion, Save-Data) never auto-restore it.
    if (store(key) === '1' && !reduce() && !saveData()) {
      on = true;
      reflect();
    }
    var onToggle = function () { toggle(); };
    var prime = function () { unlock(); };
    btn.addEventListener('click', onToggle);
    document.addEventListener('pointerdown', prime, true);
    document.addEventListener('keydown', prime, true);
    document.addEventListener('click', prime, true);
    // a hidden tab never keeps a bed running; return resumes only a still-ON channel
    var onVis = function () {
      if (!ctx) return;
      if (document.hidden) {
        if (ctx.state === 'running') ctx.suspend();
      } else if (on && ctx.state === 'suspended') {
        ctx.resume().then(function () {}, function () {});
      }
    };
    document.addEventListener('visibilitychange', onVis);

    var handle = {
      play: play,
      on: function () { return on; },
      toggle: toggle,
      getState: getState,
      destroy: function () {
        destroyed = true;
        btn.removeEventListener('click', onToggle);
        document.removeEventListener('pointerdown', prime, true);
        document.removeEventListener('keydown', prime, true);
        document.removeEventListener('click', prime, true);
        document.removeEventListener('visibilitychange', onVis);
        if (suspendTimer) { clearTimeout(suspendTimer); suspendTimer = 0; }
        if (bedState.stop) { try { bedState.stop(); } catch (e) {} }
        if (bedState.source) { try { bedState.source.stop(); } catch (e) {} }
        if (ctx) { try { ctx.close(); } catch (e) {} ctx = null; }
        if (btn.parentNode) btn.parentNode.removeChild(btn);
        instance = null;
        var s = document.getElementById(CSS_ID);
        if (s && s.parentNode) s.parentNode.removeChild(s);
      }
    };
    instance = { handle: handle };
    return handle;
  }

  global.awardSoundChannel = { init: init };
})(typeof window !== 'undefined' ? window : this);
