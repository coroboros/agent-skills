# Axis: Coherence (key `coherence`, conditional)

Cross-artifact drift across six structured sub-graphs: description, version, capability, cross-reference, example, spec-conformance. Catches the README ↔ `package.json` ↔ GitHub About ↔ marketplace ↔ topics ↔ CHANGELOG drift that motivates a dedicated axis. Conditional — activates only when metadata files appear in the diff.

## Activation

Decided by `scripts/scope.py:activates_coherence`. The axis runs when any of these appear in the diff:

- `package.json`
- `.claude-plugin/marketplace.json` or `marketplace.json`
- `SKILL.md` (any depth)
- Root `README.md`
- `tsconfig.json`
- `pyproject.toml`
- `Cargo.toml`
- `go.mod`

When inactive, the report header surfaces `Coherence axis: inactive` so the absence is visible.

## Dispatch protocol

The Phase 3 orchestrator launches one `Explore` subagent for the Coherence axis when active. `$SKILL_DIR` = this skill's folder — `${CLAUDE_SKILL_DIR}` in Claude Code, the directory containing the skill's SKILL.md elsewhere. The subagent invokes the orchestrator:

```bash
python3 "$SKILL_DIR/scripts/coherence/run.py" \
  --repo "<repo>" [--include-prose] --json
```

The Python orchestrator runs each sub-graph extractor, applies `.coherence-ignore` allowlists, and emits a unified findings list. Extractors are pure Python 3 stdlib — no network calls in default mode. Sub-graphs that depend on `gh` (description, topics) degrade gracefully when `gh` is unavailable: the header notes the skip; the sub-graph emits no findings.

## The six sub-graphs

### 1. description

Compares structured description fields across:

- `package.json` → `.description`
- `.claude-plugin/marketplace.json` → `.metadata.description`
- `gh repo view --json description` → `.description`
- `skills/<name>/SKILL.md` → frontmatter `description` (single-skill repos only)

Default mode compares structured fields only. `--include-prose` extends to the README's first paragraph (high false-positive, opt-in).

Equality uses case-insensitive normalization. Each disagreeing pair surfaces as one finding (severity Medium, confidence 90).

### 2. version

Compares all present version sources, split into two roles:

- **Manifest sources** (declared intent — bump first, in a PR):
  - `package.json` → `.version`
  - `.claude-plugin/marketplace.json` → `.metadata.version`
  - `CHANGELOG.md` → most recent `^## [vV]?\d+\.\d+\.\d+` header
- **Release sources** (published reality — bump after merge):
  - `git tag -l --sort=-v:refname | head -1`
  - `gh release list -L 1 --json tagName`

Comparison is semver-aware (`compare_versions` in `_common.py`). The conventional flow is **manifest leads release** — between the bump and the tag, manifest sources are ahead, and that is not drift. A finding emits only when:

- A release source is AHEAD of a manifest source (someone tagged but did not bump — real drift).
- Two manifest sources or two release sources DISAGREE with each other (real inconsistency).

Each finding has severity High and confidence 95.

### 3. capability

Parses README sections matching `Features`, `Commands`, `Skills`, or `Workstreams` and attempts to resolve each listed item to a file, function, or flag reference. An item with zero supporting references surfaces as one finding (severity Medium, confidence 70 — heuristic).

Resolution attempts: `Glob` against `<item>` as a partial path; `Grep` for `<item>` as a function or class; flag-shaped tokens (`--<item>` or `-<item>`) matched against `argparse` / `parse_args` patterns.

### 4. cross-reference

Resolves every relative link in `.md` files at the repo root and in `skills/*/`:

- File-existence checks for relative paths (`./foo.md`, `../bar/baz.md`).
- Anchor-existence checks for `#section` references (heading present in target file).
- Skill-name references — `/forge`, `/apex`, etc. — resolved against `.claude-plugin/marketplace.json` → `.plugins[].skills`.

A missing target surfaces as one finding (severity High, confidence 95).

### 5. example

Parses fenced code blocks marked `bash`, `sh`, or `shell`. For each command, extracts the program + flags and matches the flags against the program's script source via:

- `argparse.add_argument("-x", "--xxx", ...)` patterns
- `parse_args` shell idioms (`while getopts`, manual case statements)

A flag appearing in the example but not in the program's parser surfaces as one finding (severity Medium, confidence 80).

### 6. spec-conformance

The full spec-conformance sub-graph (`WebFetch` + cache + grammar inference) is a later iteration. The current entrypoint is a stub: detects normative-spec mentions in diff / README / CLAUDE.md using the normative-spec regex and emits a deferred placeholder finding (severity Low, confidence 50).

## `.coherence-ignore` format

Per-repo allowlist at repo root. Minimal YAML — keys are sub-graph names, values are graph-specific allowlists.

```yaml
version:
  ignore_pairs:
    - git-tag:package.json

capability:
  ignore_items:
    - legacy-cli

description:
  ignore_pairs:
    - package.json:gh-about

cross-reference:
  ignore_paths:
    - docs/internal/*.md
```

The parser supports comments (`#`), nested mappings (2-space indent), and flat lists (`-` items). Full grammar in `scripts/coherence/_common.py:load_ignore`.

## `--include-prose` semantics

