# Opt-in flag execution — `--verify-build`, `--mutation-test`, `--reconcile`, `--apply-safe`

Reference for the four opt-in flags. Defaults are off — these layer on top of the always-on 5-phase pipeline (scope → tool battery → 8 axis reviewers → fresh-context validators → synthesis). Each flag has a single load-bearing entry point script; the SKILL.md prose calls these scripts from the orchestrator (main thread).

## `--verify-build` (Phase 3.5 — build verification)

Runs the repository's canonical test command as an atomic gate BEFORE the Phase 4 validators. A generic pass or failure is project-level evidence, not proof about a specific finding, so this phase never changes finding confidence.

| Field | Value |
|-------|-------|
| Entry point | `scripts/run_build_verify.py` |
| Detector | `scripts/build_detect.py` — first-hit-wins probe |
| Finding behavior | Pass-through; no promotion or demotion |
| Runs in phase | 3.5 (between axis review and validators) |
| Default timeout | 120 s (override via `--timeout`) |

### Detection table

`build_detect.detect()` probes in fixed order; first hit wins:

| Probe file | Tool | Test command |
|------------|------|--------------|
| `pnpm-lock.yaml` + non-empty `scripts.test` | `pnpm` | `pnpm test` |
| `yarn.lock` + non-empty `scripts.test` | `yarn` | `yarn test` |
| `package-lock.json` or `package.json` + non-empty `scripts.test` | `npm` | `npm test` |
| `pyproject.toml` / requirements mentioning `pytest` + `uv.lock` | `pytest` | `uv run --frozen --offline --no-sync pytest -x` |
| `pyproject.toml` / requirements mentioning `pytest` + `poetry.lock` | `pytest` | `poetry run pytest -x` |
| Other Python manifest mentioning `pytest` | `pytest` | `pytest -x` |
| A `test*.py` file containing a unittest test method | `unittest` | `python3 -m unittest discover` |
| `Cargo.toml` | `cargo` | `cargo test` |
| `go.mod` | `go` | `go test ./...` |
| `Makefile` with a `test:` target | `make` | `make test` |

Output is `{"tool": "<name>", "test_command": "<cmd>", "available": <bool>}`. A Python manifest without a declared pytest runner or a collectable unittest suite does not qualify. A missing command or unavailable runner exits 3 with an exact remediation. A zero-test suite, command failure, timeout, or execution error exits 4. Both stop the review before validation and synthesis.

### Gate semantics

`run_build_verify.py` first marks `build_coverage` incomplete and removes any previous build findings/sidecar. It then runs the detected command once through `scripts/process_timeout.py`, which starts a separate process group and terminates the group on timeout:

- **Pass** — records complete build coverage; every finding continues unchanged to validators.
- **No sub-80 findings** — still runs the requested gate; finding confidence does not control flag execution.
- **Missing command or runner** — records incomplete coverage, prints the exact prerequisite/rerun steps, exits 3.
- **Missing/malformed findings input, zero collected tests, failure, timeout, or execution error** — records incomplete coverage and actionable diagnostics, exits 4.

The synthesis guard rejects an incomplete `build_coverage` manifest even if an orchestrator incorrectly attempts to continue after exit 3 or 4.

### Output

`<output-dir>/build-verified.jsonl` carries every input finding unchanged. A `build-verified.jsonl.meta.json` sidecar records `complete`, `applicable`, `build_status`, `tool`, `test_command`, `exit_code`, `stdout_tail`, and `stderr_tail`. The same minimum coverage state is written to `scope.json["build_coverage"]`.

### Sandbox

The test command runs in the **repo's own working tree** — no Docker / VM isolation. Invoke `code-ultrareview` on a clean tree; the scope phase already warns when `git status --porcelain` is non-empty. Captured output is limited to the final 100 lines per stream.

---

## `--mutation-test` (Phase 2 extension)

Produces an independently manifested mutation-findings stream. Axis preparation verifies and adds it to the Tests bundle; synthesis verifies and includes the same stream directly. It is never folded into the deterministic battery's `tool-findings.jsonl` manifest.

