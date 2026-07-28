/*
 * perpetual-tile-machines — the five structured tile idle-loops that make a
 * bento grid ALIVE at rest (winner: Anime.js v4 — red-dot period loop,
 * clockwork counter; Vercel/Supabase/Linear five tile-types,
 * design-canonical). ambient-idle covers unstructured glow/float/shimmer/
 * pulse; these are the CONTENT machines — each tile performs its own claim
 * on a period clock, no pointer required (the archetype's touch advantage).
 * Corpus note: the five-machine set is corpus-generalized (mainly Anime.js)
 * plus internal reference — a strong default, not award law. One
 * parameterized component, mode enum via data-ad-machine:
 *   list     Intelligent-List — the last item promotes to the top on each
 *            period, FLIP-animated (transform-only), the auto-sort loop.
 *            Needs [data-machine-list] with >= 3 children.
 *   command  Command-Input — a typewriter cycles prompts on [data-machine-text]
 *            (data-machine-prompts="a|b|c"), blinking block caret, a
 *            processing shimmer sweeps after each prompt lands.
 *   status   Live-Status — [data-machine-badge] breathes; each period a
 *            [data-machine-pop] chip pops in on an overshoot spring, holds
 *            3s (the verified hold), vanishes.
 *   stream   Wide-Data-Stream — [data-machine-stream] children are cloned
 *            once (aria-hidden) and the row glides x:0%→−50% gapless,
 *            linear infinite (linear stays legal on continuous loops).
 *   focus    Focus-Mode — [data-machine-focus-item] rows highlight in a
 *            stagger, then [data-machine-toolbar] floats in, holds, resets.
 *
 * Every loop is gated the ambient-idle way: CSS animations authored PAUSED,
 * one IntersectionObserver runs `is-running` per tile so off-screen tiles
 * cost zero, JS clocks sleep with the observer, and a visibilitychange root
 * class re-pauses a hidden tab. Rest DOM is the authored, legible content —
 * machines only ever animate what the author wrote (plus the one documented
 * stream clone). Reduced motion / no JS: nothing starts, the authored tile
 * stands. The command machine pins the accessible name (aria-label = the
 * authored line) before it starts typing.
 *
 * Usage:  awardPerpetualTileMachines.init(root, { selector })
 *   root      Element|Document  scope (default document)
 *   selector  string            tiles (default '[data-ad-machine]')
 * Attributes: data-machine-period (ms, per-mode default),
 *   data-machine-prompts ('a|b|c'), data-machine-speed (stream px/s, 40).
 * Returns { destroy() }. Idempotent per root.
 *
 * Tokens: --ad-accent (caret, highlight, badge), --ad-ink (shimmer).
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-perpetual-tile-machines-css';
  var HIDDEN_CLASS = 'ad-ptm-page-hidden';
  var ACCENT = 'var(--ad-accent,oklch(62% 0.2 25))';
  var INK = 'var(--ad-ink,oklch(96% 0 0))';
  var HOLD_MS = 3000; // the verified status hold
  var PERIODS = { list: 2600, command: 0, status: 5200, stream: 0, focus: 0 };

  var reduce = function () {
    return global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches;
  };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      // command: block caret + processing shimmer, both paused until running
      '.ad-ptm [data-machine-text]{position:relative;white-space:pre-wrap;}' +
      '.ad-ptm [data-machine-text]::after{content:"";display:inline-block;' +
      'width:.55em;height:1em;vertical-align:text-bottom;margin-left:.08em;' +
      'background:' + ACCENT + ';' +
      'animation:ad-ptm-caret 1.1s steps(1) infinite paused;}' +
      '.ad-ptm.is-running [data-machine-text]::after{animation-play-state:running;}' +
      '.ad-ptm [data-machine-text].is-processing::before{content:"";position:absolute;' +
      'inset:0;pointer-events:none;transform:translateX(-120%);' +
      'background:linear-gradient(105deg,transparent 40%,' +
      'color-mix(in oklch,' + INK + ' 16%,transparent) 50%,transparent 60%);' +
      'animation:ad-ptm-shimmer .9s ease-in-out forwards;}' +
      // status: the breathing badge
      '.ad-ptm [data-machine-badge]{' +
      'animation:ad-ptm-breathe 3.2s ease-in-out infinite alternate paused;}' +
      '.ad-ptm.is-running [data-machine-badge]{animation-play-state:running;will-change:transform,opacity;}' +
      // stream: gapless glide — duration set inline from measured width
      '.ad-ptm [data-machine-stream]{display:flex;width:max-content;' +
      'animation:ad-ptm-stream 20s linear infinite paused;}' +
      '.ad-ptm.is-running [data-machine-stream]{animation-play-state:running;will-change:transform;}' +
      '.ad-ptm--stream{overflow:hidden;}' +
      // focus: the staggered highlight + the floating toolbar
      '.ad-ptm [data-machine-focus-item]{' +
      'transition:background-color .3s ease-out,color .3s ease-out;}' +
      '.ad-ptm [data-machine-focus-item].is-hit{' +
      'background:color-mix(in oklch,' + ACCENT + ' 14%,transparent);}' +
      '.ad-ptm [data-machine-toolbar]{' +
      'transition:opacity .3s ease-out,transform .3s ease-out;}' +
      '.ad-ptm.is-machine-on [data-machine-toolbar]{opacity:0;transform:translate3d(0,8px,0);}' +
      '.ad-ptm.is-machine-on [data-machine-toolbar].is-in{opacity:1;transform:translate3d(0,0,0);}' +
      // list: the mover eases home after the FLIP invert
      '.ad-ptm [data-machine-list] > .is-flipping{' +
      'transition:transform .5s cubic-bezier(.16,1,.3,1);will-change:transform;}' +
      // a hidden tab outranks is-running (0,2,1 vs 0,2,0) — no !important needed
      'html.' + HIDDEN_CLASS + ' .ad-ptm [data-machine-text]::after,' +
      'html.' + HIDDEN_CLASS + ' .ad-ptm [data-machine-badge],' +
      'html.' + HIDDEN_CLASS + ' .ad-ptm [data-machine-stream]{animation-play-state:paused;}' +
      '@keyframes ad-ptm-caret{0%{opacity:1;}50%{opacity:0;}}' +
      '@keyframes ad-ptm-shimmer{to{transform:translateX(120%);}}' +
      '@keyframes ad-ptm-breathe{from{transform:scale(1);opacity:.75;}' +
      'to{transform:scale(1.05);opacity:1;}}' +
      '@keyframes ad-ptm-stream{to{transform:translate3d(-50%,0,0);}}' +
      '@media (prefers-reduced-motion:reduce){' +
      '.ad-ptm [data-machine-text]::after,.ad-ptm [data-machine-badge],' +
      '.ad-ptm [data-machine-stream]{animation:none;will-change:auto;}' +
      '.ad-ptm [data-machine-focus-item],.ad-ptm [data-machine-toolbar]{transition:none;}}';
    document.head.appendChild(s);
  }

  function periodOf(tile, mode) {
    var v = parseFloat(tile.getAttribute('data-machine-period'));
    return v > 0 ? v : PERIODS[mode];
  }

  // ---- the five machines — each returns { start, stop, teardown } ---------

  function listMachine(tile) {
    var list = tile.querySelector('[data-machine-list]');
    if (!list || list.children.length < 3) return null;
    var timer = 0;
    var period = periodOf(tile, 'list');
    function step() {
      var items = Array.prototype.slice.call(list.children);
      var mover = items[items.length - 1];
      var before = items.map(function (el) { return el.getBoundingClientRect().top; });
      list.insertBefore(mover, items[0]); // the new entry arrives at the top
      items.forEach(function (el, i) {
        var d = before[i] - el.getBoundingClientRect().top;
        if (!d) return;
        el.style.transform = 'translate3d(0,' + d.toFixed(1) + 'px,0)';
        el.getBoundingClientRect(); // commit the inverted pose
        el.classList.add('is-flipping');
        el.style.transform = '';
        el.addEventListener('transitionend', function done() {
          el.classList.remove('is-flipping');
          el.removeEventListener('transitionend', done);
        });
      });
      timer = global.setTimeout(step, period);
    }
    return {
      start: function () { if (!timer) timer = global.setTimeout(step, period); },
      stop: function () { global.clearTimeout(timer); timer = 0; },
      teardown: function () {
        Array.prototype.forEach.call(list.children, function (el) {
          el.classList.remove('is-flipping');
          el.style.transform = '';
        });
      }
    };
  }

  function commandMachine(tile) {
    var text = tile.querySelector('[data-machine-text]');
    if (!text) return null;
    var authored = text.textContent;
    var prompts = (tile.getAttribute('data-machine-prompts') || authored)
      .split('|').map(function (p) { return p.trim(); }).filter(Boolean);
    if (!prompts.length) return null;
    // pin the accessible name before the typing mutates the text nodes
    if (!text.hasAttribute('aria-label')) text.setAttribute('aria-label', authored);
    var timer = 0;
    var pi = 0;
    var ci = 0;
    var phase = 'type';
    function tick() {
      var prompt = prompts[pi % prompts.length];
      if (phase === 'type') {
        ci++;
        text.textContent = prompt.slice(0, ci);
        if (ci >= prompt.length) {
          phase = 'process';
          text.classList.add('is-processing');
          timer = global.setTimeout(tick, 950);
        } else {
          timer = global.setTimeout(tick, 34 + Math.random() * 46);
        }
      } else if (phase === 'process') {
        text.classList.remove('is-processing');
        phase = 'hold';
        timer = global.setTimeout(tick, 1400);
      } else if (phase === 'hold') {
        phase = 'erase';
        timer = global.setTimeout(tick, 16);
      } else {
        ci = Math.max(0, ci - 2);
        text.textContent = prompt.slice(0, ci);
        if (ci === 0) {
          pi++;
          phase = 'type';
          timer = global.setTimeout(tick, 420);
        } else {
          timer = global.setTimeout(tick, 16);
        }
      }
    }
    return {
      start: function () { if (!timer) timer = global.setTimeout(tick, 300); },
      stop: function () { global.clearTimeout(timer); timer = 0; },
      teardown: function () {
        text.textContent = authored;
        text.classList.remove('is-processing');
      }
    };
  }

  function statusMachine(tile) {
    var pop = tile.querySelector('[data-machine-pop]');
    if (!pop) return null;
    var timer = 0;
    var anim = null;
    var period = periodOf(tile, 'status');
    function cycle() {
      pop.style.opacity = '1';
      anim = pop.animate && pop.animate([
        { opacity: 0, transform: 'scale(.6)' },
        { opacity: 1, transform: 'scale(1.06)', offset: 0.7 },
        { opacity: 1, transform: 'scale(1)' }
      ], { duration: 420, easing: 'cubic-bezier(.34,1.56,.64,1)' }); // the overshoot spring
      timer = global.setTimeout(function () {
        anim = pop.animate && pop.animate(
          [{ opacity: 1 }, { opacity: 0 }], { duration: 300, fill: 'forwards' });
        timer = global.setTimeout(cycle, Math.max(600, period - HOLD_MS - 720));
      }, HOLD_MS); // pop, hold 3s, vanish
    }
    return {
      start: function () {
        if (timer) return;
        pop.style.opacity = '0'; // JS-applied — the rest DOM keeps the chip visible
        timer = global.setTimeout(cycle, 500);
      },
      stop: function () {
        global.clearTimeout(timer); timer = 0;
        if (anim && anim.cancel) anim.cancel();
      },
      teardown: function () { pop.style.opacity = ''; }
    };
  }

  function streamMachine(tile) {
    var row = tile.querySelector('[data-machine-stream]');
    if (!row || !row.children.length) return null;
    tile.classList.add('ad-ptm--stream');
    if (!row.__adPtmCloned) {
      // the one documented clone: duplicate the authored set once so −50% wraps gapless
      Array.prototype.slice.call(row.children).forEach(function (child) {
        var c = child.cloneNode(true);
        c.setAttribute('aria-hidden', 'true');
        c.setAttribute('data-ad-ptm-clone', '');
        row.appendChild(c);
      });
      row.__adPtmCloned = true;
    }
    var speed = parseFloat(tile.getAttribute('data-machine-speed')) || 40; // px/s
    var half = row.scrollWidth / 2;
    if (half > 0) row.style.animationDuration = (half / speed).toFixed(2) + 's';
    return { start: function () {}, stop: function () {}, teardown: function () {
      Array.prototype.slice.call(row.querySelectorAll('[data-ad-ptm-clone]')).forEach(function (c) {
        c.parentNode.removeChild(c);
      });
      delete row.__adPtmCloned;
      row.style.animationDuration = '';
      tile.classList.remove('ad-ptm--stream');
    } };
  }

  function focusMachine(tile) {
    var items = Array.prototype.slice.call(tile.querySelectorAll('[data-machine-focus-item]'));
    var toolbar = tile.querySelector('[data-machine-toolbar]');
    if (!items.length) return null;
    var timers = [];
    function later(fn, ms) { timers.push(global.setTimeout(fn, ms)); }
    function clear() {
      timers.forEach(function (t) { global.clearTimeout(t); });
      timers.length = 0;
    }
    function cycle() {
      items.forEach(function (item, i) {
        later(function () { item.classList.add('is-hit'); }, 400 + i * 140);
      });
      var staged = 400 + items.length * 140;
      if (toolbar) later(function () { toolbar.classList.add('is-in'); }, staged + 160);
      later(function () {
        items.forEach(function (item) { item.classList.remove('is-hit'); });
        if (toolbar) toolbar.classList.remove('is-in');
      }, staged + 160 + 2400); // the hold
      later(cycle, staged + 160 + 2400 + 1200);
    }
    return {
      start: function () {
        if (timers.length) return;
        tile.classList.add('is-machine-on'); // JS-applied — rest keeps the toolbar visible
        cycle();
      },
      stop: function () {
        clear();
        items.forEach(function (item) { item.classList.remove('is-hit'); });
        if (toolbar) toolbar.classList.remove('is-in');
      },
      teardown: function () { tile.classList.remove('is-machine-on'); }
    };
  }

  var FACTORIES = {
    list: listMachine, command: commandMachine, status: statusMachine,
    stream: streamMachine, focus: focusMachine
  };

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    var selector = opts.selector || '[data-ad-machine]';

    // Reduced motion: no machine ever starts — the authored tile stands.
    if (reduce()) return { destroy: function () {} };

    injectCss();
    if (root.__adPerpetualTileMachines) root.__adPerpetualTileMachines.destroy();

    var units = [];
    Array.prototype.forEach.call(root.querySelectorAll(selector), function (tile) {
      var mode = tile.getAttribute('data-ad-machine');
      var factory = FACTORIES[mode];
      if (!factory) return;
      var machine = factory(tile);
      if (!machine) return; // contract markup missing → the authored tile stands
      tile.classList.add('ad-ptm');
      units.push({ tile: tile, machine: machine, on: false });
    });

    function wake(unit) {
      if (unit.on) return;
      unit.on = true;
      unit.tile.classList.add('is-running');
      unit.machine.start();
    }
    function sleep(unit) {
      if (!unit.on) return;
      unit.on = false;
      unit.tile.classList.remove('is-running');
      unit.machine.stop();
    }

    var io = null;
    if ('IntersectionObserver' in global) {
      io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          units.forEach(function (u) {
            if (u.tile !== e.target) return;
            if (e.isIntersecting && !document.hidden) wake(u); else sleep(u);
          });
        });
      });
      units.forEach(function (u) { io.observe(u.tile); });
    } else {
      units.forEach(wake);
    }

    function onVisibility() {
      document.documentElement.classList.toggle(HIDDEN_CLASS, document.hidden);
      if (document.hidden) {
        units.forEach(sleep);
      } else if (io) {
        units.forEach(function (u) { io.unobserve(u.tile); io.observe(u.tile); });
      } else {
        units.forEach(wake);
      }
    }
    document.addEventListener('visibilitychange', onVisibility);
    onVisibility();

    var handle = {
      destroy: function () {
        document.removeEventListener('visibilitychange', onVisibility);
        if (io) io.disconnect();
        units.forEach(function (u) {
          sleep(u);
          u.machine.teardown();
          u.tile.classList.remove('ad-ptm');
        });
        document.documentElement.classList.remove(HIDDEN_CLASS);
        var s = document.getElementById(CSS_ID);
        if (s && s.parentNode) s.parentNode.removeChild(s);
        if (root.__adPerpetualTileMachines === handle) delete root.__adPerpetualTileMachines;
      }
    };
    root.__adPerpetualTileMachines = handle;
    return handle;
  }

  global.awardPerpetualTileMachines = { init: init };
})(typeof window !== 'undefined' ? window : this);
