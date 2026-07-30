/* award-design pixel metrics — EVIDENCE ONLY. No severities and no verdicts:
   every number here is a theory-class observation handed to the judge, who
   decides what it means. A rule that could FAIL belongs in render-floor.js.

   It is not threshold-free, and pretending otherwise would be its own dishonesty:
   GRID.emptyCell, GRID.groundCoverage, COLOR.matchTol, ACCENT.oklabTol /
   .minChroma / .minOccurrences and MOTION.rectEps / .opacityEps all shape the
   numbers below. Every one is a REPORTING parameter — it decides what gets
   counted, never whether the page passes — and each ships in the output beside
   the count it produced, so a reader can re-derive or discount it.

   Sweep protocol. The harness owns the browser: it injects this file, and after
   each resize calls run(). This payload never opens a browser, never resizes
   one, never navigates, never touches the network. It scrolls exactly once — a
   single programmatic step for the scroll proxy — and puts the page back where
   it found it.

     const evidence = await awardPixelMetrics.run();
     await awardPixelMetrics.run({ accent: '#b34700', idleMs: 4000 });

   run() takes idleMs (default 3000) to sample the page at rest, so a full call
   is roughly four seconds by design.

   What each metric measures — the provenance is a failed reference build, where
   the desire read was "the argument underneath is better than Terminal's; the
   page is not", and the gaps were all distributional:

     quadrantEmptiness  a 12×13 grid over the whole page; the coverage of each
                        of the 156 cells. That build: 28 cells effectively
                        empty, and the eye reads that as unfinished.
     inkProfile         covered-area share per viewport-height band. It ran
                        8.2%–15.1% across 13 bands — a metronome, no climax,
                        no rest, the same density everywhere.
     groundCommitment   the share of painted background area held by the single
                        dominant colour. That build held 26.7% against the
                        exemplar's 84.7%: a page that never commits to a ground.
     accentFrequency    how many elements per viewport band carry the accent.
                        It fired its blue 3–5× per viewport against its own
                        one-per-viewport spec, so the accent meant CTA and
                        link and focus and emphasis and stat simultaneously.
     idleDelta          how many animated candidates move measurably while the
                        page sits untouched.
     scrollDelta        how many move differently from the page under one
                        programmatic scroll step (parallax, scroll-driven work).

   Honest limits. True pixel-diff belongs to harness screenshots; idleDelta and
   scrollDelta are DOM proxies that see geometry, transform and opacity only.
   Everything painted inside a <canvas> or a <video> is invisible to them, and
   both metrics say so on their own output line. Their candidate set is what the
   DOM declares: Web Animations targets, canvas/video, a non-auto will-change, an
   animation-name, or a non-none transform. That last one is what catches a rAF
   tween library — GSAP and the scroll-smoothing libraries register no animation
   and no animation-name, and are visible here only through the inline transforms
   they write, so an element they move without a transform is missed. A hijacked
   or smoothed scroller may not honour a programmatic step — scrollDelta reports
   the pixels it actually moved, so a zero there means the instrument, not the
   page. Fixed and sticky subtrees sit out the motion proxies: they move against
   the page by construction. The raster places fixed elements at the offset held
   when run() was called. Coverage is per-cell occupancy, not painted alpha: a
   1px hairline crossing a cell fills it. Colours are compared in OKLab; this
   payload never needs the sRGB inverse, so it does not carry one. */