| Field | Value |
|-------|-------|
| Entry point | `scripts/run_mutation.py` |
| Per-language tools | directly declared project `stryker run` (JS/TS) · PATH `mutmut run` with project config (Python) · PATH Maven or Gradle with declared Pitest integration (JVM) |
| Output axis | `tests` |
| Severity | `Medium` (🟠) |
| Confidence | `0` (unassessed observation — requires Phase 4 context validation) |
| Default timeout | 600 s (override via `--timeout` or `MUTATION_TIMEOUT`) |

### Dispatch

`run_mutation.py` reads `scope.json["languages"]` and `scope.json["files_touched_list"]`:

- **JS/TS** — requires `@stryker-mutator/core` declared in `package.json`, its executable local/workspace-hoisted or Yarn Plug'n'Play `stryker`, and `stryker.config.*`. A declared dependency never falls back to a global version. The `--mutate` argument contains only changed `.ts/.tsx/.js/.jsx/.mjs/.cjs` files.
- **Python** — requires `mutmut` on `PATH` and project mutation configuration. mutmut v3 executes the configured project scope; findings are filtered to changed `.py` files.
- **JVM (Maven)** — requires `mvn` on `PATH`, `pom.xml`, and `org.pitest:pitest-maven` under `build.plugins`. It runs `mvn --offline -q -B pitest:mutationCoverage`; findings are filtered to changed JVM source files.
- **JVM (Gradle)** — requires `gradle` on `PATH` and the `info.solidsoft.pitest` plugin in `build.gradle` or `build.gradle.kts`. It runs `gradle --offline --no-daemon pitest`; remediation stays Gradle-specific.

### Tool-output parsing

Each tool writes its native report:

- **Stryker** — validates `reports/mutation/mutation.json` against the Mutation Report Schema. `Survived` and `NoCoverage` mutants become Tests-axis findings with `location: "<file>:<line>:<col>"`; `Ignored` is intentional and `Pending` blocks as incomplete. A successful run with zero changed-file mutants is valid and emits no findings.
- **mutmut** — runs `mutmut results --all true`, validates every mutmut v3 `name: status` row, and calls `mutmut show <name>` for findings to map them to a changed file and its unique function definition. Killed, caught-by-type-check, survived, no-tests, suspicious, timeout, and segfault rows prove evaluation; only `survived`, `no tests`, and `suspicious` rows become findings. `not checked`, interrupted, or zero evaluated mutants block as incomplete. All commands use bounded process-group timeouts.
- **Pitest** — validates each fresh canonical `mutations.xml` under `target/pit-reports/**` for Maven or `build/reports/pitest/**` for Gradle. `SURVIVED` and `NO_COVERAGE` rows mapped to changed files become findings; a successful run with no mapped survivors is valid. Any nonzero Pitest exit blocks before report parsing, even if a fresh report exists.

All parsed findings emit to `<output-dir>/mutation-findings.jsonl` with the canonical schema:

```json
{
  "axis": "tests",
  "severity": "Medium",
  "location": "<file>:<line>[:<col>]",
  "finding": "Surviving or uncovered mutant (<mutatorName>): <description>",
  "recommendation": "Add execution coverage or an assertion that catches the mutation.",
  "confidence": 0,
  "source_tool": "stryker" | "mutmut" | "pitest"
}
```

### Atomic failure contract

The script preflights every applicable language before starting any mutation process. Maven and Gradle wrappers are not used: a wrapper may download its own distribution before build-level offline flags apply. A `PATH` runner executes from the one governing build directory with offline flags, so multi-build diffs must be reviewed separately. Findings publish only after every applicable language succeeds; any later-language failure publishes no `mutation-findings.jsonl`. Missing runners exit 3 with exact remediation. A command failure, missing Pitest task/configuration, timeout, stale/missing report, or malformed report exits 4. A successful applicable run records the output path, SHA-256 digest, and finding count in `scope.json["mutation_coverage"]`; axis preparation records that same identity as an input, and synthesis requires the manifest-bound file through `--mutation-findings`. Coverage remains incomplete on failure, and both phases reject it independently. A diff with no supported changed code is explicitly `not-applicable` and exits 0. The script never auto-installs. `MUTATION_DRY_RUN=1` is a test hook that exits 0 after prerequisites pass but deliberately leaves mutation coverage incomplete, so it cannot support a verdict.

---

## `--reconcile <input>` (Intent axis derivation sub-mode)

