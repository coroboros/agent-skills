# Audit phase — signal extraction + report-header context

Read this before dispatching the audit subagent. It pins the Haiku brief, the
signal schema emitted by `scripts/audit_signals.py`, and the report-header
formatting contract owned by `scripts/audit_summary.py`. SKILL.md keeps the
audit phase under 25 lines on purpose — every detail expands here.

The audit phase is informational only. It does not route to a tier; the lens
fan-out always runs at full strength. The signals exist to (1) populate the
report header with what the diff touches and an estimated wall-clock, and (2)
inform downstream tools (build-detection, property-fuzz availability,
spec-claim triggering).

## Subagent dispatch

One `Explore` subagent, model `haiku`, runs the audit. Cost target: ~$0.005
per run (Haiku rate × ~30k input tokens).

The subagent's job is mechanical: shell out to `audit_signals.py` and pipe
the result through `audit_summary.py` for header formatting. No reasoning,
no synthesis — the scripts are deterministic.

```bash
# Clean tree
python3 "${CLAUDE_SKILL_DIR}/scripts/audit_signals.py" \
  --base "<base>" --target "<target>" --json \
| python3 "${CLAUDE_SKILL_DIR}/scripts/audit_summary.py" [--build] [--fuzz]

# Dirty tree (uncommitted: git diff HEAD + untracked files, each read in full)
python3 "${CLAUDE_SKILL_DIR}/scripts/audit_signals.py" \
  --dirty-tree --json \
| python3 "${CLAUDE_SKILL_DIR}/scripts/audit_summary.py" [--build] [--fuzz]
```

The dirty-tree mode mirrors the lens contract in `references/lenses.md:22`:
tracked changes from `git diff HEAD` plus every path from
`git ls-files --others --exclude-standard`, each counted as all-added
LOC. Output carries `"dirty_tree": true` so the summary prefixes the
scope with `dirty tree` and the report header reflects the real diff
rather than collapsing to `trivial diff`.

The `--build` and `--fuzz` flags are caller-supplied — the orchestrator runs
`build_detect.py` and inspects the manifest for `fast-check`/`hypothesis` before
invoking, then passes the booleans on the command line. They affect the
estimated wall-clock only; lens dispatch is unconditional.

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
  "security_sensitive_paths": false,
  "repo_kind": "skills",
  "repo_kind_signals": {
    "marketplace_json": ".claude-plugin/marketplace.json",
    "skill_md_count": 17,
    "package_json": null,
    "package_json_role": null,
    "pyproject_toml": null,
    "cargo_toml": null,
    "go_mod": null,
    "framework_configs": [],
    "docs_site_configs": [],
    "workspace_configs": [],
    "python_layout": false,
    "primary_signal": "marketplace.json + skills/*/SKILL.md",
    "competing_signals": [],
    "override_source": null
  }
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
| `repo_kind` | str (enum) | One of `skills`, `app`, `library`, `docs`, `monorepo`, `python`, `rust`, `go`, `unknown`. Resolved by `classify_repo()` — see *Repo-kind detection* below. |
| `repo_kind_signals` | dict | Raw detection signals + `primary_signal`, `competing_signals`, `override_source`. Lens subagents read this when their repo-kind branch needs compound-case detail beyond the single enum value. |

Test-path detection (used by `test_coverage_delta`): suffix in
`(.test.ts, .test.js, .test.tsx, .spec.ts, .spec.js)`; OR directory contains
`/tests/`/`/test/`; OR filename starts with `test_` (Python convention) or
contains `_test.` (Go convention).

### Repo-kind detection

`classify_repo()` resolves the repo's nature from on-disk signals so the
lens subagents can branch on it via their `## Repo-kind branches` sections
(`references/lens-<key>.md`). The classifier is silent on absent signals —
no log line, no warning — and emits `repo_kind: "unknown"` when nothing
matches, so existing behavior is preserved on un-classified repos.

