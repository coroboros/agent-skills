/*
 * in-scene-ambient-life — the between-input life of a rendered world
 * (winners: ERA by Vide Infra — particle-object cars following the road
 * paths of the city scene; Jordan Breton — butterflies, wind-blown flora
 * and a waterfall keeping the world alive between inputs; Messenger by
 * abeto — a world that never freezes between gestures. The gap's third
 * citation, other PLAYERS drifting in Messenger's world, is ruled OUT of
 * this component: live peers are living-presence-layer's channel and its
 * no-synthetic-peers law stands — presence is never faked. THIS
 * component's agents are AUTHORED non-human life: traffic, fauna, flora,
 * drift.) Self-animating detail INSIDE the scene so the spine never
 * freezes between inputs — the in-canvas sibling of the DOM idle channel.
 *
 * Ruled DISTINCT on the seams: ambient-idle breathes AUTHORED DOM
 * elements (CSS keyframes over glow/float/shimmer/pulse — no world, no
 * agents); living-presence-layer renders LIVE PEER DATA (marks join,
 * move and leave with a socket, capped, never synthetic); THIS is
 * authored in-world life on a deterministic clock. Why this is library
 * machinery at all: a scene owns ONE rAF loop — ambient life lives
 * inside it (onTick is the engine's frame hook), never in a second
 * hand-rolled loop beside the render. The builder ships populations as
 * DATA fed to init; the loop, gates and kinematics come debugged.
 *
 * THE SEAM: the SCENE owns rendering — no THREE import (no engine import
 * of any kind) ever crosses this boundary, the raycast-object-state
 * precedent. The component owns the CLOCK, the GATES and the KINEMATICS;
 * each population's `apply` callback receives a plain agent object
 * ({ id, index, x, y, z, hx, hy, hz, phase }) and the caller paints it
 * into its own medium — instanceMatrix, sprite, 2D canvas, its choice.
 * One optional onTick(t, dt) fires after all applies per frame — the
 * engine's frame hook (wind phase, uv scroll, the render call itself).
 *
 * Three kinematic modes — one per cited register:
 *   path    agents ride a closed polyline (ERA's cars on road paths):
 *           arc-length parameterized so speed is constant in world
 *           units, spread along the loop by index with per-agent speed
 *           jitter; heading = the segment direction of travel.
 *   wander  bounded organic drift (Jordan Breton's butterflies): two
 *           layered incommensurate sines per axis inside an AABB —
 *           smooth curls, never a twitch; phase is a faster flutter
 *           clock for wing-flap / flicker painting.
 *   drift   a directional stream that wraps its bounds (wind streaks,
 *           waterfall, snow, embers): constant flow along `dir` plus a
 *           soft lateral sway, re-entering opposite the exit face.
 * DETERMINISTIC by law: no Math.random anywhere — all per-agent variance
 * is a seeded fract-sine hash, so the same populations compose the same
 * living world every load (the assembly-loader's determinism precedent).
 * The pose is a pure function of the accumulated clock t, so pausing
 * freezes the world mid-gesture and resuming continues it — no jumps.
 *
 * Usage:  var life = awardInSceneAmbientLife.init(root, {
 *   populations: [{
 *     id: 'traffic', count: 12, mode: 'path'|'wander'|'drift',
 *     path: [[x,y,z], …],                    // path mode — closed loop
 *     bounds: { min: [x,y,z], max: [x,y,z] }, // wander + drift modes
 *     dir: [x,y,z],                          // drift flow, units/sec
 *     speed: 1,                              // units/sec (path, drift)
 *                                            // or curl rate scalar (wander)
 *     jitter: 0.3, seed: 1,
 *     apply: function (agent) {}             // REQUIRED — engine paints
 *   }],
 *   onTick: function (t, dt) {}              // optional frame hook
 * })
 * Returns { getState(), destroy() }. Idempotent per root — a second init
 * on the same root replaces the first. getState() → { running, ticking,
 * visible, hidden, reduce, t, populations: [{ id, count, sample }] } —
 * sample is agent 0's live position, the "is the world actually alive at
 * rest" readout drives and tests assert against.
 *
 * Gates: the loop runs ONLY while the root is on-screen
 * (IntersectionObserver) and the tab visible (visibilitychange); hidden
 * or off-screen cancels the rAF and freezes t — zero work, and the world
 * resumes exactly where it paused. No input of any kind drives it:
 * pointer, touch and keyboard are irrelevant by construction, so there
 * is no coarse-pointer fallback to owe. It paints nothing and injects no
 * stylesheet — the engine owns every pixel (the nav-context-ink
 * no-paint precedent). It never carries an audio graph — the
 * one-audio-carrier-per-page law is untouched by this channel.
 * reduced-motion: the loop NEVER starts — every population is applied
 * ONCE at its t=0 pose and the scene stands as a composed still (the
 * celestial-dive register: a static composed frame of an inhabited
 * world). Decoration never overrides the visitor's calm signal.
 */
