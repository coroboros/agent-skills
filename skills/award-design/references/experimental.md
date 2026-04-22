# Experimental / Art-Directed

No template, no pattern. Each site is bespoke. Mixed media, creative coding, unconventional navigation.

## Typography

Anything goes — but with intent. Custom/bespoke typefaces, mixed media lettering, generative type. The choice must serve the project's unique concept.

## Color

Project-specific. No universal rules — but internally coherent within the project's own logic.

## Layout

Unconventional: spatial exploration, physics-based interfaces, "playground" navigation, non-linear storytelling.

**Critical warning**: Experimental navigation that requires discovery tanks usability scores (30% of Awwwards) even when creativity scores high. Every unconventional pattern needs a discoverable fallback.

## Animation & Creative Coding

This is the medium, not the decoration:

- **p5.js** for generative art and interactive sketches
- **Custom GLSL shaders** with noise functions and particle systems
- **Physics engines** (Matter.js, Cannon.js) for tangible interactions
- **3D Gaussian Splatting** for hyperreal environments (Luma AI + PlayCanvas SuperSplat)
- **AR face tracking** and spatial audio as interaction mechanisms

```javascript
// Physics-based navigation with Matter.js
const engine = Matter.Engine.create();
const menuItems = items.map(item => {
  const body = Matter.Bodies.rectangle(x, y, w, h, { restitution: 0.6 });
  Matter.World.add(engine.world, body);
  return { body, element: item };
});
Matter.Engine.run(engine);
// Sync DOM positions to physics bodies in rAF loop
```

## Technical approach

This archetype demands custom tooling. No framework templates it. Build from primitives. The consistently winning studios in this category have proprietary engines (Active Theory's Hydra, Resn's internal tools).

## Ideal for

Creative developer portfolios, art institutions, experimental campaigns, design festival sites.

## Reference

Bruno Simon's portfolio (Awwwards SOTM Jan 2026): browser-based 3D world navigated by driving a vehicle. Resn (Wellington): 60 SOTD wins, "gooey interactive experiences" with game design sensibilities and New Zealand humor.

## Submission strategy

**FWA rewards this archetype more aggressively** than Awwwards — 500+ jury members who value unconventional, experimental work. Submit experimental projects to FWA first, use wins as credibility for Awwwards.
