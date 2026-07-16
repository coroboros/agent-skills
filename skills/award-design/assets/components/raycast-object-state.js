/*
 * raycast-object-state — per-object interaction states for meshes INSIDE a
 * WebGL scene (winners: Messenger by abeto — operable scene objects; Egg Hunt
 * by Merci-Michel; Bruno Simon — drive/click targets). The hover/tap axis the
 * DOM-element canon omits: a raycaster maps the pointer onto scene meshes, and
 * this component owns the input state machine + keyboard reach around it. The
 * SCENE owns rendering, so no Three import ever crosses this boundary — the
 * caller wires opts.hitTest to its own raycaster and paints each state itself.
 *
 * On fine-pointer hover of an interactive mesh it emits 'hover' and switches
 * the cursor to a pointer affordance; on a tap/click it fires an immediate
 * sub-160ms hit cue, then runs the mesh's verb; non-interactive meshes (hitTest
 * returns null) never respond. Touch has no hover — the raycast fires on the
 * tap. Visually-hidden focusable proxies make every scene action keyboard-
 * reachable. Content-visible always: the scene renders with no JS; this only
 * routes interaction onto it, it never draws the mesh.
 *
 * Usage:  awardRaycastObjectState.init(root, opts)
 *   root       the canvas container carrying data-ad-raycast
 *   hitTest    (x, y, nx, ny) -> id|null   REQUIRED — the caller's raycaster.
 *              x,y are pointer coords relative to root; nx,ny the same point as
 *              normalized device coords (-1..1, y up) for a Three raycaster.
 *   onState    (id, state)   state ∈ 'hover' | 'rest' | 'hit' — the scene paints
 *              its own visual (emissive lift / outline / scale ≈1.05).
 *   onActivate (id)   the mesh's verb — fired after the hit cue starts, never before.
 *   cueMs      hit-cue window (default 140, clamped 90–160): on activation 'hit'
 *              fires at once, then 'rest' (or 'hover' if still engaged) after cueMs.
 *   proxies    [{ id, label }]   focusable buttons rendered inside root — focus →
 *              'hover', blur → 'rest', Enter/Space → the same hit-then-activate path.
 * Returns { destroy() }. Idempotent per root. Fine pointer only for hover + the
 * pointer cursor (matchMedia '(any-hover:hover) and (pointer:fine)'); tap-to-
 * activate works on every pointer. reduced-motion: the state machine still runs
 * (interaction is not decoration) — scenes swap animated highlights for instant
 * state swaps, and the component's focus chip drops its fade.
 *
 * Perf: one pointermove writing two numbers, coalesced to a single rAF hit-test;
 * no per-frame work at rest; opacity-only transition on the focus chip.
 *
 * Tokens: --ad-accent (focus-chip outline), --ad-ground + --ad-ink (chip fill),
 *         --ad-font-mono (chip label), --ad-dur-base (chip fade).
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-raycast-object-state-css';
  var TAP_SLOP = 10; // px — a pointerup within this of its down is a tap, not a scene drag

  var fine = function () {
    return !!(global.matchMedia &&
      global.matchMedia('(any-hover: hover) and (pointer: fine)').matches);
  };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    // Proxy buttons ride the standard sr-only recipe so they stay off-screen yet
    // tab-reachable; :focus-visible re-inflates the focused one into a minimal chip
    // legible over the canvas. Anchored bottom-left — only one holds focus at once.
    s.textContent =
      '.ad-raycast-proxy{position:absolute;left:0;bottom:0;width:1px;height:1px;' +
        'margin:-1px;padding:0;border:0;overflow:hidden;clip:rect(0 0 0 0);' +
        'clip-path:inset(50%);white-space:nowrap;opacity:0;' +
        'background:transparent;color:inherit;}' +
      '.ad-raycast-proxy:focus-visible{width:auto;height:auto;margin:.5rem;padding:.4em .7em;' +
        'overflow:visible;clip:auto;clip-path:none;opacity:1;z-index:2;cursor:pointer;' +
        'font-family:var(--ad-font-mono,ui-monospace,monospace);font-size:.72rem;' +
        'letter-spacing:.14em;text-transform:uppercase;line-height:1;' +
        'background:var(--ad-ground,oklch(14% 0.01 260));color:var(--ad-ink,oklch(96% 0 0));' +
        'outline:2px solid var(--ad-accent,oklch(62% 0.2 25));outline-offset:2px;' +
        'transition:opacity var(--ad-dur-base,420ms) ease;}' +
      '@media (prefers-reduced-motion:reduce){.ad-raycast-proxy:focus-visible{transition:none;}}';
    document.head.appendChild(s);
  }

  function clampCue(v) {
    v = v == null ? 140 : +v;
    if (isNaN(v)) v = 140;
    return v < 90 ? 90 : v > 160 ? 160 : v;
  }

  // the tapped point as normalized device coords (-1..1, y up) — Three raycaster convention
  function ndc(x, y, w, h) {
    return [(x / Math.max(1, w)) * 2 - 1, -((y / Math.max(1, h)) * 2 - 1)];
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};

    // Resolve the interactive surface: root itself if it carries the marker, else
    // the first descendant that does — so init(container) and init(document) both work.
    var container = (root.getAttribute && root.getAttribute('data-ad-raycast') != null)
      ? root
      : (root.querySelector ? root.querySelector('[data-ad-raycast]') : null);
    if (!container || typeof opts.hitTest !== 'function') return { destroy: function () {} };

    // Idempotent per surface.
    if (container.__adRaycast) return container.__adRaycast.handle;

    var hitTest = opts.hitTest;
    var onState = typeof opts.onState === 'function' ? opts.onState : function () {};
    var onActivate = typeof opts.onActivate === 'function' ? opts.onActivate : function () {};
    var cueMs = clampCue(opts.cueMs);
    var useHover = fine();

    var hoveredId = null;         // pointer hover (fine only)
    var focusedId = null;         // proxy focus
    var cues = {};                // id -> timeout while its hit cue plays
    var rafId = 0, mx = 0, my = 0;
    var downX = 0, downY = 0, downId = -1;
    var prevCursor = container.style.cursor;
    var proxyEls = [];

    injectCss();

    // Ensure a positioning context so the absolute proxy chips anchor to root.
    var hadInlinePos = container.style.position;
    if (global.getComputedStyle &&
        global.getComputedStyle(container).position === 'static') {
      container.style.position = 'relative';
    }

    // the settle state for an id whose cue just ended: still engaged → 'hover', else 'rest'
    function settle(id) {
      return (hoveredId === id || focusedId === id) ? 'hover' : 'rest';
    }

    function startCue(id) {
      if (id == null) return;
      onState(id, 'hit');   // cue starts first …
      onActivate(id);       // … then the verb, never before
      if (cues[id]) clearTimeout(cues[id]);
      cues[id] = setTimeout(function () {
        delete cues[id];
        onState(id, settle(id));
      }, cueMs);
    }

    // --- fine-pointer hover pipeline ---
    function frame() {
      rafId = 0;
      var r = container.getBoundingClientRect();
      var x = mx - r.left, y = my - r.top;
      var n = ndc(x, y, r.width, r.height);
      var id = hitTest(x, y, n[0], n[1]);
      if (id === hoveredId) return;
      var prev = hoveredId;
      hoveredId = id;
      // a mesh mid-cue keeps its 'hit' — the cue owns its state until it settles
      if (prev != null && !cues[prev]) onState(prev, focusedId === prev ? 'hover' : 'rest');
      if (id != null && !cues[id]) onState(id, 'hover');
      container.style.cursor = id != null ? 'pointer' : prevCursor;
    }
    function onMove(e) {
      mx = e.clientX; my = e.clientY;
      if (!rafId) rafId = global.requestAnimationFrame(frame);
    }
    function clearHover() {
      if (rafId) { global.cancelAnimationFrame(rafId); rafId = 0; }
      if (hoveredId != null && !cues[hoveredId]) {
        onState(hoveredId, focusedId === hoveredId ? 'hover' : 'rest');
      }
      hoveredId = null;
      container.style.cursor = prevCursor;
    }

    // --- activation on every pointer: a tap on the surface, not a scene drag ---
    function onDown(e) {
      downX = e.clientX; downY = e.clientY; downId = e.pointerId;
    }
    function onUp(e) {
      if (e.pointerId !== downId) return;
      if (Math.abs(e.clientX - downX) > TAP_SLOP ||
          Math.abs(e.clientY - downY) > TAP_SLOP) return;
      var r = container.getBoundingClientRect();
      var x = e.clientX - r.left, y = e.clientY - r.top;
      var n = ndc(x, y, r.width, r.height);
      startCue(hitTest(x, y, n[0], n[1]));
    }
    function onCancel() {
      downId = -1;
      clearHover();
    }

    // --- keyboard proxies: focusable buttons standing in for the scene meshes ---
    (opts.proxies || []).forEach(function (p) {
      if (!p || p.id == null) return;
      var id = p.id;
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'ad-raycast-proxy';
      btn.setAttribute('aria-label', p.label != null ? p.label : String(id));
      btn.__adOnFocus = function () {
        focusedId = id;
        if (!cues[id]) onState(id, 'hover');
      };
      btn.__adOnBlur = function () {
        if (focusedId === id) focusedId = null;
        if (!cues[id]) onState(id, hoveredId === id ? 'hover' : 'rest');
      };
      // a native button turns Enter and Space into one click — no double-fire
      btn.__adOnClick = function () { startCue(id); };
      btn.addEventListener('focus', btn.__adOnFocus);
      btn.addEventListener('blur', btn.__adOnBlur);
      btn.addEventListener('click', btn.__adOnClick);
      container.appendChild(btn);
      proxyEls.push(btn);
    });

    container.addEventListener('pointerdown', onDown);
    container.addEventListener('pointerup', onUp);
    container.addEventListener('pointercancel', onCancel);
    if (useHover) {
      container.addEventListener('pointermove', onMove, { passive: true });
      container.addEventListener('pointerleave', clearHover);
    }

    var handle = {
      destroy: function () {
        container.removeEventListener('pointerdown', onDown);
        container.removeEventListener('pointerup', onUp);
        container.removeEventListener('pointercancel', onCancel);
        container.removeEventListener('pointermove', onMove);
        container.removeEventListener('pointerleave', clearHover);
        if (rafId) { global.cancelAnimationFrame(rafId); rafId = 0; }
        Object.keys(cues).forEach(function (k) { clearTimeout(cues[k]); });
        cues = {};
        proxyEls.forEach(function (btn) {
          btn.removeEventListener('focus', btn.__adOnFocus);
          btn.removeEventListener('blur', btn.__adOnBlur);
          btn.removeEventListener('click', btn.__adOnClick);
          if (btn.parentNode) btn.parentNode.removeChild(btn);
        });
        proxyEls = [];
        container.style.cursor = prevCursor;
        container.style.position = hadInlinePos;
        delete container.__adRaycast;
      }
    };
    container.__adRaycast = { handle: handle };
    return handle;
  }

  global.awardRaycastObjectState = { init: init };
})(typeof window !== 'undefined' ? window : this);