Activates the planning-artifact reconciliation branch of the Intent axis. The orchestrator already runs the Intent axis in standard mode (PR description vs diff, lockfile drift, generator drift); `--reconcile` adds a deterministic claim-extraction pass that produces `UNCLASSIFIED` placeholders for the Intent subagent to classify.

An explicit `--axes` subset must include `intent` when reconciliation is requested. Preparation rejects an incompatible subset; ingestion and synthesis also reject a persisted reconcile run without Intent coverage. Include `intent` in the selected axes or omit `--reconcile` for a review that does not reconcile planning artifacts.

| Field | Value |
|-------|-------|
| Entry point | `scripts/derivation/run.py` |
| Classifications | `GAP` / `SCOPE-ADD` / `DECISION-OVERRIDE` / `CONSISTENT` (LLM-assigned) |
| Default severity | `GAP: Medium` · `SCOPE-ADD: Low` · `DECISION-OVERRIDE: Medium` · `CONSISTENT: —` |
| Stale-artifact handling | `> 30 days` caps severity at `Low`; auto-discovered artifacts older than 90 days are summary-only. Explicit sources always emit their extracted claims. `--strict` disables historical freshness caps; extracted claim coverage is never capped |
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

Multiple inputs via comma: `--reconcile @auto,gh:pr:42`. Every explicit path, `@pr`, PR number, issue reference, or issue URL is atomic: unavailable sources exit 3; malformed or claim-free explicit artifacts exit 4. `@auto` requires at least one discoverable source and validates every resolved artifact before Intent review.

Invoke the deterministic stage with the Phase 1 scope and a run-local output:

```bash
python3 "$SKILL_DIR"/scripts/derivation/run.py \
  --repo <repo-root> \
  --scope <scope.json> \
  --output <run-dir>/reconcile.json \
  --reconcile <input>
```

The output is written atomically. Its path, SHA-256 digest, and finding count are stored in `scope.json["reconcile_coverage"]`. Axis preparation verifies all three and embeds the payload only in the Intent bundle; a missing, failed, or modified result exits 4 before any axis launches.

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

The reviewer first inspects the host's runner and test layout, then authors and reviews one focused executable regression test. Call `write(repo, bug_id, repro, expected_failure, test_content=..., test_path=..., yes=...)` with that exact content and a repository-relative test path. The writer previews and persists it additively; it does not infer Python/Vitest or generate tests from prose. Missing content or an invalid path refuses the write; existing tests are never overwritten. Verify that the test fails for the reported defect and passes after correcting only the implementation before claiming regression coverage. Writing the test alone proves neither result.

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
| `--verify-build --mutation-test` | Mutation tests publish their independently manifested Tests-axis stream; build verification runs Phase 3.5. Different phases, no interaction. |
| `--verify-build --reconcile @auto` | Build verification runs once in Phase 3.5 whenever requested; Intent axis runs the derivation sub-mode in Phase 3. The gate does not alter individual finding confidence. |
| `--mutation-test --apply-safe` | Mutation findings surface in the report's Tests-axis section; `--apply-safe` writers run after synthesis. The writers do not modify code-under-test in response to mutation findings — that belongs to a follow-up fix pass via `/apex` or `/oneshot`. |
| `--verify-build --mutation-test --reconcile @auto --apply-safe` | Full opt-in stack. Phase 2 extended (mutation), Phase 3 enriched (reconcile derivation), Phase 3.5 active (build verification), post-synthesis writers gated by confirmation. |

**Without a flag, its feature is off** — load-bearing default. The orchestrator never calls `run_build_verify.py`, `run_mutation.py`, `derivation/run.py`, or the `apply_safe/` writers unless its flag is set.

## Caveats

- Build verification runs the repo's own test suite. Side-effecting tests (filesystem writes, network calls) will execute — invoke `code-ultrareview` on a clean tree.
- Mutation testing runtime can exceed 10 minutes per language. The default 600 s timeout is permissive; long suites may need `MUTATION_TIMEOUT=1800` or longer.
- `--apply-safe` never modifies production logic. Logic changes belong to a fix-pass skill, not a review skill.
- `--reconcile` never silently drops a resolved source. Correct the path, GitHub authentication/reference, encoding, frontmatter delimiter, or supported claim sections, then rerun with the same value.
