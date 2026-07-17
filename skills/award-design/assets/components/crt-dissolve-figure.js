/*
 * crt-dissolve-figure — shader dissolve-to-video on a media figure (winner:
 * Naked City Films, winner-verified via Codrops; the shader is WebGL-internal
 * on the winner, so the uniforms/offsets here are illustrative — the MECHANIC
 * is the verified part). On hover/focus a custom CRT-screen shader dissolves
 * the still into brand-tinted offset R/G/B channels — scanlines press in, the
 * rows jitter, the channels split and tint toward the accent while the frame
 * dissolves through per-pixel noise — then the buffered video underneath
 * autoplays once the transition completes. Leaving reverses the dissolve and
 * pauses the video. Distinct from glitch-type (a CSS RGB-split heading) and
 * figure-hover (contained zoom) — this is a full shader dissolve on a media
 * figure with a video floor under it.
 *
 * Discipline (binding): raw WebGL, zero deps; DPR capped at 2; the rAF loop
 * runs ONLY while the dissolve is in flight (no idle loop — at rest the still
 * frame is a static composited layer); the canvas is aria-hidden and
 * pointer-events:none. No WebGL → the spec's CSS fallback: an invert(100%)
 * flash ≤0.2s, then the still fades and the video plays. Touch: tap toggles
 * the reveal (the hover has no meaning under a coarse pointer). Keyboard:
 * focus mirrors hover; a figure with no focusable child gets tabindex=0.
 * reduced-motion: a no-op — the still IS the finished state, the video never
 * autoplays. No-JS: a plain figure (nothing hidden by markup).
 *
 * Expected markup — still on top, muted buffered video as the floor:
 *   <figure data-ad-crt>
 *     <img src="still.jpg" alt="…">
 *     <video src="reel.mp4" muted loop playsinline preload="auto"></video>
 *   </figure>
 *
 * Usage:  awardCrtDissolve.init(root, { selector })
 *   root      Element|Document  scope (default document)
 *   selector  string            figures to wire (default '[data-ad-crt]')
 * Returns { destroy() }. Idempotent per figure. destroy() tears down the GL
 * contexts, removes canvases, listeners and classes, and removes the
 * stylesheet.
 *
 * Tokens: --ad-accent tints the split channels; --ad-crt-dur times the
 * dissolve (default 700ms).
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-crt-dissolve-css';
  var reduce = function () {
    return global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches;
  };

  var VERT = 'attribute vec2 p;void main(){gl_Position=vec4(p,0.,1.);}';
  // Illustrative CRT grammar: cover-mapped still, row jitter, channel split,
  // accent tint, scanlines, noise dissolve — all scaled by u_progress.
  var FRAG =
    'precision mediump float;\n' +
    'uniform sampler2D u_tex;uniform vec2 u_res;uniform vec2 u_texres;\n' +
    'uniform float u_progress;uniform float u_time;uniform vec3 u_accent;\n' +
    'float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453123);}\n' +
    'void main(){\n' +
    ' vec2 uv=gl_FragCoord.xy/u_res;uv.y=1.-uv.y;\n' +
    // cover mapping: crop the texture axis the canvas is narrower on
    ' float ra=u_res.x/u_res.y;float ta=u_texres.x/u_texres.y;\n' +
    ' vec2 t=uv-.5;\n' +
    ' if(ra>ta)t.y*=ta/ra;else t.x*=ra/ta;\n' +
    ' t+=.5;\n' +
    ' float p=u_progress;\n' +
    // CRT row jitter: whole scan rows shear sideways while the dissolve runs
    ' float row=floor(gl_FragCoord.y/3.);\n' +
    ' t.x+=(hash(vec2(row,floor(u_time*24.)))-.5)*.08*p;\n' +
    // channel split: R and B pull apart horizontally with progress
    ' float off=.035*p;\n' +
    ' float r=texture2D(u_tex,t+vec2(off,0.)).r;\n' +
    ' float g=texture2D(u_tex,t).g;\n' +
    ' float b=texture2D(u_tex,t-vec2(off,0.)).b;\n' +
    ' vec3 col=vec3(r,g,b);\n' +
    // brand tint: the split channels lean toward the accent as they break up
    ' float luma=dot(col,vec3(.299,.587,.114));\n' +
    ' col=mix(col,u_accent*(.4+1.2*luma),p*.55);\n' +
    // scanlines press in with progress
    ' float scan=.82+.18*sin(gl_FragCoord.y*3.14159);\n' +
    ' col*=mix(1.,scan,p);\n' +
    // per-pixel noise dissolve: fully transparent at p=1 → the video floor
    ' float n=hash(floor(t*u_texres*.5));\n' +
    ' float a=1.-smoothstep(n*.8,n*.8+.2,p);\n' +
    ' gl_FragColor=vec4(col*a,a);\n' +
    '}';

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      '.ad-crt{position:relative;overflow:hidden;margin:0;}' +
      '.ad-crt img{position:relative;z-index:1;display:block;width:100%;}' +
      '.ad-crt video{position:absolute;inset:0;width:100%;height:100%;' +
        'object-fit:cover;z-index:0;}' +
      '.ad-crt canvas.ad-crt__c{position:absolute;inset:0;width:100%;height:100%;' +
        'z-index:2;pointer-events:none;}' +
      // GL live: the canvas paints the still, the img hands it the frame
      '.ad-crt--gl img{visibility:hidden;}' +
      // no-WebGL fallback — the spec's invert flash (≤0.2s), then the video
      '.ad-crt--fallback img{transition:filter 160ms linear,opacity 160ms linear 160ms;}' +
      '.ad-crt--fallback.is-on img{filter:invert(100%);opacity:0;}' +
      '@media (prefers-reduced-motion:reduce){' +
      '.ad-crt--fallback img{transition:none;}}';
    document.head.appendChild(s);
  }

  // Canvas-2D parses any CSS color (including oklch) into sRGB bytes — the
  // one robust bridge from token strings to shader uniforms.
  function accentRGB(el) {
    var probe = document.createElement('canvas');
    probe.width = probe.height = 1;
    var ctx = probe.getContext('2d', { willReadFrequently: true });
    var v = getComputedStyle(el).getPropertyValue('--ad-accent').trim() ||
      'oklch(62% 0.2 25)';
    ctx.fillStyle = '#000';
    ctx.fillStyle = v;
    ctx.fillRect(0, 0, 1, 1);
    var d = ctx.getImageData(0, 0, 1, 1).data;
    return [d[0] / 255, d[1] / 255, d[2] / 255];
  }

  function crtDur(el) {
    var v = getComputedStyle(el).getPropertyValue('--ad-crt-dur').trim();
    return parseFloat(v) || 700;
  }

  function easeInOutCubic(p) {
    return p < 0.5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2;
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-crt]';

    // reduced-motion: the still is the finished state — nothing to wire.
    if (reduce()) return { destroy: function () {} };

    injectCss();
    var units = [];

    function makeUnit(fig) {
      if (fig.__adCrt) return;
      fig.__adCrt = true;
      var img = fig.querySelector('img');
      var video = fig.querySelector('video');
      if (!img || !video) { delete fig.__adCrt; return; }
      fig.classList.add('ad-crt');

      var unit = {
        fig: fig, img: img, video: video, gl: null, canvas: null, u: null,
        p: 0, target: 0, raf: 0, from: 0, t0: 0, dur: 700,
        addedTab: false, listeners: []
      };

      function playFloor() { var pr = video.play(); if (pr && pr.catch) pr.catch(function () {}); }

      // --- WebGL path -----------------------------------------------------
      function mountGl() {
        var canvas = document.createElement('canvas');
        canvas.className = 'ad-crt__c';
        canvas.setAttribute('aria-hidden', 'true');
        var gl = canvas.getContext('webgl', { alpha: true, antialias: false, powerPreference: 'low-power' });
        if (!gl) return false;
        var prog = gl.createProgram();
        [[gl.VERTEX_SHADER, VERT], [gl.FRAGMENT_SHADER, FRAG]].forEach(function (sh) {
          var o = gl.createShader(sh[0]);
          gl.shaderSource(o, sh[1]);
          gl.compileShader(o);
          gl.attachShader(prog, o);
        });
        gl.linkProgram(prog);
        if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) return false;
        gl.useProgram(prog);
        var buf = gl.createBuffer();
        gl.bindBuffer(gl.ARRAY_BUFFER, buf);
        gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
        var loc = gl.getAttribLocation(prog, 'p');
        gl.enableVertexAttribArray(loc);
        gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
        gl.enable(gl.BLEND);
        // premultiplied output (col*a in the shader) composites cleanly
        gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA);
        var tex = gl.createTexture();
        gl.bindTexture(gl.TEXTURE_2D, tex);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
        gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, img);
        var u = {};
        ['u_tex', 'u_res', 'u_texres', 'u_progress', 'u_time', 'u_accent']
          .forEach(function (n) { u[n] = gl.getUniformLocation(prog, n); });
        gl.uniform1i(u.u_tex, 0);
        gl.uniform2f(u.u_texres, img.naturalWidth, img.naturalHeight);
        gl.uniform3fv(u.u_accent, accentRGB(fig));
        fig.appendChild(canvas);
        fig.classList.add('ad-crt--gl');
        unit.gl = gl;
        unit.canvas = canvas;
        unit.u = u;
        size();
        draw(0);
        return true;
      }

      function size() {
        var dpr = Math.min(2, global.devicePixelRatio || 1);
        var w = Math.round(fig.clientWidth * dpr);
        var h = Math.round(fig.clientHeight * dpr);
        if (unit.canvas.width !== w || unit.canvas.height !== h) {
          unit.canvas.width = w;
          unit.canvas.height = h;
          unit.gl.viewport(0, 0, w, h);
          unit.gl.uniform2f(unit.u.u_res, w, h);
        }
      }

      function draw(now) {
        var gl = unit.gl;
        gl.clearColor(0, 0, 0, 0);
        gl.clear(gl.COLOR_BUFFER_BIT);
        gl.uniform1f(unit.u.u_progress, unit.p);
        gl.uniform1f(unit.u.u_time, now / 1000);
        gl.drawArrays(gl.TRIANGLES, 0, 3);
      }

      // The tween: rAF only while p travels; endpoints stop the loop cold.
      function frame(now) {
        unit.raf = 0;
        var q = Math.min(1, (now - unit.t0) / unit.dur);
        unit.p = unit.from + (unit.target - unit.from) * easeInOutCubic(q);
        draw(now);
        if (q < 1) { unit.raf = global.requestAnimationFrame(frame); return; }
        unit.p = unit.target;
        if (unit.p >= 1) playFloor();       // the video floor takes over
        if (unit.p <= 0) unit.video.pause();
      }

      function go(target) {
        unit.target = target;
        if (unit.gl) {
          size();
          unit.from = unit.p;
          unit.t0 = global.performance.now();
          unit.dur = crtDur(fig) * Math.abs(target - unit.from) || 1;
          if (!unit.raf) unit.raf = global.requestAnimationFrame(frame);
        } else {
          // fallback: the invert flash rides CSS; JS only times the floor
          fig.classList.toggle('is-on', target >= 1);
          if (target >= 1) global.setTimeout(function () {
            if (unit.target >= 1) playFloor();
          }, 320);
          else unit.video.pause();
        }
      }

      function enter() { go(1); }
      function leave() { go(0); }
      function on(el, ev, fn, opts_) {
        el.addEventListener(ev, fn, opts_);
        unit.listeners.push([el, ev, fn, opts_]);
      }

      var glOk = false;
      function wire() {
        glOk = mountGl();
        if (!glOk) fig.classList.add('ad-crt--fallback');
        // fine pointer: hover drives the dissolve both ways
        on(fig, 'pointerenter', function (e) { if (e.pointerType !== 'touch') enter(); });
        on(fig, 'pointerleave', function (e) { if (e.pointerType !== 'touch') leave(); });
        // coarse pointer: the tap toggles the reveal
        on(fig, 'click', function (e) {
          if (!global.matchMedia || !global.matchMedia('(hover: none)').matches) return;
          e.preventDefault();
          if (unit.target >= 1) leave(); else enter();
        });
        // keyboard mirrors hover; guarantee a stop on the figure
        if (!fig.querySelector('a[href],button,[tabindex]')) {
          fig.setAttribute('tabindex', '0');
          unit.addedTab = true;
        }
        on(fig, 'focusin', enter);
        on(fig, 'focusout', leave);
      }

      // the texture needs decoded pixels — wire on load when still streaming
      if (img.complete && img.naturalWidth) wire();
      else on(img, 'load', wire, { once: true });

      units.push(unit);
    }

    Array.prototype.slice.call(root.querySelectorAll(selector)).forEach(makeUnit);

    return {
      destroy: function () {
        units.forEach(function (unit) {
          if (unit.raf) global.cancelAnimationFrame(unit.raf);
          unit.listeners.forEach(function (l) { l[0].removeEventListener(l[1], l[2], l[3]); });
          unit.video.pause();
          if (unit.gl) {
            var ext = unit.gl.getExtension('WEBGL_lose_context');
            if (ext) ext.loseContext();
          }
          if (unit.canvas && unit.canvas.parentNode) unit.canvas.parentNode.removeChild(unit.canvas);
          if (unit.addedTab) unit.fig.removeAttribute('tabindex');
          unit.fig.classList.remove('ad-crt', 'ad-crt--gl', 'ad-crt--fallback', 'is-on');
          delete unit.fig.__adCrt;
        });
        units = [];
        var s = document.getElementById(CSS_ID);
        if (s && s.parentNode) s.parentNode.removeChild(s);
      }
    };
  }

  global.awardCrtDissolve = { init: init };
})(typeof window !== 'undefined' ? window : this);
