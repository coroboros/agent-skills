/*
 * corner-counter-boot — form enhancer (winner: Aristide Benoist Portfolio
 * 2021; see forms/corner-counter-boot.css for the full ruling — the
 * DIEGETIC in-page boot, never an overlay curtain). Owns the honest roll:
 * the count eases 0→99 over minDuration, holds at 99 until the real window
 * `load`, settles to 100 (data-boot="done" — the accent adopt is the
 * stylesheet's), then the digits exit translate3d(-110%,0,0) (the carried
 * Aristide read) and the corner tag fades — both WAAPI, the settle hide is
 * this enhancer's inline write. onDone fires after the exit lands: the
 * index's own boot choreography starts there. The page is never covered and
 * scroll is never locked — a visitor may already be reading the index while
 * the corner ticks.
 *
 * Skip contract (mirrors the merged loaders): reduced-motion — no roll, no
 * exit; the authored resting text stands, data-boot="done" is set and
 * onDone fires at once. sessionOnce skips the roll after the first
 * completed run this session. A dead script shows the authored settled
 * corner tag (the resting truth is the finished count).
 *
 * Usage:  awardCornerCounterBoot.init(root, { selector, minDuration,
 *                                             sessionOnce, keep, onDone })
 *   root         Element|Document  scope (default document)
 *   selector     string   the form root (default '[data-ad-form="corner-counter-boot"]')
 *   minDuration  ms       floor for the 0→99 roll (default 1800)
 *   sessionOnce  boolean  skip after the first completed run this session
 *   keep         boolean  leave the settled count standing as corner chrome
 *                         instead of playing the exit (default false)
 *   onDone       function fires once after the exit lands — and immediately
 *                         on every skip path, so the index boot never
 *                         depends on the roll having played
 * Returns { destroy() }. Idempotent per root — while rolling it returns the
 * live handle; once done a re-init is a no-op.
 */
(function (global) {
  'use strict';
  var SESSION_KEY = 'ad-corner-counter-boot';

  var reduce = function () {
    return !!(global.matchMedia &&
      global.matchMedia('(prefers-reduced-motion: reduce)').matches);
  };

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-form="corner-counter-boot"]';
    var minDuration = opts.minDuration != null ? +opts.minDuration : 1800;
    var onDone = typeof opts.onDone === 'function' ? opts.onDone : function () {};

    var section = (root.matches && root.matches(selector))
      ? root
      : (root.querySelector ? root.querySelector(selector) : null);
    var count = section ? section.querySelector('[data-slot="count"]') : null;
    if (!section || !count) return { destroy: function () {} };
    if (section.__adCornerCounterBoot) return section.__adCornerCounterBoot;

    var restingText = count.textContent;
    var rafId = 0;
    var exitAnims = [];
    var done = false;

    function finish(played) {
      if (done) return;
      done = true;
      section.setAttribute('data-boot', 'done');
      if (played && opts.sessionOnce) {
        try { global.sessionStorage.setItem(SESSION_KEY, '1'); } catch (e) {}
      }
      onDone();
    }

    // skip paths — the authored resting text IS the finished state
    var skipped = reduce() ||
      (opts.sessionOnce && (function () {
        try { return global.sessionStorage.getItem(SESSION_KEY) === '1'; }
        catch (e) { return false; }
      })());
    if (skipped) {
      finish(false);
      var noop = { destroy: function () {} };
      section.__adCornerCounterBoot = noop;
      return noop;
    }

    function exit() {
      count.textContent = '100';
      section.setAttribute('data-boot', 'done');
      if (opts.keep) { finish(true); return; }
      var targets = [count];
      var label = section.querySelector('[data-slot="label"]');
      if (label) targets.push(label);
      var pending = targets.length;
      targets.forEach(function (el, i) {
        var a = el.animate
          ? el.animate(
              i === 0
                ? [{ transform: 'translate3d(0,0,0)' },
                   { transform: 'translate3d(-110%,0,0)' }]
                : [{ opacity: 1 }, { opacity: 0 }],
              { duration: 420, delay: i * 60,
                easing: 'cubic-bezier(.7,.02,.28,1)', fill: 'forwards' })
          : null;
        var land = function () {
          el.style.visibility = 'hidden';   // the settle hide — an inline write
          if (--pending === 0) finish(true);
        };
        if (a) { a.onfinish = land; a.oncancel = land; exitAnims.push(a); }
        else land();
      });
    }

    // the honest roll: ease to 99 over the floor, hold for the real load
    var start = 0;
    var loaded = document.readyState === 'complete';
    var onLoad = function () { loaded = true; };
    if (!loaded) global.addEventListener('load', onLoad, { once: true });

    function frame(now) {
      if (!start) start = now;
      var t = Math.min(1, (now - start) / minDuration);
      var eased = 1 - Math.pow(1 - t, 3);
      var v = Math.min(99, Math.round(eased * 99));
      count.textContent = String(v);
      if (t >= 1 && loaded) { rafId = 0; exit(); return; }
      rafId = global.requestAnimationFrame(frame);
    }
    count.textContent = '0';
    rafId = global.requestAnimationFrame(frame);

    var handle = {
      destroy: function () {
        if (rafId) { global.cancelAnimationFrame(rafId); rafId = 0; }
        global.removeEventListener('load', onLoad);
        exitAnims.forEach(function (a) { a.cancel(); });
        exitAnims = [];
        count.textContent = restingText;
        count.style.visibility = '';
        var label = section.querySelector('[data-slot="label"]');
        if (label) label.style.visibility = '';
        section.removeAttribute('data-boot');
        delete section.__adCornerCounterBoot;
      }
    };
    section.__adCornerCounterBoot = handle;
    return handle;
  }

  global.awardCornerCounterBoot = { init: init };
})(typeof window !== 'undefined' ? window : this);
