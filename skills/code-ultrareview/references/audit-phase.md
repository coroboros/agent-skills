# Audit phase — brief, schema, weights

Read this before dispatching the audit subagent. It pins the Haiku brief, the
signal schema emitted by `scripts/audit_signals.py`, and the weight table
consumed by `scripts/tier_router.py`. SKILL.md keeps the audit phase under
25 lines on purpose — every detail expands here.

## Subagent dispatch

One `Explore` subagent, model `haiku`, runs the audit. Cost target: ~$0.005
per run (Haiku rate × ~30k input tokens). Skip when `-t` is set to an explicit
tier (`standard`/`deep`/`ultra`) — the router is bypassed and the chosen tier
is surfaced as `rationale: "explicit override via -t"`.

The subagent's job is mechanical: shell out to `audit_signals.py` and pipe the
result into `tier_router.py`. No reasoning, no synthesis — the scripts are
deterministic.

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/audit_signals.py" \
  --base "<base>" --target "<target>" --json \
| python3 "${CLAUDE_SKILL_DIR}/scripts/tier_router.py"
```

The audit phase runs in ~30–60s on a 1000-LOC diff (subprocess overhead +
file reads; no network).

## Signal schema (audit_signals.py output)

```json
{
  "loc_changed": 142,
  "files_touched": 4,
  "files_touched_list": ["src/a.ts", "src/b.ts", "tests/c.test.ts", "README.md"],
  "public_api_touched": true,
  "normative_spec_mentioned": false,
  "normative_specs_list": [],
  "manifest_graph_delta": true,
  "pre_1_0_or_freeze": false,
  "test_coverage_delta": 0.45,
  "security_sensitive_paths": false
}
```

| Signal | Type | Extractor |
|--------|------|-----------|
| `loc_changed` | int | Sum of `--numstat` added + deleted across all files |
| `files_touched` | int | Count of files in `--numstat` |
| `files_touched_list` | list[str] | Paths from `--numstat` (preserves order) |
| `public_api_touched` | bool | Root-level `*.md`, `SKILL.md`, `marketplace.json`, route paths, top-level `+export ` lines in the diff |
| `normative_spec_mentioned` | bool | Regex `\b(RFC\s?\d+\|WHATWG\|ISO/IEC\s?\d+\|OpenAPI\|IETF)\b` against diff content + repo `README.md` + repo `CLAUDE.md` |
| `normative_specs_list` | list[str] | Sorted unique matches from the regex above |
| `manifest_graph_delta` | bool | Any of `package.json`, `marketplace.json`, `README.md`, `SKILL.md` in `files_touched_list` |
| `pre_1_0_or_freeze` | bool | `version` in `package.json` or `metadata.version` in `marketplace.json` starts with `0.`; OR recent 20 commit subjects match `\b(freeze\|rc\d*\|beta\d*)\b` |
| `test_coverage_delta` | float | (added test LOC) / (added code LOC); `0.0` when no code added (collapsed semantics — see *Caveats*) |
| `security_sensitive_paths` | bool | Any `files_touched_list` path matches `(auth\|crypto\|secret\|password\|token\|jwt\|oauth\|tls\|ssl)` (case-insensitive) |

Test-path detection (used by `test_coverage_delta`): suffix in
`(.test.ts, .test.js, .test.tsx, .spec.ts, .spec.js)`; OR directory contains
`/tests/`/`/test/`; OR filename starts with `test_` (Python convention) or
contains `_test.` (Go convention).

## Weight table (tier_router.py)

| Signal | Weight | Normalization |
|--------|--------|---------------|
| `loc_changed` | 0.20 | `min(1.0, loc / 500)` — saturates at 500 LOC |
| `files_touched` | 0.10 | `min(1.0, files / 20)` — saturates at 20 files |
| `public_api_touched` | 0.20 | 1.0 if true else 0.0 |
| `normative_spec_mentioned` | 0.20 | 1.0 if true else 0.0 |
| `manifest_graph_delta` | 0.10 | 1.0 if true else 0.0 |
| `pre_1_0_or_freeze` | 0.05 | 1.0 if true else 0.0 |
| `test_coverage_delta` | 0.10 | `max(0.0, 1.0 - min(1.0, ratio))` — invert: 0 ratio = max gap, ≥1.0 ratio = no gap |
| `security_sensitive_paths` | 0.05 | 1.0 if true else 0.0 |

Sum of weights = 1.00.

## Tier thresholds

| Tier | Score range | Token budget |
|------|-------------|--------------|
| `standard` | `< 0.35` | 50,000 |
| `deep` | `0.35 ≤ score < 0.70` | 150,000 |
| `ultra` | `≥ 0.70` | 400,000 |

Boundaries are half-open: 0.35 belongs to `deep`, 0.70 belongs to `ultra`.

## Rationale format

```
Tier: <tier> (score <0.XX>)

