/*
 * scroll-velocity-scene-distortion — the scene's momentum made visible
 * (evidence: Lusion v3 — Dev SOTY 2023, animations 10.00, ships a public
 * WebGL scroll driver; Codrops 'Distortion and Grain Effects on Scroll with
 * Shaders in Three.js' 2024-07-18; Awwwards' WebGL-scroll-distortion
 * collections. EVIDENCE CAVEAT, carried from the gap verbatim: attribution
 * to a single winner-verified shipped read is SOFT — this is a DOCUMENTED
 * TECHNIQUE, not a measured winner spec, and every number here is a
 * default). Whole-scene distortion driven by scroll/scrub SPEED: each frame
 * the scroll velocity is smoothed and fed to the shader as one signed
 * uniform; the scene plate warps — a jelly bulge that lags the motion, a
 * stretch along the scroll axis, an RGB split proportional to speed —
 * and decays back to the composed rest when scrolling stops. On a journey
 * stack where the wheel drives the camera and NO native scroll exists,
 * handle.feed(position) drives the same signal from the virtual scrub
 * (journey-touch-momentum's onProgress is the intended feeder) — there this
 * channel is what renders momentum perceptible.
 * Ruled DISTINCT + COMPANION to scroll-speed-oscillator: the oscillator is
 * the DOM-TRANSFORM half of the velocity transfer (skewY + stretch on a
 * promoted layer — its own header delegates 'the RGB-shift expression of
 * the same signal' to WebGL); this component IS that delegated half —
 * per-pixel displacement + channel split IN the scene texture, which no
 * compositor transform can express. Same input, different substrate: a
 * build picks ONE spelling per surface, never both on one element.
 *
 * Discipline (binding): raw WebGL, zero deps; DPR capped at 2; the rAF
 * loop arms on scroll/feed and parks cold once the smoothed velocity and
 * the displayed amplitude settle; IntersectionObserver gates each plate
 * off-screen and visibilitychange parks a hidden tab. Context loss drops
 * the canvas and the plain <img> stands (the static fallback), remounting
 * on restore; a tainted plate falls back the same way. NOT pointer-gated:
 * scroll is the input, so the channel stays live on touch.
 * prefers-reduced-motion: fully dormant — nothing mounts, the authored
 * plate never distorts (static under reduce is the gap's own order).
 * No-JS / no-WebGL: the plain figure.
 *
 * Expected markup:
 *   <figure data-ad-scene-distort>
 *     <img src="plate.jpg" alt="…">
 *   </figure>
 *
 * Usage:  awardScrollVelocitySceneDistortion.init(root, opts)
 *   root      Element|Document  scope (default document)
 *   selector  string  plates (default '[data-ad-scene-distort]')
 *   amp       number  distortion amplitude at full speed (default 0.12)
 *   fullSpeed px/s    scroll speed mapping to |u_vel| = 1 (default 2400)
 * Returns { feed(pos), getState(), destroy() }.
 *   feed(pos)   drive the signal from a virtual scrub position (journey
 *               stacks — px or any monotonic unit; velocity is derived)
 *   getState()  { vel, units: [{ live, running }] } — the drive readout.
 * Idempotent per plate. destroy() tears down GL, listeners, observers and
 * the stylesheet.
 *
 * Tokens: none read directly — the distortion re-renders the plate's own
 * pixels.
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-scene-distort-css';
  var SMOOTH = 0.12;      // velocity low-pass per frame
  var PARK = 0.0015;      // |vel| floor that parks the loop
  var reduce = function () {
    return !!(global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches);
  };

  var VERT =
    'attribute vec2 p;varying vec2 v_uv;' +
    'void main(){v_uv=p*.5+.5;gl_Position=vec4(p,0.,1.);}';

  // the momentum grammar: center-lag bulge + axis stretch + channel split
  var FRAG =
    'precision mediump float;varying vec2 v_uv;\n' +
    'uniform sampler2D u_tex;uniform vec2 u_res;uniform vec2 u_texres;\n' +
    'uniform float u_vel;uniform float u_amp;\n' +
    'vec2 cover(vec2 uv){\n' +
    ' float ra=u_res.x/u_res.y;float ta=u_texres.x/u_texres.y;\n' +
    ' vec2 t=uv-.5;if(ra>ta)t.y*=ta/ra;else t.x*=ra/ta;return t+.5;\n' +
    '}\n' +
    'void main(){\n' +
    ' vec2 uv=vec2(v_uv.x,1.-v_uv.y);\n' +
    ' float b=u_vel*u_amp;\n' +
    // the jelly bulge: the row center lags the edges, signed by direction
    ' uv.y+=b*sin(3.14159*uv.x)*.55;\n' +
    // stretch along the scroll axis
    ' uv.y=(uv.y-.5)*(1.-abs(b)*.35)+.5;\n' +
    ' vec2 t=cover(uv);\n' +
    ' vec2 split=vec2(0.,b*.045);\n' +
    ' float r=texture2D(u_tex,t+split).r;\n' +
    ' float g=texture2D(u_tex,t).g;\n' +
    ' float bl=texture2D(u_tex,t-split).b;\n' +
    ' gl_FragColor=vec4(r,g,bl,1.);\n' +
    '}';

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      '.ad-sdist{position:relative;overflow:clip;margin:0;}' +
      '.ad-sdist img{display:block;width:100%;}' +
      '.ad-sdist canvas.ad-sdist__c{position:absolute;inset:0;' +
        'width:100%;height:100%;pointer-events:none;}' +
      '.ad-sdist--gl img{visibility:hidden;}';
    document.head.appendChild(s);
  }

  function compile(gl, vsrc, fsrc) {
    var prog = gl.createProgram();
    [[gl.VERTEX_SHADER, vsrc], [gl.FRAGMENT_SHADER, fsrc]].forEach(function (sh) {
      var o = gl.createShader(sh[0]);
      gl.shaderSource(o, sh[1]);
      gl.compileShader(o);
      gl.attachShader(prog, o);
    });
    gl.linkProgram(prog);
    return gl.getProgramParameter(prog, gl.LINK_STATUS) ? prog : null;
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-scene-distort]';
    var AMP = opts.amp != null ? +opts.amp : 0.12;
    var FULL = opts.fullSpeed != null ? +opts.fullSpeed : 2400;

    // reduced-motion: the authored plate stands still — dormant.
    if (reduce()) {
      return { feed: function () {}, getState: function () { return { vel: 0, units: [] }; },
               destroy: function () {} };
    }

    injectCss();
    var units = [];
    // ONE velocity for the page — every plate rides the same momentum
    var vel = 0;            // smoothed, -1..1
    var lastPos = null;     // px (native scroll or fed scrub)
    var lastT = 0;
    var fedPos = null;      // non-null once feed() drives the signal
    var pending = 0;        // px moved since the last frame

    function onScroll() {
      if (fedPos == null) {
        var y = global.pageYOffset || 0;
        if (lastPos != null) pending += y - lastPos;
        lastPos = y;
        armAll();
      }
    }

    function makeUnit(fig) {
      if (fig.__adSceneDistort) return;
      fig.__adSceneDistort = true;
      var img = fig.querySelector('img');
      if (!img) { delete fig.__adSceneDistort; return; }
      fig.classList.add('ad-sdist');

      var unit = { fig: fig, img: img, gl: null, canvas: null, live: false,
                   raf: 0, onScreen: true, u: {}, io: null, listeners: [] };

      function mount() {
        var canvas = document.createElement('canvas');
        canvas.className = 'ad-sdist__c';
        canvas.setAttribute('aria-hidden', 'true');
        var gl = canvas.getContext('webgl', { alpha: false, antialias: false, powerPreference: 'low-power' });
        if (!gl) return false;
        var prog = compile(gl, VERT, FRAG);
        if (!prog) return false;
        gl.useProgram(prog);
        var buf = gl.createBuffer();
        gl.bindBuffer(gl.ARRAY_BUFFER, buf);
        gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
        var loc = gl.getAttribLocation(prog, 'p');
        gl.enableVertexAttribArray(loc);
        gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
        var tex = gl.createTexture();
        gl.bindTexture(gl.TEXTURE_2D, tex);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
        try {
          gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGB, gl.RGB, gl.UNSIGNED_BYTE, img);
        } catch (err) { return false; } // tainted plate → the figure stands
        ['u_tex', 'u_res', 'u_texres', 'u_vel', 'u_amp'].forEach(function (n) {
          unit.u[n] = gl.getUniformLocation(prog, n);
        });
        gl.uniform1i(unit.u.u_tex, 0);
        gl.uniform2f(unit.u.u_texres, img.naturalWidth, img.naturalHeight);
        gl.uniform1f(unit.u.u_amp, AMP);
        fig.appendChild(canvas);
        fig.classList.add('ad-sdist--gl');
        unit.gl = gl;
        unit.canvas = canvas;
        unit.live = true;
        unit.onLost = function (e) { e.preventDefault(); teardownGl(); };
        unit.onRestored = function () { if (!unit.live) mount(); };
        canvas.addEventListener('webglcontextlost', unit.onLost);
        canvas.addEventListener('webglcontextrestored', unit.onRestored);
        size();
        draw();
        return true;
      }

      function teardownGl() {
        unit.live = false;
        if (unit.raf) { global.cancelAnimationFrame(unit.raf); unit.raf = 0; }
        if (unit.canvas && unit.canvas.parentNode) unit.canvas.parentNode.removeChild(unit.canvas);
        fig.classList.remove('ad-sdist--gl');
        unit.gl = null;
      }

      function size() {
        var dpr = Math.min(2, global.devicePixelRatio || 1);
        var w = Math.max(1, Math.round(fig.clientWidth * dpr));
        var h = Math.max(1, Math.round(fig.clientHeight * dpr));
        if (unit.canvas.width !== w || unit.canvas.height !== h) {
          unit.canvas.width = w;
          unit.canvas.height = h;
        }
      }

      function draw() {
        var gl = unit.gl;
        if (!gl) return;
        size();
        gl.viewport(0, 0, unit.canvas.width, unit.canvas.height);
        gl.uniform2f(unit.u.u_res, unit.canvas.width, unit.canvas.height);
        gl.uniform1f(unit.u.u_vel, vel);
        gl.drawArrays(gl.TRIANGLES, 0, 3);
      }

      function frame(now) {
        unit.raf = 0;
        if (!unit.live || !unit.onScreen || document.hidden) return;
        // one plate integrates the shared signal per frame (the first to run)
        integrate(now);
        draw();
        if (Math.abs(vel) > PARK || pending !== 0) {
          unit.raf = global.requestAnimationFrame(frame);
        } else { vel = 0; draw(); } // settle to the exact rest, park cold
      }

      unit.arm = function () {
        if (!unit.raf && unit.live && unit.onScreen && !document.hidden) {
          unit.raf = global.requestAnimationFrame(frame);
        }
      };
      unit.teardownGl = teardownGl;

      if ('IntersectionObserver' in global) {
        unit.io = new IntersectionObserver(function (entries) {
          unit.onScreen = entries[0].isIntersecting;
          if (unit.onScreen) unit.arm();
          else if (unit.raf) { global.cancelAnimationFrame(unit.raf); unit.raf = 0; }
        });
        unit.io.observe(fig);
      }

      var wire = function () { if (!mount()) delete fig.__adSceneDistort; };
      if (img.complete && img.naturalWidth) wire();
      else {
        img.addEventListener('load', wire, { once: true });
        unit.listeners.push([img, 'load', wire, { once: true }]);
      }
      units.push(unit);
    }

    var integratedAt = 0;
    function integrate(now) {
      if (now === integratedAt) return; // one integration per frame across plates
      integratedAt = now;
      if (!lastT) lastT = now;
      var dt = Math.max(1, now - lastT) / 1000;
      lastT = now;
      var raw = Math.max(-1, Math.min(1, (pending / dt) / FULL));
      pending = 0;
      vel += (raw - vel) * (SMOOTH * Math.min(4, dt * 60));
    }

    function armAll() {
      units.forEach(function (u) { u.arm(); });
    }

    Array.prototype.slice.call(root.querySelectorAll(selector)).forEach(makeUnit);

    global.addEventListener('scroll', onScroll, { passive: true });
    var onVis = function () { if (!document.hidden) armAll(); };
    document.addEventListener('visibilitychange', onVis);

    return {
      feed: function (pos) {
        pos = +pos || 0;
        if (fedPos != null) pending += pos - fedPos;
        fedPos = pos;
        armAll();
      },
      getState: function () {
        return { vel: +vel.toFixed(4),
                 units: units.map(function (u) { return { live: u.live, running: !!u.raf }; }) };
      },
      destroy: function () {
        global.removeEventListener('scroll', onScroll);
        document.removeEventListener('visibilitychange', onVis);
        units.forEach(function (u) {
          if (u.io) u.io.disconnect();
          u.listeners.forEach(function (l) { l[0].removeEventListener(l[1], l[2], l[3]); });
          if (u.canvas) {
            u.canvas.removeEventListener('webglcontextlost', u.onLost);
            u.canvas.removeEventListener('webglcontextrestored', u.onRestored);
          }
          if (u.gl) {
            var ext = u.gl.getExtension('WEBGL_lose_context');
            if (ext) ext.loseContext();
          }
          u.teardownGl();
          u.fig.classList.remove('ad-sdist', 'ad-sdist--gl');
          delete u.fig.__adSceneDistort;
        });
        units = [];
        var s = document.getElementById(CSS_ID);
        if (s && s.parentNode) s.parentNode.removeChild(s);
      }
    };
  }

  global.awardScrollVelocitySceneDistortion = { init: init };
})(typeof window !== 'undefined' ? window : this);
