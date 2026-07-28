/*
 * full-page-scrub-recolor-carry — per-CHAR recolor scrubbed across the FULL
 * page height (winner: Terminal Industries; the per-char recolor mechanic is
 * CSS-verified across prior rounds, corroborated by the 8.80 Animations
 * sub-score). The sustained substrate carry: every char of every opted-in
 * block joins ONE document-ordered sequence, and a single GLOBAL page-progress
 * driver brightens chars dim→ink as the page scrolls — the reading text
 * itself is the continuous thread hero-to-footer, not a bank of per-block
 * reveals. Distinct from text-emphasis-fill's scrub (per-WORD, per-BLOCK
 * viewport traversal): here the driver is scrollY over the whole document and
 * the granularity is the char. Reversible by construction — scroll back and
 * the recolor walks back. The dim floor keeps every char legible (an
 * emphasis, never a reveal-from-invisible); no-JS and dead-script renders
 * show plain full-bright text (the dim state is JS-applied), and
 * reduced-motion never splits — the finished state is the page.
 *
 * The global-driver specifics are partly single-source: the lead default
 * (how far the lit boundary runs ahead of raw page progress, so the last
 * lines land before the absolute bottom) is a sane calibration, not a
 * winner-verified number — retune via opts.lead or --ad-recolor-lead.
 *
 * Usage:  awardPageRecolor.init(root, { selector, floor, lead })
 *   root      Element|Document  scope (default document)
 *   selector  string   blocks whose text joins the carry
 *                      (default '[data-ad-recolor]')
 *   floor     number   dim floor opacity (default 0.45 — keep legible;
 *                      CSS --ad-recolor-floor overrides the default)
 *   lead      number   boundary lead over raw progress (default 0.15;
 *                      CSS --ad-recolor-lead overrides the default)
 * Returns { destroy() }. Idempotent — re-init on the same root replaces the
 * prior instance. Chars are plain inline spans with real space text nodes
 * between words, so native line wrapping and the accessible text stay whole;
 * inline ELEMENTS (a semantic-accent term, a <strong>) are preserved intact
 * and recolored as one unit (the text-emphasis-fill lesson).
 *
 * Perf: one passive scroll listener, one rAF; each frame writes only the
 * DELTA of chars whose lit state crossed the boundary — never the whole set.
 *
 * Tokens: --ad-dur-base (420ms) + --ad-ease-signature ease each char's step.
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-page-recolor-css';
  var reduce = function () {
    return global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches;
  };
  var clamp = function (v, lo, hi) { return v < lo ? lo : v > hi ? hi : v; };

  function injectCss(floor) {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      '.ad-recolor__c{transition:opacity var(--ad-dur-base,420ms) ' +
      'var(--ad-ease-signature,cubic-bezier(.16,1,.3,1));}' +
      // the dim state exists only under the JS-set armed attribute → no-JS is bright
      '[data-ad-recolor-armed] .ad-recolor__c{opacity:' + floor + ';}' +
      '[data-ad-recolor-armed] .ad-recolor__c.is-lit{opacity:1;}' +
      '@media (prefers-reduced-motion:reduce){' +
      '.ad-recolor__c{transition:none;}' +
      '[data-ad-recolor-armed] .ad-recolor__c{opacity:1;}}';
    document.head.appendChild(s);
  }

  function cssNumber(name) {
    if (!global.getComputedStyle || !document.documentElement) return NaN;
    return parseFloat(global.getComputedStyle(document.documentElement).getPropertyValue(name));
  }
  function setting(optValue, cssProp, fallback) {
    if (optValue != null) return optValue;
    var fromCss = cssNumber(cssProp);
    return isNaN(fromCss) ? fallback : fromCss;
  }

  // Per-char spans inside each text run; real spaces stay text nodes, so line
  // breaking and the accessible text are untouched. Inline elements stay whole.
  function splitChars(el, out) {
    if (el.__adRecolorHTML == null) el.__adRecolorHTML = el.innerHTML;
    else el.innerHTML = el.__adRecolorHTML;
    var nodes = Array.prototype.slice.call(el.childNodes);
    el.textContent = '';
    nodes.forEach(function (node) {
      if (node.nodeType === 1) {
        node.classList.add('ad-recolor__c');
        el.appendChild(node);
        out.push(node);
        return;
      }
      if (node.nodeType !== 3) return;
      var text = node.textContent;
      for (var i = 0; i < text.length; i++) {
        var ch = text.charAt(i);
        if (/\s/.test(ch)) { el.appendChild(document.createTextNode(ch)); continue; }
        var span = document.createElement('span');
        span.className = 'ad-recolor__c';
        span.textContent = ch;
        el.appendChild(span);
        out.push(span);
      }
    });
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-recolor]';
    var floor = setting(opts.floor, '--ad-recolor-floor', 0.45);
    var lead = setting(opts.lead, '--ad-recolor-lead', 0.15);
    injectCss(floor);

    if (root.__adPageRecolor) root.__adPageRecolor.destroy();

    // querySelectorAll returns document order — the sequence IS the reading order.
    var blocks = Array.prototype.slice.call(root.querySelectorAll(selector));
    var chars = [];
    var lit = 0;
    var rafId = 0;
    var onScroll = null;

    function apply(next) {
      if (next === lit) return;
      // delta writes only — the boundary walks, the rest of the page is untouched
      var lo = Math.min(lit, next), hi = Math.max(lit, next), on = next > lit;
      for (var i = lo; i < hi; i++) chars[i].classList.toggle('is-lit', on);
      lit = next;
    }

    function frame() {
      rafId = 0;
      var vh = global.innerHeight || document.documentElement.clientHeight;
      var dh = document.documentElement.scrollHeight;
      var y = global.scrollY || global.pageYOffset || 0;
      var p = clamp(y / Math.max(1, dh - vh), 0, 1);
      var boundary = clamp(p * (1 + lead), 0, 1);
      apply(Math.round(boundary * chars.length));
    }
    function kick() { if (!rafId) rafId = global.requestAnimationFrame(frame); }

    if (!reduce() && blocks.length) {
      blocks.forEach(function (el) {
        splitChars(el, chars);
        el.setAttribute('data-ad-recolor-armed', '');
      });
      onScroll = function () { kick(); };
      global.addEventListener('scroll', onScroll, { passive: true });
      global.addEventListener('resize', onScroll, { passive: true });
      kick(); // seed — a page loaded mid-scroll lights its read run immediately
    }
    // reduce(): no split at all — untouched text is plain and full-bright.

    var handle = {
      destroy: function () {
        if (rafId) global.cancelAnimationFrame(rafId);
        if (onScroll) {
          global.removeEventListener('scroll', onScroll);
          global.removeEventListener('resize', onScroll);
        }
        blocks.forEach(function (el) {
          if (el.__adRecolorHTML != null) {
            el.innerHTML = el.__adRecolorHTML;
            delete el.__adRecolorHTML;
          }
          el.removeAttribute('data-ad-recolor-armed');
        });
        chars = [];
        var s = document.getElementById(CSS_ID);
        if (s && s.parentNode) s.parentNode.removeChild(s);
        if (root.__adPageRecolor === handle) delete root.__adPageRecolor;
      }
    };
    root.__adPageRecolor = handle;
    return handle;
  }

  global.awardPageRecolor = { init: init };
})(typeof window !== 'undefined' ? window : this);
