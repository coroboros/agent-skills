# R2 Assessor A report — Undercurrent (evidence artifact for v3 analysis)

Provenance: the pixels-only R2 assessor spawned by the Undercurrent UAT build agent survived the parent's kill and completed independently (79 min, 245 browser tool uses). This is its full report, preserved verbatim as the existence proof that the desire-read judge instrument catches "ugly" when run isolated with live exemplar comparison. The operational failures were loop economics and builder convergence, NOT judge complacency: the builder's Phase 5 self-verdict said READY at 15:35; this independent assessor said LOSES 6.5/10; the builder edited the page mid-review (mtime 15:55) and rabbit-holed on AudioContext instead of converging on the P0s.

---

DESIRE-READ: LOSES Terminal Industries — "Terminal opens on a photograph you'd screenshot; this opens on a grey strip with a razor edge, hides its CTA below the fold, and then breaks its own spec table so badly the words print on top of each other. The argument underneath is better than Terminal's. The page is not."

Overall: 6.5/10 — Honorable Mention range (SOTD needs 7.5+). Concept 7 · Hierarchy 5 · Spacing 5 · Typography 8 · Color 6 · Motion 8 · A11y 6 · Anti-slop 7. Concept veto does not fire; the cap is execution, not idea.

## Key findings (full detail in the assessor's transcript)

**Aliveness: the build WINS the density read vs Terminal** — four scrubbed chapter instruments with genuinely distinct geometries, per-load computed work order, verified idle channels (pixel-diff), per-class hover palette all felt. Not the sparse-and-static failure.

**Where it loses: the fold and the finish.**

P0s:
1. `#hardware` spec list structurally broken at 1440 — DT collapsed to w:0 h:120, citation prints ON TOP of label text.
2. Three label-clipping failures — residue canvas slices "500–1500 Hz"; hardware SVG cuts trailing " m"; hero strip at 375 clips all five labels (`ΓRANSIENT`).
3. **No mobile navigation at all** — `.nav__links{display:none}` with no toggle/drawer; 4 sections unreachable across 11,577px of scroll.
4. `ch-pump → residue` seam hard-cuts (the one failing step of four), right before the climax; over-darkened scrim terminating on an edge.
5. Hero photo hard-cuts at its top edge (mask fades bottom only) AND primary CTA at y=963 — below a 900 fold, on a book-a-pilot page.
6. Hardware diagram is a 620px horizontal scroller inside 335px at mobile — undecodable, native scrollbars.

P1s: accent fires 3–5×/viewport against the spec's own one-per-viewport rule (blue means CTA + link + focus + emphasis + stats simultaneously); the signature instrument is irreversible (caption promises "press what you like"); chips lack `aria-pressed`; `.refusal` ships the 2px side-stripe anti-pattern verbatim.

**Copy: "the strongest copy I have reviewed on this brief type."** H1 "The street will not tell you. The pipe will." passes the category-headline test decisively; 346M m³/day is real and cited (Liemberger & Wyatt 2019); every number carries provenance; zero eyebrows/meta-labels/scroll-cues. Defects: "1 SOURCES" plural bug at the climax state; a footer build-note ("placeholders pending a commissioned shoot"); an unfilled bracket; trailing ellipses on placeholder names.

**Spec-vs-shipped contradictions caught by driving:** the declared contact-point chip press renders `transform: none` on all 23 sampled frames (spec fiction); declared procedural grain canvas is `display:none` everywhere while the shipped texture is the exact base64 PNG the spec bans.

**Nielsen 28/40** — killed by User Control 1/4 (irreversible signature), Recognition 1/4 (no mobile nav).

**Three gaps to Terminal:** (1) fold = photograph + CTA in bar vs strip + razor edge + buried CTA; (2) Terminal never ships text-on-text, this ships 3 clips + 1 collision — "precision instrument is the client's word, and broken type is the one thing that word cannot survive"; (3) Terminal's accent = one meaning once per viewport, this = three meanings five times.

**Method notes for the v3 judge design:** live URLs screenshotted beside the build (not description); placement ledger with six named defects per capture row; every response driven and measured, not read from CSS; computed-style sampling to catch spec fiction; per-load reload checks; touch emulation at 375; honest "did not verify" list (reduced-motion had no emulation surface). Cost: ~79 min, 245 tool uses, ~386k tokens for ONE assessor.
