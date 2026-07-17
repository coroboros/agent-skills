# Opt-in flag execution — `--verify-build`, `--mutation-test`, `--reconcile`, `--apply-safe`

Reference for the four opt-in flags. Defaults are off — these layer on top of the always-on 5-phase pipeline (scope → tool battery → 8 axis reviewers → Haiku validators → synthesis). Each flag has a single load-bearing entry point script; the SKILL.md prose calls these scripts from the orchestrator (main thread).

## `--verify-build` (Phase 3.5 — build verification)

Promotes sub-80 axis findings via the repo's own test command BEFORE the Phase 4 Haiku validators. Confirmed promotions skip Phase 4 entirely.

| Field | Value |
|-------|-------|
| Entry point | `scripts/run_build_verify.py` |
| Detector | `scripts/build_detect.py` — first-hit-wins probe |
| Composer | `scripts/synthesis_core.py:iterate_unverified` — `+30` confidence, capped at `95`, floor at `80` |
| Runs in phase | 3.5 (between axis review and validators) |
| Default timeout | 120 s (override via `--timeout`) |

### Detection table

`build_detect.detect()` probes in fixed order; first hit wins:

| Probe file | Tool | Test command |
|------------|------|--------------|
| `pnpm-lock.yaml` | `pnpm` | `pnpm test` |
| `yarn.lock` | `yarn` | `yarn test` |
| `package-lock.json` or `package.json` | `npm` | `npm test --no-coverage` |
| `pyproject.toml` / `requirements.txt` mentioning `pytest` | `pytest` | `pytest -x` |
| `pyproject.toml` / `requirements.txt` without `pytest` | `unittest` | `python3 -m unittest discover` |
| `Cargo.toml` | `cargo` | `cargo test` |
| `go.mod` | `go` | `go test ./...` |
| `Makefile` with a `test:` target | `make` | `make test` |

Output is `{"tool": "<name>", "test_command": "<cmd>", "available": <bool>}`. `available: false` (binary not on PATH) → graceful skip; the run continues without build-verification.

### Per-finding verdict

`run_build_verify.py` runs the test command **once** with `subprocess.run(shell=True, cwd=repo, timeout=…)`, then assigns a verdict per sub-80 finding:

- **`confirmed`** — exit code ≠ 0 AND `finding.axis ∈ {correctness, tests, design-api, performance}`. `iterate_unverified` applies the promotion (severity restored from `meta.original_severity` when set; `[unverified]` prefix stripped; marker re-attached).
- **`inconclusive`** — every other case. Finding passes through unchanged into Phase 4.
- **`disproved`** — intentionally unused at MVP. A passing build does not actively disprove an LLM finding, and a drop verdict would silently lose Unverified candidates the validator phase can still confirm. A2 stays load-bearing.

Style / Documentation / Intent / Simplification / Coherence findings are always `inconclusive` — the test command does not exercise them.

### Output

`<output-dir>/build-verified.jsonl` carries every input finding (with promotions applied to confirmed ones). A `build-verified.jsonl.meta.json` sidecar records: `build_status` (`ran` / `timeout` / `error` / `skipped`), `tool`, `test_command`, `exit_code`, `build_failed`, `promoted_count`, `remaining_sub80_count`.

### Sandbox

The test command runs in the **repo's own working tree** — no Docker / VM isolation at MVP. Invoke `code-ultrareview` on a clean tree; the scope phase already warns when `git status --porcelain` is non-empty. Output beyond 10 KB is truncated to the last 100 lines by callers to keep orchestrator context bounded.

---

## `--mutation-test` (Phase 2 extension)

Routes mutation-tool findings into the Phase 2 tool-findings stream so the Tests axis subagent sees surviving mutants alongside the other deterministic CLI outputs.

| Field | Value |
|-------|-------|
| Entry point | `scripts/run_mutation.sh` |
| Per-language tools | project/PATH `stryker run` (JS/TS) · PATH `mutmut run` (Python) · `mvn org.pitest:pitest-maven:mutationCoverage` (JVM) |
| Output axis | `tests` |
| Severity | `Medium` (🟠) |
| Confidence | `100` (deterministic — skips Phase 4) |
| Default timeout | 600 s (override via `--timeout` or `MUTATION_TIMEOUT`) |

### Dispatch

`run_mutation.sh` reads `scope.json["languages"]` and `scope.json["files_touched_list"]`:

