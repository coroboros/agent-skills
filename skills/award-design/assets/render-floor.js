/* award-design render floor — the mechanical D2 floor. Every rule here names an
   objectively broken thing and ships the boxes that prove it; nothing in this
   file has an opinion about taste.

   Sweep protocol. The harness owns the browser: it injects this file, calls
   arm() once on load, then for each width in SWEEP (375, 768, 1024, 1440, 1920)
   resizes the viewport and calls run(). This payload never opens a browser,
   never resizes one, never navigates, never touches the network.

     awardRenderFloor.arm();                                // once, on load
     await awardRenderFloor.run();                          // after each resize
     await awardRenderFloor.run({ root: '#chapter-3' });    // per chapter, as built

   run({ root }) scopes the text sweep to one chapter; the page-level rules
   (CTA-FOLD, MOBILE-NAV-MISSING, H-OVERFLOW, CONSOLE-ERROR) always read the
   whole document. Width-gated rules state their gate and stay silent outside it.

   What each rule catches — every one traces to a P0 measured on the Undercurrent
   build, where the builder's own Phase-5 verdict said READY and an independent
   assessor said LOSES 6.5/10 with the cap on execution, not idea:

     TEXT-OVERLAP        the spec-list citation that printed on top of its label
     TEXT-CLIPPED        "ΓRANSIENT" — a hero label cut mid-glyph at 375 — and
                         the hardware diagram that lost its trailing " m"
     ZERO-BOX-CONTENT    the <dt> that collapsed to w:0 h:120 with its text
                         still in the DOM
     CTA-FOLD            the primary CTA at y=963 under a 900px fold, on a
                         book-a-pilot page
     MOBILE-NAV-MISSING  .nav__links{display:none} with no toggle — four
                         sections unreachable across 11,577px of scroll
     H-OVERFLOW          a page wider than the viewport it was resized to
     CONSOLE-ERROR       whatever threw while the sweep was running

   TEXT-OVERLAP exempts DOM nesting only — an element and its own ancestor share
   a box by construction. Two UNRELATED elements are judged on geometry alone,
   including the case where one box sits wholly inside the other: a citation
   printing inside a label column's box is the most total form of text on text,
   not an excuse to skip it.
   TEXT-CLIPPED measures the GLYPH box (range client rects), not the border box:
   a block element never grows past its containing block, so a nowrap heading in
   a narrower overflow:hidden parent has an in-bounds rect and out-of-bounds
   type. MOBILE-NAV-MISSING counts HIDDEN links, not visible ones — a logo
   anchor plus a CTA anchor is two visible links in a header whose real menu is
   display:none. TEXT-OVERLAP carries two independent floors, a share of the
   smaller box and an absolute size, because a 700×30px collision ruins a line of
   type whatever fraction of an 800×400 block it computes to. H-OVERFLOW is
   deliberately the same id and box as detector.js's — a harness merging both
   payloads should dedupe it, not count it twice.

   Honest limits. Canvas text is pixels: a label painted into a <canvas> is
   invisible here, so the residue canvas that sliced "500–1500 Hz" is a
   screenshot finding, not a DOM one. Declared truncation (text-overflow:
   ellipsis, -webkit-line-clamp) is exempt from TEXT-CLIPPED — it cuts glyphs on
   purpose and says so. SVG text is measured by its client rect against the
   nearest clipping box, not by getBBox(): a bbox in user units cannot be
   compared to an ancestor's screen rect without the CTM. Only position:fixed
   subtrees sit out the collision pass — they stack over page content by design,
   while a sticky box at rest is in normal flow and stays in scope; the count of
   what was excluded ships in `scanned`. A clipping box carrying a LIVE scroll
   offset is a track, so escapes on that axis are skipped and the other axis is
   still judged; the scroll EXTENT is not used for this, because overflow:hidden
   makes a scroll container and its extent grows precisely when it is cutting
   content. CTA-FOLD is REVIEW, never FAIL: some archetypes defer the primary
   action legally.
   MOBILE-NAV-MISSING needs a nav container (header, nav, [role=navigation]) to
   fire: a page that authored no navigation at all cannot be proven broken here,
   and a single-scroll piece with none is an archetype decision, not a defect.
   Errors are captured from window 'error' and 'unhandledrejection' — a bare
   console.error() that never threw does not reach this instrument.

   A clean sweep says the type is not broken. It says nothing about the design. */
