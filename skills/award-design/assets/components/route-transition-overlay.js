/*
 * route-transition-overlay — the continuity law across a page navigation
 * (winners: Delvaux — HM Jun 15 2026, multi-page commerce, 51North case
 * study: 'dynamic transitions and subtle animations unify product
 * categories'; Urban Jürgensen — SOTD Oct 2025, PDP + product pages;
 * Brunello Cucinelli AI — SOTD Jul 9 2026. The per-site transition
 * mechanic — Barba/Taxi vs bespoke — was not exposed; this is the
 * playbook's Barba.js/Taxi.js-style executable default). On a multi-page
 * maison the signature thread dies at every href — this component owns the
 * NAVIGATION so it survives: intercept the same-origin link click
 * (preventDefault), cover the view with a full-bleed overlay wipe
 * (transform panel — compositor-only), fetch the next document and swap the
 * [data-ad-view] container under full cover, then hold a brief loader
 * RE-ENTRY beat while the incoming page re-establishes the thread (the
 * onEnter hook — re-init the décor bed / WebGL ground / scored drift
 * there), and uncover. History is honest: pushState on navigate, popstate
 * (back AND forward) rides the same beat. Any failure — cross-origin,
 * fetch error, no container in the incoming document — falls through to
 * the browser's own navigation; the visitor is never trapped.
 * Ruled DISTINCT, not an alias, on mechanism: curtain-transition is an
 * imperative wipe TOOL (play(fn) around a swap the BUILDER performs — it
 * intercepts nothing, fetches nothing, owns no history, has no re-entry
 * beat); route-view-transition-carrier is the minimalist SPA crossfade
 * around a builder-supplied swap fn — same builder-owned swap, quiet
 * register, no interception, no fetch; page-transition-choreography is
 * bold-maximal's between-view spectacle (engine double-render blend or
 * morphing-lip wipe) — go(fn) again builder-driven, and its register is
 * the peak the luxury page never plays. None of the three keeps a real
 * href alive; this one is the multi-PAGE pipeline.
 *
 * Usage:  var rto = awardRouteTransitionOverlay.init(root, opts)
 *   root       Element|Document  scope for link interception (default document)
 *   container  string    the swapped view root (default '[data-ad-view]')
 *   onLeave    function(url)          fires as the cover starts
 *   onEnter    function(container, url)  the re-entry hook — re-establish
 *              the thread here; may return a promise, the cover holds for it
 *              (capped by reentry) so the incoming page is never shown dead
 *   reentry    ms  cap on the held re-entry beat (default 450 — brief)
 *   color      string  panel ground (default var(--ad-ground-2))
 *   zIndex     number  panel stacking (default 9998)
 * Returns { go(url), destroy() } — go(url) drives the same beat
 * programmatically. destroy() unbinds interception, removes the panel and
 * stylesheet (history entries already written stay valid — popstate after
 * destroy is the browser's own reload).
 *
 * The register is the luxury one: cover and uncover each ride
 * --ad-dur-base on --ad-ease-signature (decelerating, ~.42s a side — the
 * whole beat lands in the gap's .6-1s band with the re-entry hold between).
 * Reduced motion: NO panel — fetch, instant container swap, then a short
 * WAAPI cross-fade on the container (the gap's own degrade order).
 * A11y: the panel is aria-hidden and inert at rest, blocks input only
 * mid-beat; after a swap, focus moves to the incoming container
 * (tabindex="-1" applied transiently) and document.title updates from the
 * fetched document — a navigation, not a mutation. No-JS: plain hrefs
 * navigate; nothing renders at rest.
 *
 * Tokens: --ad-ground-2 (panel ground), --ad-dur-base + --ad-ease-signature
 * (each side of the wipe), --ad-dur-reveal (the reduce cross-fade).
 */
