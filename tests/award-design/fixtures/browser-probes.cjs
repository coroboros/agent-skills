const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

// Expose the real private pipelines in a VM copy. The stubs supply CSSOM and
// layout observations; production code still collects, measures and classifies.
function loadPipeline(assets, file, names, globals, mutate) {
  const source = mutate(fs.readFileSync(path.join(assets, file), 'utf8'));
  const end = source.lastIndexOf('})();');
  assert.ok(end >= 0, 'expected the asset closure');
  vm.runInNewContext(source.slice(0, end) +
    `globalThis.__probe = {${names.join(',')}};\n` + source.slice(end), globals);
  return globals.__probe;
}

function hover(assets, mutate) {
  const classes = new Set();
  const styles = [];
  const button = {
    id: 'cta', tagName: 'BUTTON', nodeType: 1, isConnected: true,
    parentElement: null, classList: classes,
    getBoundingClientRect: () => ({width: 120, height: 48}),
    matches: selector => selector === '#cta' || selector.includes('button'),
    querySelectorAll: () => [],
  };
  classes.remove = value => classes.delete(value);
  const sheet = {cssRules: [
    {selectorText: 'button:focus-visible', style: {cssText: 'outline-style: solid; outline-width: 3px;'}},
  ]};
  const document = {
    body: {}, scripts: [], styleSheets: [sheet],
    getElementById: id => styles.find(style => style.id === id),
    createElement: () => {
      const style = {textContent: '', remove: () => styles.splice(styles.indexOf(style), 1)};
      return style;
    },
    head: {appendChild: style => styles.push(style)},
    querySelectorAll: selector => button.matches(selector) ? [button] : [],
  };
  const getComputedStyle = (el, pseudo) => {
    if (pseudo) return {content: 'none'};
    const computed = {
      display: 'block', visibility: 'visible', pointerEvents: 'auto', cursor: 'pointer',
      transform: 'none', scale: 'none', translate: 'none', opacity: '1',
      color: 'rgb(0, 0, 0)', backgroundColor: 'rgb(255, 255, 255)',
      borderTopColor: 'rgb(0, 0, 0)', outlineStyle: 'none', outlineWidth: '0px',
    };
    // A small CSS adapter for this fixture's simple selectors/declarations.
    // Crucially it reads the stylesheet the production probe actually injected.
    for (const style of styles) {
      for (const [, selectorText, declarations] of style.textContent.matchAll(/([^{}]+)\{([^{}]*)\}/g)) {
        const applies = selectorText.split(',').some(selector => {
          const [base, ...required] = selector.trim().split('.');
          return !selector.includes(':') && button.matches(base) &&
            required.every(name => classes.has(name));
        });
        if (!applies) continue;
        for (const declaration of declarations.split(';')) {
          const colon = declaration.indexOf(':');
          if (colon < 0) continue;
          const name = declaration.slice(0, colon).trim().replace(/-([a-z])/g, (_, c) => c.toUpperCase());
          computed[name] = declaration.slice(colon + 1).trim();
        }
      }
    }
    return computed;
  };
  const api = loadPipeline(assets, 'detector.js', ['collectStateRules', 'probeSubstrate', 'FLOORS'],
    {window: {}, document, getComputedStyle}, mutate);
  const measure = expected => {
    const findings = [];
    const report = api.probeSubstrate(api.collectStateRules(), api.FLOORS, findings);
    assert.equal(report.counts.probed, 1);
    assert.deepEqual(Array.from(report.selectors[expected]), ['button#cta']);
    assert.equal(styles.length, 0, 'probe stylesheet must be removed');
    assert.equal(classes.size, 0, 'probe class must be removed');
    return findings;
  };
  assert.ok(measure('dead').some(f => f.id === 'DEAD'), 'focus alone cannot count as hover feedback');
  sheet.cssRules.push({selectorText: '#cta:hover', style: {cssText: 'scale: 0.98;'}});
  assert.ok(measure('homeopathic').some(f => f.id === 'HOMEOPATHIC'), 'focus must not rescue a weak hover');
  sheet.cssRules[1].style.cssText = 'translate: 0 -4px;';
  assert.ok(!measure('ok').some(f => f.id === 'DEAD' || f.id === 'HOMEOPATHIC'));
}

function clipping(assets, mutate) {
  const rect = (right, bottom) => ({left: 0, top: 0, right, bottom, width: right, height: bottom});
  let glyphs = rect(140, 20);
  const style = {display: 'block', visibility: 'visible', opacity: '1', position: 'static',
    overflowX: 'visible', overflowY: 'visible', textOverflow: 'clip', webkitLineClamp: 'none'};
  const clip = {
    id: 'clip', tagName: 'DIV', nodeType: 1, parentElement: null,
    scrollLeft: 0, scrollTop: 0, scrollWidth: 140, clientWidth: 100,
    scrollHeight: 60, clientHeight: 40,
    getBoundingClientRect: () => rect(100, 40),
  };
  const text = {nodeType: 3, textContent: 'A heading wider than its box'};
  const heading = {
    id: 'heading', tagName: 'H2', nodeType: 1, parentElement: clip,
    childNodes: [text], classList: [], closest: () => null,
    getBoundingClientRect: () => rect(100, 20),
  };
  const root = {querySelectorAll: () => [heading]};
  const document = {
    body: root,
    createRange: () => {
      let contentsSelected = false, start = null, end = null;
      return {
        selectNodeContents: el => { assert.equal(el, heading); contentsSelected = true; },
        setStart: (node, offset) => { assert.equal(node, text); start = offset; },
        setEnd: (node, offset) => { assert.equal(node, text); end = offset; },
        getClientRects: () => contentsSelected || (start !== null && end > start) ? [glyphs] : [],
      };
    },
  };
  const api = loadPipeline(assets, 'render-floor.js', ['textCandidates', 'checkTextClipped'],
    {window: {}, document, getComputedStyle: el => el === clip
      ? {...style, overflowX: 'hidden', overflowY: 'hidden'} : style}, mutate);
  const measure = () => {
    const findings = [];
    api.checkTextClipped(api.textCandidates(root), findings);
    return JSON.parse(JSON.stringify(findings));
  };
  let findings = measure();
  assert.equal(findings.length, 1, 'scroll extent without an offset is not a track exemption');
  assert.equal(findings[0].rule, 'TEXT-CLIPPED');
  assert.equal(findings[0].measurement.side, 'right');
  assert.equal(findings[0].measurement.escapePx, 40);
  assert.deepEqual(findings[0].measurement.box, {x: 0, y: 0, w: 100, h: 20});
  assert.deepEqual(findings[0].measurement.glyphBox, {x: 0, y: 0, w: 140, h: 20});
  clip.scrollLeft = 12;
  assert.deepEqual(measure(), [], 'a live horizontal track exempts the horizontal cut');
  glyphs = rect(140, 60);
  findings = measure();
  assert.equal(findings.length, 1, 'horizontal scrolling cannot excuse a vertical cut');
  assert.equal(findings[0].measurement.side, 'bottom');
  assert.equal(findings[0].measurement.escapePx, 20);
  assert.deepEqual(findings[0].measurement.exemptSides, ['left', 'right']);
  clip.scrollTop = 12;
  assert.deepEqual(measure(), [], 'both live axes may be exempted');
}

module.exports = (name, assets, mutate = source => source) => {
  ({hover, clipping})[name](assets, mutate);
};
