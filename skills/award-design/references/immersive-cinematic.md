# Immersive / Cinematic

Full-screen video heroes, WebGL 3D environments, dark backgrounds that make colors pop. Scroll as narrative.

## Typography

**Headlines**: Monument Grotesk (XXL), GT Flexa, Sharp Grotesk — 80-200px, weight 700-900
**Body**: Minimal — this archetype communicates visually, text is secondary
**Treatment**: Overlaid on 3D/video with `mix-blend-mode`, glow via `text-shadow`

## Color

| Role | Values |
|------|--------|
| Background | Pitch dark: #0A0A0A to #1A1A2E |
| Text | Off-white #E0E0E0, selective glow effects |
| Accents | Vivid against dark: neon, vibrant brand colors |
| Effects | Radial gradients, bloom, lens flares via shaders |

## Layout

Full-viewport sections. Pinned scroll sequences. Minimal visible UI — content reveals through scroll progression.

## Animation

Scroll-controlled storytelling is the core:

```javascript
// Scroll-controlled video scrubbing
const video = document.querySelector('video');
gsap.to(video, {
  currentTime: video.duration,
  scrollTrigger: {
    trigger: '.video-section',
    start: 'top top', end: 'bottom bottom',
    scrub: 1, pin: true
  }
});
```

**WebGL**: Three.js for 3D scenes. WebGPU (r171+) for high-performance rendering. Custom GLSL shaders for post-processing (bloom, color grading, vignette). Common effects: image hover distortion via vertex displacement, particle systems, noise-based transitions.

**Sound**: Optional but differentiating. Howler.js for audio management, micro-interaction sounds < 0.3s, ambient at 0.05-0.15 volume. Require user consent via splash page ("Enter with Sound" / "Enter without Sound") or persistent mute toggle. Format: WebM/Opus (smallest), MP3 fallback.

## Performance

Critical for this archetype — heavy visuals must still load fast:

- Lazy-load videos via `requestIdleCallback`
- Draco-compress 3D meshes
- Target LCP ~1.3s despite shaders (Active Theory achieves this)
- `content-visibility: auto` on non-visible sections
- Progressive quality: start low-poly, enhance as assets load
- Video: all HTML attrs (`autoplay muted loop playsinline webkit-playsinline disableRemotePlayback preload="auto" poster="…"`), **MP4 source before WebM** (Safari only plays MP4 and picks the first supported source), `object-fit: cover`, under 15s, compressed below 5MB via `ffmpeg -crf 28 -preset slow`
- JS belt-and-suspenders: re-assert `video.muted = true` from script and call `play()` explicitly with `.catch(() => {})` — iOS honors HTML `autoplay` unreliably in low-power states
- `prefers-reduced-motion`: swap to static poster images

For the full production checklist (viewport units, scroll-restoration, threshold-crossing discipline, fail-safe reveal logic, real-device test workflow), see `production-hardening.md`. Most rules there are cross-browser; iOS Safari is the sharpest test case but not the only target.

## Ideal for

Automotive (Porsche), luxury brands, entertainment/film, gaming, museums, product launches.

## Reference studios

Active Theory (LA + Amsterdam) — Emmy-nominated, proprietary Hydra 3D engine, pitch-black canvases with XXL Monument Grotesk. Immersive Garden (Paris) — Awwwards Agency of Year 2025, Louis Vuitton Collectibles.
