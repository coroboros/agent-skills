# Web Audio for Sites

Add interactive or ambient audio to an award-winning marketing or portfolio site. You hold the project's `DESIGN.md` — express its committed universe as a **sound palette**: tone, material, register pulled from the brief, never generic stock sounds. A luxury watch site ticks; a playful brand pops; a brutalist site thuds. The sound is a glyph of the same world the visuals belong to.

Sound is the riskiest layer on a site — wrong by default, off by default. Earn every cue.

## When to load this

- The brief calls for UI micro-sounds (hover, toggle, send, success) or an ambient bed, and the archetype supports it — Immersive/Cinematic, Bold/Maximal, Experimental, some Spatial Organic and Editorial.
- The lead delegates the audio module to you with the `DESIGN.md` as the brief.
- Skip on Minimalist — and on Corporate Luxury default to silence, unless the brief asks or the universe earns it Cartier-style (a bespoke, consent-gated soundscape is that archetype's canonical exception).

## Library choice

| Need | Library | Why |
|------|---------|-----|
| UI micro-sounds (hover, click, toggle, send) | **Howler.js** | One audio sprite = one decode, one network request; sprite keys map to cues; cross-browser unlock and a global mute built in |
| Generative ambient bed (evolving pad, drone, texture) | **Tone.js** | Synthesizes the bed — no large loop file; `Tone.Loop` + transport drive slow evolution; per-node gain |
| Fixed ambient loop from a real recording (wind, room tone, vinyl crackle) | raw Web Audio — see `audio-loop` skill | Gapless `AudioBufferSourceNode{loop:true}`; that skill owns the encode + drop-in snippet |

Pick one per layer. Howler for discrete cues, Tone for a living bed; never both for the same sound.

## The unlock gate — resume on first gesture

Browsers start the audio context **suspended**. It resumes only inside a real user gesture (`pointerdown`, `keydown`, `click`) — `mousemove`, `scroll`, `wheel`, `pointermove` do not count. Never autoplay audio.

```javascript
// Howler — context is created lazily; first play() inside a gesture resumes it.
// A page-level one-time gesture primes it so the first hover cue isn't dropped.
import { Howler } from 'howler';
const prime = () => { if (Howler.ctx?.state !== 'running') Howler.ctx?.resume(); };
document.addEventListener('pointerdown', prime, { once: true, capture: true });
document.addEventListener('keydown', prime, { once: true, capture: true });
```

```javascript
// Tone — await Tone.start() inside the gesture before scheduling anything.
import * as Tone from 'tone';
async function startAmbient() {
  if (Tone.getContext().state !== 'running') await Tone.start();
  // build + start the bed here (see below)
}
soundToggle.addEventListener('click', startAmbient); // user opts in via the toggle
```

On reload the unlock repeats — a per-navigation browser constraint with no workaround short of the user granting the origin autoplay privilege.

## Sound-design discipline

- **Micro-sounds ≤ 0.3s**, low gain, felt not heard. A hover tick is 60–120ms; a send/success cue up to 300ms.
- **Ambient bed at 0.05–0.15 gain.** Above 0.2 it competes with the user's own music and reads as intrusive.
- **Off by default, opt-in.** No sound plays until the user enables it. The first gesture primes the context; it does not start the bed.
- **A persistent, visible mute/sound toggle is mandatory** — fixed corner, present on every view, reflecting current state.

```javascript
// Master mute — one line covers every Howler cue.
Howler.mute(isMuted);
// Ambient bed — ramp, don't cut, to avoid a click.
bedGain.gain.rampTo(isMuted ? 0 : 0.1, 0.4); // Tone.Gain node
```

## Accessibility and policy

- Never autoplay audio. Never convey information by sound alone — every cue pairs with a visible state change (the toggle flips, the field clears, the row highlights).
- Honor `prefers-reduced-motion: reduce` as a calm signal: keep sound **off**, and have the toggle default to muted.
- Give the toggle an accessible label that names the action and reflects state: `aria-label="Mute sound"` / `aria-label="Enable sound"`, `aria-pressed` tracking on/off.
- Respect the browser autoplay policy — the unlock gate above is how you comply, not a workaround around it.

```javascript
const calm = matchMedia('(prefers-reduced-motion: reduce)').matches;
let soundOn = false;            // off by default, always
if (calm) soundOn = false;      // calm preference keeps it off
```

## Performance

- **Lazy-load and decode after the gesture, not on page load.** Howler: `preload: false`, then `sound.load()` on opt-in. Tone synthesizes — nothing to download.
- **One sprite, one decode** for all UI cues — a single small file beats N requests and N decoders.
- **Keep total audio payload small** — UI sprite under ~60KB, ambient loop (if a real file via `audio-loop`) under ~300KB. A generative Tone bed adds zero bytes.
- Build perpetual Tone nodes once; reuse. Disposing and recreating per interaction leaks and stutters.

```javascript
const ui = new Howl({
  src: ['/audio/ui.webm', '/audio/ui.mp3'],   // webm first, mp3 fallback
  sprite: { hover: [0, 120], toggle: [200, 180], send: [500, 300] },
  preload: false,                              // decode on opt-in, not page load
  volume: 0.4,
});
// after the user enables sound:
ui.load();
ui.once('load', () => { /* cues ready: ui.play('hover') */ });
```

## Universe integration — the sound palette

Read the `DESIGN.md` and translate its world into sound the way you translated it into type and color. The cue is material, not a default click.

- **Tone / material** — a luxury watch ticks (short, dry, mechanical); a playful brand pops (round, bright, bouncy); a brutalist site thuds (low, blunt, no tail); an editorial site turns a page (soft paper friction); a spatial/organic site breathes (airy swell). Match the brief's adjectives.
- **Register** — pitch and brightness track the palette's energy. High-energy Bold/Maximal → brighter, faster cues; restrained Editorial → lower, slower, sparser.
- **Bed mood** — a Tone ambient bed carries the same atmosphere as the visuals: a warm low drone for a grounded brand, a shifting high pad for a futuristic one. Tie its harmony and motion to the Atmosphere Motion score.

```javascript
// Generative bed tuned to the DESIGN.md mood — built once, started on opt-in.
const bedGain = new Tone.Gain(0).toDestination();          // start silent, ramp up
const pad = new Tone.PolySynth(Tone.Synth, {
  oscillator: { type: 'sine' },                            // 'sine' warm · 'sawtooth' tense
  envelope: { attack: 4, release: 6 },                     // slow swell = calm; shorten for urgency
}).connect(bedGain);
new Tone.Loop((time) => {
  pad.triggerAttackRelease(['C2', 'G2', 'D3'], '2n', time); // chord = palette harmony
}, '2n').start(0);
Tone.getTransport().bpm.value = 40;                         // slow = ambient, not rhythmic
// on opt-in: Tone.getTransport().start(); bedGain.gain.rampTo(0.1, 2);
```

A default click on a watch site, or generic chimes on a brutalist one, is the audio equivalent of stock Tailwind — the exact failure this layer exists to avoid. The sound must read as found in this world, not bolted on.

## Cross-references

- `audio-loop` skill — gapless loop from a real recording (the third row above), with the canonical raw Web Audio gesture-unlock snippet.
- `../atmosphere-calibration.md` — the Motion score sets how present and active the bed should be.
- `../design-md-anatomy.md` — where the sound palette lives in the brief; record tone/material/register alongside motion.
- Audio failure modes pinned by this file: autoplay without a user gesture, stock cue packs, information carried by sound alone — each is stop-and-fix.
