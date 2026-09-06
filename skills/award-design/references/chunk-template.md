# Chunk template — the ladder's unit of work

A chunk is one executor run: award-design fills the form into the design_plan under `LADDER:`, frontend-dev implements it and writes Report back into the row. A calling process such as `/apex` or `/ultrapex` owns sequencing; an already authorized executor can run the self-contained prompt if the builder skill is unavailable. The final visual-review row returns to award-design's read-only review. The DESIGN.md is the grammar; a build chunk implements and verifies one slice of it. A DESIGN.md rule with no chunk that implements *and* verifies it does not exist.

Resolve `<skill root>` through the host's installed award-design entry and pass that location with the chunk. `references/`, `scripts/` and `assets/` below belong to that root, not the project or frontend-dev installation. If a referenced resource is unavailable, report the exact gap; never guess a sibling path or replace its evidence with a pass.

## The form

This form's Read first order is for build chunks. For the final review row, replace it with `references/gate/review.md` and the target URL: the fresh reviewer inventories the rendered pages before opening DESIGN.md, the direction contract, source comments or mechanical reports. It then reads those artifacts and runs the finish review. Make this order explicit in the generated row; do not prepend the build chunk's design reading to an independent review.

```markdown
### <id> — <title>                       # shell · hero · s1-<section> … · loader · nav · cursor · footer · transitions · sound · <page> · review

**Read first**
- `DESIGN.md` §<n> <section name> · §<n> …
- design_plan: the contract (THESIS · SIGNATURE) · beat table rows <a>–<b>
- `references/archetype/<name>.md` (tier 1) · `references/<name>.md` §<heading> (tier 2, this heading only)
- `references/skeletons.md` §<skeleton>            # when a technique is wired
- <corpus example path>                            # when one exists, from the tier-2 heading
- <stack-facts row>                                # when a version or support figure matters

**Implement**
1. <the surface, the mechanic by name, the trigger, the replay behavior>
2. <tokens used, by DESIGN.md name — never a new literal>
3. <what changes below 768px beyond stacking>
4. <reduced-motion branch · init/destroy · focus and keyboard path>

**Verify**                                        # <skill root> = the installed award-design folder
- `python3 <skill root>/scripts/preflight_scan.py <files> --archetype <archetype>` → 0 FAIL, every REVIEW judged; tick the `references/preflight.md` rows these files touch
- inject `<skill root>/assets/render-floor.js` through the browser rung (`references/external-truth.md`), sweep 375/768/1024/1440/1920 on <pages> → 0 FAIL · inject `<skill root>/assets/pixel-metrics.js` for the evidence pack the review reads · run `<skill root>/assets/detector.js` (`references/detector.md`) → 0 FAIL
- screenshots 1440 and 375 attached · LCP / CLS / INP measured with provenance on <page>
- <the one thing a human must see to accept this chunk>

**Out of scope**
- <the neighbouring surface this chunk must not touch>

**Report** (written into the ladder row when done)
- status: done | blocked — <reason> · deviations from Implement, each with its reason · gate outputs verbatim · open questions
```

The detector defaults to a 2-line hero H1. Only a client clause quoted in DESIGN.md can select `run({h1MaxLines: 3, h1OverrideReason: '<quoted clause and DESIGN.md reference>'})`; retain `H1-OVERRIDE` REVIEW in Report. More than 3 lines still fails. This is an explicit reported exception, not a pass against the canonical 2-line limit.

## Order and sizing

1. **shell** — tokens mirrored into the stack, motion infrastructure (smooth scroll, reduced-motion switch), nav and footer skeletons, the page host; copies the contract verbatim into the first build file's opening comment. Nothing visual beyond what every later chunk needs.
2. **hero** — 2–3 genuinely distinct directions built through one shared render frame; a fresh-context judge picks beside the archetype's live exemplar per `references/gate/hero.md` (isolation, the read, the verdict line). A candidate that looks more finished has broken the comparison, not won it. LOSES routes by its cause class — concept is handed back as a scope change and the director regenerates from R1, execution re-implements, craft goes to the optical pass (`references/optical-craft.md`) — never to polish. Only a hero that clears this earns the rest of the ladder.
3. **sections**, one chunk each, in page order — the intensity score from the design_plan decides which one carries the climax and which one rests.
4. **award surfaces** — loader, nav, cursor, footer moment, route transitions, sound: one chunk each, or a declared "out" with its reason in the ladder.
5. **pages** beyond the first, one chunk each, adopting the shell and the surfaces.
6. **review** — the last chunk ticks `references/preflight.md` whole (page-wide locks and verdict block), runs the code pass (`references/code-review.md`) and `references/gate/review.md`; its report is the verdict artifact and the ship label comes from it, never from the executor.

A chunk fits one run: if Implement passes six items or touches two surfaces, split it. A chunk never edits DESIGN.md or the contract — a needed change is a scope change reported back, and the director amends in writing before the next chunk. Rows run in order; a chunk names the rows it depends on when the order is not enough.
