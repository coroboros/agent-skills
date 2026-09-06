const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const [caseName, references] = process.argv.slice(2);

function code(file, heading, marker = '') {
  const source = fs.readFileSync(path.join(references, file), 'utf8');
  const section = source.split(heading)[1].split(/^## /m)[0];
  const blocks = [...section.matchAll(/```(?:javascript|js|tsx)\n([\s\S]*?)```/g)];
  const block = blocks.find(match => match[1].includes(marker));
  assert.ok(block, `Missing executable recipe: ${file} ${heading}`);
  return block[1].replace(/^import .*$/gm, '').replace(/export /g, '');
}

function events(target = {}) {
  const listeners = new Map();
  target.addEventListener = (type, callback) => listeners.set(type, callback);
  target.removeEventListener = (type, callback) => {
    if (listeners.get(type) === callback) listeners.delete(type);
  };
  target.fire = (type, event = {}) => listeners.get(type)?.(event);
  target.listenerCount = () => listeners.size;
  return target;
}

function context(extra) {
  return vm.createContext({ console: { error() {} }, ...extra });
}

function reveal() {
  const source = code('skeletons.md', '## G. Fire-once IO reveal', 'initReveals');
  function element(top) {
    const attributes = new Set();
    return { attributes, getBoundingClientRect: () => ({ top }),
      setAttribute: name => attributes.add(name), removeAttribute: name => attributes.delete(name) };
  }
  for (const failure of ['none', 'construct', 'observe', 'update', 'reduced']) {
    const visible = element(100), below = element(1200), next = element(1600);
    const elements = [visible, below, next];
    const motion = events({ matches: failure === 'reduced' });
    let callback, disconnects = 0, observations = 0;
    const env = context({ innerHeight: 800, matchMedia: () => motion,
      document: { querySelectorAll: () => elements },
      IntersectionObserver: class {
        constructor(cb) { if (failure === 'construct') throw Error('unavailable'); callback = cb; }
        observe() { if (++observations === 2 && failure === 'observe') throw Error('register failed'); }
        unobserve() { if (failure === 'update') throw Error('update failed'); }
        disconnect() { disconnects++; }
      },
    });
    vm.runInContext(source, env);
    const destroy = env.initReveals();
    assert.ok(visible.attributes.has('data-shown'), failure);
    assert.ok(!visible.attributes.has('data-reveal-ready'), failure);
    if (failure === 'none' || failure === 'update') {
      assert.ok(below.attributes.has('data-reveal-ready'));
      callback([{ target: below, isIntersecting: true }]);
      assert.ok(below.attributes.has('data-shown'));
    }
    if (failure === 'none') {
      motion.matches = true;
      motion.fire('change');
    }
    for (const el of elements) {
      assert.ok(el.attributes.has('data-shown'), failure);
      assert.ok(!el.attributes.has('data-reveal-ready'), failure);
    }
    destroy();
    assert.equal(motion.listenerCount(), 0);
    if (failure !== 'reduced' && failure !== 'construct') assert.ok(disconnects > 0);
  }
}

function split() {
  const source = code('skeletons.md', '## D. SplitText', 'initHeadlineReveal');
  for (const reduced of [true, false]) {
    let splits = 0, tweens = 0, restores = 0, onPreferenceChange;
    const env = context({
      gsap: {
        registerPlugin() {}, from() { tweens++; return {}; },
        matchMedia() { return {
          add(query, setup) {
            assert.equal(query, '(prefers-reduced-motion: no-preference)');
            if (!reduced) onPreferenceChange = setup();
          },
          revert() { if (onPreferenceChange) onPreferenceChange(); },
        }; },
      }, ScrollTrigger: {},
      SplitText: { create(_, options) {
        splits++; options.onSplit({ words: [{}] });
        return { revert() { restores++; } };
      } },
    });
    vm.runInContext(source, env);
    const destroy = env.initHeadlineReveal({});
    assert.equal(splits, reduced ? 0 : 1);
    assert.equal(tweens, reduced ? 0 : 1);
    if (!reduced) { onPreferenceChange(); onPreferenceChange = null; }
    destroy();
    assert.equal(restores, reduced ? 0 : 1);
  }
}

async function three() {
  const source = code('skeletons.md', '## E. Three.js scene', 'initScene');
  for (const failure of ['none', 'init', 'render', 'reduced']) {
    let renders = 0, loop = null, observer;
    const disposed = { renderer: 0, geometry: 0, material: 0 };
    const motion = events({ matches: failure === 'reduced' });
    const document = events({ visibilityState: 'visible' });
    const host = events();
    class Renderer {
      init() { return failure === 'init' ? Promise.reject(Error('backend')) : Promise.resolve(); }
      setPixelRatio() {} setSize() {}
      render() { if (failure === 'render') throw Error('render failed'); renders++; }
      setAnimationLoop(callback) { loop = callback; }
      dispose() { disposed.renderer++; }
    }
    const env = context({ ...host, document, devicePixelRatio: 2, matchMedia: () => motion,
      IntersectionObserver: class { constructor(callback) { observer = callback; } observe() {} disconnect() {} },
      THREE: { WebGPURenderer: Renderer, Scene: class { add() {} },
        PerspectiveCamera: class { constructor() { this.position = {}; } updateProjectionMatrix() {} },
        Mesh: class {}, DirectionalLight: class {},
        IcosahedronGeometry: class { dispose() { disposed.geometry++; } },
        MeshStandardNodeMaterial: class { dispose() { disposed.material++; } },
      },
    });
    vm.runInContext(source, env);
    const poster = { dataset: {} };
    const rig = await env.initScene({ clientWidth: 600, clientHeight: 400 }, { poster });
    assert.ok(!Object.hasOwn(poster.dataset, 'sceneReady'));
    assert.equal(renders, 0);
    if (failure === 'none' || failure === 'render') {
      observer([{ isIntersecting: true }]);
      assert.equal(typeof loop, 'function');
      loop();
      assert.equal(Object.hasOwn(poster.dataset, 'sceneReady'), failure === 'none');
      if (failure === 'none') {
        observer([{ isIntersecting: false }]);
        assert.equal(loop, null);
        document.visibilityState = 'hidden'; document.fire('visibilitychange');
        document.visibilityState = 'visible'; document.fire('visibilitychange');
        assert.equal(loop, null, 'tab return must not restart an offscreen scene');
        observer([{ isIntersecting: true }]);
        assert.equal(typeof loop, 'function');
        motion.matches = true; motion.fire('change');
        assert.equal(loop, null);
        assert.ok(!Object.hasOwn(poster.dataset, 'sceneReady'));
      } else assert.equal(loop, null);
    }
    rig.destroy();
    assert.equal(document.listenerCount(), 0);
    assert.equal(motion.listenerCount(), 0);
    assert.deepEqual(disposed, failure === 'reduced'
      ? { renderer: 0, geometry: 0, material: 0 }
      : failure === 'init' ? { renderer: 1, geometry: 0, material: 0 }
      : { renderer: 1, geometry: 1, material: 1 });
  }
}

function fiber() {
  const source = code('ingredients/web3d-for-sites.md', '## Performance discipline', 'SceneActivity');
  for (const reduced of [false, true]) {
    let observer, mode = 'always', invalidations = 0;
    const document = events({ hidden: false });
    const cleanups = [];
    const env = context({ document,
      useState: () => [reduced, () => {}], useEffect: callback => cleanups.push(callback()),
      matchMedia: () => events({ matches: reduced }),
      useThree: () => ({ gl: { domElement: {} }, get: () => ({ frameloop: mode }),
        setFrameloop: value => { mode = value; }, invalidate: () => invalidations++ }),
      IntersectionObserver: class { constructor(callback) { observer = callback; } observe() {} disconnect() {} },
    });
    vm.runInContext(source, env);
    env.SceneActivity();
    assert.equal(mode, 'never');
    observer([{ isIntersecting: true }]);
    assert.equal(mode, reduced ? 'demand' : 'always');
    assert.ok(invalidations > 0);
    observer([{ isIntersecting: false }]);
    document.hidden = true; document.fire('visibilitychange');
    document.hidden = false; document.fire('visibilitychange');
    assert.equal(mode, 'never');
    cleanups.reverse().forEach(cleanup => cleanup());
    assert.equal(mode, 'always');
    assert.equal(document.listenerCount(), 0);
  }
}

function cinematic() {
  const source = code('production-hardening.md', '## Scroll-driven cinematic sequences', 'initCinematicScroll');
  for (const interruption of ['wheel', 'keydown', 'pointerdown', 'reduced']) {
    let now = 1, sequence = 0, writes = 0;
    const pending = new Map(), frames = new Map(), host = events(), motion = events({ matches: false });
    const env = context({ ...host, scrollY: 0, matchMedia: () => motion, performance: { now: () => now },
      setTimeout: callback => { const id = ++sequence; pending.set(id, callback); return id; },
      clearTimeout: id => pending.delete(id),
      requestAnimationFrame: callback => { const id = ++sequence; frames.set(id, callback); return id; },
      cancelAnimationFrame: id => frames.delete(id),
      window: { scrollTo({ top }) { writes++; env.scrollY = top; host.fire('scroll'); } },
    });
    vm.runInContext(source, env);
    const rig = env.initCinematicScroll({ threshold: () => 100, target: () => 1000, duration: 1000, ease: t => t });
    env.scrollY = 120; host.fire('scroll');
    assert.equal(pending.size, 0, 'scripted crossing alone must not start a glide');
    env.scrollY = 0; host.fire('scroll');
    host.fire('wheel', { type: 'wheel', isTrusted: false, deltaY: 20 });
    env.scrollY = 120; host.fire('scroll');
    assert.equal(pending.size, 0, 'synthetic input must not authorize a glide');
    env.scrollY = 0; host.fire('scroll');
    host.fire('wheel', { type: 'wheel', isTrusted: true, deltaY: 20 });
    env.scrollY = 120; host.fire('scroll');
    assert.equal(pending.size, 1);
    host.fire('wheel', { type: 'wheel', isTrusted: true, deltaY: 20 });
    assert.equal(pending.size, 1, 'the initiating wheel burst settles before animation');
    const start = [...pending.values()][0]; pending.clear(); now = 201; start();
    const tick = [...frames.values()][0]; frames.clear(); now = 401; tick(now);
    assert.equal(writes, 1);
    assert.equal(frames.size, 1);
    if (interruption === 'reduced') { motion.matches = true; motion.fire('change'); }
    else host.fire(interruption, { type: interruption, isTrusted: true, deltaY: -20, key: 'ArrowUp', clientY: 0 });
    assert.equal(frames.size, 0, interruption);
    rig.cancel();
    rig.destroy();
    assert.equal(host.listenerCount(), 0);
    assert.equal(motion.listenerCount(), 0);
    assert.equal(pending.size, 0);
  }
}

Promise.resolve(({ reveal, split, three, fiber, cinematic })[caseName]()).catch(error => {
  console.error(error);
  process.exitCode = 1;
});
