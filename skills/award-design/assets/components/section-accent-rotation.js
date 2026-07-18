/*
 * section-accent-rotation — the SATURATED-register per-section color world
 * (winner: DICH Fashion — SOTD + Dev Award 2025-06, 'each section had its
 * own visual temperature' — the SINGLE corpus winner; Figma's per-section
 * brand hues are the design-canonical second source). NOT the archetype's
 * universal color rule: the other seven bold-maximal corpus sites are B&W,
 * single-hue, 2-hue or cream monochrome — apply this ONLY on a saturated /
 * warm-maximal register, never on a kinetic-register build.
 * The single-accent token contract cannot express DICH's chapters — this
 * component makes the SECTION the color scope: as each section claims the
 * viewport-center band, its declared accent (and optional ground
 * temperature) is written to --ad-accent (and --ad-ground) on the target
 * scope, so every token-reading component inherits the section's color
 * world with no per-component change.
 * THE ROLE LAW (drive-verified): the rotation swaps the VALUE of one role,
 * never re-deals jobs — each section's hue holds the same ONE job (the
 * accent: links, fills, kickers, state colors), the ground swap holds the
 * temperature job, and ink never rotates. A hue that shows up as accent in
 * one section and as ink or décor in another is the drift this contract
 * forbids.
 * Zero-flip by construction: the active section is the one whose band
 * contains the viewport center (IntersectionObserver, rootMargin -50%/-50%),
 * exactly one owner at a time, writes only on a real owner change.
 *
 * Declared markup — per-section attributes win over the rotation array:
 *   <section data-ad-sar data-ad-sar-accent="oklch(70% 0.19 40)"
 *            data-ad-sar-ground="oklch(16% 0.03 40)">…</section>
 *   <section data-ad-sar>…</section>  ← takes accents[i % accents.length]
 *
 * Usage:  awardSectionAccentRotation.init(root, opts)
 *   root     Element|Document  scope (default document)
 *   selector string    sections (default '[data-ad-sar]')
 *   accents  string[]  rotation array for sections with no declared accent
 *   grounds  string[]  companion grounds (optional, same indexing)
 *   target   Element   the scope the vars land on (default
 *                      document.documentElement; the ground paint class
 *                      lands on document.body)
 * Returns { destroy() }. Idempotent per root. The component never invents
 * color — sections with no declared or rotated accent are left out; with
 * nothing declared anywhere init is a no-op.
 *
 * When any ground is in play the body takes a JS-applied class painting
 * background-color: var(--ad-ground) with an unhurried transition
 * (--ad-dur-reveal), so the temperature swap eases instead of flipping.
 * The active section carries data-ad-sar-active (state rides data
 * attributes) for builders' own hooks.
 * reduced-motion: no live rotation, no eased ground — each declaring
 * section becomes its OWN static color scope (--ad-accent inline on the
 * section, its declared ground as a static background-color), so the
 * hue-per-section identity survives with zero global mutation — the
 * section-scale-momentum static-end answer. No JS: the authored page
 * stands untouched.
 *
 * Tokens: WRITES --ad-accent / --ad-ground; reads --ad-dur-reveal +
 * --ad-ease-signature for the ground ease.
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-section-accent-rotation-css';

  var reduce = function () {
    return !!(global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches);
  };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      '.ad-sar-ground{background-color:var(--ad-ground,oklch(14% 0.01 260));' +
      'transition:background-color var(--ad-dur-reveal,800ms) ' +
      'var(--ad-ease-signature,cubic-bezier(.16,1,.3,1));}' +
      '@media (prefers-reduced-motion:reduce){.ad-sar-ground{transition:none;}}';
    document.head.appendChild(s);
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-sar]';
    var accents = opts.accents || [];
    var grounds = opts.grounds || [];
    var target = opts.target || document.documentElement;

    // Resolve each section's world: declared attribute > rotation array.
    var sections = [];
    Array.prototype.forEach.call(root.querySelectorAll(selector), function (el, i) {
      var accent = el.getAttribute('data-ad-sar-accent') ||
        (accents.length ? accents[i % accents.length] : null);
      var ground = el.getAttribute('data-ad-sar-ground') ||
        (grounds.length ? grounds[i % grounds.length] : null);
      if (!accent && !ground) return; // never invent color
      sections.push({ el: el, accent: accent, ground: ground });
    });
    if (!sections.length) return { destroy: function () {} };

    // Reduced motion: each section is its own static color scope.
    if (reduce()) {
      sections.forEach(function (s) {
        if (s.accent) s.el.style.setProperty('--ad-accent', s.accent);
        if (s.ground) {
          s.el.style.setProperty('--ad-ground', s.ground);
          s.el.style.backgroundColor = s.ground;
        }
      });
      return {
        destroy: function () {
          sections.forEach(function (s) {
            s.el.style.removeProperty('--ad-accent');
            s.el.style.removeProperty('--ad-ground');
            s.el.style.backgroundColor = '';
          });
        }
      };
    }

    injectCss();
    if (root.__adSectionAccentRotation) root.__adSectionAccentRotation.destroy();

    var anyGround = sections.some(function (s) { return !!s.ground; });
    var body = document.body || document.documentElement;
    var prevAccent = target.style.getPropertyValue('--ad-accent');
    var prevGround = target.style.getPropertyValue('--ad-ground');
    if (anyGround) body.classList.add('ad-sar-ground');

    var active = null;
    function activate(s) {
      if (s === active) return; // zero-flip: write only on a real owner change
      if (active) active.el.removeAttribute('data-ad-sar-active');
      active = s;
      s.el.setAttribute('data-ad-sar-active', '');
      if (s.accent) target.style.setProperty('--ad-accent', s.accent);
      if (s.ground) target.style.setProperty('--ad-ground', s.ground);
    }

    // The center band: a section is the owner while it crosses the viewport's
    // vertical midline — exactly one at a time.
    var io = null;
    if ('IntersectionObserver' in global) {
      io = new IntersectionObserver(function (entries) {
        var winner = null;
        entries.forEach(function (e) {
          if (!e.isIntersecting) return;
          sections.forEach(function (s) { if (s.el === e.target) winner = s; });
        });
        if (winner) activate(winner);
      }, { rootMargin: '-50% 0% -50% 0%', threshold: 0 });
      sections.forEach(function (s) { io.observe(s.el); });
    }

    // Initial owner — the section whose band already holds the center.
    var mid = (global.innerHeight || 0) / 2;
    for (var i = 0; i < sections.length; i++) {
      var r = sections[i].el.getBoundingClientRect();
      if (r.top <= mid && r.bottom >= mid) { activate(sections[i]); break; }
    }

    var handle = {
      destroy: function () {
        if (io) io.disconnect();
        if (active) active.el.removeAttribute('data-ad-sar-active');
        if (prevAccent) target.style.setProperty('--ad-accent', prevAccent);
        else target.style.removeProperty('--ad-accent');
        if (prevGround) target.style.setProperty('--ad-ground', prevGround);
        else target.style.removeProperty('--ad-ground');
        body.classList.remove('ad-sar-ground');
        var s = document.getElementById(CSS_ID);
        if (s && s.parentNode) s.parentNode.removeChild(s);
        if (root.__adSectionAccentRotation === handle) delete root.__adSectionAccentRotation;
      }
    };
    root.__adSectionAccentRotation = handle;
    return handle;
  }

  global.awardSectionAccentRotation = { init: init };
})(typeof window !== 'undefined' ? window : this);
