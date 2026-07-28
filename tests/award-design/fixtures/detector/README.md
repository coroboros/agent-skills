# Detector fixtures

Two paired pages that pin `skills/award-design/assets/detector.js` verdicts: `dead/` embeds the substrate failures the detector exists to catch; `alive/` is the same page with every failure fixed. `test_detector_logic.py` parses both stylesheets (the `scale(1.02)` hover, the `-3px` lift) and feeds the literals to `classifyDelta` — keep them in sync with the expectations below.

## Manual harness

Serve the fixtures (a `file://` open works too — neither page ships JS, but a server matches the real audit path):

```
cd tests/award-design/fixtures/detector && python3 -m http.server 8123
```

Inject the detector at `http://localhost:8123/dead/` and `http://localhost:8123/alive/`:

- **Chrome DevTools MCP** — one `evaluate_script` whose function body is the full `detector.js` source followed by `return await awardDetector.run({ face: '<face below>' })`.
- **dev-browser** — page-eval the file source once, then eval `await window.awardDetector.run({ face: '<face below>' })`.

Faces: `dead/` commits to `"Marbre Display"` (deliberately nonexistent); `alive/` to `"Georgia"`.

## Expected verdicts — dead/

| Finding | Trigger |
|---|---|
| FONT-RESOLVE (FAIL) | `"Marbre Display"` never resolves — h1/h2 silently fall to system |
| NAV-BORDER (FAIL) | `1px solid #171310` under the `#fbf9f6` bar — contrasting line |
| HOMEOPATHIC (REVIEW, per link) | every `a:hover` is `scale(1.02)`, under the 1.04 floor |
| DEAD (REVIEW) | the `.cta` button has no state rule and the page ships no JS |
| SUBSTRATE-DEAD (FAIL) | zero measured elements classify OK |
| IDLE-CHANNEL (REVIEW) | no animation anywhere — nothing breathes at rest |

Silent by design: CONTRAST, H1-LINES, H-OVERFLOW, TAP-TARGET, IMG-BROKEN, UNMEASURED-JS, and TOKEN-CONFORM (the page declares zero color tokens, so the rule skips).

## Expected verdicts — alive/

Zero FAIL findings and an empty substrate deficit: every link and the button measure past the floors (ΔL ≈ 0.25 accent commit, 3px lift), the orb's 18s drift keeps IDLE-CHANNEL silent, the nav carries no border, and every computed color resolves to a `:root` token.

Environment caveats:

- FONT-RESOLVE passes where Georgia is installed (macOS, Windows); on a system without it the finding fires — environmental, not a fixture regression.
- Under `prefers-reduced-motion: reduce` emulation the orb stops **and** `run()` skips IDLE-CHANNEL — the guard working is the expected result, not a failure.
