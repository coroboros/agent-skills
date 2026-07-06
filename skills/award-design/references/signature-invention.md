# Signature Invention

The signature interaction is the single strongest predictor of 8+ (`award-imperatives.md` #1), and it is where competent builds plateau: they ship a *category* — a scroll-driven reveal, a parallax, a magnetic button — instead of a mechanic invented for the brand's world. A category is safe, buildable, and forgettable; it sits unchanged on any rival's site in the archetype. This file forces the invention.

Load at Phase 1 (conceive the signature) and re-read at R1 (refute it).

## Category vs bespoke — the test

A **category** is a known move from the award vocabulary: scroll-reveal, clip-path wipe, kinetic SplitText, parallax, magnetic CTA, custom cursor, gradient sweep. Useful *texture* — never the signature.

A **bespoke signature** is a mechanic that could only belong to *this* world. The tell is the one-sentence description a stranger gives — it names the **verb**, not the mood:

- *the one where you **drive the car** across the portfolio* (Bruno Simon)
- *the one where you **move through the pavilion** to each timepiece* (Cartier WAW)
- *the one where the **filmstrip scrubs** the archive* (Siena)
- *the one where you **turn the bottle** and the light moves through the glass*

"The one with nice scroll reveals" is not a description; it is the absence of one.

**The bespoke test — binding at R1.** Could this exact interaction sit on a rival's site in the same archetype, unchanged? If yes, it is a category — regenerate it, never file it as a gap. A generic signature is a concept-stage failure with the same weight as a thin spine: the review scores it there and the total caps with it. Filing "no bespoke signature" as a known gap is the failure this file exists to stop.

## Deriving the mechanic — the world's verb

Do not pick from a menu; derive from the spine. Ask what the world invites the user to **do**, then build the interaction around that verb.

- A world of **objects** (a fragrance bottle, a watch, a sculpture) invites *turn / hold / examine* → a real-time 3D object the user rotates, light playing across it; light *is* the reveal, not a fade.
- A world of **space** (an atelier, a pavilion, a landscape) invites *move through* → a navigable scene, scroll or drag as travel.
- A world of **process** (a distillery, a kitchen, a press) invites *run it / watch it work* → a scrubbable sequence the user drives.
- A world of **material** (ink, glass, smoke, fabric) invites *disturb it* → a shader or physics field that answers the pointer.
- A **tool or product that does something** invites *use it* → a live tile that performs its own claim (the Bento winner's move).

The verb is in the spine already. If the spine is "the last light of the room," the verb is *reveal by light* — the signature is light-driven, not a scroll fade that happens to brighten. Name the verb explicitly in the Phase 1 artifact; a signature whose verb is "scroll" has not been derived.

## Ambition is set before buildability — but fidelity governs the medium

Commit the signature's ambition (its *memorability*) at concept, then *source* what it needs — never trim the mechanic to what is easy. But ambition is not "always build 3D": the medium is chosen for **fidelity**, and a primitive-built object is *low* fidelity. When the signature is a real product — a bottle, a watch, a shoe — ask honestly before committing:

- **Can I get a premium 3D asset?** A modelled/DRACO `.glb`, or a form buildable to a convincing bar with a physical material and an HDRI environment (`ingredients/web3d-for-sites.md` fidelity floor). A lathe-turned primitive with a basic material reads as a Blender default — `imagery.md`'s silhouette test applies to 3D too: *a box-built object reads as placeholder at close range.*
- **If not, the real product is the higher-fidelity signature.** A **scroll-scrubbed real video** of the actual object (Apple-style, `immersive-cinematic.md`), or a hand-shot turntable photo-sequence, beats a primitive 3D every time — real light on real glass over a plastic-looking mesh. Not a fallback: for a real product with no premium 3D path, it is the *right* choice, and usually the more ambitious one.

The mechanic (the verb — turn, reveal) survives whichever medium; only the fidelity path changes. A signature downgraded to a safe *scroll-reveal* because the ambitious one was hard is a skipped gate — but so is a *primitive 3D shipped because it was the first idea*. R1 refutes both: the category signature, and the low-fidelity medium. A heavy layer routes through Phase 3 sourcing and the one WebGL delegation (`SKILL.md` Phase 4) — and it must clear that delegation's fidelity and input-correctness floors, not merely render.

## The signature serves the identity, never the reverse

A mechanic that works only by compromising the brand's defining attribute is the wrong mechanic. NOIRE is *black*; a reveal that forces the glass amber so a warm core can transmit has let the mechanic overrule the identity — the flacon is no longer noire. When making the signature work bends the brand's core (a black brand gone brown, a minimal brand gone busy, a quiet brand gone loud), reconceive it so the signature *expresses* the identity instead: warm light **rakes the surface** of a black bottle and catches its edge, rather than transmitting through it — the reveal happens *on* the identity, not against it. R1 gate: name the brand's one non-negotiable attribute, then confirm the signature protects it. Concept over mechanic — the mechanic bends to the identity, never the reverse.

## The quiet pairing and the dignified still

The loud bespoke mechanic still pairs with one quiet second-read detail (`award-imperatives.md` #1) — noticed only on return, in palette and voice. Loud invention + quiet detail is the full pair; either alone is incomplete.

A pointer- or motion-driven signature needs a designed static state: `prefers-reduced-motion` and touch/no-pointer users get a composed still that still reads the world (the bottle lit from one side, the pavilion as one framed room), never a dead placeholder. The fallback is art-directed, not defaulted — and it is verified in the Phase 5 degraded and reduced-motion renders.