Precedence: `skills` > `monorepo` > `docs` > `app` > `library` > `python` > `rust` > `go` > `unknown`. The pre-rendered precedence-doc test (`tests/code-ultrareview/test_classify_repo.py::test_doc_lists_canonical_order`) reads this line verbatim and compares to the implementation order — they must stay in lockstep.

| `repo_kind` | Primary signal | Secondary checks |
|-------------|----------------|------------------|
| `skills` | `.claude-plugin/marketplace.json` AND ≥1 `skills/*/SKILL.md` | `package.json` / workspace / `pyproject.toml` surface as `competing_signals` |
| `monorepo` | Any of `pnpm-workspace.yaml`, `lerna.json`, `turbo.json`, `nx.json` | Only fires when not also a skills repo (skills wins) |
| `docs` | Any of `docusaurus.config.*`, `mkdocs.{yml,yaml}`, `hugo.{toml,yaml,yml}`, `_config.yml` | A docs-site config wins over an app-role `package.json` (per the precedence line above) — Docusaurus, MkDocs, Hugo, Jekyll repos all carry app-shaped `package.json` files. `package.json` / `workspace_configs` surface as `competing_signals` |
| `app` | `package.json` with `scripts.dev` / `scripts.start` / `bin` / app-only framework config (Next, Astro) | `framework_configs` and `workspace_configs` surface as competing |
| `library` | `package.json` with `exports`, `module`, or `types` and no app indicators | — |
| `python` | `pyproject.toml` | `cargo_toml` / `go_mod` surface as competing |
| `rust` | `Cargo.toml` | `go_mod` / `pyproject_toml` surface as competing |
| `go` | `go.mod` | `pyproject_toml` surfaces as competing |
| `unknown` | None of the above | All detected signals still surface in `repo_kind_signals` |

`package_json_role` resolves to `"app"` or `"library"` (or `None` when the
file is missing or malformed) via the rules above; the permissive default
on a bare `package.json` without role signals is `"app"`. App-only
framework configs are Next/Astro (`next.config.*`, `astro.config.*`) —
Vite is ambiguous (used by both apps and libraries) and is not
role-determining at MVP.

### Repo-kind override

Two override surfaces exist; precedence is flag > config > detection.

- **CLI flag** — `python3 audit_signals.py --repo-kind <kind> --base <ref>`.
  `<kind>` must be one of the nine canonical values; invalid values exit
  with code 2 and an `invalid choice` error from argparse. `override_source`
  in the emitted JSON reads `"--repo-kind flag"`.
- **Per-repo config** — `.code-ultrareview.yaml` at repo root. One key
  recognized:

  ```yaml
  # .code-ultrareview.yaml
  repo_kind: skills  # one of the nine canonical values
  ```

  Quoted values (`repo_kind: "skills"`) and inline comments
  (`repo_kind: app # justification`) both parse. Invalid values silently
  fall through to detection (the file is not authoritative — detection is
  the floor). `override_source` reads `"config:.code-ultrareview.yaml"`.

Detection runs even when an override is in effect — `primary_signal` and
`competing_signals` still surface in `repo_kind_signals` so the report
header can show what was detected vs what was overridden.

## Audit summary (audit_summary.py output)

```json
{
  "scope": "12 files · public API · normative spec (RFC 6874) · manifest",
  "estimated_wall_clock_seconds": 480,
  "rationale": "Estimated wall-clock: 8m (480s)\n\nContributions:\n  - base: +60s\n  - 12 files × 5s: +60s\n  - public API: +60s\n  - normative spec fetch: +90s\n  - manifest delta: +60s\n  - build/execute (1000 LOC): +300s\n  - property-fuzz: +120s"
}
```

### Scope assembly

The `scope` string is a `·`-joined list of human-readable tokens, one per
signal that fires:

- `N file{s}` — from `files_touched` (singular/plural).
- `public API` — when `public_api_touched`.
- `normative spec (<names>)` — when `normative_specs_list` is non-empty;
  generic `normative spec` when only the boolean is set.
