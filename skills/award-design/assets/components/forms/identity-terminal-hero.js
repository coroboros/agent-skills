/*
 * identity-terminal-hero enhancer — the char-DIFF tag swap for the
 * identity-terminal-hero section form (winner: Eloy Benoffi, Codrops-verified:
 * TextPlugin type:'diff', 0.3s, preserveSpaces). Each corner tag that declares
 * a second string cycles between the authored line and the swap line
 * ('>>>based in madrid, spain' ⇄ '>>>born in mar del plata, arg') by typing
 * over ONLY the differing span — the common prefix and suffix never move,
 * which is what makes the swap read as a terminal correcting itself rather
 * than a re-type. Chars land on a flat clock (ease:none — the brutalist
 * tell); spaces survive because the form's CSS sets white-space:pre on tags
 * (the preserveSpaces analog). The swap runs only while the hero is on
 * screen and the tab visible. Layering law: the enhancer mutates the tag's
 * TEXT only (documented enhancer-owned, like the swipe-snap dots) — it
 * creates no nodes and never restructures a slot's inner DOM. No stylesheet
 * is injected: the form's CSS is linked, and a dead script leaves the
 * authored line standing.
 *
 * Usage:  awardIdentityTerminalHero.init(root, opts)
 *   root      Element|Document  scope (default document)
 *   selector  string  form roots (default '[data-ad-form="identity-terminal-hero"]')
 *   swapMs    ms      one diff pass (default 300 — the winner's 0.3s)
 *   holdMs    ms      rest on each completed line (default 4000)
 * Returns { destroy() } — cancels the clock and restores the authored text.
 * Idempotent per form root. Reduced motion → no-op: the authored line IS the
 * finished state.
 */
(function (global) {
  'use strict';

  var reduce = function () {
    return global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches;
  };

  // The diff: common prefix + suffix stand still; the middle is typed over.
  function diff(from, to) {
    var p = 0;
    var maxP = Math.min(from.length, to.length);
    while (p < maxP && from.charAt(p) === to.charAt(p)) p++;
    var s = 0;
    while (
      s < maxP - p &&
      from.charAt(from.length - 1 - s) === to.charAt(to.length - 1 - s)
    ) s++;
    return {
      prefix: from.slice(0, p),
      suffix: s ? from.slice(from.length - s) : '',
      outgoing: from.slice(p, from.length - s),
      incoming: to.slice(p, to.length - s)
    };
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    // Reduced motion → the authored line is the finished state; nothing types.
    if (reduce()) return { destroy: function () {} };

    var selector = opts.selector || '[data-ad-form="identity-terminal-hero"]';
    var swapMs = opts.swapMs != null ? opts.swapMs : 300;
    var holdMs = opts.holdMs != null ? opts.holdMs : 4000;

    var units = [];
    Array.prototype.forEach.call(root.querySelectorAll(selector), function (form) {
      if (form.__adTerminalHero) return; // idempotent
      var tags = Array.prototype.slice.call(
        form.querySelectorAll('[data-slot="tag"][data-tag-swap]')
      );
      if (!tags.length) return;

      var unit = {
        form: form, visible: true, raf: 0,
        tags: tags.map(function (tag) {
          return {
            el: tag,
            authored: tag.textContent,
            swap: tag.getAttribute('data-tag-swap'),
            onSwap: false,     // which line currently rests
            typingT0: 0,       // 0 → resting; else the swap's start time
            restT0: 0
          };
        })
      };

      function frame(now) {
        unit.raf = 0;
        var busy = false;
        unit.tags.forEach(function (t) {
          if (!t.restT0 && !t.typingT0) t.restT0 = now;
          if (t.typingT0) {
            var from = t.onSwap ? t.swap : t.authored;
            var to = t.onSwap ? t.authored : t.swap;
            var d = diff(from, to);
            var steps = d.outgoing.length + d.incoming.length;
            // flat cadence: elapsed maps linearly onto delete-then-type steps
            var k = Math.min(steps, Math.floor(((now - t.typingT0) / swapMs) * steps));
            var text;
            if (k <= d.outgoing.length) {
              text = d.prefix + d.outgoing.slice(0, d.outgoing.length - k) + d.suffix;
            } else {
              text = d.prefix + d.incoming.slice(0, k - d.outgoing.length) + d.suffix;
            }
            if (t.el.textContent !== text) t.el.textContent = text;
            if (k >= steps) {
              t.typingT0 = 0;
              t.onSwap = !t.onSwap;
              t.restT0 = now;
            }
            busy = true;
          } else if (now - t.restT0 >= holdMs) {
            t.typingT0 = now;
            busy = true;
          }
        });
        if (busy || unit.visible) schedule();
      }
      function schedule() {
        if (!unit.raf && unit.visible && !document.hidden) {
          unit.raf = global.requestAnimationFrame(frame);
        }
      }
      unit.schedule = schedule;
      unit.stop = function () {
        if (unit.raf) { global.cancelAnimationFrame(unit.raf); unit.raf = 0; }
      };

      if ('IntersectionObserver' in global) {
        unit.io = new IntersectionObserver(function (entries) {
          entries.forEach(function (e) {
            unit.visible = e.isIntersecting;
            if (unit.visible) schedule(); else unit.stop();
          });
        });
        unit.io.observe(form);
      }
      schedule();

      form.__adTerminalHero = unit;
      units.push(unit);
    });

    var onVisibility = null;
    if (units.length) {
      onVisibility = function () {
        units.forEach(function (u) {
          if (document.hidden) u.stop(); else u.schedule();
        });
      };
      document.addEventListener('visibilitychange', onVisibility);
    }

    return {
      destroy: function () {
        if (onVisibility) document.removeEventListener('visibilitychange', onVisibility);
        units.forEach(function (u) {
          u.stop();
          if (u.io) u.io.disconnect();
          u.tags.forEach(function (t) { t.el.textContent = t.authored; });
          delete u.form.__adTerminalHero;
        });
      }
    };
  }

  global.awardIdentityTerminalHero = { init: init };
})(typeof window !== 'undefined' ? window : this);
