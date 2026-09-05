# R2 — the finish review and the verdict

The one instrument that judges quality. It runs once, late, on the rendered site, after the mechanical layers are clean — a judge run over a broken page returns unusable signal on everything else. Its report is the verdict artifact: the builder never writes READY, and no chunk emits a ship status before this review returns.

## Isolation and discipline

- The reviewer is a fresh-context subagent, read-only by tool grant where the harness allows (no Write, no Edit). Parallel reviewers never share a browser session.
- **Inventory before anchoring.** The reviewer describes the rendered page in its own words — sections, media, what moves — before reading the direction contract, the DESIGN.md, or any mechanical report (the scanner, render-floor, detector, and the pixel-metrics evidence pack). The contract is the builder's abstraction; a review anchored on it inherits whatever that abstraction dropped.
- **Turn budget.** A review built from what you saw beats a perfect review that never arrives: by roughly the tenth turn stop reading and write, naming whatever went unread.
- **Tree hash.** Record the build tree's hash at review start. Any edit during the review voids the audit; any post-verdict edit re-runs the render-floor sweep and the touched surface's checks before the verdict stands again.

## The review pass

1. **Open with the comparative desire read** — the live exemplar (tier-1 names it) and the category's recent award winners, screenshotted beside the build where a browser rung exists. First emitted line, verbatim format, never softened, travels into the ship report:
   `DESIRE-READ: BEATS|LOSES <exemplar> — "<raw phrase>" — cause: concept|execution|craft`
   The cause class routes the remedy: `concept` → regenerate at R1 · `execution` → the ranked fix list below · `craft` → the optical pass. A LOSES read is driven evidence; it outranks every clean mechanical report.
2. **The density read follows the selected archetype and register:** compare its committed medium and motion craft with the relevant exemplar. A reading register may be static; a declared live scene must sustain its medium; a brutalist arc may defer spectacle to the footer. Judge missing declared choreography or a generic substitute as a `concept` cause, never enforce another register's channel count.
3. **Drive, don't read.** Test the signature's declared behavior as a real user: for a draggable object, mouse and touch drag must respond without drag-ghost or text selection; for a static signature, inspect its composition and legibility. Judge execution quality, not just operation: a 60fps primitive that reads CGI fails. Then check the contract's SIGNATURE promise-by-promise with the applicable rendered evidence (a declared transform beat rendering `transform: none` is spec fiction — a finding, whatever the code claims), every claimed echo and mobile performance at 375 emulated.
4. **Placement beside the exemplar frame,** hunting crowding, baseline drift, orphan labels, text-over-image contrast, dead zones — each verdict a measurement in the frame.
5. **Close with the three gaps** to the exemplar, each stated as a deficit against the brief's own world — a gap that restates the exemplar's device is inadmissible and generates no fix item.

Output: ordered `material_fixes` (max 8, severity-ranked, fidelity before craft), a `keep` list, the desire read. No praise, no summary prose.

## The fix loop — bounded

The reviewer's findings are the only list the builder works from — never its own re-opened hunt. Fixes apply in one batch; re-render; the same reviewer scores each finding `resolved | partial | unresolved` — positions moved but the quality the finding named still absent is partial at best. At most one more batch and recapture; **the second verdict ends work whatever it says.** A finding is dismissed only with a measurement, never a second glance.

## The ship label — every harness terminates

- Subagents present → **READY** is writable only by the synthesis of the reviewer's return. The final verdict table reaches the user as it stands, open items included.
- No subagents, human present → the human gate is the independent return: show the side-by-side, ask "would a jury pick this over <exemplar>?" — READY requires the yes.
- Headless single-context → terminal label **REVIEWED-SAME-CONTEXT — verdict not independent**. Never READY. The run completes; the label carries the deficiency.
- No browser rung at all → the driven checks go dark as declared gaps and the label caps at REVIEWED-SAME-CONTEXT; a build whose committed signature is interactive, or any immersive-cinematic or experimental build, caps at **NOT DONE — unverified render**.

Presenting mechanical confirmation as artistic success is how a failed build gets announced as a finished one. Report the verdict as it stands.

## Standalone review — `award-design review <url|path>`

Use this mode for a requested audit without the current build's contract and ladder. A final ladder row supplies those artifacts and uses the finish review above, including SIGNATURE checks, the bounded builder fix loop and verdict; the reviewer itself remains read-only. An explicitly standalone audit stays an audit even when the target has design files.

Without a build contract, derive the archetype from the site and brief, record a tree hash if source is available, and omit contract-dependent SIGNATURE checks, the fix loop and ship label. Everything else runs as written — inventory first, the desire read beside the archetype's exemplar and the category's recent winners, the density read, the drive, the placement pass and the three gaps. Score with `references/audit-rubric.md` (the concept veto included) and run the scanner second, anti-anchoring. Output DESIRE-READ, scores and ordered findings without a ship label.

After the verdict, production plumbing is offered per brief — the `ship-ready-floor.md` Offer tier, surfaced by name and never auto-built. It is the user's call, and it ranks below the signature it plumbs.
