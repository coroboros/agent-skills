/*
 * press-hold-reveal — the luxury gesture primitive: press-and-hold charges a
 * progressive reveal (winner: Louis Vuitton Collectibles — SOTD Feb 2024,
 * Animations 9.4; the click-and-hold product reveal: open the trunk / rotate
 * into detail / dissolve to the next universe. The hold band ~600-900ms,
 * default 700, is the LV-band executable default). Pressing an object
 * charges it over its declared hold duration; the charge drives the reveal
 * PROGRESSIVELY (the authored detail layer arrives with the press, not
 * after it), completes and LOCKS at a full hold, and retracts 3x faster on
 * an early release — the same retract grammar as the cursor's dial, so the
 * two instruments always agree.
 * This is the OBJECT half of the charge arc contextual-cursor-label
 * deliberately leaves to the object: the cursor is the affordance only (its
 * ring arc is a dial, it drives no reveal); this component owns completion.
 * The weld is the shared markup — both read the SAME declaration:
 *   <button data-ad-gesture="HOLD" data-ad-gesture-hold="700">
 *     …the object at rest (fully legible — the reveal only ADDS)…
 *     <div data-ad-press-detail>…the revealed detail…</div>
 *   </button>
 * so one attribute times the cursor's arc AND the object's charge — never
 * two clocks. Ruled DISTINCT, not an alias: hard-press-button is a styling
 * press (instant :active travel, no charge, no time dimension);
 * scrub-film maps scroll/pointer position to media time — nothing charges;
 * contextual-cursor-label is chrome-only by its own header ('this component
 * drives no reveal'). No manifest component held a time-charged gesture.
 *
 * The charge publishes three surfaces the build styles against:
 *   --ad-phr-charge   0..1 custom property written on the object per frame
 *   data-ad-charging  present while the press is live or retracting
 *   data-ad-revealed  the completed, locked state (+ aria-expanded when the
 *                     object is a control) — reset by removing the attribute
 * The injected CSS maps the charge onto [data-ad-press-detail] (opacity
 * rides the charge, a settle transition lands the completed state) — the
 * baseline reveal; richer responses (a rotate-into-detail, a universe
 * dissolve) style against the same three surfaces.
 *
 * Pointer + touch are BOTH first-class (pointerdown/up, cancel on leave —
 * the gap's own contract; this gesture is never pointer-gated dormant).
 * During a touch charge the context menu and text selection are suppressed
 * so a long-press stays a gesture. Keyboard: Enter/Space is a SINGLE
 * ACTIVATE — instant full reveal, no timing barrier (the gap's sanctioned
 * equivalent). Reduced motion: no progressive charge — any press or
 * activate reveals instantly (the finished state, no animation).
 * No-JS: the injected stylesheet never exists, so the authored detail is
 * plain visible content — nothing is ever unreachable.
 *
 * Usage:  awardPressHoldReveal.init(root, opts)
 *   root      Element|Document  scope (default document)
 *   selector  string    hold objects (default '[data-ad-gesture="HOLD"]')
 *   onReveal  function(el)  fires once per object at completion
 * Returns { destroy() }. Idempotent per root. destroy() clears charge
 * state, listeners, and the stylesheet (revealed attributes stay — a
 * revealed trunk does not slam shut on teardown).
 *
 * Perf: one rAF per pressed object, alive only while charging or
 * retracting; writes one custom property + attributes — the detail's
 * motion is CSS on a promoted layer.
 *
 * Tokens: --ad-dur-base + --ad-ease-signature (the completed settle).
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-press-hold-reveal-css';
  var HOLD_DEFAULT = 700;   // the LV band (~600-900ms) when undeclared —
                            // the same default as contextual-cursor-label
  var RETRACT_RATE = 3;     // matches the cursor dial's retract grammar

  var reduce = function () {
    return !!(global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches);
  };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    var settle = 'var(--ad-dur-base,420ms) var(--ad-ease-signature,cubic-bezier(.16,1,.3,1))';
    s.textContent =
      // a long-press is a gesture here, never a text selection
      '.ad-phr-host{touch-action:manipulation;}' +
      '.ad-phr-host[data-ad-charging]{-webkit-user-select:none;user-select:none;}' +
      // the baseline progressive reveal: the detail rides the charge
      '.ad-phr-host [data-ad-press-detail]{opacity:var(--ad-phr-charge,0);' +
      'will-change:opacity;}' +
      '.ad-phr-host[data-ad-revealed] [data-ad-press-detail]{opacity:1;}' +
      // the settle is motion — reduce lands the finished state instantly
      '@media (prefers-reduced-motion: no-preference){' +
      '.ad-phr-host[data-ad-revealed] [data-ad-press-detail]{' +
      'transition:opacity ' + settle + ';}}';
    document.head.appendChild(s);
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-gesture="HOLD"]';

    var hosts = Array.prototype.filter.call(
      root.querySelectorAll(selector),
      function (el) { return !el.__adPhr; }
    );
    if (!hosts.length) return { destroy: function () {} };

    injectCss();

    function reveal(host) {
      var u = host.__adPhr;
      if (!u || u.revealed) return;
      u.revealed = true;
      u.charge = 1;
      host.style.setProperty('--ad-phr-charge', '1');
      host.removeAttribute('data-ad-charging');
      host.setAttribute('data-ad-revealed', '');
      if (typeof host.getAttribute('aria-expanded') === 'string' ||
          host.tagName === 'BUTTON' || host.tagName === 'A') {
        host.setAttribute('aria-expanded', 'true');
      }
      if (opts.onReveal) opts.onReveal(host);
    }

    var units = hosts.map(function (host) {
      var declared = host.getAttribute('data-ad-gesture-hold');
      var u = {
        host: host,
        holdMs: parseInt(declared, 10) || HOLD_DEFAULT,
        charge: 0, holding: false, raf: 0, lastT: 0,
        revealed: host.hasAttribute('data-ad-revealed')
      };
      host.__adPhr = u;
      host.classList.add('ad-phr-host');
      if ((host.tagName === 'BUTTON' || host.tagName === 'A') &&
          !host.hasAttribute('aria-expanded')) {
        host.setAttribute('aria-expanded', u.revealed ? 'true' : 'false');
      }

      function frame(now) {
        u.raf = 0;
        var dt = now - u.lastT;
        u.lastT = now;
        if (u.holding) {
          u.charge = Math.min(1, u.charge + dt / u.holdMs);
          if (u.charge >= 1) { reveal(host); return; } // complete — locked
        } else {
          u.charge = Math.max(0, u.charge - dt * RETRACT_RATE / u.holdMs);
        }
        host.style.setProperty('--ad-phr-charge', u.charge.toFixed(3));
        if (u.holding || u.charge > 0) u.raf = global.requestAnimationFrame(frame);
        else host.removeAttribute('data-ad-charging'); // retract landed empty
      }
      function wake() {
        if (!u.raf) {
          u.lastT = performance.now();
          u.raf = global.requestAnimationFrame(frame);
        }
      }

      u.onDown = function (e) {
        if (u.revealed || e.button > 0) return;
        // Reduce: the press IS the activation — no timed charge.
        if (reduce()) { reveal(host); return; }
        u.holding = true;
        host.setAttribute('data-ad-charging', '');
        wake();
      };
      u.onUp = function () {
        if (!u.holding) return;
        u.holding = false; // early release — the frame loop retracts at 3x
        wake();
      };
      // cancel on leave — the gap's own contract; a wandering press never
      // completes off-object
      u.onLeave = u.onUp;
      u.onKey = function (e) {
        if (e.key !== 'Enter' && e.key !== ' ') return;
        e.preventDefault(); // no synthesized click double-firing
        if (!u.revealed) reveal(host); // single activate — no timing barrier
      };
      u.onMenu = function (e) {
        if (u.holding || u.charge > 0) e.preventDefault(); // long-press stays a gesture
      };

      host.addEventListener('pointerdown', u.onDown);
      host.addEventListener('pointerup', u.onUp);
      host.addEventListener('pointercancel', u.onUp);
      host.addEventListener('pointerleave', u.onLeave);
      host.addEventListener('keydown', u.onKey);
      host.addEventListener('contextmenu', u.onMenu);
      return u;
    });

    return {
      destroy: function () {
        units.forEach(function (u) {
          if (u.raf) global.cancelAnimationFrame(u.raf);
          u.host.removeEventListener('pointerdown', u.onDown);
          u.host.removeEventListener('pointerup', u.onUp);
          u.host.removeEventListener('pointercancel', u.onUp);
          u.host.removeEventListener('pointerleave', u.onLeave);
          u.host.removeEventListener('keydown', u.onKey);
          u.host.removeEventListener('contextmenu', u.onMenu);
          u.host.classList.remove('ad-phr-host');
          u.host.removeAttribute('data-ad-charging');
          u.host.style.removeProperty('--ad-phr-charge');
          delete u.host.__adPhr;
          // data-ad-revealed stands — a revealed trunk never slams shut
        });
        units = [];
        var s = document.getElementById(CSS_ID);
        if (s && s.parentNode) s.parentNode.removeChild(s);
      }
    };
  }

  global.awardPressHoldReveal = { init: init };
})(typeof window !== 'undefined' ? window : this);
