/* award-design in-page detector. Probes state rules and measures computed
   deltas, so a "perceptible" claim carries a measured value instead of a
   code-read. Reports findings and never clears them. */
(() => {
  'use strict';

  const FLOORS = { scale: 1.04, deltaL: 0.04, translatePx: 2, opacity: 0.1 };

  const RULES = [
    { id: 'FONT-RESOLVE', severity: 'FAIL', box: 'computed-face' },
    { id: 'SUBSTRATE-DEAD', severity: 'FAIL', box: 'live-substrate' },
    { id: 'DEAD', severity: 'REVIEW', box: 'live-substrate' },
    { id: 'HOMEOPATHIC', severity: 'REVIEW', box: 'live-substrate' },
    { id: 'SECTION-DEAD', severity: 'REVIEW', box: 'live-substrate' },
    { id: 'UNMEASURED-JS', severity: 'REVIEW', box: 'live-substrate' },
    { id: 'UNMEASURED-CSS', severity: 'REVIEW', box: 'live-substrate' },
    { id: 'CONTACT-GLOBAL-SQUASH', severity: 'FAIL', box: 'contact-response' },
    { id: 'CONTRAST', severity: 'FAIL', box: 'a11y-floor' },
    { id: 'UNCOMPUTABLE-BG', severity: 'REVIEW', box: 'a11y-floor' },
    { id: 'NAV-BORDER', severity: 'FAIL', box: 'nav-surface' },
    { id: 'NAV-BORDER-HAIRLINE', severity: 'REVIEW', box: 'nav-surface' },
    { id: 'NAV-HERO-OPAQUE', severity: 'FAIL', box: 'nav-over-hero' },
    { id: 'NAV-HERO-SURFACE', severity: 'REVIEW', box: 'nav-over-hero' },
    { id: 'TOKEN-CONFORM', severity: 'REVIEW', box: 'token-drift' },
    { id: 'H1-LINES', severity: 'FAIL', box: 'hero-h1-lines' },
    { id: 'H1-OVERRIDE', severity: 'REVIEW', box: 'hero-h1-lines' },
    { id: 'IDLE-CHANNEL', severity: 'REVIEW', box: 'breathes-at-rest' },
    { id: 'IMG-BROKEN', severity: 'FAIL', box: 'assets-real' },
    { id: 'H-OVERFLOW', severity: 'FAIL', box: 'no-h-scroll' },
    { id: 'TAP-TARGET', severity: 'REVIEW', box: 'touch-targets' }
  ];

  const FOOTER = 'Catches, never clears — composition, desire, fidelity, copy, pacing, seams stay judgment.';
  const PROBE_CLASS = '__ad-probe';
  const PROBE_STYLE_ID = '__ad-probe-style';
  const NATIVE_INTERACTIVE = 'a, button, [role=button], input, select, textarea, [tabindex]';
  const MAX_PROBED = 400;
  const MAX_SCAN = 5000;
  const SELECTOR_CAP = 15;
  const PEAK_WINDOW_MS = 600;
  const EPS = 1e-4;
  const STATE_PSEUDO = /:hover|:focus-visible/;

  // ---------------------------------------------------------------- pure core

  function srgbToOklab(r, g, b) {
    const lin = (c) => {
      const v = c / 255;
      return v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
    };
    const lr = lin(r), lg = lin(g), lb = lin(b);
    const l = Math.cbrt(0.4122214708 * lr + 0.5363325363 * lg + 0.0514459929 * lb);
    const m = Math.cbrt(0.2119034982 * lr + 0.6806995451 * lg + 0.1073969566 * lb);
    const s = Math.cbrt(0.0883024619 * lr + 0.2817188376 * lg + 0.6299787005 * lb);
    return {
      L: 0.2104542553 * l + 0.793617785 * m - 0.0040720468 * s,
      a: 1.9779984951 * l - 2.428592205 * m + 0.4505937099 * s,
      b: 0.0259040371 * l + 0.7827717662 * m - 0.808675766 * s
    };
  }

  function relativeLuminance(rgb) {
    const lin = (c) => {
      const v = c / 255;
      return v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
    };
    return 0.2126 * lin(rgb[0]) + 0.7152 * lin(rgb[1]) + 0.0722 * lin(rgb[2]);
  }

  function contrastRatio(rgb1, rgb2) {
    const l1 = relativeLuminance(rgb1);
    const l2 = relativeLuminance(rgb2);
    const hi = Math.max(l1, l2), lo = Math.min(l1, l2);
    return (hi + 0.05) / (lo + 0.05);
  }

  // Chrome serializes oklch()-authored computed colors as oklch(…) — contrast
  // and nav-border need rgb, so the inverse transform is required.
  function oklabToSrgb(lab) {
    const l = Math.pow(lab.L + 0.3963377774 * lab.a + 0.2158037573 * lab.b, 3);
    const m = Math.pow(lab.L - 0.1055613458 * lab.a - 0.0638541728 * lab.b, 3);
    const s = Math.pow(lab.L - 0.0894841775 * lab.a - 1.291485548 * lab.b, 3);
    const delin = (v) => {
      const c = v <= 0.0031308 ? 12.92 * v : 1.055 * Math.pow(v, 1 / 2.4) - 0.055;
      return Math.max(0, Math.min(255, Math.round(c * 255)));
    };
    return [
      delin(4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s),
      delin(-1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s),
      delin(-0.0041960863 * l - 0.7034186147 * m + 1.707614701 * s)
    ];
  }

  function hslToRgb(h, s, l) {
    h = ((h % 360) + 360) % 360;
    const c = (1 - Math.abs(2 * l - 1)) * s;
    const x = c * (1 - Math.abs(((h / 60) % 2) - 1));
    const m = l - c / 2;
    let rgb;
    if (h < 60) rgb = [c, x, 0];
    else if (h < 120) rgb = [x, c, 0];
    else if (h < 180) rgb = [0, c, x];
    else if (h < 240) rgb = [0, x, c];
    else if (h < 300) rgb = [x, 0, c];
    else rgb = [c, 0, x];
    return rgb.map((v) => Math.round((v + m) * 255));
  }

  // Returns { rgb: [r,g,b]|null, alpha, lab: {L,a,b} } or null when unparsable.
  // lab comes straight from oklch/oklab tokens (no rgb roundtrip needed there).
  function parseColor(input) {
    if (typeof input !== 'string') return null;
    const str = input.trim().toLowerCase();
    if (!str || str === 'none' || str === 'currentcolor' || str.startsWith('var(')) return null;
    if (str === 'transparent') return { rgb: [0, 0, 0], alpha: 0, lab: { L: 0, a: 0, b: 0 } };
    if (str === 'white') return { rgb: [255, 255, 255], alpha: 1, lab: srgbToOklab(255, 255, 255) };
    if (str === 'black') return { rgb: [0, 0, 0], alpha: 1, lab: srgbToOklab(0, 0, 0) };
    let m = str.match(/^#([0-9a-f]{3,8})$/);
    if (m) {
      let hex = m[1];
      if (hex.length <= 4) hex = hex.split('').map((c) => c + c).join('');
      const r = parseInt(hex.slice(0, 2), 16), g = parseInt(hex.slice(2, 4), 16), b = parseInt(hex.slice(4, 6), 16);
      const alpha = hex.length === 8 ? parseInt(hex.slice(6, 8), 16) / 255 : 1;
      return { rgb: [r, g, b], alpha, lab: srgbToOklab(r, g, b) };
    }
    m = str.match(/^rgba?\(\s*([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)(?:\s*[,/]\s*([\d.]+%?))?\s*\)$/);
    if (m) {
      const r = Math.round(+m[1]), g = Math.round(+m[2]), b = Math.round(+m[3]);
      const alpha = m[4] === undefined ? 1 : m[4].endsWith('%') ? parseFloat(m[4]) / 100 : +m[4];
      return { rgb: [r, g, b], alpha, lab: srgbToOklab(r, g, b) };
    }
    m = str.match(/^hsla?\(\s*([\d.-]+)(?:deg)?[,\s]+([\d.]+)%[,\s]+([\d.]+)%(?:\s*[,/]\s*([\d.]+%?))?\s*\)$/);
    if (m) {
      const rgb = hslToRgb(+m[1], +m[2] / 100, +m[3] / 100);
      const alpha = m[4] === undefined ? 1 : m[4].endsWith('%') ? parseFloat(m[4]) / 100 : +m[4];
      return { rgb, alpha, lab: srgbToOklab(rgb[0], rgb[1], rgb[2]) };
    }
    m = str.match(/^oklch\(\s*([\d.]+%?)\s+([\d.]+%?)\s+([\d.-]+)(?:deg)?\s*(?:\/\s*([\d.]+%?))?\s*\)$/);
    if (m) {
      const L = m[1].endsWith('%') ? parseFloat(m[1]) / 100 : +m[1];
      const C = m[2].endsWith('%') ? parseFloat(m[2]) * 0.004 : +m[2];
      const H = (+m[3] * Math.PI) / 180;
      const alpha = m[4] === undefined ? 1 : m[4].endsWith('%') ? parseFloat(m[4]) / 100 : +m[4];
      const lab = { L, a: C * Math.cos(H), b: C * Math.sin(H) };
      return { rgb: oklabToSrgb(lab), alpha, lab };
    }
    m = str.match(/^oklab\(\s*([\d.]+%?)\s+([\d.-]+)\s+([\d.-]+)\s*(?:\/\s*([\d.]+%?))?\s*\)$/);
    if (m) {
      const L = m[1].endsWith('%') ? parseFloat(m[1]) / 100 : +m[1];
      const alpha = m[4] === undefined ? 1 : m[4].endsWith('%') ? parseFloat(m[4]) / 100 : +m[4];
      const lab = { L, a: +m[2], b: +m[3] };
      return { rgb: oklabToSrgb(lab), alpha, lab };
    }
    m = str.match(/^color\(srgb\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*(?:\/\s*([\d.]+%?))?\s*\)$/);
    if (m) {
      const r = Math.round(+m[1] * 255), g = Math.round(+m[2] * 255), b = Math.round(+m[3] * 255);
      const alpha = m[4] === undefined ? 1 : m[4].endsWith('%') ? parseFloat(m[4]) / 100 : +m[4];
      return { rgb: [r, g, b], alpha, lab: srgbToOklab(r, g, b) };
    }
    return null;
  }

  function parseTransform(value) {
    const identity = { scaleX: 1, scaleY: 1, translateX: 0, translateY: 0 };
    if (!value || value === 'none') return identity;
    let m = value.match(/^matrix\(([^)]+)\)$/);
    if (m) {
      const v = m[1].split(',').map((n) => parseFloat(n));
      return {
        scaleX: Math.hypot(v[0], v[1]),
        scaleY: Math.hypot(v[2], v[3]),
        translateX: v[4],
        translateY: v[5]
      };
    }
    m = value.match(/^matrix3d\(([^)]+)\)$/);
    if (m) {
      const v = m[1].split(',').map((n) => parseFloat(n));
      return {
        scaleX: Math.hypot(v[0], v[1], v[2]),
        scaleY: Math.hypot(v[4], v[5], v[6]),
        translateX: v[12],
        translateY: v[13]
      };
    }
    return identity;
  }

  // Composes the transform matrix with the individual scale/translate properties.
  function effectiveTransform(snap) {
    const t = parseTransform(snap.transform);
    let { scaleX, scaleY, translateX, translateY } = t;
    if (snap.scale && snap.scale !== 'none') {
      const parts = snap.scale.split(/\s+/).map(parseFloat);
      scaleX *= parts[0];
      scaleY *= parts.length > 1 ? parts[1] : parts[0];
    }
    if (snap.translate && snap.translate !== 'none') {
      const parts = snap.translate.split(/\s+/).map(parseFloat);
      translateX += parts[0] || 0;
      translateY += parts[1] || 0;
    }
    return { scaleX, scaleY, translateX, translateY };
  }

  function colorPairDelta(before, after) {
    if (before === after) return { deltaL: 0, alphaDelta: 0, discrete: 0 };
    const a = parseColor(before), b = parseColor(after);
    if (!a || !b) return { deltaL: 0, alphaDelta: 0, discrete: 1 };
    if (a.alpha === 0 && b.alpha === 0) return { deltaL: 0, alphaDelta: 0, discrete: 0 };
    return { deltaL: Math.abs(a.lab.L - b.lab.L), alphaDelta: Math.abs(a.alpha - b.alpha), discrete: 0 };
  }

  function scaleRatio(a, b) {
    if (!a || !b) return 1;
    const r = Math.max(Math.abs(a), Math.abs(b)) / Math.min(Math.abs(a), Math.abs(b));
    return Number.isFinite(r) ? r : 1;
  }

  function diffPseudo(before, after, out) {
    const gone = (p) => !p || p.content === 'none' || p.content === undefined;
    if (gone(before) && gone(after)) return;
    if (gone(before) !== gone(after)) { out.discrete += 1; return; }
    for (const key of ['width', 'height']) {
      const b = parseFloat(before[key]), a = parseFloat(after[key]);
      if (Number.isFinite(b) && Number.isFinite(a)) out.translatePx = Math.max(out.translatePx, Math.abs(a - b));
      else if (before[key] !== after[key]) out.discrete += 1;
    }
    const bt = effectiveTransform(before), at = effectiveTransform(after);
    out.scale = Math.max(out.scale, scaleRatio(at.scaleX, bt.scaleX), scaleRatio(at.scaleY, bt.scaleY));
    out.translatePx = Math.max(out.translatePx,
      Math.abs(at.translateX - bt.translateX), Math.abs(at.translateY - bt.translateY));
    const bo = parseFloat(before.opacity), ao = parseFloat(after.opacity);
    if (Number.isFinite(bo) && Number.isFinite(ao)) out.opacity = Math.max(out.opacity, Math.abs(ao - bo));
  }

  function diffChannels(before, after) {
    const out = { scale: 1, translatePx: 0, deltaL: 0, opacity: 0, discrete: 0 };
    const bt = effectiveTransform(before), at = effectiveTransform(after);
    out.scale = Math.max(scaleRatio(at.scaleX, bt.scaleX), scaleRatio(at.scaleY, bt.scaleY));
    out.translatePx = Math.max(
      Math.abs(at.translateX - bt.translateX), Math.abs(at.translateY - bt.translateY));
    for (const key of ['color', 'backgroundColor', 'borderColor']) {
      const d = colorPairDelta(before[key], after[key]);
      out.deltaL = Math.max(out.deltaL, d.deltaL);
      out.opacity = Math.max(out.opacity, d.alphaDelta);
      out.discrete += d.discrete;
    }
    const bo = parseFloat(before.opacity), ao = parseFloat(after.opacity);
    if (Number.isFinite(bo) && Number.isFinite(ao)) out.opacity = Math.max(out.opacity, Math.abs(ao - bo));
    // No floor on these: an underline appearing, an outline, a shadow, a
    // gradient sweep, or a filter shift is structural — any change registers.
    for (const key of ['boxShadow', 'clipPath', 'textDecorationLine', 'outlineStyle',
      'outlineWidth', 'backgroundPosition', 'backgroundSize', 'filter']) {
      if ((before[key] || 'none') !== (after[key] || 'none')) out.discrete += 1;
    }
    diffPseudo(before.pseudoBefore, after.pseudoBefore, out);
    diffPseudo(before.pseudoAfter, after.pseudoAfter, out);
    return out;
  }

  function maxChannels(a, b) {
    if (!a) return b;
    return {
      scale: Math.max(a.scale, b.scale),
      translatePx: Math.max(a.translatePx, b.translatePx),
      deltaL: Math.max(a.deltaL, b.deltaL),
      opacity: Math.max(a.opacity, b.opacity),
      discrete: a.discrete + b.discrete
    };
  }

  // Fold for peak-hold sampling: every frame diffs against the same rest
  // snapshot, so discrete maxes instead of summing; a persistent clip-path
  // change counts as one structural delta rather than one per sampled frame.
  function peakChannels(a, b) {
    if (!a) return b;
    const out = maxChannels(a, b);
    out.discrete = Math.max(a.discrete, b.discrete);
    return out;
  }

  // object = peak channels on the struck element; secondaries = peak channels
  // per declared secondary. GLOBAL-SQUASH: the only above-floor response is a
  // whole-element scale/opacity — the paper-cutout. Any secondary above a
  // floor, or a structural/translate/color channel on the object, is LOCAL and
  // stays judgment. Canvas media never reach this classifier.
  function classifyContact(object, secondaries, floors) {
    const f = Object.assign({}, FLOORS, floors || {});
    const above = (raw) => {
      const ch = raw || {};
      return {
        squash: Math.abs((ch.scale || 1) - 1) >= f.scale - 1 - EPS ||
          (ch.opacity || 0) >= f.opacity - EPS,
        local: (ch.translatePx || 0) >= f.translatePx - EPS ||
          (ch.deltaL || 0) >= f.deltaL - EPS ||
          (ch.discrete || 0) > 0
      };
    };
    const obj = above(object);
    const anySecondary = (secondaries || []).some((ch) => {
      const a = above(ch);
      return a.squash || a.local;
    });
    if (anySecondary || obj.local) return 'LOCAL';
    return obj.squash ? 'GLOBAL-SQUASH' : 'NONE';
  }

  // sample = { hasStateRule, hasAffordance, pageHasJs, channels }.
  // Channels without a floor (box-shadow, clip-path, pseudo appear/vanish) count
  // as perceptible when they change at all, because they are structural rather
  // than gradual.
  function classifyDelta(sample, floors) {
    const f = Object.assign({}, FLOORS, floors || {});
    const ch = sample.channels || {};
    const scale = Math.abs((ch.scale || 1) - 1);
    const translate = ch.translatePx || 0;
    const dL = ch.deltaL || 0;
    const op = ch.opacity || 0;
    const discrete = ch.discrete || 0;
    const perceptible =
      scale >= f.scale - 1 - EPS ||
      dL >= f.deltaL - EPS ||
      translate >= f.translatePx - EPS ||
      op >= f.opacity - EPS ||
      discrete > 0;
    const anyDelta = perceptible || scale > EPS || dL > EPS || translate > EPS || op > EPS;
    if (!sample.hasStateRule && !sample.hasAffordance) return 'SKIP';
    if (perceptible) return 'OK';
    if (sample.hasStateRule) return 'HOMEOPATHIC';
    if (!anyDelta) return sample.pageHasJs ? 'UNMEASURED-JS' : 'DEAD';
    return 'HOMEOPATHIC';
  }

  // Nav-over-hero surface, judged at rest (scrollY === 0). A top bar that paints
  // an OWNED surface over hero media is the decapitation tell — the bone strip
  // that shipped over ARDEN's photo. sample = { hasMediaUnder, isScrim, alpha,
  // hasBackdropFilter, groundDeltaL }. Transparent (the winner norm) or a
  // to-transparent legibility scrim is EXEMPT; an opaque, unblurred band whose
  // surface is off the page ground is the FAIL; frost-with-blur, translucent, or
  // an opaque same-ground bar (winner-cited — Cyd's always-solid cream) is
  // REVIEW, judged in §8 against the archetype canon. FAIL fires only on proof:
  // a resolvable solid colour ≠ the ground (groundDeltaL > 0.05). An image-ground
  // bar, or an unresolvable page ground, leaves groundDeltaL at 0 → REVIEW, never
  // a false decapitation FAIL (the caller passes 0 when it cannot prove off-ground).
  function classifyNavHero(sample) {
    const s = sample || {};
    if (!s.hasMediaUnder || s.isScrim) return 'EXEMPT';
    const alpha = s.alpha || 0;
    if (alpha < 0.05) return 'EXEMPT';
    if (alpha >= 0.9 && !s.hasBackdropFilter && (s.groundDeltaL || 0) > 0.05) return 'FAIL';
    return 'REVIEW';
  }

  // A tall section whose largest empty region swallows most of it is the
  // "empty and dead" beat — sparse text stranded in a corner over a void, the
  // occluded / near-invisible background bed contributing nothing. VOID_FLOORS
  // is separate from FLOORS (perceptibility) so the exact-equality FLOORS test
  // holds; sectionMinVh keeps ~1-viewport heroes and short beats out of scope.
  const VOID_FLOORS = { sectionMinVh: 1.4, voidFraction: 0.45 };

  function largestRectInHistogram(h) {
    const stack = [];
    let best = 0;
    for (let i = 0; i <= h.length; i++) {
      const cur = i === h.length ? 0 : h[i];
      while (stack.length && h[stack[stack.length - 1]] >= cur) {
        const height = h[stack.pop()];
        const width = stack.length ? i - stack[stack.length - 1] - 1 : i;
        if (height * width > best) best = height * width;
      }
      stack.push(i);
    }
    return best;
  }

  // Largest all-empty (0) axis-aligned rectangle in a 0/1 grid, as a fraction of
  // the whole grid. Histogram method, O(rows·cols).
  function largestEmptyFraction(grid) {
    const rows = grid.length;
    if (!rows) return 0;
    const cols = grid[0].length;
    if (!cols) return 0;
    const hist = new Array(cols).fill(0);
    let best = 0;
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) hist[c] = grid[r][c] ? 0 : hist[c] + 1;
      const rect = largestRectInHistogram(hist);
      if (rect > best) best = rect;
    }
    return best / (rows * cols);
  }

  function classifyVoid(sample, floors) {
    const f = floors || VOID_FLOORS;
    if ((sample.heightVh || 0) < f.sectionMinVh) return 'SKIP';
    return (sample.emptyFraction || 0) > f.voidFraction ? 'DEAD' : 'ALIVE';
  }

  function runOptions(raw) {
    if (raw === undefined) raw = {};
    if (!raw || typeof raw !== 'object' || Array.isArray(raw)) throw new TypeError('run options must be an object');
    const names = ['face', 'archetype', 'floors', 'h1MaxLines', 'h1OverrideReason'];
    for (const key of Object.keys(raw)) {
      if (!names.includes(key)) throw new TypeError('unknown run option: ' + key);
    }
    for (const key of ['face', 'archetype', 'h1OverrideReason']) {
      if (raw[key] != null && typeof raw[key] !== 'string') throw new TypeError(key + ' must be a string');
    }
    const supplied = raw.floors === undefined ? {} : raw.floors;
    if (!supplied || typeof supplied !== 'object' || Array.isArray(supplied)) throw new TypeError('floors must be an object');
    const floors = Object.assign({}, FLOORS);
    for (const [key, value] of Object.entries(supplied)) {
      if (!Object.hasOwn(FLOORS, key) || !Number.isFinite(value) ||
          value <= (key === 'scale' ? 1 : 0) || (['deltaL', 'opacity'].includes(key) && value > 1)) {
        throw new TypeError('invalid floor: ' + key);
      }
      floors[key] = value;
    }
    const h1MaxLines = raw.h1MaxLines === undefined ? 2 : raw.h1MaxLines;
    const h1OverrideReason = raw.h1OverrideReason == null ? null : raw.h1OverrideReason.trim();
    if (![2, 3].includes(h1MaxLines)) throw new TypeError('h1MaxLines must be 2 or the documented client exception, 3');
    if (h1MaxLines === 3 && !h1OverrideReason) throw new TypeError('h1MaxLines: 3 requires h1OverrideReason quoting the client clause and DESIGN.md reference');
    if (h1MaxLines === 2 && h1OverrideReason) throw new TypeError('h1OverrideReason requires h1MaxLines: 3');
    return { face: raw.face || null, archetype: raw.archetype || null, floors, h1MaxLines, h1OverrideReason };
  }

  const api = { FLOORS, VOID_FLOORS, RULES, srgbToOklab, relativeLuminance, contrastRatio, parseColor, parseTransform, classifyDelta, classifyContact, classifyNavHero, largestEmptyFraction, classifyVoid, diffChannels, peakChannels, runOptions, nestedSelectors, splitCarrier };

  if (typeof window === 'undefined') {
    if (typeof module !== 'undefined' && module.exports) module.exports = api;
    return;
  }

  // ------------------------------------------------------------ browser layer

  function finding(id, selector, evidence) {
    const rule = RULES.find((r) => r.id === id);
    return { id, severity: rule.severity, box: rule.box, selector, evidence };
  }

  function cssPath(el) {
    const parts = [];
    let node = el;
    while (node && node.nodeType === 1 && node !== document.body && parts.length < 3) {
      let part = node.tagName.toLowerCase();
      if (node.id) { parts.unshift(part + '#' + node.id); break; }
      const cls = Array.from(node.classList).filter((c) => c !== PROBE_CLASS).slice(0, 2);
      if (cls.length) part += '.' + cls.join('.');
      const parent = node.parentElement;
      if (parent) {
        const same = Array.from(parent.children).filter((c) => c.tagName === node.tagName);
        if (same.length > 1) part += ':nth-of-type(' + (same.indexOf(node) + 1) + ')';
      }
      parts.unshift(part);
      node = parent;
    }
    return parts.join(' > ') || el.tagName.toLowerCase();
  }

  function isRendered(el) {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') return false;
    const rect = el.getBoundingClientRect();
    return rect.width > 0 || rect.height > 0;
  }

  function hasDirectText(el) {
    for (const node of el.childNodes) {
      if (node.nodeType === 3 && node.textContent.trim().length > 0) return true;
    }
    return false;
  }

  function snapshotChannels(el) {
    const cs = getComputedStyle(el);
    const pseudo = (which) => {
      const p = getComputedStyle(el, which);
      return { content: p.content, width: p.width, height: p.height, transform: p.transform, translate: p.translate, scale: p.scale, opacity: p.opacity };
    };
    return {
      transform: cs.transform, translate: cs.translate, scale: cs.scale,
      color: cs.color, backgroundColor: cs.backgroundColor, borderColor: cs.borderTopColor,
      opacity: cs.opacity, boxShadow: cs.boxShadow, clipPath: cs.clipPath,
      textDecorationLine: cs.textDecorationLine, outlineStyle: cs.outlineStyle,
      outlineWidth: cs.outlineWidth, backgroundPosition: cs.backgroundPosition,
      backgroundSize: cs.backgroundSize, filter: cs.filter,
      pseudoBefore: pseudo('::before'), pseudoAfter: pseudo('::after')
    };
  }

  function splitSelectors(text) {
    const parts = [];
    let depth = 0, start = 0;
    for (let i = 0; i < text.length; i++) {
      const c = text[i];
      if (c === '(' || c === '[') depth++;
      else if (c === ')' || c === ']') depth--;
      else if (c === ',' && depth === 0) { parts.push(text.slice(start, i)); start = i + 1; }
    }
    parts.push(text.slice(start));
    return parts.map((p) => p.trim()).filter(Boolean);
  }

  function nestedSelectors(selector, parent) {
    if (!parent) return selector;
    const context = ':is(' + parent + ')';
    return splitSelectors(selector).map((part) => {
      let out = '', quote = null, bracket = 0, replaced = false;
      for (let i = 0; i < part.length; i++) {
        const c = part[i];
        if (c === '\\') { out += c + (part[++i] || ''); continue; }
        if (quote) { out += c; if (c === quote) quote = null; continue; }
        if (c === '"' || c === "'") { quote = c; out += c; continue; }
        if (c === '[') bracket++;
        if (c === ']') bracket--;
        if (c === '&' && bracket === 0) { out += context; replaced = true; }
        else out += c;
      }
      return replaced ? out : context + ' ' + out;
    }).join(', ');
  }

  // carrier = the compound that carries :hover (the element the pointer touches);
  // trailing = the rest of the selector (the descendant that responds).
  function splitCarrier(selector) {
    const unknown = { carrier: null, trailing: '', unmeasured: true };
    // Only the routing copy is unwrapped. The injected probe keeps :is() and
    // its native nesting specificity. A single leading branch can be expanded
    // without moving the hover carrier onto the parent's final descendant.
    while (selector.startsWith(':is(')) {
      let depth = 1, end = 4, quote = null;
      for (; end < selector.length && depth; end++) {
        if (selector[end] === '\\') { end++; continue; }
        if (quote) { if (selector[end] === quote) quote = null; continue; }
        if (selector[end] === '"' || selector[end] === "'") { quote = selector[end]; continue; }
        if (selector[end] === '(') depth++;
        else if (selector[end] === ')') depth--;
      }
      const inner = selector.slice(4, end - 1);
      if (!STATE_PSEUDO.test(inner)) break;
      if (depth || splitSelectors(inner).length !== 1) return unknown;
      selector = inner + selector.slice(end);
    }
    if ((selector.match(/:hover|:focus-visible/g) || []).length !== 1) return unknown;
    const idx = selector.search(STATE_PSEUDO);
    let end = selector.length;
    let depth = 0;
    for (let i = 0; i < selector.length; i++) {
      const c = selector[i];
      if (i === idx && depth) return unknown; // state inside another function
      if (c === '(' || c === '[') depth++;
      else if (c === ')' || c === ']') depth--;
      else if (i > idx && depth === 0 && (c === ' ' || c === '>' || c === '+' || c === '~')) { end = i; break; }
    }
    const strip = (s) => s.replace(/:hover|:focus-visible/g, '').replace(/::[a-z-]+(\([^)]*\))?$/i, '').trim();
    let carrier = strip(selector.slice(0, end));
    if (!carrier) carrier = '*';
    let trailing = selector.slice(end).replace(/^[\s>+~]+/, '').trim();
    if (trailing) trailing = trailing.replace(/::[a-z-]+(\([^)]*\))?/gi, '').trim();
    return { carrier, trailing };
  }

  function collectStateRules() {
    const rules = [], unmeasuredRules = [];
    let sheets = 0, opaqueSheets = 0;
    const walk = (list, parent) => {
      for (const rule of Array.from(list)) {
        if (rule.styleSheet) {
          // @import — the nested sheet never appears in document.styleSheets.
          try { walk(rule.styleSheet.cssRules); } catch (e) { opaqueSheets++; }
          continue;
        }
        if (rule.style && (rule.selectorText !== undefined || parent)) {
          const sel = rule.selectorText === undefined ? parent : nestedSelectors(rule.selectorText, parent);
          for (const part of splitSelectors(sel)) {
            if (!STATE_PSEUDO.test(part)) continue;
            const { carrier, trailing } = splitCarrier(part);
            if (!carrier) { if (/:hover/.test(part)) unmeasuredRules.push(part); continue; }
            const probeSelector = part.replace(/:hover|:focus-visible/g, '.' + PROBE_CLASS);
            rules.push({ selector: part, probeSelector, carrier, trailing, css: rule.style.cssText,
              hover: /:hover/.test(part) });
          }
          if (rule.cssRules && rule.cssRules.length) walk(rule.cssRules, sel);
          continue;
        }
        if (rule.cssRules && rule.cssRules.length) {
          if (rule.media && !matchMedia(rule.conditionText).matches) continue;
          if (typeof CSSSupportsRule !== 'undefined' && rule instanceof CSSSupportsRule) {
            try { if (!CSS.supports(rule.conditionText)) continue; } catch (e) { /* keep walking */ }
          }
          if (typeof CSSKeyframesRule !== 'undefined' && rule instanceof CSSKeyframesRule) continue;
          walk(rule.cssRules, parent);
        }
      }
    };
    for (const sheet of Array.from(document.styleSheets)) {
      sheets++;
      let list;
      // Cross-origin sheets throw on cssRules access — count them rather than
      // skipping silently.
      try { list = sheet.cssRules; } catch (e) { opaqueSheets++; continue; }
      if (list) walk(list);
    }
    return { rules, sheets, opaqueSheets, unmeasuredRules, unresolvedStateSelectors: 0 };
  }

  function safeMatches(el, selector) {
    try { return el.matches(selector); } catch (e) { return false; }
  }

  function probeSubstrate(collected, floors, findings) {
    const pageHasJs = document.scripts.length > 0;
    // The substrate gate measures the POINTER response ("reads dead under the
    // pointer"). :focus-visible rules — the universal focus ring above all —
    // are not a hover affordance; folded into one probe class they paint their
    // outline onto every focusable element and credit it as alive (a structural
    // discrete carries no floor). Probe hover only. A purely focus-driven element
    // then reads UNMEASURED-JS (drive it), never a free OK from the ring.
    const hoverRules = collected.rules.filter((r) => r.hover);
    const styleEl = document.createElement('style');
    styleEl.id = PROBE_STYLE_ID;
    // The kill rule is load-bearing: without it a transitioned property reads
    // its rest value on the immediate post-probe snapshot and every hover
    // measures zero.
    styleEl.textContent = hoverRules.map((r) => r.probeSelector + ' { ' + r.css + ' }').join('\n') +
      '\n.' + PROBE_CLASS + ', .' + PROBE_CLASS + ' *, .' + PROBE_CLASS + '::before, .' +
      PROBE_CLASS + '::after, .' + PROBE_CLASS + ' *::before, .' + PROBE_CLASS +
      ' *::after { transition: none !important; }';
    const prior = document.getElementById(PROBE_STYLE_ID);
    if (prior) prior.remove();
    document.head.appendChild(styleEl);

    const candidates = new Set(document.querySelectorAll(NATIVE_INTERACTIVE));
    const unmeasuredCss = new Set();
    for (const selector of collected.unmeasuredRules) {
      try {
        for (const target of document.querySelectorAll(selector.replace(/:hover|:focus-visible/g, ''))) {
          unmeasuredCss.add(target);
          target.querySelectorAll(NATIVE_INTERACTIVE).forEach((el) => unmeasuredCss.add(el));
          for (let el = target.parentElement; el; el = el.parentElement) {
            if (el.matches(NATIVE_INTERACTIVE) || getComputedStyle(el).cursor === 'pointer') unmeasuredCss.add(el);
          }
        }
      } catch (e) { collected.unresolvedStateSelectors++; }
    }
    for (const el of unmeasuredCss) candidates.add(el);
    for (const r of hoverRules) {
      if (r.carrier === '*' || r.carrier === 'html' || r.carrier === 'body') continue;
      try { document.querySelectorAll(r.carrier).forEach((el) => candidates.add(el)); } catch (e) { /* invalid derived selector */ }
    }

    const counts = { probed: 0, ok: 0, dead: 0, homeopathic: 0, unmeasuredJs: 0, unmeasuredCss: 0 };
    const selectors = { ok: [], dead: [], homeopathic: [], unmeasuredJs: [], unmeasuredCss: [] };
    let capped = false;

    for (const el of candidates) {
      if (counts.probed >= MAX_PROBED) { capped = true; break; }
      if (!el.isConnected || !isRendered(el)) continue;
      const cs = getComputedStyle(el);
      if (cs.pointerEvents === 'none') continue;
      const matching = hoverRules.filter((r) => safeMatches(el, r.carrier));
      const hasStateRule = matching.length > 0;
      const hasAffordance = el.matches(NATIVE_INTERACTIVE) || cs.cursor === 'pointer';
      if (!hasStateRule && !hasAffordance && !unmeasuredCss.has(el)) continue;

      const targets = [el];
      for (const r of matching) {
        if (!r.trailing) continue;
        let hits;
        try { hits = el.querySelectorAll(r.trailing); } catch (e) { continue; }
        for (const h of Array.from(hits).slice(0, 8)) {
          if (!targets.includes(h)) targets.push(h);
        }
        if (targets.length > 12) break;
      }

      const before = targets.map(snapshotChannels);
      el.classList.add(PROBE_CLASS);
      const after = targets.map(snapshotChannels);
      el.classList.remove(PROBE_CLASS);

      let channels = null;
      for (let i = 0; i < targets.length; i++) channels = maxChannels(channels, diffChannels(before[i], after[i]));
      const cls = unmeasuredCss.has(el) || collected.unresolvedStateSelectors ? 'UNMEASURED-CSS' :
        classifyDelta({ hasStateRule, hasAffordance, pageHasJs, channels }, floors);
      if (cls === 'SKIP') continue;

      counts.probed++;
      const path = cssPath(el);
      if (cls === 'OK') {
        counts.ok++;
        if (selectors.ok.length < SELECTOR_CAP) selectors.ok.push(path);
      } else if (cls === 'DEAD') {
        counts.dead++;
        if (selectors.dead.length < SELECTOR_CAP) {
          selectors.dead.push(path);
          findings.push(finding('DEAD', path, 'pointer affordance, no state rule, zero delta — reads dead under the pointer'));
        }
      } else if (cls === 'HOMEOPATHIC') {
        counts.homeopathic++;
        if (selectors.homeopathic.length < SELECTOR_CAP) {
          selectors.homeopathic.push(path);
          findings.push(finding('HOMEOPATHIC', path,
            'state rule fires but every channel lands under the floors (scale ' + channels.scale.toFixed(3) +
            ', ΔL ' + channels.deltaL.toFixed(3) + ', translate ' + channels.translatePx.toFixed(1) +
            'px, opacity ' + channels.opacity.toFixed(2) + ') — imperceptible, not restrained'));
        }
      } else if (cls === 'UNMEASURED-JS') {
        counts.unmeasuredJs++;
        if (selectors.unmeasuredJs.length < SELECTOR_CAP) selectors.unmeasuredJs.push(path);
      } else if (cls === 'UNMEASURED-CSS') {
        counts.unmeasuredCss++;
        if (selectors.unmeasuredCss.length < SELECTOR_CAP) selectors.unmeasuredCss.push(path);
      }
    }

    styleEl.remove();

    if (counts.unmeasuredJs > 0) {
      findings.push(finding('UNMEASURED-JS', selectors.unmeasuredJs.join(', '),
        counts.unmeasuredJs + ' element(s) carry affordance with zero CSS delta — possibly JS-driven; drive each with a real hover, then awardDetector.measure(sel) (tier 2)'));
    }

    if (collected.unmeasuredRules.length) {
      findings.push(finding('UNMEASURED-CSS', selectors.unmeasuredCss.join(', '),
        'state carrier could not be derived safely; drive these targets and related controls: ' + collected.unmeasuredRules.join('; ')));
    }
    const measured = counts.probed - counts.unmeasuredJs - counts.unmeasuredCss;
    if (measured > 0 && (counts.ok === 0 || counts.dead + counts.homeopathic > measured / 2)) {
      findings.push(finding('SUBSTRATE-DEAD', 'page',
        'of ' + measured + ' measured interactive elements: ' + counts.ok + ' OK, ' + counts.dead +
        ' dead, ' + counts.homeopathic + ' homeopathic — the substrate reads dead page-wide'));
    }

    return { counts: Object.assign({ capped }, counts), selectors };
  }

  const GENERIC_FACES = ['system-ui', '-apple-system', 'blinkmacsystemfont', 'segoe ui', 'roboto',
    'arial', 'helvetica', 'helvetica neue', 'sans-serif', 'serif', 'monospace',
    'ui-sans-serif', 'ui-serif', 'ui-monospace', 'ui-rounded'];

  // fonts.check() returns true for families the browser has never heard of
  // (nothing needs loading to render their fallback), so metrics are the real
  // test: a face that renders shifts text width against at least one generic.
  const faceRenders = (() => {
    const cache = new Map();
    return (family) => {
      const key = family.toLowerCase();
      if (cache.has(key)) return cache.get(key);
      const span = document.createElement('span');
      span.style.cssText = 'position:absolute;left:-9999px;top:0;font-size:48px;visibility:hidden;white-space:pre;';
      span.textContent = 'ILlmw10Oo — Handgloves?';
      document.body.appendChild(span);
      const width = (stack) => {
        span.style.fontFamily = stack;
        return span.getBoundingClientRect().width;
      };
      let renders = false;
      for (const generic of ['monospace', 'serif', 'sans-serif']) {
        if (Math.abs(width('"' + family + '", ' + generic) - width(generic)) > 0.5) { renders = true; break; }
      }
      span.remove();
      cache.set(key, renders);
      return renders;
    };
  })();

  function checkFonts(all, face, findings) {
    if (face && !faceRenders(face)) {
      findings.push(finding('FONT-RESOLVE', 'document',
        'the committed face "' + face + '" never renders — width probe shows no metric difference against serif, sans-serif, or monospace fallbacks'));
    }
    const display = new Set(document.querySelectorAll('h1, h2'));
    for (const el of all) {
      if (hasDirectText(el) && parseFloat(getComputedStyle(el).fontSize) >= 28) display.add(el);
    }
    const seen = new Set();
    for (const el of display) {
      if (!isRendered(el)) continue;
      const family = getComputedStyle(el).fontFamily;
      const first = family.split(',')[0].trim().replace(/^["']|["']$/g, '');
      const key = first.toLowerCase();
      let reason = null;
      if (face && key !== face.toLowerCase()) reason = 'first family "' + first + '" is not the committed face "' + face + '"';
      else if (GENERIC_FACES.includes(key)) reason = 'display text commits to system/generic "' + first + '"';
      else if (!faceRenders(first)) reason = '"' + first + '" never renders — the stack silently falls through to the next family';
      if (!reason || seen.has(key + '|' + reason)) continue;
      seen.add(key + '|' + reason);
      findings.push(finding('FONT-RESOLVE', cssPath(el),
        reason + ' (font-family: ' + family.slice(0, 80) + ')'));
    }
  }

  function compositeLayers(layers, base) {
    // layers are top→bottom; composite bottom-up over the base.
    let out = base.slice();
    for (let i = layers.length - 1; i >= 0; i--) {
      const { rgb, alpha } = layers[i];
      out = out.map((v, k) => Math.round(rgb[k] * alpha + v * (1 - alpha)));
    }
    return out;
  }

  function coveringMedia(node, rect) {
    for (const media of node.querySelectorAll(':scope > video, :scope > img, :scope > canvas, :scope > picture')) {
      const r = media.getBoundingClientRect();
      if (r.left <= rect.left && r.right >= rect.right && r.top <= rect.top && r.bottom >= rect.bottom) return true;
    }
    return false;
  }

  function effectiveBackground(el, textRect) {
    const layers = [];
    let node = el;
    while (node && node.nodeType === 1) {
      const cs = getComputedStyle(node);
      if (cs.backgroundImage && cs.backgroundImage !== 'none') return { uncomputable: 'background-image on ' + cssPath(node) };
      if (textRect && node !== el && coveringMedia(node, textRect)) return { uncomputable: 'media layer under ' + cssPath(node) };
      const c = parseColor(cs.backgroundColor);
      if (c && c.alpha > 0) {
        layers.push(c);
        if (c.alpha >= 1) return { rgb: compositeLayers(layers.slice(0, -1), c.rgb) };
      }
      node = node.parentElement;
    }
    const root = parseColor(getComputedStyle(document.documentElement).backgroundColor);
    const base = root && root.alpha >= 1 && root.rgb ? root.rgb : [255, 255, 255];
    return { rgb: compositeLayers(layers, base) };
  }

  function checkContrast(all, findings) {
    let fails = 0, uncomputable = 0;
    const seenBg = new Set();
    for (const el of all) {
      if (fails >= 20 && uncomputable >= 10) break;
      if (!hasDirectText(el) || !isRendered(el)) continue;
      const cs = getComputedStyle(el);
      if (parseFloat(cs.opacity) < 0.1) continue;
      const fg = parseColor(cs.color);
      if (!fg || !fg.rgb || fg.alpha === 0) continue;
      const rect = el.getBoundingClientRect();
      const bg = effectiveBackground(el, rect);
      if (bg.uncomputable) {
        if (uncomputable < 10 && !seenBg.has(bg.uncomputable)) {
          seenBg.add(bg.uncomputable);
          uncomputable++;
          findings.push(finding('UNCOMPUTABLE-BG', cssPath(el),
            bg.uncomputable + ' — contrast unmeasurable over an image/gradient/media ground; judge it in the browser proof'));
        }
        continue;
      }
      let rgb = fg.rgb;
      if (fg.alpha < 1) rgb = rgb.map((v, k) => Math.round(v * fg.alpha + bg.rgb[k] * (1 - fg.alpha)));
      const size = parseFloat(cs.fontSize);
      const bold = parseInt(cs.fontWeight, 10) >= 700;
      const large = size >= 24 || (bold && size >= 18.66);
      const required = large ? 3 : 4.5;
      const ratio = contrastRatio(rgb, bg.rgb);
      if (ratio < required && fails < 20) {
        fails++;
        findings.push(finding('CONTRAST', cssPath(el),
          ratio.toFixed(2) + ':1 at ' + size.toFixed(1) + 'px' + (bold ? ' bold' : '') +
          ' — requires ' + required + ':1 (color ' + cs.color + ' on rgb(' + bg.rgb.join(', ') + '))'));
      }
    }
  }

  function checkNavBorder(all, findings) {
    const bars = new Set(document.querySelectorAll('header, nav'));
    for (const el of all) {
      const cs = getComputedStyle(el);
      if (cs.position !== 'fixed' && cs.position !== 'sticky') continue;
      const rect = el.getBoundingClientRect();
      if (rect.top < 100 && rect.width >= window.innerWidth * 0.6 && rect.height <= 200) bars.add(el);
    }
    for (const bar of bars) {
      if (!isRendered(bar)) continue;
      const cs = getComputedStyle(bar);
      if (!(parseFloat(cs.borderBottomWidth) > 0)) continue;
      const border = parseColor(cs.borderBottomColor);
      if (!border || border.alpha === 0) continue;
      const surface = effectiveBackground(bar, null);
      if (surface.uncomputable) continue;
      let rgb = border.rgb;
      if (!rgb) continue;
      if (border.alpha < 1) rgb = rgb.map((v, k) => Math.round(v * border.alpha + surface.rgb[k] * (1 - border.alpha)));
      const dL = Math.abs(srgbToOklab(rgb[0], rgb[1], rgb[2]).L -
        srgbToOklab(surface.rgb[0], surface.rgb[1], surface.rgb[2]).L);
      if (dL > 0.05) {
        findings.push(finding('NAV-BORDER', cssPath(bar),
          'border-bottom ' + cs.borderBottomWidth + ' ' + cs.borderBottomColor +
          ' draws a contrasting line under the bar (ΔL ' + dL.toFixed(3) + ' against its surface)'));
      } else {
        findings.push(finding('NAV-BORDER-HAIRLINE', cssPath(bar),
          'ΔL ' + dL.toFixed(3) + ' — same-ink hairline — allowed only as a written override citing the archetype palette row'));
      }
    }
  }

  // Returns the page ground rgb, or null when it is unresolvable (a ground
  // authored via background-image/gradient/wrapper, not a body/html
  // background-color). A white fallback would inflate groundDeltaL and fatally
  // fail an opaque SAME-ground bar (the winner-cited Cyd cream) whose real dark
  // ground is image-based — so the caller leaves groundDeltaL at 0 and the bar
  // reads REVIEW, matching the rule that FAIL fires only on proof.
  function pageGroundRgb() {
    for (const el of [document.body, document.documentElement]) {
      if (!el) continue;
      const c = parseColor(getComputedStyle(el).backgroundColor);
      if (c && c.alpha >= 1 && c.rgb) return c.rgb;
    }
    return null;
  }

  // A hero media surface actually passing under the bar's box: a large img /
  // video / canvas, or a url() background ground. The bar's own logo is excluded
  // (bar.contains); a small chip is excluded by the viewport-fraction floor.
  function heroMediaUnder(bar, barRect, all) {
    const intersects = (r) => r.top < barRect.bottom && r.bottom > barRect.top &&
      r.left < barRect.right && r.right > barRect.left;
    const bigEnough = (r) => r.height >= window.innerHeight * 0.3 && r.width >= window.innerWidth * 0.4;
    for (const m of document.querySelectorAll('img, video, canvas, picture')) {
      if (bar.contains(m) || !isRendered(m)) continue;
      const r = m.getBoundingClientRect();
      if (intersects(r) && bigEnough(r)) return cssPath(m);
    }
    for (const el of [document.body, document.documentElement, ...all]) {
      if (!el || bar.contains(el) || !isRendered(el)) continue;
      if (!/url\(/.test(getComputedStyle(el).backgroundImage || '')) continue;
      const r = el.getBoundingClientRect();
      if (intersects(r) && bigEnough(r)) return cssPath(el);
    }
    return null;
  }

  // NAV-HERO-OPAQUE / NAV-HERO-SURFACE: the decapitation gate. Rest-state only —
  // past scroll the bar is meant to ground, so a grounded bar there is correct
  // rather than a finding. The winner norm floats transparent over the hero
  // and gains ground at the hero's bottom; the bone strip painted from pixel 0
  // is the tell.
  function checkNavHeroSurface(all, findings) {
    if ((window.scrollY || window.pageYOffset || 0) > 1) return;
    const bars = new Set(document.querySelectorAll('header, nav'));
    for (const el of all) {
      const cs = getComputedStyle(el);
      if (cs.position !== 'fixed' && cs.position !== 'sticky') continue;
      const rect = el.getBoundingClientRect();
      if (rect.top < 100 && rect.width >= window.innerWidth * 0.6 && rect.height <= 200) bars.add(el);
    }
    const ground = pageGroundRgb();
    const groundLab = ground ? srgbToOklab(ground[0], ground[1], ground[2]) : null;
    for (const bar of bars) {
      if (!isRendered(bar)) continue;
      const cs = getComputedStyle(bar);
      if (cs.position !== 'fixed' && cs.position !== 'sticky') continue;
      const rect = bar.getBoundingClientRect();
      if (rect.top > 100 || rect.width < window.innerWidth * 0.6) continue;
      const mediaSel = heroMediaUnder(bar, rect, all);
      if (!mediaSel) continue;
      const bgImage = cs.backgroundImage && cs.backgroundImage !== 'none' ? cs.backgroundImage : '';
      // A to-transparent gradient scrim is legal: Chrome serializes the clear
      // stop as rgba(…,0) (not the "transparent" keyword), so match a zero-alpha
      // colour stop as well as the keyword / slash-0 form.
      const isScrim = cs.pointerEvents === 'none' ||
        (/gradient/.test(bgImage) &&
          /transparent|\/\s*0(?![.\d])|rgba?\([^)]*[,\s]0(?:\.0+)?\s*\)/.test(bgImage));
      const hasImage = /url\(/.test(bgImage);
      const bg = parseColor(cs.backgroundColor);
      let alpha = bg ? bg.alpha : 0;
      if (hasImage && !isScrim) alpha = 1;
      const bf = cs.backdropFilter || cs.webkitBackdropFilter || 'none';
      const hasBackdropFilter = !!bf && bf !== 'none';
      // groundDeltaL stays 0 (unprovable → REVIEW) when the page ground is
      // unresolvable or the bar surface is an image — FAIL needs a resolvable
      // solid off the ground.
      let groundDeltaL = 0;
      if (groundLab && bg && bg.rgb && !hasImage && bg.alpha > 0) {
        let rgb = bg.rgb;
        if (bg.alpha < 1) rgb = rgb.map((v, k) => Math.round(v * bg.alpha + ground[k] * (1 - bg.alpha)));
        groundDeltaL = Math.abs(srgbToOklab(rgb[0], rgb[1], rgb[2]).L - groundLab.L);
      }
      const cls = classifyNavHero({ hasMediaUnder: true, isScrim, alpha, hasBackdropFilter, groundDeltaL });
      if (cls === 'EXEMPT') continue;
      const id = cls === 'FAIL' ? 'NAV-HERO-OPAQUE' : 'NAV-HERO-SURFACE';
      findings.push(finding(id, cssPath(bar),
        'nav paints an owned surface over hero media (' + mediaSel + ') at rest — alpha ' + alpha.toFixed(2) +
        ', backdrop-filter ' + (hasBackdropFilter ? 'yes' : 'none') + ', ΔL vs ground ' + groundDeltaL.toFixed(3) +
        (cls === 'FAIL'
          ? ' — an opaque unblurred band decapitates the hero; float transparent/scrim over it, ground at the hero bottom'
          : ' — judged in §8 against the archetype canon (frost/blur, translucent, or opaque same-ground)')));
    }
  }

  function collectColorTokens() {
    const tokens = [];
    const walk = (list) => {
      for (const rule of Array.from(list)) {
        if (rule.style) {
          for (const prop of Array.from(rule.style)) {
            if (!prop.startsWith('--')) continue;
            const c = parseColor(rule.style.getPropertyValue(prop).trim());
            if (c) tokens.push({ name: prop, lab: c.lab });
          }
        }
        if (rule.cssRules && rule.cssRules.length) walk(rule.cssRules);
      }
    };
    for (const sheet of Array.from(document.styleSheets)) {
      try { if (sheet.cssRules) walk(sheet.cssRules); } catch (e) { /* opaque sheet, counted by collectStateRules */ }
    }
    return tokens;
  }

  function checkTokenConform(all, findings) {
    const tokens = collectColorTokens();
    if (tokens.length === 0) return;
    const near = (lab, t) =>
      Math.abs(lab.L - t.lab.L) < 0.01 && Math.abs(lab.a - t.lab.a) < 0.01 && Math.abs(lab.b - t.lab.b) < 0.01;
    const offenders = new Map();
    for (const el of all) {
      if (!isRendered(el)) continue;
      const cs = getComputedStyle(el);
      const values = [];
      if (hasDirectText(el)) values.push(cs.color);
      const bg = parseColor(cs.backgroundColor);
      if (bg && bg.alpha > 0) values.push(cs.backgroundColor);
      for (const value of values) {
        const c = parseColor(value);
        if (!c || c.alpha === 0 || !c.lab) continue;
        if (tokens.some((t) => near(c.lab, t))) continue;
        if (!offenders.has(value)) offenders.set(value, cssPath(el));
        if (offenders.size >= 20) break;
      }
      if (offenders.size >= 20) break;
    }
    for (const [value, selector] of offenders) {
      findings.push(finding('TOKEN-CONFORM', selector,
        'computed ' + value + ' resolves to no --* token value (' + tokens.length + ' color tokens collected)'));
    }
  }

  function checkH1Lines(findings, options) {
    if (options.h1MaxLines === 3) {
      findings.push(finding('H1-OVERRIDE', 'document',
        'canonical ceiling 2; effective ceiling 3 under the explicit client exception: ' + options.h1OverrideReason));
    }
    for (const h1 of document.querySelectorAll('h1')) {
      if (!isRendered(h1)) continue;
      const range = document.createRange();
      range.selectNodeContents(h1);
      const rects = Array.from(range.getClientRects())
        .filter((r) => r.width > 1 && r.height > 1)
        .sort((a, b) => a.top - b.top);
      let lines = 0, lastTop = -Infinity;
      for (const r of rects) {
        if (r.top - lastTop > r.height * 0.6) { lines++; lastTop = r.top; }
      }
      if (lines > options.h1MaxLines) {
        findings.push(finding('H1-LINES', cssPath(h1),
          'h1 wraps to ' + lines + ' line boxes at ' + window.innerWidth + 'px — ' + options.h1MaxLines + ' is the effective ceiling (canonical: 2)'));
      }
    }
  }

  function checkIdleChannel(findings) {
    // Under prefers-reduced-motion a silent page is the correct behavior — skip.
    if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    const running = document.getAnimations().filter((a) => {
      // A transition is interaction residue (including this run's own probe
      // retracts), never an ambient channel.
      if (typeof CSSTransition !== 'undefined' && a instanceof CSSTransition) return false;
      if (a.playState !== 'running' || a.playbackRate === 0) return false;
      const t = a.effect && a.effect.getTiming ? a.effect.getTiming() : null;
      return !!t && typeof t.duration === 'number' && t.duration > 0;
    });
    if (running.length === 0) {
      findings.push(finding('IDLE-CHANNEL', 'document',
        'no ambient channel running at rest — a running animation proves presence, not perceptibility; judge whether the page breathes'));
    }
  }

  function checkImages(findings) {
    let count = 0;
    for (const img of Array.from(document.images)) {
      if (img.complete && img.naturalWidth === 0 && count < 10) {
        count++;
        findings.push(finding('IMG-BROKEN', cssPath(img),
          'loaded but zero natural width — broken source (' + (img.currentSrc || img.src || '').slice(-80) + ')'));
      }
    }
  }

  function checkOverflow(findings) {
    const sw = document.documentElement.scrollWidth;
    if (sw > window.innerWidth + 1) {
      findings.push(finding('H-OVERFLOW', 'html',
        'scrollWidth ' + sw + 'px exceeds viewport ' + window.innerWidth + 'px — horizontal scroll'));
    }
  }

  function checkTapTargets(findings) {
    let count = 0;
    for (const el of document.querySelectorAll(NATIVE_INTERACTIVE)) {
      if (count >= 15) break;
      if (!isRendered(el)) continue;
      const rect = el.getBoundingClientRect();
      if (rect.width < 24 || rect.height < 24) {
        count++;
        findings.push(finding('TAP-TARGET', cssPath(el),
          Math.round(rect.width) + '×' + Math.round(rect.height) + ' CSS px at ' + window.innerWidth +
          'px — under the 24×24 floor; 44×44 is the target'));
      }
    }
  }

  function markCells(rect, sec, grid, cols, rows) {
    const top = rect.top + window.scrollY - sec.top;
    const left = rect.left + window.scrollX - sec.left;
    const x0 = Math.max(0, left), y0 = Math.max(0, top);
    const x1 = Math.min(sec.w, left + rect.width), y1 = Math.min(sec.h, top + rect.height);
    if (x1 <= x0 || y1 <= y0) return;
    const c0 = Math.floor(x0 / sec.w * cols), c1 = Math.min(cols, Math.ceil(x1 / sec.w * cols));
    const r0 = Math.floor(y0 / sec.h * rows), r1 = Math.min(rows, Math.ceil(y1 / sec.h * rows));
    for (let r = r0; r < r1; r++) for (let c = c0; c < c1; c++) grid[r][c] = 1;
  }

  function liveMedium(el) {
    if (!isRendered(el)) return false;
    const cs = getComputedStyle(el);
    if (parseFloat(cs.opacity) < 0.6) return false;  // the occluded / near-invisible bed carries nothing
    if (el.tagName === 'VIDEO') return !el.paused || el.readyState >= 2;
    return true;
  }

  // SECTION-DEAD — the "empty and dead" beat. Rasterize each tall top-level
  // section, mark cells that carry text or a perceptible medium, and flag when
  // the largest empty rectangle swallows most of it: sparse text stranded in a
  // corner over a void is what a code-read misses and what reads as dead on screen.
  function checkSectionDead(findings) {
    const vh = window.innerHeight, cols = 24;
    for (const section of document.querySelectorAll('section, article')) {
      if (section.parentElement && section.parentElement.closest('section, article')) continue;
      const r = section.getBoundingClientRect();
      if (r.width < 1 || r.height < vh * VOID_FLOORS.sectionMinVh) continue;
      const rows = Math.max(6, Math.min(160, Math.round(cols * r.height / r.width)));
      const grid = Array.from({ length: rows }, () => new Array(cols).fill(0));
      const sec = { top: r.top + window.scrollY, left: r.left + window.scrollX, w: r.width, h: r.height };
      for (const el of section.querySelectorAll('*')) {
        if (hasDirectText(el) && isRendered(el)) markCells(el.getBoundingClientRect(), sec, grid, cols, rows);
      }
      for (const el of section.querySelectorAll('img, video, canvas, picture, svg, [style*="background-image"]')) {
        if (liveMedium(el)) markCells(el.getBoundingClientRect(), sec, grid, cols, rows);
      }
      const emptyFraction = largestEmptyFraction(grid);
      if (classifyVoid({ heightVh: r.height / vh, emptyFraction }, VOID_FLOORS) === 'DEAD') {
        findings.push(finding('SECTION-DEAD', cssPath(section),
          (r.height / vh).toFixed(1) + 'vp tall and ' + Math.round(emptyFraction * 100) +
          '% of it is one continuous empty void — a rich page carries a figure or motion into its longest beats, not text stranded in a corner'));
      }
    }
  }

  async function run(options) {
    options = runOptions(options);  // validate before any DOM read or mutation
    const floors = options.floors;
    await document.fonts.ready;
    const findings = [];
    const all = Array.from(document.querySelectorAll('body *')).slice(0, MAX_SCAN);

    checkFonts(all, options.face, findings);
    // Idle first: probing leaves retract transitions behind that would read
    // as motion at rest.
    checkIdleChannel(findings);
    const collected = collectStateRules();
    // Under touch emulation the :hover probes are void — a touch-gated build
    // hides its hover rules behind (hover: hover) and would read dead here,
    // so SUBSTRATE-DEAD never fires on this pass. The touch channel is judged
    // by driving real taps (tier 2), never by run().
    const hoverNone = matchMedia('(hover: none)').matches;
    const substrate = hoverNone ? null : probeSubstrate(collected, floors, findings);
    checkContrast(all, findings);
    checkNavBorder(all, findings);
    checkNavHeroSurface(all, findings);
    checkTokenConform(all, findings);
    checkH1Lines(findings, options);
    checkImages(findings);
    checkOverflow(findings);
    checkTapTargets(findings);
    checkSectionDead(findings);

    return {
      detector: 'award-design',
      version: 1,
      viewport: { w: window.innerWidth, h: window.innerHeight },
      options,
      policy: { canonicalFloors: Object.assign({}, FLOORS), canonicalH1MaxLines: 2,
        floorsOverridden: Object.keys(FLOORS).some((key) => floors[key] !== FLOORS[key]),
        h1Overridden: options.h1MaxLines === 3 },
      findings,
      substrate: hoverNone ? {
        skipped: 'touch emulation — hover probes void; judge the touch channel by driving taps (tier 2)'
      } : {
        probed: substrate.counts.probed,
        ok: substrate.counts.ok,
        dead: substrate.counts.dead,
        homeopathic: substrate.counts.homeopathic,
        unmeasuredJs: substrate.counts.unmeasuredJs,
        unmeasuredCss: substrate.counts.unmeasuredCss,
        capped: substrate.counts.capped,
        selectors: substrate.selectors
      },
      coverage: { sheets: collected.sheets, opaqueSheets: collected.opaqueSheets, probedRules: collected.rules.length,
        unmeasuredStateRules: collected.unmeasuredRules.length, unresolvedStateSelectors: collected.unresolvedStateSelectors },
      footer: FOOTER
    };
  }

  function classifyMeasured(channels) {
    const cls = classifyDelta({ hasStateRule: true, hasAffordance: true, channels });
    return cls === 'HOMEOPATHIC' && channels.scale === 1 && channels.translatePx === 0 &&
      channels.deltaL === 0 && channels.opacity === 0 ? 'DEAD' : cls;
  }

  // Tier-2 helper: first call stores the rest snapshot; after the real hover is
  // driven by the tooling, the second call diffs against it.
  function measure(selector) {
    const el = document.querySelector(selector);
    if (!el) return { selector, error: 'no element matches' };
    window.__adRest = window.__adRest || {};
    if (!window.__adRest[selector]) {
      window.__adRest[selector] = snapshotChannels(el);
      return { selector, rest: true, note: 'rest snapshot stored — drive the real hover, then call measure again' };
    }
    const channels = diffChannels(window.__adRest[selector], snapshotChannels(el));
    return { selector, channels, classification: classifyMeasured(channels) };
  }

  // rAF-samples every pair against its rest snapshot for windowMs and folds
  // the per-channel max — a transient is caught at its crest, where a
  // post-settle read measures zero.
  function samplePeak(pairs, windowMs) {
    return new Promise((resolve) => {
      const peaks = pairs.map(() => null);
      const start = performance.now();
      let frames = 0, raf;
      const finish = () => {
        cancelAnimationFrame(raf);
        clearTimeout(timeout);
        resolve({ peaks, frames });
      };
      const timeout = setTimeout(finish, windowMs + 100);
      const tick = () => {
        for (let i = 0; i < pairs.length; i++) {
          peaks[i] = peakChannels(peaks[i], diffChannels(pairs[i].rest, snapshotChannels(pairs[i].el)));
        }
        frames++;
        if (performance.now() - start < windowMs) raf = requestAnimationFrame(tick);
        else finish();
      };
      raf = requestAnimationFrame(tick);
    });
  }

  // Arm before the real input. The second call reads the stored sampling
  // promise, so a transient that settled between tool calls is not lost.
  async function measurePeak(selector, windowMs, trigger) {
    if (windowMs !== undefined && (!Number.isFinite(windowMs) || windowMs <= 0)) {
      return { selector, error: 'windowMs must be a positive finite number' };
    }
    trigger = trigger === undefined ? 'pointerdown' : trigger;
    if (!['pointerdown', 'pointerenter', 'keydown', 'click'].includes(trigger)) {
      return { selector, error: 'trigger must be pointerdown, pointerenter, keydown or click' };
    }
    const el = document.querySelector(selector);
    if (!el) return { selector, error: 'no element matches' };
    window.__adPeak = window.__adPeak || {};
    const entry = window.__adPeak[selector];
    if (!entry) {
      const armed = { rest: snapshotChannels(el), done: null, event: null, windowMs: windowMs || PEAK_WINDOW_MS };
      const start = (event) => {
        armed.event = event.type;
        armed.done = samplePeak([{ el, rest: armed.rest }], armed.windowMs);
      };
      el.addEventListener(trigger, start, { once: true });
      window.__adPeak[selector] = armed;
      return { selector, armed: true, trigger, windowMs: armed.windowMs,
        note: 'rest stored; sampler armed on ' + trigger + ' — drive the real input, then call measurePeak again' };
    }
    if (!entry.done) return { selector, error: 'armed but no input landed — drive a real hover, press or key, then read again' };
    const result = await entry.done;
    delete window.__adPeak[selector];
    if (!result.frames) return { selector, error: 'no animation frames sampled; repeat in a visible foreground page' };
    const channels = result.peaks[0];
    return { selector, channels, frames: result.frames, event: entry.event, windowMs: entry.windowMs,
      classification: classifyMeasured(channels) };
  }

  // Contact protocol: the first call stores rest snapshots for the object and
  // each declared secondary, then arms the peak sampler on the object's next
  // pointerdown — sampling starts the instant the real press lands, so
  // tool-call latency between the click and the read never loses the
  // transient. The second call reads the peaks and classifies.
  async function measureContact(selector, options) {
    options = options || {};
    const el = document.querySelector(selector);
    if (!el) return { selector, error: 'no element matches' };
    window.__adContact = window.__adContact || {};
    const entry = window.__adContact[selector];
    if (!entry) {
      const names = options.secondaries || [];
      const pairs = [{ el, rest: snapshotChannels(el) }];
      for (const name of names) {
        const sec = document.querySelector(name);
        if (!sec) return { selector, error: 'no element matches secondary "' + name + '"' };
        pairs.push({ el: sec, rest: snapshotChannels(sec) });
      }
      const armed = { pairs, secondaries: names, done: null, windowMs: options.windowMs || PEAK_WINDOW_MS };
      el.addEventListener('pointerdown', () => { armed.done = samplePeak(armed.pairs, armed.windowMs); }, { once: true });
      window.__adContact[selector] = armed;
      return { selector, armed: true, secondaries: names,
        note: 'rest stored, sampler armed on pointerdown — drive a real click/press on the object, then call measureContact again' };
    }
    if (!entry.done) return { selector, error: 'armed but no press landed on the object — drive a real click/press, then read again' };
    const result = await entry.done;
    delete window.__adContact[selector];
    if (!result.frames) return { selector, error: 'no animation frames sampled; repeat in a visible foreground page' };
    const object = result.peaks[0];
    const secondaries = entry.secondaries.map((name, i) => ({ selector: name, channels: result.peaks[i + 1] }));
    if (el.matches('canvas') || el.querySelector('canvas')) {
      return { selector, channels: object, secondaries, frames: result.frames, classification: 'CANVAS',
        evidence: 'canvas medium — pixels are invisible to computed style, so the deformation stays judgment: drive the press and watch' };
    }
    const cls = classifyContact(object, secondaries.map((s) => s.channels));
    const out = { selector, channels: object, secondaries, frames: result.frames, classification: cls };
    if (cls === 'GLOBAL-SQUASH') {
      out.finding = finding('CONTACT-GLOBAL-SQUASH', selector,
        'peak contact response is a whole-element scale ' + object.scale.toFixed(3) + ' / opacity ' +
        object.opacity.toFixed(2) + ' and nothing else — no secondary above a floor, no structural channel: the paper-cutout squash');
    }
    return out;
  }

  window.awardDetector = Object.assign({}, api, { run, measure, measurePeak, measureContact });
})();