(() => {
  'use strict';

  const GRID = { quadCols: 12, quadRows: 13, rasterCols: 120, maxRasterRows: 1200, emptyCell: 0.02, groundCoverage: 0.9 };
  // Two tolerances, two jobs. COLOR.matchTol decides "is this the same colour"
  // for ground identity and ink; ACCENT.oklabTol decides "does this element
  // carry the accent". Sharing one constant meant retuning the accent silently
  // moved quadrantEmptiness and inkProfile.
  const COLOR = { matchTol: 0.02 };
  const ACCENT = { oklabTol: 0.04, minOccurrences: 3, minChroma: 0.04 };
  const MOTION = { idleMs: 3000, scrollFraction: 0.5, settleMs: 250, maxCandidates: 200, rectEps: 0.5, opacityEps: 0.01 };
  const METHOD = 'dom-geometry-proxy';
  const PROXY_NOTE = 'canvas/video internals invisible to this proxy';
  const FOOTER = 'Evidence only — no severities, no verdicts. Every number is a DOM-geometry proxy for a pixel fact; the judge decides what it means.';
  const MEDIA = 'img, video, canvas, svg, picture, iframe';
  const NON_LAYOUT = 'script, style, noscript, template, title, meta, link, option, optgroup, defs, clipPath, mask, pattern, symbol, marker';
  const MAX_SCAN = 5000;

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

  // Returns { alpha, lab } or null when unparsable. Chrome serializes
  // oklch()-authored computed colours as oklch(…), so the parser has to read
  // both families; the lab comes straight off the oklch/oklab tokens.
  function parseColor(input) {
    if (typeof input !== 'string') return null;
    const str = input.trim().toLowerCase();
    if (!str || str === 'none' || str === 'currentcolor' || str.startsWith('var(')) return null;
    if (str === 'transparent') return { alpha: 0, lab: { L: 0, a: 0, b: 0 } };
    if (str === 'white') return { alpha: 1, lab: srgbToOklab(255, 255, 255) };
    if (str === 'black') return { alpha: 1, lab: srgbToOklab(0, 0, 0) };
    const pct = (v) => (v.endsWith('%') ? parseFloat(v) / 100 : +v);
    let m = str.match(/^#([0-9a-f]{3,8})$/);
    if (m) {
      let hex = m[1];
      if (hex.length <= 4) hex = hex.split('').map((c) => c + c).join('');
      const alpha = hex.length === 8 ? parseInt(hex.slice(6, 8), 16) / 255 : 1;
      return { alpha, lab: srgbToOklab(parseInt(hex.slice(0, 2), 16), parseInt(hex.slice(2, 4), 16), parseInt(hex.slice(4, 6), 16)) };
    }
    m = str.match(/^rgba?\(\s*([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)(?:\s*[,/]\s*([\d.]+%?))?\s*\)$/);
    if (m) return { alpha: m[4] === undefined ? 1 : pct(m[4]), lab: srgbToOklab(+m[1], +m[2], +m[3]) };
    m = str.match(/^hsla?\(\s*([\d.-]+)(?:deg)?[,\s]+([\d.]+)%[,\s]+([\d.]+)%(?:\s*[,/]\s*([\d.]+%?))?\s*\)$/);
    if (m) {
      const rgb = hslToRgb(+m[1], +m[2] / 100, +m[3] / 100);
      return { alpha: m[4] === undefined ? 1 : pct(m[4]), lab: srgbToOklab(rgb[0], rgb[1], rgb[2]) };
    }
    m = str.match(/^oklch\(\s*([\d.]+%?)\s+([\d.]+%?)\s+([\d.-]+)(?:deg)?\s*(?:\/\s*([\d.]+%?))?\s*\)$/);
    if (m) {
      const C = m[2].endsWith('%') ? parseFloat(m[2]) * 0.004 : +m[2];
      const H = (+m[3] * Math.PI) / 180;
      return { alpha: m[4] === undefined ? 1 : pct(m[4]), lab: { L: pct(m[1]), a: C * Math.cos(H), b: C * Math.sin(H) } };
    }
    m = str.match(/^oklab\(\s*([\d.]+%?)\s+([\d.-]+)\s+([\d.-]+)\s*(?:\/\s*([\d.]+%?))?\s*\)$/);
    if (m) return { alpha: m[4] === undefined ? 1 : pct(m[4]), lab: { L: pct(m[1]), a: +m[2], b: +m[3] } };
    m = str.match(/^color\(srgb\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*(?:\/\s*([\d.]+%?))?\s*\)$/);
    if (m) return { alpha: m[4] === undefined ? 1 : pct(m[4]), lab: srgbToOklab(+m[1] * 255, +m[2] * 255, +m[3] * 255) };
    return null;
  }

  function oklabDistance(a, b) {
    if (!a || !b) return Infinity;
    return Math.sqrt(Math.pow(a.L - b.L, 2) + Math.pow(a.a - b.a, 2) + Math.pow(a.b - b.b, 2));
  }

  function chroma(lab) {
    return lab ? Math.hypot(lab.a, lab.b) : 0;
  }

  // Occupancy raster over a document-space box. A cell is marked when any rect
  // touches it — the same coarse-ink convention the detector's void grid uses,
  // so the two instruments agree on what "covered" means.
  function rasterize(rects, box, cols, rows) {
    const cells = new Uint8Array(Math.max(0, cols * rows));
    if (cols <= 0 || rows <= 0 || box.w <= 0 || box.h <= 0) return cells;
    for (const rect of rects) {
      const x0 = Math.max(0, rect.left - box.left);
      const y0 = Math.max(0, rect.top - box.top);
      const x1 = Math.min(box.w, rect.left - box.left + rect.width);
      const y1 = Math.min(box.h, rect.top - box.top + rect.height);
      if (x1 <= x0 || y1 <= y0) continue;
      const c0 = Math.floor((x0 / box.w) * cols), c1 = Math.min(cols, Math.ceil((x1 / box.w) * cols));
      const r0 = Math.floor((y0 / box.h) * rows), r1 = Math.min(rows, Math.ceil((y1 / box.h) * rows));
      for (let r = r0; r < r1; r++) for (let c = c0; c < c1; c++) cells[r * cols + c] = 1;
    }
    return cells;
  }

  function blockCoverage(cells, cols, r0, r1, c0, c1) {
    let covered = 0, total = 0;
    for (let r = r0; r < r1; r++) {
      for (let c = c0; c < c1; c++) { total++; if (cells[r * cols + c]) covered++; }
    }
    return total ? covered / total : 0;
  }

  function distribution(values) {
    if (!values.length) return null;
    const s = values.slice().sort((a, b) => a - b);
    const at = (q) => s[Math.round(q * (s.length - 1))];
    return {
      min: s[0], p25: at(0.25), median: at(0.5), p75: at(0.75), max: s[s.length - 1],
      mean: s.reduce((acc, v) => acc + v, 0) / s.length
    };
  }

  // The motion proxies' one comparison. shiftY undoes a programmatic scroll: a
  // static element's viewport y drops by exactly the pixels the page moved, so
  // anything left over is the element moving against the page.
  function delta(a, b, shiftY) {
    const dx = Math.abs(b.x - a.x);
    const dy = Math.abs(b.y + (shiftY || 0) - a.y);
    const dw = Math.abs(b.w - a.w);
    const dh = Math.abs(b.h - a.h);
    const dOpacity = Math.abs(parseFloat(b.opacity) - parseFloat(a.opacity)) || 0;
    const transformChanged = a.transform !== b.transform;
    return {
      dx, dy, dw, dh, dOpacity, transformChanged,
      moved: dx > MOTION.rectEps || dy > MOTION.rectEps || dw > MOTION.rectEps ||
        dh > MOTION.rectEps || dOpacity > MOTION.opacityEps || transformChanged
    };
  }

  // Folds background entries that are the same colour authored two ways. Chrome
  // serializes an oklch()-authored ground as oklch(…) and a hex-authored one as
  // rgb(…), so keying on the computed string alone splits one ground in two and
  // halves the headline share the judge reads.
  function mergeByColor(entries, tol) {
    const limit = typeof tol === 'number' ? tol : COLOR.matchTol;
    const merged = [];
    for (const entry of entries.slice().sort((a, b) => b.area - a.area)) {
      const host = merged.find((m) => oklabDistance(m.lab, entry.lab) <= limit);
      if (!host) {
        merged.push({ color: entry.color, lab: entry.lab, area: entry.area,
          elements: entry.elements, aliases: [] });
        continue;
      }
      host.area += entry.area;
      host.elements += entry.elements;
      if (host.aliases.indexOf(entry.color) === -1) host.aliases.push(entry.color);
    }
    return merged.sort((a, b) => b.area - a.area);
  }

  const api = { GRID, COLOR, ACCENT, MOTION, METHOD, srgbToOklab, parseColor, oklabDistance,
    chroma, mergeByColor, rasterize, blockCoverage, distribution, delta };

  if (typeof window === 'undefined') {
    if (typeof module !== 'undefined' && module.exports) module.exports = api;
    return;
  }

  // ------------------------------------------------------------ browser layer

  const r3 = (n) => Math.round(n * 1000) / 1000;
  const KILL_STYLE_ID = '__ad-pm-kill';
  const CHECK_VIS = { visibilityProperty: true, opacityProperty: true, contentVisibilityAuto: true };

  function isVisible(el) {
    if (typeof el.checkVisibility === 'function') return el.checkVisibility(CHECK_VIS);
    const cs = getComputedStyle(el);
    return cs.display !== 'none' && cs.visibility !== 'hidden' && parseFloat(cs.opacity) >= 0.05;
  }

  function hasDirectText(el) {
    for (const node of el.childNodes) {
      if (node.nodeType === 3 && node.textContent.trim().length > 0) return true;
    }
    return false;
  }

  function cssPath(el) {
    const parts = [];
    let node = el;
    while (node && node.nodeType === 1 && node !== document.body && parts.length < 3) {
      let part = node.tagName.toLowerCase();
      if (node.id) { parts.unshift(part + '#' + node.id); break; }
      const cls = Array.from(node.classList || []).slice(0, 2);
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

  function makeFixedCheck() {
    const memo = new Map();
    const check = (node) => {
      if (!node || node.nodeType !== 1) return false;
      if (memo.has(node)) return memo.get(node);
      const p = getComputedStyle(node).position;
      const v = p === 'fixed' || p === 'sticky' || check(node.parentElement);
      memo.set(node, v);
      return v;
    };
    return check;
  }

  function docBox() {
    const de = document.documentElement;
    return {
      left: 0, top: 0,
      w: Math.max(de.scrollWidth, window.innerWidth, 1),
      h: Math.max(de.scrollHeight, window.innerHeight, 1)
    };
  }

  function collect() {
    const all = document.body.querySelectorAll('*');
    const nodes = Array.from(all).slice(0, MAX_SCAN);
    const records = [];
    // The cap truncates the PRE-filter node list, so it is reported against that
    // count; comparing surviving records to it would call a truncated raster
    // complete on any page over the cap.
    records.elementsSeen = all.length;
    records.capped = all.length > MAX_SCAN;
    for (const el of [document.documentElement, document.body].concat(nodes)) {
      if (el.closest && el.closest(NON_LAYOUT)) continue;
      if (el !== document.documentElement && !isVisible(el)) continue;
      const r = el.getBoundingClientRect();
      if (r.width <= 0 || r.height <= 0) continue;
      const cs = getComputedStyle(el);
      records.push({
        el, cs,
        rect: { left: r.left + window.scrollX, top: r.top + window.scrollY, width: r.width, height: r.height },
        bg: parseColor(cs.backgroundColor),
        bgImage: !!cs.backgroundImage && cs.backgroundImage !== 'none',
        text: hasDirectText(el),
        media: el.matches(MEDIA)
      });
    }
    return records;
  }

  function groundCommitment(records, docArea) {
    const byColor = new Map();
    let painted = 0, imageArea = 0;
    for (const rec of records) {
      const area = rec.rect.width * rec.rect.height;
      if (rec.bgImage) imageArea += area;
      if (!rec.bg || rec.bg.alpha <= 0) continue;
      painted += area;
      const key = rec.cs.backgroundColor;
      const entry = byColor.get(key) || { color: key, lab: rec.bg.lab, area: 0, elements: 0 };
      entry.area += area;
      entry.elements += 1;
      byColor.set(key, entry);
    }
    const sorted = mergeByColor(Array.from(byColor.values()));
    return {
      method: METHOD,
      dominant: sorted.length ? sorted[0].color : null,
      dominantShare: sorted.length && painted ? r3(sorted[0].area / painted) : 0,
      dominantLab: sorted.length ? sorted[0].lab : null,
      top3: sorted.slice(0, 3).map((e) => ({
        color: e.color, aliases: e.aliases, share: painted ? r3(e.area / painted) : 0,
        areaPx2: Math.round(e.area), elements: e.elements
      })),
      colorsPainted: sorted.length,
      distinctSerializations: byColor.size,
      mergeTolerance: COLOR.matchTol,
      paintedAreaPx2: Math.round(painted),
      backgroundImageAreaPx2: Math.round(imageArea),
      documentAreaPx2: Math.round(docArea),
      note: 'share of summed background-box area, nested boxes counted once each; colours within ' +
        COLOR.matchTol + ' OKLab are merged and their other serializations listed under aliases'
    };
  }

  // A background box covering the whole document is a ground, not a figure, and
  // a box painted in the dominant colour is that same ground repeated. Text and
  // media are ink at any size.
  function inkRects(records, dominantLab, docArea) {
    const out = [];
    for (const rec of records) {
      if (rec.el === document.body || rec.el === document.documentElement) continue;
      if (rec.text || rec.media) { out.push(rec.rect); continue; }
      if (rec.rect.width * rec.rect.height >= docArea * GRID.groundCoverage) continue;
      if (rec.bgImage) { out.push(rec.rect); continue; }
      if (!rec.bg || rec.bg.alpha <= 0.05) continue;
      if (dominantLab && oklabDistance(rec.bg.lab, dominantLab) <= COLOR.matchTol) continue;
      out.push(rec.rect);
    }
    return out;
  }

  function quadrantEmptiness(cells, cols, rows) {
    const qc = GRID.quadCols, qr = GRID.quadRows;
    const grid = [], flat = [], empty = [];
    for (let r = 0; r < qr; r++) {
      const row = [];
      const r0 = Math.floor((r * rows) / qr), r1 = Math.max(r0 + 1, Math.floor(((r + 1) * rows) / qr));
      for (let c = 0; c < qc; c++) {
        const c0 = Math.floor((c * cols) / qc), c1 = Math.max(c0 + 1, Math.floor(((c + 1) * cols) / qc));
        const cov = blockCoverage(cells, cols, r0, r1, c0, c1);
        row.push(r3(cov));
        flat.push(cov);
        if (cov < GRID.emptyCell) empty.push({ row: r, col: c, coverage: r3(cov) });
      }
      grid.push(row);
    }
    const dist = distribution(flat);
    for (const key of Object.keys(dist)) dist[key] = r3(dist[key]);
    return {
      method: METHOD, cols: qc, rows: qr, totalCells: qc * qr,
      cells: grid, emptyThreshold: GRID.emptyCell, emptyCells: empty.length, empty,
      distribution: dist,
      note: 'per-cell occupancy of content-bearing boxes over the full page height; a cell is "empty" under ' +
        Math.round(GRID.emptyCell * 100) + '% coverage'
    };
  }

  function inkProfile(cells, cols, rows, docH, vh) {
    const bandCount = Math.max(1, Math.ceil(docH / vh));
    const bands = [];
    for (let i = 0; i < bandCount; i++) {
      const topY = i * vh, bottomY = Math.min(docH, (i + 1) * vh);
      const r0 = Math.floor((topY / docH) * rows);
      const r1 = Math.max(r0 + 1, Math.min(rows, Math.ceil((bottomY / docH) * rows)));
      bands.push({
        band: i, topY: Math.round(topY), bottomY: Math.round(bottomY),
        coverage: r3(blockCoverage(cells, cols, r0, r1, 0, cols))
      });
    }
    const values = bands.map((b) => b.coverage);
    const dist = distribution(values);
    for (const key of Object.keys(dist)) dist[key] = r3(dist[key]);
    return {
      method: METHOD, viewportHeight: vh, bandCount, bands, distribution: dist,
      spread: r3(dist.max - dist.min),
      note: 'covered-area share per viewport-height band, with the spread between the fullest and emptiest'
    };
  }

  function elementColors(rec) {
    const out = [];
    if (rec.text) out.push({ key: rec.cs.color, role: 'color' });
    if (rec.bg && rec.bg.alpha > 0) out.push({ key: rec.cs.backgroundColor, role: 'background' });
    if (parseFloat(rec.cs.borderTopWidth) > 0) out.push({ key: rec.cs.borderTopColor, role: 'border' });
    return out;
  }

  function accentFrequency(records, options, ground, vh, docH) {
    const bandCount = Math.max(1, Math.ceil(docH / vh));
    const parsed = new Map();
    const labOf = (key) => {
      if (!parsed.has(key)) parsed.set(key, parseColor(key));
      return parsed.get(key);
    };

    let accent = null, source = null;
    if (options.accent) {
      const c = parseColor(options.accent);
      if (c) { accent = { value: options.accent, lab: c.lab }; source = 'opts'; }
    }
    if (!accent) {
      const tally = new Map();
      for (const rec of records) {
        for (const { key } of elementColors(rec)) {
          const c = labOf(key);
          if (!c || c.alpha <= 0.05) continue;
          const entry = tally.get(key) || { value: key, lab: c.lab, count: 0 };
          entry.count += 1;
          tally.set(key, entry);
        }
      }
      const ranked = Array.from(tally.values())
        .filter((t) => t.count >= ACCENT.minOccurrences && chroma(t.lab) >= ACCENT.minChroma)
        .filter((t) => !ground.dominantLab || oklabDistance(t.lab, ground.dominantLab) > COLOR.matchTol)
        .sort((a, b) => chroma(b.lab) - chroma(a.lab));
      if (ranked.length) { accent = { value: ranked[0].value, lab: ranked[0].lab, occurrences: ranked[0].count }; source = 'auto'; }
    }

    if (!accent) {
      return {
        method: METHOD, accent: null, source: null, tolerance: ACCENT.oklabTol, bandCount,
        note: 'no recurring saturated colour above chroma ' + ACCENT.minChroma + ' and ' +
          ACCENT.minOccurrences + ' occurrences — either the page has no accent or it is carried by media, ' + PROXY_NOTE
      };
    }

    const bands = new Array(bandCount).fill(0);
    const roles = new Set();
    let hits = 0;
    for (const rec of records) {
      let matched = false;
      for (const { key, role } of elementColors(rec)) {
        const c = labOf(key);
        if (!c || c.alpha <= 0.05) continue;
        if (oklabDistance(c.lab, accent.lab) > ACCENT.oklabTol) continue;
        matched = true;
        roles.add(role);
      }
      if (!matched) continue;
      hits += 1;
      const centerY = rec.rect.top + rec.rect.height / 2;
      bands[Math.min(bandCount - 1, Math.max(0, Math.floor(centerY / vh)))] += 1;
    }
    const dist = distribution(bands);
    return {
      method: METHOD,
      accent: { value: accent.value, oklab: { L: r3(accent.lab.L), a: r3(accent.lab.a), b: r3(accent.lab.b) }, chroma: r3(chroma(accent.lab)) },
      source, tolerance: ACCENT.oklabTol, bandCount,
      elements: hits, roles: Array.from(roles),
      perBand: bands.map((count, i) => ({ band: i, topY: Math.round(i * vh), count })),
      perViewportMean: r3(dist.mean), max: dist.max, min: dist.min,
      bandsWithNone: bands.filter((n) => n === 0).length,
      note: 'elements carrying the accent as text, background or border, counted once each per viewport band; roles lists which of the three the match came from'
    };
  }

  function motionCandidates() {
    const isFixed = makeFixedCheck();
    const set = new Set();
    if (typeof document.getAnimations === 'function') {
      for (const anim of document.getAnimations()) {
        const target = anim.effect && anim.effect.target;
        if (target && target.nodeType === 1) set.add(target);
      }
    }
    // Insertion order is priority order — the cap slices the tail. Declared
    // animation targets first, then the ambient media, then anything merely
    // hinting at motion; a page of SVG icons must not crowd out the channels
    // that actually run.
    for (const el of document.querySelectorAll('canvas, video')) set.add(el);
    for (const el of Array.from(document.body.querySelectorAll('*')).slice(0, MAX_SCAN)) {
      if (set.size >= MOTION.maxCandidates * 2) break;
      const cs = getComputedStyle(el);
      // A non-none transform is the only DOM trace a rAF tween library leaves at
      // rest: GSAP and the scroll-smoothing libraries write inline transforms and
      // register no animation and no animation-name.
      if ((cs.animationName && cs.animationName !== 'none') ||
        (cs.willChange && cs.willChange !== 'auto') ||
        (cs.transform && cs.transform !== 'none')) set.add(el);
    }
    for (const el of document.querySelectorAll('svg')) {
      if (set.size >= MOTION.maxCandidates * 2) break;
      set.add(el);
    }
    return Array.from(set)
      .filter((el) => el.isConnected && isVisible(el) && !isFixed(el))
      .slice(0, MOTION.maxCandidates);
  }

  function sampleAll(els) {
    return els.map((el) => {
      const r = el.getBoundingClientRect();
      const cs = getComputedStyle(el);
      return { x: r.left, y: r.top, w: r.width, h: r.height, transform: cs.transform, opacity: cs.opacity };
    });
  }

  const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

  function movers(els, rows) {
    const out = [];
    for (let i = 0; i < rows.length && out.length < 10; i++) {
      if (!rows[i].moved) continue;
      out.push({
        selector: cssPath(els[i]), dx: r3(rows[i].dx), dy: r3(rows[i].dy),
        dOpacity: r3(rows[i].dOpacity), transformChanged: rows[i].transformChanged
      });
    }
    return out;
  }

  async function idleDelta(els, idleMs) {
    const first = sampleAll(els);
    await wait(idleMs / 2);
    const mid = sampleAll(els);
    await wait(idleMs / 2);
    const last = sampleAll(els);
    // Peak-hold across both halves: a periodic channel can return to its rest
    // pose exactly at the end of the window and read as dead on a single diff.
    const rows = els.map((_, i) => {
      const a = delta(first[i], mid[i], 0), b = delta(first[i], last[i], 0);
      return a.moved ? a : b;
    });
    return {
      method: METHOD, idleMs, candidates: els.length,
      changed: rows.filter((row) => row.moved).length,
      movers: movers(els, rows),
      note: PROXY_NOTE + ' — a canvas repainting every frame under a still rect reads as zero here'
    };
  }

  function scrollTo(x, y) {
    try { window.scrollTo({ left: x, top: y, behavior: 'instant' }); } catch (e) { window.scrollTo(x, y); }
  }

  async function scrollDelta(els, stepPx) {
    const startX = window.scrollX, startY = window.scrollY;
    const before = sampleAll(els);
    scrollTo(startX, startY + stepPx);
    await wait(MOTION.settleMs);
    const scrolled = window.scrollY - startY;
    const after = sampleAll(els);
    scrollTo(startX, startY);
    await wait(MOTION.settleMs);
    const rows = els.map((_, i) => delta(before[i], after[i], scrolled));
    return {
      method: METHOD, requestedStepPx: stepPx, scrolledPx: Math.round(scrolled),
      restored: Math.abs(window.scrollY - startY) < 1,
      candidates: els.length, changed: rows.filter((row) => row.moved).length,
      movers: movers(els, rows),
      note: PROXY_NOTE + '; scrolledPx 0 means the step never landed (hijacked or unscrollable page), not that the page is static'
    };
  }

  function killTransitions() {
    const prior = document.getElementById(KILL_STYLE_ID);
    if (prior) prior.remove();
    const style = document.createElement('style');
    style.id = KILL_STYLE_ID;
    style.textContent = '*, *::before, *::after { transition: none !important; }';
    document.head.appendChild(style);
    return { restore: () => style.remove() };
  }

  // A throttled or background frame loop must never hang the pass, so the
  // settle wait races a timer; resolving twice is a no-op.
  function twoFrames() {
    return new Promise((resolve) => {
      const timer = setTimeout(resolve, 200);
      requestAnimationFrame(() => requestAnimationFrame(() => { clearTimeout(timer); resolve(); }));
    });
  }

  async function run(options) {
    options = options || {};
    if (!document.body) return { payload: 'award-pixel-metrics', error: 'document.body not available — inject after the body parses' };
    if (document.fonts && document.fonts.ready) await document.fonts.ready;
    await twoFrames();

    const box = docBox();
    const vh = window.innerHeight;
    const rasterCols = GRID.rasterCols;
    const rasterRows = Math.max(GRID.quadRows * 10,
      Math.min(GRID.maxRasterRows, Math.round((rasterCols * box.h) / box.w)));

    // The raster is geometry, so transitions are killed for it; the motion
    // proxies run afterwards with the page's own timing intact.
    const kill = killTransitions();
    let records, ground, ink, cells;
    try {
      records = collect();
      ground = groundCommitment(records, box.w * box.h);
      ink = inkRects(records, ground.dominantLab, box.w * box.h);
      cells = rasterize(ink, box, rasterCols, rasterRows);
    } finally {
      kill.restore();
    }

    const candidates = motionCandidates();
    const idle = await idleDelta(candidates, options.idleMs || MOTION.idleMs);
    const step = Math.max(1, options.scrollStepPx || Math.round(vh * MOTION.scrollFraction));
    const scroll = await scrollDelta(candidates, step);

    const metrics = {
      quadrantEmptiness: quadrantEmptiness(cells, rasterCols, rasterRows),
      inkProfile: inkProfile(cells, rasterCols, rasterRows, box.h, vh),
      groundCommitment: ground,
      accentFrequency: accentFrequency(records, options, ground, vh, box.h),
      idleDelta: idle,
      scrollDelta: scroll
    };
    // The ground's lab is the internal key ink and accent are measured against,
    // not evidence — the colour string above is what the judge reads.
    delete ground.dominantLab;

    return {
      payload: 'award-pixel-metrics',
      version: 1,
      proxy: true,
      viewport: { w: window.innerWidth, h: vh, dpr: window.devicePixelRatio || 1 },
      document: { w: Math.round(box.w), h: Math.round(box.h), viewports: r3(box.h / vh) },
      metrics,
      scanned: {
        elementsSeen: records.elementsSeen, elements: records.length, inkRects: ink.length,
        raster: { cols: rasterCols, rows: rasterRows },
        capped: records.capped
      },
      footer: FOOTER
    };
  }

  window.awardPixelMetrics = Object.assign({}, api, { run });
})();