- **JS/TS** — runs only when a stryker config file (`stryker.{conf,config}.{js,mjs,json}`) exists OR `@stryker-mutator/core` appears in `package.json`, and resolves `stryker` from `node_modules/.bin` then `PATH`. Mutate scope = changed `.ts/.tsx/.js/.jsx/.mjs/.cjs` files from the diff.
- **Python** — runs when `mutmut` is on `PATH`. Mutate scope = changed `.py` files from the diff. Skips when no changed Python files are in scope.
- **JVM** — runs when `pom.xml` exists AND `mvn` is on PATH. Gradle / standalone pitest are deferred; the script logs an install hint.

### Tool-output parsing

Each tool writes its native report:

- **Stryker** — `reports/mutation/mutation.json` — Mutation Report Schema. Surviving mutants (`status: "Survived"`) become Tests-axis findings with `location: "<file>:<line>:<col>"`.
- **mutmut** — parses `mutmut results` output for the *Survived* block, then calls `mutmut show <id>` for each ID to recover the file/line.
- **pitest** — parses `target/pit-reports/<latest>/mutations.xml`; `<mutation status="SURVIVED">` rows become findings.

All parsed findings emit to `<output-dir>/mutation-findings.jsonl` with the canonical schema:

```json
{
  "axis": "tests",
  "severity": "Medium",
  "location": "<file>:<line>[:<col>]",
  "finding": "Surviving mutant (<mutatorName>): <description>",
  "recommendation": "Tests did not catch this mutation — add an assertion that fails when the mutated code path executes.",
  "confidence": 100,
  "source_tool": "stryker" | "mutmut" | "pitest"
}
```

### Graceful skip

Missing config, missing tool, no changed files in the relevant language, timeout, or `MUTATION_DRY_RUN=1` all emit `WARN: <reason>` to stderr and produce an empty (or no-newer-rows-appended) `mutation-findings.jsonl`. The script never auto-installs — install commands surface in the WARN line. `MUTATION_DRY_RUN=1` exists as a test hook so the script can be exercised without invoking actual mutation tooling.

---

## `--reconcile <input>` (Intent axis derivation sub-mode)

Activates the planning-artifact reconciliation branch of the Intent axis. The orchestrator already runs the Intent axis in standard mode (PR description vs diff, lockfile drift, generator drift); `--reconcile` adds a deterministic claim-extraction pass that produces `UNCLASSIFIED` placeholders for the Intent subagent to classify.

| Field | Value |
|-------|-------|
| Entry point | `scripts/derivation/run.py` |
| Classifications | `GAP` / `SCOPE-ADD` / `DECISION-OVERRIDE` / `CONSISTENT` (LLM-assigned) |
| Default severity | `GAP: Medium` · `SCOPE-ADD: Low` · `DECISION-OVERRIDE: Medium` · `CONSISTENT: —` |
| Stale-artifact handling | `> 30 days` caps severity at `Low`; `> 90 days` summary-only (no findings) — disable both with `--strict` |
| Allowlist file | `.derivation-ignore` (parsed by `derivation/_common.py:load_ignore`) |

### Input forms

| Token | Meaning |
|-------|---------|
| `@auto` | `~/.agents/output/{project}/forge/forge-*.md`, latest `apex/{task-id}/` plan, `docs/{proposals,design,rfcs,adr}/*.md`, current branch's PR body |
| `@pr` | Current branch's PR body via `gh pr view` |
| `<path>` | Explicit file or directory |
| `gh:pr:<N>` | PR by number via `gh api` |
| `gh:issue:<owner>/<repo>#<N>` | Issue by reference |
| GitHub issue URL | Parsed → `gh api` |

Multiple inputs via comma: `--reconcile @auto,gh:pr:42`. `gh` failures degrade silently — only available sources reach the subagent.

### Output

`derivation/run.py --json` emits:

```json
{
  "lens": "derivation",
  "artifacts": [{"path": …, "kind": …, "freshness_days": …, "claim_count": …}],
  "findings": [
    {"lens": "derivation", "classification": "UNCLASSIFIED", "severity": …,
     "location": "<artifact>:<line>", "finding": "<claim text>",
     "recommendation": "Compare this <kind> against the diff. Classify as GAP / SCOPE-ADD / DECISION-OVERRIDE / CONSISTENT.",
     "confidence": 0,
     "artifact_path": …, "artifact_freshness_days": …}
  ]
}
```

The Intent axis subagent reads this alongside its standard inputs, replaces each `UNCLASSIFIED` with the correct tag, and assigns final severity per the spec. `GAP` escalates to `High` when the artifact is a forge plan AND the claim is a numbered acceptance criterion.

