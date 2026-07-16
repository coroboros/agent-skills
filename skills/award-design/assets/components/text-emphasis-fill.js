/*
 * text-emphasis-fill — scroll emphasis on legible copy (winner: Terminal Industries).
 * The tier's text signature, two channels:
 *   scrub    — each word of an already-legible block brightens dim→bright as the
 *              block traverses the viewport; reversible and scroll-linked, legal
 *              as décor because the copy is NEVER illegible (the dim floor is
 *              0.45 opacity, an emphasis, not a reveal-from-invisible).
 *   entrance — words arrive AS the accent colour and settle to ink, staggered,
 *              fire-once — colour does the entering, then hands back to the page.
 * No-JS and dead-script renders show plain full-bright text (the dim state is
 * JS-applied); reduced-motion shows the finished state instantly.
 *
 * Usage:  awardTextEmphasis.init(root, { selector, mode, floor, stagger })
 *   selector  string   blocks to treat (default '[data-ad-emphasis]')
 *   mode      string   'scrub' | 'entrance' (default reads data-ad-emphasis
 *                      value, else 'scrub')
 *   floor     number   scrub dim floor opacity (default 0.45 — keep legible)
 *   stagger   ms       entrance per-word stagger (default 40)
 * Returns { destroy() }. Idempotent. Words are split with real space text nodes
 * between boxes, so the accessible name stays intact.
 *
 * Tokens: --ad-accent, --ad-dur-base (420ms), --ad-ease-signature.
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-text-emphasis-css';
  var reduce = function () {
    return global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches;
  };
  var clamp = function (v, lo, hi) { return v < lo ? lo : v > hi ? hi : v; };

  function injectCss(floor) {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      '.ad-emph__w{display:inline;transition:opacity var(--ad-dur-base,420ms) ' +
      'var(--ad-ease-signature,cubic-bezier(.16,1,.3,1)),color var(--ad-dur-base,420ms) ' +
      'var(--ad-ease-signature,cubic-bezier(.16,1,.3,1));}' +
      '[data-ad-emphasis-mode="scrub"] .ad-emph__w{opacity:' + floor + ';}' +
      '[data-ad-emphasis-mode="scrub"] .ad-emph__w.is-lit{opacity:1;}' +
      '[data-ad-emphasis-mode="entrance"] .ad-emph__w{color:var(--ad-accent,oklch(62% 0.2 25));}' +
      '[data-ad-emphasis-mode="entrance"] .ad-emph__w.is-settled{color:inherit;}' +
      '@media (prefers-reduced-motion:reduce){' +
      '.ad-emph__w{transition:none;}' +
      '[data-ad-emphasis-mode="scrub"] .ad-emph__w{opacity:1;}' +
      '[data-ad-emphasis-mode="entrance"] .ad-emph__w{color:inherit;}}';
    document.head.appendChild(s);
  }

  // Word boxes with real space text nodes between them — keeps line wrapping
  // native and the accessible name whole (the kinetic-reveal lesson). Inline
  // ELEMENTS (a semantic-accent term, a <strong>) are preserved intact and
  // choreographed as one word unit — flattening them via textContent would
  // silently strip the markup the two-channel pattern combines with.
  function splitWords(el) {
    if (el.__adEmphHTML == null) el.__adEmphHTML = el.innerHTML;
    else el.innerHTML = el.__adEmphHTML;
    var nodes = Array.prototype.slice.call(el.childNodes);
    el.textContent = '';
    var spans = [];
    nodes.forEach(function (node) {
      if (node.nodeType === 1) {
        node.classList.add('ad-emph__w');
        el.appendChild(node);
        spans.push(node);
        return;
      }
      if (node.nodeType !== 3) return;
      var parts = node.textContent.split(/(\s+)/);
      parts.forEach(function (part) {
        if (!part) return;
        if (/^\s+$/.test(part)) { el.appendChild(document.createTextNode(' ')); return; }
        var span = document.createElement('span');
        span.className = 'ad-emph__w';
        span.textContent = part;
        el.appendChild(span);
        spans.push(span);
      });
    });
    return spans;
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-emphasis]';
    var floor = opts.floor != null ? opts.floor : 0.45;
    var stagger = opts.stagger != null ? opts.stagger : 40;
    injectCss(floor);

    var els = Array.prototype.slice.call(root.querySelectorAll(selector));
    var units = [];
    var io = null;
    var rafId = 0;
    var onScroll = null;

    function modeFor(el) {
      var v = (el.getAttribute('data-ad-emphasis') || '').trim();
      return opts.mode || (v === 'entrance' ? 'entrance' : 'scrub');
    }

    // Scrub progress: the block's traversal of the viewport, enter-bottom to
    // exit-top — same mapping as scrub-film's free mode, biased so the block
    // is fully lit by the time it is centred (readers should never wait on
    // words below their eye line).
    function progress(el) {
      var vh = global.innerHeight || document.documentElement.clientHeight;
      var r = el.getBoundingClientRect();
      return clamp(((vh - r.top) / (vh * 0.6 + r.height)), 0, 1);
    }

    function frame() {
      rafId = 0;
      units.forEach(function (u) {
        if (u.mode !== 'scrub' || !u.inView) return;
        var lit = Math.round(progress(u.el) * u.spans.length);
        if (lit === u.lit) return;
        u.lit = lit;
        u.spans.forEach(function (s, i) { s.classList.toggle('is-lit', i < lit); });
      });
    }
    function kick() { if (!rafId) rafId = global.requestAnimationFrame(frame); }

    function playEntrance(u) {
      if (u.played) return;
      u.played = true;
      u.spans.forEach(function (s, i) {
        global.setTimeout(function () { s.classList.add('is-settled'); }, i * stagger);
      });
    }

    if (!reduce()) {
      units = els.map(function (el) {
        var mode = modeFor(el);
        el.setAttribute('data-ad-emphasis-mode', mode);
        return { el: el, mode: mode, spans: splitWords(el), lit: -1, inView: false, played: false };
      });

      if ('IntersectionObserver' in global) {
        io = new IntersectionObserver(function (entries) {
          entries.forEach(function (e) {
            var u = units.filter(function (x) { return x.el === e.target; })[0];
            if (!u) return;
            u.inView = e.isIntersecting;
            if (!e.isIntersecting) return;
            if (u.mode === 'entrance') { playEntrance(u); io.unobserve(u.el); }
            else kick();
          });
        }, { threshold: 0 });
        units.forEach(function (u) { io.observe(u.el); });
      } else {
        units.forEach(function (u) {
          if (u.mode === 'entrance') playEntrance(u);
          else { u.inView = true; }
        });
        kick();
      }

      onScroll = function () { kick(); };
      global.addEventListener('scroll', onScroll, { passive: true });
      global.addEventListener('resize', onScroll, { passive: true });
    }
    // reduce(): no split at all — the CSS @media already forces the finished
    // look for any pre-split markup, and untouched text is plain and legible.

    return {
      destroy: function () {
        if (rafId) global.cancelAnimationFrame(rafId);
        if (io) io.disconnect();
        if (onScroll) {
          global.removeEventListener('scroll', onScroll);
          global.removeEventListener('resize', onScroll);
        }
        units.forEach(function (u) {
          if (u.el.__adEmphHTML != null) { u.el.innerHTML = u.el.__adEmphHTML; delete u.el.__adEmphHTML; }
          u.el.removeAttribute('data-ad-emphasis-mode');
        });
        units = [];
        var s = document.getElementById(CSS_ID);
        if (s) s.parentNode.removeChild(s);
      }
    };
  }

  global.awardTextEmphasis = { init: init };
})(typeof window !== 'undefined' ? window : this);