(() => {
  'use strict';

  const RULES = [
    { id: 'TEXT-OVERLAP', severity: 'FAIL', box: 'type-integrity' },
    { id: 'TEXT-CLIPPED', severity: 'FAIL', box: 'type-integrity' },
    { id: 'ZERO-BOX-CONTENT', severity: 'FAIL', box: 'type-integrity' },
    { id: 'CTA-FOLD', severity: 'REVIEW', box: 'first-viewport' },
    { id: 'MOBILE-NAV-MISSING', severity: 'FAIL', box: 'reachability' },
    { id: 'H-OVERFLOW', severity: 'FAIL', box: 'no-h-scroll' },
    { id: 'CONSOLE-ERROR', severity: 'REVIEW', box: 'runtime-clean' }
  ];

  const TOL = { overlapPx: 2, overlapRatio: 0.15, overlapAbsW: 24, overlapAbsH: 8, clipPx: 2, zeroBoxPx: 0.5, foldPx: 1 };
  const GATES = { mobileMaxW: 500, desktopMinW: 1024, minHiddenLinks: 2 };
  const SWEEP = [375, 768, 1024, 1440, 1920];

  const FOOTER = 'Mechanical floor — every finding carries the boxes that prove it. A clean sweep says the type is not broken; it says nothing about the design.';
  const DEFAULT_CTA = 'a[class*="cta" i], a[class*="btn" i], button[class*="primary" i], [data-cta]';
  const NAV_ROOTS = 'header, nav, [role="navigation"]';
  const NAV_LINKS = 'header a[href], nav a[href], [role="navigation"] a[href]';
  // Searched document-wide, not inside header/nav: the fixed corner burger is
  // routinely a direct child of body or of a UI layer, and a class-named div
  // with no button semantics is common enough that scoping this to header/nav
  // would FAIL pages whose navigation works.
  const NAV_TOGGLE = 'header button, nav button, [role="navigation"] button, ' +
    '[aria-expanded], [aria-label*="menu" i], [class*="burger" i], [class*="hamburger" i], ' +
    '[class*="menu-toggle" i], [class*="nav-toggle" i], [data-menu-toggle]';
  // Elements that carry text without ever laying it out — an <option> measures
  // 0×0 in Chrome and would read as a collapsed box on every page with a select.
  const NON_LAYOUT = 'script, style, noscript, template, title, meta, link, option, optgroup, defs, clipPath, mask, pattern, symbol, marker';
  const KILL_STYLE_ID = '__ad-rf-kill';
  const MAX_SCAN = 5000;
  const MAX_TEXT = 1500;
  const FINDING_CAP = 15;
  const ERROR_CAP = 25;

  // ---------------------------------------------------------------- pure core

  function rectArea(r) {
    return Math.max(0, r.right - r.left) * Math.max(0, r.bottom - r.top);
  }

  function intersection(a, b) {
    const w = Math.min(a.right, b.right) - Math.max(a.left, b.left);
    const h = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
    return { w, h, area: w > 0 && h > 0 ? w * h : 0 };
  }

  // TEXT-OVERLAP geometry. The ONE exemption is DOM nesting: an element and its
  // own ancestor share a box by construction, so `domRelated` reads NESTED and
  // stops there. GEOMETRIC containment between unrelated elements is NOT exempt —
  // a citation sitting wholly inside a label column's box is the most total form
  // of text on text, and it is the shape the shipped defect took. The caller
  // passes the DOM answer in rather than keeping a second, hidden rule of its own.
  // Two independent floors, because neither alone is enough: the RATIO catches a
  // small box swallowed by a bigger one, and the ABSOLUTE size catches a full
  // line of type printing across a large paragraph — 700×30px of collision is a
  // ruined line whatever fraction of an 800×400 block it works out to.
  function classifyRectPair(a, b, tol, domRelated) {
    const t = Object.assign({}, TOL, tol || {});
    const inter = intersection(a, b);
    const out = { overlapW: inter.w, overlapH: inter.h, overlapArea: inter.area, ratio: 0 };
    if (inter.w <= t.overlapPx || inter.h <= t.overlapPx) {
      out.verdict = 'CLEAR';
      return out;
    }
    const smaller = Math.min(rectArea(a), rectArea(b));
    out.ratio = smaller > 0 ? inter.area / smaller : 0;
    if (domRelated) {
      out.verdict = 'NESTED';
      return out;
    }
    if (out.ratio >= t.overlapRatio ||
      (inter.w >= t.overlapAbsW && inter.h >= t.overlapAbsH)) out.verdict = 'OVERLAP';
    else out.verdict = 'GRAZE';
    return out;
  }

  // TEXT-CLIPPED, own-box axis. A content box under overflow hidden/clip whose
  // scroll extent runs past its client extent is cutting its own text. Declared
  // truncation reads DECLARED — an ellipsis cuts glyphs on purpose.
  function classifyClip(sample, tol) {
    const t = Object.assign({}, TOL, tol || {}).clipPx;
    const clips = (v) => v === 'hidden' || v === 'clip';
    const dx = (sample.scrollW || 0) - (sample.clientW || 0);
    const dy = (sample.scrollH || 0) - (sample.clientH || 0);
    const x = clips(sample.overflowX) && dx > t;
    const y = clips(sample.overflowY) && dy > t;
    const out = { hiddenX: dx, hiddenY: dy };
    if (!x && !y) out.verdict = 'OK';
    else if (sample.declaredTruncation) out.verdict = 'DECLARED';
    else {
      out.verdict = 'CLIPPED';
      out.axis = x && y ? 'both' : x ? 'x' : 'y';
    }
    return out;
  }

  // TEXT-CLIPPED, ancestor axis. How far the glyphs escape a clipping box on
  // each side; the deepest NON-EXEMPT escape is the finding's measurement.
  // exemptSides carries the axes a live scroll offset proves are a track — the
  // deepest escape overall may be on one of them while a real, unreachable cut
  // sits on another side, so the exemption is applied per side, never per box.
  function rectEscape(rect, clip, tol, exemptSides) {
    const t = typeof tol === 'number' ? tol : TOL.clipPx;
    const exempt = exemptSides || [];
    const escape = {
      left: clip.left - rect.left,
      right: rect.right - clip.right,
      top: clip.top - rect.top,
      bottom: rect.bottom - clip.bottom
    };
    let side = null, max = 0;
    for (const key of ['left', 'right', 'top', 'bottom']) {
      if (exempt.indexOf(key) !== -1) continue;
      if (escape[key] > max) { max = escape[key]; side = key; }
    }
    return { escape, side, max, exempt, clipped: max > t };
  }

  // ZERO-BOX-CONTENT. A rendered element carrying text in a box with no width or
  // no height — the <dt> that collapsed to w:0 while 120px of text stayed in the
  // DOM. The screen-reader-only idiom (both axes at zero, positioned, clipped)
  // is the one legitimate zero box.
  function classifyZeroBox(sample, tol) {
    const t = Object.assign({}, TOL, tol || {}).zeroBoxPx;
    const w = sample.width || 0, h = sample.height || 0;
    if (w >= t && h >= t) return 'OK';
    if (w < t && h < t && sample.clipped && sample.positioned) return 'SR-ONLY';
    return 'COLLAPSED';
  }

  // CTA-FOLD. In the fold means the WHOLE box above the fold line — a primary
  // action the fold cuts in half is not in the first viewport.
  function classifyFold(sample) {
    if ((sample.viewportW || 0) < GATES.desktopMinW) return 'SKIP';
    if (!sample.candidates) return 'NONE';
    return (sample.inFold || 0) > 0 ? 'OK' : 'BELOW';
  }

  // MOBILE-NAV-MISSING. The proof is HIDDEN links, not visible ones: navigation
  // authored in the DOM, not laid out at phone width, and no control to reveal
  // it. Counting visible links instead would clear the shipped defect outright —
  // a logo anchor plus one CTA anchor is two links in a header whose real menu
  // is display:none, and it would also fail a legitimate one-link header.
  function classifyMobileNav(sample) {
    if ((sample.viewportW || 0) > GATES.mobileMaxW) return 'SKIP';
    if ((sample.hiddenNavLinks || 0) < GATES.minHiddenLinks) return 'OK';
    return sample.hasToggle ? 'TOGGLE' : 'MISSING';
  }

  const api = { RULES, TOL, GATES, SWEEP, rectArea, intersection, classifyRectPair,
    classifyClip, rectEscape, classifyZeroBox, classifyFold, classifyMobileNav };

  if (typeof window === 'undefined') {
    if (typeof module !== 'undefined' && module.exports) module.exports = api;
    return;
  }

  // ------------------------------------------------------------ browser layer

  const r2 = (n) => Math.round(n * 100) / 100;
  const boxOf = (r) => ({ x: r2(r.left), y: r2(r.top), w: r2(r.right - r.left), h: r2(r.bottom - r.top) });

  function finding(rule, selector, measurement, note) {
    const spec = RULES.find((r) => r.id === rule);
    return { rule, severity: spec.severity, box: spec.box, selector, measurement, note };
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

  const CHECK_VIS = { visibilityProperty: true, opacityProperty: true, contentVisibilityAuto: true };

  // checkVisibility resolves ANCESTOR opacity and content-visibility, which the
  // own-style fallback cannot — an opacity-0 decorative overlay must not enter
  // the collision pass, and its parent is usually what zeroes it.
  function isVisible(el) {
    if (typeof el.checkVisibility === 'function') return el.checkVisibility(CHECK_VIS);
    const cs = getComputedStyle(el);
    return cs.display !== 'none' && cs.visibility !== 'hidden' && parseFloat(cs.opacity) >= 0.05;
  }

  function directText(el) {
    let out = '';
    for (const node of el.childNodes) if (node.nodeType === 3) out += node.textContent;
    return out.trim();
  }

  // position:fixed ONLY. A sticky box at rest sits in normal flow and shares the
  // coordinate frame with its siblings, so folding it in here would exempt a
  // whole scroll-pinned chapter from the collision pass and hand any CTA inside
  // one a free pass on the fold rule.
  function makeFixedCheck() {
    const memo = new Map();
    const check = (node) => {
      if (!node || node.nodeType !== 1) return false;
      if (memo.has(node)) return memo.get(node);
      const v = getComputedStyle(node).position === 'fixed' || check(node.parentElement);
      memo.set(node, v);
      return v;
    };
    return check;
  }

  // The glyph box, not the border box. A block-level element never grows past
  // its containing block, so a nowrap heading inside a narrower overflow:hidden
  // parent has an in-bounds RECT and out-of-bounds TYPE — the shape of the
  // diagram that lost its trailing " m". Range client rects are the line boxes
  // themselves, which is what actually gets cut.
  function textInkRect(el) {
    let rects;
    try {
      const range = document.createRange();
      range.selectNodeContents(el);
      rects = Array.from(range.getClientRects());
    } catch (e) { return null; }
    let left = Infinity, top = Infinity, right = -Infinity, bottom = -Infinity, found = false;
    for (const r of rects) {
      if (r.width < 0.5 || r.height < 0.5) continue;
      found = true;
      left = Math.min(left, r.left); top = Math.min(top, r.top);
      right = Math.max(right, r.right); bottom = Math.max(bottom, r.bottom);
    }
    return found ? { left, top, right, bottom } : null;
  }

  function textCandidates(root) {
    const isFixed = makeFixedCheck();
    const all = root.querySelectorAll('*');
    const nodes = Array.from(all).slice(0, MAX_SCAN);
    const out = [];
    let fixedExcluded = 0;
    for (const el of nodes) {
      if (out.length >= MAX_TEXT) break;
      const text = directText(el);
      if (!text) continue;
      if (el.closest(NON_LAYOUT) || el.closest('[aria-hidden="true"]')) continue;
      if (!isVisible(el)) continue;
      const fixed = isFixed(el);
      if (fixed) fixedExcluded++;
      out.push({ el, cs: getComputedStyle(el), rect: el.getBoundingClientRect(), text, fixed });
    }
    // Both caps are reported, and against the counts they actually truncate —
    // comparing survivors to the pre-filter scan cap would report a truncated
    // sweep as a complete one.
    out.scanCapped = all.length > MAX_SCAN;
    out.textCapped = out.length >= MAX_TEXT;
    out.elementsSeen = all.length;
    out.fixedExcluded = fixedExcluded;
    return out;
  }

  // Vertical sweep: candidates sorted by top, each compared only against those
  // that start before it ends. A full pairwise pass over a 11,577px page is not
  // affordable inside one evaluate call.
  function checkTextOverlap(candidates, findings) {
    const items = candidates.filter((c) => !c.fixed && rectArea(c.rect) > 0)
      .sort((a, b) => a.rect.top - b.rect.top);
    let count = 0, pairs = 0;
    for (let i = 0; i < items.length && count < FINDING_CAP; i++) {
      const a = items[i];
      for (let j = i + 1; j < items.length; j++) {
        const b = items[j];
        if (b.rect.top >= a.rect.bottom - TOL.overlapPx) break;
        pairs++;
        const related = a.el.contains(b.el) || b.el.contains(a.el);
        const pair = classifyRectPair(a.rect, b.rect, null, related);
        if (pair.verdict !== 'OVERLAP') continue;
        count++;
        findings.push(finding('TEXT-OVERLAP', cssPath(a.el) + ' × ' + cssPath(b.el), {
          a: boxOf(a.rect), b: boxOf(b.rect),
          overlapW: r2(pair.overlapW), overlapH: r2(pair.overlapH),
          overlapArea: r2(pair.overlapArea), ratioOfSmaller: r2(pair.ratio),
          aText: a.text.slice(0, 40), bText: b.text.slice(0, 40)
        }, 'two text boxes cut into each other by ' + Math.round(pair.overlapW) + '×' +
          Math.round(pair.overlapH) + 'px (' + Math.round(pair.ratio * 100) +
          '% of the smaller box) — neither contains the other, so this prints as text on text'));
        if (count >= FINDING_CAP) break;
      }
    }
    return pairs;
  }

  function clipAncestors(el) {
    const out = [];
    let node = el.parentElement;
    while (node && node.nodeType === 1) {
      const cs = getComputedStyle(node);
      const clips = (v) => v === 'hidden' || v === 'clip';
      // An inline <svg> in an HTML document is never :root, so the UA rule
      // `svg:not(:root) { overflow: hidden }` already computes to hidden and the
      // same test catches it — the diagram that cut its trailing " m" is here.
      const svg = node.tagName.toLowerCase() === 'svg';
      if (clips(cs.overflowX) || clips(cs.overflowY)) {
        // A LIVE scroll offset is the only proof this box is a track. Its scroll
        // extent is not: overflow:hidden makes a scroll container, so
        // scrollWidth > clientWidth is true precisely WHEN the box is cutting
        // content — reading that as a track exemption would suppress every
        // ordinary clipped card, which is most of what this rule exists to catch.
        out.push({
          el: node, rect: node.getBoundingClientRect(),
          scrolledX: Math.abs(node.scrollLeft || 0) > 1,
          scrolledY: Math.abs(node.scrollTop || 0) > 1,
          reason: svg ? 'svg viewport clip' : 'overflow ' + cs.overflowX + '/' + cs.overflowY
        });
      }
      node = node.parentElement;
    }
    return out;
  }

  function checkTextClipped(candidates, findings) {
    let count = 0;
    for (const c of candidates) {
      if (count >= FINDING_CAP) break;
      const { el, cs, rect } = c;
      if (typeof HTMLElement !== 'undefined' && el instanceof HTMLElement) {
        const own = classifyClip({
          scrollW: el.scrollWidth, clientW: el.clientWidth,
          scrollH: el.scrollHeight, clientH: el.clientHeight,
          overflowX: cs.overflowX, overflowY: cs.overflowY,
          declaredTruncation: cs.textOverflow === 'ellipsis' ||
            (!!cs.webkitLineClamp && cs.webkitLineClamp !== 'none')
        });
        if (own.verdict === 'CLIPPED') {
          count++;
          findings.push(finding('TEXT-CLIPPED', cssPath(el), {
            axis: own.axis, box: boxOf(rect),
            scroll: { w: el.scrollWidth, h: el.scrollHeight },
            client: { w: el.clientWidth, h: el.clientHeight },
            hiddenX: r2(own.hiddenX), hiddenY: r2(own.hiddenY),
            text: c.text.slice(0, 40)
          }, 'own content box hides ' + Math.round(Math.max(own.hiddenX, own.hiddenY)) +
            'px of its own text under overflow ' + cs.overflowX + '/' + cs.overflowY +
            ' — no ellipsis, no clamp: the glyphs are simply cut'));
          continue;
        }
      }
      const ink = textInkRect(el) || rect;
      for (const clip of clipAncestors(el)) {
        const exempt = (clip.scrolledX ? ['left', 'right'] : []).concat(clip.scrolledY ? ['top', 'bottom'] : []);
        const esc = rectEscape(ink, clip.rect, TOL.clipPx, exempt);
        if (!esc.clipped) continue;
        // Fully outside its clip box is hidden, not cut — a carousel slide off
        // the track reads that way and is not a glyph failure.
        if (intersection(ink, clip.rect).area <= 0) continue;
        count++;
        findings.push(finding('TEXT-CLIPPED', cssPath(el), {
          side: esc.side, escapePx: r2(esc.max), exemptSides: esc.exempt,
          glyphBox: boxOf(ink), box: boxOf(rect),
          clipBox: boxOf(clip.rect), clipSelector: cssPath(clip.el),
          clipReason: clip.reason, text: c.text.slice(0, 40)
        }, 'glyphs run ' + Math.round(esc.max) + 'px past the ' + esc.side + ' edge of their clipping box (' +
          clip.reason + ') — cut, not truncated'));
        break;
      }
    }
  }

  function checkZeroBox(candidates, findings) {
    let count = 0;
    for (const c of candidates) {
      if (count >= FINDING_CAP) break;
      const { cs, rect } = c;
      const cls = classifyZeroBox({
        width: rect.width, height: rect.height,
        clipped: cs.overflow === 'hidden' || cs.clip !== 'auto' || cs.clipPath !== 'none',
        positioned: cs.position === 'absolute' || cs.position === 'fixed'
      });
      if (cls !== 'COLLAPSED') continue;
      count++;
      const axis = rect.width < TOL.zeroBoxPx ? 'width' : 'height';
      findings.push(finding('ZERO-BOX-CONTENT', cssPath(c.el), {
        box: boxOf(rect), collapsedAxis: axis, textLength: c.text.length,
        display: cs.display, position: cs.position, text: c.text.slice(0, 40)
      }, 'carries ' + c.text.length + ' characters in a box with no ' + axis +
        ' (' + r2(rect.width) + '×' + r2(rect.height) + ') — the text is in the DOM and off the page'));
    }
  }

  function checkCtaFold(options, findings) {
    if (window.innerWidth < GATES.desktopMinW) return;
    const selector = options.ctaSelector || DEFAULT_CTA;
    let nodes = [];
    try { nodes = Array.from(document.querySelectorAll(selector)); } catch (e) { nodes = []; }
    const isFixed = makeFixedCheck();
    const fold = window.innerHeight;
    const rows = [];
    for (const el of nodes) {
      if (!isVisible(el)) continue;
      const rect = el.getBoundingClientRect();
      if (rect.width < 1 || rect.height < 1) continue;
      const fixed = isFixed(el);
      const top = fixed ? rect.top : rect.top + window.scrollY;
      const bottom = fixed ? rect.bottom : rect.bottom + window.scrollY;
      rows.push({ el, top, bottom, fixed,
        inFold: fixed || (top >= -TOL.foldPx && bottom <= fold + TOL.foldPx) });
    }
    const inFold = rows.filter((row) => row.inFold).length;
    const cls = classifyFold({ viewportW: window.innerWidth, candidates: rows.length, inFold });
    if (cls === 'OK' || cls === 'SKIP') return;
    if (cls === 'NONE') {
      findings.push(finding('CTA-FOLD', 'document',
        { viewportW: window.innerWidth, foldPx: fold, candidates: 0, selector },
        'nothing on the page matches the primary-action selector — name the CTA via opts.ctaSelector, or the first viewport is asking for nothing'));
      return;
    }
    const nearest = rows.slice().sort((a, b) => a.bottom - b.bottom)[0];
    findings.push(finding('CTA-FOLD', cssPath(nearest.el), {
      viewportW: window.innerWidth, foldPx: fold, candidates: rows.length,
      nearestTopY: r2(nearest.top), nearestBottomY: r2(nearest.bottom),
      belowFoldPx: r2(nearest.bottom - fold), selector
    }, 'no primary action sits fully inside the first viewport — the nearest of ' + rows.length +
      ' ends at y=' + Math.round(nearest.bottom) + ', ' + Math.round(nearest.bottom - fold) +
      'px under a ' + fold + 'px fold; REVIEW because some archetypes defer the ask on purpose'));
  }

  function checkMobileNav(findings) {
    if (window.innerWidth > GATES.mobileMaxW) return;
    // No nav container authored at all: nothing here proves a defect, and a
    // single-scroll piece with no navigation is an archetype decision.
    if (!document.querySelector(NAV_ROOTS)) return;
    const laidOut = (el) => {
      const r = el.getBoundingClientRect();
      return r.width > 0 && r.height > 0;
    };
    const allLinks = Array.from(document.querySelectorAll(NAV_LINKS));
    const links = allLinks.filter((el) => isVisible(el) && laidOut(el));
    const hidden = allLinks.length - links.length;
    const toggles = Array.from(document.querySelectorAll(NAV_TOGGLE))
      .filter((el) => isVisible(el) && laidOut(el));
    const cls = classifyMobileNav({
      viewportW: window.innerWidth, hiddenNavLinks: hidden, hasToggle: toggles.length > 0
    });
    if (cls !== 'MISSING') return;
    findings.push(finding('MOBILE-NAV-MISSING', 'header, nav', {
      viewportW: window.innerWidth, visibleNavLinks: links.length,
      hiddenNavLinks: hidden, toggles: 0,
      documentHeight: document.documentElement.scrollHeight, toggleSelector: NAV_TOGGLE
    }, hidden + ' navigation link(s) authored and not laid out, ' + links.length +
      ' laid out, and no control to reveal them — no toggle, no aria-expanded, no menu-labelled or burger-classed element anywhere on the page; ' +
      document.documentElement.scrollHeight + 'px of document with no way to reach it'));
  }

  function checkOverflow(findings) {
    const sw = document.documentElement.scrollWidth;
    if (sw <= window.innerWidth + 1) return;
    findings.push(finding('H-OVERFLOW', 'html',
      { scrollWidth: sw, viewportW: window.innerWidth, overflowPx: sw - window.innerWidth },
      'document scrollWidth ' + sw + 'px against a ' + window.innerWidth +
      'px viewport — the page scrolls sideways'));
  }

  // State lives ON the one global, not beside it. Re-injecting this file
  // Object.assigns onto the existing object rather than replacing it, so the
  // armed listeners and their buffer survive a re-inject across the width sweep
  // without the payload owning a second window property.
  function state() {
    const g = window.awardRenderFloor;
    if (!g.state) g.state = { armed: false, armedAt: null, errors: [], dropped: 0 };
    return g.state;
  }

  function record(entry) {
    const s = state();
    if (s.errors.length < ERROR_CAP) s.errors.push(entry);
    else s.dropped++;
  }

  // Listeners install once per page load; a second arm() would double-count
  // every throw across the width sweep.
  function arm() {
    const s = state();
    if (s.armed) return { armed: true, armedAt: s.armedAt, captured: s.errors.length, note: 'already armed' };
    s.armed = true;
    s.armedAt = Date.now();
    window.addEventListener('error', (e) => record({
      kind: 'error',
      message: String(e.message || (e.error && e.error.message) || e.error || '').slice(0, 300),
      source: String(e.filename || '').slice(-120),
      line: e.lineno || null, column: e.colno || null,
      viewportW: window.innerWidth, atMs: Date.now() - s.armedAt
    }));
    window.addEventListener('unhandledrejection', (e) => record({
      kind: 'unhandledrejection',
      message: String((e.reason && (e.reason.message || e.reason)) || '').slice(0, 300),
      source: null, line: null, column: null,
      viewportW: window.innerWidth, atMs: Date.now() - s.armedAt
    }));
    return { armed: true, armedAt: s.armedAt, captured: 0,
      note: 'error and unhandledrejection recorded from here; each run() reports what landed, tagged with the width it landed at' };
  }

  function checkConsole(findings) {
    const s = state();
    if (!s.armed) {
      findings.push(finding('CONSOLE-ERROR', 'document', { armed: false, captured: 0 },
        'never armed — call awardRenderFloor.arm() on load, before the page runs, or every runtime throw goes unrecorded'));
      return;
    }
    if (!s.errors.length) return;
    findings.push(finding('CONSOLE-ERROR', 'document', {
      captured: s.errors.length, dropped: s.dropped,
      sinceMs: Date.now() - s.armedAt, entries: s.errors.slice(0, 10)
    }, s.errors.length + ' uncaught error(s) since arming — a page still throwing while it renders is not finished'));
  }

  // Geometry read mid-transition is a different page every call. Animations are
  // left running: pausing or clearing them parks elements on a frame the page
  // never shows, which would invent collisions instead of measuring them.
  function killTransitions() {
    const prior = document.getElementById(KILL_STYLE_ID);
    if (prior) prior.remove();
    const style = document.createElement('style');
    style.id = KILL_STYLE_ID;
    style.textContent = '*, *::before, *::after { transition: none !important; }';
    document.head.appendChild(style);
    return { restore: () => style.remove() };
  }

  // A throttled or background frame loop must never hang the sweep, so the
  // settle wait races a timer; resolving twice is a no-op.
  function twoFrames() {
    return new Promise((resolve) => {
      const timer = setTimeout(resolve, 200);
      requestAnimationFrame(() => requestAnimationFrame(() => { clearTimeout(timer); resolve(); }));
    });
  }

  function runningAnimations() {
    if (typeof document.getAnimations !== 'function') return null;
    return document.getAnimations().filter((a) => a.playState === 'running').length;
  }

  async function run(options) {
    options = options || {};
    const root = options.root ? document.querySelector(options.root) : document.body;
    if (!root) {
      return { payload: 'award-render-floor', error: options.root
        ? 'no element matches root "' + options.root + '"'
        : 'document.body not available — inject after the body parses' };
    }
    if (document.fonts && document.fonts.ready) await document.fonts.ready;
    await twoFrames();

    const findings = [];
    const kill = killTransitions();
    let candidates = [], pairs = 0;
    try {
      candidates = textCandidates(root);
      pairs = checkTextOverlap(candidates, findings);
      checkTextClipped(candidates, findings);
      checkZeroBox(candidates, findings);
      checkCtaFold(options, findings);
      checkMobileNav(findings);
      checkOverflow(findings);
      checkConsole(findings);
    } finally {
      kill.restore();
    }

    const s = state();
    return {
      payload: 'award-render-floor',
      version: 1,
      viewport: { w: window.innerWidth, h: window.innerHeight, dpr: window.devicePixelRatio || 1 },
      root: options.root || null,
      findings,
      scanned: {
        elementsSeen: candidates.elementsSeen,
        textElements: candidates.length,
        fixedExcluded: candidates.fixedExcluded,
        pairsCompared: pairs,
        scanCapped: candidates.scanCapped,
        textCapped: candidates.textCapped,
        animationsRunning: runningAnimations()
      },
      console: { armed: s.armed, armedAt: s.armedAt, captured: s.errors.length, dropped: s.dropped },
      sweep: SWEEP,
      footer: FOOTER
    };
  }

  window.awardRenderFloor = Object.assign(window.awardRenderFloor || {}, api, { arm, run });
})();
