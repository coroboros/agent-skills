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

## The signature lives on the make-or-break surface

A bespoke mechanic buried below the fold does not save the build. The hero is the first impression and the largest single driver of the score (`SKILL.md` Phase 4); the signature belongs there. A page whose hero runs a *category* medium — a scrubbed stock clip, a parallax, a plain fade — while the one bespoke moment waits in section four is a category-hero build, and R1 scores it OFF-TRACK however good the buried moment is. Two ways out, both legitimate: the hero's own medium *is* the signature (the object turns in the hero, the material answers the pointer in the hero), or the signature is pulled up so the first screen carries it. "Foreshadow it above, pay it off below" is not the same as placing it below — the payoff itself must reach the make-or-break surface, not just a hint of it.

## The signature is distributed, over a live substrate

One climax is not the whole signature, and the page does not go quiet once it is spent. The shape the award record best supports is a **distributed signature over a live interaction substrate** (`interaction-signatures.md`): the dominant bespoke moment carries the make-or-break surface, and **two or three quieter section-tied echoes** recur down the scroll, over a low-amplitude substrate where *every* interactive element responds. The failure this rules out is the common one — a loud hero, then static editorial to the footer, every link and image inert. Neither "one hero moment then still" nor "one effect sustained unchanged everywhere" fit the record; the distributed model fit it best (verified on Cartier '365', a chaptered editorial winner — it transfers to a single-scroll page by inference, and what is proven-binding is the live substrate, never optional). Restraint lowers the substrate's **amplitude**, never its **coverage** — a quiet build still has everything respond, just barely. The signature is invented here; how it stays alive across the page is `interaction-signatures.md`.

## Deriving the mechanic — the world's verb

Do not pick from a menu; derive from the spine. Ask what the world invites the user to **do**, then build the interaction around that verb.

- A world of **objects** (a fragrance bottle, a watch, a sculpture) invites *turn / hold / examine* → a real-time 3D object the user rotates, light playing across it; light *is* the reveal, not a fade.
- A world of **space** (an atelier, a pavilion, a landscape) invites *move through* → a navigable scene, scroll or drag as travel.
- A world of **process** (a distillery, a kitchen, a press) invites *run it / watch it work* → a scrubbable sequence the user drives.
- A world of **material** (ink, glass, smoke, fabric) invites *disturb it* → a shader or physics field that answers the pointer.
- A **tool or product that does something** invites *use it* → a live tile that performs its own claim (the Bento winner's move).

**The verb classes — the routing table.** Every law that touches the signature routes by the verb's class, named here once: **scroll/scrub** (the page drives a sequence) · **hover/reveal** (approach discloses) · **drag/steer** (the pointer carries something) · **press/strike** (a discrete contact lands) · **turn/rotate** (a rigid object is manipulated) · **type/command** (input is the interface) · **ambient/no-input** (choreography carries it). The playable-object arbitration below fires on the physical-action classes (struck / driven / played / rotated); contact locality binds press/strike and material-disturb; the real-media-first rule governs scroll/scrub display; the substrate input law (`interaction-signatures.md`) binds press/strike only. A law applied outside its class is a category error — the walk that produced this table found drag-verb builds damaged by strike rules and turn-verb objects left unrouted.

The verb is in the spine already. If the spine is "the last light of the room," the verb is *reveal by light* — the signature is light-driven, not a scroll fade that happens to brighten. Name the verb explicitly in the Phase 1 artifact; a signature whose verb is "scroll" has not been derived.

**The primary verb, not the cleverest edge.** A world licenses several verbs; the signature takes the one the world is *built around* — its primary loop, the gesture a first-time stranger performs unprompted and reads as meaningful. Pinball is built around pulling the plunger and launching the ball; nudge-until-TILT is a connoisseur's edge, and a build that led with it left a real user asking what the mechanic was (the campaign's 6.9 UAT). Rank candidate verbs by stranger-legibility before novelty; an edge-verb signature takes a written justification naming why the primary verb was rejected — clever-over-legible without the writing is the same latitude hole as a category signature. R1 refutes it: state the world's primary verb yourself, then check the artifact chose it or justified the swap.

**The playable-object decision — written, arbitrated.** When the primary verb is a physical action on a world-object (a machine you play, a vehicle you drive, an instrument you strike, an object you turn), the interactive-object medium — a 3D scene, a scroll-scrubbed real sequence, canvas play — is considered FIRST, and the acceptance or rejection is written into the Phase 1 artifact citing one arbiter with evidence: the **premise veto** (would a real brand at this tier ship it, or is it theme-park cleverness), the **archetype's DNA** (the register governs the scene's aesthetic — a brutalist machine is raw and CRT-shaded, never a liquid-gloss render), or the **measured perf budget** (a scene hero still meets LCP < 1.5s via the poster-first path). A silent CSS-metaphor default is a skipped decision, not a choice. Displayed or scrubbed media are exempt — the real-media-first rule below governs those. **The arbitration is timestamped:** it lives in the DESIGN.md draft and is quoted verbatim in the pre-build R1 verdict — an arbitration first appearing at Phase 5 is a retroactive paste, not a decision (a build shipped exactly that: its report narrated a decision its artifact never carried); at Phase 6, Assessor B confirms the shipped code carries the arbitrated medium's fingerprint (a scene → a canvas/WebGL layer or `.glb`; scrubbed real media → the video and its scrub handler; bare CSS transforms under a scene arbitration mean the arbitration is fiction).

