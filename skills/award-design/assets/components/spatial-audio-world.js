/*
 * spatial-audio-world — the POSITIONAL audio bed of the playable world
 * (winners: Bruno's Portfolio — SOTD 2026-01-21 + Dev Award + SOTM Jan
 * 2026: springs/hydraulics/engine/tire-friction ON the vehicle, birds/
 * crickets/waves/wind/thunder IN the environment, three CC0 ambient tracks
 * by Kounine, the start gate doubling as the audio unlock; Resn's KPR world
 * carries the register. Winner PARAMETERS were never published — panner
 * model, distances and gains here are DEFAULTS and say so). Each source is
 * a Web Audio PannerNode tied to its object's WORLD COORDINATES; the
 * listener rides the camera — so sounds pan and attenuate as the visitor
 * moves through the world. Day-night/weather modulate the mix through
 * setSourceGain (the builder's clock owns the weather).
 * Ruled on the seams — three carriers, ONE per page, ever: sound-channel
 * (merged) is the page-level UI-SFX/ambient COSTUME, its bed scene-agnostic
 * by design — zero geometry; scored-scene-procession's score is the
 * pavilion's NARRATIVE mix — per-room stem gains keyed to a 1D procession
 * position, no panner, no space; THIS is the world carrier — 3D positions
 * through PannerNode/listener geometry, pan + attenuation computed from
 * where things ARE. A spatial-world page ships this and neither of the
 * other two. What is REUSED from the merged carrier is its affordance
 * contract, restated under this namespace: the same designed four-bar
 * meter toggle, aria-pressed, action-naming label, 44px target, ramp-
 * never-cut mute.
 *
 * THE UNLOCK GATE IS LAW — never autoplay: the AudioContext resumes ONLY
 * inside a real user gesture. On a world page the START GATE doubles as
 * the unlock (a hard browser constraint, not a taste choice) — the builder
 * calls handle.unlock() inside the gate's enter handler (gated-splash
 * onEnter is the intended seam); the toggle click is itself a gesture and
 * unlocks too. A persisted MUTE is honored across visits (localStorage);
 * WebM/Opus first with MP3 fallback rides the url-array contract; decode
 * is lazy behind the unlock — nothing loads before consent.
 * prefers-reduced-motion (and Save-Data) are calm signals: the world stays
 * SILENT — unlock() primes the graph but starts nothing; only the
 * visitor's own explicit toggle click sounds it this visit.
 * visibilitychange pauses a hidden tab (context suspends) and resumes an
 * audible one. Sound never carries information alone — every source pairs
 * with a visible world object; the build keeps that law.
 *
 * Usage:  var saw = awardSpatialAudioWorld.init(root, opts)
 *   sources  [{ id, url: 'x.webm'|['x.webm','x.mp3'] | make: fn(ctx,out),
 *               x,y,z, loop (default true), gain (default 0.5),
 *               ref (refDistance, default 3), rolloff (default 1) }]
 *   storageKey  string  preference key (default 'ad-saw-on')
 * Returns handle:
 *   unlock()               call INSIDE the start gesture — resumes + starts
 *   toggle(force)          the designed mute (its click is a gesture)
 *   setListener(x,y,z,fx,fy,fz)  the camera each frame (forward optional)
 *   setSource(id,x,y,z)    a moving object's position
 *   setSourceGain(id,g,ramp)     weather/day-night modulation
 *   play(id)               fire a non-loop source at its position
 *   getState()             { on, context, level, left, right, listener,
 *                            sources:[{id,x,y,z,playing}] } — level is the
 *                            master RMS, left/right the split-channel RMS:
 *                            the pan, measured. The drive/test readout.
 *   destroy()
 * Idempotent — one carrier per page; a second init returns the live handle.
 *
 * Tokens: --ad-ink + --ad-ground-2 (toggle chrome), --ad-accent (on-state
 * bars + focus ring), --ad-dur-base + --ad-ease-signature (the morph).
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-spatial-audio-css';
  var STORE_DEFAULT = 'ad-saw-on';
  var MUTE_RAMP = 0.4;   // s — ramp, never a cut
  var SWELL = 2;         // s — world fade-in on unlock
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
      '.ad-saw{position:fixed;inset-block-end:1.1rem;inset-inline-end:1.1rem;' +
      'z-index:10000;inline-size:44px;block-size:44px;padding:0;border:0;' +
      'border-radius:999px;cursor:pointer;display:grid;place-items:center;' +
      'background:color-mix(in oklch,var(--ad-ground-2,oklch(18% 0.01 260)) 82%,transparent);' +
      'backdrop-filter:blur(6px);transition:transform ' + morph + ';}' +
      '.ad-saw:hover{transform:scale(1.08);}' +
      '.ad-saw:focus-visible{outline:2px solid ' + accent + ';outline-offset:3px;}' +
      '.ad-saw__bars{display:flex;align-items:flex-end;gap:2.5px;block-size:14px;}' +
      '.ad-saw__bars i{inline-size:2.5px;block-size:4px;border-radius:1px;' +
      'background:' + ink + ';opacity:.55;transition:block-size ' + morph +
      ',background-color ' + morph + ',opacity ' + morph + ';}' +
      '.ad-saw[data-on] .ad-saw__bars i{background:' + accent + ';opacity:1;' +
      'animation:ad-saw-dance .9s ease-in-out infinite alternate;}' +
      '.ad-saw[data-on] .ad-saw__bars i:nth-child(1){block-size:8px;animation-delay:0s;}' +
      '.ad-saw[data-on] .ad-saw__bars i:nth-child(2){block-size:13px;animation-delay:-.3s;}' +
      '.ad-saw[data-on] .ad-saw__bars i:nth-child(3){block-size:10px;animation-delay:-.6s;}' +
      '.ad-saw[data-on] .ad-saw__bars i:nth-child(4){block-size:6px;animation-delay:-.15s;}' +
      '@keyframes ad-saw-dance{from{transform:scaleY(.45);}to{transform:scaleY(1);}}' +
      // reduced motion: the on-state reads by accent + bar height alone
      '@media (prefers-reduced-motion:reduce){.ad-saw__bars i{animation:none!important;}}';
    document.head.appendChild(s);
  }

  function store(key, val) {
    try {
      if (val === undefined) return global.localStorage.getItem(key);
      global.localStorage.setItem(key, val);
    } catch (e) { return null; }
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    if (instance) return instance.handle;

    var defs = (opts.sources || []).map(function (d) {
      return {
        id: d.id, url: d.url, make: d.make,
        x: +d.x || 0, y: +d.y || 0, z: +d.z || 0,
        loop: d.loop !== false, gain: d.gain != null ? +d.gain : 0.5,
        ref: d.ref != null ? +d.ref : 3,
        rolloff: d.rolloff != null ? +d.rolloff : 1,
        node: null, panner: null, out: null, buffer: null, playing: false, stop: null
      };
    });
    var key = opts.storageKey || STORE_DEFAULT;

    var ctx = null, master = null, analyser = null, split = null, aL = null, aR = null;
    var on = false, started = false, destroyed = false;
    var listenerPos = [0, 0, 0];
    var listenerFwd = null;
    var suspendTimer = 0;

    injectCss();
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'ad-saw';
    btn.setAttribute('aria-pressed', 'false');
    btn.setAttribute('aria-label', 'Enable sound');
    var bars = document.createElement('span');
    bars.className = 'ad-saw__bars';
    bars.setAttribute('aria-hidden', 'true');
    for (var i = 0; i < 4; i++) bars.appendChild(document.createElement('i'));
    btn.appendChild(bars);
    (document.body || document.documentElement).appendChild(btn);

    function ensureCtx() {
      if (ctx) return ctx;
      var AC = global.AudioContext || global.webkitAudioContext;
      if (!AC) return null;
      ctx = new AC();
      master = ctx.createGain();
      master.gain.value = 0;
      analyser = ctx.createAnalyser();
      analyser.fftSize = 256;
      // split analysers: the pan, measurable — left vs right RMS
      split = ctx.createChannelSplitter(2);
      aL = ctx.createAnalyser(); aL.fftSize = 256;
      aR = ctx.createAnalyser(); aR.fftSize = 256;
      master.connect(analyser);
      master.connect(split);
      split.connect(aL, 0);
      split.connect(aR, 1);
      analyser.connect(ctx.destination);
      // the camera may have moved behind the gate — re-apply the stored
      // pose so the world does not boot with a stale center listener
      // (drive-caught)
      applyListener();
      return ctx;
    }

    function applyListener() {
      if (!ctx) return;
      var L = ctx.listener;
      if (L.positionX) {
        L.positionX.value = listenerPos[0];
        L.positionY.value = listenerPos[1];
        L.positionZ.value = listenerPos[2];
        if (listenerFwd && L.forwardX) {
          L.forwardX.value = listenerFwd[0];
          L.forwardY.value = listenerFwd[1];
          L.forwardZ.value = listenerFwd[2];
        }
      } else {
        L.setPosition(listenerPos[0], listenerPos[1], listenerPos[2]);
        if (listenerFwd) L.setOrientation(listenerFwd[0], listenerFwd[1], listenerFwd[2], 0, 1, 0);
      }
    }

    function rms(a) {
      if (!a) return 0;
      var data = new Uint8Array(a.fftSize);
      a.getByteTimeDomainData(data);
      var sum = 0;
      for (var i = 0; i < data.length; i++) {
        var d = (data[i] - 128) / 128;
        sum += d * d;
      }
      return Math.sqrt(sum / data.length);
    }

    function pickUrl(url) {
      var list = Array.isArray(url) ? url : [url];
      var probe = document.createElement('audio');
      for (var i = 0; i < list.length; i++) {
        var ext = String(list[i]).split('.').pop().toLowerCase();
        var mime = ext === 'webm' ? 'audio/webm; codecs="opus"'
                 : ext === 'ogg' ? 'audio/ogg' : ext === 'flac' ? 'audio/flac'
                 : ext === 'wav' ? 'audio/wav' : 'audio/mpeg';
        if (probe.canPlayType && probe.canPlayType(mime)) return list[i];
      }
      return list[list.length - 1]; // let the fetch/decode chain report
    }

    function mountSource(d) {
      if (d.out) return;
      d.panner = ctx.createPanner();
      // HRTF is the positional register; every distance number is a DEFAULT
      d.panner.panningModel = 'HRTF';
      d.panner.distanceModel = 'inverse';
      d.panner.refDistance = d.ref;
      d.panner.rolloffFactor = d.rolloff;
      d.out = ctx.createGain();
      d.out.gain.value = d.gain;
      d.out.connect(d.panner);
      d.panner.connect(master);
      placeSource(d);
    }

    function placeSource(d) {
      if (!d.panner) return;
      if (d.panner.positionX) {
        d.panner.positionX.value = d.x;
        d.panner.positionY.value = d.y;
        d.panner.positionZ.value = d.z;
      } else d.panner.setPosition(d.x, d.y, d.z);
    }

    function startLoop(d) {
      if (d.playing) return;
      if (d.make) {
        d.playing = true;
        d.stop = (d.make(ctx, d.out) || {}).stop || null;
        return;
      }
      if (d.buffer) { playBuffer(d); return; }
      global.fetch(pickUrl(d.url))
        .then(function (r) { return r.arrayBuffer(); })
        .then(function (ab) { return ctx.decodeAudioData(ab); })
        .then(function (buf) {
          d.buffer = buf;
          if (!destroyed && started && d.loop) playBuffer(d);
        })
        .catch(function (err) {
          if (global.console) console.warn('spatial-audio-world: "' + d.id + '" failed to load', err);
        });
    }

    function playBuffer(d) {
      var src = ctx.createBufferSource();
      src.buffer = d.buffer;
      src.loop = d.loop;
      src.connect(d.out);
      src.start();
      d.node = src;
      d.playing = true;
      if (!d.loop) src.onended = function () { d.playing = false; d.node = null; };
    }

    function startWorld() {
      if (started || !ctx) return;
      started = true;
      defs.forEach(function (d) {
        mountSource(d);
        if (d.loop) startLoop(d);
      });
    }

    // Resume ONLY inside a real gesture — every caller below is gated.
    function unlockNow() {
      if (!ensureCtx()) return;
      if (suspendTimer) { clearTimeout(suspendTimer); suspendTimer = 0; }
      var up = function () {
        master.gain.cancelScheduledValues(ctx.currentTime);
        master.gain.setTargetAtTime(1, ctx.currentTime, SWELL / 3);
        startWorld();
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
      if (on) unlockNow(); // the toggle click IS the gesture
      else if (ctx) {
        master.gain.cancelScheduledValues(ctx.currentTime);
        master.gain.setTargetAtTime(0, ctx.currentTime, MUTE_RAMP / 3);
        suspendTimer = setTimeout(function () {
          suspendTimer = 0;
          if (!on && ctx && ctx.state === 'running') ctx.suspend();
        }, MUTE_RAMP * 1000 + 100);
      }
    }

    // The start gate's half of the law: called INSIDE the gate's gesture.
    // Calm signals (reduced-motion, Save-Data, a persisted mute) keep the
    // world silent — only the visitor's own toggle click overrides them.
    function unlock() {
      if (reduce() || saveData()) return;
      if (store(key) === '0') return; // the persisted mute is honored
      on = true;
      store(key, '1');
      reflect();
      unlockNow();
    }

    var onVis = function () {
      if (!ctx) return;
      if (document.hidden) {
        if (ctx.state === 'running') ctx.suspend();
      } else if (on && ctx.state === 'suspended') {
        ctx.resume().then(function () {}, function () {});
      }
    };
    document.addEventListener('visibilitychange', onVis);
    var onToggle = function () { toggle(); };
    btn.addEventListener('click', onToggle);

    var handle = {
      unlock: unlock,
      toggle: toggle,
      setListener: function (x, y, z, fx, fy, fz) {
        listenerPos = [+x || 0, +y || 0, +z || 0];
        if (fx != null) listenerFwd = [+fx, +fy || 0, +fz];
        applyListener();
      },
      setSource: function (id, x, y, z) {
        defs.forEach(function (d) {
          if (d.id !== id) return;
          d.x = +x || 0; d.y = +y || 0; d.z = +z || 0;
          placeSource(d);
        });
      },
      setSourceGain: function (id, g, ramp) {
        defs.forEach(function (d) {
          if (d.id !== id) return;
          d.gain = +g || 0;
          if (d.out && ctx) d.out.gain.setTargetAtTime(d.gain, ctx.currentTime, (ramp || 0.5) / 3);
        });
      },
      play: function (id) {
        if (!started || !ctx || ctx.state !== 'running') return; // silent no-op
        defs.forEach(function (d) {
          if (d.id !== id || d.loop) return;
          mountSource(d);
          if (d.buffer) playBuffer(d);
          else if (d.make) { d.make(ctx, d.out); }
          else startLoop(d);
        });
      },
      getState: function () {
        return {
          on: on,
          context: ctx ? ctx.state : 'none',
          level: rms(analyser),
          left: rms(aL),
          right: rms(aR),
          listener: listenerPos.slice(),
          sources: defs.map(function (d) {
            return { id: d.id, x: d.x, y: d.y, z: d.z, playing: d.playing };
          })
        };
      },
      destroy: function () {
        destroyed = true;
        document.removeEventListener('visibilitychange', onVis);
        btn.removeEventListener('click', onToggle);
        if (suspendTimer) { clearTimeout(suspendTimer); suspendTimer = 0; }
        defs.forEach(function (d) {
          if (d.stop) { try { d.stop(); } catch (e) {} }
          if (d.node) { try { d.node.stop(); } catch (e) {} }
        });
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

  global.awardSpatialAudioWorld = { init: init };
})(typeof window !== 'undefined' ? window : this);
