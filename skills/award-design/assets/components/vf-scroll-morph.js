/*
 * vf-scroll-morph — the archetype's signature text move (winners: Cyd
 * Stumpel — a variable-font axis scroll-morph carried hero-to-footer on
 * native animation-timeline; the SPECIFIC axis is unverified and the cited
 * 'ytuc' was refuted, so the component is genericized to REGISTERED axes;
 * the generic technique is verified this run via Codrops / Carmen Ansio).
 * Binds a variable-font axis to an element's own scroll view-range with
 * native CSS scroll-driven animation: font-variation-settings interpolates
 * across animation-range as the element traverses the viewport — reversible
 * by construction (scrolling back rewinds it), zero JS per frame (the
 * timeline is the scroll engine's). Honest perf note: the TIMELINE is
 * native and off-main-thread, but a font-variation change re-rasterizes the
 * glyphs — paint work per step — so this rides DISPLAY headings and
 * wordmarks (a few elements), never body prose. NOTHING else in the
 * manifest executes this: kinetic-reveal (line mask), char-assemble
 * (per-char), text-emphasis-fill (word brighten) and semantic-accent (term
 * color) are all discrete/opacity effects — none animates an axis on
 * scroll; cursor-proximity-typefield drives 'wght' from POINTER distance,
 * not scroll (the bold-maximal cousin, a different input).
 *
 * Markup — opt in per element; tune per element with custom properties:
 *   <h2 data-ad-vfm>…</h2>                          weight morph (default)
 *   <h2 data-ad-vfm="opsz">…</h2>                   optical-size morph
 *   <p data-ad-vfm style="--ad-vfm-from:250; --ad-vfm-to:900;
 *      --ad-vfm-range: entry 0% cover 60%;">…</p>
 *
 * Defaults: wght 300 -> 800 · opsz 12 -> 72 · range entry 0% cover 40%
 * (the morph completes early in the entry, so most of the dwell shows the
 * finished cut; a footer wordmark can stretch its range to exit 100%).
 *
 * Degrades by construction, every rung to a STATIC cut: no
 * animation-timeline support -> the @supports block never applies;
 * prefers-reduced-motion -> animation:none (the authored axis stands); the
 * axis absent from the loaded font -> font-variation-settings is ignored
 * and the authored static weight renders. A dead script leaves the page's
 * own type untouched.
 *
 * Usage:  awardVfScrollMorph.init(root, opts)
 *   root      Element|Document  kept for the shared init signature — the
 *                               stylesheet is attribute-driven
 * Returns { destroy() }. Idempotent. destroy() removes the stylesheet.
 *
 * Tokens: --ad-vfm-from / --ad-vfm-to (axis endpoints, per element),
 * --ad-vfm-range (any animation-range value, per element).
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-vf-scroll-morph-css';

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      '@supports (animation-timeline: view()) {' +
        // longhands after the shorthand: `animation:` resets timeline/range
        '[data-ad-vfm]{' +
          'animation:ad-vfm-wght auto linear both;' +
          'animation-timeline:view();' +
          'animation-range:var(--ad-vfm-range,entry 0% cover 40%);}' +
        '[data-ad-vfm="opsz"]{animation-name:ad-vfm-opsz;}' +
        // var() resolves per element inside keyframes — the endpoints are
        // element-tunable while the keyframes stay singular
        '@keyframes ad-vfm-wght{' +
          'from{font-variation-settings:"wght" var(--ad-vfm-from,300);}' +
          'to{font-variation-settings:"wght" var(--ad-vfm-to,800);}}' +
        '@keyframes ad-vfm-opsz{' +
          'from{font-variation-settings:"opsz" var(--ad-vfm-from,12);}' +
          'to{font-variation-settings:"opsz" var(--ad-vfm-to,72);}}' +
        '@media (prefers-reduced-motion: reduce){' +
          '[data-ad-vfm]{animation:none;}}' +
      '}';
    document.head.appendChild(s);
  }

  function init(root, opts) {
    injectCss();
    return {
      destroy: function () {
        var s = document.getElementById(CSS_ID);
        if (s && s.parentNode) s.parentNode.removeChild(s);
      }
    };
  }

  global.awardVfScrollMorph = { init: init };
})(typeof window !== 'undefined' ? window : this);
