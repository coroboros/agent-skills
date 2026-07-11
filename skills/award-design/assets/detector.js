/* award-design in-page detector — probes state rules and measures computed deltas
   so "perceptible" is a number, not a code-read. Catches, never clears. */
(() => {
  'use strict';

  const FLOORS = { scale: 1.04, deltaL: 0.04, translatePx: 2, opacity: 0.1 };

  const RULES = [
    { id: 'FONT-RESOLVE', severity: 'FAIL', box: 'computed-face' },
    { id: 'SUBSTRATE-DEAD', severity: 'FAIL', box: 'live-substrate' },
    { id: 'DEAD', severity: 'REVIEW', box: 'live-substrate' },
    { id: 'HOMEOPATHIC', severity: 'REVIEW', box: 'live-substrate' },
    { id: 'UNMEASURED-JS', severity: 'REVIEW', box: 'live-substrate' },
    { id: 'CONTRAST', severity: 'FAIL', box: 'a11y-floor' },
    { id: 'UNCOMPUTABLE-BG', severity: 'REVIEW', box: 'a11y-floor' },
    { id: 'NAV-BORDER', severity: 'FAIL', box: 'nav-surface' },
    { id: 'NAV-BORDER-HAIRLINE', severity: 'REVIEW', box: 'nav-surface' },
    { id: 'TOKEN-CONFORM', severity: 'REVIEW', box: 'token-drift' },
    { id: 'H1-LINES', severity: 'FAIL', box: 'hero-h1-lines' },
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
  const EPS = 1e-4;

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
  // and nav-border need rgb, so the inverse transform is not optional.
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

  // sample = { hasStateRule, hasAffordance, pageHasJs, channels }.
  // Channels without a floor (box-shadow, clip-path, pseudo appear/vanish) count
  // as perceptible when they change at all — they are structural, not gradual.
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

  const api = { FLOORS, RULES, srgbToOklab, relativeLuminance, contrastRatio, parseColor, parseTransform, classifyDelta, diffChannels };

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

  const STATE_PSEUDO = /:hover|:focus-visible/;

  // carrier = the compound that carries :hover (the element the pointer touches);
  // trailing = the rest of the selector (the descendant that responds).
  function splitCarrier(selector) {
    const idx = selector.search(STATE_PSEUDO);
    let end = selector.length;
    let depth = 0;
    for (let i = idx; i < selector.length; i++) {
      const c = selector[i];
      if (c === '(' || c === '[') depth++;
      else if (c === ')' || c === ']') depth--;
      else if (depth === 0 && (c === ' ' || c === '>' || c === '+' || c === '~')) { end = i; break; }
    }
    const strip = (s) => s.replace(/:hover|:focus-visible/g, '').replace(/::?[a-z-]+(\([^)]*\))?$/i, '').trim();
    let carrier = strip(selector.slice(0, end));
    if (!carrier) carrier = '*';
    let trailing = selector.slice(end).replace(/^[\s>+~]+/, '').trim();
    if (trailing) trailing = trailing.replace(/::[a-z-]+(\([^)]*\))?/gi, '').trim();
    return { carrier, trailing };
  }

  function collectStateRules() {
    const rules = [];
    let sheets = 0, opaqueSheets = 0;
    const walk = (list) => {
      for (const rule of Array.from(list)) {
        if (rule.styleSheet) {
          // @import — the nested sheet never appears in document.styleSheets.
          try { walk(rule.styleSheet.cssRules); } catch (e) { opaqueSheets++; }
          continue;
        }
        if (rule.selectorText !== undefined && rule.style) {
          const sel = rule.selectorText;
          if (!STATE_PSEUDO.test(sel)) continue;
          for (const part of splitSelectors(sel)) {
            if (!STATE_PSEUDO.test(part)) continue;
            const { carrier, trailing } = splitCarrier(part);
            const probeSelector = part.replace(/:hover|:focus-visible/g, '.' + PROBE_CLASS);
            rules.push({ selector: part, probeSelector, carrier, trailing, css: rule.style.cssText });
          }
          continue;
        }
        if (rule.cssRules && rule.cssRules.length) {
          if (rule.media && !matchMedia(rule.conditionText).matches) continue;
          if (typeof CSSSupportsRule !== 'undefined' && rule instanceof CSSSupportsRule) {
            try { if (!CSS.supports(rule.conditionText)) continue; } catch (e) { /* keep walking */ }
          }
          if (typeof CSSKeyframesRule !== 'undefined' && rule instanceof CSSKeyframesRule) continue;
          walk(rule.cssRules);
        }
      }
    };
    for (const sheet of Array.from(document.styleSheets)) {
      sheets++;
      let list;
      // Cross-origin sheets throw on cssRules access — count them, never skip silently.
      try { list = sheet.cssRules; } catch (e) { opaqueSheets++; continue; }
      if (list) walk(list);
    }
    return { rules, sheets, opaqueSheets };
  }

  function safeMatches(el, selector) {
    try { return el.matches(selector); } catch (e) { return false; }
  }

  function probeSubstrate(collected, floors, findings) {
    const pageHasJs = document.scripts.length > 0;
    const styleEl = document.createElement('style');
    styleEl.id = PROBE_STYLE_ID;
    // The kill rule is load-bearing: without it a transitioned property reads
    // its rest value on the immediate post-probe snapshot and every hover
    // measures zero.
    styleEl.textContent = collected.rules.map((r) => r.probeSelector + ' { ' + r.css + ' }').join('\n') +
      '\n.' + PROBE_CLASS + ', .' + PROBE_CLASS + ' *, .' + PROBE_CLASS + '::before, .' +
      PROBE_CLASS + '::after, .' + PROBE_CLASS + ' *::before, .' + PROBE_CLASS +
      ' *::after { transition: none !important; }';
    const prior = document.getElementById(PROBE_STYLE_ID);
    if (prior) prior.remove();
    document.head.appendChild(styleEl);

    const candidates = new Set(document.querySelectorAll(NATIVE_INTERACTIVE));
    for (const r of collected.rules) {
      if (r.carrier === '*' || r.carrier === 'html' || r.carrier === 'body') continue;
      try { document.querySelectorAll(r.carrier).forEach((el) => candidates.add(el)); } catch (e) { /* invalid derived selector */ }
    }

    const counts = { probed: 0, ok: 0, dead: 0, homeopathic: 0, unmeasuredJs: 0 };
    const selectors = { ok: [], dead: [], homeopathic: [], unmeasuredJs: [] };
    let capped = false;

    for (const el of candidates) {
      if (counts.probed >= MAX_PROBED) { capped = true; break; }
      if (!el.isConnected || !isRendered(el)) continue;
      const cs = getComputedStyle(el);
      if (cs.pointerEvents === 'none') continue;
      const matching = collected.rules.filter((r) => safeMatches(el, r.carrier));
      const hasStateRule = matching.length > 0;
      const hasAffordance = el.matches(NATIVE_INTERACTIVE) || cs.cursor === 'pointer';
      if (!hasStateRule && !hasAffordance) continue;

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
      const cls = classifyDelta({ hasStateRule, hasAffordance, pageHasJs, channels }, floors);
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
      }
    }

    styleEl.remove();

    if (counts.unmeasuredJs > 0) {
      findings.push(finding('UNMEASURED-JS', selectors.unmeasuredJs.join(', '),
        counts.unmeasuredJs + ' element(s) carry affordance with zero CSS delta — possibly JS-driven; drive each with a real hover, then awardDetector.measure(sel) (tier 2)'));
    }

    const measured = counts.probed - counts.unmeasuredJs;
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

  function checkH1Lines(findings) {
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
      if (lines > 2) {
        findings.push(finding('H1-LINES', cssPath(h1),
          'h1 wraps to ' + lines + ' line boxes at ' + window.innerWidth + 'px — 2 is the committed ceiling'));
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

  async function run(options) {
    options = options || {};
    const floors = Object.assign({}, FLOORS, options.floors || {});
    await document.fonts.ready;
    const findings = [];
    const all = Array.from(document.querySelectorAll('body *')).slice(0, MAX_SCAN);

    checkFonts(all, options.face, findings);
    // Idle first: probing leaves retract transitions behind that would read
    // as motion at rest.
    checkIdleChannel(findings);
    const collected = collectStateRules();
    const substrate = probeSubstrate(collected, floors, findings);
    checkContrast(all, findings);
    checkNavBorder(all, findings);
    checkTokenConform(all, findings);
    checkH1Lines(findings);
    checkImages(findings);
    checkOverflow(findings);
    checkTapTargets(findings);

    return {
      detector: 'award-design',
      version: 1,
      viewport: { w: window.innerWidth, h: window.innerHeight },
      options: { face: options.face || null, archetype: options.archetype || null },
      findings,
      substrate: {
        probed: substrate.counts.probed,
        ok: substrate.counts.ok,
        dead: substrate.counts.dead,
        homeopathic: substrate.counts.homeopathic,
        unmeasuredJs: substrate.counts.unmeasuredJs,
        capped: substrate.counts.capped,
        selectors: substrate.selectors
      },
      coverage: { sheets: collected.sheets, opaqueSheets: collected.opaqueSheets, probedRules: collected.rules.length },
      footer: FOOTER
    };
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
    const cls = classifyDelta({ hasStateRule: true, hasAffordance: true, channels });
    return { selector, channels, classification: cls === 'HOMEOPATHIC' && channels.scale === 1 &&
      channels.translatePx === 0 && channels.deltaL === 0 && channels.opacity === 0 ? 'DEAD' : cls };
  }

  window.awardDetector = Object.assign({}, api, { run, measure });
})();