(function (global) {
  'use strict';
  var CSS_ID = 'ad-route-transition-overlay-css';

  var reduce = function () {
    return !!(global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches);
  };

  function injectCss(zIndex, color) {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement('style');
    s.id = CSS_ID;
    var move = 'var(--ad-dur-base,420ms) var(--ad-ease-signature,cubic-bezier(.16,1,.3,1))';
    s.textContent =
      '.ad-rto{position:fixed;inset:0;z-index:' + zIndex + ';' +
      'background:' + (color || 'var(--ad-ground-2,oklch(18% 0.01 260))') + ';' +
      'transform:translateY(101%);will-change:transform;pointer-events:none;' +
      'display:grid;place-items:center;}' +
      '.ad-rto.is-moving{transition:transform ' + move + ';}' +
      '.ad-rto.is-cover{transform:translateY(0);pointer-events:auto;}' +
      '.ad-rto.is-exit{transform:translateY(-101%);}' +
      // the re-entry mark: a hairline that breathes while the thread re-roots
      '.ad-rto::after{content:"";width:min(18vw,9rem);height:1px;' +
      'background:currentColor;opacity:0;transform:scaleX(.2);' +
      'transform-origin:left;transition:transform ' + move + ',opacity 200ms ease;}' +
      '.ad-rto.is-cover::after{opacity:.5;transform:scaleX(1);}';
    document.head.appendChild(s);
  }

  var current = null; // one navigation owner per page, ever

  function init(root, opts) {
    root = root || document;
    opts = opts || {};
    if (current) return current;

    var containerSel = opts.container || '[data-ad-view]';
    var reentryCap = opts.reentry != null ? opts.reentry : 450;
    var panel = null;
    var busy = false;

    function container() {
      return document.querySelector(containerSel) || document.body;
    }

    function ensurePanel() {
      if (panel) return;
      injectCss(opts.zIndex != null ? opts.zIndex : 9998, opts.color);
      panel = document.createElement('div');
      panel.className = 'ad-rto';
      panel.setAttribute('aria-hidden', 'true');
      (document.body || document.documentElement).appendChild(panel);
    }

    function moveTo(cls) {
      return new Promise(function (resolve) {
        var done = function (e) {
          // only the panel's OWN transform ride ends the move — the ::after
          // hairline's transitions bubble here too and resolved a beat early
          if (e && (e.target !== panel || e.pseudoElement || e.propertyName !== 'transform')) return;
          panel.removeEventListener('transitionend', done);
          clearTimeout(guard);
          resolve();
        };
        // a lost transitionend (tab hidden mid-beat) never strands the cover
        var guard = setTimeout(done, 1200);
        panel.addEventListener('transitionend', done);
        panel.classList.add('is-moving');
        requestAnimationFrame(function () { panel.classList.add(cls); });
      });
    }

    function resetPanel() {
      panel.classList.remove('is-moving', 'is-cover', 'is-exit');
    }

    // Fetch + parse + swap: the incoming document's container replaces the
    // standing one's children; title travels too. Throws on any miss so the
    // caller can fall through to a real navigation.
    function swapFrom(url) {
      return global.fetch(url, { headers: { 'X-Requested-With': 'ad-rto' } })
        .then(function (r) {
          if (!r.ok) throw new Error('HTTP ' + r.status);
          return r.text();
        })
        .then(function (html) {
          var doc = new DOMParser().parseFromString(html, 'text/html');
          var next = doc.querySelector(containerSel);
          var mine = container();
          if (!next || mine === document.body) throw new Error('no view container');
          mine.replaceChildren.apply(mine, Array.prototype.slice.call(next.childNodes)
            .map(function (n) { return document.adoptNode(n); }));
          document.title = doc.title || document.title;
          return mine;
        });
    }

    function settleFocus(mine) {
      // the tabindex stays until focus moves on — removing it synchronously
      // drops the focus we just placed (driven finding)
      mine.setAttribute('tabindex', '-1');
      mine.addEventListener('blur', function onBlur() {
        mine.removeEventListener('blur', onBlur);
        mine.removeAttribute('tabindex');
      });
      mine.focus({ preventScroll: true });
    }

    function enterBeat(mine, url) {
      // The re-entry: the thread re-roots under the held cover, capped so a
      // slow re-init never strands the visitor behind the panel.
      var p;
      try { p = opts.onEnter ? opts.onEnter(mine, url) : null; }
      catch (e) { p = null; }
      return Promise.race([
        Promise.resolve(p).catch(function () {}),
        new Promise(function (res) { setTimeout(res, reentryCap); })
      ]);
    }

    function run(url, push) {
      if (busy) return Promise.resolve();
      busy = true;
      if (opts.onLeave) { try { opts.onLeave(url); } catch (e) {} }

      // Reduce: instant swap + a short cross-fade — no panel ever shows.
      if (reduce()) {
        return swapFrom(url)
          .then(function (mine) {
            if (push) history.pushState({ adRto: true }, '', url);
            global.scrollTo(0, 0);
            settleFocus(mine);
            if (mine.animate) {
              mine.animate([{ opacity: 0.35 }, { opacity: 1 }],
                { duration: parseFloat(getComputedStyle(document.documentElement)
                    .getPropertyValue('--ad-dur-reveal')) || 300, easing: 'ease-out' });
            }
            return enterBeat(mine, url);
          })
          .then(function () { busy = false; })
          .catch(function () { global.location.href = url; });
      }

      ensurePanel();
      return moveTo('is-cover')
        .then(function () { return swapFrom(url); })
        .then(function (mine) {
          if (push) history.pushState({ adRto: true }, '', url);
          global.scrollTo(0, 0);
          settleFocus(mine);
          return enterBeat(mine, url);
        })
        .then(function () { return moveTo('is-exit'); })
        .then(function () {
          resetPanel();
          busy = false;
        })
        .catch(function () { global.location.href = url; });
    }

    // Same-origin, same-tab, unmodified left-clicks on real page links only —
    // everything else stays the browser's.
    function onClick(e) {
      if (e.defaultPrevented || e.button !== 0 ||
          e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
      var a = e.target && e.target.closest ? e.target.closest('a[href]') : null;
      if (!a || a.target || a.hasAttribute('download') ||
          a.getAttribute('href').charAt(0) === '#') return;
      var url;
      try { url = new URL(a.href, global.location.href); } catch (err) { return; }
      if (url.origin !== global.location.origin) return;
      if (url.pathname === global.location.pathname &&
          url.search === global.location.search) return; // same page — anchors stay native
      e.preventDefault();
      run(url.href, true);
    }

    // Back AND forward ride the same beat — the thread survives both
    // directions of the history walk.
    function onPop() {
      run(global.location.href, false);
    }

    root.addEventListener('click', onClick);
    global.addEventListener('popstate', onPop);
    // mark the entry state so the first back-arrival still swaps in-beat
    if (!history.state || !history.state.adRto) {
      try { history.replaceState({ adRto: true }, '', global.location.href); } catch (e) {}
    }

    current = {
      go: function (url) { return run(new URL(url, global.location.href).href, true); },
      destroy: function () {
        root.removeEventListener('click', onClick);
        global.removeEventListener('popstate', onPop);
        if (panel && panel.parentNode) panel.parentNode.removeChild(panel);
        panel = null;
        var s = document.getElementById(CSS_ID);
        if (s && s.parentNode) s.parentNode.removeChild(s);
        current = null;
      }
    };
    return current;
  }

  global.awardRouteTransitionOverlay = { init: init };
})(typeof window !== 'undefined' ? window : this);
