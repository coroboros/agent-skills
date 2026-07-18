/*
 * contextual-cursor-label — the gesture-discovery cursor for luxury's hidden
 * gestures (winners: Louis Vuitton Collectibles — SOTD Feb 2024, the
 * click-and-hold gesture, Animations 9.4; Cartier WAW 2025 — SOTD Aug 2025,
 * hidden gestures in every alcove scene). Over a declared gesture object the
 * chrome arrives: an outline ring grows from nothing and a contextual verb
 * label (HOLD / DRAG / VIEW / EXPLORE) surfaces inside it — the affordance
 * that makes 'hidden gestures that reward curiosity' discoverable. On a HOLD
 * object, pressing charges the ring: an arc fills over the object's declared
 * hold duration (the LV click-and-hold instrument), retracting on release —
 * the cursor is the gesture's own progress dial. SURFACE-SCOPED, the ruled
 * distinction: the NATIVE cursor stands everywhere off-surface. NOT an alias
 * of cursor-verb-label (editorial-dark's field-scoped verb teacher — a label
 * chip only, no ring chrome, no hold instrument) nor of
 * custom-contextual-cursor (bold-maximal's page-level dot+ring costume that
 * replaces the pointer everywhere); one cursor component per page, ever.
 * The cursor is the AFFORDANCE only — the object's own gesture logic (a
 * press-hold-reveal, a drag surface, a WebGL raycast) owns completion; this
 * component drives no reveal.
 * Touch: dormant — native pointer; the gesture is surfaced instead by an
 * on-object hint chip carrying the same verb (the playbook's tap answer), so
 * the gesture is never undiscoverable. Keyboard: the chip also surfaces on
 * the object's :focus-visible; the object itself stays operable with its own
 * accessible name — nothing is gated behind the chrome. Reduced motion: no
 * cursor chrome; the static hint chips stand on every pointer type.
 *
 * Expected markup — gesture objects declare their verb (and a hold time):
 *   <figure data-ad-gesture="VIEW">…</figure>
 *   <button data-ad-gesture="HOLD" data-ad-gesture-hold="700">…</button>
 *
 * Usage:  awardContextualCursorLabel.init(root, opts)
 *   root      Element|Document  scope (default document)
 *   selector  string  gesture objects (default '[data-ad-gesture]')
 *   lerp      number  ring follow smoothing (default 0.18 — unhurried)
 * Returns { destroy() }. Idempotent — one chrome layer per page; a second
 * init returns the live handle. Re-evaluates its gate on pointer/reduce
 * media-query changes (a convertible flipping to touch tears the chrome
 * down and raises the chips). destroy() restores the native cursor and
 * removes the layer, chips, listeners, and the stylesheet.
 *
 * A11y + perf: ring and label are aria-hidden and pointer-events:none —
 * the chrome never intercepts a click or takes focus; cursor:none applies
 * only over a gesture object via a JS-applied class (a dead script never
 * strands a cursorless surface). Compositor-only: one promoted fixed node,
 * transform/opacity plus the arc's stroke-dashoffset, one rAF that runs
 * only while the chrome shows or is still traveling.
 *
 * Tokens: --ad-ink (ring + chip ink), --ad-ground-2 (chip ground),
 * --ad-font-mono (label face), --ad-dur-base + --ad-ease-signature (the
 * morph register).
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-contextual-cursor-label-css';
  var SVG_NS = 'http://www.w3.org/2000/svg';
  var RING_R = 26;          // ring radius (px)
  var HOLD_DEFAULT = 700;   // the LV-band hold (~600-900ms) when undeclared
  var RETRACT_RATE = 3;     // released charge retracts 3x faster than it filled

  var reduce = function () {
    return !!(global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches);
  };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var ink = 'var(--ad-ink,oklch(96% 0 0))';
    var morph = 'var(--ad-dur-base,420ms) var(--ad-ease-signature,cubic-bezier(.16,1,.3,1))';
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      // the outer node is a pure tracker (rAF writes its transform); the
      // morphs ride inner elements so a transition never fights the tracker
      '.ad-ccl{position:fixed;left:0;top:0;z-index:2147483646;pointer-events:none;' +
      'opacity:0;will-change:transform;transition:opacity 200ms ease;}' +
      '.ad-ccl.is-on{opacity:1;}' +
      '.ad-ccl svg{position:absolute;left:' + -RING_R + 'px;top:' + -RING_R + 'px;' +
      'overflow:visible;}' +
      // the outline ring grows from nothing — the shape shift of the gap
      '.ad-ccl__ring{fill:none;stroke:' + ink + ';stroke-width:1.25;opacity:.65;' +
      'transform:scale(.4);transform-origin:center;' +
      'transition:transform ' + morph + ',opacity ' + morph + ';}' +
      '.ad-ccl.is-on .ad-ccl__ring{transform:scale(1);}' +
      // the charge arc — JS writes stroke-dashoffset while a hold charges
      '.ad-ccl__arc{fill:none;stroke:' + ink + ';stroke-width:1.25;' +
      'stroke-linecap:round;stroke-dasharray:1;stroke-dashoffset:1;' +
      'transform:rotate(-90deg);transform-origin:center;}' +
      '.ad-ccl span{position:absolute;left:' + -RING_R + 'px;top:' + -RING_R + 'px;' +
      'width:' + RING_R * 2 + 'px;height:' + RING_R * 2 + 'px;' +
      'display:grid;place-items:center;color:' + ink + ';' +
      'font-family:var(--ad-font-mono,ui-monospace,monospace);font-size:.58rem;' +
      'letter-spacing:.14em;text-transform:uppercase;white-space:nowrap;' +
      'opacity:0;transform:scale(.6);' +
      'transition:opacity ' + morph + ',transform ' + morph + ';}' +
      '.ad-ccl.is-on span{opacity:1;transform:scale(1);}' +
      // a completed charge settles — the dial reads full until release
      '.ad-ccl[data-charged] .ad-ccl__ring{opacity:1;}' +
      // native cursor hides only over a gesture object, via JS-applied class
      '.ad-ccl-hide,.ad-ccl-hide *{cursor:none!important;}' +
      // ---- the on-object hint chip: touch + reduced-motion + keyboard -----
      '.ad-ccl-host{position:relative;}' +
      '.ad-ccl__hint{position:absolute;left:50%;bottom:1rem;transform:translateX(-50%);' +
      'z-index:5;pointer-events:none;padding:.45em .8em;border-radius:999px;' +
      'border:1px solid color-mix(in oklch,' + ink + ' 35%,transparent);' +
      'background:var(--ad-ground-2,oklch(18% 0.01 260));color:' + ink + ';' +
      'font-family:var(--ad-font-mono,ui-monospace,monospace);font-size:.62rem;' +
      'letter-spacing:.14em;text-transform:uppercase;white-space:nowrap;}' +
      // fine pointer + motion: the chip stands down at rest and surfaces on
      // the object's own keyboard focus — the gesture is never focus-blind
      '.ad-ccl-fine .ad-ccl__hint{visibility:hidden;}' +
      '.ad-ccl-fine [data-ad-gesture]:focus-visible .ad-ccl__hint{visibility:visible;}';
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

  var current = null; // page-level singleton — one chrome keeps init idempotent

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    if (current) return current;
    if (!global.matchMedia) return { destroy: function () {} }; // no gate → native cursor

    var selector = opts.selector || '[data-ad-gesture]';
    var lerpK = opts.lerp != null ? opts.lerp : 0.18;

    var finePointer = global.matchMedia('(hover: hover) and (pointer: fine)');
    var reduceMQ = global.matchMedia('(prefers-reduced-motion: reduce)');
    var docEl = document.documentElement;

    injectCss();

    // The hint chips exist on EVERY path — always-on for touch and reduce,
    // focus-surfaced for fine pointers (the .ad-ccl-fine scope above).
    var chips = [];
    Array.prototype.forEach.call(root.querySelectorAll(selector), function (el) {
      if (el.querySelector('.ad-ccl__hint')) return;
      var chip = document.createElement('span');
      chip.className = 'ad-ccl__hint';
      chip.setAttribute('aria-hidden', 'true');
      chip.textContent = el.getAttribute('data-ad-gesture') || '';
      el.classList.add('ad-ccl-host');
      el.appendChild(chip);
      chips.push({ el: el, chip: chip });
    });

    var active = false;
    var layer = null, arc = null, label = null;
    var raf = 0, on = false;
    var tx = 0, ty = 0, cx = 0, cy = 0;
    var host = null;          // the gesture object under the pointer
    var charge = 0, holdMs = 0, holding = false;

    function want() { return finePointer.matches && !reduce(); }

    function frame(now) {
      raf = 0;
      cx += (tx - cx) * lerpK;
      cy += (ty - cy) * lerpK;
      layer.style.transform = 'translate3d(' + cx.toFixed(1) + 'px,' + cy.toFixed(1) + 'px,0)';
      // the charge dial: fill toward 1 while held, retract fast when released
      var settled = Math.abs(tx - cx) < 0.3 && Math.abs(ty - cy) < 0.3;
      var arcBusy = false;
      if (holding && charge < 1) {
        charge = Math.min(1, charge + (now - lastT) / holdMs);
        arcBusy = charge < 1;
        if (charge >= 1) layer.setAttribute('data-charged', '');
      } else if (!holding && charge > 0) {
        charge = Math.max(0, charge - (now - lastT) * RETRACT_RATE / holdMs);
        arcBusy = charge > 0;
      }
      arc.style.strokeDashoffset = String(1 - charge);
      lastT = now;
      if (on || !settled || arcBusy) raf = global.requestAnimationFrame(frame);
    }
    var lastT = 0;
    function wake() {
      if (!raf) {
        lastT = performance.now();
        raf = global.requestAnimationFrame(frame);
      }
    }

    function onOver(e) {
      var t = e.target;
      if (!t.closest) return;
      var g = t.closest(selector);
      if (g === host) return;
      if (host) offHost();
      if (!g) return;
      host = g;
      label.textContent = g.getAttribute('data-ad-gesture') || '';
      var declared = g.getAttribute('data-ad-gesture-hold');
      holdMs = declared === null ? 0 : (parseInt(declared, 10) || HOLD_DEFAULT);
      g.classList.add('ad-ccl-hide');
      if (!on) {
        on = true;
        cx = tx = e.clientX; cy = ty = e.clientY;
        layer.style.transform = 'translate3d(' + cx + 'px,' + cy + 'px,0)';
        layer.classList.add('is-on');
      }
      wake();
    }
    function offHost() {
      if (!host) return;
      host.classList.remove('ad-ccl-hide');
      host = null;
      holding = false;
      charge = 0;
      arc.style.strokeDashoffset = '1';
      layer.removeAttribute('data-charged');
      on = false;
      layer.classList.remove('is-on'); // the native cursor returns off-surface
    }
    function onOut(e) {
      if (!host) return;
      var to = e.relatedTarget;
      if (to && to.closest && to.closest(selector) === host) return;
      offHost();
    }
    function onMove(e) {
      if (!on) return;
      tx = e.clientX; ty = e.clientY;
      wake();
    }
    // The hold charge — a visual instrument only; the object's own gesture
    // logic owns what a completed hold does.
    function onDown() {
      if (!host || !holdMs) return;
      holding = true;
      wake();
    }
    function onUp() {
      if (!holding && !charge) return;
      holding = false;
      layer.removeAttribute('data-charged');
      wake();
    }
    function onVis() { if (!document.hidden && on) wake(); }

    function activate() {
      if (active) return;
      active = true;
      docEl.classList.add('ad-ccl-fine');
      layer = document.createElement('div');
      layer.className = 'ad-ccl';
      layer.setAttribute('aria-hidden', 'true');
      var svg = document.createElementNS(SVG_NS, 'svg');
      svg.setAttribute('width', String(RING_R * 2));
      svg.setAttribute('height', String(RING_R * 2));
      svg.setAttribute('viewBox', '0 0 ' + RING_R * 2 + ' ' + RING_R * 2);
      var ring = document.createElementNS(SVG_NS, 'circle');
      ring.setAttribute('class', 'ad-ccl__ring');
      ring.setAttribute('cx', String(RING_R));
      ring.setAttribute('cy', String(RING_R));
      ring.setAttribute('r', String(RING_R - 1));
      arc = document.createElementNS(SVG_NS, 'circle');
      arc.setAttribute('class', 'ad-ccl__arc');
      arc.setAttribute('cx', String(RING_R));
      arc.setAttribute('cy', String(RING_R));
      arc.setAttribute('r', String(RING_R - 1));
      arc.setAttribute('pathLength', '1');
      svg.appendChild(ring);
      svg.appendChild(arc);
      label = document.createElement('span');
      layer.appendChild(svg);
      layer.appendChild(label);
      (document.body || docEl).appendChild(layer);
      document.addEventListener('pointerover', onOver);
      document.addEventListener('pointerout', onOut);
      document.addEventListener('pointermove', onMove, { passive: true });
      document.addEventListener('pointerdown', onDown);
      document.addEventListener('pointerup', onUp);
      document.addEventListener('pointercancel', onUp);
      document.addEventListener('visibilitychange', onVis);
    }

    function deactivate() {
      if (!active) return;
      active = false;
      offHost();
      if (raf) { global.cancelAnimationFrame(raf); raf = 0; }
      document.removeEventListener('pointerover', onOver);
      document.removeEventListener('pointerout', onOut);
      document.removeEventListener('pointermove', onMove);
      document.removeEventListener('pointerdown', onDown);
      document.removeEventListener('pointerup', onUp);
      document.removeEventListener('pointercancel', onUp);
      document.removeEventListener('visibilitychange', onVis);
      docEl.classList.remove('ad-ccl-fine');
      if (layer && layer.parentNode) layer.parentNode.removeChild(layer);
      layer = arc = label = null;
    }

    // Dormant-with-fallback: touch and reduce run chips-only (deactivate);
    // a media-query flip re-evaluates live.
    function evaluate() { if (want()) activate(); else deactivate(); }
    mqOn(finePointer, evaluate);
    mqOn(reduceMQ, evaluate);
    evaluate();

    current = {
      destroy: function () {
        mqOff(finePointer, evaluate);
        mqOff(reduceMQ, evaluate);
        deactivate();
        chips.forEach(function (c) {
          if (c.chip.parentNode) c.chip.parentNode.removeChild(c.chip);
          c.el.classList.remove('ad-ccl-host');
        });
        chips = [];
        var s = document.getElementById(CSS_ID);
        if (s && s.parentNode) s.parentNode.removeChild(s);
        current = null;
      }
    };
    return current;
  }

  global.awardContextualCursorLabel = { init: init };
})(typeof window !== 'undefined' ? window : this);
