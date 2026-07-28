/*
 * in-3d-dom-input-bridge — DOM input recreated for an in-engine world
 * (winner: Bruno's Portfolio — SOTD 2026-01-21 + Dev Award + SOTM Jan 2026;
 * 'standard DOM interactions (click/scroll/keyboard/touch/gamepad) are
 * recreated as 3D raycasts' — the usability fallback that keeps the
 * archetype above its 30% Usability floor). The world-level half of the
 * bridge, BOTH directions: every standard DOM channel is normalized into
 * one input frame the engine consumes (DOM → 3D), and the engine's own
 * raycast state is reflected back into real DOM semantics (3D → DOM).
 *
 * Ruled DISTINCT + COMPANION to raycast-object-state: that component owns
 * the per-MESH pointer state machine — hover/tap hit cue + focusable
 * proxies, via the caller's hitTest — the OBJECT axis. This bridge owns the
 * remaining channels a chrome-less world needs to stay navigable — the
 * WORLD axis: keyboard axes (arrows/WASD held), touch-drag axes (a virtual
 * joystick on the surface), wheel advance (the world owns the wheel — there
 * is no native scroll under this stack), gamepad polling (left stick +
 * primary button) — plus the application focus contract (the surface is a
 * real tab stop, role=application, keys act only while it holds focus) and
 * the reverse reflection (handle.setHover: the engine reports its raycast
 * hover, the bridge writes cursor/attribute/status so scene state reaches
 * the DOM). A page ships both: state per object, bridge for the world.
 *
 * The discoverable anchor (Usability's ten-second window): when a
 * [data-ad-bridge-start] control exists — a REAL button the builder authors
 * ('click to start') — the bridge arms on its activation and moves focus to
 * the surface; without one it arms at once.
 *
 * Usage:  awardIn3dDomInputBridge.init(root, opts)
 *   root       the surface carrying data-ad-bridge (or an ancestor/document)
 *   label      string   accessible name for the surface (aria-label)
 *   onFrame    function ({x, y})  per rAF while any axis is live — merged
 *              keyboard/touch/gamepad axes, each -1..1 (the engine lerps)
 *   onAdvance  function (delta)   wheel advance in px-normalized units
 *   onAction   function (source)  Enter/Space on the focused surface or
 *              gamepad primary — the world verb ('key'|'gamepad')
 *   radius     px  the touch joystick's full-deflection radius (default 48)
 * Returns { destroy(), arm(), setHover(id, label), clearHover() }.
 * Idempotent per surface.
 *
 * Gates: the axis loop runs ONLY while armed, the tab visible, the surface
 * on-screen (IntersectionObserver), and a channel live (a key held, a drag
 * active, a gamepad connected) — zero per-frame work at rest. Wheel is
 * non-passive only while armed. Under prefers-reduced-motion the state
 * machine still runs (interaction is not decoration — the
 * raycast-object-state law); what the engine does with the frames is its
 * own reduce answer. No canvas is
 * owned here — the engine renders; the bridge only routes input, so the
 * world stays content-visible without it.
 *
 * Tokens: --ad-accent (the surface's :focus-visible ring).
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-in-3d-dom-input-bridge-css';
  var DEAD_ZONE = 0.15; // gamepad stick noise floor

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      '[data-ad-bridge]:focus-visible{outline:2px solid var(--ad-accent,oklch(62% 0.2 25));' +
        'outline-offset:2px;}' +
      '[data-ad-bridge]{touch-action:none;}';
    document.head.appendChild(s);
  }

  var KEYS = {
    ArrowUp: [0, -1], KeyW: [0, -1],
    ArrowDown: [0, 1], KeyS: [0, 1],
    ArrowLeft: [-1, 0], KeyA: [-1, 0],
    ArrowRight: [1, 0], KeyD: [1, 0]
  };

  function init(root, opts) {
    root = root || document;
    opts = opts || {};

    var surface = (root.getAttribute && root.getAttribute('data-ad-bridge') != null)
      ? root
      : (root.querySelector ? root.querySelector('[data-ad-bridge]') : null);
    if (!surface) return { destroy: function () {}, arm: function () {},
                           setHover: function () {}, clearHover: function () {} };
    if (surface.__adInputBridge) return surface.__adInputBridge.handle;

    var onFrame = typeof opts.onFrame === 'function' ? opts.onFrame : function () {};
    var onAdvance = typeof opts.onAdvance === 'function' ? opts.onAdvance : function () {};
    var onAction = typeof opts.onAction === 'function' ? opts.onAction : function () {};
    var radius = opts.radius != null ? +opts.radius : 48;

    injectCss();

    // the application focus contract — keys act only while the surface holds focus
    if (!surface.hasAttribute('tabindex')) surface.setAttribute('tabindex', '0');
    surface.setAttribute('role', 'application');
    if (opts.label) surface.setAttribute('aria-label', opts.label);

    var armed = false, onScreen = false, rafId = 0;
    var held = {};                       // code -> [x, y]
    var drag = null;                     // { id, x0, y0, x, y }
    var pads = 0;                        // connected gamepads
    var padHeld = false;                 // primary-button edge detect
    var wasZero = true;
    var prevCursor = surface.style.cursor;
    var statusEl = surface.querySelector('[data-ad-bridge-status]') ||
      (root.querySelector ? root.querySelector('[data-ad-bridge-status]') : null);
    var startBtn = (root.querySelector ? root.querySelector('[data-ad-bridge-start]') : null);

    function channelLive() {
      for (var k in held) return true;
      return !!drag || pads > 0;
    }
    function active() {
      return armed && onScreen && !document.hidden && channelLive();
    }
    function wake() {
      if (!rafId && active()) rafId = global.requestAnimationFrame(frame);
    }

    function frame() {
      rafId = 0;
      if (!active()) {
        // the last channel just died — settle the engine on one zero frame
        if (!wasZero) { onFrame({ x: 0, y: 0 }); wasZero = true; }
        return;
      }
      var x = 0, y = 0;
      for (var k in held) { x += held[k][0]; y += held[k][1]; }
      if (drag) {
        x += Math.max(-1, Math.min(1, (drag.x - drag.x0) / radius));
        y += Math.max(-1, Math.min(1, (drag.y - drag.y0) / radius));
      }
      if (pads > 0 && global.navigator.getGamepads) {
        var list = global.navigator.getGamepads();
        for (var i = 0; i < list.length; i++) {
          var gp = list[i];
          if (!gp || !gp.connected) continue;
          var gx = gp.axes[0] || 0, gy = gp.axes[1] || 0;
          if (Math.abs(gx) > DEAD_ZONE) x += gx;
          if (Math.abs(gy) > DEAD_ZONE) y += gy;
          var pressed = !!(gp.buttons[0] && gp.buttons[0].pressed);
          if (pressed && !padHeld) onAction('gamepad');
          padHeld = pressed;
          break; // first connected pad steers
        }
      }
      x = Math.max(-1, Math.min(1, x));
      y = Math.max(-1, Math.min(1, y));
      var zero = x === 0 && y === 0;
      if (!zero || !wasZero) onFrame({ x: x, y: y }); // one settling zero-frame, then rest
      wasZero = zero;
      rafId = global.requestAnimationFrame(frame);
    }

    // --- keyboard: axes while focused, Enter/Space = the world verb ---
    function onKeyDown(e) {
      if (document.activeElement !== surface) return;
      if (KEYS[e.code]) {
        e.preventDefault(); // the world owns these keys while focused
        held[e.code] = KEYS[e.code];
        // a discrete tap (down+up inside one frame) still nudges — the DOM
        // arrow-key convention; the loop then owns the held state
        if (!e.repeat) {
          wasZero = false;
          onFrame({ x: KEYS[e.code][0], y: KEYS[e.code][1] });
        }
        wake();
      } else if (e.code === 'Enter' || e.code === 'Space') {
        e.preventDefault();
        onAction('key');
      }
    }
    function onKeyUp(e) { delete held[e.code]; }
    function onBlur() { held = {}; }

    // --- touch drag: the virtual joystick (touch pointers only — a mouse
    // drag is engine/camera territory, and mouse users hold the keys) ---
    function onPointerDown(e) {
      if (e.pointerType !== 'touch' || !armed || drag) return;
      drag = { id: e.pointerId, x0: e.clientX, y0: e.clientY, x: e.clientX, y: e.clientY };
      // capture keeps the drag through fast swipes; a vanished pointer throws
      try { surface.setPointerCapture(e.pointerId); } catch (err) {}
      wake();
    }
    function onPointerMove(e) {
      if (drag && e.pointerId === drag.id) { drag.x = e.clientX; drag.y = e.clientY; }
    }
    function onPointerEnd(e) {
      if (drag && e.pointerId === drag.id) drag = null;
    }

    // --- wheel: the world's advance channel (no native scroll to fall to) ---
    function onWheel(e) {
      if (!armed) return;
      e.preventDefault();
      var d = e.deltaY;
      if (e.deltaMode === 1) d *= 16; else if (e.deltaMode === 2) d *= global.innerHeight;
      onAdvance(d);
    }

    // --- gamepad lifecycle: connection toggles the polling channel ---
    function onPadConnect() { pads++; wake(); }
    function onPadDisconnect() { pads = Math.max(0, pads - 1); }

    function arm() {
      if (armed) return;
      armed = true;
      surface.focus({ preventScroll: true });
      wake();
    }
    function onStart(e) { e.preventDefault(); arm(); }

    var io = null;
    if (global.IntersectionObserver) {
      io = new global.IntersectionObserver(function (entries) {
        onScreen = entries[entries.length - 1].isIntersecting;
        wake();
      });
      io.observe(surface);
    } else {
      onScreen = true;
    }
    function onVis() { wake(); }

    surface.addEventListener('keydown', onKeyDown);
    surface.addEventListener('keyup', onKeyUp);
    surface.addEventListener('blur', onBlur);
    surface.addEventListener('pointerdown', onPointerDown);
    surface.addEventListener('pointermove', onPointerMove, { passive: true });
    surface.addEventListener('pointerup', onPointerEnd);
    surface.addEventListener('pointercancel', onPointerEnd);
    surface.addEventListener('wheel', onWheel, { passive: false });
    global.addEventListener('gamepadconnected', onPadConnect);
    global.addEventListener('gamepaddisconnected', onPadDisconnect);
    document.addEventListener('visibilitychange', onVis);
    if (startBtn) startBtn.addEventListener('click', onStart);
    else arm(); // no anchor authored — the world is live at once

    var handle = {
      arm: arm,
      // 3D → DOM: the engine's raycast hover becomes real DOM state
      setHover: function (id, label) {
        surface.setAttribute('data-ad-bridge-hover', id != null ? String(id) : '');
        surface.style.cursor = 'pointer';
        if (statusEl) statusEl.textContent = label != null ? String(label) : '';
      },
      clearHover: function () {
        surface.removeAttribute('data-ad-bridge-hover');
        surface.style.cursor = prevCursor;
        if (statusEl) statusEl.textContent = '';
      },
      destroy: function () {
        if (rafId) { global.cancelAnimationFrame(rafId); rafId = 0; }
        surface.removeEventListener('keydown', onKeyDown);
        surface.removeEventListener('keyup', onKeyUp);
        surface.removeEventListener('blur', onBlur);
        surface.removeEventListener('pointerdown', onPointerDown);
        surface.removeEventListener('pointermove', onPointerMove);
        surface.removeEventListener('pointerup', onPointerEnd);
        surface.removeEventListener('pointercancel', onPointerEnd);
        surface.removeEventListener('wheel', onWheel);
        global.removeEventListener('gamepadconnected', onPadConnect);
        global.removeEventListener('gamepaddisconnected', onPadDisconnect);
        document.removeEventListener('visibilitychange', onVis);
        if (startBtn) startBtn.removeEventListener('click', onStart);
        if (io) io.disconnect();
        handle.clearHover();
        delete surface.__adInputBridge;
      }
    };
    surface.__adInputBridge = { handle: handle };
    return handle;
  }

  global.awardIn3dDomInputBridge = { init: init };
})(typeof window !== 'undefined' ? window : this);
