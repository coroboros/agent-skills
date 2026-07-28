/*
 * stacked-card-scroll — the pinned deck that peels (winner: Bloom). Layered
 * cards overlap as the track scrolls: each card pins at the viewport top,
 * the next rises over it under native scroll, and the covered card peels —
 * it scales down a touch, lifts, and dims in proportion to how far its
 * successor has risen. A mid-page mechanic that re-spends hero momentum in
 * the proof/services band; distinct from card-list (a static grid). The
 * peel is a pure function of scroll position — compositor-only transform +
 * filter — so every pass re-fires and scroll-back reverses by construction.
 * The pin is native position:sticky: the component never hijacks the
 * scroll, it only reads it.
 * Mobile (the documented answer): a simple stack — under 768px the cards
 * stay in normal flow, full coverage, no pin. Reduced motion: a flat
 * stacked list (the same resting flow), nothing pins, nothing peels. A dead
 * script leaves that legible flow too — the live class is JS-applied.
 *
 * Expected markup — one card per offer/proof, content authored inside:
 *   <section data-ad-stack>
 *     <article data-ad-stack-card> … </article>
 *   </section>
 *
 * Usage:  awardStackedCardScroll.init(root, opts)
 *   root      Element|Document  scope (default document)
 *   selector  string  decks (default '[data-ad-stack]')
 *   scale     number  peel scale floor for a fully covered card (default 0.94)
 *   dim       number  peel brightness floor (default 0.6)
 * Returns { destroy() }. Idempotent per deck. destroy() restores the flat
 * flow, clears transforms, and removes observers, listeners, stylesheet.
 *
 * Perf: reads are batched before writes each frame; the rAF loop is welded
 * to scroll/resize events, gated off-screen (IO) and on hidden tabs, and
 * stops when the deck leaves the viewport. Cards clip their own content
 * (overflow:hidden) so the peel never bleeds across a section boundary.
 *
 * Tokens: none — the deck owns placement only; card grounds, type, and
 * radius are the build's.
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-stacked-card-scroll-css';
  var LIVE_MQ = '(min-width: 768px)';

  var reduce = function () {
    return !!(global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches);
  };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      // rest state: a flat stacked list — mobile, reduce, and no-JS all read this
      '[data-ad-stack-card]{position:relative;overflow:hidden;}' +
      // live state: each card pins at the top while the next rises over it
      '.ad-stack--live [data-ad-stack-card]{position:sticky;top:0;min-height:100svh;' +
      'will-change:transform,filter;}';
    document.head.appendChild(s);
  }

  function mqOn(mq, fn) {
    if (mq.addEventListener) mq.addEventListener('change', fn);
    else if (mq.addListener) mq.addListener(fn);
  }
  function mqOff(mq, fn) {
    if (mq.removeEventListener) mq.removeEventListener('change', fn);
    else if (mq.removeListener) mq.removeListener(fn);
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-stack]';
    var scaleFloor = opts.scale != null ? opts.scale : 0.94;
    var dimFloor = opts.dim != null ? opts.dim : 0.6;
    injectCss();

    var decks = [];

    // Reduced motion: the flat stacked list — never pin, never peel.
    if (reduce()) return { destroy: function () {} };

    var wide = global.matchMedia ? global.matchMedia(LIVE_MQ) : null;

    Array.prototype.forEach.call(root.querySelectorAll(selector), function (deck) {
      if (deck.__adStack) return; // idempotent
      var cards = Array.prototype.slice.call(deck.querySelectorAll('[data-ad-stack-card]'));
      if (cards.length < 2) return; // one card has nothing to peel under

      var raf = 0, running = false, inView = false, live = false;

      function clearPeel() {
        cards.forEach(function (c) { c.style.transform = ''; c.style.filter = ''; });
      }

      function frame() {
        raf = 0;
        if (!live || !inView) { running = false; return; }
        var vh = global.innerHeight || document.documentElement.clientHeight;
        // batch the reads, then the writes — no interleaved layout thrash
        var tops = cards.map(function (c) { return c.getBoundingClientRect().top; });
        for (var i = 0; i < cards.length - 1; i++) {
          // how far card i+1 has risen over pinned card i: 0 (below) → 1 (covering)
          var p = 1 - tops[i + 1] / Math.max(1, vh);
          p = p < 0 ? 0 : p > 1 ? 1 : p;
          if (p > 0) {
            var s = 1 - (1 - scaleFloor) * p;
            var b = 1 - (1 - dimFloor) * p;
            cards[i].style.transform = 'translate3d(0,' + (-4 * p).toFixed(2) + 'vh,0) ' +
              'scale(' + s.toFixed(4) + ')';
            cards[i].style.filter = 'brightness(' + b.toFixed(3) + ')';
          } else {
            cards[i].style.transform = '';
            cards[i].style.filter = '';
          }
        }
        running = false; // welded to scroll — each event schedules one frame
      }
      function kick() {
        if (document.hidden || !live || !inView) return;
        running = true;
        if (!raf) raf = global.requestAnimationFrame(frame);
      }

      function setLive(on) {
        if (on === live) return;
        live = on;
        deck.classList.toggle('ad-stack--live', on);
        if (!on) clearPeel();
        else kick();
      }
      function evaluate() { setLive(!wide || wide.matches); }

      var onScroll = function () { kick(); };
      var onVis = function () { if (!document.hidden) kick(); };

      var io = null;
      if ('IntersectionObserver' in global) {
        io = new IntersectionObserver(function (entries) {
          entries.forEach(function (e) {
            inView = e.isIntersecting;
            if (inView) kick();
          });
        }, { threshold: 0 });
        io.observe(deck);
      } else {
        inView = true;
      }

      global.addEventListener('scroll', onScroll, { passive: true });
      global.addEventListener('resize', onScroll, { passive: true });
      document.addEventListener('visibilitychange', onVis);
      if (wide) mqOn(wide, evaluate);
      evaluate();

      deck.__adStack = true;
      decks.push({
        destroy: function () {
          if (raf) global.cancelAnimationFrame(raf);
          if (io) io.disconnect();
          global.removeEventListener('scroll', onScroll);
          global.removeEventListener('resize', onScroll);
          document.removeEventListener('visibilitychange', onVis);
          if (wide) mqOff(wide, evaluate);
          deck.classList.remove('ad-stack--live');
          clearPeel();
          delete deck.__adStack;
        }
      });
    });

    return {
      destroy: function () {
        decks.forEach(function (d) { d.destroy(); });
        decks = [];
        var s = document.getElementById(CSS_ID);
        if (s && s.parentNode) s.parentNode.removeChild(s);
      }
    };
  }

  global.awardStackedCardScroll = { init: init };
})(typeof window !== 'undefined' ? window : this);