Signal contributions (weight × value):
  - loc_changed: 0.20 × 0.40 = 0.080
  - public_api_touched: 0.20 × 1.00 = 0.200
  - manifest_graph_delta: 0.10 × 1.00 = 0.100
  - test_coverage_delta: 0.10 × 0.70 = 0.070

Thresholds: standard < 0.35, deep < 0.70, ultra ≥ 0.70
```

Zero-valued signals are omitted to keep the rationale tight. When every
signal is at zero, the line `(none — all signals at zero)` appears instead.

The router emits the rationale verbatim into the report header — never
paraphrased. Lens subagents read it to know which tier they are running in.

## Ultra-tier confirmation gate

Ultra is the most expensive tier (~400k tokens; build + execute pass +
property-fuzz). The gate fires before lens dispatch when:

- `tier == "ultra"` (router-chosen or `-t ultra`)
- `--apply-safe` is NOT set
- `-y` (yes-to-all) is NOT set

Either bypass — `--apply-safe` (user explicitly opted into write semantics)
or `-y` — proceeds without prompting. The prompt prints the rationale + token
estimate and reads `y`/`yes` from stdin.

Implementation: `tier_router.confirm_ultra(tier, rationale, estimated_tokens,
apply_safe, yes)` returns `True`/`False`. The script's `--gate` mode wraps it
for shell invocation (exit 0 = proceed, exit 2 = abort).

## Override paths

- `-t auto` (default) — run the audit, route automatically.
- `-t standard`/`-t deep`/`-t ultra` — skip the audit, force the tier.
- `-y` — skip the Ultra confirmation prompt.
- `--apply-safe` — implies `-t ultra` if not set; bypasses the confirmation.

Audit signals are still computed and surfaced in the report header even when
the tier is overridden — readers see the diff's signal profile alongside the
forced tier.

## Caveats

- `test_coverage_delta = 0.0` collapses two cases: "code added with no tests"
  (max gap) and "no code added at all" (irrelevant). When `loc_changed` is
  also near zero, the test-gap contribution is mostly noise — accepted at MVP
  because the false signal stays within Standard tier (≤0.10 contribution).
- The `public_api_touched` heuristic is intentionally loose. A `route.ts`
  file in `node_modules/` would flag — but `node_modules/` shouldn't be in
  the diff. If it is, treat the audit output as advisory and override.
- `normative_spec_mentioned` matches any `RFC 6874`-shaped token, including
  references in CHANGELOG context. Pre-1.0 repos using "RFC" in commit
  subjects without a real spec dependency will over-flag — accepted: routing
  Deep on those is not harmful.
- The audit phase shells out to `git` without GIT_CONFIG isolation; tests
  isolate via env. Production runs trust the repo's git config.

## Fixtures

Audit-phase fixtures live under `tests/code-ultrareview/fixtures/audit/`,
one JSON file per case. The fixtures encode pre-computed signal sets — the
router consumes them directly. End-to-end signal extraction is exercised by
`test_audit_signals.py`, which builds tempdir git repos per signal.

| Fixture | Expected tier |
|---------|---------------|
| `small-low-risk.json` | standard |
| `manifest-only-delta.json` | standard |
| `public-api-change.json` | deep |
| `spec-claim.json` | ultra |
| `pre-1.0-large-refactor.json` | ultra |