- `manifest` — when `manifest_graph_delta`.
- `security paths` — when `security_sensitive_paths`.
- `pre-1.0/freeze` — when `pre_1_0_or_freeze`.

Empty signal set → scope is `trivial diff` (rendered as-is).

### Wall-clock cost model

The estimate is deterministic. Constants live in `scripts/audit_summary.py`
and are tunable; current values:

| Contributor | Seconds |
|-------------|---------|
| `base` (audit + lens fan-out setup) | 60 |
| Per file touched | 5 |
| `public_api_touched` | 60 |
| `normative_spec_mentioned` (fetch + diff) | 90 |
| `manifest_graph_delta` | 60 |
| `security_sensitive_paths` | 60 |
| `--build` (test execution; floor 60, then `0.3 × LOC`) | 60–∞ |
| `--fuzz` (property-fuzz harness synthesis) | 120 |

The estimate is informational. It populates the `Estimated wall-clock` header
field and does not gate execution. Implementations may tune the constants
when empirical data warrants — tests pin the contract (signal flips → delta
of that exact constant), not the absolute values.

### Rationale format

Multi-line breakdown listing every active contributor, line-by-line, with the
seconds it added. Empty signal set yields a contribution list with just
`base`. The synthesizer pastes the rationale verbatim into the report's
audit-context block (when the report exposes one) — never paraphrased.

## Caveats

- `test_coverage_delta = 0.0` collapses two cases: "code added with no tests"
  (max gap) and "no code added at all" (irrelevant). When `loc_changed` is
  also near zero, the test-gap signal is mostly noise — accepted at MVP.
  Affects only the report header; lens dispatch is unaffected.
- The `public_api_touched` heuristic is intentionally loose. A `route.ts`
  file in `node_modules/` would flag — but `node_modules/` shouldn't be in
  the diff. If it is, treat the scope summary as advisory.
- `normative_spec_mentioned` matches any `RFC 6874`-shaped token, including
  references in CHANGELOG context. Pre-1.0 repos using "RFC" in commit
  subjects without a real spec dependency will over-flag — accepted; it
  only inflates the wall-clock estimate.
- The audit phase shells out to `git` without GIT_CONFIG isolation; tests
  isolate via env. Production runs trust the repo's git config.
- Compound `repo_kind` cases (a skills repo with npm tooling, an app with
  workspace configs, a dual-language repo with both `Cargo.toml` and
  `go.mod`) are resolved by the precedence table and the non-winning
  signals surface as `competing_signals`. False-positive risk on truly
  ambiguous repos (e.g. a vendored dep folder mistakenly at the root)
  is bounded by the override mechanism — `--repo-kind` or
  `.code-ultrareview.yaml` corrects the classification, and
  `override_source` makes the human's call visible in the report header.

## Fixtures

Audit-phase fixtures live under `tests/code-ultrareview/fixtures/audit/`,
one JSON file per case. They encode pre-computed signal sets — useful for
exercising the `audit_summary.py` contract without re-running the signal
extractor. End-to-end signal extraction is exercised by
`test_audit_signals.py`, which builds tempdir git repos per signal.

| Fixture | Profile |
|---------|---------|
| `small-low-risk.json` | tiny diff, no flags |
| `manifest-only-delta.json` | manifest touched, no other signals |
| `public-api-change.json` | mid-size diff, public API touched |
| `spec-claim.json` | normative-spec mentioned |
| `pre-1.0-large-refactor.json` | pre-1.0 + LOC-heavy refactor |
| `skills-repo-clean.json` | skills repo, no competing signals |
| `app-repo-clean.json` | app repo with framework config detected |
| `skills-repo-with-override.json` | skills repo with `--repo-kind` flag override and `npm tooling` competing signal |

Repo-kind classifier fixtures live under
`tests/code-ultrareview/fixtures/classify/{skills, app, library, docs,
monorepo, python, rust, go, unknown, mixed-skills-npm}/` — minimal
on-disk repos exercising one signature per directory. The `mixed-skills-npm`
fixture pins the precedence resolver (`skills` wins over coexisting
`package.json`).
