# Ultra tier — execution, fuzz, `--apply-safe`

The Ultra tier adds build verification, property-fuzz harness synthesis,
spec-conformance fetching with a local cache, and the `--apply-safe`
writers. Standard + Deep stay in-session and read-only; Ultra layers the
extra verification on top. Read this before dispatching when the audit
phase routes to Ultra or the user passes `-t ultra`.

## Build detection

`scripts/build_detect.py` probes the repo for a known build/test tool and
returns the canonical test command. Probe order is fixed — first hit wins:

| Probe file | Tool | Test command |
|------------|------|--------------|
| `pnpm-lock.yaml` | `pnpm` | `pnpm test` |
| `yarn.lock` | `yarn` | `yarn test` |
| `package-lock.json` | `npm` | `npm test --no-coverage` |
| `package.json` (no lockfile) | `npm` | `npm test --no-coverage` |
| `pyproject.toml` or `requirements.txt` | `pytest` if listed; else `unittest` | `pytest -x` / `python3 -m unittest discover` |
| `Cargo.toml` | `cargo` | `cargo test` |
| `go.mod` | `go` | `go test ./...` |
| `Makefile` with a `test:` target | `make` | `make test` |

Output JSON: `{"tool": "<name>", "test_command": "<cmd>", "available": <bool>}`.
`available` is `false` when the underlying binary (`pnpm`, `pytest`, …) is
not on PATH — the dispatcher reports the gap and skips Ultra execution
rather than failing.

## Sandbox protocol

Build commands run in the **repo's own working tree** via `subprocess.run`
with a 120s timeout. There is no Docker / VM isolation at MVP — the user
is expected to invoke `code-ultrareview -t ultra` on a clean tree (warning
emitted otherwise). Future phase-2 work (`--remote`) escalates to
Anthropic's Code Sandbox for true isolation.

The subagent runs the command, captures stdout + stderr + exit code, and
feeds the result into the Deep iteration verdict (`confirmed` /
`disproved` / `inconclusive`). Output longer than 10 KB is truncated to
the last 100 lines — keeps the orchestrator context bounded.

## Spec-conformance lens (full implementation)

`scripts/spec_conformance.py` extends the WS-3 stub with cache management:

- Cache directory: `~/.claude/cache/code-ultrareview/specs/`
- File name: `{spec-slug}-{date}.txt`, where `spec-slug` is
  `spec_claim.slugify_spec(name)` and `date` is `YYYY-MM-DD` (cached
  fetch's date).
- Cache-hit policy: serve cached body when `now - mtime ≤ 7 days`.
  Otherwise mark stale and let the subagent refresh.
- ETag support: the subagent passes the ETag header on refresh; a 304
  Not Modified extends the mtime.

API:

```python
spec_conformance.is_cache_fresh(path, now=time.time()) -> bool
spec_conformance.cache_path_for(spec_name, date=None) -> Path
spec_conformance.read_cached(spec_name) -> Optional[str]
spec_conformance.write_cache(spec_name, body, date=None) -> Path
spec_conformance.format_unverified_finding(spec_name, location, reason) -> dict
```

The script never makes network calls. `WebFetch` is the subagent's
responsibility — Python owns cache + finding formatting.

## Property-fuzz harness synthesis

`scripts/harness_synth.py` emits a property-test skeleton for the host
repo. Detection from manifests:

- `package.json` has `fast-check` in `dependencies` or `devDependencies` → emit `tests/<name>.fast-check.ts`
- `pyproject.toml`/`requirements.txt` mentions `hypothesis` → emit `tests/test_<name>_property.py`
- Neither → return `{"skipped": true, "reason": "install fast-check or hypothesis"}`

The emitted harness is a **skeleton** — it imports the property library,
declares one `@given` / `fc.assert` block per detected invariant from the
spec grammar, and adds TODO comments where the user fills in the
property assertion. Subagents are not asked to write production property
tests — MVP target is "harness runs, raises informative TODO" so users
have a starting point.

Spec-grammar inference is best-effort: an EBNF-like clause
`ZoneID = 1*( unreserved / pct-encoded )` produces an arbitrary returning
strings matching `[A-Za-z0-9._~-]+` or `%[0-9A-Fa-f]{2}` sequences. The
generator coverage is documented in the harness skeleton, never silently.

## `--apply-safe` writers

The Ultra tier opt-in `--apply-safe` flag enables three writers under
`scripts/apply_safe/`. Each writer:

- Reads inputs from a JSON spec (passed via stdin or `--input`).
- Computes the proposed change.
- Shows the diff to the user via a `print()` block.
- Prompts `Apply this change? (y/N) `.
- Writes the file only on `y` / `yes`.

`-y` (yes-to-all) bypasses the prompt. The `confirm_write()` helper in
`scripts/apply_safe/_common.py` centralizes the gate so all three writers
share the same UX.

### `version_sync.py`

Aligns version artifacts (package.json, marketplace.json, CHANGELOG, git
tag) to a single canonical value. Selection rule: the version associated
with the **most-recently-touched** source per `git log -1 --format=%H --
<file>`. Idempotent (running twice is a no-op when sources already
agree). Never touches the git tag — the user creates tags explicitly.

### `description_sync.py`

Aligns structured description fields under a strict **full-agreement
guard**: write the new value only when every present source already
agrees on the new value. Partial agreement (e.g., 2 of 3 sources match) →
refuses with `refusing: partial-agreement` and exits 1. The guard is the
Risk #3 mitigation — auto-fixing descriptions when sources disagree could
overwrite a deliberate divergence.

### `failing_test_writer.py`

Given a confirmed bug + repro vector, writes one focused failing test
under the host repo's test layout. Python: `tests/<area>/test_<bug-id>.py`.
TypeScript: `tests/<bug-id>.test.ts`. Never modifies existing tests —
additive only. The test is a single `assert` (or `expect`) that fails on
the unfixed code and passes after the user fixes it.

## Ultra-tier flow

Detail of the orchestrator pass at Ultra:

1. Run audit + tier router → confirm `ultra`.
2. Build detection (`build_detect.py`). Report tool + availability.
3. Standard + Deep lens fan-out (already covered by WS-2 + WS-4).
4. Spec-conformance fetch + iteration on flagged specs.
5. Property-fuzz harness synthesis when a property lib is present.
6. Run the canonical test command (`build_detect`'s `test_command`); pipe verdict into Deep iteration.
7. If `--apply-safe`: invoke the three writers with per-file confirmation.
8. Emit the canonical report from `templates/code-ultrareview.md` with the `## --apply-safe summary` section listing writes applied + skipped.

## Caveats

- Ultra runs the repo's own test suite. Unit tests with side effects
  (filesystem writes, network calls) will execute. The user is expected
  to invoke Ultra on a clean working tree; a warning fires when
  `git status --porcelain` is non-empty.
- The full-agreement guard for description sync is conservative on
  purpose. When a repo legitimately wants divergent descriptions, the
  user allowlists the pair in `.coherence-ignore` and the lens stops
  flagging — `description_sync` is then never invoked.
- Property-fuzz harness synthesis is a starting point, not a finished
  test. Users still write the property — the skeleton just removes the
  setup friction.
- `--apply-safe` never modifies production logic. Three classes only:
  manifest version sync, structured-field description sync (full-agreement
  guard), failing test write. Logic changes belong to `/simplify` and the
  future `/modernize` skill.
