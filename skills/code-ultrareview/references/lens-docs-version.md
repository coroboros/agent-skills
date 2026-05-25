# Lens: Docs + version (key `docs-version`)

User-visible behavior changed without the matching update: public
API/flag/CLI without doc, behavior change without README/CHANGELOG where
the repo expects one, a version artifact not bumped per the repo's
release rule, or (for skill repos) README / marketplace parity broken
by the change.

## Repo-kind branches

The lens reads `repo_kind` from the audit phase to pick the right
version sources and doc-parity check.

| `repo_kind` | Version sources + doc parity |
|-------------|------------------------------|
| `skills` | Version sources: `.claude-plugin/marketplace.json` `.metadata.version` + git tags + `gh release list`. Release notes live in the `gh release create` body — there is no `CHANGELOG.md`, so absence is not a finding. README skills-table ↔ marketplace skills entries is the cross-doc check. |
| `app`, `library` | Existing behavior — `package.json` `.version` + `CHANGELOG.md` most-recent header + git tags. |
| `python` | `pyproject.toml` `[project].version` (or `setup.py`); `CHANGELOG.md` optional. |
| `rust` | `Cargo.toml` `[package].version`. |
| `go` | Git tags (Go modules use semver tags); `go.mod` for module path. |
| `docs` | Version field in the docs-site config (Docusaurus `versions.json`, MkDocs config). |
| `monorepo` | Per-workspace; lens emits zero version findings at the repo root (per-workspace specialization parked for MVP). Summary row renders 🟢 with the `Repo: monorepo` header carrying context. |
| `unknown` | Skip version sub-checks; lens emits zero version findings. Summary row renders 🟢 with the `Repo: unknown — heuristics not specialized` header making the absence of specialization explicit. |
