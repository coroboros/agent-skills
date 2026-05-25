# Lens: Bugs + drift (key `bugs-drift`)

- **Bug** — a logic error on a changed line: wrong condition, off-by-one, unhandled `null`/empty, mishandled error, race, resource leak.
- **Drift** — code that no longer matches its own docstring, inline comment, README claim, or `CLAUDE.md` statement; or a change that diverges from an established sibling pattern in the same module without cause.
- **Single source of truth** — a literal that must stay equal across sites (path, URL, endpoint, constant, version, env-var name) introduced or duplicated by the diff in two or more places. A change to one copy silently diverges from the others, so report it as drift and cite both sites. Distinct from cosmetic dedup (→ `/simplify`): report only when divergence would break behavior, never for stylistic repetition.

## A1 — spec-claim triggering (always on)

When the diff, README, or `CLAUDE.md` cites a named normative spec
(`RFC 6874`, `WHATWG`, `ISO/IEC 7816`, `OpenAPI`, etc. — same regex as
`scripts/audit_signals.py`), the lens fetches the spec via `WebFetch`,
quotes the governing clause verbatim in the finding's `recommendation`,
and diffs the code against the quoted clause. The cache at
`~/.claude/cache/code-ultrareview/specs/` is shared with the
spec-conformance lens; ETag refresh ≥7 days. A verifiable divergence
scores **≥80** confidence — the quoted spec clause is the evidence.

## Iteration on sub-80 findings (always on)

Sub-80 bug/drift findings are re-passed with `--iterate`: the subagent
attempts a build (`npm test --no-coverage`, `pytest -x`, `cargo test`,
or `go test` — auto-detected) on the changed file's nearest test
neighbor. If the build confirms the bug, confidence promotes to ≥80;
if the build disproves it, the finding is dropped with the build output
in the rationale. Cap: one iteration per finding.

## Repo-kind branches

The lens reads `repo_kind` from the audit phase and applies the rules
below before evaluating drift. Default (`unknown`) preserves the
operational definitions above.

| `repo_kind` | Drift framing |
|-------------|---------------|
| `skills` | Drift reframes from "code vs docstring" to "bundled scripts (`skills/<name>/scripts/`) vs the SKILL.md spec". The SKILL.md IS the canonical spec — it cannot drift from itself. Fire when: SKILL.md declares a flag absent from the script's parser; SKILL.md declares an output schema the script doesn't emit; SKILL.md cites a behavior the script no longer produces. Pure-prompt skills (no `scripts/` folder) emit no drift findings. |
| `app`, `library` | Existing behavior — code vs docstring vs README claim. |
| `python` | Docstring-aware (triple-quoted blocks); otherwise as code. |
| `rust` | `///` doc comments are the docstring surface. |
| `go` | `// godoc` comments are the docstring surface. |
| `docs` | No executable surface for drift. Lens emits zero findings; summary row renders 🟢 — the `Repo: docs` header line carries the context that the lens did not specialize. |
| `monorepo` | Cannot specialize at MVP. Subagent applies the most-permissive ruleset (treat as code repo); per-workspace tuning is parked. |
| `unknown` | Existing behavior. |