---

## `--apply-safe` (opt-in writers)

Reading-only is the default. `--apply-safe` enables three surgical writers under `scripts/apply_safe/`, each gated by a diff preview + per-file `y/N` confirmation (or `-y` to bypass).

| Writer | Module | Scope |
|--------|--------|-------|
| `version_sync` | `apply_safe/version_sync.py` | `package.json` ↔ `.claude-plugin/marketplace.json` (`version` or `metadata.version`) |
| `description_sync` | `apply_safe/description_sync.py` | `package.json` ↔ `marketplace.json` (`description` or `metadata.description`) |
| `failing_test_writer` | `apply_safe/failing_test_writer.py` | Single failing test per confirmed bug — additive only |

### `version_sync`

Most-recently-touched source wins (`git log -1 --format=%ct -- <file>`). Idempotent — running twice when sources agree is a `no-op`. Never touches the git tag. CHANGELOG-only edits are out of scope.

### `description_sync`

Strict full-agreement guard: writes the new value only when every present source already shares one value. Partial agreement (e.g. 2 of 3 match) → `refusing: partial-agreement` and exit 1. The guard prevents overwriting a deliberate divergence. Legitimate divergences belong in `.coherence-ignore`.

### `failing_test_writer`

Given a confirmed bug + repro vector + expected failure message, writes one focused failing test under the host repo's test layout (Python `tests/test_<slug>.py` or TypeScript `tests/<slug>.test.ts`). Refuses to overwrite an existing test (`refusing: existing-test`). The body is a single `assert` (or `expect`) that fails on the unfixed code and passes after the user's fix.

### Confirmation gate

`apply_safe/_common.py:confirm_write` is the single source of truth:

```python
def confirm_write(path, diff_text, yes=False) -> bool:
    print(f"\n--- {path} ---")
    print(diff_text.rstrip())
    print("--- end diff ---")
    if yes:
        return True
    answer = input(f"Apply this change to {path}? (y/N) ").strip().lower()
    return answer in ("y", "yes")
```

No writer modifies a file outside of `confirm_write` returning `True`. Reviewing the diff, declining (`n` / blank), and re-running is the expected loop.

### Report integration

When `--apply-safe` is set, the report's `## 🪛 --apply-safe summary` section lists each writer's status (`applied` / `skipped` / `no-op` / `refusing: …`) with target files. The section is omitted when the flag is absent — keeps clean reports free of unused sections.

---

## Flag composition

The four flags compose orthogonally — the orchestrator runs each independently in its assigned phase:

| Combination | Behavior |
|-------------|----------|
| `--verify-build --mutation-test` | Mutation tests join Phase 2 tool-findings (Tests axis); build verification runs Phase 3.5. Different phases, no interaction. |
| `--verify-build --reconcile @auto` | Build verification runs Phase 3.5 on sub-80 findings; Intent axis runs the derivation sub-mode in Phase 3. Build-verification does not act on Intent findings (axis filter). |
| `--mutation-test --apply-safe` | Mutation findings surface in the report's Tests-axis section; `--apply-safe` writers run after synthesis. The writers do not modify code-under-test in response to mutation findings — that belongs to a follow-up fix pass via `/apex` or `/oneshot`. |
| `--verify-build --mutation-test --reconcile @auto --apply-safe` | Full opt-in stack. Phase 2 extended (mutation), Phase 3 enriched (reconcile derivation), Phase 3.5 active (build verification), post-synthesis writers gated by confirmation. |

**Without a flag, its feature is off** — load-bearing default. The orchestrator never calls `run_build_verify.py`, `run_mutation.sh`, `derivation/run.py`, or the `apply_safe/` writers unless its flag is set.

## Caveats

- Build verification runs the repo's own test suite. Side-effecting tests (filesystem writes, network calls) will execute — invoke `code-ultrareview` on a clean tree.
- Mutation testing runtime can exceed 10 minutes per language. The default 600 s timeout is permissive; long suites may need `MUTATION_TIMEOUT=1800` or longer.
- `--apply-safe` never modifies production logic. Logic changes belong to a fix-pass skill, not a review skill.
- `--reconcile @auto` silently drops planning artifacts with malformed frontmatter (unclosed `---`, tab indentation, unquoted colons). Verify with `head -20 ~/.agents/output/{project}/forge/forge-*.md` before relying on `@auto`.