Opt-in extension to the description sub-graph. When set, the README's first paragraph is normalized (strip markdown, lowercase, collapse whitespace) and compared against the structured description fields. High false-positive rate — gated explicitly for this reason. Findings inherit severity Low (downgraded from structured Medium) to reflect the heuristic nature.

## Finding schema

Each finding carries an additional `sub_graph` field:

```json
{
  "axis": "coherence",
  "sub_graph": "description | version | capability | cross-reference | example | spec-conformance",
  "severity": "High | Medium | Low",
  "location": "path:line | path | (cross-source)",
  "finding": "What is wrong",
  "recommendation": "What to do",
  "confidence": 0
}
```

`sub_graph` is the Coherence-specific field — readers can filter by which sub-graph fired. The orchestrator preserves it through aggregation (kept as `meta.sub_graph` on the canonical row).

## Severity calibration

- 🔴 High — cross-reference miss (broken link), release source ahead of manifest, version sources disagree.
- 🟠 Medium — description divergence, capability with no supporting reference, example flag not in parser.
- 🟢 Low — `--include-prose` mismatch, spec-conformance stub placeholder.

## Repo-kind branches

### Description sub-graph

| `repo_kind` | Sources compared |
|-------------|------------------|
| `skills` (multi-skill, `skill_md_count > 1`) | `marketplace.json` `.metadata.description` ↔ `gh repo view --json description`. Per-SKILL.md cross-comparison skipped — each SKILL.md is per-skill. |
| `skills` (single-skill, `skill_md_count == 1`) | All four structured sources including the lone SKILL.md frontmatter. |
| `app`, `library` | `package.json` `.description` ↔ marketplace ↔ `gh About` ↔ SKILL.md frontmatter (where present). |
| `python`, `rust`, `go` | `gh repo view --json description` ↔ language-manifest description if present (`pyproject.toml` `[project].description`, `Cargo.toml` `[package].description`); marketplace / SKILL.md sources skipped. |
| `docs` | Docs-site-config title / description ↔ `gh About`. |
| `monorepo` | Top-level `package.json` `.description` ↔ `gh About` only. |
| `unknown` | Every present source compared. |

### Version sub-graph

| `repo_kind` | Manifest sources |
|-------------|------------------|
| `skills` | `.claude-plugin/marketplace.json` `.metadata.version`. |
| `app`, `library` | `package.json` `.version` + `CHANGELOG.md` most-recent header. |
| `python` | `pyproject.toml` `[project].version`. |
| `rust` | `Cargo.toml` `[package].version`. |
| `go` | (No manifest source — release sources only.) |
| `docs` | Version field from docs-site config. |
| `monorepo` | Per-workspace; sub-graph emits zero findings at the repo root. |
| `unknown` | Every detected source compared. |

Release sources (`git tag -l`, `gh release list -L 1`) stay unchanged across kinds.

### Capability sub-graph

| `repo_kind` | Capability resolution |
|-------------|------------------------|
| `skills` | README skills-table rows resolve to `skills/<name>/SKILL.md` AND a marketplace skill entry. A row missing either reference emits one finding. |
| `app`, `library` | README features resolve to source files, functions, or flag references via the `argparse` / `parse_args` / glob heuristics. |
| `python`, `rust`, `go` | README features resolve to language-native targets. |
| `docs` | README sections resolve to docs-site nav entries; missing pages emit one finding. |
| `monorepo` | Per-workspace; sub-graph emits zero findings at the repo root. |
| `unknown` | Existing behavior. |

Cross-reference, example, and spec-conformance sub-graphs stay repo-agnostic.

## Tool inputs (Phase 2)

No deterministic tool findings route to this axis. Coherence runs its own orchestrator (`scripts/coherence/run.py`) which produces findings the subagent then reviews.

## Graceful degradation

- `gh` missing → description sub-graph skips GitHub About + topics; header notes the skip (not a finding).
- `package.json` missing → description + version sub-graphs skip it silently.
- `CHANGELOG.md` missing → version sub-graph skips that source.
- `marketplace.json` missing → description + cross-reference sub-graphs skip it.
- `git` missing or repo unborn → version sub-graph skips the tag source.

Orchestrator exit code is always `0` when extractors complete. Non-zero means a hard failure (missing script, invalid `.coherence-ignore`, repo path doesn't exist).

## Subagent inputs

- `scope.json` — repo kind, languages, files touched, `activates_coherence: true`.
- `tool-findings.jsonl` filtered to `axis: coherence` — always empty (Coherence has its own orchestrator).
- The diff itself.
- This brief.
- `references/anthropic-verbatim.md` — rubric + false-positive list.
- Orchestrator output (`scripts/coherence/run.py --json`) carrying sub-graph findings.

## Fixtures

Coherence fixtures live under `tests/code-ultrareview/fixtures/coherence-graph/`, one directory per case:

| Fixture | Expected findings |
|---------|-------------------|
| `clean-repo/` | none |
| `clean-structured-divergent-prose/` | none in default mode; one with `--include-prose` |
| `description-divergence/` | one finding (description sub-graph) |
| `description-divergence-ignored/` | none (allowlisted in `.coherence-ignore`) |
| `version-mismatch/` | one finding (version sub-graph) |
| `broken-cross-skill-reference/` | one finding (cross-reference sub-graph) |
| `broken-example/` | one finding (example sub-graph) |
