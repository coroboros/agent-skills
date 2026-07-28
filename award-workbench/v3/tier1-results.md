# Tier-1 eval — concept convergence, measured 2026-07-28

Claim under test (BLUEPRINT §6, the roll's central premise): a model's own ranking converges on the same direction across framings; the floor-of-3 roll breaks that convergence.

## Method

One brief (Halden Frameworks — custom titanium bicycle frames, a premium-craft category that invites the workshop-ledger reflex) phrased 16 ways (formal, casual, terse, verbose, feature-led, emotion-led). Two arms × 16 runs, claude-sonnet, low effort, schema-forced output (direction one-line, 3 world keywords, palette family, display face):

- **OFF** — "commit to ONE design direction you would build."
- **ON** — steps 0–2 of the v3 skill only: read the room, write 5–7 SPINES, run `direction_roll.py` with a per-run seed, commit the assigned spine. The anchor (step 3) deliberately out of scope.

32/32 completed, 0 errors. Arms recovered from agent prompts; concept families counted by regex over the committed one-lines (`ledger|dossier|logbook|jig log|build ticket|notebook|measurement book`). Workflow run `wf_837f8870-a92`; raw rows in its journal.

## Result

| Family | OFF (n=16) | ON (n=16) |
|---|---|---|
| Workshop-ledger/dossier concept | **9** | **1** |
| Cold-steel palette | 14 | 15 |
| Grotesque display face | 12 | 8 |
| Serif display face | 1 | 6 |

The OFF arm is the measured argmax rut: a majority of independent runs committed the same site (cold-titanium workshop-ledger under a grotesque). The ON arm's sixteen committed directions are all distinct mechanics (a continuous tube drawing itself, a cross-polarized rotating frame in near-silence, a live geometry configurator, a bench-time build compression, a pavilion-glide engine world, a handwritten build log page-turning into the frame…).

**Palette is unchanged by design of the test** — palette variance is the anchor's axis (step 3, not run here), and this result isolates the two mechanisms cleanly: the roll moves the concept, the anchor moves the material. Measuring the anchor's arm is the natural next tier-1 extension.

## Limits

n=16 per arm, one brief, one model, one category; concept families counted by keyword regex (conservative for OFF — near-duplicates with different vocabulary count as distinct); ON-arm compliance not independently audited beyond the schema (SEED reproduction is spot-checkable from each run's printed key).

## Verdict

The roll's central claim survives its first falsification attempt on the axis it targets: dominant-concept share 9/16 → 1/16. Tier-2 (defect-rate on the L1 floor across full builds) remains the pre-ship gate.