(function (global) {
  'use strict';

  var registry = [];

  var reduce = function () {
    return global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches;
  };

  // Deterministic per-agent variance — fract-sine hash, never Math.random.
  function hash01(seed, i, k) {
    var x = Math.sin(seed * 127.1 + i * 311.7 + k * 74.7) * 43758.5453123;
    return x - Math.floor(x);
  }
  function fract(x) { return x - Math.floor(x); }

  function buildPath(points) {
    var lens = [0], total = 0, i, a, b, dx, dy, dz;
    for (i = 0; i < points.length; i++) {
      a = points[i];
      b = points[(i + 1) % points.length];
      dx = b[0] - a[0]; dy = b[1] - a[1]; dz = (b[2] || 0) - (a[2] || 0);
      total += Math.sqrt(dx * dx + dy * dy + dz * dz);
      lens.push(total);
    }
    return { points: points, lens: lens, total: total || 1 };
  }

  // s in [0,1) → position + unit heading on the closed polyline.
  function samplePath(path, s, agent) {
    var target = s * path.total, i = 0;
    while (i < path.points.length - 1 && path.lens[i + 1] < target) i++;
    var a = path.points[i], b = path.points[(i + 1) % path.points.length];
    var seg = path.lens[i + 1] - path.lens[i] || 1;
    var f = (target - path.lens[i]) / seg;
    var dx = b[0] - a[0], dy = b[1] - a[1], dz = (b[2] || 0) - (a[2] || 0);
    var len = Math.sqrt(dx * dx + dy * dy + dz * dz) || 1;
    agent.x = a[0] + dx * f;
    agent.y = a[1] + dy * f;
    agent.z = (a[2] || 0) + dz * f;
    agent.hx = dx / len; agent.hy = dy / len; agent.hz = dz / len;
  }

  function poseAgent(pop, agent, t) {
    var i = agent.index, seed = pop.seed;
    if (pop.mode === 'path') {
      var rate = pop.speed * (1 + pop.jitter * (hash01(seed, i, 1) - 0.5) * 2);
      var s = fract(i / pop.count + hash01(seed, i, 2) * 0.5 / pop.count + t * rate / pop._path.total);
      samplePath(pop._path, s, agent);
    } else if (pop.mode === 'wander') {
      // Two incommensurate sines per axis — smooth bounded curls.
      var k, c, h, w1, w2, p1, p2, v, d;
      for (k = 0; k < 3; k++) {
        c = (pop._min[k] + pop._max[k]) / 2;
        h = (pop._max[k] - pop._min[k]) / 2;
        w1 = pop.speed * (0.11 + 0.13 * hash01(seed, i, 10 + k));
        w2 = w1 * (1.618 + 0.2 * hash01(seed, i, 20 + k));
        p1 = hash01(seed, i, 30 + k) * Math.PI * 2;
        p2 = hash01(seed, i, 40 + k) * Math.PI * 2;
        v = 0.62 * Math.sin(w1 * t + p1) + 0.38 * Math.sin(w2 * t + p2);
        d = 0.62 * w1 * Math.cos(w1 * t + p1) + 0.38 * w2 * Math.cos(w2 * t + p2);
        agent[k === 0 ? 'x' : k === 1 ? 'y' : 'z'] = c + h * v;
        agent[k === 0 ? 'hx' : k === 1 ? 'hy' : 'hz'] = d;
      }
      var hl = Math.sqrt(agent.hx * agent.hx + agent.hy * agent.hy + agent.hz * agent.hz) || 1;
      agent.hx /= hl; agent.hy /= hl; agent.hz /= hl;
      agent.phase = Math.sin(pop.speed * (6 + 4 * hash01(seed, i, 50)) * t + hash01(seed, i, 51) * Math.PI * 2);
    } else { // drift — flow + soft lateral sway, wrapping the bounds
      var k2, ext, base, sway, pos;
      for (k2 = 0; k2 < 3; k2++) {
        ext = pop._max[k2] - pop._min[k2];
        base = pop._min[k2] + hash01(seed, i, 60 + k2) * ext;
        sway = pop.dir[k2] === 0
          ? Math.sin(pop.speed * 0.4 * t + hash01(seed, i, 70 + k2) * Math.PI * 2) * ext * 0.04 * pop.jitter * 2
          : 0;
        pos = base + pop.dir[k2] * pop.speed * t * (1 + pop.jitter * (hash01(seed, i, 80 + k2) - 0.5)) + sway;
        if (ext > 0) pos = pop._min[k2] + fract((pos - pop._min[k2]) / ext) * ext;
        agent[k2 === 0 ? 'x' : k2 === 1 ? 'y' : 'z'] = pos;
      }
      var dl = Math.sqrt(pop.dir[0] * pop.dir[0] + pop.dir[1] * pop.dir[1] + pop.dir[2] * pop.dir[2]) || 1;
      agent.hx = pop.dir[0] / dl; agent.hy = pop.dir[1] / dl; agent.hz = pop.dir[2] / dl;
    }
  }

  function pose(inst, dt) {
    var p, pop, j;
    for (p = 0; p < inst.populations.length; p++) {
      pop = inst.populations[p];
      for (j = 0; j < pop.agents.length; j++) {
        poseAgent(pop, pop.agents[j], inst.t);
        pop.apply(pop.agents[j]);
      }
    }
    if (inst.onTick) inst.onTick(inst.t, dt);
  }

  function schedule(inst) {
    var want = inst.running && inst.visible && !document.hidden;
    if (want && !inst.rafId) {
      inst.lastT = 0;
      inst.rafId = requestAnimationFrame(inst.loop);
    } else if (!want && inst.rafId) {
      cancelAnimationFrame(inst.rafId);
      inst.rafId = 0;
    }
  }

  function init(root, opts) {
    opts = opts || {};
    var prior;
    for (var r = 0; r < registry.length; r++) if (registry[r].root === root) prior = registry[r];
    if (prior) prior.handle.destroy();

    var inst = {
      root: root,
      t: 0,
      rafId: 0,
      lastT: 0,
      running: false,
      visible: true,
      reduce: reduce(),
      onTick: typeof opts.onTick === 'function' ? opts.onTick : null,
      populations: [],
    };

    var src = opts.populations || [];
    for (var p = 0; p < src.length; p++) {
      var o = src[p];
      if (typeof o.apply !== 'function' || !(o.count > 0)) continue;
      var pop = {
        id: o.id || 'pop' + p,
        mode: o.mode === 'path' || o.mode === 'drift' ? o.mode : 'wander',
        count: o.count,
        speed: typeof o.speed === 'number' ? o.speed : 1,
        jitter: typeof o.jitter === 'number' ? o.jitter : 0.3,
        seed: typeof o.seed === 'number' ? o.seed : 1,
        dir: o.dir || [0, -1, 0],
        apply: o.apply,
        agents: [],
      };
      if (pop.mode === 'path') {
        if (!o.path || o.path.length < 2) continue;
        pop._path = buildPath(o.path);
      } else {
        var b = o.bounds || { min: [0, 0, 0], max: [1, 1, 0] };
        pop._min = [b.min[0], b.min[1], b.min[2] || 0];
        pop._max = [b.max[0], b.max[1], b.max[2] || 0];
      }
      for (var i = 0; i < pop.count; i++) {
        pop.agents.push({ id: pop.id, index: i, x: 0, y: 0, z: 0, hx: 0, hy: 0, hz: 0, phase: 0 });
      }
      inst.populations.push(pop);
    }

    inst.loop = function (now) {
      inst.rafId = requestAnimationFrame(inst.loop);
      var dt = inst.lastT ? Math.min(0.05, (now - inst.lastT) / 1000) : 0;
      inst.lastT = now;
      inst.t += dt;
      pose(inst, dt);
    };

    inst.onVis = function () { schedule(inst); };

    // reduced-motion: one composed still at the t=0 pose — the loop never starts.
    if (inst.reduce || !inst.populations.length) {
      pose(inst, 0);
    } else {
      inst.running = true;
      inst.io = new IntersectionObserver(function (entries) {
        inst.visible = entries[entries.length - 1].isIntersecting;
        schedule(inst);
      }, { threshold: 0 });
      inst.io.observe(root);
      document.addEventListener('visibilitychange', inst.onVis);
      pose(inst, 0);       // seed the world before the first frame lands
      schedule(inst);
    }

    inst.handle = {
      getState: function () {
        var pops = [];
        for (var p2 = 0; p2 < inst.populations.length; p2++) {
          var pp = inst.populations[p2], a0 = pp.agents[0];
          pops.push({ id: pp.id, count: pp.count, sample: { x: a0.x, y: a0.y, z: a0.z } });
        }
        return {
          running: inst.running,
          ticking: !!inst.rafId,
          visible: inst.visible,
          hidden: !!document.hidden,
          reduce: inst.reduce,
          t: inst.t,
          populations: pops,
        };
      },
      destroy: function () {
        inst.running = false;
        if (inst.rafId) { cancelAnimationFrame(inst.rafId); inst.rafId = 0; }
        if (inst.io) inst.io.disconnect();
        document.removeEventListener('visibilitychange', inst.onVis);
        for (var r2 = registry.length - 1; r2 >= 0; r2--) {
          if (registry[r2] === inst) registry.splice(r2, 1);
        }
      },
    };
    registry.push(inst);
    return inst.handle;
  }

  global.awardInSceneAmbientLife = { init: init };
})(typeof window !== 'undefined' ? window : this);
