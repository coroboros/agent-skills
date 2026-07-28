/*
 * sdf-scramble-substrate — in-engine text as an SDF glyph field (winner:
 * Igloo Inc — SOTY 2024 + Dev SOTY; the winner-verified case-study read:
 * labels/UI rendered from an SDF glyph atlas so scramble/glitch/decode
 * happens by SWAPPING SDF TEXTURE OFFSETS in a shader — zero DOM relayout,
 * zero reflow, every frame cheap). The reflow-free scramble the fully-WebGL
 * builds require: glyphs are baked ONCE into a signed-distance atlas (a
 * runtime bake — 2D canvas raster + exact euclidean distance transform),
 * each label renders as textured quads, and the decode churns by rewriting
 * ONLY the per-glyph atlas-cell attribute buffer each tick — the DOM text
 * is never touched, so nothing recalculates style, ever. Chromatic
 * aberration rides the churn in the same fragment shader and dies at the
 * settle; a frost-dissolve pass is exposed as handle.transition(p) for the
 * engine's scene-transition beats (the full-scene passes stay the delegated
 * engine's business — the substrate mirrors them on its own quads).
 * Ruled DISTINCT from scramble-decode, the manifest's DOM spelling (its own
 * seen-in already names 'Igloo SDF decode'): that component rewrites
 * textContent per tick and forces style recalculation on every churn — the
 * right spelling for a standard DOM page; THIS is the in-engine variant the
 * gap orders for engine-world stacks. Same register law as the DOM
 * spelling: SHORT strings only — labels, nav links, stat captions, HUD
 * lines; never paragraphs.
 *
 * A11y (binding): the element's own text stays in the DOM, transparent
 * while the canvas paints (color:transparent — it remains in the
 * accessibility tree and selectable); the component also pins
 * aria-label to the true label at wire time, so the accessible name is
 * INTACT through every frame of the churn — the canvas itself is
 * aria-hidden. No-JS / no-WebGL / context loss: the plain authored text
 * stands (the --gl class drops and ink returns).
 * Discipline (binding): raw WebGL, zero deps; DPR capped at 2; the rAF
 * loop runs ONLY while a decode or transition is in flight — settled
 * labels are a static composited frame; IntersectionObserver fires the
 * entrance decode once in-view and gates replays; visibilitychange parks
 * a hidden tab. One atlas bake per page (bytes cached), one upload per
 * context.
 * prefers-reduced-motion: never scrambles — the component stays dormant
 * and the authored DOM text is the finished state (the DOM spelling's own
 * law, kept).
 *
 * Expected markup (mono targets keep the box rock-steady):
 *   <span data-ad-sdf-scramble>TELEMETRY ONLINE</span>
 *   <a data-ad-sdf-scramble="hover" href="…">ENTER THE FIELD</a>  hover replays
 *
 * Usage:  awardSdfScrambleSubstrate.init(root, opts)
 *   root      Element|Document  scope (default document)
 *   selector  string  labels (default '[data-ad-sdf-scramble]')
 *   duration  ms      entrance decode length (default 900)
 *   tick      ms      churn re-randomize interval (default 80 — the DOM
 *                     spelling's default, carried)
 * Returns { decode(i), transition(p), getState(), destroy() }.
 *   decode(i)      replay label i's decode
 *   transition(p)  0→1 frost + aberration on every label (scene pass hook)
 *   getState()     [{ live, running, resolved, total, label }] — resolved
 *                  advances left→right; label is the accessible name.
 * Idempotent per element. destroy() tears down GL, restores ink and
 * removes the stylesheet.
 *
 * Tokens: the glyph ink is the element's own computed color — the build's
 * tokens arrive through the cascade, never re-declared here.
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-sdf-scramble-css';
  var CHARSET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789·-–—:/&+*#@%!?.,’ ';
  var CELL = 64;          // atlas cell px
  var GLYPH = 44;         // bake size inside the cell
  var SPREAD = 10;        // sdf half-spread px
  var COLS = 8;
  var atlasCache = null;  // { bytes, w, h, family, charW } — one bake per page
  var reduce = function () {
    return !!(global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches);
  };

  var VERT =
    'attribute vec2 a_pos;attribute vec2 a_uv;attribute float a_cell;' +
    'uniform vec2 u_res;varying vec2 v_uv;varying float v_cell;' +
    'void main(){v_uv=a_uv;v_cell=a_cell;' +
    'vec2 c=(a_pos/u_res)*2.-1.;gl_Position=vec4(c.x,-c.y,0.,1.);}';

  var FRAG =
    'precision mediump float;varying vec2 v_uv;varying float v_cell;\n' +
    'uniform sampler2D u_atlas;uniform vec2 u_grid;uniform vec3 u_ink;\n' +
    'uniform float u_soft;uniform float u_aberr;uniform float u_frost;\n' +
    'float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453123);}\n' +
    'float sdf(vec2 uv,float cell){\n' +
    ' float col=mod(cell,u_grid.x);float row=floor(cell/u_grid.x);\n' +
    ' vec2 a=(vec2(col,row)+clamp(uv,.02,.98))/u_grid;\n' +
    ' return texture2D(u_atlas,a).r;\n' +
    '}\n' +
    'void main(){\n' +
    ' float d=sdf(v_uv,v_cell);\n' +
    ' float a=smoothstep(.5-u_soft,.5+u_soft,d);\n' +
    ' vec3 col=u_ink;\n' +
    // chromatic aberration: R/B read the field off-axis while churning
    ' if(u_aberr>0.){\n' +
    '  float r=smoothstep(.5-u_soft,.5+u_soft,sdf(v_uv+vec2(u_aberr,0.),v_cell));\n' +
    '  float b=smoothstep(.5-u_soft,.5+u_soft,sdf(v_uv-vec2(u_aberr,0.),v_cell));\n' +
    '  gl_FragColor=vec4(vec3(col.r*r,col.g*a,col.b*b),max(a,max(r,b)));\n' +
    ' } else gl_FragColor=vec4(col*a,a);\n' +
    // frost dissolve: per-pixel noise erodes the glyphs for scene passes
    ' if(u_frost>0.){\n' +
    '  float n=hash(floor(v_uv*24.)+v_cell);\n' +
    '  gl_FragColor*=1.-smoothstep(n*.8,n*.8+.2,u_frost);\n' +
    ' }\n' +
    '}';

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      '.ad-sdfs{position:relative;display:inline-block;}' +
      // the ink hide is an INLINE write (drive-caught: a builder's higher-
      // specificity color rule painted a double label under the canvas)
      '.ad-sdfs canvas.ad-sdfs__c{position:absolute;inset:0;width:100%;' +
        'height:100%;pointer-events:none;}';
    document.head.appendChild(s);
  }

  // exact euclidean distance transform (Felzenszwalb-Huttenlocher, 1D×2)
  function edt(grid, w, h) {
    var INF = 1e20;
    var f = new Float64Array(Math.max(w, h));
    var d = new Float64Array(Math.max(w, h));
    var z = new Float64Array(Math.max(w, h) + 1);
    var v = new Int32Array(Math.max(w, h));
    function edt1d(n) {
      var k = 0, q, s;
      v[0] = 0; z[0] = -INF; z[1] = INF;
      for (q = 1; q < n; q++) {
        do {
          s = ((f[q] + q * q) - (f[v[k]] + v[k] * v[k])) / (2 * q - 2 * v[k]);
        } while (s <= z[k] && --k > -1);
        k++;
        v[k] = q; z[k] = s; z[k + 1] = INF;
      }
      k = 0;
      for (q = 0; q < n; q++) {
        while (z[k + 1] < q) k++;
        d[q] = (q - v[k]) * (q - v[k]) + f[v[k]];
      }
    }
    var x, y;
    for (x = 0; x < w; x++) {
      for (y = 0; y < h; y++) f[y] = grid[y * w + x];
      edt1d(h);
      for (y = 0; y < h; y++) grid[y * w + x] = d[y];
    }
    for (y = 0; y < h; y++) {
      for (x = 0; x < w; x++) f[x] = grid[y * w + x];
      edt1d(w);
      for (x = 0; x < w; x++) grid[y * w + x] = d[x];
    }
  }

  // bake the charset into a signed-distance atlas — once per page
  function bakeAtlas(family) {
    if (atlasCache && atlasCache.family === family) return atlasCache;
    var rows = Math.ceil(CHARSET.length / COLS);
    var w = COLS * CELL, h = rows * CELL;
    var c2d = document.createElement('canvas');
    c2d.width = w; c2d.height = h;
    var ctx = c2d.getContext('2d', { willReadFrequently: true });
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, w, h);
    ctx.fillStyle = '#fff';
    ctx.font = GLYPH + 'px ' + family;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    for (var i = 0; i < CHARSET.length; i++) {
      var cx = (i % COLS) * CELL + CELL / 2;
      var cy = Math.floor(i / COLS) * CELL + CELL / 2;
      ctx.fillText(CHARSET[i], cx, cy);
    }
    var img = ctx.getImageData(0, 0, w, h).data;
    var n = w * h;
    var outside = new Float64Array(n);
    var inside = new Float64Array(n);
    var INF = 1e20;
    for (var p = 0; p < n; p++) {
      var on = img[p * 4] > 127;
      outside[p] = on ? 0 : INF;
      inside[p] = on ? INF : 0;
    }
    edt(outside, w, h);
    edt(inside, w, h);
    var bytes = new Uint8Array(n);
    for (var q = 0; q < n; q++) {
      var sd = Math.sqrt(inside[q]) - Math.sqrt(outside[q]); // + inside glyph
      bytes[q] = Math.max(0, Math.min(255, Math.round(128 + (sd / SPREAD) * 127)));
    }
    var charW = ctx.measureText('M').width; // mono advance at bake size
    atlasCache = { bytes: bytes, w: w, h: h, rows: rows, family: family, charW: charW };
    return atlasCache;
  }

  function inkRGB(el) {
    var probe = document.createElement('canvas');
    probe.width = probe.height = 1;
    var ctx = probe.getContext('2d', { willReadFrequently: true });
    ctx.fillStyle = '#fff';
    ctx.fillStyle = getComputedStyle(el).color || '#fff';
    ctx.fillRect(0, 0, 1, 1);
    var d = ctx.getImageData(0, 0, 1, 1).data;
    return [d[0] / 255, d[1] / 255, d[2] / 255];
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-sdf-scramble]';
    var DURATION = opts.duration != null ? +opts.duration : 900;
    var TICK = opts.tick != null ? +opts.tick : 80;

    // reduced-motion: the authored DOM text IS the finished state — dormant.
    if (reduce()) {
      return { decode: function () {}, transition: function () {},
               getState: function () { return []; }, destroy: function () {} };
    }

    injectCss();
    var units = [];

    function cellOf(ch) {
      var i = CHARSET.indexOf(ch.toUpperCase());
      return i < 0 ? CHARSET.indexOf(' ') : i;
    }

    function makeUnit(el) {
      if (el.__adSdfs) return;
      el.__adSdfs = true;
      var label = (el.textContent || '').trim();
      if (!label) { delete el.__adSdfs; return; }
      el.classList.add('ad-sdfs');
      // the accessible name, pinned — intact through every churn frame
      el.setAttribute('aria-label', label);

      var unit = {
        el: el, label: label, chars: label.split(''),
        gl: null, canvas: null, live: false, raf: 0, onScreen: false,
        resolved: 0, decoding: false, t0: 0, lastTick: 0,
        cells: null, cellBuf: null, u: {}, count: 0,
        aberr: 0, frost: 0, io: null, listeners: []
      };

      function mount() {
        var style = getComputedStyle(el);
        var atlas = bakeAtlas(style.fontFamily || 'monospace');
        var canvas = document.createElement('canvas');
        canvas.className = 'ad-sdfs__c';
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
        gl.enable(gl.BLEND);
        gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA); // premultiplied glyphs
        var tex = gl.createTexture();
        gl.bindTexture(gl.TEXTURE_2D, tex);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
        gl.pixelStorei(gl.UNPACK_ALIGNMENT, 1);
        gl.texImage2D(gl.TEXTURE_2D, 0, gl.LUMINANCE, atlas.w, atlas.h, 0,
                      gl.LUMINANCE, gl.UNSIGNED_BYTE, atlas.bytes);
        // glyph quads: positions/uvs static, cells dynamic (the swap buffer)
        var dpr = Math.min(2, global.devicePixelRatio || 1);
        var fontPx = parseFloat(style.fontSize) || 16;
        var scale = fontPx / GLYPH;
        var adv = atlas.charW * scale * dpr;
        var gw = CELL * scale * dpr;         // rendered cell box
        var baseY = (el.clientHeight * dpr) / 2;
        canvas.width = Math.max(1, Math.round(el.clientWidth * dpr));
        canvas.height = Math.max(1, Math.round(el.clientHeight * dpr));
        var n = unit.chars.length;
        var pos = new Float32Array(n * 12);
        var uv = new Float32Array(n * 12);
        var cells = new Float32Array(n * 6);
        for (var i = 0; i < n; i++) {
          var x0 = i * adv + adv / 2 - gw / 2;
          var y0 = baseY - gw / 2;
          var quad = [x0, y0, x0 + gw, y0, x0, y0 + gw,
                      x0 + gw, y0, x0 + gw, y0 + gw, x0, y0 + gw];
          var uvq = [0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 1];
          for (var k = 0; k < 12; k++) { pos[i * 12 + k] = quad[k]; uv[i * 12 + k] = uvq[k]; }
          for (var m = 0; m < 6; m++) cells[i * 6 + m] = cellOf(unit.chars[i]);
        }
        function attr(name, data, size, dynamic) {
          var b = gl.createBuffer();
          gl.bindBuffer(gl.ARRAY_BUFFER, b);
          gl.bufferData(gl.ARRAY_BUFFER, data, dynamic ? gl.DYNAMIC_DRAW : gl.STATIC_DRAW);
          var loc = gl.getAttribLocation(prog, name);
          gl.enableVertexAttribArray(loc);
          gl.vertexAttribPointer(loc, size, gl.FLOAT, false, 0, 0);
          return b;
        }
        attr('a_pos', pos, 2);
        attr('a_uv', uv, 2);
        unit.cellBuf = attr('a_cell', cells, 1, true);
        unit.cells = cells;
        unit.count = n * 6;
        ['u_res', 'u_atlas', 'u_grid', 'u_ink', 'u_soft', 'u_aberr', 'u_frost']
          .forEach(function (nm) { unit.u[nm] = gl.getUniformLocation(prog, nm); });
        gl.uniform2f(unit.u.u_res, canvas.width, canvas.height);
        gl.uniform1i(unit.u.u_atlas, 0);
        gl.uniform2f(unit.u.u_grid, COLS, atlas.rows);
        gl.uniform3fv(unit.u.u_ink, inkRGB(el));
        // half-spread transition ≈ 0.7 screen px, clamped — crisp at any scale
        gl.uniform1f(unit.u.u_soft,
          Math.max(0.02, Math.min(0.25, 0.7 / (scale * dpr * 2 * SPREAD))));
        el.appendChild(canvas);
        // ink sampled above — now the DOM text goes invisible but PRESENT
        // (a11y tree + selection); inline so no stylesheet can outrank it
        unit.prevColor = el.style.color;
        unit.prevShadow = el.style.textShadow;
        el.style.color = 'transparent';
        el.style.textShadow = 'none';
        unit.gl = gl;
        unit.canvas = canvas;
        unit.live = true;
        unit.onLost = function (e) { e.preventDefault(); teardownGl(); };
        unit.onRestored = function () { if (!unit.live) { mount(); draw(); } };
        canvas.addEventListener('webglcontextlost', unit.onLost);
        canvas.addEventListener('webglcontextrestored', unit.onRestored);
        draw();
        return true;
      }

      function teardownGl() {
        unit.live = false;
        unit.decoding = false;
        if (unit.raf) { global.cancelAnimationFrame(unit.raf); unit.raf = 0; }
        if (unit.canvas && unit.canvas.parentNode) unit.canvas.parentNode.removeChild(unit.canvas);
        // the authored ink returns
        el.style.color = unit.prevColor || '';
        el.style.textShadow = unit.prevShadow || '';
        unit.gl = null;
      }

      function pushCells() {
        var gl = unit.gl;
        gl.bindBuffer(gl.ARRAY_BUFFER, unit.cellBuf);
        gl.bufferSubData(gl.ARRAY_BUFFER, 0, unit.cells);
      }

      function draw() {
        var gl = unit.gl;
        if (!gl) return;
        gl.viewport(0, 0, unit.canvas.width, unit.canvas.height);
        gl.clearColor(0, 0, 0, 0);
        gl.clear(gl.COLOR_BUFFER_BIT);
        gl.uniform1f(unit.u.u_aberr, unit.aberr);
        gl.uniform1f(unit.u.u_frost, unit.frost);
        gl.drawArrays(gl.TRIANGLES, 0, unit.count);
      }

      function setCell(i, cell) {
        for (var m = 0; m < 6; m++) unit.cells[i * 6 + m] = cell;
      }

      function frame(now) {
        unit.raf = 0;
        if (!unit.live) return;
        if (document.hidden) { unit.pausedAt = now; return; } // parked; onVis resumes
        var t = Math.min(1, (now - unit.t0) / DURATION);
        unit.resolved = Math.floor(t * unit.chars.length);
        if (now - unit.lastTick >= TICK) {
          unit.lastTick = now;
          // the swap: unresolved positions churn by ATLAS OFFSET only
          for (var i = 0; i < unit.chars.length; i++) {
            if (i < unit.resolved || unit.chars[i] === ' ') setCell(i, cellOf(unit.chars[i]));
            else setCell(i, Math.floor(Math.random() * (CHARSET.length - 1)));
          }
          pushCells();
        }
        unit.aberr = 0.05 * (1 - t);
        draw();
        if (t < 1) { unit.raf = global.requestAnimationFrame(frame); return; }
        // settle: every glyph locks true, aberration dies, the loop parks
        for (var j = 0; j < unit.chars.length; j++) setCell(j, cellOf(unit.chars[j]));
        unit.resolved = unit.chars.length;
        unit.aberr = 0;
        pushCells();
        draw();
        unit.decoding = false;
      }

      unit.decode = function () {
        if (!unit.live || unit.decoding) return;
        unit.decoding = true;
        unit.resolved = 0;
        unit.t0 = global.performance.now();
        unit.lastTick = 0;
        unit.raf = global.requestAnimationFrame(frame);
      };
      unit.drawTransition = function () { if (unit.live) draw(); };
      unit.resume = function () {
        if (unit.decoding && !unit.raf && unit.live) {
          // the decode clock shifts by the paused span — no skip-ahead
          if (unit.pausedAt) {
            unit.t0 += global.performance.now() - unit.pausedAt;
            unit.pausedAt = 0;
          }
          unit.raf = global.requestAnimationFrame(frame);
        }
      };
      unit.teardownGl = teardownGl;

      function on(target, ev, fn, o) {
        target.addEventListener(ev, fn, o);
        unit.listeners.push([target, ev, fn, o]);
      }

      if ((el.getAttribute('data-ad-sdf-scramble') || '') === 'hover') {
        on(el, 'pointerenter', function (e) {
          if (e.pointerType !== 'touch') unit.decode();
        });
      }

      if ('IntersectionObserver' in global) {
        unit.io = new IntersectionObserver(function (entries) {
          unit.onScreen = entries[0].isIntersecting;
          if (unit.onScreen && unit.live && unit.resolved === 0 && !unit.decoding) {
            unit.decode(); // the entrance decode, once in view
          }
        });
        unit.io.observe(el);
      }

      if (!mount()) { delete el.__adSdfs; el.classList.remove('ad-sdfs'); return; }
      units.push(unit);
    }

    Array.prototype.slice.call(root.querySelectorAll(selector)).forEach(makeUnit);

    var onVis = function () {
      if (!document.hidden) units.forEach(function (u) { u.resume(); });
    };
    document.addEventListener('visibilitychange', onVis);

    return {
      decode: function (i) { if (units[i]) units[i].decode(); },
      transition: function (p) {
        p = Math.max(0, Math.min(1, +p || 0));
        units.forEach(function (u) {
          u.frost = p;
          u.aberr = p * 0.06;
          u.drawTransition();
        });
      },
      getState: function () {
        return units.map(function (u) {
          return { live: u.live, running: !!u.raf, resolved: u.resolved,
                   total: u.chars.length, label: u.el.getAttribute('aria-label') };
        });
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
          u.el.classList.remove('ad-sdfs');
          u.el.removeAttribute('aria-label');
          delete u.el.__adSdfs;
        });
        units = [];
        var s = document.getElementById(CSS_ID);
        if (s && s.parentNode) s.parentNode.removeChild(s);
      }
    };
  }

  global.awardSdfScrambleSubstrate = { init: init };
})(typeof window !== 'undefined' ? window : this);
