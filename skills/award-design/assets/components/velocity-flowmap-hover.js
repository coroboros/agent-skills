/*
 * velocity-flowmap-hover — the chromatic-velocity figure response (winners:
 * Igloo Inc + Active Theory carry the chromatic-hover family; the exact
 * recipe is the Guignand/Codrops technique — single-source, award-UNVERIFIED
 * numbers, carried as defaults and flagged so). Image hover that reacts to
 * cursor SPEED, not just position: each frame the cursor's velocity is
 * splatted into an off-screen RG FLOWMAP texture that decays over time
 * (ping-pong framebuffers), so a fast sweep leaves a directional trail that
 * PERSISTS after the pointer has gone and dies down on its own; the image
 * shader then offsets/splits the RGB channels along the mouse->pixel vector
 * proportional to the local flowmap strength — R x1.5, G x0.5, B x1.8 —
 * tipping into a rainbow fringe once the smoothed velocity crosses
 * uVelo > 0.01 (all four numbers are the carried Codrops read, not law).
 * Ruled DISTINCT from figure-hover (a contained 1.1 zoom + companion cue —
 * its own header names this as the generative-canvas response it cannot
 * execute) and from liquid-glass-refraction (a STILL SVG-displacement
 * material with zero per-frame work — no velocity, no memory); this is the
 * canvas/WebGL PERSISTENCE variant: a time-decaying velocity field the
 * cursor writes and the shader reads.
 *
 * Discipline (binding): raw WebGL, zero deps; render canvas DPR capped at
 * 2, the sim runs at a fixed 128px flowmap; the rAF loop runs only while
 * the pointer is over the figure OR trail energy remains — a decayed field
 * parks the loop cold; IntersectionObserver + visibilitychange gate it
 * off-screen/hidden. Context loss is handled: the canvas drops and the
 * plain <img> stands (the static fallback), remounting on restore. The
 * canvas is aria-hidden and pointer-events:none — the img keeps its alt
 * and its place in the a11y tree.
 * Fine pointers only — dormant on touch (a coarse pointer has no cursor
 * velocity; the figure rests as the plain image, per the gap's own order).
 * prefers-reduced-motion: fully dormant — a static frame, the authored
 * <img>, nothing mounted, nothing animates. No-JS / no-WebGL: the plain
 * figure.
 *
 * Expected markup:
 *   <figure data-ad-flowmap>
 *     <img src="plate.jpg" alt="…">
 *   </figure>
 *
 * Usage:  awardVelocityFlowmapHover.init(root, opts)
 *   root      Element|Document  scope (default document)
 *   selector  string  figures (default '[data-ad-flowmap]')
 *   amp       number  offset amplitude in uv (default 0.035)
 * Returns { getState(), sampleFlow(i, u, v), destroy() }.
 *   getState()          [{ live, running, energy, velo }] per figure — the
 *                       drive/test readout.
 *   sampleFlow(i, u, v) reads the live flowmap texel at uv (0-1, v up) →
 *                       { fx, fy } in -1..1 — the trail, measured.
 * Idempotent per figure. destroy() tears down GL, canvases, listeners,
 * observers and the stylesheet.
 *
 * Tokens: none read directly — the trail recolors the figure's own pixels.
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-velocity-flowmap-css';
  var SIM = 128;          // flowmap side — the field, not the image
  var DECAY = 0.955;      // per-frame trail decay
  var PARK_E = 0.004;     // energy floor that parks the loop
  var VELO_TIP = 0.01;    // the carried Codrops rainbow threshold
  var reduce = function () {
    return !!(global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches);
  };
  var finePointer = function () {
    return !!(global.matchMedia && global.matchMedia('(hover: hover) and (pointer: fine)').matches);
  };

  var VERT =
    'attribute vec2 p;varying vec2 v_uv;' +
    'void main(){v_uv=p*.5+.5;gl_Position=vec4(p,0.,1.);}';

  // splat + decay: the cursor's frame velocity written into the RG field
  var SIM_FRAG =
    'precision mediump float;varying vec2 v_uv;\n' +
    'uniform sampler2D u_prev;uniform vec2 u_mouse;uniform vec2 u_vel;\n' +
    'uniform float u_decay;uniform float u_aspect;\n' +
    'void main(){\n' +
    ' vec2 flow=(texture2D(u_prev,v_uv).rg-.5)*u_decay;\n' +
    ' vec2 d=v_uv-u_mouse;d.x*=u_aspect;\n' +
    ' flow+=u_vel*exp(-dot(d,d)/.006);\n' +
    ' flow=clamp(flow,vec2(-.5),vec2(.5));\n' +
    ' gl_FragColor=vec4(flow+.5,0.,1.);\n' +
    '}';

  // the split: RGB offset along the mouse->pixel vector, scaled by the local
  // flowmap strength; rainbow fringe above the velocity tip
  var DRAW_FRAG =
    'precision mediump float;varying vec2 v_uv;\n' +
    'uniform sampler2D u_tex;uniform sampler2D u_flow;\n' +
    'uniform vec2 u_res;uniform vec2 u_texres;uniform vec2 u_mouse;\n' +
    'uniform float u_velo;uniform float u_amp;\n' +
    'vec2 cover(vec2 uv){\n' +
    ' float ra=u_res.x/u_res.y;float ta=u_texres.x/u_texres.y;\n' +
    ' vec2 t=uv-.5;if(ra>ta)t.y*=ta/ra;else t.x*=ra/ta;return t+.5;\n' +
    '}\n' +
    'void main(){\n' +
    ' vec2 uv=vec2(v_uv.x,1.-v_uv.y);\n' +
    ' vec2 flow=(texture2D(u_flow,vec2(uv.x,1.-uv.y)).rg-.5)*2.;\n' +
    ' float m=length(flow);\n' +
    ' vec2 dir=uv-u_mouse;\n' +
    ' dir=length(dir)>.001?normalize(dir):vec2(0.);\n' +
    ' vec2 off=dir*m*u_amp;\n' +
    ' vec2 t=cover(uv);\n' +
    ' float r=texture2D(u_tex,t-off*1.5).r;\n' +
    ' float g=texture2D(u_tex,t-off*.5).g;\n' +
    ' float b=texture2D(u_tex,t-off*1.8).b;\n' +
    ' vec3 col=vec3(r,g,b);\n' +
    ' float tip=smoothstep(' + VELO_TIP + ',' + (VELO_TIP * 5) + ',u_velo)*m;\n' +
    ' if(tip>0.){\n' +
    '  vec2 perp=vec2(-dir.y,dir.x)*m*u_amp;\n' +
    '  vec3 fr=vec3(texture2D(u_tex,t-off*2.2+perp).r,\n' +
    '               texture2D(u_tex,t-off*1.+perp*.5).g,\n' +
    '               texture2D(u_tex,t-off*2.6-perp).b);\n' +
    '  col=mix(col,fr,tip*.75);\n' +
    ' }\n' +
    ' gl_FragColor=vec4(col,1.);\n' +
    '}';

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      '.ad-flowmap{position:relative;overflow:clip;margin:0;}' +
      '.ad-flowmap img{display:block;width:100%;}' +
      '.ad-flowmap canvas.ad-flowmap__c{position:absolute;inset:0;' +
        'width:100%;height:100%;pointer-events:none;}' +
      '.ad-flowmap--gl img{visibility:hidden;}';
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
    var selector = opts.selector || '[data-ad-flowmap]';
    var AMP = opts.amp != null ? +opts.amp : 0.035;

    // reduced-motion OR coarse pointer: the plain figure IS the state
    if (reduce() || !finePointer()) {
      return { getState: function () { return []; },
               sampleFlow: function () { return null; },
               destroy: function () {} };
    }

    injectCss();
    var units = [];

    function makeUnit(fig) {
      if (fig.__adFlowmap) return;
      fig.__adFlowmap = true;
      var img = fig.querySelector('img');
      if (!img) { delete fig.__adFlowmap; return; }
      fig.classList.add('ad-flowmap');

      var unit = {
        fig: fig, img: img, gl: null, canvas: null, live: false,
        raf: 0, onScreen: true, inside: false, energy: 0, velo: 0,
        mouse: [0.5, 0.5], vel: [0, 0], lastP: null,
        sims: null, simIdx: 0, progSim: null, progDraw: null,
        uS: {}, uD: {}, io: null, listeners: []
      };

      function mount() {
        var canvas = document.createElement('canvas');
        canvas.className = 'ad-flowmap__c';
        canvas.setAttribute('aria-hidden', 'true');
        var gl = canvas.getContext('webgl', { alpha: false, antialias: false, powerPreference: 'low-power' });
        if (!gl) return false;
        unit.progSim = compile(gl, VERT, SIM_FRAG);
        unit.progDraw = compile(gl, VERT, DRAW_FRAG);
        if (!unit.progSim || !unit.progDraw) return false;
        var buf = gl.createBuffer();
        gl.bindBuffer(gl.ARRAY_BUFFER, buf);
        gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
        [unit.progSim, unit.progDraw].forEach(function (prog) {
          gl.useProgram(prog);
          var loc = gl.getAttribLocation(prog, 'p');
          gl.enableVertexAttribArray(loc);
          gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
        });
        function tex2d(w, h, data) {
          var t = gl.createTexture();
          gl.bindTexture(gl.TEXTURE_2D, t);
          gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
          gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
          gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
          gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
          gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, w, h, 0, gl.RGBA, gl.UNSIGNED_BYTE, data);
          return t;
        }
        // the ping-pong flowmap pair, primed to the zero field (0.5 center)
        var zero = new Uint8Array(SIM * SIM * 4);
        for (var i = 0; i < zero.length; i += 4) { zero[i] = 128; zero[i + 1] = 128; zero[i + 3] = 255; }
        unit.sims = [0, 1].map(function () {
          var t = tex2d(SIM, SIM, zero);
          var f = gl.createFramebuffer();
          gl.bindFramebuffer(gl.FRAMEBUFFER, f);
          gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, t, 0);
          return { tex: t, fbo: f };
        });
        gl.bindFramebuffer(gl.FRAMEBUFFER, null);
        var imgTex = gl.createTexture();
        gl.bindTexture(gl.TEXTURE_2D, imgTex);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
        // a tainted plate (cross-origin, no CORS header) throws here — the
        // plain figure stands instead of an exception
        try {
          gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGB, gl.RGB, gl.UNSIGNED_BYTE, img);
        } catch (err) { return false; }
        unit.imgTex = imgTex;
        ['u_prev', 'u_mouse', 'u_vel', 'u_decay', 'u_aspect'].forEach(function (n) {
          unit.uS[n] = gl.getUniformLocation(unit.progSim, n);
        });
        ['u_tex', 'u_flow', 'u_res', 'u_texres', 'u_mouse', 'u_velo', 'u_amp'].forEach(function (n) {
          unit.uD[n] = gl.getUniformLocation(unit.progDraw, n);
        });
        fig.appendChild(canvas);
        fig.classList.add('ad-flowmap--gl');
        unit.gl = gl;
        unit.canvas = canvas;
        unit.live = true;
        // context loss: the plain img stands; restore remounts clean
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
        fig.classList.remove('ad-flowmap--gl');
        unit.gl = null;
        unit.energy = 0;
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
        // sim pass: prev → next with decay + this frame's splat
        var prev = unit.sims[unit.simIdx], next = unit.sims[1 - unit.simIdx];
        gl.useProgram(unit.progSim);
        gl.bindFramebuffer(gl.FRAMEBUFFER, next.fbo);
        gl.viewport(0, 0, SIM, SIM);
        gl.activeTexture(gl.TEXTURE0);
        gl.bindTexture(gl.TEXTURE_2D, prev.tex);
        gl.uniform1i(unit.uS.u_prev, 0);
        gl.uniform2f(unit.uS.u_mouse, unit.mouse[0], 1 - unit.mouse[1]);
        gl.uniform2f(unit.uS.u_vel, unit.vel[0], -unit.vel[1]);
        gl.uniform1f(unit.uS.u_decay, DECAY);
        gl.uniform1f(unit.uS.u_aspect, fig.clientWidth / Math.max(1, fig.clientHeight));
        gl.drawArrays(gl.TRIANGLES, 0, 3);
        unit.simIdx = 1 - unit.simIdx;
        // draw pass: the image split by the field
        gl.bindFramebuffer(gl.FRAMEBUFFER, null);
        gl.viewport(0, 0, unit.canvas.width, unit.canvas.height);
        gl.useProgram(unit.progDraw);
        gl.activeTexture(gl.TEXTURE0);
        gl.bindTexture(gl.TEXTURE_2D, unit.imgTex);
        gl.uniform1i(unit.uD.u_tex, 0);
        gl.activeTexture(gl.TEXTURE1);
        gl.bindTexture(gl.TEXTURE_2D, unit.sims[unit.simIdx].tex);
        gl.uniform1i(unit.uD.u_flow, 1);
        gl.uniform2f(unit.uD.u_res, unit.canvas.width, unit.canvas.height);
        gl.uniform2f(unit.uD.u_texres, img.naturalWidth, img.naturalHeight);
        gl.uniform2f(unit.uD.u_mouse, unit.mouse[0], unit.mouse[1]);
        gl.uniform1f(unit.uD.u_velo, unit.velo);
        gl.uniform1f(unit.uD.u_amp, AMP);
        gl.drawArrays(gl.TRIANGLES, 0, 3);
      }

      function frame() {
        unit.raf = 0;
        if (!unit.live || !unit.onScreen || document.hidden) return;
        draw();
        // the trail bookkeeping mirrors the shader decay: splat, then die
        unit.energy = Math.max(unit.energy * DECAY, Math.hypot(unit.vel[0], unit.vel[1]));
        unit.velo *= 0.92;
        unit.vel = [0, 0]; // a still pointer splats nothing next frame
        if (unit.inside || unit.energy > PARK_E) {
          unit.raf = global.requestAnimationFrame(frame);
        } // else: decayed and left — the loop parks cold
      }

      function arm() {
        if (!unit.raf && unit.live && unit.onScreen && !document.hidden) {
          unit.raf = global.requestAnimationFrame(frame);
        }
      }

      function on(el, ev, fn, o) {
        el.addEventListener(ev, fn, o);
        unit.listeners.push([el, ev, fn, o]);
      }

      on(fig, 'pointerenter', function (e) {
        if (e.pointerType === 'touch') return;
        unit.inside = true;
        unit.lastP = null;
        arm();
      });
      on(fig, 'pointermove', function (e) {
        if (e.pointerType === 'touch' || !unit.live) return;
        var r = fig.getBoundingClientRect();
        var u = (e.clientX - r.left) / Math.max(1, r.width);
        var v = (e.clientY - r.top) / Math.max(1, r.height);
        unit.mouse = [u, v];
        if (unit.lastP) {
          var dx = u - unit.lastP[0], dy = v - unit.lastP[1];
          unit.vel = [Math.max(-0.5, Math.min(0.5, dx * 1.4)),
                      Math.max(-0.5, Math.min(0.5, dy * 1.4))];
          unit.velo = Math.min(0.3, unit.velo + Math.hypot(dx, dy) * 0.5);
        }
        unit.lastP = [u, v];
        arm();
      });
      on(fig, 'pointerleave', function (e) {
        if (e.pointerType === 'touch') return;
        unit.inside = false;
        unit.lastP = null;
      });

      if ('IntersectionObserver' in global) {
        unit.io = new IntersectionObserver(function (entries) {
          unit.onScreen = entries[0].isIntersecting;
          if (unit.onScreen) arm(); else if (unit.raf) {
            global.cancelAnimationFrame(unit.raf);
            unit.raf = 0;
          }
        });
        unit.io.observe(fig);
      }
      unit.arm = arm;
      unit.teardownGl = teardownGl;

      var wire = function () { if (!mount()) delete fig.__adFlowmap; };
      if (img.complete && img.naturalWidth) wire();
      else on(img, 'load', wire, { once: true });

      units.push(unit);
    }

    Array.prototype.slice.call(root.querySelectorAll(selector)).forEach(makeUnit);

    var onVis = function () {
      if (!document.hidden) units.forEach(function (u) { u.arm(); });
    };
    document.addEventListener('visibilitychange', onVis);

    return {
      getState: function () {
        return units.map(function (u) {
          return { live: u.live, running: !!u.raf,
                   energy: +u.energy.toFixed(4), velo: +u.velo.toFixed(4) };
        });
      },
      sampleFlow: function (i, u, v) {
        var unit = units[i];
        if (!unit || !unit.gl) return null;
        var gl = unit.gl;
        gl.bindFramebuffer(gl.FRAMEBUFFER, unit.sims[unit.simIdx].fbo);
        var px = new Uint8Array(4);
        gl.readPixels(Math.round(u * (SIM - 1)), Math.round(v * (SIM - 1)),
                      1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px);
        gl.bindFramebuffer(gl.FRAMEBUFFER, null);
        return { fx: +((px[0] - 128) / 127).toFixed(3), fy: +((px[1] - 128) / 127).toFixed(3) };
      },
      destroy: function () {
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
          u.fig.classList.remove('ad-flowmap', 'ad-flowmap--gl');
          delete u.fig.__adFlowmap;
        });
        units = [];
        var s = document.getElementById(CSS_ID);
        if (s && s.parentNode) s.parentNode.removeChild(s);
      }
    };
  }

  global.awardVelocityFlowmapHover = { init: init };
})(typeof window !== 'undefined' ? window : this);
