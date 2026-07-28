/*
 * about-overlay-footer — form enhancer (winner: Aristide Benoist Portfolio
 * 2021; see forms/about-overlay-footer.css for the full ruling). The footer
 * section IS the About overlay: an About trigger ([data-ad-aof-open], a real
 * anchor to the footer's fragment) promotes the in-flow footer to a modal
 * overlay over the live index — role=dialog + aria-modal, the close control
 * un-hidden, every sibling of the form made `inert`, body scroll locked,
 * focus trapped (Tab cycles, Esc closes), focus returned to the trigger on
 * close. All of it is enhancer writes: the stylesheet hides nothing and
 * animates nothing; with a dead script the anchor simply jumps to the
 * footer in flow. The open/close move is a WAAPI rise/settle on the
 * signature easing; reduced-motion opens and closes instantly.
 *
 * Usage:  awardAboutOverlayFooter.init(root, { selector, openSelector })
 *   root          Element|Document  scope (default document)
 *   selector      string  the form root (default '[data-ad-form="about-overlay-footer"]')
 *   openSelector  string  triggers (default '[data-ad-aof-open]')
 * Returns { destroy() } — destroy closes an open overlay and unbinds.
 * Idempotent per root (one handle per form root).
 */
(function (global) {
  'use strict';

  var reduce = function () {
    return !!(global.matchMedia &&
      global.matchMedia('(prefers-reduced-motion: reduce)').matches);
  };

  // Tab-reachable focusables — for the trap and the initial focus target.
  function focusablesIn(container) {
    var sel = 'a[href], button:not([disabled]), input:not([disabled]), ' +
      'select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';
    return Array.prototype.filter.call(container.querySelectorAll(sel), function (el) {
      return el.offsetParent !== null || el === document.activeElement;
    });
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-form="about-overlay-footer"]';
    var openSelector = opts.openSelector || '[data-ad-aof-open]';

    var section = (root.matches && root.matches(selector))
      ? root
      : (root.querySelector ? root.querySelector(selector) : null);
    if (!section) return { destroy: function () {} };
    if (section.__adAboutOverlayFooter) return section.__adAboutOverlayFooter;

    var closeBtn = section.querySelector('[data-slot="close"]');
    var triggers = Array.prototype.slice.call(
      (root.querySelectorAll ? root : document).querySelectorAll(openSelector));
    var open = false;
    var lastTrigger = null;
    var inerted = [];          // siblings we set inert on — restored exactly
    var prevBodyOverflow = '';
    var anim = null;

    function siblings() {
      var out = [];
      var p = section.parentNode;
      if (!p) return out;
      for (var i = 0; i < p.children.length; i++) {
        if (p.children[i] !== section) out.push(p.children[i]);
      }
      return out;
    }

    function openOverlay(trigger) {
      if (open) return;
      open = true;
      lastTrigger = trigger || null;
      section.setAttribute('data-mode', 'overlay');
      section.setAttribute('role', 'dialog');
      section.setAttribute('aria-modal', 'true');
      if (closeBtn) closeBtn.hidden = false;
      siblings().forEach(function (el) {
        if (!el.inert) { el.inert = true; inerted.push(el); }
      });
      prevBodyOverflow = document.body.style.overflow;
      document.body.style.overflow = 'hidden';
      section.scrollTop = 0;
      var target = closeBtn || focusablesIn(section)[0] || section;
      if (target === section) section.setAttribute('tabindex', '-1');
      target.focus({ preventScroll: true });
      if (!reduce() && section.animate) {
        anim = section.animate(
          [{ transform: 'translateY(24px)', opacity: 0 },
           { transform: 'translateY(0)', opacity: 1 }],
          { duration: 480, easing: 'cubic-bezier(.16,1,.3,1)' });
      }
      document.addEventListener('keydown', onKeydown, true);
    }

    function closeOverlay() {
      if (!open) return;
      open = false;
      document.removeEventListener('keydown', onKeydown, true);
      if (anim) { anim.cancel(); anim = null; }
      var settle = function () {
        section.removeAttribute('data-mode');
        section.removeAttribute('role');
        section.removeAttribute('aria-modal');
        section.removeAttribute('tabindex');
        if (closeBtn) closeBtn.hidden = true;
        inerted.forEach(function (el) { el.inert = false; });
        inerted = [];
        document.body.style.overflow = prevBodyOverflow;
        if (lastTrigger && lastTrigger.focus) lastTrigger.focus({ preventScroll: true });
        lastTrigger = null;
      };
      if (!reduce() && section.animate) {
        var out = section.animate(
          [{ transform: 'translateY(0)', opacity: 1 },
           { transform: 'translateY(24px)', opacity: 0 }],
          { duration: 320, easing: 'cubic-bezier(.7,.02,.28,1)' });
        out.onfinish = settle;
        out.oncancel = settle;
      } else {
        settle();
      }
    }

    function onKeydown(e) {
      if (e.key === 'Escape' || e.keyCode === 27) {
        e.preventDefault();
        closeOverlay();
        return;
      }
      if (e.key !== 'Tab' && e.keyCode !== 9) return;
      var f = focusablesIn(section);
      if (!f.length) { e.preventDefault(); return; }
      var first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault(); last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault(); first.focus();
      } else if (!section.contains(document.activeElement)) {
        e.preventDefault(); first.focus();
      }
    }

    function onTrigger(e) {
      e.preventDefault();
      openOverlay(e.currentTarget);
    }
    function onClose() { closeOverlay(); }

    triggers.forEach(function (t) { t.addEventListener('click', onTrigger); });
    if (closeBtn) closeBtn.addEventListener('click', onClose);

    var handle = {
      destroy: function () {
        closeOverlay();
        triggers.forEach(function (t) { t.removeEventListener('click', onTrigger); });
        if (closeBtn) closeBtn.removeEventListener('click', onClose);
        delete section.__adAboutOverlayFooter;
      }
    };
    section.__adAboutOverlayFooter = handle;
    return handle;
  }

  global.awardAboutOverlayFooter = { init: init };
})(typeof window !== 'undefined' ? window : this);