## Ambition is set before buildability — but fidelity governs the medium

Commit the signature's ambition (its *memorability*) at concept, then *source* what it needs — never trim the mechanic to what is easy. But ambition is not "always build 3D": the medium is chosen for **fidelity**, and a primitive-built object is *low* fidelity. When the signature is a real product — a bottle, a watch, a shoe — ask honestly before committing:

- **Can I get a premium 3D asset?** A modelled/DRACO `.glb`, or a form buildable to a convincing bar with a physical material and an HDRI environment (`ingredients/web3d-for-sites.md` fidelity floor). A lathe-turned primitive with a basic material reads as a Blender default — `imagery.md`'s silhouette test applies to 3D too: *a box-built object reads as placeholder at close range.*
- **If not, the real product is the higher-fidelity signature.** A **scroll-scrubbed real video** of the actual object (Apple-style, `immersive-cinematic.md`), or a hand-shot turntable photo-sequence, beats a primitive 3D every time — real light on real glass over a plastic-looking mesh. Not a fallback: for a real product with no premium 3D path, it is the *right* choice, and usually the more ambitious one.

The mechanic (the verb — turn, reveal) survives whichever medium; only the fidelity path changes. A signature downgraded to a safe *scroll-reveal* because the ambitious one was hard is a skipped gate — but so is a *primitive 3D shipped because it was the first idea*. R1 refutes both: the category signature, and the low-fidelity medium. A heavy layer routes through Phase 3 sourcing and the one WebGL delegation (`SKILL.md` Phase 4) — and it must clear that delegation's fidelity and input-correctness floors, not merely render.

**Contact locality — the paper-cutout law.** Where the verb *contacts* a surface, material, or object (press/strike, material-disturb — any archetype, any world), the response is **local to the contact point**, never a whole-element transform: the helmet dents where the glove lands, the bottle's light shifts where the finger rests, the shader field ripples from the touch — with **at least one secondary** (a propagation, a lag in what hangs from it, a cast shadow, a particle) and weight in the settle. A global sub-perceptible squash on the whole element is the **paper-cutout tell** — the dead hover of objects (a shipped build's `scale(1.055, 0.968)`, 140 ms, global: below the skill's own dead threshold, and its report called it physics). The reaction's *register* is archetype-governed, same clause as the delegation: a raw register's contact is hard, stepped, channel-split — never a default fleshy spring; a quiet register keeps the locality at minimal amplitude. Canvas-side deformation fidelity is Assessor-A driven judgment against this tell — no computed-style floor can see canvas pixels; what IS mechanical: a struck object whose only measured response is a uniform whole-element scale/opacity fails the detector's CONTACT-GLOBAL-SQUASH rule, and the ≥1 secondary is a driven count.

**Media routing by verb class** (one table, no averaging): contact-at-arbitrary-point (press/strike, disturb) → locally-reactive media first — a mesh-warped real photograph (the photo stays the texture; the mesh gives it flesh) or a 3D scene; scrubbed/displayed (scroll/scrub) → real-media-first, unchanged — the scroll-scrubbed real video beats the primitive; rigidly-turned (turn/rotate) → a premium 3D asset or a real turntable sequence. Rig recipes: `ingredients/web3d-for-sites.md`.

## The signature serves the identity, never the reverse

A mechanic that works only by compromising the brand's defining attribute is the wrong mechanic. NOIRE is *black*; a reveal that forces the glass amber so a warm core can transmit has let the mechanic overrule the identity — the flacon is no longer noire. When making the signature work bends the brand's core (a black brand gone brown, a minimal brand gone busy, a quiet brand gone loud), reconceive it so the signature *expresses* the identity instead: warm light **rakes the surface** of a black bottle and catches its edge, rather than transmitting through it — the reveal happens *on* the identity, not against it. R1 gate: name the brand's one non-negotiable attribute, then confirm the signature protects it. Concept over mechanic — the mechanic bends to the identity, never the reverse.

## The quiet pairing and the dignified still

The loud bespoke mechanic still pairs with one quiet second-read detail (`award-imperatives.md` #1) — noticed only on return, in palette and voice. Loud invention + quiet detail is the full pair; either alone is incomplete.

A pointer- or motion-driven signature needs a designed static state: `prefers-reduced-motion` and touch/no-pointer users get a composed still that still reads the world (the bottle lit from one side, the pavilion as one framed room), never a dead placeholder. The fallback is art-directed, not defaulted — and it is verified in the Phase 5 degraded and reduced-motion renders.
