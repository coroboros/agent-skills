/*
 * living-presence-layer — the inhabited idle band (winners: Bruno's
 * Portfolio — up to 30 'Whispers': flames carrying a short message + the
 * user's country flag drifting in the shared world, plus a global cookie
 * counter and a daily leaderboard; Resn's KPR — a living Web3 world of
 * participants; Messenger — other players visible in the scene). The
 * presence CHANNEL as library machinery: a websocket (or injected source)
 * feeds peer marks that drift in a decor layer over/inside the world, a
 * global counter ticks, and the whole channel DEGRADES TO A SOLO WORLD when
 * the feed is unavailable — presence is never faked (no synthetic peers,
 * ever: an empty room is the truthful room). Inherently bespoke/delegated
 * at the high end: an engine renders marks in-scene by taking the feed via
 * onPeers, which suppresses the DOM layer entirely.
 *
 * Ruled DISTINCT from ambient-idle (decorative breathing of AUTHORED
 * elements — no data, no peers) and perpetual-tile-machines (authored
 * content machines on period clocks): presence marks are LIVE PEER DATA —
 * they join, move, leave with the feed, are capped at 30 (Bruno's verified
 * cap), and vanish when the socket dies.
 *
 * Feed protocol (JSON messages, all fields but type/id optional):
 *   {type:'join',  id, label, flag, x, y}   x,y normalized 0..1 in the layer
 *   {type:'move',  id, x, y}
 *   {type:'leave', id}
 *   {type:'count', value}                   the global counter
 * Peer label/flag land as textContent ONLY — the client never parses
 * markup; moderation (Bruno routes Whispers through a moderation model)
 * stays a server duty.
 *
 * Usage:  awardLivingPresenceLayer.init(root, opts)
 *   root       the world container carrying data-ad-presence (or an ancestor)
 *   url        string  websocket URL — the component owns the socket
 *   source     object  { connect(onMessage, onDown) -> { close() } } — an
 *              injected feed (a Durable Object stub, a test double); wins
 *              over url. Calling onDown() reports the feed's death — the
 *              layer clears to the solo world, same as a socket close
 *   max        number  peer cap (default 30 — the Bruno read)
 *   onPeers    function (peers[]) — the in-engine delegate; when set the DOM
 *              layer renders nothing and the engine draws the marks
 * Returns { destroy() }. Idempotent per container. The counter target is an
 * authored [data-ad-presence-count] anywhere under root — textContent
 * updated on 'count' messages; its authored text is the resting truth.
 *
 * Gates: the socket connects only while the container is on-screen (IO) and
 * the tab visible; hidden or off-screen closes it (marks clear — the world
 * is briefly solo) and a return reconnects once. A dead/unreachable socket
 * is the solo world, silently. The drift rAF (a gentle per-mark wander
 * between feed updates + a lerp toward fed positions) runs only while marks
 * exist and the layer is on-screen. reduced-motion: the wander and glide go
 * dormant — marks stand at their fed positions, updates land instantly
 * (presence is information; the drift is decoration). The layer is
 * pointer-events:none and aria-hidden — decor, never content; a dead script
 * leaves no trace (the layer is component-built from feed data only).
 *
 * Tokens: --ad-accent (the flame dot), --ad-ink + --ad-font-mono (labels),
 *         --ad-ground (label backdrop).
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-living-presence-layer-css';
  var WANDER_AMP = 6;     // px — the ambient wander radius
  var LERP = 0.08;        // glide toward fed positions, per 60fps frame

  var reduce = function () {
    return !!(global.matchMedia &&
      global.matchMedia('(prefers-reduced-motion: reduce)').matches);
  };

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    s.textContent =
      '.ad-presence{position:absolute;inset:0;overflow:clip;pointer-events:none;z-index:3;}' +
      '.ad-presence__mark{position:absolute;left:0;top:0;display:flex;align-items:center;' +
        'gap:.35em;will-change:transform;}' +
      '.ad-presence__dot{width:.55em;height:.55em;border-radius:50%;' +
        'background:var(--ad-accent,oklch(62% 0.2 25));' +
        'box-shadow:0 0 .6em var(--ad-accent,oklch(62% 0.2 25));}' +
      '.ad-presence__tag{font-family:var(--ad-font-mono,ui-monospace,monospace);' +
        'font-size:.62rem;letter-spacing:.08em;color:var(--ad-ink,oklch(96% 0 0));' +
        'background:color-mix(in oklab,var(--ad-ground,oklch(14% 0.01 260)) 72%,transparent);' +
        'padding:.15em .45em;border-radius:2px;white-space:nowrap;}';
    document.head.appendChild(s);
  }

  function init(root, opts) {
    root = root || document;
    opts = opts || {};

    var container = (root.getAttribute && root.getAttribute('data-ad-presence') != null)
      ? root
      : (root.querySelector ? root.querySelector('[data-ad-presence]') : null);
    if (!container) return { destroy: function () {} };
    if (container.__adPresence) return container.__adPresence.handle;

    var max = opts.max != null ? +opts.max : 30;
    var onPeers = typeof opts.onPeers === 'function' ? opts.onPeers : null;
    var still = reduce();

    var layer = null;
    if (!onPeers) {
      injectCss();
      if (global.getComputedStyle &&
          global.getComputedStyle(container).position === 'static') {
        container.style.position = 'relative';
      }
      layer = document.createElement('div');
      layer.className = 'ad-presence';
      layer.setAttribute('aria-hidden', 'true');
      container.appendChild(layer);
    }

    var counterEl = (root.querySelectorAll ? root : document)
      .querySelector('[data-ad-presence-count]');
    var counterResting = counterEl ? counterEl.textContent : '';

    var peers = {};        // id -> { id, label, flag, tx, ty, x, y, phase, el }
    var count = 0;
    var socket = null;     // { close() } — ws wrapper or injected source handle
    var rafId = 0, last = 0;
    var onScreen = false, destroyed = false, attempted = false;

    function peerList() {
      return Object.keys(peers).map(function (k) { return peers[k]; });
    }
    function notify() { if (onPeers) onPeers(peerList()); }

    function place(p, immediate) {
      if (!p.el) return;
      if (immediate) { p.x = p.tx; p.y = p.ty; }
      var w = container.clientWidth, h = container.clientHeight;
      p.el.style.transform = 'translate3d(' + (p.x * w) + 'px,' + (p.y * h) + 'px,0)';
    }

    function makeMark(p) {
      if (!layer) return;
      var el = document.createElement('span');
      el.className = 'ad-presence__mark';
      var dot = document.createElement('span');
      dot.className = 'ad-presence__dot';
      el.appendChild(dot);
      if (p.flag || p.label) {
        var tag = document.createElement('span');
        tag.className = 'ad-presence__tag';
        tag.textContent = [p.flag, p.label].filter(Boolean).join(' '); // textContent only — never markup
        el.appendChild(tag);
      }
      layer.appendChild(el);
      p.el = el;
      place(p, true);
    }

    function clearPeers() {
      peerList().forEach(function (p) {
        if (p.el && p.el.parentNode) p.el.parentNode.removeChild(p.el);
      });
      peers = {};
      count = 0;
      notify();
    }

    function wander(now) {
      rafId = 0;
      if (destroyed || !onScreen || document.hidden) return;
      if (!last) last = now;
      var f = Math.max(1, now - last) / (1000 / 60);
      last = now;
      var any = false;
      peerList().forEach(function (p) {
        any = true;
        var k = 1 - Math.pow(1 - LERP, f);
        p.x += (p.tx - p.x) * k;
        p.y += (p.ty - p.y) * k;
        if (p.el) {
          var w = container.clientWidth, h = container.clientHeight;
          var wob = now / 1000 + p.phase;
          p.el.style.transform = 'translate3d(' +
            (p.x * w + Math.sin(wob * 0.9) * WANDER_AMP) + 'px,' +
            (p.y * h + Math.cos(wob * 0.7) * WANDER_AMP) + 'px,0)';
        }
      });
      if (any) rafId = global.requestAnimationFrame(wander);
    }
    function wake() {
      if (still) return; // dormant drift — marks stand at fed positions
      if (!rafId && onScreen && !document.hidden && Object.keys(peers).length) {
        last = 0;
        rafId = global.requestAnimationFrame(wander);
      }
    }

    function onMessage(msg) {
      if (destroyed || !msg || !msg.type) return;
      if (msg.type === 'count') {
        if (counterEl && msg.value != null) counterEl.textContent = String(msg.value);
        return;
      }
      if (msg.type === 'join' && msg.id != null) {
        if (peers[msg.id] || count >= max) return; // the cap is the cap
        var p = {
          id: msg.id, label: msg.label, flag: msg.flag,
          tx: typeof msg.x === 'number' ? msg.x : Math.random(),
          ty: typeof msg.y === 'number' ? msg.y : Math.random(),
          phase: Math.random() * Math.PI * 2, el: null
        };
        p.x = p.tx; p.y = p.ty;
        peers[msg.id] = p;
        count++;
        makeMark(p);
        notify();
        wake();
      } else if (msg.type === 'move' && peers[msg.id]) {
        var q = peers[msg.id];
        if (typeof msg.x === 'number') q.tx = msg.x;
        if (typeof msg.y === 'number') q.ty = msg.y;
        if (still) place(q, true); // instant under reduce — information, not motion
        notify();
        wake();
      } else if (msg.type === 'leave' && peers[msg.id]) {
        var r = peers[msg.id];
        if (r.el && r.el.parentNode) r.el.parentNode.removeChild(r.el);
        delete peers[msg.id];
        count--;
        notify();
      }
    }

    function disconnect() {
      if (socket) { try { socket.close(); } catch (e) {} socket = null; }
      clearPeers(); // the solo world — never stale ghosts
    }

    function connect() {
      if (destroyed || socket || !onScreen || document.hidden) return;
      if (opts.source && typeof opts.source.connect === 'function') {
        // connect(onMessage, onDown) — onDown lets the source report its own
        // death, so an injected feed degrades to the solo world like a socket
        socket = opts.source.connect(onMessage, function () {
          if (socket) disconnect();
        }) || { close: function () {} };
        return;
      }
      if (!opts.url || !global.WebSocket) return;
      if (attempted) return; // one reconnect per visibility/IO activation — no retry storms
      attempted = true;
      var ws;
      try { ws = new global.WebSocket(opts.url); } catch (e) { return; } // solo world
      ws.onmessage = function (e) {
        var data;
        try { data = JSON.parse(e.data); } catch (err) { return; }
        onMessage(data);
      };
      ws.onclose = function () { if (socket && socket.__ws === ws) disconnect(); };
      ws.onerror = function () { try { ws.close(); } catch (e) {} };
      socket = { __ws: ws, close: function () { ws.onclose = null; ws.close(); } };
    }

    var io = null;
    if (global.IntersectionObserver) {
      io = new global.IntersectionObserver(function (entries) {
        onScreen = entries[entries.length - 1].isIntersecting;
        if (onScreen) { attempted = false; connect(); wake(); }
        else disconnect();
      });
      io.observe(container);
    } else {
      onScreen = true;
      connect();
    }
    function onVis() {
      if (document.hidden) disconnect();
      else { attempted = false; connect(); wake(); }
    }
    document.addEventListener('visibilitychange', onVis);

    var handle = {
      destroy: function () {
        destroyed = true;
        if (rafId) { global.cancelAnimationFrame(rafId); rafId = 0; }
        disconnect();
        document.removeEventListener('visibilitychange', onVis);
        if (io) io.disconnect();
        if (layer && layer.parentNode) layer.parentNode.removeChild(layer);
        if (counterEl) counterEl.textContent = counterResting;
        delete container.__adPresence;
      }
    };
    container.__adPresence = { handle: handle };
    return handle;
  }

  global.awardLivingPresenceLayer = { init: init };
})(typeof window !== 'undefined' ? window : this);
