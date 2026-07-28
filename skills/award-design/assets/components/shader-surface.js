/*
 * shader-surface — token-driven WebGL texture layer (winner: Siena Film Foundation
 * runs an OGL canvas; technique canon in ingredients/ogl-shaders.md).
 * A single full-quad fragment shader painted from the build's DESIGN.md tokens —
 * the craft-archetype spectacle tier: a living ground, never the hero. Modes:
 *   gradient-mesh — domain-warped flowing gradient between ground, ground-2 and
 *                   an accent-tinted highlight (the "living poster" ground)
 *   noise-field   — quiet monochrome fbm field in ink at low alpha
 *   ripple        — gradient-mesh plus a pointer-driven displacement ring that
 *                   swells on movement and decays at rest
 * Discipline (binding): raw WebGL, zero deps; DPR capped at 2; the rAF loop runs
 * only while the surface is on-screen (IntersectionObserver) and the tab visible;
 * reduced-motion renders ONE static frame; no WebGL → a CSS token-gradient
 * fallback paints the container; the canvas is aria-hidden, pointer-events:none,
 * and never the LCP element (mount behind real DOM content).
 *
 * Usage:  awardShaderSurface.init(root, { selector, mode, speed, alpha })
 *   selector  string  mount containers (default '[data-ad-shader]'; per-element
 *                     mode via the attribute value, e.g. data-ad-shader="ripple")
 *   mode      string  'gradient-mesh' | 'noise-field' | 'ripple' (default 'gradient-mesh')
 *   speed     number  time multiplier (default 1)
 *   alpha     number  canvas opacity (default 1; noise-field draws ~0.08 internally)
 * Returns { destroy() }. Idempotent per container.
 *
 * Tokens: --ad-ground, --ad-ground-2, --ad-accent, --ad-ink.
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-shader-surface-css';
  var reduce = function () {
    return global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches;
  };
  var MODES = { 'gradient-mesh': 0, 'noise-field': 1, ripple: 2 };

  var VERT =
    'attribute vec2 p;void main(){gl_Position=vec4(p,0.,1.);}';
  var FRAG =
    'precision mediump float;\n' +
    'uniform vec2 u_res;uniform float u_time;uniform int u_mode;\n' +
    'uniform vec3 u_ground;uniform vec3 u_ground2;uniform vec3 u_accent;uniform vec3 u_ink;\n' +
    'uniform vec2 u_pointer;uniform float u_strength;\n' +
    'float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453123);}\n' +
    'float noise(vec2 p){vec2 i=floor(p);vec2 f=fract(p);f=f*f*(3.-2.*f);\n' +
    ' return mix(mix(hash(i),hash(i+vec2(1.,0.)),f.x),mix(hash(i+vec2(0.,1.)),hash(i+vec2(1.,1.)),f.x),f.y);}\n' +
    'float fbm(vec2 p){float v=0.;float a=.5;for(int i=0;i<4;i++){v+=a*noise(p);p*=2.03;a*=.5;}return v;}\n' +
    'void main(){\n' +
    // .14 makes the drift legible within a couple of seconds of looking — an
    // ambient ground that only changes over minutes reads as a static gradient.
    ' vec2 uv=gl_FragCoord.xy/u_res;vec2 st=uv*vec2(u_res.x/u_res.y,1.);\n' +
    ' float t=u_time*.14;\n' +
    ' if(u_mode==1){\n' +
    '  float n=fbm(st*3.+t);\n' +
    '  gl_FragColor=vec4(u_ink,n*.08);return;\n' +
    ' }\n' +
    ' vec2 q=vec2(fbm(st+t),fbm(st+vec2(5.2,1.3)-t));\n' +
    ' vec2 warp=st+1.6*q;\n' +
    ' float dist=0.;\n' +
    ' if(u_mode==2&&u_strength>.001){\n' +
    '  vec2 d=uv-u_pointer;dist=length(d*vec2(u_res.x/u_res.y,1.));\n' +
    '  float ring=sin(dist*22.-u_time*2.5)*exp(-dist*4.);\n' +
    '  warp+=normalize(d+.0001)*ring*u_strength*.6;\n' +
    ' }\n' +
    ' float n=fbm(warp);\n' +
    ' vec3 col=mix(u_ground,u_ground2,smoothstep(.25,.65,n));\n' +
    ' col=mix(col,u_accent,smoothstep(.68,.98,n)*.3);\n' +
    // the felt half of the ripple: a local accent lift riding the ring, so the
    // pointer visibly ignites the ground instead of only warping near-blacks
    ' if(u_mode==2)col=mix(col,u_accent,exp(-dist*6.)*u_strength*.3);\n' +
    ' gl_FragColor=vec4(col,1.);\n' +
    '}';

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      '.ad-shader{position:relative;}' +
      '.ad-shader>canvas.ad-shader__c{position:absolute;inset:0;width:100%;height:100%;' +
      'pointer-events:none;}' +
      // no-WebGL fallback: the token gradient reads as a still of gradient-mesh
      '.ad-shader--fallback{background:linear-gradient(160deg,' +
      'var(--ad-ground,oklch(14% 0.01 260)) 0%,var(--ad-ground-2,oklch(18% 0.01 260)) 55%,' +
      'color-mix(in oklch,var(--ad-accent,oklch(62% 0.2 25)) 18%,var(--ad-ground,oklch(14% 0.01 260))) 100%);}';
    document.head.appendChild(s);
  }

  // Canvas-2D parses any CSS color (including oklch/color-mix) into sRGB bytes —
  // the one robust bridge from token strings to shader uniforms.
  function tokenRGB(probeCtx, el, token, fallback) {
    var v = getComputedStyle(el).getPropertyValue(token).trim() || fallback;
    probeCtx.fillStyle = '#000';
    probeCtx.fillStyle = v;
    probeCtx.clearRect(0, 0, 1, 1);
    probeCtx.fillRect(0, 0, 1, 1);
    var d = probeCtx.getImageData(0, 0, 1, 1).data;
    return [d[0] / 255, d[1] / 255, d[2] / 255];
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-shader]';
    var speed = opts.speed != null ? opts.speed : 1;
    injectCss();

    var mounts = Array.prototype.slice.call(root.querySelectorAll(selector));
    var units = [];
    var probe = document.createElement('canvas');
    probe.width = probe.height = 1;
    var probeCtx = probe.getContext('2d', { willReadFrequently: true });

    function makeUnit(el) {
      if (el.__adShader) return null;
      el.__adShader = true;
      el.classList.add('ad-shader');
      var modeName = opts.mode || (el.getAttribute('data-ad-shader') || '').trim() || 'gradient-mesh';
      var mode = MODES[modeName] != null ? MODES[modeName] : 0;

      var canvas = document.createElement('canvas');
      canvas.className = 'ad-shader__c';
      canvas.setAttribute('aria-hidden', 'true');
      if (opts.alpha != null) canvas.style.opacity = String(opts.alpha);
      var gl = canvas.getContext('webgl', { alpha: true, antialias: false, powerPreference: 'low-power' });
      if (!gl) { el.classList.add('ad-shader--fallback'); return null; }
      el.insertBefore(canvas, el.firstChild);

      var prog = gl.createProgram();
      [[gl.VERTEX_SHADER, VERT], [gl.FRAGMENT_SHADER, FRAG]].forEach(function (s) {
        var sh = gl.createShader(s[0]);
        gl.shaderSource(sh, s[1]);
        gl.compileShader(sh);
        gl.attachShader(prog, sh);
      });
      gl.linkProgram(prog);
      if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) {
        el.removeChild(canvas);
        el.classList.add('ad-shader--fallback');
        return null;
      }
      gl.useProgram(prog);
      var buf = gl.createBuffer();
      gl.bindBuffer(gl.ARRAY_BUFFER, buf);
      gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
      var loc = gl.getAttribLocation(prog, 'p');
      gl.enableVertexAttribArray(loc);
      gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
      gl.enable(gl.BLEND);
      gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);

      var u = {};
      ['u_res', 'u_time', 'u_mode', 'u_ground', 'u_ground2', 'u_accent', 'u_ink', 'u_pointer', 'u_strength']
        .forEach(function (n) { u[n] = gl.getUniformLocation(prog, n); });
      gl.uniform3fv(u.u_ground, tokenRGB(probeCtx, el, '--ad-ground', 'oklch(14% 0.01 260)'));
      gl.uniform3fv(u.u_ground2, tokenRGB(probeCtx, el, '--ad-ground-2', 'oklch(18% 0.01 260)'));
      gl.uniform3fv(u.u_accent, tokenRGB(probeCtx, el, '--ad-accent', 'oklch(62% 0.2 25)'));
      gl.uniform3fv(u.u_ink, tokenRGB(probeCtx, el, '--ad-ink', 'oklch(96% 0 0)'));
      gl.uniform1i(u.u_mode, mode);

      var unit = {
        el: el, canvas: canvas, gl: gl, u: u, mode: mode,
        inView: false, px: 0.5, py: 0.5, strength: 0, onMove: null
      };
      if (mode === 2) {
        unit.onMove = function (e) {
          var r = el.getBoundingClientRect();
          unit.px = (e.clientX - r.left) / Math.max(1, r.width);
          unit.py = 1 - (e.clientY - r.top) / Math.max(1, r.height);
          unit.strength = Math.min(1, unit.strength + 0.25);
        };
        el.addEventListener('pointermove', unit.onMove, { passive: true });
      }
      return unit;
    }

    function size(unit) {
      var dpr = Math.min(2, global.devicePixelRatio || 1);
      var w = Math.round(unit.el.clientWidth * dpr);
      var h = Math.round(unit.el.clientHeight * dpr);
      if (unit.canvas.width !== w || unit.canvas.height !== h) {
        unit.canvas.width = w;
        unit.canvas.height = h;
        unit.gl.viewport(0, 0, w, h);
        unit.gl.uniform2f(unit.u.u_res, w, h);
      }
    }

    function draw(unit, t) {
      size(unit);
      unit.gl.uniform1f(unit.u.u_time, t * speed);
      if (unit.mode === 2) {
        unit.strength *= 0.95;
        unit.gl.uniform2f(unit.u.u_pointer, unit.px, unit.py);
        unit.gl.uniform1f(unit.u.u_strength, unit.strength);
      }
      unit.gl.drawArrays(unit.gl.TRIANGLES, 0, 3);
    }

    var rafId = 0;
    var running = false;
    function frame(now) {
      rafId = 0;
      var any = false;
      units.forEach(function (unit) {
        if (!unit.inView) return;
        any = true;
        draw(unit, now / 1000);
      });
      if (any && running && !document.hidden) rafId = global.requestAnimationFrame(frame);
      else running = false;
    }
    function kick() {
      if (reduce()) return;
      running = true;
      if (!rafId) rafId = global.requestAnimationFrame(frame);
    }

    units = mounts.map(makeUnit).filter(Boolean);

    var io = null, onVis = null;
    if (units.length) {
      if ('IntersectionObserver' in global) {
        io = new IntersectionObserver(function (entries) {
          entries.forEach(function (e) {
            var unit = units.filter(function (x) { return x.el === e.target; })[0];
            if (unit) { unit.inView = e.isIntersecting; if (unit.inView) kick(); }
          });
        }, { threshold: 0 });
        units.forEach(function (unit) { io.observe(unit.el); });
      } else {
        units.forEach(function (unit) { unit.inView = true; });
        kick();
      }
      onVis = function () { if (!document.hidden) kick(); };
      document.addEventListener('visibilitychange', onVis);

      // reduced-motion: one composed still per surface — present, not animated.
      if (reduce()) {
        units.forEach(function (unit) { unit.inView = true; draw(unit, 12.7); unit.inView = false; });
      }
    }

    return {
      destroy: function () {
        running = false;
        if (rafId) global.cancelAnimationFrame(rafId);
        if (io) io.disconnect();
        if (onVis) document.removeEventListener('visibilitychange', onVis);
        units.forEach(function (unit) {
          if (unit.onMove) unit.el.removeEventListener('pointermove', unit.onMove);
          var ext = unit.gl.getExtension('WEBGL_lose_context');
          if (ext) ext.loseContext();
          if (unit.canvas.parentNode) unit.canvas.parentNode.removeChild(unit.canvas);
          unit.el.classList.remove('ad-shader', 'ad-shader--fallback');
          delete unit.el.__adShader;
        });
        units = [];
        var s = document.getElementById(CSS_ID);
        if (s) s.parentNode.removeChild(s);
      }
    };
  }

  global.awardShaderSurface = { init: init };
})(typeof window !== 'undefined' ? window : this);
