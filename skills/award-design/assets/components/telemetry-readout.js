/*
 * telemetry-readout — the scroll-progress HUD instrument (corpse-derived: the
 * campaign's own record, not a winner citation — MARE's [data-hud-alt] /
 * [data-hud-phase] altitude + phase readers with piecewise value maps, CALDERA's
 * descent HUD — the 2400M altitude countdown and the 'acquiring a fix'
 * coordinate resolve where digits stand masked as '·' until progress earns
 * them, AVALANCHE's trace rail — the vermilion thread filling with descent and
 * a 'SIGNAL n%' read riding it. Three dead builds each re-invented this HUD
 * with zero library coverage — the closed-world boundary verdict (§5) promotes
 * the recurring invention into the library). Scroll progress through a tracked
 * span drives builder-authored readout channels; the component only writes
 * textContent and transforms — it never invents chrome, copy, or units.
 *
 * Channels — hooks inside each [data-ad-telemetry] root, all optional, all
 * dirty-checked (a write lands only when the resolved string/scale changes —
 * the corpses' lastAlt/lastCoord discipline):
 *   [data-tel-value]    numeric reader. data-tel-map="0:2400|0.9:0" is a
 *                       piecewise-linear keyframe map progress→value (the MARE
 *                       altFor grammar: any segment count, plateaus included);
 *                       shorthand data-tel-from/data-tel-to = a two-key map.
 *                       data-tel-format: "int" (locale-grouped, default) |
 *                       "fixed:n" | "pad:n".
 *   [data-tel-phase]    label reader. data-tel-phases="0:Approach|0.35:Descent
 *                       |0.9:Contact" — the label of the last threshold ≤ p
 *                       (MARE's phaseFor).
 *   [data-tel-resolve]  character resolve. data-tel-text is the full string;
 *                       alphanumerics render as data-tel-mask (default '·')
 *                       until reveal, punctuation/spacing always stands —
 *                       acquiring a fix, not noise (CALDERA's resolveCoord).
 *                       data-tel-until: progress at full resolve (default 0.7).
 *   [data-tel-rail]     the fill rail: contains [data-tel-rail-fill] (scaleY —
 *                       or scaleX under data-tel-orient="horizontal") welded
 *                       DIRECTLY to progress, both directions, no easing lag,
 *                       and an optional [data-tel-rail-read] marker translated
 *                       along the rail with progress (AVALANCHE's trace read —
 *                       transform-only; the corpse wrote style.height/top,
 *                       promoted here to compositor-clean transforms). A read
 *                       marker may itself carry value/phase channels.
 *
 * Progress: by default the root's own traversal — p = -rect.top /
 * (root height − viewport height), clamped, fail-safe 0 when the root is not
 * taller than the viewport (the CALDERA pin formula; author the root as the
 * tall tracked section). data-tel-span="page" reads whole-document progress
 * instead (the MARE grammar). One passive scroll listener per instance, read
 * once per rAF frame; an IntersectionObserver parks the work while the root
 * is off-screen.
 *
 * Usage:  awardTelemetryReadout.init(root, { selector })
 *   root      Element|Document  scope (default document)
 *   selector  string            instrument roots (default '[data-ad-telemetry]')
 * Returns { destroy() }. Idempotent per root.
 *
 * Content-visible at rest: the builder authors resting text in every channel —
 * a dead script leaves a legible HUD. prefers-reduced-motion: the HUD renders
 * its FINAL STATIC VALUES — apply(1) once at init, rail full, read marker
 * seated, no scroll binding, zero animation (the build order's imposed verdict:
 * readouts render their final static values).
 *
 * Tokens: --ad-accent (rail fill), --ad-ink (rail track), --ad-font-mono
 * (nothing forced — type stays the builder's), --ad-ease-signature unused by
 * design: the instrument is welded, never eased.
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-telemetry-readout-css';
  var reduce = function () {
    return global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches;
  };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      // no overflow clip: the fill (inset:0, scale ≤ 1) can never escape, and
      // the riding read marker must overhang the thin rail (drive-caught: an
      // overflow:hidden here ate the AVALANCHE-style 'SIGNAL n%' read whole).
      // :where() — zero specificity: the builder's own rail placement always
      // wins (drive-caught: a bare position:relative here, injected after the
      // page stylesheet, beat the builder's position:absolute at equal
      // specificity and dropped the rail a full viewport out of place).
      ':where([data-tel-rail]){position:relative;' +
        'background:color-mix(in oklab,var(--ad-ink,oklch(96% 0 0)) 18%,transparent);}' +
      '[data-tel-rail-fill]{position:absolute;inset:0;display:block;' +
        'background:var(--ad-accent,oklch(62% 0.2 25));' +
        'transform-origin:top left;transform:scaleY(0);will-change:transform;}' +
      '[data-tel-rail][data-tel-orient="horizontal"] [data-tel-rail-fill]{transform:scaleX(0);}' +
      '[data-tel-rail-read]{position:absolute;top:0;left:0;will-change:transform;}';
    document.head.appendChild(s);
  }

  function clamp01(v) { return v < 0 ? 0 : (v > 1 ? 1 : v); }

  // "0:2400|0.9:0" -> sorted [[p,v],...]
  function parseMap(str) {
    if (!str) return null;
    var keys = str.split('|').map(function (pair) {
      var i = pair.indexOf(':');
      return [parseFloat(pair.slice(0, i)), parseFloat(pair.slice(i + 1))];
    }).filter(function (k) { return !isNaN(k[0]) && !isNaN(k[1]); });
    keys.sort(function (a, b) { return a[0] - b[0]; });
    return keys.length ? keys : null;
  }
  function mapValue(keys, p) {
    if (p <= keys[0][0]) return keys[0][1];
    var last = keys[keys.length - 1];
    if (p >= last[0]) return last[1];
    for (var i = 1; i < keys.length; i++) {
      if (p <= keys[i][0]) {
        var a = keys[i - 1], b = keys[i];
        var t = (b[0] === a[0]) ? 1 : (p - a[0]) / (b[0] - a[0]);
        return a[1] + (b[1] - a[1]) * t;
      }
    }
    return last[1];
  }

  // "0:Approach|0.35:Descent" -> sorted [[p,label],...]
  function parsePhases(str) {
    if (!str) return null;
    var keys = str.split('|').map(function (pair) {
      var i = pair.indexOf(':');
      return [parseFloat(pair.slice(0, i)), pair.slice(i + 1)];
    }).filter(function (k) { return !isNaN(k[0]) && k[1]; });
    keys.sort(function (a, b) { return a[0] - b[0]; });
    return keys.length ? keys : null;
  }

  function formatValue(v, format) {
    if (format && format.indexOf('fixed:') === 0) return v.toFixed(parseInt(format.slice(6), 10) || 0);
    if (format && format.indexOf('pad:') === 0) {
      var w = parseInt(format.slice(4), 10) || 0;
      return String(Math.round(Math.abs(v))).padStart(w, '0');
    }
    return Math.round(v).toLocaleString('en-US'); // 'int' — the MARE fmt
  }

  function buildInstrument(el) {
    var inst = { el: el, page: el.getAttribute('data-tel-span') === 'page', channels: [] };

    Array.prototype.forEach.call(el.querySelectorAll('[data-tel-value]'), function (n) {
      var keys = parseMap(n.getAttribute('data-tel-map'));
      if (!keys) {
        var from = parseFloat(n.getAttribute('data-tel-from'));
        var to = parseFloat(n.getAttribute('data-tel-to'));
        if (isNaN(from) || isNaN(to)) return;
        keys = [[0, from], [1, to]];
      }
      var format = n.getAttribute('data-tel-format') || 'int';
      var last = null;
      inst.channels.push(function (p) {
        var out = formatValue(mapValue(keys, p), format);
        if (out !== last) { n.textContent = out; last = out; }
      });
    });

    Array.prototype.forEach.call(el.querySelectorAll('[data-tel-phase]'), function (n) {
      var keys = parsePhases(n.getAttribute('data-tel-phases'));
      if (!keys) return;
      var last = null;
      inst.channels.push(function (p) {
        var label = keys[0][1];
        for (var i = 0; i < keys.length; i++) if (p >= keys[i][0]) label = keys[i][1];
        if (label !== last) { n.textContent = label; last = label; }
      });
    });

    Array.prototype.forEach.call(el.querySelectorAll('[data-tel-resolve]'), function (n) {
      var full = n.getAttribute('data-tel-text');
      if (!full) return;
      var until = parseFloat(n.getAttribute('data-tel-until'));
      if (isNaN(until) || until <= 0) until = 0.7;
      var mask = n.getAttribute('data-tel-mask') || '·';
      var last = null;
      inst.channels.push(function (p) {
        var reveal = Math.floor(clamp01(p / until) * full.length);
        var out = '';
        for (var i = 0; i < full.length; i++) {
          var c = full[i];
          out += (i < reveal) ? c : (/[0-9a-zA-Z]/.test(c) ? mask : c);
        }
        if (out !== last) { n.textContent = out; last = out; }
      });
    });

    Array.prototype.forEach.call(el.querySelectorAll('[data-tel-rail]'), function (rail) {
      var fill = rail.querySelector('[data-tel-rail-fill]');
      var read = rail.querySelector('[data-tel-rail-read]');
      var horizontal = rail.getAttribute('data-tel-orient') === 'horizontal';
      var travel = 0;
      var measure = function () {
        if (!read) return;
        travel = horizontal ? (rail.clientWidth - read.offsetWidth)
                            : (rail.clientHeight - read.offsetHeight);
        if (travel < 0) travel = 0;
      };
      measure();
      inst.measures = inst.measures || [];
      inst.measures.push(measure);
      var last = -1;
      inst.channels.push(function (p) {
        var q = Math.round(p * 1e4) / 1e4;
        if (q === last) return;
        last = q;
        if (fill) fill.style.transform = horizontal ? 'scaleX(' + q + ')' : 'scaleY(' + q + ')';
        if (read) read.style.transform = horizontal
          ? 'translate3d(' + (q * travel).toFixed(1) + 'px,0,0)'
          : 'translate3d(0,' + (q * travel).toFixed(1) + 'px,0)';
      });
    });

    return inst;
  }

  function progressOf(inst) {
    if (inst.page) {
      var h = document.documentElement;
      var max = (h.scrollHeight - global.innerHeight) || 1;
      return clamp01((global.scrollY || h.scrollTop || 0) / max);
    }
    var rect = inst.el.getBoundingClientRect();
    var scrollable = inst.el.offsetHeight - global.innerHeight;
    if (scrollable <= 0 || !Number.isFinite(scrollable)) return 0; // fail-safe (CALDERA)
    return clamp01(-rect.top / scrollable);
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-telemetry]';
    injectCss();

    var els = Array.prototype.slice.call(root.querySelectorAll(selector))
      .filter(function (el) { return !el.__adTelBound; });
    if (!els.length) return { destroy: function () {} };
    els.forEach(function (el) { el.__adTelBound = true; });

    var instruments = els.map(buildInstrument);

    function apply(inst, p) {
      for (var i = 0; i < inst.channels.length; i++) inst.channels[i](p);
    }

    if (reduce()) {
      // Final static values — the instrument stands at its destination.
      instruments.forEach(function (inst) { apply(inst, 1); });
      return {
        destroy: function () {
          instruments.forEach(function (inst) { delete inst.el.__adTelBound; });
        }
      };
    }

    var ticking = false, rafId = 0, destroyed = false;
    function frame() {
      ticking = false;
      if (destroyed) return;
      instruments.forEach(function (inst) {
        if (inst.parked) return;
        apply(inst, progressOf(inst));
      });
    }
    function onScroll() {
      if (ticking) return;
      ticking = true;
      rafId = requestAnimationFrame(frame);
    }
    function onResize() {
      instruments.forEach(function (inst) {
        if (inst.measures) inst.measures.forEach(function (m) { m(); });
      });
      onScroll();
    }

    // Park off-screen instruments — no per-frame work for a HUD nobody sees.
    var io = null;
    if (typeof IntersectionObserver === 'function') {
      io = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          var inst = instruments.filter(function (i) { return i.el === en.target; })[0];
          if (inst) inst.parked = !en.isIntersecting;
        });
        onScroll();
      }, { rootMargin: '25% 0px 25% 0px' });
      instruments.forEach(function (inst) { if (!inst.page) io.observe(inst.el); });
    }

    instruments.forEach(function (inst) { apply(inst, progressOf(inst)); }); // seed
    global.addEventListener('scroll', onScroll, { passive: true });
    global.addEventListener('resize', onResize, { passive: true });

    return {
      destroy: function () {
        destroyed = true;
        cancelAnimationFrame(rafId);
        global.removeEventListener('scroll', onScroll);
        global.removeEventListener('resize', onResize);
        if (io) io.disconnect();
        instruments.forEach(function (inst) { delete inst.el.__adTelBound; });
      }
    };
  }

  global.awardTelemetryReadout = { init: init };
})(typeof window !== 'undefined' ? window : this);
