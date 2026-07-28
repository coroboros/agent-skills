/*
 * gated-splash — costumed threshold / enter gate (winner: Siena Film Foundation).
 * A full-viewport overlay the visitor crosses to enter, whose ENTER control also
 * gates sound/motion. The gate is authored in the DOM carrying `hidden`, so with
 * no JS — or a dead script — it stays hidden and the page reads in full: the gate
 * is added by JS, never required to see the page (no blackout). On enter it lifts
 * off the top under the signature easing, hands focus back to the page, and drops
 * out of the a11y tree and tab order. reduced-motion lifts instantly, no wipe.
 *
 * Expected markup — authored `hidden`; JS un-hides and runs it:
 *   <div data-ad-gate hidden>
 *     <div data-ad-gate-inner>
 *       <p class="mono">A FILM FOUNDATION</p>
 *       <h2 data-ad-gate-mark>Enter the archive</h2>
 *       <button data-ad-gate-enter type="button">Enter <span aria-hidden="true">(with sound)</span></button>
 *     </div>
 *   </div>
 *
 * Usage:  awardGatedSplash.init(root, { selector, onEnter })
 *   root      Element|Document  scope (default document)
 *   selector  string            the gate (default '[data-ad-gate]')
 *   onEnter   function          run once, after the lift — wire audio / muted-video
 *                               start here; the component hardcodes no media.
 * Returns { destroy() }. Idempotent — a second init once entered is a no-op; while
 * still gating it returns the live handle. destroy() restores the original `hidden`,
 * releases the focus trap, and removes the stylesheet.
 *
 * Tokens: --ad-ground (oklch(14% 0.01 260)) + --ad-ink (oklch(96% 0 0)) paint the
 * overlay; --ad-dur-reveal (800ms) + --ad-ease-signature (cubic-bezier(.16,1,.3,1))
 * time the lift; --ad-accent, --ad-font-display, --ad-font-mono, --ad-dur-base dress
 * the threshold.
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-gated-splash-css';
  // Tab-reachable focusables — for the trap and for the release target.
  var FOCUSABLE = 'a[href],area[href],button:not([disabled]),input:not([disabled]),' +
    'select:not([disabled]),textarea:not([disabled]),iframe,' +
    '[tabindex]:not([tabindex="-1"]),[contenteditable="true"]';

  var reduce = function () {
    return global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches;
  };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    // Every rule is scoped under .ad-gate — the class JS adds after removing
    // `hidden`. No-JS never gets the class, so the UA `[hidden]` display:none
    // stands and the page shows with no gate.
    s.textContent =
      '.ad-gate{position:fixed;inset:0;z-index:100000;display:flex;' +
        'align-items:center;justify-content:center;padding:8vmin;' +
        'background:var(--ad-ground,oklch(14% 0.01 260));' +
        'color:var(--ad-ink,oklch(96% 0 0));overflow:hidden;will-change:transform;}' +
      '.ad-gate[data-ad-entered]{display:none;}' +
      '.ad-gate [data-ad-gate-inner]{display:flex;flex-direction:column;align-items:center;' +
        'gap:1.5rem;text-align:center;max-width:44rem;}' +
      '.ad-gate .mono{margin:0;font-family:var(--ad-font-mono,ui-monospace,monospace);' +
        'font-size:.75rem;letter-spacing:.28em;text-transform:uppercase;opacity:.66;}' +
      '.ad-gate [data-ad-gate-mark]{margin:0;font-family:var(--ad-font-display,inherit);' +
        'font-size:clamp(2rem,6vw,4.5rem);line-height:1.02;}' +
      '.ad-gate [data-ad-gate-enter]{margin-top:.5rem;cursor:pointer;color:inherit;' +
        'font-family:var(--ad-font-mono,ui-monospace,monospace);font-size:.8rem;' +
        'letter-spacing:.18em;text-transform:uppercase;' +
        'background:transparent;border:1px solid currentColor;border-radius:0;padding:1em 2em;' +
        'transition:color var(--ad-dur-base,420ms) var(--ad-ease-signature,cubic-bezier(.16,1,.3,1)),' +
        'background-color var(--ad-dur-base,420ms) var(--ad-ease-signature,cubic-bezier(.16,1,.3,1)),' +
        'border-color var(--ad-dur-base,420ms) var(--ad-ease-signature,cubic-bezier(.16,1,.3,1));}' +
      '.ad-gate [data-ad-gate-enter]:hover,.ad-gate [data-ad-gate-enter]:focus-visible{' +
        'background:var(--ad-accent,oklch(62% 0.2 25));' +
        'border-color:var(--ad-accent,oklch(62% 0.2 25));color:var(--ad-ground,oklch(14% 0.01 260));}' +
      '.ad-gate [data-ad-gate-enter] span{opacity:.7;}' +
      '@media (prefers-reduced-motion: reduce){.ad-gate [data-ad-gate-enter]{transition:none;}}';
    document.head.appendChild(s);
  }

  function styles() {
    var cs = getComputedStyle(document.documentElement);
    return {
      dur: (cs.getPropertyValue('--ad-dur-reveal') || '800ms').trim() || '800ms',
      ease: (cs.getPropertyValue('--ad-ease-signature') || '').trim() ||
        'cubic-bezier(.16,1,.3,1)'
    };
  }

  function isVisible(el) {
    // getClientRects (not offsetParent) — the gate is position:fixed, whose
    // descendants report offsetParent null yet are on-screen.
    return !el.disabled && el.getClientRects().length > 0;
  }

  function focusablesIn(container) {
    var out = [];
    var list = container.querySelectorAll(FOCUSABLE);
    for (var i = 0; i < list.length; i++) {
      if (isVisible(list[i])) out.push(list[i]);
    }
    return out;
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-gate]';
    var onEnter = typeof opts.onEnter === 'function' ? opts.onEnter : null;

    var gate = root.querySelector(selector);
    if (!gate) return { destroy: function () {} };

    // Idempotent: entered → no-op; still gating → the live handle (no rebind).
    var prev = gate.__adGate;
    if (prev) return prev.entered ? { destroy: function () {} } : prev.handle;

    injectCss();
    var enterBtn = gate.querySelector('[data-ad-gate-enter]');
    var hadHidden = gate.hasAttribute('hidden');
    var state = { entered: false, entering: false, anim: null, handle: null };
    gate.__adGate = state;

    function trapKeydown(e) {
      if (e.key !== 'Tab' && e.keyCode !== 9) return;
      var f = focusablesIn(gate);
      if (!f.length) { e.preventDefault(); return; }
      var first = f[0], last = f[f.length - 1];
      var active = document.activeElement;
      if (e.shiftKey) {
        if (active === first || !gate.contains(active)) { e.preventDefault(); last.focus(); }
      } else {
        if (active === last || !gate.contains(active)) { e.preventDefault(); first.focus(); }
      }
    }

    function releaseFocus() {
      var all = document.querySelectorAll(FOCUSABLE);
      for (var i = 0; i < all.length; i++) {
        if (!gate.contains(all[i]) && isVisible(all[i])) { all[i].focus(); return; }
      }
      // Nothing else to land on — drop focus off the about-to-be-hidden control
      // so it never lingers on a display:none node.
      if (document.activeElement && document.activeElement.blur) document.activeElement.blur();
    }

    function finalize() {
      state.anim = null;
      state.entering = false;
      state.entered = true;
      // Focus leaves the gate BEFORE aria-hidden/display:none — aria-hidden must
      // never sit on an ancestor of the focused node.
      releaseFocus();
      gate.setAttribute('aria-hidden', 'true');
      gate.setAttribute('data-ad-entered', ''); // → display:none, out of tab order
      // Never trap after entering.
      document.removeEventListener('keydown', trapKeydown, true);
      if (enterBtn) enterBtn.removeEventListener('click', onActivate);
      if (onEnter) onEnter();
    }

    function lift() {
      if (reduce() || !gate.animate) { finalize(); return; }
      var s = styles();
      state.anim = gate.animate(
        [{ transform: 'translateY(0)' }, { transform: 'translateY(-100%)' }],
        { duration: parseFloat(s.dur), easing: s.ease, fill: 'forwards' }
      );
      state.anim.onfinish = finalize;
    }

    // A native button dispatches click on pointer, Enter, and Space — one click
    // listener covers all three with no double-fire.
    function onActivate() {
      if (state.entered || state.entering) return;
      state.entering = true;
      lift();
    }

    // Open: un-hide, promote to the JS-only visible class, trap + focus the control.
    gate.removeAttribute('hidden');
    gate.removeAttribute('aria-hidden');
    gate.classList.add('ad-gate');
    document.addEventListener('keydown', trapKeydown, true);
    if (enterBtn) enterBtn.addEventListener('click', onActivate);
    if (enterBtn) enterBtn.focus();

    var handle = {
      destroy: function () {
        document.removeEventListener('keydown', trapKeydown, true);
        if (enterBtn) enterBtn.removeEventListener('click', onActivate);
        if (state.anim) { state.anim.cancel(); state.anim = null; }
        gate.classList.remove('ad-gate');
        gate.style.transform = '';
        gate.removeAttribute('aria-hidden');
        gate.removeAttribute('data-ad-entered');
        if (hadHidden) gate.setAttribute('hidden', '');
        else gate.removeAttribute('hidden');
        delete gate.__adGate;
        var st = document.getElementById(CSS_ID);
        if (st && st.parentNode) st.parentNode.removeChild(st);
      }
    };
    state.handle = handle;
    return handle;
  }

  global.awardGatedSplash = { init: init };
})(typeof window !== 'undefined' ? window : this);
