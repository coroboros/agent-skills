# Scroll-tied Volume Pattern

Extends the baseline gesture-unlock snippet in `SKILL.md` for cases where audio should track a visual transition — classically, a hero video that contracts out of view, with the audio fading and pausing in lockstep.

## Architecture

Volume is the product of independent factors so each control surface (entry fade-in, scroll fade, tab visibility, anything else) composes multiplicatively and nothing overrides anything else:

```
gain = TARGET × fadeInFactor × scrollVolumeFactor × …
```

- `fadeInFactor` — ramps `0→1` over the entry fade duration (rAF tick or a Web Audio linear ramp)
- `scrollVolumeFactor` — driven by the scroll handler, `0→1` mapped to "visible"
- Any additional factor — tab focus, a UI mute toggle, accessibility preference — is just another `0..1` number in the product

Each factor has its own lifetime and its own write path. `applyVolume()` recomputes the product whenever anything changes.

"Pause" at the threshold is `gain = 0` with the source still running — **not** `source.stop()`. The loop keeps ticking in the background. Scrolling back ramps the gain up and the listener hears audio continuously, with no resume glitch and no sample-level discontinuity. CPU cost of a running-but-muted `AudioBufferSourceNode` is negligible (one read per audio callback).

## Implementation

Extends the baseline snippet's `unlock()` — assumes `ctx`, `gain`, and `entered` are in scope from there:

```js
const TARGET = 0.6;
const FADE_MS = 700;
const SCROLL_THRESHOLD = 15;  // px deadband near the top

let fadeInFactor = 1;
let scrollVolumeFactor = 1;

function applyVolume() {
  if (gain) gain.gain.value = TARGET * fadeInFactor * scrollVolumeFactor;
}

function fadeInAudio() {
  fadeInFactor = 0;
  applyVolume();
  const start = performance.now();
  function tick(now) {
    fadeInFactor = Math.min(1, (now - start) / FADE_MS);
    applyVolume();
    if (fadeInFactor < 1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}

// `svh` is the scrollY at which the visual element (e.g. hero video) is
// fully out of view — derive from layout (e.g. viewport height, scroll
// spacer height) in your own code.
function onScroll(svh) {
  const y = window.scrollY;
  if (y <= SCROLL_THRESHOLD) {
    scrollVolumeFactor = 1;
  } else if (y < svh) {
    const progress = (y - SCROLL_THRESHOLD) / (svh - SCROLL_THRESHOLD);
    scrollVolumeFactor = 1 - progress;
  } else {
    scrollVolumeFactor = 0;
  }
  applyVolume();
}

window.addEventListener('scroll', () => onScroll(mySvhPx), { passive: true });
```

Call `fadeInAudio()` from the baseline `unlock()` instead of the inline `linearRampToValueAtTime` — `fadeInAudio` drives the factor, `applyVolume` combines it with whatever the scroll factor currently is, no overrides. Before unlock, `entered === false` means the scroll factor is still being updated but no sound is playing yet — the writes are harmless.

## Why multiplicative (and not additive, or last-writer-wins)

- **Additive** blows up when two factors are both 1 (`gain = 2` clips on any non-trivial source)
- **Last-writer-wins** lets fast scroll stomp the entry fade, or the fade stomp a mid-scroll read, producing audible jumps
- **Multiplicative**, each factor bounded `0..1`: product stays bounded at TARGET, new factors plug in without any coordination logic between them

## Pause vs stop

`source.stop()` is terminal on an `AudioBufferSourceNode` — the node can't restart. Resuming requires creating a new source with bookkeeping for `loopStart` / offset to avoid a click at the join. All of that is avoidable by running the source continuously and setting `gain = 0` when it should be inaudible. The CPU of a running-but-silent source is trivial, the resume path is free, and the sample-level continuity through the "pause" is preserved.

If you genuinely need to free the decoder (very long-running pages, memory pressure), stop the source and set a flag; the next unlock rebuilds from the cached `AudioBuffer`. For 99% of ambient-loop cases, don't.
